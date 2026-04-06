# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       uniaxial
Description:  Short column design under uniaxial bending per IS 456:2000 Cl 39.5.
Traceability: Functions are decorated with @clause for IS 456 clause references.

Implements:
- P-M interaction envelope generation (Cl 39.5)
- Short column uniaxial bending capacity check
- Radial utilization ratio for (Pu, Mu) against the interaction envelope

References:
    IS 456:2000, Cl. 39.5
    SP:16:1980 Design Aids, Charts 27-62, Table I
    Pillai & Menon, "Reinforced Concrete Design", 3rd Ed.
"""

from __future__ import annotations

import math
import warnings as _warnings_mod

from structural_lib.codes.is456.column.axial import classify_column, min_eccentricity
from structural_lib.codes.is456.common.constants import (
    COLUMN_AXIAL_EMIN_FACTOR,
    COLUMN_CONCRETE_COEFF,
    COLUMN_MAX_STEEL_RATIO,
    COLUMN_MIN_STEEL_RATIO,
    COLUMN_STEEL_COEFF,
    EPSILON_CU,
    STRESS_BLOCK_DEPTH,
    STRESS_BLOCK_FACTOR,
    STRESS_BLOCK_PEAK,
)
from structural_lib.codes.is456.common.stress_blocks import (
    steel_stress_from_strain_5point,
)
from structural_lib.codes.is456.traceability import clause
from structural_lib.core.data_types import (
    ColumnClassification,
    ColumnUniaxialResult,
    PMInteractionResult,
)
from structural_lib.core.errors import (
    CalculationError,
    DimensionError,
    MaterialError,
)
from structural_lib.core.numerics import safe_divide

__all__ = [
    "design_short_column_uniaxial",
    "pm_interaction_curve",
]

# ---------------------------------------------------------------------------
# SP:16 Table I -- Stress-block coefficients for xu > D
# k = D / xu -> (C1, C2)
#   Cc = C1 * 0.36 * fck * b * D
#   Centroid at C2 * D from compression face
# ---------------------------------------------------------------------------
_SP16_TABLE_I_KEYS: tuple[float, ...] = (
    0.05,
    0.10,
    0.15,
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
    0.45,
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
    0.75,
    0.80,
    0.85,
    0.90,
    0.95,
    1.00,
)

_SP16_TABLE_I_C1: tuple[float, ...] = (
    0.112,
    0.194,
    0.269,
    0.338,
    0.401,
    0.458,
    0.511,
    0.558,
    0.601,
    0.640,
    0.675,
    0.706,
    0.733,
    0.756,
    0.775,
    0.790,
    0.802,
    0.811,
    0.816,
    1.0,
)

_SP16_TABLE_I_C2: tuple[float, ...] = (
    0.072,
    0.105,
    0.135,
    0.160,
    0.182,
    0.204,
    0.223,
    0.241,
    0.258,
    0.273,
    0.287,
    0.300,
    0.313,
    0.324,
    0.335,
    0.346,
    0.356,
    0.366,
    0.376,
    0.42,
)

# Number of points to sweep for the P-M interaction envelope
_ENVELOPE_POINTS: int = 200

# Tolerance for radial distance comparisons
_RADIAL_TOL: float = 1e-6


def _interp_sp16_table_i(k: float) -> tuple[float, float]:
    """Interpolate SP:16 Table I coefficients for a given k = D/xu.

    Args:
        k: Ratio D/xu (0 < k <= 1.0). Clamped to [0.05, 1.0].

    Returns:
        Tuple (C1, C2) interpolated from SP:16 Table I.
    """
    # Clamp k to table bounds -- never extrapolate
    if k <= _SP16_TABLE_I_KEYS[0]:
        return _SP16_TABLE_I_C1[0], _SP16_TABLE_I_C2[0]
    if k >= _SP16_TABLE_I_KEYS[-1]:
        return _SP16_TABLE_I_C1[-1], _SP16_TABLE_I_C2[-1]

    # Find bounding entries
    for i in range(len(_SP16_TABLE_I_KEYS) - 1):
        k_lo = _SP16_TABLE_I_KEYS[i]
        k_hi = _SP16_TABLE_I_KEYS[i + 1]
        if k_lo <= k <= k_hi:
            # Linear interpolation
            t = safe_divide(k - k_lo, k_hi - k_lo, default=0.0)
            c1 = _SP16_TABLE_I_C1[i] + t * (
                _SP16_TABLE_I_C1[i + 1] - _SP16_TABLE_I_C1[i]
            )
            c2 = _SP16_TABLE_I_C2[i] + t * (
                _SP16_TABLE_I_C2[i + 1] - _SP16_TABLE_I_C2[i]
            )
            return c1, c2

    # Fallback (should not reach here)
    return _SP16_TABLE_I_C1[-1], _SP16_TABLE_I_C2[-1]


def _pm_envelope_point(
    xu: float,
    b_mm: float,
    D_mm: float,
    fck: float,
    fy: float,
    Asc_half_mm2: float,
    d_prime_mm: float,
) -> tuple[float, float]:
    """Compute one (Pu, Mu) point on the P-M interaction envelope.

    Forces and moments are returned in kN and kNm respectively.

    Args:
        xu: Neutral axis depth from compression face (mm).
        b_mm: Column width (mm).
        D_mm: Column depth in bending direction (mm).
        fck: Concrete strength (N/mm2).
        fy: Steel yield strength (N/mm2).
        Asc_half_mm2: Area of steel on ONE face (mm2).
        d_prime_mm: Cover to centroid of steel from nearest face (mm).

    Returns:
        (Pu_kN, Mu_kNm) -- one point on the interaction envelope.
    """
    d_eff = D_mm - d_prime_mm  # Depth to tension steel centroid

    # --- Concrete contribution ---
    if xu <= D_mm:
        # IS 456 Cl 38.1: Cc = 0.36 * fck * b * xu
        Cc_N = STRESS_BLOCK_FACTOR * fck * b_mm * xu
        # Centroid of stress block at 0.42 * xu from comp. face
        y_cc = STRESS_BLOCK_DEPTH * xu
    else:
        # xu > D: entire section in compression -- use SP:16 Table I
        k = safe_divide(D_mm, xu, default=1.0)
        c1, c2 = _interp_sp16_table_i(k)
        # IS 456 + SP:16 Table I: Cc = C1 * 0.36 * fck * b * D
        Cc_N = c1 * STRESS_BLOCK_FACTOR * fck * b_mm * D_mm
        y_cc = c2 * D_mm

    # --- Steel strains (compression and tension faces) ---
    if xu <= _RADIAL_TOL:
        eps_sc = 0.0
        eps_st = 0.0
    elif xu <= D_mm:
        # IS 456 Cl 38.1: standard strain profile (max 0.0035 at comp face, zero at NA)
        eps_sc = EPSILON_CU * safe_divide(xu - d_prime_mm, xu, default=0.0)
        eps_st = EPSILON_CU * safe_divide(xu - d_eff, xu, default=0.0)
    else:
        # IS 456 Cl 38.1: modified strain profile for xu > D (entire section in compression)
        # Strain at far face (least compressed):
        eps_far = EPSILON_CU * safe_divide(xu - D_mm, xu, default=0.0)
        # Strain at compression face: 0.0035 - 0.75 * eps_far (IS 456 Cl 38.1)
        eps_max = EPSILON_CU - 0.75 * eps_far
        # Linear interpolation across section depth
        eps_sc = eps_max - (eps_max - eps_far) * d_prime_mm / D_mm
        eps_st = eps_max - (eps_max - eps_far) * d_eff / D_mm

    f_sc = steel_stress_from_strain_5point(eps_sc, fy)
    # IS 456 Cl 38.1: subtract displaced concrete (already counted in Cc)
    # Net steel stress = f_sc - 0.446 * fck (if bar is in compression)
    if eps_sc > 0.0:
        f_sc_net = f_sc - STRESS_BLOCK_PEAK * fck
    else:
        f_sc_net = f_sc
    F_sc_N = f_sc_net * Asc_half_mm2

    f_st = steel_stress_from_strain_5point(eps_st, fy)
    # Subtract displaced concrete only if bar is in compression zone
    if eps_st > 0.0:
        f_st_net = f_st - STRESS_BLOCK_PEAK * fck
    else:
        f_st_net = f_st
    F_st_N = f_st_net * Asc_half_mm2

    # --- Axial force: Pu = Cc + F_sc + F_st ---
    Pu_N = Cc_N + F_sc_N + F_st_N

    # --- Moment about centroid (D/2 from comp. face) ---
    mid = D_mm / 2.0
    Mu_Nmm = Cc_N * (mid - y_cc) + F_sc_N * (mid - d_prime_mm) + F_st_N * (mid - d_eff)

    # Convert to kN, kNm
    Pu_kN = Pu_N / 1000.0
    Mu_kNm = Mu_Nmm / 1e6

    return Pu_kN, Mu_kNm


@clause("39.5")
def design_short_column_uniaxial(
    Pu_kN: float,
    Mu_kNm: float,
    b_mm: float,
    D_mm: float,
    le_mm: float,
    fck: float,
    fy: float,
    Asc_mm2: float,
    d_prime_mm: float,
    l_unsupported_mm: float | None = None,
) -> ColumnUniaxialResult:
    """Check short column under uniaxial bending per IS 456 Cl 39.5.

    Generates the P-M interaction envelope for the given section and
    determines whether the applied (Pu, Mu) lies within it. The capacity
    is found by radial intersection: a ray from origin through (Pu, Mu)
    intersects the envelope at (Pu_cap, Mu_cap).

    Reinforcement is assumed symmetrical: Asc_mm2 / 2 on each face, placed
    at d_prime_mm from the nearest face.

    Args:
        Pu_kN: Applied factored axial load (kN). Must be >= 0.
        Mu_kNm: Applied factored moment about the bending axis (kNm).
            Must be >= 0 (sign convention: always positive).
        b_mm: Column width perpendicular to bending axis (mm). Must be > 0.
        D_mm: Column depth in the direction of bending (mm). Must be > 0.
        le_mm: Effective length of column (mm). Must be > 0.
        fck: Characteristic compressive strength of concrete (N/mm2).
            IS 456 range: 15-80.
        fy: Characteristic yield strength of steel (N/mm2).
            IS 456 range: 250-550.
        Asc_mm2: Total area of longitudinal reinforcement (mm2).
            Assumed symmetrically placed (half on each face).
        d_prime_mm: Distance from nearest face to centroid of steel (mm).
            Must be > 0 and < D_mm / 2.
        l_unsupported_mm: Unsupported length (mm) for minimum eccentricity
            computation per Cl 25.4. If None, minimum eccentricity check
            is skipped.

    Returns:
        ColumnUniaxialResult with capacity, utilization, and safety status.

    Raises:
        DimensionError: If geometric dimensions are invalid.
        MaterialError: If material properties are out of range.
        CalculationError: If numerical issues are encountered.

    References:
        IS 456:2000, Cl. 39.5 (P-M interaction)
        IS 456:2000, Cl. 25.4 (minimum eccentricity)
        IS 456:2000, Cl. 25.1.2 (column classification)
        SP:16:1980 Table I (stress-block coefficients for xu > D)

    Limitations:
        - Short columns only (le/D < 12 per Cl. 25.1.2); if the column
          is classified as slender, a warning is issued but additional
          moment due to P-delta is NOT applied—use the ``long_column``
          module (Cl. 39.7) for slender columns.
        - Rectangular sections only; circular column interaction curves
          require a different stress-block integration.
        - Uniaxial bending only (moment about one axis); for biaxial
          bending use the ``biaxial`` module (Cl. 39.6, Bresler's
          equation).
        - Symmetrical reinforcement assumed (Asc/2 on each face); for
          asymmetric steel layouts, the interaction curve must be
          generated separately.
        - Two layers of steel only (tension face + compression face);
          intermediate bars along the depth are not considered.
        - Valid for fck ≤ 80 N/mm² and fy ≤ 550 N/mm² (IS 456 scope).
    """
    # ===========================================================
    # 1. Input validation
    # ===========================================================
    warnings: list[str] = []

    # --- Dimensions ---
    if b_mm <= 0:
        raise DimensionError(
            f"Column width b_mm must be > 0, got {b_mm}",
            details={"b_mm": b_mm},
            clause_ref="Cl. 39.5",
        )
    if D_mm <= 0:
        raise DimensionError(
            f"Column depth D_mm must be > 0, got {D_mm}",
            details={"D_mm": D_mm},
            clause_ref="Cl. 39.5",
        )
    if b_mm < 200:
        _warnings_mod.warn(
            f"Column width b_mm={b_mm}mm is below recommended minimum 200mm. "
            "Impractically small column sections may not be constructible.",
            stacklevel=2,
        )
    if D_mm < 200:
        _warnings_mod.warn(
            f"Column depth D_mm={D_mm}mm is below recommended minimum 200mm. "
            "Impractically small column sections may not be constructible.",
            stacklevel=2,
        )
    if le_mm <= 0:
        raise DimensionError(
            f"Effective length le_mm must be > 0, got {le_mm}",
            details={"le_mm": le_mm},
            clause_ref="Cl. 25.1.2",
        )
    if d_prime_mm <= 0 or d_prime_mm >= D_mm / 2.0:
        raise DimensionError(
            f"Cover d_prime_mm must be > 0 and < D/2={D_mm / 2.0}, "
            f"got {d_prime_mm}",
            details={"d_prime_mm": d_prime_mm, "D_mm": D_mm},
            clause_ref="Cl. 26.4",
        )

    # --- Materials ---
    if fck <= 0:
        raise MaterialError(
            f"fck must be > 0, got {fck}",
            details={"fck": fck},
            clause_ref="Cl. 39.5",
        )
    if fy <= 0:
        raise MaterialError(
            f"fy must be > 0, got {fy}",
            details={"fy": fy},
            clause_ref="Cl. 39.5",
        )
    if fck > 80:
        warnings.append(
            f"fck={fck} N/mm2 exceeds typical IS 456 range (15-80). "
            "Results may not be code-compliant."
        )
    if fy > 550:
        warnings.append(
            f"fy={fy} N/mm2 exceeds typical IS 456 range (250-550). "
            "Results may not be code-compliant."
        )

    # --- Loads ---
    if Pu_kN < 0:
        raise DimensionError(
            f"Axial load Pu_kN must be >= 0 for compression member, " f"got {Pu_kN}",
            details={"Pu_kN": Pu_kN},
            clause_ref="Cl. 39.5",
        )
    if Mu_kNm < 0:
        raise DimensionError(
            f"Moment Mu_kNm must be >= 0, got {Mu_kNm}",
            details={"Mu_kNm": Mu_kNm},
            clause_ref="Cl. 39.5",
        )

    # --- Steel area ---
    Ag_mm2 = b_mm * D_mm
    steel_ratio = safe_divide(Asc_mm2, Ag_mm2, default=0.0)
    if Asc_mm2 < 0:
        raise DimensionError(
            f"Total steel area Asc_mm2 must be >= 0, got {Asc_mm2}",
            details={"Asc_mm2": Asc_mm2},
            clause_ref="Cl. 26.5.3.1",
        )
    if steel_ratio < COLUMN_MIN_STEEL_RATIO:
        warnings.append(
            f"Steel ratio {steel_ratio:.4f} below minimum "
            f"{COLUMN_MIN_STEEL_RATIO} (0.8%) per Cl 26.5.3.1"
        )
    if steel_ratio > COLUMN_MAX_STEEL_RATIO:
        warnings.append(
            f"Steel ratio {steel_ratio:.4f} exceeds maximum "
            f"{COLUMN_MAX_STEEL_RATIO} (4%) per Cl 26.5.3.1"
        )

    # ===========================================================
    # 2. Column classification
    # ===========================================================
    classification = classify_column(le_mm, D_mm)
    if classification == ColumnClassification.SLENDER:
        warnings.append(
            "Column classified as slender (le/D >= 12). "
            "Additional moment per Cl 39.7 required. "
            "This function does NOT apply the slenderness moment."
        )

    # ===========================================================
    # 3. Eccentricity and minimum eccentricity check
    # ===========================================================
    e_min_mm: float | None = None
    Mu_design_kNm = Mu_kNm

    if l_unsupported_mm is not None:
        # IS 456 Cl 25.4: e_min = max(l/500 + D/30, 20)
        e_min_mm = min_eccentricity(l_unsupported_mm, D_mm)
        # IS 456 Cl 25.4: minimum design moment = Pu * e_min
        Mu_emin_kNm = Pu_kN * e_min_mm / 1000.0
        if Mu_design_kNm < Mu_emin_kNm:
            Mu_design_kNm = Mu_emin_kNm
            warnings.append(
                f"Applied moment amplified from {Mu_kNm:.2f} to "
                f"{Mu_design_kNm:.2f} kNm to satisfy "
                f"e_min={e_min_mm:.1f}mm per Cl 25.4"
            )

    # Compute actual eccentricity
    if abs(Pu_kN) < _RADIAL_TOL:
        # Pure bending case
        eccentricity_mm = float("inf")
    else:
        # IS 456: e = M / P (kNm / kN = m, multiply by 1000 for mm)
        eccentricity_mm = Mu_design_kNm / Pu_kN * 1000.0

    # Small eccentricity warning
    if (
        math.isfinite(eccentricity_mm)
        and eccentricity_mm < COLUMN_AXIAL_EMIN_FACTOR * D_mm
    ):
        warnings.append(
            f"Eccentricity {eccentricity_mm:.1f}mm < "
            f"0.05*D={COLUMN_AXIAL_EMIN_FACTOR * D_mm:.1f}mm. "
            "Pure axial formula (Cl 39.3) may be more appropriate."
        )

    # ===========================================================
    # 4. Generate P-M interaction envelope
    # ===========================================================
    Asc_half = Asc_mm2 / 2.0

    # Sweep xu from near-zero (pure bending) to 3*D (pure compression)
    xu_min = 0.01 * D_mm
    xu_max_sweep = 3.0 * D_mm

    envelope_P: list[float] = []
    envelope_M: list[float] = []

    for i in range(_ENVELOPE_POINTS + 1):
        xu = xu_min + (xu_max_sweep - xu_min) * i / _ENVELOPE_POINTS
        p_pt, m_pt = _pm_envelope_point(xu, b_mm, D_mm, fck, fy, Asc_half, d_prime_mm)
        envelope_P.append(p_pt)
        # IS 456 Cl 39.5: moment is always positive (absolute)
        envelope_M.append(abs(m_pt))

    # ===========================================================
    # 5. Find capacity on envelope (radial intersection)
    # ===========================================================
    Pu_applied = Pu_kN
    Mu_applied = Mu_design_kNm

    # Trivial case: zero load
    if abs(Pu_applied) < _RADIAL_TOL and abs(Mu_applied) < _RADIAL_TOL:
        return ColumnUniaxialResult(
            Pu_kN=Pu_kN,
            Mu_kNm=Mu_kNm,
            Pu_cap_kN=max(envelope_P),
            Mu_cap_kNm=max(envelope_M),
            utilization_ratio=0.0,
            eccentricity_mm=0.0,
            e_min_mm=e_min_mm,
            is_safe=True,
            classification=classification,
            governing_check="No load applied",
            clause_ref="Cl. 39.5",
            warnings=tuple(warnings),
        )

    # Radial distance of applied point from origin
    r_applied = math.sqrt(Pu_applied**2 + Mu_applied**2)
    # Angle of the ray from origin through (Pu, Mu)
    theta_applied = math.atan2(Mu_applied, Pu_applied)

    best_r_cap = float("inf")
    best_P_cap = 0.0
    best_M_cap = 0.0

    cos_t = math.cos(theta_applied)
    sin_t = math.sin(theta_applied)

    # Search each segment of the envelope for intersection with ray
    for i in range(len(envelope_P) - 1):
        p0, m0 = envelope_P[i], envelope_M[i]
        p1, m1 = envelope_P[i + 1], envelope_M[i + 1]

        # Ray: (P, M) = t * (cos_t, sin_t), t > 0
        # Segment: (P, M) = (p0, m0) + s * (dp, dm), 0 <= s <= 1
        dp = p1 - p0
        dm = m1 - m0

        # Solve 2x2 system:
        #   t * cos_t - s * dp = p0
        #   t * sin_t - s * dm = m0
        # det = cos_t * dm - sin_t * dp
        det = cos_t * dm - sin_t * dp
        if abs(det) < 1e-15:
            continue

        t_ray = safe_divide(p0 * dm - m0 * dp, det, default=-1.0)
        s_seg = safe_divide(p0 * sin_t - m0 * cos_t, det, default=-1.0)

        if t_ray > _RADIAL_TOL and -0.01 <= s_seg <= 1.01:
            P_cap = t_ray * cos_t
            M_cap = t_ray * sin_t
            r_cap = math.sqrt(P_cap**2 + M_cap**2)
            if r_cap < best_r_cap:
                best_r_cap = r_cap
                best_P_cap = P_cap
                best_M_cap = M_cap

    # Fallback: nearest envelope point by angle
    if best_r_cap == float("inf"):
        best_angle_diff = float("inf")
        for i in range(len(envelope_P)):
            ep, em = envelope_P[i], envelope_M[i]
            r_env = math.sqrt(ep**2 + em**2)
            if r_env < _RADIAL_TOL:
                continue
            theta_env = math.atan2(em, ep)
            angle_diff = abs(theta_env - theta_applied)
            if angle_diff < best_angle_diff:
                best_angle_diff = angle_diff
                best_P_cap = ep
                best_M_cap = em
                best_r_cap = r_env

    # ===========================================================
    # 6. Compute utilization and determine safety
    # ===========================================================
    r_cap = math.sqrt(best_P_cap**2 + best_M_cap**2)
    utilization = safe_divide(r_applied, r_cap, default=float("inf"))

    # NaN/Inf check on output
    if math.isnan(utilization) or math.isinf(utilization):
        if abs(r_cap) < _RADIAL_TOL:
            raise CalculationError(
                "P-M envelope capacity is zero. "
                "Check section dimensions and reinforcement.",
                details={
                    "r_applied": r_applied,
                    "r_cap": r_cap,
                    "b_mm": b_mm,
                    "D_mm": D_mm,
                },
                clause_ref="Cl. 39.5",
            )
        raise CalculationError(
            "Utilization ratio is NaN or Inf. " f"r_applied={r_applied}, r_cap={r_cap}",
            details={
                "Pu_kN": Pu_kN,
                "Mu_kNm": Mu_kNm,
                "best_P_cap": best_P_cap,
                "best_M_cap": best_M_cap,
            },
            clause_ref="Cl. 39.5",
        )

    utilization_ratio = round(utilization, 4)
    is_safe = utilization_ratio <= 1.0

    # Determine governing check description
    if not is_safe:
        governing = "P-M interaction envelope exceeded (Cl 39.5)"
    elif classification == ColumnClassification.SLENDER:
        governing = "Slenderness: additional moment not applied (Cl 39.7)"
    elif e_min_mm is not None and Mu_kNm < Pu_kN * e_min_mm / 1000.0:
        governing = "Minimum eccentricity governs (Cl 25.4)"
    else:
        governing = "P-M interaction check (Cl 39.5)"

    eccentricity_out = (
        round(eccentricity_mm, 1) if math.isfinite(eccentricity_mm) else eccentricity_mm
    )

    return ColumnUniaxialResult(
        Pu_kN=Pu_kN,
        Mu_kNm=Mu_design_kNm,
        Pu_cap_kN=round(best_P_cap, 2),
        Mu_cap_kNm=round(abs(best_M_cap), 2),
        utilization_ratio=utilization_ratio,
        eccentricity_mm=eccentricity_out,
        e_min_mm=round(e_min_mm, 1) if e_min_mm is not None else None,
        is_safe=is_safe,
        classification=classification,
        governing_check=governing,
        clause_ref="Cl. 39.5",
        warnings=tuple(warnings),
    )


# ---------------------------------------------------------------------------
# P-M interaction curve generation
# ---------------------------------------------------------------------------


@clause("39.5")
def pm_interaction_curve(
    b_mm: float,
    D_mm: float,
    fck: float,
    fy: float,
    Asc_mm2: float,
    d_prime_mm: float,
    n_points: int = 50,
) -> PMInteractionResult:
    """Generate the P-M interaction curve for a rectangular column section.

    Sweeps the neutral axis depth from near-zero to 3×D to produce
    (Pu, Mu) envelope points. Also computes the pure axial capacity,
    balanced point, and pure bending intercept.

    Reinforcement is assumed symmetrical: Asc_mm2 / 2 on each face,
    placed at d_prime_mm from the nearest face.

    Args:
        b_mm: Column width perpendicular to bending axis (mm). Must be > 0.
        D_mm: Column depth in the direction of bending (mm). Must be > 0.
        fck: Characteristic compressive strength of concrete (N/mm²).
            IS 456 range: 15–80.
        fy: Characteristic yield strength of steel (N/mm²).
            IS 456 range: 250–550.
        Asc_mm2: Total area of longitudinal reinforcement (mm²).
            Must be > 0.
        d_prime_mm: Distance from nearest face to centroid of steel (mm).
            Must be > 0 and < D_mm / 2.
        n_points: Number of envelope points to generate (default 50).
            Must be >= 10.

    Returns:
        PMInteractionResult with envelope points and key capacities.

    Raises:
        DimensionError: If geometric dimensions are invalid.
        MaterialError: If material properties are out of range.

    References:
        IS 456:2000, Cl. 39.5 (P-M interaction)
        IS 456:2000, Cl. 39.3 (pure axial capacity)
        SP:16:1980 Table I (stress-block coefficients for xu > D)

    Limitations:
        - Rectangular sections only; circular columns require polar
          integration of the stress block.
        - Symmetrical reinforcement assumed (Asc/2 on each face);
          asymmetric arrangements produce a different envelope.
        - Two layers of steel only (tension + compression face);
          intermediate bars along the depth are not modelled.
        - Does not include slenderness effects; the envelope is for
          the cross-section only—P-delta amplification for slender
          columns must be applied externally (Cl. 39.7).
        - Tension (negative Pu) region is not generated; the curve
          covers compression members only.
        - Valid for fck ≤ 80 N/mm² and fy ≤ 550 N/mm² (IS 456 scope).
    """
    # ===========================================================
    # 1. Input validation
    # ===========================================================
    warnings: list[str] = []

    # --- Dimensions ---
    if b_mm <= 0:
        raise DimensionError(
            f"Column width b_mm must be > 0, got {b_mm}",
            details={"b_mm": b_mm},
            clause_ref="Cl. 39.5",
        )
    if D_mm <= 0:
        raise DimensionError(
            f"Column depth D_mm must be > 0, got {D_mm}",
            details={"D_mm": D_mm},
            clause_ref="Cl. 39.5",
        )
    if d_prime_mm <= 0 or d_prime_mm >= D_mm / 2.0:
        raise DimensionError(
            f"Cover d_prime_mm must be > 0 and < D/2={D_mm / 2.0}, "
            f"got {d_prime_mm}",
            details={"d_prime_mm": d_prime_mm, "D_mm": D_mm},
            clause_ref="Cl. 26.4",
        )

    # --- Materials ---
    if fck <= 0:
        raise MaterialError(
            f"fck must be > 0, got {fck}",
            details={"fck": fck},
            clause_ref="Cl. 39.5",
        )
    if fy <= 0:
        raise MaterialError(
            f"fy must be > 0, got {fy}",
            details={"fy": fy},
            clause_ref="Cl. 39.5",
        )
    if fck > 80:
        warnings.append(
            f"fck={fck} N/mm² exceeds typical IS 456 range (15-80). "
            "Results may not be code-compliant."
        )
    if fy > 550:
        warnings.append(
            f"fy={fy} N/mm² exceeds typical IS 456 range (250-550). "
            "Results may not be code-compliant."
        )

    # --- Steel area ---
    if Asc_mm2 <= 0:
        raise DimensionError(
            f"Total steel area Asc_mm2 must be > 0, got {Asc_mm2}",
            details={"Asc_mm2": Asc_mm2},
            clause_ref="Cl. 26.5.3.1",
        )
    Ag_mm2 = b_mm * D_mm
    steel_ratio = safe_divide(Asc_mm2, Ag_mm2, default=0.0)
    if steel_ratio < COLUMN_MIN_STEEL_RATIO:
        warnings.append(
            f"Steel ratio {steel_ratio:.4f} below minimum "
            f"{COLUMN_MIN_STEEL_RATIO} (0.8%) per Cl 26.5.3.1"
        )
    if steel_ratio > COLUMN_MAX_STEEL_RATIO:
        warnings.append(
            f"Steel ratio {steel_ratio:.4f} exceeds maximum "
            f"{COLUMN_MAX_STEEL_RATIO} (4%) per Cl 26.5.3.1"
        )

    # --- n_points ---
    if n_points < 10:
        raise ValueError(f"n_points must be >= 10, got {n_points}")

    # ===========================================================
    # 2. Generate P-M interaction envelope
    # ===========================================================
    # IS 456 Cl 39.5: sweep xu from near-zero to 3*D
    Asc_half = Asc_mm2 / 2.0
    xu_min = 0.01 * D_mm
    xu_max_sweep = 3.0 * D_mm

    envelope_P: list[float] = []
    envelope_M: list[float] = []

    for i in range(n_points + 1):
        xu = xu_min + (xu_max_sweep - xu_min) * i / n_points
        p_pt, m_pt = _pm_envelope_point(xu, b_mm, D_mm, fck, fy, Asc_half, d_prime_mm)
        envelope_P.append(p_pt)
        # IS 456 Cl 39.5: moment is always positive (absolute)
        envelope_M.append(abs(m_pt))

    # ===========================================================
    # 3. Pure axial capacity (Pu_0) per IS 456 Cl 39.3
    # ===========================================================
    # IS 456 Cl 39.3: Pu_0 = 0.4 * fck * Ac + 0.67 * fy * Asc
    Ac_mm2 = Ag_mm2 - Asc_mm2
    Pu_0_kN = (
        COLUMN_CONCRETE_COEFF * fck * Ac_mm2 + COLUMN_STEEL_COEFF * fy * Asc_mm2
    ) / 1000.0

    # Cap envelope at Pu_0 per IS 456 Cl 39.3
    for i in range(len(envelope_P)):
        if envelope_P[i] > Pu_0_kN:
            envelope_P[i] = Pu_0_kN
            envelope_M[i] = 0.0

    # Ensure pure axial point (Pu_0, 0) is included
    if not envelope_P or envelope_P[-1] != Pu_0_kN or envelope_M[-1] != 0.0:
        envelope_P.append(Pu_0_kN)
        envelope_M.append(0.0)

    # ===========================================================
    # 4. Balanced point detection
    # ===========================================================
    # IS 456 Cl 38.1: balanced xu when tension steel just yields
    Es = 2e5  # Steel modulus = 200,000 N/mm²
    d_eff = D_mm - d_prime_mm
    eps_sy_elastic = fy / (1.15 * Es)
    # IS 456 Cl 38.1: HYSD bars (Fe 415, 500, 550) have 0.002 inelastic strain
    # Mild steel (Fe 250) has no inelastic component
    eps_sy = eps_sy_elastic + 0.002 if fy > 250 else eps_sy_elastic
    xu_bal = d_eff * EPSILON_CU / (EPSILON_CU + eps_sy)
    Pu_bal_kN, Mu_bal_kNm = _pm_envelope_point(
        xu_bal, b_mm, D_mm, fck, fy, Asc_half, d_prime_mm
    )
    Mu_bal_kNm = abs(Mu_bal_kNm)

    # ===========================================================
    # 5. Pure bending point (Mu_0) — where Pu crosses zero
    # ===========================================================
    Mu_0_kNm = 0.0
    for i in range(len(envelope_P) - 1):
        if envelope_P[i] * envelope_P[i + 1] <= 0:  # Sign change
            # Linear interpolation to find Pu = 0 crossing
            t = safe_divide(
                -envelope_P[i],
                envelope_P[i + 1] - envelope_P[i],
                default=0.5,
            )
            Mu_0_kNm = envelope_M[i] + t * (envelope_M[i + 1] - envelope_M[i])
            break
    else:
        # No sign change — use point with smallest |Pu|
        min_idx = min(range(len(envelope_P)), key=lambda j: abs(envelope_P[j]))
        Mu_0_kNm = envelope_M[min_idx]
        warnings.append(
            "Pure bending point (Pu=0) not found in sweep; " "using closest point"
        )

    # ===========================================================
    # 6. Build result
    # ===========================================================
    return PMInteractionResult(
        points=tuple((p, m) for p, m in zip(envelope_P, envelope_M, strict=True)),
        Pu_0_kN=Pu_0_kN,
        Mu_0_kNm=Mu_0_kNm,
        Pu_bal_kN=Pu_bal_kN,
        Mu_bal_kNm=Mu_bal_kNm,
        fck=fck,
        fy=fy,
        b_mm=b_mm,
        D_mm=D_mm,
        Asc_mm2=Asc_mm2,
        d_prime_mm=d_prime_mm,
        warnings=tuple(warnings),
    )
