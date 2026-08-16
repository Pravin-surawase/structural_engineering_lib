---
task: NEXT-SESSION-GIT-ISSUES-AND-INDIA-2
title: Next Session Git Reconciliation, Issue Repairs, and INDIA-2 Finish Plan
status: active
owner: Next Main Agent
created: 2026-08-16
last_updated: 2026-08-16
doc_type: spec
---

# Next Session Git Reconciliation, Issue Repairs, and INDIA-2 Finish Plan

## 1. Outcome and stop boundary

Combined-footing and strap-footing G0/A-D plus focused family acceptance are
integrated within their recorded bounded cases. The next session starts with
Git and confirmed issue reconciliation before any new foundation decision.

This document is a plan only. Its publication does not authorize primary-main
synchronization, discarding a local change, branch/worktree retirement, closing
dependency PRs, pile-cap or raft implementation, release work, or professional
approval. Stop after this planning packet merges.

Execute later work in this order, one fresh lane and one active writer at a
time:

1. `GIT-001-P8-RECONCILIATION` — reconcile the completed GIT-7E work, prove
   current adoption, classify retained lanes, and obtain any required owner
   decisions without cleanup.
2. `DOC-FRONTMATTER-CONTRACT` — repair the JSON-mode exit-code defect and the
   eight currently invalid frontmatter records.
3. `INDIA-2-TRUTH-HYGIENE-38-2` — source-audit every live `38.2` consumer,
   correct provenance, and change arithmetic only if an independently checked
   benchmark proves an outcome defect.
4. `INDIA-2-FOUNDATION-PILE-CAP-G0` — decision and benchmark only.
5. Implement pile-cap A/B/C/D/acceptance only if G0 returns an owner-accepted
   `GO`; otherwise record `HOLD` and its reactivation condition.
6. `INDIA-2-FOUNDATION-RAFT-G0` — decision and benchmark only.
7. Implement raft A/B/C/D/acceptance only if G0 returns an owner-accepted
   `GO`; otherwise record `HOLD` and its reactivation condition.
8. `INDIA-2-CLOSEOUT` — cumulative truth reconciliation, broad Python, the
   full 30-check gate, independent final-tree audit, hosted checks, and merge.
9. Only after INDIA-2 closes, resume the separately bounded dependency-major
   compatibility packets.

## 2. Verified planning baseline

Live inspection for this plan established:

- `origin/main = f56e1ec312902caf98e872c77ce8b71bdbc8440e`, the squash merge
  of strap-family acceptance PR #798, with merged tree
  `28698a28d96f3e5cbad26fd6964cf835cda6e1b4` equal to the audited candidate
  tree;
- Indian-code truth is `13 supported / 8 held`, with all 81 endpoints directly
  tested; wall, staircase, deep-beam, flat-slab/punching, combined-footing, and
  strap-footing are accepted only within their written cases;
- the primary checkout remains at `f87c8a32`, nine commits behind
  `origin/main`, with exactly one user-owned modification:
  `.codex/config.toml` changes `model_verbosity = "low"` to `"medium"`;
- retained `e54a` remains detached at `0fdb48ed`, with only
  `docs/SESSION_LOG.md` dirty (`119` insertions, `7` deletions); current main
  already contains the material GIT-7C1/GIT-7C2 facts, but ownership and
  retirement authorization remain unresolved;
- GIT-7E implementation PR #751 merged as `6bcbd9d3`, and compact audited
  orchestration PR #752 merged as `96f193bd`; this planning packet reconciles
  the stale parent-ledger/task wording, while Phase 8 must still verify current
  adoption and any remaining dated disposition facts;
- Clause `26.5.1.1` is no longer an open defect: STRAP-B corrected its metadata
  to beam minimum tension reinforcement, added Clause `26.4`, regenerated the
  manifest, and added semantic regression coverage;
- the live clause database, beam decorators, result provenance, and manifest
  still register `38.2` for three beam-flexure functions even though the prior
  controlled-source review found the relevant identities under Clause `38.1`
  and Annex G;
- `scripts/check_docs.py --frontmatter --json` reports eight invalid records
  but exits successfully; code inspection confirms JSON mode unconditionally
  returns `0` before applying the invalid-count failure rule; and
