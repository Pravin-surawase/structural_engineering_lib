"""Transport models for the bounded regular interior flat-slab workflow."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool


class _StrictRequestModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        allow_inf_nan=False,
        str_strip_whitespace=True,
    )


class FlatSlabGridGeometryRequest(_StrictRequestModel):
    centre_to_centre_span_x_mm: float = Field(gt=0)
    centre_to_centre_span_y_mm: float = Field(gt=0)
    continuous_span_count_x: int = Field(ge=3)
    continuous_span_count_y: int = Field(ge=3)
    column_width_x_mm: float = Field(gt=0)
    column_width_y_mm: float = Field(gt=0)
    overall_depth_mm: float = Field(ge=125)
    conservative_effective_depth_mm: float = Field(gt=0)
    analysis_method: Literal["direct_design"]
    panel_location: Literal["interior"]
    all_spans_equal_x: StrictBool
    all_spans_equal_y: StrictBool
    columns_offset_from_grid: StrictBool
    solid_slab: StrictBool
    drop_present: StrictBool
    column_head_present: StrictBool
    marginal_beam_or_wall_present: StrictBool
    openings_present: StrictBool
    geometry_basis_reference: str = Field(min_length=1)


class FlatSlabMaterialRequest(_StrictRequestModel):
    concrete_grade_nmm2: Literal[20, 25, 30, 35, 40, 45, 50, 55, 60]
    steel_grade_nmm2: Literal[415, 500]
    uncoated_deformed_bars: StrictBool
    material_basis_reference: str = Field(min_length=1)


class FlatSlabGravityLoadRequest(_StrictRequestModel):
    service_dead_load_kn_per_m2: float = Field(gt=0)
    service_live_load_kn_per_m2: float = Field(gt=0)
    factored_uniform_load_kn_per_m2: float = Field(gt=0)
    self_weight_included: StrictBool
    identical_full_loading_on_represented_panels: StrictBool
    patterned_loading_required: StrictBool
    unbalanced_or_lateral_moment_transfer_present: StrictBool
    load_combination_approved: StrictBool
    load_basis_reference: str = Field(min_length=1)


class FlatSlabProvidedBarsRequest(_StrictRequestModel):
    diameter_mm: float = Field(gt=0)
    spacing_mm: float = Field(gt=0)


class FlatSlabDirectionDetailingRequest(_StrictRequestModel):
    column_strip_negative_bars: FlatSlabProvidedBarsRequest
    column_strip_positive_bars: FlatSlabProvidedBarsRequest
    middle_strip_negative_bars: FlatSlabProvidedBarsRequest
    middle_strip_positive_bars: FlatSlabProvidedBarsRequest
    support_top_extension_from_face_mm: float = Field(gt=0)


class RegularInteriorFlatSlabRequest(_StrictRequestModel):
    """All approved-basis inputs for the sole supported flat-slab case."""

    case_id: str = Field(min_length=1)
    geometry: FlatSlabGridGeometryRequest
    material: FlatSlabMaterialRequest
    gravity_load: FlatSlabGravityLoadRequest
    x: FlatSlabDirectionDetailingRequest
    y: FlatSlabDirectionDetailingRequest
    factored_support_reaction_kn: float = Field(gt=0)
    straight_bars_only: StrictBool
    all_bottom_bars_continuous: StrictBool
    splices_present: StrictBool
    serviceability_acceptance_acknowledged: StrictBool
    centred_concentric_reaction: StrictBool
    full_critical_perimeter_available: StrictBool
    no_punching_reinforcement_provided: StrictBool
    qualified_review_required: StrictBool
    detailing_basis_reference: str = Field(min_length=1)
    serviceability_acceptance_reference: str = Field(min_length=1)
    support_reaction_basis_reference: str = Field(min_length=1)
    punching_basis_reference: str = Field(min_length=1)


class FlatSlabDirectionGeometryResponse(BaseModel):
    direction: Literal["x", "y"]
    centre_to_centre_span_mm: float
    transverse_span_mm: float
    support_width_mm: float
    face_to_face_clear_span_mm: float
    minimum_clear_span_component_mm: float
    governing_clear_span_mm: float
    column_strip_half_width_mm: float
    column_strip_total_width_mm: float
    middle_strip_width_mm: float


class FlatSlabDirectionMomentsResponse(BaseModel):
    direction: Literal["x", "y"]
    factored_uniform_load_kn_per_m2: float
    transverse_span_m: float
    governing_clear_span_m: float
    design_load_on_panel_strip_kn: float
    total_static_moment_knm: float
    total_negative_moment_knm: float
    total_positive_moment_knm: float
    column_strip_negative_moment_knm: float
    column_strip_positive_moment_knm: float
    middle_strip_negative_moment_knm: float
    middle_strip_positive_moment_knm: float


class FlatSlabProvidedCheckResponse(BaseModel):
    region_id: str
    required_for_moment_mm2_per_m: float
    minimum_required_mm2_per_m: float
    governing_required_mm2_per_m: float
    provided_mm2_per_m: float
    maximum_diameter_mm: float
    maximum_spacing_mm: float
    area_passed: bool
    diameter_passed: bool
    spacing_passed: bool
    is_adequate: bool


class FlatSlabRegionReinforcementResponse(BaseModel):
    region_id: str
    factored_moment_knm: float
    strip_width_mm: float
    ast_required_total_mm2: float
    ast_required_mm2_per_m: float
    neutral_axis_depth_mm: float
    limiting_neutral_axis_depth_mm: float
    limiting_moment_knm: float
    provided_check: FlatSlabProvidedCheckResponse
    flat_slab_maximum_spacing_mm: float
    flat_slab_spacing_passed: bool
    is_adequate: bool


class FlatSlabDirectionReinforcementResponse(BaseModel):
    direction: Literal["x", "y"]
    column_strip_negative: FlatSlabRegionReinforcementResponse
    column_strip_positive: FlatSlabRegionReinforcementResponse
    middle_strip_negative: FlatSlabRegionReinforcementResponse
    middle_strip_positive: FlatSlabRegionReinforcementResponse
    required_support_top_extension_from_face_mm: float
    provided_support_top_extension_from_face_mm: float
    support_top_extension_passed: bool
    is_adequate: bool


class FlatSlabServiceabilityResponse(BaseModel):
    actual_span_depth_ratio: float
    reviewed_modified_span_depth_limit: float
    utilization: float
    status: Literal["satisfied_with_reviewed_limit", "limit_exceeded"]
    direct_deflection_status: str
    crack_width_status: str
    source_reference: str
    qualified_acceptance_reference: str
    verified_by_library: Literal[False]
    is_satisfied: bool


class FlatSlabReinforcementResponse(BaseModel):
    geometry_x: FlatSlabDirectionGeometryResponse
    geometry_y: FlatSlabDirectionGeometryResponse
    moments_x: FlatSlabDirectionMomentsResponse
    moments_y: FlatSlabDirectionMomentsResponse
    x: FlatSlabDirectionReinforcementResponse
    y: FlatSlabDirectionReinforcementResponse
    x_serviceability: FlatSlabServiceabilityResponse
    y_serviceability: FlatSlabServiceabilityResponse
    direct_deflection_status: str
    crack_width_status: str
    source_refs: tuple[str, ...]
    limitations: tuple[str, ...]
    is_reinforcement_and_detailing_adequate: bool
    is_span_depth_satisfied: bool


class FlatSlabPunchingResponse(BaseModel):
    expected_uniform_tributary_reaction_kn: float
    critical_section_side_x_mm: float
    critical_section_side_y_mm: float
    critical_perimeter_mm: float
    critical_enclosed_area_mm2: float
    factored_load_inside_critical_section_kn: float
    punching_shear_force_kn: float
    nominal_punching_stress_n_per_mm2: float
    column_aspect_ratio_beta_c: float
    size_factor_ks: float
    basic_concrete_shear_strength_n_per_mm2: float
    no_reinforcement_capacity_n_per_mm2: float
    mandatory_redesign_boundary_n_per_mm2: float
    no_reinforcement_utilization: float
    status: Literal[
        "safe_without_punching_reinforcement",
        "punching_reinforcement_or_redesign_required",
        "redesign_required",
    ]
    source_refs: tuple[str, ...]
    limitations: tuple[str, ...]
    is_adequate_without_punching_reinforcement: bool


class RegularInteriorFlatSlabProvenanceResponse(BaseModel):
    schema_version: str
    code_edition: str
    workflow: str
    case_id: str
    benchmark_id: str
    action_generation_status: str
    support_reaction_status: str
    serviceability_verification_status: str
    geometry_basis_reference: str
    material_basis_reference: str
    load_basis_reference: str
    detailing_basis_reference: str
    serviceability_acceptance_reference: str
    support_reaction_basis_reference: str
    punching_basis_reference: str
    clause_refs: tuple[str, ...]
    source_refs: tuple[str, ...]


class RegularInteriorFlatSlabResponse(BaseModel):
    case_id: str
    status: Literal["PASS", "FAIL"]
    reinforcement: FlatSlabReinforcementResponse
    punching: FlatSlabPunchingResponse
    supported_case: str
    held_cases: tuple[str, ...]
    provenance: RegularInteriorFlatSlabProvenanceResponse
    qualified_review_required: Literal[True]
    complete_engineering_design_approved: Literal[False]
