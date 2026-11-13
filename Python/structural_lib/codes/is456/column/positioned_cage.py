"""Local enclosure and restraint for an explicit rectangular cage."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, pairwise
from math import atan2, cos, hypot, pi, radians, sin

from structural_lib.core.geometry import circle_inside_rounded_rectangle

from .detailing import calculate_tie_spacing
from .four_corner import ColumnCageCheck
from .positioned_biaxial import Point, PositionedColumnBar

_SOURCE = "IS 456:2000 Cl. 26.5.3.2, Fig. 9 and Fig. 10"
_HOOK_SOURCE = "IS 456:2000 Cl. 26.2.2.4(b) and supplied bend schedule"
_CORNERS = (("left", "top"), ("right", "top"), ("right", "bottom"), ("left", "bottom"))
_EPS = 1e-8


@dataclass(frozen=True)
class PositionedTie:
    tie_id: str
    diameter_mm: float
    internal_bend_radius_mm: float
    hook_angle_deg: float
    hook_tail_mm: float


@dataclass(frozen=True)
class PositionedCrossTie(PositionedTie):
    restrained_bar_ids: tuple[str, str]
    station_offset_mm: float
    hook_side: str


@dataclass(frozen=True)
class CrossTieHook:
    centre_mm: Point
    radius_mm: float
    tangent_mm: Point
    bend_end_mm: Point
    tail_end_mm: Point
    sweep_deg: float


@dataclass(frozen=True)
class PositionedTiePath:
    tie_id: str
    restrained_bar_ids: tuple[str, str]
    start_mm: Point
    end_mm: Point
    hooks: tuple[CrossTieHook, CrossTieHook]
    diameter_mm: float
    station_offset_mm: float
    centreline_length_mm: float
    minimum_inner_bar_clearance_mm: float | None


@dataclass(frozen=True)
class PositionedCageResult:
    checks: tuple[ColumnCageCheck, ...]
    cross_ties: tuple[PositionedTiePath, ...]
    unrestrained_ids: tuple[str, ...]
    tie_centreline_width_mm: float
    tie_centreline_depth_mm: float


def _point(bar: PositionedColumnBar) -> Point:
    return bar.x_from_left_mm, bar.y_from_top_mm


def _offset(point: Point, vector: Point, distance: float) -> Point:
    return point[0] + vector[0] * distance, point[1] + vector[1] * distance


def _segment_distance(point: Point, start: Point, end: Point) -> float:
    dx, dy = end[0] - start[0], end[1] - start[1]
    denominator = dx * dx + dy * dy
    along = (
        min(
            1.0,
            max(
                0.0,
                ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / denominator,
            ),
        )
        if denominator
        else 0.0
    )
    return hypot(point[0] - (start[0] + along * dx), point[1] - (start[1] + along * dy))


def _hook(
    centre: Point, side: Point, outward: Point, radius: float, angle: float, tail: float
) -> CrossTieHook:
    tangent = _offset(centre, side, radius)
    radial = (
        side[0] * cos(angle) + outward[0] * sin(angle),
        side[1] * cos(angle) + outward[1] * sin(angle),
    )
    bend_end = _offset(centre, radial, radius)
    tail_axis = (
        -side[0] * sin(angle) + outward[0] * cos(angle),
        -side[1] * sin(angle) + outward[1] * cos(angle),
    )
    return CrossTieHook(
        centre,
        radius,
        tangent,
        bend_end,
        _offset(bend_end, tail_axis, tail),
        angle * 180 / pi,
    )


def _hook_distance(
    point: Point, hook: CrossTieHook, side: Point, outward: Point
) -> float:
    dx, dy = point[0] - hook.centre_mm[0], point[1] - hook.centre_mm[1]
    angle = atan2(dx * outward[0] + dy * outward[1], dx * side[0] + dy * side[1]) % (
        2 * pi
    )
    arc = (
        abs(hypot(dx, dy) - hook.radius_mm)
        if angle <= radians(hook.sweep_deg)
        else min(
            hypot(point[0] - end[0], point[1] - end[1])
            for end in (hook.tangent_mm, hook.bend_end_mm)
        )
    )
    return min(arc, _segment_distance(point, hook.bend_end_mm, hook.tail_end_mm))


def _path_check(
    *,
    b_mm: float,
    D_mm: float,
    cover_mm: float,
    bars: tuple[PositionedColumnBar, ...],
    first: PositionedColumnBar,
    second: PositionedColumnBar,
    tie: PositionedCrossTie,
    horizontal: bool,
) -> tuple[PositionedTiePath, bool, float]:
    # The straight leg passes to the supplied side of both hooked bars.
    coordinate = 0 if horizontal else 1
    ends = sorted((_point(first), _point(second)), key=lambda point: point[coordinate])
    direction = (1.0, 0.0) if horizontal else (0.0, 1.0)
    opposing = (-direction[0], -direction[1])
    sign = 1.0 if tie.hook_side == "positive" else -1.0
    side = (0.0, sign) if horizontal else (sign, 0.0)
    radius = tie.internal_bend_radius_mm + tie.diameter_mm / 2
    angle = radians(tie.hook_angle_deg)
    hooks = (
        _hook(ends[0], side, opposing, radius, angle, tie.hook_tail_mm),
        _hook(ends[1], side, direction, radius, angle, tie.hook_tail_mm),
    )
    start, end = (hook.tangent_mm for hook in hooks)
    margin = cover_mm + tie.diameter_mm / 2
    cover_ok = all(
        margin + radius - _EPS <= x <= b_mm - margin - radius + _EPS
        and margin + radius - _EPS <= y <= D_mm - margin - radius + _EPS
        for x, y in ends
    ) and all(
        margin - _EPS <= x <= b_mm - margin + _EPS
        and margin - _EPS <= y <= D_mm - margin + _EPS
        for x, y in (hook.tail_end_mm for hook in hooks)
    )
    clearances = {}
    for bar in bars:
        point = _point(bar)
        clearances[bar.bar_id] = (
            min(
                _segment_distance(point, start, end),
                _hook_distance(point, hooks[0], side, opposing),
                _hook_distance(point, hooks[1], side, direction),
            )
            - (bar.diameter_mm + tie.diameter_mm) / 2
        )
    inner = [clearances[bar.bar_id] for bar in bars if bar.row == "inner"]
    return (
        PositionedTiePath(
            tie.tie_id,
            tie.restrained_bar_ids,
            start,
            end,
            hooks,
            tie.diameter_mm,
            tie.station_offset_mm,
            ends[1][coordinate]
            - ends[0][coordinate]
            + 2 * (radius * angle + tie.hook_tail_mm),
            min(inner) if inner else None,
        ),
        cover_ok,
        min(clearances.values()),
    )


def check_positioned_cage(
    *,
    b_mm: float,
    D_mm: float,
    bars: tuple[PositionedColumnBar, ...],
    nominal_cover_mm: float,
    required_cover_mm: float,
    aggregate_size_mm: float,
    required_hoop_bend_mm: float,
    required_link_bend_mm: float,
    hoop: PositionedTie,
    hoop_closed: bool,
    pitch_mm: float,
    cross_ties: tuple[PositionedCrossTie, ...],
) -> PositionedCageResult:
    """Check the local closed hoop, aligned open links and inner row."""
    checks: list[ColumnCageCheck] = []

    def record(
        code: str,
        passed: bool,
        actual: float | bool,
        limit: float | bool,
        source: str = _SOURCE,
    ) -> None:
        checks.append(ColumnCageCheck("COLUMN." + code, passed, actual, limit, source))

    outer = [bar for bar in bars if bar.row == "outer"]
    inner = [bar for bar in bars if bar.row == "inner"]
    minimum_dia = min(bar.diameter_mm for bar in bars)
    maximum_outer_dia = max((bar.diameter_mm for bar in outer), default=0)
    minimum_tie = max(6, max(bar.diameter_mm for bar in bars) / 4)
    max_pitch = calculate_tie_spacing(b_mm, D_mm, minimum_dia)
    cover = max(40, required_cover_mm, maximum_outer_dia)
    record(
        "COVER",
        nominal_cover_mm >= cover,
        nominal_cover_mm,
        cover,
        "IS 456:2000 Cl. 26.4",
    )
    record(
        "BAR_DIAMETER", minimum_dia >= 12, minimum_dia, 12, "IS 456:2000 Cl. 26.5.3.1"
    )
    record(
        "TIE_DIAMETER", hoop.diameter_mm >= minimum_tie, hoop.diameter_mm, minimum_tie
    )
    record("TIE_SPACING", pitch_mm <= max_pitch, pitch_mm, max_pitch)
    record("TIE_CLOSED", hoop_closed, hoop_closed, True)

    minimum_clearance = min(
        hypot(
            left.x_from_left_mm - right.x_from_left_mm,
            left.y_from_top_mm - right.y_from_top_mm,
        )
        - (left.diameter_mm + right.diameter_mm) / 2
        for left, right in combinations(bars, 2)
    )
    clear = all(
        hypot(
            left.x_from_left_mm - right.x_from_left_mm,
            left.y_from_top_mm - right.y_from_top_mm,
        )
        - (left.diameter_mm + right.diameter_mm) / 2
        >= max(left.diameter_mm, right.diameter_mm, aggregate_size_mm + 5, 25)
        for left, right in combinations(bars, 2)
    )
    record(
        "CLEAR_SPACING",
        clear,
        minimum_clearance,
        max(25, minimum_dia, aggregate_size_mm + 5),
        "IS 456:2000 Cl. 26.3.2",
    )

    width = b_mm - 2 * nominal_cover_mm - hoop.diameter_mm
    depth = D_mm - 2 * nominal_cover_mm - hoop.diameter_mm
    bend_extent = 2 * hoop.internal_bend_radius_mm + hoop.diameter_mm
    record(
        "TIE_BEND_FIT",
        min(width, depth) >= bend_extent,
        min(width, depth),
        bend_extent,
        _HOOK_SOURCE,
    )
    record(
        "TIE_BEND_RADIUS",
        hoop.internal_bend_radius_mm >= required_hoop_bend_mm,
        hoop.internal_bend_radius_mm,
        required_hoop_bend_mm,
        _HOOK_SOURCE,
    )
    hook_ok = (
        hoop.hook_angle_deg == 135
        and 6 * hoop.diameter_mm <= hoop.hook_tail_mm <= min(width, depth) - bend_extent
    )
    record("TIE_HOOK_FIT", hook_ok, hook_ok, True, _HOOK_SOURCE)
    face = nominal_cover_mm + hoop.diameter_mm
    encloses = all(
        circle_inside_rounded_rectangle(
            bar.x_from_left_mm,
            bar.y_from_top_mm,
            bar.diameter_mm / 2,
            face,
            b_mm - face,
            face,
            D_mm - face,
            hoop.internal_bend_radius_mm,
        )
        for bar in bars
    )
    record("TIE_ENCLOSURE", encloses, encloses, True)

    def clearances(bar: PositionedColumnBar) -> dict[str, float]:
        x, y = _point(bar)
        return {
            key: distance - bar.diameter_mm / 2
            for key, distance in (
                ("left", x),
                ("right", b_mm - x),
                ("top", y),
                ("bottom", D_mm - y),
            )
        }

    by_id = {bar.bar_id: bar for bar in outer}
    faces = {
        bar.bar_id: frozenset(
            key
            for key, clear_mm in clearances(bar).items()
            if -_EPS <= clear_mm - face <= 2 + _EPS
        )
        for bar in outer
    }
    corner_pairs = {frozenset(pair) for pair in _CORNERS}
    all_corners = all(
        sum(value == pair for value in faces.values()) == 1 for pair in corner_pairs
    )
    classified = all(
        len(value) == 1 or value in corner_pairs for value in faces.values()
    )
    record(
        "PERIMETER_RESTRAINT",
        all_corners and classified,
        all_corners and classified,
        True,
    )
    if inner:
        # Require the entire inner bars to sit behind the outer row, and
        # apply the clause's depth requirement conservatively to every face.
        inner_limit = max(
            3 * max(bar.diameter_mm for bar in inner), face + maximum_outer_dia + 2
        )
        inner_clear = min(min(clearances(bar).values()) for bar in inner)
        record(
            "INNER_ROW_RESTRAINT", inner_clear >= inner_limit, inner_clear, inner_limit
        )

    face_spans: dict[str, float] = {}
    for name in ("left", "right", "top", "bottom"):
        along = 1 if name in ("left", "right") else 0
        coordinates = sorted(
            _point(bar)[along] for bar in outer if name in faces[bar.bar_id]
        )
        if len(coordinates) >= 2:
            maximum_gap = max(end - start for start, end in pairwise(coordinates))
            face_spans[name] = coordinates[-1] - coordinates[0]
            record(
                "PERIPHERAL_SPACING",
                maximum_gap <= 300,
                maximum_gap,
                300,
                "IS 456:2000 Cl. 26.5.3.1",
            )

    if not all_corners or not classified:
        return PositionedCageResult(tuple(checks), (), (), width, depth)

    unrestrained = {bar_id for bar_id, sides in faces.items() if len(sides) == 1}
    paths = []
    ids = {hoop.tie_id}
    for tie in cross_ties:
        left, right = tie.restrained_bar_ids
        paired = (
            left != right and {left, right} <= unrestrained and tie.tie_id not in ids
        )
        sides = faces[left] | faces[right] if paired else frozenset()
        horizontal = sides == frozenset(("left", "right"))
        opposite = horizontal or sides == frozenset(("top", "bottom"))
        aligned = (
            paired
            and opposite
            and abs(
                _point(by_id[left])[1 if horizontal else 0]
                - _point(by_id[right])[1 if horizontal else 0]
            )
            <= _EPS
        )
        record("CROSS_TIE_PAIR", aligned, aligned, True)
        if not aligned:
            continue
        first, second = by_id[left], by_id[right]
        ids.add(tie.tie_id)
        unrestrained.difference_update((left, right))
        span = max(face_spans[side] for side in sides)
        span_limit = 48 * min(hoop.diameter_mm, tie.diameter_mm)
        record("CROSS_TIE_RESTRAINT_SPAN", span <= span_limit, span, span_limit)
        record(
            "CROSS_TIE_DIAMETER",
            tie.diameter_mm >= minimum_tie,
            tie.diameter_mm,
            minimum_tie,
        )
        minimum_bend = max(
            required_link_bend_mm, first.diameter_mm / 2, second.diameter_mm / 2
        )
        max_bend = min(first.diameter_mm, second.diameter_mm) / 2 + 2
        bend_ok = minimum_bend <= tie.internal_bend_radius_mm <= max_bend
        record("CROSS_TIE_BEND", bend_ok, bend_ok, True, _HOOK_SOURCE)
        hook_ok = tie.hook_angle_deg == 135 and tie.hook_tail_mm >= 6 * tie.diameter_mm
        record("CROSS_TIE_HOOK", hook_ok, hook_ok, True, _HOOK_SOURCE)
        if not bend_ok or not hook_ok:
            continue
        path, cover_ok, clearance = _path_check(
            b_mm=b_mm,
            D_mm=D_mm,
            cover_mm=nominal_cover_mm,
            bars=bars,
            first=first,
            second=second,
            tie=tie,
            horizontal=horizontal,
        )
        record("CROSS_TIE_COVER", cover_ok, cover_ok, True, _HOOK_SOURCE)
        record(
            "CROSS_TIE_BAR_CLEARANCE", clearance >= -_EPS, clearance, 0, _HOOK_SOURCE
        )
        paths.append(path)

    if paths:
        # Every hoop and complete open-link path lies in one transverse
        # plane. Separation of those planes by the sum of the bar radii
        # bounds the swept steel tubes apart even where their projections cross.
        levels = [
            (0.0, hoop.diameter_mm),
            *(sorted((path.station_offset_mm, path.diameter_mm) for path in paths)),
            (pitch_mm, hoop.diameter_mm),
        ]
        gap = min(
            end - start - (first_dia + second_dia) / 2
            for (start, first_dia), (end, second_dia) in pairwise(levels)
        )
        record(
            "CROSS_TIE_LEVELS",
            gap >= -_EPS,
            gap,
            0,
            "Physical separation within the supplied tie pitch",
        )
    return PositionedCageResult(
        tuple(checks), tuple(paths), tuple(sorted(unrestrained)), width, depth
    )
