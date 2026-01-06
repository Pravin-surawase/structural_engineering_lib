# Test Suite Organization

This document describes the test taxonomy and structure for the structural_engineering_lib test suite.

## Overview

**Total Tests:** 2270+ tests across 59 test files
**Coverage:** 86% (5470 statements, 778 missing)
**Structure:** Organized by test category for improved discoverability and selective execution

## Test Categories

### 1. Unit Tests (`unit/`)

**Purpose:** Fast, isolated tests for core calculation modules
**Scope:** Single-module tests with no external dependencies
**Speed:** <100ms per test
**File Count:** 12 files

**Files:**
- `test_detailing.py` - Reinforcement detailing calculations
- `test_serviceability.py` - Deflection and crack width checks
- `test_shear.py` - Shear strength calculations
- `test_structural.py` - Structural analysis functions
- `test_ductile.py` - Ductile detailing requirements
- `test_error_schema.py` - Error handling schema
- `test_input_validation.py` - Input validation logic
- `test_validation.py` - General validation functions
- `test_compliance.py` - IS 456:2000 compliance checks
- `test_compliance_validation.py` - Compliance validation rules
- `test_flange_width.py` - Flange width calculations
- `test_units_boundary.py` - Unit boundary conditions

**Run Command:**
```bash
pytest tests/unit/ -v
# Or with marker:
pytest -m unit -v
```

### 2. Integration Tests (`integration/`)

**Purpose:** Multi-module workflows and external integrations
**Scope:** API endpoints, CLI commands, export formats, optimizers
**Speed:** 100ms-1s per test
**File Count:** 38 files

**Categories:**
- **API Tests** (4 files): `test_api_*.py` - Public API entrypoints
- **CLI Tests** (2 files): `test_cli*.py` - Command-line interface
- **Export Tests** (5 files): `test_bbs*.py`, `test_dxf_*.py` - BBS and DXF generation
- **Excel Integration** (2 files): `test_excel_*.py` - Excel add-in functionality
- **Cost/Optimization** (4 files): `test_cost_*.py`, `test_costing.py` - Cost optimization
- **Insights** (6 files): `test_insights_*.py` - Smart insights module
- **Job Runner** (2 files): `test_job_*.py` - Batch processing
- **Reports** (1 file): `test_report.py` - Report generation
- **Smart Designer** (1 file): `test_smart_designer.py` - AI-assisted design
- **Other** (11 files): Contracts, wrappers, edges, deprecation

**Run Command:**
```bash
pytest tests/integration/ -v
# Or with marker:
pytest -m integration -v
```

### 3. Regression Tests (`regression/`)

**Purpose:** Golden vector tests and VBA parity verification
**Scope:** Known-good reference results, prevent regressions
**Speed:** Variable (some slow)
**File Count:** 8 files

**Files:**
- `test_golden_vectors_is456.py` - IS 456:2000 golden vectors
- `test_parity_vectors.py` - Python/VBA parity vectors
- `test_vba_parity.py` - VBA parity validation
- `test_verification_pack.py` - Comprehensive verification pack
- `test_critical_is456.py` - Critical IS 456 test cases
- `test_coverage_gaps.py` - Coverage edge cases
- `test_findings_regressions.py` - Bug fix regressions
- `test_report_golden.py` - Report format golden tests

**Run Command:**
```bash
pytest tests/regression/ -v
# Or with marker:
pytest -m regression -v
```

### 4. Property Tests (`property/`)

**Purpose:** Property-based tests checking mathematical invariants
**Scope:** Parametric tests with auto-generated inputs
**Speed:** Variable (100+ cases per test)
**File Count:** 1 file

**Files:**
- `test_property_invariants.py` - Mathematical invariant checks

**Run Command:**
```bash
pytest tests/property/ -v
# Or with marker:
pytest -m property -v
```

### 5. Performance Tests (`performance/`)

**Purpose:** Performance benchmarks and timing tests
**Scope:** Speed regression detection
**Speed:** Intentionally slow (multiple runs)
**File Count:** 0 files (TODO: Add pytest-benchmark suite)

**Future Files:**
- `test_benchmarks.py` - Core calculation benchmarks

**Run Command:**
```bash
pytest tests/performance/ -v --benchmark-only
# Or with marker:
pytest -m performance -v
```

## Pytest Markers

Markers allow selective test execution. Use `-m` flag to run specific categories:

```bash
# Run only unit tests
pytest -m unit

# Run unit + integration (exclude slow tests)
pytest -m "unit or integration"

# Run everything except slow tests
pytest -m "not slow"

# Run only regression tests
pytest -m regression

# Run only contract tests (API compatibility)
pytest -m contract
```

