# AI Workspace Expansion - Research & Architecture (V2)

**Type:** Research
**Audience:** Developers
**Status:** Draft
**Importance:** Critical
**Created:** 2026-01-20
**Last Updated:** 2026-01-21
**Related Tasks:** Session 58, 59 - AI Workspace Enhancement

---

## Executive Summary

This document upgrades the AI assistant from a command executor into a structural engineering design editor with a dynamic, modern workspace. Key decisions:

- Keep Streamlit as the shell, but modernize UI with custom components and a design system.
- Introduce a dynamic workspace model (dockable panels, saved layouts, AI-controlled views).
- Expand the library first (P0/P1 functions) so UI and AI tools remain thin wrappers.
- Deliver per-beam editing, one-click optimization, and multi-beam intelligence.
- Tighten exports and visualization to show work clearly in 3D, 2D, and reports.

---

## Table of Contents

1. [Current State (Verified)](#1-current-state-verified)
2. [User Vision and Workflow](#2-user-vision-and-workflow)
3. [Product Architecture (Dynamic Workspace)](#3-product-architecture-dynamic-workspace)
4. [UI Modernization Plan (Streamlit-First)](#4-ui-modernization-plan-streamlit-first)
5. [Technology Stack Assessment](#5-technology-stack-assessment)
6. [Library Expansion Plan (Critical Path)](#6-library-expansion-plan-critical-path)
7. [Multi-Beam Intelligence](#7-multi-beam-intelligence)
8. [Optimization Workspace](#8-optimization-workspace)
9. [Visualization and Export](#9-visualization-and-export)
10. [Tooling and AI Architecture](#10-tooling-and-ai-architecture)
11. [Implementation Roadmap](#11-implementation-roadmap)
12. [Risks and Mitigations](#12-risks-and-mitigations)
13. [Next Steps](#13-next-steps)

---

## 1. Current State (Verified)

### 1.1 Structural Library (structural_lib)

- 50+ API functions for IS 456:2000 beam design (flexure, shear, torsion, detailing).
- Optimization and analysis functions (optimize_beam_cost, smart_analyze_design).
- Adapters for ETABS, SAFE, STAAD, Generic CSV.
- BBS and DXF export support.

### 1.2 Streamlit Workspace (confirmed in codebase)

Existing components and files:

- `streamlit_app/components/visualizations.py` (cross-section, BMD/SFD, charts)
- `streamlit_app/components/visualizations_3d.py` (3D building and beam views)
- `streamlit_app/components/beam_viewer_3d.py` + `streamlit_app/static/beam_viewer_3d.html`
- `streamlit_app/components/ai_workspace.py`

Current capabilities:

- Multi-format import (ETABS, SAFE, STAAD, CSV)
- Batch beam design with progress tracking
- 3D building visualization with rebar
- Cross-sections and BMD/SFD diagrams
- AI chat with function calling (10 tools today)

### 1.3 Gaps to Close

| Gap | User Impact | Required Change |
| --- | --- | --- |
| No beam property editor | Cannot change bars, spacing, layers | Add beam editor with live preview |
| No one-click optimize per beam | Manual optimization is slow | Add Optimize button in editor |
| Limited multi-beam awareness | Beam lines not coordinated | Add beam line analysis + standardization |
| AI cannot call library broadly | AI describes but does not compute | Add whitelisted generic API caller |
| Limited history/undo | No comparison or rollback | Add state snapshots and diff |
| UI looks moderate | Product feels less advanced | Modernize UI and visual system |
| No dynamic workspace | Layout is static and constrained | Add dockable, resizable panels |

---

## 2. User Vision and Workflow

### 2.1 Vision

- "A flexible workspace where AI can work and show the work."
- "An editor for structural engineers, not just a report generator."
- "Optimize the beam in editor with one click."
- "Consider connected beams for Ld, laps, and constructability."

### 2.2 Target Workflow

1. Import ETABS/SAFE forces for a building.
2. AI designs all beams in batch.
3. Review with 3D and heatmaps; pick critical beams.
4. Open editor; adjust rebar and stirrup spacing.
5. Live preview updates in 3D and 2D.
6. Run one-click optimization for that beam.
7. Select beam line; optimize together with continuity rules.
8. Export JSON, BBS, DXF, PNG.

---

## 3. Product Architecture (Dynamic Workspace)

### 3.1 Workspace Layout (proposed)

```
+---------------------------------------------------------------+
| AI WORKSPACE SHELL                                             |
+-----------------------------+---------------------------------+
| CHAT (left, 30-35%)         | DYNAMIC WORKSPACE (right, 65%)  |
| - Prompts + history         | - Dockable panels              |
| - Command palette           | - 3D/2D views, editor, tables   |
| - Suggestions               | - Reports and exports           |
+-----------------------------+---------------------------------+
```

### 3.2 Dynamic Workspace Model (new)

Panel types:
- 3D View, 2D Section, BMD/SFD, Beam Editor, Optimization Table
- Beam Line Analyzer, Report Preview, Export Queue, Activity Log

Workspace actions:
- open/close panel
- dock/undock
- resize/move
- save layout
- restore layout

Minimal state shape:

```python
st.session_state.workspace = {
    "layout_id": "default",
    "panels": [
        {"id": "chat", "type": "chat", "dock": "left"},
        {"id": "viewer_3d", "type": "3d_view", "dock": "right"},
        {"id": "editor", "type": "beam_editor", "dock": "right", "active": False},
    ],
    "active_beam_id": None,
    "history": [],
}
```

### 3.3 AI Action Layer

AI tools should map to workspace actions:

- open_beam_editor -> open editor panel + focus beam
- modify_beam_reinforcement -> update state + refresh 3D/2D
- show_optimization_workspace -> open table panel
- analyze_beam_line -> open line analysis panel

---

## 4. UI Modernization Plan (Streamlit-First)

Goal: Make the Streamlit UI feel modern and advanced without leaving the Python stack.

### 4.1 Visual System

- Define design tokens (colors, spacing, typography, shadows).
- Use custom font via CSS injection for a distinctive brand look.
- Consistent card and panel styling (headers, status chips, metrics).
- Add a status bar and activity log for AI actions.

### 4.2 Dynamic Workspace in Streamlit

Recommended approach:

- Keep Streamlit for routing, data, and LLM.
- Build a custom React component for the workspace panel grid.
- Use a dockable layout library (GoldenLayout or React Grid Layout).
- Embed existing Three.js viewer inside the panel shell.

If short-term only:

- Use `streamlit-elements` for a dockable grid.
- Use `streamlit-aggrid` for professional tables.
- Use `kaleido` for PNG/SVG export of Plotly figures.

### 4.3 Interaction Polish

- Command palette for quick actions (open beam, run optimize, export).
- Real-time progress indicators for batch operations.
- "Suggestion cards" with Apply / Modify / Reject.
- Saved layouts per user (e.g., "Review", "Detailing", "Optimization").

This is the fastest way to reach a modern UI while staying on Streamlit.

---

## 5. Technology Stack Assessment

| Layer | Current Tool | Decision | Action |
| --- | --- | --- | --- |
| UI Framework | Streamlit | Keep | Add custom components + theme |
| 3D Visualization | Three.js | Keep | Embed in dynamic panels |
| Charts/Plots | Plotly | Keep | Add kaleido for export |
| Data Tables | Streamlit/Pandas | Enhance | Add streamlit-aggrid |
| PDF | ReportLab | Keep | No change |
| DXF | ezdxf | Keep | No change |
| AI Chat | OpenAI API | Keep | Expand tool access |

Optional future:
- xeokit for IFC/BIM viewing (if IFC import is needed)
- pyvista for CAD-quality views

---

## 6. Library Expansion Plan (Critical Path)

Principle: The AI should be an interface layer. Every UI feature should map to a library function.

### P0 - Editor Support

- modify_beam_reinforcement
- validate_beam_design
- compare_beam_designs
- compute_beam_cost

### P1 - Multi-Beam Intelligence

- detect_beam_lines
- analyze_beam_line
- optimize_beam_line
- compute_development_length
- compute_lap_length

### P2 - Constructability

- score_constructability
- suggest_standardization
- check_bar_congestion
- compute_bar_cut_lengths

### P3 - Visualization Support

- generate_cross_section_data
- generate_bmd_sfd_data
- export_to_png
- generate_beam_3d_mesh

### Generic API Caller (AI Tool)

- call_structural_lib(function_name, arguments)
- whitelist allowed functions
- auto-inject units where needed

---

## 7. Multi-Beam Intelligence

Core rules for beam line detection:

- Same floor
- Collinear centerlines (within tolerance)
- Shared endpoints (columns)

Outputs per line:

- Standardization recommendation (bar sizes, stirrup pattern)
- Development and lap lengths
- Constructability score with notes
- Optimized designs for each span

---

## 8. Optimization Workspace

Features:

- Interactive table with select/apply actions
- Before/after comparison (cost, steel, utilization)
- Batch optimization by floor, building, line, or selection
- History of applied changes

This workspace is the primary "savings dashboard" for engineers.

---

## 9. Visualization and Export

Visualization types:

- 3D beam and full building
- 2D cross-sections
- BMD/SFD diagrams
- Utilization heatmaps
- Optimization charts

Exports:

- PNG/SVG/PDF (Plotly + kaleido)
- DXF (detailing)
- JSON (design + optimization state)

---

## 10. Tooling and AI Architecture

Proposed tool categories:

- Design: design_beam, design_all_beams, open_beam_editor, modify_beam_reinforcement
- Optimization: optimize_beam, optimize_beam_line, show_optimization_workspace, apply_optimization
- Visualization: show_visualization, generate_visualization, export_visualization, filter_3d_view
- Analysis: get_critical_beams, analyze_beam_line, compare_designs
- Library: call_structural_lib
- State: save_design_state, undo_last_change, export_results

Multi-agent architecture is optional (v3). The current single-agent + tools pattern is sufficient.

---

## 11. Implementation Roadmap

Phase 1 (Week 1): Library P0
- Implement P0 functions + unit tests.
- Add whitelist and generic API tool.

Phase 2 (Week 2): UI modernization spike
- Add design tokens and CSS theme.
- Add dynamic workspace shell (dockable panel prototype).
- Integrate streamlit-aggrid and kaleido.

Phase 3 (Week 3): Beam editor + per-beam optimization
- Build beam_editor component with live preview.
- Wire modify_beam_reinforcement and optimize_beam.

Phase 4 (Week 4): Multi-beam + optimization workspace
- Detect beam lines, optimize lines, add constructability.
- Build optimization workspace table + apply flow.

Phase 5 (Week 5): Polish and documentation
- Performance tuning, export reliability, examples.

---

## 12. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| AI suggests invalid design | Medium | High | Always re-check IS 456 after edits |
| Dynamic UI causes complexity | Medium | Medium | Progressive disclosure, saved layouts |
| Multi-beam optimization slow | Medium | Medium | Caching and async progress |
| Layout state grows too large | Low | Medium | Limit history, compress snapshots |
| Export failures | Medium | Medium | Background jobs + clear errors |

---

## 13. Next Steps

1. Implement P0 library functions with tests.
2. Build a dynamic workspace prototype (dockable panels).
3. Add streamlit-aggrid and kaleido.
4. Integrate a beam editor with live preview.
5. Add multi-beam detection + constructability scoring.

---

## Sources (existing research)

- Three.js vs WebGPU for Construction 3D Viewers
- xeokit BIM Viewer SDK
- Streamlit vs Gradio in 2025
- Claude Artifacts Overview
- AG Grid AI Toolkit
- CrewAI Multi-Agent Framework
- Orq.ai Collaboration Platform
