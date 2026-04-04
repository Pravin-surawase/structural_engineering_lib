# Task Board

> **Single source of truth for active work.** Keep it short and current.

**Updated:** 2026-04-02 — TASKS.md cleanup: merged duplicate sections, archived 28 old items, collapsed done phases

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
| **v0.20** | V3 Foundation | ✅ Released (v0.20.0) | Batch design React UI, compliance checker, cost optimizer, 86 API tests |
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
| A1 | TASK-522 | BeamDetailPanel in BuildingEditorPage — beam click → split 3D rebar + results + redesign + edit rebar | `BeamDetailPanel.tsx`, `BuildingEditorPage.tsx`, `Viewport3D.tsx` | ✅ Done (`a242878`, `a5612b0`) |
| A2 | TASK-523 | Activate FloatingDock (already built) + BentoGrid Dashboard (already built) | `App.tsx`, `DashboardPage.tsx` | ✅ Done (`a242878`) |
| A3 | TASK-524 | DesignView dynamic layout — 3D expands when no result, export dropdown | `DesignView.tsx` | ✅ Done (`a242878`) |
| A4 | TASK-525 | Smart HubPage replacing ModeSelectPage | new `HubPage.tsx`, update `App.tsx` | ✅ Done |
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
| 4 | TASK-517 | Project BOQ | new `boq.py` ~120 lines | new `/insights/project-boq` | new `useProjectBOQ` + panel | 5 | ✅ Done |
| 5 | TASK-518 | Torsion API + React | `api.py` +60 lines | new `/design/beam/torsion` | new `useTorsionDesign` + toggle | 5 | ✅ Done |
| 6 | TASK-519 | Alternatives Panel (Pareto) | — (existing) | new `/optimization/beam/pareto` | new `useParetoDesign` + panel | 3 | 📋 |
| 7 | TASK-520 | Report/3D Test Coverage | — | — | — | ~15 | 📋 |
| 8 | TASK-521 | Beam Rationalization | new `rationalization.py` ~250 lines | new `/insights/rationalize` | new panel in BuildingEditor | 4 | 📋 |

> Detailed specs (function signatures, Pydantic models, React hooks, UI wireframes) in [next-phase-improvements-plan.md](planning/next-phase-improvements-plan.md) Part 2.

---

## Active

| ID | Task | Agent | Status |
|----|------|-------|--------|
| TASK-800 | Agent evolver infrastructure (P3-P11 done, P12 burn-in) | Copilot | Monitoring (burn-in) |

## Recently Done

