"""Freeze BEAM03 and BEAM04 by independent signed section equilibrium."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

FIXTURE = Path(__file__).with_name("library-029-beam03-beam04-sections.json")


def stress(strain, fy):
    """Interpolate the declared Fe415/Fe500 design stress law."""
    fy_design = fy / 1.15
    strain_abs = abs(strain)
    x0, y0 = 0.0, 0.0
    for fraction, plastic in (
        (0.8, 0),
        (0.85, 0.0001),
        (0.9, 0.0003),
        (0.95, 0.0007),
        (0.975, 0.001),
        (1, 0.002),
    ):
        y1 = fraction * fy_design
        x1 = y1 / 200000 + plastic
        if strain_abs <= x1:
            return math.copysign(y0 + (y1 - y0) * (strain_abs - x0) / (x1 - x0), strain)
        x0, y0 = x1, y1
    return math.copysign(fy_design, strain)


def section(request, face, effective_width, table19):
    width, height, fck, fy = (
        request[key] for key in ("width_mm", "depth_mm", "fck_nmm2", "fy_nmm2")
    )
    bars = [
        (
            item["bar_id"],
            item["face"],
            math.pi * item["diameter_mm"] ** 2 / 4,
            (
                item["y_from_top_mm"]
                if face == "bottom"
                else height - item["y_from_top_mm"]
            ),
        )
        for item in request["bars"]
    ]
    area = sum(a for _, bar_face, a, _ in bars if bar_face == face)
    depth = sum(a * y for _, bar_face, a, y in bars if bar_face == face) / area
    uses_flange = face == "bottom" and effective_width is not None
    compression_width = effective_width if uses_flange else width
    assert compression_width is not None

    def resultants(axis):
        states = {}
        for bar_id, _, a, y in bars:
            strain = 0.0035 * (1 - y / axis)
            r = max(0.0, min(strain / 0.002, 1.0))
            fc = (0.67 / 1.5) * fck * (2 * r - r**2)
            states[bar_id] = (strain, (stress(strain, fy) - fc) * a, y)
        return 0.36 * fck * compression_width * axis, states

    high = request["flange"]["thickness_mm"] if uses_flange else height
    low = 1e-6
    for _ in range(110):
        axis = (low + high) / 2
        cc, states = resultants(axis)
        if cc + sum(force for _, force, _ in states.values()) < 0:
            low = axis
        else:
            high = axis
    axis = (low + high) / 2
    cc, states = resultants(axis)
    assert abs(cc + sum(force for _, force, _ in states.values())) < 1e-6
    extreme = max(y for _, _, _, y in bars)
    limit = 0.0035 * extreme / (0.0035 + 0.002 + fy / (1.15 * 200000))
    moment = (
        cc * (depth - 0.42 * axis)
        + sum(force * (depth - y) for _, force, y in states.values())
    ) / 1e6
    pt = 100 * area / (width * depth)
    for (p0, t0), (p1, t1) in zip(table19, table19[1:]):
        if p0 <= pt <= p1:
            tau = t0 + (pt - p0) / (p1 - p0) * (t1 - t0)
            break
    else:
        raise AssertionError(f"Missing Table 19 bracket for {pt}")
    vc = tau * width * depth / 1000
    vs = (
        0.87
        * min(request["link_fy_nmm2"], 415)
        * 2
        * math.pi
        * request["link_diameter_mm"] ** 2
        / 4
        * depth
        / request["link_spacing_mm"]
        / 1000
    )
    return {
        "effective_depth_mm": depth,
        "neutral_axis_mm": axis,
        "limiting_neutral_axis_mm": limit,
        "over_reinforced": axis > limit,
        "concrete_compression_force_n": cc,
        "capacity_knm": moment,
        "uses_compression_flange": uses_flange,
        "tension_area_mm2": area,
        "shear_web_width_mm": width,
        "shear_capacity_kn": vc + vs,
        "bar_strains": {key: value[0] for key, value in states.items()},
        "bar_net_forces_n": {key: value[1] for key, value in states.items()},
    }


def bars(layer_specs):
    return [
        {
            "bar_id": f"{face[0].upper()}{layer}-{index}",
            "face": face,
            "layer": layer,
            "diameter_mm": diameter,
            "x_from_left_mm": x,
            "y_from_top_mm": y,
        }
        for face, layer, diameter, y, xs in layer_specs
        for index, x in enumerate(xs, start=1)
    ]


def fixture():
    older = json.loads(
        Path(__file__).with_name("library-027-t-beam-member.json").read_text()
    )
    inputs = older["inputs"]
    sagging = older["cases"]["main"]["expected"]
    common = {
        "member_id": "B03",
        "analysis_revision": "B03-A1",
        "current_analysis_revision": "B03-A1",
        "reinforcement_revision": "B03-R1",
        "source_reference": "BEAM03 signed section reference",
        "width_mm": 300,
        "depth_mm": 550,
        "fck_nmm2": 25,
        "fy_nmm2": 415,
        "clear_cover_mm": 25,
        "aggregate_size_mm": 20,
        "link_diameter_mm": 8,
        "link_spacing_mm": 150,
        "link_fy_nmm2": 415,
        "bars": bars(
            [
                ("top", 1, 16, 50, inputs["top_bars"]["web_local_x_mm"]),
                ("bottom", 1, 20, 500, inputs["bottom_bars"]["web_local_x_mm"]),
            ]
        ),
        "stations": [{"station_id": "SECTION", "x_mm": 0, "side": "CONTINUOUS"}],
        "combinations": [
            {"combination_id": key, "kind": "ULS", "required_station_ids": ["SECTION"]}
            for key in ("SAG", "HOG")
        ],
        "actions": [
            {
                "row_id": "SAG:SECTION",
                "combination_id": "SAG",
                "station_id": "SECTION",
                "mu_knm": sagging["ultimate_moment_knm"],
                "vu_kn": sagging["ultimate_shear_kn"],
            },
            {
                "row_id": "HOG:SECTION",
                "combination_id": "HOG",
                "station_id": "SECTION",
                "mu_knm": -150,
                "vu_kn": 100,
            },
        ],
    }
    t = {
        **common,
        "flange": {
            "kind": "t_beam",
            "thickness_mm": 150,
            "left_overhang_mm": 350,
            "right_overhang_mm": 350,
            "zero_moment_distance_mm": 6000,
            "monolithic": True,
        },
    }
    l = {
        **common,
        "member_id": "B04",
        "flange": {
            "kind": "l_beam",
            "thickness_mm": 120,
            "left_overhang_mm": 0,
            "right_overhang_mm": 300,
            "zero_moment_distance_mm": 6000,
            "monolithic": True,
        },
    }
    mixed = deepcopy(common)
    mixed.update(
        member_id="B05",
        depth_mm=600,
        fck_nmm2=30,
        fy_nmm2=500,
        clear_cover_mm=30,
        link_spacing_mm=200,
        source_reference="BEAM04 multilayer reference",
    )
    mixed["bars"] = bars(
        [
            ("top", 1, 20, 55, (55, 245)),
            ("bottom", 1, 25, 520, (55, 150, 245)),
            ("bottom", 2, 25, 450, (55, 150, 245)),
        ]
    )
    for row, mu in zip(mixed["actions"], (200, -200), strict=True):
        row.update(mu_knm=mu, vu_kn=110)
    for data in (t, l, mixed):
        data["schema_version"] = "is456-beam-section-check/v1"
    reflected = deepcopy(l)
    reflected["flange"].update(left_overhang_mm=300, right_overhang_mm=0)
    reduced = deepcopy(mixed)
    for bar in reduced["bars"]:
        if bar["face"] == "bottom":
            bar["diameter_mm"] = 20
    table25 = [(0.25, 0.36), (0.50, 0.49), (0.75, 0.57), (1, 0.64)]
    table30 = [
        (0.25, 0.37),
        (0.50, 0.50),
        (0.75, 0.59),
        (1, 0.66),
        (1.25, 0.71),
        (1.50, 0.76),
        (1.75, 0.80),
        (2, 0.84),
        (2.25, 0.88),
    ]
    fixtures = {
        "t": (t, table25),
        "l": (l, table25),
        "l_reflected": (reflected, table25),
        "multilayer": (mixed, table30),
        "multilayer_reduced": (reduced, table30),
    }
    cases = {}
    for key, (request, table19) in fixtures.items():
        flange = request.get("flange")
        effective = None
        if flange:
            web = request["width_mm"]
            geometric = web + flange["left_overhang_mm"] + flange["right_overhang_mm"]
            ratio = 1 if flange["kind"] == "t_beam" else 0.5
            effective = min(
                geometric,
                web
                + ratio
                * (flange["zero_moment_distance_mm"] / 6 + 6 * flange["thickness_mm"]),
            )
        expected = {
            face: section(request, face, effective, table19)
            for face in ("top", "bottom")
        }
        assert abs(request["actions"][0]["mu_knm"]) < expected["bottom"]["capacity_knm"]
        assert abs(request["actions"][1]["mu_knm"]) > expected["top"]["capacity_knm"]
        cases[key] = {
            "request": request,
            "effective_flange_width_mm": effective,
            "sections": expected,
            "sagging_status": (
                "FAIL" if expected["bottom"]["over_reinforced"] else "PASS"
            ),
            "hogging_status": "FAIL",
        }
    mismatch = deepcopy(l)
    mismatch["flange"]["kind"] = "t_beam"
    cases["flange_identity_mismatch"] = {"request": mismatch, "status": "BLOCKED"}
    stale = deepcopy(t)
    stale["current_analysis_revision"] = "B03-A2"
    cases["stale"] = {"request": stale, "status": "HOLD"}
    return {
        "fixture_version": "library-029-beam03-beam04-section-reference/v1",
        "sources": [
            "LIB-027 frozen T-member section, sagging actions and web-local reinforcement.",
            "IS 456:2000 Cl. 23.1.2, 26, 38.1, 40, Figures 21–23 and Tables 19 and 20.",
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
    print(f"Independent BEAM03/04 section reference: {len(reference['cases'])} cases")


if __name__ == "__main__":
    main()
