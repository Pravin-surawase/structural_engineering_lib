---
owner: Main Agent
status: active
last_updated: 2026-08-09
doc_type: guide
complexity: intermediate
tags: [git, github, codex]
---

# GitHub Workflow Guide

Codex owns the repository's Git and GitHub lifecycle. The old shell wrappers
that staged everything, synchronized branches, pushed, created PRs, or attempted
recovery have been retired.

Follow the canonical
[Codex-native Git/GitHub workflow](../git-automation/git-workflow-single-source.md).

## Pull request policy

Use a task branch and PR for production code, API changes, CI workflows,
dependencies, release changes, and coordinated multi-module work. A tiny
documentation-only correction may use the repository's existing branch policy,
but Codex must still inspect and scope the diff before committing.

## Normal flow

1. Codex inspects the current branch, worktree, upstream, and any existing PR.
2. Codex creates or switches to a `codex/<task-slug>` branch when a task branch
   is needed.
3. The implementation is verified with targeted checks and the appropriate
   closeout gate.
4. Codex stages only intended paths and creates a conventional commit.
5. Codex pushes without force or history rewriting.
6. Codex creates or updates a draft PR through the connected GitHub integration.
7. Codex reports the PR and CI state. Merge remains an explicit
   user-confirmation action.

## Failure handling

If the branch is detached, conflicted, diverged, or contains an unfinished
operation, stop and inspect the exact state. Do not run an automated recovery
script. Preserve unrelated changes and choose the smallest non-destructive
recovery path only after the evidence is clear.

Never bypass hooks or checks, force push, use `git rebase --skip`, admin-merge,
close an issue, delete a branch, or publish a release without the authority
defined in the canonical workflow.

## CI evidence

Local tests establish local software evidence. Before a PR is described as
ready, inspect the connected GitHub check state as well. Fix failing checks at
their root cause; do not weaken validation to make a lane green.
