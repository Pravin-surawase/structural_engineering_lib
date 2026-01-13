# Research: v0.18.0 Strategy & Library Expansion Feasibility

**Type:** Research
**Audience:** Planning
**Status:** CORRECTED - Infrastructure Already Complete
**Importance:** High
**Version:** 2.0.0
**Created:** 2026-01-13
**Last Updated:** 2026-01-13 (Corrected after evidence validation)
**Related Tasks:** TASK-501, TASK-503, TASK-504, TASK-505 (ALL COMPLETE)
**Archive Condition:** Archive after v0.18.0 planning is finalized

---

## ⚠️ CORRECTION NOTICE

**Original Analysis Error:** Initial version (v1.0.0) incorrectly stated infrastructure gaps still blocked v0.18.0.

**Evidence-Based Reality:** Sessions 20-22 (January 12-13, 2026) completed 4 of 5 critical infrastructure tasks:

| Task | Status | Evidence |
|------|--------|----------|
| TASK-501: Cross-Platform CI | ✅ COMPLETE | PR #356, `.github/workflows/python-tests.yml` (lines 46-50): `matrix: os: [ubuntu-latest, windows-latest, macos-latest]` |
| TASK-503: Performance Tracking | ✅ COMPLETE | PR #356, `.github/workflows/nightly.yml` (lines 37-60): `github-action-benchmark@v1` with 150% alert threshold |
| TASK-504: Integration Tests | ✅ COMPLETE | PR #356, `streamlit_app/tests/test_critical_journeys.py` (483 lines, 16 tests) |
| TASK-505: User Feedback | ✅ COMPLETE | PR #356, `README.md` (lines 365-371): PyPI stats badge, pypistats.org link, Issue Forms |
| TASK-502: VBA Automation | ⏳ DEFERRED | Explicitly deferred (not blocking v0.18.0) |

**Git Evidence:**
```
549dd20 TASK-501: Phase 1 Critical Infrastructure: Cross-platform CI, Performance Tracking, User Feedback, Integration Tests (#356)
de32e21 TASK-506: Core library error handling refactor and test updates (#357)
```

---

## 1. Executive Summary (CORRECTED)

**Actual Status:** 
- **Infrastructure:** ✅ 4/5 critical gaps COMPLETE (Sessions 20-22)
- **Test Suite:** ✅ 256 unit tests + 9 integration tests ALL PASSING (Session 22)
- **CI/CD:** ✅ Cross-platform validation (Linux/Windows/macOS) ACTIVE
- **User Readiness:** We ARE technically ready for v0.18.0

**User Intent (Validated):**
- Prioritize "Library Expansion" (new functions + Jinja2 + Hypothesis)
- Deprioritize Streamlit fixes (already has integration tests, can wait)

**Key Finding:** 
Infrastructure is solid. v0.18.0 can be a **Feature Release** focused on Core Library capabilities.

---

## 2. Infrastructure Status (CORRECTED: The "Actually Good" News)

### ✅ What We Accomplished (Sessions 20-22)

**TASK-501: Cross-Platform CI** ✅
- **Evidence:** `.github/workflows/python-tests.yml` lines 46-50
- **Matrix:** ubuntu-latest, windows-latest, macos-latest × Python 3.11, 3.12
- **Result:** 5 matrix jobs (6 - 1 excluded macos+3.11)
- **Windows-specific:** PowerShell packaging check added

**TASK-503: Performance Regression Tracking** ✅
- **Evidence:** `.github/workflows/nightly.yml` lines 37-60
- **Tool:** `github-action-benchmark@v1`
- **Alert Threshold:** 150% (triggers on 50%+ slowdown)
- **Storage:** Benchmark artifacts retained 90 days

**TASK-504: Streamlit Integration Tests** ✅
- **Evidence:** `streamlit_app/tests/test_critical_journeys.py` (483 lines)
- **Coverage:** 16 tests across 8 user journey classes
- **Status:** 11 pass, 5 skip (optional features)

