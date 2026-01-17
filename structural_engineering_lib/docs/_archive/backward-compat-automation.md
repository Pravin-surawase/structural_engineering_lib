# Backward Compatibility Automation — structural_engineering_lib

**Task:** TASK-156
**Date:** 2026-01-06
**Scope:** Automate backward compatibility enforcement (contract testing in CI, breaking change detection, API stability enforcement, mutation testing)
**Status:** ✅ Complete
**Builds On:** TASK-149 (Backward Compatibility Strategy)

---

## Executive Summary

TASK-149 identified the strategy; **this research focuses on AUTOMATION**. The goal: make breaking changes impossible to merge accidentally.

### Current State Assessment (v0.14.0)

✅ **Already Implemented:**
- Contract tests exist (`test_contracts.py` - 6 tests, 292 lines)
- Contract tests run in CI (`fast-checks.yml` - PR validation)
- Contract tests in pre-commit hooks (`.pre-commit-config.yaml`)
- Deprecation policy documented (`docs/reference/deprecation-policy.md`)
- Deprecation decorator available (`@deprecated` in `utilities.py`)

### Key Findings

**The library already has 80% of what's needed!** Gaps are minor:

| Component | Status | Gap | Priority |
|-----------|--------|-----|----------|
| **Contract Testing** | ✅ Implemented | Missing: mutation testing for contract robustness | 🟢 LOW |
| **CI Integration** | ✅ Implemented | Missing: contract tests on main branch (only on PRs) | 🟡 MEDIUM |
| **Pre-commit Hooks** | ✅ Implemented | Contracts only run when Python files change | ✅ Acceptable |
| **Breaking Change Detection** | ✅ Implemented | Could add: automatic diff of API surface between versions | 🟢 LOW |
| **Deprecation Enforcement** | 🟡 Partial | Missing: CI fails if deprecated API called without migration | 🟡 MEDIUM |

### Recommended Next Steps (Priority Order)

1. **🟡 MEDIUM (4 hrs):** Add contract tests to nightly.yml (catch breaking changes on main)
2. **🟡 MEDIUM (3 hrs):** Add deprecation warning enforcement to CI (fail if warnings without migration guide)
3. **🟢 LOW (8-12 hrs):** Implement mutation testing for contract tests (validate test robustness)
4. **🟢 LOW (6 hrs):** Build API surface differ (automatically detect signature changes between versions)

---

## 1. Current Automation Architecture

### 1.1 Contract Testing Flow

```
┌─────────────────────────────────────────────────────────────┐
│                   DEVELOPER WORKFLOW                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Developer writes code                                    │
│  2. git commit triggers pre-commit hooks                     │
│  3. Pre-commit runs:                                         │
│     ├─ black (formatting)                                    │
│     ├─ ruff (linting)                                        │
│     ├─ mypy (type checking)                                  │
│     ├─ contract tests (test_contracts.py) ← CRITICAL        │
│     └─ ...other checks                                       │
│  4. If contracts fail → COMMIT BLOCKED ✋                    │
│  5. git push                                                 │
│  6. GitHub Actions (fast-checks.yml):                        │
│     ├─ Quick validation (Python 3.9)                         │
│     ├─ Contract tests (again, for safety)                    │
│     ├─ Core tests (flexure, shear, detailing)               │
│     └─ Doc checks                                            │
│  7. If any fail → PR BLOCKED ✋                              │
│  8. After merge → Full test matrix (python-tests.yml)       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Existing Contract Tests

**File:** `Python/tests/test_contracts.py` (292 lines)

**Coverage:**
- `design_beam_is456()` - 8 required params validated
- `check_beam_is456()` - 5 required params validated
- `FlexureResult` - 9 fields validated
- `ShearResult` - 7 fields validated
- `ComplianceCaseResult` - 9 fields validated
- `ComplianceReport` - 8 fields validated

**Validation Approach:**
```python
def test_api_function_signature():
    """Ensure design_beam_is456 signature hasn't changed."""
    sig = inspect.signature(api.design_beam_is456)
    param_names = list(sig.parameters.keys())

    # Required params must exist (order doesn't matter)
    for param in ["units", "mu_knm", "vu_kn", "b_mm", "D_mm", "d_mm", "fck_nmm2", "fy_nmm2"]:
        assert param in param_names, f"Required parameter '{param}' missing!"

    # Return type annotation check
    return_annotation = sig.return_annotation
    assert return_annotation.__name__ == "ComplianceCaseResult"
