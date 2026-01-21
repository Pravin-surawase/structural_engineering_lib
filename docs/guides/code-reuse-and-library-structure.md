# Code Reuse and Library Structure

**Type:** Guide
**Audience:** Developers and AI Agents
**Status:** Active
**Created:** 2026-01-21

---

## Core Principle

**The library (`structural_lib`) is the single source of truth for all computation.**

Every calculation, validation, and data transformation MUST live in the library. UI (Streamlit, React) and AI tools are thin wrappers that call library functions.

---

## 1. Library Architecture

### 1.1 Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Streamlit UI   │  │    React UI     │  │  CLI Tools   │ │
│  └────────┬────────┘  └────────┬────────┘  └──────┬───────┘ │
└───────────┼─────────────────────┼─────────────────┼─────────┘
            │                     │                 │
            ▼                     ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                      INTERFACE LAYER                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   AI Tools      │  │   FastAPI       │  │  Python API  │ │
│  └────────┬────────┘  └────────┬────────┘  └──────┬───────┘ │
└───────────┼─────────────────────┼─────────────────┼─────────┘
            │                     │                 │
            ▼                     ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                     structural_lib (CORE)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │
│  │  api.py  │  │ flexure  │  │  shear   │  │  detailing  │  │
│  └──────────┘  └──────────┘  └──────────┘  └─────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │
│  │ adapters │  │ insights │  │  codes   │  │visualization│  │
│  └──────────┘  └──────────┘  └──────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Module Responsibilities

| Module | Responsibility | Examples |
| --- | --- | --- |
| `api.py` | Public entry points | `design_beam_is456()`, `check_beam_is456()` |
| `flexure.py` | Flexure calculations | `compute_xu()`, `compute_moment_capacity()` |
| `shear.py` | Shear calculations | `compute_vu()`, `compute_shear_capacity()` |
| `detailing.py` | Rebar placement | `detail_main_bars()`, `detail_stirrups()` |
| `adapters.py` | Data import/export | `ETABSAdapter`, `SAFEAdapter` |
| `insights/` | Smart analysis | `optimize_beam_cost()`, `suggest_improvements()` |
| `codes/is456/` | Code compliance | `check_clause_26_5_1()` |
| `visualization/` | Geometry generation | `beam_to_3d_geometry()` |

---

## 2. Code Reuse Matrix

### 2.1 What Can Be Reused

| Component | Reuse % | Notes |
| --- | --- | --- |
| Design calculations | 100% | Pure functions, no dependencies |
| IS 456 compliance checks | 100% | Pure functions |
| Adapters (ETABS, SAFE) | 100% | Framework-agnostic |
| Insights (optimization) | 100% | Pure functions |
| 3D geometry generation | 95% | Returns JSON, not meshes |
| AI tool definitions | 100% | JSON schema |
| AI tool handlers | 90% | Minor refactor for FastAPI |

### 2.2 What Needs Rewriting

| Component | Reason | Strategy |
| --- | --- | --- |
| Streamlit UI | Framework-specific | Rewrite in React |
| Plotly charts | Visualization library | Use Recharts/Visx |
| Session state | Streamlit-specific | Use Redux/Zustand |
| iframe 3D viewer | Embedding pattern | Use React Three Fiber |

---

## 3. Function Design Principles

### 3.1 Pure Functions

All library functions should be pure (no side effects):

```python
# GOOD - Pure function
def compute_xu(ast_mm2: float, b_mm: float, fck: float, fy: float) -> float:
    """Compute neutral axis depth."""
    return (0.87 * fy * ast_mm2) / (0.36 * fck * b_mm)

# BAD - Side effects
def compute_xu(ast_mm2: float, b_mm: float, fck: float, fy: float) -> float:
    xu = (0.87 * fy * ast_mm2) / (0.36 * fck * b_mm)
    print(f"xu = {xu}")  # NO! Side effect
    save_to_database(xu)  # NO! Side effect
    return xu
```

### 3.2 Dataclass Outputs

