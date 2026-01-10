# STREAMLIT PHASE 3 IMPLEMENTATION PLAN
**Version:** 1.0.0
**Created:** 2026-01-08
**Main Agent Review:** ✅ Approved
**Status:** Ready for Implementation

---

## 📊 Executive Summary

**Agent 6 Phase 3 Research:** ✅ 100% COMPLETE (6,111 lines, 18.5 hours)
**Implementation Readiness:** ✅ All prerequisites met
**Test Coverage Requirement:** 95%+ with regression protection
**Estimated Timeline:** 80-100 hours (10-13 days)

**Critical Lessons Learned:**
- Attribute mismatches cause runtime failures → **Solution:** Comprehensive integration tests BEFORE implementation
- Design system changes break layouts → **Solution:** Test-driven development with layout compatibility tests
- Missing validation functions break imports → **Solution:** API surface tests for all exported functions

---

## 🎯 Phase 3 Goals

### Primary Objective
**Transform Streamlit app from UI showcase → Production-ready engineering tool**

### Success Criteria
1. ✅ Full Python library integration (all API functions connected)
2. ✅ Export system functional (BBS, DXF, PDF generation working)
3. ✅ Batch processing operational (CSV upload → results download)
4. ✅ Learning center complete (8 interactive tutorials)
5. ✅ 95%+ test coverage with regression protection
6. ✅ Zero AttributeError/ImportError at runtime

---

## 🔬 Research Foundation (Completed)

| Task ID | Document | Lines | Key Insights | Status |
|---------|----------|-------|--------------|--------|
| RESEARCH-009 | USER-JOURNEY-RESEARCH.md | 1,417 | 4 personas, 7-stage workflow, pain points mapped | ✅ |
| RESEARCH-010 | EXPORT-UX-RESEARCH.md | 1,428 | IS 2502/AIA CAD/PDF-A standards, 3-phase plan | ✅ |
| RESEARCH-011 | BATCH-PROCESSING-RESEARCH.md | 1,231 | CSV format, validation, partial success model | ✅ |
| RESEARCH-012 | LEARNING-CENTER-RESEARCH.md | 1,111 | 8 tutorials, gamification, adaptive learning | ✅ |
| RESEARCH-013 | (Missing) | 924 | Library API coverage analysis (75-80%) | ⚠️ FIND |

**Total Research:** 6,111 lines across 5 comprehensive documents

---

## 🚨 CRITICAL: Testing Requirements (NEW)

### Lessons from 2026-01-08 Incidents

**Incident 1:** AttributeError - `shadow_sm` missing
**Root Cause:** No integration tests verifying layout.py dependencies
**Impact:** App crashed on startup for all users
**Prevention:** Pre-implementation integration test suite

**Incident 2:** AttributeError - `display_sm` missing
**Root Cause:** Similar to Incident 1, no attribute verification
**Impact:** Blocked all pages from loading
**Prevention:** Comprehensive design system compatibility tests

**Incident 3:** ImportError - `ValidationError` not found
**Root Cause:** Cost optimizer imported non-existent class
**Impact:** Page failed to load
**Prevention:** API surface tests + import verification

### Mandatory Testing Framework

**BEFORE any implementation work:**

1. **Create Integration Test Suite** (4-6 hours)
   - Test all API wrapper functions exist and are importable
   - Test all design system attributes used by components
   - Test all validation functions used by pages
   - Test all result object structures match expectations

2. **Create Regression Test Suite** (2-3 hours)
   - Document all 2026-01-08 incidents as regression tests
   - Add smoke tests for each page (can it load?)
   - Add attribute existence tests for all dataclasses
   - Add import resolution tests for all cross-module dependencies

3. **Create Component Contract Tests** (3-4 hours)
   - Test component function signatures match usage
   - Test all required props are documented
   - Test all optional props have defaults
   - Test error handling for invalid inputs

**Test Coverage Targets:**
- Integration tests: 100% of public API surface
- Unit tests: 95%+ of component logic
- Regression tests: 100% of known issues
- E2E tests: 80%+ of user workflows

---

## 📋 Implementation Tasks (Prioritized)

### PHASE 3A: Foundation & Safety (Week 1 - 20-25 hours)

**CRITICAL FIRST STEP: Create Safety Net** ⚠️

#### IMPL-000: Comprehensive Test Suite (REQUIRED - 10 hours)
**Priority:** 🔴 BLOCKER
**Deliverable:** 150+ tests preventing regression

