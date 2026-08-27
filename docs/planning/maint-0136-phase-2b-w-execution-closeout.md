---
owner: Main Agent
status: archived
last_updated: 2026-08-27
doc_type: log
complexity: intermediate
tags: [maintenance, cleanup, worktrees, recovery, git]
---

# MAINT-0136 Phase 2B-W Execution Closeout

## Outcome

Phase 2B-W is complete. After a full no-mutation preview, the owner-authorized
executor removed exactly **63 worktrees** totaling **7,686,279,168 gross bytes
(7.16 GiB)** under target-set SHA-256
`543a5f1b9298bd47e2f0b743f046fdd2c76dfd8c0f358ed0c604b57ffb6129da`.
Every removal used normal `git worktree remove` without `--force`; all 63 target
paths are absent and all 63 local branches remain at their frozen heads.

The machine-readable authority is the
[Phase 2B-W execution evidence](../verification/maint-0136-phase-2b-w-execution-evidence.json).
Its final status is `PASS`, with no partial-execution or post-execution failure.

## Preserved recovery and identity

| Surface | Before | After | Result |
|---|---:|---:|---|
| Live worktrees | 78 | 15 | Exact 63-target reduction |
| Local refs | 236 / `412bfa5c...bd16` | 236 / `412bfa5c...bd16` | Exact match |
| Protected sources | 42 files / 72,025,193 bytes / `a65d2fbc...bee4` | Exact match | Preserved |
| Local recovery archive | 92,256,339 bytes / `bf18a66b...67ac` | Exact match | Preserved |
| Drive recovery | Owner-only, downloadable, authenticated restore PASS | Reconfirmed unchanged | Preserved |
| Filesystem available | 36,361,379,840 bytes | 44,282,273,792 bytes | +7,920,893,952 bytes |
| Reported capacity | 84% | 81% | Lower after cleanup |

The filesystem increase can differ from the frozen gross path sum because APFS
accounts for shared blocks and concurrent/deferred changes. The authoritative
cleanup quantity is the exact target sum recorded in the manifest and per-row
execution ledger.

## Mutation boundary

The packet performed 63 worktree removals and zero branch deletions, ref
deletions, pull-request closures, archive deletions, protected-source deletions,
or separate cache deletions. The 119 small-cache paths from the prior review are
now absent because they lived inside the authorized worktree paths; no
standalone cache sweep was run.

No reset, clean, prune, force push, filesystem-recursive worktree deletion, or
shared-`.venv` deletion occurred. `git fsck --full` exits successfully. Its
dangling-object notices are retained unreachable history, not missing objects;
no garbage collection or pruning was performed.

## Retained topology

The 15 remaining worktrees are intentionally retained:

- the primary `main` checkout;
- seven detached Codex lanes, including the pre-existing dirty `e54a` lane;
- the backed recovery hold `codex/git-governance-research`; and
- six MAINT-0136 predecessor/current evidence lanes through this execution
  candidate.

The removed checkouts remain recoverable through their preserved exact local
branches, exact remote or integrated tracked heads, and the owner-only Drive
archive containing their ignored state. Phase 2C branch/ref/archive review is a
separate, low-disk-value decision. Its
[preparation plan](maint-0136-phase-2c-preparation-plan.md) now freezes four
local and two matching remote branch targets while retaining all archives,
tags, Codex-managed refs, worktrees, and other branches.

## Current next action

Phase 2C later completed under its exact digest-bound authorization. See the
[Phase 2C execution closeout](maint-0136-phase-2c-execution-closeout.md). Do not
perform any additional branch, ref, archive, worktree, pull-request, tag, or
Codex-ref cleanup without a new exact manifest and authorization.
