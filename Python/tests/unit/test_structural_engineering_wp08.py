"""WP08 finite-domain optimization truthfulness and determinism fixtures."""

from __future__ import annotations

from dataclasses import replace

import pytest

from structural_lib.beam.member import (
    MemberDesignOutput,
    MemberLeafEvidence,
    MemberLeafExpectation,
    MemberLeafQualification,
)
from structural_lib.beam.project import CheckScope
from structural_lib.beam.semantics import (
    ApplicabilityState,
    CompletenessState,
    EngineeringState,
    ExecutionState,
    FreshnessState,
    Provenance,
    completed_result,
    effective_inputs,
)
from structural_lib.beam_optimization import (
    AnalysisMode,
    BeamOptimizationRequest,
    CandidateChangeCategory,
    CandidateDisposition,
    CandidateEvaluation,
    CandidateObjectiveKind,
    CandidateObjectiveProfile,
    CandidateRankingContext,
    CandidateRankingRequest,
    CandidateReanalysisEvidence,
    CandidateTieBreaker,
    DiscreteCandidateDomain,
    LongitudinalCandidateChoice,
    ReanalysisPolicy,
    SearchStopReason,
    SectionCandidateChoice,
    TransverseCandidateChoice,
    build_candidate_domain,
    candidate_result_binding,
    optimize_beam,
    rank_candidates,
)
from structural_lib.construction.contracts import (
    ConstructionCostOutput,
    ConstructionQuantityOutput,
    WasteLedger,
)

PROVENANCE = Provenance("test-data-r1", "test-method-r1", ("WP08 test fixture",))


def _expectation(
    leaf_id: str = "uls@member",
    applicability: ApplicabilityState = ApplicabilityState.APPLICABLE,
) -> MemberLeafExpectation:
    return MemberLeafExpectation(
        leaf_id,
        leaf_id.split("@", 1)[0],
        f"test.{leaf_id.split('@', 1)[0]}/v1",
        "B1",
        CheckScope.MEMBER,
        applicability,
        "test-data-r1",
    )


def _member(
    candidate_id: str,
    *,
    state: EngineeringState = EngineeringState.PASS,
    expected: tuple[MemberLeafExpectation, ...] | None = None,
    applicability_override: ApplicabilityState | None = None,
    utilization: float = 0.8,
) -> MemberDesignOutput:
    expectations = expected or (_expectation(),)
    qualifications: list[MemberLeafQualification] = []
    any_fail = False
    any_incomplete = False
    for expectation in expectations:
        applicability = applicability_override or expectation.expected_applicability
        evidence_state = (
            EngineeringState.NOT_EVALUATED
            if applicability is ApplicabilityState.NOT_APPLICABLE
            else state
        )
        qualifies = (
            applicability is expectation.expected_applicability
            and (
                (
                    applicability is ApplicabilityState.APPLICABLE
                    and evidence_state is EngineeringState.PASS
                )
                or (
                    applicability is ApplicabilityState.NOT_APPLICABLE
                    and evidence_state is EngineeringState.NOT_EVALUATED
                )
            )
        )
        any_fail |= evidence_state is EngineeringState.FAIL
        any_incomplete |= not qualifies and not any_fail
        evidence = MemberLeafEvidence(
            expectation.leaf_id,
            expectation.operation_semantic_id,
            f"leaf-result-{candidate_id}-{expectation.leaf_id}",
            ExecutionState.COMPLETED,
            applicability,
            evidence_state,
            CompletenessState.COMPLETE_FOR_SCOPE,
            FreshnessState.CURRENT,
            "test-data-r1",
            "test-method-r1",
            f"leaf-input-{candidate_id}-{expectation.leaf_id}",
            f"leaf-calc-{candidate_id}-{expectation.leaf_id}",
            governing_utilization=utilization,
        )
        qualifications.append(
            MemberLeafQualification(
                expectation,
                evidence,
                qualifies,
                () if qualifies else ("LEAF.FAIL" if any_fail else "LEAF.APPLICABILITY_MISMATCH",),
            )
        )
    qualified = not any_fail and not any_incomplete and all(
        item.qualified for item in qualifications
    )
    return MemberDesignOutput(
        "project-r1",
        "profile-r1",
        "B1",
        "topology-r1",
        "actions-r1",
        candidate_id,
        "scope-r1",
        expectations,
        tuple(qualifications),
        (),
        expectations[0].leaf_id,
        qualifications[0].evidence.result_id,
        utilization,
        qualified,
    )


