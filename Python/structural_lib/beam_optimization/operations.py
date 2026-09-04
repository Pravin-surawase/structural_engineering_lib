"""WP08 deterministic beam candidate generation, evidence gating, and ranking."""

from __future__ import annotations

import math
import re
from decimal import Decimal, InvalidOperation

from structural_lib.beam.member import MemberLeafExpectation
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

from .contracts import (
    AnalysisMode,
    BeamCandidateDefinition,
    BeamOptimizationOutput,
    BeamOptimizationRequest,
    CandidateChangeCategory,
    CandidateCouplingClass,
    CandidateDisposition,
    CandidateDomainOutput,
    CandidateEvaluation,
    CandidateEvaluationRecord,
    CandidateExclusion,
    CandidateObjectiveKind,
    CandidateObjectiveProfile,
    CandidatePhysicalDefinition,
    CandidateRankingContext,
    CandidateRankingOutput,
    CandidateRankingRequest,
    CandidateReanalysisEvidence,
    CandidateResultBinding,
    CandidateTieBreaker,
    DiscreteCandidateDomain,
    ObjectiveMetric,
    RankedCandidate,
    SearchPerformance,
    SearchStopReason,
    SearchTerminalState,
)

RANK_CANDIDATES_OPERATION = "structural.candidate.rank/v1"
OPTIMIZE_BEAM_OPERATION = "structural.beam.optimize/v1"
MEMBER_DESIGN_OPERATION = "is456.beam_member.design/v1"
QUANTITY_OPERATION = "structural.construction_quantities.calculate/v1"
COST_OPERATION = "structural.construction_cost.estimate/v1"
METHOD_REVISION = "structural-beam-optimization-wp08-v1"
TRAVERSAL_ORDER = "candidate_id_ordinal_ascending"
MAXIMUM_DOMAIN_CANDIDATES = 100_000
_NONNEGATIVE_DECIMAL = re.compile(r"^(0|[0-9]+)(\.[0-9]+)?$")

_FIXED_ACTION_CHANGES = {
    CandidateChangeCategory.ACTUAL_BARS,
    CandidateChangeCategory.DETAILING,
    CandidateChangeCategory.BAR_PATHS,
    CandidateChangeCategory.BBS,
    CandidateChangeCategory.RATES_COST,
    CandidateChangeCategory.REPORT_OPTIONS,
}
_REANALYSIS_CHANGES = {
    CandidateChangeCategory.SECTION_DIMENSIONS_PROPERTY,
    CandidateChangeCategory.MATERIAL_STIFFNESS,
    CandidateChangeCategory.RELEASES,
    CandidateChangeCategory.OFFSETS,
    CandidateChangeCategory.MASS_SELF_WEIGHT,
    CandidateChangeCategory.APPLIED_LOAD,
    CandidateChangeCategory.LOAD_CASE_COMBINATION,
    CandidateChangeCategory.SUPPORT_RESTRAINT,
    CandidateChangeCategory.MESHING,
    CandidateChangeCategory.ANALYSIS_SETTINGS,
}


def candidate_result_binding(
    result: OperationResult, output_payload: object
) -> CandidateResultBinding:
    """Create the portable WP08 evidence binding for one typed output payload."""

    return CandidateResultBinding(
        result.operation_semantic_id,
        result.result_id,
        result.normalized_input_id,
        result.calculation_id,
        result.execution,
        result.applicability,
        result.engineering,
        result.completeness,
        result.freshness,
        semantic_hash("output_payload_id", output_payload),
    )


def _text(value: str | None) -> bool:
    return bool(value and value.strip())


def _positive(value: float) -> bool:
    return math.isfinite(value) and value > 0


def _nonnegative(value: float) -> bool:
    return math.isfinite(value) and value >= 0


def _provenance(source_references: tuple[str, ...] = ()) -> Provenance:
    return Provenance(
        "optimization-policy-wp08-v1",
        METHOD_REVISION,
        source_references
        or (
            "docs/planning/xll-product/library-definition/pf7/baseline.json",
            "docs/planning/xll-product/library-definition/pf8/baseline.json",
            "docs/planning/xll-product/library-definition/pf11/baseline.json",
        ),
    )


def _diagnostic(
    operation: str,
    code: str,
    message: str,
    field: str,
    remediation: str,
) -> Diagnostic:
    return Diagnostic(
        code,
        "error",
        message,
        operation,
        field,
        "optimization",
        remediation,
    )


def _validate_domain(domain: DiscreteCandidateDomain) -> None:
    identities = (
        domain.domain_id,
        domain.revision_id,
        domain.project_basis_id,
        domain.profile_revision_id,
        domain.member_id,
        domain.topology_revision_id,
        domain.action_revision_id,
        domain.design_scope_revision_id,
        domain.baseline_analysis_revision_id,
        domain.baseline_section_choice_id,
    )
    if not all(_text(item) for item in identities):
        raise ValueError("DOMAIN.IDENTITY")
    if (
        not domain.section_choices
        or not domain.longitudinal_choices
        or not domain.transverse_choices
    ):
        raise ValueError("DOMAIN.EMPTY_AXIS")
    axes = (
        domain.section_choices,
        domain.longitudinal_choices,
        domain.transverse_choices,
    )
    if any(
        len({item.choice_id for item in axis}) != len(axis)
        or any(not _text(item.choice_id) for item in axis)
        for axis in axes
    ):
        raise ValueError("DOMAIN.CHOICE_ID")
    if domain.baseline_section_choice_id not in {
        item.choice_id for item in domain.section_choices
    }:
        raise ValueError("DOMAIN.BASELINE_SECTION")
    if any(
        not all(
            _positive(value)
            for value in (
                item.width_mm,
                item.overall_depth_mm,
                item.concrete_strength_n_per_mm2,
            )
        )
        or len(set(item.additional_change_categories))
        != len(item.additional_change_categories)
        for item in domain.section_choices
    ):
        raise ValueError("DOMAIN.SECTION_CHOICE")
    if any(
        item.top_bar_count <= 0
        or item.bottom_bar_count <= 0
        or item.top_layer_count <= 0
        or item.bottom_layer_count <= 0
        or not all(
            _positive(value)
            for value in (
                item.top_bar_diameter_mm,
                item.bottom_bar_diameter_mm,
                item.steel_grade_n_per_mm2,
            )
        )
        for item in domain.longitudinal_choices
    ):
        raise ValueError("DOMAIN.LONGITUDINAL_CHOICE")
    if any(
        item.legs <= 0
        or not all(
            _positive(value)
            for value in (
                item.link_diameter_mm,
                item.steel_grade_n_per_mm2,
                item.spacing_mm,
            )
        )
        for item in domain.transverse_choices
    ):
        raise ValueError("DOMAIN.TRANSVERSE_CHOICE")
    count = (
        len(domain.section_choices)
        * len(domain.longitudinal_choices)
        * len(domain.transverse_choices)
    )
    if (
        domain.maximum_domain_candidates <= 0
        or domain.maximum_domain_candidates > MAXIMUM_DOMAIN_CANDIDATES
        or count > domain.maximum_domain_candidates
    ):
        raise ValueError("DOMAIN.BOUND_EXCEEDED")
    if (
        not domain.source_references
        or any(not _text(item) for item in domain.source_references)
        or len(set(domain.source_references)) != len(domain.source_references)
        or not domain.limitations
        or any(not _text(item) for item in domain.limitations)
    ):
        raise ValueError("DOMAIN.PROVENANCE")


