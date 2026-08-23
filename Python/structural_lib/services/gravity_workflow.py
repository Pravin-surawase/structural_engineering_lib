# SPDX-License-Identifier: MIT
"""Fail-closed component orchestration for Building Gravity Workflow V1."""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from typing import Literal

from structural_lib.codes.is456.load_analysis import compute_bmd_sfd
from structural_lib.core.building_gravity import (
    GravityLoadCaseV1,
    GravityMemberKindV1,
    GravityMemberV1,
    GravityNodeV1,
)
from structural_lib.core.data_types import FootingType, LoadDefinition, LoadType
from structural_lib.core.gravity_workflow import (
    ComponentApplicabilityMatrixV1,
    GravityComponentApplicabilityV1,
    GravityComponentKindV1,
    GravityComponentResultV1,
    GravityFootingDesignBasisV1,
    GravityMemberActionV1,
    GravityPracticalActionReconciliationV1,
    GravityPrerequisiteDispositionV1,
    GravityWorkflowRequestV1,
    GravityWorkflowResultV1,
)
from structural_lib.core.result_contract import (
    CalculationStatus,
    EngineeringStatus,
    IntakeStatus,
    StructuralIssueV1,
    StructuralResultEnvelopeV2,
)
from structural_lib.services.beam_api import design_beam_is456
from structural_lib.services.beam_reinforcement import (
    BeamReinforcementSelectionConstraintsV1,
    LongitudinalBarLayersV1,
    SuppliedBeamReinforcementV1,
    evaluate_supplied_beam_reinforcement_v1,
)
from structural_lib.services.column_api import design_column_is456
from structural_lib.services.footing_api import (
    ConcentricIsolatedFootingInput,
    design_concentric_isolated_footing_is456,
)
from structural_lib.services.gravity_loads import (
    GravityBalanceBoundaryV1,
    GravityLedgerEntryV1,
    GravityLedgerStageV1,
    GravityLoadLedgerV1,
    build_gravity_load_ledger_v1,
)
from structural_lib.services.serialization import to_transport_value
from structural_lib.services.slab_api import design_complete_one_way_slab_is456

__all__ = [
    "GravityWorkflowRequestV1",
    "build_component_applicability_matrix_v1",
    "build_gravity_member_actions_v1",
    "run_gravity_workflow_v1",
]

_LIMITATIONS = (
    "One rectangular one-storey, one-panel, two-beam, four-column topology only.",
    "Dead and unreduced live gravity actions only; no lateral loads.",
    "Practical actions require explicit caller assignment; no load generation or destination inference.",
    "Full-span line, beam point, and supported slab-area actions only.",
    "Closed-form simply supported actions only; no stiffness or frame solver.",
    "Footing design requires a complete external service/soil/detailing basis.",
    "Qualified structural-engineering review remains required.",
)

_SLAB_GENERATED = (
    "short_effective_span_mm",
    "long_effective_span_mm",
    "thickness_mm",
    "factored_area_load_kn_per_m2",
    "fck_n_per_mm2",
)
_SLAB_SUPPLIED = (
    "d_mm",
    "fy_nmm2",
    "provided main/distribution reinforcement",
    "reviewed serviceability limit and acceptance references",
)
_BEAM_GENERATED = ("b_mm", "D_mm", "Mu_knm", "Vu_kn", "fck_nmm2")
_BEAM_SUPPLIED = (
    "d_mm and source reference",
    "fy_nmm2",
    "shear reinforcement basis",
    "bar-selection constraints",
    "source-referenced supplied longitudinal reinforcement",
)
_COLUMN_GENERATED = (
    "Pu_kN",
    "b_mm",
    "D_mm",
    "l_mm",
    "fck_nmm2",
)
_COLUMN_SUPPLIED = (
    "fy_nmm2",
    "Asc_mm2",
    "d_prime_mm",
    "end condition and reinforcement references",
)
_FOOTING_GENERATED = (
    "column_L_mm",
    "column_B_mm",
    "column_concrete_fck_nmm2",
    "superstructure service/factored axial handoff",
)
_FOOTING_SUPPLIED = (
    "complete service action including footing self-weight and overburden",
    "complete factored action",
    "externally approved allowable soil pressure",
    "thickness/effective-depth/load-transfer basis",
)


def _envelope(
    *,
    intake: IntakeStatus,
    calculation: CalculationStatus,
    engineering: EngineeringStatus,
    issues: Iterable[StructuralIssueV1] = (),
) -> dict[str, object]:
    return StructuralResultEnvelopeV2(
        intake_status=intake,
        calculation_status=calculation,
        engineering_status=engineering,
        issues=tuple(issues),
    ).to_dict()


def _hold_component(
    *,
    component_id: str,
    kind: GravityComponentKindV1,
    function: str,
    action_ids: tuple[str, ...],
    code: str,
    message: str,
) -> GravityComponentResultV1:
    return GravityComponentResultV1(
        component_id=component_id,
        kind=kind,
        canonical_function=function,
        action_ids=action_ids,
        result_envelope=_envelope(
            intake=IntakeStatus.PARTIAL,
            calculation=CalculationStatus.NOT_EVALUATED,
            engineering=EngineeringStatus.HOLD,
            issues=(
                StructuralIssueV1(
                    code=code,
                    path=f"$.components.{component_id}",
                    message=message,
                ),
            ),
        ),
    )


def _error_component(
    *,
    component_id: str,
    kind: GravityComponentKindV1,
    function: str,
    action_ids: tuple[str, ...],
    exc: Exception,
) -> GravityComponentResultV1:
    return GravityComponentResultV1(
        component_id=component_id,
        kind=kind,
        canonical_function=function,
        action_ids=action_ids,
        result_envelope=_envelope(
            intake=IntakeStatus.VALID,
            calculation=CalculationStatus.ERROR,
            engineering=EngineeringStatus.HOLD,
            issues=(
                StructuralIssueV1(
                    code="COMPONENT_CALCULATION_ERROR",
                    path=f"$.components.{component_id}",
                    message=f"{type(exc).__name__}: {exc}",
                ),
            ),
        ),
    )


