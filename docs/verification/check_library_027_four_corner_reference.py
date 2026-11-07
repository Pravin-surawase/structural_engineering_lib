"""Independent physical four-corner geometry and continuous section reference."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from check_library_027_references import section

FIXTURE = Path(__file__).with_name("library-027-four-corner-column.json")


def reference(data, axis):
    b, depth = data["b_mm"], data["D_mm"]
    if axis == "y":
        b, depth = depth, b
    diameter = data["longitudinal_bar_diameter_mm"]
    steel = math.pi * diameter**2
    offset = (
        data["nominal_cover_mm"]
        + data["tie_diameter_mm"]
        + diameter / 2
        + data["corner_inset_mm"]
    )
    radius = data["tie_internal_bend_radius_mm"]
    inner_offset = offset - data["nominal_cover_mm"] - data["tie_diameter_mm"]
    clearance = (
        radius - math.hypot(radius - inner_offset, radius - inner_offset) - diameter / 2
    )
    le = 0.65 * data["unsupported_length_mm"]
    emin = max(20, data["unsupported_length_mm"] / 500 + depth / 30)
    pu = data["pu_kn"]
    mu = max(data["moment_knm"], pu * emin / 1000)
    inputs = dict(
        width_mm=b,
        depth_mm=depth,
        fck_nmm2=data["fck_nmm2"],
        fy_nmm2=data["fy_nmm2"],
        neutral_axis_depth_mm=1,
        bar_layers=[
            dict(depth_from_top_mm=offset, diameters_mm=[diameter, diameter]),
            dict(depth_from_top_mm=depth - offset, diameters_mm=[diameter, diameter]),
        ],
    )

    def residual(x):
        force_n, moment_nmm = section(inputs, x)
        return moment_nmm / 1e6 - (mu / pu) * force_n / 1000

    lo, hi = 0.01 * depth, 3 * depth
    if not residual(lo) > 0 > residual(hi):
        raise ValueError("Continuous reference is not bracketed")
    for _ in range(80):
        x = (lo + hi) / 2
        if residual(x) > 0:
            lo = x
        else:
            hi = x
    xu = (lo + hi) / 2
    force, moment = section(inputs, xu)
    if abs(residual(xu)) > 1e-8:
        raise ValueError("Continuous ray intersection did not converge")
    return dict(
        supplied_steel_area_mm2=steel,
        steel_ratio=steel / (b * depth),
        bar_centroid_offset_mm=offset,
        tie_corner_clearance_mm=clearance,
        effective_length_mm=le,
        slenderness=le / depth,
        minimum_eccentricity_mm=emin,
        design_moment_knm=mu,
        maximum_tie_spacing_mm=min(b, depth, 16 * diameter, 300),
        minimum_tie_diameter_mm=max(6, diameter / 4),
        xu_mm=xu,
        continuous_pu_capacity_kn=force / 1000,
        continuous_mu_capacity_knm=moment / 1e6,
        continuous_utilization=pu / (force / 1000),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--print-expected", action="store_true")
    args = parser.parse_args()
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for axis, case in fixture["axes"].items():
        values = reference(fixture["inputs"], axis)
        if args.print_expected:
            case["expected"] = values
        else:
            for key, expected in case["expected"].items():
                if not math.isclose(
                    values[key],
                    expected,
                    abs_tol=fixture["reference_abs_tolerances"][key],
                    rel_tol=0,
                ):
                    raise ValueError(f"{axis}.{key} differs from the frozen reference")
            print("PASS independent four-corner axis", axis)
    if args.print_expected:
        print(json.dumps(fixture, indent=2))


if __name__ == "__main__":
    main()
