# Task Board

> **Single source of truth for active work.** Keep it short and current.

**Updated:** 2026-03-23 (Session 91)

---

## Rules
- **WIP = 2** (max 2 active tasks at once)
- **Done = tests pass + docs updated + scanner passes**
- **Archive rule:** Move completed items to [tasks-history.md](_archive/tasks-history.md) after 20+ items

---

## Current Focus

- **Version:** v0.19.1 ✅ Complete → v0.20 (V3 Foundation)
- **Focus:** V3 React UI — all API + hooks ready, now wiring UX polish + REST fallback
- **Target:** v0.20 — code-split bundles, SSE batch progress, REST fallback
- **Vision:** [democratization-vision.md](planning/democratization-vision.md) — AI chat, automation, library evolution

---

## Release Roadmap

| Version | Focus | Status | Key Deliverables |
|---------|-------|--------|------------------|
| **v0.18.1** | AI v2 Bugfix | ✅ DONE | PR #393 (CSV import fix) |
| **v0.19.0** | Phase 4 + Launch | ✅ RELEASED | DXF polish, AI model fix, Streamlit API index |
| **v0.19.1** | AI Tools + UX | ✅ DONE | Dashboard insights, code checks, ExportPanel, rebar suggestions |
| **v0.20** | V3 Foundation | 📋 NEXT | Code-splitting, SSE progress, REST fallback, governance |
| **v0.21+** | V3 React | 📋 PLANNED | React + R3F + FastAPI (6-week migration) |

---

## Completed Last Sessions (Sessions 81–90)

| Task | Status | PR |
|------|--------|-----|
| Wire dashboard insights into React DashboardPage | ✅ Done | PR #431 |
| Add live code check badges to DesignView (CodeChecksPanel) | ✅ Done | PR #431 |
| Add rebar suggestion panels to DesignView (RebarSuggestionsPanel) | ✅ Done | PR #431 |
| Create ExportPanel (BBS CSV / DXF / HTML report) | ✅ Done | PR #432 |
| Add 4-layer governance lock + migration gates | ✅ Done | PR #430 |
| Scripts consolidation Phase 1 + Phase 2 (79 active scripts) | ✅ Done | PR #428, #429 |
| Create _lib/output.py + _lib/ast_helpers.py (Phase 3) | ✅ Done | `c80f454` |
| Fix 280+ stale doc references across 45+ files | ✅ Done | `6a5ee84` |

## Active

- None active

## Up Next (v0.20 Sprint)

- **Code-split Three.js + react-three-fiber** — `index.js` chunk is 1.16 MB (above 500 kB advisory)
- **Add REST fallback when WebSocket unavailable** — `DesignView` currently requires WS
- **Add SSE batch progress UI** — `streaming.py` router exists, needs React consumer
- **Test e2e with Docker + React** — verify all 13 routers respond correctly end-to-end
- **Update OpenAPI snapshot** (`openapi_baseline.json`) to reflect current 13 routers
- **Scripts Phase 3 completion** — migrate 10 more scripts to use `_lib/utils.py`

---

## Archived Sessions

Sessions 32–73 and legacy TASK items have been completed. See [tasks-history.md](_archive/tasks-history.md) for details.

Key milestones from archived sessions:
- **Session 73** (Jan 24): FastAPI skeleton (20 routes, 31 tests), WebSocket endpoint, `discover_api_signatures.py`
- **Session 66** (Jan 24): V3 automation foundation, 143 scripts audited, API latency validated
- **Session 65** (Jan 23): Agent effectiveness research, `docs-canonical.json`, `automation-map.json`
- **Session 63** (Jan 23): Rebar consolidation, scanner fixes, TASK-350/351/352 resolved
- **Sessions 32–62c** (Jan 22): Rebar editor, DXF export, cost optimizer, section geometry

---

## Notes

- **Session logs:** See [SESSION_LOG.md](SESSION_LOG.md) for detailed history
- **Task history:** See [_archive/tasks-history.md](_archive/tasks-history.md)
