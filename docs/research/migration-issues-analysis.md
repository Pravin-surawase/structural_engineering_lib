# Migration Issues Analysis & Prevention System

> **Purpose:** Comprehensive analysis of Session 5 migration issues with automated prevention strategies
> **Created:** 2026-01-11 (Session 6)
> **Status:** Research Complete

---

## Executive Summary

Session 5 successfully migrated 7 IS 456 modules (~3,048 lines) but encountered several preventable issues. This document analyzes each issue, provides automated fixes, and creates a prevention system for future migrations.

**Key Findings:**
- 5 distinct issue categories identified
- 4 issues can be prevented with automation
- 1 new validation script needed
- 2 existing scripts need enhancement

---

## Issue Catalog

### Issue #1: Black Removes Empty Import Lines

**Symptom:**
```python
# Original (what we wrote):
from structural_lib.codes.is456.tables import (  # noqa: F401
    _PT_ROWS,
    _TC_COLUMNS,
    _get_tc_for_grade,
)

# After black (what happened):
# (empty - black removed because line was just a comment)
```

**Root Cause:** Black reformats files during pre-commit. If imports are on separate lines or comments are isolated, they may be removed or reordered.

**Impact:** Tests fail with `AttributeError: module has no attribute '_get_tc_for_grade'`

**Prevention Strategy:**
1. **Always group imports together** - Don't leave empty comment lines between import blocks
2. **Run black locally before commit** - Catch reformatting before it surprises you
3. **Validate stub exports after migration** - New script to verify private functions accessible

**Automation Fix:** Create `scripts/validate_stub_exports.py`

---

### Issue #2: Star Import Doesn't Include Private Functions

**Symptom:**
```python
from structural_lib.codes.is456.tables import *  # noqa: F401, F403
# _get_tc_for_grade is NOT included because it starts with _
```

**Root Cause:** Python's `from module import *` only imports names in `__all__` or names not starting with `_`.

**Impact:** Tests using private functions (like `tables._get_tc_for_grade`) fail.

**Prevention Strategy:**
1. **Scan source module for private functions** - Automation detects all `_` prefixed names
2. **Generate explicit imports automatically** - Script creates correct stub
3. **Validate after migration** - Verify all private functions are accessible

**Automation Fix:** Enhance `scripts/create_reexport_stub.py` to:
- Parse source module AST
- Extract all function/class names (including private)
- Generate explicit imports for private functions

---

### Issue #3: Data Types Need Re-export for Type Annotations

**Symptom:**
```python
# In api.py:
def check_deflection(...) -> serviceability.DeflectionResult:  # mypy error!

# mypy says: "DeflectionResult" is not a valid type
```

**Root Cause:** Type annotations like `serviceability.DeflectionResult` require the name to be a module attribute. Star imports don't guarantee this works for mypy.

**Impact:** mypy fails on type annotations referencing migrated module types.

**Prevention Strategy:**
1. **Identify data types used in type annotations** - Scan api.py for patterns
2. **Re-export data types explicitly in stubs** - From data_types module
3. **Validate mypy passes** - Run mypy before committing

**Automation Fix:** Create `scripts/scan_type_annotations.py`:
- Scan files for `module.TypeName` patterns
- Verify types are re-exported in stubs
- Suggest fixes

---

### Issue #4: Monkeypatch Doesn't Work on Stubs

**Symptom:**
```python
# Test does:
monkeypatch.setattr(flexure, "calculate_mu_lim", mock_fn)
# But flexure is now a stub that re-exports from codes.is456.flexure
# The actual function lives in codes.is456.flexure, not the stub!
```

**Root Cause:** `monkeypatch.setattr` modifies the stub's namespace, but the actual function reference in other modules points to the source location.

**Impact:** Mocked functions still use original implementation.

**Prevention Strategy:**
1. **Patch at source location** - `from structural_lib.codes.is456 import flexure as flexure_source`
2. **Document pattern in test guidelines** - Add to testing docs
3. **Detect monkeypatch patterns in tests** - Script to find and warn

