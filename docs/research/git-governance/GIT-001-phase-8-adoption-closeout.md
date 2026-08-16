---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: GIT-001-P8-RECONCILIATION
---

# GIT-001 Phase 8 — Adoption and Preservation Closeout

## Decision

Phase 8 accepts the GIT-7E operating model as adopted with one closeout-
evidence correction. Recent packets used the read-only Git-state authority,
source-bound worktrees, exact-head hosted checks, and squash-tree comparison.
Their final GitHub and tree outcomes are sound. Their stored task-to-Git JSON
files are pre-publication transition snapshots, however, not permanent final-
merge receipts. They correctly become invalid when their time-bound external
observations become stale.

The maintenance rule is therefore explicit: use a handoff receipt only for the
decision boundary and observation time it records. A later closeout observer
must bind the final PR head, hosted checks, merge commit, and merged tree from
fresh evidence. Never rewrite a historical receipt to make it appear current.
The complete machine-readable snapshot is
[`GIT-001-phase-8-adoption-evidence.json`](GIT-001-phase-8-adoption-evidence.json).

No cleanup decision is made. Primary and `e54a` are retained. Every other
pre-existing lane remains `UNKNOWN/HOLD`; none is retirement-ready.

## Exact Phase 7 integration

| PR | Base | Reviewed head | Merge | Tree equality | Hosted result |
|---|---|---|---|---|---|
| #751 | `b91838f5` | `dd1b0ab9` | `6bcbd9d3` | `f1b38e17` = `f1b38e17` | 6 passed, 2 skipped, 0 failed |
| #752 | `6bcbd9d3` | `0690f745` | `96f193bd` | `8f38c8d4` = `8f38c8d4` | 5 passed, 3 skipped, 0 failed |

Both merge commits are reachable from fetched
`origin/main = 86f92ed16164a97b7cbb1edacd64a50a5a71e13d`. This closes the
stale parent claim that GIT-7E implementation remained active.

## Adoption sample

The bounded sample covers combined-family acceptance, STRAP-D, strap-family
acceptance, and planning PR #799.

| Task / PR | Reviewed head | Merge | Tree equality | Hosted result |
|---|---|---|---|---|
| Combined acceptance / #792 | `490b10a8` | `8e039b11` | `873aea4c` = `873aea4c` | 6 passed, 2 skipped, 0 failed |
| STRAP-D / #797 | `c107993b` | `b75daa97` | `af2695a8` = `af2695a8` | 7 passed, 1 skipped, 0 failed |
| Strap acceptance / #798 | `7f480cb5` | `f56e1ec3` | `28698a28` = `28698a28` | 6 passed, 2 skipped, 0 failed |
| Planning / #799 | `81368eae` | `339bad21` | `ecd7fe38` = `ecd7fe38` | 5 passed, 3 skipped, 0 failed |

Each session records `source_bound=true` and completion of exact-head review.
GitHub independently confirms the exact final PR heads and successful required
gates, and local object comparison proves reviewed/merged tree equality and
current-main reachability.

The durable gap is narrower: the session records do not persist an independent
audit result bound to its exact final head and tree. The four named JSON
receipts capture dirty pre-publication states and no final PR/integration
section. Running their maintained validator now fails with the same stale-
evidence hold-set errors. That is correct fail-closed behavior, not receipt
corruption; it means these files cannot be presented as current or final
closeout proof.

## Preservation and disposition

The single canonical worktree census at `2026-08-16T13:41:21Z` reported 62
worktrees including this new packet lane, with no query failure.

| Target | Current evidence | Decision |
|---|---|---|
| Primary `main` | clean at fetched `86f92ed1`, tree `1bb7e448`, exactly equal to `origin/main` | `RETAIN` integration anchor |
| Detached `e54a` | `0fdb48ed`; only `docs/SESSION_LOG.md` dirty; 119 insertions/7 deletions; exact dirty blob differs from main | `RETAIN` untouched |
| Excel planning | clean attached `a0e115e1`; 0 ahead/119 behind; no remote feature ref or PR | `HOLD_UNKNOWN_OWNER` |
| All other pre-existing lanes | no new owner/retention evidence capable of changing prior holds | aggregate `UNKNOWN/HOLD` |
| Phase 8 packet lane | fresh, source-bound, `READY_LOCAL` | retain after closeout unless separately authorized |

For `e54a`, the exact worktree file SHA-256 is
`35903e436ce2bf90752c62ef8e4ae3e162e23f7a4b6ebc97e1ddfbc0a6af3cb9`;
current main is
`9cf3f9c3ec0c321bd8ba25b53153f406e7dcf88be2e4c9915325b566f67c099b`.
Main contains the material GIT-7C1/GIT-7C2 outcome, but the dirty blob is not
identical and the owner explicitly required the lane to remain untouched.

The only fresh classifier pass was therefore the outcome-changing Excel lane.
The caller evidence is
[`GIT-001-phase-8-excel-disposition-evidence.json`](GIT-001-phase-8-excel-disposition-evidence.json).
The inspection-only classifier returned `HOLD_UNKNOWN_OWNER` with
`OWNER_UNKNOWN` and `RETENTION_EVIDENCE_UNKNOWN`. The absence of unique commits,
a remote branch, and a PR does not answer whether the external planning task
still needs its worktree.

## Root cause and recurrence guard

### Historical transition receipts were treated as permanent closeout proof

- Symptom: all four named sample receipts fail current validation, and none
  records its final PR head, hosted checks, merge commit, or merged tree.
- Main-process impact: a later agent could either describe stale evidence as
  current or incorrectly conclude that a successful integration was invalid.
- Confirmed root cause: the plan sampled time-bound pre-publication handoffs as
  though they were immutable final-closeout receipts. The validator correctly
  recomputes freshness and holds; a pre-merge tree also cannot know its future
  squash identity.
- Fix: bind final PR and tree facts in this fresh Phase 8 successor observation
  and clarify the transition-versus-closeout rule in the canonical workflow.
- Proof: PRs #751, #752, #792, #797, #798, and #799 have unchanged reviewed
  heads, no failed hosted checks, equal reviewed/merged trees, and merge commits
  reachable from current `origin/main`; all four old receipts fail only with
  stale authorization/retention hold-set errors.
- Recurrence control: never mutate a historical transition receipt to appear
  current; create a new observation-bound closeout record and bind exact
  hosted/merge identities there.

## Closeout boundary

This packet changes no product, structural arithmetic, capability, endpoint,
release, or professional-approval claim. It mutates no pre-existing branch,
worktree, dirty path, stash, issue, pull request, or GitHub setting. The only
new lane is `codex/git-001-phase8-reconciliation` from fetched current main.

After the unchanged candidate passes focused Git-governance tests, semantic
guidance, links/indexes, quick `10/10`, normal hooks, hosted checks, and merge-
tree verification, GIT-001 Phase 8 is complete with preserved holds. The sole
next packet is `DOC-FRONTMATTER-CONTRACT`.
