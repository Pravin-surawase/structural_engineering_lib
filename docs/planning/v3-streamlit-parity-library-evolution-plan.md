# V3 Streamlit Parity + Library Evolution Plan

**Type:** Plan
**Audience:** All Agents
**Status:** In Progress
**Importance:** High
**Created:** 2026-01-26
**Last Updated:** 2026-01-27
**Related Tasks:** TASK-V3-FOUNDATION, TASK-V3-REACT
**Abstract:** Compact, forward-looking plan to evolve the library + API so React can reach Streamlit parity and exceed it with a premium 3D editing workflow.

---

## Executive Summary

We already have a strong library core (design, adapters, smart analysis, 3D single-beam geometry). The remaining gaps now sit at the **API + React integration layer**: building-level geometry endpoint, cross-section geometry helper, rebar validation/apply endpoints, and live code‑check insights. This plan narrows to future work, organized into three phases, and aligns with **# V3 React Migration Roadmap (7-Week Plan)** so the React app can ship a premium, engineer-first UI without duplication.

---

## Verification Snapshot (Jan 27, 2026)

## Verification Complete

### ✅ All Claims Verified (with one path correction)

| Component | Claimed Path/Line | Actual | Status |
|-----------|-------------------|--------|--------|
| **adapters.py** | ETABSAdapter line 123 | line 123 | ✅ |
| | SAFEAdapter line 699 | line 699 | ✅ |
| | STAADAdapter line 1055 | line 1055 | ✅ |
| | GenericCSVAdapter line 1492 | line 1492 | ✅ |
| **models.py** | Point3D line 91 | line 91 | ✅ |
| | SectionProperties line 114 | line 114 | ✅ |
| | BeamGeometry line 150 | line 150 | ✅ |
| | BeamForces line 210 | line 210 | ✅ |
| | DesignDefaults line 299 | line 299 | ✅ |
| | get_merged_data line 355 | line 355 | ✅ |
| **api.py** | design_beam_is456 line 1118 | line 1118 | ✅ |
| | check_beam_is456 line 1203 | line 1203 | ✅ |
| | optimize_beam_cost line 1514 | line 1514 | ✅ |
| | suggest_beam_design_improvements line 1610 | line 1610 | ✅ |
| | smart_analyze_design line 1704 | line 1704 | ✅ |
| | design_from_input line 1830 | line 1830 | ✅ |
| **geometry_3d.py** | compute_rebar_positions line 354 | line 354 | ✅ |
| | compute_stirrup_positions line 527 | line 527 | ✅ |
| | beam_to_3d_geometry line 654 | line 654 | ✅ |
| **streaming.py** | SSE endpoint line 123 | line 123 | ✅ |
| **imports.py** | merge logic line 197+ | line 194-214 | ✅ |
| **ai_workspace.py** | create_building_3d_figure line 1666 | line 1666 | ✅ |

### ⚠️ One Path Correction

