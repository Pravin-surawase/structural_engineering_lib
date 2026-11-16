"""Independent beam and column witnesses for PROJECT03."""

from __future__ import annotations

import math
from itertools import combinations, pairwise, product

from _duct01_section_reference import rectangular_section
from _duct02_cage_reference import (
    Path,
    _closed_hoop,
    _path_pair_minimum,
    arc,
    sagitta,
    point_segment_distance_sq,
)
from check_library_030_duct01_interior_reference import shear_capacity

SPAN_MM = 4300
WIDTH_MM = 500
DEPTH_MM = 745
BAR_AXES_MM = (122, 175, 425, 478)
BAR_LEVELS_MM = (70, 675)
PHI_MM = 20
COLUMN_BAR_MM = 32
STATION_TOL_MM = 1.0
ALLOCATION_MM = 1.25
TOP_SEAT_INSET_MM = 20
SIDE_SEAT_INSET_MM = 29
BEAM_HOOP_RADIUS_MM = 25
BEAM_HOOP_TAIL_MM = 85
BEAM_HOOP_DIA_MM = 10
BEAM_CLOSURE_RUN_MM = 50
BEAM_CLOSURE_RISE_MM = 14
CENTRE_FILL = {"BX12-O": (2118, 2182), "BX12-M": (2135, 2165)}
WEST_CLEAR_SPAN_MM = 4000
WEST_EMBEDMENT_MM = 1100
WEST_SUPPORT_DEPTH_MM = 1200


def _mass(diameter, length, quantity):
    """Nominal unit mass uses 7,850 kg/m³ and the full geometric cross-section."""
    return 7850 * math.pi * (diameter / 2000) ** 2 * (length / 1000) * quantity


def _mark(mark, diameter, cut, stations, shape):
    return {
        "bar_mark": mark,
        "diameter_mm": diameter,
        "quantity": len(stations),
        "cut_mm": cut,
        "total_length_mm": cut * len(stations),
        "mass_kg": _mass(diameter, cut, len(stations)),
        "stations_mm": stations,
        "shape": shape,
    }


