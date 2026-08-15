# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-16
- Focus: Establish one durable INDIA-0 through INDIA-4 finish plan before any new calculation work begins.
- Git receipt: docs/verification/india-completion-plan-git-handoff-receipt.json | sha256:5d5255d0098303e2ee2663d011cddad3cbdbba292eb013cd6640b37b207746a8 | HOLD
- Git identity: codex/india-finish-plan-reconcile@ca65c165ba3abc23497f15ba5e305f2324b91191 | upstream=NONE@UNKNOWN | base=origin/main@62f4ba06b6287c1b74ddd41e7cdfefa71b08e515 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=OBSERVED
- Next action: WAIT_FOR_EXACT_HEAD_AUDIT
<!-- HANDOFF:END -->

**Date:** 2026-08-16

| Release state | Target |
|---|---|
| **Current** | `v0.23.1a1` Alpha; INDIA-0, INDIA-1, and the INDIA-2-STAIR family are complete |
| **Program** | Umbrella INDIA-2 remains in progress; INDIA-3 and INDIA-4 remain planned |
| **Next** | Discuss `INDIA-2-WALL-G0`; no wall implementation, release, or new stair scope is activated |

## Required Reading

1. [Canonical Indian-code completion waves](indian-code-completion-plan.md)
2. [Generated Indian-code manifest](../verification/indian-code-capability-coverage.json)
3. [Current task board](../TASKS.md)
4. [INDIA-2 staircase cumulative evidence](../verification/india-2-cumulative-gate-evidence.md)
5. [Canonical Git workflow](../git-automation/git-workflow-single-source.md)

## Start Boundary

The historical INDIA-2A-D packets and their cumulative software gate are the
completed `INDIA-2-STAIR` family. Do not reopen them, add another stair topology,
add React, or begin release work without a new owner-approved scope.

The next conversation is a decision packet, not implementation: decide whether
to start `INDIA-2-WALL-G0` and freeze exactly one practical Clause 32 wall case,
its controlled source, independent benchmark, explicit units and assumptions,
unsafe/out-of-domain cases, and retained exclusions.

```bash
./run.sh session brief --agent orchestrator
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
./scripts/python_runtime.sh scripts/generate_indian_code_manifest.py --check
```

Require a clean fresh branch from verified current `origin/main` and
`source_bound=true`. Preserve every unrelated worktree. Branch, remote-ref, or
worktree cleanup remains a separate exact-target authorization.

## INDIA-2-WALL-G0 decision exit

The decision packet ends with GO or HOLD. A GO must identify one supported wall
case, governing standard edition and provisions, lawful source provenance, an
independent benchmark with tolerance, calculation inputs/outputs, fail-closed
boundaries, and the proposed pure-math implementation packets. A HOLD must state
the missing evidence or unresolved scope decision. It must not add calculation
code, API, UI, or public capability claims.

## Review and gate boundary

Each calculation packet still requires focused tests, benchmarks, architecture
and PR checks, plus the quick gate. The expensive full Python and 30-check gate
runs once at the milestone boundary unless an outcome-changing repository-wide
issue appears earlier.

Cumulative qualified structural-engineering review belongs to INDIA-4 after the
accepted INDIA-2 and INDIA-3 scope is frozen. Packet-level source and engineering
checks still occur before each implementation GO. Software completion does not
grant professional approval, stable-release authorization, engineering-use
authorization, or cleanup authority.
