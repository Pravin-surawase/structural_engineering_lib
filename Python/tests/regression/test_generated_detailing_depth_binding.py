"""A generated BBS must use the same physical depths as its strength design."""

import math

import pytest

from structural_lib.core.errors import InputContractError
from structural_lib.design.is456 import beam
from structural_lib.services.api import compute_bbs, design_and_detail_beam_is456
from structural_lib.services.beam_pipeline import design_single_beam


def _canonical_request(*, d_mm=492, d_dash_mm=56, mu_knm=150, b_mm=300):
    options = beam.BeamDetailingOptionsV1(
        standard=beam.DetailingStandard.IS456,
        clear_cover_mm=40,
        tension_bar_diameter_mm=20,
        compression_bar_diameter_mm=16,
        nominal_top_steel_ratio=0.25,
        stirrup_diameter_mm=8,
        stirrup_legs=2,
        stirrup_spacing_support_mm=150,
        stirrup_spacing_mid_mm=200,
    )
    return beam.input(
        member_id="B-GEOMETRY",
        story="GF",
        case_id="ULS-1",
        span_mm=5000,
        b_mm=b_mm,
        D_mm=550,
        d_mm=d_mm,
        d_dash_mm=d_dash_mm,
        fck_nmm2=25,
        fy_nmm2=500,
        mu_knm=mu_knm,
        vu_kn=80,
        asv_mm2=options.asv_mm2,
        detailing=options,
    )


def _joint_result(route, *, d_mm, mu_knm=150):
    if route == "canonical":
        return beam.design_and_detail(
            _canonical_request(d_mm=d_mm, mu_knm=mu_knm),
            detailing_standard=beam.DetailingStandard.IS456,
        )
    params = {
        "units": "IS456",
        "beam_id": "B-GEOMETRY",
        "story": "GF",
        "span_mm": 5000,
        "b_mm": 300,
        "D_mm": 550,
        "d_mm": d_mm,
        "d_dash_mm": 56,
        "cover_mm": 40,
        "fck_nmm2": 25,
        "fy_nmm2": 500,
        "mu_knm": mu_knm,
        "vu_kn": 80,
    }
    if route == "compatibility":
        return design_and_detail_beam_is456(**params)
    return design_single_beam(**params)


@pytest.mark.parametrize("route", ["canonical", "compatibility", "pipeline"])
@pytest.mark.parametrize(
    ("d_mm", "mu_knm", "issue_code"),
    [
        (500, 150, "DETAILING_EFFECTIVE_DEPTH_MISMATCH"),
        (500, 340, "DETAILING_EFFECTIVE_DEPTH_UNVERIFIED"),
    ],
)
def test_joint_producers_reject_unbound_geometry(route, d_mm, mu_knm, issue_code):
    # The original high-demand case emitted 1885 mm2 in two layers and a PASS/BBS.
    with pytest.raises(InputContractError) as error:
        _joint_result(route, d_mm=d_mm, mu_knm=mu_knm)

    assert error.value.issues[0].code == issue_code
    assert "detailing.bottom_bars[0]" in error.value.issues[0].path


@pytest.mark.parametrize(
    ("route", "d_mm"), [("canonical", 492), ("compatibility", 494), ("pipeline", 494)]
)
def test_joint_producers_accept_matching_single_layer_geometry(route, d_mm):
    result = _joint_result(route, d_mm=d_mm)

    assert result.is_ok
    if route == "canonical":
        assert len(beam.bbs(result).items) == 9
    elif route == "compatibility":
        assert len(compute_bbs(result).items) == 9
    else:
        assert result.detailing.bottom_bars[0]["diameter"] == 16


def test_required_compression_depth_binds_to_actual_top_bars():
    request = _canonical_request(b_mm=600, mu_knm=600, d_dash_mm=50)
    strength = beam.design(request)
    assert strength.is_ok and strength.calculation.flexure.Asc_required > 0

    with pytest.raises(InputContractError) as error:
        beam.detail(strength, detailing_standard=beam.DetailingStandard.IS456)

    assert error.value.issues[0].code == "DETAILING_EFFECTIVE_DEPTH_MISMATCH"
    assert error.value.issues[0].path == "detailing.top_bars[0].d_dash_mm"

    corrected = beam.design_and_detail(
        _canonical_request(b_mm=600, mu_knm=600, d_dash_mm=56),
        detailing_standard=beam.DetailingStandard.IS456,
    )
    assert corrected.is_ok
    assert corrected.design.calculation.flexure.Asc_required > 0
    assert len(beam.bbs(corrected).items) == 9


def test_nominal_opposite_bars_do_not_redefine_unused_compression_depth():
    result = beam.design_and_detail(
        _canonical_request(d_dash_mm=50),
        detailing_standard=beam.DetailingStandard.IS456,
    )

    assert result.is_ok
    assert result.design.calculation.flexure.Asc_required == 0
    assert len(beam.bbs(result).items) == 9


def test_pipeline_does_not_skip_binding_for_spacing_invalid_layout():
    # This strength PASS generates two-layer rows which also violate spacing.
    # Optional drafting validity must not bypass the physical-depth requirement.
    with pytest.raises(InputContractError) as error:
        design_single_beam(
            units="IS456",
            beam_id="B-NARROW",
            story="GF",
            b_mm=120,
            D_mm=500,
            d_mm=485,
            span_mm=5000,
            cover_mm=15,
            fck_nmm2=25,
            fy_nmm2=500,
            mu_knm=300,
            vu_kn=20,
            include_detailing=True,
        )

    assert {issue.code for issue in error.value.issues} == {
        "DETAILING_EFFECTIVE_DEPTH_UNVERIFIED"
    }


def test_matching_derived_depth_reaches_canonical_bbs():
    payload = _canonical_request().model_dump(mode="python")
    payload["section"]["d_mm"] = None
    payload["section"]["effective_depth_basis"] = {
        "clear_cover_mm": 40,
        "stirrup_diameter_mm": 8,
        "tension_bar_diameter_mm": 20,
    }
    request = beam.load(payload)
    result = beam.design_and_detail(
        request, detailing_standard=beam.DetailingStandard.IS456
    )

    assert result.is_ok
    assert request.section.resolved_d_mm() == 492
    assert len(beam.bbs(result).items) == 9


def test_design_only_keeps_explicit_centroid_depth_without_certifying_layout():
    request = _canonical_request(d_mm=500, d_dash_mm=50, mu_knm=340)

    result = beam.design(request)

    assert result.is_ok
    assert result.calculation.flexure.Ast_required == pytest.approx(1884.7438058748398)
    assert 6 * math.pi * 20**2 / 4 > result.calculation.flexure.Ast_required
    # Recalculating at even the outer row of the generated layout needs more steel.
    physical_outer_row = beam.design(_canonical_request(mu_knm=340))
    assert physical_outer_row.calculation.flexure.Ast_required > 6 * math.pi * 20**2 / 4
