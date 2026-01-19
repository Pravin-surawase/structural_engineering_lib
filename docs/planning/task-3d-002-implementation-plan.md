# TASK-3D-002: ETABS 3D Visualization Implementation Plan

**Type:** Plan
**Audience:** All Agents
**Status:** In Progress
**Importance:** High
**Created:** 2026-01-20
**Last Updated:** 2026-01-20
**Related Tasks:** TASK-VBA-001, TASK-3D-002
**PR:** #TBD (task/TASK-3D-002)

---

## Objective

Transform ETABS batch import page from fake grid visualization to true 3D building model using real coordinates from frames_geometry.csv.

## Current Status

### ✅ Completed (Commit d8e9baff)
- Added `FrameGeometry` dataclass to `Python/structural_lib/etabs_import.py`
- Added `load_frames_geometry()` function to parse frames_geometry.csv
- Added `merge_forces_and_geometry()` for cross-referencing
- Tested with real data: 153 beams + 72 columns successfully loaded

### 🚧 In Progress
- Update ETABS import page to use real 3D coordinates
- Replace fake grid layout with actual building coordinates

---

## Implementation Steps

### Step 1: Update ETABS Import Page to Load Geometry ✅

**File:** `streamlit_app/pages/06_📤_etabs_import.py`

**Changes:**
1. Import new functions from `structural_lib.etabs_import`:
   ```python
   from structural_lib.etabs_import import (
       load_frames_geometry,
       merge_forces_and_geometry,
       FrameGeometry,
   )
   ```

2. Add session state for geometry:
   ```python
   if "etabs_frames_geometry" not in st.session_state:
       st.session_state.etabs_frames_geometry = None
   ```

3. Add multi-file uploader (beam_forces + frames_geometry):
   ```python
   uploaded_files = st.file_uploader(
       "Upload ETABS CSV files",
       type="csv",
       accept_multiple_files=True,
       help="Upload beam_forces.csv and frames_geometry.csv"
   )
   ```

4. Parse both files in `process_etabs_csv()`:
   - Detect file type by name (beam_forces, frames_geometry)
   - Store both in session state
   - Call `merge_forces_and_geometry()` to link them

### Step 2: Rewrite `create_beam_grid_3d()` for Real Coordinates ⏳

**Current code (FAKE):**
```python
z = story_map.get(story, 0) * 4  # Vertical spacing (FAKE!)
x = beams_per_story.get(story, {}).get(beam_id, 0) * 2  # Horizontal (FAKE!)
y = 0  # Always zero (FAKE!)
```

**New code (REAL):**
```python
def create_building_3d_view(
    results_df: pd.DataFrame,
    geometry: dict[str, FrameGeometry]
) -> go.Figure:
    """Create true 3D building visualization using real coordinates."""
    fig = go.Figure()

    for _, row in results_df.iterrows():
        beam_id = row["Beam ID"]
        geom = geometry.get(beam_id)

        if not geom:
            continue  # Skip beams without geometry

        # Use REAL coordinates from frames_geometry
        x1, y1, z1 = geom.point1_x, geom.point1_y, geom.point1_z
        x2, y2, z2 = geom.point2_x, geom.point2_y, geom.point2_z

        # Color by status
        is_safe = row["_is_safe"]
        color = "rgb(40, 167, 69)" if is_safe else "rgb(220, 53, 69)"

        # Draw beam as 3D line
        fig.add_trace(go.Scatter3d(
            x=[x1, x2],
            y=[y1, y2],
            z=[z1, z2],
            mode="lines",
            line=dict(color=color, width=6),
            ...
        ))

    # Add columns (optional - toggle in UI)
    for _, frame in geometry.items():
        if frame.frame_type == "Column":
            # Draw column
            ...

    # Real axis labels
    fig.update_layout(
        scene=dict(
            xaxis_title="X (m)",
            yaxis_title="Y (m)",
            zaxis_title="Elevation (m)",
            aspectmode="data",  # Use real proportions!
        ),
        ...
    )
```

### Step 3: Add Column Visualization Toggle ⏳

**UI Addition:**
```python
show_columns = st.checkbox(
    "Show Columns",
    value=True,
    help="Display column elements in 3D view"
)

if show_columns:
    # Add columns to figure
    for frame in st.session_state.etabs_frames_geometry:
        if frame.frame_type == "Column":
            # Draw as vertical line with different color
            ...
```

