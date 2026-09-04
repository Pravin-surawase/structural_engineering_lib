# WP08 beam candidate ranking and optimization

WP08 adds deterministic search orchestration to the reusable library without
moving beam design formulas into an optimizer. AO05 ranks supplied candidate
evidence. AO21 first expands a finite physical domain and then applies AO05.
Both operations are pure, portable, and independent of Excel and ETABS.

## Operations

| Catalogue | Semantic ID | Python | .NET |
|---|---|---|---|
| AO05 | `structural.candidate.rank/v1` | `structural_lib.beam_optimization.rank_candidates` | `StructuralEngineering.Optimization.CandidateRankingOperations.Rank` |
| AO21 | `structural.beam.optimize/v1` | `structural_lib.beam_optimization.optimize_beam` | `StructuralEngineering.Optimization.BeamOptimizationOperations.Optimize` |

`CandidateRankingContext` binds one project basis, profile, member, topology,
action revision, design scope, baseline analysis revision, and reference AO17
member result. The reference result freezes the expected leaf set. Each
candidate AO17 result must reproduce that set exactly; an application cannot
submit a shorter list to hide flexure, shear, torsion, serviceability,
anchorage, lap/curtailment, seismic, or arrangement evidence.

`DiscreteCandidateDomain` contains these required axes:

- one or more section choices: width, overall depth, concrete strength, and
  any declared model-impact categories;
- one or more longitudinal choices: top and bottom count, diameter, layers,
  and steel grade;
- one or more transverse choices: link diameter, grade, legs, and spacing;
- an explicit maximum candidate count, baseline section, revision identities,
  source references, and limitations.

AO21 expands the Cartesian product only when it fits the declared bound and
the portable hard ceiling of 100,000 candidates. A
candidate ID includes the domain revision and choice IDs. Its separate physical
definition ID includes only physical values, so two differently labelled
choices that describe the same beam are retained as a reason-coded duplicate
and are evaluated once. Candidate traversal is ascending ordinal candidate ID.

## Evaluation evidence

`CandidateEvaluation` carries immutable result bindings and typed outputs from:

- AO17 member design, with `reinforcement_revision_id` equal to the candidate
  ID;
- AO04 quantities, with `detail_revision_id` equal to the candidate ID;
- AO20 cost when cost is an objective, bound to the exact quantity result;
- a candidate-specific analysis snapshot when coupled reanalysis is required.

Every binding records operation ID, result ID, normalized input ID,
calculation ID, all result states, and a canonical typed-output payload ID.
Changing a typed output while retaining its old binding makes the candidate
incomplete.

A required applicable leaf qualifies only when its execution is completed,
applicability is applicable, engineering is pass, completeness is complete for
scope, freshness is current, and the AO17 qualification agrees. A failed leaf
is an engineering exclusion. Missing, partial, stale, unevaluated, or required
`not_applicable` evidence is incomplete. `not_applicable` qualifies only when
the frozen profile expected that state and its completed evidence reports
engineering `not_evaluated`.

## Analysis coupling

Each candidate retains one coupling class:

| Class | Trigger |
|---|---|
| `fixed_action` | actual bars, detailing, bar paths, BBS, rates/cost, or report options |
| `reanalysis_required` | section property, material/stiffness, release, offset, self-weight/mass, load, combination, support, mesh, or analysis-setting change |
| `unresolved` | unknown model impact or insufficient mapping |

In `fixed_actions` mode, every evaluation uses the baseline analysis revision.
A section-changing candidate may be ranked, but the output scope remains
`finite_domain_fixed_actions_common_force_assumption`.

In `coupled_reanalysis` mode, a candidate with model-changing inputs needs a
versioned policy that requires an owned model copy and fresh candidate-specific
analysis evidence. The evidence binds the baseline revision, candidate
physical definition, new analysis revision, snapshot result, payload,
completion, and freshness. WP08 does not mutate ETABS; a later host supplies
that evidence.

## Objectives and claims

An objective profile supplies an ordered, unique list chosen from cost, steel
mass, section depth, embodied carbon, concrete volume, formwork area,
congestion, and utilization reserve. Cost, steel, concrete, and formwork values
come from the bound WP07 outputs. Carbon and congestion need their own value and
basis identity. Tie breakers are ordered explicitly; candidate ID is always
appended as the final deterministic tie.

`evaluation_budget` counts candidate evaluations rather than elapsed time.
Supplied evaluations must be the canonical prefix of unique physical,
resolved-coupling candidates. The caller records whether the prefix ended by
completion, budget, or cancellation.

| Terminal state | Meaning | Allowed claim |
|---|---|---|
| `complete_enumeration` | every unique candidate has complete evidence and at least one passes | selected candidate and finite-domain optimum |
| `no_feasible_candidate` | every unique candidate has complete evidence and all fail engineering | finite-domain infeasibility |
| `budget_exhausted_incomplete` | evaluation budget stopped a proper prefix | best evaluated candidate only |
| `cancelled_incomplete` | caller cancelled a prefix | best evaluated candidate only |
| `evidence_incomplete` | any required evidence or coupling classification is unresolved | provisional complete-evidence candidates only |

Every generated candidate appears in the domain. Every evaluated, failed,
incomplete, unevaluated, or physical-duplicate candidate appears in the
evaluation/exclusion ledger with identities and reason codes. Partial search
never sets `selected_candidate_id`, `optimality_claimed`, or
`infeasible_claimed`.

The exact wire records and cross-language fixtures are in
`contracts/structural-engineering/schemas/wp08.schema.json` and
`contracts/structural-engineering/conformance/wp08-vectors.json`.
