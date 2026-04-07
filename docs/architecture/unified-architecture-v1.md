# Unified Architecture — structural_engineering_lib v1.0

**Type:** Architecture
**Audience:** All Agents
**Status:** Active
**Importance:** Critical
**Created:** 2026-04-06
**Last Updated:** 2026-07-09

> THE single source of truth for architecture decisions, quality gates, and safety guarantees.
> Every agent, every session, every change must comply with this document.

**Codebase snapshot (v0.21.6):**
- 168 Python source files in `structural_lib/`, 132 exports in `__all__`
- 55+ IS 456 design functions, 93+ `@clause` decorators
- 5081+ tests collected, 85%+ branch coverage (99% on codes/is456/)
- 13 routers, 60+ FastAPI endpoints
- Pydantic ≥2.0 (2.12.5), Python ≥3.11 (3.11.15)

---

## 1. Mission

Build the **definitive, professional-grade** open-source structural engineering library, supporting multiple design codes (IS 456, ACI 318, EC2) and structural elements (beams, columns, slabs, footings), with enterprise-level quality, accuracy, and safety.

**Core values:**
- **Accuracy first** — Every calculation traceable to code clause, verified against published design aids (SP:16, PCA Notes, Concrete Centre ±0.1%)
- **Safety** — Structural engineering errors can cause building failures. The library MUST be conservative when uncertain
- **Completeness** — No partial implementations that silently produce wrong results
- **Security** — OWASP Top 10 compliance, input validation, no information leakage

---

## 2. Architecture Layers (4-Layer — STRICT)

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 4: UI/IO                                                  │
│  react_app/ (React 19 + R3F + Tailwind)                         │
│  fastapi_app/ (13 routers, 60+ endpoints, REST + WebSocket)     │
│  Status: ✅ Active, 14 router files                              │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: Services                                               │
│  services/api.py — Unified public API (104 exports, re-export hub) │
│  services/adapters.py — CSV/Excel import (40+ column mappings)   │
│  services/beam_pipeline.py — Multi-step design orchestration     │
│  services/column_api.py, beam_api.py, common_api.py              │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: Design Code Math                                       │
│  codes/is456/ — IS 456:2000 (beam, column, footing, slab)       │
│  codes/is13920/ — IS 13920:2016 (ductile detailing)             │
│  codes/aci318/ — ACI 318-19 (future)                            │
│  codes/ec2/ — EN 1992-1-1 (future)                              │
│  RULES: Pure math ONLY, NO I/O, explicit units                  │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: Core                                                   │
│  core/base.py — DesignCode ABC, FlexureDesigner ABC             │
│  core/registry.py — CodeRegistry                                 │
│  core/errors.py — Error code system                              │
│  core/materials.py — Material models                             │
│  core/validation.py — Input validation                           │
│  RULES: Code-agnostic, no IS 456 math                           │
└─────────────────────────────────────────────────────────────────┘
```

### Import Rules (ENFORCED)
- Layer 1 (Core) → imports NOTHING from Layers 2-4
- Layer 2 (Codes) → imports Core only. NO I/O, NO services, NO UI
- Layer 3 (Services) → imports Core + Codes. NO UI
- Layer 4 (UI) → imports Services + Core. Never imports Codes directly
- **Validation:** `scripts/validate_imports.py --scope structural_lib`
- **Enforcement:** `scripts/check_architecture_boundaries.py`

### Unit Rules (MANDATORY)
- All parameters use explicit unit suffixes: `b_mm`, `fck_nmm2`, `Mu_kNm`
- Standard units: mm (length), N/mm² (stress), kN (force), kNm (moment)
- **NEVER** use unitless parameters for physical quantities
- ACI imperial inputs converted at boundary (in→mm, psi→MPa in `core/units.py` — 🔲 Planned v0.24)

---

## 3. Quality Assurance Framework

### 3.1 Structural Accuracy Guarantees

| Check | Tolerance | Verified Against | Tool |
|-------|-----------|-----------------|------|
| IS 456 flexure | ±0.1% | SP:16 Table I | pytest golden vectors |
| IS 456 shear | ±0.1% | SP:16 Table 19/20 | pytest golden vectors |
| IS 456 columns | ±0.1% | SP:16 Table I, Annex G | pytest golden vectors |
| ACI 318 (future) | ±0.1% | PCA Notes (12th Ed.) | pytest golden vectors |
| EC2 (future) | ±0.1% | Concrete Centre examples | pytest golden vectors |
| Textbook examples | ±1% | (rounding tolerance) | pytest |

### 3.2 Code Traceability

Every **public** design function MUST have:
1. **`@clause()` decorator** — Links to IS 456/ACI/EC2 clause number
2. **Docstring with formula** — The exact equation being implemented
3. **Unit specification** — What units each parameter expects
4. **Golden vector test** — Published design aid result that MUST match ±0.1%

**Current coverage (v0.21.5):** 93+ `@clause` decorators across `codes/`. All public IS 456 beam, column, shear, detailing, and footing sizing functions have `@clause`. Known gaps:
- 6 footing helper/private functions (`_common.py` utilities, `_design_direction`, `_check_direction`) lack `@clause` — these are internal helpers, not standalone design functions
- IS 13920 beam/column/joint functions ✅ all have `@clause(standard="IS 13920")`

| Module | @clause coverage | Status |
|--------|-----------------|--------|
| `codes/is456/beam/` | All public functions | ✅ |
| `codes/is456/column/` | All public functions | ✅ |
| `codes/is456/footing/` | 6/12 functions (helpers excluded, `size_footing` added) | 🔶 Partial |
| `codes/is13920/` | All public functions | ✅ |

> **Note:** The signature below uses Layer 2 (codes/) naming — bare IS 456 shorthand (`fck`, `fy`, `b`, `d`). At Layer 3 (services/), these become `fck_nmm2`, `fy_nmm2`, `b_mm`, `d_mm` per the two-tier naming convention (§10.5).

```python
@clause("38.1")
def design_singly_reinforced(
    fck: float,        # N/mm² — characteristic concrete strength
    fy: float,         # N/mm² — steel yield strength
    b_mm: float,       # mm — beam width
    d_mm: float,       # mm — effective depth
    Mu_kNm: float,     # kNm — factored bending moment
) -> FlexureResult:
    """IS 456 Cl 38.1 — Singly reinforced rectangular beam flexure.

    Mu = 0.36·fck·b·xu·(d - 0.42·xu)
    Ast = 0.5·(fck/fy)·b·d·[1 - √(1 - 4.6·Mu/(fck·b·d²))]
    """
```

### 3.3 Input Validation (Defense in Depth)

**Layer 2 (Code math):** Plausibility guards
- `fck` must be in valid range (15-80 for IS 456)
- Dimensions must be positive and physically reasonable
- `fck > 120` triggers "Did you mean psi instead of N/mm²?" warning

**Layer 3 (Services):** Business logic validation
- Cross-field validation (cover < overall depth)
- Unit consistency checks

**Layer 4 (FastAPI):** Pydantic models with ranges
- All endpoints use Pydantic models with `Field(ge=..., le=...)`
- Error responses use standard format: `{"success": false, "error": {...}}`

**Error Framework:**
- Every error has: What happened? Why? How to fix it?
- Error codes are prefixed per module: E_FLEXURE_001, E_COLUMN_001, etc.
- Internal exceptions NEVER leak to API responses (CWE-209)

> **Error Policy:** See §10.6 for the full error handling policy. In brief: all errors from Layers 2-3 MUST be `StructuralLibError` subclasses with `suggestion`, `clause_ref`, and `details`.

### 3.4 Testing Requirements

| Level | Requirement | Tool |
|-------|------------|------|
| **Function** | 6 test types per IS 456 function (unit, edge, degenerate, SP:16, textbook, Hypothesis) | pytest |
| **API** | Every services/api.py function has integration test | pytest |
| **Endpoint** | Every FastAPI route has request/response test | pytest + httpx |
| **Contract** | Response envelope shape validated (`{success, data}`) | pytest |
| **Architecture** | Import boundaries checked | check_architecture_boundaries.py |
| **Packaging** | Wheel contents verified (no tests/, clauses.json present) | test_packaging.py |
| **E2E** | Full pipeline: design → detailing → BBS → DXF → report | test_full_pipeline_e2e.py |
| **Coverage** | ≥85% branch coverage for production code | pytest-cov |
| **Performance** | Regression detection: single beam < 5ms, batch 100 < 500ms | pytest-benchmark |
| **Compliance** | All public code functions have @clause, return frozen dataclass, have golden vectors | ✅ 42+ golden vectors, 18 contract tests |
| **Smoke** | Quick (<5s) sanity check for CI fast-fail | 🔲 Planned (`smoke` marker not yet registered) |

**Current stats (v0.21.5):** 4700+ tests collected, all selected tests pass (100%), 99% branch coverage on `codes/is456/`, 85%+ overall.

### 3.5 Security Requirements

| Requirement | Implementation | Status |
|-------------|---------------|--------|
| Auth on all non-health endpoints | AuthMiddleware (opt-in via AUTH_ENABLED, OFF by default) | 🔶 Partial |
| Rate limiting | RateLimitMiddleware (all endpoints) | ✅ |
| Input size limits | Pydantic `max_length`, file size limits | ✅ |
| No `str(e)` in responses | Sanitized error messages, log originals server-side | ✅ |
| CORS configuration | Settings-based, not hardcoded | ✅ |
| WebSocket validation | Pydantic model validation on WS messages | ✅ |
| No path traversal | Job runner validates file paths | ✅ |
| Dependency pinning | requirements-lock.txt | ✅ |
| JSON body size limit | RequestSizeLimitMiddleware: 1MB for JSON | 🔲 Planned |
| Computation timeout | Prevent pathological inputs from hanging workers | 🔲 Planned |
| WebSocket message rate limit | 5 messages/second per session | 🔲 Planned |
| RBAC / scope enforcement | require_scope() dependency checked against User.scopes | 🔲 Planned |
| Design audit trail | Structured audit log for all design calculations | 🔲 Planned |
| Cross-field plausibility | Reject physically impossible parameter combinations | 🔲 Planned |
| Dependency CVE scanning | pip-audit in CI (`security.yml`) | ✅ Active |
| OpenAPI docs disabled in production | /docs, /redoc only in dev/debug | 🔲 Planned |

---

## 4. Code Organization

### 4.1 Per-Code Structure (Code-First Nesting)

```
codes/{code_id}/
├── __init__.py          # CodeClass (IS456Code, ACI318Code, EC2Code)
├── common/              # Code-specific shared utilities
│   ├── constants.py     # Safety factors, material limits
│   ├── stress_blocks.py # Stress block model
│   ├── validation.py    # Code-specific input guards
│   └── reinforcement.py # Bar areas, sizes per code
├── beam/
│   ├── flexure.py       # Flexural design
│   ├── shear.py         # Shear design
│   ├── detailing.py     # Detailing rules
│   ├── serviceability.py # Deflection + crack width
│   └── torsion.py       # Torsion design
├── column/
│   ├── _common.py       # Shared column utilities
│   ├── axial.py         # Axial capacity + classification
│   ├── biaxial.py       # Biaxial bending (Bresler)
│   ├── detailing.py     # Column detailing
│   ├── helical.py       # Helical reinforcement (Cl 39.4)
│   ├── long_column.py   # Long/slender column design
│   ├── slenderness.py   # Slenderness classification
│   └── uniaxial.py      # Uniaxial bending
├── slab/                # 🔲 Planned — One-way + two-way + flat slab
├── footing/             # Isolated + combined
├── tables.py            # Design tables (code-specific)
├── materials.py         # Material models (code-specific)
├── traceability.py      # @clause() decorator
└── clauses.json         # Clause database
```

> **Note:** The `core/` layer contains 20 files (only the 5 key files are shown above). Additional files include: `constants.py`, `data_types.py`, `deprecation.py`, `error_messages.py`, `geometry.py`, `inputs.py`, `logging_config.py`, `models.py`, `numerics.py`, `result_base.py`, `types.py`, `utilities.py`. Run `ls Python/structural_lib/core/` for the full listing.

### 4.2 Services Layer Pattern

```python
# services/api.py — THE public API entry point
# RULES:
# 1. NEVER duplicate math from codes/ — always delegate
# 2. EVERY public function in __all__ with proper type hints
# 3. EVERY function has a golden vector test
# 4. Parameter names MUST match code conventions (b_mm, fck, etc.)

