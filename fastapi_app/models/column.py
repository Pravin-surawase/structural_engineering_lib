"""
Column Design Pydantic Models.

Models for column classification, eccentricity, and axial design endpoints.
All dimensions in mm, forces in kN, stresses in N/mm².
"""

from pydantic import BaseModel, Field

# =============================================================================
# Request Models
# =============================================================================


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
        description="Distance from face to steel centroid (mm)",
        examples=[50.0, 60.0, 40.0],
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
