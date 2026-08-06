# Module 6: Testing — How You Know It Works

## The Big Idea

Testing is writing code that checks if your other code works correctly. Without tests, you're guessing. With tests, you have proof. In engineering software, "probably works" isn't good enough — a wrong answer could mean a collapsed building.

---

## Part 1: Why Test?

### Without tests:
```
You write code → You run it once → "Looks right" → Ship it

3 months later:
  Someone changes calculate_shear() → Your flexure code breaks
  Nobody notices → Wrong steel area in production → 💀
```

### With tests:
```
You write code → You write tests → Tests pass → Ship it

3 months later:
  Someone changes calculate_shear() → Tests run automatically
  Test fails → Developer sees "FAILED: test_flexure_basic" → Fixes it → Safe
```

### What tests give you:
1. **Confidence** — You know it works (not "think" — KNOW)
2. **Safety net** — Changes that break things are caught immediately
3. **Documentation** — Tests show how the code is meant to be used
4. **Design feedback** — Hard-to-test code is usually badly designed

---

## Part 2: Types of Tests

```
                    Fewer tests, more coverage each
                    ┌───────────┐
                    │    E2E    │  ← Test the whole system
                    │   Tests   │    "User clicks Design, sees results"
                    ├───────────┤
                    │Integration│  ← Test components working together
                    │   Tests   │    "API endpoint returns correct JSON"
                    ├───────────┤
                    │           │
                    │   Unit    │  ← Test individual functions
                    │   Tests   │    "calculate_ast(300, 500) == 1206.5"
                    │           │
                    └───────────┘
                    More tests, each tests less
```

### Unit Tests (most common, most important)
Test a single function or class in isolation.

```python
def test_calculate_ast():
    """Test steel area calculation for a known case."""
    result = calculate_ast_required(
        b_mm=300, d_mm=500, fck=25, fy=500, Mu_kNm=150
    )
    assert abs(result - 1206.5) < 1.0  # Within 1 mm²
```

### Integration Tests
Test multiple parts working together.

```python
def test_beam_design_endpoint():
    """Test the full API endpoint."""
    response = client.post("/api/v1/design/beam", json={
        "b_mm": 300, "d_mm": 500, "fck": 25, "fy": 500, "Mu_kNm": 150
    })
    assert response.status_code == 200
    assert response.json()["flexure"]["status"] == "SAFE"
```

### End-to-End (E2E) Tests
Test the entire system from the user's perspective.

```
Open browser → Fill form → Click Design → See results → Verify numbers
```

### How many of each?

| Type | Quantity | Speed | Maintenance |
|------|----------|-------|-------------|
| Unit | Many (100+) | Fast (ms each) | Low |
| Integration | Some (20-50) | Medium (seconds) | Medium |
| E2E | Few (5-10) | Slow (minutes) | High |

**Rule:** Most of your tests should be unit tests.

---

## Part 3: pytest — Python's Test Framework

pytest is the standard Python testing tool. It's simple and powerful.

### Writing a test:
```python
# tests/test_flexure.py

def test_ast_positive_result():
    """Steel area should be positive for valid inputs."""
    result = calculate_ast_required(b_mm=300, d_mm=500, fck=25, fy=500, Mu_kNm=150)
    assert result > 0

def test_ast_zero_moment():
    """Zero moment = zero steel."""
    result = calculate_ast_required(b_mm=300, d_mm=500, fck=25, fy=500, Mu_kNm=0)
    assert result == 0

def test_ast_negative_width_raises():
    """Negative width should raise an error."""
    with pytest.raises(ValueError):
        calculate_ast_required(b_mm=-300, d_mm=500, fck=25, fy=500, Mu_kNm=150)
```

### Running tests:
```bash
# Run all tests
.venv/bin/pytest Python/tests/ -v

# Run one file
.venv/bin/pytest Python/tests/test_flexure.py -v

# Run tests matching a name
.venv/bin/pytest Python/tests/ -v -k "test_shear"

# Run with coverage
.venv/bin/pytest Python/tests/ --cov=structural_lib --cov-report=term-missing
```

### Test output:
```
Python/tests/test_flexure.py::test_ast_positive_result PASSED
Python/tests/test_flexure.py::test_ast_zero_moment PASSED
Python/tests/test_flexure.py::test_ast_negative_width_raises PASSED

========================= 3 passed in 0.12s =========================
```

---

## Part 4: Arrange-Act-Assert — The Test Pattern

