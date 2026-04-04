"""
Beam Design and Detailing Pydantic Models.

Models for beam design, checking, and detailing API endpoints.
All dimensions in mm, forces in kN, moments in kN·m, stresses in N/mm².
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

# =============================================================================
# Design Request Models
# =============================================================================


class RebarLayerConfig(BaseModel):
    """Configuration for a single rebar layer in multi-layer reinforcement."""

    layer: int = Field(ge=1, le=5, description="Layer number (1 = bottom)")
    bar_count: int = Field(ge=1, le=12, description="Number of bars")
    bar_dia_mm: float = Field(ge=8, le=36, description="Bar diameter (mm)")


class BeamDesignRequest(BaseModel):
    """Request model for beam design calculation."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "width": 300.0,
                    "depth": 500.0,
                    "moment": 150.0,
                    "shear": 75.0,
                    "fck": 25.0,
                    "fy": 415.0,
                    "clear_cover": 25.0,
                    "stirrup_dia_mm": 8.0,
                    "main_bar_dia_mm": 20.0,
                }
            ]
        }
    )

    # Section dimensions
    width: float = Field(
        gt=0,
        le=2000.0,
        description="Beam width b (mm)",
        examples=[230.0, 300.0, 400.0],
    )
    depth: float = Field(
        gt=0,
        le=3000.0,
        description="Overall beam depth D (mm)",
        examples=[450.0, 600.0, 750.0],
    )

    # Loading
    moment: float = Field(
        ge=0,
        description="Factored design moment Mu (kN·m)",
        examples=[100.0, 250.0, 500.0],
    )
    shear: float = Field(
        default=0.0,
        ge=0,
        description="Factored design shear force Vu (kN)",
        examples=[50.0, 150.0, 300.0],
    )

    # Material properties
    fck: float = Field(
        default=25.0,
        ge=15.0,
        le=80.0,
        description="Characteristic compressive strength of concrete (N/mm²)",
        examples=[20.0, 25.0, 30.0, 40.0],
    )
    fy: float = Field(
        default=500.0,
        ge=250.0,
        le=600.0,
        description="Yield strength of reinforcement steel (N/mm²)",
        examples=[415.0, 500.0, 550.0],
    )

    # Optional parameters
    clear_cover: float = Field(
        default=25.0,
        ge=20.0,
        le=75.0,
        description="Clear cover to reinforcement (mm)",
        examples=[25.0, 30.0, 40.0],
    )
    effective_depth: float | None = Field(
        default=None,
        gt=0,
        description="Effective depth d (mm). Auto-calculated if not provided.",
    )
    stirrup_dia_mm: float = Field(
        default=8.0,
        ge=6,
        le=16,
        description="Stirrup diameter (mm)",
    )
    main_bar_dia_mm: float = Field(
        default=20.0,
        ge=8,
        le=36,
        description="Main bar diameter (mm)",
    )

    # Serviceability (opt-in)
    include_serviceability: bool = Field(
        default=False,
        description="Include deflection and crack width checks",
    )
    span_mm: float | None = Field(
        default=None,
        ge=0,
        description="Beam span (mm) — required when include_serviceability=True",
    )
    support_condition: str = Field(
        default="SIMPLY_SUPPORTED",
        description="Support condition for deflection check",
    )

    # Multi-layer rebar config
    rebar_layers: list[RebarLayerConfig] | None = Field(
        default=None,
        description="Multi-layer rebar configuration",
    )

    @model_validator(mode="after")
    def validate_depth_ratio(self) -> "BeamDesignRequest":
        """Validate practical depth-to-width ratio."""
        if self.depth / self.width > 6:
            raise ValueError(
                f"Depth/width ratio {self.depth / self.width:.1f} exceeds practical limit of 6"
            )
        return self


