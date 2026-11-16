"""Freeze the right-span lap with continuous, restrained corner bars."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from hashlib import sha256
from itertools import pairwise
from pathlib import Path

from check_library_030_beam05_span2_lap_reference import fixture as prior_reference
from check_library_030_beam05_t_lap_reference import LOADS_KNM, _span_actions, expected

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "library-030-beam05-span2-lap-reference.json"
TARGET = HERE / "library-030-beam05-span2-lap-restraint-reference.json"
BASE = "9c2b1c3bd48db62caac47e086813070461f09121"


def revised_request(original, name):
    request = deepcopy(original)
    request["identity"]["case_id"] = name
    member = request["member"]
    member.update(width_mm=230, clear_cover_mm=40, aggregate_size_mm=10)
    member["analysis_revision"] += "-RESTRAINT"
    member["current_analysis_revision"] = member["analysis_revision"]
    member["reinforcement_revision"] += f"-RESTRAINT-{name}"
    member["source_reference"] = (
        "BEAM05 equal-span statics with revised restrained web cage"
    )
    positions = {
        "T1-1": (58, 58),
        "T1-2": (172, 58),
        "B1-1": (58, 542),
        "B1-2": (98, 542),
        "B1-3": (172, 542),
        "B2-1": (58, 475),
        "B2-2": (172, 475),
    }
    assert {bar["bar_id"] for bar in member["bars"]} == positions.keys()
    for bar in member["bars"]:
        x, y = positions[bar["bar_id"]]
        bar.update(x_from_left_mm=x, y_from_top_mm=y)
        if bar["bar_id"] == "B1-2":
            bar["diameter_mm"] = 16
    request["lap"].update(
        bar_id="B1-2",
        partner_bar_id="B1-2-partner",
        partner_x_from_left_mm=129 if name == "congested_partner" else 132,
        placement_reference="Separated Ø16 intermediate pieces within a web link with continuous corner bars",
    )
    if name == "short_overlap":
        points = {"LAP-START": 5825, "LAP-MID": 6137.5}
        for station in member["stations"]:
            if station["station_id"] in points:
                station["x_mm"] = points[station["station_id"]]
        for row in member["actions"]:
            if row["station_id"] in points:
                row["mu_knm"], row["vu_kn"] = _span_actions(
                    LOADS_KNM[row["combination_id"]],
                    points[row["station_id"]],
                    right_span=True,
                )
    if name == "missing_lap_action":
        member["actions"] = [
            row for row in member["actions"] if row["row_id"] != "U2:LAP-MID"
        ]
    if name == "stale_analysis":
        member["current_analysis_revision"] += "-EDITED"
    return request


def restraint_evidence(request, result):
    member = request["member"]
    link = request["link_detail"]
    link_dia = member["link_diameter_mm"]
    radius = link["internal_bend_radius_mm"]
    inset = member["clear_cover_mm"] + link_dia + radius
    bars = {bar["bar_id"]: bar for bar in member["bars"]}
    lap = request["lap"]
    partner = {**bars[lap["bar_id"]], "x_from_left_mm": lap["partner_x_from_left_mm"]}
    bars[lap["partner_bar_id"]] = partner
    corners = {
        "T1-1": (inset, inset),
        "T1-2": (member["width_mm"] - inset, inset),
        "B1-1": (inset, member["depth_mm"] - inset),
        "B1-3": (member["width_mm"] - inset, member["depth_mm"] - inset),
    }
    for mark, position in corners.items():
        assert (bars[mark]["x_from_left_mm"], bars[mark]["y_from_top_mm"]) == position
        assert bars[mark]["diameter_mm"] / 2 == radius
    # The four continuous bars sit at the centres of the four nominal inner
    # bend arcs. Each bar radius equals the inner bend radius at those seats.
    # That establishes steel bearing in two directions at each corner.
    compressed = {}
    centre_gaps = {}
    for layout, piece_id in (
        ("upstream", lap["bar_id"]),
        ("downstream", lap["partner_bar_id"]),
    ):
        x = bars[piece_id]["x_from_left_mm"]
        gaps = [x - corners["B1-1"][0], corners["B1-3"][0] - x]
        assert max(gaps) <= 75
        centre_gaps[layout] = gaps
        capacities = result["strength_by_layout"][layout]
        compressed[layout] = {
            face: sorted(
                mark
                for mark, net in capacities[face]["bar_net_forces_n"].items()
                if net > 0
            )
            for face in ("bottom", "top")
        }
        assert compressed[layout]["bottom"] == ["T1-1", "T1-2"]
        assert compressed[layout]["top"] == sorted(["B1-1", "B1-3", piece_id])

    inner_depth = min(
        member["depth_mm"] - bars[mark]["y_from_top_mm"] for mark in ("B2-1", "B2-2")
    )
    assert inner_depth >= 3 * max(
        bars[mark]["diameter_mm"] for mark in ("B2-1", "B2-2")
    )
    pitch_limit = min(member["width_mm"], member["depth_mm"], 16 * 16, 300)
    assert member["link_spacing_mm"] <= pitch_limit
    tie_minimum_dia = max(6, max(bar["diameter_mm"] for bar in bars.values()) / 4)
    assert link_dia >= tie_minimum_dia
    hook_tail = link["hook_vertex_leg_mm"] - radius - link_dia / 2
    assert hook_tail >= 8 * link_dia
    # The doubled bottom row only occurs in the positive-moment overlap.
    assert all(
        envelope["minimum_moment_knm"] > 0
        for envelope in result["lap_interval_by_combination"].values()
    )
    points = sorted(
        result["drawing"]["section_centres"]["overlap"].items(),
        key=lambda item: item[1][0],
    )
    lower = [(bar_id, x) for bar_id, (x, y, layer) in points if y == 542 and layer == 1]
    overlap_clearances = []
    for (first, x1), (second, x2) in pairwise(lower):
        d1, d2 = bars[first]["diameter_mm"], bars[second]["diameter_mm"]
        actual = x2 - x1 - (d1 + d2) / 2
        minimum = max(d1, d2, member["aggregate_size_mm"] + 5)
        assert actual >= minimum
        overlap_clearances.append(
            {"bar_ids": [first, second], "actual_mm": actual, "minimum_mm": minimum}
        )
    return {
        "corner_centres_mm": {
            mark: list(position) for mark, position in corners.items()
        },
        "compression_bar_ids_by_tension_face": compressed,
        "intermediate_centre_gaps_mm": centre_gaps,
        "intermediate_centre_gap_limit_mm": 75,
        "overlap_compression_bar_ids": ["T1-1", "T1-2"],
        "inner_depth_mm": inner_depth,
        "required_inner_depth_mm": 60,
        "tie_pitch_mm": member["link_spacing_mm"],
        "maximum_tie_pitch_mm": pitch_limit,
        "tie_diameter_mm": link_dia,
        "minimum_tie_diameter_mm": tie_minimum_dia,
        "hook_tail_mm": hook_tail,
        "minimum_hook_tail_mm": 8 * link_dia,
        "overlap_clearances": overlap_clearances,
    }


def fixture():
    published = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert prior_reference() == published
    original = published["cases"]["span2_lap"]
    cases = {}
    for name, disposition in (
        ("restrained_span2_lap", ("PASS", [])),
        ("short_overlap", ("FAIL", ["SPLICE.NONCOMPLIANT"])),
        ("congested_partner", ("FAIL", ["SPACING.HORIZONTAL"])),
        ("missing_lap_action", ("HOLD", ["BEAM_ACTION_MISSING"])),
        ("stale_analysis", ("HOLD", ["BEAM_ANALYSIS_STALE"])),
    ):
        request = revised_request(original["request"], name)
        result = expected(request, right_span=True)
        assert (result["status"], result["required_issue_codes"]) == disposition
        result.update(report_available=True, lap_direction="decreasing_x")
        cases[name] = {"request": request, "expected": result}

    accepted = cases["restrained_span2_lap"]
    result = accepted["expected"]
    result["compression_restraint"] = restraint_evidence(accepted["request"], result)
    governor = max(
        result["overlap_rows"],
        key=lambda row: result["overlap_rows"][row]["moment_knm"],
    )
    result["governing_lap_row"] = {
        "row_id": governor,
        **result["overlap_rows"][governor],
    }
    assert math.isclose(
        cases["short_overlap"]["expected"]["required_lap_mm"]
        - cases["short_overlap"]["expected"]["overlap_mm"],
        100,
    )
    cases["original_unrestrained"] = {
        "request": original["request"],
        "expected": {
            "status": "HOLD",
            "required_issue_codes": ["BEAM.LAP_COMPRESSION_RESTRAINT_HELD"],
            "report_available": True,
            "checked_drawing_available": False,
            "bbs_available": False,
            "compression_bar_id": "B1-3-partner",
            "net_compression_force_kn": original["expected"]["strength_by_layout"][
                "downstream"
            ]["top"]["bar_net_forces_n"]["B1-3-partner"]
            / 1000,
        },
    }
    return {
        "fixture_version": "library-030-beam05-span2-lap-restraint-reference/v1",
        "frozen_before_implementation": True,
        "frozen_production_base": BASE,
        "source": [SOURCE.name, "span2_lap", sha256(SOURCE.read_bytes()).hexdigest()],
        "provenance": [
            "IS 456:2000 clauses 26.2.2.4(b), 26.2.5, 26.3.2, 26.5.1.2, 26.5.3.2(b)/(c), 38 and 40 with Table 19.",
            "Amendment No. 1 sets the 6 mm minimum lateral tie diameter. https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf",
        ],
        "method": {
            "scope": "Ordinary layered rectangular web cage, zero torsion, one same-layer separated lap in the positive-moment interval of span two. The longitudinal load and path coordinates come from the frozen second-span lap.",
            "compression_restraint": "Check the four continuous Ø20 seats at the nominal 90-degree tie bends and the single intermediate bar between both seats in each compressed outer row. In the overlap the four-bar bottom row is in tension and the two top corners provide the compression layout. Check the physical layout, both signed transfer models and tie pitch and anchorage.",
            "outputs": "Use the restrained case's paths in the checked drawing and BBS. Withhold checked exports where compression restraint is missing, while retaining the signed calculations and diagnostic report.",
        },
        "absolute_tolerances": published["absolute_tolerances"],
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
        print(f"PASS independent BEAM05 restraint {name}: {case['expected']['status']}")


if __name__ == "__main__":
    main()
