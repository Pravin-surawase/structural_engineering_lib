---
task: INDIA-2-NEXT-SESSION-PUBLICATION-AND-CLOSEOUT
title: INDIA-2 Next Session and Finish Plan
status: active
owner: Next Main Agent
created: 2026-08-16
last_updated: 2026-08-16
doc_type: spec
---

# INDIA-2 Next Session and Finish Plan

## 1. Immediate objective and stop boundary

COMBINED-C/D and focused family acceptance are integrated. STRAP-G0 returned
GO for one source-bound property-line two-footing model with equal uniform net
pressure, a straight no-soil-contact strap, explicit service/factored actions,
and externally verified footing slabs. STRAP-A implements its bounded statics,
bearing, clear-strap actions, and exact equilibrium. The next packet is
`INDIA-2-FOUNDATION-STRAP-B` after A merges unchanged with required checks
green.

Finish the bounded strap sequence A -> B -> C -> D -> focused acceptance, one
fresh lane and focused gate at a time. Stop before pile-cap G0. Do not add
automatic footing strength/sizing, raft, broad Python, full 30-check, React,
release, cleanup, or professional-approval work inside the strap sequence.

The complete remaining order is:

1. `COMBINED-C` — typed public Python workflow.
2. `COMBINED-D` — thin FastAPI transport and truthful capability publication.
3. `COMBINED-ACCEPTANCE` — focused cumulative family acceptance, complete.
4. `STRAP-G0` -> A -> B -> C -> D -> focused family acceptance.
5. Separate `PILE-CAP-G0` and `RAFT-G0` decisions, preserving any accepted
   `HOLD` with a blocker and reactivation condition.
6. Implement only owner-accepted later `GO` cases.
7. `INDIA-2-TRUTH-HYGIENE` — resolve the two recorded clause-registry defects.
8. `INDIA-2-CLOSEOUT` — broad Python, full 30-check, evidence index, and exact
   integrated-tree reconciliation.

## 2. Verified inherited state

At the merged COMBINED-D baseline:

- wall, staircase, deep-beam, and flat-slab/punching bounded families are
  accepted;
- combined-footing G0/A-D are integrated within one symmetric two-column case;
- generated truth is `12 supported / 9 held`, and the bounded combined-footing
  workflow is supported while all alternate systems remain held;
- all 80 endpoints have direct tests;
- COMBINED-D has 6 direct transport tests, 84 cumulative A-D tests, and a
  339-test focused combined/public-contract selection;
- architecture is `0/193`, imports are `0` broken across 222 Python files,
  1,250 internal links are valid, source binding is true, and the quick gate is
  `10/10`;
- the corrected final B head was independently audited at
  `948787bb56d28b8fbcca83aa94f1c68a26ec2eab`, tree
  `66243e06608f9323c605f16b8ca96eaf93d04fa5`, including a non-frozen
  `7200 x 3000 mm` symmetric case that returned `PASS`; and
- PR #789 squash-merged that exact tree as
  `f87c8a32aca7edc015f96f6e053f30c904ae683b`, with six applicable checks
  passing and two correctly skipped; and
- PR #790 squash-merged C as
  `7b7b310a9310c04a65b1dcdfd4ef812c792bb8cb`, tree
  `dd9ed4adf0b20de5d307689ecdf502801fad2d6e`; and
- PR #791 squash-merged the independently audited D tree
  `efba5971017b03e14e3b2f30fd40750f8fc68987` as
  `079ca22b00744ca9b01f859be0b64333b5830fcb`, with seven hosted checks passing,
  one correctly skipped, and none failing; and
- public distribution permission is already recorded and must not be requested
  again. No release, tag, package publication, branch deletion, or worktree
  cleanup is authorized.

The next agent must recheck live `main`, PR integration, and source binding;
these facts are receipts, not permission to assume remote freshness.

Required evidence:

- [combined G0 scope](../verification/india-2-foundation-combined-g0-scope-evidence.md)
- [combined A analysis](../verification/india-2-foundation-combined-a-analysis-evidence.md)
- [combined B strength](../verification/india-2-foundation-combined-b-strength-evidence.md)
- [combined C public workflow](../verification/india-2-foundation-combined-c-public-workflow-evidence.md)
- [combined D publication](../verification/india-2-foundation-combined-d-publication-evidence.md)
- [combined focused family acceptance](../verification/india-2-foundation-combined-family-acceptance-evidence.md)
- [generated capability truth](../verification/indian-code-capability-coverage.json)
- [INDIA-2 execution plan](india-2-remaining-is456-elements-plan.md)
- [canonical Git workflow](../git-automation/git-workflow-single-source.md)

## 3. Start commands and Git boundary

Run from a fresh `codex/india-2-foundation-combined-acceptance` worktree created
from verified merged-D `main`:

