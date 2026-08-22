"""Focused contract tests for Phase B1 isolated-footing orchestration."""

from __future__ import annotations

import math

import pytest

from structural_lib.codes.is456.footing.one_way_shear import footing_one_way_shear
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
        "service_load_origin": "provided",
        "factored_axial_load_kN": 1_500.0,
        "factored_load_combination_id": "ULS-GRAVITY-01",
        "allowable_soil_pressure_kPa": 200.0,
        "allowable_soil_pressure_source_reference": "GEO-REPORT-001",
        "allowable_soil_pressure_origin": "verified",
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
        "effective_supporting_area_origin": "provided",
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


def _detailed_benchmark_input(**overrides: object) -> ConcentricIsolatedFootingInput:
    values: dict[str, object] = {
        "nominal_cover_mm": 50.0,
        "cover_exposure_basis": "approved severe footing schedule",
        "cover_exposure_basis_is_approved": True,
        "nominal_max_aggregate_size_mm": 20.0,
        "lower_bottom_bar_direction": "L",
        "upper_bottom_bar_direction": "B",
        "permitted_bottom_bar_diameters_mm": (12, 16, 20, 25, 32),
        "footing_bottom_bar_type": "deformed",
    }
    values.update(overrides)
    return _benchmark_input(**values)


def test_review_benchmark_freezes_plan_structural_and_transfer_evidence():
    result = design_concentric_isolated_footing_is456(_benchmark_input())

    assert result.bearing.L_mm == result.bearing.B_mm == 2_000.0
    assert result.bearing.q_max_kPa == result.bearing.q_min_kPa == 200.0
    assert result.flexure is not None
    assert result.flexure.Mu_L_kNm == result.flexure.Mu_B_kNm == pytest.approx(192.0)
    assert result.flexure.Ast_L_mm2 == pytest.approx(1_368.9235171)
    assert result.flexure.pt_L_percent == pytest.approx(0.1711154396)
    assert result.one_way_shear is not None
    assert result.one_way_shear.utilization_ratio == pytest.approx(0.9843139475)
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


def test_maintained_detailing_closes_square_benchmark_to_aggregate_pass():
    result = design_concentric_isolated_footing_is456(_detailed_benchmark_input())

    assert (
        result.calculation_status == result.detailing_status == result.status == "PASS"
    )
    assert result.is_ok and result.calculations_are_safe
    assert result.detailing_hold_reason is None and result.hold_reasons == ()
    assert result.detailing is not None
    assert result.detailing.lower is not None and result.detailing.upper is not None
    assert result.detailing.lower.layer == "lower"
    assert result.detailing.upper.layer == "upper"
    assert result.detailing.lower.diameter_mm == 12
    assert result.detailing.upper.diameter_mm == 12
    assert result.detailing.lower.bar_count == 13
    assert result.detailing.upper.bar_count == 13
    assert result.detailing.dowel_schedule_link.bar_count == 4
    assert all(
        demand.detailing_status == "PASS" for demand in result.reinforcement_demands
    )
    assert result.provenance.clause_bases["detailing"].startswith(
        "Cl. 34.3/34.3.1 and Cl. 34.5.1"
    )
    assert (
        "structural_lib.codes.is456.footing.detailing."
        "detail_isolated_footing_bottom_steel"
    ) in result.provenance.core_function_ids


