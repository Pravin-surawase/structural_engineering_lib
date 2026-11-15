"""Freeze the BEAM05 separated lap from statics, section equilibrium and takeoff."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

from check_library_029_beam05_flanged_reference import TABLE_19
from check_library_029_beam_sections_reference import section

HERE = Path(__file__).resolve().parent
TARGET = HERE / "library-030-beam05-layered-lap.json"


def build_case(name, baseline, partner_x, *, use_published_cage=False):
    request = deepcopy(baseline)
    request["identity"]["case_id"] = name
    member = request["member"]
    member["reinforcement_revision"] += "-LAP-" + name
    if not use_published_cage:
        # The two inner bars align above uninterrupted outer bars in all zones.
        member["bars"] = [bar for bar in member["bars"] if bar["bar_id"] != "B2-3"]
    original_id, partner_id = "B1-3", "B1-3-partner"
    original = next(bar for bar in member["bars"] if bar["bar_id"] == original_id)
    partner = dict(original, bar_id=partner_id, x_from_left_mm=partner_x)
    start, middle, end = 1550, 2200, 2850
    lap_stations = {"LAP-START": start, "LAP-MID": middle, "LAP-END": end}
    for station_id, x in lap_stations.items():
        member["stations"].append(
            dict(station_id=station_id, x_mm=x, side="CONTINUOUS")
        )
    for combo, load in zip(member["combinations"], (24, 32), strict=True):
        combo["required_station_ids"].extend(lap_stations)
        reaction = 3 * load * 4 / 8
        cid = combo["combination_id"]
        for station_id, x in lap_stations.items():
            distance = x / 1000
            member["actions"].append(
                {
                    "row_id": f"{cid}:{station_id}",
                    "combination_id": cid,
                    "station_id": station_id,
                    "mu_knm": reaction * distance - load * distance**2 / 2,
                    "vu_kn": reaction - load * distance,
                    "tu_knm": 0,
                }
            )
    request["lap"] = {
        "bar_id": original_id,
        "partner_bar_id": partner_id,
        "partner_x_from_left_mm": partner_x,
        "start_station_id": "LAP-START",
        "middle_station_id": "LAP-MID",
        "end_station_id": "LAP-END",
        "placement_reference": "Straight separated equal bars in layer 1 with uniform closed links",
    }

    unchanged = [bar for bar in member["bars"] if bar != original]
    inner_axes = {bar["x_from_left_mm"] for bar in unchanged if bar["layer"] == 2}
    outer_axes = {
        bar["x_from_left_mm"]
        for bar in unchanged
        if bar["face"] == "bottom" and bar["layer"] == 1
    }
    if use_published_cage:
        assert inner_axes - outer_axes == {245}
        assert partner_x not in inner_axes
        return {
            "request": request,
            "expected": {"status": "FAIL", "unaligned_inner_bar_id": "B2-3"},
        }
    assert inner_axes <= outer_axes

    diameter = original["diameter_mm"]
    radius = diameter / 2
    width, depth = member["width_mm"], member["depth_mm"]
    for bar in (original, partner):
        x, y = bar["x_from_left_mm"], bar["y_from_top_mm"]
        assert min(x, width - x, y, depth - y) - radius >= 2 * diameter
    clear_pair = abs(partner_x - original["x_from_left_mm"]) - diameter
    required_clear = max(diameter, member["aggregate_size_mm"] + 5)
    outer = sorted((*outer_axes, original["x_from_left_mm"], partner_x))
    minimum_clear = min(b - a - diameter for a, b in zip(outer, outer[1:]))
    assert min(abs(partner_x - x) - diameter for x in outer_axes) >= required_clear
    vertical_clear = original["y_from_top_mm"] - 450 - diameter
    assert vertical_clear >= max(15, (2 / 3) * member["aggregate_size_mm"], diameter)

    ld = diameter * 0.87 * member["fy_nmm2"] / (4 * 1.5 * 1.6)
    required_lap = max(ld, 30 * diameter, 15 * diameter, 200)
    overlap = end - start
    assert overlap > required_lap
    bottom_count = sum(bar["face"] == "bottom" for bar in member["bars"])
    assert 1 / bottom_count <= 0.5
    strengths = {
        face: section(member, face, None, TABLE_19[30]) for face in ("bottom", "top")
    }
    downstream = dict(member, bars=[*unchanged, partner])
    for face, capacity in strengths.items():
        # Replacing the bar at the same y and diameter preserves signed resistance.
        other = section(downstream, face, None, TABLE_19[30])
        assert math.isclose(other["capacity_knm"], capacity["capacity_knm"])
        assert math.isclose(other["shear_capacity_kn"], capacity["shear_capacity_kn"])
        assert not capacity["over_reinforced"]
    stress_limit = strengths["bottom"]["capacity_knm"] / 2
    overlap_rows = {}
    for row in member["actions"]:
        moment, shear = row["mu_knm"], row["vu_kn"]
        face = "top" if moment < 0 else "bottom"
        assert abs(moment) < strengths[face]["capacity_knm"]
        assert abs(shear) < min(
            value["shear_capacity_kn"] for value in strengths.values()
        )
        if row["station_id"] in lap_stations:
            assert 0 < moment < stress_limit
            overlap_rows[row["row_id"]] = {
                "moment_knm": moment,
                "shear_kn": shear,
                "half_capacity_knm": stress_limit,
            }
    detail = request["link_detail"]
    link_dia = member["link_diameter_mm"]
    inset = member["clear_cover_mm"] + link_dia / 2
    w, h = width - 2 * inset, depth - 2 * inset
    radius_at_bend = detail["internal_bend_radius_mm"] + link_dia / 2
    link_cut = (
        2 * detail["hook_vertex_leg_mm"]
        + w
        + 2 * h
        + math.hypot(w, detail["hook_plane_offset_mm"])
        + 5 * radius_at_bend * (math.pi / 2 - 2)
    )
    spacing = member["link_spacing_mm"]
    link_count = (detail["last_station_mm"] - detail["first_station_mm"]) // spacing + 1
    assert spacing <= min(
        300, *(0.75 * value["effective_depth_mm"] for value in strengths.values())
    )

    extent = member["straight_bars"]
    cut_original, cut_partner = end - extent["start_mm"], extent["end_mm"] - start
    full_cut = extent["end_mm"] - extent["start_mm"]

    def mass(diameter_mm, length_mm):
        return math.pi * diameter_mm**2 / 4 * length_mm * 7850e-9

    return {
        "request": request,
        "expected": {
            "status": "PASS" if minimum_clear >= required_clear else "FAIL",
            "overlap_mm": overlap,
            "required_lap_mm": required_lap,
            "pair_clear_mm": clear_pair,
            "minimum_clear_mm": minimum_clear,
            "required_clear_mm": required_clear,
            "vertical_clear_mm": vertical_clear,
            "overlap_rows": overlap_rows,
            "cut_original_mm": cut_original,
            "cut_partner_mm": cut_partner,
            "full_cut_mm": full_cut,
            "full_bar_count": len(unchanged),
            "link_count": link_count,
            "link_cut_mm": link_cut,
            "mass_kg": sum(mass(bar["diameter_mm"], full_cut) for bar in unchanged)
            + mass(diameter, cut_original + cut_partner)
            + link_count * mass(link_dia, link_cut),
        },
    }


def build():
    baseline = json.loads(
        (HERE / "library-029-beam05-flanged-detailing.json").read_text()
    )["cases"]["rect_multilayer"]["request"]
    return {
        "fixture_version": "library-030-beam05-layered-lap/v1",
        "sources": [
            "Published 300 x 600 mm BEAM05 rectangle, support and link geometry, materials and 24/32 kN/m two-span actions.",
            "IS 456:2000 cl. 26.2.1, 26.2.5, 26.3.2 and Table 19. The passing cage omits B2-3 so both remaining inner bars stay in line with uninterrupted outer bars.",
            "Straight cut takeoff and tangent-filleted link centreline with a 7850 kg/m³ steel density.",
        ],
        "cases": {
            "layered_lap": build_case("layered_lap", baseline, 197.5),
            "layered_lap_congestion": build_case(
                "layered_lap_congestion", baseline, 215
            ),
            "published_cage_misalignment": build_case(
                "published_cage_misalignment", baseline, 197.5, use_published_cage=True
            ),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    expected = build()
    if args.freeze:
        TARGET.write_text(
            json.dumps(expected, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
    else:
        assert json.loads(TARGET.read_text(encoding="utf-8")) == expected
    print(f"Independent BEAM05 layered lap reference: {len(expected['cases'])} cases")


if __name__ == "__main__":
    main()
