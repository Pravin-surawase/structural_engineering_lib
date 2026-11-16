"""Frozen BEAM05 rectangular multilayer lap-placement replay."""

import hashlib
import html
import json
from copy import deepcopy
from pathlib import Path

import pytest

from structural_lib.design.is456 import beam
from tests.integration.test_beam_lap_placement_reference import _assert_reference
from tests.integration.test_beam_t_lap_reference import _assert_sections_and_bbs

REFERENCE_PATH = (
    Path(__file__).resolve().parents[3]
    / "docs/verification/library-030-beam05-rectangular-lap-placement-reference.json"
)
REFERENCE_SHA256 = "3736cf58b4f457d3bdb36a27be20730c5256ac5ea9bf2ddc92faeda7eaa9a649"
REFERENCE = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
CASES = REFERENCE["cases"]

PLACEMENT_ISSUES = {
    "placement_interference": "BEAM.LAP_PLACEMENT_INTERFERENCE",
    "restraint_sector_unresolved": "BEAM.LAP_RESTRAINT_SECTOR_HELD",
    "placement_basis_missing": "BEAM.LAP_PLACEMENT_EVIDENCE_HELD",
}


def _request(case: dict) -> dict:
    raw = deepcopy(case["request"])
    if "placement" in case:
        raw["placement_envelope"] = case["placement"]
    return raw


def test_rectangular_lap_placement_reference_is_frozen() -> None:
    assert hashlib.sha256(REFERENCE_PATH.read_bytes()).hexdigest() == REFERENCE_SHA256


def test_rectangular_lap_placement_pass_replays_signed_and_adverse_design() -> None:
    case = CASES["rectangular_lap"]
    expected = case["expected"]
    request = beam.load_continuous_detailing(_request(case))
    result = beam.check_continuous_detailing(request)
    report = beam.render_continuous_detailing_html(result, current=request)
    drawing = beam.render_continuous_detailing_svg(result, current=request)
    schedule = beam.render_continuous_detailing_bbs_csv(result, current=request)

    assert result.engineering_status.value == expected["status"] == "PASS"
    assert result.calculation["strength"]["governing_rows"] == {
        check: reference["row_id"]
        for check, reference in case["nominal_governing_acceptance_rows"].items()
    }
    for check, reference in case["nominal_governing_acceptance_rows"].items():
        assert reference["row_id"] in reference["tied_row_ids"]
        row = next(
            row
            for row in result.calculation["strength"]["rows"]
            if row["action"]["row_id"] == reference["row_id"]
        )
        utilization = (
            row["flexure_utilization"]
            if check in {"sagging", "hogging"}
            else row["shear_utilization"]
        )
        assert utilization == pytest.approx(reference["utilization"], abs=1e-9)

    placement = result.calculation["placement"]
    assert placement["status"] == "PASS"
    _assert_reference(placement, expected)
    assert placement["minimum_overlap_mm"] == pytest.approx(case["minimum_overlap_mm"])
    assert placement["minimum_straight_support_development_mm"] == pytest.approx(
        case["minimum_straight_support_development_mm"]
    )
    _assert_reference(placement["worst_strength"], case["worst_strength"])

    assert drawing is not None and schedule is not None
    assert drawing in report
    identity = result.envelope.result_identity
    assert identity is not None and identity.input_hash is not None
    _assert_sections_and_bbs(
        drawing,
        schedule,
        case,
        identity.input_hash,
        result.calculation["paths"]["result_id"],
    )


@pytest.mark.parametrize("name", [name for name in CASES if name != "rectangular_lap"])
def test_rectangular_lap_placement_controls_are_diagnostic_only(name: str) -> None:
    case = CASES[name]
    expected = case["expected"]
    request = beam.load_continuous_detailing(_request(case))
    result = beam.check_continuous_detailing(request)
    report = beam.render_continuous_detailing_html(result, current=request)
    drawing = beam.render_continuous_detailing_svg(result, current=request)
    schedule = beam.render_continuous_detailing_bbs_csv(result, current=request)

    assert result.engineering_status.value == expected["status"]
    issue_codes = {issue.code for issue in result.issues}
    if "required_issue_codes" in expected:
        assert issue_codes >= set(expected["required_issue_codes"])
    else:
        assert PLACEMENT_ISSUES[expected["issue"]] in issue_codes
        _assert_reference(result.calculation["placement"], expected)

    assert result.calculation["bbs"] is None
    assert drawing is schedule is None
    assert "BBS held" in report
    assert "<svg" not in report.lower()
    assert all(html.escape(issue.message) in report for issue in result.issues)
