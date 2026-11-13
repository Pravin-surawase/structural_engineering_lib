"""Freeze physical continuous two-span bar lengths and ordinary link placement."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "library-029-beam05-member-detailing.json"


def fixture():
    source = json.loads((ROOT / "library-029-beam01-flow01.json").read_text())["cases"]
    request = {
        "identity": {"family_id": "beam", "case_id": "BEAM05", "member_id": "B01"},
        "member": source["two_span"]["request"],
        "link_detail": {
            "first_station_mm": 0,
            "last_station_mm": 8100,
            "internal_bend_radius_mm": 10,
            "hook_vertex_leg_mm": 100,
            "hook_plane_offset_mm": 10,
            "source_reference": "BEAM05 ordinary two-hook closed-cage specimen detail",
        },
        "stock_length_mm": 12000,
    }
    # Five tangent bends, three planar right angles and two slightly oblique
    # corners adjacent to the longitudinal hook-plane offset.
    inner_width, inner_depth = 228, 478
    offset, leg, radius = 10, 100, 14
    oblique = math.hypot(inner_width, offset)
    angles = (math.pi / 2,) * 5
    link_cut = 2 * leg + inner_width + 2 * inner_depth + oblique
    link_cut += sum(radius * (theta - 2 * math.tan(theta / 2)) for theta in angles)
    longitudinal_cut = 8218 - (-218)

    def mass(quantity, diameter, cut):
        return quantity * math.pi * diameter**2 / 4 * cut * 7850e-9

    expected = {
        "status": "PASS",
        "link_count": 28,
        "link_cut_mm": link_cut,
        "longitudinal_count": 6,
        "longitudinal_cut_mm": longitudinal_cut,
        "mass_kg": mass(28, 8, link_cut) + mass(6, 20, longitudinal_cut),
    }
    cases = {"continuous": {"request": request, "expected": expected}}
    short = deepcopy(request)
    short["identity"]["case_id"] = "BEAM05-short-anchor"
    short["member"] = source["short_anchorage"]["request"]
    cases["short_anchor"] = {"request": short, "expected": {"status": "FAIL"}}
    held = deepcopy(request)
    held["identity"]["case_id"] = "BEAM05-missing-link"
    held["link_detail"] = None
    cases["missing_link"] = {"request": held, "expected": {"status": "HOLD"}}
    return {
        "fixture_version": "library-029-beam05-member-detailing-reference/v1",
        "sources": [
            "BEAM01 two-span physical bars and support-face station checks.",
            "Tangent correction for each ordinary hook and corner, uniform discrete link grid and actual steel mass.",
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
    print(f"Independent BEAM05 reference: {len(data['cases'])} cases")


if __name__ == "__main__":
    main()
