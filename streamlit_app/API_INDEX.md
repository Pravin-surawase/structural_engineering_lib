# Streamlit App - Function & Component Index

**Type:** Reference
**Audience:** Developers
**Status:** Production Ready
**Importance:** High
**Created:** 2026-01-21
**Last Updated:** 2026-01-21

---

> Quick reference for all reusable functions and components in the Streamlit app.
> Use this to avoid duplicate implementations and find existing functionality.

---

## Pages Overview

| Page | File | Description |
|------|------|-------------|
| Home | `app.py` | Landing page with feature overview |
| Beam Design | `pages/01_🏗️_beam_design.py` | Single beam design with 5 tabs |
| Cost Optimizer | `pages/02_💰_cost_optimizer.py` | Bar arrangement optimization |
| Compliance | `pages/03_✅_compliance.py` | IS 456 compliance checker |
| Documentation | `pages/04_📚_documentation.py` | Interactive tutorials |
| 3D Viewer Demo | `pages/05_3d_viewer_demo.py` | PyVista/Plotly 3D demo |
| Multi-Format Import | `pages/06_📥_multi_format_import.py` | ETABS/SAFE/CSV batch import |
| Report Generator | `pages/07_📄_report_generator.py` | PDF report generation |
| AI Assistant | `pages/08_⚡_ai_assistant.py` | Chat-based design with workspace |
| Feedback | `pages/90_feedback.py` | User feedback form |

---

## Components (`components/`)

### ai_workspace.py
AI Assistant's dynamic workspace panel with state machine.

| Function | Purpose | Usage |
|----------|---------|-------|
| `WorkspaceState` (Enum) | 9 states: WELCOME, IMPORT, DESIGN, VIEW_3D, BUILDING_3D, CROSS_SECTION, REBAR_EDIT, EDIT, DASHBOARD |
| `init_workspace_state()` | Initialize session state for workspace | Call in page setup |
| `set_workspace_state(state)` | Transition to new state | After user action |
| `render_dynamic_workspace()` | Main workspace renderer | In AI page |
| `load_sample_data()` | Load 10-beam sample dataset | On "load sample" command |
| `design_all_beams_ws()` | Design all loaded beams | Returns DataFrame |

### beam_viewer_3d.py
3D beam visualization using Plotly.

| Function | Purpose | Parameters |
|----------|---------|------------|
| `create_beam_3d_plot()` | Create beam mesh with rebar | `width, depth, span, rebar_layout` |
| `create_building_3d_plot()` | Full building visualization | `beams_df, design_results` |
| `create_cross_section_plot()` | 2D cross-section with dimensions | `width, depth, bars, stirrups` |

### inputs.py
Standardized input components.

| Function | Purpose | Returns |
|----------|---------|---------|
| `create_geometry_inputs()` | Beam geometry (b, D, span) | Dict |
| `create_material_inputs()` | Concrete/steel grade | Dict |
| `create_loading_inputs()` | Mu, Vu | Dict |
| `create_cover_inputs()` | Clear cover | Dict |

### results.py
Design result display components.

| Function | Purpose |
|----------|---------|
| `show_design_summary()` | Key metrics in cards |
| `show_design_status()` | Pass/fail with utilization |
| `show_reinforcement_details()` | Bar arrangement table |

### visualizations.py
2D plotting functions.

| Function | Purpose |
|----------|---------|
| `plot_cross_section()` | Matplotlib cross-section |
| `plot_rebar_layout()` | Bar positions diagram |
| `plot_stirrup_layout()` | Stirrup spacing visualization |

### visualizations_3d.py
3D Plotly visualizations.

| Function | Purpose |
|----------|---------|
| `create_beam_mesh()` | Beam solid geometry |
| `create_rebar_mesh()` | Reinforcement bars |
| `create_stirrup_rings()` | Stirrup geometry |

### smart_dashboard.py
AI insights dashboard.

| Function | Purpose |
|----------|---------|
| `render_smart_dashboard()` | Full dashboard with scores |
| `show_design_score()` | Gauge chart (0-100) |
| `show_optimization_tips()` | AI recommendations |

### report_export.py
Export functionality.

| Function | Purpose |
|----------|---------|
| `export_to_pdf()` | Generate PDF report |
| `export_to_csv()` | Export design data |
| `export_to_dxf()` | Generate DXF drawing |

