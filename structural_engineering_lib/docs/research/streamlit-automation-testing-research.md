# Streamlit Automation Testing Research

**Type:** Research
**Audience:** All Agents
**Status:** Complete
**Importance:** High
**Created:** 2026-01-14
**Last Updated:** 2026-01-14
**Related Tasks:** TASK-600
**Archive Condition:** Archive when implemented and stable

---

## Executive Summary

This document researches automated testing solutions for Streamlit applications that can:
1. Open the app and run each page
2. Click buttons and interact with widgets
3. Verify outputs and catch runtime errors
4. Run in CI without a browser

**Recommendation:** Use Streamlit's official `st.testing.v1.AppTest` framework for headless testing, supplemented with Playwright for critical user journey tests.

---

## 1. Solutions Analyzed

### 1.1 Streamlit AppTest (RECOMMENDED - Primary Solution)

**Official Documentation:** https://docs.streamlit.io/develop/api-reference/app-testing

**What it is:**
- Official Streamlit headless testing framework (st.testing.v1.AppTest)
- Simulates Streamlit app execution without browser
- Runs in pytest, integrated with CI

**How it works:**
```python
from streamlit.testing.v1 import AppTest

def test_beam_design_page():
    """Test beam design page with valid inputs."""
    at = AppTest.from_file("streamlit_app/pages/01_🏗️_beam_design.py").run()

    # Check no exceptions
    assert not at.exception

    # Interact with widgets
    at.number_input[0].set_value(300).run()  # width
    at.number_input[1].set_value(500).run()  # depth

    # Click button
    at.button[0].click().run()

    # Verify outputs
    assert at.success  # Check for st.success messages
    assert not at.error  # No st.error messages
```

**Pros:**
- ✅ Official Streamlit solution
- ✅ Runs headlessly (no browser)
- ✅ Fast execution (~100ms per test)
- ✅ Full widget interaction
- ✅ Can check st.write, st.metric, st.success, st.error outputs
- ✅ Works in CI
- ✅ Python-native (pytest integration)

