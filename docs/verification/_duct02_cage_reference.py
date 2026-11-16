"""Independent centreline geometry and adverse DUCT02 construction clearance."""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import combinations, pairwise, product


def dot(left, right):
    return sum(a * b for a, b in zip(left, right, strict=True))


def minus(left, right):
    return tuple(a - b for a, b in zip(left, right, strict=True))


def box(points):
    columns = tuple(zip(*points, strict=True))
    return tuple((min(column), max(column)) for column in columns)


def box_distance_sq(left, right):
    return sum(
        max(lo_a - hi_b, lo_b - hi_a, 0.0) ** 2
        for (lo_a, hi_a), (lo_b, hi_b) in zip(left, right, strict=True)
    )


def point_segment_distance_sq(point, start, finish):
    edge, offset = minus(finish, start), minus(point, start)
    length_sq = dot(edge, edge)
    t = max(0.0, min(1.0, dot(offset, edge) / length_sq)) if length_sq else 0.0
    return sum((a - t * b) ** 2 for a, b in zip(offset, edge, strict=True))


def segment_distance_sq(a, b, c, d):
    """Bounded segment distance, including an interior-interior crossing."""
    answer = min(
        point_segment_distance_sq(a, c, d),
        point_segment_distance_sq(b, c, d),
        point_segment_distance_sq(c, a, b),
        point_segment_distance_sq(d, a, b),
    )
    u, v, w = minus(b, a), minus(d, c), minus(a, c)
    uu, uv, vv, uw, vw = dot(u, u), dot(u, v), dot(v, v), dot(u, w), dot(v, w)
    det = uu * vv - uv**2
    if det > 0:
        s, t = (uv * vw - vv * uw) / det, (uu * vw - uv * uw) / det
        if 0 <= s <= 1 and 0 <= t <= 1:
            answer = min(
                answer,
                sum((z + s * x - t * y) ** 2 for x, y, z in zip(u, v, w, strict=True)),
            )
    return answer


@dataclass
class Path:
    """Nominal path sampled with a bounded arc-to-chord deviation."""

    name: str
    diameter: float
    points: list[tuple[float, float, float]]
    sagitta_mm: float = 0.0

    def __post_init__(self):
        self.bounds = box(self.points)
        self.chords = [
            (start, end, box((start, end)))
            for start, end in pairwise(self.points)
            if start != end
        ]

    def translated(self, name, z):
        return Path(
            name,
            self.diameter,
            [(a, b, c + z) for a, b, c in self.points],
            self.sagitta_mm,
        )


def arc(centre, radius, start_deg, end_deg, plane="XY"):
    """Sample a circle uniformly with at most 7.5° between chords."""
    count = math.ceil(abs(end_deg - start_deg) / 7.5)
    result = []
    for i in range(count + 1):
        angle = math.radians(start_deg + (end_deg - start_deg) * i / count)
        x = centre[0] + radius * math.cos(angle)
        transverse = radius * math.sin(angle)
        if plane == "XY":
            result.append((x, centre[1] + transverse, centre[2]))
        else:
            result.append((x, centre[1], centre[2] + transverse))
    return result


def sagitta(radius):
    return radius * (1 - math.cos(math.radians(3.75)))


def _path_pair_minimum(pairs, allocation_mm):
    # Bounding boxes are lower bounds on chord distance and can prune pairs.
    best_clear, controlling = math.inf, ()
    for left, right in pairs:
        deduction = (
            (left.diameter + right.diameter) / 2
            + 2 * allocation_mm
            + left.sagitta_mm
            + right.sagitta_mm
        )
        if (
            math.sqrt(box_distance_sq(left.bounds, right.bounds)) - deduction
            >= best_clear
        ):
            continue
        pair_best_sq = math.inf
        for a, b, left_box in left.chords:
            for c, d, right_box in right.chords:
                if box_distance_sq(left_box, right_box) >= pair_best_sq:
                    continue
                pair_best_sq = min(pair_best_sq, segment_distance_sq(a, b, c, d))
        clear = math.sqrt(pair_best_sq) - deduction
        if clear < best_clear:
            best_clear, controlling = clear, (left.name, right.name)
    return {"adverse_clearance_mm": best_clear, "parts": controlling}


