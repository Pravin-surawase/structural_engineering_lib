---
owner: Main Agent
status: active
last_updated: 2026-09-03
doc_type: guide
complexity: beginner
tags: [excel-dna, xll, git, handoff]
---

# Resume the XLL plan on Mac or Windows

The shared home is the existing [structural_engineering_lib repository](https://github.com/Pravin-surawase/structural_engineering_lib). Start at `docs/planning/xll-product/README.md` in the exact fetched revision. This guide applies the [canonical multi-device Git workflow](../../git-automation/git-workflow-single-source.md); it does not create a second workflow.

## Why the earlier mismatch happened

The intended architecture was initially identified by a Mac worktree path and was unavailable in the Windows task. A different optimizer roadmap was then compared as if it were the original. Later, changing the app's saved project folder did not change that existing task's working directory. The research workspace itself had no commits or remote.

The shared architecture, corrected research map and source hashes address the missing-source problem. Checking the actual execution directory addresses the folder problem. Neither a commit nor a correct folder alone proves that a plan has been interpreted correctly.

## Starting work

1. Select the library checkout in the app, then verify the actual terminal/command directory with `git rev-parse --show-toplevel`. Check that `git remote get-url origin` identifies this repository. The display name is not identity evidence.
2. Inspect `git status --short --branch` before switching or pulling. Preserve local work. Follow the canonical workflow to fetch and fast-forward a clean local main, or retrieve the exact handed-off task branch. Do not reset, replace a Git directory or copy another project's configuration to fix a mismatch.
3. Record the full selected commit with `git rev-parse HEAD`. Run the repository's `./scripts/python_runtime.sh scripts/git_state.py --json` for the lane state. Verify the advertised remote separately; that script's NOT_CHECKED value is not remote proof.
4. Read the [original architecture](../excel-dna-xll-product-architecture-decision.md), [current plan](current-plan.md) and [Windows packet](windows-p0-task.txt) before explaining phases. Compare their bytes/hashes with the [source manifest](source-manifest.json) when checking an intake or suspected drift.
5. Read [the learning record](learning/README.md). Resume the pending observation; do not invent completion from expected output or a repository commit.

If a source is missing, retrieve that exact file from the identified revision. If it differs, inspect the change. Report an unresolved discrepancy instead of substituting a similarly named plan. An older task whose directory cannot be changed can issue commands with an explicit verified checkout directory; future tasks should start in the correct project folder.

## Leaving a computer

Finish the current-plan/learning updates before the commit, stage only intended files and use the repository's normal hooks and PR checks. Preserve source/proposal/evidence distinctions. Push the task branch and verify its remote hash before reporting that another computer can retrieve it. Use one writer device per branch.

Record this short handoff outside the frozen candidate after publication:

```text
Repository: https://github.com/Pravin-surawase/structural_engineering_lib
Branch: actual branch
Commit: full selected/pushed commit ID
Shared status: local only / remote branch verified / merged and verified
Start: docs/planning/xll-product/README.md
Current scope: shell-only Windows P0; see the preserved packet
Observed learning result: actual result, or pending
Open issue / next action: current concrete description
```

The source manifest describes the intake, not live GitHub status. Query GitHub for later publication/merge facts. Windows installed Excel/ETABS evidence remains machine-specific; fetching the same source on Mac does not recreate it.