**Available Markers:**
- `contract` - API contract tests (prevent breaking changes)
- `unit` - Fast unit tests for core modules
- `integration` - Multi-module integration tests
- `regression` - Golden vector and parity tests
- `property` - Property-based invariant tests
- `performance` - Performance benchmark tests
- `slow` - Tests taking >1 second

## Running Tests

### Run All Tests
```bash
pytest
# Or with coverage:
pytest --cov=structural_lib --cov-report=term-missing
```

### Run by Category
```bash
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest tests/regression/     # Regression tests only
```

### Run by Marker
```bash
pytest -m unit              # Unit tests only
pytest -m "not slow"        # Everything except slow tests
pytest -m "unit or integration"  # Unit + integration
```

### Run Specific File
```bash
pytest tests/unit/test_flexure.py -v
pytest tests/integration/test_api_entrypoints_is456.py -v
```

### Run with Coverage
```bash
pytest --cov=structural_lib --cov-report=html
# Open htmlcov/index.html to view coverage report
```

### Run in Parallel (faster)
```bash
pytest -n auto  # Use all CPU cores
pytest -n 4     # Use 4 workers
```

## Test Statistics

- **Total Tests:** 2270+
- **Total Files:** 59
- **Coverage:** 86%
- **Average Speed:** ~30s for full suite
- **Breakdown:**
  - Unit: 12 files (~500 tests)
  - Integration: 38 files (~1400 tests)
  - Regression: 8 files (~300 tests)
  - Property: 1 file (~70 tests)
  - Performance: 0 files (TODO)

## CI/CD Integration

The following tests run in CI on every PR:

1. **Contract Tests** (`-m contract`) - Prevent API breaking changes
2. **Core Tests** (`tests/unit/`) - Fast smoke tests
3. **Full Suite** (all tests) - On `main` branch pushes

**GitHub Actions Workflow:** `.github/workflows/fast-checks.yml`

## Test Data and Fixtures

- **`data/`** - Golden vector data files (JSON, CSV)
- **`fixtures/`** - Pytest fixtures and test utilities
- **`conftest.py`** - Shared fixtures across all tests

## Adding New Tests

### 1. Choose the Right Category

Ask yourself:
- **Unit?** → Tests a single module in isolation, no external dependencies
- **Integration?** → Tests multiple modules or external integrations (API, CLI, exports)
- **Regression?** → Validates known-good reference results
- **Property?** → Tests mathematical invariants with parametric inputs
- **Performance?** → Measures execution time and speed regressions

### 2. Place File in Appropriate Directory

```bash
# Unit test example
touch tests/unit/test_new_module.py

# Integration test example
touch tests/integration/test_new_api.py
```

### 3. Add Pytest Markers

```python
import pytest

@pytest.mark.unit
def test_calculation():
    """Fast unit test."""
    assert calculate(5) == 10

@pytest.mark.integration
@pytest.mark.slow
def test_full_workflow():
    """Slow integration test."""
    result = run_full_pipeline()
    assert result.success
```

### 4. Follow Naming Conventions

- **File names:** `test_<module>.py` or `test_<feature>.py`
- **Test functions:** `test_<what_it_tests>()`
- **Test classes:** `TestClassName` (PascalCase)
- **Test methods:** `test_method_name()` (snake_case)

## Troubleshooting

### Tests Not Found After Restructuring

If pytest can't find tests after moving files:
```bash
# Clear pytest cache
rm -rf .pytest_cache

# Verify pytest can discover tests
pytest --collect-only
```

### Import Errors

If you see `ModuleNotFoundError` after restructuring:
- Ensure `__init__.py` exists in all test directories (not required in pytest but helps)
- Check `sys.path` includes project root
- Run from project root: `python -m pytest tests/`

### Slow Tests

If full suite is too slow:
```bash
# Run only fast tests
pytest -m "not slow"

# Run in parallel
pytest -n auto

# Profile slow tests
pytest --durations=10
```

## References

- **Research Document:** `docs/research/test-organization-audit.md` (TASK-170)
- **Testing Strategy:** `docs/TESTING_STRATEGY.md`
- **Pytest Docs:** https://docs.pytest.org/
- **Coverage Docs:** https://pytest-cov.readthedocs.io/

## Maintenance

**Last Updated:** 2024-12-XX (TASK-191)
**Maintainer:** AI Agent / Project Team
**Review Frequency:** Quarterly or when test count changes >10%
