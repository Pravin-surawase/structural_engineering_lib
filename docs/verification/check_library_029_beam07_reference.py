"""Freeze signed eccentric-load statics and same-row torsion checks."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "library-029-beam07-equilibrium-torsion.json"


def fixture():
    d2 = json.loads((ROOT / "library-027-torsion-physical.json").read_text())
    span, load, eccentricity = 5000, 12, 50
    bar_area = 2 * math.pi * 20**2 / 4
    d = 350
    pt = 100 * bar_area / (300 * d)
    tc = 0.49 + (pt - 0.5) / 0.25 * (0.57 - 0.49)
    fy = 0.87 * 415
    cases = {}
    for name, sign, spacing, status in (
        ("equilibrium", 1, 100, "PASS"),
        ("reversed_torque", -1, 100, "PASS"),
        ("inadequate_links", 1, 175, "FAIL"),
        ("missing_transfer", 1, 100, "HOLD"),
        ("inadequate_longitudinal", 1, 100, "FAIL"),
    ):
        rows = []
        w = 22 if name == "inadequate_longitudinal" else load
        for station in d2["expected"]["action_rows"]:
            x = station["station_mm"]
            moment = w * x * (span - x) / 2e6
            shear = w * (span / 2 - x) / 1000
            torque = sign * eccentricity * shear / 1000
            ve = abs(shear) + 1.6 * abs(torque) * 1000 / 300
            mt = abs(torque) * (1 + 400 / 300) / 1.7
            area = abs(torque) * 1e6 / (200 * 300 * fy) + abs(shear) * 1000 / (
                2.5 * (300 if torque else 342) * fy
            )
            rows.append(
                {
                    "station_mm": x,
                    "v2_kn": shear,
                    "m3_knm": moment,
                    "torsion_knm": torque,
                    "equivalent_shear_kn": ve,
                    "primary_moment_knm": moment + mt,
                    "opposite_moment_knm": max(0, mt - moment),
                    "required_link_area_per_spacing_mm": max(
                        area, (ve * 1000 / (300 * d) - tc) * 300 / fy, 0.4 * 300 / fy
                    ),
                    "provided_link_area_per_spacing_mm": 2
                    * math.pi
                    * 8**2
                    / 4
                    / spacing,
                }
            )
        cases[name] = {
            "status": status,
            "uniform_load_n_per_mm": w,
            "eccentricity_mm": sign * eccentricity,
            "link_spacing_mm": spacing,
            "rows": rows,
            "support_reaction_kn": w * span / 2000,
            "support_external_torque_knm": -sign * w * eccentricity * span / 2e6,
        }
    return {
        "fixture_version": "library-029-beam07-equilibrium-torsion-reference/v1",
        "sources": [
            "Qualified D2 edge beam geometry and receiving crossheads; eccentric UDL free body.",
            "IS 456 Cl. 41.3 and 41.4 and Table 19, evaluated for each same-station row.",
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
    print(f"Independent BEAM07 reference: {len(data['cases'])} cases")


if __name__ == "__main__":
    main()
