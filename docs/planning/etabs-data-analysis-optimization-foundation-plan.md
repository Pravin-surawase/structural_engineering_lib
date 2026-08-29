---
owner: Main Agent
status: draft
last_updated: 2026-08-29
doc_type: spec
complexity: advanced
tags: [etabs, beams, data-contracts, frame-analysis, optimization, provenance]
---

# ETABS Data, Beam Analysis, and Optimization Foundation

## Purpose and authority

This document converts the recent W1/W2 ETABS work into a practical public-
library foundation for beam audit, local candidate screening, and later
ETABS-verified optimization. It is the current planning authority for that
foundation only. W2C is integrated through PR #898 at merge
`f1873e7b...`; the owner has authorized the W3 start after this maintenance
closeout. This document does not itself authorize ETABS analysis or design,
mutate an ETABS model, or establish engineering/professional approval.

Use the companion
[ETABS, Excel, Professional Attestation, and Surface Retirement Audit](etabs-excel-professional-surface-audit.md)
for professional-signature evidence, Excel review architecture, public API
retirement, React freeze/pruning, and repository compaction decisions.

The execution principle is:

```text
ETABS supplies exact model and global-analysis evidence
                         ->
the public library supplies typed data, beam checks, local screening, and
candidate ranking
                         ->
ETABS reanalyses only a bounded shortlist
                         ->
the public library verifies the fresh actions and records the comparison
```

The objective is fewer ETABS trips without pretending that a local beam model
has full 3D ETABS parity.

## Exact audit boundary

The original audit was performed on 2026-08-29 from:

- local branch `codex/etabs-analysis-foundation-audit`;
- base and current `origin/main` `ee50aaa3cad619b41c6153f5f7970553ef65248c`;
- clean tree before documentation work;
- no current pull request for the planning branch; and
- a successful `git fetch origin` immediately before comparison, after which
  local `main` and the local `origin/main` ref both resolved to `ee50aaa3`.

The W3-readiness maintenance refreshed that boundary after a new fetch:

- PR #898 merged the exact reviewed W2C candidate `57f53d48...` as
  `f1873e7b...`, with candidate and merge tree both `bb20ba0c...`;
- direct service, REST, and all seven saved Excel tables reconcile baseline
  `d4c28586...`, 3,502 stations, and 3,626,096 canonical JSON bytes;
- model hash/size/mtime, locked state, units, and the active approved
  combination remained exact; and
- no ETABS analysis/design/save/write-back occurred, while independent frame
  analysis remains `HELD_NOT_SUPPORTED`.

The earlier blocked retry and six-table JSON-write evidence remain retained as
historical fail-closed records. They no longer describe the current W2 state.

The required repository session start was also blocked by the preserved
unmatched `EXCEL-ETABS-PYTHON-BRIDGE-PILOT` checkpoint. The audit did not close,
rewrite, or borrow that historical timing state.

## Current capability truth

### W2 beam baseline: useful and bounded

`ETABSBeamBaselineV1` already provides a strong read-only foundation:

- exact authorized model-file identity and before/after evidence;
- ETABS/library/runtime identity and getter-matrix digest;
- lock and temporary-unit restoration proof;
- story, point, frame, rectangular-section, local-axis, and endpoint topology;
- explicit requested result-selection evidence;
- every retained force-station row with member, source row, object/element
  stations, step identity, and signed `P`, `V2`, `V3`, `T`, `M2`, and `M3`;
- complete accepted/excluded/blocked dispositions; and
- deterministic canonical bytes and a baseline SHA-256.

Blocked inventory, topology, or result-selection conditions are resolved
before `FrameForce`. No partial accepted baseline is returned. These controls
should be extended by linked snapshots rather than weakened or silently
reinterpreted.

### W2 gaps that matter to later work

The current baseline inventories case and combination names only to validate
explicitly requested selections. It does not expose a complete typed catalogue
of:

- load patterns and self-weight multipliers;
- load-case types and relevant case parameters;
- case analysis status for the complete catalogue;
- response-combination type;
- ordered combination constituents and scale factors;
- nested combination relationships;
- design-combination ownership or purpose; or
- the exact definition digest used by a future local or ETABS reanalysis.

It also retains endpoint topology but does not yet interpret a beam line,
support condition, span continuity, releases, offsets, stiffness modifiers, or
slab participation. Those are engineering-model inputs, not safe inferences
from frame labels.

### Beam design and optimization truth

The canonical beam service is valuable but currently consumes one non-negative
factored `Mu/Vu/Tu` action triple. Its serviceability field is deliberately
held until strict typed serviceability models are frozen. A short provenance
string is not enough to bind a design decision to an ETABS baseline, member,
selection, station, step, and envelope rule.

The maintained single-objective cost optimizer:

- searches rectangular singly reinforced sections;
- evaluates flexure and shear for fixed caller-supplied actions;
- uses an explicit stirrup area for shear feasibility; and
- reports longitudinal-steel/concrete/formwork cost while explicitly excluding
  stirrup mass and cost.

It does not evaluate torsion, serviceability, continuity, stiffness
redistribution, model provenance, beam families, or whole-model constraints.
Its result is therefore a fixed-action screening result.

The current Pareto optimizer has an outcome-changing defect: it accepts
`vu_kn` but its candidate path performs flexure only and marks candidates safe
without a shear check. It must remain held from engineering or ETABS candidate
selection until shear participates in feasibility and reported utilization.

The rebar optimizer is a useful deterministic bar-arrangement helper for a
known required steel area. It is not a frame solver, action generator,
torsion/shear design, or complete constructability optimizer.

### Independent analysis truth

There is no accepted direct-stiffness or continuous-beam solver in the current
library. The gravity workflow is solver-free, and the serviceability module
explicitly limits its continuous-beam approximation. The older Project BHEEM
masterplan contains a broad future FEM vision; it is not current capability,
acceptance evidence, or the execution plan for this bounded programme.

## Architecture decision

Use four explicit layers and never pass vendor-shaped COM arrays into the
engineering API:

```text
ETABS adapter and evidence
  - attach/read/verify, normalize units, retain vendor identities
                     |
                     v
Versioned public data contracts
  - immutable model context, definitions, demands, scenarios, provenance
                     |
                     v
Pure library analysis and design
  - beam-line surrogate, beam checks, serviceability, constructability
                     |
                     v
Optimization and verification orchestration
  - propose, rank, compare, shortlist; ETABS mutation remains a guarded adapter
```

ETABS remains the final global-analysis authority. The local solver is a
surrogate for gravity-dominated beam-line screening and sensitivity studies.

## Data foundation

### Snapshot set

Do not create one unbounded “all ETABS data” object. Use immutable, hash-linked
snapshots with explicit scope:

| Snapshot | Required content | Normal size/use |
|---|---|---|
| `ETABSModelContextV1` | File/hash/version, lock, units, runtime/getter identity, analysis state, active output selections | Small preflight identity |
| `ETABSModelDefinitionSnapshotV1` | Stories, points, frames, sections/material labels, axes, connectivity, assignments, releases, offsets, modifiers, supports and explicitly captured area/diaphragm context | Broad model semantics |
| `ETABSResultCatalogueV1` | Load patterns, cases, case status, combinations, ordered/nested components, scale factors, output-selection state and catalogue digest | Definition authority |
| Existing `ETABSBeamBaselineV1` | Complete bounded beam topology and same-row signed force stations for requested selections | Heavy immutable W2 evidence |
| `ETABSDisplacementSnapshotV1` | Joint/member displacement rows for explicit selections, with node, step, units, source row and catalogue/baseline identity | Optional calibration evidence; new getter scope |
| `BeamDemandSnapshotV1` | Compact member/scenario demand records with references to exact baseline station IDs | W3 design/audit input |
| `ETABSReanalysisEvidenceV1` | Pre/post model identity, approved change plan, run status, fresh result identity, comparison and abort/revert evidence | Future W6 only |

