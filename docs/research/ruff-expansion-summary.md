# Ruff Configuration Expansion - TASK-189

**Date:** 2026-01-06
**Status:** Expanded ruff rules implemented, 17 auto-fixes applied

---

## Changes Made

### 1. Expanded Ruff Rules (pyproject.toml)

**Previous configuration:**
```toml
[tool.ruff.lint]
select = ["F"]  # Pyflakes only
```

**New configuration:**
```toml
[tool.ruff.lint]
select = [
  "F",   # Pyflakes (errors)
  "E",   # pycodestyle errors
  "W",   # pycodestyle warnings
  "I",   # isort (import sorting)
  "N",   # pep8-naming
  "UP",  # pyupgrade (Python version-specific improvements)
  "B",   # flake8-bugbear (common bugs and design problems)
  "C4",  # flake8-comprehensions (better list/dict/set comprehensions)
  "PIE", # flake8-pie (misc lints including unnecessary code)
]

ignore = [
  "E501",  # Line too long (handled by black)
  "B008",  # Do not perform function call in argument defaults
]
```

### 2. Current State Analysis

**Total issues found:** 490 (after 17 auto-fixes)

**Breakdown by category:**
- `UP006` (284 issues): Use `list` instead of `List` for type annotations (PEP 585)
- `UP045` (63 issues): Use `T | None` instead of `Optional[T]` (PEP 604)
- `UP035` (51 issues): Deprecated imports (e.g., `typing.List` → `list`)
- `N803` (35 issues): Invalid argument names (lowercase with underscores)
- `N806` (18 issues): Non-lowercase variables in functions
- `E402` (10 issues): Module import not at top of file
- Other (29 issues): Various minor issues

**High-traffic modules (api.py, report.py, dxf_export.py):**
- 119 issues total
- Mostly type annotation modernization (UP006, UP045)
- 11 naming convention issues (N803)

### 3. Docstring Style Guide Created

**Location:** `docs/contributing/docstring-style-guide.md`

**Key features:**
- Google Style format (Args, Returns, Raises, References, Examples)
- Units convention documented (mm, N/mm², kN·m)
- Module/function/class docstring templates
- Migration plan: High-traffic → Core → Complete coverage

---

## Remaining Work (Phased Approach)

### Phase 1: Type Annotation Modernization (v0.15 - Next Sprint)

**Task:** Upgrade type hints to PEP 585/604

```bash
# Enable unsafe fixes for type modernization
ruff check structural_lib/ --fix --unsafe-fixes --select UP006,UP045,UP035
```

**Impact:**
- 398 issues (UP006 + UP045 + UP035)
- Modernizes codebase to Python 3.9+ standards
- No functional changes, only syntax

**Risk:** Low (syntax only, covered by mypy + tests)

### Phase 2: Naming Conventions (v0.15)

**Task:** Fix pep8-naming issues

- `N803`: Rename function arguments (lowercase_with_underscores)
- `N806`: Rename variables in functions
- `N802`: Rename functions (if any are non-compliant)

**Impact:**
- 59 issues (N803 + N806 + N802)
- Improves code readability
- Potentially breaking if arguments are part of public API

**Risk:** Medium (requires careful review of public API impact)

### Phase 3: Docstring Enhancement (v1.0)

**Task:** Add complete docstrings to all public functions

**Priority modules:**
1. **api.py** - 20+ public functions (highest priority)
2. **report.py** - 10+ report generation functions
3. **dxf_export.py** - DXF export functions
4. **flexure.py** - Core calculation functions
5. **shear.py** - Core calculation functions

**Template** (from docstring-style-guide.md):
```python
def function_name(arg: type) -> return_type:
    """One-line summary.

    Extended description if needed.

    Args:
        arg: Description (units if applicable)

    Returns:
        Description of return value (units)

    Raises:
        ErrorType: When this occurs

    References:
        IS 456:2000, Cl. X.Y.Z

    Examples:
        >>> result = function_name(value)
        >>> print(result)
        123.45
    """
```

**Tools:**
```bash
# Check docstring coverage
pip install interrogate
interrogate -v structural_lib/

# Target: 100% coverage for public API functions in v1.0
```

---

## Summary

### Completed (TASK-189)
✅ Expanded ruff rules (9 rule categories vs 1)
✅ Created comprehensive docstring style guide
✅ Applied 17 auto-fixes
✅ Documented current state and migration plan

### Deferred to Future Sprints
⏭️ Type annotation modernization (398 issues) - v0.15
⏭️ Naming convention fixes (59 issues) - v0.15
⏭️ Complete docstring coverage - v1.0

### Why Phased Approach?

1. **Type modernization** (UP* rules) is safe but touches many files - better as dedicated sprint
2. **Naming conventions** (N* rules) requires API impact analysis - can't rush
3. **Docstring enhancement** is ongoing work - prioritize high-traffic modules first

**Result:** Codebase now has stricter linting, clear style guide, and actionable improvement plan.

---

## Next Steps

1. **Create tasks for future phases:**
   - TASK-XXX: Modernize type annotations (PEP 585/604)
   - TASK-XXX: Fix naming convention issues
   - TASK-XXX: Add docstrings to api.py (20 functions)
   - TASK-XXX: Add docstrings to flexure.py/shear.py

2. **Update pre-commit hooks** (future):
   - Add ruff docstring rules (D1**, D2**, D3**)
   - Add interrogate for docstring coverage
   - Gradually increase coverage requirement

3. **Monitor compliance:**
   - Run `ruff check --statistics` before each release
   - Track issue count reduction over time
   - Target: <100 issues for v1.0

---

**References:**
- [docs/contributing/docstring-style-guide.md](../contributing/docstring-style-guide.md)
- [docs/research/code-style-consistency.md](code-style-consistency.md)
- [Ruff Rules Documentation](https://docs.astral.sh/ruff/rules/)
