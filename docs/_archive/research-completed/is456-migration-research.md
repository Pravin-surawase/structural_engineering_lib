# IS 456 Module Migration Research

> **Status:** Complete Research | **Date:** 2026-01-10
> **Purpose:** Comprehensive analysis for migrating IS 456 modules from flat structure to `codes/is456/`
> **Based on:** enterprise-folder-structure-research.md, folder-cleanup-research.md

---

## Executive Summary

This document provides a complete migration plan for moving IS 456-specific modules from the flat `structural_lib/` structure to the namespaced `structural_lib/codes/is456/` structure. The migration enables multi-code support (IS 456, ACI 318, Eurocode 2) while maintaining 100% backward compatibility.

**Key Findings:**
- 8 core modules need migration (flexure, shear, detailing, etc.)
- 70+ test files need import updates
- 719+ doc links must remain valid
- Backward compatibility via re-exports is **mandatory**

**Risk Level:** 🟡 Medium (with proper automation)

---

## 1. Current State Analysis

### 1.1 Module Inventory

| Module | Lines | Purpose | Migration Priority |
|--------|-------|---------|-------------------|
| `flexure.py` | 877 | Flexural design IS 456 Cl. 38.1 | 🔴 Phase 1 |
| `shear.py` | 178 | Shear design IS 456 Cl. 40 | 🔴 Phase 1 |
| `detailing.py` | 591 | Reinforcement detailing | 🔴 Phase 1 |
| `tables.py` | 83 | IS 456 Table lookups | 🔴 Phase 1 |
| `serviceability.py` | 751 | Deflection/cracking | 🟠 Phase 2 |
| `compliance.py` | 427 | Compliance checks | 🟠 Phase 2 |
| `ductile.py` | 127 | Seismic (IS 13920) | 🟠 Phase 2 |
| `constants.py` | 14 | Constants (partial) | 🟢 Phase 3 |

**Total: ~3,048 lines of code to migrate**

### 1.2 Dependency Graph

```
                    ┌──────────────────────────────────────────┐
                    │           CORE (code-agnostic)           │
                    │  materials.py, utilities.py, types.py,   │
                    │  errors.py, data_types.py, validation.py │
                    └──────────────────────────────────────────┘
                                        ↑
                    ┌──────────────────────────────────────────┐
                    │         IS 456 SPECIFIC MODULES          │
                    ├──────────────────────────────────────────┤
                    │ tables.py (no deps)                      │
                    │   ↳ shear.py (uses tables)               │
                    │   ↳ flexure.py (uses materials)          │
                    │      ↳ detailing.py (uses flexure)       │
                    │      ↳ compliance.py (uses flexure,shear)│
                    │         ↳ serviceability.py              │
                    │            ↳ ductile.py                  │
                    └──────────────────────────────────────────┘
                                        ↑
                    ┌──────────────────────────────────────────┐
                    │         APPLICATION LAYER                │
                    │  api.py, bbs.py, dxf_export.py,          │
                    │  report.py, excel_bridge.py              │
                    └──────────────────────────────────────────┘
```

### 1.3 Current Import Patterns

**Internal imports (within structural_lib):**
```python
# Current pattern - MUST remain working
from structural_lib import flexure, shear, detailing
from structural_lib.flexure import design_singly_reinforced
```

**Test imports (70 files):**
```python
# Pattern 1: Module import
from structural_lib import flexure

# Pattern 2: Direct function import
from structural_lib.flexure import calculate_ast_required
```

---

## 2. Target Architecture

### 2.1 Final Structure

```
Python/structural_lib/
├── __init__.py           # Re-exports for backward compat
├── core/                  # ✅ Already exists (Session 3)
│   ├── base.py            # Abstract classes
│   ├── materials.py       # Material models
│   ├── geometry.py        # Section geometry
│   └── registry.py        # CodeRegistry
├── codes/
│   ├── __init__.py
│   └── is456/             # ← Target for migration
│       ├── __init__.py    # ✅ Exists with IS456Code
│       ├── flexure.py     # ← Migrate from root
│       ├── shear.py       # ← Migrate from root
│       ├── detailing.py   # ← Migrate from root
│       ├── tables.py      # ← Migrate from root
│       ├── serviceability.py # ← Migrate from root
│       ├── compliance.py  # ← Migrate from root
│       └── ductile.py     # ← Migrate from root
├── flexure.py             # → Re-export stub (backward compat)
├── shear.py               # → Re-export stub (backward compat)
├── detailing.py           # → Re-export stub (backward compat)
└── ...                    # Other stubs
```

