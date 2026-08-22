# Day 11: Services Layer — API, Adapters & Pipeline (Deep Dive)

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** Critical
**Created:** 2026-04-08
**Last Updated:** 2026-04-09
**Prerequisites:** Days 8-10 (architecture, type system, error handling)
**Library files:** `Python/structural_lib/services/api.py`, `Python/structural_lib/services/beam_api.py`, `Python/structural_lib/services/adapters.py`, `Python/structural_lib/services/beam_pipeline.py`
**Key scripts:** `scripts/discover_api_signatures.py`

---

## What You'll Learn Today

By the end of this module you'll understand:
- What the services layer does (and what it delegates)
- How `design_beam_is456()` orchestrates a full beam design — step by step
- Why `api.py` is a re-export hub (the "barrel" pattern)
- How `GenericCSVAdapter` maps 40+ messy column names from ETABS/SAP2000/manual CSVs
- How `beam_pipeline.py` runs multi-step batch designs with a canonical schema
- How to discover any API function's exact parameters without guessing
- The deprecated parameter resolution trick (`_resolve_deprecated_param`)
- **Things to know** — the stub trap, parameter naming conventions, batch vs single design
- **What can be done better** — adapter testing, pipeline error recovery, too many re-exports
- **Innovation** — async pipelines, streaming results, adapter auto-detection
- **Next repo must-add** — adapter registry, pipeline hooks, result caching

---

## Part 1: What the Services Layer Does

### 1.1 The Role

Remember the restaurant analogy from Day 8? Services is the waiter layer. Waiters don't cook food (that's `codes/`). They don't define what "medium rare" means (that's `core/`). They don't decorate the dining room (that's `react_app/`).

Waiters do three things:
1. **Take orders** — Accept inputs from the UI, validate them
2. **Relay to the kitchen** — Call the right `codes/` functions with the right parameters
3. **Bring back food** — Collect results, format them, return to the caller

```
┌───────────────────────────────────────────────────────────────────┐
│                    SERVICES LAYER RESPONSIBILITIES                  │
│                                                                    │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────────┐      │
│  │  VALIDATE    │───►│  ORCHESTRATE │───►│  FORMAT RESULTS   │      │
│  │             │    │             │    │                   │      │
│  │ • Units     │    │ • Flexure   │    │ • Frozen result   │      │
│  │ • Plausible │    │ • Shear     │    │ • Dict-compat     │      │
│  │ • Cross-fld │    │ • Detailing │    │ • Errors attached  │      │
│  └─────────────┘    └──────────────┘    └───────────────────┘      │
│                                                                    │
│  Also:                                                             │
│  • ADAPT external data (CSV/Excel → canonical parameters)          │
│  • PIPELINE batch designs (load → validate → design → report)      │
│  • DEPRECATION backward compat for old parameter names              │
└───────────────────────────────────────────────────────────────────┘
```

### 1.2 What Services DOES NOT Do

- **No IS 456 math** — `0.36 * fck * b * xu...` lives in `codes/`
- **No type definitions** — `FlexureResult`, `Severity` live in `core/`
- **No HTTP/JSON** — That's `fastapi_app/`
- **No React rendering** — That's `react_app/`

Services is ONLY orchestration — calling the right functions in the right order with validated inputs.

---

## Part 2: The `api.py` Re-Export Hub (Barrel Pattern)

### 2.1 Two Files Named `api.py` — The Trap

```
Python/structural_lib/
├── api.py                  ← ⚠️ STUB (backward compat) — NEVER EDIT
└── services/
    └── api.py              ← ✅ Real re-export hub
    └── beam_api.py         ← ✅ Actual beam functions
    └── column_api.py       ← ✅ Actual column functions
    └── common_api.py       ← ✅ Shared utilities
```

**The stub** (`Python/structural_lib/api.py`) exists only so old code `from structural_lib.api import design_beam_is456` still works. It just re-imports from the real location.

**The re-export hub** (`services/api.py`) collects all public functions from domain-specific modules:

