"""Transport models for the bounded property-line strap-footing workflow."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


def _require_boolean(value: object) -> object:
    """Reject Pydantic's normal integer/string coercion at approval boundaries."""
    if type(value) is not bool:
        raise ValueError("Input should be a valid boolean")
    return value


StrictTrue = Annotated[Literal[True], BeforeValidator(_require_boolean)]
StrictFalse = Annotated[Literal[False], BeforeValidator(_require_boolean)]


class _StrictRequestModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        allow_inf_nan=False,
        str_strip_whitespace=True,
    )


class StrapFootingGeometryRequest(_StrictRequestModel):
    exterior_footing_length_mm: float = Field(gt=0)
    exterior_footing_width_mm: float = Field(gt=0)
    exterior_footing_depth_mm: float = Field(ge=150)
    interior_footing_length_mm: float = Field(gt=0)
    interior_footing_width_mm: float = Field(gt=0)
    interior_footing_depth_mm: float = Field(ge=150)
    exterior_column_side_mm: float = Field(gt=0)
    interior_column_side_mm: float = Field(gt=0)
    exterior_column_center_x_mm: float = Field(gt=0)
    interior_column_center_x_mm: float = Field(gt=0)
    strap_width_mm: float = Field(gt=0)
    strap_overall_depth_mm: float = Field(gt=0)
    strap_effective_depth_mm: float = Field(gt=0)
    footing_count: Literal[2]
    column_count: Literal[2]
    footings_rectangular: StrictTrue
    footings_parallel: StrictTrue
    footings_constant_depth: StrictTrue
    columns_square: StrictTrue
    columns_and_strap_share_centerline: StrictTrue
    interior_column_centered_on_footing: StrictTrue
    strap_straight_and_prismatic: StrictTrue
    strap_centered_across_footings: StrictTrue
    foundation_on_soil: StrictTrue
    strap_soil_contact: StrictFalse
    openings_present: StrictFalse
    pedestals_present: StrictFalse
    analysis_method: Literal["rigid_equal_pressure"]
    pressure_model: Literal["equal_uniform_net"]
    geometry_basis_reference: str = Field(min_length=1)
    rigidity_basis_reference: str = Field(min_length=1)
    strap_isolation_basis_reference: str = Field(min_length=1)


class StrapFootingActionRequest(_StrictRequestModel):
    service_exterior_column_load_kn: float = Field(gt=0)
    service_interior_column_load_kn: float = Field(gt=0)
    factored_exterior_column_load_kn: float = Field(gt=0)
    factored_interior_column_load_kn: float = Field(gt=0)
    service_clear_strap_line_load_kn_per_m: float = Field(ge=0)
    factored_clear_strap_line_load_kn_per_m: float = Field(ge=0)
    service_exterior_footing_carrier_kn_per_m2: float = Field(ge=0)
    service_interior_footing_carrier_kn_per_m2: float = Field(ge=0)
    factored_exterior_footing_carrier_kn_per_m2: float = Field(ge=0)
    factored_interior_footing_carrier_kn_per_m2: float = Field(ge=0)
    allowable_gross_bearing_pressure_kn_per_m2: float = Field(gt=0)
    load_combination_approved: StrictTrue
    bearing_and_settlement_approved: StrictTrue
    equal_uniform_pressure_approved: StrictTrue
    footing_carrier_basis_approved: StrictTrue
    strap_line_load_basis_approved: StrictTrue
    load_pattern_compatible: StrictTrue
    column_moments_present: StrictFalse
    horizontal_actions_present: StrictFalse
    uplift_or_load_reversal_present: StrictFalse
    independently_factored_or_patterned_actions_present: StrictFalse
    load_basis_reference: str = Field(min_length=1)
    bearing_settlement_basis_reference: str = Field(min_length=1)
    footing_carrier_basis_reference: str = Field(min_length=1)
    strap_line_load_basis_reference: str = Field(min_length=1)
    load_pattern_basis_reference: str = Field(min_length=1)


class StrapFootingApprovalRequest(_StrictRequestModel):
    exterior_footing_design_verified: StrictTrue
    interior_footing_design_verified: StrictTrue
    column_and_strap_transfer_verified: StrictTrue
    footing_reinforcement_and_anchorage_verified: StrictTrue
    supporting_areas_verified: StrictTrue
    construction_clearances_verified: StrictTrue
    exterior_footing_verification_reference: str = Field(min_length=1)
    interior_footing_verification_reference: str = Field(min_length=1)
    transfer_verification_reference: str = Field(min_length=1)
    construction_verification_reference: str = Field(min_length=1)


class StrapFootingAnalysisRequest(_StrictRequestModel):
    geometry: StrapFootingGeometryRequest
    actions: StrapFootingActionRequest
    approvals: StrapFootingApprovalRequest


class StrapFootingMaterialRequest(_StrictRequestModel):
    strap_concrete_grade_nmm2: Literal[20, 25, 30, 35, 40]
    steel_grade_nmm2: Literal[415, 500]
    uncoated_deformed_bars: StrictTrue
    material_basis_reference: str = Field(min_length=1)


