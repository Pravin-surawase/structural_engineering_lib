# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Frozen F0 facade workflow inventory used by generated public discovery."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["FAMILY_FACADE_WORKFLOWS", "FamilyFacadeWorkflowV1"]


@dataclass(frozen=True)
class FamilyFacadeWorkflowV1:
    journey_id: str
    module: str
    request_contract: str
    request_type: str
    result_contract: str
    constructor: str
    operation: str
    compatibility_owner: str
    evidence_class: str

    @property
    def cookbook_path(self) -> str:
        slug = (
            self.journey_id.removeprefix("is456.")
            .removesuffix("/v1")
            .replace(".", "-")
            .replace("/", "-")
        )
        return f"docs/cookbook/python/{slug}.md"

    @property
    def validation_contract(self) -> str:
        return "field-contract/v1"

    @property
    def error_contract(self) -> str:
        return "input-issue/v1 + structural-problem/v1"

    @property
    def consumer_contract(self) -> str:
        return "to_dict() -> finite JSON + structural-result-envelope/v2"


FAMILY_FACADE_WORKFLOWS = (
    FamilyFacadeWorkflowV1(
        "is456.beam.design/v1",
        "structural_lib.design.is456.beam",
        "beam-design-input/v1",
        "structural_lib.services.contracts.beam.BeamDesignInputV1",
        "beam-design-result/v1 + structural-result-envelope/v2",
        "input/load",
        "design",
        "structural_lib.services.canonical_beam.design",
        "independent arithmetic + wrapper parity + generated regression",
    ),
    FamilyFacadeWorkflowV1(
        "is456.torsion.design/v1",
        "structural_lib.design.is456.torsion",
        "torsion-design-input/v1",
        "structural_lib.services.contracts.family_f1.TorsionDesignInputV1",
        "family-design-result/v1 + structural-result-envelope/v2",
        "input/load",
        "design",
        "structural_lib.codes.is456.beam.torsion.design_torsion",
        "independent arithmetic + wrapper parity",
    ),
    FamilyFacadeWorkflowV1(
        "is456.column.supplied-steel-check/v1",
        "structural_lib.design.is456.column",
        "column-supplied-steel-check-input/v1",
        "structural_lib.services.contracts.family_f1.ColumnDesignInputV1",
        "family-design-result/v1 + structural-result-envelope/v2",
        "input/load",
        "design/check",
        "structural_lib.services.column_api.design_column_is456",
        "independent arithmetic + wrapper parity + generated regression",
    ),
    FamilyFacadeWorkflowV1(
        "is456.slab.one-way/v1",
        "structural_lib.design.is456.slab",
        "one-way-slab-input/v1",
        "structural_lib.services.contracts.family_f1.OneWaySlabInputV1",
        "family-design-result/v1 + structural-result-envelope/v2",
        "load_one_way",
        "design_one_way",
        "structural_lib.services.slab_api.design_complete_one_way_slab_is456",
        "independent arithmetic + wrapper parity",
    ),
    FamilyFacadeWorkflowV1(
        "is456.slab.continuous-one-way/v1",
        "structural_lib.design.is456.slab",
        "continuous-one-way-slab-input/v1",
        "structural_lib.services.contracts.family_f1.ContinuousOneWaySlabInputV1",
        "family-design-result/v1 + structural-result-envelope/v2",
        "load_continuous_one_way",
        "design_continuous_one_way",
        "structural_lib.services.slab_api.design_continuous_one_way_slab_builtin_is456",
        "normalized data + wrapper parity + generated regression",
    ),
    FamilyFacadeWorkflowV1(
        "is456.slab.two-way/v1",
        "structural_lib.design.is456.slab",
        "two-way-slab-input/v1",
        "structural_lib.services.contracts.family_f1.TwoWaySlabInputV1",
        "family-design-result/v1 + structural-result-envelope/v2",
        "load_two_way",
        "design_two_way",
        "structural_lib.services.slab_api.design_two_way_slab_panel_builtin_is456",
        "normalized data + wrapper parity + generated regression",
    ),
    FamilyFacadeWorkflowV1(
        "is456.wall.braced-axial/v1",
        "structural_lib.design.is456.wall",
        "braced-wall-input/v1",
        "structural_lib.services.contracts.family_f2.BracedWallInputV1",
        "family-design-result/v1 + structural-result-envelope/v2",
        "input/load",
        "design",
        "structural_lib.services.wall_api.design_braced_wall_is456",
        "independent arithmetic + wrapper parity",
    ),
    FamilyFacadeWorkflowV1(
        "is456.staircase.straight-flight/v1",
        "structural_lib.design.is456.staircase",
        "straight-flight-staircase-input/v1",
        "structural_lib.services.contracts.family_f2.StaircaseInputV1",
        "family-design-result/v1 + structural-result-envelope/v2",
        "input/load",
        "design",
        "structural_lib.services.staircase_api.design_straight_flight_staircase_is456",
        "independent arithmetic + wrapper parity",
    ),
    FamilyFacadeWorkflowV1(
        "is456.deep-beam.simply-supported/v1",
        "structural_lib.design.is456.deep_beam",
        "simply-supported-deep-beam-input/v1",
        "structural_lib.services.contracts.family_f2.DeepBeamInputV1",
        "family-design-result/v1 + structural-result-envelope/v2",
        "input/load",
        "design",
        "structural_lib.services.deep_beam_api.design_simply_supported_deep_beam_is456",
        "independent arithmetic + wrapper parity",
    ),
    FamilyFacadeWorkflowV1(
        "is456.flat-slab.regular-interior/v1",
        "structural_lib.design.is456.flat_slab",
        "regular-interior-flat-slab-input/v1",
        "structural_lib.services.contracts.family_f2.FlatSlabInputV1",
        "family-design-result/v1 + structural-result-envelope/v2",
        "input/load",
        "design",
        "structural_lib.services.flat_slab_api.design_regular_interior_flat_slab_is456",
        "normalized data + independent arithmetic + wrapper parity",
    ),
    FamilyFacadeWorkflowV1(
        "is456.isolated-footing.concentric/v1",
        "structural_lib.design.is456.isolated_footing",
        "concentric-isolated-footing-input/v1",
        "structural_lib.services.contracts.family_f3.IsolatedFootingInputV1",
        "family-design-result/v1 + structural-result-envelope/v2",
        "input/load",
        "design",
        "structural_lib.services.footing_api.design_concentric_isolated_footing_is456",
        "independent arithmetic + wrapper parity + generated regression",
    ),
    FamilyFacadeWorkflowV1(
        "is456.combined-footing.symmetric/v1",
        "structural_lib.design.is456.combined_footing",
        "symmetric-combined-footing-input/v1",
        "structural_lib.services.contracts.family_f3.CombinedFootingInputV1",
        "family-design-result/v1 + structural-result-envelope/v2",
        "input/load",
        "design",
        "structural_lib.services.combined_footing_api.design_symmetric_combined_footing_is456",
        "independent arithmetic + wrapper parity",
    ),
    FamilyFacadeWorkflowV1(
        "is456.strap-footing.property-line/v1",
        "structural_lib.design.is456.strap_footing",
        "property-line-strap-footing-input/v1",
        "structural_lib.services.contracts.family_f3.StrapFootingInputV1",
        "family-design-result/v1 + structural-result-envelope/v2",
        "input/load",
        "design",
        "structural_lib.services.strap_footing_api.design_property_line_strap_footing_is456",
        "independent arithmetic + wrapper parity",
    ),
)
