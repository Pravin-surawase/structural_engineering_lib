"""Freeze ordinary circular member ring and helix quantities independently."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "library-029-col07-circular-member.json"


def fixture():
    source = json.loads((ROOT / "library-029-col05-circular-column.json").read_text())[
        "cases"
    ]
    base = json.loads((ROOT / "library-029-col07-column-member.json").read_text())[
        "cases"
    ]["continuous"]["request"]
    cases = {}
    for name, first, last, start_pitch, end_pitch in (
        ("tied", 75, 2925, None, None),
        ("spiral", 90, 2910, 15, 15),
    ):
        member = source[name]["request"]
        transverse = member["reinforcement"]["transverse"]
        request = {
            "identity": {**member["identity"], "case_id": f"COL07-{name}"},
            "geometry": member["geometry"],
            "materials": member["materials"],
            "reinforcement": member["reinforcement"],
            "basis": base["basis"],
            "end_detail": {
                **base["end_detail"],
                "start_straight_mm": 1000,
                "end_straight_mm": 1000,
            },
            "actions": [
                {**member["actions"], "combination_id": "U1", "vx_kn": 0, "vy_kn": 0},
                {
                    **member["actions"],
                    "combination_id": "U2",
                    "mx_knm": -70,
                    "my_knm": -40,
                    "check_station_mm": 900,
                    "vx_kn": 0,
                    "vy_kn": 0,
                },
            ],
            "placement": {
                "first_station_mm": first,
                "last_station_mm": last,
                "end_clearance_mm": 30,
                "start_anchor_pitch_mm": start_pitch,
                "end_anchor_pitch_mm": end_pitch,
                "source_reference": "Ordinary ring/spiral layout and end-turn fabrication worksheet",
            },
            "transverse_cut_schedule": (
                {
                    "detailing_revision": "D1",
                    "reference": "Approved closed ring cut and closure geometry",
                    "cut_lengths_mm": {"R1": 1180},
                }
                if name == "tied"
                else None
            ),
        }
        main_turns = (last - first) / transverse["pitch_mm"]
        circ = math.pi * (450 - 2 * 40 - 10)
        if name == "tied":
            cut, qty = 1180, int(main_turns) + 1
        else:
            cut = main_turns * math.hypot(circ, 60) + 3 * math.hypot(circ, 15)
            qty = 1
        weight = (
            8 * 5000 * math.pi * 20**2 / 4 + qty * cut * math.pi * 10**2 / 4
        ) * 7850e-9
        cases[name] = {
            "request": request,
            "expected": {
                "status": "PASS",
                "transverse_count": qty,
                "cut_mm": cut,
                "longitudinal_count": 8,
                "longitudinal_cut_mm": 5000,
                "mass_kg": weight,
            },
        }
    for name, origin, status in (
        ("stale_ring_register", "tied", "HOLD"),
        ("missing_anchor_pitch", "spiral", "HOLD"),
        ("crowded_anchor_pitch", "spiral", "FAIL"),
        ("nonzero_shear", "tied", "HOLD"),
    ):
        request = deepcopy(cases[origin]["request"])
        request["identity"]["case_id"] = f"COL07-{name}"
        if name == "stale_ring_register":
            request["transverse_cut_schedule"]["detailing_revision"] = "D0"
        elif name == "missing_anchor_pitch":
            request["placement"]["start_anchor_pitch_mm"] = None
        elif name == "crowded_anchor_pitch":
            request["placement"]["start_anchor_pitch_mm"] = 8
        else:
            request["actions"][0]["vy_kn"] = 40
        cases[name] = {"request": request, "expected": {"status": status}}
    return {
        "fixture_version": "library-029-col07-circular-member-reference/v1",
        "sources": [
            "COL05 actual tied/spiral member, separately checked axial and signed bending at supplied stations.",
            "Physical ring grid and declared cut register. Helix length per turn is hypot(pi*centreline diameter, pitch), summed over body and the two end segments.",
            "No circular shear strength or splice model is assumed.",
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
    print(f"Independent circular COL07 reference: {len(data['cases'])} cases")


if __name__ == "__main__":
    main()
