# SPDX-License-Identifier: MIT
"""
Rebar API Models.

Request/response models for rebar validation and application endpoints.
"""

from pydantic import BaseModel, Field


class BeamDimensions(BaseModel):
    """Basic beam geometry for rebar checks."""

    width_mm: float = Field(gt=0, description="Beam width (mm)")
    depth_mm: float = Field(gt=0, description="Beam depth (mm)")
    cover_mm: float = Field(default=40.0, description="Clear cover (mm)")
    span_mm: float = Field(default=5000.0, description="Span length (mm)")


class RebarConfigModel(BaseModel):
    """Rebar configuration parameters."""

    bar_count: int = Field(gt=0, description="Number of bars")
    bar_dia_mm: float = Field(gt=0, description="Main bar diameter (mm)")
    stirrup_dia_mm: float = Field(default=8.0, description="Stirrup diameter (mm)")
    layers: int = Field(default=1, ge=1, description="Number of layers")
    is_top: bool = Field(default=False, description="Top layer bars")
    stirrup_spacing_start: float = Field(
        default=150.0, description="Stirrup spacing at start (mm)"
    )
    stirrup_spacing_mid: float = Field(
        default=200.0, description="Stirrup spacing at mid (mm)"
    )
    stirrup_spacing_end: float = Field(
        default=150.0, description="Stirrup spacing at end (mm)"
    )
    agg_size_mm: float = Field(default=20.0, description="Aggregate size (mm)")


class RebarValidationRequest(BaseModel):
    beam: BeamDimensions
    config: RebarConfigModel


class RebarValidationResponse(BaseModel):
    success: bool
    message: str
    validation: dict
    warnings: list[str] = Field(default_factory=list)


class RebarApplyRequest(BaseModel):
    beam: BeamDimensions
    config: RebarConfigModel


class RebarApplyResponse(BaseModel):
    success: bool
    message: str
    validation: dict | None = None
    geometry: dict | None = None
    warnings: list[str] = Field(default_factory=list)
