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

Run once for one exact task:

```bash
./run.sh session begin --task-id <task> --agent <role>
```

`session begin` first performs read-only admission, then starts the shared task
timer and prints the bounded brief. A clean synchronized default branch is
admitted for intake only; create the feature branch before `BOUNDED_UNITS` or
any write. Use
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

1. Record the acceptance files at `BOUNDED_UNITS`, complete the bounded writes,
   then enter `CONTENT_FROZEN`.
2. Run `./run.sh format --write` once. Advance through `FORMATTED`,
   `FOCUSED_VERIFIED`, and `PREPARED` with exact evidence.
3. Update `docs/TASKS.md`, the newest `docs/SESSION_LOG.md` entry, maintained
   generated projections, and `docs/planning/next-session-brief.md` before the
   candidate commit. A versioned `scripts/git_handoff_receipt.py` receipt is
   required only for a real cross-device, cross-worktree, installed-artifact,
   or authority transition; routine same-checkout delivery needs none.
   Every declared receipt remains evidence rather than authority:
   `receipt_grants_authority: false` is mandatory.
4. Commit the clean `CANDIDATE`, have one independent audit return one decision,
   then advance to `AUDIT_ACCEPTED`. One rejection admits one consolidated
   repair candidate; a second enters `REPLAN` until acceptance content changes.
5. Run `./run.sh check --candidate-integrity` once on the accepted unchanged
   head and advance to `INTEGRITY_VERIFIED`. On failure, record
   `INTEGRITY_REJECTED`; it consumes the same single repair allowance as an
   audit rejection, and a repaired-candidate failure enters `REPLAN`.
6. Push normally. The pre-push hook runs one read-only `session end`, records
   `FINAL_CLOSED`, and does not rerun on a repeated push of the same head. After
   one hosted run passes, record `HOSTED_PASSED`, merge, record `MERGED`, and
   create the automatically derived usage closeout. If the run fails, record
   `HOSTED_REJECTED` with its exact run ID before entering repair; the
   replacement head receives one new closeout and hosted verdict.

Do not run global doc syncing, legacy index generation, evolution fixes, release
checks, or a second documentation commit by default. After push or PR creation,
keep hosted-check and merge facts in GitHub and the external handoff; do not
write them back into the same candidate. If session end identifies an essential
handoff defect, correct only that defect as an explicit repair candidate through
the same Codex-native workflow.

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
