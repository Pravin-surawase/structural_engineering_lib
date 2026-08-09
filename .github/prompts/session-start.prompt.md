---
description: "Compact session start — bounded brief, environment check, then scoped work"
---

# Session Start Workflow

## Start Once

```bash
./run.sh session brief --agent <role>
./run.sh session start
```

The brief provides bounded priorities and handoff state. Session start verifies
the environment, branch, and working tree. Use `./run.sh session context` only
when the brief cannot answer a concrete question; do not separately reload the
same task files and Git state.

Choose one active task, state its main-process outcome and non-goals, then inspect
the exact implementation path before editing.
