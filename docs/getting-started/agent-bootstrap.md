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

## 🌐 Verify Online for Volatile Info

If information is likely to change, verify it online before using it:
- Model names and availability
- Library/framework versions
- CLI flags and API endpoints

## ⚠️ Frontend Compatibility (React + R3F + Drei + Dockview)

Before setting up the React UI stack, confirm dependency alignment:
- R3F v9 is the React 19 compatibility release; if you are on React 18, use the prior major (v8) and verify peer deps.
- Drei 10.7.x peers React ^19 and @react-three/fiber ^9.
- Dockview peer range allows React >=16.8, but still run a smoke test.

Quick check:
```bash
npm ls react react-dom @react-three/fiber @react-three/drei dockview
```

Smoke test: render a Dockview layout plus a basic R3F `<Canvas>` scene in dev and production builds.

---

## 📚 Duplication Prevention

**Before creating ANY new document:**

```bash
# Check if a canonical doc already exists
.venv/bin/python scripts/check_doc_similarity.py "your topic"
```

**Canonical registry:** [docs-canonical.json](../docs-canonical.json) maps topics → single source of truth.

**Naming rules:** [doc-naming-conventions.md](../guidelines/doc-naming-conventions.md)

---

## ⚙️ Quick Commands & Checklists

Use the [agent-quick-reference.md](../agents/guides/agent-quick-reference.md) card for
commands, API touchpoints, scanner usage, and emergency workflows.

---

## 📍 Essential Links

- **Copilot rules:** [../../.github/copilot-instructions.md](../../.github/copilot-instructions.md)
- **Git workflow (CRITICAL):** [../contributing/git-workflow-ai-agents.md](../contributing/git-workflow-ai-agents.md) ⚠️
- **Automation scripts:** [../reference/automation-catalog.md](../reference/automation-catalog.md) 🤖
- **Known pitfalls:** [../reference/known-pitfalls.md](../reference/known-pitfalls.md)
- **Session issues:** [../contributing/session-issues.md](../contributing/session-issues.md)
- **API docs:** [../reference/api.md](../reference/api.md)
- **FastAPI REST API:** [../reference/fastapi-rest-api.md](../reference/fastapi-rest-api.md) 🚀
- **Docker guide:** [../learning/docker-fundamentals-guide.md](../learning/docker-fundamentals-guide.md) 🐳

---

## 🐳 Docker Quick Start (FastAPI Backend)

```bash
# Check Docker is running
docker --version

# Run FastAPI in container (production)
docker compose up --build

# Run with hot reload (development)
docker compose -f docker-compose.dev.yml up --build

# Stop containers
docker compose down

# Validate Docker config
.venv/bin/python scripts/check_docker_config.py
```

**API at:** http://localhost:8000/docs

---

## 📇 Machine-Readable Indexes

- `scripts/automation-map.json` (task → script)
- `docs/docs-canonical.json` (topic → canonical doc)
- `scripts/index.json` + `docs/docs-index.json` (automation + docs catalog)

**Automation lookup:** `.venv/bin/python scripts/find_automation.py "your task"`

---

## 🧭 Task → Context Quick Start

1. Run: `.venv/bin/python scripts/find_automation.py "your task"`
2. Open the **Context docs** listed in the output
3. If none, check `scripts/automation-map.json` + `docs/docs-index.json`

---

*Don't hardcode stats here — run `./scripts/agent_start.sh --quick` for live data.*
