# Standards, Rules & Knowledge

**Version:** 2.0
**Type:** Reference
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-04-07
**Last Updated:** 2026-04-08

---

## Coding Standards

### Units Convention (MANDATORY)

> **See also:** Rule FN-01 in [Architecture Rules](#architecture-rules-40-numbered-rules) below.

- **Dimensions** get unit suffixes: `b_mm`, `d_mm`, `Mu_kNm`, `Vu_kN`
- **Material properties** use IS 456 standard symbols WITHOUT suffix: `fck`, `fy`, `Es`
- All return values: documented units in docstring
- No hidden conversions inside functions
- SI units throughout: mm, N/mm² (MPa), kN, kNm

> **Material Property Exception:** Material strengths (`fck`, `fy`, `Es`) use IS 456 standard symbols without unit suffixes. These are ALWAYS in N/mm² (MPa) per IS 456 convention. Units are documented in docstrings, not parameter names. This matches structuralcodes (fib International) convention and avoids verbose parameter names for domain experts.

```python
# ✅ CORRECT — explicit units
def design_beam(b_mm: float, d_mm: float, Mu_kNm: float, fck: float, fy: float) -> BeamResult:

# ❌ WRONG — ambiguous units
def design_beam(width: float, depth: float, moment: float, grade: float) -> dict:
```

### Clause Referencing (Mandatory)

> **See also:** Rules FN-04 and DC-03 in [Architecture Rules](#architecture-rules-40-numbered-rules) below.

Every IS 456 function MUST reference the specific clause, table, or annex in its docstring:

```python
def tau_c(fck: float, pt: float) -> float:
    """Design shear strength of concrete.

    IS 456:2000, Table 19.

    Parameters
    ----------
    fck : float
        Characteristic compressive strength (N/mm²). Range: 15-80.
    pt : float
        Percentage of tensile reinforcement. Range: 0.15-3.0.

    Returns
    -------
    float
        Design shear strength (N/mm²).

    References
    ----------
    IS 456:2000, Table 19
    SP:16:1980, Table 61
    """
```

### Function Naming

| Pattern | Example | When to Use |
|---------|---------|-------------|
| `verb_element_specific()` | `design_beam()`, `check_deflection()` | High-level design functions |
| Engineering symbols | `tau_c(fck, pt)`, `Mu_lim(b, d, fck)` | Table lookups, known formulas |
| `calculate_*` | `calculate_ast_required()` | Internal computation steps |

- No `_is456` suffix — the whole library IS for IS 456
- Drop redundant prefixes: `design_beam()` not `design_beam_is456()`

### Type Safety

> **See also:** Rules FN-02, TC-01 through TC-04 in [Architecture Rules](#architecture-rules-40-numbered-rules) below.

- All functions: fully typed parameters AND return types
- Return Pydantic BaseModel or frozen dataclass, **never raw dict**
- `py.typed` PEP 561 marker in package
- `mypy --strict`: zero errors in CI
- `pyright` basic check in CI (for IDE support)

### Documentation

> **See also:** Rules DC-01 through DC-03 in [Architecture Rules](#architecture-rules-40-numbered-rules) below.

Every public function requires:

```python
"""
Calculate limiting moment of resistance per IS 456 Cl. 38.1.

Parameters
----------
b_mm : float
    Width of beam section (mm). Must be >= 150mm.
d_mm : float
    Effective depth (mm). Must be > 0.
fck : float
    Characteristic compressive strength of concrete (N/mm²).
    Valid range: 15–80.

Returns
-------
MuLimResult
    Frozen dataclass with:
    - ``value_kNm``: Limiting moment in kNm
    - ``xu_max_mm``: Maximum neutral axis depth in mm
    - ``is_safe(Mu_kNm)``: Check if applied moment is within limit

Raises
------
DimensionError
    If ``b_mm < 150`` or ``d_mm <= 0``.
MaterialError
    If ``fck`` is outside valid range.

References
----------
IS 456:2000, Cl. 38.1, Table H (Annex G)
SP:16:1980, Chart 2

Examples
--------
>>> result = calculate_mu_lim(b_mm=230, d_mm=450, fck=25)
>>> result.value_kNm
136.73
>>> result.is_safe(Mu_kNm=120)
True
"""
```

### Import Rules

> **See also:** Rules AR-03 and AR-07 in [Architecture Rules](#architecture-rules-40-numbered-rules) below.

- **No relative imports** — following Polars pattern: `ban-relative-imports = "all"` in ruff
- Clean public API via `__init__.py` with explicit `__all__`
- Internal modules prefixed with `_` (e.g., `_internals/`)
- Users never import from internal paths

---

## Testing Standards

### 6 Test Types (for Every IS 456 Function)

> **See also:** Rules TS-01 through TS-05 in [Architecture Rules](#architecture-rules-40-numbered-rules) below.

| # | Type | Purpose | Example |
|---|------|---------|---------|
| 1 | **Unit tests** | Basic function behavior | `assert design_beam(...).is_safe()` |
| 2 | **Edge cases** | Zero values, minimum sections, maximum reinforcement | `design_beam(b_mm=150, ...)` |
| 3 | **Degenerate cases** | What happens at physical limits | `Mu_kNm=0`, `pt=0`, max allowed `pt` |
| 4 | **SP:16 benchmarks** | ±0.1% accuracy against published charts | Charts 1–62 known-answer tests |
| 5 | **Textbook examples** | Pillai & Menon, Varghese, Jain | Worked examples with known answers |
| 6 | **Hypothesis tests** | Property-based testing for invariants | Increasing moment → increasing steel |

### Quality Gates

> **See also:** Rules TC-01, TC-02, TS-05 in [Architecture Rules](#architecture-rules-40-numbered-rules) below.

| Gate | Threshold | Tool |
|------|-----------|------|
| Branch coverage | 95%+ | `pytest --cov` |
| SP:16 benchmarks | ±0.1% accuracy | `pytest -m benchmark` |
| Type safety | Zero errors | `mypy --strict src/` |
| Lint | Zero issues | `ruff check src/` |
| Performance | No regressions | `pytest-benchmark` |

### pytest Configuration

```ini
xfail_strict = true          # A passing xfail is a real bug
strict_markers = true         # Undefined markers cause errors
strict_config = true          # Unknown config keys cause errors
```

---

## Historical Mistakes to Avoid

From 70+ audit findings across v0.21.0–v0.21.3. These rules are encoded into agent instructions.

### Python (PY)

| Rule | Description | Impact |
|------|-------------|--------|
| **PY-1** | Never guess parameter names — use API discovery first | #1 cause of incorrect function calls |
| **PY-2** | Never mix IS 456 math with I/O code | Architecture violation, untestable |
| **PY-3** | Always explicit units in parameter names | Ambiguous units = silent calculation errors |
| **PY-4** | Return typed models, never raw dicts | No IDE support, no validation, no safety |
| **PY-5** | No backward-compat stubs in new code | Creates maintenance burden, confuses imports |

### Testing (TE)

| Rule | Description | Impact |
|------|-------------|--------|
| **TE-1** | Never skip SP:16 verification for IS 456 functions | Unverified formulas = liability |
| **TE-2** | Always test edge cases (zero Mu, maximum pt%) | Production crashes at boundaries |
| **TE-3** | Use Hypothesis for monotonicity/dimensional consistency | Catches edge cases humans miss |
| **TE-4** | `xfail_strict = true` — failing expected-fail = real bug | Silently passing broken tests |

### Git (GI)

| Rule | Description | Impact |
|------|-------------|--------|
| **GI-1** | Never manual git — always use commit script | Merge conflicts, lost changes |
| **GI-2** | Never `--force` or `--no-verify` | Caused 10+ hours rework historically |
| **GI-3** | Never bypass CI checks | Shipped broken releases |
| **GI-4** | Always check PR status before committing | Commits to wrong branch |

### Agent (AG)

| Rule | Description | Impact |
|------|-------------|--------|
| **AG-1** | Search before coding — duplication is #1 mistake | 70+ audit findings from duplication |
| **AG-2** | Read ENTIRE agent file before starting work | Missed rules, repeated mistakes |
| **AG-3** | Always hand off to reviewer after implementation | Uncaught bugs reach production |
| **AG-4** | Follow the pipeline — no skipping steps | Quality regressions |

---

## IS 456:2000 Coverage

### Current State

| Element | Coverage | Key Clauses | Status |
|---------|----------|-------------|--------|
| **Beam** | 95/100 | Cl 22, 23, 26, 37–41, Annex C/F/G | ✅ Production ready |
| **Column** | 90/100 | Cl 25, 26, 39, IS 13920 Cl 6–7 | ✅ Production ready |
| **Footing** | 75/100 | Cl 31.6, 34 | 🔶 Needs completion |
| **Slab** | 0/100 | Cl 24, Table 26, Annex D | ❌ **CRITICAL GAP** |
| **Load Combinations** | 0/100 | Table 18 | ❌ **CRITICAL GAP** |

### v1.0 Must-Have Gaps

| Gap | IS 456 Reference | Priority |
|-----|-----------------|----------|
| One-way slab | Cl 24 | P0 — must have for v1.0 |
| Two-way slab | Cl 24, Table 26, Annex D | P0 — must have for v1.0 |
| Load combinations | Table 18 | P0 — must have for v1.0 |
| Nominal cover table | Table 16, 16A | P1 — should have |

---

## Python Version Support

Following Scientific Python SPEC-0000 (rolling support window):

| Python Version | Support Window | Drop Date |
|---------------|---------------|-----------|
| 3.11 | Supported | When 3.14 releases (~Oct 2027) |
| 3.12 | Supported | When 3.15 releases (~Oct 2028) |
| 3.13 | Supported | When 3.16 releases (~Oct 2029) |

- Minimum version: Python 3.11 (for `tomllib`, `ExceptionGroup`, `TaskGroup`)
- Test matrix: 3.11, 3.12, 3.13
- Drop policy: 3-year rolling window per SPEC-0000

---

## Dependency Policy

### Runtime Dependencies

| Dependency | Purpose | Policy |
|-----------|---------|--------|
| `pydantic>=2.0` | Input validation, typed models | Only runtime dependency |

**Goal:** Minimize runtime deps. Everything else is development-only.

### Development Dependencies (via dependency-groups)

| Group | Dependencies |
|-------|-------------|
| `test` | pytest, pytest-cov, pytest-benchmark, hypothesis, inline-snapshot |
| `lint` | mypy, pyright |
| `docs` | mkdocs-material, mkdocstrings, mkdocs-llmstxt |
| `dev` | pre-commit |

---

## Architecture Rules (40+ Numbered Rules)

These rules are the definitive coding standards for the library, synthesized from 70+ audit findings, best practices from structuralcodes/polars/pydantic, and @library-expert research. Every rule has an ID for cross-referencing in code reviews and agent instructions.

### AR — Architecture Rules (7)

| Rule | Description |
|------|-------------|
| **AR-01** | **Five-layer strict dependency:** core ← common ← codes ← services ← ui/io. Enforce via `tach.toml`. No exceptions. |
| **AR-02** | **No I/O in codes layer** — pure math only. No file reads, no API calls, no logging side effects. |
| **AR-03** | **No relative imports** — `ban-relative-imports = "all"` in ruff. All imports are absolute. |
| **AR-04** | **Core has zero code-specific knowledge.** Core defines `BeamSection`, `DesignCode` protocol — but never mentions IS 456, ACI, or EC2. |
| **AR-05** | **Shared math used by 2+ codes moves to `common/`.** If only one code uses it, it stays in `codes/<code>/`. |
| **AR-06** | **Registry-based code discovery.** `CodeRegistry.register("is456", IS456Code)` / `CodeRegistry.get("is456")`. No `if/elif` chains. |
| **AR-07** | **Each code is a self-contained package** with its own `__init__.py`, constants, tables, and submodules. |

### FN — Function Rules (6)

| Rule | Description |
|------|-------------|
| **FN-01** | **Unit suffixes on dimensional params** (`b_mm`, `d_mm`, `Mu_kNm`, `Vu_kN`). Material properties use IS 456 standard symbols WITHOUT suffix (`fck`, `fy`, `Es` — always N/mm²). |
| **FN-02** | **Return frozen dataclasses or Pydantic BaseModel, never raw dicts.** Every result has `.is_safe()`, `.to_dict()`, `.summary()`. |
| **FN-03** | **Safety factors are constants, never function parameters.** `GAMMA_C = 1.5` is in `constants.py`, never passed as `gamma_c=1.5`. |
| **FN-04** | **`@clause()` decorator on every math function** — `clause_ref`, `table_ref`, `formula` fields for traceability. |
| **FN-05** | **Monotonicity note in docstring** where applicable (e.g., "increasing `d_mm` → increasing `Mu_lim`"). |
| **FN-06** | **Error accumulation pattern** — collect errors as tuples in result objects, not exceptions mid-calculation. Fail at the end with all issues, not on the first one. |

### MT — Math Safety Rules (5)

| Rule | Description |
|------|-------------|
| **MT-01** | **No float equality** — use `approx_equal(a, b, tol=1e-6)` or `math.isclose()`. Never `==` on floats. |
| **MT-02** | **`safe_divide()` everywhere** — handles zero denominator gracefully instead of raising `ZeroDivisionError`. |
| **MT-03** | **NaN/Inf guard on output** via `BaseResult.__post_init__()`. If any result field is NaN or Inf, raise immediately. |
| **MT-04** | **No extrapolation beyond table bounds** — raise `InterpolationError`, don't silently clamp. IS 456 tables have specific valid ranges. |
| **MT-05** | **Monotonicity invariant testing via Hypothesis.** Property: increasing depth → increasing moment capacity (etc.). |

### TC — Type Checking Rules (4)

| Rule | Description |
|------|-------------|
| **TC-01** | **basedpyright v1.39.0 as primary type checker** — stricter than standard pyright, catches more issues. |
| **TC-02** | **mypy `--strict` as CI backup** — catches different categories of issues than basedpyright. Both must pass. |
| **TC-03** | **`py.typed` PEP 561 marker required** in package root. Downstream users get type information. |
| **TC-04** | **All public functions fully typed** — parameters AND return types. No `Any` in public API. |

### TS — Testing Rules (5)

| Rule | Description |
|------|-------------|
| **TS-01** | **6 test types mandatory for every IS 456 function:** unit, edge case, degenerate, SP:16 benchmark, textbook example, Hypothesis property. |
| **TS-02** | **SP:16 benchmarks at ±0.1% accuracy.** Charts 1–62 from SP:16:1980 are the gold standard for IS 456. |
| **TS-03** | **Hypothesis for monotonicity and dimensional consistency.** Property-based testing catches edge cases humans miss. |
| **TS-04** | **mutmut mutation testing for safety-critical functions.** Line coverage alone is insufficient for life-safety code. |
| **TS-05** | **`xfail_strict = true`, `strict_markers = true`, `strict_config = true`.** A passing xfail is a real bug. Undefined markers are errors. |

### DC — Documentation Rules (3)

| Rule | Description |
|------|-------------|
| **DC-01** | **NumPy-style docstrings** (structuralcodes/polars convention). Sections: Parameters, Returns, Raises, References, Examples. |
| **DC-02** | **Every public function has:** Parameters, Returns, References (IS 456 clause), and Examples sections. No exceptions. |
| **DC-03** | **Clause reference mandatory in docstring** for every IS 456 function — `IS 456:2000, Cl. XX.X` or `Table YY`. |

### MC — Multi-Code Rules (5)

| Rule | Description |
|------|-------------|
| **MC-01** | **Code-native parameter names internally.** IS 456 uses `fck`; ACI 318 uses `fc_prime`; EC2 uses `fck`. Don't force one convention. |
| **MC-02** | **SI units at API boundaries, code-native internally.** The `services/` layer converts. Code modules use their natural units. |
| **MC-03** | **Comparison only on shared features.** Don't compare IS 456 torsion with ACI 318 torsion if the approaches are fundamentally different. |
| **MC-04** | **Grade mapping explicit, never silent conversion.** M25 (IS 456) → C25/30 (EC2) must be an explicit mapping, not assumed equal. |
| **MC-05** | **Each code self-contained, no cross-code imports.** `codes/is456/` NEVER imports from `codes/aci318/`. Shared logic goes to `common/`. |

### SC — Security Rules (3)

| Rule | Description |
|------|-------------|
| **SC-01** | **Input validation at API boundaries.** Validate dimensions (b ≥ 150mm), material ranges (fck 15–80), and reinforcement ratios at the service layer. |
| **SC-02** | **Error messages never expose internal paths.** User sees "Invalid beam width" not "Error in /src/<PACKAGE_NAME>/codes/is456/beam/flexure.py:142". |
| **SC-03** | **Dependencies pinned with hashes in lock file.** `uv.lock` provides hash verification. CI runs `uv sync --locked` to enforce. |

---

## Rule Quick Reference (All 38 Rules)

| Category | Count | Rules |
|----------|-------|-------|
| Architecture (AR) | 7 | AR-01 through AR-07 |
| Function (FN) | 6 | FN-01 through FN-06 |
| Math Safety (MT) | 5 | MT-01 through MT-05 |
| Type Checking (TC) | 4 | TC-01 through TC-04 |
| Testing (TS) | 5 | TS-01 through TS-05 |
| Documentation (DC) | 3 | DC-01 through DC-03 |
| Multi-Code (MC) | 5 | MC-01 through MC-05 |
| Security (SC) | 3 | SC-01 through SC-03 |
| **Total** | **38** | |
