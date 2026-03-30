# Library Expansion Master Blueprint v3.0

**Type:** Planning
**Audience:** All Agents
**Status:** Approved
**Importance:** Critical
**Created:** 2026-03-29
**Last Updated:** 2026-03-30
**Version:** 3.0
**Review Round:** 4 (library-expert, structural-engineer, reviewer — quality systems approved)

> Single source of truth for expanding structural_engineering_lib from beam-only to a full IS 456 structural design suite.

---

## 1. Vision

Transform the current beam-only IS 456 library into a **production-grade, multi-element structural design suite** covering columns, slabs, footings, staircases, and shear walls — with the accuracy, traceability, and code quality standards of organisations like ARUP, Bentley, and RISA.

### Goals
- **Engineering credibility:** Validated against SP:16 with downloadable validation report for practicing engineers
- **Developer experience:** 5-minute quickstart from `pip install` to first design result
- **Maintainability:** Automated quality gates, maintenance playbook, succession plan
- **Extensibility:** Clean patterns that make adding the 7th element as easy as the 2nd

### Non-Goals (for now)
- Multi-code support (ACI 318, EC2) — deferred until IS 456 suite is complete
- Full React UI per element — API-first, frontend later
- Combined project workflows (beam + column + footing) — defer to v0.25+
- Internationalization (i18n) — defer to v1.0+ when user demand confirmed

---

## 2. Current State Assessment

### What Works Well
| Area | Status | Details |
|------|--------|---------|
| IS 456 Beam Math | ✅ Excellent | 10 modules (flexure, shear, torsion, detailing, ductile, serviceability, slenderness, materials, tables, compliance) |
| Error Hierarchy | ✅ Solid | 8-class hierarchy with `StructuralLibError` base, `DesignError` dataclass with 29+ pre-defined codes |
| Validation Framework | ✅ Good | `validate_dimensions()`, `validate_materials()` return error lists (no early abort) |
| Traceability | ✅ Excellent | `@clause("XX.X")` decorator + `clauses.json` database — every function linked to IS 456 clause |
| Test Suite | ✅ Comprehensive | 2270+ tests, 86% coverage, 7 marker categories, Hypothesis property tests, golden vectors |
| 4-Layer Architecture | ✅ Enforced | Core → IS 456 → Services → UI, one-direction imports, validated by CI scripts |
| API Surface | ✅ Stable | 23+ public functions in `services/api.py`, machine-readable manifest |
| Centralized Logging | ✅ Done | `get_logger(__name__)` factory with `STRUCTURAL_LIB_LOG_LEVEL` env var |
| FastAPI Exception Handlers | ✅ Done | 7 handlers mapping structural_lib errors → HTTP status codes with structured JSON |
| Error Code Registry | ✅ Done | `generate_error_docs.py` auto-generates `error-codes.md` (29 codes, 5 categories) |
| API Versioning Contract | ✅ Done | `check_api_compat.py` + `api_manifest.json` detect breaking changes |
| Test Fixtures | ✅ Done | `m25_fe415()`, `m30_fe500()` fixtures + Hypothesis profiles |

### What Still Needs Improvement
| Gap | Impact | Priority | Status |
|-----|--------|----------|--------|
| No `@deprecated` decorator | Cannot deprecate 50+ stubs safely | 🔴 High | Not started |
| No shared math in `codes/is456/common/` | Column will duplicate beam xu_max logic | 🔴 High | Not started |
| No `is456_assertions.py` helper | Test duplication across element test files | 🟡 Medium | Not started |
| `clauses.json` missing 66+ subclauses | New elements have no clause references | 🔴 High | Not started |
| IS 13920 not referenced anywhere | Seismic compliance impossible | 🔴 High | Not started |
| No Request ID middleware | Cannot trace requests end-to-end | 🟡 Medium | Not started |
| No top-level `__init__.py` exports | Users must use verbose imports | 🟡 Medium | Not started |
| No 5-minute quickstart CLI | External users can't verify installation | 🟡 Medium | Not started |
| No validation pack | Engineers can't prove library accuracy to clients | 🟡 Medium | Not started |
| No maintenance playbook | No documented process for ongoing operations | 🔴 High | Not started |

---

## 3. Architecture & Code Patterns

### 3.1 Shared Math Organization

Functions used by 2+ elements MUST be extracted to `codes/is456/common/`:

```
Python/structural_lib/codes/is456/common/
├── __init__.py
├── stress_blocks.py      — xu_max, stress block depth, balanced section
├── reinforcement.py      — pt limits, bar area helpers, spacing rules
├── confinement.py        — ties/spirals for columns and boundary elements
├── minimums.py           — min reinforcement, min dimensions per element
└── punching_shear.py     — punching shear checks (footing + two-way slab)
```

**Examples of shared math:**
| Function | Used By | Current Location |
|----------|---------|-----------------|
| `calculate_xu_max(fck, fy)` | beam, column, slab | `flexure.py` (extract) |
| `stress_block_depth(xu, fck)` | beam, column, slab | `flexure.py` (extract) |
| `bar_spacing_limits(bar_dia, agg_size)` | all elements | `detailing.py` (extract) |
| `punching_shear_stress(Vu, bo, d)` | footing, two-way slab | NEW |
| `min_reinforcement(element_type, fck, fy)` | all elements | NEW |
| `confinement_ties(b, D, bar_dia)` | column, shear wall | NEW |

**Rule:** Extract BEFORE starting Phase 2 column work. Never duplicate beam math in column.py.

### 3.2 Result Type Strategy

All new result types use **immutable frozen dataclasses** with convenience methods:

```python
@dataclass(frozen=True)
class ColumnResult:
    """Column design result (immutable, thread-safe)."""
    ast_required_mm2: float
    ast_provided_mm2: float
    pu_capacity_kN: float
    mu_capacity_kNm: float
    interaction_ok: bool
    governing_check: str
    clause_refs: tuple[str, ...] = ()
    errors: tuple[DesignError, ...] = ()

    def is_safe(self) -> bool:
        """Check if design passes all ERROR-severity checks."""
        return not any(e.severity == Severity.ERROR for e in self.errors)

    def to_dict(self) -> dict:
        """Export as dict for JSON serialization."""
        from dataclasses import asdict
        return asdict(self)

    def summary(self) -> str:
        """Human-readable one-line summary."""
        status = "✓ SAFE" if self.is_safe() else "✗ UNSAFE"
        return f"Column {status}: Ast={self.ast_provided_mm2:.0f} mm²"

    @property
    def utilization_ratio(self) -> float:
        """Capacity utilization (0.0 to 1.0+)."""
        if self.ast_provided_mm2 <= 0:
            return float('inf')
        return self.ast_required_mm2 / self.ast_provided_mm2
```

**Mandatory methods for all result types:** `is_safe()`, `to_dict()`, `summary()`
**Use `tuple` not `list`** for immutable collections in frozen dataclasses.

### 3.3 API Import Strategy

```python
# Users CAN do (preferred — simple):
from structural_lib import design_column_is456

# Users CAN do (explicit):
from structural_lib.services.api import design_column_is456

# Internal: api.py stays flat but imports from submodules
# services/api.py re-exports everything
# __init__.py re-exports all public design functions
```

**CI Gate:** Validate `__init__.py` exports match `api_manifest.json` functions.

### 3.4 Cross-Element Workflows (v0.25+)

```
Single element design:    codes/is456/<element>.py    (pure math)
Multi-element workflows:  services/workflows/          (orchestration, future)

Example: services/workflows/column_footing.py
  → imports from codes/is456/column AND codes/is456/footing
  → orchestrates: design column → extract reactions → design footing
  → NEVER merge IS 456 math across elements in one file
```

### 3.5 Function Writing Standards (mandatory for all agents)

Every function in `codes/is456/` MUST follow these rules. The `@library-expert` agent enforces these during review.

#### Pure Function Requirements
```
✅ MUST be stateless — same inputs → same outputs, always
✅ MUST NOT read files, env vars, databases, or network
✅ MUST NOT modify any global or module-level state
✅ MUST raise exceptions for invalid inputs (no silent None returns)
✅ MUST return typed result objects (frozen dataclass), never raw floats or dicts
✅ MAY call get_active_trace() for tracing (read-only check, no side effects when disabled)
```

#### Input/Output Contract Template

Every public function in `codes/is456/` must follow this docstring format:

```python
@clause("XX.X")
def calculate_something(
    b_mm: float,      # Always: explicit name with unit suffix
    d_mm: float,      # b_mm → mm; fck → N/mm²; Mu_kNm → kN·m
    fck: float,
    fy: float,
) -> SomeResult:      # Always return a typed result, never a raw float
    """One-line description per IS 456 clause.

    IS 456 Cl XX.X:
        Formula: Mu_lim = 0.36 × (xu_max/d) × [1 - 0.42 × (xu_max/d)] × b × d² × fck

    Args:
        b_mm: Width (mm). Must be > 0.
        d_mm: Effective depth (mm). Must be > 0.
        fck: Concrete strength (N/mm²). Standard grades: 15-80.
        fy: Steel yield strength (N/mm²). Standard: 250, 415, 500.

    Returns:
        SomeResult with fields: [list key fields]

    Raises:
        DimensionError: If b or d ≤ 0
        MaterialError: If fck or fy ≤ 0 or out of IS 456 range

    References:
        IS 456:2000 Cl XX.X
        SP:16, Table YY (validation source)
    """
```

#### Numerical Stability Rules
```
✅ NEVER compare floats with ==. Use abs(a - b) < TOLERANCE
✅ NEVER divide without checking denominator — use safe_divide() from core/numerics.py
✅ ALWAYS use intermediate variables for complex expressions (aids tracing and debugging)
✅ ALWAYS compute in consistent units internally, convert at boundaries only
✅ CLAMP interpolation inputs to table bounds (never extrapolate IS 456 tables)
✅ PREFER multiplication over division where algebraically equivalent
✅ GUARD against catastrophic cancellation (a - b where a ≈ b)
✅ CHECK every output: if math.isnan(result) or math.isinf(result) → raise CalculationError
```

#### IS 456 Formula Annotation Standard

Every formula computation MUST be preceded by a comment showing the clause reference and symbolic form:

```python
# IS 456 Cl 38.1: xu_max/d from Table 21.1 (based on fy)
xu_max_d = materials.get_xu_max_d(fy)

# IS 456 Cl 38.1: Mu_lim = 0.36 × (xu_max/d) × [1 - 0.42 × (xu_max/d)] × b × d² × fck
k = 0.36 * xu_max_d * (1 - 0.42 * xu_max_d)
mu_lim_nmm = k * fck * b * d * d

# Convert N·mm → kN·m
mu_lim_knm = mu_lim_nmm / 1e6
```

#### Red-Flag Detection (post-design sanity checks)

All result types should include a `safety_flags` property that catches:
- Utilization > 0.95 → `NEAR_CAPACITY` warning
- Ast > 4% bD → `HIGH_STEEL` constructability concern
- Negative reinforcement area → `CALCULATION_ERROR`
- Slenderness > 60 → `SECTION_INADEQUATE` per Cl 25.3.1

These are NOT clause checks — they're sanity checks that catch calculation errors individual clause checks might miss.

---

## 4. Phased Implementation Plan

### Phase 1: Foundation Cleanup (remaining items)

Must complete before writing the first column function.

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 1.1 | Create `@deprecated` decorator | `core/deprecation.py` | 📋 TODO |
| 1.2 | Create test assertion helpers | `tests/helpers/is456_assertions.py` | 📋 TODO |
| 1.3 | Stack trace sanitization (security — P0) | `fastapi_app/main.py` catch-all handler | 📋 TODO |
| 1.4 | Extract shared math | `codes/is456/common/` (5 files) | 📋 TODO |
| 1.5 | Populate clauses.json | Cl 24, 25, 31.6, 32, 33, 34, 39 (~66 subclauses) | 📋 TODO |
| 1.6 | Add IS 13920 references | `clauses.json` (~15 entries) | 📋 TODO |
| 1.7 | Top-level `__init__.py` exports | `structural_lib/__init__.py` | 📋 TODO |
| 1.8 | Create maintenance playbook | `docs/governance/maintenance-playbook.md` | 📋 TODO |
| 1.9 | Create `core/numerics.py` — numerical precision utilities | `safe_divide()`, `approx_equal()`, `clamp()`, epsilon constants | 📋 TODO |
| 1.10 | Add `recovery` field to `DesignError` | `core/errors.py` — non-breaking (optional field) | 📋 TODO |
| 1.11 | Create `scripts/check_clause_coverage.py` | IS 456 clause gap detection CI script | 📋 TODO |
| 1.12 | Create `scripts/check_new_element_completeness.py` | Verify new modules have all required artifacts | 📋 TODO |
| 1.13 | Add `X-Process-Time` middleware | `fastapi_app/main.py` — CORS already declares it | 📋 TODO |
| 1.14 | Consolidate existing `_clamp`/division guards | Migrate from `utilities.py`, `report_svg.py` → `core/numerics.py` | 📋 TODO |
| 1.15 | Hardcode partial safety factors | `codes/is456/common/constants.py` — γc=1.5, γs=1.15 as immutable constants | 📋 TODO |
| 1.16 | Unit plausibility guards at API boundary | `services/api.py` — `assert_unit_mm()`, `assert_unit_mpa()`, `assert_unit_kn()` | 📋 TODO |
| 1.17 | Add `formula_signatures` to `clauses.json` | Cross-reference validation data per clause | 📋 TODO |

### Phase 2: Column Design (Priority 1)

**IS 456 Clauses:** Cl 25.1-25.4 (slenderness), Cl 26.5 (detailing), Cl 39.1-39.8 (design)
**IS 13920 Clauses:** Cl 7.3 (min bars, pt≥0.8%), Cl 7.4 (lap splices in central half), Cl 7.4.8 (confinement at joints)
**SP:16 Charts:** 27-44 (rectangular), 45-50 (circular), 51-62 (P-M interaction)
**Benchmark References:** Pillai & Menon Ch. 13, Ramamrutham Ch. 15, N. Krishna Raju

#### 2.1 Core Types
| File | Addition | Pattern |
|------|----------|---------|
| `core/inputs.py` | `ColumnGeometryInput`, `ColumnLoadsInput` | Match `BeamGeometryInput` (frozen dataclass) |
| `core/data_types.py` | `ColumnResult`, `ColumnInteractionPoint`, `ColumnType` enum | Frozen, with `is_safe()`, `to_dict()`, `summary()` |
| `core/errors.py` | `E_COLUMN_001` through `E_COLUMN_015` | Sub-ranges: 001-019 short, 020-039 slender, 040-059 biaxial |
| `core/validation.py` | `validate_column_dimensions()` | Match `validate_dimensions()` accumulation pattern |

#### 2.2 IS 456 Math
**File:** `Python/structural_lib/codes/is456/column.py`

| Function | IS 456 Clause | Description |
|----------|---------------|-------------|
| `calculate_min_eccentricity` | Cl 39.1 | emin = l/500 + D/30, min 20mm |
| `design_short_column_axial` | Cl 39.3 | Pu,max = 0.4·fck·Ac + 0.67·fy·Asc |
| `design_short_column_uniaxial` | Cl 39.3 + 39.5 | Axial + uniaxial bending via P-M interaction |
| `pm_interaction_curve` | Cl 39.5, Annex G | P-M interaction diagram (balanced, tension, compression) |
| `biaxial_bending_check` | Cl 39.6 | Bresler: (Mux/Mux1)^αn + (Muy/Muy1)^αn ≤ 1.0 |
| `biaxial_linear_check` | Cl 39.6 Note | Linear: Mux/Mux1 + Muy/Muy1 ≤ 1.0 (when Pu/Puz < 0.2) |
| `calculate_additional_moment` | Cl 39.7.1 | Ma = Pu × (l_eff)² / (2000 × D), with convergence check |
| `design_long_column` | Cl 39.7 | Iterative: short column + additional moment until Ma stable |
| `calculate_effective_length` | Cl 25.2, Annex E, Table 28 | Effective length factors for 6 end conditions |
| `check_helical_reinforcement` | Cl 39.8 | Volumetric ratio ρv check |

**Input signature:**
```python
def design_column_is456(
    b_mm: float, D_mm: float, height_mm: float,
    fck: float, fy: float,
    Pu_kN: float, Mux_kNm: float = 0, Muy_kNm: float = 0,
    cover_mm: float = 40, rebar_config: str = 'uniform',
    end_conditions: str = 'pinned-pinned',
    seismic_zone: int = 0,
    method: str = 'bresler',  # 'bresler' | 'linear'
) -> ColumnResult:
```

#### 2.3 Tests
| File | Type | Count | Tolerance |
|------|------|-------|-----------|
| `tests/unit/test_column.py` | Unit | 5 per function (50+) | exact |
| `tests/regression/test_column_sp16.py` | SP:16 benchmark | Charts 27-62 | ±0.1% (uniaxial), ±1% (biaxial) |
| `tests/property/test_column_hypothesis.py` | Property-based | Equilibrium, monotonicity, symmetry | — |
| `tests/data/benchmark_vectors/column_sp16.json` | Reference data | SP:16 chart values | — |
| `tests/integration/test_column_integration.py` | Integration | Column → footing interface | — |

#### 2.4 API + Endpoint
- `services/api.py` → `design_column_is456()` (follow `design_beam_is456()` pattern)
- `__init__.py` → re-export `design_column_is456`
- `fastapi_app/routers/column.py` → `POST /api/v1/design/column`
- `Python/examples/column_design.py` — minimal + professional workflows

### Phase 3: Footing Design (Priority 2) — Moved up from P3

**Rationale:** Simpler than slabs, directly uses column output for loads/dowels.

**IS 456 Clauses:** Cl 34.1.1-34.4, Cl 31.6.1-31.6.3.1
**IS 13920 Clauses:** Cl 10 (dowels from footing into column)
**Benchmark References:** Pillai & Menon Ch. 14, Bowles

| Function | IS 456 Clause | Description |
|----------|---------------|-------------|
| `design_isolated_footing` | Cl 34 | Rectangular/square footing design |
| `punching_shear_check` | Cl 31.6.1-31.6.3.1 | Critical perimeter at d/2 from column face |
| `one_way_shear_check` | Cl 34.2.4.1 | One-way shear at d from column face |
| `calculate_bearing_pressure` | Cl 34.4 | Column bearing on footing |
| `check_dowel_bars` | Cl 34.2.5 | Min 0.5% of column area, min 4-12mm |

**Key parameters:**
- `location='internal' | 'edge' | 'corner'` for punching shear perimeter
- `cover_mm=75` (soil contact — higher than column/beam)
- `sbc_kN_m2` (safe bearing capacity)
- ks enhancement factor: ks = 0.5 + βc ≤ 1.0

**Tolerances:** Flexure ±0.1%, Punching shear ±0.5%

### Phase 4: Slab Design (Priority 3) — Moved down from P2

#### 4.1 One-Way Slab
**IS 456 Clauses:** Cl 24.1-24.5, Cl 26.5.2.1
**SP:16 Charts:** 1-26 (same as beam flexure)
**Benchmark:** Pillai & Menon Ch. 9, Varghese

| Function | Clause | Description |
|----------|--------|-------------|
| `design_oneway_slab` | Cl 24 | Main design (flexure + shear per meter width) |
| `calculate_distribution_steel` | Cl 26.5.2.1 | 0.12% gross area, max 5D or 450mm spacing |
| `check_slab_deflection` | Cl 23.2, Table 23 | Span/depth ratio check |
| `calculate_min_slab_thickness` | Cl 24.2 | From span/depth tables |

#### 4.2 Two-Way Slab
**IS 456 Clauses:** Cl 24, Annex D-1.1 to D-2
**Tables:** Table 26 (αx, αy positive), Table 27 (αx', αy' negative), Table 28 (βx, βy shear)
**Benchmark:** Pillai & Menon Ch. 10, Park & Gamble (yield line)

| Function | Clause | Description |
|----------|--------|-------------|
| `design_twoway_slab` | Cl 24, Annex D | Two-way slab design |
| `moment_coefficients` | Table 26, 27 | αx, αy for positive; αx', αy' for negative moments |
| `shear_coefficients` | Table 28 | βx, βy |
| `torsion_reinforcement` | Annex D-1.8 | At corners only (not continuous edges) |
| `yield_line_analysis` | IS 456 Commentary | Upper-bound theorem (optional method) |

