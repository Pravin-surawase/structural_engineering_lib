# Day 12: Testing Patterns for Structural Code (Deep Dive)

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** Critical
**Created:** 2026-04-08
**Last Updated:** 2026-04-09
**Prerequisites:** Days 1-7 (understand the IS 456 design pipeline)
**Library files:** `Python/tests/conftest.py`, `Python/tests/property/strategies.py`, `Python/tests/regression/test_golden_vectors_is456.py`, `Python/tests/performance/test_benchmarks.py`
**IS 456 Clauses:** All clauses — testing validates every formula in the library

---

## What You'll Learn Today

By the end of this module you'll understand:
- Why testing matters MORE in structural engineering than in typical software
- The 6 types of tests this library uses (and why each exists)
- How `conftest.py` shares fixtures across hundreds of tests
- What golden vector tests are and why they're sacred
- How Hypothesis generates thousands of random inputs to find edge cases
- How to run the test suite and read the output
- **Things to know** — tolerance traps, `pytest.approx` pitfalls, the "it passes but is wrong" anti-pattern
- **What can be done better** — coverage gaps, mutation testing, fuzz testing
- **Innovation** — metamorphic testing, differential testing against other IS 456 tools
- **Next repo must-add** — test pyramid ratios, automated golden vector generation

---

## Part 1: Why Testing Matters MORE Here

In a web app, a bug means a broken page. Users refresh, file a ticket, life goes on.

In a structural engineering library, a bug means **a building might be under-designed**. The steel area comes out 20% too low, the beam passes the code check, the contractor pours concrete — and years later, cracks appear under load.

The library computes values that go into real design documents:
- $A_{st}$ — how much steel to put in a beam
- $\tau_v$ vs $\tau_c$ — whether a beam needs extra stirrups
- $M_{u,lim}$ — the maximum moment a section can handle

If `calculate_ast_required()` returns 400 mm² when the correct answer is 500 mm², that's a **safety defect**. The only thing standing between correct math and a mistake is the test suite.

---

## Part 2: The 6 Test Types

```
┌──────────────────────────────────────────────┐
│  6. Performance Tests     ← "Is it fast?"     │
├──────────────────────────────────────────────┤
│  5. Regression Tests      ← "Old bugs back?"  │
├──────────────────────────────────────────────┤
│  4. Integration Tests     ← "Pipeline works?"  │
├──────────────────────────────────────────────┤
│  3. Property-Based (Hypo) ← "Invariants hold?" │
├──────────────────────────────────────────────┤
│  2. Golden Vector (SP:16) ← "Matches textbook?"│
├──────────────────────────────────────────────┤
│  1. Unit Tests            ← "Function correct?" │
└──────────────────────────────────────────────┘
```

### Type 1: Unit Tests

Call one function with known inputs, check the output.

```python
def test_mu_lim_standard_beam():
    """IS 456 Cl 38.1 — M25/Fe415, 300×450mm beam."""
    mu_lim = flexure.calculate_mu_lim(b=300, d=450, fck=25.0, fy=415.0)
    assert mu_lim == pytest.approx(171.11, rel=0.01)
```

Located in `Python/tests/unit/` — tests for shear, detailing, compliance, rebar, anchorage, adapters.

### Type 2: Golden Vector Tests (The Sacred Tests)

A "golden vector" is a pre-calculated result from **SP:16 Design Aids** — the official IS 456 reference tables published by the Bureau of Indian Standards.

```json
{
  "case_id": "G1",
  "description": "Singly reinforced beam — M25/Fe500",
  "mu_knm": 80.0,
  "vu_kn": 60.0,
  "expected": {
    "flexure": { "mu_lim": 202.914, "ast_required": 437.207 }
  }
}
```

```python
# ACTUAL test from test_golden_vectors_is456.py
@pytest.mark.golden
@pytest.mark.parametrize(
    "vector", _VECTORS["beam_flexure_cases"], ids=lambda v: v["case_id"]
)
def test_beam_flexure_golden(vector):
    common = _VECTORS["common_inputs"]
    res = api.design_beam_is456(
        b_mm=common["b_mm"], D_mm=common["D_mm"], d_mm=common["d_mm"],
        fck_nmm2=common["fck_nmm2"], fy_nmm2=common["fy_nmm2"],
        mu_knm=vector["mu_knm"], vu_kn=vector["vu_kn"],
    )
    exp = vector["expected"]
    tol = vector.get("tolerance", 1e-12)
    assert res.flexure.Mu_lim == pytest.approx(exp["flexure"]["mu_lim"], rel=tol)
```