def _envelope(payload: object, operation: str, engineering: EngineeringState):
    return completed_result(
        operation,
        effective_inputs(fixture="wp08"),
        {"payload": payload},
        engineering=engineering,
        provenance=PROVENANCE,
    )


def _quantities(candidate_id: str, steel_kg: float = 100.0) -> ConstructionQuantityOutput:
    return ConstructionQuantityOutput(
        "profile-r1",
        "project-r1",
        "B1",
        candidate_id,
        f"bbs-{candidate_id}",
        "concrete-policy-r1",
        "formwork-policy-r1",
        (),
        (),
        (),
        WasteLedger(0, 0, 0),
        steel_kg,
        steel_kg,
        0.9,
        7.8,
        0,
    )


def _cost(
    candidate_id: str, quantity_result_id: str, total: float
) -> ConstructionCostOutput:
    decimal = f"{total:.2f}"
    return ConstructionCostOutput(
        "profile-r1",
        "project-r1",
        "B1",
        candidate_id,
        quantity_result_id,
        "rates-r1",
        "rates-revision-r1",
        "INR",
        "2026-09-04",
        "India",
        "test-rate-source",
        (),
        (),
        (),
        decimal,
        "0.00",
        decimal,
        "0.00",
        decimal,
    )


def _domain(
    *,
    sections: tuple[SectionCandidateChoice, ...] | None = None,
    longitudinal: tuple[LongitudinalCandidateChoice, ...] | None = None,
) -> DiscreteCandidateDomain:
    return DiscreteCandidateDomain(
        "domain-r1",
        "domain-revision-r1",
        "project-r1",
        "profile-r1",
        "B1",
        "topology-r1",
        "actions-r1",
        "scope-r1",
        "analysis-r1",
        "S1",
        sections
        or (SectionCandidateChoice("S1", 300, 500, 25),),
        longitudinal
        or (
            LongitudinalCandidateChoice("L1", 2, 16, 1, 3, 20, 1, 500),
            LongitudinalCandidateChoice("L2", 2, 16, 1, 4, 20, 1, 500),
            LongitudinalCandidateChoice("L3", 2, 16, 1, 5, 20, 1, 500),
        ),
        (TransverseCandidateChoice("T1", 8, 500, 2, 150),),
        100,
        ("WP08 test domain",),
        ("Finite declared choices only",),
    )


def _context(
    expected: tuple[MemberLeafExpectation, ...] | None = None,
) -> CandidateRankingContext:
    reference = _member("reference", expected=expected)
    result = _envelope(
        reference, "is456.beam_member.design/v1", EngineeringState.PASS
    )
    return CandidateRankingContext(
        "project-r1",
        "profile-r1",
        "B1",
        "topology-r1",
        "actions-r1",
        "scope-r1",
        "analysis-r1",
        result.result_id,
        candidate_result_binding(result, reference),
        reference,
    )


def _profile(
    *objectives: CandidateObjectiveKind,
) -> CandidateObjectiveProfile:
    return CandidateObjectiveProfile(
        "objectives-r1",
        "objectives-revision-r1",
        objectives or (CandidateObjectiveKind.COST,),
        (
            CandidateTieBreaker.LOWER_UTILIZATION,
            CandidateTieBreaker.FEWER_BAR_MARKS,
        ),
    )


