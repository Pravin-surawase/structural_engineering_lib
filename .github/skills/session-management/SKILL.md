---
name: session-management
description: "Run the compact project session workflow: one canonical start, task-scoped state updates, one validation ladder, and one normal commit. Use at session start, handoff, or closeout."
---

# Session Management

Use the canonical `run.sh` entry points from the workspace root. Do not repeat their internal reads and checks with separate commands.

## When to Use

- Starting a new coding session
- Ending or handing off a session
- Checking session state mid-work

## Session Start

Run once, in this order:

```bash
./run.sh session brief --agent <role>
./run.sh session start
```

The brief is the bounded orientation packet; session start verifies the environment and current project state. Use `./run.sh session context` only when the brief does not contain enough information for the task.

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

1. Run the narrow checks for changed behavior while iterating.
2. Update `docs/TASKS.md` and `docs/planning/next-session-brief.md` only when their project state actually changed or another agent needs a durable handoff. Update other logs only when the task explicitly owns them.
   Create or update the task's versioned receipt with
   `scripts/git_handoff_receipt.py`; include its path in the newest session entry
   as `**Git handoff receipt:** <path>`. Session handoff validates the
   `local_state_receipt_hash`, exact identities, independently derived
   fail-closed holds, `receipt_grants_authority: false`, and externally sourced
   exact-target authorization evidence, including fresh/query-successful
   provenance and a next action bound to that authority or the closed safe-hold
   set.
3. Run the pre-commit gate once:

   ```bash
   ./run.sh check --quick
   ```

4. Have Codex inspect the final diff, stage only intended paths, create one
   conventional commit, push without rewriting history, and create or update the
   PR through the connected GitHub integration.

5. Validate the clean handoff:

   ```bash
   ./run.sh session end --agent <role>
   ```

Do not run global doc syncing, index regeneration, evolution fixes, release checks, or a second documentation commit by default. If session end identifies an essential handoff defect, correct only that defect and return it through the same Codex-native workflow.

## Session Check (mid-session)

```bash
./run.sh session check
```

Verifies:
- SESSION_LOG.md is not stale
- next-session-brief.md has recent updates
- TASKS.md has no abandoned "in progress" items

## Key Files

| File | Purpose |
|------|---------|
| `docs/SESSION_LOG.md` | Durable session history when a recorded handoff is needed |
| `docs/WORKLOG.md` | Compact completed-work history when the task changes it |
| `docs/planning/next-session-brief.md` | Handoff to next session |
| `docs/TASKS.md` | Active task board |
| `scripts/session.py` | Session management CLI and receipt round-trip validation |
| `scripts/git_handoff_receipt.py` | Read-only task-to-Git receipt contract |

## Context Checkpoint (save before context overflow)

When a task must transfer to another session, update the handoff with: completed
outcome, the versioned receipt path and `local_state_receipt_hash`, exact
remaining work, verification already run, and blockers. Remote/PR/check facts
are exact or `UNKNOWN`/`NOT_CHECKED`; `NOT_APPLICABLE` always has a reason. Keep
it task-specific; do not copy the conversation.

## Context Recovery (new chat after overflow)

Use the compact handoff view first:

```bash
./run.sh session brief --handoff
```

Read larger logs only if that brief cannot answer a concrete recovery question.
