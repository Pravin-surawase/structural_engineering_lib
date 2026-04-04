"""
Column Design Pydantic Models.

Models for column classification, eccentricity, and axial design endpoints.
All dimensions in mm, forces in kN, stresses in N/mm².
"""

from typing import Literal

from pydantic import BaseModel, Field

# =============================================================================
# Request Models
# =============================================================================


class EffectiveLengthRequest(BaseModel):
    """Request model for effective length calculation per IS 456 Cl 25.2, Table 28."""

    l_mm: float = Field(
        ...,
        gt=0,
        le=50000,
        description="Unsupported length of column (mm)",
        examples=[3000.0, 4500.0, 6000.0],
    )
    end_condition: str = Field(
        ...,
        description=(
            "IS 456 Table 28 end condition. One of: "
            "FIXED_FIXED, FIXED_HINGED, FIXED_FIXED_SWAY, FIXED_FREE, "
            "HINGED_HINGED, FIXED_PARTIAL, HINGED_PARTIAL"
        ),
        examples=["FIXED_FIXED", "FIXED_HINGED", "HINGED_HINGED"],
    )
    use_theoretical: bool = Field(
        False,
        description=(
            "Use theoretical (Euler) values instead of recommended. "
            "Cases 6 and 7 have no theoretical values; recommended is used."
        ),
    )


class EffectiveLengthResponse(BaseModel):
    """Response model for effective length calculation."""

    le_mm: float = Field(
        description="Effective length of column (mm)",
        examples=[1950.0, 3000.0],
    )
    ratio: float = Field(
        description="Effective length ratio le/l",
        examples=[0.65, 1.0],
    )
    end_condition: str = Field(
        description="End condition used",
        examples=["FIXED_FIXED", "HINGED_HINGED"],
    )
    method: Literal["recommended", "theoretical"] = Field(
        description="Method used: 'recommended' or 'theoretical'",
        examples=["recommended", "theoretical"],
    )


class ColumnClassifyRequest(BaseModel):
    """Request model for column classification (short vs slender)."""

    le_mm: float = Field(
        ...,
        gt=0,
        le=50000,
        description="Effective length of column (mm)",
        examples=[3000.0, 4500.0, 6000.0],
    )
    D_mm: float = Field(
        ...,
        gt=0,
        le=3000,
        description="Least lateral dimension of column (mm)",
        examples=[300.0, 400.0, 500.0],
    )


class ColumnEccentricityRequest(BaseModel):
    """Request model for minimum eccentricity calculation."""

    l_unsupported_mm: float = Field(
        ...,
        gt=0,
        le=50000,
        description="Unsupported length of column (mm)",
        examples=[3000.0, 4500.0, 6000.0],
    )
    D_mm: float = Field(
        ...,
        gt=0,
        le=3000,
        description="Lateral dimension of column in the direction considered (mm)",
        examples=[300.0, 400.0, 500.0],
    )


class ColumnAxialRequest(BaseModel):
    """Request model for short column axial capacity calculation."""

    fck: float = Field(
        ...,
        ge=15,
        le=80,
        description="Characteristic compressive strength of concrete (N/mm²)",
        examples=[20.0, 25.0, 30.0, 40.0],
    )
    fy: float = Field(
        ...,
        ge=250,
        le=600,
        description="Yield strength of reinforcement steel (N/mm²)",
        examples=[415.0, 500.0, 550.0],
    )
    Ag_mm2: float = Field(
        ...,
        gt=0,
        le=9000000,
        description="Gross cross-sectional area of column (mm²)",
        examples=[90000.0, 120000.0, 160000.0],
    )
    Asc_mm2: float = Field(
        ...,
        ge=0,
        description="Area of longitudinal reinforcement (mm²)",
        examples=[1256.64, 1800.0, 2513.27],
    )


# =============================================================================
# Response Models
# =============================================================================


