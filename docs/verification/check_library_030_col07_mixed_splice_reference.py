"""Freeze a mixed-column contact splice using geometry and independent section equilibrium."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from copy import deepcopy
from itertools import combinations, pairwise
from pathlib import Path

from check_library_029_col03_reference import reference as section_reference

HERE = Path(__file__).resolve().parent
BASE = HERE / "library-029-col07-mixed-member.json"
FIXTURE = HERE / "library-030-col07-mixed-splice.json"
PAIR = ("L1", "R1")
LAP_MARK = "LX"


def specimen(base):
    request = deepcopy(base)
    request["identity"]["case_id"] = "COL07-mixed-contact-splice"
    request["tie_zones"][1:2] = [
        {"zone_id": "FIELD_LOW", "start_mm": 700, "end_mm": 1020, "pitch_mm": 160},
        {"zone_id": "SPLICE", "start_mm": 1020, "end_mm": 1980, "pitch_mm": 80},
        {"zone_id": "FIELD_HIGH", "start_mm": 1980, "end_mm": 2300, "pitch_mm": 160},
    ]
    request["basis"]["action_source_reference"] = (
        "COL07 mixed-splice synthetic station worksheet and U2 interval in this fixture"
    )
    request["basis"]["detailing_revision"] = "D2"
    request["transverse_cut_schedule"]["detailing_revision"] = "D2"
    request["actions"][1].update(mx_knm=12, my_knm=-8, vx_kn=-60)
    request["actions"].append(
        {
            "combination_id": "U3",
            "check_station_mm": 2750,
            "pu_kn": 800,
            "mx_knm": -65,
            "my_knm": 40,
            "vx_kn": 0,
            "vy_kn": -200,
        }
    )
    request["laps"] = [
        {
            "lap_id": "S1",
            "bar_ids": list(PAIR),
            "start_mm": 1170,
            "end_mm": 1810,
            "stress_basis": "compression",
            "contact_assembly": {
                "partner_y_mm": 216,
                "lap_link_id": LAP_MARK,
                "hook_tail_mm": 80,
                "fabrication_reference": "D2 local LX return at the X1 seat",
                "compression_reference": "A1 synthetic U2 compression interval in this fixture",
            },
        }
    ]
    return request


def point(bar):
    return bar["x_from_left_mm"], bar["y_from_top_mm"]


def area(diameter):
    return math.pi * diameter**2 / 4


def clearances(bars, contact_pairs=()):
    return sorted(
        (
            math.dist(point(a), point(b)) - (a["diameter_mm"] + b["diameter_mm"]) / 2,
            a["bar_id"],
            b["bar_id"],
        )
        for a, b in combinations(bars, 2)
        if (a["bar_id"], b["bar_id"]) not in contact_pairs
    )


def clear_from_box(bars, bounds, link_diameter):
    xmin, ymin, xmax, ymax = bounds
    return min(
        math.hypot(max(xmin - x, 0, x - xmax), max(ymin - y, 0, y - ymax))
        - (bar["diameter_mm"] + link_diameter) / 2
        for bar in bars
        for x, y in (point(bar),)
    )


def gross_kern_stress(pu, abs_mx, abs_my, width, depth):
    return 1000 * pu / (width * depth) - (
        6e6 * abs_mx / (width * depth**2) + 6e6 * abs_my / (depth * width**2)
    )


def shear(action, pitch, width, depth):
    vx, vy = action["vx_kn"], action["vy_kn"]
    axis, demand = ("x", vx) if vx else ("y", vy)
    web_width, effective_depth = (depth, width - 60) if vx else (width, depth - 60)
    axial_factor = min(1.5, 1 + 3000 * action["pu_kn"] / (width * depth * 30))
    concrete = 0.29 * axial_factor * web_width * effective_depth / 1000
    hoop = 0.87 * 415 * 2 * area(10) * effective_depth / (1000 * pitch)
    crushing = 3.5 * web_width * effective_depth / 1000
    capacity = min(concrete + hoop, crushing)
    return {
        "direction": axis,
        "signed_demand_kn": demand,
        "d_mm": effective_depth,
        "pitch_mm": pitch,
        "pitch_limit_mm": 0.75 * effective_depth,
        "credited_hoop_id": "HOOP",
        "credited_legs": 2,
        "vc_kn": concrete,
        "vus_kn": hoop,
        "crushing_kn": crushing,
        "capacity_kn": capacity,
        "utilization": abs(demand) / capacity,
    }


def geometry_checks(request):
    cage = request["reinforcement"]
    width, depth = (request["geometry"][key] for key in ("b_mm", "D_mm"))
    lower = cage["bars"]
    lap = request["laps"][0]
    assembly = lap["contact_assembly"]
    partners = {
        bar["bar_id"]: {
            **bar,
            "y_from_top_mm": assembly["partner_y_mm"],
        }
        for bar in lower
        if bar["bar_id"] in PAIR
    }
    upper = [partners.get(bar["bar_id"], bar) for bar in lower]
    overlap = lower + [
        {**partner, "bar_id": f"{mark}-U"} for mark, partner in partners.items()
    ]
    intended = tuple((mark, f"{mark}-U") for mark in PAIR)
    contact = [
        math.dist(point(bar), point(partners[bar["bar_id"]]))
        for bar in lower
        if bar["bar_id"] in partners
    ]
    assert contact == [16, 16]
    clear, *governing = clearances(overlap, intended)[0]
    partner_clear, *governing_partner = next(
        row for row in clearances(overlap, intended) if row[2].endswith("-U")
    )

    end_cover = cage["nominal_cover_mm"]
    hoop_diameter = cage["tie"]["diameter_mm"]
    # The published hoop encloses the base bars. The two additions lie on
    # the flat left/right sides well beyond either corner bend.
    for mate in partners.values():
        x, y = point(mate)
        assert min(x, width - x) - 8 >= end_cover + hoop_diameter
        assert 66 <= y <= depth - 66
    # Every quadrant, tangent and tail of LX is contained in this box.
    # Exclude its four seated bars and bound clearance to every other bar
    # from outside the box. The exact seat clearance is r - Rbar - Rlink.
    unrelated = [bar for bar in lower if bar["bar_id"] not in PAIR]
    other_bar_bound = clear_from_box(unrelated, (45, 185, 405, 231), hoop_diameter)
    # Ordinary X1 is fabricated with 135° bends and 60 mm tails. Its upper
    # version translates to the y=216 seats. The opposing Y links remain
    # on the published axes, far from either new side bar.
    hook_extent = (15 + 60) / math.sqrt(2)
    ordinary_x1_bound = {
        label: clear_from_box(unrelated, (45, y - hook_extent, 405, y + 15), 10)
        for label, y in (("lower", 200), ("upper", 216))
    }
    y_link_partner_bound = min(
        clear_from_box(partners.values(), bounds, 10)
        for bounds in (
            (140, 45, 155 + hook_extent, 505),
            (295 - hook_extent, 45, 310, 505),
        )
    )
    assert other_bar_bound >= 0
    assert min(ordinary_x1_bound.values()) >= 0 and y_link_partner_bound >= 0
    steel_area = sum(area(bar["diameter_mm"]) for bar in overlap)
    return (
        lower,
        upper,
        {
            "partner_centres_mm": {mark: point(bar) for mark, bar in partners.items()},
            "lower_centres_mm": {bar["bar_id"]: point(bar) for bar in lower},
            "contact_separation_mm": 16,
            "minimum_unrelated_clear_mm": clear,
            "minimum_unrelated_clear_limit_mm": 25,
            "governing_unrelated_pair": governing,
            "minimum_partner_to_unrelated_clear_mm": partner_clear,
            "governing_partner_clear_pair": governing_partner,
            "overlap_steel_area_mm2": steel_area,
            "overlap_steel_ratio": steel_area / (width * depth),
            "overlap_steel_ratio_limit": 0.04,
            "spliced_bar_fraction": len(PAIR) / len(lower),
            "max_side_face_bar_pitch_mm": 488 - 200,
            "side_face_bar_pitch_limit_mm": 300,
            "restrained_side_span_mm": 488 - 62,
            "restrained_side_span_limit_mm": 48 * hoop_diameter,
            "lx_minimum_cover_mm": 45 - hoop_diameter / 2,
            "lx_required_cover_mm": end_cover,
            "lx_seat_clear_mm": 15 - (16 + hoop_diameter) / 2,
            "lx_unrelated_bar_lower_bound_mm": other_bar_bound,
            "x1_unrelated_bar_lower_bounds_mm": ordinary_x1_bound,
            "y_links_to_partner_lower_bound_mm": y_link_partner_bound,
            "lx_tail_to_tail_clear_mm": 330
            - 2 * assembly["hook_tail_mm"]
            - hoop_diameter,
        },
    )


def placements(request):
    hoops = sorted(
        {
            station
            for zone in request["tie_zones"]
            for station in range(zone["start_mm"], zone["end_mm"] + 1, zone["pitch_mm"])
        }
    )
    levels = {
        **{request["reinforcement"]["tie"]["tie_id"]: hoops},
        **{
            link["tie_id"]: [station + link["station_offset_mm"] for station in hoops]
            for link in request["reinforcement"]["cross_ties"]
        },
    }
    lap = request["laps"][0]
    start, end = lap["start_mm"], lap["end_mm"]
    x_levels = levels["X1"]
    in_lap = [z for z in x_levels if start < z < end]
    assert start not in x_levels and end not in x_levels
    levels["X1"] = [z for z in x_levels if z not in in_lap]
    levels[LAP_MARK] = in_lap
    distances = [
        start - max(z for z in x_levels if z < start),
        in_lap[0] - start,
        end - in_lap[-1],
        min(z for z in x_levels if z > end) - end,
    ]
    all_levels = sorted(z for stations in levels.values() for z in stations)
    return levels, distances, min(b - a for a, b in pairwise(all_levels)) - 10


def quantities(request, lower, upper, levels):
    start, end = (request["laps"][0][key] for key in ("start_mm", "end_mm"))
    first = -request["end_detail"]["start_straight_mm"]
    last = (
        request["geometry"]["unsupported_length_mm"]
        + request["end_detail"]["end_straight_mm"]
    )
    long_pieces = {}
    for old, new in zip(lower, upper, strict=True):
        mark = old["bar_id"]
        ranges = ((mark, old, first, last),)
        if mark in PAIR:
            ranges = ((f"{mark}-L", old, first, end), (f"{mark}-U", new, start, last))
        for name, bar, low, high in ranges:
            long_pieces[name] = {
                "parent_bar_id": mark,
                "diameter_mm": bar["diameter_mm"],
                "centre_mm": point(bar),
                "start_mm": low,
                "end_mm": high,
                "cut_mm": high - low,
            }
    # Ordinary 135° links retain their checked cut when the X1 seats
    # translate. LX uses four quadrants, two tangents and two 80 mm tails.
    allowance = 2 * (15 * math.radians(135) + 60)
    lengths = {
        "HOOP": request["transverse_cut_schedule"]["cut_lengths_mm"]["HOOP"],
        "Y1": 430 + allowance,
        "Y2": 430 + allowance,
        "X1": 330 + allowance,
        LAP_MARK: 330 + 2 * math.pi * 15 + 2 * 16 + 2 * 80,
    }
    cuts = {
        mark: (1, piece["cut_mm"], piece["diameter_mm"])
        for mark, piece in long_pieces.items()
    }
    cuts.update(
        {mark: (len(stations), lengths[mark], 10) for mark, stations in levels.items()}
    )
    return {
        "longitudinal_pieces": long_pieces,
        "cuts_qty_length_diameter": cuts,
        "bbs_quantity": sum(count for count, _, _ in cuts.values()),
        "bbs_total_mm": sum(count * cut for count, cut, _ in cuts.values()),
        "bbs_mass_kg": sum(
            count * cut * area(dia) * 7850e-9 for count, cut, dia in cuts.values()
        ),
    }


def action_checks(request, lower, upper):
    geometry, materials = request["geometry"], request["materials"]
    rows = {}
    start, end = (request["laps"][0][key] for key in ("start_mm", "end_mm"))
    for action in request["actions"]:
        z = action["check_station_mm"]
        effective = {"lower": lower} if z < start else {"upper": upper}
        if start <= z <= end:
            effective = {"lower": lower, "upper": upper}
        sections = {
            label: section_reference(
                {
                    "geometry": geometry,
                    "materials": materials,
                    "reinforcement": {"bars": bars},
                    "actions": action,
                },
                samples=90,
            )
            for label, bars in effective.items()
        }
        pitch = min(
            zone["pitch_mm"]
            for zone in request["tie_zones"]
            if zone["start_mm"] <= z <= zone["end_mm"]
        )
        rows[action["combination_id"]] = {
            "station_mm": z,
            "sections": sections,
            "governing_section": max(
                sections, key=lambda k: sections[k]["governing_ratio"]
            ),
            "shear": shear(action, pitch, geometry["b_mm"], geometry["D_mm"]),
        }
    return rows


def fixture():
    request = specimen(
        json.loads(BASE.read_text())["cases"]["mixed_continuous"]["request"]
    )
    geometry = request["geometry"]
    b, d = geometry["b_mm"], geometry["D_mm"]
    lower, upper, geometry_checks_expected = geometry_checks(request)
    levels, distances, link_clear = placements(request)
    actions = action_checks(request, lower, upper)
    assert all(
        section["strength_status"] == "PASS"
        for row in actions.values()
        for section in row["sections"].values()
    )
    assert all(row["shear"]["utilization"] < 1 for row in actions.values())
    tension = {str(dia): dia * 0.87 * 500 / (4 * 1.5 * 1.6) for dia in (16, 20)}
    plain_lap = tension["16"] / 1.25
    required = max(1.1 * plain_lap, 24 * 16)
    lap = request["laps"][0]
    provided = lap["end_mm"] - lap["start_mm"]
    assert provided >= required and 5 <= min(distances) <= max(distances) <= 4 * 16
    assert link_clear == 5

    # U2 uses constant Pu and Mx, with linear My and constant Vx. Bound
    # absolute My at the ends of the declared synthetic compression interval.
    interval = request["approved_lap_zone"]
    u2 = request["actions"][1]
    end_moments = [
        u2["my_knm"] + u2["vx_kn"] * (z - u2["check_station_mm"]) / 1000
        for z in (interval["start_mm"], interval["end_mm"])
    ]
    compression = gross_kern_stress(
        u2["pu_kn"], abs(u2["mx_knm"]), max(map(abs, end_moments)), b, d
    )
    assert compression > 0
    expected = {
        "status": "PASS",
        "checked_bbs_available": True,
        "provided_lap_mm": provided,
        "unadjusted_compression_development_mm": plain_lap,
        "required_contact_lap_mm": required,
        "length_margin_mm": provided - required,
        "maximum_lap_hoop_pitch_mm": 80,
        "approved_pitch_limit_mm": interval["max_tie_pitch_mm"],
        "required_end_projection_by_diameter_mm": tension,
        "governing_end_projection_diameter_mm": 20,
        "restraint_distances_outer_inner_inner_outer_mm": distances,
        "maximum_restraint_distance_mm": 4 * 16,
        "minimum_restraint_distance_mm": 5,
        "transverse_stations_mm": levels,
        "minimum_transverse_level_clear_mm": link_clear,
        "minimum_end_face_link_cover_mm": geometry["unsupported_length_mm"]
        - levels["X1"][-1]
        - 5,
        "u2_interval_compression": {
            "start_mm": interval["start_mm"],
            "end_mm": interval["end_mm"],
            "mx_constant_knm": u2["mx_knm"],
            "my_at_ends_knm": end_moments,
            "minimum_gross_stress_nmm2": compression,
        },
        "geometry": geometry_checks_expected,
        "actions": actions,
        "governing_shear_row": max(
            actions, key=lambda k: actions[k]["shear"]["utilization"]
        ),
        "governing_section_row": max(
            actions,
            key=lambda k: max(
                s["governing_ratio"] for s in actions[k]["sections"].values()
            ),
        ),
        **quantities(request, lower, upper, levels),
    }
    cases = {"mixed_contact_splice": {"request": request, "expected": expected}}
    for name in (
        "short_lap",
        "congested_partner",
        "missing_end_restraint",
        "short_anchor",
        "inadequate_shear",
        "numeric_only",
        "missing_compression_basis",
    ):
        control = deepcopy(request)
        control["identity"]["case_id"] += f"-{name}"
        splice = control["laps"][0]
        status = "FAIL"
        if name == "short_lap":
            splice.update(start_mm=1165, end_mm=1765)
            _, support, _ = placements(control)
            assert 5 <= min(support) <= max(support) <= 64
            actual = splice["end_mm"] - splice["start_mm"]
            assert plain_lap < actual < required
            values = dict(provided_lap_mm=actual, required_contact_lap_mm=required)
            issue = "COLUMN.LAP_LENGTH"
        elif name == "congested_partner":
            inner = next(
                bar for bar in control["reinforcement"]["bars"] if bar["bar_id"] == "I1"
            )
            inner.update(x_from_left_mm=87, y_from_top_mm=245)
            before, after, checks = geometry_checks(control)
            assert clearances(before)[0][0] >= 25
            assert clearances(after)[0][0] < 25
            assert checks["lx_unrelated_bar_lower_bound_mm"] >= 0
            values = {
                "governing_pair": checks["governing_unrelated_pair"],
                "minimum_clear_mm": checks["minimum_unrelated_clear_mm"],
                "required_clear_mm": 25,
            }
            issue = "COLUMN.LAP_CLEAR_SPACING"
        elif name == "missing_end_restraint":
            splice.update(start_mm=1155, end_mm=1795)
            _, support, _ = placements(control)
            assert max(support) > 64
            values = dict(restraint_distances_mm=support, maximum_mm=64)
            issue = "COLUMN.LAP_END_RESTRAINT"
        elif name == "short_anchor":
            control["end_detail"]["end_straight_mm"] = 800
            assert tension["16"] < 800 < tension["20"]
            values = dict(
                provided_mm=800, required_mm=tension["20"], governing_diameter_mm=20
            )
            issue = "COLUMN.END_DEVELOPMENT"
        elif name == "inadequate_shear":
            control["actions"][0]["vy_kn"] = 400
            values = shear(control["actions"][0], 100, b, d)
            assert values["capacity_kn"] < 400 < values["crushing_kn"]
            issue = "COLUMN.SHEAR_CAPACITY"
        elif name == "numeric_only":
            del splice["contact_assembly"]
            status, issue, values = "HOLD", "COLUMN.LAP_ASSEMBLY_REQUIRED", {}
        else:
            splice["contact_assembly"]["compression_reference"] = None
            status, issue, values = "HOLD", "COLUMN.LAP_COMPRESSION_BASIS", {}
        cases[name] = {
            "request": control,
            "expected": {
                "status": status,
                "governing_issue": issue,
                "checked_bbs_available": False,
                **values,
            },
        }
    return {
        "schema_version": "library-030-col07-mixed-splice-reference/v1",
        "frozen_source_base": "99e93e4ba77169333c6779f24b2dd2af263c9cc9",
        "base_fixture": BASE.name,
        "base_fixture_sha256": hashlib.sha256(BASE.read_bytes()).hexdigest(),
        "sources": [
            "IS 456:2000 Clauses 25.4, 26.2, 26.3.2, 26.4, 26.5.3, 38.1, 39 and 40 and Tables 19 and 20.",
            "https://www.cracindia.in/admin/uploads/IS-456.pdf",
            "COL03 independent strip quadrature and fixed-Pu demand ray. Evaluate both transferred bar layouts in the overlap.",
            "COL07 mixed continuous hoop register and positioned link bends. X1 keeps its original 135 degree geometry outside the lap.",
            "COL07 contact reference uses the 10% conservative two-bar contact allowance and an inner/outer link each within 4d of each end.",
        ],
        "scope": "One ordinary braced short column with nominally straight equal-16 mm contact mates in the mixed 16/20 mm cage. Synthetic design rows and an explicitly declared U2 interval. No imported or seismic design claim.",
        "absolute_tolerances": {
            "geometry_and_cut_mm": 0.001,
            "shear_kn": 0.001,
            "section_capacity_knm": 0.12,
            "utilization": 0.001,
            "weight_kg": 0.001,
        },
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    data = json.loads(json.dumps(fixture(), allow_nan=False))
    if args.freeze:
        FIXTURE.write_text(json.dumps(data, indent=2) + "\n")
    elif data != json.loads(FIXTURE.read_text()):
        raise SystemExit("COL07 mixed-splice reference drifted")
    for name, case in data["cases"].items():
        print(f"{name}: expected {case['expected']['status']}")


if __name__ == "__main__":
    main()
