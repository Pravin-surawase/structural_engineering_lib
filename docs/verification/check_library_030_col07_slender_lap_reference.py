"""Independent COL07 S1 slender compression-lap freeze; no product imports."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from hashlib import sha256
from itertools import combinations
from pathlib import Path

from check_library_029_col04_reference import _section_reference

ROOT = Path(__file__).resolve().parent
LEGACY = ROOT / "library-029-col07-slender-member.json"
FIXTURE = ROOT / "library-030-col07-slender-lap-reference.json"
BASE = "4f9af7321f6762c932ca14c6d4a9d337004d5f59"
BAR_MARKS = ("C1", "C2", "C3", "C4", "M_LEFT", "M_RIGHT", "M_TOP", "M_BOTTOM")
PAIR = ("M_LEFT", "M_RIGHT")


def _bars(upper: bool) -> list[dict[str, float]]:
    points = [
        (60, 60),
        (240, 60),
        (240, 340),
        (60, 340),
        (60, 200),
        (240, 200),
        (150, 60),
        (150, 340),
    ]
    return [
        {
            "x_from_left_mm": x,
            "y_from_top_mm": y + (20 if upper and y == 200 else 0),
            "diameter_mm": 20,
        }
        for x, y in points
    ]


def _ratio(action: dict, bars: list[dict[str, float]]) -> dict:
    axes, puz, alpha, ray, _ = _section_reference(
        300, 400, 25, 415, action["pu_kn"], json.dumps(bars, sort_keys=True), 64
    )
    mx, my = action["mx_knm"], action["my_knm"]
    cap_x = axes["x_negative" if mx < 0 else "x_positive"]["capacity_knm"]
    cap_y = axes["y_negative" if my < 0 else "y_positive"]["capacity_knm"]
    contour = (abs(mx) / cap_x) ** alpha + (abs(my) / cap_y) ** alpha
    demand = ray(mx, my)
    direct = math.hypot(mx, my) / demand["capacity_knm"]
    return {
        "puz_kn": puz,
        "alpha_n": alpha,
        "capacity_x_knm": cap_x,
        "capacity_y_knm": cap_y,
        "contour_ratio": contour,
        "direct_ratio": direct,
        "ratio": max(contour, direct),
    }


def _grid(request: dict) -> list[float]:
    return sorted(
        {
            p
            for z in request["tie_zones"]
            for p in range(z["start_mm"], z["end_mm"] + 1, z["pitch_mm"])
        }
    )


def _gross_minimum_stress(request: dict, action: dict) -> float:
    b, depth = request["geometry"]["b_mm"], request["geometry"]["D_mm"]
    return (
        1000 * action["pu_kn"] / (b * depth)
        - 6e6 * abs(action["mx_knm"]) / (b * depth**2)
        - 6e6 * abs(action["my_knm"]) / (depth * b**2)
    )


def _pass_expected(request: dict) -> dict:
    lap = request["laps"][0]
    # Increase the compression development length by 10% for the declared
    # contact-pair profile and retain the straight compression minimum of 24d.
    end_development = 0.87 * 415 * 20 / (4 * 1.4 * 1.6)
    required = max(1.10 * end_development / 1.25, 24 * 20)
    ends = request["end_detail"]
    assert min(ends["start_straight_mm"], ends["end_straight_mm"]) >= end_development
    grid = _grid(request)
    lap_grid = [s for s in grid if lap["start_mm"] <= s <= lap["end_mm"]]
    rows = []
    for station_id, phase, action, bars in (
        ("A", "LOWER_ONLY", request["actions"][0], _bars(False)),
        ("MID", "OVERLAP_LOWER", request["actions"][1], _bars(False)),
        ("MID", "OVERLAP_UPPER", request["actions"][1], _bars(True)),
        ("B", "UPPER_ONLY", request["actions"][2], _bars(True)),
    ):
        rows.append(
            {"station_id": station_id, "physical_phase": phase, **_ratio(action, bars)}
        )
    assert all(row["ratio"] < 1 for row in rows)
    gross = [_gross_minimum_stress(request, action) for action in request["actions"]]
    assert min(gross) > 0
    assert lap["end_mm"] - lap["start_mm"] >= required
    assert (
        len(lap_grid) >= 6 and max(b - a for a, b in zip(lap_grid, lap_grid[1:])) <= 120
    )
    r, dt = 16, 8
    x_levels = [station + 12 for station in grid]
    within = [
        station for station in x_levels if lap["start_mm"] < station < lap["end_mm"]
    ]
    support = [station for station in x_levels if station not in within]
    end_support = [
        lap["start_mm"] - max(s for s in x_levels if s < lap["start_mm"]),
        min(within) - lap["start_mm"],
        lap["end_mm"] - max(within),
        min(s for s in x_levels if s > lap["end_mm"]) - lap["end_mm"],
    ]
    assert max(end_support) <= 80 and min(end_support) >= dt / 2
    # Existing H hoop cut is an external register. The return-link formula is
    # independent centreline geometry: spine + four quadrant bends + two 8d tails.
    xt = 180 + 2 * math.pi * r + 16 * dt
    yt = 280 + 2 * math.pi * r + 16 * dt
    s1 = xt + 2 * 20
    assert 60 - r - dt / 2 == 40 and 300 - 120 - 2 * (8 * dt) - dt == 44
    assert r - 10 - dt / 2 == 2 and 64 >= 8 * dt
    lower = dict(zip(BAR_MARKS, _bars(False), strict=True))
    upper = dict(zip(BAR_MARKS, _bars(True), strict=True))
    overlap = {
        **lower,
        **{f"{mark}-U": upper[mark] for mark in PAIR},
    }
    unrelated_clearance = min(
        math.hypot(
            bar["x_from_left_mm"] - other["x_from_left_mm"],
            bar["y_from_top_mm"] - other["y_from_top_mm"],
        )
        - 20
        for (mark, bar), (other_mark, other) in combinations(overlap.items(), 2)
        if other_mark != f"{mark}-U"
    )
    assert unrelated_clearance == 70
    assert unrelated_clearance >= max(
        20, request["reinforcement"]["aggregate_size_mm"] + 5
    )
    length = request["geometry"]["unsupported_length_mm"]
    z_start, z_end = -ends["start_straight_mm"], length + ends["end_straight_mm"]
    hoop_mark = request["reinforcement"]["tie"]["tie_id"]
    hoop_cut = request["transverse_cut_schedule"]["cut_lengths_mm"][hoop_mark]
    cuts = {
        **{mark: [1, z_end - z_start, 20] for mark in BAR_MARKS if mark not in PAIR},
        **{f"{mark}-L": [1, lap["end_mm"] - z_start, 20] for mark in PAIR},
        **{f"{mark}-U": [1, z_end - lap["start_mm"], 20] for mark in PAIR},
        hoop_mark: [len(grid), hoop_cut, dt],
        "XT": [len(support), xt, 8],
        "YT": [len(grid), yt, 8],
        "S1-LINK": [len(within), s1, 8],
    }
    return {
        "status": "PASS",
        "issue": None,
        "svg_available": True,
        "bbs_available": True,
        "lap_required_mm": required,
        "lap_actual_mm": lap["end_mm"] - lap["start_mm"],
        "end_development_required_mm": end_development,
        "simultaneous_lapped_bar_fraction": len(PAIR) / len(BAR_MARKS),
        "contact_pair_basis": "two equal 20-mm side-midpoint bars only; 1.10 compression factor is not applied to other bars",
        "lap_hoop_stations_mm": lap_grid,
        "lap_link_stations_mm": within,
        "end_support_distances_mm": end_support,
        "minimum_unrelated_clear_mm": unrelated_clearance,
        "minimum_3d_clear_mm": 2,
        "gross_kern_stress_nmm2": gross,
        "return_fit": {
            "bend_radius_centreline_mm": 16,
            "return_angle_deg": 90,
            "tail_mm": 64,
            "tail_required_mm": 64,
            "cover_clear_mm": 40,
            "tail_gap_mm": 44,
            "minimum_link_to_longitudinal_clear_mm": 2,
        },
        "drawing": {
            "view": "elevation and 300x400 section",
            "lap_link": "S1-LINK at every listed X cross-tie level within the overlap",
            "contact_offset_mm": 20,
        },
        "svg_markers": {
            "member_z_mm": [0, 2640, 3360, 6000],
            "side_pair_centres_mm": [[60, 200], [240, 200], [60, 220], [240, 220]],
            "lap_link_stations_mm": within,
        },
        "section_phase_checks": rows,
        "governing_section": max(rows, key=lambda row: row["ratio"]),
        "cuts": cuts,
        "bbs_quantity": sum(v[0] for v in cuts.values()),
        "bbs_total_mm": sum(v[0] * v[1] for v in cuts.values()),
        "bbs_mass_kg": sum(
            v[0] * v[1] * math.pi * v[2] ** 2 / 4 * 7850e-9 for v in cuts.values()
        ),
    }


def _gate(request: dict) -> dict:
    """Return the permitted artifact state from independently inspectable inputs."""
    lap = request["laps"][0]
    if (
        request["basis"]["analysis_revision"]
        != request["basis"]["current_analysis_revision"]
    ):
        return {
            "status": "HOLD",
            "issue": "COLUMN.STALE_ANALYSIS",
            "svg_available": False,
            "bbs_available": False,
        }
    second_order = request["second_order"]
    supplied = {
        (
            second_order["combination_id"],
            row["station_mm"],
            second_order["pu_kn"],
            row["mx_knm"],
            row["my_knm"],
        )
        for row in second_order["stations"]
    }
    actions = {
        (
            row["combination_id"],
            row["check_station_mm"],
            row["pu_kn"],
            row["mx_knm"],
            row["my_knm"],
        )
        for row in request["actions"]
    }
    if supplied != actions:
        return {
            "status": "HOLD",
            "issue": "COLUMN.SLENDER_DETAIL_ACTIONS_HELD",
            "svg_available": False,
            "bbs_available": False,
        }
    assembly = lap.get("contact_assembly")
    in_lap = [
        _gross_minimum_stress(request, action)
        for action in request["actions"]
        if lap["start_mm"] <= action["check_station_mm"] <= lap["end_mm"]
    ]
    if (
        not assembly
        or not assembly.get("compression_reference")
        or not request["basis"].get("lap_action_continuity_reference")
        or not in_lap
        or min(in_lap) <= 0
    ):
        return {
            "status": "HOLD",
            "issue": "COLUMN.LAP_COMPRESSION_BASIS",
            "svg_available": False,
            "bbs_available": False,
            "minimum_supplied_lap_stress_nmm2": min(in_lap, default=None),
        }
    if assembly["partner_y_mm"] == 200:
        return {
            "status": "FAIL",
            "issue": "COLUMN.LAP_CONTACT_GEOMETRY",
            "svg_available": False,
            "bbs_available": False,
            "actual_contact_centre_distance_mm": 0,
            "required_contact_centre_distance_mm": 20,
        }
    ld = 0.87 * 415 * 20 / (4 * 1.4 * 1.6 * 1.25)
    actual_lap = lap["end_mm"] - lap["start_mm"]
    required_lap = max(1.1 * ld, 24 * 20)
    if actual_lap < required_lap:
        return {
            "status": "FAIL",
            "issue": "COLUMN.LAP_LENGTH",
            "svg_available": False,
            "bbs_available": False,
            "lap_actual_mm": actual_lap,
            "lap_required_mm": required_lap,
        }
    return _pass_expected(request)


def fixture() -> dict:
    request = deepcopy(json.loads(LEGACY.read_text())["cases"]["slender"]["request"])
    request["identity"]["case_id"] = "COL07-slender-S1"
    # Only the closed hoop cut is externally supplied. The three link cuts
    # follow the checked return geometry at their respective levels.
    cut_lengths = request["transverse_cut_schedule"]["cut_lengths_mm"]
    hoop_mark = request["reinforcement"]["tie"]["tie_id"]
    request["transverse_cut_schedule"]["cut_lengths_mm"] = {
        hoop_mark: cut_lengths[hoop_mark]
    }
    request["approved_lap_zone"] = {
        "start_mm": 2640,
        "end_mm": 3360,
        "max_tie_pitch_mm": 120,
        "reference": "Fixed specimen midpoint compression splice window",
    }
    request["laps"] = [
        {
            "lap_id": "S1",
            "bar_ids": ["M_LEFT", "M_RIGHT"],
            "start_mm": 2640,
            "end_mm": 3360,
            "stress_basis": "compression",
            "contact_assembly": {
                "partner_y_mm": 220,
                "lap_link_id": "S1-LINK",
                "hook_tail_mm": 64,
                "fabrication_reference": "S1 paired-side contact link schedule",
                "compression_reference": "Supplied U1 compression action continuity declaration across 2640--3360 mm",
            },
        }
    ]
    request["basis"][
        "lap_action_continuity_reference"
    ] = "Declared synthetic U1 compression throughout the lap interval. At fixed 500 kN and EI, 0.30 times the COL04 eccentricity record gives moment magnitudes bounded by MID on both axes."
    request["basis"][
        "action_source_reference"
    ] = "COL04 fixed-P constant-EI worksheet, declared 0.30 eccentricity specimen"
    request["second_order"][
        "member_deflection_basis"
    ] = "Supplied COL04 constant-EI second-order moments scaled by 0.30 at fixed P and EI for the smaller eccentricities"
    # Deliberately supplied/reduced action pairs: 0.30 x COL04 fixed-P record.
    for action, second in zip(
        request["actions"], request["second_order"]["stations"], strict=True
    ):
        action["mx_knm"], action["my_knm"] = (
            second["mx_knm"] * 0.30,
            second["my_knm"] * 0.30,
        )
        second["mx_knm"], second["my_knm"] = action["mx_knm"], action["my_knm"]
    cases = {"s1_pass": {"request": request, "expected": _gate(request)}}
    for name, status, issue in (
        ("short_lap", "FAIL", "COLUMN.LAP_LENGTH"),
        ("coincident_contact", "FAIL", "COLUMN.LAP_CONTACT_GEOMETRY"),
        ("missing_compression_evidence", "HOLD", "COLUMN.LAP_COMPRESSION_BASIS"),
        ("outside_compression_kern", "HOLD", "COLUMN.LAP_COMPRESSION_BASIS"),
        ("stale_analysis", "HOLD", "COLUMN.STALE_ANALYSIS"),
        ("missing_matching_second_order", "HOLD", "COLUMN.SLENDER_DETAIL_ACTIONS_HELD"),
    ):
        control = deepcopy(request)
        control["identity"]["case_id"] = "COL07-slender-S1-" + name
        if name == "short_lap":
            control["laps"][0]["end_mm"] = 3300
        elif name == "coincident_contact":
            control["laps"][0]["contact_assembly"]["partner_y_mm"] = 200
        elif name == "missing_compression_evidence":
            control["laps"][0]["contact_assembly"]["compression_reference"] = None
        elif name == "outside_compression_kern":
            control["actions"][1]["mx_knm"] = -30
            control["second_order"]["stations"][1]["mx_knm"] = -30
        elif name == "stale_analysis":
            control["basis"]["current_analysis_revision"] = "model-00"
        else:
            control["actions"][1]["mx_knm"] += 0.1
        expected = _gate(control)
        assert (expected["status"], expected["issue"]) == (status, issue)
        cases[name] = {"request": control, "expected": expected}
    return {
        "schema_version": "library-030-col07-slender-lap-reference/v1",
        "frozen_production_base": BASE,
        "legacy_fixture_sha256": sha256(LEGACY.read_bytes()).hexdigest(),
        "sources": [
            "BIS IS 456:2000 Cl. 26.2.1, 26.2.5.1, 26.3.2, 26.5.3 and 39.6–39.7. https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf",
            "check_library_029_col04_reference.py supplies the independent fixed-load section integration. check_library_029_col07_splice_reference.py supplies the straight paired contact and link geometry precedent.",
        ],
        "absolute_tolerances": {
            "length_mm": 0.001,
            "mass_kg": 0.001,
            "stress_nmm2": 0.001,
            "moment_knm": 0.01,
            "section_ratio": 0.0001,
        },
        "method": "Independent fixed-load P-M contour replay at each supplied station and every physical reinforcement phase affected by S1 transfer. Supplied second-order U1 actions/revision are fixed inputs, never regenerated. The declared 0.30-eccentricity action pair gives gross stress P/A-6|Mx|/(bD^2)-6|My|/(Db^2)>0 at every supplied station. Geometry and action scaling are specimen assumptions, not IS 456 text.",
        "cases": cases,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    data = fixture()
    if args.freeze:
        FIXTURE.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    else:
        assert json.loads(FIXTURE.read_text()) == data
    print(f"PASS independent COL07 slender S1: {len(data['cases'])} cases")


if __name__ == "__main__":
    main()
