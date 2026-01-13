# IMPL-004: Error Handling & Graceful Degradation

**Task ID:** IMPL-004
**Priority:** 🟠 HIGH
**Status:** 🚧 IN PROGRESS
**Estimated Time:** 3-4 hours
**Created:** 2026-01-09

---

## 📋 Objective

Improve error messages and implement graceful degradation throughout the Streamlit app to provide professional, user-friendly error handling that helps users recover from issues quickly.

---

## 🎯 Success Criteria

1. ✅ All errors show actionable user-friendly messages
2. ✅ App never crashes to white screen
3. ✅ Graceful degradation when library unavailable
4. ✅ Input validation prevents bad data from reaching library
5. ✅ Error boundaries catch and display exceptions
6. ✅ 30+ error handling tests passing
7. ✅ User can always recover without page reload

---

## 🔍 Current State Analysis

### Issues Found (from recent sessions):

1. **TypeError: '>' not supported between instances of 'NoneType' and 'int'**
   - Location: `visualizations.py:157`
   - Cause: `xu` parameter is None, but code tries comparison
   - Impact: App crashes when rendering beam diagrams

2. **StreamlitDuplicateElementId**
   - Location: Multiple `plotly_chart` calls without unique keys
   - Cause: Missing `key` parameter in st.plotly_chart()
   - Impact: App crashes when rendering multiple charts

3. **AttributeError incidents** (2026-01-08)
   - Missing design system attributes
   - Missing validation functions
   - Impact: Prevented app from loading

4. **Library import failures**
   - When `structural_lib` not available
   - No graceful fallback
   - Impact: App unusable

5. **Poor input validation**
   - Invalid inputs reach library
   - Cryptic error messages
   - No guidance for users

---

## 🏗️ Implementation Plan

### Part 1: Enhanced Error Handler (1-1.5 hours)

**File:** `utils/error_handler.py` (enhance existing)

**Features to Add:**

```python
class ErrorSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ErrorContext:
    """Enhanced error context with recovery suggestions"""
    severity: ErrorSeverity
    message: str
    technical_details: str
    recovery_steps: List[str]
    can_continue: bool
    fallback_value: Optional[Any]

def handle_library_error(e: Exception, context: str) -> ErrorContext:
    """Handle errors from structural_lib with user-friendly messages"""

def handle_validation_error(e: Exception, field: str) -> ErrorContext:
    """Handle input validation errors with specific guidance"""

def handle_visualization_error(e: Exception, chart_type: str) -> ErrorContext:
    """Handle chart rendering errors with fallback options"""

@contextmanager
def error_boundary(
    fallback_value: Any = None,
    show_error: bool = True,
    severity: ErrorSeverity = ErrorSeverity.ERROR
):
    """Context manager for graceful error handling with fallback"""
    try:
        yield
    except Exception as e:
        if show_error:
            display_error_with_recovery(e, severity)
        return fallback_value
```

**Tests:** `tests/test_error_handler_enhanced.py` (10 tests)

---

### Part 2: Input Validation Enhancement (1 hour)

**File:** `utils/validators.py` (new)

**Validation Functions:**

```python
class ValidationResult:
    """Result of input validation with detailed feedback"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    sanitized_value: Any

def validate_beam_inputs(
    span_mm: float,
    width_mm: float,
    depth_mm: float,
    **kwargs
) -> ValidationResult:
    """Validate beam geometry with IS 456 constraints"""
    # Check: span > 0
    # Check: width >= 150mm (IS 456 minimum)
    # Check: depth >= 200mm (typical minimum)
    # Check: d/b ratio reasonable (1.5 to 3.5)
    # Check: span/depth ratio reasonable (10 to 25)

def validate_material_inputs(
    fck: float,
    fy: float
) -> ValidationResult:
    """Validate material properties"""
    # Check: fck in [15, 20, 25, 30, 35, 40, 45, 50]
    # Check: fy in [250, 415, 500, 550]

def validate_loading_inputs(
    dead_load_kn_m: float,
    live_load_kn_m: float
) -> ValidationResult:
    """Validate loading with engineering checks"""
    # Check: loads >= 0
    # Check: total load reasonable (< 1000 kN/m typically)
    # Check: dead/live ratio makes sense (0.5 to 4.0)

def sanitize_numeric_input(
    value: Any,
    min_val: float,
    max_val: float,
    default: float
) -> float:
    """Safely convert and bound numeric input"""
```

