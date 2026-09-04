"""Resolve explicit reinforcement centreline paths into tangent geometry."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from .semantics import (
    Diagnostic,
    EngineeringState,
    OperationResult,
    Provenance,
    completed_result,
    effective_inputs,
    rejected_result,
)

RESOLVE_BAR_PATHS_OPERATION = "structural.reinforcement_paths.resolve/v1"
BAR_PATH_METHOD_REVISION = "structural-reinforcement-paths-wp06-v1"


class BarPathRole(StrEnum):
    TOP_LONGITUDINAL = "top_longitudinal"
    BOTTOM_LONGITUDINAL = "bottom_longitudinal"
    SIDE_LEFT = "side_left"
    SIDE_RIGHT = "side_right"
    TORSION_CORNER = "torsion_corner"
    TRANSVERSE_LINK = "transverse_link"


class BendKind(StrEnum):
    STANDARD_BEND = "standard_bend"
    HOOK = "hook"
    TRANSITION = "transition"


class PathSegmentKind(StrEnum):
    TANGENT_STRAIGHT = "tangent_straight"
    BEND_ARC = "bend_arc"


@dataclass(frozen=True)
class MemberLocalCoordinateSystem:
    datum_id: str
    station_axis: str
    section_horizontal_axis: str
    section_vertical_axis: str


@dataclass(frozen=True)
class PathPoint:
    station_x_mm: float
    section_x_from_left_mm: float
    section_y_from_top_mm: float


@dataclass(frozen=True)
class MemberLocalVector:
    station_component: float
    section_horizontal_component: float
    section_vertical_component: float


@dataclass(frozen=True)
class PathNode:
    node_id: str
    point: PathPoint
    bend_radius_mm: float | None = None
    bend_kind: BendKind | None = None


@dataclass(frozen=True)
class BarPathSeed:
    bar_id: str
    bar_mark: str
    role: BarPathRole
    layer: int
    diameter_mm: float
    steel_grade_n_per_mm2: float
    nodes: tuple[PathNode, ...]
    closed: bool = False
    bundle_size: int = 1
    anchorage_requirement_ids: tuple[str, ...] = ()
    splice_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class BarPathRequest:
    profile_id: str
    project_basis_id: str
    criteria_revision_id: str
    member_id: str
    physical_span_id: str
    topology_revision_id: str
    detail_revision_id: str
    coordinate_system: MemberLocalCoordinateSystem
    member_start_x_mm: float
    member_end_x_mm: float
    section_width_mm: float
    section_depth_mm: float
    paths: tuple[BarPathSeed, ...]
    stock_lengths_mm: tuple[float, ...]
    geometry_tolerance_mm: float = 1e-6


@dataclass(frozen=True)
class ResolvedPathSegment:
    segment_id: str
    kind: PathSegmentKind
    start: PathPoint
    end: PathPoint
    centreline_length_mm: float
    bend_centre: PathPoint | None = None
    bend_radius_mm: float | None = None
    bend_angle_degrees: float | None = None
    bend_plane_normal: MemberLocalVector | None = None
    bend_sweep_degrees: float | None = None
    bend_kind: BendKind | None = None


@dataclass(frozen=True)
class ResolvedBarPath:
    bar_id: str
    bar_mark: str
    role: BarPathRole
    layer: int
    diameter_mm: float
    steel_grade_n_per_mm2: float
    bundle_size: int
    closed: bool
    node_ids: tuple[str, ...]
    segments: tuple[ResolvedPathSegment, ...]
    developed_centreline_length_mm: float
    compatible_stock_length_mm: float | None
    anchorage_requirement_ids: tuple[str, ...]
    splice_ids: tuple[str, ...]


@dataclass(frozen=True)
class BarMarkSummary:
    bar_mark: str
    role: BarPathRole
    diameter_mm: float
    steel_grade_n_per_mm2: float
    bundle_size: int
    closed: bool
    bar_ids: tuple[str, ...]
    count: int
    developed_centreline_length_mm: float
    compatible_stock_length_mm: float | None


@dataclass(frozen=True)
class BarPathOutput:
    profile_id: str
    project_basis_id: str
    criteria_revision_id: str
    member_id: str
    physical_span_id: str
    topology_revision_id: str
    detail_revision_id: str
    coordinate_system: MemberLocalCoordinateSystem
    paths: tuple[ResolvedBarPath, ...]
    marks: tuple[BarMarkSummary, ...]
    passed: bool


@dataclass(frozen=True)
class _BendGeometry:
    tangent_in: PathPoint
    tangent_out: PathPoint
    centre: PathPoint
    radius_mm: float
    angle_radians: float
    plane_normal: MemberLocalVector
    kind: BendKind
    tangent_offset_mm: float


class _PathError(ValueError):
    def __init__(self, code: str, message: str, field: str) -> None:
        super().__init__(message)
        self.code = code
        self.field = field


def _text(value: str | None) -> bool:
    return bool(value and value.strip())


def _diagnostic(code: str, message: str, field: str, remediation: str) -> Diagnostic:
    return Diagnostic(
        code,
        "error",
        message,
        RESOLVE_BAR_PATHS_OPERATION,
        field,
        "reinforcement-paths",
        remediation,
    )


def _provenance() -> Provenance:
    return Provenance(
        "reinforcement-geometry-wp06-v1",
        BAR_PATH_METHOD_REVISION,
        (
            "PF5 AO18 tangent-straight and bend-arc path contract",
            "WP05 anchorage, lap, curtailment, and arrangement consumers",
        ),
    )


def _coords(point: PathPoint) -> tuple[float, float, float]:
    return (
        point.station_x_mm,
        point.section_x_from_left_mm,
        point.section_y_from_top_mm,
    )


def _point(values: tuple[float, float, float]) -> PathPoint:
    return PathPoint(*values)


def _subtract(
    first: PathPoint,
    second: PathPoint,
) -> tuple[float, float, float]:
    a = _coords(first)
    b = _coords(second)
    return tuple(left - right for left, right in zip(a, b, strict=True))  # type: ignore[return-value]


def _add_scaled(
    base: PathPoint,
    direction: tuple[float, float, float],
    scale: float,
) -> PathPoint:
    return _point(
        tuple(
            value + scale * component
            for value, component in zip(_coords(base), direction, strict=True)
        )  # type: ignore[arg-type]
    )


def _norm(vector: tuple[float, float, float]) -> float:
    return math.sqrt(math.fsum(component * component for component in vector))


def _cross(
    first: tuple[float, float, float],
    second: tuple[float, float, float],
) -> tuple[float, float, float]:
    return (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )


def _unit(
    vector: tuple[float, float, float],
    tolerance: float,
) -> tuple[float, float, float]:
    length = _norm(vector)
    if length <= tolerance:
        raise _PathError(
            "PATH.ZERO_LENGTH",
            "Adjacent path nodes must define a nonzero centreline segment.",
            "nodes",
        )
    return tuple(component / length for component in vector)  # type: ignore[return-value]


def _distance(first: PathPoint, second: PathPoint) -> float:
    return _norm(_subtract(first, second))


def _bend_at(
    previous: PathPoint,
    node: PathNode,
    following: PathPoint,
    tolerance: float,
) -> _BendGeometry | None:
    incoming = _unit(_subtract(node.point, previous), tolerance)
    outgoing = _unit(_subtract(following, node.point), tolerance)
    dot = max(
        -1.0,
        min(1.0, math.fsum(a * b for a, b in zip(incoming, outgoing, strict=True))),
    )
    angle = math.acos(dot)
    has_bend_data = node.bend_radius_mm is not None or node.bend_kind is not None
    if angle <= 1e-10:
        if has_bend_data:
            raise _PathError(
                "BEND.UNNEEDED",
                "A collinear path node cannot carry bend radius or bend kind.",
                f"nodes[{node.node_id}]",
            )
        return None
    if math.pi - angle <= 1e-10:
        raise _PathError(
            "BEND.REVERSAL",
            "A reinforcement path cannot reverse direction through a 180-degree vertex.",
            f"nodes[{node.node_id}]",
        )
    if (
        node.bend_radius_mm is None
        or not math.isfinite(node.bend_radius_mm)
        or node.bend_radius_mm <= 0
        or not isinstance(node.bend_kind, BendKind)
    ):
        raise _PathError(
            "BEND.EVIDENCE_REQUIRED",
            "Every direction change requires a positive centreline bend radius and bend kind.",
            f"nodes[{node.node_id}]",
        )
    tangent_offset = node.bend_radius_mm * math.tan(angle / 2)
    tangent_in = _add_scaled(node.point, incoming, -tangent_offset)
    tangent_out = _add_scaled(node.point, outgoing, tangent_offset)
    bisector = _unit(
        tuple(-a + b for a, b in zip(incoming, outgoing, strict=True)),  # type: ignore[arg-type]
        tolerance,
    )
    centre_distance = node.bend_radius_mm / math.cos(angle / 2)
    centre = _add_scaled(node.point, bisector, centre_distance)
    normal = _unit(_cross(incoming, outgoing), tolerance)
    return _BendGeometry(
        tangent_in,
        tangent_out,
        centre,
        node.bend_radius_mm,
        angle,
        MemberLocalVector(*normal),
        node.bend_kind,
        tangent_offset,
    )


def _resolve_seed(
    seed: BarPathSeed,
    tolerance: float,
    stock_lengths: tuple[float, ...],
) -> ResolvedBarPath:
    points = [node.point for node in seed.nodes]
    count = len(points)
    bends: list[_BendGeometry | None] = [None] * count
    if seed.closed:
        for index, node in enumerate(seed.nodes):
            bends[index] = _bend_at(
                points[(index - 1) % count],
                node,
                points[(index + 1) % count],
                tolerance,
            )
    else:
        if any(
            value is not None
            for node in (seed.nodes[0], seed.nodes[-1])
            for value in (node.bend_radius_mm, node.bend_kind)
        ):
            raise _PathError(
                "BEND.ENDPOINT",
                "Open-path endpoints cannot carry bend data; model the hook with an interior tangent vertex and terminal tail.",
                f"paths[{seed.bar_id}].nodes",
            )
        for index in range(1, count - 1):
            bends[index] = _bend_at(
                points[index - 1],
                seed.nodes[index],
                points[index + 1],
                tolerance,
            )

    edge_count = count if seed.closed else count - 1
    for index in range(edge_count):
        following = (index + 1) % count
        available = _distance(points[index], points[following])
        used = (bends[index].tangent_offset_mm if bends[index] is not None else 0) + (
            bends[following].tangent_offset_mm if bends[following] is not None else 0
        )
        if used + tolerance >= available:
            raise _PathError(
                "BEND.OVERLAP",
                "Adjacent bend tangencies consume the complete straight between path nodes.",
                f"paths[{seed.bar_id}].nodes[{index}:{following}]",
            )

    segments: list[ResolvedPathSegment] = []
    sequence = 1
    for index in range(edge_count):
        following = (index + 1) % count
        start = bends[index].tangent_out if bends[index] is not None else points[index]
        end = (
            bends[following].tangent_in
            if bends[following] is not None
            else points[following]
        )
        straight_length = _distance(start, end)
        segments.append(
            ResolvedPathSegment(
                f"{seed.bar_id}:{sequence:03d}",
                PathSegmentKind.TANGENT_STRAIGHT,
                start,
                end,
                straight_length,
            )
        )
        sequence += 1
        bend = bends[following]
        if bend is not None:
            segments.append(
                ResolvedPathSegment(
                    f"{seed.bar_id}:{sequence:03d}",
                    PathSegmentKind.BEND_ARC,
                    bend.tangent_in,
                    bend.tangent_out,
                    bend.radius_mm * bend.angle_radians,
                    bend.centre,
                    bend.radius_mm,
                    math.degrees(bend.angle_radians),
                    bend.plane_normal,
                    math.degrees(bend.angle_radians),
                    bend.kind,
                )
            )
            sequence += 1

    developed = math.fsum(segment.centreline_length_mm for segment in segments)
    stock = next(
        (length for length in stock_lengths if length + tolerance >= developed),
        None,
    )
    return ResolvedBarPath(
        seed.bar_id,
        seed.bar_mark,
        seed.role,
        seed.layer,
        seed.diameter_mm,
        seed.steel_grade_n_per_mm2,
        seed.bundle_size,
        seed.closed,
        tuple(node.node_id for node in seed.nodes),
        tuple(segments),
        developed,
        stock,
        seed.anchorage_requirement_ids,
        seed.splice_ids,
    )


def _same_shape(
    first: ResolvedBarPath,
    second: ResolvedBarPath,
    tolerance: float,
) -> bool:
    if (
        first.role is not second.role
        or abs(first.diameter_mm - second.diameter_mm) > tolerance
        or abs(first.steel_grade_n_per_mm2 - second.steel_grade_n_per_mm2) > tolerance
        or first.bundle_size != second.bundle_size
        or first.closed != second.closed
        or len(first.segments) != len(second.segments)
    ):
        return False
    for left, right in zip(first.segments, second.segments, strict=True):
        if (
            left.kind is not right.kind
            or abs(left.centreline_length_mm - right.centreline_length_mm) > tolerance
            or left.bend_kind is not right.bend_kind
            or (left.bend_radius_mm is None) != (right.bend_radius_mm is None)
            or left.bend_radius_mm is not None
            and right.bend_radius_mm is not None
            and abs(left.bend_radius_mm - right.bend_radius_mm) > tolerance
            or (left.bend_angle_degrees is None) != (right.bend_angle_degrees is None)
            or left.bend_angle_degrees is not None
            and right.bend_angle_degrees is not None
            and abs(left.bend_angle_degrees - right.bend_angle_degrees) > tolerance
            or (left.bend_sweep_degrees is None) != (right.bend_sweep_degrees is None)
            or left.bend_sweep_degrees is not None
            and right.bend_sweep_degrees is not None
            and abs(left.bend_sweep_degrees - right.bend_sweep_degrees) > tolerance
        ):
            return False
    first_normals = tuple(
        segment.bend_plane_normal
        for segment in first.segments
        if segment.bend_plane_normal is not None
    )
    second_normals = tuple(
        segment.bend_plane_normal
        for segment in second.segments
        if segment.bend_plane_normal is not None
    )
    if len(first_normals) != len(second_normals):
        return False
    for left_index in range(len(first_normals)):
        for right_index in range(left_index + 1, len(first_normals)):
            if (
                abs(
                    _vector_dot(first_normals[left_index], first_normals[right_index])
                    - _vector_dot(
                        second_normals[left_index], second_normals[right_index]
                    )
                )
                > tolerance
            ):
                return False
    for first_index in range(len(first_normals)):
        for second_index in range(first_index + 1, len(first_normals)):
            for third_index in range(second_index + 1, len(first_normals)):
                if (
                    abs(
                        _vector_triple(
                            first_normals[first_index],
                            first_normals[second_index],
                            first_normals[third_index],
                        )
                        - _vector_triple(
                            second_normals[first_index],
                            second_normals[second_index],
                            second_normals[third_index],
                        )
                    )
                    > tolerance
                ):
                    return False
    return True


def _vector_dot(first: MemberLocalVector, second: MemberLocalVector) -> float:
    return (
        first.station_component * second.station_component
        + first.section_horizontal_component * second.section_horizontal_component
        + first.section_vertical_component * second.section_vertical_component
    )


def _vector_triple(
    first: MemberLocalVector,
    second: MemberLocalVector,
    third: MemberLocalVector,
) -> float:
    first_values = (
        first.station_component,
        first.section_horizontal_component,
        first.section_vertical_component,
    )
    second_values = (
        second.station_component,
        second.section_horizontal_component,
        second.section_vertical_component,
    )
    cross = _cross(first_values, second_values)
    return (
        cross[0] * third.station_component
        + cross[1] * third.section_horizontal_component
        + cross[2] * third.section_vertical_component
    )


def resolve_bar_paths(request: BarPathRequest) -> OperationResult:
    """Resolve tangent straights and bend arcs for every identified bar path."""

    inputs = effective_inputs(request=request)
    provenance = _provenance()
    identities = (
        request.profile_id,
        request.project_basis_id,
        request.criteria_revision_id,
        request.member_id,
        request.physical_span_id,
        request.topology_revision_id,
        request.detail_revision_id,
        request.coordinate_system.datum_id,
    )
    coordinate_system = request.coordinate_system
    if (
        not all(_text(value) for value in identities)
        or coordinate_system.station_axis != "member_station_x"
        or coordinate_system.section_horizontal_axis != "section_x_from_left"
        or coordinate_system.section_vertical_axis != "section_y_from_top"
        or not all(
            math.isfinite(value)
            for value in (
                request.member_start_x_mm,
                request.member_end_x_mm,
                request.section_width_mm,
                request.section_depth_mm,
                request.geometry_tolerance_mm,
            )
        )
        or request.member_start_x_mm >= request.member_end_x_mm
        or request.section_width_mm <= 0
        or request.section_depth_mm <= 0
        or request.geometry_tolerance_mm <= 0
    ):
        return rejected_result(
            RESOLVE_BAR_PATHS_OPERATION,
            inputs,
            (
                _diagnostic(
                    "PATH.CONTEXT_INVALID",
                    "Path resolution requires complete revisions, the canonical local axes, ordered member limits, positive section dimensions, and tolerance.",
                    "request",
                    "Correct the member coordinate and revision context.",
                ),
            ),
            provenance=provenance,
        )
    if (
        not request.paths
        or not request.stock_lengths_mm
        or any(
            not math.isfinite(value) or value <= 0 for value in request.stock_lengths_mm
        )
        or len(request.stock_lengths_mm) != len(set(request.stock_lengths_mm))
    ):
        return rejected_result(
            RESOLVE_BAR_PATHS_OPERATION,
            inputs,
            (
                _diagnostic(
                    "PATH.CATALOGUE_INVALID",
                    "At least one path and unique positive available stock lengths are required.",
                    "paths,stock_lengths_mm",
                    "Supply the selected detail and versioned stock-length catalogue values.",
                ),
            ),
            provenance=provenance,
        )

    bar_ids = [seed.bar_id for seed in request.paths]
    if len(bar_ids) != len(set(bar_ids)):
        return rejected_result(
            RESOLVE_BAR_PATHS_OPERATION,
            inputs,
            (
                _diagnostic(
                    "PATH.BAR_ID_DUPLICATE",
                    "Every physical bar path requires a unique bar id.",
                    "paths",
                    "Correct the physical placement identities.",
                ),
            ),
            provenance=provenance,
        )

    stock_lengths = tuple(sorted(request.stock_lengths_mm))
    resolved: list[ResolvedBarPath] = []
    for seed in request.paths:
        node_ids = [node.node_id for node in seed.nodes]
        references = (*seed.anchorage_requirement_ids, *seed.splice_ids)
        minimum_nodes = 3 if seed.closed else 2
        if (
            not _text(seed.bar_id)
            or not _text(seed.bar_mark)
            or not isinstance(seed.role, BarPathRole)
            or seed.layer < 1
            or not math.isfinite(seed.diameter_mm)
            or seed.diameter_mm <= 0
            or not math.isfinite(seed.steel_grade_n_per_mm2)
            or seed.steel_grade_n_per_mm2 <= 0
            or seed.bundle_size not in (1, 2, 3, 4)
            or len(seed.nodes) < minimum_nodes
            or not all(_text(node_id) for node_id in node_ids)
            or len(node_ids) != len(set(node_ids))
            or not all(_text(reference) for reference in references)
            or len(references) != len(set(references))
        ):
            return rejected_result(
                RESOLVE_BAR_PATHS_OPERATION,
                inputs,
                (
                    _diagnostic(
                        "PATH.SEED_INVALID",
                        "Each bar requires a unique id, mark, role, layer, diameter, grade, nodes, bundle size, and unique detail references.",
                        f"paths[{seed.bar_id}]",
                        "Correct the selected physical bar path.",
                    ),
                ),
                provenance=provenance,
            )
        if any(
            not all(math.isfinite(value) for value in _coords(node.point))
            or node.point.station_x_mm
            < request.member_start_x_mm - request.geometry_tolerance_mm
            or node.point.station_x_mm
            > request.member_end_x_mm + request.geometry_tolerance_mm
            or node.point.section_x_from_left_mm < -request.geometry_tolerance_mm
            or node.point.section_x_from_left_mm
            > request.section_width_mm + request.geometry_tolerance_mm
            or node.point.section_y_from_top_mm < -request.geometry_tolerance_mm
            or node.point.section_y_from_top_mm
            > request.section_depth_mm + request.geometry_tolerance_mm
            for node in seed.nodes
        ):
            return rejected_result(
                RESOLVE_BAR_PATHS_OPERATION,
                inputs,
                (
                    _diagnostic(
                        "PATH.NODE_OUTSIDE_CONTEXT",
                        "Every path node must be finite and lie within the supplied member and section coordinate bounds.",
                        f"paths[{seed.bar_id}].nodes",
                        "Correct the actual bar centreline coordinates or member context.",
                    ),
                ),
                provenance=provenance,
            )
        try:
            resolved.append(
                _resolve_seed(seed, request.geometry_tolerance_mm, stock_lengths)
            )
        except _PathError as exc:
            return rejected_result(
                RESOLVE_BAR_PATHS_OPERATION,
                inputs,
                (
                    _diagnostic(
                        exc.code,
                        str(exc),
                        exc.field,
                        "Resolve complete non-overlapping tangent and bend geometry.",
                    ),
                ),
                provenance=provenance,
            )

    marks: list[BarMarkSummary] = []
    for mark in sorted({path.bar_mark for path in resolved}):
        marked = [path for path in resolved if path.bar_mark == mark]
        exemplar = marked[0]
        if any(
            not _same_shape(exemplar, other, request.geometry_tolerance_mm)
            for other in marked[1:]
        ):
            return rejected_result(
                RESOLVE_BAR_PATHS_OPERATION,
                inputs,
                (
                    _diagnostic(
                        "MARK.GEOMETRY_CONFLICT",
                        "One bar mark cannot identify different fabrication geometry or material.",
                        f"paths[mark={mark}]",
                        "Assign separate marks to paths with different shapes, roles, diameters, grades, or bundles.",
                    ),
                ),
                provenance=provenance,
            )
        marks.append(
            BarMarkSummary(
                mark,
                exemplar.role,
                exemplar.diameter_mm,
                exemplar.steel_grade_n_per_mm2,
                exemplar.bundle_size,
                exemplar.closed,
                tuple(path.bar_id for path in marked),
                len(marked),
                exemplar.developed_centreline_length_mm,
                exemplar.compatible_stock_length_mm,
            )
        )

    diagnostics = [
        _diagnostic(
            "PATH.STOCK_LENGTH_EXCEEDED",
            f"Resolved path {path.bar_id} exceeds every supplied stock length.",
            f"paths[{path.bar_id}]",
            "Split the physical bar with an explicit checked splice or revise the stock catalogue.",
        )
        for path in resolved
        if path.compatible_stock_length_mm is None
    ]
    passed = not diagnostics
    output = BarPathOutput(
        request.profile_id,
        request.project_basis_id,
        request.criteria_revision_id,
        request.member_id,
        request.physical_span_id,
        request.topology_revision_id,
        request.detail_revision_id,
        request.coordinate_system,
        tuple(resolved),
        tuple(marks),
        passed,
    )
    return completed_result(
        RESOLVE_BAR_PATHS_OPERATION,
        inputs,
        {"reinforcement_schedule": output},
        engineering=(EngineeringState.PASS if passed else EngineeringState.FAIL),
        diagnostics=diagnostics,
        provenance=provenance,
    )


__all__ = [
    "BarMarkSummary",
    "BarPathOutput",
    "BarPathRequest",
    "BarPathRole",
    "BarPathSeed",
    "BendKind",
    "MemberLocalCoordinateSystem",
    "MemberLocalVector",
    "PathNode",
    "PathPoint",
    "PathSegmentKind",
    "ResolvedBarPath",
    "ResolvedPathSegment",
    "resolve_bar_paths",
]