def _coupling_class(
    changes: tuple[CandidateChangeCategory, ...],
) -> CandidateCouplingClass:
    values = set(changes)
    if CandidateChangeCategory.UNKNOWN in values:
        return CandidateCouplingClass.UNRESOLVED
    if values & _REANALYSIS_CHANGES:
        return CandidateCouplingClass.REANALYSIS_REQUIRED
    if values <= _FIXED_ACTION_CHANGES:
        return CandidateCouplingClass.FIXED_ACTION
    return CandidateCouplingClass.UNRESOLVED


def build_candidate_domain(domain: DiscreteCandidateDomain) -> CandidateDomainOutput:
    """Expand a bounded Cartesian product and seal canonical candidate identities."""

    _validate_domain(domain)
    baseline = next(
        item
        for item in domain.section_choices
        if item.choice_id == domain.baseline_section_choice_id
    )
    candidates: list[BeamCandidateDefinition] = []
    for section in domain.section_choices:
        for longitudinal in domain.longitudinal_choices:
            for transverse in domain.transverse_choices:
                physical = CandidatePhysicalDefinition(
                    section.width_mm,
                    section.overall_depth_mm,
                    section.concrete_strength_n_per_mm2,
                    longitudinal.top_bar_count,
                    longitudinal.top_bar_diameter_mm,
                    longitudinal.top_layer_count,
                    longitudinal.bottom_bar_count,
                    longitudinal.bottom_bar_diameter_mm,
                    longitudinal.bottom_layer_count,
                    longitudinal.steel_grade_n_per_mm2,
                    transverse.link_diameter_mm,
                    transverse.steel_grade_n_per_mm2,
                    transverse.legs,
                    transverse.spacing_mm,
                )
                physical_id = semantic_hash(
                    "candidate_physical_definition_id", physical
                )
                changes = {
                    CandidateChangeCategory.ACTUAL_BARS,
                    CandidateChangeCategory.DETAILING,
                    CandidateChangeCategory.BAR_PATHS,
                    CandidateChangeCategory.BBS,
                    *section.additional_change_categories,
                }
                if (
                    section.width_mm != baseline.width_mm
                    or section.overall_depth_mm != baseline.overall_depth_mm
                ):
                    changes.add(CandidateChangeCategory.SECTION_DIMENSIONS_PROPERTY)
                if (
                    section.concrete_strength_n_per_mm2
                    != baseline.concrete_strength_n_per_mm2
                ):
                    changes.add(CandidateChangeCategory.MATERIAL_STIFFNESS)
                ordered_changes = tuple(sorted(changes, key=lambda item: item.value))
                candidate_payload = {
                    "change_categories": ordered_changes,
                    "domain_id": domain.domain_id,
                    "domain_revision_id": domain.revision_id,
                    "longitudinal_choice_id": longitudinal.choice_id,
                    "physical_definition_id": physical_id,
                    "section_choice_id": section.choice_id,
                    "transverse_choice_id": transverse.choice_id,
                }
                candidate_id = semantic_hash("beam_candidate_id", candidate_payload)
                candidates.append(
                    BeamCandidateDefinition(
                        candidate_id,
                        physical_id,
                        domain.domain_id,
                        domain.revision_id,
                        section,
                        longitudinal,
                        transverse,
                        physical,
                        ordered_changes,
                        _coupling_class(ordered_changes),
                    )
                )
    ordered = tuple(sorted(candidates, key=lambda item: item.candidate_id))
    semantic_payload = {
        "domain_id": domain.domain_id,
        "domain_revision_id": domain.revision_id,
        "project_basis_id": domain.project_basis_id,
        "profile_revision_id": domain.profile_revision_id,
        "member_id": domain.member_id,
        "topology_revision_id": domain.topology_revision_id,
        "action_revision_id": domain.action_revision_id,
        "design_scope_revision_id": domain.design_scope_revision_id,
        "baseline_analysis_revision_id": domain.baseline_analysis_revision_id,
        "baseline_section_choice_id": domain.baseline_section_choice_id,
        "traversal_order": TRAVERSAL_ORDER,
        "candidate_ids": tuple(item.candidate_id for item in ordered),
    }
    return CandidateDomainOutput(
        domain.domain_id,
        domain.revision_id,
        semantic_hash("candidate_domain_id", semantic_payload),
        domain.project_basis_id,
        domain.profile_revision_id,
        domain.member_id,
        domain.topology_revision_id,
        domain.action_revision_id,
        domain.design_scope_revision_id,
        domain.baseline_analysis_revision_id,
        domain.baseline_section_choice_id,
        TRAVERSAL_ORDER,
        ordered,
        len(ordered),
    )


