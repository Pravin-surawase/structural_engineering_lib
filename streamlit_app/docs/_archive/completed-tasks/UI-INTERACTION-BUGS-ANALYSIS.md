# UI Interaction Bugs - Root Cause Analysis

**Date:** 2026-01-08
**Agent:** Agent 6 (Streamlit UI Specialist)
**Status:** 🔴 CRITICAL BUGS IDENTIFIED

---

## 🐛 Reported Issues

### Issue 1: Dropdowns Not Fully Visible
**Symptom:** Material grade, exposure condition dropdowns show truncated text

**Example:**
```
Expected: "M25 - Standard beams/columns"
Actual:   "M25 - Standard bea..."
```

### Issue 2: Geometry Diagram Not Updating
**Symptom:** After changing inputs (span, width, depth), the beam diagram doesn't refresh

### Issue 3: Design Can't Be Re-run After First Analysis
**Symptom:** After first "Analyze Design", changing inputs and clicking button again doesn't update results

---

## 🔍 Root Cause Analysis

### Bug #1: Dropdown Truncation

**Location:** `components/inputs.py` lines 165-172, 200-207

**Problem:**
```python
# Current code creates LONG option strings:
grade_options = [f"{g} - {props['description']}" for g, props in grades_db.items()]
# Example: "M25 - Standard beams/columns"
#          "Very Severe - Marine, chemical"
```

**Why it happens:**
- Streamlit `selectbox` has fixed width in column layout
- Long descriptions get truncated with ellipsis
- No `format_func` parameter used to separate display from value

**Impact:** Medium - Functional but poor UX

---

### Bug #2: Geometry Diagram Not Updating

**Location:** `pages/01_🏗️_beam_design.py` lines 371-381

**Problem:**
```python
# Diagram is rendered OUTSIDE the rerun trigger
if st.session_state.beam_inputs.get('design_computed', False):
    # ... tabs ...
    with tab2:
        # Create diagram with session_state values
        fig = create_beam_diagram(
            b_mm=st.session_state.beam_inputs['b_mm'],  # ← These are updated
            D_mm=st.session_state.beam_inputs['D_mm'],  # ← But diagram only renders
            d_mm=st.session_state.beam_inputs['d_mm'],  #   when design_computed=True
            ...
        )
```

**Why it happens:**
- Diagram only shows after "Analyze Design" button clicked
- Session state updates inputs immediately (lines 114, 126, 138, 150)
- But diagram is inside `if design_computed` block
- So diagram shows OLD values until button clicked again

**Impact:** HIGH - Confusing UX, looks like inputs are ignored

**Expected behavior:**
1. User changes width from 300→350mm
2. Geometry preview updates immediately (before clicking Analyze)
3. Results stay stale until Analyze clicked

---

### Bug #3: Design Won't Re-run

**Location:** `pages/01_🏗️_beam_design.py` lines 218-243

**Problem:**
```python
if st.button("🚀 Analyze Design", disabled=not all_valid, use_container_width=True):
    st.session_state.beam_inputs['design_computed'] = False  # ← Line 219

    with loading_context("spinner", "Computing design... Please wait"):
        # ... call cached_design() ...

        st.session_state.beam_inputs['design_result'] = result
        st.session_state.beam_inputs['design_computed'] = True  # ← Line 237
        st.success("✅ Design computed successfully!")
        st.rerun()  # ← Line 239 triggers rerun
```

**Why it happens:**
1. **Cache issue:** `cached_design()` uses `@st.cache_data` (in `utils/api_wrapper.py`)
2. When inputs change, cache key should change, but it doesn't
3. Line 219 sets `design_computed=False` but cache still returns OLD result
4. Line 237 sets `design_computed=True` with OLD cached result
5. UI shows old results even though inputs changed

**Cache key problem:**
```python
# In utils/api_wrapper.py
@st.cache_data
def cached_design(mu_knm, vu_kn, b_mm, D_mm, d_mm, fck_nmm2, fy_nmm2, span_mm, exposure):
    # Cache key = hash(all parameters)
    # If ANY parameter changes, cache should miss
    # BUT if parameters are SAME as previous call, cache hits with OLD result
```

