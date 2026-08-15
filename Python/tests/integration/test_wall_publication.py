"""Public-contract proof for the composed braced-wall Python workflow."""

from __future__ import annotations

import dataclasses
import json

import pytest

import structural_lib
from structural_lib.codes.is456.wall import WallAxialStatus, WallContractError
from structural_lib.services import api as services_api


def _benchmark_request(**overrides: object) -> services_api.BracedWallDesignInput:
    values: dict[str, object] = {
        "case_id": "INDIA-2-WALL-HAND-01",
        "unsupported_height_mm": 3000.0,
        "lateral_restraint_spacing_mm": 4000.0,
        "wall_length_mm": 4000.0,
        "wall_thickness_mm": 150.0,
        "concrete_grade_nmm2": 20.0,
        "factored_axial_load_kn": 2000.0,
        "supplied_eccentricity_mm": 0.0,
        "vertical_bar_diameter_mm": 8.0,
        "vertical_bar_spacing_mm": 250.0,
        "horizontal_bar_diameter_mm": 10.0,
        "horizontal_bar_spacing_mm": 250.0,
        "bracing_basis_reference": "INDIA-2-WALL-HAND-01-BRACING",
        "action_basis_reference": "INDIA-2-WALL-HAND-01-ACTIONS",
        "reinforcement_basis_reference": ("INDIA-2-WALL-HAND-01-REINFORCEMENT"),
    }
    values.update(overrides)
    return services_api.BracedWallDesignInput(**values)  # type: ignore[arg-type]


def test_wall_has_one_canonical_public_function_and_types() -> None:
    assert (
        structural_lib.design_braced_wall_is456 is services_api.design_braced_wall_is456
    )
    for name in (
        "design_braced_wall_is456",
        "BracedWallDesignInput",
        "BracedWallDesignProvenance",
        "BracedWallDesignResult",
    ):
        assert name in services_api.__all__
        assert name in structural_lib.__all__


def test_public_composition_matches_frozen_benchmark_and_retains_review() -> None:
    result = structural_lib.design_braced_wall_is456(_benchmark_request())

    assert result.status is WallAxialStatus.PASS
    assert result.axial.geometry.effective_height_mm == pytest.approx(2250.0)
    assert result.axial.axial_capacity_n_per_mm == pytest.approx(684.0)
    assert result.axial.axial_demand_n_per_mm == pytest.approx(500.0)
    assert result.axial.utilization_ratio == pytest.approx(0.7309941520)
    assert result.reinforcement.vertical.required_area_mm2_per_m == pytest.approx(180.0)
    assert result.reinforcement.vertical.provided_area_mm2_per_m == pytest.approx(
        201.06192983
    )
    assert result.reinforcement.horizontal.required_area_mm2_per_m == pytest.approx(
        300.0
    )
    assert result.reinforcement.horizontal.provided_area_mm2_per_m == pytest.approx(
        314.15926536
    )
    assert result.provenance.workflow == "design_braced_wall_is456"
    assert result.provenance.benchmark_id == "INDIA-2-WALL-HAND-01"
    assert result.provenance.load_generation_status == (
        "not_generated_caller_supplied_factored_action"
    )
    assert result.qualified_review_required
    assert not result.complete_engineering_design_approved
    json.dumps(dataclasses.asdict(result))


def test_overload_and_inadequate_reinforcement_fail_the_composed_result() -> None:
    overloaded = structural_lib.design_braced_wall_is456(
        _benchmark_request(factored_axial_load_kn=3000.0)
    )
    under_reinforced = structural_lib.design_braced_wall_is456(
        _benchmark_request(
            vertical_bar_diameter_mm=6.0,
            horizontal_bar_diameter_mm=6.0,
            vertical_bar_spacing_mm=450.0,
            horizontal_bar_spacing_mm=450.0,
        )
    )

    assert overloaded.axial.status is WallAxialStatus.FAIL
    assert overloaded.status is WallAxialStatus.FAIL
    assert under_reinforced.reinforcement.status is WallAxialStatus.FAIL
    assert under_reinforced.status is WallAxialStatus.FAIL


def test_public_result_names_supported_and_held_boundaries() -> None:
    result = structural_lib.design_braced_wall_is456(_benchmark_request())

    assert "100-200 mm" in result.supported_case
    assert any("Applied moment" in item for item in result.held_cases)
    assert any("two reinforcement grids" in item for item in result.held_cases)
    assert any("Seismic" in item for item in result.held_cases)
    assert result.provenance.clause_refs == (
        "32.2.1",
        "32.2.2",
        "32.2.3",
        "32.2.4",
        "32.2.5",
        "32.5",
        "32.5.1",
        "32.5.2",
    )
    assert result.provenance.source_refs == (
        "IS 456:2000 Cl. 32.2.1-32.2.5",
        "IS456-2000-A6",
        "INDIA-2-WALL-HAND-01-BRACING",
        "INDIA-2-WALL-HAND-01-ACTIONS",
        "IS 456:2000 Cl. 32.5-32.5.2",
        "INDIA-2-WALL-HAND-01-REINFORCEMENT",
    )


def test_invalid_public_contract_fails_closed() -> None:
    with pytest.raises(WallContractError, match="BracedWallDesignInput"):
        services_api.design_braced_wall_is456(object())  # type: ignore[arg-type]
    with pytest.raises(WallContractError, match="case_id"):
        services_api.design_braced_wall_is456(_benchmark_request(case_id=" "))
    with pytest.raises(WallContractError, match="rotation_restraint"):
        services_api.design_braced_wall_is456(
            _benchmark_request(rotation_restraint="unsupported")
        )
    with pytest.raises(WallContractError, match="reinforcement_kind"):
        services_api.design_braced_wall_is456(
            _benchmark_request(reinforcement_kind="unsupported")
        )


def test_wall_is_not_advertised_before_wall_d_capability_packet() -> None:
    assert all(
        item.element != "wall"
        for item in services_api.get_supported_is456_capabilities()
    )
