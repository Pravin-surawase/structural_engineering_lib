# Test Organization & Coverage Audit

**Task:** TASK-170
**Date:** 2026-01-06
**Status:** Complete
**Scope:** Python test suite organization, coverage gaps, test quality, and structure.

---

## Executive Summary
The test suite is comprehensive in scope (59 test files, 2200+ tests) and covers core modules, CLI, insights, and regression vectors. The main structural gap is organizational: tests live in a single flat directory, making it harder to distinguish unit vs integration vs regression tests. Property-based testing exists but is implemented manually with parametric sweeps rather than a generator-based framework. Coverage appears strong overall (~86% per AI context), but there is no documented coverage by module or an explicit benchmark/performance suite.

## Methodology
- Listed test files in `Python/tests` and counted `test_*.py` files.
- Reviewed `Python/tests/data` and `Python/tests/fixtures`.
- Spot-checked property tests in `test_property_invariants.py`.
- Used project metrics in `docs/AI_CONTEXT_PACK.md` for coverage context.

## Findings

### 1) Organization Assessment
Current structure:
- **Flat test layout** under `Python/tests/`.
- Data stored in `Python/tests/data/`.
- Fixtures in `Python/tests/fixtures/`.

Implications:
- Harder to separate unit vs integration tests.
- Harder to isolate slow tests or external-dependency tests.

### 2) Category Coverage (Estimated)
- **Unit tests:** High (core modules, math checks, validation, detailing).
- **Integration tests:** Present (CLI, job runner, report generation).
- **Property tests:** Present but manual (`test_property_invariants.py`), no Hypothesis.
- **Regression tests:** Present (golden vectors and fixtures).
- **Performance tests:** Not explicit; no pytest-benchmark suite found.

### 3) Quantitative Coverage Snapshot (2026-01-06)
Run: `.venv/bin/python -m pytest Python/tests --cov=structural_lib --cov-report=term-missing`
- **Result:** 0 failed, 2270 passed.
- **Overall coverage:** 86% (Stmts: 5470, Miss: 778).

Modules with coverage below 80% (selection):
- `Python/structural_lib/job_cli.py`: 38%
- `Python/structural_lib/__main__.py`: 69%
- `Python/structural_lib/api.py`: 77%
- `Python/structural_lib/__init__.py`: 76%
- `Python/structural_lib/excel_bridge.py`: 0%
- `Python/structural_lib/constants.py`: 0%
- `Python/structural_lib/intelligence.py`: 0%

### 4) Test Collection Stats (AST-based)
Run: AST scan of `Python/tests/test_*.py` (function-level count).
- **Test files:** 59
- **Test functions:** 900
- **Assert statements:** 1,984
- **Asserts per test (avg):** 2.20

Top files by assert count:
- `Python/tests/test_cli.py` (170)
- `Python/tests/test_rebar_optimizer.py` (124)
- `Python/tests/test_validation.py` (117)
- `Python/tests/test_report.py` (112)
- `Python/tests/test_error_schema.py` (98)

Top files by test count:
- `Python/tests/test_validation.py` (78)
- `Python/tests/test_cli.py` (64)
- `Python/tests/test_report.py` (44)
- `Python/tests/test_rebar_optimizer.py` (42)
- `Python/tests/test_detailing.py` (41)

Note: parametrized tests expand at runtime, so executed test cases are higher than the function count.

### 5) Pytest Collection Stats (collect-only)
Run: `.venv/bin/python -m pytest Python/tests --collect-only`
- **Nodeids collected:** 2,270
- **Parametrized nodeids:** 1,407 (nodeids with `[...]` parameters)

### 6) Test Durations (slowest 20)
Run: `.venv/bin/python -m pytest Python/tests --durations=20`
- **Result:** 0 failed, 2270 passed.
- **Slowest calls observed (top 5):**
  - `tests/test_cli.py::test_module_execution_with_subprocess` (0.29s)
  - `tests/test_cli_report_regression.py::test_cli_critical_from_job_output` (0.21s)
  - `tests/test_cli.py::test_help_via_subprocess` (0.21s)
  - `tests/test_cli_report_regression.py::test_cli_report_from_design_results` (0.21s)
  - `tests/test_excel_integration.py::TestProcessing::test_batch_generate_from_csv` (0.08s)

