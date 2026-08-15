"""Transport models for the bounded braced-wall workflow."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BracedWallRequest(BaseModel):
    """Explicit inputs for the sole supported Clause 32 wall case."""

    model_config = ConfigDict(
        extra="forbid",
        allow_inf_nan=False,
        str_strip_whitespace=True,
    )

    case_id: str = Field(min_length=1)
    unsupported_height_mm: float = Field(gt=0)
    lateral_restraint_spacing_mm: float = Field(gt=0)
    wall_length_mm: float = Field(gt=0)
    wall_thickness_mm: float = Field(ge=100, le=200)
    concrete_grade_nmm2: Literal[20, 25, 30, 35, 40, 45, 50, 55, 60]
    factored_axial_load_kn: float = Field(gt=0)
    supplied_eccentricity_mm: float = Field(ge=0)
    vertical_bar_diameter_mm: float = Field(gt=0)
    vertical_bar_spacing_mm: float = Field(gt=0)
    horizontal_bar_diameter_mm: float = Field(gt=0)
    horizontal_bar_spacing_mm: float = Field(gt=0)
    bracing_basis_reference: str = Field(min_length=1)
    action_basis_reference: str = Field(min_length=1)
    reinforcement_basis_reference: str = Field(min_length=1)
    rotation_restraint: Literal["restrained_both_ends", "not_restrained_both_ends"] = (
        "restrained_both_ends"
    )
    reinforcement_kind: Literal[
        "deformed_415_or_greater", "other_bars", "welded_wire_fabric"
    ] = "deformed_415_or_greater"
    bracing_elements_in_two_directions: Literal[True] = True
    lateral_forces_resisted_by_bracing_system: Literal[True] = True
    diaphragm_transfer_confirmed: Literal[True] = True
    lateral_connection_capacity_confirmed: Literal[True] = True


class BracedWallAxialResponse(BaseModel):
    effective_height_mm: float
    effective_height_to_thickness_ratio: float
    minimum_eccentricity_mm: float
    design_eccentricity_mm: float
    additional_eccentricity_mm: float
    effective_compression_thickness_mm: float
    axial_capacity_n_per_mm: float
    axial_capacity_kn_per_m: float
    total_axial_capacity_kn: float
    axial_demand_n_per_mm: float
    axial_demand_kn_per_m: float
    utilization_ratio: float
    status: Literal["PASS", "FAIL"]
    source_refs: tuple[str, ...]
    load_generation_status: str


class WallDirectionalReinforcementResponse(BaseModel):
    minimum_ratio: float
    required_area_mm2_per_m: float
    provided_area_mm2_per_m: float
    provided_ratio: float
    maximum_spacing_mm: float
    provided_spacing_mm: float
    area_status: Literal["PASS", "FAIL"]
    spacing_status: Literal["PASS", "FAIL"]
    status: Literal["PASS", "FAIL"]


class WallReinforcementResponse(BaseModel):
    vertical: WallDirectionalReinforcementResponse
    horizontal: WallDirectionalReinforcementResponse
    transverse_enclosure_required: bool
    status: Literal["PASS", "FAIL"]
    source_refs: tuple[str, ...]


class BracedWallProvenanceResponse(BaseModel):
    schema_version: str
    code_edition: str
    workflow: str
    case_id: str
    benchmark_id: str
    load_generation_status: str
    bracing_basis_reference: str
    action_basis_reference: str
    reinforcement_basis_reference: str
    clause_refs: tuple[str, ...]
    source_refs: tuple[str, ...]


class BracedWallResponse(BaseModel):
    """Typed transport subset of the composed wall result."""

    case_id: str
    status: Literal["PASS", "FAIL"]
    axial: BracedWallAxialResponse
    reinforcement: WallReinforcementResponse
    supported_case: str
    held_cases: tuple[str, ...]
    provenance: BracedWallProvenanceResponse
    qualified_review_required: Literal[True]
    complete_engineering_design_approved: Literal[False]