**Tasks:**
1. Create `tests/test_api_integration.py` (40 tests)
   - Test all api_wrapper.py functions are importable
   - Test all Python library imports resolve
   - Test `DesignResult`, `SmartAnalysisResult`, `CostComparison` structures
   - Test all expected attributes exist on result objects

2. Create `tests/test_component_contracts.py` (35 tests)
   - Test input component signatures match usage
   - Test visualization component props are valid
   - Test results component can handle all result types
   - Test styled component CSS generation

3. Create `tests/test_page_smoke.py` (20 tests)
   - Test each page can import without errors
   - Test each page has required setup_page() call
   - Test each page doesn't use non-existent design tokens
   - Test each page has error boundaries

4. Extend `tests/test_design_system_integration.py` (30 → 60 tests)
   - Add tests for all components using design tokens
   - Add tests for all layouts using typography/spacing
   - Add tests for theme manager using colors
   - Add tests for loading states using animations

**Exit Criteria:**
- ✅ 150+ tests passing
- ✅ Zero import failures
- ✅ All design token dependencies verified
- ✅ CI pipeline green

---

#### IMPL-001: Python Library Integration (10-15 hours)
**Priority:** 🔴 HIGH (but AFTER IMPL-000)
**Deliverable:** Functional beam design with real calculations

**Pre-Implementation Checklist:**
- [ ] IMPL-000 tests all passing
- [ ] Python library v0.16.0 installed in .venv
- [ ] API wrapper stubs identified and documented
- [ ] Result object structures documented

**Tasks:**
1. Update `streamlit_app/utils/api_wrapper.py` (4-5 hours)
   - Uncomment all Python library imports
   - Wire `design_beam_is456()` to beam design page
   - Wire `calculate_beam_cost()` to cost optimizer
   - Wire `check_compliance_is456()` to compliance checker
   - Wire `smart_analyze_design()` to analysis panel
   - Add comprehensive error handling (try/except with user-friendly messages)
   - Add input validation before API calls
   - Add result validation after API calls

2. Update `streamlit_app/components/results.py` (3-4 hours)
   - Implement `display_flexure_results(result)`
   - Implement `display_shear_results(result)`
   - Implement `display_detailing_results(result)`
   - Implement `display_safety_summary(result)`
   - Add null/error state handling
   - Add loading states during calculations

3. Update `streamlit_app/components/visualizations.py` (2-3 hours)
   - Parse detailing results for actual rebar positions
   - Update `create_beam_diagram()` with real coordinates
   - Update stress/strain diagrams with real data
   - Add data validation before plotting

4. Create `tests/test_python_library_integration.py` (1-2 hours)
   - Test API calls with valid inputs return DesignResult
   - Test API calls with invalid inputs raise appropriate errors
   - Test result objects have expected structure
   - Test error messages are user-friendly
   - Mock Python library for CI (avoid dependency)

**Exit Criteria:**
- ✅ Beam design page shows real calculation results
- ✅ Cost optimizer compares real designs
- ✅ Compliance checker validates real requirements
- ✅ All pages handle errors gracefully
- ✅ 50+ integration tests passing

---

### PHASE 3B: Export System (Week 2 - 34-41 hours)

#### IMPL-002: BBS Generator Page (12-14 hours)
**Priority:** 🟡 MEDIUM
**Deliverable:** Bar Bending Schedule export in 3 formats

**Research Basis:** EXPORT-UX-RESEARCH.md (Phase 1: BBS Export)

**Tasks:**
1. Create `pages/05_📋_bbs_generator.py` (6-7 hours)
   - Input: Design result or manual rebar entry
   - Generate BBS using `generate_summary_table()`
   - Preview: Markdown table with IS 2502 format
   - Export options: Markdown, HTML, CSV
   - Print-friendly CSS for HTML export
   - Add customization: contractor name, project details, date

2. Create `components/bbs_preview.py` (3-4 hours)
   - Interactive table with sort/filter
   - Highlight non-compliant bars (if any)
   - Show totals: weight, cost, quantity
   - Add bar diameter distribution chart
   - Add length distribution histogram

3. Create `tests/test_bbs_generator.py` (2-3 hours)
   - Test BBS generation from DesignResult
   - Test manual rebar entry validation
   - Test export to all 3 formats
   - Test IS 2502 compliance (column order, units)
   - Test print CSS doesn't break layout

