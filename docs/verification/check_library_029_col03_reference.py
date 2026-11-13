"""Independent fixed-Pu reference using horizontal-strip quadrature."""

from __future__ import annotations

import argparse
import json
import math
from functools import cache
from pathlib import Path

from check_library_027_references import concrete_stress, steel_stress

FIXTURE = Path(__file__).with_name("library-029-col03-mixed-column.json")


def resultants(data, theta, xu):
    """Integrate along horizontal strips split at the strain transitions."""
    geometry, materials = data["geometry"], data["materials"]
    b, depth = geometry["b_mm"], geometry["D_mm"]
    fck, fy = materials["fck_nmm2"], materials["fy_nmm2"]
    nx, ny = math.cos(theta), math.sin(theta)
    q_max = max(0, nx * b) + max(0, ny * depth)
    projected = abs(nx * b) + abs(ny * depth)
    top = 0.0035 if xu <= projected else 0.0035 / (1 + 0.75 * (1 - projected / xu))
    levels = (q_max - xu, q_max - xu * (1 - 0.002 / top))

    def strain(x, y):
        return top * (1 - (q_max - nx * x - ny * y) / xu)

    def row(y):
        x_breaks = sorted(
            {
                0,
                b,
                *(
                    (q - ny * y) / nx
                    for q in levels
                    if abs(nx) > 1e-12 and 0 < (q - ny * y) / nx < b
                ),
            }
        )
        force = my = 0.0
        for left, right in zip(x_breaks[:-1], x_breaks[1:], strict=True):
            midpoint = (left + right) / 2
            for x, weight in ((left, 1), (midpoint, 4), (right, 1)):
                term = concrete_stress(strain(x, y), fck) * weight * (right - left) / 6
                force += term
                my += term * (b / 2 - x)
        return force, force * (depth / 2 - y), my

    y_breaks = sorted(
        {
            0,
            depth,
            *(
                (q - nx * x) / ny
                for q in levels
                for x in (0, b)
                if abs(ny) > 1e-12 and 0 < (q - nx * x) / ny < depth
            ),
        }
    )
    p = mx = my = 0.0
    gaussian = ((-math.sqrt(3 / 5), 5 / 9), (0, 8 / 9), (math.sqrt(3 / 5), 5 / 9))
    for low, high in zip(y_breaks[:-1], y_breaks[1:], strict=True):
        half, middle = (high - low) / 2, (high + low) / 2
        for node, weight in gaussian:
            axial, x_moment, y_moment = row(middle + half * node)
            p += half * weight * axial
            mx += half * weight * x_moment
            my += half * weight * y_moment
    for bar in data["reinforcement"]["bars"]:
        x, y, diameter = bar["x_from_left_mm"], bar["y_from_top_mm"], bar["diameter_mm"]
        e = strain(x, y)
        net = (
            math.pi
            * (diameter / 2) ** 2
            * (steel_stress(e, fy) - concrete_stress(e, fck))
        )
        p += net
        mx += net * (depth / 2 - y)
        my += net * (b / 2 - x)
    return p / 1000, mx / 1e6, my / 1e6