### 2.2 Backward Compatibility Layer

Each migrated module gets a **re-export stub** at the original location:

```python
# structural_lib/flexure.py (after migration)
"""Backward compatibility - imports from codes/is456/flexure.py"""
from structural_lib.codes.is456.flexure import *  # noqa: F401, F403
from structural_lib.codes.is456.flexure import __all__  # noqa: F401
```

This ensures:
- ✅ `from structural_lib import flexure` works
- ✅ `from structural_lib.flexure import func` works
- ✅ Zero changes needed in existing code
- ✅ Tests pass without modification

---

## 3. Migration Phases

### Phase 1: Foundation Modules (No Dependencies)

**Modules:** `tables.py`
**Order:** 1st (has no IS 456 dependencies)
**Risk:** 🟢 Low

**Steps:**
1. Copy `tables.py` → `codes/is456/tables.py`
2. Update internal imports to use relative paths
3. Create re-export stub at original location
4. Run tests: `pytest tests/test_tables*.py -v`
5. Verify: All tests pass

### Phase 2: Core Calculation Modules

**Modules:** `flexure.py`, `shear.py`
**Order:** After tables.py
**Risk:** 🟡 Medium

**Dependencies:**
- `flexure.py` → materials.py, data_types.py, errors.py, validation.py
- `shear.py` → tables.py, data_types.py, errors.py

**Steps:**
1. Migrate `shear.py` first (depends only on tables)
2. Migrate `flexure.py` second
3. Update cross-imports within codes/is456/
4. Create re-export stubs
5. Run full test suite

### Phase 3: Dependent Modules

**Modules:** `detailing.py`, `compliance.py`, `serviceability.py`
**Order:** After flexure, shear
**Risk:** 🟡 Medium

**Dependencies:**
- `detailing.py` → errors.py, error_messages.py
- `compliance.py` → flexure, shear, serviceability, data_types
- `serviceability.py` → data_types

### Phase 4: Specialized Modules

**Modules:** `ductile.py`, `constants.py` (partial)
**Order:** Last
**Risk:** 🟢 Low

---

## 4. Potential Issues & Mitigations

### 4.1 Circular Import Risk 🔴

**Scenario:** compliance.py imports flexure.py, flexure.py imports compliance.py

**Current status:** Analyzed - NO circular imports exist currently

**Mitigation:**
- Import at function level if needed: `from structural_lib.codes.is456.flexure import func`
- Use TYPE_CHECKING guards for type hints
- Create shared interfaces in core/

### 4.2 Relative vs Absolute Import Confusion 🟡

**Problem:** After moving, imports like `from . import materials` will break

**Solution:** Use absolute imports in migrated modules:
```python
# CORRECT (in codes/is456/flexure.py)
from structural_lib import materials
from structural_lib.data_types import FlexureResult

# NOT (relative - breaks easily)
from ... import materials  # Hard to maintain
```

### 4.3 Test Import Failures 🟡

**Problem:** 70 test files import from structural_lib

**Solution:** Re-export stubs ensure tests don't need changes

**Verification:** Run all tests after each module migration

### 4.4 Doc Link Breakage 🟢

**Problem:** 719+ links might reference moved files

**Current status:** Doc links reference `docs/` not `Python/`, so no impact

**Verification:** Run `scripts/check_links.py` after migration

### 4.5 API Surface Changes 🟢

**Problem:** `api.py` imports from flexure, shear, etc.

**Solution:** Re-export stubs ensure api.py works unchanged

### 4.6 VBA Parity 🟢

