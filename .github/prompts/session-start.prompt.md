---
description: "Compact session start — bounded brief, environment check, then scoped work"
---

# Session Start Workflow

## Start Once

```bash
./run.sh session begin --task-id <task> --agent <role>
```

The canonical command combines the bounded brief, environment check, branch and
working-tree evidence, and task-scoped usage checkpoint. `session brief` and
`session start` remain read-only compatibility diagnostics, not the normal
two-step task workflow. Use `./run.sh session context` only when the combined
start cannot answer a concrete question.

Choose one active task, state its main-process outcome and non-goals, then inspect
the exact implementation path before editing.
