# Design Editor Workflow & UX Research

**Type:** Research
**Audience:** Developers, UX Designers
**Status:** Draft
**Importance:** High
**Created:** 2026-01-22
**Last Updated:** 2026-01-22
**Related Tasks:** TASK-EDITOR-UX

---

## 1. Executive Summary

This document researches the optimal workflow for structural engineers using the design editor. The current implementation has UX issues that prevent practical use. This research proposes a **unified editor experience** with integrated 3D visualization and AI-assisted design checks.

---

## 2. Current State Analysis

### 2.1 Current Issues

| Issue | Impact | Priority |
|-------|--------|----------|
| **Separate edit and check views** | Engineers must switch between panels to see results | Critical |
| **No contextual 3D feedback** | Can't visualize changes while editing | High |
| **Chat panel takes space during editing** | Reduces editor workspace | Medium |
| **No beam-line navigation** | Hard to work through beams systematically | Medium |
| **No undo/redo capability** | Risky edits without safety net | High |

### 2.2 Current Layout (35% Chat + 65% Workspace)

```
┌──────────────────────────────────────────────────────────────────────┐
│ ⚡ StructEng AI                                    📍 Design         │
├──────────────────┬───────────────────────────────────────────────────┤
│                  │                                                   │
│    AI CHAT       │              WORKSPACE                            │
│    (35%)         │              (65%)                                │
│                  │                                                   │
│  Messages        │   Results Table / Editor / 3D Views               │
│  ...             │                                                   │
│                  │                                                   │
│  ─────────────   │                                                   │
│  Input           │                                                   │
│                  │                                                   │
└──────────────────┴───────────────────────────────────────────────────┘
```

**Problem:** During editing, the 35% chat column wastes valuable screen space.

---

## 3. Proposed Solution: Unified Editor Mode

### 3.1 Full-Width Editor Layout (When Editing)

When an engineer enters edit mode, collapse the chat panel and maximize the editor:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ ⚡ Editor: B1-001                          💬 Chat │ ← Back │ Save │ Next → │
├──────────────────────────────────────────────────────────────────────────────┤
│                         3D REBAR PREVIEW (Dynamic)                           │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                                                                        │  │
│  │            [3D beam visualization - updates on every edit]             │  │
│  │                  Shows: bars, stirrups, dimensions                     │  │
│  │                                                                        │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
├────────────────────────────────────────┬─────────────────────────────────────┤
│        REINFORCEMENT CONTROLS          │         LIVE DESIGN CHECKS          │
│  ┌──────────────────────────────────┐  │  ┌─────────────────────────────────┐│
│  │ Section: 300×450 | Span: 4.5m   │  │  │ 🟢 Flexure: 85% (Mu=156 kN·m)  ││
│  │ Mu=142 kN·m | Vu=78 kN          │  │  │ 🟢 Shear: 62% (Vu=126 kN)      ││
│  ├──────────────────────────────────┤  │  │ 🟢 Min Ast: 628 ≥ 285 mm²     ││
│  │ BOTTOM BARS                      │  │  │ 🟢 Max Ast: 628 ≤ 2700 mm²    ││
│  │ Layer 1: [4▼] × ϕ[16▼]          │  │  │ 🟢 Spacing: 76mm ≥ 25mm       ││
│  │ Layer 2: [0▼] × ϕ[12▼]          │  │  ├─────────────────────────────────┤│
│  ├──────────────────────────────────┤  │  │ ✅ ALL CHECKS PASS              ││
│  │ TOP BARS                         │  │  │ Ast: 628 mm² | d_eff: 394mm    ││
│  │ [2▼] × ϕ[12▼]                   │  │  └─────────────────────────────────┘│
│  ├──────────────────────────────────┤  │                                     │
│  │ STIRRUPS                         │  │  ┌─────────────────────────────────┐│
│  │ ϕ[8▼] @ [150▼] mm              │  │  │ 📐 Cross-Section 2D View       ││
│  └──────────────────────────────────┘  │  │      [Inline section drawing]   ││
│                                        │  └─────────────────────────────────┘│
├────────────────────────────────────────┴─────────────────────────────────────┤
│  ◀ B1-000 │ ▌▌▌▌▌▌●▌▌▌▌▌▌ │ B1-002 ▶     [Beam navigation - 12 of 48]      │
│            [Auto-saves on navigation]      │ Export All │ Apply Optimizations │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Key Features

