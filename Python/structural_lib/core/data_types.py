# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       types
Description:  Custom Data Types (Classes/Dataclasses) and Enums
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field, fields
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
    Mu_lim: float  # Limiting moment of resistance (kN-m)
    Ast_required: float  # Area of tension steel required/provided (mm^2)
    pt_provided: float  # Percentage of steel provided
    section_type: DesignSectionType
    xu: float  # Depth of neutral axis (mm)
    xu_max: float  # Max depth of neutral axis (mm)
    is_safe: bool  # True if design is valid
    Asc_required: float = 0.0  # Area of compression steel required (mm^2)
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

    @property
    def mu_lim(self) -> float:
        """Deprecated: Use Mu_lim instead."""
        import warnings

        warnings.warn(
            "FlexureResult.mu_lim is deprecated, use Mu_lim instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.Mu_lim

    @property
    def ast_required(self) -> float:
        """Deprecated: Use Ast_required instead."""
        import warnings

        warnings.warn(
            "FlexureResult.ast_required is deprecated, use Ast_required instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.Ast_required

    @property
    def asc_required(self) -> float:
        """Deprecated: Use Asc_required instead."""
        import warnings

        warnings.warn(
            "FlexureResult.asc_required is deprecated, use Asc_required instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.Asc_required


@dataclass
class ShearResult:
    tau_v: float  # Nominal shear stress (N/mm^2)
    tau_c: float  # Design shear strength of concrete (N/mm^2)
    tau_c_max: float  # Max shear stress (N/mm^2)
    Vus: float  # Shear capacity of stirrups (kN)
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

    @property
    def tv(self) -> float:
        """Deprecated: Use tau_v instead."""
        import warnings

        warnings.warn(
            "ShearResult.tv is deprecated, use tau_v instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.tau_v

    @property
    def tc(self) -> float:
        """Deprecated: Use tau_c instead."""
        import warnings

        warnings.warn(
            "ShearResult.tc is deprecated, use tau_c instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.tau_c

    @property
    def tc_max(self) -> float:
        """Deprecated: Use tau_c_max instead."""
        import warnings

        warnings.warn(
            "ShearResult.tc_max is deprecated, use tau_c_max instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.tau_c_max

    @property
    def vus(self) -> float:
        """Deprecated: Use Vus instead."""
        import warnings

        warnings.warn(
            "ShearResult.vus is deprecated, use Vus instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.Vus


@dataclass
class TorsionResult:
    """Result of torsion design per IS 456 Clause 41.

    Attributes:
        Tu_knm: Applied torsional moment (kN·m)
        Vu_kn: Applied shear force (kN)
        Mu_knm: Applied bending moment (kN·m)
        Ve_kn: Equivalent shear force (kN)
        Me_knm: Equivalent bending moment (kN·m)
        tau_ve: Equivalent shear stress (N/mm²)
        tau_c: Design shear strength of concrete (N/mm²)
        tau_c_max: Maximum shear stress limit (N/mm²)
        Asv_torsion: Area of stirrups for torsion per unit length (mm²/mm)
        Asv_shear: Area of stirrups for shear per unit length (mm²/mm)
        Asv_total: Total stirrup area per unit length (mm²/mm)
        stirrup_spacing: Designed stirrup spacing (mm)
        Al_torsion: Longitudinal steel for torsion (mm²)
        is_safe: True if section is safe
        requires_closed_stirrups: True (always for torsion)
        errors: List of structured errors/warnings
    """

    Tu_knm: float
    Vu_kn: float
    Mu_knm: float
    Ve_kn: float
    Me_knm: float
    tau_ve: float
    tau_c: float
    tau_c_max: float
    Asv_torsion: float
    Asv_shear: float
    Asv_total: float
    stirrup_spacing: float
    Al_torsion: float
    is_safe: bool
    requires_closed_stirrups: bool = True
    errors: list[DesignError] = field(default_factory=list)

    @property
    def tu_knm(self) -> float:
        """Deprecated: Use Tu_knm instead."""
        import warnings

        warnings.warn(
            "TorsionResult.tu_knm is deprecated, use Tu_knm instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.Tu_knm

    @property
    def vu_kn(self) -> float:
        """Deprecated: Use Vu_kn instead."""
        import warnings

        warnings.warn(
            "TorsionResult.vu_kn is deprecated, use Vu_kn instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.Vu_kn

    @property
    def mu_knm(self) -> float:
        """Deprecated: Use Mu_knm instead."""
        import warnings

        warnings.warn(
            "TorsionResult.mu_knm is deprecated, use Mu_knm instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.Mu_knm

    @property
    def ve_kn(self) -> float:
        """Deprecated: Use Ve_kn instead."""
        import warnings

        warnings.warn(
            "TorsionResult.ve_kn is deprecated, use Ve_kn instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.Ve_kn

    @property
    def me_knm(self) -> float:
        """Deprecated: Use Me_knm instead."""
        import warnings

        warnings.warn(
            "TorsionResult.me_knm is deprecated, use Me_knm instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.Me_knm

    @property
    def tv_equiv(self) -> float:
        """Deprecated: Use tau_ve instead."""
        import warnings

        warnings.warn(
            "TorsionResult.tv_equiv is deprecated, use tau_ve instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.tau_ve

    @property
    def tc(self) -> float:
        """Deprecated: Use tau_c instead."""
        import warnings

        warnings.warn(
            "TorsionResult.tc is deprecated, use tau_c instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.tau_c

    @property
    def tc_max(self) -> float:
        """Deprecated: Use tau_c_max instead."""
        import warnings

        warnings.warn(
            "TorsionResult.tc_max is deprecated, use tau_c_max instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.tau_c_max

    @property
    def asv_torsion(self) -> float:
        """Deprecated: Use Asv_torsion instead."""
        import warnings

        warnings.warn(
            "TorsionResult.asv_torsion is deprecated, use Asv_torsion instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.Asv_torsion

    @property
    def asv_shear(self) -> float:
        """Deprecated: Use Asv_shear instead."""
        import warnings

        warnings.warn(
            "TorsionResult.asv_shear is deprecated, use Asv_shear instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.Asv_shear

    @property
    def asv_total(self) -> float:
        """Deprecated: Use Asv_total instead."""
        import warnings

        warnings.warn(
            "TorsionResult.asv_total is deprecated, use Asv_total instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.Asv_total

    @property
    def al_torsion(self) -> float:
        """Deprecated: Use Al_torsion instead."""
        import warnings

        warnings.warn(
            "TorsionResult.al_torsion is deprecated, use Al_torsion instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.Al_torsion


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
    Mu_knm: float
    Vu_kn: float
    flexure: FlexureResult
    shear: ShearResult
    deflection: DeflectionResult | None = None
    crack_width: CrackWidthResult | None = None
    is_ok: bool = False
    governing_utilization: float = 0.0
    utilizations: dict[str, float] = field(default_factory=dict)
    failed_checks: list[str] = field(default_factory=list)
    remarks: str = ""

    @property
    def mu_knm(self) -> float:
        """Deprecated: Use Mu_knm instead."""
        import warnings

        warnings.warn(
            "ComplianceCaseResult.mu_knm is deprecated, use Mu_knm instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.Mu_knm

    @property
    def vu_kn(self) -> float:
        """Deprecated: Use Vu_kn instead."""
        import warnings

        warnings.warn(
            "ComplianceCaseResult.vu_kn is deprecated, use Vu_kn instead. "
            "Will be removed in v1.0.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.Vu_kn


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


# =============================================================================
# Column Design Types — IS 456 Cl. 25, 39
# =============================================================================


class ColumnClassification(Enum):
    """Column classification per IS 456 Cl 25.1.2."""

    SHORT = auto()
    SLENDER = auto()


class EndCondition(Enum):
    """Column end-condition for effective length per IS 456 Table 28."""

    FIXED_FIXED = auto()  # Case 1: Both ends fixed, no lateral translation
    FIXED_HINGED = auto()  # Case 2: One end fixed, one hinged
    FIXED_FIXED_SWAY = auto()  # Case 3: Both ends fixed, lateral translation allowed
    FIXED_FREE = auto()  # Case 4: One end fixed, one free (cantilever)
    HINGED_HINGED = auto()  # Case 5: Both ends hinged
    FIXED_PARTIAL = auto()  # Case 6: One fixed, partial restraint at other
    HINGED_PARTIAL = auto()  # Case 7: One hinged, partial restraint at other


@dataclass
class ColumnAxialResult:
    """Result of short column axial capacity check per IS 456 Cl 39.3.

    Attributes:
        Pu_kN: Axial capacity (kN)
        fck: Concrete grade used (N/mm²)
        fy: Steel grade used (N/mm²)
        Ag_mm2: Gross area (mm²)
        Asc_mm2: Steel area (mm²)
        Ac_mm2: Concrete area = Ag - Asc (mm²)
        steel_ratio: Asc/Ag
        classification: Column classification (short or slender)
        is_safe: True if capacity >= applied load (when load provided)
        warnings: List of design warnings
        errors: List of structured design errors
    """

    Pu_kN: float
    fck: float
    fy: float
    Ag_mm2: float
    Asc_mm2: float
    Ac_mm2: float
    steel_ratio: float
    classification: ColumnClassification
    is_safe: bool
    warnings: list[str] = field(default_factory=list)
    errors: list[DesignError] = field(default_factory=list)


@dataclass(frozen=True)
class ColumnUniaxialResult:
    """Result of short column uniaxial bending check per IS 456 Cl 39.5.

    Attributes:
        Pu_kN: Applied axial load (kN)
        Mu_kNm: Applied moment (kN·m)
        Pu_cap_kN: Axial capacity on P-M envelope at applied load ratio (kN)
        Mu_cap_kNm: Moment capacity on P-M envelope at applied load ratio (kN·m)
        utilization_ratio: Radial utilization (applied / capacity), <= 1.0 is safe
        eccentricity_mm: Applied eccentricity Mu/Pu (mm)
        e_min_mm: Minimum eccentricity per Cl 25.4 (mm), None if not computed
        is_safe: True if utilization_ratio <= 1.0
        classification: Column classification (SHORT or SLENDER)
        governing_check: Description of the governing design check
        clause_ref: IS 456 clause reference
        warnings: Tuple of warning messages
    """

    Pu_kN: float
    Mu_kNm: float
    Pu_cap_kN: float
    Mu_cap_kNm: float
    utilization_ratio: float
    eccentricity_mm: float
    e_min_mm: float | None
    is_safe: bool
    classification: ColumnClassification
    governing_check: str
    clause_ref: str
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "Pu_kN": self.Pu_kN,
            "Mu_kNm": self.Mu_kNm,
            "Pu_cap_kN": self.Pu_cap_kN,
            "Mu_cap_kNm": self.Mu_cap_kNm,
            "utilization_ratio": self.utilization_ratio,
            "eccentricity_mm": self.eccentricity_mm,
            "e_min_mm": self.e_min_mm,
            "is_safe": self.is_safe,
            "classification": (
                self.classification.value
                if hasattr(self.classification, "value")
                else str(self.classification)
            ),
            "governing_check": self.governing_check,
            "clause_ref": self.clause_ref,
            "warnings": list(self.warnings),
        }

    def summary(self) -> str:
        """Return one-line human-readable summary."""
        status = "SAFE" if self.is_safe else "UNSAFE"
        return (
            f"Column Uniaxial Check ({status}): "
            f"Pu={self.Pu_kN:.1f}kN, Mu={self.Mu_kNm:.1f}kNm, "
            f"Utilization={self.utilization_ratio:.2f}, "
            f"Governed by: {self.governing_check}"
        )


@dataclass(frozen=True)
class PMInteractionResult:
    """P-M interaction curve for a column section per IS 456 Cl 39.5.

    Note: Unlike single-point result types (ColumnAxialResult, ColumnUniaxialResult),
    this type intentionally omits ``is_safe`` — an interaction *curve* is a diagnostic
    envelope, not a pass/fail design check.

    Attributes:
        points: Tuple of (Pu_kN, Mu_kNm) pairs along the interaction curve
        Pu_0_kN: Pure axial capacity (kN) — Cl 39.3
        Mu_0_kNm: Pure bending capacity (kN·m) — Pu = 0 intercept
        Pu_bal_kN: Balanced point axial load (kN)
        Mu_bal_kNm: Balanced point moment capacity (kN·m)
        fck: Concrete strength used (N/mm²)
        fy: Steel yield strength used (N/mm²)
        b_mm: Column width (mm)
        D_mm: Column depth in bending direction (mm)
        Asc_mm2: Total steel area (mm²)
        d_prime_mm: Cover to steel centroid (mm)
        clause_ref: IS 456 clause reference
        warnings: Tuple of warning messages
    """

    points: tuple[tuple[float, float], ...]
    Pu_0_kN: float
    Mu_0_kNm: float
    Pu_bal_kN: float
    Mu_bal_kNm: float
    fck: float
    fy: float
    b_mm: float
    D_mm: float
    Asc_mm2: float
    d_prime_mm: float
    clause_ref: str = "Cl. 39.5"
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "points": [{"Pu_kN": p, "Mu_kNm": m} for p, m in self.points],
            "Pu_0_kN": self.Pu_0_kN,
            "Mu_0_kNm": self.Mu_0_kNm,
            "Pu_bal_kN": self.Pu_bal_kN,
            "Mu_bal_kNm": self.Mu_bal_kNm,
            "fck": self.fck,
            "fy": self.fy,
            "b_mm": self.b_mm,
            "D_mm": self.D_mm,
            "Asc_mm2": self.Asc_mm2,
            "d_prime_mm": self.d_prime_mm,
            "clause_ref": self.clause_ref,
            "warnings": list(self.warnings),
        }

    def summary(self) -> str:
        """Return one-line human-readable summary."""
        return (
            f"P-M Curve: {len(self.points)} pts, "
            f"Pu_0={self.Pu_0_kN:.1f}kN, Mu_0={self.Mu_0_kNm:.1f}kNm, "
            f"Balanced=({self.Pu_bal_kN:.1f}kN, {self.Mu_bal_kNm:.1f}kNm)"
        )


@dataclass(frozen=True)
class ColumnBiaxialResult:
    """Result of biaxial bending check per IS 456 Cl 39.6.

    Attributes:
        Pu_kN: Applied axial load (kN)
        Mux_kNm: Applied moment about x-axis (kN·m)
        Muy_kNm: Applied moment about y-axis (kN·m)
        Mux1_kNm: Uniaxial moment capacity about x at Pu (kN·m)
        Muy1_kNm: Uniaxial moment capacity about y at Pu (kN·m)
        Puz_kN: Pure axial crush capacity (kN) per Cl 39.6a
        alpha_n: Bresler exponent (1.0–2.0)
        interaction_ratio: (Mux/Mux1)^αn + (Muy/Muy1)^αn
        is_safe: True if interaction_ratio ≤ 1.0
        classification: Column classification (SHORT or SLENDER)
        clause_ref: IS 456 clause reference
        warnings: Tuple of warning messages
    """

    Pu_kN: float
    Mux_kNm: float
    Muy_kNm: float
    Mux1_kNm: float
    Muy1_kNm: float
    Puz_kN: float
    alpha_n: float
    interaction_ratio: float
    is_safe: bool
    classification: ColumnClassification
    clause_ref: str = "Cl. 39.6"
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "Pu_kN": self.Pu_kN,
            "Mux_kNm": self.Mux_kNm,
            "Muy_kNm": self.Muy_kNm,
            "Mux1_kNm": self.Mux1_kNm,
            "Muy1_kNm": self.Muy1_kNm,
            "Puz_kN": self.Puz_kN,
            "alpha_n": self.alpha_n,
            "interaction_ratio": self.interaction_ratio,
            "is_safe": self.is_safe,
            "classification": (
                self.classification.value
                if hasattr(self.classification, "value")
                else str(self.classification)
            ),
            "clause_ref": self.clause_ref,
            "warnings": list(self.warnings),
        }

    def summary(self) -> str:
        """Return one-line human-readable summary."""
        status = "SAFE" if self.is_safe else "UNSAFE"
        return (
            f"Column Biaxial Check ({status}): "
            f"Pu={self.Pu_kN:.1f}kN, "
            f"Mux={self.Mux_kNm:.1f}kNm, Muy={self.Muy_kNm:.1f}kNm, "
            f"IR={self.interaction_ratio:.3f}, αn={self.alpha_n:.2f}"
        )


@dataclass(frozen=True)
class AdditionalMomentResult:
    """Additional moment for slender columns per IS 456 Cl 39.7.1.

    For slender columns (le/D >= 12), IS 456 requires an additional moment
    Ma = Pu × eadd, where eadd = D × (le/D)² / 2000.

    The additional moment may be reduced by factor k per Cl 39.7.1.1:
    k = (Puz - Pu) / (Puz - Pb) ≤ 1.0
    """

    # Per x-axis (bending about x → depth D governs)
    eadd_x_mm: float  # Additional eccentricity about x-axis (mm)
    Max_kNm: float  # Additional moment about x-axis (kN·m)
    slenderness_ratio_x: float  # le_x / D
    is_slender_x: bool  # True if le_x/D >= 12

    # Per y-axis (bending about y → width b governs)
    eadd_y_mm: float  # Additional eccentricity about y-axis (mm)
    May_kNm: float  # Additional moment about y-axis (kN·m)
    slenderness_ratio_y: float  # le_y / b
    is_slender_y: bool  # True if le_y/b >= 12

    # k-factor reduction (Cl 39.7.1.1)
    k: float  # Reduction factor (Puz - Pu) / (Puz - Pb), clamped ≤ 1.0
    Max_reduced_kNm: float  # k × Max_kNm
    May_reduced_kNm: float  # k × May_kNm
    Puz_kN: float  # Pure axial crush load
    Pb_kN: float  # Balanced failure axial load

    # Input echo
    Pu_kN: float
    b_mm: float
    D_mm: float
    lex_mm: float
    ley_mm: float

    clause_ref: str = "Cl. 39.7.1"
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def summary(self) -> str:
        """Human-readable summary."""
        lines = [f"Additional Moment — IS 456 {self.clause_ref}"]
        if self.is_slender_x:
            lines.append(
                f"  X-axis: le/D = {self.slenderness_ratio_x:.1f}, "
                f"eadd = {self.eadd_x_mm:.1f} mm, "
                f"Ma = {self.Max_kNm:.2f} kNm "
                f"(reduced: {self.Max_reduced_kNm:.2f} kNm)"
            )
        else:
            lines.append(
                f"  X-axis: le/D = {self.slenderness_ratio_x:.1f} "
                f"— SHORT, no additional moment"
            )
        if self.is_slender_y:
            lines.append(
                f"  Y-axis: le/b = {self.slenderness_ratio_y:.1f}, "
                f"eadd = {self.eadd_y_mm:.1f} mm, "
                f"Ma = {self.May_kNm:.2f} kNm "
                f"(reduced: {self.May_reduced_kNm:.2f} kNm)"
            )
        else:
            lines.append(
                f"  Y-axis: le/b = {self.slenderness_ratio_y:.1f} "
                f"— SHORT, no additional moment"
            )
        lines.append(
            f"  k = {self.k:.3f} "
            f"(Puz = {self.Puz_kN:.1f} kN, Pb = {self.Pb_kN:.1f} kN)"
        )
        return "\n".join(lines)


@dataclass(frozen=True)
class LongColumnResult:
    """Result of long (slender) column design per IS 456 Cl 39.7.

    For slender columns (le/D >= 12), IS 456 requires augmenting the
    design moment with an additional moment Ma = Pu × eadd, reduced
    by factor k. The final design moment is checked against the P-M
    interaction envelope via biaxial or uniaxial check.

    Attributes:
        Pu_kN: Applied factored axial load (kN)
        Mux_design_kNm: Final design moment about x (after augmentation) (kN·m)
        Muy_design_kNm: Final design moment about y (after augmentation) (kN·m)
        is_safe: True if design moments are within capacity
        classification_x: Column classification per x-axis
        classification_y: Column classification per y-axis
        is_slender_x: True if le_x/D >= 12
        is_slender_y: True if le_y/b >= 12
        eadd_x_mm: Additional eccentricity about x-axis (mm)
        eadd_y_mm: Additional eccentricity about y-axis (mm)
        Max_kNm: Additional moment about x-axis (kN·m)
        May_kNm: Additional moment about y-axis (kN·m)
        k: k-factor reduction (Cl 39.7.1.1)
        Max_reduced_kNm: k × Max_kNm (kN·m)
        May_reduced_kNm: k × May_kNm (kN·m)
        interaction_ratio: From biaxial or uniaxial check
        governing_check: "biaxial" or "uniaxial_x" or "uniaxial_y"
        Puz_kN: Pure axial crush capacity (kN)
        Pb_kN: Balanced failure axial load (kN)
        b_mm: Column width (mm)
        D_mm: Column depth (mm)
        lex_mm: Effective length about x-axis (mm)
        ley_mm: Effective length about y-axis (mm)
        braced: True if column is braced
        clause_ref: IS 456 clause reference
        warnings: Tuple of warning messages
    """

    Pu_kN: float
    Mux_design_kNm: float
    Muy_design_kNm: float
    is_safe: bool
    classification_x: ColumnClassification
    classification_y: ColumnClassification
    is_slender_x: bool
    is_slender_y: bool
    eadd_x_mm: float
    eadd_y_mm: float
    Max_kNm: float
    May_kNm: float
    k: float
    Max_reduced_kNm: float
    May_reduced_kNm: float
    interaction_ratio: float
    governing_check: str
    Puz_kN: float
    Pb_kN: float
    b_mm: float
    D_mm: float
    lex_mm: float
    ley_mm: float
    braced: bool
    clause_ref: str = "Cl. 39.7"
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result: dict = {}
        for f in fields(self):
            val = getattr(self, f.name)
            if isinstance(val, ColumnClassification):
                result[f.name] = val.name
            elif isinstance(val, tuple):
                result[f.name] = list(val)
            else:
                result[f.name] = val
        return result

    def summary(self) -> str:
        """Return one-line human-readable summary."""
        status = "SAFE" if self.is_safe else "UNSAFE"
        slender_axes = []
        if self.is_slender_x:
            slender_axes.append("x")
        if self.is_slender_y:
            slender_axes.append("y")
        slender_str = "+".join(slender_axes) if slender_axes else "none"
        return (
            f"Long Column Check ({status}): "
            f"Pu={self.Pu_kN:.1f}kN, "
            f"Mux_des={self.Mux_design_kNm:.1f}kNm, "
            f"Muy_des={self.Muy_design_kNm:.1f}kNm, "
            f"IR={self.interaction_ratio:.3f}, "
            f"slender={slender_str}, k={self.k:.3f}"
        )


@dataclass(frozen=True)
class HelicalReinforcementResult:
    """Result of helical reinforcement check per IS 456 Cl 39.4.

    For circular columns with helical reinforcement, IS 456 permits a
    1.05 enhancement factor on the short column axial capacity, provided
    the helical ratio requirement is met.

    Attributes:
        is_adequate: True if helical reinforcement meets IS 456 requirements
        enhancement_factor: 1.05 per Cl 39.4
        Pu_enhanced_kN: 1.05 × Pu_short_axial (kN)
        helical_ratio_provided: V_helix / V_core (provided ratio)
        helical_ratio_required: 0.36 × (Ag/Ac - 1) × fck/fy (required ratio)
        pitch_mm: Provided helix pitch (mm)
        min_pitch_mm: max(25mm, 3 × d_helix_bar) (mm)
        max_pitch_mm: min(75mm, D_core/6) (mm)
        pitch_ok: True if pitch is within limits
        D_core_mm: Core diameter (mm)
        clause_ref: IS 456 clause reference
        warnings: Tuple of warning messages
    """

    is_adequate: bool
    enhancement_factor: float
    Pu_enhanced_kN: float
    helical_ratio_provided: float
    helical_ratio_required: float
    pitch_mm: float
    min_pitch_mm: float
    max_pitch_mm: float
    pitch_ok: bool
    D_core_mm: float
    clause_ref: str = "Cl. 39.4"
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def summary(self) -> str:
        """Return one-line human-readable summary."""
        status = "ADEQUATE" if self.is_adequate else "INADEQUATE"
        return (
            f"Helical Reinforcement ({status}): "
            f"ratio={self.helical_ratio_provided:.4f} "
            f"(req={self.helical_ratio_required:.4f}), "
            f"pitch={self.pitch_mm:.0f}mm "
            f"[{self.min_pitch_mm:.0f}-{self.max_pitch_mm:.0f}mm], "
            f"Pu_enh={self.Pu_enhanced_kN:.1f}kN"
        )


@dataclass(frozen=True)
class ColumnDetailingResult:
    """Column detailing result per IS 456 Cl 26.5.3.

    Attributes:
        b_mm: Column width (mm)
        D_mm: Column depth (mm)
        Ag_mm2: Gross cross-sectional area (mm²)
        num_bars: Number of longitudinal bars
        bar_dia_mm: Longitudinal bar diameter (mm)
        Asc_provided_mm2: Total longitudinal steel area provided (mm²)
        steel_ratio: Asc / Ag
        min_steel_ok: True if ratio >= 0.8%
        max_steel_ok: True if ratio <= 4% (or 6% at lap)
        min_bars_ok: True if bar count >= minimum
        min_bar_dia_ok: True if bar diameter >= 12mm
        bar_spacing_mm: Minimum clear spacing between bars (mm)
        bar_spacing_ok: True if spacing checks pass
        tie_dia_mm: Provided/selected tie diameter (mm)
        tie_dia_required_mm: Minimum required tie diameter (mm)
        tie_spacing_mm: Provided tie spacing (mm)
        max_tie_spacing_mm: Maximum permissible tie spacing (mm)
        tie_spacing_ok: True if tie spacing <= max permissible
        cross_ties_needed: True if cross-ties are required (Cl 26.5.3.2c)
        is_valid: True if all checks pass
        clause_ref: IS 456 clause reference
        warnings: Tuple of warning messages
    """

    # Section
    b_mm: float
    D_mm: float
    Ag_mm2: float

    # Longitudinal bars
    num_bars: int
    bar_dia_mm: float
    Asc_provided_mm2: float
    steel_ratio: float
    min_steel_ok: bool
    max_steel_ok: bool
    min_bars_ok: bool
    min_bar_dia_ok: bool
    bar_spacing_mm: float
    bar_spacing_ok: bool

    # Ties
    tie_dia_mm: float
    tie_dia_required_mm: float
    tie_spacing_mm: float
    max_tie_spacing_mm: float
    tie_spacing_ok: bool
    cross_ties_needed: bool

    # Overall
    is_valid: bool
    clause_ref: str = "Cl. 26.5.3"
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def summary(self) -> str:
        """Return one-line human-readable summary."""
        status = "VALID" if self.is_valid else "INVALID"
        return (
            f"Column Detailing ({status}): "
            f"{self.num_bars}-T{self.bar_dia_mm:.0f} "
            f"(ρ={self.steel_ratio:.3f}), "
            f"ties T{self.tie_dia_mm:.0f}@{self.tie_spacing_mm:.0f}mm, "
            f"cross-ties={'YES' if self.cross_ties_needed else 'NO'}"
        )


# =============================================================================
# Footing Design Types — IS 456 Cl. 34, 31.6
# =============================================================================


class FootingType(Enum):
    """Footing classification."""

    ISOLATED_SQUARE = auto()
    ISOLATED_RECTANGULAR = auto()


@dataclass(frozen=True)
class FootingBearingResult:
    """Bearing pressure check per IS 456 Cl 34.1.

    Note: Sizing uses SERVICE (unfactored) loads per IS 456 Cl 34.1.
    Structural design (flexure, shear) uses FACTORED loads.
    """

    L_mm: float  # Footing length (mm)
    B_mm: float  # Footing width (mm)
    q_max_kPa: float  # Maximum soil pressure at service (kPa = kN/m²)
    q_min_kPa: float  # Minimum soil pressure at service (kPa)
    q_safe_kPa: float  # Allowable bearing capacity (kPa)
    pressure_type: str  # "uniform", "trapezoidal", "partial_contact"
    utilization_ratio: float  # q_max / q_safe
    is_safe: bool
    clause_ref: str = "Cl. 34.1"
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "L_mm": self.L_mm,
            "B_mm": self.B_mm,
            "q_max_kPa": self.q_max_kPa,
            "q_min_kPa": self.q_min_kPa,
            "q_safe_kPa": self.q_safe_kPa,
            "pressure_type": self.pressure_type,
            "utilization_ratio": self.utilization_ratio,
            "is_safe": self.is_safe,
            "clause_ref": self.clause_ref,
            "warnings": list(self.warnings),
        }

    def summary(self) -> str:
        """Return one-line human-readable summary."""
        status = "SAFE" if self.is_safe else "UNSAFE"
        return (
            f"Footing Bearing ({status}): {self.L_mm:.0f}×{self.B_mm:.0f}mm, "
            f"q_max={self.q_max_kPa:.1f}kPa, q_safe={self.q_safe_kPa:.1f}kPa, "
            f"Util={self.utilization_ratio:.2f}, Type={self.pressure_type}"
        )


@dataclass(frozen=True)
class FootingFlexureResult:
    """Flexural design per IS 456 Cl 34.2.3.1 — both directions."""

    # L-direction (steel runs parallel to B)
    Mu_L_kNm: float  # Moment at column face along L (kN·m)
    Ast_L_mm2: float  # Steel area for L-direction (mm²)
    pt_L_percent: float  # Steel percentage for L-direction
    cantilever_L_mm: float  # Cantilever (L-a)/2 (mm)

    # B-direction (steel runs parallel to L)
    Mu_B_kNm: float  # Moment at column face along B (kN·m)
    Ast_B_mm2: float  # Steel area for B-direction (mm²)
    pt_B_percent: float  # Steel percentage for B-direction
    cantilever_B_mm: float  # Cantilever (B-b)/2 (mm)

    d_mm: float  # Effective depth used (mm)
    is_safe: bool
    central_band_fraction: float = (
        1.0  # Cl 34.3.1: fraction in central band (rectangular)
    )
    clause_ref: str = "Cl. 34.2.3.1"
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "Mu_L_kNm": self.Mu_L_kNm,
            "Ast_L_mm2": self.Ast_L_mm2,
            "pt_L_percent": self.pt_L_percent,
            "cantilever_L_mm": self.cantilever_L_mm,
            "Mu_B_kNm": self.Mu_B_kNm,
            "Ast_B_mm2": self.Ast_B_mm2,
            "pt_B_percent": self.pt_B_percent,
            "cantilever_B_mm": self.cantilever_B_mm,
            "d_mm": self.d_mm,
            "is_safe": self.is_safe,
            "central_band_fraction": self.central_band_fraction,
            "clause_ref": self.clause_ref,
            "warnings": list(self.warnings),
        }

    def summary(self) -> str:
        """Return one-line summary showing the critical (larger Mu) direction."""
        status = "SAFE" if self.is_safe else "UNSAFE"
        # Show critical direction
        if self.Mu_L_kNm >= self.Mu_B_kNm:
            return (
                f"Footing Flexure ({status}): Mu_L={self.Mu_L_kNm:.1f}kNm (governs), "
                f"Ast_L={self.Ast_L_mm2:.0f}mm², pt_L={self.pt_L_percent:.2f}%"
            )
        return (
            f"Footing Flexure ({status}): Mu_B={self.Mu_B_kNm:.1f}kNm (governs), "
            f"Ast_B={self.Ast_B_mm2:.0f}mm², pt_B={self.pt_B_percent:.2f}%"
        )


@dataclass(frozen=True)
class FootingOneWayShearResult:
    """One-way shear check per IS 456 Cl 34.2.4.1(a) — both directions."""

    tau_v_nmm2: float  # Nominal shear stress at governing section (N/mm²)
    tau_c_nmm2: float  # Design shear strength from Table 19 (N/mm²)
    Vu_kN: float  # Shear force at governing critical section (kN)
    d_mm: float  # Effective depth (mm)
    critical_section_mm: float  # Distance from column face to critical section (mm)
    utilization_ratio: float  # tau_v / tau_c (governing direction)
    is_safe: bool  # True only if BOTH directions pass
    governing_direction: str = "L"  # "L" or "B" — which direction governs
    clause_ref: str = "Cl. 34.2.4.1(a)"
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "tau_v_nmm2": self.tau_v_nmm2,
            "tau_c_nmm2": self.tau_c_nmm2,
            "Vu_kN": self.Vu_kN,
            "d_mm": self.d_mm,
            "critical_section_mm": self.critical_section_mm,
            "utilization_ratio": self.utilization_ratio,
            "is_safe": self.is_safe,
            "governing_direction": self.governing_direction,
            "clause_ref": self.clause_ref,
            "warnings": list(self.warnings),
        }

    def summary(self) -> str:
        """Return one-line human-readable summary."""
        status = "SAFE" if self.is_safe else "UNSAFE"
        return (
            f"Footing One-Way Shear ({status}, governs={self.governing_direction}): "
            f"τv={self.tau_v_nmm2:.3f}, τc={self.tau_c_nmm2:.3f} N/mm², "
            f"Util={self.utilization_ratio:.2f}"
        )


@dataclass(frozen=True)
class FootingPunchingResult:
    """Punching shear check per IS 456 Cl 31.6.1 + 34.2.4.1(b)."""

    tau_v_nmm2: float  # Nominal punching shear stress (N/mm²)
    tau_c_nmm2: float  # Permissible punching stress = ks × 0.25√fck (N/mm²)
    perimeter_mm: float  # Critical perimeter at d/2 from column face (mm)
    Vu_punch_kN: float  # Shear force on critical section (kN)
    d_mm: float  # Effective depth (mm)
    beta_c: float  # min(a,b)/max(a,b) — column aspect ratio
    ks: float  # (0.5 + beta_c) ≤ 1.0
    utilization_ratio: float  # tau_v / tau_c
    is_safe: bool
    clause_ref: str = "Cl. 31.6.1"
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "tau_v_nmm2": self.tau_v_nmm2,
            "tau_c_nmm2": self.tau_c_nmm2,
            "perimeter_mm": self.perimeter_mm,
            "Vu_punch_kN": self.Vu_punch_kN,
            "d_mm": self.d_mm,
            "beta_c": self.beta_c,
            "ks": self.ks,
            "utilization_ratio": self.utilization_ratio,
            "is_safe": self.is_safe,
            "clause_ref": self.clause_ref,
            "warnings": list(self.warnings),
        }

    def summary(self) -> str:
        """Return one-line human-readable summary."""
        status = "SAFE" if self.is_safe else "UNSAFE"
        return (
            f"Footing Punching Shear ({status}): "
            f"τv={self.tau_v_nmm2:.3f}, τc={self.tau_c_nmm2:.3f} N/mm², "
            f"βc={self.beta_c:.2f}, ks={self.ks:.2f}, "
            f"Util={self.utilization_ratio:.2f}"
        )


# =============================================================================
# Multi-Layer Reinforcement Types
# =============================================================================


@dataclass(frozen=True)
class RebarLayer:
    """Single layer of reinforcement bars.

    Attributes:
        bar_dia_mm: Bar diameter (mm). Must be positive.
        count: Number of bars. Must be >= 1.
        distance_from_bottom_mm: Distance from bottom face of beam to centroid
            of this layer (mm).
    """

    bar_dia_mm: float
    count: int
    distance_from_bottom_mm: float

    def __post_init__(self) -> None:
        if self.bar_dia_mm <= 0:
            raise ValueError(f"bar_dia_mm must be positive, got {self.bar_dia_mm}")
        if self.count < 1:
            raise ValueError(f"count must be >= 1, got {self.count}")
        if self.distance_from_bottom_mm < 0:
            raise ValueError(
                f"distance_from_bottom_mm cannot be negative, "
                f"got {self.distance_from_bottom_mm}"
            )

    @property
    def area_mm2(self) -> float:
        """Total area of bars in this layer (mm²)."""
        return self.count * math.pi / 4 * self.bar_dia_mm**2


@dataclass(frozen=True)
class RebarArrangement:
    """Multi-layer bar arrangement with weighted centroid calculation.

    Attributes:
        layers: Tuple of RebarLayer objects. Must not be empty.
    """

    layers: tuple[RebarLayer, ...]

    def __post_init__(self) -> None:
        if not self.layers:
            raise ValueError("At least one rebar layer required")

    @property
    def centroid_from_bottom_mm(self) -> float:
        """Weighted centroid of all bars from bottom face (mm).

        Uses area-weighted average: d_cg = Σ(Asi × di) / Σ(Asi)
        """
        total_area = sum(layer.area_mm2 for layer in self.layers)
        weighted_dist = sum(
            layer.area_mm2 * layer.distance_from_bottom_mm for layer in self.layers
        )
        return weighted_dist / total_area

    @property
    def total_area_mm2(self) -> float:
        """Total area of all bars across all layers (mm²)."""
        return sum(layer.area_mm2 for layer in self.layers)

    @property
    def layer_count(self) -> int:
        """Number of layers."""
        return len(self.layers)

    def effective_depth(self, D_mm: float) -> float:
        """Calculate effective depth from overall depth.

        d = D - centroid_from_bottom

        Args:
            D_mm: Overall beam depth (mm).

        Returns:
            Effective depth (mm) measured from compression face to
            centroid of tension steel.
        """
        d = D_mm - self.centroid_from_bottom_mm
        if d <= 0:
            raise ValueError(
                f"Effective depth must be positive: "
                f"D={D_mm}, centroid={self.centroid_from_bottom_mm}"
            )
        return d