class ColumnClassifyResponse(BaseModel):
    """Response model for column classification."""

    classification: str = Field(
        description="Column classification: 'SHORT' or 'SLENDER'",
        examples=["SHORT", "SLENDER"],
    )
    slenderness_ratio: float = Field(
        description="Slenderness ratio le/D",
        examples=[10.0, 16.0],
    )


class ColumnEccentricityResponse(BaseModel):
    """Response model for minimum eccentricity."""

    e_min_mm: float = Field(
        description="Minimum eccentricity per IS 456 Cl. 25.4 (mm)",
        examples=[20.0, 25.0],
    )


class ColumnAxialResponse(BaseModel):
    """Response model for short column axial capacity."""

    Pu_kN: float = Field(
        description="Ultimate axial load capacity (kN)",
    )
    fck: float = Field(
        description="Concrete strength used (N/mm²)",
    )
    fy: float = Field(
        description="Steel yield strength used (N/mm²)",
    )
    Ag_mm2: float = Field(
        description="Gross cross-sectional area (mm²)",
    )
    Asc_mm2: float = Field(
        description="Area of longitudinal steel (mm²)",
    )
    Ac_mm2: float = Field(
        description="Net concrete area Ag - Asc (mm²)",
    )
    steel_ratio: float = Field(
        description="Reinforcement ratio Asc/Ag",
    )
    is_safe: bool = Field(
        description="Whether steel ratio is within IS 456 limits (0.8%–6%)",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Design warnings (e.g., steel ratio out of code limits)",
    )


# =============================================================================
# Uniaxial Bending Models
# =============================================================================


class ColumnUniaxialRequest(BaseModel):
    """Request model for short column uniaxial bending design per IS 456 Cl 39.5."""

    Pu_kN: float = Field(
        ...,
        ge=0,
        description="Factored axial load (kN)",
        examples=[1200.0, 800.0, 0.0],
    )
    Mu_kNm: float = Field(
        ...,
        ge=0,
        description="Factored uniaxial moment (kNm)",
        examples=[150.0, 100.0, 50.0],
    )
    b_mm: float = Field(
        ...,
        ge=100,
        le=2000,
        description="Column width perpendicular to bending axis (mm)",
        examples=[300.0, 400.0, 500.0],
    )
    D_mm: float = Field(
        ...,
        ge=100,
        le=2000,
        description="Column depth in direction of bending (mm)",
        examples=[300.0, 450.0, 600.0],
    )
    le_mm: float = Field(
        ...,
        gt=0,
        le=50000,
        description="Effective length of column (mm)",
        examples=[3000.0, 4500.0, 6000.0],
    )
    fck: float = Field(
        ...,
        ge=15,
        le=80,
        description="Characteristic concrete strength (N/mm²)",
        examples=[20.0, 25.0, 30.0],
    )
    fy: float = Field(
        ...,
        ge=250,
        le=550,
        description="Steel yield strength (N/mm²)",
        examples=[415.0, 500.0],
    )
    Asc_mm2: float = Field(
        ...,
        gt=0,
        description="Total longitudinal reinforcement area, symmetrically placed (mm²)",
        examples=[2700.0, 1800.0, 3600.0],
    )
    d_prime_mm: float = Field(
        ...,
        gt=0,
        le=500,
        description="Cover to centroid of reinforcement from nearest face (mm). Must be less than D/2.",
        examples=[40.0, 50.0, 60.0],
    )
    l_unsupported_mm: float | None = Field(
        None,
        gt=0,
        le=50000,
        description="Unsupported length for min eccentricity per Cl 25.4 (mm). "
        "If omitted, minimum eccentricity check is skipped.",
        examples=[3000.0, 4500.0],
    )


