"""Transport models for the bounded symmetric combined-footing workflow."""

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


class CombinedFootingGeometryRequest(_StrictRequestModel):
    footing_length_mm: float = Field(gt=0)
    footing_width_mm: float = Field(gt=0)
    overall_depth_mm: float = Field(ge=150)
    effective_depth_mm: float = Field(gt=0)
    column_side_mm: float = Field(gt=0)
    left_column_center_x_mm: float = Field(gt=0)
    right_column_center_x_mm: float = Field(gt=0)
    column_count: Literal[2]
    columns_identical: StrictTrue
    columns_square: StrictTrue
    columns_centered_across_width: StrictTrue
    foundation_on_soil: StrictTrue
    constant_depth: StrictTrue
    openings_present: StrictFalse
    pedestals_present: StrictFalse
    analysis_method: Literal["conventional_rigid"]
    pressure_model: Literal["uniform"]
    rigid_footing_verified: StrictTrue
    rigidity_basis_reference: str = Field(min_length=1)
    geometry_basis_reference: str = Field(min_length=1)


class CombinedFootingActionRequest(_StrictRequestModel):
    service_axial_load_each_kn: float = Field(gt=0)
    factored_axial_load_each_kn: float = Field(gt=0)
    service_uniform_carrier_kn_per_m2: float = Field(gt=0)
    factored_uniform_carrier_kn_per_m2: float = Field(gt=0)
    allowable_gross_bearing_pressure_kn_per_m2: float = Field(gt=0)
    load_combination_approved: StrictTrue
    bearing_and_settlement_approved: StrictTrue
    pressure_uniformity_approved: StrictTrue
    distributed_carrier_cancellation_approved: StrictTrue
    column_moments_present: StrictFalse
    horizontal_actions_present: StrictFalse
    uplift_or_load_reversal_present: StrictFalse
    load_basis_reference: str = Field(min_length=1)
    bearing_settlement_basis_reference: str = Field(min_length=1)
    cancellation_basis_reference: str = Field(min_length=1)


class CombinedFootingAnalysisRequest(_StrictRequestModel):
    geometry: CombinedFootingGeometryRequest
    actions: CombinedFootingActionRequest


class CombinedFootingMaterialRequest(_StrictRequestModel):
    footing_concrete_grade_nmm2: Literal[20, 25, 30, 35, 40]
    column_concrete_grade_nmm2: Literal[20, 25, 30, 35, 40]
    steel_grade_nmm2: Literal[415, 500]
    uncoated_deformed_bars: StrictTrue
    material_basis_reference: str = Field(min_length=1)


class CombinedFootingReinforcementRequest(_StrictRequestModel):
    top_longitudinal_diameter_mm: Literal[8, 10, 12, 16, 20, 25, 32, 36]
    top_longitudinal_spacing_mm: float = Field(gt=0)
    bottom_longitudinal_diameter_mm: Literal[8, 10, 12, 16, 20, 25, 32, 36]
    bottom_longitudinal_spacing_mm: float = Field(gt=0)
    transverse_diameter_mm: Literal[8, 10, 12, 16, 20, 25, 32, 36]
    transverse_spacing_mm: float = Field(gt=0)
    nominal_cover_mm: float = Field(gt=0)
    aggregate_size_mm: float = Field(gt=0)
    available_top_longitudinal_anchorage_each_end_mm: float = Field(gt=0)
    available_bottom_longitudinal_anchorage_each_end_mm: float = Field(gt=0)
    available_transverse_anchorage_each_edge_mm: float = Field(gt=0)
    straight_uncoated_deformed_bars: StrictTrue
    effective_depth_basis_approved: StrictTrue
    reinforcement_schedule_approved: StrictTrue
    detailing_basis_reference: str = Field(min_length=1)


class CombinedFootingTransferRequest(_StrictRequestModel):
    effective_supporting_area_each_mm2: float = Field(gt=0)
    effective_supporting_area_basis: Literal["largest_frustum_1v_2h"]
    effective_supporting_area_approved: StrictTrue
    dowel_count_each: int = Field(gt=0)
    dowel_diameter_mm: Literal[8, 10, 12, 16, 20, 25, 32, 36]
    column_longitudinal_bar_diameter_mm: Literal[8, 10, 12, 16, 20, 25, 32, 36]
    available_dowel_development_into_footing_mm: float = Field(gt=0)
    available_dowel_development_into_column_mm: float = Field(gt=0)
    uncoated_deformed_dowels: StrictTrue
    transfer_basis_reference: str = Field(min_length=1)


