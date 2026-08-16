"""INDIA-2-COMBINED-A benchmark, boundary, and traceability tests."""

from __future__ import annotations

import math
from dataclasses import FrozenInstanceError

import pytest

from structural_lib.codes.is456.combined_footing import (
    CombinedFootingActionInput,
    CombinedFootingAnalysisMethod,
    CombinedFootingContractError,
    CombinedFootingGeometryInput,
    CombinedFootingInput,
    CombinedFootingPressureModel,
    CombinedFootingSectionKind,
    CombinedFootingTensionFace,
    analyze_symmetric_combined_footing,
    resolve_symmetric_combined_footing_geometry,
)
from structural_lib.codes.is456.traceability import get_clause_refs


def _geometry(**overrides: object) -> CombinedFootingGeometryInput:
    values: dict[str, object] = {
        "footing_length_mm": 6000.0,
        "footing_width_mm": 2500.0,
        "overall_depth_mm": 850.0,
        "effective_depth_mm": 750.0,
        "column_side_mm": 500.0,
        "left_column_center_x_mm": 1000.0,
        "right_column_center_x_mm": 5000.0,
        "column_count": 2,
        "columns_identical": True,
        "columns_square": True,
        "columns_centered_across_width": True,
        "foundation_on_soil": True,
        "constant_depth": True,
        "openings_present": False,
        "pedestals_present": False,
        "analysis_method": CombinedFootingAnalysisMethod.CONVENTIONAL_RIGID,
        "pressure_model": CombinedFootingPressureModel.UNIFORM,
        "rigid_footing_verified": True,
        "rigidity_basis_reference": "INDIA-2-COMBINED-HAND-01-RIGIDITY",
        "geometry_basis_reference": "INDIA-2-COMBINED-HAND-01-GEOMETRY",
    }
    values.update(overrides)
    return CombinedFootingGeometryInput(**values)  # type: ignore[arg-type]


def _actions(**overrides: object) -> CombinedFootingActionInput:
    values: dict[str, object] = {
        "service_axial_load_each_kn": 900.0,
        "factored_axial_load_each_kn": 1350.0,
        "service_uniform_carrier_kn_per_m2": 25.0,
        "factored_uniform_carrier_kn_per_m2": 37.5,
        "allowable_gross_bearing_pressure_kn_per_m2": 150.0,
        "load_combination_approved": True,
        "bearing_and_settlement_approved": True,
        "pressure_uniformity_approved": True,
        "distributed_carrier_cancellation_approved": True,
        "column_moments_present": False,
        "horizontal_actions_present": False,
        "uplift_or_load_reversal_present": False,
        "load_basis_reference": "INDIA-2-COMBINED-HAND-01-LOAD",
        "bearing_settlement_basis_reference": ("INDIA-2-COMBINED-HAND-01-GEOTECHNICAL"),
        "cancellation_basis_reference": "INDIA-2-COMBINED-HAND-01-CANCELLATION",
    }
    values.update(overrides)
    return CombinedFootingActionInput(**values)  # type: ignore[arg-type]


def _input(**overrides: object) -> CombinedFootingInput:
    values: dict[str, object] = {
        "geometry": _geometry(),
        "actions": _actions(),
    }
    values.update(overrides)
    return CombinedFootingInput(**values)  # type: ignore[arg-type]


def test_frozen_geometry_and_punching_perimeters() -> None:
    result = resolve_symmetric_combined_footing_geometry(_geometry())

    assert result.plan_area_m2 == pytest.approx(15.0)
    assert result.footing_centroid_x_mm == pytest.approx(3000.0)
    assert result.column_spacing_mm == pytest.approx(4000.0)
    assert result.inter_column_clear_gap_mm == pytest.approx(3500.0)
    assert result.equal_end_projection_mm == pytest.approx(750.0)
    assert result.transverse_column_face_cantilever_mm == pytest.approx(1000.0)
    assert result.punching_critical_side_mm == pytest.approx(1250.0)
    assert result.punching_area_each_m2 == pytest.approx(1.5625)
    assert result.punching_perimeter_each_mm == pytest.approx(5000.0)
    assert result.rigid_uniform_pressure_eligible is True


