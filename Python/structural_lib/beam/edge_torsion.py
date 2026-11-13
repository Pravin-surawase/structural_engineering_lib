"""Compose a bounded edge-beam torsion check from actual paths and concurrent actions."""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose

from .analysis import ACTION_NORMALIZE_OPERATION
from .bar_paths import BarPathRole
from .detailing import (
    AnchorageCheckRequest,
    AnchorageDirection,
    AnchorageLocation,
    AnchoragePath,
    BarSurface,
    DevelopmentLengthRequest,
    StressState,
    check_anchorage,
)
from .physical_torsion import (
    ClosedLinkDetailRequest,
    TorsionSupportTransferRequest,
    check_closed_link_detail,
    check_torsion_support_transfer,
)
from .semantics import (
    CompletenessState,
    Diagnostic,
    EngineeringState,
    ExecutionState,
    FreshnessState,
    OperationResult,
    Provenance,
    completed_result,
    effective_inputs,
    partial_result,
)
from .shear_torsion import (
    ActionBasis,
    ConcurrentActionRow,
    TorsionCheckRequest,
    check_torsion,
)

EDGE_TORSION_OPERATION = "is456.beam.equilibrium-torsion.check/v1"
_PROVENANCE = Provenance(
    "is456-amd6",
    "is456-edge-equilibrium-torsion-v1",
    (
        "IS 456:2000 Cl. 26.2 and 41",
        "Concurrent source actions and signed receiving-crosshead force and torque equilibrium",
    ),
)


@dataclass(frozen=True)
class EdgeBeamTorsionRequest:
    """One current source action snapshot and the physical ordinary edge-beam detail."""

    transfer: TorsionSupportTransferRequest
    link_detail: ClosedLinkDetailRequest
    required_source_row_ids: tuple[str, ...]
    load_path_reference: str | None


def _issue(code: str, field: str, message: str) -> Diagnostic:
    return Diagnostic(
        code,
        "error",
        message,
        EDGE_TORSION_OPERATION,
        field,
        "edge-torsion",
        "Supply the current signed source rows and matched physical detail.",
    )


