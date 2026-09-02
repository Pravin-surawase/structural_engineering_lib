---
owner: Main Agent
status: active
last_updated: 2026-09-02
doc_type: spec
complexity: intermediate
tags: [beam, etabs, structural-model, design, optimization, reanalysis]
---

# Beam design and ETABS optimization master plan

## Decision

Use the six phases below as the human-facing programme for beam automation.
Work on one phase at a time, close its evidence gate, and only then activate the
next phase. Code that already exists for a later phase may remain and may be
tested with authored fixtures, but it does not make that phase complete.

The detailed [W3 execution plan](w3-beam-professional-integrated-execution-plan.md)
continues to own low-level packet IDs, ETABS safety controls and evidence
receipts. This document owns the overall goal, phase order, phase outputs and
definition of done.

This plan records work; it does not by itself authorize an ETABS operation,
model mutation, release, professional approval or construction use.

## North-star goal

Starting from an exactly identified ETABS model, produce a reproducible
structural dataset, understand the connected beam system, design every supported
beam through all mandatory gates, find the best feasible candidate, and verify
the selected changes by fresh whole-model ETABS analysis on an owned copy.

The final result must explain:

- what was read from ETABS and which result epoch it belongs to;
- how each beam, span, joint, support and connected element was interpreted;
- which design checks passed, failed or could not be completed;
- which alternatives were considered and why one was selected;
- what changed in the verified copy, what stayed unchanged and what was saved;
- the material, cost and constructability effect of the accepted changes; and
- the exact limitations and review still required.

The target is the **best feasible design under declared project criteria**, not
merely the smallest dimensions. A smaller beam can be worse because of
deflection, reinforcement congestion, anchorage, continuity, formwork,
construction practice or whole-building response.

## System boundary

- **ETABS owns whole-building analysis.** Its fresh results are the final source
  for changed-model forces, reactions, drifts and other global safeguards.
- **The structural library owns interpretation, design, detailing and candidate
  evaluation.** Engineering decisions must not live inside a COM, SQLite, REST
  or UI adapter.
- **The local beam-line solver is a bounded screening tool.** It may be used
  only inside a proved applicability envelope; it does not silently replace
  ETABS as the building-analysis authority.
- **A database is optional storage, not a second truth source.** The working
  authority is a typed, hash-bound project snapshot. Cache or database rows must
  be reproducible from that snapshot.
- **The original ETABS model is never the optimization workspace.** Every
  candidate that reaches reanalysis uses a fresh, identified owned copy.

## Six-phase flow

```text
ETABS model
    |
    v
1. Trusted acquisition
    |
    v
2. Canonical project data
    |
    v
3. Connected structural model
    |
    v
4. Design-gate result
    |
    v
5. Ranked feasible candidates
    |
    v
6. Owned-copy ETABS reanalysis loop
    |
    v
Verified change set + savings + limitations
```

Every phase ends in one of three states:

- `PASS`: the declared phase output and all mandatory evidence are complete;
- `FAIL`: the input or candidate was evaluated and does not satisfy the gate;
- `HOLD`: required identity, data, applicability or evidence is missing or
  uncertain. `HOLD` is never converted into `PASS` by a default assumption.

## Current programme status

| Phase | Status | Present position |
|---|---|---|
| 1. Connect and acquire | **ACTIVE** | Process/runtime/model guards and the installed schema inventory are accepted. The exact-schema parser and a fresh trusted building-result epoch are still missing. |
| 2. Normalize and understand | Partial, not active | Typed points, frames, actions and foundation readback exist, but there is no complete canonical project dataset. |
| 3. Reconstruct the structure | Partial, not active | Frame/joint contracts and a bounded 2D beam-line solver exist. Complete beam-line, support, continuity, column and slab topology is not yet reconstructed. |
| 4. Run design gates | Partial, not active | Strength, supplied reinforcement, detailing and layer-aware candidate composition exist. The unified path does not yet natively close every torsion, serviceability, lap, continuity and constructability case. |
| 5. Optimize | Partial, not active | Deterministic candidate evaluation and search exist. Practical candidate generation and changed-stiffness/global-response closure do not. |
| 6. Reanalyse and converge | Planned | Owned-copy mutation, reanalysis, recovery and bounded iteration are specified but not implemented. |