class BeamCheckRequest(BaseModel):
    """Request model for checking existing beam with provided reinforcement."""

    # Section dimensions
    width: float = Field(gt=0, le=2000.0, description="Beam width b (mm)")
    depth: float = Field(gt=0, le=3000.0, description="Overall beam depth D (mm)")

    # Loading
    moment: float = Field(ge=0, description="Factored design moment Mu (kN·m)")
    shear: float = Field(default=0.0, ge=0, description="Factored shear Vu (kN)")

    # Provided reinforcement
    ast_provided: float = Field(
        gt=0,
        description="Provided tension reinforcement area Ast (mm²)",
        examples=[615.0, 942.0, 1256.0],
    )
    asc_provided: float = Field(
        default=0.0,
        ge=0,
        description="Provided compression reinforcement area Asc (mm²)",
    )
    stirrup_area: float = Field(
        default=0.0,
        ge=0,
        description="Two-legged stirrup area Asv (mm²)",
        examples=[100.5, 157.0, 201.0],
    )
    stirrup_spacing: float = Field(
        default=150.0,
        gt=0,
        le=300.0,
        description="Stirrup spacing sv (mm)",
    )

    # Material properties
    fck: float = Field(default=25.0, ge=15.0, le=80.0, description="fck (N/mm²)")
    fy: float = Field(default=500.0, ge=250.0, le=600.0, description="fy (N/mm²)")
    clear_cover: float = Field(default=25.0, ge=20.0, le=75.0, description="Cover (mm)")


# =============================================================================
# Detailing Request Models
# =============================================================================


class BeamDetailingRequest(BaseModel):
    """Request model for beam reinforcement detailing."""

    # Section dimensions
    width: float = Field(gt=0, le=2000.0, description="Beam width b (mm)")
    depth: float = Field(gt=0, le=3000.0, description="Overall beam depth D (mm)")

    # Required reinforcement (from design)
    ast_required: float = Field(
        gt=0,
        description="Required tension reinforcement area Ast (mm²)",
    )
    asc_required: float = Field(
        default=0.0,
        ge=0,
        description="Required compression reinforcement area Asc (mm²)",
    )
    asv_required: float = Field(
        default=0.0,
        ge=0,
        description="Required stirrup area Asv (mm²/mm)",
    )

    # Material properties
    fck: float = Field(default=25.0, ge=15.0, le=80.0, description="fck (N/mm²)")
    fy: float = Field(default=500.0, ge=250.0, le=600.0, description="fy (N/mm²)")
    clear_cover: float = Field(default=25.0, ge=20.0, le=75.0, description="Cover (mm)")

    # Detailing preferences
    preferred_bar_dia: list[int] | None = Field(
        default=None,
        description="Preferred bar diameters (mm)",
        examples=[[16, 20], [12, 16, 20, 25]],
    )
    max_layers: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Maximum number of reinforcement layers",
    )

    # Span information for development length
    span_length: float | None = Field(
        default=None,
        gt=0,
        description="Beam span length (mm) for development length calculation",
    )
    is_continuous: bool = Field(
        default=False,
        description="Whether beam is part of continuous system",
    )


# =============================================================================
# Response Models
# =============================================================================


class FlexureResult(BaseModel):
    """Flexure design result."""

    ast_required: float = Field(description="Required tension steel area (mm²)")
    ast_min: float = Field(description="Minimum required steel area (mm²)")
    ast_max: float = Field(description="Maximum allowed steel area (mm²)")
    xu: float = Field(description="Neutral axis depth (mm)")
    xu_max: float = Field(description="Limiting neutral axis depth (mm)")
    is_under_reinforced: bool = Field(description="Whether section is under-reinforced")
    moment_capacity: float = Field(description="Moment capacity Mu,cap (kN·m)")
    asc_required: float = Field(
        default=0.0, description="Compression steel if needed (mm²)"
    )


class ShearResult(BaseModel):
    """Shear design result."""

    tau_v: float = Field(description="Nominal shear stress (N/mm²)")
    tau_c: float = Field(description="Concrete shear strength (N/mm²)")
    tau_c_max: float = Field(description="Maximum shear stress limit (N/mm²)")
    asv_required: float = Field(description="Required stirrup area (mm²/mm)")
    stirrup_spacing: float = Field(description="Calculated stirrup spacing (mm)")
    sv_max: float = Field(description="Maximum allowed spacing (mm)")
    shear_capacity: float = Field(description="Shear capacity Vu,cap (kN)")


class DeflectionCheckResult(BaseModel):
    """Result of deflection span/depth check."""

    is_ok: bool
    span_depth_actual: float | None = None
    span_depth_allowable: float | None = None
    remarks: str = ""


class CrackWidthCheckResult(BaseModel):
    """Result of crack width check."""

    is_ok: bool
    crack_width_mm: float | None = None
    crack_width_limit_mm: float | None = None
    remarks: str = ""


