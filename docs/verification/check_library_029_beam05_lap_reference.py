"""Independently derive one straight separated beam lap and its cut quantities."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "library-029-beam05-lap.json"


def fixture():
    baseline = json.loads(
        (HERE / "library-029-beam05-member-detailing.json").read_text()
    )["cases"]["continuous"]
    cases = {}
    ld = 20 * 0.87 * 415 / (4 * 1.4 * 1.6)
    for name, overlap, partner_x, status in (
        ("lap", 900, 198, "PASS"),
        ("short_lap", 700, 198, "FAIL"),
        ("lap_congestion", 900, 180, "FAIL"),
        ("missing_mid_lap_row", 900, 198, "HOLD"),
    ):
        request = deepcopy(baseline["request"])
        request["identity"]["case_id"] = f"BEAM05-{name}"
        request["member"]["reinforcement_revision"] = f"SPECIMEN-{name}"
        member = request["member"]
        # Shift the target bar to the other side of its checked lap partner.
        member["bars"][-1]["x_from_left_mm"] = 250
        start, end = 2600, 2600 + overlap
        stations = {"LAP-START": start, "LAP-MID": (start + end) / 2, "LAP-END": end}
        for key, x in stations.items():
            member["stations"].append(dict(station_id=key, x_mm=x, side="CONTINUOUS"))
        for combo in member["combinations"]:
            if combo["kind"] != "ULS":
                continue
            cid = combo["combination_id"]
            for key, x in stations.items():
                if name == "missing_mid_lap_row" and cid == "U2" and key == "LAP-MID":
                    continue
                combo["required_station_ids"].append(key)
                if cid == "B01":
                    mu, vu = 90 - 70 * (x / 1000 - 2), -70
                elif cid == "PATTERN":
                    mu, vu = 50 * x / 1000 - 15 * (x / 1000) ** 2, 50 - 30 * x / 1000
                else:
                    mu, vu = (30, -52) if key == "LAP-START" else (-12, -60)
                member["actions"].append(
                    dict(
                        row_id=f"{cid}:{key}",
                        combination_id=cid,
                        station_id=key,
                        mu_knm=mu,
                        vu_kn=vu,
                    )
                )
        request["lap"] = {
            "bar_id": "bottom-3",
            "partner_bar_id": "bottom-3-partner",
            "partner_x_from_left_mm": partner_x,
            "start_station_id": "LAP-START",
            "middle_station_id": "LAP-MID",
            "end_station_id": "LAP-END",
            "placement_reference": "One separated bottom-bar lap within the checked ordinary links",
        }
        cases[name] = {
            "request": request,
            "expected": {
                "status": status,
                "required_lap_mm": ld,
                "overlap_mm": overlap,
                "minimum_pair_clear_mm": min(abs(250 - partner_x), abs(partner_x - 150))
                - 20,
                "cut_original_mm": end + 218,
                "cut_partner_mm": 8218 - start,
                "mass_kg": baseline["expected"]["mass_kg"]
                + overlap * math.pi * 20**2 / 4 * 7850e-9,
            },
        }
    return {"fixture_version": "library-029-beam05-lap/v1", "cases": cases}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    expected = fixture()
    if args.freeze:
        TARGET.write_text(json.dumps(expected, indent=2) + "\n")
    else:
        assert json.loads(TARGET.read_text()) == expected
    print(f"Independent BEAM05 lap reference: {len(expected['cases'])} cases")
