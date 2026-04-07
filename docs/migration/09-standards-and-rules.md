# Standards, Rules & Knowledge

**Type:** Reference
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-04-07
**Last Updated:** 2026-04-08

---

## Coding Standards

### Units Convention (MANDATORY)

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

- All functions: fully typed parameters AND return types
- Return Pydantic BaseModel or frozen dataclass, **never raw dict**
- `py.typed` PEP 561 marker in package
- `mypy --strict`: zero errors in CI
- `pyright` basic check in CI (for IDE support)

### Documentation

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

- **No relative imports** — following Polars pattern: `ban-relative-imports = "all"` in ruff
- Clean public API via `__init__.py` with explicit `__all__`
- Internal modules prefixed with `_` (e.g., `_internals/`)
- Users never import from internal paths

---

## Testing Standards

### 6 Test Types (for Every IS 456 Function)

| # | Type | Purpose | Example |
|---|------|---------|---------|
| 1 | **Unit tests** | Basic function behavior | `assert design_beam(...).is_safe()` |
| 2 | **Edge cases** | Zero values, minimum sections, maximum reinforcement | `design_beam(b_mm=150, ...)` |
| 3 | **Degenerate cases** | What happens at physical limits | `Mu_kNm=0`, `pt=0`, max allowed `pt` |
| 4 | **SP:16 benchmarks** | ±0.1% accuracy against published charts | Charts 1–62 known-answer tests |
| 5 | **Textbook examples** | Pillai & Menon, Varghese, Jain | Worked examples with known answers |
| 6 | **Hypothesis tests** | Property-based testing for invariants | Increasing moment → increasing steel |

### Quality Gates

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
