"""Bound physical loads, spans, concurrent actions and T lateral stability."""

from __future__ import annotations

import math
from dataclasses import dataclass

from structural_lib.codes.is456.beam.flanged_serviceability import (
    lateral_stability_length_limit,
)

from .analysis import (
    ACTION_NORMALIZE_OPERATION,
    BeamTopologyRequest,
    define_beam_topology,
)
from .reinforcement import Face, ReinforcementGeometryRequest, effective_depth
from .semantics import (
    Diagnostic,
    EngineeringState,
    OperationResult,
    Provenance,
    completed_result,
    effective_inputs,
    not_evaluated_result,
    rejected_result,
)
from .t_section_geometry import (
    TGeometryCheckRequest,
    TSectionGeometry,
    check_t_geometry,
    valid_t_section,
)

T_ACTION_BASIS_OPERATION = "structural.beam.t_action_basis.check/v1"
T_STABILITY_OPERATION = "is456.beam.t_lateral_stability.check/v1"
T_ZERO_TORSION_OPERATION = "is456.beam.t_zero_torsion.check/v1"
T_MEMBER_BASIS_REVISION = "is456-physical-t-member-e-v1"


@dataclass(frozen=True)
class TBeamLoadBasis:
    concrete_unit_weight_kn_per_m3: float
    superimposed_permanent_load_n_per_mm: float
    imposed_load_n_per_mm: float
    permanent_ultimate_factor: float
    imposed_ultimate_factor: float
    age_at_permanent_loading_days: float
    finish_installation_age_days: float
    assessment_age_days: float
    temperature_effects_applicable: bool
    history_reference: str


@dataclass(frozen=True)
class TBeamActionBasisRequest:
    geometry: TGeometryCheckRequest
    topology: BeamTopologyRequest | None
    ultimate_actions: OperationResult
    total_service_actions: OperationResult
    permanent_actions: OperationResult
    loads: TBeamLoadBasis | None


@dataclass(frozen=True)
class TLateralStabilityRequest:
    profile_id: str
    member_id: str
    section: TSectionGeometry
    effective_depth_mm: float
    member_start_mm: float
    member_end_mm: float
    lateral_restraint_stations_mm: tuple[float, ...]
    restraint_reference: str | None


def _passed(result: OperationResult) -> bool:
    return (
        result.execution == "completed"
        and result.engineering == "pass"
        and result.completeness == "complete_for_scope"
        and result.freshness == "current"
    )


def _diagnostic(operation: str, code: str, field: str, message: str) -> Diagnostic:
    return Diagnostic(
        code,
        "error",
        message,
        operation,
        field,
        "T-member-basis",
        "Supply the same current actual geometry, support, load and source-row evidence.",
    )


def _provenance() -> Provenance:
    return Provenance(
        T_MEMBER_BASIS_REVISION,
        T_MEMBER_BASIS_REVISION,
        (
            "IS456:2000 through Amendment6;22.2/22.6/23.1.2/23.3; explicit physical T self-weight",
            "Simply supported prismatic UDL statics; separate ULS, total and permanent service cases",
        ),
    )