---

## Utilities (`utils/`)

### api_wrapper.py
Cached structural library API calls.

| Function | Purpose | Cache |
|----------|---------|-------|
| `cached_design()` | Design with caching | 5 min TTL |
| `batch_design()` | Multiple beams | Parallel |
| `get_design_result()` | Parse API response | - |

### caching.py
Session and cache management.

| Function | Purpose |
|----------|---------|
| `get_cache_key()` | Generate unique cache key |
| `cache_result()` | Store in session_state |
| `invalidate_cache()` | Clear cached results |

### constants.py
App-wide constants.

| Constant | Value | Usage |
|----------|-------|-------|
| `CONCRETE_GRADES` | ["M20", "M25", "M30"...] | Dropdown options |
| `STEEL_GRADES` | ["Fe415", "Fe500", "Fe550"] | Dropdown options |
| `DEFAULT_COVER` | 40 | mm, clear cover |

### data_loader.py
File import utilities.

| Function | Purpose |
|----------|---------|
| `load_csv()` | Parse CSV with auto-mapping |
| `detect_format()` | ETABS/SAFE/Generic detection |
| `validate_columns()` | Check required columns |

### error_handler.py
Error handling and display.

| Function | Purpose |
|----------|---------|
| `show_error()` | User-friendly error display |
| `handle_api_error()` | API error recovery |
| `log_error()` | Console logging |

### fragments.py
Streamlit fragment utilities.

| Function | Purpose |
|----------|---------|
| `safe_fragment()` | Wrapper for @st.fragment |
| `check_fragment_safe()` | Validate no sidebar calls |

### lod_manager.py
Level-of-detail for 3D performance.

| Function | Purpose |
|----------|---------|
| `LODManager` | Manage detail levels |
| `get_lod_for_count()` | Auto LOD based on beam count |
| `simplify_geometry()` | Reduce polygon count |

### pdf_generator.py
PDF report generation.

| Function | Purpose |
|----------|---------|
| `generate_beam_report()` | Single beam PDF |
| `generate_batch_report()` | Multiple beams PDF |
| `add_is456_references()` | Code clause citations |

### session_manager.py
Session state management.

| Function | Purpose |
|----------|---------|
| `init_session()` | Initialize all state vars |
| `get_session_value()` | Safe session_state access |
| `set_session_value()` | Update with validation |

### validators.py
Input validation.

| Function | Purpose | Returns |
|----------|---------|---------|
| `validate_geometry()` | Check b, D, span | bool, errors |
| `validate_materials()` | Check fck, fy | bool, errors |
| `validate_loading()` | Check Mu, Vu | bool, errors |

---

## AI Module (`ai/`)

### context.py
AI context generation.

| Function | Purpose |
|----------|---------|
| `load_system_prompt()` | Get system prompt |
| `generate_workspace_context()` | Current state for AI |
| `build_messages()` | Construct API messages |

### tools.py
Function calling definitions.

| Function | Purpose |
|----------|---------|
| `get_tools()` | OpenAI function definitions |
| `AVAILABLE_TOOLS` | Tool name list |

### handlers.py
Tool execution.

| Function | Purpose |
|----------|---------|
| `handle_tool_call()` | Execute AI tool |
| `load_sample_data_tool()` | Load sample action |
| `design_beams_tool()` | Design all action |

---

## Quick Patterns

### Adding a New Component

```python
# components/my_component.py
from __future__ import annotations
import streamlit as st

def render_my_component(data: dict) -> None:
    """Render my component.

    Args:
        data: Component data
    """
    st.subheader("My Component")
    # ... implementation
```

### Using Session State Safely

```python
# ✅ Safe access
value = st.session_state.get("key", default_value)

# ❌ Unsafe (may raise AttributeError)
value = st.session_state.key
```

### Fragment API Rules

```python
# ✅ OK - regular widgets
@st.fragment
def my_fragment():
    st.button("Click")
    st.number_input("Value")

# ❌ FORBIDDEN - no sidebar in fragments
@st.fragment
def bad_fragment():
    st.sidebar.button("Click")  # Will crash!
```

---

## See Also

- [docs/reference/api.md](../docs/reference/api.md) - Core library API
- [QUICK_START.md](QUICK_START.md) - User guide
- [tests/](tests/) - Test examples
