"""Reproduce column service reference values with independent strip integration."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "library-029-sec03-column-service.json"
GAUSS = (-1 / math.sqrt(3), 1 / math.sqrt(3))


def solve(matrix, vector):
    """Solve the independent finite-difference step by row reduction."""
    rows = [list(row) + [value] for row, value in zip(matrix, vector, strict=True)]
    for index in range(3):
        pivot = max(range(index, 3), key=lambda j: abs(rows[j][index]))
        rows[index], rows[pivot] = rows[pivot], rows[index]
        divisor = rows[index][index]
        rows[index] = [value / divisor for value in rows[index]]
        for j in range(3):
            if j != index:
                factor = rows[j][index]
                rows[j] = [
                    x - factor * y for x, y in zip(rows[j], rows[index], strict=True)
                ]
    return [row[-1] for row in rows]


def reference(request):
    b, h = (request["geometry"][key] for key in ("b_mm", "D_mm"))
    ec, es = (request["moduli"][key] for key in ("ec_nmm2", "es_nmm2"))
    actions = request["actions"]
    target = [
        1000 * actions["p_kn"],
        1e6 * actions["mx_knm"] / h,
        1e6 * actions["my_knm"] / b,
    ]
    bars = request["bars"]

    def ordinate(plane, x, y):
        return plane[0] + plane[1] * (0.5 - y / h) + plane[2] * (0.5 - x / b)

    def samples(plane):
        # Split at intersections with the top and bottom edges. The active
        # vertical strip bounds are then affine on each integration interval.
        cuts = [0, b]
        if plane[2]:
            for y in (0, h):
                cut = b * (0.5 + (plane[0] + plane[1] * (0.5 - y / h)) / plane[2])
                if 0 < cut < b:
                    cuts.append(cut)
        cuts.sort()
        for x0, x1 in zip(cuts[:-1], cuts[1:], strict=True):
            dx = (x1 - x0) / 2
            for u in GAUSS:
                x = (x1 + x0) / 2 + u * dx
                top, bottom = ordinate(plane, x, 0), ordinate(plane, x, h)
                if top < 0 and bottom < 0:
                    continue
                low, high = 0, h
                if top < 0:
                    low = h * top / (top - bottom)
                elif bottom < 0:
                    high = h * top / (top - bottom)
                dy = (high - low) / 2
                for v in GAUSS:
                    y = (high + low) / 2 + v * dy
                    yield x, y, dx * dy, ordinate(plane, x, y)
        for bar in bars:
            x, y = bar["x_from_left_mm"], bar["y_from_top_mm"]
            strain = ordinate(plane, x, y)
            area = math.pi * (bar["diameter_mm"] / 2) ** 2
            yield x, y, area * (es / ec - (strain >= 0)), strain

    def actions_for(plane):
        response = [0.0, 0.0, 0.0]
        for x, y, area, strain in samples(plane):
            force = ec * area * strain
            for j, factor in enumerate((1, 0.5 - y / h, 0.5 - x / b)):
                response[j] += force * factor
        return response

    plane = [1e-4, 0.0, 0.0]
    for _ in range(40):
        state = actions_for(plane)
        error = [a - v for a, v in zip(target, state, strict=True)]
        if max(map(abs, error)) < 1e-7:
            break
        delta = 1e-9
        derivatives = []
        for j in range(3):
            perturbed = plane.copy()
            perturbed[j] += delta
            derivatives.append(
                [
                    (a - v) / delta
                    for a, v in zip(actions_for(perturbed), state, strict=True)
                ]
            )
        step = solve(zip(*derivatives, strict=True), error)
        plane = [value + change for value, change in zip(plane, step, strict=True)]
    else:
        raise RuntimeError("Reference plane did not converge")

    points = list(samples(plane))
    area = math.fsum(a for _, _, a, _ in points)
    cx = math.fsum(a * x for x, _, a, _ in points) / area
    cy = math.fsum(a * y for _, y, a, _ in points) / area
    corners = [ordinate(plane, x, y) for x, y in ((0, 0), (b, 0), (b, h), (0, h))]
    return {
        "strain_at_centroid": plane[0],
        "strain_gradient_x_per_mm": -plane[2] / b,
        "strain_gradient_y_per_mm": -plane[1] / h,
        "max_concrete_compression_nmm2": ec * max(0, *corners),
        "neutral_axis_angle_deg": math.degrees(math.atan2(-plane[2] / b, plane[1] / h))
        % 180,
        "bar_strains": {
            bar["bar_id"]: ordinate(plane, bar["x_from_left_mm"], bar["y_from_top_mm"])
            for bar in bars
        },
        "properties": {
            "area_mm2": area,
            "cx_mm": cx,
            "cy_mm": cy,
            "ix_mm4": math.fsum(a * (y - cy) ** 2 for _, y, a, _ in points),
            "iy_mm4": math.fsum(a * (x - cx) ** 2 for x, _, a, _ in points),
            "ixy_mm4": math.fsum(a * (x - cx) * (y - cy) for x, y, a, _ in points),
        },
    }


def fixture():
    source = json.loads((ROOT / "library-029-col03-mixed-column.json").read_text())
    column = source["cases"]["admitted_12_bar"]["request"]
    b, h = (column["geometry"][key] for key in ("b_mm", "D_mm"))
    request = {
        "identity": {
            "family_id": "column",
            "case_id": "SEC03-S07",
            "member_id": column["identity"]["member_id"],
            "source_reference": "SEC03 COL03 positioned cage; independent strip reference",
        },
        "geometry": {"shape": "rectangular", "b_mm": b, "D_mm": h},
        "bars": column["reinforcement"]["bars"],
        "materials": column["materials"],
        "moduli": {"ec_nmm2": 5000 * math.sqrt(30), "es_nmm2": 200000},
        "concrete_linear_limit_nmm2": 12,
        "actions": {"p_kn": 300, "mx_knm": -40, "my_knm": 25},
    }
    reflected = deepcopy(request)
    reflected["identity"]["case_id"] = "SEC03-S08"
    reflected["actions"].update(mx_knm=40, my_knm=-25)
    for bar in reflected["bars"]:
        bar["x_from_left_mm"] = b - bar["x_from_left_mm"]
        bar["y_from_top_mm"] = h - bar["y_from_top_mm"]

    cases = {
        name: {"request": payload, "expected": reference(payload), "status": "PASS"}
        for name, payload in (("biaxial", request), ("reflected", reflected))
    }
    for name, actions, status in (
        ("fully_compressed", {"p_kn": 300, "mx_knm": 2, "my_knm": -1}, "PASS"),
        ("all_tension", {"p_kn": -100, "mx_knm": 0, "my_knm": 0}, "PASS"),
        ("outside_linear_range", {"p_kn": 1200, "mx_knm": -160, "my_knm": 100}, "HOLD"),
    ):
        payload = deepcopy(request)
        payload["identity"]["case_id"] = f"SEC03-{name}"
        payload["actions"] = actions
        cases[name] = {
            "request": payload,
            "expected": reference(payload),
            "status": status,
        }
    return {
        "fixture_version": "library-029-sec03-column-service-reference/v1",
        "sources": [
            "COL03 admitted twelve-bar rectangular cage and the SEC03 S07/S08 plan.",
            "Independent vertical-strip Gaussian integration and finite-difference equilibrium.",
            "Compression-positive linear concrete with zero tensile stress, centroidal steel point areas, and declared elastic range.",
            "IS 456:2000 Cl. 6.2.3.1 nominal Ec; Cl. 5.6.3 nominal Es. The concrete model limit is supplied for this study.",
        ],
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
    print(f"Independent SEC03 reference: {len(reference['cases'])} cases")


if __name__ == "__main__":
    main()
