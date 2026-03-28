# Task Board

> **Single source of truth for active work.** Keep it short and current.

**Updated:** 2026-03-28 (Session 105 — Agent testing + architecture fixes + shear tests)

---

## Rules (read first)
- **WIP = 2** (max 2 active tasks at once)
- **Done = tests pass + docs updated + scanner passes**
- **Archive rule:** Move completed items to [tasks-history.md](_archive/tasks-history.md) after 20+ items
- **No new Streamlit work** — all new features go to React. Bug fixes only for Streamlit-only features.

---

## Current Release

- **Version:** v0.19.1 ✅ Complete → v0.20 (V3 Foundation) → v0.21 (Library Expansion)
- **Focus:** Library expansion — new Python modules + FastAPI endpoints + React UI
- **Target:** v0.21 — PDF export, load calculator, BOQ, torsion API, Pareto panel, rationalization
- **Vision:** [democratization-vision.md](planning/democratization-vision.md) — AI chat, automation, library evolution
- **Detailed Plan:** [next-phase-improvements-plan.md](planning/next-phase-improvements-plan.md) — code-level specs for all 8 tasks

### Release Roadmap

| Version | Focus | Status | Key Deliverables |
|---------|-------|--------|------------------|
| **v0.19.1** | AI Tools + UX | ✅ DONE | Dashboard insights, code checks, ExportPanel, rebar suggestions |
| **v0.20** | V3 Foundation | ✅ DONE | Batch design React UI, compliance checker, cost optimizer, 86 API tests |
| **v0.21** | React UX + Library Expansion | 🔄 ACTIVE | Editor-centric UX, BeamDetailPanel, FloatingDock, PDF export, load calc, BOQ, torsion |
| **v0.22** | Full React | 📋 NEXT | AI assistant port, learning center, Streamlit deprecation |

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

### v0.21 Feature Matrix

#### React UX Overhaul (new — Phase A quick wins first)

| # | Task ID | Feature | Files | Status |
|---|---------|---------|-------|--------|
| -- | TASK-529 | Column slenderness — `check_column_slenderness`, `get_effective_length_factor`, `get_stress_block_params`, `get_xu_max_ratio` + 28 tests | `slenderness.py`, `materials.py`, `tables.py`, `test_slenderness_column.py` | ✅ Done |
| A1 | TASK-522 | BeamDetailPanel in BuildingEditorPage — beam click → split 3D rebar + results + redesign + edit rebar | `BeamDetailPanel.tsx`, `BuildingEditorPage.tsx`, `Viewport3D.tsx` | ✅ Done (`a242878`, `a5612b0`) |
| A2 | TASK-523 | Activate FloatingDock (already built) + BentoGrid Dashboard (already built) | `App.tsx`, `DashboardPage.tsx` | ✅ Done (`a242878`) |
| A3 | TASK-524 | DesignView dynamic layout — 3D expands when no result, export dropdown | `DesignView.tsx` | ✅ Done (`a242878`) |
| A4 | TASK-525 | Smart HubPage replacing ModeSelectPage | new `HubPage.tsx`, update `App.tsx` | 📋 |
| A5 | TASK-526 | Cross-section annotations — utilization color, actual barDia/barCount, ascRequired | `CrossSectionView.tsx` | ✅ Done (`a242878`, `a5612b0`) |
| A6 | TASK-527 | TopBar context badges + fix settings button (SettingsPanel slide-over) | `TopBar.tsx`, new `SettingsPanel.tsx` | 📋 |
| A7 | TASK-528 | Workflow breadcrumb for batch flow (Import → Editor → Batch → Dashboard) | new `WorkflowBreadcrumb.tsx`, 4 page files | 📋 |

> **Design principle:** Editor is the workstation. Manual beam form lives only in `/design`. No redundant forms in batch flow.
> Full UX spec: [react-ux-improvement-plan.md](planning/react-ux-improvement-plan.md)

#### Library Expansion (original v0.21 plan)

