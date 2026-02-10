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


class LoadType(Enum):
    """Type of applied load for BMD/SFD analysis."""

    UDL = auto()  # Uniformly distributed load (w kN/m)
    POINT = auto()  # Concentrated/point load (P kN at position a)
    TRIANGULAR = auto()  # Triangularly distributed load (w_max at one end)
    MOMENT = auto()  # Applied moment (M kN·m at position a)


@dataclass
class LoadDefinition:
    """Definition of a single load for BMD/SFD computation.

    Attributes:
        load_type: Type of load (UDL, POINT, TRIANGULAR, MOMENT)
        magnitude: Load magnitude (kN/m for UDL/TRI, kN for POINT, kN·m for MOMENT)
        position_mm: Position from left support (mm), required for POINT/MOMENT
        end_position_mm: End position (mm), optional for partial loads

    Examples:
        # UDL of 20 kN/m over full span
        LoadDefinition(LoadType.UDL, magnitude=20.0)

        # Point load of 50 kN at midspan (for 6000mm span)
        LoadDefinition(LoadType.POINT, magnitude=50.0, position_mm=3000.0)

        # Moment of 25 kN·m at support
        LoadDefinition(LoadType.MOMENT, magnitude=25.0, position_mm=0.0)
    """

    load_type: LoadType
    magnitude: float  # kN/m for UDL, kN for POINT, kN·m for MOMENT
    position_mm: float = 0.0  # Position from left support (mm)
    end_position_mm: float | None = None  # End position for partial loads (mm)


@dataclass
class CriticalPoint:
    """Critical point on BMD/SFD diagram (max, min, zero crossing).

    Attributes:
        position_mm: Position from left support (mm)
        point_type: Type of critical point ("max_bm", "min_bm", "max_sf", "zero_bm", etc.)
        bm_knm: Bending moment at this point (kN·m)
        sf_kn: Shear force at this point (kN)
    """

    position_mm: float
    point_type: str  # "max_bm", "min_bm", "max_sf", "min_sf", "zero_bm", "zero_sf"
    bm_knm: float
    sf_kn: float


@dataclass
class LoadDiagramResult:
    """Result of BMD/SFD computation for a beam.

    Contains discretized BMD and SFD data along with critical points.
    Use with Plotly or matplotlib for visualization.

    Attributes:
        positions_mm: List of positions along span (mm), typically 101 points
        bmd_knm: Bending moment at each position (kN·m), positive = sagging
        sfd_kn: Shear force at each position (kN), positive = upward on left face
        critical_points: List of critical points (max/min/zero)
        span_mm: Total span (mm)
        support_condition: "simply_supported" or "cantilever"
        loads: List of applied loads
        max_bm_knm: Maximum bending moment (kN·m)
        min_bm_knm: Minimum bending moment (kN·m)
        max_sf_kn: Maximum shear force (kN)
        min_sf_kn: Minimum shear force (kN)

    Example:
        >>> result = compute_bmd_sfd(span_mm=6000, support="simply_supported",
        ...                          loads=[LoadDefinition(LoadType.UDL, 20)])
        >>> print(f"Max moment: {result.max_bm_knm:.1f} kN·m")
        Max moment: 90.0 kN·m
    """

    positions_mm: list[float]
    bmd_knm: list[float]
    sfd_kn: list[float]
    critical_points: list[CriticalPoint]
    span_mm: float
    support_condition: str
    loads: list[LoadDefinition]
    max_bm_knm: float = 0.0
    min_bm_knm: float = 0.0
    max_sf_kn: float = 0.0
    min_sf_kn: float = 0.0


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
class TorsionResult:
    """Result of torsion design per IS 456 Clause 41.

    Attributes:
        tu_knm: Applied torsional moment (kN·m)
        vu_kn: Applied shear force (kN)
        mu_knm: Applied bending moment (kN·m)
        ve_kn: Equivalent shear force (kN)
        me_knm: Equivalent bending moment (kN·m)
        tv_equiv: Equivalent shear stress (N/mm²)
        tc: Design shear strength of concrete (N/mm²)
        tc_max: Maximum shear stress limit (N/mm²)
        asv_torsion: Area of stirrups for torsion per unit length (mm²/mm)
        asv_shear: Area of stirrups for shear per unit length (mm²/mm)
        asv_total: Total stirrup area per unit length (mm²/mm)
        stirrup_spacing: Designed stirrup spacing (mm)
        al_torsion: Longitudinal steel for torsion (mm²)
        is_safe: True if section is safe
        requires_closed_stirrups: True (always for torsion)
        errors: List of structured errors/warnings
    """

    tu_knm: float
    vu_kn: float
    mu_knm: float
    ve_kn: float
    me_knm: float
    tv_equiv: float
    tc: float
    tc_max: float
    asv_torsion: float
    asv_shear: float
    asv_total: float
    stirrup_spacing: float
    al_torsion: float
    is_safe: bool
    requires_closed_stirrups: bool = True
    errors: list[DesignError] = field(default_factory=list)


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
class DeflectionLevelCResult:
    """Level C deflection result with separate creep and shrinkage.

    IS 456 Annex C detailed deflection calculation with:
    - Separate creep and shrinkage components
    - Sustained vs live load differentiation
    - Humidity and age of loading factors
    """

    is_ok: bool
    remarks: str
    support_condition: SupportCondition
    assumptions: list[str]
    inputs: dict[str, Any]
    computed: dict[str, Any]

    # Key computed values
    mcr_knm: float = 0.0  # Cracking moment (kN·m)
    igross_mm4: float = 0.0  # Gross moment of inertia (mm^4)
    icr_mm4: float = 0.0  # Cracked moment of inertia (mm^4)
    ieff_mm4: float = 0.0  # Effective moment of inertia (mm^4)

    # Deflection components (Level C separates these)
    delta_immediate_mm: float = 0.0  # Immediate deflection under total load (mm)
    delta_creep_mm: float = 0.0  # Creep deflection component (mm)
    delta_shrinkage_mm: float = 0.0  # Shrinkage deflection component (mm)
    delta_total_mm: float = 0.0  # Total deflection (mm)
    delta_limit_mm: float = 0.0  # Allowable deflection limit (mm)

    # Factors
    creep_coefficient: float = 0.0  # Creep coefficient (θ)
    shrinkage_curvature: float = 0.0  # Shrinkage curvature (1/mm)


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
