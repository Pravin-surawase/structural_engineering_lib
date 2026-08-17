"""
Smart Analysis Pydantic Models.

Models for AI-assisted design analysis API endpoints.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

# =============================================================================
# Load Analysis Models
# =============================================================================


class LoadItem(BaseModel):
    """Single load definition."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    load_type: Literal["udl", "point"] = Field(
        description="Load type: 'udl' (kN/m) or 'point' (kN)"
    )
    magnitude: float = Field(
        gt=0, description="Load magnitude (kN/m for UDL, kN for point)"
    )
    position_mm: float = Field(
        default=0.0,
        ge=0,
        description="Position from left support (mm), required for point loads",
    )
    end_position_mm: float | None = Field(
        default=None,
        ge=0,
        description="UDL end position (mm); omitted means the right support",
    )

    @model_validator(mode="after")
    def validate_partial_load_contract(self) -> "LoadItem":
        if self.end_position_mm is not None and self.load_type != "udl":
            raise ValueError("end_position_mm is only valid for UDL loads")
        return self


class LoadAnalysisRequest(BaseModel):
    """Request model for simple load analysis (BMD/SFD)."""

    model_config = ConfigDict(
        extra="forbid",
        allow_inf_nan=False,
        json_schema_extra={
            "examples": [
                {
                    "span_mm": 6000.0,
                    "support_condition": "simply_supported",
                    "loads": [
                        {
                            "load_type": "udl",
                            "magnitude": 20.0,
                            "position_mm": 0.0,
                        }
                    ],
                    "num_points": 51,
                }
            ]
        },
    )

    span_mm: float = Field(gt=0, le=30000, description="Beam span (mm)")
    support_condition: Literal["simply_supported", "cantilever"] = Field(
        default="simply_supported",
        description="Support type",
    )
    loads: list[LoadItem] = Field(
        min_length=1,
        description="List of applied loads",
    )
    num_points: int = Field(
        default=51, ge=11, le=201, description="Discretization points"
    )

    @model_validator(mode="after")
    def validate_load_locations(self) -> "LoadAnalysisRequest":
        for index, load in enumerate(self.loads):
            if load.position_mm > self.span_mm:
                raise ValueError(f"loads[{index}].position_mm exceeds span_mm")
            if load.end_position_mm is not None:
                if load.end_position_mm <= load.position_mm:
                    raise ValueError(
                        f"loads[{index}].end_position_mm must exceed position_mm"
                    )
                if load.end_position_mm > self.span_mm:
                    raise ValueError(f"loads[{index}].end_position_mm exceeds span_mm")
        return self


class CriticalPointResponse(BaseModel):
    """Critical point on BMD/SFD diagram."""

    position_mm: float
    point_type: str
    bm_knm: float
    sf_kn: float


class LoadAnalysisResponse(BaseModel):
    """Response model for load analysis with BMD/SFD data."""

    span_mm: float
    support_condition: str
    positions_mm: list[float]
    bmd_knm: list[float]
    sfd_kn: list[float]
    max_bm_knm: float
    min_bm_knm: float
    max_sf_kn: float
    min_sf_kn: float
    critical_points: list[CriticalPointResponse]


# =============================================================================
# Request Models
# =============================================================================


class SmartAnalysisRequest(BaseModel):
    """Request model for smart design analysis."""

    # Section dimensions
    width: float = Field(gt=0, le=2000.0, description="Beam width (mm)")
    depth: float = Field(gt=0, le=3000.0, description="Beam depth (mm)")
    effective_depth: float = Field(
        gt=0,
        description="Explicit effective depth d (mm); no hidden cover assumption",
    )

    # Loading
    moment: float = Field(ge=0, description="Factored moment Mu (kN·m)")
    shear: float = Field(default=0.0, ge=0, description="Factored shear Vu (kN)")

    # Material properties
    fck: float = Field(default=25.0, ge=15.0, le=80.0, description="fck (N/mm²)")
    fy: float = Field(default=500.0, ge=250.0, le=600.0, description="fy (N/mm²)")

    # Context for analysis
    span_length: float = Field(
        gt=0,
        description="Explicit beam span length (mm)",
    )
    exposure_class: str = Field(
        default="moderate",
        description="Exposure condition per IS 456",
    )
    seismic_zone: str | None = Field(
        default=None,
        description="Seismic zone for ductile detailing",
    )

    # Analysis options
    include_suggestions: bool = Field(
        default=True,
        description="Include design improvement suggestions",
    )
    include_code_checks: bool = Field(
        default=True,
        description="Include code compliance checks",
    )
    analyze_efficiency: bool = Field(
        default=True,
        description="Analyze design efficiency and cost-effectiveness",
    )

    @model_validator(mode="after")
    def validate_cross_fields(self) -> "SmartAnalysisRequest":
        """Validate cross-field constraints."""
        if self.depth / self.width > 6:
            raise ValueError(
                f"Depth/width ratio {self.depth / self.width:.1f} exceeds "
                f"practical limit of 6"
            )
        if self.effective_depth >= self.depth:
            raise ValueError(
                f"effective_depth ({self.effective_depth}mm) must be less than "
                f"depth ({self.depth}mm)"
            )
        return self


