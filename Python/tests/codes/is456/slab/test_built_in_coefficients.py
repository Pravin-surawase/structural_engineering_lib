# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Exact endpoints, interpolation, provenance, and bounds for built-in coefficients."""

from __future__ import annotations

import pytest

from structural_lib.codes.is456.slab.built_in_coefficients import (
    resolve_builtin_one_way_continuous_coefficients,
    resolve_builtin_two_way_panel_coefficients,
)
from structural_lib.codes.is456.slab.coefficients import CoefficientMethod
from structural_lib.codes.is456.slab.models import SlabContractError
from structural_lib.codes.is456.slab.topology import (
    CornerLiftCondition,
    OrientedSlabPanelGeometry,
    SlabCorner,
    SlabEdgeContinuity,
    SlabSupportTopology,
)
from structural_lib.services.slab_api import (
    design_continuous_one_way_slab_builtin_is456,
    design_two_way_slab_panel_builtin_is456,
)


def _topology(
    x_min: str = "discontinuous",
    x_max: str = "continuous",
    y_min: str = "discontinuous",
    y_max: str = "continuous",
    lift: str = "restrained",
) -> SlabSupportTopology:
    return SlabSupportTopology(
        x_min=SlabEdgeContinuity(x_min),
        x_max=SlabEdgeContinuity(x_max),
        y_min=SlabEdgeContinuity(y_min),
        y_max=SlabEdgeContinuity(y_max),
        corner_lift_condition=CornerLiftCondition(lift),
    )


def test_table_12_13_b02_exact_coefficients() -> None:
    result = resolve_builtin_one_way_continuous_coefficients(
        factored_dead_and_fixed_imposed_load_kn_per_m2=14.25,
        factored_nonfixed_imposed_load_kn_per_m2=0,
        positive_location="end_span_positive",
        negative_location="next_to_end_support_negative",
        shear_location="end_support",
    )
    assert result.positive_midspan == pytest.approx(1 / 12)
    assert result.negative_support == pytest.approx(1 / 10)
    assert result.shear_support == pytest.approx(0.4)
    assert result.method is CoefficientMethod.BUILT_IN_EXACT
    assert result.verified_by_library is True
    assert result.table_id == "IS456_TABLE_12_13"


def test_table_12_combines_fixed_and_nonfixed_components_by_action() -> None:
    result = resolve_builtin_one_way_continuous_coefficients(
        factored_dead_and_fixed_imposed_load_kn_per_m2=6,
        factored_nonfixed_imposed_load_kn_per_m2=4,
        positive_location="interior_span_positive",
        negative_location="other_interior_support_negative",
        shear_location="other_interior_support",
    )
    assert result.positive_midspan == pytest.approx((6 / 16 + 4 / 12) / 10)
    assert result.negative_support == pytest.approx((6 / 12 + 4 / 9) / 10)
    assert result.shear_support == pytest.approx((6 * 0.5 + 4 * 0.6) / 10)


# IS 456:2000 Table 26, columns 1.50, 1.75 and all long-span ratios.
# https://www.cracindia.in/admin/uploads/IS-456.pdf (printed page 91).
# Each pair lists negative and positive magnitudes in that direction.
_TABLE_26 = {
    1: ((0.053, 0.041), (0.060, 0.045), (0.032, 0.024)),
    2: ((0.057, 0.044), (0.064, 0.048), (0.037, 0.028)),
    3: ((0.067, 0.051), (0.077, 0.059), (0.037, 0.028)),
    4: ((0.075, 0.056), (0.084, 0.063), (0.047, 0.035)),
    5: ((0.060, 0.045), (0.065, 0.049), (0.000, 0.035)),
    6: ((0.000, 0.068), (0.000, 0.080), (0.045, 0.035)),
    7: ((0.084, 0.064), (0.091, 0.069), (0.000, 0.043)),
    8: ((0.000, 0.076), (0.000, 0.087), (0.057, 0.043)),
    9: ((0.000, 0.089), (0.000, 0.100), (0.000, 0.056)),
}