def _beam_hook(mark, y, z, tip_x, tail, radius, phi, down):
    tangent_x = tip_x - radius
    delta = 1 if down else -1
    centre = (tangent_x, y, z + delta * radius)
    bend = arc(centre, radius, -90 * delta, 0, "XZ")
    terminal = (tip_x, y, centre[2] + delta * tail)
    points = [(0.0, y, z), *bend, terminal]
    path = Path(mark, phi, points, sagitta(radius))
    schedule = {
        "bar_id": mark,
        "diameter_mm": phi,
        "start_at_inner_face_xyz_mm": points[0],
        "bend_start_xyz_mm": (tangent_x, y, z),
        "bend_centre_xyz_mm": centre,
        "bend_end_xyz_mm": (tip_x, y, centre[2]),
        "bend_centreline_radius_mm": radius,
        "bend_angle_deg": 90,
        "tail_end_xyz_mm": terminal,
        "straight_horizontal_mm": tangent_x,
        "straight_tail_mm": tail,
        "arc_mm": math.pi * radius / 2,
        "centreline_length_beyond_face_mm": tangent_x + math.pi * radius / 2 + tail,
    }
    return path, schedule


def _closure_offset(x, y, run, rise, radius):
    """A tangent S offset using two equal-radius bends and a straight web."""
    direction = math.copysign(1, rise)
    height = abs(rise)
    # Solve the horizontal and vertical projections for tan(theta / 2).
    root = math.sqrt(run**2 - (4 * radius - height) * height)
    theta = 2 * math.atan(height / (run + root))
    degrees = math.degrees(theta)
    straight = (run - 2 * radius * math.sin(theta)) / math.cos(theta)
    assert straight > 0
    points = [
        *arc((x, y, height - radius), radius, 90, 90 - degrees, "XZ"),
        *arc((x + run, y, radius), radius, -90 - degrees, -90, "XZ"),
    ]
    return (
        [(a, b, direction * z) for a, b, z in points],
        2 * radius * theta + straight,
        degrees,
    )


def _closed_hoop(name, xi, xf, lo, hi, radius, tail, run, rise, phi):
    """Three 90° body bends and two offset 135° returns at one corner."""
    c = xi + radius
    k = lo + radius
    raised = arc((c, k, rise), radius, 135, 270)
    returned = arc((c, k, 0), radius, 180, 315)
    diagonal = tail / math.sqrt(2)
    offset_points, offset_length, offset_angle = _closure_offset(
        c, lo, run, rise, radius
    )
    points = [
        (raised[0][0] + diagonal, raised[0][1] + diagonal, rise),
        *raised,
        *offset_points[1:],
        *arc((xf - radius, k, 0), radius, 270, 360),
        *arc((xf - radius, hi - radius, 0), radius, 0, 90),
        *arc((c, hi - radius, 0), radius, 90, 180),
        *returned,
        (returned[-1][0] + diagonal, returned[-1][1] + diagonal, 0),
    ]
    length = (
        2 * (xf - xi + hi - lo - 4 * radius)
        + 3 * math.pi * radius
        + 2 * tail
        + offset_length
        - run
    )
    return Path(name, phi, points, sagitta(radius)), length, offset_angle


def _cross_tie(near, far, mid, radius, tail, phi):
    """90° on the inside and 135° at the exterior +X face."""
    inside = arc((near, mid, 0), radius, 180, 270)
    outside = arc((far, mid, 0), radius, 270, 405)
    diagonal = tail / math.sqrt(2)
    vertices = [
        (near - radius, mid + tail, 0),
        *inside,
        *outside,
        (outside[-1][0] - diagonal, outside[-1][1] + diagonal, 0),
    ]
    length = far - near + 1.25 * math.pi * radius + 2 * tail
    return Path("C-TX", phi, vertices, sagitta(radius)), length


def _column_steel(request):
    width = request["column_width_mm"]
    depth = request["joint_depth_mm"]
    edge = request["column_bar_edge_mm"]
    axes = (edge, width / 2, width - edge)
    return [
        Path(f"C-{ix}-{iy}", request["column_bar_mm"], [(x, y, 0), (x, y, depth)])
        for ix, x in enumerate(axes)
        for iy, y in enumerate(axes)
        if (ix, iy) != (1, 1)
    ]


