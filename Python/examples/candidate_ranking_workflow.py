"""Rank actual calculated arrangements within an explicit teaching profile.

Run from the examples directory or repository with the current source build:
    python3 Python/examples/candidate_ranking_workflow.py

Keep physical_member_workflow.py beside this file. It owns the shared example
inputs and invokes the library's real checks, physical paths, BBS and quantities.
The finite-domain result covers its declared geometry/flexure/seismic teaching
profile only. It is not a complete building design or construction approval.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace

from physical_member_workflow import Workflow, build_workflow

from structural_lib import beam
from structural_lib import beam_optimization as optimization


@dataclass(frozen=True)
class RankingWorkflow:
    domain: optimization.CandidateDomainOutput
    evaluations: tuple[optimization.CandidateEvaluation, ...]
    complete: beam.OperationResult
    budget_limited: beam.OperationResult
    stale: beam.OperationResult


def evaluate_fixture(
    candidate: optimization.BeamCandidateDefinition,
) -> tuple[optimization.CandidateEvaluation, Workflow]:
    """Map only the declared four-bar fixture; reject unsupported domain edits."""
    diameter_mm = candidate.physical.bottom_bar_diameter_mm
    supported = optimization.CandidatePhysicalDefinition(
        width_mm=300,
        overall_depth_mm=500,
        concrete_strength_n_per_mm2=25,
        top_bar_count=2,
        top_bar_diameter_mm=diameter_mm,
        top_layer_count=1,
        bottom_bar_count=2,
        bottom_bar_diameter_mm=diameter_mm,
        bottom_layer_count=1,
        longitudinal_steel_grade_n_per_mm2=415,
        link_diameter_mm=8,
        link_steel_grade_n_per_mm2=415,
        link_legs=2,
        link_spacing_mm=150,
    )
    if candidate.physical != supported:
        raise ValueError(
            "Extend the fixture's real calculation mapper before changing its physical domain"
        )
    workflow = build_workflow(
        bar_diameter_mm=diameter_mm,
        detail_revision=candidate.candidate_id,
        include_links=True,
    )
    evaluation = optimization.bind_candidate_evaluation(
        candidate_id=candidate.candidate_id,
        analysis_revision_id="fixed-actions-r1",
        member_result=workflow.member,
        quantity_result=workflow.quantities,
        cost_result=workflow.cost,
    )
    return evaluation, workflow


def build_ranking_workflow() -> RankingWorkflow:
    """Calculate three physical alternatives and retain every search outcome."""
    reference = build_workflow(include_links=True)
    member = reference.member.output_as("member_design", beam.MemberDesignOutput)
    context = optimization.CandidateRankingContext(
        project_basis_id=member.project_basis_id,
        profile_revision_id=member.profile_revision_id,
        member_id=member.member_id,
        topology_revision_id=member.topology_revision_id,
        action_revision_id=member.action_revision_id,
        design_scope_revision_id=member.design_scope_revision_id,
        baseline_analysis_revision_id="fixed-actions-r1",
        reference_member_result_id=reference.member.result_id,
        reference_member_binding=optimization.candidate_result_binding(
            reference.member, member
        ),
        reference_member=member,
    )
    domain_request = optimization.DiscreteCandidateDomain(
        domain_id="four-bars-and-links",
        revision_id="r1",
        project_basis_id=member.project_basis_id,
        profile_revision_id=member.profile_revision_id,
        member_id=member.member_id,
        topology_revision_id=member.topology_revision_id,
        action_revision_id=member.action_revision_id,
        design_scope_revision_id=member.design_scope_revision_id,
        baseline_analysis_revision_id=context.baseline_analysis_revision_id,
        baseline_section_choice_id="R300x500",
        section_choices=(
            optimization.SectionCandidateChoice("R300x500", 300, 500, 25),
        ),
        longitudinal_choices=tuple(
            optimization.LongitudinalCandidateChoice(
                f"4H{diameter}", 2, diameter, 1, 2, diameter, 1, 415
            )
            for diameter in (12, 20, 25)
        ),
        transverse_choices=(
            optimization.TransverseCandidateChoice("H8-150", 8, 415, 2, 150),
        ),
        maximum_domain_candidates=3,
        source_references=("Explicit physical_member_workflow teaching fixture",),
        limitations=(
            "Fixed 50 kNm actions and the declared teaching profile only.",
            "Four straight longitudinal bars plus 40 resolved closed centreline loops.",
            "No shear, serviceability, anchorage, durability or building-design qualification.",
        ),
    )
    domain = optimization.build_candidate_domain(domain_request)
    # The domain supplies the canonical order; do not sort by diameter or score.
    evaluated = tuple(evaluate_fixture(candidate) for candidate in domain.candidates)
    evaluations = tuple(item[0] for item in evaluated)
    objectives = optimization.CandidateObjectiveProfile(
        "steel-mass",
        "r1",
        (optimization.CandidateObjectiveKind.STEEL_MASS,),
        (optimization.CandidateTieBreaker.LOWER_UTILIZATION,),
    )
    request = optimization.BeamOptimizationRequest(
        search_id="three-diameters",
        context=context,
        domain=domain_request,
        objective_profile=objectives,
        analysis_mode=optimization.AnalysisMode.FIXED_ACTIONS,
        reanalysis_policy=None,
        evaluation_budget=3,
        stop_reason=optimization.SearchStopReason.COMPLETED,
        evaluations=evaluations,
    )
    complete = optimization.optimize_beam(request)
    output = complete.output_as("optimization", optimization.BeamOptimizationOutput)
    # AO05 accepts the expanded domain; AO21 expands it. Both use one ranker.
    ranked = optimization.rank_candidates(
        optimization.CandidateRankingRequest(
            ranking_id=request.search_id,
            context=context,
            domain=domain,
            objective_profile=objectives,
            analysis_mode=request.analysis_mode,
            reanalysis_policy=None,
            evaluation_budget=3,
            stop_reason=request.stop_reason,
            evaluations=evaluations,
        )
    )
    assert (
        ranked.output_as("ranking", optimization.CandidateRankingOutput)
        == output.ranking
    )
    budget_limited = optimization.optimize_beam(
        replace(
            request,
            evaluation_budget=2,
            evaluations=evaluations[:2],
            stop_reason=optimization.SearchStopReason.EVALUATION_BUDGET_REACHED,
        )
    )
    stale_evaluations = tuple(
        (
            optimization.bind_candidate_evaluation(
                candidate_id=evaluation.candidate_id,
                analysis_revision_id=evaluation.analysis_revision_id,
                member_result=workflow.stale_member,
                quantity_result=workflow.quantities,
                cost_result=workflow.cost,
            )
            if evaluation.candidate_id == output.ranking.selected_candidate_id
            else evaluation
        )
        for evaluation, workflow in evaluated
    )
    stale = optimization.optimize_beam(replace(request, evaluations=stale_evaluations))
    return RankingWorkflow(domain, evaluations, complete, budget_limited, stale)


def main() -> None:
    workflow = build_ranking_workflow()
    complete = workflow.complete.output_as(
        "optimization", optimization.BeamOptimizationOutput
    ).ranking
    partial = workflow.budget_limited.output_as(
        "optimization", optimization.BeamOptimizationOutput
    ).ranking
    stale = workflow.stale.output_as(
        "optimization", optimization.BeamOptimizationOutput
    ).ranking
    selected = next(
        item
        for item in workflow.domain.candidates
        if item.candidate_id == complete.selected_candidate_id
    )
    assert selected.physical.bottom_bar_diameter_mm == 20
    assert complete.performance.engineering_fail_count == 1
    assert complete.performance.feasible_count == 2
    assert complete.optimality_claimed and complete.enumeration_complete
    assert (
        partial.terminal_state
        is optimization.SearchTerminalState.BUDGET_EXHAUSTED_INCOMPLETE
    )
    assert partial.selected_candidate_id is None and not partial.optimality_claimed
    assert stale.terminal_state is optimization.SearchTerminalState.EVIDENCE_INCOMPLETE
    assert stale.selected_candidate_id is None and not stale.optimality_claimed
    print(
        json.dumps(
            {
                "scope": "finite teaching profile under fixed actions; not building-design approval",
                "candidates": [
                    {
                        "diameter_mm": candidate.physical.bottom_bar_diameter_mm,
                        "engineering": evaluation.member_binding.engineering,
                        "steel_kg": round(
                            evaluation.quantities.steel_scheduled_mass_kg, 6
                        ),
                        "scheduled_links": next(
                            row.scheduled_bar_count
                            for row in evaluation.quantities.steel_items
                            if row.bar_mark == "LINK-8"
                        ),
                    }
                    for candidate, evaluation in zip(
                        workflow.domain.candidates, workflow.evaluations, strict=True
                    )
                ],
                "selected_diameter_mm": selected.physical.bottom_bar_diameter_mm,
                "complete": complete.terminal_state,
                "budget_limited": partial.terminal_state,
                "stale": stale.terminal_state,
                "partial_or_stale_optimum_claimed": partial.optimality_claimed
                or stale.optimality_claimed,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