def _member_length_mm(
    member: GravityMemberV1, nodes: dict[str, GravityNodeV1]
) -> float:
    start = nodes[member.start_node_id]
    end = nodes[member.end_node_id]
    return math.dist(
        (
            start.x_mm,
            start.y_mm,
            start.z_mm,
        ),
        (
            end.x_mm,
            end.y_mm,
            end.z_mm,
        ),
    )


def _required_dimension(value: float | None, name: str) -> float:
    if value is None:
        raise ValueError(f"validated component section is missing {name}")
    return value


def _beam_support_widths(
    member: GravityMemberV1,
    *,
    members: tuple[GravityMemberV1, ...],
    sections: Mapping[str, object],
) -> tuple[float | None, float | None, str | None]:
    """Resolve unambiguous square-column support widths from the physical model."""

    widths: list[float] = []
    column_ids: list[str] = []
    for node_id in (member.start_node_id, member.end_node_id):
        supporting_columns = tuple(
            item
            for item in members
            if item.kind is GravityMemberKindV1.COLUMN and item.end_node_id == node_id
        )
        if len(supporting_columns) != 1:
            return None, None, None
        column = supporting_columns[0]
        section = sections[column.section_id]
        width_mm = getattr(section, "width_mm", None)
        depth_mm = getattr(section, "depth_mm", None)
        if (
            width_mm is None
            or depth_mm is None
            or not math.isclose(width_mm, depth_mm, rel_tol=0.0, abs_tol=1e-9)
        ):
            return None, None, None
        widths.append(float(width_mm))
        column_ids.append(column.id)
    return (
        widths[0],
        widths[1],
        "BuildingModelV1 square column sections at beam ends: " + ", ".join(column_ids),
    )


def _beam_reinforcement_hold_payload(code: str, message: str) -> dict[str, object]:
    return {
        "schema_version": "beam-reinforcement-evaluation/v1",
        "status": "HOLD",
        "recommended_tension": None,
        "supplied_tension": None,
        "supplied_compression_or_hanger": None,
        "checks": {"supply_complete": False},
        "issues": [{"code": code, "message": message}],
        "limitations": [
            "Required steel remains a design demand, not supplied detailing.",
            "Qualified structural-engineering review remains required.",
        ],
        "qualified_review_required": True,
    }


def _beam_envelope_with_reinforcement(
    *,
    component_id: str,
    original: dict[str, object],
    reinforcement: dict[str, object],
) -> dict[str, object]:
    """Preserve canonical design failures, otherwise govern by supplied bars."""

    if _result_status(original) != "PASS":
        return original
    status = str(reinforcement["status"])
    if status == "PASS":
        return original
    issue_values = reinforcement.get("issues")
    issues: list[StructuralIssueV1] = []
    if isinstance(issue_values, list):
        for value in issue_values:
            if isinstance(value, dict):
                issues.append(
                    StructuralIssueV1(
                        code=str(value.get("code", "BEAM_REINFORCEMENT_HOLD")),
                        path=(
                            f"$.components.{component_id}.result."
                            "reinforcement_evaluation"
                        ),
                        message=str(
                            value.get(
                                "message",
                                "Beam reinforcement evaluation is incomplete.",
                            )
                        ),
                    )
                )
    if not issues:
        issues.append(
            StructuralIssueV1(
                code=f"BEAM_REINFORCEMENT_{status}",
                path=f"$.components.{component_id}.result.reinforcement_evaluation",
                message=f"Supplied beam reinforcement governs as {status}.",
            )
        )
    return _envelope(
        intake=(IntakeStatus.PARTIAL if status == "HOLD" else IntakeStatus.VALID),
        calculation=CalculationStatus.COMPLETED,
        engineering=(
            EngineeringStatus.HOLD if status == "HOLD" else EngineeringStatus.FAIL
        ),
        issues=issues,
    )


def _factor_map(
    request: GravityWorkflowRequestV1,
    combination_id: Literal["SERVICE_DL_LL", "ULS_1_5_DL_LL"],
) -> dict[GravityLoadCaseV1, float]:
    combination = next(
        item for item in request.loads.combinations if item.id == combination_id
    )
    return {factor.case_id: factor.factor for factor in combination.factors}


def _entries_for(
    ledger: GravityLoadLedgerV1,
    *,
    stage: GravityLedgerStageV1,
    destination_id: str,
) -> tuple[GravityLedgerEntryV1, ...]:
    return tuple(
        item
        for item in ledger.entries
        if item.stage is stage and item.destination_id == destination_id
    )