**Automation Fix:** Create `scripts/check_monkeypatch_targets.py`:
- Scan test files for `monkeypatch.setattr` calls
- Check if target module is a stub
- Suggest patching at source location

---

### Issue #5: E402 Import Order Violations

**Symptom:**
```
ruff: E402: Module level import not at top of file
```

**Root Cause:** Logger initialization (`_logger = logging.getLogger(__name__)`) was placed before imports in migrated module.

**Impact:** Pre-commit blocks commit with ruff errors.

**Prevention Strategy:**
1. **Move all imports to top** - Before any code
2. **Run ruff locally before commit** - Catch issues early
3. **Validate migrated modules** - Check import order

**Automation Fix:** Already handled by ruff auto-fix. Just run:
```bash
.venv/bin/python -m ruff check --fix <file>
```

---

## Current Automation Scripts

### Migration Scripts (Session 5)

| Script | Purpose | Status |
|--------|---------|--------|
| `migrate_module.py` | One-command module migration | ✅ Works |
| `create_reexport_stub.py` | Generate backward compatibility stubs | ⚠️ Needs enhancement |
| `validate_migration.py` | Validate migration completeness | ✅ Works |
| `pre_migration_check.py` | Pre-flight verification | ✅ Works |

### File Operation Scripts (Session 4)

| Script | Purpose | Status |
|--------|---------|--------|
| `safe_file_move.py` | Move files with link updates | ✅ Works |
| `safe_file_delete.py` | Delete with reference check | ✅ Works |
| `check_folder_readmes.py` | Verify folder documentation | ✅ Works |
| `find_orphan_files.py` | Find unreferenced docs | ✅ Works |

### Validation Scripts

| Script | Purpose | Status |
|--------|---------|--------|
| `check_links.py` | Verify markdown links | ✅ Works |
| `fix_broken_links.py` | Auto-fix broken links | ✅ Works |

---

## New Scripts Needed

### 1. `validate_stub_exports.py` (HIGH PRIORITY)

**Purpose:** Verify stub modules correctly re-export all functions from source.

**Features:**
- Compare stub exports vs source exports
- Check private functions are explicitly imported
- Check data types are re-exported
- Report missing exports

**Usage:**
```bash
.venv/bin/python scripts/validate_stub_exports.py tables
.venv/bin/python scripts/validate_stub_exports.py --all
```

### 2. `scan_type_annotations.py` (MEDIUM PRIORITY)

**Purpose:** Find type annotations that reference migrated modules.

**Features:**
- Scan api.py and other files for `module.TypeName` patterns
- Check if TypeName is accessible in module
- Suggest data type re-exports

### 3. `check_monkeypatch_targets.py` (LOW PRIORITY)

**Purpose:** Find tests that monkeypatch stub modules.

**Features:**
- Parse test files for monkeypatch usage
- Check if target is a stub module
- Warn about potential issues

### 4. Enhanced `create_reexport_stub.py` (HIGH PRIORITY)

**Enhancements needed:**
- Auto-detect private functions to export
- Auto-detect data types used in type annotations
- Generate complete stub automatically

---

## Recommended Workflow Updates

### Pre-Commit Checklist

Before committing any migration:

```bash
# 1. Run black to catch formatting issues
.venv/bin/python -m black Python/structural_lib/<module>.py

# 2. Run ruff to catch import order issues
.venv/bin/python -m ruff check Python/structural_lib/codes/is456/<module>.py --fix

# 3. Validate stub exports
.venv/bin/python scripts/validate_stub_exports.py <module>

# 4. Run mypy to catch type issues
.venv/bin/python -m mypy Python/structural_lib/

# 5. Run tests
.venv/bin/python -m pytest Python/tests/ -x -q
```

### Post-Migration Checklist

After migrating a module:

1. ✅ Source code in `codes/is456/<module>.py` with `__all__`
2. ✅ Stub in `structural_lib/<module>.py` with re-exports
3. ✅ Private functions explicitly imported in stub
4. ✅ Data types re-exported if used in type annotations
5. ✅ `codes/is456/__init__.py` updated with module import
6. ✅ All tests passing
7. ✅ mypy passing

