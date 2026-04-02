"""
IS 456 Compliance Check Pydantic Models.

Request/response models for standalone IS 456 compliance check endpoints:
- Beam ductility (IS 13920)
- Beam slenderness (IS 456 Cl 23.3)
- Anchorage at simple support (IS 456 Cl 26.2.3.3)
- Deflection span/depth ratio (IS 456 Cl 23.2)
- Crack width (IS 456 Annex F)
- Multi-case compliance report

All dimensions in mm, forces in kN, moments in kN·m, stresses in N/mm².
"""

from typing import Any

from pydantic import BaseModel, Field

# =============================================================================
# 1. Ductility Check (IS 13920)
# =============================================================================


class DuctilityCheckRequest(BaseModel):
    """Request for IS 13920 beam ductility check."""

    b: float = Field(..., gt=0, le=2000, description="Beam width (mm)")
    D: float = Field(..., gt=0, le=3000, description="Overall depth (mm)")
    d: float = Field(..., gt=0, le=3000, description="Effective depth (mm)")
    fck: float = Field(..., ge=15, le=80, description="Concrete strength (N/mm²)")
    fy: float = Field(..., ge=250, le=600, description="Steel yield strength (N/mm²)")
    min_long_bar_dia: float = Field(
        ..., ge=6, le=40, description="Minimum longitudinal bar diameter (mm)"
    )


class DuctilityCheckResponse(BaseModel):
    """Response for IS 13920 beam ductility check."""

    is_geometry_valid: bool = Field(description="Geometry satisfies IS 13920 Cl 6.1")
    min_pt: float = Field(description="Minimum tension steel percentage (%)")
    max_pt: float = Field(description="Maximum tension steel percentage (%)")
    confinement_spacing: float = Field(
        description="Hoop spacing in confinement zone (mm)"
    )
    remarks: str = Field(default="", description="Summary remarks")
    errors: list[dict[str, Any]] = Field(
        default_factory=list, description="Structured design errors"
    )


# =============================================================================
# 2. Slenderness Check (IS 456 Cl 23.3)
# =============================================================================


class SlendernessCheckRequest(BaseModel):
    """Request for beam slenderness / lateral stability check."""

    b_mm: float = Field(
        ..., gt=0, le=2000, description="Width of compression flange (mm)"
    )
    d_mm: float = Field(..., gt=0, le=3000, description="Overall depth of beam (mm)")
    l_eff_mm: float = Field(
        ..., gt=0, le=100000, description="Effective unsupported length (mm)"
    )
    beam_type: str = Field(
        default="simply_supported",
        description="Beam type: 'simply_supported', 'continuous', or 'cantilever'",
    )
    has_lateral_restraint: bool = Field(
        default=False,
        description="Whether beam is laterally restrained (e.g. slab on top)",
    )


class SlendernessCheckResponse(BaseModel):
    """Response for beam slenderness check."""

    is_ok: bool = Field(description="True if beam passes slenderness checks")
    is_slender: bool = Field(description="True if beam is classified as slender")
    slenderness_ratio: float = Field(description="l_eff / b ratio")
    slenderness_limit: float = Field(description="Maximum allowable ratio")
    utilization: float = Field(description="ratio / limit (>1.0 is fail)")
    depth_to_width_ratio: float = Field(description="D/b ratio")
    remarks: str = Field(description="Human-readable summary")
    errors: list[str] = Field(default_factory=list, description="Compliance errors")
    warnings: list[str] = Field(default_factory=list, description="Warnings")


# =============================================================================
# 3. Anchorage Check (IS 456 Cl 26.2.3.3)
# =============================================================================


