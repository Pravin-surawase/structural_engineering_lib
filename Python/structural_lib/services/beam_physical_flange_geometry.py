"""Resolve the ordinary T-flange assembly and certify its physical fit."""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import combinations, pairwise
from typing import Annotated, Any, Literal

from pydantic import Field, field_validator

from structural_lib.beam.bar_paths import (
    BarPathOutput,
    BarPathRequest,
    BarPathRole,
    BarPathSeed,
    BendKind,
    MemberLocalCoordinateSystem,
    PathNode,
    PathPoint,
    ResolvedBarPath,
    resolve_bar_paths,
)
from structural_lib.beam.semantics import EngineeringState, OperationResult
from structural_lib.beam.t_section_geometry import (
    _segment_boxes,
    _segment_station_bounds,
)
from structural_lib.codes.is456.column.detailing import (
    calculate_tie_spacing,
    minimum_tie_diameter,
)
from structural_lib.construction import LinkPlacementZone
from structural_lib.core.result_contract import StructuralIssueV1
from structural_lib.services._physical_dxf import _segment_points
from structural_lib.services.beam_physical_flange_strip import BeamPhysicalFlangeStripV1
from structural_lib.services.contracts.beam_continuous import (
    BeamLayeredContinuousCheckRequestV1,
    Identifier,
)
from structural_lib.services.contracts.common import StrictPublicModel

_MM = Annotated[float, Field(ge=-32000, le=32000)]
_Point = tuple[float, float, float]
_Box = tuple[float, float, float, float, float, float]
_Interval = tuple[float, float]
_EPS = 1e-7


class BeamPhysicalFlangeBarV1(StrictPublicModel):
    """A straight beam-owned bar outside the web in the tension flange."""

    bar_id: Identifier
    mark: Identifier
    face: Literal["top"]
    x_from_left_mm: _MM
    y_from_top_mm: Annotated[float, Field(gt=0, le=300)]
    diameter_mm: Annotated[float, Field(ge=8, le=32)]
    start_mm: _MM
    end_mm: _MM


class BeamFlangeLinkV1(StrictPublicModel):
    """One linked pair of 90-degree hooks on a uniform transverse grid."""

    mark: Identifier
    first_station_mm: _MM
    last_station_mm: _MM
    spacing_mm: Annotated[float, Field(gt=0, le=300)]
    left_axis_mm: _MM
    right_axis_mm: _MM
    top_axis_mm: Annotated[float, Field(gt=0, le=300)]
    bottom_axis_mm: Annotated[float, Field(gt=0, le=300)]
    diameter_mm: Annotated[float, Field(ge=6, le=16)]
    internal_bend_radius_mm: Annotated[float, Field(gt=0, le=100)]
    hook_vertex_leg_mm: Annotated[float, Field(gt=0, le=300)]


class BeamPhysicalFlangePlacementV1(StrictPublicModel):
    """Project placement allowances for the tied assemblies and slab layers."""

    maximum_assembly_translation_per_axis_mm: Annotated[float, Field(ge=0, le=10)]
    minimum_compaction_access_mm: Annotated[float, Field(gt=0, le=150)]
    web_cover_mm: Annotated[float, Field(ge=20, le=75)]
    flange_link_cover_mm: Annotated[float, Field(ge=20, le=75)]
    slab_cover_mm: Annotated[float, Field(ge=20, le=75)]


class BeamPhysicalFlangeDetailV1(StrictPublicModel):
    """Physical tension-flange evidence for one symmetric monolithic T beam."""

    geometry_revision: Identifier
    analysis_revision: Identifier
    reinforcement_revision: Identifier
    flange_bars: tuple[BeamPhysicalFlangeBarV1, BeamPhysicalFlangeBarV1]
    flange_links: BeamFlangeLinkV1
    slab_strip: BeamPhysicalFlangeStripV1 | None
    placement: BeamPhysicalFlangePlacementV1

    @field_validator("flange_bars", mode="before")
    @classmethod
    def accept_bar_array(cls, value: object) -> object:
        return tuple(value) if isinstance(value, list) else value


