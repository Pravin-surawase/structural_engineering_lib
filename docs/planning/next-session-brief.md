# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-16
- Focus: Accept the bounded wall family from integrated A-D using cumulative focused gates and retain its exclusions.
- Git receipt: docs/verification/india-2-wall-acceptance-git-handoff-receipt.json | sha256:560e669e73f4aba0ab2ff87c5ce55863d3ef2d5752264b3dbb1a5db14c927670 | HOLD
- Git identity: codex/india-2-wall-acceptance@46094a8c35c75fcfb0644f23a851087cc3297c60 | upstream=NONE@UNKNOWN | base=origin/main@46094a8c35c75fcfb0644f23a851087cc3297c60 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=OBSERVED
- Next action: WAIT_FOR_EXACT_HEAD_AUDIT
<!-- HANDOFF:END -->

**Date:** 2026-08-16

| Release state | Target |
|---|---|
| **Current** | `v0.23.1a1` Alpha; INDIA-0, INDIA-1, and the INDIA-2-STAIR family are complete |
| **Program** | Umbrella INDIA-2 remains in progress; INDIA-3 and INDIA-4 remain planned |
| **Next** | Run `INDIA-2-DEEP-G0`; do not write deep-beam calculation code unless its source/scope/benchmark decision is GO |

## Required Reading

1. [INDIA-2 remaining-elements execution plan](india-2-remaining-is456-elements-plan.md)
2. [Canonical Indian-code completion waves](indian-code-completion-plan.md)
3. [Generated Indian-code manifest](../verification/indian-code-capability-coverage.json)
4. [Current task board](../TASKS.md)
5. [INDIA-2 staircase cumulative evidence](../verification/india-2-cumulative-gate-evidence.md)
6. [Canonical Git workflow](../git-automation/git-workflow-single-source.md)

## Start Boundary

The historical INDIA-2A-D packets and their cumulative software gate are the
completed `INDIA-2-STAIR` family. Do not reopen them, add another stair topology,
add React, or begin release work without a new owner-approved scope.

`INDIA-2-WALL` is accepted through one regular 100-200 mm thick, one-grid,
braced empirical vertical-compression workflow. WALL-A-D are integrated and the
focused family receipt is
[`india-2-wall-family-acceptance-evidence.md`](../verification/india-2-wall-family-acceptance-evidence.md).
Do not expand the accepted wall topology while starting deep-beam G0.

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

## INDIA-2-WALL-G0 decision result

The GO record is
[`india-2-wall-g0-scope-evidence.md`](../verification/india-2-wall-g0-scope-evidence.md).
It freezes the supported wall case, IS 456 clauses, public normalized-content
boundary, hand benchmark and tolerance, units, fail-closed exclusions, and
WALL-A-D packet split. No wall calculation or capability claim is part of G0.

## INDIA-2-WALL acceptance result

[`india-2-wall-family-acceptance-evidence.md`](../verification/india-2-wall-family-acceptance-evidence.md)
records the integrated A-D head, public clause/source visibility, independent
benchmark, unsafe and fail-closed behavior, semantic-contract correction,
focused validation, retained holds, and deferred broad-gate boundary.

## Review and gate boundary

Each calculation packet requires focused tests, benchmarks, architecture and PR
checks, plus the quick gate. The expensive full Python and 30-check gate runs
once after the whole accepted INDIA-2 wave is integrated unless an
outcome-changing repository-wide issue appears earlier.

Cumulative qualified structural-engineering review belongs to INDIA-4 after the
accepted INDIA-2 and INDIA-3 scope is frozen. Packet-level source and engineering
checks still occur before each implementation GO. Software completion does not
grant professional approval, stable-release authorization, engineering-use
authorization, or cleanup authority.
