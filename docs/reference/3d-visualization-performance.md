# 3D Visualization Performance Benchmarks

**Type:** Reference
**Audience:** Developers
**Status:** Production Ready
**Importance:** Medium
**Created:** 2026-01-18
**Last Updated:** 2026-01-18
**Related Tasks:** TASK-3D-10, TASK-3D-12

---

## Overview

This document provides performance benchmarks for the 3D beam visualization module (`streamlit_app/components/visualizations_3d.py`). These benchmarks ensure the visualization meets the <100ms latency target for live preview functionality.

## Performance Targets

| Metric | Target | Measured | Status |
|--------|--------|----------|--------|
| Simple figure generation | <150ms | ~50-100ms | ✅ Pass |
| Complex figure (80 stirrups) | <500ms | ~140ms | ✅ Pass |
| Single cylinder mesh | <5ms | <1ms | ✅ Pass |
| Geometry hash computation | <1ms | <0.1ms | ✅ Pass |

## Test Results (Session 37)

### Test Suite Summary

```
tests/test_visualizations_3d.py
├── TestGenerateCylinderMesh (5 tests)     ✅ All passing
├── TestGenerateBoxMesh (3 tests)          ✅ All passing
├── TestGenerateStirrupTube (2 tests)      ✅ All passing
├── TestCreateBeam3dFigure (5 tests)       ✅ All passing
├── TestCreateBeam3dFromDict (2 tests)     ✅ All passing
├── TestComputeGeometryHash (3 tests)      ✅ All passing
├── TestPerformance (4 tests)              ✅ All passing
└── TestColors (2 tests)                   ✅ All passing

Total: 26 tests, 100% passing
Execution time: ~1.5 seconds
```

### Performance Test Details

#### 1. Simple Figure Generation

**Test:** `TestPerformance::test_simple_figure_performance`

```python
# Parameters
b = 300mm (width)
D = 450mm (depth)
span = 4000mm

# Result
Typical: 50-100ms
Threshold: <150ms (with CI headroom)
```

**Includes:**
- Concrete beam mesh generation
- Default rebar placement calculation
- 6 stirrup tube meshes
- Plotly figure construction

#### 2. Complex Figure Generation

**Test:** `TestPerformance::test_complex_figure_performance`

```python
# Parameters
b = 300mm
D = 450mm
span = 8000mm
bottom_bars = 4 bars
top_bars = 2 bars
stirrups = 80 positions (100mm spacing)

# Result
Typical: ~140ms
Threshold: <500ms
```

**Notes:**
- Linear scaling with stirrup count
- 80 stirrups ≈ 140ms → ~1.75ms per stirrup
- WebGL handles rendering efficiently

#### 3. Cylinder Mesh Performance

**Test:** `TestPerformance::test_cylinder_mesh_performance`

```python
# Parameters
start = (0, 0, 0)
end = (4000, 0, 0)
radius = 8mm
iterations = 10 (averaged)

# Result
Typical: <1ms per cylinder
Threshold: <5ms
```

#### 4. Geometry Hash Performance

**Test:** `TestPerformance::test_geometry_hash_performance`

```python
# Hash computation for caching
iterations = 100 (averaged)

# Result
Typical: <0.1ms per hash
Threshold: <1ms
```

## Architecture Notes

### Mesh Generation Strategy

1. **Cylinder meshes** (rebars): Parametric surface generation with rotation matrices
2. **Box meshes** (concrete): 12-triangle mesh for solid rendering
3. **Stirrup tubes**: 4-segment rectangles with cylinder corners

### Caching Strategy

```python
@st.cache_data(ttl=3600)  # 1 hour cache
def create_beam_3d_figure(b, D, span, ...):
    # Geometry hash used for cache key
    cache_key = compute_geometry_hash(b, D, span, bottom_bars, ...)
```

### Performance Optimizations Applied

1. **Pre-computed trigonometry**: Sin/cos arrays cached in mesh generation
2. **Efficient mesh3d traces**: Single Plotly trace per component type
3. **Fragment isolation**: `@st.fragment` prevents full page rerenders
4. **Geometry hashing**: Fast cache key computation for change detection

## Scaling Considerations

| Beam Count | Estimated Time | Approach |
|------------|----------------|----------|
| 1 beam | <100ms | Real-time preview |
| 10 beams | ~1s | Acceptable for batch |
| 100 beams | ~10s | Background processing |
| 1000 beams | ~100s | Worker queue recommended |

## Future Optimizations (V1.1)

1. **WebGL instancing**: Render identical meshes with single draw call
2. **Level-of-detail (LOD)**: Reduce stirrup detail for zoomed-out views
3. **Progressive rendering**: Show concrete first, add rebars async
4. **GPU-side computation**: Transfer mesh math to shader (Three.js path)

## Related Documentation

- [8-week-development-plan.md](../planning/8-week-development-plan.md) - Project timeline
- [visualizations_3d.py](../../streamlit_app/components/visualizations_3d.py) - Source code
- [test_visualizations_3d.py](../../tests/test_visualizations_3d.py) - Test suite
