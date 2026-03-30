# Library Improvement Master Plan — v1.0

**Type:** Plan
**Audience:** All Agents
**Status:** Approved
**Importance:** Critical
**Created:** 2026-01-16
**Last Updated:** 2026-01-16
**Related Tasks:** AUTOMATION-PHASE0, LIB-IMPROVEMENT

---

## Executive Summary

This document outlines a systematic plan to upgrade the structural engineering library from a solid IS 456 beam design tool to a **professional-grade, multi-code platform** with world-class 3D visualization, testable UI, and daily feedback loops.

**Goals:**
1. Make the library the **best-in-class** RC design engine
2. Enable **daily testing** by engineers with visible UI
3. Create **professional documentation** and API design
4. Build toward the **automation platform vision**

---

## Current State Assessment

### Strengths (Keep & Enhance)
| Asset | Status | Value |
|-------|--------|-------|
| IS 456 Design Engine | Production-ready | 2430 tests, 86% coverage |
| API Surface | 65 public functions | Type-safe dataclasses |
| Cost Optimization | Working | Multi-objective Pareto |
| Detailing Module | Working | BBS, DXF export |
| 3D Geometry | POC ready | JSON contract defined |
| Streamlit UI | 5 pages | Basic but functional |
| ETABS Integration | Working | CSV import + batch |
| Audit Trail | Working | Deterministic hashes |

### Gaps (Must Fix)
| Gap | Impact | Priority |
|-----|--------|----------|
| 3D Viewer not production-ready | High | P0 |
| ACI 318 not implemented | High | P1 |
| EC2 not implemented | Medium | P2 |
| Flanged beams incomplete | High | P1 |
| Continuous beams missing | High | P1 |
| Column design missing | Medium | P2 |
| API naming inconsistent | Medium | P1 |
| Documentation fragmented | Medium | P1 |

---

## Phase 0: Foundation (Week 1-2)

### 0.1 SDK API Contract Definition

Define the clean, consistent API that will be the public face of the library.

```python
# Namespace structure
import structural_sdk as sk

# Core namespaces
sk.ui         # Input helpers (for Streamlit/UI)
sk.engine     # Design + verification + optimization
sk.viz        # Visualization (2D + 3D)
sk.io         # Import/export (CSV, JSON, DXF, BBS)
sk.codes      # Code-specific modules (is456, aci318, ec2)
sk.utils      # Utilities (validation, units, etc.)
```

#### `sk.engine` — Design Engine API

```python
# Single beam design
sk.engine.design_beam(
    beam: BeamInput,
    code: str = "IS456",
    include_detailing: bool = True
) -> DesignResult

# Verification only (no sizing)
sk.engine.verify_beam(
    beam: BeamInput,
    code: str = "IS456"
) -> VerificationResult

# Batch design
sk.engine.batch_design(
    beams: list[BeamInput],
    code: str = "IS456",
    parallel: bool = False
) -> list[DesignResult]

# Optimization
sk.engine.optimize_beam(
    constraints: OptimizationConstraints,
    objective: str = "cost",  # "cost", "weight", "carbon"
    code: str = "IS456"
) -> OptimizationResult

# Smart analysis (combined insights)
sk.engine.analyze_beam(
    beam: BeamInput,
    include_cost: bool = True,
    include_suggestions: bool = True,
    include_sensitivity: bool = False
) -> AnalysisResult
```

#### `sk.viz` — Visualization API

```python
# 3D geometry
sk.viz.beam_3d(result: DesignResult) -> Beam3DGeometry
sk.viz.to_threejs_json(geometry: Beam3DGeometry) -> str

# 2D diagrams
sk.viz.plot_bmd_sfd(loads: LoadsInput, span: float) -> PlotlyFigure
sk.viz.plot_section(result: DesignResult) -> PlotlyFigure
sk.viz.plot_rebar_layout(detailing: DetailingResult) -> PlotlyFigure

# Compliance visualization
sk.viz.compliance_panel(result: VerificationResult) -> dict
sk.viz.comparison_chart(results: list[DesignResult]) -> PlotlyFigure
```

