# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-16
- Focus: post-INDIA-2 owner decision; no implementation packet is active
- Baseline: closeout started from merged raft-HOLD origin/main d28852156752ea6e44b0c9fbb67988088851bf3e, tree 38958c8a484d5f63a1092b2e852af64bef7afc2a
- Truth: 13 supported / 8 held; 81/81 endpoints directly tested
- Foundation outcome: pile-cap and raft G0 both HOLD; required controlled companion sources and accepted replayable structural benchmarks were not retained, and no calculation file was created
- Closeout: six bounded families accepted; pile-cap and raft remain HELD / NOT_IMPLEMENTED; final evidence index and cumulative gates pass without new behavior
- Retained lanes: primary, detached dirty e54a, Excel HOLD_UNKNOWN_OWNER, and every other pre-existing lane remain untouched; no cleanup authority exists
- Next action: none inferred; INDIA-3, dependency, release, cleanup, and professional-approval work require separate authorization
<!-- HANDOFF:END -->

**Date:** 2026-08-16

| State | Boundary |
|---|---|
| **Current** | `v0.23.1a1` Alpha; INDIA-2 complete within six accepted and two held family decisions |
| **Next** | Owner-selected work only; no packet is activated by closeout |
| **Later** | Separately authorized INDIA-3 or dependency work |
| **Held** | Cleanup/deletion, release, React expansion, professional approval, dependency majors |

## Required Reading

1. [Final INDIA-2 closeout evidence](../verification/india-2-final-closeout-evidence.md)
2. [Current task board](../TASKS.md)
3. [Indian-code completion waves](indian-code-completion-plan.md)
4. [Completed INDIA-2 execution plan](india-2-remaining-is456-elements-plan.md)

## Exact next start

Wait for an explicit owner-selected packet. Then fetch and verify `origin/main`
and create one fresh `codex/<task-slug>` worktree. Do not write on primary,
reuse an INDIA-2 lane, or touch retained worktrees.

```bash
./run.sh session brief --agent structural-engineer
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
```

Require `source_bound=true`, `READY_LOCAL`, no operation marker, and exact base
equality with fetched `origin/main` before editing.

## Closed INDIA-2 order

1. Complete INDIA-2 evidence index and final task/plan truth.
2. Broad Python and the full 30-check repository gate pass after their recorded
   failure-required corrective reruns.
3. Exact-head/hosted-check/final-tree closeout evidence merges unchanged.
4. Post-INDIA-2 work remains separately authorized.

## Frozen closed scope

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

## Closeout gate record

Focused evidence/documentation checks, links, quick `10/10`, broad Python, the
full 30-check gate, normal hooks, exact-head review, hosted checks, and merge-
tree verification form the closeout record. The planned single local runs and
their failure-required corrective reruns are recorded in the closeout evidence.

The session entry must contain `Issues encountered` and `Root causes and
resolutions`, with executable evidence for the corrected outcome.

## Retained efficiency record

- Freeze the evidence index and no-new-behavior boundary before editing.
- Use one writer, one candidate, one planned broad Python run, one full gate,
  one push, and one hosted-check cycle. The actual closeout needed one
  corrective broad rerun because the first run exposed stale exact-equilibrium
  contracts, and one corrective full-gate rerun because the first run exposed
  a stale generated public API manifest.
- Record orientation, implementation, repair, CI wait, closeout, and total
  elapsed workflow time separately.

## Stop rule

INDIA-2 stops at closeout. Do not begin INDIA-3, calculation code, dependency,
cleanup, release, professional approval, or React work without a separately
authorized packet.
