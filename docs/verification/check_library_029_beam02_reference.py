"""Freeze and replay BEAM02 equilibrium, section and anchorage references."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

FIXTURE = Path(__file__).with_name("library-029-beam02-cantilever.json")


def section_reference(
    tension_diameter, tension_count, opposite_diameter, opposite_count
):
    """Solve the fixture's rectangular stress block by independent bisection."""
    width, fck, fy = 300, 25, 415
    d, opposite_depth = 450, 50
    ast = tension_count * math.pi * tension_diameter**2 / 4
    opposite_area = opposite_count * math.pi * opposite_diameter**2 / 4
    tensile_force = ast * fy / 1.15

    def forces(xu):
        strain = 0.0035 * (1 - opposite_depth / xu)
        assert abs(strain) < 0.8 * fy / 1.15 / 200000
        r = max(0, strain / 0.002)
        concrete_stress = (0.67 / 1.5) * fck * (2 * r - r * r)
        return 0.36 * fck * width * xu, opposite_area * (
            200000 * strain - concrete_stress
        )

    low, high = 40.0, 85.0
    assert sum(forces(low)) < tensile_force < sum(forces(high))
    for _ in range(65):
        mid = (low + high) / 2
        if sum(forces(mid)) < tensile_force:
            low = mid
        else:
            high = mid
    xu = (low + high) / 2
    assert 0.0035 * (d / xu - 1) > fy / 1.15 / 200000 + 0.002
    cc, fs = forces(xu)
    pt = 100 * ast / (width * d)
    lower, upper, t_lower, t_upper = (
        (0.25, 0.50, 0.36, 0.49) if pt < 0.50 else (0.50, 0.75, 0.49, 0.57)
    )
    assert lower <= pt <= upper
    tau_c = t_lower + (pt - lower) * (t_upper - t_lower) / (upper - lower)
    vc = tau_c * width * d / 1000
    vs = 0.87 * fy * (2 * math.pi * 8**2 / 4) * d / (250 * 1000)
    return {
        "d_mm": d,
        "xu_mm": xu,
        "tension_area_mm2": ast,
        "capacity_knm": (cc * (d - 0.42 * xu) + fs * (d - opposite_depth)) / 1e6,
        "concrete_shear_kn": vc,
        "link_shear_kn": vs,
        "shear_capacity_kn": vc + vs,
        "development_mm": tension_diameter * 0.87 * fy / (4 * 1.4 * 1.6),
    }


