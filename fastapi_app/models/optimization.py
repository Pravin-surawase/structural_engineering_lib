"""
Cost Optimization Pydantic Models.

Models for beam cost optimization API endpoints.
"""

from pydantic import BaseModel, Field

# =============================================================================
# Request Models
# =============================================================================


class CostParameters(BaseModel):
    """Cost parameters for optimization."""

    concrete_cost: float = Field(
        default=6000.0,
        gt=0,
        description="Cost of concrete per m³ (₹/m³)",
        examples=[5000.0, 6000.0, 8000.0],
    )
    steel_cost: float = Field(
        default=60.0,
        gt=0,
        description="Cost of reinforcement steel per kg (₹/kg)",
        examples=[55.0, 60.0, 75.0],
    )
    formwork_cost: float = Field(
        default=400.0,
        gt=0,
        description="Cost of formwork per m² (₹/m²)",
        examples=[350.0, 400.0, 500.0],
    )


class DesignConstraints(BaseModel):
    """Design constraints for optimization."""

    min_width: float = Field(
        default=200.0,
        gt=0,
        description="Minimum beam width (mm)",
    )
    max_width: float = Field(
        default=600.0,
        gt=0,
        description="Maximum beam width (mm)",
    )
    min_depth: float = Field(
        default=300.0,
        gt=0,
        description="Minimum beam depth (mm)",
    )
    max_depth: float = Field(
        default=1200.0,
        gt=0,
        description="Maximum beam depth (mm)",
    )
    width_step: float = Field(
        default=50.0,
        gt=0,
        description="Width increment step (mm)",
    )
    depth_step: float = Field(
        default=50.0,
        gt=0,
        description="Depth increment step (mm)",
    )
    min_utilization: float = Field(
        default=0.7,
        ge=0.5,
        le=1.0,
        description="Minimum utilization ratio for efficient design",
    )


class CostOptimizationRequest(BaseModel):
    """Request model for beam cost optimization."""

    # Loading
    moment: float = Field(
        ge=0,
        description="Factored design moment Mu (kN·m)",
    )
    shear: float = Field(
        default=0.0,
        ge=0,
        description="Factored design shear force Vu (kN)",
    )
    span_length: float = Field(
        gt=0,
        description="Beam span length (mm) for L/d ratio checks",
    )

    # Material properties
    fck: float = Field(
        default=25.0,
        ge=15.0,
        le=80.0,
        description="fck (N/mm²)",
    )
    fy: float = Field(
        default=500.0,
        ge=250.0,
        le=600.0,
        description="fy (N/mm²)",
    )

    # Cost parameters
    cost_params: CostParameters = Field(
        default_factory=CostParameters,
        description="Unit cost parameters",
    )

    # Constraints
    constraints: DesignConstraints = Field(
        default_factory=DesignConstraints,
        description="Design constraints for optimization",
    )

    # Optimization settings
    optimize_for: str = Field(
        default="cost",
        description="Optimization objective",
        pattern="^(cost|weight|depth)$",
    )
    include_alternatives: bool = Field(
        default=True,
        description="Whether to include alternative solutions",
    )
    max_alternatives: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of alternative solutions",
    )


# =============================================================================
# Response Models
# =============================================================================


class CostBreakdown(BaseModel):
    """Detailed cost breakdown."""

    concrete_cost: float = Field(description="Cost of concrete (₹)")
    steel_cost: float = Field(description="Cost of reinforcement (₹)")
    formwork_cost: float = Field(description="Cost of formwork (₹)")
    total_cost: float = Field(description="Total cost (₹)")
    cost_per_meter: float = Field(description="Cost per meter length (₹/m)")


class OptimalDesign(BaseModel):
    """Single optimal design solution."""

    width: float = Field(description="Beam width (mm)")
    depth: float = Field(description="Beam depth (mm)")
    ast_required: float = Field(description="Tension steel required (mm²)")
    asc_required: float = Field(default=0.0, description="Compression steel (mm²)")
    utilization: float = Field(description="Moment utilization ratio")
    ld_ratio: float = Field(description="Span/depth ratio")

    # Quantities
    concrete_volume: float = Field(description="Concrete volume (m³/m)")
    steel_weight: float = Field(description="Steel weight (kg/m)")
    formwork_area: float = Field(description="Formwork area (m²/m)")

    # Cost
    cost_breakdown: CostBreakdown

    # Ranking
    rank: int = Field(description="Solution rank (1 = best)")
    score: float = Field(description="Optimization score (lower is better)")


class CostOptimizationResponse(BaseModel):
    """Response model for cost optimization."""

    success: bool = Field(description="Whether optimization succeeded")
    message: str = Field(description="Summary message")

    # Best solution
    optimal: OptimalDesign = Field(description="Optimal design solution")

    # Alternatives
    alternatives: list[OptimalDesign] = Field(
        default_factory=list,
        description="Alternative design solutions",
    )

    # Statistics
    total_combinations_evaluated: int = Field(
        description="Number of combinations evaluated"
    )
    valid_solutions_found: int = Field(description="Number of valid solutions found")

    # Savings comparison
    savings_vs_min_section: float = Field(
        default=0.0,
        description="Cost savings vs minimum section size (%)",
    )

    # Warnings
    warnings: list[str] = Field(
        default_factory=list, description="Optimization warnings"
    )
