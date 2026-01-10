# Insights Module Implementation Plan

**Created:** 2025-12-31
**Status:** In Progress
**Target:** v0.13 completion

---

## Current State Assessment

### ✅ What Exists (v0.13 Foundation)

**Module Structure:**
- `structural_lib/insights/` directory created
- `__init__.py`, `types.py`, `precheck.py`, `sensitivity.py`, `constructability.py`
- Basic test coverage (`test_insights_*.py`)

**Features Implemented:**
1. **Precheck** (heuristic validation) - 90% complete
2. **Sensitivity** (parameter perturbation) - 60% complete (needs fixes)
3. **Constructability** (BDAS-based scoring) - 70% complete

### ❌ What Needs Work

**Critical Issues Found:**

1. **Sensitivity Analysis (TASK-133):**
   - ❌ **BUG:** Sensitivity not normalized correctly
     - Current: `sensitivity = delta_util / perturbation`
     - Should be: `sensitivity = (delta_util / base_util) / perturbation`
     - Impact: Cannot compare parameters with different units/scales
   - ❌ Missing comprehensive tests (golden vectors from IS 456)
   - ❌ No validation against known beam theory (depth > width for flexure)
   - ❌ Robustness calculation is heuristic-based, not margin-based
   - ❌ No multi-objective sensitivity (flexure + deflection)

2. **Constructability Scoring (TASK-134):**
   - ⚠️ Score range 0-10 (blog spec uses 0-100 for finer granularity)
   - ⚠️ Missing some factors from blog (standard bar sizes, depth increments)
   - ❌ Limited tests

3. **General:**
   - ❌ No JSON schema for insights output (TASK-136)
   - ❌ No CLI integration
   - ❌ No verification pack (5-10 benchmarks against IS 456)

---

## Implementation Tasks

### TASK-133: Sensitivity Analysis Refinement (HIGH PRIORITY)

**Estimated:** 1 day

**Subtasks:**

1. **Fix normalization bug** (30 min)
   - Change formula from `delta_util / perturbation` to `(delta_util / base_util) / perturbation`
   - Update tests to verify normalized coefficients
   - Ensure dimensionless comparison

2. **Improve robustness calculation** (1 hour)
   - Change from heuristic-based to margin-based
   - Calculate allowable parameter variations before failure
   - Implement proper scoring: `min_variation / 0.20` capped at 1.0

3. **Add comprehensive tests** (3 hours)
   - Golden vector validation (IS 456 worked examples)
   - Physical validation (depth > width for flexure)
   - Edge cases (zero utilization, >1.0 utilization, parameter = 0)
   - Multi-objective sensitivity (flexure + deflection)
   - Determinism check (same inputs → same outputs)

4. **Add validation suite** (2 hours)
   - Test against 3-4 IS 456 Annexure examples
   - Verify error < 0.1 percentage point
   - Document expected sensitivities for reference beams

5. **Documentation** (1 hour)
   - Docstring improvements (explain normalized coefficient)
   - Usage examples in module docstring
   - Add type hints for better IDE support

**Files to modify:**
- `structural_lib/insights/sensitivity.py` (fix formula, improve robustness)
- `tests/test_insights_sensitivity.py` (add comprehensive tests)
- Add: `tests/data/sensitivity_golden_vectors.json` (reference data)

**Acceptance Criteria:**
- ✅ Normalized sensitivity coefficient (dimensionless)
- ✅ Margin-based robustness scoring
- ✅ 10+ test cases covering edge cases
- ✅ Validation against IS 456 examples (error <0.1%)
- ✅ Physical validation tests (depth > width)

---

### TASK-134: Constructability Scoring Refinement (MEDIUM PRIORITY)

**Estimated:** 1 day

**Subtasks:**

1. **Align with blog specification** (2 hours)
   - Change score range from 0-10 to 0-100 (finer granularity)
   - Add missing factors:
     - Standard bar size check (8, 10, 12, 16, 20, 25, 32mm)
     - Standard depth increments (50mm multiples)
     - Bar configuration simplicity (2-3 bars bonus)
   - Update penalties/bonuses to match blog values

2. **Improve factor breakdown** (1 hour)
   - Clear penalty/bonus attribution
   - Specific recommendations per factor
   - Impact statements (labor productivity, cost, quality)

3. **Add comprehensive tests** (2 hours)
   - Light reinforcement beam (expected score: 85-100)
   - Typical reinforcement (expected score: 70-85)
   - Heavy reinforcement (expected score: 55-70)
   - Congested design (expected score: <55)
   - Edge cases (non-standard sizes, too many bars)

4. **Documentation** (1 hour)
   - Explain BDAS framework basis
   - Cite Poh & Chen (1998) in docstring
   - Usage examples

**Files to modify:**
- `structural_lib/insights/constructability.py` (align with blog spec)
- `structural_lib/insights/types.py` (update ConstructabilityScore if needed)
- `tests/test_insights_constructability.py` (add comprehensive tests)

