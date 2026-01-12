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
- `0.16.6 → 1.0.0`: Breaking changes (major)

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
  Will be removed in v2.0. (issue #123)
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

### 5.1 When Breaking Changes Are Justified

**Breaking changes are acceptable when:**

1. **Security/correctness**: Old API has bugs that can't be fixed compatibly
2. **Usability**: Old API causes frequent user errors
3. **Maintainability**: Old API blocks critical improvements
4. **Consistency**: Old API contradicts library conventions

**Examples:**

```python
# ✅ Justified: Security issue
# v1.x: Vulnerable to injection
def execute_query(sql: str):
    cursor.execute(sql)  # SQL injection risk!

# v2.0: Force parameterized queries
def execute_query(sql: str, params: tuple):
    cursor.execute(sql, params)  # Safe

# ✅ Justified: Prevents common errors
# v1.x: Silent unit mismatches
def calculate_load(value, unit='kN'):
    # Users often forget unit, get wrong results
    ...

# v2.0: Explicit unit in parameter name
def calculate_load(value_kn: float):
    # No ambiguity
    ...

# ❌ NOT justified: Just preference
# v1.x: Works fine
def calculate_steel(...):
    ...

# v2.0: Renaming just because
def calculate_reinforcement(...):  # Not worth breaking!
    ...
```

### 5.2 Making Breaking Changes Safely

**Process:**

```
Step 1 (v1.5): Announce deprecation
              ↓
Step 2 (v1.6-1.9): Maintain both APIs, warn on old API
              ↓
Step 3 (v2.0-rc): Release candidate, community testing
              ↓
Step 4 (v2.0): Remove old API, migration guide available
```

**Example migration:**

```python
# v1.5: Announce deprecation
@deprecated(version='1.5', removal_version='2.0')
def calculate_steel(b_mm, d_mm, mu_kn_m):
    """Deprecated: Use calculate_reinforcement() instead."""
    return calculate_reinforcement(b_mm, d_mm, mu_kn_m)

def calculate_reinforcement(b_mm, d_mm, mu_kn_m):
    """Calculate required reinforcement per IS 456."""
    # Implementation
    ...

# v1.6-1.9: Both functions work, warnings appear

# v2.0: Remove old function
# calculate_steel() no longer exists
# Only calculate_reinforcement() remains
```

### 5.3 Breaking Change Checklist

**Before making a breaking change:**

- [ ] Can it be avoided with compatibility layer?
- [ ] Is the benefit worth the user cost?
- [ ] Have we documented the migration path?
- [ ] Have we announced it at least 2 minor versions early?
- [ ] Have we updated examples and tutorials?
- [ ] Have we tested the migration on real user code?

### 5.4 Batching Breaking Changes

**Don't break frequently!** Save breaking changes for major releases.

```
v1.0 → v1.1 → v1.2 → ... → v1.9 → v2.0
       ✅     ✅            ✅     🔥 ALL breaking changes here
```

**Bad practice:**
```
v1.0 → v1.1 → v1.2 → v1.3 → v1.4
       🔥     ✅     🔥     🔥
Breaking changes scattered across minor versions → user frustration
```

**Good practice:**
```
v1.0: Stable API
v1.1: Add features, announce deprecations for v2.0
v1.2: Add features, announce more deprecations
v1.3: Add features, announce more deprecations
...
v1.9: API freeze, final deprecation warnings
v2.0: Remove all deprecated items at once, clear migration guide
```

---

## 6. Version Communication

### 6.1 Release Notes Template

**CHANGELOG.md format:**

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- (Nothing yet)

### Changed
- (Nothing yet)

### Deprecated
- (Nothing yet)

### Removed
- (Nothing yet)

### Fixed
- (Nothing yet)

### Security
- (Nothing yet)

## [1.5.0] - 2026-01-15

### Added
- New function `calculate_reinforcement()` with improved parameter names
- Optional `cover_mm` parameter in `design_beam()` (#145)
- Support for M40 concrete grade in material tables (#148)

### Changed
- `design_beam()` now accepts `cover_mm` as optional parameter
  (defaults to IS 456 values if not specified)

### Deprecated
- `calculate_steel()` is deprecated in favor of `calculate_reinforcement()`.
  Will be removed in v2.0. Use `calculate_reinforcement()` instead. (#147)
- Parameter `b_mm` in `design_beam()` is deprecated in favor of `width_mm`.
  Will be removed in v2.0. Both names work in v1.x for backward compatibility.

### Fixed
- Fixed incorrect ast_min calculation for Fe 550 steel (#146)
- Fixed rounding error in development length calculation (#149)

### Migration Guide (for deprecated items)

```python
# Before (v1.4):
ast = calculate_steel(b_mm=300, d_mm=550, mu_kn_m=180)

# After (v1.5+):
ast = calculate_reinforcement(b_mm=300, d_mm=550, mu_kn_m=180)

# Old code still works but shows deprecation warning
```

[1.5.0]: https://github.com/owner/repo/compare/v1.4.0...v1.5.0
```

### 6.2 GitHub Release Description

**For each release, create GitHub Release with:**

```markdown
## 🚀 Highlights

Brief summary of major features and improvements in this release.

## ✨ What's New

### New Features
- Feature 1 with brief description (#123)
- Feature 2 with brief description (#124)

### Improvements
- Improvement 1 (#125)
- Improvement 2 (#126)

## ⚠️ Deprecations

The following items are deprecated and will be removed in v2.0:

- `calculate_steel()` → Use `calculate_reinforcement()` instead
- `design_beam(b_mm=...)` → Use `design_beam(width_mm=...)` instead

See the migration guide (planned) for details.

## 🐛 Bug Fixes

- Fixed issue 1 (#127)
- Fixed issue 2 (#128)

## 📖 Documentation

- Added tutorial for X (#129)
- Updated API reference for Y (#130)

## 🙏 Contributors

Thank you to everyone who contributed to this release!

- @contributor1
- @contributor2

## 📦 Installation

```bash
pip install --upgrade structural-lib-is456==1.5.0
```

**Full Changelog**: https://github.com/owner/repo/compare/v1.4.0...v1.5.0
```

### 6.3 Deprecation Warnings in Code

**Make warnings actionable:**

```python
# ❌ BAD: Vague warning
warnings.warn("This function is deprecated")

# ✅ GOOD: Specific, actionable warning
warnings.warn(
    "calculate_steel() is deprecated since v1.5 and will be removed in v2.0. "
    "Use calculate_reinforcement() instead. "
    "See https://docs.example.com/migration for details.",
    DeprecationWarning,
    stacklevel=2,
)
```

**User sees:**
```
DeprecationWarning: calculate_steel() is deprecated since v1.5
and will be removed in v2.0. Use calculate_reinforcement() instead.
See https://docs.example.com/migration for details.
  at my_code.py:42
```

### 6.4 Migration Guides

**Create dedicated migration guides for major versions:**

```markdown
# Migration Guide: v1.x → v2.0

This guide helps you migrate from v1.x to v2.0.

## Summary of Breaking Changes

v2.0 removes all items deprecated in v1.5-1.9. This includes:

1. Removed functions
2. Removed parameters
3. Changed defaults
4. Changed return types

## Detailed Migration

### 1. Function Renames

#### calculate_steel() → calculate_reinforcement()

**What changed:** Function was renamed for clarity.

**Before (v1.x):**
```python
ast = calculate_steel(b_mm=300, d_mm=550, mu_kn_m=180)
```

**After (v2.0):**
```python
ast = calculate_reinforcement(b_mm=300, d_mm=550, mu_kn_m=180)
```

**Search & replace:**
```bash
# Find all occurrences
grep -r "calculate_steel" .

# Replace (GNU sed)
sed -i 's/calculate_steel/calculate_reinforcement/g' *.py
```

### 2. Parameter Renames

#### design_beam(b_mm=...) → design_beam(width_mm=...)

**What changed:** Parameter renamed for explicitness.

**Before (v1.x):**
```python
result = design_beam(b_mm=300, d_mm=550, mu_kn_m=180)
```

**After (v2.0):**
```python
result = design_beam(width_mm=300, d_mm=550, mu_kn_m=180)
```

### 3. Validation Now Mandatory

**What changed:** `validate=False` parameter removed. All inputs are validated.

**Before (v1.x):**
```python
# Skip validation for speed
result = design_beam(..., validate=False)
```

**After (v2.0):**
```python
# Validation always runs (no flag)
result = design_beam(...)

# If you were skipping validation because inputs are pre-validated,
# remove the validate=False parameter. Validation is fast (~13% overhead).
```

## Automated Migration Tool

We provide a migration tool to automate most changes:

```bash
# Install tool
pip install structural-lib-migrate

# Run migration (creates backup)
structural-lib-migrate v1-to-v2 my_project/

# Review changes, then commit
```

## Need Help?

- Read the FAQ (planned)
- Ask on GitHub Discussions (planned)
- Report migration issues via GitHub Issues (planned)
```

### 6.5 Communicating Pre-Release

**Before v1.0 (current state):**

```markdown
# README.md

## ⚠️ Pre-1.0 Notice

This library is in active development (currently v0.15.x).

**What this means:**
- ✅ Core functionality is stable and tested
- ✅ We use the library in production
- ⚠️ API may change between 0.x versions (but we minimize this)
- ⚠️ Follow SemVer for 1.0+, but 0.x allows breaking changes

**When will 1.0 release?**
- Target: Q2 2026
- Requirements: Complete API review, user feedback, documentation polish

**Should I use this now?**
- Yes, if you can tolerate occasional API changes (with migration guides)
- Pin versions in production: `structural-lib-is456>=0.15,<0.16`
```

---

## 7. Migration Tools & Helpers

### 7.1 Automated Migration Script

**Tool to help users migrate code:**

```python
# tools/migrate_v1_to_v2.py
"""Automated migration tool for v1.x → v2.0.

Usage:
    python migrate_v1_to_v2.py my_project/

This tool automates most migration tasks:
1. Renames deprecated functions
2. Renames deprecated parameters
3. Updates import statements
4. Removes validate=False parameters

Always review changes before committing!
"""

import re
import argparse
from pathlib import Path
from typing import List, Tuple

# Migration rules
FUNCTION_RENAMES = {
    'calculate_steel': 'calculate_reinforcement',
    'design_beam_old': 'design_beam',
}

PARAMETER_RENAMES = {
    'b_mm': 'width_mm',
    'd_mm': 'depth_mm',
}

def migrate_function_names(content: str) -> Tuple[str, int]:
    """Replace deprecated function names."""
    changes = 0
    for old, new in FUNCTION_RENAMES.items():
        pattern = rf'\b{old}\b'
        new_content, count = re.subn(pattern, new, content)
        content = new_content
        changes += count
    return content, changes

def migrate_parameter_names(content: str) -> Tuple[str, int]:
    """Replace deprecated parameter names."""
    changes = 0
    for old, new in PARAMETER_RENAMES.items():
        # Match parameter in function call: old=value
        pattern = rf'\b{old}\s*='
        new_content, count = re.subn(pattern, f'{new}=', content)
        content = new_content
        changes += count
    return content, changes

def remove_validate_false(content: str) -> Tuple[str, int]:
    """Remove validate=False parameters."""
    # Match validate=False (with optional spaces)
    patterns = [
        r',\s*validate\s*=\s*False',  # In middle of params
        r'validate\s*=\s*False\s*,',  # At start of params
        r'\(\s*validate\s*=\s*False\s*\)',  # Only param
    ]
    changes = 0
    for pattern in patterns:
        new_content, count = re.subn(pattern, '', content)
        content = new_content
        changes += count
    return content, changes

def migrate_file(filepath: Path, dry_run: bool = False) -> dict:
    """Migrate a single Python file."""
    content = filepath.read_text()
    original = content

    results = {
        'functions': 0,
        'parameters': 0,
        'validate': 0,
    }

    # Apply migrations
    content, results['functions'] = migrate_function_names(content)
    content, results['parameters'] = migrate_parameter_names(content)
    content, results['validate'] = remove_validate_false(content)

    total_changes = sum(results.values())

    if total_changes > 0 and not dry_run:
        # Backup original
        backup = filepath.with_suffix('.py.bak')
        backup.write_text(original)

        # Write migrated version
        filepath.write_text(content)

    return results

def migrate_project(project_dir: Path, dry_run: bool = False):
    """Migrate all Python files in project."""
    python_files = list(project_dir.rglob('*.py'))

    print(f"Found {len(python_files)} Python files in {project_dir}")
    if dry_run:
        print("DRY RUN: No files will be modified\n")
    else:
        print("Migrating files...\n")

    total_results = {
        'functions': 0,
        'parameters': 0,
        'validate': 0,
    }

    for filepath in python_files:
        results = migrate_file(filepath, dry_run)
        if sum(results.values()) > 0:
            print(f"✓ {filepath.relative_to(project_dir)}")
            print(f"  Functions: {results['functions']}")
            print(f"  Parameters: {results['parameters']}")
            print(f"  Validate flags: {results['validate']}")

            for key in total_results:
                total_results[key] += results[key]

    print(f"\nTotal changes:")
    print(f"  Function renames: {total_results['functions']}")
    print(f"  Parameter renames: {total_results['parameters']}")
    print(f"  Validate=False removed: {total_results['validate']}")

    if not dry_run:
        print(f"\n✓ Migration complete! Backup files saved as *.py.bak")
        print(f"Review changes, test your code, then delete backups.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migrate v1.x code to v2.0')
    parser.add_argument('project_dir', type=Path, help='Project directory to migrate')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without modifying files')

    args = parser.parse_args()

    if not args.project_dir.is_dir():
        print(f"Error: {args.project_dir} is not a directory")
        exit(1)

    migrate_project(args.project_dir, dry_run=args.dry_run)
```

**Usage:**

```bash
# Dry run (preview changes)
python migrate_v1_to_v2.py my_project/ --dry-run

# Actual migration
python migrate_v1_to_v2.py my_project/

# Review changes
git diff

# Test
pytest tests/

# Commit if all passes
git commit -am "Migrate to v2.0 API"
```

### 7.2 Compatibility Shims

**Provide backward compatibility layers:**

```python
# structural_lib/compat.py
"""Backward compatibility shims for v1.x users.

Import from this module to use v1.x API with v2.0 library:

    from structural_lib.compat import calculate_steel

This allows gradual migration without breaking existing code.
"""

import warnings
from structural_lib import calculate_reinforcement

def calculate_steel(*args, **kwargs):
    """Compatibility shim for v1.x calculate_steel().

    .. deprecated:: 2.0
        This is a compatibility shim. Use calculate_reinforcement()
        from the main API instead.
    """
    warnings.warn(
        "Using compatibility shim for calculate_steel(). "
        "Migrate to calculate_reinforcement() from main API. "
        "This shim may be removed in v3.0.",
        DeprecationWarning,
        stacklevel=2,
    )
    return calculate_reinforcement(*args, **kwargs)

# Add more shims as needed...
```

**User can import from compat module:**

```python
# v1.x code (still works in v2.0)
from structural_lib.compat import calculate_steel

ast = calculate_steel(b_mm=300, d_mm=550, mu_kn_m=180)
# Works but shows deprecation warning

# Gradual migration:
# 1. Use compat module to unblock v2.0 upgrade
# 2. Migrate code incrementally
# 3. Remove compat imports before v3.0
```

### 7.3 Version Detection Helper

**Help users detect version incompatibilities:**

```python
# structural_lib/__version__.py
__version__ = '2.0.0'

def require_version(min_version: str, max_version: str = None):
    """Ensure library version is compatible.

    Args:
        min_version: Minimum required version (inclusive)
        max_version: Maximum required version (exclusive), optional

    Raises:
        RuntimeError: If version is incompatible

    Example:
        >>> from structural_lib import require_version
        >>> require_version('1.5', '2.0')  # Requires 1.5 ≤ version < 2.0
    """
    from packaging import version

    current = version.parse(__version__)
    min_ver = version.parse(min_version)

    if current < min_ver:
        raise RuntimeError(
            f"structural_lib {__version__} is too old. "
            f"Requires >={min_version}. "
            f"Upgrade with: pip install --upgrade structural-lib-is456"
        )

    if max_version:
        max_ver = version.parse(max_version)
        if current >= max_ver:
            raise RuntimeError(
                f"structural_lib {__version__} is too new. "
                f"Requires <{max_version}. "
                f"Your code may need migration. "
                f"See https://docs.example.com/migration"
            )
```

**Users can add version checks:**

```python
# At top of their script
from structural_lib import require_version

# Ensure compatible version
require_version('1.5', '2.0')  # Works with 1.5-1.x only

# Rest of script uses v1.x API safely
```

---

## 8. API Lifecycle Management

### 8.1 API Stability Levels

**Mark API stability explicitly:**

```python
# Stable API (1.0+ contract)
def design_beam(...):
    """Design beam section per IS 456.

    **Stability: Stable** - This API is covered by semantic versioning.
    Breaking changes will only occur in major releases.
    """
    ...

# Experimental API (may change)
def optimize_topology(...):
    """Experimental topology optimization.

    **Stability: Experimental** - This API may change in minor releases.
    Not recommended for production use.

    .. versionadded:: 1.5
        Experimental feature
    """
    warnings.warn(
        "optimize_topology() is experimental and may change",
        FutureWarning,
    )
    ...

# Internal API (no guarantees)
def _internal_helper(...):
    """Internal helper function.

    **Stability: Internal** - This is a private API with no stability
    guarantees. Do not use directly.
    """
    ...
```

### 8.2 Feature Flags

**Use flags to test new behavior:**

```python
# Introduce new behavior behind flag
def calculate_ast_required(
    ...,
    *,
    use_exact_formula: bool = False,  # New behavior
):
    """Calculate required steel area.

    Args:
        use_exact_formula: If True, use exact iterative formula.
            If False (default), use simplified formula.
            **Note:** Default will change to True in v2.0.
    """
    if use_exact_formula:
        # New exact formula
        return _calculate_exact(...)
    else:
        # Old simplified formula
        warnings.warn(
            "Simplified formula is deprecated. "
            "Set use_exact_formula=True for exact calculation. "
            "This will become the default in v2.0.",
            FutureWarning,
        )
        return _calculate_simplified(...)

# v2.0: Change default
def calculate_ast_required(..., use_exact_formula: bool = True):
    ...
```

### 8.3 API Review Process

**Before each release:**

1. **API Audit**: Review all public functions for consistency
2. **Deprecation Review**: Check deprecation timeline (ready to remove?)
3. **Breaking Change Analysis**: Document impact of any breaks
4. **Documentation Update**: Update all docs for changes
5. **Migration Guide**: Write guide for major versions
6. **Community Review**: Get feedback on breaking changes
7. **Release Candidate**: Test in real projects

**Checklist template:**

```markdown
# v2.0 Release Checklist

## API Review
- [ ] All deprecated items removed
- [ ] All new functions documented
- [ ] Type hints complete
- [ ] Examples updated

## Documentation
- [ ] CHANGELOG.md updated
- [ ] Migration guide written
- [ ] API reference regenerated
- [ ] Tutorials updated

## Testing
- [ ] All tests pass
- [ ] Migration tool tested
- [ ] Breaking changes tested
- [ ] Release candidate published

## Communication
- [ ] Deprecation warnings clear
- [ ] GitHub release drafted
- [ ] Migration guide published
- [ ] Community notified
```

### 8.4 Long-Term Support (LTS)

**For critical users who can't upgrade frequently:**

```
v1.0 ────────────────────────→ v1.9 (LTS: 2 years)
      \                              ↑
       \                             │
        v2.0 ──────→ v2.9 (LTS: 2 years)
                      \
                       \
                        v3.0 ──→ ...
```

**LTS policy:**
- **Regular releases**: Bug fixes for 6 months after next major
- **LTS releases**: Bug fixes for 2 years
- **Security fixes**: All supported versions

**Example:**
```
v1.9 LTS released: 2026-03-01
v2.0 released: 2026-06-01
v1.9 support:
  - Bug fixes: Until 2026-12-01 (6 months after v2.0)
  - Security fixes: Until 2028-03-01 (2 years)
```

---

## Appendix A: Quick Reference Card

### Deprecation Checklist

**When deprecating a function:**
- [ ] Add `@deprecated()` decorator with version numbers
- [ ] Update docstring with deprecation notice
- [ ] Add entry to CHANGELOG.md "Deprecated" section
- [ ] Add to deprecation timeline in docs
- [ ] Provide clear replacement/migration instructions
- [ ] Test that deprecation warning appears
- [ ] Wait minimum 2 minor versions before removal

### Breaking Change Checklist

**When making a breaking change:**
- [ ] Justify: Is it worth breaking user code?
- [ ] Announce: Deprecate in advance (≥2 minor versions)
- [ ] Document: Write migration guide
- [ ] Automate: Provide migration script if possible
- [ ] Communicate: Update CHANGELOG, release notes, docs
- [ ] Test: Verify on real user code
- [ ] Batch: Save for major release (don't scatter)

### Release Checklist

**For each release:**
- [ ] Update version in `__version__.py`
- [ ] Update CHANGELOG.md with version and date
- [ ] Tag release in git: `git tag v1.5.0`
- [ ] Build distributions: `python -m build`
- [ ] Test upload: `twine upload --repository testpypi dist/*`
- [ ] Upload to PyPI: `twine upload dist/*`
- [ ] Create GitHub Release with notes
- [ ] Announce on communication channels

### Version Number Decision Tree

```
Is this a bug fix?
├─ Yes → Patch bump (1.5.2 → 1.5.3)
└─ No
   ├─ Are we adding features (backward compatible)?
   │  └─ Yes → Minor bump (1.5.3 → 1.6.0)
   └─ Are we making breaking changes?
      └─ Yes → Major bump (1.9.0 → 2.0.0)
```

---

## Appendix B: Real-World Examples

### Example 1: NumPy's Matrix Deprecation

**Scenario:** NumPy deprecated `np.matrix` in favor of regular arrays.

**Timeline:**
- v1.15 (2018): Announced deprecation
- v1.15-1.19: Warnings shown, still works
- v1.20 (2021): Removed (3 years later!)

**Lesson:** Long deprecation cycle (3 years) for widely-used API.

### Example 2: Django's url() → path()

**Scenario:** Django renamed `url()` to `path()` with simpler syntax.

**Approach:**
- Kept both functions for 2 years
- Provided automatic conversion tool
- Clear migration guide
- Gradual adoption (not forced)

**Lesson:** Provide both old and new, give users time.

### Example 3: Pandas' append() Removal

**Scenario:** Pandas removed `DataFrame.append()` (inefficient).

**Approach:**
- Deprecated in v1.4 (2022)
- Recommended `pd.concat()` instead
- Removed in v2.0 (2023)
- Clear performance explanation

**Lesson:** Explain WHY change is needed (performance), not just HOW to migrate.

### Example 4: Requests' Stability Promise

**Scenario:** Requests promised no breaking changes after 1.0.

**Approach:**
- Strict SemVer since 1.0
- No breaking changes in 10+ years!
- Occasional deprecations, never forced removal
- Users trust it completely

**Lesson:** Stability builds trust. Breaking rarely is better than breaking often.

### Example 5: FastAPI's 0.x Development

**Scenario:** FastAPI stayed 0.x for 3 years while stabilizing.

**Approach:**
- Honest about 0.x = "may change"
- Documented breaking changes clearly
- Planned 1.0 when API stabilized
- Users accepted 0.x = development

**Lesson:** It's OK to stay 0.x during development, just be transparent.

---

## Summary

**Key Takeaways:**

1. **Use Semantic Versioning**: Version numbers communicate impact
2. **Deprecate Before Breaking**: Minimum 2 minor versions notice
3. **Provide Migration Paths**: Clear instructions + automation
4. **Batch Breaking Changes**: Save for major releases
5. **Communicate Clearly**: CHANGELOG, warnings, migration guides
6. **Build Trust**: Stability → user confidence → adoption

**Our Commitment:**

- **0.x (current)**: Iterating on API, minimizing breaks, warning first
- **1.0 (target)**: Stability promise, strict SemVer, long deprecation cycles
- **Future**: Breaking changes only in majors, clear migration guides always
