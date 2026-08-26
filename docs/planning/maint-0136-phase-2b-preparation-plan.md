---
owner: Main Agent
status: active
last_updated: 2026-08-26
doc_type: spec
complexity: intermediate
tags: [maintenance, cleanup, worktrees, recovery, git]
---

# MAINT-0136 Phase 2B Preparation Plan

## Decision

Phase 2B is prepared but is **not authorized and should not execute yet**.
The live evidence separates two very different cleanup surfaces:

1. The remaining exact small-cache ceiling is 119 directories and 47,378,432
   bytes (45.18 MiB), only 0.4165% of the current worktree footprint. A separate
   deletion session would provide negligible disk relief and is not recommended.
2. Sixty-four clean, non-special worktrees are eligible only for retirement
   review and occupy 7,753,789,440 gross path bytes (7.22 GiB). Every one has
   ignored local state, and the full topology contains 3,190 ignored entries.
   Sixty-seven worktrees contain ignored session state and 67 contain ignored
   pipeline state. Removing worktrees before preserving and restore-testing
   that state could lose evidence even when the tracked branch is recoverable.

The machine-readable authority is the
[Phase 2B preparation manifest](../verification/maint-0136-phase-2b-preparation-manifest.json).
Its status is `PHASE_2B_PREPARED_NOT_AUTHORIZED` and its recommendation is
`DO_NOT_EXECUTE_PHASE_2B_YET`.

## Frozen live facts

| Surface | Observed result | Disposition |
|---|---:|---|
| Phase 2A predecessor | `2d898e9b`; 30/30 targets remain absent | Retain immutable |
| Disk | 35.12 GiB available; 84% reported capacity | Stable enough to avoid low-value cleanup |
| Worktrees | 75 / 10.59 GiB total | No removal authorized |
| Retirement-review rows | 64 / 7.22 GiB gross | Recovery and ownership hold |
| Detached rows | 6 clean plus dirty `e54a` | Owner/unique-work hold |
| Open pull requests | 10; Phase 1 PR #874 included | Excluded |
| Remaining small caches | 119 / 45.18 MiB | Skip recommended; not authorized |
| Protected sources | 42 files / 72,025,193 bytes | Unchanged and excluded |
| Off-device destination | Unavailable | Worktree-removal hold |

The disk percentage moved from 83% during the first recheck to 84% at manifest
freeze because filesystem accounting and percentage rounding changed while the
machine remained active. No Phase 2B deletion occurred.

## Why the original broad Phase 2B should be split

Worktree removal, branch/ref deletion, and small-cache deletion have different
recovery and value profiles. Combining them would make review harder and could
turn a recoverable tracked branch into accidental loss of ignored local state.

The efficient order is therefore:

1. **Phase 2B-R — recovery and retention preparation.** Establish a usable
   encrypted external or off-device destination. Copy the all-ref bundle,
   detached dirty patch, protected-source archive, and per-worktree ignored
   session/pipeline state. Restore-test representative and unique material.
2. **Phase 2B-W — exact worktree retirement.** Reinspect topology and current
   tasks, then freeze only exact clean worktree paths whose owner retention is
   confirmed, whose pull request is not open, whose branch is remotely
   recoverable or integrated, and whose ignored-state archive restores.
   Preserve every branch and ref during this packet.
3. **Phase 2C — branch/ref/archive review.** Consider this only after the
   retained worktree result is stable. It has little immediate disk value and
   requires its own exact authorization. No prune or automatic archival is
   proposed.

The 119 small caches may be included in a later authorized worktree-retirement
packet, where their deletion is incidental to a higher-value removal. Running a
standalone small-cache sweep now would repeat coordination and verification for
only 45.18 MiB.

## Phase 2B-R acceptance criteria

All of these must pass before an executable worktree target set is frozen:

- the external/off-device destination is mounted, encrypted, writable, and has
  sufficient verified free space;
- the existing all-ref bundle and `e54a` patch are copied off-device and their
  SHA-256 values match the Phase 1 evidence;
- ignored `logs/sessions`, `logs/pipelines`, trust/evolution state, benchmarks,
  and any other non-cache ignored material are archived per exact worktree;
- protected sources are backed up without tracking or exposing protected paths,
  prose, or filenames, and their aggregate digest is unchanged;
- at least one managed restore proves the ignored-state archive can be opened
  and matches its source digest;
- fresh `git_state.py --json --worktrees` has zero query failures and no
  operation/conflict in any proposed lane;
- every proposed lane has confirmed owner-retention disposition, no open pull
  request, zero dirty paths, and an exact remote head or integrated commit; and
- Phase 1 PR #874 and the Phase 2A candidate have reached a publication state
  that does not make successor ordering ambiguous.

## Exact execution boundary for a later authorization

A later Phase 2B-W authorization must bind to an immutable target manifest and
state its target count, gross bytes, and target-set SHA-256. It may authorize
only `git worktree remove` for those exact clean paths after all preconditions
are rechecked. It must continue to prohibit:

- removing the primary checkout, current task, Phase 1 or Phase 2A predecessor,
  dirty `e54a`, detached/unknown-owner lanes, or any open-PR lane;
- deleting local or remote branches, refs, archives, protected sources, the
  shared `.venv`, or pull requests;
- `git clean`, reset, prune, force push, or filesystem-recursive deletion; and
- proceeding after target, head, ignored-state, PR, recovery, or topology drift.

Suggested later wording, only after the acceptance criteria pass:

> I authorize Phase 2B-W worktree retirement for only the exact frozen target
> manifest and target-set digest presented to me. Preserve all branches, refs,
> pull requests, archives, protected sources, the shared `.venv`, excluded
> lanes, and stop on any drift.

That wording is not the current authorization. The current task authorizes
preparation evidence only.

## Stop conditions

Stop without removal if the recovery destination disappears, a digest or
restore check fails, a target becomes dirty or active, a PR opens, a Git
operation appears, a remote head changes, ignored state is not archived, a path
is a symlink or escapes its worktree, or predecessor publication order changes.

## Current next action

Phase 2B-R Google Drive backup and authenticated restore now pass under the
[backup closeout](maint-0136-phase-2b-r-google-drive-backup-closeout.md). Do not
run the 119-target low-value cache sweep. Next prepare Phase 2B-W by rechecking
the 64 exact lanes, resolving owner retention and remote/integration state, and
freezing a worktree-only manifest. Worktree removal and every branch/ref/archive
cleanup remain separately held until a new explicit authorization. The paused
20-minute GitHub heartbeat is not needed for this local work and should remain
paused until a deliberate PR #874 status recheck is requested.