def _evaluation(
    candidate_id: str,
    *,
    engineering: EngineeringState = EngineeringState.PASS,
    expected: tuple[MemberLeafExpectation, ...] | None = None,
    applicability_override: ApplicabilityState | None = None,
    steel_kg: float = 100,
    cost_total: float = 1000,
    utilization: float = 0.8,
    analysis_revision_id: str = "analysis-r1",
    reanalysis: CandidateReanalysisEvidence | None = None,
) -> CandidateEvaluation:
    member = _member(
        candidate_id,
        state=engineering,
        expected=expected,
        applicability_override=applicability_override,
        utilization=utilization,
    )
    member_envelope = _envelope(
        member,
        "is456.beam_member.design/v1",
        engineering if engineering is not EngineeringState.NOT_EVALUATED else engineering,
    )
    quantities = _quantities(candidate_id, steel_kg)
    quantity_envelope = _envelope(
        quantities,
        "structural.construction_quantities.calculate/v1",
        EngineeringState.PASS,
    )
    cost = _cost(candidate_id, quantity_envelope.result_id, cost_total)
    cost_envelope = _envelope(
        cost,
        "structural.construction_cost.estimate/v1",
        EngineeringState.PASS,
    )
    return CandidateEvaluation(
        candidate_id,
        analysis_revision_id,
        candidate_result_binding(member_envelope, member),
        member,
        candidate_result_binding(quantity_envelope, quantities),
        quantities,
        candidate_result_binding(cost_envelope, cost),
        cost,
        reanalysis_evidence=reanalysis,
    )


def _rank(
    domain: DiscreteCandidateDomain,
    evaluations: tuple[CandidateEvaluation, ...],
    *,
    context: CandidateRankingContext | None = None,
    profile: CandidateObjectiveProfile | None = None,
    mode: AnalysisMode = AnalysisMode.FIXED_ACTIONS,
    policy: ReanalysisPolicy | None = None,
    budget: int | None = None,
    stop: SearchStopReason = SearchStopReason.COMPLETED,
):
    expanded = build_candidate_domain(domain)
    return rank_candidates(
        CandidateRankingRequest(
            "rank-r1",
            context or _context(),
            expanded,
            profile or _profile(),
            mode,
            policy,
            budget or len(evaluations),
            stop,
            evaluations,
        )
    )


def test_domain_is_canonical_and_duplicate_physical_labels_are_retained() -> None:
    repeated = (
        LongitudinalCandidateChoice("L-A", 2, 16, 1, 3, 20, 1, 500),
        LongitudinalCandidateChoice("L-B", 2, 16, 1, 3, 20, 1, 500),
    )
    output = build_candidate_domain(_domain(longitudinal=repeated))
    evaluations = (_evaluation(output.candidates[0].candidate_id),)
    result = _rank(_domain(longitudinal=repeated), evaluations)
    ranking = result.outputs["ranking"]

    assert tuple(item.candidate_id for item in output.candidates) == tuple(
        sorted(item.candidate_id for item in output.candidates)
    )
    assert output.candidates[0].physical_definition_id == output.candidates[1].physical_definition_id
    assert ranking["performance"]["duplicate_physical_candidate_count"] == 1
    assert any(
        item["disposition"] == CandidateDisposition.DUPLICATE_PHYSICAL_DEFINITION
        for item in ranking["exclusions"]
    )


def test_domain_identities_match_portable_cross_language_vector() -> None:
    domain = _domain(longitudinal=(_domain().longitudinal_choices[0],))
    output = build_candidate_domain(domain)
    candidate = output.candidates[0]

    assert candidate.physical_definition_id == (
        "candidate_physical_definition_id:pf4-canonical-json-v1:"
        "90ee7462f17213d30ad5db1b1ffa7b3b6e457da10fb1af83a40c730d8ce600b1"
    )
    assert candidate.candidate_id == (
        "beam_candidate_id:pf4-canonical-json-v1:"
        "8e1523fd24a52bde7a96f47fa8608e98301aebf4f17319082ddc1e910084873e"
    )
    assert output.domain_semantic_id == (
        "candidate_domain_id:pf4-canonical-json-v1:"
        "cf3a07c34d286a5336bd7f1a3c1d8a748cecc31e66f3a849539ae4f251917807"
    )