```bash
./run.sh session brief --agent reviewer
./run.sh session start
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/generate_indian_code_manifest.py --check
./run.sh parity
```

Require `source_bound=true`, a clean new lane, no unfinished operation, and a
base equal to verified current `origin/main`. Preserve every retained sibling
worktree. Never reset, clean, stash, delete, rebase, force-push, or repurpose a
prior packet lane.

At B closeout, read-only state reported the foreign retained worktree
`/Users/pravinsurawase/.codex/worktrees/e54a/structural_engineering_lib` as
detached with one dirty path. Its root cause and ownership are unconfirmed.
Do not use, mutate, clean, or retire it during INDIA-2; classify it only in a
separately authorized Git-governance task.

Use one active writer. The parent normally implements and validates. Use at
most one read-only independent auditor after an immutable candidate commit;
do not delegate broad context or duplicate implementation.

## 4. COMBINED-C exact packet

### Objective

Expose the sole accepted A/B composition as one stable typed public Python
workflow named `design_symmetric_combined_footing_is456` while leaving machine
capability truth held until D.

### Intended files

- add `Python/structural_lib/services/combined_footing_api.py`;
- export only through `Python/structural_lib/services/api.py`,
  `Python/structural_lib/services/__init__.py`, and
  `Python/structural_lib/__init__.py`; the backward `api.py` stub should inherit
  exports and must not contain implementation;
- add `Python/tests/integration/test_combined_footing_publication.py`;
- update `docs/reference/api.md`, `docs/reference/api-stability.md`, maintained
  API/export tests, folder indexes, session log, and C evidence.

### Public contract

Create immutable:

- `SymmetricCombinedFootingDesignInput`;
- `SymmetricCombinedFootingDesignProvenance`;
- `SymmetricCombinedFootingDesignResult`;
- `SymmetricCombinedFootingDesignStatus`; and
- a mapping builder only if transport construction needs it later.

The workflow must consume the A/B typed inputs without duplicating structural
math. It must return the B action/strength result, supported case, held cases,
schema/code/workflow/benchmark identities, all caller basis references, exact
clause/source references, qualified-review true, and complete-engineering-
approval false. `PASS` and valid in-domain `FAIL` remain results; unsupported
input raises `CombinedFootingContractError`.

The frozen benchmark remains:

- `6000 x 2500 x 850 mm`, `d = 750 mm`, two 500 mm square columns at
  `x = 1000/5000 mm`, M30/Fe500;
- `900/1350 kN` service/factored load at each column, `25/37.5 kN/m2`
  distributed carrier, and `150 kN/m2` allowable gross pressure;
- 16 mm longitudinal bars at 190 mm, 12 mm transverse bars at 110 mm,
  50 mm cover, 20 mm aggregate, and 800 mm anchorage;
- approved `250000 mm2` supporting area at each column and four 20 mm dowels
  with 800 mm embedment into footing and column; and
- aggregate `PASS`, review required, approval false.

### C acceptance

- exact root/services/stub identity and `__all__` tests;
- frozen serializable result, provenance, held cases, valid `FAIL`, and invalid
  fail-closed tests;
- capability manifest must remain 11/10 and combined footing held;
- focused A/B/C, public API signature/export/docs, clause/manifest, Ruff,
  mypy, architecture/import/link/index, quick 10/10, normal commit hooks,
  immutable independent audit, and all applicable hosted PR checks pass;
- no FastAPI, semantic-contract, capability promotion, React, broad Python, or
  full 30-check mutation/run.

## 5. COMBINED-D exact packet

Start a new clean `codex/india-2-foundation-combined-d` lane from merged C.
Recommended owner role: `api-developer`.

Publish only:

- strict Pydantic request/response types in
  `fastapi_app/models/combined_footing.py`;
- thin router `fastapi_app/routers/combined_footing.py` at
  `POST /api/v1/design/combined-footing/symmetric`;
- router mounting/tag metadata and direct transport tests;
- exact OpenAPI baseline update after independently reviewing the intended
  new path/schema only;
- capability declaration, public workflow, semantic fields/statuses, and
  generated manifest promotion for the exact supported case; and
- D publication evidence plus maintained docs/index/session records.

Do not reimplement calculations in Pydantic/router code. Map domain errors to
the maintained safe error response. The capability claim must say exactly two
identical square columns with equal concentric loads on one symmetric rigid
rectangular constant-depth footing under caller-approved uniform pressure.

Expected truth after D is `12 supported / 9 held` and 80/80 directly tested
endpoints, subject to live verification. React remains excluded and should be
skipped, not represented as tested.

Run the D-focused service/router/OpenAPI/capability/semantic/manifest selection,
architecture/import/link/index, quick gate, commit hooks, immutable audit, and
hosted checks. Defer broad Python and full 30-check.

