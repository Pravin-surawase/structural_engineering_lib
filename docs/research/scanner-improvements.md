# Scanner Improvements Research

**Type:** Research
**Audience:** Developers
**Status:** Active
**Importance:** High
**Created:** 2026-01-20
**Last Updated:** 2026-01-20
**Related Tasks:** TASK-354, TASK-355

---

## Executive Summary

The `check_streamlit_issues.py` scanner (2075 lines) is a sophisticated AST-based static analyzer with **8 enhancement phases**. This research identifies **false positives**, **missing detections**, and **improvement opportunities**.

**Key Findings:**
- **~150 false positives** in `06_multi_format_import.py` from IndexError checks on structurally guaranteed lists
- Scanner misses some common safe patterns (fixed-size loops, structural guarantees)
- Performance is good (~1-2s for all pages)
- Some MEDIUM severity issues are noise (type hints, widget defaults)

---

## Current Scanner Capabilities

### Detections (8 Phases)

| Phase | Feature | Status |
|-------|---------|--------|
| 1 | NameError - undefined variables | ✅ Working |
| 2 | Import inside functions | ✅ Working |
| 3 | Guard clause / API signature | ✅ Working |
| 4 | Path division detection | ✅ Working |
| 5 | Widget default validation | ✅ Working (noisy) |
| 6 | Session state safe methods | ✅ Working |
| 7 | Widget key conflicts | ✅ Working |
| 8 | ZeroDivisionError detection | ✅ Working |

### Severity Levels

| Level | Meaning | Current Count |
|-------|---------|---------------|
| CRITICAL | Will crash at runtime | 0 in pages |
| HIGH | Likely to crash | 4 (imports inside functions) |
| MEDIUM | Potential issues | ~160 (mostly false positives) |
| LOW | Style/best practice | Few |

---

## False Positive Analysis

### 1. IndexError on Structurally Guaranteed Lists (~150 issues)

**Location:** `06_multi_format_import.py` lines 834-923

**Pattern:**
```python
# Scanner flags corners[0] through corners[7] as IndexError risks
# But corners is ALWAYS built with exactly 8 elements:
corners = []
for end_pt in [beam.point1, beam.point2]:  # Always 2 iterations
    for w_sign in [-1, 1]:                  # Always 2 iterations
        for d_sign in [-1, 1]:              # Always 2 iterations
            corners.append((cx, cy, cz))    # 2 × 2 × 2 = 8 elements

# Later accesses corners[0] through corners[7] - ALWAYS safe
x_mesh = [c[0] for c in corners]
```

**Why False Positive:** The scanner doesn't track that:
1. Loop constructs produce fixed-size outputs
2. List literal lengths are known at compile time
3. `len(corners) == 8` is structurally guaranteed

**Fix Options:**
1. **Pattern recognition:** Detect fixed-iteration loops
2. **Ignore config:** Add to `.scanner-ignore.yml` for this file
3. **Inline suppression:** `# noqa: scanner-indexerror`
4. **Severity adjustment:** Lower IndexError to LOW for unknown lists

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

## Recommended Improvements

### Phase 9: Structural Guarantee Detection

**Priority:** HIGH - Eliminates ~150 false positives

**Implementation:**
```python
def _is_structurally_guaranteed_length(self, container: str, min_length: int) -> bool:
    """Check if container has guaranteed minimum length.

    Detects:
    1. Fixed-iteration loops (for x in [a, b, c]: list.append())
    2. List literals with known length
    3. zip()/enumerate() over known-length iterables
    4. Comment hints like '# always 8 elements'
    """
    # Check if container was built in a tracked fixed-size loop
    if container in self.fixed_size_containers:
        return self.fixed_size_containers[container] >= min_length
    return False
```

### Phase 10: Severity Tuning

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

### Quick Wins (1-2 hours)

1. **Add lines to `.scanner-ignore.yml`** for `06_multi_format_import.py` corners
2. **Adjust severity levels** for type hints and widget defaults
3. **Add `--strict` flag** to show all issues (current default becomes relaxed)

### Medium Term (3-4 hours)

1. **Implement Phase 9** structural guarantee detection
2. **Add range support** to ignore config
3. **Improve denominator tracking** for `.get(..., 0)` patterns

### Long Term

1. **Inline suppression** via comments: `# scanner: ignore`
2. **Per-file configuration** in docstrings or YAML frontmatter
3. **Auto-fix suggestions** for simple issues

---

## Scripts Performance Research

### `safe_file_delete.py` - CRITICAL ISSUE

**Problem:** Takes 9+ minutes to check references for a single file (blocks/hangs)

**Root Cause:** `find_references()` function does exhaustive file search:
```python
for search_dir in search_dirs:  # 6 directories
    for ext in extensions:      # 7 extensions
        for file in search_path.rglob(f"*{ext}"):  # Recursive
            for pattern in patterns:  # 4 patterns
                if pattern in line:   # O(n) string search
```

**Fix Options:**
1. **Use grep/ripgrep:** Shell out to `rg` for fast search
2. **Cache file index:** Build once, query many times
3. **Parallel processing:** Use `concurrent.futures`
4. **Limit search depth:** Add `--max-depth` option

### Other Slow Scripts (To Investigate)

1. `safe_file_move.py` - Likely same issue
2. `check_links.py` - May have similar exhaustive search
3. `find_orphan_files.py` - File enumeration overhead

---

## Next Steps

1. **TASK-354:** Fix critical scanner issues in ai_workspace.py (separate file, not pages)
2. **TASK-355:** Fix other page issues (5 HIGH severity import issues)
3. **Create `.scanner-ignore.yml`** with false positive exclusions
4. **Update scanner** with Phase 9 improvements
5. **Fix safe_file_delete.py** performance issue

---

## Related Documents

- [check_streamlit_issues.py](../../scripts/check_streamlit_issues.py) - Scanner implementation
- [TASKS.md](../TASKS.md) - Current task list
- [library-refactoring-strategy.md](library-refactoring-strategy.md) - Code quality strategy