# Current primary API (v0.21.5):
def design_beam_is456(**kwargs) -> ComplianceCaseResult:
    """IS 456 beam design — direct entry point."""
    # Delegates to codes/is456/ for all math
    ...

# Planned unified multi-code API (v0.24):
def design_beam(*, code: str, **kwargs) -> DesignEnvelope:
    """Unified multi-code beam design (v0.24+)."""
    code_impl = CodeRegistry.get(code)
    return code_impl.design_beam(**kwargs)
```

> **Note:** The `design_beam()` unified dispatch is **planned for v0.24**. The current primary path is `design_beam_is456()` which delegates directly to IS 456 math modules without going through `CodeRegistry`. The `CodeRegistry` infrastructure exists and IS456 is registered, but the unified API path is not yet wired.

### 4.3 FastAPI Pattern

```python
# fastapi_app/routers/{element}.py
# RULES:
# 1. Pydantic models with Field(ge=..., le=...) for all inputs
# 2. Standard response: {"success": true, "data": {...}}
# 3. Error response: {"success": false, "data": null, "error": "<sanitized string>"}
# 4. No str(e) in error details — sanitize all error messages
# 5. Rate limiting applied via middleware
# 6. Auth required on all non-health endpoints
```

**Current Error Shape** (v0.21.5):
```json
{
  "success": false,
  "data": null,
  "error": "Sanitized error message string"
}
```

**Target Structured Error Shape** (🔲 Planned v0.24 — consumed by frontend):
```json
{
  "success": false,
  "error": {
    "code": "E_FLEXURE_001",
    "message": "User-facing description",
    "suggestion": "Actionable fix (see §10.6)",
    "clause_ref": "IS456:38.1",
    "details": {}
  }
}
```

---

## 5. Schema & Data Model

### 5.1 Pydantic Models (Input Validation)

**FastAPI layer uses Pydantic models** for all inputs. These serve as the schema:

```python
class BeamDesignRequest(BaseModel):
    """Request model for beam design calculation."""
    width: float = Field(gt=0, le=2000.0, description="Beam width b (mm)")
    depth: float = Field(gt=0, le=3000.0, description="Overall beam depth D (mm)")
    moment: float = Field(ge=0, description="Factored moment (kNm)")
    shear: float = Field(ge=0, default=0, description="Factored shear (kN)")
    fck: float = Field(ge=15, le=80, description="Concrete grade (N/mm²)")
    fy: float = Field(ge=250, le=550, description="Steel grade (N/mm²)")
    clear_cover: float = Field(default=25.0, description="Clear cover (mm)")
```

> **Note:** FastAPI Pydantic models use descriptive English (`width`, `depth`, `moment`) with `alias` fields for backward compat. The Layer 3 API uses unit-suffix names (`b_mm`, `d_mm`, `Mu_kNm`) per the two-tier naming convention (§10.5).

### 5.2 Result Dataclasses (Output Schema)

Result dataclasses provide structured output. Most are **frozen** (`@dataclass(frozen=True)`), but `FlexureResult` is currently **mutable** pending refactor (TODO SM-6).

> **Note:** The schema below shows the **target v0.24** design (frozen, unit-suffix field names). The current `FlexureResult` in [core/data_types.py](../../Python/structural_lib/core/data_types.py) is **not frozen** (TODO SM-6) and uses different field names (`Mu_lim`, `Ast_required`, `xu`, `xu_max`, `is_safe`, `Asc_required`, `errors`, `Ast_min`, `Ast_max`, `clause_refs`). See migration notes in §15.1.

```python
@dataclass(frozen=True)  # TARGET — current FlexureResult is NOT frozen (TODO SM-6)
class FlexureResult:
    Ast_mm2: float           # Required tension steel area
    xu_mm: float             # Neutral axis depth
    xu_max_mm: float         # Limiting neutral axis depth
    Mu_cap_kNm: float        # Moment capacity
    is_doubly: bool          # Whether doubly reinforced
    status: str              # "OK" or "FAIL"
    clause_refs: list[str]   # ["IS456:38.1"]

    def to_dict(self) -> dict: ...
```

### 5.3 DesignEnvelope (Multi-Code Result — v0.24)

🔲 Planned v0.24

```python
@dataclass(frozen=True)
class DesignEnvelope:
    """Code-agnostic result wrapper for unified API."""
    is_safe: bool
    utilization_ratio: float     # 0.0–1.0+
    governing_check: str         # "flexure", "shear", "deflection"
    code: str                    # "IS456", "ACI318", "EC2"
    element: str                 # "beam", "column", "slab"
    details: object              # Code-specific result dataclass
    warnings: list[str]
    clause_refs: list[str]
