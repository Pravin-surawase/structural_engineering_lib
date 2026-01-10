# IS 456 Module Migration Workflow

> **Status:** Ready for Use | **Date:** 2026-01-10
> **Purpose:** Step-by-step guide for executing the IS 456 module migration

---

## Quick Reference

```bash
# Pre-flight check (run first!)
.venv/bin/python scripts/pre_migration_check.py

# Migrate a single module
.venv/bin/python scripts/migrate_module.py tables --dry-run
.venv/bin/python scripts/migrate_module.py tables

# Check migration status
.venv/bin/python scripts/migrate_module.py --list

# Validate after migration
.venv/bin/python scripts/validate_migration.py --verbose
```

---

## Overview

### What We're Doing

Moving IS 456-specific modules from:
```
structural_lib/flexure.py      (current)
```

To:
```
structural_lib/codes/is456/flexure.py  (new location)
structural_lib/flexure.py              (re-export stub)
```

### Why

- Enable multi-code support (IS 456, ACI 318, Eurocode 2)
- Clean architecture with code-agnostic core
- Backward compatible - existing code continues to work

### Migration Order

**MUST migrate in this order** (respects dependencies):

| Order | Module | Dependencies | Estimated Time |
|-------|--------|--------------|----------------|
| 1 | `tables.py` | None | 15 min |
| 2 | `shear.py` | tables | 20 min |
| 3 | `flexure.py` | materials | 30 min |
| 4 | `detailing.py` | errors | 20 min |
| 5 | `serviceability.py` | data_types | 25 min |
| 6 | `compliance.py` | flexure, shear, serviceability | 25 min |
| 7 | `ductile.py` | errors | 15 min |

---

## Phase 0: Pre-Migration Setup (Once per session)

### Step 0.1: Initialize Session
```bash
.venv/bin/python scripts/start_session.py --quick
```

### Step 0.2: Run Pre-Flight Checks
```bash
.venv/bin/python scripts/pre_migration_check.py
```

**Expected output:**
```
✅ Git Clean: Working tree clean
✅ Git Synced: Up to date with origin/main
✅ Tests Pass: 2300 passed in 45s
✅ Current Imports: All current imports work
✅ Codes Namespace: IS456Code exists and registered
✅ Core Module: Core module exports all base classes
✅ Doc Links: No broken links
✅ Migration Scripts: All migration scripts exist
✅ No Circular Imports: No circular imports detected

✅ ALL CHECKS PASSED (9/9)
```

**If any check fails:** Fix before proceeding.

### Step 0.3: Create Feature Branch
```bash
git checkout -b feat/migrate-is456-modules
```

**Important:** This provides rollback safety.

---

## Phase 1: Migrate tables.py (First Module)

### Step 1.1: Preview Migration
```bash
.venv/bin/python scripts/migrate_module.py tables --dry-run
```

**Review:**
- Import changes shown
- Stub content shown
- No unexpected changes

### Step 1.2: Execute Migration
```bash
.venv/bin/python scripts/migrate_module.py tables
```

**Expected:**
```
✅ Migrated: structural_lib/tables.py -> structural_lib/codes/is456/tables.py
✅ Created stub: structural_lib/tables.py
✅ tables validation passed
```

### Step 1.3: Run Module Tests
```bash
.venv/bin/python -m pytest Python/tests/test_tables*.py Python/tests/test_shear*.py -v
```

Tests should pass unchanged.

### Step 1.4: Commit
```bash
./scripts/ai_commit.sh "refactor: migrate tables.py to codes/is456/"
```

---

## Phase 2: Migrate shear.py

### Step 2.1: Preview and Execute
```bash
.venv/bin/python scripts/migrate_module.py shear --dry-run
.venv/bin/python scripts/migrate_module.py shear
```

### Step 2.2: Verify
```bash
.venv/bin/python -m pytest Python/tests/test_shear*.py -v
.venv/bin/python -c "from structural_lib.shear import design_shear; print('OK')"
```

### Step 2.3: Commit
```bash
./scripts/ai_commit.sh "refactor: migrate shear.py to codes/is456/"
```

---

## Phase 3: Migrate flexure.py

### Step 3.1: Preview and Execute
```bash
.venv/bin/python scripts/migrate_module.py flexure --dry-run
.venv/bin/python scripts/migrate_module.py flexure
```

### Step 3.2: Verify
```bash
.venv/bin/python -m pytest Python/tests/test_flexure*.py -v
.venv/bin/python -c "from structural_lib.flexure import design_singly_reinforced; print('OK')"
```

### Step 3.3: Commit
```bash
./scripts/ai_commit.sh "refactor: migrate flexure.py to codes/is456/"
```

---

## Phase 4: Migrate detailing.py

### Step 4.1: Preview and Execute
```bash
.venv/bin/python scripts/migrate_module.py detailing --dry-run
.venv/bin/python scripts/migrate_module.py detailing
```

### Step 4.2: Verify
```bash
.venv/bin/python -m pytest Python/tests/test_detailing*.py -v
```

### Step 4.3: Commit
```bash
./scripts/ai_commit.sh "refactor: migrate detailing.py to codes/is456/"
```

---

## Phase 5: Migrate serviceability.py

### Step 5.1: Preview and Execute
```bash
.venv/bin/python scripts/migrate_module.py serviceability --dry-run
.venv/bin/python scripts/migrate_module.py serviceability
```