def _binding_reasons(
    binding: CandidateResultBinding,
    payload: object,
    expected_operation: str,
    prefix: str,
    *,
    allow_engineering_fail: bool,
) -> list[str]:
    reasons: list[str] = []
    if not all(
        _text(value)
        for value in (
            binding.result_id,
            binding.normalized_input_id,
            binding.calculation_id,
            binding.output_payload_id,
        )
    ):
        reasons.append(f"{prefix}.BINDING_IDENTITY")
    if binding.operation_semantic_id != expected_operation:
        reasons.append(f"{prefix}.OPERATION_MISMATCH")
    if binding.output_payload_id != semantic_hash("output_payload_id", payload):
        reasons.append(f"{prefix}.PAYLOAD_MISMATCH")
    if binding.execution is not ExecutionState.COMPLETED:
        reasons.append(f"{prefix}.EXECUTION_INCOMPLETE")
    if binding.applicability is not ApplicabilityState.APPLICABLE:
        reasons.append(f"{prefix}.NOT_APPLICABLE")
    if binding.completeness is not CompletenessState.COMPLETE_FOR_SCOPE:
        reasons.append(f"{prefix}.PARTIAL")
    if binding.freshness is not FreshnessState.CURRENT:
        reasons.append(f"{prefix}.STALE")
    if binding.engineering is EngineeringState.NOT_EVALUATED:
        reasons.append(f"{prefix}.NOT_EVALUATED")
    elif binding.engineering is EngineeringState.FAIL and not allow_engineering_fail:
        reasons.append(f"{prefix}.FAIL")
    return reasons


def _expected_leaf_id(expectations: tuple[MemberLeafExpectation, ...]) -> str:
    return semantic_hash("expected_leaf_set_id", expectations)


def _context_reasons(context: CandidateRankingContext) -> list[str]:
    if not all(
        _text(value)
        for value in (
            context.project_basis_id,
            context.profile_revision_id,
            context.member_id,
            context.topology_revision_id,
            context.action_revision_id,
            context.design_scope_revision_id,
            context.baseline_analysis_revision_id,
            context.reference_member_result_id,
        )
    ):
        return ["CONTEXT.IDENTITY"]
    member = context.reference_member
    reasons = _binding_reasons(
        context.reference_member_binding,
        member,
        MEMBER_DESIGN_OPERATION,
        "REFERENCE_MEMBER",
        allow_engineering_fail=True,
    )
    if context.reference_member_result_id != context.reference_member_binding.result_id:
        reasons.append("REFERENCE_MEMBER.RESULT_ID_MISMATCH")
    if (
        member.project_basis_id != context.project_basis_id
        or member.profile_revision_id != context.profile_revision_id
        or member.member_id != context.member_id
        or member.topology_revision_id != context.topology_revision_id
        or member.action_revision_id != context.action_revision_id
        or member.design_scope_revision_id != context.design_scope_revision_id
    ):
        reasons.append("REFERENCE_MEMBER.CONTEXT_MISMATCH")
    if not member.expected_leaves:
        reasons.append("REFERENCE_MEMBER.EXPECTED_LEAVES_EMPTY")
    return reasons


def _profile_reasons(profile: CandidateObjectiveProfile) -> list[str]:
    reasons: list[str] = []
    if not _text(profile.profile_id) or not _text(profile.revision_id):
        reasons.append("OBJECTIVE_PROFILE.IDENTITY")
    if not profile.objectives or len(set(profile.objectives)) != len(
        profile.objectives
    ):
        reasons.append("OBJECTIVE_PROFILE.OBJECTIVES")
    if len(set(profile.tie_breakers)) != len(profile.tie_breakers):
        reasons.append("OBJECTIVE_PROFILE.TIE_BREAKERS")
    return reasons


def _domain_context_reasons(
    context: CandidateRankingContext, domain: CandidateDomainOutput
) -> list[str]:
    reasons: list[str] = []
    if (
        not _text(domain.domain_id)
        or not _text(domain.domain_revision_id)
        or not _text(domain.domain_semantic_id)
        or domain.traversal_order != TRAVERSAL_ORDER
        or domain.generated_count != len(domain.candidates)
        or tuple(sorted(domain.candidates, key=lambda item: item.candidate_id))
        != domain.candidates
        or len({item.candidate_id for item in domain.candidates})
        != len(domain.candidates)
    ):
        reasons.append("DOMAIN.OUTPUT_INVALID")
    if any(
        item.domain_id != domain.domain_id
        or item.domain_revision_id != domain.domain_revision_id
        for item in domain.candidates
    ):
        reasons.append("DOMAIN.CANDIDATE_BINDING")
    baseline_sections = {
        item.section
        for item in domain.candidates
        if item.section.choice_id == domain.baseline_section_choice_id
    }
    baseline = next(iter(baseline_sections)) if len(baseline_sections) == 1 else None
    if baseline is None:
        reasons.append("DOMAIN.BASELINE_SECTION")
    for item in domain.candidates:
        expected_physical = CandidatePhysicalDefinition(
            item.section.width_mm,
            item.section.overall_depth_mm,
            item.section.concrete_strength_n_per_mm2,
            item.longitudinal.top_bar_count,
            item.longitudinal.top_bar_diameter_mm,
            item.longitudinal.top_layer_count,
            item.longitudinal.bottom_bar_count,
            item.longitudinal.bottom_bar_diameter_mm,
            item.longitudinal.bottom_layer_count,
            item.longitudinal.steel_grade_n_per_mm2,
            item.transverse.link_diameter_mm,
            item.transverse.steel_grade_n_per_mm2,
            item.transverse.legs,
            item.transverse.spacing_mm,
        )
        physical_id = semantic_hash("candidate_physical_definition_id", item.physical)
        candidate_id = semantic_hash(
            "beam_candidate_id",
            {
                "change_categories": item.change_categories,
                "domain_id": domain.domain_id,
                "domain_revision_id": domain.domain_revision_id,
                "longitudinal_choice_id": item.longitudinal.choice_id,
                "physical_definition_id": physical_id,
                "section_choice_id": item.section.choice_id,
                "transverse_choice_id": item.transverse.choice_id,
            },
        )
        expected_changes = {
            CandidateChangeCategory.ACTUAL_BARS,
            CandidateChangeCategory.DETAILING,
            CandidateChangeCategory.BAR_PATHS,
            CandidateChangeCategory.BBS,
            *item.section.additional_change_categories,
        }
        if baseline is not None:
            if (
                item.section.width_mm != baseline.width_mm
                or item.section.overall_depth_mm != baseline.overall_depth_mm
            ):
                expected_changes.add(
                    CandidateChangeCategory.SECTION_DIMENSIONS_PROPERTY
                )
            if (
                item.section.concrete_strength_n_per_mm2
                != baseline.concrete_strength_n_per_mm2
            ):
                expected_changes.add(CandidateChangeCategory.MATERIAL_STIFFNESS)
        ordered_changes = tuple(sorted(expected_changes, key=lambda value: value.value))
        if (
            item.physical != expected_physical
            or item.physical_definition_id != physical_id
            or item.candidate_id != candidate_id
            or item.change_categories != ordered_changes
            or item.coupling_class != _coupling_class(ordered_changes)
        ):
            reasons.append("DOMAIN.CANDIDATE_IDENTITY")
            break
    semantic_payload = {
        "domain_id": domain.domain_id,
        "domain_revision_id": domain.domain_revision_id,
        "project_basis_id": domain.project_basis_id,
        "profile_revision_id": domain.profile_revision_id,
        "member_id": domain.member_id,
        "topology_revision_id": domain.topology_revision_id,
        "action_revision_id": domain.action_revision_id,
        "design_scope_revision_id": domain.design_scope_revision_id,
        "baseline_analysis_revision_id": domain.baseline_analysis_revision_id,
        "baseline_section_choice_id": domain.baseline_section_choice_id,
        "traversal_order": domain.traversal_order,
        "candidate_ids": tuple(item.candidate_id for item in domain.candidates),
    }
    if domain.domain_semantic_id != semantic_hash(
        "candidate_domain_id", semantic_payload
    ):
        reasons.append("DOMAIN.SEMANTIC_ID_MISMATCH")
    if (
        domain.project_basis_id != context.project_basis_id
        or domain.profile_revision_id != context.profile_revision_id
        or domain.member_id != context.member_id
        or domain.topology_revision_id != context.topology_revision_id
        or domain.action_revision_id != context.action_revision_id
        or domain.design_scope_revision_id != context.design_scope_revision_id
        or domain.baseline_analysis_revision_id != context.baseline_analysis_revision_id
    ):
        reasons.append("DOMAIN.CONTEXT_MISMATCH")
    return reasons