- seven old Dependabot PRs remain open. Their historical checks and stale bases
  are not current merge authority.

Every fact above must be refreshed in the executing packet. A dated plan is not
remote-freshness or mutation authority.

## 3. Packet 1 — GIT-001 Phase 8 reconciliation

### Objective

Verify that the reconciled GIT-7E status and operating model are actually used
by recent combined/strap packets, then produce a current preservation/
disposition record. This is inspection and documentation work, not cleanup.

### Required start

From a fresh worktree based on fetched `origin/main`:

```bash
./run.sh session brief --agent ops
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
```

Require `source_bound=true`, `READY_LOCAL`, no operation marker, and exact base
equality with current `origin/main`.

### Work and decisions

1. Bind PR #751/#752 reviewed heads, merge commits, trees, required checks, and
   current reachability. Verify the current “Phase 7 complete; Phase 8
   adoption/closeout next” parent records, and reconcile only remaining dated
   claims that change the current lifecycle outcome.
2. Sample recent combined/strap receipts and exact-head audits to prove whether
   `git_state.py`, source binding, immutable review, hosted checks, and
   post-merge tree equivalence are working in ordinary packets. Record defects
   only when they change the lifecycle outcome.
3. Classify the primary config edit without touching it:
   - **publish** — recover only the `medium` verbosity intent on a fresh
     current-main lane and review it through a separate PR;
   - **retain local-only** — keep the primary held and continue work in fresh
     lanes; or
   - **discard** — requires explicit owner approval immediately before the
     destructive restoration action.
4. Compare `e54a` by exact patch/blob identity with integrated main evidence.
   Never merge its whole historical log, reset it, stash it, or remove it as a
   shortcut. Retention may advance only with a named owner decision and a fresh
   classifier receipt; deletion remains separate exact-target authorization.
5. Refresh every retained worktree/branch read-only. Missing ownership,
   retention, PR, or freshness evidence remains `UNKNOWN`/hold. Do not produce
   a bulk-cleanup command.

### Acceptance

- no pre-existing branch, ref, worktree, dirty path, stash, GitHub setting,
  issue, or PR is mutated;
- GIT-001 status and phase ledger match merged reality;
- adoption evidence is tied to exact recent receipts rather than prose;
- each primary/e54a/other-lane decision is `RETAIN`, `UNKNOWN/HOLD`, or
  `RETIREMENT_READY_PENDING_APPROVAL`; none grants deletion authority;
- focused Git-governance tests, semantic guidance, receipt validation, links,
  indexes, quick `10/10`, normal hooks, hosted checks, and exact-tree closeout
  pass.

## 4. Packet 2 — frontmatter checker and record repair

### Confirmed root cause

`check_frontmatter()` correctly computes `invalid_frontmatter`, but its
`json_output` branch prints the report and returns `0` unconditionally. The
normal text branch applies `return 1 if invalid_frontmatter else 0`. This makes
machine-readable validation say “passed” while returning eight invalid records.

The eight records are separate data defects:

- invalid status: `planning/is456-library-first-master-plan.md`,
  `verification/india-2-foundation-combined-c-public-workflow-evidence.md`,
  and wall/deep/flat family-acceptance evidence;
- invalid `doc_type: verification`: strap A, B, and C evidence.

The 60 legacy documents without lowercase frontmatter are reported separately
and are not automatically in scope because current policy permits their legacy
metadata/no-frontmatter forms. Expand scope only if a maintained gate proves a
main-process failure.

### Fix and acceptance

1. Make JSON mode return the same pass/fail result as text mode without changing
   its JSON payload.
2. Add a direct regression proving invalid JSON-mode input exits nonzero and a
   valid fixture exits zero.
3. Give each of the eight records a schema-valid lifecycle/doc type that
   preserves its narrative completion/acceptance meaning; do not rewrite
   engineering evidence.
4. Require live JSON output to report `invalid_frontmatter: 0`, text mode to
   pass, focused checker tests, links/indexes, quick `10/10`, normal hooks, and
   hosted documentation checks to pass.

## 5. Packet 3 — Clause 38.2 flexure truth hygiene

### Objective and non-goals

