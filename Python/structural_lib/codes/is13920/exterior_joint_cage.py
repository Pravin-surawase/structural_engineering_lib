# SPDX-License-Identifier: MIT
"""Resolved physical paths for the bounded DUCT02 exterior joint."""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from itertools import combinations, pairwise, product
from typing import Any

__all__ = ["exterior_joint_placement"]


def _dot(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=True))


def _sub(a: tuple[float, ...], b: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(x - y for x, y in zip(a, b, strict=True))


def _box(points: list[tuple[float, float, float]]) -> tuple[tuple[float, float], ...]:
    return tuple((min(v), max(v)) for v in zip(*points, strict=True))


def _box_distance_sq(
    a: tuple[tuple[float, float], ...], b: tuple[tuple[float, float], ...]
) -> float:
    return sum(
        max(x0 - y1, y0 - x1, 0.0) ** 2 for (x0, x1), (y0, y1) in zip(a, b, strict=True)
    )


_Point = tuple[float, float, float]


def _point_seg_sq(p: _Point, a: _Point, b: _Point) -> float:
    edge, off = _sub(b, a), _sub(p, a)
    length = _dot(edge, edge)
    t = max(0.0, min(1.0, _dot(off, edge) / length)) if length else 0.0
    return sum((x - t * y) ** 2 for x, y in zip(off, edge, strict=True))


def _seg_sq(a: _Point, b: _Point, c: _Point, d: _Point) -> float:
    answer = min(
        _point_seg_sq(a, c, d),
        _point_seg_sq(b, c, d),
        _point_seg_sq(c, a, b),
        _point_seg_sq(d, a, b),
    )
    u, v, w = _sub(b, a), _sub(d, c), _sub(a, c)
    uu, uv, vv, uw, vw = _dot(u, u), _dot(u, v), _dot(v, v), _dot(u, w), _dot(v, w)
    det = uu * vv - uv**2
    if det > 0:
        s, t = (uv * vw - vv * uw) / det, (uu * vw - uv * uw) / det
        if 0 <= s <= 1 and 0 <= t <= 1:
            answer = min(
                answer,
                sum((z + s * x - t * y) ** 2 for x, y, z in zip(u, v, w, strict=True)),
            )
    return answer


class _Path:
    def __init__(
        self,
        name: str,
        diameter: float,
        points: list[tuple[float, float, float]],
        sagitta: float = 0.0,
        extra_station_allowance: float = 0.0,
    ) -> None:
        self.name, self.diameter, self.points, self.sagitta = (
            name,
            diameter,
            points,
            sagitta,
        )
        self.extra_station_allowance = extra_station_allowance
        self.bounds = _box(points)
        self.chords = [(a, b, _box([a, b])) for a, b in pairwise(points) if a != b]

    def translate(self, name: str, z: float, extra_station_allowance: float) -> _Path:
        return _Path(
            name,
            self.diameter,
            [(x, y, q + z) for x, y, q in self.points],
            self.sagitta,
            extra_station_allowance,
        )


def _arc(
    centre: _Point, radius: float, first: float, last: float, *, xz: bool = False
) -> list[_Point]:
    count = math.ceil(abs(last - first) / 7.5)
    points = []
    cx, cy, cz = centre
    for index in range(count + 1):
        angle = math.radians(first + (last - first) * index / count)
        along = radius * math.cos(angle)
        across = radius * math.sin(angle)
        points.append(
            (cx + along, cy, cz + across) if xz else (cx + along, cy + across, cz)
        )
    return points


def _sag(r: float) -> float:
    return r * (1 - math.cos(math.radians(3.75)))


def _minimum(pairs: Iterable[tuple[_Path, _Path]], allocation: float) -> dict[str, Any]:
    best = math.inf
    names: tuple[str, ...] = ()
    for left, right in pairs:
        deduction = (
            (left.diameter + right.diameter) / 2
            + 2 * allocation
            + left.sagitta
            + right.sagitta
            + left.extra_station_allowance
            + right.extra_station_allowance
        )
        if math.sqrt(_box_distance_sq(left.bounds, right.bounds)) - deduction >= best:
            continue
        # Clamp the search to boxes that can still improve the reported bound.
        pair_minimum_sq = math.inf
        for a, b, box_ab in left.chords:
            for c, d, box_cd in right.chords:
                if _box_distance_sq(box_ab, box_cd) < pair_minimum_sq:
                    pair_minimum_sq = min(pair_minimum_sq, _seg_sq(a, b, c, d))
        value = math.sqrt(pair_minimum_sq) - deduction
        if value < best:
            best = value
            names = left.name, right.name
    return {"adverse_clearance_mm": best, "parts": names}


def _hook(
    mark: str,
    y: float,
    z: float,
    tip: float,
    tail: float,
    radius: float,
    phi: float,
    *,
    down: bool,
) -> tuple[_Path, dict[str, Any]]:
    tangent, sign = tip - radius, (1 if down else -1)
    centre = (tangent, y, z + sign * radius)
    bend = _arc(centre, radius, -90 * sign, 0, xz=True)
    end = (tip, y, centre[2] + sign * tail)
    points = [(0.0, y, z), *bend, end]
    return _Path(mark, phi, points, _sag(radius)), {
        "bar_id": mark,
        "diameter_mm": phi,
        "start_at_inner_face_xyz_mm": points[0],
        "bend_start_xyz_mm": (tangent, y, z),
        "bend_centre_xyz_mm": centre,
        "bend_end_xyz_mm": (tip, y, centre[2]),
        "bend_centreline_radius_mm": radius,
        "bend_angle_deg": 90,
        "tail_end_xyz_mm": end,
        "straight_horizontal_mm": tangent,
        "straight_tail_mm": tail,
        "arc_mm": math.pi * radius / 2,
        "centreline_length_beyond_face_mm": tangent + math.pi * radius / 2 + tail,
    }


def _offset_angle(run: float, rise: float, radius: float) -> float | None:
    """Return the tangent angle of an offset with two opposing bends."""
    height = abs(rise)
    discriminant = run**2 - height * (4 * radius - height)
    if discriminant < 0:
        return None
    turn = 2 * math.atan(height / (run + math.sqrt(discriminant)))
    if turn >= math.pi / 2 or 2 * radius * math.sin(turn) >= run:
        return None
    return turn


def _closed(
    name: str,
    xi: float,
    xf: float,
    lo: float,
    hi: float,
    r: float,
    tail: float,
    run: float,
    rise: float,
    angle: float,
    phi: float,
) -> tuple[_Path, float]:
    c, k, diagonal = xi + r, lo + r, tail / math.sqrt(2)
    raised = _arc((c, k, rise), r, 135, 270)
    returned = _arc((c, k, 0), r, 180, 315)
    # The two opposite bends connect horizontal tangents. Record actual arc
    # length in the cutting length and carry their 3-D path into fit.
    height = abs(rise)
    angle_deg = math.degrees(angle)
    offset = [
        *_arc((c, lo, height - r), r, 90, 90 - angle_deg, xz=True),
        *_arc((c + run, lo, r), r, -90 - angle_deg, -90, xz=True),
    ]
    sign = math.copysign(1.0, rise)
    offset = [(x, y, sign * z) for x, y, z in offset]
    points = [
        (raised[0][0] + diagonal, raised[0][1] + diagonal, rise),
        *raised,
        *offset[1:],
        *_arc((xf - r, k, 0), r, 270, 360),
        *_arc((xf - r, hi - r, 0), r, 0, 90),
        *_arc((c, hi - r, 0), r, 90, 180),
        *returned,
        (returned[-1][0] + diagonal, returned[-1][1] + diagonal, 0),
    ]
    straight_jog = (run - 2 * r * math.sin(angle)) / math.cos(angle)
    cut = 2 * (xf - xi + hi - lo - 4 * r) + 3 * math.pi * r + 2 * tail
    cut += 2 * r * angle + straight_jog - run
    return _Path(name, phi, points, _sag(r)), cut


def _cross(
    near: float, far: float, mid: float, r: float, tail: float, phi: float
) -> tuple[_Path, float]:
    inside = _arc((near, mid, 0), r, 180, 270)
    outside = _arc((far, mid, 0), r, 270, 405)
    diagonal = tail / math.sqrt(2)
    points = [
        (near - r, mid + tail, 0),
        *inside,
        *outside,
        (outside[-1][0] - diagonal, outside[-1][1] + diagonal, 0),
    ]
    return (
        _Path("C-TX", phi, points, _sag(r)),
        far - near + 1.25 * math.pi * r + 2 * tail,
    )


def exterior_joint_placement(data: Mapping[str, Any]) -> dict[str, Any]:
    """Resolve all local DUCT02 bars and ties with adverse 3-D clearances."""
    w, depth, allocation = (
        float(data["column_width_mm"]),
        float(data["joint_depth_mm"]),
        float(data["axis_tolerance_mm"]) + float(data["diameter_overage_mm"]) / 2,
    )
    radius, axes, levels = (
        float(data["x_hook_radius_mm"]),
        data["beam_axes_mm"],
        data["beam_top_z_mm"],
    )
    xbars = []
    hooks = []
    ybars = []
    through = []
    for face, zx, zy in (
        ("TOP", levels["X"], levels["Y"]),
        ("BOTTOM", depth - levels["X"], depth - levels["Y"]),
    ):
        spec = data["x_hooks"][face]
        for i, y in enumerate(axes["X"], 1):
            path, wire = _hook(
                f"BX-{face}-{i}",
                float(y),
                float(zx),
                float(spec["tip_x_mm"]),
                float(spec["tail_mm"]),
                radius,
                float(data["beam_bar_mm"]["X"]),
                down=face == "TOP",
            )
            xbars.append(path)
            hooks.append(wire)
        for i, x in enumerate(axes["Y"], 1):
            path = _Path(
                f"BY-{face}-{i}",
                float(data["beam_bar_mm"]["Y"]),
                [
                    (float(x), -float(data["y_straight_each_side_mm"]), float(zy)),
                    (float(x), w + float(data["y_straight_each_side_mm"]), float(zy)),
                ],
            )
            ybars.append(path)
            through.append(
                {
                    "bar_id": path.name,
                    "diameter_mm": path.diameter,
                    "points_mm": path.points,
                }
            )
    edge = data["column_bar_edge_mm"]
    one = (edge, w / 2, w - edge)
    columns = [
        _Path(f"C-{i}-{j}", float(data["column_bar_mm"]), [(x, y, 0), (x, y, depth)])
        for i, x in enumerate(one)
        for j, y in enumerate(one)
        if (i, j) != (1, 1)
    ]
    phi = data["column_link_mm"]
    c = data["column_cover_mm"] + phi / 2
    r = data["column_link_radius_mm"]
    off = data["link_group_offset_mm"]
    overlap = data["column_link_overlap_half_mm"]
    tail = data["column_link_tail_mm"]
    run = data["column_link_ramp_run_mm"]
    angle = _offset_angle(run, off, r)
    if angle is None:
        return {"fit_checks": {"closure_has_tangent_bends": False}}
    west, cw = _closed(
        "C-W", c, w / 2 + overlap, c, w - c, r, tail, run, off, angle, phi
    )
    east, ce = _closed(
        "C-E", w / 2 - overlap, w - c, c, w - c, r, tail, run, -off, angle, phi
    )
    cross_y = data["column_cross_tie_axis_y_mm"]
    cross, cx = _cross(edge + 5, w - edge - 5, cross_y, r, tail, phi)
    ties: list[_Path] = []
    marks = {}
    extra_station = max(
        0.0, data["tie_station_tolerance_mm"] - data["axis_tolerance_mm"]
    )
    for item, cut, dz in ((west, cw, -off), (east, ce, off), (cross, cx, 0)):
        zs = [s + dz for s in data["joint_hoop_centres_mm"]]
        ties.extend(
            item.translate(f"{item.name}-{index}", z, extra_station)
            for index, z in enumerate(zs, 1)
        )
        marks[item.name] = {
            "quantity": len(zs),
            "diameter_mm": phi,
            "nominal_cut_length_mm": cut,
            "local_centreline_polyline_mm": item.points,
            "sampled_arc_max_deviation_mm": item.sagitta,
            "stations_mm": zs,
            "bend_centreline_radius_mm": r,
            "hook_tail_mm": tail,
            "closure_plane_offset_mm": -dz,
            "closure_offset_run_mm": run if dz else 0,
            "closure_offset_bends_deg": (
                [math.degrees(angle), -math.degrees(angle)] if dz else []
            ),
            "hook_angles_deg": [135, 135] if dz else [90, 135],
        }
    groups = {
        "opposed_terminations_and_parallel_x_bars": _minimum(
            combinations(xbars, 2), allocation
        ),
        "x_hooks_to_y_through_bars": _minimum(product(xbars, ybars), allocation),
        "x_hooks_to_column_bars": _minimum(product(xbars, columns), allocation),
        "x_hooks_to_ties": _minimum(product(xbars, ties), allocation),
        "y_through_to_ties": _minimum(product(ybars, ties), allocation),
        "y_through_to_column_bars": _minimum(product(ybars, columns), allocation),
        "column_bars_to_ties": _minimum(product(columns, ties), allocation),
        "ties_to_each_other": _minimum(combinations(ties, 2), allocation),
    }
    # The remaining acceptance evidence follows the frozen local physical envelope.
    centre = (w / 2, w / 2, 0.0)
    allpaths = xbars + ybars + columns + ties
    corridor = min(
        math.sqrt(
            min(
                _point_seg_sq(centre, (a[0], a[1], 0), (b[0], b[1], 0))
                for a, b, _ in p.chords
            )
        )
        - p.diameter / 2
        - allocation
        - p.sagitta
        for p in allpaths
    )
    inner = min(
        min(p.bounds[0][0], p.bounds[1][0], w - p.bounds[0][1], w - p.bounds[1][1])
        - p.diameter / 2
        - allocation
        - p.sagitta
        for p in columns + ties
    )
    depthclear = min(
        min(p.bounds[2][0], depth - p.bounds[2][1])
        - p.diameter / 2
        - allocation
        - p.sagitta
        for p in xbars
    )
    outer = min(
        w - p.bounds[0][1] - p.diameter / 2 - allocation - p.sagitta for p in xbars
    )
    colaxes = [p.points[0][:2] for p in columns]
    centres = [
        (x, y)
        for lo, hi in ((c, w / 2 + overlap), (w / 2 - overlap, w - c))
        for x in (lo + r, hi - r)
        for y in (c + r, w - c - r)
    ]
    seat = min(
        r
        - (phi + float(data["column_bar_mm"])) / 2
        - min(math.dist(q, a) for a in colaxes)
        - 2 * allocation
        for q in centres
    )
    seated = {min(colaxes, key=lambda a: math.dist(q, a)) for q in centres}
    expected = {a for a in colaxes if a[1] != w / 2}
    # Aligned top and bottom beam rows give the same minimum projected
    # spacing at each pair of opposed vertical tails.
    x_diameter = data["beam_bar_mm"]["X"]
    tips = data["x_hooks"]
    tailclear = (
        abs(tips["TOP"]["tip_x_mm"] - tips["BOTTOM"]["tip_x_mm"])
        - x_diameter
        - 2 * allocation
    )
    required_tailclear = max(x_diameter, data["aggregate_max_mm"] + 5)
    cross_seat = (
        r
        - (phi + data["column_bar_mm"]) / 2
        - math.hypot(5, cross_y - w / 2)
        - 2 * allocation
    )
    # The internal 90-degree hook encloses the near face bar only in its
    # south-west quadrant. The exterior 135-degree hook encloses the other.
    closure_clear = off - phi - 2 * (allocation + extra_station)
    checks = {k: v["adverse_clearance_mm"] > 0 for k, v in groups.items()}
    checks.update(
        paired_closed_hoop_seats=seat > 0 and seated == expected,
        cross_tie_seats=cross_seat > 0 and cross_y >= w / 2,
        column_and_tie_cover=inner >= float(data["required_column_cover_mm"]),
        anchor_outer_face_cover=outer >= float(data["required_column_cover_mm"]),
        anchor_within_beam_depth=depthclear >= float(data["required_beam_cover_mm"]),
        compaction_corridor=2 * corridor >= float(data["compaction_head_mm"]),
        closure_vertical_separation=closure_clear > 0,
        link_bend_diameter=2 * r - phi >= 4 * phi,
        nominal_tie_levels_in_core=all(
            0 <= p.bounds[2][0] <= p.bounds[2][1] <= depth for p in ties
        ),
        perimeter_bars=(w - 2 * edge) / 2 + 2 * float(data["axis_tolerance_mm"]) <= 300
        and 0.008
        <= 8 * math.pi * float(data["column_bar_mm"]) ** 2 / (4 * w * w)
        <= 0.04,
        opposed_parallel_tail_spacing=tailclear >= required_tailclear,
    )
    return {
        "fit_checks": checks,
        "pair_clearances": groups,
        "compaction_diameter_mm": 2 * corridor,
        "closure_adverse_separation_mm": closure_clear,
        "cross_tie_seat_clearance_mm": cross_seat,
        "column_hoop_seat_clearance_mm": seat,
        "column_and_link_cover_mm": inner,
        "anchor_outer_cover_mm": outer,
        "anchor_top_soffit_clear_mm": depthclear,
        "opposed_parallel_tail_clear_mm": tailclear,
        "required_parallel_tail_clear_mm": required_tailclear,
        "x_hook_paths": hooks,
        "y_through_paths": through,
        "column_axes_xy_mm": colaxes,
        "joint_tie_marks": marks,
        "exterior_cross_tie": {
            "marked_exterior_face": "X+",
            "exterior_hook_deg": 135,
            "inside_hook_deg": 90,
        },
    }