**Cons:**
- ❌ NOT compatible with `st.navigation` and `st.Page` (multipage apps)
- ❌ Each page must be tested individually
- ❌ No visual rendering (can't screenshot)
- ❌ Limited to Streamlit widgets (no custom JS components)

**Compatibility with our app:**
Our app uses `pages/` folder structure (NOT st.navigation), so AppTest IS compatible.

---

### 1.2 Playwright (Supplementary Solution)

**What it is:**
- Browser automation framework by Microsoft
- Controls real Chrome/Firefox/WebKit
- Full E2E testing capability

**How it works:**
```python
from playwright.sync_api import sync_playwright
import subprocess
import time

def test_full_workflow():
    # Start Streamlit app
    proc = subprocess.Popen(["streamlit", "run", "streamlit_app/app.py"])
    time.sleep(5)  # Wait for app to start

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto("http://localhost:8501")

            # Navigate to page
            page.click("text=Beam Design")

            # Fill inputs
            page.fill("input[aria-label='Width (mm)']", "300")
            page.fill("input[aria-label='Depth (mm)']", "500")

            # Click button
            page.click("button:text('Calculate')")

            # Wait for result
            page.wait_for_selector("text=Design Safe")

            browser.close()
    finally:
        proc.terminate()
```

**Pros:**
- ✅ Real browser testing
- ✅ Works with any Streamlit version
- ✅ Can screenshot and record video
- ✅ Full multipage navigation
- ✅ Works with custom components

**Cons:**
- ❌ Slower (~5-10s per test)
- ❌ Requires browser binary in CI
- ❌ Flaky network/timing issues
- ❌ More complex setup

---

### 1.3 Selenium (Legacy Option)

**What it is:** Traditional browser automation

**Verdict:** Not recommended. Playwright is faster and more reliable.

---

### 1.4 streamlit-test (Third-party)

**What it is:** Community package for testing

**Verdict:** Use official AppTest instead. streamlit-test is less maintained.

---

### 1.5 Locust/Gatling (Load Testing)

**What it is:** Load/stress testing frameworks

**Verdict:** Out of scope for functional testing. Use for performance benchmarks only.

---

## 2. Recommended Architecture

### 2.1 Three-Tier Testing Strategy

```
┌─────────────────────────────────────────────────────────┐
│ Tier 1: Unit Tests (pytest)                             │
│ - Test individual functions in utils/                   │
│ - Fast, comprehensive coverage                          │
│ - Already have: test_api_wrapper.py, etc.               │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ Tier 2: Component Tests (AppTest) ← NEW                 │
│ - Test each Streamlit page in isolation                 │
│ - Headless, fast (~100ms)                               │
│ - Verify widget interactions                            │
│ - Catch st.error, st.exception                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ Tier 3: E2E Tests (Playwright) ← OPTIONAL               │
│ - Full user journey tests                               │
│ - Real browser, screenshots                             │
│ - Slower, run weekly or pre-release                     │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Test File Structure

```
streamlit_app/tests/
├── conftest.py                    # Existing mocks
├── test_api_wrapper.py            # Existing unit tests
├── test_page_fixes_*.py           # Existing
│
├── apptest/                       # NEW: AppTest-based tests
│   ├── conftest.py               # AppTest fixtures
│   ├── test_page_01_beam_design.py
│   ├── test_page_02_analysis.py
│   ├── test_page_03_cost.py
│   ├── test_page_04_bbs.py
│   ├── test_page_05_learning.py
│   ├── test_page_06_settings.py
│   ├── test_page_07_report.py
│   └── test_all_pages_smoke.py   # Quick smoke test all pages
│
└── e2e/                           # OPTIONAL: Playwright tests
    ├── conftest.py               # Playwright fixtures
    ├── test_user_journey.py      # Critical path tests
    └── test_screenshots.py       # Visual regression
```

---

## 3. Implementation Plan

### Phase 1: AppTest Infrastructure (Priority)

**Time estimate:** 2-3 hours

1. Create `tests/apptest/` directory (NOT in streamlit_app/tests/ to avoid mock conflicts)
2. Create `conftest.py` with common fixtures:
   ```python
   import pytest
   from streamlit.testing.v1 import AppTest

   @pytest.fixture
   def beam_design_app():
       return AppTest.from_file("streamlit_app/pages/01_🏗️_beam_design.py")
   ```

3. Create smoke test for all pages:
   ```python
   @pytest.mark.parametrize("page", [
       "01_🏗️_beam_design.py",
       "02_📊_analysis.py",
       # ... all pages
   ])
   def test_page_loads_without_exception(page):
       at = AppTest.from_file(f"streamlit_app/pages/{page}").run()
       assert not at.exception, f"Page {page} raised: {at.exception}"
   ```

### Phase 2: Critical Path Tests

**Time estimate:** 3-4 hours

1. Beam Design happy path:
   - Set inputs → Click Calculate → Verify success

2. Report Generator:
   - Check design exists → Fill project info → Generate PDF

3. Cost Optimizer:
   - Load design → Compare options → Export

### Phase 3: CI Integration

**Time estimate:** 1 hour

1. Add to `.github/workflows/tests.yml`:
   ```yaml
   - name: Run Streamlit AppTests
     run: |
       cd Python
       pytest tests/apptest/ -v
   ```

2. Add to pre-commit (optional, may be slow):
   ```yaml
   - id: streamlit-smoke
     name: Streamlit Smoke Test
     entry: pytest tests/apptest/test_all_pages_smoke.py -v
     language: system
     pass_filenames: false
   ```

### Phase 4: Playwright E2E (Optional, Future)

**Time estimate:** 4-6 hours (if needed)

Only implement if AppTest coverage is insufficient for critical paths.

---

## 4. Known Limitations

### 4.1 AppTest Limitations

| Limitation | Workaround |
|------------|------------|
| No st.navigation support | Use pages/ folder (we already do) |
| No custom JS components | Test component logic separately |
| No visual regression | Use Playwright for screenshots |
| No multipage flow | Test each page individually |
| Session state isolation | Each test starts fresh |

### 4.2 Our App-Specific Considerations

1. **reportlab dependency:** PDF tests need reportlab installed
2. **Library import:** AppTest runs real code, so structural_lib must be available
3. **Cache behavior:** st.cache_data/st.cache_resource work normally in AppTest

---

## 5. Example Test Implementations

### 5.1 Smoke Test (All Pages Load)

```python
# tests/apptest/test_all_pages_smoke.py
import pytest
from streamlit.testing.v1 import AppTest
from pathlib import Path

PAGES_DIR = Path(__file__).parent.parent.parent / "pages"

def get_all_pages():
    """Get all page files."""
    return sorted(PAGES_DIR.glob("*.py"))

@pytest.mark.parametrize("page_path", get_all_pages(), ids=lambda p: p.name)
def test_page_loads_without_exception(page_path):
    """Each page should load without raising an exception."""
    at = AppTest.from_file(str(page_path)).run()

    assert not at.exception, f"Page {page_path.name} raised: {at.exception}"
```

### 5.2 Beam Design Happy Path

```python
# tests/apptest/test_page_01_beam_design.py
from streamlit.testing.v1 import AppTest

def test_beam_design_calculation_success():
    """Test successful beam design calculation."""
    at = AppTest.from_file("streamlit_app/pages/01_🏗️_beam_design.py").run()

    # Verify page loaded
    assert not at.exception

    # Set inputs via number_input widgets
    # Note: Widget order matters, or use key-based selection
    if len(at.number_input) >= 4:
        at.number_input[0].set_value(5000.0).run()  # span_mm
        at.number_input[1].set_value(300.0).run()   # b_mm
        at.number_input[2].set_value(500.0).run()   # D_mm
        at.number_input[3].set_value(120.0).run()   # mu_knm

    # Find and click the calculate button
    calculate_buttons = [b for b in at.button if "Calculate" in str(b.label)]
    if calculate_buttons:
        calculate_buttons[0].click().run()

    # Verify no errors
    assert not at.exception
    assert not at.error  # No st.error() called
```

### 5.3 Session State Persistence Test

```python
def test_session_state_persistence():
    """Test that session state persists between runs."""
    at = AppTest.from_file("streamlit_app/pages/01_🏗️_beam_design.py").run()

    # Set a value
    at.number_input[0].set_value(6000.0).run()

    # Re-run the app (simulates user interaction)
    at.run()

    # Check value persisted
    assert at.session_state.get("beam_inputs", {}).get("span_mm") == 6000.0
```

---

## 6. Decision Matrix

| Solution | Speed | Coverage | CI-Ready | Complexity | Recommendation |
|----------|-------|----------|----------|------------|----------------|
| AppTest | Fast | High | Yes | Low | **Primary** |
| Playwright | Slow | Complete | Medium | Medium | Supplementary |
| Selenium | Slow | Complete | Medium | High | Not recommended |
| Manual | N/A | Low | No | N/A | Not scalable |

---

## 7. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Page coverage | 100% | All pages have smoke test |
| Critical path coverage | 80% | Key user journeys tested |
| Test execution time | <30s | All AppTests run in 30s |
| CI integration | Yes | Tests run on every PR |
| Flakiness rate | <5% | Tests fail only for real issues |

---

## 8. Next Steps

1. ✅ Research complete (this document)
2. ✅ Created `tests/apptest/` structure with 29 tests (18 smoke + 11 beam design)
3. ⏳ Implement smoke tests for all pages
4. ⏳ Implement critical path tests for beam design
5. ⏳ Add to CI workflow
6. ⏳ Document in testing guide

---

## References

1. [Streamlit AppTest Documentation](https://docs.streamlit.io/develop/api-reference/app-testing)
2. [AppTest API Reference](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest)
3. [Playwright Python](https://playwright.dev/python/)
4. [Testing Streamlit Apps Blog](https://blog.streamlit.io/how-to-test-streamlit-apps/)
