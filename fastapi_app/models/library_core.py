"""Requests for the bounded footing and slab public-library workflows."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, StrictInt


class FootingLoadTransferRequest(BaseModel):
    """Explicit inputs for the bounded concentric isolated-footing transfer check."""

    Pu_kN: float = Field(gt=0)
    loaded_area_A2_mm2: float = Field(gt=0)
    effective_supporting_area_A1_mm2: float = Field(gt=0)
    effective_supporting_area_basis: Literal["largest_frustum_1v_2h"]
    effective_supporting_area_is_approved: Literal[True]
    supporting_concrete_fck_nmm2: float = Field(gt=0)
    supported_concrete_fck_nmm2: float = Field(gt=0)
    steel_fy_nmm2: float = Field(gt=0)
    dowel_count: StrictInt = Field(gt=0)
    dowel_diameter_mm: float = Field(gt=0)
    column_longitudinal_bar_diameter_mm: float = Field(gt=0)
    available_dowel_development_length_into_footing_mm: float = Field(gt=0)
    available_dowel_development_length_into_supported_member_mm: float = Field(gt=0)
    dowel_bar_type: Literal["deformed", "plain"] = "deformed"


class OneWaySlabDesignRequest(BaseModel):
    """Explicit inputs for the supported simply supported one-way slab strip."""

    short_effective_span_mm: float = Field(gt=0)
    long_effective_span_mm: float = Field(gt=0)
    thickness_mm: float = Field(gt=0)
    d_mm: float = Field(gt=0)
    factored_area_load_kn_per_m2: float = Field(gt=0)
    fck_n_per_mm2: float = Field(ge=20, le=80)
    fy_n_per_mm2: Literal[250.0, 415.0, 500.0]
    main_bar_diameter_mm: float = Field(gt=0)
    main_bar_spacing_mm: float = Field(gt=0)
    distribution_bar_diameter_mm: float = Field(gt=0)
    distribution_bar_spacing_mm: float = Field(gt=0)
    strip_width_mm: float = Field(default=1000.0, gt=0)


class SlabServiceabilityCarrierRequest(BaseModel):
    """Reviewed external serviceability-limit carrier; no silent defaults."""

    reviewed_base_span_depth_limit: float = Field(gt=0)
    reviewed_aggregate_modification_factor: float = Field(gt=0)
    serviceability_limit_source_reference: str = Field(min_length=1)
    serviceability_limit_source_is_approved: Literal[True]
    qualified_serviceability_acceptance_reference: str = Field(min_length=1)
    qualified_serviceability_acceptance_acknowledged: Literal[True]


class CompleteOneWaySlabDesignRequest(
    OneWaySlabDesignRequest, SlabServiceabilityCarrierRequest
):
    """Simply supported one-way flexure/detailing plus shear/serviceability."""


class ContinuousOneWaySlabDesignRequest(SlabServiceabilityCarrierRequest):
    """Explicit continuous one-way coefficient-method request."""

    short_effective_span_mm: float = Field(gt=0)
    long_effective_span_mm: float = Field(gt=0)
    thickness_mm: float = Field(gt=0)
    d_mm: float = Field(gt=0)
    factored_area_load_kn_per_m2: float = Field(gt=0)
    fck_n_per_mm2: float = Field(ge=20, le=40)
    fy_n_per_mm2: Literal[250.0, 415.0, 500.0]
    positive_moment_coefficient: float = Field(gt=0, le=1)
    negative_moment_coefficient: float = Field(gt=0, le=1)
    shear_coefficient: float = Field(gt=0, le=1)
    coefficient_source_reference: str = Field(min_length=1)
    coefficient_source_is_approved: Literal[True]
    qualified_coefficient_acceptance_reference: str = Field(min_length=1)
    qualified_coefficient_acceptance_acknowledged: Literal[True]
    number_of_spans: StrictInt = Field(ge=3)
    maximum_span_variation_percent: float = Field(ge=0, le=15)
    uniform_cross_section_acknowledged: Literal[True]
    substantially_uniform_load_acknowledged: Literal[True]
    redistribution_applied: Literal[False]
    positive_bar_diameter_mm: float = Field(gt=0)
    positive_bar_spacing_mm: float = Field(gt=0)
    negative_bar_diameter_mm: float = Field(gt=0)
    negative_bar_spacing_mm: float = Field(gt=0)
    distribution_bar_diameter_mm: float = Field(gt=0)
    distribution_bar_spacing_mm: float = Field(gt=0)
    strip_width_mm: float = Field(default=1000.0, gt=0)


class BuiltinContinuousOneWaySlabDesignRequest(SlabServiceabilityCarrierRequest):
    """Continuous one-way request resolved from built-in Tables 12 and 13."""

    short_effective_span_mm: float = Field(gt=0)
    long_effective_span_mm: float = Field(gt=0)
    thickness_mm: float = Field(gt=0)
    d_mm: float = Field(gt=0)
    factored_dead_and_fixed_imposed_load_kn_per_m2: float = Field(ge=0)
    factored_nonfixed_imposed_load_kn_per_m2: float = Field(ge=0)
    positive_location: Literal["end_span_positive", "interior_span_positive"]
    negative_location: Literal[
        "next_to_end_support_negative", "other_interior_support_negative"
    ]
    shear_location: Literal[
        "end_support",
        "next_to_end_support_outer",
        "next_to_end_support_inner",
        "other_interior_support",
    ]
    fck_n_per_mm2: float = Field(ge=20, le=40)
    fy_n_per_mm2: Literal[250.0, 415.0, 500.0]
    number_of_spans: StrictInt = Field(ge=3)
    maximum_span_variation_percent: float = Field(ge=0, le=15)
    uniform_cross_section_acknowledged: Literal[True]
    substantially_uniform_load_acknowledged: Literal[True]
    redistribution_applied: Literal[False]
    positive_bar_diameter_mm: float = Field(gt=0)
    positive_bar_spacing_mm: float = Field(gt=0)
    negative_bar_diameter_mm: float = Field(gt=0)
    negative_bar_spacing_mm: float = Field(gt=0)
    distribution_bar_diameter_mm: float = Field(gt=0)
    distribution_bar_spacing_mm: float = Field(gt=0)
    strip_width_mm: float = Field(default=1000.0, gt=0)


EdgeContinuity = Literal["continuous", "discontinuous"]
TopologyKind = Literal[
    "four_edges_continuous",
    "one_edge_discontinuous",
    "two_adjacent_edges_discontinuous",
    "two_opposite_edges_discontinuous",
    "three_edges_discontinuous",
    "four_edges_discontinuous_restrained",
    "simply_supported_corners_free",
]


class TwoWaySlabPanelDesignRequest(SlabServiceabilityCarrierRequest):
    """Common oriented two-way panel with reviewed external coefficients."""

    x_effective_span_mm: float = Field(gt=0)
    y_effective_span_mm: float = Field(gt=0)
    thickness_mm: float = Field(gt=0)
    x_min_edge: EdgeContinuity
    x_max_edge: EdgeContinuity
    y_min_edge: EdgeContinuity
    y_max_edge: EdgeContinuity
    corner_lift_condition: Literal["restrained", "free_to_lift"]
    support_topology_kind: TopologyKind
    alpha_x_negative: float = Field(ge=0, le=1)
    alpha_x_positive: float = Field(gt=0, le=1)
    alpha_y_negative: float = Field(ge=0, le=1)
    alpha_y_positive: float = Field(gt=0, le=1)
    coefficient_source_reference: str = Field(min_length=1)
    coefficient_source_is_approved: Literal[True]
    qualified_coefficient_acceptance_reference: str = Field(min_length=1)
    qualified_coefficient_acceptance_acknowledged: Literal[True]
    factored_area_load_kn_per_m2: float = Field(gt=0)
    d_x_mm: float = Field(gt=0)
    d_y_mm: float = Field(gt=0)
    fck_n_per_mm2: float = Field(ge=20, le=40)
    fy_n_per_mm2: Literal[250.0, 415.0, 500.0]
    x_positive_bar_diameter_mm: float = Field(gt=0)
    x_positive_bar_spacing_mm: float = Field(gt=0)
    x_negative_bar_diameter_mm: float = Field(gt=0)
    x_negative_bar_spacing_mm: float = Field(gt=0)
    y_positive_bar_diameter_mm: float = Field(gt=0)
    y_positive_bar_spacing_mm: float = Field(gt=0)
    y_negative_bar_diameter_mm: float = Field(gt=0)
    y_negative_bar_spacing_mm: float = Field(gt=0)
    edge_strip_bar_diameter_mm: float = Field(gt=0)
    edge_strip_bar_spacing_mm: float = Field(gt=0)
    torsion_bar_diameter_mm: float = Field(gt=0)
    torsion_bar_spacing_mm: float = Field(gt=0)


class BuiltinTwoWaySlabPanelDesignRequest(SlabServiceabilityCarrierRequest):
    """Two-way request resolved from built-in Table 26 or 27."""

    x_effective_span_mm: float = Field(gt=0)
    y_effective_span_mm: float = Field(gt=0)
    thickness_mm: float = Field(gt=0)
    x_min_edge: EdgeContinuity
    x_max_edge: EdgeContinuity
    y_min_edge: EdgeContinuity
    y_max_edge: EdgeContinuity
    corner_lift_condition: Literal["restrained", "free_to_lift"]
    factored_area_load_kn_per_m2: float = Field(gt=0)
    d_x_mm: float = Field(gt=0)
    d_y_mm: float = Field(gt=0)
    fck_n_per_mm2: float = Field(ge=20, le=40)
    fy_n_per_mm2: Literal[250.0, 415.0, 500.0]
    x_positive_bar_diameter_mm: float = Field(gt=0)
    x_positive_bar_spacing_mm: float = Field(gt=0)
    x_negative_bar_diameter_mm: float = Field(gt=0)
    x_negative_bar_spacing_mm: float = Field(gt=0)
    y_positive_bar_diameter_mm: float = Field(gt=0)
    y_positive_bar_spacing_mm: float = Field(gt=0)
    y_negative_bar_diameter_mm: float = Field(gt=0)
    y_negative_bar_spacing_mm: float = Field(gt=0)
    edge_strip_bar_diameter_mm: float = Field(gt=0)
    edge_strip_bar_spacing_mm: float = Field(gt=0)
    torsion_bar_diameter_mm: float = Field(gt=0)
    torsion_bar_spacing_mm: float = Field(gt=0)


class FootingLoadTransferResponse(BaseModel):
    """Bounded isolated-footing bearing and dowel-transfer result."""

    source_ids: tuple[str, str]
    source_notes: tuple[str, str]
    clause_refs: tuple[str, str, str, str, str]
    supported_case: str
    exclusions: tuple[str, ...]
    units: dict[str, str]
    limits: dict[str, float | int | str]
    Pu_kN: float
    loaded_area_A2_mm2: float
    effective_supporting_area_A1_mm2: float
    effective_supporting_area_basis: str
    bearing_enhancement_factor: float
    actual_bearing_stress_nmm2: float
    supported_concrete_bearing_capacity_kN: float
    supporting_concrete_bearing_capacity_kN: float
    governing_concrete_member: str
    governing_concrete_bearing_capacity_kN: float
    concrete_bearing_without_transfer_is_safe: bool
    excess_force_kN: float
    excess_transfer_steel_area_mm2: float
    minimum_transfer_steel_area_mm2: float
    required_transfer_steel_area_mm2: float
    provided_transfer_steel_area_mm2: float
    transfer_steel_capacity_kN: float
    minimum_bar_count: int
    provided_bar_count: int
    maximum_dowel_diameter_mm: float
    provided_dowel_diameter_mm: float
    supporting_concrete_design_bond_stress_nmm2: float
    supported_concrete_design_bond_stress_nmm2: float
    required_dowel_development_length_into_footing_mm: float
    required_dowel_development_length_into_supported_member_mm: float
    available_dowel_development_length_into_footing_mm: float
    available_dowel_development_length_into_supported_member_mm: float
    reinforcement_area_is_safe: bool
    bar_count_is_safe: bool
    dowel_diameter_is_safe: bool
    footing_development_length_is_safe: bool
    supported_member_development_length_is_safe: bool
    development_lengths_are_safe: bool
    is_safe: bool
    reasons: tuple[str, ...]


class SlabGeometryResponse(BaseModel):
    """Normalized one-way slab geometry used by the service."""

    span_a_effective_mm: float
    span_b_effective_mm: float
    thickness_mm: float
    strip_width_mm: float | None


class OneWaySlabFlexureInputResponse(BaseModel):
    """Inputs retained with a one-way slab flexure result."""

    geometry: SlabGeometryResponse
    d_mm: float
    factored_area_load_kn_per_m2: float
    fck_n_per_mm2: float
    fy_n_per_mm2: float


class SlabGoverningCheckResponse(BaseModel):
    """One explicit flexure or detailing comparison."""

    check_id: str
    actual: float
    limit: float
    unit: str
    comparison: str
    passed: bool | None = None


class OneWaySlabFlexureResponse(BaseModel):
    """Bounded one-way slab flexure result."""

    input: OneWaySlabFlexureInputResponse
    effective_short_span_mm: float
    design_strip_width_mm: float
    line_load_kn_per_m: float
    factored_moment_knm: float
    ast_required_mm2: float
    neutral_axis_depth_mm: float
    limiting_moment_knm: float
    governing_checks: list[SlabGoverningCheckResponse]
    status: str
    limitations: list[str]
    source_refs: list[str]


class OneWaySlabDetailingInputResponse(BaseModel):
    """Inputs retained with a one-way slab detailing result."""

    flexure_result: OneWaySlabFlexureResponse
    main_bar_diameter_mm: float
    main_bar_spacing_mm: float
    distribution_bar_diameter_mm: float
    distribution_bar_spacing_mm: float


class OneWaySlabDetailingResponse(BaseModel):
    """Provided-bar checks and the serviceability review boundary."""

    input: OneWaySlabDetailingInputResponse
    minimum_reinforcement_ratio: float
    minimum_reinforcement_mm2: float
    main_reinforcement_required_mm2: float
    distribution_reinforcement_required_mm2: float
    main_reinforcement_provided_mm2: float
    distribution_reinforcement_provided_mm2: float
    maximum_bar_diameter_mm: float
    maximum_main_spacing_mm: float
    maximum_distribution_spacing_mm: float
    basic_span_to_depth_ratio: float
    basic_span_to_depth_limit: float
    governing_checks: list[SlabGoverningCheckResponse]
    detailing_adequacy: str
    serviceability_status: str
    review_requirement: str
    limitations: list[str]
    source_refs: list[str]


class OneWaySlabDesignResponse(BaseModel):
    """Complete bounded one-way slab flexure and detailing response."""

    flexure: OneWaySlabFlexureResponse
    detailing: OneWaySlabDetailingResponse


class CompleteOneWaySlabDesignResponse(BaseModel):
    reinforcement: dict[str, Any]
    shear: dict[str, Any]
    serviceability: dict[str, Any]
    punching_shear_disposition: str
    complete_engineering_design_approved: bool


class ContinuousOneWaySlabDesignResponse(BaseModel):
    flexure: dict[str, Any]
    positive_reinforcement: dict[str, Any]
    negative_reinforcement: dict[str, Any]
    distribution_reinforcement: dict[str, Any]
    shear: dict[str, Any]
    serviceability: dict[str, Any]
    punching_shear_disposition: str
    complete_engineering_design_approved: bool


class TwoWaySlabPanelDesignResponse(BaseModel):
    panel: dict[str, Any]
    serviceability: dict[str, Any]
    complete_engineering_design_approved: bool