#### `sk.io` — Input/Output API

```python
# Import
sk.io.read_csv(path: str, schema: str = "standard") -> list[BeamInput]
sk.io.read_etabs(path: str) -> list[BeamInput]
sk.io.read_excel(path: str, sheet: str = None) -> list[BeamInput]

# Export
sk.io.export_csv(results: list[DesignResult], path: str)
sk.io.export_json(results: list[DesignResult], path: str)
sk.io.export_dxf(detailing: DetailingResult, path: str)
sk.io.export_bbs(detailing: DetailingResult, path: str, format: str = "csv")
sk.io.export_report(result: DesignResult, path: str, format: str = "html")
```

#### `sk.codes` — Code-Specific Access

```python
# Direct code access (for advanced users)
sk.codes.is456.flexure.design(...)
sk.codes.is456.shear.design(...)
sk.codes.is456.detailing.compute(...)

# Code metadata
sk.codes.list_available()  # ["IS456", "ACI318", "EC2"]
sk.codes.get_info("IS456")  # {"name": "IS 456:2000", "version": "2000", ...}
```

### 0.2 Directory Restructure

```
Python/structural_lib/
├── __init__.py              # Re-exports sk.* namespace
├── engine/                  # Design engine (NEW)
│   ├── __init__.py
│   ├── design.py            # design_beam, batch_design
│   ├── verify.py            # verify_beam
│   ├── optimize.py          # optimize_beam
│   └── analyze.py           # analyze_beam (smart insights)
├── viz/                     # Visualization (NEW)
│   ├── __init__.py
│   ├── geometry_3d.py       # 3D geometry (existing, move)
│   ├── plots_2d.py          # Plotly 2D plots
│   └── renderers.py         # Three.js JSON, SVG, etc.
├── io/                      # Import/Export (NEW)
│   ├── __init__.py
│   ├── readers.py           # CSV, Excel, ETABS readers
│   ├── writers.py           # CSV, JSON, DXF writers
│   └── reports.py           # HTML/PDF report generation
├── codes/                   # Code implementations (existing)
│   ├── __init__.py
│   ├── is456/               # Complete
│   ├── aci318/              # To implement
│   └── ec2/                 # To implement
├── core/                    # Shared infrastructure (existing)
│   ├── __init__.py
│   ├── data_types.py        # All dataclasses
│   ├── inputs.py            # Input dataclasses
│   ├── validation.py        # Input validation
│   ├── errors.py            # Error types
│   └── units.py             # Unit handling
└── api.py                   # Legacy API (backward compat)
```

### 0.3 Backward Compatibility Strategy

```python
# api.py maintains all existing functions
# They become thin wrappers around new sk.* API

def design_beam_is456(...):
    """Legacy API - use sk.engine.design_beam() instead."""
    warnings.warn("Use sk.engine.design_beam()", DeprecationWarning)
    return sk.engine.design_beam(beam, code="IS456")
```

---

## Phase 1: 3D Visualization Production (Week 2-4)

### 1.1 Three.js Viewer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit App                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              st_components.html()                      │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │              Three.js Viewer                     │  │  │
│  │  │  ┌────────────┐  ┌─────────────┐  ┌──────────┐  │  │  │
│  │  │  │ BeamMesh   │  │ RebarMeshes │  │ Stirrups │  │  │  │
│  │  │  │ (concrete) │  │ (steel)     │  │ (loops)  │  │  │  │
│  │  │  └────────────┘  └─────────────┘  └──────────┘  │  │  │
│  │  │                                                  │  │  │
│  │  │  Controls: Orbit | Zoom | Pan | Explode         │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
              ↑
              │ JSON (Beam3DGeometry.to_dict())
              │
┌─────────────────────────────────────────────────────────────┐
│                  Python Backend                              │
│  sk.viz.beam_3d(result) → Beam3DGeometry                    │
│  sk.viz.to_threejs_json(geometry) → JSON string             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Three.js Component Features

