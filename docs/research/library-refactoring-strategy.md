# Library Refactoring Strategy: Framework-Agnostic Core

**Type:** Research
**Audience:** All Agents, Developers
**Status:** Complete
**Importance:** Critical
**Created:** 2026-01-22
**Last Updated:** 2026-01-23
**Related Tasks:** TASK-034, PR #398, PR #399, PR #400

---

## Implementation Progress

### ✅ Phase 1: Core Design Checks (COMPLETE - Session 34)
- **PR #398** - `beam_checks.py` module
- `BeamDesignCheckResult` dataclass with 18 fields
- `check_beam_design()` function with full IS 456 verification
- 21 comprehensive tests

### ✅ Phase 2: Optimization Functions (COMPLETE - Session 34)
- **PR #399** - `optimization.py` additions
- `ConstructabilityResult` and `RebarOptimizationResult` dataclasses
- `calculate_constructability_score()` for buildability scoring
- `suggest_optimal_rebar()` for IS 456 compliant optimization
- 18 comprehensive tests

### ✅ Phase 3: Material Takeoff (COMPLETE - Session 34)
- **PR #400** - `bbs.py` additions
- `BeamQuantity` and `MaterialTakeoffResult` dataclasses
- `calculate_material_takeoff()` for cost estimation
- 10 comprehensive tests

### ✅ Phase 4: Beam Line Optimization (COMPLETE - Session 35)
- Added to `optimization.py`:
  - `BeamLineInput` dataclass (beam_id, b_mm, D_mm, mu_knm, vu_kn)
  - `BeamConfig` dataclass (layer configuration)
  - `BeamLineOptimizationResult` dataclass
  - `optimize_beam_line()` function for construction consistency
- 16 comprehensive tests in `test_beam_line_optimization.py`

### ✅ Phase 5: Rebar Layout Consolidation (COMPLETE - Session 35)
- Added to `geometry_3d.py`:
  - `RebarLayoutResult` dataclass (bar positions, stirrups, summary)
  - `compute_rebar_layout()` unified function
- Exports added to `api.py`
- 15 comprehensive tests in `test_compute_rebar_layout.py`

### ✅ Phase 6: UI Integration (COMPLETE - Session 35)
- Updated `ai_workspace.py`:
  - Added library imports with fallback
  - `calculate_rebar_layout()` now uses `compute_rebar_layout` from library
  - `optimize_beam_line()` now uses `lib_optimize_beam_line` from library
  - Fallback to local implementation if library unavailable

---

## Executive Summary

This document outlines a strategic plan to refactor UI-embedded functions into `structural_lib` core, enabling:
1. **Reuse across frontends** (Streamlit → React/Next.js/Three.js)
2. **Better testability** (pure functions > UI-coupled code)
3. **API consistency** (following professional patterns from numpy/scipy)
4. **Quality control** (CI gates, type safety, coverage requirements)

**Core Principle:** The library should be usable by ANY frontend framework. All business logic, calculations, and data transformations belong in `structural_lib`, not in UI components.

---

## 1. Current State Analysis (Session 35 Research)

### 1.1 Comprehensive Function Audit

**ai_workspace.py (4790 lines)** - All functions categorized:

#### ✅ ALREADY EXTRACTED (PRs #398-400)
| Function | Lines | Target Module | Status |
|----------|-------|---------------|--------|
| `calculate_rebar_checks()` | 2275-2400 | `beam_checks.py` | PR #398 |
| `suggest_optimal_rebar()` | 2002-2162 | `optimization.py` | PR #399 |
| `calculate_constructability_score()` | 1928-2000 | `optimization.py` | PR #399 |
| `calculate_material_takeoff()` | 3297-3349 | `bbs.py` | PR #400 |