```python
# services/api.py — the barrel file
from structural_lib.services.beam_api import (
    design_beam_is456,
    detail_beam_is456,
    optimize_beam_cost,
    # ... 20+ more beam functions
)
from structural_lib.services.column_api import (
    design_column_is456,
    classify_column_is456,
    # ... 12+ more column functions
)
from structural_lib.services.common_api import (
    get_library_version,
    validate_design_results,
    check_code,
)
```

### 2.2 Why the Barrel Pattern?

The public API grew to 37+ functions. All in one file = 3000+ lines. Unmanageable.

```
# BEFORE (one giant file):
services/api.py → 3000 lines, impossible to navigate

# AFTER (split + barrel):
services/beam_api.py    → ~800 lines (beam design, detailing, optimization)
services/column_api.py  → ~500 lines (column design, classification)
services/common_api.py  → ~200 lines (shared validation, versioning)
services/api.py         → ~50 lines (re-exports only)
```

Users import from the barrel: `from structural_lib.services.api import design_beam_is456`. They don't need to know the internal split.

This is the same as TypeScript's `index.ts` barrel: `export { useAuth } from './auth'`.

---

## Part 3: Anatomy of `design_beam_is456()`

### 3.1 The Function Signature

```python
# ACTUAL code from services/beam_api.py
def design_beam_is456(
    *,                      # ALL keyword-only — prevents positional mistakes
    units: str,             # "IS456" — validated at boundary
    b_mm: float,            # Beam width (mm)
    D_mm: float,            # Overall depth (mm)
    d_mm: float,            # Effective depth (mm)
    fck_nmm2: float,        # Concrete grade (N/mm²)
    fy_nmm2: float,         # Steel yield strength (N/mm²)
    mu_knm: float,          # Factored bending moment (kN·m)
    vu_kn: float,           # Factored shear force (kN)
    d_dash_mm: float | None = None,  # Compression steel depth (optional)
    ...
) -> ComplianceCaseResult:
```

**Critical design decisions:**

| Decision | Why |
|----------|-----|
| `*` (keyword-only) | Can't call `func(300, 500, ...)` — must name every arg |
| `_mm`, `_nmm2`, `_knm` suffixes | Units are visible in the parameter name |
| `d_dash_mm` optional with `None` | Doubly reinforced design only when needed |
| Returns `ComplianceCaseResult` | Frozen, dict-compatible, carries errors |

### 3.2 Internal Execution Flow

```python
# What happens inside design_beam_is456():

# STEP 1: Boundary validation
_require_is456_units(units)
# → Raises ConfigurationError if units != "IS456"

# STEP 2: Deprecated parameter resolution
b_mm = _resolve_deprecated_param(b_mm, kwargs.get("width"), "b_mm", "width")
# → Old code uses "width=300", new code uses "b_mm=300"
# → Both work, but deprecated param logs a FutureWarning

# STEP 3: Plausibility check
_validate_plausibility(fck_nmm2, fy_nmm2, b_mm, d_mm)
# → Catches unit confusion: fck=3600 probably means psi, not MPa

# STEP 4: Flexure design (delegates to codes/)
flexure_result = flexure.design_singly_reinforced(
    fck=fck_nmm2, fy=fy_nmm2, b_mm=b_mm, d_mm=d_mm, Mu_kNm=mu_knm
)

# STEP 5: Shear design (delegates to codes/)
shear_result = shear.design_shear(
    fck=fck_nmm2, fy=fy_nmm2, b_mm=b_mm, d_mm=d_mm,
    Vu_kN=vu_kn, Ast_mm2=flexure_result.Ast_required
)

# STEP 6: Assemble unified result
return ComplianceCaseResult(
    flexure=flexure_result,
    shear=shear_result,
    is_safe=flexure_result.is_safe and shear_result.is_safe,
    errors=[...],  # Collected from both steps
)
```

### 3.3 The Deprecated Parameter Trick

