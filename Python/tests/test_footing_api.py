"""Focused contract tests for Phase B1 isolated-footing orchestration."""

from __future__ import annotations

import pytest

from structural_lib.core.data_types import FootingType
from structural_lib.core.errors import ValidationError
from structural_lib.services.footing_api import (
    ConcentricIsolatedFootingInput,
    design_concentric_isolated_footing_is456,
)


def _input(**overrides: object) -> ConcentricIsolatedFootingInput:
    values: dict[str, object] = {
        "case_id": "FOOT-B1-RECT-001",
        "service_axial_load_kN": 1_000.0,
        "service_load_combination_id": "SLS-GRAVITY-01",
        "service_load_basis": "includes_footing_self_weight_and_overburden",
        "factored_axial_load_kN": 1_500.0,
        "factored_load_combination_id": "ULS-GRAVITY-01",
        "allowable_soil_pressure_kPa": 200.0,
        "allowable_soil_pressure_source_reference": "GEO-REPORT-001",
        "allowable_soil_pressure_is_externally_approved": True,
        "footing_type": FootingType.ISOLATED_RECTANGULAR,
        "column_L_mm": 400.0,
        "column_B_mm": 300.0,
        "minimum_overall_thickness_mm": 600.0,
        "maximum_overall_thickness_mm": 700.0,
        "thickness_increment_mm": 50.0,
        "effective_depth_offset_L_mm": 80.0,
        "effective_depth_offset_B_mm": 80.0,
        "footing_concrete_fck_nmm2": 25.0,
        "column_concrete_fck_nmm2": 25.0,
        "steel_fy_nmm2": 415.0,
        "effective_supporting_area_A1_mm2": 480_000.0,
        "effective_supporting_area_basis": "largest_frustum_1v_2h",
        "effective_supporting_area_is_approved": True,
        "dowel_count": 8,
        "dowel_diameter_mm": 25.0,
        "column_longitudinal_bar_diameter_mm": 25.0,
        "available_dowel_development_length_into_footing_mm": 1_400.0,
        "available_dowel_development_length_into_column_mm": 1_400.0,
    }
    values.update(overrides)
    return ConcentricIsolatedFootingInput(**values)  # type: ignore[arg-type]


def _benchmark_input(**overrides: object) -> ConcentricIsolatedFootingInput:
    values: dict[str, object] = {
        "case_id": "FOOT-B1-SQ-001",
        "service_axial_load_kN": 800.0,
        "factored_axial_load_kN": 1_200.0,
        "footing_type": FootingType.ISOLATED_SQUARE,
        "column_L_mm": 400.0,
        "column_B_mm": 400.0,
        "minimum_overall_thickness_mm": 500.0,
        "maximum_overall_thickness_mm": 500.0,
        "effective_depth_offset_L_mm": 100.0,
        "effective_depth_offset_B_mm": 100.0,
        "effective_supporting_area_A1_mm2": 640_000.0,
        "dowel_count": 4,
        "dowel_diameter_mm": 20.0,
        "column_longitudinal_bar_diameter_mm": 20.0,
        "available_dowel_development_length_into_footing_mm": 1_000.0,
        "available_dowel_development_length_into_column_mm": 1_000.0,
    }
    values.update(overrides)
    return _input(**values)


def test_review_benchmark_freezes_plan_structural_and_transfer_evidence():
    result = design_concentric_isolated_footing_is456(_benchmark_input())

    assert result.bearing.L_mm == result.bearing.B_mm == 2_000.0
    assert result.bearing.q_max_kPa == result.bearing.q_min_kPa == 200.0
    assert result.flexure is not None
    assert result.flexure.Mu_L_kNm == result.flexure.Mu_B_kNm == pytest.approx(192.0)
    assert result.flexure.Ast_L_mm2 == pytest.approx(1_369.01)
    assert result.flexure.pt_L_percent == pytest.approx(0.1711262)
    assert result.one_way_shear is not None
    assert result.one_way_shear.utilization_ratio == pytest.approx(0.98429)
    assert result.punching is not None
    assert result.punching.utilization_ratio == pytest.approx(0.63)
    assert result.load_transfer.required_transfer_steel_area_mm2 == 800.0
    assert result.load_transfer.provided_transfer_steel_area_mm2 == pytest.approx(
        1_256.6371
    )
    assert (
        result.load_transfer.required_dowel_development_length_into_footing_mm
        == pytest.approx(805.915)
    )
    assert result.calculation_status == "PASS"
    assert result.detailing_status == result.status == "HOLD"
    assert result.is_ok is False
    assert result.calculations_are_safe is True


