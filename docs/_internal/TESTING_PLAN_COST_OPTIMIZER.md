# Comprehensive Testing Plan for Issue Discovery
**Date:** 2026-01-09
**Purpose:** Systematic testing to find remaining issues in Cost Optimizer and Beam Design flow
**Status:** 📋 Planning Phase

---

## Testing Philosophy

**Goal:** Find issues BEFORE users do by systematically testing:
1. **Happy paths** - Normal usage scenarios
2. **Edge cases** - Boundary conditions, unusual inputs
3. **Error paths** - What happens when things fail?
4. **Integration points** - Where components interact
5. **Performance** - Speed, caching, memory usage

---

## Testing Categories

### Category 1: Data Flow Testing 🔄

**Objective:** Verify data passes correctly between components

**Tests:**
1. **Beam Design → Session State**
   - [ ] Verify `beam_inputs["design_result"]` is set after design
   - [ ] Verify `design_results` is also set (dual key)
   - [ ] Check flexure dict contains all required keys
   - [ ] Verify `_bar_alternatives` exists and has 5-10 items
   - [ ] Verify `tension_steel` structure exists

2. **Session State → Cost Optimizer**
   - [ ] Cost optimizer reads from correct session state key
   - [ ] Fallback to `cached_smart_analysis` works if no session data
   - [ ] Data structure matches expected format

3. **Cost Calculation Flow**
   - [ ] Bar alternatives extracted correctly
   - [ ] Steel costs calculated for each alternative
   - [ ] Comparison table populated
   - [ ] Visualization chart receives data

**Tools:**
- Manual testing via Streamlit UI
- Add debug st.write() statements to show session state
- Check browser console for errors

**Expected Issues:**
- Missing keys in session state
- Type mismatches (dict vs object)
- None values not handled

---

### Category 2: Input Validation Testing ✅

**Objective:** Test all input edge cases and invalid combinations

**Tests:**

1. **Beam Geometry Extremes**
   - [ ] Very narrow beam: b=150mm, D=500mm
   - [ ] Very wide beam: b=600mm, D=400mm
   - [ ] Very small beam: b=200mm, D=250mm
   - [ ] Very large beam: b=500mm, D=900mm
   - [ ] Impossible d > D (should error)
   - [ ] Negative dimensions (should error)

2. **Loading Extremes**
   - [ ] Very small moment: Mu=10 kN·m
   - [ ] Very large moment: Mu=1000 kN·m
   - [ ] Zero moment (should error or handle gracefully)
   - [ ] Negative moment (should error)
   - [ ] Very small shear: Vu=5 kN
   - [ ] Very large shear: Vu=500 kN

3. **Material Combinations**
   - [ ] Lowest grade: M20 + Fe415
   - [ ] Highest grade: M40 + Fe550
   - [ ] Mid grades: M25 + Fe500
   - [ ] M40 + Fe415 (high concrete, low steel)

4. **Missing/Invalid Inputs**
   - [ ] Missing span_mm
   - [ ] Span = 0 or negative
   - [ ] Missing fck or fy
   - [ ] Invalid concrete grade (M100)

**Tools:**
- Manual input testing
- Automated test script with parametric inputs

**Expected Issues:**
- No validation for unreasonable values
- KeyError for missing required fields
- ZeroDivisionError in calculations
- No user-friendly error messages

---

### Category 3: Bar Optimizer Testing 🔧

**Objective:** Verify bar selection logic is practical and correct

**Tests:**

1. **Bar Selection Logic**
   - [ ] Test Ast=500mm² → should select 3-12mm or 3-16mm
   - [ ] Test Ast=1000mm² → should select 3-20mm or 4-16mm
   - [ ] Test Ast=1500mm² → should select 3-25mm or 5-20mm
   - [ ] Test Ast=2000mm² → should select 4-25mm or 7-20mm
   - [ ] Test Ast=3000mm² → should use 2 layers

2. **Width Constraints**
   - [ ] b=250mm → max 3-4 bars (no 32mm)
   - [ ] b=300mm → max 5 bars (no 32mm)
   - [ ] b=400mm → can use 32mm bars
   - [ ] b=500mm → 7+ bars fit in single layer

3. **Spacing Validation**
   - [ ] All alternatives have spacing ≥ 25mm
   - [ ] Spacing displayed matches calculated
   - [ ] Multi-layer triggered when spacing < 25mm

4. **Alternative Generation**
   - [ ] At least 3 alternatives generated
   - [ ] All diameters from [12, 16, 20, 25, 32] tried
   - [ ] Infeasible alternatives excluded
   - [ ] Alternatives sorted by area or cost

**Tools:**
- Unit tests for optimizer function
- Manual testing with known Ast values
- Compare to hand calculations

**Expected Issues:**
- 2-32mm bars still appearing (despite fix)
- Spacing validation not working
- Alternatives missing some diameters
- Too few alternatives (<3)

---

### Category 4: Cost Calculation Testing 💰

**Objective:** Verify cost calculations are accurate

**Tests:**