The existing exported-file `ETABSCanonicalSnapshotV1` remains a useful
export-first path, but its old `ProjectBeamDesignInputV1` projection must not be
treated as the live W3 successor. It reduces forces to fixed `mu_knm/vu_kn` and
uses generic metadata; W3 should instead link to exact demand scenarios and the
strict current beam contract.

### Required model fields

Fields are required when their absence would change analysis, design, or the
ability to reproduce a decision:

- saved model path/name and SHA-256, ETABS version, library/adapter identity;
- model lock, present/database units, analysis completion/freshness evidence;
- stories, coordinates, stable object names, labels and story assignments;
- frame connectivity, local axes, end releases, offsets/insertion points;
- assigned section, material property, auto-select state and stiffness/mass/
  weight modifiers;
- support/restraint/spring data used by the bounded beam-line model;
- load-pattern type and self-weight multiplier;
- load-case type, relevant parameters and analysis status;
- combination type, ordered constituents, scale factors and nested references;
- exact cases/combinations selected for output;
- member, station, output case, step type/number and signed six-component
  action row; and
- design preferences/overwrites only when a comparison claims to reproduce
  ETABS design behavior.

Concrete grade, reinforcement grade, cover, bar sizes, detailing standard,
cracked-stiffness basis, support interpretation, slab participation and seismic
applicability must remain explicit caller-owned engineering inputs unless an
exact typed ETABS getter contract proves them.

### Optional-field policy

Optional must mean one of:

1. a read-only filter that narrows an otherwise defined query;
2. one of several explicit alternative representations;
3. an opt-in module whose omission visibly holds that check; or
4. an expected-state guard used only for a future mutation request.

Missing information must be represented as typed `NOT_AVAILABLE`,
`NOT_APPLICABLE`, `NOT_REQUESTED`, or `BLOCKED_MISSING_INPUT` evidence. Do not
substitute hidden engineering defaults and do not copy COM by-reference output
arrays into the public API.

### Result volume and access

Keep the W2 capacity limits and fail on overflow rather than truncating. Build
member/scenario envelopes lazily from the immutable station inventory. Normal
W3 results should return compact governing references; raw stations should be
available through an explicit read-only paged/detail query. This avoids a
second unbounded transport while retaining lossless evidence.

## Demand and envelope foundation

The current live pilot independently chooses absolute maxima for `V2`, `T`,
and `M3`; those extrema can come from different rows. That is acceptable only
as explicitly labelled independent-component screening. It must not be called
a concurrent load state.

Add transport-neutral public contracts:

### `BeamActionRowV1`

Required fields:

- source snapshot and baseline digests;
- member and station identities;
- result selection, step type and step number;
- object/element station and source row index;
- signed `P`, `V2`, `V3`, `T`, `M2`, `M3`; and
- unit basis.

### `BeamDemandScenarioV1`

Required fields:

- scenario ID and purpose (`STRENGTH`, `SERVICE`, or `COMPARISON`);
- included selection IDs and definition-catalogue digest;
- station domain and component policy;
- concurrency rule;
- governing row references; and
- explicit held components/checks.

### `BeamDemandEnvelopeRuleV1`

It must state whether the result is:

- one exact same-row concurrent action;
- signed positive/negative extrema per component;
- an independent-component absolute envelope; or
- a caller-defined code/design envelope.

No function may label actions concurrent unless they originate from the same
retained result row.

### Pure functions

- `build_etabs_result_catalogue_v1(...)`
- `verify_etabs_result_catalogue_hash_v1(...)`
- `derive_beam_demand_scenarios_v1(baseline, catalogue, rules)`
- `build_beam_audit_inputs_v1(demands, design_basis)`
- `evaluate_beam_audit_v1(inputs)`

The ETABS-named function owns translation/provenance. Demand derivation and
beam evaluation remain adapter-neutral and reusable by CSV, Excel, SAFE, or
future analysis sources.

## Local beam-line surrogate

### Bounded scope

Implement a public, transport-neutral, 2D linear-elastic Euler-Bernoulli
continuous-beam solver using the direct-stiffness method. Its first accepted
scope is:

- one horizontal beam line with one to five prismatic spans;
- vertical translation and nodal rotation degrees of freedom;
- explicit simple/fixed/rotational-spring support conditions;
- bounded end releases and rigid/end offsets only after their contract freezes;
- uniform and point loads;
- explicit factored and service load scenarios;
- section `E`, `I`, density/self-weight basis and stiffness modifier;
- nodal displacements/rotations, reactions, member-end actions, station
  diagrams and equilibrium residuals; and
- mandatory `SURROGATE_ONLY` capability status.

Do not include 3D framing, diaphragms, shell/slab elements, lateral/seismic or
wind analysis, modal response, P-Delta, material nonlinearity, staged
construction, soil-structure interaction, or ETABS-parity claims.

### Proposed public contracts and functions

- `BeamLineNodeV1`
- `BeamLineSpanV1`
- `BeamLineSupportV1`
- `BeamLineLoadCaseV1`
- `BeamLineCombinationV1`
- `BeamLineScenarioV1`
- `BeamLineAnalysisRequestV1`
- `BeamLineAnalysisResultV1`
- `solve_beam_line_linear_v1(request)`
- `compare_beam_line_to_reference_v1(local, reference, policy)`

Torsion cannot be derived by the first 2D solver. It must be supplied from an
ETABS demand scenario or reported as `HELD_NOT_DERIVED`.

### Scenario and uncertainty model

Use named deterministic scenarios rather than an unsupported reliability
claim:

- nominal extracted geometry/stiffness/load basis;
- lower and upper effective `EI`;
- lower and upper support rotational stiffness;
- patterned service/live loads;
- explicit slab-participation alternatives where supplied; and
- any engineer-approved conservative scenario.

Produce the best candidate per scenario, a Pareto shortlist, and one robust
candidate that passes every mandatory scenario. Do not select only the optimum
under an optimistic assumption.

### Calibration boundary

`BeamLineCalibrationV1` must bind:

- ETABS model/baseline/catalogue digests;
- exact member/span/station/result selection mapping;
- compared action/displacement components;
- predeclared absolute and relative tolerances;
- local assumptions; and
- `CALIBRATED`, `OUT_OF_BAND`, or `NOT_COMPARABLE` status.

Calibration is model/version specific and invalidates when geometry, loads,
combination definitions, releases, modifiers, supports, analysis settings, or
the ETABS file digest changes. It improves local screening; it does not promote
the local solver to final authority.

## Optimization and ETABS verification loop

The target loop is:

```text
accepted baseline and definitions
  -> group constructible beam families
  -> generate bounded section/rebar candidates
  -> solve local factored and service scenarios
  -> run canonical strength/serviceability/constructability checks
  -> reject held or unsafe candidates
  -> rank a small robust shortlist
  -> apply one candidate plan to an authorized copied ETABS model
  -> run only approved analysis cases
  -> extract a fresh hash-bound demand snapshot
  -> redesign and compare all affected constraints
  -> accept, revise, or reject with a finite stopping rule
```

The original model remains untouched. Every future ETABS candidate starts from
the same approved baseline copy, not from cumulative unverified mutations.

Future public orchestration types:

- `BeamFamilyDefinitionV1`
- `CandidateSectionPlanV1`
- `CandidateScreeningResultV1`
- `CandidateShortlistV1`
- `ETABSReanalysisPlanV1`
- `ETABSReanalysisEvidenceV1`
- `AnalysisIterationComparisonV1`

`ETABSReanalysisPlanV1` must include an allowlisted copy, baseline hash,
expected old assignments, proposed new definitions/assignments, approved cases,
combination/catalogue digest, backup identity, unit/lock policy, save target,
abort policy and finite evaluation budget. This is a future separately reviewed
mutation contract, not part of the initial solver.

## Dependency-ordered execution packets

### P0 — Complete: W2C integrated

