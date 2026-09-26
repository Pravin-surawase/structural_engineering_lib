---
name: session-management
description: "Run the compact project session workflow: one start, focused verification, cohesive commits in one PR, and one timing closeout. Use at session start, handoff, or closeout."
---

# Session Management

Use the canonical `run.sh` entry points from the workspace root. Do not repeat their internal reads and checks with separate commands.

## When to Use

- Starting a new coding session
- Ending or handing off a session
- Checking session state mid-work

## Session Start

Run once for one exact task:

```bash
./run.sh session begin --task-id <task> --agent <role>
```

`session begin` first performs read-only admission, then starts the shared task
timer and prints the bounded brief. A clean synchronized default branch is
admitted for intake only; create the feature branch before any write. Use
`./run.sh session context` only when the brief does not contain enough
information for the task. `session brief` and `session start` remain read-only/
compatibility entry points, but using them separately does not create complete
end-to-end timing evidence.

Before editing, confirm the branch and working tree shown by session start. Preserve unrelated user changes.

In a linked worktree, `.venv/` may exist only in the primary checkout. Use
`./run.sh` or `./scripts/python_runtime.sh`; never bypass the launcher with a
primary-checkout interpreter path. Session start must report `Python source
binding: current worktree`. If it does not, stop and run:

```bash
./scripts/python_runtime.sh --diagnose
```

If a direct helper name is missing or has been consolidated, do not guess an
archive path. Resolve the maintained command with `./run.sh find "task"`.

## Session Closeout

1. Complete the scoped work in cohesive commits on one branch. Format changed
   files and run affected behavior tests and relevant contract checks once after
   the batch. Repair confirmed failures and rerun only affected evidence.
2. Review the essential diff once, push one PR, and wait for required hosted
   checks before merging. Normal hooks check Git safety without a delivery
   ledger, session-document gate, or mandatory separate local audit.
3. Record the problem, change, and tests in the PR. Update task/session/handoff
   files only for unfinished work, durable decisions, or an actual transition.
4. Close the timer after delivery; elapsed time is measured automatically:

   ```bash
   ./run.sh session usage --checkpoint closeout --task-id <task> \
     --verification "focused tests and required PR checks passed"
   ```

The [detailed audit track](../../../docs/git-automation/git-workflow-single-source.md#compact-audited-integration)
is opt-in when an accepted plan explicitly requires release, installed-artifact,
or independent audit evidence. Only that track requires delivery transitions,
acceptance matrices, candidate integrity, structured session records, and the
explicit `session delivery --guard-push` closeout. Existing detailed tasks keep
their recorded history; do not reset their timers or ledgers to recover.

A versioned `scripts/git_handoff_receipt.py` receipt is required only for a real
cross-device, cross-worktree, installed-artifact, or authority transition.
`receipt_grants_authority: false` remains mandatory. If the task updates the
newest session entry, record completed outcomes and run `session handoff` then
`session check` to keep its handoff consistent.

Keep hosted and merge facts in GitHub. Do not run global doc syncing, evolution
fixes, release checks, or open a documentation-only follow-up PR by default.

## Session Check (mid-session)

```bash
./run.sh session check
```

Verifies the newest session's focus, completed outcomes and issue/recurrence
record, plus the maintained briefing structure, date and declared receipt.
Run it when editing those records. `session end` remains an optional read-only
diagnostic for detailed closeout; routine timing closeout does not depend on it.

## Key Files

| File | Purpose |
|------|---------|
| `docs/SESSION_LOG.md` | Durable session history when a recorded handoff is needed |
| `docs/WORKLOG.md` | Compact completed-work history when the task changes it |
| `docs/planning/next-session-brief.md` | Handoff to next session |
| `docs/TASKS.md` | Active task board |
| `scripts/session.py` | Session management CLI, executable delivery state, and optional receipt validation |
| `scripts/git_handoff_receipt.py` | Read-only task-to-Git receipt contract |

## Context Checkpoint (save before context overflow)

When a task must transfer to another session, update the handoff with: completed
outcome, exact remaining work, verification already run, and blockers. Include
the versioned receipt path and `local_state_receipt_hash` when the transition
crosses the receipt boundary described above. Remote/PR/check facts
are exact or `UNKNOWN`/`NOT_CHECKED`; `NOT_APPLICABLE` always has a reason. Keep
it task-specific; do not copy the conversation.

## Context Recovery (new chat after overflow)

Use the compact handoff view first:

```bash
./run.sh session brief --handoff
```

Read larger logs only if that brief cannot answer a concrete recovery question.
