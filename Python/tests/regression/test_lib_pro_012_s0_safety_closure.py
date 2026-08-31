"""LIB-PRO-012 S0 fail-closed regressions for the external P0 routes."""

from __future__ import annotations

from copy import deepcopy

import pytest

from structural_lib.codes.is456.beam.detailing import create_beam_detailing
from structural_lib.codes.is456.beam.torsion import (
    calculate_equivalent_moment,
    calculate_equivalent_shear,
    calculate_longitudinal_torsion_steel,
    calculate_torsion_shear_stress,
    calculate_torsion_stirrup_area,
    design_torsion,
)
from structural_lib.core.errors import DimensionError, MaterialError
from structural_lib.core.inputs import (
    BeamGeometryInput,
    BeamInput,
    DetailingConfigInput,
    LoadCaseInput,
    LoadsInput,
    MaterialsInput,
)
from structural_lib.services.api import (
    check_beam_is456,
    compute_bbs,
    design_and_detail_beam_is456,
    design_beam_is456,
    design_column_is456,
    design_from_input,
    detail_beam_is456,
    smart_analyze_design,
)


def _combined_kwargs() -> dict:
    return {
        "units": "IS456",
        "beam_id": "B-S0",
        "story": "GF",
        "span_mm": 5000.0,
        "mu_knm": 150.0,
        "vu_kn": 80.0,
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "cover_mm": 40.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }


def _detail_kwargs() -> dict:
    return {
        "units": "IS456",
        "beam_id": "B-S0",
        "story": "GF",
        "b_mm": 300.0,
        "D_mm": 500.0,
        "span_mm": 5000.0,
        "cover_mm": 40.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
        "ast_start_mm2": 900.0,
        "ast_mid_mm2": 900.0,
        "ast_end_mm2": 900.0,
    }


def _torsion_kwargs() -> dict:
    return {
        "corner_bar_centres_mm": (184.0, 384.0),
        "d_opposite_mm": 450.0,
        "tu_knm": 10.0,
        "vu_kn": 100.0,
        "mu_knm": 150.0,
        "b": 300.0,
        "D": 500.0,
        "d": 450.0,
        "fck": 25.0,
        "fy": 500.0,
        "cover": 40.0,
        "stirrup_dia": 8.0,
        "pt": 1.0,
    }


@pytest.mark.parametrize(
    "span_mm", [-1.0, 0.0, float("nan"), float("inf"), float("-inf")]
)
def test_ext_beam_001_002_combined_rejects_nonpositive_or_nonfinite_span(
    span_mm,
):
    with pytest.raises(ValueError, match="span_mm"):
        design_and_detail_beam_is456(**{**_combined_kwargs(), "span_mm": span_mm})


@pytest.mark.parametrize("field", ["mu_knm", "vu_kn"])
def test_ext_beam_003_004_combined_rejects_negative_action_magnitudes(field):
    with pytest.raises(ValueError, match=field):
        design_and_detail_beam_is456(**{**_combined_kwargs(), field: -1.0})


@pytest.mark.parametrize("field", ["mu_knm", "vu_kn"])
def test_ext_beam_005_design_only_rejects_negative_action_magnitudes(field):
    kwargs = {
        "units": "IS456",
        "case_id": "S0-CASE",
        "mu_knm": 150.0,
        "vu_kn": 80.0,
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }
    with pytest.raises(ValueError, match=field):
        design_beam_is456(**{**kwargs, field: -1.0})


@pytest.mark.parametrize("field,value", [("b_mm", 0.0), ("D_mm", -1.0)])
def test_ext_beam_006_invalid_geometry_stops_before_result(field, value):
    with pytest.raises(ValueError, match=field):
        design_and_detail_beam_is456(**{**_combined_kwargs(), field: value})


@pytest.mark.parametrize("field", ["mu_knm", "vu_kn"])
def test_ext_beam_007_compliance_rejects_negative_case_actions(field):
    case = {"case_id": "S0-CASE", "mu_knm": 150.0, "vu_kn": 80.0}
    case[field] = -1.0
    with pytest.raises(ValueError, match=field):
        check_beam_is456(
            units="IS456",
            cases=[case],
            b_mm=300.0,
            D_mm=500.0,
            d_mm=450.0,
            fck_nmm2=25.0,
            fy_nmm2=500.0,
        )