def fixture():
    stations = [
        ("FIXED", 0, "CONTINUOUS"),
        ("P-LEFT", 1000, "LEFT"),
        ("P-RIGHT", 1000, "RIGHT"),
        ("FREE", 2000, "CONTINUOUS"),
    ]
    rows = []
    for combo, q, p in (("UDL", 20, 0), ("POINT", 20, 10), ("S1", 12, 0)):
        for station, x_mm, side in stations:
            x = x_mm / 1000
            point_present = x < 1 or (x == 1 and side == "LEFT")
            arm = 2 - x
            rows.append(
                {
                    "row_id": f"{combo}:{station}",
                    "combination_id": combo,
                    "station_id": station,
                    "mu_knm": -(q * arm**2 / 2 + (p * (1 - x) if point_present else 0)),
                    "vu_kn": -(q * arm + (p if point_present else 0)),
                }
            )
    request = {
        "schema_version": "is456-cantilever-beam-check/v1",
        "member_id": "B02",
        "analysis_revision": "B02-A1",
        "current_analysis_revision": "B02-A1",
        "reinforcement_revision": "B02-R1",
        "source_reference": "BEAM02 independent right-hand free-body equilibrium",
        "width_mm": 300,
        "depth_mm": 500,
        "fck_nmm2": 25,
        "fy_nmm2": 415,
        "clear_cover_mm": 32,
        "aggregate_size_mm": 20,
        "link_diameter_mm": 8,
        "link_spacing_mm": 250,
        "link_fy_nmm2": 415,
        "fixed_support_id": "A",
        "fixed_support_width_mm": 900,
        "free_end_mm": 2000,
        "straight_bars": {
            "start_mm": -850,
            "end_mm": 1968,
            "source_reference": "B02 straight full-span bars",
        },
        "bars": [
            {
                "bar_id": f"{face[0].upper()}{i}",
                "face": face,
                "diameter_mm": diameter,
                "x_from_left_mm": x,
                "y_from_top_mm": y,
            }
            for face, diameter, xs, y in (
                ("top", 20, (50, 150, 250), 50),
                ("bottom", 16, (50, 250), 450),
            )
            for i, x in enumerate(xs, start=1)
        ],
        "stations": [
            {"station_id": key, "x_mm": x, "side": side} for key, x, side in stations
        ],
        "combinations": [
            {
                "combination_id": combo,
                "kind": kind,
                "required_station_ids": [station for station, *_ in stations],
            }
            for combo, kind in (("UDL", "ULS"), ("POINT", "ULS"), ("S1", "SLS"))
        ],
        "actions": rows,
    }
    cases = {
        name: {"request": deepcopy(request), "ultimate_status": status}
        for name, status in (
            ("point_and_udl", "PASS"),
            ("missing_side", "HOLD"),
            ("short_anchorage", "FAIL"),
            ("missing_anchorage", "HOLD"),
            ("overload", "FAIL"),
            ("flipped_cage", "FAIL"),
            ("stale_analysis", "HOLD"),
            ("unsupported_torsion", "HOLD"),
            ("duplicate_station", "BLOCKED"),
        )
    }
    missing = cases["missing_side"]["request"]
    missing["actions"] = [
        row for row in missing["actions"] if row["row_id"] != "POINT:P-RIGHT"
    ]
    cases["short_anchorage"]["request"]["straight_bars"]["start_mm"] = -750
    cases["missing_anchorage"]["request"].pop("straight_bars")
    for name in ("overload", "flipped_cage"):
        control = cases[name]["request"]
        row = next(row for row in control["actions"] if row["row_id"] == "POINT:FIXED")
        row["mu_knm"] = -180 if name == "overload" else -100
        if name == "flipped_cage":
            for bar in control["bars"]:
                bar["face"] = "bottom" if bar["face"] == "top" else "top"
                bar["y_from_top_mm"] = 500 - bar["y_from_top_mm"]
    cases["stale_analysis"]["request"]["current_analysis_revision"] = "B02-A2"
    cases["unsupported_torsion"]["request"]["actions"][0]["tu_knm"] = 1
    duplicate = cases["duplicate_station"]["request"]["stations"]
    duplicate.append({**duplicate[1], "station_id": "P-LEFT-DUPLICATE"})

    top = section_reference(20, 3, 16, 2)
    bottom = section_reference(16, 2, 20, 3)
    assert bottom["capacity_knm"] < 100 < top["capacity_knm"] < 180
    return {
        "fixture_version": "library-029-beam02-cantilever-reference/v1",
        "sources": [
            "Independent free-body equilibrium of the segment from x to the free end.",
            "IS 456:2000 Cl. 38.1, Fig. 21–23, Annex G, Cl. 26.2, Cl. 40 and Tables 19 and 20.",
        ],
        "section": {"top": top, "bottom": bottom},
        "station_targets": {
            "UDL:FIXED": [-40, -40],
            "POINT:FIXED": [-50, -50],
            "POINT:P-LEFT": [-10, -30],
            "POINT:P-RIGHT": [-10, -20],
            "POINT:FREE": [0, 0],
        },
        "point_shear_jump_kn": 10,
        "governing_hogging_row": "POINT:FIXED",
        "governing_shear_row": "POINT:FIXED",
        "fixed_anchorage_available_mm": 850,
        "short_anchorage_available_mm": 750,
        "tolerances": {"capacity_knm": 0.02, "xu_mm": 0.01, "shear_kn": 0.01},
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    reference = fixture()
    if args.freeze:
        FIXTURE.write_text(json.dumps(reference, indent=2, allow_nan=False) + "\n")
    else:
        assert json.loads(FIXTURE.read_text()) == reference
    print(f"Independent BEAM02 reference: {len(reference['cases'])} cases")


if __name__ == "__main__":
    main()
