# Git Workflow Enhancement v2.0

**Date:** 2026-01-06
**Implemented by:** DEVOPS

## Summary

Enhanced the git workflow decision tool (`should_use_pr.sh`) with sophisticated size and complexity analysis. The workflow now follows a **PR-first philosophy** for substantial changes while reserving direct commits only for truly minor edits.

## Motivation

Previous workflow used file-type only (docs = direct commit). This missed substantial documentation changes that would benefit from review despite being low technical risk. User feedback: "why we did not use pr in the last step, it was major change?" (1500+ line automation catalog).

## Changes

### 1. Enhanced `should_use_pr.sh` with Change Metrics

**New metrics analyzed:**
- **File count** - Multiple files = higher impact
- **Lines changed** - Total additions + deletions
- **New files** - Creation vs editing
- **Renamed files** - Structural changes

**Thresholds defined:**
```bash
MINOR_LINES_THRESHOLD=50       # <50 lines = potentially minor
MINOR_FILES_THRESHOLD=2        # <2 files = potentially minor
SUBSTANTIAL_LINES=150          # ≥150 lines = substantial
MAJOR_LINES=500                # ≥500 lines = major
```

### 2. Sophisticated Decision Logic

**Production Code (NO CHANGE - Still ALWAYS PR):**
- Python/structural_lib/**/*.py
- VBA/**/*.bas, Excel/**/*.xlsm
- .github/workflows/**/*.yml
- pyproject.toml, requirements*.txt

**Documentation (NEW - Size-based):**
- **Major** (500+ lines): → PR required
- **Substantial** (150+ lines OR 3+ files): → PR required
- **Medium** (50-149 lines OR 2 files): → PR required
- **Minor** (<50 lines, 1 file, no new files): → Direct commit OK

**Tests (NEW - Size-based):**
- **Large** (≥50 lines OR 2+ files): → PR required
- **Minor** (<50 lines, 1 file): → Direct commit OK

**Scripts (NEW - Size-based):**
- **Large** (≥50 lines OR 2+ files): → PR required
- **Minor** (<50 lines, 1 file): → Direct commit OK

**Mixed docs + scripts (NEW - Size-based):**
- **Substantial** (≥50 lines OR 2+ files): → PR required
- **Minor** (<50 lines, 1 file): → Direct commit OK

### 3. Updated copilot-instructions.md

**Documented:**
- PR-first philosophy
- Size thresholds for all file types
- Examples of minor vs substantial changes
- Clear criteria (ALL must be true for direct commit)

## Examples

**❌ OLD: Would recommend direct commit**
- 1500-line automation catalog → docs/ → direct commit

**✅ NEW: Correctly recommends PR**
- 1500-line automation catalog → 1500 lines > 500 threshold → PR required

**✅ OLD & NEW: Typo fix is still direct commit**
- Fix typo in 1 doc file → 2 lines, 1 file → direct commit OK

**✅ NEW: Medium docs get PR**
- Update 3 doc files, 80 lines → 80 lines (medium) → PR required

## Validation

Tested with current changes (307 lines, 2 files):
```
Change metrics:
  Files changed: 2
  Lines changed: 307
  New files: 0

🔀 RECOMMENDATION: Pull Request
   (Substantial docs+scripts: 307 lines, 2 file(s))

Reasoning:
- Mixed docs + scripts changes
- Substantial scope (307 lines ≥50)
- Combined changes deserve review
```

## Impact

**More PRs (expected and desired):**
- Substantial docs changes now get review
- Large test suites get review
- Major script changes get review

**Faster iteration for truly minor changes:**
- Typo fixes still direct commit
- Small doc clarifications still direct commit
- Single-line test fixes still direct commit

**Better quality:**
- Substantial changes get CI validation
- Review catches completeness gaps, broken links
- Audit trail for major changes

## Backward Compatibility

**No breaking changes:**
- Production code workflow unchanged (still ALWAYS PR)
- safe_push.sh unchanged (still works as before)
- Stricter rules = safer (false positive = PR when could be direct commit)

## Files Changed

1. `scripts/should_use_pr.sh` - Rewritten with size analysis
2. `.github/copilot-instructions.md` - Updated workflow documentation
3. `scripts/should_use_pr_old.sh` - Backup of old version (for reference)

## Next Steps

1. Use this enhanced workflow going forward
2. Monitor false positives (if any) and adjust thresholds
3. Document learnings in TASKS.md or session log

## Decision

This commit uses the OLD workflow rules (being committed). Future commits will use NEW rules.
