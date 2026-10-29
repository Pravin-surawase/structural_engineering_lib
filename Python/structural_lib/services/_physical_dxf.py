"""Physical beam drawing projection from the immutable WP06/WP07 package.

Geometry is resolved by the beam operation. This module only projects those
centreline paths; it does not infer a layer, a bend, an approval or a cut length.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

from structural_lib.beam import bar_paths as paths
from structural_lib.beam import semantics
from structural_lib.reporting import calculation_package as packages

_APPID = "STRUCTLIB_PHYSICAL"


def _xyz(point: paths.PathPoint) -> tuple[float, float, float]:
    return (
        point.station_x_mm,
        point.section_x_from_left_mm,
        point.section_y_from_top_mm,
    )


def _segment_points(
    segment: paths.ResolvedPathSegment, sagitta: float
) -> list[tuple[float, float, float]]:
    start, end = _xyz(segment.start), _xyz(segment.end)
    if segment.kind is paths.PathSegmentKind.TANGENT_STRAIGHT:
        return [start, end]
    if (
        segment.bend_centre is None
        or segment.bend_plane_normal is None
        or segment.bend_radius_mm is None
        or segment.bend_sweep_degrees is None
    ):
        raise ValueError("Resolved arc is missing its centre/radius/normal/sweep")
    centre = _xyz(segment.bend_centre)
    normal = segment.bend_plane_normal
    n = (
        normal.station_component,
        normal.section_horizontal_component,
        normal.section_vertical_component,
    )
    norm = math.sqrt(sum(v * v for v in n))
    if norm == 0 or segment.bend_radius_mm <= 0:
        raise ValueError("Resolved arc has an invalid plane or radius")
    n = (n[0] / norm, n[1] / norm, n[2] / norm)
    u = (start[0] - centre[0], start[1] - centre[1], start[2] - centre[2])
    v = (
        n[1] * u[2] - n[2] * u[1],
        n[2] * u[0] - n[0] * u[2],
        n[0] * u[1] - n[1] * u[0],
    )
    sweep = math.radians(segment.bend_sweep_degrees)
    step = 2 * math.acos(max(-1.0, 1 - min(sagitta / segment.bend_radius_mm, 1.0)))
    count = max(1, math.ceil(abs(sweep) / step))

    def rotated(i: int) -> tuple[float, float, float]:
        c, s = math.cos(sweep * i / count), math.sin(sweep * i / count)
        return (
            centre[0] + u[0] * c + v[0] * s,
            centre[1] + u[1] * c + v[1] * s,
            centre[2] + u[2] * c + v[2] * s,
        )

    points = [rotated(i) for i in range(count + 1)]
    if math.dist(points[-1], end) > 1e-6:
        raise ValueError("Resolved arc endpoint does not agree with its stored sweep")
    points[0], points[-1] = start, end
    return points


def _binding_inputs(
    path_result: semantics.OperationResult, package_result: semantics.OperationResult
) -> tuple[paths.BarPathOutput, packages.CalculationPackageOutput, dict[str, Any]]:
    if (
        path_result.operation_semantic_id != paths.RESOLVE_BAR_PATHS_OPERATION
        or path_result.execution is not semantics.ExecutionState.COMPLETED
        or path_result.engineering is not semantics.EngineeringState.PASS
        or path_result.freshness is not semantics.FreshnessState.CURRENT
        or package_result.execution is not semantics.ExecutionState.COMPLETED
        or package_result.freshness is not semantics.FreshnessState.CURRENT
    ):
        raise ValueError(
            "Physical drawing requires completed current paths and package"
        )
    if (
        semantics.semantic_hash("normalized_input_id", path_result.effective_inputs)
        != path_result.normalized_input_id
    ):
        raise ValueError("Path input identity does not match its physical dimensions")
    schedule = path_result.output_as("reinforcement_schedule", paths.BarPathOutput)
    package = package_result.output_as(
        "calculation_package", packages.CalculationPackageOutput
    )
    binding = packages.result_binding(path_result, "reinforcement_schedule")
    if not schedule.passed or binding not in package.dependency_bindings:
        raise ValueError("Calculation package does not bind the current path result")
    if package.reinforcement_schedule != schedule:
        raise ValueError("Calculation package and physical schedule differ")
    bbs = package.bbs
    if (
        bbs.schedule_result_id != path_result.result_id
        or package.metadata.member_id != schedule.member_id
        or any(
            getattr(bbs, k) != getattr(schedule, k)
            for k in (
                "profile_id",
                "project_basis_id",
                "member_id",
                "detail_revision_id",
            )
        )
    ):
        raise ValueError(
            "BBS/member/detail identity differs from the physical schedule"
        )
    source_ids = [bar_id for row in bbs.rows for bar_id in row.source_path_ids]
    if Counter(source_ids) != Counter(bar.bar_id for bar in schedule.paths):
        raise ValueError("Physical BBS source paths do not match the drawing schedule")
    request = path_result.effective_inputs["request"]["value"]
    return schedule, package, dict(request)


def write_physical_dxf(
    path_result: semantics.OperationResult,
    package_result: semantics.OperationResult,
    output_path: str | Path,
    *,
    section_station_mm: float | None = None,
    max_arc_sagitta_mm: float = 0.02,
) -> str:
    """Write source-bound 3D paths and labelled 2D views in millimetres.

    The section is a true cut through straight longitudinal segments. A link
    panel is explicitly a projection of an identified physical path, since
    the accepted closure can span more than one station plane. Curved section
    intersections are not inferred. Arc projections are tessellated with a
    caller-visible maximum 3D sagitta, never a fabricated hook approximation.
    """
    import ezdxf

    if not math.isfinite(max_arc_sagitta_mm) or max_arc_sagitta_mm <= 0:
        raise ValueError("Arc sagitta must be a positive finite value in mm")
    schedule, package, request = _binding_inputs(path_result, package_result)
    left, right = request["member_start_x_mm"], request["member_end_x_mm"]
    width, depth = request["section_width_mm"], request["section_depth_mm"]
    station = (left + right) / 2 if section_station_mm is None else section_station_mm
    if not math.isfinite(station) or not left <= station <= right:
        raise ValueError("Section station must lie in the resolved member extent")

    # Finish all geometric/admission work before writing a document.
    polylines: list[tuple[paths.ResolvedBarPath, list[tuple[float, float, float]]]] = []
    section: list[tuple[paths.ResolvedBarPath, tuple[float, float]]] = []
    for bar in schedule.paths:
        vertices: list[tuple[float, float, float]] = []
        hits: list[tuple[float, float]] = []
        for segment in bar.segments:
            points = _segment_points(segment, max_arc_sagitta_mm)
            vertices.extend(points if not vertices else points[1:])
            if bar.role is paths.BarPathRole.TRANSVERSE_LINK:
                continue
            a, b = _xyz(segment.start), _xyz(segment.end)
            if segment.kind is paths.PathSegmentKind.BEND_ARC:
                if (
                    min(p[0] for p in points) - max_arc_sagitta_mm
                    <= station
                    <= max(p[0] for p in points) + max_arc_sagitta_mm
                ):
                    raise ValueError(
                        "A curved longitudinal section crossing needs an explicit resolved cut"
                    )
            elif a[0] != b[0] and min(a[0], b[0]) <= station <= max(a[0], b[0]):
                ratio = (station - a[0]) / (b[0] - a[0])
                hit = (a[1] + ratio * (b[1] - a[1]), a[2] + ratio * (b[2] - a[2]))
                if not any(math.dist(hit, p) < 1e-6 for p in hits):
                    hits.append(hit)
        polylines.append((bar, vertices))
        section.extend((bar, point) for point in hits)

    doc = ezdxf.new("R2010")
    doc.units = 4  # DXF INSUNITS: millimetres.
    doc.appids.new(_APPID)
    for name, color in (
        ("PHYSICAL_3D", 8),
        ("ELEVATION_LONGITUDINAL", 1),
        ("ELEVATION_LINKS", 3),
        ("LONGITUDINAL_SECTION", 1),
        ("LINK_PATH_PROJECTION", 3),
        ("OUTLINE", 7),
        ("TEXT", 7),
    ):
        doc.layers.new(name, dxfattribs={"color": color})
    doc.layers.get("PHYSICAL_3D").off()
    msp = doc.modelspace()

    def tag(entity: Any, bar: paths.ResolvedBarPath, kind: str) -> None:
        entity.set_xdata(
            _APPID,
            [
                (1000, kind),
                (1000, bar.bar_id),
                (1000, bar.bar_mark),
                (1000, bar.role.value),
                (1070, bar.layer),
                (1040, bar.diameter_mm),
                (1000, path_result.result_id),
            ],
        )

    def text(value: str, at: tuple[float, float], height: float = 70) -> None:
        msp.add_text(
            value, dxfattribs={"height": height, "insert": at, "layer": "TEXT"}
        )

    def outline(x: float, y: float, w: float, h: float) -> None:
        msp.add_lwpolyline(
            [(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
            close=True,
            dxfattribs={"layer": "OUTLINE"},
        )

    outline(left, 0, right - left, depth)
    text(
        f"{schedule.member_id} | {package.issue_state.upper()} | physical paths | mm",
        (left, depth + 650),
        110,
    )
    text(
        f"Member {width:g} x {depth:g} mm; station extents {left:g} to {right:g} mm",
        (left, depth + 490),
    )
    text(
        f"Schedule {schedule.detail_revision_id}; {len(schedule.paths)} physical bars",
        (left, depth + 340),
    )
    text(
        f"Professional approval: {'recorded' if package.active_approval else 'none'}; digital review drawing",
        (left, depth + 190),
    )
    text("ELEVATION - all resolved centreline paths", (left, -140))
    for bar, vertices in polylines:
        tag(
            msp.add_polyline3d(
                [(x, y, depth - z) for x, y, z in vertices],
                dxfattribs={"layer": "PHYSICAL_3D"},
            ),
            bar,
            "path_3d",
        )
        layer = (
            "ELEVATION_LINKS"
            if bar.role is paths.BarPathRole.TRANSVERSE_LINK
            else "ELEVATION_LONGITUDINAL"
        )
        tag(
            msp.add_lwpolyline(
                [(x, depth - z) for x, _, z in vertices], dxfattribs={"layer": layer}
            ),
            bar,
            "elevation",
        )

    scale = 3.0
    section_x = right + 500
    outline(section_x, 0, width * scale, depth * scale)
    text("LONGITUDINAL CUT", (section_x, depth * scale + 210))
    text(
        f"Station {station:g} mm; view x{scale:g}", (section_x, depth * scale + 100), 55
    )
    for bar, (x, y) in section:
        centre = (section_x + x * scale, (depth - y) * scale)
        tag(
            msp.add_circle(
                centre,
                bar.diameter_mm * scale / 2,
                dxfattribs={"layer": "LONGITUDINAL_SECTION"},
            ),
            bar,
            "longitudinal_section",
        )
        text(
            f"{bar.bar_id} T{bar.diameter_mm:g}",
            (centre[0] + bar.diameter_mm * scale / 2 + 20, centre[1] + 30),
            55,
        )

    link_groups: dict[
        str, tuple[paths.ResolvedBarPath, list[tuple[float, float, float]]]
    ] = {}
    for bar, vertices in polylines:
        if bar.role is paths.BarPathRole.TRANSVERSE_LINK:
            link_groups.setdefault(bar.bar_mark, (bar, vertices))
    link_x = section_x + width * scale + 450
    for i, (bar, vertices) in enumerate(link_groups.values()):
        x0 = link_x + i * (width * scale + 350)
        tag(
            msp.add_lwpolyline(
                [(x0 + y * scale, (depth - z) * scale) for _, y, z in vertices],
                dxfattribs={"layer": "LINK_PATH_PROJECTION"},
            ),
            bar,
            "link_projection",
        )
        text("LINK PATH PROJECTION", (x0, depth * scale + 210))
        text(f"{bar.bar_id}; view x{scale:g}", (x0, depth * scale + 100), 55)
        text("Closure uses actual 3D path; not a planar cut", (x0, -160), 55)

    y = -350
    for row in package.bbs.rows:
        text(
            f"{row.bar_mark}: {row.scheduled_bar_count} x T{row.diameter_mm:g}; cut {row.fabrication_cut_length_each_mm:.3f} mm; mass {row.theoretical_mass_kg:.3f} kg",
            (left, y),
            60,
        )
        y -= 110
    text(
        f"Steel total {package.bbs.scheduled_steel_mass_kg:.3f} kg; issue state {package.issue_state}",
        (left, y - 30),
        70,
    )
    metadata = {
        "schema_version": "physical-beam-dxf/v1",
        "member_id": schedule.member_id,
        "package_id": package.calculation_package_id,
        "path_result_id": path_result.result_id,
        "schedule_payload_id": packages.result_binding(
            path_result, "reinforcement_schedule"
        ).output_payload_id,
        "detail_revision_id": schedule.detail_revision_id,
        "issue_state": package.issue_state,
        "active_approval": package.active_approval,
        "section_station_mm": station,
        "section_origin_x_mm": section_x,
        "section_view_scale": scale,
        "max_arc_sagitta_mm": max_arc_sagitta_mm,
        "units": "mm",
        "source_path_ids": [b.bar_id for b in schedule.paths],
    }
    encoded = json.dumps(metadata, sort_keys=True, separators=(",", ":"))
    record = doc.rootdict.add_xrecord("STRUCTLIB_PHYSICAL_METADATA")
    record.extend((1000, encoded[i : i + 240]) for i in range(0, len(encoded), 240))
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(str(target))
    return str(target)
