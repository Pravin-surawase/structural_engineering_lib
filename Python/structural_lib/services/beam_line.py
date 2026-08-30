# SPDX-License-Identifier: MIT
"""Pure bounded W3G beam-line solve, without NumPy, COM, I/O or design approval.

Euler-Bernoulli Hermite stiffness and consistent loads use w up and theta=w'.
Independent hinge rotations avoid penalties or guessed stiffness. Unloaded
rigid arms use exact kinematic transformations. Station fields integrate the
actual piecewise load, not just the unloaded cubic displacement interpolation.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass

from pydantic import BaseModel, ValidationError

from structural_lib.core.analysis_contracts import EvidenceStateV1, EvidenceValueV1
from structural_lib.core.beam_line import (
    BeamLineAnalysisBuildResultV1,
    BeamLineAnalysisRequestV1,
    BeamLineAnalysisResultV1,
    BeamLineEquilibriumV1,
    BeamLineIssueV1,
    BeamLineNodeResultV1,
    BeamLinePointLoadV1,
    BeamLineSpanResultV1,
    BeamLineSpanV1,
    BeamLineStationV1,
)

__all__ = ["solve_beam_line_linear_v1"]


class _BeamLineError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _hash(model: BaseModel, *, exclude: set[str] | None = None) -> str:
    data = model.model_dump(mode="json", exclude=exclude)
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise _BeamLineError("DUPLICATE_IDENTITY", f"duplicate {label}")


def _weights(request: BeamLineAnalysisRequestV1) -> list[tuple[str, float]]:
    cases = {case.case_id: case for case in request.load_cases}
    combos = {combo.combination_id: combo for combo in request.combinations}
    _unique([case.case_id for case in request.load_cases], "case")
    _unique([combo.combination_id for combo in request.combinations], "combination")
    visited: set[str] = set()

    def validate(name: str, active: frozenset[str]) -> None:
        if name in active:
            raise _BeamLineError("COMBINATION_CYCLE", "nested combination cycle")
        if name not in combos:
            raise _BeamLineError("MISSING_COMBINATION", f"unknown combination {name}")
        if name in visited:
            return
        for factor in combos[name].factors:
            if factor.source_kind == "CASE":
                if factor.source_id not in cases:
                    raise _BeamLineError(
                        "MISSING_CASE", f"unknown case {factor.source_id}"
                    )
            else:
                validate(factor.source_id, active | {name})
        visited.add(name)

    for name in combos:
        validate(name, frozenset())
    resolved: list[tuple[str, float]] = []
    expansions = 0

    def expand(kind: str, name: str, weight: float) -> None:
        nonlocal expansions
        expansions += 1
        if expansions > 4096:
            raise _BeamLineError(
                "CAPACITY_EXCEEDED", "combination expansion exceeds 4096"
            )
        if not math.isfinite(weight):
            raise _BeamLineError("NONFINITE_NUMERICS", "nonfinite combination factor")
        if kind == "CASE":
            if name not in cases:
                raise _BeamLineError("MISSING_CASE", f"unknown selected case {name}")
            resolved.append((name, weight))
        else:
            if name not in combos:
                raise _BeamLineError(
                    "MISSING_COMBINATION", f"unknown selected combination {name}"
                )
            for item in combos[name].factors:
                expand(item.source_kind, item.source_id, weight * item.factor)

    expand(request.scenario.result_kind, request.scenario.result_id, 1.0)
    return resolved


@dataclass
class _Element:
    span: BeamLineSpanV1
    x: float
    length: float
    ei: float
    maps: list[dict[int, float]]
    stiffness: list[list[float]]
    loads: list[float]
    uniform: float
    points: list[BeamLinePointLoadV1]


def _stiffness(length: float, ei: float) -> list[list[float]]:
    a, b, c, d = (
        12 * ei / length**3,
        6 * ei / length**2,
        4 * ei / length,
        2 * ei / length,
    )
    return [[a, b, -a, b], [b, c, -b, d], [-a, -b, a, -b], [b, d, -b, c]]


def _cholesky(matrix: list[list[float]], rhs: list[float], floor: float) -> list[float]:
    """Diagonal scaling keeps the pivot test independent of force/length units."""
    size = len(rhs)
    if not size:
        return []
    if any(matrix[i][i] <= 0 or not math.isfinite(matrix[i][i]) for i in range(size)):
        raise _BeamLineError(
            "SINGULAR_OR_UNSTABLE", "nonpositive free stiffness diagonal"
        )
    scale = [math.sqrt(matrix[i][i]) for i in range(size)]
    lower = [[0.0] * size for _ in range(size)]
    for i in range(size):
        for j in range(i + 1):
            value = matrix[i][j] / scale[i] / scale[j] - math.fsum(
                lower[i][k] * lower[j][k] for k in range(j)
            )
            if i == j:
                if not math.isfinite(value) or value <= floor:
                    raise _BeamLineError(
                        "SINGULAR_OR_UNSTABLE",
                        "scaled stiffness pivot below declared floor",
                    )
                lower[i][j] = math.sqrt(value)
            else:
                lower[i][j] = value / lower[j][j]
    forward = [0.0] * size
    solved = [0.0] * size
    for i in range(size):
        forward[i] = (
            rhs[i] / scale[i] - math.fsum(lower[i][j] * forward[j] for j in range(i))
        ) / lower[i][i]
    for i in reversed(range(size)):
        solved[i] = (
            forward[i] - math.fsum(lower[j][i] * solved[j] for j in range(i + 1, size))
        ) / lower[i][i]
    return [solved[i] / scale[i] for i in range(size)]


def _matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [
        math.fsum(a * b for a, b in zip(row, vector, strict=True)) for row in matrix
    ]


def _four(values: list[float]) -> tuple[float, float, float, float]:
    return values[0], values[1], values[2], values[3]


def _solve(request: BeamLineAnalysisRequestV1) -> BeamLineAnalysisResultV1:
    nodes = request.nodes
    _unique([node.node_id for node in nodes], "node")
    _unique([span.span_id for span in request.spans], "span")
    _unique([support.node_id for support in request.supports], "support")
    node_index = {node.node_id: i for i, node in enumerate(nodes)}
    if len(request.spans) != len(nodes) - 1 or any(
        b.x_m <= a.x_m for a, b in zip(nodes, nodes[1:], strict=False)
    ):
        raise _BeamLineError(
            "TOPOLOGY_UNSUPPORTED",
            "require one ordered horizontal line with increasing x",
        )
    if set(node_index) != {support.node_id for support in request.supports}:
        raise _BeamLineError(
            "SUPPORT_IDENTITY", "each node requires one explicit support definition"
        )
    span_by_id = {span.span_id: span for span in request.spans}
    elements: list[_Element] = []
    ndof = 2 * len(nodes)
    for i, span in enumerate(request.spans):
        if (span.start_node_id, span.end_node_id) != (
            nodes[i].node_id,
            nodes[i + 1].node_id,
        ):
            raise _BeamLineError(
                "TOPOLOGY_UNSUPPORTED",
                "spans must connect each successive ordered node pair",
            )
        a, b = span.rigid_offset_start_m, span.rigid_offset_end_m
        length = nodes[i + 1].x_m - nodes[i].x_m - a - b
        if length <= 0:
            raise _BeamLineError("INVALID_FLEXIBLE_LENGTH", "offsets consume the span")
        # N/mm2 * mm4 = N mm2 = 1e-9 kN m2.
        ei = (
            span.elastic_modulus_nmm2
            * span.second_moment_mm4
            * span.stiffness_modifier
            * 1e-9
        )
        maps = [{2 * i: 1.0}, {2 * i + 1: 1.0}, {2 * i + 2: 1.0}, {2 * i + 3: 1.0}]
        if a:
            maps[0][2 * i + 1] = a
        if b:
            maps[2][2 * i + 3] = -b
        for local, released in (
            (1, span.release_start_rotation),
            (3, span.release_end_rotation),
        ):
            if released:
                maps[local] = {ndof: 1.0}
                ndof += 1
        elements.append(
            _Element(
                span,
                nodes[i].x_m + a,
                length,
                ei,
                maps,
                _stiffness(length, ei),
                [0.0] * 4,
                0.0,
                [],
            )
        )
    element_by_id = {element.span.span_id: element for element in elements}
    for case in request.load_cases:
        if any(item.span_id not in span_by_id for item in case.uniform_loads) or any(
            item.span_id not in span_by_id for item in case.point_loads
        ):
            raise _BeamLineError("LOAD_IDENTITY", "member load names an unknown span")
        if any(load.node_id not in node_index for load in case.nodal_loads):
            raise _BeamLineError("LOAD_IDENTITY", "nodal load names an unknown node")
        for load in case.point_loads:
            if (
                not 0
                < load.distance_from_flexible_start_m
                < element_by_id[load.span_id].length
            ):
                raise _BeamLineError(
                    "LOAD_POSITION",
                    "point loads must be inside flexible length; use nodal loads at nodes",
                )
    cases = {case.case_id: case for case in request.load_cases}
    force = [0.0] * ndof
    applied_force: list[float] = []
    applied_moments: list[float] = []
    origin = nodes[0].x_m
    for case_id, factor in _weights(request):
        case = cases[case_id]
        for nodal in case.nodal_loads:
            i = node_index[nodal.node_id]
            vertical, moment = factor * nodal.vertical_kn, factor * nodal.moment_knm
            force[2 * i] += vertical
            force[2 * i + 1] += moment
            applied_force.append(vertical)
            applied_moments.extend((vertical * (nodes[i].x_m - origin), moment))
        for uniform in case.uniform_loads:
            element = element_by_id[uniform.span_id]
            value = factor * uniform.vertical_kn_per_m
            element.uniform += value
            applied_force.append(value * element.length)
            applied_moments.append(
                value * element.length * (element.x - origin + element.length / 2)
            )
        for element in elements:
            span = element.span
            # kg/m3 * mm2 * 1e-6 * m/s2 / 1000 = kN/m; downward is negative.
            value = (
                -factor
                * case.self_weight_factor
                * span.density_kg_m3
                * span.area_mm2
                * 1e-9
                * request.gravity_m_per_s2
            )
            element.uniform += value
            applied_force.append(value * element.length)
            applied_moments.append(
                value * element.length * (element.x - origin + element.length / 2)
            )
        for load in case.point_loads:
            element = element_by_id[load.span_id]
            value = factor * load.vertical_kn
            element.points.append(
                BeamLinePointLoadV1(
                    span_id=load.span_id,
                    distance_from_flexible_start_m=load.distance_from_flexible_start_m,
                    vertical_kn=value,
                )
            )
            applied_force.append(value)
            applied_moments.append(
                value * (element.x - origin + load.distance_from_flexible_start_m)
            )
    matrix = [[0.0] * ndof for _ in range(ndof)]
    for element in elements:
        length, q = element.length, element.uniform
        element.loads = [
            q * length / 2,
            q * length**2 / 12,
            q * length / 2,
            -q * length**2 / 12,
        ]
        for point in element.points:
            t = point.distance_from_flexible_start_m / length
            shape = (
                1 - 3 * t**2 + 2 * t**3,
                length * (t - 2 * t**2 + t**3),
                3 * t**2 - 2 * t**3,
                length * (-(t**2) + t**3),
            )
            for i in range(4):
                element.loads[i] += point.vertical_kn * shape[i]
        for a in range(4):
            for i, ci in element.maps[a].items():
                force[i] += ci * element.loads[a]
                for b in range(4):
                    for j, cj in element.maps[b].items():
                        matrix[i][j] += ci * element.stiffness[a][b] * cj
    structural_matrix = [row[:] for row in matrix]
    fixed: set[int] = set()
    springs: dict[int, float] = {}
    for support in request.supports:
        i = node_index[support.node_id]
        if support.vertical == "FIXED":
            fixed.add(2 * i)
        if support.rotation == "FIXED":
            fixed.add(2 * i + 1)
        if support.rotation == "SPRING":
            if (
                support.spring.state != EvidenceStateV1.PRESENT
                or support.spring.value is None
            ):
                raise _BeamLineError(
                    "SPRING_EVIDENCE_REQUIRED",
                    "rotational spring requires PRESENT stiffness",
                )
            stiffness = support.spring.value.rotational_stiffness_knm_per_rad
            springs[2 * i + 1] = stiffness
            matrix[2 * i + 1][2 * i + 1] += stiffness
        elif support.spring.state != EvidenceStateV1.NOT_APPLICABLE:
            raise _BeamLineError(
                "SPRING_APPLICABILITY",
                "FREE/FIXED rotation requires explicit NOT_APPLICABLE spring",
            )
    inactive: set[int] = set()
    for i, row in enumerate(matrix):
        if i in fixed:
            continue
        if all(value == 0.0 for value in row):
            if i < 2 * len(nodes) and i % 2 and force[i] == 0:
                inactive.add(i)
            else:
                raise _BeamLineError(
                    "SINGULAR_OR_UNSTABLE",
                    "unrestrained loaded or translational degree of freedom",
                )
    free = [i for i in range(ndof) if i not in fixed | inactive]
    values = _cholesky(
        [[matrix[i][j] for j in free] for i in free],
        [force[i] for i in free],
        request.numerics.scaled_pivot_floor,
    )
    displacement = [0.0] * ndof
    for i, value in zip(free, values, strict=True):
        displacement[i] = value
    residual = [
        a - b for a, b in zip(_matvec(matrix, displacement), force, strict=True)
    ]
    structural_residual = [
        a - b
        for a, b in zip(_matvec(structural_matrix, displacement), force, strict=True)
    ]
    node_results: list[BeamLineNodeResultV1] = []
    for i, node in enumerate(nodes):
        rotation = EvidenceValueV1[float](
            state=EvidenceStateV1.PRESENT,
            value=displacement[2 * i + 1],
            source_references=(node.node_id,),
        )
        if 2 * i + 1 in inactive:
            rotation = EvidenceValueV1[float](
                state=EvidenceStateV1.NOT_APPLICABLE,
                reason_code="DISCONNECTED_RELEASE_ROTATION",
                message="No connected rotational DOF; member end rotations are retained separately",
                source_references=(node.node_id,),
            )
        node_results.append(
            BeamLineNodeResultV1(
                node_id=node.node_id,
                vertical_displacement_m=displacement[2 * i],
                rotation_rad=rotation,
                vertical_reaction_kn=(
                    structural_residual[2 * i] if 2 * i in fixed else 0.0
                ),
                reaction_moment_knm=(
                    structural_residual[2 * i + 1]
                    if 2 * i + 1 in fixed
                    else -springs.get(2 * i + 1, 0.0) * displacement[2 * i + 1]
                ),
            )
        )
    force_residual = math.fsum(
        applied_force + [node.vertical_reaction_kn for node in node_results]
    )
    moment_residual = math.fsum(
        applied_moments
        + [
            result.vertical_reaction_kn * (node.x_m - origin)
            + result.reaction_moment_knm
            for node, result in zip(nodes, node_results, strict=True)
        ]
    )
    force_norm = math.fsum(abs(value) for value in applied_force)
    moment_norm = math.fsum(abs(value) for value in applied_moments)
    # Include nodal-equivalent load norms in residual checks, never stiffness terms.
    force_norm = max(
        force_norm, math.fsum(abs(force[i]) for i in range(0, 2 * len(nodes), 2))
    )
    moment_norm = max(
        moment_norm,
        math.fsum(abs(force[i]) for i in range(ndof) if i >= 2 * len(nodes) or i % 2),
    )
    force_tol = (
        request.numerics.absolute_force_kn
        + request.numerics.equilibrium_relative * force_norm
    )
    moment_tol = (
        request.numerics.absolute_moment_knm
        + request.numerics.equilibrium_relative * moment_norm
    )
    free_force = max(
        (abs(residual[i]) for i in free if i < 2 * len(nodes) and i % 2 == 0),
        default=0.0,
    )
    free_moment = max(
        (abs(residual[i]) for i in free if i >= 2 * len(nodes) or i % 2), default=0.0
    )
    if (
        abs(force_residual) > force_tol
        or free_force > force_tol
        or abs(moment_residual) > moment_tol
        or free_moment > moment_tol
    ):
        raise _BeamLineError(
            "EQUILIBRIUM_FAILED",
            "force, moment or free-DOF residual exceeds frozen tolerance",
        )
    equilibrium = BeamLineEquilibriumV1(
        force_residual_kn=force_residual,
        moment_residual_knm=moment_residual,
        max_free_force_residual_kn=free_force,
        max_free_moment_residual_knm=free_moment,
        applied_force_norm_kn=force_norm,
        applied_moment_norm_knm=moment_norm,
        force_tolerance_kn=force_tol,
        moment_tolerance_knm=moment_tol,
    )
    span_results: list[BeamLineSpanResultV1] = []
    row_count = 0
    for element in elements:
        end_d = [
            math.fsum(displacement[i] * c for i, c in row.items())
            for row in element.maps
        ]
        end_q = [
            a - b
            for a, b in zip(
                _matvec(element.stiffness, end_d), element.loads, strict=True
            )
        ]
        stations = _stations(element, end_d, end_q, request.station_intervals_per_span)
        row_count += len(stations)
        if row_count > request.max_station_rows:
            raise _BeamLineError(
                "CAPACITY_EXCEEDED",
                "station rows exceed the request bound; no truncation",
            )
        span_results.append(
            BeamLineSpanResultV1(
                span_id=element.span.span_id,
                flexible_length_m=element.length,
                effective_ei_knm2=element.ei,
                end_actions_kn_knm=_four(end_q),
                end_displacements_m_rad=_four(end_d),
                uniform_vertical_kn_per_m=element.uniform,
                point_loads=tuple(element.points),
                stations=tuple(stations),
            )
        )
    result = BeamLineAnalysisResultV1(
        request=request,
        request_sha256=_hash(request),
        result_sha256="0" * 64,
        nodes=tuple(node_results),
        spans=tuple(span_results),
        equilibrium=equilibrium,
        station_row_count=row_count,
    )
    return result.model_copy(
        update={"result_sha256": _hash(result, exclude={"result_sha256"})}
    )


def _stations(
    element: _Element, end_d: list[float], end_q: list[float], intervals: int
) -> list[BeamLineStationV1]:
    positions = {element.length * i / intervals for i in range(intervals + 1)}
    point_positions = {load.distance_from_flexible_start_m for load in element.points}
    positions.update(point_positions)
    result: list[BeamLineStationV1] = []
    for x in sorted(positions):
        moment = -end_q[1] + end_q[0] * x + element.uniform * x**2 / 2
        rotation = (
            end_d[1]
            + (-end_q[1] * x + end_q[0] * x**2 / 2 + element.uniform * x**3 / 6)
            / element.ei
        )
        vertical = (
            end_d[0]
            + end_d[1] * x
            + (-end_q[1] * x**2 / 2 + end_q[0] * x**3 / 6 + element.uniform * x**4 / 24)
            / element.ei
        )
        shear = end_q[0] + element.uniform * x
        for point in element.points:
            a = point.distance_from_flexible_start_m
            delta = max(0.0, x - a)
            moment += point.vertical_kn * delta
            rotation += point.vertical_kn * delta**2 / (2 * element.ei)
            vertical += point.vertical_kn * delta**3 / (6 * element.ei)
            if a < x:
                shear += point.vertical_kn
        data = {
            "span_id": element.span.span_id,
            "distance_from_flexible_start_m": x,
            "x_m": element.x + x,
            "vertical_displacement_m": vertical,
            "rotation_rad": rotation,
            "shear_kn": shear,
            "moment_knm": moment,
        }
        if x in point_positions:
            result.append(BeamLineStationV1.model_validate({**data, "side": "LEFT"}))
            data["shear_kn"] = shear + math.fsum(
                p.vertical_kn
                for p in element.points
                if p.distance_from_flexible_start_m == x
            )
            result.append(BeamLineStationV1.model_validate({**data, "side": "RIGHT"}))
        else:
            result.append(
                BeamLineStationV1.model_validate({**data, "side": "CONTINUOUS"})
            )
    return result


def solve_beam_line_linear_v1(
    request: BeamLineAnalysisRequestV1, /
) -> BeamLineAnalysisBuildResultV1:
    """Solve one exact scenario, or return typed issues and no partial result.

    This is numerical software evidence only. No ETABS calibration, torsion,
    whole-building analysis, design acceptance or professional approval follows.
    """
    try:
        # Revalidate even a model_copy/model_construct supplied by a caller.
        request = BeamLineAnalysisRequestV1.model_validate(request.model_dump())
        return BeamLineAnalysisBuildResultV1(status="ACCEPTED", result=_solve(request))
    except _BeamLineError as exc:
        return BeamLineAnalysisBuildResultV1(
            status="BLOCKED",
            issues=(BeamLineIssueV1(reason_code=exc.code, message=str(exc)),),
        )
    except (ValidationError, ArithmeticError, ValueError) as exc:
        return BeamLineAnalysisBuildResultV1(
            status="BLOCKED",
            issues=(
                BeamLineIssueV1(
                    reason_code="INVALID_OR_NONFINITE_INPUT",
                    message=f"{type(exc).__name__}: invalid or nonfinite bounded solver input/result",
                ),
            ),
        )
