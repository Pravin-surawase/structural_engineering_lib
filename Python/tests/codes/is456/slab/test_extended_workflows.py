# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Benchmarks and fail-closed contracts for the completed solid-slab workflows."""

from __future__ import annotations

import pytest

from structural_lib.codes.is456.slab.models import (
    SlabCapacityFailureResult,
    SlabContractError,
)
from structural_lib.codes.is456.slab.one_way import OneWaySlabFlexureStatus
from structural_lib.codes.is456.slab.serviceability import (
    SlabServiceabilityInput,
)
from structural_lib.codes.is456.slab.shear import slab_depth_shear_factor
from structural_lib.codes.is456.slab.topology import (
    CornerLiftCondition,
    CornerTorsionClass,
    OrientedSlabPanelGeometry,
    SlabCorner,
    SlabEdgeContinuity,
    SlabSupportTopology,
    SlabSupportTopologyKind,
)
from structural_lib.core.result_contract import EngineeringStatus
from structural_lib.services.slab_api import (
    design_complete_one_way_slab_is456,
    design_continuous_one_way_slab_is456,
    design_two_way_slab_panel_is456,
)


def _continuous_b02(**overrides: object):
    values: dict[str, object] = {
        "short_effective_span_mm": 3000,
        "long_effective_span_mm": 7500,
        "thickness_mm": 140,
        "d_mm": 115,
        "factored_area_load_kn_per_m2": 14.25,
        "fck_n_per_mm2": 20,
        "fy_n_per_mm2": 415,
        "positive_moment_coefficient": 1 / 12,
        "negative_moment_coefficient": 1 / 10,
        "shear_coefficient": 0.4,
        "coefficient_source_reference": "NPTEL-L18-B02",
        "coefficient_source_is_approved": True,
        "qualified_coefficient_acceptance_reference": "review:SLAB-B02",
        "qualified_coefficient_acceptance_acknowledged": True,
        "number_of_spans": 3,
        "maximum_span_variation_percent": 0,
        "uniform_cross_section_acknowledged": True,
        "substantially_uniform_load_acknowledged": True,
        "redistribution_applied": False,
        "positive_bar_diameter_mm": 8,
        "positive_bar_spacing_mm": 180,
        "negative_bar_diameter_mm": 10,
        "negative_bar_spacing_mm": 230,
        "distribution_bar_diameter_mm": 8,
        "distribution_bar_spacing_mm": 250,
        "reviewed_base_span_depth_limit": 23,
        "reviewed_aggregate_modification_factor": 1.18,
        "serviceability_limit_source_reference": "NPTEL-L18-B02-SLS",
        "serviceability_limit_source_is_approved": True,
        "qualified_serviceability_acceptance_reference": "review:SLAB-B02-SLS",
        "qualified_serviceability_acceptance_acknowledged": True,
    }
    values.update(overrides)
    return design_continuous_one_way_slab_is456(**values)  # type: ignore[arg-type]


def _two_way_b04(**overrides: object):
    values: dict[str, object] = {
        "x_effective_span_mm": 4000,
        "y_effective_span_mm": 6000,
        "thickness_mm": 160,
        "x_min_edge": "discontinuous",
        "x_max_edge": "continuous",
        "y_min_edge": "discontinuous",
        "y_max_edge": "continuous",
        "corner_lift_condition": "restrained",
        "support_topology_kind": "two_adjacent_edges_discontinuous",
        "alpha_x_negative": 0.075,
        "alpha_x_positive": 0.056,
        "alpha_y_negative": 0.047,
        "alpha_y_positive": 0.035,
        "coefficient_source_reference": "NPTEL-L19-B04",
        "coefficient_source_is_approved": True,
        "qualified_coefficient_acceptance_reference": "review:SLAB-B04",
        "qualified_coefficient_acceptance_acknowledged": True,
        "factored_area_load_kn_per_m2": 15.5,
        "d_x_mm": 135,
        "d_y_mm": 125,
        "fck_n_per_mm2": 20,
        "fy_n_per_mm2": 415,
        "x_positive_bar_diameter_mm": 10,
        "x_positive_bar_spacing_mm": 200,
        "x_negative_bar_diameter_mm": 10,
        "x_negative_bar_spacing_mm": 200,
        "y_positive_bar_diameter_mm": 8,
        "y_positive_bar_spacing_mm": 200,
        "y_negative_bar_diameter_mm": 8,
        "y_negative_bar_spacing_mm": 200,
        "edge_strip_bar_diameter_mm": 8,
        "edge_strip_bar_spacing_mm": 250,
        "torsion_bar_diameter_mm": 8,
        "torsion_bar_spacing_mm": 200,
        "reviewed_base_span_depth_limit": 30,
        "reviewed_aggregate_modification_factor": 1,
        "serviceability_limit_source_reference": "NPTEL-L19-B04-SLS",
        "serviceability_limit_source_is_approved": True,
        "qualified_serviceability_acceptance_reference": "review:SLAB-B04-SLS",
        "qualified_serviceability_acceptance_acknowledged": True,
    }
    values.update(overrides)
    return design_two_way_slab_panel_is456(**values)  # type: ignore[arg-type]


