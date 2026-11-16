"""Independent DUCT01 bar paths and conservative installation clearances."""

import math
from itertools import pairwise, product


def area(diameter):
    return math.pi * diameter**2 / 4


def max_pitch(stations):
    return max(b - a for a, b in pairwise(stations))


def point_segment_distance(point, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = ((point[0] - a[0]) * dx + (point[1] - a[1]) * dy) / (dx**2 + dy**2)
    t = min(1.0, max(0.0, t))
    return math.dist(point, (a[0] + t * dx, a[1] + t * dy))


def column_bars(width, edge):
    axes = (edge, width / 2, width - edge)
    return [(x, y) for x, y in product(axes, repeat=2) if (x, y) != (axes[1], axes[1])]


def cross_tie(width, edge, radius, tail):
    """A straight stem, two 135-degree bends and two inward hook tails."""
    middle = width / 2
    left = edge + 5
    left_arc = (left - radius / math.sqrt(2), middle + radius / math.sqrt(2))
    left_tail = (left_arc[0] + tail / math.sqrt(2), left_arc[1] + tail / math.sqrt(2))
    return {
        "bend_centres_xy_mm": [(left, middle), (width - left, middle)],
        "stem_xy_mm": [(left, middle - radius), (width - left, middle - radius)],
        "arc_end_xy_mm": [left_arc, (width - left_arc[0], left_arc[1])],
        "tail_end_xy_mm": [left_tail, (width - left_tail[0], left_tail[1])],
        "cut_mm": width - 2 * left + 1.5 * math.pi * radius + 2 * tail,
    }


def cage(request):
    width = request["column_width_mm"]
    depth = request["joint_depth_mm"]
    beam_dia = request["beam_bar_mm"]
    col_dia = request["column_bar_mm"]
    col_edge = request["column_bar_edge_mm"]
    hoop_dia = request["column_link_mm"]
    hoop_yield = request["link_fy_mpa"]
    col_fck = request["column_fck_mpa"]
    joint_fck = request["joint_fck_mpa"]
    cover = request["column_cover_mm"]
    bar_tol = request["axis_tolerance_mm"]
    tie_tol = request["tie_station_tolerance_mm"]
    rad_tol = request["diameter_overage_mm"] / 2
    hoop_r = request["column_link_centre_radius_mm"]
    hoop_tail = request["column_hook_tail_mm"]
    raised_hook = request["column_hook_rise_mm"]
    offset = request["cross_tie_station_offset_mm"]
    inner = cover + hoop_dia / 2
    centres = (inner + hoop_r, width - inner - hoop_r)
    axes = column_bars(width, col_edge)
    chord = width - 2 * (inner + hoop_r)
    ramp = request["column_hook_ramp_length_mm"]
    hoop_cut = (
        4 * chord
        + 3 * math.pi * hoop_r
        + 2 * hoop_tail
        + math.hypot(ramp, raised_hook)
        - ramp
    )
    if request.get("column_hook_offset_radiused"):
        from _duct02_cage_reference import _closed_hoop

        _, hoop_cut, _ = _closed_hoop(
            "C-H",
            inner,
            width - inner,
            inner,
            width - inner,
            hoop_r,
            hoop_tail,
            ramp,
            raised_hook,
            hoop_dia,
        )
    tie = cross_tie(width, col_edge, hoop_r, hoop_tail)
    # The Y cross-tie is the X path turned 90 degrees about the core centre.
    y_tie = {
        key: [(width - y, x) for x, y in points]
        for key, points in tie.items()
        if key.endswith("_xy_mm")
    }
    y_tie["cut_mm"] = tie["cut_mm"]
    marks = {
        "C-H": {"plane_offset_mm": 0, "cut_mm": hoop_cut},
        "C-TX": {"plane_offset_mm": -offset, **tie},
        "C-TY": {"plane_offset_mm": offset, **y_tie},
    }
    stations = request["joint_hoop_centres_mm"]
    beam_across = request["beam_axis_across_column_mm"]
    X, Y = (request["beam_row_depth_from_top_mm"][plane] for plane in ("X", "Y"))
    levels = (X, depth - X, Y, depth - Y)
    radial_sum = (beam_dia + hoop_dia) / 2 + 2 * rad_tol
    beam_hoop_clear = min(
        min(abs(z - (s - offset)), abs(z - (s + offset)))
        for z, s in product(levels, stations)
    )
    # Includes the raised closure hook and the ramp on the first corner rail.
    beam_outer_hoop_clear = min(
        max(s - z, z - s - raised_hook, 0.0) for z, s in product(levels, stations)
    )
    beam_column_sep = min(
        abs(w - x) for x, w in product({p[0] for p in axes}, beam_across)
    )
    beam_column_clear = (
        beam_column_sep - (beam_dia + col_dia) / 2 - 2 * (bar_tol + rad_tol)
    )
    beam_transverse_clear = (
        min(beam_hoop_clear, beam_outer_hoop_clear) - radial_sum - bar_tol - tie_tol
    )
    beam_crossing_clear = abs(X - Y) - beam_dia - 2 * (bar_tol + rad_tol)
    tie_plane_clear = min(offset, raised_hook) - hoop_dia - 2 * (tie_tol + rad_tol)
    hoop_seat_clear = (
        hoop_r - (col_dia + hoop_dia) / 2 - math.sqrt(2) * abs(centres[0] - col_edge)
    )
    cross_seat_clear = hoop_r - (col_dia + hoop_dia) / 2 - 5
    seat_tol = math.sqrt(2) * bar_tol + 2 * rad_tol
    # The two tie stems govern the unobstructed vertical vibrator corridor.
    centre = (width / 2, width / 2)
    route_radius = (
        min(
            min(abs(width / 2 - bar) for bar in beam_across) - beam_dia / 2,
            min(math.dist(centre, point) for point in axes) - col_dia / 2,
            hoop_r - hoop_dia / 2,
            *(
                point_segment_distance(centre, *shaped["stem_xy_mm"]) - hoop_dia / 2
                for shaped in (tie, y_tie)
            ),
        )
        - bar_tol
        - rad_tol
    )
    # Hook/ramp are confined near a corner and its adjacent rail. Mid-face
    # cross-tie bends/tails stay outside the central vibrator corridor.
    hooks_clear = (
        min(
            min(
                min(math.dist(centre, p) for p in shaped["bend_centres_xy_mm"])
                - hoop_r,
                min(
                    point_segment_distance(centre, a, b)
                    for a, b in zip(
                        shaped["arc_end_xy_mm"], shaped["tail_end_xy_mm"], strict=True
                    )
                ),
            )
            for shaped in (tie, y_tie)
        )
        - hoop_dia / 2
    )
    assert hooks_clear > route_radius
    # The ramp and raised hook stay at the NW outside corner, remote from
    # the two centre tie routes even where their vertical bands overlap.
    ramp_end_x = centres[0] + ramp
    assert ramp_end_x + 2 * hoop_dia < width / 2 - hoop_r
    core_outer = width - 2 * cover
    core_area = core_outer**2
    # Conservative larger half bay measured outside-to-outside of the legs.
    h = max(width / 2 + hoop_r - inner, width - inner - (width / 2 - hoop_r)) + hoop_dia
    joint_pitch = max_pitch(stations) + 2 * tie_tol
    end_pitch = request["column_end_pitch_mm"] + 2 * tie_tol

    def ash_terms(pitch, fck):
        basic = pitch * h * fck / hoop_yield
        return (0.18 * basic * (width**2 / core_area - 1), 0.05 * basic)

    joint_ash = ash_terms(joint_pitch, joint_fck)
    end_ash = ash_terms(end_pitch, col_fck)
    provided_ash = area(hoop_dia)
    coverage = request["beam_width_mm"] / width
    confined = coverage >= 0.75
    required_joint_ash = (0.5 if confined else 1.0) * max(joint_ash)
    joint_pitch_limit = 150 if confined else min(width / 4, 6 * col_dia, 100)
    end_pitch_limit = min(width / 4, 6 * col_dia, 100)
    required_end_zone = max(
        width, max(request["column_clear_heights_mm"].values()) / 6, 450
    )
    edge_spacing = (width - 2 * col_edge) / 2
    first_end_hoop = request["column_first_end_hoop_mm"]
    end_zone = request["column_end_confinement_length_mm"]
    end_pitch_nominal = request["column_end_pitch_mm"]
    end_intervals = math.ceil((end_zone - first_end_hoop) / end_pitch_nominal)
    end_stations = [
        first_end_hoop + i * end_pitch_nominal for i in range(end_intervals + 1)
    ]
    transition_pitch = (
        max(stations[0] + first_end_hoop, depth - stations[-1] + first_end_hoop)
        + 2 * tie_tol
    )
    beam_hoops = {}
    beam_link_dia = request["beam_link_mm"]
    beam_outline = (width - request["beam_width_mm"]) / 2
    beam_inset = request["beam_link_seat_inset_mm"]
    depth_inset = request.get("beam_link_depth_seat_inset_mm", beam_inset)
    beam_r = request["beam_link_centre_radius_mm"]
    outer_rail_cover = min(beam_across) - beam_outline - beam_inset - beam_link_dia / 2
    beam_corner_clear = (
        beam_r
        - (beam_dia + beam_link_dia) / 2
        - math.hypot(beam_r - beam_inset, beam_r - depth_inset)
    )
    min_row_clear = (
        min(b - a for a, b in pairwise(beam_across))
        - beam_dia
        - 2 * (bar_tol + rad_tol)
    )
    min_row_clear_required = max(beam_dia, request["aggregate_max_mm"] + 5)
    for plane, level in (("X", X), ("Y", Y)):
        top = level - depth_inset
        beam_hoops[plane] = {
            "outer_across_axis_bounds_mm": [
                beam_across[0] - beam_inset,
                beam_across[-1] + beam_inset,
            ],
            "middle_across_axis_bounds_mm": [
                beam_across[1] - beam_inset,
                beam_across[2] + beam_inset,
            ],
            "depth_axis_bounds_mm": [top, depth - top],
            "internal_bend_radius_mm": beam_r - beam_link_dia / 2,
            "first_outer_hoop_station_from_face_mm": request["beam_first_link_mm"],
            "middle_hoop_station_offset_mm": request["beam_inner_link_offset_mm"],
            "link_pitch_mm": request["beam_pitch_mm"],
            "top_nominal_cover_mm": top - beam_link_dia / 2,
            "steel_clearance_between_link_planes_mm": (
                request["beam_inner_link_offset_mm"]
                - beam_link_dia
                - 2 * (tie_tol + rad_tol)
            ),
        }
    checks = {
        "beam_beam_clearance": beam_crossing_clear > 0,
        "beam_column_clearance": beam_column_clear > 0,
        "beam_tie_clearance": beam_transverse_clear > 0,
        "tie_plane_and_closure_clearance": tie_plane_clear > 0,
        "cage_seats": min(hoop_seat_clear, cross_seat_clear) > seat_tol,
        "column_cover": cover - bar_tol - rad_tol
        >= request["required_column_cover_mm"],
        "beam_link_seats_and_cover": beam_corner_clear > seat_tol
        and min(
            outer_rail_cover,
            *(item["top_nominal_cover_mm"] for item in beam_hoops.values()),
        )
        - bar_tol
        - rad_tol
        >= request["required_beam_cover_mm"],
        "beam_outer_middle_link_clearance": all(
            item["steel_clearance_between_link_planes_mm"] > 0
            for item in beam_hoops.values()
        ),
        "beam_parallel_row_spacing": min_row_clear >= min_row_clear_required,
        "compaction_access": 2 * route_radius >= request["compaction_head_mm"],
        "perimeter_bar_spacing": edge_spacing + 2 * bar_tol <= 300,
        "perimeter_longitudinal_ratio": 0.008 <= 8 * area(col_dia) / width**2 <= 0.04,
    }
    confinement = {
        "pitch": joint_pitch <= joint_pitch_limit and end_pitch <= end_pitch_limit,
        "joint_to_end_zone_transition": transition_pitch <= end_pitch_limit,
        "area": provided_ash >= max(required_joint_ash, max(end_ash)),
        "end_zone": request["column_end_confinement_length_mm"] >= required_end_zone,
        "leg_spacing": h <= 300,
        "hooks": hoop_tail >= max(8 * hoop_dia, 75),
    }
    return {
        "fit_checks": checks,
        "confinement_checks": confinement,
        "minimum_clearances_mm": {
            "perpendicular_beam_bars": beam_crossing_clear,
            "beam_to_column_bars": beam_column_clear,
            "beam_to_column_ties": beam_transverse_clear,
            "tie_planes_and_hoop_closure": tie_plane_clear,
            "hoop_corner_seat": hoop_seat_clear - seat_tol,
            "face_bar_to_cross_tie": cross_seat_clear - seat_tol,
            "vertical_compaction_corridor_diameter": 2 * route_radius,
            "parallel_beam_row_clear_spacing": min_row_clear,
            "parallel_beam_row_clear_spacing_required": min_row_clear_required,
        },
        "column_longitudinal_axes_xy_mm": axes,
        "column_hoop_axis_bounds_mm": [inner, width - inner],
        "column_hoop_corner_centre_axes_mm": centres,
        "column_hoop_closure_rise_mm": raised_hook,
        "beam_hoop_sections": beam_hoops,
        "beam_bar_paths": {
            plane: [
                {
                    "bar_id": f"B{plane}-{face}-{index + 1}",
                    "across_axis_mm": across,
                    "depth_mm": level,
                    "joint_relative_axial_interval_mm": [
                        -request["beam_uninterrupted_development_mm"],
                        width + request["beam_uninterrupted_development_mm"],
                    ],
                }
                for face, level in (("TOP", z), ("BOTTOM", depth - z))
                for index, across in enumerate(beam_across)
            ]
            for plane, z in (("X", X), ("Y", Y))
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
            "joint_ash_full_terms_mm2": joint_ash,
            "joint_ash_required_mm2": required_joint_ash,
            "end_pitch_mm": end_pitch,
            "end_pitch_limit_mm": end_pitch_limit,
            "joint_to_end_zone_transition_pitch_mm": transition_pitch,
            "end_ash_terms_mm2": end_ash,
            "end_length_required_mm": required_end_zone,
            "ash_provided_per_leg_mm2": provided_ash,
        },
    }
