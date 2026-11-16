"""Physical reinforcement geometry for the bounded BEAM05 haunch profile.

This module deliberately owns geometry only.  Strength, development, schedules
and transport remain consumers of its resolved paths.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import pairwise
from typing import Any, Literal

from pydantic import Field, field_validator, model_validator

from structural_lib.beam.bar_paths import (
    BarPathOutput,
    BarPathRequest,
    BarPathRole,
    BarPathSeed,
    BendKind,
    MemberLocalCoordinateSystem,
    PathNode,
    PathPoint,
    PathSegmentKind,
    ResolvedPathSegment,
    resolve_bar_paths,
)
from structural_lib.beam.semantics import OperationResult
from structural_lib.codes.is456.beam.detailing import ordinary_link_anchorage_limits
from structural_lib.core.result_contract import StructuralIssueV1
from structural_lib.services.contracts.beam_continuous import (
    BeamContinuousCheckRequestV1,
    Identifier,
    Reference,
)
from structural_lib.services.contracts.common import StrictPublicModel


class BeamHaunchOutlinePointV1(StrictPublicModel):
    station_mm: float = Field(ge=-1500, le=30000)
    depth_mm: float = Field(gt=0, le=2000)


class BeamHaunchBottomBarNodeV1(StrictPublicModel):
    node_id: Identifier
    station_mm: float = Field(ge=-1500, le=30000)
    y_mm: float = Field(gt=0, le=2000)
    radius_mm: float | None = Field(default=None, gt=0, le=1000)


class BeamHaunchLinkV1(StrictPublicModel):
    station_mm: float = Field(ge=-1500, le=30000)
    bottom_axis_mm: float = Field(gt=0, le=2000)
    bar_mark: Identifier
    purpose: Literal["shear", "bend"]


class BeamHaunchBendRestraintV1(StrictPublicModel):
    node_id: Identifier
    link_stations_mm: tuple[float, ...] = Field(max_length=2)

    @field_validator("link_stations_mm", mode="before")
    @classmethod
    def as_tuple(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value


class BeamHaunchDetailV1(StrictPublicModel):
    source_reference: Reference
    outline: tuple[BeamHaunchOutlinePointV1, ...] = Field(min_length=2, max_length=30)
    bottom_bar_path: tuple[BeamHaunchBottomBarNodeV1, ...] = Field(
        min_length=2, max_length=30
    )
    links: tuple[BeamHaunchLinkV1, ...] = Field(min_length=1, max_length=300)
    bend_restraint: tuple[BeamHaunchBendRestraintV1, ...] | None = None
    minimum_cover_mm: float = Field(gt=0, le=100)
    maximum_seat_gap_mm: float = Field(ge=0, le=2)

    @field_validator(
        "outline", "bottom_bar_path", "links", "bend_restraint", mode="before"
    )
    @classmethod
    def tuples(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value

    @model_validator(mode="after")
    def ordered(self) -> BeamHaunchDetailV1:
        if any(
            b.station_mm <= a.station_mm
            for a, b in zip(self.outline, self.outline[1:], strict=False)
        ):
            raise ValueError("Haunch outline stations must be strictly increasing.")
        if any(
            b.station_mm <= a.station_mm
            for a, b in zip(
                self.bottom_bar_path, self.bottom_bar_path[1:], strict=False
            )
        ):
            raise ValueError("Bottom-bar path stations must be strictly increasing.")
        if len({item.station_mm for item in self.links}) != len(self.links):
            raise ValueError("Each physical link station must be unique.")
        return self


@dataclass(frozen=True)
class HaunchGeometry:
    paths: OperationResult
    outline: tuple[BeamHaunchOutlinePointV1, ...]
    bottom_path: tuple[ResolvedPathSegment, ...]
    bottom_segments: list[dict[str, Any]]
    link_checks: list[dict[str, Any]]
    minimum_link_cover_mm: float
    bottom_bar_soffit_cover_bound_mm: float
    minimum_axial_opening_mm: float

    def depth_at(self, x: float) -> float:
        return _linear_value(self.outline, x, "depth_mm")

    def bottom_axis_at(self, x: float) -> float:
        return _bar_axis_at(self.bottom_path, x)

    def slope_at(self, x: float, side: str = "CONTINUOUS") -> float:
        points = self.outline
        if side == "LEFT":
            x -= 1e-9
        elif side == "RIGHT":
            x += 1e-9
        for left, right in zip(points, points[1:], strict=False):
            if left.station_mm <= x <= right.station_mm:
                return (right.depth_mm - left.depth_mm) / (
                    right.station_mm - left.station_mm
                )
        raise ValueError("Station lies outside the haunch outline.")


def _linear_value(
    points: tuple[BeamHaunchOutlinePointV1, ...], x: float, key: str
) -> float:
    return _linear_pairs(
        [(item.station_mm, float(getattr(item, key))) for item in points], x
    )


def _linear_pairs(points: list[tuple[float, float]], x: float) -> float:
    for (x1, y1), (x2, y2) in zip(points, points[1:], strict=False):
        if x1 <= x <= x2:
            return y1 + (x - x1) * (y2 - y1) / (x2 - x1)
    raise ValueError("Station lies outside the declared geometry.")


def _issue(code: str, path: str, message: str) -> StructuralIssueV1:
    return StructuralIssueV1(code, path, message)


def _path_point(segment: ResolvedPathSegment, x: float) -> float:
    start = segment.start
    end = segment.end
    if segment.kind is PathSegmentKind.BEND_ARC:
        centre, radius = segment.bend_centre, segment.bend_radius_mm
        assert centre is not None and radius is not None
        dy = math.sqrt(max(0, radius**2 - (x - centre.station_x_mm) ** 2))
        return centre.section_y_from_top_mm + math.copysign(
            dy, start.section_y_from_top_mm - centre.section_y_from_top_mm
        )
    ratio = (x - start.station_x_mm) / (end.station_x_mm - start.station_x_mm)
    return start.section_y_from_top_mm + ratio * (
        end.section_y_from_top_mm - start.section_y_from_top_mm
    )


def _bar_axis_at(path: tuple[ResolvedPathSegment, ...], x: float) -> float:
    for segment in path:
        if segment.start.station_x_mm - 1e-9 <= x <= segment.end.station_x_mm + 1e-9:
            return _path_point(segment, x)
    raise ValueError("Station lies outside the resolved bottom bar.")


def _point_segment_distance(
    point: tuple[float, float],
    a: tuple[float, float],
    b: tuple[float, float],
) -> float:
    dx, dy = b[0] - a[0], b[1] - a[1]
    projection = ((point[0] - a[0]) * dx + (point[1] - a[1]) * dy) / (dx * dx + dy * dy)
    t = min(1.0, max(0.0, projection))
    return math.hypot(point[0] - a[0] - t * dx, point[1] - a[1] - t * dy)


def _link_soffit_cover(
    x: float,
    other: float,
    top: float,
    bottom: float,
    outline: tuple[BeamHaunchOutlinePointV1, ...],
    steel_radius: float,
) -> float:
    """Bound the actual sweep of a link by the rectangle in elevation."""
    soffit = [(point.station_mm, point.depth_mm) for point in outline]
    local_depths = [_linear_pairs(soffit, end) for end in (x, other)]
    local_depths.extend(y for station, y in soffit if x < station < other)
    if min(local_depths) <= bottom:
        return -steel_radius
    projection = [(x, top), (x, bottom), (other, bottom), (other, top), (x, top)]
    return (
        min(
            min(
                _point_segment_distance(p, a, b),
                _point_segment_distance(q, a, b),
                _point_segment_distance(a, p, q),
                _point_segment_distance(b, p, q),
            )
            for a, b in pairwise(projection)
            for p, q in pairwise(soffit)
        )
        - steel_radius
    )


def _bar_maximum_slope(path: tuple[ResolvedPathSegment, ...]) -> float:
    slopes: list[float] = []
    for segment in path:
        if segment.kind is PathSegmentKind.BEND_ARC:
            centre = segment.bend_centre
            assert centre is not None
            slopes.extend(
                abs(
                    (point.station_x_mm - centre.station_x_mm)
                    / (point.section_y_from_top_mm - centre.section_y_from_top_mm)
                )
                for point in (segment.start, segment.end)
            )
        else:
            slopes.append(
                abs(
                    (
                        segment.end.section_y_from_top_mm
                        - segment.start.section_y_from_top_mm
                    )
                    / (segment.end.station_x_mm - segment.start.station_x_mm)
                )
            )
    return max(slopes)


def resolve_haunch_geometry(
    member: BeamContinuousCheckRequestV1,
    haunch: BeamHaunchDetailV1,
    *,
    first_station_mm: float,
    last_station_mm: float,
    internal_bend_radius_mm: float,
    hook_vertex_leg_mm: float,
    hook_plane_offset_mm: float,
    source_hash: str,
    stock_length_mm: float,
) -> tuple[HaunchGeometry | None, tuple[StructuralIssueV1, ...]]:
    """Resolve rounded bottom bars and every actual seven-node web link."""
    issues: list[StructuralIssueV1] = []
    outline, nodes, links = haunch.outline, haunch.bottom_bar_path, haunch.links
    left, _, right = member.supports
    extent = member.straight_bars
    if extent is None or (
        outline[0].station_mm != left.left_face_mm
        or outline[-1].station_mm != right.right_face_mm
        or not first_station_mm
        <= left.right_face_mm
        < right.left_face_mm
        <= last_station_mm
        or len(nodes) < 3
        or nodes[0].station_mm != extent.start_mm
        or nodes[-1].station_mm != extent.end_mm
        or any(node.radius_mm is None for node in nodes[1:-1])
    ):
        return None, (
            _issue(
                "BEAM.HAUNCH_BASIS_HELD",
                "haunch",
                "Bind the full concrete outline and rounded bar path to the declared member and link interval.",
            ),
        )

    diameter = member.link_diameter_mm
    link_radius = diameter / 2
    inset = member.clear_cover_mm + link_radius
    top_axis = inset
    radius = internal_bend_radius_mm + link_radius
    bottom_bars = [bar for bar in member.bars if bar.face == "bottom"]
    top_bars = [bar for bar in member.bars if bar.face == "top"]
    if len(bottom_bars) != 2 or len(top_bars) != 2:
        return None, (
            _issue(
                "BEAM.HAUNCH_BASIS_HELD",
                "member.bars",
                "The bounded cage requires one bar at each of four corners.",
            ),
        )
    bottom_r = bottom_bars[0].diameter_mm / 2
    if any(
        node.radius_mm is not None and node.radius_mm <= bottom_r
        for node in nodes[1:-1]
    ):
        return None, (
            _issue(
                "BEAM.HAUNCH_BEND_RESTRAINT_FAIL",
                "haunch.bottom_bar_path",
                "The rounded bottom bar needs a positive internal bend radius.",
            ),
        )
    if (
        nodes[0].y_mm != nodes[1].y_mm
        or nodes[-1].y_mm != nodes[-2].y_mm
        or any(
            bar.y_from_top_mm != nodes[0].y_mm or bar.y_from_top_mm != nodes[-1].y_mm
            for bar in bottom_bars
        )
    ):
        return None, (
            _issue(
                "BEAM.HAUNCH_BASIS_HELD",
                "haunch.bottom_bar_path",
                "Bind both end bars and their actual straight support projections.",
            ),
        )

    regular = [link.station_mm for link in links if link.purpose == "shear"]
    if (
        len(regular) < 2
        or regular[0] != first_station_mm
        or regular[-1] != last_station_mm
        or any(
            not math.isclose(b - a, member.link_spacing_mm, rel_tol=0, abs_tol=1e-8)
            for a, b in pairwise(regular)
        )
    ):
        return None, (
            _issue(
                "BEAM.HAUNCH_LINK_COVERAGE_FAIL",
                "haunch.links",
                "Resolve the full regular shear grid independently of the supplementary links.",
            ),
        )

    gap = min(b.station_mm - a.station_mm for a, b in pairwise(links))
    opening = gap - hook_plane_offset_mm - diameter
    minimum_tail, minimum_radius = ordinary_link_anchorage_limits(diameter, 90)
    if (
        min(link.station_mm for link in links) - link_radius
        < left.left_face_mm + haunch.minimum_cover_mm
        or max(link.station_mm for link in links) + hook_plane_offset_mm + link_radius
        > right.right_face_mm - haunch.minimum_cover_mm
        or opening < member.aggregate_size_mm + 5
        or hook_plane_offset_mm < diameter
        or hook_vertex_leg_mm - radius < minimum_tail
        or internal_bend_radius_mm < minimum_radius
        or any(link.bottom_axis_mm <= top_axis + 2 * radius for link in links)
    ):
        return None, (
            _issue(
                "BEAM.HAUNCH_LINK_FIT_FAIL",
                "haunch.links",
                "Check hook anchorage, member end cover, plate clearance and the axial opening of the link grid.",
            ),
        )

    seeds_list: list[BarPathSeed] = []
    for bar in member.bars:
        is_bottom = bar.face == "bottom"
        if is_bottom:
            bar_nodes = tuple(
                PathNode(
                    node.node_id,
                    PathPoint(node.station_mm, bar.x_from_left_mm, node.y_mm),
                    node.radius_mm,
                    BendKind.TRANSITION if node.radius_mm else None,
                )
                for node in nodes
            )
        else:
            bar_nodes = tuple(
                PathNode(
                    name, PathPoint(station, bar.x_from_left_mm, bar.y_from_top_mm)
                )
                for name, station in (
                    ("start", extent.start_mm),
                    ("end", extent.end_mm),
                )
            )
        seeds_list.append(
            BarPathSeed(
                bar.bar_id,
                f"{member.member_id}-{bar.face}-D{bar.diameter_mm:g}",
                (
                    BarPathRole.BOTTOM_LONGITUDINAL
                    if is_bottom
                    else BarPathRole.TOP_LONGITUDINAL
                ),
                1,
                bar.diameter_mm,
                member.fy_nmm2,
                bar_nodes,
            )
        )
    used = {bar.bar_id for bar in member.bars}
    for index, link in enumerate(links, 1):
        x1, x2, y2 = inset, member.width_mm - inset, link.bottom_axis_mm
        vertices = (
            (0.0, x1 + hook_vertex_leg_mm, top_axis),
            (0.0, x1, top_axis),
            (0.0, x1, y2),
            (hook_plane_offset_mm, x2, y2),
            (hook_plane_offset_mm, x2, top_axis),
            (hook_plane_offset_mm, x1, top_axis),
            (hook_plane_offset_mm, x1, top_axis + hook_vertex_leg_mm),
        )
        bar_id = f"{link.bar_mark}-{index}"
        while bar_id in used:
            bar_id += "-link"
        used.add(bar_id)
        seeds_list.append(
            BarPathSeed(
                bar_id,
                link.bar_mark,
                BarPathRole.TRANSVERSE_LINK,
                1,
                diameter,
                member.link_fy_nmm2,
                tuple(
                    PathNode(
                        str(i),
                        PathPoint(link.station_mm + dx, px, py),
                        radius if 0 < i < 6 else None,
                        (
                            BendKind.HOOK
                            if i in (1, 5)
                            else BendKind.STANDARD_BEND if 0 < i < 6 else None
                        ),
                    )
                    for i, (dx, px, py) in enumerate(vertices)
                ),
            )
        )
    request = BarPathRequest(
        "is456.beam.haunch-geometry/v1",
        haunch.source_reference,
        "is456.beam.haunch-geometry/v1",
        member.member_id,
        "both-spans",
        source_hash,
        member.reinforcement_revision,
        MemberLocalCoordinateSystem(
            "beam-local",
            "member_station_x",
            "section_x_from_left",
            "section_y_from_top",
        ),
        left.left_face_mm,
        right.right_face_mm,
        member.width_mm,
        max(item.depth_mm for item in outline),
        tuple(seeds_list),
        (stock_length_mm,),
    )
    paths = resolve_bar_paths(request)
    if paths.engineering.value != "pass":
        return None, tuple(
            _issue(issue.code, issue.field_or_location or "paths", issue.message)
            for issue in paths.diagnostics
        )
    output = paths.output_as("reinforcement_schedule", BarPathOutput)
    bottom_path = next(
        item.segments for item in output.paths if item.bar_id == bottom_bars[0].bar_id
    )
    bottom_segments = []
    for segment in bottom_path:
        record = {
            "start": [segment.start.station_x_mm, segment.start.section_y_from_top_mm],
            "end": [segment.end.station_x_mm, segment.end.section_y_from_top_mm],
            "length_mm": segment.centreline_length_mm,
        }
        if segment.kind is PathSegmentKind.BEND_ARC:
            centre = segment.bend_centre
            assert centre is not None
            record.update(
                centre=[centre.station_x_mm, centre.section_y_from_top_mm],
                radius_mm=segment.bend_radius_mm,
            )
        bottom_segments.append(record)

    if any(
        item.kind is PathSegmentKind.BEND_ARC
        and (item.bend_sweep_degrees is None or item.bend_sweep_degrees >= 90)
        for item in bottom_path
    ):
        return None, (
            _issue(
                "BEAM.HAUNCH_BASIS_HELD",
                "haunch.bottom_bar_path",
                "Use a shallow and monotonic longitudinal path through the haunch.",
            ),
        )
    bar_slope = _bar_maximum_slope(bottom_path)
    outline_slope = max(
        abs((b.depth_mm - a.depth_mm) / (b.station_mm - a.station_mm))
        for a, b in pairwise(outline)
    )
    bar_secant = math.hypot(1, bar_slope)
    intervals = math.ceil(extent.end_mm - extent.start_mm)
    step = (extent.end_mm - extent.start_mm) / intervals
    sampled = min(
        _linear_value(outline, x, "depth_mm") - _bar_axis_at(bottom_path, x)
        for x in (extent.start_mm + i * step for i in range(intervals + 1))
    )
    soffit_cover = (sampled - step * (bar_slope + outline_slope) / 2) / math.hypot(
        1, outline_slope
    ) - bottom_r
    if soffit_cover < haunch.minimum_cover_mm:
        issues.append(
            _issue(
                "BEAM.HAUNCH_BAR_COVER_FAIL",
                "haunch.bottom_bar_path",
                "The resolved curved bar does not maintain cover along the whole haunch.",
            )
        )

    corner_x = inset + radius
    for face in (top_bars, bottom_bars):
        ordered = sorted(face, key=lambda bar: bar.x_from_left_mm)
        if not (
            ordered[0].x_from_left_mm
            <= corner_x
            < member.width_mm - corner_x
            <= ordered[-1].x_from_left_mm
            and ordered[-1].x_from_left_mm - ordered[0].x_from_left_mm
            >= member.aggregate_size_mm
            + 5
            + (ordered[0].diameter_mm + ordered[1].diameter_mm) / 2
        ):
            issues.append(
                _issue(
                    "BEAM.HAUNCH_LINK_FIT_FAIL",
                    "member.bars",
                    "The cage requires separate, correctly spaced bars seated in the four link bends.",
                )
            )
    for bar in top_bars:
        corner_y = top_axis + radius
        offset_x = corner_x - min(
            bar.x_from_left_mm, member.width_mm - bar.x_from_left_mm
        )
        radial = (
            internal_bend_radius_mm
            - bar.diameter_mm / 2
            - math.hypot(offset_x, corner_y - bar.y_from_top_mm)
        )
        if (
            bar.y_from_top_mm > corner_y
            or not -1e-9 <= radial <= haunch.maximum_seat_gap_mm
        ):
            issues.append(
                _issue(
                    "BEAM.HAUNCH_LINK_FIT_FAIL",
                    f"member.bars.{bar.bar_id}",
                    "The top bar does not occupy a supported rounded link bend.",
                )
            )

    checks: list[dict[str, Any]] = []
    for link in links:
        x, bottom = link.station_mm, link.bottom_axis_mm
        other = x + hook_plane_offset_mm
        lower_axes = [_bar_axis_at(bottom_path, station) for station in (x, other)]
        lower_section_axes = [*lower_axes]
        lower_section_axes.extend(
            _path_point(segment, segment.bend_centre.station_x_mm)
            for segment in bottom_path
            if segment.bend_centre is not None
            and max(x, segment.start.station_x_mm)
            < segment.bend_centre.station_x_mm
            < min(other, segment.end.station_x_mm)
        )
        cover = min(
            inset - link_radius,
            _link_soffit_cover(x, other, top_axis, bottom, outline, link_radius),
        )
        corner_y = bottom - radius
        radial_distances = [
            math.hypot(
                corner_x
                - min(bar.x_from_left_mm, member.width_mm - bar.x_from_left_mm),
                y - corner_y,
            )
            for bar in bottom_bars
            for y in lower_section_axes
        ]
        minimum_gap = (
            internal_bend_radius_mm - bottom_r * bar_secant - max(radial_distances)
        )
        maximum_gap = internal_bend_radius_mm - bottom_r - min(radial_distances)
        checks.append(
            {
                "station_mm": x,
                "bottom_axis_mm": bottom,
                "bottom_axes_mm": lower_axes,
                "cover_mm": cover,
                "minimum_seat_gap_mm": minimum_gap,
                "maximum_seat_gap_mm": maximum_gap,
            }
        )
        if (
            cover + 1e-9 < haunch.minimum_cover_mm
            or min(lower_section_axes) < corner_y
            or minimum_gap < -1e-9
            or maximum_gap > haunch.maximum_seat_gap_mm
        ):
            issues.append(
                _issue(
                    "BEAM.HAUNCH_LINK_FIT_FAIL",
                    f"haunch.links[{x:g}]",
                    "The actual rounded link clashes, loses a supported seat, or reduces normal cover.",
                )
            )
    return HaunchGeometry(
        paths,
        outline,
        bottom_path,
        bottom_segments,
        checks,
        min(row["cover_mm"] for row in checks),
        soffit_cover,
        opening,
    ), tuple(issues)