1. **Steel Cost Accuracy**
   - [ ] Verify steel density = 7850 kg/m³
   - [ ] Verify unit cost = ₹72/kg
   - [ ] Test known example: 3-25mm × 5m span
     - Area = 3×491 = 1473mm²
     - Volume = 1473×5000 = 7.365M mm³
     - Mass = 7.365M × 7.85e-9 = 57.8 kg
     - Cost = 57.8 × 72 = ₹4,162
   - [ ] Verify calculation matches expected

2. **Comparison Table**
   - [ ] All alternatives appear in table
   - [ ] Costs increase with steel area (generally)
   - [ ] ₹ symbol displays correctly
   - [ ] Relative area ratios make sense

3. **Visualization**
   - [ ] Scatter plot appears
   - [ ] Points correspond to table data
   - [ ] Lowest cost point marked as optimal
   - [ ] Hover shows correct data

4. **Edge Cases**
   - [ ] span_mm=0 → should error
   - [ ] Very long span (20m) → very high cost
   - [ ] Very short span (1m) → very low cost

**Tools:**
- Manual calculation verification
- Excel cross-check
- Unit tests for cost functions

**Expected Issues:**
- Unit conversions wrong (mm to m)
- Density or unit cost incorrect
- Rounding errors accumulating
- Display formatting issues (₹ vs Rs)

---

### Category 5: UI/UX Testing 🎨

**Objective:** Test user experience and interface behavior

**Tests:**

1. **Navigation Flow**
   - [ ] User goes to Beam Design
   - [ ] Enters inputs, clicks "Analyze Design"
   - [ ] Sees results
   - [ ] Navigates to Cost Optimizer
   - [ ] Sees "From Beam Design" auto-selected
   - [ ] Clicks "Run Cost Optimization"
   - [ ] Sees 5-10 alternatives

2. **Error Messages**
   - [ ] Friendly error when library fails
   - [ ] Clear guidance when no alternatives available
   - [ ] Helpful hints when inputs invalid

3. **Loading States**
   - [ ] Spinner shows during computation
   - [ ] Progress indication (if added)
   - [ ] Results appear smoothly

4. **Responsive Design**
   - [ ] Tables scroll on small screens
   - [ ] Charts resize properly
   - [ ] Sidebar doesn't overlap content

