---
owner: Main Agent
status: active
last_updated: 2026-08-22
doc_type: spec
complexity: advanced
tags: [safety, validation, websocket, boq, packaging, react]
---

# LIB-PRO-005 Release-Safety Closure Plan

## Goal

Close the reproduced release-safety defects found after `LIB-PRO-004` without
turning the diagnostic inventory into a claim that every unproven parameter is
a confirmed bug. Preserve the truthful `PARTIAL` readiness verdict until the
remaining public-surface evidence is assigned and qualified engineering review
is complete.

## Source and authorization boundary

- Source base: merged PR #836 at
  `f1a9937cfdba4c72c22e6219ffaf02f94809f1a5`.
- Task branch: `codex/lib-pro-005-release-safety-closure`.
- Authorized: bounded implementation, tests, documentation, commit, push, PR,
  required checks, and eligible exact-head merge.
- Excluded: tag, package publication, GitHub Release, branch/worktree deletion,
  professional approval, ETABS, and new engineering capability.

## Frozen dispositions

| Audit item | Required action |
|---|---|
| Empty WebSocket beam design | Require all nine calculation-bearing inputs and run no calculation when any is missing. |
| Missing BOQ concrete rate | Use the documented default table only when the whole table is omitted; reject every uncovered used grade. Price mixed-grade stories from exact per-beam rates. |
| Unsafe lower-level scalars | Reject booleans and non-finite values in equivalent shear, development length/bond stress, and beam outline at their actual calculation boundary. |
| Experimental PMM dependency | Declare NumPy as the installable `pmm` extra and provide an actionable missing-extra error. |
| Root API omissions | Publish the four already-supported workflow-catalogue symbols through the recommended package root. |
| React status loss | Preserve the server's canonical fail-closed `BLOCKED`, `ERROR`, `NOT_EVALUATED`, `STALE`, and `HOLD` statuses. |
| Performance threshold claim | No code change: the standalone workflow is intentionally parked and FastAPI load tests already enforce thresholds. This packet must not add a flaky PR microbenchmark gate. |
| Excel CI skip claim | No workflow change: path-aware skipping is intentional and the required PR gate owns the decision. Run the 21 local tests in cumulative verification. |
| Stale documentation counts | Apply only the two replacements identified by `sync_numbers.py`; do not rewrite immutable historical release statistics. |

## Verification sequence

1. Run focused Python, FastAPI, React, audit-truth, packaging, and public-entry
   tests after the implementation batch.
2. Build one exact wheel and prove minimal root import plus `pmm` extra import in
   clean environments.
3. Run the maintained one-storey comparison/manual arithmetic evidence and the
   public-route safety gate.
4. Freeze evidence, session records, handoff receipt, and affected indexes.
5. Run one consolidated quick/full repository sequence, normal hooks, exact
   candidate review, required hosted PR checks, and eligible merge.

Any changed outcome after the freeze reopens only its affected focused evidence
and the consolidated gate. Diagnostic `UNPROVEN` rows remain a successor
evidence backlog, not an instruction to patch 361 parameters blindly.