class AnchorageCheckRequest(BaseModel):
    """Request for anchorage check at simple support."""

    bar_dia_mm: float = Field(..., ge=6, le=40, description="Bottom bar diameter (mm)")
    fck: float = Field(..., ge=15, le=80, description="Concrete strength (N/mm²)")
    fy: float = Field(..., ge=250, le=600, description="Steel yield strength (N/mm²)")
    vu_kn: float = Field(..., gt=0, description="Factored shear force at support (kN)")
    support_width_mm: float = Field(
        ..., gt=0, le=2000, description="Width of support (mm)"
    )
    cover_mm: float = Field(
        default=40.0, ge=20, le=75, description="Clear cover at support (mm)"
    )
    bar_type: str = Field(default="deformed", description="'plain' or 'deformed'")
    has_standard_bend: bool = Field(
        default=True, description="True if bar has 90° bend at support"
    )


class AnchorageCheckResponse(BaseModel):
    """Response for anchorage check at simple support."""

    is_adequate: bool = Field(description="True if anchorage is sufficient")
    ld_required: float = Field(description="Development length required (mm)")
    ld_available: float = Field(description="Available development length (mm)")
    m1_enhancement: float = Field(description="Enhancement factor from Mu/Vu")
    utilization: float = Field(description="ld_required / ld_available (>1.0 fails)")
    errors: list[str] = Field(default_factory=list, description="Issues found")
    warnings: list[str] = Field(default_factory=list, description="Warnings")


# =============================================================================
# 4. Deflection Span/Depth Check (IS 456 Cl 23.2)
# =============================================================================


class DeflectionCheckRequest(BaseModel):
    """Request for deflection span/depth ratio check."""

    span_mm: float = Field(..., gt=0, le=50000, description="Clear span (mm)")
    d_mm: float = Field(..., gt=0, le=3000, description="Effective depth (mm)")
    support_condition: str = Field(
        default="simply_supported",
        description="'simply_supported', 'continuous', or 'cantilever'",
    )
    base_allowable_ld: float | None = Field(
        default=None, gt=0, description="Base L/d limit (overrides default)"
    )
    mf_tension_steel: float | None = Field(
        default=None, gt=0, description="Tension steel modification factor"
    )
    mf_compression_steel: float | None = Field(
        default=None, gt=0, description="Compression steel modification factor"
    )
    mf_flanged: float | None = Field(
        default=None, gt=0, description="Flanged beam modification factor"
    )


class DeflectionCheckResponse(BaseModel):
    """Response for deflection span/depth ratio check."""

    is_ok: bool = Field(description="True if deflection check passes")
    remarks: str = Field(description="Human-readable summary")
    support_condition: str = Field(description="Support condition used")
    assumptions: list[str] = Field(default_factory=list, description="Assumptions made")
    inputs: dict[str, Any] = Field(
        default_factory=dict, description="Input values used"
    )
    computed: dict[str, Any] = Field(
        default_factory=dict, description="Computed values (L/d actual, L/d allowable)"
    )


# =============================================================================
# 5. Crack Width Check (IS 456 Annex F)
# =============================================================================


class CrackWidthCheckRequest(BaseModel):
    """Request for crack width check."""

    exposure_class: str = Field(
        default="moderate",
        description="Exposure class: 'mild', 'moderate', 'severe', 'very_severe', 'extreme'",
    )
    limit_mm: float | None = Field(
        default=None, gt=0, description="Crack width limit (mm), overrides defaults"
    )
    acr_mm: float | None = Field(
        default=None,
        gt=0,
        description="Distance from point considered to nearest bar surface (mm)",
    )
    cmin_mm: float | None = Field(
        default=None, gt=0, description="Minimum cover to bar surface (mm)"
    )
    h_mm: float | None = Field(default=None, gt=0, description="Member depth (mm)")
    x_mm: float | None = Field(
        default=None, gt=0, description="Neutral axis depth (mm)"
    )
    epsilon_m: float | None = Field(
        default=None, description="Mean strain at reinforcement level"
    )
    fs_service_nmm2: float | None = Field(
        default=None, ge=0, description="Steel stress at service (N/mm²)"
    )
    es_nmm2: float = Field(
        default=200000.0, gt=0, description="Modulus of elasticity of steel (N/mm²)"
    )