```

### 5.4 Do We Need a Formal Schema?

**Answer: Pydantic IS our schema.** The Pydantic models serve triple duty:
1. **Input validation** — Type checking, range validation, cross-field checks
2. **OpenAPI schema** — Auto-generated API docs at `/docs`
3. **JSON schema** — `model.model_json_schema()` exports standard JSON Schema

**Additional schemas:**
- `clauses.json` — Clause database schema (section 12.4 of blueprint)
- `api_manifest.json` — API function registry
- `index.json` — Folder metadata schema

No separate schema definition language (like Protocol Buffers or GraphQL) is needed. Pydantic provides type safety, validation, and auto-generated documentation.

---

## 6. Safety Guarantees

### 6.1 Structural Safety

| Guarantee | Mechanism |
|-----------|-----------|
| No incorrect formulas | @clause traceability + SP:16 benchmarks ±0.1% |
| No silent failures | Error framework: What? Why? How to fix? |
| Conservative when uncertain | If two interpretations exist, use conservative + warn (see §15.2) |
| Explicit limitations | Every function documents what it does NOT handle |
| No partial results | Functions return complete results or raise errors |
| Unit confusion prevention | Plausibility guards (fck > 120 → "Expected N/mm², not Pa") |
| Conservative defaults | Documented conservative defaults for ambiguous inputs | Conservative Defaults Registry (§15.2) |

### 6.2 Software Safety

| Guarantee | Mechanism |
|-----------|-----------|
| Import boundaries enforced | validate_imports.py, check_architecture_boundaries.py |
| No backward-compat breaks | @deprecated decorator, 2 minor version retention |
| Test coverage ≥85% | pytest-cov enforcement |
| No production code without PR | should_use_pr.sh blocks direct main commits |
| No manual git operations | ai_commit.sh is the ONLY commit path |
| No force pushes | Blocked at script level |

### 6.3 API Safety

| Guarantee | Mechanism |
|-----------|-----------|
| All endpoints protected | Auth middleware |
| Rate limiting | Global RateLimitMiddleware |
| Input validated | Pydantic models with ranges |
| Errors sanitized | No str(e) leakage |
| Response envelope consistent | {success, data} contract |
| OpenAPI documentation | Auto-generated, always current |

---

## 7. File Ownership & Responsibilities

| File/Folder | Owner Agent | Rules |
|-------------|-------------|-------|
| `codes/is456/` | @structural-math | Pure math only, @clause required |
| `codes/is13920/` | @structural-math | Seismic detailing |
| `core/` | @backend | No IS 456 math |
| `services/` | @backend | Orchestration only, no math duplication |
| `fastapi_app/` | @api-developer | Pydantic models, no math |
| `react_app/` | @frontend | Tailwind only, API-first |
| `docs/` | @doc-master | Append-first, check duplicates |
| `scripts/` | @ops | All git through ai_commit.sh |
| `.github/agents/` | @agent-evolver | Evolution tracking |

---

## 8. Development Workflow

### 8.1 New Function Checklist

Every new structural function MUST:
- [ ] Have @clause decorator linking to code clause
- [ ] Have docstring with exact formula
- [ ] Use explicit unit suffixes on parameters
- [ ] Have plausibility guards on inputs
- [ ] Return frozen dataclass result
- [ ] Include clause_refs in result
- [ ] Have 6 test types (unit, edge, degenerate, benchmark, textbook, Hypothesis)
- [ ] Pass SP:16/PCA benchmark ±0.1%
- [ ] Be wired into services/api.py
- [ ] Have FastAPI endpoint with Pydantic model
- [ ] Be documented in api.md
- [ ] Pass architecture boundary checks

### 8.2 New Endpoint Checklist

- [ ] Pydantic request model with Field ranges
- [ ] Pydantic response model
- [ ] Standard response envelope {success, data}
- [ ] Error handling with sanitized messages
- [ ] Rate limiting (via middleware)
- [ ] Auth required
- [ ] OpenAPI examples
- [ ] Integration test
- [ ] Unit plausibility guards (ge/le constraints detecting meters-vs-mm confusion)
- [ ] Router imports from structural_lib — NEVER reimplements math
- [ ] curl/httpie example for testing/handoff
- [ ] Response model fields match the frozen dataclass fields

### 8.3 Quality Pipeline (9 Steps)

```
1. PLAN          → Orchestrator identifies clause + formula + benchmark
2. MATH REVIEW   → @structural-engineer verifies formula independently
3. IMPLEMENT     → @structural-math writes code (12-point checklist)
4. TEST          → @tester writes 6 test types
5. REVIEW        → Two-pass: @structural-engineer (math) + @reviewer (code)
6. API WIRE      → @backend adds to services/api.py
7. ENDPOINT      → @api-developer creates FastAPI route
8. DOCUMENT      → @doc-master updates all docs
9. COMMIT        → @ops commits via ai_commit.sh
```

---

## 9. Version Roadmap

### 9.1 Micro-Release Strategy (v0.21.x Series)

We use **patch releases** for focused, testable increments. Each v0.21.x release has a single theme, clear deliverables, and a quality gate that must pass before the next release begins. This prevents the "big bang" stabilization problem where too many changes ship at once and regressions slip through.

**Current baseline:** v0.21.6 — 5081+ tests collected, pre-commit hooks active, architecture checker enforced, golden vectors and contract tests established.

| Version | Theme | Quality Gate |
|---------|-------|-------------|
| v0.21.5 | Test Coverage & Regression Prevention | 90%+ branch coverage on `codes/is456/` |
| v0.21.6 | API Quality & Introspection | `check_code("IS456")` passes all checks |
| v0.21.7 | Security Hardening | `audit_input_validation.py` reports 0 findings |
| v0.21.8 | Performance & Property Testing | All benchmarks baselined, Hypothesis tests pass |
| v0.22.0 | Stabilization Release | Full CI/CD pipeline with all gates active |

### 9.2 v0.21.5 — Test Coverage & Regression Prevention ✅ DONE

**Theme:** Establish golden vector baselines and contract tests so that no future change can silently break existing calculations.

**Deliverables:**
- ✅ Golden vector baselines for all IS 456 functions — 42+ tests (9 beam + 20 column + 13 footing)
- ✅ Contract tests for API surface stability — 18 contract tests (`@pytest.mark.contract`)
- ✅ Report & 3D visualization test coverage (TASK-520) — 71 new tests
- ✅ `conftest.py` golden_vectors fixture with SP:16 reference values
- ✅ Target: 99% branch coverage on `codes/is456/` (exceeded 90% target)

**Quality Gate:** `pytest -m golden` passes with 0 failures ✅, branch coverage 99% on `codes/is456/` ✅

### 9.3 v0.21.6 — API Quality & Introspection ✅ DONE

**Theme:** Make the library self-describing and self-validating. Users can inspect capabilities and limitations without reading docs.

**Deliverables:**
- ✅ `check_code()` — validates design inputs against IS 456 limits (returns warnings/errors without computing) (§10.2)
- ✅ `show_versions()` — prints library + dependency versions (like `np.show_config()`) (§10.3)
- ✅ API surface freeze: OpenAPI baseline diff in CI (`openapi_baseline.json` already exists)
- ✅ Function limitation documentation (explicit "what this function does NOT do")

**Quality Gate:** `check_code("IS456")` returns report. OpenAPI diff integrated into CI. ✅

### 9.4 v0.21.7 — Security Hardening

**Theme:** Close all OWASP-relevant gaps. Every input path validated, every output bounded.

**Deliverables:**
- 🔲 JSON body size limit (FastAPI middleware, 1MB default)
- 🔲 Cross-field plausibility guards (e.g., `d_mm > b_mm` raises warning)
- 🔲 Input validation audit completion (`scripts/audit_input_validation.py` exists)
- ✅ Dependency CVE scanning in CI (`pip-audit` — active in `security.yml`)

**Quality Gate:** `audit_input_validation.py` reports 0 unresolved findings. `pip-audit` clean.

### 9.5 v0.21.8 — Performance & Property Testing

**Theme:** Establish performance baselines and property-based invariants so regressions are caught automatically.

**Deliverables:**
- 🔲 `pytest-benchmark` integration for hot-path functions
- 🔲 Property-based testing with Hypothesis for IS 456 shear/moment
- 🔲 Performance regression baselines (fail CI if >20% slower)
- 🔲 Pre-commit hook validation (already have `.pre-commit-config.yaml`)

**Quality Gate:** All benchmarks baselined in `Python/test_stats.json`. Hypothesis tests pass 10,000 examples.

### 9.6 v0.22.0 — Stabilization Release

**Theme:** Ship a production-quality release with full provenance, verification, and CI gates.

**Deliverables:**
- 🔲 CalculationProvenance foundation (`core/provenance.py`)
- 🔲 SP:16 full verification (TASK-643)
- 🔲 Beam rationalization (TASK-521)
- 🔲 Deprecate old architecture docs
- 🔲 Full CI/CD pipeline with all gates active
- 🔲 Release checklist automation

**Quality Gate:** All v0.21.x quality gates pass simultaneously. SP:16 verification ±0.1%. Release preflight clean.

### 9.7 Future Roadmap (v0.23→v1.0)

> **Detailed task-level roadmap:** See §20 for complete deliverables per version with owners and status markers.

| Version | Focus | Key Deliverables |
|---------|-------|------------------|
| v0.23 | IS 456 Slabs | One-way + two-way slab, footing completion, punching shear |
| v0.24 | Multi-Code Infra | CodeRegistry thread-safety, DesignEnvelope, `units.py`, API v2, client SDK generation (§13.1) |
| v0.25 | ACI 318 Beam | Flexure + shear, PCA Notes benchmarks |
| v1.0 | Production | IS 456 complete, ACI 318 beam+column, EC2 beam, API stability, full OWASP (§12), provenance (§11) |

---

## 10. API Design Principles (Inspired by NumPy/pandas/scikit-learn)

These principles are drawn from analysis of successful scientific Python libraries and adapted for structural engineering.

### 10.1 Flat Import Pattern (Required)

Every public API function MUST be importable directly from `structural_lib`:

```python
from structural_lib import design_beam_is456      # ✅ Required
import structural_lib as sl; sl.design_beam_is456(...)  # ✅ Required
```

The `__init__.py` re-exports all public API functions from `services/api.py`. Users should never need to know internal module paths. This follows the NumPy pattern (`from numpy import array`) and pandas pattern (`from pandas import DataFrame`).

**Rules:**
- Package `__init__.py` imports from `services/api.py` and re-exports via `__all__`
- Sub-packages (e.g., `codes.is456`) do NOT need flat imports — they are internal
- New public functions added to `services/api.py` MUST also be added to `__all__` in `__init__.py`

### 10.2 `check_code()` Self-Validation Utility

Inspired by scikit-learn's `check_estimator()`. A runtime validator that checks a design code implementation meets the API contract:

```python
from structural_lib import check_code

results = check_code("IS456")
# Returns CheckCodeReport with:
# - all_importable: bool         — All beam/column/slab modules importable
# - all_decorated: bool          — All functions have @clause decorator
# - all_frozen: bool             — All functions return frozen dataclasses
# - all_results_valid: bool      — All results have is_safe(), to_dict(), summary()
# - all_params_named: bool       — All parameter names use unit suffixes
# - all_golden_pass: bool        — All golden vector tests pass
# - no_boundary_violations: bool — No import boundary violations
# - issues: list[str]            — Detailed list of any failures
```

This is **critical for v0.24+** when third-party codes (ACI 318, EC2) are added. A code implementation that fails `check_code()` MUST NOT be registered in `CodeRegistry`.

| Status | Target Version |
|--------|---------------|
| ✅ Implemented | v0.21.6 |

### 10.3 `show_versions()` Diagnostic Utility

Like scikit-learn's `sklearn.show_versions()` and pandas' `pd.show_versions()`. Reports environment information critical for bug reports:

```python
from structural_lib import show_versions

