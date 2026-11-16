"""Freeze the separated outer-bottom lap in the second clear span."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

from check_library_030_beam05_t_lap_reference import (
    LOADS_KNM,
    _span_actions,
    expected,
    fixture as first_span_reference,
)

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "library-030-beam05-t-lap-reference.json"
TARGET = HERE / "library-030-beam05-span2-lap-reference.json"
BASE = "9d4b97c705a2aedbe13ec6b3a5f6ced49b72ebc5"
MEMBER_END_MM = 8000
REFLECTED_STATIONS = {
    "LAP-START": "LAP-END",
    "LAP-MID": "LAP-MID",
    "LAP-END": "LAP-START",
}


def right_span_request(name, original, left_positions):
    request = deepcopy(original)
    member = request["member"]
    request["identity"]["case_id"] = name
    member["reinforcement_revision"] += f"-SPAN2-{name}"
    member["source_reference"] = (
        "BEAM05 two-span three-moment statics, longitudinal mirror of the layered lap"
    )
    positions = {
        station_id: MEMBER_END_MM - left_positions[reflected]
        for station_id, reflected in REFLECTED_STATIONS.items()
    }
    for station in member["stations"]:
        if station["station_id"] in positions:
            station["x_mm"] = positions[station["station_id"]]
    for row in member["actions"]:
        if row["station_id"] in positions:
            row["mu_knm"], row["vu_kn"] = _span_actions(
                LOADS_KNM[row["combination_id"]],
                positions[row["station_id"]],
                right_span=True,
            )
    if name == "congested_partner":
        request["lap"]["partner_x_from_left_mm"] = 215
    if name == "missing_lap_action":
        member["actions"] = [
            row for row in member["actions"] if row["row_id"] != "U2:LAP-MID"
        ]
    if name == "stale_analysis":
        member["current_analysis_revision"] += "-EDITED"
    return request


def fixture():
    prior = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert first_span_reference() == prior
    control = deepcopy(prior["cases"]["rectangular_control"])
    control["expected"]["report_available"] = True
    request = control["request"]
    cases = {"first_span_control": control}
    dispositions = {
        "span2_lap": ("PASS", []),
        "short_overlap": ("FAIL", ["SPLICE.NONCOMPLIANT"]),
        "congested_partner": ("FAIL", ["SPACING.HORIZONTAL"]),
        "missing_lap_action": ("HOLD", ["BEAM_ACTION_MISSING"]),
        "stale_analysis": ("HOLD", ["BEAM_ANALYSIS_STALE"]),
    }
    for name, (status, issues) in dispositions.items():
        key = "short_overlap" if name == "short_overlap" else "rectangular_control"
        left_positions = {
            row["station_id"]: row["x_mm"]
            for row in prior["cases"][key]["request"]["member"]["stations"]
        }
        mirrored = right_span_request(name, request, left_positions)
        result = expected(mirrored, right_span=True)
        assert (result["status"], result["required_issue_codes"]) == (status, issues)
        assert 4500 < next(
            row["x_mm"]
            for row in mirrored["member"]["stations"]
            if row["station_id"] == "LAP-START"
        )
        result.update(report_available=True, lap_direction="decreasing_x")
        cases[name] = {"request": mirrored, "expected": result}

    result = cases["span2_lap"]["expected"]
    original = control["expected"]
    assert result["bbs"] == original["bbs"]
    prior_paths = original["drawing"]["bar_extents_mm"]
    assert result["drawing"]["bar_extents_mm"] == {
        bar_id: [MEMBER_END_MM - end, MEMBER_END_MM - start]
        for bar_id, (start, end) in prior_paths.items()
    }
    for name, reflected in (
        ("before", "after"),
        ("overlap", "overlap"),
        ("after", "before"),
    ):
        assert (
            result["drawing"]["section_centres"][name]
            == original["drawing"]["section_centres"][reflected]
        )
    lap_rows = result["overlap_rows"]
    governor = max(lap_rows, key=lambda row_id: lap_rows[row_id]["moment_knm"])
    result["governing_lap_row"] = {"row_id": governor, **lap_rows[governor]}
    combination = governor.partition(":")[0]
    assert lap_rows[governor]["moment_knm"] == (
        result["lap_interval_by_combination"][combination]["maximum_moment_knm"]
    )
    return {
        "fixture_version": "library-030-beam05-span2-lap-reference/v1",
        "frozen_before_implementation": True,
        "frozen_production_base": BASE,
        "catalogue_window_mm": [4500, 7500],
        "source": [
            SOURCE.name,
            "rectangular_control",
            sha256(SOURCE.read_bytes()).hexdigest(),
        ],
        "method": {
            "scope": "Reflect the independently checked rectangular lap about the centre support, along the longitudinal axis only. Retain the multilayer cross-section, transverse partner offset, uniform web links and zero torsion.",
            "actions": "Use the declared U1 and U2 equal-span UDLs. Recompute signed rows from three-moment statics. In span two the positive moment interval is 5000 to 8000 mm, with the stationary maximum at 6500 mm.",
            "transfer": "Order the three supplied overlap stations by increasing coordinate. Transfer toward decreasing x. Upstream denotes the outer-right original piece and downstream the partner reaching the left support. Test each layout in the overlap without double credit.",
            "outputs": "Use the checked paths in report, elevation, sections and BBS. Withhold the checked drawing and BBS on all FAIL and HOLD controls.",
        },
        "absolute_tolerances": prior["absolute_tolerances"],
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    data = fixture()
    if args.freeze:
        TARGET.write_text(
            json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
    else:
        assert json.loads(TARGET.read_text(encoding="utf-8")) == data
    for name, case in data["cases"].items():
        print(
            f"PASS independent BEAM05 span 2 lap {name}: {case['expected']['status']}"
        )


if __name__ == "__main__":
    main()