def build_gravity_member_actions_v1(
    request: GravityWorkflowRequestV1,
    ledger: GravityLoadLedgerV1,
) -> tuple[GravityMemberActionV1, ...]:
    """Derive service/factored component actions from the reconciled B1 ledger."""

    nodes = {item.id: item for item in request.building.nodes}
    panel = request.building.panels[0]
    x_values = [nodes[node_id].x_mm for node_id in panel.corner_node_ids]
    y_values = [nodes[node_id].y_mm for node_id in panel.corner_node_ids]
    panel_area_m2 = (
        (max(x_values) - min(x_values)) * (max(y_values) - min(y_values)) / 1_000_000.0
    )
    actions: list[GravityMemberActionV1] = []

    panel_sources = _entries_for(
        ledger, stage=GravityLedgerStageV1.SOURCE, destination_id=panel.id
    )
    beams = tuple(
        item
        for item in request.building.members
        if item.kind is GravityMemberKindV1.BEAM
    )
    columns = tuple(
        item
        for item in request.building.members
        if item.kind is GravityMemberKindV1.COLUMN
    )
    footing_by_column = {
        item.column_id: item for item in request.building.footing_destinations
    }

    combinations: tuple[
        tuple[
            Literal["SERVICE_DL_LL", "ULS_1_5_DL_LL"],
            Literal["SERVICE", "FACTORED"],
        ],
        ...,
    ] = (
        ("SERVICE_DL_LL", "SERVICE"),
        ("ULS_1_5_DL_LL", "FACTORED"),
    )
    for combination_id, state in combinations:
        factors = _factor_map(request, combination_id)
        panel_total = math.fsum(
            item.magnitude_kn * factors[item.case_id] for item in panel_sources
        )
        actions.append(
            GravityMemberActionV1(
                action_id=f"action:{combination_id}:{panel.id}",
                component_id=panel.id,
                kind=GravityComponentKindV1.SLAB,
                combination_id=combination_id,
                state=state,
                area_load_kn_m2=panel_total / panel_area_m2,
                source_entry_ids=tuple(sorted(item.entry_id for item in panel_sources)),
                sign_convention="DOWNWARD_AREA_LOAD_POSITIVE",
            )
        )

        for beam in beams:
            line_entries = _entries_for(
                ledger,
                stage=GravityLedgerStageV1.BEAM_LINE,
                destination_id=beam.id,
            )
            point_entries = _entries_for(
                ledger,
                stage=GravityLedgerStageV1.BEAM_POINT,
                destination_id=beam.id,
            )
            line_load = math.fsum(
                (item.line_load_kn_m or 0.0) * factors[item.case_id]
                for item in line_entries
            )
            span_mm = _member_length_mm(beam, nodes)
            applied_loads = [LoadDefinition(LoadType.UDL, magnitude=line_load)]
            applied_loads.extend(
                LoadDefinition(
                    LoadType.POINT,
                    magnitude=(item.point_load_kn or 0.0) * factors[item.case_id],
                    position_mm=item.point_position_mm or 0.0,
                )
                for item in point_entries
            )
            diagram = compute_bmd_sfd(
                span_mm=span_mm,
                support_condition="simply_supported",
                loads=applied_loads,
                num_points=2,
            )
            actions.append(
                GravityMemberActionV1(
                    action_id=f"action:{combination_id}:{beam.id}",
                    component_id=beam.id,
                    kind=GravityComponentKindV1.BEAM,
                    combination_id=combination_id,
                    state=state,
                    line_load_kn_m=line_load,
                    moment_knm=max(abs(diagram.max_bm_knm), abs(diagram.min_bm_knm)),
                    shear_kn=max(abs(diagram.max_sf_kn), abs(diagram.min_sf_kn)),
                    source_entry_ids=tuple(
                        sorted(
                            item.entry_id for item in (*line_entries, *point_entries)
                        )
                    ),
                    sign_convention=(
                        "SAGGING_MOMENT_POSITIVE; SUPPORT_SHEAR_ABSOLUTE_DESIGN_MAGNITUDE"
                    ),
                )
            )

        for column in columns:
            column_entries = _entries_for(
                ledger,
                stage=GravityLedgerStageV1.COLUMN_ACTION,
                destination_id=column.id,
            )
            axial = math.fsum(
                item.magnitude_kn * factors[item.case_id] for item in column_entries
            )
            source_ids = tuple(sorted(item.entry_id for item in column_entries))
            actions.append(
                GravityMemberActionV1(
                    action_id=f"action:{combination_id}:{column.id}",
                    component_id=column.id,
                    kind=GravityComponentKindV1.COLUMN,
                    combination_id=combination_id,
                    state=state,
                    axial_kn=axial,
                    source_entry_ids=source_ids,
                    sign_convention="AXIAL_COMPRESSION_POSITIVE",
                )
            )
            footing = footing_by_column[column.id]
            footing_entries = _entries_for(
                ledger,
                stage=GravityLedgerStageV1.FOOTING_ACTION,
                destination_id=footing.id,
            )
            footing_axial = math.fsum(
                item.magnitude_kn * factors[item.case_id] for item in footing_entries
            )
            actions.append(
                GravityMemberActionV1(
                    action_id=f"action:{combination_id}:{footing.id}",
                    component_id=footing.id,
                    kind=GravityComponentKindV1.FOOTING,
                    combination_id=combination_id,
                    state=state,
                    axial_kn=footing_axial,
                    source_entry_ids=tuple(
                        sorted(item.entry_id for item in footing_entries)
                    ),
                    sign_convention="CONCENTRIC_AXIAL_COMPRESSION_POSITIVE",
                )
            )
    return tuple(sorted(actions, key=lambda item: item.action_id))


def _practical_action_reconciliation(
    request: GravityWorkflowRequestV1,
    ledger: GravityLoadLedgerV1,
) -> tuple[GravityPracticalActionReconciliationV1, ...]:
    records: list[GravityPracticalActionReconciliationV1] = []
    for action in request.loads.practical_actions:
        matching = tuple(
            item for item in ledger.entries if item.practical_action_id == action.id
        )
        sources = tuple(
            item for item in matching if item.stage is GravityLedgerStageV1.SOURCE
        )
        destinations = tuple(
            item
            for item in matching
            if item.stage
            in {GravityLedgerStageV1.BEAM_LINE, GravityLedgerStageV1.BEAM_POINT}
        )
        balances = tuple(
            item
            for item in ledger.balances
            if item.boundary is GravityBalanceBoundaryV1.PRACTICAL_ACTION_ASSIGNMENT
            and item.source_id == action.id
        )
        if len(sources) != 1 or not destinations or len(balances) != 1:
            raise ValueError(
                f"practical action {action.id} lacks one exact ledger reconciliation"
            )
        source = sources[0]
        balance = balances[0]
        records.append(
            GravityPracticalActionReconciliationV1(
                action_id=action.id,
                kind=action.kind,
                source_category=action.source_category,
                case_id=action.case_id,
                source_identity=action.source_identity,
                source_ref_id=action.source_ref_id,
                destination_id=action.destination_id,
                supplied_magnitude=action.magnitude,
                units=action.units,
                point_position_mm=action.point_position_mm,
                assignment_basis=action.assignment_basis,
                source_entry_id=source.entry_id,
                destination_entry_ids=tuple(
                    sorted(item.entry_id for item in destinations)
                ),
                source_total_kn=balance.source_total_kn,
                destination_total_kn=balance.destination_total_kn,
                residual_kn=balance.residual_kn,
                tolerance_kn=balance.tolerance_kn,
                reconciled=balance.passed,
            )
        )
    return tuple(sorted(records, key=lambda item: item.action_id))


