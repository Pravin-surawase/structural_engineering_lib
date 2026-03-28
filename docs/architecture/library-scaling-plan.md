# Library Scaling Plan — structural-lib-is456

**Type:** Architecture
**Audience:** All Agents, Developers
**Status:** Approved
**Importance:** Critical
**Created:** 2026-03-29
**Last Updated:** 2026-03-29

---

## Vision

Transform `structural-lib-is456` from a beam-focused IS 456 library into the definitive open-source RC design library for civil/structural engineers. **v1.0** completes IS 456 coverage for all major building elements. **v2.0** adds ACI 318 as the second design code, proving the multi-code architecture.

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Package structure | Single PyPI package, all codes included | Simpler for users; plugins add complexity too early |
| Version strategy | v1.0 = IS 456 complete → v2.0 = multi-code | Quality over breadth; establish patterns first |
| Next element after columns | RC slabs (one-way, two-way per IS 456 Cl 24) | Most common use case |
| Next design code | ACI 318 (USA) | Most global demand |
| Backward-compat stubs (46 files) | Deprecate now, remove in v2.0 | Migration time for users |
| Code organization | By design code, then by element type | Proven by SciPy/SfePy; code-specific helpers stay isolated |
| Element isolation | `beam/` cannot import from `column/` | Shared code goes in `common/` only |

---

## Architecture: 4-Layer (Unchanged)

```
Layer 1: Core Types    → core/           Code-agnostic base classes, types, constants
Layer 2: Design Codes  → codes/is456/    Pure math, NO I/O, explicit units (mm, N/mm², kN, kNm)
Layer 3: Services      → services/       Orchestration: api.py, adapters.py, pipelines
Layer 4: UI/IO         → react_app/, fastapi_app/
```

**Import rule:** Core ← Codes ← Services ← UI. Never upward.
**Units rule:** All explicit — mm, N/mm², kN, kNm. No hidden conversions.

---

## Phase 1: Architecture Foundation (Pre-requisite)

### 1.1 Restructure `codes/is456/` by Element

