"""Freeze one BEAM05 T-beam lap from independent statics and section equilibrium."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import pairwise
from pathlib import Path

from check_library_029_beam05_flanged_reference import TABLE_19
from check_library_029_beam_sections_reference import section
from check_library_030_beam05_lap_reference import build as rectangular_reference

HERE = Path(__file__).resolve().parent
T_CUTOFF = HERE / "library-030-beam05-layered-cutoff.json"
RECTANGLE = HERE / "library-030-beam05-layered-lap.json"
TARGET = HERE / "library-030-beam05-t-lap-reference.json"
BASE = "1bb7c55b8a4ff99812387fde6b6b52eb5f8e1493"
LOADS_KNM = {"U1": 24, "U2": 32}


def _span_actions(load, x_mm, *, right_span=False):
    # Three-moment support solution for equal 4 m UDL spans with simple ends.
    span_mm = 4000
    reaction = 3 * load * span_mm / (8 * 1000)
    distance = (2 * span_mm - x_mm if right_span else x_mm) / 1000
    moment = reaction * distance - load * distance**2 / 2
    shear = reaction - load * distance
    return moment, -shear if right_span else shear


def _check_bound_statics(member):
    stations = {value["station_id"]: value for value in member["stations"]}
    for action in member["actions"]:
        station = stations[action["station_id"]]
        x_mm = station["x_mm"]
        right_span = x_mm > 4000 or (x_mm == 4000 and station["side"] == "RIGHT")
        moment, shear = _span_actions(
            LOADS_KNM[action["combination_id"]], x_mm, right_span=right_span
        )
        assert math.isclose(action["mu_knm"], moment, abs_tol=1e-9)
        assert math.isclose(action["vu_kn"], shear, abs_tol=1e-9)
        assert action["tu_knm"] == 0


def requests(rectangle, published):
    # Retain the previously qualified rectangular lap cage and its load rows.
    # It matches the published T multilayer profile after omission of B2-3.
    request = deepcopy(rectangle)
    member, parent = request["member"], published["member"]
    inherited = (
        "width_mm",
        "depth_mm",
        "fck_nmm2",
        "fy_nmm2",
        "supports",
        "straight_bars",
        "clear_cover_mm",
        "aggregate_size_mm",
        "link_diameter_mm",
        "link_spacing_mm",
        "link_fy_nmm2",
    )
    assert all(member[key] == parent[key] for key in inherited)
    assert request["link_detail"] == published["link_detail"]
    assert member["bars"] == [bar for bar in parent["bars"] if bar["bar_id"] != "B2-3"]
    member_rows = {row["row_id"]: row for row in member["actions"]}
    assert all(
        member_rows[row["row_id"]] == row
        for row in parent["actions"]
        if row["station_id"] not in {"CUT-THEORETICAL", "CUT-END"}
    )
    assert parent["flange"]["kind"] == "t_beam"
    member["flange"] = deepcopy(parent["flange"])
    member_id = "B-T_MULTILAYER"
    member.update(
        member_id=member_id,
        analysis_revision=f"{member_id}-A1",
        current_analysis_revision=f"{member_id}-A1",
        reinforcement_revision=f"{member_id}-R1",
        source_reference="BEAM05 multilayer T beam, equal-EI two-span three-moment actions",
    )
    request["identity"]["member_id"] = member_id
    cases = {}
    for name in (
        "t_lap",
        "short_overlap",
        "congested_partner",
        "missing_lap_action",
        "stale_analysis",
    ):
        case = deepcopy(request)
        case["identity"]["case_id"] = name
        case["member"]["reinforcement_revision"] += f"-{name}"
        cases[name] = case
    short = cases["short_overlap"]["member"]
    limits = {"LAP-MID": 1950, "LAP-END": 2350}
    for station in short["stations"]:
        if station["station_id"] in limits:
            station["x_mm"] = limits[station["station_id"]]
    for row in short["actions"]:
        if row["station_id"] in limits:
            row["mu_knm"], row["vu_kn"] = _span_actions(
                LOADS_KNM[row["combination_id"]], limits[row["station_id"]]
            )
    cases["congested_partner"]["lap"]["partner_x_from_left_mm"] = 215.0
    missing = cases["missing_lap_action"]["member"]
    missing["actions"] = [
        row for row in missing["actions"] if row["row_id"] != "U2:LAP-MID"
    ]
    cases["stale_analysis"]["member"]["current_analysis_revision"] += "-EDITED"
    return {"rectangular_control": rectangle, **cases}


def _strengths(member, layouts):
    table19 = TABLE_19[member["fck_nmm2"]]
    flange = member.get("flange")
    web = member["width_mm"]
    physical = web
    effective = None
    if flange is not None:
        assert flange["monolithic"]
        # Both positive-moment zeros follow from the equal-span UDL parabola.
        zero_distance = 2 * (3 * 4000 / 8)
        assert flange["zero_moment_distance_mm"] == zero_distance
        physical += flange["left_overhang_mm"] + flange["right_overhang_mm"]
        thickness = flange["thickness_mm"]
        if flange["kind"] == "t_beam":
            effective = min(physical, web + zero_distance / 6 + 6 * thickness)
        else:
            assert flange["kind"] == "l_beam"
            assert flange["left_overhang_mm"] == 0 < flange["right_overhang_mm"]
            effective = min(physical, web + zero_distance / 12 + 3 * thickness)
    capacities = {}
    for name, bars in layouts.items():
        model = {**member, "bars": bars}
        capacities[name] = {
            **{
                face: section(model, face, effective, table19)
                for face in ("bottom", "top")
            },
            "bottom_web": section(model, "bottom", None, table19),
        }
        assert all(not value["over_reinforced"] for value in capacities[name].values())
    for face in ("bottom", "top", "bottom_web"):
        for key in ("capacity_knm", "shear_capacity_kn", "effective_depth_mm"):
            assert math.isclose(
                capacities["upstream"][face][key], capacities["downstream"][face][key]
            )
    return physical, effective, capacities


def _governing(rows, field, face=None):
    candidates = [row for row in rows if face is None or row["tension_face"] == face]
    maximum = max(row[field] for row in candidates)
    tied = sorted(
        row["row_id"] for row in candidates if abs(row[field] - maximum) < 1e-10
    )
    return {"row_id": tied[0], "tied_row_ids": tied, "utilization": maximum}


def _support_evidence(member, checked_rows, capacities, first, last, development):
    left, inner, right = member["supports"]
    face_geometry = {
        left["centre_mm"] + left["width_mm"] / 2: (left, -1),
        inner["centre_mm"] - inner["width_mm"] / 2: (inner, 1),
        inner["centre_mm"] + inner["width_mm"] / 2: (inner, -1),
        right["centre_mm"] - right["width_mm"] / 2: (right, 1),
    }
    rows = {}
    for row in checked_rows:
        x_mm = row["station_mm"]
        if x_mm not in face_geometry:
            continue
        support, direction = face_geometry[x_mm]
        at_end = support in (left, right)
        path_end = first if direction < 0 else last
        straight = direction * (path_end - x_mm)
        assert straight >= development
        check = {
            "support_id": support["support_id"],
            "direction": "decreasing_x" if direction < 0 else "increasing_x",
            "straight_available_mm": straight,
            "development_required_mm": development,
            "checked_bar_ids": (
                row["layout_bar_ids"]
                if at_end
                else [mark for mark in row["layout_bar_ids"] if mark.startswith("T")]
            ),
        }
        if at_end:
            moment = capacities[row["layout"]]["bottom_web"]["capacity_knm"]
            over_centre = direction * (path_end - support["centre_mm"])
            flexure_shear = 1000 * moment / abs(row["shear_kn"]) + over_centre
            limit = min(3 * straight, flexure_shear)
            assert limit >= development
            check["positive_support"] = {
                "bottom_bar_ids": [
                    mark for mark in row["layout_bar_ids"] if mark.startswith("B")
                ],
                "web_only_capacity_knm": moment,
                "extension_beyond_centre_mm": over_centre,
                "three_times_projection_mm": 3 * straight,
                "m_over_v_plus_extension_mm": flexure_shear,
                "available_mm": limit,
            }
        rows[row["row_id"]] = check
    return rows


def _takeoff(request, layout, original, partner, overlap):
    member, detail = request["member"], request["link_detail"]
    diameter = member["link_diameter_mm"]
    cover = member["clear_cover_mm"]
    inset = cover + diameter / 2
    width, depth = member["width_mm"] - 2 * inset, member["depth_mm"] - 2 * inset
    radius = detail["internal_bend_radius_mm"] + diameter / 2
    # Five tangent fillets replace two radius lengths with each quarter arc.
    link_cut = (
        2 * detail["hook_vertex_leg_mm"]
        + width
        + 2 * depth
        + math.hypot(width, detail["hook_plane_offset_mm"])
        + 5 * radius * (math.pi / 2 - 2)
    )
    grid = list(
        range(
            detail["first_station_mm"],
            detail["last_station_mm"] + 1,
            member["link_spacing_mm"],
        )
    )
    assert grid[-1] == detail["last_station_mm"]
    web, height = member["width_mm"], member["depth_mm"]

    def clear_to_straight_leg(bar):
        x, y = bar["x_from_left_mm"], bar["y_from_top_mm"]
        centre_distance = min(x - inset, web - inset - x, y - inset, height - inset - y)
        return centre_distance - (bar["diameter_mm"] + diameter) / 2

    straight_leg_clearance = min(clear_to_straight_leg(bar) for bar in layout)
    assert straight_leg_clearance >= 0
    outline = [[0, 0], [web, 0], [web, height], [0, height]]
    flange = member.get("flange")
    if flange is not None:
        left = -flange["left_overhang_mm"]
        right = web + flange["right_overhang_mm"]
        thickness = flange["thickness_mm"]
        outline = [
            [left, 0],
            [right, 0],
            [right, thickness],
            [web, thickness],
            [web, height],
            [0, height],
        ]
        if left < 0:
            outline.extend(([0, thickness], [left, thickness]))
    first, last = (member["straight_bars"][f"{end}_mm"] for end in ("start", "end"))
    overlap_start, overlap_end = overlap
    paths = {
        bar["bar_id"]: [
            overlap_start if bar == partner else first,
            overlap_end if bar == original else last,
        ]
        for bar in layout
    }
    group = Counter()
    for bar in layout:
        suffix = "-lap-I" if bar == original else "-lap-J" if bar == partner else ""
        mark = f"{member['member_id']}-{bar['face']}-L{bar['layer']}-D{bar['diameter_mm']:g}{suffix}"
        start, end = paths[bar["bar_id"]]
        group[mark, bar["diameter_mm"], end - start] += 1
    group[member["member_id"] + f"-L{diameter:g}", diameter, link_cut] = len(grid)
    return {
        "drawing": {
            "bar_extents_mm": paths,
            "section_outline_mm": outline,
            "web_link_centreline_bounds_mm": [
                inset,
                inset,
                web - inset,
                height - inset,
            ],
            "minimum_bar_to_straight_link_leg_clearance_mm": straight_leg_clearance,
            "section_centres": {
                name: {
                    bar["bar_id"]: [
                        bar["x_from_left_mm"],
                        bar["y_from_top_mm"],
                        bar["layer"],
                    ]
                    for bar in layout
                    if not (
                        name == "before"
                        and bar == partner
                        or name == "after"
                        and bar == original
                    )
                }
                for name in ("before", "overlap", "after")
            },
            "link_stations_mm": grid,
            "links_inside_overlap_mm": [
                x for x in grid if overlap_start <= x <= overlap_end
            ],
        },
        "bbs": {
            "rows_qty_cut_mm_diameter_mm": {
                mark: [quantity, cut, dia]
                for (mark, dia, cut), quantity in group.items()
            },
            "total_quantity": sum(group.values()),
            "total_length_mm": math.fsum(
                quantity * cut for (_, _, cut), quantity in group.items()
            ),
            "total_mass_kg": 7850e-9
            * math.fsum(
                quantity * cut * (math.pi * dia**2 / 4)
                for (_, dia, cut), quantity in group.items()
            ),
        },
    }


def expected(request):
    member, lap = request["member"], request["lap"]
    _check_bound_statics(member)
    stations = {row["station_id"]: row["x_mm"] for row in member["stations"]}
    start, middle, end = (
        stations[lap[f"{part}_station_id"]] for part in ("start", "middle", "end")
    )
    assert 500 < start < middle < end < 3850
    original = next(bar for bar in member["bars"] if bar["bar_id"] == lap["bar_id"])
    partner = {
        **original,
        "bar_id": lap["partner_bar_id"],
        "x_from_left_mm": lap["partner_x_from_left_mm"],
    }
    assert original["face"] == "bottom" and original["layer"] == 1
    unchanged = [bar for bar in member["bars"] if bar != original]
    outer = [bar for bar in unchanged if bar["face"] == "bottom" and bar["layer"] == 1]
    inner = [bar for bar in unchanged if bar["face"] == "bottom" and bar["layer"] == 2]
    assert {bar["x_from_left_mm"] for bar in inner} <= {
        bar["x_from_left_mm"] for bar in outer
    }
    layouts = {"upstream": [*unchanged, original], "downstream": [*unchanged, partner]}
    dia = original["diameter_mm"]
    assert dia <= 32
    development = 0.87 * member["fy_nmm2"] * dia / (4 * 1.5 * 1.6)
    required_lap = max(development, 30 * dia, 15 * dia, 200)
    overlap = end - start
    min_clear = max(dia, member["aggregate_size_mm"] + 5)
    pair_clear = abs(original["x_from_left_mm"] - partner["x_from_left_mm"]) - dia
    all_outer = sorted(bar["x_from_left_mm"] for bar in [*outer, original, partner])
    actual_clear = min(b - a - dia for a, b in pairwise(all_outer))
    vertical_clear = (
        original["y_from_top_mm"] - max(bar["y_from_top_mm"] for bar in inner) - dia
    )
    assert vertical_clear >= max(15, (2 / 3) * member["aggregate_size_mm"], dia)
    piece_cover = {
        bar["bar_id"]: min(
            bar["x_from_left_mm"],
            member["width_mm"] - bar["x_from_left_mm"],
            bar["y_from_top_mm"],
            member["depth_mm"] - bar["y_from_top_mm"],
        )
        - dia / 2
        for bar in (original, partner)
    }
    assert min(piece_cover.values()) >= 2 * dia
    physical_width, effective_width, capacities = _strengths(member, layouts)
    baseline = capacities["upstream"]
    half_cap = baseline["bottom"]["capacity_knm"] / 2
    max_moments = {}
    for cid, load in LOADS_KNM.items():
        vertex_mm = 1500
        points = [start, end] + ([vertex_mm] if start < vertex_mm < end else [])
        moments = [_span_actions(load, x)[0] for x in points]
        x_max = points[moments.index(max(moments))]
        assert 0 < min(moments) <= max(moments) < half_cap
        max_moments[cid] = {
            "maximum_station_mm": x_max,
            "maximum_moment_knm": max(moments),
            "minimum_moment_knm": min(moments),
            "half_capacity_knm": half_cap,
            "utilization": max(moments) / half_cap,
        }

    required = {
        (combo["combination_id"], station_id)
        for combo in member["combinations"]
        for station_id in combo["required_station_ids"]
    }
    supplied = {(row["combination_id"], row["station_id"]) for row in member["actions"]}
    assert supplied <= required and len(supplied) == len(member["actions"])
    issues = []
    if overlap < required_lap:
        issues.append("SPLICE.NONCOMPLIANT")
    if actual_clear < min_clear:
        issues.append("SPACING.HORIZONTAL")
    missing_rows = [f"{cid}:{sid}" for cid, sid in sorted(required - supplied)]
    if missing_rows:
        issues.append("BEAM_ACTION_MISSING")
    stale = member["analysis_revision"] != member["current_analysis_revision"]
    if stale:
        issues.append("BEAM_ANALYSIS_STALE")
    status = "HOLD" if stale or missing_rows else "FAIL" if issues else "PASS"
    result = {
        "status": status,
        "required_issue_codes": issues,
        "checked_drawing_available": status == "PASS",
        "bbs_available": status == "PASS",
        "overlap_mm": overlap,
        "required_lap_mm": required_lap,
        "pair_clear_mm": pair_clear,
        "minimum_clear_mm": actual_clear,
        "required_clear_mm": min_clear,
        "missing_required_rows": missing_rows,
        "analysis_revision": member["analysis_revision"],
        "current_analysis_revision": member["current_analysis_revision"],
    }
    if status != "PASS":
        return result

    rows = []
    for action in member["actions"]:
        x_mm = stations[action["station_id"]]
        # Both transfer layouts apply in the overlap, excluding double credit.
        active_layouts = [
            name
            for name, applies in (
                ("upstream", x_mm <= end),
                ("downstream", x_mm >= start),
            )
            if applies
        ]
        for name in active_layouts:
            moment, shear = action["mu_knm"], action["vu_kn"]
            face = "top" if moment < 0 else "bottom"
            capacity = capacities[name][face]
            shear_capacity = (
                capacity["shear_capacity_kn"]
                if moment
                else min(
                    capacities[name][side]["shear_capacity_kn"]
                    for side in ("top", "bottom")
                )
            )
            m_ratio, v_ratio = (
                abs(moment) / capacity["capacity_knm"],
                abs(shear) / shear_capacity,
            )
            assert max(m_ratio, v_ratio) < 1
            rows.append(
                {
                    "row_id": action["row_id"],
                    "station_mm": x_mm,
                    "layout": name,
                    "layout_bar_ids": [bar["bar_id"] for bar in layouts[name]],
                    "tension_face": face if moment else None,
                    "moment_knm": moment,
                    "shear_kn": shear,
                    "flexure_utilization": m_ratio,
                    "shear_utilization": v_ratio,
                    "diagnostic_only": x_mm in (0, 4000, 8000),
                }
            )
    acceptance = [row for row in rows if not row["diagnostic_only"]]
    centreline = [row for row in rows if row["diagnostic_only"]]
    minimum_link_stress = (
        0.87
        * min(member["link_fy_nmm2"], 415)
        * math.pi
        * member["link_diameter_mm"] ** 2
        / 2
        / (member["width_mm"] * member["link_spacing_mm"])
    )
    max_link_pitch = min(
        300,
        *(0.75 * baseline[face]["effective_depth_mm"] for face in ("top", "bottom")),
    )
    assert minimum_link_stress >= 0.4 and member["link_spacing_mm"] <= max_link_pitch
    bottom_bars = sum(bar["face"] == "bottom" for bar in member["bars"])
    assert 1 / bottom_bars <= 0.5
    first, last = (member["straight_bars"][f"{part}_mm"] for part in ("start", "end"))
    return {
        **result,
        "physical_width_mm": physical_width,
        "effective_flange_width_mm": effective_width,
        "cover_at_lap_pieces_mm": piece_cover,
        "vertical_clear_mm": vertical_clear,
        "spliced_bottom_fraction": 1 / bottom_bars,
        "minimum_link_reinforcement_nmm2": minimum_link_stress,
        "maximum_link_pitch_mm": max_link_pitch,
        "lap_interval_by_combination": max_moments,
        "overlap_rows": {
            row["row_id"]: {
                "moment_knm": row["moment_knm"],
                "shear_kn": row["shear_kn"],
                "half_capacity_knm": half_cap,
            }
            for row in rows
            if row["layout"] == "upstream" and start <= row["station_mm"] <= end
        },
        "strength_by_layout": capacities,
        "signed_rows": rows,
        "governing_acceptance_rows": {
            "sagging": _governing(acceptance, "flexure_utilization", "bottom"),
            "hogging": _governing(acceptance, "flexure_utilization", "top"),
            "shear": _governing(acceptance, "shear_utilization"),
        },
        "governing_centreline_diagnostics": {
            "hogging": _governing(centreline, "flexure_utilization", "top"),
            "shear": _governing(centreline, "shear_utilization"),
        },
        "support_anchorage": _support_evidence(
            member, acceptance, capacities, first, last, development
        ),
        **_takeoff(
            request, [*unchanged, original, partner], original, partner, (start, end)
        ),
    }


def fixture():
    stored_rect = json.loads(RECTANGLE.read_text())["cases"]["layered_lap"]
    assert rectangular_reference()["cases"]["layered_lap"] == stored_rect
    published = json.loads(T_CUTOFF.read_text())["cases"]["t_multilayer"]["request"]
    cases = {
        name: {"request": request, "expected": expected(request)}
        for name, request in requests(stored_rect["request"], published).items()
    }
    reference = cases["rectangular_control"]["expected"]
    t_case = cases["t_lap"]["expected"]
    for key in (
        "overlap_mm",
        "required_lap_mm",
        "pair_clear_mm",
        "minimum_clear_mm",
        "vertical_clear_mm",
    ):
        assert reference[key] == t_case[key] == stored_rect["expected"][key]
    for key in ("total_quantity", "total_length_mm", "total_mass_kg"):
        assert t_case["bbs"][key] == reference["bbs"][key]
    assert math.isclose(
        t_case["bbs"]["total_mass_kg"], stored_rect["expected"]["mass_kg"]
    )
    for face in ("top", "bottom_web"):
        assert (
            t_case["strength_by_layout"]["downstream"][face]
            == reference["strength_by_layout"]["downstream"][face]
        )
    assert (
        t_case["strength_by_layout"]["upstream"]["bottom"]["capacity_knm"]
        > reference["strength_by_layout"]["upstream"]["bottom"]["capacity_knm"]
    )
    dispositions = {
        "rectangular_control": ("PASS", []),
        "t_lap": ("PASS", []),
        "short_overlap": ("FAIL", ["SPLICE.NONCOMPLIANT"]),
        "congested_partner": ("FAIL", ["SPACING.HORIZONTAL"]),
        "missing_lap_action": ("HOLD", ["BEAM_ACTION_MISSING"]),
        "stale_analysis": ("HOLD", ["BEAM_ANALYSIS_STALE"]),
    }
    for name, (status, issues) in dispositions.items():
        assert cases[name]["expected"]["status"] == status
        assert cases[name]["expected"]["required_issue_codes"] == issues
    return {
        "fixture_version": "library-030-beam05-t-lap-reference/v1",
        "frozen_before_implementation": True,
        "frozen_production_base": BASE,
        "bound_sources": {
            "published_t_multilayer": [
                T_CUTOFF.name,
                "t_multilayer",
                sha256(T_CUTOFF.read_bytes()).hexdigest(),
            ],
            "published_rectangular_lap": [
                RECTANGLE.name,
                "layered_lap",
                sha256(RECTANGLE.read_bytes()).hexdigest(),
            ],
        },
        "sources": [
            "IS 456:2000 Cl. 23.1.2, 26.2.1, 26.2.3.3, 26.2.5, 26.3.2, 26.5.1, 38 and 40 with Table 19. https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf",
            "Published BEAM05 multilayer cutoff and separated rectangular lap, with independent three-moment actions, signed section equilibrium and link cut takeoff.",
        ],
        "method": {
            "scope": "One straight separated B1-3 Ø20 lap in the same outer-bottom layer and first clear span of the prismatic symmetric T web cage with uniform closed web links and zero torsion. Retain the two aligned inner bars from the rectangular lap. The defined reference omits B2-3.",
            "actions": "Equal 4 m spans with simple outer supports, uniform stiffness along the member and U1/U2 UDLs of 24/32 kN/m. Verify each signed M/V pair and the complete required row inventory from three-moment statics. Retain centreline diagnostics separately from acceptance rows.",
            "section": "Solve the signed strain-compatible section twice, with the original and partner layouts. Sagging uses the effective monolithic flange with neutral axis inside the flange. Hogging and shear use the web. Use one piece in each transfer layout at overlap stations.",
            "lap_window": "Check the full sagging interval from its analytical endpoints and the stationary point where it lies within the interval. Use the declared half-capacity screen as in the rectangular lap. Length uses full-stress deformed-bar flexural tension development and the straight-lap minima.",
            "support": "Use supplied support-face actions and physical bar extents. The positive support anchorage uses the web-only flexural resistance in M/V plus the extension beyond the support centre.",
            "outputs": "Bind report, elevation, the before/overlap/after T sections and BBS to the same input and checked path revisions. Draw both physical pieces in the overlap with their separate marks. Keep diagnostic reports and withhold drawing and BBS in FAIL/HOLD controls.",
        },
        "absolute_tolerances": {
            "length_mm": 0.001,
            "moment_knm": 0.01,
            "force_kn": 0.01,
            "ratio": 0.0001,
            "mass_kg": 0.001,
        },
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    data = fixture()
    if args.freeze:
        TARGET.write_text(
            json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
    else:
        assert json.loads(TARGET.read_text(encoding="utf-8")) == data
    for name, case in data["cases"].items():
        print(f"PASS independent BEAM05 T lap {name}: {case['expected']['status']}")


if __name__ == "__main__":
    main()