def _basis_ids(values: Iterable[object], name: str) -> set[str]:
    return {str(getattr(item, name)) for item in values}


def build_component_applicability_matrix_v1(
    request: GravityWorkflowRequestV1,
) -> ComponentApplicabilityMatrixV1:
    """Declare every component prerequisite before invoking any design function."""

    entries: list[GravityComponentApplicabilityV1] = []
    slab_basis_ids = _basis_ids(request.slab_design_bases, "panel_id")
    beam_basis_ids = _basis_ids(request.beam_design_bases, "beam_id")
    column_basis_ids = _basis_ids(request.column_design_bases, "column_id")
    footing_basis_ids = _basis_ids(request.footing_design_bases, "footing_id")
    nodes = {item.id: item for item in request.building.nodes}

    panel = request.building.panels[0]
    x_values = {nodes[node_id].x_mm for node_id in panel.corner_node_ids}
    y_values = {nodes[node_id].y_mm for node_id in panel.corner_node_ids}
    length_x = max(x_values) - min(x_values)
    span_y = max(y_values) - min(y_values)
    slab_holds: list[str] = []
    if panel.id not in slab_basis_ids:
        slab_holds.append("SLAB_DESIGN_BASIS_NOT_SUPPLIED")
    if length_x / span_y <= 2.0:
        slab_holds.append("SLAB_COMPONENT_REQUIRES_EFFECTIVE_ASPECT_RATIO_GT_2")
    entries.append(
        GravityComponentApplicabilityV1(
            component_id=panel.id,
            kind=GravityComponentKindV1.SLAB,
            canonical_function="design_complete_one_way_slab_is456",
            supported_case_id="simply_supported_one_way_solid_slab_strip",
            required_generated_inputs=_SLAB_GENERATED,
            required_supplied_inputs=_SLAB_SUPPLIED,
            disposition=(
                GravityPrerequisiteDispositionV1.HOLD
                if slab_holds
                else GravityPrerequisiteDispositionV1.READY
            ),
            hold_reasons=tuple(slab_holds),
        )
    )
    for member in request.building.members:
        generated: tuple[str, ...]
        supplied: tuple[str, ...]
        if member.kind is GravityMemberKindV1.BEAM:
            kind = GravityComponentKindV1.BEAM
            basis_ids = beam_basis_ids
            function = "design_beam_is456"
            supported = "simply_supported_rectangular_beam_factored_explicit_actions"
            generated, supplied = _BEAM_GENERATED, _BEAM_SUPPLIED
            reason = "BEAM_DESIGN_BASIS_NOT_SUPPLIED"
        else:
            kind = GravityComponentKindV1.COLUMN
            basis_ids = column_basis_ids
            function = "design_column_is456"
            supported = "braced_rectangular_column_axial_only"
            generated, supplied = _COLUMN_GENERATED, _COLUMN_SUPPLIED
            reason = "COLUMN_DESIGN_BASIS_NOT_SUPPLIED"
        holds = () if member.id in basis_ids else (reason,)
        entries.append(
            GravityComponentApplicabilityV1(
                component_id=member.id,
                kind=kind,
                canonical_function=function,
                supported_case_id=supported,
                required_generated_inputs=generated,
                required_supplied_inputs=supplied,
                disposition=(
                    GravityPrerequisiteDispositionV1.READY
                    if not holds
                    else GravityPrerequisiteDispositionV1.HOLD
                ),
                hold_reasons=holds,
            )
        )
    for footing in request.building.footing_destinations:
        holds = (
            ()
            if footing.id in footing_basis_ids
            else ("FOOTING_EXTERNAL_SERVICE_SOIL_BASIS_NOT_SUPPLIED",)
        )
        entries.append(
            GravityComponentApplicabilityV1(
                component_id=footing.id,
                kind=GravityComponentKindV1.FOOTING,
                canonical_function="design_concentric_isolated_footing_is456",
                supported_case_id="concentric_centred_isolated_square_or_rectangular_footing",
                required_generated_inputs=_FOOTING_GENERATED,
                required_supplied_inputs=_FOOTING_SUPPLIED,
                disposition=(
                    GravityPrerequisiteDispositionV1.READY
                    if not holds
                    else GravityPrerequisiteDispositionV1.HOLD
                ),
                hold_reasons=holds,
            )
        )
    return ComponentApplicabilityMatrixV1(
        entries=tuple(sorted(entries, key=lambda item: item.component_id))
    )


def _action(
    actions: tuple[GravityMemberActionV1, ...], component_id: str, combination_id: str
) -> GravityMemberActionV1:
    return next(
        item
        for item in actions
        if item.component_id == component_id and item.combination_id == combination_id
    )


def _result_status(result_envelope: dict[str, object]) -> str:
    return str(result_envelope["overall_status"])


def _with_fallback_component_issue(
    envelope: dict[str, object],
    *,
    component_id: str,
    kind: GravityComponentKindV1,
    message: str | None = None,
) -> dict[str, object]:
    """Ensure every non-pass component has one directly discoverable reason."""

    status = _result_status(envelope)
    issues = envelope.get("issues")
    if status == "PASS" or (isinstance(issues, list) and issues):
        return envelope
    issue = StructuralIssueV1(
        code=f"{kind.value}_GOVERNING_{status}",
        path=f"$.components.{component_id}",
        message=message
        or (
            f"{kind.value.title()} component {component_id} governs as {status}; "
            "inspect its component result for the failed or held check."
        ),
    )
    return {**envelope, "issues": [issue.to_dict()]}


