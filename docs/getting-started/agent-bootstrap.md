# Agent Bootstrap

**Type:** Guide
**Audience:** All Agents
**Status:** Approved
**Importance:** Critical
**Version:** 2.2.0
**Created:** 2026-01-08
**Last Updated:** 2026-01-23

---

> **Read this first.** This is the fastest path to productive work.

> **👤 For users onboarding a new agent:** See [../contributing/agent-onboarding-message.md](../contributing/agent-onboarding-message.md) for the exact message to send.

---

## Guide Hierarchy

**You are here:** Quick Start (Bootstrap)

| Need | Guide | Use When |
|------|-------|----------|
| **50-Line Essentials** | [agent-essentials.md](agent-essentials.md) | Critical rules only, fits in context |
| **Quick Start** | This document | First 30 seconds, immediate productivity ← **YOU ARE HERE** |
| **Quick Reference** | [agent-quick-reference.md](../agents/guides/agent-quick-reference.md) | Cheat sheet, emergency commands |
| **Complete Guide** | [agent-workflow-master-guide.md](../agents/guides/agent-workflow-master-guide.md) | Decision trees, troubleshooting, deep patterns |

---

## ⚡ Ultra-Short Version (Context-Efficient)

For minimal context loading, just read [agent-essentials.md](agent-essentials.md) — 50 lines with the critical rules.

---

## First 30 Seconds

```bash
# RECOMMENDED: Quick mode (6s, 54% faster, sufficient for 95% of sessions)
./scripts/agent_start.sh --quick

# OPTIONAL: Full validation (13s, use when debugging)
./scripts/agent_start.sh

# With agent-specific guidance:
./scripts/agent_start.sh --agent 9 --quick   # For governance agents
./scripts/agent_start.sh --agent 8 --quick   # For git/automation agents
./scripts/agent_start.sh --agent 6 --quick   # For UI agents

# Background agent worktree:
./scripts/agent_start.sh --worktree AGENT_5 --quick
```

This shows: version, branch, active tasks, blockers, and agent-specific commands.

---

## 📖 Required Context

| Priority | Document | Why |
|----------|----------|-----|
| 0 | [agent-essentials.md](agent-essentials.md) | **50 lines** — Critical rules, fits in any context |
| 1 | [ai-context-pack.md](ai-context-pack.md) | Project summary, layers, golden rules |
| 2 | [TASKS.md](../TASKS.md) | Current work: Active, Up Next, Backlog |
| 3 | [next-session-brief.md](../planning/next-session-brief.md) | What happened last, what's blocked |

---

## 📚 Duplication Prevention

**Before creating ANY new document:**

```bash
# Check if a canonical doc already exists
.venv/bin/python scripts/check_doc_similarity.py "your topic"
```

**Canonical registry:** [docs-canonical.json](../docs-canonical.json) maps topics → single source of truth.

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

# End session
.venv/bin/python scripts/end_session.py
```

---

## � Scanner & Validation

The scanner (`check_streamlit_issues.py`) detects runtime crash risks:
- **ZeroDivisionError** - Division without zero checks
- **KeyError/IndexError** - Dict/list access without validation
- **NameError** - Undefined variables
- **Import issues** - Imports inside functions

**Key files:**
- [.scanner-ignore.yml](../../.scanner-ignore.yml) - False positive suppressions
- [docs/research/scanner-improvements.md](../research/scanner-improvements.md) - Scanner research

**Current state (2026-01-23):** 25 issues (0 critical, 0 high) across all pages.

---

## �📍 Quick Reference

- **Copilot rules:** [../../.github/copilot-instructions.md](../../.github/copilot-instructions.md)
- **Git workflow (CRITICAL):** [../contributing/git-workflow-ai-agents.md](../contributing/git-workflow-ai-agents.md) ⚠️
- **Automation scripts:** [../reference/automation-catalog.md](../reference/automation-catalog.md) 🤖
- **Handoff quick start:** [../contributing/handoff.md](../contributing/handoff.md)
- **Background agent guide:** [../contributing/background-agent-guide.md](../contributing/background-agent-guide.md)
- **API docs:** [../reference/api.md](../reference/api.md)
- **Known pitfalls:** [../reference/known-pitfalls.md](../reference/known-pitfalls.md)
- **Recent issues:** [../contributing/session-issues.md](../contributing/session-issues.md)
- **Agent roles:** [../agents/README.md](../agents/README.md)
- **Project status (archived):** [../_archive/planning/project-status.md](../_archive/planning/project-status.md)
- **Project status (deep dive):** [../planning/project-status-deep-dive.md](../planning/project-status-deep-dive.md)

---

## 📇 Index Files (Machine-Readable)

These JSON indexes help agents discover content programmatically:

| Index | Purpose | Use When |
|-------|---------|----------|
| [scripts/automation-map.json](../../scripts/automation-map.json) | Task → script mapping | **Finding automation for a task** |
| [docs/docs-canonical.json](../docs-canonical.json) | Topic → canonical doc | **Before creating new docs** |
| [scripts/index.json](../../scripts/index.json) | All automation scripts | Finding automation tools |
| [docs/index.json](../index.json) | Documentation structure | Navigating docs |
| [docs/docs-index.json](../docs-index.json) | Document catalog | Finding specific docs |
| [Python/index.json](../../Python/index.json) | Python module structure | Understanding code layout |
| [streamlit_app/API_INDEX.md](../../streamlit_app/API_INDEX.md) | UI components & functions | Working on Streamlit pages |

**Quick automation lookup:**
```bash
.venv/bin/python scripts/find_automation.py "your task"
```

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
.venv/bin/python scripts/fix_broken_links.py --fix      # Fix links
.venv/bin/python scripts/validate_folder_structure.py   # Check structure
.venv/bin/python scripts/check_doc_versions.py --fix    # Fix versions
.venv/bin/python scripts/check_repo_hygiene.py          # Hygiene audit
.venv/bin/python scripts/safe_file_move.py --dry-run old.md new.md
.venv/bin/python scripts/safe_file_delete.py --dry-run old.md
```

---

*Don't hardcode stats here — run `./scripts/agent_start.sh --quick` for live data.*