```python
# ACTUAL pattern from services/beam_api.py
def _resolve_deprecated_param(new_val, old_val, new_name, old_name):
    """Support old parameter names with deprecation warning."""
    if old_val is not None:
        if new_val is not None:
            raise ValueError(f"Cannot provide both '{new_name}' and '{old_name}'")
        import warnings
        warnings.warn(
            f"'{old_name}' is deprecated. Use '{new_name}' instead.",
            FutureWarning, stacklevel=3,
        )
        return old_val
    return new_val
```

This allows gradual migration:
```python
# Old code still works (with deprecation warning):
design_beam_is456(units="IS456", width=300, ...)
# FutureWarning: 'width' is deprecated. Use 'b_mm' instead.

# New code (no warning):
design_beam_is456(units="IS456", b_mm=300, ...)
```

### 3.4 The `build_detailing_input()` Helper

```python
# After design, services builds the input for detailing:
def build_detailing_input(design_result, beam_params):
    """Transform design output into detailing input format."""
    return {
        "b_mm": beam_params["b_mm"],
        "d_mm": beam_params["d_mm"],
        "Ast_required_mm2": design_result.flexure.Ast_required,
        "Asv_required_mm2": design_result.shear.Asv_required,
        "fck": beam_params["fck_nmm2"],
        "fy": beam_params["fy_nmm2"],
    }
```

Services transforms outputs from one step into inputs for the next — that's orchestration.

---

## Part 4: The Adapter Pattern — Taming Real-World Data

### 4.1 The Problem

In a perfect world, users send `{"b_mm": 300, "D_mm": 500, "fck_nmm2": 25}`. In reality, they import CSVs from ETABS, SAP2000, SAFE, STAAD Pro, or hand-made Excel templates. Each uses different column names.

The same beam width might be:

| Source | Column Name |
|--------|-------------|
| ETABS | `b (mm)` |
| Our canonical format | `b_mm` |
| Manual CSV | `Width`, `Width (mm)`, `width_mm` |
| Shorthand | `b`, `B` |
| British English | `Breadth` |

### 4.2 The Adapter ABC

```python
# ACTUAL library code — services/adapters.py
class InputAdapter(ABC):
    """Base class for all data adapters."""

    @abstractmethod
    def can_handle(self, source: str) -> bool:
        """Can this adapter process the given data source?"""
        ...

    @abstractmethod
    def load_geometry(self, source: str) -> list[BeamGeometry]:
        """Parse the source and return canonical beam geometry objects."""
        ...

    @abstractmethod
    def load_forces(self, source: str) -> list[BeamForces]:
        """Parse the source and return canonical force objects."""
        ...
```

### 4.3 GenericCSVAdapter — 40+ Column Mappings

```python
# ACTUAL library code — the column mapping dictionaries
class GenericCSVAdapter(InputAdapter):
    GEOMETRY_COLUMNS = {
        "width_mm": [
            "b (mm)", "b_mm", "b", "Width",
            "Width (mm)", "width_mm", "B", "Breadth",
        ],
        "depth_mm": [
            "D (mm)", "D_mm", "D", "Depth",
            "Depth (mm)", "depth_mm", "H", "Height",
        ],
        "fck_mpa": [
            "fck", "fck_nmm2", "Fck",
            "fck (N/mm2)", "Concrete Grade",
        ],
        # ... 40+ column mappings total
    }

    FORCES_COLUMNS = {
        "moment_knm": [
            "Mu", "Mu (kN-m)", "mu_knm", "Moment",
            "Factored Moment", "M_u", "Mu(kNm)",
        ],
        "shear_kn": [
            "Vu", "Vu (kN)", "vu_kn", "Shear",
            "Factored Shear", "V_u", "Vu(kN)",
        ],
    }
```

### 4.4 How Column Resolution Works

```
CSV Header: "Width", "Depth", "Mu (kN-m)", "Vu (kN)"
                │         │         │              │
                ▼         ▼         ▼              ▼
Mapping:    width_mm  depth_mm  moment_knm    shear_kn
                │         │         │              │
                ▼         ▼         ▼              ▼
Canonical:  b_mm=300  D_mm=500  mu_knm=150    vu_kn=100
```