def _governing_component_issue(
    components: tuple[GravityComponentResultV1, ...],
    governing_statuses: frozenset[str],
) -> StructuralIssueV1 | None:
    """Select one deterministic component reason for the aggregate envelope."""

    component = next(
        (
            item
            for item in components
            if _result_status(item.result_envelope) in governing_statuses
        ),
        None,
    )
    if component is None:
        return None
    issues = component.result_envelope.get("issues")
    if isinstance(issues, list) and issues and isinstance(issues[0], dict):
        issue = issues[0]
        return StructuralIssueV1(
            code=str(issue.get("code", "GOVERNING_COMPONENT_ISSUE")),
            path=str(issue.get("path", f"$.components.{component.component_id}")),
            message=str(issue.get("message", "Governing component issue.")),
        )
    status = _result_status(component.result_envelope)
    return StructuralIssueV1(
        code=f"GOVERNING_COMPONENT_{status}",
        path=f"$.components.{component.component_id}",
        message=(
            f"{component.kind.value.title()} component {component.component_id} "
            f"governs the workflow as {status}."
        ),
    )


def _aggregate_envelope(
    components: tuple[GravityComponentResultV1, ...],
) -> dict[str, object]:
    statuses = [_result_status(item.result_envelope) for item in components]
    if "BLOCKED" in statuses:
        issue = _governing_component_issue(components, frozenset({"BLOCKED"}))
        return _envelope(
            intake=IntakeStatus.BLOCKED,
            calculation=CalculationStatus.NOT_EVALUATED,
            engineering=EngineeringStatus.NOT_EVALUATED,
            issues=() if issue is None else (issue,),
        )
    if "ERROR" in statuses:
        issue = _governing_component_issue(components, frozenset({"ERROR"}))
        return _envelope(
            intake=IntakeStatus.VALID,
            calculation=CalculationStatus.ERROR,
            engineering=EngineeringStatus.HOLD,
            issues=() if issue is None else (issue,),
        )
    if any(status in {"HOLD", "NOT_EVALUATED"} for status in statuses):
        issue = _governing_component_issue(
            components, frozenset({"HOLD", "NOT_EVALUATED"})
        )
        return _envelope(
            intake=IntakeStatus.PARTIAL,
            calculation=CalculationStatus.NOT_EVALUATED,
            engineering=EngineeringStatus.HOLD,
            issues=() if issue is None else (issue,),
        )
    issue = _governing_component_issue(components, frozenset({"FAIL"}))
    return _envelope(
        intake=IntakeStatus.VALID,
        calculation=CalculationStatus.COMPLETED,
        engineering=(
            EngineeringStatus.FAIL if "FAIL" in statuses else EngineeringStatus.PASS
        ),
        issues=() if issue is None else (issue,),
    )


def _footing_request(
    basis: GravityFootingDesignBasisV1,
    *,
    column_width_mm: float,
    column_depth_mm: float,
    column_fck_nmm2: float,
) -> ConcentricIsolatedFootingInput:
    footing_type = (
        FootingType.ISOLATED_SQUARE
        if basis.footing_type == "SQUARE"
        else FootingType.ISOLATED_RECTANGULAR
    )
    return ConcentricIsolatedFootingInput(
        case_id=basis.footing_id,
        service_axial_load_kN=basis.complete_service_axial_load_kn,
        service_load_combination_id=basis.service_load_combination_id,
        service_load_basis=basis.service_load_basis,
        service_load_origin=basis.service_load_origin,
        factored_axial_load_kN=basis.complete_factored_axial_load_kn,
        factored_load_combination_id=basis.factored_load_combination_id,
        allowable_soil_pressure_kPa=basis.allowable_soil_pressure_kpa,
        allowable_soil_pressure_source_reference=(
            basis.allowable_soil_pressure_source_reference
        ),
        allowable_soil_pressure_origin=basis.allowable_soil_pressure_origin,
        allowable_soil_pressure_is_externally_approved=(
            basis.allowable_soil_pressure_is_externally_approved
        ),
        footing_type=footing_type,
        column_L_mm=column_depth_mm,
        column_B_mm=column_width_mm,
        minimum_overall_thickness_mm=basis.minimum_overall_thickness_mm,
        maximum_overall_thickness_mm=basis.maximum_overall_thickness_mm,
        thickness_increment_mm=basis.thickness_increment_mm,
        effective_depth_offset_L_mm=basis.effective_depth_offset_l_mm,
        effective_depth_offset_B_mm=basis.effective_depth_offset_b_mm,
        footing_concrete_fck_nmm2=basis.footing_concrete_fck_nmm2,
        column_concrete_fck_nmm2=column_fck_nmm2,
        steel_fy_nmm2=basis.steel_fy_nmm2,
        effective_supporting_area_A1_mm2=basis.effective_supporting_area_a1_mm2,
        effective_supporting_area_basis=basis.effective_supporting_area_basis,
        effective_supporting_area_origin=basis.effective_supporting_area_origin,
        effective_supporting_area_is_approved=(
            basis.effective_supporting_area_is_approved
        ),
        dowel_count=basis.dowel_count,
        dowel_diameter_mm=basis.dowel_diameter_mm,
        column_longitudinal_bar_diameter_mm=(basis.column_longitudinal_bar_diameter_mm),
        available_dowel_development_length_into_footing_mm=(
            basis.available_dowel_development_length_into_footing_mm
        ),
        available_dowel_development_length_into_column_mm=(
            basis.available_dowel_development_length_into_column_mm
        ),
        dowel_bar_type=basis.dowel_bar_type,
        nominal_cover_mm=basis.nominal_cover_mm,
        cover_exposure_basis=basis.cover_exposure_basis,
        cover_exposure_basis_is_approved=basis.cover_exposure_basis_is_approved,
        nominal_max_aggregate_size_mm=basis.nominal_max_aggregate_size_mm,
        lower_bottom_bar_direction=basis.lower_bottom_bar_direction,
        upper_bottom_bar_direction=basis.upper_bottom_bar_direction,
        permitted_bottom_bar_diameters_mm=basis.permitted_bottom_bar_diameters_mm,
        footing_bottom_bar_type=basis.footing_bottom_bar_type,
        bottom_bar_end_arrangement=basis.bottom_bar_end_arrangement,
        bend_internal_radius_mm=basis.bend_internal_radius_mm,
        extension_after_bend_mm=basis.extension_after_bend_mm,
        bend_geometry_source_reference=basis.bend_geometry_source_reference,
        bend_geometry_source_is_approved=(basis.bend_geometry_source_is_approved),
    )


