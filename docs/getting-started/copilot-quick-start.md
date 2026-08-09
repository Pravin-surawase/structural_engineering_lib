---
owner: Main Agent
status: active
last_updated: 2026-08-09
doc_type: guide
complexity: beginner
tags: [codex, setup, git]
---

# Agent Quick Start

Run from the repository root:

```bash
./run.sh session brief --agent <role>
./run.sh session start
git status --short
git branch --show-current
```

Use `.venv/bin/python` for project Python commands. For validation and discovery:

```bash
./run.sh check --quick
./run.sh test
./run.sh find "topic"
./run.sh find --api function_name
```

## Git and GitHub

Codex owns branch inspection, scoped staging, conventional commits, pushes, and
connected GitHub PR creation or updates. Repository scripts do not perform those
operations. Follow the
[canonical workflow](../git-automation/git-workflow-single-source.md).

Never bypass hooks or required checks, force push, use `git rebase --skip`, or
run automated Git recovery. Merge, release, issue closure, and branch deletion
require explicit user confirmation.

## Closeout

Run targeted checks while editing, then one closeout gate. Return the intended
files and suggested conventional commit to Codex. Preserve unrelated work in a
dirty worktree.