#### ✅ EXTRACTED IN SESSION 35 (Phases 4-6)
| Function | Target Module | Status |
|----------|---------------|--------|
| `optimize_beam_line()` | `optimization.py` | ✅ Complete - 16 tests |
| `calculate_rebar_layout()` | `geometry_3d.py` | ✅ Complete - 15 tests |
| UI Integration | `ai_workspace.py` | ✅ Uses library with fallback |

#### ⚠️ CONSOLIDATE (Use Existing Library)
| UI Function | Library Equivalent | Action |
|-------------|-------------------|--------|
| `auto_map_columns()` | `adapters.py` column detection | Refactor to use adapters |
| `standardize_dataframe()` | `adapters.GenericCSVAdapter` | Refactor to use adapters |
| `design_beam_row()` | `api.design_beam()` | Already uses API, just thin wrapper |

#### ❌ STAY IN UI (Framework-Specific)
| Function | Lines | Reason |
|----------|-------|--------|
| `create_building_3d_figure()` | 1609-1833 | Returns `plotly.go.Figure` (Plotly-specific) |
| `create_cross_section_figure()` | 2702-2898 | Returns `plotly.go.Figure` (Plotly-specific) |
| `render_*()` functions | various | Use `st.` (Streamlit-specific) |
| `init_workspace_state()` | 157-192 | Uses `st.session_state` |
| `_render_*()` functions | various | Pure UI rendering |

### 1.2 Library Module Status

| Module | Lines | Functions | Status |
|--------|-------|-----------|--------|
| `visualization/geometry_3d.py` | 1000+ | `compute_rebar_positions`, `compute_rebar_layout`, `beam_to_3d_geometry` | ✅ Complete |
| `optimization.py` | ~550 | `optimize_beam_cost`, `suggest_optimal_rebar`, `optimize_beam_line` | ✅ Complete |
| `bbs.py` | ~800 | `generate_bbs_from_detailing`, `calculate_material_takeoff` | ✅ Complete |
| `adapters.py` | ~900 | `ETABSAdapter`, `SAFEAdapter`, `STAADAdapter`, `GenericCSVAdapter` | ✅ Complete |
| `compliance.py` | 477 | `check_compliance_case`, `check_compliance_report` | ✅ Complete |
| `beam_checks.py` | ~200 | `check_beam_design` | ✅ PR #398 |

### 1.3 Decision Framework: What Belongs in the Library?

**✅ INCLUDE if ALL of:**
1. Pure computation (no UI state, no rendering)
2. IS 456 / SP 34 reference-able
3. Useful for non-Streamlit consumers (REST API, CLI, Excel)
4. Deterministic output for same inputs

**❌ EXCLUDE if ANY of:**
1. Uses `st.` / Streamlit session state
2. Returns Plotly/Matplotlib figures (framework-specific)
3. Only useful for one UI page
4. Has DataFrame as primary interface (UI convenience)

---

## 2. Refactoring Principles

### 2.1 The "Framework-Agnostic" Rule

**Library functions MUST:**
1. **NO UI imports** - Never import streamlit, plotly, matplotlib
2. **Pure data in/out** - Accept dicts/dataclasses, return dicts/dataclasses
3. **Explicit units** - All parameters documented with units (mm, kN, etc.)
4. **Type hints** - Full typing for IDE support and documentation
5. **Serializable output** - Results must be JSON-serializable for REST APIs

**Example - Good:**
```python
# structural_lib/compliance.py
def check_beam_design(
    b_mm: float,
    D_mm: float,
    mu_knm: float,
    vu_kn: float,
    fck: float,
    fy: float,
    cover_mm: float,
    bottom_bars: list[tuple[int, int]],  # [(dia_mm, count), ...]
    top_bars: list[tuple[int, int]],
    stirrup_dia_mm: int,
    stirrup_spacing_mm: int,
) -> BeamDesignCheckResult:
    """Perform full IS 456 compliance check.

    Returns:
        BeamDesignCheckResult with flexure_ok, shear_ok, spacing_ok, etc.
    """
```