class ColumnUniaxialResponse(BaseModel):
    """Response model for short column uniaxial bending design."""

    ok: bool = Field(
        description="True if (Pu, Mu) is within the P-M interaction capacity envelope",
    )
    utilization: float = Field(
        description="Radial utilization ratio (applied / capacity). < 1.0 means safe.",
        examples=[0.72, 0.95, 1.15],
    )
    Pu_cap_kN: float = Field(
        description="Capacity axial load at the same Pu/Mu slope (kN)",
    )
    Mu_cap_kNm: float = Field(
        description="Capacity moment at the same Pu/Mu slope (kNm)",
    )
    classification: str = Field(
        description="Column classification: 'SHORT' or 'SLENDER'",
        examples=["SHORT", "SLENDER"],
    )
    eccentricity_mm: float = Field(
        description="Actual eccentricity e = M/P (mm)",
    )
    e_min_mm: float | None = Field(
        None,
        description="Minimum eccentricity per IS 456 Cl 25.4 (mm), if l_unsupported_mm was provided",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Code compliance warnings",
    )


# =============================================================================
# P-M Interaction Curve Models
# =============================================================================


class PMInteractionRequest(BaseModel):
    """Request model for P-M interaction curve generation."""

    b_mm: float = Field(
        ...,
        gt=0,
        le=3000,
        description="Column width perpendicular to bending axis (mm)",
        examples=[300.0, 400.0],
    )
    D_mm: float = Field(
        ...,
        gt=0,
        le=3000,
        description="Column depth in bending direction (mm)",
        examples=[400.0, 500.0, 600.0],
    )
    fck: float = Field(
        ...,
        ge=15,
        le=80,
        description="Characteristic compressive strength of concrete (N/mm²)",
        examples=[25.0, 30.0, 40.0],
    )
    fy: float = Field(
        ...,
        ge=250,
        le=550,
        description="Characteristic yield strength of steel (N/mm²)",
        examples=[415.0, 500.0],
    )
    Asc_mm2: float = Field(
        ...,
        gt=0,
        le=100000,
        description="Total area of longitudinal reinforcement (mm²)",
        examples=[2400.0, 3000.0, 4800.0],
    )
    d_prime_mm: float = Field(
        ...,
        gt=0,
        le=200,
        description="Cover to centroid of reinforcement from nearest face (mm)",
        examples=[40.0, 50.0, 60.0],
    )
    n_points: int = Field(
        default=50,
        ge=10,
        le=500,
        description="Number of points on the interaction curve (default 50, min 10)",
        examples=[50, 100],
    )


class PMPoint(BaseModel):
    """A single point on the P-M interaction curve."""

    Pu_kN: float = Field(..., description="Axial force (kN)")
    Mu_kNm: float = Field(..., description="Moment (kN·m)")


class PMInteractionResponse(BaseModel):
    """Response model for P-M interaction curve."""

    points: list[PMPoint] = Field(
        ..., description="Points on the P-M interaction curve"
    )
    Pu_0_kN: float = Field(..., description="Pure axial capacity (kN)")
    Mu_0_kNm: float = Field(..., description="Pure bending capacity (kN·m)")
    Pu_bal_kN: float = Field(..., description="Balanced point axial load (kN)")
    Mu_bal_kNm: float = Field(..., description="Balanced point moment capacity (kN·m)")
    fck: float = Field(..., description="Concrete strength used (N/mm²)")
    fy: float = Field(..., description="Steel yield strength used (N/mm²)")
    b_mm: float = Field(..., description="Column width (mm)")
    D_mm: float = Field(..., description="Column depth (mm)")
    Asc_mm2: float = Field(..., description="Total steel area (mm²)")
    d_prime_mm: float = Field(..., description="Cover to steel centroid (mm)")
    clause_ref: str = Field(default="Cl. 39.5", description="IS 456 clause reference")
    warnings: list[str] = Field(default_factory=list, description="Design warnings")


# =============================================================================
# Biaxial Bending Check Models (IS 456 Cl. 39.6)
# =============================================================================


