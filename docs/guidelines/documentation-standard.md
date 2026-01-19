# API Documentation & Discoverability Standard

**Type:** Guideline
**Audience:** Developers
**Status:** Active
**Importance:** High
**Created:** 2026-01-07
**Last Updated:** 2026-01-13

---

> **Standard for documentation, docstrings, and API discoverability**
> Part of: API Improvement Research (TASK-206)

---

## Purpose

This document establishes standards for API documentation to ensure:
- **Discoverability**: Users can find functions and understand capabilities without reading source code
- **Clarity**: Documentation explains purpose, usage, and constraints clearly
- **Completeness**: All public APIs have comprehensive, accurate documentation
- **Consistency**: Documentation follows uniform patterns and conventions

**Target audience**: Library developers writing public APIs, docstrings, and examples.

---

## Table of Contents

1. [Core Principles](#1-core-principles)
2. [Docstring Standard (Google Style)](#2-docstring-standard-google-style)
3. [Type Hints & Annotations](#3-type-hints--annotations)
4. [Example-Driven Documentation](#4-example-driven-documentation)
5. [IDE Integration & Autocomplete](#5-ide-integration--autocomplete)
6. [Module-Level Documentation](#6-module-level-documentation)
7. [API Reference Generation](#7-api-reference-generation)
8. [Error Documentation](#8-error-documentation)
9. [Code Examples Best Practices](#9-code-examples-best-practices)
10. [Documentation Testing](#10-documentation-testing)

**Appendices:**
- [A: Quick Reference Card](#appendix-a-quick-reference-card)
- [B: Docstring Templates](#appendix-b-docstring-templates)

---

## 1. Core Principles

### 1.1 The Documentation Pyramid

Good API documentation has three levels:

```
                 ┌─────────────────────┐
                 │   Quick Start       │  ← Fastest path to first success
                 │   (1 example)       │
                 └─────────────────────┘
                          ▲
                 ┌─────────────────────┐
                 │   Common Patterns   │  ← 80% of use cases
                 │   (5-10 examples)   │
                 └─────────────────────┘
                          ▲
        ┌────────────────────────────────────┐
        │   Complete Reference              │  ← Every parameter, edge case
        │   (Comprehensive API docs)        │
        └────────────────────────────────────┘
```

**Users start at the top** (quick start) and **drill down as needed** (patterns → reference).

### 1.2 The Four Questions Framework

Every function's documentation must answer:

1. **What does it do?** (One-sentence summary)
2. **When should I use it?** (Use cases, constraints)
3. **How do I use it?** (Parameters, returns, examples)
4. **What can go wrong?** (Exceptions, edge cases, validation)

### 1.3 Write for Three Audiences

| Audience | Needs | Documentation Focus |
|----------|-------|---------------------|
| **Beginner** | Getting started, common patterns | Quick examples, clear explanations, avoid jargon |
| **Intermediate** | Solving specific problems | Use cases, parameter options, common pitfalls |
| **Expert** | Edge cases, performance, internals | Full parameter details, constraints, performance notes |

### 1.4 Documentation as Code

- **Docstrings are part of the API contract** (not optional comments)
- **Examples must be runnable** (tested with doctest or pytest)
- **Documentation failures = code failures** (CI enforces completeness)
- **Keep docs close to code** (docstrings > separate markdown files)

---

## 2. Docstring Standard (Google Style)

### 2.1 Why Google Style?

**Chosen over NumPy/Sphinx styles because:**
- ✅ More readable in plain text (no excessive formatting)
- ✅ Works well with type hints (types in signature, not docstring)
- ✅ Better IDE support (VSCode, PyCharm parse correctly)
- ✅ Widely adopted (Pydantic, FastAPI, Google's internal codebases)

### 2.2 Function Docstring Template

```python
def design_singly_reinforced(
    b_mm: float,
    d_mm: float,
    mu_kn_m: float,
    fck_mpa: float,
    fy_mpa: float,
    *,
    validate: bool = True,
) -> FlexureResult:
    """Design singly reinforced rectangular beam section per IS 456:2000.

    Calculates required tension reinforcement for a rectangular beam section
    subjected to sagging (positive) moment. Checks minimum and maximum steel
    requirements per IS 456 Cl. 26.5.1.1.

    Args:
        b_mm: Beam width in millimeters. Must be ≥ 200mm per IS 456 Cl. 26.5.1.1.
        d_mm: Effective depth in millimeters. Distance from compression face
            to centroid of tension reinforcement.
        mu_kn_m: Factored bending moment in kilonewton-meters. Must be positive
            (sagging moment).
        fck_mpa: Characteristic compressive strength of concrete in megapascals.
            Must be one of [20, 25, 30, 35, 40, 45, 50] per IS 456 Table 2.
        fy_mpa: Characteristic yield strength of steel in megapascals.
            Must be one of [250, 415, 500, 550] per IS 456 Cl. 6.2.
        validate: If True, validate all inputs before calculation. Set to False
            for batch operations where inputs are pre-validated. Default: True.

    Returns:
        FlexureResult with fields:
            - ast_required_mm2: Required tension steel area (mm²)
            - ast_min_mm2: Minimum steel per IS 456 Cl. 26.5.1.1
            - ast_max_mm2: Maximum steel per IS 456 Cl. 26.5.1.1
            - mu_lim_kn_m: Section capacity with xu = xu,max
            - reinforcement_ratio: Ast / (b × d)

    Raises:
        DimensionError: If b_mm < 200mm or d_mm < 150mm
        MaterialError: If fck_mpa or fy_mpa not in standard grades
        LoadError: If mu_kn_m ≤ 0
        DesignError: If mu_kn_m > mu_lim (requires compression steel)
        ComplianceError: If ast_required < ast_min or ast_required > ast_max

    Example:
        >>> from structural_lib import design_singly_reinforced
        >>> result = design_singly_reinforced(
        ...     b_mm=300,
        ...     d_mm=550,
        ...     mu_kn_m=180,
        ...     fck_mpa=30,
        ...     fy_mpa=415,
        ... )
        >>> print(f"Required steel: {result.ast_required_mm2:.0f} mm²")
        Required steel: 1245 mm²

    Note:
        For doubly reinforced sections (compression steel required), use
        design_doubly_reinforced() instead. This function assumes xu ≤ xu,max.

    See Also:
        - design_doubly_reinforced: For sections requiring compression steel
        - calculate_mu_lim: To check section capacity before design
        - FlexureResult: Complete documentation of result object

    References:
        IS 456:2000 Clauses:
        - Cl. 38.1: Limiting depth of neutral axis
        - Cl. 26.5.1.1: Minimum and maximum reinforcement
        - Cl. G-1.1: Design equations (Annex G)
    """
    # Implementation...
```

### 2.3 Docstring Section Rules

#### Summary Line (Required)

**Rules:**
- First line, one sentence, imperative mood ("Calculate" not "Calculates")
- End with period
- < 80 characters
- Describes WHAT the function does, not implementation details

```python
# ✅ GOOD: Clear, actionable, < 80 chars
"""Design singly reinforced beam section per IS 456:2000."""

# ❌ BAD: Too long, passive voice, implementation detail
"""This function is used to calculate the required area of steel reinforcement
for a singly reinforced rectangular beam section using the limit state design
method as specified in IS 456:2000."""

# ❌ BAD: Not imperative mood
"""Designs a beam section."""  # "Design" not "Designs"
```

#### Description (Optional but Recommended)

**When to include:**
- Function is not obvious from name
- Need to explain use cases or context
- Important constraints or assumptions

**Keep it brief:** 2-4 sentences maximum.

```python
"""Design singly reinforced rectangular beam section per IS 456:2000.

Calculates required tension reinforcement for a rectangular beam section
subjected to sagging (positive) moment. Checks minimum and maximum steel
requirements per IS 456 Cl. 26.5.1.1.
"""
```

#### Args Section (Required for functions with parameters)

**Format:**
```
Args:
    param_name: Description. Constraints/units/defaults.
        Additional context on second line (indented).
    another_param: Description...
```

**Rules:**
- List ALL parameters (required + optional)
- Describe constraints (ranges, valid values, units)
- Explain optional parameters and defaults
- Multi-line descriptions indent second+ lines
- Don't repeat type (already in signature)

```python
"""
Args:
    b_mm: Beam width in millimeters. Must be ≥ 200mm per IS 456 Cl. 26.5.1.1.
    d_mm: Effective depth in millimeters. Distance from compression face
        to centroid of tension reinforcement.
    fck_mpa: Characteristic compressive strength of concrete in megapascals.
        Must be one of [20, 25, 30, 35, 40, 45, 50] per IS 456 Table 2.
    validate: If True, validate all inputs before calculation. Set to False
        for batch operations where inputs are pre-validated. Default: True.
"""
```

#### Returns Section (Required for functions that return)

**Format:**
```
Returns:
    Type: Description of what is returned.
        Additional details (fields, structure).
```

**Rules:**
- Describe the return value, not the type (type is in signature)
- For dataclasses/objects: List key fields
- For simple types: Describe value and units

```python
"""
Returns:
    FlexureResult with fields:
        - ast_required_mm2: Required tension steel area (mm²)
        - ast_min_mm2: Minimum steel per IS 456 Cl. 26.5.1.1
        - ast_max_mm2: Maximum steel per IS 456 Cl. 26.5.1.1
        - mu_lim_kn_m: Section capacity with xu = xu,max
        - reinforcement_ratio: Ast / (b × d)
"""

# For simple returns:
"""
Returns:
    Limiting moment capacity in kN·m. This is the maximum moment the
    section can resist with xu = xu,max per IS 456 Cl. 38.1.
"""
```

#### Raises Section (Required if function raises exceptions)

**Format:**
```
Raises:
    ExceptionType: When this exception is raised. Conditions.
    AnotherException: When this is raised.
```

**Rules:**
- List ALL exception types the function can raise
- Explain WHEN each exception is raised
- Order by likelihood (most common first)

```python
"""
Raises:
    DimensionError: If b_mm < 200mm or d_mm < 150mm
    MaterialError: If fck_mpa or fy_mpa not in standard grades
    LoadError: If mu_kn_m ≤ 0
    DesignError: If mu_kn_m > mu_lim (requires compression steel)
    ComplianceError: If ast_required < ast_min or ast_required > ast_max
"""
```

#### Example Section (Highly Recommended)

**Rules:**
- Show REALISTIC usage (not toy examples)
- Use doctest format (>>> prompts)
- Must be runnable (tested in CI)
- Show imports if not obvious
- Include expected output

```python
"""
Example:
    >>> from structural_lib import design_singly_reinforced
    >>> result = design_singly_reinforced(
    ...     b_mm=300,
    ...     d_mm=550,
    ...     mu_kn_m=180,
    ...     fck_mpa=30,
    ...     fy_mpa=415,
    ... )
    >>> print(f"Required steel: {result.ast_required_mm2:.0f} mm²")
    Required steel: 1245 mm²
"""
```

#### Note Section (Optional)

**When to use:**
- Important caveats or assumptions
- Performance considerations
- Behavioral quirks

```python
"""
Note:
    For doubly reinforced sections (compression steel required), use
    design_doubly_reinforced() instead. This function assumes xu ≤ xu,max.

    Performance: For batch operations with 1000+ beams, set validate=False
    and pre-validate inputs to save ~13% execution time.
"""
```

#### See Also Section (Optional)

**When to use:**
- Related functions users might need
- Alternative approaches
- Prerequisite or follow-up functions

```python
"""
See Also:
    - design_doubly_reinforced: For sections requiring compression steel
    - calculate_mu_lim: To check section capacity before design
    - FlexureResult: Complete documentation of result object
"""
```

#### References Section (Optional but Recommended for engineering functions)

**When to use:**
- Code clause references (IS 456, ACI, Eurocode)
- Research papers
- Standard design procedures

```python
"""
References:
    IS 456:2000 Clauses:
    - Cl. 38.1: Limiting depth of neutral axis
    - Cl. 26.5.1.1: Minimum and maximum reinforcement
    - Cl. G-1.1: Design equations (Annex G)
"""
```

---

## 3. Type Hints & Annotations

### 3.1 Type Hints as Documentation

**Type hints ARE documentation** - they appear in IDE tooltips and help users understand parameter types.

```python
# ✅ GOOD: Clear types, users know what to pass
def design_beam(
    b_mm: float,
    d_mm: float,
    mu_kn_m: float,
    fck_mpa: float,
    fy_mpa: float,
) -> FlexureResult:
    ...

# ❌ BAD: No types, users must guess
def design_beam(b_mm, d_mm, mu_kn_m, fck_mpa, fy_mpa):
    ...
```

### 3.2 Advanced Type Annotations

**Use Union for alternative types:**
```python
from typing import Union

def get_reinforcement(
    ast_mm2: float,
    bar_dia_mm: Union[int, list[int]] = 16,  # Single size or multiple
) -> BarArrangement:
    """Get bar arrangement for required steel area.

    Args:
        ast_mm2: Required steel area in mm²
        bar_dia_mm: Bar diameter(s) in mm. Can be single diameter (e.g., 16)
            or list of allowed diameters (e.g., [12, 16, 20]). Default: 16.
    """
```

**Use Literal for constrained choices:**
```python
from typing import Literal

def calculate_stress_block_factor(
    fck_mpa: float,
    code: Literal['IS456', 'ACI318', 'EC2'] = 'IS456',
) -> float:
    """Calculate stress block factor α per design code.

    Args:
        fck_mpa: Concrete strength in MPa
        code: Design code to use. One of 'IS456', 'ACI318', 'EC2'. Default: 'IS456'.
    """
```

**Use Optional for None defaults:**
```python
from typing import Optional

def design_beam(
    ...,
    cover_mm: Optional[float] = None,  # None = use default
) -> FlexureResult:
    """Design beam section.

    Args:
        cover_mm: Clear cover in mm. If None, uses default per IS 456 Table 16
            (25mm for beams in mild exposure). Default: None.
    """
```

### 3.3 Return Type Documentation

**Always annotate return types:**
```python
def calculate_mu_lim(b_mm: float, d_mm: float, fck_mpa: float) -> float:
    """Calculate limiting moment capacity.

    Returns:
        Limiting moment in kN·m.
    """
    # IDE shows: calculate_mu_lim(...) -> float
```

**For complex returns, use dataclasses:**
```python
@dataclass(frozen=True)
class FlexureResult:
    """Result of flexural design calculation."""
    ast_required_mm2: float
    ast_min_mm2: float
    ast_max_mm2: float
    mu_lim_kn_m: float
    reinforcement_ratio: float

def design_flexure(...) -> FlexureResult:
    """Design flexure.

    Returns:
        FlexureResult with design outputs.
    """
    # IDE shows all fields when user types `result.`
```

---

## 4. Example-Driven Documentation

### 4.1 The Power of Examples

**Users learn from examples, not parameter descriptions.** A single realistic example is worth 100 words of explanation.

**Research finding**: Developers prefer example-driven docs over reference docs (Stack Overflow study, 2018).

### 4.2 Example Hierarchy

Every function should have 1-3 examples at different complexity levels:

```
Level 1: "Hello World" (simplest possible usage)
         ↓
Level 2: Realistic Use Case (common pattern with context)
         ↓
Level 3: Advanced Usage (edge cases, options, error handling)
```

**Example progression:**

```python
def design_singly_reinforced(...) -> FlexureResult:
    """Design singly reinforced beam section.

    Example:
        Basic usage (most common case):

        >>> result = design_singly_reinforced(
        ...     b_mm=300, d_mm=550, mu_kn_m=180,
        ...     fck_mpa=30, fy_mpa=415
        ... )
        >>> print(f"Required steel: {result.ast_required_mm2:.0f} mm²")
        Required steel: 1245 mm²

        Realistic engineering context:

        >>> # G+Q moment on 6m simply supported beam
        >>> beam = BeamInput(span_m=6, b_mm=300, d_mm=550)
        >>> loads = LoadCase(dead_kn_m=10, live_kn_m=8)
        >>> mu_kn_m = (1.5 * loads.dead_kn_m + 1.5 * loads.live_kn_m) * beam.span_m**2 / 8
        >>> result = design_singly_reinforced(
        ...     b_mm=beam.b_mm, d_mm=beam.d_mm, mu_kn_m=mu_kn_m,
        ...     fck_mpa=30, fy_mpa=415
        ... )

        Error handling (when design fails):

        >>> try:
        ...     result = design_singly_reinforced(
        ...         b_mm=300, d_mm=550, mu_kn_m=500,  # Too high!
        ...         fck_mpa=30, fy_mpa=415
        ...     )
        ... except DesignError as e:
        ...     print(f"Design failed: {e}")
        ...     print(f"Suggestion: {e.suggestion}")
        Design failed: Moment 500 kN·m exceeds mu_lim 245 kN·m
        Suggestion: Increase section depth or use compression steel
    """
```

### 4.3 Example Best Practices

**DO:**
- ✅ Use realistic values (not foo=1, bar=2)
- ✅ Show imports if not obvious
- ✅ Include expected output
- ✅ Show error handling for critical cases
- ✅ Add context comments ("G+Q moment on 6m beam")

**DON'T:**
- ❌ Use toy examples (b=1, d=2) - not helpful
- ❌ Assume users know all imports
- ❌ Skip expected output (users need to verify)
- ❌ Only show success cases (errors happen!)
- ❌ Write examples that don't run

### 4.4 Doctest vs Manual Examples

**Use doctest for:**
- Simple, deterministic examples
- Examples that should always work (smoke tests)
- Return value demonstrations

**Use manual examples (not tested) for:**
- Examples requiring external files
- Examples with non-deterministic output
- Long examples that would clutter docstring

```python
"""
Example:
    >>> result = calculate_mu_lim(b_mm=300, d_mm=550, fck_mpa=30)
    >>> print(f"{result:.1f}")
    245.3
"""

# vs

"""
Example (not tested):

    # Load beam geometry from Excel
    df = pd.read_excel("beams.xlsx")
    for row in df.itertuples():
        result = design_singly_reinforced(...)
        # Process results...
"""
```

---

## 5. IDE Integration & Autocomplete

### 5.1 IDE-Friendly Function Signatures

**IDEs show function signatures in tooltips.** Design signatures for readability:

```python
# ✅ GOOD: Clear parameter names, IDE shows helpful tooltip
def design_singly_reinforced(
    b_mm: float,
    d_mm: float,
    mu_kn_m: float,
    fck_mpa: float,
    fy_mpa: float,
    *,
    validate: bool = True,
) -> FlexureResult:
    # IDE shows:
    # design_singly_reinforced(
    #     b_mm: float,
    #     d_mm: float,
    #     mu_kn_m: float,
    #     fck_mpa: float,
    #     fy_mpa: float,
    #     *,
    #     validate: bool = True
    # ) -> FlexureResult

# ❌ BAD: Cryptic names, unhelpful tooltip
def design(b, d, m, fc, fy, v=True):
    # IDE shows: design(b, d, m, fc, fy, v=True)
    # User has no idea what parameters mean!
```

### 5.2 Keyword-Only Parameters

**Use `*` to force keyword arguments** for readability and safety:

```python
def design_singly_reinforced(
    b_mm: float,
    d_mm: float,
    mu_kn_m: float,
    fck_mpa: float,
    fy_mpa: float,
    *,  # ← Everything after this is keyword-only
    validate: bool = True,
    cover_mm: Optional[float] = None,
) -> FlexureResult:
    """Design beam section.

    Args:
        b_mm: Beam width (mm)
        d_mm: Effective depth (mm)
        mu_kn_m: Factored moment (kN·m)
        fck_mpa: Concrete strength (MPa)
        fy_mpa: Steel yield strength (MPa)
        validate: Validate inputs before calculation. Default: True.
        cover_mm: Clear cover (mm). If None, uses IS 456 defaults. Default: None.
    """

# Forces readable call:
result = design_singly_reinforced(
    b_mm=300,
    d_mm=550,
    mu_kn_m=180,
    fck_mpa=30,
    fy_mpa=415,
    validate=False,  # Must use keyword
)

# Prevents cryptic call:
# result = design_singly_reinforced(300, 550, 180, 30, 415, False)  # ERROR!
```

### 5.3 Autocomplete-Friendly Naming

**IDEs autocomplete based on prefix.** Group related functions with common prefixes:

```python
# ✅ GOOD: Common prefix, autocomplete shows all flexure functions
calculate_mu_lim(...)
calculate_ast_required(...)
calculate_ast_min(...)
calculate_ast_max(...)
# User types "calculate_" and sees all options

# ✅ GOOD: Verb-first for discoverability
design_singly_reinforced(...)
design_doubly_reinforced(...)
design_shear(...)
# User types "design_" and sees all design functions

# ❌ BAD: No common prefix, hard to discover
mu_lim_calculation(...)
required_ast(...)
get_min_steel(...)
steel_max(...)
# User has no idea what exists!
```

### 5.4 VSCode IntelliSense Optimization

**VSCode shows:**
1. Function signature (from type hints)
2. First line of docstring (summary)
3. Full docstring on hover

**Optimize for this:**
```python
def calculate_mu_lim(b_mm: float, d_mm: float, fck_mpa: float) -> float:
    """Calculate limiting moment capacity per IS 456 Cl. 38.1.

    Returns maximum moment the section can resist with xu = xu,max.
    Used to check if compression steel is required.

    Args:
        b_mm: Beam width in mm
        d_mm: Effective depth in mm
        fck_mpa: Concrete strength in MPa

    Returns:
        Limiting moment capacity in kN·m
    """

# VSCode shows in autocomplete:
#   calculate_mu_lim(b_mm: float, d_mm: float, fck_mpa: float) -> float
#   Calculate limiting moment capacity per IS 456 Cl. 38.1.
```

### 5.5 PyCharm Quick Documentation

**PyCharm renders docstrings as formatted documentation** (Ctrl+Q / Cmd+J):

- Renders **Args**, **Returns**, **Raises** sections
- Shows **type hints** next to parameters
- Formats **code blocks** and **lists**

**Optimize for rendering:**
```python
"""Design singly reinforced beam section.

Calculates required tension steel for rectangular section.

Args:
    b_mm: Beam width (mm). Must be ≥ 200mm.
    d_mm: Effective depth (mm). Must be ≥ 150mm.
    mu_kn_m: Factored moment (kN·m). Must be > 0.

Returns:
    FlexureResult with fields:
        - ast_required_mm2: Required steel area (mm²)
        - ast_min_mm2: Minimum steel (mm²)
        - mu_lim_kn_m: Section capacity (kN·m)

Raises:
    DimensionError: If b_mm or d_mm below minimum
    DesignError: If mu_kn_m > mu_lim

Example:
    >>> result = design_singly_reinforced(
    ...     b_mm=300, d_mm=550, mu_kn_m=180,
    ...     fck_mpa=30, fy_mpa=415
    ... )
"""
# PyCharm renders this beautifully with proper formatting
```

---

## 6. Module-Level Documentation

### 6.1 Module Docstring Template

Every module should have a docstring explaining its purpose and contents:

```python
"""Flexural design functions for RC beam sections per IS 456:2000.

This module provides functions for:
- Singly reinforced section design (tension steel only)
- Doubly reinforced section design (compression + tension steel)
- Limiting moment capacity calculation
- Reinforcement ratio checks (min/max per IS 456 Cl. 26.5.1.1)

Key Functions:
    - design_singly_reinforced: Design with tension steel only
    - design_doubly_reinforced: Design requiring compression steel
    - calculate_mu_lim: Calculate section capacity with xu = xu,max
    - calculate_ast_min: Minimum steel per IS 456 Cl. 26.5.1.1
    - calculate_ast_max: Maximum steel per IS 456 Cl. 26.5.1.1

Typical Usage:
    >>> from structural_lib import design_singly_reinforced
    >>> result = design_singly_reinforced(
    ...     b_mm=300, d_mm=550, mu_kn_m=180,
    ...     fck_mpa=30, fy_mpa=415
    ... )
    >>> print(f"Required steel: {result.ast_required_mm2:.0f} mm²")
    Required steel: 1245 mm²

References:
    IS 456:2000 Clauses:
    - Cl. 38.1: Limiting depth of neutral axis
    - Cl. 26.5.1.1: Minimum and maximum reinforcement
    - Annex G: Design aids for flexure
"""
```

### 6.2 Package-Level Documentation

Top-level `__init__.py` should document the entire package:

```python
"""structural_lib: Reinforced concrete beam design per IS 456:2000.

A Python library for structural engineering calculations following Indian
standard code IS 456:2000. Provides deterministic, well-tested functions
for flexure, shear, detailing, and serviceability design.

Core Modules:
    - flexure: Flexural design (moment capacity, reinforcement)
    - shear: Shear design (stirrup spacing, design shear strength)
    - detailing: Reinforcement detailing (curtailment, anchorage, spacing)
    - serviceability: Deflection and crack width checks
    - compliance: IS 456 code compliance validation

Quick Start:
    >>> from structural_lib import design_beam_is456
    >>> result = design_beam_is456(
    ...     span_m=6.0,
    ...     b_mm=300,
    ...     d_mm=550,
    ...     fck_mpa=30,
    ...     fy_mpa=415,
    ...     moment_kn_m=180,
    ...     shear_kn=120,
    ... )
    >>> print(result.summary())

Installation:
    pip install structural-lib-is456

Documentation:
    https://github.com/your-repo/structural_lib

License:
    MIT License - see LICENSE file
"""
```

### 6.3 Public API Declaration

Use `__all__` to explicitly declare public API:

```python
"""Flexure module."""

__all__ = [
    # Main design functions
    'design_singly_reinforced',
    'design_doubly_reinforced',

    # Calculation helpers
    'calculate_mu_lim',
    'calculate_ast_required',
    'calculate_ast_min',
    'calculate_ast_max',

    # Result objects
    'FlexureResult',
    'DoublyReinforcedResult',
]

# IDE autocomplete shows only __all__ items when user types:
# from structural_lib.flexure import <TAB>
```

---

## 7. API Reference Generation

### 7.1 Tool Selection: pdoc

**Why pdoc?**
- ✅ Generates docs directly from docstrings (no separate files)
- ✅ Supports Google-style docstrings
- ✅ Clean, readable output (HTML + markdown)
- ✅ Works with type hints
- ✅ Simple command: `pdoc structural_lib`

**Alternatives considered:**
- Sphinx: Too complex, requires separate .rst files
- MkDocs: Requires manual documentation files
- pydoc: Built-in but ugly output

### 7.2 pdoc Configuration

**pyproject.toml:**
```toml
[tool.pdoc]
# Output directory
output-dir = "docs/api"

# Show source code links
show-source = true

# Include private members starting with _
include-private = false

# Template directory (for custom styling)
template-dir = "docs/pdoc-templates"

# Footer text
footer-text = "structural_lib v{version} | IS 456:2000 Design Library"
```

### 7.3 Generating API Docs

**Command:**
```bash
# Generate HTML docs
pdoc structural_lib --output-dir docs/api

# Generate markdown docs
pdoc structural_lib --output-dir docs/api --format markdown

# Serve docs locally (auto-refresh on changes)
pdoc structural_lib
# Opens http://localhost:8080
```

### 7.4 CI Integration

**GitHub Actions workflow:**
```yaml
name: Generate API Docs

on:
  push:
    branches: [main]
    paths:
      - 'Python/structural_lib/**/*.py'

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install pdoc
        run: pip install pdoc

      - name: Generate API docs
        run: pdoc structural_lib --output-dir docs/api

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/api
```

### 7.5 Docstring Quality Checks

**Pre-commit hook to enforce docstring completeness:**

```python
# scripts/check_api_docstrings.py
"""Check that all public functions have complete docstrings."""

import ast
import sys
from pathlib import Path

def check_docstring(node: ast.FunctionDef, filepath: str) -> list[str]:
    """Check if function has complete docstring."""
    errors = []

    # Must have docstring
    docstring = ast.get_docstring(node)
    if not docstring:
        errors.append(f"{filepath}:{node.lineno}: {node.name} missing docstring")
        return errors

    # Must have summary line
    if not docstring.strip():
        errors.append(f"{filepath}:{node.lineno}: {node.name} empty docstring")

    # Must have Args section if has parameters
    if node.args.args and 'Args:' not in docstring:
        errors.append(f"{filepath}:{node.lineno}: {node.name} missing Args section")

    # Must have Returns section if returns something
    if node.returns and 'Returns:' not in docstring:
        errors.append(f"{filepath}:{node.lineno}: {node.name} missing Returns section")

    # Must have Example section
    if 'Example:' not in docstring and 'Examples:' not in docstring:
        errors.append(f"{filepath}:{node.lineno}: {node.name} missing Example section")

    return errors

# Check all Python files in structural_lib/
# Fail CI if any public function lacks complete docstring
```

---

## 8. Error Documentation

### 8.1 Documenting Exceptions

**Every exception raised must be documented** in Raises section:

```python
def design_singly_reinforced(...) -> FlexureResult:
    """Design singly reinforced section.

    Raises:
        DimensionError: If b_mm < 200mm or d_mm < 150mm (IS 456 minimums)
        MaterialError: If fck_mpa not in [20, 25, 30, 35, 40, 45, 50]
        LoadError: If mu_kn_m ≤ 0 (must be positive sagging moment)
        DesignError: If mu_kn_m > mu_lim (compression steel required)
        ComplianceError: If ast_required < ast_min or > ast_max
    """
    # Implementation raises these exceptions...
```

### 8.2 Exception Docstrings

**Every exception class needs a docstring:**

```python
class DimensionError(StructuralLibError):
    """Raised when beam dimensions violate IS 456 minimum requirements.

    Common causes:
        - Beam width (b) < 200mm
        - Effective depth (d) < 150mm
        - Span-to-depth ratio < minimum per IS 456 Cl. 23.2.1

    Resolution:
        - Increase section dimensions
        - Check that effective depth d = D - cover - stirrup_dia - bar_dia/2

    Example:
        >>> design_singly_reinforced(b_mm=150, d_mm=550, ...)
        DimensionError: Beam width 150mm < minimum 200mm per IS 456 Cl. 26.5.1.1
    """
```

### 8.3 Error Examples in Docstrings

**Show how to handle errors:**

```python
def design_singly_reinforced(...) -> FlexureResult:
    """Design singly reinforced section.

    Example:
        Handle design failure gracefully:

        >>> try:
        ...     result = design_singly_reinforced(
        ...         b_mm=300, d_mm=550, mu_kn_m=500,
        ...         fck_mpa=30, fy_mpa=415
        ...     )
        ... except DesignError as e:
        ...     print(f"Design failed: {e}")
        ...     print(f"Try: {e.suggestion}")
        ...     # Fall back to doubly reinforced design
        ...     result = design_doubly_reinforced(...)
        Design failed: Moment 500 kN·m exceeds mu_lim 245 kN·m
        Try: Increase section depth or use compression steel
    """
```

---

## 9. Code Examples Best Practices

### 9.1 Standalone Example Files

**Create runnable example scripts** in `examples/` directory:

```python
# examples/beam_design_basic.py
"""Basic beam design example using structural_lib.

Designs a simply supported beam for G+Q loading per IS 456:2000.
"""

from structural_lib import design_beam_is456, FlexureResult

def main():
    """Design a 6m simply supported beam."""

    # Input parameters
    span_m = 6.0
    b_mm = 300
    d_mm = 550
    fck_mpa = 30
    fy_mpa = 415

    # Loads
    dead_load_kn_m = 10.0  # Unfactored DL
    live_load_kn_m = 8.0   # Unfactored LL

    # Factored moment at midspan
    wu_kn_m = 1.5 * dead_load_kn_m + 1.5 * live_load_kn_m
    mu_kn_m = wu_kn_m * span_m**2 / 8

    print(f"Design Parameters:")
    print(f"  Span: {span_m} m")
    print(f"  Section: {b_mm} × {d_mm + 50} mm")
    print(f"  Factored moment: {mu_kn_m:.1f} kN·m")
    print()

    # Design
    result = design_beam_is456(
        span_m=span_m,
        b_mm=b_mm,
        d_mm=d_mm,
        fck_mpa=fck_mpa,
        fy_mpa=fy_mpa,
        moment_kn_m=mu_kn_m,
        shear_kn=wu_kn_m * span_m / 2,
    )

    # Print results
    print("Design Results:")
    print(result.summary())

if __name__ == '__main__':
    main()
```

### 9.2 Jupyter Notebook Examples

**Create interactive tutorials** in `examples/notebooks/`:

```python
# examples/notebooks/01_getting_started.ipynb
"""
# Getting Started with structural_lib

This notebook demonstrates basic beam design using the structural_lib library.

## Installation

```bash
pip install structural-lib-is456
```

## Basic Design Example
"""

# Cell 1: Imports
from structural_lib import design_singly_reinforced

# Cell 2: Design a beam
result = design_singly_reinforced(
    b_mm=300,
    d_mm=550,
    mu_kn_m=180,
    fck_mpa=30,
    fy_mpa=415,
)

# Cell 3: Display results
print(f"Required steel: {result.ast_required_mm2:.0f} mm²")
print(f"Min steel: {result.ast_min_mm2:.0f} mm²")
print(f"Max steel: {result.ast_max_mm2:.0f} mm²")

# Cell 4: Visualization
import matplotlib.pyplot as plt
# Plot reinforcement ratio vs moment...
```

### 9.3 Example Documentation

**Create examples/README.md:**

```markdown
# Examples

Runnable examples demonstrating structural_lib usage.

## Basic Examples

| File | Description | Topics |
|------|-------------|--------|
| `beam_design_basic.py` | Simple beam design | Flexure, loads, IS 456 |
| `beam_design_with_shear.py` | Flexure + shear | Stirrups, detailing |
| `batch_processing.py` | Design multiple beams | Job runner, optimization |

## Jupyter Notebooks

Interactive tutorials (requires `jupyter`):

```bash
pip install jupyter
jupyter notebook examples/notebooks/
```

- `01_getting_started.ipynb`: Basic beam design
- `02_advanced_features.ipynb`: Optimization, detailing, BBS
- `03_integration_excel.ipynb`: Excel integration via xlwings

## Running Examples

```bash
# Run a script
python examples/beam_design_basic.py

# Run all examples (CI test)
pytest examples/ --doctest-modules
```
```

---

## 10. Documentation Testing

### 10.1 Doctest Integration

**Enable doctest in pytest.ini:**

```ini
[pytest]
# Run doctests in all Python files
addopts =
    --doctest-modules
    --doctest-continue-on-failure

# Ignore test directories when running doctests
doctest_optionflags =
    NORMALIZE_WHITESPACE
    ELLIPSIS
```

**Run doctests:**
```bash
# Test all docstrings
pytest --doctest-modules structural_lib/

# Test specific module
pytest --doctest-modules structural_lib/flexure.py

# Verbose output
pytest --doctest-modules structural_lib/ -v
```

### 10.2 Doctest Best Practices

**DO:**
```python
"""
Example:
    >>> from structural_lib import calculate_mu_lim
    >>> result = calculate_mu_lim(b_mm=300, d_mm=550, fck_mpa=30)
    >>> print(f"{result:.1f}")
    245.3
"""
# ✅ Uses explicit formatting, testable
```

**DON'T:**
```python
"""
Example:
    >>> result = calculate_mu_lim(300, 550, 30)
    >>> result
    245.34567890123
"""
# ❌ Float comparison fails (floating point precision)
# ❌ No import shown (where does calculate_mu_lim come from?)
```

### 10.3 Skipping Flaky Doctests

**Skip tests that depend on external state:**

```python
"""
Example (not tested):

    # Load beams from Excel file
    df = pd.read_excel("beams.xlsx")
    for row in df.itertuples():
        result = design_singly_reinforced(...)
"""
# Marked as "not tested" - won't run in CI
```

**Or use doctest directives:**

```python
"""
Example:
    >>> import pandas as pd
    >>> df = pd.read_excel("beams.xlsx")  # doctest: +SKIP
    >>> # Rest of example...
"""
# doctest: +SKIP directive skips this line
```

### 10.4 Example Coverage Tracking

**Track which functions have runnable examples:**

```python
# scripts/check_example_coverage.py
"""Check that all public functions have runnable examples."""

import ast
from pathlib import Path

def has_runnable_example(docstring: str) -> bool:
    """Check if docstring has >>> example."""
    return docstring and '>>>' in docstring

# Scan all modules, report % of functions with examples
# Fail CI if coverage < 80%
```

### 10.5 CI Doctest Job

**GitHub Actions workflow:**

```yaml
name: Test Documentation

on: [push, pull_request]

jobs:
  doctest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -e .[dev]

      - name: Run doctests
        run: pytest --doctest-modules structural_lib/ -v

      - name: Check example coverage
        run: .venv/bin/python scripts/check_example_coverage.py

      - name: Validate docstring completeness
        run: .venv/bin/python scripts/check_api_docstrings.py
```

---

## Appendix A: Quick Reference Card

### Documentation Checklist (Per Function)

**Docstring sections:**
- [ ] Summary line (< 80 chars, imperative mood, ends with period)
- [ ] Description (2-4 sentences, use cases, constraints)
- [ ] Args (all parameters, units, constraints, defaults)
- [ ] Returns (type, structure, units, fields for objects)
- [ ] Raises (all exception types, when raised)
- [ ] Example (1-3 examples at different complexity levels)
- [ ] Note (optional: caveats, performance, assumptions)
- [ ] See Also (optional: related functions)
- [ ] References (optional: IS 456 clauses, papers)

**Type hints:**
- [ ] All parameters have type hints
- [ ] Return type annotated
- [ ] Use Union/Optional/Literal where appropriate
- [ ] Use `*` for keyword-only parameters

**Examples:**
- [ ] At least one basic example
- [ ] Shows imports if not obvious
- [ ] Includes expected output
- [ ] Uses realistic values (not toy data)
- [ ] Runnable (passes doctest)

**Naming:**
- [ ] Function name is verb_noun (calculate_mu_lim, design_flexure)
- [ ] Parameter names include units (b_mm, mu_kn_m, fck_mpa)
- [ ] Boolean parameters are is_/has_/should_ prefix
- [ ] Groups related functions with common prefix

### Module Documentation Checklist

- [ ] Module docstring present
- [ ] Module docstring lists key functions
- [ ] Module docstring has usage example
- [ ] Module docstring references IS 456 clauses
- [ ] `__all__` declares public API
- [ ] Package `__init__.py` has overview docstring

### Example Documentation Checklist

- [ ] At least 3 standalone example scripts in examples/
- [ ] At least 1 Jupyter notebook in examples/notebooks/
- [ ] examples/README.md lists all examples with descriptions
- [ ] All examples are tested in CI (pytest examples/)
- [ ] Examples show realistic engineering use cases

### CI Documentation Checks

- [ ] Doctest runs in CI (pytest --doctest-modules)
- [ ] Docstring completeness checked (missing Args/Returns/Examples)
- [ ] Example coverage ≥ 80% (functions with runnable examples)
- [ ] API docs generated and deployed (pdoc)
- [ ] Link validation (no broken cross-references)

---

## Appendix B: Docstring Templates

### B.1 Simple Calculation Function

```python
def calculate_value(
    input_a: float,
    input_b: float,
    *,
    validate: bool = True,
) -> float:
    """Calculate derived value from inputs per IS 456 Cl. X.X.

    Brief description of what the function calculates and when to use it.

    Args:
        input_a: Description with units. Constraints (min/max values).
        input_b: Description with units. Constraints.
        validate: Validate inputs before calculation. Default: True.

    Returns:
        Result value with units and physical meaning.

    Raises:
        ValidationError: If input_a or input_b outside valid range.

    Example:
        >>> result = calculate_value(input_a=10.0, input_b=20.0)
        >>> print(f"{result:.1f}")
        30.0

    References:
        IS 456:2000 Cl. X.X: Brief description
    """
```

### B.2 Design Function (Returns Dataclass)

```python
def design_component(
    param1: float,
    param2: float,
    material_grade: Literal['A', 'B', 'C'],
    *,
    validate: bool = True,
    option_flag: bool = False,
) -> DesignResult:
    """Design component per IS 456 Cl. X.X.

    Detailed description of design procedure, assumptions, and applicability.

    Args:
        param1: Parameter description with units and constraints.
        param2: Parameter description with units and constraints.
        material_grade: Material grade. One of 'A', 'B', 'C' per IS 456 Table Y.
        validate: Validate all inputs before design. Default: True.
        option_flag: Enable optional behavior. Description. Default: False.

    Returns:
        DesignResult with fields:
            - output1: Description with units
            - output2: Description with units
            - status: Design status (passed/failed)

    Raises:
        ValidationError: If param1 or param2 invalid
        DesignError: If design cannot satisfy requirements
        ComplianceError: If result violates code limits

    Example:
        Basic usage:

        >>> result = design_component(
        ...     param1=100.0,
        ...     param2=200.0,
        ...     material_grade='B',
        ... )
        >>> print(result.output1)
        150.0

        Handle design failure:

        >>> try:
        ...     result = design_component(param1=1000.0, ...)
        ... except DesignError as e:
        ...     print(f"Failed: {e.suggestion}")

    Note:
        Important caveats or assumptions about the design.

    See Also:
        - related_function: When to use instead
        - DesignResult: Complete result documentation

    References:
        IS 456:2000 Clauses:
        - Cl. X.X: Main design equations
        - Cl. Y.Y: Minimum/maximum limits
    """
```

### B.3 Validation Function

```python
def validate_dimension(value: float, min_val: float, max_val: float, name: str) -> None:
    """Validate dimension is within acceptable range.

    Args:
        value: Value to validate
        min_val: Minimum acceptable value (inclusive)
        max_val: Maximum acceptable value (inclusive)
        name: Parameter name for error message

    Raises:
        ValidationError: If value < min_val or value > max_val

    Example:
        >>> validate_dimension(value=300.0, min_val=200.0, max_val=1000.0, name='b_mm')
        # No error (passes)

        >>> validate_dimension(value=150.0, min_val=200.0, max_val=1000.0, name='b_mm')
        ValidationError: b_mm = 150.0 < minimum 200.0
    """
```

### B.4 API Wrapper Function

```python
def api_function(
    input1: float,
    input2: float,
    *,
    options: Optional[dict] = None,
) -> dict:
    """High-level API for common use case.

    Simplified interface that handles common patterns. For advanced control,
    use underlying functions directly.

    Args:
        input1: Input description with units
        input2: Input description with units
        options: Optional configuration dict with keys:
            - 'key1': Description (default: value)
            - 'key2': Description (default: value)

    Returns:
        Dictionary with keys:
            - 'result1': Description
            - 'result2': Description
            - 'status': 'success' or 'failure'

    Example:
        >>> result = api_function(input1=10.0, input2=20.0)
        >>> print(result['result1'])
        30.0

        >>> # With options
        >>> result = api_function(
        ...     input1=10.0,
        ...     input2=20.0,
        ...     options={'key1': 'custom_value'}
        ... )

    See Also:
        - underlying_function: For advanced use cases
    """
```