**Example - Bad:**
```python
# ❌ UI coupling
def check_beam_design(row: pd.Series, st_session: dict) -> None:
    st.write(f"Beam {row['beam_id']}: {'PASS' if ok else 'FAIL'}")
```

### 2.2 API Design (Following NumPy/SciPy Patterns)

**Signature Convention:**
```python
func(subject, /, *params, **options) -> ResultObject
```

1. **Subject first** (the thing being operated on)
2. **Required params** (positional, obvious order)
3. **Optional params** (keyword-only, sensible defaults)
4. **Return rich objects** (not tuples)

**Result Objects Pattern:**
```python
@dataclass
class BeamDesignCheckResult:
    """Complete design verification results."""
    # Core results
    all_ok: bool
    status: str  # "✅ SAFE" or "❌ REVISE"

    # Flexure
    flexure_ok: bool
    flexure_util: float  # 0.0 to 1.0+
    mu_capacity_knm: float

    # Shear
    shear_ok: bool
    shear_util: float
    vu_capacity_kn: float

    # Spacing
    spacing_ok: bool
    bar_spacing_mm: float
    min_spacing_required_mm: float

    # Reinforcement limits
    min_reinf_ok: bool
    max_reinf_ok: bool
    ast_min_mm2: float
    ast_max_mm2: float
    ast_provided_mm2: float

    def to_dict(self) -> dict:
        """JSON-serializable dict for REST API responses."""
        return asdict(self)
```

---

## 3. Migration Plan

### Phase 1: Extract Core Functions (Week 1-2)

**Priority 1 - Design Checks:**
```
ai_workspace.calculate_rebar_checks() → structural_lib/compliance.py
```
- Create `BeamDesignCheckResult` dataclass
- Add comprehensive docstring with IS 456 references
- Add unit tests for edge cases (division by zero, etc.)

**Priority 2 - Optimization:**
```
ai_workspace.suggest_optimal_rebar() → structural_lib/optimization.py
ai_workspace.optimize_beam_line() → structural_lib/optimization.py
ai_workspace.calculate_constructability_score() → structural_lib/optimization.py
```
- Create `RebarOptimizationResult` dataclass
- Document the scoring algorithm

**Priority 3 - Geometry:**
```
ai_workspace.calculate_rebar_layout() → structural_lib/visualization/geometry_3d.py
```
- Already exists as `compute_rebar_positions`, consolidate

### Phase 2: Update UI to Use Library (Week 2-3)

1. Import functions from `structural_lib` instead of local definitions
2. Keep UI functions thin - just call library and render
3. Verify all tests still pass

### Phase 3: Add Missing Features (Week 3-4)

1. **Multi-beam geometry** - Building-level 3D coordinates
2. **Material takeoff** - Complete BBS generation
3. **Column mapping** - Smarter adapter logic

---

## 4. Quality Gates

### 4.1 CI Requirements for New Library Code

| Gate | Requirement |
|------|-------------|
| Type Coverage | 100% (all public functions typed) |
| Test Coverage | ≥85% branch coverage |
| Documentation | Docstrings with Examples section |
| No UI Imports | CI check for streamlit/plotly imports |
| JSON Serializable | All result types must have `to_dict()` |

### 4.2 Review Checklist

- [ ] No `st.` or `px.` or `plt.` imports
- [ ] All params have explicit units in docstring
- [ ] Return type is a dataclass, not dict/tuple
- [ ] Unit tests cover nominal, edge, and error cases
- [ ] IS 456 clause references in docstring
- [ ] Example usage in docstring

---

## 5. Framework Migration Path

### 5.1 Current: Streamlit (Python)

```
[Streamlit UI] → [structural_lib] → [Results]
     ↑                                  ↓
     └─────────── Render ───────────────┘
```

### 5.2 Future: React/Next.js (TypeScript + Python API)

```
[Next.js Frontend] ──HTTP──→ [FastAPI Backend] → [structural_lib]
       ↑                                              ↓
       └──────────── JSON Response ───────────────────┘
```

