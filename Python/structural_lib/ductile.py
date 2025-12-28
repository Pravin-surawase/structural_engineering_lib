"""
Module:       ductile
Description:  IS 13920:2016 Ductile Detailing checks for Beams
"""

import math
from dataclasses import dataclass, field
from typing import List, Tuple

from .errors import (
    DesignError,
    E_DUCTILE_001,
    E_DUCTILE_002,
    E_DUCTILE_003,
    E_INPUT_002,
    E_INPUT_004,
    E_INPUT_005,
    E_INPUT_011,
)


@dataclass
class DuctileBeamResult:
    is_geometry_valid: bool
    min_pt: float
    max_pt: float
    confinement_spacing: float
    remarks: str = ""  # Deprecated: Use errors list instead
    errors: List[DesignError] = field(default_factory=list)  # Structured errors


def check_geometry(b: float, D: float) -> Tuple[bool, str, List[DesignError]]:
    """
    Clause 6.1: Geometry requirements
    1. b >= 200 mm
    2. b/D >= 0.3

    .. deprecated:: 0.10.5
        Return signature changed from (bool, str) to (bool, str, List[DesignError]).
        This is a breaking change for direct callers. Use check_beam_ductility()
        for the stable public API.
    """
    errors = []

    if b < 200:
        errors.append(E_DUCTILE_001)
        return False, f"Width {b} mm < 200 mm (IS 13920 Cl 6.1.1)", errors

    if D <= 0:
        errors.append(E_DUCTILE_003)
        return False, "Invalid depth", errors

    ratio = b / D
    if ratio < 0.3:
        errors.append(E_DUCTILE_002)
        return False, f"Width/Depth ratio {ratio:.2f} < 0.3 (IS 13920 Cl 6.1.2)", errors

    return True, "OK", errors


def get_min_tension_steel_percentage(fck: float, fy: float) -> float:
    """
    Clause 6.2.1 (b): Min tension steel ratio
    rho_min = 0.24 * sqrt(fck) / fy
    Returns percentage (0-100)

    Returns 0.0 if inputs are invalid (fck <= 0 or fy <= 0).
    """
    if fck <= 0 or fy <= 0:
        return 0.0
    rho = 0.24 * math.sqrt(fck) / fy
    return rho * 100.0


def get_max_tension_steel_percentage() -> float:
    """
    Clause 6.2.2: Max tension steel ratio = 2.5%
    """
    return 2.5


def calculate_confinement_spacing(d: float, min_long_bar_dia: float) -> float:
    """
    Clause 6.3.5: Hoop spacing in confinement zone (2d from face)
    Spacing shall not exceed:
    1. d/4
    2. 8 * db_min (smallest longitudinal bar diameter)
    3. 100 mm
    """
    s1 = d / 4.0
    s2 = 8.0 * min_long_bar_dia
    s3 = 100.0

    return min(s1, s2, s3)


def check_beam_ductility(
    b: float, D: float, d: float, fck: float, fy: float, min_long_bar_dia: float
) -> DuctileBeamResult:
    """
    Perform comprehensive ductility checks for a beam section.
    """
    is_geo_valid, geo_msg, geo_errors = check_geometry(b, D)
    if not is_geo_valid:
        return DuctileBeamResult(
            is_geometry_valid=False,
            min_pt=0.0,
            max_pt=0.0,
            confinement_spacing=0.0,
            remarks=geo_msg,
            errors=geo_errors,
        )

    input_errors = []
    if d <= 0:
        input_errors.append(E_INPUT_002)
    if min_long_bar_dia <= 0:
        input_errors.append(E_INPUT_011)
    if input_errors:
        failed_fields = [e.field for e in input_errors if e.field]
        error_message = f"Invalid input: {', '.join(failed_fields)} must be > 0."
        return DuctileBeamResult(
            is_geometry_valid=False,
            min_pt=0.0,
            max_pt=0.0,
            confinement_spacing=0.0,
            remarks=error_message,
            errors=input_errors,
        )

    material_errors = []
    if fck <= 0:
        material_errors.append(E_INPUT_004)
    if fy <= 0:
        material_errors.append(E_INPUT_005)
    if material_errors:
        return DuctileBeamResult(
            is_geometry_valid=False,
            min_pt=0.0,
            max_pt=0.0,
            confinement_spacing=0.0,
            remarks="Invalid input: fck and fy must be > 0.",
            errors=material_errors,
        )

    min_pt = get_min_tension_steel_percentage(fck, fy)
    max_pt = get_max_tension_steel_percentage()
    spacing = calculate_confinement_spacing(d, min_long_bar_dia)

    return DuctileBeamResult(
        is_geometry_valid=True,
        min_pt=min_pt,
        max_pt=max_pt,
        confinement_spacing=spacing,
        remarks="Compliant",
        errors=[],
    )