**TASK-505: User Feedback Setup** ✅
- **Evidence:** `README.md` lines 365-371
- **PyPI Badge:** `![PyPI Downloads](https://img.shields.io/pypi/dm/structural-lib-is456)`
- **Stats Link:** [pypistats.org/packages/structural-lib-is456](https://pypistats.org/packages/structural-lib-is456)
- **Issue Forms:** `.github/ISSUE_TEMPLATE/*.yml` (4 YAML forms)

### 🔴 One Gap Remains (Non-Blocking)

**TASK-502: VBA Test Automation** ⏳
- **Status:** Explicitly deferred (requires Windows CI runner + COM automation)
- **Impact:** Not blocking v0.18.0 (manual testing continues)

---

## 3. Library Expansion Analysis (User Proposed)

The user proposed adding "more lib functions", "Jinja2", and "Hypothesis".

### 3.1 Hypothesis (Property-Based Testing)
*   **Status:** Currently in `dev` extras in `pyproject.toml`.
*   **Value:** HIGH for structural engineering. Test `beam(w, d)` with random valid floats.
*   **Readiness:** ✅ Performance tracking now in place (nightly benchmarks)
*   **Implementation Plan:**
    1.  Create `tests/properties/` directory.
    2.  Define strategies: `st_concrete_grade` (20-80), `st_beam_width` (150-1000), etc.
    3.  Apply to `ductile.py`, `shear.py`, `flexure.py` first.
    4.  Run in CI (nightly only, not on PRs - too slow).

### 3.2 Jinja2 (Templating)
*   **Status:** Currently in `report` extras in `pyproject.toml`.
*   **Value:** CRITICAL for "Professional Output". Engineers need calculation sheets.
*   **Readiness:** ✅ Cross-platform CI validates rendering on Windows/macOS
*   **Implementation Plan:**
    1.  Create `structural_lib/reports/templates/` folder.
    2.  Design `calculation_sheet.html.j2` (mimic IS 456 manual format).
    3.  Create API: `generate_html_report(design_result) -> str`.
    4.  Add CLI: `structural_lib report results.json -o report.html`.
    5.  (Future) Refactor Streamlit to use this API.

### 3.3 New Library Functions (Candidates from Backlog)

**Top 3 Candidates for v0.18.0:**

1.  **Slenderness Check (TASK-088)** - 4 hours
    - IS 456 Cl. 25.1.1-25.1.3 (short vs slender column)
    - Critical for tall beams (D/b > 4)
    - Inputs: b, D, effective length, support conditions
    - Output: `is_slender: bool`, `additional_moment: float`

2.  **Anchorage Check (TASK-087)** - 1 day
    - IS 456 Cl. 26.2.1 (development length check)
    - Essential for bar cutoffs and support detailing
    - Inputs: bar diameter, fck, fy, anchorage type
    - Output: `L_d_required: float`, `available_anchorage_ok: bool`

3.  **Torsion Design (TASK-085)** - 2-3 days
    - IS 456 Cl. 41 (torsion + shear interaction)
    - Complex but high-value (many beams have torsion)
    - Inputs: Tu (torsion), Vu (shear), b, D
    - Output: `Asv_combined`, `spacing`, `longitudinal_steel`

**Sequencing:** Slenderness → Anchorage → Torsion (increasing complexity)

---

## 4. Proposed Roadmap: v0.18.0 "Core Library Expansion"

### Phase 1: Property-Based Testing Foundation (Week 1, 8-10 hrs)
**Focus:** Add Hypothesis to existing codebase

- [ ] Create `tests/properties/` directory
- [ ] Define strategies module: `tests/properties/strategies.py`
  - `st_concrete_grade()`: 20, 25, 30, 35, 40, 50, 60, 80
  - `st_steel_grade()`: 415, 500, 550
  - `st_beam_dimensions()`: b (150-1000), D (300-1200), d/D ratio (0.85-0.95)
  - `st_design_moment()`: 10-5000 kN·m (log distribution)
- [ ] Write property tests for 3 existing modules:
  - `test_flexure_properties.py`: Test `calculate_xu_xu_lim_ast()` with 1000+ random cases
  - `test_shear_properties.py`: Test `calculate_shear_reinforcement()` similarly
  - `test_ductile_properties.py`: Test `calculate_redistribution_limit()`
- [ ] Add to `nightly.yml` (not PR checks - too slow)

**Expected Bugs Found:** 2-5 edge cases (e.g., very low moment + very high grade → negative steel)

**Success Metric:** Hypothesis finds at least 1 real bug in existing code

---

### Phase 2: Jinja2 Report Generation (Week 2, 10-12 hrs)
**Focus:** Professional HTML/PDF output

- [ ] Create `structural_lib/reports/` package
- [ ] Design template: `templates/beam_design_report.html.j2`
  - Header: Project info, beam ID, code reference (IS 456:2000)
  - Section 1: Input data table
  - Section 2: Flexural design calculations (step-by-step)
  - Section 3: Shear design calculations
  - Section 4: Detailing (bar sizes, spacing)
  - Section 5: Compliance checks (green/red status)
  - Footer: Software version, disclaimer
- [ ] Implement `generate_report()` API:
  ```python
  from structural_lib.reports import generate_html_report
  
  html = generate_html_report(design_result, template="beam_design")
  with open("report.html", "w") as f:
      f.write(html)
  ```
- [ ] Add CLI command: `structural_lib report results.json -o report.html`
- [ ] Add tests: `test_report_generation.py`
- [ ] Cross-platform validation (CI tests HTML rendering on Windows/macOS)

**Deliverable:** Engineers can generate professional calculation sheets from CLI

---

### Phase 3: New Physics - Slenderness (Week 3, 4-6 hrs)
**Focus:** Implement TASK-088 (easiest new function)

- [ ] Create `structural_lib/codes/is456/slenderness.py`
- [ ] Implement `check_slenderness(b, D, L_eff, support_conditions)`
  - IS 456 Cl. 25.1.1: `l_eff / min(b, D) ≤ 12` for no slenderness effects
  - Cl. 25.1.3: Additional moment for slender members
- [ ] Add property tests (Hypothesis)
- [ ] Add to `api.py` as `api.check_slenderness()`
- [ ] Generate report section for slenderness results
- [ ] Update docs: `docs/reference/api.md` + example

**Success Metric:** Slenderness check integrated with report generation

---

### Phase 4: New Physics - Anchorage (Week 4, 8-10 hrs)
**Focus:** Implement TASK-087 (detailing critical path)

- [ ] Create `structural_lib/codes/is456/anchorage.py`
- [ ] Implement development length calculations:
  - IS 456 Cl. 26.2.1: `L_d = φ·σ_s / (4·τ_bd)`
  - Table 16: Design bond stress values
  - Cl. 26.2.3.2: Effective anchorage beyond face of support
- [ ] Add property tests (Hypothesis)
- [ ] Integrate with `detailing.py` (bar cutoff logic)
- [ ] Generate report section
- [ ] Update docs

**Deliverable:** Complete bar detailing validation (cutoffs + anchorage)

---

## 5. Recommendation (CORRECTED)

### ✅ WE ARE READY FOR v0.18.0

**Infrastructure:** COMPLETE (4/5 tasks done, 1 deferred non-blocker)
**Test Suite:** ROBUST (256 unit + 9 integration, all passing)
**CI/CD:** PRODUCTION-GRADE (cross-platform, performance tracking)

### v0.18.0 Strategy: "Core Library Expansion"

**Theme:** Professional Engineering Features (Not Streamlit)

**Timeline:** 4 weeks (30-38 hours total)

**Deliverables:**
1. Property-based testing (Hypothesis) for robustness
2. Professional HTML report generation (Jinja2)
3. Slenderness check (new physics, 4 hrs)
4. Anchorage check (new physics, 8-10 hrs)

**NOT in v0.18.0:**
- Streamlit UI fixes (has integration tests, can wait for v0.19)
- Torsion design (too complex, defer to v0.19)
- VBA automation (deferred)