**Key Requirement:** `structural_lib` functions return JSON-serializable results that can be sent over HTTP.

### 5.3 Three.js 3D Visualization

**Current (Plotly):**
```python
# ai_workspace.py
fig = go.Figure()
fig.add_trace(go.Mesh3d(...))
st.plotly_chart(fig)
```

**Future (Three.js via REST):**
```python
# structural_lib/visualization/geometry_3d.py
def compute_beam_mesh(beam: BeamGeometry) -> Mesh3DData:
    """Compute 3D mesh vertices for Three.js consumption.

    Returns:
        Mesh3DData with vertices, faces, colors arrays
        compatible with THREE.BufferGeometry
    """
    return Mesh3DData(
        vertices=[...],  # Float32Array format
        faces=[...],     # Uint32Array format
        colors=[...],    # RGB arrays
    )
```

```typescript
// Frontend: React + Three.js
const meshData = await fetch('/api/beam-mesh/B11');
const geometry = new THREE.BufferGeometry();
geometry.setAttribute('position', new THREE.Float32BufferAttribute(meshData.vertices, 3));
```

---

## 6. Function-by-Function Migration Spec

### 6.1 `calculate_rebar_checks`

**Current Location:** `ai_workspace.py:2275-2400`

**Target Location:** `structural_lib/compliance.py`

**New Signature:**
```python
def check_beam_design(
    *,
    b_mm: float,
    D_mm: float,
    mu_knm: float,
    vu_kn: float,
    fck: float = 25.0,
    fy: float = 500.0,
    cover_mm: float = 40.0,
    bottom_bars: list[tuple[int, int]],
    top_bars: list[tuple[int, int]] | None = None,
    stirrup_dia_mm: int = 8,
    stirrup_spacing_mm: int = 150,
) -> BeamDesignCheckResult:
```

**Tests Required:**
- Nominal case (all checks pass)
- Flexure failure (under-reinforced)
- Shear failure (insufficient stirrups)
- Spacing failure (too many bars)
- Min reinforcement failure
- Max reinforcement failure
- Zero/negative input handling

### 6.2 `suggest_optimal_rebar`

**Current Location:** `ai_workspace.py:2002-2162`

**Target Location:** `structural_lib/optimization.py`

**New Signature:**
```python
def optimize_rebar_selection(
    *,
    b_mm: float,
    D_mm: float,
    mu_knm: float,
    vu_kn: float,
    fck: float = 25.0,
    fy: float = 500.0,
    cover_mm: float = 40.0,
    bar_diameters: list[int] | None = None,  # Default: [12, 16, 20, 25, 32]
    stirrup_diameters: list[int] | None = None,  # Default: [8, 10, 12]
    stirrup_spacings: list[int] | None = None,  # Default: [100, 125, ..., 300]
    optimize_for: str = "cost",  # "cost", "constructability", "balanced"
) -> RebarOptimizationResult:
```

### 6.3 `calculate_material_takeoff`

**Current Location:** `ai_workspace.py:3297-3349`

**Target Location:** `structural_lib/bbs.py`

**New Signature:**
```python
def calculate_takeoff(
    beams: list[BeamDesignResult],
    *,
    wastage_percent: float = 5.0,
    unit_price_steel: float = 65.0,  # INR/kg
    unit_price_concrete: float = 6500.0,  # INR/m³
) -> MaterialTakeoffResult:
```

---

## 7. Testing Strategy

### 7.1 Unit Tests (structural_lib/tests/)

