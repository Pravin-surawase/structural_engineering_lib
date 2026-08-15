"""INDIA-2C structural design benchmarks and dispositions."""

from __future__ import annotations

from dataclasses import replace

import pytest

from structural_lib.codes.is456.staircase import (
    StaircaseContractError,
    StaircaseDesignStatus,
    StaircaseServiceabilityStatus,
    StraightFlightActionInput,
    StraightFlightDesignInput,
    StraightFlightLoads,
    StraightFlightStairGeometry,
    analyze_straight_flight_actions,
    design_straight_flight_staircase,
)


def _actions(
    *,
    upper_landing_effective_length_mm: float = 1650.0,
    ultimate_load_factor: float = 1.5,
) -> object:
    geometry = StraightFlightStairGeometry(
        lower_landing_effective_length_mm=750.0,
        going_mm=2700.0,
        upper_landing_effective_length_mm=upper_landing_effective_length_mm,
        flight_width_mm=1500.0,
        riser_mm=160.0,
        tread_mm=270.0,
        waist_thickness_mm=250.0,
        landing_thickness_mm=200.0,
    )
    loads = StraightFlightLoads(
        lower_landing_superimposed_service_load_kn_per_m2=6.0,
        flight_superimposed_service_load_kn_per_m2=6.0,
        upper_landing_superimposed_service_load_kn_per_m2=6.0,
        lower_landing_load_share=0.5,
        upper_landing_load_share=1.0,
        concrete_unit_weight_kn_per_m3=25.0,
        ultimate_load_factor=ultimate_load_factor,
        load_basis_reference="NPTEL-M9L20-EX9.1",
    )
    return analyze_straight_flight_actions(
        StraightFlightActionInput(geometry=geometry, loads=loads)
    )


def _design_input(**overrides: object) -> StraightFlightDesignInput:
    values: dict[str, object] = {
        "actions": _actions(),
        "effective_depth_mm": 224.0,
        "fck_n_per_mm2": 20.0,
        "fy_n_per_mm2": 415.0,
        "main_bar_diameter_mm": 12.0,
        "main_bar_spacing_mm": 120.0,
        "distribution_bar_diameter_mm": 8.0,
        "distribution_bar_spacing_mm": 160.0,
    }
    values.update(overrides)
    return StraightFlightDesignInput(**values)  # type: ignore[arg-type]


def test_nptel_example_9_1_flexure_shear_and_reinforcement_benchmark() -> None:
    result = design_straight_flight_staircase(_design_input())

    assert result.factored_moment_knm_per_m == pytest.approx(102.08 / 1.5, abs=0.04)
    assert result.ast_required_mm2_per_m == pytest.approx(920.64, abs=2.0)
    assert result.main_reinforcement_provided_mm2_per_m == pytest.approx(
        942.48, abs=0.1
    )
    assert result.distribution_reinforcement_provided_mm2_per_m == pytest.approx(
        314.16, abs=0.1
    )
    assert result.shear.tau_v_n_per_mm2 == pytest.approx(0.217, abs=0.002)
    assert result.shear.is_safe_without_shear_reinforcement


def test_nptel_example_requires_serviceability_review_without_invented_factor() -> None:
    result = design_straight_flight_staircase(_design_input())

    assert result.actual_span_to_depth_ratio == pytest.approx(5100.0 / 224.0)
    assert result.serviceability_status is StaircaseServiceabilityStatus.REVIEW_REQUIRED
    assert result.status is StaircaseDesignStatus.REVIEW_REQUIRED
    assert result.is_strength_and_detailing_satisfied
    assert not result.complete_engineering_design_approved


def test_shorter_supported_member_can_pass_basic_span_depth_boundary() -> None:
    actions = _actions(upper_landing_effective_length_mm=550.0)
    result = design_straight_flight_staircase(_design_input(actions=actions))

    assert result.actual_span_to_depth_ratio < 20.0
    assert result.status is StaircaseDesignStatus.PASS


def test_insufficient_provided_main_steel_returns_fail() -> None:
    result = design_straight_flight_staircase(_design_input(main_bar_spacing_mm=300.0))
    assert result.status is StaircaseDesignStatus.FAIL
    main_check = next(
        check
        for check in result.governing_checks
        if check.check_id == "INDIA-2C-MAIN-STEEL-01"
    )
    assert not main_check.passed


def test_singly_reinforced_capacity_exceedance_returns_fail_without_fake_ast() -> None:
    actions = _actions(ultimate_load_factor=5.0)
    result = design_straight_flight_staircase(_design_input(actions=actions))

    assert result.status is StaircaseDesignStatus.FAIL
    assert result.ast_required_mm2_per_m is None
    assert result.main_reinforcement_required_mm2_per_m is None
    main_check = next(
        check
        for check in result.governing_checks
        if check.check_id == "INDIA-2C-MAIN-STEEL-01"
    )
    assert main_check.limit is None


def test_effective_depth_outside_waist_fails_closed() -> None:
    with pytest.raises(StaircaseContractError, match="less than waist_thickness"):
        _design_input(effective_depth_mm=250.0)


def test_forged_action_result_fails_integrity_check() -> None:
    actions = _actions()
    assert hasattr(actions, "maximum_factored_moment_knm_per_m")
    forged = replace(
        actions,
        maximum_factored_moment_knm_per_m=(
            actions.maximum_factored_moment_knm_per_m + 1.0
        ),
    )
    with pytest.raises(StaircaseContractError, match="inconsistent"):
        design_straight_flight_staircase(_design_input(actions=forged))