def _reanalysis_reasons(
    candidate: BeamCandidateDefinition,
    evaluation: CandidateEvaluation,
    request: CandidateRankingRequest,
) -> list[str]:
    if candidate.coupling_class is CandidateCouplingClass.UNRESOLVED:
        return ["COUPLING.UNRESOLVED"]
    if request.analysis_mode is AnalysisMode.FIXED_ACTIONS:
        if (
            evaluation.analysis_revision_id
            != request.context.baseline_analysis_revision_id
        ):
            return ["ANALYSIS.FIXED_ACTION_REVISION_MISMATCH"]
        return []
    if candidate.coupling_class is CandidateCouplingClass.FIXED_ACTION:
        if (
            evaluation.analysis_revision_id
            != request.context.baseline_analysis_revision_id
        ):
            return ["ANALYSIS.FIXED_CHANGE_REVISION_MISMATCH"]
        return []
    policy = request.reanalysis_policy
    evidence = evaluation.reanalysis_evidence
    reasons: list[str] = []
    if policy is None or not all(
        _text(value)
        for value in (policy.policy_id, policy.revision_id, policy.source_reference)
    ):
        reasons.append("REANALYSIS.POLICY_REQUIRED")
    elif not policy.owned_copy_required:
        reasons.append("REANALYSIS.OWNED_COPY_REQUIRED")
    if evidence is None:
        reasons.append("REANALYSIS.EVIDENCE_REQUIRED")
        return reasons
    if not _valid_reanalysis_evidence(candidate, evaluation, request.context, evidence):
        reasons.append("REANALYSIS.EVIDENCE_INVALID")
    return reasons


def _valid_reanalysis_evidence(
    candidate: BeamCandidateDefinition,
    evaluation: CandidateEvaluation,
    context: CandidateRankingContext,
    evidence: CandidateReanalysisEvidence,
) -> bool:
    return (
        evidence.candidate_id == candidate.candidate_id
        and evidence.candidate_definition_id == candidate.physical_definition_id
        and evidence.baseline_analysis_revision_id
        == context.baseline_analysis_revision_id
        and evidence.candidate_analysis_revision_id == evaluation.analysis_revision_id
        and evidence.candidate_analysis_revision_id
        != context.baseline_analysis_revision_id
        and all(
            _text(value)
            for value in (
                evidence.snapshot_result_id,
                evidence.snapshot_output_payload_id,
            )
        )
        and evidence.execution_completed
        and evidence.freshness_current
    )


