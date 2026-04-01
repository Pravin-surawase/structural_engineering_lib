# Task Board

> **Single source of truth for active work.** Keep it short and current.

**Updated:** 2026-04-02 (19/23 claw-code adaptation tasks done — agent infrastructure, TASK-637 done — additional moment / slenderness effects, TASK-635 done — biaxial bending check, TASK-636 done — effective length, TASK-642 done — 5-point steel curve)

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
| TASK-800 | Agent evolver infrastructure (P3-P11 done, P12 burn-in) | Copilot | 🔄 In Progress |

## Recently Done

| ID | Task | Agent | Status |
|----|------|-------|--------|
| TASK-637 | Additional moment / slenderness effects (IS 456 Cl 39.7.1) — slenderness.py + AdditionalMomentResult + 24 tests + API + endpoint + 8 API tests | Copilot | ✅ Done |
| TASK-642 | Five-point steel stress-strain curve (IS 456 Fig 23) — stress_blocks.py + uniaxial.py + 26 tests | Copilot | ✅ Done |
| TASK-636 | Effective length per IS 456 Table 28 — axial.py + EndCondition enum + 69 tests + API + endpoint | Copilot | ✅ Done |
| TASK-635 | Biaxial bending check (Cl 39.6) — biaxial.py + ColumnBiaxialResult + 84 tests + API + endpoint | Copilot | ✅ Done |
| TASK-634 | P-M interaction curve (Cl 39.5) — core + API + FastAPI endpoint + 45 tests | Copilot | ✅ Done |
| TASK-633 | Short column uniaxial (Cl 39.5) — uniaxial.py + 57 tests + API + endpoint | Copilot | ✅ Done |
| TASK-630 | Column types (ColumnClassification, ColumnAxialResult, E_COLUMN errors) | Copilot | ✅ Done |
| TASK-631 | classify_column (Cl 25.1.2) + min_eccentricity (Cl 25.4) | Copilot | ✅ Done |
| TASK-632 | short_axial_capacity (Cl 39.3) + API + FastAPI + 75 tests | Copilot | ✅ Done |
| TASK-800.P2-P11 | Agent evolver: 10 scripts + agent-evolver.agent.md + skill + run.sh integration | Copilot | ✅ Done |
| TASK-525 | Smart HubPage replacing ModeSelectPage | Copilot | ✅ Done |
| TASK-515 | Load Calculator (FastAPI + React) | Copilot | ✅ Done |

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

## Library Expansion — Multi-Code, Multi-Element

> **v5.0:** Multi-code (IS 456 + ACI 318 + EC2), multi-element expansion. Every function goes through a 9-step quality pipeline.
> See [library-expansion-blueprint-v5.md](planning/library-expansion-blueprint-v5.md) for full plan.
> Use `/function-quality-pipeline` skill for every new function.

### Phase 0: Quality Infrastructure ✅ Done

| ID | Task | Status |
|----|------|--------|
| TASK-600 | Create function-quality-pipeline skill | ✅ Done |
| TASK-601 | Create function-quality-gate prompt | ✅ Done |
| TASK-602 | Update structural-math agent (12-point checklist, numerical rules) | ✅ Done |
| TASK-603 | Update tester agent (benchmark, degenerate, monotonicity tests) | ✅ Done |
| TASK-604 | Update reviewer agent (two-pass review, IS 456 quality checks) | ✅ Done |
| TASK-605 | Update api-developer agent (endpoint quality, plausibility guards) | ✅ Done |
| TASK-606 | Update structural-engineer agent (math verification protocol) | ✅ Done |
| TASK-607 | Update governance agent (quality metrics tracking) | ✅ Done |
| TASK-608 | Update doc-master agent (element doc checklist) | ✅ Done |
| TASK-609 | Update library-expert agent (quality enforcement rules) | ✅ Done |
| TASK-610 | Create blueprint v4.0 with quality pipeline | ✅ Done |

### Phase 1: Foundation Cleanup (Before Column Work)

