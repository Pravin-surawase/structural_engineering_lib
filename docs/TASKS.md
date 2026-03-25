# Task Board

> **Single source of truth for active work.** Keep it short and current.

**Updated:** 2026-03-25 (Session 96 — nav + audit: no new pages needed)

---

## Rules (read first)
- **WIP = 2** (max 2 active tasks at once)
- **Done = tests pass + docs updated + scanner passes**
- **Archive rule:** Move completed items to [tasks-history.md](_archive/tasks-history.md) after 20+ items
- **No new Streamlit work** — all new features go to React. Bug fixes only for Streamlit-only features.

---

## Current Release

- **Version:** v0.19.1 ✅ Complete → v0.20 (V3 Foundation)
- **Focus:** React migration — port remaining Streamlit-only features to React
- **Target:** v0.20 — batch design UI, compliance checker, cost optimizer in React
- **Vision:** [democratization-vision.md](planning/democratization-vision.md) — AI chat, automation, library evolution

### Release Roadmap

| Version | Focus | Status | Key Deliverables |
|---------|-------|--------|------------------|
| **v0.19.1** | AI Tools + UX | ✅ DONE | Dashboard insights, code checks, ExportPanel, rebar suggestions |
| **v0.20** | V3 Foundation | 🔄 ACTIVE | Batch design React UI, compliance page, cost optimizer page |
| **v0.21** | Full React | 📋 NEXT | AI assistant port, learning center, Streamlit deprecation |

### Migration Status (React vs Streamlit)

| Feature | Streamlit | React | API Ready | Priority |
|---------|-----------|-------|-----------|----------|
| Single beam design | ✅ | ✅ | ✅ | Done |
| CSV import (40+ cols) | ✅ | ✅ | ✅ | Done |
| 3D visualization | ✅ | ✅ R3F | ✅ | Done |
| Export (BBS/DXF/Report) | ✅ | ✅ | ✅ | Done |
| Dashboard insights | ✅ | ✅ | ✅ | Done |
| Rebar suggestions | ✅ | ✅ | ✅ | Done |
| **Batch design UI** | ✅ | ✅ | ✅ streaming.py | Done |
| **Compliance checker** | ✅ | ✅ DesignView panel | ✅ insights.py | Done |
| **Cost optimizer** | ✅ | ✅ DesignView rebar | ✅ optimization.py | Done |
| **AI Assistant** | ✅ | -- | Partial | 🟡 Medium |
| Learning center | ✅ | -- | -- | 🟢 Low |

---

## Active

| ID | Task | Agent | Status |
|----|------|-------|--------|
| — | TopBar nav + ModeSelect quick links | Copilot | 🔄 In progress |

## Up Next

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| TASK-505 | Test e2e with Docker + React (13 routers) | — | 0.5d | 🟡 Medium | 📋 |
| — | Wire BuildingEditor Cost tab (placeholder → real data) | — | 0.5d | 🟢 Low | 📋 |

## Backlog

| ID | Task | Priority | Notes |
|----|------|----------|-------|
| TASK-513 | React: AI assistant port | 🟡 Medium | Needs OpenAI/LLM integration design for React |
| — | 28 unit conversion warnings | 🟢 Low | Informational, not bugs. Self-documenting via `_nmm`/`_knm` var names. |
| — | 287 legacy import warnings (Streamlit) | 🟢 Low | Won't fix — will go away when Streamlit is deprecated |

## Recently Done

| ID | Task | Agent | Status |
|----|------|-------|--------|
| TASK-510 | React: Batch design page with SSE progress + `/batch` route | Copilot | ✅ Done (merged to main) |
| TASK-511 | Compliance checker — **already exists** (useCodeChecks + DesignView panel) | — | ✅ Not needed |
| TASK-512 | Cost optimizer — **already exists** (useRebarSuggestions + DesignView panel) | — | ✅ Not needed |
| TASK-509 | Type annotations: Streamlit 100% coverage (19 files, PR #438) | Copilot | ✅ Done |
| — | Phase 1+2 cleanup: delete stale files + Streamlit deprecation markers | Copilot | ✅ Done (`ec62ed0`) |
| TASK-502 | Code-split React bundle: lazy routes + manual chunks (1,158→67 kB main) | Copilot | ✅ Done |
| TASK-501 | Fix pre-existing check_all.py failures (19/28 → 25/28) | Copilot | ✅ Done (PR #437) |
| TASK-508 | Split ai_workspace.py into 6 modules (5103→5314 lines, 7 files) | Copilot | ✅ Done (`b9b2733`) |
| TASK-503 | Wire REST fallback in DesignView (WS disconnect → REST auto-design) | Copilot | ✅ Done (`cad5e24`) |
| TASK-506 | React test infra: Vitest + 5 test suites (23 tests) | Copilot | ✅ Done (`ff3a937`) |
| TASK-507 | Fix arch violations: stub imports in Streamlit + delete dead test | Copilot | ✅ Done (`0e6657e`) |
| TASK-500 | Unified CLI + onboarding audit (run.sh, check_all.py, 28 checks) | Claude | ✅ Done (PR #436) |
| TASK-499 | AI agent efficiency + git workflow improvements | Claude | ✅ Done (`a9bf35e`) |

## Archive

Sessions 32–73 and legacy TASK items have been completed. See [docs/_archive/tasks-history.md](_archive/tasks-history.md) for details.

Key milestones from archived sessions:
- **Session 73** (Jan 24): FastAPI skeleton (20 routes, 31 tests), WebSocket endpoint, `discover_api_signatures.py`
- **Session 66** (Jan 24): V3 automation foundation, 143 scripts audited, API latency validated
- **Session 65** (Jan 23): Agent effectiveness research, `docs-canonical.json`, `automation-map.json`
- **Session 63** (Jan 23): Rebar consolidation, scanner fixes, TASK-350/351/352 resolved
- **Sessions 32–62c** (Jan 22): Rebar editor, DXF export, cost optimizer, section geometry

---

**Session logs:** See [SESSION_LOG.md](SESSION_LOG.md) for detailed history.
**Task history:** See [_archive/tasks-history.md](_archive/tasks-history.md)
