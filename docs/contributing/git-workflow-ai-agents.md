---
owner: Main Agent
status: active
last_updated: 2026-08-09
doc_type: guide
complexity: beginner
tags: [git, github, codex]
---

# Git Workflow for AI Agents

The canonical workflow is
[git-workflow-single-source.md](../git-automation/git-workflow-single-source.md).

In short: repository automations do not own Git or GitHub. Codex inspects and
scopes the diff, performs ordinary commits and pushes, and manages PRs through
the connected GitHub integration. Standard validation hooks may run, but custom
wrapper-enforcement hooks are not installed.

Destructive or history-changing actions—including merge, branch deletion,
issue closure, release, force push, amend of published history, and reset—need
explicit user confirmation. Unclear Git state is a stop condition, not a reason
to invoke automated recovery.
