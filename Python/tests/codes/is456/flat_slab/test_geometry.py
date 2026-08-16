"""INDIA-2-FLAT-A benchmark and fail-closed geometry tests."""

from __future__ import annotations

import math

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
    resolve_regular_interior_flat_slab_geometry,
)
from structural_lib.codes.is456.traceability import get_clause_refs


def _benchmark_geometry(**overrides: object) -> FlatSlabGridGeometry:
    values: dict[str, object] = {
        "centre_to_centre_span_x_mm": 6000.0,
        "centre_to_centre_span_y_mm": 6000.0,
        "continuous_span_count_x": 3,
        "continuous_span_count_y": 3,
        "column_width_x_mm": 500.0,
        "column_width_y_mm": 500.0,
        "overall_depth_mm": 300.0,
        "conservative_effective_depth_mm": 260.0,
        "analysis_method": FlatSlabAnalysisMethod.DIRECT_DESIGN,
        "panel_location": FlatSlabPanelLocation.INTERIOR,
        "all_spans_equal_x": True,
        "all_spans_equal_y": True,
        "columns_offset_from_grid": False,
        "solid_slab": True,
        "drop_present": False,
        "column_head_present": False,
        "marginal_beam_or_wall_present": False,
        "openings_present": False,
        "geometry_basis_reference": "INDIA-2-FLAT-HAND-01-GEOMETRY",
    }
    values.update(overrides)
    return FlatSlabGridGeometry(**values)  # type: ignore[arg-type]


def _benchmark_material(**overrides: object) -> FlatSlabMaterial:
    values: dict[str, object] = {
        "concrete_grade_nmm2": 30.0,
        "steel_grade_nmm2": 500.0,
        "uncoated_deformed_bars": True,
        "material_basis_reference": "INDIA-2-FLAT-HAND-01-MATERIAL",
    }
    values.update(overrides)
    return FlatSlabMaterial(**values)  # type: ignore[arg-type]


def _benchmark_load(**overrides: object) -> FlatSlabGravityLoad:
    values: dict[str, object] = {
        "service_dead_load_kn_per_m2": 9.0,
        "service_live_load_kn_per_m2": 4.0,
        "factored_uniform_load_kn_per_m2": 19.5,
        "self_weight_included": True,
        "identical_full_loading_on_represented_panels": True,
        "patterned_loading_required": False,
        "unbalanced_or_lateral_moment_transfer_present": False,
        "load_combination_approved": True,
        "load_basis_reference": "INDIA-2-FLAT-HAND-01-LOAD",
    }
    values.update(overrides)
    return FlatSlabGravityLoad(**values)  # type: ignore[arg-type]


def _benchmark_panel(**overrides: object) -> FlatSlabPanelInput:
    values: dict[str, object] = {
        "geometry": _benchmark_geometry(),
        "material": _benchmark_material(),
        "gravity_load": _benchmark_load(),
    }
    values.update(overrides)
    return FlatSlabPanelInput(**values)  # type: ignore[arg-type]


def test_hand_benchmark_geometry_and_strip_widths_in_both_directions() -> None:
    result = resolve_regular_interior_flat_slab_geometry(_benchmark_panel())

    assert result.direct_design_eligible is True
    assert result.minimum_slab_thickness_mm == pytest.approx(125.0)
    assert result.service_live_dead_ratio == pytest.approx(4.0 / 9.0)
    assert result.expected_factored_uniform_load_kn_per_m2 == pytest.approx(19.5)
    for direction_result, direction in (
        (result.x, FlatSlabDirection.X),
        (result.y, FlatSlabDirection.Y),
    ):
        assert direction_result.direction is direction
        assert direction_result.centre_to_centre_span_mm == pytest.approx(6000.0)
        assert direction_result.transverse_span_mm == pytest.approx(6000.0)
        assert direction_result.support_width_mm == pytest.approx(500.0)
        assert direction_result.face_to_face_clear_span_mm == pytest.approx(5500.0)
        assert direction_result.minimum_clear_span_component_mm == pytest.approx(3900.0)
        assert direction_result.governing_clear_span_mm == pytest.approx(5500.0)
        assert direction_result.column_strip_half_width_mm == pytest.approx(1500.0)
        assert direction_result.column_strip_total_width_mm == pytest.approx(3000.0)
        assert direction_result.middle_strip_width_mm == pytest.approx(3000.0)
        assert (
            direction_result.column_strip_total_width_mm
            + direction_result.middle_strip_width_mm
            == pytest.approx(direction_result.transverse_span_mm)
        )