show_versions()
# structural_lib: 0.22.0
# Python: 3.12.4
# Platform: macOS-14.5-arm64
#
# Design Codes:
#   IS 456:2000 — 14/14 beam clauses, 12/12 column clauses
#   ACI 318-19  — not installed
#   EC2         — not installed
#
# Optional Dependencies:
#   numpy:      1.26.4
#   pandas:     2.2.1
#   httpx:      0.27.0 (for client SDK)
#   hypothesis: 6.100.0 (for property-based testing)
```

| Status | Target Version |
|--------|---------------|
| ✅ Implemented | v0.21.6 |

### 10.4 CodeRegistry vs Global State (Design Decision)

The `structuralcodes` library (fib-international) uses a global `set_design_code()` pattern:

```python
# structuralcodes pattern (NOT used here)
import structuralcodes
structuralcodes.set_design_code("EC2")  # Global state — affects all subsequent calls
```

We chose `CodeRegistry.get("IS456")` instead. Reasons:

| Concern | Global State | Registry Pattern (Ours) |
|---------|-------------|------------------------|
| Thread safety | ❌ Race conditions in multi-threaded FastAPI | 🔶 Effective under CPython GIL, no explicit locks |
| Testability | ❌ Tests must reset global state | ✅ `CodeRegistry.clear()` for test isolation |
| Concurrent multi-code | ❌ One code at a time | ✅ Compare IS 456 vs ACI 318 in same request |
| Explicit dependency | ❌ Implicit — which code is active? | ✅ `code="IS456"` passed explicitly |

**Current status (v0.21.5):**
- `CodeRegistry` is **live code** — `IS456Code` is registered via `@register_code("IS456")` in `codes/is456/__init__.py`
- ACI 318 and EC2 code classes exist as stubs with `@register_code` commented out
- Instance caching uses a simple `dict` — effective under CPython GIL but **not explicitly thread-safe** (no `threading.Lock`). Adding explicit locks is planned for v0.24 when multi-code concurrent access becomes a real use case
- The unified multi-code dispatch path (`design_beam(code='IS456')` → `CodeRegistry.get()`) shown in §4.2 is **planned infrastructure**, not the current primary API path. Users currently call `design_beam_is456()` directly

**Thread-safety gap:** The `_instances` dict in `CodeRegistry` is mutated on first `get()` call. Under CPython's GIL, dict mutations are atomic, so concurrent `get()` calls will not corrupt data. However, two threads calling `get()` simultaneously for an unregistered code could both create instances. This is benign (last write wins, same type) but not formally thread-safe. Explicit `threading.Lock` is planned for v0.24.

This design decision stands for the v1.0 architecture. The registry pattern is the correct choice for a multi-code library with concurrent API access.

### 10.5 Parameter Naming Convention

**Rule:** Dimensional parameters MUST have unit suffixes.

#### Two-Tier Convention (Implemented v0.22.0)

The library uses a **two-tier naming convention** that respects both IS 456 textbook notation and API explicitness:

| Layer | Scope | Convention | Example |
|-------|-------|------------|--------|
| **Layer 2** (`codes/is456/`) | Pure IS 456 math | Bare IS 456 shorthand — no suffixes | `fck`, `fy`, `Mu`, `Vu`, `b`, `d` |
| **Layer 3** (`services/`) | Public API surface | Full unit-suffix names | `fck_nmm2`, `fy_nmm2`, `Mu_kNm`, `b_mm`, `d_mm` |

**Why two tiers?**
- Layer 2 matches textbook notation exactly — engineers reading IS 456 code see familiar symbols
- Layer 3 makes units explicit for API consumers who may not know IS 456 conventions
- The boundary between L2 and L3 handles the translation

#### Unit Suffix Rules

| Category | Convention | Examples |
|----------|-----------|----------|
| Length | `_mm` suffix | `b_mm`, `d_mm`, `cover_mm`, `Ld_mm` |
| Force | `_kN` suffix | `Vu_kN`, `Pu_kN` |
| Moment | `_kNm` suffix | `Mu_kNm`, `Mcr_kNm` |
| Stress | `_nmm2` suffix | `fck_nmm2`, `fy_nmm2`, `sigma_nmm2` |

**Naming choices follow IS 456 notation:**
- `fck_nmm2` — **not** `fck_MPa`. IS 456 writes "N/mm²", not "MPa".
- `Mu_kNm` — **not** `mu_knm`. IS 456 uses uppercase $M_u$, $V_u$.
- `fy_nmm2` — **not** `fy_mpa`. Consistent with IS 456 clause 5.2.

#### Backward Compatibility

Old parameter names (`fck`, `fy`, `b`, `d`, etc.) continue to work at Layer 3 as **deprecated aliases**. They emit a `DeprecationWarning` with migration guidance and will be **removed in v0.24**.

```python
# ✅ New convention (preferred)
result = design_column_axial_is456(fck_nmm2=25, fy_nmm2=415, ...)

# ⚠️ Old names still work but emit DeprecationWarning
result = design_column_axial_is456(fck=25, fy=415, ...)  # warns: use fck_nmm2
```

#### Functions Migrated (Batch 3)

| Module | Functions | Parameters Renamed |
|--------|-----------|-------------------|
| `column_api.py` | 10 functions | `fck`→`fck_nmm2`, `fy`→`fy_nmm2` |
| `beam_api.py` | `check_beam_ductility` | `b`→`b_mm`, `D`→`D_mm`, `d`→`d_mm`, `fck`→`fck_nmm2`, `fy`→`fy_nmm2` |
| `beam_api.py` | `check_anchorage_at_simple_support` | `fck`→`fck_nmm2`, `fy`→`fy_nmm2` |
| FastAPI models | Pydantic `alias` | Backward compat in JSON payloads |

**Rationale:** Unit suffixes prevent the most dangerous class of structural engineering bugs — unit confusion. A beam designed with `b=300` (mm) vs `b=300` (cm) vs `b=300` (in) gives wildly different results.

### 10.6 Error Handling Policy

Every error from Layer 2 (Codes) or Layer 3 (Services) MUST be a `StructuralLibError` subclass. Raw `ValueError`/`TypeError` are FORBIDDEN outside Layer 1 validation.

Every error MUST include:

| Field | Purpose | Example |
|-------|---------|---------|
| `suggestion` | Actionable fix the user can take | `"Increase beam depth to at least 300mm"` |
| `clause_ref` | Governing IS 456 clause | `"IS456:38.1"` |
| `details` | Dict with failing values for debugging | `{"d_mm": 150, "min_d_mm": 300}` |

```python
# ❌ WRONG — unhelpful
raise ValueError("Depth too small")

# ✅ RIGHT — actionable, traceable
raise DesignInputError(
    message="Effective depth insufficient for the applied moment",
    suggestion="Increase beam depth to at least 300mm per IS 456 Cl 23.1",
    clause_ref="IS456:23.1",
    details={"d_mm": d_mm, "min_d_mm": 300, "Mu_kNm": Mu_kNm}
)
```

### 10.7 Function Limitation Documentation

Every code function docstring MUST include a `Limitations:` section that explicitly states what the function does NOT handle:

```python
def design_singly_reinforced(
    fck: float, fy: float, b_mm: float, d_mm: float, Mu_kNm: float
) -> FlexureResult:
    """IS 456 Cl 38.1 — Singly reinforced rectangular beam flexure.

    Mu = 0.36·fck·b·xu·(d - 0.42·xu)
    Ast = 0.5·(fck/fy)·b·d·[1 - √(1 - 4.6·Mu/(fck·b·d²))]

    Limitations:
        - Rectangular sections only (for T-beam use design_flanged_beam)
        - No axial load consideration (for beam-columns use column modules)
        - Does not check lateral stability (L/b > 60)
        - Valid for fck ≤ 80 N/mm² (high-strength concrete outside IS 456 scope)
        - Assumes short-term loading (no creep reduction on xu_max)
    """
```

This prevents the most dangerous failure mode: a user applying a function outside its valid scope and getting silently incorrect results.

---

## 11. Calculation Provenance & Audit Trail (CRITICAL)

This is the **highest priority architectural gap**. Licensed structural engineers who sign off on designs need a complete audit trail proving:
- Which library version produced the result
- Which code and amendments were applied
- Exact inputs used (for reproducibility)
- When the calculation was performed

### 11.1 CalculationProvenance Dataclass

```python
@dataclass(frozen=True)
class CalculationProvenance:
    """Audit trail attached to every design result."""
    library_version: str          # "0.22.0"
    code_id: str                  # "IS456:2000"
    code_amendments: tuple[str, ...]  # ("AMD1:2003", "AMD4:2020")
    timestamp_utc: str            # ISO 8601 — "2026-04-06T14:30:00Z"
    input_hash: str               # SHA-256 of canonical input JSON
    input_echo: dict              # Exact inputs for reproducibility
    compute_time_ms: float        # Profiling data
    result_hash: str              # SHA-256 of output for tamper detection
    warnings: tuple[str, ...]     # Conservative defaults applied (see §15.2)
    element_id: str               # Beam/column/footing ID (e.g. "B1-3F")
    design_status: str            # "SAFE" / "UNSAFE" / "WARNING"
    safety_factors: dict           # {"gamma_c": 1.5, "gamma_s": 1.15}
