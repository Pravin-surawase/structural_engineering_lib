"""INDIA-2-WALL-A benchmark and fail-closed axial-kernel tests."""

from __future__ import annotations

import math

import pytest

from structural_lib.codes.is456.traceability import get_clause_refs
from structural_lib.codes.is456.wall import (
    BracedWallAxialInput,
    BracedWallGeometry,
    WallAxialStatus,
    WallContractError,
    WallRotationRestraint,
    check_braced_wall_axial_capacity,
    resolve_braced_wall_geometry,
)


def _benchmark_geometry(**overrides: object) -> BracedWallGeometry:
    values: dict[str, object] = {
        "unsupported_height_mm": 3000.0,
        "lateral_restraint_spacing_mm": 4000.0,
        "wall_length_mm": 4000.0,
        "wall_thickness_mm": 150.0,
        "rotation_restraint": WallRotationRestraint.RESTRAINED_BOTH_ENDS,
        "bracing_elements_in_two_directions": True,
        "lateral_forces_resisted_by_bracing_system": True,
        "diaphragm_transfer_confirmed": True,
        "lateral_connection_capacity_confirmed": True,
        "bracing_basis_reference": "INDIA-2-WALL-HAND-01-BRACING",
    }
    values.update(overrides)
    return BracedWallGeometry(**values)  # type: ignore[arg-type]


def _benchmark_input(**overrides: object) -> BracedWallAxialInput:
    values: dict[str, object] = {
        "geometry": _benchmark_geometry(),
        "concrete_grade_nmm2": 20.0,
        "factored_axial_load_kn": 2000.0,
        "supplied_eccentricity_mm": 0.0,
        "action_basis_reference": "INDIA-2-WALL-HAND-01-ACTIONS",
    }
    values.update(overrides)
    return BracedWallAxialInput(**values)  # type: ignore[arg-type]


def test_hand_benchmark_effective_height_eccentricity_and_capacity() -> None:
    result = check_braced_wall_axial_capacity(_benchmark_input())

    assert result.geometry.height_effective_component_mm == pytest.approx(2250.0)
    assert result.geometry.lateral_effective_component_mm == pytest.approx(3000.0)
    assert result.geometry.effective_height_mm == pytest.approx(2250.0)
    assert result.geometry.effective_height_to_thickness_ratio == pytest.approx(15.0)
    assert result.minimum_eccentricity_mm == pytest.approx(7.5)
    assert result.design_eccentricity_mm == pytest.approx(7.5)
    assert result.additional_eccentricity_mm == pytest.approx(13.5)
    assert result.effective_compression_thickness_mm == pytest.approx(114.0)
    assert result.axial_capacity_n_per_mm == pytest.approx(684.0, abs=1e-6)
    assert result.axial_capacity_kn_per_m == pytest.approx(684.0, abs=1e-6)
    assert result.total_axial_capacity_kn == pytest.approx(2736.0, abs=1e-6)
    assert result.axial_demand_n_per_mm == pytest.approx(500.0, abs=1e-6)
    assert result.axial_demand_kn_per_m == pytest.approx(500.0, abs=1e-6)
    assert result.utilization_ratio == pytest.approx(0.7309941520, abs=1e-10)
    assert result.status is WallAxialStatus.PASS


def test_actual_eccentricity_above_minimum_controls() -> None:
    result = check_braced_wall_axial_capacity(
        _benchmark_input(supplied_eccentricity_mm=15.0)
    )

    assert result.design_eccentricity_mm == pytest.approx(15.0)
    assert result.effective_compression_thickness_mm == pytest.approx(105.0)
    assert result.axial_capacity_n_per_mm == pytest.approx(630.0)


def test_unrestrained_rotation_uses_full_effective_components() -> None:
    geometry = _benchmark_geometry(
        rotation_restraint=WallRotationRestraint.NOT_RESTRAINED_BOTH_ENDS
    )
    result = resolve_braced_wall_geometry(geometry)

    assert result.height_effective_component_mm == pytest.approx(3000.0)
    assert result.lateral_effective_component_mm == pytest.approx(4000.0)
    assert result.effective_height_mm == pytest.approx(3000.0)
    assert result.effective_height_to_thickness_ratio == pytest.approx(20.0)