class StrapFootingReinforcementRequest(_StrictRequestModel):
    top_bar_count: int = Field(ge=2)
    top_bar_diameter_mm: Literal[8, 10, 12, 16, 20, 25, 32, 36]
    bottom_bar_count: int = Field(ge=2)
    bottom_bar_diameter_mm: Literal[8, 10, 12, 16, 20, 25, 32, 36]
    side_face_bar_count_each_face: int = Field(ge=2)
    side_face_bar_diameter_mm: Literal[8, 10, 12, 16, 20, 25, 32, 36]
    side_face_vertical_spacing_mm: float = Field(gt=0)
    stirrup_leg_count: int = Field(ge=2)
    stirrup_diameter_mm: Literal[8, 10, 12, 16, 20, 25, 32, 36]
    stirrup_spacing_mm: float = Field(gt=0)
    nominal_cover_mm: float = Field(gt=0)
    required_nominal_cover_mm: float = Field(gt=0)
    maximum_aggregate_size_mm: float = Field(gt=0)
    available_top_anchorage_exterior_mm: float = Field(gt=0)
    available_top_anchorage_interior_mm: float = Field(gt=0)
    available_bottom_anchorage_exterior_mm: float = Field(gt=0)
    available_bottom_anchorage_interior_mm: float = Field(gt=0)
    vertical_closed_stirrups: StrictTrue
    straight_anchorage: StrictTrue
    bars_bundled: StrictFalse
    bars_spliced: StrictFalse
    bars_curtailed: StrictFalse
    reinforcement_schedule_approved: StrictTrue
    effective_depth_basis_approved: StrictTrue
    durability_cover_basis_approved: StrictTrue
    detailing_basis_reference: str = Field(min_length=1)
    durability_basis_reference: str = Field(min_length=1)


class StrapFootingDesignRequest(_StrictRequestModel):
    analysis: StrapFootingAnalysisRequest
    material: StrapFootingMaterialRequest
    reinforcement: StrapFootingReinforcementRequest


class PropertyLineStrapFootingRequest(_StrictRequestModel):
    """Explicit approved-basis inputs for the sole strap-footing case."""

    case_id: str = Field(min_length=1)
    footing: StrapFootingDesignRequest
    qualified_review_required: StrictTrue


class StrapFootingGeometryResponse(BaseModel):
    input: StrapFootingGeometryRequest
    exterior_footing_area_m2: float
    interior_footing_area_m2: float
    exterior_footing_centroid_x_mm: float
    interior_footing_centroid_x_mm: float
    exterior_column_eccentricity_mm: float
    reaction_spacing_mm: float
    exterior_footing_inner_edge_x_mm: float
    interior_footing_outer_edge_x_mm: float
    interior_footing_inner_edge_x_mm: float
    clear_strap_start_x_mm: float
    clear_strap_end_x_mm: float
    clear_strap_length_mm: float
    clear_strap_centroid_x_mm: float
    clear_span_to_overall_depth_ratio: float
    rigid_equal_pressure_eligible: bool
    source_refs: tuple[str, ...]


class StrapFootingLoadCaseResponse(BaseModel):
    load_case: Literal["service", "factored"]
    exterior_column_load_kn: float
    interior_column_load_kn: float
    clear_strap_line_load_kn_per_m: float
    clear_strap_total_load_kn: float
    total_downward_load_kn: float
    exterior_reaction_kn: float
    interior_reaction_kn: float
    exterior_net_pressure_kn_per_m2: float
    interior_net_pressure_kn_per_m2: float
    pressure_relative_mismatch: float
    equal_uniform_net_pressure: bool
    exterior_footing_carrier_kn_per_m2: float
    interior_footing_carrier_kn_per_m2: float
    exterior_gross_pressure_kn_per_m2: float
    interior_gross_pressure_kn_per_m2: float
    vertical_equilibrium_residual_kn: float
    moment_equilibrium_residual_kn_m: float


class StrapFootingClearSpanActionResponse(BaseModel):
    load_case: Literal["service", "factored"]
    exterior_face_x_mm: float
    exterior_face_shear_kn: float
    exterior_face_moment_kn_m: float
    interior_face_x_mm: float
    interior_face_shear_kn: float
    interior_face_moment_kn_m: float
    governing_shear_demand_kn: float
    governing_shear_x_mm: float
    governing_moment_demand_kn_m: float
    governing_moment_signed_kn_m: float
    governing_moment_x_mm: float
    governing_tension_face: Literal["bottom", "top", "none"]


class StrapFootingAnalysisResponse(BaseModel):
    input: StrapFootingAnalysisRequest
    geometry: StrapFootingGeometryResponse
    service: StrapFootingLoadCaseResponse
    factored: StrapFootingLoadCaseResponse
    service_clear_strap: StrapFootingClearSpanActionResponse
    factored_clear_strap: StrapFootingClearSpanActionResponse
    common_factored_multiplier: float
    allowable_gross_bearing_pressure_kn_per_m2: float
    exterior_service_bearing_utilization: float
    interior_service_bearing_utilization: float
    exterior_service_bearing_within_allowable: bool
    interior_service_bearing_within_allowable: bool
    gross_service_bearing_within_allowable: bool
    source_refs: tuple[str, ...]