@dataclass(frozen=True)
class _Piece:
    seed: BarPathSeed
    owner: str
    role: str


@dataclass(frozen=True)
class PhysicalFlangeGeometry:
    paths: OperationResult
    zones: tuple[LinkPlacementZone, LinkPlacementZone]
    placement: dict[str, Any]
    pieces: list[dict[str, Any]]


def flange_issue(code: str, path: str, message: str) -> StructuralIssueV1:
    return StructuralIssueV1("BEAM.FLANGE_" + code, "physical_flange." + path, message)


def _stations(start: float, end: float, pitch: float) -> tuple[float, ...]:
    count = (end - start) / pitch
    if not 1 <= round(count) <= 250 or not math.isclose(
        count, round(count), abs_tol=_EPS, rel_tol=0
    ):
        return ()
    return tuple(start + i * pitch for i in range(round(count) + 1))


def _straight(
    key: str,
    mark: str,
    role: BarPathRole,
    diameter: float,
    start: _Point,
    end: _Point,
    origin: float,
) -> BarPathSeed:
    return BarPathSeed(
        key,
        mark,
        role,
        1,
        diameter,
        415,
        (
            PathNode("start", PathPoint(start[0], start[1] + origin, start[2])),
            PathNode("end", PathPoint(end[0], end[1] + origin, end[2])),
        ),
    )


def _links(
    mark: str,
    vertices: tuple[_Point, ...],
    hooks: tuple[int, int],
    stations: tuple[float, ...],
    diameter: float,
    radius: float,
    origin: float,
    role: str,
) -> list[_Piece]:
    return [
        _Piece(
            BarPathSeed(
                f"{mark}-{i}",
                mark,
                BarPathRole.TRANSVERSE_LINK,
                1,
                diameter,
                415,
                tuple(
                    PathNode(
                        str(index),
                        PathPoint(station + offset, x + origin, y),
                        radius if 0 < index < len(vertices) - 1 else None,
                        (
                            BendKind.HOOK
                            if index in hooks
                            else (
                                BendKind.STANDARD_BEND
                                if 0 < index < len(vertices) - 1
                                else None
                            )
                        ),
                    )
                    for index, (offset, x, y) in enumerate(vertices)
                ),
            ),
            "BEAM",
            role,
        )
        for i, station in enumerate(stations, 1)
    ]


def _spacing_is_clear(a: float, b: float, limit: float) -> bool:
    return math.isclose(a, b, abs_tol=limit, rel_tol=0)


def _web_cage_seated(
    member: BeamLayeredContinuousCheckRequestV1, r_internal: float
) -> bool:
    inset = member.clear_cover_mm + member.link_diameter_mm
    left = inset + r_internal
    depth = member.depth_mm
    diameters = tuple(bar.diameter_mm for bar in member.bars)
    # This ordinary cage uses four nominal seats with bar radii equal to
    # the inside bend radius, as well as restrained intermediate face bars.
    if min(diameters) != max(diameters) or not _spacing_is_clear(
        diameters[0] / 2, r_internal, _EPS
    ):
        return False
    if member.link_spacing_mm > calculate_tie_spacing(
        member.width_mm, depth, diameters[0]
    ) or member.link_diameter_mm < minimum_tie_diameter(diameters[0]):
        return False
    for face, y in (("top", left), ("bottom", depth - left)):
        bars = sorted(
            (bar for bar in member.bars if bar.face == face),
            key=lambda bar: bar.x_from_left_mm,
        )
        if not (
            2 <= len(bars) <= 4
            and all(
                bar.layer == 1 and _spacing_is_clear(bar.y_from_top_mm, y, _EPS)
                for bar in bars
            )
            and _spacing_is_clear(bars[0].x_from_left_mm, left, _EPS)
            and _spacing_is_clear(bars[-1].x_from_left_mm, member.width_mm - left, _EPS)
        ):
            return False
        if len(bars) > 2 and any(
            b.x_from_left_mm - a.x_from_left_mm > 75 + _EPS for a, b in pairwise(bars)
        ):
            return False
    return True