Only Phase 1 is active. Later-phase implementation is retained, but expansion
of those phases waits until Phase 1 passes.

## Phase 1 — Connect to ETABS and acquire trusted data

### Goal

Read the correct model, geometry, properties, connectivity and analysis/design
results without changing the user's model, and prove exactly where every value
came from.

### Minimum required data

Acquire only data required by the beam workflow:

- process, ETABS/API runtime, model path, file hash, units and lock state;
- stories, grids where needed, points, restraints, springs and diaphragms;
- frame objects, end joints, local axes, releases, offsets, insertion points and
  stiffness modifiers;
- material and frame-section properties used by the selected beams and their
  connected supports;
- loads, load cases, combinations and selected output basis;
- signed station forces with frame, story, end, local-axis and physical-face
  identity;
- required beam design rows and their governing combinations; and
- result-epoch, acquisition-method, row-count and source-table evidence.

Do not copy the entire ETABS database merely because it is available. Start
with an allowlist and extend it only when a later phase proves a missing field is
necessary.

### Output

A **trusted ETABS baseline package** containing immutable raw evidence plus a
typed normalized projection. The raw evidence supports audit; later phases
consume the typed projection.

### Exit gate

Phase 1 passes only when:

1. the exact process, runtime, model and saved-file identity are bound together;
2. the result epoch is fresh for the exact model state being claimed;
3. all required fields parse with explicit types and units;
4. signed forces retain station, local-axis, combination and physical-face
   identity;
5. pre/post state proves the original model was unchanged; and
6. a repeated acquisition produces the same normalized identities, counts and
   values within declared tolerances.

### Current gap

The session/target/freshness contracts, getter-only installed evidence and exact
C1 SQLite schema are accepted through PRs #947 and #952. The next offline work
is the exact-schema C2 parser. The observed design export remains diagnostic
because its result epoch is `BLOCKED`; it cannot yet be called fresh project
force or design truth.

## Phase 2 — Normalize the data and make engineering sense of it

### Goal

Convert ETABS-shaped records into one canonical in-memory project model without
losing source identity or creating a second calculation route.

### Work

- normalize all units at the boundary;
- resolve stable identities for stories, joints, frames, sections, materials,
  load cases, combinations and result rows;
- retain both raw and normalized values with provenance;
- build signed action sets and envelopes without losing the governing row;
- distinguish absent, unavailable, unsupported and not-yet-acquired data; and
- store only the canonical snapshot or a reproducible cache of it.

### Output

A **canonical project dataset** that later phases can consume without knowing
whether a value came from COM, a proved getter or the allowlisted SQLite export.

### Exit gate

Every required value has explicit units, source and identity; all relationships
resolve; repeated normalization is deterministic; and no engineering default
silently fills missing evidence.

## Phase 3 — Reconstruct the connected structural system

### Goal

Turn normalized objects into the structural system needed to understand each
beam rather than treating every ETABS frame as an isolated line.

### Work

- build the joint-member connectivity graph;
- classify beams, columns, supports and beam ends from geometry and connectivity;
- join collinear beam objects into physical spans and continuous beam lines;
- retain releases, offsets, insertion points, local axes and stiffness changes;
- identify columns, walls, slabs, diaphragms and adjoining beams that affect
  support or load-path interpretation;
- establish tributary/load-path information only where required and evidenced;
  and
- declare the applicability boundary for the local beam-line solver.

### Output

A **connected structural model** with beam lines, spans, joints, supports,
connected elements and traceable source-object identities.

### Exit gate

The model closes topologically, beam ends and supports are unambiguous, signed
actions align with reconstructed local axes, and unsupported structural systems
are explicitly held.

