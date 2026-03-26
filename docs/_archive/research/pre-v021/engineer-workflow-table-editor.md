# Engineer Workflow: Table Editor & 3D Visualization

**Type:** Research
**Audience:** Developers
**Status:** Draft
**Importance:** High
**Created:** 2026-01-22
**Last Updated:** 2026-01-22
**Related Tasks:** Session 33

---

## 1. Engineer's Mental Model

An engineer designing beams thinks in this flow:

```
Import Data → Overview → Filter/Group → Review Issues → Fix Issues → Verify → Export
```

### 1.1 Current Pain Points (Session 33 Findings)

| Issue | Impact | User Quote |
|-------|--------|------------|
| 3D view hidden in expander | Can't see building context | "3D view not working" |
| No beam focus on selection | Lost in large projects | "focus camera on that beam" |
| Top 20% wasted space | Too much scrolling | "use full page" |
| Two optimize buttons | Confusing | "why two optimize buttons" |
| Filter changes results | Unexpected behavior | "still many beams fail after filter" |
| No single-beam optimize | Can't fix one at a time | "button to optimize only that" |
| Column widths uniform | Inefficient space use | "size of each column need not be same" |
| Error messages vague | Hard to diagnose | "error message can be better" |
| Utilization not highlighted | Hard to spot issues | "highlight cells which we need to change" |

---

## 2. Proposed Engineer Workflow

### 2.1 Complete Flow (Start to End)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          ENGINEER WORKFLOW                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  STEP 1: IMPORT                                                          │
│  ┌─────────────────┐                                                     │
│  │ Upload CSV/JSON │  → Validate format → Show summary (X beams, Y fail) │
│  └─────────────────┘                                                     │
│                                                                          │
│  STEP 2: OVERVIEW (3D Building View)                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  ┌─────────────────────────────────────────────────────────────┐│    │
│  │  │              FULL 3D BUILDING VIEW (40% height)             ││    │
│  │  │   • Red = Failed beams, Green = Passed                      ││    │
│  │  │   • Click beam → Selects row in table below                 ││    │
│  │  │   • Floor selector → Filters both 3D + Table                ││    │
│  │  └─────────────────────────────────────────────────────────────┘│    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  STEP 3: FILTER & GROUP                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ [Story ▼] [Beam Line ▼] [Status: Failed Only ▼] [⚡ Optimize All]│    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  STEP 4: TABLE VIEW (Review & Edit)                                      │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │ ID    │ Size   │ Mu  │ Vu  │ Bot# │ϕBot │ Util% │ Status │ ⚡  │    │
│  ├───────┼────────┼─────┼─────┼──────┼─────┼───────┼────────┼─────┤    │
│  │ B1-1F │ 300x500│ 120 │ 80  │  4   │ 16  │ 85%▓▓ │ ✅ PASS │     │    │
│  │ B2-1F │ 300x450│ 180 │ 90  │  3   │ 16  │ 115%▓▓│ ❌ FAIL │ [⚡]│    │
│  │ B3-1F │ 300x500│ 95  │ 60  │  4   │ 12  │ 72%▓▓ │ ✅ PASS │     │    │
│  └───────┴────────┴─────┴─────┴──────┴─────┴───────┴────────┴─────┘    │
│  ↑                                                                       │
│  Click row → 3D zooms to that beam with reinforcement detail             │
│                                                                          │
│  STEP 5: FOCUSED EDITING (When row selected)                             │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  3D VIEW TRANSITIONS TO:                                         │    │
│  │  ┌─────────────────────────────────────────────────────────────┐│    │
│  │  │       SINGLE BEAM WITH REINFORCEMENT (Zoomed)               ││    │
│  │  │   • Shows actual bars (bottom + top)                        ││    │
│  │  │   • Shows stirrups at actual spacing                        ││    │
│  │  │   • Rotate/zoom for inspection                              ││    │
│  │  └─────────────────────────────────────────────────────────────┘│    │
│  │  [← Back to Floor] [⚡ Optimize This] [✓ Save] [→ Next Failed]  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  STEP 6: VERIFY                                                          │
│  • All beams green in 3D                                                 │
│  • Status filter shows 0 Failed                                          │
│  • Summary: "All 150 beams PASS"                                         │
│                                                                          │
│  STEP 7: EXPORT                                                          │
│  [📥 Export CSV] [📄 Export Report] [📐 Export DXF]                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Layout Redesign

### 3.1 Current Layout (Problems)

```
┌─────────────────────────────────────────┐
│ Header (80px)                           │  ← Minimal, OK
├─────────────────────────────────────────┤
│ [Expander: 3D Floor View] (collapsed)   │  ← HIDDEN! Not useful
├─────────────────────────────────────────┤
│ Caption + Toolbar (120px)               │  ← TOO MUCH SPACE
├─────────────────────────────────────────┤
│ Table (400px fixed)                     │  ← FIXED HEIGHT = bad
├─────────────────────────────────────────┤
│ (empty space)                           │  ← WASTED
└─────────────────────────────────────────┘
```

### 3.2 Proposed Layout

```
┌─────────────────────────────────────────┐
│ Header + Toolbar (50px)                 │  ← COMPACT
│ [Group▼][Status▼][Floor▼]  [⚡Optimize All]│
├─────────────────────────────────────────┤
│                                         │
│  3D VIEW (35% of screen)                │  ← ALWAYS VISIBLE
│  • Building view by default             │
│  • Transitions to beam detail on select │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  TABLE (65% of screen, dynamic height)  │  ← FILLS REMAINING
│  • Row selection triggers 3D transition │
│  • Per-row optimize button              │
│  • Highlighted cells for issues         │
│                                         │
└─────────────────────────────────────────┘
```

