"""INDIA-2C structural benchmarks and issued-amendment dispositions.

A3 PDF112/printed2, Cl26.3.3(b)(2), controlled source SHA256
964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264,
replaces the absolute distribution-spacing maximum with 300 mm. At d=224 mm,
14@400 provides 384.8451 mm2/m above the independent 0.0012*1000*250=300
minimum and below the 250/8=31.25 mm diameter cap. A shortened 4000 mm span
also satisfies the basic 20 limit, isolating the old spacing false pass.
These altered software fixtures are not the published 5100 mm NPTEL case.
The ceiling conservatively checks the existing scalar; physical spacing
datum and drawing qualification remain outside these tests.
"""

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


@pytest.mark.parametrize(
    ("spacing_mm", "expected_pass"),
    [(300.0, True), (301.0, False), (400.0, False), (450.0, False), (451.0, False)],
)
def test_amended_distribution_ceiling_governs_adequately_reinforced_case(
    spacing_mm: float, expected_pass: bool
) -> None:
    original = _actions(upper_landing_effective_length_mm=550.0)
    actions = analyze_straight_flight_actions(
        replace(
            original.input,
            loads=replace(
                original.input.loads,
                load_basis_reference="AMD3-STAIR-ALTERED-4000MM-FIXTURE",
            ),
        )
    )
    result = design_straight_flight_staircase(
        _design_input(
            actions=actions,
            distribution_bar_diameter_mm=14.0,
            distribution_bar_spacing_mm=spacing_mm,
        )
    )
    spacing = next(
        check
        for check in result.governing_checks
        if check.check_id == "INDIA-2C-DIST-SPACING-01"
    )

    assert result.maximum_distribution_bar_spacing_mm == 300.0
    assert spacing.actual == spacing_mm and spacing.limit == 300.0
    assert spacing.passed is expected_pass
    assert all(
        check.passed
        for check in result.governing_checks
        if check.check_id != "INDIA-2C-DIST-SPACING-01"
    )
    assert result.is_strength_and_detailing_satisfied is expected_pass
    assert result.status is (
        StaircaseDesignStatus.PASS if expected_pass else StaircaseDesignStatus.FAIL
    )
    assert result.maximum_main_bar_spacing_mm == 300.0
    assert "IS 456:2000 Cl. 26.3.3(b)(2), Amendment 3 (August 2007)" in (
        result.source_refs
    )
    assert any("physical horizontal/soffit" in item for item in result.limitations)
    assert not result.complete_engineering_design_approved


@pytest.mark.parametrize(
    ("spacing_mm", "expected_pass"), [(250.0, True), (251.0, False)]
)
def test_distribution_depth_bound_remains_inclusive(
    spacing_mm: float, expected_pass: bool
) -> None:
    original = _actions()
    actions = analyze_straight_flight_actions(
        replace(
            original.input,
            geometry=replace(
                original.input.geometry,
                lower_landing_effective_length_mm=100.0,
                going_mm=300.0,
                upper_landing_effective_length_mm=100.0,
                waist_thickness_mm=75.0,
                landing_thickness_mm=75.0,
            ),
            loads=replace(
                original.input.loads,
                load_basis_reference="AMD3-STAIR-DEPTH-SOFTWARE-BOUNDARY",
            ),
        )
    )
    result = design_straight_flight_staircase(
        _design_input(
            actions=actions,
            effective_depth_mm=50.0,
            main_bar_diameter_mm=8.0,
            main_bar_spacing_mm=100.0,
            distribution_bar_diameter_mm=8.0,
            distribution_bar_spacing_mm=spacing_mm,
        )
    )
    spacing = next(
        check
        for check in result.governing_checks
        if check.check_id == "INDIA-2C-DIST-SPACING-01"
    )

    assert spacing.limit == result.maximum_distribution_bar_spacing_mm == 250.0
    assert spacing.passed is expected_pass
    assert all(
        check.passed
        for check in result.governing_checks
        if check.check_id != "INDIA-2C-DIST-SPACING-01"
    )
    assert result.status is (
        StaircaseDesignStatus.PASS if expected_pass else StaircaseDesignStatus.FAIL
    )
    assert result.maximum_main_bar_spacing_mm == 150.0
    assert not result.complete_engineering_design_approved


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
