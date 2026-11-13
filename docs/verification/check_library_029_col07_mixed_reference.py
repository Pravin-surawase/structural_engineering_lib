"""Independently freeze the continuous mixed-bar member shear and bar schedule."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "library-029-col07-mixed-member.json"


def fixture():
    member = json.loads((ROOT / "library-029-col03-mixed-column.json").read_text())[
        "cases"
    ]["admitted_12_bar"]["request"]
    base = json.loads((ROOT / "library-029-col07-column-member.json").read_text())[
        "cases"
    ]["continuous"]["request"]
    request = {
        **base,
        "schema_version": "column-positioned-member-detailing-input/v1",
        "identity": {**member["identity"], "case_id": "COL07-mixed-continuous"},
        "geometry": member["geometry"],
        "materials": member["materials"],
        "reinforcement": member["reinforcement"],
        "end_detail": {
            **base["end_detail"],
            "start_straight_mm": 1000,
            "end_straight_mm": 1000,
            "end_hoop_offset_mm": 100,
            "max_end_hoop_offset_mm": 110,
        },
        "tie_zones": [
            {"zone_id": "LOW", "start_mm": 100, "end_mm": 700, "pitch_mm": 100},
            {"zone_id": "FIELD", "start_mm": 700, "end_mm": 2300, "pitch_mm": 160},
            {"zone_id": "HIGH", "start_mm": 2300, "end_mm": 2900, "pitch_mm": 100},
        ],
        "actions": [
            {
                **member["actions"],
                "combination_id": "U1",
                "check_station_mm": 250,
                "vx_kn": 0,
                "vy_kn": 250,
            },
            {
                **member["actions"],
                "combination_id": "U2",
                "check_station_mm": 1500,
                "vx_kn": -170,
                "vy_kn": 0,
            },
        ],
        "transverse_cut_schedule": {
            "detailing_revision": "D1",
            "reference": "COL07 mixed closed hoop fabrication register",
            "cut_lengths_mm": {"HOOP": 1870},
        },
    }
    grid = sorted(
        {
            p
            for z in request["tie_zones"]
            for p in range(z["start_mm"], z["end_mm"] + 1, z["pitch_mm"])
        }
    )
    cut_links = {
        "Y1": 430 + 2 * (15 * math.radians(135) + 60),
        "Y2": 430 + 2 * (15 * math.radians(135) + 60),
        "X1": 330 + 2 * (15 * math.radians(135) + 60),
    }
    diameter_lengths = [(4, 20, 5000), (8, 16, 5000), (len(grid), 10, 1870)]
    diameter_lengths += [(len(grid), 10, cut) for cut in cut_links.values()]

    def shear(width, depth, pitch):
        axial_factor = min(1.5, 1 + 3 * 800000 / (450 * 550 * 30))
        concrete = 0.29 * axial_factor * width * depth / 1000
        links = 0.87 * 415 * (math.pi * 10**2 / 2) * depth / pitch / 1000
        return {"vc_kn": concrete, "vus_kn": links, "d_mm": depth}

    reference = {
        "status": "PASS",
        "end_required_mm": 20 * 0.87 * 500 / (4 * 1.5 * 1.6),
        "hoop_stations_mm": grid,
        "shear": [shear(450, 490, 100), shear(550, 390, 160)],
        "cross_tie_cut_mm": cut_links,
        "quantity": sum(count for count, _, _ in diameter_lengths),
        "total_length_mm": sum(count * length for count, _, length in diameter_lengths),
        "total_weight_kg": sum(
            count * math.pi * diameter**2 / 4 * length * 7850e-9
            for count, diameter, length in diameter_lengths
        ),
    }
    cases = {"mixed_continuous": {"request": request, "expected": reference}}
    for name, status in (
        ("stale_register", "HOLD"),
        ("short_anchor", "FAIL"),
        ("unresolved_splice", "HOLD"),
    ):
        control = deepcopy(request)
        control["identity"]["case_id"] = f"COL07-mixed-{name}"
        if name == "stale_register":
            control["transverse_cut_schedule"]["detailing_revision"] = "D0"
        elif name == "short_anchor":
            control["end_detail"]["end_straight_mm"] = 800
        else:
            control["laps"] = [
                {
                    "lap_id": "L1",
                    "bar_ids": ["C1", "C2"],
                    "start_mm": 1150,
                    "end_mm": 1850,
                    "stress_basis": "compression",
                }
            ]
        cases[name] = {"request": control, "expected": {"status": status}}
    return {
        "fixture_version": "library-029-col07-mixed-member-reference/v1",
        "sources": [
            "Admitted COL03 twelve-bar mixed cage and its independently checked section strength.",
            "IS 456 Clause 40 lowest Table 19 M30 shear row, two closed hoop legs and conservative face setback.",
            "IS 456 Clause 26.2 full tension development and independently summed actual straight bars, link arcs and supplied hoop cut.",
        ],
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    data = fixture()
    if args.freeze:
        FIXTURE.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    else:
        assert json.loads(FIXTURE.read_text()) == data
    print(f"Independent mixed COL07 reference: {len(data['cases'])} cases")


if __name__ == "__main__":
    main()