def test_oriented_geometry_never_silently_swaps_physical_edges() -> None:
    with pytest.raises(SlabContractError, match="explicit short span"):
        OrientedSlabPanelGeometry(6000, 4000, 160)


def test_physical_edge_topology_resolves_case_and_each_corner() -> None:
    topology = SlabSupportTopology(
        x_min=SlabEdgeContinuity.DISCONTINUOUS,
        x_max=SlabEdgeContinuity.CONTINUOUS,
        y_min=SlabEdgeContinuity.DISCONTINUOUS,
        y_max=SlabEdgeContinuity.CONTINUOUS,
        corner_lift_condition=CornerLiftCondition.RESTRAINED,
    )
    assert topology.kind is SlabSupportTopologyKind.TWO_ADJACENT_EDGES_DISCONTINUOUS
    assert (
        topology.corner_torsion_class(SlabCorner.X_MIN_Y_MIN) is CornerTorsionClass.FULL
    )
    assert (
        topology.corner_torsion_class(SlabCorner.X_MIN_Y_MAX) is CornerTorsionClass.HALF
    )
    assert (
        topology.corner_torsion_class(SlabCorner.X_MAX_Y_MAX) is CornerTorsionClass.NONE
    )


def test_b02_continuous_actions_flexure_shear_and_serviceability() -> None:
    result = _continuous_b02()
    assert result.flexure.positive_midspan.factored_moment_knm_per_m == pytest.approx(
        10.6875
    )
    assert result.flexure.negative_support.factored_moment_knm_per_m == pytest.approx(
        12.825
    )
    # The lesson's rounded direct equation reports 270.615/328.34 mm2/m.
    # The library's canonical 0.36/0.42 stress block is slightly conservative.
    assert result.flexure.positive_midspan.ast_required_mm2_per_m == pytest.approx(
        270.615, abs=0.35
    )
    assert result.flexure.negative_support.ast_required_mm2_per_m == pytest.approx(
        328.34, abs=0.35
    )
    assert result.flexure.factored_shear_kn_per_m == pytest.approx(17.1)
    assert result.shear.tau_v_n_per_mm2 == pytest.approx(0.148, abs=0.001)
    assert result.flexure.coefficient_correctness_verified_by_library is False
    assert result.serviceability.verified_by_library is False
    assert result.serviceability.is_satisfied is True


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("number_of_spans", 2, "at least three"),
        ("maximum_span_variation_percent", 15.1, "between 0 and 15"),
        ("redistribution_applied", True, "explicitly False"),
        ("coefficient_source_is_approved", False, "explicitly True"),
    ],
)
def test_continuous_coefficient_method_domain_fails_closed(
    field: str, value: object, message: str
) -> None:
    with pytest.raises(SlabContractError, match=message):
        _continuous_b02(**{field: value})


def test_slab_depth_factor_matches_benchmark_points_and_interpolation() -> None:
    assert slab_depth_shear_factor(140) == pytest.approx(1.3)
    assert slab_depth_shear_factor(160) == pytest.approx(1.28)
    assert slab_depth_shear_factor(300) == pytest.approx(1.0)


def test_serviceability_requires_reviewed_limit_carrier() -> None:
    with pytest.raises(SlabContractError, match="limit_source_is_approved"):
        SlabServiceabilityInput(3000, 115, 23, 1.18, "source", False, "review", True)


def test_b04_two_way_moments_strips_shear_and_corner_torsion() -> None:
    result = _two_way_b04()
    panel = result.panel
    assert panel.x_negative.factored_moment_knm_per_m == pytest.approx(18.60, abs=0.01)
    assert panel.x_positive.factored_moment_knm_per_m == pytest.approx(13.89, abs=0.01)
    assert panel.y_negative.factored_moment_knm_per_m == pytest.approx(11.66, abs=0.01)
    assert panel.y_positive.factored_moment_knm_per_m == pytest.approx(8.68, abs=0.01)
    assert panel.shear.tau_v_n_per_mm2 == pytest.approx(31 / 125, abs=1e-12)
    assert panel.strip_distribution.x_moment_middle_strip_width_mm == 4500
    assert panel.strip_distribution.x_moment_edge_strip_width_each_mm == 750
    assert panel.strip_distribution.moment_redistribution_applied is False
    assert panel.corner_torsion[0].zone_extent_from_each_edge_mm == 800
    assert [corner.torsion_class for corner in panel.corner_torsion] == [
        CornerTorsionClass.FULL,
        CornerTorsionClass.HALF,
        CornerTorsionClass.HALF,
        CornerTorsionClass.NONE,
    ]
    assert panel.coefficient_correctness_verified_by_library is False
    assert panel.complete_engineering_design_approved is False
    assert "not_applicable" in panel.punching_shear_disposition
    assert (
        panel.serviceability_dependency
        == "evaluated_by_composed_workflow_with_reviewed_limit_carrier"
    )
    assert not any("built-in coefficient" in item.lower() for item in panel.held_scope)


