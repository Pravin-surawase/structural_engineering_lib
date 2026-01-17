# Recurring Issues Analysis

**Date:** 2026-01-10
**Owner:** Agent 9 (Governance)
**Purpose:** Identify patterns that need automation to prevent future issues

---

## Executive Summary

Analysis of the codebase identified 8 recurring patterns that could benefit from automation.
Priority rankings based on: frequency, impact, and ease of automation.

---

## High Priority (Automate Now)

### 1. Root Test Files (Orphaned) ✅ RESOLVED

**Pattern:** Test files in project root instead of tests/
**Current Count:** 0 files (was 3)
**Status:** ✅ Already fixed - files now in tests/

**Files (now correctly located):**
- `tests/test_quality_assessment.py` ✅
- `tests/test_scanner_detection.py` ✅
- `tests/test_xlwings_bridge.py` ✅

**Verified:** 2026-01-10

---

### 2. Stale Redirect Stubs (Small Files) ⚠️ PARTIAL

**Pattern:** Files <10 lines that are just redirects to moved files
**Current Count:** 13 stubs with references (was 17, 4 removed)
**Impact:** Clutters docs/, confusing for navigators
**Status:** ⚠️ 4 orphaned stubs removed, 13 remain with active references

**Stubs Removed (2026-01-10):**
- `docs/planning/task-210-211-session-complete.md` ✅
- `docs/planning/task-210-211-complete.md` ✅
- `docs/planning/task-210-211-work-session.md` ✅
- `docs/planning/task-210-211-status.md` ✅

**Remaining (have references - need link updates first):**
- `docs/reference/api-reference.md` (14 refs)
- `docs/getting-started/project-overview.md` (24 refs)
- `docs/reference/vba-guide.md` (12 refs)
- `docs/planning/production-roadmap.md` (11 refs)
- ... and 9 more (use `scripts/check_redirect_stubs.py` for full list)

**Automation Created:**
```bash
# Check redirect stubs
.venv/bin/python scripts/check_redirect_stubs.py

# Remove safe stubs (no references)
.venv/bin/python scripts/check_redirect_stubs.py --fix

# Preview removals
.venv/bin/python scripts/check_redirect_stubs.py --dry-run
```

**Next Steps:**
1. Run script periodically to find new orphaned stubs
2. Update references before removing remaining stubs
3. Consider bulk reference update script for future

---

### 3. Duplicate File Names ⚠️ PARTIAL

**Pattern:** Same filename in multiple directories
**Current Count:** 7 duplicate patterns (some expected, some not)
**Impact:** Confusion about canonical version, link ambiguity
**Status:** ⚠️ Automation created, 4 duplicates are redirect stubs (tracked in #2)

**Expected Duplicates (per-folder files):**
- `README.md` - one per folder is correct
- `draft.md`, `outline.md` - one per blog post is correct

**Unexpected Duplicates (redirect stubs - see #2):**
- `excel-addin-guide.md` (contributing/ is canonical, getting-started/ is stub)
- `project-overview.md` (architecture/ is canonical, getting-started/ is stub)
- `vba-guide.md` (contributing/ is canonical, reference/ is stub)
- `vba-testing-guide.md` (contributing/ is canonical, reference/ is stub)

**True Duplicate (needs resolution):**
- `ui-layout-final-decision.md` (both have substantial content)
  - `docs/research/` (27,968 bytes)
  - `docs/planning/` (46,418 bytes)

**Automation Created:**
```bash
# Find duplicate filenames
.venv/bin/python scripts/check_duplicate_docs.py

# Output as JSON for scripting
.venv/bin/python scripts/check_duplicate_docs.py --json
```

**Next Steps:**
1. Resolve ui-layout-final-decision.md (merge or archive one)
2. Remove redirect stubs when references are updated (see #2)

---

## Medium Priority (Plan for Later)

### 4. Files with Spaces in Names

**Pattern:** Files with spaces instead of hyphens
**Current Count:** 9+ files
**Impact:** Shell command issues, URL encoding problems

**Locations:**
- `external_data/` (folder and contents)
- `docs/_references/downloads-snapshot/` (reference files)

**Assessment:**
- External reference files - may be intentional to preserve original names
- Should be in .gitignore (already done for downloads-snapshot)

**Recommendation:** Add to .gitignore rather than rename (external files)

---

### 5. TODO/FIXME Comments

**Pattern:** Scattered TODO comments in code
**Current Count:** 1186 files with TODOs
**Impact:** Technical debt accumulation, forgotten tasks

**Automation Proposed:**
```python
# Script: collect_todos.py
# Generate TODO.md with all pending items
# Run monthly to track debt
```

**Note:** This is informational, not blocking

---

### 6. Empty Directories

**Pattern:** Folders with no content
**Current Count:** 2 (build artifacts, cache)
**Impact:** Minimal (already gitignored)

**Assessment:** Non-issue - these are build/cache artifacts

---

## Low Priority (Monitor)

### 7. Markdown Files Outside docs/

**Pattern:** .md files in project subdirectories
**Current Count:** 15+ files
**Impact:** Low - these are legitimate README files in component folders

**Assessment:**
- README.md in Python/, Excel/, tests/ - intentional and useful
- No automation needed - this is correct structure

---

### 8. Tests in Nested Locations

**Pattern:** Test files in docs/_internal/
**Current Count:** 6 files
**Impact:** Low - these are QA assessment scripts, not unit tests

**Assessment:**
- Located in `docs/_internal/quality-assessments/`
- Historical assessment scripts, not part of test suite
- Archive or keep for reference

---

## Immediate Actions

### Fix Now (3 items)

1. **Move root test files to tests/**
   ```bash
   git mv test_quality_assessment.py tests/
   git mv test_scanner_detection.py tests/
   git mv test_xlwings_bridge.py tests/
   ```

2. **Clean up redirect stubs**
   - Verify stubs point to valid targets
   - Remove redirect-only files

3. **Resolve duplicate docs**
   - Identify canonical versions
   - Archive or remove duplicates

### Automate Later (2 items)

1. **check_redirect_stubs.py** - Flag small files with redirect pattern
2. **check_duplicate_docs.py** - Flag duplicate filenames

---

## Tracking

| Issue | Priority | Status | Automation |
|-------|----------|--------|------------|
| Root test files | High | ✅ Resolved | N/A (already fixed) |
| Redirect stubs | High | ⚠️ Partial (4 removed, 13 remain) | `scripts/check_redirect_stubs.py` ✅ |
| Duplicate docs | High | ⚠️ Partial (1 true duplicate found) | `scripts/check_duplicate_docs.py` ✅ |
| Spaces in names | Medium | Gitignored | N/A |
| TODO comments | Medium | Track monthly | Script |
| Empty dirs | Low | Non-issue | N/A |
| MD outside docs | Low | Correct | N/A |
| Nested tests | Low | Historical | N/A |
