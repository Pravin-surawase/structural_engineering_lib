"""INDIA-2-DEEP-A benchmark and fail-closed geometry tests."""

from __future__ import annotations

import math

import pytest

from structural_lib.codes.is456.deep_beam import (
    DeepBeamActionInput,
    DeepBeamContractError,
    DeepBeamGeometry,
    DeepBeamLeverArmCase,
    DeepBeamSupportType,
    resolve_simply_supported_deep_beam_geometry,
)
from structural_lib.codes.is456.traceability import get_clause_refs


def _benchmark_geometry(**overrides: object) -> DeepBeamGeometry:
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


def _benchmark_action(**overrides: object) -> DeepBeamActionInput:
    values: dict[str, object] = {
        "geometry": _benchmark_geometry(),
        "concrete_grade_nmm2": 30.0,
        "steel_grade_nmm2": 500.0,
        "factored_positive_moment_knm": 900.0,
        "action_basis_reference": "INDIA-2-DEEP-HAND-01-ACTIONS",
    }
    values.update(overrides)
    return DeepBeamActionInput(**values)  # type: ignore[arg-type]


def test_hand_benchmark_effective_span_classification_and_lever_arm() -> None:
    result = resolve_simply_supported_deep_beam_geometry(_benchmark_geometry())

    assert result.centre_to_centre_span_component_mm == pytest.approx(3000.0)
    assert result.clear_span_component_mm == pytest.approx(3220.0)
    assert result.effective_span_mm == pytest.approx(3000.0)
    assert result.effective_span_to_depth_ratio == pytest.approx(1.5)
    assert result.lever_arm_case is DeepBeamLeverArmCase.RATIO_ONE_TO_TWO
    assert result.lever_arm_mm == pytest.approx(1400.0)
    assert result.positive_reinforcement_zone_depth_mm == pytest.approx(350.0)


def test_clear_span_component_can_govern_effective_span() -> None:
    result = resolve_simply_supported_deep_beam_geometry(
        _benchmark_geometry(centre_to_centre_span_mm=4000.0)
    )

    assert result.clear_span_component_mm == pytest.approx(3220.0)
    assert result.effective_span_mm == pytest.approx(3220.0)


def test_ratio_below_one_uses_point_six_span_lever_arm() -> None:
    result = resolve_simply_supported_deep_beam_geometry(
        _benchmark_geometry(overall_depth_mm=4000.0)
    )

    assert result.effective_span_to_depth_ratio == pytest.approx(0.75)
    assert result.lever_arm_case is DeepBeamLeverArmCase.RATIO_BELOW_ONE
    assert result.lever_arm_mm == pytest.approx(1800.0)


def test_ratio_one_is_continuous_between_lever_arm_branches() -> None:
    result = resolve_simply_supported_deep_beam_geometry(
        _benchmark_geometry(overall_depth_mm=3000.0)
    )

    assert result.effective_span_to_depth_ratio == pytest.approx(1.0)
    assert result.lever_arm_case is DeepBeamLeverArmCase.RATIO_ONE_TO_TWO
    assert result.lever_arm_mm == pytest.approx(1800.0)


def test_ratio_just_below_two_is_accepted_and_two_fails_closed() -> None:
    accepted = resolve_simply_supported_deep_beam_geometry(
        _benchmark_geometry(overall_depth_mm=1500.1)
    )
    assert accepted.effective_span_to_depth_ratio < 2.0

    with pytest.raises(DeepBeamContractError, match="must be less than 2.0"):
        resolve_simply_supported_deep_beam_geometry(
            _benchmark_geometry(overall_depth_mm=1500.0)
        )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("centre_to_centre_span_mm", 0.0),
        ("clear_span_mm", math.inf),
        ("overall_depth_mm", -1.0),
        ("beam_width_mm", math.nan),
    ),
)
def test_invalid_dimensions_fail_closed(field: str, value: float) -> None:
    with pytest.raises(DeepBeamContractError, match=field):
        _benchmark_geometry(**{field: value})


def test_clear_span_must_be_less_than_support_centre_span() -> None:
    with pytest.raises(DeepBeamContractError, match="clear_span_mm"):
        _benchmark_geometry(clear_span_mm=3000.0)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("solid_rectangular_section", False),
        ("openings_present", True),
        ("dapped_ends_present", True),
        ("top_loaded", False),
        ("hanging_action_required", True),
        ("bearing_nodal_zone_verified", False),
    ),
)
def test_each_topology_and_external_confirmation_is_required(
    field: str, value: bool
) -> None:
    with pytest.raises(DeepBeamContractError, match=field):
        _benchmark_geometry(**{field: value})


def test_support_type_and_references_fail_closed() -> None:
    with pytest.raises(DeepBeamContractError, match="support_type"):
        _benchmark_geometry(support_type="continuous")
    with pytest.raises(DeepBeamContractError, match="geometry_basis_reference"):
        _benchmark_geometry(geometry_basis_reference=" ")
    with pytest.raises(DeepBeamContractError, match="bearing_nodal_zone_reference"):
        _benchmark_geometry(bearing_nodal_zone_reference=" ")


def test_action_material_and_reference_contracts() -> None:
    accepted = _benchmark_action()
    assert accepted.concrete_grade_nmm2 == pytest.approx(30.0)
    assert accepted.steel_grade_nmm2 == pytest.approx(500.0)
    assert accepted.factored_positive_moment_knm == pytest.approx(900.0)

    with pytest.raises(DeepBeamContractError, match="standard M20-M60"):
        _benchmark_action(concrete_grade_nmm2=27.0)
    with pytest.raises(DeepBeamContractError, match="Fe415 or Fe500"):
        _benchmark_action(steel_grade_nmm2=550.0)
    with pytest.raises(DeepBeamContractError, match="factored_positive_moment_knm"):
        _benchmark_action(factored_positive_moment_knm=0.0)
    with pytest.raises(DeepBeamContractError, match="action_basis_reference"):
        _benchmark_action(action_basis_reference=" ")


def test_wrong_types_fail_closed() -> None:
    with pytest.raises(DeepBeamContractError, match="DeepBeamGeometry"):
        DeepBeamActionInput(
            geometry=object(),  # type: ignore[arg-type]
            concrete_grade_nmm2=30.0,
            steel_grade_nmm2=500.0,
            factored_positive_moment_knm=900.0,
            action_basis_reference="benchmark",
        )
    with pytest.raises(DeepBeamContractError, match="DeepBeamGeometry"):
        resolve_simply_supported_deep_beam_geometry(object())  # type: ignore[arg-type]


def test_clause_and_source_provenance_is_machine_visible() -> None:
    result = resolve_simply_supported_deep_beam_geometry(_benchmark_geometry())

    assert get_clause_refs(resolve_simply_supported_deep_beam_geometry) == [
        "29.1",
        "29.2",
        "29.3.1",
    ]
    assert result.source_refs == (
        "IS 456:2000 Cl. 29.1-29.3.1",
        "IS456-2000-A6",
        "INDIA-2-DEEP-HAND-01-GEOMETRY",
        "INDIA-2-DEEP-HAND-01-BEARING",
    )
