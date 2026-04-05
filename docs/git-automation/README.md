# Git Automation for AI Agents

**Type:** Hub
**Audience:** All Agents
**Status:** Production Ready
**Version:** 0.21.4
**Last Updated:** 2026-03-24

---

## Single Source of Truth

**→ [git-workflow-single-source.md](git-workflow-single-source.md)** — Complete reference for the entire git workflow system.

---

## Quick Start (3 Commands)

```bash
./scripts/agent_start.sh --quick              # 1. Session start
./scripts/ai_commit.sh "scope: description"   # 2. Commit (repeat)
.venv/bin/python scripts/session.py end       # 3. Session end
```

## Common Tasks

| Task | Command |
|------|---------|
| Commit changes | `./scripts/ai_commit.sh "message"` |
| Check if PR needed | `./scripts/should_use_pr.sh --explain` |
| Create PR | `./scripts/create_task_pr.sh TASK-XXX "desc"` |
| Finish PR | `./scripts/finish_task_pr.sh TASK-XXX "desc"` |
| Fix git issues | `./scripts/recover_git_state.sh` |

## The One Rule

```bash
# ✅ ALWAYS: ./scripts/ai_commit.sh "message"
# ❌ NEVER:  git add / git commit / git push
```

## Archived Docs

Previous separate guides have been consolidated into the single-source doc:

- [workflow-guide.md](../_archive/git-automation-consolidated/workflow-guide.md) — merged into sections 1, 4, 10
- [automation-scripts.md](../_archive/git-automation-consolidated/automation-scripts.md) — merged into section 3
- [efficient-agent-usage.md](../_archive/git-automation-consolidated/efficient-agent-usage.md) — merged into section 1
- [mistakes-prevention.md](../_archive/git-automation-consolidated/mistakes-prevention.md) — merged into section 14
- [advanced-coordination.md](../_archive/git-automation-consolidated/advanced-coordination.md) — merged into section 11
