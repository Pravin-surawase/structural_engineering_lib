---
owner: Main Agent
status: active
last_updated: 2026-09-27
doc_type: guide
complexity: beginner
tags: [maintenance]
---

# Maintenance Checklist

The [maintenance playbook](../governance/maintenance-playbook.md) is the canonical
procedure. This page is a short entry point, not another delivery policy.

## Quick Reference

| Need | Action |
|---|---|
| Start work | `./run.sh session begin --task-id <task> --agent <role>` |
| Verify checkout/device state | Fetch GitHub, then `./scripts/python_runtime.sh scripts/git_state.py --json --worktrees` |
| Diagnose repository health | `./run.sh health`; inspect each reported owner |
| Verify a completed batch | Affected tests plus `./run.sh check` for essential changed-area checks |
| Inspect policy/context drift | `./run.sh efficiency check` and `./run.sh context validate` when relevant |
| Finish delivery | Required hosted checks, merge, then one `session usage --checkpoint closeout` |

## Daily Maintenance

Use the task's compact start and current priorities. Do not add a health scan,
quick check, full suite and evolution run to every normal edit. Refresh the
handoff after a milestone changes what the next agent should do.

## Weekly Maintenance

Inspect the current GitHub state, repository health and unresolved feedback.
Fix confirmed drift in one bounded batch with several cohesive commits and one
PR. Update the existing canonical documentation and record material recurrence.

## Monthly Maintenance

Review dependencies, recurring failures and the next release need. Broad suites
and `./run.sh check --full` require a concrete risk or release reason.
Branch/worktree classification is inspection; cleanup requires separate exact
authorization.

## Health Score Categories

The current diagnostic implementation is `scripts/project_health.py`. A cached
startup score is the last report, not a new scan. A green score does not prove
complete engineering scope, live-host qualification or release readiness.

## Common Fix Patterns

Repair inventory drift in its shared owner, invalid metadata in the named
document, and stale commands in the guide that recommends them. Keep error
states explicit. Do not overwrite hooks, delete worktrees or run broad
auto-fix commands as a generic response to a warning.

## Maintenance Pipeline (Who Does What)

One parent normally performs diagnosis, scoped repairs, focused verification
and essential review. Codex owns Git/GitHub delivery. Repair only affected
evidence if the candidate changes; do not restart every gate.

## Tracking

Put the problem, root cause, correction and checks in the PR. Maintain a
session/handoff record when next work or a durable decision changes; routine
commits need no bookkeeping-only follow-up PR. Preserve unresolved feedback
until evidence supports resolution.
