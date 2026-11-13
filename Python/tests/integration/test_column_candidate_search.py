"""Replay independent COL06 selections through the public installed API."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from xml.etree import ElementTree

import pytest

from structural_lib.core.errors import InputContractError
from structural_lib.design.is456 import column
from structural_lib.services.capabilities import get_supported_is456_capability_document

_REFERENCE = (
    Path(__file__).resolve().parents[3]
    / "docs/verification/library-029-col06-column-catalogue.json"
)
_FIXTURE = json.loads(_REFERENCE.read_text())
_CASES = _FIXTURE["cases"]


@pytest.mark.parametrize("name", tuple(_CASES))
def test_catalogue_matches_frozen_reference(name):
    case = _CASES[name]
    expected = case["expected"]
    request = column.load_column_catalogue(json.dumps(case["request"]))
    result = column.select_column_from_catalogue(request)
    payload = result.to_dict()
    calc = payload["calculation"]
    assert result.engineering_status.value == expected["engineering_status"]
    assert result.qualified_review_required
    for key in (
        "terminal_state",
        "catalogue_count",
        "enumeration_complete",
        "eligible_ids",
        "selected_id",
        "analysis_status",
    ):
        assert calc[key] == expected[key]
    assert calc["evaluated_count"] == len(expected["evaluated"])
    assert list(calc["evaluated"]) == list(expected["evaluated"])
    for identifier, reference in expected["evaluated"].items():
        actual = calc["evaluated"][identifier]
        assert actual["status"] == reference["status"]
        assert actual["bar_center_offset_mm"] == pytest.approx(
            reference["bar_center_offset_mm"],
            abs=_FIXTURE["tolerances"]["dimension_mm"],
        )
        assert actual["governing_combination_id"] == reference.get(
            "governing_combination_id"
        )
        assert list(actual["combinations"]) == list(reference["combinations"])
        for combination_id, row in reference["combinations"].items():
            check = actual["combinations"][combination_id]
            assert check["status"] == row["status"]
            if "issue" in reference:
                assert reference["issue"] in check["issue_codes"]
            if "utilization" in row:
                assert check["utilization"] == pytest.approx(
                    row["utilization"], abs=_FIXTURE["tolerances"]["utilization"]
                )
            else:
                assert check["utilization"] is None

    report = column.render_column_catalogue_html(result)
    svg = column.render_column_catalogue_svg(result)
    input_hash = payload["envelope"]["result_identity"]["input_hash"]
    assert input_hash in report
    assert expected["terminal_state"] in report
    assert expected["engineering_status"] in report
    if expected["selected_id"] is None:
        assert calc["selected"] is None
        assert svg is None
        assert "No candidate selected." in report
        assert "<svg" not in report
        return

    selected = calc["selected"]
    identifier = selected["candidate_id"]
    checked = selected["checked_member"]
    selected_summary = calc["evaluated"][identifier]
    governing = selected_summary["governing_combination_id"]
    assert identifier == expected["selected_id"]
    assert checked["envelope"]["engineering_status"] == "PASS"
    assert (
        checked["calculation"]["strength"]["governing_ratio"]
        == selected_summary["utilization"]
    )
    source_actions = next(
        action for action in request.actions if action.combination_id == governing
    )
    assert checked["request"]["actions"] == source_actions.model_dump(
        exclude={"combination_id"}
    )
    child_hash = checked["envelope"]["result_identity"]["input_hash"]
    assert child_hash == selected_summary["combinations"][governing]["check_input_hash"]
    assert svg is not None
    for output in (report, svg):
        assert child_hash in output and input_hash in output
        assert identifier in output
    assert svg in report
    root = ElementTree.fromstring(svg)
    ns = {"svg": "http://www.w3.org/2000/svg"}
    assert root.find("svg:title", ns).text.startswith(expected["engineering_status"])
    drawn_bars = {
        item.find("svg:title", ns).text: (
            float(item.get("cx")),
            float(item.get("cy")),
            float(item.get("r")),
        )
        for item in root.findall("svg:circle", ns)
    }
    assert drawn_bars == {
        bar["bar_id"]: (
            bar["x_from_left_mm"],
            bar["y_from_top_mm"],
            bar["diameter_mm"] / 2,
        )
        for bar in checked["calculation"]["cage"]["bars"]
    }
    assert len(drawn_bars) == 8
    assert [item.text for item in root.findall("svg:line/svg:title", ns)] == [
        tie["tie_id"] for tie in checked["calculation"]["cross_ties"]
    ]


def test_duplicate_combination_id_is_a_structured_input_error():
    payload = _CASES["nominal"]["request"]
    with pytest.raises(InputContractError) as exc:
        column.load_column_catalogue(dict(payload, actions=payload["actions"] * 2))
    assert "Supply unique combination IDs" in json.dumps(exc.value.to_problem())


def test_capability_profile_resolves_to_public_catalogue_api():
    document = get_supported_is456_capability_document()
    item = next(
        row for row in document["capabilities"] if row["capability_id"] == "column"
    )
    profile = next(
        row
        for row in item["python_profiles"]
        if row["operation"] == "select_column_from_catalogue"
    )
    module = importlib.import_module(profile["module"])
    request = getattr(module, profile["loader"])(_CASES["nominal"]["request"])
    result = getattr(module, profile["operation"])(request)
    assert request.schema_version == profile["request_schema"]
    assert result.workflow_id == profile["workflow_id"]
