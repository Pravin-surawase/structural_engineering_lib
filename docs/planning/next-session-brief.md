# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-15
- Focus: Preserve the unique audit entry from stale dirty primary main before any INDIA-3 lane or destructive cleanup.
- Git receipt: docs/verification/git-primary-session-log-reconcile-handoff-receipt.json | sha256:899b385ab0227bb7d5dbf3a19e72107cd09cb303c03f33f4394c1c5341e157db | HOLD
- Git identity: codex/git-primary-session-log-reconcile@9d68f53e70dc088c3ee7034ca99d0ed1c418717a | upstream=origin/main@9d68f53e70dc088c3ee7034ca99d0ed1c418717a | base=origin/main@9d68f53e70dc088c3ee7034ca99d0ed1c418717a | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=OBSERVED
- Next action: WAIT_FOR_EXACT_HEAD_AUDIT
<!-- HANDOFF:END -->

**Date:** 2026-08-15

| Release state | Target |
|---|---|
| **Current** | `v0.23.1a1` Alpha; INDIA-1 and INDIA-2 software and cumulative gates complete |
| **Next** | Qualified structural-engineering review; no release or further stair scope is activated |

## Required Reading

1. [INDIA-2 cumulative gate evidence](../verification/india-2-cumulative-gate-evidence.md)
2. [INDIA-2D public-workflow evidence](../verification/india-2d-staircase-publication-evidence.md)
3. [Generated Indian-code manifest](../verification/indian-code-capability-coverage.json)
4. [Current task board](../TASKS.md)
5. [Canonical Git workflow](../git-automation/git-workflow-single-source.md)

## Start Boundary

INDIA-2A-D and the cumulative software gates are complete. Do not reopen those
packets, add another stair topology, add React, or begin release work without a
new owner-approved scope. The next engineering step is independent qualified
review of the bounded workflow and its retained assumptions.

```bash
./run.sh session brief --agent structural-engineer
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
./scripts/python_runtime.sh scripts/generate_indian_code_manifest.py --check
```

Require a clean fresh branch from verified current `origin/main` and
`source_bound=true`. Preserve the dirty primary checkout, every unrelated
worktree, and all INDIA-2 branches/worktrees until cleanup is explicitly
authorized.

## Qualified-review boundary

The qualified reviewer should assess the accepted NPTEL benchmark, Clause 33
geometry/action interpretation, flexure, supplied-bar and ordinary-shear checks,
basic span/depth disposition, public provenance, and all retained holds. Record
review findings separately from software-gate evidence.

Software completion does not grant professional approval, stable-release
authorization, or engineering-use authorization. Any outcome-changing review
finding must be resolved in a separately bounded packet and revalidated in
proportion to the change.

## INDIA-2 Exit

INDIA-2 meets its software exit: the bounded stair family is executable,
independently benchmarked, provenance-bearing, and truthfully limited; every
other held family is unchanged; manifests contain no unknown status; and the
cumulative gates pass. Qualified engineering review, professional approval,
release authorization, and branch/worktree cleanup remain separate.
