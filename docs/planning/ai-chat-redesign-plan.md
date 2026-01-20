# AI Chat Page Redesign Plan

**Type:** Architecture / Planning
**Status:** Draft
**Importance:** Critical
**Created:** 2026-01-20
**Last Updated:** 2026-01-20
**Related Tasks:** TASK-AI-V2

---

## Executive Summary

Complete redesign of the AI Assistant page (10_🤖_ai_assistant.py) to create a professional, modern engineering tool that:
- Uses **100% of screen space** (no wasted header area)
- Has a **single dynamic workspace** (not multiple tabs)
- Provides **auto-mapping** like ETABS import (no manual column mapping)
- Follows **modern AI assistant patterns** (Cursor, ChatGPT, Claude)
- Enables **seamless workflow** from import → design → 3D → edit

---

## Current Problems

### 1. Wasted Space (Top 20%)
```
┌─────────────────────────────────────────────────────┐
│ ❌ Title bar, instructions, excessive padding       │ ← 20% WASTED
├─────────────────────────────────────────────────────┤
│                                                     │
│   Chat (40%)    │    Workspace (60%) with 5 tabs   │
│                 │    📋 Results 🎨 3D 📥 Import     │
│                 │    💰 Cost 📊 Dashboard           │
│                 │                                   │
└─────────────────────────────────────────────────────┘
```

### 2. Tab Overload
- 5 tabs create cognitive load
- User must switch tabs manually
- Content doesn't flow with workflow
- Looks "intern-level" not professional

### 3. Manual Column Mapping
- Current: User must map CSV columns manually
- Problem: ETABS has standard column names - we should auto-detect
- Page 7 already has smart auto-detection

### 4. Disconnected Workflow
- Import → wait → preview → design → switch tab → 3D
- Each step is isolated
- No beam-by-beam editing capability

---

## Proposed Design: Single Dynamic Workspace

### Visual Layout
```
┌──────────────────────────────────────────────────────────────┐
│ ⚡ StructEng AI                                    [Settings]│ ← Minimal header (3%)
├─────────────────────────┬────────────────────────────────────┤
│                         │                                    │
│   💬 CHAT               │   📐 WORKSPACE (Dynamic)           │
│   (35% width)           │   (65% width)                      │
│                         │                                    │
│   ┌─────────────────┐   │   ┌────────────────────────────┐   │
│   │ AI responses    │   │   │                            │   │
│   │ with rich       │   │   │  Changes based on state:   │   │
│   │ cards & actions │   │   │                            │   │
│   │                 │   │   │  1. WELCOME (no data)      │   │
│   │                 │   │   │  2. IMPORT (data loaded)   │   │
│   │                 │   │   │  3. DESIGN (designed)      │   │
│   │                 │   │   │  4. 3D VIEW (visualizing)  │   │
│   │                 │   │   │  5. EDIT (beam selected)   │   │
│   └─────────────────┘   │   │                            │   │
│                         │   └────────────────────────────┘   │
│   ┌─────────────────┐   │                                    │
│   │ [Design] [3D]   │   │   [◀ Prev] [State indicator] [▶]  │
│   │ [Optimize]      │   │                                    │
│   └─────────────────┘   │                                    │
│   ┌─────────────────┐   │                                    │
│   │ Type message... │   │                                    │
│   └─────────────────┘   │                                    │
└─────────────────────────┴────────────────────────────────────┘
```

### Workspace States

| State | Trigger | Content |
|-------|---------|---------|
| **WELCOME** | Initial load | Quick start cards: Sample data, Upload, Manual input |
| **IMPORT** | File uploaded or sample selected | Auto-mapped preview table, beam summary |
| **DESIGN** | "Design all" or chat command | Results table with status, summary stats |
| **3D VIEW** | Click beam or "Show 3D" | 3D model with rebar, stirrups |
| **EDIT** | Click beam row | Single beam editor with live preview |
| **DASHBOARD** | "Show dashboard" | SmartDesigner insights, cost analysis |

---

## Implementation Plan

### Phase 1: Core Architecture (1 day)

#### 1.1 State Machine
```python
from enum import Enum

class WorkspaceState(Enum):
    WELCOME = "welcome"
    IMPORT = "import"
    DESIGN = "design"
    VIEW_3D = "view_3d"
    EDIT = "edit"
    DASHBOARD = "dashboard"

# Session state
if "workspace_state" not in st.session_state:
    st.session_state.workspace_state = WorkspaceState.WELCOME
if "selected_beam" not in st.session_state:
    st.session_state.selected_beam = None
if "beams_df" not in st.session_state:
    st.session_state.beams_df = None
```