def _member_evidence_reasons(
    candidate: BeamCandidateDefinition,
    evaluation: CandidateEvaluation,
    context: CandidateRankingContext,
) -> tuple[list[str], bool]:
    member = evaluation.member_result
    reasons = _binding_reasons(
        evaluation.member_binding,
        member,
        MEMBER_DESIGN_OPERATION,
        "MEMBER",
        allow_engineering_fail=True,
    )
    if (
        member.project_basis_id != context.project_basis_id
        or member.profile_revision_id != context.profile_revision_id
        or member.member_id != context.member_id
        or member.topology_revision_id != context.topology_revision_id
        or member.action_revision_id != context.action_revision_id
        or member.design_scope_revision_id != context.design_scope_revision_id
        or member.reinforcement_revision_id != candidate.candidate_id
    ):
        reasons.append("MEMBER.CONTEXT_MISMATCH")
    if plain(member.expected_leaves) != plain(context.reference_member.expected_leaves):
        reasons.append("MEMBER.EXPECTED_LEAF_SET_MISMATCH")
    qualification_by_id = {
        item.expectation.leaf_id: item for item in member.leaf_qualifications
    }
    if len(qualification_by_id) != len(member.leaf_qualifications):
        reasons.append("MEMBER.DUPLICATE_LEAF")
    engineering_fail = False
    expected_ids = {item.leaf_id for item in context.reference_member.expected_leaves}
    if set(qualification_by_id) != expected_ids:
        reasons.append("MEMBER.LEAF_COVERAGE")
    for expectation in context.reference_member.expected_leaves:
        qualification = qualification_by_id.get(expectation.leaf_id)
        if qualification is None:
            continue
        if plain(qualification.expectation) != plain(expectation):
            reasons.append(f"LEAF.{expectation.leaf_id}.EXPECTATION_MISMATCH")
            continue
        evidence = qualification.evidence
        evidence_identity_valid = (
            evidence is not None
            and evidence.leaf_id == expectation.leaf_id
            and evidence.operation_semantic_id == expectation.operation_semantic_id
            and (
                expectation.code_data_revision_id is None
                or evidence.code_data_revision_id == expectation.code_data_revision_id
            )
            and all(
                _text(value)
                for value in (
                    evidence.result_id,
                    evidence.code_data_revision_id,
                    evidence.method_revision_id,
                    evidence.normalized_input_id,
                    evidence.calculation_id,
                )
            )
        )
        if not evidence_identity_valid:
            reasons.append(f"LEAF.{expectation.leaf_id}.IDENTITY_INVALID")
            continue
        assert evidence is not None
        if expectation.expected_applicability is ApplicabilityState.NOT_APPLICABLE:
            if (
                not qualification.qualified
                or evidence.execution is not ExecutionState.COMPLETED
                or evidence.applicability is not ApplicabilityState.NOT_APPLICABLE
                or evidence.engineering is not EngineeringState.NOT_EVALUATED
                or evidence.completeness is not CompletenessState.COMPLETE_FOR_SCOPE
                or evidence.freshness is not FreshnessState.CURRENT
            ):
                reasons.append(f"LEAF.{expectation.leaf_id}.EXCLUDED_NA_INVALID")
            continue
        if evidence.engineering is EngineeringState.FAIL:
            if (
                qualification.qualified
                or "LEAF.FAIL" not in qualification.reason_codes
                or evidence.execution is not ExecutionState.COMPLETED
                or evidence.applicability is not ApplicabilityState.APPLICABLE
                or evidence.completeness is not CompletenessState.COMPLETE_FOR_SCOPE
                or evidence.freshness is not FreshnessState.CURRENT
            ):
                reasons.append(f"LEAF.{expectation.leaf_id}.FAIL_STATE_INVALID")
            else:
                engineering_fail = True
        elif (
            not qualification.qualified
            or evidence.execution is not ExecutionState.COMPLETED
            or evidence.applicability is not ApplicabilityState.APPLICABLE
            or evidence.engineering is not EngineeringState.PASS
            or evidence.completeness is not CompletenessState.COMPLETE_FOR_SCOPE
            or evidence.freshness is not FreshnessState.CURRENT
        ):
            reasons.append(f"LEAF.{expectation.leaf_id}.INCOMPLETE")
    if evaluation.member_binding.engineering is EngineeringState.FAIL:
        engineering_fail = True
    expected_engineering = (
        EngineeringState.PASS
        if member.qualified
        else (
            EngineeringState.FAIL
            if engineering_fail
            else EngineeringState.NOT_EVALUATED
        )
    )
    if evaluation.member_binding.engineering is not expected_engineering:
        reasons.append("MEMBER.ENGINEERING_STATE_MISMATCH")
    if member.qualified != (not reasons and not engineering_fail):
        reasons.append("MEMBER.QUALIFIED_FLAG_MISMATCH")
    return reasons, engineering_fail


def _quantity_reasons(
    candidate: BeamCandidateDefinition,
    evaluation: CandidateEvaluation,
    context: CandidateRankingContext,
) -> list[str]:
    quantities = evaluation.quantities
    reasons = _binding_reasons(
        evaluation.quantity_binding,
        quantities,
        QUANTITY_OPERATION,
        "QUANTITY",
        allow_engineering_fail=False,
    )
    if (
        quantities.project_basis_id != context.project_basis_id
        or quantities.member_id != context.member_id
        or quantities.detail_revision_id != candidate.candidate_id
    ):
        reasons.append("QUANTITY.CONTEXT_MISMATCH")
    if quantities.coupler_count < 0 or not all(
        _nonnegative(value)
        for value in (
            quantities.steel_scheduled_mass_kg,
            quantities.steel_stock_mass_kg,
            quantities.concrete_volume_m3,
            quantities.formwork_area_m2,
        )
    ):
        reasons.append("QUANTITY.NONFINITE")
    return reasons


def _cost_metric(
    evaluation: CandidateEvaluation,
    candidate: BeamCandidateDefinition,
    context: CandidateRankingContext,
) -> tuple[ObjectiveMetric | None, list[str]]:
    if evaluation.cost is None or evaluation.cost_binding is None:
        return None, ["OBJECTIVE.COST_MISSING"]
    cost = evaluation.cost
    reasons = _binding_reasons(
        evaluation.cost_binding,
        cost,
        COST_OPERATION,
        "COST",
        allow_engineering_fail=False,
    )
    if (
        cost.project_basis_id != context.project_basis_id
        or cost.member_id != context.member_id
        or cost.detail_revision_id != candidate.candidate_id
        or cost.quantity_result_id != evaluation.quantity_binding.result_id
    ):
        reasons.append("COST.CONTEXT_MISMATCH")
    if not _text(cost.currency):
        reasons.append("OBJECTIVE.COST_MISSING")
        return None, reasons
    if not _NONNEGATIVE_DECIMAL.fullmatch(cost.total_decimal):
        reasons.append("COST.TOTAL_INVALID")
        return None, reasons
    try:
        value = float(Decimal(cost.total_decimal))
    except (InvalidOperation, ValueError, OverflowError):
        reasons.append("COST.TOTAL_INVALID")
        return None, reasons
    if not _nonnegative(value):
        reasons.append("COST.TOTAL_INVALID")
        return None, reasons
    return (
        ObjectiveMetric(
            CandidateObjectiveKind.COST,
            value,
            cost.currency,
            evaluation.cost_binding.result_id,
        ),
        reasons,
    )