**Key:** `method='elastic' | 'yield_line'` parameter.
**Tolerances:** Elastic ±0.1%, Yield line ±5%

### Phase 5: Staircase & Shear Wall (Priority 4)

#### 5.1 Staircase
**IS 456 Clauses:** Cl 33.1-33.4 | **No SP:16 charts — use textbook examples**
**Benchmark:** Pillai & Menon Ch. 11, Ramamrutham Ch. 14

| Function | Clause | Description |
|----------|--------|-------------|
| `design_waist_slab_staircase` | Cl 33 | Waist slab type |
| `design_dog_legged` | Cl 33 | Dog-legged staircase |
| `calculate_effective_span` | Cl 33.1, 33.2 | Horizontal vs. inclined spanning |
| `check_landing_torsion` | Cl 33.4 | Torsion at landings |

**Tolerance:** ±1%

#### 5.2 Shear Wall
**IS 456 Clauses:** Cl 32.1-32.5.1 | **IS 13920:** Cl 9.1-9.4
**Benchmark:** Paulay & Priestley, Jain & Murty (IS 13920)

| Function | Clause | Description |
|----------|--------|-------------|
| `design_shear_wall` | Cl 32 | Wall under lateral loads |
| `interaction_check` | Cl 32.3 | Axial + moment interaction |
| `check_boundary_elements` | IS 13920 Cl 9.1 | Required when M/(Vd) > 1.5 |
| `design_boundary_element` | IS 13920 Cl 9.2-9.4 | Confinement rules (same as columns) |

**Tolerance:** ±2%

### Phase 6: Cross-Cutting Quality Infrastructure

#### 6.1 Debug, Trace & Quality Infrastructure

##### Build NOW (Phase 1)

| System | File(s) | Description |
|--------|---------|-------------|
| `core/numerics.py` | New file | `safe_divide()`, `approx_equal()`, `clamp()`, epsilon constants. Consolidate existing `_clamp` from `report_svg.py` and division guard from `utilities.py` |
| `recovery` field on `DesignError` | `core/errors.py` | Non-breaking optional field: machine-actionable recovery hints (e.g., `"USE_DOUBLY_REINFORCED"`, `"INCREASE_SECTION"`) |
| Stack trace sanitization | `fastapi_app/main.py` | Catch-all `@app.exception_handler(Exception)` — never leak internal paths to clients (OWASP security fix) |
| `X-Process-Time` middleware | `fastapi_app/main.py` | Already declared in CORS `expose_headers` but not computed. Add `time.perf_counter()` middleware |
| Unit plausibility guards | `services/api.py` | `assert_unit_mm()`, `assert_unit_mpa()`, `assert_unit_kn()` — catch #1 user mistake (passing meters instead of mm) |
| Hardcoded safety factors | `codes/is456/common/constants.py` | `GAMMA_CONCRETE = 1.5`, `GAMMA_STEEL = 1.15` — NEVER user-configurable parameters |
| Clause coverage CI | `scripts/check_clause_coverage.py` | Verify all required IS 456 clauses have implementing functions. Exit 1 on gaps |
| Element completeness CI | `scripts/check_new_element_completeness.py` | Verify new modules have types + math + tests + API + docs |

##### Build with Column (Phase 2 — pulled by need, not pushed)

| System | File(s) | Trigger |
|--------|---------|---------|
| `DesignTrace` context manager | `core/trace.py` | Column P-M iteration needs step-by-step logging |
| `IterationLog` for convergent methods | `core/trace.py` | Slender column Ma iteration needs convergence monitoring |
| Design context propagation | `core/context.py` | Batch column processing needs beam_id/story tracking |
| Structured JSON logging | `core/logging_config.py` | Production debugging of batch API calls |

##### DesignTrace Pattern (Phase 2 implementation reference)

```python
# core/trace.py — build when column P-M iteration needs it
@dataclass
class CalcStep:
    function: str        # e.g. "calculate_mu_lim"
    clause: str          # e.g. "38.1"
    label: str           # e.g. "Limiting moment capacity"
    expression: str      # e.g. "Mu_lim = 0.36 × (xu_max/d) × [1 - 0.42×(xu_max/d)] × b×d²×fck"
    variables: dict      # e.g. {"xu_max_d": 0.48, "fck": 25, "b": 300, "d": 450}
    result: float        # e.g. 165.68
    unit: str = ""       # e.g. "kN·m"

@dataclass
class DesignTrace:
    steps: list[CalcStep] = field(default_factory=list)
    timings: dict[str, float] = field(default_factory=dict)

    def to_report(self) -> str:
        """Human-readable calculation sheet (like ETABS/RISA output)."""
        ...

    def to_dict(self) -> list[dict]:
        """Machine-readable for JSON export."""
        ...

# Thread-local storage: zero overhead when tracing disabled
@contextmanager
def trace_design():
    """Usage:
        with trace_design() as trace:
            result = design_beam_is456(...)
        print(trace.to_report())
    """
```

**Why tracing matters professionally:** When a government reviewer asks "show me how you got Mu_lim = 165.5 kN·m," the engineer exports a calculation sheet that mirrors IS 456 Cl 38.1 worked examples in SP:16. ETABS, RISA, and SAFE all provide this capability.

##### IterationLog Pattern (Phase 2 implementation reference)

```python
@dataclass
class IterationLog:
    method: str                   # e.g. "slender_column_ma_iteration"
    max_iterations: int = 20
    tolerance: float = 0.001      # 0.1% relative change
    records: list[IterationRecord] = field(default_factory=list)

    @property
    def converged(self) -> bool: ...
    @property
    def iterations_used(self) -> int: ...
```

Critical for column P-M interaction diagrams and slender column Ma iteration. Non-convergence must use the **last (largest) value** as the conservative default — never silently return an unconverged underestimate.

#### 6.2 User-Facing Deliverables
- One example per element: minimal → professional → batch
- Cookbook with scenario-based recipes
- 5-minute quickstart CLI demo
- Validation report generator (`scripts/generate_validation_report.py`)

#### 6.3 API Documentation Overhaul
- Sphinx + autodoc for auto-generated API reference
- Per-function parameter tables, return types, error codes, clause refs
- Hosted on GitHub Pages

#### 6.4 Stub Cleanup
- Apply `@deprecated` decorator to 50+ stubs (target v0.25 removal)
- Migration guide `docs/guides/migration-to-v1.md`

#### 6.5 Combined Loading Helpers
```python
def apply_load_factors(DL_kN, LL_kN, WL_kN=0, EQ_kN=0,
                       combination='DL+LL') -> float:
    """Apply IS 456 Cl 36.4 load factors."""
```

#### 6.6 Durability Validation
```python
def validate_durability(cover_mm, fck, exposure='moderate') -> list[DesignError]:
    """Validate IS 456 Cl 21, Table 16/16A requirements."""
```

#### 6.7 Cross-Element Error Codes
- `E_DESIGN_001-099` for multi-element failures (v0.25+)
- Example: `E_DESIGN_001` — "Column reaction exceeds footing bearing capacity"

---

## 5. IS 456 Clause Coverage Matrix

### Currently Covered (beam design)
| Clause | Topic | Coverage |
|--------|-------|----------|
| Cl 5-6 | Materials, concrete properties | Partial |
| Cl 21 | Durability | Partial |
| Cl 23 | Effective span | Good |
| Cl 26 | Detailing requirements | 30+ subclauses |
| Cl 36 | Limit state design | Partial |
| Cl 38 | Flexure | ✅ Complete |
| Cl 40 | Shear | ✅ Good (5 entries) |
| Cl 41 | Torsion | ✅ Good (6 entries) |
| Cl 43 | Serviceability | ✅ Good |

### Must Add for Expansion (~66 subclauses)
| Clause Group | Topic | Subclauses | For Element |
|-------------|-------|------------|-------------|
| Cl 24.1-24.5 | Slabs | ~10 | Slab |
| Annex D-1.1 to D-2 | Two-way slabs | ~10 | Slab (two-way) |
| Cl 25.1-25.4 | Compression member slenderness | ~5 | Column |
| Cl 31.6.1-31.6.3.1 | Punching shear | ~4 | Footing, Slab |
| Cl 32.1-32.5.1 | Shear walls | ~6 | Shear Wall |
| Cl 33.1-33.4 | Staircases | ~4 | Staircase |
| Cl 34.1.1-34.4 | Footings | ~10 | Footing |
| Cl 39.1-39.8 | Column design | ~12 | Column |
| IS 13920 Cl 5-10 | Seismic ductile detailing | ~15 | All elements |
| **Total** | | **~66+** | |

---

## 6. IS 13920 Seismic Provisions

**Cross-cutting concern — applies to ALL elements when `seismic_zone > 0`.**

| Element | IS 13920 Clauses | Critical Requirements |
|---------|------------------|----------------------|
| **Beam** | Cl 6.2, 6.3 | Top/bottom 2-12mm continuous, confining near plastic hinges |
| **Column** | Cl 7.3, 7.4, 7.4.8 | Min 4 bars, pt≥0.8%, lap in central half only, confinement at joints |
| **Slab** | Cl 5 | Integrity reinforcement across supports |
| **Footing** | Cl 10 | Dowels from footing into column |
| **Shear Wall** | Cl 9.1-9.4 | Boundary elements when M/(Vd)>1.5, confinement |
| **Beam-Column Joint** | Cl 8 | Shear reinforcement across joint face |

**Implementation:** `seismic_zone: int = 0` parameter on all design functions. When > 0, automatically apply IS 13920 checks and append results.

---

## 7. Module Pattern (template for every new element)

