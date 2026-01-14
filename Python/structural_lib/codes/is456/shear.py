# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       shear
Description:  Shear design and analysis functions
"""

from structural_lib.data_types import ShearResult
from structural_lib.error_messages import dimension_too_small
from structural_lib.errors import (
    E_INPUT_001,
    E_INPUT_002,
    E_INPUT_004,
    E_INPUT_005,
    E_INPUT_008,
    E_INPUT_009,
    E_SHEAR_001,
    E_SHEAR_003,
    E_SHEAR_004,
    DimensionError,
)

from . import tables
from .traceability import clause

__all__ = ["calculate_tv", "design_shear", "round_to_practical_spacing"]


# Standard stirrup spacings used in construction (mm)
# These are practical values that are easy to mark and maintain on site
STANDARD_STIRRUP_SPACINGS = [75, 100, 125, 150, 175, 200, 225, 250, 275, 300]


def round_to_practical_spacing(spacing_mm: float, round_down: bool = True) -> float:
    """
    Round calculated stirrup spacing to practical construction values.

    Stirrup spacings in practice are rounded to standard values that are
    easy to mark and maintain on site. This function rounds to the nearest
    standard value from: 75, 100, 125, 150, 175, 200, 225, 250, 275, 300 mm.

    Args:
        spacing_mm: Calculated spacing in mm.
        round_down: If True, round down (conservative). If False, round to nearest.

    Returns:
        Practical spacing value in mm.

    Example:
        >>> round_to_practical_spacing(241.3)
        225.0
        >>> round_to_practical_spacing(241.3, round_down=False)
        250.0
    """
    if spacing_mm <= 0:
        return 0.0

    if spacing_mm <= STANDARD_STIRRUP_SPACINGS[0]:
        return float(STANDARD_STIRRUP_SPACINGS[0])

    if spacing_mm >= STANDARD_STIRRUP_SPACINGS[-1]:
        return float(STANDARD_STIRRUP_SPACINGS[-1])

    if round_down:
        # Find the largest standard spacing that is <= calculated spacing
        for s in reversed(STANDARD_STIRRUP_SPACINGS):
            if s <= spacing_mm:
                return float(s)
        return float(STANDARD_STIRRUP_SPACINGS[0])
    else:
        # Find the nearest standard spacing
        closest = STANDARD_STIRRUP_SPACINGS[0]
        min_diff = abs(spacing_mm - closest)
        for s in STANDARD_STIRRUP_SPACINGS[1:]:
            diff = abs(spacing_mm - s)
            if diff < min_diff:
                min_diff = diff
                closest = s
        return float(closest)


@clause("40.1")
def calculate_tv(vu_kn: float, b: float, d: float) -> float:
    """
    Calculate nominal shear stress (tv).

    Args:
        vu_kn: Factored shear force (kN).
        b: Beam width (mm).
        d: Effective depth (mm).

    Returns:
        Nominal shear stress tv (N/mm²).

    Raises:
        DimensionError: If b or d <= 0.
    """
    if b <= 0:
        raise DimensionError(
            dimension_too_small("beam width b", b, 0, "Cl. 40.1"),
            details={"b": b, "minimum": 0},
            clause_ref="Cl. 40.1",
        )
    if d <= 0:
        raise DimensionError(
            dimension_too_small("effective depth d", d, 0, "Cl. 40.1"),
            details={"d": d, "minimum": 0},
            clause_ref="Cl. 40.1",
        )

    return (abs(vu_kn) * 1000.0) / (b * d)


@clause("40.1", "40.2", "40.4", "26.5.1.5", "26.5.1.6")
def design_shear(
    vu_kn: float, b: float, d: float, fck: float, fy: float, asv: float, pt: float
) -> ShearResult:
    """
    Main Shear Design Function

    Args:
        vu_kn: Factored shear (kN)
        b: Beam width (mm)
        d: Effective depth (mm)
        fck: Concrete strength (N/mm^2)
        fy: Steel yield strength (N/mm^2)
        asv: Area of shear reinforcement legs (mm^2)
        pt: Tension steel percentage for Table 19 lookup (%)

    Returns:
        ShearResult with nominal stress, design spacing, and pass/fail status.

    Notes:
        - Uses IS 456 Table 19/20 values for tc and tc_max via lookup helpers.
        - Returns structured errors instead of raising for validation failures.
        - Applies max spacing limits per Cl. 26.5.1.5.
    """
    # Input validation with structured errors
    input_errors = []
    if b <= 0:
        input_errors.append(E_INPUT_001)
    if d <= 0:
        input_errors.append(E_INPUT_002)

    if input_errors:
        return ShearResult(
            tv=0.0,
            tc=0.0,
            tc_max=0.0,
            vus=0.0,
            spacing=0.0,
            is_safe=False,
            errors=input_errors,
        )

    material_errors = []
    if fck <= 0:
        material_errors.append(E_INPUT_004)
    if fy <= 0:
        material_errors.append(E_INPUT_005)

    if material_errors:
        return ShearResult(
            tv=0.0,
            tc=0.0,
            tc_max=0.0,
            vus=0.0,
            spacing=0.0,
            is_safe=False,
            errors=material_errors,
        )

    if asv <= 0:
        return ShearResult(
            tv=0.0,
            tc=0.0,
            tc_max=0.0,
            vus=0.0,
            spacing=0.0,
            is_safe=False,
            errors=[E_INPUT_008],
        )

    if pt < 0:
        return ShearResult(
            tv=0.0,
            tc=0.0,
            tc_max=0.0,
            vus=0.0,
            spacing=0.0,
            is_safe=False,
            errors=[E_INPUT_009],
        )

    warning_errors = []
    if fck < 15 or fck > 40:
        warning_errors.append(E_SHEAR_004)

    # 1. Calculate Tv
    tv = calculate_tv(vu_kn, b, d)

    # 2. Get Tc_max
    tc_max = tables.get_tc_max_value(fck)

    # Check Safety
    if tv > tc_max:
        return ShearResult(
            tv=tv,
            tc=0.0,
            tc_max=tc_max,
            vus=0.0,
            spacing=0.0,
            is_safe=False,
            errors=warning_errors + [E_SHEAR_001],
        )

    # 3. Get Tc
    tc = tables.get_tc_value(fck, pt)

    # 4. Calculate Vus and Spacing
    vu_n = abs(vu_kn) * 1000.0
    vc_n = tc * b * d
    design_errors = list(warning_errors)

    if tv <= tc:
        # Nominal shear < Design strength
        vus = 0.0
        design_errors.append(E_SHEAR_003)

        # Spacing for min reinforcement (Cl. 26.5.1.6)
        spacing_calc = (0.87 * fy * asv) / (0.4 * b)
    else:
        # Design for shear
        vus = (vu_n - vc_n) / 1000.0  # kN

        # sv = (0.87 * fy * Asv * d) / Vus_N
        spacing_calc = (0.87 * fy * asv * d) / (vus * 1000.0)

    # 5. Apply Max Spacing Limits (Cl. 26.5.1.5)
    max_spacing_1 = 0.75 * d
    max_spacing_2 = 300.0
    max_spacing_min_reinf = (0.87 * fy * asv) / (0.4 * b)

    spacing = spacing_calc
    if spacing > max_spacing_1:
        spacing = max_spacing_1
    if spacing > max_spacing_2:
        spacing = max_spacing_2
    if spacing > max_spacing_min_reinf:
        spacing = max_spacing_min_reinf

    # 6. Round to practical construction spacing (conservative)
    spacing = round_to_practical_spacing(spacing, round_down=True)

    return ShearResult(
        tv=tv,
        tc=tc,
        tc_max=tc_max,
        vus=vus,
        spacing=spacing,
        is_safe=True,
        errors=design_errors,
    )