class BeamDesignResponse(BaseModel):
    """Response model for beam design calculation."""

    # Status
    success: bool = Field(description="Whether design is valid")
    message: str = Field(description="Summary message")

    # Design results
    flexure: FlexureResult
    shear: ShearResult | None = Field(default=None)

    # Summary
    ast_total: float = Field(description="Total tension steel required (mm²)")
    asc_total: float = Field(default=0.0, description="Total compression steel (mm²)")
    utilization_ratio: float = Field(
        ge=0, le=2.0, description="Mu/Mu_cap utilization ratio"
    )
    effective_depth_used: float | None = Field(
        default=None,
        description="Actual effective depth used in calculation (mm)",
    )

    # Serviceability results (populated when include_serviceability=True)
    deflection_check: DeflectionCheckResult | None = None
    crack_width_check: CrackWidthCheckResult | None = None

    # Warnings
    warnings: list[str] = Field(default_factory=list, description="Design warnings")


class BeamCheckResponse(BaseModel):
    """Response model for beam adequacy check."""

    # Status
    is_adequate: bool = Field(description="Whether beam is adequate for loads")
    success: bool = Field(description="Whether calculation completed successfully")
    message: str = Field(description="Summary message")

    # Capacity check
    moment_capacity: float = Field(description="Moment capacity Mu,cap (kN·m)")
    shear_capacity: float = Field(description="Shear capacity Vu,cap (kN)")
    moment_utilization: float = Field(description="Mu/Mu,cap ratio")
    shear_utilization: float = Field(description="Vu/Vu,cap ratio")

    # Detailed check results
    flexure_adequate: bool = Field(description="Whether flexure is adequate")
    shear_adequate: bool = Field(description="Whether shear is adequate")

    # Warnings
    warnings: list[str] = Field(default_factory=list, description="Check warnings")


class BarArrangement(BaseModel):
    """Reinforcement bar arrangement."""

    layer: int = Field(description="Layer number (1 = bottom)")
    bar_count: int = Field(description="Number of bars in layer")
    bar_diameter: int = Field(description="Bar diameter (mm)")
    area_provided: float = Field(description="Total area provided (mm²)")
    spacing: float = Field(description="Clear spacing between bars (mm)")


class StirrupArrangement(BaseModel):
    """Stirrup arrangement."""

    diameter: int = Field(description="Stirrup diameter (mm)")
    legs: int = Field(description="Number of legs")
    spacing: float = Field(description="Spacing (mm)")
    area_per_meter: float = Field(description="Asv/sv provided (mm²/mm)")


class BeamDetailingResponse(BaseModel):
    """Response model for beam detailing."""

    success: bool = Field(description="Whether detailing is valid")
    message: str = Field(description="Summary message")

    # Tension reinforcement
    tension_bars: list[BarArrangement] = Field(
        description="Tension bar arrangement by layer"
    )
    ast_provided: float = Field(description="Total tension steel provided (mm²)")

    # Compression reinforcement
    compression_bars: list[BarArrangement] = Field(
        default_factory=list, description="Compression bar arrangement"
    )
    asc_provided: float = Field(
        default=0.0, description="Compression steel provided (mm²)"
    )

    # Shear reinforcement
    stirrups: StirrupArrangement | None = Field(
        default=None, description="Stirrup details"
    )

    # Development lengths
    ld_tension: float = Field(description="Development length for tension bars (mm)")
    ld_compression: float = Field(
        default=0.0, description="Development length for compression bars (mm)"
    )
    anchorage_length: float = Field(description="Anchorage length at supports (mm)")

    # Curtailment
    curtailment_points: list[dict[str, Any]] = Field(
        default_factory=list, description="Bar curtailment positions"
    )

    # Warnings
    warnings: list[str] = Field(default_factory=list, description="Detailing warnings")


# =============================================================================
# Torsion Models
# =============================================================================


