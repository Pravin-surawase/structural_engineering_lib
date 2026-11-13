"""Independent checks for the COL07 C1/C2 straight contact corner laps."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from itertools import combinations
from pathlib import Path

from check_library_029_col07_splice_reference import _axis_rows

BASE = Path(__file__).with_name("library-029-col07-column-member.json")
FIXTURE = Path(__file__).with_name("library-029-col07-corner-splice.json")


def cases():
    original = json.loads(BASE.read_text())["cases"]["lap_numeric_pass"]["request"]
    reference = deepcopy(original)
    reference["end_detail"]["end_hoop_offset_mm"] = 70
    reference["tie_zones"] = [
        {"zone_id": "LOWER", "start_mm": 70, "end_mm": 670, "pitch_mm": 100},
        {"zone_id": "FIELD", "start_mm": 670, "end_mm": 2330, "pitch_mm": 83},
        {"zone_id": "UPPER", "start_mm": 2330, "end_mm": 2930, "pitch_mm": 100},
    ]
    reference["actions"][1].update(mx_knm=10, my_knm=5)
    reference["actions"].append(
        {
            "combination_id": "U3",
            "check_station_mm": 2850,
            "pu_kn": 500,
            "mx_knm": -35,
            "my_knm": -10,
            "vx_kn": 0,
            "vy_kn": 100,
        }
    )
    reference["laps"][0].update(
        end_mm=1890,
        contact_assembly={
            "partner_y_mm": 80,
            "lap_link_id": "CL",
            "hook_tail_mm": 64,
            "corner_link_id": "CX",
            "corner_link_offset_mm": 36,
            "fabrication_reference": "Specimen mirrored C1/C2 return links and hoop closure schedule",
            "compression_reference": "Specimen verified compression throughout the C1/C2 overlap",
        },
    )
    reference["transverse_cut_schedule"]["cut_lengths_mm"] = {"H": 1220}
    names = (
        "corner_splice",
        "missing_corner_link",
        "coincident_partners",
        "link_level_clash",
        "end_cover",
        "missing_end_restraint",
        "short_contact_lap",
        "compression_basis",
        "congested_longitudinal",
        "stale_revision",
    )
    requests = {name: deepcopy(reference) for name in names}
    requests["original_numeric_only"] = original
    for name, request in requests.items():
        request["identity"]["case_id"] = name
    for field in ("corner_link_id", "corner_link_offset_mm"):
        requests["missing_corner_link"]["laps"][0]["contact_assembly"].pop(field)
    requests["coincident_partners"]["laps"][0]["contact_assembly"]["partner_y_mm"] = 60
    requests["link_level_clash"]["laps"][0]["contact_assembly"][
        "corner_link_offset_mm"
    ] = 24
    requests["end_cover"]["laps"][0]["contact_assembly"]["corner_link_offset_mm"] = 42
    requests["missing_end_restraint"]["tie_zones"][1]["pitch_mm"] = 166
    requests["missing_end_restraint"]["approved_lap_zone"]["max_tie_pitch_mm"] = 175
    requests["short_contact_lap"]["laps"][0]["end_mm"] = 1850
    requests["compression_basis"]["actions"][1].update(mx_knm=50, my_knm=35)
    congested = requests["congested_longitudinal"]
    congested["geometry"]["D_mm"] = 300
    congested["reinforcement"]["aggregate_size_mm"] = 50
    for row in congested["actions"]:
        row.update(mx_knm=10, my_knm=5, vx_kn=0, vy_kn=60)
    requests["stale_revision"]["basis"]["current_analysis_revision"] = "A2"
    return requests


def expected(name, request):
    outcomes = {
        "corner_splice": ("PASS", None),
        "missing_corner_link": ("HOLD", "COLUMN.LAP_CORNER_LINK_REQUIRED"),
        "coincident_partners": ("FAIL", "COLUMN.LAP_CONTACT_GEOMETRY"),
        "link_level_clash": ("FAIL", "COLUMN.LAP_CORNER_LINK_LEVELS"),
        "end_cover": ("FAIL", "COLUMN.LAP_CORNER_END_COVER"),
        "missing_end_restraint": ("FAIL", "COLUMN.LAP_END_RESTRAINT"),
        "short_contact_lap": ("FAIL", "COLUMN.LAP_LENGTH"),
        "compression_basis": ("HOLD", "COLUMN.LAP_COMPRESSION_BASIS"),
        "congested_longitudinal": ("FAIL", "COLUMN.LAP_CLEAR_SPACING"),
        "stale_revision": ("HOLD", "COLUMN.STALE_ANALYSIS"),
        "original_numeric_only": ("HOLD", "COLUMN.LAP_ASSEMBLY_REQUIRED"),
    }
    status, issue = outcomes[name]
    result = {"status": status, "issue": issue, "bbs_available": status == "PASS"}
    if name != "corner_splice":
        return result

    dia, dt, r, b, depth = 20, 8, 16, 300, 400
    start, end = 1150, 1890
    base = {
        "C1": (60, 60),
        "C2": (240, 60),
        "C3": (240, 340),
        "C4": (60, 340),
        "M_TOP": (150, 60),
        "M_BOTTOM": (150, 340),
        "M_LEFT": (60, 200),
        "M_RIGHT": (240, 200),
    }
    mates = {"C1": (60, 80), "C2": (240, 80)}
    overlap = {**base, "C1-U": mates["C1"], "C2-U": mates["C2"]}
    unrelated_gap = min(
        math.dist(p, q) - dia
        for (a, p), (bmark, q) in combinations(overlap.items(), 2)
        if bmark != a + "-U"
    )
    assert unrelated_gap == 70
    # Independent extreme and distance checks. In the lap the link spine is
    # at y=44. Above it is reflected to y=96 to clear M_TOP. Its nearest
    # tail tip to M_TOP is at (124,64), so the upper tails also clear M_TOP.
    assert 60 - r - dt / 2 == 40
    assert 80 + r - 60 - (dia + dt) / 2 == 22
    assert math.dist((124, 64), base["M_TOP"]) > (dia + dt) / 2
    assert r - (dia + dt) / 2 == 2
    assert 48 * dt >= max(b, depth) - 120
    hoops = sorted(
        {
            station
            for zone in request["tie_zones"]
            for station in range(zone["start_mm"], zone["end_mm"] + 1, zone["pitch_mm"])
        }
    )
    corner = [station + 36 for station in hoops]
    lap_levels = [s for s in corner if start < s < end]
    support = [
        start - max(s for s in corner if s < start),
        lap_levels[0] - start,
        end - lap_levels[-1],
        min(s for s in corner if s > end) - end,
    ]
    all_levels = sorted(s + offset for s in hoops for offset in (0, 12, 24, 36))
    minimum_gap = (
        min(next_level - level for level, next_level in zip(all_levels, all_levels[1:]))
        - dt
    )
    cover = 3000 - all_levels[-1] - dt / 2
    assert minimum_gap == 4 and cover == 30 and max(support) <= 80
    return_cut = 180 + 2 * math.pi * r + 16 * dt
    cuts = {
        **{mark: [1, 4700, dia] for mark in base if mark not in mates},
        **{mark + "-L": [1, 850 + end, dia] for mark in mates},
        **{mark + "-U": [1, 3850 - start, dia] for mark in mates},
        "H": [len(hoops), 1220, dt],
        "XT": [len(hoops), return_cut, dt],
        "YT": [len(hoops), return_cut + 100, dt],
        "CX": [len(hoops) - len(lap_levels), return_cut, dt],
        "CL": [len(lap_levels), return_cut + 2 * dia, dt],
    }
    result.update(
        required_lap_mm=1.1 * dia * 0.87 * 415 / (4 * 1.4 * 1.6 * 1.25),
        overlap_mm=end - start,
        lap_stations_mm=lap_levels,
        end_support_distances_mm=support,
        minimum_unrelated_bar_clear_mm=unrelated_gap,
        minimum_link_clear_mm=2,
        minimum_level_clear_mm=minimum_gap,
        minimum_end_cover_mm=cover,
        upper_centres_mm={**base, **mates},
        shear_depths_mm=[340, 320, 240, 320],
        section_rows=_axis_rows(request, base, {**base, **mates}),
        cuts=cuts,
        bbs_quantity=sum(q for q, _, _ in cuts.values()),
        bbs_total_mm=sum(q * cut for q, cut, _ in cuts.values()),
        bbs_mass_kg=sum(
            q * cut * math.pi * bar**2 / 4 * 7850e-9 for q, cut, bar in cuts.values()
        ),
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--derive", action="store_true")
    args = parser.parse_args()
    record = {
        "schema_version": "library-029-col07-corner-splice-reference/v1",
        "frozen_production_base": "e07528f2baf757079d3e5e458541b1fad634f571",
        "sources": [
            "IS 456:2000 Cl. 26.1.1, 26.2.1.2, 26.2.2.4(b), 26.2.5.1, 26.3.2, 26.4 and 26.5.3.",
            "https://www.cracindia.in/admin/uploads/IS-456.pdf",
        ],
        "method": "Analytic bar circles, quadrant extrema, mirrored upper returns, independent fixed-compression sections and hand-counted station grids. The reduced y-plane effective depth uses the innermost credited face corner after transfer. Centreline cut lengths are from actual segment and arc lengths; the hoop cut remains supplied.",
        "cases": {
            name: {"request": request, "expected": expected(name, request)}
            for name, request in cases().items()
        },
    }
    if args.derive:
        FIXTURE.write_text(json.dumps(record, indent=2) + "\n")
    else:
        assert json.loads(FIXTURE.read_text()) == json.loads(json.dumps(record))
        for name in record["cases"]:
            print(f"PASS independent COL07 corner {name}")


if __name__ == "__main__":
    main()