def test_actual_provided_pt_closes_the_detailing_to_shear_acceptance_loop():
    defective_area_mm2 = 11 * math.pi * 12**2 / 4
    defective_pt_percent = defective_area_mm2 / (2_000 * 400) * 100
    reproduced_defect = footing_one_way_shear(
        Pu_kN=1_200,
        L_mm=2_000,
        B_mm=2_000,
        d_mm=400,
        a_mm=400,
        b_mm=400,
        fck=25,
        pt_L_percent=defective_pt_percent,
        pt_B_percent=12 * math.pi * 12**2 / 4 / (2_000 * 400) * 100,
    )
    result = design_concentric_isolated_footing_is456(_detailed_benchmark_input())

    assert defective_pt_percent == pytest.approx(0.1555088364)
    assert reproduced_defect.utilization_ratio == pytest.approx(1.0209076)
    assert not reproduced_defect.is_safe
    assert result.status == "PASS"
    assert result.one_way_shear_basis == "actual_provided_pt_final"
    assert result.one_way_shear is not None and result.one_way_shear.is_safe
    assert result.one_way_shear.utilization_ratio == pytest.approx(0.95648558)
    assert result.one_way_shear_screening is not None
    assert result.one_way_shear_screening.utilization_ratio == pytest.approx(
        0.9843139475
    )
    assert result.screening_pt_passed_to_one_way_shear_percent == {
        "L": pytest.approx(0.1711154396),
        "B": pytest.approx(0.1711154396),
    }
    assert result.detailing is not None
    selected = {
        item.direction: item
        for item in (result.detailing.lower, result.detailing.upper)
        if item is not None
    }
    expected_actual_pt = {
        "L": selected["L"].provided_area_mm2 / (2_000 * 400) * 100,
        "B": selected["B"].provided_area_mm2 / (2_000 * 400) * 100,
    }
    assert result.pt_passed_to_one_way_shear_percent == pytest.approx(
        expected_actual_pt
    )
    for demand in result.reinforcement_demands:
        assert demand.provided_steel_area_mm2 is not None
        assert demand.provided_steel_area_mm2 >= demand.required_steel_area_mm2
        assert demand.provided_steel_percent == pytest.approx(
            result.pt_passed_to_one_way_shear_percent[demand.direction]
        )


def test_detailing_failure_fails_aggregate_without_reclassifying_calculations():
    result = design_concentric_isolated_footing_is456(
        _detailed_benchmark_input(nominal_cover_mm=20.0)
    )

    assert result.calculation_status == "PASS"
    assert result.detailing_status == result.status == "FAIL"
    assert result.failed_checks == ("detailing",)
    assert result.detailing is not None
    assert result.detailing.lower is None and result.detailing.upper is None


def test_unapproved_exposure_holds_aggregate_with_calculations_safe():
    result = design_concentric_isolated_footing_is456(
        _detailed_benchmark_input(cover_exposure_basis_is_approved=False)
    )

    assert result.calculation_status == "PASS"
    assert result.detailing_status == result.status == "HOLD"
    assert result.detailing is not None
    assert result.detailing_hold_reason == result.detailing.reasons[0]
    assert result.hold_reasons == result.detailing.reasons


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
    assert result.provenance.service_load_origin == "provided"
    assert result.provenance.allowable_soil_pressure_origin == "verified"
    assert result.provenance.allowable_soil_pressure_is_externally_approved is True
    assert result.provenance.effective_supporting_area_origin == "provided"
    assert result.provenance.effective_supporting_area_is_approved is True
    assert len(result.provenance.arithmetic_input_hash) == 64
    assert len(result.provenance.assumption_identity_hash) == 64
    assert len(result.provenance.library_content_identity) == 64
    assert len(result.provenance.replay_receipt_hash) == 64
    assert "no SBC derivation" in result.provenance.allowable_soil_pressure_role
    assert result.provenance.clause_bases["flexure"] == (
        "Cl. 34.2.3.1 and Cl. 34.3.1; factored axial action and "
        "rectangular-footing central-band distribution"
    )
    assert result.provenance.clause_bases["one_way_shear"] == (
        "Cl. 34.2.4.1(a) and IS 456 Table 19; factored axial action using "
        "actual selected provided directional pt for a completed detailed "
        "result; required directional pt remains explicitly labelled screening "
        "evidence while detailing is pending"
    )
    assert result.provenance.qualified_review_requirement


def test_approved_assumed_basis_stays_assumed_and_holds_result():
    request = _detailed_benchmark_input(
        allowable_soil_pressure_origin="assumed",
        allowable_soil_pressure_is_externally_approved=True,
    )

    result = design_concentric_isolated_footing_is456(request)

    assert result.provenance.allowable_soil_pressure_origin == "assumed"
    assert result.provenance.allowable_soil_pressure_is_externally_approved is True
    assert result.status == "HOLD"
    assert (
        "ASSUMED_BASIS_REQUIRES_VERIFICATION:allowable_soil_pressure_origin"
        in result.hold_reasons
    )


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


@pytest.mark.parametrize(
    "origin_field",
    [
        "service_load_origin",
        "allowable_soil_pressure_origin",
        "effective_supporting_area_origin",
    ],
)
def test_unknown_provenance_origins_are_rejected(origin_field):
    with pytest.raises(ValidationError, match=origin_field):
        design_concentric_isolated_footing_is456(_input(**{origin_field: "invented"}))
