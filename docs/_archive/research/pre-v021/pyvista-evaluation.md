# PyVista Evaluation for CAD-Quality 3D Visualization

**Type:** Research
**Audience:** Developers
**Status:** Approved
**Importance:** High
**Created:** 2026-01-21
**Last Updated:** 2026-01-21
**Related Tasks:** TASK-PHASE4

---

## Executive Summary

**Recommendation: Hybrid approach - Keep Plotly as primary, add PyVista export for CAD-quality output**

PyVista offers superior CAD-quality rendering and export capabilities (STL, VTK, screenshots), but has significant deployment challenges on Streamlit Cloud. The optimal strategy is to keep Plotly for interactive web visualization and use PyVista for high-quality export/screenshot generation.

---

## 0. Professional CAD Quality Guidelines

### 0.1 Beam Count to LOD Mapping

| Beam Count | LOD Level | Rendering Strategy | Target FPS |
|------------|-----------|-------------------|------------|
| 1-50 | ULTRA_HIGH | Full rebar + stirrups + PBR | 60 |
| 51-250 | HIGH | Simplified rebar + stirrups | 45 |
| 251-500 | MEDIUM | Box beams + simplified bars | 30 |
| 501-1000 | LOW | Simple boxes only | 20 |
| 1000+ | ULTRA_LOW | Billboards/lines + clustering | 15 |

### 0.2 Industry-Standard CAD Output

For professional CAD output (DXF/DWG/STL):

```python
# Always use maximum detail for export
export_config = {
    "mesh_resolution": "high",      # Don't simplify for export
    "include_rebar": True,          # Full reinforcement geometry
    "include_stirrups": True,       # Include shear reinforcement
    "pbr_materials": True,          # Physical-based rendering
    "dimension_lines": True,        # CAD dimension annotations
    "layer_separation": True,       # Separate layers for CAD editing
}
```

### 0.3 Quality Targets by Use Case

| Use Case | Resolution | Detail Level | Format |
|----------|------------|--------------|--------|
| Screen preview | 1080p | LOD-based | Plotly/WebGL |
| Report images | 2K | Full detail | PNG/SVG |
| CAD import | N/A | Full detail | STL/VTK/DXF |
| Print drawings | 4K+ | Full detail | PDF/DXF |
| BIM integration | N/A | Full detail | IFC/STL |

---

## 1. Technology Comparison

| Feature | Plotly (Current) | PyVista | Three.js (V3) |
|---------|------------------|---------|---------------|
| **Rendering Quality** | Good (WebGL) | Excellent (VTK) | Excellent (WebGL/WebGPU) |
| **CAD Export (STL/VTK)** | ❌ None | ✅ Native | ❌ Client-side only |
| **High-res Screenshots** | ⚠️ Browser-dependent | ✅ 4K+ resolution | ⚠️ Client-side |
| **Streamlit Integration** | ✅ Native | ⚠️ stpyvista (iframe) | ❌ Requires V3 |
| **Performance (1000 beams)** | ⚠️ Degrades | ✅ VTK optimized | ✅ Instancing |
| **Deployment Complexity** | ✅ Zero | ⚠️ Xvfb required | ⚠️ React build |
| **Interactive Features** | ✅ Hover, click | ✅ Pick, clip, slice | ✅ Full control |
| **Materials/Lighting** | ⚠️ Basic | ✅ PBR materials | ✅ PBR materials |
| **Cross-section Views** | ⚠️ Manual | ✅ Clipping planes | ✅ Clipping planes |

---

## 2. PyVista Capabilities

### 2.1 Core Strengths

```python
import pyvista as pv

# CAD-quality mesh with proper lighting
plotter = pv.Plotter()
plotter.add_mesh(beam_mesh, color='#C0C0C0',
                 pbr=True, metallic=0.1, roughness=0.5)
plotter.add_mesh(rebar_mesh, color='#1E40AF',
                 pbr=True, metallic=0.8, roughness=0.3)

# Built-in export
plotter.screenshot('beam_render.png', scale=4)  # 4x resolution
beam_mesh.save('beam.stl')  # Direct STL export
beam_mesh.save('beam.vtk')  # VTK for CAD tools
```