class CrackWidthCheckResponse(BaseModel):
    """Response for crack width check."""

    is_ok: bool = Field(description="True if crack width is within limit")
    remarks: str = Field(description="Human-readable summary")
    exposure_class: str = Field(description="Exposure class used")
    assumptions: list[str] = Field(default_factory=list, description="Assumptions made")
    inputs: dict[str, Any] = Field(
        default_factory=dict, description="Input values used"
    )
    computed: dict[str, Any] = Field(
        default_factory=dict, description="Computed values (width, limit)"
    )


# =============================================================================
# 6. Compliance Report (Multi-case)
# =============================================================================


class ComplianceCaseInput(BaseModel):
    """A single load case for compliance checking."""

    case_id: str = Field(description="Unique case identifier")
    mu_knm: float = Field(ge=0, description="Factored moment (kN·m)")
    vu_kn: float = Field(ge=0, description="Factored shear (kN)")


class DeflectionParamsInput(BaseModel):
    """Optional deflection parameters for compliance report."""

    span_mm: float | None = Field(default=None, gt=0, description="Span (mm)")
    d_mm: float | None = Field(default=None, gt=0, description="Effective depth (mm)")
    support_condition: str | None = Field(default=None, description="Support condition")


class CrackWidthParamsInput(BaseModel):
    """Optional crack width parameters for compliance report."""

    exposure: str | None = Field(default=None, description="Exposure class")
    max_crack_width_mm: float | None = Field(
        default=None, gt=0, description="Max allowable crack width (mm)"
    )


class ComplianceReportRequest(BaseModel):
    """Request for multi-case IS 456 compliance report."""

    cases: list[ComplianceCaseInput] = Field(
        ..., min_length=1, description="Load cases to check"
    )
    b_mm: float = Field(..., gt=0, le=2000, description="Beam width (mm)")
    D_mm: float = Field(..., gt=0, le=3000, description="Overall depth (mm)")
    d_mm: float = Field(..., gt=0, le=3000, description="Effective depth (mm)")
    fck_nmm2: float = Field(..., ge=15, le=80, description="Concrete strength (N/mm²)")
    fy_nmm2: float = Field(
        ..., ge=250, le=600, description="Steel yield strength (N/mm²)"
    )
    d_dash_mm: float = Field(
        default=50.0, ge=0, description="Compression steel depth from top (mm)"
    )
    asv_mm2: float = Field(
        default=100.0, ge=0, description="Area of stirrup legs (mm²)"
    )
    pt_percent: float | None = Field(
        default=None,
        ge=0,
        le=6,
        description="Tension steel percentage for shear table lookup (%)",
    )
    deflection_defaults: DeflectionParamsInput | None = Field(
        default=None, description="Default deflection parameters"
    )
    crack_width_defaults: CrackWidthParamsInput | None = Field(
        default=None, description="Default crack width parameters"
    )


class ComplianceCaseOutput(BaseModel):
    """Result for a single compliance case."""

    case_id: str = Field(description="Case identifier")
    mu_knm: float = Field(description="Applied moment (kN·m)")
    vu_kn: float = Field(description="Applied shear (kN)")
    is_ok: bool = Field(description="Overall pass/fail")
    governing_utilization: float = Field(description="Governing utilization ratio")
    utilizations: dict[str, float] = Field(
        default_factory=dict, description="Per-check utilization ratios"
    )
    failed_checks: list[str] = Field(
        default_factory=list, description="List of failed checks"
    )
    remarks: str = Field(default="", description="Summary remarks")


class ComplianceReportResponse(BaseModel):
    """Response for multi-case compliance report."""

    is_ok: bool = Field(description="True if all cases pass")
    governing_case_id: str = Field(description="ID of the governing (worst) case")
    governing_utilization: float = Field(
        description="Utilization ratio of governing case"
    )
    cases: list[ComplianceCaseOutput] = Field(description="Per-case results")
    summary: dict[str, Any] = Field(
        default_factory=dict, description="Summary statistics"
    )