**geometry_3d.py** is at:
- ❌ `geometry_3d.py` (claimed path doesn't exist)
- ✅ `Python/structural_lib/visualization/geometry_3d.py` (correct path)

### ✅ Resolved Gaps (Completed Jan 27, 2026)

1. **`building_to_3d_geometry`** — Implemented in `Python/structural_lib/visualization/geometry_3d.py`
2. **`design_beams_iter`** — Implemented in `Python/structural_lib/batch.py` and used by SSE
3. **`validate_rebar_config`** — Implemented in `Python/structural_lib/rebar.py`

### ⏳ Remaining Gaps (Still Open)

1. ✅ **FastAPI** building geometry endpoint (`/api/v1/geometry/building`) + React hook — **Done Jan 27**
2. ✅ **FastAPI** rebar validate/apply endpoints (`/api/v1/rebar/validate`, `/api/v1/rebar/apply`) — **Done Jan 27**
3. ✅ **Library** cross-section geometry helper (`geometry_3d.cross_section_geometry`) — **Done Jan 27**
4. ⏳ **Insights** dashboard + live code checks wrappers — **Still Open**

### ✅ Session Progress (Jan 27, 2026 - Session 2)

**New endpoints added:**
- `POST /api/v1/geometry/building` — Building-level 3D geometry for wireframe
- `POST /api/v1/geometry/cross-section` — 2D cross-section for section cuts
- `POST /api/v1/geometry/rebar/validate` — Rebar config validation
- `POST /api/v1/geometry/rebar/apply` — Rebar apply with geometry preview

**New React hooks:**
- `useBuildingGeometry` / `useBuildingGeometryMutation`
- `useRebarValidation` / `useRebarApply`

**New library function:**
- `cross_section_geometry()` in `geometry_3d.py`

### Verdict

**The previous agent's verification was accurate at the time.** The three gaps above are now resolved; remaining gaps are listed for Phase 2–3 work.

---

## Why This Matters for React (Future Work)

React is fastest when the library provides **canonical data contracts** and **stable geometry outputs**. This plan makes React thinner by:
- Centralizing CSV parsing, validation, and merging in `structural_lib`.
- Exposing deterministic 3D geometry outputs (single beam + building) for R3F.
- Moving rebar checks/constraints out of UI so React can render or warn without duplicating logic.
- Enabling streaming batch design in React via **library-level generators** + FastAPI SSE/WebSocket wrappers.
- Making editor state reversible + debuggable (structured errors, warnings, and audit traces).

Result: React features (live 3D, dynamic rebar, code checks) ship faster, with fewer regressions.

---

## Three-Phase Execution Plan (Library → FastAPI → React)

Each phase is structured so **library work lands first**, then **FastAPI wrappers**, then **React UX**, with tests and automation at every step.

## Progress Update (Jan 27, 2026)

**Phase 1 (Complete)**
- ✅ FastAPI import + batch endpoints already exist (`/api/v1/import/csv`, `/api/v1/import/batch-design`).
- ✅ SSE batch streaming endpoint exists (`/stream/batch-design`).
- ✅ Library dual‑CSV wrapper added: `structural_lib.imports.parse_dual_csv` + validation helpers.
- ✅ Library batch generator + batch helper added: `structural_lib.batch.design_beams_iter` / `design_beams`.
- ✅ FastAPI dual CSV endpoint added (`/api/v1/import/dual-csv`) + React hook (`useDualCSVImport`).

**Phase 2 (Complete)**
- ✅ React building frame visualization exists (3D frame from import data).
- ✅ Full single‑beam geometry endpoint exists (`/api/v1/geometry/beam/full`).
- ✅ Library building geometry added (`building_to_3d_geometry`).
- ✅ Rebar validation/apply helpers added (`validate_rebar_config`, `apply_rebar_config`).
- ✅ FastAPI building geometry endpoint (`/api/v1/geometry/building`).
- ✅ FastAPI rebar endpoints (`/api/v1/geometry/rebar/validate`, `/apply`).
- ✅ FastAPI cross-section endpoint (`/api/v1/geometry/cross-section`).
- ✅ React hooks: `useBuildingGeometry`, `useRebarValidation`, `useRebarApply`.
- ✅ Library cross-section helper (`cross_section_geometry`).

**Phase 3 (Not Started)**
- ⏳ Dashboard wrapper + live code checks + rebar suggestions (library + API + React).

**Commit:** `6ee623f` — feat: add dual-csv import + building geometry + rebar helpers

### Phase 1 — Canonical Inputs + Batch Foundations (Weeks 4–5)

**Status:** ✅ Complete (commit `6ee623f`)

**Goal:** Clean, repeatable import + design flows that React can trust.

**Library Tasks**
1. ✅ `structural_lib.imports.parse_dual_csv(geometry_csv, forces_csv, format="auto", defaults=None)`
2. ✅ `structural_lib.imports.merge_geometry_forces(geometry_list, forces_list, key="beam_id")`
3. ✅ `structural_lib.imports.validate_import(data)` with warnings + row/column context
4. ✅ `structural_lib.batch.design_beams(models, defaults)` (sync batch)
5. ✅ `structural_lib.batch.design_beams_iter(models, defaults)` (streaming generator)

**FastAPI Tasks**
1. ✅ `POST /api/v1/import/dual-csv` → wraps `parse_dual_csv`
2. ✅ `GET /stream/batch-design` → uses `design_beams_iter` generator
3. ⏳ `POST /api/v1/design/batch` → wraps `design_beams` (still needed)

**React Tasks**
1. ✅ Add `useDualCSVImport` hook for geometry + forces
2. ⏳ Update import UI to call dual CSV endpoint (geometry + forces)
3. ⏳ Render import warnings inline; do not block UI on warnings

**Quality + Automation**
- ✅ Unit tests for import/merge edge cases
- ✅ Integration test for dual CSV endpoint
- ⏳ Integration test for SSE stream ordering

---

### Phase 2 — Geometry + Editor Foundations (Weeks 5–6)

**Status:** ✅ Complete (Jan 27, 2026)

**Goal:** Make React's 3D workspace dynamic and trustworthy.

**Library Tasks**
1. ✅ `structural_lib.geometry_3d.building_to_3d_geometry(models, lod="auto")`
2. ✅ `structural_lib.geometry_3d.cross_section_geometry(beam_width, beam_depth, ...)` — **Added Jan 27**
3. ✅ `structural_lib.rebar.validate_rebar_config(beam, config)`
4. ✅ `structural_lib.rebar.apply_rebar_config(beam, config)` (returns updated design + geometry)

**FastAPI Tasks**
1. ✅ `POST /api/v1/geometry/building` (returns line segments for wireframe) — **Added Jan 27**
2. ✅ `POST /api/v1/geometry/cross-section` — **Added Jan 27**
3. ✅ `POST /api/v1/geometry/rebar/validate` + `POST /api/v1/geometry/rebar/apply` — **Added Jan 27**

**React Tasks**
1. ✅ Building frame visualization exists (import-driven)
2. ✅ Building view: `useBuildingGeometry` + `useBuildingGeometryMutation` hooks — **Added Jan 27**
3. ✅ Rebar hooks: `useRebarValidation` + `useRebarApply` — **Added Jan 27**
4. ⏳ Editor mode: live rebar validation + cross-section update (UI integration)
5. ⏳ Dynamic focus: when editing beam row, 3D view filters + zooms to beam
6. ✅ `ConnectionStatus` + `useLiveDesign` already available for live updates

**Quality + Automation**
- Snapshot tests for geometry schema (single + building)
- Visual regression for 3D camera framing + selection highlighting
- Error policy: **never throw** on validation; return structured warnings/errors

---

### Phase 3 — Advanced UX + Code-Driven Feedback (Weeks 6–7)

**Goal:** Engineer-first full-page editor with real-time IS-code pass/fail and optimizer insights.

**Library Tasks**
1. `structural_lib.insights.generate_dashboard(design_result)` (wrapper)
2. `structural_lib.insights.code_checks_live(beam, config)` (fast pass/fail)
3. `structural_lib.optimization.suggest_rebar_options(beam, targets)`
4. Optional: `structural_lib.export.to_bbs/to_dxf` unified wrappers (UI-ready)

**FastAPI Tasks**
1. `POST /api/v1/insights/dashboard`
2. `POST /api/v1/insights/code-checks`
3. `POST /api/v1/optimization/rebar-suggest`

**React Tasks**
1. Full-page editor layout: 3D view on top + grid editor below
2. Live IS-code status (pass/fail + actionable warnings)
3. Optimizer suggestions panel with “Apply” workflow
4. Export buttons for BBS/DXF + audit/cert links

**Quality + Automation**
- SSE/WebSocket latency budget (<150ms)
- Profiling: ensure 1k-beam building view stays interactive
- Add debug “replay” logs for editing steps

---

## React Work Plan (Aligned with V3 React Migration Roadmap)

This section mirrors **# V3 React Migration Roadmap (7-Week Plan)** and explains what React should do and which library functions it should call (or add).

### Phase 4 (Week 5) — Live Design + Streaming
- **Use existing hooks:** `useLiveDesign`, `useBeamGeometry`, `useCSVFileImport`.
- **Add hook:** `useDualCSVImport` → calls new `/import/dual-csv` endpoint.
- **Error policy:** show parse warnings in a non-blocking panel; hard errors block only when no beams are parsed.
- **Debug:** log request IDs + beam IDs; include error trace in dev console.

### Phase 5 (Week 6) — Building 3D + Editor
- **Add hooks:** `useBuildingGeometry`, `useCrossSectionGeometry`, `useRebarValidation`.
- **Use library:** `building_to_3d_geometry`, `cross_section_geometry`, `validate_rebar_config`.
- **UX behavior:** editing a beam row focuses 3D, filters others, updates cross-section and rebar hints.
- **Error policy:** invalid rebar configs show inline warnings and disable “Apply”, but keep editor editable.

### Phase 6 (Week 7) — Intelligent UX + Optimizer
- **Add hooks:** `useDashboardInsights`, `useRebarSuggestions`.
- **Use library:** SmartDesigner + `generate_dashboard`, `suggest_rebar_options`.
- **Debug:** include a “why failed” drawer with code clause references + link to calculation report.
- **Error policy:** missing optimization results degrade gracefully to “manual edit” mode.

### React UI Work Until End (End-State Requirements)
- **Workspace layout:** 3D viewport (top), data grid editor (bottom), inspector (right).
- **Dynamic 3D:** camera zooms to beam under edit, highlights rebar layers.
- **Real-time checks:** pass/fail from code checks update live as user edits.
- **Export:** BBS/DXF + audit certificate on one click.

---

## Shared Error + Debug Policy (All Phases)

- **Structured errors:** `{ success, message, warnings[], errors[] }` everywhere.
- **Non-blocking warnings:** allow UI to proceed unless there are zero valid beams.
- **Traceability:** include `beam_id`, `case_id`, `source_file`, and `row_index` in errors.
- **Debug hooks:** support verbose logging flags and replay logs for editor actions.
- **Fallbacks:** if FastAPI unavailable, UI should show a clear “offline” banner and disable actions.

---

## Implementation Checklist (Start Now)

1. Add Phase 1 library tasks to TASKS.md + split by function.
2. Add FastAPI endpoints for dual CSV + batch streaming generator.
3. Create `useDualCSVImport` hook + UI warnings panel in React.
4. Add schema tests for `parse_dual_csv` and `design_beams_iter`.

---

## Notes

- This plan is intentionally compact and forward-focused.
- Historical details and Streamlit baseline audits have been removed to keep this document actionable.
- Use the **7-week React Migration Roadmap** as the calendar; this plan fills in missing library + API details.