**Golden test rules:**
- ±0.1% tolerance for table values, ±0.5% for chart interpolations
- Once passing, **permanent** — you can never delete one
- Expected values are **immutable** (only tolerance can be loosened, with justification)
- Marked with `@pytest.mark.golden`

### Type 3: Property-Based Tests (Hypothesis)

Generates **thousands of random inputs** and checks mathematical invariants:

```python
@given(b=beam_width(), d=effective_depth(), fck=concrete_grade(), fy=steel_grade())
def test_mu_lim_always_positive(b, d, fck, fy):
    """Mu_lim should always be positive for valid inputs."""
    mu_lim = flexure.calculate_mu_lim(b, d, float(fck), float(fy))
    assert mu_lim > 0

@given(b=beam_width(), d=effective_depth(), fck=concrete_grade(), fy=steel_grade())
def test_mu_lim_proportional_to_b(b, d, fck, fy):
    """Mu_lim doubles when width doubles (linear in b)."""
    mu_lim_1 = flexure.calculate_mu_lim(b, d, float(fck), float(fy))
    mu_lim_2 = flexure.calculate_mu_lim(2 * b, d, float(fck), float(fy))
    assert abs(mu_lim_2 - 2 * mu_lim_1) < 0.001 * mu_lim_1
```

**Custom strategies** from `tests/property/strategies.py`:

```python
CONCRETE_GRADES = [15, 20, 25, 30, 35, 40, 50, 60, 70, 80]
STEEL_GRADES = [250, 415, 500, 550]

def concrete_grade(): return st.sampled_from(CONCRETE_GRADES)
def steel_grade(): return st.sampled_from(STEEL_GRADES)
def beam_width(): return st.integers(min_value=150, max_value=600)
def effective_depth(): return st.integers(min_value=200, max_value=1700)
```

**Common invariants tested:**
- Non-negativity: $M_{u,lim} > 0$, $A_{st} > 0$
- Monotonicity: More depth → more capacity
- Linearity: $M_{u,lim} \propto b$
- Quadratic: $M_{u,lim} \propto d^2$

### Type 4: Integration Tests

Test the **whole pipeline**: CSV → design → detailing → BBS → report.

Located in `Python/tests/integration/` — catches interface mismatches between layers.

### Type 5: Regression Tests

Every fixed bug gets a test to prevent recurrence:

```python
def test_flanged_beam_effective_width_regression():
    """Regression: Issue #42 — bf computed from total depth instead of flange depth."""
    result = design_flanged_beam(bf_mm=1200, bw_mm=300, df_mm=120, ...)
    assert result.bf_effective == 1200  # Not the old wrong value
```

### Type 6: Performance Tests

```python
@pytest.mark.performance
def test_benchmark_calculate_mu_lim(benchmark):
    result = benchmark(flexure.calculate_mu_lim, b=300, d=450, fck=25, fy=415)
    assert result > 0
```

Uses `pytest-benchmark` to track timing across commits.

---

## Part 3: conftest.py — Shared Fixtures

### 3.1 Reusable Beam Configurations

```python
# conftest.py
@pytest.fixture()
def m25_fe415():
    return {"fck": 25.0, "fy": 415.0}

@pytest.fixture()
def standard_beam_230x500(m25_fe415):
    return {
        "b_mm": 230.0, "D_mm": 500.0, "d_mm": 450.0,
        "cover_mm": 25.0, **m25_fe415,
    }
```

### 3.2 Hypothesis Profiles

| Profile | Max Examples | Use Case |
|---------|-------------|----------|
| `default` | 100 | Local development |
| `dev` | 25 | Quick iteration |
| `ci` | 200 | CI (reproducible seed) |
| `exhaustive` | 1000 | Deep testing critical functions |

