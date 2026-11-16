"""Verify the separated Ø20 lap on two physically checked link grids."""

import hashlib
import html
import json
from copy import deepcopy
from pathlib import Path

import pytest

from structural_lib.design.is456 import beam
from tests.integration.test_beam_t_lap_reference import (
    _assert_rows_and_capacities,
    _assert_sections_and_bbs,
)

REFERENCE_PATH = (
    Path(__file__).resolve().parents[3]
    / "docs/verification/library-030-beam05-flanged-lap-restraint-reference.json"
)
REFERENCE_SHA256 = "2c14a36ac2dd2a0a9a4cf321aa50da54c5c7d66f1de5d7ba6b20bd0a1b546f07"
CASES = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))["cases"]


def test_flanged_lap_reference_is_frozen() -> None:
    assert hashlib.sha256(REFERENCE_PATH.read_bytes()).hexdigest() == REFERENCE_SHA256


@pytest.mark.parametrize("name", CASES)
def test_flanged_lap_reference(name: str) -> None:
    case = CASES[name]
    expected = case["expected"]
    request = beam.load_continuous_detailing(case["request"])
    result = beam.check_continuous_detailing(request)
    report = beam.render_continuous_detailing_html(result, current=request)
    drawing = beam.render_continuous_detailing_svg(result, current=request)
    schedule = beam.render_continuous_detailing_bbs_csv(result, current=request)

    assert result.engineering_status.value == expected["status"]
    assert {issue.code for issue in result.issues} >= set(
        expected["required_issue_codes"]
    )
    assert bool(report) is expected["report_available"]
    assert bool(drawing) is expected["checked_drawing_available"]
    assert bool(schedule) is expected["bbs_available"]
    if expected["status"] != "PASS":
        assert result.calculation["bbs"] is None
        assert drawing is schedule is None
        assert "BBS held" in report
        assert "<svg" not in report.lower()
        assert all(html.escape(issue.message) in report for issue in result.issues)
        return

    assert drawing is not None and schedule is not None
    calculation = result.calculation
    _assert_rows_and_capacities(calculation, expected)
    identity = result.envelope.result_identity
    assert identity is not None and identity.input_hash is not None
    _assert_sections_and_bbs(
        drawing,
        schedule,
        expected,
        identity.input_hash,
        calculation["paths"]["result_id"],
    )
    lap = calculation["lap"]
    restraint = lap["compression_restraint"]
    assert restraint["verified"]
    assert (
        restraint["minimum_between_link_grids_mm"]
        == expected["compression_restraint"]["minimum_between_link_grids_mm"]
    )
    assert (
        restraint["corner_bar_ids_by_grid"]
        == expected["compression_restraint"]["corner_bar_ids_by_grid"]
    )
    for layout in restraint["layouts"]:
        tension_face = "bottom" if layout["compression_face"] == "top" else "top"
        assert layout["verified"] and not layout["unresolved_bar_ids"]
        assert (
            layout["compressed_bar_ids"]
            == expected["compression_restraint"]["compression_bar_ids_by_tension_face"][
                layout["layout"]
            ][tension_face]
        )
        assert sorted(layout["corner_bar_ids"]) == layout["compressed_bar_ids"]

    links = calculation["bbs"]["outputs"]["bbs"]["link_zones"]
    for zone, key, checks in zip(
        links,
        ("link_stations_mm", "restraint_link_stations_mm"),
        (calculation["link_check"], calculation["restraint_link_check"]),
        strict=True,
    ):
        assert zone["stations_x_mm"] == expected["drawing"][key]
        assert checks["outputs"]["placement_pass"]
        assert len(checks["outputs"]["checks"]) == zone["count"] == 41
        assert all(row["passed"] for row in checks["outputs"]["checks"])
    assert links[1]["bar_mark"] == expected["drawing"]["restraint_link_mark"]

    splice = lap["lap_result"]["outputs"]["splice_checks"][0]
    assert splice["actual_length_mm"] == pytest.approx(expected["overlap_mm"])
    assert splice["required_length_mm"] == pytest.approx(expected["required_lap_mm"])
    row_id, demand = max(
        expected["overlap_rows"].items(), key=lambda item: item[1]["moment_knm"]
    )
    assert (
        f"Governing lap moment {row_id} · {demand['moment_knm']:.3f} kN·m against "
        f"{demand['half_capacity_knm']:.3f} kN·m."
    ) in report
    for check, governor in expected["governing_acceptance_rows"].items():
        assert f"{check} · {governor['row_id']}" in report
    assert (
        f"Effective sagging flange width {expected['effective_flange_width_mm']:g} mm"
        in report
    )
    assert "Compression-bar restraint PASS" in report
    assert (
        f"Clear spacing between link grids {restraint['minimum_between_link_grids_mm']:g} mm"
        in report
    )
    assert "Closed link bend seats by grid" in report
    assert "Checked on nominal dimensions" in report
    assert drawing.count('data-link-display="projected"') == 6
    assert "Link shapes are projected onto each bar section" in drawing
    assert drawing in report


def test_supplementary_link_requires_clear_placement_grid() -> None:
    raw = deepcopy(CASES["l_lap"]["request"])
    raw["link_detail"]["restraint_link"]["station_offset_mm"] = 18
    request = beam.load_continuous_detailing(raw)
    result = beam.check_continuous_detailing(request)
    assert result.engineering_status.value == "HOLD"
    assert "BEAM.DETAIL_LINK_BASIS_HELD" in {issue.code for issue in result.issues}
    assert not result.calculation["lap"]["compression_restraint"]["verified"]
    assert beam.render_continuous_detailing_svg(result, current=request) is None
    assert beam.render_continuous_detailing_bbs_csv(result, current=request) is None