def test_frozen_service_pressure_resultants_and_net_action_carrier() -> None:
    result = analyze_symmetric_combined_footing(_input())

    assert result.service_column_resultant_kn == pytest.approx(1800.0)
    assert result.service_column_resultant_x_mm == pytest.approx(3000.0)
    assert result.service_total_vertical_load_kn == pytest.approx(2175.0)
    assert result.service_total_resultant_x_mm == pytest.approx(3000.0)
    assert result.gross_service_pressure_kn_per_m2 == pytest.approx(145.0)
    assert result.gross_service_bearing_utilization == pytest.approx(145.0 / 150.0)
    assert result.gross_service_bearing_within_allowable is True
    assert result.factored_column_resultant_kn == pytest.approx(2700.0)
    assert result.factored_column_resultant_x_mm == pytest.approx(3000.0)
    assert result.factored_total_vertical_load_kn == pytest.approx(3262.5)
    assert result.gross_factored_pressure_kn_per_m2 == pytest.approx(217.5)
    assert result.net_factored_structural_pressure_kn_per_m2 == pytest.approx(180.0)
    assert result.upward_line_load_kn_per_m == pytest.approx(450.0)
    assert result.service_resultant_alignment_residual_mm == pytest.approx(0.0)
    assert result.factored_resultant_alignment_residual_mm == pytest.approx(0.0)


def test_frozen_longitudinal_sections_and_sign_convention() -> None:
    result = analyze_symmetric_combined_footing(_input())

    assert result.left_free_edge.x_mm == pytest.approx(0.0)
    assert result.left_free_edge.shear_kn == pytest.approx(0.0)
    assert result.left_free_edge.moment_kn_m == pytest.approx(0.0)
    assert result.left_outer_one_way_shear.x_mm == pytest.approx(0.0)
    assert result.left_outer_one_way_shear.shear_demand_kn == pytest.approx(0.0)
    assert result.left_outer_column_face.x_mm == pytest.approx(750.0)
    assert result.left_outer_column_face.moment_kn_m == pytest.approx(126.5625)
    assert (
        result.left_outer_column_face.tension_face is CombinedFootingTensionFace.BOTTOM
    )
    assert result.left_inner_column_face.x_mm == pytest.approx(1250.0)
    assert result.left_inner_column_face.moment_kn_m == pytest.approx(14.0625)
    assert result.left_inner_one_way_shear.x_mm == pytest.approx(2000.0)
    assert result.left_inner_one_way_shear.shear_kn == pytest.approx(-450.0)
    assert result.left_inner_one_way_shear.shear_demand_kn == pytest.approx(450.0)
    assert result.inter_column_midpoint.x_mm == pytest.approx(3000.0)
    assert result.inter_column_midpoint.shear_kn == pytest.approx(0.0)
    assert result.inter_column_midpoint.moment_kn_m == pytest.approx(-675.0)
    assert result.inter_column_midpoint.tension_face is CombinedFootingTensionFace.TOP
    assert result.right_inner_one_way_shear.x_mm == pytest.approx(4000.0)
    assert result.right_inner_one_way_shear.shear_kn == pytest.approx(450.0)
    assert result.right_inner_column_face.moment_kn_m == pytest.approx(14.0625)
    assert result.right_outer_column_face.moment_kn_m == pytest.approx(126.5625)
    assert result.right_outer_one_way_shear.shear_demand_kn == pytest.approx(0.0)
    assert result.right_free_edge.x_mm == pytest.approx(6000.0)
    assert result.right_free_edge.shear_kn == pytest.approx(0.0)
    assert result.right_free_edge.moment_kn_m == pytest.approx(0.0)
    assert result.vertical_equilibrium_residual_kn == pytest.approx(0.0)
    assert result.moment_equilibrium_residual_kn_m == pytest.approx(0.0)


def test_transverse_action_includes_flexure_and_one_way_shear_demand() -> None:
    result = analyze_symmetric_combined_footing(_input())

    assert result.transverse.column_face_cantilever_mm == pytest.approx(1000.0)
    assert result.transverse.moment_kn_m_per_m == pytest.approx(90.0)
    assert result.transverse.one_way_shear_section_from_column_face_mm == pytest.approx(
        750.0
    )
    assert result.transverse.one_way_shear_demand_kn_per_m == pytest.approx(45.0)


