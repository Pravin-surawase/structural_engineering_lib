# IS 456 Migration Pre-Flight Checklist

**Type:** Checklist
**Audience:** Developers
**Status:** Ready for Use
**Importance:** High
**Created:** 2026-01-10
**Last Updated:** 2026-01-13

---

**Purpose:** Complete checklist to run before starting IS 456 module migration

## Quick Start

```bash
# Run all pre-migration checks automatically
.venv/bin/.venv/bin/python scripts/pre_migration_check.py

# Or run individually
.venv/bin/python -m pytest Python/tests/ -v --tb=short    # All tests pass
.venv/bin/.venv/bin/python scripts/check_links.py                    # Doc links valid
gh run list -L 5                                           # CI is green
```

---

## ✅ Phase 1: Environment & Git

### 1.1 Clean Working Tree
```bash
git status
# Expected: "nothing to commit, working tree clean"
```
- [ ] No uncommitted changes
- [ ] No untracked files in Python/

### 1.2 Main Branch Sync
```bash
git fetch origin
git log --oneline HEAD..origin/main
# Expected: empty (up to date)
```
- [ ] Local main is up-to-date with origin

### 1.3 CI Status
```bash
gh run list -L 3
# Expected: All recent runs ✓ completed
```
- [ ] Last CI run passed on main
- [ ] No failing workflows

### 1.4 Create Feature Branch
```bash
git checkout -b feat/migrate-is456-modules
```
- [ ] Feature branch created (provides rollback safety)

---

## ✅ Phase 2: Test Suite Baseline

### 2.1 All Tests Pass
```bash
.venv/bin/python -m pytest Python/tests/ -v --tb=short 2>&1 | tail -20
```
- [ ] All tests pass (expected: 2300+)
- [ ] No skipped tests unexpectedly

### 2.2 Core Module Tests
```bash
.venv/bin/python -m pytest Python/tests/test_core.py -v
```
- [ ] 24 core tests pass (CodeRegistry, MaterialFactory, geometry)

### 2.3 IS 456 Module Tests
```bash
# Run tests for modules being migrated
.venv/bin/python -m pytest Python/tests/test_flexure*.py Python/tests/test_shear*.py Python/tests/test_detailing*.py -v
```
- [ ] Flexure tests pass
- [ ] Shear tests pass
- [ ] Detailing tests pass

### 2.4 Test Count Snapshot
```bash
.venv/bin/python -m pytest Python/tests/ --collect-only -q | tail -5
```
- [ ] Record test count: _____ tests
- [ ] This count should not change after migration

---

## ✅ Phase 3: Import Validation

### 3.1 Current Import Paths Work
```bash
.venv/bin/python -c "
from structural_lib import flexure, shear, detailing, tables
from structural_lib.flexure import design_singly_reinforced
from structural_lib.shear import design_shear
print('✅ All current imports work')
"
```
- [ ] All current import paths work

### 3.2 Codes Namespace Exists
```bash
.venv/bin/python -c "
from structural_lib.codes.is456 import IS456Code
from structural_lib.core import CodeRegistry
print(f'IS456 registered: {CodeRegistry.is_registered(\"IS456\")}')
"
```
- [ ] IS456Code class exists
- [ ] CodeRegistry has IS456 registered

### 3.3 Core Module Ready
```bash
.venv/bin/python -c "
from structural_lib.core import (
    CodeRegistry,
    MaterialFactory,
    RectangularSection,
    DesignCode,
)
print('✅ Core module ready')
"
```
- [ ] Core module exports all base classes

---

## ✅ Phase 4: Documentation Links

### 4.1 Link Check
```bash
.venv/bin/.venv/bin/python scripts/check_links.py
```
- [ ] 0 broken links (expected: 719+ links, 0 broken)

### 4.2 Docs Index Valid
```bash
.venv/bin/.venv/bin/python scripts/check_docs_index.py
```
- [ ] Docs index is valid

---

## ✅ Phase 5: Automation Ready

### 5.1 Migration Scripts Exist
```bash
ls scripts/migrate_module.py scripts/create_reexport_stub.py scripts/validate_migration.py 2>/dev/null
```
- [ ] `migrate_module.py` exists
- [ ] `create_reexport_stub.py` exists
- [ ] `validate_migration.py` exists

### 5.2 Safe File Scripts Ready
```bash
ls scripts/safe_file_move.py scripts/safe_file_delete.py 2>/dev/null
```
- [ ] Safe file operations available (for rollback if needed)

---

## ✅ Phase 6: Dependency Mapping

### 6.1 Module Dependencies Documented
Verify these dependencies before migration:

| Module | Depends On | Depended By |
|--------|------------|-------------|
| `tables.py` | utilities | shear |
| `shear.py` | tables, data_types, errors | compliance |
| `flexure.py` | materials, data_types, errors, validation | compliance, optimization |
| `detailing.py` | error_messages, errors | bbs, dxf_export, excel_integration |
| `compliance.py` | flexure, shear, serviceability | job_runner |
| `serviceability.py` | data_types | compliance |
| `ductile.py` | errors, utilities | report |

- [ ] Dependencies verified and unchanged

### 6.2 No Circular Import Risk
```bash
# Check for potential circular imports
grep -r "from structural_lib.compliance import" Python/structural_lib/flexure.py
grep -r "from structural_lib.flexure import" Python/structural_lib/compliance.py
# Expected: compliance imports flexure, NOT vice versa
```
- [ ] No circular dependencies detected

---

## ✅ Phase 7: API Surface Check

### 7.1 Public API Functions
```bash
.venv/bin/python -c "
from structural_lib import api
funcs = [x for x in dir(api) if not x.startswith('_')]
print(f'API functions: {len(funcs)}')
"
```
- [ ] Record API function count: _____
- [ ] Should not change after migration

### 7.2 API Still Works
```bash
.venv/bin/python -c "
from structural_lib.api import design_beam_is456
print(f'design_beam_is456: {design_beam_is456.__name__}')
"
```
- [ ] Main API function accessible

---

## 🚨 Stop Conditions

**DO NOT proceed if any of these are true:**

- ❌ Tests failing (fix first)
- ❌ CI is red (wait for green)
- ❌ Broken doc links (fix first)
- ❌ Uncommitted changes (commit or stash)
- ❌ Migration scripts don't exist (create first)

---

## 📋 Summary Checklist

Copy this to your migration session:

```
PRE-MIGRATION CHECKLIST
========================
[ ] Git: Clean working tree
[ ] Git: Up-to-date with origin/main
[ ] Git: Feature branch created
[ ] Tests: All 2300+ tests pass
[ ] Tests: Core module tests pass
[ ] Tests: IS 456 module tests pass
[ ] Imports: Current paths work
[ ] Imports: codes/is456 namespace ready
[ ] Imports: Core module ready
[ ] Docs: 0 broken links
[ ] Scripts: Migration automation exists
[ ] Deps: No circular imports
[ ] API: Function count stable

All checks passed: [ ] YES → Proceed with migration
```

---

## After Migration Completion

Run this checklist after completing all migrations:

- [ ] All modules in `codes/is456/`
- [ ] All re-export stubs created
- [ ] All tests still pass (same count)
- [ ] Old import paths still work
- [ ] New import paths work
- [ ] API unchanged
- [ ] CI is green
- [ ] Documentation updated

---

*Checklist created: 2026-01-10 Session 5*
