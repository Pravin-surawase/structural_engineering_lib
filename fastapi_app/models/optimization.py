"""Pydantic contracts for beam cost optimization endpoints."""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

# =============================================================================
# Request Models
# =============================================================================


class CostParameters(BaseModel):
    """Cost parameters for optimization."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    currency: str = Field(
        ...,
        min_length=3,
        max_length=3,
        pattern="^[A-Za-z]{3}$",
        description="Three-letter currency code for every supplied rate",
        examples=["INR"],
    )

    concrete_cost: float = Field(
        ...,
        gt=0,
        description="Cost of concrete per m³ in the supplied currency",
        examples=[5000.0, 6000.0, 8000.0],
    )
    steel_cost: float = Field(
        ...,
        gt=0,
        description="Cost of reinforcement steel per kg in the supplied currency",
        examples=[55.0, 60.0, 75.0],
    )
    formwork_cost: float = Field(
        ...,
        gt=0,
        description="Cost of formwork per m² in the supplied currency",
        examples=[350.0, 400.0, 500.0],
    )
    congestion_threshold_pt: float = Field(
        ...,
        gt=0,
        description="Longitudinal steel percentage above which congestion applies",
    )
    congestion_multiplier: float = Field(
        ...,
        ge=1,
        description="Steel-cost multiplier applied above the congestion threshold",
    )
    location_factor: float = Field(
        ...,
        gt=0,
        description="Explicit regional multiplier applied to the total cost",
    )


class DesignConstraints(BaseModel):
    """Design constraints for optimization."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    min_width: int = Field(
        ...,
        gt=0,
        description="Minimum beam width (mm)",
    )
    max_width: int = Field(
        ...,
        gt=0,
        description="Maximum beam width (mm)",
    )
    min_depth: int = Field(
        ...,
        gt=0,
        description="Minimum beam depth (mm)",
    )
    max_depth: int = Field(
        ...,
        gt=0,
        description="Maximum beam depth (mm)",
    )
    width_step: int = Field(
        ...,
        gt=0,
        description="Width increment step (mm)",
    )
    depth_step: int = Field(
        ...,
        gt=0,
        description="Depth increment step (mm)",
    )
    min_utilization: float = Field(
        ...,
        ge=0.5,
        le=1.0,
        description="Minimum utilization ratio for efficient design",
    )

    @model_validator(mode="after")
    def validate_bounds(self) -> Self:
        if self.min_width > self.max_width:
            raise ValueError("min_width must not exceed max_width")
        if self.min_depth > self.max_depth:
            raise ValueError("min_depth must not exceed max_depth")
        return self


