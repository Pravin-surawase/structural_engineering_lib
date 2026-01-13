# Agent Bootstrap

**Type:** Guide
**Audience:** All Agents
**Status:** Approved
**Importance:** Critical
**Version:** 2.0.0
**Created:** 2026-01-08
**Last Updated:** 2026-01-13

---

> **Read this first.** This is the fastest path to productive work.

> **👤 For users onboarding a new agent:** See [../contributing/agent-onboarding-message.md](../contributing/agent-onboarding-message.md) for the exact message to send.

---

## 🚀 First 30 Seconds

```bash
# RECOMMENDED: Quick mode (6s, 54% faster, sufficient for 95% of sessions)
./scripts/agent_start.sh --quick

# OPTIONAL: Full validation (13s, use when debugging)
./scripts/agent_start.sh

# With agent-specific guidance:
./scripts/agent_start.sh --agent 9 --quick   # For governance agents
./scripts/agent_start.sh --agent 8 --quick   # For git/automation agents
./scripts/agent_start.sh --agent 6 --quick   # For UI agents
```

This shows: version, branch, active tasks, blockers, and agent-specific commands.

---

## 📖 Required Context

| Priority | Document | Why |
|----------|----------|-----|
| 1 | [ai-context-pack.md](ai-context-pack.md) | Project summary, layers, golden rules |
| 2 | [TASKS.md](../TASKS.md) | Current work: Active, Up Next, Backlog |
| 3 | [next-session-brief.md](../planning/next-session-brief.md) | What happened last, what's blocked |

---

## ✅ API Touchpoints Checklist (When Changing Public API)

1. Update exports in `Python/structural_lib/api.py` (`__all__`).
2. Update docs in `docs/reference/api.md` and `docs/reference/api-stability.md`.
3. Regenerate the manifest:
   `./.venv/bin/python scripts/generate_api_manifest.py`
4. Run API checks:
   `./.venv/bin/python scripts/check_api_doc_signatures.py`

Keep public signatures stable unless explicitly approved.

---

## ⚙️ Key Commands

```bash
# Tests
.venv/bin/python -m pytest Python/tests -q

# Format check
.venv/bin/python -m black Python/ --check

# Streamlit validation (run before committing Streamlit changes)
.venv/bin/python scripts/check_streamlit_issues.py --all-pages
# Expected: Critical: 0, High: 123 (as of 2026-01-09)

# End session
.venv/bin/python scripts/end_session.py
```

---

## 📍 Quick Reference

- **Copilot rules:** [../../.github/copilot-instructions.md](../../.github/copilot-instructions.md)
- **Git workflow (CRITICAL):** [../contributing/git-workflow-ai-agents.md](../contributing/git-workflow-ai-agents.md) ⚠️
- **Automation scripts:** [../reference/automation-catalog.md](../reference/automation-catalog.md) 🤖
- **Handoff quick start:** [../contributing/handoff.md](../contributing/handoff.md)
- **Background agent guide:** [../contributing/background-agent-guide.md](../contributing/background-agent-guide.md)
- **API docs:** [../reference/api.md](../reference/api.md)
- **Known pitfalls:** [../reference/known-pitfalls.md](../reference/known-pitfalls.md)
- **Recent issues:** [../contributing/session-issues.md](../contributing/session-issues.md)
- **Agent roles:** [../agents/README.md](../agents/README.md)
- **Project status:** [../planning/project-status.md](../_archive/planning/project-status.md) (quick) or [../planning/project-status-deep-dive.md](../planning/project-status-deep-dive.md) (detailed)

---

## 🧠 Automation-First Mentality

> **CRITICAL: If you see 10+ similar issues → Build automation FIRST!**

| Principle | What It Means |
|-----------|---------------|
| **Pattern Recognition** | 10+ issues = automation script, not manual fixes |
| **Research First** | Check `scripts/` before writing new tools |
| **Full Sessions** | 5-10+ commits, don't stop early |
| **Document Always** | Update TASKS.md, SESSION_LOG after work |

### Quick Automation
```bash
python scripts/fix_broken_links.py --fix      # Fix links
python scripts/validate_folder_structure.py   # Check structure
python scripts/check_doc_versions.py --fix    # Fix versions
```

---

*Don't hardcode stats here — run `start_session.py` for live data.*
