# Cost Optimizer Prevention System - Usage Guide
**Version:** 0.16.5
**Date:** 2026-01-09
**Status:** ✅ Production Ready

---

## Overview

This prevention system ensures cost optimizer code quality through:
1. **Automated Issue Detection** - Pre-commit hooks catch problems before commit
2. **Validation Helpers** - Type-safe input/output validation
3. **Error Boundaries** - Safe error handling prevents crashes
4. **CI Static Analysis** - Continuous quality checks
5. **Comprehensive Tests** - 34 tests ensure validator reliability

---

## Quick Start

### 1. Enable Pre-Commit Hooks

```bash
# One-time setup
pip install pre-commit
pre-commit install

# Test it works
pre-commit run --all-files
```

The cost optimizer check will now run automatically on every commit!

### 2. Use Validators in Code

```python
from streamlit_app.utils.cost_optimizer_validators import (
    validate_beam_inputs,
    validate_design_result,
    safe_divide,
    safe_format_currency,
    ValidationResult
)

# Validate inputs before processing
def process_beam(inputs: dict):
    result = validate_beam_inputs(inputs)

    if not result:  # ValidationResult is falsy when invalid
        for error in result.errors:
            st.error(f"❌ {error}")
        return None

    # Inputs guaranteed valid here!
    mu_knm = inputs["mu_knm"]  # Safe - validated
    ...

# Safe division with zero check
ratio = safe_divide(alt_area, selected_area, default=0.0)

# Safe formatting
st.metric("Cost", safe_format_currency(total_cost))
st.metric("Savings", safe_format_percent(savings_pct))
```

### 3. Use Error Boundaries

```python
from streamlit_app.utils.cost_optimizer_error_boundary import (
    error_boundary,
    monitor_performance,
    require_session_state,
    SafeSessionState
)

# Protect functions from crashes
@error_boundary(fallback_value={"analysis": None, "comparison": []})
@monitor_performance(threshold_seconds=2.0)
def run_cost_optimization(inputs: dict) -> dict:
    # If this crashes, returns fallback_value
    # If it takes >2s, logs a warning
    ...

# Validate session state
@require_session_state("beam_inputs", "design_results")
def use_cached_results():
    # Guaranteed these keys exist
    return st.session_state.design_results

# Type-safe session state access
safe_state = SafeSessionState()
inputs = safe_state.get_dict("beam_inputs", default={})
results = safe_state.get_list("cost_comparison_data", default=[])
```

---

## Components

### 1. Automated Issue Detection Script

**Location:** `scripts/check_cost_optimizer_issues.py`

**What it checks:**
- ✅ Direct dict access (use `.get()` instead)
- ✅ Division without zero checks
- ✅ Imports inside functions
- ✅ Missing type hints on dict returns
- ✅ Session state access without validation

**Run manually:**
```bash
python scripts/check_cost_optimizer_issues.py
```

**Output example:**
```
🔴 CRITICAL ISSUES:
  Line 309: Division operation without obvious zero check (validate denominator)

🟠 HIGH PRIORITY ISSUES:
  Line 222: Direct dict access 'design_result[...]' may raise KeyError (use .get() with default)
  Line 215: Import from 'structural_lib.costing' inside function 'run_cost_optimization'

📊 Total issues found: 40
   Critical: 4, High: 25, Medium: 11
```

### 2. Validation Helpers

**Location:** `streamlit_app/utils/cost_optimizer_validators.py`

#### `validate_beam_inputs(inputs: dict) -> ValidationResult`

Validates beam design parameters with comprehensive checks:
- Required keys present
- Type correctness (numeric, not NaN/Inf)
- Range validation (mu_knm > 0, b_mm 100-1000, etc.)
- Cross-validation (d < D, cover 20-100mm)
- Span/depth ratio (5-30)
- Material grades (fck 20-100, fy 250-600)

**Returns:** `ValidationResult` with `is_valid` flag and `errors` list

#### `validate_design_result(result: Any) -> ValidationResult`

Validates design result structure:
- Has `design.flexure` keys
- `tension_steel` has `num`, `dia`, `area`
- `_bar_alternatives` is non-empty list
- Each alternative has required keys

#### `safe_divide(numerator, denominator, default=0.0) -> float`

Division with zero/NaN/Inf checks. Returns `default` if invalid.

#### `safe_format_currency(value) -> str`

Format currency handling NaN/Inf/None. Returns "Invalid" or "N/A" for bad values.