#### 1.2 Dynamic Workspace Renderer
```python
def render_workspace():
    """Render workspace based on current state."""
    state = st.session_state.workspace_state

    if state == WorkspaceState.WELCOME:
        render_welcome_panel()
    elif state == WorkspaceState.IMPORT:
        render_import_preview()
    elif state == WorkspaceState.DESIGN:
        render_design_results()
    elif state == WorkspaceState.VIEW_3D:
        render_3d_view()
    elif state == WorkspaceState.EDIT:
        render_beam_editor()
    elif state == WorkspaceState.DASHBOARD:
        render_dashboard()
```

### Phase 2: Welcome Panel (0.5 day)

#### 2.1 Quick Start Cards
```python
def render_welcome_panel():
    st.markdown("### 🚀 Get Started")

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("**📂 Sample Data**")
            st.caption("Try with 10 beams from ETABS export")
            if st.button("Load Sample", key="sample", use_container_width=True):
                load_sample_data()
                st.session_state.workspace_state = WorkspaceState.IMPORT
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("**📤 Upload CSV**")
            st.caption("From ETABS, SAFE, or custom format")
            uploaded = st.file_uploader("", type=["csv"], key="upload")
            if uploaded:
                process_upload(uploaded)
                st.session_state.workspace_state = WorkspaceState.IMPORT
                st.rerun()

    with col3:
        with st.container(border=True):
            st.markdown("**✏️ Manual Input**")
            st.caption("Enter beam parameters directly")
            if st.button("Start Manual", key="manual", use_container_width=True):
                st.session_state.beams_df = create_empty_beam_df()
                st.session_state.workspace_state = WorkspaceState.EDIT
                st.rerun()
```

### Phase 3: Smart Auto-Import (0.5 day)

#### 3.1 Auto-Detection Logic (from Page 7)
```python
# Column name patterns for auto-mapping
COLUMN_PATTERNS = {
    "beam_id": ["unique name", "beam", "element", "name", "id", "label"],
    "b_mm": ["width", "b", "b_mm", "breadth", "b (mm)"],
    "D_mm": ["depth", "d", "D_mm", "D", "height", "h", "d (mm)"],
    "span_mm": ["length", "span", "L", "l_mm", "span_mm"],
    "mu_knm": ["moment", "m3", "mu", "m_max", "bending", "mu_knm"],
    "vu_kn": ["shear", "v2", "vu", "v_max", "vu_kn"],
    "fck": ["fck", "concrete", "fc", "grade"],
    "fy": ["fy", "steel", "rebar"],
}

def auto_map_columns(df: pd.DataFrame) -> dict[str, str]:
    """Auto-detect column mapping from CSV headers."""
    mapping = {}
    df_cols_lower = {c.lower().strip(): c for c in df.columns}

    for target, patterns in COLUMN_PATTERNS.items():
        for pattern in patterns:
            pattern_lower = pattern.lower()
            for col_lower, col_orig in df_cols_lower.items():
                if pattern_lower in col_lower or col_lower in pattern_lower:
                    mapping[target] = col_orig
                    break
            if target in mapping:
                break

    return mapping
```

#### 3.2 Smart Import Flow
```python
def process_upload(file) -> None:
    """Process uploaded file with auto-mapping."""
    df = pd.read_csv(file)

    # Auto-detect format
    format_detected = detect_format(df)

    # Auto-map columns
    mapping = auto_map_columns(df)

    # Apply defaults for missing columns
    defaults = get_defaults()
    standardized_df = standardize_dataframe(df, mapping, defaults)

    # Store in session
    st.session_state.beams_df = standardized_df
    st.session_state.import_mapping = mapping
    st.session_state.import_format = format_detected

    # Auto-transition to IMPORT state (shows preview)
    st.session_state.workspace_state = WorkspaceState.IMPORT
```

### Phase 4: Design Results View (0.5 day)

