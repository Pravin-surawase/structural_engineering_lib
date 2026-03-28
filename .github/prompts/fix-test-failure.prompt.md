---
description: "Fix test failure workflow — reproduce, diagnose, fix, verify"
---

# Fix Test Failure Workflow

## 1. Identify the Failing Test

```bash
# Run the specific failing test with verbose output
.venv/bin/pytest Python/tests/ -v -k "{{test_name}}" --tb=long

# Or run the full suite to see all failures
.venv/bin/pytest Python/tests/ -v --tb=short
```

## 2. Understand What Changed

```bash
# What was recently modified?
git --no-pager log --oneline -10
git --no-pager diff HEAD~3 --stat

# Check if the test itself changed or the source code
git --no-pager log --oneline -5 -- Python/tests/
git --no-pager log --oneline -5 -- Python/structural_lib/
```

## 3. Diagnose the Failure

| Failure Type | Likely Cause | Check |
|-------------|-------------|-------|
| `AssertionError` (value mismatch) | Formula changed, units wrong | Compare expected vs actual values |
| `ImportError` | Module moved, circular import | `scripts/validate_imports.py` |
| `TypeError` (wrong args) | API signature changed | `scripts/discover_api_signatures.py <func>` |
| `KeyError` | Dict structure changed | Check Pydantic model or return dict |
| `AttributeError` | Class/method renamed | Search for the old name in codebase |

## 4. Fix Strategy

### If the test is correct and code is wrong:
- Fix the source code to produce expected results
- Verify with: `.venv/bin/pytest Python/tests/ -v -k "{{test_name}}"`

### If the code is correct and test is outdated:
- Update the test expectations with justification comment
- Cite IS 456 clause if structural calculation changed
- Run full suite to ensure no regressions: `.venv/bin/pytest Python/tests/ -v`

### If it's a regression from a recent change:
- Check the commit that introduced the change: `git --no-pager log --oneline -10`
- Fix the regression, don't just update the test

## 5. Verify Fix

```bash
# Run the specific test
.venv/bin/pytest Python/tests/ -v -k "{{test_name}}"

# Run the full suite (check for regressions)
.venv/bin/pytest Python/tests/ -v

# If frontend tests:
cd react_app && npx vitest run
```

## 6. Commit

```bash
./scripts/ai_commit.sh "fix: resolve {{test_name}} failure — [brief cause]"
```
