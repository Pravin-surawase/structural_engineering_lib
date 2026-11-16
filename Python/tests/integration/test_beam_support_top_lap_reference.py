"""Frozen BEAM05 support-top-lap acceptance reference replay."""

import hashlib
import html
import json
from pathlib import Path

import pytest

from structural_lib.design.is456 import beam
from tests.integration.test_beam_lap_placement_reference import (
    ISSUE_CODES,
    _assert_reference,
    _request,
)
from tests.integration.test_beam_t_lap_reference import _assert_sections_and_bbs

REFERENCE_PATH = (
    Path(__file__).resolve().parents[3]
    / "docs/verification/library-030-beam05-support-top-lap-reference.json"
)
REFERENCE_SHA256 = "82a07e7f2b958df4c1e041667039d7e2d50a16d4b1f68130463d78853168e0df"
REFERENCE = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
CASES = REFERENCE["cases"]


def test_support_top_lap_reference_is_frozen() -> None:
    assert hashlib.sha256(REFERENCE_PATH.read_bytes()).hexdigest() == REFERENCE_SHA256


@pytest.mark.parametrize("name", CASES)
def test_support_top_lap_reference(name: str) -> None:
    case = CASES[name]
    expected = case["expected"]
    request = beam.load_continuous_detailing(_request(case))
    result = beam.check_continuous_detailing(request)
    report = beam.render_continuous_detailing_html(result, current=request)
    drawing = beam.render_continuous_detailing_svg(result, current=request)
    schedule = beam.render_continuous_detailing_bbs_csv(result, current=request)

    assert result.engineering_status.value == expected["status"]
    if expected["status"] != "PASS":
        expected_codes = expected.get("required_issue_codes")
        if expected_codes is None:
            expected_codes = [ISSUE_CODES[expected["issue"]]]
        assert {issue.code for issue in result.issues} >= set(expected_codes)
        assert result.calculation["bbs"] is None
        assert drawing is schedule is None
        assert "BBS held" in report
        assert "<svg" not in report.lower()
        assert all(html.escape(issue.message) in report for issue in result.issues)
        if "issue" in expected:
            _assert_reference(result.calculation["placement"], expected)
        return

    assert drawing is not None and schedule is not None
    placement = result.calculation["placement"]
    _assert_reference(placement, expected)
    assert placement["minimum_overlap_mm"] == pytest.approx(case["minimum_overlap_mm"])
    assert placement["minimum_straight_support_development_mm"] == pytest.approx(
        case["minimum_straight_support_development_mm"]
    )
    assert placement["minimum_lap_cover_mm"] == pytest.approx(
        case["minimum_lap_cover_mm"]
    )
    _assert_reference(placement["worst_strength"], case["worst_strength"])
    _assert_reference(
        placement["negative_steel_continuity"], case["negative_steel_continuity"]
    )
    _assert_retained_support_anchorage(placement, case)
    restraint = result.calculation["lap"]["compression_restraint"]
    assert restraint["verified"] and restraint["placement_envelope_verified"]
    for layout in restraint["layouts"]:
        tension_face = "top" if layout["compression_face"] == "bottom" else "bottom"
        expected_bars = case["compression_bar_ids_by_tension_face"][layout["layout"]]
        assert layout["compressed_bar_ids"] == expected_bars[tension_face]
        assert layout["verified"] and not layout["unresolved_bar_ids"]

    governing_rows = result.calculation["strength"]["governing_rows"]
    assert governing_rows == {
        kind: reference["row_id"]
        for kind, reference in case["nominal_governing_acceptance_rows"].items()
    }
    identity = result.envelope.result_identity
    assert identity is not None and identity.input_hash is not None
    assert identity.input_hash in report
    assert request.member.analysis_revision in report
    assert request.member.reinforcement_revision in report
    assert drawing in report
    for metric in (
        placement["minimum_overlap_mm"],
        placement["minimum_straight_support_development_mm"],
        placement["minimum_lap_cover_mm"],
    ):
        assert f"{metric:g}" in report
    _assert_sections_and_bbs(
        drawing,
        schedule,
        case,
        identity.input_hash,
        result.calculation["paths"]["result_id"],
    )


def _assert_retained_support_anchorage(placement: dict, case: dict) -> None:
    """The retained nominal bar is checked on its tolerance-shortened partner."""
    retained = placement["retained_support_anchorage"]
    adverse = case["adverse_support_anchorage"]
    expected_keys = {
        f"{combination}:{face}"
        for combination in ("U1", "U2")
        for face in ("BF1", "BF2")
    }
    assert retained.keys() == expected_keys
    for row_id, actual in retained.items():
        partner_bar_id = "T1-3-partner"
        assert actual["bar_id"] == partner_bar_id
        reference = adverse[row_id]
        assert actual["direction"] == reference["direction"]
        _assert_reference(
            {
                key: actual[key]
                for key in ("straight_available_mm", "development_required_mm")
            },
            reference["checks_by_bar"][partner_bar_id],
        )