def test_rectangular_sizing_and_provenance_keep_load_and_soil_roles_explicit():
    result = design_concentric_isolated_footing_is456(_input())

    assert (result.bearing.L_mm, result.bearing.B_mm) == (2_600.0, 1_950.0)
    assert result.bearing.q_max_kPa == pytest.approx(197.23866)
    assert result.service_axial_load_kN == 1_000.0
    assert result.factored_axial_load_kN == 1_500.0
    assert result.provenance.service_load_combination_id == "SLS-GRAVITY-01"
    assert result.provenance.factored_load_combination_id == "ULS-GRAVITY-01"
    assert result.provenance.allowable_soil_pressure_source_reference == (
        "GEO-REPORT-001"
    )
    assert "no SBC derivation" in result.provenance.allowable_soil_pressure_role
    assert result.provenance.clause_bases["flexure"] == (
        "Cl. 34.2.3.1 and Cl. 34.3.1; factored axial action and "
        "rectangular-footing central-band distribution"
    )
    assert result.provenance.clause_bases["one_way_shear"] == (
        "Cl. 34.2.4.1(a) and IS 456 Table 19; factored axial action using "
        "directional required pt as a conservative screening input pending "
        "provided detailing"
    )
    assert result.provenance.qualified_review_requirement


def test_depth_loop_selects_first_passing_uniform_depth_and_retains_history():
    result = design_concentric_isolated_footing_is456(
        _benchmark_input(
            minimum_overall_thickness_mm=450.0,
            maximum_overall_thickness_mm=500.0,
            thickness_increment_mm=50.0,
        )
    )

    assert [item.structural_status for item in result.depth_candidates] == [
        "FAIL",
        "PASS",
    ]
    assert result.selected_overall_thickness_mm == 500.0
    assert result.selected_effective_depth_L_mm == 400.0
    assert result.selected_effective_depth_B_mm == 400.0


def test_exhausted_depth_range_has_no_selected_top_level_check_evidence():
    result = design_concentric_isolated_footing_is456(
        _benchmark_input(
            minimum_overall_thickness_mm=450.0,
            maximum_overall_thickness_mm=450.0,
        )
    )

    assert result.status == result.calculation_status == "FAIL"
    assert result.failed_checks == ("depth_selection",)
    assert result.selected_overall_thickness_mm is None
    assert result.selected_effective_depth_L_mm is None
    assert result.selected_effective_depth_B_mm is None
    assert result.flexure is None
    assert result.one_way_shear is None
    assert result.punching is None
    assert result.pt_passed_to_one_way_shear_percent == {}
    assert result.reinforcement_demands == ()
    assert len(result.depth_candidates) == 1
    assert result.depth_candidates[0].structural_status == "FAIL"
    assert result.depth_candidates[0].one_way_shear_utilization is not None


def test_service_and_factored_actions_are_not_silently_inferred():
    base = design_concentric_isolated_footing_is456(_input())
    changed_factored = design_concentric_isolated_footing_is456(
        _input(factored_axial_load_kN=1_800.0)
    )

    assert changed_factored.bearing == base.bearing
    assert changed_factored.flexure is not None
    assert base.flexure is not None
    assert changed_factored.flexure.Mu_L_kNm > base.flexure.Mu_L_kNm
    assert changed_factored.load_transfer.Pu_kN == 1_800.0


def test_unequal_directional_depths_return_hold_without_structural_evaluation():
    result = design_concentric_isolated_footing_is456(
        _input(effective_depth_offset_B_mm=100.0)
    )

    assert result.status == "HOLD"
    assert result.calculation_status == "NOT_EVALUATED"
    assert result.flexure is result.one_way_shear is result.punching is None
    assert "DIRECTIONAL_EFFECTIVE_DEPTH_NOT_SUPPORTED_BY_CURRENT_CORE" in (
        result.hold_reasons
    )


def test_directional_steel_demand_and_shear_inputs_are_traceable_but_not_detailed():
    result = design_concentric_isolated_footing_is456(_input())

    assert [item.direction for item in result.reinforcement_demands] == ["L", "B"]
    assert result.pt_passed_to_one_way_shear_percent == {
        "L": result.reinforcement_demands[0].required_steel_percent,
        "B": result.reinforcement_demands[1].required_steel_percent,
    }
    assert all(item.detailing_status == "HOLD" for item in result.reinforcement_demands)
    assert result.reinforcement_demands[0].central_band_fraction is None
    assert result.reinforcement_demands[1].central_band_fraction == pytest.approx(
        0.857142857
    )
    assert "bar selection" in result.detailing_hold_reason


def test_unsafe_load_transfer_aggregates_to_fail():
    result = design_concentric_isolated_footing_is456(
        _input(dowel_count=4, dowel_diameter_mm=10.0)
    )

    assert result.load_transfer.is_safe is False
    assert result.status == result.calculation_status == "FAIL"
    assert result.failed_checks == ("load_transfer",)
    assert result.is_ok is False


@pytest.mark.parametrize(
    "overrides,match",
    [
        ({"allowable_soil_pressure_is_externally_approved": False}, "externally"),
        ({"allowable_soil_pressure_source_reference": ""}, "non-empty"),
        ({"service_load_basis": "column_only"}, "self-weight"),
        ({"effective_supporting_area_is_approved": False}, "A1 geometry"),
        ({"service_axial_load_kN": 0.0}, "finite positive"),
    ],
)
def test_required_external_and_load_provenance_fail_closed(
    overrides: dict[str, object],
    match: str,
):
    with pytest.raises(ValidationError, match=match):
        design_concentric_isolated_footing_is456(_input(**overrides))