The adapter iterates through each canonical field, checks if any of its aliases appear in the CSV headers, and maps the first match. If no alias matches, the field is reported as missing.

### 4.5 The Adapter Hierarchy

```
InputAdapter (ABC)
├── ETABSAdapter      — ETABS CSV (geometry, forces, properties files)
├── SAFEAdapter       — CSI SAFE floor design export
├── STAADAdapter      — Bentley STAAD Pro
├── GenericCSVAdapter — Manual CSVs, Excel exports, unknown formats
└── ManualInputAdapter — Programmatic input (no file parsing)
```

Each adapter implements `can_handle(source)` → bool. The system tries each adapter until one claims the file.

---

## Part 5: The Beam Pipeline — Batch Design

### 5.1 The Canonical Output Schema

```python
# ACTUAL code from services/beam_pipeline.py
SCHEMA_VERSION = 1

IS456_UNITS = {
    "length": "mm",
    "stress": "N/mm²",
    "force": "kN",
    "moment": "kN·m",
    "area": "mm²",
}

# Canonical dataclasses for pipeline stages:
@dataclass
class BeamGeometry:
    beam_id: str
    b_mm: float
    D_mm: float
    d_mm: float
    # ...

@dataclass
class BeamDesignOutput:
    """Full output for one beam in the pipeline."""
    beam_id: str
    geometry: BeamGeometry
    materials: BeamMaterials
    loads: BeamLoads
    flexure: FlexureOutput
    shear: ShearOutput
    serviceability: ServiceabilityOutput | None
    detailing: DetailingOutput | None
    errors: list[DesignError]
    schema_version: int = SCHEMA_VERSION
```

### 5.2 Pipeline Steps

```
Step 1: LOAD      ──► Read CSV via adapter → list[BeamGeometry]
Step 2: VALIDATE  ──► validate_units(), check all inputs
Step 3: DESIGN    ──► design_beam_is456() for each beam
Step 4: DETAIL    ──► detail_beam_is456() for each result (optional)
Step 5: OPTIMIZE  ──► Cost optimization (optional)
Step 6: REPORT    ──► Generate calculation reports
Step 7: VISUALIZE ──► Generate 3D geometry for React viewer
```

```python
# Pipeline units validation at the top:
def validate_units(units: str | None) -> str:
    """Validate units string at application boundary."""
    if units is None or units.strip() == "":
        raise UnitsValidationError(
            "units is required. Use 'IS456' for standard units."
        )
    normalized = units.strip().upper().replace(" ", "")
    if normalized not in _VALID_UNIT_NORMALIZED:
        raise UnitsValidationError(f"Invalid units '{units}'.")
    return "IS456"
```

Units validated once at the top → passed to every design call. No per-beam validation.

### 5.3 API Discovery — Never Guess Parameter Names

```bash
# The #1 mistake: guessing parameter names
# WRONG: width=300, grade=25, moment=150
# RIGHT: b_mm=300, fck_nmm2=25, mu_knm=150

# Always run this BEFORE calling any API function:
.venv/bin/python scripts/discover_api_signatures.py design_beam_is456
```

Output:
```
design_beam_is456(
    *, units: str, b_mm: float, D_mm: float, d_mm: float,
    fck_nmm2: float, fy_nmm2: float, mu_knm: float, vu_kn: float,
    d_dash_mm: float | None = None, ...
) -> ComplianceCaseResult
```

---

## Part 6: Exercises

### Exercise 1: API Discovery

```bash
# From workspace root:
.venv/bin/python scripts/discover_api_signatures.py design_beam_is456
.venv/bin/python scripts/discover_api_signatures.py detail_beam_is456
.venv/bin/python scripts/discover_api_signatures.py design_column_is456
```

### Exercise 2: Design a Beam

