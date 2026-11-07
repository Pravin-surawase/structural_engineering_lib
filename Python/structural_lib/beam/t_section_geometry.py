"""Actual T material, cover, and identity-bound projection to a web cage.

The global section datum is the left edge/top of the owned physical flange.
Rectangular web helpers receive an explicit translated copy; a rectangular
path envelope never establishes that steel lies in the actual T material.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

from .bar_paths import (
    BarPathOutput,
    BarPathRequest,
    BarPathRole,
    ResolvedPathSegment,
    resolve_bar_paths,
)
from .reinforcement import BarPosition, Face, ReinforcementGeometryRequest
from .semantics import (
    Diagnostic,
    EngineeringState,
    OperationResult,
    Provenance,
    completed_result,
    effective_inputs,
    not_evaluated_result,
    partial_result,
    rejected_result,
)

T_GEOMETRY_OPERATION = "structural.beam.t_geometry.check/v1"
T_GEOMETRY_REVISION = "physical-t-section-e-v1"


@dataclass(frozen=True)
class TSectionGeometry:
    section_id: str
    geometry_revision_id: str
    web_width_mm: float
    depth_mm: float
    flange_width_physical_mm: float
    flange_thickness_mm: float
    web_left_from_flange_left_mm: float

    @property
    def area_mm2(self) -> float:
        return (
            self.flange_width_physical_mm * self.flange_thickness_mm
            + self.web_width_mm * (self.depth_mm - self.flange_thickness_mm)
        )

    @property
    def outline(self) -> tuple[tuple[float, float], ...]:
        left = self.web_left_from_flange_left_mm
        right = left + self.web_width_mm
        return (
            (0, 0),
            (self.flange_width_physical_mm, 0),
            (self.flange_width_physical_mm, self.flange_thickness_mm),
            (right, self.flange_thickness_mm),
            (right, self.depth_mm),
            (left, self.depth_mm),
            (left, self.flange_thickness_mm),
            (0, self.flange_thickness_mm),
        )


@dataclass(frozen=True)
class TGeometryCheckRequest:
    profile_id: str
    member_id: str
    reinforcement_revision_id: str
    section: TSectionGeometry
    expected_geometry_revision_id: str
    nominal_cover_mm: float
    link_diameter_mm: float
    minimum_clear_spacing_mm: float
    bars: tuple[BarPosition, ...]
    paths: BarPathRequest


def _diagnostic(code: str, field: str, message: str) -> Diagnostic:
    return Diagnostic(
        code,
        "error",
        message,
        T_GEOMETRY_OPERATION,
        field,
        "physical-T-material",
        "Supply the same actual T geometry, steel and current detail/path identities.",
    )


def _provenance() -> Provenance:
    return Provenance(
        T_GEOMETRY_REVISION,
        T_GEOMETRY_REVISION,
        ("Physical T-union geometry; IS456 26.4 cover and explicit flange/web datum",),
    )


def valid_t_section(section: TSectionGeometry) -> bool:
    values = (
        section.web_width_mm,
        section.depth_mm,
        section.flange_width_physical_mm,
        section.flange_thickness_mm,
        section.web_left_from_flange_left_mm,
    )
    return (
        bool(section.section_id and section.geometry_revision_id)
        and all(math.isfinite(v) for v in values)
        and 0 < section.web_width_mm < section.flange_width_physical_mm
        and 0 < section.flange_thickness_mm < section.depth_mm
        and 0
        < section.web_left_from_flange_left_mm
        < section.flange_width_physical_mm - section.web_width_mm
    )


def _cover_distance(section: TSectionGeometry, x: float, y: float) -> float:
    left = section.web_left_from_flange_left_mm
    inside = (
        0 <= y <= section.flange_thickness_mm
        and 0 <= x <= section.flange_width_physical_mm
    ) or (0 <= y <= section.depth_mm and left <= x <= left + section.web_width_mm)
    minimum = math.inf
    outline = section.outline
    for (x0, y0), (x1, y1) in zip(outline, outline[1:] + outline[:1], strict=True):
        dx, dy = x1 - x0, y1 - y0
        t = min(1.0, max(0.0, ((x - x0) * dx + (y - y0) * dy) / (dx * dx + dy * dy)))
        minimum = min(minimum, math.hypot(x - x0 - t * dx, y - y0 - t * dy))
    return minimum if inside else -minimum


def _arc_parameters(
    segment: ResolvedPathSegment,
) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float], float] | None:
    centre, normal = segment.bend_centre, segment.bend_plane_normal
    if centre is None or normal is None or segment.bend_sweep_degrees is None:
        return None
    u = (
        segment.start.station_x_mm - centre.station_x_mm,
        segment.start.section_x_from_left_mm - centre.section_x_from_left_mm,
        segment.start.section_y_from_top_mm - centre.section_y_from_top_mm,
    )
    n = (
        normal.station_component,
        normal.section_horizontal_component,
        normal.section_vertical_component,
    )
    v = (
        n[1] * u[2] - n[2] * u[1],
        n[2] * u[0] - n[0] * u[2],
        n[0] * u[1] - n[1] * u[0],
    )
    return (
        (centre.section_x_from_left_mm, centre.section_y_from_top_mm),
        (u[1], u[2]),
        (v[1], v[2]),
        math.radians(segment.bend_sweep_degrees),
    )


def _segment_boxes(
    segment: ResolvedPathSegment,
) -> tuple[tuple[float, float, float, float], ...]:
    arc = _arc_parameters(segment)
    if arc is None:
        return (
            (
                min(
                    segment.start.section_x_from_left_mm,
                    segment.end.section_x_from_left_mm,
                ),
                max(
                    segment.start.section_x_from_left_mm,
                    segment.end.section_x_from_left_mm,
                ),
                min(
                    segment.start.section_y_from_top_mm,
                    segment.end.section_y_from_top_mm,
                ),
                max(
                    segment.start.section_y_from_top_mm,
                    segment.end.section_y_from_top_mm,
                ),
            ),
        )
    centre, u, v, sweep = arc
    boxes: list[tuple[float, float, float, float]] = []
    for i in range(32):
        a, b = sweep * i / 32, sweep * (i + 1) / 32
        bounds: list[float] = []
        for axis in range(2):
            angles = [a, b]
            extremum = math.atan2(v[axis], u[axis])
            angles.extend(
                extremum + k * math.pi
                for k in range(-2, 4)
                if a < extremum + k * math.pi < b
            )
            values = [
                centre[axis] + u[axis] * math.cos(t) + v[axis] * math.sin(t)
                for t in angles
            ]
            bounds.extend((min(values), max(values)))
        boxes.append((bounds[0], bounds[1], bounds[2], bounds[3]))
    return tuple(boxes)


def _segment_station_bounds(segment: ResolvedPathSegment) -> tuple[float, float]:
    centre, normal = segment.bend_centre, segment.bend_plane_normal
    if centre is None or normal is None or segment.bend_sweep_degrees is None:
        return min(segment.start.station_x_mm, segment.end.station_x_mm), max(
            segment.start.station_x_mm, segment.end.station_x_mm
        )
    u = segment.start.station_x_mm - centre.station_x_mm
    v = normal.section_horizontal_component * (
        segment.start.section_y_from_top_mm - centre.section_y_from_top_mm
    ) - normal.section_vertical_component * (
        segment.start.section_x_from_left_mm - centre.section_x_from_left_mm
    )
    sweep = math.radians(segment.bend_sweep_degrees)
    angles = [0.0, sweep]
    extremum = math.atan2(v, u)
    angles.extend(
        extremum + k * math.pi
        for k in range(-2, 4)
        if 0 < extremum + k * math.pi < sweep
    )
    values = [centre.station_x_mm + u * math.cos(t) + v * math.sin(t) for t in angles]
    return min(values), max(values)


def _box_certified(
    section: TSectionGeometry, box: tuple[float, float, float, float], margin: float
) -> bool:
    xmin, xmax, ymin, ymax = box
    left = section.web_left_from_flange_left_mm
    # Each expanded analytic box must fit wholly in a convex material piece.
    # This is a sufficient whole-curve proof, not a sampled-point inference.
    in_flange = (
        xmin >= margin - 1e-8
        and xmax <= section.flange_width_physical_mm - margin + 1e-8
        and ymin >= margin - 1e-8
        and ymax <= section.flange_thickness_mm - margin + 1e-8
    )
    in_web = (
        xmin >= left + margin - 1e-8
        and xmax <= left + section.web_width_mm - margin + 1e-8
        and ymin >= margin - 1e-8
        and ymax <= section.depth_mm - margin + 1e-8
    )
    return in_flange or in_web


def check_t_geometry(request: TGeometryCheckRequest) -> OperationResult:
    """Qualify actual material/cover and emit an explicit web-local projection.

    Whole-curve analytic bounds certify the selected web cage. A curve that
    needs a more general reentrant-corner certificate retains HOLD; it cannot
    gain a material PASS from nodes or its rectangular section envelope.
    """
    op, provenance = T_GEOMETRY_OPERATION, _provenance()
    inputs = effective_inputs(request=request)
    section, paths = request.section, request.paths
    if not valid_t_section(section) or not all(
        math.isfinite(v) and v > 0
        for v in (
            request.nominal_cover_mm,
            request.link_diameter_mm,
            request.minimum_clear_spacing_mm,
        )
    ):
        return rejected_result(
            op,
            inputs,
            (
                _diagnostic(
                    "T_GEOMETRY.INPUT",
                    "section",
                    "Finite physical T dimensions and cover are required.",
                ),
            ),
            provenance=provenance,
        )
    if (
        not request.profile_id
        or not request.member_id
        or not request.reinforcement_revision_id
        or request.expected_geometry_revision_id != section.geometry_revision_id
        or paths.profile_id != request.profile_id
        or paths.member_id != request.member_id
        or paths.detail_revision_id != request.reinforcement_revision_id
        or paths.section_width_mm != section.flange_width_physical_mm
        or paths.section_depth_mm != section.depth_mm
    ):
        return not_evaluated_result(
            op,
            inputs,
            _diagnostic(
                "T_GEOMETRY.IDENTITY",
                "request",
                "Current matching section/detail identities and the physical flange envelope are required.",
            ),
            provenance=provenance,
        )
    resolved = resolve_bar_paths(paths)
    if resolved.execution != "completed" or resolved.engineering != "pass":
        return not_evaluated_result(
            op,
            inputs,
            _diagnostic(
                "T_GEOMETRY.PATHS",
                "paths",
                "Valid actual fabricated paths are required before T-material certification.",
            ),
            provenance=provenance,
        )
    schedule = resolved.output_as("reinforcement_schedule", BarPathOutput)
    diagnostics = []
    checks = []
    for bar in request.bars:
        cover = (
            _cover_distance(section, bar.x_from_left_mm, bar.y_from_top_mm)
            - bar.diameter_mm / 2
        )
        required_cover = request.nominal_cover_mm + request.link_diameter_mm
        passed = cover >= required_cover - 1e-8
        checks.append(
            {
                "bar_id": bar.bar_id,
                "physical_cover_mm": cover,
                "required_bar_cover_including_link_mm": required_cover,
                "passed": passed,
            }
        )
        if not passed:
            diagnostics.append(
                _diagnostic(
                    "T_GEOMETRY.BAR_COVER",
                    bar.bar_id,
                    "The actual bar surface lies outside T material or violates physical cover.",
                )
            )
    uncertified = []
    for path in schedule.paths:
        margin = request.nominal_cover_mm + path.diameter_mm / 2
        if path.role in (BarPathRole.TOP_LONGITUDINAL, BarPathRole.BOTTOM_LONGITUDINAL):
            margin += request.link_diameter_mm
        for segment in path.segments:
            minimum_station, maximum_station = _segment_station_bounds(segment)
            # Bound continuous straight beam runs by their actual flat ends.
            # Link curves use a conservative complete bar-tube envelope.
            axial_margin = (
                request.nominal_cover_mm
                if path.role
                in (BarPathRole.TOP_LONGITUDINAL, BarPathRole.BOTTOM_LONGITUDINAL)
                else request.nominal_cover_mm + path.diameter_mm / 2
            )
            if (
                minimum_station < paths.member_start_x_mm + axial_margin - 1e-8
                or maximum_station > paths.member_end_x_mm - axial_margin + 1e-8
            ):
                diagnostics.append(
                    _diagnostic(
                        "T_GEOMETRY.END_COVER",
                        path.bar_id,
                        "The actual run/curve violates cover at a declared physical concrete end.",
                    )
                )
            if all(
                _box_certified(section, box, margin) for box in _segment_boxes(segment)
            ):
                continue
            points = (segment.start, segment.end)
            if any(
                _cover_distance(
                    section, p.section_x_from_left_mm, p.section_y_from_top_mm
                )
                < margin - 1e-8
                for p in points
            ):
                diagnostics.append(
                    _diagnostic(
                        "T_GEOMETRY.PATH_COVER",
                        path.bar_id,
                        "The actual resolved path violates T material/cover, including the empty shoulder region.",
                    )
                )
            else:
                uncertified.append(segment.segment_id)
    offset = section.web_left_from_flange_left_mm
    projected_bars = tuple(
        replace(bar, x_from_left_mm=bar.x_from_left_mm - offset) for bar in request.bars
    )
    projected_paths = replace(
        paths,
        section_width_mm=section.web_width_mm,
        coordinate_system=replace(
            paths.coordinate_system, datum_id=paths.coordinate_system.datum_id + ":web"
        ),
        paths=tuple(
            replace(
                seed,
                nodes=tuple(
                    replace(
                        node,
                        point=replace(
                            node.point,
                            section_x_from_left_mm=node.point.section_x_from_left_mm
                            - offset,
                        ),
                    )
                    for node in seed.nodes
                ),
            )
            for seed in paths.paths
        ),
    )
    # This initial profile admits beam bars in a web cage. Separately owned
    # slab-strip steel is checked by its own owner, never projected into it.
    beam_ids = {bar.bar_id for bar in request.bars}
    path_by_id = {seed.bar_id: seed for seed in paths.paths}
    longitudinal_ids = {
        seed.bar_id
        for seed in paths.paths
        if seed.role in (BarPathRole.TOP_LONGITUDINAL, BarPathRole.BOTTOM_LONGITUDINAL)
    }
    binding = (
        bool(beam_ids)
        and len(beam_ids) == len(request.bars)
        and longitudinal_ids == beam_ids
    )
    binding = binding and all(
        seed.role
        in (
            BarPathRole.TOP_LONGITUDINAL,
            BarPathRole.BOTTOM_LONGITUDINAL,
            BarPathRole.TRANSVERSE_LINK,
        )
        for seed in paths.paths
    )
    for bar in request.bars:
        seed = path_by_id.get(bar.bar_id)
        binding = binding and seed is not None
        if seed is not None:
            expected_role = (
                BarPathRole.TOP_LONGITUDINAL
                if bar.face is Face.TOP
                else BarPathRole.BOTTOM_LONGITUDINAL
            )
            binding = (
                binding
                and seed.role is expected_role
                and seed.diameter_mm == bar.diameter_mm
                and all(
                    node.point.section_x_from_left_mm == bar.x_from_left_mm
                    and node.point.section_y_from_top_mm == bar.y_from_top_mm
                    for node in seed.nodes
                )
            )
    if not binding:
        diagnostics.append(
            _diagnostic(
                "T_GEOMETRY.BAR_PATH_BINDING",
                "bars,paths",
                "All actual beam bars must retain the same IDs, sizes and positioned continuous paths.",
            )
        )
    outputs = {
        "section_id": section.section_id,
        "geometry_revision_id": section.geometry_revision_id,
        "reinforcement_revision_id": request.reinforcement_revision_id,
        "outline_mm": section.outline,
        "physical_area_mm2": section.area_mm2,
        "web_left_offset_mm": offset,
        "global_path_result_id": resolved.result_id,
        "checks": checks,
        "uncertified_segment_ids": uncertified,
        "web_geometry": ReinforcementGeometryRequest(
            request.profile_id,
            section.web_width_mm,
            section.depth_mm,
            request.nominal_cover_mm,
            request.link_diameter_mm,
            request.minimum_clear_spacing_mm,
            projected_bars,
        ),
        "web_paths": projected_paths,
        "projection_round_trip_pass": all(
            math.isclose(
                projected.x_from_left_mm + offset, original.x_from_left_mm, abs_tol=1e-9
            )
            for projected, original in zip(projected_bars, request.bars, strict=True)
        ),
    }
    if uncertified and not diagnostics:
        return partial_result(
            op,
            inputs,
            outputs,
            (
                _diagnostic(
                    "T_GEOMETRY.CURVE_CERTIFICATE",
                    "paths",
                    "A whole-curve T-material certificate is missing for the named reentrant-region segments.",
                ),
            ),
            provenance=provenance,
        )
    return completed_result(
        op,
        inputs,
        outputs,
        engineering=EngineeringState.FAIL if diagnostics else EngineeringState.PASS,
        diagnostics=diagnostics,
        provenance=provenance,
    )
