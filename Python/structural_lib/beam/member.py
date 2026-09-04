"""Whole-member aggregation over versioned WP01-WP05 leaf results."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .project import BeamProject, BeamProjectRequest, CheckScope, create_beam_project
from .semantics import (
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
    rejected_result,
)

DESIGN_MEMBER_OPERATION = "is456.beam_member.design/v1"
MEMBER_METHOD_REVISION = "is456-beam-member-aggregation-wp06-v1"


@dataclass(frozen=True)
class MemberScopeInstance:
    scope_id: str
    scope: CheckScope
    source_revision_id: str


@dataclass(frozen=True)
class EffectiveDepthIteration:
    iteration_number: int
    reinforcement_revision_id: str
    effective_depth_mm: float
    dependent_result_ids: tuple[str, ...]
    converged: bool


@dataclass(frozen=True)
class MemberLeafExpectation:
    leaf_id: str
    rule_id: str
    operation_semantic_id: str
    scope_id: str
    scope: CheckScope
    expected_applicability: ApplicabilityState
    code_data_revision_id: str | None


@dataclass(frozen=True)
class MemberLeafEvidence:
    leaf_id: str
    operation_semantic_id: str
    result_id: str
    execution: ExecutionState
    applicability: ApplicabilityState
    engineering: EngineeringState
    completeness: CompletenessState
    freshness: FreshnessState
    code_data_revision_id: str
    method_revision_id: str
    normalized_input_id: str
    calculation_id: str
    required_value: float | None = None
    selected_value: float | None = None
    supplied_value: float | None = None
    unit: str | None = None
    governing_utilization: float | None = None
    diagnostic_codes: tuple[str, ...] = ()


@dataclass(frozen=True)
class MemberLeafQualification:
    expectation: MemberLeafExpectation
    evidence: MemberLeafEvidence | None
    qualified: bool
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class MemberDesignRequest:
    project: BeamProject
    member_id: str
    topology_revision_id: str
    action_revision_id: str
    reinforcement_revision_id: str
    design_scope_revision_id: str
    scope_instances: tuple[MemberScopeInstance, ...]
    depth_iterations: tuple[EffectiveDepthIteration, ...]
    leaf_results: tuple[MemberLeafEvidence, ...]


@dataclass(frozen=True)
class MemberDesignOutput:
    project_basis_id: str
    profile_revision_id: str
    member_id: str
    topology_revision_id: str
    action_revision_id: str
    reinforcement_revision_id: str
    design_scope_revision_id: str
    expected_leaves: tuple[MemberLeafExpectation, ...]
    leaf_qualifications: tuple[MemberLeafQualification, ...]
    depth_iterations: tuple[EffectiveDepthIteration, ...]
    governing_leaf_id: str | None
    governing_result_id: str | None
    governing_utilization: float | None
    qualified: bool


def _text(value: str | None) -> bool:
    return bool(value and value.strip())


def _diagnostic(code: str, message: str, field: str, remediation: str) -> Diagnostic:
    return Diagnostic(
        code,
        "error",
        message,
        DESIGN_MEMBER_OPERATION,
        field,
        "beam-member",
        remediation,
    )


def _provenance(project: BeamProject) -> Provenance:
    revisions = ",".join(binding.revision_id for binding in project.code_data_revisions)
    return Provenance(
        revisions or "project-bound-code-data",
        MEMBER_METHOD_REVISION,
        (
            "PF5 AO17 complete-member aggregation contract",
            "WP01-WP05 qualified leaf result identities",
        ),
    )


def _expected_leaves(
    project: BeamProject,
    member_id: str,
    scope_instances: tuple[MemberScopeInstance, ...],
) -> tuple[MemberLeafExpectation, ...]:
    scopes: dict[CheckScope, list[str]] = {CheckScope.MEMBER: [member_id]}
    for item in scope_instances:
        scopes.setdefault(item.scope, []).append(item.scope_id)
    code_revisions = {
        binding.binding_id: binding.revision_id
        for binding in project.code_data_revisions
    }
    leaves: list[MemberLeafExpectation] = []
    for rule in project.profile.check_rules:
        for scope_id in sorted(scopes.get(rule.scope, [])):
            leaves.append(
                MemberLeafExpectation(
                    f"{rule.rule_id}@{scope_id}",
                    rule.rule_id,
                    rule.operation_semantic_id,
                    scope_id,
                    rule.scope,
                    rule.expected_applicability,
                    (
                        code_revisions[rule.code_data_binding_id]
                        if rule.code_data_binding_id is not None
                        else None
                    ),
                )
            )
    return tuple(leaves)


def _validate_depth_iterations(
    iterations: tuple[EffectiveDepthIteration, ...],
) -> bool:
    return all(
        item.iteration_number == index
        and _text(item.reinforcement_revision_id)
        and math.isfinite(item.effective_depth_mm)
        and item.effective_depth_mm > 0
        and item.dependent_result_ids
        and all(_text(result_id) for result_id in item.dependent_result_ids)
        and len(item.dependent_result_ids) == len(set(item.dependent_result_ids))
        for index, item in enumerate(iterations, start=1)
    )


def _validate_leaf_evidence(evidence: MemberLeafEvidence) -> bool:
    values = (
        evidence.required_value,
        evidence.selected_value,
        evidence.supplied_value,
        evidence.governing_utilization,
    )
    numerics_valid = all(value is None or math.isfinite(value) for value in values)
    utilization_valid = (
        evidence.governing_utilization is None or evidence.governing_utilization >= 0
    )
    has_numeric = any(value is not None for value in values[:3])
    return (
        isinstance(evidence.execution, ExecutionState)
        and isinstance(evidence.applicability, ApplicabilityState)
        and isinstance(evidence.engineering, EngineeringState)
        and isinstance(evidence.completeness, CompletenessState)
        and isinstance(evidence.freshness, FreshnessState)
        and _text(evidence.leaf_id)
        and _text(evidence.operation_semantic_id)
        and _text(evidence.result_id)
        and _text(evidence.code_data_revision_id)
        and _text(evidence.method_revision_id)
        and _text(evidence.normalized_input_id)
        and (
            evidence.execution is not ExecutionState.COMPLETED
            or _text(evidence.calculation_id)
        )
        and numerics_valid
        and utilization_valid
        and (not has_numeric or _text(evidence.unit))
        and all(_text(code) for code in evidence.diagnostic_codes)
    )


def _qualify_leaf(
    expectation: MemberLeafExpectation,
    evidence: MemberLeafEvidence | None,
) -> MemberLeafQualification:
    if evidence is None:
        return MemberLeafQualification(
            expectation,
            None,
            False,
            ("LEAF.MISSING",),
        )
    reasons: list[str] = []
    if evidence.operation_semantic_id != expectation.operation_semantic_id:
        reasons.append("LEAF.OPERATION_MISMATCH")
    if (
        expectation.code_data_revision_id is not None
        and evidence.code_data_revision_id != expectation.code_data_revision_id
    ):
        reasons.append("LEAF.CODE_DATA_MISMATCH")
    if evidence.execution is not ExecutionState.COMPLETED:
        reasons.append("LEAF.EXECUTION_INCOMPLETE")
    if evidence.completeness is not CompletenessState.COMPLETE_FOR_SCOPE:
        reasons.append("LEAF.PARTIAL")
    if evidence.freshness is not FreshnessState.CURRENT:
        reasons.append(f"LEAF.{evidence.freshness.value.upper()}")
    if evidence.applicability is not expectation.expected_applicability:
        reasons.append("LEAF.APPLICABILITY_MISMATCH")
    elif expectation.expected_applicability is ApplicabilityState.APPLICABLE:
        if evidence.engineering is EngineeringState.FAIL:
            reasons.append("LEAF.FAIL")
        elif evidence.engineering is not EngineeringState.PASS:
            reasons.append("LEAF.NOT_EVALUATED")
    elif evidence.engineering is not EngineeringState.NOT_EVALUATED:
        reasons.append("LEAF.NOT_APPLICABLE_STATE_INVALID")
    return MemberLeafQualification(
        expectation,
        evidence,
        not reasons,
        tuple(reasons),
    )


def design_member(request: MemberDesignRequest) -> OperationResult:
    """Aggregate the project-derived complete member leaf set without rerunning formulas."""

    inputs = effective_inputs(request=request)
    provenance = _provenance(request.project)
    project_request = BeamProjectRequest(
        request.project.project,
        request.project.unit_basis,
        request.project.code_data_revisions,
        request.project.profile,
        request.project.catalogue_revisions,
    )
    project_validation = create_beam_project(project_request)
    if (
        project_validation.execution is not ExecutionState.COMPLETED
        or project_validation.outputs["project"]["project_basis_id"]
        != request.project.project_basis_id
    ):
        return rejected_result(
            DESIGN_MEMBER_OPERATION,
            inputs,
            (
                _diagnostic(
                    "PROJECT.BASIS_INVALID",
                    "The member project is not the validated immutable project basis represented by its identity.",
                    "project",
                    "Use the exact current output of structural.beam_project.create/v1.",
                ),
            ),
            provenance=provenance,
        )
    if not all(
        _text(value)
        for value in (
            request.project.project_basis_id,
            request.member_id,
            request.topology_revision_id,
            request.action_revision_id,
            request.reinforcement_revision_id,
            request.design_scope_revision_id,
        )
    ):
        return rejected_result(
            DESIGN_MEMBER_OPERATION,
            inputs,
            (
                _diagnostic(
                    "MEMBER.IDENTITY",
                    "The project, member, topology, action, reinforcement, and scope revisions are required.",
                    "request",
                    "Bind the calculation to immutable current revisions.",
                ),
            ),
            provenance=provenance,
        )

    scope_keys = [(item.scope, item.scope_id) for item in request.scope_instances]
    required_scopes = {
        rule.scope
        for rule in request.project.profile.check_rules
        if rule.scope is not CheckScope.MEMBER
    }
    if (
        any(
            not isinstance(item.scope, CheckScope)
            or item.scope is CheckScope.MEMBER
            or not _text(item.scope_id)
            or "@" in item.scope_id
            or not _text(item.source_revision_id)
            or item.source_revision_id != request.design_scope_revision_id
            for item in request.scope_instances
        )
        or "@" in request.member_id
        or len(scope_keys) != len(set(scope_keys))
        or any(
            not any(item.scope is scope for item in request.scope_instances)
            for scope in required_scopes
        )
    ):
        return rejected_result(
            DESIGN_MEMBER_OPERATION,
            inputs,
            (
                _diagnostic(
                    "SCOPE.INVALID",
                    "Every non-member rule requires at least one uniquely identified scope instance from a named revision.",
                    "scope_instances",
                    "Supply the frozen topology-derived span, station, face, axis, bar-end, and arrangement scopes.",
                ),
            ),
            provenance=provenance,
        )

    expected = _expected_leaves(
        request.project,
        request.member_id,
        request.scope_instances,
    )
    if not expected:
        return rejected_result(
            DESIGN_MEMBER_OPERATION,
            inputs,
            (
                _diagnostic(
                    "LEAF.PROFILE_EMPTY",
                    "The project profile and supplied scope produce no expected member leaves.",
                    "project.profile.check_rules,scope_instances",
                    "Correct the project required-check profile or design scope.",
                ),
            ),
            provenance=provenance,
        )

    evidence_ids = [item.leaf_id for item in request.leaf_results]
    expected_ids = {item.leaf_id for item in expected}
    if (
        len(evidence_ids) != len(set(evidence_ids))
        or any(not _validate_leaf_evidence(item) for item in request.leaf_results)
        or any(leaf_id not in expected_ids for leaf_id in evidence_ids)
    ):
        return rejected_result(
            DESIGN_MEMBER_OPERATION,
            inputs,
            (
                _diagnostic(
                    "LEAF.EVIDENCE_INVALID",
                    "Leaf evidence must be valid, uniquely identified, and present in the profile-derived expected set.",
                    "leaf_results",
                    "Remove unexpected leaves and correct their identities, states, revisions, and numerical summaries.",
                ),
            ),
            provenance=provenance,
        )
    if request.depth_iterations and not _validate_depth_iterations(
        request.depth_iterations
    ):
        return rejected_result(
            DESIGN_MEMBER_OPERATION,
            inputs,
            (
                _diagnostic(
                    "DEPTH.ITERATION_INVALID",
                    "Effective-depth iterations must be sequential and bind positive depths to unique dependent results.",
                    "depth_iterations",
                    "Correct the actual-depth iteration history.",
                ),
            ),
            provenance=provenance,
        )

    evidence_by_id = {item.leaf_id: item for item in request.leaf_results}
    qualifications = tuple(
        _qualify_leaf(expectation, evidence_by_id.get(expectation.leaf_id))
        for expectation in expected
    )
    diagnostics: list[Diagnostic] = []
    for qualification in qualifications:
        for reason in qualification.reason_codes:
            diagnostics.append(
                _diagnostic(
                    reason,
                    f"Expected member leaf {qualification.expectation.leaf_id} is not qualified: {reason}.",
                    f"leaf_results[{qualification.expectation.leaf_id}]",
                    "Recalculate the exact expected leaf against current complete inputs.",
                )
            )

    current_depth_result_ids = {
        item.evidence.result_id
        for item in qualifications
        if item.evidence is not None
        and item.expectation.expected_applicability is ApplicabilityState.APPLICABLE
    }
    final_iteration = request.depth_iterations[-1] if request.depth_iterations else None
    depth_result_binding_complete = (
        final_iteration is not None
        and set(final_iteration.dependent_result_ids) == current_depth_result_ids
    )
    depth_complete = final_iteration is not None and (
        final_iteration.converged
        and final_iteration.reinforcement_revision_id
        == request.reinforcement_revision_id
        and depth_result_binding_complete
    )
    if not depth_complete:
        diagnostic_code = (
            "DEPTH.RESULT_BINDING"
            if final_iteration is not None
            and final_iteration.converged
            and final_iteration.reinforcement_revision_id
            == request.reinforcement_revision_id
            and not depth_result_binding_complete
            else "DEPTH.NOT_CONVERGED"
        )
        diagnostics.append(
            _diagnostic(
                diagnostic_code,
                "The final effective depth must be converged against the current reinforcement revision and every applicable leaf result.",
                "depth_iterations",
                "Iterate the physical bar arrangement and bind every applicable current leaf result to the final depth.",
            )
        )

    qualified_evidence = [
        item.evidence
        for item in qualifications
        if item.evidence is not None
        and item.evidence.governing_utilization is not None
        and set(item.reason_codes).issubset({"LEAF.FAIL"})
    ]
    governing = max(
        qualified_evidence,
        key=lambda item: item.governing_utilization or 0,
        default=None,
    )
    governing_leaf_id = governing.leaf_id if governing is not None else None
    output = MemberDesignOutput(
        request.project.project_basis_id,
        request.project.profile.revision_id,
        request.member_id,
        request.topology_revision_id,
        request.action_revision_id,
        request.reinforcement_revision_id,
        request.design_scope_revision_id,
        expected,
        qualifications,
        request.depth_iterations,
        governing_leaf_id,
        governing.result_id if governing is not None else None,
        governing.governing_utilization if governing is not None else None,
        all(item.qualified for item in qualifications) and depth_complete,
    )

    partial_reasons = {
        reason
        for item in qualifications
        for reason in item.reason_codes
        if reason != "LEAF.FAIL"
    }
    if partial_reasons or not depth_complete:
        leaf_freshness = {item.freshness for item in request.leaf_results}
        freshness = (
            FreshnessState.STALE
            if FreshnessState.STALE in leaf_freshness
            else (
                FreshnessState.UNBOUND
                if FreshnessState.UNBOUND in leaf_freshness
                else FreshnessState.CURRENT
            )
        )
        return partial_result(
            DESIGN_MEMBER_OPERATION,
            inputs,
            {"member_design": output},
            diagnostics,
            provenance=provenance,
            freshness=freshness,
        )

    engineering = (
        EngineeringState.FAIL
        if any("LEAF.FAIL" in item.reason_codes for item in qualifications)
        else EngineeringState.PASS
    )
    return completed_result(
        DESIGN_MEMBER_OPERATION,
        inputs,
        {"member_design": output},
        engineering=engineering,
        diagnostics=diagnostics,
        provenance=provenance,
    )


__all__ = [
    "EffectiveDepthIteration",
    "MemberDesignOutput",
    "MemberDesignRequest",
    "MemberLeafEvidence",
    "MemberLeafExpectation",
    "MemberLeafQualification",
    "MemberScopeInstance",
    "design_member",
]
