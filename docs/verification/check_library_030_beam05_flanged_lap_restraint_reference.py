"""Independent reference for a separated Ø20 lap with two closed link grids."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from hashlib import sha256
from itertools import pairwise
from pathlib import Path

from check_library_030_beam05_l_lap_reference import fixture as l_reference
from check_library_030_beam05_t_lap_reference import expected

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "library-030-beam05-l-lap-reference.json"
TARGET = HERE / "library-030-beam05-flanged-lap-restraint-reference.json"
BASE = "72836c6a2c7c9e59a4c632b3498abbbf0d0caa5f"


def revised_request(original, name):
    request = deepcopy(original)
    request["identity"]["case_id"] = name
    member = request["member"]
    member["clear_cover_mm"] = 35
    member["reinforcement_revision"] += "-TWO-LINKS"
    member["source_reference"] += "; two independently checked web link grids"
    position_by_id = {
        "T1-1": (55, 55),
        "T1-2": (245, 55),
        "B1-1": (55, 545),
        "B1-2": (105, 545),
        "B1-3": (245, 545),
        "B2-1": (55, 475),
        "B2-2": (245, 475),
    }
    assert {bar["bar_id"] for bar in member["bars"]} == position_by_id.keys()
    for bar in member["bars"]:
        x, y = position_by_id[bar["bar_id"]]
        bar.update(x_from_left_mm=x, y_from_top_mm=y)
    for index, x in enumerate((105, 195), start=3):
        member["bars"].append(
            dict(member["bars"][0], bar_id=f"T1-{index}", x_from_left_mm=x)
        )
    request["lap"].update(
        bar_id="B1-2",
        partner_bar_id="B1-2-partner",
        partner_x_from_left_mm=145 if name == "congested_partner" else 195,
        placement_reference="Separated Ø20 pieces seated in the two bottom bends of a supplementary closed link",
    )
    request["link_detail"]["internal_bend_radius_mm"] = 15
    request["link_detail"]["restraint_link"] = {
        "left_centre_x_mm": 89,
        "right_centre_x_mm": 211,
        "station_offset_mm": 50,
    }
    return request


def restrained_takeoff(request, result):
    member, link = request["member"], request["link_detail"]
    drawing, bbs = result["drawing"], result["bbs"]
    inner = link["restraint_link"]
    link_diameter = member["link_diameter_mm"]
    inner_radius = link["internal_bend_radius_mm"]
    centreline_radius = inner_radius + link_diameter / 2
    shift = link["hook_plane_offset_mm"]
    offset = inner["station_offset_mm"]
    pitch = member["link_spacing_mm"]
    x1, y1, x2, y2 = drawing["web_link_centreline_bounds_mm"]
    width = inner["right_centre_x_mm"] - inner["left_centre_x_mm"]
    assert width > link["hook_vertex_leg_mm"]
    assert x1 < inner["left_centre_x_mm"] < inner["right_centre_x_mm"] < x2
    assert inner_radius == 15
    assert link["hook_vertex_leg_mm"] - centreline_radius >= 8 * link_diameter
    assert shift >= link_diameter
    # Both sets occupy closed station intervals 10 mm long. The two
    # nearest planes in adjacent sets are 40 mm apart centre to centre.
    gap = min(offset, pitch - offset) - shift - link_diameter
    assert gap == 32 >= member["aggregate_size_mm"] + 5
    grid = [station + offset for station in drawing["link_stations_mm"]]
    assert grid[0] <= member["supports"][0]["centre_mm"] + 500
    assert grid[-1] >= member["supports"][-1]["centre_mm"] - 500
    assert grid[-1] + shift + link_diameter / 2 <= 8500 - member["clear_cover_mm"]
    link_cut = (
        2 * link["hook_vertex_leg_mm"]
        + width
        + 2 * (y2 - y1)
        + math.hypot(width, shift)
        + 5 * centreline_radius * (math.pi / 2 - 2)
    )
    link_mark = f"{member['member_id']}-L{link_diameter:g}-restraint"
    drawing.update(
        restraint_link_centreline_bounds_mm=[
            inner["left_centre_x_mm"],
            y1,
            inner["right_centre_x_mm"],
            y2,
        ],
        restraint_link_stations_mm=grid,
        restraint_link_mark=link_mark,
    )
    bbs["rows_qty_cut_mm_diameter_mm"][link_mark] = [len(grid), link_cut, link_diameter]
    bbs["total_quantity"] += len(grid)
    bbs["total_length_mm"] += len(grid) * link_cut
    bbs["total_mass_kg"] += (
        7850e-9 * len(grid) * link_cut * math.pi * link_diameter**2 / 4
    )

    seat_ids = {
        "outer": {"T1-1", "T1-2", "B1-1", "B1-3"},
        "restraint": {"T1-3", "T1-4", "B1-2", "B1-2-partner"},
    }
    centres = drawing["section_centres"]["overlap"]
    bar_radius = 10
    arc_clearance = inner_radius - bar_radius - math.hypot(3, 3)
    assert 0 < arc_clearance < 1
    for (left, top, right, bottom), mark_ids in zip(
        (
            drawing["web_link_centreline_bounds_mm"],
            drawing["restraint_link_centreline_bounds_mm"],
        ),
        seat_ids.values(),
        strict=True,
    ):
        # Move the bar 3 mm toward each straight leg from the arc centre.
        # Its surface remains inside the bend with positive nominal clearance.
        seat_inset = centreline_radius - 3
        seats = {
            (x, y)
            for x in (left + seat_inset, right - seat_inset)
            for y in (top + seat_inset, bottom - seat_inset)
        }
        assert {tuple(centres[mark][:2]) for mark in mark_ids} == seats
    # External longitudinal bars lie outside the narrow link by at
    # least 34 mm centre-to-centre. Each seated Ø20 has a 10 mm radius.
    transverse_distance = inner["left_centre_x_mm"] - centres["B1-1"][0]
    assert transverse_distance == centres["B1-3"][0] - inner["right_centre_x_mm"]
    assert transverse_distance - link_diameter / 2 - bar_radius == 20
    assert all(bar["diameter_mm"] == 2 * bar_radius for bar in member["bars"])
    bottom = sorted(item[0] for item in centres.values() if item[1:] == [545, 1])
    clearances = [right - left - 2 * bar_radius for left, right in pairwise(bottom)]
    assert min(clearances) >= member["aggregate_size_mm"] + 5

    bottom_inner_depth = min(
        member["depth_mm"] - bar["y_from_top_mm"]
        for bar in member["bars"]
        if bar["layer"] == 2
    )
    assert bottom_inner_depth >= 3 * 2 * bar_radius
    pitch_limit = min(member["width_mm"], member["depth_mm"], 16 * 20, 300)
    assert pitch <= pitch_limit and link_diameter >= max(20 / 4, 6)
    assert all(
        row["minimum_moment_knm"] > 0
        for row in result["lap_interval_by_combination"].values()
    )
    compressed_by_layout = {}
    for layout, capacities in result["strength_by_layout"].items():
        piece = "B1-2" if layout == "upstream" else "B1-2-partner"
        compressed_by_layout[layout] = {
            face: sorted(
                mark
                for mark, net_force in capacities[face]["bar_net_forces_n"].items()
                if net_force > 0
            )
            for face in ("bottom", "top")
        }
        assert compressed_by_layout[layout]["bottom"] == sorted(
            ["T1-1", "T1-2", "T1-3", "T1-4"]
        )
        assert compressed_by_layout[layout]["top"] == sorted(["B1-1", piece, "B1-3"])
    return {
        "corner_bar_ids_by_grid": {key: sorted(ids) for key, ids in seat_ids.items()},
        "compression_bar_ids_by_tension_face": compressed_by_layout,
        "minimum_between_link_grids_mm": gap,
        "bar_to_inside_bend_clearance_mm": arc_clearance,
        "bar_to_straight_leg_clearance_mm": seat_inset - link_diameter / 2 - bar_radius,
        "overlap_clearances_mm": clearances,
        "inner_depth_mm": bottom_inner_depth,
        "maximum_tie_pitch_mm": pitch_limit,
        "minimum_tie_diameter_mm": 6,
    }


def fixture():
    stored = json.loads(SOURCE.read_text())
    assert stored == l_reference()
    cases = {}
    for name, entry in stored["cases"].items():
        request = revised_request(entry["request"], name)
        target = expected(request)
        assert target["status"] == entry["expected"]["status"]
        assert (
            target["required_issue_codes"] == entry["expected"]["required_issue_codes"]
        )
        if target["status"] == "PASS":
            target["compression_restraint"] = restrained_takeoff(request, target)
        target["report_available"] = True
        cases[name] = {"request": request, "expected": target}
    for name in ("l_lap", "t_control"):
        unrevised = deepcopy(stored["cases"][name])
        unrevised["expected"].update(
            status="HOLD",
            checked_drawing_available=False,
            bbs_available=False,
            required_issue_codes=["BEAM.LAP_COMPRESSION_RESTRAINT_HELD"],
        )
        cases[f"original_{name}"] = unrevised
    return {
        "fixture_version": "library-030-beam05-flanged-lap-restraint-reference/v1",
        "frozen_before_implementation": True,
        "frozen_production_base": BASE,
        "bound_sources": {SOURCE.name: sha256(SOURCE.read_bytes()).hexdigest()},
        "sources": [
            "IS 456:2000 clauses 26.2.2.4(b), 26.3.2, 26.5.1.2 and 26.5.3.2 including Amendment No. 1. https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf",
            "Frozen L and T specimens and two-span three-moment actions, with no torsion.",
        ],
        "method": {
            "scope": "Nominal fixed cage with one Ø20 separated bottom lap and two interleaved, two-hook Ø8 closed links. Credit only the exterior link for strength.",
            "restraint": "Each outer compression bar sits at a closed-link bend. The two grids are physically disjoint and each meets the restraint pitch. The pair coexists only in sagging. Verify both transfer layouts and the actual bar and tie spacings.",
            "outputs": "Independent section equilibrium, signed action checks and centreline takeoff. Both link marks and the nominal support for each bar appear in the checked exports.",
        },
        "absolute_tolerances": stored["absolute_tolerances"],
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    data = fixture()
    if parser.parse_args().freeze:
        TARGET.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    else:
        assert json.loads(TARGET.read_text()) == data
    for name, entry in data["cases"].items():
        print(
            f"PASS independent BEAM05 flanged restraint {name}: {entry['expected']['status']}"
        )


if __name__ == "__main__":
    main()