def test_valid_bearing_failure_is_reported_without_leaving_domain() -> None:
    result = analyze_symmetric_combined_footing(
        _input(actions=_actions(allowable_gross_bearing_pressure_kn_per_m2=140.0))
    )

    assert result.gross_service_pressure_kn_per_m2 == pytest.approx(145.0)
    assert result.gross_service_bearing_utilization == pytest.approx(145.0 / 140.0)
    assert result.gross_service_bearing_within_allowable is False


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("footing_length_mm", 0.0),
        ("footing_width_mm", math.inf),
        ("overall_depth_mm", math.nan),
        ("effective_depth_mm", -1.0),
        ("column_side_mm", True),
        ("left_column_center_x_mm", "1000"),
        ("right_column_center_x_mm", 0.0),
    ),
)
def test_invalid_geometry_scalars_fail_closed(field: str, value: object) -> None:
    with pytest.raises(CombinedFootingContractError, match=field):
        _geometry(**{field: value})


def test_rectangular_depth_and_column_location_boundaries_fail_closed() -> None:
    with pytest.raises(CombinedFootingContractError, match="must exceed"):
        _geometry(footing_length_mm=2500.0)
    with pytest.raises(CombinedFootingContractError, match="at least 150"):
        _geometry(overall_depth_mm=149.999)
    with pytest.raises(CombinedFootingContractError, match="less than overall"):
        _geometry(effective_depth_mm=850.0)
    with pytest.raises(CombinedFootingContractError, match="column_side_mm"):
        _geometry(column_side_mm=2500.0)
    with pytest.raises(CombinedFootingContractError, match="left_column_center"):
        _geometry(left_column_center_x_mm=5000.0)
    with pytest.raises(CombinedFootingContractError, match="equal longitudinal"):
        _geometry(right_column_center_x_mm=4900.0)


def test_critical_section_and_punching_boundaries_fail_closed() -> None:
    with pytest.raises(CombinedFootingContractError, match="end projection"):
        _geometry(
            footing_length_mm=5900.0,
            left_column_center_x_mm=900.0,
            right_column_center_x_mm=5000.0,
        )
    with pytest.raises(CombinedFootingContractError, match="inter-column gap"):
        _geometry(
            footing_length_mm=4000.0,
            left_column_center_x_mm=1100.0,
            right_column_center_x_mm=2900.0,
        )
    with pytest.raises(CombinedFootingContractError, match="transverse.*cantilever"):
        _geometry(footing_width_mm=1900.0)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("column_count", 3),
        ("columns_identical", False),
        ("columns_square", False),
        ("columns_centered_across_width", False),
        ("foundation_on_soil", False),
        ("constant_depth", False),
        ("openings_present", True),
        ("pedestals_present", True),
        ("rigid_footing_verified", False),
        ("analysis_method", "elastic_line"),
        ("pressure_model", "linear"),
    ),
)
def test_each_geometry_scope_carrier_fails_closed(field: str, value: object) -> None:
    with pytest.raises(CombinedFootingContractError, match=field):
        _geometry(**{field: value})


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("service_axial_load_each_kn", 0.0),
        ("factored_axial_load_each_kn", math.inf),
        ("service_uniform_carrier_kn_per_m2", math.nan),
        ("factored_uniform_carrier_kn_per_m2", -1.0),
        ("allowable_gross_bearing_pressure_kn_per_m2", True),
    ),
)
def test_invalid_action_scalars_fail_closed(field: str, value: object) -> None:
    with pytest.raises(CombinedFootingContractError, match=field):
        _actions(**{field: value})


def test_action_factors_and_unsupported_actions_fail_closed() -> None:
    with pytest.raises(CombinedFootingContractError, match="must not be less"):
        _actions(factored_axial_load_each_kn=800.0)
    with pytest.raises(CombinedFootingContractError, match="ratios must match"):
        _actions(factored_uniform_carrier_kn_per_m2=35.0)
    for field, value in (
        ("load_combination_approved", False),
        ("bearing_and_settlement_approved", False),
        ("pressure_uniformity_approved", False),
        ("distributed_carrier_cancellation_approved", False),
        ("column_moments_present", True),
        ("horizontal_actions_present", True),
        ("uplift_or_load_reversal_present", True),
    ):
        with pytest.raises(CombinedFootingContractError, match=field):
            _actions(**{field: value})


@pytest.mark.parametrize(
    "field",
    (
        "rigidity_basis_reference",
        "geometry_basis_reference",
    ),
)
def test_geometry_references_are_required(field: str) -> None:
    with pytest.raises(CombinedFootingContractError, match=field):
        _geometry(**{field: " "})