**Tests:** `tests/test_validators.py` (15 tests)

---

### Part 3: Graceful Library Fallback (45 min)

**File:** `utils/api_wrapper.py` (enhance existing)

**Features to Add:**

```python
class LibraryStatus:
    """Track library availability and version"""
    available: bool
    version: Optional[str]
    missing_modules: List[str]
    error_message: Optional[str]

def get_library_status() -> LibraryStatus:
    """Check library availability with detailed diagnostics"""

def with_library_fallback(fallback_fn: Callable):
    """Decorator for graceful library fallback"""
    def wrapper(*args, **kwargs):
        if not is_library_available():
            st.warning("⚠️ Design library unavailable. Using simplified calculations.")
            return fallback_fn(*args, **kwargs)
        try:
            return original_fn(*args, **kwargs)
        except ImportError as e:
            st.error(f"Library import failed: {e}")
            return fallback_fn(*args, **kwargs)
    return wrapper

@with_library_fallback(fallback_fn=_fallback_design)
def run_beam_design(...):
    """Run beam design with automatic fallback"""
```

**Tests:** `tests/test_library_fallback.py` (8 tests)

---

### Part 4: Visualization Error Handling (45 min)

**File:** `components/visualizations.py` (enhance)

**Fixes:**

1. **Add None checks everywhere:**
```python
def create_beam_diagram(...):
    # Before: if xu > 0:
    # After:
    if xu is not None and xu > 0:
        # render strain distribution
    else:
        # show "data unavailable" placeholder
```

2. **Add unique keys to all charts:**
```python
# Before: st.plotly_chart(fig)
# After:
st.plotly_chart(fig, key=f"beam_diagram_{diagram_id}")
```

3. **Add error boundaries:**
```python
with error_boundary(fallback_value=create_placeholder_chart()):
    fig = create_beam_diagram(...)
    st.plotly_chart(fig, key=chart_key)
```

4. **Add data validation:**
```python
def create_beam_diagram(...) -> go.Figure:
    # Validate all inputs first
    if not _validate_diagram_inputs(span_mm, width_mm, depth_mm, xu, ast):
        return _create_error_chart("Invalid beam parameters")

    # Proceed with rendering
```

**Tests:** `tests/test_visualization_errors.py` (12 tests)

---

### Part 5: Page-Level Error Boundaries (30 min)

**Update all pages:** `01_🏗️_beam_design.py`, etc.

**Pattern:**

```python
# At top of page
from utils.error_handler import error_boundary, ErrorSeverity

# Wrap design calculation
with error_boundary(severity=ErrorSeverity.ERROR, show_error=True):
    result = run_beam_design(...)
    if result:
        display_results(result)

# Wrap visualizations
with error_boundary(fallback_value=None):
    fig = create_beam_diagram(...)
    if fig:
        st.plotly_chart(fig, key=f"diagram_{tab_name}")
```

**Tests:** `tests/test_page_error_handling.py` (10 tests)

---

## 📊 Error Message Templates

### For Users:
```
❌ Design Failed
The beam design could not be completed due to invalid inputs.

Problem: Span/depth ratio (45.5) exceeds recommended limit (25)

Suggestions:
• Increase beam depth from 200mm to at least 364mm
• Reduce span from 9100mm
• Or click "Override" to proceed anyway (not recommended)

[View Details] [Try Again] [Reset Inputs]
```

### For Developers (expandable):
```
Technical Details (click to expand):
---
Exception: ValueError
Location: flexure.py:145
Message: xu_max cannot be greater than effective depth
Stack trace: [...]
---
```

---

## 🧪 Testing Strategy

### Test Coverage:

1. **Error Handler Tests** (10 tests)
   - Test each error severity level
   - Test recovery suggestions
   - Test fallback values
   - Test error display formatting

2. **Validator Tests** (15 tests)
   - Test beam geometry validation
   - Test material validation
   - Test loading validation
   - Test boundary cases (min/max)
   - Test sanitization

3. **Library Fallback Tests** (8 tests)
   - Test library unavailable scenario
   - Test missing module scenario
   - Test import error scenario
   - Test fallback calculations
   - Test status diagnostics

4. **Visualization Error Tests** (12 tests)
   - Test None parameter handling
   - Test invalid data handling
   - Test duplicate key prevention
   - Test placeholder charts
   - Test error boundaries