```

Every design result dataclass WILL carry (once implemented in v1.0) a `provenance: CalculationProvenance` field. This is non-optional and automatically populated by the services layer.

**Implementation plan:**
- `core/provenance.py` — `CalculationProvenance` dataclass + builder
- Services layer wraps every code call with provenance generation
- `input_hash` is SHA-256 of canonicalized (sorted keys, deterministic float format) input JSON
- `compute_time_ms` uses `time.perf_counter_ns()` for accuracy

| Status | Target Version |
|--------|---------------|
| 🔲 Planned | v1.0 |

### 11.2 Code Amendment Tracking

IS 456:2000 has 4 amendments (2003, 2005, 2006, 2020). Each code module must declare which amendments it implements:

```python
# codes/is456/__init__.py
__code_id__ = "IS456:2000"
__amendments__ = ("AMD1:2003", "AMD2:2005", "AMD3:2006", "AMD4:2020")
__implemented_amendments__ = ("AMD1:2003", "AMD4:2020")
__reference_edition__ = "Reaffirmed 2021"
```

This metadata:
- Feeds into `CalculationProvenance.code_amendments`
- Is displayed by `show_versions()`
- Is checked by `check_code()` — unimplemented amendments produce warnings
- Enables future amendment-aware calculations (e.g., AMD4:2020 includes various clause corrections)

| Status | Target Version |
|--------|---------------|
| 🔲 Planned | v0.24 |

### 11.3 Export Integrity

All exported files (BBS, DXF, reports) must include provenance metadata:

| Field | Location | Format |
|-------|----------|--------|
| SHA-256 content hash | File header/comment | `# SHA-256: a1b2c3...` |
| Library version | File header/comment | `# structural_lib v0.22.0` |
| Timestamp | File header/comment | ISO 8601 UTC |
| Beam/element ID | File header/comment | User-provided identifier |
| Code + amendments | File header/comment | `IS456:2000 (AMD1:2003, AMD4:2020)` |

For DXF files, provenance is stored in the XDATA section. For CSV/BBS, it is in comment lines at the top. For PDF reports, it is in the document metadata.

| Status | Target Version |
|--------|---------------|
| 🔲 Planned | v1.0 |

---

## 12. OWASP API Security Top 10 (2023) Compliance

Systematic mapping of each OWASP API Security risk to our controls, gaps, and remediation plan.

### 12.1 Risk Assessment Matrix

| # | OWASP Risk | Risk Level | Our Controls | Gap | Remediation |
|---|-----------|-----------|-------------|-----|-------------|
| API1 | Broken Object Level Auth (BOLA) | Low | Stateless API, no user-owned objects | WS session_id needs format validation | Validate session_id format (UUID only) |
| API2 | Broken Authentication | Partial | JWT auth (OFF by default) | Auth OFF by default in development; must enforce in production | Add refresh tokens, enforce in prod |
| API3 | Broken Object Property Level Auth | Low | Pydantic explicit fields, no `extra="allow"` | No gap | Maintain strict Pydantic models |
| API4 | Unrestricted Resource Consumption | Partial | Rate limit (120/min), file 10MB, batch 500 | Missing JSON body limit, computation timeout, WS rate | Add RequestSizeLimitMiddleware (1MB), computation timeout, WS rate limit |
| API5 | Broken Function Level Auth | Not Impl | `User.scopes` defined but NOT checked | Scopes not enforced | Add `require_scope()` dependency |
| API6 | Unrestricted Access to Sensitive Business Flows | Partial | Range validation on inputs | No cross-field plausibility, no audit trail | Add plausibility guards, audit trail, export watermarking |
| API7 | Server Side Request Forgery (SSRF) | No Risk | No external URL fetching | None | Monitor if webhooks added |
| API8 | Security Misconfiguration | Good | CORS configured, Docker hardened, JWT enforced | `/docs` accessible in prod, debug mode | Disable `/docs` in prod, guard debug mode |
| API9 | Improper Inventory Management | Good | Single `/api/v1`, OpenAPI baseline exists | No deprecation headers | Add deprecation headers, endpoint registry |
| API10 | Unsafe Consumption of Third-Party APIs | Low | No external API calls | CSV adapter path handling | Validate CSV adapter doesn't follow filesystem paths |

### 12.2 Structural Engineering Specific Security

Beyond standard OWASP controls, structural engineering APIs have domain-specific security needs:

**Cross-field plausibility guards (API boundary):**
```python
# Reject physically impossible parameter combinations
if Mu_kNm > 0.138 * fck * b_mm * d_mm**2 * 1e-6 * 5.0:
    raise DesignInputError(
        message="Applied moment far exceeds section capacity",
        suggestion="Check units — Mu_kNm should be in kNm, not Nm",
        clause_ref="IS456:38.1"
    )
```

**Design calculation audit trail:**
- Middleware logs every design request with inputs, outputs, and provenance
- Enables forensic analysis if a design is questioned
- Required by professional engineering liability standards

**Anomaly detection for unusual parameters:**
- Moment > 5000 kNm → flag for review (very large member)
- Section width < 150mm → warning (suspiciously small)
- Batch size > 200 → rate limit warning
- Concrete grade > M60 → warning (rare in IS 456 practice)

**Export provenance metadata:**
- Every exported file (BBS, DXF, report) includes library version, timestamp, and content hash
- Prevents undetected modification of exported design documents

---

## 13. Client SDK & User Experience

### 13.1 Client SDK Strategy (v0.24+)

The existing hand-written clients in `clients/` should be REPLACED with auto-generated clients for consistency and maintenance:

| Language | Generator | Source | Status |
|----------|-----------|--------|---------|
| Python | openapi-python-client | OpenAPI spec at `/openapi.json` | 🔲 Planned (v0.24) |
| TypeScript | openapi-typescript | OpenAPI spec at `/openapi.json` | 🔲 Planned (v0.24) |

**Release process:**
- SDK versions pinned to API version (e.g., SDK 0.24.0 → API v1 at server 0.24.0)
- Breaking API changes require SDK version bump
- Generated code committed to `clients/python/` and `clients/typescript/`
- CI generates and tests SDKs on every API change

**HTTPX-based Python client pattern:**
```python
import httpx
from structural_lib_client import StructuralLibClient

client = StructuralLibClient(base_url="http://localhost:8000")
result = client.design_beam(
    fck=25, fy=415, b_mm=300, d_mm=450, Mu_kNm=120
)
print(result.Ast_mm2)
```

### 13.2 Progress Callbacks

Batch operations (beam_pipeline, adapters) should support optional progress callbacks for UI integration:

```python
from typing import Callable

ProgressCallback = Callable[[int, int, str], None]  # (current, total, stage)

def batch_design_beams(
    beams: list[dict],
    *,
    on_progress: ProgressCallback | None = None
) -> list[ComplianceCaseResult]:
    """Design multiple beams with optional progress reporting."""
    for i, beam in enumerate(beams):
        if on_progress:
            on_progress(i + 1, len(beams), "designing")
        # ... design logic ...
```

This enables:
- React progress bars via WebSocket
- CLI progress bars via tqdm
- Logging of batch progress

| Status | Target Version |
|--------|---------------|
| 🔲 Planned | v0.23 |

### 13.3 Structured Error Types

Custom exception hierarchy providing actionable error messages:

> **Note:** The hierarchy below shows the **target design**. Current actual exceptions in `core/errors.py` include `StructuralLibError`, `DesignConstraintError`, `ComplianceError`, `DimensionError`, `LoadError`. The additional subclasses listed below are planned for v0.24+.

```
StructuralLibError (base)
├── ValidationError
│   ├── DesignInputError      — Invalid design parameters
│   └── MaterialError         — Invalid material properties
├── CalculationError
│   ├── ConvergenceError      — Iterative solution didn't converge
│   └── CapacityExceededError — Section capacity exceeded
└── ConfigurationError
    ├── CodeNotFoundError     — Requested code not registered
    └── MissingAmendmentError — Required amendment not implemented
```

Every exception carries `suggestion`, `clause_ref`, and `details` per §10.6.

| Status | Target Version |
|--------|---------------|
| 🔶 Partial (base classes exist) | v0.23 complete hierarchy |

---

## 14. Testing Strategy (Enhanced)

### 14.1 Property-Based Testing Invariants

Using Hypothesis to verify mathematical invariants that must hold for ALL valid inputs:

| Module | Required Hypothesis Invariants |
|--------|---------------------------------|
| Flexure | Increasing `fck` → non-decreasing capacity; `Ast ≥ Ast_min` always; `xu ≤ xu_max` for singly reinforced |
| Shear | `τc` monotonically non-decreasing with `pt` (plateaus for high pt per Table 19); `sv ≤ sv_max` always |
| Column | `Pu` symmetric for symmetric sections; P-M interaction curve convex for symmetric reinforcement layouts |
| Detailing | `Ld ≥ Ld_min` always; lap length ≥ `Ld` always |
| ALL | `is_safe()` consistent with `utilization_ratio ≤ 1.0` |

```python
from hypothesis import given, strategies as st

@given(
    fck=st.sampled_from([20, 25, 30, 35, 40]),
    fy=st.sampled_from([415, 500]),
    b_mm=st.floats(min_value=200, max_value=1000),
    d_mm=st.floats(min_value=200, max_value=1500),
)
def test_flexure_capacity_increases_with_fck(fck, fy, b_mm, d_mm):
    """Higher concrete grade → higher moment capacity (monotonicity)."""
    result_low = design_singly_reinforced(fck=20, fy=fy, b_mm=b_mm, d_mm=d_mm, Mu_kNm=50)
    result_high = design_singly_reinforced(fck=fck, fy=fy, b_mm=b_mm, d_mm=d_mm, Mu_kNm=50)
    assert result_high.Mu_cap_kNm >= result_low.Mu_cap_kNm
```