def _objective_metrics(
    candidate: BeamCandidateDefinition,
    evaluation: CandidateEvaluation,
    profile: CandidateObjectiveProfile,
    context: CandidateRankingContext,
) -> tuple[tuple[ObjectiveMetric, ...], list[str]]:
    metrics: list[ObjectiveMetric] = []
    reasons: list[str] = []
    for objective in profile.objectives:
        if objective is CandidateObjectiveKind.COST:
            metric, metric_reasons = _cost_metric(evaluation, candidate, context)
            reasons.extend(metric_reasons)
            if metric is not None:
                metrics.append(metric)
        elif objective is CandidateObjectiveKind.STEEL_MASS:
            metrics.append(
                ObjectiveMetric(
                    objective,
                    evaluation.quantities.steel_scheduled_mass_kg,
                    "kg",
                    evaluation.quantity_binding.result_id,
                )
            )
        elif objective is CandidateObjectiveKind.SECTION_DEPTH:
            metrics.append(
                ObjectiveMetric(
                    objective,
                    candidate.physical.overall_depth_mm,
                    "mm",
                    candidate.physical_definition_id,
                )
            )
        elif objective is CandidateObjectiveKind.CONCRETE_VOLUME:
            metrics.append(
                ObjectiveMetric(
                    objective,
                    evaluation.quantities.concrete_volume_m3,
                    "m3",
                    evaluation.quantity_binding.result_id,
                )
            )
        elif objective is CandidateObjectiveKind.FORMWORK_AREA:
            metrics.append(
                ObjectiveMetric(
                    objective,
                    evaluation.quantities.formwork_area_m2,
                    "m2",
                    evaluation.quantity_binding.result_id,
                )
            )
        elif objective is CandidateObjectiveKind.CARBON:
            if (
                evaluation.embodied_carbon_kg_co2e is None
                or not _nonnegative(evaluation.embodied_carbon_kg_co2e)
                or not _text(evaluation.carbon_basis_id)
            ):
                reasons.append("OBJECTIVE.CARBON_MISSING")
            else:
                assert evaluation.embodied_carbon_kg_co2e is not None
                assert evaluation.carbon_basis_id is not None
                metrics.append(
                    ObjectiveMetric(
                        objective,
                        evaluation.embodied_carbon_kg_co2e,
                        "kg_co2e",
                        evaluation.carbon_basis_id,
                    )
                )
        elif objective is CandidateObjectiveKind.CONGESTION:
            if (
                evaluation.congestion_score is None
                or not _nonnegative(evaluation.congestion_score)
                or not _text(evaluation.congestion_basis_id)
            ):
                reasons.append("OBJECTIVE.CONGESTION_MISSING")
            else:
                assert evaluation.congestion_score is not None
                assert evaluation.congestion_basis_id is not None
                metrics.append(
                    ObjectiveMetric(
                        objective,
                        evaluation.congestion_score,
                        "ratio",
                        evaluation.congestion_basis_id,
                    )
                )
        else:
            utilization = evaluation.member_result.governing_utilization
            if utilization is None or not _nonnegative(utilization):
                reasons.append("OBJECTIVE.UTILIZATION_MISSING")
            else:
                metrics.append(
                    ObjectiveMetric(
                        objective,
                        max(0.0, 1.0 - utilization),
                        "ratio",
                        evaluation.member_binding.result_id,
                    )
                )
    return tuple(metrics), reasons


def _metric_sort_value(metric: ObjectiveMetric) -> float:
    if metric.kind is CandidateObjectiveKind.UTILIZATION_RESERVE:
        return -metric.value
    return metric.value


def _tie_values(
    candidate: BeamCandidateDefinition,
    evaluation: CandidateEvaluation,
    tie_breakers: tuple[CandidateTieBreaker, ...],
) -> tuple[float | int | str, ...]:
    values: list[float | int | str] = []
    for tie in tie_breakers:
        if tie is CandidateTieBreaker.LOWER_UTILIZATION:
            utilization = evaluation.member_result.governing_utilization
            values.append(utilization if utilization is not None else math.inf)
        elif tie is CandidateTieBreaker.FEWER_BAR_MARKS:
            values.append(len(evaluation.quantities.steel_items))
        elif tie is CandidateTieBreaker.LOWER_SECTION_DEPTH:
            values.append(candidate.physical.overall_depth_mm)
        else:
            values.append(candidate.candidate_id)
    return tuple(values)


def _validate_search_shape(
    request: CandidateRankingRequest,
) -> tuple[
    list[BeamCandidateDefinition],
    dict[str, CandidateEvaluation],
    list[CandidateExclusion],
]:
    candidates = list(request.domain.candidates)
    seen_physical: set[str] = set()
    evaluable: list[BeamCandidateDefinition] = []
    exclusions: list[CandidateExclusion] = []
    for candidate in candidates:
        if candidate.physical_definition_id in seen_physical:
            exclusions.append(
                CandidateExclusion(
                    candidate.candidate_id,
                    CandidateDisposition.DUPLICATE_PHYSICAL_DEFINITION,
                    ("DOMAIN.DUPLICATE_PHYSICAL_DEFINITION",),
                    None,
                )
            )
        else:
            seen_physical.add(candidate.physical_definition_id)
            if candidate.coupling_class is CandidateCouplingClass.UNRESOLVED:
                exclusions.append(
                    CandidateExclusion(
                        candidate.candidate_id,
                        CandidateDisposition.INCOMPLETE,
                        ("COUPLING.UNRESOLVED",),
                        None,
                    )
                )
            else:
                evaluable.append(candidate)
    evaluation_ids = tuple(item.candidate_id for item in request.evaluations)
    if len(set(evaluation_ids)) != len(evaluation_ids):
        raise ValueError("EVALUATION.DUPLICATE_CANDIDATE")
    if evaluation_ids != tuple(
        item.candidate_id for item in evaluable[: len(evaluation_ids)]
    ):
        raise ValueError("EVALUATION.NOT_CANONICAL_PREFIX")
    if (
        request.evaluation_budget <= 0
        or request.evaluation_budget > MAXIMUM_DOMAIN_CANDIDATES
    ):
        raise ValueError("SEARCH.BUDGET")
    if len(request.evaluations) > request.evaluation_budget:
        raise ValueError("SEARCH.BUDGET_EXCEEDED")
    if request.stop_reason is SearchStopReason.COMPLETED:
        if len(request.evaluations) != len(evaluable):
            raise ValueError("SEARCH.COMPLETED_WITHOUT_FULL_EVALUATION")
    elif request.stop_reason is SearchStopReason.EVALUATION_BUDGET_REACHED:
        if len(request.evaluations) != request.evaluation_budget or len(
            request.evaluations
        ) >= len(evaluable):
            raise ValueError("SEARCH.BUDGET_STOP_INVALID")
    return (
        evaluable,
        {item.candidate_id: item for item in request.evaluations},
        exclusions,
    )


