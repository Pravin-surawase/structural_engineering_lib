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