class CombinedFootingDesignRequest(_StrictRequestModel):
    analysis: CombinedFootingAnalysisRequest
    material: CombinedFootingMaterialRequest
    reinforcement: CombinedFootingReinforcementRequest
    transfer: CombinedFootingTransferRequest


class SymmetricCombinedFootingRequest(_StrictRequestModel):
    """Explicit approved-basis inputs for the sole combined-footing case."""

    case_id: str = Field(min_length=1)
    footing: CombinedFootingDesignRequest
    qualified_review_required: StrictTrue


class CombinedFootingGeometryResponse(BaseModel):
    plan_area_m2: float
    footing_centroid_x_mm: float
    column_spacing_mm: float
    inter_column_clear_gap_mm: float
    equal_end_projection_mm: float
    transverse_column_face_cantilever_mm: float
    punching_critical_side_mm: float
    punching_area_each_m2: float
    punching_perimeter_each_mm: float
    rigid_uniform_pressure_eligible: bool
    source_refs: tuple[str, ...]


class CombinedFootingSectionActionResponse(BaseModel):
    kind: str
    x_mm: float
    shear_kn: float
    moment_kn_m: float
    tension_face: Literal["bottom", "top", "none"]


class CombinedFootingTransverseActionResponse(BaseModel):
    column_face_cantilever_mm: float
    moment_kn_m_per_m: float
    one_way_shear_section_from_column_face_mm: float
    one_way_shear_demand_kn_per_m: float


class CombinedFootingActionResponse(BaseModel):
    geometry: CombinedFootingGeometryResponse
    service_column_resultant_kn: float
    service_column_resultant_x_mm: float
    service_total_vertical_load_kn: float
    service_total_resultant_x_mm: float
    gross_service_pressure_kn_per_m2: float
    gross_service_bearing_utilization: float
    gross_service_bearing_within_allowable: bool
    factored_column_resultant_kn: float
    factored_column_resultant_x_mm: float
    factored_total_vertical_load_kn: float
    gross_factored_pressure_kn_per_m2: float
    net_factored_structural_pressure_kn_per_m2: float
    upward_line_load_kn_per_m: float
    service_resultant_alignment_residual_mm: float
    factored_resultant_alignment_residual_mm: float
    left_outer_one_way_shear: CombinedFootingSectionActionResponse
    left_outer_column_face: CombinedFootingSectionActionResponse
    left_inner_column_face: CombinedFootingSectionActionResponse
    left_inner_one_way_shear: CombinedFootingSectionActionResponse
    inter_column_midpoint: CombinedFootingSectionActionResponse
    right_inner_one_way_shear: CombinedFootingSectionActionResponse
    right_inner_column_face: CombinedFootingSectionActionResponse
    right_outer_column_face: CombinedFootingSectionActionResponse
    right_outer_one_way_shear: CombinedFootingSectionActionResponse
    transverse: CombinedFootingTransverseActionResponse
    vertical_equilibrium_residual_kn: float
    moment_equilibrium_residual_kn_m: float
    source_refs: tuple[str, ...]


class CombinedFootingFlexureResponse(BaseModel):
    region: str
    design_width_mm: float
    effective_depth_mm: float
    overall_depth_mm: float
    factored_moment_kn_m: float
    flexural_steel_required_mm2: float | None
    minimum_steel_ratio: float
    minimum_steel_required_mm2: float
    governing_steel_required_mm2: float | None
    provided_bar_diameter_mm: float
    provided_bar_spacing_mm: float
    provided_steel_area_mm2: float
    provided_steel_ratio_percent: float
    maximum_bar_diameter_mm: float
    maximum_bar_spacing_mm: float
    provided_clear_spacing_mm: float
    minimum_clear_spacing_mm: float
    provided_nominal_cover_mm: float
    minimum_nominal_cover_mm: float
    tension_design_bond_stress_nmm2: float
    required_tension_development_length_mm: float
    available_straight_anchorage_each_end_mm: float
    singly_reinforced_capacity_is_sufficient: bool
    reinforcement_area_is_safe: bool
    bar_diameter_is_safe: bool
    bar_spacing_is_safe: bool
    clear_spacing_is_safe: bool
    nominal_cover_is_safe: bool
    anchorage_is_safe: bool
    is_safe: bool


