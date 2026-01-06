# API Evolution & Migration Standard

> **Standard for API versioning, deprecation, and backward compatibility**
> Created: 2026-01-07 | Status: Active | Part of: API Improvement Research (TASK-207)

---

## Purpose

This document establishes standards for evolving APIs while maintaining stability and user trust:
- **Stability**: Users can upgrade without breaking their code
- **Clarity**: Changes are well-communicated with clear migration paths
- **Predictability**: Version numbers signal impact and breaking changes
- **Professionalism**: Deprecation follows industry best practices

**Target audience**: Library developers making API changes, releasing new versions.

---

## Table of Contents

1. [Core Principles](#1-core-principles)
2. [Semantic Versioning (SemVer)](#2-semantic-versioning-semver)
3. [Backward Compatibility Strategies](#3-backward-compatibility-strategies)
4. [Deprecation Process](#4-deprecation-process)
5. [Breaking Changes](#5-breaking-changes)
6. [Version Communication](#6-version-communication)
7. [Migration Tools & Helpers](#7-migration-tools--helpers)
8. [API Lifecycle Management](#8-api-lifecycle-management)

**Appendices:**
- [A: Quick Reference Card](#appendix-a-quick-reference-card)
- [B: Real-World Examples](#appendix-b-real-world-examples)

---

## 1. Core Principles

### 1.1 The Stability Promise

**Users trust libraries that don't break their code.** Every breaking change costs users time and erodes trust.

**Our commitment:**
- **0.x releases**: Can break, but we minimize it
- **1.0+ releases**: Breaking changes ONLY in major versions (1.0 → 2.0)
- **Deprecation period**: Minimum 2 minor versions (e.g., 1.2 → 1.3 → 1.4 → 2.0)
- **Clear warnings**: Deprecation warnings tell users what to do

### 1.2 The Three Rules of API Evolution

**Rule 1: Never break silently**
```python
# ❌ BAD: Function disappears in v2.0, user code fails at runtime
# v1.5: design_beam() exists
# v2.0: design_beam() removed → ImportError!

# ✅ GOOD: Deprecation warnings in v1.6-1.9, removal in v2.0
# v1.6: design_beam() works but warns
# v2.0: design_beam() removed, but user had 4 versions to migrate
```

**Rule 2: Provide migration path before removal**
```python
# ❌ BAD: Rename function, no guidance
def calculate_reinforcement(...):  # Was calculate_steel()
    """Calculate reinforcement."""
    # User has no idea this replaced calculate_steel()

# ✅ GOOD: Old function delegates to new, warns with guidance
@deprecated(
    version='1.6',
    removal_version='2.0',
    replacement='calculate_reinforcement',
    instructions='Rename calculate_steel() to calculate_reinforcement()'
)
def calculate_steel(...):
    """Deprecated: Use calculate_reinforcement() instead."""
    return calculate_reinforcement(...)
```

**Rule 3: Version numbers communicate impact**
```
1.2.3 → 1.2.4  (patch)   → Bug fix, safe to upgrade
1.2.4 → 1.3.0  (minor)   → New features, safe to upgrade, deprecations announced
1.3.0 → 2.0.0  (major)   → Breaking changes, read migration guide
```

### 1.3 Cost-Benefit Analysis

**Before making a breaking change, ask:**

| Question | If YES → | If NO → |
|----------|----------|---------|
| Does the old API have critical bugs? | Breaking change justified | Keep backward compat |
| Will the new API prevent common user errors? | Breaking change justified | Keep backward compat |
| Does the old API block important features? | Breaking change justified | Keep backward compat |
| Is the old API widely used? | Provide compatibility layer | Safe to break |
| Can we maintain both APIs? | Keep backward compat | Document trade-off |

**Example decision matrix:**

```python
# Scenario: Rename b_mm → width_mm for clarity

# Analysis:
# - Old API bugs? NO (works correctly)
# - New API prevents errors? MAYBE (slightly clearer)
# - Blocks features? NO
# - Widely used? YES (in 100+ function calls)
# - Can maintain both? YES (parameter alias)

# Decision: DON'T break, use parameter alias
def design_beam(
    width_mm: float = None,  # New name
    b_mm: float = None,      # Old name (deprecated)
):
    if b_mm is not None:
        warnings.warn("b_mm is deprecated, use width_mm", DeprecationWarning)
        if width_mm is None:
            width_mm = b_mm
    # Implementation uses width_mm
```

### 1.4 Industry Standards We Follow

**Inspiration from mature libraries:**

| Library | Practice We Adopt |
|---------|-------------------|
| **NumPy** | Deprecation warnings with version numbers, long deprecation cycles |
| **Pandas** | FutureWarning for behavior changes, clear "what to do instead" |
| **Django** | Detailed release notes, migration guides, deprecation timeline |
| **Requests** | Semantic versioning strictly followed since 1.0 |
| **FastAPI** | Breaking changes only in 0.x, explicit 1.0 stability promise |

---

## 2. Semantic Versioning (SemVer)

### 2.1 Version Number Format

**Format:** `MAJOR.MINOR.PATCH` (e.g., `1.5.2`)

```
MAJOR.MINOR.PATCH
  │     │     │
  │     │     └─ Bug fixes (backward compatible)
  │     └─────── New features (backward compatible)
  └───────────── Breaking changes (NOT backward compatible)
```

**Examples:**
- `0.15.0 → 0.15.1`: Bug fix (patch)
- `0.15.1 → 0.16.0`: New feature (minor)
- `0.16.5 → 1.0.0`: Breaking changes (major)

### 2.2 Pre-1.0 Development (Current: v0.15.x)

**Rules for 0.x versions:**
- **0.x.0 → 0.x.y** (patch): Bug fixes only
- **0.x.y → 0.(x+1).0** (minor): New features OR breaking changes (with warnings)
- **Breaking changes allowed** but we minimize them

**Our practice during 0.x:**
```python
# v0.15.0: Initial API
def design_beam(b_mm, d_mm, mu_kn_m):
    ...

# v0.16.0: Add optional parameter (non-breaking)
def design_beam(b_mm, d_mm, mu_kn_m, cover_mm=25):
    ...

# v0.17.0: Could break if needed, but we'll warn first
@deprecated(version='0.17', removal_version='1.0')
def design_beam_old(...):
    ...
```

### 2.3 Post-1.0 Stability (Target)

**Rules for 1.x versions:**
- **1.x.y → 1.x.(y+1)** (patch): Bug fixes ONLY, 100% backward compatible
- **1.x.0 → 1.(x+1).0** (minor): New features, deprecations announced, 100% backward compatible
- **1.x.0 → 2.0.0** (major): Breaking changes, migration guide provided

**Timeline for 1.0 release:**
- **v0.16-0.19**: Stabilize API, fix known issues, collect feedback
- **v0.20**: API freeze, final breaking changes
- **v1.0-rc1**: Release candidate, community testing
- **v1.0**: Stability promise begins

### 2.4 Version Bumping Rules

**Patch bump (x.y.Z):**
```python
# Bug fix: incorrect calculation
# v1.5.2 → v1.5.3

# BEFORE (bug):
def calculate_ast_min(b_mm, d_mm):
    return 0.85 * b_mm * d_mm / 100  # Wrong coefficient

# AFTER (fixed):
def calculate_ast_min(b_mm, d_mm):
    return 0.85 * b_mm * d_mm / fy  # Correct per IS 456
```

**Minor bump (x.Y.0):**
```python
# New feature: add optional parameter
# v1.5.3 → v1.6.0

# New feature: optional clear cover
def design_beam(..., cover_mm: Optional[float] = None):
    if cover_mm is None:
        cover_mm = get_default_cover(...)
    # Rest of implementation
```

**Major bump (X.0.0):**
```python
# Breaking change: remove deprecated function
# v1.9.0 → v2.0.0

# v1.x: Function exists but deprecated
@deprecated(version='1.6', removal_version='2.0')
def calculate_steel(...):
    return calculate_reinforcement(...)

# v2.0: Function removed
# calculate_steel() no longer exists
```

### 2.5 Version Constraints in Dependencies

**When users install our library:**

```bash
# Exact version (fragile, avoid)
pip install structural-lib-is456==1.5.2

# Compatible release (recommended)
pip install "structural-lib-is456~=1.5.2"  # Allows 1.5.2+, < 1.6.0

# Minor version range (safe for 1.x)
pip install "structural-lib-is456>=1.5,<2.0"  # Any 1.x

# Minimum version (risky, can break)
pip install "structural-lib-is456>=1.5"  # Any version ≥ 1.5
```

**Our recommendation in docs:**
```python
# requirements.txt
structural-lib-is456>=1.5,<2.0  # Safe: any 1.x version
```

---

## 3. Backward Compatibility Strategies

### 3.1 Adding Optional Parameters

**Safe: Add parameters with defaults at the end**

```python
# v1.0: Original function
def design_beam(b_mm: float, d_mm: float, mu_kn_m: float) -> BeamResult:
    ...

# v1.1: Add optional parameter (backward compatible)
def design_beam(
    b_mm: float,
    d_mm: float,
    mu_kn_m: float,
    cover_mm: Optional[float] = None,  # New, optional
) -> BeamResult:
    if cover_mm is None:
        cover_mm = 25  # Default
    ...

# User code from v1.0 still works:
result = design_beam(300, 550, 180)  # ✅ No changes needed
```

**Unsafe: Adding required parameters**
```python
# ❌ BREAKING: New required parameter
def design_beam(
    b_mm: float,
    d_mm: float,
    mu_kn_m: float,
    cover_mm: float,  # NEW REQUIRED - breaks old code!
) -> BeamResult:
    ...

# Old user code breaks:
result = design_beam(300, 550, 180)  # ❌ TypeError: missing cover_mm
```

### 3.2 Renaming Parameters (Without Breaking)

**Strategy: Accept both names, deprecate old name**

```python
# v1.5: Rename b_mm → width_mm (more explicit)
def design_beam(
    width_mm: Optional[float] = None,  # New name
    d_mm: float,
    mu_kn_m: float,
    *,
    b_mm: Optional[float] = None,  # Old name (deprecated)
) -> BeamResult:
    """Design beam section.

    Args:
        width_mm: Beam width in mm. (Preferred over b_mm)
        d_mm: Effective depth in mm
        mu_kn_m: Factored moment in kN·m
        b_mm: (Deprecated) Use width_mm instead.
    """
    # Handle both parameters
    if b_mm is not None and width_mm is not None:
        raise ValueError("Cannot specify both b_mm and width_mm")

    if b_mm is not None:
        warnings.warn(
            "Parameter 'b_mm' is deprecated since v1.5, "
            "use 'width_mm' instead. Will be removed in v2.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        width_mm = b_mm

    if width_mm is None:
        raise ValueError("Must specify width_mm")

    # Implementation uses width_mm
    ...

# v2.0: Remove b_mm parameter completely
def design_beam(width_mm: float, d_mm: float, mu_kn_m: float) -> BeamResult:
    ...
```

### 3.3 Changing Return Types (Without Breaking)

**Strategy 1: Return new type that's compatible with old usage**

```python
# v1.0: Returns dict
def design_beam(...) -> dict:
    return {
        'ast_required': 1245.0,
        'ast_min': 825.0,
        'status': 'OK',
    }

# User code expects dict:
result = design_beam(...)
print(result['ast_required'])  # Works

# v1.5: Return dataclass that behaves like dict
@dataclass
class BeamResult:
    ast_required: float
    ast_min: float
    status: str

    def __getitem__(self, key: str):
        """Support dict-like access for backward compatibility."""
        return getattr(self, key)

def design_beam(...) -> BeamResult:
    return BeamResult(
        ast_required=1245.0,
        ast_min=825.0,
        status='OK',
    )

# Old user code still works:
result = design_beam(...)
print(result['ast_required'])  # ✅ Works via __getitem__

# New user code can use attributes:
print(result.ast_required)  # ✅ Also works
```

**Strategy 2: Add new function, deprecate old**

```python
# v1.0: Returns dict
def design_beam(...) -> dict:
    ...

# v1.5: Add new function with better return type
def design_beam_ex(...) -> BeamResult:
    """Extended version with structured result."""
    ...

@deprecated(version='1.5', removal_version='2.0')
def design_beam(...) -> dict:
    """Deprecated: Use design_beam_ex() for structured results."""
    result = design_beam_ex(...)
    return {
        'ast_required': result.ast_required,
        'ast_min': result.ast_min,
        'status': result.status,
    }

# v2.0: Remove old function
def design_beam(...) -> BeamResult:
    """Returns structured BeamResult object."""
    ...
```

### 3.4 Changing Behavior (Tricky!)

**Strategy: Use explicit flag for new behavior**

```python
# v1.0: Function rounds results to 1 decimal
def calculate_ast_required(...) -> float:
    ast = ...  # Calculate
    return round(ast, 1)  # Always rounded

# v1.5: Want to return exact value, but old code expects rounding
def calculate_ast_required(
    ...,
    *,
    round_result: bool = True,  # Explicit flag
) -> float:
    """Calculate required steel area.

    Args:
        round_result: If True (default), round to 1 decimal for
            backward compatibility. Set False for exact value.
            Default will change to False in v2.0.
    """
    ast = ...  # Calculate

    if round_result:
        warnings.warn(
            "Rounding behavior is deprecated. "
            "Set round_result=False for exact values. "
            "Default will change to False in v2.0.",
            FutureWarning,
        )
        return round(ast, 1)
    else:
        return ast

# v2.0: Change default to False
def calculate_ast_required(..., round_result: bool = False) -> float:
    ...
```

### 3.5 Adding Required Validation

**Strategy: Make it optional first, required later**

```python
# v1.0: No validation
def design_beam(b_mm: float, d_mm: float, mu_kn_m: float):
    # Accepts any values, even invalid ones
    ...

# v1.5: Add validation with opt-out
def design_beam(
    b_mm: float,
    d_mm: float,
    mu_kn_m: float,
    *,
    validate: bool = True,  # New parameter
):
    """Design beam section.

    Args:
        validate: If True (default), validate inputs per IS 456.
            Set False to skip validation (for backward compatibility
            or when inputs are pre-validated). Validation will be
            mandatory in v2.0.
    """
    if validate:
        if b_mm < 200:
            raise DimensionError(f"b_mm={b_mm} < minimum 200mm")
        # More validation...
    else:
        warnings.warn(
            "Skipping validation is deprecated. "
            "Validation will be mandatory in v2.0.",
            FutureWarning,
        )

    # Implementation...

# v2.0: Remove validate parameter, always validate
def design_beam(b_mm: float, d_mm: float, mu_kn_m: float):
    """Design beam section. Inputs are validated per IS 456."""
    if b_mm < 200:
        raise DimensionError(f"b_mm={b_mm} < minimum 200mm")
    # Always validate
    ...
```

---

## 4. Deprecation Process

### 4.1 Deprecation Decorator

**Implementation:**

```python
# structural_lib/deprecation.py
import warnings
import functools
from typing import Optional, Callable

def deprecated(
    version: str,
    removal_version: str,
    replacement: Optional[str] = None,
    instructions: Optional[str] = None,
) -> Callable:
    """Mark function as deprecated.

    Args:
        version: Version when deprecation started (e.g., '1.5')
        removal_version: Version when function will be removed (e.g., '2.0')
        replacement: Name of replacement function (if any)
        instructions: Detailed migration instructions

    Example:
        @deprecated(
            version='1.5',
            removal_version='2.0',
            replacement='calculate_reinforcement',
            instructions='Rename calculate_steel() to calculate_reinforcement()'
        )
        def calculate_steel(...):
            return calculate_reinforcement(...)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Build warning message
            msg = (
                f"{func.__name__} is deprecated since v{version} "
                f"and will be removed in v{removal_version}."
            )

            if replacement:
                msg += f" Use {replacement}() instead."

            if instructions:
                msg += f" Migration: {instructions}"

            # Emit warning
            warnings.warn(msg, DeprecationWarning, stacklevel=2)

            # Call original function
            return func(*args, **kwargs)

        # Mark as deprecated in docstring
        if wrapper.__doc__:
            wrapper.__doc__ = (
                f"**DEPRECATED since v{version}** "
                f"(will be removed in v{removal_version})\n\n"
                f"{wrapper.__doc__}"
            )

        return wrapper
    return decorator
```

**Usage:**

```python
@deprecated(
    version='1.5',
    removal_version='2.0',
    replacement='calculate_reinforcement',
)
def calculate_steel(b_mm: float, d_mm: float, mu_kn_m: float) -> float:
    """Calculate required steel area.

    **Deprecated:** Use calculate_reinforcement() instead.
    """
    return calculate_reinforcement(b_mm, d_mm, mu_kn_m)

# When user calls:
ast = calculate_steel(300, 550, 180)
# Warning shown:
# DeprecationWarning: calculate_steel is deprecated since v1.5
# and will be removed in v2.0. Use calculate_reinforcement() instead.
```

### 4.2 Deprecation Timeline

**Standard deprecation cycle:**

```
v1.5: Announce deprecation (warning appears, function works)
      ↓
v1.6: Still deprecated (warning appears, function works)
      ↓
v1.7: Still deprecated (warning appears, function works)
      ↓
v1.8: Still deprecated (warning appears, function works)
      ↓
v2.0: Remove function (ImportError or AttributeError)
```

**Minimum deprecation period: 2 minor versions** (e.g., 1.5 → 1.6 → 1.7 → 2.0)

**For critical functions: 4+ minor versions** (give users more time)

### 4.3 Deprecation Warning Types

**Python has 3 warning types:**

```python
# 1. DeprecationWarning (default, hidden by Python)
warnings.warn("Deprecated", DeprecationWarning)
# Hidden unless user runs: python -Wd script.py

# 2. FutureWarning (shown by default)
warnings.warn("Behavior will change", FutureWarning)
# Always visible to users

# 3. PendingDeprecationWarning (hidden, for early notice)
warnings.warn("Will deprecate soon", PendingDeprecationWarning)
# Hidden unless user runs: python -Wd script.py
```

**When to use each:**

| Warning Type | When to Use | Example |
|--------------|-------------|---------|
| **DeprecationWarning** | Function will be removed | Deprecated function |
| **FutureWarning** | Behavior will change | Default parameter value changes |
| **PendingDeprecationWarning** | Might deprecate in future | Experimental feature might change |

**Our practice:**
```python
# Function removal → DeprecationWarning
@deprecated(version='1.5', removal_version='2.0')
def old_function():
    warnings.warn("...", DeprecationWarning)

# Behavior change → FutureWarning
def function(param: bool = True):
    warnings.warn(
        "Default value of param will change to False in v2.0",
        FutureWarning,
    )
```

### 4.4 Documenting Deprecations

**In docstring:**
```python
def calculate_steel(...):
    """Calculate required steel area.

    .. deprecated:: 1.5
        Use :func:`calculate_reinforcement` instead.
        Will be removed in version 2.0.

    Args:
        ...
    """
```

**In CHANGELOG.md:**
```markdown
## [1.5.0] - 2026-01-15

### Deprecated
- `calculate_steel()` is deprecated in favor of `calculate_reinforcement()`.
  Will be removed in v2.0. ([#123](link-to-issue))
- `design_beam()` parameter `b_mm` is deprecated in favor of `width_mm`.
  Will be removed in v2.0.

### Migration Guide
```python
# Before (v1.4):
ast = calculate_steel(b_mm, d_mm, mu_kn_m)

# After (v1.5+):
ast = calculate_reinforcement(b_mm, d_mm, mu_kn_m)
```
```

**In API docs:**
```python
# docs/deprecations.md

# Deprecation Schedule

## v2.0 Removals (from v1.5 deprecations)

| Deprecated Item | Deprecated In | Removal In | Replacement |
|-----------------|---------------|------------|-------------|
| `calculate_steel()` | v1.5 | v2.0 | `calculate_reinforcement()` |
| `design_beam(b_mm=...)` | v1.5 | v2.0 | `design_beam(width_mm=...)` |
| `validate=False` | v1.6 | v2.0 | Always validate (no flag) |
```

---

## 5. Breaking Changes

*(To be added in Step 2)*

---

## 6. Version Communication

*(To be added in Step 2)*

---

## 7. Migration Tools & Helpers

*(To be added in Step 2)*

---

## 8. API Lifecycle Management

*(To be added in Step 2)*

---

## Appendix A: Quick Reference Card

*(To be added in Step 2)*

---

## Appendix B: Real-World Examples

*(To be added in Step 2)*