### Step 5.2: Verify
```bash
.venv/bin/python -m pytest Python/tests/test_serviceability*.py -v
```

### Step 5.3: Commit
```bash
./scripts/ai_commit.sh "refactor: migrate serviceability.py to codes/is456/"
```

---

## Phase 6: Migrate compliance.py

### Step 6.1: Preview and Execute
```bash
.venv/bin/python scripts/migrate_module.py compliance --dry-run
.venv/bin/python scripts/migrate_module.py compliance
```

### Step 6.2: Verify
```bash
.venv/bin/python -m pytest Python/tests/test_compliance*.py -v
```

### Step 6.3: Commit
```bash
./scripts/ai_commit.sh "refactor: migrate compliance.py to codes/is456/"
```

---

## Phase 7: Migrate ductile.py

### Step 7.1: Preview and Execute
```bash
.venv/bin/python scripts/migrate_module.py ductile --dry-run
.venv/bin/python scripts/migrate_module.py ductile
```

### Step 7.2: Verify
```bash
.venv/bin/python -m pytest Python/tests/test_ductile*.py -v
```

### Step 7.3: Commit
```bash
./scripts/ai_commit.sh "refactor: migrate ductile.py to codes/is456/"
```

---

## Post-Migration: Final Validation

### Step 8.1: Full Validation
```bash
.venv/bin/python scripts/validate_migration.py --verbose --run-tests
```

**Expected:**
```
✅ Passed:  35+
❌ Failed:  0
✅ All validations passed!
```

### Step 8.2: Full Test Suite
```bash
.venv/bin/python -m pytest Python/tests/ -v --tb=short
```

All tests should pass.

### Step 8.3: API Verification
```bash
.venv/bin/python -c "
from structural_lib.api import design_beam_is456
from structural_lib import flexure, shear, detailing
from structural_lib.codes.is456 import IS456Code
from structural_lib.core import CodeRegistry

print('Old paths work:', 'design_singly_reinforced' in dir(flexure))
print('New paths work:', CodeRegistry.is_registered('IS456'))
print('API works:', design_beam_is456.__name__)
"
```

### Step 8.4: Update codes/is456/__init__.py

Ensure all migrated functions are exported:

```python
# Python/structural_lib/codes/is456/__init__.py
from structural_lib.codes.is456.flexure import *
from structural_lib.codes.is456.shear import *
from structural_lib.codes.is456.detailing import *
# ... etc
```

### Step 8.5: Final Commit
```bash
./scripts/ai_commit.sh "refactor: complete IS 456 module migration"
```

---

## Rollback Procedures

### Rollback Single Module

```bash
# Restore original from git
git checkout HEAD~1 -- Python/structural_lib/flexure.py

# Remove migrated file
rm Python/structural_lib/codes/is456/flexure.py

# Verify
.venv/bin/python -c "from structural_lib.flexure import design_singly_reinforced; print('OK')"
```

### Rollback All (Emergency)

```bash
# Return to main branch
git checkout main

# Delete feature branch
git branch -D feat/migrate-is456-modules

# Verify clean state
.venv/bin/python scripts/pre_migration_check.py
```

---

## Troubleshooting

### Import Error After Migration

**Symptom:** `ModuleNotFoundError: No module named 'structural_lib.codes.is456.flexure'`

**Cause:** Migration didn't complete properly

**Fix:**
```bash
# Check file exists
ls Python/structural_lib/codes/is456/flexure.py

# If missing, re-run migration
.venv/bin/python scripts/migrate_module.py flexure
```

### Circular Import Error

**Symptom:** `ImportError: cannot import name 'X' from partially initialized module`

**Cause:** Circular dependency between modules

**Fix:**
1. Check which modules are involved
2. Use lazy import (import inside function)
3. Move shared code to core/

### Test Failures After Migration

**Symptom:** Tests fail with import errors

**Cause:** Re-export stub not working

**Fix:**
```bash
# Verify stub exists and is correct
cat Python/structural_lib/flexure.py

# Should show "Backward compatibility stub"
# If not, recreate:
.venv/bin/python scripts/create_reexport_stub.py flexure
```

### Stub Has Wrong Content

**Symptom:** Original code exists instead of stub

**Cause:** Migration script didn't create stub

**Fix:**
```bash
# Manually create stub
.venv/bin/python scripts/create_reexport_stub.py flexure
```

---

## Checklist Summary

Copy this for your migration session:

```
PRE-MIGRATION
[ ] Session started
[ ] Pre-flight checks pass
[ ] Feature branch created

PHASE 1-7 (for each module)
[ ] Dry-run preview
[ ] Execute migration
[ ] Module tests pass
[ ] Commit

POST-MIGRATION
[ ] Full validation passes
[ ] All tests pass
[ ] API verification passes
[ ] codes/is456/__init__.py updated
[ ] Final commit

CLEANUP
[ ] Merge feature branch
[ ] Update documentation
[ ] Close migration task
```

---

## Related Documents

- [is456-migration-research.md](../research/is456-migration-research.md) - Full research
- [migration-preflight-checklist.md](migration-preflight-checklist.md) - Detailed checklist
- [enterprise-folder-structure-research.md](../research/enterprise-folder-structure-research.md) - Architecture research

---

*Workflow created: 2026-01-10 Session 5*
