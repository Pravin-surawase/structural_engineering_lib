"""Portable WP08 candidate-domain, evaluation, and ranking records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from structural_lib.beam.member import MemberDesignOutput
from structural_lib.beam.semantics import (
    ApplicabilityState,
    CompletenessState,
    EngineeringState,
    ExecutionState,
    FreshnessState,
)
from structural_lib.construction.contracts import (
    ConstructionCostOutput,
    ConstructionQuantityOutput,
)


class AnalysisMode(StrEnum):
    FIXED_ACTIONS = "fixed_actions"
    COUPLED_REANALYSIS = "coupled_reanalysis"


class CandidateObjectiveKind(StrEnum):
    COST = "cost"
    STEEL_MASS = "steel_mass"
    SECTION_DEPTH = "section_depth"
    CARBON = "carbon"
    CONCRETE_VOLUME = "concrete_volume"
    FORMWORK_AREA = "formwork_area"
    CONGESTION = "congestion"
    UTILIZATION_RESERVE = "utilization_reserve"


class CandidateTieBreaker(StrEnum):
    LOWER_UTILIZATION = "lower_utilization"
    FEWER_BAR_MARKS = "fewer_bar_marks"
    LOWER_SECTION_DEPTH = "lower_section_depth"
    CANDIDATE_ID = "candidate_id"


class CandidateChangeCategory(StrEnum):
    ACTUAL_BARS = "actual_bars"
    DETAILING = "detailing"
    BAR_PATHS = "bar_paths"
    BBS = "bbs"
    RATES_COST = "rates_cost"
    REPORT_OPTIONS = "report_options"
    SECTION_DIMENSIONS_PROPERTY = "section_dimensions_property"
    MATERIAL_STIFFNESS = "material_stiffness"
    RELEASES = "releases"
    OFFSETS = "offsets"
    MASS_SELF_WEIGHT = "mass_self_weight"
    APPLIED_LOAD = "applied_load"
    LOAD_CASE_COMBINATION = "load_case_combination"
    SUPPORT_RESTRAINT = "support_restraint"
    MESHING = "meshing"
    ANALYSIS_SETTINGS = "analysis_settings"
    UNKNOWN = "unknown"


class CandidateCouplingClass(StrEnum):
    FIXED_ACTION = "fixed_action"
    REANALYSIS_REQUIRED = "reanalysis_required"
    UNRESOLVED = "unresolved"


class SearchStopReason(StrEnum):
    COMPLETED = "completed"
    EVALUATION_BUDGET_REACHED = "evaluation_budget_reached"
    CANCELLED = "cancelled"


class SearchTerminalState(StrEnum):
    COMPLETE_ENUMERATION = "complete_enumeration"
    BUDGET_EXHAUSTED_INCOMPLETE = "budget_exhausted_incomplete"
    CANCELLED_INCOMPLETE = "cancelled_incomplete"
    EVIDENCE_INCOMPLETE = "evidence_incomplete"
    NO_FEASIBLE_CANDIDATE = "no_feasible_candidate"


class CandidateDisposition(StrEnum):
    FEASIBLE = "feasible"
    ENGINEERING_FAIL = "engineering_fail"
    INCOMPLETE = "incomplete"
    NOT_EVALUATED = "not_evaluated"
    DUPLICATE_PHYSICAL_DEFINITION = "duplicate_physical_definition"


@dataclass(frozen=True)
class CandidateResultBinding:
    """Immutable typed-output evidence without an optimization-to-reporting dependency."""

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
class CandidateObjectiveProfile:
    profile_id: str
    revision_id: str
    objectives: tuple[CandidateObjectiveKind, ...]
    tie_breakers: tuple[CandidateTieBreaker, ...]


@dataclass(frozen=True)
class SectionCandidateChoice:
    choice_id: str
    width_mm: float
    overall_depth_mm: float
    concrete_strength_n_per_mm2: float
    additional_change_categories: tuple[CandidateChangeCategory, ...] = ()


@dataclass(frozen=True)
class LongitudinalCandidateChoice:
    choice_id: str
    top_bar_count: int
    top_bar_diameter_mm: float
    top_layer_count: int
    bottom_bar_count: int
    bottom_bar_diameter_mm: float
    bottom_layer_count: int
    steel_grade_n_per_mm2: float


@dataclass(frozen=True)
class TransverseCandidateChoice:
    choice_id: str
    link_diameter_mm: float
    steel_grade_n_per_mm2: float
    legs: int
    spacing_mm: float


@dataclass(frozen=True)
class DiscreteCandidateDomain:
    domain_id: str
    revision_id: str
    project_basis_id: str
    profile_revision_id: str
    member_id: str
    topology_revision_id: str
    action_revision_id: str
    design_scope_revision_id: str
    baseline_analysis_revision_id: str
    baseline_section_choice_id: str
    section_choices: tuple[SectionCandidateChoice, ...]
    longitudinal_choices: tuple[LongitudinalCandidateChoice, ...]
    transverse_choices: tuple[TransverseCandidateChoice, ...]
    maximum_domain_candidates: int
    source_references: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class CandidatePhysicalDefinition:
    width_mm: float
    overall_depth_mm: float
    concrete_strength_n_per_mm2: float
    top_bar_count: int
    top_bar_diameter_mm: float
    top_layer_count: int
    bottom_bar_count: int
    bottom_bar_diameter_mm: float
    bottom_layer_count: int
    longitudinal_steel_grade_n_per_mm2: float
    link_diameter_mm: float
    link_steel_grade_n_per_mm2: float
    link_legs: int
    link_spacing_mm: float


@dataclass(frozen=True)
class BeamCandidateDefinition:
    candidate_id: str
    physical_definition_id: str
    domain_id: str
    domain_revision_id: str
    section: SectionCandidateChoice
    longitudinal: LongitudinalCandidateChoice
    transverse: TransverseCandidateChoice
    physical: CandidatePhysicalDefinition
    change_categories: tuple[CandidateChangeCategory, ...]
    coupling_class: CandidateCouplingClass


@dataclass(frozen=True)
class CandidateDomainOutput:
    domain_id: str
    domain_revision_id: str
    domain_semantic_id: str
    project_basis_id: str
    profile_revision_id: str
    member_id: str
    topology_revision_id: str
    action_revision_id: str
    design_scope_revision_id: str
    baseline_analysis_revision_id: str
    baseline_section_choice_id: str
    traversal_order: str
    candidates: tuple[BeamCandidateDefinition, ...]
    generated_count: int


@dataclass(frozen=True)
class CandidateRankingContext:
    project_basis_id: str
    profile_revision_id: str
    member_id: str
    topology_revision_id: str
    action_revision_id: str
    design_scope_revision_id: str
    baseline_analysis_revision_id: str
    reference_member_result_id: str
    reference_member_binding: CandidateResultBinding
    reference_member: MemberDesignOutput


@dataclass(frozen=True)
class ReanalysisPolicy:
    policy_id: str
    revision_id: str
    owned_copy_required: bool
    source_reference: str


@dataclass(frozen=True)
class CandidateReanalysisEvidence:
    candidate_id: str
    candidate_definition_id: str
    baseline_analysis_revision_id: str
    candidate_analysis_revision_id: str
    snapshot_result_id: str
    snapshot_output_payload_id: str
    execution_completed: bool
    freshness_current: bool


@dataclass(frozen=True)
class CandidateEvaluation:
    candidate_id: str
    analysis_revision_id: str
    member_binding: CandidateResultBinding
    member_result: MemberDesignOutput
    quantity_binding: CandidateResultBinding
    quantities: ConstructionQuantityOutput
    cost_binding: CandidateResultBinding | None = None
    cost: ConstructionCostOutput | None = None
    embodied_carbon_kg_co2e: float | None = None
    carbon_basis_id: str | None = None
    congestion_score: float | None = None
    congestion_basis_id: str | None = None
    reanalysis_evidence: CandidateReanalysisEvidence | None = None


@dataclass(frozen=True)
class ObjectiveMetric:
    kind: CandidateObjectiveKind
    value: float
    unit: str
    source_identity: str


@dataclass(frozen=True)
class RankedCandidate:
    rank: int
    candidate_id: str
    physical_definition_id: str
    coupling_class: CandidateCouplingClass
    analysis_revision_id: str
    member_result_id: str
    quantity_result_id: str
    cost_result_id: str | None
    objective_metrics: tuple[ObjectiveMetric, ...]


@dataclass(frozen=True)
class CandidateExclusion:
    candidate_id: str
    disposition: CandidateDisposition
    reason_codes: tuple[str, ...]
    member_result_id: str | None


@dataclass(frozen=True)
class CandidateEvaluationRecord:
    candidate_id: str
    physical_definition_id: str
    disposition: CandidateDisposition
    analysis_revision_id: str | None
    member_binding: CandidateResultBinding | None
    quantity_binding: CandidateResultBinding | None
    cost_binding: CandidateResultBinding | None
    objective_metrics: tuple[ObjectiveMetric, ...]
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class SearchPerformance:
    domain_candidate_count: int
    unique_physical_candidate_count: int
    duplicate_physical_candidate_count: int
    evaluation_budget: int
    evaluated_count: int
    feasible_count: int
    engineering_fail_count: int
    incomplete_count: int


@dataclass(frozen=True)
class CandidateRankingRequest:
    ranking_id: str
    context: CandidateRankingContext
    domain: CandidateDomainOutput
    objective_profile: CandidateObjectiveProfile
    analysis_mode: AnalysisMode
    reanalysis_policy: ReanalysisPolicy | None
    evaluation_budget: int
    stop_reason: SearchStopReason
    evaluations: tuple[CandidateEvaluation, ...]


@dataclass(frozen=True)
class CandidateRankingOutput:
    ranking_id: str
    domain_id: str
    domain_semantic_id: str
    expected_leaf_set_id: str
    analysis_mode: AnalysisMode
    baseline_analysis_revision_id: str
    objective_profile_id: str
    objective_profile_revision_id: str
    effective_tie_breakers: tuple[CandidateTieBreaker, ...]
    evaluation_records: tuple[CandidateEvaluationRecord, ...]
    ranked_candidates: tuple[RankedCandidate, ...]
    exclusions: tuple[CandidateExclusion, ...]
    performance: SearchPerformance
    terminal_state: SearchTerminalState
    enumeration_complete: bool
    best_evaluated_candidate_id: str | None
    selected_candidate_id: str | None
    optimality_claimed: bool
    infeasible_claimed: bool
    provisional_shortlist: bool
    optimality_scope: str


@dataclass(frozen=True)
class BeamOptimizationRequest:
    search_id: str
    context: CandidateRankingContext
    domain: DiscreteCandidateDomain
    objective_profile: CandidateObjectiveProfile
    analysis_mode: AnalysisMode
    reanalysis_policy: ReanalysisPolicy | None
    evaluation_budget: int
    stop_reason: SearchStopReason
    evaluations: tuple[CandidateEvaluation, ...]


@dataclass(frozen=True)
class BeamOptimizationOutput:
    search_id: str
    domain: CandidateDomainOutput
    ranking: CandidateRankingOutput


__all__ = [
    "AnalysisMode",
    "BeamCandidateDefinition",
    "BeamOptimizationOutput",
    "BeamOptimizationRequest",
    "CandidateChangeCategory",
    "CandidateCouplingClass",
    "CandidateDisposition",
    "CandidateDomainOutput",
    "CandidateEvaluation",
    "CandidateEvaluationRecord",
    "CandidateObjectiveKind",
    "CandidateObjectiveProfile",
    "CandidatePhysicalDefinition",
    "CandidateRankingContext",
    "CandidateRankingOutput",
    "CandidateRankingRequest",
    "CandidateResultBinding",
    "CandidateReanalysisEvidence",
    "CandidateTieBreaker",
    "DiscreteCandidateDomain",
    "LongitudinalCandidateChoice",
    "ObjectiveMetric",
    "RankedCandidate",
    "ReanalysisPolicy",
    "SearchPerformance",
    "SearchStopReason",
    "SearchTerminalState",
    "SectionCandidateChoice",
    "TransverseCandidateChoice",
]