def beam_links():
    """Shape both link families and reconcile the station grids at midspan."""
    zz0 = BAR_LEVELS_MM[0] - TOP_SEAT_INSET_MM
    zz1 = DEPTH_MM - zz0
    schedule = {}
    paths = []
    for mark, edges, end_start in (
        ("BX12-O", (BAR_AXES_MM[0], BAR_AXES_MM[-1]), 30),
        ("BX12-M", (BAR_AXES_MM[1], BAR_AXES_MM[-2]), 46),
    ):
        bounds = (
            edges[0] - SIDE_SEAT_INSET_MM,
            edges[1] + SIDE_SEAT_INSET_MM,
            zz0,
            zz1,
        )
        path, cut, angle = _closed_hoop(
            mark,
            *bounds,
            BEAM_HOOP_RADIUS_MM,
            BEAM_HOOP_TAIL_MM,
            BEAM_CLOSURE_RUN_MM,
            -BEAM_CLOSURE_RISE_MM if mark == "BX12-O" else BEAM_CLOSURE_RISE_MM,
            BEAM_HOOP_DIA_MM,
        )
        # The nested hoop closes on the opposite diagonal corner.
        if mark == "BX12-M":
            path = Path(
                mark,
                path.diameter,
                [(600 - x, DEPTH_MM - z, station) for x, z, station in path.points],
                path.sagitta_mm,
            )
        left = [end_start + i * 75 for i in range(28)]
        right = [SPAN_MM - x for x in reversed(left)]
        stations = [*left, *CENTRE_FILL[mark], *right]
        # Rotate the same fabricated link 180 degrees about the across
        # axis at the other end. Its closure jog remains away from the
        # neighboring nested link through the overlap in section.
        reflected = Path(
            mark,
            path.diameter,
            [(x, DEPTH_MM - z, -longitudinal) for x, z, longitudinal in path.points],
            path.sagitta_mm,
        )
        paths.extend(
            (path if station < SPAN_MM / 2 else reflected).translated(
                f"{mark}-{index + 1}", station
            )
            for index, station in enumerate(stations)
        )
        shape = {
            "section_axis_bounds_mm": bounds,
            "closure_corner": "upper left" if mark == "BX12-O" else "lower right",
            "bend_centreline_radius_mm": BEAM_HOOP_RADIUS_MM,
            "closure_hook_angles_deg": [135, 135],
            "closure_tail_mm": BEAM_HOOP_TAIL_MM,
            "closure_run_mm": BEAM_CLOSURE_RUN_MM,
            "closure_rise_left_mm": (
                -BEAM_CLOSURE_RISE_MM if mark == "BX12-O" else BEAM_CLOSURE_RISE_MM
            ),
            "right_half_installation": "Rotate 180 degrees about the transverse horizontal axis.",
            "first_right_orientation_station_mm": next(
                station for station in stations if station > SPAN_MM / 2
            ),
            "closure_offset_angles_deg": [angle, -angle],
            "local_centreline_xyz_mm": path.points,
            "arc_sagitta_bound_mm": path.sagitta_mm,
        }
        schedule[mark] = _mark(mark, BEAM_HOOP_DIA_MM, cut, stations, shape)

    rods = [
        Path(
            f"BX12-{level}-{index}",
            PHI_MM,
            [(across, depth, 0), (across, depth, SPAN_MM)],
        )
        for level, depth in zip(("T", "B"), BAR_LEVELS_MM, strict=True)
        for index, across in enumerate(BAR_AXES_MM, 1)
    ]
    link_clear = _path_pair_minimum(combinations(paths, 2), ALLOCATION_MM)
    bar_clear = _path_pair_minimum(product(paths, rods), ALLOCATION_MM)
    max_pitch = (
        max(
            right - left
            for mark in schedule.values()
            for left, right in pairwise(mark["stations_mm"])
        )
        + 2 * STATION_TOL_MM
    )
    min_phase = min(
        right - left
        for left, right in pairwise(
            sorted(
                station for mark in schedule.values() for station in mark["stations_mm"]
            )
        )
    )
    # Plane through an available insertion station and the beam centre. The
    # projection removes depth, so the clearance bounds the full needle path.
    needle_axis = (300, 0, 75.5)
    needle_clear = min(
        math.sqrt(
            min(
                point_segment_distance_sq(needle_axis, (a[0], 0, a[2]), (b[0], 0, b[2]))
                for a, b, _ in path.chords
            )
        )
        - path.diameter / 2
        - ALLOCATION_MM
        - path.sagitta_mm
        for path in paths + rods
    )
    return {
        "marks": schedule,
        "adverse_family_pitch_mm": max_pitch,
        "minimum_reference_plane_gap_mm": min_phase,
        "hoop_to_hoop": link_clear,
        "hoop_to_longitudinal": bar_clear,
        "probe_station_mm": needle_axis[2],
        "probe_across_mm": needle_axis[0],
        "compaction_diameter_mm": 2 * needle_clear,
        "pass": (
            link_clear["adverse_clearance_mm"] > 0
            and bar_clear["adverse_clearance_mm"] > 0
            and 2 * needle_clear >= 40
            and max_pitch <= min(BAR_LEVELS_MM[1] / 4, 6 * PHI_MM, 100)
        ),
    }