**Acceptance Criteria:**
- ✅ Score range 0-100 (aligned with blog)
- ✅ All factors from blog implemented
- ✅ 8+ test cases covering design spectrum
- ✅ Clear penalty/bonus breakdown in results

---

### TASK-136: JSON Schema + CLI Integration (MEDIUM PRIORITY)

**Estimated:** 1 day

**Subtasks:**

1. **Define JSON schemas** (2 hours)
   - Schema for PredictiveCheckResult
   - Schema for SensitivityResult + RobustnessScore
   - Schema for ConstructabilityScore
   - Validate against real outputs

2. **Add JSON export** (1 hour)
   - `.to_dict()` method for all insights dataclasses
   - Ensure JSON serializable (no numpy types, etc.)

3. **CLI integration** (3 hours)
   - Add `--insights` flag to `beam_pipeline.py`
   - Output insights to separate JSON file (e.g., `case_insights.json`)
   - Safe output handling (don't crash if insights fail)
   - Log warnings if insights unavailable

4. **Tests** (1 hour)
   - Test JSON round-trip (export + schema validate)
   - Test CLI with `--insights` flag
   - Test CLI without insights (ensure backward compatibility)

**Files to modify:**
- `structural_lib/insights/types.py` (add `.to_dict()` methods)
- `structural_lib/beam_pipeline.py` (add `--insights` flag handling)
- Add: `structural_lib/insights/schema.py` (JSON schema definitions)
- `tests/test_beam_pipeline_cli.py` (test CLI with insights)

**Acceptance Criteria:**
- ✅ Valid JSON schemas for all insights types
- ✅ `.to_dict()` export for all dataclasses
- ✅ CLI `--insights` flag outputs separate JSON file
- ✅ Backward compatibility (CLI works without `--insights`)

---

### TASK-135: Verification Pack (HIGH PRIORITY, DEFERRED)

**Estimated:** 2-3 days (post-implementation)

**Purpose:** Comprehensive validation against IS 456 worked examples

**Subtasks:**
1. Create 5-10 reference beams from IS 456 Annexure + SP:16
2. Document expected sensitivities for each
3. Automate verification (pytest fixtures)
4. Add to CI/CD (regression prevention)

**Defer until:** TASK-133 and TASK-134 complete

---

## Implementation Order

### Phase 1: Fix Critical Issues (Days 1-2)
1. **Day 1 AM:** TASK-133 subtasks 1-2 (fix normalization, improve robustness)
2. **Day 1 PM:** TASK-133 subtask 3 (comprehensive tests)
3. **Day 2 AM:** TASK-133 subtasks 4-5 (validation suite, docs)
4. **Day 2 PM:** TASK-134 subtasks 1-2 (align spec, improve factors)

### Phase 2: Polish & Integration (Day 3)
5. **Day 3 AM:** TASK-134 subtasks 3-4 (tests, docs)
6. **Day 3 PM:** TASK-136 subtasks 1-2 (JSON schema, export)

### Phase 3: CLI & Final Verification (Day 4)
7. **Day 4 AM:** TASK-136 subtasks 3-4 (CLI integration, tests)
8. **Day 4 PM:** Integration testing, final validation
9. **Day 5+:** TASK-135 (verification pack) - stretch goal

---

## Success Metrics

**Code Quality:**
- ✅ All functions have type hints
- ✅ All public APIs have docstrings with examples
- ✅ Test coverage >90% for insights module
- ✅ No regressions in existing tests

**Correctness:**
- ✅ Sensitivity normalization matches blog specification
- ✅ Physical validation tests pass (depth > width for flexure)
- ✅ Validation against IS 456 examples (error <0.1%)
- ✅ Robustness scoring aligns with margin-based calculation

**Usability:**
- ✅ CLI `--insights` flag works end-to-end
- ✅ JSON output is valid and well-structured
- ✅ Clear error messages if insights unavailable
- ✅ Documentation includes usage examples

---

## Risk Mitigation

**Risk 1: Breaking changes to insights API**
- Mitigation: Insights are opt-in (separate module), core API unaffected
- Version: Mark insights as "preview" in v0.13, stable in v0.14

**Risk 2: Performance impact of sensitivity analysis**
- Mitigation: Sensitivity requires N+1 design evaluations (acceptable for <10 params)
- Document: Recommend limiting `parameters_to_vary` to critical params

**Risk 3: Validation failures**
- Mitigation: Start with simple test cases, gradually add complexity
- Fallback: Mark failing tests as `@pytest.mark.xfail` with issue links

---

## Next Steps (Immediate)

1. ✅ Review existing code (DONE)
2. 🔄 Fix sensitivity normalization bug (IN PROGRESS)
3. ⏳ Add comprehensive tests
4. ⏳ Improve robustness calculation
5. ⏳ Align constructability with blog spec

**Current Focus:** TASK-133 subtask 1 (fix normalization bug)

---

**Last Updated:** 2025-12-31
**Owner:** AI + Pravin
**Tracking:** TASKS.md lines 570-590
