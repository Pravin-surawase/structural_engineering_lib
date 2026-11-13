"""Bind an independently solved second-order member to full-length detailing targets."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "library-029-col07-slender-member.json"


def fixture():
    col04 = json.loads((ROOT / "library-029-col04-slender-column.json").read_text())[
        "cases"
    ]["supplied_second_order"]
    base = json.loads((ROOT / "library-029-col07-column-member.json").read_text())[
        "cases"
    ]["continuous"]["request"]
    strength = col04["request"]
    request = {
        **base,
        "schema_version": "column-slender-member-detailing-input/v1",
        "identity": {
            "family_id": "column",
            "case_id": "COL07-slender",
            "member_id": "COL04-C",
        },
        "geometry": {
            **base["geometry"],
            "unsupported_length_mm": 6000,
            "end_condition": "HINGED_HINGED",
        },
        "materials": strength["materials"],
        "reinforcement": {
            **strength["reinforcement"],
            "cross_ties": base["reinforcement"]["cross_ties"],
        },
        "basis": {
            **base["basis"],
            "analysis_revision": strength["analysis_revision"],
            "current_analysis_revision": strength["current_analysis_revision"],
        },
        "tie_zones": [
            {"zone_id": "LOW", "start_mm": 60, "end_mm": 660, "pitch_mm": 100},
            {"zone_id": "FIELD", "start_mm": 660, "end_mm": 5340, "pitch_mm": 120},
            {"zone_id": "HIGH", "start_mm": 5340, "end_mm": 5940, "pitch_mm": 100},
        ],
        "restraint": strength["geometry"],
        "second_order": strength["actions"],
        "actions": [
            {
                "combination_id": strength["actions"]["combination_id"],
                "check_station_mm": row["station_mm"],
                "pu_kn": strength["actions"]["pu_kn"],
                "mx_knm": row["mx_knm"],
                "my_knm": row["my_knm"],
                "vx_kn": 0,
                "vy_kn": 0,
            }
            for row in strength["actions"]["stations"]
        ],
    }
    hoop_mark = request["reinforcement"]["tie"]["tie_id"]
    register = request["transverse_cut_schedule"]
    register["cut_lengths_mm"][hoop_mark] = register["cut_lengths_mm"].pop("H")
    grid = sorted(
        {
            p
            for zone in request["tie_zones"]
            for p in range(zone["start_mm"], zone["end_mm"] + 1, zone["pitch_mm"])
        }
    )
    cuts = [
        (8, 20, 7700),
        *(
            (len(grid), 8, cut)
            for cut in base["transverse_cut_schedule"]["cut_lengths_mm"].values()
        ),
    ]
    expected = {
        "status": "PASS",
        "governing_id": col04["expected"]["governing_id"],
        "governing_ratio": col04["expected"]["governing_ratio"],
        "hoop_stations_mm": grid,
        "quantity": sum(q for q, _, _ in cuts),
        "total_length_mm": sum(q * cut for q, _, cut in cuts),
        "mass_kg": sum(
            q * math.pi * dia**2 / 4 * cut * 7850e-9 for q, dia, cut in cuts
        ),
    }
    cases = {"slender": {"request": request, "expected": expected}}
    for name, status in (
        ("stale_analysis", "HOLD"),
        ("unmatched_second_order", "HOLD"),
        ("short_anchor", "FAIL"),
    ):
        control = deepcopy(request)
        control["identity"]["case_id"] = f"COL07-slender-{name}"
        if name == "stale_analysis":
            control["basis"]["current_analysis_revision"] = "earlier"
        elif name == "unmatched_second_order":
            control["actions"][1]["mx_knm"] += 1
        else:
            control["end_detail"]["end_straight_mm"] = 750
        cases[name] = {"request": control, "expected": {"status": status}}
    for name, vx, vy, status in (
        ("slender_shear_x", -75, 0, "PASS"),
        ("slender_shear_y", 0, 95, "PASS"),
        ("slender_shear_excess", -150, 0, "FAIL"),
        ("slender_shear_combined", -75, 20, "HOLD"),
    ):
        control = deepcopy(request)
        control["identity"]["case_id"] = f"COL07-{name}"
        control["actions"][1].update(vx_kn=vx, vy_kn=vy)
        width, depth = (400, 240) if vx else (300, 340)
        vc = 0.29 * 1.5 * width * depth / 1000
        vs = 0.87 * 415 * (2 * math.pi * 8**2 / 4) * depth / 120 / 1000
        cases[name] = {
            "request": control,
            "expected": {
                **expected,
                "status": status,
                "shear": (
                    {
                        "direction": "x" if vx else "y",
                        "demand_kn": vx or vy,
                        "pitch_mm": 120,
                        "d_mm": depth,
                        "vc_kn": vc,
                        "vus_kn": vs,
                        "utilization": abs(vx or vy) / (vc + vs),
                    }
                    if not (vx and vy)
                    else None
                ),
            },
        }
    return {
        "fixture_version": "library-029-col07-slender-member-reference/v1",
        "sources": [
            "COL04 independent secant beam-column second-order actions and signed strength targets.",
            "COL07 independent straight tension development, tie placement and cut registers.",
            "The independently supplied principal shear uses COL07 two-leg hoop resistance and the COL04 concurrent axial force.",
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
    print(f"Independent slender COL07 reference: {len(data['cases'])} cases")


if __name__ == "__main__":
    main()