### 3.3 Session-Scoped Golden Vectors

```python
@pytest.fixture(scope="session")
def golden_vectors():
    data_file = Path(__file__).parent / "data" / "golden_vectors_is456.json"
    with open(data_file) as f:
        return json.load(f)
```

---

## Part 4: Test Organization

```
Python/tests/
├── conftest.py                ← Shared fixtures + Hypothesis config
├── data/
│   └── golden_vectors_is456.json  ← SP:16 reference data
├── unit/                      ← Type 1: Individual functions
├── regression/                ← Types 2+5: Golden vectors + bug fixes
├── integration/               ← Type 4: End-to-end pipeline
├── property/                  ← Type 3: Hypothesis random inputs
│   └── strategies.py          ← Custom strategies for IS 456
└── performance/               ← Type 6: Benchmarks
```

---

## Part 5: Running Tests

```bash
# From workspace root:
.venv/bin/pytest Python/tests/ -v                       # All tests
.venv/bin/pytest Python/tests/unit/ -v                   # Unit only
.venv/bin/pytest Python/tests/ -v -k "test_shear"        # Keyword filter
.venv/bin/pytest Python/tests/regression/ -v             # Golden + regression
.venv/bin/pytest Python/tests/ --cov=structural_lib      # With coverage
.venv/bin/pytest Python/tests/property/ --hypothesis-profile=ci  # 200 examples
```

---

## Part 6: Exercises

### Exercise 1: Run the Suite

```bash
.venv/bin/pytest Python/tests/ -v --tb=short 2>&1 | tail -30
```

Answer: How many passed? How long? Any golden vector case IDs?

### Exercise 2: Write a Golden Vector

```python
# Python/tests/test_my_first_test.py
import pytest
from structural_lib import flexure

def test_mu_lim_m30_fe500():
    """M30/Fe500, 300×550mm beam.
    Mu_lim = 0.133 × 30 × 300 × 550² ≈ 362.09 kNm
    """
    mu_lim = flexure.calculate_mu_lim(b=300, d=550, fck=30.0, fy=500.0)
    assert mu_lim == pytest.approx(362.09, rel=0.01)
```

```bash
.venv/bin/pytest Python/tests/test_my_first_test.py -v
```

---

## Part 7: Can You Explain? (Self-Check)

### Q1: Why 6 test types, not just unit tests?

<details><summary>Answer</summary>

Each catches different bugs: unit tests catch implementation errors, golden tests catch formula errors against SP:16, property tests catch edge cases across 1000s of inputs, integration tests catch interface mismatches between layers, regression tests prevent old bugs returning, performance tests catch slowdowns. No single type suffices.
</details>

### Q2: What makes golden tests "golden"?

<details><summary>Answer</summary>

Their expected values come from **authoritative external sources** — SP:16 design aids by the Bureau of Indian Standards. If our code disagrees with SP:16, the code is wrong. Expected values are immutable. Tolerance can only be loosened with documented justification.
</details>

### Q3: How does Hypothesis know valid structural inputs?

<details><summary>Answer</summary>

We teach it via custom strategies: `st.sampled_from(CONCRETE_GRADES)` picks from [15, 20, 25, ...80], not random integers. `beam_width()` generates 150-600mm. `assume(d <= 850)` skips invalid combos.
</details>

### Q4: Why `deadline=None` for Hypothesis?

<details><summary>Answer</summary>

Default Hypothesis fails if any example takes >200ms. Structural calculations (iterative designs, optimization) can legitimately take longer. `deadline=None` means "don't fail for slow math." Performance is tested separately with `pytest-benchmark`.
</details>

---

## Part 8: Things to Know (Critical Knowledge)

### 8.1 The `pytest.approx` Trap

```python
# ❌ DANGER: rel=0.01 means ±1% — too loose for golden tests
assert result == pytest.approx(209.59, rel=0.01)  # Passes for 207.49-211.69!

# ✅ CORRECT: Use tight tolerance for golden vectors
assert result == pytest.approx(209.59, rel=1e-3)  # ±0.1% (SP:16 table accuracy)

# ✅ BEST: Use absolute tolerance when values are near zero
assert result == pytest.approx(0.001, abs=1e-6)   # rel fails near zero
```

