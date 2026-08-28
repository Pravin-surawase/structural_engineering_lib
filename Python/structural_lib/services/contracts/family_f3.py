# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Strict grouped contracts for the three bounded F3 footing facades."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, StrictInt

from structural_lib.services.canonical_family import FamilyIdentityV1
from structural_lib.services.contracts.common import (
    StrictPublicModel,
    complete_field_contracts_from_schema,
)

__all__ = [
    "CombinedFootingInputV1",
    "IsolatedFootingInputV1",
    "StrapFootingInputV1",
]


class IsolatedIdentitySourceV1(StrictPublicModel):
    identity: FamilyIdentityV1
    service_load_combination_id: str = Field(min_length=1)
    service_load_basis: Literal["includes_footing_self_weight_and_overburden"]
    service_load_origin: Literal["provided", "assumed", "verified"]
    factored_load_combination_id: str = Field(min_length=1)
    allowable_soil_pressure_source_reference: str = Field(min_length=1)
    allowable_soil_pressure_origin: Literal["provided", "assumed", "verified"]


class IsolatedGeometryTopologyV1(StrictPublicModel):
    footing_type: Literal["ISOLATED_SQUARE", "ISOLATED_RECTANGULAR"]
    column_length_mm: float = Field(gt=0)
    column_width_mm: float = Field(gt=0)
    minimum_overall_thickness_mm: float = Field(ge=150)
    maximum_overall_thickness_mm: float = Field(ge=150)
    thickness_increment_mm: float = Field(gt=0)
    effective_depth_offset_length_mm: float = Field(gt=0)
    effective_depth_offset_width_mm: float = Field(gt=0)


class IsolatedActionsV1(StrictPublicModel):
    service_axial_load_kn: float = Field(gt=0)
    factored_axial_load_kn: float = Field(gt=0)
    allowable_soil_pressure_kpa: float = Field(gt=0)


class IsolatedMaterialsReinforcementV1(StrictPublicModel):
    footing_concrete_fck_nmm2: float = Field(gt=0)
    column_concrete_fck_nmm2: float = Field(gt=0)
    steel_fy_nmm2: float = Field(gt=0)
    dowel_count: StrictInt = Field(gt=0)
    dowel_diameter_mm: float = Field(gt=0)
    column_longitudinal_bar_diameter_mm: float = Field(gt=0)
    available_dowel_development_length_into_footing_mm: float = Field(gt=0)
    available_dowel_development_length_into_column_mm: float = Field(gt=0)
    dowel_bar_type: Literal["deformed", "plain"]
    nominal_cover_mm: float = Field(gt=0)
    nominal_max_aggregate_size_mm: float = Field(gt=0)
    lower_bottom_bar_direction: Literal["L", "B"]
    upper_bottom_bar_direction: Literal["L", "B"]
    permitted_bottom_bar_diameters_mm: list[StrictInt] = Field(min_length=1)
    footing_bottom_bar_type: Literal["deformed", "plain"]
    bottom_bar_end_arrangement: Literal[
        "straight", "bend_90", "u_hook_180", "bend_135", "mechanical"
    ]


class IsolatedEvidenceReviewV1(StrictPublicModel):
    allowable_soil_pressure_is_externally_approved: Literal[True]
    effective_supporting_area_mm2: float = Field(gt=0)
    effective_supporting_area_basis: Literal["largest_frustum_1v_2h"]
    effective_supporting_area_origin: Literal["provided", "assumed", "verified"]
    effective_supporting_area_is_approved: Literal[True]
    cover_exposure_basis: str = Field(min_length=1)
    cover_exposure_basis_is_approved: Literal[True]
    qualified_review_required: Literal[True]


class IsolatedFootingInputV1(StrictPublicModel):
    schema_version: Literal["concentric-isolated-footing-input/v1"] = (
        "concentric-isolated-footing-input/v1"
    )
    identity_source: IsolatedIdentitySourceV1
    geometry_topology: IsolatedGeometryTopologyV1
    actions: IsolatedActionsV1
    materials_reinforcement: IsolatedMaterialsReinforcementV1
    evidence_review: IsolatedEvidenceReviewV1

    @property
    def identity(self) -> FamilyIdentityV1:
        return self.identity_source.identity


