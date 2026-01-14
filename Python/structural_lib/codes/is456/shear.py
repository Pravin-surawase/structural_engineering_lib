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

__all__ = [
    "calculate_tv",
    "design_shear",
    "round_to_practical_spacing",
    "select_stirrup_diameter",
    "STANDARD_STIRRUP_DIAMETERS",
    "STANDARD_STIRRUP_SPACINGS",
]


# Standard stirrup spacings used in construction (mm)
# These are practical values that are easy to mark and maintain on site
STANDARD_STIRRUP_SPACINGS = [75, 100, 125, 150, 175, 200, 225, 250, 275, 300]

# Standard stirrup diameters (mm) per IS 456 and SP 34 practice
# 6mm: Light shear, small beams
# 8mm: Normal shear, typical beams (most common)
# 10mm: Moderate shear, medium beams
# 12mm: High shear, large beams
STANDARD_STIRRUP_DIAMETERS = [6, 8, 10, 12]


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


def select_stirrup_diameter(
    vu_kn: float,
    b_mm: float,
    d_mm: float,
    fck: float,
    main_bar_dia: float = 16.0,
    num_legs: int = 2,
) -> int:
    """
    Select appropriate stirrup diameter based on shear demand.

    Selection criteria (IS 456 + SP 34 practice):
    - 6mm: Light shear (tv < 0.4 N/mm²), narrow beams (b < 200mm)
    - 8mm: Normal shear (tv < 0.8 N/mm²), typical beams (default)
    - 10mm: Moderate shear (tv < 1.5 N/mm²), medium-large beams
    - 12mm: High shear (tv >= 1.5 N/mm²), large beams (b >= 400mm)

    Also considers:
    - Main bar diameter (stirrup should be >= main_bar/4 per IS 456)
    - Beam width (larger beams use larger stirrups)

    Args:
        vu_kn: Factored shear force (kN).
        b_mm: Beam width (mm).
        d_mm: Effective depth (mm).
        fck: Concrete strength (N/mm²).
        main_bar_dia: Main reinforcement bar diameter (mm).
        num_legs: Number of stirrup legs.

    Returns:
        Recommended stirrup diameter (mm): 6, 8, 10, or 12.

    Example:
        >>> select_stirrup_diameter(80, 300, 450, 25, 16)
        8
        >>> select_stirrup_diameter(200, 500, 700, 30, 25)
        12
    """
    import math

    # Calculate nominal shear stress
    if b_mm <= 0 or d_mm <= 0:
        return 8  # Default

    tv = (abs(vu_kn) * 1000.0) / (b_mm * d_mm)

    # Minimum stirrup diameter per IS 456 Cl. 26.5.1.8
    # Stirrup diameter should not be less than main_bar / 4
    min_dia_from_main = math.ceil(main_bar_dia / 4)
    min_dia = max(6, min_dia_from_main)

    # Selection based on shear stress and beam size
    if tv < 0.4:
        # Light shear - use minimum practical size
        if b_mm < 200:
            selected = 6
        else:
            selected = 8
    elif tv < 0.8:
        # Normal shear - standard 8mm for most cases
        if b_mm >= 400:
            selected = 10
        else:
            selected = 8
    elif tv < 1.5:
        # Moderate shear
        if b_mm >= 400 or d_mm >= 600:
            selected = 10
        else:
            selected = 8
    else:
        # High shear - use larger stirrups
        if b_mm >= 400:
            selected = 12
        else:
            selected = 10

    # Ensure minimum diameter constraint
    selected = max(selected, min_dia)

    # Ensure it's a standard size
    if selected not in STANDARD_STIRRUP_DIAMETERS:
        # Round up to next standard size
        for std in STANDARD_STIRRUP_DIAMETERS:
            if std >= selected:
                selected = std
                break

    return selected


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
