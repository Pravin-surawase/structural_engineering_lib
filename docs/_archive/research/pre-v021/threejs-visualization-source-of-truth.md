# Three.js 3D Visualization - Single Source of Truth

**Type:** Research + Plan + Status
**Audience:** Developers, AI Agents
**Status:** Active
**Created:** 2026-01-16
**Last Updated:** 2026-01-16
**Related Tasks:** TASK-3D-01, TASK-3D-02, TASK-3D-03, TASK-3D-04, TASK-3D-05, TASK-3D-06

---

## 1. Purpose and Scope

This document consolidates all Three.js 3D visualization research, decisions,
architecture, and roadmap. It is the single source of truth for Three.js work.
Other documents should link here and avoid duplicating details.

---

## 2. Current State (Repo)

- Phase 0 POC is in PR #373 (branch `task/TASK-3D-01`).
- Core library: `Python/structural_lib/visualization/geometry_3d.py` with data
  classes, compute helpers, and JSON serialization.
- Contract: `docs/reference/3d-json-contract.md` (BeamGeometry3D schema).
- Streamlit POC viewer: `streamlit_app/static/beam_viewer_3d.html` (Three.js r128
  CDN) plus `streamlit_app/components/beam_viewer_3d.py`.
- Demo page: `streamlit_app/pages/05_3d_viewer_demo.py`.
- Tests: 59 tests for geometry and integration (per `docs/TASKS.md`).
- API docs: Section 15 in `docs/reference/api.md`.

---

## 3. Decision Summary

- Primary engine: Three.js with react-three-fiber for production.
- Fallback: Plotly 3D MVP if Streamlit iframe/postMessage is blocked.
- Optional later: PyVista for CAD-quality or server-side rendering tiers.

---

## 4. Architecture Overview

- Data flow: `BeamDetailingResult` -> `Beam3DGeometry` -> JSON -> iframe ->
  Three.js viewer.
- Communication: Python -> JS via embedded JSON or postMessage; JS -> Python via
  viewer events (ready, render complete).
- Boundary rule: no Three.js or UI dependencies inside `structural_lib`.
- Coordinate system: X along span, Y across width, Z height; units in mm.

---

## 5. Data Contract and API Surface

- Canonical contract: `docs/reference/3d-json-contract.md`.
- API reference: `docs/reference/api.md` section 15.
- SDK contract reference: `docs/reference/sdk-api-contract-v1.md`.
- POC uses embedded JSON in HTML to avoid CORS and timing issues.

---

## 6. Research Synthesis (Why Three.js)

- Performance: best for large scenes (instancing, LOD) with 1000+ beams target.
- Quality: PBR materials, lighting, and post-processing for CAD-like visuals.
- Ecosystem: mature, stable, large community; React Three Fiber reduces boilerplate.
- Integration: iframe approach works with Streamlit; fallback path exists.

---

## 7. Roadmap (Phases)

### Phase 0 - Feasibility Gate (in review)

- Prove iframe + postMessage on Streamlit Cloud.
- Lock contract + geometry serialization.
- Micro-bench targets: 100 beams at 60 FPS; 1000 beams at 30 FPS.

### Phase 1 - Foundation (2 weeks)

- Standalone Three.js viewer (React/Vite).
- Basic concrete mesh + lighting.
- Live updates with <100ms latency.

### Phase 2 - Reinforcement Rendering (2 weeks)

- Instanced rebar cylinders and stirrup tubes.
- Materials polish, shadows.

### Phase 3 - Multi-beam + CSV import (2 weeks)

- Multi-beam rendering with LOD.
- Click selection and details panel.

### Phase 4 - Advanced features (1 week)

- Section cuts, AI explain overlays, exports (GLTF, screenshots).

### Phase 5 - Performance + polish (2 weeks)

- Profiling, memory cleanup, stability passes.

---

## 8. Risks and Mitigations

- Iframe/postMessage restrictions: keep Plotly fallback and embedded JSON path.
- Performance with large scenes: instancing, LOD, GPU-friendly materials.
- Memory leaks: explicit dispose of geometries/materials; lifecycle cleanup.
- Build/tooling drift: lock viewer dependencies and add CI build step.

---

## 9. Efficiency and Automation Plan

- Contract validation: pre-commit/CI check for JSON schema and sample payloads.
- Viewer build check: CI job that builds the Three.js viewer bundle.
- Golden fixtures: versioned JSON fixtures for regression tests.
- Integration tests: keep `Beam3DGeometry.to_dict()` in sync with the TS contract.

---

## 10. Open Questions

- Confirm PR #373 merge status and follow-up tasks (TASK-3D-06 automation hook).
- Decide viewer hosting strategy (static HTML vs bundled React app).
- Define upgrade cadence for Three.js versions.

---

## 11. Source References (Historical)

- `docs/research/3d-technology-deep-dive-research.md`
- `docs/research/live-3d-visualization-architecture.md`
- `docs/planning/3d-visualization-strategic-decision.md`
- `docs/research/chat-ui-product-strategy-research.md` (3D section)
- `docs/TASKS.md`