```python
# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       <element>
Description:  <Element> design per IS 456:2000
Traceability: Functions decorated with @clause for IS 456 references.
"""
from __future__ import annotations
import math

from structural_lib.codes.is456.traceability import clause
from structural_lib.codes.is456.common import stress_blocks, reinforcement
from structural_lib.core.data_types import <Element>Result
from structural_lib.core.errors import E_<ELEMENT>_001, DimensionError
from structural_lib.core.validation import validate_<element>_dimensions, validate_materials

__all__ = ["design_<element>", ...]

@clause("XX.X")
def design_<element>(
    b_mm: float, D_mm: float, fck: float, fy: float, ...
) -> <Element>Result:
    """Design <element> per IS 456 Cl. XX.X.

    Args:
        b_mm: Width (mm).
        D_mm: Depth (mm).
        fck: Concrete strength (N/mm²).
        fy: Steel yield strength (N/mm²).

    Returns:
        <Element>Result with is_safe(), to_dict(), summary() methods.
    """
    errs = validate_<element>_dimensions(b=b_mm, D=D_mm)
    errs += validate_materials(fck=fck, fy=fy)
    if any(e.severity == Severity.ERROR for e in errs):
        return <Element>Result(errors=tuple(errs), ...)

    # IS 456:2000 Cl. XX.X formula
    xu_max = stress_blocks.calculate_xu_max(fck, fy)
    ...
    return <Element>Result(errors=tuple(errs), ...)
```

**Key rules:**
- `@dataclass(frozen=True)` on all result types
- `tuple` not `list` for error collections
- Import shared math from `codes/is456/common/`
- No I/O, no imports from services/ or UI
- All units explicit in parameter names

---

## 8. Units Convention (non-negotiable)

| Quantity | Unit | Param Pattern | Example |
|----------|------|---------------|---------|
| Width/depth | mm | `b_mm`, `D_mm`, `d_mm` | `b_mm=300` |
| Length/span/height | mm | `span_mm`, `height_mm` | `height_mm=3000` |
| Concrete strength | N/mm² | `fck` | `fck=25` |
| Steel strength | N/mm² | `fy` | `fy=415` |
| Moment | kNm | `Mu_kNm`, `Mux_kNm` | `Mu_kNm=150` |
| Shear/axial load | kN | `Vu_kN`, `Pu_kN` | `Pu_kN=1000` |
| Area | mm² | `Ast_mm2` | `Ast_mm2=1256.6` |
| Stress | N/mm² | `tau_v`, `sigma_c` | `tau_v=1.2` |
| Bearing capacity | kN/m² | `sbc_kN_m2` | `sbc_kN_m2=150` |
| Load per area | kN/m² | `DL_kN_m2` | `DL_kN_m2=5` |

---

## 9. Error Code Convention

### Naming: `E_<CATEGORY>_<NNN>`

| Element | Code Range | Example |
|---------|------------|---------|
| Input (general) | `E_INPUT_001-019` | `E_INPUT_001` (b must be > 0) |
| Input (column) | `E_INPUT_020-039` | `E_INPUT_020` (column height) |
| Input (slab) | `E_INPUT_040-059` | `E_INPUT_040` (span ratio) |
| Input (footing) | `E_INPUT_060-079` | `E_INPUT_060` (bearing capacity) |
| Input (reserved) | `E_INPUT_080-099` | — |
| Flexure | `E_FLEXURE_001-099` | `E_FLEXURE_001` (Mu exceeds Mu_lim) |
| Shear | `E_SHEAR_001-099` | `E_SHEAR_001` (tv exceeds tc_max) |
| Torsion | `E_TORSION_001-099` | `E_TORSION_001` (equivalent shear) |
| Ductile | `E_DUCTILE_001-099` | `E_DUCTILE_001` (width < 200mm) |
| **Column** | `E_COLUMN_001-019` (short) | `E_COLUMN_001` (section too slender) |
| **Column** | `E_COLUMN_020-039` (slender) | `E_COLUMN_020` (Ma exceeds capacity) |
| **Column** | `E_COLUMN_040-059` (biaxial) | `E_COLUMN_040` (Bresler > 1.0) |
| **Slab** | `E_SLAB_001-099` | `E_SLAB_001` (span/depth ratio) |
| **Footing** | `E_FOOTING_001-099` | `E_FOOTING_001` (punching shear) |
| **Staircase** | `E_STAIR_001-099` | `E_STAIR_001` (waist too thin) |
| **Shear Wall** | `E_WALL_001-099` | `E_WALL_001` (boundary element) |
| **Cross-element** | `E_DESIGN_001-099` | `E_DESIGN_001` (column exceeds footing) |

**Rule:** Reserve codes 080-099 in each category for future expansion.

---

## 10. Test Requirements Per Element

### Element-Specific Tolerances

| Element | Benchmark Source | Tolerance | Rationale |
|---------|-----------------|-----------|-----------|
| Column (uniaxial) | SP:16 Charts 27-62 | ±0.1% | Digitally precise charts |
| Column (biaxial) | Pillai & Menon examples | ±1% | Bresler is empirical |
| Slab (elastic) | IS 456 Table 26/27 | ±0.1% | Exact coefficients |
| Slab (yield line) | Park & Gamble examples | ±5% | Upper-bound theorem |
| Footing (flexure) | Pillai & Menon Ch. 14 | ±0.1% | Same as beam flexure |
| Footing (punching) | Pillai & Menon Ch. 14 | ±0.5% | τc table interpolation |
| Staircase | Pillai & Menon Ch. 11 | ±1% | No SP:16 charts |
| Shear wall | Paulay & Priestley | ±2% | No SP:16 charts |

### Test Categories (mandatory per element)

| Category | Requirement | Tool |
|----------|-------------|------|
| Unit tests | ≥5 per public function (normal, boundary, edge, error, min/max) | pytest |
| SP:16 / textbook benchmarks | Element-specific tolerances (see above) | `tests/regression/` |
| Property tests | Equilibrium, capacity monotonicity, symmetry, reinforcement bounds | Hypothesis |
| Golden vectors | JSON reference data with source citation | `tests/data/` |
| Error path tests | Every `E_*` code has at least one test triggering it | pytest |
| Parametrize | Grades (M20-M40 × Fe250-Fe550), boundary conditions, load cases | `@pytest.mark.parametrize` |
| Integration | Cross-element interface tests (Phase 3+) | `tests/integration/` |
| Coverage | ≥85% branch coverage per module | pytest-cov |

### Property Test Examples
```python
# Equilibrium: For any column, C + T = P
# Monotonicity: Increasing fck should never decrease capacity
# Symmetry: Square column swapping Mux/Muy should swap results
# Bounds: 0.8% ≤ pt ≤ 6% per IS 456
```

---

## 11. Non-Functional Requirements

### Performance Targets

| Operation | Target | Measurement |
|-----------|--------|-------------|
| Single beam design | <50ms | pytest-benchmark on CI machine |
| Single column design | <100ms | Includes P-M interaction curve |
| Single slab design | <50ms | Per meter width |
| 100-element batch | <5s | multiprocessing.Pool |
| CSV parse (10k rows) | <2s | File I/O bound |
| 3D geometry (1000 beams) | <500ms | React rendering requirement |

### Degradation Policy
- **Acceptable:** <20% slower than beam for same-complexity element
- **Review required:** 20-50% slower (optimize before release)
- **Blocks release:** >50% slower