### 7) Coverage Gaps (Qualitative)
- Coverage by module is not documented in a single place.
- Some workflows (SmartDesigner, comparison) have tests but lack full end-to-end tutorial-backed examples.
- Performance regression tracking not defined.

### 8) Test Quality Signals
- Tests use parametrized sweeps and golden vectors.
- Parity and boundary tests exist.
- No explicit markers for slow vs fast tests.

## Recommendations
1. **Introduce subdirectories** within `Python/tests/` for `unit/`, `integration/`, `regression/`, `property/`, `performance/`.
2. **Add markers** (e.g., `@pytest.mark.slow`) for long-running tests and configure default selection.
3. **Create a small benchmark suite** using `pytest-benchmark` for core calculations.
4. **Document module-level coverage** (auto-generate with coverage config and add to docs).
5. **Consider Hypothesis** for property tests to broaden input space.

## Action Plan

### Quick Wins (1-2 hrs)
- Add pytest markers for slow/integration tests.
- Add README in `Python/tests/` describing test categories.

### Medium Effort (1-2 days)
- Restructure tests into subdirectories and update pytest configuration if needed.
- Add performance baseline tests for flexure/shear pipelines.

### Major Work (3-5 days)
- Add property-based tests via Hypothesis for core formulas.
- Implement module-by-module coverage reporting.

## Testing Standards (Proposed)
- **Naming:** `test_<module>.py` within category subfolders.
- **Assertions:** avoid `assert True` and prefer domain-specific assertions with tolerances.
- **Determinism:** no random tests without fixed seeds.
- **Performance:** include a small set of benchmarks to guard regressions.

## Additional Research Opportunities

### High Value Additions (RECOMMENDED)

1. **Module Coverage Matrix** (1 hour) - **HIGH PRIORITY**
   ```bash
   # Generate detailed coverage report
   cd Python
   pytest --cov=structural_lib --cov-report=html --cov-report=term-missing

   # Per-module coverage
   pytest --cov=structural_lib --cov-report=term | grep structural_lib
   ```
   **Output format:**
   ```
   Module                    Stmts   Miss  Cover
   structural_lib/api.py       234     15    94%
   structural_lib/flexure.py   189      8    96%
   structural_lib/shear.py     156     12    92%
   ```
   **Benefit:** Identify under-tested modules

2. **Test Quality Metrics** (1-2 hours) - **HIGH PRIORITY**
   ```bash
   # Test duration analysis
   pytest --durations=20 > test_durations.txt

   # Test count by category
   pytest --collect-only | grep "<Function" | wc -l

   # Assertion density
   rg "assert" tests/ --count | sort -t: -k2 -n

   # Parametrized test expansion
   pytest --collect-only | grep "\[" | wc -l
   ```
   **Metrics to track:**
   - Assertions per test (target: 3-5)
   - Test duration distribution (target: <100ms for 90%)
   - Parametrization usage (target: >30% of tests)

3. **Coverage Trend Analysis** (2 hours)
   ```bash
   # Historical coverage (if tracked)
   git log --all --pretty=format:"%h %ad" --date=short | while read hash date; do
     git checkout $hash
     coverage=$(pytest --cov=structural_lib --cov-report=term | grep TOTAL | awk '{print $4}')
     echo "$date,$hash,$coverage"
   done > coverage_history.csv
   ```
   **Benefit:** Track coverage improvement over time

4. **Edge Case Coverage** (1-2 hours)
   ```bash
   # Analyze boundary condition testing
   rg "(min|max|zero|negative|None|empty)" tests/ --count

   # Check for property-based test coverage
   rg "@pytest.mark.parametrize" tests/ --count
   rg "@given|hypothesis" tests/ --count
   ```
   **Benefit:** Ensure robust boundary testing

5. **Test Maintenance Cost** (1 hour)
   ```bash
   # Tests that frequently fail
   git log --all --grep="test" --grep="fix" --oneline | wc -l

   # Tests with many changes
   for test in tests/test_*.py; do
     changes=$(git log --oneline -- "$test" | wc -l)
     echo "$test: $changes changes"
   done | sort -t: -k2 -n | tail -10
   ```
   **Benefit:** Identify brittle tests needing improvement