def test_two_way_topology_and_coefficient_case_must_match() -> None:
    with pytest.raises(SlabContractError, match="must match"):
        _two_way_b04(support_topology_kind="four_edges_continuous")


def test_free_to_lift_simple_support_has_no_restrained_corner_torsion() -> None:
    result = _two_way_b04(
        x_max_edge="discontinuous",
        y_max_edge="discontinuous",
        corner_lift_condition="free_to_lift",
        support_topology_kind="simply_supported_corners_free",
        alpha_x_negative=0,
        alpha_y_negative=0,
    )
    assert all(
        corner.torsion_class is CornerTorsionClass.NOT_APPLICABLE_FREE_TO_LIFT
        and corner.required_each_of_four_layers_mm2_per_m == 0
        for corner in result.panel.corner_torsion
    )


def test_complete_simply_supported_route_adds_shear_and_strict_serviceability() -> None:
    result = design_complete_one_way_slab_is456(
        short_effective_span_mm=3000,
        long_effective_span_mm=7500,
        thickness_mm=150,
        d_mm=125,
        factored_area_load_kn_per_m2=10,
        fck_n_per_mm2=20,
        fy_n_per_mm2=415,
        main_bar_diameter_mm=10,
        main_bar_spacing_mm=250,
        distribution_bar_diameter_mm=8,
        distribution_bar_spacing_mm=250,
        reviewed_base_span_depth_limit=20,
        reviewed_aggregate_modification_factor=1.2,
        serviceability_limit_source_reference="reviewed-limit:SS",
        serviceability_limit_source_is_approved=True,
        qualified_serviceability_acceptance_reference="review:SS",
        qualified_serviceability_acceptance_acknowledged=True,
    )
    assert result.reinforcement.flexure.factored_moment_knm == 11.25
    assert (
        result.reinforcement.flexure.status
        is OneWaySlabFlexureStatus.COMPLETE_WORKFLOW_CHECKS_COMPOSED
    )
    assert (
        result.reinforcement.detailing.input.flexure_result.status
        is OneWaySlabFlexureStatus.COMPLETE_WORKFLOW_CHECKS_COMPOSED
    )
    serialized_limitations = (
        result.reinforcement.flexure.limitations
        + result.reinforcement.detailing.limitations
    )
    assert not any("pending" in item.lower() for item in serialized_limitations)
    assert not any(
        "shear design is pending" in item.lower() for item in serialized_limitations
    )
    assert result.shear.is_safe_without_shear_reinforcement is True
    assert result.serviceability.is_satisfied is True
    assert result.complete_engineering_design_approved is False


def test_complete_one_way_capacity_miss_returns_structured_fail() -> None:
    result = design_complete_one_way_slab_is456(
        short_effective_span_mm=3000,
        long_effective_span_mm=7000,
        thickness_mm=150,
        d_mm=100,
        factored_area_load_kn_per_m2=50,
        fck_n_per_mm2=20,
        fy_n_per_mm2=415,
        main_bar_diameter_mm=10,
        main_bar_spacing_mm=200,
        distribution_bar_diameter_mm=8,
        distribution_bar_spacing_mm=250,
        reviewed_base_span_depth_limit=20,
        reviewed_aggregate_modification_factor=1.0,
        serviceability_limit_source_reference="reviewed:packet-c",
        serviceability_limit_source_is_approved=True,
        qualified_serviceability_acceptance_reference="review:packet-c",
        qualified_serviceability_acceptance_acknowledged=True,
    )

    failure = result.reinforcement.flexure
    assert isinstance(failure, SlabCapacityFailureResult)
    assert failure.factored_moment_knm == pytest.approx(56.25)
    assert failure.limiting_moment_knm == pytest.approx(27.5925, abs=0.001)
    assert failure.result_envelope.engineering_status is EngineeringStatus.FAIL
    assert result.reinforcement.detailing is None
    assert result.shear is None
    assert result.serviceability is None
    assert result.punching_shear_disposition == (
        "not_evaluated_due_to_flexural_capacity_failure"
    )


def test_complete_two_way_capacity_miss_returns_structured_fail() -> None:
    result = _two_way_b04(factored_area_load_kn_per_m2=100)

    assert isinstance(result.panel, SlabCapacityFailureResult)
    assert result.panel.governing_region == "x_negative_continuous_edge"
    assert result.panel.result_envelope.engineering_status is EngineeringStatus.FAIL
    assert result.serviceability is None
