"""Replay the independently frozen BEAM01 and FLOW01 source rows."""

from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from structural_lib.design.is456 import beam
from structural_lib.services.capabilities import get_supported_is456_capabilities

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "docs/verification/library-029-beam01-flow01.json"
REFERENCE = json.loads(FIXTURE.read_text(encoding="utf-8"))
CASES = REFERENCE["cases"]


def check(case):
    return beam.check_continuous(beam.load_continuous(deepcopy(CASES[case]["request"])))


@pytest.mark.parametrize("case", CASES)
def test_frozen_statuses(case):
    expected = CASES[case]["ultimate_status"]
    if expected == "BLOCKED":
        with pytest.raises(beam.InputContractError, match="Station IDs"):
            check(case)
        return
    result = check(case)
    assert result.ultimate_status == expected
    assert result.serviceability_status == "HOLD"
    assert result.result_envelope.to_dict()["qualified_review_required"] is True
    assert "bbs" not in result.to_dict()
    json.dumps(result.to_dict(), allow_nan=False)


def test_both_signs_match_independent_resistance_and_faces():
    result = check("two_span")
    reference = REFERENCE["section"]
    tolerance = REFERENCE["tolerances"]
    for face, section in result.flexural_sections.items():
        values = section.outputs
        assert values["capacity_knm"] == pytest.approx(
            reference["flexural_capacity_knm"], abs=tolerance["capacity_knm"]
        )
        assert values["equilibrium_neutral_axis_depth_mm"] == pytest.approx(
            reference["xu_mm"], abs=tolerance["xu_mm"]
        )
        assert values["effective_depth_mm"] == pytest.approx(reference["d_mm"])
        assert values["tension_steel_area_mm2"] == pytest.approx(
            reference["tension_area_mm2"]
        )
        assert all(
            (bar["net_force_n"] < 0) == (bar["face"] == face)
            for bar in values["bar_responses"]
        )
        shear = result.shear_sections[face].outputs
        for field, target in (
            ("concrete_capacity_kn", "concrete_shear_kn"),
            ("stirrup_capacity_kn", "link_shear_kn"),
            ("provided_capacity_kn", "shear_capacity_kn"),
            ("limiting_capacity_kn", "max_shear_kn"),
        ):
            assert shear[field] == pytest.approx(
                reference[target], abs=tolerance["shear_kn"]
            )
    rows = {item.action.row_id: item for item in result.rows}
    for name in ("B01:L-MID", "B01:R-MID"):
        assert rows[name].tension_face == "bottom"
        assert rows[name].flexure_utilization == pytest.approx(
            REFERENCE["actions"]["sagging_utilization"]
        )
    assert rows["B01:B-LEFT"].tension_face == "top"
    assert rows["B01:B-LEFT"].diagnostic_only


def test_physical_supports_and_simultaneous_governing_rows():
    result = check("two_span")
    rows = {item.action.row_id: item for item in result.rows}
    assert {key: item.action for key, item in rows.items()} == {
        item.row_id: item for item in result.request.actions
    }
    u1, u2 = (rows[f"U{number}:B-RIGHT-FACE"] for number in (1, 2))
    assert [(row.action.mu_knm, row.action.vu_kn) for row in (u1, u2)] == [
        (-120, 70),
        (-85, 115),
    ]
    assert u1.flexure_utilization == pytest.approx(
        REFERENCE["actions"]["u1_hogging_utilization"]
    )
    assert u2.shear_utilization == pytest.approx(
        REFERENCE["actions"]["u2_shear_utilization"]
    )
    assert (
        result.governing_rows["hogging"]
        == REFERENCE["actions"]["governing_hogging_row"]
    )
    assert result.governing_rows["shear"] == REFERENCE["actions"]["governing_shear_row"]
    left, right = rows["PATTERN:B-LEFT"], rows["PATTERN:B-RIGHT"]
    assert left.station.x_mm == right.station.x_mm == 4000
    assert left.station.side == "LEFT" and right.station.side == "RIGHT"
    assert right.action.vu_kn - left.action.vu_kn == pytest.approx(
        REFERENCE["actions"]["pattern_internal_reaction_kn"]
    )
    assert rows["PATTERN:B-LEFT-FACE"].station.x_mm == 3850
    assert rows["PATTERN:B-RIGHT-FACE"].station.x_mm == 4150
    for name, available in (
        ("B01:A-FACE", "external_available_mm"),
        ("U1:B-RIGHT-FACE", "internal_available_mm"),
    ):
        anchorage = rows[name].anchorage
        assert anchorage is not None
        for path in anchorage.outputs["checks"]:
            assert path["passed"]
            assert path["required_development_length_mm"] == pytest.approx(
                REFERENCE["section"]["development_mm"]
            )
            assert path["available_for_criterion_mm"] == REFERENCE["section"][available]


