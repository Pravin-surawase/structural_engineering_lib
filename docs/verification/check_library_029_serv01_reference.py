"""Freeze elastic, fully cracked instantaneous beam service references."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "library-029-serv01-beam-service.json"


def section(member, moment, surface_x):
    b, depth = member["width_mm"], member["depth_mm"]
    bars = member["bars"]
    ec = 5000 * math.sqrt(member["fck_nmm2"])
    ratio = 200000 / ec
    face = "bottom" if moment >= 0 else "top"
    positions = [
        (
            bar["y_from_top_mm"] if face == "bottom" else depth - bar["y_from_top_mm"],
            math.pi * bar["diameter_mm"] ** 2 / 4,
        )
        for bar in bars
    ]
    low, high = 0, depth
    for _ in range(60):
        x = (low + high) / 2
        force = b * x * x / 2 + math.fsum(
            (ratio - (y < x)) * area * (x - y) for y, area in positions
        )
        if force > 0:
            high = x
        else:
            low = x
    inertia = b * x**3 / 3 + math.fsum(
        (ratio - (y < x)) * area * (y - x) ** 2 for y, area in positions
    )
    curvature = abs(moment) * 1e6 / (ec * inertia)
    fcr = 0.7 * math.sqrt(member["fck_nmm2"])
    cracking_moment = fcr * b * depth**2 / 6 / 1e6
    selected = [bar for bar in bars if bar["face"] == face]
    tension_surface_y = depth if face == "bottom" else 0
    cmin = min(
        abs(bar["y_from_top_mm"] - tension_surface_y) - bar["diameter_mm"] / 2
        for bar in selected
    )
    acr = min(
        math.hypot(
            bar["x_from_left_mm"] - surface_x, bar["y_from_top_mm"] - tension_surface_y
        )
        - bar["diameter_mm"] / 2
        for bar in selected
    )
    width = 3 * acr * curvature * (depth - x) / (1 + 2 * (acr - cmin) / (depth - x))
    return {
        "tension_face": face,
        "cracking_moment_knm": cracking_moment,
        "neutral_axis_mm": x,
        "cracked_inertia_mm4": inertia,
        "width_mm": width if abs(moment) > cracking_moment else 0,
    }


def reference(member, length, udl, point, continuous):
    # Elastic force method about the three support centrelines. For equal
    # spans with identical symmetric loading, internal rotations cancel.
    support_moment = -udl * length**2 / 8 - 3 * point * length / 16 if continuous else 0
    reaction = udl * length / 2 + point / 2 + support_moment / length
    ei = (
        5000
        * math.sqrt(member["fck_nmm2"])
        * section(member, 1, 0)["cracked_inertia_mm4"]
    )

    def integrated(x, order):
        return (
            reaction * x ** (order + 1) / math.factorial(order + 1)
            - udl * x ** (order + 2) / math.factorial(order + 2)
            - point * max(0, x - length / 2) ** (order + 1) / math.factorial(order + 1)
        )

    slope = -integrated(length, 2) / length
    low, high = 0, length / 2
    for _ in range(60):
        x = (low + high) / 2
        if slope + integrated(x, 1) > 0:
            high = x
        else:
            low = x
    midpoint_moment = integrated(length / 2, 0)
    return {
        "support_centre_moment_knm": support_moment / 1e6,
        "midpoint_moment_knm": midpoint_moment / 1e6,
        "maximum_deflection_mm": -(slope * x + integrated(x, 2)) / ei,
        "maximum_deflection_x_mm": x,
        "midpoint": section(member, midpoint_moment / 1e6, 0),
        "support": section(member, support_moment / 1e6, 0) if continuous else None,
    }


def fixture():
    two_span = json.loads((ROOT / "library-029-beam01-flow01.json").read_text())[
        "cases"
    ]["two_span"]["request"]
    section_member = json.loads(
        (ROOT / "library-029-beam03-beam04-sections.json").read_text()
    )["cases"]["multilayer"]["request"]
    cases = {}
    for name, member, length, udl, point, continuous, limit in (
        ("two_span", two_span, 4000, 11.25, 70000, True, 16),
        ("two_span_tight_limit", two_span, 4000, 11.25, 70000, True, 1),
        ("multilayer", section_member, 3000, 320 / 3, 0, False, 12),
    ):
        cases[name] = {
            "request": {
                "identity": {
                    "family_id": "beam",
                    "case_id": f"SERV01-{name}",
                    "member_id": member["member_id"],
                },
                "member": member,
                "span_mm": length,
                "service_load": {
                    "combination_id": "SERV01-SLS",
                    "analysis_revision": member["analysis_revision"],
                    "reinforcement_revision": member["reinforcement_revision"],
                    "source_reference": "Independent symmetric service loading worksheet",
                    "uniform_load_kn_per_m": udl,
                    "midpoint_load_kn": point / 1000,
                },
                "exposure": "mild",
                "instantaneous_deflection_limit_mm": limit,
                "crack_width_limit_mm": 0.3,
            },
            "expected": reference(member, length, udl, point, continuous),
        }
    for control, field in (
        ("missing_service_load", "service_load"),
        ("missing_crack_limit", "crack_width_limit_mm"),
    ):
        cases[control] = {
            "request": {**cases["two_span"]["request"], field: None},
            "expected": None,
        }
    cases["stale_reinforcement"] = {
        "request": {
            **cases["two_span"]["request"],
            "service_load": {
                **cases["two_span"]["request"]["service_load"],
                "reinforcement_revision": "earlier-cage-revision",
            },
        },
        "expected": None,
    }
    return {
        "fixture_version": "library-029-serv01-beam-service-reference/v1",
        "sources": [
            "Equal-span elastic force method or simply supported statics; integrate M/EI twice.",
            "One fully cracked stiffness per span for this declared profile. Equal, symmetric two-span loading and cages.",
            "Cracked transformed force balance by bisection and explicit Annex F width with zero tension-stiffening credit.",
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
    print(f"Independent SERV01 reference: {len(data['cases'])} cases")


if __name__ == "__main__":
    main()
