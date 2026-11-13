"""Freeze two-span flanged and layered web-cage cuts without importing StructLib."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from copy import deepcopy
from pathlib import Path

from check_library_029_beam_sections_reference import fixture as section_fixture
from check_library_029_beam_sections_reference import section

FIXTURE = Path(__file__).with_name("library-029-beam05-flanged-detailing.json")
TABLE_19 = {
    25: [(0.25, 0.36), (0.50, 0.49), (0.75, 0.57), (1, 0.64), (1.25, 0.70)],
    30: [
        (0.25, 0.37),
        (0.50, 0.50),
        (0.75, 0.59),
        (1, 0.66),
        (1.25, 0.71),
        (1.50, 0.76),
    ],
}
# x in mm, with separate approaches at the internal support.
STATIONS = (
    ("A", 0, "RIGHT"),
    ("AF", 500, "CONTINUOUS"),
    ("S1", 1500, "CONTINUOUS"),
    ("BF1", 3850, "CONTINUOUS"),
    ("B1", 4000, "LEFT"),
    ("B2", 4000, "RIGHT"),
    ("BF2", 4150, "CONTINUOUS"),
    ("S2", 6500, "CONTINUOUS"),
    ("CF", 7500, "CONTINUOUS"),
    ("C", 8000, "LEFT"),
)


def actions():
    # Equal simply ended spans of length L. The three-moment equation gives
    # M_B = -q L²/8. Each outer reaction is qL/2 + M_B/L.
    span = 4
    rows = []
    for combination, q in (("U1", 24), ("U2", 32)):
        m_b = -q * span**2 / 8
        reaction = q * span / 2 + m_b / span
        for name, x, side in STATIONS:
            right_span = x > 4000 or (x == 4000 and side == "RIGHT")
            s = (8000 - x if right_span else x) / 1000
            rows.append(
                {
                    "row_id": f"{combination}:{name}",
                    "combination_id": combination,
                    "station_id": name,
                    "mu_knm": reaction * s - q * s**2 / 2,
                    "vu_kn": (-1 if right_span else 1) * (reaction - q * s),
                    "tu_knm": 0,
                }
            )
    return rows


def reference_case(name, source, flange=None):
    member = deepcopy(source)
    if flange is not None:
        member["flange"] = deepcopy(flange)
    flange = member.get("flange")
    member_id = f"B-{name.upper()}"
    member.update(
        schema_version="is456-layered-continuous-beam-check/v1",
        member_id=member_id,
        analysis_revision=f"{member_id}-A1",
        current_analysis_revision=f"{member_id}-A1",
        reinforcement_revision=f"{member_id}-R1",
        source_reference="BEAM05 two-span three-moment reference with no equilibrium torsion",
        link_spacing_mm=200,
        supports=[
            {"support_id": key, "centre_mm": x, "width_mm": width}
            for key, x, width in (("A", 0, 1000), ("B", 4000, 300), ("C", 8000, 1000))
        ],
        straight_bars={
            "start_mm": -460,
            "end_mm": 8460,
            "source_reference": "Continuous straight specimen bars with covered ends",
        },
        stations=[
            {"station_id": key, "x_mm": x, "side": side} for key, x, side in STATIONS
        ],
        combinations=[
            {
                "combination_id": key,
                "kind": "ULS",
                "required_station_ids": [name for name, _, _ in STATIONS],
            }
            for key in ("U1", "U2")
        ],
        actions=actions(),
    )
    width = member["width_mm"]
    height = member["depth_mm"]
    grade = member["fck_nmm2"]
    left = flange["left_overhang_mm"] if flange else 0
    right = flange["right_overhang_mm"] if flange else 0
    effective = None
    if flange:
        # The positive moment parabola has roots at 0 and 2R/q = 3 m.
        flange["zero_moment_distance_mm"] = 3000
        factor = 1 if flange["kind"] == "t_beam" else 0.5
        effective = min(
            width + left + right,
            width + factor * (3000 / 6 + 6 * flange["thickness_mm"]),
        )
    strengths = {
        face: section(member, face, effective, TABLE_19[grade])
        for face in ("top", "bottom")
    }
    assert all(not value["over_reinforced"] for value in strengths.values())
    for row in member["actions"]:
        face = "top" if row["mu_knm"] < 0 else "bottom"
        assert abs(row["mu_knm"]) < strengths[face]["capacity_knm"]
        assert abs(row["vu_kn"]) < strengths[face]["shear_capacity_kn"]

    link_count = 41
    link_radius = 14
    inset = member["clear_cover_mm"] + 4
    w, h = width - 2 * inset, height - 2 * inset
    # Centreline perimeter with an oblique crossing, two tails and five fillets.
    link_cut = 200 + w + 2 * h + math.hypot(w, 10)
    link_cut += 5 * link_radius * (math.pi / 2 - 2)
    longitudinal_cut = 8920
    marks = Counter(
        (bar["face"], bar["layer"], bar["diameter_mm"]) for bar in member["bars"]
    )

    def mass(diameter, quantity, length):
        return quantity * math.pi * diameter**2 / 4 * length * 7850e-9

    bond = {25: 1.4, 30: 1.5}[grade] * 1.6
    end_ld = {
        bar["bar_id"]: bar["diameter_mm"] * (0.87 * member["fy_nmm2"]) / (4 * bond)
        for bar in member["bars"]
    }
    assert max(end_ld.values()) < 960
    return {
        "request": {
            "identity": {"family_id": "beam", "case_id": name, "member_id": member_id},
            "member": member,
            "link_detail": {
                "first_station_mm": 0,
                "last_station_mm": 8000,
                "internal_bend_radius_mm": 10,
                "hook_vertex_leg_mm": 100,
                "hook_plane_offset_mm": 10,
                "source_reference": "BEAM05 ordinary web link with separate hook planes",
            },
            "stock_length_mm": 12000,
        },
        "expected": {
            "status": "PASS",
            "effective_flange_width_mm": effective,
            "physical_width_mm": width + left + right,
            "capacity_knm": {
                face: values["capacity_knm"] for face, values in strengths.items()
            },
            "shear_capacity_kn": {
                face: values["shear_capacity_kn"] for face, values in strengths.items()
            },
            "outer_available_mm": 960,
            "outer_ld_mm": end_ld,
            "longitudinal_cut_mm": longitudinal_cut,
            "link_count": link_count,
            "link_cut_mm": link_cut,
            "marks": {
                f"{member_id}-{face}-L{layer}-D{diameter}": count
                for (face, layer, diameter), count in marks.items()
            },
            "mass_kg": mass(8, link_count, link_cut)
            + sum(
                mass(diameter, count, longitudinal_cut)
                for (_, _, diameter), count in marks.items()
            ),
        },
    }


def fixture():
    section_cases = section_fixture()["cases"]
    layers = section_cases["multilayer_reduced"]["request"]
    cases = {
        "t_beam": reference_case("t_beam", section_cases["t"]["request"]),
        "l_multilayer": reference_case(
            "l_multilayer", layers, section_cases["l"]["request"]["flange"]
        ),
        "l_reflected": reference_case(
            "l_reflected", section_cases["l_reflected"]["request"]
        ),
        "rect_multilayer": reference_case("rect_multilayer", layers),
    }
    for name, baseline, status in (
        ("short_anchor", "t_beam", "FAIL"),
        ("congested", "l_multilayer", "FAIL"),
        ("missing_combination_face", "l_multilayer", "HOLD"),
        ("missing_link", "t_beam", "HOLD"),
        ("torsion", "l_multilayer", "HOLD"),
        ("stale", "t_beam", "HOLD"),
        ("cutoff", "t_beam", "HOLD"),
    ):
        request = deepcopy(cases[baseline]["request"])
        request["identity"]["case_id"] = name
        member = request["member"]
        if name == "short_anchor":
            member["straight_bars"]["start_mm"] = 0
        elif name == "congested":
            for bar in member["bars"]:
                if bar["face"] == "bottom" and bar["layer"] == 2:
                    bar["y_from_top_mm"] = 500
        elif name == "missing_combination_face":
            member["combinations"][1]["required_station_ids"].remove("BF1")
            member["actions"] = [
                row for row in member["actions"] if row["row_id"] != "U2:BF1"
            ]
        elif name == "missing_link":
            request["link_detail"] = None
        elif name == "torsion":
            member["actions"][1]["tu_knm"] = 1
        elif name == "stale":
            member["current_analysis_revision"] += "-edited"
        elif name == "cutoff":
            request["cutoff"] = {
                "bar_id": "B1-1",
                "theoretical_station_id": "S1",
                "termination_station_id": "BF1",
            }
        expected = {"status": status}
        if name == "short_anchor":
            expected["outer_available_mm"] = 500
            expected["outer_ld_mm"] = cases[baseline]["expected"]["outer_ld_mm"]
        cases[name] = {"request": request, "expected": expected}
    return {
        "fixture_version": "library-029-beam05-flanged-detailing-reference/v1",
        "sources": [
            "Two equal 4 m spans with independent three-moment ULS actions.",
            "IS 456:2000 Cl. 23.1.2, 26.2 and 26.3, Table 19 and signed section equilibrium.",
            "Physical web-only link grid, tangent-filleted centreline lengths and steel density 7850 kg/m³.",
        ],
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    data = fixture()
    if args.freeze:
        FIXTURE.write_text(
            json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
    else:
        assert json.loads(FIXTURE.read_text(encoding="utf-8")) == data
    print(
        f"Independent BEAM05 flanged and multilayer reference: {len(data['cases'])} cases"
    )


if __name__ == "__main__":
    main()
