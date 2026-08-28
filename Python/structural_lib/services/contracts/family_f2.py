# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Strict five-group contracts for evidence-heavy F2 family facades."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, StrictBool, StrictInt

from structural_lib.services.canonical_family import FamilyIdentityV1
from structural_lib.services.contracts.common import (
    StrictPublicModel,
    complete_field_contracts_from_schema,
)

__all__ = [
    "BracedWallInputV1",
    "DeepBeamInputV1",
    "FlatSlabInputV1",
    "StaircaseInputV1",
]


class WallIdentitySourceV1(StrictPublicModel):
    identity: FamilyIdentityV1
    bracing_basis_reference: str = Field(min_length=1)


class WallGeometryTopologyV1(StrictPublicModel):
    unsupported_height_mm: float = Field(gt=0)
    lateral_restraint_spacing_mm: float = Field(gt=0)
    wall_length_mm: float = Field(gt=0)
    wall_thickness_mm: float = Field(ge=100, le=200)
    rotation_restraint: Literal["restrained_both_ends", "not_restrained_both_ends"]
    bracing_elements_in_two_directions: Literal[True]
    lateral_forces_resisted_by_bracing_system: Literal[True]
    diaphragm_transfer_confirmed: Literal[True]
    lateral_connection_capacity_confirmed: Literal[True]


class WallActionsV1(StrictPublicModel):
    factored_axial_load_kn: float = Field(gt=0)
    supplied_eccentricity_mm: float = Field(ge=0)
    action_basis_reference: str = Field(min_length=1)


class WallMaterialsReinforcementV1(StrictPublicModel):
    concrete_grade_nmm2: Literal[20, 25, 30, 35, 40, 45, 50, 55, 60]
    vertical_bar_diameter_mm: float = Field(gt=0)
    vertical_bar_spacing_mm: float = Field(gt=0)
    horizontal_bar_diameter_mm: float = Field(gt=0)
    horizontal_bar_spacing_mm: float = Field(gt=0)
    reinforcement_kind: Literal[
        "deformed_415_or_greater", "other_bars", "welded_wire_fabric"
    ]


class WallEvidenceReviewV1(StrictPublicModel):
    reinforcement_basis_reference: str = Field(min_length=1)
    qualified_review_required: Literal[True]


class BracedWallInputV1(StrictPublicModel):
    schema_version: Literal["braced-wall-input/v1"] = "braced-wall-input/v1"
    identity_source: WallIdentitySourceV1
    geometry_topology: WallGeometryTopologyV1
    actions: WallActionsV1
    materials_reinforcement: WallMaterialsReinforcementV1
    evidence_review: WallEvidenceReviewV1

    @property
    def identity(self) -> FamilyIdentityV1:
        return self.identity_source.identity


class StairIdentitySourceV1(StrictPublicModel):
    identity: FamilyIdentityV1
    load_basis_reference: str = Field(min_length=1)


class StairGeometryTopologyV1(StrictPublicModel):
    lower_landing_effective_length_mm: float = Field(gt=0)
    going_mm: float = Field(gt=0)
    upper_landing_effective_length_mm: float = Field(gt=0)
    flight_width_mm: float = Field(gt=0)
    riser_mm: float = Field(gt=0)
    tread_mm: float = Field(gt=0)
    waist_thickness_mm: float = Field(gt=0)
    landing_thickness_mm: float = Field(gt=0)
    support_case: Literal["landings_span_with_flight"]
    span_direction: Literal["longitudinal"]
    landings_collinear: Literal[True]
    has_stringer_beams: Literal[False]
    is_cast_in_situ_solid: Literal[True]


class StairActionsV1(StrictPublicModel):
    lower_landing_superimposed_service_load_kn_per_m2: float = Field(ge=0)
    flight_superimposed_service_load_kn_per_m2: float = Field(ge=0)
    upper_landing_superimposed_service_load_kn_per_m2: float = Field(ge=0)
    lower_landing_load_share: float = Field(gt=0, le=1)
    upper_landing_load_share: float = Field(gt=0, le=1)
    concrete_unit_weight_kn_per_m3: float = Field(gt=0)
    ultimate_load_factor: float = Field(gt=0)


class StairMaterialsReinforcementV1(StrictPublicModel):
    effective_depth_mm: float = Field(gt=0)
    fck_nmm2: float = Field(ge=20, le=40)
    fy_nmm2: Literal[250, 415, 500]
    main_bar_diameter_mm: float = Field(gt=0)
    main_bar_spacing_mm: float = Field(gt=0)
    distribution_bar_diameter_mm: float = Field(gt=0)
    distribution_bar_spacing_mm: float = Field(gt=0)


class StairEvidenceReviewV1(StrictPublicModel):
    qualified_review_required: Literal[True]


class StaircaseInputV1(StrictPublicModel):
    schema_version: Literal["straight-flight-staircase-input/v1"] = (
        "straight-flight-staircase-input/v1"
    )
    identity_source: StairIdentitySourceV1
    geometry_topology: StairGeometryTopologyV1
    actions: StairActionsV1
    materials_reinforcement: StairMaterialsReinforcementV1
    evidence_review: StairEvidenceReviewV1

    @property
    def identity(self) -> FamilyIdentityV1:
        return self.identity_source.identity


class DeepIdentitySourceV1(StrictPublicModel):
    identity: FamilyIdentityV1
    geometry_basis_reference: str = Field(min_length=1)


class DeepGeometryTopologyV1(StrictPublicModel):
    centre_to_centre_span_mm: float = Field(gt=0)
    clear_span_mm: float = Field(gt=0)
    overall_depth_mm: float = Field(gt=0)
    beam_width_mm: float = Field(gt=0)
    support_type: Literal["simply_supported"]
    solid_rectangular_section: Literal[True]
    openings_present: Literal[False]
    dapped_ends_present: Literal[False]
    top_loaded: Literal[True]
    hanging_action_required: Literal[False]