def test_asymmetric_steel_is_assigned_to_the_physical_tension_face():
    request = deepcopy(CASES["two_span"]["request"])
    for bar in request["bars"]:
        if bar["face"] == "top":
            bar["diameter_mm"] = 16
    result = beam.check_continuous(beam.load_continuous(request))
    rows = {item.action.row_id: item for item in result.rows}
    hogging, sagging = rows["U1:B-RIGHT-FACE"], rows["B01:L-MID"]
    assert hogging.tension_face == "top" and hogging.section_status == "FAIL"
    assert sagging.tension_face == "bottom" and sagging.section_status == "PASS"


def test_reordering_combinations_and_station_actions_keeps_identity():
    request = deepcopy(CASES["two_span"]["request"])
    result = check("two_span")
    for field in ("actions", "combinations", "stations", "bars"):
        request[field].reverse()
    for item in request["combinations"]:
        item["required_station_ids"].reverse()
    reordered = beam.check_continuous(beam.load_continuous(json.dumps(request)))
    assert reordered.rows == result.rows
    assert reordered.governing_rows == result.governing_rows
    assert (
        reordered.result_envelope.result_identity
        == result.result_envelope.result_identity
    )


def test_missing_sustained_and_stale_analysis_keep_separate_outcomes():
    result = check("missing_sustained")
    assert result.ultimate_status == "PASS"
    assert any(
        issue.path == "combinations.S2.B-RIGHT-FACE"
        for issue in result.result_envelope.issues
    )
    stale = check("stale_analysis")
    assert stale.result_envelope.overall_status.value == "STALE"
    assert all(row.section_status is None for row in stale.rows)
    short = check("short_anchorage")
    assert any(
        issue.code == "BEAM_ANCHORAGE_FAIL" for issue in short.result_envelope.issues
    )
    assert not any(
        issue.code == "BEAM_SECTION_FAIL" for issue in short.result_envelope.issues
    )


def test_unsupported_torsion_and_non_simple_end_are_held():
    request = deepcopy(CASES["two_span"]["request"])
    for action in request["actions"]:
        if action["row_id"] == "B01:A":
            action["mu_knm"] = -40
        if action["row_id"] == "U2:B-RIGHT-FACE":
            action["tu_knm"] = 10
    result = beam.check_continuous(beam.load_continuous(request))
    assert result.ultimate_status == "HOLD"
    assert {"BEAM_ACTION_SCOPE_HELD", "BEAM_OUTER_RESTRAINT_HELD"} <= {
        issue.code for issue in result.result_envelope.issues
    }


@pytest.mark.parametrize("case", ["two_span", "strength_failure", "missing_anchorage"])
def test_installed_style_example_and_result_bound_report(case, tmp_path):
    run = subprocess.run(
        [
            sys.executable,
            str(ROOT / "Python/examples/continuous_beam_check.py"),
            "--reference",
            str(FIXTURE),
            "--case",
            case,
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    payload = json.loads(run.stdout)
    assert payload == json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))
    assert payload["ultimate_status"] == CASES[case]["ultimate_status"]
    report = (tmp_path / "report.html").read_text(encoding="utf-8")
    assert payload["result_envelope"]["result_identity"]["input_hash"] in report
    assert f"<strong>{payload['ultimate_status']}</strong>" in report
    assert "U1:B-RIGHT-FACE" in report and "U2:B-RIGHT-FACE" in report
    assert "Qualified review required" in report
    assert "Anchorage required / available (mm)" in report
    assert {path.name for path in tmp_path.iterdir()} == {"report.html", "result.json"}


def test_profile_discovery_advertises_the_python_route():
    capability = next(
        item for item in get_supported_is456_capabilities() if item.element == "beam"
    )
    profile = next(
        item
        for item in capability.python_profiles
        if item.workflow_id == "is456.beam.continuous-check/v1"
    )
    assert getattr(beam, profile.loader) is beam.load_continuous
    assert getattr(beam, profile.operation) is beam.check_continuous
    assert (
        beam.load_continuous(CASES["two_span"]["request"]).schema_version
        == profile.request_schema
    )