**Current** (flat, 14 files — won't scale):
```
codes/is456/
├── flexure.py        ← beam-specific
├── shear.py          ← beam-specific
├── detailing.py      ← beam-specific
├── column.py         ← column-specific
├── slenderness.py    ← mixed beam+column
├── torsion.py        ← beam-specific
├── serviceability.py ← beam-specific
├── ductile.py        ← beam-specific (IS 13920)
├── compliance.py     ← orchestration
├── materials.py      ← shared
├── tables.py         ← shared
├── load_analysis.py  ← shared
├── traceability.py   ← shared
└── clauses.json      ← shared
```

**Target** (element-organized):
```
codes/is456/
├── __init__.py           ← IS456Code, @clause, constants
├── clauses.json          ← All clause metadata
├── traceability.py       ← @clause decorator, clause DB
├── compliance.py         ← Multi-element compliance orchestration
│
├── common/               ← Shared IS 456 helpers
│   ├── __init__.py
│   ├── materials.py      ← Grade tables, xu_max, stress-strain
│   ├── tables.py         ← Table 19 (τc), Table 20 (τc_max), Table 28
│   ├── load_analysis.py  ← BMD/SFD computation
│   ├── durability.py     ← Cl 8: Cover, exposure classes (future)
│   └── safety_factors.py ← γc=1.5, γs=1.15, load factors (future)
│
├── beam/                 ← Beam design (Cl 22-26, 38-43)
│   ├── __init__.py
│   ├── flexure.py        ← Cl 38: Singly/doubly/flanged
│   ├── shear.py          ← Cl 40: Shear design
│   ├── torsion.py        ← Cl 41: Torsion
│   ├── detailing.py      ← Cl 26: Bar spacing, hooks, anchorage
│   ├── serviceability.py ← Cl 42-43: Deflection, crack width
│   ├── slenderness.py    ← Cl 23.3: Beam lateral stability
│   └── ductile.py        ← IS 13920: Seismic ductile detailing
│
├── column/               ← Column design (Cl 25, 39)
│   ├── __init__.py
│   ├── design.py         ← Cl 39: Axial + bending, P-M interaction
│   ├── slenderness.py    ← Cl 25.1: Short/long classification
│   ├── detailing.py      ← Cl 26.5.3: Ties, spacing, lap lengths (future)
│   └── biaxial.py        ← Cl 39.6: Biaxial bending — Bresler (future)
│
├── slab/                 ← Slab design (Cl 24, 31) — v0.22+
│   ├── __init__.py
│   ├── one_way.py        ← Cl 22.2: One-way bending
│   ├── two_way.py        ← Cl 24.4: Coefficient method (Table 26)
│   ├── detailing.py      ← Cl 26.3: Slab reinforcement rules
│   └── serviceability.py ← Deflection, crack width for slabs
│
├── footing/              ← Footing design (Cl 34) — v0.24+
│   ├── __init__.py
│   ├── isolated.py       ← Cl 34.1-34.3: Isolated footings
│   ├── combined.py       ← Combined/strap footings
│   ├── punching_shear.py ← Cl 31.6: Punching shear
│   └── detailing.py      ← Footing rebar rules
│
├── wall/                 ← Wall design (Cl 32) — v0.26+
│   ├── __init__.py
│   ├── design.py         ← Cl 32: Plain/RC walls
│   ├── shear_wall.py     ← IS 13920 Part 2: Shear walls
│   └── detailing.py      ← Wall reinforcement
│
└── staircase/            ← Staircase design (Cl 33) — v0.28+
    ├── __init__.py
    ├── design.py          ← Waist slab, folded plate
    └── detailing.py       ← Stair rebar
```

**Migration approach:**
1. Create new subdirectories
2. Copy files into element-specific subfolders
3. Create backward-compat stubs at old locations (re-export from new path)
4. Update internal imports in moved files
5. Add deprecation warnings to old-path stubs
6. Run `scripts/validate_imports.py` after each batch
7. Run full test suite — all 2,270+ tests must pass

### 1.2 Extend Core Types for Multi-Element

Add to `core/`:
- `ColumnInput`, `SlabInput`, `FootingInput` (in `inputs.py`)
- `CircularSection` (in `geometry.py`)
- `ElementType` enum: BEAM, COLUMN, SLAB, FOOTING, WALL (in `data_types.py`)
- `LoadCombination` class (new `loads.py`)

**Principle**: Core types are code-agnostic — they define geometry and load concepts, not IS 456 or ACI math.

### 1.3 Deprecate Root-Level Backward-Compat Stubs

46 files at `Python/structural_lib/` root re-export from `services/` or `core/`:
- Add `DeprecationWarning` to each
- Document as deprecated in CHANGELOG (v0.21)
- Remove in v2.0
- Provide migration guide

### 1.4 Formalize Element Addition Workflow

8-step pipeline (already in `/new-structural-element` skill):
1. Research — IS 456 clauses, formulas, tables
2. Core types — geometry/input/result types in `core/`
3. Math module — pure math in `codes/is456/<element>/`
4. Unit tests — clause-by-clause verification, hand-calc benchmarks
5. API wiring — public functions in `services/api.py`
6. FastAPI endpoint — router in `fastapi_app/routers/`
7. React UI — component + hook (deferred for v1.0)
8. Documentation — API reference + verification doc

---

## Phase 2: Complete IS 456 Column Design (v0.20-v0.21)

| Feature | IS 456 Clause | Status |
|---------|---------------|--------|
| Short column design (axial + uniaxial) | Cl 39.3-39.5 | ✅ Done |
| Column slenderness classification | Cl 25.1.2 | ✅ Done |
| Effective length factor | Table 28 | ✅ Done |
| Long column additional moment | Cl 39.7.1 | ❌ Planned |
| Biaxial bending (Bresler) | Cl 39.6 | ❌ Planned |
| Full P-M interaction curve | Cl 39.5 | ❌ Planned |
| Column detailing (ties, spirals) | Cl 26.5.3 | ❌ Planned |
| Circular columns | — | ❌ Planned |

**Key formulas:**
- Long column: $M_{add} = P_u \cdot e_a$ where $e_a = \frac{l_{eff}^2}{2000 D}$
- Biaxial: $\left(\frac{M_{ux}}{M_{ux1}}\right)^{\alpha_n} + \left(\frac{M_{uy}}{M_{uy1}}\right)^{\alpha_n} \leq 1.0$

**Verification**: SP 16 charts (27-62), hand calculations, ETABS comparison.

---

## Phase 3: Slab Design — IS 456 Cl 24, 31 (v0.22-v0.23)

### Scope: RC slabs only (IS 456)

1. **Core types**: `SlabGeometryInput(Lx_mm, Ly_mm, D_mm, cover_mm, edge_conditions)`, `SlabDesignResult`
2. **One-way slab** — Cl 22.2 (span ratio > 2): design per meter strip width
3. **Two-way slab** — Cl 24.4: coefficient method from Table 26 (9 edge conditions)
   - $M_x = \alpha_x \cdot w \cdot l_x^2$ and $M_y = \alpha_y \cdot w \cdot l_x^2$
   - Torsion reinforcement at corners (Cl 24.4.3)
4. **Slab detailing** — Cl 26.3: min steel, max spacing (3d or 300mm), curtailment
5. **Slab serviceability** — different span/depth factors for slabs
6. **Verification**: SP 24 examples, textbook benchmarks (Pillai & Menon)

---

## Phase 4: Footing Design — IS 456 Cl 34 (v0.24-v0.25)

1. Isolated footing — Cl 34.1-34.3: bearing pressure, flexure, one-way shear, punching shear
2. Punching shear — Cl 31.6: critical perimeter, shear stress (shared with slabs)
3. Combined/strap footings
4. Footing detailing — development length, bar spacing

---

## Phase 5: Walls & Staircases (v0.26-v0.28)

1. Plain/RC walls — Cl 32: axial + lateral loads, effective height
2. Shear walls — IS 13920 Part 2: ductile shear walls
3. Staircases — Cl 33: waist slab design, dog-leg, open-well

---

## Phase 6: Multi-Code — ACI 318 (v2.0)

### 6.1 Code Abstraction

Extend `core/` with design operation protocols:
```python
# core/protocols.py
class FlexureProtocol(Protocol):
    def design_flexure(self, section, loads, materials) -> FlexureResult: ...

class ShearProtocol(Protocol):
    def design_shear(self, section, loads, materials) -> ShearResult: ...
```

### 6.2 ACI 318 Structure (mirrors IS 456)

```
codes/aci318/
├── common/            ← ACI material models (f'c, fy), φ factors
├── beam/              ← ACI beam flexure (Whitney stress block)
├── column/            ← ACI column (P-M interaction, moment magnification)
└── slab/              ← ACI direct design / equivalent frame
```

### 6.3 Unified API

```python
def design_beam(geometry, materials, loads, code="is456"):
    designer = CodeRegistry.get(code).get_beam_designer()
    return designer.design(geometry, materials, loads)
```

### 6.4 Unit System

ACI 318 uses imperial. Add `core/units.py`:
- All internal math stays SI (mm, N/mm²)
- Imperial conversion at API boundary only
- `@require_units("SI")` / `@require_units("imperial")` decorators

### 6.5 Cleanup

- Remove all 46 backward-compat stubs
- Clean up root `__init__.py`
- Bump major version → breaking change
- Migration guide in docs

---

## Versioning Roadmap

| Version | Milestone | Key Deliverables |
|---------|-----------|-----------------|
| **v0.20** | Column complete | Long columns, biaxial, P-M curve, detailing |
| **v0.21** | Architecture refactor | Element subfolders, stub deprecation, core types |
| **v0.22** | Slab design | One-way slab (Cl 22.2, Table 12/13) |
| **v0.23** | Slab complete | Two-way slab (Cl 24.4, Table 26), slab detailing |
| **v0.24** | Footing design | Isolated footing (Cl 34), punching shear |
| **v0.25** | Footing complete | Combined footing, footing detailing |
| **v0.26** | Wall design | Plain/RC walls (Cl 32) |
| **v0.27** | Shear walls | IS 13920 shear walls |
| **v0.28** | Staircase | Waist slab design (Cl 33) |
| **v1.0** | **IS 456 Complete** | All elements, full clause coverage, verification |
| **v2.0** | **Multi-code** | ACI 318, unified API, stubs removed |

---

## Testing Strategy

### Mirror Code Structure in Tests
```
tests/unit/codes/is456/beam/test_flexure.py
tests/unit/codes/is456/column/test_design.py
tests/unit/codes/is456/slab/test_two_way.py
tests/verification/is456/sp16_benchmarks.py
tests/integration/test_cross_code.py        ← v2.0: IS 456 vs ACI 318
```

### Requirements per Element
- 85% branch coverage (existing)
- At least 1 hand-calc benchmark per IS 456 clause
- Property-based tests for boundary conditions (Hypothesis)
- Regression snapshots for API output stability
- Minimum 20 tests per element module

### Benchmark Sources
| Source | Accuracy | Use For |
|--------|----------|---------|
| SP:16 Design Aids | ±0.1% (authoritative) | Standard design charts |
| SP:24 Explanatory Handbook | ±0.5% | Worked examples |
| Pillai & Menon | ±1% | Textbook cross-check |
| ETABS/STAAD | Exact match target | Software validation |

---

## Debugging & Maintenance

### Traceability
- Every IS 456 function decorated with `@clause("Cl X.Y.Z")`
- Extend with `element=` parameter for element-aware tracing
- CLI: `python -m structural_lib clause 38.1` → show implementation + tests

### Error Hierarchy
```
E_BEAM_FLX_001  (beam flexure error)
E_COL_DES_001   (column design error)
E_SLAB_2W_001   (two-way slab error)
E_FTG_PUN_001   (footing punching shear error)
```

### Logging
```python
logger = logging.getLogger("structural_lib.is456.beam.flexure")
logger.debug("Neutral axis: xu=%.2f mm (xu_max=%.2f mm)", xu, xu_max)
```
- Default: WARNING (silent)
- Debug: `logging.getLogger("structural_lib").setLevel(logging.DEBUG)`

### Architecture Enforcement
- `scripts/check_architecture_boundaries.py` — 4-layer + element isolation
- CI: import direction validation on every PR
- Rule: `beam/` cannot import from `column/` — shared code in `common/` only

### Performance
- `pytest-benchmark` for critical path functions
- CI regression detection (flag >10% slowdown)
- Profile batch designs (1000+ elements)

---

## Efficiency Considerations

### Lazy Loading
```python
# codes/__init__.py — don't load ACI 318 unless requested
def __getattr__(name):
    if name == "aci318":
        from structural_lib.codes import aci318
        return aci318
    raise AttributeError(name)
```

### Caching
- Material property lookups: `@functools.lru_cache`
- Table interpolations: `@lru_cache(maxsize=256)`
- P-M interaction curves: compute once, reuse for multiple load cases

### Batch Processing
- Extend `beam_pipeline.py` pattern for all elements
- `concurrent.futures` for independent element designs
- NumPy vectorization for table lookups

### Memory
- `__slots__` on high-frequency dataclasses
- `TypedDict` for transient data, `dataclass` for persistent results

---

## Further Considerations

1. **ReadTheDocs**: Deploy documentation site (like section-properties) for v1.0 launch
2. **JOSS Paper**: Submit to Journal of Open Source Software at v1.0 — significantly boosts academic adoption
3. **Standard Section Library**: Pre-built IS section profiles (ISMB, ISMC, etc.) in `core/sections.py`
4. **Entry Points**: Prepare `pyproject.toml` entry points for future third-party code plugins

---

## References

- IS 456:2000 — Indian Standard for Plain and Reinforced Concrete
- SP:16 — Design Aids for Reinforced Concrete (IS 456)
- SP:24 — Explanatory Handbook on IS 456
- ACI 318-19 — Building Code Requirements for Structural Concrete
- SciPy contributor guide — Module organization patterns
- section-properties (v3.10) — Cross-section analysis library (structural engineering Python reference)
- SfePy — Finite element library organization
