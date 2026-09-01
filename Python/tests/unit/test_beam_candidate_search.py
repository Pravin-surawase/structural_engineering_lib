# SPDX-License-Identifier: MIT
"""B2 deterministic search and route-convergence acceptance."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from structural_lib.services.beam_candidate_evaluator import (
    BeamCandidateDefinitionDraftV2,
    build_beam_candidate_definition_v2,
    evaluate_beam_candidate_v2,
)
from structural_lib.services.beam_candidate_search import (
    BeamCandidateSearchDomainDraftV1,
    BeamCandidateSearchRequestV1,
    build_beam_candidate_search_domain_v1,
    search_beam_candidates_v1,
)
from structural_lib.services.beam_project_contracts import (
    BeamLongitudinalLayerV1,
    BeamMemberReinforcementScheduleDraftV1,
    build_beam_member_reinforcement_schedule_v1,
)
from tests.unit.test_beam_candidate_evaluator import _candidate


def _variant(
    criteria,
    catalogue,
    candidate,
    *,
    candidate_id: str,
    tension_count: int,
    tension_diameter_mm: float = 20.0,
):
    schedule_draft = BeamMemberReinforcementScheduleDraftV1.model_validate(
        candidate.schedule.model_dump(
            mode="python", exclude={"schema_version", "schedule_sha256"}
        )
    )
    layers = tuple(
        BeamLongitudinalLayerV1(
            face=layer.face,
            bar_count=(
                tension_count
                if layer.face == candidate.primary_tension_face
                else layer.bar_count
            ),
            bar_diameter_mm=(
                tension_diameter_mm
                if layer.face == candidate.primary_tension_face
                else layer.bar_diameter_mm
            ),
            grade_nmm2=layer.grade_nmm2,
        )
        for layer in candidate.schedule.longitudinal_layers
    )
    schedule = build_beam_member_reinforcement_schedule_v1(
        schedule_draft.model_copy(
            update={
                "schedule_id": f"fixture:schedule:{candidate_id}",
                "longitudinal_layers": layers,
            }
        ),
        criteria=criteria,
        catalogue=catalogue,
    )
    draft = BeamCandidateDefinitionDraftV2.model_validate(
        candidate.model_dump(
            mode="python", exclude={"schema_version", "candidate_sha256"}
        )
    ).model_copy(
        update={
            "candidate_id": candidate_id,
            "schedule": schedule,
            "side_face_disposition": schedule.side_face_disposition,
        }
    )
    return build_beam_candidate_definition_v2(
        draft, criteria=criteria, catalogue=catalogue
    )


def _domain(criteria, catalogue, candidates):
    return build_beam_candidate_search_domain_v1(
        BeamCandidateSearchDomainDraftV1(
            domain_id="fixture:search-domain",
            criteria_sha256=criteria.criteria_sha256,
            catalogue_sha256=catalogue.catalogue_sha256,
            candidates=tuple(candidates),
            source_references=("fixture:candidate-generator",),
            limitations=("Finite software acceptance fixture.",),
        ),
        criteria=criteria,
        catalogue=catalogue,
    )


def _search(criteria, catalogue, domain, *, maximum: int):
    return search_beam_candidates_v1(
        BeamCandidateSearchRequestV1(
            search_id="fixture:search-1",
            domain=domain,
            maximum_generated_candidates=maximum,
            maximum_evaluated_candidates=maximum,
        ),
        criteria=criteria,
        catalogue=catalogue,
    )


def test_complete_search_is_order_independent_and_routes_one_b1b_identity() -> None:
    criteria, catalogue, base = _candidate()
    heavier = _variant(
        criteria,
        catalogue,
        base,
        candidate_id="candidate:heavier",
        tension_count=5,
    )
    forward = _domain(criteria, catalogue, (base, heavier))
    reverse = _domain(criteria, catalogue, (heavier, base))

    assert forward == reverse
    result = _search(criteria, catalogue, forward, maximum=2)
    repeated = _search(criteria, catalogue, reverse, maximum=2)

    assert result == repeated
    assert result.budget.terminal_state == "COMPLETE_ENUMERATION"
    assert result.budget.generated_count == 2
    assert result.budget.evaluated_count == 2
    assert result.budget.accepted_count == 2
    assert result.budget.pruned_count == 0
    assert result.optimality_claimed is True
    assert result.pareto_complete is True
    assert result.infeasible_claimed is False
    assert result.provisional_shortlist is False
    assert result.cost_ranked[0].candidate_id == base.candidate_id
    assert {item.candidate_id for item in result.pareto_front} == {base.candidate_id}

    direct = {item.candidate_sha256: item for item in result.direct}
    for projection in (*result.cost_ranked, *result.pareto_front):
        source = direct[projection.candidate_sha256]
        assert projection.evaluation_sha256 == source.evaluation_sha256
        assert projection.verdict == source.verdict == "PASS"


def test_budget_exhaustion_never_claims_optimum_pareto_or_infeasibility() -> None:
    criteria, catalogue, base = _candidate()
    heavier = _variant(
        criteria,
        catalogue,
        base,
        candidate_id="candidate:heavier",
        tension_count=5,
    )
    result = _search(
        criteria,
        catalogue,
        _domain(criteria, catalogue, (base, heavier)),
        maximum=1,
    )

    assert result.budget.terminal_state == "BUDGET_EXHAUSTED_INCOMPLETE"
    assert result.budget.enumeration_complete is False
    assert result.budget.generated_count == 1
    assert result.budget.evaluated_count == 1
    assert result.optimality_claimed is False
    assert result.pareto_complete is False
    assert result.infeasible_claimed is False
    assert result.provisional_shortlist is False
    assert result.cost_ranked == result.pareto_front == ()
    assert len(result.direct) == 1


def test_allowed_incomplete_shortlist_is_explicitly_provisional() -> None:
    criteria, catalogue, base = _candidate(allow_incomplete_shortlist=True)
    heavier = _variant(
        criteria,
        catalogue,
        base,
        candidate_id="candidate:heavier",
        tension_count=5,
    )
    result = _search(
        criteria,
        catalogue,
        _domain(criteria, catalogue, (base, heavier)),
        maximum=1,
    )

    assert result.budget.terminal_state == "BUDGET_EXHAUSTED_INCOMPLETE"
    assert result.provisional_shortlist is True
    assert result.cost_ranked and result.pareto_front
    assert result.optimality_claimed is result.pareto_complete is False
    assert result.cost_ranked[0].evaluation_sha256 == (
        result.direct[0].evaluation_sha256
    )


def test_no_feasible_claim_requires_complete_failed_enumeration() -> None:
    criteria, catalogue, base = _candidate()
    failing = _variant(
        criteria,
        catalogue,
        base,
        candidate_id="candidate:insufficient",
        tension_count=2,
        tension_diameter_mm=16.0,
    )
    evaluation = evaluate_beam_candidate_v2(
        failing, criteria=criteria, catalogue=catalogue
    )
    assert evaluation.verdict == "FAIL"

    result = _search(
        criteria,
        catalogue,
        _domain(criteria, catalogue, (failing,)),
        maximum=1,
    )

    assert result.budget.terminal_state == "NO_FEASIBLE_CANDIDATE"
    assert result.budget.enumeration_complete is True
    assert result.infeasible_claimed is True
    assert result.optimality_claimed is result.pareto_complete is False
    assert result.cost_ranked == result.pareto_front == ()


def test_complete_fixture_hold_blocks_every_search_claim() -> None:
    criteria, catalogue, held = _candidate(reviewed=False)
    result = _search(
        criteria,
        catalogue,
        _domain(criteria, catalogue, (held,)),
        maximum=1,
    )

    assert result.evaluations[0].verdict == "HOLD"
    assert result.budget.terminal_state == "BLOCKED_MANDATORY_CHECK"
    assert result.budget.enumeration_complete is True
    assert result.optimality_claimed is False
    assert result.pareto_complete is False
    assert result.infeasible_claimed is False


def test_one_held_candidate_keeps_complete_domain_ranking_provisional() -> None:
    criteria, catalogue, base = _candidate()
    held_draft = BeamCandidateDefinitionDraftV2.model_validate(
        base.model_dump(mode="python", exclude={"schema_version", "candidate_sha256"})
    ).model_copy(
        update={
            "candidate_id": "candidate:missing-service-evidence",
            "supplemental_checks": tuple(
                item
                for item in base.supplemental_checks
                if item.check != "SERVICEABILITY"
            ),
        }
    )
    held = build_beam_candidate_definition_v2(
        held_draft, criteria=criteria, catalogue=catalogue
    )
    result = _search(
        criteria,
        catalogue,
        _domain(criteria, catalogue, (base, held)),
        maximum=2,
    )

    assert result.budget.terminal_state == "BLOCKED_MANDATORY_CHECK"
    assert result.budget.enumeration_complete is True
    assert result.provisional_shortlist is True
    assert {item.candidate_id for item in result.cost_ranked} == {base.candidate_id}
    assert result.optimality_claimed is result.pareto_complete is False


def test_domain_and_search_budget_digests_fail_closed() -> None:
    criteria, catalogue, candidate = _candidate()
    domain = _domain(criteria, catalogue, (candidate,))
    tampered_domain = domain.model_copy(update={"domain_sha256": "f" * 64})
    with pytest.raises(ValidationError, match="domain_sha256"):
        _search(criteria, catalogue, tampered_domain, maximum=1)

    with pytest.raises(ValidationError, match="evaluated bound"):
        BeamCandidateSearchRequestV1(
            search_id="fixture:invalid-budget",
            domain=domain,
            maximum_generated_candidates=1,
            maximum_evaluated_candidates=2,
        )