class DeepActionsV1(StrictPublicModel):
    factored_positive_moment_knm: float = Field(gt=0)
    action_basis_reference: str = Field(min_length=1)


class DeepMaterialsReinforcementV1(StrictPublicModel):
    concrete_grade_nmm2: Literal[20, 25, 30, 35, 40, 45, 50, 55, 60]
    steel_grade_nmm2: Literal[415, 500]
    main_bar_count: StrictInt = Field(gt=0)
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


class DeepEvidenceReviewV1(StrictPublicModel):
    bearing_nodal_zone_verified: Literal[True]
    bearing_nodal_zone_reference: str = Field(min_length=1)
    reinforcement_basis_reference: str = Field(min_length=1)
    qualified_review_required: Literal[True]


class DeepBeamInputV1(StrictPublicModel):
    schema_version: Literal["simply-supported-deep-beam-input/v1"] = (
        "simply-supported-deep-beam-input/v1"
    )
    identity_source: DeepIdentitySourceV1
    geometry_topology: DeepGeometryTopologyV1
    actions: DeepActionsV1
    materials_reinforcement: DeepMaterialsReinforcementV1
    evidence_review: DeepEvidenceReviewV1

    @property
    def identity(self) -> FamilyIdentityV1:
        return self.identity_source.identity


class FlatIdentitySourceV1(StrictPublicModel):
    identity: FamilyIdentityV1
    geometry_basis_reference: str = Field(min_length=1)
    material_basis_reference: str = Field(min_length=1)
    load_basis_reference: str = Field(min_length=1)


class FlatGeometryTopologyV1(StrictPublicModel):
    centre_to_centre_span_x_mm: float = Field(gt=0)
    centre_to_centre_span_y_mm: float = Field(gt=0)
    continuous_span_count_x: StrictInt = Field(ge=3)
    continuous_span_count_y: StrictInt = Field(ge=3)
    column_width_x_mm: float = Field(gt=0)
    column_width_y_mm: float = Field(gt=0)
    overall_depth_mm: float = Field(ge=125)
    conservative_effective_depth_mm: float = Field(gt=0)
    analysis_method: Literal["direct_design"]
    panel_location: Literal["interior"]
    all_spans_equal_x: Literal[True]
    all_spans_equal_y: Literal[True]
    columns_offset_from_grid: Literal[False]
    solid_slab: Literal[True]
    drop_present: Literal[False]
    column_head_present: Literal[False]
    marginal_beam_or_wall_present: Literal[False]
    openings_present: Literal[False]


class FlatActionsV1(StrictPublicModel):
    service_dead_load_kn_per_m2: float = Field(gt=0)
    service_live_load_kn_per_m2: float = Field(gt=0)
    factored_uniform_load_kn_per_m2: float = Field(gt=0)
    factored_support_reaction_kn: float = Field(gt=0)
    self_weight_included: Literal[True]
    identical_full_loading_on_represented_panels: Literal[True]
    patterned_loading_required: Literal[False]
    unbalanced_or_lateral_moment_transfer_present: Literal[False]
    load_combination_approved: Literal[True]


class FlatProvidedBarsV1(StrictPublicModel):
    diameter_mm: float = Field(gt=0)
    spacing_mm: float = Field(gt=0)


class FlatDirectionReinforcementV1(StrictPublicModel):
    column_strip_negative_bars: FlatProvidedBarsV1
    column_strip_positive_bars: FlatProvidedBarsV1
    middle_strip_negative_bars: FlatProvidedBarsV1
    middle_strip_positive_bars: FlatProvidedBarsV1
    support_top_extension_from_face_mm: float = Field(gt=0)


class FlatMaterialsReinforcementV1(StrictPublicModel):
    concrete_grade_nmm2: Literal[20, 25, 30, 35, 40, 45, 50, 55, 60]
    steel_grade_nmm2: Literal[415, 500]
    uncoated_deformed_bars: Literal[True]
    x: FlatDirectionReinforcementV1
    y: FlatDirectionReinforcementV1


class FlatEvidenceReviewV1(StrictPublicModel):
    straight_bars_only: Literal[True]
    all_bottom_bars_continuous: Literal[True]
    splices_present: Literal[False]
    serviceability_acceptance_acknowledged: Literal[True]
    centred_concentric_reaction: Literal[True]
    full_critical_perimeter_available: Literal[True]
    no_punching_reinforcement_provided: Literal[True]
    qualified_review_required: Literal[True]
    detailing_basis_reference: str = Field(min_length=1)
    serviceability_acceptance_reference: str = Field(min_length=1)
    support_reaction_basis_reference: str = Field(min_length=1)
    punching_basis_reference: str = Field(min_length=1)


class FlatSlabInputV1(StrictPublicModel):
    schema_version: Literal["regular-interior-flat-slab-input/v1"] = (
        "regular-interior-flat-slab-input/v1"
    )
    identity_source: FlatIdentitySourceV1
    geometry_topology: FlatGeometryTopologyV1
    actions: FlatActionsV1
    materials_reinforcement: FlatMaterialsReinforcementV1
    evidence_review: FlatEvidenceReviewV1

    @property
    def identity(self) -> FamilyIdentityV1:
        return self.identity_source.identity


for _request_model in (
    BracedWallInputV1,
    StaircaseInputV1,
    DeepBeamInputV1,
    FlatSlabInputV1,
):
    _request_model.field_contracts = complete_field_contracts_from_schema(
        _request_model
    )