def test_lateral_restraint_can_control_effective_height() -> None:
    result = resolve_braced_wall_geometry(
        _benchmark_geometry(lateral_restraint_spacing_mm=2000.0)
    )

    assert result.effective_height_mm == pytest.approx(1500.0)


def test_slenderness_boundary_thirty_is_accepted_and_above_fails_closed() -> None:
    boundary = resolve_braced_wall_geometry(
        _benchmark_geometry(
            unsupported_height_mm=4000.0,
            lateral_restraint_spacing_mm=5000.0,
            wall_thickness_mm=100.0,
        )
    )
    assert boundary.effective_height_to_thickness_ratio == pytest.approx(30.0)

    with pytest.raises(WallContractError, match="must not exceed 30"):
        resolve_braced_wall_geometry(
            _benchmark_geometry(
                unsupported_height_mm=4100.0,
                lateral_restraint_spacing_mm=5000.0,
                wall_thickness_mm=100.0,
            )
        )


def test_valid_overload_returns_fail_disposition() -> None:
    result = check_braced_wall_axial_capacity(
        _benchmark_input(factored_axial_load_kn=3000.0)
    )

    assert result.utilization_ratio > 1.0
    assert result.status is WallAxialStatus.FAIL


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("unsupported_height_mm", 0.0),
        ("lateral_restraint_spacing_mm", math.inf),
        ("wall_length_mm", -1.0),
        ("wall_thickness_mm", 99.0),
        ("wall_thickness_mm", 201.0),
    ),
)
def test_invalid_geometry_fails_closed(field: str, value: float) -> None:
    with pytest.raises(WallContractError, match=field):
        _benchmark_geometry(**{field: value})


@pytest.mark.parametrize(
    "confirmation",
    (
        "bracing_elements_in_two_directions",
        "lateral_forces_resisted_by_bracing_system",
        "diaphragm_transfer_confirmed",
        "lateral_connection_capacity_confirmed",
    ),
)
def test_each_bracing_confirmation_is_required(confirmation: str) -> None:
    with pytest.raises(WallContractError, match=confirmation):
        _benchmark_geometry(**{confirmation: False})


def test_material_action_and_reference_contracts_fail_closed() -> None:
    with pytest.raises(WallContractError, match="standard M20-M60"):
        _benchmark_input(concrete_grade_nmm2=27.0)
    with pytest.raises(WallContractError, match="factored_axial_load_kn"):
        _benchmark_input(factored_axial_load_kn=0.0)
    with pytest.raises(WallContractError, match="supplied_eccentricity_mm"):
        _benchmark_input(supplied_eccentricity_mm=-1.0)
    with pytest.raises(WallContractError, match="action_basis_reference"):
        _benchmark_input(action_basis_reference=" ")


def test_nonpositive_empirical_compression_zone_fails_closed() -> None:
    with pytest.raises(WallContractError, match="effective compression thickness"):
        check_braced_wall_axial_capacity(
            _benchmark_input(supplied_eccentricity_mm=120.0)
        )


def test_wrong_types_fail_closed() -> None:
    with pytest.raises(WallContractError, match="BracedWallGeometry"):
        resolve_braced_wall_geometry(object())  # type: ignore[arg-type]
    with pytest.raises(WallContractError, match="BracedWallAxialInput"):
        check_braced_wall_axial_capacity(object())  # type: ignore[arg-type]


def test_clause_and_source_provenance_is_machine_visible() -> None:
    result = check_braced_wall_axial_capacity(_benchmark_input())

    assert get_clause_refs(resolve_braced_wall_geometry) == [
        "32.2.1",
        "32.2.3",
        "32.2.4",
    ]
    assert get_clause_refs(check_braced_wall_axial_capacity) == ["32.2.2", "32.2.5"]
    assert result.source_refs[:2] == (
        "IS 456:2000 Cl. 32.2.1-32.2.5",
        "IS456-2000-A6",
    )
    assert result.source_refs[-2:] == (
        "INDIA-2-WALL-HAND-01-BRACING",
        "INDIA-2-WALL-HAND-01-ACTIONS",
    )
    assert result.load_generation_status == (
        "not_generated_caller_supplied_factored_action"
    )