#### `safe_format_percent(value) -> str`

Format percentage handling NaN/Inf/None. Returns "Invalid" or "N/A" for bad values.

### 3. Error Boundary Decorators

**Location:** `streamlit_app/utils/cost_optimizer_error_boundary.py`

#### `@error_boundary(fallback_value=None, show_error=True, log_error=True)`

Catches exceptions and provides safe fallback. Handles:
- `ZeroDivisionError`
- `KeyError`
- `ValueError`
- `TypeError`
- Generic `Exception`

Shows user-friendly error messages, logs details for debugging.

#### `@monitor_performance(threshold_seconds=1.0)`

Logs warning if function takes longer than threshold. Useful for detecting slow operations.

#### `@require_session_state(*keys)`

Validates session state keys exist before running function. Raises `KeyError` with helpful message if missing.

#### `SafeSessionState` Class

Type-safe wrapper for session state:
- `get_dict(key, default)` - Returns dict or default
- `get_list(key, default)` - Returns list or default
- `get_int(key, default)` - Returns int with type coercion
- `get_float(key, default)` - Returns float with type coercion
- `set(key, value)` - Set value
- `exists(key)` - Check if key exists
- `clear(key)` - Remove key

### 4. CI Workflow

**Location:** `.github/workflows/cost-optimizer-analysis.yml`

Runs automatically on pushes to `main` or `task/FIX-*` branches when cost optimizer files change.

**Checks:**
1. **Automated issue detection** - Runs `check_cost_optimizer_issues.py`
2. **Type checking** - `mypy` for type safety
3. **Security scan** - `bandit` for security vulnerabilities
4. **Complexity** - `radon` for cyclomatic complexity
5. **Code quality** - `pylint` for code smells

**Note:** All checks are informational and don't block PRs (yet). See output for issues to fix.

### 5. Tests

**Location:** `streamlit_app/tests/test_cost_optimizer_validators.py`

**Coverage:** 34 tests, 100% of validator functions

**Categories:**
- Beam input validation (7 tests)
- Design result validation (5 tests)
- Safe division (6 tests)
- Currency formatting (7 tests)
- Percentage formatting (6 tests)
- ValidationResult class (3 tests)

**Run tests:**
```bash
.venv/bin/python -m pytest streamlit_app/tests/test_cost_optimizer_validators.py -v
```

---

## Usage Patterns

### Pattern 1: Validate User Input

```python
def manual_input_form():
    with st.form("manual_input"):
        mu_knm = st.number_input("Moment (kN·m)", value=120.0)
        # ... other inputs ...

        submitted = st.form_submit_button("Analyze")

        if submitted:
            inputs = {
                "mu_knm": mu_knm,
                # ... all inputs ...
            }

            # Validate before processing
            result = validate_beam_inputs(inputs)
            if not result:
                for error in result.errors:
                    st.error(f"❌ {error}")
                return None  # Don't proceed

            # Safe to process
            return process_beam(inputs)
```

### Pattern 2: Validate Cached Results

```python
def get_design_results():
    """Get design results with validation."""
    safe_state = SafeSessionState()

    # Check key exists
    if not safe_state.exists("design_results"):
        st.warning("No design results available")
        return None

    # Get with type safety
    results = safe_state.get_dict("design_results")

    # Validate structure
    validation = validate_design_result(results)
    if not validation:
        st.error("Design results are invalid:")
        for error in validation.errors:
            st.error(f"  • {error}")
        return None

    return results
```

### Pattern 3: Safe Calculations

```python
def calculate_costs(alternatives, selected_area):
    """Calculate costs with zero division protection."""
    comparison = []

    # Validate denominator upfront
    if selected_area <= 0:
        st.error("Invalid baseline design: steel area is zero")
        return []

    for alt in alternatives:
        alt_area = alt.get("area", 0)

        # Safe division
        utilization = safe_divide(alt_area, selected_area, default=1.0)

        # Safe formatting
        comparison.append({
            "area": safe_format_currency(alt_area),
            "utilization": safe_format_percent(utilization),
        })

    return comparison
```

### Pattern 4: Complete Function Protection

```python
@error_boundary(
    fallback_value={"analysis": None, "comparison": []},
    show_error=True,
    log_error=True
)
@monitor_performance(threshold_seconds=3.0)
def run_cost_optimization(inputs: dict) -> dict:
    """
    Run cost optimization with complete protection.

    - Validates inputs
    - Catches all errors
    - Logs performance
    - Returns safe fallback on failure
    """
    # Validate inputs
    result = validate_beam_inputs(inputs)
    if not result:
        raise ValueError(f"Invalid inputs: {result.errors}")

    # ... rest of implementation ...

    return {"analysis": analysis_data, "comparison": comparison_data}
```

