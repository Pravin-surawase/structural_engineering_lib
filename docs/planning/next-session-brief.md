# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-16
- Focus: cumulative INDIA-2 closeout
- Baseline: raft G0 started from fetched origin/main def0b493e33fa566fd3f23bf166287fcda6169d6, tree 7da91c66143e83933a88bb9a4d5396bede89cf6d
- Truth: 13 supported / 8 held; 81/81 endpoints directly tested
- Foundation outcome: pile-cap and raft G0 both HOLD; required controlled companion sources and accepted replayable structural benchmarks were not retained, and no calculation file was created
- Scope guard: closeout reconciles evidence/truth and runs broad gates once; no new behavior or held-family promotion
- Retained lanes: primary, detached dirty e54a, Excel HOLD_UNKNOWN_OWNER, and every other pre-existing lane remain untouched; no cleanup authority exists
- Next action: begin only INDIA-2-CLOSEOUT in a fresh fetched-current-main lane after the raft HOLD candidate merges
<!-- HANDOFF:END -->

**Date:** 2026-08-16

| State | Boundary |
|---|---|
| **Current** | `v0.23.1a1` Alpha; pile-cap integrated HOLD and raft G0 closes as HOLD on merge |
| **Next** | Cumulative `INDIA-2-CLOSEOUT` |
| **Later** | Separately authorized INDIA-3 or dependency work only after closeout |
| **Held** | Cleanup/deletion, release, React expansion, professional approval, dependency majors |

## Required Reading

1. [Next-session Git/issues/INDIA-2 plan](india-2-next-session-publication-and-closeout-plan.md)
2. [Current task board](../TASKS.md)
3. [IS 456 public-distribution permission](../verification/is456-public-distribution-permission.json)
4. Discover the accepted family receipts, both foundation HOLD records,
   manifest/parity consumers, and broad-gate entry points with `rg --files`.

## Exact start

Fetch and verify `origin/main`, then create one fresh
`codex/india-2-closeout` worktree. Do not write on primary, reuse a family/G0
lane, or touch retained worktrees.

```bash
./run.sh session brief --agent structural-engineer
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
```

Require `source_bound=true`, `READY_LOCAL`, no operation marker, and exact base
equality with fetched `origin/main` before editing.

## Packet order

1. Reconcile one complete INDIA-2 evidence index and final task/plan truth.
2. Run broad Python once and the full 30-check repository gate once.
3. Publish exact-head/hosted-check/final-tree closeout evidence and merge.
4. Post-INDIA-2 work remains separately authorized afterward.

## Frozen closeout scope

Close INDIA-2 administratively around six accepted bounded families: wall,
staircase, deep beam, flat slab/punching, combined footing, and strap footing.
Preserve pile-cap and raft as `HELD / NOT_IMPLEMENTED` with their exact G0
reactivation contracts. Build one evidence index that links source, benchmark,
publication, focused acceptance, PR/merge, and integrated-tree evidence for
each accepted family and the two HOLD records.

No calculation, service, API, React, manifest promotion, feature expansion,
dependency change, release, cleanup, or professional-approval behavior belongs
in closeout. The final truth target remains 13 supported / 8 held and 81/81
directly tested endpoints.

## Owner-decision boundaries

- Primary, `e54a`, Excel, the frontmatter lane, and every other retained lane
  stay untouched.
- Public-source distribution permission is already recorded; do not reopen it.
- Pile-cap and raft remain held. Cleanup/deletion, release/tag/package
  publication, and professional approval remain separately gated.

## Gate cadence

Run focused evidence/documentation checks, links, quick `10/10`, broad Python
once, the full 30-check gate once, normal hooks, exact-head review, hosted
checks, and merge-tree verification.

The session entry must contain `Issues encountered` and `Root causes and
resolutions`, with executable evidence for the corrected outcome.

## Efficiency card

- Freeze the evidence index and no-new-behavior boundary before editing.
- Use one writer, one candidate, one broad Python run, one full gate, one push,
  and one hosted-check cycle.
- Record orientation, implementation, repair, CI wait, closeout, and total
  elapsed workflow time separately.

## Stop rule

Start and finish only `INDIA-2-CLOSEOUT`. Do not begin INDIA-3, calculation
code, dependency, cleanup, release, professional approval, or React work in
that lane.