| Status | Target Version |
|--------|---------------|
| 🔶 Partial (5 modules: serviceability, shear, flexure, ductile, slenderness) | v0.23 expand to all modules |

### 14.2 Performance Benchmarks

| Operation | Target | Tool | Status |
|-----------|--------|------|--------|
| Single beam design | < 5ms | pytest-benchmark | 🔲 Planned |
| Batch 100 beams | < 500ms | pytest-benchmark | 🔲 Planned |
| CSV import (1000 rows) | < 2s | pytest-benchmark | 🔲 Planned |
| 3D geometry generation | < 50ms | pytest-benchmark | 🔲 Planned |
| JSON serialization (100 results) | < 10ms | pytest-benchmark | 🔲 Planned |

> **Note (v0.21.5):** `test_benchmarks.py` exists with 13 benchmark tests. However, formal `pytest-benchmark` integration with regression detection (>20% slowdown blocks merge) is not yet active.

**Regression policy:** >20% slowdown from baseline blocks merge. Benchmark results stored in `Python/test_stats.json` and tracked across versions.

### 14.3 Automated Compliance Checker

Pytest fixtures that verify ALL code functions meet the API contract:

```python
import dataclasses
from typing import get_type_hints

@pytest.mark.parametrize("func", get_all_code_functions())
def test_function_has_clause_decorator(func):
    """Every IS 456 function must have @clause traceability."""
    assert hasattr(func, '_clause_ref'), f"{func.__name__} missing @clause decorator"

@pytest.mark.parametrize("func", get_all_code_functions())
def test_function_returns_frozen_dataclass(func):
    """Every IS 456 function must return a frozen dataclass."""
    result_type = get_type_hints(func).get('return')
    assert dataclasses.is_dataclass(result_type), f"{func.__name__} doesn't return a dataclass"
    assert result_type.__dataclass_params__.frozen, f"{func.__name__} result is not frozen"

@pytest.mark.parametrize("func", get_all_code_functions())
def test_function_params_have_units(func):
    """Dimensional parameters must have unit suffixes."""
    import inspect
    sig = inspect.signature(func)
    for name in sig.parameters:
        if name in ('self', 'cls'):
            continue
        # Standard IS 456 symbols exempt
        if name in ('fck', 'fy', 'fsc', 'Es', 'Ec'):
            continue
        # Check dimensional params have unit suffix
        # (heuristic — not all params are dimensional)
```

| Status | Target Version |
|--------|---------------|
| 🔲 Planned | v0.23 |

---

## 15. Backward Compatibility Policy

### 15.1 Deprecation Protocol

**Process:**
1. Add `@deprecated(version, remove_version, alternative)` decorator
2. Function continues to work for 2 minor versions
3. Migration guide auto-generated from `@deprecated` decorator metadata
4. API surface diffing in CI: `check_api_surface.py --baseline api_manifest.json`

**CI enforcement:**
- New functions: ✅ OK (additive change)
- Removed functions: ❌ BLOCK merge (breaking change)
- Changed signatures: ⚠️ WARN (may be breaking)

```python
from structural_lib.core.deprecation import deprecated

@deprecated(
    version="0.22.0",
    remove_version="0.24.0",
    alternative="design_beam(code='is456', ...)"
)
def design_beam_is456(**kwargs):
    """Backward-compatible — use design_beam() instead."""
    return design_beam(code='is456', **kwargs)
```

### 15.2 Conservative Defaults Registry

When input is ambiguous or unspecified, the library MUST use conservative (safe-side) defaults. These are documented and traceable:

| Parameter | Conservative Default | IS 456 Clause | Rationale |
|-----------|---------------------|---------------|----------|
| End condition (unknown) | Both ends pinned | Cl 25.2 | Pinned gives longer effective length → more conservative |
| Exposure condition | Moderate (not mild) | Table 3 | Requires more cover → conservative |
| Cover | Table 16 + 5mm tolerance | Cl 26.4 | Extra tolerance for construction variance |
| Bar type | Fe 415 for ductility | Cl 5.6 | Fe 415 has better ductility than Fe 500 |
| Effective span | Clear span + d or c/c, whichever less | Cl 22.2 | Uses the lesser value |
| Live load reduction | None (full live load) | — | No reduction is always conservative |
| Concrete density | 25 kN/m³ | — | Standard for normal weight concrete |
| Load combination (unknown) | 1.5(DL+LL) | Cl 18.2.3, Table 18 | Most conservative basic combination |

**Rule:** If a default is used, the result MUST include a warning indicating which defaults were applied:
```python
warnings=["Default: Moderate exposure assumed (IS 456 Table 3)"]
```

---

## 16. Observability & Operations

### 16.1 Structured Logging

| Feature | Implementation | Status |
|---------|---------------|--------|
| JSON format in production | `StructuredFormatter` in `config.py` | ✅ Implemented |
| PII scrubbing | Email, token, password fields redacted | ✅ Implemented |
| Request ID propagation | From middleware to calculation layer | 🔶 Partial |
| Correlation across services | Request ID in all log entries | 🔲 Planned |

### 16.2 Request Tracing

- `RequestIDMiddleware` injects `X-Request-ID` header on every response (existing)
- Request ID must propagate to `structural_lib` calculations and error messages (gap)
- Use same request ID in `sanitize_error()` instead of generating new UUIDs
- Enables end-to-end tracing: `HTTP request → FastAPI → structural_lib → response`

| Status | Target Version |
|--------|---------------|
| 🔶 Partial | v0.23 |

### 16.3 Anomaly Detection

> Anomaly detection rules are defined in §12.2 (Structural Engineering Specific Security). The monitoring system flags unusual parameter combinations and logs them to the security audit log.

### 16.4 Supply Chain Security

| Measure | Tool | Status |
|---------|------|--------|
| CVE scanning | pip-audit in CI (`security.yml`) | ✅ Active |
| Hash verification | `requirements-lock.txt` with hashes | 🔶 Partial (lock exists, no hashes) |
| Automated updates | Dependabot/Renovate for dependency PRs | 🔲 Planned |
| Docker build | Uses lock file (not unpinned requirements.txt) | ✅ Implemented |
| Minimal base image | `python:3.11-slim` | ✅ Implemented |

### 16.5 Pre-commit Hooks

`.pre-commit-config.yaml` is **active** and `.git/hooks/pre-commit` is installed. Current hooks:

```yaml
repos:
  # General file hygiene
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks: [check-yaml, check-toml, check-json, end-of-file-fixer,
            trailing-whitespace, mixed-line-ending, check-merge-conflict,
            check-added-large-files]

  # Python formatting
  - repo: https://github.com/psf/black
    rev: 25.9.0
    hooks: [black]
```

> **Note:** In addition to the basic hygiene hooks, ruff v0.4.4 (lint + auto-fix) and mypy (structural_lib type checking) are **active** pre-commit hooks. black is also active for formatting.

**Planned additions (v0.23):**

| Hook | Purpose | Status |
|------|---------|--------|
| ruff lint + format (v0.4.4) | Python linting + auto-fix | ✅ Active |
| mypy (structural_lib) | Static type checking | ✅ Active |
| architecture-check | Import boundary validation | 🔲 Planned |
| api-surface-check | OpenAPI baseline diff | 🔲 Planned |
| clause-coverage | IS 456 clause parity check | 🔲 Planned |

Git hooks also exist via `ai_commit.sh`, which runs staging, formatting, and push operations. The `.pre-commit-config.yaml` complements these for contributors who don't use agent scripts.

| Status | Target Version |
|--------|---------------|
| ✅ Active (basic hygiene + formatting) | v0.21.5 |
| 🔲 Planned (architecture + API checks) | v0.23 |

### 16.6 Concurrency Model

FastAPI runs with uvicorn's async event loop. Structural calculations are CPU-bound and run in the default thread pool executor via `asyncio.to_thread()` or `run_in_executor()`.

**CodeRegistry caching:** The `CodeRegistry` uses simple `dict`-based instance caching (see §10.4). This is **not explicitly thread-safe** — there are no `threading.Lock` guards. Under CPython's GIL, dict mutations are effectively atomic, so concurrent access is safe in practice but not by design. Explicit locking is planned for v0.24 when multi-code concurrent access becomes a production requirement.

**Implication:** For the current single-code (IS 456) deployment, the concurrency model is adequate. When ACI 318/EC2 codes are added and concurrent multi-code requests become real, the `CodeRegistry` must be hardened with proper locking.

### 16.7 Future Architecture Considerations (v1.0+)

**WASM Compilation Path:** Layer 2 (pure math, no I/O) is a natural candidate for WebAssembly compilation via Pyodide or Rust rewrite. Client-side calculation would enable offline-capable progressive web apps. The 4-layer architecture already isolates pure math — this requires no refactoring. 🔲 Planned post-v1.0.

**Entry-Point Plugin Discovery:** The `CodeRegistry` (§10.4) currently requires manual `register()` calls. For third-party codes (`pip install structural-lib-aci318`), Python's `importlib.metadata.entry_points()` pattern (used by pytest, tox, flake8) would enable auto-registration. 🔲 Planned v0.24.

```python
# pyproject.toml — third-party code plugin
[project.entry-points."structural_lib.codes"]
aci318 = "structural_lib_aci318:ACI318Code"
```

**Serialization Performance:** For batch operations at scale (§14.2 targets), benchmark `msgspec.Struct` vs frozen dataclass `.to_dict()` for the `DesignEnvelope` wrapper — `msgspec` is 5-20x faster for JSON serialization. 🔲 Benchmark in v0.24.

