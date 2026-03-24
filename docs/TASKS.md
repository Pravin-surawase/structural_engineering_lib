# Task Board

> **Single source of truth for active work.** Keep it short and current.

**Updated:** 2026-03-25 (Session 94 — weak points audit)

---

## Rules (read first)
- **WIP = 2** (max 2 active tasks at once)
- **Done = tests pass + docs updated + scanner passes**
- **Archive rule:** Move completed items to [tasks-history.md](_archive/tasks-history.md) after 20+ items

---

## Current Release

- **Version:** v0.19.1 ✅ Complete → v0.20 (V3 Foundation)
- **Focus:** V3 React UI — all API + hooks ready, now wiring UX polish + REST fallback
- **Target:** v0.20 — code-split bundles, SSE batch progress, REST fallback
- **Vision:** [democratization-vision.md](planning/democratization-vision.md) — AI chat, automation, library evolution

### Release Roadmap

| Version | Focus | Status | Key Deliverables |
|---------|-------|--------|------------------|
| **v0.18.1** | AI v2 Bugfix | ✅ DONE | PR #393 (CSV import fix) |
| **v0.19.0** | Phase 4 + Launch | ✅ RELEASED | DXF polish, AI model fix, Streamlit API index |
| **v0.19.1** | AI Tools + UX | ✅ DONE | Dashboard insights, code checks, ExportPanel, rebar suggestions |
| **v0.20** | V3 Foundation | 📋 NEXT | Code-splitting, SSE progress, REST fallback, governance |
| **v0.21+** | V3 React | 📋 PLANNED | React + R3F + FastAPI (6-week migration) |

---

## Active

| ID | Task | Agent | Status |
|----|------|-------|--------|
| TASK-501 | Fix pre-existing check_all.py failures + expand audit | Copilot | 🔄 In Progress |

## Up Next

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| TASK-506 | React test infra: Vitest + 5 smoke tests (DesignView, useLiveDesign, useCSVFileImport…) | — | 2d | 🔴 Critical | 📋 |
| TASK-507 | Fix 293 arch violations: 2-line Streamlit stub fix + legacy test imports | — | 0.5d | 🟡 Moderate | 📋 |
| TASK-502 | Code-split Three.js + react-three-fiber + lazy-load routes (1.16 MB chunk) | — | 1d | 🟠 High | 📋 |
| TASK-503 | Wire REST fallback in DesignView (useAutoDesign on WS disconnect) | — | 0.5d | 🟠 High | 📋 |
| TASK-508 | Split ai_workspace.py (5103 lines → 6 modules) | — | 2d | 🟠 High | 📋 |
| TASK-504 | Add SSE batch progress UI (streaming.py → React) | — | 1d | Medium | 📋 |
| TASK-505 | Test e2e with Docker + React (13 routers) | — | 0.5d | Medium | 📋 |
| TASK-509 | Type annotations: Streamlit pages (49 return types + 4 __all__) | — | 1d | 🟢 Low | 📋 |

## Backlog

| ID | Task | Priority | Notes |
|----|------|----------|-------|
| TASK-506 | Set up React test infrastructure (Vitest + 5 smoke tests) | 🔴 Critical | Must exist before TASK-502/503 refactors. See [weak-points-audit.md](planning/weak-points-audit.md#wp-1) |
| TASK-507 | Fix 293 arch violations: 2-line Streamlit fix + legacy test imports | 🟡 Moderate | Fast win: `02_cost_optimizer.py:42`, `api_wrapper.py:47`. See [weak-points-audit.md](planning/weak-points-audit.md#wp-3) |
| TASK-508 | Split `ai_workspace.py` (5103 lines → 6 modules) | 🟠 High | Dedicated PR only; do after TASK-506. See [weak-points-audit.md](planning/weak-points-audit.md#wp-4) |
| TASK-509 | Type annotations: 49 missing return types + 4 missing `__all__` (Streamlit) | 🟢 Low | Core already passes mypy. See [weak-points-audit.md](planning/weak-points-audit.md#wp-6) |
| — | 28 unit conversion warnings | 🟢 Low | `* 1000`/`/ 1000` in IS 456 code. Informational, not bugs. Self-documenting via `_nmm`/`_knm` var names. |

## Recently Done

| ID | Task | Agent | Status |
|----|------|-------|--------|
| TASK-500 | Unified CLI + onboarding audit (run.sh, check_all.py, 28 checks) | Claude | ✅ Done (PR #436) |
| TASK-499 | AI agent efficiency + git workflow improvements | Claude | ✅ Done (`a9bf35e`) |
| TASK-498 | Full repo folder audit (11 batches) + agent logging rules | Claude | ✅ Done (Session 91) |
| TASK-497 | React dashboard insights + code checks + rebar suggestions | Claude | ✅ Done (PR #431) |
| TASK-496 | ExportPanel (BBS CSV / DXF / HTML report) | Claude | ✅ Done (PR #432) |
| TASK-495 | 4-layer governance lock + migration gates | Claude | ✅ Done (PR #430) |
| TASK-494 | Scripts consolidation Phase 1–3 (79 active scripts) | Claude | ✅ Done (PR #428, #429) |
| TASK-493 | Fix 280+ stale doc references across 45+ files | Claude | ✅ Done (`6a5ee84`) |

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