def beam_bars(exterior):
    """Resolve each continuous bar once, from west anchorage to east hook."""
    west = WEST_CLEAR_SPAN_MM + WEST_EMBEDMENT_MM
    prefix = west + 600 + SPAN_MM
    required_ld = 0.87 * 500 * PHI_MM / (4 * 2.4)
    west_adverse_embedment = WEST_EMBEDMENT_MM - 2
    far_wall_cover = (
        WEST_SUPPORT_DEPTH_MM - WEST_EMBEDMENT_MM - PHI_MM / 2 - ALLOCATION_MM
    )
    rows = []
    for hook in exterior["placement"]["x_hook_paths"]:
        face = "TOP" if "-TOP-" in hook["bar_id"] else "BOTTOM"
        member_mark = "BX12-T" if face == "TOP" else "BX12-B"
        number = int(hook["bar_id"].rsplit("-", maxsplit=1)[1])
        cut = prefix + hook["centreline_length_beyond_face_mm"]
        rows.append(
            {
                "bar_id": f"{member_mark}-{number}",
                "mark": member_mark,
                "diameter_mm": PHI_MM,
                "interior_joint_path_id": f"BX-{face}-{number}",
                "exterior_joint_path_id": hook["bar_id"],
                "across_mm": hook["start_at_inner_face_xyz_mm"][1],
                "depth_mm": hook["start_at_inner_face_xyz_mm"][2],
                "west_end_project_x_mm": -west - 600,
                "interior_west_face_x_mm": -600,
                "interior_east_face_x_mm": 0,
                "exterior_inside_face_x_mm": SPAN_MM,
                "east_tangent_x_mm": SPAN_MM + hook["bend_start_xyz_mm"][0],
                "east_bend_end_x_mm": SPAN_MM + hook["bend_end_xyz_mm"][0],
                "east_tail_end_z_mm": hook["tail_end_xyz_mm"][2],
                "cut_mm": cut,
                "mass_kg": _mass(PHI_MM, cut, 1),
            }
        )
    return {
        "bars": rows,
        "total_length_mm": sum(row["cut_mm"] for row in rows),
        "mass_kg": sum(row["mass_kg"] for row in rows),
        "required_west_development_mm": required_ld,
        "adverse_west_development_mm": west_adverse_embedment,
        "available_far_wall_cover_mm": far_wall_cover,
        "ordered_stock_length_mm": 12000,
        "pass": west_adverse_embedment >= required_ld
        and far_wall_cover >= 40
        and all(row["cut_mm"] + 2 <= 12000 for row in rows),
    }


def _beam_sections(beam, beam_response, pitch):
    span = beam["clear_span_m"]
    load = beam["factored_udl_kn_m"]
    m0, m1 = beam["sectional_end_moments_knm"]
    r0, r1 = beam["vertical_reactions_kn"]
    zero_shear = r0 / load
    checks_at = {
        "J1-face": (0.0, m0, r0),
        "J2-face": (span, m1, -r1),
    }
    if 0 < zero_shear < span:
        checks_at["zero-shear"] = (
            zero_shear,
            m0 + r0 * zero_shear - load * zero_shear**2 / 2,
            0.0,
        )
    mu = beam_response["moment_knm"]
    capacity, vs, crush = shear_capacity(
        BAR_LEVELS_MM[1], WIDTH_MM, BEAM_HOOP_DIA_MM, pitch, 415, 0
    )
    min_link_ratio = 0.4 / (0.87 * 415)
    return {
        "flexural_capacity_knm_each_face": mu,
        "steel_shear_capacity_kn": vs,
        "crushing_bound_kn": crush,
        "accepted_shear_capacity_kn": capacity,
        "minimum_shear_links_pass": 2 * math.pi * 10**2 / 4 / (WIDTH_MM * pitch)
        >= min_link_ratio,
        "stations": {
            name: {
                "x_m": x,
                "sectional_moment_knm": moment,
                "sectional_shear_kn": shear,
                "flexure_utilization": abs(moment) / mu,
                "shear_utilization": abs(shear) / capacity,
            }
            for name, (x, moment, shear) in checks_at.items()
        },
    }


