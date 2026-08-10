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


def test_builtin_continuous_service_marks_coefficients_verified_by_library() -> None:
    result = design_continuous_one_way_slab_builtin_is456(
        short_effective_span_mm=3000,
        long_effective_span_mm=7500,
        thickness_mm=140,
        d_mm=115,
        factored_dead_and_fixed_imposed_load_kn_per_m2=14.25,
        factored_nonfixed_imposed_load_kn_per_m2=0,
        positive_location="end_span_positive",
        negative_location="next_to_end_support_negative",
        shear_location="end_support",
        fck_n_per_mm2=20,
        fy_n_per_mm2=415,
        number_of_spans=3,
        maximum_span_variation_percent=0,
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
    assert result.flexure.positive_midspan.factored_moment_knm_per_m == 10.6875
    assert result.flexure.coefficient_correctness_verified_by_library is True
    assert result.flexure.input.coefficients.table_id == "IS456_TABLE_12_13"


def test_builtin_two_way_service_retains_table_case_and_interpolation() -> None:
    result = design_two_way_slab_panel_builtin_is456(
        x_effective_span_mm=4000,
        y_effective_span_mm=6000,
        thickness_mm=160,
        x_min_edge="discontinuous",
        x_max_edge="continuous",
        y_min_edge="discontinuous",
        y_max_edge="continuous",
        corner_lift_condition="restrained",
        factored_area_load_kn_per_m2=15.5,
        d_x_mm=135,
        d_y_mm=125,
        fck_n_per_mm2=20,
        fy_n_per_mm2=415,
        x_positive_bar_diameter_mm=10,
        x_positive_bar_spacing_mm=200,
        x_negative_bar_diameter_mm=10,
        x_negative_bar_spacing_mm=200,
        y_positive_bar_diameter_mm=8,
        y_positive_bar_spacing_mm=200,
        y_negative_bar_diameter_mm=8,
        y_negative_bar_spacing_mm=200,
        edge_strip_bar_diameter_mm=8,
        edge_strip_bar_spacing_mm=250,
        torsion_bar_diameter_mm=8,
        torsion_bar_spacing_mm=200,
        reviewed_base_span_depth_limit=30,
        reviewed_aggregate_modification_factor=1,
        serviceability_limit_source_reference="IS456_CL24_REVIEWED",
        serviceability_limit_source_is_approved=True,
        qualified_serviceability_acceptance_reference="review:B04-SLS",
        qualified_serviceability_acceptance_acknowledged=True,
    )
    assert result.panel.x_negative.factored_moment_knm_per_m == pytest.approx(18.6)
    assert result.panel.coefficient_correctness_verified_by_library is True
    assert result.panel.input.coefficients.case_id == "table_26_case_4"
