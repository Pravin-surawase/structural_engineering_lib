"""INDIA-2-DEEP-B positive tie, anchorage, and side-face tests."""

from __future__ import annotations

import math

import pytest

from structural_lib.codes.is456.deep_beam import (
    DeepBeamActionInput,
    DeepBeamCheckStatus,
    DeepBeamContractError,
    DeepBeamGeometry,
    DeepBeamReinforcementInput,
    DeepBeamSupportType,
    check_simply_supported_deep_beam_reinforcement,
)
from structural_lib.codes.is456.traceability import get_clause_refs


def _geometry(**overrides: object) -> DeepBeamGeometry:
    values: dict[str, object] = {
        "centre_to_centre_span_mm": 3000.0,
        "clear_span_mm": 2800.0,
        "overall_depth_mm": 2000.0,
        "beam_width_mm": 300.0,
        "support_type": DeepBeamSupportType.SIMPLY_SUPPORTED,
        "solid_rectangular_section": True,
        "openings_present": False,
        "dapped_ends_present": False,
        "top_loaded": True,
        "hanging_action_required": False,
        "bearing_nodal_zone_verified": True,
        "geometry_basis_reference": "INDIA-2-DEEP-HAND-01-GEOMETRY",
        "bearing_nodal_zone_reference": "INDIA-2-DEEP-HAND-01-BEARING",
    }
    values.update(overrides)
    return DeepBeamGeometry(**values)  # type: ignore[arg-type]


def _action(**overrides: object) -> DeepBeamActionInput:
    values: dict[str, object] = {
        "geometry": _geometry(),
        "concrete_grade_nmm2": 30.0,
        "steel_grade_nmm2": 500.0,
        "factored_positive_moment_knm": 900.0,
        "action_basis_reference": "INDIA-2-DEEP-HAND-01-ACTIONS",
    }
    values.update(overrides)
    return DeepBeamActionInput(**values)  # type: ignore[arg-type]


def _reinforcement(**overrides: object) -> DeepBeamReinforcementInput:
    values: dict[str, object] = {
        "action": _action(),
        "main_bar_count": 4,
        "main_bar_diameter_mm": 22.0,
        "furthest_main_bar_from_tension_face_mm": 250.0,
        "main_bars_continuous_between_supports": True,
        "main_bars_bundled": False,
        "main_bar_splices_present": False,
        "left_support_embedment_mm": 850.0,
        "right_support_embedment_mm": 850.0,
        "face_grid_count": 2,
        "vertical_side_bar_diameter_mm": 10.0,
        "vertical_side_bar_spacing_mm": 300.0,
        "horizontal_side_bar_diameter_mm": 10.0,
        "horizontal_side_bar_spacing_mm": 250.0,
        "reinforcement_basis_reference": "INDIA-2-DEEP-HAND-01-REINFORCEMENT",
    }
    values.update(overrides)
    return DeepBeamReinforcementInput(**values)  # type: ignore[arg-type]


def test_frozen_benchmark_passes_with_exact_intermediates() -> None:
    result = check_simply_supported_deep_beam_reinforcement(_reinforcement())

    assert result.geometry.effective_span_mm == pytest.approx(3000.0, abs=1e-6)
    assert result.geometry.lever_arm_mm == pytest.approx(1400.0, abs=1e-6)
    assert result.positive_tie.required_area_mm2 == pytest.approx(
        1477.832512315271, abs=1e-6
    )
    assert result.positive_tie.provided_area_mm2 == pytest.approx(
        1520.53084433746, abs=1e-6
    )
    assert result.placement.permitted_zone_depth_mm == pytest.approx(350.0)
    assert result.anchorage.design_steel_stress_nmm2 == pytest.approx(435.0)
    assert result.anchorage.design_bond_stress_nmm2 == pytest.approx(2.4)
    assert result.anchorage.development_length_mm == pytest.approx(996.875)
    assert result.anchorage.required_embedment_mm == pytest.approx(797.5)
    assert result.vertical_side_face.required_area_mm2_per_m == pytest.approx(360.0)
    assert result.vertical_side_face.provided_area_mm2_per_m == pytest.approx(
        523.598775598299, abs=1e-6
    )
    assert result.horizontal_side_face.required_area_mm2_per_m == pytest.approx(600.0)
    assert result.horizontal_side_face.provided_area_mm2_per_m == pytest.approx(
        628.318530717959, abs=1e-6
    )
    assert result.status is DeepBeamCheckStatus.PASS
    assert result.shear_deemed_satisfied_within_clause_29_scope is True
    assert result.qualified_review_required is True
    assert result.complete_engineering_approval is False