class CombinedGeometryTopologyV1(StrictPublicModel):
    footing_length_mm: float = Field(gt=0)
    footing_width_mm: float = Field(gt=0)
    overall_depth_mm: float = Field(ge=150)
    effective_depth_mm: float = Field(gt=0)
    column_side_mm: float = Field(gt=0)
    left_column_center_x_mm: float = Field(gt=0)
    right_column_center_x_mm: float = Field(gt=0)
    column_count: Literal[2]
    columns_identical: Literal[True]
    columns_square: Literal[True]
    columns_centered_across_width: Literal[True]
    foundation_on_soil: Literal[True]
    constant_depth: Literal[True]
    openings_present: Literal[False]
    pedestals_present: Literal[False]
    analysis_method: Literal["conventional_rigid"]
    pressure_model: Literal["uniform"]
    rigid_footing_verified: Literal[True]


class CombinedActionsV1(StrictPublicModel):
    service_axial_load_each_kn: float = Field(gt=0)
    factored_axial_load_each_kn: float = Field(gt=0)
    service_uniform_carrier_kn_per_m2: float = Field(gt=0)
    factored_uniform_carrier_kn_per_m2: float = Field(gt=0)
    allowable_gross_bearing_pressure_kn_per_m2: float = Field(gt=0)
    load_combination_approved: Literal[True]
    bearing_and_settlement_approved: Literal[True]
    pressure_uniformity_approved: Literal[True]
    distributed_carrier_cancellation_approved: Literal[True]
    column_moments_present: Literal[False]
    horizontal_actions_present: Literal[False]
    uplift_or_load_reversal_present: Literal[False]


class CombinedMaterialsReinforcementV1(StrictPublicModel):
    footing_concrete_grade_nmm2: Literal[20, 25, 30, 35, 40]
    column_concrete_grade_nmm2: Literal[20, 25, 30, 35, 40]
    steel_grade_nmm2: Literal[415, 500]
    uncoated_deformed_bars: Literal[True]
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
    straight_uncoated_deformed_bars: Literal[True]
    effective_depth_basis_approved: Literal[True]
    reinforcement_schedule_approved: Literal[True]
    effective_supporting_area_each_mm2: float = Field(gt=0)
    effective_supporting_area_basis: Literal["largest_frustum_1v_2h"]
    effective_supporting_area_approved: Literal[True]
    dowel_count_each: StrictInt = Field(gt=0)
    dowel_diameter_mm: Literal[8, 10, 12, 16, 20, 25, 32, 36]
    column_longitudinal_bar_diameter_mm: Literal[8, 10, 12, 16, 20, 25, 32, 36]
    available_dowel_development_into_footing_mm: float = Field(gt=0)
    available_dowel_development_into_column_mm: float = Field(gt=0)
    uncoated_deformed_dowels: Literal[True]


class CombinedIdentitySourceV1(StrictPublicModel):
    identity: FamilyIdentityV1
    geometry_basis_reference: str = Field(min_length=1)
    rigidity_basis_reference: str = Field(min_length=1)
    load_basis_reference: str = Field(min_length=1)
    bearing_settlement_basis_reference: str = Field(min_length=1)
    cancellation_basis_reference: str = Field(min_length=1)
    material_basis_reference: str = Field(min_length=1)


class CombinedEvidenceReviewV1(StrictPublicModel):
    detailing_basis_reference: str = Field(min_length=1)
    transfer_basis_reference: str = Field(min_length=1)
    qualified_review_required: Literal[True]


class CombinedFootingInputV1(StrictPublicModel):
    schema_version: Literal["symmetric-combined-footing-input/v1"] = (
        "symmetric-combined-footing-input/v1"
    )
    identity_source: CombinedIdentitySourceV1
    geometry_topology: CombinedGeometryTopologyV1
    actions: CombinedActionsV1
    materials_reinforcement: CombinedMaterialsReinforcementV1
    evidence_review: CombinedEvidenceReviewV1

    @property
    def identity(self) -> FamilyIdentityV1:
        return self.identity_source.identity


class StrapIdentitySourceV1(StrictPublicModel):
    identity: FamilyIdentityV1
    geometry_basis_reference: str = Field(min_length=1)
    rigidity_basis_reference: str = Field(min_length=1)
    strap_isolation_basis_reference: str = Field(min_length=1)
    load_basis_reference: str = Field(min_length=1)
    bearing_settlement_basis_reference: str = Field(min_length=1)
    footing_carrier_basis_reference: str = Field(min_length=1)
    strap_line_load_basis_reference: str = Field(min_length=1)
    load_pattern_basis_reference: str = Field(min_length=1)
    material_basis_reference: str = Field(min_length=1)


