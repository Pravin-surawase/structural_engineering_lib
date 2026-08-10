"""
Common Pydantic Models.

Shared models used across multiple API endpoints.
All dimensions in mm, forces in kN, moments in kN·m, stresses in N/mm².
"""

from typing import Any

from pydantic import BaseModel, Field

from fastapi_app.models.response import APIResponse as APIResponse

# =============================================================================
# Material Properties
# =============================================================================


class MaterialProperties(BaseModel):
    """Concrete and steel material properties."""

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


# =============================================================================
# Beam Section
# =============================================================================


class BeamSection(BaseModel):
    """Beam cross-section dimensions."""

    width: float = Field(
        gt=0,
        le=2000.0,
        description="Beam width (mm)",
        examples=[230.0, 300.0, 400.0],
    )
    depth: float = Field(
        gt=0,
        le=3000.0,
        description="Overall beam depth (mm)",
        examples=[450.0, 600.0, 750.0],
    )
    clear_cover: float = Field(
        default=25.0,
        ge=20.0,
        le=75.0,
        description="Clear cover to reinforcement (mm)",
        examples=[25.0, 30.0, 40.0],
    )
    effective_depth: float | None = Field(
        default=None,
        description="Effective depth if known (mm). If not provided, calculated from depth - cover - bar_diameter/2",
    )


# =============================================================================
# Load Cases
# =============================================================================


class LoadCase(BaseModel):
    """Applied loads on the beam."""

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
    torsion: float = Field(
        default=0.0,
        ge=0,
        description="Factored design torsion Tu (kN·m)",
        examples=[0.0, 20.0, 50.0],
    )


# =============================================================================
# Design Basis
# =============================================================================


class DesignBasis(BaseModel):
    """Design code and assumptions."""

    code: str = Field(
        default="IS 456:2000",
        description="Design code reference",
        examples=["IS 456:2000"],
    )
    exposure_class: str = Field(
        default="moderate",
        description="Exposure condition per IS 456 Table 3",
        examples=["mild", "moderate", "severe", "very severe", "extreme"],
    )
    seismic_zone: str | None = Field(
        default=None,
        description="Seismic zone for ductile detailing per IS 13920",
        examples=["II", "III", "IV", "V"],
    )


# =============================================================================
# Common error model and canonical API response re-export
# =============================================================================


class ErrorResponse(BaseModel):
    """Error response model."""

    success: bool = Field(default=False, description="Always false for errors")
    error_code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error message")
    details: dict[str, Any] | None = Field(
        default=None, description="Additional error details"
    )