PR #898 integrated the exact reviewed candidate after independent Mac review,
full local verification, and green Python/FastAPI/Excel/documentation hosted
checks. Typed literal cells, seven-table rollback, exact readback/rejoin/hash,
and installed model preservation all passed. This closes the W2 predecessor as
software workflow evidence only; it does not change the solver, mutation, or
professional-review holds.

### P1 — Pareto optimizer truth repair

- Make shear participate in feasibility and reported utilization, or reject
  nonzero `vu_kn` until that is implemented.
- Validate objective names strictly rather than silently treating unknown
  objectives as cost.
- Label remaining torsion, serviceability, stirrup-cost and fixed-action holds.

Exit: a high-shear regression produces no shear-unsafe Pareto recommendation;
every reported safe candidate states exactly which checks ran and which remain
held.

### P2 — Result catalogue and demand contracts

- Freeze the typed load pattern/case/combination catalogue and hash.
- Expand the getter matrix only for approved exact operations.
- Add same-row action, scenario, envelope and governing-reference contracts.
- Add a separately versioned displacement snapshot and exact node/selection/
  step mapping before any later packet compares displacements; an action-only
  packet may leave it explicitly `NOT_REQUESTED`.
- Link every W3 input to W2 baseline and catalogue digests.

Exit: unapproved selections, missing constituents, hash mismatch, absent
station, cross-row concurrency, or missing design basis fail closed.

### P3 — Beam audit evaluator

- Convert accepted demand scenarios plus explicit materials/detailing basis to
  strict beam inputs.
- Freeze typed strength and service scenario results.
- Keep torsion and serviceability visibly held until their required inputs and
  strict contracts exist.

Exit: every flexure/shear/torsion/serviceability outcome cites its exact demand
scenario, governing station row, assumptions and clause evidence.

### P4 — Independent beam-line kernel

- Freeze model/load/result types.
- Implement deterministic stiffness assembly and boundary handling.
- Support one to five spans with UDL/point loads.
- Add equilibrium, closed-form, symmetry and continuous-beam benchmarks.

Exit criteria:

- simply supported UDL and point-load cases agree with closed form under a
  frozen absolute-plus-relative tolerance per dimensional quantity;
- deterministic equilibrium residual norm is at most `1e-8` of the nonzero
  applied-load norm, with a separately frozen absolute floor;
- symmetric two-span cases satisfy a frozen absolute-plus-relative comparison;
- singular/unstable systems fail closed with a typed reason; and
- result serialization and candidate ordering are deterministic.

Every numerical benchmark must declare units, a nonzero characteristic
reference scale, absolute tolerance, and relative tolerance. Use
`abs(error) <= atol + rtol * reference_scale`; never divide by an expected
quantity that may legitimately be zero.

### P5 — Scenario screening and family optimization

- Couple candidate `E/I`, self-weight and scenario loads to the local solver.
- Run strength, typed service and constructability checks.
- Group beams into engineer-editable constructible families.
- Return robust and Pareto shortlists with held-check ledgers.

Target benchmark, to be measured rather than assumed: 100 section candidates
over five spans and five scenarios complete locally in two seconds on the
recorded supported runtime. Performance failure changes implementation choice,
not engineering tolerances.

### P6 — ETABS calibration adapter

- Map an accepted W2/W3 baseline to comparison stations.
- Compare local actions under frozen tolerances. Compare displacements only
  when a hash-linked accepted `ETABSDisplacementSnapshotV1` exists; otherwise
  return an explicit action-only calibration status.
- Store model-specific calibration and invalidation evidence.

Exit: missing station/scenario data is `NOT_COMPARABLE`; no candidate becomes
`CALIBRATED` unless every declared comparison passes.

### P7 — Controlled copied-model reanalysis

- Freeze the mutation/reanalysis contract before implementing setters.
- Apply one candidate plan to an allowlisted recoverable copy.
- Run approved analysis cases and capture fresh results.
- Compare beams plus affected columns, reactions, drifts and other frozen
  whole-model constraints.

Exit: the exact copy, changes, analysis run, result snapshot, restoration and
comparison reconcile. Any unexpected dialog, stale result, model drift, failed
analysis, out-of-scope affected member or restore failure rejects the candidate.