def test_domain_rejects_declared_bound_above_portable_safety_ceiling() -> None:
    with pytest.raises(ValueError, match="DOMAIN.BOUND_EXCEEDED"):
        build_candidate_domain(replace(_domain(), maximum_domain_candidates=100_001))


def test_only_third_candidate_feasible_and_complete_search_selects_it() -> None:
    domain = _domain()
    candidates = build_candidate_domain(domain).candidates
    evaluations = tuple(
        _evaluation(
            item.candidate_id,
            engineering=(
                EngineeringState.PASS if index == 2 else EngineeringState.FAIL
            ),
        )
        for index, item in enumerate(candidates)
    )
    result = _rank(domain, evaluations)
    ranking = result.outputs["ranking"]

    assert result.engineering is EngineeringState.PASS
    assert ranking["selected_candidate_id"] == candidates[2].candidate_id
    assert ranking["optimality_claimed"] is True
    assert ranking["performance"]["engineering_fail_count"] == 2


def test_objective_tie_uses_explicit_candidate_id_last() -> None:
    domain = _domain()
    candidates = build_candidate_domain(domain).candidates
    evaluations = tuple(_evaluation(item.candidate_id) for item in candidates)
    ranking = _rank(domain, evaluations).outputs["ranking"]

    assert ranking["effective_tie_breakers"][-1] == CandidateTieBreaker.CANDIDATE_ID
    assert [item["candidate_id"] for item in ranking["ranked_candidates"]] == [
        item.candidate_id for item in candidates
    ]


def test_missing_required_sls_leaf_is_incomplete_not_feasible() -> None:
    expected = (_expectation(), _expectation("sls@member"))
    context = _context(expected)
    domain = _domain(longitudinal=(_domain().longitudinal_choices[0],))
    candidate = build_candidate_domain(domain).candidates[0]
    evaluation = _evaluation(candidate.candidate_id)
    result = _rank(domain, (evaluation,), context=context)
    ranking = result.outputs["ranking"]

    assert result.completeness is CompletenessState.PARTIAL
    assert ranking["terminal_state"] == "evidence_incomplete"
    assert ranking["enumeration_complete"] is True
    assert ranking["optimality_claimed"] is False


def test_profile_excluded_not_applicable_is_valid_but_required_na_is_not() -> None:
    excluded = (_expectation("torsion@member", ApplicabilityState.NOT_APPLICABLE),)
    context = _context(excluded)
    domain = _domain(longitudinal=(_domain().longitudinal_choices[0],))
    candidate = build_candidate_domain(domain).candidates[0]
    accepted = _evaluation(candidate.candidate_id, expected=excluded)
    accepted_result = _rank(domain, (accepted,), context=context)

    required = (_expectation("sls@member"),)
    required_context = _context(required)
    wrong_na = _evaluation(
        candidate.candidate_id,
        expected=required,
        applicability_override=ApplicabilityState.NOT_APPLICABLE,
        engineering=EngineeringState.NOT_EVALUATED,
    )
    rejected_result = _rank(domain, (wrong_na,), context=required_context)

    assert accepted_result.outputs["ranking"]["optimality_claimed"] is True
    assert rejected_result.outputs["ranking"]["terminal_state"] == "evidence_incomplete"
    assert rejected_result.outputs["ranking"]["ranked_candidates"] == []