def check_t_action_basis(request: TBeamActionBasisRequest) -> OperationResult:
    """Validate rather than invent a physical UDL decomposition and span basis.

    The action model uses bearing centres, conservatively longer than the
    derived code-effective span. The actual zero-moment distance is retained
    separately for flange width; it is not silently replaced by code span.
    """
    op, inputs, provenance = (
        T_ACTION_BASIS_OPERATION,
        effective_inputs(request=request),
        _provenance(),
    )
    top, loads, geometry = request.topology, request.loads, request.geometry

    def hold(code: str, message: str) -> OperationResult:
        return not_evaluated_result(
            op, inputs, _diagnostic(op, code, "request", message), provenance=provenance
        )

    if top is None or loads is None or not loads.history_reference:
        return hold(
            "T_BASIS.MISSING",
            "Explicit support faces, physical load decomposition and history are required.",
        )
    numbers = (
        loads.concrete_unit_weight_kn_per_m3,
        loads.superimposed_permanent_load_n_per_mm,
        loads.imposed_load_n_per_mm,
        loads.permanent_ultimate_factor,
        loads.imposed_ultimate_factor,
        loads.age_at_permanent_loading_days,
        loads.finish_installation_age_days,
        loads.assessment_age_days,
    )
    if (
        not all(math.isfinite(v) for v in numbers)
        or loads.concrete_unit_weight_kn_per_m3 <= 0
        or min(loads.superimposed_permanent_load_n_per_mm, loads.imposed_load_n_per_mm)
        < 0
        or min(loads.permanent_ultimate_factor, loads.imposed_ultimate_factor) < 1
        or not 0
        < loads.age_at_permanent_loading_days
        <= loads.finish_installation_age_days
        <= loads.assessment_age_days
    ):
        return rejected_result(
            op,
            inputs,
            (
                _diagnostic(
                    op,
                    "T_BASIS.INPUT",
                    "loads",
                    "Finite physical loads/factors and chronological history are required.",
                ),
            ),
            provenance=provenance,
        )
    if loads.temperature_effects_applicable:
        return hold(
            "T_BASIS.UNSUPPORTED",
            "The selected ordinary gravity profile has no qualified applicable thermal action model.",
        )
    if (
        len(top.supports) != 2
        or len(top.spans) != 1
        or top.member_id != geometry.member_id
    ):
        return hold(
            "T_BASIS.SUPPORT_SCOPE",
            "Exactly one physical member/span with both current support faces is required.",
        )
    if any(
        not isinstance(v, (int, float)) or not math.isfinite(v)
        for support in top.supports
        for v in (support.centre_x_mm, support.left_face_x_mm, support.right_face_x_mm)
    ):
        return hold(
            "T_BASIS.SUPPORT_WIDTH",
            "Both actual support faces and centres must be supplied.",
        )
    topology_result = define_beam_topology(top)
    physical = check_t_geometry(geometry)
    if not _passed(topology_result) or not _passed(physical):
        return hold(
            "T_BASIS.PHYSICAL",
            "Current qualifying physical topology and actual T-material evidence are required.",
        )
    web = physical.output_as("web_geometry", ReinforcementGeometryRequest)
    depth_result = effective_depth(web, Face.BOTTOM)
    if not _passed(depth_result):
        return hold("T_BASIS.DEPTH", "Current actual-bar effective depth is required.")
    d = float(depth_result.outputs["effective_depth_mm"])
    if not math.isclose(top.spans[0].effective_depth_mm, d, rel_tol=0, abs_tol=1e-8):
        return completed_result(
            op,
            inputs,
            {
                "actual_effective_depth_mm": d,
                "topology_effective_depth_mm": top.spans[0].effective_depth_mm,
            },
            engineering=EngineeringState.FAIL,
            diagnostics=(
                _diagnostic(
                    op,
                    "T_BASIS.DEPTH_CONFLICT",
                    "topology",
                    "The topology and actual reinforcement have conflicting effective depths.",
                ),
            ),
            provenance=provenance,
        )
    supports = sorted(top.supports, key=lambda s: s.centre_x_mm)
    origin, end = supports[0].centre_x_mm, supports[1].centre_x_mm
    span = end - origin
    if origin != 0 or span <= 0:
        return hold(
            "T_BASIS.DATUM",
            "The selected supplied one-span model starts at bearing centre zero.",
        )
    clear_span = supports[1].left_face_x_mm - supports[0].right_face_x_mm
    code_span = float(topology_result.outputs["spans"][0]["effective_span_mm"])
    section = geometry.section
    self_weight = section.area_mm2 * loads.concrete_unit_weight_kn_per_m3 / 1e6
    permanent = self_weight + loads.superimposed_permanent_load_n_per_mm
    service = permanent + loads.imposed_load_n_per_mm
    ultimate = (
        permanent * loads.permanent_ultimate_factor
        + loads.imposed_load_n_per_mm * loads.imposed_ultimate_factor
    )
    snapshots = (
        (request.ultimate_actions, ultimate),
        (request.total_service_actions, service),
        (request.permanent_actions, permanent),
    )
    critical = (
        origin,
        supports[0].right_face_x_mm,
        span / 2,
        supports[1].left_face_x_mm,
        end,
    )
    case_ids = []
    governing_rows = []
    for snapshot, load in snapshots:
        if (
            not _passed(snapshot)
            or snapshot.operation_semantic_id != ACTION_NORMALIZE_OPERATION
        ):
            return hold(
                "T_BASIS.ACTION_STATE",
                "Each load case needs its own current complete normalized actions.",
            )
        rows = snapshot.outputs.get("rows", ())
        if not rows or len({row["load_case_id"] for row in rows}) != 1:
            return hold(
                "T_BASIS.CASE_IDENTITY",
                "Each snapshot must retain exactly one concurrent load-case identity.",
            )
        if any(
            not any(
                math.isclose(row["object_station_mm"], x, abs_tol=1e-8, rel_tol=0)
                for row in rows
            )
            for x in critical
        ):
            return hold(
                "T_BASIS.CRITICAL_STATION",
                "End, support-face and exact midspan rows are required.",
            )
        case_ids.append(rows[0]["load_case_id"])
        for row in rows:
            x = row["object_station_mm"]
            if (
                any(row[key] != 0 for key in ("p_n", "v3_n", "m2_nmm", "t_nmm"))
                or row["m3_nmm"] < -1e-3
            ):
                return hold(
                    "T_BASIS.UNSUPPORTED_ACTION",
                    "Nonzero torsion/axial/weak-axis or beam-axis hogging actions are outside the selected sagging T profile.",
                )
            if (
                row["member_id"] != geometry.member_id
                or row["axis_id"] != top.local_axes.axis_id
                or row["concurrency"] != "static_concurrent"
                or not 0 <= x <= span
                or not math.isclose(
                    row["v2_n"], load * (span / 2 - x), rel_tol=1e-11, abs_tol=1e-6
                )
                or not math.isclose(
                    row["m3_nmm"],
                    load * x * (span - x) / 2,
                    rel_tol=1e-11,
                    abs_tol=1e-3,
                )
            ):
                return hold(
                    "T_BASIS.ACTION_BINDING",
                    "Current rows conflict with the actual physical-width self-weight, G/Q factors, member, axes or UDL statics.",
                )
        governing_rows.append(max(rows, key=lambda row: row["m3_nmm"])["row_id"])
    if (
        len(set(case_ids)) != 3
        or len({snapshot.result_id for snapshot, _ in snapshots}) != 3
    ):
        return hold(
            "T_BASIS.CASE_IDENTITY",
            "ULS, total-service and permanent snapshots must have distinct identities.",
        )
    return completed_result(
        op,
        inputs,
        {
            "section_id": section.section_id,
            "geometry_revision_id": section.geometry_revision_id,
            "reinforcement_revision_id": geometry.reinforcement_revision_id,
            "topology_result_id": topology_result.result_id,
            "t_geometry_result_id": physical.result_id,
            "analysis_span_mm": span,
            "zero_moment_distance_mm": span,
            "clear_span_mm": clear_span,
            "code_effective_span_mm": code_span,
            "effective_depth_mm": d,
            "self_weight_n_per_mm": self_weight,
            "permanent_load_n_per_mm": permanent,
            "total_service_load_n_per_mm": service,
            "ultimate_load_n_per_mm": ultimate,
            "ultimate_moment_knm": ultimate * span**2 / 8 / 1e6,
            "ultimate_shear_kn": ultimate * span / 2 / 1000,
            "service_moment_knm": service * span**2 / 8 / 1e6,
            "governing_ultimate_row_id": governing_rows[0],
            "governing_service_row_id": governing_rows[1],
            "governing_permanent_row_id": governing_rows[2],
            "ultimate_action_result_id": request.ultimate_actions.result_id,
            "total_service_action_result_id": request.total_service_actions.result_id,
            "permanent_action_result_id": request.permanent_actions.result_id,
            "history_reference": loads.history_reference,
        },
        provenance=provenance,
    )