Trace and correct the root cause rather than deleting a label. Do not mass
replace `38.2`, copy protected prose, alter unrelated beam behavior, or infer
that a metadata-only correction proves the flexural arithmetic.

### Required work

1. Recheck the controlled IS 456 base/amendment source and bind the exact
   Clause 38.1 and Annex G identities used by each formula.
2. Enumerate every live consumer: clause metadata, decorators,
   `calculate_ast_required`, singly/doubly reinforced design, serialized
   `sources_used`, tests, docs, and generated manifest records.
3. Independently back-substitute required steel into the exact rectangular
   stress-block equilibrium and compare the legacy `4.6` approximation with the
   shared exact helper already used by slab/combined/strap work.
4. If the difference can change a supported beam PASS/FAIL, fix the shared
   arithmetic root cause with compatibility and benchmark evidence. If it
   cannot, keep arithmetic unchanged and correct only unsupported identities.
5. Add semantic tests that reject reintroduction of unsupported `38.2` metadata,
   decorators, or public provenance. Regenerate the manifest once after the
   executable truth freezes.

### Acceptance

- every changed formula/provenance identity is source-bound and independently
  replayable;
- no registration-only or unsupported clause contradiction remains;
- public signatures and unit conventions remain stable unless a separately
  recorded compatibility decision is required;
- focused flexure, traceability, manifest, public-contract, architecture,
  imports, quick `10/10`, normal hooks, immutable-head review, and hosted checks
  pass.

## 6. Packets 4 onward — remaining foundation decisions

Run `PILE-CAP-G0` and then `RAFT-G0` as separate decision-only packets. Each
must search existing code, bind controlled/authoritative sources, freeze one
useful case and independent benchmark, enumerate companion-code boundaries and
unsafe exclusions, and return `GO`, `REVISE`, or owner-accepted `HOLD` before
calculation code.

Pile-cap G0 must explicitly decide pile-reaction input/model, layout, nodal and
bearing checks, anchorage, deep-region treatment, and companion-code
dependencies. Raft G0 must decide soil-pressure input/model, strip/panel action
extraction, settlement boundary, and whether a useful non-FEM case exists.
Never reuse isolated/combined/strap capability for these different models.

For a `GO`, use A analysis -> B strength -> C typed Python -> D FastAPI/truth ->
focused family acceptance. For a `HOLD`, publish the blocker, retained truth,
and exact reactivation condition; do not manufacture implementation to avoid a
hold.

## 7. INDIA-2 final boundary

Only after all accepted/held family decisions and issue packets are integrated:

1. reconcile plans, task board, public docs, capability/semantic declarations,
   generated manifest, and an evidence index for every accepted family;
2. run the broad Python suite once with `./run.sh test`;
3. run the canonical full repository gate once with `./run.sh check`;
4. run complete FastAPI/public-contract and maintained packaging/OpenAPI checks
   selected by the gate;
5. independently audit the exact final head/tree, require all hosted checks
   green, merge unchanged, and verify the integrated tree; and
6. report local-work, CI-wait, closeout, and total elapsed time.

Using the cadence quoted by the owner: focused gates per packet, with the broad
Python and 30-check gates only at the final INDIA-2 integration boundary unless
a repository-wide failure forces them earlier.

## 8. Later dependency program

Keep the seven current Dependabot PRs separate from INDIA-2. Refresh them as
five compatibility groups rather than merging stale branches independently:

1. Python typing: #715 and #717 together;
2. ESLint 10 toolchain: #683 and #713 together;
3. React build major: #684, held until Vite/toolchain compatibility is proved;
4. Node type/runtime policy: #714, held while runtime remains Node 24; and
5. Framer Motion 13: #716 with focused live motion verification.

Closing or superseding any old PR requires explicit owner approval. Each actual
upgrade uses a fresh lane, focused compatibility hypothesis, owned lockfiles,
complete affected-stack validation, exact-head hosted checks, and its own merge
receipt.

## 9. Required return format

For every packet report: task/status, base/head/tree, source binding, exact
changed paths, focused counts, issues and confirmed/unconfirmed root causes,
implemented correction and proof, retained holds, capability/endpoint truth,
review/release/cleanup boundaries, PR/check/merge receipts, elapsed workflow
time, and the one exact next packet.
