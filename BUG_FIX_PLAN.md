# Bug Fix Plan - Agent 6 Work
**Date:** 2026-01-09
**PR:** #314
**Status:** 28 CRITICAL issues found by scanner

## Issue Categories

### Category A: FALSE POSITIVES (Scanner needs improvement)
These are valid code patterns that scanner incorrectly flags:

1. **kwargs parameter (2 issues)**
   - File: `01_beam_design.py` lines 129, 138
   - Reason: Function has `**kwargs` in signature - these are valid
   - Action: No fix needed, scanner Phase 2 improvement required

2. **Loop variables (9 issues)**
   - File: `11_demo_showcase.py` lines 253-265
   - Code: `for name, scenario in DEMO_SCENARIOS.items():`
   - Reason: `name` and `scenario` are loop variables - valid
   - Action: No fix needed, scanner Phase 2 improvement required

**Total False Positives: 11 issues**

### Category B: REAL BUGS (Must fix before merge)

#### B1: NameError - Missing Constants (HIGH PRIORITY)
1. **LAYERS dictionary missing**
   - File: `06_dxf_export.py` line 222
   - Code: `for layer_name, (color, linetype) in LAYERS.items():`
   - Fix: Define LAYERS constant at module level

#### B2: ZeroDivisionError - Missing Validation (HIGH PRIORITY)
Multiple files have unprotected division operations:

1. **01_beam_design.py** - Line 36
2. **02_cost_optimizer.py** - Lines 37, 395
3. **05_bbs_generator.py** - Lines 36
4. **06_dxf_export.py** - Lines 36
5. **08_batch_design.py** - Lines 38, 99, 277, 279, 281
6. **09_advanced_analysis.py** - Lines 38, 156, 157
7. **11_demo_showcase.py** - Lines 36, 328, 440, 486

**Total: 17 ZeroDivisionError risks**

Pattern: All at line 36-38 suggest common utility function
Action: Check if these are the same function, fix at source

#### B3: Import Statements Inside Functions (MEDIUM PRIORITY)
1. `01_beam_design.py` line 107: `import hashlib` inside `get_input_hash()`
2. `01_beam_design.py` line 117: `import json` inside `create_cached_beam_diagram()`

Fix: Move imports to module level

### Category C: WARNINGS (Not blocking, but should fix)

#### C1: KeyError risks
Multiple dictionary accesses without `.get()`:
- result['flexure'], result['shear'], result['status']
- Multiple files, ~20 occurrences

#### C2: AttributeError risks
Session state access without checking:
- st.session_state.design_results
- st.session_state.cost_results
- Multiple files, ~5 occurrences

#### C3: ValueError risks
int() calls without try/except:
- Multiple files, ~15 occurrences

**Total Category C: ~40 warnings** (HIGH/MEDIUM severity, not CRITICAL)

## Fix Strategy

### Phase 1: Fix Real CRITICAL Bugs (Priority: MUST FIX)
1. Add LAYERS constant to `06_dxf_export.py`
2. Add zero-checks for all 17 division operations
3. Move imports to module level (2 fixes)

**Estimated: 20 fixes, 30-45 minutes**

### Phase 2: Fix HIGH Warnings (Priority: SHOULD FIX)
1. Replace dict['key'] with dict.get('key', default)
2. Add session state checks

**Estimated: ~25 fixes, 30 minutes**

### Phase 3: Document Scanner Improvements Needed
1. Loop variable detection
2. **kwargs parameter detection
3. Create GitHub issue for scanner Phase 2

## Execution Plan

**Step 1:** Verify each line 36-38 division issue (might be same code)
**Step 2:** Create multi_replace batch for all real bugs
**Step 3:** Test with scanner (should reduce CRITICAL to 0)
**Step 4:** Push to worktree branch
**Step 5:** Wait for CI
**Step 6:** Merge PR #314

## Expected Results After Fixes

- CRITICAL: 28 → 11 (false positives remain)
- HIGH: 64 → ~30 (after dict/session fixes)
- MEDIUM: 30 → ~20 (after int() fixes)
- Total: 122 → ~61 issues

**CI Status:** Should PASS (false positives don't block CI)
