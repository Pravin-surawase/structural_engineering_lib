"""Regenerate the source-derived WP01 vectors; requires SciPy only for this tool.

No production library imports. IS 456:2000 38.1 / Fig 21-23 / Annex G.
Run with --write to replace the retained reference, otherwise print its summary.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import quad
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[4]
TARGET = ROOT / "contracts/structural-engineering/conformance/wp01-per-bar-vectors.json"


def solve(request, *, integrated=False):
    fy, fck = (
        request["steel_yield_strength_n_per_mm2"],
        request["concrete_strength_n_per_mm2"],
    )
    width, height = request["web_width_mm"], request["depth_mm"]
    design_strength = fy / 1.15
    fractions = np.array([0, 0.8, 0.85, 0.9, 0.95, 0.975, 1])
    stresses = fractions * design_strength
    strains = stresses / 200000 + np.array([0, 0, 0.0001, 0.0003, 0.0007, 0.001, 0.002])
    if fy == 250:
        stresses = np.array([0, design_strength])
        strains = stresses / 200000
    bars = request["bars"]
    areas = np.array([math.pi * bar["diameter_mm"] ** 2 / 4 for bar in bars])
    depths = np.array(
        [
            (
                bar["y_from_top_mm"]
                if request["tension_face"] == "bottom"
                else height - bar["y_from_top_mm"]
            )
            for bar in bars
        ]
    )

    def steel(x):
        strain = 0.0035 * (x - depths) / x
        stress = np.sign(strain) * np.interp(abs(strain), strains, stresses)
        concrete = 0.67 * fck / 1.5 * (1 - (1 - np.clip(strain / 0.002, 0, 1)) ** 2)
        return strain, stress, concrete, areas * (stress - concrete)

    def concrete(x):
        if integrated:

            def stress(y):
                ratio = min(1, 0.0035 * (x - y) / x / 0.002)
                return 0.67 * fck / 1.5 * (1 - (1 - ratio) ** 2)

            force = width * quad(stress, 0, x, points=[3 * x / 7], epsabs=1e-8)[0]
            first = (
                width
                * quad(lambda y: stress(y) * y, 0, x, points=[3 * x / 7], epsabs=1e-8)[
                    0
                ]
            )
            return force, first
        flanged = (
            request["section_kind"] != "rectangular"
            and request["tension_face"] == "bottom"
        )
        if not flanged:
            force = 0.36 * fck * width * x
            return force, force * 0.42 * x
        flange, thickness = request["flange_width_mm"], request["flange_thickness_mm"]
        if x <= thickness:
            force = 0.36 * fck * flange * x
            return force, force * 0.42 * x
        equivalent = min(thickness, 0.15 * x + 0.65 * thickness)
        web_force, flange_force = (
            0.36 * fck * width * x,
            0.45 * fck * (flange - width) * equivalent,
        )
        return (
            web_force + flange_force,
            web_force * 0.42 * x + flange_force * equivalent / 2,
        )

    axis = brentq(lambda x: concrete(x)[0] + sum(steel(x)[3]), 1e-6, height, xtol=1e-12)
    strain, stress, displaced, forces = steel(axis)
    moment = -(concrete(axis)[1] + sum(forces * depths)) / 1e6
    minimum_strain = fy / (1.15 * 200000) + 0.002
    return {
        "neutral_axis_depth_mm": axis,
        "capacity_knm": moment,
        "engineering": "pass" if max(-strain) >= minimum_strain else "fail",
        "force_residual_n": float(concrete(axis)[0] + sum(forces)),
        "maximum_tension_strain": float(max(-strain)),
        "minimum_tension_strain": minimum_strain,
        "bar_responses": [
            {
                "bar_id": bar["bar_id"],
                "depth_from_compression_face_mm": float(depth),
                "area_mm2": float(area),
                "strain": float(e),
                "steel_stress_n_per_mm2": float(s),
                "displaced_concrete_stress_n_per_mm2": float(c),
                "net_force_n": float(force),
            }
            for bar, depth, area, e, s, c, force in zip(
                bars, depths, areas, strain, stress, displaced, forces, strict=True
            )
        ],
    }


def request_for(fy=415, fck=25, bottom_diameter=25, mirror=False):
    bars = []
    for face, rows in (
        ("bottom", [(bottom_diameter, 450), (bottom_diameter, 375)]),
        ("top", [(16, 50), (12, 125)]),
    ):
        for layer, (diameter, y) in enumerate(rows, 1):
            for position, x in enumerate([50, 250], 1):
                bars.append(
                    {
                        "bar_id": f"{face[0].upper()}{(layer-1)*2+position}",
                        "diameter_mm": diameter,
                        "x_from_left_mm": x,
                        "y_from_top_mm": 500 - y if mirror else y,
                        "face": (
                            {"top": "bottom", "bottom": "top"}[face] if mirror else face
                        ),
                        "layer": layer,
                    }
                )
    return {
        "profile_id": "LIB-MEMBER-WORKFLOW-002",
        "section_kind": "rectangular",
        "web_width_mm": 300,
        "depth_mm": 500,
        "concrete_strength_n_per_mm2": fck,
        "steel_yield_strength_n_per_mm2": fy,
        "bars": bars,
        "tension_face": "top" if mirror else "bottom",
    }


def build():
    vectors = []

    def add(name, request):
        vectors.append({"id": name, "input": request, "expected": solve(request)})

    for fy in [250, 415, 500]:
        for diameter in [20, 25, 32]:
            for mirror in [False, True]:
                add(
                    f"fe{fy}-bottom{diameter}-{'top' if mirror else 'bottom'}",
                    request_for(fy, 25, diameter, mirror),
                )
    for fck in [20, 40]:
        for mirror in [False, True]:
            add(
                f"m{fck}-{'top' if mirror else 'bottom'}",
                request_for(fck=fck, mirror=mirror),
            )
    reverse = request_for()
    reverse["tension_face"] = "top"
    add("same-arrangement-reverse-bending", reverse)
    for kind, thickness in [("t_beam", 100), ("l_beam", 40)]:
        flange = request_for()
        flange.update(
            section_kind=kind, flange_width_mm=800, flange_thickness_mm=thickness
        )
        add(kind, flange)
    single = request_for()
    single["profile_id"] = "LIB-MEMBER-WORKFLOW-001"
    single["bars"] = [
        dict(bar, diameter_mm=20 if bar["face"] == "bottom" else 12)
        for bar in single["bars"]
        if bar["layer"] == 1
    ]
    add("workflow-001", single)
    singly = dict(
        single, bars=[bar for bar in single["bars"] if bar["face"] == "bottom"]
    )
    add("singly-reinforced", singly)
    case = request_for()
    design, integrated = solve(case), solve(case, integrated=True)
    return {
        "schema_version": "wp01-per-bar-reference/v1",
        "generator": str(Path(__file__).relative_to(ROOT)),
        "source": "IS 456:2000 38.1 / Fig 21-23 / Annex G; controlled PDF SHA256 964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264",
        "solver": f"SciPy {scipy.__version__} brentq; independent NumPy interpolation; no production imports",
        "tolerances": {
            "axis_mm": 1e-7,
            "moment_knm": 1e-7,
            "stress_n_per_mm2": 1e-6,
            "force_n": 1e-6,
        },
        "design_block_comparison": {
            "design_block_capacity_knm": design["capacity_knm"],
            "integrated_fig21_capacity_knm": integrated["capacity_knm"],
            "difference_percent": 100
            * (design["capacity_knm"] / integrated["capacity_knm"] - 1),
            "meaning": "Different concrete-block approximations, not an identical-model comparison",
        },
        "vectors": vectors,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    data = build()
    if args.write:
        TARGET.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "vectors": len(data["vectors"]),
                "comparison": data["design_block_comparison"],
            },
            indent=2,
        )
    )