def run_gravity_workflow_v1(
    request: GravityWorkflowRequestV1,
) -> GravityWorkflowResultV1:
    """Run the bounded V1 ledger, exact actions, and conditional components."""

    ledger = build_gravity_load_ledger_v1(request.building, request.loads)
    actions = build_gravity_member_actions_v1(request, ledger)
    applicability = build_component_applicability_matrix_v1(request)
    applicability_by_id = {item.component_id: item for item in applicability.entries}
    sections = {item.id: item for item in request.building.sections}
    materials = {item.id: item for item in request.building.materials}
    nodes = {item.id: item for item in request.building.nodes}
    slab_bases = {item.panel_id: item for item in request.slab_design_bases}
    beam_bases = {item.beam_id: item for item in request.beam_design_bases}
    column_bases = {item.column_id: item for item in request.column_design_bases}
    footing_bases = {item.footing_id: item for item in request.footing_design_bases}
    components: list[GravityComponentResultV1] = []

    panel = request.building.panels[0]
    slab_action = _action(actions, panel.id, "ULS_1_5_DL_LL")
    slab_applicability = applicability_by_id[panel.id]
    if slab_applicability.disposition is GravityPrerequisiteDispositionV1.HOLD:
        components.append(
            _hold_component(
                component_id=panel.id,
                kind=GravityComponentKindV1.SLAB,
                function=slab_applicability.canonical_function,
                action_ids=(slab_action.action_id,),
                code=";".join(slab_applicability.hold_reasons),
                message="Slab component prerequisites are incomplete or unsupported.",
            )
        )
    else:
        slab_basis = slab_bases[panel.id]
        section = sections[panel.section_id]
        material = materials[section.material_id]
        x_values = [nodes[node_id].x_mm for node_id in panel.corner_node_ids]
        y_values = [nodes[node_id].y_mm for node_id in panel.corner_node_ids]
        try:
            slab_result = design_complete_one_way_slab_is456(
                short_effective_span_mm=max(y_values) - min(y_values),
                long_effective_span_mm=max(x_values) - min(x_values),
                thickness_mm=_required_dimension(
                    section.thickness_mm, "slab thickness_mm"
                ),
                d_mm=slab_basis.d_mm,
                factored_area_load_kn_per_m2=_required_dimension(
                    slab_action.area_load_kn_m2, "slab factored area action"
                ),
                fck_n_per_mm2=material.fck_nmm2,
                fy_n_per_mm2=slab_basis.fy_nmm2,
                main_bar_diameter_mm=slab_basis.main_bar_diameter_mm,
                main_bar_spacing_mm=slab_basis.main_bar_spacing_mm,
                distribution_bar_diameter_mm=(slab_basis.distribution_bar_diameter_mm),
                distribution_bar_spacing_mm=slab_basis.distribution_bar_spacing_mm,
                reviewed_base_span_depth_limit=(
                    slab_basis.reviewed_base_span_depth_limit
                ),
                reviewed_aggregate_modification_factor=(
                    slab_basis.reviewed_aggregate_modification_factor
                ),
                serviceability_limit_source_reference=(
                    slab_basis.serviceability_limit_source_reference
                ),
                serviceability_limit_source_is_approved=(
                    slab_basis.serviceability_limit_source_is_approved
                ),
                qualified_serviceability_acceptance_reference=(
                    slab_basis.qualified_serviceability_acceptance_reference
                ),
                qualified_serviceability_acceptance_acknowledged=(
                    slab_basis.qualified_serviceability_acceptance_acknowledged
                ),
            )
            passed = (
                slab_result.reinforcement.is_detailing_adequate
                and slab_result.shear is not None
                and slab_result.shear.is_safe_without_shear_reinforcement
                and slab_result.serviceability is not None
                and slab_result.serviceability.is_satisfied
            )
            slab_envelope = _with_fallback_component_issue(
                _envelope(
                    intake=IntakeStatus.VALID,
                    calculation=CalculationStatus.COMPLETED,
                    engineering=(
                        EngineeringStatus.PASS if passed else EngineeringStatus.FAIL
                    ),
                ),
                component_id=panel.id,
                kind=GravityComponentKindV1.SLAB,
            )
            components.append(
                GravityComponentResultV1(
                    component_id=panel.id,
                    kind=GravityComponentKindV1.SLAB,
                    canonical_function=slab_applicability.canonical_function,
                    action_ids=(slab_action.action_id,),
                    result_envelope=slab_envelope,
                    result=to_transport_value(slab_result),
                )
            )
        except (TypeError, ValueError) as exc:
            components.append(
                _error_component(
                    component_id=panel.id,
                    kind=GravityComponentKindV1.SLAB,
                    function=slab_applicability.canonical_function,
                    action_ids=(slab_action.action_id,),
                    exc=exc,
                )
            )

    for member in request.building.members:
        component_action = _action(actions, member.id, "ULS_1_5_DL_LL")
        applicable = applicability_by_id[member.id]
        kind = (
            GravityComponentKindV1.BEAM
            if member.kind is GravityMemberKindV1.BEAM
            else GravityComponentKindV1.COLUMN
        )
        if applicable.disposition is GravityPrerequisiteDispositionV1.HOLD:
            components.append(
                _hold_component(
                    component_id=member.id,
                    kind=kind,
                    function=applicable.canonical_function,
                    action_ids=(component_action.action_id,),
                    code=applicable.hold_reasons[0],
                    message=f"{kind.value.title()} design basis was not supplied.",
                )
            )
            continue
        section = sections[member.section_id]
        material = materials[section.material_id]
        try:
            if member.kind is GravityMemberKindV1.BEAM:
                beam_basis = beam_bases[member.id]
                beam_result = design_beam_is456(
                    units="IS456",
                    case_id=component_action.action_id,
                    mu_knm=_required_dimension(
                        component_action.moment_knm, "beam factored moment action"
                    ),
                    vu_kn=_required_dimension(
                        component_action.shear_kn, "beam factored shear action"
                    ),
                    b_mm=_required_dimension(section.width_mm, "beam width_mm"),
                    D_mm=_required_dimension(section.depth_mm, "beam depth_mm"),
                    d_mm=beam_basis.d_mm,
                    fck_nmm2=material.fck_nmm2,
                    fy_nmm2=beam_basis.fy_nmm2,
                    d_dash_mm=beam_basis.d_dash_mm,
                    asv_mm2=beam_basis.asv_mm2,
                    pt_percent=beam_basis.pt_percent,
                    ast_mm2_for_shear=beam_basis.ast_mm2_for_shear,
                    cover_mm=beam_basis.cover_mm,
                    stirrup_dia_mm=beam_basis.stirrup_dia_mm,
                )
                result_payload = to_transport_value(beam_result)
                envelope = beam_result.result_envelope or _envelope(
                    intake=IntakeStatus.VALID,
                    calculation=CalculationStatus.COMPLETED,
                    engineering=(
                        EngineeringStatus.PASS
                        if beam_result.is_ok
                        else EngineeringStatus.FAIL
                    ),
                )
                reinforcement_basis = beam_basis.reinforcement_basis
                if reinforcement_basis is None:
                    reinforcement_payload = _beam_reinforcement_hold_payload(
                        "BEAM_REINFORCEMENT_BASIS_NOT_SUPPLIED",
                        "Required steel was calculated, but bar-selection constraints "
                        "and supplied longitudinal reinforcement were not provided.",
                    )
                else:
                    selection = BeamReinforcementSelectionConstraintsV1(
                        permitted_diameters_mm=(
                            reinforcement_basis.permitted_diameters_mm
                        ),
                        maximum_layers=reinforcement_basis.maximum_layers,
                        maximum_bars_per_layer=(
                            reinforcement_basis.maximum_bars_per_layer
                        ),
                        nominal_max_aggregate_size_mm=(
                            reinforcement_basis.nominal_max_aggregate_size_mm
                        ),
                        effective_depth_tolerance_mm=(
                            reinforcement_basis.effective_depth_tolerance_mm
                        ),
                        objective=reinforcement_basis.objective,
                        source_reference=(
                            reinforcement_basis.selection_source_reference
                        ),
                    )
                    supplied = None
                    if (
                        reinforcement_basis.supplied_tension is not None
                        and reinforcement_basis.supplied_compression_or_hanger
                        is not None
                        and reinforcement_basis.supplied_reinforcement_source_reference
                        is not None
                    ):
                        tension = reinforcement_basis.supplied_tension
                        compression = reinforcement_basis.supplied_compression_or_hanger
                        supplied = SuppliedBeamReinforcementV1(
                            tension=LongitudinalBarLayersV1(
                                diameter_mm=tension.diameter_mm,
                                bars_per_layer=tension.bars_per_layer,
                                vertical_center_spacings_mm=(
                                    tension.vertical_center_spacings_mm
                                ),
                            ),
                            compression_or_hanger=LongitudinalBarLayersV1(
                                diameter_mm=compression.diameter_mm,
                                bars_per_layer=compression.bars_per_layer,
                                vertical_center_spacings_mm=(
                                    compression.vertical_center_spacings_mm
                                ),
                            ),
                            bar_type=reinforcement_basis.bar_type,
                            has_standard_bend_at_start=(
                                reinforcement_basis.has_standard_bend_at_start
                            ),
                            has_standard_bend_at_end=(
                                reinforcement_basis.has_standard_bend_at_end
                            ),
                            source_reference=(
                                reinforcement_basis.supplied_reinforcement_source_reference
                            ),
                        )
                    support_start_mm, support_end_mm, support_source = (
                        _beam_support_widths(
                            member,
                            members=request.building.members,
                            sections=sections,
                        )
                    )
                    reinforcement_payload = evaluate_supplied_beam_reinforcement_v1(
                        ast_required_mm2=beam_result.flexure.Ast_required,
                        asc_required_mm2=beam_result.flexure.Asc_required,
                        b_mm=_required_dimension(section.width_mm, "beam width_mm"),
                        D_mm=_required_dimension(section.depth_mm, "beam depth_mm"),
                        d_design_mm=beam_basis.d_mm,
                        d_dash_design_mm=beam_basis.d_dash_mm,
                        cover_mm=_required_dimension(
                            beam_basis.cover_mm, "beam cover_mm"
                        ),
                        stirrup_dia_mm=beam_basis.stirrup_dia_mm,
                        fck_nmm2=material.fck_nmm2,
                        fy_nmm2=beam_basis.fy_nmm2,
                        vu_kn=_required_dimension(
                            component_action.shear_kn,
                            "beam factored shear action",
                        ),
                        support_width_start_mm=support_start_mm,
                        support_width_end_mm=support_end_mm,
                        support_width_source_reference=support_source,
                        selection=selection,
                        supplied=supplied,
                    ).to_dict()
                if not isinstance(result_payload, dict):
                    raise TypeError("beam result must serialize to an object")
                result_payload["reinforcement_evaluation"] = reinforcement_payload
                envelope = _beam_envelope_with_reinforcement(
                    component_id=member.id,
                    original=envelope,
                    reinforcement=reinforcement_payload,
                )
            else:
                column_basis = column_bases[member.id]
                length_mm = _member_length_mm(member, nodes)
                result_payload = design_column_is456(
                    Pu_kN=_required_dimension(
                        component_action.axial_kn, "column factored axial action"
                    ),
                    Mux_kNm=0.0,
                    Muy_kNm=0.0,
                    b_mm=_required_dimension(section.width_mm, "column width_mm"),
                    D_mm=_required_dimension(section.depth_mm, "column depth_mm"),
                    l_mm=length_mm,
                    end_condition=column_basis.end_condition,
                    fck_nmm2=material.fck_nmm2,
                    fy_nmm2=column_basis.fy_nmm2,
                    Asc_mm2=column_basis.Asc_mm2,
                    d_prime_mm=column_basis.d_prime_mm,
                    l_unsupported_mm=length_mm,
                    braced=True,
                )
                envelope = result_payload["result_envelope"]
                result_payload = to_transport_value(result_payload)
            envelope = _with_fallback_component_issue(
                envelope,
                component_id=member.id,
                kind=kind,
            )
            components.append(
                GravityComponentResultV1(
                    component_id=member.id,
                    kind=kind,
                    canonical_function=applicable.canonical_function,
                    action_ids=(component_action.action_id,),
                    result_envelope=envelope,
                    result=result_payload,
                )
            )
        except (TypeError, ValueError) as exc:
            components.append(
                _error_component(
                    component_id=member.id,
                    kind=kind,
                    function=applicable.canonical_function,
                    action_ids=(component_action.action_id,),
                    exc=exc,
                )
            )

    column_by_id = {
        item.id: item
        for item in request.building.members
        if item.kind is GravityMemberKindV1.COLUMN
    }
    for footing in request.building.footing_destinations:
        service_action = _action(actions, footing.id, "SERVICE_DL_LL")
        factored_action = _action(actions, footing.id, "ULS_1_5_DL_LL")
        applicable = applicability_by_id[footing.id]
        action_ids = (service_action.action_id, factored_action.action_id)
        if applicable.disposition is GravityPrerequisiteDispositionV1.HOLD:
            components.append(
                _hold_component(
                    component_id=footing.id,
                    kind=GravityComponentKindV1.FOOTING,
                    function=applicable.canonical_function,
                    action_ids=action_ids,
                    code=applicable.hold_reasons[0],
                    message=(
                        "Reconciled footing action is available, but the external "
                        "service/soil basis was not supplied."
                    ),
                )
            )
            continue
        footing_basis = footing_bases[footing.id]
        if (
            footing_basis.complete_service_axial_load_kn
            <= _required_dimension(
                service_action.axial_kn, "footing service axial handoff"
            )
            + request.loads.balance_tolerance_kn
            or footing_basis.complete_factored_axial_load_kn
            <= _required_dimension(
                factored_action.axial_kn, "footing factored axial handoff"
            )
            + request.loads.balance_tolerance_kn
        ):
            components.append(
                _hold_component(
                    component_id=footing.id,
                    kind=GravityComponentKindV1.FOOTING,
                    function=applicable.canonical_function,
                    action_ids=action_ids,
                    code="FOOTING_EXTERNAL_ACTION_NOT_ADDED",
                    message=(
                        "Complete footing actions must exceed the superstructure "
                        "handoff because footing self-weight/overburden are external."
                    ),
                )
            )
            continue
        column = column_by_id[footing.column_id]
        section = sections[column.section_id]
        material = materials[section.material_id]
        try:
            footing_result = design_concentric_isolated_footing_is456(
                _footing_request(
                    footing_basis,
                    column_width_mm=_required_dimension(
                        section.width_mm, "column width_mm"
                    ),
                    column_depth_mm=_required_dimension(
                        section.depth_mm, "column depth_mm"
                    ),
                    column_fck_nmm2=material.fck_nmm2,
                )
            )
            engineering = {
                "PASS": EngineeringStatus.PASS,
                "FAIL": EngineeringStatus.FAIL,
                "HOLD": EngineeringStatus.HOLD,
            }[footing_result.status]
            calculation = (
                CalculationStatus.NOT_EVALUATED
                if footing_result.calculation_status == "NOT_EVALUATED"
                else CalculationStatus.COMPLETED
            )
            intake = (
                IntakeStatus.PARTIAL
                if footing_result.status == "HOLD"
                else IntakeStatus.VALID
            )
            footing_envelope = _with_fallback_component_issue(
                _envelope(
                    intake=intake,
                    calculation=calculation,
                    engineering=engineering,
                ),
                component_id=footing.id,
                kind=GravityComponentKindV1.FOOTING,
                message=footing_result.detailing_hold_reason,
            )
            components.append(
                GravityComponentResultV1(
                    component_id=footing.id,
                    kind=GravityComponentKindV1.FOOTING,
                    canonical_function=applicable.canonical_function,
                    action_ids=action_ids,
                    result_envelope=footing_envelope,
                    result=to_transport_value(footing_result),
                )
            )
        except (TypeError, ValueError) as exc:
            components.append(
                _error_component(
                    component_id=footing.id,
                    kind=GravityComponentKindV1.FOOTING,
                    function=applicable.canonical_function,
                    action_ids=action_ids,
                    exc=exc,
                )
            )

    component_tuple = tuple(sorted(components, key=lambda item: item.component_id))
    return GravityWorkflowResultV1(
        model_hash=request.model_hash,
        load_model_hash=request.load_model_hash,
        ledger_hash=ledger.ledger_hash,
        applicability=applicability,
        practical_action_reconciliation=_practical_action_reconciliation(
            request, ledger
        ),
        actions=actions,
        components=component_tuple,
        result_envelope=_aggregate_envelope(component_tuple),
        limitations=_LIMITATIONS,
    )
