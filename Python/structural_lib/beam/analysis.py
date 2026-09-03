"""Vendor-neutral actions, beam topology, and bounded planar beam analysis.

The module is host-free.  It does not acquire ETABS data, read workbooks, or
claim equivalence with a global frame model.  The beam solver uses N, mm,
N/mm2, and mm4 internally with upward force and sagging-positive moment.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from .semantics import (
    Diagnostic,
    EngineeringState,
    OperationResult,
    Provenance,
    completed_result,
    effective_inputs,
    rejected_result,
    semantic_hash,
)

ACTION_NORMALIZE_OPERATION = "structural.action_snapshot.normalize/v1"
BEAM_LINE_SOLVE_OPERATION = "structural.beam_line.solve/v1"
TOPOLOGY_OPERATION = "structural.beam_topology.define/v1"
METHOD_REVISION = "structural-analysis-wp03-v1"


class ForceUnit(StrEnum):
    N = "n"
    KN = "kn"


class MomentUnit(StrEnum):
    N_MM = "n_mm"
    N_M = "n_m"
    KN_MM = "kn_mm"
    KN_M = "kn_m"


class LengthUnit(StrEnum):
    MM = "mm"
    M = "m"


class ActionConcurrency(StrEnum):
    STATIC_CONCURRENT = "static_concurrent"
    STAGED_STEP = "staged_step"
    RESPONSE_RESULT = "response_result"
    COMPONENT_ENVELOPE = "component_envelope"
    DESIGN_ENVELOPE = "design_envelope"


@dataclass(frozen=True)
class Vector3:
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class LocalAxes:
    axis_id: str
    e1: Vector3
    e2: Vector3
    e3: Vector3


@dataclass(frozen=True)
class RawActionRow:
    source_row_id: str
    member_id: str
    physical_span_id: str
    object_id: str
    analysis_element_id: str
    axis_id: str
    object_station: float
    element_station: float
    load_case_id: str
    step_type: str
    step_number: float | None
    concurrency: ActionConcurrency
    p: float
    v2: float
    v3: float
    t: float
    m2: float
    m3: float


@dataclass(frozen=True)
class RawActionSnapshot:
    source_id: str
    model_id: str
    analysis_epoch_id: str
    result_epoch_id: str
    force_unit: ForceUnit
    moment_unit: MomentUnit
    station_unit: LengthUnit
    local_axes: tuple[LocalAxes, ...]
    rows: tuple[RawActionRow, ...]


@dataclass(frozen=True)
class PhysicalSupport:
    support_id: str
    centre_x_mm: float
    left_face_x_mm: float
    right_face_x_mm: float


@dataclass(frozen=True)
class SectionRegion:
    region_id: str
    section_id: str
    start_x_mm: float
    end_x_mm: float


@dataclass(frozen=True)
class PhysicalSpan:
    span_id: str
    start_support_id: str
    end_support_id: str
    effective_depth_mm: float
    section_regions: tuple[SectionRegion, ...]


@dataclass(frozen=True)
class AnalysisElementMapping:
    analysis_element_id: str
    physical_span_id: str
    start_x_mm: float
    end_x_mm: float


@dataclass(frozen=True)
class BeamTopologyRequest:
    member_id: str
    local_axes: LocalAxes
    supports: tuple[PhysicalSupport, ...]
    spans: tuple[PhysicalSpan, ...]
    analysis_elements: tuple[AnalysisElementMapping, ...]


@dataclass(frozen=True)
class BeamNode:
    node_id: str
    x_mm: float
    vertical_restraint: bool
    rotation_restraint: bool
    vertical_displacement_mm: float = 0.0
    prescribed_rotation_rad: float = 0.0
    nodal_force_n: float = 0.0
    nodal_moment_nmm: float = 0.0


@dataclass(frozen=True)
class BeamElement:
    analysis_element_id: str
    physical_span_id: str
    start_node_id: str
    end_node_id: str
    elastic_modulus_n_per_mm2: float
    second_moment_mm4: float
    uniform_load_n_per_mm: float = 0.0


@dataclass(frozen=True)
class BeamPointLoad:
    analysis_element_id: str
    distance_from_start_mm: float
    vertical_force_n: float


@dataclass(frozen=True)
class BeamLineRequest:
    model_id: str
    load_case_id: str
    nodes: tuple[BeamNode, ...]
    elements: tuple[BeamElement, ...]
    point_loads: tuple[BeamPointLoad, ...] = ()
    station_intervals: int = 20


def _provenance(method: str) -> Provenance:
    return Provenance(
        METHOD_REVISION,
        method,
        (
            "Euler-Bernoulli direct-stiffness formulation",
            "PF4 action identity and unit conventions",
        ),
    )


def _diagnostic(operation: str, code: str, message: str, field: str) -> Diagnostic:
    return Diagnostic(
        code,
        "error",
        message,
        operation,
        field,
        "structural-analysis",
        "Correct the declared bounded input and retry.",
    )


def _finite(value: float) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value)


def _vector_values(vector: Vector3) -> tuple[float, float, float]:
    return vector.x, vector.y, vector.z


def _validate_axes(axes: LocalAxes) -> str | None:
    if not axes.axis_id:
        return "axis_id is required"
    vectors = (_vector_values(axes.e1), _vector_values(axes.e2), _vector_values(axes.e3))
    if not all(_finite(value) for vector in vectors for value in vector):
        return "local axes must contain finite components"
    if any(abs(math.sqrt(math.fsum(value * value for value in vector)) - 1.0) > 1e-9 for vector in vectors):
        return "each local axis must be a unit vector"
    if any(abs(math.fsum(a * b for a, b in zip(vectors[i], vectors[j], strict=True))) > 1e-9 for i, j in ((0, 1), (0, 2), (1, 2))):
        return "local axes must be mutually perpendicular"
    cross = (
        vectors[0][1] * vectors[1][2] - vectors[0][2] * vectors[1][1],
        vectors[0][2] * vectors[1][0] - vectors[0][0] * vectors[1][2],
        vectors[0][0] * vectors[1][1] - vectors[0][1] * vectors[1][0],
    )
    if any(abs(a - b) > 1e-9 for a, b in zip(cross, vectors[2], strict=True)):
        return "local axes must be right-handed (e1 cross e2 equals e3)"
    return None


def _force_factor(unit: ForceUnit) -> float:
    return {ForceUnit.N: 1.0, ForceUnit.KN: 1_000.0}[unit]


def _moment_factor(unit: MomentUnit) -> float:
    return {
        MomentUnit.N_MM: 1.0,
        MomentUnit.N_M: 1_000.0,
        MomentUnit.KN_MM: 1_000.0,
        MomentUnit.KN_M: 1_000_000.0,
    }[unit]


def _length_factor(unit: LengthUnit) -> float:
    return {LengthUnit.MM: 1.0, LengthUnit.M: 1_000.0}[unit]


def normalize_action_snapshot(request: RawActionSnapshot) -> OperationResult:
    """Normalize units while preserving one same-row six-component identity."""

    inputs = effective_inputs(snapshot=request)
    provenance = _provenance("action-normalization-wp03-v1")
    identities = (
        request.source_id,
        request.model_id,
        request.analysis_epoch_id,
        request.result_epoch_id,
    )
    units_are_valid = (
        isinstance(request.force_unit, ForceUnit)
        and isinstance(request.moment_unit, MomentUnit)
        and isinstance(request.station_unit, LengthUnit)
    )
    if (
        not all(identities)
        or not request.rows
        or not request.local_axes
        or not units_are_valid
    ):
        return rejected_result(
            ACTION_NORMALIZE_OPERATION,
            inputs,
            (_diagnostic(ACTION_NORMALIZE_OPERATION, "INPUT.REQUIRED", "Snapshot identities, axes, and at least one row are required.", "snapshot"),),
            provenance=provenance,
        )
    axis_by_id: dict[str, LocalAxes] = {}
    for axes in request.local_axes:
        issue = _validate_axes(axes)
        if issue:
            return rejected_result(
                ACTION_NORMALIZE_OPERATION,
                inputs,
                (_diagnostic(ACTION_NORMALIZE_OPERATION, "AXIS.INVALID", issue, f"local_axes[{axes.axis_id}]"),),
                provenance=provenance,
            )
        if axes.axis_id in axis_by_id:
            return rejected_result(
                ACTION_NORMALIZE_OPERATION,
                inputs,
                (_diagnostic(ACTION_NORMALIZE_OPERATION, "IDENTITY.DUPLICATE", "Local axis ids must be unique.", "local_axes"),),
                provenance=provenance,
            )
        axis_by_id[axes.axis_id] = axes
    force_factor = _force_factor(request.force_unit)
    moment_factor = _moment_factor(request.moment_unit)
    station_factor = _length_factor(request.station_unit)
    rows: list[dict[str, Any]] = []
    seen_source_rows: set[str] = set()
    for source in request.rows:
        row_ids = (
            source.source_row_id,
            source.member_id,
            source.physical_span_id,
            source.object_id,
            source.analysis_element_id,
            source.axis_id,
            source.load_case_id,
            source.step_type,
        )
        values = (
            source.object_station,
            source.element_station,
            source.p,
            source.v2,
            source.v3,
            source.t,
            source.m2,
            source.m3,
        )
        if (
            not all(row_ids)
            or not isinstance(source.concurrency, ActionConcurrency)
            or not all(_finite(value) for value in values)
            or (source.step_number is not None and not _finite(source.step_number))
        ):
            return rejected_result(
                ACTION_NORMALIZE_OPERATION,
                inputs,
                (_diagnostic(ACTION_NORMALIZE_OPERATION, "INPUT.INVALID", "Every row requires finite components/stations and complete identity.", f"rows[{source.source_row_id}]"),),
                provenance=provenance,
            )
        if source.source_row_id in seen_source_rows:
            return rejected_result(
                ACTION_NORMALIZE_OPERATION,
                inputs,
                (_diagnostic(ACTION_NORMALIZE_OPERATION, "IDENTITY.DUPLICATE", "Source row ids must be unique within a snapshot.", "rows"),),
                provenance=provenance,
            )
        if source.axis_id not in axis_by_id:
            return rejected_result(
                ACTION_NORMALIZE_OPERATION,
                inputs,
                (_diagnostic(ACTION_NORMALIZE_OPERATION, "AXIS.MISSING", "The row axis id is not declared by the snapshot.", f"rows[{source.source_row_id}].axis_id"),),
                provenance=provenance,
            )
        seen_source_rows.add(source.source_row_id)
        normalized = {
            "source_row_id": source.source_row_id,
            "source_id": request.source_id,
            "model_id": request.model_id,
            "analysis_epoch_id": request.analysis_epoch_id,
            "result_epoch_id": request.result_epoch_id,
            "member_id": source.member_id,
            "physical_span_id": source.physical_span_id,
            "object_id": source.object_id,
            "analysis_element_id": source.analysis_element_id,
            "axis_id": source.axis_id,
            "object_station_mm": source.object_station * station_factor,
            "element_station_mm": source.element_station * station_factor,
            "load_case_id": source.load_case_id,
            "step_type": source.step_type,
            "step_number": source.step_number,
            "concurrency": source.concurrency,
            "p_n": source.p * force_factor,
            "v2_n": source.v2 * force_factor,
            "v3_n": source.v3 * force_factor,
            "t_nmm": source.t * moment_factor,
            "m2_nmm": source.m2 * moment_factor,
            "m3_nmm": source.m3 * moment_factor,
        }
        normalized["row_id"] = semantic_hash("action_row_id", normalized)
        rows.append(normalized)
    snapshot_value = {
        "source_id": request.source_id,
        "model_id": request.model_id,
        "analysis_epoch_id": request.analysis_epoch_id,
        "result_epoch_id": request.result_epoch_id,
        "unit_basis": "mm_n_nmm",
        "local_axes": request.local_axes,
        "rows": rows,
    }
    return completed_result(
        ACTION_NORMALIZE_OPERATION,
        inputs,
        {**snapshot_value, "snapshot_id": semantic_hash("action_snapshot_id", snapshot_value)},
        provenance=provenance,
    )


def define_beam_topology(request: BeamTopologyRequest) -> OperationResult:
    """Bind support faces, span measures, section regions, and analysis elements."""

    inputs = effective_inputs(request=request)
    provenance = _provenance("beam-topology-wp03-v1")
    axis_issue = _validate_axes(request.local_axes)
    if not request.member_id or axis_issue:
        return rejected_result(
            TOPOLOGY_OPERATION,
            inputs,
            (_diagnostic(TOPOLOGY_OPERATION, "AXIS.INVALID" if axis_issue else "INPUT.REQUIRED", axis_issue or "member_id is required", "local_axes" if axis_issue else "member_id"),),
            provenance=provenance,
        )
    if len(request.supports) < 2 or len(request.spans) != len(request.supports) - 1:
        return rejected_result(
            TOPOLOGY_OPERATION,
            inputs,
            (_diagnostic(TOPOLOGY_OPERATION, "TOPOLOGY.UNSUPPORTED", "An ordered beam line requires one span between every adjacent support.", "supports/spans"),),
            provenance=provenance,
        )
    if len({support.support_id for support in request.supports}) != len(request.supports) or len({span.span_id for span in request.spans}) != len(request.spans):
        return rejected_result(
            TOPOLOGY_OPERATION,
            inputs,
            (_diagnostic(TOPOLOGY_OPERATION, "IDENTITY.DUPLICATE", "Support and span ids must be unique.", "supports/spans"),),
            provenance=provenance,
        )
    supports = {support.support_id: support for support in request.supports}
    ordered = sorted(request.supports, key=lambda item: item.centre_x_mm)
    for support in ordered:
        values = (support.left_face_x_mm, support.centre_x_mm, support.right_face_x_mm)
        if not all(_finite(value) for value in values) or not values[0] < values[1] < values[2]:
            return rejected_result(
                TOPOLOGY_OPERATION,
                inputs,
                (_diagnostic(TOPOLOGY_OPERATION, "SUPPORT.GEOMETRY", "Each support needs ordered finite left-face, centre, and right-face coordinates.", f"supports[{support.support_id}]"),),
                provenance=provenance,
            )
    if tuple(ordered) != request.supports:
        return rejected_result(
            TOPOLOGY_OPERATION,
            inputs,
            (_diagnostic(TOPOLOGY_OPERATION, "TOPOLOGY.ORDER", "Supports must be supplied in increasing centre coordinate order.", "supports"),),
            provenance=provenance,
        )
    mapped_by_span: dict[str, list[AnalysisElementMapping]] = {}
    element_ids: set[str] = set()
    for item in request.analysis_elements:
        if item.analysis_element_id in element_ids or item.physical_span_id not in {span.span_id for span in request.spans}:
            return rejected_result(
                TOPOLOGY_OPERATION,
                inputs,
                (_diagnostic(TOPOLOGY_OPERATION, "ANALYSIS_MAPPING.INVALID", "Analysis element ids must be unique and reference a declared physical span.", "analysis_elements"),),
                provenance=provenance,
            )
        if not all(_finite(value) for value in (item.start_x_mm, item.end_x_mm)) or item.end_x_mm <= item.start_x_mm:
            return rejected_result(
                TOPOLOGY_OPERATION,
                inputs,
                (_diagnostic(TOPOLOGY_OPERATION, "ANALYSIS_MAPPING.INVALID", "Analysis element limits must be finite and increasing.", f"analysis_elements[{item.analysis_element_id}]"),),
                provenance=provenance,
            )
        element_ids.add(item.analysis_element_id)
        mapped_by_span.setdefault(item.physical_span_id, []).append(item)
    outputs: list[dict[str, Any]] = []
    region_ids = [
        region.region_id for span in request.spans for region in span.section_regions
    ]
    if (
        len(region_ids) != len(set(region_ids))
        or any(
            not region.region_id or not region.section_id
            for span in request.spans
            for region in span.section_regions
        )
    ):
        return rejected_result(
            TOPOLOGY_OPERATION,
            inputs,
            (
                _diagnostic(
                    TOPOLOGY_OPERATION,
                    "IDENTITY.DUPLICATE",
                    "Section region ids must be complete and unique.",
                    "spans.section_regions",
                ),
            ),
            provenance=provenance,
        )
    tolerance = 1e-6
    for index, span in enumerate(request.spans):
        start, end = supports.get(span.start_support_id), supports.get(span.end_support_id)
        expected_start, expected_end = request.supports[index], request.supports[index + 1]
        if start != expected_start or end != expected_end or not _finite(span.effective_depth_mm) or span.effective_depth_mm <= 0:
            return rejected_result(
                TOPOLOGY_OPERATION,
                inputs,
                (_diagnostic(TOPOLOGY_OPERATION, "SPAN.IDENTITY", "Each span must join its adjacent ordered supports and have positive effective depth.", f"spans[{span.span_id}]"),),
                provenance=provenance,
            )
        centreline = end.centre_x_mm - start.centre_x_mm
        clear = end.left_face_x_mm - start.right_face_x_mm
        if clear <= 0:
            return rejected_result(
                TOPOLOGY_OPERATION,
                inputs,
                (_diagnostic(TOPOLOGY_OPERATION, "SPAN.GEOMETRY", "Opposing support faces leave no positive clear span.", f"spans[{span.span_id}]"),),
                provenance=provenance,
            )
        for label, regions in (("section_regions", list(span.section_regions)), ("analysis_elements", mapped_by_span.get(span.span_id, []))):
            regions.sort(key=lambda item: item.start_x_mm)
            if not regions or abs(regions[0].start_x_mm - start.centre_x_mm) > tolerance or abs(regions[-1].end_x_mm - end.centre_x_mm) > tolerance or any(abs(a.end_x_mm - b.start_x_mm) > tolerance for a, b in zip(regions, regions[1:], strict=False)):
                return rejected_result(
                    TOPOLOGY_OPERATION,
                    inputs,
                    (_diagnostic(TOPOLOGY_OPERATION, "REGION.COVERAGE", f"{label} must cover the centreline span exactly without gaps or overlap.", f"spans[{span.span_id}].{label}"),),
                    provenance=provenance,
                )
        outputs.append(
            {
                "span_id": span.span_id,
                "start_support_id": start.support_id,
                "end_support_id": end.support_id,
                "start_support_right_face_x_mm": start.right_face_x_mm,
                "end_support_left_face_x_mm": end.left_face_x_mm,
                "clear_span_mm": clear,
                "centreline_span_mm": centreline,
                "effective_span_mm": min(centreline, clear + span.effective_depth_mm),
                "effective_span_rule": "min(centreline_span, clear_span + effective_depth)",
                "section_regions": span.section_regions,
                "analysis_elements": tuple(mapped_by_span[span.span_id]),
            }
        )
    topology = {
        "member_id": request.member_id,
        "local_axes": request.local_axes,
        "supports": request.supports,
        "spans": outputs,
    }
    return completed_result(
        TOPOLOGY_OPERATION,
        inputs,
        {**topology, "topology_id": semantic_hash("beam_topology_id", topology)},
        provenance=provenance,
    )


def _stiffness(length: float, ei: float) -> list[list[float]]:
    a, b, c, d = 12 * ei / length**3, 6 * ei / length**2, 4 * ei / length, 2 * ei / length
    return [[a, b, -a, b], [b, c, -b, d], [-a, -b, a, -b], [b, d, -b, c]]


def _matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [math.fsum(a * b for a, b in zip(row, vector, strict=True)) for row in matrix]


def _solve_positive_definite(matrix: list[list[float]], rhs: list[float]) -> list[float]:
    size = len(rhs)
    if not size:
        return []
    if any(matrix[i][i] <= 0 or not _finite(matrix[i][i]) for i in range(size)):
        raise ValueError("nonpositive stiffness diagonal")
    scale = [math.sqrt(matrix[i][i]) for i in range(size)]
    lower = [[0.0] * size for _ in range(size)]
    for i in range(size):
        for j in range(i + 1):
            value = matrix[i][j] / scale[i] / scale[j] - math.fsum(lower[i][k] * lower[j][k] for k in range(j))
            if i == j:
                if not _finite(value) or value <= 1e-12:
                    raise ValueError("scaled stiffness pivot indicates an unstable model")
                lower[i][j] = math.sqrt(value)
            else:
                lower[i][j] = value / lower[j][j]
    forward = [0.0] * size
    solved = [0.0] * size
    for i in range(size):
        forward[i] = (rhs[i] / scale[i] - math.fsum(lower[i][j] * forward[j] for j in range(i))) / lower[i][i]
    for i in reversed(range(size)):
        solved[i] = (forward[i] - math.fsum(lower[j][i] * solved[j] for j in range(i + 1, size))) / lower[i][i]
    return [solved[i] / scale[i] for i in range(size)]


def solve_beam_line(request: BeamLineRequest) -> OperationResult:
    """Solve a bounded prismatic planar beam line by direct stiffness."""

    inputs = effective_inputs(request=request)
    provenance = _provenance("euler-bernoulli-direct-stiffness-wp03-v1")
    if not request.model_id or not request.load_case_id or not 2 <= len(request.nodes) <= 20 or len(request.elements) != len(request.nodes) - 1 or not 2 <= request.station_intervals <= 100:
        return rejected_result(
            BEAM_LINE_SOLVE_OPERATION,
            inputs,
            (_diagnostic(BEAM_LINE_SOLVE_OPERATION, "PROFILE.UNSUPPORTED", "Require 2-20 ordered nodes, one element per adjacent node pair, and 2-100 station intervals.", "request"),),
            provenance=provenance,
        )
    if (
        any(not node.node_id for node in request.nodes)
        or any(
            not element.analysis_element_id or not element.physical_span_id
            for element in request.elements
        )
        or len({node.node_id for node in request.nodes}) != len(request.nodes)
        or len({element.analysis_element_id for element in request.elements})
        != len(request.elements)
    ):
        return rejected_result(
            BEAM_LINE_SOLVE_OPERATION,
            inputs,
            (_diagnostic(BEAM_LINE_SOLVE_OPERATION, "IDENTITY.DUPLICATE", "Node and analysis-element ids must be unique.", "nodes/elements"),),
            provenance=provenance,
        )
    nodes = request.nodes
    if any(not _finite(node.x_mm) for node in nodes) or any(b.x_mm <= a.x_mm for a, b in zip(nodes, nodes[1:], strict=False)):
        return rejected_result(
            BEAM_LINE_SOLVE_OPERATION,
            inputs,
            (_diagnostic(BEAM_LINE_SOLVE_OPERATION, "TOPOLOGY.ORDER", "Node coordinates must be finite and strictly increasing.", "nodes"),),
            provenance=provenance,
        )
    node_index = {node.node_id: i for i, node in enumerate(nodes)}
    points_by_element: dict[str, list[BeamPointLoad]] = {}
    for point in request.point_loads:
        points_by_element.setdefault(point.analysis_element_id, []).append(point)
    size = 2 * len(nodes)
    matrix = [[0.0] * size for _ in range(size)]
    force = [0.0] * size
    for i, node in enumerate(nodes):
        values = (node.vertical_displacement_mm, node.prescribed_rotation_rad, node.nodal_force_n, node.nodal_moment_nmm)
        if not all(_finite(value) for value in values) or (not node.vertical_restraint and node.vertical_displacement_mm != 0) or (not node.rotation_restraint and node.prescribed_rotation_rad != 0):
            return rejected_result(
                BEAM_LINE_SOLVE_OPERATION,
                inputs,
                (_diagnostic(BEAM_LINE_SOLVE_OPERATION, "SUPPORT.INVALID", "Prescribed movement requires its matching restraint and all node values must be finite.", f"nodes[{node.node_id}]"),),
                provenance=provenance,
            )
        force[2 * i] += node.nodal_force_n
        force[2 * i + 1] += node.nodal_moment_nmm
    element_data: list[dict[str, Any]] = []
    for index, element in enumerate(request.elements):
        if (element.start_node_id, element.end_node_id) != (nodes[index].node_id, nodes[index + 1].node_id) or not element.physical_span_id:
            return rejected_result(
                BEAM_LINE_SOLVE_OPERATION,
                inputs,
                (_diagnostic(BEAM_LINE_SOLVE_OPERATION, "TOPOLOGY.UNSUPPORTED", "Elements must connect each adjacent ordered node pair and retain physical-span identity.", f"elements[{element.analysis_element_id}]"),),
                provenance=provenance,
            )
        length = nodes[index + 1].x_mm - nodes[index].x_mm
        values = (element.elastic_modulus_n_per_mm2, element.second_moment_mm4, element.uniform_load_n_per_mm)
        if not all(_finite(value) for value in values) or values[0] <= 0 or values[1] <= 0:
            return rejected_result(
                BEAM_LINE_SOLVE_OPERATION,
                inputs,
                (_diagnostic(BEAM_LINE_SOLVE_OPERATION, "ELEMENT.INVALID", "E and I must be finite and positive and UDL must be finite.", f"elements[{element.analysis_element_id}]"),),
                provenance=provenance,
            )
        k = _stiffness(length, element.elastic_modulus_n_per_mm2 * element.second_moment_mm4)
        q = element.uniform_load_n_per_mm
        equivalent = [q * length / 2, q * length**2 / 12, q * length / 2, -q * length**2 / 12]
        points = points_by_element.pop(element.analysis_element_id, [])
        for point in points:
            if not _finite(point.distance_from_start_mm) or not _finite(point.vertical_force_n) or not 0 < point.distance_from_start_mm < length:
                return rejected_result(
                    BEAM_LINE_SOLVE_OPERATION,
                    inputs,
                    (_diagnostic(BEAM_LINE_SOLVE_OPERATION, "LOAD.POSITION", "Point loads must be finite and strictly inside their element.", f"point_loads[{element.analysis_element_id}]"),),
                    provenance=provenance,
                )
            ratio = point.distance_from_start_mm / length
            shape = (1 - 3 * ratio**2 + 2 * ratio**3, length * (ratio - 2 * ratio**2 + ratio**3), 3 * ratio**2 - 2 * ratio**3, length * (-(ratio**2) + ratio**3))
            for local in range(4):
                equivalent[local] += point.vertical_force_n * shape[local]
        dofs = (2 * index, 2 * index + 1, 2 * index + 2, 2 * index + 3)
        for a in range(4):
            force[dofs[a]] += equivalent[a]
            for b in range(4):
                matrix[dofs[a]][dofs[b]] += k[a][b]
        element_data.append({"element": element, "length": length, "stiffness": k, "equivalent": equivalent, "points": points, "dofs": dofs})
    if points_by_element:
        return rejected_result(
            BEAM_LINE_SOLVE_OPERATION,
            inputs,
            (_diagnostic(BEAM_LINE_SOLVE_OPERATION, "LOAD.IDENTITY", "A point load references an unknown analysis element.", "point_loads"),),
            provenance=provenance,
        )
    prescribed: dict[int, float] = {}
    for index, node in enumerate(nodes):
        if node.vertical_restraint:
            prescribed[2 * index] = node.vertical_displacement_mm
        if node.rotation_restraint:
            prescribed[2 * index + 1] = node.prescribed_rotation_rad
    free = [dof for dof in range(size) if dof not in prescribed]
    displacement = [0.0] * size
    for dof, value in prescribed.items():
        displacement[dof] = value
    rhs = [force[i] - math.fsum(matrix[i][j] * displacement[j] for j in prescribed) for i in free]
    try:
        values = _solve_positive_definite([[matrix[i][j] for j in free] for i in free], rhs)
    except (ArithmeticError, ValueError):
        return rejected_result(
            BEAM_LINE_SOLVE_OPERATION,
            inputs,
            (_diagnostic(BEAM_LINE_SOLVE_OPERATION, "ANALYSIS.UNSTABLE", "The declared restraints do not produce a stable positive-definite beam system.", "nodes"),),
            provenance=provenance,
        )
    for dof, value in zip(free, values, strict=True):
        displacement[dof] = value
    residual = [value - applied for value, applied in zip(_matvec(matrix, displacement), force, strict=True)]
    origin = nodes[0].x_mm
    node_results = []
    for index, node in enumerate(nodes):
        node_results.append(
            {
                "node_id": node.node_id,
                "x_mm": node.x_mm,
                "vertical_displacement_mm": displacement[2 * index],
                "rotation_rad": displacement[2 * index + 1],
                "vertical_reaction_n": residual[2 * index] if node.vertical_restraint else 0.0,
                "reaction_moment_nmm": residual[2 * index + 1] if node.rotation_restraint else 0.0,
            }
        )
    station_results: list[dict[str, Any]] = []
    for data in element_data:
        element: BeamElement = data["element"]
        local_d = [displacement[dof] for dof in data["dofs"]]
        end_actions = [a - b for a, b in zip(_matvec(data["stiffness"], local_d), data["equivalent"], strict=True)]
        positions = {data["length"] * i / request.station_intervals for i in range(request.station_intervals + 1)}
        point_positions = {point.distance_from_start_mm for point in data["points"]}
        positions.update(point_positions)
        for x in sorted(positions):
            moment = -end_actions[1] + end_actions[0] * x + element.uniform_load_n_per_mm * x**2 / 2
            rotation = local_d[1] + (-end_actions[1] * x + end_actions[0] * x**2 / 2 + element.uniform_load_n_per_mm * x**3 / 6) / (element.elastic_modulus_n_per_mm2 * element.second_moment_mm4)
            vertical = local_d[0] + local_d[1] * x + (-end_actions[1] * x**2 / 2 + end_actions[0] * x**3 / 6 + element.uniform_load_n_per_mm * x**4 / 24) / (element.elastic_modulus_n_per_mm2 * element.second_moment_mm4)
            shear = end_actions[0] + element.uniform_load_n_per_mm * x
            for point in data["points"]:
                delta = max(0.0, x - point.distance_from_start_mm)
                moment += point.vertical_force_n * delta
                rotation += point.vertical_force_n * delta**2 / (2 * element.elastic_modulus_n_per_mm2 * element.second_moment_mm4)
                vertical += point.vertical_force_n * delta**3 / (6 * element.elastic_modulus_n_per_mm2 * element.second_moment_mm4)
                if point.distance_from_start_mm < x:
                    shear += point.vertical_force_n
            base = {
                "analysis_element_id": element.analysis_element_id,
                "physical_span_id": element.physical_span_id,
                "distance_from_start_mm": x,
                "x_mm": nodes[node_index[element.start_node_id]].x_mm + x,
                "vertical_displacement_mm": vertical,
                "rotation_rad": rotation,
                "v2_n": shear,
                "m3_nmm": moment,
            }
            if x in point_positions:
                station_results.append({**base, "side": "left"})
                station_results.append({**base, "side": "right", "v2_n": shear + math.fsum(point.vertical_force_n for point in data["points"] if point.distance_from_start_mm == x)})
            else:
                station_results.append({**base, "side": "continuous"})
    applied_force = math.fsum(node.nodal_force_n for node in nodes) + math.fsum(element.uniform_load_n_per_mm * data["length"] for element, data in zip(request.elements, element_data, strict=True)) + math.fsum(point.vertical_force_n for point in request.point_loads)
    reaction_force = math.fsum(item["vertical_reaction_n"] for item in node_results)
    force_residual = reaction_force + applied_force
    applied_moment = math.fsum(node.nodal_moment_nmm + node.nodal_force_n * (node.x_mm - origin) for node in nodes)
    applied_moment += math.fsum(element.uniform_load_n_per_mm * data["length"] * (nodes[index].x_mm - origin + data["length"] / 2) for index, (element, data) in enumerate(zip(request.elements, element_data, strict=True)))
    applied_moment += math.fsum(point.vertical_force_n * (nodes[node_index[next(element.start_node_id for element in request.elements if element.analysis_element_id == point.analysis_element_id)]].x_mm - origin + point.distance_from_start_mm) for point in request.point_loads)
    reaction_moment = math.fsum(item["reaction_moment_nmm"] + item["vertical_reaction_n"] * (item["x_mm"] - origin) for item in node_results)
    moment_residual = reaction_moment + applied_moment
    force_tolerance = max(1e-6, 1e-9 * max(1.0, abs(applied_force)))
    moment_tolerance = max(1e-3, 1e-9 * max(1.0, abs(applied_moment)))
    free_force_residual = max(
        (abs(residual[dof]) for dof in free if dof % 2 == 0), default=0.0
    )
    free_moment_residual = max(
        (abs(residual[dof]) for dof in free if dof % 2 == 1), default=0.0
    )
    if (
        abs(force_residual) > force_tolerance
        or abs(moment_residual) > moment_tolerance
        or free_force_residual > force_tolerance
        or free_moment_residual > moment_tolerance
    ):
        return rejected_result(
            BEAM_LINE_SOLVE_OPERATION,
            inputs,
            (_diagnostic(BEAM_LINE_SOLVE_OPERATION, "ANALYSIS.EQUILIBRIUM", "The solved response failed force, moment, or free-DOF equilibrium.", "result"),),
            provenance=provenance,
        )
    return completed_result(
        BEAM_LINE_SOLVE_OPERATION,
        inputs,
        {
            "solver_identity": "euler_bernoulli_direct_stiffness_v1",
            "analysis_profile": "bounded_planar_major_axis",
            "unit_basis": "mm_n_nmm_rad",
            "nodes": node_results,
            "stations": station_results,
            "equilibrium": {
                "force_residual_n": force_residual,
                "moment_residual_nmm": moment_residual,
                "max_free_force_residual_n": free_force_residual,
                "max_free_moment_residual_nmm": free_moment_residual,
                "force_tolerance_n": force_tolerance,
                "moment_tolerance_nmm": moment_tolerance,
            },
        },
        engineering=EngineeringState.NOT_EVALUATED,
        provenance=provenance,
    )


__all__ = [
    "ACTION_NORMALIZE_OPERATION",
    "BEAM_LINE_SOLVE_OPERATION",
    "TOPOLOGY_OPERATION",
    "ActionConcurrency",
    "AnalysisElementMapping",
    "BeamElement",
    "BeamLineRequest",
    "BeamNode",
    "BeamPointLoad",
    "BeamTopologyRequest",
    "ForceUnit",
    "LengthUnit",
    "LocalAxes",
    "MomentUnit",
    "PhysicalSpan",
    "PhysicalSupport",
    "RawActionRow",
    "RawActionSnapshot",
    "SectionRegion",
    "Vector3",
    "define_beam_topology",
    "normalize_action_snapshot",
    "solve_beam_line",
]