```python
# test_compliance.py
def test_check_beam_design_nominal():
    """Verify pass case with standard beam."""
    result = check_beam_design(
        b_mm=300, D_mm=450, mu_knm=80, vu_kn=60,
        fck=25, fy=500, cover_mm=40,
        bottom_bars=[(16, 4)],
        top_bars=[(12, 2)],
        stirrup_dia_mm=8,
        stirrup_spacing_mm=150,
    )
    assert result.all_ok is True
    assert result.flexure_util < 1.0
    assert result.shear_util < 1.0

def test_check_beam_design_shear_failure():
    """Verify shear failure detection."""
    result = check_beam_design(
        b_mm=200, D_mm=300, mu_knm=50, vu_kn=150,  # High shear
        bottom_bars=[(16, 3)],
        stirrup_dia_mm=6,
        stirrup_spacing_mm=300,  # Inadequate
    )
    assert result.shear_ok is False
    assert result.shear_util > 1.0
```

### 7.2 Integration Tests (with UI)

After migration, verify Streamlit app still works:
```python
# tests/integration/test_ai_workspace_uses_lib.py
def test_table_editor_uses_lib_checks():
    """Verify table editor calls structural_lib.check_beam_design."""
    # Patch and verify call
```

---

## 8. Documentation Requirements

### 8.1 Docstring Template

```python
def function_name(params) -> ReturnType:
    """One-line summary.

    Detailed description with context.

    Args:
        param1: Description with units (mm).
        param2: Description with units (kN·m).

    Returns:
        Description of return value.

    Raises:
        ValueError: When input is invalid.

    Example:
        >>> result = function_name(param1=100, param2=50)
        >>> print(result.status)
        '✅ SAFE'

    References:
        - IS 456:2000, Cl 26.5.1.1 (Minimum reinforcement)
        - SP 34:1987, Section 3.2.1

    Notes:
        Additional implementation notes.
    """
```

### 8.2 API Reference Updates

Update `docs/reference/api.md` with:
- New function signatures
- Usage examples
- Link to IS 456 clauses

---

## 9. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing UI | Phased migration, keep old functions as wrappers initially |
| Missing edge cases | Comprehensive test suite before removing old code |
| Performance regression | Benchmark before/after for batch operations |
| Documentation drift | Generate API docs from docstrings |

---

## 10. Timeline (Updated)