def test_inadequate_positive_tie_is_a_fail_disposition() -> None:
    result = check_simply_supported_deep_beam_reinforcement(
        _reinforcement(main_bar_count=3)
    )

    assert result.positive_tie.status is DeepBeamCheckStatus.FAIL
    assert result.status is DeepBeamCheckStatus.FAIL
    assert result.shear_deemed_satisfied_within_clause_29_scope is False


def test_tie_placement_boundary_and_failure() -> None:
    boundary = check_simply_supported_deep_beam_reinforcement(
        _reinforcement(furthest_main_bar_from_tension_face_mm=350.0)
    )
    assert boundary.placement.status is DeepBeamCheckStatus.PASS

    outside = check_simply_supported_deep_beam_reinforcement(
        _reinforcement(furthest_main_bar_from_tension_face_mm=350.0001)
    )
    assert outside.placement.status is DeepBeamCheckStatus.FAIL
    assert outside.status is DeepBeamCheckStatus.FAIL


def test_discontinuous_main_bars_return_fail() -> None:
    result = check_simply_supported_deep_beam_reinforcement(
        _reinforcement(main_bars_continuous_between_supports=False)
    )

    assert result.continuity_status is DeepBeamCheckStatus.FAIL
    assert result.status is DeepBeamCheckStatus.FAIL


def test_each_support_anchorage_boundary_and_failure() -> None:
    boundary = check_simply_supported_deep_beam_reinforcement(
        _reinforcement(
            left_support_embedment_mm=797.5,
            right_support_embedment_mm=797.5,
        )
    )
    assert boundary.anchorage.status is DeepBeamCheckStatus.PASS

    left_fail = check_simply_supported_deep_beam_reinforcement(
        _reinforcement(left_support_embedment_mm=797.499)
    )
    assert left_fail.anchorage.left_status is DeepBeamCheckStatus.FAIL
    assert left_fail.anchorage.right_status is DeepBeamCheckStatus.PASS
    assert left_fail.status is DeepBeamCheckStatus.FAIL

    right_fail = check_simply_supported_deep_beam_reinforcement(
        _reinforcement(right_support_embedment_mm=797.499)
    )
    assert right_fail.anchorage.right_status is DeepBeamCheckStatus.FAIL
    assert right_fail.status is DeepBeamCheckStatus.FAIL


@pytest.mark.parametrize(
    ("grade", "expected_bond_stress"),
    (
        (20.0, 1.92),
        (25.0, 2.24),
        (30.0, 2.40),
        (35.0, 2.72),
        (40.0, 3.04),
        (60.0, 3.04),
    ),
)
def test_normalized_deformed_tension_bond_stress_lookup(
    grade: float, expected_bond_stress: float
) -> None:
    result = check_simply_supported_deep_beam_reinforcement(
        _reinforcement(action=_action(concrete_grade_nmm2=grade))
    )

    assert result.anchorage.design_bond_stress_nmm2 == pytest.approx(
        expected_bond_stress
    )


def test_side_face_area_and_spacing_failures_are_visible() -> None:
    area_fail = check_simply_supported_deep_beam_reinforcement(
        _reinforcement(
            vertical_side_bar_diameter_mm=6.0,
            vertical_side_bar_spacing_mm=450.0,
            horizontal_side_bar_diameter_mm=6.0,
            horizontal_side_bar_spacing_mm=450.0,
        )
    )
    assert area_fail.vertical_side_face.area_status is DeepBeamCheckStatus.FAIL
    assert area_fail.horizontal_side_face.area_status is DeepBeamCheckStatus.FAIL
    assert area_fail.status is DeepBeamCheckStatus.FAIL

    spacing_fail = check_simply_supported_deep_beam_reinforcement(
        _reinforcement(
            vertical_side_bar_spacing_mm=451.0,
            horizontal_side_bar_spacing_mm=451.0,
        )
    )
    assert spacing_fail.vertical_side_face.spacing_status is DeepBeamCheckStatus.FAIL
    assert spacing_fail.horizontal_side_face.spacing_status is DeepBeamCheckStatus.FAIL
    assert spacing_fail.status is DeepBeamCheckStatus.FAIL


