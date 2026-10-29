---
owner: Main Agent
status: active
last_updated: 2026-10-29
doc_type: guide
complexity: intermediate
tags: [agents, coding, navigation]
---

# AI Agent Coding Guide

**Type:** Guide
**Audience:** Developers and AI agents
**Status:** Active
**Importance:** High
**Last Updated:** 2026-10-29

Use [AGENTS.md](../../AGENTS.md) for the execution contract and the canonical
[Agent Coding Standards](../contributing/agent-coding-standards.md) for code
conventions. The earlier January migration inventory, Streamlit instructions,
mandatory all-suite loops and stub-owned API examples on this page are retired.
Their historical versions remain in Git; they are not current instructions.

## Start and locate the owner

Verify the actual checkout, source binding, branch/upstream, diff and task scope.
Start one exact task with `./run.sh session begin --task-id <task> --agent <role>`
from the repository root. Resolve placeholders to the selected real task and role.
Search exact symbols/callers with `rg`; use a bounded context area only when
needed. Do not load large agent catalogs or historical logs by default.

Implementation follows Core types ← IS 456 code ← Services ← UI/IO. Core has no
IS 456 math; code calculations have no I/O. `services/api.py` is the service
owner; the root `api.py` is a compatibility stub. Typed family facades are the
promoted task APIs, with individual support limits in [API levels](../reference/api-levels.md).

## Implement and verify

Keep one writer for shared/generated files. Finish the selected implementation,
focused tests and documentation as a cohesive batch, then format/lint and verify
the affected outcomes once. Use `./scripts/python_runtime.sh` for repository
Python commands. Preserve explicit units, input/source identity, effective-depth
and physical-layout checks, and meaningful FAIL/HOLD/unavailable results.
Do not convert missing evidence into a default or PASS.

The [native Git workflow](../git-automation/git-workflow-single-source.md)
owns stage/commit/push/PR/check/merge. The [efficiency policy](../guidelines/ai-token-efficiency.md)
owns agent/model and frozen-batch choices. Required hosted checks are retained;
full local suites need a concrete task risk or release reason. Do not mutate
files while claiming to perform read-only validation.

## Finish with evidence

Review the essential final diff and its actual maintained consumers. Record the
root cause, fix and relevant checks in the PR. Close the task usage checkpoint.
Keep a handoff for unfinished work or a real device/worktree/artifact transition;
do not manufacture routine SESSION_LOG/WORKLOG updates or release approval.
Software review and CI do not replace qualified engineering or installed-host
acceptance. Follow the canonical guides above when an old example conflicts.