class BiaxialCheckRequest(BaseModel):
    """Request model for biaxial bending check per IS 456 Cl 39.6 (Bresler load contour)."""

    Pu_kN: float = Field(
        ...,
        ge=0,
        description="Factored axial load (kN)",
        examples=[1500.0, 800.0, 2000.0],
    )
    Mux_kNm: float = Field(
        ...,
        ge=0,
        description="Factored moment about x-axis (kNm)",
        examples=[120.0, 80.0, 200.0],
    )
    Muy_kNm: float = Field(
        ...,
        ge=0,
        description="Factored moment about y-axis (kNm)",
        examples=[80.0, 60.0, 150.0],
    )
    b_mm: float = Field(
        ...,
        ge=100,
        le=3000,
        description="Column width in mm",
        examples=[300.0, 400.0, 500.0],
    )
    D_mm: float = Field(
        ...,
        ge=100,
        le=3000,
        description="Column depth in mm",
        examples=[400.0, 500.0, 600.0],
    )
    le_mm: float = Field(
        ...,
        gt=0,
        le=50000,
        description="Effective length in mm",
        examples=[3000.0, 4500.0, 6000.0],
    )
    fck: float = Field(
        ...,
        ge=15,
        le=80,
        description="Concrete grade in N/mm²",
        examples=[20.0, 25.0, 30.0],
    )
    fy: float = Field(
        ...,
        ge=250,
        le=600,
        description="Steel yield strength in N/mm²",
        examples=[415.0, 500.0],
    )
    Asc_mm2: float = Field(
        ...,
        gt=0,
        le=100000,
        description="Total steel area in mm²",
        examples=[2400.0, 3600.0, 4800.0],
    )
    d_prime_mm: float = Field(
        ...,
        gt=0,
        le=500,
        description="Cover to steel centroid in mm",
        examples=[40.0, 50.0, 60.0],
    )
    l_unsupported_mm: float | None = Field(
        None,
        gt=0,
        le=50000,
        description="Unsupported length in mm (optional, for min eccentricity check)",
        examples=[3000.0, 4500.0],
    )


class BiaxialCheckResponse(BaseModel):
    """Response model for biaxial bending check per IS 456 Cl 39.6."""

    Pu_kN: float = Field(description="Applied axial load (kN)")
    Mux_kNm: float = Field(description="Applied moment about x-axis (kNm)")
    Muy_kNm: float = Field(description="Applied moment about y-axis (kNm)")
    Mux1_kNm: float = Field(
        description="Uniaxial moment capacity about x-axis when Pu acts alone (kNm)"
    )
    Muy1_kNm: float = Field(
        description="Uniaxial moment capacity about y-axis when Pu acts alone (kNm)"
    )
    Puz_kN: float = Field(description="Pure axial capacity Puz per Cl 39.6 (kN)")
    alpha_n: float = Field(
        description="Bresler exponent alpha_n interpolated from Pu/Puz"
    )
    interaction_ratio: float = Field(
        description="Bresler interaction ratio (Mux/Mux1)^an + (Muy/Muy1)^an. "
        "< 1.0 means safe."
    )
    is_safe: bool = Field(description="True if interaction_ratio <= 1.0")
    classification: int = Field(
        description="Column classification: 1 = SHORT, 2 = SLENDER"
    )
    clause_ref: str = Field(default="Cl. 39.6", description="IS 456 clause reference")
    warnings: list[str] = Field(
        default_factory=list, description="Code compliance warnings"
    )


# =============================================================================
# Additional Moment Models (IS 456 Cl. 39.7.1)
# =============================================================================


class AdditionalMomentRequest(BaseModel):
    """Request for additional moment calculation per IS 456 Cl 39.7.1."""

    Pu_kN: float = Field(
        ..., ge=0, description="Factored axial load (kN)", examples=[1500.0]
    )
    b_mm: float = Field(
        ...,
        ge=100,
        le=3000,
        description="Column width (mm)",
        examples=[300.0],
    )
    D_mm: float = Field(
        ...,
        ge=100,
        le=3000,
        description="Column depth (mm)",
        examples=[450.0],
    )
    lex_mm: float = Field(
        ...,
        gt=0,
        le=50000,
        description="Effective length about x-axis (mm)",
        examples=[6000.0],
    )
    ley_mm: float = Field(
        ...,
        gt=0,
        le=50000,
        description="Effective length about y-axis (mm)",
        examples=[4500.0],
    )
    fck: float = Field(
        ...,
        gt=0,
        le=100,
        description="Concrete strength (N/mm²)",
        examples=[25.0],
    )
    fy: float = Field(
        ...,
        gt=0,
        le=600,
        description="Steel yield strength (N/mm²)",
        examples=[415.0],
    )
    Asc_mm2: float = Field(
        ..., ge=0, description="Total steel area (mm²)", examples=[2400.0]
    )
    d_prime_mm: float = Field(
        ...,
        ge=0,
        le=200,
        description="Cover to steel centroid (mm)",
        examples=[50.0],
    )


