# Streamlit UI Testing Strategy
**Version:** 1.0.0
**Date:** 2026-01-08
**Status:** ACTIVE

---

## Overview

This document defines the testing strategy for the Streamlit UI to prevent trial-and-error development and catch bugs before deployment.

---

## Testing Pyramid

```
         ┌─────────────────────┐
         │   E2E (Manual)      │  ← 10%: User acceptance, visual checks
         ├─────────────────────┤
         │  Integration Tests  │  ← 30%: Component interactions
         ├─────────────────────┤
         │    Unit Tests       │  ← 60%: Pure functions, calculations
         └─────────────────────┘
```

---

## Test Categories

### 1. Null Safety Tests (CRITICAL)

**Purpose:** Prevent `TypeError: '>' not supported between NoneType and int`

**What to test:**
- All visualization functions with `None` inputs
- All functions with empty lists `[]`
- All functions with zero values
- All optional parameters

**Example:**
```python
def test_beam_diagram_with_none_xu(self):
    """CRITICAL: create_beam_diagram must handle xu=None."""
    fig = create_beam_diagram(
        b_mm=300.0, D_mm=500.0, d_mm=450.0,
        rebar_positions=[],  # Empty
        xu=None,             # None before analysis
        bar_dia=0, cover=30.0
    )
    assert fig is not None
```

**File:** `tests/test_beam_design_integration.py` → `TestVisualizationNullSafety`

---

### 2. Dynamic Result Tests (CRITICAL)

**Purpose:** Ensure different inputs produce different outputs

**What to test:**
- Changing moment → different Ast
- Changing shear → different spacing
- Changing dimensions → different results
- Changing materials → different limits

**Example:**
```python
def test_different_moments_give_different_ast(self):
    result1 = cached_design(mu_knm=100.0, ...)
    result2 = cached_design(mu_knm=200.0, ...)  # Different moment
    assert result2['flexure']['ast_required'] > result1['flexure']['ast_required']
```

**File:** `tests/test_beam_design_integration.py` → `TestAPIWrapperDynamicResults`

---

### 3. Calculation Correctness Tests

**Purpose:** Verify IS 456 formulas are implemented correctly

**What to test:**
- Mu_limit = 0.138 × fck × b × d² (balanced section)
- Ast_min = 0.85 × b × d / fy (minimum steel)
- tau_v = Vu / (b × d) (shear stress)

**Example:**
```python
def test_moment_limit_formula(self):
    expected = 0.138 * fck * b * (d ** 2) / 1e6
    assert abs(result['mu_limit_knm'] - expected) < 1.0
```

**File:** `tests/test_beam_design_integration.py` → `TestDesignCalculationCorrectness`

---

### 4. Contract Tests

**Purpose:** Ensure components return expected data structures

**What to test:**
- Material selectors return `{grade, fck/fy, cost_factor, description}`
- Exposure selector returns `{exposure, cover, max_crack_width}`
- All required keys are present

**File:** `tests/test_beam_design_integration.py` → `TestInputComponentContracts`

---

### 5. Edge Case Tests

**Purpose:** Handle extreme/boundary values

**What to test:**
- Zero moment → minimum steel
- Extreme aspect ratios (very deep/narrow beams)
- High concrete grades (M40+)
- All exposure conditions

**File:** `tests/test_beam_design_integration.py` → `TestEdgeCasesAndErrorHandling`

---

## Running Tests

### Quick Check (Before Commits)
```bash
cd streamlit_app
../.venv/bin/python -m pytest tests/test_beam_design_integration.py -v
```

### Full Suite
```bash
cd streamlit_app
../.venv/bin/python -m pytest tests/ -v --tb=short
```

### Specific Test Class
```bash
../.venv/bin/python -m pytest tests/test_beam_design_integration.py::TestVisualizationNullSafety -v
```

---

## Pre-Commit Checklist

Before making any UI change:

1. **Run integration tests:**
   ```bash
   pytest tests/test_beam_design_integration.py -v
   ```

2. **Check for None handling:**
   - Does your code handle `None` inputs?
   - Does your code handle empty lists?
   - Does your code handle zero values?

3. **Verify dynamic behavior:**
   - Do different inputs produce different outputs?
   - Is caching working correctly?

4. **Start app locally:**
   ```bash
   streamlit run app.py
   ```

5. **Manual checks:**
   - Change inputs → results change?
   - Empty state renders correctly?
   - No console errors?

---

## Adding New Tests

### When to add tests:

1. **After fixing a bug:** Add test that would have caught it
2. **Before adding feature:** Write test first (TDD)
3. **After code review finds issue:** Add regression test

### Test template:
```python
def test_feature_name_scenario(self):
    """
    Purpose: What this tests
    Bug/Feature: Link to issue or description
    """
    # Arrange
    input_data = {...}

    # Act
    result = function_under_test(**input_data)

    # Assert
    assert expected_condition
```

---

## Common Bugs to Test For

| Bug Type | Test Strategy |
|----------|---------------|
| `NoneType` errors | Pass `None` to all optional params |
| Empty list errors | Pass `[]` to all list params |
| Division by zero | Pass `0` to divisor params |
| Cache issues | Test with same inputs twice |
| State issues | Test initial state separately |
| Type errors | Test with edge type values |

---

## CI Integration

These tests run automatically in CI:

```yaml
# .github/workflows/streamlit-tests.yml
- name: Run Streamlit Integration Tests
  run: |
    cd streamlit_app
    python -m pytest tests/test_beam_design_integration.py -v --tb=short
```

---

## Test Coverage Goals

| Category | Target | Current |
|----------|--------|---------|
| Null safety | 100% | ✅ 100% |
| Dynamic results | 100% | ✅ 100% |
| Calculation correctness | 80% | ✅ 100% |
| Edge cases | 80% | ✅ 80% |
| UI components | 60% | 🟡 40% |

---

## Maintenance

1. **Run tests before every commit**
2. **Add test for every bug fix**
3. **Review tests monthly for coverage gaps**
4. **Update this doc when adding new test categories**

---

*Document Version: 1.0.0 | Author: Main Agent | Last Updated: 2026-01-08*