### 8.2 The "It Passes But Is Wrong" Anti-Pattern

```python
# ❌ This test ALWAYS passes — it tests nothing
def test_design_beam():
    result = design_beam_is456(units="IS456", b_mm=300, ...)
    assert result is not None  # Meaningless — any non-None passes

# ✅ CORRECT: Assert specific numerical results
def test_design_beam():
    result = design_beam_is456(units="IS456", b_mm=300, ...)
    assert result.flexure.Ast_required == pytest.approx(876.5, rel=1e-3)
    assert result.flexure.is_safe is True
    assert result.shear.sv_mm <= 300  # Max spacing per IS 456
```

### 8.3 Floating-Point Equality — Never Use `==`

```python
# ❌ FAILS due to floating-point representation:
assert 0.1 + 0.2 == 0.3       # False! (0.30000000000000004)

# ✅ Always use pytest.approx:
assert 0.1 + 0.2 == pytest.approx(0.3)  # True
```

### 8.4 Tests Must Be Deterministic

```python
# ❌ Non-deterministic — fails randomly
import random
def test_random_beam():
    b = random.randint(200, 500)  # Different every run!
    result = design_beam(b=b, ...)
    assert result.is_safe

# ✅ Use Hypothesis instead — same seed = same results:
@given(b=st.integers(200, 500))
def test_hypothesis_beam(b):
    result = design_beam(b=b, ...)
    assert result.is_safe  # Reproducible!
```

### 8.5 Coverage vs Confidence

```
85% line coverage ≠ 85% confidence the code is correct.

Coverage tells you:   "This line executed during tests"
Coverage doesn't say: "This line produced the correct output"

Example: A test that calls calculate_mu_lim() but doesn't assert
the result gives 100% coverage on that function with 0% verification.
```

---

## Part 9: What Can Be Done Better

### 9.1 Current Issues

| Issue | Current State | Better Approach |
|-------|--------------|-----------------|
| **Golden vector coverage** | ~12 beam cases | 50+ cases across all design scenarios |
| **No mutation testing** | Tests might be too weak | `mutmut` to verify tests catch mutations |
| **Column tests lag** | Fewer column golden vectors | Full column test parity with beams |
| **No fuzz testing** | Random but structured (Hypothesis) | True fuzz testing for edge cases |
| **Hypothesis settings** | Per-profile only | Per-function `@settings` overrides |

### 9.2 Missing Mutation Testing

```bash
# Mutation testing: change code slightly, verify tests fail
# If tests still pass after mutating code → tests are weak

# Install: pip install mutmut
# Run: mutmut run --paths-to-mutate Python/structural_lib/codes/is456/beam/flexure.py
# Result: "42 mutants killed, 3 survived" → 3 weak spots in tests
```

### 9.3 Test Pyramid Imbalance

```
Current (estimated):
  Unit: 60%
  Golden: 15%
  Property: 10%
  Integration: 10%
  Regression: 3%
  Performance: 2%

Ideal for structural code:
  Unit: 30%
  Golden: 30%  ← More golden vectors needed
  Property: 20%
  Integration: 10%
  Regression: 5%
  Performance: 5%
```

---

## Part 10: Innovation Directions

### 10.1 Metamorphic Testing

Instead of knowing the exact output, test **relationships between outputs**:

```python
def test_metamorphic_scaling():
    """If all loads scale by 2×, Ast should also scale by ~2×."""
    r1 = design_beam(mu_knm=100, vu_kn=50, ...)
    r2 = design_beam(mu_knm=200, vu_kn=100, ...)  # 2× loads
    ratio = r2.flexure.Ast_required / r1.flexure.Ast_required
    assert 1.5 < ratio < 2.5  # Approximately 2× steel
```

### 10.2 Differential Testing Against Other Tools

```python
def test_against_etabs_verification():
    """Compare our library output against ETABS verification results."""
    our_result = design_beam_is456(b_mm=300, D_mm=500, ...)
    etabs_result = load_etabs_verification("beam_B1.json")
    assert our_result.flexure.Ast_required == pytest.approx(
        etabs_result["Ast_required"], rel=0.05  # ±5% acceptable
    )
```

