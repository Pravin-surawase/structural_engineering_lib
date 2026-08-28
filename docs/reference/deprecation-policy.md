---
owner: Main Agent
status: active
last_updated: 2026-08-24
doc_type: reference
complexity: intermediate
tags: []
---

# Deprecation Policy

**Type:** Reference
**Audience:** Developers
**Status:** Pre-1.0 Beta Policy
**Importance:** Medium
**Version:** 0.24.0
**Created:** 2025-12-01
**Last Updated:** 2026-08-24

---

## Overview

This document defines deprecation behavior for the pre-1.0 Beta package. Deprecation
metadata is a real project commitment, not a label for every compatibility
facade. No public file, export, or signature may be removed without the
separate authorization and evidence required by repository Git governance.

---

## Policy

### Timeline

- A deprecation must name a real replacement and an owner-approved removal
  version before `@deprecated` is added.
- A stable identity-only re-export is not deprecated merely because another
  module owns the object.
- A contract that remains callable but cannot satisfy a newer safety contract
  may be marked `HELD_COMPATIBILITY` with `removal_version: null`. Held metadata
  emits no warning and makes no removal promise.
- Removing an item remains a separate task requiring caller, test, documentation,
  archive/fixture, rollback, and explicit deletion-authorization evidence.

### Versioning Strategy