**The REAL issue:**
- Button click at line 218 triggers function
- Line 219 sets `design_computed=False`
- Line 224 calls `cached_design()` with CURRENT inputs
- IF inputs are same as last time → cache HIT → returns old result
- IF inputs changed → cache MISS → computes new result
- **BUT** after `st.rerun()` at line 239, the NEXT render cycle starts
- In next cycle, button is NOT clicked, so block doesn't execute
- Result: UI shows result from line 237, but block never runs again until button clicked

**Secondary issue - session state updates:**
```python
# Lines 104-150: Input widgets update session state IMMEDIATELY
st.session_state.beam_inputs['span_mm'] = span  # ← Happens on every widget change
st.session_state.beam_inputs['b_mm'] = b
# ... etc

# But these updates DON'T trigger design recomputation
# Design only recomputes when button clicked
```

**Impact:** CRITICAL - Core functionality broken

---

## ✅ Solutions

### Fix #1: Dropdown Truncation (EASY)

**Option A: Use `format_func` parameter**
```python
def material_selector(...):
    # Show SHORT labels in dropdown
    grades = list(CONCRETE_GRADES.keys())

    selected_grade = st.selectbox(
        "Concrete Grade (IS 456 Table 2)",
        options=grades,  # Just ["M20", "M25", "M30", ...]
        index=default_idx,
        format_func=lambda g: f"{g} - {CONCRETE_GRADES[g]['description']}",  # ← Display format
        key=key
    )

    # Then show full description BELOW dropdown
    st.caption(f"📋 {CONCRETE_GRADES[selected_grade]['description']}")
```

**Option B: Remove descriptions from dropdown, add info panel**
```python
selected_grade = st.selectbox(
    "Concrete Grade (IS 456 Table 2)",
    options=list(CONCRETE_GRADES.keys()),  # Just ["M20", "M25", ...]
    index=default_idx,
    key=key
)

# Show info panel below
st.info(f"**{selected_grade}:** {CONCRETE_GRADES[selected_grade]['description']}")
```

**Recommendation:** Option A - More compact, better UX

---

### Fix #2: Geometry Diagram Not Updating (MEDIUM)

**Approach: Always show preview, separate from results**

```python
# In col_preview section (line 258)
with col_preview:
    st.header("📊 Design Preview")

    # ALWAYS show geometry preview (not gated by design_computed)
    with st.expander("📐 Geometry Visualization", expanded=True):
        cover = 30  # Default or from exposure
        bar_dia = 16  # Placeholder
        rebar_positions = [...]  # Calculate from current inputs
        xu = st.session_state.beam_inputs['d_mm'] * 0.33

        fig = create_beam_diagram(
            b_mm=st.session_state.beam_inputs['b_mm'],  # ← Always current
            D_mm=st.session_state.beam_inputs['D_mm'],
            d_mm=st.session_state.beam_inputs['d_mm'],
            rebar_positions=rebar_positions,
            xu=xu,
            bar_dia=bar_dia,
            cover=cover
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # THEN show results if computed
    if st.session_state.beam_inputs.get('design_computed', False):
        st.subheader("📊 Design Results")
        # ... existing tabs ...
```

**Benefits:**
- Geometry preview always visible and up-to-date
- Clear separation: preview (always) vs results (after analysis)
- User sees changes immediately

---

### Fix #3: Design Won't Re-run (COMPLEX)

**Root cause:** Cache + session state + rerun interaction

**Solution: Add cache invalidation trigger**