#### A. Dynamic 3D Preview (Top Section)
- **Real-time update:** 3D view updates instantly when any rebar value changes
- **Camera memory:** Keeps same view angle when values change
- **Toggle views:** Switch between 3D isometric, front elevation, side elevation
- **Highlight active:** Currently-editing bar layer highlighted in different color

#### B. Unified Controls + Checks (Side-by-Side)
- **No scrolling needed:** All controls and checks visible simultaneously
- **Immediate feedback:** Check status updates as you change values
- **Visual indicators:** 🟢/🔴 status is instantly visible

#### C. Beam Navigation Bar (Bottom)
- **Progress indicator:** Shows which beams done, current, remaining
- **Quick jump:** Click any beam dot to jump to it
- **Auto-save:** Changes saved automatically on navigation
- **Batch status:** Colors show pass/fail status of each beam

#### D. Collapsible Chat (Header Button)
- **💬 Chat button:** Opens chat panel as overlay when needed
- **AI assistance:** Ask AI for optimization suggestions without leaving editor
- **Contextual awareness:** AI knows which beam you're editing

---

## 4. Engineer Workflow Scenarios

### 4.1 Scenario: Reviewing Failed Beams

**Goal:** Fix all failed beam designs efficiently

**Current workflow (problematic):**
1. View results table → See 5 failures
2. Click one beam → Navigate to rebar editor
3. Adjust values → See checks update
4. Go back to results → See if fixed
5. Repeat for each beam (context switching)

**Proposed workflow (efficient):**
1. Filter by "Failed" → Shows only failed beams
2. Click "Edit All Failed" → Enters editor mode
3. Editor shows first failed beam with 3D + checks
4. Adjust values → Checks update live, 3D updates
5. Click "→ Next" → Auto-saves, moves to next failed
6. Repeat until all fixed (no context switching)

### 4.2 Scenario: Beam-Line Standardization

**Goal:** Standardize all beams in a beam line to same rebar

**Proposed feature:**
```
┌─────────────────────────────────────────────────────────────┐
│ 🎯 Standardize Beam Line                                    │
│                                                             │
│ Select: [BL-01 ▼] (12 beams)                               │
│                                                             │
│ Current variation:                                          │
│   4×ϕ16 (6 beams) | 3×ϕ16 (4 beams) | 4×ϕ20 (2 beams)     │
│                                                             │
│ Proposed standard: [4▼] × ϕ[20▼]                          │
│   ✅ 10 beams pass | ⚠️ 2 beams marginal (95-100%)         │
│                                                             │
│ [Preview Changes] [Apply to All]                            │
└─────────────────────────────────────────────────────────────┘
```

This is the **Beam-Line Standardization Optimization** feature for V1.1.

### 4.3 Scenario: Quick Optimization

**Goal:** Auto-optimize all beams for minimum steel

```
┌─────────────────────────────────────────────────────────────┐
│ ⚡ Auto-Optimize                                            │
│                                                             │
│ Strategy: [Minimum Steel ▼]                                │
│           • Minimum Steel (cost optimized)                  │
│           • Standard Diameters Only                         │
│           • Constructability Priority                       │
│           • Balance (cost + constructability)               │
│                                                             │
│ Scope: [All Beams ▼]                                       │
│        • All Beams (48 beams)                               │
│        • Current Story (12 beams)                           │
│        • Selected Beam Line (8 beams)                       │
│        • Failed Beams Only (5 beams)                        │
│                                                             │
│ [Preview] [Optimize]                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Technical Implementation

### 5.1 State Management

```python
# New session state structure for editor mode
st.session_state.editor_mode = {
    "active": False,
    "current_beam_idx": 0,
    "beam_queue": ["B1-001", "B1-002", ...],  # Beams to edit
    "unsaved_changes": {},
    "undo_stack": [],
    "redo_stack": [],
    "chat_visible": False,
}
```

### 5.2 Layout Switching

```python
def render_ai_page():
    editor_mode = st.session_state.get("editor_mode", {}).get("active", False)

    if editor_mode:
        # Full-width editor layout
        render_full_editor()
    else:
        # Normal 35/65 layout
        chat_col, workspace_col = st.columns([0.35, 0.65])
        with chat_col:
            render_chat_panel()
        with workspace_col:
            render_dynamic_workspace()