```python
from structural_lib.services.api import design_beam_is456

# Standard beam — note the keyword-only parameters
result = design_beam_is456(
    units="IS456",
    b_mm=300, D_mm=500, d_mm=450,
    fck_nmm2=25, fy_nmm2=500,
    mu_knm=150, vu_kn=100,
)
print(f"Safe: {result.flexure.is_safe}")
print(f"Ast: {result.flexure.Ast_required:.1f} mm²")
print(f"Section: {result.flexure.section_type}")

# Heavy beam — higher moment forces more steel
result2 = design_beam_is456(
    units="IS456",
    b_mm=300, D_mm=500, d_mm=450,
    fck_nmm2=25, fy_nmm2=500,
    mu_knm=300, vu_kn=200,
)
print(f"\nHeavy beam Ast: {result2.flexure.Ast_required:.1f} mm²")
```

### Exercise 3: Explore the Re-export Hub

```python
import structural_lib.services.api as api

public = [name for name in dir(api) if not name.startswith('_')]
print(f"Total public symbols: {len(public)}")

beam_funcs = [n for n in public if 'beam' in n.lower()]
column_funcs = [n for n in public if 'column' in n.lower()]
print(f"Beam functions: {len(beam_funcs)}")
print(f"Column functions: {len(column_funcs)}")

for name in sorted(beam_funcs):
    print(f"  - {name}")
```

---

## Part 7: Can You Explain? (Self-Check)

### Q1: Why barrel/re-export pattern instead of one big file?

<details><summary>Answer</summary>

37+ public functions all in one file = 3000+ lines. By splitting into `beam_api.py`, `column_api.py`, and `common_api.py`, each file is focused (~500-800 lines). The barrel (`services/api.py`) provides a single import point. Users write `from structural_lib.services.api import design_beam_is456` without knowing the internal split.
</details>

### Q2: Why 40+ column aliases in `GenericCSVAdapter`?

<details><summary>Answer</summary>

Real structural engineering data is messy. ETABS exports `b (mm)`, STAAD uses `Width`, manual CSVs use `B` or `Breadth`. Without mappings, every user would need to rename CSV columns to match our exact format. With 40+ aliases, the adapter handles most common formats automatically. Usability over purity.
</details>

### Q3: Why keyword-only arguments?

<details><summary>Answer</summary>

Safety. `design_beam_is456(300, 500, 450, 25, 500, 150, 100)` — is 300 the width or depth? A parameter swap produces valid but wrong results. With `b_mm=300, D_mm=500`, every value is unambiguous. The `*` in the signature enforces this — Python rejects positional calls.
</details>

### Q4: What's the stub warning?

<details><summary>Answer</summary>

Two files named `api.py`: the stub at `structural_lib/api.py` (backward compat, just re-imports) and the real hub at `services/api.py`. If you edit the stub, your changes do nothing. Never edit the stub. Always work in `services/`.
</details>

---

## Part 8: Things to Know (Critical Knowledge)

### 8.1 The `_extract_beam_params_from_schema()` Pattern

```python
# When FastAPI sends a Pydantic model, services extracts raw values:
def _extract_beam_params_from_schema(schema: BeamDesignRequest) -> dict:
    """Convert Pydantic model to raw kwargs for design_beam_is456."""
    return {
        "b_mm": schema.width,
        "D_mm": schema.depth,
        "d_mm": schema.effective_depth or (schema.depth - 50),
        "fck_nmm2": schema.fck,
        "fy_nmm2": schema.fy,
        "mu_knm": schema.moment,
        "vu_kn": schema.shear,
    }
```

This is the translation layer between FastAPI's Pydantic models (user-friendly names) and the library's IS 456 parameter names (canonical).

### 8.2 The `ComplianceCaseResult` Return Type

Every services function returns a frozen, dict-compatible result:

```python
result = design_beam_is456(...)

# Access as attributes:
result.flexure.Ast_required  # 876.5 mm²

# Convert to dict (for JSON serialization):
result_dict = result.to_dict()

# Check safety:
if not result.is_safe:
    for error in result.errors:
        print(f"[{error.severity}] {error.message}")
```

### 8.3 Batch Processing with Error Boundaries

