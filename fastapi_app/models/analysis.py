"""
Smart Analysis Pydantic Models.

Models for AI-assisted design analysis API endpoints.
"""

from typing import Literal

from pydantic import BaseModel, Field


# =============================================================================
# Request Models
# =============================================================================


class SmartAnalysisRequest(BaseModel):
    """Request model for smart design analysis."""

    # Section dimensions
    width: float = Field(gt=0, le=2000.0, description="Beam width (mm)")
    depth: float = Field(gt=0, le=3000.0, description="Beam depth (mm)")

    # Loading
    moment: float = Field(ge=0, description="Factored moment Mu (kN·m)")
    shear: float = Field(default=0.0, ge=0, description="Factored shear Vu (kN)")

    # Material properties
    fck: float = Field(default=25.0, ge=15.0, le=80.0, description="fck (N/mm²)")
    fy: float = Field(default=500.0, ge=250.0, le=600.0, description="fy (N/mm²)")

    # Context for analysis
    span_length: float | None = Field(
        default=None,
        gt=0,
        description="Beam span length (mm) for deflection analysis",
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


class EfficiencyMetrics(BaseModel):
    """Design efficiency metrics."""

    utilization_ratio: float = Field(
        ge=0, le=2.0, description="Moment utilization ratio Mu/Mu_cap"
    )
    steel_efficiency: float = Field(
        ge=0, le=1.0, description="Steel utilization vs max allowed"
    )
    concrete_efficiency: float = Field(
        ge=0, le=1.0, description="Concrete utilization vs capacity"
    )
    overall_efficiency: float = Field(
        ge=0, le=1.0, description="Overall design efficiency score"
    )
    efficiency_grade: str = Field(
        description="Efficiency grade (A-F)",
        pattern="^[A-F]$",
    )
    efficiency_comment: str = Field(description="Explanation of efficiency grade")


class CostEstimate(BaseModel):
    """Rough cost estimate for analysis."""

    relative_cost: float = Field(
        description="Relative cost index (1.0 = baseline)"
    )
    estimated_concrete: float = Field(description="Estimated concrete (m³/m)")
    estimated_steel: float = Field(description="Estimated steel (kg/m)")
    cost_rating: str = Field(
        description="Cost rating",
        examples=["economical", "moderate", "expensive"],
    )


class SmartAnalysisResponse(BaseModel):
    """Response model for smart analysis."""

    success: bool = Field(description="Whether analysis succeeded")
    message: str = Field(description="Summary message")

    # Design summary
    design_summary: dict = Field(description="Summary of design parameters and results")

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

    # Efficiency
    efficiency: EfficiencyMetrics | None = Field(
        default=None,
        description="Design efficiency metrics",
    )

    # Cost estimate
    cost_estimate: CostEstimate | None = Field(
        default=None,
        description="Rough cost estimate",
    )

    # Warnings
    warnings: list[str] = Field(default_factory=list, description="Analysis warnings")