---

## Troubleshooting

### Issue: Pre-commit hook fails on cost optimizer changes

**Symptom:** `check-cost-optimizer-issues` hook shows errors on commit

**Solution:**
1. Review the output - it lists all issues found
2. Fix the issues or add them to backlog
3. If urgent, skip hook temporarily: `git commit --no-verify` (not recommended!)

### Issue: Tests fail after changes

**Symptom:** `test_cost_optimizer_validators.py` tests fail

**Solution:**
1. Check which test failed - name indicates the issue
2. Update validators if intentional API change
3. Update tests if validator behavior changed correctly

### Issue: CI workflow fails

**Symptom:** Cost Optimizer Static Analysis workflow shows failures

**Solution:**
1. Check workflow logs on GitHub Actions
2. Most common: mypy type errors, bandit security warnings
3. Fix locally and push again

### Issue: ValidationResult doesn't work as expected

**Symptom:** Validation passes but shouldn't (or vice versa)

**Solution:**
1. Check `result.errors` list - shows specific issues
2. Ensure using `if not result:` not `if result is False:`
3. ValidationResult implements `__bool__` - use it directly

---

## Maintenance

### Adding New Validators

1. Add function to `cost_optimizer_validators.py`
2. Add tests to `test_cost_optimizer_validators.py`
3. Run tests: `.venv/bin/python -m pytest streamlit_app/tests/test_cost_optimizer_validators.py`
4. Update this documentation

### Adding New Error Patterns

1. Update `check_cost_optimizer_issues.py`:
   - Add to `IssueDetector` class (AST-based)
   - Or add to regex-based checks in `check_file()`
2. Test: `python scripts/check_cost_optimizer_issues.py`
3. Commit changes - will automatically run in pre-commit

### Updating CI Checks

1. Edit `.github/workflows/cost-optimizer-analysis.yml`
2. Add new analysis tools or change thresholds
3. Test locally first
4. Push and verify on GitHub Actions

---

## Metrics

### Current Stats (as of 2026-01-09)

- **Issues detected by script:** 40 (4 Critical, 25 High, 11 Medium)
- **Validators created:** 5 main functions + 1 class
- **Tests written:** 34 (100% passing)
- **Error boundary decorators:** 4
- **CI checks:** 5 (issue detection, mypy, bandit, radon, pylint)

### Goals

- **Short term:** Fix all CRITICAL issues (4)
- **Medium term:** Fix all HIGH issues (25)
- **Long term:** Reduce issues to zero, maintain with prevention system

---

## Best Practices

### DO:
✅ Use validators before processing user input
✅ Use `@error_boundary` on all public functions
✅ Use `SafeSessionState` for session state access
✅ Use `safe_divide()` for any division
✅ Use `safe_format_*()` for displaying numbers
✅ Run `check_cost_optimizer_issues.py` before committing
✅ Write tests for new validators

### DON'T:
❌ Use direct dict access (`result["key"]`) - use `.get()`
❌ Divide without checking for zero
❌ Import modules inside functions
❌ Return dict without type hints
❌ Access session state without validation
❌ Show raw exceptions to users
❌ Skip pre-commit hooks (`--no-verify`)

---

## Next Steps

### Phase 1: Fix Existing Issues (Week 1)
1. Fix 4 CRITICAL issues (zero division, key errors)
2. Apply validators to main functions
3. Add error boundaries

### Phase 2: Complete Integration (Week 2)
1. Fix 25 HIGH issues
2. Use SafeSessionState throughout
3. Add comprehensive logging

### Phase 3: Enhancement (Week 3)
1. Fix MEDIUM issues
2. Add more validators
3. Improve CI checks

### Phase 4: Maintenance (Ongoing)
1. Monitor CI for new issues
2. Add tests for edge cases
3. Update documentation

---

## Support

**Issues with prevention system:**
- Check this documentation first
- Review `COST_OPTIMIZER_FIX_PLAN.md` for fix examples
- Check `COST_OPTIMIZER_COMPLETE_AUDIT.md` for all 227 issues

**Contributing:**
- Add tests for new validators
- Update documentation
- Follow existing patterns
- Run all checks before PR

---

**Remember:** This prevention system is your safety net. Use it!