class StrapGeometryTopologyV1(StrictPublicModel):
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
    footings_rectangular: Literal[True]
    footings_parallel: Literal[True]
    footings_constant_depth: Literal[True]
    columns_square: Literal[True]
    columns_and_strap_share_centerline: Literal[True]
    interior_column_centered_on_footing: Literal[True]
    strap_straight_and_prismatic: Literal[True]
    strap_centered_across_footings: Literal[True]
    foundation_on_soil: Literal[True]
    strap_soil_contact: Literal[False]
    openings_present: Literal[False]
    pedestals_present: Literal[False]
    analysis_method: Literal["rigid_equal_pressure"]
    pressure_model: Literal["equal_uniform_net"]


class StrapActionsV1(StrictPublicModel):
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
    load_combination_approved: Literal[True]
    bearing_and_settlement_approved: Literal[True]
    equal_uniform_pressure_approved: Literal[True]
    footing_carrier_basis_approved: Literal[True]
    strap_line_load_basis_approved: Literal[True]
    load_pattern_compatible: Literal[True]
    column_moments_present: Literal[False]
    horizontal_actions_present: Literal[False]
    uplift_or_load_reversal_present: Literal[False]
    independently_factored_or_patterned_actions_present: Literal[False]


class StrapMaterialsReinforcementV1(StrictPublicModel):
    strap_concrete_grade_nmm2: Literal[20, 25, 30, 35, 40]
    steel_grade_nmm2: Literal[415, 500]
    uncoated_deformed_bars: Literal[True]
    top_bar_count: StrictInt = Field(ge=2)
    top_bar_diameter_mm: Literal[8, 10, 12, 16, 20, 25, 32, 36]
    bottom_bar_count: StrictInt = Field(ge=2)
    bottom_bar_diameter_mm: Literal[8, 10, 12, 16, 20, 25, 32, 36]
    side_face_bar_count_each_face: StrictInt = Field(ge=2)
    side_face_bar_diameter_mm: Literal[8, 10, 12, 16, 20, 25, 32, 36]
    side_face_vertical_spacing_mm: float = Field(gt=0)
    stirrup_leg_count: StrictInt = Field(ge=2)
    stirrup_diameter_mm: Literal[8, 10, 12, 16, 20, 25, 32, 36]
    stirrup_spacing_mm: float = Field(gt=0)
    nominal_cover_mm: float = Field(gt=0)
    required_nominal_cover_mm: float = Field(gt=0)
    maximum_aggregate_size_mm: float = Field(gt=0)
    available_top_anchorage_exterior_mm: float = Field(gt=0)
    available_top_anchorage_interior_mm: float = Field(gt=0)
    available_bottom_anchorage_exterior_mm: float = Field(gt=0)
    available_bottom_anchorage_interior_mm: float = Field(gt=0)
    vertical_closed_stirrups: Literal[True]
    straight_anchorage: Literal[True]
    bars_bundled: Literal[False]
    bars_spliced: Literal[False]
    bars_curtailed: Literal[False]
    reinforcement_schedule_approved: Literal[True]
    effective_depth_basis_approved: Literal[True]
    durability_cover_basis_approved: Literal[True]


class StrapEvidenceReviewV1(StrictPublicModel):
    exterior_footing_design_verified: Literal[True]
    interior_footing_design_verified: Literal[True]
    column_and_strap_transfer_verified: Literal[True]
    footing_reinforcement_and_anchorage_verified: Literal[True]
    supporting_areas_verified: Literal[True]
    construction_clearances_verified: Literal[True]
    exterior_footing_verification_reference: str = Field(min_length=1)
    interior_footing_verification_reference: str = Field(min_length=1)
    transfer_verification_reference: str = Field(min_length=1)
    construction_verification_reference: str = Field(min_length=1)
    detailing_basis_reference: str = Field(min_length=1)
    durability_basis_reference: str = Field(min_length=1)
    qualified_review_required: Literal[True]


class StrapFootingInputV1(StrictPublicModel):
    schema_version: Literal["property-line-strap-footing-input/v1"] = (
        "property-line-strap-footing-input/v1"
    )
    identity_source: StrapIdentitySourceV1
    geometry_topology: StrapGeometryTopologyV1
    actions: StrapActionsV1
    materials_reinforcement: StrapMaterialsReinforcementV1
    evidence_review: StrapEvidenceReviewV1

    @property
    def identity(self) -> FamilyIdentityV1:
        return self.identity_source.identity


for _request_model in (
    IsolatedFootingInputV1,
    CombinedFootingInputV1,
    StrapFootingInputV1,
):
    _request_model.field_contracts = complete_field_contracts_from_schema(
        _request_model
    )
