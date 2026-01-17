# API Stability & Versioning Policy

**Type:** Policy
**Audience:** Developers
**Status:** Production Ready
**Importance:** Critical
**Created:** 2026-01-15
**Last Updated:** 2026-01-15

---

## Overview

This document defines how `structural_engineering_lib` manages **API stability**, **breaking changes**, and **versioning** to ensure **your code doesn't break** when upgrading.

---

## Versioning Scheme

We follow **Semantic Versioning (SemVer 2.0)**: `MAJOR.MINOR.PATCH`

### Version Format: `v0.17.5`

- **MAJOR (`0`)**: Breaking changes (rare, with migration guide)
- **MINOR (`17`)**: New features, backwards compatible
- **PATCH (`5`)**: Bug fixes, no API changes

### Current Status

| Version | Status | Stability |
|---------|--------|-----------|
| `v0.x.x` | Pre-1.0 (current) | ⚠️ API may change between minor versions |
| `v1.x.x` | Stable (planned Q1 2026) | ✅ API frozen, only compatible additions |
| `v2.x.x` | Future | ✅ Breaking changes allowed (with migration guide) |

---

## Stability Guarantees

### v1.0+ (Stable)

**Once v1.0 is released:**

✅ **GUARANTEED STABLE:**
- All 29 public functions in `structural_lib.api`
- Function signatures (parameters, return types)
- Data structures (`BeamDesignResult`, `BarArrangement`, etc.)
- Core calculation logic (IS 456 compliance)

⚠️ **MAY CHANGE (with deprecation warnings):**
- Internal implementation details
- Private functions (prefix `_`)
- Undocumented behavior

❌ **BREAKING CHANGES ONLY IN v2.0:**
- Removing public functions
- Changing function signatures
- Renaming data structure fields

### v0.x (Pre-Release)

**Before v1.0:**

⚠️ **API may change between minor versions** (`v0.16.x` → `v0.17.x`)
- New parameters may be added to functions
- Data structures may gain new fields
- Return types may be enhanced

✅ **We try to maintain compatibility:**
- Add new parameters with defaults
- Preserve existing parameter behavior
- Keep core calculation logic stable

---

## Public API Surface

### What's Included

**29 public functions are part of the stable API:**

```python
from structural_lib.api import (
    # Main entry points
    design_beam_is456,
    check_beam_is456,
    detail_beam_is456,

    # Design functions
    design_beam_flexure_is456,
    design_shear,

    # Detailing functions
    calculate_development_length,
    calculate_lap_length,
    calculate_anchorage_length,

    # Serviceability
    check_deflection_is456,
    check_crack_width,

    # Optimization
    optimize_beam_cost,
    suggest_design_improvements,

    # Analysis
    compute_bmd_sfd,
    analyze_torsion,

    # BBS
    generate_bbs_from_detailing,
    format_bbs_csv,

    # ... and 13 more
)
```

**See full list:** [API Reference](../reference/api.md)

### What's NOT Included

❌ **Private/internal functions (unstable):**
```python
# These may change without notice:
from structural_lib.flexure import _calculate_xu_max  # Private function
from structural_lib.internal.helpers import _format_bar  # Internal helper
```

❌ **VBA implementation details:**
- VBA module internal functions
- Excel worksheet structures

❌ **Streamlit UI code:**
- Page layouts
- Widget configurations

---

## Breaking Change Policy

### Definition

**A breaking change is:**
- Removing a public function
- Changing function signature (parameters, return type)
- Renaming data structure fields
- Changing calculation behavior (results differ)

### Process

**If we must make a breaking change:**

1. **Announce 3+ months in advance** (GitHub Discussion + release notes)
2. **Deprecation warning** in 1-2 minor versions before removal
3. **Migration guide** published with examples
4. **MAJOR version bump** (`v1.x` → `v2.0`)

### Example: Deprecating a Function

```python
# v1.5.0 - Deprecation warning
import warnings

def old_function_name(...):
    warnings.warn(
        "old_function_name() is deprecated, use new_function_name() instead. "
        "Will be removed in v2.0.",
        DeprecationWarning,
        stacklevel=2
    )
    return new_function_name(...)

# v2.0.0 - Removed
# Function no longer exists, use new_function_name()
```

---

## Safe Upgrade Practices