@pytest.mark.parametrize("field", ["mu_knm", "vu_kn"])
def test_ext_beam_008_smart_analysis_rejects_negative_actions(field):
    kwargs = {
        "units": "IS456",
        "span_mm": 5000.0,
        "mu_knm": 150.0,
        "vu_kn": 80.0,
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
    }
    with pytest.raises(ValueError, match=field):
        smart_analyze_design(**{**kwargs, field: -1.0})


@pytest.mark.parametrize(
    "field,value",
    [
        ("span_mm", 0.0),
        ("span_mm", float("nan")),
        ("cover_mm", -1.0),
        ("stirrup_dia_mm", 0.0),
        ("stirrup_spacing_start_mm", 0.0),
        ("stirrup_spacing_mid_mm", float("nan")),
        ("stirrup_spacing_end_mm", -1.0),
    ],
)
def test_ext_detail_001_002_direct_service_rejects_invalid_scalars(field, value):
    with pytest.raises(ValueError, match=field):
        detail_beam_is456(**{**_detail_kwargs(), field: value})


def test_ext_detail_002_pure_entrypoint_defends_itself():
    with pytest.raises(ValueError, match="stirrup_spacing_start"):
        create_beam_detailing(
            "B-S0",
            "GF",
            300.0,
            500.0,
            5000.0,
            40.0,
            25.0,
            500.0,
            900.0,
            900.0,
            900.0,
            stirrup_spacing_start=0.0,
        )


def test_ext_bbs_001_invalid_detailing_is_rejected_and_valid_reference_has_nine():
    combined = design_and_detail_beam_is456(**_combined_kwargs())
    document = compute_bbs(combined)
    assert len(document.items) == 9
    assert document.summary.total_items == 9

    invalid = deepcopy(combined.detailing)
    invalid.span = 0.0
    with pytest.raises(ValueError, match="span"):
        compute_bbs(invalid)


@pytest.mark.parametrize("field", ["tu_knm", "vu_kn", "mu_knm"])
def test_ext_torsion_001_002_negative_actions_are_rejected(field):
    with pytest.raises(ValueError, match=field):
        design_torsion(**{**_torsion_kwargs(), field: -1.0})


@pytest.mark.parametrize(
    "changes,error_type,match",
    [
        ({"cover": 0.0}, DimensionError, "cover"),
        ({"stirrup_dia": 0.0}, DimensionError, "stirrup_dia"),
        ({"d": 501.0}, DimensionError, "less than D"),
        ({"b": 80.0, "cover": 40.0}, DimensionError, "closed-stirrup core"),
        ({"fy": 600.0}, MaterialError, "fy"),
    ],
)
def test_ext_torsion_003_004_005_invalid_domain_stops_before_result(
    changes, error_type, match
):
    with pytest.raises(error_type, match=match):
        design_torsion(**{**_torsion_kwargs(), **changes})


def test_ext_torsion_006_positive_width_message_matches_predicate():
    with pytest.raises(DimensionError, match=r"b must be > 0 mm"):
        calculate_equivalent_shear(vu_kn=100.0, tu_knm=10.0, b=0.0)


@pytest.mark.parametrize(
    "function,kwargs,field",
    [
        (calculate_equivalent_shear, {"vu_kn": -1, "tu_knm": 10, "b": 300}, "vu_kn"),
        (
            calculate_equivalent_moment,
            {"mu_knm": -1, "tu_knm": 10, "d": 450, "b": 300, "D_mm": 500},
            "mu_knm",
        ),
        (
            calculate_torsion_shear_stress,
            {"ve_kn": -1, "b": 300, "d": 450},
            "ve_kn",
        ),
        (
            calculate_torsion_stirrup_area,
            {
                "tu_knm": -1,
                "vu_kn": 100,
                "b": 300,
                "d": 450,
                "b1": 220,
                "d1": 420,
                "fy": 500,
                "tc": 0.62,
            },
            "tu_knm",
        ),
        (
            calculate_longitudinal_torsion_steel,
            {"tu_knm": 10, "vu_kn": -1, "b1": 220, "d1": 420, "fy": 500, "sv": 150},
            "vu_kn",
        ),
    ],
)
def test_torsion_expert_helpers_share_the_magnitude_contract(function, kwargs, field):
    with pytest.raises(ValueError, match=field):
        function(**kwargs)


