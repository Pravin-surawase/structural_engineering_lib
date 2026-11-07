"""Outcome regressions for the five reproduced 0.27 consumer defects."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

from structural_lib import api
from structural_lib.core.errors import InputContractError
from structural_lib.design.is456 import beam, column
from structural_lib.reports import generator

ROOT = Path(__file__).resolve().parents[3]
COLUMN = {
    "Pu_kN": 500,
    "Mux_kNm": 400,
    "Muy_kNm": 0,
    "b_mm": 300,
    "D_mm": 450,
    "l_mm": 6000,
    "end_condition": "HINGED_HINGED",
    "fck_nmm2": 25,
    "fy_nmm2": 415,
    "Asc_mm2": 2400,
    "d_prime_mm": 50,
    "braced": True,
}
BEAM = {
    "units": "IS456",
    "b_mm": 300,
    "D_mm": 500,
    "d_mm": 444,
    "fck_nmm2": 25,
    "fy_nmm2": 500,
    "mu_knm": 150,
    "vu_kn": 100,
}


def canonical_request():
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
        member_id="B1",
        story="L1",
        case_id="ULS-1",
        span_mm=5000,
        b_mm=300,
        D_mm=550,
        d_mm=492,
        fck_nmm2=25,
        fy_nmm2=500,
        mu_knm=150,
        vu_kn=80,
        d_dash_mm=56,
        asv_mm2=options.asv_mm2,
        detailing=options,
    )


@pytest.mark.parametrize("axis", ["x", "y"])
def test_slender_conflicting_declared_demand_is_structured_rejection(axis):
    args = {**COLUMN, "Mux_kNm": 0, "Muy_kNm": 0, f"Mu{axis}_kNm": 400}
    with pytest.raises(InputContractError) as error:
        api.design_column_is456(**args, M1x_kNm=0, M2x_kNm=0, M1y_kNm=0, M2y_kNm=0)
    issue = error.value.issues[0]
    assert issue.code == "COLUMN_ACTION_CONFLICT"
    assert issue.path == f"Mu{axis}_kNm"
    assert issue.received["applied_kNm"] == 400


@pytest.mark.parametrize("ends", [None, (400, 400), (-400, -400)])
def test_consistent_column_demand_preserves_overload(ends):
    values = {} if ends is None else {"M1x_kNm": ends[0], "M2x_kNm": ends[1]}
    result = api.design_column_is456(**COLUMN, M1y_kNm=0, M2y_kNm=0, **values)
    assert result["Mux_design_kNm"] == 420
    assert result["is_safe"] is False
    assert result["result_envelope"]["engineering_status"] == "FAIL"


@pytest.mark.parametrize(
    "ends", [(0, 0), (-60, 100), (60, -100), (50, 100), (None, 100)]
)
def test_slender_signed_ends_and_minimum_defaults_remain_admitted(ends):
    applied = 0 if ends == (0, 0) else 50
    result = api.design_column_is456(
        **{**COLUMN, "Mux_kNm": applied}, M1x_kNm=ends[0], M2x_kNm=ends[1]
    )
    assert result["Mux_design_kNm"] >= max(applied, abs(ends[1]))
    assert result["Mux_design_kNm"] >= result["Mux_min_kNm"]
    assert result["Muy_design_kNm"] >= result["Muy_min_kNm"]


def test_zero_omitted_end_defaults_keep_existing_minimum_eccentricity_basis():
    result = api.design_column_is456(**{**COLUMN, "Mux_kNm": 0})
    assert result["Mux_design_kNm"] == 33.5
    assert result["Muy_design_kNm"] == 41


def test_slender_end_order_rejection_and_short_action_control():
    with pytest.raises(InputContractError) as error:
        api.design_column_is456(**COLUMN, M1x_kNm=400, M2x_kNm=0)
    assert error.value.issues[0].code == "COLUMN_END_MOMENT_ORDER"
    short = api.design_column_is456(**{**COLUMN, "l_mm": 3000}, M1x_kNm=0, M2x_kNm=0)
    assert short["classification"] == "SHORT"
    assert short["Mux_design_kNm"] == 400 and not short["is_safe"]


def test_canonical_column_preserves_rejected_action_field_path():
    request = column.load(
        {
            "identity": {"family_id": "column", "case_id": "ULS", "member_id": "C1"},
            "geometry": {
                "b_mm": 300,
                "D_mm": 450,
                "unsupported_length_mm": 6000,
                "minimum_eccentricity_length_mm": 6000,
                "end_condition": "HINGED_HINGED",
                "braced": True,
            },
            "actions": {
                "pu_kn": 500,
                "mux_knm": 400,
                "muy_knm": 0,
                "m1x_signed_knm": 0,
                "m2x_signed_knm": 0,
                "m1y_signed_knm": 0,
                "m2y_signed_knm": 0,
            },
            "materials": {"fck_nmm2": 25, "fy_nmm2": 415},
            "reinforcement": {
                "supplied_steel_area_mm2": 2400,
                "reinforcement_centroid_depth_mm": 50,
            },
        }
    )
    with pytest.raises(InputContractError) as error:
        column.check(request)
    assert error.value.issues[0].code == "COLUMN_ACTION_CONFLICT"
    assert error.value.issues[0].path == "actions.mux_knm"


@pytest.mark.parametrize("combined", [False, True])
def test_canonical_report_retains_original_basis_steel_and_envelope(combined):
    request = canonical_request()
    result = beam.design_and_detail(request) if combined else beam.design(request)
    report = api.generate_calculation_report(result)
    data = json.loads(report.to_json())
    assert data["source"]["request"] == request.model_dump(mode="json")
    assert data["result_envelope"] == result.envelope.to_dict()
    assert data["inputs"]["loads"][0] == {
        "case_id": "ULS-1",
        "mu_knm": 150,
        "vu_kn": 80,
        "tu_knm": 0,
    }
    assert data["inputs"]["materials"]["fck_nmm2"] == 25
    assert data["inputs"]["geometry"]["d_mm"] == 492
    # Retained-wheel review value, rounded to its reported precision.
    assert data["results"]["flexure"]["ast_required"] == pytest.approx(
        785.79, abs=0.005
    )
    assert data["results"]["flexure"]["ast_provided"] is None
    if combined:
        assert len(beam.bbs(result).items) == 9
        rows = data["results"]["detailing"]["bottom_bars"]
        assert len(rows) == 3 and all(row["count"] == 3 for row in rows)
        assert all(
            row["area_provided_mm2"] > data["results"]["flexure"]["ast_required"]
            for row in rows
        )
    else:
        assert data["results"]["detailing"] == {
            "status": "unavailable",
            "reason": "design_only",
        }
    assert data["results"]["summary"]["engineering_status"] == "PASS"
    assert data["result_envelope"]["review_status"] == "QUALIFIED_REVIEW_REQUIRED"


@pytest.mark.parametrize("fallback", [False, True])
@pytest.mark.parametrize("template", ["beam_design", "summary", "detailed"])
def test_canonical_html_reports_preserve_outcome_and_evidence(
    monkeypatch, fallback, template
):
    if not fallback:
        pytest.importorskip("jinja2")
    monkeypatch.setattr(generator, "JINJA2_AVAILABLE", not fallback)
    result = beam.design_and_detail(canonical_request())
    document = generator.generate_html_report(result, template=template)
    badge = re.search(
        r'<span class="(?:status-badge [^"]+|status)">\s*([^<]+)', document
    )
    assert badge is not None and badge[1].strip() == "PASS"
    text = html.unescape(re.sub(r"<[^>]+>", " ", document))
    assert "PASS" in text and "QUALIFIED_REVIEW_REQUIRED" in text
    assert "785.79" in text or "785.787" in text
    assert "ULS-1" in text and "492" in text and "150" in text
    assert "Provided reinforcement" in text and "area_provided_mm2" in text
    assert "NOT EVALUATED" in text


@pytest.mark.parametrize("combined", [False, True])
def test_legacy_report_keeps_retained_inputs_and_actual_actions(combined):
    result = (
        api.design_and_detail_beam_is456(
            **BEAM, beam_id="B12", story="L2", span_mm=6000, cover_mm=40
        )
        if combined
        else api.design_beam_is456(**BEAM)
    )
    data = api.generate_calculation_report(result).to_dict()
    assert data["inputs"]["geometry"]["b_mm"] == 300
    assert data["inputs"]["geometry"]["d_mm"] == 444
    assert data["inputs"]["materials"] == {"fck_nmm2": 25, "fy_nmm2": 500}
    assert data["inputs"]["loads"][0]["mu_knm"] == 150
    assert data["inputs"]["loads"][0]["vu_kn"] == 100
    calculation = result.design if combined else result
    assert data["results"]["shear"]["tau_v"] == calculation.shear.tau_v
    if not combined:
        assert "span_mm" not in data["inputs"]["geometry"]
        assert "cover_mm" not in data["inputs"]["geometry"]


@pytest.mark.parametrize("output_format", ["json", "html", "markdown"])
def test_serviceability_only_failure_is_explained_in_every_report(
    tmp_path, output_format
):
    result = api.design_beam_is456(
        **BEAM,
        deflection_params={
            "span_mm": 10000,
            "d_mm": 444,
            "support_condition": "simply_supported",
            "mf_tension_steel": 0.5,
        },
    )
    assert result.flexure.is_safe and result.shear.is_safe and not result.is_ok
    path = tmp_path / f"failure.{output_format}"
    report = api.generate_calculation_report(
        result, output_path=path, output_format=output_format
    )
    assert report.results.summary["failed_checks"] == ["deflection"]
    check = report.results.serviceability["deflection"]
    assert check["is_ok"] is False
    assert check["computed"]["ld_ratio"] == pytest.approx(10000 / 444)
    assert check["computed"]["allowable_ld"] == 10
    text = html.unescape(path.read_text(encoding="utf-8"))
    assert "deflection" in text and "22.522522" in text and "allowable_ld" in text
    assert "QUALIFIED_REVIEW_REQUIRED" in text
    assert report.results.summary["engineering_status"] == "FAIL"


def test_report_adapter_rejects_unrecognized_result_without_shape_guess():
    with pytest.raises(TypeError, match="Beam reports require"):
        api.generate_calculation_report(SimpleNamespace(design=object()))
    with pytest.raises(TypeError, match="typed canonical beam result"):
        generator.generate_html_report(beam.design(canonical_request()).to_dict())


def test_exact_developer_quickstart_base_journey(tmp_path, monkeypatch):
    guide = ROOT / "docs/developers/platform-guide.md"
    blocks = re.findall(r"```python\n(.*?)```", guide.read_text(encoding="utf-8"), re.S)
    namespace = {}
    monkeypatch.chdir(tmp_path)
    for marker in ("# quick_start_example.py", "# verify_quickstart_outputs"):
        block = next(block for block in blocks if marker in block)
        exec(compile(block, str(guide), "exec"), namespace)
    assert len(namespace["schedule"].items) == 9
    assert (tmp_path / "beam_B1_outputs/beam_B1.html").is_file()