class CostOptimizationRequest(BaseModel):
    """Request model for beam cost optimization."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    # Loading
    moment: float = Field(
        gt=0,
        description="Factored design moment Mu (kN·m)",
    )
    shear: float = Field(
        ...,
        ge=0,
        description="Factored design shear force Vu (kN)",
    )
    span_length: float = Field(
        gt=0,
        description="Beam span length (mm) for quantities and reported L/d ratio",
    )

    # Material properties
    fck: int = Field(
        ...,
        ge=15.0,
        le=40.0,
        description="Concrete grade used for every candidate (N/mm²)",
    )
    fy: int = Field(
        ...,
        ge=250.0,
        le=550.0,
        description="Reinforcement grade used for every candidate (N/mm²)",
    )

    # Effective-depth and shear-design basis (all explicit project inputs)
    clear_cover: float = Field(
        ...,
        gt=0,
        description="Clear cover to the outside of the stirrup (mm)",
    )
    main_bar_diameter: float = Field(
        ...,
        gt=0,
        description="Candidate longitudinal-bar diameter used to establish d (mm)",
    )
    stirrup_diameter: float = Field(
        ...,
        gt=0,
        description="Stirrup bar diameter used to establish d and Asv (mm)",
    )
    stirrup_legs: int = Field(
        ...,
        ge=2,
        description="Number of effective vertical stirrup legs",
    )

    # Cost parameters
    cost_params: CostParameters = Field(
        ...,
        description="Unit cost parameters",
    )

    # Constraints
    constraints: DesignConstraints = Field(
        ...,
        description="Design constraints for optimization",
    )

    # Optimization settings
    optimize_for: Literal["cost"] = Field(
        default="cost",
        description="This endpoint supports the cost objective only",
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

    @model_validator(mode="after")
    def validate_effective_depth_basis(self) -> Self:
        deduction = (
            self.clear_cover + self.stirrup_diameter + 0.5 * self.main_bar_diameter
        )
        if deduction >= self.constraints.min_depth:
            raise ValueError(
                "clear cover plus bar-size deduction must be less than min_depth"
            )
        return self


# =============================================================================
# Response Models
# =============================================================================


class CostBreakdown(BaseModel):
    """Detailed cost breakdown."""

    concrete_cost: float = Field(description="Cost of concrete")
    steel_cost: float = Field(description="Cost of longitudinal reinforcement")
    formwork_cost: float = Field(description="Cost of formwork")
    labor_adjustment: float = Field(description="Explicit congestion adjustment")
    location_factor: float = Field(description="Regional multiplier applied to total")
    total_cost: float = Field(description="Total cost")
    cost_per_meter: float = Field(description="Cost per meter length")
    currency: str = Field(description="Three-letter currency code")


class OptimalDesign(BaseModel):
    """Single optimal design solution."""

    width: float = Field(description="Beam width (mm)")
    depth: float = Field(description="Beam depth (mm)")
    effective_depth: float = Field(description="Effective depth d (mm)")
    effective_depth_deduction: float = Field(
        description="Total deduction D-d used by the calculation (mm)"
    )
    clear_cover: float = Field(description="Clear cover basis (mm)")
    main_bar_diameter: float = Field(description="Longitudinal-bar diameter basis (mm)")
    stirrup_diameter: float = Field(description="Stirrup diameter basis (mm)")
    stirrup_legs: int = Field(description="Effective vertical stirrup legs")
    fck: float = Field(description="Concrete grade (N/mm²)")
    fy: float = Field(description="Reinforcement grade (N/mm²)")
    ast_required: float = Field(description="Tension steel required (mm²)")
    asc_required: float = Field(default=0.0, description="Compression steel (mm²)")
    utilization: float = Field(description="Moment utilization ratio")
    shear_utilization: float = Field(
        description="Nominal-to-maximum shear stress ratio"
    )
    stirrup_utilization: float = Field(
        description="Required-to-provided stirrup shear capacity ratio"
    )
    shear_stress: float = Field(description="Nominal shear stress tau_v (N/mm²)")
    concrete_shear_strength: float = Field(
        description="Concrete design shear strength tau_c (N/mm²)"
    )
    maximum_shear_stress: float = Field(
        description="Maximum design shear stress tau_c,max (N/mm²)"
    )
    stirrup_spacing: float = Field(description="Designed stirrup spacing (mm)")
    shear_reinforcement_area: float = Field(
        description="Area of effective stirrup legs Asv (mm²)"
    )
    ld_ratio: float = Field(description="Span/depth ratio")

    # Quantities
    concrete_volume: float = Field(description="Concrete volume (m³/m)")
    steel_weight: float = Field(
        description="Required longitudinal steel weight (kg/m); stirrups excluded"
    )
    steel_weight_total: float = Field(
        description="Required longitudinal steel over the supplied span (kg)"
    )
    formwork_area: float = Field(description="Formwork area (m²/m)")

    # Cost
    cost_breakdown: CostBreakdown

    # Ranking
    rank: int = Field(description="Solution rank (1 = best)")
    score: float = Field(description="Optimization score (lower is better)")
    is_safe: bool = Field(description="Flexure and maintained shear checks pass")
    code_edition: str = Field(description="Structural design-code edition")
    clause_refs: dict[str, str] = Field(
        description="Maintained flexure and shear source references"
    )
    quantity_basis: str = Field(description="Boundary of the reported steel quantity")


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
    savings_vs_baseline: float = Field(
        default=0.0,
        description="Cost savings vs the conventional valid baseline candidate (%)",
    )

    # Warnings
    warnings: list[str] = Field(
        default_factory=list, description="Optimization warnings"
    )


# =============================================================================
# Pareto Optimization Models
# =============================================================================


class ParetoCandidateResponse(BaseModel):
    """A single Pareto-optimal beam design candidate."""

    b_mm: int = Field(description="Beam width (mm)")
    D_mm: int = Field(description="Beam total depth (mm)")
    d_mm: int = Field(description="Effective depth (mm)")
    fck_nmm2: int = Field(description="Concrete grade (N/mm²)")
    fy_nmm2: int = Field(description="Steel grade (N/mm²)")
    ast_required: float = Field(description="Required steel area (mm²)")
    ast_provided: float = Field(description="Provided steel area (mm²)")
    bar_config: str = Field(description="Bar configuration (e.g. '4-16mm')")
    cost: float = Field(description="Total cost (INR)")
    steel_weight_kg: float = Field(description="Steel weight (kg)")
    utilization: float = Field(description="Capacity utilization ratio (0-1)")
    is_safe: bool = Field(description="Meets IS 456 requirements")
    governing_clauses: list[str] = Field(
        default_factory=list, description="Governing IS 456 clauses"
    )
    rank: int = Field(description="Pareto rank (1 = best front)")
    crowding_distance: float = Field(description="NSGA-II crowding distance")


class ParetoRequest(BaseModel):
    """Request model for Pareto multi-objective beam optimization."""

    span_mm: float = Field(
        ...,
        gt=0,
        le=30000,
        description="Beam span (mm)",
        examples=[5000.0, 6000.0],
    )
    mu_knm: float = Field(
        ...,
        gt=0,
        description="Factored bending moment (kN·m)",
        examples=[120.0, 200.0],
    )
    vu_kn: float = Field(
        ...,
        ge=0,
        description="Factored shear force (kN)",
        examples=[80.0, 100.0],
    )
    objectives: list[str] | None = Field(
        default=None,
        description="Objectives to optimize: 'cost', 'steel_weight', 'utilization'. Default: ['cost', 'utilization']",
        examples=[["cost", "utilization"]],
    )
    cover_mm: int = Field(
        default=40,
        ge=20,
        le=75,
        description="Concrete cover (mm)",
    )
    max_candidates: int = Field(
        default=50,
        ge=5,
        le=200,
        description="Maximum number of candidates to generate",
    )


class ParetoResponse(BaseModel):
    """Response model for Pareto multi-objective optimization."""

    pareto_front: list[ParetoCandidateResponse] = Field(
        description="Pareto-optimal designs (rank 1)"
    )
    pareto_count: int = Field(description="Number of Pareto-optimal designs")
    total_candidates: int = Field(description="Total valid candidates evaluated")
    objectives_used: list[str] = Field(description="Objectives optimized")
    computation_time_sec: float = Field(description="Computation time (seconds)")
    best_by_cost: ParetoCandidateResponse | None = Field(
        default=None, description="Cheapest design"
    )
    best_by_utilization: ParetoCandidateResponse | None = Field(
        default=None, description="Most efficient design"
    )
    best_by_weight: ParetoCandidateResponse | None = Field(
        default=None, description="Lightest design"
    )
