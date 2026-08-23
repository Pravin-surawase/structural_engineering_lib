# SPDX-License-Identifier: MIT
"""Outcome-focused tests for the bounded footing detailing slice."""

import importlib

import pytest

import structural_lib.codes.is456.footing.detailing as detailing_module
from structural_lib.codes.is456.footing.detailing import (
    detail_isolated_footing_bottom_steel,
)
from structural_lib.codes.is456.footing.load_transfer import (
    AMENDMENT_6_SOURCE_ID,
    IS456_CONSOLIDATED_SOURCE_ID,
    check_isolated_footing_load_transfer,
)


def _receipt(**changes):
    data = {
        "Pu_kN": 1200,
        "loaded_area_A2_mm2": 160000,
        "effective_supporting_area_A1_mm2": 640000,
        "effective_supporting_area_basis": "largest_frustum_1v_2h",
        "effective_supporting_area_is_approved": True,
        "supporting_concrete_fck_nmm2": 25,
        "supported_concrete_fck_nmm2": 25,
        "steel_fy_nmm2": 415,
        "dowel_count": 4,
        "dowel_diameter_mm": 20,
        "column_longitudinal_bar_diameter_mm": 20,
        "available_dowel_development_length_into_footing_mm": 900,
        "available_dowel_development_length_into_supported_member_mm": 900,
    }
    data.update(changes)
    return check_isolated_footing_load_transfer(**data)


def _case(**changes):
    data = {
        "Pu_kN": 1200,
        "L_mm": 2000,
        "B_mm": 2000,
        "column_L_mm": 400,
        "column_B_mm": 400,
        "D_mm": 500,
        "analysis_d_L_mm": 400,
        "analysis_d_B_mm": 400,
        "fck": 25,
        "fy": 415,
        "nominal_cover_mm": 50,
        "exposure_basis": "approved severe footing schedule",
        "exposure_is_approved": True,
        "aggregate_size_mm": 20,
        "lower_direction": "L",
        "upper_direction": "B",
        # The independent benchmark is a T12-and-above schedule.  T10 remains
        # a supported explicit option and is exercised separately below.
        "permitted_diameters_mm": (12, 16, 20, 25, 32),
        "bar_type": "deformed",
        "load_transfer_result": _receipt(),
    }
    data.update(changes)
    return detail_isolated_footing_bottom_steel(**data)


def test_square_benchmark_selects_buildable_12mm_layers():
    result = _case()

    assert result.status == "PASS" and result.qualified_review_required
    assert result.lower is not None and result.upper is not None
    assert result.lower.layer == "lower" and result.upper.layer == "upper"
    assert result.lower.diameter_mm == result.upper.diameter_mm == 12
    assert result.lower.physical_effective_depth_mm == pytest.approx(444)
    assert result.upper.physical_effective_depth_mm == pytest.approx(432)
    assert result.lower.Mu_kNm == pytest.approx(192)
    assert result.lower.flexure_result_area_mm2 == pytest.approx(1226.238497)
    assert result.upper.flexure_result_area_mm2 == pytest.approx(1262.037813)
    assert result.lower.analysis_screening_area_mm2 == pytest.approx(1368.923517)
    assert result.upper.analysis_screening_area_mm2 == pytest.approx(1368.923517)
    assert result.lower.minimum_area_mm2 == result.upper.minimum_area_mm2 == 1200
    assert result.lower.required_area_mm2 == pytest.approx(1368.923517)
    assert result.upper.required_area_mm2 == pytest.approx(1368.923517)
    assert result.lower.bar_count == result.upper.bar_count == 13
    assert result.lower.provided_area_mm2 == pytest.approx(1470.265, rel=1e-4)
    assert result.upper.provided_area_mm2 == pytest.approx(1470.265, rel=1e-4)
    assert result.lower.spacing_mm == pytest.approx(157.333, rel=1e-4)
    assert result.lower.clear_spacing_mm == pytest.approx(145.333, rel=1e-4)
    assert result.lower.max_diameter_mm == pytest.approx(62.5)
    assert result.lower.max_spacing_mm == 300
    assert result.lower.development_length_unrounded_mm == pytest.approx(483.549)
    assert result.lower.development_length_mm == 484
    assert result.lower.straight_anchorage_available_each_end_mm == 744
    assert result.lower.straight_bar_length_mm == 1900
    assert result.dowel_schedule_link.bar_count == 4
    assert result.dowel_schedule_link.diameter_mm == 20
    assert result.dowel_schedule_link.is_safe
    assert result.actual_provided_pt_percent == {
        "L": pytest.approx(0.1837831702),
        "B": pytest.approx(0.1837831702),
    }
    assert result.final_one_way_shear is not None
    assert result.final_one_way_shear.is_safe
    assert result.final_one_way_shear.utilization_ratio == pytest.approx(0.95648558)