## 6. COMBINED family acceptance — complete

The fresh acceptance-only lane starts from merged D and adds no feature
behavior.

Re-run:

- all combined A-D unit/integration/FastAPI tests;
- frozen benchmark and at least one independent non-frozen symmetric case;
- valid bearing, reinforcement, shear, punching, and transfer failures;
- every topology/material/approval/supporting-area fail-closed boundary;
- public export, JSON serialization, OpenAPI, capability, semantic, and
  deterministic manifest checks;
- architecture/import/link/index, quick, exact-head independent audit, and all
  hosted checks.

Write one family acceptance receipt binding source, benchmark, C/D PRs,
integrated tree, supported case, held cases, review boundary, and deferred broad
gate. Do not add another topology or implementation during acceptance.

## 7. Remaining foundation decisions

After combined acceptance, STRAP-G0 returned GO and activated its A/B/C/D/
acceptance sequence. Finish that bounded sequence before starting the remaining
decision-only packets in this order:

1. `INDIA-2-FOUNDATION-PILE-CAP-G0`;
2. `INDIA-2-FOUNDATION-RAFT-G0`.

Each G0 must search existing code, bind controlled/authoritative sources,
freeze one useful supported case and independent benchmark, list exclusions,
and return `GO`, `REVISE`, or owner-approved `HOLD` before code. Do not reuse
combined- or isolated-footing capability for a different analysis model.

If a decision is `GO`, activate A/B/C/D/acceptance packets with the same
analysis → strength → public Python → FastAPI/truth → family acceptance order.
If `HOLD`, record the missing source/model/benchmark, retained public hold, and
exact reactivation condition. An owner-approved hold closes the INDIA-2
administrative obligation truthfully; it is not implementation.

STRAP-G0 resolved strap-beam soil contact and compatibility only for its frozen
property-line model. High-risk distinctions still requiring later decisions
are pile reaction/nodal/bearing and companion-code boundaries, plus raft soil-
structure/FEM requirements. Do not guess them.

## 8. Recorded truth defects — required later packet

Do not mix these cross-cutting repairs into COMBINED-C/D. Create one bounded
`INDIA-2-TRUTH-HYGIENE` packet after all family decisions and before the broad
closeout:

- `clauses.json` currently labels `26.5.1.1` as minimum shear reinforcement,
  but the controlled IS 456 source identifies it as beam tension
  reinforcement. The origin of the stale metadata entry is unconfirmed.
- the controlled source contains Clause 38.1 and Annex G-1.1 for the relevant
  flexural solution, but the registry and legacy beam decorators retain a
  `38.2` identity. COMBINED-B correctly avoids it; a broad migration/removal was
  out of B scope. The historical reason for the fabricated identity is
  unconfirmed.

Trace every live `38.2` consumer before changing it. Correct exact metadata and
decorators only where the controlled source supports the replacement, update
traceability expectations, regenerate the manifest once, and prove zero
registration-only/unknown contradictions. Do not use a mass textual replace.

## 9. INDIA-2 final closeout

Only after combined acceptance and every remaining foundation decision/GO
packet is integrated:

1. reconcile the execution plan, completion waves, task board, next-session
   brief, public API docs, capability declarations, semantic contract, and
   generated manifest;
2. build an INDIA-2 evidence index mapping every accepted family to source,
   benchmark, public workflow/route, PR, checks, and integrated tree;
3. run the broad Python suite once with `./run.sh test`;
4. run the canonical 30-check repository gate once with `./run.sh check`;
5. run complete FastAPI/public-contract tests and any closeout-only packaging
   or OpenAPI gates selected by the maintained 30-check command;
6. independently audit the exact final tree, require all hosted checks green,
   and merge unchanged; and
7. report total elapsed workflow time, including CI and closeout.

Do not claim whole-standard coverage, professional approval, stable release,
package publication, tag/release authority, INDIA-3/4 completion, or
engineering-use authorization.

## 10. Efficiency and return format

- Read this plan and the three combined evidence files; do not reload large
  historical logs.
- Start with folder indexes and targeted `rg`; discover signatures instead of
  guessing paths/names.
- Run focused gates once per packet; broad gates only at final closeout unless
  a confirmed repository-wide outcome-changing failure forces them earlier.
- Record every encountered material issue. If intentionally left out of scope,
  record symptom/impact, confirmed root cause or `unconfirmed`, why it was not
  changed, and the follow-up packet/reactivation condition.
- Keep one writer and one immutable read-only audit; preserve every other lane.

At each handoff return: packet/status, base/head/tree, source binding, changed
paths, benchmark and unsafe results, focused test/gate counts, issues/root
causes/resolutions including deferred items, capability/endpoint truth,
review/release/cleanup boundaries, PR/check/merge receipts, and the exact next
packet.
