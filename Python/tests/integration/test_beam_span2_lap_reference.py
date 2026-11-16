"""Frozen BEAM05 rectangular separated-lap acceptance in clear span two."""

import hashlib
import html
import json
from pathlib import Path

import pytest

from structural_lib.design.is456 import beam
from tests.integration.test_beam_t_lap_reference import (
    _assert_rows_and_capacities,
    _assert_sections_and_bbs,
)

REFERENCE_PATH = (
    Path(__file__).resolve().parents[3]
    / "docs/verification/library-030-beam05-span2-lap-reference.json"
)
REFERENCE_SHA256 = "234a223be34bf889c64e66c267ed60c121e677b6f26ddf7ddba8c51324318fe9"
REFERENCE = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
CASES = REFERENCE["cases"]


def test_span2_lap_reference_is_frozen() -> None:
    assert hashlib.sha256(REFERENCE_PATH.read_bytes()).hexdigest() == REFERENCE_SHA256


@pytest.mark.parametrize("name", CASES)
def test_span2_lap_reference_all_outcomes(name: str) -> None:
    expected = CASES[name]["expected"]
    request = beam.load_continuous_detailing(CASES[name]["request"])
    result = beam.check_continuous_detailing(request)
    report = beam.render_continuous_detailing_html(result, current=request)
    drawing = beam.render_continuous_detailing_svg(result, current=request)
    schedule = beam.render_continuous_detailing_bbs_csv(result, current=request)

    assert result.engineering_status.value == expected["status"]
    assert {issue.code for issue in result.issues} >= set(
        expected["required_issue_codes"]
    )
    assert bool(report) is expected["report_available"]
    assert (drawing is not None) is expected["checked_drawing_available"]
    assert (schedule is not None) is expected["bbs_available"]
    if expected["status"] != "PASS":
        assert result.calculation["bbs"] is None
        assert drawing is schedule is None
        assert "BBS held" in report
        assert "<svg" not in report.lower()
        assert all(html.escape(issue.message) in report for issue in result.issues)
        return

    assert drawing is not None and schedule is not None
    _assert_rows_and_capacities(result.calculation, expected)
    _assert_sections_and_bbs(
        drawing,
        schedule,
        expected,
        result.envelope.result_identity.input_hash,
        result.calculation["paths"]["result_id"],
    )
    lap = result.calculation["lap"]
    if name == "first_span_control":
        assert "lap_direction" not in lap
        return

    assert lap["lap_direction"] == expected["lap_direction"] == "decreasing_x"
    assert [
        lap[f"{position}_station_mm"] for position in ("start", "middle", "end")
    ] == [
        5150,
        5800,
        6450,
    ]
    assert {row["action"]["row_id"] for row in lap["partner_rows"]} == {
        row["row_id"]
        for row in expected["signed_rows"]
        if row["layout"] == "downstream"
    }
    paths = {
        bar["bar_id"]: [bar["start_station_mm"], bar["end_station_mm"]]
        for bar in lap["lap_result"]["effective_inputs"]["request"]["value"]["bars"]
    }
    assert paths == {
        bar_id: expected["drawing"]["bar_extents_mm"][bar_id]
        for bar_id in ("B1-3", "B1-3-partner")
    }
    governor = expected["governing_lap_row"]
    assert (
        f"Governing lap moment {governor['row_id']} · "
        f"{governor['moment_knm']:.3f} kN·m against "
        f"{governor['half_capacity_knm']:.3f} kN·m."
    ) in report
    assert (
        "Lap transfer toward decreasing x. Each transfer layout credits one lap piece."
        in report
    )
    assert "Lap-I · original" in drawing and "Lap-J · partner" in drawing
    assert drawing in report