```python
# Pipeline processes ALL beams, collecting per-beam errors:
results = []
for beam in beams:
    try:
        result = design_beam_is456(units="IS456", **beam.to_dict())
        results.append(result)
    except StructuralLibError as e:
        results.append(FailedBeamResult(beam_id=beam.beam_id, error=e))

# One failed beam doesn't stop the other 199
failed = [r for r in results if isinstance(r, FailedBeamResult)]
print(f"Designed: {len(results) - len(failed)}, Failed: {len(failed)}")
```

---

## Part 9: What Can Be Done Better

### 9.1 Current Issues

| Issue | Current State | Better Approach |
|-------|--------------|-----------------|
| **Adapter testing gaps** | GenericCSVAdapter has limited test coverage | Fuzzy header matching tests |
| **Pipeline error recovery** | One bad beam fails silently | Structured per-beam error reporting |
| **Too many re-exports** | 100+ symbols in `__all__` | Group by namespace (`api.beam.`, `api.column.`) |
| **No adapter auto-detection** | Manual format specification | Sniff file headers to choose adapter |
| **No result caching** | Same beam re-designed from scratch | Cache by input hash |

### 9.2 The Re-export Bloat Problem

```python
# Current: services/api.py exports 100+ symbols
# This makes IDE autocomplete noisy:
from structural_lib.services.api import ...  # 100+ options

# Better: namespace grouping
from structural_lib.services.api import beam   # beam.design(), beam.detail()
from structural_lib.services.api import column # column.design(), column.classify()
```

### 9.3 Missing Adapter Validation

```python
# Current: If GenericCSVAdapter can't match a column, it silently skips:
beams = adapter.load_geometry("weird.csv")
# → silently ignores unmapped columns, might produce incomplete data

# Better: Report unmapped columns explicitly:
result = adapter.load_geometry("weird.csv")
# → AdapterResult(beams=[...], unmapped_columns=["CustomWidth", "Strange_Col"])
```

---

## Part 10: Innovation Directions

### 10.1 Async Pipeline with Streaming Results

```python
# Current: Batch design blocks until all beams are done
results = pipeline.design_all(beams)  # Blocks for 30 seconds on 1000 beams

# Innovation: Stream results as they complete
async for result in pipeline.design_stream(beams):
    yield result  # Frontend updates in real-time
    # Progress: 1/1000, 2/1000, ...
```

The FastAPI backend already has `streaming.py` with `BatchJobManager` and SSE. The pipeline could feed directly into SSE streaming.

### 10.2 Adapter Auto-Detection

```python
# Current: User specifies adapter type
adapter = GenericCSVAdapter()
beams = adapter.load_geometry("file.csv")

# Innovation: Sniff headers and auto-select adapter
adapter = detect_adapter("file.csv")
# → Reads first row, matches against all adapter COLUMN dicts
# → Returns ETABSAdapter if "Story" and "IntPtDist" found
# → Returns GenericCSVAdapter otherwise
```

### 10.3 Result Caching by Input Hash

```python
# Current: Re-designing same beam = full recomputation
# After: Cache by input hash

import hashlib

def _input_hash(**kwargs) -> str:
    return hashlib.sha256(str(sorted(kwargs.items())).encode()).hexdigest()

_cache = {}

def design_beam_cached(**kwargs):
    h = _input_hash(**kwargs)
    if h in _cache:
        return _cache[h]
    result = design_beam_is456(**kwargs)
    _cache[h] = result
    return result
```

### 10.4 Innovation Comparison

| Feature | Current State | Innovation | Difficulty |
|---------|--------------|------------|------------|
| Batch pipeline | Synchronous, blocking | Async streaming | Medium |
| Adapter selection | Manual | Header auto-detection | Low |
| Result caching | None | Input hash cache | Low |
| Parameter validation | Per-call | Schema-level validation | Medium |
| Multi-code support | IS 456 only | Plugin adapters for ACI/EC2 | High |

---

## Part 11: Next Repo Must-Add

### 11.1 Adapter Registry