class CombinedFootingOneWayShearResponse(BaseModel):
    section: str
    factored_shear_demand_kn: float
    design_width_mm: float
    effective_depth_mm: float
    tension_reinforcement_area_mm2: float
    tension_reinforcement_percent: float
    table_19_lookup_reinforcement_percent: float
    nominal_shear_stress_nmm2: float
    concrete_design_shear_strength_nmm2: float
    utilization: float
    is_safe_without_shear_reinforcement: bool


class CombinedFootingPunchingResponse(BaseModel):
    column: str
    factored_column_load_kn: float
    net_factored_pressure_kn_per_m2: float
    critical_enclosed_area_m2: float
    critical_perimeter_mm: float
    effective_depth_mm: float
    factored_punching_shear_kn: float
    nominal_punching_stress_nmm2: float
    column_aspect_ratio_beta_c: float
    size_factor_ks: float
    concrete_capacity_nmm2: float
    utilization: float
    is_safe_without_punching_reinforcement: bool


class CombinedFootingLoadTransferResponse(BaseModel):
    column: str
    factored_column_load_kn: float
    loaded_area_mm2: float
    effective_supporting_area_mm2: float
    bearing_enhancement_factor: float
    actual_bearing_stress_nmm2: float
    supported_column_bearing_capacity_kn: float
    supporting_footing_bearing_capacity_kn: float
    governing_concrete_member: str
    governing_concrete_bearing_capacity_kn: float
    concrete_bearing_without_transfer_is_safe: bool
    excess_force_kn: float
    excess_transfer_steel_area_mm2: float
    minimum_transfer_steel_area_mm2: float
    required_transfer_steel_area_mm2: float
    provided_transfer_steel_area_mm2: float
    minimum_dowel_count: int
    provided_dowel_count: int
    maximum_dowel_diameter_mm: float
    provided_dowel_diameter_mm: float
    footing_compression_design_bond_stress_nmm2: float
    column_compression_design_bond_stress_nmm2: float
    required_development_into_footing_mm: float
    required_development_into_column_mm: float
    available_development_into_footing_mm: float
    available_development_into_column_mm: float
    reinforcement_area_is_safe: bool
    bar_count_is_safe: bool
    dowel_diameter_is_safe: bool
    footing_development_is_safe: bool
    column_development_is_safe: bool
    is_safe: bool


class CombinedFootingStrengthResponse(BaseModel):
    actions: CombinedFootingActionResponse
    top_longitudinal_flexure: CombinedFootingFlexureResponse
    bottom_longitudinal_flexure: CombinedFootingFlexureResponse
    transverse_flexure: CombinedFootingFlexureResponse
    longitudinal_one_way_shear: tuple[CombinedFootingOneWayShearResponse, ...]
    transverse_one_way_shear: CombinedFootingOneWayShearResponse
    punching: tuple[CombinedFootingPunchingResponse, ...]
    load_transfer: tuple[CombinedFootingLoadTransferResponse, ...]
    disposition: Literal["PASS", "FAIL"]
    reasons: tuple[str, ...]
    clause_refs: tuple[str, ...]
    source_refs: tuple[str, ...]
    limitations: tuple[str, ...]
    qualified_review_required: Literal[True]
    complete_engineering_approval: Literal[False]


class SymmetricCombinedFootingProvenanceResponse(BaseModel):
    schema_version: str
    code_edition: str
    workflow: str
    case_id: str
    benchmark_id: str
    action_generation_status: str
    soil_verification_status: str
    geometry_basis_reference: str
    rigidity_basis_reference: str
    load_basis_reference: str
    bearing_settlement_basis_reference: str
    cancellation_basis_reference: str
    material_basis_reference: str
    detailing_basis_reference: str
    transfer_basis_reference: str
    clause_refs: tuple[str, ...]
    source_refs: tuple[str, ...]


class SymmetricCombinedFootingResponse(BaseModel):
    """Typed transport projection of the composed combined-footing result."""

    case_id: str
    status: Literal["PASS", "FAIL"]
    strength: CombinedFootingStrengthResponse
    supported_case: str
    held_cases: tuple[str, ...]
    provenance: SymmetricCombinedFootingProvenanceResponse
    qualified_review_required: Literal[True]
    complete_engineering_design_approved: Literal[False]
