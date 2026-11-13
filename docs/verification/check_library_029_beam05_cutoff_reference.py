"""Independent station checks and material takeoff for one BEAM05 bottom cutoff."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "library-029-beam05-cutoff.json"


def build():
    continuous = json.loads(
        (HERE / "library-029-beam05-member-detailing.json").read_text()
    )["cases"]["continuous"]
    original = continuous["request"]
    reference = continuous["expected"]
    theoretical = 2600.0
    development = 20 * 0.87 * 415 / (4 * 1.4 * 1.6)
    area = 2 * math.pi * 20**2 / 4
    ratio = 100 * area / (300 * 500)
    tau_c = 0.36 + (ratio - 0.25) / 0.25 * (0.49 - 0.36)
    shear = (
        tau_c * 300 * 500 / 1000
        + 0.87 * 415 * (2 * math.pi * 8**2 / 4) * 500 / 300 / 1000
    )
    cases = {}
    for name, end, status in (
        ("cutoff", 3500.0, "PASS"),
        ("short_development", theoretical + development - 100, "FAIL"),
        ("missing_cutoff_rows", 3500.0, "HOLD"),
        ("cutoff_shear_over_two_thirds", 3500.0, "FAIL"),
    ):
        request = deepcopy(original)
        request["identity"]["case_id"] = "BEAM05-" + name
        request["member"]["reinforcement_revision"] = "SPECIMEN-" + name
        request["cutoff"] = {
            "bar_id": "bottom-3",
            "theoretical_station_id": "CUT-THEORETICAL",
            "termination_station_id": "CUT-END",
        }
        member = request["member"]
        added_stations = {
            "CUT-THEORETICAL": theoretical,
            "CUT-END": end,
        }
        for sid, coordinate in added_stations.items():
            member["stations"].append(
                {"station_id": sid, "x_mm": coordinate, "side": "CONTINUOUS"}
            )
        for combo in member["combinations"]:
            if combo["kind"] != "ULS":
                continue
            cid = combo["combination_id"]
            if name == "missing_cutoff_rows" and cid == "U2":
                continue
            combo["required_station_ids"].extend(added_stations)
            for sid, coordinate in added_stations.items():
                x = coordinate / 1000
                if cid == "B01":
                    mu, vu = 90 - 70 * (x - 2), -70
                elif cid == "PATTERN":
                    mu, vu = 50 * x - 15 * x**2, 50 - 30 * x
                else:
                    # Independent supplied U1/U2 actions in this teaching case.
                    mu, vu = (30, -52) if sid == "CUT-THEORETICAL" else (-12, -60)
                if (
                    name == "cutoff_shear_over_two_thirds"
                    and cid == "B01"
                    and sid == "CUT-END"
                ):
                    vu = -90
                member["actions"].append(
                    dict(
                        row_id=f"{cid}:{sid}",
                        combination_id=cid,
                        station_id=sid,
                        mu_knm=mu,
                        vu_kn=vu,
                    )
                )
        cut = end - original["member"]["straight_bars"]["start_mm"]
        cases[name] = {
            "request": request,
            "expected": {
                "status": status,
                "development_mm": development,
                "required_extension_mm": 500.0,
                "available_extension_mm": end - theoretical,
                "continuing_bottom_mm2": area,
                "continuing_shear_capacity_kn": shear,
                "two_thirds_shear_kn": 2 * shear / 3,
                "cut_mm": cut,
                "mass_kg": reference["mass_kg"]
                - (8436 - cut) * math.pi * 20**2 / 4 * 7850e-9,
            },
        }
    return {"fixture_version": "library-029-beam05-cutoff/v1", "cases": cases}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    expected = build()
    if args.freeze:
        TARGET.write_text(json.dumps(expected, indent=2, allow_nan=False) + "\n")
    else:
        assert json.loads(TARGET.read_text()) == expected
    print(f"Independent BEAM05 cutoff reference: {len(expected['cases'])} cases")


if __name__ == "__main__":
    main()
