"""Freeze a prescribed finite-time multilayer beam service history."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

from check_library_029_serv01_reference import section

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "library-029-serv02-beam-history.json"


def reference(request):
    member, history = request["member"], request["history"]
    b, depth, span = member["width_mm"], member["depth_mm"], request["span_mm"]
    ec = 5000 * math.sqrt(member["fck_nmm2"])
    total = request["service_load"]["uniform_load_kn_per_m"]
    sustained = history["sustained_load"]["uniform_load_kn_per_m"]
    stiffness = section(member, 1, 0)
    tension = [bar for bar in member["bars"] if bar["face"] == "bottom"]
    ast = sum(math.pi * bar["diameter_mm"] ** 2 / 4 for bar in tension)
    asc = sum(
        math.pi * bar["diameter_mm"] ** 2 / 4
        for bar in member["bars"]
        if bar["face"] == "top"
    )
    d = (
        sum(
            math.pi * bar["diameter_mm"] ** 2 / 4 * bar["y_from_top_mm"]
            for bar in tension
        )
        / ast
    )
    pt = 100 * ast / (b * d)
    pc = 100 * asc / (b * d)
    k4 = min(1, 0.65 * (pt - pc) / math.sqrt(pt))

    def displacement(load, modulus, inertia):
        return 5 * load * span**4 / (384 * modulus * inertia)

    initial_total = displacement(total, ec, stiffness["cracked_inertia_mm4"])
    initial_sustained = displacement(sustained, ec, stiffness["cracked_inertia_mm4"])
    stages = []
    for stage in (history["at_finishes"], history["at_assessment"]):
        modulus = ec / (1 + stage["creep_coefficient"])
        cracked = section(member, 1, 0, modulus)
        sustained_deflection = displacement(
            sustained, modulus, cracked["cracked_inertia_mm4"]
        )
        shrinkage = span**2 / 8 * k4 * stage["shrinkage_strain"] / depth
        transient_deflection = initial_total - initial_sustained if stages else 0
        stages.append(
            {
                "concrete_modulus_nmm2": modulus,
                "neutral_axis_mm": cracked["neutral_axis_mm"],
                "cracked_inertia_mm4": cracked["cracked_inertia_mm4"],
                "sustained_deflection_mm": sustained_deflection,
                "shrinkage_deflection_mm": shrinkage,
                "total_deflection_mm": sustained_deflection
                + shrinkage
                + transient_deflection,
            }
        )

    final = stages[-1]
    g = (
        sustained
        * span**2
        / 8
        / (final["concrete_modulus_nmm2"] * final["cracked_inertia_mm4"])
    )
    q = (total - sustained) * span**2 / 8 / (ec * stiffness["cracked_inertia_mm4"])
    axis = (g * final["neutral_axis_mm"] + q * stiffness["neutral_axis_mm"]) / (g + q)
    epsilon = (g + q) * (depth - axis)
    covers = [depth - bar["y_from_top_mm"] - bar["diameter_mm"] / 2 for bar in tension]
    acr = min(
        math.hypot(bar["x_from_left_mm"], depth - bar["y_from_top_mm"])
        - bar["diameter_mm"] / 2
        for bar in tension
    )
    width = 3 * acr * epsilon / (1 + 2 * (acr - min(covers)) / (depth - axis))
    return {
        "initial_total_mm": initial_total,
        "initial_sustained_mm": initial_sustained,
        "at_finishes": stages[0],
        "at_assessment": final,
        "after_finishes_mm": final["total_deflection_mm"]
        - stages[0]["total_deflection_mm"],
        "flexural_neutral_axis_mm": axis,
        "flexural_surface_strain": epsilon,
        "flexural_width_mm": width,
    }


def continuous_reference(request):
    member, history = request["member"], request["history"]
    span, depth = request["span_mm"], member["depth_mm"]
    total = request["service_load"]["uniform_load_kn_per_m"]
    sustained = history["sustained_load"]["uniform_load_kn_per_m"]
    ec = 5000 * math.sqrt(member["fck_nmm2"])
    fraction = (1 + math.sqrt(33)) / 16
    coefficient = fraction / 48 - fraction**3 / 16 + fraction**4 / 24
    instant = section(member, 1, 0)
    ei = ec * instant["cracked_inertia_mm4"]
    first_total = coefficient * total * span**4 / ei
    first_sustained = coefficient * sustained * span**4 / ei
    stages = {}
    for key in ("at_finishes", "at_assessment"):
        age = history[key]
        effective = ec / (1 + age["creep_coefficient"])
        state = section(member, 1, 0, effective)
        sustained_deflection = (
            coefficient
            * sustained
            * span**4
            / (effective * state["cracked_inertia_mm4"])
        )
        stages[key] = {
            "concrete_modulus_nmm2": effective,
            "neutral_axis_mm": state["neutral_axis_mm"],
            "cracked_inertia_mm4": state["cracked_inertia_mm4"],
            "sustained_deflection_mm": sustained_deflection,
            "shrinkage_deflection_mm": 0,
            "total_deflection_mm": sustained_deflection
            + (first_total - first_sustained if key == "at_assessment" else 0),
        }
    final = stages["at_assessment"]
    span_ei = final["concrete_modulus_nmm2"] * final["cracked_inertia_mm4"]
    cracks = {}
    for face, multiplier in (("bottom", 9 / 128), ("top", 1 / 8)):
        sustained_k = sustained * multiplier * span**2 / span_ei
        transient_k = (total - sustained) * multiplier * span**2 / ei
        axis = (
            sustained_k * final["neutral_axis_mm"]
            + transient_k * instant["neutral_axis_mm"]
        ) / (sustained_k + transient_k)
        tension = [bar for bar in member["bars"] if bar["face"] == face]
        surface = depth if face == "bottom" else 0
        cover = min(
            abs(surface - bar["y_from_top_mm"]) - bar["diameter_mm"] / 2
            for bar in tension
        )
        acr = min(
            math.hypot(bar["x_from_left_mm"], surface - bar["y_from_top_mm"])
            - bar["diameter_mm"] / 2
            for bar in tension
        )
        strain = (sustained_k + transient_k) * (depth - axis)
        width = (
            3 * acr * strain / (1 + 2 * (acr - cover) / (depth - axis))
            if total * multiplier * span**2 / 1e6 > instant["cracking_moment_knm"]
            else 0
        )
        cracks[face] = {
            "neutral_axis_mm": axis,
            "surface_strain": strain,
            "width_mm": width,
        }
    return {
        "initial_total_mm": first_total,
        "initial_sustained_mm": first_sustained,
        "deflection_station_mm": fraction * span,
        **stages,
        "after_finishes_mm": final["total_deflection_mm"]
        - stages["at_finishes"]["total_deflection_mm"],
        "cracks": cracks,
    }


def fixture():
    instant = json.loads((ROOT / "library-029-serv01-beam-service.json").read_text())
    request = deepcopy(instant["cases"]["multilayer"]["request"])
    request["identity"]["case_id"] = "SERV02-multilayer"
    request["history"] = {
        "sustained_load": {
            **request["service_load"],
            "combination_id": "SERV02-SUSTAINED",
            "uniform_load_kn_per_m": 64,
        },
        "loading_age_days": 28,
        "at_finishes": {
            "age_days": 90,
            "creep_coefficient": 0.6,
            "shrinkage_strain": 0.00010,
        },
        "at_assessment": {
            "age_days": 365,
            "creep_coefficient": 1.2,
            "shrinkage_strain": 0.00022,
        },
        "relative_humidity_percent": 60,
        "notional_size_mm": 240,
        "finish_added_load_kn_per_m": 0,
        "source_reference": "SERV02 example input worksheet: prescribed finite-age coefficients and strains, given for replay",
        "bending_basis": "downward_gravity",
    }
    cases = {
        "multilayer_history": {
            "request": request,
            "expected": reference(request),
            "status": "PASS",
        }
    }
    tight = deepcopy(request)
    tight["identity"]["case_id"] = "SERV02-tight-crack-limit"
    tight["crack_width_limit_mm"] = 0.16
    cases["tight_crack_limit"] = {
        "request": tight,
        "expected": reference(tight),
        "status": "FAIL",
    }
    for name, changes in (
        ("missing_sustained", {"sustained_load": None}),
        ("reverse_bending", {"bending_basis": "reverse"}),
        ("finish_load_unresolved", {"finish_added_load_kn_per_m": 5}),
    ):
        control = deepcopy(request)
        control["identity"]["case_id"] = f"SERV02-{name}"
        control["history"].update(changes)
        cases[name] = {"request": control, "expected": None, "status": "HOLD"}
    continuous = deepcopy(instant["cases"]["two_span"]["request"])
    continuous["identity"]["case_id"] = "SERV02-continuous"
    continuous["service_load"].update(midpoint_load_kn=0, uniform_load_kn_per_m=32)
    continuous["history"] = deepcopy(request["history"])
    continuous["history"]["sustained_load"] = {
        **continuous["service_load"],
        "combination_id": "SERV02-CONTINUOUS-G",
        "uniform_load_kn_per_m": 20,
    }
    cases["continuous_history"] = {
        "request": continuous,
        "expected": continuous_reference(continuous),
        "status": "PASS",
    }
    stale = deepcopy(continuous)
    stale["identity"]["case_id"] = "SERV02-continuous-stale"
    stale["history"]["sustained_load"]["reinforcement_revision"] = "old-reinforcement"
    cases["continuous_stale"] = {"request": stale, "expected": None, "status": "HOLD"}
    return {
        "fixture_version": "library-029-serv02-beam-history-reference/v1",
        "sources": [
            "Prescribed finite-age creep and shrinkage inputs for this replay. The history scalars are sample inputs.",
            "Recompute multilayer transformed section at each effective modulus; closed form UDL deflections.",
            "IS 456 Annex C-3 shrinkage curvature uses areas and the tension centroid from actual layers. Annex C-4 uses recomputed sustained displacement.",
            "Annex F flexural width from combined long-term sustained and instantaneous transient strain planes without tension-stiffening credit.",
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
    print(f"Independent SERV02 reference: {len(data['cases'])} cases")


if __name__ == "__main__":
    main()
