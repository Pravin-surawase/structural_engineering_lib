"""Replay the independent COL02 fixed-load reference without the library."""

from __future__ import annotations

import json
import math
from pathlib import Path

from check_library_027_references import section

FIXTURE = Path(__file__).with_name("library-029-col02-rectangular-column.json")


def axis_reference(inputs, bars, axis):
    width, depth, coordinate = (
        (inputs["b_mm"], inputs["D_mm"], 1)
        if axis == "x"
        else (inputs["D_mm"], inputs["b_mm"], 0)
    )
    data = {
        "width_mm": width,
        "depth_mm": depth,
        "fck_nmm2": inputs["fck_nmm2"],
        "fy_nmm2": inputs["fy_nmm2"],
        "neutral_axis_depth_mm": 1,
        "bar_layers": [
            {
                "depth_from_top_mm": bar[coordinate],
                "diameters_mm": [inputs["longitudinal_bar_diameter_mm"]],
            }
            for bar in bars.values()
        ],
    }
    target_n = inputs["pu_kn"] * 1000
    lo, hi = 0.01, depth
    if not section(data, lo)[0] < target_n < section(data, hi)[0]:
        raise ValueError(
            "COL02 reference plane is outside the partial-compression interval"
        )
    for _ in range(60):
        xu = (lo + hi) / 2
        if section(data, xu)[0] < target_n:
            lo = xu
        else:
            hi = xu
    xu = (lo + hi) / 2
    force, moment = section(data, xu)
    return {
        "xu_mm": xu,
        "axial_residual_kn": (force - target_n) / 1000,
        "capacity_knm": moment / 1e6,
    }


def verify(fixture):
    inputs = fixture["inputs"]
    b, depth = inputs["b_mm"], inputs["D_mm"]
    pu = inputs["pu_kn"]
    emin_x = max(20, inputs["unsupported_length_mm"] / 500 + depth / 30)
    emin_y = max(20, inputs["unsupported_length_mm"] / 500 + b / 30)
    tolerance = fixture["reference_absolute_tolerance"]

    def near(actual, expected):
        if not math.isclose(actual, expected, abs_tol=tolerance, rel_tol=0):
            raise ValueError(f"{actual:.15g} differs from {expected:.15g}")

    for name, case in fixture["layouts"].items():
        bars = case["bars_from_left_top_mm"]
        axes = {axis: axis_reference(inputs, bars, axis) for axis in ("x", "y")}
        for axis, values in axes.items():
            for field, value in values.items():
                near(value, case["axes"][axis][field])

        asc = len(bars) * math.pi * inputs["longitudinal_bar_diameter_mm"] ** 2 / 4
        ac = b * depth - asc
        puz = (0.45 * inputs["fck_nmm2"] * ac + 0.75 * inputs["fy_nmm2"] * asc) / 1000
        alpha = min(2.0, max(1.0, 1 + (pu / puz - 0.2) / 0.6))
        near(asc, case["steel_area_mm2"])
        near(puz, case["puz_kn"])
        near(alpha, case["alpha_n"])
        cap_x, cap_y = axes["x"]["capacity_knm"], axes["y"]["capacity_knm"]
        for action, pair in fixture["actions_knm"].items():
            mx, my = pair
            interaction = (abs(mx) / cap_x) ** alpha + (abs(my) / cap_y) ** alpha
            minimum_x = pu * emin_x / 1000 / cap_x
            minimum_y = pu * emin_y / 1000 / cap_y
            utilization = max(interaction, minimum_x, minimum_y)
            expected = case["actions"][action]
            near(interaction, expected["interaction_ratio"])
            near(utilization, expected["governing_ratio"])
            assert expected["strength_status"] == (
                "PASS" if utilization <= 1 else "FAIL"
            )
        print(f"PASS independent COL02 {name}")


if __name__ == "__main__":
    verify(json.loads(FIXTURE.read_text(encoding="utf-8")))
