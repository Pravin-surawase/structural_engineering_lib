# FIX-002: Test Suite Mock Enhancement

**Task ID:** FIX-002
**Priority:** 🔴 CRITICAL
**Estimated Time:** 2-3 hours
**Goal:** Reduce test failures from 127 to <10

---

## Current Status

```
Total Tests: 939
Passed: 801 (85.3%)
Failed: 127 (13.5%)
Skipped: 11 (1.2%)
```

## Root Cause Analysis

### Issue Categories

1. **Missing Streamlit Runtime Mocks** (90+ failures)
   - `st.session_state` access patterns not fully mocked
   - `st.markdown()`, `st.empty()` context managers incomplete
   - Missing `st.spinner()`, `st.status()` context managers

2. **Incomplete Component Mocks** (20+ failures)
   - `st.container()` not returning proper context manager
   - `st.tabs()` not mocked
   - `st.plotly_chart()` not mocked

3. **Test-Specific Issues** (10-15 failures)
   - Tests expecting real Streamlit behavior
   - Assertions checking actual HTML output
   - Integration tests needing Streamlit app context

---

## Implementation Plan

### Phase 1: Core Mock Enhancement (45 min)

**File:** `streamlit_app/tests/conftest.py`

#### Add Missing Methods:
```python
@staticmethod
def spinner(text):
    """Mock st.spinner() context manager"""

@staticmethod
def status(label, expanded=False, state="running"):
    """Mock st.status() context manager"""

@staticmethod
def tabs(labels):
    """Mock st.tabs() - returns list of tab contexts"""

@staticmethod
def plotly_chart(fig, use_container_width=True, **kwargs):
    """Mock st.plotly_chart()"""

@staticmethod
def container():
    """Mock st.container() context manager"""
```

#### Enhance Session State:
```python
class MockSessionState(dict):
    """Enhanced with get() method and default handling"""

    def get(self, key, default=None):
        return super().get(key, default)
```

### Phase 2: Component-Specific Mocks (30 min)

**Target Files:**
- `tests/test_accessibility.py` - 5 failures
- `tests/test_loading_states.py` - 14 failures
- `tests/test_polish.py` - 1 failure

#### Accessibility Mocks:
```python
# Add ARIA attribute tracking
MockStreamlit.aria_labels = {}
MockStreamlit.focus_target = None

@staticmethod
def set_aria_label(element_id, label):
    MockStreamlit.aria_labels[element_id] = label
```

#### Loading State Mocks:
```python
# Add shimmer effect tracking
MockStreamlit.shimmer_active = False

@staticmethod
def spinner(text):
    MockStreamlit.shimmer_active = True
    class SpinnerContext:
        def __enter__(self): return self
        def __exit__(self, *args):
            MockStreamlit.shimmer_active = False
    return SpinnerContext()
```

### Phase 3: Results & Visualization Mocks (30 min)

**Target Files:**
- `tests/test_results.py` - 8 failures
- `tests/test_results_components.py` - 3 failures
- `tests/test_visualizations.py` - 4 failures

#### Add Chart Tracking:
```python
MockStreamlit.charts_rendered = []

@staticmethod
def plotly_chart(fig, **kwargs):
    MockStreamlit.charts_rendered.append({
        'figure': fig,
        'kwargs': kwargs
    })
```

### Phase 4: Integration Test Separation (15 min)

**Create new marker:**
```python
# pytest.ini or conftest.py
@pytest.mark.streamlit_app
def test_requires_real_streamlit():
    """Tests that need actual Streamlit runtime"""
```

**Add CLI option to skip:**
```bash
pytest -m "not streamlit_app"  # Skip integration tests
```

---

## Test-by-Test Fix Strategy

### High-Priority Failures

#### 1. `test_accessibility.py` (5 failures)
- **Fix:** Add `aria-label` tracking to MockStreamlit
- **Time:** 10 min

#### 2. `test_loading_states.py` (14 failures)
- **Fix:** Mock `st.spinner()`, `st.status()` context managers
- **Time:** 15 min

#### 3. `test_results.py` (8 failures)
- **Fix:** Enhance dict handling in mock responses
- **Time:** 10 min

#### 4. `test_results_components.py` (3 failures)
- **Fix:** Mock `st.metric()` with delta tracking
- **Time:** 5 min

#### 5. `test_visualizations.py` (4 failures)
- **Fix:** Mock `st.plotly_chart()` properly
- **Time:** 10 min

### Remaining Failures (95 tests)
- **Strategy:** Run pytest with `-x` flag to fix one at a time
- **Time:** 45-60 min

---

## Verification Steps

1. **After Each Phase:**
   ```bash
   pytest --tb=short -v
   ```

2. **Track Progress:**
   ```bash
   pytest --tb=no -q | grep "failed"
   ```

3. **Final Verification:**
   ```bash
   pytest --cov=streamlit_app --cov-report=term-missing
   ```

---

## Success Criteria

- ✅ **Failures < 10** (target: 0-5 failures)
- ✅ **Pass Rate > 95%** (current: 85.3%)
- ✅ **All critical paths tested** (beam design, results display, error handling)
- ✅ **No Streamlit runtime warnings**

---

## Rollback Plan

If mock changes break existing tests:

1. **Git stash changes:**
   ```bash
   git stash save "FIX-002 WIP - reverting"
   ```

2. **Identify breaking change:**
   ```bash
   git diff stash@{0} tests/conftest.py
   ```

3. **Apply selective fixes:**
   ```bash
   git stash pop
   # Fix specific issue
   git add tests/conftest.py
   git commit -m "fix(tests): address mock compatibility"
   ```

---

## Notes

- **DO NOT** modify production code to pass tests
- **DO** enhance mocks to match Streamlit API
- **SEPARATE** unit tests (pure functions) from integration tests (Streamlit runtime)
- **DOCUMENT** any test-specific workarounds

---

**Next Action:** Start Phase 1 - Core Mock Enhancement
