# Agent Bootstrap

> **Read this first.** This is the fastest path to productive work.

> **👤 For users onboarding a new agent:** See [contributing/agent-onboarding-message.md](contributing/agent-onboarding-message.md) for the exact message to send.

---

## 🚀 First 30 Seconds

```bash
# Run this immediately:
.venv/bin/python scripts/start_session.py
```

This shows: version, branch, active tasks, blockers, and doc freshness.

---

## 📖 Required Context

| Priority | Document | Why |
|----------|----------|-----|
| 1 | [AI_CONTEXT_PACK.md](AI_CONTEXT_PACK.md) | Project summary, layers, golden rules |
| 2 | [TASKS.md](TASKS.md) | Current work: Active, Up Next, Backlog |
| 3 | [planning/next-session-brief.md](planning/next-session-brief.md) | What happened last, what's blocked |

---

## ⚙️ Key Commands

```bash
# Tests
.venv/bin/python -m pytest Python/tests -q

# Format check
.venv/bin/python -m black Python/ --check

# End session
.venv/bin/python scripts/end_session.py
```

---

## 📍 Quick Reference

- **Copilot rules:** [../.github/copilot-instructions.md](../.github/copilot-instructions.md)
- **Git workflow (CRITICAL):** [GIT_WORKFLOW_AI_AGENTS.md](GIT_WORKFLOW_AI_AGENTS.md) ⚠️
- **Automation scripts (41):** [reference/automation-catalog.md](reference/automation-catalog.md) 🤖
- **Handoff quick start:** [HANDOFF.md](HANDOFF.md)
- **API docs:** [reference/api.md](reference/api.md)
- **Known pitfalls:** [reference/known-pitfalls.md](reference/known-pitfalls.md)
- **Recent issues:** [contributing/session-issues.md](contributing/session-issues.md)
- **Agent roles:** [../agents/README.md](../agents/README.md)
- **Project status:** [planning/project-status.md](planning/project-status.md) (quick) or [planning/project-status-deep-dive.md](planning/project-status-deep-dive.md) (detailed)

---

*Don't hardcode stats here — run `start_session.py` for live data.*