class StrapFootingFlexureResponse(BaseModel):
    governing_tension_face: Literal["bottom", "top", "none"]
    factored_moment_demand_kn_m: float
    limiting_singly_reinforced_moment_kn_m: float
    exact_flexural_steel_required_mm2: float | None
    exact_neutral_axis_depth_mm: float | None
    beam_minimum_steel_required_mm2: float
    top_steel_required_mm2: float | None
    bottom_steel_required_mm2: float | None
    top_steel_provided_mm2: float
    bottom_steel_provided_mm2: float
    top_neutral_axis_depth_mm: float
    bottom_neutral_axis_depth_mm: float
    top_moment_capacity_kn_m: float
    bottom_moment_capacity_kn_m: float
    top_clear_spacing_mm: float
    bottom_clear_spacing_mm: float
    minimum_top_clear_spacing_mm: float
    minimum_bottom_clear_spacing_mm: float
    nominal_cover_mm: float
    required_nominal_cover_mm: float
    tension_design_bond_stress_nmm2: float
    top_development_length_required_mm: float
    bottom_development_length_required_mm: float
    top_anchorage_exterior_available_mm: float
    top_anchorage_interior_available_mm: float
    bottom_anchorage_exterior_available_mm: float
    bottom_anchorage_interior_available_mm: float
    singly_reinforced_capacity_is_sufficient: bool
    top_area_is_safe: bool
    bottom_area_is_safe: bool
    top_section_is_under_reinforced: bool
    bottom_section_is_under_reinforced: bool
    top_clear_spacing_is_safe: bool
    bottom_clear_spacing_is_safe: bool
    nominal_cover_is_safe: bool
    top_anchorage_is_safe: bool
    bottom_anchorage_is_safe: bool
    is_safe: bool


class StrapFootingSideFaceResponse(BaseModel):
    required: bool
    required_total_area_mm2: float
    required_area_each_face_mm2: float
    provided_area_each_face_mm2: float
    provided_total_area_mm2: float
    provided_vertical_spacing_mm: float
    maximum_vertical_spacing_mm: float
    area_is_safe: bool
    spacing_is_safe: bool
    is_safe: bool


class StrapFootingShearResponse(BaseModel):
    factored_shear_demand_kn: float
    tension_reinforcement_area_mm2: float
    tension_reinforcement_percent: float
    table_19_lookup_reinforcement_percent: float
    nominal_shear_stress_nmm2: float
    concrete_design_shear_strength_nmm2: float
    maximum_design_shear_stress_nmm2: float
    concrete_shear_capacity_kn: float
    stirrup_carried_shear_required_kn: float
    stirrup_area_provided_mm2: float
    minimum_stirrup_area_at_provided_spacing_mm2: float
    stirrup_shear_capacity_provided_kn: float
    provided_stirrup_spacing_mm: float
    maximum_stirrup_spacing_mm: float
    maximum_stress_is_safe: bool
    minimum_stirrup_area_is_safe: bool
    stirrup_strength_is_safe: bool
    stirrup_spacing_is_safe: bool
    is_safe: bool


class StrapFootingStrengthResponse(BaseModel):
    input: StrapFootingDesignRequest
    actions: StrapFootingAnalysisResponse
    flexure: StrapFootingFlexureResponse
    side_face: StrapFootingSideFaceResponse
    shear: StrapFootingShearResponse
    disposition: Literal["PASS", "FAIL"]
    reasons: tuple[str, ...]
    clause_refs: tuple[str, ...]
    source_refs: tuple[str, ...]
    limitations: tuple[str, ...]
    qualified_review_required: Literal[True]
    complete_engineering_approval: Literal[False]


class PropertyLineStrapFootingProvenanceResponse(BaseModel):
    schema_version: str
    code_edition: str
    workflow: str
    case_id: str
    benchmark_id: str
    action_generation_status: str
    soil_verification_status: str
    geometry_basis_reference: str
    rigidity_basis_reference: str
    strap_isolation_basis_reference: str
    load_basis_reference: str
    bearing_settlement_basis_reference: str
    footing_carrier_basis_reference: str
    strap_line_load_basis_reference: str
    load_pattern_basis_reference: str
    exterior_footing_verification_reference: str
    interior_footing_verification_reference: str
    transfer_verification_reference: str
    construction_verification_reference: str
    material_basis_reference: str
    detailing_basis_reference: str
    durability_basis_reference: str
    clause_refs: tuple[str, ...]
    source_refs: tuple[str, ...]


class PropertyLineStrapFootingResponse(BaseModel):
    """Typed transport projection of the composed strap-footing result."""

    case_id: str
    status: Literal["PASS", "FAIL"]
    strength: StrapFootingStrengthResponse
    supported_case: str
    held_cases: tuple[str, ...]
    provenance: PropertyLineStrapFootingProvenanceResponse
    qualified_review_required: Literal[True]
    complete_engineering_design_approved: Literal[False]