Every test follows this structure:

```python
def test_beam_flexure():
    # ARRANGE — set up the inputs
    b_mm = 300
    d_mm = 500
    fck = 25
    fy = 500
    Mu_kNm = 150

    # ACT — call the function
    result = calculate_ast_required(b_mm, d_mm, fck, fy, Mu_kNm)

    # ASSERT — check the output
    assert result > 0
    assert result < 5000  # Sanity check: not absurdly large
    assert abs(result - 1206.5) < 1.0  # Close to known answer
```

**Arrange:** Prepare everything your test needs.
**Act:** Do the one thing you're testing.
**Assert:** Verify the result is correct.

---

## Part 5: What to Test (and What Not To)

### DO test:
```
✅ Core business logic (IS 456 formulas)
✅ Edge cases (zero, negative, very large numbers)
✅ Error conditions (invalid input raises proper errors)
✅ Boundary values (minimum concrete grade, maximum steel ratio)
✅ Known benchmark results (hand-calculated or textbook examples)
```

### DON'T test:
```
❌ Python's built-in functions (they already work)
❌ Third-party libraries (they have their own tests)
❌ Simple getters/setters with no logic
❌ Implementation details (test WHAT, not HOW)
```

### Example — what vs how:
```python
# ✅ GOOD: Tests the WHAT (result is correct)
def test_ast_result():
    result = calculate_ast_required(b_mm=300, d_mm=500, fck=25, fy=500, Mu_kNm=150)
    assert abs(result - 1206.5) < 1.0

# ❌ BAD: Tests the HOW (implementation detail)
def test_ast_uses_quadratic_formula():
    # This tests internal implementation, not behavior
    # If someone refactors the formula, this breaks even if results are correct
    assert "quadratic" in inspect.getsource(calculate_ast_required)
```

---

## Part 6: Fixtures — Reusable Test Setup

When multiple tests need the same setup, use **fixtures**.

```python
import pytest

@pytest.fixture
def standard_beam():
    """A standard M25 beam for testing."""
    return {
        "b_mm": 300,
        "d_mm": 500,
        "fck": 25,
        "fy": 500,
        "Mu_kNm": 150,
    }

def test_flexure(standard_beam):
    result = design_beam_is456(**standard_beam)
    assert result["flexure"]["status"] == "SAFE"

def test_shear(standard_beam):
    standard_beam["Vu_kN"] = 75
    result = design_beam_is456(**standard_beam)
    assert result["shear"]["status"] == "SAFE"
```

**Fixtures prevent copy-paste:** Define setup once, reuse everywhere.

---

## Part 7: Test Coverage — How Much Is Tested?

**Coverage** measures what percentage of your code is exercised by tests.

```bash
.venv/bin/pytest Python/tests/ --cov=structural_lib --cov-report=term-missing
```

Output:
```
Name                               Stmts   Miss  Cover   Missing
----------------------------------------------------------------
structural_lib/codes/is456/flexure    45      3    93%   78-80
structural_lib/codes/is456/shear      38      0   100%
structural_lib/services/api           92     12    87%   145-156
----------------------------------------------------------------
TOTAL                                 175     15    91%
```

### Coverage guidelines:

| Coverage | Assessment |
|----------|-----------|
| < 50% | Dangerous — most code untested |
| 50-70% | Minimum acceptable |
| 70-85% | Good — covers main paths |
| 85-95% | Very good — covers edge cases |
| 100% | Rarely needed — diminishing returns |

**This project targets:** 85% branch coverage.

**Warning:** High coverage ≠ good tests. You can have 100% coverage with useless assertions.

---

## Part 8: Benchmark Tests — Engineering Verification

For engineering code, you need **benchmark tests** — tests against known correct answers (from textbooks, hand calculations, or reference software).

```python
def test_is456_flexure_benchmark():
    """
    Benchmark: SP-16 Example 1.1
    M25 concrete, Fe500 steel, b=300mm, d=450mm, Mu=180kNm
    Expected Ast = 1340 mm² (from SP-16 chart)
    """
    result = calculate_ast_required(
        b_mm=300, d_mm=450, fck=25, fy=500, Mu_kNm=180
    )
    # Allow 2% tolerance for rounding differences
    assert abs(result - 1340) / 1340 < 0.02, (
        f"Expected ~1340 mm², got {result} mm²"
    )
```