```

### 5.3 Dynamic 3D Update

```python
@st.fragment
def render_editor_3d_preview():
    """Fragment for dynamic 3D that updates without full rerun."""
    config = st.session_state.ws_rebar_config
    beam_data = get_current_beam_data()

    # Build 3D mesh from current config
    mesh = create_beam_mesh(
        b=beam_data["b_mm"],
        D=beam_data["D_mm"],
        span=beam_data["span_mm"],
        bottom_bars=config["bottom_bars"],
        top_bars=config["top_bars"],
        stirrup_dia=config["stirrup_dia"],
        stirrup_spacing=config["stirrup_spacing"],
    )

    # Render with stpyvista
    stpyvista(mesh, key="editor_3d_preview")
```

### 5.4 Auto-Save on Navigation

```python
def navigate_to_beam(direction: str):
    """Navigate to next/prev beam with auto-save."""
    # Save current changes
    if st.session_state.editor_mode["unsaved_changes"]:
        apply_changes_to_beam(
            st.session_state.ws_selected_beam,
            st.session_state.ws_rebar_config
        )

    # Move to next/prev beam
    idx = st.session_state.editor_mode["current_beam_idx"]
    queue = st.session_state.editor_mode["beam_queue"]

    if direction == "next" and idx < len(queue) - 1:
        st.session_state.editor_mode["current_beam_idx"] = idx + 1
    elif direction == "prev" and idx > 0:
        st.session_state.editor_mode["current_beam_idx"] = idx - 1

    # Load new beam
    new_beam = queue[st.session_state.editor_mode["current_beam_idx"]]
    st.session_state.ws_selected_beam = new_beam
    st.session_state.ws_rebar_config = None  # Reset to load new config
```

---

## 6. Implementation Roadmap

### Phase 1: Core Editor Improvements (Current Sprint)
- [x] Fix NaN handling in editable table
- [x] Fix 2D section bar positioning
- [ ] Add full-width editor mode toggle
- [ ] Integrate 3D preview in editor

### Phase 2: Navigation & Workflow (V1.0)
- [ ] Beam navigation bar
- [ ] Auto-save on navigation
- [ ] Undo/redo support
- [ ] Filter-then-edit workflow

### Phase 3: Optimization Features (V1.1)
- [ ] Beam-line standardization
- [ ] Auto-optimize with strategies
- [ ] Batch operations
- [ ] Cost estimation

---

## 7. UI/UX Guidelines

### 7.1 Design Principles

1. **No context switching:** All relevant info visible simultaneously
2. **Immediate feedback:** Changes reflected within 100ms
3. **Keyboard-first:** Support Tab, Enter, Arrow keys for power users
4. **Fail-safe:** Auto-save, undo/redo, confirmation for destructive actions

### 7.2 Color Coding

| Status | Color | Use Case |
|--------|-------|----------|
| Pass | 🟢 `#28b463` | Check passed, beam safe |
| Fail | 🔴 `#e74c3c` | Check failed, needs attention |
| Warning | 🟡 `#f39c12` | Marginal (90-100% utilization) |
| Info | 🔵 `#3498db` | Informational, no action needed |
| Editing | 🟣 `#9b59b6` | Currently being edited |

### 7.3 Keyboard Shortcuts (Future)

| Shortcut | Action |
|----------|--------|
| `Tab` | Move to next input field |
| `Shift+Tab` | Move to previous input field |
| `Ctrl+S` | Save current beam |
| `Ctrl+Z` | Undo last change |
| `Ctrl+Y` | Redo |
| `Ctrl+→` | Next beam |
| `Ctrl+←` | Previous beam |
| `Esc` | Exit editor mode |

---

## 8. References

- [Streamlit Fragment Documentation](https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment)
- [stpyvista Integration](../research/live-3d-visualization-architecture.md)
- [IS 456:2000 Design Requirements](../reference/is456-quick-reference.md)

---

## 9. Open Questions

1. **Performance:** Can we achieve <100ms 3D updates with current stpyvista integration?
2. **Mobile support:** Should editor work on tablets? (Common on construction sites)
3. **Offline mode:** Should changes be savable locally when network is unavailable?
4. **Multi-user:** Should we support collaborative editing in future?

---

*Document created based on UX research session on 2026-01-22*