### Check Deprecation Warnings

**Before upgrading:**

```bash
# Run your code with warnings enabled
python -Wd my_script.py

# Check for DeprecationWarning
```

**Look for:**
```
DeprecationWarning: calculate_ast_required() is deprecated.
Use design_beam_flexure_is456() instead. Will be removed in v2.0.
```

### Test After Upgrade

```python
# test_after_upgrade.py
import pytest
from structural_lib.api import design_beam_is456

def test_my_integration_still_works():
    """Smoke test after library upgrade."""
    result = design_beam_is456(
        beam_id="B1",
        story="GF",
        span_mm=5000,
        b_mm=300,
        D_mm=500,
        cover_mm=25,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
        mu_knm=120.0,
        vu_kn=80.0,
    )

    assert result.ok, "Design should succeed"
    assert result.bars_bottom_start.count > 0, "Should have bottom steel"
```

### Pin Dependencies

**In production, pin to specific version:**

```python
# requirements.txt
structural-engineering-lib==1.2.5  # Pin exact version

# Or allow PATCH updates only:
structural-engineering-lib~=1.2.0  # Allows 1.2.x, not 1.3.0
```

---

## Version History

### v0.17.5 (Current - 2026-01-15)

**Added:**
- Multi-objective Pareto optimization
- API signature validation in CI
- 1317 tests (up from 1290)

**Changed:**
- None (backwards compatible)

**Deprecated:**
- None

### v0.16.6 (2026-01-12)

**Added:**
- Python 3.11 baseline
- Torsion design module
- ETABS CSV import

**Changed:**
- None (backwards compatible)

**Deprecated:**
- None

### v0.15.0 (2025-12-20)

**Added:**
- Cost optimization module
- Design suggestions with confidence scores

**Changed:**
- None (backwards compatible)

**Deprecated:**
- None

---

## Migration Guides

### Migrating from v0.16.x to v0.17.x

**No breaking changes** - drop-in replacement

```python
# v0.16.x code works unchanged in v0.17.x
result = design_beam_is456(...)
```

### Migrating from v0.15.x to v0.16.x

**New optional parameters added** (backwards compatible):

```python
# v0.15.x (still works)
result = design_beam_is456(
    beam_id="B1",
    span_mm=5000,
    # ... existing params
)

# v0.16.x (enhanced, optional)
result = design_beam_is456(
    beam_id="B1",
    span_mm=5000,
    # ... existing params
    torsion_mu_knm=15.0,  # NEW optional parameter
)
```

---

## API Compatibility Promise

### We Promise

✅ **Your code will not break** when upgrading MINOR versions (`v1.2.x` → `v1.3.x`)

✅ **Deprecation warnings** before removal (minimum 3 months notice)

✅ **Migration guides** for MAJOR version bumps

✅ **Bug fixes** never change API (only internal behavior)

### You Should

✅ **Pin versions** in production (`structural-engineering-lib==1.2.5`)

✅ **Test after upgrade** (run your test suite)

✅ **Watch for deprecation warnings** (`python -Wd`)

✅ **Read release notes** before upgrading

---

## Release Channels

### Stable (Recommended)

```bash
pip install structural-engineering-lib
```

- Semantic versioning
- Production-ready
- API stability guaranteed (v1.0+)

### Latest (Pre-Release)

```bash
pip install structural-engineering-lib --pre
```

- Early access to new features
- May have API changes
- Not recommended for production

### Development (Unstable)

```bash
pip install git+https://github.com/Pravin-surawase/structural_engineering_lib.git@main
```

- Latest commits
- No stability guarantees
- For testing only

---

## Monitoring API Changes

### Check Before Upgrading

```bash
# View changelog
pip show structural-engineering-lib

# Or check GitHub releases
https://github.com/Pravin-surawase/structural_engineering_lib/releases
```

### Subscribe to Notifications

- **GitHub Releases** → Watch repository, select "Releases only"
- **Breaking Changes** → Announced in GitHub Discussions

---

## Questions?

**API stability concerns?** [Open a discussion](https://github.com/Pravin-surawase/structural_engineering_lib/discussions)

**Found a breaking change?** [Report it](https://github.com/Pravin-surawase/structural_engineering_lib/issues/new)

---

**Version:** v0.17.5
**Last Updated:** 2026-01-15
