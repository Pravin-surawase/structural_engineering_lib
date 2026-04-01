# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       slenderness
Description:  Additional moment for slender columns per IS 456:2000 Cl 39.7.1.
Traceability: Functions are decorated with @clause for IS 456 clause references.

Implements:
- Additional eccentricity due to slenderness (Cl 39.7.1)
- k-factor reduction (Cl 39.7.1.1)

References:
    IS 456:2000, Cl. 39.7.1, 39.7.1.1
    SP:16:1980 Design Aids for Reinforced Concrete
    Pillai & Menon, "Reinforced Concrete Design", 3rd Ed., Ch. 13
"""

from __future__ import annotations

from structural_lib.codes.is456.column.uniaxial import pm_interaction_curve
from structural_lib.codes.is456.common.constants import (
    MAX_SLENDERNESS_RATIO,
    SHORT_COLUMN_SLENDERNESS_LIMIT,
)
from structural_lib.codes.is456.traceability import clause
from structural_lib.core.data_types import AdditionalMomentResult
from structural_lib.core.errors import DimensionError

__all__ = [
    "calculate_additional_moment",
]

# ---------------------------------------------------------------------------
# IS 456 Cl 39.6a: Puz coefficients
# Puz = 0.45 * fck * Ac + 0.75 * fy * Asc
# 0.45 = 0.67 * fck / gamma_c where gamma_c = 1.5
# 0.75 = fy / (gamma_s * factor) — IS 456 specified
# ---------------------------------------------------------------------------
_PUZ_CONCRETE_COEFF: float = 0.45
_PUZ_STEEL_COEFF: float = 0.75

# IS 456 Cl 39.7.1: eadd denominator constant
_EADD_DENOMINATOR: float = 2000.0


def _calculate_puz(
    b_mm: float,
    D_mm: float,
    fck: float,
    fy: float,
    Asc_mm2: float,
) -> float:
    """Calculate pure axial crush capacity per IS 456 Cl 39.6a.

    Returns:
        Puz in kN.
    """
    Ag_mm2 = b_mm * D_mm
    Ac_mm2 = Ag_mm2 - Asc_mm2
    Puz_N = _PUZ_CONCRETE_COEFF * fck * Ac_mm2 + _PUZ_STEEL_COEFF * fy * Asc_mm2
    return Puz_N / 1000.0


def _additional_eccentricity(le_mm: float, D_mm: float) -> float:
    """Calculate additional eccentricity per IS 456 Cl 39.7.1.

    Formula: eadd = D × (le/D)² / 2000 = le² / (2000 × D)

    Args:
        le_mm: Effective length (mm).
        D_mm: Lateral dimension in plane of bending (mm).

    Returns:
        Additional eccentricity in mm.
    """
    return (le_mm * le_mm) / (_EADD_DENOMINATOR * D_mm)


@clause("39.7.1")
def calculate_additional_moment(
    Pu_kN: float,
    b_mm: float,
    D_mm: float,
    lex_mm: float,
    ley_mm: float,
    fck: float,
    fy: float,
    Asc_mm2: float,
    d_prime_mm: float,
) -> AdditionalMomentResult:
    """Calculate additional moment for slender columns per IS 456 Cl 39.7.1.

    For slender columns (le/D >= 12), the code requires an additional
    moment Ma = Pu × eadd to account for P-delta effects, where:

        eadd = D × (le/D)² / 2000

    The additional moment may be reduced by factor k per Cl 39.7.1.1:

        k = (Puz - Pu) / (Puz - Pb) ≤ 1.0

    Args:
        Pu_kN: Factored axial load (kN). Must be >= 0.
        b_mm: Column width — y-axis dimension (mm). Must be > 0.
        D_mm: Column depth — x-axis dimension (mm). Must be > 0.
        lex_mm: Effective length about x-axis (mm). Must be > 0.
        ley_mm: Effective length about y-axis (mm). Must be > 0.
        fck: Concrete characteristic strength (N/mm²). Must be > 0.
        fy: Steel yield strength (N/mm²). Must be > 0.
        Asc_mm2: Total longitudinal steel area (mm²). Must be >= 0.
        d_prime_mm: Cover to centroid of reinforcement (mm). Must be >= 0.

    Returns:
        AdditionalMomentResult with additional eccentricities, moments,
        k-factor, and reduced moments for both axes.

    Raises:
        DimensionError: If any dimension is non-positive or Pu is negative.

    References:
        IS 456:2000, Cl. 39.7.1, 39.7.1.1
    """
    # --- Input validation ---
    if Pu_kN < 0:
        raise DimensionError("Pu_kN must be >= 0 (compression)")
    if b_mm <= 0:
        raise DimensionError("b_mm must be > 0")
    if D_mm <= 0:
        raise DimensionError("D_mm must be > 0")
    if lex_mm <= 0:
        raise DimensionError("lex_mm must be > 0")
    if ley_mm <= 0:
        raise DimensionError("ley_mm must be > 0")
    if fck <= 0:
        raise DimensionError("fck must be > 0")
    if fy <= 0:
        raise DimensionError("fy must be > 0")
    if Asc_mm2 < 0:
        raise DimensionError("Asc_mm2 must be >= 0")
    if d_prime_mm < 0:
        raise DimensionError("d_prime_mm must be >= 0")

    warnings: list[str] = []

    # --- Slenderness classification per axis ---
    slenderness_ratio_x = lex_mm / D_mm
    slenderness_ratio_y = ley_mm / b_mm

    is_slender_x = slenderness_ratio_x >= SHORT_COLUMN_SLENDERNESS_LIMIT
    is_slender_y = slenderness_ratio_y >= SHORT_COLUMN_SLENDERNESS_LIMIT

    # Warn if slenderness approaches or exceeds IS 456 Cl 25.3.1 limit
    _APPROACH_THRESHOLD = 40.0
    if slenderness_ratio_x >= MAX_SLENDERNESS_RATIO:
        warnings.append(
            f"le_x/D = {slenderness_ratio_x:.1f} exceeds IS 456 Cl 25.3.1 "
            f"limit of {MAX_SLENDERNESS_RATIO:.0f}"
        )
    elif slenderness_ratio_x >= _APPROACH_THRESHOLD:
        warnings.append(
            f"le_x/D = {slenderness_ratio_x:.1f} approaching IS 456 Cl 25.3.1 "
            f"slenderness limit of {MAX_SLENDERNESS_RATIO:.0f}"
        )
    if slenderness_ratio_y >= MAX_SLENDERNESS_RATIO:
        warnings.append(
            f"le_y/b = {slenderness_ratio_y:.1f} exceeds IS 456 Cl 25.3.1 "
            f"limit of {MAX_SLENDERNESS_RATIO:.0f}"
        )
    elif slenderness_ratio_y >= _APPROACH_THRESHOLD:
        warnings.append(
            f"le_y/b = {slenderness_ratio_y:.1f} approaching IS 456 Cl 25.3.1 "
            f"slenderness limit of {MAX_SLENDERNESS_RATIO:.0f}"
        )

    # --- Additional eccentricity and moment per axis ---
    # IS 456 Cl 39.7.1: eadd = D × (le/D)² / 2000
    if is_slender_x:
        eadd_x_mm = _additional_eccentricity(lex_mm, D_mm)
        Max_kNm = Pu_kN * eadd_x_mm / 1000.0
    else:
        eadd_x_mm = 0.0
        Max_kNm = 0.0

    if is_slender_y:
        eadd_y_mm = _additional_eccentricity(ley_mm, b_mm)
        May_kNm = Pu_kN * eadd_y_mm / 1000.0
    else:
        eadd_y_mm = 0.0
        May_kNm = 0.0

    # --- k-factor reduction per Cl 39.7.1.1 ---
    # k = (Puz - Pu) / (Puz - Pb), clamped to [0, 1.0]
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
            "— section may be overloaded"
        )
        k = 0.0
    else:
        denom = Puz_kN - Pb_kN
        if abs(denom) < 1e-6:
            # Puz ≈ Pb — degenerate case, use k = 1.0
            k = 1.0
        else:
            k = (Puz_kN - Pu_kN) / denom
            # Clamp to [0, 1.0]
            if k > 1.0:
                k = 1.0
            elif k < 0.0:
                k = 0.0

    # Reduced additional moments
    Max_reduced_kNm = k * Max_kNm
    May_reduced_kNm = k * May_kNm

    return AdditionalMomentResult(
        eadd_x_mm=eadd_x_mm,
        Max_kNm=Max_kNm,
        slenderness_ratio_x=slenderness_ratio_x,
        is_slender_x=is_slender_x,
        eadd_y_mm=eadd_y_mm,
        May_kNm=May_kNm,
        slenderness_ratio_y=slenderness_ratio_y,
        is_slender_y=is_slender_y,
        k=k,
        Max_reduced_kNm=Max_reduced_kNm,
        May_reduced_kNm=May_reduced_kNm,
        Puz_kN=Puz_kN,
        Pb_kN=Pb_kN,
        Pu_kN=Pu_kN,
        b_mm=b_mm,
        D_mm=D_mm,
        lex_mm=lex_mm,
        ley_mm=ley_mm,
        warnings=tuple(warnings),
    )