def _tie_groups(request):
    w = request["column_width_mm"]
    phi = request["column_link_mm"]
    c = request["column_cover_mm"] + phi / 2
    r = request["column_link_radius_mm"]
    tail = request["column_link_tail_mm"]
    offset = request["link_group_offset_mm"]
    ramp = request["column_link_ramp_run_mm"]
    overlap = request["column_link_overlap_half_mm"]
    axis = request["column_bar_edge_mm"] + 5
    west, cut_w, angle_w = _closed_hoop(
        "C-W", c, w / 2 + overlap, c, w - c, r, tail, ramp, offset, phi
    )
    east, cut_e, angle_e = _closed_hoop(
        "C-E", w / 2 - overlap, w - c, c, w - c, r, tail, ramp, -offset, phi
    )
    cross, cut_x = _cross_tie(
        axis, w - axis, request["column_cross_tie_axis_y_mm"], r, tail, phi
    )
    all_ties, marks = [], {}
    for item, cut, dz, angle in (
        (west, cut_w, -offset, angle_w),
        (east, cut_e, offset, angle_e),
        (cross, cut_x, 0, 0),
    ):
        stations = [group + dz for group in request["joint_hoop_centres_mm"]]
        all_ties.extend(
            item.translated(f"{item.name}-{index + 1}", z)
            for index, z in enumerate(stations)
        )
        marks[item.name] = {
            "quantity": len(stations),
            "diameter_mm": phi,
            "nominal_cut_length_mm": cut,
            "local_centreline_polyline_mm": item.points,
            "sampled_arc_max_deviation_mm": item.sagitta_mm,
            "stations_mm": stations,
            "bend_centreline_radius_mm": r,
            "hook_tail_mm": tail,
            "closure_plane_offset_mm": -dz,
            "closure_offset_run_mm": ramp if dz else 0,
            "closure_offset_bends_deg": [angle, -angle] if dz else [],
            "hook_angles_deg": [135, 135] if item.name != "C-TX" else [90, 135],
        }
    return all_ties, marks