def test_budget_truncation_retains_best_evaluated_without_optimum_claim() -> None:
    domain = _domain()
    candidates = build_candidate_domain(domain).candidates
    result = _rank(
        domain,
        (_evaluation(candidates[0].candidate_id, cost_total=500),),
        budget=1,
        stop=SearchStopReason.EVALUATION_BUDGET_REACHED,
    )
    ranking = result.outputs["ranking"]

    assert ranking["terminal_state"] == "budget_exhausted_incomplete"
    assert ranking["best_evaluated_candidate_id"] == candidates[0].candidate_id
    assert ranking["selected_candidate_id"] is None
    assert ranking["provisional_shortlist"] is True


def test_cancelled_prefix_cannot_claim_optimum_or_infeasibility() -> None:
    domain = _domain()
    candidates = build_candidate_domain(domain).candidates
    result = _rank(
        domain,
        (_evaluation(candidates[0].candidate_id, engineering=EngineeringState.FAIL),),
        budget=3,
        stop=SearchStopReason.CANCELLED,
    )
    ranking = result.outputs["ranking"]

    assert ranking["terminal_state"] == "cancelled_incomplete"
    assert ranking["optimality_claimed"] is False
    assert ranking["infeasible_claimed"] is False


def test_complete_all_fail_domain_can_claim_infeasible() -> None:
    domain = _domain()
    candidates = build_candidate_domain(domain).candidates
    evaluations = tuple(
        _evaluation(item.candidate_id, engineering=EngineeringState.FAIL)
        for item in candidates
    )
    result = _rank(domain, evaluations)
    ranking = result.outputs["ranking"]

    assert result.engineering is EngineeringState.FAIL
    assert ranking["terminal_state"] == "no_feasible_candidate"
    assert ranking["infeasible_claimed"] is True


def test_fixed_actions_marks_section_change_but_uses_common_force_revision() -> None:
    sections = (
        SectionCandidateChoice("S1", 300, 500, 25),
        SectionCandidateChoice("S2", 300, 600, 25),
    )
    domain = _domain(
        sections=sections,
        longitudinal=(_domain().longitudinal_choices[0],),
    )
    candidates = build_candidate_domain(domain).candidates
    changed = next(
        item
        for item in candidates
        if CandidateChangeCategory.SECTION_DIMENSIONS_PROPERTY in item.change_categories
    )
    evaluations = tuple(_evaluation(item.candidate_id) for item in candidates)
    result = _rank(domain, evaluations)

    assert changed.coupling_class.value == "reanalysis_required"
    assert result.outputs["ranking"]["optimality_scope"] == (
        "finite_domain_fixed_actions_common_force_assumption"
    )
    assert result.outputs["ranking"]["optimality_claimed"] is True


def test_coupled_section_change_requires_candidate_specific_fresh_analysis() -> None:
    sections = (
        SectionCandidateChoice("S1", 300, 500, 25),
        SectionCandidateChoice("S2", 300, 600, 25),
    )
    domain = _domain(
        sections=sections,
        longitudinal=(_domain().longitudinal_choices[0],),
    )
    candidates = build_candidate_domain(domain).candidates
    evaluations = tuple(_evaluation(item.candidate_id) for item in candidates)
    result = _rank(
        domain,
        evaluations,
        mode=AnalysisMode.COUPLED_REANALYSIS,
        policy=ReanalysisPolicy("P1", "r1", True, "owned-model policy"),
    )

    assert result.outputs["ranking"]["terminal_state"] == "evidence_incomplete"
    assert any(
        "REANALYSIS.EVIDENCE_REQUIRED" in item["reason_codes"]
        for item in result.outputs["ranking"]["exclusions"]
    )


