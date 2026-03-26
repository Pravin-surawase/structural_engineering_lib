# Scanner Improvements Research

**Type:** Research
**Audience:** Developers
**Status:** Complete
**Importance:** High
**Created:** 2026-01-20
**Last Updated:** 2026-01-21
**Related Tasks:** TASK-354, TASK-355

---

## Executive Summary

The `check_streamlit_issues.py` scanner (~2200 lines) is a sophisticated AST-based static analyzer with **9 enhancement phases**. This research identified **false positives**, **missing detections**, and **improvement opportunities**.

**Results:**
- **0 false positives** - Phase 9 structural guarantee detection eliminates all ~150 false positives
- Scanner now correctly handles fixed-size loops and structural guarantees
- Performance is good (~1-2s for all pages)
- All 43 unit tests pass

---

## Current Scanner Capabilities

### Detections (9 Phases)

| Phase | Feature | Status |
|-------|---------|--------|
| 1 | NameError - undefined variables | ✅ Working |
| 2 | Import inside functions | ✅ Working |
| 3 | Guard clause / API signature | ✅ Working |
| 4 | Path division detection | ✅ Working |
| 5 | Widget default validation | ✅ Working |
| 6 | Session state safe methods | ✅ Working |
| 7 | Widget key conflicts | ✅ Working |
| 8 | ZeroDivisionError detection | ✅ Working |
| 9 | Fixed-size container guarantees | ✅ **NEW** - Implemented 2026-01-21 |

### Severity Levels

| Level | Meaning | Current Count |
|-------|---------|---------------|
| CRITICAL | Will crash at runtime | 0 in pages |
| HIGH | Likely to crash | 0 |
| MEDIUM | Potential issues | 0 |
| LOW | Style/best practice | 21 |

---

## Phase 9: Structural Guarantee Detection (COMPLETED)

**Implementation Date:** 2026-01-21
**Impact:** Eliminated ~150 false positives

### What It Does

Tracks list containers built with fixed-iteration loops and calculates guaranteed minimum sizes:

```python
# Scanner now tracks this pattern:
corners = []
for end_pt in [beam.point1, beam.point2]:  # 2 iterations
    for w_sign in [-1, 1]:                  # × 2 iterations
        for d_sign in [-1, 1]:              # × 2 iterations
            corners.append((cx, cy, cz))    # = 8 elements guaranteed

# These are now correctly identified as safe:
x_mesh = [c[0] for c in corners]  # corners[0-7] all valid
```

### Implementation Details

**New tracking variables in `StreamlitIssueScanner.__init__`:**
- `fixed_size_containers: Dict[str, int]` - Maps container name → guaranteed minimum size
- `empty_list_assignments: Dict[str, int]` - Tracks where `var = []` or `var = list()` appears

**New methods:**
- `_get_fixed_iteration_count(iter_node)` - Returns count for `[a,b,c]`, `(a,b,c)`, `range(n)` literals
- `_count_nested_fixed_loops(node)` - Multiplies nested loop counts for `.append()` calls

**Enhanced methods:**
- `visit_Assign()` - Now tracks empty list assignments
- `visit_For()` - Detects fixed-iteration loops with `.append()` calls
- `visit_Subscript()` - Checks `fixed_size_containers` before flagging IndexError

### Unit Tests

5 new tests in `TestPhase9FixedSizeContainers`:
1. `test_detects_single_loop_container_size` - Single `range(5)` loop
2. `test_detects_nested_loop_container_size` - 2×2×2 nested loops = 8 elements
3. `test_flags_access_beyond_guaranteed_bounds` - Correctly flags `items[5]` when only 3 elements
4. `test_detects_tuple_iteration_count` - Tuple literals `(1,2,3,4)` = 4 elements
5. `test_flags_unknown_iteration_source` - Unknown sources still flagged

---

## False Positive Analysis (RESOLVED)

### 1. IndexError on Structurally Guaranteed Lists (FIXED)

**Location:** `06_multi_format_import.py` lines 834-923

**Pattern:**
```python
# Scanner previously flagged corners[0] through corners[7] as IndexError risks
# But corners is ALWAYS built with exactly 8 elements:
corners = []
for end_pt in [beam.point1, beam.point2]:  # Always 2 iterations
    for w_sign in [-1, 1]:                  # Always 2 iterations
        for d_sign in [-1, 1]:              # Always 2 iterations
            corners.append((cx, cy, cz))    # 2 × 2 × 2 = 8 elements
```

**Resolution:** Phase 9 now detects this pattern automatically. The `.scanner-ignore.yml` entries for `corners[0-7]` have been removed.

