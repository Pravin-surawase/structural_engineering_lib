# Streamlit App Issues Analysis

**Type:** Research
**Audience:** All Agents
**Status:** In Progress
**Importance:** Critical
**Created:** 2026-01-14
**Last Updated:** 2026-01-14
**Related Tasks:** SESSION-24
**Archive Condition:** Archive when Status: Complete

---

## Executive Summary

User-reported issues with the Streamlit app identified 10+ bugs spanning API mismatches, UI rendering problems, and missing features. This document catalogs all issues, identifies root causes, and proposes fixes.

---

## Issue Catalog

### 🔴 CRITICAL (Blocking Functionality)

#### ISSUE-001: Advanced Analysis Page Crashes
**Error:** `TypeError: cached_design() missing 7 required positional arguments`
**Location:** `pages/09_🔬_advanced_analysis.py:161`
**Root Cause:** Page uses old parameter names (`L`, `b`, `D`, `fck`, `fy`, `Mu`, `Vu`) but `cached_design()` expects (`mu_knm`, `vu_kn`, `b_mm`, `D_mm`, `d_mm`, `fck_nmm2`, `fy_nmm2`).
**Fix:** Update all calls in advanced_analysis.py to use correct parameter names.

#### ISSUE-002: Sensitivity Analysis Crashes
**Error:** Same as ISSUE-001
**Location:** `pages/09_🔬_advanced_analysis.py:415`
**Root Cause:** Same API signature mismatch.

#### ISSUE-003: Loading Scenarios Crashes
**Error:** `IndexError: list index out of range`
**Location:** `pages/09_🔬_advanced_analysis.py:301`
**Root Cause:** DataFrame column check fails when expected columns don't exist.

---

### 🟠 HIGH (Incorrect Behavior)

#### ISSUE-004: Incorrect Utilization Numbers
**Report:** "Flexure Utilization 🟡 86.1%, Shear Utilization 🔴 120.4%"
**Location:** `pages/01_🏗️_beam_design.py` (display logic)
**Root Cause:** Need to verify calculation and display logic.

#### ISSUE-005: Compliance Page Wrong Values
**Report:** "Provided: —, Required: —" for all checks
**Location:** `pages/03_✅_compliance.py`
**Root Cause:** Compliance checks not receiving proper data from design result.

#### ISSUE-006: Cost Optimization Shows No Savings
**Report:** "Baseline Cost ₹2,238, Optimal Cost ₹2,238, Savings ₹0"
**Location:** `pages/02_💰_cost_optimizer.py`
**Root Cause:** Optimization logic not finding better alternatives.

---

### 🟡 MEDIUM (UI/UX Issues)

#### ISSUE-007: Material Dropdown Height/Font Issues
**Report:** "Materials M25 Fe500" dropdown text not visible like other dropdowns
**Location:** `pages/01_🏗️_beam_design.py` input section
**Root Cause:** CSS styling or component configuration issue.

#### ISSUE-008: Double Printed "Capacity Utilization"
**Report:** "📊 Capacity Utilization" printed twice
**Location:** `pages/01_🏗️_beam_design.py`
**Root Cause:** Duplicate section render call.

#### ISSUE-009: Geometry Preview - Reinforcement Details
**Report:** Steel numbers, diameters, and shear spacing not properly formatted
**Location:** `components/preview.py`
**Root Cause:** Need better formatting for reinforcement display.

#### ISSUE-010: Report Generator Missing Dependency
**Report:** "Missing Dependency: reportlab"
**Location:** `pages/07_📄_report_generator.py`
**Status:** Expected - optional dependency not installed.

#### ISSUE-011: DXF Export Annotations Misplaced
**Report:** "Annotations are all over the place"
**Location:** `pages/06_📐_dxf_export.py` / `structural_lib/dxf_export.py`
**Root Cause:** DXF text positioning logic needs refinement.

---

## Git Workflow Issues (Session 23 Learnings)

### Issue: Repeated CI Failures
**Symptoms:**
1. Black formatting failures on new code
2. Ruff import sorting failures
3. MyPy type errors (unused ignores, any-return)

**Root Causes:**
1. **Pre-commit not running locally** - New files weren't being formatted before commit
2. **Ruff isort different from black** - Black formats code but doesn't sort imports
3. **TYPE_CHECKING pattern not used** - For optional imports like Jinja2

### Solutions Applied:
1. Run `black` and `ruff check --fix` locally before committing new files
2. Use `TYPE_CHECKING` pattern for optional dependencies:
   ```python
   from typing import TYPE_CHECKING
   if TYPE_CHECKING:
       from optional_lib import OptionalClass
   ```
3. For template render returns, use explicit type annotation:
   ```python
   rendered: str = template.render(**context)
   return rendered
   ```

### Recommendations for Agents:
1. **Always run formatters on new files:**
   ```bash
   .venv/bin/python -m black <new_file>
   .venv/bin/python -m ruff check <new_file> --fix
   ```
2. **Run mypy on new library code:**
   ```bash
   .venv/bin/python -m mypy Python/structural_lib/<module>.py
   ```
3. **Check CI once, then fix all issues together** rather than fixing one at a time

---

## API Compatibility Matrix

| Page | cached_design Call | Correct? | Fix Required |
|------|-------------------|----------|--------------|
| 01_beam_design.py | ✅ Uses correct params | Yes | No |
| 02_cost_optimizer.py | Needs check | TBD | TBD |
| 03_compliance.py | Needs check | TBD | TBD |
| 09_advanced_analysis.py | ❌ Uses old params | No | **YES** |

---

## Fix Priority and Effort

| Issue | Priority | Effort | Blocked By |
|-------|----------|--------|------------|
| ISSUE-001 | P0 | Low | - |
| ISSUE-002 | P0 | Low | - |
| ISSUE-003 | P0 | Low | - |
| ISSUE-005 | P1 | Medium | - |
| ISSUE-004 | P1 | Medium | - |
| ISSUE-006 | P2 | Medium | - |
| ISSUE-007 | P2 | Low | - |
| ISSUE-008 | P2 | Low | - |
| ISSUE-009 | P2 | Medium | - |
| ISSUE-011 | P3 | High | - |
| ISSUE-010 | P3 | Low | User install |

---

## Clarification on Jinja2 Reports vs Streamlit UI

**User Question:** "Will the Streamlit app UI change after Jinja2?"

**Answer:** **No.** The Jinja2 reports module (`structural_lib.reports`) generates standalone HTML report files for export/printing. It does NOT change the Streamlit web UI itself.

- **Streamlit UI:** Built with Streamlit components (`st.columns`, `st.metric`, etc.)
- **Jinja2 Reports:** Generates downloadable HTML/PDF for professional documentation

These are separate concerns. The Streamlit pages would need to be updated separately.

---

## Action Plan

### Phase 1: Critical Fixes (This Session)
1. Fix advanced_analysis.py API calls
2. Fix compliance page data flow
3. Fix double printing issue

### Phase 2: UI Improvements
4. Fix dropdown styling
5. Improve geometry preview formatting
6. Improve cost optimization display

### Phase 3: Future Work
7. DXF annotation positioning
8. Consider PDF dependency as optional extra
