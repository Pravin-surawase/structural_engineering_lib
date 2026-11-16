"""Anchorage and detailing checks for the regular exterior joint."""

from __future__ import annotations

import math
from collections.abc import Mapping
from itertools import pairwise
from typing import Any

from structural_lib.codes.is456.beam.detailing import (
    calculate_development_length_unrounded,
)
from structural_lib.codes.is13920.column import (
    calculate_ash_required,
    calculate_special_confining_spacing,
)


def exterior_anchorage(data: Mapping[str, Any]) -> dict[str, Any]:
    """Check exterior 90-degree terminations and straight through-bars."""
    fy, fck = data["longitudinal_fy_mpa"], data["beam_fck_mpa"]
    phi_x, phi_y = data["beam_bar_mm"]["X"], data["beam_bar_mm"]["Y"]
    tolerance = data["anchor_cut_length_tolerance_mm"]
    radius = data["x_hook_radius_mm"]
    bend_diameter = 2 * radius - phi_x
    development_x = calculate_development_length_unrounded(phi_x, fck, fy)
    bend_credit = 8 * phi_x
    required_x = development_x + 10 * phi_x - bend_credit
    arc_length = math.pi * radius / 2
    hooks = {}
    for face, hook in data["x_hooks"].items():
        tangent = hook["tip_x_mm"] - radius
        tail = hook["tail_mm"]
        straight = tangent + tail
        adverse = straight - tolerance
        hooks[face] = {
            "development_mm": development_x,
            "codal_bend_credit_mm": bend_credit,
            "required_mm": required_x,
            "straight_horizontal_mm": tangent,
            "straight_tail_mm": tail,
            "arc_length_mm": arc_length,
            "centreline_length_beyond_face_mm": straight + arc_length,
            "adverse_straight_length_mm": adverse,
            "diameter_mm": phi_x,
            "arc_centreline_radius_mm": radius,
            "internal_bend_diameter_mm": bend_diameter,
            "pass": adverse >= required_x and bend_diameter >= 4 * phi_x,
        }
    required_y = calculate_development_length_unrounded(phi_y, fck, fy)
    adjacent_y = data["y_straight_each_side_mm"] - tolerance
    width = data["column_width_mm"]
    through = {
        "joint_width_mm": width,
        "joint_width_required_mm": 20 * phi_y,
        "required_development_mm": required_y,
        "adverse_development_each_side_mm": adjacent_y,
        "pass": width >= 20 * phi_y and adjacent_y >= required_y,
    }
    return {
        "terminated_X": hooks,
        "continuous_Y": through,
        "pass": through["pass"] and all(hook["pass"] for hook in hooks.values()),
    }


