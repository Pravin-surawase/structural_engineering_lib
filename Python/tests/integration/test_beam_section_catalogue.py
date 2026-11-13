"""Replay each checked candidate against independent signed equilibrium."""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from structural_lib.design.is456 import beam

REFERENCE = json.loads(
    (
        Path(__file__).resolve().parents[3]
        / "docs/verification/library-029-flow02-beam-catalogue.json"
    ).read_text(encoding="utf-8")
)


def test_catalogue_matches_all_independent_candidates():
    request = beam.load_section_catalogue(json.dumps(REFERENCE["request"]))
    result = beam.select_section_catalogue(request)
    expected = REFERENCE["expected"]
    assert result.engineering_status.value == "PASS"
    data = result.calculation
    assert data["enumeration_complete"]
    assert data["selected_id"] == expected["selected_id"]
    assert data["eligible_ids"] == expected["eligible_ids"]
    assert data["catalogue_count"] == len(expected["evaluated"]) == 81
    for key, reference in expected["evaluated"].items():
        actual = data["evaluated"][key]
        assert actual["status"] == reference["status"]
        assert actual["governing_row_id"] == reference["governing_row_id"]
        assert actual["bottom_area_mm2"] == pytest.approx(reference["bottom_area_mm2"])
        if actual["status"] == "PASS":
            assert actual["capacities_knm"] == pytest.approx(
                reference["capacities_knm"], rel=1e-8
            )
    section = data["selected"]
    assert (
        section["request"]["reinforcement_revision"]
        != request.member.reinforcement_revision
    )
    assert section["ultimate_status"] == "PASS"
    replay = beam.check_section(beam.load_section(section["request"]))
    assert replay.to_dict() == section
    report = beam.render_section_catalogue_html(result)
    assert "2x20/2x16" in report
    assert result.to_dict()["envelope"]["result_identity"]["input_hash"] in report


@pytest.mark.parametrize(
    ("control", "expected"),
    (
        ("budget", "INCOMPLETE_BUDGET"),
        ("stale", "BLOCKED_MANDATORY_CHECK"),
        ("stiffness", "REANALYSIS_REQUIRED"),
        ("congested", "COMPLETE_INFEASIBLE"),
    ),
)
def test_catalogue_withholds_selection_when_mandatory_check_is_unresolved(
    control, expected
):
    request = deepcopy(REFERENCE["request"])
    if control == "budget":
        request["evaluation_limit"] = 4
    elif control == "stale":
        request["member"]["current_analysis_revision"] = "new-actions"
    elif control == "stiffness":
        request["analysis_basis"] = "reinforcement_dependent_stiffness"
    else:
        for layer in request["layers"]:
            layer["options"] = [
                {
                    "option_id": "congested",
                    "diameter_mm": 25,
                    "x_from_left_mm": [50, 70],
                }
            ]
    result = beam.select_section_catalogue(beam.load_section_catalogue(request))
    assert result.engineering_status.value == (
        "FAIL" if control == "congested" else "HOLD"
    )
    assert result.calculation["terminal_state"] == expected
    assert result.calculation["selected_id"] is None
    assert result.calculation["selected"] is None
    if control == "stale":
        assert result.envelope.freshness_status.value == "STALE"
