"""AO24: immutable calculation/report/drawing semantic package."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from structural_lib.beam.bar_paths import BarPathOutput
from structural_lib.beam.member import MemberDesignOutput
from structural_lib.beam.semantics import (
    ApplicabilityState,
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
    plain,
    rejected_result,
    semantic_hash,
)
from structural_lib.construction.contracts import (
    BbsOutput,
    ConstructionCostOutput,
    ConstructionQuantityOutput,
)

CREATE_CALCULATION_PACKAGE_OPERATION = "structural.calculation_package.create/v1"
CALCULATION_PACKAGE_METHOD_REVISION = "structural-calculation-package-wp07-v1"


class HumanActionKind(StrEnum):
    PREPARED = "prepared"
    CHECKED = "checked"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ResultBinding:
    operation_semantic_id: str
    result_id: str
    normalized_input_id: str
    calculation_id: str
    execution: ExecutionState
    applicability: ApplicabilityState
    engineering: EngineeringState
    completeness: CompletenessState
    freshness: FreshnessState
    output_payload_id: str


@dataclass(frozen=True)
class CalculationPackageMetadata:
    project_id: str
    project_name: str
    project_revision_id: str
    member_id: str
    package_revision_id: str
    engine_build: str
    dataset_revision_ids: tuple[str, ...]
    issued_at_utc: str


@dataclass(frozen=True)
class CalculationPackageProfile:
    profile_id: str
    revision_id: str
    template_id: str
    required_leaf_ids: tuple[str, ...]
    required_section_ids: tuple[str, ...]


@dataclass(frozen=True)
class CalculationTrace:
    trace_id: str
    leaf_id: str
    rule_reference: str
    formula_reference: str
    normalized_substitution: str
    required_value: float | None
    provided_value: float | None
    selected_value: float | None
    unit: str | None
    utilization: float | None
    governing: bool


@dataclass(frozen=True)
class DrawingDatum:
    datum_id: str
    source_identity: str
    label: str
    value: str
    unit: str | None = None


@dataclass(frozen=True)
class DrawingView:
    view_id: str
    kind: str
    detail_revision_id: str
    data: tuple[DrawingDatum, ...]


@dataclass(frozen=True)
class HumanAction:
    action_id: str
    actor_id: str
    actor_display_name: str
    professional_role: str
    action: HumanActionKind
    recorded_at_utc: str
    scope_id: str
    bound_result_id: str


@dataclass(frozen=True)
class CalculationPackageRequest:
    metadata: CalculationPackageMetadata
    package_profile: CalculationPackageProfile
    member_result: MemberDesignOutput
    member_binding: ResultBinding
    schedule: BarPathOutput
    schedule_binding: ResultBinding
    bbs: BbsOutput
    bbs_binding: ResultBinding
    quantities: ConstructionQuantityOutput
    quantity_binding: ResultBinding
    cost: ConstructionCostOutput | None
    cost_binding: ResultBinding | None
    assumptions: tuple[str, ...]
    traces: tuple[CalculationTrace, ...]
    drawings: tuple[DrawingView, ...]
    limitations: tuple[str, ...]
    human_actions: tuple[HumanAction, ...] = ()


@dataclass(frozen=True)
class PackageLeaf:
    leaf_id: str
    operation_semantic_id: str
    result_id: str | None
    required_value: float | None
    provided_value: float | None
    selected_value: float | None
    unit: str | None
    utilization: float | None
    governing: bool
    qualified: bool
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class RenderSection:
    section_id: str
    source_identities: tuple[str, ...]
    semantic_payload_kind: str


@dataclass(frozen=True)
class CalculationPackageOutput:
    calculation_package_id: str
    metadata: CalculationPackageMetadata
    package_profile_id: str
    package_profile_revision_id: str
    dependency_bindings: tuple[ResultBinding, ...]
    assumptions: tuple[str, ...]
    leaves: tuple[PackageLeaf, ...]
    traces: tuple[CalculationTrace, ...]
    governing_leaf_id: str | None
    reinforcement_schedule: BarPathOutput
    bbs: BbsOutput
    quantities: ConstructionQuantityOutput
    cost: ConstructionCostOutput | None
    drawings: tuple[DrawingView, ...]
    render_sections: tuple[RenderSection, ...]
    renderer_interface_revision: str
    limitations: tuple[str, ...]
    human_actions: tuple[HumanAction, ...]
    issue_state: str
    active_approval: bool


def _text(value: str | None) -> bool:
    return bool(value and value.strip())


def _provenance() -> Provenance:
    return Provenance(
        "calculation-package-wp07-v1",
        CALCULATION_PACKAGE_METHOD_REVISION,
        (
            "PF5 AO24 calculation-package contract",
            "PF7 AR24 reproducible leaf, identity, drawing, and human-action evidence",
        ),
    )


def _error(code: str, message: str, field: str, remediation: str) -> Diagnostic:
    return Diagnostic(
        code,
        "error",
        message,
        CREATE_CALCULATION_PACKAGE_OPERATION,
        field,
        "calculation-package",
        remediation,
    )


def _reject(
    inputs: dict[str, dict[str, object]],
    code: str,
    message: str,
    field: str,
    remediation: str,
) -> OperationResult:
    return rejected_result(
        CREATE_CALCULATION_PACKAGE_OPERATION,
        inputs,
        (_error(code, message, field, remediation),),
        provenance=_provenance(),
    )


def _timestamp(value: str) -> bool:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _binding_valid(binding: ResultBinding) -> bool:
    return (
        all(
            _text(value)
            for value in (
                binding.operation_semantic_id,
                binding.result_id,
                binding.normalized_input_id,
                binding.calculation_id,
                binding.output_payload_id,
            )
        )
        and isinstance(binding.execution, ExecutionState)
        and isinstance(binding.applicability, ApplicabilityState)
        and isinstance(binding.engineering, EngineeringState)
        and isinstance(binding.completeness, CompletenessState)
        and isinstance(binding.freshness, FreshnessState)
    )


def result_binding(
    result: OperationResult,
    output_key: str,
) -> ResultBinding:
    """Bind an immutable operation result to its selected typed output payload."""

    if output_key not in result.outputs:
        raise ValueError(f"Operation result has no {output_key!r} output")
    return ResultBinding(
        result.operation_semantic_id,
        result.result_id,
        result.normalized_input_id,
        result.calculation_id,
        result.execution,
        result.applicability,
        result.engineering,
        result.completeness,
        result.freshness,
        semantic_hash("output_payload_id", result.outputs[output_key]),
    )


def _binding_current(binding: ResultBinding) -> bool:
    return (
        binding.execution is ExecutionState.COMPLETED
        and binding.applicability is ApplicabilityState.APPLICABLE
        and binding.engineering is EngineeringState.PASS
        and binding.completeness is CompletenessState.COMPLETE_FOR_SCOPE
        and binding.freshness is FreshnessState.CURRENT
    )


def create_calculation_package(request: CalculationPackageRequest) -> OperationResult:
    """Create adapter-ready semantic data; file rendering remains a host concern."""

    inputs = effective_inputs(request=request)
    metadata = request.metadata
    profile = request.package_profile
    if (
        not all(
            _text(value)
            for value in (
                metadata.project_id,
                metadata.project_name,
                metadata.project_revision_id,
                metadata.member_id,
                metadata.package_revision_id,
                metadata.engine_build,
                metadata.issued_at_utc,
                profile.profile_id,
                profile.revision_id,
                profile.template_id,
            )
        )
        or not metadata.dataset_revision_ids
        or not all(_text(value) for value in metadata.dataset_revision_ids)
        or not _timestamp(metadata.issued_at_utc)
    ):
        return _reject(
            inputs,
            "PACKAGE.METADATA",
            "Complete project/member/revision/engine/dataset metadata and a timezone-aware issue time are required.",
            "metadata",
            "Supply the reproducible package metadata.",
        )
    if (
        not profile.required_leaf_ids
        or not profile.required_section_ids
        or len(profile.required_leaf_ids) != len(set(profile.required_leaf_ids))
        or len(profile.required_section_ids) != len(set(profile.required_section_ids))
        or not all(
            _text(value)
            for value in (*profile.required_leaf_ids, *profile.required_section_ids)
        )
    ):
        return _reject(
            inputs,
            "PACKAGE.PROFILE",
            "The package profile requires unique leaf and semantic section identities.",
            "package_profile",
            "Correct the versioned package profile.",
        )

    bindings = [
        request.member_binding,
        request.schedule_binding,
        request.bbs_binding,
        request.quantity_binding,
    ]
    if request.cost is None:
        if request.cost_binding is not None:
            return _reject(
                inputs,
                "PACKAGE.COST_BINDING",
                "A cost binding cannot be supplied without a cost result.",
                "cost_binding",
                "Remove the binding or supply its exact cost result.",
            )
    elif request.cost_binding is None:
        return _reject(
            inputs,
            "PACKAGE.COST_BINDING",
            "A supplied cost result requires its exact semantic binding.",
            "cost_binding",
            "Supply the current AO20 result binding.",
        )
    else:
        bindings.append(request.cost_binding)
    expected_operations = [
        "is456.beam_member.design/v1",
        "structural.reinforcement_paths.resolve/v1",
        "structural.bbs.create/v1",
        "structural.construction_quantities.calculate/v1",
    ] + (
        ["structural.construction_cost.estimate/v1"] if request.cost is not None else []
    )
    if (
        any(not _binding_valid(binding) for binding in bindings)
        or [item.operation_semantic_id for item in bindings] != expected_operations
    ):
        return _reject(
            inputs,
            "PACKAGE.BINDING",
            "Every dependency requires its exact valid operation and semantic result binding.",
            "dependency_bindings",
            "Bind the current AO17, AO18, AO19, AO04, and optional AO20 results in order.",
        )
    payloads: list[object] = [
        request.member_result,
        request.schedule,
        request.bbs,
        request.quantities,
    ] + ([request.cost] if request.cost is not None else [])
    if any(
        binding.output_payload_id != semantic_hash("output_payload_id", plain(payload))
        for binding, payload in zip(bindings, payloads, strict=True)
    ):
        return _reject(
            inputs,
            "PACKAGE.PAYLOAD_BINDING",
            "A dependency binding does not identify the supplied semantic output payload.",
            "dependency_bindings",
            "Create bindings directly from the unchanged operation results.",
        )

    member = request.member_result
    schedule = request.schedule
    bbs = request.bbs
    quantities = request.quantities
    if (
        metadata.member_id != member.member_id
        or schedule.member_id != member.member_id
        or bbs.member_id != member.member_id
        or quantities.member_id != member.member_id
        or schedule.project_basis_id != member.project_basis_id
        or bbs.project_basis_id != member.project_basis_id
        or quantities.project_basis_id != member.project_basis_id
        or bbs.detail_revision_id != schedule.detail_revision_id
        or quantities.detail_revision_id != schedule.detail_revision_id
        or bbs.schedule_result_id != request.schedule_binding.result_id
        or quantities.bbs_result_id != request.bbs_binding.result_id
        or request.cost is not None
        and (
            request.cost.member_id != member.member_id
            or request.cost.project_basis_id != member.project_basis_id
            or request.cost.detail_revision_id != schedule.detail_revision_id
            or request.cost.quantity_result_id != request.quantity_binding.result_id
        )
    ):
        return _reject(
            inputs,
            "PACKAGE.IDENTITY_CONFLICT",
            "Package dependencies must describe one project, member, detail, and result chain.",
            "request",
            "Rebuild dependent results from one current design chain.",
        )

    expected_leaf_ids = tuple(item.leaf_id for item in member.expected_leaves)
    if set(profile.required_leaf_ids) != set(expected_leaf_ids):
        return _reject(
            inputs,
            "PACKAGE.LEAF_PROFILE",
            "The package profile must retain the complete profile-derived member leaf set.",
            "package_profile.required_leaf_ids",
            "Use the AO17 expected leaf identities exactly.",
        )
    qualifications = {
        item.expectation.leaf_id: item for item in member.leaf_qualifications
    }
    if set(qualifications) != set(expected_leaf_ids):
        return _reject(
            inputs,
            "PACKAGE.LEAF_SET",
            "Member leaf qualifications do not match the expected leaf set.",
            "member_result.leaf_qualifications",
            "Regenerate the whole-member result.",
        )

    traces = {item.leaf_id: item for item in request.traces}
    trace_ids = [item.trace_id for item in request.traces]
    if (
        len(trace_ids) != len(set(trace_ids))
        or len(request.traces) != len(expected_leaf_ids)
        or set(traces) != set(expected_leaf_ids)
        or any(
            not all(
                _text(value)
                for value in (
                    item.trace_id,
                    item.leaf_id,
                    item.rule_reference,
                    item.formula_reference,
                    item.normalized_substitution,
                )
            )
            for item in request.traces
        )
    ):
        return _reject(
            inputs,
            "PACKAGE.TRACE",
            "Every required member leaf needs one unique rule/formula/substitution trace.",
            "traces",
            "Supply one semantic calculation trace per AO17 leaf.",
        )
    if (
        not request.assumptions
        or not all(_text(value) for value in request.assumptions)
        or not all(_text(value) for value in request.limitations)
    ):
        return _reject(
            inputs,
            "PACKAGE.NARRATIVE",
            "At least one explicit assumption and only nonblank limitations are required.",
            "assumptions,limitations",
            "Record the calculation basis and applicable limitations.",
        )

    drawing_ids = [item.view_id for item in request.drawings]
    datum_ids = [datum.datum_id for view in request.drawings for datum in view.data]
    if (
        not request.drawings
        or len(drawing_ids) != len(set(drawing_ids))
        or len(datum_ids) != len(set(datum_ids))
        or any(
            not all(
                _text(value)
                for value in (view.view_id, view.kind, view.detail_revision_id)
            )
            or view.detail_revision_id != schedule.detail_revision_id
            or not view.data
            or any(
                not all(
                    _text(value)
                    for value in (
                        datum.datum_id,
                        datum.source_identity,
                        datum.label,
                        datum.value,
                    )
                )
                for datum in view.data
            )
            for view in request.drawings
        )
    ):
        return _reject(
            inputs,
            "PACKAGE.DRAWING",
            "Drawing views require unique identities, current detail revision, and sourced semantic data.",
            "drawings",
            "Supply current elevation, section, or schedule view data.",
        )

    dependency_ids = {item.result_id for item in bindings}
    action_ids = [item.action_id for item in request.human_actions]
    if len(action_ids) != len(set(action_ids)) or any(
        not all(
            _text(value)
            for value in (
                item.action_id,
                item.actor_id,
                item.actor_display_name,
                item.professional_role,
                item.recorded_at_utc,
                item.scope_id,
                item.bound_result_id,
            )
        )
        or not isinstance(item.action, HumanActionKind)
        or not _timestamp(item.recorded_at_utc)
        or item.bound_result_id not in dependency_ids
        for item in request.human_actions
    ):
        return _reject(
            inputs,
            "PACKAGE.HUMAN_ACTION",
            "Prepared, checked, approved, or rejected fields require a real actor, time, scope, and exact dependency identity.",
            "human_actions",
            "Record only actual identity-bound human actions.",
        )

    package_leaves: list[PackageLeaf] = []
    for leaf_id in profile.required_leaf_ids:
        qualification = qualifications[leaf_id]
        evidence = qualification.evidence
        package_leaves.append(
            PackageLeaf(
                leaf_id,
                qualification.expectation.operation_semantic_id,
                evidence.result_id if evidence is not None else None,
                evidence.required_value if evidence is not None else None,
                evidence.supplied_value if evidence is not None else None,
                evidence.selected_value if evidence is not None else None,
                evidence.unit if evidence is not None else None,
                evidence.governing_utilization if evidence is not None else None,
                member.governing_leaf_id == leaf_id,
                qualification.qualified,
                qualification.reason_codes,
            )
        )
    leaves = tuple(package_leaves)
    for leaf in leaves:
        trace = traces[leaf.leaf_id]
        if (
            trace.required_value != leaf.required_value
            or trace.provided_value != leaf.provided_value
            or trace.selected_value != leaf.selected_value
            or trace.unit != leaf.unit
            or trace.utilization != leaf.utilization
            or trace.governing != leaf.governing
        ):
            return _reject(
                inputs,
                "PACKAGE.TRACE_VALUE",
                "Calculation traces must reproduce the exact required, provided, selected, unit, utilization, and governing leaf evidence.",
                f"traces[{leaf.leaf_id}]",
                "Build trace substitutions from the unchanged qualified leaf result.",
            )
    current = (
        member.qualified
        and all(_binding_current(item) for item in bindings)
        and all(item.qualified for item in leaves)
    )
    member_actions = sorted(
        (
            item
            for item in request.human_actions
            if item.scope_id == metadata.member_id
            and item.bound_result_id == request.member_binding.result_id
        ),
        key=lambda item: (
            datetime.fromisoformat(
                item.recorded_at_utc.replace("Z", "+00:00")
            ).astimezone(UTC),
            item.action_id,
        ),
    )
    active_approval = (
        current
        and bool(member_actions)
        and member_actions[-1].action is HumanActionKind.APPROVED
    )
    sections = tuple(
        RenderSection(
            section_id,
            tuple(item.result_id for item in bindings),
            {
                "inputs": "effective_inputs_and_assumptions",
                "calculations": "leaf_traces",
                "reinforcement": "resolved_paths_and_bbs",
                "quantities": "construction_quantities",
                "cost": "dated_direct_cost",
                "drawings": "drawing_views",
                "signatures": "recorded_human_actions",
            }.get(section_id, "declared_semantic_section"),
        )
        for section_id in profile.required_section_ids
    )
    payload = {
        "metadata": metadata,
        "profile": profile,
        "bindings": tuple(bindings),
        "assumptions": request.assumptions,
        "leaves": leaves,
        "traces": request.traces,
        "schedule": schedule,
        "bbs": bbs,
        "quantities": quantities,
        "cost": request.cost,
        "drawings": request.drawings,
        "limitations": request.limitations,
        "human_actions": request.human_actions,
    }
    output = CalculationPackageOutput(
        semantic_hash("calculation_package_id", payload),
        metadata,
        profile.profile_id,
        profile.revision_id,
        tuple(bindings),
        request.assumptions,
        leaves,
        request.traces,
        member.governing_leaf_id,
        schedule,
        bbs,
        quantities,
        request.cost,
        request.drawings,
        sections,
        "structural-calculation-renderer/v1",
        request.limitations,
        request.human_actions,
        "issue_ready" if current else "draft",
        active_approval,
    )
    if current:
        return completed_result(
            CREATE_CALCULATION_PACKAGE_OPERATION,
            inputs,
            {"calculation_package": output},
            provenance=_provenance(),
        )
    diagnostics = (
        _error(
            "PACKAGE.EVIDENCE_INCOMPLETE",
            "The semantic package is a draft because required engineering evidence is incomplete or stale.",
            "dependency_bindings,leaves",
            "Refresh every required result and qualified member leaf before issue.",
        ),
    )
    freshness = (
        FreshnessState.STALE
        if any(item.freshness is FreshnessState.STALE for item in bindings)
        else FreshnessState.CURRENT
    )
    return partial_result(
        CREATE_CALCULATION_PACKAGE_OPERATION,
        inputs,
        {"calculation_package": output},
        diagnostics,
        provenance=_provenance(),
        freshness=freshness,
    )