def exterior_confinement(data: Mapping[str, Any]) -> dict[str, Any]:
    """Check full special confinement using split legs and station tolerances."""
    width = data["column_width_mm"]
    diameter = data["column_link_mm"]
    cover = data["column_cover_mm"]
    inset = cover + diameter / 2
    half_overlap = data["column_link_overlap_half_mm"]
    legs_x = [inset, width / 2 - half_overlap, width / 2 + half_overlap, width - inset]
    cross_y = data["column_cross_tie_axis_y_mm"] - data["column_link_radius_mm"]
    legs_y = [inset, cross_y, width - inset]
    h = (
        max(right - left for legs in (legs_x, legs_y) for left, right in pairwise(legs))
        + diameter
    )
    adverse_h = h + 2 * data["axis_tolerance_mm"]
    core_area = (width - 2 * cover) ** 2
    stations = data["joint_hoop_centres_mm"]
    allowance = 2 * data["tie_station_tolerance_mm"]
    joint_pitch = max(right - left for left, right in pairwise(stations)) + allowance
    end_pitch = data["column_end_pitch_mm"] + allowance
    first_end = data["column_end_link_first_mm"]
    transition = (
        first_end + max(stations[0], data["joint_depth_mm"] - stations[-1]) + allowance
    )
    limit = calculate_special_confining_spacing(width, data["column_bar_mm"])
    fy = data["link_fy_mpa"]
    joint_ash = calculate_ash_required(
        joint_pitch, adverse_h, data["joint_fck_mpa"], fy, width**2, core_area
    )
    end_ash = calculate_ash_required(
        end_pitch, adverse_h, data["column_fck_mpa"], fy, width**2, core_area
    )
    ash = math.pi * diameter**2 / 4
    length = max(width, max(data["column_clear_heights_mm"].values()) / 6, 450)
    checks = {
        "joint_pitch": joint_pitch <= min(150, limit),
        "end_pitch": max(end_pitch, transition) <= limit,
        "split_legs": adverse_h <= 300,
        "full_joint_ash": ash >= joint_ash,
        "full_end_ash": ash >= end_ash,
        "end_confinement_length": data["column_end_confinement_length_mm"] >= length,
        "link_hook_tails": data["column_link_tail_mm"] >= max(8 * diameter, 75),
    }
    return {
        "required_fraction": 1.0,
        "leg_planes_x_mm": legs_x,
        "leg_planes_y_mm": legs_y,
        "outside_confined_core_area_mm2": core_area,
        "h_mm": h,
        "adverse_h_mm": adverse_h,
        "joint_pitch_mm": joint_pitch,
        "column_end_pitch_mm": end_pitch,
        "end_pitch_mm": end_pitch,
        "joint_to_adjacent_pitch_mm": transition,
        "pitch_limit_mm": limit,
        "joint_required_ash_mm2": joint_ash,
        "end_required_ash_mm2": end_ash,
        "provided_ash_mm2": ash,
        "required_end_confinement_length_mm": length,
        "checks": checks,
        "pass": all(checks.values()),
        # A three-face joint gets the elevated limit only when all present
        # beam widths cover at least 75% of the associated column face.
        "confined_faces": (
            3 if min(data["beam_width_mm"].values()) >= 0.75 * width else 0
        ),
    }


def exterior_beam_link_sections(data: Mapping[str, Any]) -> dict[str, Any]:
    """Check the outer and middle hoop seats and cover of each adjoining beam."""
    tie = data["beam_link_mm"]
    tolerance = data["axis_tolerance_mm"]
    overage = data["diameter_overage_mm"]
    offset = data["beam_inner_link_offset_mm"]
    pitch = data["beam_pitch_mm"]
    phase_clearance = (
        min(offset, pitch - offset)
        - tie
        - 2 * data["tie_station_tolerance_mm"]
        - overage
    )
    sections = {}
    for plane, axes in data["beam_axes_mm"].items():
        phi = data["beam_bar_mm"][plane]
        radius = data["beam_link_centre_radius_mm"][plane]
        inset = data["beam_link_seat_inset_mm"][plane]
        edge = (data["column_width_mm"] - data["beam_width_mm"][plane]) / 2
        z = data["beam_top_z_mm"][plane] - inset
        cover = min(axes[0] - edge - inset, z) - tie / 2 - tolerance - overage / 2
        seat = radius - math.hypot(radius - inset, radius - inset) - (phi + tie) / 2
        seat -= math.sqrt(2) * tolerance + overage
        spacing = min(b - a for a, b in pairwise(axes)) - phi - 2 * tolerance - overage
        middle_width = axes[2] - axes[1] + 2 * inset
        hoop_depth = data["joint_depth_mm"] - 2 * z
        checks = {
            "four_outer_corner_seats_and_middle_hoop": seat > 0
            and min(middle_width, hoop_depth) > 2 * radius,
            "cover": cover >= data["required_beam_cover_mm"],
            "row_clear": spacing >= max(phi, data["aggregate_max_mm"] + 5),
            "nested_hoops_clear": phase_clearance > 0,
            "closed_hoop_hooks": data["beam_link_hook_tail_mm"] >= max(8 * tie, 75),
        }
        sections[plane] = {
            "outer_across_bounds_mm": [axes[0] - inset, axes[-1] + inset],
            "middle_across_bounds_mm": [axes[1] - inset, axes[2] + inset],
            "depth_bounds_mm": [z, data["joint_depth_mm"] - z],
            "first_outer_station_mm": data["beam_first_link_mm"],
            "middle_station_offset_mm": offset,
            "pitch_mm": pitch,
            "corner_seat_adverse_mm": seat,
            "parallel_clearance_mm": spacing,
            "hoop_phase_clearance_mm": phase_clearance,
            "checks": checks,
            "pass": all(checks.values()),
        }
    return sections