@pytest.mark.parametrize(
    "field",
    (
        "load_basis_reference",
        "bearing_settlement_basis_reference",
        "cancellation_basis_reference",
    ),
)
def test_action_references_are_required(field: str) -> None:
    with pytest.raises(CombinedFootingContractError, match=field):
        _actions(**{field: " "})


def test_wrong_typed_inputs_fail_closed() -> None:
    with pytest.raises(CombinedFootingContractError, match="geometry"):
        CombinedFootingInput(geometry=object(), actions=_actions())  # type: ignore[arg-type]
    with pytest.raises(CombinedFootingContractError, match="actions"):
        CombinedFootingInput(geometry=_geometry(), actions=object())  # type: ignore[arg-type]
    with pytest.raises(CombinedFootingContractError, match="geometry"):
        resolve_symmetric_combined_footing_geometry(object())  # type: ignore[arg-type]
    with pytest.raises(CombinedFootingContractError, match="footing_input"):
        analyze_symmetric_combined_footing(object())  # type: ignore[arg-type]


def test_results_are_frozen_and_deterministic() -> None:
    first = analyze_symmetric_combined_footing(_input())
    second = analyze_symmetric_combined_footing(_input())

    assert first == second
    with pytest.raises(FrozenInstanceError):
        first.upward_line_load_kn_per_m = 0.0  # type: ignore[misc]


@pytest.mark.parametrize(
    ("length", "width", "depth", "column", "left_x", "right_x"),
    (
        (6000.0, 2500.0, 750.0, 500.0, 1000.0, 5000.0),
        (7200.0, 3000.0, 800.0, 600.0, 1300.0, 5900.0),
        (8000.0, 3200.0, 900.0, 600.0, 1500.0, 6500.0),
    ),
)
def test_symmetric_cases_close_vertical_and_moment_equilibrium(
    length: float,
    width: float,
    depth: float,
    column: float,
    left_x: float,
    right_x: float,
) -> None:
    result = analyze_symmetric_combined_footing(
        _input(
            geometry=_geometry(
                footing_length_mm=length,
                footing_width_mm=width,
                overall_depth_mm=depth + 100.0,
                effective_depth_mm=depth,
                column_side_mm=column,
                left_column_center_x_mm=left_x,
                right_column_center_x_mm=right_x,
            )
        )
    )

    assert result.service_resultant_alignment_residual_mm == pytest.approx(0.0)
    assert result.factored_resultant_alignment_residual_mm == pytest.approx(0.0)
    assert result.vertical_equilibrium_residual_kn == pytest.approx(0.0, abs=1e-9)
    assert result.moment_equilibrium_residual_kn_m == pytest.approx(0.0, abs=1e-9)
    assert result.left_outer_column_face.moment_kn_m == pytest.approx(
        result.right_outer_column_face.moment_kn_m
    )
    assert result.left_inner_column_face.moment_kn_m == pytest.approx(
        result.right_inner_column_face.moment_kn_m
    )


def test_section_kinds_and_source_provenance_are_exact() -> None:
    result = analyze_symmetric_combined_footing(_input())

    assert (
        result.left_outer_column_face.kind
        is CombinedFootingSectionKind.LEFT_OUTER_COLUMN_FACE
    )
    assert (
        result.inter_column_midpoint.kind
        is CombinedFootingSectionKind.INTER_COLUMN_MIDPOINT
    )
    assert result.right_free_edge.kind is CombinedFootingSectionKind.RIGHT_FREE_EDGE
    assert result.source_refs[:4] == (
        "IS 456:2000 Cl. 34.1, 34.1.2, 34.2.3.1, 34.2.4.1",
        "IS456-2000-A5",
        "IS456-AMD6-2024",
        "NPTEL-AFE-C3 Sections 3.7, 3.8, 3.14",
    )
    assert "INDIA-2-COMBINED-HAND-01-GEOMETRY" in result.source_refs
    assert "INDIA-2-COMBINED-HAND-01-LOAD" in result.source_refs
    assert "INDIA-2-COMBINED-HAND-01-RIGIDITY" in result.geometry.source_refs


def test_clause_registration_is_exact() -> None:
    expected = ["34.1", "34.2.3.1", "34.2.4.1"]
    assert get_clause_refs(resolve_symmetric_combined_footing_geometry) == expected
    assert get_clause_refs(analyze_symmetric_combined_footing) == expected