def _bounds(path: ResolvedBarPath) -> tuple[_Box, ...]:
    return tuple(
        (*_segment_station_bounds(segment), *box)
        for segment in path.segments
        for box in _segment_boxes(segment)
    )


def _envelope(boxes: tuple[_Box, ...]) -> _Box:
    result: _Box = (
        min(b[0] for b in boxes),
        max(b[1] for b in boxes),
        min(b[2] for b in boxes),
        max(b[3] for b in boxes),
        min(b[4] for b in boxes),
        max(b[5] for b in boxes),
    )
    return result


def _separation(a: _Box, b: _Box, allowance: float) -> float:
    return math.hypot(
        max(a[0] - b[1] - allowance, b[0] - a[1] - allowance, 0),
        max(a[2] - b[3] - allowance, b[2] - a[3] - allowance, 0),
        max(a[4] - b[5] - allowance, b[4] - a[5] - allowance, 0),
    )


def _clearance(
    a: tuple[_Box, ...], b: tuple[_Box, ...], allowance: float, limit: float
) -> float:
    result = limit
    for left in a:
        for right in b:
            distance = _separation(left, right, allowance)
            if distance < result:
                result = distance
    return result


def _largest_gap(intervals: list[_Interval], low: float, high: float) -> float:
    end = low
    greatest = 0.0
    for start, stop in sorted(intervals):
        if stop < end or start >= high:
            continue
        greatest = max(greatest, start - end)
        end = max(end, stop)
    return max(greatest, high - end)


@dataclass(frozen=True)
class _ResolvedPiece:
    piece: _Piece
    path: ResolvedBarPath
    boxes: tuple[_Box, ...]
    extent: _Box

    @property
    def radius(self) -> float:
        return self.path.diameter_mm / 2

    @property
    def assembly(self) -> str:
        return self.piece.role.split("_", 1)[0]

    @property
    def longitudinal(self) -> bool:
        return (
            self.piece.role.endswith("longitudinal")
            or self.piece.role == "slab_distribution"
        )


def _parallel_bars_fit(
    pieces: tuple[_ResolvedPiece, ...], aggregate: float, tolerance: float
) -> bool:
    longitudinal = (piece for piece in pieces if piece.longitudinal)
    for a, b in combinations(longitudinal, 2):
        if a.assembly == b.assembly:
            continue
        x, y = abs(a.extent[2] - b.extent[2]), abs(a.extent[4] - b.extent[4])
        margin = a.radius + b.radius + 2 * tolerance
        diameter = 2 * max(a.radius, b.radius)
        if (
            x - margin < max(diameter, aggregate + 5) - _EPS
            and y - margin < max(diameter, 15, 2 * aggregate / 3) - _EPS
        ):
            return False
    return True


def _crossings(
    pieces: tuple[_ResolvedPiece, ...], tolerance: float
) -> dict[str, float]:
    nominal: dict[str, float] = {}
    adverse: dict[str, float] = {}
    for a, b in combinations(pieces, 2):
        if a.assembly == b.assembly and (
            a.assembly != "slab" or a.piece.role == b.piece.role
        ):
            # The web and flange pieces are already pinned to their seats
            # inside each tied assembly. Parallel slab spacing is checked
            # by the physical strip leaf.
            continue
        name = ":".join(sorted((a.piece.role, b.piece.role)))
        radius = a.radius + b.radius
        for destination, shift in ((nominal, 0.0), (adverse, 2 * tolerance)):
            best = destination.get(name, math.inf) + radius
            if _separation(a.extent, b.extent, shift) >= best:
                continue
            destination[name] = _clearance(a.boxes, b.boxes, shift, best) - radius
    return {**{f"nominal/{k}": v for k, v in nominal.items()}, **adverse}