| Phase | Status | Milestone |
|-------|--------|-----------|
| 1 | ✅ DONE | `check_beam_design()` → `beam_checks.py` (PR #398) |
| 2 | ✅ DONE | Optimization functions → `optimization.py` (PR #399) |
| 3 | ✅ DONE | Material takeoff → `bbs.py` (PR #400) |
| 4 | 🔄 TODO | `optimize_beam_line()` → `optimization.py` |
| 5 | 🔄 TODO | Consolidate rebar layout with `geometry_3d.py` |
| 6 | 🔄 TODO | Update UI to use library imports |

---

## 11. Success Criteria

1. ✅ **Phase 1-3 functions** moved to `structural_lib` (49 tests)
2. ✅ **85%+ test coverage** on new library code
3. ✅ **Zero UI imports** in library modules
4. ✅ **All result types** have `to_dict()` for JSON serialization
5. ⏳ **Streamlit app** still works identically (after UI integration)
6. ⏳ **Documentation** updated with new API signatures

---

## 12. Phase 4-6 Detailed Specifications

### Phase 4: Beam Line Optimization

**Function:** `optimize_beam_line()` (ai_workspace.py:2165-2272)

**Purpose:** Optimize all beams in a beam line together for construction consistency (uniform bar sizes across adjacent beams).

**Should Extract?** ✅ YES
- Pure algorithm, no UI dependencies
- Useful for REST API / CLI scenarios
- Deterministic output

**Target:** `structural_lib/optimization.py`

**New Signature:**
```python
@dataclass
class BeamLineOptimizationResult:
    """Result of beam line optimization."""
    beam_configs: dict[str, dict]  # beam_id -> rebar config
    unified_bar_dia: int  # Max bar dia used across line
    total_steel_kg: float
    constructability_score: float

    def to_dict(self) -> dict:
        return asdict(self)

def optimize_beam_line(
    beams: list[dict],  # [{beam_id, b_mm, D_mm, mu_knm, vu_kn}, ...]
    *,
    fck: float = 25.0,
    fy: float = 500.0,
    cover_mm: float = 40.0,
    unify_diameters: bool = True,
) -> BeamLineOptimizationResult:
    """Optimize multiple beams for construction consistency.

    Args:
        beams: List of beam dictionaries with design parameters
        fck: Concrete grade (N/mm²)
        fy: Steel grade (N/mm²)
        cover_mm: Cover to reinforcement (mm)
        unify_diameters: If True, use same bar diameter across all beams

    Returns:
        BeamLineOptimizationResult with unified configurations

    References:
        - SP 34:1987, Section on construction practicality
    """
```

### Phase 5: Rebar Layout Consolidation

**Problem:** `calculate_rebar_layout()` in ai_workspace.py duplicates functionality from `geometry_3d.compute_rebar_positions()`.

**Analysis:**
| Aspect | ai_workspace.py | geometry_3d.py |
|--------|----------------|----------------|
| Input | ast_mm2, dimensions | bar_count, bar_dia, dimensions |
| Output | dict with positions | list[Point3D] |
| Bar selection | Auto-selects from AST | Caller provides count/dia |
| Stirrups | Computes positions | Separate function |

**Decision:** ⚠️ PARTIAL CONSOLIDATION
- Keep `geometry_3d.compute_rebar_positions()` as the core
- Add helper function to select bar configuration from AST
- UI function becomes thin wrapper

**Target:** Add to `structural_lib/visualization/geometry_3d.py`:
```python
def select_bar_configuration(
    ast_mm2: float,
    available_diameters: list[int] | None = None,
    max_bars_per_layer: int = 6,
) -> tuple[int, int]:
    """Select optimal bar diameter and count for required steel area.

    Args:
        ast_mm2: Required steel area (mm²)
        available_diameters: Bar diameters to consider (default: [12,16,20,25,32])
        max_bars_per_layer: Maximum bars per layer

    Returns:
        (diameter_mm, count) tuple
    """
```

### Phase 6: UI Integration

**After PRs #398-400 merge:**

1. **Import library functions in ai_workspace.py:**
```python
from structural_lib.beam_checks import check_beam_design, BeamDesignCheckResult
from structural_lib.optimization import (
    calculate_constructability_score,
    suggest_optimal_rebar,
)
from structural_lib.bbs import calculate_material_takeoff
```

2. **Replace local function calls:**
```python
# Before:
checks = calculate_rebar_checks(b_mm, D_mm, ...)

# After:
result = check_beam_design(b_mm=b_mm, D_mm=D_mm, ...)
checks = result.to_dict()  # If dict needed for UI
```

3. **Remove deprecated local functions:**
- Delete `calculate_rebar_checks()` from ai_workspace.py
- Delete `suggest_optimal_rebar()` from ai_workspace.py
- Delete `calculate_constructability_score()` from ai_workspace.py
- Delete `calculate_material_takeoff()` from ai_workspace.py

4. **Test thoroughly:**
```bash
cd Python && pytest tests/ -v
.venv/bin/python scripts/check_streamlit_issues.py --all-pages
```

---

## Related Documents

- [professional-api-patterns.md](professional-api-patterns.md) - API design research
- [live-3d-visualization-architecture.md](live-3d-visualization-architecture.md) - 3D architecture
- [threejs-visualization-source-of-truth.md](threejs-visualization-source-of-truth.md) - Three.js planning

---

## Next Steps (Session 35+)

1. [x] ~~Create `BeamDesignCheckResult` dataclass~~ (PR #398)
2. [x] ~~Move `calculate_rebar_checks` with tests~~ (PR #398)
3. [x] ~~Add optimization functions~~ (PR #399)
4. [x] ~~Add material takeoff~~ (PR #400)
5. [ ] Wait for PRs to merge
6. [ ] Phase 4: Add `optimize_beam_line()` to library
7. [ ] Phase 5: Consolidate rebar layout
8. [ ] Phase 6: Update ai_workspace.py imports
