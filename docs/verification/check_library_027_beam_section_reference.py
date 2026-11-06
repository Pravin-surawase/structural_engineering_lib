"""Replay the independent 0.27 section shear and sagging flange targets."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from check_library_027_references import check, circle_area, steel_stress

FIXTURE = Path(__file__).with_name("library-027-beam-section-closure.json")


def shear_targets(case, data):
    def resistance(group):
        if group is None:
            return 0.0
        area = sum(map(circle_area, group["diameters_mm"]))
        stress = 0.87 * min(415, group["fy_nmm2"])
        angle = math.radians(group["angle_deg"])
        spacing = group["spacing_mm"]
        if spacing is None:
            return stress * area * math.sin(angle) / 1000
        return (
            stress
            * area
            * (math.sin(angle) + math.cos(angle))
            * (data["effective_depth_mm"] / spacing)
            / 1000
        )

    bd = data["web_width_mm"] * data["effective_depth_mm"]
    stirrup = resistance(case["stirrups"])
    bent = resistance(case["bent_up_bars"])
    concrete = data["table_19_nmm2"] * bd / 1000
    limit = data["table_20_nmm2"] * bd / 1000
    credited_bent = min(stirrup, bent)
    return {
        "concrete_capacity_kn": concrete,
        "stirrup_capacity_kn": stirrup,
        "bent_up_capacity_raw_kn": bent,
        "bent_up_capacity_credited_kn": credited_bent,
        "limiting_capacity_kn": limit,
        "provided_capacity_kn": min(concrete + stirrup + credited_bent, limit),
    }


def flanged_targets(data, flange_thickness_mm):
    b, bf, fck, fy = (data[key] for key in ("bw_mm", "bf_mm", "fck_nmm2", "fy_nmm2"))
    df = flange_thickness_mm
    steel = [
        (group["y_mm"], sum(map(circle_area, group["diameters_mm"])))
        for group in data["tension_layers"]
    ]
    d = sum(y * area for y, area in steel) / sum(area for _, area in steel)

    def actions(x):
        if x <= df:
            blocks = [(0.36 * fck * bf * x, 0.42 * x)]
            branch = "within_flange"
        else:
            full = df / x <= 0.43
            yf = df if full else 0.15 * x + 0.65 * df
            blocks = [
                (0.36 * fck * b * x, 0.42 * x),
                (0.45 * fck * (bf - b) * yf, yf / 2),
            ]
            branch = "web_full_flange" if full else "web_reduced_flange"
        bar_forces = [
            (area * steel_stress(0.0035 * (1 - y / x), fy), y) for y, area in steel
        ]
        return blocks, bar_forces, branch

    def residual(x):
        blocks, bars, _ = actions(x)
        return sum(force for force, _ in blocks + bars)

    lo, hi = 0.001, 200.0
    if not residual(lo) < 0 < residual(hi) or hi >= min(y for y, _ in steel):
        raise ValueError("Reference requires tension-only bars and a bracketed root")
    for _ in range(64):
        mid = (lo + hi) / 2
        if residual(mid) < 0:
            lo = mid
        else:
            hi = mid
    if abs(residual(hi)) > 1e-6:
        return "rounded_force_gap", {}

    blocks, bars, branch = actions(hi)
    return branch, {
        "equilibrium_neutral_axis_depth_mm": hi,
        "concrete_compression_force_n": sum(force for force, _ in blocks),
        "capacity_knm": sum(force * (d - y) for force, y in blocks + bars) / 1e6,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--print-expected", action="store_true")
    args = parser.parse_args()
    fixture = json.loads(FIXTURE.read_text())
    for case in fixture["shear_cases"]:
        values = shear_targets(case, fixture["shear_section"])
        if args.print_expected:
            case["expected"] = values
        else:
            check(case["id"], values, case["expected"], fixture["shear_abs_tolerances"])
            print("PASS", case["id"])
    for case in fixture["flanged_cases"]:
        branch, values = flanged_targets(
            fixture["flanged_section"], case["flange_thickness_mm"]
        )
        if args.print_expected:
            case.update(branch=branch, expected=values)
        else:
            if branch != case["branch"]:
                raise ValueError(f"{case['id']}: wrong concrete block branch")
            check(
                case["id"], values, case["expected"], fixture["flanged_abs_tolerances"]
            )
            print("PASS", case["id"])
    if args.print_expected:
        print(json.dumps(fixture, indent=2))


if __name__ == "__main__":
    main()