def check_t_lateral_stability(request: TLateralStabilityRequest) -> OperationResult:
    """IS45623.3, conservatively using web breadth below compression-face b."""
    op, inputs, provenance = (
        T_STABILITY_OPERATION,
        effective_inputs(request=request),
        _provenance(),
    )
    if (
        not request.restraint_reference
        or len(request.lateral_restraint_stations_mm) < 2
    ):
        return not_evaluated_result(
            op,
            inputs,
            _diagnostic(
                op,
                "T_STABILITY.RESTRAINTS",
                "restraints",
                "Actual lateral restraints and their evidence reference are required.",
            ),
            provenance=provenance,
        )
    if (
        not valid_t_section(request.section)
        or not 0 < request.effective_depth_mm < request.section.depth_mm
    ):
        return rejected_result(
            op,
            inputs,
            (
                _diagnostic(
                    op,
                    "T_STABILITY.INPUT",
                    "section",
                    "Actual physical T geometry/effective depth is required.",
                ),
            ),
            provenance=provenance,
        )
    positions = request.lateral_restraint_stations_mm
    if (
        not all(math.isfinite(x) for x in positions)
        or tuple(sorted(set(positions))) != positions
        or positions[0] != request.member_start_mm
        or positions[-1] != request.member_end_mm
    ):
        return not_evaluated_result(
            op,
            inputs,
            _diagnostic(
                op,
                "T_STABILITY.SCOPE",
                "restraints",
                "Ordered actual restraints must cover both ends of the declared member.",
            ),
            provenance=provenance,
        )
    b = request.section.web_width_mm
    limit = lateral_stability_length_limit(b, request.effective_depth_mm)
    actual = max(
        right - left for left, right in zip(positions, positions[1:], strict=False)
    )
    return completed_result(
        op,
        inputs,
        {
            "compression_face_physical_breadth_mm": request.section.flange_width_physical_mm,
            "conservative_breadth_used_mm": b,
            "maximum_unrestrained_length_mm": actual,
            "limiting_unrestrained_length_mm": limit,
            "passed": actual <= limit,
        },
        engineering=EngineeringState.PASS if actual <= limit else EngineeringState.FAIL,
        diagnostics=(
            ()
            if actual <= limit
            else (
                _diagnostic(
                    op,
                    "T_STABILITY.LIMIT",
                    "restraints",
                    "Actual unrestrained length exceeds the conservative code limit.",
                ),
            )
        ),
        provenance=provenance,
    )