### 2. Type Hint Warnings (4 issues)

**Pattern:**
```python
def main() -> None:  # Missing return type on dict-returning functions
```

**Issue:** Scanner flags functions returning dict without type hints as MEDIUM.

**Recommendation:** Lower to LOW or remove - this is style, not a crash risk.

### 3. Widget Default Warnings

**Pattern:**
```python
st.number_input("Value")  # No value= parameter
```

**Issue:** These have sensible defaults (0.0 for number_input, "" for text_input).

**Recommendation:** Make this opt-in via `--check-widget-defaults` flag.

---

## Missing Detections

### 1. Division by Variable Without Recent Check

The scanner tracks division safety well, but misses some patterns:

```python
# NOT detected - denominator from dict access
ratio = total / data.get("count", 0)  # Can be 0!
```

**Fix:** Extend safe denominator tracking to detect `.get(..., 0)` patterns.

### 2. Async/Await Issues

No detection for common async anti-patterns:
- `await` inside synchronous functions
- Missing `await` on async calls

**Priority:** Low (Streamlit is mostly sync)

### 3. Streamlit Fragment Issues

Already covered by `check_fragment_violations.py` - good separation.

---

## Performance Analysis

| Operation | Time |
|-----------|------|
| Scan all pages | ~1.5s |
| Scan single page | ~0.2s |
| Build signature registry | ~0.3s |

**Verdict:** Performance is acceptable. No optimization needed.

---

## Recommended Future Improvements

### Phase 10: Severity Tuning (Optional)

**Changes:**
1. IndexError on unknown containers: MEDIUM → LOW
2. Type hint warnings: MEDIUM → LOW
3. Widget defaults: MEDIUM → LOW (or make opt-in)

### Ignore Config Enhancement

**Current:** `.scanner-ignore.yml` supports file/line ignores

**Add:** Pattern-based ignores
```yaml
false_positives:
  - file: 06_multi_format_import.py
    lines: [834-923]  # Range support
    reason: "Structurally guaranteed corners list"

  - pattern: "corners\\[\\d+\\]"
    reason: "8-element list from fixed loop"
```

---

## Implementation Plan

### ✅ Completed

1. **Phase 9 structural guarantee detection** - 2026-01-21
   - Fixed-iteration loop detection (list, tuple, range literals)
   - Nested loop multiplication (2×2×2 = 8)
   - `.append()` tracking within loops
   - 5 unit tests added (43 total tests now pass)
   - Eliminated ~150 false positives

2. **Updated `.scanner-ignore.yml`** - Reduced from ~42 lines to ~6 lines
   - Removed `corners[0-7]` entries (Phase 9 handles automatically)
   - Kept only tuple element access entries (`c[0]`, `edge[0]`, etc.)

3. **Fixed pre-existing test failures** - ValueError detection now works
   - Enhanced `_could_be_string_input()` to detect input-like variable names

### Future Improvements (Low Priority)

1. **Inline suppression** via comments: `# scanner: ignore`
2. **Per-file configuration** in docstrings or YAML frontmatter
3. **Auto-fix suggestions** for simple issues
4. **Phase 10 severity tuning** - Lower noise-level warnings

---

## Scripts Performance Research (RESOLVED)

### `safe_file_delete.py` - FIXED (170x speedup)

**Problem:** Took 9+ minutes to check references for a single file

**Root Cause:** Exhaustive Python file search with O(n²) string matching

**Solution:** Replaced with `git grep` subprocess call
- Before: 9+ minutes
- After: ~3 seconds
- **Improvement: 170x faster**

### `safe_file_move.py` - FIXED (Same approach)

Applied same `git grep` optimization for consistent performance.

---

## Next Steps

1. ~~**TASK-354:** Fix critical scanner issues~~ ✅ Complete
2. ~~**TASK-355:** Fix other page issues~~ ✅ Complete
3. ~~**Create `.scanner-ignore.yml`**~~ ✅ Complete and minimized
4. ~~**Update scanner with Phase 9**~~ ✅ Complete
5. ~~**Fix safe_file_delete.py performance**~~ ✅ Complete (170x faster)

### Remaining (Low Priority)
- Consider Phase 10 severity tuning if LOW issues become noisy
- Add inline suppression comments if needed for edge cases

---

## Related Documents

- [check_streamlit_issues.py](../../scripts/check_streamlit_issues.py) - Scanner implementation
- [TASKS.md](../TASKS.md) - Current task list
- [library-refactoring-strategy.md](library-refactoring-strategy.md) - Code quality strategy
