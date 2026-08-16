# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-16
- Focus: post-INDIA-2 cleanup, maintenance, and deterministic-index closeout; no implementation packet is active
- Base: maintenance merged at `7541a7c7`, with merged tree exactly equal to reviewed PR #809 tree `0f025913`
- Cleanup: candidate set `POST-INDIA2-2499DF4ADE0DF704` completed 193/193 exact actions and recovered 8,388,911,104 bytes
- Retained: dirty detached `e54a`, Excel, `gh-pages`, Dependabot/open-PR heads, and every non-candidate or evidence-incomplete lane remain retained or held
- Maintenance: five stale count occurrences refreshed; session and task history compacted without loss; `_active` has no multi-session plans
- Indexes: freshness ignores filesystem timestamps recursively; writes are affected-folder only; the existing Monday workflow audits all 32 indexes without writing
- Truth: 13 supported / 8 held; 81/81 endpoints directly tested; pile-cap and raft remain `HELD / NOT_IMPLEMENTED`
- Next action: owner-selected work only; INDIA-3, dependency, release, further cleanup, and professional approval require separate activation
<!-- HANDOFF:END -->

**Date:** 2026-08-16

| State | Boundary |
|---|---|
| **Current** | `v0.23.1a1` Alpha; INDIA-2 and its bounded cleanup/maintenance closeout are complete on merge |
| **Next** | Owner-selected work only; no implementation packet is active |
| **Later** | Separately authorized INDIA-3, dependency, or product work |
| **Held** | Pile-cap, raft, release, React expansion, professional approval, and all non-candidate Git lanes |

## Required Reading

1. [Cleanup execution receipt](../verification/post-india2-cleanup-execution-receipt.json)
2. [Cleanup disposition evidence](../verification/post-india2-cleanup-disposition-evidence.json)
3. [Final INDIA-2 closeout evidence](../verification/india-2-final-closeout-evidence.md)
4. [Current task board](../TASKS.md)

## Exact next start

Wait for an owner-selected packet. Fetch and verify `origin/main`, then create
one fresh `codex/<task-slug>` worktree. Do not write on primary, reuse cleanup
lanes, or touch retained worktrees.

```bash
./run.sh session brief --agent <role>
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
```

Require `source_bound=true`, `READY_LOCAL`, no operation marker, and exact base
equality with fetched `origin/main` before editing.

## Closed post-INDIA-2 sequence

1. PR #807 froze the union inventory, exact candidate set, and every hold.
2. PR #808 recorded exact cleanup execution and retained-lane postconditions.
3. MAINT-010 refreshed generated truth, compacted history, archived superseded
   plans, and ran the overdue monthly evolution review without applying changes.
4. The bounded index follow-up removed cross-worktree `mtime` drift, migrated
   the 32 maintained hashes once, and added a weekly read-only freshness audit.
5. No structural arithmetic, API/React behavior, dependency, release, INDIA-3,
   or professional-approval claim changed.

## Retained boundaries

- `e54a` remains dirty and detached exactly as found.
- Excel remains a retained worktree/branch; `gh-pages` remains remote.
- Dependabot heads remain tied to their open PRs and outside manual cleanup.
- Every branch without complete owner, PR, exact-tree, or retention evidence
  remains retained or held.
- Pile-cap and raft remain held until their recorded source and benchmark
  reactivation conditions are satisfied.

## Acceptance record

The maintenance packet requires zero stale generated counts; deterministic
32/32 indexes from the same commit in independent worktrees;
health 100/100 or explicit holds; audit 19/19; parity 13 supported / 8 held and
81/81 endpoints; focused governance tests; links; strict metadata; quick 10/10;
full 30/30; exact-head hosted checks; and squash-tree equality.

## Stop rule

Stop after MAINT-010 merge and primary synchronization. Do not infer INDIA-3,
calculation, dependency, release, professional-approval, React, or further Git
cleanup authority from this maintenance closeout.
