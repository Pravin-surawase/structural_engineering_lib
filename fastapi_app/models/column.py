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