5. **Page Error Handling Tests** (10 tests)
   - Test page doesn't crash on bad input
   - Test error messages display correctly
   - Test recovery options work
   - Test partial results displayed
   - Test session state preserved

**Total:** 55 tests (exceeds 30+ target)

---

## 🚀 Rollout Plan

### Step 1: Create Enhanced Error Handler (30 min)
```bash
# Create/enhance files
touch streamlit_app/utils/error_handler.py  # enhance existing
touch streamlit_app/tests/test_error_handler_enhanced.py

# Run tests
pytest streamlit_app/tests/test_error_handler_enhanced.py -v
```

### Step 2: Add Validators (30 min)
```bash
touch streamlit_app/utils/validators.py
touch streamlit_app/tests/test_validators.py

pytest streamlit_app/tests/test_validators.py -v
```

### Step 3: Enhance Library Fallback (30 min)
```bash
# Update existing file
vim streamlit_app/utils/api_wrapper.py
touch streamlit_app/tests/test_library_fallback.py

pytest streamlit_app/tests/test_library_fallback.py -v
```

### Step 4: Fix Visualization Errors (30 min)
```bash
# Update existing file
vim streamlit_app/components/visualizations.py
touch streamlit_app/tests/test_visualization_errors.py

pytest streamlit_app/tests/test_visualization_errors.py -v
```

### Step 5: Add Page Error Boundaries (30 min)
```bash
# Update all pages
vim streamlit_app/pages/01_🏗️_beam_design.py
# ... repeat for other pages

touch streamlit_app/tests/test_page_error_handling.py
pytest streamlit_app/tests/test_page_error_handling.py -v
```

### Step 6: Integration Test (15 min)
```bash
# Run full test suite
pytest streamlit_app/tests/ -v

# Manual testing
streamlit run streamlit_app/app.py
# Test error scenarios:
# - Invalid inputs
# - Library unavailable
# - None parameters
# - Network issues (if applicable)
```

### Step 7: Commit via Agent 8 (15 min)
```bash
./scripts/ai_commit.sh "feat(streamlit): IMPL-004 error handling & graceful degradation

- Enhanced error_handler.py with ErrorContext and recovery suggestions
- Added validators.py with comprehensive input validation
- Enhanced api_wrapper.py with library fallback decorator
- Fixed visualizations.py None parameter handling
- Added error boundaries to all pages
- Added 55 error handling tests (100% passing)

Impact:
- No more white screen crashes
- User-friendly error messages with recovery steps
- Graceful degradation when library unavailable
- Comprehensive input validation
- Professional error experience

Tests: 55 new tests, 100% passing
Lines: ~800 new lines (code + tests + docs)"
```

---

## 📈 Success Metrics

After IMPL-004:

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| White screen crashes | ~5/week | 0 | 0 |
| User error reports | High | Low | <2/week |
| Error message clarity | 2/5 | 4.5/5 | >4/5 |
| Recovery success rate | ~30% | >90% | >85% |
| Library fallback working | ❌ No | ✅ Yes | ✅ Yes |
| Input validation coverage | ~40% | ~95% | >90% |
| Error handling tests | 15 | 70 | >50 |

---

## 🔗 Dependencies

**Requires:**
- ✅ IMPL-001 (Library Integration) - for fallback testing
- ✅ IMPL-002 (Results Display) - for error display components
- ✅ IMPL-003 (Page Integration) - for page-level error boundaries

**Enables:**
- IMPL-005 (Session State) - reliable state with error recovery
- IMPL-006 (Performance) - graceful degradation under load
- All FEAT-xxx tasks - production-ready error handling

---

## 📚 References

- `docs/CODE-AUDIT-2026-01-08.md` - Known issues
- `docs/IMPL-001-LIBRARY-INTEGRATION.md` - Library usage patterns
- `docs/IMPL-002-COMPLETE.md` - Results display contracts
- Python `contextlib` docs - for error_boundary pattern
- Streamlit error handling best practices

---

## 🎓 Lessons from Previous Sessions

1. **None checks everywhere** - Never assume optional parameters exist
2. **Unique keys always** - All Streamlit widgets need unique keys
3. **Test error paths** - 50% of code is error handling, test it!
4. **User-friendly messages** - Engineers need actionable guidance
5. **Graceful degradation** - App should work even without library

---

**Status:** Ready to implement
**Next Step:** Part 1 - Enhanced Error Handler
**Assigned to:** Agent 6 (Background Agent)
**Timeline:** 3-4 hours total (can split across 2 sessions)
