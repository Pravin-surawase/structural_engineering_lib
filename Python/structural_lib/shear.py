"""
Module:       shear
Description:  Shear design and analysis functions
"""

from . import tables
from .types import ShearResult
from .errors import (
    E_INPUT_001,
    E_INPUT_002,
    E_INPUT_004,
    E_INPUT_005,
    E_INPUT_008,
    E_INPUT_009,
    E_SHEAR_001,
    E_SHEAR_003,
)


def calculate_tv(vu_kn: float, b: float, d: float) -> float:
    """Calculate Nominal Shear Stress (N/mm^2)"""
    if b * d == 0:
        return 0.0
    return (abs(vu_kn) * 1000.0) / (b * d)


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
            remarks="Invalid input: b and d must be > 0.",
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
            remarks="Invalid input: fck and fy must be > 0.",
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
            remarks="Invalid input: asv must be > 0.",
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
            remarks="Invalid input: pt must be >= 0.",
            errors=[E_INPUT_009],
        )

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
            remarks="Shear stress exceeds Tc_max. Redesign section.",
            errors=[E_SHEAR_001],
        )

    # 3. Get Tc
    tc = tables.get_tc_value(fck, pt)

    # 4. Calculate Vus and Spacing
    vu_n = abs(vu_kn) * 1000.0
    vc_n = tc * b * d
    design_errors = []

    if tv <= tc:
        # Nominal shear < Design strength
        vus = 0.0
        remarks = "Nominal shear < Tc. Provide minimum shear reinforcement."
        design_errors.append(E_SHEAR_003)

        # Spacing for min reinforcement (Cl. 26.5.1.6)
        spacing_calc = (0.87 * fy * asv) / (0.4 * b)
    else:
        # Design for shear
        vus = (vu_n - vc_n) / 1000.0  # kN
        remarks = "Shear reinforcement required."

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

    return ShearResult(
        tv=tv,
        tc=tc,
        tc_max=tc_max,
        vus=vus,
        spacing=spacing,
        is_safe=True,
        remarks=remarks,
        errors=design_errors,
    )
