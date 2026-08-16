"""INDIA-2-FLAT-B frozen direct-design moment tests."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from structural_lib.codes.is456.flat_slab import (
    FlatSlabAnalysisMethod,
    FlatSlabContractError,
    FlatSlabDirection,
    FlatSlabGravityLoad,
    FlatSlabGridGeometry,
    FlatSlabMaterial,
    FlatSlabPanelInput,
    FlatSlabPanelLocation,
    calculate_regular_interior_flat_slab_moments,
)
from structural_lib.codes.is456.traceability import get_clause_refs


def _benchmark_panel() -> FlatSlabPanelInput:
    return FlatSlabPanelInput(
        geometry=FlatSlabGridGeometry(
            centre_to_centre_span_x_mm=6000.0,
            centre_to_centre_span_y_mm=6000.0,
            continuous_span_count_x=3,
            continuous_span_count_y=3,
            column_width_x_mm=500.0,
            column_width_y_mm=500.0,
            overall_depth_mm=300.0,
            conservative_effective_depth_mm=260.0,
            analysis_method=FlatSlabAnalysisMethod.DIRECT_DESIGN,
            panel_location=FlatSlabPanelLocation.INTERIOR,
            all_spans_equal_x=True,
            all_spans_equal_y=True,
            columns_offset_from_grid=False,
            solid_slab=True,
            drop_present=False,
            column_head_present=False,
            marginal_beam_or_wall_present=False,
            openings_present=False,
            geometry_basis_reference="INDIA-2-FLAT-HAND-01-GEOMETRY",
        ),
        material=FlatSlabMaterial(
            concrete_grade_nmm2=30.0,
            steel_grade_nmm2=500.0,
            uncoated_deformed_bars=True,
            material_basis_reference="INDIA-2-FLAT-HAND-01-MATERIAL",
        ),
        gravity_load=FlatSlabGravityLoad(
            service_dead_load_kn_per_m2=9.0,
            service_live_load_kn_per_m2=4.0,
            factored_uniform_load_kn_per_m2=19.5,
            self_weight_included=True,
            identical_full_loading_on_represented_panels=True,
            patterned_loading_required=False,
            unbalanced_or_lateral_moment_transfer_present=False,
            load_combination_approved=True,
            load_basis_reference="INDIA-2-FLAT-HAND-01-LOAD",
        ),
    )


def test_frozen_moment_benchmark_in_both_directions() -> None:
    result = calculate_regular_interior_flat_slab_moments(_benchmark_panel())

    for direction_result, direction in (
        (result.x, FlatSlabDirection.X),
        (result.y, FlatSlabDirection.Y),
    ):
        assert direction_result.direction is direction
        assert direction_result.factored_uniform_load_kn_per_m2 == pytest.approx(19.5)
        assert direction_result.transverse_span_m == pytest.approx(6.0)
        assert direction_result.governing_clear_span_m == pytest.approx(5.5)
        assert direction_result.design_load_on_panel_strip_kn == pytest.approx(643.5)
        assert direction_result.total_static_moment_knm == pytest.approx(442.40625)
        assert direction_result.total_negative_moment_knm == pytest.approx(287.5640625)
        assert direction_result.total_positive_moment_knm == pytest.approx(154.8421875)
        assert direction_result.column_strip_negative_moment_knm == pytest.approx(
            215.673046875
        )
        assert direction_result.column_strip_positive_moment_knm == pytest.approx(
            92.9053125
        )
        assert direction_result.middle_strip_negative_moment_knm == pytest.approx(
            71.891015625
        )
        assert direction_result.middle_strip_positive_moment_knm == pytest.approx(
            61.936875
        )


def test_distribution_preserves_each_total_moment() -> None:
    result = calculate_regular_interior_flat_slab_moments(_benchmark_panel())

    for direction in (result.x, result.y):
        assert (
            direction.total_negative_moment_knm + direction.total_positive_moment_knm
        ) == pytest.approx(direction.total_static_moment_knm)
        assert (
            direction.column_strip_negative_moment_knm
            + direction.middle_strip_negative_moment_knm
        ) == pytest.approx(direction.total_negative_moment_knm)
        assert (
            direction.column_strip_positive_moment_knm
            + direction.middle_strip_positive_moment_knm
        ) == pytest.approx(direction.total_positive_moment_knm)


def test_calculation_reuses_resolved_geometry_and_input() -> None:
    panel = _benchmark_panel()
    result = calculate_regular_interior_flat_slab_moments(panel)

    assert result.input is panel
    assert result.geometry.input is panel
    assert result.geometry.x.governing_clear_span_mm == pytest.approx(5500.0)
    assert result.geometry.x.column_strip_total_width_mm == pytest.approx(3000.0)


def test_clause_and_source_provenance_is_retained() -> None:
    refs = get_clause_refs(calculate_regular_interior_flat_slab_moments)
    assert refs == [
        "31.4.2.2",
        "31.4.3.2",
        "31.4.4",
        "31.5.5.1",
        "31.5.5.3",
        "31.5.5.4",
    ]

    result = calculate_regular_interior_flat_slab_moments(_benchmark_panel())
    assert result.source_refs[0].startswith("IS 456:2000 Cl. 31.4.2.2")
    assert "IS456-2000-A6" in result.source_refs
    assert "INDIA-2-FLAT-HAND-01-GEOMETRY" in result.source_refs
    assert "INDIA-2-FLAT-HAND-01-LOAD" in result.source_refs


def test_result_contracts_are_immutable() -> None:
    result = calculate_regular_interior_flat_slab_moments(_benchmark_panel())

    with pytest.raises(FrozenInstanceError):
        result.x.total_static_moment_knm = 0.0  # type: ignore[misc]


def test_non_panel_input_fails_closed() -> None:
    with pytest.raises(FlatSlabContractError, match="FlatSlabPanelInput"):
        calculate_regular_interior_flat_slab_moments(object())  # type: ignore[arg-type]