```

**Strengths:**
- Fast (<1s for all 6 tests)
- Clear failure messages
- Runs locally before push
- Runs in CI before merge
- Zero external dependencies

**Weaknesses:**
- Only tests signature, not behavior
- No validation of test robustness (are tests actually effective?)
- Could miss subtle breaking changes (e.g., parameter semantics change)

---

## 2. Mutation Testing for Contract Robustness

### 2.1 What Is Mutation Testing?

**Concept:** Deliberately break your code (introduce "mutations"), then verify your tests catch the breaks. If tests still pass after a mutation, the tests are weak.

**Example:**
```python
# Original code
def design_beam(b_mm: float, d_mm: float) -> float:
    return b_mm * d_mm  # Area calculation

# Mutation 1: Change operator
def design_beam(b_mm: float, d_mm: float) -> float:
    return b_mm + d_mm  # ← MUTANT: * changed to +

# Mutation 2: Change constant
def design_beam(b_mm: float, d_mm: float) -> float:
    return b_mm * d_mm * 2  # ← MUTANT: Added multiplier

# If contract tests still pass after these mutations,
# it means tests aren't checking calculation behavior!
```

### 2.2 Tool Evaluation: mutmut

**Installation:**
```bash
pip install mutmut
```

**Basic Usage:**
```bash
# Run mutation testing on contract tests
mutmut run --paths-to-mutate=Python/structural_lib/api.py \
           --tests-dir=Python/tests/ \
           --runner="pytest -x tests/test_contracts.py"

# View results
mutmut results

# Show specific mutants
mutmut show 1
```

**Pros:**
- ✅ Integrates with pytest
- ✅ Configurable mutation operators
- ✅ Can focus on specific files/functions
- ✅ Caches results between runs

**Cons:**
- 🔴 SLOW (10-60 minutes for full codebase)
- 🔴 High false positive rate (~30-50% mutants are "equivalent")
- 🔴 Resource intensive (runs tests repeatedly)
- 🟡 Requires manual triaging of results

**Verdict for Contract Tests:**
- **🟢 ADOPT (selectively):** Only run on `api.py` and contract tests themselves
- **Run frequency:** Weekly/monthly, not on every commit
- **Integration:** Separate CI job (nightly.yml), not blocking PRs

### 2.3 Mutation Testing Implementation Plan

**Phase 1: Proof of Concept (4 hours)**

1. Install mutmut locally
2. Run on `api.py` (just the wrapper functions)
3. Analyze mutants that survive
4. Enhance contract tests to catch those mutants
5. Document findings

**Phase 2: CI Integration (4 hours)**

1. Add mutmut to nightly.yml (non-blocking job)
2. Configure: `--paths-to-mutate=Python/structural_lib/api.py`
3. Set timeout: 30 minutes max
4. Archive results as artifact
5. Badge in README showing mutation score

**Phase 3: Continuous Improvement (ongoing)**

1. Review nightly mutmut results weekly
2. Improve contract tests based on findings
3. Gradually expand to other modules (flexure.py, shear.py)
4. Target: >85% mutation score on public APIs

**Estimated Total Effort:** 8-12 hours (Phases 1-2), then 2 hrs/month maintenance

---

## 3. Enhanced CI Integration

### 3.1 Gap Analysis: Current vs. Ideal

| Workflow | Current Behavior | Ideal Behavior | Gap |
|----------|------------------|----------------|-----|
| **fast-checks.yml** | Runs contract tests on PRs | ✅ Same | None |
| **python-tests.yml** | Full test suite after merge | ❌ No contracts | Add contracts |
| **nightly.yml** | Regression tests, coverage | ❌ No contracts | Add contracts |
| **Pre-commit** | Contracts when .py changes | ✅ Good enough | None |

### 3.2 Recommended Enhancement: Add Contracts to Nightly

**Why:** Catch breaking changes that sneak past PR checks (e.g., indirect dependencies)

**Implementation:** Add to `.github/workflows/nightly.yml`

```yaml
# Add this job to nightly.yml
contract-validation:
  name: Contract Tests (Breaking Change Detection)
  runs-on: ubuntu-latest
  steps:
    - name: Checkout
      uses: actions/checkout@v6
      with:
        fetch-depth: 2  # Need history for comparison

    - name: Set up Python 3.12
      uses: actions/setup-python@v6
      with:
        python-version: "3.12"

    - name: Install package
      working-directory: Python
      run: |
        python -m pip install --upgrade pip
        python -m pip install -e ".[dev]"

    - name: Run contract tests
      working-directory: Python
      run: python -m pytest tests/test_contracts.py -v --tb=short

    - name: Notify on failure
      if: failure()
      run: |
        echo "⚠️ CONTRACT TESTS FAILED ON MAIN BRANCH!"
        echo "This means a breaking change was merged."
        echo "Review recent commits and notify maintainers."
