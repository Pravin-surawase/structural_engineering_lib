# TASK-210/211 Implementation Status & Plan

**Date**: 2026-01-07
**Agent**: Background (worktree-2026-01-07T07-28-08)
**Status**: Infrastructure complete, minimal refactoring needed

---

## ✅ Infrastructure Complete (TASK-212, 213, 214)

1. **Exception Hierarchy** (TASK-212) - 19 tests ✅
   - `StructuralLibError` base
   - 5 Level-1 categories
   - 3 Level-2 specific exceptions

2. **Error Message Templates** (TASK-213) - 29 tests ✅
   - Three Questions Framework
   - 15+ template functions

3. **Result Base Classes** (TASK-214) - 14 tests ✅
   - `BaseResult`, `CalculationResult`, `ComplianceResult`

---

## 📊 API Analysis (api.py)

**Total Public Functions**: 19
**Already Using Result Objects**: 16 ✅
**Need Refactoring**: 3 ❌

### Functions Already Compliant:
- ✅ `design_beam_is456` → `ComplianceCaseResult`
- ✅ `check_beam_is456` → `ComplianceReport`
- ✅ `detail_beam_is456` → `BeamDetailingResult`
- ✅ `check_beam_ductility` → `DuctileBeamResult`
- ✅ `check_deflection_span_depth` → `DeflectionResult`
- ✅ `check_crack_width` → `CrackWidthResult`
- ✅ `compute_detailing` → `list[BeamDetailingResult]`
- ✅ `compute_bbs` → `BBSDocument`
- ✅ 11 more functions with proper types

### Functions Needing Refactoring:
1. ❌ `optimize_beam_cost` → `dict[str, Any]`
2. ❌ `suggest_beam_design_improvements` → `dict[str, Any]`
3. ❌ `smart_analyze_design` → `Union[dict[str, Any], str]`

---

## 🎯 TASK-210: Revised Scope

**Original Estimate**: 2-3 days (12 functions)
**Actual Scope**: 3 functions need refactoring
**Revised Estimate**: 4-6 hours

### Phase 1: Create Result Dataclasses
Create 3 new result classes inheriting from `BaseResult`:

1. **`CostOptimizationResult`** (for `optimize_beam_cost`)
   ```python
   @dataclass(frozen=True)
   class CostOptimizationResult(BaseResult):
       optimal_design: OptimalDesign
       baseline_cost: float
       savings_amount: float
       savings_percent: float
       alternatives: list[AlternativeDesign]
       metadata: dict[str, Any]

       def summary(self) -> str: ...
   ```

2. **`DesignSuggestionsResult`** (for `suggest_beam_design_improvements`)
   ```python
   @dataclass(frozen=True)
   class DesignSuggestionsResult(BaseResult):
       suggestions: list[Suggestion]
       priority_order: list[str]
       estimated_savings: Optional[float]

       def summary(self) -> str: ...
   ```

3. **`DesignAnalysisResult`** (for `smart_analyze_design`)
   ```python
   @dataclass(frozen=True)
   class DesignAnalysisResult(BaseResult):
       analysis_type: str
       findings: list[Finding]
       recommendations: list[str]
       severity: str

       def summary(self) -> str: ...
   ```

### Phase 2: Refactor Functions
Update 3 functions to return result objects instead of dicts.

### Phase 3: Update Tests
- Update existing tests for new return types
- Add tests for result object methods

### Phase 4: Add Deprecation (Optional)
- Keep old dict returns for one version
- Add `@deprecated` decorator with migration guide

---

## 🎯 TASK-211: Core Modules

**Original Estimate**: 2-3 days
**Actual Scope**: Apply exception hierarchy + error templates
**Revised Estimate**: 6-8 hours

### Target Modules:
1. `flexure.py` - Replace generic exceptions with hierarchy
2. `shear.py` - Use error message templates
3. `detailing.py` - Add proper exception handling

### Changes Needed:
- Replace `ValueError`, `RuntimeError` with proper exceptions
- Use error message templates for consistency
- Add context (`details`, `suggestion`, `clause_ref`)

---

## 📅 Revised Timeline

### Today (2026-01-07):
- ✅ Infrastructure complete (62 tests)
- ⏳ TASK-210 Phase 1-2: 4 hours
- ⏳ TASK-211: 6 hours
- **Total**: ~10 hours remaining

### Approach:
1. Create 3 result dataclasses (1 hour)
2. Refactor 3 API functions (2 hours)
3. Update/add tests (1 hour)
4. Apply to core modules (6 hours)

**Total Estimated**: 10 hours
**Can complete in 1-2 sessions**

---

## 🚀 Next Steps

1. Create result dataclasses in `data_types.py`
2. Refactor `optimize_beam_cost` first (has most complex dict structure)
3. Refactor `suggest_beam_design_improvements`
4. Refactor `smart_analyze_design`
5. Run tests, commit
6. Move to TASK-211 (core modules)

---

**Note**: The API is in much better shape than the roadmap suggested. Most work was already done in previous refactorings. We only need to finish the last 3 functions and apply patterns to core modules.
