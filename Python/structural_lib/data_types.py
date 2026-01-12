# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       types
Description:  Custom Data Types (Classes/Dataclasses) and Enums
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, TypedDict

from .utilities import deprecated_field

if TYPE_CHECKING:
    from .errors import DesignError


# =============================================================================
# TypedDicts for Structured Data
# =============================================================================


class BarDict(TypedDict):
    """Bar arrangement dictionary for bottom/top bars."""

    count: int
    diameter: float
    callout: str


class StirrupDict(TypedDict):
    """Stirrup arrangement dictionary."""

    diameter: float
    spacing: float
    callout: str


class DeflectionParams(TypedDict, total=False):
    """Parameters for deflection calculation.

    All fields are optional (total=False).
    """

    span_mm: float
    d_mm: float
    support_condition: str  # "CANTILEVER", "SIMPLY_SUPPORTED", "CONTINUOUS"


class CrackWidthParams(TypedDict, total=False):
    """Parameters for crack width calculation.

    All fields are optional (total=False).
    """

    exposure: str  # Exposure class: "MILD", "MODERATE", "SEVERE", "VERY_SEVERE"
    max_crack_width_mm: float  # Maximum allowable crack width


class OptimizerInputs(TypedDict, total=False):
    """Input parameters for rebar optimizer.

    All fields optional (total=False) to allow partial structures in error cases.
    """

    ast_required_mm2: float
    b_mm: float
    cover_mm: float
    stirrup_dia_mm: float
    agg_size_mm: float
    max_layers: int
    min_total_bars: int
    max_bars_per_layer: int


class OptimizerCandidate(TypedDict, total=False):
    """Candidate solution from rebar optimizer.

    All fields optional (total=False) since candidate may be empty when not feasible.
    """

    bar_dia_mm: float
    count: int
    layers: int
    bars_per_layer: int
    spacing_mm: float
    spacing_check: str


class OptimizerChecks(TypedDict, total=False):
    """Rebar optimizer checks structure.

    All fields optional (total=False) to allow partial structures in error cases.
    """

    inputs: OptimizerInputs
    candidate: OptimizerCandidate
    selection: dict[str, Any]  # Selection metadata


class BeamGeometry(TypedDict, total=False):
    """Beam geometry and material properties.

    Required fields: b_mm, D_mm, d_mm, fck_nmm2, fy_nmm2
    Optional fields marked with total=False.

    Units: mm for dimensions, N/mm² for stresses
    """

    # Required fields (must be present in TypedDict usage)
    b_mm: float  # Beam width (mm)
    D_mm: float  # Overall depth (mm)
    d_mm: float  # Effective depth (mm)
    fck_nmm2: float  # Characteristic compressive strength of concrete (N/mm²)
    fy_nmm2: float  # Characteristic yield strength of steel (N/mm²)

    # Optional fields
    d_dash_mm: float  # Cover to compression steel (mm), default 50.0
    asv_mm2: float  # Area of stirrup legs (mm²), default 100.0
    pt_percent: float | None  # Percentage of steel for deflection, optional
    deflection_defaults: DeflectionParams | None  # Deflection calculation params
    crack_width_defaults: CrackWidthParams | None  # Crack width params


class LoadCase(TypedDict):
    """Load case with bending moment and shear force.

    All fields required.
    """

    case_id: str  # Load case identifier (e.g., "1.5(DL+LL)")
    mu_knm: float  # Factored moment (kN·m)
    vu_kn: float  # Factored shear (kN)


class JobSpec(TypedDict):
    """Complete job specification for beam design.

    Schema version 1 format for job.json files.
    """

    job_id: str  # Job identifier
    schema_version: int  # Schema version (currently 1)
    code: str  # Design code (e.g., "IS456")
    units: str  # Unit system (e.g., "SI-mm")
    beam: BeamGeometry  # Beam geometry and materials
    cases: list[LoadCase]  # List of load cases


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
    errors: list[DesignError] = field(default_factory=list)  # Structured errors

    def __post_init__(self) -> None:
        if self.error_message:
            deprecated_field(
                "FlexureResult",
                "error_message",
                "0.14.0",
                "1.0.0",
                alternative="errors",
            )


@dataclass
class ShearResult:
    tv: float  # Nominal shear stress (N/mm^2)
    tc: float  # Design shear strength of concrete (N/mm^2)
    tc_max: float  # Max shear stress (N/mm^2)
    vus: float  # Shear capacity of stirrups (kN)
    spacing: float  # Calculated spacing (mm)
    is_safe: bool  # True if section is safe in shear
    remarks: str = ""  # Deprecated: Use errors list instead
    errors: list[DesignError] = field(default_factory=list)  # Structured errors

    def __post_init__(self) -> None:
        if self.remarks:
            deprecated_field(
                "ShearResult",
                "remarks",
                "0.14.0",
                "1.0.0",
                alternative="errors",
            )


@dataclass
class DeflectionResult:
    is_ok: bool
    remarks: str
    support_condition: SupportCondition
    assumptions: list[str]
    inputs: dict[str, Any]
    computed: dict[str, Any]


@dataclass
class DeflectionLevelBResult:
    """Level B deflection result with full curvature-based calculation.

    IS 456 Cl 23.2 (Annex C) deflection calculation.
    """

    is_ok: bool
    remarks: str
    support_condition: SupportCondition
    assumptions: list[str]
    inputs: dict[str, Any]
    computed: dict[str, Any]

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
    assumptions: list[str]
    inputs: dict[str, Any]
    computed: dict[str, Any]


@dataclass
class ComplianceCaseResult:
    case_id: str
    mu_knm: float
    vu_kn: float
    flexure: FlexureResult
    shear: ShearResult
    deflection: DeflectionResult | None = None
    crack_width: CrackWidthResult | None = None
    is_ok: bool = False
    governing_utilization: float = 0.0
    utilizations: dict[str, float] = field(default_factory=dict)
    failed_checks: list[str] = field(default_factory=list)
    remarks: str = ""


@dataclass
class ComplianceReport:
    is_ok: bool
    governing_case_id: str
    governing_utilization: float
    cases: list[ComplianceCaseResult]
    summary: dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationReport:
    """Validation result for job specs or design results."""

    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
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
    cuts: list[tuple[str, float]]  # List of (mark, cut_length) tuples
    waste: float  # mm remaining


@dataclass
class CuttingPlan:
    """Complete cutting plan with waste statistics."""

    assignments: list[CuttingAssignment]
    total_stock_used: int  # number of bars
    total_waste: float  # mm
    waste_percentage: float  # %
