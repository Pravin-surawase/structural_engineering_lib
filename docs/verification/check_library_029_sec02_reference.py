"""Freeze independent signed interaction slices and elastic section properties."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

from check_library_029_col03_reference import reference as rectangular_reference
from check_library_029_col05_reference import _capacity_model

ROOT = Path(__file__).parent
FIXTURE = ROOT / "library-029-sec02-column-interaction.json"


def properties(section, bars, modular_ratio):
    if section["shape"] == "rectangular":
        b, h = section["b_mm"], section["D_mm"]
        area, ix, iy = b * h, b * h**3 / 12, h * b**3 / 12
    else:
        b = h = section["diameter_mm"]
        area, ix, iy = math.pi * b**2 / 4, math.pi * b**4 / 64, math.pi * b**4 / 64
    additions = [
        (
            (modular_ratio - 1) * math.pi * bar["diameter_mm"] ** 2 / 4,
            (modular_ratio - 1) * math.pi * bar["diameter_mm"] ** 4 / 64,
            bar["x_from_left_mm"],
            bar["y_from_top_mm"],
        )
        for bar in bars
    ]
    transformed = area + sum(a for a, _, _, _ in additions)
    x = (area * b / 2 + sum(a * x for a, _, x, _ in additions)) / transformed
    y = (area * h / 2 + sum(a * y for a, _, _, y in additions)) / transformed
    return {
        "gross": {
            "area_mm2": area,
            "cx_mm": b / 2,
            "cy_mm": h / 2,
            "ix_mm4": ix,
            "iy_mm4": iy,
            "ixy_mm4": 0.0,
        },
        "transformed": {
            "area_mm2": transformed,
            "cx_mm": x,
            "cy_mm": y,
            "ix_mm4": ix
            + area * (h / 2 - y) ** 2
            + sum(i + a * (by - y) ** 2 for a, i, _, by in additions),
            "iy_mm4": iy
            + area * (b / 2 - x) ** 2
            + sum(i + a * (bx - x) ** 2 for a, i, bx, _ in additions),
            "ixy_mm4": area * (b / 2 - x) * (h / 2 - y)
            + sum(a * (bx - x) * (by - y) for a, _, bx, by in additions),
        },
    }


def fixture():
    positions = json.loads(
        (ROOT / "library-029-col02-rectangular-column.json").read_text()
    )["layouts"]["eight_bar"]["bars_from_left_top_mm"]
    bars = [
        {
            "bar_id": key,
            "x_from_left_mm": x,
            "y_from_top_mm": y,
            "diameter_mm": 20,
            "row": "outer",
        }
        for key, (x, y) in positions.items()
    ]
    common = {
        "identity": {
            "family_id": "column",
            "case_id": "SEC02-R",
            "source_reference": "SEC02 independent signed rays",
        },
        "geometry": {"shape": "rectangular", "b_mm": 300, "D_mm": 400},
        "bars": bars,
        "materials": {"fck_nmm2": 25, "fy_nmm2": 415},
        "pu_kn": 500,
        "modular_ratio": 8,
        "point_count": 8,
    }
    circle = deepcopy(common)
    circle["identity"]["case_id"] = "SEC02-C"
    circle["geometry"] = {"shape": "circular", "diameter_mm": 450}
    circle["materials"] = {"fck_nmm2": 30, "fy_nmm2": 500}
    circle["bars"] = [
        {
            "bar_id": f"B{index + 1:02d}",
            "diameter_mm": 20,
            "row": "outer",
            "x_from_left_mm": 225 + 165 * math.cos(math.pi * index / 4),
            "y_from_top_mm": 225 + 165 * math.sin(math.pi * index / 4),
        }
        for index in range(8)
    ]
    cases = {}
    axial_cases = {"rectangle": common, "circle": circle}
    for shape, request in (("rectangle", common), ("circle", circle)):
        for suffix, axial in (("zero_axial", 0), ("tension", -100)):
            case = deepcopy(request)
            case["identity"]["case_id"] += f"-{suffix}"
            case["pu_kn"] = axial
            axial_cases[f"{shape}_{suffix}"] = case
    for name, request in axial_cases.items():
        geometry = request["geometry"]
        fck, fy = request["materials"].values()
        is_circular = geometry["shape"] == "circular"
        axial = request["pu_kn"]
        if is_circular:
            circle_ray = _capacity_model(450, fck, fy, axial, 8, 20, 165, 0, 96)
        rays = []
        for degrees in range(0, 360, 45):
            angle = math.radians(degrees)
            mx, my = math.cos(angle), math.sin(angle)
            if is_circular:
                ray = {"p_kn": axial, **circle_ray(mx, my)}
            else:
                ray = rectangular_reference(
                    {
                        "geometry": {**geometry, "unsupported_length_mm": 3000},
                        "materials": request["materials"],
                        "actions": {"pu_kn": axial, "mx_knm": mx, "my_knm": my},
                        "reinforcement": {"bars": request["bars"]},
                    },
                    samples=96,
                )["demand"]
            rays.append({"angle_deg": degrees, **ray})
        cases[name] = {
            "request": request,
            "properties": properties(geometry, request["bars"], 8),
            "rays": rays,
        }
    high = deepcopy(common)
    high["pu_kn"] = 3500
    cases["above_compression_domain"] = {"request": high, "status": "HOLD"}
    tension = deepcopy(circle)
    tension["identity"]["case_id"] = "SEC02-C-tension-limit"
    tension["pu_kn"] = -1200
    assert -tension["pu_kn"] > 8 * math.pi * 20**2 / 4 * 500 / 1.15 / 1000
    cases["beyond_tension_domain"] = {"request": tension, "status": "HOLD"}
    return {
        "fixture_version": "library-029-sec02-column-interaction-reference/v1",
        "sources": [
            "COL02 actual rectangle and COL05 actual circular ring",
            "Independent rectangular strip and analytic circular chord integration.",
            "Gross elastic geometry and explicit transformed-section parallel-axis arithmetic.",
        ],
        "tolerances": {
            "moment_knm": 0.02,
            "axial_kn": 0.01,
            "angle_deg": 0.02,
            "axis_mm": 0.02,
        },
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
    print(f"Independent SEC02 reference: {len(reference['cases'])} cases")


if __name__ == "__main__":
    main()