Following [Semantic Versioning 2.0.0](https://semver.org/):

| Version Change | Breaking Changes Allowed | Example |
|----------------|-------------------------|---------|
| **Major** (1.0.0 → 2.0.0) | ✅ Yes | Remove deprecated features |
| **Minor** (0.14.0 → 0.15.0) | ❌ No | Add deprecation warnings only |
| **Patch** (0.14.0 → 0.14.1) | ❌ No | Bug fixes only |

### Pre-1.0 Exception

During 0.x releases, semantic versioning does not itself authorize a breaking
change. Repository approval and evidence gates still apply.

### Compatibility is not deprecation

`structural_lib.api` and the package's pure root re-export modules remain
compatible when they resolve to the same object and signature. They must not
emit warning floods during ordinary package import. The P5 ETABS historical
helpers carry limitation metadata because they cannot represent the accepted
snapshot contract; P7 does not give them a fabricated removal release.

---

## Implementation

### For Functions

Use the `@deprecated` decorator:

```python
from structural_lib.core.deprecation import deprecated

@deprecated(
    version="0.14.0",
    remove_version="1.0.0",
    alternative="api.design_beam_is456",
    reason="Simplified API signature"
)
def design_beam_old(b, d, D, mu, fck, fy):
    """Old design function (DEPRECATED)."""
    # Redirect to new API
    return design_beam_is456(b=b, d=d, fck=fck, fy=fy, mu_knm=mu)
```

Use this decorator only after the example versions have been replaced with an
approved live schedule. The values below are illustrative, not current project
removal claims.

**Required Parameters:**
- `version`: Version when deprecation was introduced
- `remove_version`: Version when feature will be removed

**Optional Parameters:**
- `alternative`: Recommended replacement (helps users migrate)
- `reason`: Explanation of why feature was deprecated

### For Dataclass Fields

Use `deprecated_field()` in `__post_init__`:

```python
from dataclasses import dataclass, field
from structural_lib.core.deprecation import deprecated_field
from structural_lib.core.errors import DesignError

@dataclass
class FlexureResult:
    # New structured errors field
    errors: list[DesignError] = field(default_factory=list)

    # Old string field (deprecated)
    error_message: str = ""

    def __post_init__(self):
        # Only warn if field is actually used
        if self.error_message:
            deprecated_field(
                dataclass_name="FlexureResult",
                field_name="error_message",
                version="0.14.0",
                remove_version="1.0.0",
                alternative="errors"
            )
```

---

## Warning Behavior

### Default Behavior

Python **silences** `DeprecationWarning` by default. Users won't see warnings unless they explicitly enable them.

### For Library Users

Enable deprecation warnings in your code:

```python
import warnings

# Show all deprecation warnings
warnings.simplefilter("default", DeprecationWarning)

# Or show all warnings
warnings.simplefilter("always")
```

Or run Python with warnings enabled:

```bash
python -W default::DeprecationWarning your_script.py
```

### For Library Developers

Tests automatically capture deprecation warnings:

```python
import warnings
import pytest

def test_deprecated_function():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        result = old_function()  # Calls deprecated function

        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "old_function is deprecated" in str(w[0].message)
```

---

## Documentation Requirements

### 1. Function/Class Docstring

Mark the item as deprecated in the docstring:

```python
@deprecated("0.14.0", "1.0.0", alternative="new_function")
def old_function():
    """
    Calculate something (DEPRECATED).

    .. deprecated:: 0.14.0
       Use :func:`new_function` instead. This function will be removed in v1.0.0.

    Returns
    -------
    float
        The result.
    """
    pass
```

### 2. CHANGELOG.md Entry

Add entry in `CHANGELOG.md` under "Deprecated" section:

```markdown
### Deprecated

- `flexure.calculate_moment_old()` — Use `flexure.calculate_moment()` instead.
  Will be removed in v1.0.0. (#254)
- `FlexureResult.error_message` field — Use `FlexureResult.errors` list instead.
  Will be removed in v1.0.0. (#254)
```

### 3. API Documentation

Update `docs/api-reference.md` to mark deprecated items:

```markdown
## ⚠️ Deprecated Functions

These functions are deprecated and will be removed in future versions:

| Function | Deprecated In | Remove In | Alternative |
|----------|---------------|-----------|-------------|
| `calculate_moment_old()` | v0.14.0 | v1.0.0 | `calculate_moment()` |
```

---

## Migration Guide Template

When an approved deprecation exists, provide migration examples in release
notes. Every name and version below is a template placeholder, not a current
project schedule:

```markdown
## Migration Guide: v0.14.0 → v1.0.0

### Deprecated API Changes

#### `calculate_moment_old()` → `calculate_moment()`

**Old Code (v0.13.x):**
```python
result = calculate_moment_old(b=300, d=450, fck=25, fy=500, mu=150)
```

**New Code (v0.14.0+):**
```python
result = calculate_moment(
    b_mm=300,
    d_mm=450,
    fck_mpa=25,
    fy_mpa=500,
    mu_knm=150
)
```

**Why Changed:** Explicit unit naming reduces confusion and errors.

**Timeline:**
- v0.14.0: Deprecation warning added
- v1.0.0: Old function removed
```

---

## Removal Process

### When Removing Deprecated Features

Removal is not authorized by elapsed time or metadata alone. Stop and obtain
explicit owner authorization after producing the required retirement evidence.

1. **Check Metadata:** Use `__deprecated__` attribute to find all deprecated items:

```python
import inspect
from structural_lib import api

for name, obj in inspect.getmembers(api):
    if hasattr(obj, "__deprecated__"):
        meta = obj.__deprecated__
        print(f"{name}: Remove in {meta['remove_version']}")
```

2. **Verify Timeline:** Ensure minimum notice period has elapsed

3. **Update CHANGELOG:**

```markdown
### Removed

- `calculate_moment_old()` — Deprecated since v0.14.0. Use `calculate_moment()`.
```

4. **Update Tests:** Remove tests for deprecated features (or mark as testing removal)

5. **Update Docs:** Remove from API reference, add to "Removed Features" section

---

## Illustrative examples only

The following names and versions are placeholders. They do not describe a
current export or authorize its removal.

### Example 1: Deprecating a Function

```python
# Step 1: Create new function
def calculate_shear_new(vd_kn, b_mm, d_mm):
    """New shear calculation with explicit units."""
    return vd_kn / (b_mm * d_mm)

# Step 2: Deprecate old function
@deprecated("0.14.0", "1.0.0", alternative="calculate_shear_new")
def calculate_shear(vd, b, d):
    """Old shear calculation (DEPRECATED)."""
    return calculate_shear_new(vd, b, d)
```

### Example 2: Deprecating a Parameter

```python
@deprecated("0.14.0", "1.0.0", reason="units parameter removed")
def design_beam(b, d, fck, fy, units="IS456"):
    """
    Design beam.

    Parameters
    ----------
    units : str, optional (DEPRECATED)
        This parameter is deprecated and will be removed in v1.0.0.
        All calculations now use IS 456 units by default.
    """
    if units != "IS456":
        warnings.warn(
            f"units='{units}' is deprecated. All calculations use IS 456 units.",
            DeprecationWarning,
            stacklevel=2
        )
    # ... rest of function
```

---

## Introspection

Find all deprecated items programmatically:

```python
import inspect
from structural_lib import api, flexure, shear

def find_deprecated(module):
    """Find all deprecated items in a module."""
    deprecated_items = []

    for name, obj in inspect.getmembers(module):
        if callable(obj) and hasattr(obj, "__deprecated__"):
            meta = obj.__deprecated__
            deprecated_items.append({
                "name": name,
                "version": meta["version"],
                "remove_version": meta["remove_version"],
                "alternative": meta.get("alternative"),
            })

    return deprecated_items

# Usage
deprecated = find_deprecated(api)
for item in deprecated:
    print(f"{item['name']}: deprecated in {item['version']}, "
          f"remove in {item['remove_version']}")
```

---

## References

- [PEP 387](https://peps.python.org/pep-0387/) — Backwards Compatibility Policy
- [Semantic Versioning](https://semver.org/)
- [NumPy Deprecation Policy](https://numpy.org/neps/nep-0023-backwards-compatibility.html)
- [Pandas Deprecation Policy](https://pandas.pydata.org/docs/development/policies.html#deprecation-policy)

---

## See Also

- [`structural_lib.core.deprecation.deprecated`](../reference/api.md#deprecated) — Decorator owner
- [`structural_lib.core.deprecation.deprecated_field`](../reference/api.md#deprecated_field) — Field deprecation owner
- [P7 compatibility migration](../migration/lib-pro-007-p7-compatibility-convergence.md) — Current facade and held-compatibility policy
- [CHANGELOG.md](../../CHANGELOG.md) — Release history with deprecation notices
- [docs/research/backward-compatibility-strategy.md](../_archive/research-completed/backward-compatibility-strategy.md) — Full research document