### Batch Processing (Phase 6+)
```python
def design_columns_batch(inputs: list[ColumnInput]) -> list[ColumnResult]:
    """Batch column design with parallel processing."""
    with Pool() as pool:
        return pool.map(_design_column_worker, inputs)
```
- Streaming for 10k+ elements (yield results, don't accumulate)
- Memory-bounded: process in chunks of 1000

---

## 12. User Experience & Usability

### 12.1 Installation & Quickstart

```bash
pip install structural-lib-is456
structural-lib-demo              # Run demo design → confirms installation works
```

**README quickstart block:**
```python
from structural_lib import design_beam_is456, design_column_is456

beam = design_beam_is456(b_mm=300, d_mm=450, D_mm=500, fck=25, fy=415, Mu_kNm=150)
print(beam.summary())  # "Beam ✓ SAFE: Ast=1256 mm²"

column = design_column_is456(b_mm=300, D_mm=300, height_mm=3000,
                              fck=25, fy=415, Pu_kN=1000, Mux_kNm=50)
print(column.summary())  # "Column ✓ SAFE: Ast=2412 mm²"
```

### 12.2 Validation Pack (for practicing engineers)

**Script:** `scripts/generate_validation_report.py`
**Output:** `docs/for-engineers/validation-pack/validation-report.md`

Contents:
- Library version, validation date, Python version
- IS 456:2000 clauses covered (with clause numbers)
- SP:16 charts verified (list all, with ±0.1% tolerance results)
- Benchmark sources (Pillai & Menon, Ramamrutham references)
- Test pass rate: "All 3000+ tests passed on [date]"

**Why:** Engineers need audit trails. Clients/managers need proof the library is accurate.

### 12.3 Cookbook (scenario-based recipes)

Location: `docs/cookbook/`

| Recipe | Scenario | Clauses |
|--------|----------|---------|
| 01 | Simply supported beam | Cl 38, 40, 26 |
| 02 | Cantilever beam | Cl 22.4.2, 38, 40 |
| 03 | Continuous beam (3-span) | Cl 38, 40, 22.5 |
| 04 | T-beam | Cl 23.1, 38 |
| 05 | Short column (uniaxial) | Cl 39.3, 39.5 |
| 06 | Slender column (biaxial) | Cl 39.6, 39.7 |
| 07 | Isolated footing | Cl 34, 31.6 |
| 08 | One-way slab | Cl 24, 23.2 |
| 09 | Two-way slab | Annex D, Table 26 |
| 10 | CSV batch design (50 beams) | — |

### 12.4 Common Engineer Mistakes (validation must catch)

| Mistake | Impact | Validation |
|---------|--------|------------|
| Cover < min per exposure condition | Durability failure | `validate_durability()` |
| fck < min for exposure (severe → fck≥30) | IS 456 Cl 21 violation | `validate_durability()` |
| Column d'/D > 0.15 | SP:16 charts invalid | `validate_column_dimensions()` |
| Footing projection < column dimension | Bearing failure | `validate_footing_dimensions()` |
| Two-way slab Lx/Ly > 2.0 | Should be designed as one-way | `validate_slab_geometry()` |
| Slenderness λ > 60 | Section inadequate | `validate_column_slenderness()` |
| Dowel bars < 0.5% column area | IS 456 Cl 34.2.5 violation | `check_dowel_bars()` |
| Seismic zone > 0 without IS 13920 | Non-compliant | Automatic when `seismic_zone > 0` |

### 12.5 Sensible Defaults

| Parameter | Default | Rationale |
|-----------|---------|-----------|
| `fck`, `fy` | **No default** — must be explicit | Safety-critical parameters |
| `cover_mm` (beam/column) | 40 mm | IS 456 Table 16 (moderate exposure) |
| `cover_mm` (footing) | 75 mm | Soil contact |
| `cover_mm` (slab) | 25 mm | IS 456 Table 16 (mild exposure) |
| `exposure` | `'moderate'` | Most common in Indian construction |
| `seismic_zone` | 0 (non-seismic) | Safe default, warn if relied upon |
| `end_conditions` | `'pinned-pinned'` | Conservative assumption |
| `support_type` (slab) | `'simply_supported'` | Conservative |

**Rule:** Never default `fck` or `fy`. Log WARNING when user relies on cover/exposure defaults.

---

## 13. Maintenance Playbook

### How to Add a New Error Code

1. Define in `Python/structural_lib/core/errors.py`:
   ```python
   E_COLUMN_005 = DesignError(
       code="E_COLUMN_005", severity=Severity.ERROR,
       message="Column slenderness exceeds λ_max",
       field="slenderness_ratio",
       hint="Increase section size or reduce effective length",
       clause="IS 456 Cl 25.1.2"
   )
   ```
2. Add test that triggers it in `tests/unit/test_column_errors.py`
3. Regenerate: `.venv/bin/python scripts/generate_error_docs.py`
4. Commit: `./scripts/ai_commit.sh "feat(column): add E_COLUMN_005"`

### How to Add a New CI Check

1. Create script: `scripts/check_<thing>.py` (exit 0 = pass, exit 1 = fail)
2. Test locally: `.venv/bin/python scripts/check_<thing>.py`
3. Add to `scripts/check_all.py` in the relevant category
4. Add to `.github/workflows/fast-checks.yml` (if <10s) or `python-tests.yml` (if >10s)
5. Register in `scripts/automation-map.json`
6. Verify: `./run.sh check`

### How to Deprecate a Function

1. Add `@deprecated("v0.X", "Use new_function instead")` decorator
2. Update docstring: `.. deprecated:: 0.X`
3. Add to CHANGELOG under "Deprecated"
4. Wait ≥2 versions or ≥6 months (whichever is longer)
5. Remove function, update API manifest: `check_api_compat.py --update`
6. Bump MINOR version, add migration guide

### How to Handle a Security Vulnerability

**Internal (in structural_lib code):**
1. Fix immediately (P0 interrupt — security trumps features)
2. Write regression test
3. Bump PATCH version, tag release
4. Publish to PyPI
5. GitHub Security Advisory if public

**External (in a dependency):**
1. Check Dependabot alert
2. Auto-fix available → merge PR
3. Breaking change required → test locally, then merge
4. No fix available → pin to last safe version, warn users, monitor

### Regular Audit Schedule

| Frequency | Task | Command |
|-----------|------|---------|
| Weekly | Archive stale docs | `./scripts/archive_old_files.sh` |
| Weekly | Check broken links | `.venv/bin/python scripts/check_links.py` |
| Weekly | Health score | `./run.sh health` |
| Monthly | Dependency updates | `pip list --outdated` |
| Monthly | Security audit | `bandit -r Python/structural_lib/` |
| Quarterly | Performance benchmarks | `pytest --benchmark-compare` |
| Quarterly | Review metrics trends | `./scripts/generate_metrics_report.py` |
| Yearly | License compliance | `pip-licenses --fail-on="GPL,LGPL,AGPL"` |

---

## 14. Security Considerations

### Input Sanitization
- All public API functions MUST call `validate_*()` before calculation
- No raw user input reaches core math modules
- Numeric bounds: dimensions 1-100,000 mm, stresses 1-1000 N/mm²

### DoS Protection (FastAPI)
- Rate limiting: 100 requests/minute per IP (recommended)
- CSV import: max 10,000 rows
- Batch design: max 1,000 elements per request
- 3D geometry: max 1,000 beams per building
- Document limits in API reference

### Dependency Security
- Dependabot enabled ✅
- Add: `bandit` scan in CI (Python security audit)
- Add: `pip-licenses --fail-on="GPL,LGPL,AGPL"` (license compliance)

### API Authentication
- Pre-v1.0: Unauthenticated (internal/demo use)
- v1.0+: Optional API keys for production deployments

---

## 15. Documentation Strategy

### Audience Segmentation

| Audience | Entry Point | Key Docs |
|----------|-------------|----------|
| **Structural Engineers** | README → quickstart | Cookbook, validation pack, IS 456 compliance |
| **Python Developers** | README → developer guide | Architecture, API ref, contributing guide |
| **API Consumers** | `/docs` (OpenAPI) | REST reference, error codes, Pydantic schemas |

### Planned Documentation Structure
```
docs/
├── for-engineers/              # User-facing
│   ├── quickstart.md           # 5-min first design
│   ├── cookbook/                # Scenario recipes
│   ├── validation-pack/        # SP:16 verification results
│   └── is456-compliance.md     # Clause coverage report
├── for-developers/             # Contributor-facing
│   ├── architecture.md         # 4-layer model
│   ├── adding-features.md      # Module creation guide
│   └── testing-best-practices.md
├── api-reference/              # Auto-generated
│   ├── python-api.md           # Sphinx autodoc
│   ├── rest-api.md             # FastAPI endpoints
│   └── error-codes.md          # Auto-generated
└── governance/                 # Project operations
    ├── maintenance-playbook.md
    ├── versioning-policy.md
    └── succession-plan.md
```

### Auto-Generation
- **Error codes:** `scripts/generate_error_docs.py` → `error-codes.md`
- **API reference:** Sphinx autodoc (Phase 6.3)
- **Validation report:** `scripts/generate_validation_report.py` (Phase 6.2)

---

## 16. Governance

### Governance Model
- **Model:** BDFL (Pravin Surawase) with merit-based committer access
- **Architecture decisions:** Pravin only
- **Non-breaking features:** Committers with review
- **Multi-code support (ACI, EC2):** Requires consensus

### Versioning Policy (SemVer 2.0)

**Before v1.0 (current: Alpha):**
- `MAJOR`: Reserved for v1.0 launch
- `MINOR`: Breaking changes, new elements, major features
- `PATCH`: Bug fixes, non-breaking improvements, docs

**Breaking Change Definition:**
- ❌ Breaking: Remove/rename public function, rename parameter, change return type, change units
- ✅ Non-breaking: Add optional parameter with default, add new function, add new fields to result

**Deprecation Cycle:**
1. v0.X: Mark with `@deprecated("0.Y", "Use new_function")`
2. v0.Y: Emits `DeprecationWarning` (still works)
3. v0.Z (≥2 versions later, ≥6 months): Remove, document in migration guide

### PR Acceptance Criteria
- ✅ Follows 4-layer architecture (`check_architecture_boundaries.py` passes)
- ✅ Includes SP:16/textbook benchmarks for new math (element-specific tolerance)
- ✅ Has `@clause` decorator with IS 456 references
- ✅ No breaking changes without deprecation cycle
- ✅ Tests pass (`./run.sh test`)
- ✅ Architecture check passes (`./run.sh check --quick`)

### Succession Plan Outline
- Document emergency contacts in `docs/governance/succession-plan.md`
- Add 2nd CODEOWNER as backup reviewer
- Credential recovery process documented (password manager, GPG keys)
- "If maintainer unavailable 14+ days" protocol

---

## 17. Agent Pipeline (per element)

```
orchestrator      → scope, identify files, assign
structural-eng    → IS 456 clause research, formula validation, benchmark values
structural-math   → core types + IS 456 math (frozen dataclass + @clause)
tester            → unit + regression + property + integration tests
reviewer          → architecture check + IS 456 verification (MANDATORY GATE)
backend           → services/api.py wiring + __init__.py exports
api-developer     → FastAPI router + Pydantic models
frontend          → React hook + component (future phase)
doc-master        → API docs, WORKLOG, error-codes.md, cookbook recipe
ops               → commit + PR via ai_commit.sh
```

### Agent Scalability Decision
- **12 agents constant** — no new per-element agents
- `structural-math` handles ALL IS 456 modules (beam, column, slab, etc.)
- Element specialization via **prompts** (cheap), not agents (expensive)
- Create `prompts/add-column.prompt.md`, `prompts/add-slab.prompt.md`, etc.

### Agent Instruction Updates Per Element
When adding a new element, update these 5 files:
1. `.github/agents/structural-math.agent.md` — add element to module list
2. `.github/agents/backend.agent.md` — add to API wiring checklist
3. `.github/skills/new-structural-element/SKILL.md` — add element example
4. `.github/prompts/add-structural-element.prompt.md` — update template
5. `docs/getting-started/agent-bootstrap.md` — update "What the library covers"

---

## 18. CI/CD Quality Gates

| Gate | Threshold | Script | When |
|------|-----------|--------|------|
| Test coverage | ≥85% branch | `pytest --cov` | Every commit |
| API compat | No breaking changes | `check_api_compat.py` | Every commit |
| Architecture | No import violations | `check_architecture_boundaries.py` | Every commit |
| Imports | No broken imports | `validate_imports.py` | Every commit |
| Benchmarks | Element-specific tolerances | Regression tests | Every commit |
| Error docs | Up-to-date | `generate_error_docs.py --check` | Every commit |
| Element completeness | Tests + examples + API for new modules | `check_new_element_completeness.py` | Every commit |
| Performance | <2× baseline | `pytest --benchmark-compare` | Weekly |
| License compliance | No GPL/LGPL/AGPL | `pip-licenses` | Weekly |
| Security audit | No high-severity findings | `bandit -r structural_lib/` | Weekly |
| Health score | ≥80 | `./run.sh health` | Weekly |

### New CI Check: Element Completeness
**Script:** `scripts/check_new_element_completeness.py`

For each module in `codes/is456/`:
- ✅ Has corresponding `tests/unit/test_<element>.py`
- ✅ Has corresponding `tests/regression/test_<element>_benchmark.py`
- ✅ Has error codes `E_<ELEMENT>_*` in `core/errors.py`
- ✅ Has API entry point in `services/api.py`
- ✅ Has example in `Python/examples/`

---

## 19. Decisions Log

| # | Decision | Rationale | Date |
|---|----------|-----------|------|
| D1 | IS 456 only (no ACI/EC2 yet) | Complete one code suite before branching | 2026-03-29 |
| D2 | Infrastructure first (Phase 1) before new elements | Prevents tech debt accumulation | 2026-03-29 |
| D3 | Flat module structure (column.py, not column/column.py) | Matches existing flexure.py, shear.py | 2026-03-29 |
| D4 | SP:16 as primary benchmark where available | Authoritative IS 456 reference | 2026-03-29 |
| D5 | API-first, React UI later | Keeps scope manageable per element | 2026-03-29 |
| D6 | One element fully done before starting next | Complete = types + math + tests + API + docs | 2026-03-29 |
| D7 | Production-grade (not full enterprise) | Structured logging, CI gates, version contracts | 2026-03-29 |
| D8 | Never default fck/fy | Safety-critical — engineers MUST specify | 2026-03-29 |
| D9 | Flat api.py with __init__.py re-exports | `from structural_lib import design_column_is456` works | 2026-03-29 |
| D10 | No breaking changes in minor versions | Pre-1.0 exception: with deprecation + migration guide | 2026-03-29 |
| D11 | Element order: Column → Footing → Slab → Staircase → Shear Wall | Structural dependency + complexity ordering | 2026-03-29 |
| D12 | IS 13920 is cross-cutting, not per-element | `seismic_zone` param triggers checks automatically | 2026-03-29 |
| D13 | 12 agents constant, specialization via prompts | Prompts are cheap, agents are expensive to maintain | 2026-03-29 |
| D14 | All results frozen=True with is_safe(), to_dict(), summary() | Immutable, thread-safe, consistent API | 2026-03-29 |
| D15 | Element-specific benchmark tolerances | Biaxial ±1%, yield line ±5% — not blanket ±0.1% | 2026-03-29 |
| D17 | Partial safety factors hardcoded (γc=1.5, γs=1.15) | Safety-critical — never user-configurable. Future multi-code via `DesignCode` object, not function params | 2026-03-30 |
| D18 | Build quality infrastructure on-demand, not in advance | DesignTrace, CAUTION severity, contextvars — wait for column P-M to pull them | 2026-03-30 |
| D19 | No `@finite_result` decorator — use inline NaN/Inf checks per §23 | Decorator hides control flow; inline checks are more visible and already mandated | 2026-03-30 |
| D20 | No new `CAUTION` severity level — use WARNING with subcategory field instead | CAUTION would break existing API consumers parsing severity values | 2026-03-30 |
| D21 | Unit plausibility guards at Services boundary only, not in core math | Core layer shouldn't know plausible ranges; validation is Services responsibility | 2026-03-30 |
| D22 | Invariant tests merge into existing `tests/property/`, no new directory | Avoid test directory proliferation; `@pytest.mark.invariant` → `@pytest.mark.property` | 2026-03-30 |
| D23 | Recovery field on DesignError is additive (non-breaking), build now | Machine-actionable hints enable auto-fix in smart_analyze_design() and batch pipeline | 2026-03-30 |

---

## 20. Version Roadmap

| Version | Focus | Target | Confidence | Key Deliverables |
|---------|-------|--------|------------|------------------|
| **v0.21** | Phase 1 cleanup + Column types/math | Q2 2026 | High | Foundation cleanup, column.py, unit tests |
| **v0.22** | Column complete + Footing | Q3 2026 | Medium | Column API/endpoint, footing.py, regression tests |
| **v0.23** | Slab (one-way + two-way) | Q4 2026 | Medium | slab.py, moment coefficients, Table 26/27/28 |
| **v0.24** | Staircase + Shear Wall | Q1 2027 | Low | staircase.py, shear_wall.py, IS 13920 Cl 9 |
| **v0.25** | Stub cleanup + API docs + v1.0 prep | Q2 2027 | Low | Remove 50+ stubs, Sphinx docs, validation pack |

**Assumptions:**
- Solo maintainer with AI agents, ~15 hours/week
- Each element: ~40 hours (types + math + tests + API + docs)
- Phase 1 foundation: ~20 hours
- Buffer: 30% for unknowns, CI fixes, user support

**Quarterly Checkpoints:** Assess timeline realism. If behind: cut scope (defer element) or extend timeline.

---

## 21. References

### IS Standards
- IS 456:2000 — Plain and Reinforced Concrete (reaffirmed 2021)
- IS 456:2000 Amendment No. 3 (2019) — Development length clarifications
- IS 13920:2016 — Ductile Detailing for Seismic Resistance
- SP:16 — Design Aids for Reinforced Concrete to IS 456

### Textbooks (benchmark validation sources)

| Element | Primary | Secondary | Tertiary |
|---------|---------|-----------|----------|
| **Column** | Pillai & Menon Ch. 13 | Ramamrutham Ch. 15 | N. Krishna Raju |
| **Slab (one-way)** | Pillai & Menon Ch. 9 | Varghese | Unnikrishna Pillai |
| **Slab (two-way)** | Pillai & Menon Ch. 10 | Park & Gamble | Timoshenko |
| **Footing** | Pillai & Menon Ch. 14 | Bowles | ACI 318 (comparison) |
| **Staircase** | Pillai & Menon Ch. 11 | Ramamrutham Ch. 14 | — |
| **Shear Wall** | Paulay & Priestley | Jain & Murty (IS 13920) | ACI 318 App. B |

### Project Resources
- [structural-math.agent.md](../../.github/agents/structural-math.agent.md) — IS 456 math agent
- [new-structural-element skill](../../.github/skills/new-structural-element/SKILL.md) — Step-by-step workflow
- [add-structural-element prompt](../../.github/prompts/add-structural-element.prompt.md) — Template
- [agent-bootstrap.md](../getting-started/agent-bootstrap.md) — Full project reference

---

## 22. Review History

| Round | Date | Reviewers | Verdict | Key Changes |
|-------|------|-----------|---------|-------------|
| 1 | 2026-03-29 | @structural-engineer (7/10), @reviewer (approved w/ enhancements), @governance (technically excellent, governance-incomplete) | **Approved with 26 enhancements** | Added §3 (architecture), §5-6 (IS 456/13920), §11-16 (NFR, UX, maintenance, security, docs, governance); reordered elements; element-specific tolerances; frozen result types; shared math extraction; Input sub-ranges; 8 new decisions (D8-D15) |

### Open Items from Review Round 1
- [ ] Investigate yield line theory accuracy bounds (structural-engineer)
- [ ] Audit existing FlexureResult for mutable collections (reviewer)
- [ ] Draft succession-plan.md with emergency contacts (governance)
- [ ] Create `scripts/check_new_element_completeness.py` (ops)
- [ ] Create `core/deprecation.py` with @deprecated decorator (backend)
- [ ] Populate clauses.json with 66+ missing subclauses (doc-master)

---

## Definition of Done (per element)

An element is **complete** only when ALL are checked:

- [ ] Core types in `core/inputs.py`, `core/data_types.py` (frozen=True)
- [ ] Error codes in `core/errors.py` (with sub-range allocation)
- [ ] Math module in `codes/is456/<element>.py` with `@clause` decorators
- [ ] Shared math extracted to `codes/is456/common/` (no duplication)
- [ ] Input validation with `validate_<element>_*()` functions
- [ ] Unit tests (≥5 per function, ≥85% branch coverage)
- [ ] Benchmark tests (element-specific tolerance)
- [ ] Property tests (Hypothesis: equilibrium, monotonicity, bounds)
- [ ] Error path tests (every `E_*` code triggered)
- [ ] Parametrized tests (grade × boundary condition matrix)
- [ ] `check_architecture_boundaries.py` clean
- [ ] `validate_imports.py` clean
- [ ] API wiring in `services/api.py`
- [ ] `__init__.py` re-export added
- [ ] FastAPI endpoint created with Pydantic models
- [ ] `ErrorResponse` model documented in OpenAPI
- [ ] Example script (minimal + professional)
- [ ] Cookbook recipe added
- [ ] Error codes in `error-codes.md` (regenerated)
- [ ] API manifest updated
- [ ] `check_new_element_completeness.py` passes
- [ ] WORKLOG.md entry appended
- [ ] IS 13920 checks included (if `seismic_zone` parameter needed)
- [ ] All functions pass numerical precision checks (no NaN/Inf outputs)
- [ ] Unit plausibility guards in `services/api.py` cover new parameters
- [ ] `scripts/check_clause_coverage.py` reports green for new element
- [ ] `scripts/check_new_element_completeness.py` passes
- [ ] Safety flags in result type catch red-flag conditions
- [ ] Degenerate case tests included (zero loads, minimum materials)
- [ ] Monotonicity property tests confirm capacity increases with strength
- [ ] Equilibrium invariant confirmed (C = T for flexure, sum forces = 0)

---

## 23. Numerical Precision & Accuracy

### Float vs Decimal Policy
- Use `float` for all structural calculations (IEEE 754 double precision — 15 significant digits)
- Use `Decimal` only for financial calculations (cost optimization) or accumulating 10,000+ values
- **Never** use `float` equality (`==`). Always: `abs(a - b) < tolerance`

### Rounding Policy for Engineering Output

| Quantity | Round To | Rationale |
|----------|----------|-----------|
| Steel area (Ast, Asc) | 1 mm² | Bar area precision |
| Dimensions (b, D, d) | 1 mm | Construction tolerance |
| Moment capacity (Mu) | 0.01 kNm | Design precision |
| Shear capacity (Vu) | 0.01 kN | Design precision |
| Stress (σ, τ) | 0.01 N/mm² | Material grade resolution |
| Reinforcement ratio (pt) | 0.001% | Engineering convention |
| Deflection | 0.1 mm | Serviceability precision |
| Utilization ratio | 0.001 | Three decimal places |

### Comparison Epsilon Values

```python
# Python/structural_lib/core/constants.py
EPSILON_FORCE = 0.01        # kN — force comparison
EPSILON_MOMENT = 0.01       # kNm — moment comparison
EPSILON_STRESS = 0.01       # N/mm² — stress comparison
EPSILON_DIMENSION = 0.1     # mm — dimension comparison
EPSILON_RATIO = 1e-6        # dimensionless — ratio comparison
EPSILON_XU = 0.001          # mm — neutral axis depth
```

### Convergence Criteria
- Slender column Ma iteration: `|Ma_new - Ma_old| / Ma_old < 0.001` (0.1%)
- P-M curve interpolation: linear between computed points, min 20 points
- Bresler biaxial: convergence not needed (direct formula)

### NaN/Infinity Guards
Every public function MUST check output:
```python
if math.isnan(result) or math.isinf(result):
    raise CalculationError("E_CALC_001", f"Non-finite result: {result}")
```

---

## 24. Professional Use & Liability

### Disclaimer (MUST appear in README, docs, validation pack)

```
PROFESSIONAL USE DISCLAIMER

This library provides structural design calculation tools implementing IS 456:2000.

Users are solely responsible for:
• Independent verification of ALL design results
• Applying professional engineering judgment
• Compliance with local building codes and authority approvals
• Professional liability insurance for their construction projects
• Ensuring designs are reviewed by a licensed structural engineer

This software is provided "as-is" under the MIT license. Authors and
contributors assume NO liability for structural failures, design errors,
construction defects, or any consequences arising from the use of this
library in real construction projects.

This library does NOT constitute BIS certification. For authority submissions,
designs must be verified and signed by a licensed structural engineer.
```

### Where Disclaimer Appears
1. `README.md` — top-level section
2. `docs/for-engineers/quickstart.md` — prominent notice
3. Validation pack PDF — first page
4. API `/health` endpoint — `disclaimer` field in response
5. `structural_lib/__init__.py` — module docstring
6. Every `DesignResult.summary()` output — footer line

---

## 25. Advanced Engineering Provisions (Deferred)

### Documented as Out-of-Scope (v0.26+)

| Provision | IS Code | Priority | Planned Version |
|-----------|---------|----------|-----------------|
| Crack width calculation | IS 456 Annex F | Medium | v0.26 |
| Fire resistance design | IS 456 Cl 21.4, Table 16A | Medium | v0.26 |
| Creep & shrinkage | IS 456 Cl 6.2.4, 6.2.5 | Medium | v0.26 |
| Long-term deflection | IS 456 Cl 23.2 (creep) | Medium | v0.26 |
| Temperature effects | IS 456 Cl 20 | Low | v0.27 |
| Progressive collapse resistance | IS 456 Cl 20.4.1 | Low | v0.27 |
| Wind load calculation | IS 875 Part 3 | Low | v0.27 |
| Earthquake force calculation | IS 1893:2016 | Low | v0.27 |
| Foundation settlement | Geotechnical | Low | v0.28 |
| Construction stage analysis | — | Low | v1.0+ |
| Prestressed concrete | IS 1343 | Low | v1.0+ |
| Multi-story frame analysis | — | Low | v1.0+ |

### Load Combinations (IS 456 Table 18 — stub for Phase 6.5)

```python
# Planned: services/load_combinations.py
LOAD_COMBINATIONS = {
    "LC1": {"name": "1.5DL + 1.5LL", "DL": 1.5, "LL": 1.5},
    "LC2": {"name": "1.5DL + 1.5WL", "DL": 1.5, "WL": 1.5},
    "LC3": {"name": "1.2DL + 1.2LL + 1.2WL", "DL": 1.2, "LL": 1.2, "WL": 1.2},
    "LC4": {"name": "1.5DL + 1.5EQ", "DL": 1.5, "EQ": 1.5},
    "LC5": {"name": "0.9DL + 1.5EQ", "DL": 0.9, "EQ": 1.5},
    "LC6_IS1893": {"name": "1.2DL + 1.2LL ± 1.2EQ", "DL": 1.2, "LL": 1.2, "EQ": 1.2},
}
```

### Durability Module (planned Phase 6.6 — already in blueprint)
Covers: Cl 21 (exposure conditions), Table 3-5 (fck, w/c, cement content)
Missing from current plan: max w/c ratio validation, min cement content, carbonation depth

---

## 26. Extension Architecture Strategy (v1.0+)

### Design Principles for Future Multi-Code Support
- **Phase 1-5:** Design shared math in `codes/is456/common/` for eventual extraction
- **v0.25:** Rename `common/` → `codes/shared/` (code-agnostic helpers)
- **v1.0:** Introduce `BaseDesignCode` abstraction
- **v1.1+:** Add ACI 318, EC2 implementations

### Extension Points to Preserve
```python
# Future: abstract base for all design codes
class BaseDesignCode:
    def stress_block_params(self) -> StressBlockConfig: ...
    def material_safety_factors(self) -> dict: ...
    def minimum_reinforcement(self, element: str) -> float: ...

class IS456Code(BaseDesignCode):
    """IS 456:2000 implementation."""
    ...

class ACI318Code(BaseDesignCode):
    """ACI 318-19 implementation (future)."""
    ...
```

### What NOT to Hard-Code
- Stress block shape (IS 456 uses parabolic-rectangular, ACI uses rectangular)
- Material safety factors (IS 456: γm=1.5 concrete, 1.15 steel; EC2: 1.5, 1.15)
- Minimum reinforcement formulas (differ by code)
- Cover requirements (differ by code and exposure)

### Decision D16: Design for eventual extraction, but don't abstract prematurely

---

## 27. Performance & Caching Strategy

### Caching Policy
```python
from functools import lru_cache

# ✅ DO cache: Pure functions with immutable inputs
@lru_cache(maxsize=256)
def calculate_xu_max(fck: float, fy: float) -> float: ...

@lru_cache(maxsize=128)
def tau_c_table19(fck: float, pt: float) -> float: ...

# ❌ DO NOT cache: Functions with mutable inputs or I/O
def design_beam_is456(...) -> BeamResult: ...  # Too many param combos
```

### Performance Budget Per Function

| Function | Target | Measured (v0.19) | Budget |
|----------|--------|------------------|--------|
| `design_beam_is456()` | <50ms | ~30ms | ✅ |
| `design_column_is456()` | <100ms | — | Phase 2 |
| `design_isolated_footing()` | <50ms | — | Phase 3 |
| `design_oneway_slab()` | <30ms | — | Phase 4 |
| `design_twoway_slab()` | <50ms | — | Phase 4 |
| `pm_interaction_curve()` | <200ms | — | Phase 2 |
| Batch 100 beams | <5s | ~3s | ✅ |
| CSV import 1000 rows | <2s | ~1.5s | ✅ |

### CI Performance Gate
- Weekly: Run `pytest --benchmark-only --benchmark-compare=baseline.json`
- Alert: >20% regression vs previous week
- Block release: >50% regression vs baseline

---

## 28. Test Strategy Enhancements

### Benchmark Vector Creation Workflow

1. **Research** (@structural-engineer) — identify SP:16 charts/textbook examples, document source
2. **Data Entry** (@tester) — digitize into `tests/data/benchmark_vectors/<element>_sp16.json`
3. **Verification** (@structural-engineer + @tester) — independent cross-check by 2nd person
4. **Version Control** — treat benchmark data as code; breaking change = MINOR version bump

**JSON Schema for all benchmark vectors:**
```json
{
  "source": "SP:16 Chart 27, Page 95",
  "isbn": "978-81-7061-009-3",
  "parameters": {"b_mm": 300, "D_mm": 500, "fck": 25, "fy": 415},
  "expected": {"Ast_mm2": 1256.6, "xu_mm": 112.3},
  "tolerance": 0.001,
  "verified_by": "structural-engineer",
  "verified_date": "2026-04-15"
}
```

### Property Test Requirements (all elements)

**Mandatory properties (6 universal):**
1. Equilibrium: internal forces = external loads
2. Monotonicity: increasing capacity params → never decreases capacity
3. Symmetry: symmetric inputs → symmetric outputs
4. Bounds: results within IS 456 limits (0.8% ≤ pt ≤ 6%)
5. Idempotence: `design(design(x).inputs)` stable within tolerance
6. Unit consistency: result units match documented units

**Element-specific:**
- Column: P-M interaction convex, biaxial ≥ uniaxial capacity check
- Slab: two-way approaches one-way as Lx/Ly → 2.0
- Footing: punching perimeter > one-way shear critical section

### Chaos & Boundary Testing

**Location:** `tests/chaos/test_<element>_chaos.py`

Categories per element:
1. **Extreme dimensions** — min/max per IS 456 limits
2. **Extreme materials** — fck=15 (below M20, should ERROR), fck=100, fy=250, fy=600
3. **Extreme loads** — Pu=0 (pure bending), Pu≈Pu_max, Mu≈0
4. **Numerical edge cases** — xu/d = 0.001, Ast at exact min/max
5. **Pathological inputs** — b > D, cover > D/2, negative values

**Rule:** Design functions must NEVER crash. Invalid input → `DesignError`, not `RuntimeError`.

### Regression Test Tiers

| Tier | Frequency | Max Tests | Criteria |
|------|-----------|-----------|----------|
| Tier 1 (critical) | Every commit | 50 | Production bugs, safety-critical |
| Tier 2 (important) | Nightly | 200 | Released version bugs |
| Tier 3 (historical) | Weekly | Unlimited | Older bugs covered by property tests |

### Mutation Testing (Phase 2+)

**Tool:** `mutmut`
**Scope:** `codes/is456/` modules only (pure math)
**Target:** ≥80% mutation score per module
**Frequency:** Weekly CI job
**Critical functions** (`design_*`, `calculate_*`) must be 100% mutation score

### Flaky Test Strategy

- Use `pytest.approx(abs=tolerance)` for ALL float comparisons
- Seed all random generators: `random.seed(42)`
- Mark flaky tests: `@pytest.mark.flaky(reruns=3)` with root cause comment
- Monthly audit: review all `@pytest.mark.flaky`, fix root cause or remove

### Test Environment Matrix

| Python | OS | Frequency |
|--------|----|-----------|
| 3.10 | Ubuntu | Every commit |
| 3.11 | Ubuntu | Every commit |
| 3.12 | Ubuntu, macOS | Weekly |

**Minimum supported:** Python 3.10 (EOL Oct 2026)

---

## 29. Observability & Configuration

### Observability Stack (Phase 6)

```python
# FastAPI Prometheus metrics endpoint
# fastapi_app/metrics.py
from prometheus_client import Counter, Histogram

DESIGN_DURATION = Histogram(
    "design_duration_seconds",
    "Time to complete a design calculation",
    ["element"]  # beam, column, slab, footing
)

VALIDATION_ERRORS = Counter(
    "validation_errors_total",
    "Input validation errors",
    ["error_code"]  # E_INPUT_001, E_COLUMN_005
)
```

### Configuration Module (Phase 1 or v0.25)

```python
# structural_lib/config.py
@dataclass
class LibraryConfig:
    """Global library configuration."""
    default_exposure: str = "moderate"
    log_level: str = "WARNING"
    enable_telemetry: bool = False  # Opt-in only
    precision_digits: int = 4
    max_iterations: int = 100

# Usage: config = LibraryConfig.from_env()
# Override: STRUCTURAL_LIB_EXPOSURE=severe
```

### Telemetry (opt-in only)
- Environment variable: `STRUCTURAL_LIB_TELEMETRY=1` (default: disabled)
- Data collected: function name, parameter types (NOT values), timing, library version
- Privacy: no PII, no design values, no IP addresses
- Destination: self-hosted or disabled entirely

---

## 30. Community & Adoption

### Issue Triage & Support

**Response Time Targets** (best-effort, not SLA):

| Priority | Response | Examples |
|----------|----------|---------|
| P0 (security) | 24 hours | Vulnerability, data corruption |
| P1 (broken) | 72 hours | API breaking, test failures |
| P2 (feature) | 7 days (triage) | New element request, enhancement |
| P3 (minor) | 14 days | Docs, cosmetic bugs |

**Support model:** Free via GitHub Issues/Discussions. Enterprise consulting post-v1.0.

### Community Engagement Plan (post-v0.21)

| Quarter | Activity |
|---------|----------|
| Q2 2026 | Blog series: "Building an IS 456 Library" (4 posts on Medium/Dev.to) |
| Q3 2026 | Submit talk proposal to PyCon India 2026 |
| Q4 2026 | LinkedIn campaign: "IS 456 Explained" weekly posts |
| Q1 2027 | Academic outreach: IIT/NIT structural engineering departments |

**Target metrics:**
- 500+ GitHub stars by v1.0
- 1000+ PyPI downloads/month
- 5+ external contributors

### Contribution Workflow Enhancements

1. **Issue templates:** Bug report, feature request, IS 456 clause request
2. **PR template:** Checklist (tests, architecture check, clause refs, benchmarks)
3. **Good First Issue** labels for onboarding
4. **Code of Conduct** enforcement: CoC referenced in CONTRIBUTING.md and PR template
5. **Contributor recognition:** AUTHORS.md auto-updated on merge
6. **CLA:** Not required pre-v1.0 (MIT license sufficient)

### Changelog Policy (Keep-a-Changelog 1.1.0)
- Format: `## [Version] - YYYY-MM-DD` → `### Added/Changed/Deprecated/Removed/Fixed/Security`
- Auto-generation: `scripts/generate_changelog_entry.py` from conventional commits
- Manual review before release (group commits, add context)

### Release Process

```
Pre-Release Checklist:
- [ ] All CI checks green (./run.sh check)
- [ ] Version bumped in pyproject.toml
- [ ] CHANGELOG.md updated (Unreleased → vX.Y.Z)
- [ ] Migration guide updated if breaking changes
- [ ] Validation report regenerated
- [ ] Benchmark results reviewed

Release Steps:
1. Create git tag: git tag vX.Y.Z
2. CI auto-publishes to PyPI
3. CI creates GitHub Release with notes
4. CI deploys docs to GitHub Pages

Post-Release:
- [ ] pip install structural-lib-is456==X.Y.Z works
- [ ] Quickstart example runs
- [ ] FastAPI /health returns 200
```

### Academic Citation
```bibtex
@software{structural_lib_is456,
  author = {Surawase, Pravin},
  title = {structural-lib-is456: IS 456 Structural Design Library},
  year = {2026},
  url = {https://github.com/pravinsurawase/structural_engineering_lib}
}
```
Add citation badge to README. Reference CITATION.cff in docs.

### Metrics Dashboard

**Tracked metrics** (auto-generated weekly):
- PyPI downloads/month (pepy.tech badge)
- GitHub stars, forks, open issues, PR throughput
- Test pass rate, code coverage %
- Documentation freshness (last update vs code changes)
- Contributor count

**Script:** `scripts/generate_metrics_dashboard.py`
**Output:** `docs/metrics/dashboard.md`
**Review:** Monthly by @governance

---

## 31. Accessibility & React UI Standards

### WCAG 2.1 Level AA Targets (React app)
- Color contrast ratio ≥ 4.5:1 for text
- All interactive elements keyboard-accessible
- Screen reader labels on 3D viewport controls
- Focus indicators visible on all forms
- Error messages associated with form fields (aria-describedby)

### 3D Viewport Accessibility
- Keyboard shortcuts for camera rotation/zoom
- Alt text for viewport content ("3D view of beam with 4 bottom bars, 2 top bars")
- Fallback 2D cross-section view for screen reader users

---

## 32. Partner Ecosystem & Integrations

### Current Integrations (v0.19)
| Software | Integration | Status |
|----------|-------------|--------|
| ETABS | CSV import (dual CSV) | ✅ Production |
| Any CSV | Generic CSV adapter (40+ columns) | ✅ Production |

### Planned Integrations

| Version | Software | Integration Type |
|---------|----------|-----------------|
| v0.26 | ETABS | Enhanced export (results → ETABS format) |
| v0.27 | STAAD.Pro | CSV import adapter |
| v0.28 | SAFE | Slab results import |
| v1.0+ | Revit | IFC import/export (community contribution) |
| v1.0+ | BIM | OpenBIM/IFC standard format |

### Integration Architecture
```
Adapters Layer (services/adapters.py)
├── GenericCSVAdapter       ← base class
├── ETABSAdapter           ← ETABS-specific column mappings
├── SAFEAdapter            ← SAFE-specific (existing)
├── STAADAdapter           ← STAAD.Pro (future)
└── IFCAdapter             ← BIM integration (future)
```

---

## 33. Review History (Updated)

| Round | Date | Reviewers | Verdict | Key Changes |
|-------|------|-----------|---------|-------------|
| 1 | 2026-03-29 | @structural-engineer (7/10), @reviewer (approved w/ enhancements), @governance (governance-incomplete) | Approved with 26 enhancements | Added §3, §5-6, §11-16; reordered elements; element-specific tolerances |
| 2 | 2026-03-29 | @structural-engineer (9/10), @reviewer (10/10), @governance (9.5/10) | All APPROVED | All Round 1 concerns addressed |
| 3 | 2026-03-29 | @structural-engineer (6.5/10 depth), @reviewer (7/10 DevOps), @governance (7.5/10 community), @tester (7.2/10 test depth) | NEEDS ADDITIONS | Added §23-32: precision, liability, deferred provisions, extension architecture, caching, test enhancements, observability, community, accessibility, partner ecosystem |
| 4 | 2026-03-30 | @library-expert (comprehensive), @structural-engineer (engineering verification), @reviewer (architecture + maintainability) | **Approved with adjustments** | Added §3.5 (function writing standards), enhanced §6.1 (debug/trace/quality), expanded Phase 1 (1.9-1.17), added D17-D23, structural invariant tests, numerical precision guards, safety factor hardcoding, stack trace sanitization, unit plausibility guards, clause coverage CI, element completeness CI. Deferred: DesignTrace/IterationLog/CAUTION severity/contextvars (to Phase 2). Dropped: `@finite_result` decorator (redundant with §23). Merged: invariant tests into tests/property/ |

### Round 3 Key Additions
- **@structural-engineer:** Numerical precision policy, crack width/fire/creep deferred, load combinations stub
- **@reviewer:** Caching strategy, extension architecture plan, release process, observability, configuration
- **@governance:** Professional use disclaimer, issue triage SLA, community engagement plan, metrics dashboard
- **@tester:** Benchmark creation workflow, chaos testing, mutation testing, flaky test strategy, test environment matrix

### New Agents Created (Round 3)
- **@security** — Security auditing, OWASP, dependency scanning, input validation review
- **@library-expert** — Library domain expert, IS 456 knowledge, professional standards, usage guidance

### Open Items from Round 3
- [ ] Add numerical precision constants to `core/constants.py`
- [ ] Add professional use disclaimer to README and __init__.py
- [ ] Create issue templates (bug, feature, IS 456 clause request)
- [ ] Create PR template with checklist
- [ ] Set up locust load testing: `fastapi_app/tests/load/locustfile.py`
- [ ] Evaluate mutmut for mutation testing (Phase 2)
- [ ] Add chaos test template: `tests/chaos/`
- [ ] Set up codecov.io badge
- [ ] Add CITATION.cff badge to README
- [ ] Create `scripts/generate_metrics_dashboard.py`

### Open Items from Review Round 4
- [ ] Create `core/numerics.py` with `safe_divide()`, `approx_equal()`, `clamp()` (backend)
- [ ] Add `recovery` field to `DesignError` frozen dataclass (backend)
- [ ] Add catch-all exception handler to `fastapi_app/main.py` — no stack trace leaks (api-developer)
- [ ] Add `X-Process-Time` middleware to `fastapi_app/main.py` (api-developer)
- [ ] Create `scripts/check_clause_coverage.py` with `REQUIRED_CLAUSES` per element (tester)
- [ ] Create `scripts/check_new_element_completeness.py` (ops)
- [ ] Add unit plausibility guards to `services/api.py` entry points (backend)
- [ ] Add `formula_signatures` to `clauses.json` for cross-reference validation (doc-master)
- [ ] Consolidate `_clamp` from `report_svg.py` and division guard from `utilities.py` into `core/numerics.py` (backend)
- [ ] Add `GAMMA_CONCRETE`, `GAMMA_STEEL` to `codes/is456/common/constants.py` (structural-math)
- [ ] Add structural invariant tests to `tests/property/` — equilibrium, monotonicity, bounds (tester)
- [ ] Add degenerate case parametrized tests for beam (Mu=0, Vu=0, fck=minimum) (tester)
- [ ] Update library-expert agent with function writing standards enforcement (orchestrator) ✅