class TorsionDesignRequest(BaseModel):
    """Request model for torsion design per IS 456 Cl 41."""

    # Section dimensions
    width: float = Field(
        gt=0,
        le=2000.0,
        description="Beam width b (mm)",
        examples=[230.0, 300.0, 400.0],
    )
    depth: float = Field(
        gt=0,
        le=3000.0,
        description="Overall beam depth D (mm)",
        examples=[450.0, 600.0, 750.0],
    )

    # Loading
    torsion: float = Field(
        gt=0,
        description="Factored torsional moment Tu (kN·m)",
        examples=[5.0, 15.0, 30.0],
    )
    moment: float = Field(
        ge=0,
        description="Factored bending moment Mu (kN·m)",
        examples=[100.0, 250.0],
    )
    shear: float = Field(
        default=0.0,
        ge=0,
        description="Factored shear force Vu (kN)",
        examples=[50.0, 150.0],
    )

    # Material properties
    fck: float = Field(
        default=25.0,
        ge=15.0,
        le=80.0,
        description="Characteristic compressive strength of concrete (N/mm²)",
    )
    fy: float = Field(
        default=500.0,
        ge=250.0,
        le=600.0,
        description="Yield strength of reinforcement steel (N/mm²)",
    )

    # Optional parameters
    clear_cover: float = Field(
        default=25.0,
        ge=20.0,
        le=75.0,
        description="Clear cover to reinforcement (mm)",
    )
    stirrup_dia: float = Field(
        default=8.0,
        ge=6.0,
        le=16.0,
        description="Stirrup diameter (mm)",
    )
    pt: float = Field(
        default=1.0,
        ge=0.1,
        le=4.0,
        description="Tension steel percentage (%)",
    )
    effective_depth: float | None = Field(
        default=None,
        gt=0,
        description="Effective depth d (mm). Auto-calculated if not provided.",
    )


class TorsionDesignResponse(BaseModel):
    """Response model for torsion design."""

    success: bool = Field(description="Whether design is safe")
    message: str = Field(description="Summary message")

    # Applied forces
    tu_knm: float = Field(description="Applied torsional moment (kN·m)")
    vu_kn: float = Field(description="Applied shear force (kN)")
    mu_knm: float = Field(description="Applied bending moment (kN·m)")

    # Equivalent forces (IS 456 Cl 41.3–41.4)
    ve_kn: float = Field(description="Equivalent shear Ve (kN)")
    me_knm: float = Field(description="Equivalent moment Me (kN·m)")

    # Stresses
    tv_equiv: float = Field(description="Equivalent shear stress τve (N/mm²)")
    tc: float = Field(description="Concrete shear strength τc (N/mm²)")
    tc_max: float = Field(description="Maximum shear stress limit τc,max (N/mm²)")

    # Reinforcement
    asv_torsion: float = Field(description="Stirrup area for torsion (mm²/mm)")
    asv_shear: float = Field(description="Stirrup area for shear (mm²/mm)")
    asv_total: float = Field(description="Total stirrup area (mm²/mm)")
    stirrup_spacing: float = Field(description="Designed stirrup spacing (mm)")
    al_torsion: float = Field(description="Longitudinal steel for torsion (mm²)")

    # Status
    is_safe: bool = Field(description="Section safe against combined loading")
    requires_closed_stirrups: bool = Field(
        default=True, description="Closed stirrups mandatory for torsion"
    )

    # Warnings
    warnings: list[str] = Field(default_factory=list, description="Design warnings")


# =============================================================================
# Enhanced Shear Models (IS 456 Cl 40.3)
# =============================================================================


class EnhancedShearRequest(BaseModel):
    """Request model for enhanced shear strength near supports (IS 456 Cl 40.3)."""

    fck: float = Field(
        ...,
        ge=15.0,
        le=80.0,
        description="Characteristic compressive strength of concrete (N/mm²)",
        examples=[20.0, 25.0, 30.0, 40.0],
    )
    pt_percent: float = Field(
        ...,
        ge=0.0,
        le=6.0,
        description="Tension steel percentage (%)",
        examples=[0.5, 1.0, 1.5],
    )
    d_mm: float = Field(
        ...,
        gt=0,
        le=3000.0,
        description="Effective depth (mm)",
        examples=[400.0, 450.0, 600.0],
    )
    av_mm: float = Field(
        ...,
        gt=0,
        le=10000.0,
        description="Distance from face of support to nearest edge of concentrated load (mm)",
        examples=[200.0, 300.0, 500.0],
    )


class EnhancedShearResponse(BaseModel):
    """Response model for enhanced shear strength calculation."""

    tau_c_enhanced: float = Field(description="Enhanced shear strength τc' (N/mm²)")
    tau_c_base: float = Field(description="Base shear strength τc (N/mm²)")
    enhancement_factor: float = Field(description="Enhancement factor 2d/av")
    tau_c_max: float = Field(description="Maximum shear stress τc,max (N/mm²)")
    is_capped: bool = Field(description="Whether τc' was capped at τc,max")
    clause: str = Field(default="IS 456 Cl 40.3", description="Governing clause")
