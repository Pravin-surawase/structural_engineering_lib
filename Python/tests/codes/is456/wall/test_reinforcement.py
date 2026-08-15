"""INDIA-2-WALL-B Clause 32.5 reinforcement-check tests."""

from __future__ import annotations

import math

import pytest

from structural_lib.codes.is456.traceability import get_clause_refs
from structural_lib.codes.is456.wall import (
    BracedWallGeometry,
    WallAxialStatus,
    WallContractError,
    WallReinforcementInput,
    WallReinforcementKind,
    WallRotationRestraint,
    check_wall_minimum_reinforcement,
)


def _geometry(**overrides: object) -> BracedWallGeometry:
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


def _reinforcement(**overrides: object) -> WallReinforcementInput:
    values: dict[str, object] = {
        "geometry": _geometry(),
        "reinforcement_kind": WallReinforcementKind.DEFORMED_415_OR_GREATER,
        "vertical_bar_diameter_mm": 8.0,
        "vertical_bar_spacing_mm": 250.0,
        "horizontal_bar_diameter_mm": 10.0,
        "horizontal_bar_spacing_mm": 250.0,
        "reinforcement_basis_reference": "INDIA-2-WALL-HAND-01-REINFORCEMENT",
    }
    values.update(overrides)
    return WallReinforcementInput(**values)  # type: ignore[arg-type]


def test_frozen_benchmark_minimum_reinforcement_passes() -> None:
    result = check_wall_minimum_reinforcement(_reinforcement())

    assert result.vertical.minimum_ratio == pytest.approx(0.0012)
    assert result.vertical.required_area_mm2_per_m == pytest.approx(180.0)
    assert result.vertical.provided_area_mm2_per_m == pytest.approx(201.06192983)
    assert result.horizontal.minimum_ratio == pytest.approx(0.0020)
    assert result.horizontal.required_area_mm2_per_m == pytest.approx(300.0)
    assert result.horizontal.provided_area_mm2_per_m == pytest.approx(314.15926536)
    assert result.vertical.maximum_spacing_mm == pytest.approx(450.0)
    assert result.horizontal.maximum_spacing_mm == pytest.approx(450.0)
    assert result.vertical.status is WallAxialStatus.PASS
    assert result.horizontal.status is WallAxialStatus.PASS
    assert result.transverse_enclosure_required is False
    assert result.status is WallAxialStatus.PASS


@pytest.mark.parametrize(
    ("kind", "vertical_ratio", "horizontal_ratio"),
    (
        (WallReinforcementKind.DEFORMED_415_OR_GREATER, 0.0012, 0.0020),
        (WallReinforcementKind.WELDED_WIRE_FABRIC, 0.0012, 0.0020),
        (WallReinforcementKind.OTHER_BARS, 0.0015, 0.0025),
    ),
)
def test_material_category_selects_exact_minimum_ratios(
    kind: WallReinforcementKind,
    vertical_ratio: float,
    horizontal_ratio: float,
) -> None:
    result = check_wall_minimum_reinforcement(_reinforcement(reinforcement_kind=kind))

    assert result.vertical.minimum_ratio == pytest.approx(vertical_ratio)
    assert result.horizontal.minimum_ratio == pytest.approx(horizontal_ratio)


def test_maximum_spacing_uses_three_times_thickness_or_450() -> None:
    thin = check_wall_minimum_reinforcement(
        _reinforcement(
            geometry=_geometry(wall_thickness_mm=100.0),
            vertical_bar_spacing_mm=300.0,
            horizontal_bar_spacing_mm=300.0,
        )
    )
    assert thin.vertical.maximum_spacing_mm == pytest.approx(300.0)
    assert thin.vertical.spacing_status is WallAxialStatus.PASS

    thick = check_wall_minimum_reinforcement(
        _reinforcement(
            geometry=_geometry(wall_thickness_mm=200.0),
            vertical_bar_spacing_mm=450.0,
            horizontal_bar_spacing_mm=450.0,
        )
    )
    assert thick.vertical.maximum_spacing_mm == pytest.approx(450.0)
    assert thick.vertical.spacing_status is WallAxialStatus.PASS


def test_inadequate_area_and_excess_spacing_return_fail() -> None:
    area = check_wall_minimum_reinforcement(
        _reinforcement(
            vertical_bar_diameter_mm=6.0,
            horizontal_bar_diameter_mm=6.0,
            vertical_bar_spacing_mm=450.0,
            horizontal_bar_spacing_mm=450.0,
        )
    )
    assert area.vertical.area_status is WallAxialStatus.FAIL
    assert area.horizontal.area_status is WallAxialStatus.FAIL
    assert area.status is WallAxialStatus.FAIL

    spacing = check_wall_minimum_reinforcement(
        _reinforcement(
            vertical_bar_spacing_mm=451.0,
            horizontal_bar_spacing_mm=451.0,
        )
    )
    assert spacing.vertical.spacing_status is WallAxialStatus.FAIL
    assert spacing.horizontal.spacing_status is WallAxialStatus.FAIL
    assert spacing.status is WallAxialStatus.FAIL


def test_vertical_ratio_above_one_percent_requires_held_enclosure_route() -> None:
    result = check_wall_minimum_reinforcement(
        _reinforcement(
            vertical_bar_diameter_mm=16.0,
            vertical_bar_spacing_mm=100.0,
        )
    )

    assert result.vertical.provided_ratio > 0.01
    assert result.transverse_enclosure_required is True
    assert result.status is WallAxialStatus.FAIL


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("vertical_bar_diameter_mm", 0.0),
        ("vertical_bar_spacing_mm", math.inf),
        ("horizontal_bar_diameter_mm", -1.0),
        ("horizontal_bar_spacing_mm", 0.0),
    ),
)
def test_invalid_bar_geometry_fails_closed(field: str, value: float) -> None:
    with pytest.raises(WallContractError, match=field):
        _reinforcement(**{field: value})


def test_sixteen_millimetre_category_limit_is_enforced() -> None:
    with pytest.raises(WallContractError, match="must not exceed 16 mm"):
        _reinforcement(vertical_bar_diameter_mm=17.0)

    other = _reinforcement(
        reinforcement_kind=WallReinforcementKind.OTHER_BARS,
        vertical_bar_diameter_mm=20.0,
    )
    assert other.vertical_bar_diameter_mm == pytest.approx(20.0)


def test_wrong_type_and_blank_reference_fail_closed() -> None:
    with pytest.raises(WallContractError, match="WallReinforcementInput"):
        check_wall_minimum_reinforcement(object())  # type: ignore[arg-type]
    with pytest.raises(WallContractError, match="reinforcement_basis_reference"):
        _reinforcement(reinforcement_basis_reference=" ")


def test_clause_and_source_provenance_is_machine_visible() -> None:
    result = check_wall_minimum_reinforcement(_reinforcement())

    assert get_clause_refs(check_wall_minimum_reinforcement) == [
        "32.5",
        "32.5.1",
        "32.5.2",
    ]
    assert result.source_refs == (
        "IS 456:2000 Cl. 32.5-32.5.2",
        "IS456-2000-A6",
        "INDIA-2-WALL-HAND-01-REINFORCEMENT",
    )