---

## Full Library Migration Plan

### Modules Already Migrated (Session 5)

| Module | Lines | Location |
|--------|-------|----------|
| tables.py | 83 | `codes/is456/tables.py` |
| shear.py | 178 | `codes/is456/shear.py` |
| flexure.py | 877 | `codes/is456/flexure.py` |
| detailing.py | 591 | `codes/is456/detailing.py` |
| serviceability.py | 751 | `codes/is456/serviceability.py` |
| compliance.py | 427 | `codes/is456/compliance.py` |
| ductile.py | 127 | `codes/is456/ductile.py` |

### Modules Remaining in Root

| Module | Lines | Migration Target | Notes |
|--------|-------|------------------|-------|
| `materials.py` | ~200 | `core/materials.py` | Code-agnostic, shared by all codes |
| `utilities.py` | ~150 | `core/utilities.py` | Code-agnostic helpers |
| `data_types.py` | ~400 | `core/data_types.py` | Already in correct location? |
| `constants.py` | ~50 | `core/constants.py` | Code-agnostic constants |
| `types.py` | ~100 | `core/types.py` | Type definitions |
| `api.py` | ~1600 | Keep in root | Entry point, orchestrates all |
| `bbs.py` | ~300 | Keep in root | Bar bending schedule |
| `rebar_optimizer.py` | ~500 | Keep in root | Optimization (code-agnostic) |
| `job_runner.py` | ~200 | Keep in root | Job execution |
| `dxf_export.py` | ~300 | Keep in root | Export functionality |
| `excel_integration.py` | ~200 | Keep in root | Excel bridge |

### Migration Priority

1. **TASK-317: Update codes/is456/__init__.py** (This session)
   - Add all migrated module exports
   - Update IS456Code class methods

2. **TASK-XXX: Core module organization** (Future)
   - Move materials.py → core/materials.py
   - Move utilities.py → core/utilities.py
   - Keep backward compatibility stubs

3. **No migration needed:**
   - api.py (entry point)
   - bbs.py, rebar_optimizer.py (code-agnostic)
   - job_runner.py, dxf_export.py, excel_integration.py (I/O layer)

---

## Automation Enhancement Plan

### Phase 1: Stub Validation (This Session)

1. Create `validate_stub_exports.py`
2. Enhance `create_reexport_stub.py` with auto-detection
3. Update migration workflow documentation

### Phase 2: __init__.py Automation (This Session)

1. Create `update_init_exports.py` script
2. Auto-detect migrated modules
3. Generate correct __init__.py exports

### Phase 3: Future Migration Prep (This Session)

1. Research remaining modules
2. Document migration order
3. Create automation for core/ migration

---

## Quick Reference

### When to Re-export Private Functions

A stub needs explicit private function imports when:
- Tests call `module._private_function()`
- Other modules import `from module import _private_function`

**Detection:** Search for `_` prefixed names in tests:
```bash
grep -r "tables\._" Python/tests/
grep -r "flexure\._" Python/tests/
```

### When to Re-export Data Types

A stub needs data type re-exports when:
- api.py uses `module.TypeName` in type annotations
- Other files use `module.TypeName` for type hints

**Detection:** Search for type annotation patterns:
```bash
grep -r "serviceability\.\w*Result" Python/structural_lib/
```

### When to Patch at Source

Tests should patch at source location when:
- The module being patched is a stub (re-export)
- The function is called from the original source

**Pattern:**
```python
# Instead of:
monkeypatch.setattr(flexure, "fn", mock)

# Use:
from structural_lib.codes.is456 import flexure as flexure_source
monkeypatch.setattr(flexure_source, "fn", mock)
```

---

## Conclusion

Session 5 migration was successful but revealed 5 issue categories. With the automation enhancements proposed in this document, future migrations will be:

1. **Faster** - Automation handles tedious checks
2. **Safer** - Validation catches issues before commit
3. **Consistent** - Same process for all modules

**Next Steps:**
1. Implement `validate_stub_exports.py`
2. Complete TASK-317 (update __init__.py)
3. Document lessons in copilot-instructions.md
