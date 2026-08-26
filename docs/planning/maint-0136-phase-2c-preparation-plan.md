---
owner: Main Agent
status: active
last_updated: 2026-08-27
doc_type: spec
complexity: intermediate
tags: [maintenance, cleanup, branches, refs, archives, recovery, git]
---

# MAINT-0136 Phase 2C Preparation

## Outcome

Phase 2C preparation is complete and no deletion has occurred. The canonical
branch-disposition classifier reduced 77 local branches and 237 local refs to
an exact cleanup set of **four merged local branches** and **two matching remote
branches**. The six local refs affected by those actions are frozen under
target-set SHA-256:

`08a68419515cf9f469e8a7bb3d0a1f4e92218c7e086de5bb89c71368093b23c7`

The machine-readable authority is the
[Phase 2C manifest](../verification/maint-0136-phase-2c-manifest.json). Its
status is `PHASE_2C_TARGETS_FROZEN_AWAITING_DIGEST_BOUND_AUTHORIZATION`.

## Exact targets

| Branch | Exact head | Local action | Remote action |
|---|---|---|---|
| `codex/excel-product-planning` | `a0e115e1` | Normal `git branch -d` | Already absent |
| `codex/release-0231-stable` | `09861d3d` | Normal `git branch -d` | Already absent |
| `codex/release-0240a1-publication` | `d3a4d223` | Normal `git branch -d` | Delete exact matching remote |
| `codex/release-smoothness` | `3cec0bd4` | Normal `git branch -d` | Delete exact matching remote |

All four heads are exact Phase 2B-W preserved branches, reachable from live
`origin/main`, unattached to a worktree, clean of any open pull request, present
in the authenticated recovery package, and classified
`RETIREMENT_READY_PENDING_APPROVAL`. The two remote targets match their local
heads exactly. The other two remote branches are already absent.

## Retention result

| Surface | Result | Disposition |
|---|---:|---|
| Local branches | 77 total; 4 targets; 73 held | Preserve all held branches |
| Live remote branches | 81 total; 2 targets | Preserve 79 |
| Local refs | 237 total; 6 affected refs | Preserve 231 |
| Tags | 45 | Preserve all |
| Codex-managed refs | 33 | Preserve all |
| Worktrees | 16 after opening this preparation lane | Preserve all |
| Open pull requests | 10 | Preserve all; zero target overlap |
| Local recovery bundle | 42,922,979 bytes | Preserve exact hash |
| Local Drive-package archive | 92,256,339 bytes | Preserve exact hash |
| Google Drive archive | Owner-only, downloadable, 92,256,339 bytes | Preserve |
| Protected sources | 42 files / 72,025,193 bytes | Preserve exact aggregate |

The principal holds are 58 former worktree branches whose heads are not
integrated into live `origin/main`, 13 branches attached to retained lanes or
outside the backed Phase 2B target set, `main`, and
`codex/release-preflight-alpha-policy`. The last branch is integrated locally
but its local and live remote heads differ, so the canonical classifier retains
it rather than guessing ownership of the mismatch.

Archive cleanup has zero targets. The local bundle and local package are only
about 129 MiB combined and remain the fastest recovery tier; deleting them
would weaken recovery for negligible disk benefit. Tags and Codex-managed refs
are release/application evidence, not Phase 2C clutter.

## Authorization boundary

The owner gave full Phase 2C approval before the immutable target set existed.
That authorizes live inspection, exact manifest preparation, and committing the
preparation evidence. The canonical classifier still requires a separate
exact-target approval before branch deletion.

The required confirmation is:

> I authorize Phase 2C execution for exactly four local branches and two
> matching remote branches, affecting six local refs, under target-set SHA-256
> `08a68419515cf9f469e8a7bb3d0a1f4e92218c7e086de5bb89c71368093b23c7`.
> Use only normal `git branch -d` and exact `git push origin --delete` for the
> frozen branches. Preserve all 73 held local branches, 79 other live remote
> branches, 45 tags, 33 Codex-managed refs, worktrees, pull requests, protected
> sources, and local/Google Drive recovery archives. Stop on any drift.

## Execution contract

Re-fetch without prune and rebuild the whole classification immediately before
execution. The digest, branch names, local heads, remote heads, integration,
worktree attachment, open-PR state, recovery identities, and protected-source
aggregate must match. Delete each exact remote target first so the local branch
remains a fallback if the network action fails; then delete the corresponding
local branch with normal `git branch -d`.

Write an atomic incremental ledger after every mutation. Stop on the first
failure and report exact partial progress. Do not use `-D`, `--force`, prune,
garbage collection, reset, worktree removal, tag deletion, Codex-ref deletion,
archive deletion, PR closure, or broad filesystem deletion.

## Current next action

Wait for authorization bound to the exact digest above. Then execute only the
four local and two remote targets and prove that exactly six named local refs
were removed while every retained surface remains unchanged.