class AdditionalMomentResponse(BaseModel):
    """Response for additional moment per IS 456 Cl 39.7.1."""

    eadd_x_mm: float = Field(description="Additional eccentricity about x-axis (mm)")
    Max_kNm: float = Field(description="Additional moment about x-axis (kN·m)")
    slenderness_ratio_x: float = Field(description="le_x / D")
    is_slender_x: bool = Field(description="True if le_x/D >= 12")

    eadd_y_mm: float = Field(description="Additional eccentricity about y-axis (mm)")
    May_kNm: float = Field(description="Additional moment about y-axis (kN·m)")
    slenderness_ratio_y: float = Field(description="le_y / b")
    is_slender_y: bool = Field(description="True if le_y/b >= 12")

    k: float = Field(description="Reduction factor per Cl 39.7.1.1")
    Max_reduced_kNm: float = Field(
        description="Reduced additional moment x-axis (kN·m)"
    )
    May_reduced_kNm: float = Field(
        description="Reduced additional moment y-axis (kN·m)"
    )
    Puz_kN: float = Field(description="Pure axial crush capacity (kN)")
    Pb_kN: float = Field(description="Balanced failure load (kN)")

    Pu_kN: float = Field(description="Applied axial load (kN)")
    b_mm: float = Field(description="Column width (mm)")
    D_mm: float = Field(description="Column depth (mm)")
    lex_mm: float = Field(description="Effective length x-axis (mm)")
    ley_mm: float = Field(description="Effective length y-axis (mm)")

    clause_ref: str = Field(default="Cl. 39.7.1", description="IS 456 clause reference")
    warnings: list[str] = Field(default_factory=list, description="Design warnings")


# =============================================================================
# Long Column Design (Cl 39.7)
# =============================================================================


class LongColumnRequest(BaseModel):
    """Request for long (slender) column design per IS 456 Cl 39.7."""

    Pu_kN: float = Field(
        ..., ge=0, description="Factored axial load (kN)", examples=[1500.0]
    )
    M1x_kNm: float = Field(
        0.0, description="Smaller end moment about x (kNm)", examples=[30.0]
    )
    M2x_kNm: float = Field(
        0.0, description="Larger end moment about x (kNm)", examples=[80.0]
    )
    M1y_kNm: float = Field(
        0.0, description="Smaller end moment about y (kNm)", examples=[20.0]
    )
    M2y_kNm: float = Field(
        0.0, description="Larger end moment about y (kNm)", examples=[60.0]
    )
    b_mm: float = Field(
        ..., gt=0, le=2000, description="Column width (mm)", examples=[300.0]
    )
    D_mm: float = Field(
        ..., gt=0, le=2000, description="Column depth (mm)", examples=[450.0]
    )
    lex_mm: float = Field(
        ...,
        gt=0,
        le=100000,
        description="Effective length about x (mm)",
        examples=[6000.0],
    )
    ley_mm: float = Field(
        ...,
        gt=0,
        le=100000,
        description="Effective length about y (mm)",
        examples=[4500.0],
    )
    fck: float = Field(
        ..., gt=0, le=100, description="Concrete strength (N/mm²)", examples=[25.0]
    )
    fy: float = Field(
        ..., gt=0, le=600, description="Steel yield strength (N/mm²)", examples=[415.0]
    )
    Asc_mm2: float = Field(
        ..., gt=0, description="Total steel area (mm²)", examples=[2400.0]
    )
    d_prime_mm: float = Field(
        ..., gt=0, description="Cover to steel centroid (mm)", examples=[50.0]
    )
    braced: bool = Field(True, description="True if column is braced against sway")