def test_minimum_clear_span_component_can_govern() -> None:
    panel = _benchmark_panel(
        geometry=_benchmark_geometry(
            column_width_x_mm=2500.0,
            column_width_y_mm=2500.0,
        )
    )
    result = resolve_regular_interior_flat_slab_geometry(panel)

    assert result.x.face_to_face_clear_span_mm == pytest.approx(3500.0)
    assert result.x.minimum_clear_span_component_mm == pytest.approx(3900.0)
    assert result.x.governing_clear_span_mm == pytest.approx(3900.0)
    assert result.y.governing_clear_span_mm == pytest.approx(3900.0)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("centre_to_centre_span_x_mm", 0.0),
        ("centre_to_centre_span_y_mm", math.inf),
        ("column_width_x_mm", math.nan),
        ("column_width_y_mm", -1.0),
        ("overall_depth_mm", 0.0),
        ("conservative_effective_depth_mm", math.inf),
    ),
)
def test_invalid_geometry_dimensions_fail_closed(field: str, value: float) -> None:
    with pytest.raises(FlatSlabContractError, match=field):
        _benchmark_geometry(**{field: value})


@pytest.mark.parametrize(
    "field", ("continuous_span_count_x", "continuous_span_count_y")
)
def test_direct_design_requires_at_least_three_spans(field: str) -> None:
    with pytest.raises(FlatSlabContractError, match="at least 3"):
        _benchmark_geometry(**{field: 2})
    with pytest.raises(FlatSlabContractError, match="positive integer"):
        _benchmark_geometry(**{field: True})


def test_square_panel_and_square_column_boundaries_fail_closed() -> None:
    with pytest.raises(FlatSlabContractError, match="spans must be equal"):
        _benchmark_geometry(centre_to_centre_span_y_mm=5000.0)
    with pytest.raises(FlatSlabContractError, match="column widths must be equal"):
        _benchmark_geometry(column_width_y_mm=600.0)
    with pytest.raises(FlatSlabContractError, match="column_width_x_mm"):
        _benchmark_geometry(column_width_x_mm=6000.0, column_width_y_mm=6000.0)


def test_depth_and_method_boundaries_fail_closed() -> None:
    with pytest.raises(FlatSlabContractError, match="at least 125"):
        _benchmark_geometry(overall_depth_mm=124.999)
    with pytest.raises(FlatSlabContractError, match="effective_depth_mm"):
        _benchmark_geometry(conservative_effective_depth_mm=300.0)
    with pytest.raises(FlatSlabContractError, match="analysis_method"):
        _benchmark_geometry(analysis_method="equivalent_frame")
    with pytest.raises(FlatSlabContractError, match="panel_location"):
        _benchmark_geometry(panel_location="exterior")


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("all_spans_equal_x", False),
        ("all_spans_equal_y", False),
        ("solid_slab", False),
        ("columns_offset_from_grid", True),
        ("drop_present", True),
        ("column_head_present", True),
        ("marginal_beam_or_wall_present", True),
        ("openings_present", True),
    ),
)
def test_each_topology_boundary_is_explicit(field: str, value: bool) -> None:
    with pytest.raises(FlatSlabContractError, match=field):
        _benchmark_geometry(**{field: value})


def test_geometry_reference_is_required() -> None:
    with pytest.raises(FlatSlabContractError, match="geometry_basis_reference"):
        _benchmark_geometry(geometry_basis_reference=" ")