### 10.3 Snapshot Testing

```python
# Record a "snapshot" of the full result:
def test_design_snapshot(snapshot):
    result = design_beam_is456(units="IS456", b_mm=300, ...)
    assert result.to_dict() == snapshot
    # First run: creates snapshot file
    # Later runs: compares against snapshot — any change flags review
```

### 10.4 Innovation Comparison

| Technique | What It Catches | Difficulty | Value |
|-----------|----------------|-----------|-------|
| Mutation testing | Weak/useless tests | Low | High |
| Metamorphic testing | Relationship violations | Medium | High |
| Differential testing | Disagreement with other tools | Medium | Very High |
| Snapshot testing | Unexpected output changes | Low | Medium |
| Chaos testing | Random failures under stress | High | Medium |

---

## Part 11: Next Repo Must-Add

### 11.1 Test Pyramid Ratios — Enforced

```yaml
# test_config.yaml — enforce test ratios
pyramid:
  unit: { min_pct: 25, max_pct: 40 }
  golden: { min_pct: 25, max_pct: 35 }
  property: { min_pct: 15, max_pct: 25 }
  integration: { min_pct: 8, max_pct: 15 }
  regression: { min_pct: 3, max_pct: 8 }
  performance: { min_pct: 3, max_pct: 8 }
```

### 11.2 Automated Golden Vector Generation

```python
# Generate golden vectors from SP:16 tables programmatically:
def generate_golden_vectors():
    vectors = []
    for fck in [20, 25, 30]:
        for fy in [415, 500]:
            for pt in [0.5, 1.0, 1.5, 2.0]:
                mu = sp16_lookup(fck, fy, pt)  # From digitized SP:16 tables
                vectors.append({
                    "case_id": f"G_{fck}_{fy}_{pt}",
                    "fck": fck, "fy": fy, "pt": pt,
                    "expected_mu": mu,
                })
    return vectors
```

### 11.3 Day-1 Checklist for Next Repo Testing

- [ ] Mutation testing setup (`mutmut`) — run weekly in CI
- [ ] Test pyramid enforcement — CI fails if golden < 25%
- [ ] Automated golden vector generation from digitized SP:16
- [ ] Metamorphic test suite (relationship tests)
- [ ] Differential testing against at least one other IS 456 tool
- [ ] Snapshot testing for full design results
- [ ] Per-function Hypothesis `@settings` overrides
- [ ] Coverage badge showing branch coverage (not just line)
- [ ] Test flake detection — quarantine flaky tests automatically
- [ ] Dead test detection — remove tests that asserting nothing meaningful

---

## Part 12: Summary

| Concept | Purpose | Location |
|---------|---------|----------|
| **Unit tests** | Check individual functions | `tests/unit/` |
| **Golden vectors** | Validate against SP:16 (sacred) | `tests/regression/` |
| **Property tests** | Hypothesis random invariant checks | `tests/property/` |
| **Integration tests** | End-to-end pipeline | `tests/integration/` |
| **Regression tests** | Prevent old bugs | `tests/regression/` |
| **Performance tests** | Benchmark timing | `tests/performance/` |
| **conftest.py** | Shared fixtures, Hypothesis profiles | `tests/conftest.py` |
| **Custom strategies** | IS 456-valid Hypothesis inputs | `tests/property/strategies.py` |
| **`pytest.approx`** | Floating-point tolerance | Everywhere |
| **`@pytest.mark.golden`** | Mark test as permanent | Golden tests |

---

## 📎 References

- **SP:16:1980** — Design Aids for Reinforced Concrete (golden vector source)
- **Hypothesis docs:** https://hypothesis.readthedocs.io/
- **pytest docs:** https://docs.pytest.org/
- **Test suite:** `Python/tests/`
- **Golden vectors data:** `Python/tests/data/golden_vectors_is456.json`

---

## What's Next?

**Day 13: Exports & Reports** — You've designed a beam and tested the math. Now we need to turn those results into documents that construction teams can actually use: Bar Bending Schedules (BBS), CAD drawings (DXF), and design reports (HTML/PDF). That's where `bbs.py`, `dxf_export.py`, and `report.py` come in.
