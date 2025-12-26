"""
Module:       ductile
Description:  IS 13920:2016 Ductile Detailing checks for Beams
"""

import math
from dataclasses import dataclass
from typing import Tuple


@dataclass
class DuctileBeamResult:
    is_geometry_valid: bool
    min_pt: float
    max_pt: float
    confinement_spacing: float
    remarks: str


def check_geometry(b: float, D: float) -> Tuple[bool, str]:
    """
    Clause 6.1: Geometry requirements
    1. b >= 200 mm
    2. b/D >= 0.3
    """
    if b < 200:
        return False, f"Width {b} mm < 200 mm (IS 13920 Cl 6.1.1)"

    if D <= 0:
        return False, "Invalid depth"

    ratio = b / D
    if ratio < 0.3:
        return False, f"Width/Depth ratio {ratio:.2f} < 0.3 (IS 13920 Cl 6.1.2)"

    return True, "OK"


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
    is_geo_valid, geo_msg = check_geometry(b, D)

    min_pt = get_min_tension_steel_percentage(fck, fy)
    max_pt = get_max_tension_steel_percentage()
    spacing = calculate_confinement_spacing(d, min_long_bar_dia)

    remarks = []
    if not is_geo_valid:
        remarks.append(geo_msg)

    return DuctileBeamResult(
        is_geometry_valid=is_geo_valid,
        min_pt=min_pt,
        max_pt=max_pt,
        confinement_spacing=spacing,
        remarks="; ".join(remarks) if remarks else "Compliant",
    )