def test_coupled_section_change_accepts_bound_reanalysis_evidence() -> None:
    sections = (
        SectionCandidateChoice("S1", 300, 500, 25),
        SectionCandidateChoice("S2", 300, 600, 25),
    )
    domain = _domain(
        sections=sections,
        longitudinal=(_domain().longitudinal_choices[0],),
    )
    candidates = build_candidate_domain(domain).candidates
    evaluations: list[CandidateEvaluation] = []
    for item in candidates:
        if item.coupling_class.value == "reanalysis_required":
            analysis_id = f"analysis-{item.candidate_id}"
            evidence = CandidateReanalysisEvidence(
                item.candidate_id,
                item.physical_definition_id,
                "analysis-r1",
                analysis_id,
                f"snapshot-{item.candidate_id}",
                f"snapshot-payload-{item.candidate_id}",
                True,
                True,
            )
            evaluations.append(
                _evaluation(
                    item.candidate_id,
                    analysis_revision_id=analysis_id,
                    reanalysis=evidence,
                )
            )
        else:
            evaluations.append(_evaluation(item.candidate_id))
    result = _rank(
        domain,
        tuple(evaluations),
        mode=AnalysisMode.COUPLED_REANALYSIS,
        policy=ReanalysisPolicy("P1", "r1", True, "owned-model policy"),
    )

    assert result.outputs["ranking"]["terminal_state"] == "complete_enumeration"
    assert result.outputs["ranking"]["optimality_claimed"] is True


def test_wp07_quantity_and_cost_outputs_drive_objectives() -> None:
    domain = _domain()
    candidates = build_candidate_domain(domain).candidates
    evaluations = (
        _evaluation(candidates[0].candidate_id, steel_kg=80, cost_total=900),
        _evaluation(candidates[1].candidate_id, steel_kg=70, cost_total=1100),
        _evaluation(candidates[2].candidate_id, steel_kg=100, cost_total=800),
    )
    profile = _profile(CandidateObjectiveKind.STEEL_MASS, CandidateObjectiveKind.COST)
    ranking = _rank(domain, evaluations, profile=profile).outputs["ranking"]

    assert ranking["ranked_candidates"][0]["candidate_id"] == candidates[1].candidate_id
    assert [
        metric["value"] for metric in ranking["ranked_candidates"][0]["objective_metrics"]
    ] == [70, 1100]


def test_optimize_operation_returns_domain_and_ranking_with_same_identity() -> None:
    domain = _domain(longitudinal=(_domain().longitudinal_choices[0],))
    candidate = build_candidate_domain(domain).candidates[0]
    result = optimize_beam(
        BeamOptimizationRequest(
            "search-r1",
            _context(),
            domain,
            _profile(),
            AnalysisMode.FIXED_ACTIONS,
            None,
            1,
            SearchStopReason.COMPLETED,
            (_evaluation(candidate.candidate_id),),
        )
    )
    optimization = result.outputs["optimization"]

    assert optimization["domain"]["domain_semantic_id"] == optimization["ranking"][
        "domain_semantic_id"
    ]
    assert optimization["ranking"]["selected_candidate_id"] == candidate.candidate_id


def test_changed_typed_output_with_old_binding_is_rejected_as_incomplete() -> None:
    domain = _domain(longitudinal=(_domain().longitudinal_choices[0],))
    candidate = build_candidate_domain(domain).candidates[0]
    evaluation = _evaluation(candidate.candidate_id)
    detached = replace(
        evaluation,
        quantities=replace(evaluation.quantities, steel_scheduled_mass_kg=1),
    )
    result = _rank(domain, (detached,))

    assert result.outputs["ranking"]["terminal_state"] == "evidence_incomplete"
    assert "QUANTITY.PAYLOAD_MISMATCH" in result.outputs["ranking"]["exclusions"][0][
        "reason_codes"
    ]


