"""Replay the four LIB-9 section references with Python's standard library.

This evidence tool imports neither calculation engine. With --print-expected,
emit freshly derived values without reading either engine's recorded outputs.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "library-027-comparator-reference.json"
BASELINE = HERE / "library-027-comparator-baseline.json"


def circle_area(diameter):
    return math.pi * diameter**2 / 4


def steel_stress(strain, fy):
    design = fy / 1.15
    es = 200_000
    # Interpolate in strain between the normalized Fig. 23A design points.
    offsets = (0, 0.0001, 0.0003, 0.0007, 0.001, 0.002)
    stresses = tuple(design * r for r in (0.8, 0.85, 0.9, 0.95, 0.975, 1))
    strains = (0.0,) + tuple(s / es + p for s, p in zip(stresses, offsets))
    levels = (0.0,) + stresses
    e = abs(strain)
    for i, high in enumerate(strains[1:]):
        if e <= high:
            f = (e - strains[i]) / (high - strains[i])
            return math.copysign(levels[i] + f * (levels[i + 1] - levels[i]), strain)
    return math.copysign(design, strain)


def concrete_stress(strain, fck):
    e = min(1.0, max(0.0, strain / 0.002))
    return (0.67 * fck / 1.5) * (2 * e - e**2)


def simpson(fn, lo, hi):
    return (hi - lo) * (fn(lo) + 4 * fn((lo + hi) / 2) + fn(hi)) / 6


def section(data, xu, *, rounded_beam_block=False):
    depth, b = data["depth_mm"], data["width_mm"]
    fck, fy = data["fck_nmm2"], data["fy_nmm2"]
    bf = data.get("flange_width_mm", b)
    df = data.get("flange_thickness_mm", depth)
    is_column = "neutral_axis_depth_mm" in data
    top = 0.0035
    if is_column and xu > depth:
        # Independently solve the Cl. 39.1(b) top/far constraint.
        top /= 1 + 0.75 * (1 - depth / xu)

    def strain(y):
        return top * (1 - y / xu)

    def stress(y):
        return concrete_stress(strain(y), fck)

    # Piecewise quadratic concrete; Simpson integrates both the force and
    # the cubic moment integrand exactly on each interval (up to roundoff).
    if rounded_beam_block:
        if xu > df:
            raise ValueError("Frozen beam reference requires xu within the flange")
        fc = 0.36 * fck * bf * xu
        mc = fc * (depth / 2 - 0.42 * xu)
    else:
        stops = sorted(
            {0.0, min(xu, depth), min(df, xu, depth), xu * (1 - 0.002 / top)}
        )
        stops = [y for y in stops if 0 <= y <= min(xu, depth)]
        fc = mc = 0.0
        for lo, hi in zip(stops, stops[1:]):
            width = bf if (lo + hi) / 2 <= df else b
            fc += width * simpson(stress, lo, hi)
            mc += width * simpson(lambda y: stress(y) * (depth / 2 - y), lo, hi)

    force, moment = fc, mc
    for layer in data["bar_layers"]:
        y = layer["depth_from_top_mm"]
        area = math.fsum(map(circle_area, layer["diameters_mm"]))
        net = area * (steel_stress(strain(y), fy) - stress(y))
        force += net
        moment += net * (depth / 2 - y)
    return force, moment


def beam(data, *, rounded_beam_block):
    tension = [
        (r["depth_from_top_mm"], math.fsum(map(circle_area, r["diameters_mm"])))
        for r in data["bar_layers"]
        if r["face"] == "bottom"
    ]
    ast = math.fsum(a for _, a in tension)
    d = math.fsum(y * a for y, a in tension) / ast
    lo, hi = 0.000001, d
    if section(data, lo, rounded_beam_block=rounded_beam_block)[0] >= 0:
        raise ValueError("Lower bound is not tension controlled")
    # The frozen flanged case has xu within the flange for either method.
    if "flange_thickness_mm" in data:
        hi = min(hi, data["flange_thickness_mm"])
    if section(data, hi, rounded_beam_block=rounded_beam_block)[0] <= 0:
        raise ValueError("Upper bound does not bracket equilibrium")
    for _ in range(64):
        xu = (lo + hi) / 2
        force, _ = section(data, xu, rounded_beam_block=rounded_beam_block)
        if force < 0:
            lo = xu
        else:
            hi = xu
    xu = (lo + hi) / 2
    force, mu = section(data, xu, rounded_beam_block=rounded_beam_block)
    if abs(force) > 0.001:
        raise ValueError("Beam reference did not satisfy force equilibrium")

    b = data["width_mm"]
    pt = 100 * ast / (b * d)
    link = data["shear_links"]
    link_area = link["active_legs"] * circle_area(link["diameter_mm"])
    fy = min(415, link["fy_nmm2"])
    if rounded_beam_block:
        (p0, t0), (p1, t1) = data["shear_table_19_bracket"]
        if not p0 <= pt <= p1:
            raise ValueError(
                "Reinforcement percentage outside the frozen Table 19 bracket"
            )
        tau = t0 + (t1 - t0) * (pt - p0) / (p1 - p0)
        link_stress = 0.87 * fy
    else:
        beta = max(1.0, 0.8 * data["fck_nmm2"] / (6.89 * pt))
        tau = (
            0.85
            * math.sqrt(0.8 * data["fck_nmm2"])
            * (math.sqrt(1 + 5 * beta) - 1)
            / (6 * beta)
        )
        link_stress = fy / 1.15
    vc = tau * b * d / 1000
    vs = link_stress * link_area * d / link["spacing_mm"] / 1000
    max_shear = data["shear_table_20_max_nmm2"] * b * d / 1000
    if vc + vs >= max_shear:
        raise ValueError("Frozen comparator case must be below the Table 20 cap")
    return dict(
        xu_mm=xu,
        d_mm=d,
        pt_percent=pt,
        mu_knm=mu / 1e6,
        vuc_kn=vc,
        vus_kn=vs,
        shear_total_kn=vc + vs,
    )


def reference(case):
    data = case["inputs"]
    if "neutral_axis_depth_mm" not in data:
        return {
            "rcdesign": beam(data, rounded_beam_block=False),
            "structlib": beam(data, rounded_beam_block=True),
        }
    xu = data["neutral_axis_depth_mm"]
    p, m = section(data, xu)
    return {
        "shared": {"xu_mm": xu, "axial_kn": p / 1000, "centroid_moment_knm": m / 1e6}
    }


def check(label, observed, expected, tolerances):
    for field, target in expected.items():
        actual = observed[field]
        if not math.isclose(actual, target, abs_tol=tolerances[field], rel_tol=0.0):
            raise ValueError(f"{label}.{field}: {actual} differs from {target}")


def check_inputs(frozen, baseline):
    """The baseline uses web_width_mm for the flanged beam."""
    for field, observed in baseline.items():
        key = "width_mm" if field == "web_width_mm" else field
        expected = frozen[key]
        if field == "bar_layers":
            expected = [
                {k: v for k, v in layer.items() if k != "face"} for layer in expected
            ]
        if field == "shear_links":
            expected = {k: expected[k] for k in observed}
        if expected != observed:
            raise ValueError(f"Observed input {field} differs from frozen reference")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--print-expected", action="store_true")
    args = parser.parse_args()
    fixture = json.loads(FIXTURE.read_text())
    cases = fixture["cases"]
    derived = {case["id"]: reference(case) for case in cases}
    if args.print_expected:
        print(json.dumps(derived, indent=2, allow_nan=False))
        return
    baseline = {case["id"]: case for case in json.loads(BASELINE.read_text())["cases"]}
    if set(derived) != set(baseline) or len(cases) != 4 or len(derived) != 4:
        raise ValueError("Expected four distinct matching case IDs")
    for case in cases:
        key = case["id"]
        refs = derived[key]
        frozen = case["expected"]
        if refs.keys() != frozen.keys():
            raise ValueError(f"{key} reference method mismatch")
        for method, values in refs.items():
            if values.keys() != frozen[method].keys():
                raise ValueError(f"{key}/{method} reference metric mismatch")
            check(
                f"{key}/{method}/regenerate",
                values,
                frozen[method],
                dict.fromkeys(values, 1e-9),
            )
        recorded = baseline[key]
        check_inputs(case["inputs"], recorded["inputs"])
        lib = recorded["structlib_outputs"]
        acceptance = fixture["acceptance"]
        tol = acceptance["absolute_tolerances"]
        if "shared" in refs:
            if (
                case["inputs"]["neutral_axis_depth_mm"]
                != acceptance["column_fixed_xu_mm_exact"]
            ):
                raise ValueError("Prescribed column depth mismatch")
            check(
                f"{key}/rcdesign", recorded["rcdesign_outputs"], frozen["shared"], tol
            )
            for mesh in ("experimental_200", "experimental_2000"):
                observed = dict(
                    lib[mesh], xu_mm=recorded["inputs"]["neutral_axis_depth_mm"]
                )
                check(f"{key}/{mesh}", observed, frozen["shared"], tol)
        else:
            check(
                f"{key}/rcdesign", recorded["rcdesign_outputs"], frozen["rcdesign"], tol
            )
            check(
                f"{key}/structlib",
                lib["public_component_results"],
                frozen["structlib"],
                tol,
            )
            if abs(lib["force_residual_n"]) > acceptance["beam_force_residual_n_max"]:
                raise ValueError(f"{key}: recorded beam force equilibrium failed")
        print(f"PASS {key}")


if __name__ == "__main__":
    main()
