"""
Module:       types
Description:  Custom Data Types (Classes/Dataclasses) and Enums
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .errors import DesignError


class BeamType(Enum):
    RECTANGULAR = 1
    FLANGED_T = 2
    FLANGED_L = 3


class DesignSectionType(Enum):
    UNDER_REINFORCED = 1
    BALANCED = 2
    OVER_REINFORCED = 3


class SupportCondition(Enum):
    CANTILEVER = auto()
    SIMPLY_SUPPORTED = auto()
    CONTINUOUS = auto()


class ExposureClass(Enum):
    MILD = auto()
    MODERATE = auto()
    SEVERE = auto()
    VERY_SEVERE = auto()


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
    error_message: str = ""  # Deprecated: Use errors list instead
    errors: List["DesignError"] = field(default_factory=list)  # Structured errors


@dataclass
class ShearResult:
    tv: float  # Nominal shear stress (N/mm^2)
    tc: float  # Design shear strength of concrete (N/mm^2)
    tc_max: float  # Max shear stress (N/mm^2)
    vus: float  # Shear capacity of stirrups (kN)
    spacing: float  # Calculated spacing (mm)
    is_safe: bool  # True if section is safe in shear
    remarks: str = ""  # Deprecated: Use errors list instead
    errors: List["DesignError"] = field(default_factory=list)  # Structured errors


@dataclass
class DeflectionResult:
    is_ok: bool
    remarks: str
    support_condition: SupportCondition
    assumptions: List[str]
    inputs: Dict[str, Any]
    computed: Dict[str, Any]


@dataclass
class DeflectionLevelBResult:
    """Level B deflection result with full curvature-based calculation.

    IS 456 Cl 23.2 (Annex C) deflection calculation.
    """

    is_ok: bool
    remarks: str
    support_condition: SupportCondition
    assumptions: List[str]
    inputs: Dict[str, Any]
    computed: Dict[str, Any]

    # Key computed values (also in computed dict)
    mcr_knm: float = 0.0  # Cracking moment (kN·m)
    igross_mm4: float = 0.0  # Gross moment of inertia (mm^4)
    icr_mm4: float = 0.0  # Cracked moment of inertia (mm^4)
    ieff_mm4: float = 0.0  # Effective moment of inertia (mm^4)
    delta_short_mm: float = 0.0  # Short-term (immediate) deflection (mm)
    delta_long_mm: float = 0.0  # Long-term deflection (mm)
    delta_total_mm: float = 0.0  # Total deflection (mm)
    delta_limit_mm: float = 0.0  # Allowable deflection limit (mm)
    long_term_factor: float = 1.0  # Creep/shrinkage multiplier


@dataclass
class CrackWidthResult:
    is_ok: bool
    remarks: str
    exposure_class: ExposureClass
    assumptions: List[str]
    inputs: Dict[str, Any]
    computed: Dict[str, Any]


@dataclass
class ComplianceCaseResult:
    case_id: str
    mu_knm: float
    vu_kn: float
    flexure: FlexureResult
    shear: ShearResult
    deflection: Optional[DeflectionResult] = None
    crack_width: Optional[CrackWidthResult] = None
    is_ok: bool = False
    governing_utilization: float = 0.0
    utilizations: Dict[str, float] = field(default_factory=dict)
    failed_checks: List[str] = field(default_factory=list)
    remarks: str = ""


@dataclass
class ComplianceReport:
    is_ok: bool
    governing_case_id: str
    governing_utilization: float
    cases: List[ComplianceCaseResult]
    summary: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationReport:
    """Validation result for job specs or design results."""

    ok: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "errors": self.errors,
            "warnings": self.warnings,
            "details": self.details,
        }


@dataclass
class CuttingAssignment:
    """Assignment of cuts to a stock bar for cutting-stock optimization."""

    stock_length: float  # mm
    cuts: List[Tuple[str, float]]  # List of (mark, cut_length) tuples
    waste: float  # mm remaining


@dataclass
class CuttingPlan:
    """Complete cutting plan with waste statistics."""

    assignments: List[CuttingAssignment]
    total_stock_used: int  # number of bars
    total_waste: float  # mm
    waste_percentage: float  # %