```python
# In pages/01_🏗️_beam_design.py

# Add input hash to session state
def get_input_hash():
    """Hash of all inputs to detect changes"""
    import hashlib
    inputs_str = f"{st.session_state.beam_inputs['mu_knm']}_{st.session_state.beam_inputs['vu_kn']}_{st.session_state.beam_inputs['b_mm']}_{st.session_state.beam_inputs['D_mm']}_{st.session_state.beam_inputs['d_mm']}_{st.session_state.beam_inputs['concrete_grade']}_{st.session_state.beam_inputs['steel_grade']}_{st.session_state.beam_inputs['span_mm']}_{st.session_state.beam_inputs['exposure']}"
    return hashlib.md5(inputs_str.encode()).hexdigest()

# After line 76 (session state initialization)
if 'last_input_hash' not in st.session_state:
    st.session_state.last_input_hash = None

# Before button (after line 213)
current_hash = get_input_hash()
inputs_changed = (current_hash != st.session_state.last_input_hash)

# Update button logic (line 218)
if st.button("🚀 Analyze Design", disabled=not all_valid, use_container_width=True):
    # Clear result if inputs changed
    if inputs_changed:
        st.session_state.beam_inputs['design_result'] = None
        st.session_state.beam_inputs['design_computed'] = False

    st.session_state.last_input_hash = current_hash  # ← Store hash

    with loading_context("spinner", "Computing design... Please wait"):
        try:
            # Clear cache explicitly if needed
            if inputs_changed:
                from utils.api_wrapper import clear_cache
                clear_cache()  # ← Force fresh computation

            result = cached_design(...)

            st.session_state.beam_inputs['design_result'] = result
            st.session_state.beam_inputs['design_computed'] = True
            st.success("✅ Design computed successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Design computation failed: {str(e)}")
```

**Alternative: Remove cache for design function**
```python
# In utils/api_wrapper.py
# Remove @st.cache_data decorator
def cached_design(...):
    """Design computation (no caching - always fresh)"""
    # Direct call to Python library
    return run_design(...)
```

**Recommendation:**
1. Short term: Remove cache (simpler, always works)
2. Long term: Smart cache invalidation based on input hash

---

## 📋 Implementation Plan

### Phase 1: Critical Fixes (30 min)
1. ✅ Fix dropdown truncation (Option A with `format_func`)
2. ✅ Fix geometry preview (always show, separate from results)
3. ✅ Fix design re-run (remove cache or add invalidation)

### Phase 2: Testing (15 min)
1. ✅ Test dropdown text fully visible
2. ✅ Test geometry updates on input change
3. ✅ Test design updates on button click with different inputs
4. ✅ Test design stays same if inputs unchanged

### Phase 3: Documentation (15 min)
1. ✅ Update UI-IMPLEMENTATION-AGENT-GUIDE.md with lessons learned
2. ✅ Add to known issues / solutions catalog
3. ✅ Update test suite to catch these patterns

---

## 🎯 Success Criteria

- [ ] Dropdown shows full text: "M25 - Standard beams/columns" (no ellipsis)
- [ ] Geometry diagram updates immediately when width/depth changed
- [ ] Design results update when inputs changed + button clicked
- [ ] Design results stay same when button clicked without input changes
- [ ] No console errors
- [ ] Smooth UX (no flickering, fast response)

---

## 📚 Lessons Learned

### 1. Streamlit Dropdown Best Practices
- Keep option text short OR use `format_func`
- Show detailed info separately (caption, info panel, expander)
- Don't embed long descriptions in selectbox options

### 2. Session State + Rerun Patterns
- Input widgets update session state immediately
- But UI only re-renders after `st.rerun()` or next interaction
- Separate "input changed" from "computation triggered"

### 3. Caching Pitfalls
- `@st.cache_data` is powerful but can cause stale data
- Always provide cache invalidation mechanism
- For user-driven actions, consider NO caching (instant response more important)

### 4. Preview vs Results
- Show live preview ALWAYS (e.g., geometry)
- Show computed results ONLY AFTER analysis
- Clear visual separation improves UX

---

## 🔄 Next Steps

1. Implement fixes in order (dropdown → geometry → design re-run)
2. Test each fix independently
3. Commit with descriptive messages
4. Update agent guide with patterns
5. Add regression tests to prevent recurrence

---

**Status:** Ready for implementation
**Priority:** HIGH
**Estimated time:** 1 hour total
