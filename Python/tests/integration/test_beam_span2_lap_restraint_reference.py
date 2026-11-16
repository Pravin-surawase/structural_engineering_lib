"""Frozen BEAM05 restrained second-span separated-lap acceptance."""

import hashlib
import html
import json
from copy import deepcopy
from pathlib import Path

import pytest

from structural_lib.design.is456 import beam

REFERENCE_PATH = (
    Path(__file__).resolve().parents[3]
    / "docs/verification/library-030-beam05-span2-lap-restraint-reference.json"
)
REFERENCE_SHA256 = "c0b199bea8f40dd71883e5c8c9df25e5da676d7921e46b20ff3d35a71c0cb16d"
REFERENCE = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
CASES = REFERENCE["cases"]


def test_compression_restraint_requires_a_checked_link_grid() -> None:
    raw = deepcopy(CASES["restrained_span2_lap"]["request"])
    raw["link_detail"]["last_station_mm"] -= 10
    request = beam.load_continuous_detailing(raw)
    result = beam.check_continuous_detailing(request)

    assert result.engineering_status.value == "HOLD"
    assert "BEAM.DETAIL_LINK_BASIS_HELD" in {issue.code for issue in result.issues}
    assert not result.calculation["lap"]["compression_restraint"]["verified"]
    assert beam.render_continuous_detailing_svg(result, current=request) is None
    assert beam.render_continuous_detailing_bbs_csv(result, current=request) is None


def _result(name: str):
    request = beam.load_continuous_detailing(CASES[name]["request"])
    result = beam.check_continuous_detailing(request)
    return (
        request,
        result,
        beam.render_continuous_detailing_html(result, current=request),
        beam.render_continuous_detailing_svg(result, current=request),
        beam.render_continuous_detailing_bbs_csv(result, current=request),
    )


def test_span2_lap_restraint_reference_is_frozen() -> None:
    assert hashlib.sha256(REFERENCE_PATH.read_bytes()).hexdigest() == REFERENCE_SHA256


@pytest.mark.parametrize(
    "name",
    (
        "restrained_span2_lap",
        "short_overlap",
        "congested_partner",
        "missing_lap_action",
        "stale_analysis",
        "original_unrestrained",
    ),
)
def test_span2_lap_restraint_fixture_outcomes(name: str) -> None:
    expected = CASES[name]["expected"]
    _, result, report, drawing, schedule = _result(name)

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


def test_restrained_span2_lap_preserves_signed_mechanics_and_artifacts() -> None:
    expected = CASES["restrained_span2_lap"]["expected"]
    _, result, report, drawing, schedule = _result("restrained_span2_lap")
    assert drawing is not None and schedule is not None

    lap = result.calculation["lap"]
    assert lap["lap_direction"] == expected["lap_direction"] == "decreasing_x"
    assert [lap[f"{name}_station_mm"] for name in ("start", "middle", "end")] == [
        5150,
        5800,
        6450,
    ]
    assert lap["overlap_mm"] == pytest.approx(expected["overlap_mm"])
    splice = lap["lap_result"]["outputs"]["splice_checks"][0]
    assert splice["actual_length_mm"] == pytest.approx(expected["overlap_mm"])
    assert splice["required_length_mm"] == pytest.approx(expected["required_lap_mm"])

    strength = result.calculation["strength"]
    primary = {row["action"]["row_id"]: row for row in strength["rows"]}
    partner = {row["action"]["row_id"]: row for row in lap["partner_rows"]}
    for reference in expected["signed_rows"]:
        actual = (
            primary[reference["row_id"]]
            if reference["layout"] == "upstream"
            else partner[reference["row_id"]]
        )
        assert actual["station"]["x_mm"] == pytest.approx(reference["station_mm"])
        assert actual["tension_face"] == reference["tension_face"]
        assert actual["diagnostic_only"] is reference["diagnostic_only"]
        assert actual["action"]["mu_knm"] == pytest.approx(reference["moment_knm"])
        assert actual["action"]["vu_kn"] == pytest.approx(reference["shear_kn"])
        assert actual["flexure_utilization"] == pytest.approx(
            reference["flexure_utilization"], abs=1e-4
        )
        assert actual["shear_utilization"] == pytest.approx(
            reference["shear_utilization"], abs=1e-4
        )

    for face in ("bottom", "top"):
        reference = expected["strength_by_layout"]["upstream"][face]
        actual = strength["flexural_sections"][face]["outputs"]
        assert actual["capacity_knm"] == pytest.approx(
            reference["capacity_knm"], abs=0.01
        )
        assert actual["effective_depth_mm"] == pytest.approx(
            reference["effective_depth_mm"], abs=0.001
        )

    paths = {
        path["bar_id"]: path
        for path in result.calculation["paths"]["outputs"]["reinforcement_schedule"][
            "paths"
        ]
    }
    for bar_id in ("B1-2", "B1-2-partner"):
        path = paths[bar_id]
        assert path["bar_mark"] == (
            "B-RECT_MULTILAYER-bottom-L1-D16-lap-I"
            if bar_id == "B1-2"
            else "B-RECT_MULTILAYER-bottom-L1-D16-lap-J"
        )
        assert [
            path["segments"][0]["start"]["station_x_mm"],
            path["segments"][-1]["end"]["station_x_mm"],
        ] == expected["drawing"]["bar_extents_mm"][bar_id]
    assert drawing in report
    assert "Lap-I · original" in drawing and "Lap-J · partner" in drawing


def test_restrained_span2_lap_reports_verified_actual_compression_restraint() -> None:
    expected = CASES["restrained_span2_lap"]["expected"]["compression_restraint"]
    _, result, _, _, _ = _result("restrained_span2_lap")
    restraint = result.calculation["lap"]["compression_restraint"]
    assert restraint["verified"] is True
    rows = restraint["layouts"]
    assert {(row["layout"], row["compression_face"]) for row in rows} == {
        ("upstream", "top"),
        ("downstream", "top"),
        ("downstream", "bottom"),
    }
    assert all(row["verified"] is True for row in rows)
    assert all(row["unresolved_bar_ids"] == [] for row in rows)
    top_rows = [row for row in rows if row["compression_face"] == "top"]
    assert all(row["corner_bar_ids"] == ["T1-1", "T1-2"] for row in top_rows)
    assert all(row["compressed_bar_ids"] == ["T1-1", "T1-2"] for row in top_rows)
    bottom = next(row for row in rows if row["compression_face"] == "bottom")
    assert bottom["corner_bar_ids"] == ["B1-1", "B1-3"]
    assert bottom["compressed_bar_ids"] == ["B1-1", "B1-2-partner", "B1-3"]
    assert (
        bottom["intermediate_centre_gaps_mm"]
        == expected["intermediate_centre_gaps_mm"]["downstream"]
    )
    assert all(row["row_ids"] for row in rows)


def test_original_span2_lap_is_withheld_for_unresolved_compression_restraint() -> None:
    expected = CASES["original_unrestrained"]["expected"]
    _, result, report, drawing, schedule = _result("original_unrestrained")
    restraint = result.calculation["lap"]["compression_restraint"]
    assert restraint["verified"] is False
    unresolved = {
        bar_id for row in restraint["layouts"] for bar_id in row["unresolved_bar_ids"]
    }
    assert expected["compression_bar_id"] in unresolved
    assert drawing is schedule is None
    assert "BBS held" in report
