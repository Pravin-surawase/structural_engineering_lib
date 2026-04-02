# Quality Fix Plan - Agent 6 Streamlit Features
**Date:** 2026-01-09
**Estimated Time:** 45 minutes
**Goal:** Fix 1 CRITICAL bug + 38 quality improvements

## Research Phase (10 min) ✓

### Files to Fix:
1. **01_🏗️_beam_design.py** - Move 2 imports (lines 107, 117)
2. **03_✅_compliance.py** - Add .get() to 19 dict accesses
3. **06_📐_dxf_export.py** - Add LAYERS fallback (line 58)
4. **08_📊_batch_design.py** - Add .get() to 5 dict accesses
5. **09_🔬_advanced_analysis.py** - Add .get() to 12 dict accesses

### Issue Categories:
- **CRITICAL (1 real):** LAYERS undefined in ImportError path
- **HIGH (36):** KeyError risks from direct dict access
- **MEDIUM (2):** Import hygiene (imports in functions)

## Execution Plan

### Step 1: Fix CRITICAL - LAYERS Fallback (5 min)
**File:** 06_📐_dxf_export.py
**Location:** After line 58 (in except ImportError block)
**Change:** Add fallback LAYERS definition

### Step 2: Fix Import Hygiene (5 min)
**File:** 01_🏗️_beam_design.py
**Changes:**
- Move `import hashlib` from line 107 to module top
- Move `import json` from line 117 to module top

### Step 3: Add .get() Protection - Compliance (10 min)
**File:** 03_✅_compliance.py
**Pattern:** `result['flexure']` → `result.get('flexure', {})`
**Count:** ~19 occurrences

### Step 4: Add .get() Protection - Batch Design (5 min)
**File:** 08_📊_batch_design.py
**Pattern:** `result['flexure']`, `result['shear']`, `result['status']`
**Count:** ~5 occurrences

### Step 5: Add .get() Protection - Advanced Analysis (10 min)
**File:** 09_🔬_advanced_analysis.py
**Pattern:** Similar to above
**Count:** ~12 occurrences

## Verification Plan

### Pre-Fix Baseline:
- CRITICAL: 28 (27 false positives + 1 real)
- HIGH: 64
- MEDIUM: 30
- Total: 122 issues

### Post-Fix Expected:
- CRITICAL: 27 (all false positives)
- HIGH: 28 (64 - 36 fixed)
- MEDIUM: 28 (30 - 2 fixed)
- Total: 83 issues (-39 fixed, -32%)

### Verification Steps:
1. Run scanner on each fixed file individually
2. Run full scanner on all pages
3. Compare before/after counts
4. Verify CI passes on PR #314

## Commit Strategy

**Single commit with clear message:**
```
fix(streamlit): resolve scanner issues in Agent 6 features

- Add LAYERS fallback for ImportError handling (dxf_export.py)
- Move hashlib/json imports to module level (beam_design.py)
- Add .get() protection for 36 dict accesses across 3 files
- Reduces scanner issues from 122 to 83 (-32%)

Fixes: #314 (partial - 27 false positives remain, need scanner Phase 2)
```

## Risk Assessment

**Low Risk:**
- All changes are defensive (adding fallbacks, safety checks)
- No behavior changes for happy path
- Only improves error handling

**Testing:**
- Scanner validation
- CI checks (black, ruff, pylint, AST scanner)
- Manual spot-check of changed functions

## Success Criteria

✅ Scanner shows <30 CRITICAL issues (all false positives)
✅ CI passes on PR #314
✅ No functionality regressions
✅ Ready to merge