Columns and slabs are reconstructed here as context and safeguards. Their full
design and optimization remain separate future programmes.

## Phase 4 — Design each beam through mandatory gates

### Goal

Evaluate the existing beam and every later candidate as a physical member over
its spans, faces, supports and construction zones—not as one governing scalar.

### Mandatory gates

- flexure at relevant positive- and negative-moment regions;
- shear and torsion, including their interaction and detailing effects;
- serviceability, including the supported deflection and cracking basis;
- minimum/maximum reinforcement and bar spacing;
- anchorage, development length, curtailment and support conditions;
- lap/splice location and bar continuation through spans and supports;
- beam-column/slab/joint compatibility and continuity constraints;
- reinforcement congestion, cover, constructability and formwork rules; and
- quantities, bar marks and reinforcement schedule consistency.

Reinforcement layers are first-class data. Each layer must preserve its face,
bar count, diameter, material and centroid position; total steel area and
effective depth are derived from the layers. No adapter may reduce a layer
layout to only `As` and then recreate geometry from assumptions.

The first end-to-end slice remains deliberately bounded to rectangular beams,
full-span top/bottom reinforcement layers and exact transverse zones. Multiple
layers, mixed diameters, curtailment and wider torsion arrangements are added
after the first complete loop works; until then those cases return `HOLD`.

### Output

One **design-gate result** per existing beam or candidate, with a result for
every mandatory check and one aggregate `PASS`, `FAIL` or `HOLD` disposition.

### Exit gate

No mandatory check is missing, every result identifies the governing demand and
calculation basis, and quantities/detailing describe the same reinforcement
that was checked.

## Phase 5 — Generate and rank the best feasible candidates

### Goal

Generate realistic alternatives, pass each through the Phase 4 evaluator and
rank only candidates that satisfy every mandatory project criterion.

### Two optimization levels

1. **Reinforcement optimization with unchanged section stiffness.** These
   candidates may be screened against the trusted baseline forces.
2. **Section/property optimization.** These candidates are proposals only until
   Phase 6 obtains fresh ETABS forces, because changing stiffness redistributes
   whole-building actions.

The first reanalysis loop uses verified section properties that already exist
in the ETABS model. Creating arbitrary new ETABS property definitions is a
later extension after the transaction loop is proved.

### Objectives

Optimize under declared priorities such as cost, steel mass, concrete volume,
formwork, embodied impact, congestion and number of distinct bar marks. The
search must record its domain, traversal, limits and tie-break rules. A
budget-truncated search may return useful provisional candidates but may not
claim an optimum, complete Pareto frontier or infeasibility.

### Output

A **ranked shortlist** with exact candidate geometry, reinforcement schedule,
gate result, quantities, objective values and search-completeness status.

### Exit gate

Every shortlisted candidate has no mandatory `HOLD`, the search claim matches
its completeness, and any stiffness-changing candidate is marked for Phase 6
rather than accepted on old forces.

## Phase 6 — Reanalyse candidates in ETABS and converge

### Goal

Prove that the selected modifications remain feasible after their effect on the
whole model is included, then stop at a declared terminal condition.

### Loop

For each accepted shortlist candidate:

1. create a fresh hash-bound copy and start an owned ETABS process;
2. apply the exact allowed change set and read it back;
3. run analysis and required design operations under a new result epoch;
4. reacquire the Phase 1 minimum dataset;
5. rebuild the Phase 2 and Phase 3 artifacts;
6. rerun all Phase 4 gates and Phase 5 ranking;
7. check whole-model safeguards such as reactions, drift, connected columns,
   joints, slabs and unchanged objects; and
8. accept, reject or generate the next bounded candidate.

Each candidate starts from a clean copy. A failed or interrupted transaction is
verified or quarantined; a non-idempotent ETABS call is never guessed or blindly
replayed.

### Terminal outcomes

