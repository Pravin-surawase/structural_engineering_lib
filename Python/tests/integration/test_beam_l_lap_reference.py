"""Frozen BEAM05 L-beam separated-lap acceptance reference."""

import hashlib
import html
import json
from copy import deepcopy
from pathlib import Path

import pytest

from structural_lib.design.is456 import beam
from tests.integration.test_beam_t_lap_reference import (
    _assert_legacy_lap_restraint_hold,
    _assert_rows_and_capacities,
    _assert_sections_and_bbs,
)

REFERENCE_PATH = (
    Path(__file__).resolve().parents[3]
    / "docs/verification/library-030-beam05-l-lap-reference.json"
)
REFERENCE_SHA256 = "072f3b45c263fcbb05841726295e217bb09e648ba215d2b259e2c3f4b09703a0"
REFERENCE = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
CASES = REFERENCE["cases"]


def test_l_lap_reference_is_frozen() -> None:
    assert hashlib.sha256(REFERENCE_PATH.read_bytes()).hexdigest() == REFERENCE_SHA256


@pytest.mark.parametrize("name", CASES)
def test_l_lap_reference(name: str) -> None:
    case = CASES[name]
    expected = case["expected"]
    request = beam.load_continuous_detailing(case["request"])
    result = beam.check_continuous_detailing(request)
    report = beam.render_continuous_detailing_html(result, current=request)
    drawing = beam.render_continuous_detailing_svg(result, current=request)
    schedule = beam.render_continuous_detailing_bbs_csv(result, current=request)

    if expected["status"] == "PASS":
        _assert_legacy_lap_restraint_hold(result, report, drawing, schedule)
        _assert_rows_and_capacities(result.calculation, expected)
        return

    assert result.engineering_status.value == expected["status"]
    assert bool(report) is expected["report_available"]
    assert {issue.code for issue in result.issues} >= set(
        expected["required_issue_codes"]
    )
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
    if name == "l_lap":
        assert (
            "L beam with a 300 mm right overhang and a 120 mm flange. "
            "Physical width 600 mm."
        ) in report
        assert (
            f"Effective sagging flange width {expected['effective_flange_width_mm']:g} mm"
            in report
        )
        governor = expected["governing_lap_row"]
        assert (
            f"Governing lap moment {governor['row_id']} · "
            f"{governor['moment_knm']:.3f} kN·m against "
            f"{governor['half_capacity_knm']:.3f} kN·m."
        ) in report
        assert "Lap-I · original" in drawing and "Lap-J · partner" in drawing
        assert (
            f"Clear distance between lap pieces {expected['pair_clear_mm']:g} mm. "
            f"Required {expected['required_clear_mm']:g} mm."
        ) in report
    for check, governor in expected["governing_acceptance_rows"].items():
        assert f"{check} · {governor['row_id']}" in report
    assert request.member.analysis_revision in report
    assert request.member.reinforcement_revision in report
    assert result.envelope.result_identity.input_hash in report
    assert drawing in report

    _assert_rows_and_capacities(result.calculation, expected)
    _assert_sections_and_bbs(
        drawing,
        schedule,
        expected,
        result.envelope.result_identity.input_hash,
        result.calculation["paths"]["result_id"],
    )


@pytest.mark.parametrize(
    ("name", "left_mm", "right_mm"), [("l_lap", 300, 0), ("t_control", 300, 400)]
)
def test_flanged_lap_requires_supported_topology(
    name: str, left_mm: float, right_mm: float
) -> None:
    raw = deepcopy(CASES[name]["request"])
    raw["member"]["flange"].update(left_overhang_mm=left_mm, right_overhang_mm=right_mm)
    request = beam.load_continuous_detailing(raw)
    result = beam.check_continuous_detailing(request)

    assert result.engineering_status.value == "HOLD"
    assert "BEAM.LAYERED_BAR_DETAIL_HELD" in {issue.code for issue in result.issues}
    assert beam.render_continuous_detailing_svg(result, current=request) is None
    assert beam.render_continuous_detailing_bbs_csv(result, current=request) is None