| ID | Task | Priority | Status |
|----|------|----------|--------|
| TASK-611 | Create `core/numerics.py` — safe_divide(), approx_equal(), clamp() | 🔴 P0 | ✅ Done |
| TASK-612 | Extract shared math to `codes/is456/common/` (stress_blocks, reinforcement, minimums) | 🔴 P0 | ✅ Done |
| TASK-613 | Hardcode safety factors in `codes/is456/common/constants.py` | 🔴 P0 | ✅ Done |
| TASK-614 | Create `@deprecated` decorator in `core/deprecation.py` | 🔴 High | ✅ Done |
| TASK-615 | Populate clauses.json with ~66 subclauses (Cl 24, 25, 31.6, 32-34, 39) | 🔴 High | ✅ Done |
| TASK-616 | Add IS 13920 references to clauses.json (~15 entries) | 🔴 High | ✅ Done |
| TASK-617 | Create test assertion helpers `tests/helpers/is456_assertions.py` | 🟡 Medium | ✅ Done |
| TASK-618 | Top-level `__init__.py` exports for all public functions | 🟡 Medium | ✅ Done |
| TASK-619 | Unit plausibility guards in `services/api.py` | 🟡 Medium | ✅ Done |
| TASK-620 | Stack trace sanitization (security) in `fastapi_app/main.py` | 🟡 Medium | ✅ Done |
| TASK-621 | Add `recovery` field to `DesignError` in `core/errors.py` | 🟡 Medium | 📋 |
| TASK-622 | Create `check_function_quality.py` script (12-point checklist CI) | 🟡 Medium | 📋 |
| TASK-623 | Create `check_clause_coverage.py` script (clause gap detection) | 🟡 Medium | 📋 |
| TASK-624 | Create `check_new_element_completeness.py` script | 🟡 Medium | 📋 |
| TASK-625 | Create maintenance playbook `docs/governance/maintenance-playbook.md` | 🟢 Low | 📋 |

### Phase 1.5: IS 456 Beam Restructure (v5 Phase 0)