Always return structured data, never raw dicts:

```python
from dataclasses import dataclass, asdict
from typing import List

@dataclass
class FlexureResult:
    xu_mm: float
    mu_capacity_knm: float
    utilization: float
    status: str
    citations: List[str]

    def to_dict(self) -> dict:
        return asdict(self)

def compute_flexure(ast_mm2: float, ...) -> FlexureResult:
    # ... calculations
    return FlexureResult(
        xu_mm=xu,
        mu_capacity_knm=mu_cap,
        utilization=mu / mu_cap,
        status="safe" if mu < mu_cap else "unsafe",
        citations=["IS 456:2000 Cl 38.1"]
    )
```

### 3.3 Composable Functions

Design functions to be composable:

```python
# Small, focused functions
def compute_xu(ast, b, fck, fy) -> float: ...
def compute_lever_arm(d, xu) -> float: ...
def compute_moment_capacity(ast, d, xu, fy) -> float: ...

# Composed into higher-level functions
def check_flexure(ast, b, d, fck, fy, mu) -> FlexureResult:
    xu = compute_xu(ast, b, fck, fy)
    z = compute_lever_arm(d, xu)
    mu_cap = compute_moment_capacity(ast, d, xu, fy)
    return FlexureResult(...)
```

---

## 4. Preventing Duplication

### 4.1 Before Writing New Code

```bash
# Search for existing functionality
grep -r "keyword" Python/structural_lib/

# Search function names
grep -r "def compute" Python/structural_lib/

# Search class names
grep -r "class.*Result" Python/structural_lib/
```

### 4.2 Common Utilities

Create shared utilities for repeated patterns:

```python
# structural_lib/utils/validation.py
def validate_positive(value: float, name: str) -> None:
    if value <= 0:
        raise ValidationError(f"{name} must be positive, got {value}")

def validate_range(value: float, min_val: float, max_val: float, name: str) -> None:
    if not min_val <= value <= max_val:
        raise ValidationError(f"{name} must be between {min_val} and {max_val}, got {value}")

# Usage in multiple modules
from structural_lib.utils.validation import validate_positive

def design_beam(b_mm: float, D_mm: float, ...):
    validate_positive(b_mm, "b_mm")
    validate_positive(D_mm, "D_mm")
```

### 4.3 DRY Checklist

Before adding new code, verify:

- [ ] No existing function does this
- [ ] No similar pattern exists to follow
- [ ] Can't be implemented by composing existing functions
- [ ] Not already in a utility module

---

## 5. API Entry Points

### 5.1 Public API Design

The `api.py` file is the public interface. It should:

1. Import and compose lower-level functions
2. Provide clear, documented entry points
3. Handle all input validation
4. Return structured results

```python
# structural_lib/api.py

# Re-export public types
from structural_lib.types import (
    BeamDesignOutput,
    BeamDetailingResult,
    OptimizationResult,
)

# Public API functions
def design_beam_is456(
    mu_knm: float,
    vu_kn: float,
    b_mm: float,
    D_mm: float,
    fck: float = 25.0,
    fy: float = 500.0,
) -> BeamDesignOutput:
    """Design a beam per IS 456:2000.

    This is the main entry point for beam design. It handles:
    - Input validation
    - Flexure design
    - Shear design
    - Code compliance checks

    Args:
        mu_knm: Ultimate moment in kN-m.
        ...

    Returns:
        BeamDesignOutput with design results.
    """
    # Validate inputs
    validate_beam_inputs(b_mm, D_mm, fck, fy)

    # Compute
    flexure = compute_flexure(...)
    shear = compute_shear(...)

    # Check compliance
    compliance = check_is456_compliance(...)

    return BeamDesignOutput(
        flexure=flexure,
        shear=shear,
        compliance=compliance,
    )
```

### 5.2 API Versioning

For breaking changes, use versioned functions:

