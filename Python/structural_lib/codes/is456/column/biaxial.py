# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       biaxial
Description:  Biaxial bending check for columns per IS 456:2000 Cl 39.6.
Traceability: Functions are decorated with @clause for IS 456 clause references.

Implements:
- Bresler load contour formula (Cl 39.6)
- Puz: pure axial crush capacity (Cl 39.6a)
- αn exponent interpolation

References:
    IS 456:2000, Cl. 39.6
    SP:16:1980 Design Aids, Chart 63-64
    Pillai & Menon, "Reinforced Concrete Design", 3rd Ed., Ch. 13
"""

from __future__ import annotations

import math

from structural_lib.codes.is456.column._common import _calculate_puz
from structural_lib.codes.is456.column.axial import classify_column
from structural_lib.codes.is456.column.uniaxial import pm_interaction_curve
from structural_lib.codes.is456.traceability import clause
from structural_lib.core.data_types import (
    ColumnBiaxialResult,
    ColumnClassification,
    PMInteractionResult,
)
from structural_lib.core.errors import (
    CalculationError,
    DimensionError,
    MaterialError,
)
from structural_lib.core.numerics import clamp, safe_divide

__all__ = [
    "biaxial_bending_check",
]

# ---------------------------------------------------------------------------
# IS 456 Cl 39.6: alpha_n interpolation bounds
# ---------------------------------------------------------------------------
_ALPHA_N_MIN: float = 1.0
_ALPHA_N_MAX: float = 2.0
_PU_PUZ_LOWER: float = 0.2
_PU_PUZ_UPPER: float = 0.8

# Tolerance for near-zero capacity checks
_CAPACITY_TOL: float = 1e-6


def _calculate_alpha_n(Pu_kN: float, Puz_kN: float) -> float:
    """Calculate Bresler exponent alpha_n per IS 456 Cl 39.6.

    IS 456 Cl 39.6:
    - Pu/Puz <= 0.2 -> alpha_n = 1.0
    - Pu/Puz >= 0.8 -> alpha_n = 2.0
    - Between: alpha_n = 1.0 + (Pu/Puz - 0.2) / 0.6

    Args:
        Pu_kN: Applied axial load (kN).
        Puz_kN: Pure axial crush capacity (kN).

    Returns:
        alpha_n clamped to [1.0, 2.0].
    """
    ratio = safe_divide(Pu_kN, Puz_kN, default=0.0)

    # IS 456 Cl 39.6: linear interpolation, clamped to [1.0, 2.0]
    alpha_n_raw = _ALPHA_N_MIN + safe_divide(
        ratio - _PU_PUZ_LOWER,
        _PU_PUZ_UPPER - _PU_PUZ_LOWER,
        default=0.0,
    )
    return clamp(alpha_n_raw, _ALPHA_N_MIN, _ALPHA_N_MAX)


def _moment_at_axial_load(pm_result: PMInteractionResult, Pu_kN: float) -> float:
    """Interpolate P-M interaction curve to find moment capacity at given Pu.

    Scans the P-M envelope points to find all segments that bracket
    Pu_kN, then linearly interpolates and returns the maximum moment
    capacity (outer envelope).

    Args:
        pm_result: P-M interaction curve result.
        Pu_kN: Axial load at which to find moment capacity (kN).

    Returns:
        Moment capacity (kNm) at the given axial load.
        Returns 0.0 if Pu exceeds the pure axial capacity.
    """
    points = pm_result.points

    if not points:
        return 0.0

    # If Pu exceeds pure axial capacity, no moment capacity
    if Pu_kN > pm_result.Pu_0_kN:
        return 0.0

    # If Pu is zero or negative, return pure bending capacity
    if Pu_kN <= 0.0:
        return pm_result.Mu_0_kNm

    # Find the maximum moment at any point where P brackets Pu_kN.
    # The P-M envelope may have multiple segments where P passes through Pu_kN
    # (compression-controlled and tension-controlled branches).
    # We want the maximum moment capacity (outer envelope).
    best_moment = 0.0

    for i in range(len(points) - 1):
        P_i, M_i = points[i]
        P_next, M_next = points[i + 1]

        # Check if Pu_kN is bracketed by this segment
        P_lo = min(P_i, P_next)
        P_hi = max(P_i, P_next)

        if P_lo <= Pu_kN <= P_hi:
            # Linear interpolation parameter
            dP = P_next - P_i
            if abs(dP) < _CAPACITY_TOL:
                # Segment is nearly horizontal in P — use max moment
                moment = max(abs(M_i), abs(M_next))
            else:
                t = safe_divide(Pu_kN - P_i, dP, default=0.0)
                t = clamp(t, 0.0, 1.0)
                moment = abs(M_i + t * (M_next - M_i))

            best_moment = max(best_moment, moment)

    return best_moment


@clause("39.6")
def biaxial_bending_check(
    Pu_kN: float,
    Mux_kNm: float,
    Muy_kNm: float,
    b_mm: float,
    D_mm: float,
    le_mm: float,
    fck: float,
    fy: float,
    Asc_mm2: float,
    d_prime_mm: float,
    l_unsupported_mm: float | None = None,
) -> ColumnBiaxialResult:
    """Check column under biaxial bending per IS 456 Cl 39.6.

    Implements the Bresler load contour formula:
        (Mux / Mux1)^alpha_n + (Muy / Muy1)^alpha_n <= 1.0

    where Mux1, Muy1 are the uniaxial moment capacities at the applied
    axial load Pu, obtained from P-M interaction curves.

    Reinforcement is assumed symmetrical: Asc_mm2 / 2 on each face,
    placed at d_prime_mm from the nearest face.

    Args:
        Pu_kN: Applied factored axial load (kN). Must be >= 0.
        Mux_kNm: Applied factored moment about x-axis (kNm). Must be >= 0.
        Muy_kNm: Applied factored moment about y-axis (kNm). Must be >= 0.
        b_mm: Column width perpendicular to x-axis bending (mm). Must be > 0.
            When computing Muy1 (bending about y), b_mm acts as the depth
            in the bending direction.
        D_mm: Column depth in x-axis bending direction (mm). Must be > 0.
            When computing Mux1 (bending about x), D_mm acts as the depth
            in the bending direction.
        le_mm: Effective length of column (mm). Must be > 0.
        fck: Characteristic compressive strength of concrete (N/mm2).
            IS 456 range: 15-80.
        fy: Characteristic yield strength of steel (N/mm2).
            IS 456 range: 250-550.
        Asc_mm2: Total area of longitudinal reinforcement (mm2). Must be > 0.
        d_prime_mm: Distance from nearest face to centroid of steel (mm).
            Must be > 0 and less than half the smaller dimension.
        l_unsupported_mm: Unsupported length (mm) for slenderness warning.
            If None, slenderness is checked using le_mm only.

    Returns:
        ColumnBiaxialResult with interaction ratio and safety status.

    Raises:
        DimensionError: If geometric dimensions are invalid.
        MaterialError: If material properties are out of range.
        CalculationError: If numerical issues are encountered.

    References:
        IS 456:2000, Cl. 39.6 (biaxial bending)
        IS 456:2000, Cl. 39.6a (Puz formula)
        IS 456:2000, Cl. 39.5 (P-M interaction envelope)
        IS 456:2000, Cl. 25.1.2 (column classification)
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
            clause_ref="Cl. 39.6",
        )
    if D_mm <= 0:
        raise DimensionError(
            f"Column depth D_mm must be > 0, got {D_mm}",
            details={"D_mm": D_mm},
            clause_ref="Cl. 39.6",
        )
    if le_mm <= 0:
        raise DimensionError(
            f"Effective length le_mm must be > 0, got {le_mm}",
            details={"le_mm": le_mm},
            clause_ref="Cl. 25.1.2",
        )

    # d_prime_mm must be valid for BOTH bending directions
    min_half_dim = min(b_mm, D_mm) / 2.0
    if d_prime_mm <= 0 or d_prime_mm >= min_half_dim:
        raise DimensionError(
            f"Cover d_prime_mm must be > 0 and < min(b,D)/2={min_half_dim}, "
            f"got {d_prime_mm}",
            details={"d_prime_mm": d_prime_mm, "b_mm": b_mm, "D_mm": D_mm},
            clause_ref="Cl. 26.4",
        )

    # --- Materials ---
    if fck <= 0:
        raise MaterialError(
            f"fck must be > 0, got {fck}",
            details={"fck": fck},
            clause_ref="Cl. 39.6",
        )
    if fy <= 0:
        raise MaterialError(
            f"fy must be > 0, got {fy}",
            details={"fy": fy},
            clause_ref="Cl. 39.6",
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
            f"Axial load Pu_kN must be >= 0 for compression member, got {Pu_kN}",
            details={"Pu_kN": Pu_kN},
            clause_ref="Cl. 39.6",
        )
    if Mux_kNm < 0:
        raise DimensionError(
            f"Moment Mux_kNm must be >= 0, got {Mux_kNm}",
            details={"Mux_kNm": Mux_kNm},
            clause_ref="Cl. 39.6",
        )
    if Muy_kNm < 0:
        raise DimensionError(
            f"Moment Muy_kNm must be >= 0, got {Muy_kNm}",
            details={"Muy_kNm": Muy_kNm},
            clause_ref="Cl. 39.6",
        )

    # --- Steel area ---
    if Asc_mm2 <= 0:
        raise DimensionError(
            f"Total steel area Asc_mm2 must be > 0, got {Asc_mm2}",
            details={"Asc_mm2": Asc_mm2},
            clause_ref="Cl. 26.5.3.1",
        )

    # ===========================================================
    # 2. Column classification
    # ===========================================================
    # IS 456 Cl 25.1.2: use the larger lateral dimension for classification
    classification = classify_column(le_mm, max(b_mm, D_mm))
    if classification == ColumnClassification.SLENDER:
        warnings.append(
            "Column classified as slender (le/D >= 12). "
            "Additional moment per Cl 39.7 required. "
            "This function does NOT apply the slenderness moment."
        )

    # ===========================================================
    # 3. Calculate Puz (IS 456 Cl 39.6a)
    # ===========================================================
    # IS 456 Cl 39.6a: Puz = 0.45 * fck * Ac + 0.75 * fy * Asc
    Puz_kN = _calculate_puz(b_mm, D_mm, fck, fy, Asc_mm2)

    # Check Puz is positive (sanity check)
    if Puz_kN <= _CAPACITY_TOL:
        raise CalculationError(
            f"Puz is zero or negative ({Puz_kN:.2f} kN). "
            "Check section and reinforcement.",
            details={"Puz_kN": Puz_kN, "b_mm": b_mm, "D_mm": D_mm},
            clause_ref="Cl. 39.6a",
        )

    # Check if axial load exceeds crush capacity
    if Pu_kN >= Puz_kN:
        return ColumnBiaxialResult(
            Pu_kN=Pu_kN,
            Mux_kNm=Mux_kNm,
            Muy_kNm=Muy_kNm,
            Mux1_kNm=0.0,
            Muy1_kNm=0.0,
            Puz_kN=round(Puz_kN, 2),
            alpha_n=_ALPHA_N_MAX,
            interaction_ratio=float("inf"),
            is_safe=False,
            classification=classification,
            clause_ref="Cl. 39.6",
            warnings=tuple(
                [
                    *warnings,
                    f"Pu ({Pu_kN:.1f} kN) >= Puz ({Puz_kN:.1f} kN). "
                    "Axial capacity exceeded.",
                ]
            ),
        )

    # ===========================================================
    # 4. Calculate alpha_n (IS 456 Cl 39.6)
    # ===========================================================
    # IS 456 Cl 39.6: alpha_n depends on Pu/Puz ratio
    alpha_n = _calculate_alpha_n(Pu_kN, Puz_kN)

    # ===========================================================
    # 5. Get Mux1 from P-M curve (bending about x-axis)
    # ===========================================================
    # Bending about x-axis: D_mm is depth in bending direction, b_mm is width
    pm_x = pm_interaction_curve(
        b_mm=b_mm,
        D_mm=D_mm,
        fck=fck,
        fy=fy,
        Asc_mm2=Asc_mm2,
        d_prime_mm=d_prime_mm,
    )
    Mux1_kNm = _moment_at_axial_load(pm_x, Pu_kN)

    # ===========================================================
    # 6. Get Muy1 from P-M curve (bending about y-axis)
    # ===========================================================
    # CRITICAL: bending about y-axis — swap b and D
    # b_mm becomes depth in bending direction, D_mm becomes width
    pm_y = pm_interaction_curve(
        b_mm=D_mm,  # Width perpendicular to y-axis bending
        D_mm=b_mm,  # Depth in y-axis bending direction
        fck=fck,
        fy=fy,
        Asc_mm2=Asc_mm2,
        d_prime_mm=d_prime_mm,
    )
    Muy1_kNm = _moment_at_axial_load(pm_y, Pu_kN)

    # ===========================================================
    # 7. Handle degenerate cases
    # ===========================================================
    # If both applied moments are zero, the check trivially passes
    if abs(Mux_kNm) < _CAPACITY_TOL and abs(Muy_kNm) < _CAPACITY_TOL:
        return ColumnBiaxialResult(
            Pu_kN=Pu_kN,
            Mux_kNm=Mux_kNm,
            Muy_kNm=Muy_kNm,
            Mux1_kNm=round(Mux1_kNm, 2),
            Muy1_kNm=round(Muy1_kNm, 2),
            Puz_kN=round(Puz_kN, 2),
            alpha_n=round(alpha_n, 4),
            interaction_ratio=0.0,
            is_safe=True,
            classification=classification,
            clause_ref="Cl. 39.6",
            warnings=tuple(warnings),
        )

    # If uniaxial capacities are zero or very small, section has no capacity
    if Mux1_kNm < _CAPACITY_TOL:
        warnings.append(
            f"Mux1 capacity is near zero ({Mux1_kNm:.4f} kNm) at "
            f"Pu={Pu_kN:.1f} kN. Section cannot resist x-axis bending."
        )
        if abs(Mux_kNm) > _CAPACITY_TOL:
            return ColumnBiaxialResult(
                Pu_kN=Pu_kN,
                Mux_kNm=Mux_kNm,
                Muy_kNm=Muy_kNm,
                Mux1_kNm=round(Mux1_kNm, 2),
                Muy1_kNm=round(Muy1_kNm, 2),
                Puz_kN=round(Puz_kN, 2),
                alpha_n=round(alpha_n, 4),
                interaction_ratio=float("inf"),
                is_safe=False,
                classification=classification,
                clause_ref="Cl. 39.6",
                warnings=tuple(warnings),
            )

    if Muy1_kNm < _CAPACITY_TOL:
        warnings.append(
            f"Muy1 capacity is near zero ({Muy1_kNm:.4f} kNm) at "
            f"Pu={Pu_kN:.1f} kN. Section cannot resist y-axis bending."
        )
        if abs(Muy_kNm) > _CAPACITY_TOL:
            return ColumnBiaxialResult(
                Pu_kN=Pu_kN,
                Mux_kNm=Mux_kNm,
                Muy_kNm=Muy_kNm,
                Mux1_kNm=round(Mux1_kNm, 2),
                Muy1_kNm=round(Muy1_kNm, 2),
                Puz_kN=round(Puz_kN, 2),
                alpha_n=round(alpha_n, 4),
                interaction_ratio=float("inf"),
                is_safe=False,
                classification=classification,
                clause_ref="Cl. 39.6",
                warnings=tuple(warnings),
            )

    # ===========================================================
    # 8. Compute interaction ratio (Bresler load contour)
    # ===========================================================
    # IS 456 Cl 39.6: (Mux/Mux1)^alpha_n + (Muy/Muy1)^alpha_n <= 1.0
    ratio_x = safe_divide(Mux_kNm, Mux1_kNm, default=0.0)
    ratio_y = safe_divide(Muy_kNm, Muy1_kNm, default=0.0)

    # IS 456 Cl 39.6: Bresler formula
    interaction_ratio = ratio_x**alpha_n + ratio_y**alpha_n

    # NaN/Inf guard on output
    if math.isnan(interaction_ratio) or math.isinf(interaction_ratio):
        raise CalculationError(
            "Interaction ratio is NaN or Inf. "
            f"ratio_x={ratio_x}, ratio_y={ratio_y}, alpha_n={alpha_n}",
            details={
                "Mux_kNm": Mux_kNm,
                "Muy_kNm": Muy_kNm,
                "Mux1_kNm": Mux1_kNm,
                "Muy1_kNm": Muy1_kNm,
                "alpha_n": alpha_n,
            },
            clause_ref="Cl. 39.6",
        )

    is_safe = interaction_ratio <= 1.0

    return ColumnBiaxialResult(
        Pu_kN=Pu_kN,
        Mux_kNm=Mux_kNm,
        Muy_kNm=Muy_kNm,
        Mux1_kNm=round(Mux1_kNm, 2),
        Muy1_kNm=round(Muy1_kNm, 2),
        Puz_kN=round(Puz_kN, 2),
        alpha_n=round(alpha_n, 4),
        interaction_ratio=round(interaction_ratio, 4),
        is_safe=is_safe,
        classification=classification,
        clause_ref="Cl. 39.6",
        warnings=tuple(warnings),
    )