def _rank_output(request: CandidateRankingRequest) -> CandidateRankingOutput:
    context_reasons = _context_reasons(request.context)
    profile_reasons = _profile_reasons(request.objective_profile)
    domain_reasons = _domain_context_reasons(request.context, request.domain)
    if context_reasons or profile_reasons or domain_reasons:
        raise ValueError(
            ";".join((*context_reasons, *profile_reasons, *domain_reasons))
        )
    evaluable, evaluation_by_id, exclusions = _validate_search_shape(request)
    tie_breakers = (
        *(
            item
            for item in request.objective_profile.tie_breakers
            if item is not CandidateTieBreaker.CANDIDATE_ID
        ),
        CandidateTieBreaker.CANDIDATE_ID,
    )
    candidate_by_id = {item.candidate_id: item for item in request.domain.candidates}
    records: list[CandidateEvaluationRecord] = []
    feasible: list[
        tuple[BeamCandidateDefinition, CandidateEvaluation, tuple[ObjectiveMetric, ...]]
    ] = []
    engineering_fail_count = 0
    incomplete_count = sum(
        item.disposition is CandidateDisposition.INCOMPLETE for item in exclusions
    )
    for candidate in evaluable:
        evaluation = evaluation_by_id.get(candidate.candidate_id)
        if evaluation is None:
            exclusion = CandidateExclusion(
                candidate.candidate_id,
                CandidateDisposition.NOT_EVALUATED,
                ("SEARCH.NOT_EVALUATED",),
                None,
            )
            exclusions.append(exclusion)
            records.append(
                CandidateEvaluationRecord(
                    candidate.candidate_id,
                    candidate.physical_definition_id,
                    exclusion.disposition,
                    None,
                    None,
                    None,
                    None,
                    (),
                    exclusion.reason_codes,
                )
            )
            continue
        reasons = _reanalysis_reasons(candidate, evaluation, request)
        member_reasons, engineering_fail = _member_evidence_reasons(
            candidate, evaluation, request.context
        )
        reasons.extend(member_reasons)
        reasons.extend(_quantity_reasons(candidate, evaluation, request.context))
        metrics, objective_reasons = _objective_metrics(
            candidate, evaluation, request.objective_profile, request.context
        )
        reasons.extend(objective_reasons)
        reasons = list(dict.fromkeys(reasons))
        if reasons:
            disposition = CandidateDisposition.INCOMPLETE
            incomplete_count += 1
        elif engineering_fail:
            disposition = CandidateDisposition.ENGINEERING_FAIL
            engineering_fail_count += 1
            reasons = ["ENGINEERING.REQUIRED_CHECK_FAILED"]
        else:
            disposition = CandidateDisposition.FEASIBLE
            feasible.append((candidate, evaluation, metrics))
        records.append(
            CandidateEvaluationRecord(
                candidate.candidate_id,
                candidate.physical_definition_id,
                disposition,
                evaluation.analysis_revision_id,
                evaluation.member_binding,
                evaluation.quantity_binding,
                evaluation.cost_binding,
                metrics,
                tuple(reasons),
            )
        )
        if disposition is not CandidateDisposition.FEASIBLE:
            exclusions.append(
                CandidateExclusion(
                    candidate.candidate_id,
                    disposition,
                    tuple(reasons),
                    evaluation.member_binding.result_id,
                )
            )
    duplicate_count = sum(
        item.disposition is CandidateDisposition.DUPLICATE_PHYSICAL_DEFINITION
        for item in exclusions
    )
    recorded_ids = {item.candidate_id for item in records}
    for exclusion in exclusions:
        if exclusion.candidate_id not in recorded_ids:
            candidate = candidate_by_id[exclusion.candidate_id]
            records.append(
                CandidateEvaluationRecord(
                    candidate.candidate_id,
                    candidate.physical_definition_id,
                    exclusion.disposition,
                    None,
                    None,
                    None,
                    None,
                    (),
                    exclusion.reason_codes,
                )
            )
            recorded_ids.add(exclusion.candidate_id)
    feasible.sort(
        key=lambda item: (
            *(_metric_sort_value(metric) for metric in item[2]),
            *_tie_values(item[0], item[1], tie_breakers),
        )
    )
    ranked = tuple(
        RankedCandidate(
            index,
            candidate.candidate_id,
            candidate.physical_definition_id,
            candidate.coupling_class,
            evaluation.analysis_revision_id,
            evaluation.member_binding.result_id,
            evaluation.quantity_binding.result_id,
            evaluation.cost_binding.result_id if evaluation.cost_binding else None,
            metrics,
        )
        for index, (candidate, evaluation, metrics) in enumerate(feasible, start=1)
    )
    stop_complete = request.stop_reason is SearchStopReason.COMPLETED and len(
        request.evaluations
    ) == len(evaluable)
    has_unresolved = any(
        item.coupling_class is CandidateCouplingClass.UNRESOLVED
        for item in request.domain.candidates
    )
    enumeration_complete = stop_complete
    if request.stop_reason is SearchStopReason.EVALUATION_BUDGET_REACHED:
        terminal = SearchTerminalState.BUDGET_EXHAUSTED_INCOMPLETE
    elif request.stop_reason is SearchStopReason.CANCELLED:
        terminal = SearchTerminalState.CANCELLED_INCOMPLETE
    elif not enumeration_complete or has_unresolved or incomplete_count > 0:
        terminal = SearchTerminalState.EVIDENCE_INCOMPLETE
    elif not ranked:
        terminal = SearchTerminalState.NO_FEASIBLE_CANDIDATE
    else:
        terminal = SearchTerminalState.COMPLETE_ENUMERATION
    performance = SearchPerformance(
        len(request.domain.candidates),
        len(request.domain.candidates) - duplicate_count,
        duplicate_count,
        request.evaluation_budget,
        len(request.evaluations),
        len(ranked),
        engineering_fail_count,
        incomplete_count,
    )
    optimality_scope = (
        "finite_domain_fixed_actions_common_force_assumption"
        if request.analysis_mode is AnalysisMode.FIXED_ACTIONS
        else "finite_domain_candidate_specific_coupled_reanalysis"
    )
    complete_with_feasible = terminal is SearchTerminalState.COMPLETE_ENUMERATION
    no_feasible = terminal is SearchTerminalState.NO_FEASIBLE_CANDIDATE
    return CandidateRankingOutput(
        request.ranking_id,
        request.domain.domain_id,
        request.domain.domain_semantic_id,
        _expected_leaf_id(request.context.reference_member.expected_leaves),
        request.analysis_mode,
        request.context.baseline_analysis_revision_id,
        request.objective_profile.profile_id,
        request.objective_profile.revision_id,
        tie_breakers,
        tuple(sorted(records, key=lambda item: item.candidate_id)),
        ranked,
        tuple(sorted(exclusions, key=lambda item: item.candidate_id)),
        performance,
        terminal,
        enumeration_complete,
        ranked[0].candidate_id if ranked else None,
        ranked[0].candidate_id if complete_with_feasible else None,
        complete_with_feasible,
        no_feasible,
        bool(ranked) and not complete_with_feasible,
        optimality_scope,
    )