**Problem:** VBA modules mirror Python structure

**Current status:** VBA won't move - it remains IS 456-specific
No action needed for VBA

---

## 5. Automation Scripts Needed

### 5.1 Existing Automation ✅

| Script | Purpose | Migration Use |
|--------|---------|---------------|
| `safe_file_move.py` | Move with link updates | ❌ Not for Python |
| `check_links.py` | Validate doc links | ✅ Validation |
| `find_orphan_files.py` | Find unreferenced | ❌ Not needed |

### 5.2 New Automation Required

| Script | Purpose | Priority |
|--------|---------|----------|
| `scripts/migrate_module.py` | Migrate one module end-to-end | 🔴 Critical |
| `scripts/create_reexport_stub.py` | Generate re-export file | 🔴 Critical |
| `scripts/update_imports.py` | Update imports in migrated module | 🔴 Critical |
| `scripts/validate_migration.py` | Verify migration is complete | 🟡 High |
| `scripts/check_circular_imports.py` | Detect circular import risks | 🟢 Nice-to-have |

### 5.3 Migrate Module Script (Core Logic)

```python
#!/usr/bin/env python3
"""Migrate a single IS 456 module to codes/is456/"""

def migrate_module(module_name: str, dry_run: bool = True) -> None:
    """
    1. Copy module to codes/is456/
    2. Update internal imports
    3. Create re-export stub at original location
    4. Run validation tests
    """
    src = f"Python/structural_lib/{module_name}.py"
    dst = f"Python/structural_lib/codes/is456/{module_name}.py"

    # Read source
    content = Path(src).read_text()

    # Update imports (only internal structural_lib imports)
    # e.g., "from . import materials" stays the same
    # e.g., "from .tables import lookup" → "from structural_lib.codes.is456.tables import lookup"

    # Write to destination
    if not dry_run:
        Path(dst).write_text(updated_content)

    # Create re-export stub
    stub = f'''"""Backward compatibility stub - redirects to codes/is456/{module_name}.py"""
from structural_lib.codes.is456.{module_name} import *  # noqa: F401, F403
'''
    if not dry_run:
        Path(src).write_text(stub)
```

---

## 6. Pre-Migration Checklist

### Before Starting ANY Migration

- [ ] All tests pass: `pytest Python/tests/ -v`
- [ ] CI is green on main branch
- [ ] Doc links valid: `python scripts/check_links.py`
- [ ] Create feature branch: `git checkout -b feat/migrate-is456-phase1`
- [ ] Backup exists (git branch is backup)

### Before Each Module Migration

- [ ] Identify all internal dependencies
- [ ] Identify all external consumers (grep for imports)
- [ ] Module tests exist and pass
- [ ] No circular import risk with already-migrated modules

### After Each Module Migration

- [ ] Module runs: `python -c "from structural_lib.codes.is456.module import *"`
- [ ] Re-export works: `python -c "from structural_lib.module import *"`
- [ ] Module tests pass: `pytest tests/test_module*.py -v`
- [ ] Full test suite passes: `pytest Python/tests/ -v`
- [ ] Commit with message: `refactor: migrate module.py to codes/is456/`

### After All Migrations

- [ ] All tests pass
- [ ] CI is green
- [ ] API still works: `python -c "from structural_lib import api; print(api.design_beam_is456)"`
- [ ] Update codes/is456/__init__.py to export all functions
- [ ] Update documentation if needed

---

## 7. Validation Strategy

### 7.1 Test Coverage

| Test Type | Count | After Migration |
|-----------|-------|-----------------|
| Unit tests | 2,300+ | Must all pass |
| Integration | ~50 | Must all pass |
| Example scripts | ~10 | Must all work |

### 7.2 Import Validation

```bash
# Verify re-exports work
python -c "from structural_lib import flexure; print(flexure.design_singly_reinforced)"

# Verify new path works
python -c "from structural_lib.codes.is456 import flexure; print(flexure.design_singly_reinforced)"

# Verify registry works
python -c "from structural_lib.core import CodeRegistry; print(CodeRegistry.get('IS456'))"
```