@pytest.mark.parametrize(
    ("edges", "case_id"),
    (
        ("CCCC", 1),
        ("CCDC", 2),
        ("CCCD", 2),
        ("DCCC", 3),
        ("CDCC", 3),
        ("DCDC", 4),
        ("DCCD", 4),
        ("CDDC", 4),
        ("CDCD", 4),
        ("CCDD", 5),
        ("DDCC", 6),
        ("DCDD", 7),
        ("CDDD", 7),
        ("DDCD", 8),
        ("DDDC", 8),
        ("DDDD", 9),
    ),
)
@pytest.mark.parametrize(
    ("span_y", "fraction", "method", "bounds"),
    (
        (6000, 0.0, CoefficientMethod.BUILT_IN_EXACT, (1.50, 1.50)),
        (6200, 0.2, CoefficientMethod.BUILT_IN_INTERPOLATED, (1.50, 1.75)),
    ),
)
def test_table_26_all_labelled_topologies_and_reflections(
    edges, case_id, span_y, fraction, method, bounds
):
    first, second, long_span = _TABLE_26[case_id]
    short_span = tuple(
        lo + fraction * (hi - lo) for lo, hi in zip(first, second, strict=True)
    )
    geometry = OrientedSlabPanelGeometry(4000, span_y, 160)
    x_min, x_max, y_min, y_max = edges
    corner_classes = []
    for ordering in (
        edges,
        x_max + x_min + y_min + y_max,
        x_min + x_max + y_max + y_min,
    ):
        topology = _topology(
            *("discontinuous" if edge == "D" else "continuous" for edge in ordering)
        )
        result = resolve_builtin_two_way_panel_coefficients(
            geometry=geometry, topology=topology
        )
        assert result.case_id == f"table_26_case_{case_id}"
        assert result.method is method
        assert result.interpolation_bounds == bounds
        assert (
            result.alpha_x_negative,
            result.alpha_x_positive,
            result.alpha_y_negative,
            result.alpha_y_positive,
        ) == pytest.approx(short_span + long_span, abs=1e-12)
        assert result.table_id == "IS456_TABLE_26"
        corner_classes.append(
            tuple(topology.corner_torsion_class(corner).value for corner in SlabCorner)
        )
    original, across_x, across_y = corner_classes
    corners = ((x_min, y_min), (x_min, y_max), (x_max, y_min), (x_max, y_max))
    assert original == tuple(
        ("none", "half", "full")[pair.count("D")] for pair in corners
    )
    assert across_x == (original[2], original[3], original[0], original[1])
    assert across_y == (original[1], original[0], original[3], original[2])


def test_swapped_two_way_span_order_is_rejected() -> None:
    with pytest.raises(SlabContractError, match="short"):
        OrientedSlabPanelGeometry(6000, 4000, 160)


def test_table_26_case_4_b04_exact_point() -> None:
    result = resolve_builtin_two_way_panel_coefficients(
        geometry=OrientedSlabPanelGeometry(4000, 6000, 160),
        topology=_topology(),
    )
    assert result.case_id == "table_26_case_4"
    assert result.alpha_x_negative == 0.075
    assert result.alpha_x_positive == 0.056
    assert result.alpha_y_negative == 0.047
    assert result.alpha_y_positive == 0.035
    assert result.method is CoefficientMethod.BUILT_IN_EXACT
    assert result.interpolation_bounds == (1.5, 1.5)
    assert result.verified_by_library is True


def test_table_26_interpolates_only_between_adjacent_points() -> None:
    result = resolve_builtin_two_way_panel_coefficients(
        geometry=OrientedSlabPanelGeometry(4000, 6200, 160),
        topology=_topology(),
    )
    assert result.method is CoefficientMethod.BUILT_IN_INTERPOLATED
    assert result.interpolation_bounds == (1.5, 1.75)
    assert result.alpha_x_negative == pytest.approx(0.075 + 0.2 * (0.084 - 0.075))
    assert result.alpha_x_positive == pytest.approx(0.056 + 0.2 * (0.063 - 0.056))


def test_table_27_simple_support_exact_point_has_no_negative_coefficients() -> None:
    result = resolve_builtin_two_way_panel_coefficients(
        geometry=OrientedSlabPanelGeometry(4000, 6000, 160),
        topology=_topology(
            x_max="discontinuous",
            y_max="discontinuous",
            lift="free_to_lift",
        ),
    )
    assert result.table_id == "IS456_TABLE_27"
    assert result.alpha_x_positive == 0.104
    assert result.alpha_y_positive == 0.046
    assert result.alpha_x_negative == result.alpha_y_negative == 0.0


def test_table_26_extrapolation_fails_closed() -> None:
    with pytest.raises(SlabContractError, match="table bounds"):
        resolve_builtin_two_way_panel_coefficients(
            geometry=OrientedSlabPanelGeometry(4000, 8200, 160),
            topology=_topology(),
        )


def _b02(fixed, nonfixed, *, spans=3, variation=15):
    return design_continuous_one_way_slab_builtin_is456(
        short_effective_span_mm=3000,
        long_effective_span_mm=7500,
        thickness_mm=140,
        d_mm=115,
        factored_dead_and_fixed_imposed_load_kn_per_m2=fixed,
        factored_nonfixed_imposed_load_kn_per_m2=nonfixed,
        positive_location="end_span_positive",
        negative_location="next_to_end_support_negative",
        shear_location="end_support",
        fck_n_per_mm2=20,
        fy_n_per_mm2=415,
        number_of_spans=spans,
        maximum_span_variation_percent=variation,
        uniform_cross_section_acknowledged=True,
        substantially_uniform_load_acknowledged=True,
        redistribution_applied=False,
        positive_bar_diameter_mm=8,
        positive_bar_spacing_mm=180,
        negative_bar_diameter_mm=10,
        negative_bar_spacing_mm=230,
        distribution_bar_diameter_mm=8,
        distribution_bar_spacing_mm=250,
        reviewed_base_span_depth_limit=23,
        reviewed_aggregate_modification_factor=1.18,
        serviceability_limit_source_reference="IS456_CL23_REVIEWED",
        serviceability_limit_source_is_approved=True,
        qualified_serviceability_acceptance_reference="review:B02-SLS",
        qualified_serviceability_acceptance_acknowledged=True,
    )