| Feature | Priority | Status |
|---------|----------|--------|
| Beam concrete box rendering | P0 | POC done |
| Longitudinal bars (bottom) | P0 | POC done |
| Longitudinal bars (top) | P0 | POC done |
| Stirrup loops | P0 | POC done |
| Orbit/zoom/pan controls | P0 | POC done |
| Exploded view toggle | P1 | Planned |
| Color by utilization | P1 | Planned |
| Dimension annotations | P2 | Planned |
| Screenshot export | P2 | Planned |
| Multiple beams view | P2 | Planned |

### 1.3 Implementation Tasks

1. **Create standalone Three.js viewer** (`viewer.html`)
   - Import Three.js from CDN
   - Parse JSON geometry
   - Render beam + rebar + stirrups
   - Add OrbitControls

2. **Streamlit component wrapper** (`components/beam_viewer_3d.py`)
   - Use `st.components.v1.html()`
   - Pass geometry JSON via postMessage
   - Handle resize and responsive layout

3. **Production optimizations**
   - InstancedMesh for stirrups (performance)
   - Level-of-detail for large models
   - Loading states and error handling

### 1.4 3D Viewer Test Page (For Engineer Feedback)

```python
# streamlit_app/pages/05_3d_viewer.py

st.title("3D Beam Visualization")

# Input controls
col1, col2, col3 = st.columns(3)
with col1:
    b = st.slider("Width (mm)", 200, 500, 300)
    D = st.slider("Depth (mm)", 300, 800, 500)
with col2:
    span = st.slider("Span (mm)", 3000, 8000, 5000)
    mu = st.slider("Moment (kN·m)", 50, 500, 200)
with col3:
    fck = st.selectbox("Concrete", [20, 25, 30, 35, 40])
    fy = st.selectbox("Steel", [415, 500, 550])

# Design and render
if st.button("Design & Visualize"):
    beam = BeamInput(...)
    result = sk.engine.design_beam(beam)

    # Show 3D
    geometry = sk.viz.beam_3d(result)
    render_beam_3d(geometry)  # Three.js component

    # Show design summary
    st.json(result.to_dict())
```

---

## Phase 2: Multi-Code Support (Week 4-8)

### 2.1 Code Abstraction Layer

```python
# codes/base.py

class DesignCode(ABC):
    """Abstract base class for all design codes."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def version(self) -> str: ...

    @abstractmethod
    def design_flexure(
        self,
        mu_knm: float,
        b_mm: float,
        d_mm: float,
        fck: float,
        fy: float,
        **kwargs
    ) -> FlexureResult: ...

    @abstractmethod
    def design_shear(
        self,
        vu_kn: float,
        b_mm: float,
        d_mm: float,
        fck: float,
        pt: float,
        **kwargs
    ) -> ShearResult: ...

    @abstractmethod
    def compute_detailing(
        self,
        design_result: DesignResult,
        **kwargs
    ) -> DetailingResult: ...
```

### 2.2 IS 456 Refactoring

Refactor existing IS 456 code to implement `DesignCode` interface:

```python
# codes/is456/__init__.py

class IS456Code(DesignCode):
    name = "IS 456:2000"
    version = "2000"

    def design_flexure(self, mu_knm, b_mm, d_mm, fck, fy, **kwargs):
        from .flexure import design_singly_reinforced
        return design_singly_reinforced(mu_knm, b_mm, d_mm, fck, fy)

    def design_shear(self, vu_kn, b_mm, d_mm, fck, pt, **kwargs):
        from .shear import design_shear_reinforcement
        return design_shear_reinforcement(vu_kn, b_mm, d_mm, fck, pt)

    # ... etc
```

### 2.3 ACI 318 Implementation Plan

| Module | IS 456 Equivalent | Key Differences | Priority |
|--------|-------------------|-----------------|----------|
| flexure.py | flexure.py | Phi factors, strain limits | P1 |
| shear.py | shear.py | Vc formula, stirrup rules | P1 |
| detailing.py | detailing.py | Cover, spacing, Ld | P1 |
| tables.py | tables.py | Material properties | P1 |
| torsion.py | torsion.py | Different formulation | P2 |

