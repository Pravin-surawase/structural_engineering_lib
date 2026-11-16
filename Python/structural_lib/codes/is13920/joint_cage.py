# SPDX-License-Identifier: MIT
"""Physical cage and confinement evidence for the bounded DUCT01 joint."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from itertools import pairwise, product
from typing import Any

from structural_lib.codes.is13920.exterior_joint_cage import _closed, _offset_angle

__all__ = ["check_joint_cage"]


def _area(diameter: float) -> float:
    return math.pi * diameter**2 / 4.0


def _distance_to_segment(
    point: Sequence[float], a: Sequence[float], b: Sequence[float]
) -> float:
    dx, dy = b[0] - a[0], b[1] - a[1]
    length_squared = dx**2 + dy**2
    if length_squared <= 0.0:
        return math.dist(point, a)
    projection = ((point[0] - a[0]) * dx + (point[1] - a[1]) * dy) / length_squared
    projection = min(1.0, max(0.0, projection))
    return math.dist(point, (a[0] + projection * dx, a[1] + projection * dy))


def _false_result(message: str) -> dict[str, Any]:
    """Return a JSON-safe fail-closed geometry result for finite bad inputs."""
    return {
        "fit_checks": {"valid_geometry": False},
        "confinement_checks": {"valid_geometry": False},
        "diagnostic": message,
        "column_transverse_joint_marks": {},
        "beam_bar_paths": {},
        "beam_hoop_sections": {},
        "minimum_clearances_mm": {},
        "confinement": {},
    }


def _numbers(request: Mapping[str, Any], *names: str) -> tuple[float, ...] | None:
    try:
        values = tuple(float(request[name]) for name in names)
    except (KeyError, TypeError, ValueError):
        return None
    return values if all(math.isfinite(value) for value in values) else None


def check_joint_cage(request: Mapping[str, Any]) -> dict[str, Any]:
    """Resolve actual DUCT01 interior-joint cage geometry.

    The caller supplies a normalized, validated request.  This bounded owner
    deliberately emits failed checks rather than raising for finite but
    impossible cage geometry; schema validation remains the caller's job.
    """
    values = _numbers(
        request,
        "column_width_mm",
        "joint_depth_mm",
        "beam_width_mm",
        "beam_bar_mm",
        "column_bar_mm",
        "column_bar_edge_mm",
        "column_link_mm",
        "link_fy_mpa",
        "column_fck_mpa",
        "joint_fck_mpa",
        "column_cover_mm",
        "axis_tolerance_mm",
        "tie_station_tolerance_mm",
        "diameter_overage_mm",
        "column_link_centre_radius_mm",
        "column_hook_tail_mm",
        "column_hook_rise_mm",
        "cross_tie_station_offset_mm",
        "column_hook_ramp_length_mm",
        "required_column_cover_mm",
        "aggregate_max_mm",
        "compaction_head_mm",
        "beam_link_mm",
        "beam_link_seat_inset_mm",
        "beam_link_centre_radius_mm",
        "beam_first_link_mm",
        "beam_inner_link_offset_mm",
        "beam_pitch_mm",
        "column_first_end_hoop_mm",
        "column_end_pitch_mm",
        "column_end_confinement_length_mm",
    )
    if values is None:
        return _false_result("missing or non-finite DUCT01 cage dimension")
    (
        width,
        depth,
        beam_width,
        beam_dia,
        col_dia,
        col_edge,
        hoop_dia,
        hoop_yield,
        col_fck,
        joint_fck,
        cover,
        bar_tol,
        tie_tol,
        diameter_overage,
        hoop_r,
        hoop_tail,
        raised_hook,
        offset,
        ramp,
        required_cover,
        aggregate,
        compaction_head,
        beam_link_dia,
        beam_inset,
        beam_r,
        first_link_station,
        inner_link_offset,
        beam_pitch,
        first_end_hoop,
        end_pitch_nominal,
        end_zone,
    ) = values
    try:
        stations = tuple(float(value) for value in request["joint_hoop_centres_mm"])
        beam_across = tuple(
            float(value) for value in request["beam_axis_across_column_mm"]
        )
        row_depths = request["beam_row_depth_from_top_mm"]
        x_level, y_level = float(row_depths["X"]), float(row_depths["Y"])
        heights = request["column_clear_heights_mm"]
        clear_heights = tuple(float(heights[end]) for end in ("upper", "lower"))
    except (KeyError, TypeError, ValueError):
        return _false_result(
            "missing cage stations, bar axes, row levels, or column heights"
        )
    all_values = (*stations, *beam_across, x_level, y_level, *clear_heights)
    if (
        len(stations) < 2
        or len(beam_across) < 2
        or not all(math.isfinite(v) for v in all_values)
        or min(
            width,
            depth,
            beam_width,
            beam_dia,
            col_dia,
            hoop_dia,
            hoop_yield,
            cover,
            hoop_r,
            beam_link_dia,
            beam_r,
        )
        <= 0.0
    ):
        return _false_result("non-positive or insufficient DUCT01 cage geometry")

    radial_tolerance = diameter_overage / 2.0
    inner = cover + hoop_dia / 2.0
    centres = (inner + hoop_r, width - inner - hoop_r)
    axes_1d = (col_edge, width / 2.0, width - col_edge)
    column_axes = [
        [x, y]
        for x, y in product(axes_1d, repeat=2)
        if (x, y) != (axes_1d[1], axes_1d[1])
    ]
    chord = width - 2.0 * (inner + hoop_r)
    if chord <= 0.0:
        return _false_result("column hoop has no positive straight chord")
    hoop_cut = (
        4.0 * chord
        + 3.0 * math.pi * hoop_r
        + 2.0 * hoop_tail
        + math.hypot(ramp, raised_hook)
        - ramp
    )

    hoop_path: dict[str, Any] = {}
    if request.get("column_hook_offset_radiused"):
        turn = _offset_angle(ramp, raised_hook, hoop_r)
        if turn is None or ramp >= chord:
            return _false_result(
                "column hoop closure cannot fit with the declared bend radius"
            )
        path, hoop_cut = _closed(
            "C-H",
            inner,
            width - inner,
            inner,
            width - inner,
            hoop_r,
            hoop_tail,
            ramp,
            raised_hook,
            turn,
            hoop_dia,
        )
        hoop_path = {
            "local_centreline_xyz_mm": path.points,
            "closure_offset_angles_deg": [math.degrees(turn), -math.degrees(turn)],
        }

    middle, left = width / 2.0, col_edge + 5.0
    left_arc = (left - hoop_r / math.sqrt(2.0), middle + hoop_r / math.sqrt(2.0))
    left_tail = (
        left_arc[0] + hoop_tail / math.sqrt(2.0),
        left_arc[1] + hoop_tail / math.sqrt(2.0),
    )
    x_tie = {
        "bend_centres_xy_mm": [[left, middle], [width - left, middle]],
        "stem_xy_mm": [[left, middle - hoop_r], [width - left, middle - hoop_r]],
        "arc_end_xy_mm": [list(left_arc), [width - left_arc[0], left_arc[1]]],
        "tail_end_xy_mm": [list(left_tail), [width - left_tail[0], left_tail[1]]],
    }
    y_tie = {key: [[width - y, x] for x, y in points] for key, points in x_tie.items()}
    cross_tie_cut = width - 2.0 * left + 1.5 * math.pi * hoop_r + 2.0 * hoop_tail
    marks: dict[str, dict[str, Any]] = {
        "C-H": {"plane_offset_mm": 0.0, "cut_mm": hoop_cut, **hoop_path},
        "C-TX": {"plane_offset_mm": -offset, "cut_mm": cross_tie_cut, **x_tie},
        "C-TY": {"plane_offset_mm": offset, "cut_mm": cross_tie_cut, **y_tie},
    }

    levels = (x_level, depth - x_level, y_level, depth - y_level)
    radial_sum = (beam_dia + hoop_dia) / 2.0 + 2.0 * radial_tolerance
    beam_hoop_clear = min(
        min(abs(z - (s - offset)), abs(z - (s + offset)))
        for z, s in product(levels, stations)
    )
    beam_outer_hoop_clear = min(
        max(s - z, z - s - raised_hook, 0.0) for z, s in product(levels, stations)
    )
    beam_column_sep = min(
        abs(w - x) for x, w in product({point[0] for point in column_axes}, beam_across)
    )
    beam_column_clear = (
        beam_column_sep
        - (beam_dia + col_dia) / 2.0
        - 2.0 * (bar_tol + radial_tolerance)
    )
    beam_transverse_clear = (
        min(beam_hoop_clear, beam_outer_hoop_clear) - radial_sum - bar_tol - tie_tol
    )
    beam_crossing_clear = (
        abs(x_level - y_level) - beam_dia - 2.0 * (bar_tol + radial_tolerance)
    )
    tie_plane_clear = (
        min(offset, raised_hook) - hoop_dia - 2.0 * (tie_tol + radial_tolerance)
    )
    hoop_seat_clear = (
        hoop_r
        - (col_dia + hoop_dia) / 2.0
        - math.sqrt(2.0) * abs(centres[0] - col_edge)
    )
    cross_seat_clear = hoop_r - (col_dia + hoop_dia) / 2.0 - 5.0
    seat_tol = math.sqrt(2.0) * bar_tol + 2.0 * radial_tolerance

    centre = (width / 2.0, width / 2.0)
    route_radius = (
        min(
            min(abs(width / 2.0 - bar) for bar in beam_across) - beam_dia / 2.0,
            min(math.dist(centre, point) for point in column_axes) - col_dia / 2.0,
            hoop_r - hoop_dia / 2.0,
            *(
                _distance_to_segment(centre, *shape["stem_xy_mm"]) - hoop_dia / 2.0
                for shape in (x_tie, y_tie)
            ),
        )
        - bar_tol
        - radial_tolerance
    )
    hooks_clear = (
        min(
            min(
                min(math.dist(centre, point) for point in shape["bend_centres_xy_mm"])
                - hoop_r,
                min(
                    _distance_to_segment(centre, a, b)
                    for a, b in zip(
                        shape["arc_end_xy_mm"], shape["tail_end_xy_mm"], strict=True
                    )
                ),
            )
            for shape in (x_tie, y_tie)
        )
        - hoop_dia / 2.0
    )
    ramp_end_x = centres[0] + ramp
    closure_ramp_clear = width / 2.0 - hoop_r - (ramp_end_x + 2.0 * hoop_dia)
    tie_points = [
        point
        for shape in (x_tie, y_tie)
        for key in ("bend_centres_xy_mm", "arc_end_xy_mm", "tail_end_xy_mm")
        for point in shape[key]
    ]
    tie_core_envelope_clear = (
        min(
            min(
                point[0] - cover,
                width - cover - point[0],
                point[1] - cover,
                width - cover - point[1],
            )
            for point in tie_points
        )
        - bar_tol
        - radial_tolerance
    )

    # Each corner bar is deliberately seated inside the corresponding rounded
    # hoop quadrant; merely measuring a diagonal distance would accept a bar in
    # the wrong (non-engaging) sector.
    corner_seats = (
        ((centres[0], centres[0]), (col_edge, col_edge), (-1.0, -1.0)),
        ((centres[0], centres[1]), (col_edge, width - col_edge), (-1.0, 1.0)),
        ((centres[1], centres[0]), (width - col_edge, col_edge), (1.0, -1.0)),
        ((centres[1], centres[1]), (width - col_edge, width - col_edge), (1.0, 1.0)),
    )
    rounded_sector_clear = (
        min(
            hoop_r - math.dist(centre_point, bar_point) - (col_dia + hoop_dia) / 2.0
            for centre_point, bar_point, _ in corner_seats
        )
        - seat_tol
    )
    rounded_sector_engagement = all(
        (bar[0] - centre_point[0]) * signs[0] > 0.0
        and (bar[1] - centre_point[1]) * signs[1] > 0.0
        for centre_point, bar, signs in corner_seats
    )

    core_outer = width - 2.0 * cover
    core_area = core_outer**2
    h = (
        max(width / 2.0 + hoop_r - inner, width - inner - (width / 2.0 - hoop_r))
        + hoop_dia
    )
    joint_pitch = max(b - a for a, b in pairwise(stations)) + 2.0 * tie_tol
    end_pitch = end_pitch_nominal + 2.0 * tie_tol
    if core_area <= 0.0 or h <= 0.0:
        return _false_result("non-positive confined core or effective link dimension")

    def ash_terms(pitch: float, fck: float) -> tuple[float, float]:
        basic = pitch * h * fck / hoop_yield
        return 0.18 * basic * (width**2 / core_area - 1.0), 0.05 * basic

    joint_ash, end_ash = ash_terms(joint_pitch, joint_fck), ash_terms(
        end_pitch, col_fck
    )
    provided_ash = _area(hoop_dia)
    coverage = beam_width / width
    confined = coverage >= 0.75
    required_joint_ash = (0.5 if confined else 1.0) * max(joint_ash)
    joint_pitch_limit = 150.0 if confined else min(width / 4.0, 6.0 * col_dia, 100.0)
    end_pitch_limit = min(width / 4.0, 6.0 * col_dia, 100.0)
    required_end_zone = max(width, max(clear_heights) / 6.0, 450.0)
    edge_spacing = (width - 2.0 * col_edge) / 2.0
    end_intervals = (
        math.ceil((end_zone - first_end_hoop) / end_pitch_nominal)
        if end_pitch_nominal > 0.0
        else 0
    )
    end_stations = [
        first_end_hoop + i * end_pitch_nominal for i in range(max(0, end_intervals) + 1)
    ]
    transition_pitch = (
        max(stations[0] + first_end_hoop, depth - stations[-1] + first_end_hoop)
        + 2.0 * tie_tol
    )

    mark_stations = sorted(
        station + shape["plane_offset_mm"]
        for shape in marks.values()
        for station in stations
    )
    minimum_mark_gap = min(b - a for a, b in pairwise(mark_stations))
    staggered_mark_clear = (
        minimum_mark_gap - hoop_dia - 2.0 * (tie_tol + radial_tolerance)
    )
    marks_within_joint = all(0.0 <= station <= depth for station in mark_stations)
    end_transition_clear = (
        min(
            mark_stations[0] + first_end_hoop,
            depth + first_end_hoop - mark_stations[-1],
        )
        - hoop_dia
        - 2.0 * (tie_tol + radial_tolerance)
    )

    beam_outline = (width - beam_width) / 2.0
    outer_rail_cover = (
        min(beam_across) - beam_outline - beam_inset - beam_link_dia / 2.0
    )
    depth_inset = request.get("beam_link_depth_seat_inset_mm") or beam_inset
    beam_corner_clear = (
        beam_r
        - (beam_dia + beam_link_dia) / 2.0
        - math.hypot(beam_r - beam_inset, beam_r - depth_inset)
    )
    min_row_clear = (
        min(b - a for a, b in pairwise(beam_across))
        - beam_dia
        - 2.0 * (bar_tol + radial_tolerance)
    )
    min_row_required = max(beam_dia, aggregate + 5.0)
    nested_beam_grid_clear = (
        min(inner_link_offset, beam_pitch - inner_link_offset)
        - beam_link_dia
        - 2.0 * (tie_tol + radial_tolerance)
    )
    beam_hoops: dict[str, dict[str, Any]] = {}
    for plane, level in (("X", x_level), ("Y", y_level)):
        top = level - depth_inset
        beam_hoops[plane] = {
            "outer_across_axis_bounds_mm": [
                beam_across[0] - beam_inset,
                beam_across[-1] + beam_inset,
            ],
            "middle_across_axis_bounds_mm": [
                beam_across[1] - beam_inset,
                beam_across[-2] + beam_inset,
            ],
            "depth_axis_bounds_mm": [top, depth - top],
            "internal_bend_radius_mm": beam_r - beam_link_dia / 2.0,
            "first_outer_hoop_station_from_face_mm": first_link_station,
            "middle_hoop_station_offset_mm": inner_link_offset,
            "link_pitch_mm": beam_pitch,
            "top_nominal_cover_mm": top - beam_link_dia / 2.0,
            "steel_clearance_between_link_planes_mm": inner_link_offset
            - beam_link_dia
            - 2.0 * (tie_tol + radial_tolerance),
        }

    fit_checks = {
        "beam_beam_clearance": beam_crossing_clear > 0.0,
        "beam_column_clearance": beam_column_clear > 0.0,
        "beam_tie_clearance": beam_transverse_clear > 0.0,
        "tie_plane_and_closure_clearance": tie_plane_clear > 0.0,
        "closure_ramp_clear_of_mid_ties": closure_ramp_clear > 0.0,
        "cross_tie_core_envelope": tie_core_envelope_clear >= 0.0,
        "staggered_joint_mark_clearance": staggered_mark_clear > 0.0
        and marks_within_joint,
        "joint_to_end_hoop_clearance": end_transition_clear > 0.0,
        "cage_seats": min(hoop_seat_clear, cross_seat_clear) > seat_tol
        and rounded_sector_clear > 0.0
        and rounded_sector_engagement,
        "column_cover": cover - bar_tol - radial_tolerance >= required_cover,
        "beam_link_seats_and_cover": beam_corner_clear > seat_tol
        and min(
            outer_rail_cover,
            *(item["top_nominal_cover_mm"] for item in beam_hoops.values()),
        )
        - bar_tol
        - radial_tolerance
        >= float(request.get("required_beam_cover_mm", required_cover)),
        "beam_outer_middle_link_clearance": all(
            item["steel_clearance_between_link_planes_mm"] > 0.0
            for item in beam_hoops.values()
        ),
        "beam_nested_link_grid_clearance": nested_beam_grid_clear > 0.0,
        "beam_parallel_row_spacing": min_row_clear >= min_row_required,
        "compaction_access": 2.0 * route_radius >= compaction_head
        and hooks_clear > route_radius,
        "perimeter_bar_spacing": edge_spacing + 2.0 * bar_tol <= 300.0,
        "perimeter_longitudinal_ratio": 0.008
        <= 8.0 * _area(col_dia) / width**2
        <= 0.04,
    }
    confinement_checks = {
        "pitch": joint_pitch <= joint_pitch_limit and end_pitch <= end_pitch_limit,
        "joint_to_end_zone_transition": transition_pitch <= end_pitch_limit,
        "area": provided_ash >= max(required_joint_ash, max(end_ash)),
        "end_zone": end_zone >= required_end_zone,
        "leg_spacing": h <= 300.0,
        "hooks": hoop_tail >= max(8.0 * hoop_dia, 75.0),
    }
    return {
        "fit_checks": fit_checks,
        "confinement_checks": confinement_checks,
        "minimum_clearances_mm": {
            "perpendicular_beam_bars": beam_crossing_clear,
            "beam_to_column_bars": beam_column_clear,
            "beam_to_column_ties": beam_transverse_clear,
            "tie_planes_and_hoop_closure": tie_plane_clear,
            "hoop_corner_seat": hoop_seat_clear - seat_tol,
            "face_bar_to_cross_tie": cross_seat_clear - seat_tol,
            "rounded_corner_sector": rounded_sector_clear,
            "closure_ramp_to_mid_ties": closure_ramp_clear,
            "cross_tie_core_envelope": tie_core_envelope_clear,
            "staggered_joint_mark_clearance": staggered_mark_clear,
            "joint_to_end_hoop_clearance": end_transition_clear,
            "nested_beam_link_grid_clearance": nested_beam_grid_clear,
            "vertical_compaction_corridor_diameter": 2.0 * route_radius,
            "parallel_beam_row_clear_spacing": min_row_clear,
            "parallel_beam_row_clear_spacing_required": min_row_required,
        },
        "column_longitudinal_axes_xy_mm": column_axes,
        "column_hoop_axis_bounds_mm": [inner, width - inner],
        "column_hoop_corner_centre_axes_mm": list(centres),
        "column_hoop_closure_rise_mm": raised_hook,
        "beam_hoop_sections": beam_hoops,
        "beam_bar_paths": {
            plane: [
                {
                    "bar_id": f"B{plane}-{face}-{index + 1}",
                    "across_axis_mm": across,
                    "depth_mm": level,
                    "joint_relative_axial_interval_mm": [
                        -float(request["beam_uninterrupted_development_mm"]),
                        width + float(request["beam_uninterrupted_development_mm"]),
                    ],
                }
                for face, level in (("TOP", z), ("BOTTOM", depth - z))
                for index, across in enumerate(beam_across)
            ]
            for plane, z in (("X", x_level), ("Y", y_level))
        },
        "cross_tie_orientation": "Both hooks turn into the core. Their planes are staggered.",
        "column_transverse_joint_marks": {
            mark: {
                **shape,
                "stations_mm": [z + shape["plane_offset_mm"] for z in stations],
                "quantity": len(stations),
            }
            for mark, shape in marks.items()
        },
        "column_end_hoop_stations_from_face_mm": end_stations,
        "confinement": {
            "confined_faces": 4 if confined else 0,
            "min_face_coverage": coverage,
            "Ag_mm2": width**2,
            "Ak_outer_mm2": core_area,
            "h_outer_mm": h,
            "joint_pitch_mm": joint_pitch,
            "joint_pitch_limit_mm": joint_pitch_limit,
            "joint_ash_full_terms_mm2": list(joint_ash),
            "joint_ash_required_mm2": required_joint_ash,
            "end_pitch_mm": end_pitch,
            "end_pitch_limit_mm": end_pitch_limit,
            "joint_to_end_zone_transition_pitch_mm": transition_pitch,
            "end_ash_terms_mm2": list(end_ash),
            "end_length_required_mm": required_end_zone,
            "ash_provided_per_leg_mm2": provided_ash,
        },
    }