def test_one_and_two_grid_width_rules_are_fail_closed() -> None:
    one_grid = check_simply_supported_deep_beam_reinforcement(
        _reinforcement(
            action=_action(geometry=_geometry(beam_width_mm=200.0)),
            face_grid_count=1,
        )
    )
    assert one_grid.vertical_side_face.required_face_grid_count == 1

    with pytest.raises(DeepBeamContractError, match="face_grid_count must be 1"):
        _reinforcement(
            action=_action(geometry=_geometry(beam_width_mm=200.0)),
            face_grid_count=2,
        )
    with pytest.raises(DeepBeamContractError, match="face_grid_count must be 2"):
        _reinforcement(face_grid_count=1)
    with pytest.raises(DeepBeamContractError, match="integer 1 or 2"):
        _reinforcement(face_grid_count=3)


def test_transverse_enclosure_boundary_is_held_fail_closed() -> None:
    below = check_simply_supported_deep_beam_reinforcement(
        _reinforcement(
            vertical_side_bar_diameter_mm=16.0,
            vertical_side_bar_spacing_mm=140.0,
        )
    )
    assert below.vertical_side_face.provided_ratio < 0.01

    with pytest.raises(DeepBeamContractError, match="transverse-enclosure"):
        check_simply_supported_deep_beam_reinforcement(
            _reinforcement(
                vertical_side_bar_diameter_mm=16.0,
                vertical_side_bar_spacing_mm=130.0,
            )
        )


def test_bundles_splices_and_large_side_bars_are_excluded() -> None:
    with pytest.raises(DeepBeamContractError, match="main_bars_bundled"):
        _reinforcement(main_bars_bundled=True)
    with pytest.raises(DeepBeamContractError, match="main_bar_splices_present"):
        _reinforcement(main_bar_splices_present=True)
    with pytest.raises(DeepBeamContractError, match="must not exceed 16 mm"):
        _reinforcement(vertical_side_bar_diameter_mm=16.1)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("main_bar_diameter_mm", 0.0),
        ("furthest_main_bar_from_tension_face_mm", math.inf),
        ("left_support_embedment_mm", -1.0),
        ("vertical_side_bar_spacing_mm", math.nan),
        ("horizontal_side_bar_diameter_mm", 0.0),
    ),
)
def test_invalid_reinforcement_geometry_fails_closed(field: str, value: float) -> None:
    with pytest.raises(DeepBeamContractError, match=field):
        _reinforcement(**{field: value})


def test_count_continuity_type_reference_and_wrong_input_fail_closed() -> None:
    with pytest.raises(DeepBeamContractError, match="positive integer"):
        _reinforcement(main_bar_count=True)
    with pytest.raises(DeepBeamContractError, match="must be a boolean"):
        _reinforcement(main_bars_continuous_between_supports=1)
    with pytest.raises(DeepBeamContractError, match="reinforcement_basis_reference"):
        _reinforcement(reinforcement_basis_reference=" ")
    with pytest.raises(DeepBeamContractError, match="DeepBeamReinforcementInput"):
        check_simply_supported_deep_beam_reinforcement(object())  # type: ignore[arg-type]


def test_clause_and_source_provenance_is_machine_visible() -> None:
    result = check_simply_supported_deep_beam_reinforcement(_reinforcement())

    assert get_clause_refs(check_simply_supported_deep_beam_reinforcement) == [
        "29.1",
        "29.2",
        "29.3.1",
        "29.3.4",
        "26.2.1",
        "26.2.1.1",
        "32.5",
        "32.5.1",
        "32.5.2",
    ]
    assert result.source_refs == (
        "IS 456:2000 Cl. 29.1(b), 29.2, 29.3.1, 29.3.4",
        "IS 456:2000 Cl. 26.2.1-26.2.1.1, 32.5-32.5.2",
        "IS456-2000-A6",
        "IS456-AMD3-DEEP-SIDEFACE",
        "INDIA-2-DEEP-HAND-01-GEOMETRY",
        "INDIA-2-DEEP-HAND-01-BEARING",
        "INDIA-2-DEEP-HAND-01-ACTIONS",
        "INDIA-2-DEEP-HAND-01-REINFORCEMENT",
    )
