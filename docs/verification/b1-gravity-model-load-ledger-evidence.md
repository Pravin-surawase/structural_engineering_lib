---
owner: Main Agent
status: active
last_updated: 2026-08-17
doc_type: reference
complexity: advanced
tags: [b1, gravity, load-ledger, reconciliation, evidence]
---

# B1 Gravity Model and Load Ledger Evidence

**Evidence boundary:** B1 physical model, immutable dead/live basis,
deterministic transfer ledger, and exact balance checks only. This record does
not claim component design or Gravity Workflow V1 completion.

## Source identity

- Branch: `codex/b1-gravity-model-load-ledger`.
- Base: merged G1 head `32daa0138b969be0b77b59dd33d938ad170f3a9e`.
- The isolated worktree runtime reported `source_bound=true` before writes.

## Implemented contract

- `BuildingModelV1` accepts only the frozen one-storey slab/beam/column/footing
  topology and rejects duplicate, orphan, disconnected, ambiguous, or
  incompletely accounted content.
- Every physical object has separate canonical, load-path, and render identity.
  Raw-source records retain provenance while harmless ordering is excluded from
  accepted-model identity.
- `LoadModelV1` freezes five included dead/live source categories, two exact
  combinations, source references, ownership, balance tolerance, and all 11
  approved V1 exclusions.
- The service ledger generates self-weight exactly once, transfers the one-way
  slab to its two beams, takes simple beam reactions to four columns, adds each
  column self-weight, and hands concentric axial actions to four footing
  destinations.
- Every transfer preserves origin identities and formula basis. Six boundary
  types reconcile source and destination totals. A model-hash mismatch or
  out-of-tolerance balance fails closed.
- Footing self-weight, overburden, and soil are visibly excluded; the footing
  result is an action handoff, not a design approval.

## Independent hand arithmetic

For the frozen 6 m x 4 m example:

- slab dead = `(0.15 x 25 + 1.5) x 24 = 126 kN`;
- live = `3.0 x 24 = 72 kN`;
- each beam dead = `126/2 + (0.3 x 0.5 x 25 x 6) = 85.5 kN`;
- each beam-end dead reaction = `85.5/2 = 42.75 kN`;
- each column self-weight = `0.3 x 0.3 x 3 x 25 = 6.75 kN`;
- each footing destination = `49.5 kN DL + 18 kN LL`;
- all footings = `198 kN DL + 72 kN LL = 270 kN service`; and
- factored foundation total = `1.5 x 270 = 405 kN`.

The executable vector confirms 67.5 kN service and 101.25 kN factored action
at each of the four footing destinations.

## Verification through implementation freeze

- New focused tests: `10 passed`.
- Configured mypy for the two new source modules: no issues.
- The tests cover exact arithmetic, all boundary residuals, source/exclusion
  counts, no inferred footing weight, deterministic repeat identity, harmless
  input ordering, orphan and duplicate-source rejection, exact combinations,
  model-hash mismatch, two-times scaling, and non-finite input rejection.
- The consolidated focused Python selection passed `52/52`. Architecture
  checked 210 files with zero violations; all 1,384 imports across 238 library
  files resolved; 191-file circular-import analysis found no cycle; and the
  public core/service re-exports import successfully.
- All five documentation checks pass at the 400-file active limit and all 1,362
  internal links resolve. The first quick gate passed `10/10`.
- The first normal hook attempt passed full-library mypy (238 files), Ruff,
  Bandit, JSON, links, docs, and governance checks. Only its EOF fixer rejected
  the candidate; the generator/EOF root cause is repaired and has a dedicated
  passing regression.

The consolidated focused B1 selection, architecture/import checks, one quick
gate, commit hooks, immutable audit, push, and hosted validation are recorded
only after content freeze. Broad Python and the full repository gate remain
reserved for cumulative M2+M3 milestone closeout under the master plan.

## Efficiency receipt through implementation freeze

| Receipt | Actual |
|---|---:|
| Unchanged-suite reruns | 0 |
| New focused test-file runs | 3 (initial, repair, post-type repair) |
| Frozen focused verification batches | 1 (documentation metadata rejected) |
| Impact-mapped repair batches | 2 |
| Normal commit-hook attempts | 2 (EOF generator repair; Black-only test repair) |
| Broad Python suites | 0 |
| Full repository gates | 0 |
| Quick gates | 2 (initial and repaired candidates both 10/10) |
| Hosted validation runs | 0 |