---

## 17. Comparison with Established Libraries

### 17.1 Pattern Adoption Matrix

Systematic tracking of patterns adopted from mature scientific Python libraries:

| Pattern | Source Library | Our Implementation | Status |
|---------|--------------|-------------------|--------|
| Flat imports | NumPy, pandas | `__init__.py` re-exports from `services/api.py` | ✅ Implemented |
| ABC + Registry | scikit-learn `BaseEstimator` | `DesignCode` ABC + `CodeRegistry` | ✅ Implemented |
| `@clause` traceability | structuralcodes | `@clause()` decorator | ✅ Implemented |
| `check_code()` validation | scikit-learn `check_estimator()` | Runtime code contract checker | ✅ Implemented |
| `show_versions()` | scikit-learn, pandas | Environment diagnostic utility | ✅ Implemented |
| Frozen dataclass results | Pythonic immutable design | Most results frozen; `FlexureResult` mutable (TODO SM-6) | 🔶 Partial |
| `@deprecated` decorator | pandas, scikit-learn | `core/deprecation.py` | ✅ Implemented |
| Property-based testing | pandas Hypothesis suite | 5 modules (serviceability, shear, flexure, ductile, slenderness) | 🔶 Expand |
| Performance benchmarks | pandas ASV benchmarks | pytest-benchmark planned | 🔲 v0.23 |
| Pre-commit hooks | pandas, scikit-learn | `.pre-commit-config.yaml` active (black, file hygiene) | ✅ Basic / 🔲 Advanced |
| Client SDK generation | HTTPX patterns | Hand-written stubs in `clients/` | 🔲 v0.24 |
| Code module metadata | structuralcodes | `__code_id__`, `__amendments__` planned | 🔲 v0.24 |
| National annex support | structuralcodes | Not implemented | 🔲 v0.24 |
| Progress callbacks | pandas `tqdm` integration | Batch design with `on_progress` | 🔲 v0.23 |

### 17.2 Comparison with structuralcodes (fib-international)

Detailed comparison with the closest open-source structural engineering library:

| Aspect | structuralcodes | structural_lib | Assessment |
|--------|----------------|----------------|------------|
| Architecture | Flat modules, global `set_design_code()` | 4-layer, `CodeRegistry` class-based | Ours is better (thread-safe, testable) |
| Scope | Material properties, constitutive laws | Full design → detailing → BBS → DXF | Complementary — we do more |
| Multi-code support | EC2, MC2010, MC2020 | IS 456 (ACI 318/EC2 planned) | They're ahead on code coverage |
| National annexes | `set_national_annex()` globally | Not implemented | Gap — needed for v0.24 |
| Testing rigor | Standard pytest | pytest + Hypothesis + golden vectors + SP:16 benchmarks | Ours more rigorous |
| Factory pattern | `create_concrete()`, `create_reinforcement()` | Direct construction | Gap — factory pattern better for multi-code |
| API design | Functional (stateless functions) | Functional + OOP (CodeRegistry) | Similar philosophy |
| Documentation | Standard docstrings | `@clause` decorator + `Limitations:` section + formula in docstring | Ours more traceable |
| Web API | None | FastAPI with 60+ endpoints | Unique to our project |
| 3D visualization | None | React + R3F + Three.js | Unique to our project |

**Integration opportunity:** `structuralcodes` material models could be used as optional backend for constitutive laws, especially for Eurocode material properties.

---

## 18. Regression Prevention Framework

### 18.1 Golden Vector Testing

Every IS 456 function MUST have golden vectors — known-good input/output pairs from SP:16 or textbook examples.

```python
# conftest.py
@pytest.fixture
def golden_beam_vectors():
    """SP:16 Example 1 — Simply supported beam."""
    return {
        "input": {"b_mm": 230, "d_mm": 450, "fck": 20, "fy": 415, "Mu_kNm": 120},
        "expected": {"Ast_mm2": 821.5, "status": "Under-reinforced"},
        "tolerance": 0.001,  # ±0.1%
        "source": "SP:16 Example 1, p.12"
    }
```

**Rules:**
- Mark with `@pytest.mark.golden` — run separately: `pytest -m golden`
- Tolerance: ±0.1% for SP:16, ±1% for textbook, ±5% for edge cases
- Every new IS 456 function MUST add golden vectors before merge

### 18.2 API Surface Protection

- `openapi_baseline.json` tracks all endpoint signatures
- CI diff: any endpoint change without version bump = failure
- Python API: `__all__` exports tracked, removal = breaking change

### 18.3 Architecture Boundary Enforcement

- `scripts/check_architecture_boundaries.py` runs in CI
- Core cannot import Services or UI (one-way dependency)
- Violations block merge

### 18.4 Performance Regression Gates

- Benchmark baselines stored in `Python/test_stats.json`
- CI fails if any benchmark >20% slower than baseline
- Run: `pytest --benchmark-only -m performance`

### 18.5 Contract Testing

```python
@pytest.mark.contract
def test_design_beam_returns_required_keys():
    """API contract: design_beam_is456 must return these keys."""
    result = design_beam_is456(b_mm=230, d_mm=450, fck=20, fy=415, Mu_kNm=120)
    required = {"Ast_mm2", "xu_mm", "xu_max_mm", "status", "Mu_capacity_kNm"}
    assert required.issubset(result.keys())
```

### 18.6 Regression Test Categories

| Category | Marker | Frequency | Tolerance |
|----------|--------|-----------|-----------|
| Golden vectors | `@golden` | Every CI run | ±0.1% (SP:16) |
| Contract tests | `@contract` | Every CI run | Exact match |
| Property tests | `@property` | Nightly | Statistical |
| Performance | `@performance` | Weekly | ±20% baseline |
| Integration | `@integration` | Every PR | Pass/fail |

---

## 19. Governance & Release Process

Inspired by NumPy's NEP process and pandas' release engineering. Adapted for a structural engineering library where **incorrect releases can cause building failures**.

### 19.1 Release Process (Mandatory Steps)

Every release MUST follow this sequence. Skipping steps has caused 4+ emergency re-releases historically.

```
1. PREFLIGHT    → ./run.sh release preflight 0.X.Y
                  - Packaging verification (wheel contents, clauses.json present)
                  - API drift detection (OpenAPI baseline diff)
                  - Security scan (pip-audit, input validation audit)
                  - Import validation (no broken imports)
                  - Test suite passes (4700+ tests, ≥85% coverage)

2. UAT          → /user-acceptance-test skill
                  - pip install from built wheel in clean venv
                  - Import all public API functions
                  - Run end-to-end design pipeline
                  - Verify CLI examples work

3. QUALITY GATE → /quality-gate skill (3 levels)
                  Level 1 (Commit):  lint, type-check, architecture check
                  Level 2 (PR):      full test suite, coverage, API surface
                  Level 3 (Release): UAT, security, packaging, benchmark

4. VERSION BUMP → ./run.sh release run 0.X.Y
                  - Updates pyproject.toml version
                  - Updates CHANGELOG.md
                  - Creates git tag
                  - Builds wheel + sdist

5. POST-RELEASE → Verify on PyPI test index
                  - pip install from test PyPI
                  - Smoke test: import + design_beam_is456()
                  - Update docs/reference/api.md if API changed
```

### 19.2 Version Numbering

| Increment | When | Example |
|-----------|------|---------|
| Patch (0.21.x) | Bug fixes, test additions, doc updates | 0.21.4 → 0.21.5 |
| Minor (0.x.0) | New features, new elements, new endpoints | 0.21.x → 0.22.0 |
| Major (x.0.0) | Breaking API changes, multi-code support | 0.x → 1.0.0 |

**Micro-release strategy:** Each v0.21.x release has a single theme and quality gate (see §9.1). This prevents "big bang" releases where too many changes ship at once.

### 19.3 Decision Records (ADR)

Architectural decisions are recorded in `docs/adr/`. Each ADR captures:
- Context: Why the decision was needed
- Decision: What was chosen
- Consequences: Trade-offs accepted
- Status: Proposed / Accepted / Deprecated / Superseded

Key ADRs: CodeRegistry pattern (§10.4), 4-layer architecture (§2), frozen dataclass results (§5.2), `@clause` traceability (§3.2).

### 19.4 Agent Compliance & Enforcement

Every AI agent MUST complete this checklist before handing off:
- [ ] Read own `.agent.md` file at task start
- [ ] Searched for existing code before writing new code
- [ ] Used `discover_api_signatures.py` before calling any API function
- [ ] All new functions have at least one golden vector test
- [ ] Architecture boundaries verified (no upward imports)
- [ ] Committed via `ai_commit.sh` (never manual git)

**Enforcement mechanisms:**

| Rule | Enforced By | Failure Mode |
|------|-------------|--------------|
| No upward imports | `check_architecture_boundaries.py` | 🔲 Local script only — not yet in CI |
| API surface stability | OpenAPI baseline diff | 🔲 Planned — baseline exists, CI check not wired |
| Golden vectors exist | `pytest -m golden` | PR review catches |
| Commit message format | `ai_commit.sh` hooks | Commit rejected |
| PR required for prod code | `should_use_pr.sh` | Push rejected |
| No `--force` or `--no-verify` | Pre-push hook | Push rejected |

**Agent performance tracking:**
- `scripts/agent_scorer.py` — scores each agent per session (0-100)
- `scripts/agent_drift_detector.py` — detects instruction drift
- `logs/agent-performance/` — historical scores
- Dashboard: `./run.sh evolve --status`

### 19.5 Continuous Improvement Loop