### 2.2 Advanced Features for Structural Engineering

1. **Clipping Planes** - Built-in cross-section views
2. **Picking** - Interactive beam selection with callbacks
3. **Silhouettes** - CAD-style edge rendering
4. **Annotations** - Dimension lines and labels
5. **Volume Rendering** - Stress/utilization visualization
6. **Multi-view** - Side-by-side comparison

### 2.3 Streamlit Integration (stpyvista)

```python
import pyvista as pv
import stpyvista
from stpyvista.utils import start_xvfb

# Required for headless deployment
start_xvfb()

plotter = pv.Plotter()
plotter.add_mesh(mesh)

# Render in Streamlit (via iframe)
stpyvista.stpyvista(plotter)
```

---

## 3. Deployment Challenges

### 3.1 Streamlit Cloud Requirements

```
# packages.txt (Linux packages required)
libgl1-mesa-glx
xvfb
procps
```

### 3.2 Known Issues

| Issue | Impact | Workaround |
|-------|--------|------------|
| **macOS NSInternalInconsistencyException** | Dev machines crash | Use VM or skip on macOS |
| **Xvfb memory overhead** | ~100MB per session | Start once via session_state |
| **VTK version conflicts** | cadquery bundled VTK | Install stpyvista first |
| **iframe communication** | No direct callbacks | Use Plotly for interactive |

### 3.3 Performance on Streamlit Cloud

- Cold start: +3-5 seconds (Xvfb initialization)
- Memory: +100-200MB per session
- Render time: Similar to Plotly for simple meshes
- Large models: PyVista handles 1000+ beams better

---

## 4. Recommended Implementation Strategy

### Phase 1: Export-Only Integration (Low Risk)

Add PyVista as optional dependency for high-quality export:

```python
# In pyproject.toml
[project.optional-dependencies]
cad = ["pyvista>=0.43", "stpyvista>=0.1.4"]
```

```python
# visualization_export.py
def export_beam_stl(geometry: Beam3DGeometry, path: str) -> None:
    """Export beam to STL for CAD import."""
    import pyvista as pv

    mesh = pv.PolyData(vertices, faces)
    mesh.save(path)

def render_beam_screenshot(geometry: Beam3DGeometry, path: str,
                           resolution: int = 2048) -> None:
    """Render high-quality screenshot using PyVista."""
    import pyvista as pv

    plotter = pv.Plotter(off_screen=True)
    plotter.add_mesh(beam_mesh, color='#C0C0C0', pbr=True)
    plotter.add_mesh(rebar_mesh, color='#1E40AF', pbr=True)
    plotter.screenshot(path, scale=resolution // 800)
```

### Phase 2: Hybrid Visualization (Medium Risk)

Keep Plotly for interactive, add PyVista toggle for CAD-quality:

```python
# In Streamlit page
render_mode = st.selectbox("Render Quality",
                           ["Standard (Plotly)", "CAD Quality (PyVista)"])

if render_mode == "Standard (Plotly)":
    fig = create_beam_3d_figure(...)
    st.plotly_chart(fig)
else:
    import stpyvista
    plotter = create_pyvista_plotter(...)
    stpyvista.stpyvista(plotter)
```

### Phase 3: Full PyVista (Deferred to V3)

For V3 React migration, consider:
- FastAPI backend with PyVista rendering
- Stream screenshots or use VTK.js for client-side
- Full CAD interactivity with picking/clipping

---

## 5. Implementation Plan for v0.19

### 5.1 Tasks

| Task | Priority | Effort | Notes |
|------|----------|--------|-------|
| Add pyvista to optional deps | 🔴 High | 1h | `cad` extras |
| Create `visualization_export.py` | 🔴 High | 4h | STL, screenshot export |
| Add export buttons to UI | 🔴 High | 2h | Beam design page |
| Test on Streamlit Cloud | 🟡 Medium | 2h | Verify Xvfb works |
| Document CAD export workflow | 🟡 Medium | 1h | User guide |