class LongColumnResponse(BaseModel):
    """Response for long column design."""

    Pu_kN: float
    Mux_design_kNm: float
    Muy_design_kNm: float
    is_safe: bool
    classification_x: str
    classification_y: str
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
    warnings: list[str] = []


# =============================================================================
# Helical Reinforcement (Cl 39.4)
# =============================================================================


class HelicalCheckRequest(BaseModel):
    """Request for helical reinforcement check per IS 456 Cl 39.4."""

    D_mm: float = Field(
        ..., gt=0, description="Column outer diameter (mm)", examples=[450.0]
    )
    D_core_mm: float = Field(
        ..., gt=0, description="Core diameter inside helix (mm)", examples=[350.0]
    )
    fck: float = Field(
        ..., gt=0, le=100, description="Concrete strength (N/mm²)", examples=[25.0]
    )
    fy: float = Field(
        ..., gt=0, le=600, description="Steel yield strength (N/mm²)", examples=[415.0]
    )
    d_helix_mm: float = Field(
        ..., gt=0, description="Helix bar diameter (mm)", examples=[8.0]
    )
    pitch_mm: float = Field(..., gt=0, description="Helix pitch (mm)", examples=[50.0])
    Pu_axial_kN: float = Field(
        ..., gt=0, description="Short column axial capacity (kN)", examples=[2000.0]
    )


class HelicalCheckResponse(BaseModel):
    """Response for helical reinforcement check."""

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
    warnings: list[str] = []


# =============================================================================
# Column Design Orchestrator
# =============================================================================


class ColumnDesignRequest(BaseModel):
    """Request for unified column design per IS 456."""

    Pu_kN: float = Field(
        ..., ge=0, description="Factored axial load (kN)", examples=[1500.0]
    )
    Mux_kNm: float = Field(
        0.0, ge=0, description="Applied moment about x (kNm)", examples=[120.0]
    )
    Muy_kNm: float = Field(
        0.0, ge=0, description="Applied moment about y (kNm)", examples=[80.0]
    )
    b_mm: float = Field(
        ..., gt=0, le=2000, description="Column width (mm)", examples=[300.0]
    )
    D_mm: float = Field(
        ..., gt=0, le=2000, description="Column depth (mm)", examples=[450.0]
    )
    l_mm: float = Field(
        ..., gt=0, le=50000, description="Unsupported length (mm)", examples=[3500.0]
    )
    end_condition: str = Field(
        "FIXED_FIXED",
        description="End condition per Table 28",
        examples=["FIXED_FIXED", "FIXED_HINGED"],
    )
    fck: float = Field(
        25.0, gt=0, le=100, description="Concrete strength (N/mm²)", examples=[25.0]
    )
    fy: float = Field(
        415.0,
        gt=0,
        le=600,
        description="Steel yield strength (N/mm²)",
        examples=[415.0],
    )
    Asc_mm2: float = Field(
        ..., gt=0, description="Total steel area (mm²)", examples=[2400.0]
    )
    d_prime_mm: float = Field(
        50.0, gt=0, description="Cover to steel centroid (mm)", examples=[50.0]
    )
    l_unsupported_mm: float | None = Field(
        None,
        description="Unsupported length (mm, defaults to l_mm)",
        examples=[3500.0],
    )
    braced: bool = Field(True, description="Braced against sway")
    M1x_kNm: float | None = Field(
        None, description="Smaller end moment about x (for slender)", examples=[30.0]
    )
    M2x_kNm: float | None = Field(
        None, description="Larger end moment about x (for slender)", examples=[80.0]
    )
    M1y_kNm: float | None = Field(
        None, description="Smaller end moment about y (for slender)", examples=[20.0]
    )
    M2y_kNm: float | None = Field(
        None, description="Larger end moment about y (for slender)", examples=[60.0]
    )


class ColumnDesignResponse(BaseModel):
    """Response for unified column design."""

    is_safe: bool
    classification: str
    governing_check: str
    checks: dict
    warnings: list[str] = []


