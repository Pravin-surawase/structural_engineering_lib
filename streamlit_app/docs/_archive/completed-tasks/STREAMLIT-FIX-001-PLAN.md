# STREAMLIT-FIX-001: Test Fixes Plan
**Phase:** Day 1-2 of 12
**Priority:** 🔴 CRITICAL
**Agent:** STREAMLIT UI SPECIALIST (Agent 6)

## Problem Analysis

### Root Cause
Tests were written without verifying actual function signatures, resulting in 44 of 52 tests failing.

### Test File Issues

#### 1. test_visualizations.py (Multiple signature mismatches)

**create_beam_diagram() Issues:**
- **Wrong:** Tests use `ast_mm2`, `asc_mm2` parameters
- **Actual signature:** `(b_mm, D_mm, d_mm, rebar_positions, xu, bar_dia, cover, show_dimensions)`
- **Affected tests:**
  - `test_basic_beam_diagram()`
  - `test_beam_diagram_without_compression_steel()`
  - `test_beam_diagram_extreme_dimensions()`
  - `test_beam_diagram_invalid_inputs()`
  - `test_beam_diagram_with_neutral_axis()`

**create_cost_comparison() Issues:**
- **Wrong:** Tests use `total_cost`, `concrete_cost`, `steel_cost`, `label` keys
- **Actual signature:** Expects `cost_per_meter`, `bar_arrangement`, `is_optimal`, `area_provided`
- **Wrong:** Tests use `show_breakdown` parameter (doesn't exist)
- **Affected tests:**
  - `test_basic_cost_comparison()`
  - `test_cost_comparison_with_breakdown()`
  - `test_cost_comparison_empty_data()`
  - `test_cost_comparison_single_option()`

**create_utilization_gauge() Issues:**
- **Wrong:** Tests use positional `utilization` and `title` parameters
- **Actual signature:** `(value, label, thresholds)`
- **Affected tests:**
  - `test_basic_gauge()`
  - `test_gauge_with_title()`
  - All other gauge tests

**create_sensitivity_tornado() Issues:**
- **Wrong:** Tests use `{"parameter": str, "impact_percent": float}` structure
- **Actual signature:** Expects `parameters` list with `name`, `low_value`, `high_value` + `baseline_value` argument
- **Missing:** `baseline_value` required argument
- **Affected tests:**
  - `test_basic_tornado_chart()`
  - `test_tornado_chart_sorting()`
  - `test_tornado_chart_empty_data()`
  - `test_tornado_chart_single_parameter()`

#### 2. test_api_wrapper.py (Functions return placeholders, not actual data)
- All tests pass with placeholder data
- No actual integration with structural_lib yet
- Tests are valid but superficial

## Fix Strategy

### Phase 1: Fix create_beam_diagram() tests (5 tests)
1. Replace `ast_mm2`/`asc_mm2` with proper `rebar_positions` list
2. Add `xu` (neutral axis depth) parameter
3. Add `bar_dia` parameter
4. Generate realistic rebar positions based on area

### Phase 2: Fix create_cost_comparison() tests (4 tests)
1. Replace `total_cost` → `cost_per_meter`
2. Replace `label` → `bar_arrangement`
3. Add `area_provided` key
4. Remove `show_breakdown` parameter
5. Remove breakdown cost keys

### Phase 3: Fix create_utilization_gauge() tests (6 tests)
1. Change `utilization=` → `value=`
2. Change `title=` → `label=`
3. Ensure value is 0-1 float

### Phase 4: Fix create_sensitivity_tornado() tests (4 tests)
1. Add required `baseline_value` parameter
2. Restructure data: `parameter` → `name`
3. Add `low_value`, `high_value` keys
4. Calculate realistic impact values

### Phase 5: Document and verify
1. Run full test suite
2. Verify all 52 tests pass
3. Document changes

## Expected Outcome
- ✅ 52/52 tests passing
- ✅ All function signatures match actual implementations
- ✅ Test coverage maintained at 80%+
- ✅ No changes to production code (only tests fixed)

## Test Execution Plan
```bash
# Run tests incrementally after each phase
python3 -m pytest streamlit_app/tests/test_visualizations.py::TestBeamDiagram -v
python3 -m pytest streamlit_app/tests/test_visualizations.py::TestCostComparison -v
python3 -m pytest streamlit_app/tests/test_visualizations.py::TestUtilizationGauge -v
python3 -m pytest streamlit_app/tests/test_visualizations.py::TestSensitivityTornado -v
python3 -m pytest streamlit_app/tests/ -v  # Full suite
```

## Files to Modify
1. `streamlit_app/tests/test_visualizations.py` - Fix 19 tests
2. (test_api_wrapper.py and test_inputs.py already passing)

## Estimated Time
- Phase 1-4: 1.5 hours
- Phase 5: 0.5 hours
- **Total:** 2 hours

---

**Status:** 📝 PLANNING COMPLETE - Ready to implement
**Next Step:** Begin Phase 1 - Fix create_beam_diagram() tests