def check_t_zero_torsion(request: TBeamActionBasisRequest) -> OperationResult:
    """Prove zero torque over all current cases; compute no T resistance.

    This Python T-profile admission operation is separate from the shared
    rectangular ``is456.beam.torsion.check/v1`` resistance contract.
    """
    op, inputs, provenance = (
        T_ZERO_TORSION_OPERATION,
        effective_inputs(request=request),
        _provenance(),
    )
    basis = check_t_action_basis(request)
    if not _passed(basis):
        return not_evaluated_result(
            op,
            inputs,
            _diagnostic(
                op,
                "T_ZERO.CURRENT_ACTION_BASIS",
                "actions",
                "Current qualifying actual T ULS, total-service and permanent actions with zero torque are required.",
            ),
            provenance=provenance,
        )
    return completed_result(
        op,
        inputs,
        {
            "zero_demand": True,
            "torsion_resistance_computed": False,
            "action_basis_result_id": basis.result_id,
            "snapshot_result_ids": tuple(
                snapshot.result_id
                for snapshot in (
                    request.ultimate_actions,
                    request.total_service_actions,
                    request.permanent_actions,
                )
            ),
            "zero_torque_row_ids": tuple(
                row["row_id"]
                for snapshot in (
                    request.ultimate_actions,
                    request.total_service_actions,
                    request.permanent_actions,
                )
                for row in snapshot.outputs["rows"]
            ),
        },
        provenance=provenance,
    )
