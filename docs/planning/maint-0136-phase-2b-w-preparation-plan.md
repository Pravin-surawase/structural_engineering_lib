---
owner: Main Agent
status: active
last_updated: 2026-08-27
doc_type: spec
complexity: intermediate
tags: [maintenance, cleanup, worktrees, recovery, git]
---

# MAINT-0136 Phase 2B-W Worktree Preparation

## Outcome

Phase 2B-W preparation froze **63 exact worktree targets** totaling
**7,686,279,168 gross bytes (7.16 GiB)**. The immutable target-set SHA-256 is:

`543a5f1b9298bd47e2f0b743f046fdd2c76dfd8c0f358ed0c604b57ffb6129da`

The machine-readable authority is the
[Phase 2B-W preparation manifest](../verification/maint-0136-phase-2b-w-preparation-manifest.json).
Its status is
`PHASE_2B_W_TARGETS_FROZEN_AWAITING_DIGEST_BOUND_AUTHORIZATION`. No worktree,
cache, branch, ref, pull request, archive, protected source, or shared `.venv`
was removed during preparation.

## Live decision

| Surface | Result | Disposition |
|---|---:|---|
| Live worktrees | 78 | Fully inventoried |
| Verified backup mappings | 64 | Exact package mapping retained |
| Frozen targets | 63 / 7,686,279,168 bytes | Await digest-bound authorization |
| Backed recovery hold | 1 | Retain `codex/git-governance-research` |
| Live lanes outside backup mapping | 14 | Retain |
| Open pull requests | 10 | No target overlap |
| Active Codex tasks targeting a frozen path | 0 | Inactivity gate passes |
| Drive backup | 92,256,339 bytes | Owner-only, downloadable, restore PASS |

The one backed hold is not remotely recoverable at its exact head and is not
integrated into live `origin/main`; removing that worktree could therefore
make its current checkout materially harder to recover. The 14 unbacked live
lanes include the primary checkout, seven detached lanes, and the MAINT-0136
predecessor/current lanes. They are not eligible for this packet.

## Exact target gates

Every frozen target satisfies all of these conditions:

1. its exact path, branch, head, and ignored-state aggregate match a worktree
   mapping inside the authenticated, restore-tested Google Drive package;
2. it is a canonical directory, clean, inactive, and has no Git operation;
3. its branch has no open pull request;
4. its head is either the exact live remote branch head or is integrated into
   live `origin/main`; and
5. the owner disposition is to retire only the worktree while preserving its
   branch, refs, backup, and recovery evidence.

The target selector has no removal code path. Six focused regressions prove
remote/integrated selection, dirty-lane hold, open-PR hold, ignored-state drift
hold, local-only recovery hold, and backup-identity rejection.

## Authorization boundary

The owner gave general cleanup and deletion approval before the exact target
set existed. That authorizes this preparation and records the intended owner
retention disposition, but it cannot prove that the owner reviewed this exact
63-path digest. Execution therefore remains held until the following exact
authority is confirmed:

> I authorize Phase 2B-W execution for exactly 63 worktrees totaling
> 7,686,279,168 gross bytes under target-set SHA-256
> `543a5f1b9298bd47e2f0b743f046fdd2c76dfd8c0f358ed0c604b57ffb6129da`.
> Use only non-force Git worktree removal. Preserve all branches, refs, pull
> requests, backups, protected sources, the shared `.venv`, the one backed
> hold, and all 14 unbacked live lanes. Stop on any drift.

This confirmation authorizes worktree removal only. Branch/ref/archive cleanup
remains Phase 2C, and the standalone 119-directory small-cache sweep remains
skipped as low value.

## Execution and stop contract

Before any removal, revalidate the whole manifest against live topology,
current task activity, open pull requests, remote heads, local cleanliness,
ignored-state aggregates, and the verified backup identity. Remove a target
only through normal non-force `git worktree remove`; never use filesystem
recursive deletion or `--force`.

Stop before or during execution if any target path, branch, head, size,
ignored-state aggregate, open-PR state, operation, remote/integration proof,
backup identity, or target-set digest changes. A stopped packet must retain all
unprocessed worktrees and report exact partial progress without deleting any
branch or ref.

## Current next action

Obtain the digest-bound authorization above. Then execute only the 63 frozen
targets with per-target prechecks and before/after evidence. Do not start Phase
2C or the small-cache-only sweep.
