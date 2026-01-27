"""
Insights Models — Pydantic models for insights endpoints.

Covers dashboard data, code checks, and rebar suggestions.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# =============================================================================
# Request Models
# =============================================================================


class BeamParams(BaseModel):
    """Beam geometry parameters."""

    b_mm: float = Field(300.0, description="Beam width (mm)")
    D_mm: float = Field(450.0, description="Beam total depth (mm)")
    cover_mm: float = Field(40.0, description="Clear cover (mm)")
    span_mm: float = Field(5000.0, description="Span length (mm)")
    fck: float = Field(25.0, description="Concrete grade (N/mm²)")
    fy: float = Field(500.0, description="Steel grade (N/mm²)")
    stirrup_dia_mm: float = Field(8.0, description="Stirrup diameter (mm)")
    agg_size_mm: float = Field(20.0, description="Aggregate size (mm)")


class RebarConfig(BaseModel):
    """Rebar configuration."""

    bar_count: int = Field(4, description="Number of bars", ge=2)
    bar_dia_mm: float = Field(16.0, description="Bar diameter (mm)")
    layers: int = Field(1, description="Number of layers", ge=1)
    stirrup_dia_mm: float = Field(8.0, description="Stirrup diameter (mm)")


class DashboardRequest(BaseModel):
    """Request for dashboard generation."""

    design_result: dict = Field(..., description="Design result from design_beam_is456")
    beam_params: BeamParams | None = Field(None, description="Optional beam parameters")


class CodeChecksRequest(BaseModel):
    """Request for live code checks."""

    beam: BeamParams = Field(..., description="Beam parameters")
    config: RebarConfig = Field(..., description="Rebar configuration")


class RebarSuggestRequest(BaseModel):
    """Request for rebar suggestions."""

    beam: BeamParams = Field(..., description="Beam parameters")
    ast_required_mm2: float = Field(500.0, description="Required steel area (mm²)")
    min_bars: int = Field(2, description="Minimum number of bars", ge=2)
    max_layers: int = Field(2, description="Maximum number of layers", ge=1, le=3)
    max_options: int = Field(5, description="Maximum suggestions to return", ge=1, le=10)


# =============================================================================
# Response Models
# =============================================================================


class UtilizationData(BaseModel):
    """Utilization breakdown."""

    moment: float = Field(..., description="Moment utilization ratio")
    shear: float = Field(..., description="Shear utilization ratio")
    overall: float = Field(..., description="Overall utilization ratio")


class SteelData(BaseModel):
    """Steel quantity data."""

    astRequired: float = Field(..., description="Required steel area (mm²)")
    astProvided: float = Field(..., description="Provided steel area (mm²)")
    ratioPercent: float = Field(..., description="Steel ratio (%)")


class CapacityData(BaseModel):
    """Capacity data."""

    momentKnm: float = Field(..., description="Moment capacity (kN·m)")
    shearKn: float = Field(..., description="Shear capacity (kN)")


class AppliedData(BaseModel):
    """Applied loads data."""

    momentKnm: float = Field(..., description="Applied moment (kN·m)")
    shearKn: float = Field(..., description="Applied shear (kN)")


class CodeChecksData(BaseModel):
    """Code checks summary."""

    passed: int = Field(..., description="Number of checks passed")
    total: int = Field(..., description="Total number of checks")
    critical: list[str] = Field(default_factory=list, description="Critical check failures")


class DashboardResponse(BaseModel):
    """Dashboard data response."""

    beamId: str = Field(..., description="Beam identifier")
    status: str = Field(..., description="Overall status (pass/fail/warning)")
    utilization: UtilizationData = Field(..., description="Utilization ratios")
    steel: SteelData = Field(..., description="Steel quantities")
    capacity: CapacityData = Field(..., description="Beam capacities")
    applied: AppliedData = Field(..., description="Applied loads")
    codeChecks: CodeChecksData = Field(..., description="Code checks summary")
    messages: list[str] = Field(default_factory=list, description="Messages/warnings")


class SingleCodeCheck(BaseModel):
    """Single IS 456 code check result."""

    clause: str = Field(..., description="IS 456 clause reference")
    description: str = Field(..., description="Check description")
    passed: bool = Field(..., description="Whether check passed")
    value: float | None = Field(None, description="Actual value")
    limit: float | None = Field(None, description="Limit value")
    message: str = Field("", description="Status message")


class CodeChecksResponse(BaseModel):
    """Code checks response."""

    overallPass: bool = Field(..., description="All checks passed")
    checks: list[SingleCodeCheck] = Field(..., description="Individual check results")
    errors: list[str] = Field(default_factory=list, description="Error messages")
    warnings: list[str] = Field(default_factory=list, description="Warning messages")
    passCount: int = Field(..., description="Number of checks passed")
    failCount: int = Field(..., description="Number of checks failed")


class RebarSuggestion(BaseModel):
    """A suggested rebar configuration."""

    barCount: int = Field(..., description="Number of bars")
    barDia: float = Field(..., description="Bar diameter (mm)")
    layers: int = Field(..., description="Number of layers")
    astProvided: float = Field(..., description="Steel area provided (mm²)")
    utilization: float = Field(..., description="Steel utilization ratio")
    costIndex: float = Field(..., description="Relative cost index")
    spacingOk: bool = Field(..., description="Spacing check passed")
    message: str = Field("", description="Additional info")


class RebarSuggestResponse(BaseModel):
    """Rebar suggestions response."""

    success: bool = Field(True, description="Request succeeded")
    suggestions: list[RebarSuggestion] = Field(..., description="Rebar options")
    target_ast_mm2: float = Field(..., description="Target steel area")
    message: str = Field("", description="Summary message")