### 5.2 Files to Create/Modify

1. **New:** `streamlit_app/components/visualization_export.py`
2. **Modify:** `Python/pyproject.toml` - Add `cad` optional dep
3. **Modify:** `streamlit_app/pages/01_beam_design.py` - Add export tab
4. **New:** `docs/guides/cad-export-guide.md`

---

## 6. Code Prototype

### 6.1 Mesh Conversion (Plotly → PyVista)

```python
def plotly_mesh_to_pyvista(mesh3d: go.Mesh3d) -> 'pv.PolyData':
    """Convert Plotly Mesh3d to PyVista PolyData."""
    import pyvista as pv
    import numpy as np

    vertices = np.column_stack([mesh3d.x, mesh3d.y, mesh3d.z])
    faces = np.column_stack([mesh3d.i, mesh3d.j, mesh3d.k])

    # PyVista face format: [n_points, p1, p2, p3, ...]
    n_faces = len(faces)
    pv_faces = np.column_stack([
        np.full(n_faces, 3),  # All triangles
        faces
    ]).flatten()

    return pv.PolyData(vertices, pv_faces)
```

### 6.2 High-Quality Beam Render

```python
def render_beam_hq(
    geometry: dict,
    output_path: str = 'beam_render.png',
    resolution: int = 2048,
    background: str = '#1a1a2e'
) -> str:
    """Render CAD-quality beam visualization."""
    import pyvista as pv

    pv.OFF_SCREEN = True
    plotter = pv.Plotter(off_screen=True)
    plotter.set_background(background)

    # Concrete beam with semi-transparency
    if 'concrete' in geometry:
        concrete = create_box_mesh(geometry['concrete'])
        plotter.add_mesh(concrete, color='#D1D5DB',
                        opacity=0.3, pbr=True, roughness=0.8)

    # Rebar with metallic appearance
    for bar in geometry.get('bottom_bars', []):
        mesh = create_cylinder_mesh(bar)
        plotter.add_mesh(mesh, color='#DC2626',
                        pbr=True, metallic=0.8, roughness=0.3)

    for bar in geometry.get('top_bars', []):
        mesh = create_cylinder_mesh(bar)
        plotter.add_mesh(mesh, color='#1E40AF',
                        pbr=True, metallic=0.8, roughness=0.3)

    # Stirrups
    for stirrup in geometry.get('stirrups', []):
        mesh = create_stirrup_mesh(stirrup)
        plotter.add_mesh(mesh, color='#16A34A',
                        pbr=True, metallic=0.6)

    # Camera and lighting
    plotter.camera_position = 'iso'
    plotter.add_light(pv.Light(position=(1, 1, 1), intensity=0.8))

    # Render
    plotter.screenshot(output_path, scale=resolution // 800)
    plotter.close()

    return output_path
```

---

## 7. Decision Matrix

| Scenario | Recommendation |
|----------|----------------|
| Interactive exploration | **Plotly** (current) |
| Print-quality screenshots | **PyVista** (off-screen) |
| STL export for CAD | **PyVista** |
| PDF report images | **PyVista** |
| 1000+ beams visualization | **PyVista** (better performance) |
| Quick preview | **Plotly** (faster startup) |
| V3 React migration | **Three.js** (client-side) |

---

## 8. Conclusion

**For v0.19:**
1. Keep Plotly as primary visualization (proven, works everywhere)
2. Add PyVista as optional dependency for CAD export
3. Implement STL export and high-res screenshot features
4. Document the hybrid approach

**For V3 (v0.21+):**
- Consider FastAPI + PyVista backend for server-side rendering
- Three.js/React Three Fiber for client-side interactivity
- Full CAD-quality without deployment headaches

---

## References

- [PyVista Documentation](https://docs.pyvista.org/)
- [stpyvista GitHub](https://github.com/edsaac/stpyvista)
- [VTK File Formats](https://vtk.org/wp-content/uploads/2015/04/file-formats.pdf)
- [PBR Materials in PyVista](https://docs.pyvista.org/version/stable/examples/02-plot/pbr.html)
