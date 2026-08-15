# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-15
- Focus: Publish the typed staircase Python/FastAPI workflow and promote only its verified straight-flight capability.
- Git receipt: docs/verification/india-2d-git-handoff-receipt.json | sha256:1d7c13e35fd53e0b47dbbc716d8a316b726253f1e7443096af034cfdc327543a | HOLD
- Git identity: codex/india-2d-staircase-public@bb1abd1818028118f92b1f7c8b0ed1ba57994fdf | upstream=origin/main@bb1abd1818028118f92b1f7c8b0ed1ba57994fdf | base=origin/main@bb1abd1818028118f92b1f7c8b0ed1ba57994fdf | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=OBSERVED
- Next action: WAIT_FOR_EXACT_HEAD_AUDIT
<!-- HANDOFF:END -->

**Date:** 2026-08-15

| Release state | Target |
|---|---|
| **Current** | `v0.23.1a1` Alpha; INDIA-1 software and cumulative gates complete |
| **Next** | One cumulative broad-gate packet after INDIA-2D integration; qualified review remains separate |

## Required Reading

1. [INDIA-2D public-workflow evidence](../verification/india-2d-staircase-publication-evidence.md)
2. [Generated Indian-code manifest](../verification/indian-code-capability-coverage.json)
3. [Current task board](../TASKS.md)
4. [Canonical efficiency policy](../guidelines/ai-token-efficiency.md)
5. [Canonical Git workflow](../git-automation/git-workflow-single-source.md)

## Start Boundary

INDIA-2A-C are integrated. INDIA-2D is complete on its isolated branch and must
be merged unchanged after required checks pass. Start the cumulative packet only
from that verified merge SHA; do not reuse an earlier worktree or reopen A-D.

```bash
./run.sh session brief --agent reviewer
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
./scripts/python_runtime.sh scripts/generate_indian_code_manifest.py --check
```

Require a clean fresh branch from verified current `origin/main` and
`source_bound=true`. Preserve the dirty primary checkout and every unrelated
worktree.

## Cumulative Packet

Create `codex/india-2-cumulative-gates` from verified integrated `origin/main`.
Run exactly once:

1. the broad Python suite through `./run.sh test`;
2. the full repository gate through `./run.sh check`;
3. Indian-code manifest generation/check and capability truth review;
4. an essential review of the supported route, benchmark provenance, public
   facade/FastAPI identity, and retained holds; and
5. a cumulative evidence document plus task/session reconciliation.

Fix only outcome-changing INDIA-2 or repository-wide failures. Do not add
adjacent stair features, React, or release work during the gate packet.

## INDIA-2 Exit

INDIA-2 is complete when this bounded stair family remains executable,
independently benchmarked, provenance-bearing, and truthfully limited; every
other held family remains unchanged; manifests contain no unknown status; and
the cumulative software gates pass. Qualified engineering review, professional
approval, release authorization, and branch/worktree cleanup remain separate.
