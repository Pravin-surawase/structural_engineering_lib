"""
Module:       types
Description:  Custom Data Types (Classes/Dataclasses) and Enums
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional


class BeamType(Enum):
    RECTANGULAR = 1
    FLANGED_T = 2
    FLANGED_L = 3


class DesignSectionType(Enum):
    UNDER_REINFORCED = 1
    BALANCED = 2
    OVER_REINFORCED = 3


@dataclass
class FlexureResult:
    mu_lim: float  # Limiting moment of resistance (kN-m)
    ast_required: float  # Area of tension steel required/provided (mm^2)
    pt_provided: float  # Percentage of steel provided
    section_type: DesignSectionType
    xu: float  # Depth of neutral axis (mm)
    xu_max: float  # Max depth of neutral axis (mm)
    is_safe: bool  # True if design is valid
    asc_required: float = 0.0  # Area of compression steel required (mm^2)
    error_message: str = ""


@dataclass
class ShearResult:
    tv: float  # Nominal shear stress (N/mm^2)
    tc: float  # Design shear strength of concrete (N/mm^2)
    tc_max: float  # Max shear stress (N/mm^2)
    vus: float  # Shear capacity of stirrups (kN)
    spacing: float  # Calculated spacing (mm)
    is_safe: bool  # True if section is safe in shear
    remarks: str = ""