### 2.4 EC2 Implementation Plan

| Module | Key Differences from IS 456 |
|--------|----------------------------|
| flexure.py | Parabolic-rectangular stress block |
| shear.py | Variable strut inclination method |
| detailing.py | Different cover and spacing rules |
| materials.py | Characteristic vs design values |

---

## Phase 3: UI for Daily Testing (Week 2-6)

### 3.1 Tester-Friendly UI Design

Create UI pages that engineers can use to:
1. Test each function independently
2. Compare results with hand calculations
3. Report issues with screenshots
4. Track what they've tested

### 3.2 UI Pages to Build

| Page | Purpose | Priority |
|------|---------|----------|
| **Single Beam Design** | Test one beam design | P0 (exists) |
| **Batch Design** | Test CSV import + batch | P0 |
| **3D Viewer** | Test 3D visualization | P0 |
| **Comparison Tool** | Compare 2 designs | P1 |
| **Function Tester** | Test individual API functions | P1 |
| **Report Generator** | Test report output | P1 |
| **Feedback Form** | Submit issues/feedback | P0 |

### 3.3 Feedback Collection System

```python
# streamlit_app/pages/99_feedback.py

st.title("Tester Feedback")

feedback_type = st.selectbox("Type", [
    "Bug Report",
    "Incorrect Result",
    "UI Issue",
    "Feature Request",
    "Other"
])

description = st.text_area("Description")
screenshot = st.file_uploader("Screenshot (optional)")

# Capture current session state for debugging
session_data = {
    "timestamp": datetime.now().isoformat(),
    "inputs": st.session_state.get("last_inputs"),
    "results": st.session_state.get("last_results"),
    "version": sk.get_version()
}

if st.button("Submit Feedback"):
    save_feedback(feedback_type, description, screenshot, session_data)
    st.success("Feedback submitted! Reference: FB-2026-01-001")
```

### 3.4 Daily Testing Workflow

```
Morning:
  1. Engineer opens Streamlit app
  2. Tests 3-5 beam designs
  3. Compares with their hand calculations or reference tool

During Day:
  4. Uses "Feedback" page to report any issues
  5. Screenshots automatically capture inputs + outputs

Evening (Developer):
  6. Review feedback submissions
  7. Prioritize fixes
  8. Deploy fixes overnight

Next Morning:
  9. Engineer tests fixes
  10. Cycle continues
```

---

## Phase 4: Documentation Upgrade (Week 3-6)

### 4.1 Documentation Structure

```
docs/
├── index.md                    # Landing page
├── getting-started/
│   ├── installation.md         # pip install, requirements
│   ├── quickstart.md           # 5-minute tutorial
│   └── concepts.md             # Key concepts explained
├── tutorials/
│   ├── single-beam-design.md   # Step-by-step guide
│   ├── batch-processing.md     # CSV import, batch design
│   ├── 3d-visualization.md     # Using the 3D viewer
│   ├── cost-optimization.md    # Finding optimal designs
│   └── etabs-integration.md    # ETABS workflow
├── api-reference/
│   ├── engine.md               # sk.engine.* functions
│   ├── viz.md                  # sk.viz.* functions
│   ├── io.md                   # sk.io.* functions
│   ├── codes/
│   │   ├── is456.md            # IS 456 specific
│   │   ├── aci318.md           # ACI 318 specific
│   │   └── ec2.md              # EC2 specific
│   └── data-types.md           # All dataclasses
├── examples/
│   ├── README.md               # Example index
│   └── [example notebooks]
├── technical/
│   ├── architecture.md         # System design
│   ├── code-structure.md       # Module organization
│   └── testing.md              # How we test
└── changelog.md                # Version history
```

### 4.2 API Documentation Standard

Every public function must have:

