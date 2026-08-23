# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-23
- Focus: Consolidate duplicate scanners and retire obsolete compatibility scripts.
- Git receipt: docs/verification/maint-012d-git-handoff-receipt.json | sha256:ceecfafee7f0f24b5964ad63f04b33917ffb0bfb7d1d2998bf4de67a188786fd | HOLD
- Git identity: codex/maint-012d-scanner-consolidation@84f3cbe6ce576a6c3a22882ddec2e1c08415c4e0 | upstream=origin/main@84f3cbe6ce576a6c3a22882ddec2e1c08415c4e0 | base=origin/main@84f3cbe6ce576a6c3a22882ddec2e1c08415c4e0 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | `MAINT-012D` is complete on merge: one-owner scanner/script contracts, preserved safety scanners, and no active executable bridge paths |
| **Next** | Require the frozen candidate's broad Python, quick/full, ordinary-hook, and hosted proof; after merge, start no successor without explicit selection |
| **Why** | Old executable bridges, duplicate registry operations, dormant hooks, and linked-worktree-broken health scripts kept adding discovery and verification cost |
| **Held** | Distinct engineering safety scanners; product/structural/API/UI/Excel/ETABS behavior; dependencies; publication; settings; branch deletion; and professional approval |

## Exact MAINT-012D state

- Branch: `codex/maint-012d-scanner-consolidation`, created from exact merged
  `origin/main` commit `84f3cbe6ce576a6c3a22882ddec2e1c08415c4e0`.
- Canonical target: 115 active operations, no deprecated bridge operation, and
  102/102 active top-level scripts represented by `scripts/control-plane.json`.
- Sixteen obsolete files are archived without redirect stubs. Old Git/index,
  OpenAPI, WIP, link-fix, and health intent resolves to canonical aliases.
- The local/nightly OpenAPI path now performs one full-spec comparison and
  ignores only `info.version`.
- Historical logs, audits, research, receipts, and explicit retirement
  sentinels retain their original path text.
- Readiness, error handling, input validation, function quality, public-route
  safety, and maintained agent-evolution scanners remain separate.
- After merge, no calendar refresh is needed. Reassess only when callers,
  ownership, runtime, false-result evidence, or requested archive reuse changes.

## Required Reading

1. [MAINT-012 modernization plan](maint-012-control-plane-modernization.md)
2. [Current task board](../TASKS.md)
3. [Git workflow single source](../git-automation/git-workflow-single-source.md)