# =============================================================================
# Column Detailing Models (IS 456 Cl. 26.5.3)
# =============================================================================


class ColumnDetailingRequest(BaseModel):
    """Request for column detailing check per IS 456 Cl 26.5.3."""

    b_mm: float = Field(
        ...,
        ge=100,
        le=5000,
        description="Column width (mm)",
        examples=[300.0, 400.0, 500.0],
    )
    D_mm: float = Field(
        ...,
        ge=100,
        le=5000,
        description="Column depth (mm)",
        examples=[300.0, 450.0, 600.0],
    )
    cover_mm: float = Field(
        40.0,
        ge=15,
        le=100,
        description="Clear cover (mm)",
        examples=[40.0, 50.0],
    )
    fck: float = Field(
        25.0,
        ge=15,
        le=80,
        description="Concrete grade (N/mm²)",
        examples=[20.0, 25.0, 30.0],
    )
    fy: float = Field(
        415.0,
        ge=250,
        le=600,
        description="Steel yield strength (N/mm²)",
        examples=[415.0, 500.0],
    )
    num_bars: int = Field(
        ...,
        ge=3,
        le=60,
        description="Number of longitudinal bars",
        examples=[4, 6, 8],
    )
    bar_dia_mm: float = Field(
        ...,
        ge=8,
        le=50,
        description="Longitudinal bar diameter (mm)",
        examples=[16.0, 20.0, 25.0],
    )
    tie_dia_mm: float | None = Field(
        None,
        ge=6,
        le=20,
        description="Tie diameter (mm), auto-computed if None",
        examples=[8.0, 10.0],
    )
    is_circular: bool = Field(
        False,
        description="True for circular columns",
    )
    at_lap_section: bool = Field(
        False,
        description="True if checking at lap splice location",
    )


class ColumnDetailingResponse(BaseModel):
    """Response for column detailing check per IS 456 Cl 26.5.3."""

    b_mm: float
    D_mm: float
    Ag_mm2: float
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
    tie_dia_mm: float
    tie_dia_required_mm: float
    tie_spacing_mm: float
    max_tie_spacing_mm: float
    tie_spacing_ok: bool
    cross_ties_needed: bool
    is_valid: bool
    clause_ref: str
    warnings: list[str]


# =============================================================================
# Ductile Detailing Models (IS 13920:2016 Cl 7)
# =============================================================================


class ColumnDuctileDetailingRequest(BaseModel):
    """Request for column ductile detailing check per IS 13920:2016 Cl 7."""

    b_mm: float = Field(
        ...,
        ge=200,
        le=5000,
        description="Column width — shorter dimension (mm)",
        examples=[300.0, 400.0, 500.0],
    )
    D_mm: float = Field(
        ...,
        ge=200,
        le=5000,
        description="Column depth — longer dimension (mm)",
        examples=[400.0, 500.0, 600.0],
    )
    clear_height_mm: float = Field(
        ...,
        gt=0,
        le=50000,
        description="Clear height of column between floors (mm)",
        examples=[3000.0, 4500.0],
    )
    bar_dia_mm: float = Field(
        ...,
        ge=8,
        le=50,
        description="Smallest longitudinal bar diameter (mm)",
        examples=[16.0, 20.0, 25.0],
    )
    fck: float = Field(
        ...,
        ge=15,
        le=80,
        description="Characteristic concrete strength (N/mm²)",
        examples=[20.0, 25.0, 30.0],
    )
    fy: float = Field(
        ...,
        ge=250,
        le=600,
        description="Yield strength of steel (N/mm²)",
        examples=[415.0, 500.0],
    )
    Ag_mm2: float | None = Field(
        None,
        gt=0,
        description="Gross area of column (mm²). Defaults to b×D if omitted.",
        examples=[200000.0],
    )
    Ak_mm2: float | None = Field(
        None,
        gt=0,
        description="Confined core area to hoop centerline (mm²). Estimated if omitted.",
        examples=[102400.0],
    )
