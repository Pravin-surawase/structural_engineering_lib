# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-16
- Focus: Consolidate all INDIA-2 work into one understandable, executable plan without starting calculation implementation.
- Git receipt: docs/verification/india-2-plan-git-handoff-receipt.json | sha256:ecbc84c246e9f7e8bdaa19cac60ba0fa8ef12aea115bee9ddd1db077d5aa75f6 | HOLD
- Git identity: codex/india-2-detailed-plan@b3fed846210d3460cf4d6d6f326d2d6d6caf100d | upstream=NONE@UNKNOWN | base=origin/main@b3fed846210d3460cf4d6d6f326d2d6d6caf100d | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=OBSERVED
- Next action: WAIT_FOR_EXACT_HEAD_AUDIT
<!-- HANDOFF:END -->

**Date:** 2026-08-16

| Release state | Target |
|---|---|
| **Current** | `v0.23.1a1` Alpha; INDIA-0, INDIA-1, and the INDIA-2-STAIR family are complete |
| **Program** | Umbrella INDIA-2 remains in progress; INDIA-3 and INDIA-4 remain planned |
| **Next** | Integrate `INDIA-2-WALL-D`, then run focused wall-family acceptance from the verified integrated head |

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

`INDIA-2-WALL-G0` and WALL-A-C are integrated. WALL-D now has a verified local
typed FastAPI route plus canonical capability/semantic truth and manifest
promotion. After its exact head integrates, run focused family acceptance before
starting deep-beam G0.

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

## INDIA-2-WALL-D candidate result

[`india-2-wall-d-publication-evidence.md`](../verification/india-2-wall-d-publication-evidence.md)
records the thin REST schema/route, benchmark and unsafe-case behavior, public
clause/source visibility, canonical capability/semantic contract, retained
holds, manifest promotion, and focused validation. After integration, the
acceptance packet verifies the whole wall family without new calculation scope.

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
