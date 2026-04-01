# Library Expansion Blueprint v5.0 — Multi-Code, Multi-Element

**Type:** Architecture
**Audience:** All Agents
**Status:** Active
**Importance:** Critical
**Created:** 2026-03-31
**Last Updated:** 2026-04-01
**Supersedes:** [library-expansion-blueprint-v4.md](../_archive/planning-completed-2026-03/library-expansion-blueprint-v4.md) (IS 456-only)

> Master plan for expanding structural_engineering_lib from single-code beam-only (IS 456) to multi-code (IS 456, ACI 318-19, EC2), multi-element (beam, column, slab, footing, wall, stair) with complete companion code support.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Decisions](#2-architecture-decisions)
3. [Current State](#3-current-state)
4. [Phase 0 — IS 456 Restructure](#4-phase-0--is-456-restructure)
5. [Phase 1 — IS 456 Multi-Element](#5-phase-1--is-456-multi-element)
6. [Phase 2 — Multi-Code Infrastructure](#6-phase-2--multi-code-infrastructure)
7. [Phase 3 — ACI 318-19](#7-phase-3--aci-318-19)
8. [Phase 4 — EC2 (EN 1992-1-1)](#8-phase-4--ec2-en-1992-1-1)
9. [Phase 5 — Fill the Matrix](#9-phase-5--fill-the-matrix)
10. [Risk Register](#10-risk-register)
11. [Testing Strategy](#11-testing-strategy)
12. [Documentation Plan](#12-documentation-plan)
13. [API Design](#13-api-design)
14. [Agent Coordination](#14-agent-coordination)
15. [Success Criteria](#15-success-criteria)
16. [Appendices](#16-appendices)

---

## 1. Executive Summary

### Goal
Transform structural_engineering_lib from a single-code beam design library (IS 456:2000) into a production-grade multi-code structural engineering library supporting 3 country standards and 8+ structural elements.

### Scope
| Dimension | Current | Target |
|-----------|---------|--------|
| Codes | IS 456:2000 only | IS 456 + ACI 318-19 + EC2 |
| Elements | Beam only | Beam, Column, Slab (one-way + two-way), Footing, Wall, Staircase, Deep Beam |
| Companion Codes | IS 13920 (beam only) | IS 875/1893/13920, ASCE 7, EN 1990/1991/1998 |
| Test Count | ~2270 | ~6000-8000 projected |
| Source Files | 133 | ~600 projected |

### Design Principles (Locked)
1. **Code-first nesting**: `codes/is456/beam/`, not `elements/beam/is456/`
2. **3 levels of common**: `core/` → `codes/common/` → `codes/is456/common/`
3. **SI units internally**: Imperial adapters at boundary for ACI only
4. **No shared formulas across codes**: Each code's math is self-contained
5. **Explicit `code=` parameter**: Thread-safe, no global state
6. **Backward compatibility**: Shims with deprecation warnings for 2 minor versions

---

## 2. Architecture Decisions

### 2.1 Code-First vs Element-First (DECIDED: Code-First)

**Why:** Structural design formulas are fundamentally different per code. IS 456 flexure (parabolic-rectangular stress block, 0.36·fck) has nothing in common with ACI flexure (Whitney block, 0.85·f'c·β1). Sharing code across standards is a maintenance trap.

**Evidence:** structuralcodes library uses code-first. concrete-properties uses `design_codes/` per code. Every major structural library follows this pattern.

### 2.2 Folder Structure (DECIDED)

```
Python/structural_lib/
├── core/                           # Layer 0: Code-agnostic
│   ├── base.py                     # DesignCode ABC, FlexureDesigner ABC, etc.
│   ├── registry.py                 # CodeRegistry (get/register/list)
│   ├── data_types.py               # DesignEnvelope, BaseResult
│   ├── units.py                    # Unit conversion at boundaries
│   ├── errors.py                   # Error code registry
│   ├── materials.py                # Material base classes
│   └── sections.py                 # Section geometry (code-agnostic)
│
├── codes/
│   ├── common/                     # Cross-code physics (starts empty)
│   │   └── __init__.py
│   │
│   ├── is456/                      # IS 456:2000
│   │   ├── __init__.py             # IS456Code class, re-exports
│   │   ├── common/                 # Within-code shared (constants, stress_blocks, validation, reinforcement)
│   │   ├── beam/                   # Beam-specific (flexure, shear, detailing, serviceability, torsion)
│   │   ├── column/                 # Column-specific (axial, interaction, slenderness)
│   │   ├── slab/                   # Slab-specific (one-way, two-way, flat slab)
│   │   ├── footing/                # Footing-specific (isolated, combined, punching)
│   │   ├── wall/                   # Wall-specific (Cl 32)
│   │   ├── staircase/              # Staircase (Cl 33)
│   │   ├── compliance.py           # Multi-element orchestrator
│   │   ├── tables.py               # Table 19, 20, 26, 28 data
│   │   ├── materials.py            # IS 456 material models
│   │   ├── traceability.py         # @clause() decorator
│   │   └── clauses.json            # Clause database (namespaced)
│   │
│   ├── is13920/                    # IS 13920:2016 (ductile detailing)
│   │   ├── __init__.py
│   │   ├── beam.py                 # Beam ductile detailing (migrated from is456/ductile.py)
│   │   ├── column.py               # Column ductile detailing
│   │   ├── joint.py                # Beam-column joint
│   │   └── wall.py                 # Shear wall detailing
│   │
│   ├── aci318/                     # ACI 318-19
│   │   ├── __init__.py             # ACI318Code class
│   │   ├── common/                 # ACI-specific shared (beta1, phi_factors, etc.)
│   │   ├── beam/                   # ACI beam design
│   │   ├── column/                 # ACI column design
│   │   └── ...
│   │
│   └── ec2/                        # EN 1992-1-1
│       ├── __init__.py             # EC2Code class
│       ├── common/                 # EC2-specific shared (national_annex, stress_blocks)
│       ├── beam/                   # EC2 beam design
│       ├── column/                 # EC2 column design
│       └── ...
│
├── services/                       # Layer 3: Orchestration
│   ├── api.py                      # Unified API: design_beam(code='is456', ...)
│   ├── adapters.py                 # CSV/Excel adapters (code-aware)
│   └── beam_pipeline.py            # Multi-step pipeline
│
└── visualization/                  # 3D geometry (code-aware detailing)
    └── geometry_3d.py
```

### 2.3 Safety Factor Philosophy (CRITICAL)

| Concept | IS 456 / EC2 | ACI 318 |
|---------|-------------|---------|
| Philosophy | Partial safety factors on **materials** | Strength reduction on **capacity** |
| Concrete | γc = 1.5 → fcd = 0.67·fck/1.5 | φ applied to total Mn |
| Steel | γs = 1.15 → fyd = fy/1.15 | φ applied to total Mn |
| Flexure | φ not used | φ = 0.90 (tension-controlled) |
| Shear | φ not used | φ = 0.75 |
| Column | φ not used | φ = 0.65–0.90 (transition) |

**Impact:** Cannot swap γ for φ. Each code's math functions must implement their own safety approach from scratch. The `DesignCode` ABC must NOT enforce a single safety model.

### 2.4 Stress Block Parameters (Per-Code, Not Parameterized)

| Parameter | IS 456 | ACI 318 | EC2 |
|-----------|--------|---------|-----|
| Block type | Parabolic-rectangular | Whitney rectangular | Parabolic-rectangular (or bilinear) |
| Stress factor | 0.36·fck | 0.85·f'c | αcc·fck/γc (αcc = 0.85 or 1.0 per NA) |
| Depth factor | 0.42·xu | β1·c (β1 = 0.85–0.65) | λ·x (λ = 0.8 for fck ≤ 50) |
| Concrete strain | εcu = 0.0035 (fixed) | εcu = 0.003 (fixed) | εcu2 = 0.0035 (≤C50), variable for HSC |
| Steel strain for balanced | Based on fy (Table xu_max/d) | εt = 0.005 for tension-controlled | εud = 0.9·εuk (ductility class) |

### 2.5 API Pattern (DECIDED: Hybrid)

```python
# PRIMARY: Unified router with code-specific input dataclass
result = design_beam(code='is456', input=IS456BeamInput(fck=25, fy=415, b_mm=300, ...))

# BACKWARD-COMPAT: Direct IS 456 call (frozen, never changes)
result = design_beam_is456(fck_nmm2=25, fy_nmm2=415, b_mm=300, ...)

# DIRECT: Code-specific module import
from structural_lib.codes.aci318.beam import flexure
result = flexure.required_steel_area(fc_prime_mpa=28, fy_mpa=420, ...)
```

### 2.6 Unit Strategy (DECIDED: Each Code in Native Units)

Each code module operates in its own native units internally:
- IS 456: mm, N/mm², kN, kNm
- ACI 318: mm, MPa internally (imperial adapter at boundary: in → mm, psi → MPa)
- EC2: mm, MPa, kN, kNm

**No Pint dependency.** Conversion is thin wrappers in `core/units.py`:
```python
def psi_to_mpa(psi: float) -> float: return psi * 0.006895
def inches_to_mm(inches: float) -> float: return inches * 25.4
```

### 2.7 Result Types (DECIDED: Common Envelope + Code Details)

```python
@dataclass(frozen=True)
class DesignEnvelope:
    """Code-agnostic result wrapper."""
    is_safe: bool
    utilization_ratio: float       # 0.0–1.0+
    governing_check: str           # "flexure", "shear", "deflection"
    code: str                      # "IS456", "ACI318", "EC2"
    element: str                   # "beam", "column", "slab"
    details: CodeSpecificDetails   # IS456FlexureDetail, ACI318FlexureDetail, etc.
    warnings: list[str]
    clause_refs: list[str]         # ["IS456:38.1", "IS456:40.2"]
```

---

## 3. Current State

### 3.1 IS 456 Implementation Status

| Module | IS 456 Clauses | Status | Lines | Functions |
|--------|---------------|--------|-------|-----------|
| flexure.py | Cl 38.1–38.4 | ✅ Done | 923 | 7 |
| shear.py | Cl 40.1–40.5 | ✅ Done | 373 | 4 |
| torsion.py | Cl 41.1–41.4 | ✅ Done | 533 | 6 |
| detailing.py | Cl 26.2–26.5 | ✅ Done | 1189 | 16 |
| serviceability.py | Cl 43.1–43.4 | ✅ Done | 1356 | 17 |
| ductile.py | IS 13920 Cl 6 | ✅ Done (beam only) | — | — |
| materials.py | Cl 6.2, 38.1 | ✅ Done | — | — |
| tables.py | Table 19, 20 | ✅ Done | — | — |
| slenderness.py | Cl 23.3 | ✅ Done (beam only) | — | — |
| load_analysis.py | Ch 22 | ✅ Done (SS & cantilever) | — | — |
| compliance.py | Orchestrator | ✅ Done | 476 | 10 |
| common/ | Shared math | ✅ Done | ~11,506 | — |

### 3.2 Infrastructure Status

| Component | Status | Notes |
|-----------|--------|-------|
| DesignCode ABC | ✅ Exists | code_id, code_name, code_version |
| FlexureDesigner ABC | ✅ Exists | required_steel_area() |
| ShearDesigner ABC | ✅ Exists | Not implemented by IS456Code |
| DetailingRules ABC | ✅ Exists | Not implemented by IS456Code |
| CodeRegistry | ✅ Exists | **Dead code** — never called in production |
| IS456Code class | ✅ Exists | Registered but doesn't implement ABCs |
| @clause() decorator | ✅ Exists | IS 456-only, no code namespace |
| clauses.json | ✅ Exists | IS 456 clauses, ~100 entries |
| Backward-compat shims | ✅ 46 exist | @deprecated decorator available in core/deprecation.py |
| @deprecated decorator | ✅ Done | In core/deprecation.py (TASK-614) |
| Code-specific input types | ❌ Missing | Only IS456 BeamInput exists |
| DesignEnvelope result | ❌ Missing | Two parallel result hierarchies |
| Unit conversion layer | ❌ Missing | No core/units.py |
| Code discovery API | ❌ Missing | No list_codes(), get_capabilities() |

### 3.3 NOT Implemented (IS 456)

| Element | Clauses | Priority |
|---------|---------|----------|
| Column | Cl 25, 39, Annex E/G | P1 🔄 — 7/10 functions done: classify ✅, min_ecc ✅, axial ✅, uniaxial ✅, biaxial ✅, P-M curve ✅, effective_length ✅ (254+ tests). Remaining: additional_moment, helical, column_detailing, ductile_detailing |
| One-way slab | Cl 24.1–24.2 | P1 |
| Two-way slab | Cl 24.3, Annex D, Table 26 | P1 |
| Footing | Cl 34, 31.6 | P1 |
| Wall | Cl 32 | P2 |
| Staircase | Cl 33 | P2 |
| Deep beam | Cl 29 | P2 |
| Flat slab | Cl 31.6 (punching) | P2 |
| Enhanced shear near supports | Cl 40.3 | ✅ Done (TASK-712) |
| Punching shear | Cl 31.6 | P1 |
| Moment redistribution | Annex C | P2 |
| Effective flange width (L-beam) | Cl 36.4.2 | P1 |
| Continuous beam coefficients | Annex B | P2 |

---

## 4. Phase 0 — IS 456 Restructure

**Goal:** Reorganize existing IS 456 beam code into nested folders without breaking anything.

### 4.1 Tasks

| # | Task | Files | Blocker? |
|---|------|-------|----------|
| 0.1 | Create `codes/is456/beam/` directory + `__init__.py` | New | No |
| 0.2 | Move `flexure.py` → `beam/flexure.py` | 1 file | No |
| 0.3 | Move `shear.py` → `beam/shear.py` | 1 file | No |
| 0.4 | Move `detailing.py` → `beam/detailing.py` | 1 file | No |
| 0.5 | Move `serviceability.py` → `beam/serviceability.py` | 1 file | No |
| 0.6 | Move `torsion.py` → `beam/torsion.py` | 1 file | No |
| 0.7 | Update `compliance.py` line 40: `from .beam import flexure, shear, serviceability` | 1 line | 🔴 BLOCKING |
| 0.8 | Update `codes/is456/__init__.py` to re-export from `beam/` | 1 file | No |
| 0.9 | Generate backward-compat shims at old locations | 5 files | No |
| 0.10 | Move `ductile.py` → `codes/is13920/beam.py` + shim | 2 files | No |
| 0.11 | Update 7 services files that import from `codes.is456` | 7 files | Uses shims |
| 0.12 | Update 10 test files importing from `codes.is456` | 10 files | Uses shims |
| 0.13 | Fix upward import in `detailing.py` line 152 (codes → visualization) | 1 line | 🔴 ARCHITECTURAL |
| 0.14 | Run full test suite — zero failures | — | Gate |
| 0.15 | Add `@deprecated` decorator infrastructure | 1 file | No |

### 4.2 Import Update Map

| File | Current Import | New Import |
|------|---------------|------------|
| `compliance.py` L40 | `from . import flexure, serviceability, shear` | `from .beam import flexure, serviceability, shear` |
| `services/api.py` L16 | `from structural_lib.codes.is456 import compliance, detailing, ductile, serviceability, slenderness` | No change (shim handles) |
| `services/rebar.py` L11 | `from structural_lib.codes.is456 import detailing` | No change (shim handles) |
| `services/excel_integration.py` L24 | `from structural_lib.codes.is456.detailing import (...)` | No change (shim handles) |
| `services/dxf_export.py` L60 | `from structural_lib.codes.is456.detailing import (...)` | No change (shim handles) |
| `services/bbs.py` L25 | `from structural_lib.codes.is456.detailing import BeamDetailingResult` | No change (shim handles) |
| `services/rebar_optimizer.py` L25 | `from structural_lib.codes.is456.detailing import (...)` | No change (shim handles) |
| `services/job_runner.py` L26 | `from structural_lib.codes.is456 import compliance` | No change (stays at top level) |
| `services/report.py` L41 | `from structural_lib.codes.is456 import ductile` | Update to `from structural_lib.codes.is13920 import ductile` |

### 4.3 Backward Compatibility Shim Pattern

```python
# codes/is456/flexure.py (after content moves to beam/flexure.py)
"""DEPRECATED: Import from structural_lib.codes.is456.beam.flexure instead."""
import warnings
from structural_lib.codes.is456.beam.flexure import *  # noqa: F401, F403
warnings.warn(
    "Importing from 'structural_lib.codes.is456.flexure' is deprecated. "
    "Use 'structural_lib.codes.is456.beam.flexure'. Removal in v1.0.0.",
    DeprecationWarning, stacklevel=2,
)
```

### 4.4 Success Criteria
- [x] All 3401 tests pass (originally 2270+)
- [x] `from structural_lib.codes.is456 import flexure` still works (via shim)
- [x] `from structural_lib.codes.is456.beam import flexure` is the new canonical path
- [x] No circular imports
- [x] `validate_imports.py` passes
- [x] `check_architecture_boundaries.py` passes

---

## 5. Phase 1 — IS 456 Multi-Element

**Goal:** Add column, slab, and footing design under IS 456 BEFORE adding new codes.

**Why before multi-code:** The abstraction layer (ABCs, result types) must handle multiple elements before it handles multiple codes. Otherwise the API is designed beam-only, then breaks for columns.

### 5.1 Column Design (IS 456 Cl 25, 39, Annex E/G)

**10 functions in incremental complexity order:**

| # | Function | IS 456 Reference | Complexity | Status |
|---|----------|-----------------|------------|--------|
| 1 | `classify_column()` | Cl 25.1.2 | ✅ Done | ✅ |
| 2 | `min_eccentricity()` | Cl 25.4 | ✅ Done | ✅ |
| 3 | `short_axial_capacity()` | Cl 39.3 | ✅ Done | ✅ |
| 4 | `helical_capacity()` | Cl 39.4 | Low | 📋 TASK-639 |
| 5 | `design_short_column_uniaxial()` | Cl 39.5, Annex G | ✅ Done | ✅ |
| 6 | `biaxial_bending_check()` | Cl 39.6 (Bresler) | ✅ Done | ✅ |
| 7 | `slender_additional_moment()` | Cl 39.7 | Medium | 📋 TASK-637 |
| 8 | `pm_interaction_curve()` | Cl 39.5, SP:16 Table I | ✅ Done | ✅ |
| 9 | `column_detailing()` | Cl 26.5.3 | Medium | 📋 |
| 10 | `column_ductile_detailing()` | IS 13920 Cl 7 | Medium | 📋 |
| 11 | `effective_length()` | Cl 25.2, Table 28 | ✅ Done | ✅ |

**Quality Gate:** Each function goes through the 9-step function quality pipeline. SP:16 benchmarks required ±0.1%.

**Edge Cases to Handle:**
- Pu = 0 (pure bending → treat as beam)
- Pu > Puz (section inadequate → error, not garbage)
- Biaxial with zero moment on one axis (reduce to uniaxial)
- d'/d > threshold where compression steel doesn't yield
- Non-standard column shapes (L, C, hollow) — Phase 5 only

### 5.2 One-Way Slab Design (IS 456 Cl 24.1–24.2)

| # | Function | IS 456 Reference |
|---|----------|-----------------|
| 1 | `classify_slab()` | ly/lx ratio check |
| 2 | `oneway_coefficients()` | Table 12/13 |
| 3 | `design_oneway_slab()` | Cl 24.1–24.2 |
| 4 | `slab_detailing()` | Cl 26.5 (min steel, max spacing) |

### 5.3 Two-Way Slab Design (IS 456 Cl 24.3, Annex D)

| # | Function | IS 456 Reference |
|---|----------|-----------------|
| 1 | `twoway_moment_coefficients()` | Table 26 (9 cases × αx, αy) |
| 2 | `twoway_shear_coefficients()` | Table 27 |
| 3 | `design_twoway_slab()` | Annex D-1 |
| 4 | `torsion_reinforcement()` | Annex D-1.7/D-1.8 |
| 5 | `strip_distribution()` | Annex D-1.2 (middle/edge strips) |

**Edge Case:** ly/lx exactly = 2.0 — IS 456 says "may be designed as one-way" — library should default to two-way and document the choice.

### 5.4 Footing Design (IS 456 Cl 34)

| # | Function | IS 456 Reference |
|---|----------|-----------------|
| 1 | `size_footing()` | Cl 34.1 (bearing capacity) |
| 2 | `footing_flexure()` | Cl 34.2.1–34.2.3 |
| 3 | `footing_oneway_shear()` | Cl 34.2.4 (at d from face) |
| 4 | `footing_punching_shear()` | Cl 31.6 (at d/2 from face) |
| 5 | `footing_detailing()` | Cl 34.3 (rebar distribution) |
| 6 | `bearing_check()` | Cl 34.4 (σbr ≤ 0.45·fck·√(A1/A2)) |

**Edge Cases:**
- Eccentric loading → trapezoidal/triangular pressure
- Biaxial eccentricity → kern boundary check (ex/Lx + ey/Ly ≤ 1/6)

### 5.5 Missing Beam Provisions (Fix Before Phase 2)

| # | Task | IS 456 Reference | Priority |
|---|------|-----------------|----------|
| 1 | Enhanced shear near supports | Cl 40.3 (τc' = τc·2d/av) | ✅ Done (TASK-712) |
| 2 | Punching shear (shared with slab/footing) | Cl 31.6 | HIGH |
| 3 | Effective flange width for L-beams | Cl 36.4.2 variant | MEDIUM |
| 4 | Deep beam lever arm | Cl 29 | MEDIUM |
| 5 | Moment redistribution | Annex C (≤30%) | LOW |

### 5.6 New ABCs Required

```python
# core/base.py additions
class ColumnDesigner(ABC):
    @abstractmethod
    def axial_capacity(self, ...) -> DesignResult: ...
    @abstractmethod
    def interaction_diagram(self, ...) -> list[tuple[float, float]]: ...

class SlabDesigner(ABC):
    @abstractmethod
    def design_one_way(self, ...) -> DesignResult: ...
    @abstractmethod
    def design_two_way(self, ...) -> DesignResult: ...

class FootingDesigner(ABC):
    @abstractmethod
    def size_footing(self, ...) -> DesignResult: ...
    @abstractmethod
    def punching_shear(self, ...) -> DesignResult: ...

class ConcreteStressBlock(ABC):
    @abstractmethod
    def stress_block_factor(self, fck: float) -> float: ...
    @abstractmethod
    def lever_arm_factor(self, fck: float) -> float: ...

class LoadCombination(ABC):
    @abstractmethod
    def get_combinations(self, load_types: list[str]) -> list[dict]: ...
```

### 5.7 Phase 1 Success Criteria
- [x] IS 456 column design: 7/10 functions done (classify, min_ecc, axial, uniaxial, biaxial, P-M curve, effective_length). 254+ column tests, SP:16 benchmarks passing ±0.1%. Remaining: additional_moment, helical, detailing
- [ ] IS 456 one-way slab: 4 functions
- [ ] IS 456 two-way slab: 5 functions with all 9 Table 26 cases
- [ ] IS 456 footing: 6 functions including punching shear
- [x] Enhanced shear (Cl 40.3) implemented
- [ ] New ABCs added to core/base.py
- [ ] IS456Code implements all ABCs
- [ ] All tests pass (including new ~500 tests)

---

## 6. Phase 2 — Multi-Code Infrastructure

**Goal:** Build the infrastructure that makes adding new codes mechanical, not architectural.

### 6.1 Tasks

| # | Task | Description |
|---|------|-------------|
| 2.1 | Activate CodeRegistry | Make `services/api.py` actually use `CodeRegistry.get()` for dispatch |
| 2.2 | IS456Code implements ABCs | `FlexureDesigner`, `ShearDesigner`, `DetailingRules`, `ColumnDesigner`, etc. |
| 2.3 | Create code-specific input dataclasses | `IS456BeamInput`, `ACI318BeamInput`, `EC2BeamInput` |
| 2.4 | Create `DesignEnvelope` result type | Unify `FlexureResult` + `ShearResult` under common wrapper |
| 2.5 | Resolve dual result hierarchy | `core.base.DesignResult` vs `core.data_types.FlexureResult` — inherit or merge |
| 2.6 | Create `core/units.py` | psi↔MPa, in↔mm, kip↔kN, ft-kip↔kNm |
| 2.7 | Namespace `clauses.json` | Add `code` field: `"IS456:38.1"`, `"ACI318:22.2.2.4.1"` |
| 2.8 | Namespace `@clause()` decorator | `@clause("ACI318:22.2.2.4.1")` |
| 2.9 | Create code discovery API | `list_codes()`, `list_elements(code)`, `get_code_info(code)` |
| 2.10 | Feature flags for experimental codes | `EXPERIMENTAL_CODES = {"ACI318": False, "EC2": False}` |
| 2.11 | `@deprecated` decorator | Warning system for shim deprecation cycle |
| 2.12 | API versioning for FastAPI | `/api/v2/{code}/design/beam` alongside `/api/v1/design/beam` |
| 2.13 | Fix `api_manifest.json` for multi-code | Add `code` field per entry |
| 2.14 | Lazy loading for code modules | `__getattr__` in `__init__.py` — load ACI only when accessed |
| 2.15 | Plausibility guards | fck > 100 for IS 456 → "Did you mean ACI psi?" |

### 6.2 Safety Factor Abstraction

**DO NOT** create a generic `apply_safety_factor()`. Instead:
- IS 456 / EC2: Material safety factors applied inside each function
- ACI 318: φ factor applied to the final capacity result
- The `DesignEnvelope` reports utilization_ratio which abstracts over both philosophies

### 6.3 The @deprecated Decorator

```python
# core/deprecation.py
import warnings, functools

def deprecated(since: str, remove_in: str, replacement: str = ""):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            msg = f"{func.__qualname__} is deprecated since v{since}, will be removed in v{remove_in}."
            if replacement: msg += f" Use {replacement} instead."
            warnings.warn(msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### 6.4 Phase 2 Success Criteria
- [ ] `CodeRegistry.get("IS456")` returns functional IS456Code
- [ ] `CodeRegistry.list_codes()` returns `["IS456"]`
- [ ] `design_beam(code='is456', input=IS456BeamInput(...))` works
- [ ] `design_beam_is456(...)` still works (backward compat)
- [ ] All shims have `@deprecated` warnings
- [ ] `clauses.json` has code namespace
- [ ] Feature flags block access to incomplete codes

---

## 7. Phase 3 — ACI 318-19

**Goal:** First non-IS 456 code. Validates the entire multi-code pattern.

### 7.1 Start with Beam Flexure + Shear Only

Smallest scope to validate pattern. If the architecture works for ACI beam, it works for everything.

### 7.2 Fundamental Differences That Affect Implementation

| Concern | IS 456 Approach | ACI 318 Approach | Impact |
|---------|----------------|------------------|--------|
| Concrete strength | fck (cube, N/mm²) | f'c (cylinder, MPa) | Input validation, conversion |
| Stress block | 0.36·fck, 0.42·xu | 0.85·f'c, β1·c | Completely different math |
| Safety | γc=1.5, γs=1.15 | φ=0.90 flexure, 0.75 shear | Different function structure |
| Min steel | As,min = 0.85·bd/fy | As,min = max(0.25√f'c·bw·d/fy, 1.4·bw·d/fy) | Different formula |
| Balanced condition | xu_max/d from table | εt ≥ 0.005 for tension-controlled | Different concept |
| Torsion | Equivalent shear/moment | Thin-walled tube analogy (Aoh) | Completely different procedure |
| Dev length | Ld = φ·σs/(4·τbd) | Complex formula with factors | Different formula |
| Shear | τv vs τc from Table 19 | Vc = 0.17·λ·√f'c·bw·d | No table lookup |

### 7.3 ACI 318 Beam Functions

| # | Function | ACI 318 Reference |
|---|----------|------------------|
| 1 | `required_steel_area()` | Ch.22 (Whitney block) |
| 2 | `check_tension_controlled()` | §21.2.2 (εt ≥ 0.005) |
| 3 | `phi_factor()` | Table 21.2.2 (transition zone) |
| 4 | `shear_capacity()` | §22.5 (Vc + Vs) |
| 5 | `minimum_reinforcement()` | §9.6.1.2 |
| 6 | `development_length()` | Ch.25 |
| 7 | `design_beam_aci318()` | Full beam design |

### 7.4 Benchmark Sources

| Source | Purpose | Tolerance |
|--------|---------|-----------|
| PCA Notes on ACI 318 (12th Ed.) | Primary benchmark | ±0.1% |
| Wight & MacGregor (7th Ed.) | Secondary benchmark | ±1% (textbook rounding) |
| ACI SP-17 Design Handbook | Design aids validation | ±0.5% |

### 7.5 Implementation Risks

1. **Cylinder vs. cube strength confusion** — fck = 25 (IS 456 cube) ≈ f'c = 20 (ACI cylinder). A user entering 25 for ACI gets wrong results. Plausibility guard needed.
2. **φ factor transition zone** — Between εt = 0.002 and 0.005, φ interpolates linearly. Small errors in strain cascade into wrong φ.
3. **β1 for high-strength concrete** — β1 = 0.85–0.65 depending on f'c. Must handle all grades correctly.
4. **Shear design without Table 19** — ACI is purely formula-based. Different code flow from IS 456.
5. **Strut-and-tie model** (ACI Ch.23) — Required for deep beams, corbels. No IS 456 equivalent. Phase 5.

### 7.6 Phase 3 Success Criteria
- [ ] `CodeRegistry.get("ACI318")` returns ACI318Code
- [ ] ACI beam flexure matches PCA Notes ±0.1%
- [ ] ACI beam shear matches PCA Notes ±0.1%
- [ ] `design_beam(code='aci318', input=ACI318BeamInput(...))` works
- [ ] Cross-code test: same beam (300×500, Mu=150kNm) gives different but physically consistent Ast under IS 456 vs ACI
- [ ] FastAPI route `/api/v2/aci318/design/beam` works
- [ ] Feature flag disabled until verification pack complete

---

## 8. Phase 4 — EC2 (EN 1992-1-1)

### 8.1 EU-Specific Complications

1. **National Annex (NA)** — ~150 Nationally Determined Parameters. Default: recommended values. Must support UK NA, German NA as overrides.
2. **Variable strut inclination** — θ = 21.8°–45° for shear. An optimization problem inside a design function. No precedent in IS 456 or ACI.
3. **Parabolic-rectangular OR bilinear** — Two stress block options. HSC (C55+) changes the parabolic curve shape (n ≠ 2).
4. **εcu varies** — For C12–C50: 3.5‰. For C55–C90: variable. Affects ALL flexural calculations.
5. **Concrete classes** — C12/15 to C90/105. Much wider range than IS 456 (M15–M80).
6. **Creep model** — Complex function of RH, member size, cement class, age. Not a simple table lookup.
7. **Exposure classes** — XC1-4, XD1-3, XS1-3, XF1-4, XA1-3. More granular than IS 456.

### 8.2 EC2 Beam Functions

| # | Function | EC2 Reference |
|---|----------|--------------|
| 1 | `required_steel_area()` | Cl 6.1 |
| 2 | `variable_strut_shear()` | Cl 6.2.3 (optimize θ) |
| 3 | `concrete_shear_capacity()` | Cl 6.2.2 (VRd,c formula) |
| 4 | `torsion_design()` | Cl 6.3 (thin-walled tube) |
| 5 | `crack_width()` | Cl 7.3.4 |
| 6 | `deflection_span_depth()` | Cl 7.4.2 |
| 7 | `design_beam_ec2()` | Full beam design |

### 8.3 National Annex Architecture

```python
@dataclass
class NationalAnnex:
    """EC2 Nationally Determined Parameters."""
    name: str                    # "UK", "DE", "FR", "recommended"
    alpha_cc: float = 0.85       # UK: 0.85, recommended: 1.0
    gamma_c: float = 1.5         # All: 1.5
    gamma_s: float = 1.15        # All: 1.15
    k1_crack: float = 0.8        # Crack width param
    # ... ~150 parameters

EC2_RECOMMENDED = NationalAnnex(name="recommended")
EC2_UK_NA = NationalAnnex(name="UK", alpha_cc=0.85)
EC2_DE_NA = NationalAnnex(name="DE", alpha_cc=0.85)
```

### 8.4 Benchmark Sources

| Source | Purpose | Tolerance |
|--------|---------|-----------|
| The Concrete Centre "How to Design" | Primary (UK practice) | ±0.1% |
| Narayanan & Goodchild | Worked examples | ±1% |
| EC2 Worked Examples (Concrete Centre) | Comprehensive | ±0.5% |

### 8.5 Phase 4 Success Criteria
- [ ] EC2 beam flexure matches benchmarks ±0.1%
- [ ] Variable strut inclination optimization produces correct θ
- [ ] National Annex override system works for UK, recommended
- [ ] Cross-code test: same beam gives physically consistent results across 3 codes
- [ ] HSC (C55+) correctly uses variable εcu

---

## 9. Phase 5 — Fill the Matrix

### 9.1 Element × Code Matrix

| Element | IS 456 | ACI 318 | EC2 | Priority |
|---------|--------|---------|-----|----------|
| Beam | ✅ P0 | P3 | P4 | Core |
| Column | P1 | P5 | P5 | Core |
| One-way slab | P1 | P5 | P5 | Core |
| Two-way slab | P1 | P5 | P5 | Core |
| Footing | P1 | P5 | P5 | Core |
| Wall | P5 | P5+ | P5+ | Extended |
| Staircase | P5 | — | — | Extended |
| Deep beam | P5 | P5 | P5 | Extended |
| Flat slab | P5+ | P5+ | P5+ | Extended |
| Retaining wall | P5+ | P5+ | P5+ | Extended |

### 9.2 Companion Code Roadmap

| Code | Companion To | Status | Priority |
|------|-------------|--------|----------|
| IS 13920:2016 | IS 456 | Beam ✅, Column/Joint/Wall ❌ | P1 (column ductile) |
| IS 875 Parts 1-5 | IS 456 | ❌ | P2 (load combinations) |
| IS 1893:2016 | IS 456 | ❌ | P2 (seismic forces) |
| ASCE 7 | ACI 318 | ❌ | P3 (required for ACI combinations) |
| EN 1990 (EC0) | EC2 | ❌ | P4 (required for EC2 combinations) |
| EN 1991 (EC1) | EC2 | ❌ | P4 (loads for EC2) |
| EN 1998 (EC8) | EC2 | ❌ | P5 (seismic for EC2) |
| IS 1343 (Prestressed) | IS 456 | ❌ | P5+ (different domain) |
| IS 800 (Steel) | Independent | ❌ | P5+ (different domain) |
| IS 3370 (Liquid Retaining) | IS 456 | ❌ | P5+ |

### 9.3 Load Combination Engine

**Required for production multi-code use.** Each code has different load combinations:

| Code | Source | Typical Combinations |
|------|--------|---------------------|
| IS 456 | IS 875 Table 18 + IS 1893 | 8–12 gravity, 20–30 with seismic |
| ACI 318 | ASCE 7 §2.3.1 | 7 basic + permutations → 30–50 |
| EC2 | EN 1990 | Persistent/transient/accidental → 50+ |

**Data model:**
```python
@dataclass
class LoadCombination:
    name: str
    code: str
    factors: dict[str, float]  # {"DL": 1.5, "LL": 1.5, "WL": 0.0}
    situation: str             # "ultimate" | "service" | "accidental"
    reference: str             # "IS 456 Table 18 Case 1"
```

---

## 10. Risk Register

### 10.1 Top 10 Critical Risks

| # | Risk | Impact | Likelihood | Mitigation |
|---|------|--------|-----------|------------|
| 1 | **Cylinder vs cube confusion** | Systematic 25% errors in ACI/EC2 | HIGH | Plausibility guards: fck > 100 → "Did you mean psi?" |
| 2 | **φ vs γ architecture mismatch** | ACI code produces wrong results | HIGH | Each code's math is self-contained, never abstract safety factors |
| 3 | **National Annex proliferation (EC2)** | 150 parameters × N countries | MEDIUM | Start with "recommended" + UK NA only |
| 4 | **Variable strut inclination (EC2)** | No precedent in codebase | MEDIUM | Start with θ = 21.8° (conservative), add optimizer later |
| 5 | **Enhanced shear NOT implemented** | IS 456 currently unconservative | ~~HIGH~~ RESOLVED | ✅ Fixed in TASK-712 (PR #468) |
| 6 | **Column P-M interaction complexity** | Most complex IS 456 calculation | 🔄 PARTIALLY MITIGATED | Implemented incrementally as prescribed: axial → uniaxial → biaxial → P-M curve. 7/10 functions done. Remaining: slenderness, detailing |
| 7 | **Load combination explosion** | 50+ combinations per code | MEDIUM | Build combination engine early (Phase 2) |
| 8 | **ACI/EC2 code review expertise** | Team has IS 456 expertise only | HIGH | Require professional review for non-IS 456 code |
| 9 | **Test count explosion** | ~8000 tests, CI time grows | LOW | Parallelize by code in CI matrix |
| 10 | **Package rename** | `structural-lib-is456` → `structural-lib` | MEDIUM | Transitional package that depends on new name |

### 10.2 Numerical Edge Cases (ALL must be handled)

**Flexure:**
- Mu exactly = Mu_lim (balanced: singly reinforced, not doubly)
- Mu = 0 (return minimum steel, no division by zero)
- Doubly reinforced with compression steel NOT yielding
- T-beam with xu ≈ Df (three sub-cases in IS 456 Cl 38.4)
- T-beam with xu > D (impossible — error out)
- Negative moment on T-beam (flange in tension, use bw only)

**Shear:**
- τv exactly = τc (still need minimum stirrups per Cl 26.5.1.6)
- τv > τc,max (section inadequate — error, not design stirrups)
- pt < 0.15% (Table 19 clamped — document)
- Circular section shear (τv = VQ/Ib, not V/bd)

**Columns:**
- Pu = 0 (pure bending → beam analysis)
- Pu > Puz (section inadequate — αn undefined)
- Biaxial with Muy = 0 (reduce to uniaxial)
- Slender column biaxial (additional moments on BOTH axes)

**Slabs:**
- ly/lx exactly = 2.0 (one-way vs two-way boundary)
- Two-way with one free edge (not in Table 26)
- Flat slab punching with unbalanced moment

**Footings:**
- Eccentric loading (partial contact → triangular pressure)
- Biaxial eccentricity (outside kern)

**Torsion:**
- Equilibrium vs compatibility torsion (currently not distinguished)
- Combined torsion + shear contradictory rebar requirements

### 10.3 Material Model Risks

| Risk | Affected Codes | Severity |
|------|---------------|----------|
| Cube→cylinder conversion not constant (0.76–0.84) | IS456↔ACI/EC2 cross-reference | HIGH |
| HSC (>C50) changes εcu in EC2 | EC2 only | HIGH |
| β1 varies with f'c in ACI | ACI only | MEDIUM |
| Steel stress-strain differs (multi-point vs elasto-plastic vs hardening) | All | MEDIUM |
| Creep model complexity (EC2 >> IS 456 >> ACI) | EC2 | MEDIUM |

---

## 11. Testing Strategy

### 11.1 Test Organization

Mirror source structure:
```
Python/tests/
├── codes/
│   ├── is456/
│   │   ├── beam/
│   │   │   ├── test_flexure.py
│   │   │   ├── test_shear.py
│   │   │   └── ...
│   │   ├── column/
│   │   │   ├── test_axial.py
│   │   │   └── ...
│   │   └── test_common.py
│   ├── aci318/
│   │   ├── beam/
│   │   │   ├── test_flexure.py
│   │   │   └── ...
│   │   └── ...
│   └── ec2/
│       └── ...
├── cross_code/
│   ├── test_beam_comparison.py
│   ├── test_invariants.py
│   └── ...
└── existing tests (backward compat)
```

### 11.2 Six Test Types Per Function

1. **Unit tests** — Single function, known inputs/outputs
2. **Edge case tests** — Boundary conditions from §10.2
3. **Degenerate tests** — Zero moment, zero shear, etc.
4. **SP:16 / PCA / Concrete Centre benchmarks** — ±0.1% golden vectors
5. **Textbook examples** — ±1% (rounding tolerance)
6. **Hypothesis property tests** — Code-specific input strategies

### 11.3 Cross-Code Invariants

Properties that must hold regardless of code:
- Increasing concrete strength always increases capacity
- Zero moment → minimum steel (code-specific min)
- Capacity is always positive for valid inputs
- Doubling width approximately halves steel ratio (under-reinforced)
- All three codes agree on safe/unsafe for extreme cases (big margin or clearly failed)

### 11.4 Tolerances

| Source | Tolerance | Reason |
|--------|-----------|--------|
| SP:16 tables | ±0.1% | Published design tables |
| PCA Notes | ±0.1% | Precise examples |
| Textbook examples | ±1% | Intermediate rounding |
| Chart reading (SP:16 P-M diagrams) | ±0.5% | Visual reading error |
| Cross-code comparison | ±20% | Different codes, different safety margins |

### 11.5 CI Strategy

```yaml
# Parallelize by code
jobs:
  test-is456:
    run: pytest tests/codes/is456/ -v
  test-aci318:
    run: pytest tests/codes/aci318/ -v
  test-ec2:
    run: pytest tests/codes/ec2/ -v
  test-cross-code:
    run: pytest tests/cross_code/ -v
  test-legacy:
    run: pytest tests/ --ignore=tests/codes --ignore=tests/cross_code -v
```

---

## 12. Documentation Plan

### 12.1 Per-Code Documentation

Each code needs:
- [ ] Clause reference guide — mapping clauses to library functions
- [ ] Unit system guide — what units each parameter expects
- [ ] Material model description — stress-strain curves
- [ ] Safety factor explanation — partial factors vs φ
- [ ] Limitations — what is NOT implemented
- [ ] Worked examples (minimum 3 per code)
- [ ] Verification report with golden vectors

### 12.2 Cross-Code Docs

- [ ] "Which code should I use?" guide
- [ ] Parameter mapping table (machine-readable JSON)
- [ ] Conservatism comparison (same beam, 3 codes)
- [ ] Migration guide from v4 (single-code) to v5 (multi-code)

### 12.3 Parameter Mapping Table

| Concept | IS 456 | ACI 318 | EC2 |
|---------|--------|---------|-----|
| Concrete strength | `fck` (N/mm²) | `fc_prime` (MPa) | `fck` (MPa) |
| Steel yield | `fy` (N/mm²) | `fy` (MPa) | `fyk` (MPa) |
| Width | `b_mm` | `b_mm` | `b_mm` |
| Effective depth | `d_mm` | `d_mm` | `d_mm` |
| Design moment | `Mu_kNm` | `Mu_kNm` | `MEd_kNm` |
| Concrete partial factor | `gamma_c` = 1.5 | N/A (uses φ) | `gamma_c` = 1.5 |
| Steel partial factor | `gamma_s` = 1.15 | N/A (uses φ) | `gamma_s` = 1.15 |
| Flexure φ | N/A | `phi` = 0.90 | N/A |
| Shear φ | N/A | `phi` = 0.75 | N/A |

### 12.4 clauses.json Schema V2

```json
{
  "version": 2,
  "clauses": [
    {
      "id": "IS456:38.1",
      "code": "IS456",
      "clause": "38.1",
      "title": "Flexure — Rectangular sections",
      "category": "flexure",
      "element": "beam",
      "implemented": true,
      "function": "design_beam_flexure",
      "module": "codes.is456.beam.flexure"
    },
    {
      "id": "ACI318:22.2.2.4.1",
      "code": "ACI318",
      "clause": "22.2.2.4.1",
      "title": "Equivalent rectangular stress block",
      "category": "flexure",
      "element": "beam",
      "implemented": false
    }
  ]
}
```

### 12.5 CHANGELOG Convention

```markdown
## [0.22.0] - 2026-XX-XX
### Added
- [IS456] Column short axial capacity (Cl 39.3)
- [ACI318] Beam flexure with Whitney stress block
### Fixed
- [IS456] Enhanced shear near supports (Cl 40.3) — was unconservative
```

---

## 13. API Design

### 13.1 Unified Router Pattern

```python
# services/api.py
def design_beam(*, code: str, **kwargs) -> DesignEnvelope:
    """Design a beam under specified code.

    Args:
        code: "IS456", "ACI318", or "EC2"
        **kwargs: Code-specific parameters
    """
    code_impl = CodeRegistry.get(code)
    return code_impl.design_beam(**kwargs)
```

### 13.2 Code-Specific Input Dataclasses

```python
@dataclass
class IS456BeamInput:
    fck: float               # N/mm² (cube strength)
    fy: float                # N/mm²
    b_mm: float
    d_mm: float
    Mu_kNm: float
    Vu_kN: float = 0.0

@dataclass
class ACI318BeamInput:
    fc_prime: float           # MPa (cylinder strength)
    fy: float                # MPa
    b_mm: float
    d_mm: float
    Mu_kNm: float
    Vu_kN: float = 0.0

@dataclass
class EC2BeamInput:
    fck: float               # MPa (cylinder strength)
    fyk: float               # MPa
    b_mm: float
    d_mm: float
    MEd_kNm: float
    VEd_kN: float = 0.0
    national_annex: str = "recommended"
```

### 13.3 FastAPI Route Design

```
# v1 (backward compat, IS 456 only)
POST /api/v1/design/beam                    ← IS 456 hardcoded

# v2 (multi-code)
POST /api/v2/{code}/design/beam             ← code in path
POST /api/v2/{code}/design/column
POST /api/v2/{code}/design/slab
GET  /api/v2/codes                          ← list available codes
GET  /api/v2/{code}/capabilities            ← list available elements
```

### 13.4 CSV Adapter Multi-Code Support

`GenericCSVAdapter` maps 40+ column names (IS 456-specific). Needs per-code column mappings:
```python
COLUMN_MAPPINGS = {
    "IS456": {"fck": ["fck", "fck_mpa", "concrete_grade"], ...},
    "ACI318": {"fc_prime": ["fc", "f'c", "fc_psi", "concrete_strength"], ...},
    "EC2": {"fck": ["fck", "fck_mpa"], ...},
}
```

### 13.5 API Stability Contract

| API | Status | Policy |
|-----|--------|--------|
| `design_beam_is456(...)` | **Frozen** | Never changes (backward compat) |
| `design_beam(code='is456', ...)` | **Stable** from v5.0 | Follows semver |
| `codes.aci318.beam.flexure.required_steel_area()` | **Internal** | May change between minor versions |
| `CodeRegistry.get()` | **Stable** from v5.0 | Follows semver |

---

## 14. Agent Coordination

### 14.1 Phase 0 Agents

| Step | Agent | Task |
|------|-------|------|
| 1 | @backend | Create beam/ folder, move files, update imports |
| 2 | @backend | Generate backward-compat shims |
| 3 | @backend | Move ductile.py → is13920/ |
| 4 | @tester | Run full test suite, verify zero breakage |
| 5 | @reviewer | Architecture validation, import direction check |
| 6 | @doc-master | Update import docs, migration guide |
| 7 | @ops | Commit + create PR |

### 14.2 Phase 1 Agents (Per Element)

| Step | Agent | Task |
|------|-------|------|
| 1 | @structural-engineer | Define clauses, formulas, benchmark values |
| 2 | @structural-math | Implement pure math functions (9-step pipeline) |
| 3 | @tester | Write 6 test types per function, SP:16 benchmarks |
| 4 | @reviewer | Two-pass review (structural + code) |
| 5 | @backend | Wire into services/api.py |
| 6 | @api-developer | Create FastAPI endpoints |
| 7 | @frontend | Add UI forms for new elements |
| 8 | @doc-master | Update docs |
| 9 | @ops | Commit + PR |

### 14.3 Phase 2-4 Agents (Per Code)

Same as Phase 1, but with additional:
- @library-expert validates API design decisions
- @security reviews input validation for new code parameters
- Professional review (external) for non-IS 456 math

### 14.4 Quality Pipeline (Mandatory — No Exceptions)

Every IS 456 function must pass the 9-step pipeline from `/function-quality-pipeline`:

1. PLAN → Identify clause + formula + benchmark
2. MATH REVIEW → @structural-engineer verifies independently
3. IMPLEMENT → @structural-math writes code (12-point checklist)
4. TEST → @tester: unit + edge + degenerate + SP:16 + textbook + Hypothesis
5. REVIEW → Two-pass: @structural-engineer (math) + @reviewer (code)
6. API WIRE → @backend adds to services/api.py
7. ENDPOINT → @api-developer creates FastAPI route
8. DOCUMENT → @doc-master
9. COMMIT → @ops via ai_commit.sh

**Gates:**
- Step 2→3: Formula approved by @structural-engineer
- Step 4→5: All tests pass (SP:16 ±0.1%)
- Step 5→6: Both reviews APPROVED

---

## 15. Success Criteria

### 15.1 Per-Phase Gates

| Phase | Gate | Metric |
|-------|------|--------|
| 0 | All tests pass, backward compat works | 0 test failures |
| 1 | Column SP:16 ±0.1%, slab Table 26 matches | All benchmarks pass |
| 2 | CodeRegistry functional, design_beam(code=) works | smoke test passes |
| 3 | ACI beam matches PCA Notes ±0.1% | Golden vectors pass |
| 4 | EC2 beam matches Concrete Centre ±0.1% | Golden vectors pass |
| 5 | All Phase elements × codes verified | Full matrix green |

### 15.2 Overall v5 Targets

- [ ] 3 codes registered and functional
- [ ] 5+ elements per code (beam, column, slab 1-way, slab 2-way, footing)
- [ ] Golden vector verification for each code×element
- [ ] Cross-code comparison test suite
- [ ] FastAPI v2 routes for all codes
- [ ] Complete API documentation per code
- [ ] Zero backward-compat breakage for existing IS 456 users
- [ ] CI parallel by code, total time < 15 minutes

---

## 16. Appendices

### A. IS 456 Clause Coverage (Complete List)

| Clause | Description | Status | Phase |
|--------|-------------|--------|-------|
| Cl 24.1–24.2 | One-way slab | ❌ | P1 |
| Cl 24.3, Annex D | Two-way slab | ❌ | P1 |
| Cl 25.1–25.4 | Column classification & eccentricity | ✅ Done | P1 |
| Cl 26.2–26.5 | Detailing (beam) | ✅ | Done |
| Cl 29 | Deep beams | ❌ | P5 |
| Cl 31.6 | Punching shear | ❌ | P1 |
| Cl 32 | Walls | ❌ | P5 |
| Cl 33 | Stairs | ❌ | P5 |
| Cl 34 | Footings | ❌ | P1 |
| Cl 38.1–38.4 | Flexure (beam) | ✅ | Done |
| Cl 39.1–39.7 | Column design | 🔄 Partial — 39.3/39.5/39.6 ✅, 39.4/39.7 ❌ | P1 |
| Cl 40.1–40.5 | Shear (beam) | ✅ | Done |
| Cl 40.3 | Enhanced shear near supports | ✅ Done | Done |
| Cl 41 | Torsion | ✅ | Done |
| Cl 43 | Serviceability | ✅ | Done |
| Annex B | Continuous beam coefficients | ❌ | P2 |
| Annex C | Moment redistribution | ❌ | P2 |
| Annex D | Two-way slab coefficients | ❌ | P1 |
| Annex E | Column effective length (stiffness method) | ❌ | P1 |
| Annex G | P-M interaction | ✅ Done | P1 |
| Table 26 | Two-way moment coefficients | ❌ | P1 |
| Table 28 | Column effective length ratios | ✅ Done | P1 |

### B. Seismic Detailing Comparison

| Parameter | IS 13920 | ACI Ch.18 | EC8 |
|-----------|----------|-----------|-----|
| classification | Single level | Special/Intermediate/Ordinary | DCL/DCM/DCH |
| Strong column-weak beam | ΣMc ≥ 1.1·ΣMb | ΣMnc ≥ 1.2·ΣMnb | ΣMRc ≥ 1.3·ΣMRb |
| Max stirrup spacing (PHZ) | d/4, 8db, 100mm | d/4, 6db, 150mm | bo/2, 175mm, 8dbL |
| Min beam steel | 0.24√fck/fy | standard min | ductility-dependent |
| Confinement | Ash formula | Pu/(Ag·f'c) dependent | ωwd (ductility class) |
| Capacity shear | 1.4·Mu at ends | 1.25·fy (Mpr) | γRd overstrength |

### C. File Count Projection

| Phase | Source Files | Test Files | Total |
|-------|-------------|------------|-------|
| Current | 133 | 113 | 246 |
| After P0 | ~140 (+shims) | 113 | ~253 |
| After P1 | ~180 (+elements) | ~220 (+element tests) | ~400 |
| After P2 | ~200 (+infra) | ~230 | ~430 |
| After P3 | ~240 (+ACI beam) | ~300 (+ACI tests) | ~540 |
| After P4 | ~280 (+EC2 beam) | ~370 (+EC2 tests) | ~650 |
| After P5 | ~500-600 | ~500-600 | ~1100 |

### D. Dependency Impact

| Phase | New Dependencies | Reason |
|-------|-----------------|--------|
| P0-P2 | None | Pure restructure + infrastructure |
| P3 (ACI) | None likely | Formula-based, no tables |
| P4 (EC2) | None likely | Complex math but achievable in pure Python |
| P1 (Column P-M) | NumPy (optional) | Interaction diagram efficiency; fallback to pure Python |

### E. Package Distribution Strategy

| Version | Package Name | Contents |
|---------|-------------|----------|
| 0.20.x | `structural-lib-is456` | Current (IS 456 only) |
| 0.21.0 | `structural-lib-is456` | Phase 0 restructure, backward compat |
| 1.0.0 | `structural-lib` | Multi-code release (IS 456 + ACI beam) |
| 1.0.0 | `structural-lib-is456` | Transitional shim → depends on `structural-lib>=1.0.0` |
