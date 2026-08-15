"""Transport models for the bounded simply supported deep-beam workflow."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool


class SimplySupportedDeepBeamRequest(BaseModel):
    """Explicit inputs for the sole supported Clause 29 deep-beam case."""

    model_config = ConfigDict(
        extra="forbid",
        allow_inf_nan=False,
        str_strip_whitespace=True,
    )

    case_id: str = Field(min_length=1)
    centre_to_centre_span_mm: float = Field(gt=0)
    clear_span_mm: float = Field(gt=0)
    overall_depth_mm: float = Field(gt=0)
    beam_width_mm: float = Field(gt=0)
    concrete_grade_nmm2: Literal[20, 25, 30, 35, 40, 45, 50, 55, 60]
    steel_grade_nmm2: Literal[415, 500]
    factored_positive_moment_knm: float = Field(gt=0)
    main_bar_count: int = Field(gt=0)
    main_bar_diameter_mm: float = Field(gt=0)
    furthest_main_bar_from_tension_face_mm: float = Field(gt=0)
    main_bars_continuous_between_supports: StrictBool
    main_bars_bundled: Literal[False]
    main_bar_splices_present: Literal[False]
    left_support_embedment_mm: float = Field(ge=0)
    right_support_embedment_mm: float = Field(ge=0)
    face_grid_count: Literal[1, 2]
    vertical_side_bar_diameter_mm: float = Field(gt=0, le=16)
    vertical_side_bar_spacing_mm: float = Field(gt=0)
    horizontal_side_bar_diameter_mm: float = Field(gt=0, le=16)
    horizontal_side_bar_spacing_mm: float = Field(gt=0)
    geometry_basis_reference: str = Field(min_length=1)
    bearing_nodal_zone_reference: str = Field(min_length=1)
    action_basis_reference: str = Field(min_length=1)
    reinforcement_basis_reference: str = Field(min_length=1)
    support_type: Literal["simply_supported"]
    solid_rectangular_section: Literal[True]
    openings_present: Literal[False]
    dapped_ends_present: Literal[False]
    top_loaded: Literal[True]
    hanging_action_required: Literal[False]
    bearing_nodal_zone_verified: Literal[True]


class DeepBeamGeometryResponse(BaseModel):
    effective_span_mm: float
    effective_span_to_depth_ratio: float
    lever_arm_case: str
    lever_arm_mm: float
    positive_reinforcement_zone_depth_mm: float
    source_refs: tuple[str, ...]


class DeepBeamTieResponse(BaseModel):
    required_area_mm2: float
    provided_area_mm2: float
    design_steel_stress_nmm2: float
    status: Literal["PASS", "FAIL"]


class DeepBeamPlacementResponse(BaseModel):
    permitted_zone_depth_mm: float
    furthest_bar_distance_mm: float
    status: Literal["PASS", "FAIL"]


class DeepBeamAnchorageResponse(BaseModel):
    design_steel_stress_nmm2: float
    design_bond_stress_nmm2: float
    development_length_mm: float
    required_embedment_mm: float
    left_embedment_mm: float
    right_embedment_mm: float
    left_status: Literal["PASS", "FAIL"]
    right_status: Literal["PASS", "FAIL"]
    status: Literal["PASS", "FAIL"]


class DeepBeamSideFaceDirectionResponse(BaseModel):
    minimum_ratio: float
    required_area_mm2_per_m: float
    provided_area_mm2_per_m: float
    provided_ratio: float
    required_face_grid_count: int
    provided_face_grid_count: int
    maximum_spacing_mm: float
    provided_spacing_mm: float
    area_status: Literal["PASS", "FAIL"]
    spacing_status: Literal["PASS", "FAIL"]
    status: Literal["PASS", "FAIL"]


class DeepBeamReinforcementResponse(BaseModel):
    geometry: DeepBeamGeometryResponse
    positive_tie: DeepBeamTieResponse
    placement: DeepBeamPlacementResponse
    continuity_status: Literal["PASS", "FAIL"]
    anchorage: DeepBeamAnchorageResponse
    vertical_side_face: DeepBeamSideFaceDirectionResponse
    horizontal_side_face: DeepBeamSideFaceDirectionResponse
    external_bearing_nodal_prerequisite_satisfied: Literal[True]
    status: Literal["PASS", "FAIL"]
    shear_deemed_satisfied_within_clause_29_scope: bool
    source_refs: tuple[str, ...]


class SimplySupportedDeepBeamProvenanceResponse(BaseModel):
    schema_version: str
    code_edition: str
    workflow: str
    case_id: str
    benchmark_id: str
    action_generation_status: str
    bearing_nodal_zone_status: str
    geometry_basis_reference: str
    bearing_nodal_zone_reference: str
    action_basis_reference: str
    reinforcement_basis_reference: str
    clause_refs: tuple[str, ...]
    source_refs: tuple[str, ...]


class SimplySupportedDeepBeamResponse(BaseModel):
    """Typed transport subset of the composed deep-beam result."""

    case_id: str
    status: Literal["PASS", "FAIL"]
    reinforcement: DeepBeamReinforcementResponse
    supported_case: str
    held_cases: tuple[str, ...]
    provenance: SimplySupportedDeepBeamProvenanceResponse
    qualified_review_required: Literal[True]
    complete_engineering_design_approved: Literal[False]
    shear_deemed_satisfied_within_clause_29_scope: bool