def test_material_contract_accepts_only_frozen_grades_and_bar_type() -> None:
    accepted = _benchmark_material()
    assert accepted.concrete_grade_nmm2 == pytest.approx(30.0)
    assert accepted.steel_grade_nmm2 == pytest.approx(500.0)

    with pytest.raises(FlatSlabContractError, match="standard M20-M60"):
        _benchmark_material(concrete_grade_nmm2=27.0)
    with pytest.raises(FlatSlabContractError, match="Fe415 or Fe500"):
        _benchmark_material(steel_grade_nmm2=550.0)
    with pytest.raises(FlatSlabContractError, match="uncoated_deformed_bars"):
        _benchmark_material(uncoated_deformed_bars=False)
    with pytest.raises(FlatSlabContractError, match="material_basis_reference"):
        _benchmark_material(material_basis_reference=" ")


def test_gravity_load_contract_matches_benchmark_and_half_ratio_boundary() -> None:
    accepted = _benchmark_load()
    assert accepted.factored_uniform_load_kn_per_m2 == pytest.approx(19.5)

    boundary = _benchmark_load(
        service_dead_load_kn_per_m2=8.0,
        service_live_load_kn_per_m2=4.0,
        factored_uniform_load_kn_per_m2=18.0,
    )
    assert (
        boundary.service_live_load_kn_per_m2 / boundary.service_dead_load_kn_per_m2
        == pytest.approx(0.5)
    )

    with pytest.raises(FlatSlabContractError, match="must not exceed 0.5"):
        _benchmark_load(service_live_load_kn_per_m2=5.0)
    with pytest.raises(FlatSlabContractError, match="must equal 1.5"):
        _benchmark_load(factored_uniform_load_kn_per_m2=19.0)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("self_weight_included", False),
        ("identical_full_loading_on_represented_panels", False),
        ("patterned_loading_required", True),
        ("unbalanced_or_lateral_moment_transfer_present", True),
        ("load_combination_approved", False),
    ),
)
def test_each_load_boundary_is_explicit(field: str, value: bool) -> None:
    with pytest.raises(FlatSlabContractError, match=field):
        _benchmark_load(**{field: value})


def test_load_dimensions_and_reference_fail_closed() -> None:
    with pytest.raises(FlatSlabContractError, match="service_dead_load_kn_per_m2"):
        _benchmark_load(service_dead_load_kn_per_m2=math.nan)
    with pytest.raises(FlatSlabContractError, match="service_live_load_kn_per_m2"):
        _benchmark_load(service_live_load_kn_per_m2=0.0)
    with pytest.raises(FlatSlabContractError, match="load_basis_reference"):
        _benchmark_load(load_basis_reference=" ")


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("geometry", object(), "FlatSlabGridGeometry"),
        ("material", object(), "FlatSlabMaterial"),
        ("gravity_load", object(), "FlatSlabGravityLoad"),
    ),
)
def test_composed_input_types_fail_closed(
    field: str, value: object, message: str
) -> None:
    with pytest.raises(FlatSlabContractError, match=message):
        _benchmark_panel(**{field: value})


def test_resolver_type_clause_and_source_provenance() -> None:
    with pytest.raises(FlatSlabContractError, match="FlatSlabPanelInput"):
        resolve_regular_interior_flat_slab_geometry(object())  # type: ignore[arg-type]

    result = resolve_regular_interior_flat_slab_geometry(_benchmark_panel())
    assert get_clause_refs(resolve_regular_interior_flat_slab_geometry) == [
        "31.1.1",
        "31.2.1",
        "31.3.1",
        "31.4.1",
    ]
    assert result.source_refs == (
        "IS 456:2000 Cl. 31.1.1, 31.2.1, 31.3.1, 31.4.1",
        "IS456-2000-A6",
        "INDIA-2-FLAT-HAND-01-GEOMETRY",
        "INDIA-2-FLAT-HAND-01-MATERIAL",
        "INDIA-2-FLAT-HAND-01-LOAD",
    )