---

## 4. Implementation Plan

### 4.1 Phase 1: Critical Fixes (Session 33 - COMPLETED)

| Priority | Task | Status | Notes |
|----------|------|--------|-------|
| P1 | Remove duplicate "Optimize All" button | ✅ Done | Single button in toolbar |
| P1 | Fix beam-line filter state bug | ✅ Done | Recalculate is_safe on init |
| P2 | Make 3D view always visible | ✅ Done | Above table, 280px height |
| P2 | Add beam selection → 3D focus | ✅ Done | Click selectbox → focused view |
| P2 | Show reinforcement in focused beam | ✅ Done | Uses create_beam_3d_figure |
| P3 | Improve column widths (smart sizing) | ✅ Done | 45-80px based on content |
| P3 | Stirrup optimization (8/10/12mm) | ✅ Done | 100-300mm spacing range |
| P3 | Auto-layout when no coordinates | ✅ Done | Grid based on beam_line |

### 4.2 Phase 2: Enhanced Features (Next Session)

| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| P1 | Show reinforcement in ALL floor beams | 45 min | WOW factor |
| P2 | Click beam in 3D → select table row | 30 min | Two-way sync |
| P2 | Highlight cells >100% utilization | 15 min | Visual clarity |
| P3 | Dynamic table (click cell → update 3D) | 45 min | Complex - needs workaround |

### 4.3 Phase 3: Polish (Future)

| Task | Notes |
|------|-------|
| Improved error messages | Show clause reference, required vs provided |
| Export buttons | CSV, PDF report, DXF |
| Undo/redo | Track changes, allow revert |
| Keyboard navigation | Arrow keys, Enter to optimize |

---

## 5. Technical Details

### 5.1 3D View Modes

```python
class View3DMode(Enum):
    BUILDING = "building"     # Multi-beam floor view
    FOCUSED = "focused"       # Single beam with rebar

# Session state tracking
st.session_state.view_3d_mode = View3DMode.BUILDING
st.session_state.focused_beam_id = None  # Set when row selected
```

### 5.2 Table-3D Interaction

```python
# When user clicks/selects a table row:
def on_row_select(beam_id: str):
    st.session_state.focused_beam_id = beam_id
    st.session_state.view_3d_mode = View3DMode.FOCUSED
    # 3D view will rerender with single beam + reinforcement

# When user clicks "Back to Floor":
def on_back_to_floor():
    st.session_state.focused_beam_id = None
    st.session_state.view_3d_mode = View3DMode.BUILDING
```

### 5.3 Existing 3D Functions (Reuse)

| Function | Purpose | Location |
|----------|---------|----------|
| `create_multi_beam_3d_figure()` | Building view | `visualizations_3d.py:857` |
| `create_beam_3d_figure()` | Single beam with rebar | `visualizations_3d.py:385` |
| `generate_cylinder_mesh()` | Rebar rendering | `visualizations_3d.py:130` |
| `generate_stirrup_tube()` | Stirrup rendering | `visualizations_3d.py:280` |

### 5.4 Column Sizing Strategy

```python
column_config = {
    "beam_id": st.column_config.TextColumn("ID", width=80),      # Fixed narrow
    "story": st.column_config.TextColumn("Story", width=60),     # Fixed narrow
    "b_mm": st.column_config.NumberColumn("b", width=50),        # Compact
    "D_mm": st.column_config.NumberColumn("D", width=50),        # Compact
    "mu_knm": st.column_config.NumberColumn("Mu", width=60),     # Compact
    "vu_kn": st.column_config.NumberColumn("Vu", width=60),      # Compact
    "bottom_bar_count": st.column_config.NumberColumn("Bot#", width=55),
    "bottom_bar_dia": st.column_config.SelectboxColumn("ϕBot", width=60),
    "_utilization": st.column_config.ProgressColumn("Util%", width=80),  # Wider for bar
    "status": st.column_config.TextColumn("Status", width=70),
    "_optimize": ...  # Per-row button column
}
```

---

## 6. Bugs Fixed (Session 33)

### 6.1 Duplicate Optimize Buttons ✅ Fixed

**Was:** Two buttons - toolbar row + above table.
**Now:** Single "Fix N Failed" button in toolbar.

### 6.2 Beam-Line Filter State Bug ✅ Fixed

**Was:** After filter, beams showed as failed even after optimization.
**Fix:** Added `is_safe` and `status` recalculation in initialization loop.

### 6.3 Stirrup Optimization Limited to 8mm ✅ Fixed

**Was:** `suggest_optimal_rebar()` only used 8mm stirrups.
**Now:** Supports 8/10/12mm with IS 456 shear calculation.
**Spacing:** 100, 125, 150, 175, 200, 250, 300mm options.

### 6.4 3D View All Beams Overlap ✅ Fixed

**Was:** Without coordinates, all beams at (0,0,0)→(1000,0,0).
**Now:** Auto-layout grid based on beam_line naming convention.

---

## 7. Known Issues (For Next Session)

| Metric | Current | Target |
|--------|---------|--------|
| Clicks to optimize one beam | 5+ | 1 (per-row button) |
| Screen utilization | ~50% | ~90% |
| Time to find failed beams | Scroll + read | Instant (red in 3D) |
| 3D visibility | Hidden expander | Always visible |
| Beam detail access | Switch to Single mode | Click row → zoom |

---

## 8. Next Steps

1. **This session:** Implement Phase 1 fixes
2. **Next session:** Implement Phase 2 (3D interaction)
3. **Testing:** Real project with 100+ beams
4. **Feedback:** Document new issues discovered