def check_edge_beam_torsion(request: EdgeBeamTorsionRequest) -> OperationResult:
    """Check one rectangular edge beam under concurrent V2, M3 and equilibrium torque.

    Parameters
    ----------
    request : EdgeBeamTorsionRequest
        Current normalized rows, physical paths, ordinary links and receiving supports.

    Returns
    -------
    OperationResult
        Station resistance, full-stress straight anchorage, link geometry and transfer.

    Raises
    ------
    TypeError
        The request must be an EdgeBeamTorsionRequest.

    Examples
    --------
    >>> callable(check_edge_beam_torsion)
    True

    Limitations
    -----------
    One span and one declared action case. The receiver boundary stops at
    its section flexure and shear. Service and foundation checks are separate.

    Provenance
    ----------
    IS 456 Clause 41 for same-row strength and the physical support-transfer owner.
    """
    if not isinstance(request, EdgeBeamTorsionRequest):
        raise TypeError("request must be EdgeBeamTorsionRequest")
    transfer, link = request.transfer, request.link_detail
    snapshot = transfer.action_snapshot
    inputs = effective_inputs(request=request)
    outputs: dict[str, object] = {
        "action_snapshot_id": snapshot.result_id,
        "station_checks": (),
        "anchors": (),
        "transfer": None,
        "link_detail": None,
    }

    def hold(code: str, field: str, message: str) -> OperationResult:
        return partial_result(
            EDGE_TORSION_OPERATION,
            inputs,
            outputs,
            (_issue(code, field, message),),
            provenance=_PROVENANCE,
            freshness=snapshot.freshness,
        )

    if (
        snapshot.operation_semantic_id != ACTION_NORMALIZE_OPERATION
        or snapshot.engineering is not EngineeringState.PASS
        or snapshot.freshness is not FreshnessState.CURRENT
        or snapshot.completeness is not CompletenessState.COMPLETE_FOR_SCOPE
        or snapshot.execution is not ExecutionState.COMPLETED
    ):
        return hold(
            "EDGE.ACTION_SNAPSHOT_HELD",
            "transfer.action_snapshot",
            "Current complete normalized action evidence is required.",
        )
    rows = snapshot.outputs.get("rows", ())
    required = set(request.required_source_row_ids)
    if (
        not required
        or len(required) != len(request.required_source_row_ids)
        or required != {row["source_row_id"] for row in rows}
        or len({row["load_case_id"] for row in rows}) != 1
    ):
        return hold(
            "EDGE.STATION_INVENTORY_HELD",
            "required_source_row_ids",
            "The supplied rows must match one complete declared station inventory.",
        )
    topology = transfer.primary_topology
    if len(topology.supports) != 2 or len(topology.spans) != 1:
        return hold(
            "EDGE.TOPOLOGY_HELD",
            "transfer.primary_topology",
            "This profile requires one simply supported span.",
        )
    left, right = sorted(topology.supports, key=lambda item: item.centre_x_mm)
    if (
        link.paths != transfer.primary_paths
        or not isclose(link.required_start_mm, left.centre_x_mm, abs_tol=1e-9)
        or not isclose(link.required_end_mm, right.centre_x_mm, abs_tol=1e-9)
        or any(
            row["member_id"] != transfer.member_id
            or row["axis_id"] != topology.local_axes.axis_id
            or row["physical_span_id"] != topology.spans[0].span_id
            or row["concurrency"] != "static_concurrent"
            or row["p_n"] != 0
            or not left.centre_x_mm <= row["object_station_mm"] <= right.centre_x_mm
            for row in rows
        )
    ):
        return hold(
            "EDGE.SOURCE_BINDING_HELD",
            "transfer",
            "The same member, axes, span, concurrent rows and full-length link path must bind all checks.",
        )

    if len(rows) != len(required) or not any(row["t_nmm"] for row in rows):
        return hold(
            "EDGE.TORQUE_ROWS_HELD",
            "transfer.action_snapshot",
            "Supply distinct same-station rows with an applied equilibrium-torsion action.",
        )
    section = transfer.primary_section
    main_paths = tuple(
        path
        for path in transfer.primary_paths.paths
        if path.role in (BarPathRole.TOP_LONGITUDINAL, BarPathRole.BOTTOM_LONGITUDINAL)
    )
    if any(
        path.steel_grade_n_per_mm2 != section.steel_yield_strength_n_per_mm2
        for path in main_paths
    ):
        return hold(
            "EDGE.MATERIAL_BINDING_HELD",
            "transfer.primary_paths",
            "The longitudinal paths and section resistance must use the same steel grade.",
        )
    perimeter = tuple(bar.bar_id for bar in section.bars)
    checks = tuple(
        check_torsion(
            TorsionCheckRequest(
                transfer.profile_id,
                ConcurrentActionRow(
                    row["source_row_id"],
                    f"station-{row['object_station_mm']:g}",
                    ActionBasis.STATIC_CONCURRENT,
                    row["v2_n"] / 1000,
                    row["v3_n"] / 1000,
                    row["t_nmm"] / 1e6,
                    row["m2_nmm"] / 1e6,
                    row["m3_nmm"] / 1e6,
                    row["row_id"],
                ),
                section,
                link.link,
                perimeter,
            )
        )
        for row in rows
    )
    anchors = []
    for support, face, direction in (
        (left, left.right_face_x_mm, AnchorageDirection.DECREASING_X),
        (right, right.left_face_x_mm, AnchorageDirection.INCREASING_X),
    ):
        anchor_paths = []
        for seed in transfer.primary_paths.paths:
            if (
                seed.role
                not in (
                    BarPathRole.TOP_LONGITUDINAL,
                    BarPathRole.BOTTOM_LONGITUDINAL,
                )
                or len(seed.nodes) != 2
            ):
                continue
            start, end = (node.point.station_x_mm for node in seed.nodes)
            anchor_paths.append(
                AnchoragePath(
                    seed.bar_id,
                    support.support_id,
                    AnchorageLocation.DIRECT_SUPPORT,
                    direction,
                    start,
                    end,
                    face,
                    support.support_id,
                    face,
                    support.centre_x_mm,
                    (),
                    None,
                    DevelopmentLengthRequest(
                        transfer.profile_id,
                        seed.diameter_mm,
                        0.87 * section.steel_yield_strength_n_per_mm2,
                        section.steel_yield_strength_n_per_mm2,
                        section.concrete_strength_n_per_mm2,
                        BarSurface.DEFORMED,
                        StressState.TENSION,
                    ),
                )
            )
        anchors.append(
            check_anchorage(
                AnchorageCheckRequest(
                    transfer.profile_id,
                    transfer.member_id,
                    transfer.reinforcement_revision_id,
                    tuple(anchor_paths),
                )
            )
        )
    hooks = check_closed_link_detail(link)
    outputs.update(
        station_checks=tuple(check.to_dict() for check in checks),
        anchors=tuple(leaf.to_dict() for leaf in anchors),
        link_detail=hooks.to_dict(),
    )
    leaves = (*checks, *anchors, hooks)
    if request.load_path_reference and transfer.supports:
        transfer_check = check_torsion_support_transfer(transfer)
        outputs["transfer"] = transfer_check.to_dict()
        leaves += (transfer_check,)
    missing_transfer = outputs["transfer"] is None
    diagnostics = tuple(item for leaf in leaves for item in leaf.diagnostics)
    if missing_transfer:
        diagnostics += (
            _issue(
                "EDGE.TRANSFER_HELD",
                "load_path_reference",
                "The signed torque transfer and physical receiving supports are required.",
            ),
        )
    if any(
        leaf.execution is ExecutionState.COMPLETED
        and leaf.engineering is EngineeringState.FAIL
        for leaf in leaves
    ):
        status = EngineeringState.FAIL
    elif not missing_transfer and all(
        leaf.execution is ExecutionState.COMPLETED
        and leaf.engineering is EngineeringState.PASS
        and leaf.completeness is CompletenessState.COMPLETE_FOR_SCOPE
        and leaf.freshness is FreshnessState.CURRENT
        for leaf in leaves
    ):
        status = EngineeringState.PASS
    else:
        return partial_result(
            EDGE_TORSION_OPERATION, inputs, outputs, diagnostics, provenance=_PROVENANCE
        )
    outputs["governing_primary_moment_row_id"] = max(
        checks,
        key=lambda item: item.outputs.get("primary_equivalent_moment_knm", 0),
    ).outputs.get("action_row_id")
    return completed_result(
        EDGE_TORSION_OPERATION,
        inputs,
        outputs,
        engineering=status,
        diagnostics=diagnostics,
        provenance=_PROVENANCE,
    )