def beam_strength(action_rows, interior, exterior, links):
    response = rectangular_section(
        WIDTH_MM, DEPTH_MM, 30, 500, [(70, 4, 20), (675, 4, 20)]
    )
    result = {
        combo: _beam_sections(
            action["beams"]["BX12"], response, links["adverse_family_pitch_mm"]
        )
        for combo, action in action_rows.items()
    }
    cap_shear_controls = {}
    for joint, end_plane_rows, side in (
        ("J1", interior["directions"], "plus"),
        ("J2", exterior["directions"], "minus"),
    ):
        cap_shear_controls[joint] = max(
            (
                {
                    "direction": direction,
                    "combination_id": row["combination_id"],
                    **row["beam_capacity_shear"][side],
                }
                for direction in ("X+", "X-")
                for row in end_plane_rows[direction]["rows"]
            ),
            key=lambda row: row["utilization"],
        )
    governing = {}
    for family in ("flexure", "shear"):
        key = f"{family}_utilization"
        governing[family] = max(
            (
                {"combination_id": combo, "station": location, **station}
                for combo, row in result.items()
                for location, station in row["stations"].items()
            ),
            key=lambda row: row[key],
        )
    return {
        "section": response,
        "rows": result,
        "governing": governing,
        "governing_capacity_shear_at_faces": cap_shear_controls,
        "pass": response["tension_ductile"]
        and all(governing[family][f"{family}_utilization"] <= 1 for family in governing)
        and all(row["pass"] for row in cap_shear_controls.values())
        and all(row["minimum_shear_links_pass"] for row in result.values()),
    }


def column_strength(action_rows, joint_results, joint_requests):
    """Check four short two-plane legs at both limiting ends with shared hoops."""
    columns = {}
    pitch_mm = 65 + 2 * STATION_TOL_MM
    width = 600
    edge = 89.5
    steel = ((edge, 3, 32), (width / 2, 2, 32), (width - edge, 3, 32))
    for combo, source in action_rows.items():
        direction = source["direction"]
        for member, leg in source["columns"].items():
            joint, end = leg["joint"], leg["position"]
            request = joint_requests[joint]
            height = request["column_clear_heights_mm"][end]
            govern_shear = next(
                row
                for row in joint_results[joint]["directions"][direction]["rows"]
                if row["combination_id"] == combo
            )["column_capacity_shear"][end]
            # Include the larger seismic capacity shear in the active plane,
            # keeping the simultaneous orthogonal analysis shear.
            concurrent = leg["near_face"]["force_kn"]
            shear_demand = govern_shear["demand_kn"] + abs(
                concurrent[1 if direction[0] == "X" else 0]
            )
            near = leg["near_face"]
            far = leg["boundary_face"]
            minimum_pu = min(abs(near["force_kn"][2]), abs(far["force_kn"][2]))
            factor = min(1.5, 1 + 3000 * minimum_pu / (width**2 * 30))
            concrete = 0.37 * width * (width - edge) * factor / 1000
            phi = request["column_link_mm"]
            shear, steel_v, crushing = shear_capacity(
                width - edge, width, phi, pitch_mm, 415, concrete
            )
            ends = {}
            for label, face in (("joint", near), ("boundary", far)):
                pu = abs(face["force_kn"][2])
                response = rectangular_section(width, width, 30, 500, steel, pu)
                ex = max(20, height / 500 + width / 30)
                min_m = pu * ex / 1000
                demand_x, demand_y = (
                    max(abs(m), min_m) for m in face["couple_knm"][:2]
                )
                resistance = response["moment_knm"]
                ends[label] = {
                    "pu_kn": pu,
                    "signed_moments_knm": face["couple_knm"][:2],
                    "minimum_eccentricity_mm": ex,
                    "biaxial_demand_abs_knm": (demand_x, demand_y),
                    "uniaxial_moment_capacity_knm_each_axis": resistance,
                    "conservative_linear_biaxial_utilization": (demand_x + demand_y)
                    / resistance,
                }
            columns.setdefault(member, {})[combo] = {
                "ends": ends,
                "effective_length_mm": height,
                "slenderness_each_axis": height / width,
                "shear_component_sum_kn": shear_demand,
                "steel_shear_capacity_kn": steel_v,
                "crushing_bound_kn": crushing,
                "accepted_shear_capacity_kn": shear,
                "shear_utilization": shear_demand / shear,
            }
    result = {}
    for member, rows in columns.items():
        flexure = max(
            (
                {"combination_id": combo, "end": end, **values}
                for combo, row in rows.items()
                for end, values in row["ends"].items()
            ),
            key=lambda row: row["conservative_linear_biaxial_utilization"],
        )
        shear = max(
            ({"combination_id": combo, **row} for combo, row in rows.items()),
            key=lambda row: row["shear_utilization"],
        )
        end_height = shear["effective_length_mm"]
        joint_id = member.split("-")[1]
        first_key = (
            "column_first_end_hoop_mm"
            if joint_id == "J1"
            else "column_end_link_first_mm"
        )
        first_station = joint_requests[joint_id][first_key]
        tie_stations = list(range(first_station, end_height, 65))
        transition_ok = (
            first_station + STATION_TOL_MM <= 50 and end_height - tie_stations[-1] <= 65
        )
        result[member] = {
            "rows": rows,
            "governing_flexure": flexure,
            "governing_shear": shear,
            "longitudinal_bar_count": 8,
            "longitudinal_bar_diameter_mm": COLUMN_BAR_MM,
            "transverse_group_stations_from_face_mm": tie_stations,
            "transverse_pieces_per_group": 3,
            "adverse_transverse_pitch_mm": pitch_mm,
            "pass": (
                flexure["conservative_linear_biaxial_utilization"] <= 1
                and shear["shear_utilization"] <= 1
                and shear["slenderness_each_axis"] <= 12
                and flexure["pu_kn"] / (width**2 / 1000) <= 0.40 * 30
                and transition_ok
            ),
        }
    return result