def test_rectangle_short_direction_has_consistent_buildable_zone_schedule():
    result = _case(L_mm=3000, B_mm=2000)
    assert result.status == "PASS"
    assert result.lower is not None and result.upper is not None
    short = result.upper if result.upper.direction == "B" else result.lower

    assert short.layout == "central_band"
    assert [zone.zone for zone in short.zones] == [
        "central_band",
        "outer_band_each",
    ]
    central, outer = short.zones
    assert central.width_mm == 2000
    assert outer.width_mm == 500
    assert central.provided_area_mm2 >= central.required_area_mm2
    assert outer.provided_area_mm2 >= outer.required_area_mm2
    assert short.bar_count == central.bar_count + 2 * outer.bar_count
    assert short.provided_area_mm2 == pytest.approx(
        central.provided_area_mm2 + 2 * outer.provided_area_mm2
    )
    assert short.spacing_mm == max(central.spacing_mm, outer.spacing_mm)
    assert short.clear_spacing_mm == min(
        central.clear_spacing_mm, outer.clear_spacing_mm
    )
    assert all(zone.spacing_mm <= short.max_spacing_mm for zone in short.zones)
    assert all(
        zone.clear_spacing_mm >= short.minimum_clear_spacing_mm for zone in short.zones
    )


def test_ten_mm_bars_are_supported_when_explicitly_permitted():
    result = _case(permitted_diameters_mm=(10,))
    assert result.status == "PASS"
    assert result.lower is not None and result.upper is not None
    assert result.lower.diameter_mm == result.upper.diameter_mm == 10


def test_explicit_layer_order_controls_directional_physical_depths():
    result = _case(lower_direction="B", upper_direction="L")
    assert result.status == "PASS"
    assert result.lower is not None and result.upper is not None
    assert result.lower.direction == "B" and result.lower.layer == "lower"
    assert result.upper.direction == "L" and result.upper.layer == "upper"
    assert result.lower.physical_effective_depth_mm == pytest.approx(444)
    assert result.upper.physical_effective_depth_mm == pytest.approx(432)


def test_numeric_depth_cover_and_spacing_constraints_fail_closed():
    assert _case(D_mm=440).status == "FAIL"
    assert _case(nominal_cover_mm=20).status == "FAIL"
    assert _case(analysis_d_L_mm=449, analysis_d_B_mm=449).status == "FAIL"


def test_required_hook_or_bend_is_hold_not_selected_failure():
    result = _case(L_mm=1200, B_mm=1200)
    assert result.status == "HOLD"
    assert result.lower is not None and result.upper is not None
    assert not result.lower.end_anchorage.arrangement_was_explicit
    assert result.lower.end_anchorage.shortfall_mm > 0
    assert "explicit supported end arrangement" in result.reasons[0]


def test_explicit_90_degree_bend_closes_anchorage_and_geometry():
    result = _case(
        L_mm=1400,
        B_mm=1400,
        bottom_bar_end_arrangement="bend_90",
        bend_internal_radius_mm=24,
        extension_after_bend_mm=144,
        bend_geometry_source_reference="APPROVED-FOOTING-BEND-SCHEDULE-90",
        bend_geometry_source_is_approved=True,
    )

    assert result.status == "PASS"
    assert result.lower is not None and result.upper is not None
    for detail in (result.lower, result.upper):
        anchorage = detail.end_anchorage
        assert anchorage.arrangement == "bend_90"
        assert anchorage.arrangement_was_explicit
        assert anchorage.required_development_length_mm == pytest.approx(483.549107)
        assert anchorage.available_straight_length_mm == pytest.approx(414)
        assert anchorage.anchorage_value_mm == 96
        assert anchorage.total_available_development_length_mm == pytest.approx(510)
        assert anchorage.bend_angle_degrees == 90
        assert anchorage.internal_bend_radius_mm == 24
        assert anchorage.centreline_bend_radius_mm == 30
        assert anchorage.extension_after_bend_mm == 144
        assert anchorage.geometry_fits
        assert anchorage.bounded_constructability_is_adequate
        assert anchorage.geometry_source_is_approved
        assert detail.total_bar_length_mm > detail.straight_bar_length_mm


def test_standard_u_hook_closes_shorter_footing_anchorage():
    result = _case(
        L_mm=1200,
        B_mm=1200,
        bottom_bar_end_arrangement="u_hook_180",
        bend_internal_radius_mm=24,
        extension_after_bend_mm=65,
        bend_geometry_source_reference="APPROVED-FOOTING-U-HOOK-SCHEDULE",
        bend_geometry_source_is_approved=True,
    )

    assert result.status == "PASS"
    assert result.lower is not None and result.upper is not None
    anchorage = result.lower.end_anchorage
    assert anchorage.arrangement == "u_hook_180"
    assert anchorage.available_straight_length_mm == pytest.approx(314)
    assert anchorage.anchorage_value_mm == 192
    assert anchorage.total_available_development_length_mm == pytest.approx(506)
    assert anchorage.return_extension_available_mm == pytest.approx(344)
    assert anchorage.anchorage_is_adequate and anchorage.geometry_fits


