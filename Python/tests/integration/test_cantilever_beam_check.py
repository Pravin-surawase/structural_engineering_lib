"""Replay independently frozen BEAM02 results through the public facade."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from structural_lib.design.is456 import beam
from structural_lib.services.capabilities import get_supported_is456_capabilities

REFERENCE = json.loads(
    (
        Path(__file__).resolve().parents[3]
        / "docs/verification/library-029-beam02-cantilever.json"
    ).read_text(encoding="utf-8")
)
CASES = REFERENCE["cases"]


def check(case):
    return beam.check_cantilever(beam.load_cantilever(deepcopy(CASES[case]["request"])))


@pytest.mark.parametrize("case", CASES)
def test_frozen_dispositions(case):
    expected = CASES[case]["ultimate_status"]
    if expected == "BLOCKED":
        with pytest.raises(beam.InputContractError, match="coordinate-side"):
            check(case)
        return
    result = check(case)
    assert result.ultimate_status == expected
    assert result.serviceability_status == "HOLD"
    output = result.to_dict()
    assert output["schema_version"] == "is456-cantilever-beam-result/v1"
    assert output["result_envelope"]["qualified_review_required"] is True
    assert "bbs" not in output
    json.dumps(output, allow_nan=False)


def test_physical_checks_match_frozen_resistance_and_signed_actions():
    result = check("point_and_udl")
    tolerance = REFERENCE["tolerances"]
    for face, flexure in result.flexural_sections.items():
        expected = REFERENCE["section"][face]
        assert flexure.outputs["capacity_knm"] == pytest.approx(
            expected["capacity_knm"], abs=tolerance["capacity_knm"]
        )
        assert flexure.outputs["equilibrium_neutral_axis_depth_mm"] == pytest.approx(
            expected["xu_mm"], abs=tolerance["xu_mm"]
        )
        assert flexure.outputs["effective_depth_mm"] == expected["d_mm"]
        assert flexure.outputs["tension_steel_area_mm2"] == pytest.approx(
            expected["tension_area_mm2"]
        )
        for field, target in (
            ("concrete_capacity_kn", "concrete_shear_kn"),
            ("stirrup_capacity_kn", "link_shear_kn"),
            ("provided_capacity_kn", "shear_capacity_kn"),
        ):
            assert result.shear_sections[face].outputs[field] == pytest.approx(
                expected[target], abs=tolerance["shear_kn"]
            )
    rows = {row.action.row_id: row for row in result.rows}
    for row_id, (moment, shear) in REFERENCE["station_targets"].items():
        row = rows[row_id]
        assert not row.diagnostic_only
        assert (row.action.mu_knm, row.action.vu_kn) == (moment, shear)
    left, right = rows["POINT:P-LEFT"], rows["POINT:P-RIGHT"]
    assert left.station.x_mm == right.station.x_mm == 1000
    assert (left.station.side, right.station.side) == ("LEFT", "RIGHT")
    assert right.action.vu_kn - left.action.vu_kn == REFERENCE["point_shear_jump_kn"]
    fixed = rows["POINT:FIXED"]
    assert fixed.tension_face == "top"
    assert result.governing_rows == {
        "hogging": REFERENCE["governing_hogging_row"],
        "shear": REFERENCE["governing_shear_row"],
    }
    assert fixed.anchorage is not None
    assert {item["bar_id"] for item in fixed.anchorage.outputs["checks"]} == {
        "T1",
        "T2",
        "T3",
    }
    for item in fixed.anchorage.outputs["checks"]:
        assert item["required_development_length_mm"] == pytest.approx(
            REFERENCE["section"]["top"]["development_mm"]
        )
        assert (
            item["available_for_criterion_mm"]
            == REFERENCE["fixed_anchorage_available_mm"]
        )
        assert item["passed"]


def test_missing_and_stale_rows_hold_without_dropping_evidence():
    result = check("missing_side")
    assert any(
        issue.code == "BEAM_ACTION_MISSING"
        and issue.path == "combinations.POINT.P-RIGHT"
        for issue in result.result_envelope.issues
    )
    stale = check("stale_analysis")
    assert stale.result_envelope.overall_status.value == "STALE"
    assert stale.geometry is None and all(
        row.section_status is None for row in stale.rows
    )
    short = check("short_anchorage")
    fixed = next(row for row in short.rows if row.action.row_id == "POINT:FIXED")
    assert fixed.section_status == "PASS" and fixed.anchorage is not None
    assert fixed.anchorage.outputs["checks"][0]["available_for_criterion_mm"] == (
        REFERENCE["short_anchorage_available_mm"]
    )
    assert not fixed.anchorage.outputs["checks"][0]["passed"]


def test_reordering_preserves_result_identity_and_report():
    request = deepcopy(CASES["point_and_udl"]["request"])
    baseline = check("point_and_udl")
    for name in ("bars", "stations", "combinations", "actions"):
        request[name].reverse()
    for combo in request["combinations"]:
        combo["required_station_ids"].reverse()
    result = beam.check_cantilever(beam.load_cantilever(json.dumps(request)))
    assert result.rows == baseline.rows
    assert result.result_envelope == baseline.result_envelope
    report = beam.render_cantilever_html(result)
    assert report == beam.render_cantilever_html(baseline)
    assert "POINT:P-LEFT" in report and "POINT:P-RIGHT" in report
    assert "B02-A1" in report and "B02-R1" in report
    assert (
        result.to_dict()["result_envelope"]["result_identity"]["input_hash"] in report
    )


def test_cantilever_discovery_points_to_public_workflow():
    item = next(x for x in get_supported_is456_capabilities() if x.element == "beam")
    profile = next(x for x in item.python_profiles if x.operation == "check_cantilever")
    assert profile.loader == "load_cantilever"
    assert profile.request_schema == "is456-cantilever-beam-check/v1"
