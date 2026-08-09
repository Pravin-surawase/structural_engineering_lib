"""Requests for the bounded footing and slab public-library workflows."""

from __future__ import annotations

from typing import Literal

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