def test_complete_bend_basis_fails_inadequate_anchorage_or_physical_fit():
    inadequate = _case(
        L_mm=1200,
        B_mm=1200,
        bottom_bar_end_arrangement="bend_90",
        bend_internal_radius_mm=24,
        extension_after_bend_mm=144,
        bend_geometry_source_reference="APPROVED-FOOTING-BEND-SCHEDULE-90",
        bend_geometry_source_is_approved=True,
    )
    clashes = _case(
        L_mm=1400,
        B_mm=1400,
        bottom_bar_end_arrangement="bend_90",
        bend_internal_radius_mm=24,
        extension_after_bend_mm=400,
        bend_geometry_source_reference="APPROVED-FOOTING-BEND-SCHEDULE-90-TALL",
        bend_geometry_source_is_approved=True,
    )

    assert inadequate.status == "FAIL"
    assert inadequate.lower is not None
    assert not inadequate.lower.end_anchorage.anchorage_is_adequate
    assert "exact required development length" in inadequate.reasons[0]
    assert clashes.status == "FAIL"
    assert clashes.lower is not None
    assert not clashes.lower.end_anchorage.geometry_fits
    assert "available footing envelope" in clashes.reasons[0]


@pytest.mark.parametrize("arrangement", ["bend_135", "mechanical"])
def test_unsupported_end_arrangements_hold(arrangement):
    result = _case(bottom_bar_end_arrangement=arrangement)

    assert result.status == "HOLD"
    assert "outside the supported" in result.reasons[0]


def test_missing_bend_geometry_approval_holds():
    result = _case(bottom_bar_end_arrangement="bend_90")

    assert result.status == "HOLD"
    assert "complete approved bend radius" in result.reasons[0]


def test_anchorage_check_uses_unrounded_required_length():
    result = _case(L_mm=1479.5, B_mm=1479.5, permitted_diameters_mm=(12,))
    assert result.status == "PASS"
    assert result.lower is not None
    assert result.lower.development_length_unrounded_mm < 483.75
    assert result.lower.development_length_mm == 484
    assert result.lower.straight_anchorage_available_each_end_mm == 483.75


def test_dowel_schedule_is_linked_and_never_silently_reworked():
    unsafe = _case(load_transfer_result=_receipt(dowel_count=3))
    stale = _case(load_transfer_result=_receipt(Pu_kN=1000))

    assert unsafe.status == "FAIL"
    assert not unsafe.dowel_schedule_link.is_safe
    assert stale.status == "HOLD"
    assert "stale or inconsistent" in stale.reasons[0]


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({"fck": 55}, "HOLD"),
        ({"fy": 415, "bar_type": "plain"}, "HOLD"),
        ({"fy": 250, "bar_type": "deformed"}, "HOLD"),
        ({"exposure_is_approved": False}, "HOLD"),
        ({"permitted_diameters_mm": (8, 12)}, "HOLD"),
    ],
)
def test_unsupported_material_or_missing_engineering_basis_holds(changes, expected):
    assert _case(**changes).status == expected


def test_selection_and_provenance_are_deterministic_and_normalized():
    first = _case()
    reversed_schedule = _case(permitted_diameters_mm=(32, 25, 20, 16, 12))

    assert first.lower is not None and first.upper is not None
    assert reversed_schedule.lower is not None and reversed_schedule.upper is not None
    assert (first.lower.diameter_mm, first.upper.diameter_mm) == (
        reversed_schedule.lower.diameter_mm,
        reversed_schedule.upper.diameter_mm,
    )
    assert first.contract_version == "FOOT-ISO-DETAILING-P3-V1"
    assert first.source_ids == (IS456_CONSOLIDATED_SOURCE_ID, AMENDMENT_6_SOURCE_ID)
    assert first.units["length"] == "mm" and first.units["moment"] == "kNm"
    assert {"34.3.1", "26.2.1", "34.4"}.issubset(first.clause_refs)
    assert set(first.source_ids).issubset(first.accepted_load_transfer.source_ids)
    assert {"34.3", "26.2.1", "34.4"}.issubset(
        detail_isolated_footing_bottom_steel._is456_clauses
    )


def test_traceability_decorator_uses_known_ids_without_unknown_clause_warning(caplog):
    caplog.set_level("WARNING", logger="structural_lib.codes.is456.traceability")
    reloaded = importlib.reload(detailing_module)

    assert _case().status == "PASS"
    assert set(reloaded.detail_isolated_footing_bottom_steel._is456_clauses) == {
        "34.2.3.1",
        "34.2.4.1",
        "34.3",
        "26.5.2.1",
        "26.3.2",
        "26.3.3",
        "26.2.1",
        "26.2.2.1",
        "34.4",
    }
    assert not any(
        "Unknown clause reference" in record.message for record in caplog.records
    )