```python
# Instead of manual adapter selection, register all adapters:
class AdapterRegistry:
    _adapters: list[InputAdapter] = []

    @classmethod
    def register(cls, adapter_class):
        cls._adapters.append(adapter_class())
        return adapter_class

    @classmethod
    def detect(cls, source: str) -> InputAdapter:
        for adapter in cls._adapters:
            if adapter.can_handle(source):
                return adapter
        raise ValueError(f"No adapter found for: {source}")

@AdapterRegistry.register
class ETABSAdapter(InputAdapter):
    ...
```

### 11.2 Pipeline Hooks (Pre/Post)

```python
# Allow custom steps before/after each pipeline stage:
class PipelineHook(ABC):
    def before_design(self, beam: BeamGeometry) -> BeamGeometry: ...
    def after_design(self, result: BeamDesignOutput) -> BeamDesignOutput: ...

# Example: Log every design to database
class AuditHook(PipelineHook):
    def after_design(self, result):
        db.log_design(result)
        return result

pipeline = BeamPipeline(hooks=[AuditHook()])
```

### 11.3 Namespace-Based API Surface

```python
# Instead of flat 100+ exports:
# from structural_lib.api import design_beam_is456, detail_beam_is456, ...

# Use namespaces:
from structural_lib import beam, column

result = beam.design(units="IS456", b_mm=300, ...)
detail = beam.detail(result)
column_result = column.design(units="IS456", b_mm=400, ...)
```

### 11.4 Day-1 Checklist for Next Repo Services

- [ ] Adapter registry with auto-detection (no manual adapter selection)
- [ ] Pipeline hooks (pre/post for each stage)
- [ ] Namespace-based API (`beam.design()` instead of `design_beam_is456()`)
- [ ] Result caching by input hash (skip redundant recomputation)
- [ ] Async pipeline with streaming support
- [ ] Structured per-beam error reporting in batch mode
- [ ] Adapter unmapped-column warnings (not silent)
- [ ] Deprecation policy: max 2 versions before removal
- [ ] API versioning from day 1 (`v1.design_beam()`, `v2.design_beam()`)
- [ ] Schema migration support (SCHEMA_VERSION auto-upgrade)

---

## Part 12: Summary

| Concept | Purpose | Key File |
|---------|---------|----------|
| **Services layer** | Orchestrate, validate, adapt | `services/` |
| **`services/api.py`** | Barrel re-export (37+ functions) | `services/api.py` |
| **Stub `api.py`** | Backward compat — never edit | `structural_lib/api.py` |
| **`design_beam_is456()`** | Main entry: validate → flexure → shear → result | `services/beam_api.py` |
| **Keyword-only args** | Prevent positional parameter mistakes | All services functions |
| **`GenericCSVAdapter`** | Map 40+ column aliases to canonical | `services/adapters.py` |
| **`beam_pipeline.py`** | Multi-step batch design | `services/beam_pipeline.py` |
| **`_resolve_deprecated_param`** | Old parameter names still work | `services/beam_api.py` |
| **`discover_api_signatures.py`** | Never guess parameter names | `scripts/` |

---

## 📎 References

- **Re-export hub:** `Python/structural_lib/services/api.py`
- **Beam API:** `Python/structural_lib/services/beam_api.py`
- **Column API:** `Python/structural_lib/services/column_api.py`
- **Common API:** `Python/structural_lib/services/common_api.py`
- **Adapters:** `Python/structural_lib/services/adapters.py`
- **Pipeline:** `Python/structural_lib/services/beam_pipeline.py`
- **API discovery:** `scripts/discover_api_signatures.py`

---

## What's Next?

**Day 12: Testing & Quality** — Now that you understand all four layers (core, codes, services, UI) and the types that flow between them, we'll explore how we test all of it. Golden vector tests from SP:16, Hypothesis property-based testing, contract tests for API responses, the 85% branch coverage requirement, and the 6 test types every IS 456 function must have. Testing is where the architecture pays off — pure math functions are trivially testable.