def _cover(
    extent: _Box,
    longitudinal: _Interval,
    horizontal: _Interval,
    depth: float,
    radius: float,
    role: str,
) -> float:
    # Orthogonal straight pieces end in a flat cross-section. Their
    # steel radius projects onto the two axes across the piece.
    axial_radius = (
        0 if role.endswith("longitudinal") or role == "slab_distribution" else radius
    )
    horizontal_radius = 0 if role == "slab_transverse" else radius
    return min(
        extent[0] - longitudinal[0] - axial_radius,
        longitudinal[1] - extent[1] - axial_radius,
        extent[2] - horizontal[0] - horizontal_radius,
        horizontal[1] - extent[3] - horizontal_radius,
        extent[4] - radius,
        depth - extent[5] - radius,
    )


def _receipts(
    pieces: tuple[_ResolvedPiece, ...],
    member: BeamLayeredContinuousCheckRequestV1,
    detail: BeamPhysicalFlangeDetailV1,
    origin: float,
) -> dict[str, Any]:
    flange, slab = member.flange, detail.slab_strip
    assert flange is not None and slab is not None
    left, middle, right = member.supports
    tol = detail.placement.maximum_assembly_translation_per_axis_mm
    beam_span = (left.left_face_mm, right.right_face_mm)
    slab_span = slab.width_between_stations_mm
    cover = {
        "web": math.inf,
        "flange": math.inf,
        "slab": math.inf,
    }
    x_blocked = []
    z_blocked = []
    for piece in pieces:
        group, box, radius = piece.assembly, piece.extent, piece.radius
        if group == "web":
            depth, span = member.depth_mm, beam_span
            width = (origin, origin + member.width_mm)
        elif group == "flange":
            depth, span = flange.thickness_mm, beam_span
            width = (
                origin - flange.left_overhang_mm,
                origin + member.width_mm + flange.right_overhang_mm,
            )
        else:
            depth, span = flange.thickness_mm, slab_span
            width = (
                origin + slab.transverse_edge_x_mm[0],
                origin + slab.transverse_edge_x_mm[1],
            )
        cover[group] = min(
            cover[group], _cover(box, span, width, depth, radius, piece.piece.role)
        )
        if not piece.longitudinal:
            z_blocked.append((box[0] - radius - tol, box[1] + radius + tol))
        else:
            # The concrete placement lane can follow the as-built rigid
            # web cage. Other assemblies can displace relative to it.
            relative = 0 if group == "web" else 2 * tol
            x_blocked.append((box[2] - radius - relative, box[3] + radius + relative))
    inset = member.clear_cover_mm + member.link_diameter_mm / 2
    transverse = _largest_gap(
        x_blocked, origin + inset, origin + member.width_mm - inset
    )
    axial = _largest_gap(z_blocked, middle.left_face_mm, middle.right_face_mm)
    return {
        "nominal_cover_mm": cover,
        "minimum_cover_after_tolerance_mm": {k: v - tol for k, v in cover.items()},
        "crossing_clearances_mm": _crossings(pieces, tol),
        "axial_access_mm": axial,
        "transverse_access_mm": transverse,
        "minimum_compaction_access_mm": min(axial, transverse),
    }


def _visible_pieces(
    pieces: tuple[_ResolvedPiece, ...], origin: float
) -> list[dict[str, Any]]:
    output = []
    for item in pieces:
        points = [
            (z, x - origin, y)
            for segment in item.path.segments
            for z, x, y in _segment_points(segment, 0.12)
        ]
        output.append(
            {
                "bar_id": item.path.bar_id,
                "mark": item.path.bar_mark,
                "owner": item.piece.owner,
                "role": item.piece.role,
                "diameter_mm": item.path.diameter_mm,
                "points_mm": points,
            }
        )
    return output


