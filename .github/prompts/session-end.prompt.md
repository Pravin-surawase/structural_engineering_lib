---
description: "Compact closeout — task-owned state, one gate, one commit, read-only validation"
---

# Session Closeout Workflow

Use this once after the scoped work and its narrow checks are complete.

## Steps

1. Update `docs/TASKS.md` or `docs/planning/next-session-brief.md` only when
   their project state changed or a durable handoff is required. Update global
   logs, context routing, counts, feedback, and evolution records only when the task
   explicitly owns them.
2. Freeze all owned versioned logs, task/handoff state, evidence, and the
   pre-commit receipt. Validate live repository context read-only.
3. Run the quick gate once:
   ```bash
   ./run.sh check --quick
   ```
4. Confirm the required Git path and make one normal task commit:
   ```bash
   # Codex reviews, stages intended paths, commits, pushes, and updates the PR.
   ```
5. Validate the clean handoff without hidden mutations:
   ```bash
   ./run.sh session end --agent <role>
   ```

Do not run session summary/sync, evolution, release checks, legacy index generation,
or a second documentation commit by default. Keep PR, hosted-check, and merge
facts in GitHub and the external handoff instead of writing them into the same
candidate. If validation finds an essential handoff defect, fix only that
defect as an explicit repair candidate through the same safe path.