def test_builtin_continuous_service_marks_coefficients_verified_by_library() -> None:
    result = _b02(14.25, 0)
    assert result.flexure.positive_midspan.factored_moment_knm_per_m == 10.6875
    assert result.flexure.coefficient_correctness_verified_by_library is True
    assert result.flexure.input.coefficients.table_id == "IS456_TABLE_12_13"


def test_b02_mixed_actions_at_three_spans_and_15_percent_variation() -> None:
    result = _b02(10, 4.25).flexure
    # IS 456:2000 Tables 12 and 13 at L = 3 m.
    assert result.positive_midspan.factored_moment_knm_per_m == pytest.approx(
        (10 / 12 + 4.25 / 10) * 3**2
    )
    assert result.negative_support.factored_moment_knm_per_m == pytest.approx(
        (10 / 10 + 4.25 / 9) * 3**2
    )
    assert result.factored_shear_kn_per_m == pytest.approx((0.4 * 10 + 0.45 * 4.25) * 3)


@pytest.mark.parametrize(("spans", "variation"), ((2, 15), (3, 15.01)))
def test_b02_rejects_outside_three_span_and_variation_bounds(spans, variation):
    with pytest.raises(SlabContractError):
        _b02(10, 4.25, spans=spans, variation=variation)


def _builtin_two_way(**overrides: object):
    values: dict[str, object] = {
        "x_effective_span_mm": 4000,
        "y_effective_span_mm": 6000,
        "thickness_mm": 160,
        "x_min_edge": "discontinuous",
        "x_max_edge": "continuous",
        "y_min_edge": "discontinuous",
        "y_max_edge": "continuous",
        "corner_lift_condition": "restrained",
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
        "serviceability_limit_source_reference": "IS456_CL24_REVIEWED",
        "serviceability_limit_source_is_approved": True,
        "qualified_serviceability_acceptance_reference": "review:B04-SLS",
        "qualified_serviceability_acceptance_acknowledged": True,
    }
    values.update(overrides)
    return design_two_way_slab_panel_builtin_is456(**values)  # type: ignore[arg-type]


def test_builtin_two_way_service_retains_table_case_and_composed_truth() -> None:
    result = _builtin_two_way()
    assert result.panel.x_negative.factored_moment_knm_per_m == pytest.approx(18.6)
    assert result.panel.coefficient_correctness_verified_by_library is True
    assert result.panel.input.coefficients.case_id == "table_26_case_4"
    assert (
        result.panel.serviceability_dependency
        == "evaluated_by_composed_workflow_with_reviewed_limit_carrier"
    )
    assert not any(
        "built-in coefficient" in item.lower() for item in result.panel.held_scope
    )


@pytest.mark.parametrize(
    ("span_y", "alpha_x", "alpha_y"),
    (
        (6000, 0.104, 0.046),
        (6200, 0.104 + 0.2 * (0.113 - 0.104), 0.046 + 0.2 * (0.037 - 0.046)),
    ),
)
def test_builtin_table_27_free_corner_workflow_has_no_torsion_or_false_hold(
    span_y,
    alpha_x,
    alpha_y,
) -> None:
    result = _builtin_two_way(
        y_effective_span_mm=span_y,
        x_max_edge="discontinuous",
        y_max_edge="discontinuous",
        corner_lift_condition="free_to_lift",
    )
    assert result.panel.input.coefficients.table_id == "IS456_TABLE_27"
    assert result.panel.x_positive.coefficient == pytest.approx(alpha_x, abs=1e-12)
    assert result.panel.y_positive.coefficient == pytest.approx(alpha_y, abs=1e-12)
    assert result.panel.x_negative.coefficient == 0.0
    assert result.panel.y_negative.coefficient == 0.0
    assert all(
        corner.torsion_class.value == "not_applicable_free_to_lift"
        and corner.required_each_of_four_layers_mm2_per_m == 0.0
        for corner in result.panel.corner_torsion
    )
    assert not any(
        "built-in coefficient" in item.lower() for item in result.panel.held_scope
    )


def test_builtin_four_edge_continuous_restrained_topology_resolves_case_one() -> None:
    result = _builtin_two_way(
        x_min_edge="continuous",
        y_min_edge="continuous",
    )
    assert result.panel.input.coefficients.case_id == "table_26_case_1"
    assert all(
        corner.torsion_class.value == "none" for corner in result.panel.corner_torsion
    )
