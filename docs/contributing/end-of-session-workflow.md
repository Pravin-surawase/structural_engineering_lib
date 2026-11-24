---
owner: Main Agent
status: active
last_updated: 2026-11-24
doc_type: guide
complexity: intermediate
tags: []
---

# End-of-Session Workflow

**Type:** Guide
**Audience:** All Agents
**Status:** Approved
**Importance:** Critical
**Created:** 2026-01-08
**Last Updated:** 2026-11-24

[AGENTS.md](https://github.com/Pravin-surawase/structural_engineering_lib/blob/main/AGENTS.md) and the
[canonical Git workflow](../git-automation/git-workflow-single-source.md)
define routine delivery, audited integration, and handoff requirements.

## Quick Checklist (5 Minutes)

1. Finish the scoped changes. Run the affected tests and relevant contract
   checks, and review the diff against the intended base.
2. Publish one scoped PR. Record the problem, confirmed cause, change, and
   verification in its description. Verify that required hosted checks pass
   on the reviewed head before merging.
3. Close the task timer with the same ID used to start the session.

```bash
./run.sh session usage --checkpoint closeout --task-id <task> \
  --verification "focused checks and required PR checks passed"
```

For unfinished work or a durable decision, record what changed and the next
action in the task's existing handoff. Copy hosted check and merge facts from
GitHub when the receiving task needs them.

## Full Workflow (Step-by-Step)

### Routine integration

Use the [routine Git workflow](../git-automation/git-workflow-single-source.md#routine-integration)
for the normal branch, commit, PR, and hosted-check sequence. Use the
[handoff quick start](handoff.md#resume-next-agent) to resume the work on the
intended checkout. Update task, session, or handoff records when the work
changes their durable state.

### Audited integration

Use [compact audited integration](../git-automation/git-workflow-single-source.md#compact-audited-integration)
when the owner or an accepted plan explicitly selects detailed release,
installed-artifact, or independent audit evidence. That workflow owns the
candidate freeze, independent review, integrity gate, and publication guard.
Its final closeout runs a read-only session diagnostic.

For a manual diagnostic, run `./run.sh session end`. Use
`./run.sh session end --help` for its supported options.

### Step 7: Confirm Handoff Readiness

When state crosses a device, worktree, installed-artifact, or external
authority boundary, follow the
[durable task-to-Git handoff](../git-automation/git-workflow-single-source.md#durable-task-to-git-handoff).
Prepare its tracked receipt and provide the exact identities and the next
permitted action. Use the handoff command to validate a declared receipt and
update the receiving brief.

```bash
./run.sh session handoff --git-receipt <tracked-path>
```

An installed host or release must satisfy its own scope, permission, and
evidence gates before the next authorized action.

## Quick Reference by Session Type

| Session | Closeout |
| --- | --- |
| Routine fix, feature, or documentation | Affected checks, one PR, required hosted checks, and the task timer. |
| Selected detailed audit | Follow the canonical audited-integration stages and the accepted plan. |
| Task, device, worktree, or installed-artifact transition | Record the receiving task, identity, pending evidence, and next action. Create a receipt when the transition crosses a defined boundary. |
| Research or investigation | Record the decision or finding in its owning note and link the evidence needed to resume. Close the task timer. |

### Session Docs Rule (Avoid the Commit Loop)

Use the repository's existing record when a handoff changes. Keep later PR and
merge outcomes on GitHub. A completed routine change uses its delivery PR as
the closeout record.

## Templates

For a handoff that needs a durable record, include:

- Task, receiving role, and writer device or worktree.
- Exact branch, base and head, or the installed artifact identity.
- Verified result, evidence source, and remaining blocker.
- Next command or source to inspect and the result needed to proceed.
- A [tracked Git receipt](../git-automation/git-workflow-single-source.md#durable-task-to-git-handoff)
  when the transition requires one.

Use the [session issues log](session-issues.md) for the detailed issue record
when the accepted maintenance or audit plan calls for it.

## Related Documentation

- [Handoff quick start](handoff.md)
- [Current session brief](../planning/next-session-brief.md)
- [Canonical Git workflow](../git-automation/git-workflow-single-source.md)
- [Automation catalog](../reference/automation-catalog.md)
