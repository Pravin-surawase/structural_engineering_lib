---
owner: Main Agent
status: active
last_updated: 2026-08-15
doc_type: hub
complexity: beginner
tags: [git, github, codex]
---

# Codex-Native Git and GitHub

The repository no longer uses commit, push, recovery, or pull-request shell
wrappers. Codex performs the normal Git and GitHub lifecycle directly while
preserving unrelated work and respecting approval gates.

Read [Codex-Native Git and GitHub Workflow](git-workflow-single-source.md) for
the authoritative process, recovery boundary, verification ladder, and
owner-approved operations.

Worked learning records:

- [Column PMM recovery](git-recovery-case-study-column-pmm.md) — preserve stale
  unique work, selectively recover current-compatible intent, and verify
  source/engineering/integration evidence separately.
- [GIT-7D2 and cleanup audit](git-governance-case-study-git-7d2-cleanup-audit.md)
  — bind disposition evidence to exact identities, preserve `NOT_CHECKED`, and
  distinguish holds, future candidates, and separate deletion approvals.

Historical Git-automation documents under `docs/_archive/` remain evidence only.