#### 4.1 Interactive Data Table
```python
def render_design_results():
    """Render design results with interactive table."""
    df = st.session_state.design_results_df

    # Summary stats bar
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Beams", len(df))
    with col2:
        pass_count = (df["status"] == "OK").sum()
        st.metric("Passing", f"{pass_count}/{len(df)}", delta=f"{100*pass_count/len(df):.0f}%")
    with col3:
        st.metric("Avg Utilization", f"{df['utilization'].mean():.1f}%")
    with col4:
        st.metric("Total Steel", f"{df['steel_kg'].sum():.0f} kg")

    # Interactive table with row selection
    st.markdown("**Click a beam to view details or edit:**")

    # Using st.dataframe with selection
    event = st.dataframe(
        df[["beam_id", "b×D", "Mu", "Ast", "status", "utilization"]],
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
    )

    # Handle row selection
    if event.selection.rows:
        selected_idx = event.selection.rows[0]
        st.session_state.selected_beam = df.iloc[selected_idx]["beam_id"]

        # Quick action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🎨 View 3D", use_container_width=True):
                st.session_state.workspace_state = WorkspaceState.VIEW_3D
                st.rerun()
        with col2:
            if st.button("✏️ Edit Beam", use_container_width=True):
                st.session_state.workspace_state = WorkspaceState.EDIT
                st.rerun()
        with col3:
            if st.button("💰 Cost Analysis", use_container_width=True):
                st.session_state.workspace_state = WorkspaceState.DASHBOARD
                st.rerun()
```

### Phase 5: 3D View Integration (0.5 day)

#### 5.1 Seamless 3D with Rebar
```python
def render_3d_view():
    """Render 3D view for selected beam."""
    beam_id = st.session_state.selected_beam

    if not beam_id:
        st.info("Select a beam from the results to view 3D")
        return

    beam_data = get_beam_data(beam_id)
    design_result = get_design_result(beam_id)

    # Calculate rebar layout
    rebar_layout = calculate_rebar_layout(
        ast_mm2=design_result.flexure.ast_required,
        b_mm=beam_data["b_mm"],
        D_mm=beam_data["D_mm"],
        span_mm=beam_data["span_mm"],
    )

    # Header with beam info
    st.markdown(f"### 🎨 {beam_id}")
    st.caption(rebar_layout["summary"])
    st.caption(rebar_layout["detailing_summary"])

    # 3D Figure
    fig = create_beam_3d_figure(
        b=beam_data["b_mm"],
        D=beam_data["D_mm"],
        span=beam_data["span_mm"],
        bottom_bars=rebar_layout["bottom_bars"],
        top_bars=rebar_layout["top_bars"],
        stirrup_positions=rebar_layout["stirrup_positions"],
    )
    st.plotly_chart(fig, use_container_width=True, key=f"3d_{beam_id}")

    # Navigation
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("◀ Back to Results"):
            st.session_state.workspace_state = WorkspaceState.DESIGN
            st.rerun()
    with col2:
        if st.button("✏️ Edit This Beam"):
            st.session_state.workspace_state = WorkspaceState.EDIT
            st.rerun()
    with col3:
        if st.button("▶ Next Beam"):
            select_next_beam()
            st.rerun()
```

### Phase 6: Beam Editor (0.5 day)

#### 6.1 Live Editing with Preview
```python
def render_beam_editor():
    """Edit single beam with live preview."""
    beam_id = st.session_state.selected_beam
    beam_data = get_beam_data(beam_id)

    st.markdown(f"### ✏️ Edit: {beam_id}")

    col1, col2 = st.columns([0.4, 0.6])

    with col1:
        st.markdown("**Geometry**")
        b = st.number_input("Width b (mm)", value=float(beam_data["b_mm"]), step=25.0)
        D = st.number_input("Depth D (mm)", value=float(beam_data["D_mm"]), step=25.0)
        span = st.number_input("Span (mm)", value=float(beam_data["span_mm"]), step=100.0)

        st.markdown("**Loading**")
        mu = st.number_input("Moment Mu (kN·m)", value=float(beam_data["mu_knm"]), step=10.0)
        vu = st.number_input("Shear Vu (kN)", value=float(beam_data["vu_kn"]), step=5.0)

        st.markdown("**Materials**")
        fck = st.selectbox("Concrete Grade", [20, 25, 30, 35, 40], index=1)
        fy = st.selectbox("Steel Grade", [415, 500, 550], index=1)

        # Live redesign on change
        if st.button("💫 Redesign", type="primary", use_container_width=True):
            updated_data = {"b_mm": b, "D_mm": D, "span_mm": span, "mu_knm": mu, "vu_kn": vu, "fck": fck, "fy": fy}
            update_beam_and_redesign(beam_id, updated_data)
            st.rerun()

    with col2:
        # Live 3D preview
        rebar_layout = calculate_rebar_layout(...)
        fig = create_beam_3d_figure(...)
        st.plotly_chart(fig, use_container_width=True)

        # Design summary
        st.markdown("**Current Design**")
        st.info(f"Ast = {design.flexure.ast_required:.0f} mm² → {rebar_layout['summary']}")
```

---

## New Dependencies

