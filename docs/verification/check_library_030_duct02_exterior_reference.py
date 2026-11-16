"""Freeze the exterior DUCT02 joint using independent section and path checks."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

from _duct01_section_reference import rectangular_section
from _duct02_cage_reference import geometry
from check_library_030_duct01_interior_reference import beam_mechanism, shear_capacity

TARGET = Path(__file__).with_name("library-030-duct02-exterior-joint.json")
DIRECTIONS = ("X+", "X-", "Y+", "Y-")
COLUMN_ENDS = ("upper", "lower")


def area_mm2(diameter_mm):
    return math.pi * diameter_mm**2 / 4


def specimen():
    """Declared geometry and action inventory for the local exterior specimen."""
    request = {
        "joint_id": "J2",
        "topology": "exterior_x_minus",
        "action_revision": "DUCT02-DECLARED-R1",
        "cage_action_revision": "DUCT02-DECLARED-R1",
        "column_width_mm": 600,
        "joint_depth_mm": 745,
        "beam_width_mm": {"X": 480, "Y": 480},
        "column_bar_mm": 32,
        "column_bar_edge_mm": 89.5,
        "beam_bar_mm": {"X": 20, "Y": 25},
        "beam_axes_mm": {"X": [125, 175, 425, 475], "Y": [156, 236, 364, 444]},
        "beam_top_z_mm": {"X": 70, "Y": 160},
        "x_hooks": {
            "TOP": {"tip_x_mm": 520, "tail_mm": 500},
            "BOTTOM": {"tip_x_mm": 472, "tail_mm": 529},
        },
        "x_hook_radius_mm": 50,
        "y_straight_each_side_mm": 1450,
        "column_cover_mm": 49,
        "column_link_mm": 16,
        "column_link_radius_mm": 40,
        "column_link_overlap_half_mm": 31,
        "column_cross_tie_axis_y_mm": 302,
        "column_link_tail_mm": 136,
        "column_link_ramp_run_mm": 60,
        "link_group_offset_mm": 20,
        "joint_hoop_centres_mm": [26, 115, 208, 303, 385, 462, 533, 630, 719],
        "column_end_link_first_mm": 35,
        "column_end_pitch_mm": 65,
        "column_end_confinement_length_mm": 630,
        "column_clear_heights_mm": {"upper": 3400, "lower": 3600},
        "mechanism_inflection_offsets_mm": {"upper": 1700, "lower": 1800},
        "beam_clear_spans_mm": {
            "X": {"minus": 4300},
            "Y": {"minus": 4500, "plus": 4700},
        },
        "beam_dead_plus_live_kn_m": {
            "X": {"minus": 30},
            "Y": {"minus": 31, "plus": 32},
        },
        "beam_link_mm": 10,
        "beam_pitch_mm": 75,
        "beam_first_link_mm": 30,
        "beam_inner_link_offset_mm": 16,
        "beam_link_centre_radius_mm": {"X": 25, "Y": 28},
        "beam_link_seat_inset_mm": {"X": 22, "Y": 23},
        "beam_link_hook_tail_mm": 85,
        "column_fck_mpa": 30,
        "beam_fck_mpa": 30,
        "joint_fck_mpa": 30,
        "longitudinal_fy_mpa": 500,
        "link_fy_mpa": 415,
        "longitudinal_grade": "Fe500D",
        "transverse_grade": "Fe415D",
        "required_beam_cover_mm": 30,
        "required_column_cover_mm": 40,
        "aggregate_max_mm": 20,
        "axis_tolerance_mm": 1,
        "diameter_overage_mm": 0.5,
        "tie_station_tolerance_mm": 1,
        "anchor_cut_length_tolerance_mm": 2,
        "compaction_head_mm": 40,
        "assembly": (
            "Use prebent links and hooks with temporary positioning during cage assembly. "
            "The local reference checks final placement and a vertical compaction corridor. "
            "The site insertion sequence and support arrangements require separate verification."
        ),
    }
    directions = {}
    for index, direction in enumerate(DIRECTIONS):
        plane, sway = direction
        directions[direction] = [
            {
                "combination_id": f"EQ2-{direction}-{row + 1}",
                "upper_axial_compression_kn": 720 + 25 * index + 40 * row,
                "beam_on_joint_downward_shear_kn": {
                    side: (70 if side == "minus" else -15) + 6 * row + 4 * index
                    for side in request["beam_clear_spans_mm"][plane]
                },
                "analysis_column_shear_magnitude_kn": 160 + 10 * index + 7 * row,
                "beam_axial_kn": 0,
                "sway": sway,
            }
            for row in range(2)
        ]
    request["directions"] = directions
    return request


def anchorage(request):
    """Check both 90° returns and the continuous orthogonal bars."""
    fy = request["longitudinal_fy_mpa"]
    bend_radius = request["x_hook_radius_mm"]
    width = request["column_width_mm"]
    cut_tolerance = request["anchor_cut_length_tolerance_mm"]
    phi = request["beam_bar_mm"]["X"]
    bond_stress = 2.4  # Table 26.2.1.1 M30, deformed in tension.
    x_development_mm = 0.87 * fy * phi / (4 * bond_stress)
    bend_credit = 8 * phi
    x_required = x_development_mm + 10 * phi - bend_credit
    # A conservative length proof counts the two straight tangents after
    # crediting the codal bend allowance. The bend arc is measured for BBS.
    x_checks = {}
    for face, hook in request["x_hooks"].items():
        run = hook["tip_x_mm"] - bend_radius
        tail = hook["tail_mm"]
        straight = run + tail
        x_checks[face] = {
            "development_mm": x_development_mm,
            "codal_bend_credit_mm": bend_credit,
            "required_mm": x_required,
            "straight_horizontal_mm": run,
            "straight_tail_mm": tail,
            "arc_length_mm": math.pi * bend_radius / 2,
            "centreline_length_beyond_face_mm": straight + math.pi * bend_radius / 2,
            "adverse_straight_length_mm": straight - cut_tolerance,
            "diameter_mm": phi,
            "arc_centreline_radius_mm": bend_radius,
            "internal_bend_diameter_mm": 2 * bend_radius - phi,
            "pass": straight - cut_tolerance >= x_required
            and 2 * bend_radius - phi >= 4 * phi,
        }
    y_phi = request["beam_bar_mm"]["Y"]
    y_development = 0.87 * fy * y_phi / (4 * bond_stress)
    y_length = request["y_straight_each_side_mm"] - cut_tolerance
    y_checks = {
        "joint_width_mm": width,
        "joint_width_required_mm": 20 * y_phi,
        "required_development_mm": y_development,
        "adverse_development_each_side_mm": y_length,
        "pass": width >= 20 * y_phi and y_length >= y_development,
    }
    return {
        "terminated_X": x_checks,
        "continuous_Y": y_checks,
        "pass": y_checks["pass"] and all(value["pass"] for value in x_checks.values()),
    }


def confinement(request):
    """Apply full special confinement using actual split link-leg spacing."""
    w = request["column_width_mm"]
    fck_end = request["column_fck_mpa"]
    fck_joint = request["joint_fck_mpa"]
    fy = request["link_fy_mpa"]
    dia = request["column_link_mm"]
    cover = request["column_cover_mm"]
    r = request["column_link_radius_mm"]
    z = request["joint_hoop_centres_mm"]
    station_tol = request["tie_station_tolerance_mm"]
    outside = (w - 2 * cover) ** 2
    leg_inset = cover + dia / 2
    overlap_half = request["column_link_overlap_half_mm"]
    leg_x = [
        leg_inset,
        w / 2 - overlap_half,
        w / 2 + overlap_half,
        w - leg_inset,
    ]
    leg_y = [leg_inset, request["column_cross_tie_axis_y_mm"] - r, w - leg_inset]
    h_x = max(b - a for a, b in zip(leg_x, leg_x[1:])) + dia
    h_y = max(b - a for a, b in zip(leg_y, leg_y[1:])) + dia
    h = max(h_x, h_y)
    adverse_h = h + 2 * request["axis_tolerance_mm"]
    pitch = max(b - a for a, b in zip(z, z[1:])) + 2 * station_tol
    end_pitch = request["column_end_pitch_mm"] + 2 * station_tol
    first_end = request["column_end_link_first_mm"]
    transition = (
        max(z[0] + first_end, request["joint_depth_mm"] - z[-1] + first_end)
        + 2 * station_tol
    )
    limit = min(w / 4, 6 * request["column_bar_mm"], 100)

    def required(pitch_mm, fck_mpa):
        fact = pitch_mm * adverse_h * fck_mpa / fy
        return max(0.18 * fact * (w**2 / outside - 1), 0.05 * fact)

    joint_ash, end_ash = required(pitch, fck_joint), required(end_pitch, fck_end)
    required_length = max(w, max(request["column_clear_heights_mm"].values()) / 6, 450)
    supplied_ash = area_mm2(dia)
    checks = {
        "joint_pitch": pitch <= min(150, limit),
        "end_pitch": max(end_pitch, transition) <= limit,
        "split_legs": adverse_h <= 300,
        "full_joint_ash": supplied_ash >= joint_ash,
        "full_end_ash": supplied_ash >= end_ash,
        "end_confinement_length": request["column_end_confinement_length_mm"]
        >= required_length,
        "link_hook_tails": request["column_link_tail_mm"] >= max(8 * dia, 75),
    }
    return {
        "required_fraction": 1.0,
        "leg_planes_x_mm": leg_x,
        "leg_planes_y_mm": leg_y,
        "outside_confined_core_area_mm2": outside,
        "h_mm": h,
        "adverse_h_mm": adverse_h,
        "joint_pitch_mm": pitch,
        "column_end_pitch_mm": end_pitch,
        "joint_to_adjacent_pitch_mm": transition,
        "pitch_limit_mm": limit,
        "joint_required_ash_mm2": joint_ash,
        "end_required_ash_mm2": end_ash,
        "provided_ash_mm2": supplied_ash,
        "required_end_confinement_length_mm": required_length,
        "checks": checks,
        "pass": all(checks.values()),
    }


def _section_data(request):
    """Independent steel/concrete equilibrium for both symmetric beam sections."""
    fy = request["longitudinal_fy_mpa"]
    D = request["joint_depth_mm"]
    fck = request["beam_fck_mpa"]
    beams = {}
    mechanisms = {}
    for plane, axes in request["beam_axes_mm"].items():
        b = request["beam_width_mm"][plane]
        phi = request["beam_bar_mm"][plane]
        y = request["beam_top_z_mm"][plane]
        count = len(axes)
        beams[plane] = rectangular_section(
            b, D, fck, fy, ((y, count, phi), (D - y, count, phi))
        )
        mechanisms[plane] = beam_mechanism(
            {
                "beam_fck_mpa": fck,
                "longitudinal_fy_mpa": fy,
                "beam_width_mm": b,
                "joint_depth_mm": D,
                "beam_axis_across_column_mm": axes,
                "beam_bar_mm": phi,
            },
            y,
        )
    return beams, mechanisms


def _column_axial(action):
    up = action["upper_axial_compression_kn"]
    return {
        "upper": up,
        "lower": (
            up
            + sum(action["beam_on_joint_downward_shear_kn"].values())
            + action.get("orthogonal_downward_reaction_kn", 0)
        ),
    }


def _column_sections(request):
    w = request["column_width_mm"]
    edge = request["column_bar_edge_mm"]
    phi = request["column_bar_mm"]
    layers = ((edge, 3, phi), (w / 2, 2, phi), (w - edge, 3, phi))
    responses = {end: [] for end in COLUMN_ENDS}
    for actions in request["directions"].values():
        for action in actions:
            for end, pu in _column_axial(action).items():
                response = rectangular_section(
                    w,
                    w,
                    request["column_fck_mpa"],
                    request["longitudinal_fy_mpa"],
                    layers,
                    pu,
                )
                responses[end].append(
                    {"combination_id": action["combination_id"], **response}
                )
    return responses


def _beam_reactions(request, plane, sign, moment_knm, factor):
    """Joint-face reactions from both hinges of each participating beam span."""
    result = {}
    for side, span_mm in request["beam_clear_spans_mm"][plane].items():
        span = span_mm / 1000
        gravity = 1.2 * request["beam_dead_plus_live_kn_m"][plane][side] * span / 2
        hinge = factor * (moment_knm + moment_knm) / span
        result[side] = gravity + (sign if side == "minus" else -sign) * hinge
    return result


def _beam_link_detail(request, plane):
    axes = request["beam_axes_mm"][plane]
    w = request["column_width_mm"]
    b = request["beam_width_mm"][plane]
    r = request["beam_link_centre_radius_mm"][plane]
    inset = request["beam_link_seat_inset_mm"][plane]
    depth_inset = request.get("beam_link_depth_seat_inset_mm", {}).get(plane, inset)
    phi = request["beam_bar_mm"][plane]
    tie = request["beam_link_mm"]
    depth = request["joint_depth_mm"]
    top_axis = request["beam_top_z_mm"][plane]
    tolerance = request["axis_tolerance_mm"]
    dia_increase = request["diameter_overage_mm"]
    z = top_axis - depth_inset
    edge = (w - b) / 2
    hook_seat_clear = r - math.hypot(r - inset, r - depth_inset) - (phi + tie) / 2
    hook_seat_adverse = hook_seat_clear - math.sqrt(2) * tolerance - dia_increase
    clear_h = (
        min(y - x for x, y in zip(axes, axes[1:])) - phi - 2 * tolerance - dia_increase
    )
    side_cover = axes[0] - edge - inset - tie / 2
    top_cover = z - tie / 2
    nominal_phase_gap = min(
        request["beam_inner_link_offset_mm"],
        request["beam_pitch_mm"] - request["beam_inner_link_offset_mm"],
    )
    phase_clear = (
        nominal_phase_gap - tie - 2 * request["tie_station_tolerance_mm"] - dia_increase
    )
    checks = {
        "four_outer_corner_seats_and_middle_hoop": hook_seat_adverse > 0,
        "cover": min(side_cover, top_cover) - tolerance - dia_increase / 2
        >= request["required_beam_cover_mm"],
        "row_clear": clear_h >= max(phi, request["aggregate_max_mm"] + 5),
        "nested_hoops_clear": phase_clear > 0,
        "closed_hoop_hooks": request["beam_link_hook_tail_mm"] >= max(8 * tie, 75),
    }
    return {
        "outer_across_bounds_mm": [axes[0] - inset, axes[-1] + inset],
        "middle_across_bounds_mm": [axes[1] - inset, axes[2] + inset],
        "depth_bounds_mm": [z, depth - z],
        "first_outer_station_mm": request["beam_first_link_mm"],
        "middle_station_offset_mm": request["beam_inner_link_offset_mm"],
        "pitch_mm": request["beam_pitch_mm"],
        "corner_seat_adverse_mm": hook_seat_adverse,
        "parallel_clearance_mm": clear_h,
        "hoop_phase_clearance_mm": phase_clear,
        "checks": checks,
        "pass": all(checks.values()),
    }


def _signed_checks(request, direction, beams, mechanisms, columns, transverse):
    plane, sense = direction
    sign = 1 if sense == "+" else -1
    width = request["column_width_mm"]
    depth = request["joint_depth_mm"]
    beam_width = request["beam_width_mm"][plane]
    d = depth - request["beam_top_z_mm"][plane]
    moment = beams[plane]["moment_knm"]
    mechanism = mechanisms[plane]
    count = len(request["beam_clear_spans_mm"][plane])
    phi = request["beam_bar_mm"][plane]
    link_fy = request["link_fy_mpa"]
    station_tol = request["tie_station_tolerance_mm"]
    beam_pitch = request["beam_pitch_mm"] + 2 * station_tol
    beam_pitch_limit = min(d / 4, 6 * phi, 100)
    first_link = (
        request["beam_first_link_mm"]
        + request["beam_inner_link_offset_mm"]
        + station_tol
    )
    beam_available, beam_steel, beam_max = shear_capacity(
        d, beam_width, request["beam_link_mm"], beam_pitch, link_fy, 0
    )
    hinge = _beam_reactions(request, plane, sign, moment, 1.4)
    overstrength = _beam_reactions(request, plane, sign, mechanism["moment_knm"], 1)
    signed_reaction_couple = (
        sign * (overstrength["minus"] - overstrength.get("plus", 0)) * width / 2000
    )
    arm = sum(request["mechanism_inflection_offsets_mm"].values()) + depth
    mechanism_column_v = (
        (count * mechanism["moment_knm"] + signed_reaction_couple) * 1000 / arm
    )
    joint_v = count * mechanism["tension_kn"] - mechanism_column_v
    assert mechanism_column_v > 0 and joint_v > 0
    breadth = min(width, beam_width + width / 2)
    effective_area = width * breadth
    joint_stress = joint_v * 1000 / effective_area
    three_faces = all(b >= 0.75 * width for b in request["beam_width_mm"].values())
    joint_stress_limit = (1.2 if three_faces else 1.0) * math.sqrt(
        request["joint_fck_mpa"]
    )
    min_columns = {
        end: min(responses, key=lambda row: row["moment_knm"])
        for end, responses in columns.items()
    }
    available_moment = sum(response["moment_knm"] for response in min_columns.values())
    required_moment = 1.4 * count * moment
    col_d = width - request["column_bar_edge_mm"]
    rows = []
    for action in request["directions"][direction]:
        axial = _column_axial(action)
        vertical = action["beam_on_joint_downward_shear_kn"]
        beam_rows = {}
        for side, demand_kn in hinge.items():
            demand = max(abs(demand_kn), abs(vertical[side]))
            beam_rows[side] = {
                "signed_near_hinge_moment_knm": (-sign if side == "minus" else sign)
                * moment,
                "analysis_downward_reaction_kn": vertical[side],
                "capacity_downward_reaction_kn": demand_kn,
                "demand_kn": demand,
                "steel_capacity_kn": beam_steel,
                "concrete_crushing_cap_kn": beam_max,
                "accepted_capacity_kn": beam_available,
                "pitch_mm": beam_pitch,
                "pitch_limit_mm": beam_pitch_limit,
                "utilization": demand / beam_available,
                "pass": demand <= beam_available
                and beam_pitch <= beam_pitch_limit
                and first_link <= 50,
            }
        column_rows = {}
        for end, pu in axial.items():
            pt = 100 * 3 * area_mm2(request["column_bar_mm"]) / (width * col_d)
            assert pt >= 0.25
            multiplier = min(1.5, 1 + 3000 * pu / (30 * width**2))
            # M30 Table 19 conservative 0.25% row, with concurrent axial enhancement.
            concrete = 0.37 * multiplier * width * col_d / 1000
            capacity, steel, maximum = shear_capacity(
                col_d,
                width,
                request["column_link_mm"],
                transverse["column_end_pitch_mm"],
                link_fy,
                concrete,
            )
            design_v = required_moment * 1000 / request["column_clear_heights_mm"][end]
            analysis_v = action["analysis_column_shear_magnitude_kn"]
            demand = max(design_v, analysis_v)
            column_rows[end] = {
                "signed_analysis_shear_kn": sign * analysis_v,
                "signed_capacity_shear_kn": sign * design_v,
                "concurrent_axial_compression_kn": pu,
                "axial_shear_multiplier": multiplier,
                "concrete_capacity_kn": concrete,
                "steel_capacity_kn": steel,
                "concrete_crushing_cap_kn": maximum,
                "demand_kn": demand,
                "accepted_capacity_kn": capacity,
                "utilization": demand / capacity,
                "pass": demand <= capacity,
            }
        rows.append(
            {
                "combination_id": action["combination_id"],
                "column_axial_compression_kn": axial,
                "signed_axial_balance_residual_kn": axial["lower"]
                - axial["upper"]
                - (
                    sum(vertical.values())
                    + action.get("orthogonal_downward_reaction_kn", 0)
                ),
                "maximum_column_axial_stress_mpa": 1000
                * max(axial.values())
                / width**2,
                "beam_capacity_shear": beam_rows,
                "column_capacity_shear": column_rows,
            }
        )
    return {
        "connected_beams": count,
        "rows": rows,
        "scwb": {
            "beam_capacity_direction": direction,
            "column_capacity_direction": plane + ("-" if sense == "+" else "+"),
            "required_column_capacity_knm": required_moment,
            "available_column_capacity_knm": available_moment,
            "governing_column_combination_ids": {
                end: row["combination_id"] for end, row in min_columns.items()
            },
            "utilization": required_moment / available_moment,
            "pass": required_moment <= available_moment,
        },
        "joint_shear": {
            "confined_faces": 3 if three_faces else 0,
            "design_beam_tension_kn_each": mechanism["tension_kn"],
            "mechanism_beam_reactions_kn": overstrength,
            "reaction_moment_about_centre_knm": signed_reaction_couple,
            "column_inflection_force_couple_arm_mm": arm,
            "signed_compatible_column_shear_kn": sign * mechanism_column_v,
            "signed_joint_shear_kn": sign * joint_v,
            "effective_breadth_mm": breadth,
            "effective_area_mm2": effective_area,
            "stress_mpa": joint_stress,
            "strength_mpa": joint_stress_limit,
            "utilization": joint_stress / joint_stress_limit,
            "pass": joint_stress <= joint_stress_limit,
        },
    }


def evaluate(request):
    for condition, reason in (
        (set(request["directions"]) != set(DIRECTIONS), "required_direction_missing"),
        (
            request["cage_action_revision"] != request["action_revision"],
            "stale_action_revision",
        ),
        (request["x_hooks"] is None, "terminated_bar_path_missing"),
        (
            request["mechanism_inflection_offsets_mm"] is None,
            "compatible_capacity_mechanism_missing",
        ),
    ):
        if condition:
            return {"status": "HOLD", "reason": reason}
    assert all(
        action["beam_axial_kn"] == 0
        for rows in request["directions"].values()
        for action in rows
    )
    placed = geometry(request)
    transverse = confinement(request)
    anchors = anchorage(request)
    beam_links = {plane: _beam_link_detail(request, plane) for plane in ("X", "Y")}
    beams, mechanisms = _section_data(request)
    columns = _column_sections(request)
    directions = {
        direction: _signed_checks(
            request, direction, beams, mechanisms, columns, transverse
        )
        for direction in DIRECTIONS
    }
    ratios = {
        plane: 100
        * len(request["beam_axes_mm"][plane])
        * area_mm2(request["beam_bar_mm"][plane])
        / (
            request["beam_width_mm"][plane]
            * (request["joint_depth_mm"] - request["beam_top_z_mm"][plane])
        )
        for plane in ("X", "Y")
    }
    min_steel_ratio = 100 * 0.24 * math.sqrt(30) / request["longitudinal_fy_mpa"]
    checks = {
        "construction_fit": all(placed["fit_checks"].values())
        and all(item["pass"] for item in beam_links.values()),
        "confinement": transverse["pass"],
        "anchorage": anchors["pass"],
        "beam_flexural_prerequisite": all(
            beam["tension_ductile"] and min_steel_ratio <= ratios[plane] <= 2.5
            for plane, beam in beams.items()
        ),
        "column_axial_stress": all(
            row["maximum_column_axial_stress_mpa"] <= 0.40 * request["column_fck_mpa"]
            for item in directions.values()
            for row in item["rows"]
        ),
    }
    governing = {}
    for family in ("beam_capacity_shear", "column_capacity_shear"):
        actions = [
            {
                "direction": direction,
                "combination_id": row["combination_id"],
                "side": side,
                **item,
            }
            for direction, result in directions.items()
            for row in result["rows"]
            for side, item in row[family].items()
        ]
        checks[family] = all(row["pass"] for row in actions)
        governing[family] = max(actions, key=lambda item: item["utilization"])
    for family in ("scwb", "joint_shear"):
        checks[family] = all(row[family]["pass"] for row in directions.values())
        label = max(
            directions,
            key=lambda direction: directions[direction][family]["utilization"],
        )
        governing[family] = {"direction": label, **directions[label][family]}
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "governing": governing,
        "directions": directions,
        "beam_section_by_plane": beams,
        "column_sections_by_combination_and_end": columns,
        "beam_joint_shear_mechanism_by_plane": mechanisms,
        "anchorage": anchors,
        "confinement": transverse,
        "placement": placed,
        "adjacent_beam_link_sections": beam_links,
    }


def fixture():
    base = specimen()
    baseline = evaluate(base)
    assert baseline["status"] == "PASS", (
        baseline["checks"],
        baseline["placement"]["fit_checks"],
    )
    short_end = deepcopy(base["x_hooks"])
    short_end["BOTTOM"]["tail_mm"] = 470
    collide = deepcopy(base["x_hooks"])
    collide["BOTTOM"]["tip_x_mm"] = collide["TOP"]["tip_x_mm"]
    changes = {
        "weak_column": ({"column_bar_mm": 25, "column_bar_edge_mm": 87}, "scwb"),
        "weak_joint_core": ({"joint_fck_mpa": 20}, "joint_shear"),
        "widely_spaced_link_groups": (
            {
                "joint_hoop_centres_mm": [
                    z for z in base["joint_hoop_centres_mm"] if z != 385
                ]
            },
            "confinement",
        ),
        "short_bottom_hook": ({"x_hooks": short_end}, "anchorage"),
        "overlapping_vertical_hooks": ({"x_hooks": collide}, "construction_fit"),
    }
    controls = {}
    for name, (patch, failure) in changes.items():
        result = evaluate(base | patch)
        failed = [check for check, accepted in result["checks"].items() if not accepted]
        assert failed == [failure], (name, failed)
        controls[name] = {
            "changes": patch,
            "expected": {"status": "FAIL", "failed_checks": failed},
        }
    for name, patch, reason in (
        (
            "missing_orthogonal_negative",
            {
                "directions": {
                    d: rows for d, rows in base["directions"].items() if d != "Y-"
                }
            },
            "required_direction_missing",
        ),
        ("missing_terminated_paths", {"x_hooks": None}, "terminated_bar_path_missing"),
        (
            "stale_revision",
            {"cage_action_revision": "DUCT02-DECLARED-R0"},
            "stale_action_revision",
        ),
        (
            "missing_joint_mechanism",
            {"mechanism_inflection_offsets_mm": None},
            "compatible_capacity_mechanism_missing",
        ),
    ):
        result = evaluate(base | patch)
        assert result == {"status": "HOLD", "reason": reason}
        controls[name] = {"changes": patch, "expected": result}
    return {
        "fixture_version": "library-030-duct02-exterior-joint/v1",
        "sources": [
            "BIS IS 13920:2016 with Amendments 1 (2017) and 2 (2020). https://standards.bis.gov.in/website/standard-details?encryptedId=eyJpdiI6Ik9yaTN1NC9ERTFvYVN5b1UwTG1ZUVE9PSIsInZhbHVlIjoiRHdrTlIzRloyOXg1WXFqMUN6ZTVBdz09IiwibWFjIjoiNmM5NTg5NzU4ZTIwOTNlMDkwMjcyZDg1MzM1MjEzMmNlNGYwMjc2MGVjMWFjYjM2ODdjYWRhOGQyNzE2MDU1NiIsInRhZyI6IiJ9",
            "IS 13920 §§6.2.3 and 6.2.5 Fig. 2, 6.3.3, 7.2, 7.4.2 Fig. 10, 7.5–7.6, 9.1 and 9.2.2. https://nfrlyconstruction.org/uploads/File/Codes/17072023-29_147_IS_13920-2016_DUCTILE_DETAILING_OF_RC_STRUCTURES.pdf_504314034.pdf",
            "IS 456 §§26.2.1, 26.2.2.1, 38, 40 and Tables 19–20. https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf",
        ],
        "scope": [
            "Regular non-roof exterior at X plus. One terminating beam from X minus and opposed through beams in Y. All three beams cover 80% of their respective vertical face. No contributing slab bars.",
            "Declared concurrent actions and a separate compatible joint capacity mechanism. All beams have zero axial force in the considered plane. Opposed column force couple is evaluated at the declared inflection heights.",
            "Both hook faces are checked in tension. The conservative anchorage proof uses only the two straight parts after allowing the 90 degree bend credit, while the arc is retained for cutting length. The 4db internal bend diameter is the declared fixture fabrication limit.",
            "Closed overlapping links and one X cross-tie form each exterior group. Its 135 degree end is at the exterior face. Full confinement is checked in the joint and adjoining column zones.",
            "The paired straight hook tails meet a declared 25 mm aggregate-based clear opening. The adjacent beam hoops seat four corner bars and separately restrain the two middle bars on each face.",
            "Local joint fabrication marks cover the checked transverse pieces and the in-core termination portions. The orthogonal through lengths are local checked intervals. Whole-frame stock lengths and lapping are separate.",
        ],
        "acceptance_tolerances": {
            "geometry_and_cut_lengths_abs_mm": 1e-6,
            "section_and_action_results_relative": 1e-8,
            "dispositions_signs_identifiers_and_counts": "exact",
        },
        "request": base,
        "expected": baseline,
        "controls": controls,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    output = json.dumps(fixture(), indent=2, sort_keys=True) + "\n"
    if args.write:
        TARGET.write_text(output, encoding="utf-8")
    elif TARGET.read_text(encoding="utf-8") != output:
        raise SystemExit(f"{TARGET.name} differs from independent regeneration")
    print(
        "DUCT02: four directions, eight simultaneous combinations, five FAIL and four HOLD controls"
    )


if __name__ == "__main__":
    main()
