---
owner: Main Agent
status: active
last_updated: 2026-11-24
doc_type: guide
complexity: intermediate
tags: []
---

# Handoff Quick Start

Use the [canonical Git workflow](../git-automation/git-workflow-single-source.md)
to resume a task and choose the correct closeout. Git-state output describes
the local checkout. Check the remote and GitHub separately when current hosted
state matters.

## Resume (next agent)

Start the task in its intended worktree.

```bash
./run.sh session begin --task-id <task> --agent <role>
```

Check the [session brief](../planning/next-session-brief.md) for the latest
verified work and the [task board](../TASKS.md) for the queue. Use
[AGENTS.md](https://github.com/Pravin-surawase/structural_engineering_lib/blob/main/AGENTS.md) for repository instructions. If the start reports a
hold, inspect the source binding with `./scripts/python_runtime.sh --diagnose`
and the local lane with `./scripts/python_runtime.sh scripts/git_state.py --json`.

### Release verify (clean venv)

Use the [release checklist](../planning/pre-release-checklist.md) for exact
artifact qualification and the [release ledger](../getting-started/releases.md)
for the public install receipt. Follow the release's own authorization and
evidence gates.

## Handoff (ending)

For routine delivery, record the change and verification in the PR and close
the task timer. Follow the [end-of-session guide](end-of-session-workflow.md)
for the supported command and the audited integration path.

For unfinished work or a durable decision, record the task identity, head or
artifact, verified outcome, blocker, and next permitted action in the
existing handoff. For device, worktree, installed-artifact, or external
authority transitions, build and validate the tracked receipt described in
the [durable handoff workflow](../git-automation/git-workflow-single-source.md#durable-task-to-git-handoff).

## Debug Snapshot Checklist

When encountering persistent errors, collect this information for handoff:

1. **Collect diagnostics bundle:**
   ```bash
   ./scripts/python_runtime.sh scripts/collect_diagnostics.py > diagnostics.txt
   ```

2. **Inspect the active React/FastAPI stack:**
   ```bash
   ./run.sh dev
   ```
   Reproduce the request and retain the browser console plus FastAPI terminal
   output. Streamlit is retired.

3. **Check the owning evidence:**
   - the exact-head GitHub checks
   - the versioned task-to-Git receipt when the handoff requires one

4. **Run validators:**
   ```bash
   ./scripts/python_runtime.sh scripts/generate_api_manifest.py --check
   ./scripts/python_runtime.sh scripts/check_scripts_index.py
   ./scripts/python_runtime.sh scripts/check_links.py
   ```

5. **Include in handoff:**
   - Diagnostics output
   - Relevant log excerpts
   - Error screenshots/messages
   - Steps to reproduce

## Common Traps (fast fixes)
- CI query times out: record `UNKNOWN`/hold and have Codex re-query the exact head.
- PR behind base: inspect exact base/head and let Codex choose a normal, non-rewriting update path.
- PyPI verification: always use a clean venv.