def _column_double_return(name, axis_y, rotate):
    radius = 40
    tail = 136
    a, b = 94.5, 505.5
    west = arc((a, axis_y, 0), radius, 135, 270)
    east = arc((b, axis_y, 0), radius, 270, 405)
    projection = tail / math.sqrt(2)
    points = [
        (west[0][0] + projection, west[0][1] + projection, 0),
        *west,
        *east,
        (east[-1][0] - projection, east[-1][1] + projection, 0),
    ]
    if rotate:
        points = [(600 - y, x, z) for x, y, z in points]
    path = Path(name, 16, points, sagitta(radius))
    return path, b - a + 1.5 * math.pi * radius + 2 * tail


def _positioned_column_groups(joint):
    c, d, radius, tail, run, rise = 57, 543, 40, 136, 60, 20
    tx, cut_x = _column_double_return("C-TX", 300 if joint == "J1" else 302, False)
    if joint == "J1":
        body, hoop_cut, _ = _closed_hoop("C-H", c, d, c, d, radius, tail, run, rise, 16)
        ty, cut_y = _column_double_return("C-TY", 300, True)
        return ((body, hoop_cut, 0), (tx, cut_x, -20), (ty, cut_y, 20))
    west, west_cut, _ = _closed_hoop("C-W", c, 331, c, d, radius, tail, run, rise, 16)
    east, east_cut, _ = _closed_hoop("C-E", 269, d, c, d, radius, tail, run, -rise, 16)
    return ((west, west_cut, -20), (east, east_cut, 20), (tx, cut_x, 0))


def _leg_schedule(member, stations, joint_result):
    _, joint, end = member.split("-")
    group = _positioned_column_groups(joint)
    sign = -1 if end == "upper" else 1
    face = 0 if end == "upper" else DEPTH_MM
    first_two_groups = [
        template.translated(f"{template.name}-{i}", face + sign * station + offset)
        for i, station in enumerate(stations[:2], start=1)
        for template, _, offset in group
    ]
    placement = joint_result["placement"]
    axes = placement[
        "column_longitudinal_axes_xy_mm" if joint == "J1" else "column_axes_xy_mm"
    ]
    column_bars = [
        Path(f"C-{i}", 32, [(x, y, -180), (x, y, DEPTH_MM + 180)])
        for i, (x, y) in enumerate(axes, 1)
    ]
    joint_groups = []
    if joint == "J1":
        marks = placement["column_transverse_joint_marks"]
        for template, _, _ in group:
            station = marks[template.name]["stations_mm"][0 if end == "upper" else -1]
            joint_groups.append(template.translated(f"joint:{template.name}", station))
    else:
        for name, mark in placement["joint_tie_marks"].items():
            template = Path(
                name,
                16,
                mark["local_centreline_polyline_mm"],
                mark["sampled_arc_max_deviation_mm"],
            )
            station = mark["stations_mm"][0 if end == "upper" else -1]
            joint_groups.append(template.translated(f"joint:{name}", station))
    clearances = {
        "adjacent_leg_groups": _path_pair_minimum(
            combinations(first_two_groups, 2), ALLOCATION_MM
        ),
        "joint_to_end_zone_transition": _path_pair_minimum(
            product(first_two_groups, joint_groups), ALLOCATION_MM
        ),
        "column_bars_to_leg_links": _path_pair_minimum(
            product(column_bars, first_two_groups), ALLOCATION_MM
        ),
    }
    # Place the complete repeating hoop shape at the end of the column core,
    # and count its full cut once per listed base station.
    zone = {}
    for template, cut, offset in group:
        mark = f"{member}:{template.name}"
        zone[mark] = _mark(
            mark,
            16,
            cut,
            stations,
            {
                "position": end,
                "source": f"column_tie_sections.{joint}.{template.name}",
                "global_depth_offset_from_group_mm": offset,
                "hook_angles_deg": [135, 135],
            },
        )
    return zone, clearances