| ID | Task | Agent | Status |
|----|------|-------|--------|
| TASK-690 | Column P-M interaction math fixes (SP:16 Table I continuity, Cl 38.1 modified strain, xu_bal inelastic strain, Pu_0 cap) | Copilot | ✅ Done |
| TASK-691 | Column biaxial e_min enforcement (Cl 25.4 both axes before Bresler) | Copilot | ✅ Done |
| TASK-692 | Column router exception sanitization (OWASP CWE-209) | Copilot | ✅ Done |
| TASK-900 | Git workflow hardening — all phases complete (13/14 tasks) | Copilot | ✅ Done |
| TASK-671 | Fix 4 known limitations (effective depth, serviceability, multi-layer rebar, failure story) | Copilot | ✅ Done |
| TASK-670 | Fix calculation_report.py shear field bug (4 non-existent ShearResult fields, masked by MagicMock) | Copilot | ✅ Done |
| TASK-660 | Standardize variable naming to IS 456 industry convention (21 fields, 4 dataclasses) | Copilot | ✅ Done |
| TASK-650/651/652/653 | Phase 3 Footing: types, bearing/flexure, one-way shear, punching shear (61 tests) | Copilot | ✅ Done |
| TASK-712 | Enhanced shear near supports (Cl 40.3) — shear.py + 14 tests + API endpoint (PR #468) | Copilot | ✅ Done |
| TASK-709 | Move ductile.py → codes/is13920/beam.py + shim (PR #467) | Copilot | ✅ Done |
| TASK-710 | Fix upward import in detailing.py (PR #467) | Copilot | ✅ Done |
| TASK-642 | Five-point steel stress-strain curve (IS 456 Fig 23) — 26 tests | Copilot | ✅ Done |
| TASK-800.P2-P11 | Agent evolver: 10 scripts + agent-evolver.agent.md + skill + run.sh | Copilot | ✅ Done |

## Up Next

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| TASK-527 | TopBar context badges + SettingsPanel slide-over | — | 2h | 🟡 Medium | 📋 |
| TASK-528 | Workflow breadcrumb for batch flow | — | 1h | 🟢 Low | 📋 |
| TASK-516 | Triangular + Moment load stubs in load_analysis.py | — | 1d | 🟡 Medium | 📋 |
| TASK-519 | Alternatives Panel — Pareto front in DesignView | — | 3–4d | 🟡 Medium | 📋 |
| TASK-520 | Test coverage: report.py, geometry_3d.py, dashboard.py | — | 2–3d | 🟡 Medium | 📋 |
| TASK-521 | Beam Rationalization (new algo + FastAPI + React) | — | 1–2w | 🟢 Low | 📋 |
| TASK-643 | Verify SP:16 Table I normalization convention against physical publication | — | 0.5d | 🟡 Medium | 📋 |
| TASK-681 | Migrate python-jose → PyJWT in auth.py | — | 0.5d | 🟡 Medium | ✅ Done |

## Library Expansion — Multi-Code, Multi-Element

> **v5.0:** Multi-code (IS 456 + ACI 318 + EC2), multi-element expansion. Every function goes through a 9-step quality pipeline.
> See [library-expansion-blueprint-v5.md](planning/library-expansion-blueprint-v5.md) for full plan.
> Use `/function-quality-pipeline` skill for every new function.

### Phase 0: Quality Infrastructure ✅ Done (11/11)

> TASK-600–610 complete. Function quality pipeline, agent updates, blueprint v4.0. See [tasks-history.md](_archive/tasks-history.md).

### Phase 1: Foundation Cleanup ✅ Done (15/15)

> TASK-611–625 complete. core/numerics.py, is456/common/, @deprecated decorator, clauses.json, plausibility guards, check scripts. See [tasks-history.md](_archive/tasks-history.md).

### Phase 1.5: IS 456 Beam Restructure ✅ Done (13/13)

> TASK-700–712 complete. Beam modules → `codes/is456/beam/`, ductile → `codes/is13920/`, backward-compat shims, enhanced shear (Cl 40.3). PRs #466, #467, #468. See [tasks-history.md](_archive/tasks-history.md).

### Phase 2: Column Design ✅ Done (14/14)

| ID | Task | Function | IS 456 Clause | Priority | Status |
|----|------|----------|---------------|----------|--------|
| TASK-630 | Column types (ColumnClassification, ColumnAxialResult, E_COLUMN errors) | Types | — | 🔴 P0 | ✅ Done |
| TASK-631 | classify_column + min_eccentricity | `classify_column`, `min_eccentricity` | Cl 25.1.2, 25.4 | 🔴 P0 | ✅ Done |
| TASK-632 | Short column axial | `short_axial_capacity` | Cl 39.3 | 🔴 P0 | ✅ Done |
| TASK-633 | Short column uniaxial | `design_short_column_uniaxial` | Cl 39.5 | 🔴 High | ✅ Done |
| TASK-634 | P-M interaction curve | `pm_interaction_curve` | Cl 39.5, Annex G | 🔴 High | ✅ Done |
| TASK-635 | Biaxial bending check | `biaxial_bending_check` | Cl 39.6 | 🔴 High | ✅ Done |
| TASK-636 | Effective length | `calculate_effective_length` | Cl 25.2 | 🟡 Medium | ✅ Done (PR #481) |
| TASK-637 | Additional moment | `calculate_additional_moment` | Cl 39.7.1 | 🟡 Medium | ✅ Done |
| TASK-638 | Long column design | `design_long_column` | Cl 39.7 | 🟡 Medium | ✅ Done — long_column.py (395 lines), braced/unbraced, k-factor, additional moments, 23 tests |
| TASK-639 | Helical reinforcement | `check_helical_reinforcement` | Cl 39.4 | 🟢 Low | ✅ Done — helical.py (236 lines), volume ratio, pitch limits, 1.05 enhancement, 14 tests |
| TASK-640 | Column orchestrator | `design_column_is456` | All | 🟡 Medium | ✅ Done — services/api.py (~300 lines), routes short→axial/uniaxial/biaxial, slender→long_column |
| TASK-641 | Column FastAPI endpoint | `POST /api/v1/design/column` | — | 🟡 Medium | ✅ Done — 3 endpoints (long-column, helical-check, design/column), 6 Pydantic models |

| TASK-645 | Column detailing | `column_detailing` | Cl 26.5.3 | 🟡 Medium | ✅ Done — detailing.py (617 lines, 8 functions), ColumnDetailingResult, 5 error codes, API + FastAPI endpoint, 47 tests |
| TASK-646 | Column ductile detailing | `column_ductile_detailing` | IS 13920 Cl 7 | 🟡 Medium | ✅ Done — codes/is13920/column.py (280 lines, 8 functions), DuctileColumnResult, 5 error codes, API + FastAPI endpoint, 18 tests |

> Phase 2 progress: **14/14 tasks done — Phase 2 Column COMPLETE.** Full IS 456 column design: axial, uniaxial, biaxial, P-M curves, effective length, slender columns, helical reinforcement, detailing (Cl 26.5.3), ductile detailing (IS 13920 Cl 7), orchestrator + FastAPI.

### Phase 3: Footing Design (After Phase 2)

| ID | Task | Function | IS 456 Clause | Status |
|----|------|----------|---------------|--------|
| TASK-650 | Footing types + errors (FootingType enum, 4 result dataclasses, 8 error codes) | Types | — | ✅ Done |
| TASK-651 | Isolated footing design (bearing sizing + flexure) | `size_footing`, `footing_flexure` | Cl 34.1, 34.2.3.1 | ✅ Done |
| TASK-652 | Punching shear check | `footing_punching_shear` | Cl 31.6.1 | ✅ Done |
| TASK-653 | One-way shear check | `footing_one_way_shear` | Cl 34.2.4.1(a) | ✅ Done |
| TASK-654 | Bearing pressure | `calculate_bearing_pressure` | Cl 34.4 | 📋 |
| TASK-655 | Dowel bars | `check_dowel_bars` | Cl 34.2.5 | 📋 |
| TASK-656 | Footing FastAPI endpoint | `POST /api/v1/design/footing` | — | 📋 |

> Phase 3 in progress: 4/7 tasks done. Footing types, bearing sizing (Cl 34.1), flexure (Cl 34.2.3.1), one-way shear (Cl 34.2.4.1(a)), punching shear (Cl 31.6.1). 6 new modules in `codes/is456/footing/`. 79 tests, 0 failures. Fixes applied: both-direction flexure + shear design, Cl 34.3.1 steel distribution for rectangular footings, 150mm minimum depth enforcement. Remaining: TASK-654 (bearing at column-footing interface), TASK-655 (dowel bars), TASK-656 (FastAPI endpoint).

### Variable Naming Migration (TASK-660)

| ID | Task | Scope | Priority | Status |
|----|------|-------|----------|--------|
| TASK-660 | Standardize variable naming to IS 456 industry convention | FlexureResult, ShearResult, TorsionResult, LoadCase, ComplianceCaseResult | 🟡 Medium | ✅ Done |

> TASK-660 complete. 21 field renames across 4 dataclasses. @property backward-compat aliases added (deprecation warnings, removal in v1.0.0). ~60 files updated. JSON API backward compatible. 4165 Python + 180 FastAPI tests pass.

### Phase 4-6: Slab, Staircase, Shear Wall (Future)

See [library-expansion-blueprint-v5.md](planning/library-expansion-blueprint-v5.md) for full multi-code, multi-element plan.

### Agent Evolver Infrastructure (TASK-800)

> Self-evolving agent system. P3–P11 + tests complete. See [tasks-history.md](_archive/tasks-history.md).

| ID | Task | Phase | Status |
|----|------|-------|--------|
| TASK-800.P12 | Burn-in validation (15-20 sessions) | P12 | 👀 Monitoring |

### Agent Infrastructure (claw-code adaptation) ✅ Done (23/23)

> TASK-850–872 complete. Agent registry, tool registry, prompt router, permission enforcement, hooks, parity dashboard, skill tiers. See [tasks-history.md](_archive/tasks-history.md).

### Git Workflow Hardening (TASK-900)

> **Hardening the git automation infrastructure** based on 9-script audit and TASK-640 root-cause analysis.
> Full plan: [git-workflow-hardening-plan.md](_active/git-workflow-hardening-plan.md)
> WIP limit: 2 active at once.

| ID | Task | Phase | Priority | Status |
|----|------|-------|----------|--------|
| TASK-900 | Fix safe_push.sh Step 6 divergence detection | Phase 1 | 🔴 Critical | ✅ Done |
| TASK-901 | Block --amend on main/develop/release branches | Phase 1 | 🔴 Critical | ✅ Done |
| TASK-902 | Route --push through safe_push.sh | Phase 1 | 🔴 Critical | ✅ Done |
| TASK-903 | Wire or delete validate_git_state.sh | Phase 1 | 🟡 Medium | ✅ Done |
| TASK-904 | Persist --finish state (.git/FINISH_STATE) | Phase 2 | 🔴 High | ✅ Done |
| TASK-905 | Squash-merge divergence detection | Phase 2 | 🔴 High | ✅ Done (merged into TASK-900/906) |
| TASK-906 | Actionable push error messages | Phase 2 | 🔴 High | ✅ Done |
| TASK-907 | Log all bypass events | Phase 3 | 🟡 Medium | ✅ Done |
| TASK-908 | bats-core tests for failure paths | Phase 3 | 🟡 Medium | 📋 (deferred — requires bats-core install) |
| TASK-909 | Consolidate finish_task_pr.sh duplicates | Phase 3 | 🟡 Medium | ✅ Done |
| TASK-910 | Script line budget in check_all.py | Phase 3 | 🟢 Low | ✅ Done |
| TASK-911 | Task ID validation in create_task_pr.sh | Phase 4 | 🟢 Low | ✅ Done |
| TASK-912 | Log rotation for git_workflow.log | Phase 4 | 🟢 Low | ✅ Done |
| TASK-913 | Agent instruction updates (FORBIDDEN commands) | Phase 4 | 🟢 Low | ✅ Done |

## Backlog

| ID | Task | Priority | Notes |
|----|------|----------|-------|
| TASK-513 | React: AI assistant port | 🟡 Medium | Deferred to v0.22 — needs LLM API design |
| — | Wire BuildingEditor Cost tab (placeholder → real data) | 🟢 Low | Use `/optimization/cost-rates` |
| — | 28 unit conversion warnings | 🟢 Low | Informational, not bugs. Self-documenting via `_nmm`/`_knm` var names. |
| — | 287 legacy import warnings (Streamlit) | 🟢 Low | Won't fix — will go away when Streamlit is deprecated |

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