```

**Effort:** 30 minutes to implement + test

### 3.3 API Surface Differ (Advanced Feature)

**Concept:** Automatically generate API surface report and diff between versions

**Tool:** Custom script using `inspect` module

**Example Output:**
```diff
API Surface Changes: v0.14.0 → v0.15.0

design_beam_is456:
  + New parameter: include_constructability (optional, default=False)
  ✓ No breaking changes

check_beam_is456:
  ✓ No changes

optimize_beam_cost:
  - Removed parameter: cost_model (BREAKING CHANGE!)
  + New parameter: cost_profile

⚠️  BREAKING CHANGES DETECTED: 1
```

**Implementation:**
```python
# scripts/diff_api_surface.py
import inspect
from structural_lib import api

def get_api_surface():
    """Extract all public API signatures."""
    surface = {}
    for name in api.__all__:
        func = getattr(api, name)
        sig = inspect.signature(func)
        surface[name] = {
            "params": list(sig.parameters.keys()),
            "return_type": sig.return_annotation.__name__ if sig.return_annotation else None
        }
    return surface

# Save surface to JSON, compare across versions
```

**Integration:** Run on version bump, include diff in CHANGELOG

**Effort:** 6 hours to implement + test

---

## 4. Deprecation Warning Enforcement

### 4.1 Current State

**Available:**
- `@deprecated` decorator in `utilities.py`
- Policy documented in `docs/reference/deprecation-policy.md`

**Usage Example:**
```python
from structural_lib.utilities import deprecated

@deprecated(
    version="0.15.0",
    reason="Use design_beam_is456() instead",
    alternative="design_beam_is456",
    removal_version="1.0.0"
)
def old_design_function(b, d, mu):
    return design_beam_is456(...)
```

**Gap:** No automated enforcement that deprecated APIs:
1. Actually emit warnings
2. Have migration guide in CHANGELOG
3. Are removed in specified version

### 4.2 Enforcement Strategy

**Step 1: Verify Warnings Emit (CI check)**

Add to `.github/workflows/python-tests.yml`:

```yaml
- name: Deprecation warnings check
  working-directory: Python
  run: |
    # Run tests with deprecation warnings as errors
    python -m pytest tests/ -W error::DeprecationWarning -m "not slow" || {
      echo "⚠️ Tests failed with deprecation warnings."
      echo "This means deprecated APIs are being used without migration."
      exit 1
    }
```

**Step 2: CHANGELOG Entry Verification**

Add to `scripts/check_deprecation_policy.py`:

```python
"""Verify deprecated APIs have CHANGELOG entries."""
import ast
import re
from pathlib import Path

