"""Independent hand equations and schedules for the first COL07 member packet."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

REFERENCE = Path(__file__).with_name("library-029-col07-column-member.json")


def requests():
    base = {
        "identity": {
            "family_id": "column",
            "member_id": "COL07-C",
            "case_id": "continuous",
            "source_reference": "COL07 independent worked member",
        },
        "geometry": {
            "b_mm": 300,
            "D_mm": 400,
            "unsupported_length_mm": 3000,
            "end_condition": "FIXED_FIXED",
            "braced": True,
        },
        "materials": {"fck_nmm2": 25, "fy_nmm2": 415},
        "reinforcement": {
            "layout": "eight_bar",
            "longitudinal_bar_diameter_mm": 20,
            "bar_center_offset_mm": 60,
            "nominal_cover_mm": 40,
            "aggregate_size_mm": 20,
            "project_required_cover_mm": 40,
            "project_required_bend_radius_mm": 12,
            "detailing_basis_reference": "COL07 specimen cage and hoop closure",
            "tie": {
                "tie_id": "H",
                "diameter_mm": 8,
                "spacing_mm": 100,
                "internal_bend_radius_mm": 12,
                "closed": True,
                "hook_angle_deg": 135,
                "hook_tail_mm": 48,
            },
            "cross_ties": [
                {
                    "tie_id": "XT",
                    "restrained_bar_ids": ["M_LEFT", "M_RIGHT"],
                    "station_offset_mm": 12,
                },
                {
                    "tie_id": "YT",
                    "restrained_bar_ids": ["M_TOP", "M_BOTTOM"],
                    "station_offset_mm": 24,
                },
            ],
        },
        "basis": {
            "analysis_revision": "A1",
            "current_analysis_revision": "A1",
            "detailing_revision": "D1",
            "nonseismic_reference": "Ordinary braced specimen; no ductile detailing",
            "action_source_reference": "COL07 signed factored station worksheet",
            "end_development_reference": "Straight projections into checked adjoining concrete",
            "placement_reference": "COL07 specimen end and tie placement",
        },
        "end_detail": {
            "start_straight_mm": 850,
            "end_straight_mm": 850,
            "end_hoop_offset_mm": 60,
            "max_end_hoop_offset_mm": 75,
            "end_face_clearance_mm": 25,
        },
        "tie_fy_nmm2": 415,
        "tie_zones": [
            {"zone_id": "LOWER", "start_mm": 60, "end_mm": 660, "pitch_mm": 100},
            {"zone_id": "FIELD", "start_mm": 660, "end_mm": 2340, "pitch_mm": 140},
            {"zone_id": "UPPER", "start_mm": 2340, "end_mm": 2940, "pitch_mm": 100},
        ],
        "actions": [
            {
                "combination_id": "U1",
                "check_station_mm": 150,
                "pu_kn": 500,
                "mx_knm": 50,
                "my_knm": 35,
                "vx_kn": 0,
                "vy_kn": 160,
            },
            {
                "combination_id": "U1",
                "check_station_mm": 1500,
                "pu_kn": 500,
                "mx_knm": 50,
                "my_knm": 35,
                "vx_kn": 0,
                "vy_kn": 115,
            },
            {
                "combination_id": "U2",
                "check_station_mm": 2850,
                "pu_kn": 500,
                "mx_knm": -35,
                "my_knm": -50,
                "vx_kn": -100,
                "vy_kn": 0,
            },
        ],
        "approved_lap_zone": {
            "start_mm": 1100,
            "end_mm": 1900,
            "max_tie_pitch_mm": 150,
            "reference": "COL07 project-approved low stress compression splice window",
        },
        "laps": [],
        "transverse_cut_schedule": {
            "detailing_revision": "D1",
            "reference": "COL07 independent specimen cut-length register",
            "cut_lengths_mm": {"H": 1220, "XT": 365, "YT": 465},
        },
    }
    cases = {"continuous": base}
    for name in (
        "shear_shortfall",
        "crushing",
        "zone_boundary",
        "short_anchor",
        "congested_links",
        "stale_analysis",
        "combined_shear",
        "lap_numeric_pass",
        "lap_short",
        "lap_bad_zone",
        "lap_pitch",
        "lap_too_many",
        "missing_cut_register",
        "stale_cut_register",
    ):
        cases[name] = deepcopy(base)
        cases[name]["identity"]["case_id"] = name
    cases["shear_shortfall"]["tie_zones"][0]["pitch_mm"] = 150
    cases["crushing"]["actions"][0]["vy_kn"] = 400
    cases["zone_boundary"]["actions"][0].update(check_station_mm=660, vy_kn=145)
    cases["short_anchor"]["end_detail"]["end_straight_mm"] = 750
    cases["congested_links"]["reinforcement"]["cross_ties"][1]["station_offset_mm"] = 12
    cases["stale_analysis"]["basis"]["current_analysis_revision"] = "A2"
    cases["combined_shear"]["actions"][0]["vx_kn"] = 60
    for name in (
        "lap_numeric_pass",
        "lap_short",
        "lap_bad_zone",
        "lap_pitch",
        "lap_too_many",
    ):
        cases[name]["laps"] = [
            {
                "lap_id": "S1",
                "bar_ids": ["C1", "C2"],
                "start_mm": 1150,
                "end_mm": 1850,
                "stress_basis": "compression",
            }
        ]
    cases["lap_short"]["laps"][0]["end_mm"] = 1700
    cases["lap_bad_zone"]["laps"][0].update(start_mm=700, end_mm=1400)
    cases["lap_pitch"]["approved_lap_zone"]["max_tie_pitch_mm"] = 125
    cases["lap_too_many"]["laps"][0]["bar_ids"] += ["C3", "C4", "M_TOP"]
    cases["missing_cut_register"]["transverse_cut_schedule"] = None
    cases["stale_cut_register"]["transverse_cut_schedule"]["detailing_revision"] = "D0"
    for axis, keep in (("x", "YT"), ("y", "XT")):
        case_id = f"six_bar_omit_{axis}_face_midpoints"
        candidate = deepcopy(base)
        candidate["identity"]["case_id"] = case_id
        candidate["reinforcement"]["layout"] = case_id
        candidate["reinforcement"]["cross_ties"] = [
            link
            for link in base["reinforcement"]["cross_ties"]
            if link["tie_id"] == keep
        ]
        candidate["transverse_cut_schedule"]["cut_lengths_mm"] = {
            mark: cut
            for mark, cut in base["transverse_cut_schedule"]["cut_lengths_mm"].items()
            if mark in ("H", keep)
        }
        # Use the same two-plane shear controls, with modest compression
        # and bending inside the frozen COL02 six-bar resistance domain.
        for action in candidate["actions"]:
            action["mx_knm"] *= 0.6
            action["my_knm"] *= 0.6
        cases[case_id] = candidate

    cases["six_bar_unresolved_lap"] = deepcopy(cases["six_bar_omit_x_face_midpoints"])
    cases["six_bar_unresolved_lap"]["identity"]["case_id"] = "six_bar_unresolved_lap"
    cases["six_bar_unresolved_lap"]["laps"] = deepcopy(
        cases["lap_numeric_pass"]["laps"]
    )
    cases["six_bar_revised_pitch"] = deepcopy(cases["six_bar_omit_y_face_midpoints"])
    revised = cases["six_bar_revised_pitch"]
    revised["identity"]["case_id"] = "six_bar_revised_pitch"
    revised["tie_zones"][1]["pitch_mm"] = 120
    revised["basis"]["detailing_revision"] = "D2"
    revised["transverse_cut_schedule"]["detailing_revision"] = "D2"
    cases["six_bar_stale_cut"] = deepcopy(revised)
    cases["six_bar_stale_cut"]["identity"]["case_id"] = "six_bar_stale_cut"
    cases["six_bar_stale_cut"]["transverse_cut_schedule"]["detailing_revision"] = "D1"
    return cases


def expected(name, request):
    # One worked M25 grade. Use the lower Table 19 row without claiming
    # continuing tensile steel or any enhancement at an adjoining face.
    b, depth, offset = 300, 400, 60
    fy, fck, db, dt = 415, 25, 20, 8
    beta = min(1.5, 1 + 3 * 500_000 / (b * depth * fck))
    gross_hoop_area = 2 * math.pi * dt**2 / 4
    zones = request["tie_zones"]
    stations = sorted(
        {
            position
            for z in zones
            for position in range(z["start_mm"], z["end_mm"] + 1, z["pitch_mm"])
        }
    )
    statuses = {
        "continuous": ("PASS", None),
        "shear_shortfall": ("FAIL", "COLUMN.SHEAR_CAPACITY"),
        "crushing": ("FAIL", "COLUMN.SHEAR_CRUSHING"),
        "zone_boundary": ("FAIL", "COLUMN.SHEAR_CAPACITY"),
        "short_anchor": ("FAIL", "COLUMN.END_DEVELOPMENT"),
        "congested_links": ("FAIL", "COLUMN.MIDPOINT_TIE_LEVELS"),
        "stale_analysis": ("HOLD", "COLUMN.STALE_ANALYSIS"),
        "combined_shear": ("HOLD", "COLUMN.COMBINED_SHEAR"),
        "lap_numeric_pass": ("HOLD", "COLUMN.LAP_ASSEMBLY_REQUIRED"),
        "lap_short": ("FAIL", "COLUMN.LAP_LENGTH"),
        "lap_bad_zone": ("FAIL", "COLUMN.LAP_LOCATION"),
        "lap_pitch": ("FAIL", "COLUMN.LAP_TIE_PITCH"),
        "lap_too_many": ("FAIL", "COLUMN.LAP_BAR_FRACTION"),
        "missing_cut_register": ("HOLD", "COLUMN.TRANSVERSE_CUT_BASIS"),
        "stale_cut_register": ("HOLD", "COLUMN.TRANSVERSE_CUT_BASIS"),
        "six_bar_omit_x_face_midpoints": ("PASS", None),
        "six_bar_omit_y_face_midpoints": ("PASS", None),
        "six_bar_unresolved_lap": ("HOLD", "COLUMN.LAP_ASSEMBLY_REQUIRED"),
        "six_bar_revised_pitch": ("PASS", None),
        "six_bar_stale_cut": ("HOLD", "COLUMN.TRANSVERSE_CUT_BASIS"),
    }
    status, issue = statuses[name]
    result = {"status": status, "issue": issue, "bbs_available": status == "PASS"}
    # M25 Table 21 plain tension tau=1.4; deformed +60%; compression +25%.
    tension = db * (0.87 * fy) / (4 * 1.4 * 1.6)
    compression = tension / 1.25
    result["end_required_mm"] = tension
    result["lap_required_mm"] = max(compression, 24 * db)
    result["hoop_stations_mm"] = stations
    result["shear_rows"] = []
    for row in request["actions"]:
        if row["vx_kn"] and row["vy_kn"] or name == "congested_links":
            continue
        s = row["check_station_mm"]
        pitch = max(z["pitch_mm"] for z in zones if z["start_mm"] <= s <= z["end_mm"])
        width, d = (depth, b - offset) if row["vx_kn"] else (b, depth - offset)
        demand = abs(row["vx_kn"] or row["vy_kn"])
        concrete = 0.29 * beta * width * d / 1000
        ties = 0.87 * fy * gross_hoop_area * d / pitch / 1000
        cap = 3.1 * width * d / 1000
        result["shear_rows"].append(
            {
                "station_mm": s,
                "pitch_mm": pitch,
                "d_mm": d,
                "width_mm": width,
                "axial_factor": beta,
                "vc_kn": concrete,
                "vus_kn": ties,
                "crushing_kn": cap,
                "utilization": demand / min(concrete + ties, cap),
            }
        )
    if status == "PASS":
        longitudinal_count = (
            8 if request["reinforcement"]["layout"] == "eight_bar" else 6
        )
        cuts = request["transverse_cut_schedule"]["cut_lengths_mm"]
        quantities = [(longitudinal_count, 20, 4700)] + [
            (len(stations), 8, cut) for cut in cuts.values()
        ]
        result["bbs_quantity"] = sum(q for q, _, _ in quantities)
        result["bbs_length_mm"] = sum(q * cut for q, _, cut in quantities)
        result["bbs_weight_kg"] = sum(
            q * math.pi * dia**2 / 4 * cut * 7850e-9 for q, dia, cut in quantities
        )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--derive", action="store_true")
    args = parser.parse_args()
    cases = {
        name: {"request": request, "expected": expected(name, request)}
        for name, request in requests().items()
    }
    if args.derive:
        data = {
            "schema_version": "library-029-col07-member-reference/v1",
            "frozen_production_base": "e03c58186f53a7062dd2a0570d8df6c84105b130",
            "sources": [
                "IS 456:2000 Cl. 26.2.1, 26.2.5, 26.5.1.5–6, 26.5.3.2 and Cl. 40 with Tables 19 and 20.",
                "https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf",
            ],
            "method": "Independent equations at supplied rows. Conservative Table 19 base without tensile-steel or end-region credit. Station grid with shared boundary hoop; maximum adjacent pitch at boundaries. Straight tension development at both ends. Compression lap length and supplied zone geometry, with unresolved physical lap assembly held. Transverse cut lengths supplied by the fixture, not inferred from a centreline sketch.",
            "cases": cases,
        }
        REFERENCE.write_text(json.dumps(data, indent=2) + "\n")
    else:
        frozen = json.loads(REFERENCE.read_text())["cases"]
        assert frozen == cases
        for name in frozen:
            print(f"PASS independent COL07 {name}")


if __name__ == "__main__":
    main()
