"""Independent straight contact splice geometry, section and quantity reference."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from itertools import combinations
from pathlib import Path

from check_library_029_col02_reference import axis_reference

BASE = Path(__file__).with_name("library-029-col07-column-member.json")
FIXTURE = Path(__file__).with_name("library-029-col07-contact-splice.json")


def cases():
    base = json.loads(BASE.read_text())["cases"]["continuous"]["request"]
    base["tie_zones"][1]["pitch_mm"] = 84
    base["transverse_cut_schedule"]["cut_lengths_mm"] = {"H": 1220}
    base["actions"][1].update(mx_knm=10, my_knm=5, vy_kn=60)
    base["laps"] = [
        {
            "lap_id": "S1",
            "bar_ids": ["M_LEFT", "M_RIGHT"],
            "start_mm": 1150,
            "end_mm": 1890,
            "stress_basis": "compression",
            "contact_assembly": {
                "partner_y_mm": 220,
                "lap_link_id": "LX",
                "hook_tail_mm": 64,
                "fabrication_reference": "Specimen quarter-bend and straight-tail link schedule",
                "compression_reference": "Specimen A1 compression verification throughout the splice window",
            },
        }
    ]
    names = (
        "contact_splice",
        "missing_assembly",
        "coincident_partners",
        "short_hook",
        "crowded_hook_tails",
        "congested_longitudinal",
        "missing_end_restraint",
        "compression_basis",
        "short_contact_lap",
        "stale_revision",
    )
    inputs = {name: deepcopy(base) for name in names}
    for name, request in inputs.items():
        request["identity"]["case_id"] = name
    inputs["missing_assembly"]["laps"][0].pop("contact_assembly")
    inputs["missing_assembly"]["transverse_cut_schedule"]["cut_lengths_mm"].update(
        XT=365, YT=465
    )
    inputs["coincident_partners"]["laps"][0]["contact_assembly"]["partner_y_mm"] = 200
    inputs["short_hook"]["laps"][0]["contact_assembly"]["hook_tail_mm"] = 63
    inputs["crowded_hook_tails"]["laps"][0]["contact_assembly"]["hook_tail_mm"] = 90
    crowded = inputs["congested_longitudinal"]
    crowded["geometry"]["D_mm"] = 300
    crowded["reinforcement"]["aggregate_size_mm"] = 50
    crowded["laps"][0]["contact_assembly"]["partner_y_mm"] = 170
    for row in crowded["actions"]:
        row.update(mx_knm=10, my_knm=5, vy_kn=60, vx_kn=0)
    inputs["missing_end_restraint"]["tie_zones"][1]["pitch_mm"] = 140
    inputs["compression_basis"]["actions"][1]["mx_knm"] = 45
    inputs["short_contact_lap"]["laps"][0]["end_mm"] = 1850
    inputs["stale_revision"]["basis"]["current_analysis_revision"] = "A2"
    six = deepcopy(base)
    six["identity"]["case_id"] = "six_bar_side_splice"
    six["reinforcement"]["layout"] = "six_bar_omit_y_face_midpoints"
    six["reinforcement"]["cross_ties"] = [
        tie for tie in six["reinforcement"]["cross_ties"] if tie["tie_id"] == "XT"
    ]
    inputs["six_bar_side_splice"] = six
    short_six = deepcopy(six)
    short_six["identity"]["case_id"] = "six_bar_short_lap"
    short_six["laps"][0]["end_mm"] = 1850
    inputs["six_bar_short_lap"] = short_six
    return inputs


def _axis_rows(request, bars, shifted_bars):
    geometry, materials = request["geometry"], request["materials"]
    b, d = geometry["b_mm"], geometry["D_mm"]
    start, end = (request["laps"][0][field] for field in ("start_mm", "end_mm"))
    rows = []
    for action in request["actions"]:
        position = action["check_station_mm"]
        layouts = (
            {"lower": bars}
            if position < start
            else (
                {"upper": shifted_bars}
                if position > end
                else {"lower": bars, "upper": shifted_bars}
            )
        )
        inputs = {
            **geometry,
            **materials,
            "pu_kn": action["pu_kn"],
            "longitudinal_bar_diameter_mm": 20,
        }
        capacities = {}
        for label, layout in layouts.items():
            values = {}
            for axis, moment, index, depth in (
                ("x", action["mx_knm"], 1, d),
                ("y", action["my_knm"], 0, b),
            ):
                reflected = {
                    mark: tuple(
                        depth - point[i] if i == index and moment < 0 else point[i]
                        for i in range(2)
                    )
                    for mark, point in layout.items()
                }
                values[axis] = axis_reference(inputs, reflected, axis)["capacity_knm"]
            capacities[label] = values
        rows.append({"station_mm": position, "capacities_knm": capacities})
    return rows


def expected(name, request):
    dispositions = {
        "contact_splice": ("PASS", None),
        "missing_assembly": ("HOLD", "COLUMN.LAP_ASSEMBLY_REQUIRED"),
        "coincident_partners": ("FAIL", "COLUMN.LAP_CONTACT_GEOMETRY"),
        "short_hook": ("FAIL", "COLUMN.LAP_LINK_FIT"),
        "crowded_hook_tails": ("FAIL", "COLUMN.LAP_LINK_FIT"),
        "congested_longitudinal": ("FAIL", "COLUMN.LAP_CLEAR_SPACING"),
        "missing_end_restraint": ("FAIL", "COLUMN.LAP_END_RESTRAINT"),
        "compression_basis": ("HOLD", "COLUMN.LAP_COMPRESSION_BASIS"),
        "short_contact_lap": ("FAIL", "COLUMN.LAP_LENGTH"),
        "stale_revision": ("HOLD", "COLUMN.STALE_ANALYSIS"),
        "six_bar_side_splice": ("PASS", None),
        "six_bar_short_lap": ("FAIL", "COLUMN.LAP_LENGTH"),
    }
    status, issue = dispositions[name]
    result = {"status": status, "issue": issue, "bbs_available": status == "PASS"}
    if status != "PASS":
        return result

    b, d, setback, dia, dt, inside = 300, 400, 60, 20, 8, 12
    r = inside + dt / 2
    radius = dia / 2
    start, end = 1150, 1890
    bars = {
        "C1": (60, 60),
        "C2": (240, 60),
        "C3": (240, 340),
        "C4": (60, 340),
        "M_TOP": (150, 60),
        "M_BOTTOM": (150, 340),
        "M_LEFT": (60, 200),
        "M_RIGHT": (240, 200),
    }
    six = request["reinforcement"]["layout"] == "six_bar_omit_y_face_midpoints"
    if six:
        for mark in ("M_TOP", "M_BOTTOM"):
            bars.pop(mark)
    spliced = ("M_LEFT", "M_RIGHT")
    mates = {mark: (bars[mark][0], bars[mark][1] + dia) for mark in spliced}
    active = {**bars, **{mark + "-U": p for mark, p in mates.items()}}
    unrelated_gap = min(
        math.dist(p, q) - dia
        for (left, p), (right, q) in combinations(active.items(), 2)
        if right != left + "-U"
    )
    assert unrelated_gap == (100 if six else 70)
    # All hooks are quadrant arcs with 8d straight tails. For the overlap
    # link the exposed bends route around the outside of the two tangent circles.
    # The close surfaces are the two hook seats and the two tangent side legs.
    # Other longitudinal circles are at least 70 mm clear before adding the link.
    assert setback - r - dt / 2 == 40
    assert b - 2 * setback - 2 * (8 * dt) - dt == 44
    assert r - radius - dt / 2 == 2
    assert 48 * dt >= d - 2 * setback
    # Cl. 26.2.1.2 contact-pair allowance retained for the full lap as a
    # conservative profile rule. The straight compression minimum is 24d.
    required = max(1.1 * dia * 0.87 * 415 / (4 * 1.4 * 1.6 * 1.25), 24 * dia)
    assert end - start > required
    hoops = sorted(
        {
            s
            for z in request["tie_zones"]
            for s in range(z["start_mm"], z["end_mm"] + 1, z["pitch_mm"])
        }
    )
    x_stations = [s + 12 for s in hoops]
    lap_stations = [s for s in x_stations if start < s < end]
    end_support = [
        start - max(s for s in x_stations if s < start),
        min(lap_stations) - start,
        end - max(lap_stations),
        min(s for s in x_stations if s > end) - end,
    ]
    assert max(end_support) <= 4 * dia
    cuts = {
        **{mark: [1, 4700, dia] for mark in bars if mark not in spliced},
        **{mark + "-L": [1, 850 + end, dia] for mark in spliced},
        **{mark + "-U": [1, 3850 - start, dia] for mark in spliced},
        "H": [len(hoops), 1220, dt],
        "XT": [len(hoops) - len(lap_stations), 180 + 2 * math.pi * r + 16 * dt, dt],
        "LX": [len(lap_stations), 180 + 2 * math.pi * r + 16 * dt + 2 * dia, dt],
    }
    if not six:
        cuts["YT"] = [len(hoops), 280 + 2 * math.pi * r + 16 * dt, dt]
    result.update(
        contact_lap_required_mm=required,
        overlap_mm=end - start,
        lap_stations_mm=lap_stations,
        end_support_distances_mm=end_support,
        minimum_unrelated_bar_clear_mm=unrelated_gap,
        minimum_link_clear_mm=r - radius - dt / 2,
        lower_bar_centres_mm=bars,
        upper_bar_centres_mm={**bars, **mates},
        steel_ratio=len(active) * math.pi * dia**2 / 4 / (b * d),
        cuts=cuts,
        bbs_quantity=sum(quantity for quantity, _, _ in cuts.values()),
        bbs_total_mm=sum(quantity * cut for quantity, cut, _ in cuts.values()),
        bbs_mass_kg=sum(
            quantity * cut * math.pi * bar**2 / 4 * 7850e-9
            for quantity, cut, bar in cuts.values()
        ),
        section_rows=_axis_rows(request, bars, {**bars, **mates}),
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--derive", action="store_true")
    args = parser.parse_args()
    calculated = {
        name: {"request": request, "expected": expected(name, request)}
        for name, request in cases().items()
    }
    record = {
        "schema_version": "library-029-col07-contact-splice-reference/v1",
        "frozen_production_base": "35c79a1d530d9888417d6a719e73e7091752f98e",
        "sources": [
            "IS 456:2000 Cl. 26.1.1, 26.2.1.2, 26.2.2.4(b), 26.2.5.1, 26.3.2, 26.4 and 26.5.3.",
            "https://www.cracindia.in/admin/uploads/IS-456.pdf",
            "BIS SP 34:1987 Fig. 4.4 and section 4.6. https://law.resource.org/pub/in/bis/S03/is.sp.34.1987.pdf",
        ],
        "method": "Contact bar circles and quadrant geometry checked analytically. Two 90 degree curves and 8d tail at each open-link end. Station grid verified against both ends of overlap. Independently integrated fixed-load sections before and after transfer. Piece lengths from straight elevations and true centreline arc lengths. Hoop cut remains supplied by the fixture.",
        "cases": calculated,
    }
    if args.derive:
        FIXTURE.write_text(json.dumps(record, indent=2) + "\n")
    else:
        frozen = json.loads(FIXTURE.read_text())
        assert frozen == json.loads(json.dumps(record))
        for name in calculated:
            print(f"PASS independent COL07 splice {name}")


if __name__ == "__main__":
    main()