```python
def design_beam(
    beam: BeamInput,
    code: str = "IS456",
    include_detailing: bool = True
) -> DesignResult:
    """
    Design a reinforced concrete beam.

    This function performs complete beam design including flexure,
    shear, and optionally detailing checks per the specified code.

    Args:
        beam: Beam input specification containing geometry, materials,
              and loads. See BeamInput for required fields.
        code: Design code to use. Options: "IS456", "ACI318", "EC2".
              Default is "IS456".
        include_detailing: If True, compute bar arrangements and
                          stirrup layout. Default is True.

    Returns:
        DesignResult containing:
        - is_ok: Overall pass/fail status
        - flexure: Flexure check results
        - shear: Shear check results
        - detailing: Bar/stirrup arrangement (if include_detailing=True)
        - remarks: Human-readable summary

    Raises:
        ValidationError: If beam input fails validation
        CodeNotFoundError: If specified code is not available

    Example:
        >>> beam = BeamInput(
        ...     beam_id="B1",
        ...     geometry=BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000),
        ...     materials=MaterialsInput.M25_FE500(),
        ...     loads=LoadsInput(mu_knm=200, vu_kn=100)
        ... )
        >>> result = sk.engine.design_beam(beam)
        >>> print(result.is_ok)  # True or False
        >>> print(result.flexure.ast_required)  # Required steel area

    See Also:
        - verify_beam: For verification without sizing
        - batch_design: For multiple beams
        - optimize_beam: For finding optimal dimensions

    References:
        - IS 456:2000 Clause 38 (Flexure)
        - IS 456:2000 Clause 40 (Shear)
    """
```

### 4.3 Auto-Generated Reference

Use `sphinx` or `mkdocs` with autodoc to generate API reference from docstrings:

```yaml
# mkdocs.yml
plugins:
  - mkdocstrings:
      handlers:
        python:
          paths: [Python/structural_lib]
          options:
            show_source: true
            show_signature_annotations: true
```

---

## Phase 5: Testing Infrastructure (Ongoing)

### 5.1 Test Categories

| Category | Purpose | Tools |
|----------|---------|-------|
| Unit | Individual functions | pytest |
| Integration | End-to-end workflows | pytest |
| Property | Mathematical invariants | Hypothesis |
| Regression | Known-good results | pytest + fixtures |
| Performance | Speed benchmarks | pytest-benchmark |
| Visual | 3D rendering snapshots | Playwright |

### 5.2 New Test Requirements

For each new feature:
1. Unit tests for core logic
2. Integration test for API endpoint
3. Property test for mathematical invariants
4. Example in documentation

### 5.3 CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run tests
        run: pytest --cov=structural_lib
      - name: Upload coverage
        uses: codecov/codecov-action@v4

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run ruff
        run: ruff check Python/

  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build docs
        run: mkdocs build
      - name: Check links
        run: linkchecker site/
```

---

## Timeline Summary

| Week | Phase | Key Deliverables |
|------|-------|-----------------|
| 1 | Foundation | SDK API design document |
| 2 | Foundation + 3D | Directory restructure, 3D viewer v1 |
| 3 | 3D + UI | 3D production-ready, Feedback system |
| 4 | Multi-code | ACI 318 flexure + shear |
| 5 | Multi-code | ACI 318 detailing, EC2 start |
| 6 | Docs + Polish | Documentation complete |
| 7 | Testing | Full test coverage |
| 8 | Release | v0.18.0 with multi-code + 3D |

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Test coverage | 86% | 90% |
| API functions documented | ~50% | 100% |
| Design codes supported | 1 | 3 |
| 3D viewer status | POC | Production |
| UI pages for testing | 5 | 10 |
| Daily feedback items | 0 | 5-10 |

---

## Immediate Next Steps

1. **Today**: Create SDK API signature document
2. **Today**: Set up tester feedback form in Streamlit
3. **This week**: Complete 3D viewer production version
4. **This week**: Start ACI 318 flexure implementation

---

## Open Questions

1. Should we support multiple unit systems (SI vs Imperial)?
2. Do we need real-time collaboration features?
3. Should feedback go to GitHub Issues or separate system?
4. What's the minimum viable ACI 318 scope for first release?

---

*This plan is a living document. Update as we learn from tester feedback.*
