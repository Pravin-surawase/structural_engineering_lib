"""Resolve the bounded PROJECT03 common-bay cage from checked joint geometry."""

from __future__ import annotations

import math
from collections.abc import Mapping
from itertools import combinations, pairwise, product
from typing import Any

from structural_lib.codes.is456.beam.detailing import (
    calculate_development_length_unrounded,
)
from structural_lib.codes.is13920.exterior_joint_cage import (
    _arc,
    _closed,
    _minimum,
    _offset_angle,
    _Path,
    _point_seg_sq,
    _sag,
)

__all__ = ["FrameCageDomainError", "reconcile_frame_marks", "resolve_shared_beam"]


class FrameCageDomainError(ValueError):
    """The supplied final-fit cage cannot be resolved into checked marks."""


def _mass(diameter_mm: float, length_mm: float, quantity: int = 1) -> float:
    return 7850 * math.pi * (diameter_mm / 2000) ** 2 * (length_mm / 1000) * quantity


def _mark(
    mark: str, diameter: float, cut: float, stations: list[Any], shape: dict[str, Any]
) -> dict[str, Any]:
    quantity = len(stations)
    return {
        "bar_mark": mark,
        "diameter_mm": diameter,
        "quantity": quantity,
        "cut_mm": cut,
        "total_length_mm": cut * quantity,
        "mass_kg": _mass(diameter, cut, quantity),
        "stations_mm": stations,
        "shape": shape,
    }


