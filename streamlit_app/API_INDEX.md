# Streamlit App - Function & Component Index

**Type:** Reference
**Audience:** Developers
**Status:** Production Ready
**Importance:** High
**Created:** 2026-01-21
**Last Updated:** 2026-01-24

---

> Quick reference for reusable functions and components in the Streamlit app.
> Use this to avoid duplicate implementations and find existing functionality fast.

---

## Pages Overview

| Page | File | Description |
|------|------|-------------|
| Home | `app.py` | Landing page with feature overview |
| Beam Design | `pages/01_🏗️_beam_design.py` | Single beam design with tabs |
| Cost Optimizer | `pages/02_💰_cost_optimizer.py` | Optimization workflows |
| Compliance | `pages/03_✅_compliance.py` | IS 456 compliance checker |
| Documentation | `pages/04_📚_documentation.py` | Interactive tutorials |
| 3D Viewer Demo | `pages/05_3d_viewer_demo.py` | 3D viewer demo |
| Multi-Format Import | `pages/06_📥_multi_format_import.py` | ETABS/SAFE/CSV batch import |
| Report Generator | `pages/07_📄_report_generator.py` | PDF report generation |
| AI Assistant | `pages/08_⚡_ai_assistant.py` | Chat + dynamic workspace |
| Feedback | `pages/90_feedback.py` | User feedback form |

### Hidden Pages (pages/_hidden/)

Legacy or experimental pages:
- `_06_📐_dxf_export.py`, `_07_📄_report_generator.py`, `_10_🤖_ai_assistant.py`
- `_05_📋_bbs_generator.py`, `_08_📊_batch_design.py`, `_09_🔬_advanced_analysis.py`

---

## Components (`components/`)

### ai_workspace.py
AI Assistant dynamic workspace and data pipeline.

| Function | Purpose |
|----------|---------|
| `init_workspace_state()` | Initialize session state |
| `set_workspace_state()` / `get_workspace_state()` | Workspace transitions |
| `auto_map_columns()` | Auto-map CSV columns |
| `process_with_adapters()` | ETABS/SAFE adapter pipeline |
| `design_all_beams_ws()` | Batch design from workspace |
| `render_dynamic_workspace()` | Main workspace renderer |

### beam_viewer_3d.py
Three.js-based beam viewer (iframe).

| Function | Purpose |
|----------|---------|
| `render_beam_3d()` | Render Beam3DGeometry or dict |
| `render_beam_3d_from_detailing()` | Convenience from detailing result |
| `create_demo_geometry()` | Demo geometry for testing |

### inputs.py
Standardized input widgets.

| Function | Purpose |
|----------|---------|
| `dimension_input()` | Geometry inputs |
| `material_selector()` | Concrete/steel grade selection |
| `load_input()` | Load input widget |
| `exposure_selector()` | Exposure class selection |
| `support_condition_selector()` | Support type selector |

### results.py
Design result display components.

| Function | Purpose |
|----------|---------|
| `display_design_status()` | Pass/fail summary |
| `display_reinforcement_summary()` | Bar summary cards |
| `display_flexure_result()` | Flexure result panel |
| `display_shear_result()` | Shear result panel |
| `display_summary_metrics()` | Key metrics strip |
| `display_utilization_meters()` | Utilization gauges |
| `display_material_properties()` | Material summary |
| `display_compliance_checks()` | Code compliance table |

### visualizations.py
Plotly-based 2D charts.

| Function | Purpose |
|----------|---------|
| `get_plotly_theme()` | Shared Plotly theme |
| `create_beam_diagram()` | Beam elevation + loads |
| `create_cost_comparison()` | Cost comparison chart |
| `create_bmd_sfd_diagram()` | BMD/SFD diagram |
| `create_utilization_gauge()` | Utilization gauge |
| `create_sensitivity_tornado()` | Sensitivity chart |
| `create_compliance_visual()` | Compliance summary |

### visualizations_3d.py
Plotly-based 3D geometry.

| Function | Purpose |
|----------|---------|
| `create_beam_3d_figure()` | Beam 3D view |
| `create_beam_3d_from_geometry()` | From Beam3DGeometry |
| `create_beam_3d_from_dict()` | From geometry dict |
| `create_multi_beam_3d_figure()` | Building-level 3D |
| `compute_geometry_hash()` | Geometry cache key |

### smart_dashboard.py
SmartDesigner visualization helpers.

| Function | Purpose |
|----------|---------|
| `render_score_gauge()` | Score gauge |
| `render_score_breakdown()` | Score components |
| `render_status_badge()` | Status pill |
| `render_issues_list()` | Issues list |
| `render_quick_wins()` | Quick wins list |
| `render_suggestions_table()` | Suggestions table |
| `render_cost_comparison()` | Cost comparison |
| `render_constructability_details()` | Constructability |
| `render_smart_dashboard_full()` | Full dashboard |
| `render_smart_dashboard_compact()` | Compact view |