### P8 — Bounded iterative controller

- Use a finite candidate budget and deterministic stopping rules.
- Cache by baseline/scenario/candidate digest.
- Start every ETABS candidate from the clean approved baseline.
- Independently rerun the selected final candidate.

Exit: convergence or budget exhaustion is explicit; no infinite overnight loop
or silent “best available” engineering acceptance is permitted.

## Work sizing

These are planning ranges for one experienced developer, not delivery promises:

| Foundation | Indicative effort | Dominant risk |
|---|---:|---|
| P1 optimizer truth repair | 2–5 focused days | Compatibility and result-schema truth |
| P2 result catalogue/demand contracts | 2–4 weeks | Exact ETABS definitions and provenance |
| P3 beam audit evaluator | 2–4 weeks | Typed serviceability and governing-action rules |
| P4 validated beam-line kernel | 4–8 weeks | Boundary/load equivalence and benchmarks |
| P5 scenario/family screening | 3–6 weeks | Constructability and deterministic ranking |
| P6 calibration adapter | 2–4 weeks after accepted W2/W3 data | Exact member/station/scenario mapping |
| P7 controlled ETABS reanalysis | 4–8 weeks plus installed Windows evidence | Safe mutation, analysis, restoration and global comparisons |

A dependable public beam-line screening programme is therefore a multi-packet,
roughly three-to-six-month effort. A general 2D/3D building FEM engine is a
separate much larger programme and is not required to reduce ETABS trips.

## Expected time saving

The target operating pattern is:

1. one baseline ETABS extraction;
2. many local candidate and assumption runs;
3. a bounded ETABS shortlist verification;
4. at most a small number of correction cycles; and
5. one independent final ETABS run.

No trip-reduction percentage or force-accuracy percentage may be claimed until
P6 benchmarks representative models. The main success metrics are fewer ETABS
analysis cycles, zero unsafe screened recommendations, explicit held checks,
stable candidate ranking, and improving model-specific prediction error.

## Verification matrix

| Boundary | Required evidence |
|---|---|
| Data identity | Canonical hashes, exact units, source/runtime identity, no partial accepted snapshot |
| Case/combo semantics | Complete typed inventory, constituents/factors, nested references, finished/selected status |
| Demand concurrency | Exact same-row references; independent extrema labelled as such |
| Solver math | Closed-form, equilibrium, symmetry, singularity and deterministic serialization tests |
| Beam checks | Flexure, shear, torsion/service holds, service scenario and detailing evidence |
| Optimization | Feasibility before ranking, deterministic objectives, held-check ledger, bounded budget |
| Calibration | Predeclared tolerances, exact reference mapping, invalidation on model drift |
| ETABS iteration | Authorized copy, expected-state guards, analysis success, fresh results, restore/save proof |
| Whole-model review | Affected beams, columns, reactions, drifts and other explicitly governed metrics |

## Stop conditions

Stop and request direction when:

- the exact integrated W2 predecessor or its evidence identities no longer
  match `f1873e7b...` / `57f53d48...`;
- the authorized model file, hash, ETABS version or result definitions change;
- analysis results are stale, incomplete, inactive or not traceable;
- a required getter/setter is outside the reviewed matrix;
- a local scenario requires an unsupported 3D/nonlinear behavior;
- an optimizer cannot prove all declared feasibility checks;
- a future ETABS mutation cannot guarantee an allowlisted copy and recovery;
- an unexpected ETABS/license/abnormal-condition dialog appears; or
- software evidence is being represented as engineering or construction
  approval.

## Immediate next decision

Start W3 with P2 as the bounded W3A contract packet: freeze the typed load
pattern/case/combination catalogue, same-row demand scenarios, envelope rules,
and governing references before designing any beam. Keep P1 as a separate
high-priority optimizer-truth repair before Pareto optimization is reused; it
does not block the read-only W3A data contract. P3 follows only after W3A is
accepted. Do not start with a broad FEM engine or ETABS write-back setters.