5. **Data Persistence**
   - [ ] Refresh page → design results lost (Issue #9)
   - [ ] Navigate away and back → results still there?
   - [ ] Multiple designs → last one shown

**Tools:**
- Manual browser testing
- Different screen sizes
- Browser dev tools

**Expected Issues:**
- No loading indicators
- Cryptic error messages
- Results lost on page refresh
- Layout breaks on mobile

---

### Category 6: Error Handling Testing 🚨

**Objective:** Test graceful degradation when things fail

**Tests:**

1. **Library Failures**
   - [ ] Mock `design_beam_is456()` to raise exception
   - [ ] Verify fallback works
   - [ ] Check user sees friendly error

2. **Optimizer Failures**
   - [ ] Mock `optimize_bar_arrangement()` to fail
   - [ ] Verify manual fallback works
   - [ ] Check alternatives still generated (Issue #5)

3. **Network/API Failures**
   - [ ] Simulate slow network
   - [ ] Simulate timeout
   - [ ] Verify retry logic or error message

4. **Session State Corruption**
   - [ ] Manually corrupt session_state
   - [ ] Verify app doesn't crash
   - [ ] Check recovery mechanism

**Tools:**
- Manual exception injection
- pytest with mocking
- Browser dev tools (throttle network)

**Expected Issues:**
- No try-except around critical operations
- Silent failures (no user notification)
- Cascading failures (one error breaks everything)
- No recovery path

---

### Category 7: Performance Testing ⚡

**Objective:** Ensure acceptable speed and resource usage

**Tests:**

1. **Computation Speed**
   - [ ] Time beam design computation: should be <2 seconds
   - [ ] Time cost optimization: should be <1 second
   - [ ] Time alternative generation: should be <3 seconds total

2. **Caching Effectiveness**
   - [ ] First design: slow
   - [ ] Same inputs again: should use cache, instant
   - [ ] Different inputs: recomputes

3. **Memory Usage**
   - [ ] Check session_state size
   - [ ] Verify no memory leaks
   - [ ] Test with 100 designs in sequence

4. **Concurrent Users**
   - [ ] Open in 2 browser tabs
   - [ ] Both should work independently
   - [ ] No session state conflicts

**Tools:**
- Python time.time() measurements
- Streamlit profiler
- Browser performance tab

**Expected Issues:**
- No caching (Issue #4)
- Slow alternative generation
- Session state grows unbounded
- Cache never cleared

---

### Category 8: Integration Testing 🔗

**Objective:** Test component interactions end-to-end

**Tests:**

1. **Full User Journey**
   ```
   Start → Beam Design page
   → Enter: 220kNm, 150kN, 300×500mm, M25, Fe500
   → Click "Analyze Design"
   → Verify: 3-25mm bars or 7-16mm bars (not 2-32mm!)
   → Navigate to Cost Optimizer
   → Click "Run Cost Optimization"
   → Verify: 5-10 alternatives shown
   → Verify: Costs displayed in ₹
   → Click "Export CSV"
   → Verify: Download works
   End
   ```

2. **Multiple Design Iterations**
   - [ ] Design 1: 220kNm
   - [ ] Design 2: 300kNm (different inputs)
   - [ ] Go to cost optimizer
   - [ ] Verify: Shows Design 2 results, not Design 1

3. **Cross-Page Data Sharing**
   - [ ] Design on Beam Design page
   - [ ] Close browser
   - [ ] Reopen (new session)
   - [ ] Check: Data lost? Expected if no persistence

**Tools:**
- Manual end-to-end testing
- Automated Selenium tests (future)

**Expected Issues:**
- Old data shown instead of new
- Session state confusion between pages
- Export fails silently

---

## Execution Plan

### Phase 1: Critical Path Testing (30 minutes)
**Priority:** HIGH
**Focus:** Verify fixes work, find showstoppers

1. Test Category 1 (Data Flow) - 15 min
2. Test Category 8 (Integration) - 15 min

**Output:** List of blocking issues

---

### Phase 2: Edge Case Testing (45 minutes)
**Priority:** MEDIUM
**Focus:** Find unusual failure modes

1. Test Category 2 (Input Validation) - 20 min
2. Test Category 3 (Bar Optimizer) - 15 min
3. Test Category 4 (Cost Calculation) - 10 min

**Output:** List of edge case bugs

---

### Phase 3: Reliability Testing (30 minutes)
**Priority:** MEDIUM
**Focus:** Error handling and robustness

1. Test Category 6 (Error Handling) - 20 min
2. Test Category 7 (Performance) - 10 min

**Output:** List of reliability issues

---

### Phase 4: UX Polish Testing (20 minutes)
**Priority:** LOW
**Focus:** User experience improvements

1. Test Category 5 (UI/UX) - 20 min

**Output:** List of UX improvements

---

## Issue Tracking Template

For each issue found, document:

```markdown
### Issue #X: [Short Title]

**Severity:** 🔴 CRITICAL / 🟡 HIGH / 🟢 MEDIUM / ⚪ LOW

**Category:** [Data Flow / Input Validation / Bar Optimizer / Cost Calculation / UI/UX / Error Handling / Performance / Integration]

**Location:** `file.py:line` or `Component → Component` flow

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Observe issue

**Expected Behavior:** What should happen

**Actual Behavior:** What actually happens

**Root Cause:** Why it fails (if known)

**Proposed Fix:**
```python
# Code or description of fix
```

**Estimated Fix Time:** X minutes

**Dependencies:** Requires Issue #Y to be fixed first (if any)
```

---

## Testing Tools & Setup

### Required Tools:
- [x] Streamlit app running locally
- [ ] Python debugger (pdb or IDE debugger)
- [ ] Browser dev tools open
- [ ] Notebook for manual test notes
- [ ] Excel for calculation verification

### Test Data Sets:

**Small Beam:**
- Mu=120 kNm, Vu=80 kN
- b=300mm, D=500mm, d=450mm
- M25, Fe500
- Expected: 3-20mm or 4-16mm

**Medium Beam:**
- Mu=220 kNm, Vu=150 kN
- b=300mm, D=500mm, d=450mm
- M25, Fe500
- Expected: 3-25mm or 7-16mm

**Large Beam:**
- Mu=400 kNm, Vu=250 kN
- b=400mm, D=600mm, d=550mm
- M30, Fe500
- Expected: 5-25mm or 4-32mm

**Edge Case Beam:**
- Mu=50 kNm, Vu=30 kN
- b=200mm, D=300mm, d=250mm
- M20, Fe415
- Expected: 3-12mm minimum

---

## Success Criteria

Testing is complete when:
- [x] All Category 1 tests pass (Data Flow)
- [ ] All Category 8 tests pass (Integration)
- [ ] At least 80% of other categories tested
- [ ] All CRITICAL issues documented
- [ ] All HIGH issues documented
- [ ] Known limitations documented

**Target:** Find 5-10 new issues minimum

---

## Deliverables

1. **Issue Report:** `COST_OPTIMIZER_ISSUES_ROUND2.md`
   - All issues found
   - Categorized by severity
   - Prioritized fix order
   - Estimated fix times

2. **Test Results Log:** Section in issue report
   - Which tests passed/failed
   - Unexpected behaviors
   - Performance metrics

3. **Recommendations:**
   - Quick wins (easy fixes, big impact)
   - Long-term improvements
   - Testing automation opportunities

---

## Notes & Observations

### Test Environment:
- Python version: 3.9
- Streamlit version: 1.50.0
- Browser: [To be filled during testing]
- OS: macOS
- structural_lib version: 0.16.0

### Testing Sessions:
- Session 1: [Date/Time] - Category 1 & 8
- Session 2: [Date/Time] - Categories 2, 3, 4
- Session 3: [Date/Time] - Categories 6, 7
- Session 4: [Date/Time] - Category 5

---

**Status:** 📋 Plan Ready - Ready to Execute
**Next Action:** Begin Phase 1 testing (Categories 1 & 8)