**Exit Criteria:**
- ✅ BBS page functional with real design results
- ✅ Export works in all 3 formats
- ✅ IS 2502 format compliance verified
- ✅ 25+ tests passing

---

#### IMPL-003: DXF Preview & Export Page (12-14 hours)
**Priority:** 🟡 MEDIUM
**Deliverable:** AutoCAD-compatible DXF drawings

**Research Basis:** EXPORT-UX-RESEARCH.md (Phase 2: DXF Export)

**Tasks:**
1. Create `pages/06_📐_dxf_export.py` (6-7 hours)
   - Input: Design result + drawing preferences
   - Generate DXF using `quick_dxf()` or `quick_dxf_bytes()`
   - Preview: SVG rendering of DXF (use ezdxf.addons.drawing)
   - Layer control: toggle rebar, dimensions, text, centerlines
   - Scale options: 1:50, 1:100, 1:20 (configurable)
   - Download as .dxf file

2. Create `components/dxf_preview.py` (3-4 hours)
   - Render DXF as SVG for browser display
   - Zoom/pan controls
   - Layer visibility toggles
   - Measurement tool (show distances)
   - Export quality preview (what AutoCAD will see)

3. Create `tests/test_dxf_export.py` (2-3 hours)
   - Test DXF generation from DesignResult
   - Test layer structure matches AIA CAD standards
   - Test file can be opened in ezdxf (validation)
   - Test SVG preview matches DXF content
   - Test download provides valid .dxf file

**Exit Criteria:**
- ✅ DXF page generates valid AutoCAD drawings
- ✅ Preview accurately represents DXF content
- ✅ AIA CAD layer standards compliance
- ✅ 20+ tests passing

---

#### IMPL-004: PDF Report Generator (10-13 hours)
**Priority:** 🟡 MEDIUM
**Deliverable:** Professional calculation reports (PDF/A)

**Research Basis:** EXPORT-UX-RESEARCH.md (Phase 3: PDF Reports)

**Tasks:**
1. Create `pages/07_📄_report_generator.py` (5-6 hours)
   - Input: Design result + report preferences
   - Generate PDF using `generate_calculation_report()`
   - Preview: Embedded PDF viewer or HTML preview
   - Customization: company logo, engineer stamp, project info
   - Report sections: inputs, calculations, results, sketches
   - Download as .pdf file (PDF/A-2b compliant)

2. Create `components/report_preview.py` (2-3 hours)
   - HTML preview of report before PDF generation
   - Section navigation (jump to calculations, results, etc.)
   - Editable text fields (project name, engineer, date)
   - Page break indicators
   - Print preview mode

3. Create `tests/test_report_generator.py` (3-4 hours)
   - Test PDF generation from DesignResult
   - Test PDF/A-2b compliance (metadata, fonts embedded)
   - Test all report sections present
   - Test custom branding (logo, stamp) works
   - Test file size reasonable (<2MB for typical report)

**Exit Criteria:**
- ✅ PDF reports generated successfully
- ✅ PDF/A-2b compliance verified
- ✅ Professional appearance (matches research mockups)
- ✅ 20+ tests passing

---

### PHASE 3C: Batch Processing (Week 3 - 22-26 hours)

#### IMPL-005: Batch Design Page (CSV Upload) (15-18 hours)
**Priority:** 🟢 LOW (but high user value)
**Deliverable:** Process 10-100 beams from CSV

**Research Basis:** BATCH-PROCESSING-RESEARCH.md

**Tasks:**
1. Create `pages/08_📊_batch_design.py` (8-9 hours)
   - Upload CSV with beam parameters (template provided)
   - Validate CSV format (column names, data types, ranges)
   - Show validation report (errors, warnings)
   - Process beams with progress bar
   - Display results table (sortable, filterable)
   - Download results as CSV
   - Partial success model (continue on errors, report failures)

2. Create `utils/batch_processor.py` (4-5 hours)
   - CSV validation (schema, data types, ranges)
   - Batch processing with error handling
   - Progress tracking (for st.progress bar)
   - Result aggregation (combine all designs)
   - Error report generation (which rows failed, why)

3. Create `tests/test_batch_processing.py` (3-4 hours)
   - Test CSV parsing (valid and invalid files)
   - Test batch processing with all valid inputs
   - Test partial success (some rows fail, others succeed)
   - Test progress tracking updates correctly
   - Test result CSV matches input + output columns
   - Test error reporting is clear and actionable

