"""Freeze the layered cutoff specimens from statics, section equilibrium and takeoff."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from copy import deepcopy
from pathlib import Path

from check_library_029_beam05_flanged_reference import TABLE_19
from check_library_029_beam_sections_reference import section

HERE = Path(__file__).resolve().parent
TARGET = HERE / "library-030-beam05-layered-cutoff.json"


def build_case(name, baseline, *, flange=None, control=None):
    request = deepcopy(baseline["request"])
    member = request["member"]
    request["identity"]["case_id"] = name
    member["reinforcement_revision"] += "-CUT-" + name
    if flange:
        member["flange"] = deepcopy(flange)
    cut_bar = next(bar for bar in member["bars"] if bar["bar_id"] == "B1-3")
    diameter = cut_bar["diameter_mm"]
    grade = member["fck_nmm2"]
    ld = diameter * 0.87 * member["fy_nmm2"] / (4 * 1.6 * {25: 1.4, 30: 1.5}[grade])
    theoretical = 2500.0
    end = theoretical + ld - 100 if control == "short" else 3500.0
    request["cutoff"] = {
        "bar_id": cut_bar["bar_id"],
        "theoretical_station_id": "CUT-THEORETICAL",
        "termination_station_id": "CUT-END",
    }
    new_stations = {"CUT-THEORETICAL": theoretical, "CUT-END": end}
    for station_id, coordinate in new_stations.items():
        member["stations"].append(
            {"station_id": station_id, "x_mm": coordinate, "side": "CONTINUOUS"}
        )
    for combo, load in zip(member["combinations"], (24, 32), strict=True):
        cid = combo["combination_id"]
        combo["required_station_ids"].extend(new_stations)
        for station_id, coordinate in new_stations.items():
            if control == "missing" and (cid, station_id) == ("U2", "CUT-END"):
                continue
            x = coordinate / 1000
            reaction = 3 * load * 4 / 8
            member["actions"].append(
                {
                    "row_id": f"{cid}:{station_id}",
                    "combination_id": cid,
                    "station_id": station_id,
                    "mu_knm": reaction * x - load * x**2 / 2,
                    "vu_kn": reaction - load * x,
                    "tu_knm": 0,
                }
            )
    if control == "stale":
        member["current_analysis_revision"] += "-EDITED"
    status = {None: "PASS", "short": "FAIL", "missing": "HOLD", "stale": "HOLD"}[
        control
    ]
    expected = {"status": status}
    if status == "HOLD":
        return {"request": request, "expected": expected}

    continuing = deepcopy(member)
    continuing["bars"].remove(cut_bar)
    width, depth = member["width_mm"], member["depth_mm"]
    shape = member.get("flange")
    physical_width = width
    effective_width = None
    if shape:
        physical_width += shape["left_overhang_mm"] + shape["right_overhang_mm"]
        factor = 1 if shape["kind"] == "t_beam" else 0.5
        effective_width = min(
            physical_width,
            width + factor * (3000 / 6 + 6 * shape["thickness_mm"]),
        )
    reduced = {
        face: section(continuing, face, effective_width, TABLE_19[grade])
        for face in ("bottom", "top")
    }
    assert all(not value["over_reinforced"] for value in reduced.values())
    full_bottom = section(member, "bottom", effective_width, TABLE_19[grade])
    web_bottom = section(continuing, "bottom", None, TABLE_19[grade])
    termination_limit = (
        2 / 3 * min(value["shear_capacity_kn"] for value in reduced.values())
    )
    stations = {row["station_id"]: row["x_mm"] for row in member["stations"]}
    reduced_rows = {}
    for row in member["actions"]:
        sid = row["station_id"]
        if stations[sid] < theoretical:
            continue
        moment, shear = row["mu_knm"], row["vu_kn"]
        face = "top" if moment < 0 else "bottom"
        resistance = reduced[face]
        m_ratio = abs(moment) / resistance["capacity_knm"]
        # At a zero-moment station neither face is selected by flexure.
        shear_capacity = (
            resistance["shear_capacity_kn"]
            if moment
            else min(value["shear_capacity_kn"] for value in reduced.values())
        )
        v_ratio = abs(shear) / shear_capacity
        assert max(m_ratio, v_ratio) < 1
        if sid == "CUT-END":
            assert abs(shear) < termination_limit
        reduced_rows[row["row_id"]] = {
            "flexure_utilization": m_ratio,
            "shear_utilization": v_ratio,
        }
        if sid == "CF":
            # Outer face extension and cl. 26.2.3.3(c) with a web-only M/V.
            available = member["straight_bars"]["end_mm"] - stations[sid]
            beyond_centre = member["straight_bars"]["end_mm"] - 8000
            reduced_rows[row["row_id"]]["positive_anchor_mm"] = min(
                3 * available,
                web_bottom["capacity_knm"] * 1000 / abs(shear) + beyond_centre,
            )
            assert reduced_rows[row["row_id"]]["positive_anchor_mm"] >= ld

    required_extension = max(full_bottom["effective_depth_mm"], 12 * diameter)
    assert end - theoretical >= required_extension
    assert (end - theoretical >= ld) == (status == "PASS")
    assert reduced["bottom"]["tension_area_mm2"] >= full_bottom["tension_area_mm2"] / 4

    # Physical links and cut lengths from the declared centreline geometry.
    detail = request["link_detail"]
    link_diameter = member["link_diameter_mm"]
    cover = member["clear_cover_mm"]
    inset = cover + link_diameter / 2
    w, h = width - 2 * inset, depth - 2 * inset
    radius = detail["internal_bend_radius_mm"] + link_diameter / 2
    link_cut = (
        2 * detail["hook_vertex_leg_mm"]
        + w
        + 2 * h
        + math.hypot(w, detail["hook_plane_offset_mm"])
        + 5 * radius * (math.pi / 2 - 2)
    )
    spacing = member["link_spacing_mm"]
    link_count = (
        int((detail["last_station_mm"] - detail["first_station_mm"]) / spacing) + 1
    )
    assert spacing <= min(
        0.75 * min(value["effective_depth_mm"] for value in reduced.values()), 300
    )
    assert (
        0.87
        * min(member["link_fy_nmm2"], 415)
        * math.pi
        * link_diameter**2
        / 2
        / (width * spacing)
        >= 0.4
    )
    for bar in member["bars"]:
        x, y, r = bar["x_from_left_mm"], bar["y_from_top_mm"], bar["diameter_mm"] / 2
        assert min(x, width - x, y, depth - y) >= cover + link_diameter + r
    for i, bar in enumerate(member["bars"]):
        for other in member["bars"][i + 1 :]:
            clear = (
                math.hypot(
                    bar["x_from_left_mm"] - other["x_from_left_mm"],
                    bar["y_from_top_mm"] - other["y_from_top_mm"],
                )
                - (bar["diameter_mm"] + other["diameter_mm"]) / 2
            )
            assert clear >= max(
                bar["diameter_mm"],
                other["diameter_mm"],
                member["aggregate_size_mm"] + 5,
            )

    start = member["straight_bars"]["start_mm"]
    full_cut = member["straight_bars"]["end_mm"] - start
    cut_length = end - start
    bar_counts = Counter()
    mass = link_count * link_cut * math.pi * link_diameter**2 / 4 * 7850e-9
    for bar in member["bars"]:
        d = bar["diameter_mm"]
        mark = f"{member['member_id']}-{bar['face']}-L{bar['layer']}-D{d:g}"
        if bar == cut_bar:
            mark += "-cutoff"
        bar_counts[mark] += 1
        mass += (
            (cut_length if bar == cut_bar else full_cut) * math.pi * d**2 / 4 * 7850e-9
        )
    expected.update(
        development_mm=ld,
        required_extension_mm=required_extension,
        available_extension_mm=end - theoretical,
        continuing_bottom_mm2=reduced["bottom"]["tension_area_mm2"],
        termination_limit_kn=termination_limit,
        reduced_rows=reduced_rows,
        reduced_moment_knm={
            face: values["capacity_knm"] for face, values in reduced.items()
        },
        reduced_shear_kn={
            face: values["shear_capacity_kn"] for face, values in reduced.items()
        },
        effective_flange_width_mm=effective_width,
        physical_width_mm=physical_width,
        continuing_bar_ids=sorted(bar["bar_id"] for bar in continuing["bars"]),
        cut_mm=cut_length,
        full_cut_mm=full_cut,
        marks=dict(bar_counts),
        link_count=link_count,
        link_cut_mm=link_cut,
        mass_kg=mass,
    )
    return {"request": request, "expected": expected}


def build():
    published = json.loads(
        (HERE / "library-029-beam05-flanged-detailing.json").read_text()
    )["cases"]
    rect = published["rect_multilayer"]
    cases = {
        "rect_multilayer": build_case("rect_multilayer", rect),
        "short_development": build_case("short_development", rect, control="short"),
        "missing_action": build_case("missing_action", rect, control="missing"),
        "stale_action": build_case("stale_action", rect, control="stale"),
        "t_multilayer": build_case(
            "t_multilayer",
            rect,
            flange=published["t_beam"]["request"]["member"]["flange"],
        ),
        "l_multilayer": build_case("l_multilayer", published["l_multilayer"]),
        "l_multilayer_reflected": build_case(
            "l_multilayer_reflected",
            published["l_multilayer"],
            flange=published["l_reflected"]["request"]["member"]["flange"],
        ),
    }
    return {
        "fixture_version": "library-030-beam05-layered-cutoff/v1",
        "sources": [
            "Published 0.29.2 two-span BEAM05 fixtures, with the published T and reflected L flanges on the multilayer web cages.",
            "Three-moment equilibrium for 24/32 kN/m ULS; IS 456:2000 cl. 23.1.2, 26.2, 26.3, 40.4 and Table 19.",
            "Section equilibrium on actual bar centres and physical link centreline takeoff, density 7850 kg/m³.",
        ],
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    fixture = build()
    if args.freeze:
        TARGET.write_text(
            json.dumps(fixture, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
    else:
        assert json.loads(TARGET.read_text(encoding="utf-8")) == fixture
    print(f"Independent BEAM05 layered cutoff reference: {len(fixture['cases'])} cases")


if __name__ == "__main__":
    main()
