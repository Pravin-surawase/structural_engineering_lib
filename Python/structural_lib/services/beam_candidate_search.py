"""Deterministic B2 search over exact B1B beam candidates.

This service owns traversal, counts, rankings, and completeness claims only.
Every engineering verdict and objective quantity is consumed unchanged from
``evaluate_beam_candidate_v2``; no beam equation is duplicated here.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Literal, Self

from pydantic import Field, model_validator

from structural_lib.services.beam_candidate_evaluator import (
    BeamCandidateDefinitionV2,
    BeamCandidateEvaluationResultV2,
    evaluate_beam_candidate_v2,
)
from structural_lib.services.beam_project_contracts import (
    ProjectBeamCandidateCatalogueV1,
    ProjectBeamCriteriaV1,
)
from structural_lib.services.contracts.common import StrictPublicModel

__all__ = [
    "BeamCandidateProjectionV1",
    "BeamCandidateSearchDomainDraftV1",
    "BeamCandidateSearchDomainV1",
    "BeamCandidateSearchRequestV1",
    "BeamCandidateSearchResultV1",
    "OptimizationSearchBudgetV1",
    "build_beam_candidate_search_domain_v1",
    "search_beam_candidates_v1",
]

_SHA = r"^[0-9a-f]{64}$"
SearchTerminalState = Literal[
    "COMPLETE_ENUMERATION",
    "BUDGET_EXHAUSTED_INCOMPLETE",
    "NO_FEASIBLE_CANDIDATE",
    "BLOCKED_MANDATORY_CHECK",
]


def _raise_json_type(value: object):
    raise TypeError(f"{type(value).__name__} is not canonically JSON serializable")


def _json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
        default=(
            lambda item: (
                item.model_dump(mode="json")
                if isinstance(item, StrictPublicModel)
                else _raise_json_type(item)
            )
        ),
    )


def _digest(value: object) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _validated(model: type[StrictPublicModel], value: StrictPublicModel):
    return model.model_validate(value.model_dump(mode="python"))


class BeamCandidateSearchDomainDraftV1(StrictPublicModel):
    """Finite caller-owned candidate domain before canonical ordering."""

    domain_id: str = Field(min_length=1, max_length=160)
    criteria_sha256: str = Field(pattern=_SHA)
    catalogue_sha256: str = Field(pattern=_SHA)
    candidates: tuple[BeamCandidateDefinitionV2, ...] = Field(
        min_length=1, max_length=100_000
    )
    traversal_order: Literal["CANDIDATE_SHA256_ASC"] = "CANDIDATE_SHA256_ASC"
    permitted_pruning_rules: tuple[Literal["NONE"], ...] = ("NONE",)
    source_references: tuple[str, ...] = Field(min_length=1)
    limitations: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_domain(self) -> Self:
        ids = tuple(item.candidate_id for item in self.candidates)
        hashes = tuple(item.candidate_sha256 for item in self.candidates)
        if len(ids) != len(set(ids)):
            raise ValueError("search candidate IDs must be unique")
        if len(hashes) != len(set(hashes)):
            raise ValueError("search candidate hashes must be unique")
        if self.permitted_pruning_rules != ("NONE",):
            raise ValueError("B2 v1 implements no pruning")
        if len(self.source_references) != len(set(self.source_references)):
            raise ValueError("search source references must be unique")
        return self


class BeamCandidateSearchDomainV1(BeamCandidateSearchDomainDraftV1):
    schema_version: Literal["beam-candidate-search-domain/v1"] = (
        "beam-candidate-search-domain/v1"
    )
    domain_sha256: str = Field(pattern=_SHA)

    @model_validator(mode="after")
    def validate_digest(self) -> Self:
        expected = _digest(self.model_dump(mode="json", exclude={"domain_sha256"}))
        if self.domain_sha256 != expected:
            raise ValueError("domain_sha256 does not match canonical search domain")
        hashes = tuple(item.candidate_sha256 for item in self.candidates)
        if hashes != tuple(sorted(hashes)):
            raise ValueError("search domain is not in canonical traversal order")
        return self


class BeamCandidateSearchRequestV1(StrictPublicModel):
    """Explicit deterministic bounds for one search invocation."""

    schema_version: Literal["beam-candidate-search-request/v1"] = (
        "beam-candidate-search-request/v1"
    )
    search_id: str = Field(min_length=1, max_length=160)
    domain: BeamCandidateSearchDomainV1
    maximum_generated_candidates: int = Field(ge=1, le=1_000_000)
    maximum_evaluated_candidates: int = Field(ge=1, le=1_000_000)

    @model_validator(mode="after")
    def validate_bounds(self) -> Self:
        if self.maximum_evaluated_candidates > self.maximum_generated_candidates:
            raise ValueError("evaluated bound cannot exceed generated bound")
        return self


class OptimizationSearchBudgetV1(StrictPublicModel):
    """Canonical B2 traversal policy, counts, and terminal completeness state."""

    schema_version: Literal["optimization-search-budget/v1"] = (
        "optimization-search-budget/v1"
    )
    domain_sha256: str = Field(pattern=_SHA)
    traversal_order: Literal["CANDIDATE_SHA256_ASC"]
    permitted_pruning_rules: tuple[Literal["NONE"], ...]
    tie_breaks: tuple[
        Literal["LOWER_UTILIZATION", "FEWER_BAR_MARKS", "PROPERTY_ID"], ...
    ]
    maximum_generated_candidates: int = Field(ge=1)
    maximum_evaluated_candidates: int = Field(ge=1)
    generated_count: int = Field(ge=0)
    pruned_count: int = Field(ge=0)
    evaluated_count: int = Field(ge=0)
    accepted_count: int = Field(ge=0)
    ranked_count: int = Field(ge=0)
    terminal_state: SearchTerminalState
    enumeration_complete: bool
    correctness_proof_sha256: str | None = Field(default=None, pattern=_SHA)
    budget_sha256: str = Field(pattern=_SHA)

    @model_validator(mode="after")
    def validate_budget(self) -> Self:
        if self.budget_sha256 != _digest(
            self.model_dump(mode="json", exclude={"budget_sha256"})
        ):
            raise ValueError("budget_sha256 does not match search budget")
        if self.generated_count > self.maximum_generated_candidates:
            raise ValueError("generated count exceeds its bound")
        if self.evaluated_count > self.maximum_evaluated_candidates:
            raise ValueError("evaluated count exceeds its bound")
        if self.pruned_count != 0 or self.correctness_proof_sha256 is not None:
            raise ValueError("B2 v1 does not implement pruning")
        if self.accepted_count > self.evaluated_count:
            raise ValueError("accepted count exceeds evaluated count")
        if self.ranked_count > self.accepted_count:
            raise ValueError("ranked count exceeds accepted count")
        complete_state = self.terminal_state in {
            "COMPLETE_ENUMERATION",
            "NO_FEASIBLE_CANDIDATE",
            "BLOCKED_MANDATORY_CHECK",
        }
        if self.enumeration_complete != complete_state:
            raise ValueError("terminal state and enumeration completeness disagree")
        return self


class BeamCandidateProjectionV1(StrictPublicModel):
    """One route-specific view retaining the exact B1B result identity."""

    route: Literal["DIRECT", "COST", "PARETO"]
    rank: int = Field(ge=1)
    candidate_id: str
    candidate_sha256: str = Field(pattern=_SHA)
    evaluation_sha256: str = Field(pattern=_SHA)
    verdict: Literal["PASS", "FAIL", "HOLD"]
    existing_property_id: str
    steel_mass_kg: float = Field(gt=0)
    total_cost: float = Field(ge=0)
    congestion_score: float = Field(gt=0)
    maximum_utilization: float = Field(ge=0)
    bar_mark_count: int = Field(ge=3)


class BeamCandidateSearchResultV1(StrictPublicModel):
    """Terminal search evidence with truthful ranking claims."""

    schema_version: Literal["beam-candidate-search-result/v1"] = (
        "beam-candidate-search-result/v1"
    )
    search_id: str
    domain_sha256: str = Field(pattern=_SHA)
    budget: OptimizationSearchBudgetV1
    evaluations: tuple[BeamCandidateEvaluationResultV2, ...]
    direct: tuple[BeamCandidateProjectionV1, ...]
    cost_ranked: tuple[BeamCandidateProjectionV1, ...]
    pareto_front: tuple[BeamCandidateProjectionV1, ...]
    optimality_claimed: bool
    pareto_complete: bool
    infeasible_claimed: bool
    provisional_shortlist: bool
    result_sha256: str = Field(pattern=_SHA)

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        if self.result_sha256 != _digest(
            self.model_dump(mode="json", exclude={"result_sha256"})
        ):
            raise ValueError("result_sha256 does not match candidate search result")
        complete = self.budget.terminal_state == "COMPLETE_ENUMERATION"
        infeasible = self.budget.terminal_state == "NO_FEASIBLE_CANDIDATE"
        if self.optimality_claimed != (complete and bool(self.cost_ranked)):
            raise ValueError("optimality claim disagrees with complete accepted search")
        if self.pareto_complete != (complete and bool(self.pareto_front)):
            raise ValueError("Pareto-complete claim disagrees with terminal state")
        if self.infeasible_claimed != infeasible:
            raise ValueError("infeasibility claim disagrees with terminal state")
        if self.provisional_shortlist and self.budget.terminal_state not in {
            "BUDGET_EXHAUSTED_INCOMPLETE",
            "BLOCKED_MANDATORY_CHECK",
        }:
            raise ValueError(
                "provisional shortlist requires an incomplete or blocked search"
            )
        identities = {
            item.candidate_sha256: (item.evaluation_sha256, item.verdict)
            for item in self.direct
        }
        for projection in (*self.cost_ranked, *self.pareto_front):
            if identities.get(projection.candidate_sha256) != (
                projection.evaluation_sha256,
                projection.verdict,
            ):
                raise ValueError(
                    "route projections changed the B1B identity or verdict"
                )
        return self


def build_beam_candidate_search_domain_v1(
    draft: BeamCandidateSearchDomainDraftV1,
    /,
    *,
    criteria: ProjectBeamCriteriaV1,
    catalogue: ProjectBeamCandidateCatalogueV1,
) -> BeamCandidateSearchDomainV1:
    """Validate all candidate bindings and seal their deterministic traversal."""

    criteria = _validated(ProjectBeamCriteriaV1, criteria)
    catalogue = _validated(ProjectBeamCandidateCatalogueV1, catalogue)
    if catalogue.criteria_sha256 != criteria.criteria_sha256:
        raise ValueError("search catalogue criteria identity mismatch")
    if draft.criteria_sha256 != criteria.criteria_sha256:
        raise ValueError("search domain criteria identity mismatch")
    if draft.catalogue_sha256 != catalogue.catalogue_sha256:
        raise ValueError("search domain catalogue identity mismatch")
    ordered: list[BeamCandidateDefinitionV2] = []
    for candidate in draft.candidates:
        candidate = _validated(BeamCandidateDefinitionV2, candidate)
        if candidate.criteria_sha256 != criteria.criteria_sha256:
            raise ValueError("search candidate criteria identity mismatch")
        if candidate.catalogue_sha256 != catalogue.catalogue_sha256:
            raise ValueError("search candidate catalogue identity mismatch")
        ordered.append(candidate)
    ordered.sort(key=lambda item: item.candidate_sha256)
    payload: dict[str, Any] = {
        "schema_version": "beam-candidate-search-domain/v1",
        **draft.model_dump(mode="python", exclude={"candidates"}),
        "candidates": tuple(ordered),
    }
    return BeamCandidateSearchDomainV1.model_validate(
        {**payload, "domain_sha256": _digest(payload)}
    )


def _maximum_utilization(result: BeamCandidateEvaluationResultV2) -> float:
    longitudinal = result.supplied_check["longitudinal"]
    checks = longitudinal["checks"]
    ratios: list[float] = [float(result.supplied_check["shear"]["utilization"])]
    for name in ("tension_area", "compression_area"):
        required = float(checks[name]["required_mm2"])
        provided = float(checks[name]["provided_mm2"])
        ratios.append(required / provided if provided > 0 else float("inf"))
    return max(ratios)


def _projection(
    route: Literal["DIRECT", "COST", "PARETO"],
    rank: int,
    candidate: BeamCandidateDefinitionV2,
    result: BeamCandidateEvaluationResultV2,
) -> BeamCandidateProjectionV1:
    composition = result.composition
    return BeamCandidateProjectionV1(
        route=route,
        rank=rank,
        candidate_id=candidate.candidate_id,
        candidate_sha256=candidate.candidate_sha256,
        evaluation_sha256=result.evaluation_sha256,
        verdict=result.verdict,
        existing_property_id=candidate.existing_property_id,
        steel_mass_kg=composition.total_steel_mass_kg,
        total_cost=composition.total_cost,
        congestion_score=composition.congestion_score,
        maximum_utilization=_maximum_utilization(result),
        bar_mark_count=composition.bar_mark_count,
    )


def _tie_key(
    candidate: BeamCandidateDefinitionV2,
    result: BeamCandidateEvaluationResultV2,
    criteria: ProjectBeamCriteriaV1,
) -> tuple[float | int | str, ...]:
    values: list[float | int | str] = []
    for tie_break in criteria.tie_breaks:
        if tie_break == "LOWER_UTILIZATION":
            values.append(_maximum_utilization(result))
        elif tie_break == "FEWER_BAR_MARKS":
            values.append(result.composition.bar_mark_count)
        else:
            values.append(candidate.existing_property_id)
    values.append(candidate.candidate_sha256)
    return tuple(values)


def _objective_values(
    result: BeamCandidateEvaluationResultV2, criteria: ProjectBeamCriteriaV1
) -> tuple[float, ...]:
    values = {
        "STEEL_MASS": result.composition.total_steel_mass_kg,
        "COST": result.composition.total_cost,
        "CONGESTION": result.composition.congestion_score,
    }
    return tuple(values[name] for name in criteria.objectives)


def _dominates(left: tuple[float, ...], right: tuple[float, ...]) -> bool:
    return all(a <= b for a, b in zip(left, right, strict=True)) and any(
        a < b for a, b in zip(left, right, strict=True)
    )


def _ranked_pairs(
    candidates: tuple[BeamCandidateDefinitionV2, ...],
    evaluations: tuple[BeamCandidateEvaluationResultV2, ...],
    criteria: ProjectBeamCriteriaV1,
) -> list[tuple[BeamCandidateDefinitionV2, BeamCandidateEvaluationResultV2]]:
    accepted = [
        (candidate, result)
        for candidate, result in zip(candidates, evaluations, strict=True)
        if result.verdict == "PASS"
    ]
    return sorted(
        accepted,
        key=lambda item: (
            item[1].composition.total_cost,
            *_tie_key(item[0], item[1], criteria),
        ),
    )


def _pareto_pairs(
    ranked: list[tuple[BeamCandidateDefinitionV2, BeamCandidateEvaluationResultV2]],
    criteria: ProjectBeamCriteriaV1,
) -> list[tuple[BeamCandidateDefinitionV2, BeamCandidateEvaluationResultV2]]:
    front = [
        item
        for item in ranked
        if not any(
            other is not item
            and _dominates(
                _objective_values(other[1], criteria),
                _objective_values(item[1], criteria),
            )
            for other in ranked
        )
    ]
    return sorted(front, key=lambda item: _tie_key(item[0], item[1], criteria))


def search_beam_candidates_v1(
    request: BeamCandidateSearchRequestV1,
    /,
    *,
    criteria: ProjectBeamCriteriaV1,
    catalogue: ProjectBeamCandidateCatalogueV1,
) -> BeamCandidateSearchResultV1:
    """Evaluate a bounded prefix and make only completeness-supported claims."""

    request = _validated(BeamCandidateSearchRequestV1, request)
    criteria = _validated(ProjectBeamCriteriaV1, criteria)
    catalogue = _validated(ProjectBeamCandidateCatalogueV1, catalogue)
    domain = build_beam_candidate_search_domain_v1(
        BeamCandidateSearchDomainDraftV1.model_validate(
            request.domain.model_dump(
                mode="python", exclude={"schema_version", "domain_sha256"}
            )
        ),
        criteria=criteria,
        catalogue=catalogue,
    )
    generated_limit = min(
        request.maximum_generated_candidates,
        criteria.stop_policy.maximum_generated_candidates,
    )
    evaluated_limit = min(
        request.maximum_evaluated_candidates,
        criteria.stop_policy.maximum_evaluated_candidates,
        generated_limit,
    )
    generated = domain.candidates[:generated_limit]
    evaluated_candidates = generated[:evaluated_limit]
    evaluations = tuple(
        evaluate_beam_candidate_v2(candidate, criteria=criteria, catalogue=catalogue)
        for candidate in evaluated_candidates
    )
    enumeration_complete = len(evaluations) == len(domain.candidates)
    has_hold = any(item.verdict == "HOLD" for item in evaluations)
    accepted_count = sum(item.verdict == "PASS" for item in evaluations)
    if not enumeration_complete:
        terminal: SearchTerminalState = "BUDGET_EXHAUSTED_INCOMPLETE"
    elif has_hold:
        terminal = "BLOCKED_MANDATORY_CHECK"
    elif accepted_count == 0:
        terminal = "NO_FEASIBLE_CANDIDATE"
    else:
        terminal = "COMPLETE_ENUMERATION"
    ranked = _ranked_pairs(evaluated_candidates, evaluations, criteria)
    pareto = _pareto_pairs(ranked, criteria)
    allow_shortlist = (
        terminal == "BUDGET_EXHAUSTED_INCOMPLETE"
        and criteria.stop_policy.allow_incomplete_shortlist
    )
    expose_rankings = enumeration_complete or allow_shortlist
    direct = tuple(
        _projection("DIRECT", index, candidate, result)
        for index, (candidate, result) in enumerate(
            zip(evaluated_candidates, evaluations, strict=True), start=1
        )
    )
    cost_ranked = (
        tuple(
            _projection("COST", index, candidate, result)
            for index, (candidate, result) in enumerate(ranked, start=1)
        )
        if expose_rankings
        else ()
    )
    pareto_front = (
        tuple(
            _projection("PARETO", index, candidate, result)
            for index, (candidate, result) in enumerate(pareto, start=1)
        )
        if expose_rankings
        else ()
    )
    budget_payload: dict[str, Any] = {
        "schema_version": "optimization-search-budget/v1",
        "domain_sha256": domain.domain_sha256,
        "traversal_order": domain.traversal_order,
        "permitted_pruning_rules": domain.permitted_pruning_rules,
        "tie_breaks": criteria.tie_breaks,
        "maximum_generated_candidates": generated_limit,
        "maximum_evaluated_candidates": evaluated_limit,
        "generated_count": len(generated),
        "pruned_count": 0,
        "evaluated_count": len(evaluations),
        "accepted_count": accepted_count,
        "ranked_count": len(cost_ranked),
        "terminal_state": terminal,
        "enumeration_complete": enumeration_complete,
        "correctness_proof_sha256": None,
    }
    budget = OptimizationSearchBudgetV1.model_validate(
        {**budget_payload, "budget_sha256": _digest(budget_payload)}
    )
    result_payload: dict[str, Any] = {
        "schema_version": "beam-candidate-search-result/v1",
        "search_id": request.search_id,
        "domain_sha256": domain.domain_sha256,
        "budget": budget,
        "evaluations": evaluations,
        "direct": direct,
        "cost_ranked": cost_ranked,
        "pareto_front": pareto_front,
        "optimality_claimed": terminal == "COMPLETE_ENUMERATION" and bool(ranked),
        "pareto_complete": terminal == "COMPLETE_ENUMERATION" and bool(pareto),
        "infeasible_claimed": terminal == "NO_FEASIBLE_CANDIDATE",
        "provisional_shortlist": (
            terminal in {"BUDGET_EXHAUSTED_INCOMPLETE", "BLOCKED_MANDATORY_CHECK"}
            and bool(cost_ranked)
        ),
    }
    return BeamCandidateSearchResultV1.model_validate(
        {**result_payload, "result_sha256": _digest(result_payload)}
    )