def _checked_x_hooks(joints: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    return list(joints["J2"]["placement"]["x_hook_paths"])


def resolve_shared_beam(
    inputs: Mapping[str, Mapping[str, Any]],
    joints: Mapping[str, Mapping[str, Any]],
    detailing: Mapping[str, Any],
) -> dict[str, Any]:
    """Resolve link grids and the eight once-counted common X bars.

    Coordinate contract: J1 east face is x=0, J1 west face is x=-J1 width,
    and the J2 inside face is one clear span from the origin. The local
    hook coordinates and bend data remain those supplied
    by J2's checked hook paths.
    """
    j1, j2 = inputs["J1"], inputs["J2"]
    width = float(j2["column_width_mm"])
    depth = float(j2["joint_depth_mm"])
    axes = tuple(float(value) for value in j2["beam_axes_mm"]["X"])
    top = float(j2["beam_top_z_mm"]["X"])
    levels = (top, depth - top)
    phi = float(j2["beam_bar_mm"]["X"])
    link_phi = float(j2["beam_link_mm"])
    radius = float(j2["beam_link_centre_radius_mm"]["X"])
    side_inset = float(j2["beam_link_seat_inset_mm"]["X"])
    top_inset = float(
        j1["beam_link_depth_seat_inset_mm"] or j1["beam_link_seat_inset_mm"]
    )
    tail = float(detailing["beam_link_hook_tail_mm"])
    run, rise = float(detailing["beam_closure_run_mm"]), float(
        detailing["beam_closure_rise_mm"]
    )
    span = float(j2["beam_clear_spans_mm"]["X"]["minus"])
    pitch, tolerance = float(j2["beam_pitch_mm"]), float(j2["tie_station_tolerance_mm"])
    allocation = float(j2["axis_tolerance_mm"]) + float(j2["diameter_overage_mm"]) / 2
    marks: dict[str, dict[str, Any]] = {}
    link_paths: list[_Path] = []
    centre_fill = detailing["center_fill_mm"]
    if set(centre_fill) != {"BX12-O", "BX12-M"}:
        raise FrameCageDomainError(
            "Declare the centre stations for both link families."
        )
    turn = _offset_angle(run, rise, radius)
    if turn is None or 2 * radius - link_phi < 4 * link_phi:
        raise FrameCageDomainError(
            "The selected hook and jog bend geometry cannot be fabricated."
        )
    angle = math.degrees(turn)
    first_outer = float(j2["beam_first_link_mm"])
    first_middle = first_outer + float(j2["beam_inner_link_offset_mm"])
    extra_station = max(0.0, tolerance - float(j2["axis_tolerance_mm"]))
    probe_station = 0.5 * (first_middle + first_outer + pitch)
    for mark, edges, first, sign in (
        ("BX12-O", (axes[0], axes[-1]), first_outer, -1.0),
        ("BX12-M", (axes[1], axes[-2]), first_middle, 1.0),
    ):
        bounds = (
            edges[0] - side_inset,
            edges[1] + side_inset,
            levels[0] - top_inset,
            depth - (levels[0] - top_inset),
        )
        if (
            bounds[1] - bounds[0] <= 2 * radius + run
            or bounds[3] - bounds[2] <= 2 * radius
        ):
            raise FrameCageDomainError(
                f"{mark} corner and closure bends exceed the hoop outline."
            )
        path, cut = _closed(
            mark,
            *bounds,
            radius,
            tail,
            run,
            sign * rise,
            turn,
            link_phi,
        )
        if mark == "BX12-M":
            path = _Path(
                mark,
                link_phi,
                [(width - x, depth - z, q) for x, z, q in path.points],
                path.sagitta,
            )
        fills = centre_fill[mark]
        left_stop = min(fills, default=span / 2)
        right_stop = span - max(fills, default=span / 2)
        left = [
            first + pitch * index
            for index in range(math.ceil((left_stop - first) / pitch))
        ]
        right = [
            first + pitch * index
            for index in range(math.ceil((right_stop - first) / pitch))
        ]
        stations = [*left, *fills, *(span - value for value in reversed(right))]
        if not left or not right:
            raise FrameCageDomainError(
                f"{mark} requires checked links at both beam faces."
            )
        if (
            any(not 0 < station < span for station in stations)
            or stations != sorted(stations)
            or len(set(stations)) != len(stations)
        ):
            raise FrameCageDomainError(
                f"{mark} station grid must be ordered, unique, and within the clear span."
            )
        reflected = _Path(
            mark,
            link_phi,
            [(x, depth - z, -q) for x, z, q in path.points],
            path.sagitta,
        )
        link_paths.extend(
            (path if station < span / 2 else reflected).translate(
                f"{mark}-{index}", station, extra_station
            )
            for index, station in enumerate(stations, start=1)
        )
        marks[mark] = _mark(
            mark,
            link_phi,
            cut,
            stations,
            {
                "section_axis_bounds_mm": bounds,
                "closure_corner": "upper left" if mark == "BX12-O" else "lower right",
                "bend_centreline_radius_mm": radius,
                "closure_hook_angles_deg": [135, 135],
                "closure_tail_mm": tail,
                "closure_run_mm": run,
                "closure_rise_left_mm": sign * rise,
                "right_half_installation": "Rotate 180 degrees about the transverse horizontal axis.",
                "first_right_orientation_station_mm": next(
                    value for value in stations if value > span / 2
                ),
                "closure_offset_angles_deg": [angle, -angle],
                "local_centreline_xyz_mm": path.points,
                "arc_sagitta_bound_mm": path.sagitta,
            },
        )
    rods = [
        _Path(
            f"BX12-{label}-{index}", phi, [(across, level, 0.0), (across, level, span)]
        )
        for label, level in zip(("T", "B"), levels, strict=True)
        for index, across in enumerate(axes, 1)
    ]
    hoop_clear = _minimum(combinations(link_paths, 2), allocation)
    bar_clear = _minimum(product(link_paths, rods), allocation)
    adverse_pitch = (
        max(
            right - left
            for entry in marks.values()
            for left, right in pairwise(entry["stations_mm"])
        )
        + 2 * tolerance
    )
    all_stations = sorted(
        value for entry in marks.values() for value in entry["stations_mm"]
    )
    phase = min(right - left for left, right in pairwise(all_stations))
    if phase <= 2 * tolerance:
        raise FrameCageDomainError(
            "Link family station grids overlap within the declared station tolerance."
        )
    probe = (width / 2, 0.0, probe_station)
    needle_clear = min(
        math.sqrt(
            min(
                _point_seg_sq(probe, (a[0], 0.0, a[2]), (b[0], 0.0, b[2]))
                for a, b, _ in path.chords
            )
        )
        - path.diameter / 2
        - allocation
        - path.sagitta
        for path in [*link_paths, *rods]
    )

    west = float(detailing["west_clear_span_mm"]) + float(
        detailing["west_development_mm"]
    )
    prefix = west + float(j1["column_width_mm"]) + span
    bars: list[dict[str, Any]] = []
    x_paths = joints["J1"]["placement"]["beam_bar_paths"]["X"]
    for hook, interior in zip(_checked_x_hooks(joints), x_paths, strict=True):
        face = "TOP" if "-TOP-" in hook["bar_id"] else "BOTTOM"
        mark, number = f"BX12-{'T' if face == 'TOP' else 'B'}", int(
            hook["bar_id"].rsplit("-", 1)[1]
        )
        axis, level = hook["start_at_inner_face_xyz_mm"][1:]
        if (interior["across_axis_mm"], interior["depth_mm"]) != (axis, level):
            raise FrameCageDomainError(
                "The checked interior and exterior bar paths do not align."
            )
        cut = prefix + hook["centreline_length_beyond_face_mm"]
        bars.append(
            {
                "bar_id": f"{mark}-{number}",
                "mark": mark,
                "diameter_mm": phi,
                "interior_joint_path_id": interior["bar_id"],
                "exterior_joint_path_id": hook["bar_id"],
                "across_mm": hook["start_at_inner_face_xyz_mm"][1],
                "depth_mm": hook["start_at_inner_face_xyz_mm"][2],
                "west_end_project_x_mm": -west - float(j1["column_width_mm"]),
                "interior_west_face_x_mm": -float(j1["column_width_mm"]),
                "interior_east_face_x_mm": 0.0,
                "exterior_inside_face_x_mm": span,
                "east_tangent_x_mm": span + hook["bend_start_xyz_mm"][0],
                "east_bend_end_x_mm": span + hook["bend_end_xyz_mm"][0],
                "east_tail_end_z_mm": hook["tail_end_xyz_mm"][2],
                "cut_mm": cut,
                "mass_kg": _mass(phi, cut),
            }
        )
    required_ld = calculate_development_length_unrounded(
        phi, j2["beam_fck_mpa"], j2["longitudinal_fy_mpa"]
    )
    tolerance_cut = j2["anchor_cut_length_tolerance_mm"]
    adverse_development = detailing["west_development_mm"] - tolerance_cut
    far_wall_cover = (
        detailing["west_support_depth_mm"]
        - detailing["west_development_mm"]
        - phi / 2
        - allocation
    )
    inside_span = all(
        path.bounds[2][0] - link_phi / 2 - tolerance > 0
        and path.bounds[2][1] + link_phi / 2 + tolerance < span
        for path in link_paths
    )
    return {
        "links": {
            "marks": marks,
            "adverse_family_pitch_mm": adverse_pitch,
            "minimum_reference_plane_gap_mm": phase,
            "hoop_to_hoop": hoop_clear,
            "hoop_to_longitudinal": bar_clear,
            "probe_station_mm": probe[2],
            "probe_across_mm": probe[0],
            "compaction_diameter_mm": 2 * needle_clear,
            "pass": hoop_clear["adverse_clearance_mm"] > 0
            and bar_clear["adverse_clearance_mm"] > 0
            and 2 * needle_clear
            >= max(j1["compaction_head_mm"], j2["compaction_head_mm"])
            and inside_span
            and adverse_pitch <= min(levels[1] / 4, 6 * phi, 100),
        },
        "longitudinal": {
            "bars": bars,
            "total_length_mm": sum(row["cut_mm"] for row in bars),
            "mass_kg": sum(row["mass_kg"] for row in bars),
            "required_west_development_mm": required_ld,
            "adverse_west_development_mm": adverse_development,
            "available_far_wall_cover_mm": far_wall_cover,
            "ordered_stock_length_mm": detailing["stock_length_mm"],
            "pass": adverse_development >= required_ld
            and far_wall_cover >= j1["required_column_cover_mm"]
            and all(
                row["cut_mm"] + tolerance_cut <= detailing["stock_length_mm"]
                for row in bars
            ),
        },
    }


def _checked_turn(run: float, rise: float, radius: float) -> float:
    turn = _offset_angle(run, rise, radius)
    if turn is None:
        raise FrameCageDomainError(
            "The column link closure cannot fit the declared bend radius."
        )
    return turn


def _double_return(
    name: str,
    axis: float,
    rotate: bool,
    width: float,
    edge: float,
    radius: float,
    tail: float,
    diameter: float,
) -> tuple[_Path, float]:
    near, far = edge + 5, width - edge - 5
    west, east = _arc((near, axis, 0), radius, 135, 270), _arc(
        (far, axis, 0), radius, 270, 405
    )
    projection = tail / math.sqrt(2)
    points = [
        (west[0][0] + projection, west[0][1] + projection, 0),
        *west,
        *east,
        (east[-1][0] - projection, east[-1][1] + projection, 0),
    ]
    if rotate:
        points = [(width - y, x, z) for x, y, z in points]
    return (
        _Path(name, diameter, points, _sag(radius)),
        far - near + 1.5 * math.pi * radius + 2 * tail,
    )


def _column_groups(
    joint: str, result: Mapping[str, Any], inputs: Mapping[str, Mapping[str, Any]]
) -> tuple[tuple[_Path, float, float], ...]:
    request, placement = inputs[joint], result["placement"]
    width, radius, tail = (
        float(request["column_width_mm"]),
        float(
            request["column_link_radius_mm"]
            if joint == "J2"
            else request["column_link_centre_radius_mm"]
        ),
        float(
            request["column_link_tail_mm"]
            if joint == "J2"
            else request["column_hook_tail_mm"]
        ),
    )
    diameter = request["column_link_mm"]
    edge = request["column_bar_edge_mm"]
    c = request["column_cover_mm"] + diameter / 2
    d = width - c
    exterior = joint == "J2"
    run = request[
        "column_link_ramp_run_mm" if exterior else "column_hook_ramp_length_mm"
    ]
    rise = request["link_group_offset_mm" if exterior else "column_hook_rise_mm"]
    offset = request[
        "link_group_offset_mm" if exterior else "cross_tie_station_offset_mm"
    ]
    turn = _checked_turn(run, rise, radius)
    axis = request["column_cross_tie_axis_y_mm"] if exterior else width / 2
    tx, tx_cut = _double_return(
        "C-TX", axis, False, width, edge, radius, tail, diameter
    )
    if not exterior:
        checked = placement["column_transverse_joint_marks"]["C-H"]
        body = _Path(
            "C-H",
            diameter,
            [tuple(q) for q in checked["local_centreline_xyz_mm"]],
            _sag(radius),
        )
        ty, ty_cut = _double_return(
            "C-TY", width / 2, True, width, edge, radius, tail, diameter
        )
        return (
            (body, checked["cut_mm"], 0.0),
            (tx, tx_cut, -offset),
            (ty, ty_cut, offset),
        )
    overlap = request["column_link_overlap_half_mm"]
    west, west_cut = _closed(
        "C-W", c, width / 2 + overlap, c, d, radius, tail, run, rise, turn, diameter
    )
    east, east_cut = _closed(
        "C-E", width / 2 - overlap, d, c, d, radius, tail, run, -rise, turn, diameter
    )
    return ((west, west_cut, -offset), (east, east_cut, offset), (tx, tx_cut, 0.0))


def _leg_schedule(
    member: str,
    stations: list[float],
    joint_result: Mapping[str, Any],
    inputs: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    _, joint, end = member.split("-")
    request, depth = inputs[joint], float(inputs[joint]["joint_depth_mm"])
    groups = _column_groups(joint, joint_result, inputs)
    if len(stations) < 2:
        raise FrameCageDomainError(f"{member} needs at least two resolved link groups.")
    allowance = request["axis_tolerance_mm"] + request["diameter_overage_mm"] / 2
    extra_station = max(
        0, request["tie_station_tolerance_mm"] - request["axis_tolerance_mm"]
    )
    sign, face = (-1.0, 0.0) if end == "upper" else (1.0, depth)
    next_groups = [
        template.translate(
            f"{template.name}-{index}", face + sign * station + offset, extra_station
        )
        for index, station in enumerate(stations[:2], 1)
        for template, _, offset in groups
    ]
    placement = joint_result["placement"]
    axes = placement[
        "column_longitudinal_axes_xy_mm" if joint == "J1" else "column_axes_xy_mm"
    ]
    bars = [
        _Path(
            f"C-{index}",
            float(request["column_bar_mm"]),
            [(x, y, -180), (x, y, depth + 180)],
        )
        for index, (x, y) in enumerate(axes, 1)
    ]
    marks = (
        placement["column_transverse_joint_marks"]
        if joint == "J1"
        else placement["joint_tie_marks"]
    )
    joint_paths = []
    for template, _, _ in groups:
        source = marks[template.name]
        if joint == "J1":
            # The project group template is the checked section geometry.
            station = source["stations_mm"][0 if end == "upper" else -1]
            joint_paths.append(
                template.translate(f"joint:{template.name}", station, extra_station)
            )
        else:
            station = source["stations_mm"][0 if end == "upper" else -1]
            joint_paths.append(
                _Path(
                    template.name,
                    template.diameter,
                    [tuple(point) for point in source["local_centreline_polyline_mm"]],
                    source["sampled_arc_max_deviation_mm"],
                ).translate(f"joint:{template.name}", station, extra_station)
            )
    clearance = {
        "adjacent_leg_groups": _minimum(combinations(next_groups, 2), allowance),
        "joint_to_end_zone_transition": _minimum(
            product(next_groups, joint_paths), allowance
        ),
        "column_bars_to_leg_links": _minimum(product(bars, next_groups), allowance),
    }
    schedule = {}
    for template, cut, offset in groups:
        mark = f"{member}:{template.name}"
        schedule[mark] = _mark(
            mark,
            template.diameter,
            cut,
            stations,
            {
                "position": end,
                "source": f"column_tie_sections.{joint}.{template.name}",
                "global_depth_offset_from_group_mm": offset,
                "hook_angles_deg": [135, 135],
            },
        )
    return schedule, clearance


def reconcile_frame_marks(
    joints: Mapping[str, Mapping[str, Any]],
    columns: Mapping[str, Mapping[str, Any]],
    shared: Mapping[str, Any],
    *,
    inputs: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Reconcile one frame BBS by unique checked mark without re-cutting joints."""
    schedule = {
        mark: {**entry, "shape": {"source": f"shared_beam.links.marks.{mark}.shape"}}
        for mark, entry in shared["links"]["marks"].items()
    }
    for face in ("T", "B"):
        mark = f"BX12-{face}"
        rows = [row for row in shared["longitudinal"]["bars"] if row["mark"] == mark]
        cuts = {row["cut_mm"] for row in rows}
        if len(cuts) != 1:
            raise FrameCageDomainError(f"{mark} must have one resolved cut length.")
        entry = _mark(
            mark,
            rows[0]["diameter_mm"],
            cuts.pop(),
            [row["bar_id"] for row in rows],
            {"scope": "continuous_bx12_through_j1_to_j2_return"},
        )
        entry.pop("stations_mm")
        entry["bar_ids"] = [row["bar_id"] for row in rows]
        schedule[mark] = entry
    for name, result in joints.items():
        placement = result["placement"]
        source_marks = (
            placement["column_transverse_joint_marks"]
            if name == "J1"
            else placement["joint_tie_marks"]
        )
        for short, source in source_marks.items():
            cut = source["cut_mm" if name == "J1" else "nominal_cut_length_mm"]
            schedule[f"{name}:{short}"] = _mark(
                f"{name}:{short}",
                source.get("diameter_mm", inputs[name]["column_link_mm"]),
                cut,
                list(source["stations_mm"]),
                {"owner": name, "local_mark": short},
            )
    column_clearances = {}
    for member, check in columns.items():
        marks, clearances = _leg_schedule(
            member,
            list(check["transverse_group_stations_from_face_mm"]),
            joints[member.split("-")[1]],
            inputs,
        )
        schedule.update(marks)
        column_clearances[member] = clearances
    sections = {
        joint: {
            path.name: {
                "local_centreline_xyz_mm": path.points,
                "arc_sagitta_bound_mm": path.sagitta,
                "cut_mm": cut,
            }
            for path, cut, _ in _column_groups(joint, result, inputs)
        }
        for joint, result in joints.items()
    }
    segments = {
        joint: {
            "axis_coordinates_mm": result["placement"][
                (
                    "column_longitudinal_axes_xy_mm"
                    if joint == "J1"
                    else "column_axes_xy_mm"
                )
            ],
            "diameter_mm": inputs[joint]["column_bar_mm"],
            "local_length_mm": inputs[joint]["joint_depth_mm"]
            + sum(inputs[joint]["column_clear_heights_mm"].values()),
            "piece_count": 8,
            "boundary_anchorage_unresolved": True,
        }
        for joint, result in joints.items()
    }
    return {
        "checked_tie_and_beam_cut_marks": schedule,
        "unique_cut_piece_count": sum(row["quantity"] for row in schedule.values()),
        "shared_longitudinal_sources": {
            row["bar_id"]: [
                row["interior_joint_path_id"],
                row["exterior_joint_path_id"],
            ]
            for row in shared["longitudinal"]["bars"]
        },
        "continuous_column_local_segments": segments,
        "column_tie_sections": sections,
        "column_link_clearances": column_clearances,
        "cut_weight_kg": sum(row["mass_kg"] for row in schedule.values()),
        "pass": all(
            value["adverse_clearance_mm"] > 0
            for family in column_clearances.values()
            for value in family.values()
        ),
    }