> Move existing beam modules into `codes/is456/beam/` subfolder. See [blueprint v5.0 §4](planning/library-expansion-blueprint-v5.md#4-phase-0--is-456-restructure).

| ID | Task | Priority | Status |
|----|------|----------|--------|
| TASK-700 | Create `codes/is456/beam/` directory + `__init__.py` | 🔴 P0 | ✅ PR #466 |
| TASK-701 | Move `flexure.py` → `beam/flexure.py` | 🔴 P0 | ✅ PR #466 |
| TASK-702 | Move `shear.py` → `beam/shear.py` | 🔴 P0 | ✅ PR #466 |
| TASK-703 | Move `detailing.py` → `beam/detailing.py` | 🔴 P0 | ✅ PR #466 |
| TASK-704 | Move `serviceability.py` → `beam/serviceability.py` | 🔴 P0 | ✅ PR #466 |
| TASK-705 | Move `torsion.py` → `beam/torsion.py` | 🔴 P0 | ✅ PR #466 |
| TASK-706 | Update `compliance.py` imports: `from .beam import flexure, shear, serviceability` | 🔴 P0 | ✅ PR #466 |
| TASK-707 | Update `codes/is456/__init__.py` — re-export beam modules for backward compat | 🔴 P0 | ✅ PR #466 |
| TASK-708 | Generate backward-compat shims at old locations (5 files) | 🔴 P0 | ✅ PR #466 |
| TASK-709 | Move `ductile.py` → `codes/is13920/beam.py` + shim | 🟡 Medium | ✅ Done (`32f49571`, PR #467) |
| TASK-710 | Fix upward import in `detailing.py` line 152 (codes → visualization) | 🔴 P0 | ✅ Done (`32f49571`, PR #467) |
| TASK-711 | Run full test suite — zero failures gate | 🔴 P0 | ✅ PR #466 |
| TASK-712 | Implement enhanced shear near supports (Cl 40.3) — new function + 14 tests + API endpoint | 🔴 HIGH | ✅ Done (PR #468) |

### Phase 2: Column Design (After Phase 1.5)

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
| TASK-638 | Long column design | `design_long_column` | Cl 39.7 | 🟡 Medium | 📋 |
| TASK-639 | Helical reinforcement | `check_helical_reinforcement` | Cl 39.8 | 🟢 Low | 📋 |
| TASK-640 | Column orchestrator | `design_column_is456` | All | 🟡 Medium | 📋 |
| TASK-641 | Column FastAPI endpoint | `POST /api/v1/design/column` | — | 🟡 Medium | 📋 |

### Phase 3: Footing Design (After Phase 2)

| ID | Task | Function | IS 456 Clause | Status |
|----|------|----------|---------------|--------|
| TASK-650 | Footing types + errors | Types | — | 📋 |
| TASK-651 | Isolated footing design | `design_isolated_footing` | Cl 34 | 📋 |
| TASK-652 | Punching shear check | `punching_shear_check` | Cl 31.6 | 📋 |
| TASK-653 | One-way shear check | `one_way_shear_check` | Cl 34.2.4 | 📋 |
| TASK-654 | Bearing pressure | `calculate_bearing_pressure` | Cl 34.4 | 📋 |
| TASK-655 | Dowel bars | `check_dowel_bars` | Cl 34.2.5 | 📋 |
| TASK-656 | Footing FastAPI endpoint | `POST /api/v1/design/footing` | — | 📋 |

### Phase 4-6: Slab, Staircase, Shear Wall (Future)

See [library-expansion-blueprint-v5.md](planning/library-expansion-blueprint-v5.md) for full multi-code, multi-element plan.

### Agent Evolver Infrastructure (TASK-800)

> Self-evolving agent system. See [self-evolving-system.md](architecture/self-evolving-system.md) and [agent-evolver-plan.md.bak](_archive/2026-03/agent-evolver-plan-v1.md).

| ID | Task | Phase | Script | Status |
|----|------|-------|--------|--------|
| TASK-800.P3 | Shared libraries (_lib/agent_registry, scoring, agent_data) | P3 | `scripts/_lib/*.py` | ✅ Done (8808c16b) |
| TASK-800.P4 | Session collector | P4 | `agent_session_collector.py` | ✅ Done (8808c16b) |
| TASK-800.P5 | Agent scorer (11 dimensions) | P5 | `agent_scorer.py` | ✅ Done (d875dcfa) |
| TASK-800.P6 | Drift detector (12 agents × rules) | P6 | `agent_drift_detector.py` | ✅ Done (d875dcfa) |
| TASK-800.P7 | Compliance checker (8 rules) | P7 | `agent_compliance_checker.py` | ✅ Done (d875dcfa) |
| TASK-800.P8 | Trend analysis (Mann-Kendall) | P8 | `agent_trends.py` | ✅ Done (d69c4a4f) |
| TASK-800.P9 | Instruction evolver (SHA-256, security levels) | P9 | `agent_evolve_instructions.py` | ✅ Done (e0702346) |
| TASK-800.P10 | Paper data export (CSV, bootstrap CIs) | P10 | `export_paper_data.py` | ✅ Done (d69c4a4f) |
| TASK-800.P2 | Agent-evolver definition + skill | P2 | `agent-evolver.agent.md`, `SKILL.md` | ✅ Done |
| TASK-800.P11 | run.sh evolve integration | P11 | `run.sh` | ✅ Done |
| TASK-800.P12 | Burn-in validation (15-20 sessions) | P12 | — | 📋 Ongoing |
| TASK-800.T | Evolver unit tests | Tests | — | ✅ Done (c1e0d222) |

### Agent Infrastructure (claw-code adaptation)

| # | Task ID | Feature | Script/File | Status |
|---|---------|---------|-------------|--------|
| 1 | TASK-850 | Agent Registry JSON | `agents/agent_registry.json` | ✅ Done |
| 2 | TASK-851 | Unified Tool Registry | `scripts/tool_registry.py` | ✅ Done |
| 3 | TASK-852 | Prompt Router | `scripts/prompt_router.py` | ✅ Done |
| 4 | TASK-853 | run.sh integration (route, tools, pipeline) | `run.sh` | ✅ Done |
| 5 | TASK-854 | Automation-map groups | `scripts/automation-map.json` | ✅ Done |
| 6 | TASK-855 | SESSION_LOG compaction | `scripts/session.py compact` | ✅ Done |
| 7 | TASK-856 | Session state persistence | `scripts/session_store.py` | ✅ Done |
| 8 | TASK-857 | Pipeline state tracking | `scripts/pipeline_state.py` | ✅ Done |
| 9 | TASK-858 | Fast session start (--fast) | `scripts/session.py start --fast` | ✅ Done |
| 10 | TASK-859 | Cost/token logging | `scripts/session.py costs` | ✅ Done |
| 11 | TASK-860 | Tool permission enforcement | `scripts/tool_permissions.py` | ✅ Done |
| 12 | TASK-862 | Permission audit report | `scripts/audit_permissions.py` | ✅ Done |
| 13 | TASK-863 | Hook framework | `scripts/hooks/` | ✅ Done |
| 14 | TASK-864 | Hook implementations (6 hooks) | `scripts/hooks/pre_commit.py` etc. | ✅ Done |
| 15 | TASK-865 | CLI smoke tests (13 tests) | `scripts/test_cli_smoke.py` | ✅ Done |
| 16 | TASK-866 | Parity dashboard (4 dimensions) | `scripts/parity_dashboard.py` | ✅ Done |
| 17 | TASK-868 | Config precedence validator | `scripts/config_precedence.py` | ✅ Done |
| 18 | TASK-870 | Parallel pipeline stages | `scripts/pipeline_state.py` (updated) | ✅ Done |
| 19 | TASK-872 | Skill tier classification | `scripts/skill_tiers.py` | ✅ Done |
| 20 | TASK-861 | Trust gate initialization | 📋 Session 4 |
| 21 | TASK-867 | Snapshot regression tests | 📋 Session 4 |
| 22 | TASK-869 | Update all 15 agent files | 📋 Session 4 |
| 23 | TASK-871 | Update AGENTS.md/CLAUDE.md | 📋 Session 4 |

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
| — | Release infrastructure overhaul — preflight, semver validation, CI tests, rollback, 37 tests | Copilot | ✅ Done |
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
| TASK-525 | Smart HubPage replacing ModeSelectPage — quick actions + last session context | Copilot | ✅ Done |
| TASK-517 | Project BOQ — services/boq.py + FastAPI endpoint + useProjectBOQ hook + DashboardPage | Copilot | ✅ Done |
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
