# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-09-02
- Focus: Complete urgent repository hygiene and record deferred performance work.
- Git receipt: docs/verification/repository-hygiene-closeout-git-handoff-receipt.json | sha256:b70205b0e0e85bf8a842738af1e71ac555e280ada31b9b3705e374def75870bc | HOLD
- Git identity: codex/repository-hygiene-closeout@30395bc1111aee72f3bfc385e4cff9c0e9479609 | upstream=origin/main@742719dd3f6c1e30c023e7585e9ea00d13b60fc2 | base=origin/main@742719dd3f6c1e30c023e7585e9ea00d13b60fc2 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Current boundary

The offline B1B/B2 candidate-convergence batch is accepted through PR #950 at
merge `742719dd`. The owner then authorized the next bounded A1/C1 milestone.
Branch `codex/w3-installed-readonly-evidence` started from current
`origin/main`; ETABS 23.3.1 and API 2.16.0 are installed, but no ETABS process
was running at preflight, so live attachment/export truthfully remains `HOLD`.
The exact-process A1 transport and C1 read-only SQLite schema inventory are now
implemented and pass their focused fake/static checks; no COM object was made.

| State | Next action / claim boundary |
|---|---|
| **Current** | A1 exact-process preflight/supervised getter capture and C1 immutable SQLite schema inventory are implemented on `codex/w3-installed-readonly-evidence`. Focused tests, Ruff, Black and configured mypy pass; the installed preflight records zero application calls and `HOLD_NO_RUNNING_TARGET`. |
| **Next** | Open the intended saved ETABS model, record its exact PID/start/path/version, refresh the preflight, then run one bounded getter-only A1 capture. If preservation passes, acquire the C1 create-new SQLite file through the operator UI and inventory it offline. |
| Commit lane | Exactly the three accepted mutation-safety hooks from PR #949; no broad gate is repeated per commit. |
| PR lane | Formatting, linting, typing, security, tests, generated contracts, docs and API parity run once for the complete batch. |
| W3 state | A0/B0/B1A/C0 is accepted through PR #947 and B1B/B2 through PR #950. A1/C1 is active under getter-only/create-new-export authority; its live evidence is not yet acquired. |
| Held | C2 until C1 supplies the exact accepted schema; setters, save, unlock, analysis/design run, application exit, model mutation, Excel automation, original-model changes, release/publication, and unrelated worktree or branch cleanup. |

## Next decision order

1. Have the operator open the intended saved ETABS model; do not launch or
   select a model automatically.
2. Re-run the no-COM process/runtime preflight immediately before installed
   work and require exact PID, start time, model path/name and version.
3. Run the supervised attached observation getter-only. Acquire C1 by operator
   UI into a new
   destination and prove pre/post model, file and state preservation.
4. Do not start C2 until C1 supplies the complete accepted hash-bound export and
   exact schema inventory.

## Cleanup state

- Urgent cleanup removed 40 clean merged-PR worktrees and 266 closed/merged-PR
  cache records. Five protected worktrees, all branches, open-PR/default-branch
  caches and dirty user work remain.
- No task-owned stale Python/test/dev/ETABS/Excel process remained. Codex/MCP
  and remote-desktop helpers are unrelated and must remain running.
- The hygiene-documentation worktree was removed after PR #951 was accepted;
  its branch remains preserved because deletion was not authorized.
- The dirty Excel-pilot and W3F live-foundation worktrees are suspended
  preservation lanes with zero commits ahead and overlapping historical docs.
  Preserve their exact dirty files and rebind deliberately before resumption;
  do not merge, reset, stash or rebase them as cleanup.

## Required Reading

1. [W3 and professional beam integrated plan](w3-beam-professional-integrated-execution-plan.md)
2. [Current task board](../TASKS.md)
3. [Newest session entry](../SESSION_LOG.md)
4. [Canonical Git workflow](../git-automation/git-workflow-single-source.md)
5. [Commit and PR validation consolidation plan](commit-pr-validation-consolidation-plan.md)