### Step 4: Add Building Extent Info ⏳

**Calculate building dimensions:**
```python
def get_building_extent(frames: list[FrameGeometry]):
    """Calculate building bounding box."""
    xs = [f.point1_x for f in frames] + [f.point2_x for f in frames]
    ys = [f.point1_y for f in frames] + [f.point2_y for f in frames]
    zs = [f.point1_z for f in frames] + [f.point2_z for f in frames]

    return {
        "x_min": min(xs), "x_max": max(xs), "x_range": max(xs) - min(xs),
        "y_min": min(ys), "y_max": max(ys), "y_range": max(ys) - min(ys),
        "z_min": min(zs), "z_max": max(zs), "z_range": max(zs) - min(zs),
    }
```

**Display in UI:**
```python
st.info(f"""
**Building Dimensions:**
- Length (X): {extent['x_range']:.2f} m
- Width (Y): {extent['y_range']:.2f} m
- Height (Z): {extent['z_range']:.2f} m
- Total Frames: {len(frames)} ({beams_count} beams + {columns_count} columns)
""")
```

### Step 5: Testing with Real Data ⏳

**Test dataset:** `VBA/ETABS_Export_v2/Etabs_output/2026-01-17_222801/`
- beam_forces.csv: 154 beams
- frames_geometry.csv: 225 frames (153 beams + 72 columns)

**Expected results:**
- Building: 10.5m × 9m × 17m
- 6 stories visible at correct elevations (0, 2, 5, 8, 11, 14, 17m)
- Beams drawn at correct positions in 3D space
- Columns visible if toggle enabled
- Status colors correct (green=safe, red=unsafe)

### Step 6: Documentation ⏳

**Update files:**
- [docs/specs/csv-import-schema.md](../specs/csv-import-schema.md) - Add frames_geometry schema
- [docs/guides/etabs-vba-user-guide.md](../guides/etabs-vba-user-guide.md) - ETABS export workflow guide
- [docs/planning/8-week-development-plan.md](8-week-development-plan.md) - Mark Week 3-4 as in-progress

---

## Technical Decisions

### Q: Show columns by default?
**A:** YES - More impressive demo, shows complete building. Add toggle to hide.

### Q: Handle missing geometry gracefully?
**A:** YES - Skip beams without geometry, show warning count in UI.

### Q: Coordinate units?
**A:** Meters (m) for consistency with ETABS export. Display matches calculations.

### Q: LOD system now or later?
**A:** LATER (Step 5 in original plan). Current 225 frames renders instantly.

---

## Success Criteria

- ✅ Real coordinates from frames_geometry.csv displayed correctly
- ✅ Building dimensions match ETABS (10.5m × 9m × 17m)
- ✅ Story elevations correct (0, 2, 5, 8, 11, 14, 17m)
- ✅ Beams colored by design status (green/red)
- ✅ Columns visible with toggle
- ✅ Performance <100ms for 225 frames
- ✅ No regressions in existing functionality
- ✅ Tests pass with real data
- ✅ Documentation updated

---

## Next Session Tasks

1. ✅ Complete Step 1: Update imports and multi-file upload
2. ✅ Complete Step 2: Rewrite create_beam_grid_3d()
3. ✅ Complete Step 3: Add column toggle
4. ✅ Complete Step 4: Add building extent info
5. ✅ Complete Step 5: Test with real data
6. ✅ Complete Step 6: Update documentation
7. ✅ Commit all changes
8. ✅ Create PR with finish_task_pr.sh
9. ✅ Merge and move to next task (LOD system)

---

## Related Files

**Modified:**
- `Python/structural_lib/etabs_import.py` (✅ d8e9baff)
- `streamlit_app/pages/06_📤_etabs_import.py` (⏳ in progress)

**Created:**
- `docs/planning/task-3d-002-implementation-plan.md` (this file)

**Updated (planned):**
- `docs/specs/csv-import-schema.md`
- `docs/guides/etabs-vba-user-guide.md`
- `docs/planning/8-week-development-plan.md`

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing batch design | HIGH | Test thoroughly before commit |
| Performance regression with columns | MEDIUM | Add toggle to hide columns |
| Missing geometry for some beams | LOW | Graceful fallback, show warning |
| Coordinate mismatch | HIGH | Validate with known building dimensions |

---

**Status:** IN PROGRESS (Step 1-2)
**Next:** Implement multi-file upload and rewrite 3D function