def _rejected(
    operation: str,
    inputs: dict[str, dict[str, object]],
    error: ValueError,
    source_references: tuple[str, ...] = (),
) -> OperationResult:
    detail = str(error) or "SEARCH.INVALID"
    return rejected_result(
        operation,
        inputs,
        (
            _diagnostic(
                operation,
                detail.split(";", 1)[0],
                f"The candidate search request is invalid: {detail}",
                "request",
                "Correct the finite domain, evidence identities, stop state, and objective profile.",
            ),
        ),
        provenance=_provenance(source_references),
    )


def _ranking_result(
    request: CandidateRankingRequest,
    output: CandidateRankingOutput,
) -> OperationResult:
    inputs = effective_inputs(request=request)
    payload = {"ranking": output}
    diagnostics: tuple[Diagnostic, ...] = ()
    if output.terminal_state is SearchTerminalState.COMPLETE_ENUMERATION:
        return completed_result(
            RANK_CANDIDATES_OPERATION,
            inputs,
            payload,
            provenance=_provenance(),
        )
    if output.terminal_state is SearchTerminalState.NO_FEASIBLE_CANDIDATE:
        return completed_result(
            RANK_CANDIDATES_OPERATION,
            inputs,
            payload,
            engineering=EngineeringState.FAIL,
            diagnostics=(
                _diagnostic(
                    RANK_CANDIDATES_OPERATION,
                    "SEARCH.NO_FEASIBLE_CANDIDATE",
                    "Every unique candidate failed at least one required engineering leaf.",
                    "evaluations",
                    "Expand or revise the finite candidate domain and reevaluate all candidates.",
                ),
            ),
            provenance=_provenance(),
        )
    diagnostics = (
        _diagnostic(
            RANK_CANDIDATES_OPERATION,
            f"SEARCH.{output.terminal_state.value.upper()}",
            "The retained ranking is provisional because the finite search is incomplete.",
            "evaluations",
            "Complete all required candidate evidence before claiming an optimum or infeasibility.",
        ),
    )
    return partial_result(
        RANK_CANDIDATES_OPERATION,
        inputs,
        payload,
        diagnostics,
        provenance=_provenance(),
    )


def rank_candidates(request: CandidateRankingRequest) -> OperationResult:
    """AO05: rank evaluated candidates only after complete profile-derived checks."""

    inputs = effective_inputs(request=request)
    try:
        output = _rank_output(request)
    except ValueError as error:
        return _rejected(RANK_CANDIDATES_OPERATION, inputs, error)
    return _ranking_result(request, output)


def optimize_beam(request: BeamOptimizationRequest) -> OperationResult:
    """AO21: generate the finite domain and make only evidence-supported claims."""

    inputs = effective_inputs(request=request)
    try:
        domain = build_candidate_domain(request.domain)
        if (
            request.domain.project_basis_id != request.context.project_basis_id
            or request.domain.profile_revision_id != request.context.profile_revision_id
            or request.domain.member_id != request.context.member_id
            or request.domain.topology_revision_id
            != request.context.topology_revision_id
            or request.domain.action_revision_id != request.context.action_revision_id
            or request.domain.design_scope_revision_id
            != request.context.design_scope_revision_id
            or request.domain.baseline_analysis_revision_id
            != request.context.baseline_analysis_revision_id
        ):
            raise ValueError("DOMAIN.CONTEXT_MISMATCH")
        ranking = _rank_output(
            CandidateRankingRequest(
                request.search_id,
                request.context,
                domain,
                request.objective_profile,
                request.analysis_mode,
                request.reanalysis_policy,
                request.evaluation_budget,
                request.stop_reason,
                request.evaluations,
            )
        )
    except ValueError as error:
        return _rejected(
            OPTIMIZE_BEAM_OPERATION,
            inputs,
            error,
            request.domain.source_references,
        )
    output = BeamOptimizationOutput(request.search_id, domain, ranking)
    payload = {"optimization": output}
    if ranking.terminal_state is SearchTerminalState.COMPLETE_ENUMERATION:
        return completed_result(
            OPTIMIZE_BEAM_OPERATION,
            inputs,
            payload,
            provenance=_provenance(request.domain.source_references),
        )
    if ranking.terminal_state is SearchTerminalState.NO_FEASIBLE_CANDIDATE:
        return completed_result(
            OPTIMIZE_BEAM_OPERATION,
            inputs,
            payload,
            engineering=EngineeringState.FAIL,
            diagnostics=(
                _diagnostic(
                    OPTIMIZE_BEAM_OPERATION,
                    "SEARCH.NO_FEASIBLE_CANDIDATE",
                    "The complete finite search found no candidate that passed every required leaf.",
                    "evaluations",
                    "Revise the candidate domain or design basis before running another search.",
                ),
            ),
            provenance=_provenance(request.domain.source_references),
        )
    return partial_result(
        OPTIMIZE_BEAM_OPERATION,
        inputs,
        payload,
        (
            _diagnostic(
                OPTIMIZE_BEAM_OPERATION,
                f"SEARCH.{ranking.terminal_state.value.upper()}",
                "The search stopped without the evidence required for an optimum claim.",
                "evaluations",
                "Complete the canonical candidate prefix and every profile-required check.",
            ),
        ),
        provenance=_provenance(request.domain.source_references),
    )


__all__ = [
    "COST_OPERATION",
    "MEMBER_DESIGN_OPERATION",
    "MAXIMUM_DOMAIN_CANDIDATES",
    "OPTIMIZE_BEAM_OPERATION",
    "QUANTITY_OPERATION",
    "RANK_CANDIDATES_OPERATION",
    "TRAVERSAL_ORDER",
    "build_candidate_domain",
    "candidate_result_binding",
    "optimize_beam",
    "rank_candidates",
]