```python
# Current API
def design_beam_is456(mu_knm: float, ...) -> BeamDesignOutput:
    """Current implementation."""
    pass

# Deprecated (will be removed in v3.0)
def design_beam(mu_knm: float, ...) -> dict:
    """DEPRECATED: Use design_beam_is456 instead."""
    import warnings
    warnings.warn(
        "design_beam is deprecated, use design_beam_is456",
        DeprecationWarning,
        stacklevel=2
    )
    result = design_beam_is456(mu_knm, ...)
    return result.to_dict()
```

---

## 6. Adapter Pattern

### 6.1 Standard Adapter Interface

```python
# structural_lib/adapters/base.py
from abc import ABC, abstractmethod
import pandas as pd

class DataAdapter(ABC):
    """Base class for all data adapters."""

    @abstractmethod
    def read(self, file_path: str) -> pd.DataFrame:
        """Read data from file."""
        pass

    @abstractmethod
    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize to standard column names."""
        pass

    def import_data(self, file_path: str) -> pd.DataFrame:
        """Import and normalize data."""
        df = self.read(file_path)
        return self.normalize(df)
```

### 6.2 Concrete Adapters

```python
# structural_lib/adapters/etabs.py
class ETABSAdapter(DataAdapter):
    """Adapter for ETABS CSV exports."""

    def read(self, file_path: str) -> pd.DataFrame:
        return pd.read_csv(file_path)

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.rename(columns={
            "Beam": "beam_id",
            "P": "pu_kn",
            "V2": "vu_kn",
            "M3": "mu_knm",
        })

# structural_lib/adapters/safe.py
class SAFEAdapter(DataAdapter):
    """Adapter for SAFE CSV exports."""
    # ...
```

### 6.3 Factory Function

```python
# structural_lib/adapters/__init__.py
def get_adapter(format: str) -> DataAdapter:
    """Get appropriate adapter for file format."""
    adapters = {
        "etabs": ETABSAdapter,
        "safe": SAFEAdapter,
        "staad": STAADAdapter,
        "csv": GenericCSVAdapter,
    }
    if format not in adapters:
        raise ValueError(f"Unknown format: {format}")
    return adapters[format]()
```

---

## 7. Visualization Separation

### 7.1 Data vs Rendering

The library generates DATA for visualization, not rendered output:

```python
# structural_lib/visualization/geometry_3d.py

@dataclass
class RebarGeometry:
    """Rebar geometry for 3D rendering."""
    start: Tuple[float, float, float]
    end: Tuple[float, float, float]
    diameter_mm: float

@dataclass
class Beam3DGeometry:
    """Complete beam geometry for 3D rendering."""
    concrete_outline: List[Tuple[float, float, float]]
    main_bars: List[RebarGeometry]
    stirrups: List[List[Tuple[float, float, float]]]

def beam_to_3d_geometry(detailing: BeamDetailingResult) -> Beam3DGeometry:
    """Convert detailing result to 3D geometry data.

    This function generates coordinates, NOT rendered meshes.
    The UI layer (React/Three.js) handles actual rendering.
    """
    return Beam3DGeometry(
        concrete_outline=compute_concrete_outline(detailing),
        main_bars=compute_rebar_positions(detailing),
        stirrups=compute_stirrup_paths(detailing),
    )
```

### 7.2 Chart Data Generation

```python
# structural_lib/visualization/charts.py

@dataclass
class CrossSectionData:
    """Data for cross-section diagram."""
    concrete_outline: List[Tuple[float, float]]
    rebar_positions: List[Tuple[float, float, float]]  # x, y, diameter
    neutral_axis_y: float
    compression_zone: List[Tuple[float, float]]

def generate_cross_section_data(detailing: BeamDetailingResult) -> CrossSectionData:
    """Generate data for cross-section visualization.

    Returns coordinates and positions, NOT Plotly/chart objects.
    """
    return CrossSectionData(...)
```

---

## 8. Testing Reusable Code

### 8.1 Test Organization

```
tests/
├── unit/
│   └── structural_lib/
│       ├── test_flexure.py
│       ├── test_shear.py
│       ├── test_detailing.py
│       └── test_adapters.py
├── integration/
│   └── test_api.py
└── fixtures/
    └── sample_inputs.py
```

