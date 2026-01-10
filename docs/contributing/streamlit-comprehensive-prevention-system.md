# Comprehensive Streamlit App Prevention System
**Version:** 0.16.0
**Date:** 2026-01-09
**Status:** 🎯 PROPOSED

> **Context:** Built prevention system for cost_optimizer.py (PR #301), but discovered
> NameError in beam_design.py that wasn't caught. Need app-wide solution.

---

## 🐛 Problem Statement

### Current Situation
✅ **What We Have:**
- Prevention system for `streamlit_app/pages/02_💰_cost_optimizer.py`
- Detects: ZeroDivisionError, KeyError, direct dict access
- CI integration + pre-commit hooks
- 34 passing validation tests

❌ **What We Don't Have:**
- Coverage for other 4 Streamlit pages:
  - `01_🏗️_beam_design.py` ← **HAS ERROR**
  - `03_✅_compliance.py`
  - `04_📊_batch_processor.py`
  - `05_📚_learning_center.py`
- NameError detection (undefined variables)
- AttributeError detection (missing session state keys)
- Scope analysis
- Runtime error boundaries for all pages

### Discovered Bug
**Location:** `streamlit_app/pages/01_🏗️_beam_design.py:659`
```python
"actual_value": ast_req,  # NameError: name 'ast_req' is not defined
```

**Impact:** App crashes when viewing Compliance tab
**Root Cause:** Variable used without definition
**Why Missed:** Prevention system doesn't scan this page

---

## 🎯 Proposed Solution Architecture

### Design Principles
1. **Comprehensive:** Cover ALL Streamlit pages, not just one
2. **Multi-Layered:** Static analysis + runtime protection + testing
3. **Proactive:** Catch errors BEFORE deployment (CI/pre-commit)
4. **Maintainable:** Central configuration, reusable components
5. **Performance:** Minimal runtime overhead

### Three-Layer Defense System

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: STATIC ANALYSIS (Pre-Commit + CI)             │
│ - Scan all 5 Streamlit pages                           │
│ - Detect: NameError, AttributeError, KeyError, etc.    │
│ - AST-based + pylint integration                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Layer 2: RUNTIME PROTECTION (Error Boundaries)         │
│ - Global error boundary decorator                      │
│ - Session state validators                             │
│ - Input sanitization                                   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Layer 3: MONITORING & TESTING (Validation)             │
│ - Integration tests for all pages                      │
│ - Error simulation tests                               │
│ - Regression detection                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Plan

### Phase 1: Extend Static Analyzer (HIGH PRIORITY)

#### 1.1 Create Multi-Page Scanner
**File:** `scripts/check_streamlit_issues.py`

**Features:**
- Scan ALL pages in `streamlit_app/pages/*.py`
- Detect error types:
  - ✅ NameError (undefined variables)
  - ✅ AttributeError (session state access)
  - ✅ KeyError (dict access without validation)
  - ✅ ZeroDivisionError (division operations)
  - ✅ TypeError (function calls with wrong args)
  - ✅ ImportError (missing imports)

**Technical Approach:**
```python
# Pseudo-code structure
class StreamlitIssueDetector:
    def __init__(self, pages_dir):
        self.pages = glob(f"{pages_dir}/*.py")
        self.issues = []

    def detect_undefined_variables(self, node):
        """NEW: Detect NameError - track scope and usage"""
        # Build symbol table (defined variables)
        # Check all Name nodes against symbol table
        # Report undefined references

    def detect_session_state_issues(self, node):
        """NEW: Detect AttributeError on st.session_state"""
        # Track session_state keys that are set
        # Check all access against known keys
        # Report missing key access

    def detect_unsafe_dict_access(self, node):
        """EXISTING: Already implemented in cost optimizer"""

    def scan_all_pages(self):
        """Scan all pages and aggregate issues"""
        for page in self.pages:
            page_issues = self.scan_page(page)
            self.issues.extend(page_issues)
```

**Severity Levels:**
- CRITICAL: Definite crash (NameError, AttributeError)
- HIGH: Likely crash (KeyError on critical path)
- MEDIUM: Potential crash (unchecked edge cases)
- LOW: Code smell (unused variables, etc.)

#### 1.2 Integrate pylint for Undefined Variables
**Why:** AST analysis alone can miss complex scope issues

```bash
# Add to CI workflow
pylint streamlit_app/pages/*.py \
  --disable=all \
  --enable=undefined-variable,used-before-assignment,no-member
```

### Phase 2: Global Error Boundary System

#### 2.1 Create Page-Level Error Boundary
**File:** `streamlit_app/utils/error_boundaries.py`

```python
import functools
import streamlit as st
from typing import Callable, Any

def streamlit_page_boundary(page_name: str):
    """
    Global error boundary for Streamlit pages.
    Catches ALL unhandled exceptions and shows user-friendly error.

    Usage:
        @streamlit_page_boundary("Beam Design")
        def main():
            # Page code
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except NameError as e:
                st.error(f"🐛 **Variable Error in {page_name}**")
                st.error(f"A required variable is undefined: {str(e)}")
                st.info("This is a bug. Please report to developers.")
                with st.expander("🔍 Technical Details"):
                    st.exception(e)
                return None
            except AttributeError as e:
                if "session_state" in str(e):
                    st.error(f"⚠️ **Session State Error in {page_name}**")
                    st.error("Required session data is missing. Try refreshing the page.")
                else:
                    st.error(f"🐛 **Attribute Error in {page_name}**: {str(e)}")
                with st.expander("🔍 Technical Details"):
                    st.exception(e)
                return None
            except KeyError as e:
                st.error(f"⚠️ **Data Access Error in {page_name}**")
                st.error(f"Required key '{str(e)}' not found")
                st.info("This might be due to missing inputs. Check your configuration.")
                return None
            except Exception as e:
                st.error(f"❌ **Unexpected Error in {page_name}**")
                st.error(f"An unexpected error occurred: {type(e).__name__}")
                with st.expander("🔍 Technical Details"):
                    st.exception(e)
                return None
        return wrapper
    return decorator
```

**Apply to All Pages:**
```python
# In each page file (beam_design.py, cost_optimizer.py, etc.)
from utils.error_boundaries import streamlit_page_boundary

@streamlit_page_boundary("Beam Design")
def main():
    # All page code goes here
    ...

if __name__ == "__main__":
    main()
```

#### 2.2 Session State Validator
**File:** `streamlit_app/utils/session_state_validator.py`

```python
from typing import List, Dict, Any
import streamlit as st

class SessionStateValidator:
    """Validates session state has required keys before access"""

    @staticmethod
    def require_keys(keys: List[str], context: str = "page"):
        """
        Ensure required session state keys exist.

        Args:
            keys: List of required key names
            context: Where this is used (for error message)

        Returns:
            bool: True if all keys exist

        Raises:
            AttributeError: If any key missing (caught by error boundary)
        """
        missing = [k for k in keys if k not in st.session_state]
        if missing:
            st.error(f"⚠️ Missing session data for {context}: {', '.join(missing)}")
            st.info("Please go to previous steps and provide required inputs.")
            return False
        return True

    @staticmethod
    def get_safe(key: str, default: Any = None) -> Any:
        """Safe session state access with default"""
        return st.session_state.get(key, default)
```

### Phase 3: CI/Pre-Commit Integration

#### 3.1 Update CI Workflow
**File:** `.github/workflows/streamlit-validation.yml`

```yaml
name: Streamlit App Validation

on:
  push:
    paths:
      - 'streamlit_app/**'
  pull_request:
    paths:
      - 'streamlit_app/**'

jobs:
  validate-all-pages:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run multi-page issue detector
        run: |
          python scripts/check_streamlit_issues.py --all-pages

      - name: Run pylint on all pages
        run: |
          pylint streamlit_app/pages/*.py \
            --disable=all \
            --enable=undefined-variable,used-before-assignment,no-member \
            --exit-zero > pylint_report.txt
          cat pylint_report.txt

      - name: Fail on CRITICAL issues
        run: |
          python scripts/check_streamlit_issues.py --all-pages --fail-on critical
```

#### 3.2 Update Pre-Commit Hook
**File:** `.pre-commit-config.yaml`

```yaml
- repo: local
  hooks:
    - id: check-streamlit-issues
      name: Check Streamlit App Issues (All Pages)
      entry: python scripts/check_streamlit_issues.py --all-pages --fail-on critical,high
      language: python
      files: ^streamlit_app/pages/.*\.py$
      pass_filenames: false

    - id: pylint-streamlit
      name: Pylint Undefined Variables (Streamlit)
      entry: pylint
      language: python
      types: [python]
      files: ^streamlit_app/pages/.*\.py$
      args:
        - --disable=all
        - --enable=undefined-variable,used-before-assignment,no-member
        - --score=no
```

### Phase 4: Testing & Validation

#### 4.1 Integration Tests for All Pages
**File:** `Python/tests/test_streamlit_pages_integration.py`

```python
"""Integration tests for all Streamlit pages"""
import pytest
from streamlit.testing.v1 import AppTest

@pytest.mark.parametrize("page_file", [
    "pages/01_🏗️_beam_design.py",
    "pages/02_💰_cost_optimizer.py",
    "pages/03_✅_compliance.py",
    "pages/04_📊_batch_processor.py",
    "pages/05_📚_learning_center.py",
])
def test_page_loads_without_error(page_file):
    """Test that page loads without crashing"""
    at = AppTest.from_file(f"streamlit_app/{page_file}")
    at.run()
    assert not at.exception  # No exceptions

def test_beam_design_compliance_tab():
    """Test the specific tab where ast_req error occurred"""
    at = AppTest.from_file("streamlit_app/pages/01_🏗️_beam_design.py")
    at.run()

    # Simulate clicking Analyze button
    at.button[0].click()

    # Check compliance tab loads
    # (This would have caught the ast_req error!)
    assert not at.exception
```

#### 4.2 Error Simulation Tests
Test that error boundaries work:

```python
def test_error_boundary_catches_nameerror():
    """Test that undefined variable is caught gracefully"""
    # Inject undefined variable into page
    # Verify error boundary shows user-friendly message
    # Verify app doesn't crash
```

---

## 📊 Comparison: Current vs Proposed

| Feature | Current System | Proposed System |
|---------|----------------|-----------------|
| **Pages Covered** | 1 (cost optimizer) | 5 (all pages) |
| **Error Types Detected** | 3 (ZeroDivision, KeyError, unsafe dict) | 8 (+ NameError, AttributeError, TypeError, ImportError, ScopeError) |
| **Static Analysis** | AST only | AST + pylint |
| **Runtime Protection** | Cost optimizer only | All pages |
| **Session State Validation** | ❌ No | ✅ Yes |
| **Undefined Variable Detection** | ❌ No | ✅ Yes |
| **CI Integration** | ✅ Yes (1 page) | ✅ Yes (all pages) |
| **Pre-Commit** | ✅ Yes (1 page) | ✅ Yes (all pages) |
| **Error Boundaries** | ✅ Yes (1 page) | ✅ Yes (all pages) |
| **Integration Tests** | ❌ No | ✅ Yes |

---

## 🚀 Implementation Timeline

### Week 1: Core Foundation (HIGH PRIORITY)
- [ ] **Day 1-2:** Fix immediate beam_design.py bug (ast_req)
- [ ] **Day 3-4:** Extend static analyzer to all pages
- [ ] **Day 5:** Add NameError detection to analyzer
- [ ] **Day 6-7:** Test multi-page analyzer

### Week 2: Runtime Protection
- [ ] **Day 1-2:** Create global error boundary system
- [ ] **Day 3:** Apply boundaries to all 5 pages
- [ ] **Day 4:** Create session state validator
- [ ] **Day 5:** Integration testing
- [ ] **Day 6-7:** Bug fixes and refinement

### Week 3: CI/Testing Integration
- [ ] **Day 1-2:** Update CI workflows
- [ ] **Day 3:** Update pre-commit hooks
- [ ] **Day 4-5:** Write integration tests
- [ ] **Day 6:** Write error simulation tests
- [ ] **Day 7:** Documentation and handoff

---

## 🎯 Success Metrics

### Coverage Metrics
- ✅ 100% of Streamlit pages scanned (5/5)
- ✅ 100% of pages have error boundaries (5/5)
- ✅ 90%+ test coverage for page loading
- ✅ 80%+ detection rate for common errors

### Quality Metrics
- ✅ Zero NameError in production
- ✅ Zero AttributeError (session state) in production
- ✅ CI catches issues before merge
- ✅ Pre-commit catches issues before commit

### Performance Metrics
- Static analysis: <10 seconds for all pages
- Runtime overhead: <50ms per page load
- CI workflow: <5 minutes total

---

## 🔧 Maintenance Plan

### Weekly
- Review new issues detected by scanner
- Triage and prioritize fixes
- Update issue patterns if new types emerge

### Monthly
- Analyze false positive rate
- Refine detection rules
- Update documentation

### Quarterly
- Review effectiveness metrics
- Add new error types if discovered
- Optimize performance

---

## 📚 Documentation Requirements

### For Developers
1. **STREAMLIT_ERROR_PREVENTION_GUIDE.md** - How to use the system
2. **ADDING_NEW_PAGES.md** - Checklist for new pages
3. **DEBUGGING_STREAMLIT_ERRORS.md** - How to debug when issues occur

### For Users
1. Update **troubleshooting.md** with common Streamlit errors
2. Add FAQ section for "Page crashed" scenarios

---

## 🎓 Lessons Learned

### What Worked
✅ AST-based static analysis catches many issues
✅ Error boundaries provide good user experience
✅ CI integration prevents bugs from merging
✅ Pre-commit hooks catch issues early

### What Didn't Work
❌ Single-page focus too narrow
❌ AST alone misses scope issues
❌ No runtime monitoring for other pages

### Future Improvements
- Consider runtime error logging/telemetry
- Add fuzzing tests for edge cases
- Integrate with Sentry or similar for production monitoring

---

## 🔗 Related Documents
- [Cost Optimizer Prevention System](../../scripts/check_cost_optimizer_issues.py) - Original system
- [Error Boundary Implementation](../../streamlit_app/utils/cost_optimizer_error_boundary.py) - Current boundaries
- [TASKS.md](../TASKS.md#STREAMLIT-IMPL) - Implementation tasks

---

**Status:** 🎯 PROPOSED - Awaiting approval to implement
**Next Steps:** Review with user, get approval, start Phase 1
