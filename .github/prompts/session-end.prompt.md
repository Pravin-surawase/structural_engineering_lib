---
description: "Compact closeout — task-owned state, one gate, one commit, read-only validation"
---

# Session Closeout Workflow

Use this once after the scoped work and its narrow checks are complete.

## Steps

1. Update `docs/TASKS.md` or `docs/planning/next-session-brief.md` only when
   their project state changed or a durable handoff is required. Update global
   logs, indexes, counts, feedback, and evolution records only when the task
   explicitly owns them.
2. Run the quick gate once:
   ```bash
   ./run.sh check --quick
   ```
3. Confirm the required Git path and make one normal task commit:
   ```bash
   # Codex reviews, stages intended paths, commits, pushes, and updates the PR.
   ```
4. Validate the clean handoff without hidden mutations:
   ```bash
   ./run.sh session end --agent <role>
   ```

Do not run session summary/sync, evolution, release checks, index generation,
or a second documentation commit by default. If validation finds an essential
handoff defect, fix only that defect and commit it through the same safe path.
