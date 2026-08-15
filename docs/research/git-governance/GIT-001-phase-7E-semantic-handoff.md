---
owner: Main Agent
status: active
last_updated: 2026-08-15
doc_type: spec
task: GIT-7E
---

# GIT-7E — Semantic Live Guidance and Durable Git Handoff

## Exact boundary

GIT-7E started at `2026-08-15T09:12:34Z` on
`codex/git-7e-semantic-handoff` from freshly fetched and independently verified
`origin/main = b91838f594a04aff1d21c43bf6f87a64710b0748` (merged PR #750).
It changes instruction coherence and task handoff only. GIT-7D1/GIT-7D2,
retirement classification, preserved lanes, remote refresh, deletion, release,
and product/IS-code behavior remain unchanged.

## Semantic rules

`docs/git-automation/live-git-guidance-index.json` deterministically discovers
maintained exact files, globs, and active indexed guide entries. An indexed
deprecated entry is historical only when its opening text explicitly identifies
it as historical, archived, or legacy. Repository archives are excluded by
named paths. A file cannot silently escape validation merely by containing a
deprecated metadata field.

The semantic checker rejects live guidance that restores retired wrappers,
cleanup entrypoints, destructive recovery, non-Codex task branches, direct
lifecycle ownership, or remote-current claims based on `NOT_CHECKED`. Required
contracts bind maintained session and handoff surfaces to `git_state.py`, the
receipt, source-bound runtime diagnosis, inspection-only disposition, explicit
unknowns, and reasoned `NOT_APPLICABLE`.

## Receipt contract

`scripts/git_handoff_receipt.py` is a read-only evidence consumer. It obtains
local Git facts only through `scripts/git_state.py`; it contains no independent
Git or network query and performs no fetch, prune, ref, worktree, or GitHub
mutation. Caller-supplied hosted evidence is accepted only when fresh,
query-successful, structurally complete, and exact-head-bound.

The versioned JSON receipt records:

- task, integration owner, and owned/shared/forbidden paths;
- local branch, full head, upstream, base relation, worktree, dirty state,
  operation, source identity, and a canonical local-state hash;
- remote identity/freshness or explicit `NOT_CHECKED`;
- PR number/state/base/head/merge state and exact-head required checks;
- reviewed base/head/tree and squash tree-equivalence evidence;
- retention owner/decision/holds, while marking task archive state as never
  Git-retention evidence; and
- authorized/prohibited actions plus the exact next-action boundary.

Missing, malformed, stale, query-failed, contradictory, or unreasoned
`NOT_APPLICABLE` evidence yields `UNKNOWN`/`HOLD`. A squash merge is content
evidence only when reviewed and merged trees match; it never implies ancestry
or retirement authority. `session handoff` persists the receipt path/hash and
identity summary, and `session end` validates its schema, hashes, freshness,
contradictions, and round trip.

## Validation boundary

Focused regressions cover all six Phase 5 scenarios: live contradiction
rejection, coherent guidance, explicit archive/historical handling, local
identity round trip, exact hosted evidence or unknown holds, archive/retention
separation, and maintained aliases. The packet must also pass the semantic Git
workflow check, strict documentation/index checks, quick 10/10, full 30/30,
efficiency, and session-end validation.

Opening a draft PR is authorized after local green. Ready/merge is held until
the supervising orchestrator independently audits the exact PR base, head, and
tree. Feature branch/worktree retention remains required; no cleanup or
deletion is part of this packet.
