# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       long_column
Description:  Long (slender) column design per IS 456:2000 Cl 39.7.
Traceability: Functions are decorated with @clause for IS 456 clause references.

Implements:
- Additional moment calculation for slender columns
- Initial moment from end moments (braced vs unbraced)
- Design moment augmentation and capacity check

The procedure combines:
- Slenderness classification (Cl 25.1.2)
- Additional eccentricity and moment (Cl 39.7.1)
- k-factor reduction (Cl 39.7.1.1)
- End-moment combination (Cl 39.7.1 for braced, Cl 39.7.1 for unbraced)
- Final capacity check via biaxial or uniaxial interaction

References:
    IS 456:2000, Cl. 39.7, 39.7.1, 39.7.1.1, 25.1.2, 25.3.1
    SP:16:1980 Design Aids for Reinforced Concrete
    Pillai & Menon, "Reinforced Concrete Design", 3rd Ed., Ch. 13
"""

from __future__ import annotations

import math

from structural_lib.codes.is456.column._common import _calculate_puz
from structural_lib.codes.is456.column.axial import classify_column
from structural_lib.codes.is456.column.biaxial import biaxial_bending_check
from structural_lib.codes.is456.column.slenderness import _additional_eccentricity
from structural_lib.codes.is456.column.uniaxial import (
    design_short_column_uniaxial,
    pm_interaction_curve,
)
from structural_lib.codes.is456.common.constants import (
    MAX_SLENDERNESS_RATIO,
)
from structural_lib.codes.is456.traceability import clause
from structural_lib.core.data_types import (
    ColumnClassification,
    LongColumnResult,
)
from structural_lib.core.errors import DimensionError, MaterialError

__all__ = [
    "design_long_column",
]

# Tolerance for near-zero values
_TOL: float = 1e-6


@clause("39.7")
def design_long_column(
    Pu_kN: float,
    M1x_kNm: float,
    M2x_kNm: float,
    M1y_kNm: float,
    M2y_kNm: float,
    b_mm: float,
    D_mm: float,
    lex_mm: float,
    ley_mm: float,
    fck: float,
    fy: float,
    Asc_mm2: float,
    d_prime_mm: float,
    braced: bool = True,
) -> LongColumnResult:
    """Design a long (slender) column per IS 456 Cl 39.7.

    For slender columns (le/D >= 12), the code requires an additional
    moment to account for P-delta effects. The procedure:

    1. Classify per axis: le/D >= 12 → SLENDER
    2. Calculate additional eccentricity eadd = le² / (2000 × D)
    3. Calculate additional moment Ma = Pu × eadd
    4. Reduce by k-factor: Ma_red = k × Ma
    5. Combine with end moments to get design moment
    6. Check via biaxial or uniaxial interaction

    Sign convention for end moments:
    - Same sign → single curvature bending
    - Opposite sign → double curvature bending
    - |M2| must be >= |M1| (M2 is the larger end moment)

    Args:
        Pu_kN: Factored axial load (kN). Must be >= 0.
        M1x_kNm: Smaller end moment about x-axis (kN·m).
        M2x_kNm: Larger end moment about x-axis (kN·m), |M2x| >= |M1x|.
        M1y_kNm: Smaller end moment about y-axis (kN·m).
        M2y_kNm: Larger end moment about y-axis (kN·m), |M2y| >= |M1y|.
        b_mm: Column width (mm). Must be > 0.
        D_mm: Column depth (mm). Must be > 0.
        lex_mm: Effective length about x-axis (mm). Must be > 0.
        ley_mm: Effective length about y-axis (mm). Must be > 0.
        fck: Concrete compressive strength (N/mm²). Must be > 0.
        fy: Steel yield strength (N/mm²). Must be > 0.
        Asc_mm2: Total longitudinal steel area (mm²). Must be > 0.
        d_prime_mm: Cover to centroid of reinforcement (mm). Must be > 0.
        braced: True if column is braced against sidesway (default True).

    Returns:
        LongColumnResult with augmented design moments and capacity check.

    Raises:
        DimensionError: If geometric dimensions are invalid or le/D > 60.
        MaterialError: If material properties are out of range.

    References:
        IS 456:2000, Cl. 39.7, 39.7.1, 39.7.1.1
    """
    # ===========================================================
    # 1. Input validation
    # ===========================================================
    if Pu_kN < 0:
        raise DimensionError(
            f"Pu_kN must be >= 0 (compression), got {Pu_kN}",
            details={"Pu_kN": Pu_kN},
            clause_ref="Cl. 39.7",
        )
    if b_mm <= 0:
        raise DimensionError(
            f"b_mm must be > 0, got {b_mm}",
            details={"b_mm": b_mm},
            clause_ref="Cl. 39.7",
        )
    if D_mm <= 0:
        raise DimensionError(
            f"D_mm must be > 0, got {D_mm}",
            details={"D_mm": D_mm},
            clause_ref="Cl. 39.7",
        )
    if lex_mm <= 0:
        raise DimensionError(
            f"lex_mm must be > 0, got {lex_mm}",
            details={"lex_mm": lex_mm},
            clause_ref="Cl. 39.7",
        )
    if ley_mm <= 0:
        raise DimensionError(
            f"ley_mm must be > 0, got {ley_mm}",
            details={"ley_mm": ley_mm},
            clause_ref="Cl. 39.7",
        )
    if fck <= 0:
        raise MaterialError(
            f"fck must be > 0, got {fck}",
            details={"fck": fck},
            clause_ref="Cl. 39.7",
        )
    if fy <= 0:
        raise MaterialError(
            f"fy must be > 0, got {fy}",
            details={"fy": fy},
            clause_ref="Cl. 39.7",
        )
    if Asc_mm2 <= 0:
        raise DimensionError(
            f"Asc_mm2 must be > 0, got {Asc_mm2}",
            details={"Asc_mm2": Asc_mm2},
            clause_ref="Cl. 39.7",
        )
    if d_prime_mm <= 0:
        raise DimensionError(
            f"d_prime_mm must be > 0, got {d_prime_mm}",
            details={"d_prime_mm": d_prime_mm},
            clause_ref="Cl. 39.7",
        )

    warnings: list[str] = []

    # ===========================================================
    # 2. Slenderness classification per axis (IS 456 Cl 25.1.2)
    # ===========================================================
    slenderness_ratio_x = lex_mm / D_mm
    slenderness_ratio_y = ley_mm / b_mm

    # IS 456 Cl 25.3.1: reject if le/D > 60
    if slenderness_ratio_x > MAX_SLENDERNESS_RATIO:
        raise DimensionError(
            f"le_x/D = {slenderness_ratio_x:.1f} exceeds IS 456 Cl 25.3.1 "
            f"limit of {MAX_SLENDERNESS_RATIO:.0f}",
            details={"lex_mm": lex_mm, "D_mm": D_mm},
            clause_ref="Cl. 25.3.1",
        )
    if slenderness_ratio_y > MAX_SLENDERNESS_RATIO:
        raise DimensionError(
            f"le_y/b = {slenderness_ratio_y:.1f} exceeds IS 456 Cl 25.3.1 "
            f"limit of {MAX_SLENDERNESS_RATIO:.0f}",
            details={"ley_mm": ley_mm, "b_mm": b_mm},
            clause_ref="Cl. 25.3.1",
        )

    # IS 456 Cl 25.1.2: short when le/D < 12
    classification_x = classify_column(lex_mm, D_mm)
    classification_y = classify_column(ley_mm, b_mm)

    is_slender_x = classification_x == ColumnClassification.SLENDER
    is_slender_y = classification_y == ColumnClassification.SLENDER

    # ===========================================================
    # 3. Additional eccentricity and moment (IS 456 Cl 39.7.1)
    # ===========================================================
    # IS 456 Cl 39.7.1: eadd = le² / (2000 × D)
    if is_slender_x:
        eadd_x_mm = _additional_eccentricity(lex_mm, D_mm)
        # IS 456 Cl 39.7.1: Ma = Pu × eadd
        Max_kNm = Pu_kN * eadd_x_mm / 1000.0
    else:
        eadd_x_mm = 0.0
        Max_kNm = 0.0

    if is_slender_y:
        eadd_y_mm = _additional_eccentricity(ley_mm, b_mm)
        # IS 456 Cl 39.7.1: Ma = Pu × eadd
        May_kNm = Pu_kN * eadd_y_mm / 1000.0
    else:
        eadd_y_mm = 0.0
        May_kNm = 0.0

    # If short on BOTH axes, warn and route to direct check
    if not is_slender_x and not is_slender_y:
        warnings.append(
            "Column is short on both axes (le/D < 12). "
            "No additional moment required — routed to direct check."
        )

    # ===========================================================
    # 4. k-factor reduction (IS 456 Cl 39.7.1.1)
    # ===========================================================
    # IS 456 Cl 39.7.1.1: k = (Puz - Pu) / (Puz - Pb) ≤ 1.0
    Puz_kN = _calculate_puz(b_mm, D_mm, fck, fy, Asc_mm2)

    # Get balanced point from P-M interaction curve
    pm_result = pm_interaction_curve(
        b_mm=b_mm,
        D_mm=D_mm,
        fck=fck,
        fy=fy,
        Asc_mm2=Asc_mm2,
        d_prime_mm=d_prime_mm,
    )
    Pb_kN = pm_result.Pu_bal_kN

    # k-factor calculation
    if Pu_kN > Puz_kN:
        warnings.append(
            f"Pu ({Pu_kN:.1f} kN) exceeds Puz ({Puz_kN:.1f} kN) "
            "— section is overloaded, k set to 0"
        )
        k = 0.0
    elif abs(Pu_kN) < _TOL:
        # IS 456 Cl 39.7.1: Pu = 0 → no additional moment
        k = 1.0
    else:
        denom = Puz_kN - Pb_kN
        if abs(denom) < _TOL:
            # Puz ≈ Pb — degenerate case
            k = 1.0
        else:
            # IS 456 Cl 39.7.1.1: k = (Puz - Pu) / (Puz - Pb)
            k_raw = (Puz_kN - Pu_kN) / denom
            # Clamp to [0.0, 1.0]
            k = max(0.0, min(1.0, k_raw))

    # Reduced additional moments
    Max_reduced_kNm = k * Max_kNm
    May_reduced_kNm = k * May_kNm

    # ===========================================================
    # 5. Initial moment from end moments (IS 456 Cl 39.7.1)
    # ===========================================================
    if braced:
        # IS 456 Cl 39.7.1 (braced): Mi = 0.4*M1 + 0.6*M2, but Mi >= 0.4*M2
        Mi_x = 0.4 * M1x_kNm + 0.6 * M2x_kNm
        Mi_x = max(Mi_x, 0.4 * M2x_kNm)
        Mi_y = 0.4 * M1y_kNm + 0.6 * M2y_kNm
        Mi_y = max(Mi_y, 0.4 * M2y_kNm)
    else:
        # IS 456 Cl 39.7.1 (unbraced): Mi = M2
        Mi_x = M2x_kNm
        Mi_y = M2y_kNm

    # ===========================================================
    # 6. Design moment = Mi + Ma_reduced (IS 456 Cl 39.7)
    # ===========================================================
    # IS 456 Cl 39.7: M_design = Mi + Ma_reduced
    Mux_design_raw = Mi_x + Max_reduced_kNm
    Muy_design_raw = Mi_y + May_reduced_kNm

    # IS 456 Cl 39.7: Lower bound — M_design >= M2 (always)
    Mux_design_kNm = max(Mux_design_raw, M2x_kNm)
    Muy_design_kNm = max(Muy_design_raw, M2y_kNm)

    # Use absolute values for capacity check (moments are magnitudes)
    Mux_abs = abs(Mux_design_kNm)
    Muy_abs = abs(Muy_design_kNm)

    # ===========================================================
    # 7. Capacity check via biaxial or uniaxial interaction
    # ===========================================================
    if Muy_abs < _TOL and Mux_abs < _TOL:
        # Pure axial case — no moment, trivially safe if Pu < Puz
        interaction_ratio = Pu_kN / Puz_kN if Puz_kN > _TOL else float("inf")
        is_safe = interaction_ratio <= 1.0
        governing_check = "axial"
    elif Muy_abs < _TOL:
        # Uniaxial about x only
        uniaxial_result = design_short_column_uniaxial(
            Pu_kN=Pu_kN,
            Mu_kNm=Mux_abs,
            b_mm=b_mm,
            D_mm=D_mm,
            le_mm=max(lex_mm, ley_mm),
            fck=fck,
            fy=fy,
            Asc_mm2=Asc_mm2,
            d_prime_mm=d_prime_mm,
        )
        interaction_ratio = uniaxial_result.utilization_ratio
        is_safe = uniaxial_result.is_safe
        governing_check = "uniaxial_x"
        warnings.extend(uniaxial_result.warnings)
    elif Mux_abs < _TOL:
        # Uniaxial about y only — swap b and D for bending about y
        uniaxial_result = design_short_column_uniaxial(
            Pu_kN=Pu_kN,
            Mu_kNm=Muy_abs,
            b_mm=D_mm,
            D_mm=b_mm,
            le_mm=max(lex_mm, ley_mm),
            fck=fck,
            fy=fy,
            Asc_mm2=Asc_mm2,
            d_prime_mm=d_prime_mm,
        )
        interaction_ratio = uniaxial_result.utilization_ratio
        is_safe = uniaxial_result.is_safe
        governing_check = "uniaxial_y"
        warnings.extend(uniaxial_result.warnings)
    else:
        # Biaxial bending check (IS 456 Cl 39.6)
        biaxial_result = biaxial_bending_check(
            Pu_kN=Pu_kN,
            Mux_kNm=Mux_abs,
            Muy_kNm=Muy_abs,
            b_mm=b_mm,
            D_mm=D_mm,
            le_mm=max(lex_mm, ley_mm),
            fck=fck,
            fy=fy,
            Asc_mm2=Asc_mm2,
            d_prime_mm=d_prime_mm,
        )
        interaction_ratio = biaxial_result.interaction_ratio
        is_safe = biaxial_result.is_safe
        governing_check = "biaxial"
        warnings.extend(biaxial_result.warnings)

    # NaN/Inf guard on output
    if math.isnan(interaction_ratio) or math.isinf(interaction_ratio):
        is_safe = False

    return LongColumnResult(
        Pu_kN=Pu_kN,
        Mux_design_kNm=round(Mux_design_kNm, 2),
        Muy_design_kNm=round(Muy_design_kNm, 2),
        is_safe=is_safe,
        classification_x=classification_x,
        classification_y=classification_y,
        is_slender_x=is_slender_x,
        is_slender_y=is_slender_y,
        eadd_x_mm=round(eadd_x_mm, 2),
        eadd_y_mm=round(eadd_y_mm, 2),
        Max_kNm=round(Max_kNm, 2),
        May_kNm=round(May_kNm, 2),
        k=round(k, 4),
        Max_reduced_kNm=round(Max_reduced_kNm, 2),
        May_reduced_kNm=round(May_reduced_kNm, 2),
        interaction_ratio=round(interaction_ratio, 4),
        governing_check=governing_check,
        Puz_kN=round(Puz_kN, 2),
        Pb_kN=round(Pb_kN, 2),
        b_mm=b_mm,
        D_mm=D_mm,
        lex_mm=lex_mm,
        ley_mm=ley_mm,
        braced=braced,
        warnings=tuple(warnings),
    )