def test_cost_objective_rejects_nonportable_decimal_notation() -> None:
    domain = _domain(longitudinal=(_domain().longitudinal_choices[0],))
    candidate = build_candidate_domain(domain).candidates[0]
    evaluation = _evaluation(candidate.candidate_id)
    invalid_cost = replace(evaluation.cost, total_decimal="1e3")
    invalid_envelope = _envelope(
        invalid_cost,
        "structural.construction_cost.estimate/v1",
        EngineeringState.PASS,
    )
    detached = replace(
        evaluation,
        cost=invalid_cost,
        cost_binding=candidate_result_binding(invalid_envelope, invalid_cost),
    )

    result = _rank(domain, (detached,))

    assert result.outputs["ranking"]["terminal_state"] == "evidence_incomplete"
    assert "COST.TOTAL_INVALID" in result.outputs["ranking"]["exclusions"][0][
        "reason_codes"
    ]


def test_stale_failed_leaf_cannot_support_infeasibility_claim() -> None:
    domain = _domain(longitudinal=(_domain().longitudinal_choices[0],))
    candidate = build_candidate_domain(domain).candidates[0]
    evaluation = _evaluation(
        candidate.candidate_id, engineering=EngineeringState.FAIL
    )
    qualification = evaluation.member_result.leaf_qualifications[0]
    assert qualification.evidence is not None
    stale_evidence = replace(
        qualification.evidence, freshness=FreshnessState.STALE
    )
    stale_member = replace(
        evaluation.member_result,
        leaf_qualifications=(replace(qualification, evidence=stale_evidence),),
    )
    stale_envelope = _envelope(
        stale_member,
        "is456.beam_member.design/v1",
        EngineeringState.FAIL,
    )
    stale = replace(
        evaluation,
        member_result=stale_member,
        member_binding=candidate_result_binding(stale_envelope, stale_member),
    )

    result = _rank(domain, (stale,))

    assert result.outputs["ranking"]["terminal_state"] == "evidence_incomplete"
    assert result.outputs["ranking"]["infeasible_claimed"] is False
    assert any(
        reason.endswith("FAIL_STATE_INVALID")
        for reason in result.outputs["ranking"]["exclusions"][0]["reason_codes"]
    )


def test_negative_coupler_count_is_incomplete_quantity_evidence() -> None:
    domain = _domain(longitudinal=(_domain().longitudinal_choices[0],))
    candidate = build_candidate_domain(domain).candidates[0]
    evaluation = _evaluation(candidate.candidate_id)
    invalid_quantities = replace(evaluation.quantities, coupler_count=-1)
    quantity_envelope = _envelope(
        invalid_quantities,
        "structural.construction_quantities.calculate/v1",
        EngineeringState.PASS,
    )
    invalid = replace(
        evaluation,
        quantity_binding=candidate_result_binding(
            quantity_envelope, invalid_quantities
        ),
        quantities=invalid_quantities,
        cost_binding=None,
        cost=None,
    )

    result = _rank(
        domain,
        (invalid,),
        profile=_profile(CandidateObjectiveKind.STEEL_MASS),
    )

    assert result.outputs["ranking"]["terminal_state"] == "evidence_incomplete"
    assert "QUANTITY.NONFINITE" in result.outputs["ranking"]["exclusions"][0][
        "reason_codes"
    ]


def test_cost_objective_requires_nonblank_currency() -> None:
    domain = _domain(longitudinal=(_domain().longitudinal_choices[0],))
    candidate = build_candidate_domain(domain).candidates[0]
    evaluation = _evaluation(candidate.candidate_id)
    invalid_cost = replace(evaluation.cost, currency="")
    invalid_envelope = _envelope(
        invalid_cost,
        "structural.construction_cost.estimate/v1",
        EngineeringState.PASS,
    )
    invalid = replace(
        evaluation,
        cost=invalid_cost,
        cost_binding=candidate_result_binding(invalid_envelope, invalid_cost),
    )

    result = _rank(domain, (invalid,))

    assert result.outputs["ranking"]["terminal_state"] == "evidence_incomplete"
    assert "OBJECTIVE.COST_MISSING" in result.outputs["ranking"]["exclusions"][
        0
    ]["reason_codes"]
