# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Strict grouped contracts for F1 torsion, column, and slab facades."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, StrictBool, StrictInt, model_validator

from structural_lib.services.canonical_family import FamilyIdentityV1
from structural_lib.services.contracts.common import (
    StrictPublicModel,
    complete_field_contracts_from_schema,
)

__all__ = [
    "ColumnActionsV1",
    "ColumnDesignInputV1",
    "ColumnGeometryV1",
    "ColumnMaterialsV1",
    "ColumnReinforcementV1",
    "ContinuousOneWaySlabInputV1",
    "OneWaySlabInputV1",
    "SlabMaterialsV1",
    "SlabServiceabilityEvidenceV1",
    "TorsionActionsV1",
    "TorsionDesignInputV1",
    "TorsionGeometryV1",
    "TorsionMaterialsV1",
    "TorsionReinforcementV1",
    "TwoWaySlabInputV1",
]


class TorsionGeometryV1(StrictPublicModel):
    b_mm: float = Field(gt=0)
    D_mm: float = Field(gt=0)
    d_mm: float = Field(gt=0)
    clear_cover_mm: float = Field(gt=0)


class TorsionActionsV1(StrictPublicModel):
    tu_knm: float = Field(ge=0)
    vu_kn: float = Field(ge=0)
    mu_knm: float = Field(ge=0)


class TorsionMaterialsV1(StrictPublicModel):
    fck_nmm2: float = Field(ge=15, le=40)
    fy_nmm2: float = Field(ge=250, le=500)


class TorsionReinforcementV1(StrictPublicModel):
    stirrup_diameter_mm: float = Field(gt=0)
    tension_steel_percent: float = Field(ge=0.15, le=3.0)


class TorsionDesignInputV1(StrictPublicModel):
    schema_version: Literal["torsion-design-input/v1"] = "torsion-design-input/v1"
    identity: FamilyIdentityV1
    geometry: TorsionGeometryV1
    actions: TorsionActionsV1
    materials: TorsionMaterialsV1
    reinforcement: TorsionReinforcementV1

    @model_validator(mode="after")
    def validate_geometry(self) -> Self:
        if self.geometry.d_mm >= self.geometry.D_mm:
            raise ValueError("geometry.d_mm must be less than geometry.D_mm")
        closed_core_offset = (
            self.geometry.clear_cover_mm + self.reinforcement.stirrup_diameter_mm / 2
        )
        if 2 * closed_core_offset >= min(self.geometry.b_mm, self.geometry.D_mm):
            raise ValueError(
                "cover and stirrup diameter must leave a positive closed core"
            )
        return self


class ColumnGeometryV1(StrictPublicModel):
    b_mm: float = Field(gt=0, le=2000)
    D_mm: float = Field(gt=0, le=2000)
    unsupported_length_mm: float = Field(gt=0)
    minimum_eccentricity_length_mm: float = Field(gt=0)
    end_condition: Literal[
        "FIXED_FIXED",
        "FIXED_HINGED",
        "FIXED_FIXED_SWAY",
        "FIXED_FREE",
        "HINGED_HINGED",
        "FIXED_PARTIAL",
        "HINGED_PARTIAL",
    ]
    braced: StrictBool


class ColumnActionsV1(StrictPublicModel):
    pu_kn: float = Field(ge=0)
    mux_knm: float = Field(ge=0)
    muy_knm: float = Field(ge=0)
    m1x_signed_knm: float
    m2x_signed_knm: float
    m1y_signed_knm: float
    m2y_signed_knm: float


class ColumnMaterialsV1(StrictPublicModel):
    fck_nmm2: float = Field(ge=15, le=80)
    fy_nmm2: float = Field(ge=250, le=550)


class ColumnReinforcementV1(StrictPublicModel):
    supplied_steel_area_mm2: float = Field(gt=0)
    reinforcement_centroid_depth_mm: float = Field(gt=0)


class ColumnDesignInputV1(StrictPublicModel):
    schema_version: Literal["column-supplied-steel-check-input/v1"] = (
        "column-supplied-steel-check-input/v1"
    )
    identity: FamilyIdentityV1
    geometry: ColumnGeometryV1
    actions: ColumnActionsV1
    materials: ColumnMaterialsV1
    reinforcement: ColumnReinforcementV1

    @model_validator(mode="after")
    def validate_reinforcement(self) -> Self:
        area = self.geometry.b_mm * self.geometry.D_mm
        ratio = self.reinforcement.supplied_steel_area_mm2 / area
        if not 0.008 <= ratio <= 0.04:
            raise ValueError(
                "supplied longitudinal steel must be 0.8% to 4.0% of gross area"
            )
        if (
            self.reinforcement.reinforcement_centroid_depth_mm
            >= min(self.geometry.b_mm, self.geometry.D_mm) / 2
        ):
            raise ValueError("reinforcement centroid depth must lie inside the section")
        return self


