---
name: session-management
description: "Run the compact project task/session workflow: lane-safe intake, one canonical start, bounded work, one validation ladder, and one normal commit. Use at task intake, session start, handoff, or closeout."
---

# Session Management

Use the canonical `run.sh` entry points from the workspace root. Do not repeat their internal reads and checks with separate commands.

## When to Use

- Starting a new coding session
- Starting a nontrivial task in a repository with active worktrees
- Ending or handing off a session
- Checking session state mid-work

## Efficient Task Intake

For a new nontrivial task, run once from the workspace root:

```bash
./run.sh task brief "concrete task description"
```

The command is read-only. It composes live worktree state, the existing role
router, skill assignments, automation registry, and a bounded initial read set.
It does not create or switch branches, stage, commit, stash, reset, push, or
change GitHub state.

Inspect every lane warning before editing. When isolation is needed, Codex owns
the native Git/worktree operation and must preserve dirty lanes. Do not add a
repository Git lifecycle wrapper.

For concurrent parent tasks, follow
`docs/guidelines/parallel-task-policy.md`: use one task per worktree and unique
branch, allow no overlapping owned path, and name one integration owner. The
default ceiling is two independent implementation tasks plus the integration
lane. Shared task boards, handoffs, generated artifacts, lock files, and public
registries stay single-writer surfaces.

Before editing, define one compact task contract:

- objective and explicit non-goals;
- exact base, owned paths, and integration owner;
- exact files and existing patterns to reuse;
- likely pitfalls and architecture/Git constraints;
- measurable acceptance criteria and narrow verification commands.

Use `./run.sh pipeline` only for an explicitly tracked multi-session workflow
that must resume later. Routine tasks do not need pipeline state.

## Session Start

Run once, in this order:

```bash
./run.sh session brief --agent <role>
./run.sh session start
```

The brief is the bounded orientation packet; session start verifies the environment and current project state. Use `./run.sh session context` only when the brief does not contain enough information for the task.

Before editing, confirm the branch and working tree shown by session start. Preserve unrelated user changes.

## Bounded Work Loop

```text
inspect the affected index and files
-> change one coherent outcome
-> run focused verification
-> record material issue, root cause, resolution, and evidence
```

Do not repeat task intake, session start, unchanged checks, or broad context
reads inside the loop.

## Session Closeout

1. Run the narrow checks for changed behavior while iterating.
2. Update `docs/TASKS.md` and `docs/planning/next-session-brief.md` only when their project state actually changed or another agent needs a durable handoff. Update other logs only when the task explicitly owns them.
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
| `scripts/session.py` | Session management CLI |

## Context Checkpoint (save before context overflow)

When a task must transfer to another session, update the handoff with: completed outcome, current branch/commit, exact remaining work, verification already run, and blockers. Keep it task-specific; do not copy the conversation.

## Context Recovery (new chat after overflow)

Use the compact handoff view first:

```bash
./run.sh session brief --handoff
```

Read larger logs only if that brief cannot answer a concrete recovery question.
