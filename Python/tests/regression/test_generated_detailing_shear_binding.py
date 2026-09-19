"""Generated stirrups must bind to the accepted shear-design basis."""

import math

import pytest

from structural_lib.core.errors import InputContractError
from structural_lib.design.is456 import beam
from structural_lib.services.api import compute_bbs, design_and_detail_beam_is456
from structural_lib.services.beam_pipeline import design_single_beam

_ASV_2L8 = 2 * math.pi * 8**2 / 4


def _canonical_request(*, spacing_mm: float) -> object:
    options = beam.BeamDetailingOptionsV1(
        standard=beam.DetailingStandard.IS456,
        clear_cover_mm=40,
        tension_bar_diameter_mm=16,
        compression_bar_diameter_mm=12,
        nominal_top_steel_ratio=0.25,
        stirrup_diameter_mm=8,
        stirrup_legs=2,
        stirrup_spacing_support_mm=spacing_mm,
        stirrup_spacing_mid_mm=spacing_mm,
    )
    return beam.input(
        member_id="B-SHEAR",
        story="GF",
        case_id="ULS-1",
        span_mm=5000,
        b_mm=300,
        D_mm=500,
        d_mm=444,
        d_dash_mm=54,
        fck_nmm2=25,
        fy_nmm2=500,
        mu_knm=150,
        vu_kn=200,
        asv_mm2=options.asv_mm2,
        detailing=options,
    )


def _compatibility_params(*, asv_mm2: float, stirrup_dia_mm: float, spacing_mm: float):
    return {
        "units": "IS456",
        "beam_id": "B-SHEAR",
        "story": "GF",
        "span_mm": 5000,
        "b_mm": 300,
        "D_mm": 500,
        "d_mm": 446 if stirrup_dia_mm == 6 else 444,
        "d_dash_mm": 50,
        "cover_mm": 40,
        "fck_nmm2": 25,
        "fy_nmm2": 500,
        "mu_knm": 150,
        "vu_kn": 200,
        "asv_mm2": asv_mm2,
        "stirrup_dia_mm": stirrup_dia_mm,
        "stirrup_spacing_support_mm": spacing_mm,
        "stirrup_spacing_mid_mm": spacing_mm,
    }


def _joint_result(
    route: str, *, asv_mm2: float, stirrup_dia_mm: float, spacing_mm: float
):
    if route == "canonical":
        return beam.design_and_detail(
            _canonical_request(spacing_mm=spacing_mm),
            detailing_standard=beam.DetailingStandard.IS456,
        )
    params = _compatibility_params(
        asv_mm2=asv_mm2,
        stirrup_dia_mm=stirrup_dia_mm,
        spacing_mm=spacing_mm,
    )
    if route == "compatibility":
        return design_and_detail_beam_is456(**params)
    pipeline_params = {
        **params,
        "stirrup_spacing_start_mm": params["stirrup_spacing_support_mm"],
        "stirrup_spacing_end_mm": params["stirrup_spacing_mid_mm"],
    }
    pipeline_params.pop("stirrup_spacing_support_mm")
    return design_single_beam(**pipeline_params)


@pytest.mark.parametrize("route", ["canonical", "compatibility", "pipeline"])
def test_joint_producers_reject_overspaced_generated_stirrups(route: str):
    with pytest.raises(InputContractError) as error:
        _joint_result(
            route,
            asv_mm2=_ASV_2L8,
            stirrup_dia_mm=8,
            spacing_mm=300,
        )

    issues = error.value.issues
    assert {issue.code for issue in issues} == {"DETAILING_SHEAR_SPACING_EXCEEDED"}
    assert {issue.path for issue in issues} == {
        "detailing.stirrups[0].spacing_mm",
        "detailing.stirrups[1].spacing_mm",
        "detailing.stirrups[2].spacing_mm",
    }
    assert all(
        issue.constraint == "spacing_mm must not exceed 125 mm" for issue in issues
    )


@pytest.mark.parametrize("route", ["compatibility", "pipeline"])
def test_joint_producers_allow_conservative_default_asv(route: str):
    result = _joint_result(
        route,
        asv_mm2=100.0,
        stirrup_dia_mm=8,
        spacing_mm=125,
    )

    assert result.is_ok


@pytest.mark.parametrize("route", ["canonical", "compatibility", "pipeline"])
def test_coherent_generated_stirrups_reach_passing_joint_result(route: str):
    result = _joint_result(
        route,
        asv_mm2=_ASV_2L8,
        stirrup_dia_mm=8,
        spacing_mm=125,
    )

    assert result.is_ok
    if route == "canonical":
        assert len(beam.bbs(result).items) == 9
    elif route == "compatibility":
        assert len(compute_bbs(result).items) == 9
    else:
        assert result.detailing.stirrups[0]["callout"] == "2L-8φ@125"


def test_compatibility_rejects_underarea_even_with_closer_spacing():
    with pytest.raises(InputContractError) as error:
        _joint_result(
            "compatibility",
            asv_mm2=100.0,
            stirrup_dia_mm=6,
            spacing_mm=75,
        )

    issues = error.value.issues
    assert {issue.code for issue in issues} == {"DETAILING_SHEAR_AREA_MISMATCH"}
    assert {issue.path for issue in issues} == {
        "detailing.stirrups[0].area_mm2",
        "detailing.stirrups[1].area_mm2",
        "detailing.stirrups[2].area_mm2",
    }
    assert all("Rerun strength design" in (issue.suggestion or "") for issue in issues)


def test_compatibility_rejects_original_underarea_overspacing_reproducer():
    with pytest.raises(InputContractError) as error:
        _joint_result(
            "compatibility",
            asv_mm2=2 * _ASV_2L8,
            stirrup_dia_mm=6,
            spacing_mm=300,
        )

    assert {issue.code for issue in error.value.issues} == {
        "DETAILING_SHEAR_AREA_MISMATCH",
        "DETAILING_SHEAR_SPACING_EXCEEDED",
    }