### report_export.py
Export panel helpers.

| Function | Purpose |
|----------|---------|
| `show_export_options()` | Export UI panel |
| `show_audit_trail_summary()` | Audit summary |
| `show_dxf_export()` | DXF export controls |

### visualization_export.py
PyVista export helpers (optional CAD outputs).

| Function | Purpose |
|----------|---------|
| `check_pyvista_available()` | Optional dependency check |
| `geometry_to_pyvista_meshes()` | Geometry conversion |
| `export_beam_stl()` | Export STL |
| `export_beam_vtk()` | Export VTK |
| `render_beam_screenshot()` | PNG screenshot |
| `show_pyvista_in_streamlit()` | Embedded viewer |

### preview.py
Real-time preview and quick checks.

| Function | Purpose |
|----------|---------|
| `render_real_time_preview()` | Quick preview panel |
| `create_beam_preview_diagram()` | Lightweight preview diagram |
| `calculate_quick_checks()` | Fast check summary |
| `render_status_dashboard()` | Status dashboard |
| `calculate_rough_cost()` | Rough cost |
| `render_cost_summary()` | Cost summary card |

### polish.py
UI polish helpers.

| Function | Purpose |
|----------|---------|
| `show_skeleton_loader()` | Loading skeletons |
| `show_empty_state()` | Empty state callouts |
| `show_toast()` | Toast notifications |
| `show_progress()` | Progress bar |
| `apply_hover_effect()` | Hover CSS |
| `apply_smooth_transitions()` | Transition CSS |

---

## Utilities (`utils/`)

### api_wrapper.py

| Function | Purpose |
|----------|---------|
| `cached_design()` | Cached design wrapper |
| `cached_smart_analysis()` | Cached SmartDesigner |
| `cached_bmd_sfd()` | Cached diagrams |
| `clear_cache()` | Clear local cache |
| `get_library_status()` | Library status check |

### batch_design.py *(Session 63)*

Shared batch design utilities for designing multiple beams.

| Function | Purpose |
|----------|---------|
| `design_single_beam()` | Design one beam, returns standardized dict |
| `design_beam_row()` | Design from DataFrame row |
| `design_all_beams_df()` | Batch design with progress callback |

### caching.py

| Function | Purpose |
|----------|---------|
| `cached_design_beam()` | Cached beam design |
| `cached_plotly_chart()` | Cached figures |
| `cache_stats()` | Cache stats |
| `clear_all_caches()` | Clear all caches |

### data_loader.py

| Function | Purpose |
|----------|---------|
| `load_csv()` | CSV loader |
| `detect_format()` | Detect ETABS/SAFE/Generic |
| `validate_columns()` | Column validation |

### error_handler.py

| Function | Purpose |
|----------|---------|
| `show_error()` | User-facing error |
| `handle_api_error()` | API error recovery |
| `log_error()` | Console logging |

### lod_manager.py

| Function | Purpose |
|----------|---------|
| `LODManager` | Level-of-detail control |
| `get_lod_for_count()` | LOD selector |
| `simplify_geometry()` | Geometry simplifier |

### pdf_generator.py

| Function | Purpose |
|----------|---------|
| `generate_beam_report()` | Single beam PDF |
| `generate_batch_report()` | Batch report PDF |
| `add_is456_references()` | Clause citations |

### rebar_layout.py *(Session 63)*

Shared rebar layout calculations for 3D visualization.

| Function | Purpose |
|----------|---------|
| `calculate_rebar_layout()` | Full layout with dev length, stirrup zones |
| `calculate_rebar_layout_simple()` | Quick layout for previews |

### rebar_optimization.py *(Session 63)*

Shared rebar optimization using library functions.

| Function | Purpose |
|----------|---------|
| `suggest_optimal_rebar()` | Optimal bar config using `select_bar_arrangement()` |
| `optimize_beam_line()` | Unified bar sizes across beam line |

### session_manager.py

| Function | Purpose |
|----------|---------|
| `init_session()` | Session init |
| `get_session_value()` | Safe access |
| `set_session_value()` | Safe update |

### validators.py

| Function | Purpose |
|----------|---------|
| `validate_beam_inputs()` | Beam input validation |
| `validate_material_inputs()` | Materials validation |
| `validate_loading_inputs()` | Loads validation |
| `validate_reinforcement_inputs()` | Rebar validation |

---

## Quick Notes

- Use this index before adding new helpers or components.
- Prefer `utils/` and `components/` reuse over new implementations.
