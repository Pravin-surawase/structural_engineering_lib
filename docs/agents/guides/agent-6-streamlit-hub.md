# Agent 6 Streamlit Hub

**Role:** Streamlit UI Specialist
**Owner:** Agent 6
**Status:** Active

---

## Purpose

This is your navigation hub for all Streamlit-related documentation.
Start here, find what you need, get back to work.

---

## Quick Links

### 🚀 START HERE (New Agents)

| Document | Purpose |
|----------|---------|
| **[Comprehensive Onboarding](agent-6-comprehensive-onboarding.md)** | **Full onboarding with guard rails, coding standards, scanner usage** |
| [Quick Start](agent-6-quick-start.md) | 5-minute overview |

### Core Documentation

| Document | Purpose |
|----------|---------|
| [Streamlit Maintenance Guide](../../contributing/streamlit-maintenance-guide.md) | Day-to-day maintenance |
| [Prevention System](../../contributing/streamlit-comprehensive-prevention-system.md) | Error prevention patterns |
| [Issues Catalog](../../contributing/streamlit-issues-catalog.md) | Known issues + solutions |
| [Validation Reference](../../reference/streamlit-validation.md) | Validation patterns |
| [Code Files Analysis](../../research/streamlit-code-files-analysis.md) | File-by-file deep dive, scanner results |

### Planning & Tasks

| Document | Purpose |
|----------|---------|
| [Agent 6 Tasks](../../planning/agent-6-tasks-streamlit.md) | Full task history + details |
| [v0.17.5 Tasks in TASKS.md](../../TASKS.md) | Current sprint tasks (TASK-401-437) |

### App Structure

| Location | Contents |
|----------|----------|
| `streamlit_app/Home.py` | Main entry point |
| `streamlit_app/pages/` | Individual calculator pages |
| `streamlit_app/utils/` | Shared utilities |
| `streamlit_app/tests/` | Test suite |
| `streamlit_app/config/` | Configuration files |

---

## Validation Commands

```bash
# Run all Streamlit tests
cd streamlit_app && pytest tests/ -v

# Check for code issues (AST scanner)
.venv/bin/.venv/bin/python scripts/check_streamlit_issues.py --all-pages

# Run pylint on Streamlit code
.venv/bin/python -m pylint --rcfile=.pylintrc-streamlit streamlit_app/

# Start the app locally
cd streamlit_app && streamlit run Home.py
```

---

## Prevention System Overview

Agent 6 uses a **3-layer prevention system** to catch issues before they reach users:

1. **AST Scanner** (`check_streamlit_issues.py`)
   - Detects: NameError, ZeroDivisionError, AttributeError, KeyError
   - Runs: Pre-commit hook + CI

2. **Pylint** (`.pylintrc-streamlit`)
   - Style + code quality checks
   - Runs: Pre-commit hook + CI

3. **Unit Tests** (`streamlit_app/tests/`)
   - Functional verification
   - Runs: CI on every PR

---

## Session Workflow

1. **Start:** Check [agent-6-tasks-streamlit.md](../../planning/agent-6-tasks-streamlit.md) for priorities
2. **Develop:** Implement features with tests
3. **Validate:** Run scanner + pylint + tests
4. **Commit:** Use Agent 8 workflow (`./scripts/ai_commit.sh`)
5. **Document:** Update task status + session log

---

## Related Agents

| Agent | Collaboration |
|-------|---------------|
| [Agent 8](agent-8-automation.md) | Git operations for commits |
| [Agent 9](agent-9-quick-start.md) | Governance and structure |

---

## Archived Documentation

For historical reference only:
- [Agent 6 Status Analysis (archived)](../../_archive/2026-01/agent-6-streamlit-status-analysis.md)