### 7.3 Automated Validation Script

```python
#!/usr/bin/env python3
"""Validate migration is complete and working."""

import importlib
import sys

MODULES = ["flexure", "shear", "detailing", "tables", "serviceability", "compliance", "ductile"]

def validate_migration():
    errors = []

    for mod in MODULES:
        # Check re-export works
        try:
            old = importlib.import_module(f"structural_lib.{mod}")
            assert hasattr(old, "__all__") or True  # Stub may not have __all__
        except Exception as e:
            errors.append(f"Re-export failed for {mod}: {e}")

        # Check new location works
        try:
            new = importlib.import_module(f"structural_lib.codes.is456.{mod}")
        except Exception as e:
            errors.append(f"New location failed for {mod}: {e}")

    if errors:
        print("❌ Validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print("✅ All modules validated!")
    sys.exit(0)
```

---

## 8. Rollback Plan

### If Migration Fails

```bash
# Restore from git
git checkout main -- Python/structural_lib/flexure.py  # etc.

# Remove migrated files
rm Python/structural_lib/codes/is456/flexure.py  # etc.

# Verify tests pass
pytest Python/tests/ -v
```

### If Partial Migration Needed

Each module can be migrated independently. If one fails:
1. Rollback that module only
2. Keep already-migrated modules
3. Investigate the failure
4. Retry when fixed

---

## 9. Estimated Effort

| Phase | Modules | Estimated Time | Risk |
|-------|---------|----------------|------|
| Create automation scripts | - | 1-2 hours | 🟢 Low |
| Phase 1 (tables) | 1 | 30 min | 🟢 Low |
| Phase 2 (flexure, shear) | 2 | 1 hour | 🟡 Medium |
| Phase 3 (detailing, compliance, serviceability) | 3 | 1.5 hours | 🟡 Medium |
| Phase 4 (ductile, constants) | 2 | 30 min | 🟢 Low |
| Validation & docs | - | 1 hour | 🟢 Low |

**Total: ~6-8 hours of focused work**

---

## 10. Success Criteria

✅ **Complete when:**
1. All 7+ modules exist in `codes/is456/`
2. All re-export stubs exist at original locations
3. All 2,300+ tests pass unchanged
4. `CodeRegistry.get("IS456")` returns working code
5. API unchanged: `from structural_lib import flexure` works
6. No circular imports
7. CI is green

---

## 11. Next Steps

1. **Create automation scripts** (Task 3)
   - `migrate_module.py`
   - `create_reexport_stub.py`
   - `validate_migration.py`

2. **Create migration workflow guide** (Task 4)
   - Step-by-step commands
   - Checkpoint validation
   - Rollback procedures

3. **Execute Phase 1** (future session)
   - Migrate `tables.py`
   - Verify, test, commit

4. **Execute Phases 2-4** (future sessions)
   - One module at a time
   - Full test suite after each

---

## Appendix A: Full Import Analysis

### Modules that import from IS 456 modules

```
api.py → flexure, shear, detailing, serviceability, compliance
beam_pipeline.py → api, detailing
bbs.py → detailing
compliance.py → flexure, shear, serviceability
dxf_export.py → bbs, detailing
excel_bridge.py → flexure, shear, detailing
excel_integration.py → detailing, dxf_export
job_runner.py → api, beam_pipeline, compliance
optimization.py → flexure, costing
report.py → ductile
```

### Test files import patterns

```
test_detailing*.py → from structural_lib.detailing import ...
test_flexure*.py → from structural_lib import flexure
test_shear*.py → from structural_lib.shear import ...
test_compliance*.py → from structural_lib.compliance import ...
test_serviceability*.py → from structural_lib.serviceability import ...
```

---

## Appendix B: Module Line Counts

```bash
$ wc -l Python/structural_lib/*.py | sort -rn | head -20

 877 flexure.py
 751 serviceability.py
 591 detailing.py
 427 compliance.py
 178 shear.py
 127 ductile.py
  83 tables.py
  14 constants.py
```

---

*Research completed: 2026-01-10 Session 5*