### 8.2 Testing Pure Functions

```python
# tests/unit/structural_lib/test_flexure.py
import pytest
from structural_lib.flexure import compute_xu

class TestComputeXu:
    def test_positive_result(self):
        xu = compute_xu(ast_mm2=1000, b_mm=300, fck=25, fy=500)
        assert xu > 0

    def test_increases_with_steel(self):
        xu1 = compute_xu(ast_mm2=500, b_mm=300, fck=25, fy=500)
        xu2 = compute_xu(ast_mm2=1000, b_mm=300, fck=25, fy=500)
        assert xu2 > xu1

    @pytest.mark.parametrize("ast,expected", [
        (500, 40.3),
        (1000, 80.6),
        (1500, 120.8),
    ])
    def test_known_values(self, ast, expected):
        xu = compute_xu(ast_mm2=ast, b_mm=300, fck=25, fy=500)
        assert xu == pytest.approx(expected, rel=0.01)
```

---

## 9. Dependency Management

### 9.1 Minimal Dependencies

The core library should have minimal dependencies:

```
# requirements-core.txt (structural_lib only)
numpy>=1.24.0
pandas>=2.0.0

# requirements-full.txt (includes UI)
-r requirements-core.txt
streamlit>=1.30.0
plotly>=5.18.0
```

### 9.2 Optional Dependencies

Use optional imports for non-core features:

```python
def export_to_dxf(detailing: BeamDetailingResult, file_path: str) -> None:
    """Export detailing to DXF format.

    Requires: pip install ezdxf
    """
    try:
        import ezdxf
    except ImportError:
        raise ImportError("DXF export requires ezdxf. Install with: pip install ezdxf")

    # ... export logic
```

---

## 10. Migration Strategy

### 10.1 From Streamlit to React

When migrating to React frontend:

1. **Keep library unchanged** - All computation stays in `structural_lib`
2. **Create FastAPI wrapper** - Expose library via REST API
3. **Build React components** - Call API, render results
4. **Reuse AI tool definitions** - JSON schema is framework-agnostic

### 10.2 API Wrapper Example

```python
# api_server/main.py
from fastapi import FastAPI
from structural_lib.api import design_beam_is456, detail_beam_is456

app = FastAPI()

@app.post("/api/design-beam")
def design_beam(request: BeamDesignRequest):
    result = design_beam_is456(**request.dict())
    return result.to_dict()

@app.post("/api/detail-beam")
def detail_beam(request: BeamDetailingRequest):
    result = detail_beam_is456(**request.dict())
    return result.to_dict()
```

---

## Quick Reference

### Directory Structure

```
Python/structural_lib/
├── api.py              # Public entry points
├── flexure.py          # Flexure calculations
├── shear.py            # Shear calculations
├── detailing.py        # Rebar detailing
├── adapters/           # Data import/export
│   ├── __init__.py
│   ├── base.py
│   ├── etabs.py
│   └── safe.py
├── insights/           # Smart analysis
│   ├── cost_optimization.py
│   └── smart_designer.py
├── codes/is456/        # IS 456 compliance
│   └── checks.py
├── visualization/      # Geometry generation
│   ├── geometry_3d.py
│   └── charts.py
├── types.py            # Shared dataclasses
├── exceptions.py       # Custom exceptions
└── utils/              # Shared utilities
    └── validation.py
```

### Search Commands

```bash
# Find function definition
grep -r "def function_name" Python/structural_lib/

# Find all usages
grep -r "function_name(" --include="*.py" .

# Find similar patterns
grep -r "pattern" Python/structural_lib/
```

### Reuse Checklist

- [ ] Searched existing code for similar functionality
- [ ] Checked if can compose from existing functions
- [ ] Placed code in correct module (library vs UI)
- [ ] Used existing validation utilities
- [ ] Followed existing patterns and conventions
- [ ] Added to public API if needed
