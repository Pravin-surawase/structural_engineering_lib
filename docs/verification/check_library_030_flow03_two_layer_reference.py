"""Freeze the edited B05 two-layer cage independently of StructLib."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import pairwise
from pathlib import Path

from check_library_029_beam05_flanged_reference import reference_case
from check_library_029_beam_sections_reference import section
from check_library_029_flow02_reference import TABLE_19_M30

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE / "library-029-flow02-beam-catalogue.json"
TARGET = HERE / "library-030-flow03-two-layer-edit.json"
OPTION = "3x20/2x16"
BASE_REVISION = "0969c986f51c46f61c93887ab180bd862cc2b298"
CORNERS = ("T1-1", "T1-2", "B1-1", "B1-3")
PLACEMENT = {
    "source_reference": "Trial open-top form with a straight lift, bar-seat jig and ±5 mm end stops",
    "form_opening_width_mm": 270,
    "form_opening_height_mm": 570,
    "required_cover_mm": 30,
    "consolidation_access_diameter_mm": 40,
    "bar_axis_tolerance_mm": 1,
    "bar_end_tolerance_mm": 5,
    "cage_location_tolerance_mm": 5,
    "link_bound_tolerance_mm": 1,
    "link_station_tolerance_mm": 5,
    "bend_radius_tolerance_mm": 1,
    "bar_diameter_allowance_mm": 1,
    "link_diameter_allowance_mm": 1,
    "closed_hook_plane_offset_tolerance_mm": 1,
    "cross_tie_hook_tail_tolerance_mm": 2,
    "cross_tie_maximum_hook_angle_deg": 137,
}
CROSS_TIE = {
    "restrained_bar_ids": ["T1-3", "B1-2"],
    "diameter_mm": 8,
    "station_offset_mm": 60,
    "internal_bend_radius_mm": 14,
    "hook_angle_deg": 135,
    "hook_tail_mm": 64,
    "straight_leg_side": "right",
    "source_reference": "Two 135-degree inward tails; seat the top and bottom middle bars",
}


def bar_area(diameter):
    return math.pi * diameter**2 / 4


def coordinates(bars):
    return {
        bar["bar_id"]: [
            bar["x_from_left_mm"],
            bar["y_from_top_mm"],
            bar["diameter_mm"],
            bar["layer"],
        ]
        for bar in bars
    }


def placed_candidate():
    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    member = deepcopy(catalogue["request"]["member"])
    accepted = catalogue["expected"]["evaluated"][OPTION]
    assert accepted["status"] == "PASS"
    layers = [
        next(option for option in row["options"] if option["option_id"] == choice)
        for row, choice in zip(
            catalogue["request"]["layers"], OPTION.split("/"), strict=True
        )
    ]
    bars = []
    for bar, x in zip(member["bars"][:2], (66, 234), strict=True):
        bars.append(dict(bar, x_from_left_mm=x, y_from_top_mm=64))
    # The cross-tie has a permanent top engagement bar in the physical companion.
    bars.append(dict(bars[0], bar_id="T1-3", x_from_left_mm=150))
    for layer, row in enumerate(layers, start=1):
        assert len(row["x_from_left_mm"]) == (3 if layer == 1 else 2)
        xs = (66, 150, 234) if layer == 1 else (66, 234)
        for i, x in enumerate(xs, 1):
            bars.append(
                {
                    "bar_id": f"B{layer}-{i}",
                    "face": "bottom",
                    "layer": layer,
                    "diameter_mm": row["diameter_mm"],
                    "x_from_left_mm": x,
                    "y_from_top_mm": 536 if layer == 1 else 464,
                }
            )
    assert math.isclose(
        sum(bar_area(bar["diameter_mm"]) for bar in bars if bar["face"] == "bottom"),
        accepted["bottom_area_mm2"],
    )
    member["bars"] = bars
    member["clear_cover_mm"] = 40
    case = reference_case("flow03-b05", member)
    request = case["request"]
    request["member"][
        "source_reference"
    ] = "FLOW02 B05 3x20/2x16 bottom inventory on the BEAM05 fixed equal-EI two-span action reference"
    request["link_detail"]["internal_bend_radius_mm"] = 22
    request["link_detail"][
        "source_reference"
    ] = "Closed outer hoop with two anchored hook planes"
    return request


def rows(member):
    strength = {
        face: section(member, face, None, TABLE_19_M30) for face in ("top", "bottom")
    }
    assert all(not item["over_reinforced"] for item in strength.values())
    acceptance = []
    by_row = {}
    for action in member["actions"]:
        face = "top" if action["mu_knm"] < 0 else "bottom"
        capacity = strength[face]
        flexure = abs(action["mu_knm"]) / capacity["capacity_knm"]
        shear = abs(action["vu_kn"]) / capacity["shear_capacity_kn"]
        assert max(flexure, shear) < 1
        station = action["station_id"]
        by_row[action["row_id"]] = {
            "tension_face": face,
            "moment_knm": action["mu_knm"],
            "shear_kn": action["vu_kn"],
            "flexure_utilization": flexure,
            "shear_utilization": shear,
        }
        if station not in {"A", "B1", "B2", "C"}:
            acceptance.append(action["row_id"])
    return {
        "section_by_face": strength,
        "signed_rows": by_row,
        "governing_flexure_row_id": min(
            by_row, key=lambda k: (-by_row[k]["flexure_utilization"], k)
        ),
        "governing_acceptance_shear_row_id": min(
            acceptance,
            key=lambda k: (-by_row[k]["shear_utilization"], k),
        ),
    }


def interim_service(member, sagging_depth):
    # Equal prismatic spans with independently prescribed, unfactored UDLs.
    # M/EI integrates twice to R*x^3/6-q*x^4/24-q*L^3*x/48.
    q, span = 16, 4000
    support_moment = q * span**2 / 8e6
    peak_x = span * (1 + math.sqrt(33)) / 16
    reaction = 3 * q * span / 8
    width, depth = member["width_mm"], member["depth_mm"]
    inertia = width * depth**3 / 12
    ec = 5000 * math.sqrt(member["fck_nmm2"])
    modulus_of_rupture = 0.7 * math.sqrt(member["fck_nmm2"])
    mcr = modulus_of_rupture * inertia / (depth / 2) / 1e6
    assert support_moment < mcr
    deflection = abs(
        reaction * peak_x**3 / 6 - q * peak_x**4 / 24 - q * span**3 * peak_x / 48
    ) / (ec * inertia)
    return {
        "unfactored_udl_kn_per_m_per_span": q,
        "source_reference": "Declared instantaneous service replay on the checked reinforcement revision",
        "sagging_effective_depth_mm": sagging_depth,
        "effective_span_to_depth": span / sagging_depth,
        "maximum_moment_magnitude_knm": support_moment,
        "cracking_moment_knm": mcr,
        "flexural_crack_width_mm": 0,
        "maximum_instantaneous_deflection_mm": deflection,
        "controlling_station_x_mm": [peak_x, 2 * span - peak_x],
    }


def outer_bounds(member):
    inset = member["clear_cover_mm"] + member["link_diameter_mm"] / 2
    return (inset, inset, member["width_mm"] - inset, member["depth_mm"] - inset)


def worst_case_arrangement(request, placement, cross_tie):
    member, link = request["member"], request["link_detail"]
    bars = coordinates(member["bars"])
    mesh, dia_allowance = (
        placement[key] for key in ("bar_axis_tolerance_mm", "bar_diameter_allowance_mm")
    )
    bend_tol, cage_tol, bound_tol = (
        placement[key]
        for key in (
            "bend_radius_tolerance_mm",
            "cage_location_tolerance_mm",
            "link_bound_tolerance_mm",
        )
    )
    x1, y1, x2, y2 = outer_bounds(member)
    link_dia = member["link_diameter_mm"]
    max_link_dia = link_dia + placement["link_diameter_allowance_mm"]
    radius = link["internal_bend_radius_mm"]
    nominal_centre_radius = radius + link_dia / 2
    nominal_corners = (
        (x1, y1, -1, -1),
        (x2, y1, 1, -1),
        (x1, y2, -1, 1),
        (x2, y2, 1, 1),
    )
    corners = {}
    for mark, (bx, by, sx, sy) in zip(CORNERS, nominal_corners, strict=True):
        x, y, dia, _ = bars[mark]
        radial_values = []
        seat_x_values = []
        seat_y_values = []
        for realised_radius in (radius - bend_tol, radius + bend_tol):
            for hoop_dia in (link_dia, max_link_dia):
                offset = realised_radius + hoop_dia / 2
                for bound_error in (-bound_tol, bound_tol):
                    cx = bx - sx * (offset + bound_error)
                    cy = by - sy * (offset + bound_error)
                    for bar_error in (-mesh, mesh):
                        sx_distance = (x - cx) * sx + bar_error
                        sy_distance = (y - cy) * sy + bar_error
                        seat_x_values.append(sx_distance)
                        seat_y_values.append(sy_distance)
                        radial_values.append(
                            realised_radius
                            - (dia + dia_allowance) / 2
                            - math.hypot(max(0, sx_distance), max(0, sy_distance))
                        )
        seating_x, seating_y = min(seat_x_values), min(seat_y_values)
        radial = min(radial_values)
        corners[mark] = {
            "axis_mm": [x, y],
            "bend_centre_mm": [
                bx - sx * nominal_centre_radius,
                by - sy * nominal_centre_radius,
            ],
            "min_radial_clearance_mm": radial,
            "signed_seating_coordinates_mm": [seating_x, seating_y],
            "seated_through_tolerance": radius - bend_tol > 0
            and min(seating_x, seating_y) > 0
            and radial >= 0,
        }
    horizontal = {}
    for face, layer in (("top", 1), ("bottom", 1), ("bottom", 2)):
        row = sorted(
            (bar["x_from_left_mm"], bar["diameter_mm"])
            for bar in member["bars"]
            if bar["face"] == face and bar["layer"] == layer
        )
        horizontal[f"{face}-{layer}"] = [
            x_b - x_a - (d_a + d_b) / 2 - 2 * mesh - dia_allowance
            for (x_a, d_a), (x_b, d_b) in pairwise(row)
        ]
    vertical = min(
        outer[1] - inner[1] - (outer[2] + inner[2]) / 2 - 2 * mesh - dia_allowance
        for outer, inner in ((bars["B1-1"], bars["B2-1"]), (bars["B1-3"], bars["B2-2"]))
    )
    inner_depth = min(
        member["depth_mm"] - y - (dia + dia_allowance) / 2 - mesh - cage_tol
        for _, y, dia, layer in bars.values()
        if layer == 2
    )
    compressed_inner_dia = (
        max(dia for _, _, dia, layer in bars.values() if layer == 2) + dia_allowance
    )
    pitch_limit = min(
        member["width_mm"],
        member["depth_mm"],
        300,
        16 * min(item[2] for item in bars.values()),
    )
    result = {
        "outer_corner_checks": corners,
        "worst_horizontal_clearance_mm": horizontal,
        "worst_vertical_clearance_mm": vertical,
        "inner_bottom_depth_to_steel_mm": inner_depth,
        "inner_bottom_required_depth_mm": 3 * compressed_inner_dia,
        "worst_outer_hoop_cover_mm": member["clear_cover_mm"]
        - cage_tol
        - bound_tol
        - (max_link_dia - link_dia) / 2,
        "max_pitch_under_tolerance_mm": member["link_spacing_mm"]
        + 2 * placement["link_station_tolerance_mm"],
        "restraint_pitch_limit_mm": pitch_limit,
        "hoop_finished_straight_tail_mm": link["hook_vertex_leg_mm"]
        - nominal_centre_radius,
        "lift_envelope_width_mm": x2 - x1 + max_link_dia + 2 * (cage_tol + bound_tol),
        "lift_envelope_height_mm": y2 - y1 + max_link_dia + 2 * (cage_tol + bound_tol),
    }
    assert min(value["min_radial_clearance_mm"] for value in corners.values()) > 0
    assert inner_depth >= result["inner_bottom_required_depth_mm"]
    assert result["worst_outer_hoop_cover_mm"] >= placement["required_cover_mm"]
    assert result["max_pitch_under_tolerance_mm"] <= pitch_limit
    assert result["hoop_finished_straight_tail_mm"] >= 8 * link_dia

    if cross_tie is not None:
        top, bottom = (bars[key] for key in cross_tie["restrained_bar_ids"])
        assert top[0] == bottom[0] == 150 and top[2] == bottom[2] == 20
        tie_r = cross_tie["internal_bend_radius_mm"]
        max_tie_r = tie_r + bend_tol + max_link_dia / 2
        max_tail = (
            cross_tie["hook_tail_mm"] + placement["cross_tie_hook_tail_tolerance_mm"]
        )
        max_angle = math.radians(placement["cross_tie_maximum_hook_angle_deg"])
        tie_x_max = top[0] + max_tie_r
        tie_y_margin = (
            min(top[1], member["depth_mm"] - bottom[1])
            - max_tie_r
            - max_link_dia / 2
            - mesh
            - cage_tol
        )
        protected_radius = (max_link_dia + 20 + dia_allowance) / 2 + 2 * mesh
        smallest_centre_radius = tie_r - bend_tol + cross_tie["diameter_mm"] / 2
        maximum_inward_tail = -max_tail * math.cos(
            max_angle
        ) - smallest_centre_radius * math.sin(max_angle)
        clearances = []
        for mark, (x, y, _, _) in bars.items():
            if mark in cross_tie["restrained_bar_ids"]:
                continue
            if x > top[0]:
                gap = x - tie_x_max
            elif y in (top[1], bottom[1]):
                # The outward normal to either straight hook tail has a
                # horizontal projection of at least cos(45°).
                gap = (top[0] - x) / math.sqrt(2) - max_tie_r
            else:
                gap = min(
                    tie_x_max - x,
                    y - top[1] - maximum_inward_tail,
                    bottom[1] - y - maximum_inward_tail,
                )
            clearances.append(gap - protected_radius)
        other_clearance = min(clearances)
        tie_min_inside = (
            tie_r - bend_tol - (20 + dia_allowance) / 2 - math.sqrt(2) * mesh
        )
        axial_tol = placement["link_station_tolerance_mm"]
        offset = cross_tie["station_offset_mm"]
        along_beam = member["link_spacing_mm"] - offset - 2 * axial_tol - max_link_dia
        closed_shift = (
            link["hook_plane_offset_mm"]
            + placement["closed_hook_plane_offset_tolerance_mm"]
        )
        worst_grid_gap = offset - closed_shift - 2 * axial_tol - max_link_dia
        lane_width = (
            bars["B1-3"][0]
            - bottom[0]
            - (max(bars["B1-3"][2], bars["B2-2"][2]) + bottom[2]) / 2
            - 2 * mesh
            - dia_allowance
        )
        result["cross_tie"] = {
            "restraint_corner_span_mm": bars["B1-3"][0] - bars["B1-1"][0],
            "restraint_span_limit_mm": 48 * cross_tie["diameter_mm"],
            "maximum_untied_spacing_each_side_mm": 75,
            "middle_bar_spacing_each_side_mm": [
                bottom[0] - bars["B1-1"][0],
                bars["B1-3"][0] - bottom[0],
            ],
            "hook_min_clearance_to_engaged_steel_mm": tie_min_inside,
            "envelope_clearance_to_other_bars_mm": other_clearance,
            "minimum_cover_mm": tie_y_margin,
            "minimum_tail_mm": cross_tie["hook_tail_mm"]
            - placement["cross_tie_hook_tail_tolerance_mm"],
            "minimum_grid_clearance_mm": worst_grid_gap,
            "consolidation_lane_width_mm": lane_width,
            "consolidation_lane_length_mm": along_beam,
            "consolidation_opening_mm": min(lane_width, along_beam),
        }
        assert other_clearance > 0
        assert tie_min_inside > 0 and tie_y_margin >= placement["required_cover_mm"]
        assert worst_grid_gap >= member["aggregate_size_mm"] + 5
        assert result["cross_tie"]["minimum_tail_mm"] >= 6 * cross_tie["diameter_mm"]
    return result


def takeoff(request, cross_tie):
    member, hoop = request["member"], request["link_detail"]
    x1, y1, x2, y2 = outer_bounds(member)
    width, height = x2 - x1, y2 - y1
    tie_dia = member["link_diameter_mm"]
    lap_radius = hoop["internal_bend_radius_mm"] + tie_dia / 2
    hoop_cut = (
        2 * hoop["hook_vertex_leg_mm"]
        + width
        + 2 * height
        + math.hypot(width, hoop["hook_plane_offset_mm"])
        + 5 * lap_radius * (math.pi / 2 - 2)
    )
    stations = list(range(0, 8001, 200))
    assert len(stations) == 41
    start, end = (member["straight_bars"][key] for key in ("start_mm", "end_mm"))
    cut = end - start
    stock = request["stock_length_mm"]
    assert 0 < cut < stock
    mark = member["member_id"]
    bars = coordinates(member["bars"])
    counts = Counter(
        (bar["face"], bar["layer"], bar["diameter_mm"]) for bar in member["bars"]
    )
    lengths = {
        f"{mark}-{face}-L{layer}-D{dia:g}": [count, cut, dia]
        for (face, layer, dia), count in counts.items()
    }
    top_id, bottom_id = cross_tie["restrained_bar_ids"]
    tx, ty = bars[top_id][:2]
    _, by = bars[bottom_id][:2]
    d = cross_tie["diameter_mm"]
    radius = cross_tie["internal_bend_radius_mm"] + d / 2
    angle = math.radians(cross_tie["hook_angle_deg"])
    tail = cross_tie["hook_tail_mm"]
    cross_stations = [z + cross_tie["station_offset_mm"] for z in stations]
    cross_length = by - ty + 2 * (radius * angle + tail)
    gross_extension = member["supports"][0]["width_mm"] / 2 - start
    worst_extension = gross_extension - PLACEMENT["bar_end_tolerance_mm"]
    end_cover = member["supports"][0]["width_mm"] / 2 + start
    worst_end_cover = end_cover - PLACEMENT["bar_end_tolerance_mm"]
    ld = {
        key: (dia + PLACEMENT["bar_diameter_allowance_mm"])
        * 0.87
        * member["fy_nmm2"]
        / (4 * 1.5 * 1.6)
        for key, (_, _, dia, _) in bars.items()
    }
    assert worst_extension >= max(ld.values())
    assert worst_end_cover >= PLACEMENT["required_cover_mm"]
    lengths[f"{mark}-L{tie_dia:g}"] = [len(stations), hoop_cut, tie_dia]
    lengths[f"{mark}-CT{d:g}"] = [len(cross_stations), cross_length, d]
    return {
        "drawing": {
            "section_centres_and_diameters": bars,
            "bar_extents_mm": {key: [start, end] for key in bars},
            "outer_hoop_centreline_bounds_mm": [x1, y1, x2, y2],
            "outer_hoop_stations_mm": stations,
            "centre_cross_tie_stations_mm": cross_stations,
            "cross_tie_tangent_points_mm": [[tx + radius, ty], [tx + radius, by]],
            "cross_tie_tail_points_mm": [
                [
                    tx + radius * math.cos(angle) - tail * math.sin(angle),
                    ty - radius * math.sin(angle) - tail * math.cos(angle),
                ],
                [
                    tx + radius * math.cos(angle) - tail * math.sin(angle),
                    by + radius * math.sin(angle) + tail * math.cos(angle),
                ],
            ],
        },
        "bbs": {
            "rows_qty_cut_mm_diameter_mm": lengths,
            "total_quantity": sum(quantity for quantity, _, _ in lengths.values()),
            "total_length_mm": sum(
                quantity * length for quantity, length, _ in lengths.values()
            ),
            "total_mass_kg": sum(
                bar_area(dia) * quantity * length * 7850e-9
                for quantity, length, dia in lengths.values()
            ),
        },
        "end_anchorage": {
            "nominal_left_and_right_development_available_mm": gross_extension,
            "worst_development_available_mm": worst_extension,
            "minimum_end_cover_mm": worst_end_cover,
            "required_by_bar_id_mm": ld,
        },
    }


def apply_edit(base, edit, case_id):
    updated = deepcopy(base)
    updated["identity"]["case_id"] = case_id
    member = updated["member"]
    member["reinforcement_revision"] += f"-{case_id}"
    for bar in member["bars"]:
        if bar["bar_id"] == edit["bar_id"]:
            bar.update(edit)
            return updated
    raise AssertionError(f"Unknown edited bar {edit['bar_id']}")


def checked_targets(request, placement, cross_tie):
    member = request["member"]
    strengths = rows(member)
    arrangement = worst_case_arrangement(request, placement, cross_tie)
    assert all(
        c["seated_through_tolerance"]
        for c in arrangement["outer_corner_checks"].values()
    )
    assert (
        arrangement["cross_tie"]["restraint_corner_span_mm"]
        <= arrangement["cross_tie"]["restraint_span_limit_mm"]
    )
    assert (
        arrangement["cross_tie"]["consolidation_opening_mm"]
        >= placement["consolidation_access_diameter_mm"]
    )
    assert arrangement["lift_envelope_width_mm"] <= placement["form_opening_width_mm"]
    assert arrangement["lift_envelope_height_mm"] <= placement["form_opening_height_mm"]
    assert (
        min(
            n
            for row in arrangement["worst_horizontal_clearance_mm"].values()
            for n in row
        )
        >= 25
    )
    assert arrangement["worst_vertical_clearance_mm"] >= 20
    shift = placement["cage_location_tolerance_mm"] + placement["bar_axis_tolerance_mm"]
    tolerance_sections = []
    for vertical_shift in (-shift, shift):
        shifted = deepcopy(member)
        shifted["link_spacing_mm"] = arrangement["max_pitch_under_tolerance_mm"]
        for bar in shifted["bars"]:
            bar["y_from_top_mm"] += vertical_shift
        limit_rows = rows(shifted)
        tolerance_sections.append(
            {
                "common_vertical_axis_shift_mm": vertical_shift,
                "outer_link_pitch_mm": shifted["link_spacing_mm"],
                "face_checks": {
                    face: {
                        key: state[key]
                        for key in (
                            "effective_depth_mm",
                            "capacity_knm",
                            "shear_capacity_kn",
                        )
                    }
                    for face, state in limit_rows["section_by_face"].items()
                },
                "governing_flexure_row_id": limit_rows["governing_flexure_row_id"],
                "governing_acceptance_shear_row_id": limit_rows[
                    "governing_acceptance_shear_row_id"
                ],
            }
        )
    return {
        "status": "PASS",
        "report_available": True,
        "checked_drawing_available": True,
        "bbs_available": True,
        "strength": strengths,
        "placement": arrangement,
        "placement_limit_section_rechecks": tolerance_sections,
        "service": interim_service(
            request["member"],
            strengths["section_by_face"]["bottom"]["effective_depth_mm"],
        ),
        **takeoff(request, cross_tie),
    }


def fixture():
    base = placed_candidate()
    good = {"bar_id": "B2-2", "diameter_mm": 20}
    empty = {"bar_id": "T1-1", "diameter_mm": 20, "x_from_left_mm": 92}
    congested = {"bar_id": "B2-2", "diameter_mm": 20, "x_from_left_mm": 97}
    narrow = dict(PLACEMENT, form_opening_width_mm=205)
    accepted = apply_edit(base, good, "edited")
    baseline_expected = checked_targets(base, PLACEMENT, CROSS_TIE)
    edited_expected = checked_targets(accepted, PLACEMENT, CROSS_TIE)
    assert (
        edited_expected["bbs"]["total_quantity"]
        == baseline_expected["bbs"]["total_quantity"]
        == 90
    )
    assert (
        edited_expected["service"]["sagging_effective_depth_mm"]
        < baseline_expected["service"]["sagging_effective_depth_mm"]
    )
    added_mass = (bar_area(20) - bar_area(16)) * 8920 * 7850e-9
    assert math.isclose(
        edited_expected["bbs"]["total_mass_kg"]
        - baseline_expected["bbs"]["total_mass_kg"],
        added_mass,
    )
    empty_request = apply_edit(base, empty, "empty_corner")
    empty_seat = worst_case_arrangement(empty_request, PLACEMENT, CROSS_TIE)
    assert {
        mark
        for mark, check in empty_seat["outer_corner_checks"].items()
        if not check["seated_through_tolerance"]
    } == {"T1-1"}
    assert min(empty_seat["worst_horizontal_clearance_mm"]["top-1"]) == 35
    assert rows(empty_request["member"]) == baseline_expected["strength"]
    crowded = worst_case_arrangement(
        apply_edit(base, congested, "congested"), PLACEMENT, CROSS_TIE
    )
    assert crowded["worst_horizontal_clearance_mm"]["bottom-2"] == [10]
    limited = worst_case_arrangement(accepted, narrow, CROSS_TIE)
    assert limited["lift_envelope_width_mm"] > narrow["form_opening_width_mm"]
    assert all(
        d > 75
        for d in baseline_expected["placement"]["cross_tie"][
            "middle_bar_spacing_each_side_mm"
        ]
    )
    cases = {
        "edited": {
            "edit": good,
            "analysis_basis": "fixed_supplied_actions",
            "expected_member": accepted["member"],
            "expected": edited_expected,
        }
    }
    for name, edit, overrides, status, governing_check, diagnostic in (
        (
            "empty_corner",
            empty,
            {},
            "FAIL",
            "outer_corner_restraint",
            {"missing_seat_bar_id": "T1-1", "worst_top_clearance_mm": 35},
        ),
        (
            "congested",
            congested,
            {},
            "FAIL",
            "horizontal_clear_spacing",
            {"worst_clearance_mm": 10, "required_clearance_mm": 25},
        ),
        (
            "short_form_opening",
            good,
            {"placement": narrow},
            "FAIL",
            "cage_insertion",
            {
                "available_width_mm": 205,
                "required_width_mm": limited["lift_envelope_width_mm"],
            },
        ),
        (
            "missing_cross_tie",
            good,
            {"cross_tie": None},
            "FAIL",
            "intermediate_bar_restraint",
            {"bar_ids": ["T1-3", "B1-2"], "adjacent_spacing_mm": 86, "limit_mm": 75},
        ),
        (
            "stale_analysis",
            good,
            {"current_analysis_revision": "B-FLOW03-B05-A2"},
            "HOLD",
            "action_revision",
            {},
        ),
        (
            "stiffness_dependent",
            good,
            {"analysis_basis": "reinforcement_dependent_stiffness"},
            "HOLD",
            "analysis_basis",
            {},
        ),
        ("missing_placement", good, {"placement": None}, "HOLD", "placement_basis", {}),
    ):
        cases[name] = {
            "edit": edit,
            "analysis_basis": "fixed_supplied_actions",
            **overrides,
            "expected": {
                "status": status,
                "report_available": True,
                "checked_drawing_available": False,
                "bbs_available": False,
                "governing_check": governing_check,
                "diagnostic": diagnostic,
            },
        }
    return {
        "fixture_version": "library-030-flow03-two-layer-edit/v1",
        "source_commit": BASE_REVISION,
        "catalogue": {
            "fixture": CATALOGUE.name,
            "sha256": sha256(CATALOGUE.read_bytes()).hexdigest(),
            "accepted_b05_option": OPTION,
            "physical_companion": "The accepted bottom-inventory option with reseated outer axes and an added middle top bar for the cross-tie.",
        },
        "sources": [
            "IS 456:2000 Clauses 23.2, 26.2, 26.3, 26.4, 26.5.1.2 and 26.5.3.2; Figures 8 to 10",
            "BEAM05 two-span equal-EI signed statics and support face positions",
            "Trial assembly: preset footed links and cross-ties on longitudinal bars, then lift into the open form between registered supports. An unobstructed top-entry probe is specified between successive tie planes.",
        ],
        "base_request": base,
        "placement": PLACEMENT,
        "cross_tie": CROSS_TIE,
        "base_expected": baseline_expected,
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    data = fixture()
    payload = json.dumps(data, indent=2, allow_nan=False) + "\n"
    if args.write:
        TARGET.write_text(payload, encoding="utf-8")
    else:
        assert TARGET.read_text(encoding="utf-8") == payload
    print("Reproduced FLOW03 two PASS, four FAIL and three HOLD cases.")


if __name__ == "__main__":
    main()
