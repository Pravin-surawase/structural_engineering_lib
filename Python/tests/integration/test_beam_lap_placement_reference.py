"""Frozen BEAM05 lap placement-envelope reference replay."""

import hashlib
import html
import json
from copy import deepcopy
from pathlib import Path

import pytest

from structural_lib.design.is456 import beam
from tests.integration.test_beam_t_lap_reference import _assert_sections_and_bbs

REFERENCE_PATH = (
    Path(__file__).resolve().parents[3]
    / "docs/verification/library-030-beam05-lap-placement-reference.json"
)
REFERENCE_SHA256 = "fa7f06829923cccc26aae6669be692ff326d7b8ab059fa9166b38d7909bd777b"
REFERENCE = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
CASES = REFERENCE["cases"]
NOMINAL_REFERENCE_PATH = (
    Path(__file__).resolve().parents[3]
    / "docs/verification/library-030-beam05-flanged-lap-restraint-reference.json"
)
NOMINAL_CASES = json.loads(NOMINAL_REFERENCE_PATH.read_text(encoding="utf-8"))["cases"]

ISSUE_CODES = {
    "placement_interference": "BEAM.LAP_PLACEMENT_INTERFERENCE",
    "restraint_sector_unresolved": "BEAM.LAP_RESTRAINT_SECTOR_HELD",
    "placement_basis_missing": "BEAM.LAP_PLACEMENT_EVIDENCE_HELD",
}


def _assert_reference(actual, expected) -> None:
    """Compare a reference-shaped result, allowing only numerical round-off."""
    if isinstance(expected, dict):
        assert actual.keys() >= expected.keys()
        for key, value in expected.items():
            _assert_reference(actual[key], value)
    elif isinstance(expected, list):
        assert len(actual) == len(expected)
        for actual_value, expected_value in zip(actual, expected, strict=True):
            _assert_reference(actual_value, expected_value)
    elif isinstance(expected, float):
        assert actual == pytest.approx(expected, abs=1e-9)
    else:
        assert actual == expected


def _request(case: dict) -> dict:
    raw = deepcopy(case["request"])
    # An explicit None requests evidence checking and differs from omission.
    raw["placement_envelope"] = case["placement"]
    return raw


def test_lap_placement_reference_is_frozen() -> None:
    assert hashlib.sha256(REFERENCE_PATH.read_bytes()).hexdigest() == REFERENCE_SHA256


@pytest.mark.parametrize("name", CASES)
def test_lap_placement_reference(name: str) -> None:
    case = CASES[name]
    expected = case["expected"]
    request = beam.load_continuous_detailing(_request(case))
    result = beam.check_continuous_detailing(request)
    report = beam.render_continuous_detailing_html(result, current=request)
    drawing = beam.render_continuous_detailing_svg(result, current=request)
    schedule = beam.render_continuous_detailing_bbs_csv(result, current=request)

    placement = result.calculation["placement"]
    assert result.engineering_status.value == expected["status"]
    assert placement["status"] == expected["status"]
    assert placement["issue"] == expected["issue"]
    if "returns" in expected:
        _assert_reference(placement, expected)

    if expected["status"] != "PASS":
        assert ISSUE_CODES[expected["issue"]] in {issue.code for issue in result.issues}
        assert result.calculation["bbs"] is None
        assert drawing is schedule is None
        assert "BBS held" in report
        assert "<svg" not in report.lower()
        assert all(html.escape(issue.message) in report for issue in result.issues)
        return

    assert drawing is not None and schedule is not None
    assert drawing in report
    assert "<svg" in report.lower()
    _assert_reference(placement, expected)
    assert placement["minimum_overlap_mm"] == pytest.approx(case["minimum_overlap_mm"])
    assert placement["minimum_straight_support_development_mm"] == pytest.approx(
        case["minimum_straight_support_development_mm"]
    )
    _assert_reference(placement["worst_strength"], case["worst_strength"])
    for metric in (
        placement["minimum_overlap_mm"],
        placement["minimum_straight_support_development_mm"],
        placement["minimum_steel_cover_mm"],
    ):
        assert f"{metric:g}" in report

    identity = result.envelope.result_identity
    assert identity is not None and identity.input_hash is not None
    _assert_sections_and_bbs(
        drawing,
        schedule,
        case,
        identity.input_hash,
        result.calculation["paths"]["result_id"],
    )


def test_omitted_placement_envelope_preserves_historical_lap_workflow() -> None:
    raw = deepcopy(NOMINAL_CASES["l_lap"]["request"])
    request = beam.load_continuous_detailing(raw)
    result = beam.check_continuous_detailing(request)
    assert result.engineering_status.value == "PASS"
    assert "placement" not in result.calculation

    raw = deepcopy(CASES["l_lap"]["request"])
    request = beam.load_continuous_detailing(raw)
    result = beam.check_continuous_detailing(request)
    assert result.engineering_status.value == "HOLD"
    assert "BEAM.LAP_COMPRESSION_RESTRAINT_HELD" in {
        issue.code for issue in result.issues
    }
    assert "placement" not in result.calculation