### Required
```toml
# Already have these
streamlit>=1.30.0
plotly>=5.18.0
pandas>=2.0.0
openai>=1.0.0
```

### Optional Enhancements
```toml
# For enhanced UI (consider for future)
streamlit-elements==0.1.*   # MUI components, draggable dashboards
streamlit-extras            # Additional components
```

**Recommendation:** Start without new dependencies. Add `streamlit-elements` later if needed for more advanced UI.

---

## Sample Data (Built-in)

Create sample ETABS-like data for testing:

```python
SAMPLE_ETABS_DATA = """Unique Name,Width,Depth,Length,M3,V2
B1-L1,300,500,5000,120.5,45.2
B2-L1,300,500,5000,145.3,52.1
B3-L1,300,600,6000,185.7,68.3
B4-L1,350,600,6000,210.2,75.4
B5-L2,300,500,4500,95.6,38.9
B6-L2,300,500,4500,110.3,42.5
B7-L2,300,550,5500,155.8,55.7
B8-L3,350,650,7000,245.6,88.2
B9-L3,350,650,7000,265.3,95.1
B10-L3,400,700,8000,320.5,112.4
"""

def load_sample_data():
    """Load built-in sample ETABS data."""
    from io import StringIO
    df = pd.read_csv(StringIO(SAMPLE_ETABS_DATA))
    mapping = auto_map_columns(df)
    st.session_state.beams_df = standardize_dataframe(df, mapping, get_defaults())
    st.session_state.workspace_state = WorkspaceState.IMPORT
```

---

## Migration Path

### Step 1: Refactor Current Code (Session 52)
1. Extract current tab content into separate functions
2. Add WorkspaceState enum
3. Add state transition logic
4. Test each state independently

### Step 2: Implement Welcome + Import (Session 53)
1. Create welcome panel with 3 cards
2. Implement auto-mapping from Page 7
3. Add sample data
4. Test ETABS import end-to-end

### Step 3: Implement Design + 3D (Session 54)
1. Interactive results table with selection
2. Seamless 3D view transition
3. Beam navigation (prev/next)
4. Test workflow end-to-end

### Step 4: Implement Edit + Polish (Session 55)
1. Single beam editor with live preview
2. Dashboard integration
3. Chat command routing
4. Final polish and testing

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Screen utilization | 80% | 97% |
| Tabs/panels | 5 tabs | 1 dynamic workspace |
| Steps to design | 6+ clicks | 2-3 clicks |
| Column mapping | Manual | Auto-detect |
| Import formats | 1 (custom) | 4 (ETABS, SAFE, STAAD, generic) |
| Beam editing | None | Live edit with preview |

---

## Files to Modify

| File | Changes |
|------|---------|
| `pages/10_🤖_ai_assistant.py` | Complete rewrite |
| `utils/etabs_mapper.py` | NEW - Auto-mapping logic |
| `data/sample_etabs.csv` | NEW - Sample data |
| `components/workspace_states.py` | NEW - State renderers |

---

## Timeline

| Session | Task | Duration |
|---------|------|----------|
| 52 | Phase 1: Architecture refactor | 1 day |
| 53 | Phase 2-3: Welcome + Import | 1 day |
| 54 | Phase 4-5: Design + 3D | 1 day |
| 55 | Phase 6: Edit + Polish | 1 day |

**Total:** 4 sessions / 4 days

---

## Related Documents

- [8-week-development-plan.md](8-week-development-plan.md) - Overall roadmap
- [live-3d-visualization-architecture.md](../research/live-3d-visualization-architecture.md) - 3D system
- [ai-effective-usage-patterns.md](../research/ai-effective-usage-patterns.md) - AI model patterns

---

## Appendix: Research References

### Modern AI Chat UI Patterns

1. **ChatGPT / Claude**
   - Full-height chat with sidebar for history
   - Minimal chrome, maximum content
   - Streaming responses with typewriter effect

2. **Cursor IDE**
   - Chat integrated into IDE workflow
   - Context-aware suggestions
   - Actions that modify code directly

3. **Streamlit LLM Examples**
   - `st.chat_message` + `st.chat_input` pattern
   - `st.write_stream` for typewriter effect
   - Session state for history

4. **Streamlit Elements**
   - MUI components for professional look
   - Draggable dashboards
   - Monaco editor integration

### Key Streamlit APIs

```python
# Chat elements
st.chat_message("user/assistant")
st.chat_input("placeholder")
st.write_stream(generator)

# Layout
st.columns([0.35, 0.65])
st.container(border=True)
st.dataframe(on_select="rerun", selection_mode="single-row")

# State
st.session_state
st.rerun()
```
