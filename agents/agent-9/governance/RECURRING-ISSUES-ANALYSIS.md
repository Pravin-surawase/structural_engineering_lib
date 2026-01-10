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

### 1. Root Test Files (Orphaned)

**Pattern:** Test files in project root instead of tests/
**Current Count:** 3 files
**Impact:** Confusing structure, tests may not run in CI

**Files Found:**
- `test_quality_assessment.py` (root)
- `test_scanner_detection.py` (root)
- `test_xlwings_bridge.py` (root)

**Automation Proposed:**
```yaml
# Pre-commit hook: check-test-location
- id: check-test-location
  name: Check test files are in tests/
  entry: |
    find . -maxdepth 1 -name "test_*.py" -exec echo "ERROR: {} should be in tests/" \;
  language: system
```

**Manual Fix:**
```bash
git mv test_*.py tests/
```

---

### 2. Stale Redirect Stubs (Small Files)

**Pattern:** Files <10 lines that are just redirects to moved files
**Current Count:** 10+ files
**Impact:** Clutters docs/, confusing for navigators

**Files Found (sample):**
- `docs/research/research-detailing.md` (6 lines)
- `docs/contributing/git-workflow-for-ai-agents.md` (6 lines)
- `docs/contributing/troubleshooting.md` (6 lines)

**Automation Proposed:**
```python
# Script: check_redirect_stubs.py
# Flag files <10 lines with "Moved to" pattern
```

**Manual Fix:**
```bash
# Verify content exists at target
wc -l docs/path/file.md
cat docs/path/file.md  # Should show redirect

# If redirect only, remove
git rm docs/path/file.md
```

---

### 3. Duplicate File Names

**Pattern:** Same filename in multiple directories
**Current Count:** 10+ duplicates
**Impact:** Confusion about canonical version, link ambiguity

**Duplicates Found:**
- `README.md` (expected - per-folder)
- `current-state-and-goals.md` (unexpected)
- `deep-project-map.md` (unexpected)
- `next-session-brief.md` (unexpected)
- `mission-and-principles.md` (unexpected)

**Automation Proposed:**
```python
# Script: check_duplicate_docs.py
# Flag duplicate filenames (excluding README.md, index.md)
```

**Manual Fix:**
- Identify canonical version
- Redirect or archive duplicates
- Update references

---

## Medium Priority (Plan for Later)

### 4. Files with Spaces in Names

**Pattern:** Files with spaces instead of hyphens
**Current Count:** 9+ files
**Impact:** Shell command issues, URL encoding problems

**Locations:**
- `files from external yser/` (folder and contents)
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
| Root test files | High | Action needed | Pre-commit hook |
| Redirect stubs | High | Action needed | Script |
| Duplicate docs | High | Action needed | Script |
| Spaces in names | Medium | Gitignored | N/A |
| TODO comments | Medium | Track monthly | Script |
| Empty dirs | Low | Non-issue | N/A |
| MD outside docs | Low | Correct | N/A |
| Nested tests | Low | Historical | N/A |
