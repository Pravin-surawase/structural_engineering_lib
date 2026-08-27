---
owner: Main Agent
status: active
last_updated: 2026-08-26
doc_type: spec
complexity: intermediate
tags: [maintenance, cleanup, git, preservation, recovery]
---

# MAINT-0136 Cleanup Preservation Plan

## Decision

The owner authorized Phase 0 and Phase 1 only. Those phases reconcile the
existing session ledger, inspect current topology, preserve unique work, prove
local recovery, and freeze an exact manifest. They do not delete a file, cache,
worktree, branch, remote ref, or pull request.

The machine-readable authorities are:

- [cleanup preservation manifest](../verification/maint-0136-cleanup-preservation-manifest.json);
- [cleanup recovery evidence](../verification/maint-0136-cleanup-recovery-evidence.json); and
- the later immutable-candidate
  `maint-0136-cleanup-preservation-git-handoff-receipt.json`.

Historical cleanup evidence is comparison material only. Its old retirement
decisions are not promoted to current authority.

## Phase 0 result — ledger reconciliation

The unmatched `ARCH-FOCUS-REVIEW-001` start was closed against its inspected
head `e2fac7419551988def59101ac63a5f8e491bc7a2`. The closeout truthfully records
zero mutations, zero verification reruns, zero hosted runs, and all elapsed
time in contract/intake. The active-session query then returned no unmatched
session.

## Phase 1 result — current preservation baseline

The frozen baseline was observed on 2026-08-26 from fresh hosted and local
`main` identity `ee04bfbf76b1a3a022d07c8203b5274a0f71998f`.

| Surface | Observed result | Phase 1 disposition |
|---|---:|---|
| Worktrees | 73 total; 72 pre-existing; 7 detached | Primary, current task, and dirty lane retained; 70 held |
| Dirty worktrees | 2 at freeze; 1 pre-existing | Current task writes retained; detached `e54a` preserved with verified patch |
| Worktree disk use | 17.587 GiB | Measured only; no removal |
| Current local/remote branch or PR heads | 83 | `main` and current task retained; 81 held |
| Remote branch heads | 80 | No remote deletion or prune |
| Open-PR branch rows | 9 | Preserved; no PR closure |
| Existing cache paths | 157 / 7.698 GiB | Inventoried only |
| Clean inactive Phase 2 cache ceiling | 149 / 7.183 GiB | Candidate only; not authorized |
| Filesystem free space | 27.900 GiB; 87% used | No emergency deletion justified |

The 7.183 GiB Phase 2 ceiling is dominated by 16 inactive
`react_app/node_modules` directories (6.531 GiB) and 14 inactive
`.mypy_cache` directories (0.608 GiB). The remaining candidate caches are
small pytest, Ruff, and React build outputs. The primary runtime, current task
runtime, and every dirty-lane runtime remain excluded.

## Recovery proof

The same-disk recovery directory is ignored under
`private_sources/worktree_cleanup_archives/maint-0136-20260826T144500Z`.

- The 40.93 MiB all-ref Git bundle has SHA-256
  `c57240f207b5730de92b9d27d5d64a819a89e0b0496d92351f4eec580c637dac`,
  contains 303 refs and complete history, and passes `git bundle verify`.
- The 7,146-byte detached-worktree patch has SHA-256
  `cf70f18f57ea3c7e14c85fe06cdd00d0171ac65da42dce08eef6a286b4930394`.
  A temporary clone checked out its exact base, passed `git apply --check`,
  applied the patch, passed `git fsck --full --no-dangling`, and reproduced the
  dirty `docs/SESSION_LOG.md` SHA-256 exactly.
- The ignored protected-source surface contains 42 files and 72,025,193 bytes
  outside the recovery/archive and Python-cache exclusions. Zero paths are
  Git-tracked. An exact temporary copy passes the private library verifier, and
  the canonical aggregate remains unchanged during that proof.

The recovery directory is on the same physical disk. Time Machine reports no
configured destination and no external volume is available, so this evidence
is `LOCAL_RECOVERY_VERIFIED_OFF_DEVICE_HOLD`, not disaster-recovery proof.

## Efficiency and correctness controls

Phase 1 uses one generator and three focused regression tests to keep later
refreshes deterministic. The collector:

1. consumes the canonical read-only `git_state.py --json --worktrees` result;
2. refreshes remote heads, hosted `main`, and pull-request associations once;
3. measures each live worktree and only known cache roots;
4. fails closed to retention/hold dispositions; and
5. verifies recovery in managed temporary directories that are removed on
   exit.

The private verifier initializes and commits its SQLite schema even in
`verify` mode, which changes database bytes. MAINT-0136 therefore verifies an
exact temporary copy and proves the canonical aggregate is unchanged, rather
than running that command against the canonical database during evidence
freeze.

## Phase 2 gate — not authorized

No cleanup execution may begin from this plan alone. A later Phase 2 requires:

1. a usable encrypted external or off-device recovery destination, or an
   explicit owner decision accepting the narrower recovery tier;
2. a fresh topology and current-PR reinspection;
3. separate owner authorization bound to exact cache/worktree/branch targets;
4. exclusion of the primary checkout, active task, dirty `e54a` lane, open PRs,
   unknown owners, protected sources, and shared `.venv`; and
5. recoverable execution with before/after evidence and no broad `git clean`,
   reset, force push, ref deletion, or prune.

Until those gates pass, the correct outcome is preservation, not deletion.