def geometry(request):
    """Prove local 3D fit of the supplied X hooks, Y bars and exterior cage."""
    width = request["column_width_mm"]
    depth = request["joint_depth_mm"]
    radius = request["x_hook_radius_mm"]
    allocation = request["axis_tolerance_mm"] + request["diameter_overage_mm"] / 2
    x_bars, y_bars = [], []
    hooks, through = [], []
    for face, z_x, z_y in (
        ("TOP", request["beam_top_z_mm"]["X"], request["beam_top_z_mm"]["Y"]),
        (
            "BOTTOM",
            depth - request["beam_top_z_mm"]["X"],
            depth - request["beam_top_z_mm"]["Y"],
        ),
    ):
        x_hook = request["x_hooks"][face]
        for index, y in enumerate(request["beam_axes_mm"]["X"], start=1):
            bar, exact = _beam_hook(
                f"BX-{face}-{index}",
                y,
                z_x,
                x_hook["tip_x_mm"],
                x_hook["tail_mm"],
                radius,
                request["beam_bar_mm"]["X"],
                face == "TOP",
            )
            x_bars.append(bar)
            hooks.append(exact)
        for index, x in enumerate(request["beam_axes_mm"]["Y"], start=1):
            interval = (
                -request["y_straight_each_side_mm"],
                width + request["y_straight_each_side_mm"],
            )
            item = Path(
                f"BY-{face}-{index}",
                request["beam_bar_mm"]["Y"],
                [(x, y, z_y) for y in interval],
            )
            y_bars.append(item)
            through.append(
                {
                    "bar_id": item.name,
                    "diameter_mm": item.diameter,
                    "points_mm": item.points,
                }
            )

    column = _column_steel(request)
    ties, marks = _tie_groups(request)
    opposed_tail_clear = min(
        math.dist(top["tail_end_xyz_mm"][:2], bottom["tail_end_xyz_mm"][:2])
        - request["beam_bar_mm"]["X"]
        - 2 * allocation
        for top, bottom in product(hooks[: len(x_bars) // 2], hooks[len(x_bars) // 2 :])
    )
    required_parallel_clear = max(
        request["beam_bar_mm"]["X"], request["aggregate_max_mm"] + 5
    )
    clear = {
        "opposed_terminations_and_parallel_x_bars": _path_pair_minimum(
            combinations(x_bars, 2), allocation
        ),
        "x_hooks_to_y_through_bars": _path_pair_minimum(
            product(x_bars, y_bars), allocation
        ),
        "x_hooks_to_column_bars": _path_pair_minimum(
            product(x_bars, column), allocation
        ),
        "x_hooks_to_ties": _path_pair_minimum(product(x_bars, ties), allocation),
        "y_through_to_ties": _path_pair_minimum(product(y_bars, ties), allocation),
        "y_through_to_column_bars": _path_pair_minimum(
            product(y_bars, column), allocation
        ),
        "column_bars_to_ties": _path_pair_minimum(product(column, ties), allocation),
        "ties_to_each_other": _path_pair_minimum(combinations(ties, 2), allocation),
    }
    all_paths = x_bars + y_bars + column + ties
    centre = (width / 2, width / 2, 0)
    corridor_radius = min(
        math.sqrt(
            min(
                point_segment_distance_sq(centre, (*start[:2], 0), (*end[:2], 0))
                for start, end, _ in item.chords
            )
        )
        - item.diameter / 2
        - allocation
        - item.sagitta_mm
        for item in all_paths
    )
    inner_cover = min(
        min(
            item.bounds[0][0],
            item.bounds[1][0],
            width - item.bounds[0][1],
            width - item.bounds[1][1],
        )
        - item.diameter / 2
        - allocation
        - item.sagitta_mm
        for item in column + ties
    )
    hook_clear_top_or_soffit = min(
        min(item.bounds[2][0], depth - item.bounds[2][1])
        - item.diameter / 2
        - allocation
        - item.sagitta_mm
        for item in x_bars
    )
    hook_cover_at_outer_face = min(
        width - item.bounds[0][1] - item.diameter / 2 - allocation - item.sagitta_mm
        for item in x_bars
    )
    r = request["column_link_radius_mm"]
    phi = request["column_link_mm"]
    rise = request["link_group_offset_mm"]
    position_tolerance = request["axis_tolerance_mm"]
    col_axes = [item.points[0][:2] for item in column]
    c = request["column_cover_mm"] + phi / 2
    mid = width / 2
    overlap = request["column_link_overlap_half_mm"]
    centres = [
        (x, y)
        for lo, hi in ((c, mid + overlap), (mid - overlap, width - c))
        for x in (lo + r, hi - r)
        for y in (c + r, width - c - r)
    ]
    clearance_at_seats = min(
        r
        - (phi + request["column_bar_mm"]) / 2
        - min(math.dist(centre, point) for point in col_axes)
        - 2 * allocation
        for centre in centres
    )
    seat_bars = {
        min(col_axes, key=lambda point: math.dist(centre, point)) for centre in centres
    }
    expected_hoop_seats = {point for point in col_axes if point[1] != mid}
    fit_checks = {
        name: item["adverse_clearance_mm"] > 0 for name, item in clear.items()
    }
    fit_checks.update(
        opposed_parallel_tail_spacing=opposed_tail_clear >= required_parallel_clear,
        paired_closed_hoop_seats=(
            clearance_at_seats > 0 and seat_bars == expected_hoop_seats
        ),
        column_and_tie_cover=inner_cover >= request["required_column_cover_mm"],
        anchor_outer_face_cover=hook_cover_at_outer_face
        >= request["required_column_cover_mm"],
        anchor_within_beam_depth=hook_clear_top_or_soffit
        >= request["required_beam_cover_mm"],
        compaction_corridor=2 * corridor_radius >= request["compaction_head_mm"],
        closure_vertical_separation=rise - phi - 2 * allocation > 0,
        link_bend_diameter=2 * r - phi >= 4 * phi,
        nominal_tie_levels_in_core=all(
            0 <= item.bounds[2][0] <= item.bounds[2][1] <= depth for item in ties
        ),
        perimeter_bars=(
            (width - 2 * request["column_bar_edge_mm"]) / 2 + 2 * position_tolerance
            <= 300
            and 0.008
            <= 8 * math.pi * request["column_bar_mm"] ** 2 / (4 * width**2)
            <= 0.04
        ),
    )
    return {
        "fit_checks": fit_checks,
        "pair_clearances": clear,
        "compaction_diameter_mm": 2 * corridor_radius,
        "opposed_parallel_tail_clear_mm": opposed_tail_clear,
        "required_parallel_tail_clear_mm": required_parallel_clear,
        "closure_adverse_separation_mm": rise - phi - 2 * allocation,
        "column_hoop_seat_clearance_mm": clearance_at_seats,
        "column_and_link_cover_mm": inner_cover,
        "anchor_outer_cover_mm": hook_cover_at_outer_face,
        "anchor_top_soffit_clear_mm": hook_clear_top_or_soffit,
        "x_hook_paths": hooks,
        "y_through_paths": through,
        "column_axes_xy_mm": col_axes,
        "joint_tie_marks": marks,
        "exterior_cross_tie": {
            "marked_exterior_face": "X+",
            "exterior_hook_deg": 135,
            "inside_hook_deg": 90,
        },
    }