6. **Mutation Testing** (2-3 hours, optional)
   ```bash
   # Install mutmut
   pip install mutmut

   # Run mutation testing (slow)
   mutmut run --paths-to-mutate=Python/structural_lib/flexure.py
   mutmut results
   ```
   **Benefit:** Measure test suite effectiveness

## Enhancement Recommendations

### For Implementation Phase

1. **Test Directory Structure** (1-2 days)
   ```
   Python/tests/
   ├── unit/           # Fast, isolated tests
   │   ├── test_flexure.py
   │   ├── test_shear.py
   │   └── ...
   ├── integration/    # Multi-module tests
   │   ├── test_job_runner.py
   │   └── test_cli.py
   ├── regression/     # Golden vectors
   │   ├── test_benchmarks.py
   │   └── fixtures/
   ├── property/       # Property-based tests
   │   └── test_invariants.py
   └── performance/    # Speed benchmarks
       └── test_benchmarks.py
   ```

2. **Pytest Configuration with Markers**
   ```toml
   [tool.pytest.ini_options]
   markers = [
       "unit: Fast unit tests",
       "integration: Multi-module integration tests",
       "slow: Tests taking >1s",
       "regression: Golden vector tests",
       "property: Property-based tests",
       "performance: Performance benchmarks",
   ]
   ```

   Usage:
   ```bash
   pytest -m "not slow"  # Fast tests only
   pytest -m integration  # Integration tests
   ```

3. **Performance Benchmark Suite**
   ```python
   import pytest

   @pytest.mark.performance
   @pytest.mark.benchmark(group="flexure")
   def test_flexure_speed(benchmark):
       """Benchmark flexure calculation speed."""
       result = benchmark(calculate_mu_lim, b=300, d=450, fck=25, fy=415)
       assert result > 0
   ```

4. **Coverage Requirements**
   ```toml
   [tool.coverage.run]
   branch = true
   source = ["structural_lib"]

   [tool.coverage.report]
   precision = 2
   show_missing = true
   skip_covered = false

   fail_under = 90  # Minimum coverage
   exclude_lines = [
       "pragma: no cover",
       "def __repr__",
       "raise AssertionError",
       "raise NotImplementedError",
   ]
   ```

### Tracking Metrics
```bash
# Test quality dashboard
pytest --collect-only | grep "<Function" | wc -l  # Total tests
pytest --cov=structural_lib --cov-report=term | grep "TOTAL"
pytest --durations=10  # Slowest tests
rg "@pytest.mark.parametrize" tests/ | wc -l  # Parametrized tests
rg "TODO|FIXME|skip" tests/ | wc -l  # Incomplete tests (target: 0)
```

## Module Coverage Baseline (To Be Added)

**Run this and add results to document:**
```bash
cd Python
pytest --cov=structural_lib --cov-report=term-missing | tee coverage_detail.txt
```

**Expected output format:**
```
Name                              Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------------------------------
structural_lib/__init__.py           12      0      0      0   100%
structural_lib/api.py               234     15     48      3    94%   145-156, 234
structural_lib/flexure.py           189      8     32      2    96%   234-241
structural_lib/shear.py             156     12     28      1    92%   189-200
...
--------------------------------------------------------------------------------
TOTAL                              2847    154    482     18    86%
```

## Test Quality Baseline (To Be Added)

**Run these and add results:**
```bash
# 1. Test count by type
pytest --collect-only | grep "<Function" | wc -l

# 2. Slow tests (>1s)
pytest --durations=0 | grep "1\.[0-9]\+s" | wc -l

# 3. Assertion density
total_asserts=$(rg "assert" tests/ | wc -l)
total_tests=$(pytest --collect-only | grep "<Function" | wc -l)
echo "Assertions per test: $(echo "scale=2; $total_asserts / $total_tests" | bc)"

# 4. Parametrized tests
rg "@pytest.mark.parametrize" tests/ | wc -l
```

## References
- `Python/tests/`
- `Python/tests/test_property_invariants.py`
- `docs/AI_CONTEXT_PACK.md`
- [pytest documentation](https://docs.pytest.org/)
- [Coverage.py documentation](https://coverage.readthedocs.io/)
- [pytest-benchmark](https://pytest-benchmark.readthedocs.io/)