- an accepted candidate passes and is independently repeated from a fresh copy;
- the complete declared domain contains no feasible candidate;
- the attempt, time or analysis budget is exhausted;
- required external/project evidence remains unavailable; or
- a safety, applicability or transaction uncertainty forces `HOLD`.

### Output

A **verified optimization package** containing the final change set, original
and final identities, fresh results, complete gate results, rejected candidates,
material/cost savings, constructability effects, limitations and rollback or
retention instructions.

## Function and capability roadmap

The rule is simple: extend the existing engineering owner when the calculation
already exists; add a new function only for a genuinely new responsibility.
ETABS, SQLite, REST and UI adapters translate data and never duplicate design
logic.

| Phase | Reuse now | Required addition or convergence |
|---|---|---|
| 1 | `discover_etabs_processes_v1`, runtime/target/state/freshness/result-epoch functions, `extract_etabs_beam_baseline_v1`, `inventory_etabs_sqlite_export_v1` | Implement `parse_etabs_sqlite_export_v1`; add one allowlisted acquisition orchestrator and repeatability receipt rather than more one-off getters. |
| 2 | Typed ETABS point/frame/action/foundation contracts, including `BeamActionsV1` | Add one canonical project-snapshot assembler, relationship validator and deterministic normalization path. |
| 3 | Existing joint/frame contracts and `solve_beam_line_linear_v1` | Add topology reconstruction, beam-line/span classification, support/continuity resolution and solver-applicability checks. |
| 4 | `LongitudinalBarLayersV1`, supplied-beam services and `evaluate_beam_candidate_v2` | Compose native torsion, serviceability, lap/continuity and constructability gates; extend layer/schedule support without bypassing the common evaluator. |
| 5 | `search_beam_candidates_v1` and project criteria/catalogue contracts | Implement `generate_bar_layer_candidates_v2`, bounded section/property generation and objective projections that all reuse the same evaluator. |
| 6 | Session guard, lease, broker, ledger and evidence contracts | Implement change-set planning, owned-copy preparation/session start, apply/readback, analysis transaction, recovery, candidate verification and finalization. |

Before adding any new public function, search the maintained API and callers.
If an existing function owns the outcome, update and version it rather than
creating another calculation path.

## Efficient execution rules

1. Keep **one active phase** and one writer. Use parallel review only for
   independent read-only questions that materially shorten the work.
2. Freeze the phase output contract before expanding implementation.
3. Prove one thin vertical slice first: one identified model, one beam line, one
   existing beam and one candidate through the complete available path.
4. Acquire only the ETABS fields needed by the next consumer.
5. Keep installed ETABS work in bounded, separately authorized evidence windows;
   do parsing, normalization, design and search offline.
6. Reuse immutable artifact digests so unchanged calculations can be cached and
   compared without reacquisition.
7. Batch related code, tests and documentation into one coherent candidate and
   one PR-level validation cycle after content freezes.
8. Do not build a full 3D solver merely to avoid an explicit ETABS-first route.
9. Record every phase decision, missing datum and limitation so later work does
   not reopen settled questions.

## Immediate Phase 1 plan

Work in this order:

1. freeze the minimum baseline field allowlist and canonical output contract;
2. implement C2 parsing for only the accepted C1 tables and fields;
3. prove schema, integrity, bounds, units, identity and deterministic offline
   normalization while preserving the current result-epoch `HOLD`;
4. add the single Phase 1 acquisition/repeatability receipt;
5. obtain separately authorized fresh-result evidence for the exact project
   state; and
6. repeat acquisition and close Phase 1 only when the full exit gate passes.

Until then, Phase 2 is the next planned phase, not active work.

## Deliberately deferred

- full column, slab, footing or wall design/optimization;
- a general-purpose three-dimensional building solver;
- arbitrary new ETABS section-property creation;
- unsupported deep, flanged, seismic-capacity or unusual torsion cases;
- broad UI/product expansion before the canonical backend loop works; and
- any claim of professional approval or construction readiness without the
  required qualified review.