```
Agent makes mistake → logs/feedback/ captures it
→ @agent-evolver detects pattern
→ .agent.md instruction updated
→ Next session: mistake prevented
```

This loop has prevented 70+ recurring issues since v0.21.0. All violations are logged to `logs/feedback/` with agent name, timestamp, rule violated, impact, and the instruction fix that prevents recurrence.

### 19.6 Contribution Guidelines

- **All contributors** (human or AI) must use `ai_commit.sh` for commits
- **Production code** requires PR review before merge
- **IS 456 math changes** require two-pass review: @structural-engineer (math) + @reviewer (code)
- **New structural elements** follow the 9-step quality pipeline (§8.3)
- **Breaking changes** require an ADR and 2 minor version deprecation cycle

---

## 20. Complete Roadmap (v0.21.5 → v1.0)

### 20.1 v0.21.5 — Test Coverage & Regression Prevention ✅ DONE

**Theme:** Golden vector baselines and contract tests. No future change can silently break existing calculations.

| Deliverable | Status | Owner |
|------------|--------|-------|
| Golden vector baselines for all IS 456 functions (`@pytest.mark.golden`) — 42+ tests | ✅ | @tester |
| Contract tests for API surface stability (`@pytest.mark.contract`) — 18 tests | ✅ | @tester |
| Report & 3D visualization test coverage (TASK-520) — 71 new tests | ✅ | @tester |
| `conftest.py` golden_vectors fixture with SP:16 reference values | ✅ | @tester |
| 99% branch coverage on `codes/is456/` (exceeded 90% target) | ✅ | @tester |
| Add `@clause("34.1")` to `size_footing()` | ✅ | @structural-math |

**Quality Gate:** `pytest -m golden` passes with 0 failures ✅, branch coverage 99% on `codes/is456/` ✅

### 20.2 v0.21.6 — API Quality & Introspection ✅ DONE

**Theme:** Self-describing, self-validating library.

| Deliverable | Status | Owner |
|------------|--------|-------|
| `check_code("IS456")` — validates code implementation contract (§10.2) | ✅ | @backend |
| `show_versions()` — environment diagnostic utility (§10.3) | ✅ | @backend |
| API surface freeze: OpenAPI baseline diff in CI | ✅ | @api-developer |
| Function limitation documentation for all public functions | ✅ | @doc-master |

**Quality Gate:** `check_code("IS456")` returns report. OpenAPI diff integrated into CI. ✅

### 20.3 v0.21.7 — Security Hardening

**Theme:** Close all OWASP-relevant gaps.

| Deliverable | Status | Owner |
|------------|--------|-------|
| JSON body size limit (FastAPI middleware, 1MB default) | 🔲 | @api-developer |
| Cross-field plausibility guards (API boundary validation) | 🔲 | @api-developer |
| Input validation audit completion (`audit_input_validation.py`) | 🔲 | @security |
| Dependency CVE scanning in CI (`pip-audit`) | ✅ Active (`security.yml`) | @ops |
| WebSocket message rate limit (5 msg/s per session) | 🔲 | @api-developer |
| Computation timeout (prevent pathological inputs) | 🔲 | @api-developer |

**Quality Gate:** `audit_input_validation.py` reports 0 unresolved findings. `pip-audit` clean.

### 20.4 v0.21.8 — Performance & Property Testing

**Theme:** Performance baselines and property-based invariants.

| Deliverable | Status | Owner |
|------------|--------|-------|
| `pytest-benchmark` integration for hot-path functions | 🔲 | @tester |
| Hypothesis tests for IS 456 — expand beyond current 5 modules (§14.1) | 🔶 Partial | @tester |
| Performance regression baselines (>20% slowdown blocks merge) | 🔲 | @ops |
| Benchmark results stored in `Python/test_stats.json` | 🔲 | @tester |

**Quality Gate:** All benchmarks baselined. Hypothesis tests pass 10,000 examples.

### 20.5 v0.22.0 — Stabilization Release

**Theme:** Production-quality release with full provenance and CI gates.

| Deliverable | Status | Owner |
|------------|--------|-------|
| CalculationProvenance foundation (`core/provenance.py`, §11) | 🔲 | @backend |
| SP:16 full verification (TASK-643) | 🔲 | @structural-engineer |
| Beam rationalization (TASK-521) | 🔲 | @backend |
| Full CI/CD pipeline with all quality gates active | 🔲 | @ops |
| Release checklist automation | 🔲 | @ops |
| Deprecate old architecture docs | 🔲 | @doc-master |

**Quality Gate:** All v0.21.x quality gates pass simultaneously. SP:16 verification ±0.1%. Release preflight clean.

### 20.6 v0.23.0 — IS 456 Slabs & Footing Completion

| Deliverable | Status | Owner |
|------------|--------|-------|
| One-way slab design | 🔲 | @structural-math |
| Two-way slab design (Rankine-Grashoff coefficients) | 🔲 | @structural-math |
| Flat slab with drop panels | 🔲 | @structural-math |
| Punching shear enhancement | 🔲 | @structural-math |
| Footing `@clause` coverage to 100% (size_footing done in v0.21.5) | 🔶 Partial | @structural-math |
| Combined footing design | 🔲 | @structural-math |
| Progress callbacks for batch operations (§13.2) | 🔲 | @backend |
| Complete error hierarchy (§13.3) | 🔲 | @backend |
| Property-based testing expansion to all modules (§14.1) | 🔲 | @tester |
| Performance benchmarks baselined (§14.2) | 🔲 | @tester |

### 20.7 v0.24.0 — Multi-Code Infrastructure

| Deliverable | Status | Owner |
|------------|--------|-------|
| CodeRegistry thread-safe locking | 🔲 | @backend |
| `DesignEnvelope` multi-code result wrapper (§5.3) | 🔲 | @backend |
| `core/units.py` — unit conversion at boundary (in→mm, psi→MPa) | 🔲 | @backend |
| `check_code()` implementation (§10.2) — see v0.21.6 | Moved to v0.21.6 (§9.3) | @backend |
| `show_versions()` implementation (§10.3) — see v0.21.6 | Moved to v0.21.6 (§9.3) | @backend |
| Code Amendment Tracking metadata (§11.2) | 🔲 | @structural-math |
| National annex support infrastructure | 🔲 | @backend |
| Entry-point plugin discovery for third-party codes (§16.7) | 🔲 | @backend |
| Auto-generated client SDKs (Python + TypeScript) (§13.1) | 🔲 | @api-developer |
| Parameter naming convention migration (`b`→`b_mm`) | 🔲 | @backend |
| API v2 with unified `design_beam(code='IS456')` | 🔲 | @backend |

### 20.8 v0.25.0 — ACI 318 Beam

| Deliverable | Status | Owner |
|------------|--------|-------|
| ACI 318-19 beam flexure | 🔲 | @structural-math |
| ACI 318-19 beam shear | 🔲 | @structural-math |
| PCA Notes (12th Ed.) benchmarks ±0.1% | 🔲 | @tester |
| `@register_code("ACI318")` activation | 🔲 | @backend |
| ACI318 FastAPI endpoints | 🔲 | @api-developer |

### 20.9 v1.0.0 — Production Release

| Deliverable | Status | Owner |
|------------|--------|-------|
| IS 456 complete (beam + column + slab + footing) | 🔲 | @structural-math |
| ACI 318 beam + column | 🔲 | @structural-math |
| EC2 beam (basic) | 🔲 | @structural-math |
| CalculationProvenance on all results (§11) | 🔲 | @backend |
| Export integrity/watermarking (§11.3) | 🔲 | @backend |
| Full OWASP compliance (§12) | 🔲 | @security |
| API stability guarantee (no breaking changes without major version) | 🔲 | @backend |
| Complete documentation coverage | 🔲 | @doc-master |
| Performance benchmarks all met (§14.2) | 🔲 | @tester |
| RBAC / scope enforcement (§3.5) | 🔲 | @api-developer |
| Design audit trail middleware (§11.1) | 🔲 | @api-developer |

### 20.10 Post-v1.0 Considerations

| Item | Description | Status |
|------|-------------|--------|
| WASM compilation path | Layer 2 pure math → Pyodide/Rust for client-side calc | 🔲 Research |
| msgspec serialization | Benchmark vs frozen dataclass for batch perf | 🔲 Research |
| structuralcodes integration | Material models as optional backend | 🔲 Research |
| IS 16700 (tall buildings) | Wind/seismic response spectra | 🔲 Research |
| IS 1893 integration | Seismic load generation | 🔲 Research |

---

## 21. References

- [Library Expansion Blueprint v5.0](../planning/library-expansion-blueprint-v5.md) — Detailed multi-code plan
- [Mission & Principles](mission-and-principles.md) — Project philosophy
- [Project Overview](project-overview.md) — Original architecture docs
- [Data Flow Diagrams](data-flow-diagrams.md) — System data flows
- [Config Precedence](config-precedence.md) — Agent configuration hierarchy
- [API Reference](../reference/api.md) — Public API documentation
- [TASKS.md](../TASKS.md) — Active task board
- [OWASP API Security Top 10 (2023)](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) — Security baseline
- [structuralcodes](https://github.com/fib-international/structuralcodes) — Open-source structural engineering library (fib)
- [scikit-learn Developer Guide](https://scikit-learn.org/stable/developers/develop.html) — API design patterns
- [IS 456:2000 (Reaffirmed 2021)](https://www.bis.gov.in/) — Indian Standard for Plain and Reinforced Concrete
- [NumPy Enhancement Proposals (NEPs)](https://numpy.org/neps/) — Governance model inspiration
- [pandas Release Process](https://pandas.pydata.org/docs/development/maintaining.html) — Release engineering reference