def reference(data, *, samples):
    geometry, actions, materials = (
        data[key] for key in ("geometry", "actions", "materials")
    )
    b, depth = geometry["b_mm"], geometry["D_mm"]
    pu, mx, my = actions["pu_kn"], actions["mx_knm"], actions["my_knm"]

    @cache
    def plane(theta):
        span = abs(b * math.cos(theta)) + abs(depth * math.sin(theta))
        lo, hi = 1e-6 * span, 256 * span
        if not resultants(data, theta, lo)[0] < pu < resultants(data, theta, hi)[0]:
            raise ValueError("Reference axial root is unbracketed")
        for _ in range(44):
            mid = (lo + hi) / 2
            if resultants(data, theta, mid)[0] < pu:
                lo = mid
            else:
                hi = mid
        xu = (lo + hi) / 2
        return xu, *resultants(data, theta, xu)

    angles = [2 * math.pi * k / samples for k in range(samples + 1)]

    def ray(dx, dy):
        magnitude = math.hypot(dx, dy)
        dx, dy = dx / magnitude, dy / magnitude

        def cross(theta):
            _, _, x, y = plane(theta)
            return -dy * x + dx * y

        positive = []
        candidates = [theta for theta in angles[:-1] if abs(cross(theta)) < 1e-8]
        for low, high in zip(angles[:-1], angles[1:], strict=True):
            low_value, high_value = cross(low), cross(high)
            if (
                abs(low_value) < 1e-8
                or abs(high_value) < 1e-8
                or low_value * high_value > 0
            ):
                continue
            for _ in range(37):
                middle = (low + high) / 2
                middle_value = cross(middle)
                if middle_value * low_value <= 0:
                    high = middle
                else:
                    low, low_value = middle, middle_value
            candidates.append((low + high) / 2)
        for theta in candidates:
            xu, p, x, y = plane(theta)
            if x * dx + y * dy > 0:
                positive.append(
                    {
                        "normal_deg": math.degrees(theta) % 360,
                        "xu_mm": xu,
                        "p_kn": p,
                        "mx_knm": x,
                        "my_knm": y,
                        "capacity_knm": x * dx + y * dy,
                        "axial_residual_kn": p - pu,
                        "transverse_residual_knm": -dy * x + dx * y,
                    }
                )
        if len(positive) != 1:
            raise ValueError(f"Reference ray has {len(positive)} positive roots")
        return positive[0]

    directions = {
        "x_positive": (1, 0),
        "x_negative": (-1, 0),
        "y_positive": (0, 1),
        "y_negative": (0, -1),
    }
    axes = {name: ray(*direction) for name, direction in directions.items()}
    demand = ray(mx, my)
    steel = sum(
        math.pi * bar["diameter_mm"] ** 2 / 4 for bar in data["reinforcement"]["bars"]
    )
    puz = (
        0.45 * materials["fck_nmm2"] * (b * depth - steel)
        + 0.75 * materials["fy_nmm2"] * steel
    ) / 1000
    alpha = max(1, min(2, 1 + (pu / puz - 0.2) / 0.6))
    cap_x = axes["x_positive" if mx >= 0 else "x_negative"]["capacity_knm"]
    cap_y = axes["y_positive" if my >= 0 else "y_negative"]["capacity_knm"]
    contour = (abs(mx) / cap_x) ** alpha + (abs(my) / cap_y) ** alpha
    direct = math.hypot(mx, my) / demand["capacity_knm"]
    minimum = {}
    for axis, dimension in (("x", depth), ("y", b)):
        eccentricity = max(20, geometry["unsupported_length_mm"] / 500 + dimension / 30)
        adverse = min(
            axes[f"{axis}_positive"]["capacity_knm"],
            axes[f"{axis}_negative"]["capacity_knm"],
        )
        minimum[axis] = pu * eccentricity / 1000 / adverse
    governing = max(contour, direct, *minimum.values())
    return {
        "steel_area_mm2": steel,
        "puz_kn": puz,
        "alpha_n": alpha,
        "axes": axes,
        "demand": demand,
        "contour_ratio": contour,
        "direct_ratio": direct,
        "minimum_eccentricity_ratios": minimum,
        "governing_ratio": governing,
        "strength_status": "PASS" if governing <= 1 else "FAIL",
    }


def verify_values(actual, expected, prefix):
    if isinstance(expected, dict):
        for key, value in expected.items():
            verify_values(actual[key], value, f"{prefix}.{key}")
    elif isinstance(expected, str):
        if actual != expected:
            raise ValueError(f"{prefix} differs from its frozen disposition")
    else:
        difference = abs(actual - expected)
        if prefix.endswith("normal_deg"):
            difference = abs((actual - expected + 180) % 360 - 180)
        if difference > 0.000001:
            raise ValueError(f"{prefix} differs by {difference:g}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--derive", action="store_true")
    args = parser.parse_args()
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for name, case in fixture["cases"].items():
        reference_values = reference(case["request"], samples=64)
        verify_values(reference(case["request"], samples=32), reference_values, name)
        if args.derive:
            case["expected"] = reference_values
        else:
            verify_values(reference_values, case["expected"], name)
            print(f"PASS independent COL03 {name}")
    if args.derive:
        print(json.dumps(fixture, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