def artifacts(joints, columns, links, bars):
    """Reconcile joint, shared beam and cut-column quantities by unique mark."""
    schedule = {
        mark: {**entry, "shape": {"source": f"shared_beam.links.marks.{mark}.shape"}}
        for mark, entry in links["marks"].items()
    }
    for face in ("T", "B"):
        mark = f"BX12-{face}"
        members = [row for row in bars["bars"] if row["mark"] == mark]
        cuts = {row["cut_mm"] for row in members}
        assert len(cuts) == 1
        bar_ids = [row["bar_id"] for row in members]
        schedule[mark] = _mark(
            mark,
            20,
            cuts.pop(),
            bar_ids,
            {"scope": "continuous_bx12_through_j1_to_j2_return"},
        )
        schedule[mark].pop("stations_mm")
        schedule[mark]["bar_ids"] = bar_ids
    for name, result in joints.items():
        placement = result["placement"]
        marks = (
            placement["column_transverse_joint_marks"]
            if name == "J1"
            else placement["joint_tie_marks"]
        )
        for short, source in marks.items():
            mark = f"{name}:{short}"
            schedule[mark] = _mark(
                mark,
                16,
                source["cut_mm" if name == "J1" else "nominal_cut_length_mm"],
                source["stations_mm"],
                {"owner": name, "local_mark": short},
            )
    column_placements = {}
    for member, checks in columns.items():
        marks, minimum = _leg_schedule(
            member,
            checks["transverse_group_stations_from_face_mm"],
            joints[member.split("-")[1]],
        )
        schedule.update(marks)
        column_placements[member] = minimum
    return {
        "checked_tie_and_beam_cut_marks": schedule,
        "unique_cut_piece_count": sum(row["quantity"] for row in schedule.values()),
        "shared_longitudinal_sources": {
            row["bar_id"]: [
                row["interior_joint_path_id"],
                row["exterior_joint_path_id"],
            ]
            for row in bars["bars"]
        },
        "continuous_column_local_segments": {
            joint: {
                "axis_coordinates_mm": result["placement"][
                    (
                        "column_longitudinal_axes_xy_mm"
                        if joint == "J1"
                        else "column_axes_xy_mm"
                    )
                ],
                "diameter_mm": 32,
                "local_length_mm": 3400 + 745 + 3600,
                "piece_count": 8,
                "boundary_anchorage_unresolved": True,
            }
            for joint, result in joints.items()
        },
        "column_tie_sections": {
            joint: {
                path.name: {
                    "local_centreline_xyz_mm": path.points,
                    "arc_sagitta_bound_mm": path.sagitta_mm,
                    "cut_mm": cut,
                }
                for path, cut, _ in _positioned_column_groups(joint)
            }
            for joint in joints
        },
        "column_link_clearances": column_placements,
        "cut_weight_kg": sum(row["mass_kg"] for row in schedule.values()),
        "pass": all(
            row["adverse_clearance_mm"] > 0
            for family in column_placements.values()
            for row in family.values()
        ),
    }
