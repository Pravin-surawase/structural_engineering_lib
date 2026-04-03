# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Pydantic models for Project BOQ endpoint."""

from pydantic import BaseModel, Field


class BeamMetadata(BaseModel):
    """Per-beam metadata for BOQ aggregation."""

    beam_id: str = Field(max_length=200, description="Beam identifier")
    story: str = Field(default="GF", max_length=200, description="Story/floor name")
    b_mm: float = Field(..., gt=0, description="Beam width in mm")
    D_mm: float = Field(..., gt=0, description="Overall depth in mm")
    span_mm: float = Field(..., gt=0, description="Span length in mm")
    fck: int = Field(default=25, description="Concrete grade (N/mm²)")
    steel_weight_kg: float = Field(
        default=0.0, ge=0, description="Total steel weight for this beam in kg"
    )


class ProjectBOQRequest(BaseModel):
    """Request for project BOQ aggregation."""

    project_name: str = Field(
        default="Project", max_length=200, description="Display name"
    )
    beams: list[BeamMetadata] = Field(min_length=1, description="List of beam metadata")
    steel_cost_per_kg: float = Field(default=60.0, gt=0, description="Steel rate ₹/kg")
    concrete_costs: dict[int, float] | None = Field(
        default=None,
        description=(
            "Concrete costs by grade {fck: ₹/m³}. "
            "Defaults: {25: 6000, 30: 7000, 35: 8000, 40: 9500}"
        ),
    )


class SteelSummaryResponse(BaseModel):
    """Steel quantities for one grade."""

    grade: str = Field(description="Steel grade (e.g. Fe500)")
    total_weight_kg: float = Field(description="Total steel weight in kg")
    cost_inr: float = Field(description="Cost in ₹")


class ConcreteSummaryResponse(BaseModel):
    """Concrete quantities for one grade."""

    grade: str = Field(description="Concrete grade (e.g. M25)")
    total_volume_m3: float = Field(description="Total volume in m³")
    cost_inr: float = Field(description="Cost in ₹")


class StorySummaryResponse(BaseModel):
    """Quantities for one story/floor."""

    story: str = Field(description="Story name")
    beam_count: int = Field(description="Number of beams")
    steel_kg: float = Field(description="Total steel in kg")
    concrete_m3: float = Field(description="Total concrete in m³")
    cost_inr: float = Field(description="Total cost in ₹")


class ProjectBOQResponse(BaseModel):
    """BOQ response with aggregated quantities and costs."""

    success: bool = Field(default=True, description="Whether aggregation succeeded")
    project_name: str = Field(description="Project display name")
    total_beams: int = Field(description="Total number of beams")
    steel: list[SteelSummaryResponse] = Field(description="Steel by grade")
    concrete: list[ConcreteSummaryResponse] = Field(description="Concrete by grade")
    by_story: list[StorySummaryResponse] = Field(description="Breakdown by story")
    grand_total_steel_kg: float = Field(description="Total steel weight in kg")
    grand_total_concrete_m3: float = Field(description="Total concrete volume in m³")
    grand_total_cost_inr: float = Field(description="Grand total cost in ₹")