class SlabMaterialsV1(StrictPublicModel):
    fck_nmm2: float = Field(ge=20, le=40)
    fy_nmm2: Literal[250, 415, 500]


class SlabServiceabilityEvidenceV1(StrictPublicModel):
    reviewed_base_span_depth_limit: float = Field(gt=0)
    reviewed_aggregate_modification_factor: float = Field(gt=0)
    serviceability_limit_source_reference: str = Field(min_length=1)
    serviceability_limit_source_is_approved: Literal[True]
    qualified_serviceability_acceptance_reference: str = Field(min_length=1)
    qualified_serviceability_acceptance_acknowledged: Literal[True]


class OneWaySlabGeometryV1(StrictPublicModel):
    short_effective_span_mm: float = Field(gt=0)
    long_effective_span_mm: float = Field(gt=0)
    thickness_mm: float = Field(gt=0)
    effective_depth_mm: float = Field(gt=0)
    strip_width_mm: float = Field(gt=0)


class OneWaySlabActionsV1(StrictPublicModel):
    factored_area_load_kn_per_m2: float = Field(gt=0)


class OneWaySlabReinforcementV1(StrictPublicModel):
    main_bar_diameter_mm: float = Field(gt=0)
    main_bar_spacing_mm: float = Field(gt=0)
    distribution_bar_diameter_mm: float = Field(gt=0)
    distribution_bar_spacing_mm: float = Field(gt=0)


class OneWaySlabInputV1(StrictPublicModel):
    schema_version: Literal["one-way-slab-input/v1"] = "one-way-slab-input/v1"
    identity: FamilyIdentityV1
    geometry: OneWaySlabGeometryV1
    actions: OneWaySlabActionsV1
    materials: SlabMaterialsV1
    reinforcement: OneWaySlabReinforcementV1
    serviceability_evidence: SlabServiceabilityEvidenceV1


class ContinuousOneWaySlabGeometryV1(OneWaySlabGeometryV1):
    number_of_spans: StrictInt = Field(ge=3)
    maximum_span_variation_percent: float = Field(ge=0, le=15)
    uniform_cross_section_acknowledged: Literal[True]


class ContinuousOneWaySlabActionsV1(StrictPublicModel):
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
    substantially_uniform_load_acknowledged: Literal[True]
    redistribution_applied: Literal[False]


class ContinuousOneWaySlabReinforcementV1(StrictPublicModel):
    positive_bar_diameter_mm: float = Field(gt=0)
    positive_bar_spacing_mm: float = Field(gt=0)
    negative_bar_diameter_mm: float = Field(gt=0)
    negative_bar_spacing_mm: float = Field(gt=0)
    distribution_bar_diameter_mm: float = Field(gt=0)
    distribution_bar_spacing_mm: float = Field(gt=0)


class ContinuousOneWaySlabInputV1(StrictPublicModel):
    schema_version: Literal["continuous-one-way-slab-input/v1"] = (
        "continuous-one-way-slab-input/v1"
    )
    identity: FamilyIdentityV1
    geometry: ContinuousOneWaySlabGeometryV1
    actions: ContinuousOneWaySlabActionsV1
    materials: SlabMaterialsV1
    reinforcement: ContinuousOneWaySlabReinforcementV1
    serviceability_evidence: SlabServiceabilityEvidenceV1


class TwoWaySlabGeometryV1(StrictPublicModel):
    x_effective_span_mm: float = Field(gt=0)
    y_effective_span_mm: float = Field(gt=0)
    thickness_mm: float = Field(gt=0)
    d_x_mm: float = Field(gt=0)
    d_y_mm: float = Field(gt=0)
    x_min_edge: Literal["continuous", "discontinuous"]
    x_max_edge: Literal["continuous", "discontinuous"]
    y_min_edge: Literal["continuous", "discontinuous"]
    y_max_edge: Literal["continuous", "discontinuous"]
    corner_lift_condition: Literal["restrained", "free_to_lift"]


class TwoWaySlabActionsV1(StrictPublicModel):
    factored_area_load_kn_per_m2: float = Field(gt=0)


class TwoWaySlabReinforcementV1(StrictPublicModel):
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


class TwoWaySlabInputV1(StrictPublicModel):
    schema_version: Literal["two-way-slab-input/v1"] = "two-way-slab-input/v1"
    identity: FamilyIdentityV1
    geometry: TwoWaySlabGeometryV1
    actions: TwoWaySlabActionsV1
    materials: SlabMaterialsV1
    reinforcement: TwoWaySlabReinforcementV1
    serviceability_evidence: SlabServiceabilityEvidenceV1


for _request_model in (
    TorsionDesignInputV1,
    ColumnDesignInputV1,
    OneWaySlabInputV1,
    ContinuousOneWaySlabInputV1,
    TwoWaySlabInputV1,
):
    _request_model.field_contracts = complete_field_contracts_from_schema(
        _request_model
    )