# =============================================================================
# Response Models
# =============================================================================


class Suggestion(BaseModel):
    """Design suggestion with priority."""

    category: str = Field(
        description="Suggestion category",
        examples=["geometry", "reinforcement", "materials", "detailing"],
    )
    priority: Literal["high", "medium", "low"] = Field(
        description="Suggestion priority"
    )
    title: str = Field(description="Short suggestion title")
    description: str = Field(description="Detailed explanation")
    potential_savings: float | None = Field(
        default=None,
        description="Estimated cost savings (%)",
    )
    action_required: bool = Field(
        default=False,
        description="Whether action is required (vs optional)",
    )


class CodeCheck(BaseModel):
    """Code compliance check result."""

    clause: str = Field(description="Code clause reference")
    description: str = Field(description="Check description")
    passed: bool = Field(description="Whether check passed")
    calculated_value: float | None = Field(default=None, description="Calculated value")
    limit_value: float | None = Field(default=None, description="Code limit value")
    message: str | None = Field(default=None, description="Additional message")


class SmartDesignSummary(BaseModel):
    """Explicit inputs and canonical design-check semantics."""

    width_mm: float
    depth_mm: float
    effective_depth_mm: float
    span_mm: float
    moment_knm: float
    shear_kn: float
    fck_nmm2: float
    fy_nmm2: float
    design_status: Literal["PASS", "WARNING", "FAIL"]
    governing_utilization: float = Field(ge=0)
    capacity_margin: float = Field(ge=0, le=1)
    governing_check: str
    key_issues: list[str] = Field(default_factory=list)
    quick_wins: list[str] = Field(default_factory=list)


class SmartScoreMetrics(BaseModel):
    """Core-owned normalized advisory scores; no transport relabelling."""

    cost_efficiency: float = Field(ge=0, le=1)
    constructability: float = Field(ge=0, le=1)
    robustness: float = Field(ge=0, le=1)
    overall_score: float = Field(ge=0, le=1)


class SmartCostAnalysis(BaseModel):
    """Cost-analysis values calculated by the core smart-design service."""

    current_cost: float = Field(ge=0)
    optimal_cost: float = Field(ge=0)
    savings_percent: float = Field(ge=0)
    baseline_alternative: dict | None = None
    optimal_alternative: dict | None = None
    alternatives: list[dict] = Field(default_factory=list)


class SmartAnalysisResponse(BaseModel):
    """Response model for smart analysis."""

    success: bool = Field(description="Whether analysis succeeded")
    message: str = Field(description="Summary message")

    # Design summary
    design_summary: SmartDesignSummary

    # Code compliance
    code_checks: list[CodeCheck] = Field(
        default_factory=list,
        description="Code compliance check results",
    )
    all_checks_passed: bool = Field(description="Whether all code checks passed")

    # Suggestions
    suggestions: list[Suggestion] = Field(
        default_factory=list,
        description="Design improvement suggestions",
    )
    critical_suggestions: int = Field(
        default=0,
        description="Number of high-priority suggestions",
    )

    # Core-owned advisory scores
    scores: SmartScoreMetrics | None = Field(
        default=None,
        description="Normalized advisory scores calculated by the core service",
    )

    # Core-owned cost analysis
    cost_analysis: SmartCostAnalysis | None = Field(
        default=None,
        description="Cost analysis calculated by the core service",
    )

    # Warnings
    warnings: list[str] = Field(default_factory=list, description="Analysis warnings")