| # | Task ID | Feature | Python | FastAPI | React | Tests | Status |
|---|---------|---------|--------|---------|-------|-------|--------|
| 1 | TASK-514 | PDF Export | `report.py` +15 lines | extend export router | extend useExport type | 4 | ✅ Done |
| 2 | TASK-515 | Load Calculator | — (existing) | new `/analysis/loads/simple` | new `useLoadAnalysis` + panel | 7 | ✅ Done |
| 3 | TASK-516 | Triangular + Moment loads | `load_analysis.py` +120 lines | — (extends TASK-515) | — | 6 | 📋 |
| 4 | TASK-517 | Project BOQ | new `boq.py` ~120 lines | new `/insights/project-boq` | new `useProjectBOQ` + panel | 5 | 📋 |
| 5 | TASK-518 | Torsion API + React | `api.py` +60 lines | new `/design/beam/torsion` | new `useTorsionDesign` + toggle | 5 | ✅ Done |
| 6 | TASK-519 | Alternatives Panel (Pareto) | — (existing) | new `/optimization/beam/pareto` | new `useParetoDesign` + panel | 3 | 📋 |
| 7 | TASK-520 | Report/3D Test Coverage | — | — | — | ~15 | 📋 |
| 8 | TASK-521 | Beam Rationalization | new `rationalization.py` ~250 lines | new `/insights/rationalize` | new panel in BuildingEditor | 4 | 📋 |

> Detailed specs (function signatures, Pydantic models, React hooks, UI wireframes) in [next-phase-improvements-plan.md](planning/next-phase-improvements-plan.md) Part 2.

---

## Active

| ID | Task | Agent | Status |
|----|------|-------|--------|
| TASK-525 | Smart HubPage replacing ModeSelectPage | — | 📋 Next |
| TASK-515 | Load Calculator (FastAPI + React) | Copilot | ✅ Done |

## Up Next

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| TASK-525 | Smart HubPage replacing ModeSelectPage | — | 3–4h | 🟡 Medium | 📋 |
| TASK-527 | TopBar context badges + SettingsPanel slide-over | — | 2h | 🟡 Medium | 📋 |
| TASK-528 | Workflow breadcrumb for batch flow | — | 1h | 🟢 Low | 📋 |
| TASK-516 | Triangular + Moment load stubs in load_analysis.py | — | 1d | 🟡 Medium | 📋 |
| TASK-517 | Project BOQ (Python module + FastAPI + React panel) | — | 3–4d | 🔴 High | 📋 |
| TASK-519 | Alternatives Panel — Pareto front in DesignView | — | 3–4d | 🟡 Medium | 📋 |
| TASK-520 | Test coverage: report.py, geometry_3d.py, dashboard.py | — | 2–3d | 🟡 Medium | 📋 |
| TASK-521 | Beam Rationalization (new algo + FastAPI + React) | — | 1–2w | 🟢 Low | 📋 |

## Backlog

| ID | Task | Priority | Notes |
|----|------|----------|-------|
| TASK-513 | React: AI assistant port | 🟡 Medium | Deferred to v0.22 — needs LLM API design |
| — | Wire BuildingEditor Cost tab (placeholder → real data) | 🟢 Low | Use `/optimization/cost-rates` |
| — | 28 unit conversion warnings | 🟢 Low | Informational, not bugs. Self-documenting via `_nmm`/`_knm` var names. |
| — | 287 legacy import warnings (Streamlit) | 🟢 Low | Won't fix — will go away when Streamlit is deprecated |

## Recently Done

| ID | Task | Agent | Status |
|----|------|-------|--------|
| — | Session 107: Safety gates hardening — FORBIDDEN commands in 5 files, CodeQL fix, ops role scoping | Copilot | ✅ Done |
| — | TopBar nav + ModeSelect quick links (v0.20 wrap-up) | Copilot | ✅ Done |
| TASK-518 | Torsion API + React — endpoint + hook + DesignView toggle + 3 API tests | Copilot | ✅ Done |
| TASK-515 | Load Calculator — endpoint + useLoadAnalysis hook + MiniDiagram + 4 tests | Copilot | ✅ Done |
| TASK-514 | PDF Export — export_pdf() + extend export router + PDF button + 4 export tests | Copilot | ✅ Done |
| — | Created WORKLOG.md compact change log + updated agent-bootstrap | Copilot | ✅ Done |
| TASK-522 | BeamDetailPanel + 3D rebar + redesign + edit rebar in BuildingEditorPage | Copilot | ✅ Done (`a242878`, `a5612b0`) |
| TASK-523 | Activate FloatingDock + BentoGrid Dashboard | Copilot | ✅ Done (`a242878`) |
| TASK-524 | DesignView dynamic layout + export dropdown | Copilot | ✅ Done (`a242878`) |
| TASK-526 | Cross-section annotations + utilization color + ascRequired fix | Copilot | ✅ Done (`a242878`, `a5612b0`) |
| — | Bug fix: 3D/2D top bar mismatch + utilization formula + BatchDesignResult.utilization_ratio | Copilot | ✅ Done (`a5612b0`) |
| TASK-505 | React: API integration tests (86 tests, 12 routers, all pass) | Copilot | ✅ Done |
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