def test_ext_column_001_requires_supplied_steel():
    with pytest.raises(TypeError, match="requires 'Asc_mm2'"):
        design_column_is456(
            Pu_kN=800.0,
            Mux_kNm=120.0,
            b_mm=300.0,
            D_mm=450.0,
            l_mm=3000.0,
            fck_nmm2=25.0,
            fy_nmm2=415.0,
        )


@pytest.mark.parametrize("field", ["Mux_kNm", "Muy_kNm"])
def test_ext_column_002_rejects_negative_applied_moment_magnitudes(field):
    kwargs = {
        "Pu_kN": 800.0,
        "Mux_kNm": 120.0,
        "Muy_kNm": 0.0,
        "b_mm": 300.0,
        "D_mm": 450.0,
        "l_mm": 3000.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 415.0,
        "Asc_mm2": 2400.0,
    }
    with pytest.raises(ValueError, match="must be >= 0"):
        design_column_is456(**{**kwargs, field: -1.0})


@pytest.mark.parametrize(
    "constructor,kwargs,field",
    [
        (
            BeamGeometryInput,
            {"b_mm": 300, "D_mm": 500, "span_mm": float("nan")},
            "span_mm",
        ),
        (MaterialsInput, {"fck_nmm2": 25, "fy_nmm2": float("inf")}, "fy_nmm2"),
        (LoadsInput, {"mu_knm": True, "vu_kn": 80}, "mu_knm"),
        (
            DetailingConfigInput,
            {"stirrup_spacing_start_mm": float("nan")},
            "stirrup_spacing_start_mm",
        ),
    ],
)
def test_ext_typed_001_002_003_rejects_nonfinite_and_boolean_scalars(
    constructor, kwargs, field
):
    with pytest.raises(ValueError, match=field):
        constructor(**kwargs)


def test_ext_typed_004_strict_boolean_from_dict():
    with pytest.raises(ValueError, match="is_seismic must be a boolean"):
        DetailingConfigInput.from_dict({"is_seismic": "false"})


def test_ext_typed_005_one_load_case_is_supported():
    beam = BeamInput(
        beam_id="B-S0",
        story="GF",
        geometry=BeamGeometryInput(300.0, 500.0, 5000.0),
        materials=MaterialsInput(25.0, 500.0),
        load_cases=[LoadCaseInput("LC-1", 150.0, 80.0)],
    )
    result = design_from_input(beam)
    assert result.is_ok is True


@pytest.mark.parametrize("field", ["beam_id", "story"])
def test_ext_typed_006_and_id_001_missing_identity_is_not_fabricated(field):
    data = {
        "beam_id": "B-S0",
        "story": "GF",
        "geometry": {"b_mm": 300, "D_mm": 500, "span_mm": 5000},
        "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
        "loads": {"mu_knm": 150, "vu_kn": 80},
    }
    del data[field]
    with pytest.raises(ValueError, match=field):
        BeamInput.from_dict(data)


def test_ext_typed_007_zero_loads_are_preserved_by_alias_parsing():
    loads = LoadsInput.from_dict({"mu_knm": 0, "vu_kn": 0})
    assert loads.mu_knm == 0
    assert loads.vu_kn == 0


def test_valid_beam_values_and_corrected_torsion_source_vector():
    combined = design_and_detail_beam_is456(**_combined_kwargs())
    assert combined.design.flexure.Ast_required == pytest.approx(883.7158126109596)
    assert combined.design.shear.tau_v == pytest.approx(0.5925925925925926)
    assert combined.design.shear.spacing == pytest.approx(300.0)
    assert combined.detailing.ld_tension == pytest.approx(777.0)

    torsion = design_torsion(**_torsion_kwargs())
    assert torsion.Ve_kn == pytest.approx(153.33333333333334)
    assert torsion.Me_knm == pytest.approx(165.68627450980392)
    assert torsion.Asv_total == pytest.approx(0.5648)
    # Stirrup dimensions 212x412 give a 156 mm spacing ceiling => 150 mm.
    assert torsion.stirrup_spacing == pytest.approx(150.0)