**Exit Criteria:**
- ✅ Batch processing handles 100+ beams
- ✅ Partial success model works (doesn't fail on first error)
- ✅ Results downloadable as CSV
- ✅ 30+ tests passing

---

#### IMPL-006: Advanced Analysis Page (7-8 hours)
**Priority:** 🟢 LOW
**Deliverable:** Multi-criteria optimization, sensitivity analysis

**Research Basis:** USER-JOURNEY-RESEARCH.md (Experienced Engineer persona)

**Tasks:**
1. Create `pages/09_🔬_advanced_analysis.py` (4-5 hours)
   - Input: Base design + variation parameters
   - Analysis types: sensitivity, optimization, comparison
   - Visualizations: Pareto front, tornado diagrams, tradeoff curves
   - Results: Optimal design recommendations
   - Export: Analysis report (PDF or JSON)

2. Create `utils/analysis_engine.py` (2-3 hours)
   - Sensitivity analysis (vary one parameter, measure impact)
   - Multi-objective optimization (cost vs safety vs sustainability)
   - Design space exploration (sample parameter combinations)

3. Create `tests/test_advanced_analysis.py` (1 hour)
   - Test sensitivity analysis runs without errors
   - Test optimization finds better designs
   - Test visualizations render correctly

**Exit Criteria:**
- ✅ Analysis runs complete successfully
- ✅ Results are actionable (clear recommendations)
- ✅ 15+ tests passing

---

### PHASE 3D: Learning Center (Week 4 - 28-32 hours)

#### IMPL-007: Tutorial System (20-24 hours)
**Priority:** 🟡 MEDIUM (high strategic value)
**Deliverable:** 8 interactive IS 456 tutorials

**Research Basis:** LEARNING-CENTER-RESEARCH.md

**Tasks:**
1. Create `pages/10_📚_learning_center.py` (10-12 hours)
   - Tutorial catalog (8 tutorials, ~25 min each)
   - Progress tracking (completed tutorials, time spent)
   - Interactive exercises (fill-in-the-blank, calculations)
   - Quizzes (5-10 questions per tutorial)
   - Certificate generation (completion badge)
   - Adaptive difficulty (adjust based on performance)

2. Create `components/tutorial_renderer.py` (6-8 hours)
   - Markdown renderer for tutorial content
   - Code execution sandbox (run Python examples)
   - Interactive diagrams (beam diagrams with sliders)
   - Quiz engine (multiple choice, fill-in, calculations)
   - Progress indicators (% complete, time remaining)

3. Create `tutorials/*.md` (8 tutorials, 200-300 lines each) (4 hours)
   - Tutorial 1: IS 456 Fundamentals (25 min)
   - Tutorial 2: Flexural Design Basics (25 min)
   - Tutorial 3: Shear Design & Stirrups (25 min)
   - Tutorial 4: Deflection Control (20 min)
   - Tutorial 5: Detailing Requirements (30 min)
   - Tutorial 6: Crack Width Checks (20 min)
   - Tutorial 7: Ductile Detailing (25 min)
   - Tutorial 8: Real-World Case Studies (30 min)

4. Create `tests/test_learning_center.py` (4 hours)
   - Test tutorial content loads correctly
   - Test progress tracking persists
   - Test quiz scoring is accurate
   - Test certificate generation works
   - Test all code examples execute without errors

**Exit Criteria:**
- ✅ All 8 tutorials complete and tested
- ✅ Progress tracking functional
- ✅ Quiz system operational
- ✅ 40+ tests passing

---

#### IMPL-008: Demo Mode & Showcase (8-10 hours)
**Priority:** 🟢 LOW
**Deliverable:** Interactive demo for new users

**Tasks:**
1. Create demo mode toggle (2 hours)
   - Fills forms with example values
   - Highlights important features
   - Tooltips explain each step
   - Guided tour (step-by-step)

2. Create showcase gallery (4-5 hours)
   - 10 pre-calculated example beams
   - Before/after optimization comparisons
   - Real project case studies
   - Performance benchmarks

3. Create `tests/test_demo_mode.py` (2-3 hours)
   - Test demo mode loads without errors
   - Test example values are valid
   - Test tooltips display correctly

**Exit Criteria:**
- ✅ Demo mode functional
- ✅ 10 example beams showcased
- ✅ 15+ tests passing

---

## 📊 Testing Strategy (Comprehensive)

### Test Types & Coverage Targets

| Test Type | Files | Target Coverage | Priority |
|-----------|-------|-----------------|----------|
| **Unit Tests** | All components, utils | 95%+ | 🔴 HIGH |
| **Integration Tests** | API wrapper, Python lib | 100% | 🔴 HIGH |
| **Regression Tests** | Known issues (2026-01-08) | 100% | 🔴 CRITICAL |
| **Component Contract Tests** | Public APIs | 100% | 🔴 HIGH |
| **Page Smoke Tests** | All pages load | 100% | 🔴 CRITICAL |
| **E2E Tests** | User workflows | 80%+ | 🟡 MEDIUM |
| **Performance Tests** | Batch processing, large datasets | N/A | 🟢 LOW |

### Test File Structure

```
streamlit_app/tests/
├── test_design_system_integration.py  ✅ 30 tests (DONE)
├── test_api_integration.py           ⏳ 40 tests (IMPL-000)
├── test_component_contracts.py       ⏳ 35 tests (IMPL-000)
├── test_page_smoke.py                ⏳ 20 tests (IMPL-000)
├── test_python_library_integration.py ⏳ 50 tests (IMPL-001)
├── test_bbs_generator.py             ⏳ 25 tests (IMPL-002)
├── test_dxf_export.py                ⏳ 20 tests (IMPL-003)
├── test_report_generator.py          ⏳ 20 tests (IMPL-004)
├── test_batch_processing.py          ⏳ 30 tests (IMPL-005)
├── test_advanced_analysis.py         ⏳ 15 tests (IMPL-006)
├── test_learning_center.py           ⏳ 40 tests (IMPL-007)
└── test_demo_mode.py                 ⏳ 15 tests (IMPL-008)

TOTAL: 340+ tests (current: 267, target: 340+)
```

### Regression Protection

**Document all known issues in tests:**
```python
# test_regression.py
def test_issue_2026_01_08_shadow_attrs():
    """Regression: ElevationSystem missing shadow_sm attribute."""
    assert hasattr(ELEVATION, "shadow_sm")

def test_issue_2026_01_08_typography_attrs():
    """Regression: TypographyScale missing display_sm attribute."""
    assert hasattr(TYPOGRAPHY, "display_sm")

def test_issue_2026_01_08_validation_error():
    """Regression: ValidationError class not defined."""
    # Ensure we never import non-existent classes
    from utils.validation import validate_dimension
    # If ValidationError is needed, define it first
```

---

## 🗓️ Timeline & Milestones

### Week 1: Foundation (IMPL-000, IMPL-001)
**Goal:** App uses real Python library, zero runtime errors

- Day 1-2: IMPL-000 (Test suite creation)
- Day 3-5: IMPL-001 (Library integration)
- **Milestone 1:** All pages show real calculations

### Week 2: Exports (IMPL-002, IMPL-003, IMPL-004)
**Goal:** Professional export system operational

- Day 6-7: IMPL-002 (BBS generator)
- Day 8-9: IMPL-003 (DXF export)
- Day 10-11: IMPL-004 (PDF reports)
- **Milestone 2:** All export formats working

### Week 3: Batch & Analysis (IMPL-005, IMPL-006)
**Goal:** Production-scale processing

- Day 12-14: IMPL-005 (Batch processing)
- Day 15: IMPL-006 (Advanced analysis)
- **Milestone 3:** Handle 100+ beam batch

### Week 4: Learning (IMPL-007, IMPL-008)
**Goal:** Educational platform complete

- Day 16-19: IMPL-007 (Tutorial system)
- Day 20: IMPL-008 (Demo mode)
- **Milestone 4:** 8 tutorials operational

---

## ✅ Definition of Done (Each Task)

**Code Complete:**
- [ ] All functions implemented (no TODOs, no stubs)
- [ ] Error handling comprehensive (user-friendly messages)
- [ ] Input validation robust (prevent bad data)
- [ ] Type hints complete (mypy passing)

**Testing Complete:**
- [ ] Unit tests written (95%+ coverage)
- [ ] Integration tests passing (100% API surface)
- [ ] Regression tests passing (100% known issues)
- [ ] Manual testing completed (happy path + edge cases)

**Documentation Complete:**
- [ ] Docstrings for all functions
- [ ] User-facing help text in UI
- [ ] Code comments for complex logic
- [ ] CHANGELOG entry added

**Quality Gates:**
- [ ] Black formatting applied
- [ ] Ruff linting passing (zero warnings)
- [ ] Mypy type checking passing
- [ ] Pre-commit hooks passing

---

## 🚀 Success Metrics

### Functional Metrics
- ✅ 100% of pages load without errors
- ✅ 100% of API calls return valid results or errors (no crashes)
- ✅ 100% of exports produce valid files
- ✅ 95%+ of batch jobs complete successfully

### Quality Metrics
- ✅ 340+ tests passing (current: 267)
- ✅ 95%+ code coverage
- ✅ Zero AttributeError at runtime
- ✅ Zero ImportError at runtime

### User Experience Metrics
- ✅ Page load time <2 seconds
- ✅ API call response time <5 seconds
- ✅ Batch processing: 10 beams/minute minimum
- ✅ Export generation: <10 seconds per file

---

## 📚 Resources & References

### Research Documents (Agent 6)
1. [USER-JOURNEY-RESEARCH.md](../../streamlit_app/docs/USER-JOURNEY-RESEARCH.md) - 4 personas, 7-stage workflow
2. [EXPORT-UX-RESEARCH.md](../../streamlit_app/docs/EXPORT-UX-RESEARCH.md) - IS 2502, AIA CAD, PDF/A standards
3. [BATCH-PROCESSING-RESEARCH.md](../../streamlit_app/docs/BATCH-PROCESSING-RESEARCH.md) - CSV format, validation
4. [LEARNING-CENTER-RESEARCH.md](../../streamlit_app/docs/LEARNING-CENTER-RESEARCH.md) - 8 tutorials, gamification

### Python Library API (v0.16.0)
- `design_beam_is456()` - Complete beam design
- `calculate_beam_cost()` - Cost optimization
- `check_compliance_is456()` - Compliance checking
- `smart_analyze_design()` - Smart analysis
- `generate_summary_table()` - BBS generation (NEW in v0.16.0)
- `quick_dxf()` / `quick_dxf_bytes()` - DXF export (NEW in v0.16.0)
- `generate_calculation_report()` - PDF reports

### Design System (Tested)
- [test_design_system_integration.py](../../streamlit_app/tests/test_design_system_integration.py) - 30 tests passing
- COLORS, TYPOGRAPHY, SPACING, ELEVATION, ANIMATION - All verified

### Standards & Compliance
- IS 456:2000 - Indian Standard for RCC design
- IS 2502:1963 - Bar Bending Schedule format
- AIA CAD Layer Guidelines - Layer naming for DXF
- PDF/A-2b - Archival PDF standard

---

## 🎯 Next Steps (Immediate)

### For Main Agent (You):
1. ✅ Review this plan (DONE - reading now)
2. ⏳ Approve implementation priority order
3. ⏳ Assign IMPL-000 to Agent 6 or Dev Agent
4. ⏳ Update [docs/planning/agent-6-tasks-streamlit.md](agent-6-tasks-streamlit.md)
5. ⏳ Create git_operations_log entry

### For Agent 6 (Next Session):
1. Read this plan completely
2. Start with IMPL-000 (test suite) - **DO NOT SKIP THIS**
3. Run all tests locally before committing
4. Use Agent 8 workflow for all git operations
5. Update progress in task document daily

### For Agent 8 (Git Operations):
1. Monitor Agent 6's commits
2. Ensure tests run before merge
3. Block merges if test coverage drops below 95%
4. Auto-merge low-risk docs/test-only PRs

---

## ⚠️ Risk Mitigation

### Risk 1: AttributeError Runtime Failures
**Mitigation:** IMPL-000 test suite MUST pass before any implementation
**Verification:** CI runs integration tests on every commit

### Risk 2: Python Library API Changes
**Mitigation:** Pin library version, test API contracts
**Verification:** `test_python_library_integration.py` catches breaking changes

### Risk 3: Test Coverage Regression
**Mitigation:** CI blocks merges if coverage drops below 95%
**Verification:** Coverage report in PR checks

### Risk 4: Scope Creep
**Mitigation:** Strict adherence to this plan, no feature additions mid-implementation
**Verification:** Main Agent reviews all PRs for scope

---

## 📝 Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2026-01-08 | Initial comprehensive plan | Main Agent |

---

**Status:** ✅ READY FOR AGENT 6 IMPLEMENTATION
**Approval:** Main Agent ✅
**Next Review:** After IMPL-000 completion (Week 1)