def resolve_physical_flange_geometry(
    member: BeamLayeredContinuousCheckRequestV1,
    detail: BeamPhysicalFlangeDetailV1,
    *,
    web_first: float,
    web_last: float,
    web_internal_radius: float,
    web_tail: float,
    web_hook_shift: float,
    source_hash: str,
    stock_length_mm: float,
) -> tuple[PhysicalFlangeGeometry | None, tuple[StructuralIssueV1, ...]]:
    """Resolve and compare actual curves on their declared assembly grids."""
    slab, cap = detail.slab_strip, detail.flange_links
    flange, extent = member.flange, member.straight_bars
    assert slab is not None and flange is not None and extent is not None
    origin = -slab.transverse_edge_x_mm[0]
    wl = _stations(web_first, web_last, member.link_spacing_mm)
    fl = _stations(cap.first_station_mm, cap.last_station_mm, cap.spacing_mm)
    a, _, c = member.supports
    if not (
        wl
        and fl
        and max(wl[0], fl[0]) <= a.right_face_mm
        and min(wl[-1], fl[-1]) >= c.left_face_mm
        and cap.spacing_mm
        <= min(
            member.link_spacing_mm, 16 * min(b.diameter_mm for b in detail.flange_bars)
        )
    ):
        return None, (
            flange_issue(
                "LINK_GRID_FAIL",
                "flange_links",
                "Both fitted link grids must cover the spans at their governing pitches.",
            ),
        )
    if not _web_cage_seated(member, web_internal_radius):
        return None, (
            flange_issue(
                "WEB_SEAT_FAIL",
                "member.bars",
                "Provide four seated web corners and demonstrably restrained intermediate bars.",
            ),
        )
    radius = cap.internal_bend_radius_mm + cap.diameter_mm / 2
    left, right = sorted(detail.flange_bars, key=lambda b: b.x_from_left_mm)
    if not (
        cap.hook_vertex_leg_mm - radius >= 8 * cap.diameter_mm
        and cap.right_axis_mm - cap.left_axis_mm > 2 * cap.hook_vertex_leg_mm
        and cap.bottom_axis_mm - cap.top_axis_mm > 2 * radius
        and right.x_from_left_mm > member.width_mm > 0 > left.x_from_left_mm
        and _spacing_is_clear(left.x_from_left_mm, cap.left_axis_mm + radius, _EPS)
        and _spacing_is_clear(right.x_from_left_mm, cap.right_axis_mm - radius, _EPS)
        and all(
            _spacing_is_clear(bar.y_from_top_mm, cap.top_axis_mm + radius, _EPS)
            and 0 <= cap.internal_bend_radius_mm - bar.diameter_mm / 2 <= 2
            and bar.start_mm <= fl[0]
            and bar.end_mm >= fl[-1]
            for bar in (left, right)
        )
        and cap.diameter_mm
        >= minimum_tie_diameter(max(b.diameter_mm for b in (left, right)))
    ):
        return None, (
            flange_issue(
                "CAP_SEAT_FAIL",
                "flange_links",
                "The flange link must seat both outboard bars and provide its two developed hook tails.",
            ),
        )
    x1 = y1 = member.clear_cover_mm + member.link_diameter_mm / 2
    x2, y2 = member.width_mm - x1, member.depth_mm - y1
    wl_r = web_internal_radius + member.link_diameter_mm / 2
    if not (
        web_tail - wl_r >= 8 * member.link_diameter_mm
        and web_tail < min(x2 - x1, y2 - y1)
        and member.link_diameter_mm
        < web_hook_shift
        < member.link_spacing_mm - member.link_diameter_mm
    ):
        return None, (
            flange_issue(
                "WEB_HOOK_FAIL",
                "link_detail",
                "Check both web hook tails and spacing between the two hook planes.",
            ),
        )
    web_vertices: tuple[_Point, ...] = (
        (0, x1 + web_tail, y1),
        (0, x1, y1),
        (0, x1, y2),
        (web_hook_shift, x2, y2),
        (web_hook_shift, x2, y1),
        (web_hook_shift, x1, y1),
        (web_hook_shift, x1, y1 + web_tail),
    )
    cap_vertices: tuple[_Point, ...] = (
        (0, cap.left_axis_mm + cap.hook_vertex_leg_mm, cap.top_axis_mm),
        (0, cap.left_axis_mm, cap.top_axis_mm),
        (0, cap.left_axis_mm, cap.bottom_axis_mm),
        (0, cap.right_axis_mm, cap.bottom_axis_mm),
        (0, cap.right_axis_mm, cap.top_axis_mm),
        (0, cap.right_axis_mm - cap.hook_vertex_leg_mm, cap.top_axis_mm),
    )
    web_mark = f"WL{member.link_diameter_mm:g}"
    pieces = _links(
        web_mark,
        web_vertices,
        (1, 5),
        wl,
        member.link_diameter_mm,
        wl_r,
        origin,
        "web_link",
    )
    pieces.extend(
        _links(
            cap.mark,
            cap_vertices,
            (1, 4),
            fl,
            cap.diameter_mm,
            radius,
            origin,
            "flange_link",
        )
    )
    for bar in member.bars:
        top = bar.face == "top"
        pieces.append(
            _Piece(
                _straight(
                    bar.bar_id,
                    f"W{'T' if top else 'B'}{bar.diameter_mm:g}",
                    (
                        BarPathRole.TOP_LONGITUDINAL
                        if top
                        else BarPathRole.BOTTOM_LONGITUDINAL
                    ),
                    bar.diameter_mm,
                    (extent.start_mm, bar.x_from_left_mm, bar.y_from_top_mm),
                    (extent.end_mm, bar.x_from_left_mm, bar.y_from_top_mm),
                    origin,
                ),
                "BEAM",
                "web_longitudinal",
            )
        )
    for flange_bar in detail.flange_bars:
        pieces.append(
            _Piece(
                _straight(
                    flange_bar.bar_id,
                    flange_bar.mark,
                    BarPathRole.TOP_LONGITUDINAL,
                    flange_bar.diameter_mm,
                    (
                        flange_bar.start_mm,
                        flange_bar.x_from_left_mm,
                        flange_bar.y_from_top_mm,
                    ),
                    (
                        flange_bar.end_mm,
                        flange_bar.x_from_left_mm,
                        flange_bar.y_from_top_mm,
                    ),
                    origin,
                ),
                "BEAM",
                "flange_longitudinal",
            )
        )
    for face in ("TOP", "BOTTOM"):
        main, dist = slab.main, slab.distribution
        my = main.top_axis_mm if face == "TOP" else main.bottom_axis_mm
        dy = dist.top_axis_mm if face == "TOP" else dist.bottom_axis_mm
        main_mark = f"SM{main.diameter_mm:g}-{face}"
        dist_mark = f"SD{dist.diameter_mm:g}-{face}"
        for number, station in enumerate(main.stations_mm, 1):
            pieces.append(
                _Piece(
                    _straight(
                        f"{main_mark}-{number}",
                        main_mark,
                        BarPathRole.FLANGE_TRANSVERSE,
                        main.diameter_mm,
                        (station, main.x_ends_mm[0], my),
                        (station, main.x_ends_mm[1], my),
                        origin,
                    ),
                    "SLAB",
                    "slab_transverse",
                )
            )
        for number, x in enumerate(dist.x_axes_mm, 1):
            pieces.append(
                _Piece(
                    _straight(
                        f"{dist_mark}-{number}",
                        dist_mark,
                        BarPathRole.FLANGE_DISTRIBUTION,
                        dist.diameter_mm,
                        (dist.end_stations_mm[0], x, dy),
                        (dist.end_stations_mm[1], x, dy),
                        origin,
                    ),
                    "SLAB",
                    "slab_distribution",
                )
            )

    marks: dict[str, tuple[str, str]] = {}
    for piece in pieces:
        ownership = (piece.owner, piece.role)
        if marks.setdefault(piece.seed.bar_mark, ownership) != ownership:
            return None, (
                flange_issue(
                    "MARK_CONFLICT_FAIL",
                    "flange_bars",
                    "Each mark must identify one physical role and schedule owner.",
                ),
            )
    path_result = resolve_bar_paths(
        BarPathRequest(
            "IS456-PHYSICAL-T-FLANGE",
            source_hash,
            detail.geometry_revision,
            member.member_id,
            member.member_id,
            detail.geometry_revision,
            detail.reinforcement_revision,
            MemberLocalCoordinateSystem(
                "slab-left",
                "member_station_x",
                "section_x_from_left",
                "section_y_from_top",
            ),
            min(slab.width_between_stations_mm[0], a.left_face_mm),
            max(slab.width_between_stations_mm[1], c.right_face_mm),
            slab.transverse_edge_x_mm[1] + origin,
            member.depth_mm,
            tuple(piece.seed for piece in pieces),
            (stock_length_mm,),
        )
    )
    if path_result.engineering is not EngineeringState.PASS:
        return None, (
            flange_issue(
                "PATH_FAIL",
                "flange_links",
                "The submitted bars do not resolve into supported fabricated paths.",
            ),
        )
    metadata = {p.seed.bar_id: p for p in pieces}
    resolved = []
    for path in path_result.output_as("reinforcement_schedule", BarPathOutput).paths:
        boxes = _bounds(path)
        resolved.append(
            _ResolvedPiece(metadata[path.bar_id], path, boxes, _envelope(boxes))
        )
    items = tuple(resolved)
    placement = _receipts(items, member, detail, origin)
    issues = []
    if not _parallel_bars_fit(
        items,
        member.aggregate_size_mm,
        detail.placement.maximum_assembly_translation_per_axis_mm,
    ):
        issues.append(
            flange_issue(
                "BAR_SPACING_FAIL",
                "flange_bars",
                "Check clear spacing between parallel bars in the separate assemblies at the placement limits.",
            )
        )
    if any(value < -_EPS for value in placement["crossing_clearances_mm"].values()):
        issues.append(
            flange_issue(
                "LINK_CLASH_FAIL",
                "flange_links",
                "Resolved beam or slab steel crosses another assembly within the placement tolerance.",
            )
        )
    for key, need in (
        ("web", detail.placement.web_cover_mm),
        ("flange", detail.placement.flange_link_cover_mm),
        ("slab", detail.placement.slab_cover_mm),
    ):
        if placement["minimum_cover_after_tolerance_mm"][key] < need - _EPS:
            issues.append(
                flange_issue(
                    "COVER_FAIL",
                    "placement",
                    f"The {key} assembly does not have the required cover at the declared tolerance.",
                )
            )
    if (
        placement["minimum_compaction_access_mm"]
        < detail.placement.minimum_compaction_access_mm - _EPS
    ):
        issues.append(
            flange_issue(
                "ACCESS_FAIL",
                "placement",
                "The interior support lacks the required local compaction opening.",
            )
        )
    zones = (
        LinkPlacementZone(
            "web-grid", web_mark, wl[0], wl[-1], member.link_spacing_mm, True, True
        ),
        LinkPlacementZone(
            "flange-grid", cap.mark, fl[0], fl[-1], cap.spacing_mm, True, True
        ),
    )
    return PhysicalFlangeGeometry(
        path_result, zones, placement, _visible_pieces(items, origin)
    ), tuple(issues)