### Why benchmark tests matter:
- A formula can be coded wrong and still produce "reasonable" numbers
- Benchmark tests catch subtle math errors
- They prove compliance with IS 456:2000
- They give users confidence in the library

---

## Part 9: Test-Driven Development (TDD)

TDD means writing the test BEFORE writing the code.

```
Step 1: Write a failing test
   def test_shear_capacity():
       result = calculate_shear_capacity(b_mm=300, d_mm=500, fck=25)
       assert abs(result - 112.5) < 1.0

   → FAILS (function doesn't exist yet)

Step 2: Write the minimum code to pass
   def calculate_shear_capacity(b_mm, d_mm, fck):
       tau_c = 0.25 * sqrt(fck)  # IS 456 simplified
       return tau_c * b_mm * d_mm / 1000

   → PASSES

Step 3: Refactor (improve without changing behavior)
   → Tests still pass = safe to refactor
```

### TDD cycle:
```
  ┌─────────────┐
  │  Write Test  │ ← RED (test fails)
  │  (what you   │
  │   want)      │
  └──────┬───────┘
         │
         ▼
  ┌─────────────┐
  │  Write Code  │ ← GREEN (test passes)
  │  (minimum to │
  │   pass test) │
  └──────┬───────┘
         │
         ▼
  ┌─────────────┐
  │  Refactor    │ ← CLEAN (improve code)
  │  (keep tests │
  │   passing)   │
  └──────┴───────┘
         │
         └──→ Repeat
```

**Not everyone uses TDD.** But writing tests BEFORE or DURING coding (not after) catches design problems early.

---

## Part 10: Common Testing Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| No tests at all | Every change is a gamble | Start with the most critical path |
| Testing only happy path | Edge cases cause bugs | Test zeros, negatives, extremes |
| Tests that depend on each other | Test order matters, flaky | Each test must be independent |
| Testing implementation, not behavior | Refactoring breaks tests | Test inputs and outputs only |
| Asserting too little | `assert result is not None` proves nothing | Assert specific values |
| Tests that take minutes | Nobody runs them | Keep unit tests under 1 second total |
| No CI test automation | Tests only run locally | Set up GitHub Actions (see Module 10) |

---

## Part 11: This Project's Testing Structure

```
Python/tests/
├── test_flexure.py           ← IS 456 flexure calculations
├── test_shear.py             ← IS 456 shear calculations
├── test_detailing.py         ← Rebar detailing
├── test_api.py               ← API integration tests
├── test_adapters.py          ← CSV adapter tests
├── test_beam_pipeline.py     ← Multi-step design workflow
├── test_column.py            ← Column design
├── test_geometry_3d.py       ← 3D geometry generation
├── benchmarks/               ← Known-answer verification
└── conftest.py               ← Shared fixtures

react_app/
├── vitest.config.ts          ← Vitest (React test framework)
└── src/**/*.test.tsx         ← Component tests (co-located)

fastapi_app/tests/
└── test_routes.py            ← API endpoint tests
```

Run commands:
```bash
.venv/bin/pytest Python/tests/ -v                   # All Python tests
.venv/bin/pytest Python/tests/ -v -k "test_shear"   # Specific tests
cd react_app && npx vitest run                       # React tests
```

---

## Part 12: Exercises

1. **Write your first test:** Pick any function from IS 456 math. Write a test with a hand-calculated expected result.
2. **Run the test suite:** Execute `.venv/bin/pytest Python/tests/ -v`. How many tests pass? Any failures?
3. **Check coverage:** Run with `--cov`. Which files have the lowest coverage?
4. **Write a failing test first:** Think of a function that doesn't exist. Write a test for it. Then implement the function.

---

## Part 13: Self-Check

1. **What are the three types of tests?** Unit, integration, end-to-end.
2. **What's the Arrange-Act-Assert pattern?** Set up → call function → check result.
3. **Why are benchmark tests important for engineering code?** They verify against known correct answers from textbooks/standards.
4. **What's the TDD cycle?** Write failing test → write code to pass → refactor.
5. **What's a good coverage target?** 85% branch coverage (for this project).
6. **Should you test implementation or behavior?** Behavior (inputs → outputs).

---

## Key Takeaway

> Tests are not extra work — they're **insurance**. Every test you write is a guarantee: "this calculation will NEVER silently break." In engineering software, that guarantee can literally save lives.

**Next:** [Module 7 — Frontend](07-frontend.md) explains how user interfaces are built with React.