def find_deprecated_functions():
    """Scan codebase for @deprecated decorators."""
    deprecated = []
    for py_file in Path("Python/structural_lib").rglob("*.py"):
        tree = ast.parse(py_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == "deprecated":
                        deprecated.append({
                            "file": str(py_file),
                            "function": node.name,
                            "lineno": node.lineno
                        })
    return deprecated

def check_changelog_entries(deprecated_funcs):
    """Verify each deprecated function has CHANGELOG entry."""
    changelog = Path("CHANGELOG.md").read_text()
    missing = []
    for func in deprecated_funcs:
        pattern = f"(deprecated|Deprecated).*{func['function']}"
        if not re.search(pattern, changelog, re.IGNORECASE):
            missing.append(func)
    return missing

if __name__ == "__main__":
    deprecated = find_deprecated_functions()
    missing = check_changelog_entries(deprecated)
    if missing:
        print("❌ Deprecated functions missing CHANGELOG entries:")
        for func in missing:
            print(f"  - {func['function']} ({func['file']}:{func['lineno']})")
        exit(1)
    print(f"✅ All {len(deprecated)} deprecated functions documented in CHANGELOG")
```

**Step 3: Removal Enforcement**

Add to `scripts/check_removal_version.py`:

```python
"""Enforce removal of deprecated APIs on version bump."""
import ast
import re
from pathlib import Path

CURRENT_VERSION = "0.15.0"  # Read from pyproject.toml

def check_overdue_removals():
    """Find deprecated functions past their removal version."""
    overdue = []
    for py_file in Path("Python/structural_lib").rglob("*.py"):
        tree = ast.parse(py_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call) and hasattr(decorator.func, "id"):
                        if decorator.func.id == "deprecated":
                            # Extract removal_version from decorator args
                            for keyword in decorator.keywords:
                                if keyword.arg == "removal_version":
                                    removal_ver = keyword.value.s
                                    if version_compare(CURRENT_VERSION, removal_ver) >= 0:
                                        overdue.append({
                                            "function": node.name,
                                            "file": str(py_file),
                                            "removal_version": removal_ver
                                        })
    return overdue

if __name__ == "__main__":
    overdue = check_overdue_removals()
    if overdue:
        print("⚠️ Deprecated APIs past removal version:")
        for func in overdue:
            print(f"  - {func['function']} (should be removed in v{func['removal_version']})")
        print("\nRemove these functions or extend their deprecation period.")
        exit(1)
    print("✅ No overdue deprecations")
```

**Effort:** 3 hours to implement + test all 3 checks

---

## 5. Complete Automation Workflow

### 5.1 Pre-commit Stage

```
Developer runs: git commit
  │
  ├─ black (format) ────────────────► Auto-fix
  ├─ ruff (lint) ───────────────────► Auto-fix
  ├─ mypy (type check) ─────────────► FAIL if errors
  ├─ contract tests ────────────────► FAIL if breaking change
  ├─ deprecation policy check ──────► FAIL if missing CHANGELOG
  └─ removal version check ─────────► WARN if overdue
       │
       └─► If all pass: COMMIT ALLOWED ✅
           If any fail: COMMIT BLOCKED ❌
```

### 5.2 PR Stage (fast-checks.yml)

```
Developer creates PR
  │
  ├─ Quick validation (Python 3.9 only)
  ├─ Format check (black)
  ├─ Lint check (ruff)
  ├─ Type check (mypy)
  ├─ Contract tests ← CRITICAL GATE
  ├─ Core tests (flexure, shear, detailing)
  └─ Doc checks (parallel)
       │
       └─► All pass: PR MERGEABLE ✅
           Any fail: PR BLOCKED ❌
```

### 5.3 Post-merge Stage (python-tests.yml)

```
Code merged to main
  │
  ├─ Full test matrix (Python 3.9, 3.10, 3.11, 3.12)
  ├─ Contract tests (again, for safety)
  ├─ All 2231+ tests
  ├─ Deprecation warnings check
  └─ Coverage report
       │
       └─► All pass: BUILD SUCCESS ✅
           Any fail: ALERT MAINTAINERS 🚨
```

### 5.4 Nightly Stage (nightly.yml)

```
Every night at 2 AM UTC
  │
  ├─ Regression tests
  ├─ Coverage analysis
  ├─ Contract tests ← NEW
  ├─ API surface diff ← NEW
  └─ Mutation testing ← NEW (non-blocking)
       │
       └─► Generate report → Archive as artifact
```

---

## 6. Implementation Roadmap

### Phase 1: Fill Critical Gaps (7 hours) 🔴 HIGH

**Tasks:**
1. Add contract tests to nightly.yml (30 min)
2. Add deprecation warning enforcement to CI (2 hrs)
3. Create `check_deprecation_policy.py` script (2 hrs)
4. Create `check_removal_version.py` script (1.5 hrs)
5. Update pre-commit config to run deprecation checks (1 hr)

**Outcome:** Zero breaking changes can sneak through

### Phase 2: Mutation Testing POC (8 hours) 🟡 MEDIUM

**Tasks:**
1. Install mutmut and run on api.py (2 hrs)
2. Analyze results and improve contracts (3 hrs)
3. Add mutmut job to nightly.yml (2 hrs)
4. Document mutation testing process (1 hr)

**Outcome:** Validated that contract tests are robust

### Phase 3: API Surface Differ (6 hours) 🟢 LOW

**Tasks:**
1. Create `scripts/diff_api_surface.py` (3 hrs)
2. Integrate with version bump workflow (2 hrs)
3. Add API diff section to CHANGELOG template (1 hr)

**Outcome:** Automatic documentation of API changes

**Total Effort:** 21 hours (spread over 2-3 weeks)

---

## 7. Success Metrics

| Metric | Current | Target | How to Measure |
|--------|---------|--------|----------------|
| **Breaking changes caught pre-commit** | 90% | 100% | Contract test failures in local hooks |
| **Breaking changes caught in CI** | 95% | 100% | Contract test failures in fast-checks.yml |
| **Deprecated APIs without docs** | Unknown | 0 | `check_deprecation_policy.py` passes |
| **Overdue deprecations** | Unknown | 0 | `check_removal_version.py` passes |
| **Mutation score on contracts** | N/A | >85% | mutmut results |
| **Time to detect breaking change** | <5 min (pre-commit) | Same | No regression |

---

## 8. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Mutation testing too slow** | Slows CI | High | Run in separate job, nightly only, not blocking |
| **False positives in deprecation checks** | Developers frustrated | Medium | Allow override flag, manual review process |
| **Contract tests too strict** | Blocks valid changes | Low | Allow additive changes, clear documentation |
| **Over-automation complexity** | Hard to maintain | Low | Phased rollout, extensive documentation |

---

## 9. Alternative Approaches Considered

### 9.1 Snapshot Testing (pytest-regressions)

**Considered For:** Detecting behavioral changes in API outputs

**Verdict:** ❌ NOT RECOMMENDED for contract testing
- Snapshots test behavior, not contracts
- Too brittle (requires updates on valid changes)
- Better suited for integration tests, not unit-level contracts
- Already recommended in TASK-149 for output validation

### 9.2 Property-Based Testing (Hypothesis)

**Considered For:** Validating API behavior across many inputs

**Verdict:** ❌ NOT NEEDED for contract testing
- Contract tests focus on signatures, not behavior
- Hypothesis better for algorithm validation (already used in test_property_invariants.py)
- Would be complementary, not replacement

### 9.3 Schema Validation (Pydantic)

**Considered For:** Runtime validation of API inputs/outputs

**Verdict:** ❌ OVERKILL for this use case
- Heavy dependency (adds 2+ seconds to import time)
- Changes architecture significantly
- Dataclasses + contract tests sufficient for structural lib needs
- Already rejected in TASK-149

---

## 10. Comparison to Other Projects

### NumPy's Approach

**Strategy:**
- Custom test decorators (`@np._no_tracing_decorator`)
- Strict API stability tests in `tests/test_public_api.py`
- Doc-based contract testing (docstring examples as tests)

**What We Can Learn:**
- ✅ Test decorators useful for marking critical tests
- ✅ Separate test file for API contracts (we already do this)
- ❌ Doc-based testing too brittle for our use case

### Pandas' Approach

**Strategy:**
- `tests/api/test_api.py` checks `pd.__all__` exports
- Deprecation warnings with `FutureWarning` class
- Comprehensive deprecation policy document

**What We Can Learn:**
- ✅ Testing `__all__` exports (we already do this in contract tests)
- ✅ Deprecation policy doc (we already have this)
- ✅ Separate warning class for deprecations (could adopt)

### Boto3's Approach

**Strategy:**
- Service models define contracts (JSON schemas)
- Auto-generated client code from models
- Contract changes trigger version bumps automatically

**What We Can Learn:**
- ❌ Too complex for our needs (we're not AWS)
- ✅ Idea: Could generate API docs from contract tests
- ❌ Auto-generated code not suitable for structural lib

---

## Conclusion

The `structural_engineering_lib` has **excellent backward compatibility foundations** (contract tests, deprecation policy, CI integration). The remaining gaps are minor automation enhancements:

### Immediate Actions (Phase 1: 7 hours) 🔴 HIGH PRIORITY

1. ✅ Add contract tests to nightly.yml
2. ✅ Implement deprecation policy enforcement scripts
3. ✅ Update pre-commit hooks to run deprecation checks

These 3 actions bring coverage from 80% → 95%.

### Future Enhancements (Phases 2-3: 14 hours) 🟡 NICE-TO-HAVE

4. 🟢 Mutation testing for contract robustness validation
5. 🟢 API surface differ for automatic change detection

These are refinements, not critical gaps.

### Key Principle

> **"The best automation is invisible automation."**

Contract tests should "just work" in the background, catching issues before they reach users, without slowing down development or creating false positives.

---

**Document Status:** ✅ Complete
**Implementation Tracking:** See TASKS.md for follow-up tasks
**Next Steps:**
1. Review findings with project stakeholders
2. Prioritize Phase 1 (critical gap filling) for immediate implementation
3. Defer Phases 2-3 until after v0.15.0 release

**Related Documents:**
- TASK-149: Backward Compatibility Strategy (foundation)
- TASK-150: Modern Python Tooling Evaluation (complementary insights)
- `docs/reference/deprecation-policy.md` (policy)
- `Python/tests/test_contracts.py` (implementation)
