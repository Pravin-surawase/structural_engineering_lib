# V3 Streamlit Parity + Library Evolution Plan

**Type:** Plan
**Audience:** All Agents
**Status:** In Progress
**Importance:** High
**Created:** 2026-01-26
**Last Updated:** 2026-01-26
**Related Tasks:** TASK-V3-FOUNDATION, TASK-V3-REACT
**Abstract:** Compact, forward-looking plan to evolve the library + API so React can reach Streamlit parity and exceed it with a premium 3D editing workflow.

---

## Executive Summary

We already have a strong library core (design, adapters, smart analysis, 3D single-beam geometry). The remaining gaps block the React workspace: building-level 3D, batch streaming at the library level, rebar editor constraints, and CSV dual-file parsing as a canonical library API. This plan narrows to future work, organized into three phases, and aligns with **# V3 React Migration Roadmap (7-Week Plan)** so the React app can ship a premium, engineer-first UI without duplication.

---

## Verification Snapshot (Jan 26, 2026)

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
- ❌ geometry_3d.py (claimed path doesn't exist)
- ✅ geometry_3d.py (correct path)

### ✅ Confirmed Gaps (Plan is Correct)

1. **`building_to_3d_geometry`** — Does NOT exist in library
   - Only `create_building_3d_figure` in Streamlit's ai_workspace.py (UI-layer, uses Plotly meshes)
   - Library has `beam_to_3d_geometry` (single beam), needs multi-beam/building version

2. **`design_beams_iter`** — async streaming generator doesn't exist in library
   - FastAPI has SSE endpoint, but library lacks native async design iterator

3. **`validate_rebar_config`** — not found as standalone function

### Verdict

**The previous agent's verification is ~95% accurate.** All line numbers and function existence claims are correct. Only correction: geometry_3d.py path should include the `visualization/` subfolder.

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

### Phase 1 — Canonical Inputs + Batch Foundations (Weeks 4–5)

**Goal:** Clean, repeatable import + design flows that React can trust.

**Library Tasks**
1. `structural_lib.imports.parse_dual_csv(geometry_csv, forces_csv, format="auto", defaults=None)`
2. `structural_lib.imports.merge_geometry_forces(geometry_list, forces_list, key="beam_id")`
3. `structural_lib.imports.validate_import(data)` with warnings + row/column context
4. `structural_lib.batch.design_beams(models, defaults)` (sync batch)
5. `structural_lib.batch.design_beams_iter(models, defaults)` (streaming generator)

**FastAPI Tasks**
1. `POST /api/v1/import/dual-csv` → wraps `parse_dual_csv`
2. `POST /api/v1/design/batch` → wraps `design_beams`
3. `GET /stream/batch-design` → switch to `design_beams_iter` generator

**React Tasks**
1. Update import UI to call dual CSV endpoint (geometry + forces)
2. Use `useCSVFileImport` + new `useDualCSVImport` hook
3. Render import warnings inline; do not block UI on warnings

**Quality + Automation**
- Run `scripts/discover_api_signatures.py` before wrapping
- Add unit tests for import/merge edge cases (missing IDs, mixed units)
- Add integration tests for dual CSV endpoint + SSE stream ordering

---

### Phase 2 — Geometry + Editor Foundations (Weeks 5–6)

**Goal:** Make React’s 3D workspace dynamic and trustworthy.

**Library Tasks**
1. `structural_lib.geometry_3d.building_to_3d_geometry(models, lod="auto")`
2. `structural_lib.geometry_3d.cross_section_geometry(beam, rebar_config)`
3. `structural_lib.rebar.validate_rebar_config(beam, config)`
4. `structural_lib.rebar.apply_rebar_config(beam, config)` (returns updated design + geometry)

**FastAPI Tasks**
1. `POST /api/v1/geometry/building` (returns instancing-ready meshes)
2. `POST /api/v1/geometry/cross-section`
3. `POST /api/v1/rebar/validate` + `POST /api/v1/rebar/apply`

**React Tasks**
1. Building view: new `useBuildingGeometry` hook with LOD controls
2. Editor mode: live rebar validation + cross-section update
3. Dynamic focus: when editing beam row, 3D view filters + zooms to beam
4. Add `ConnectionStatus` + `useLiveDesign` for live updates

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
