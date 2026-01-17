# Result Object Design Standard

**Type:** Guideline
**Audience:** Developers
**Status:** Draft
**Importance:** High
**Created:** 2026-01-07
**Last Updated:** 2026-01-13

---

**Version:** 1.0
**Owner:** RESEARCHER
**Related:** [Function Signature Standard](function-signature-standard.md), [Professional API Patterns](../research/professional-api-patterns.md), [UX Patterns](../research/ux-patterns-for-technical-apis.md)

---

## Purpose

This document defines standards for result objects returned by functions in structural_engineering_lib. Result objects replace primitive returns (tuples, dicts) with structured, self-documenting, type-safe containers.

**Benefits:**
- **Discoverability**: IDE autocomplete shows available fields
- **Type Safety**: Type checkers catch field access errors
- **Maintainability**: Adding fields doesn't break existing code
- **Documentation**: Field names are self-documenting
- **Extensibility**: Can add methods without changing call sites

**Target Audience**: All developers contributing to the library

---

## Table of Contents

1. [Core Principles](#1-core-principles)
2. [Choosing the Right Container](#2-choosing-the-right-container)
3. [Dataclass Standard (Primary Choice)](#3-dataclass-standard-primary-choice)
4. [Essential Methods](#4-essential-methods)
5. [Immutability & Validation](#5-immutability--validation)
6. [Nested Result Objects](#6-nested-result-objects)
7. [Error Handling in Results](#7-error-handling-in-results)
8. [Serialization & Persistence](#8-serialization--persistence)
9. [Display & Formatting](#9-display--formatting)
10. [Anti-Patterns](#10-anti-patterns)
11. [Migration Strategy](#11-migration-strategy)
12. [Examples by Complexity](#12-examples-by-complexity)

---

## 1. Core Principles

### 1.1 Never Return Bare Tuples

**Problem:** Tuples require memorizing field order and offer no type safety.

```python
# ❌ CATASTROPHIC: Mystery tuple
def calculate_reinforcement(moment, width, depth):
    ast = ...
    count = ...
    diameter = ...
    return (ast, count, diameter)  # Which is which? Must check docs!

# Usage (fragile, error-prone):
area, n, dia = calculate_reinforcement(150, 230, 450)
# 3 months later: Was it (area, n, dia) or (n, dia, area)?
```

**Solution:**
```python
# ✅ EXCELLENT: Named result
from dataclasses import dataclass

@dataclass(frozen=True)
class ReinforcementResult:
    """Result of reinforcement calculation."""
    area_mm2: float
    bar_count: int
    bar_diameter_mm: int

def calculate_reinforcement(
    moment_knm: float,
    width_mm: float,
    depth_mm: float
) -> ReinforcementResult:
    ast = ...
    count = ...
    diameter = ...
    return ReinforcementResult(
        area_mm2=ast,
        bar_count=count,
        bar_diameter_mm=diameter
    )

# Usage (self-documenting, refactor-safe):
result = calculate_reinforcement(150, 230, 450)
print(f"Area: {result.area_mm2} mm²")  # Autocomplete works!
print(f"Bars: {result.bar_count}-#{result.bar_diameter_mm}")
```

### 1.2 Result Objects Are Immutable

**Rule:** All result objects MUST be immutable (frozen dataclasses).

**Rationale:**
- Results represent facts about a completed calculation
- Immutability enables caching and safe sharing
- Prevents accidental modification bugs
- Makes objects hashable (can use in sets/dicts)

```python
# ✅ CORRECT: Frozen dataclass
@dataclass(frozen=True)
class DesignResult:
    moment_capacity_knm: float
    reinforcement: ReinforcementResult
    compliance: ComplianceResult

# Usage:
result = design_beam(...)
result.moment_capacity_knm = 200  # ❌ Raises FrozenInstanceError (good!)
```

### 1.3 Results Are Complete

**Rule:** Result objects should contain everything needed to understand the calculation outcome.

**Include:**
- Primary results (what user asked for)
- Intermediate values (for debugging/verification)
- Metadata (convergence status, iterations, warnings)
- References (code clauses, assumptions)

```python
# ❌ INCOMPLETE: Only final answer
@dataclass(frozen=True)
class FlexureResult:
    ast_mm2: float

# ✅ COMPLETE: Everything needed
@dataclass(frozen=True)
class FlexureResult:
    # Primary results
    ast_required_mm2: float
    ast_provided_mm2: float
    bar_configuration: str  # e.g., "3-#16"

    # Intermediate values (for verification)
    neutral_axis_depth_mm: float
    moment_capacity_knm: float
    steel_ratio: float

    # Metadata
    design_method: str  # "singly_reinforced" | "doubly_reinforced"
    assumptions: list[str]  # ["rectangular stress block", "no compression steel"]
    code_references: list[str]  # ["IS 456 Cl. 38.1", "SP:16 Chart 3"]

    # Compliance
    min_steel_check: bool
    max_steel_check: bool
    spacing_check: bool
```

---

## 2. Choosing the Right Container

### 2.1 Decision Tree

```
Is the result returned by a PUBLIC function?
├─ YES → Use Dataclass (frozen=True)
└─ NO (internal only)
   ├─ Need methods/behavior? → Use Dataclass
   ├─ Simple 2-3 fields? → NamedTuple OK
   └─ Dynamic fields? → Dict (discouraged)
```

### 2.2 Container Comparison

| Feature | Dataclass | NamedTuple | Dict | Recommendation |
|---------|-----------|------------|------|----------------|
| **Type hints** | ✅ Full support | ✅ Full support | ❌ No field types | Dataclass |
| **Immutability** | ✅ With `frozen=True` | ✅ Always | ❌ Mutable | Dataclass |
| **Methods** | ✅ Easy to add | ⚠️ Requires class body | ❌ No methods | Dataclass |
| **Defaults** | ✅ Field-level | ✅ Factory functions | ❌ Runtime only | Dataclass |
| **Inheritance** | ✅ Full support | ⚠️ Limited | ❌ N/A | Dataclass |
| **Memory** | Efficient | Most efficient | Least efficient | NamedTuple |
| **Readability** | Excellent | Good | Poor | Dataclass |
| **IDE support** | ✅ Perfect | ✅ Good | ❌ None | Dataclass |

**Verdict:** Use `@dataclass(frozen=True)` for 99% of cases.

### 2.3 When to Use Alternatives

**NamedTuple:** Only for:
- Internal helper functions
- Simple 2-3 field returns with no behavior
- Performance-critical inner loops (proven bottleneck)

**Dict:** Never for public API. Acceptable only for:
- Dynamic external data (JSON deserialization)
- Prototyping (must convert to dataclass before release)

---

## 3. Dataclass Standard (Primary Choice)

### 3.1 Basic Template

```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class CalculationResult:
    """
    Result of [describe calculation].

    Attributes:
        primary_output: [describe with units]
        secondary_output: [describe with units]

    Example:
        >>> result = some_function(...)
        >>> print(result.primary_output)
        123.45
    """
    # Required fields (no defaults)
    primary_output: float

    # Optional fields (with defaults)
    secondary_output: float = 0.0
    metadata: Optional[dict] = None

    def summary(self) -> str:
        """Return human-readable summary."""
        return f"Primary: {self.primary_output:.2f}"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        from dataclasses import asdict
        return asdict(self)
```

### 3.2 Mandatory Attributes

**Every result dataclass MUST have:**

1. **Class docstring** with description and example
2. **Type hints** for ALL fields
3. **Unit suffixes** for dimensional fields (`_mm`, `_kn`, `_mpa`)
4. **`frozen=True`** to prevent modification

```python
@dataclass(frozen=True)  # ← MANDATORY
class ShearResult:
    """
    Result of shear design per IS 456 Cl. 40.

    Attributes:
        stirrup_diameter_mm: Diameter of stirrup reinforcement
        stirrup_spacing_mm: Center-to-center spacing
        shear_capacity_kn: Design shear capacity
    """
    stirrup_diameter_mm: int  # ← MANDATORY type hint
    stirrup_spacing_mm: float  # ← MANDATORY type hint
    shear_capacity_kn: float  # ← MANDATORY unit suffix
```

### 3.3 Field Ordering

**Standard order:**
1. Primary results (what user explicitly asked for)
2. Secondary results (related calculations)
3. Intermediate values (for verification)
4. Metadata (assumptions, references, warnings)
5. Compliance flags (boolean checks)

```python
@dataclass(frozen=True)
class BeamDesignResult:
    # 1. PRIMARY RESULTS
    moment_capacity_knm: float
    reinforcement: ReinforcementResult

    # 2. SECONDARY RESULTS
    shear_capacity_kn: float
    deflection_mm: float

    # 3. INTERMEDIATE VALUES
    neutral_axis_depth_mm: float
    steel_ratio: float

    # 4. METADATA
    design_method: str
    iterations: int
    warnings: list[str]

    # 5. COMPLIANCE
    all_checks_passed: bool
    failed_checks: list[str]
```

### 3.4 Default Values

**Rules:**
- Required fields: No default
- Optional fields: Sensible default or `None`
- Never use mutable defaults directly (use `field(default_factory=...)`

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class AnalysisResult:
    # Required (no default)
    load_kn: float

    # Optional with immutable default
    factor: float = 1.5

    # Optional with None
    note: Optional[str] = None

    # Optional with mutable default (MUST use factory)
    warnings: list[str] = field(default_factory=list)  # ✅ CORRECT
    # warnings: list[str] = []  # ❌ WRONG: Shared across instances!
```

---

## 4. Essential Methods

### 4.1 Required Methods (All Result Objects)

#### `__repr__` (Auto-generated by dataclass)

Dataclasses automatically provide good `__repr__`:

```python
@dataclass(frozen=True)
class ReinforcementResult:
    area_mm2: float
    bar_count: int
    bar_diameter_mm: int

result = ReinforcementResult(1250.5, 4, 16)
print(result)
# Output: ReinforcementResult(area_mm2=1250.5, bar_count=4, bar_diameter_mm=16)
```

#### `summary()` - Human-Readable Summary

Every result MUST provide a `summary()` method:

```python
@dataclass(frozen=True)
class FlexureDesignResult:
    ast_required_mm2: float
    ast_provided_mm2: float
    bar_configuration: str
    moment_capacity_knm: float

    def summary(self) -> str:
        """Return concise human-readable summary."""
        return (
            f"Flexure Design Summary:\n"
            f"  Required Ast: {self.ast_required_mm2:.0f} mm²\n"
            f"  Provided Ast: {self.ast_provided_mm2:.0f} mm²\n"
            f"  Bars: {self.bar_configuration}\n"
            f"  Capacity: {self.moment_capacity_knm:.1f} kN-m"
        )

# Usage:
result = design_flexure(...)
print(result.summary())
# Flexure Design Summary:
#   Required Ast: 1250 mm²
#   Provided Ast: 1340 mm²
#   Bars: 3-#16
#   Capacity: 165.5 kN-m
```

#### `to_dict()` - Dictionary Serialization

For JSON export, Excel, databases:

```python
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class DesignResult:
    span_mm: float
    load_kn: float
    reinforcement: ReinforcementResult

    def to_dict(self) -> dict:
        """
        Convert to dictionary for serialization.

        Returns flat dict with nested objects expanded.
        """
        return asdict(self)

# Usage:
result = design_beam(...)
data = result.to_dict()
# {'span_mm': 5000, 'load_kn': 10.0, 'reinforcement': {'area_mm2': 1250.5, ...}}

import json
json.dump(data, file)  # Serialize to JSON
```

### 4.2 Recommended Methods (Common Patterns)

#### `is_valid()` - Validation Check

```python
@dataclass(frozen=True)
class ComplianceResult:
    flexure_ok: bool
    shear_ok: bool
    deflection_ok: bool
    cracking_ok: bool

    def is_valid(self) -> bool:
        """Return True if all compliance checks passed."""
        return all([
            self.flexure_ok,
            self.shear_ok,
            self.deflection_ok,
            self.cracking_ok
        ])

    @property
    def failed_checks(self) -> list[str]:
        """Return list of failed check names."""
        failures = []
        if not self.flexure_ok:
            failures.append("flexure")
        if not self.shear_ok:
            failures.append("shear")
        if not self.deflection_ok:
            failures.append("deflection")
        if not self.cracking_ok:
            failures.append("cracking")
        return failures
```

#### `compare()` - Result Comparison

```python
@dataclass(frozen=True)
class DesignResult:
    span_mm: float
    cost_inr: float
    steel_kg: float

    def compare(self, other: 'DesignResult') -> str:
        """
        Compare this result with another design.

        Returns:
            Human-readable comparison summary
        """
        cost_diff_pct = (self.cost_inr - other.cost_inr) / other.cost_inr * 100
        steel_diff_pct = (self.steel_kg - other.steel_kg) / other.steel_kg * 100

        return (
            f"Cost: {cost_diff_pct:+.1f}%\n"
            f"Steel: {steel_diff_pct:+.1f}%"
        )
```

#### `to_report()` - Formatted Report

```python
@dataclass(frozen=True)
class CompleteDesignResult:
    flexure: FlexureResult
    shear: ShearResult
    deflection: DeflectionResult
    compliance: ComplianceResult

    def to_report(self, format: str = 'text') -> str:
        """
        Generate formatted design report.

        Args:
            format: 'text', 'markdown', or 'html'

        Returns:
            Formatted report string
        """
        if format == 'text':
            return self._text_report()
        elif format == 'markdown':
            return self._markdown_report()
        elif format == 'html':
            return self._html_report()
        else:
            raise ValueError(f"Unknown format: {format}")

    def _text_report(self) -> str:
        return f"""
BEAM DESIGN REPORT
==================

Flexure Design:
{self.flexure.summary()}

Shear Design:
{self.shear.summary()}

Deflection Check:
{self.deflection.summary()}

Compliance:
{self.compliance.summary()}
"""
```

---

## 5. Immutability & Validation

### 5.1 Why Immutability Matters

**Benefits:**
- **Cacheable**: Can cache expensive calculations safely
- **Thread-safe**: Multiple threads can read without locks
- **Hashable**: Can use in sets, dict keys
- **Debuggable**: State doesn't change unexpectedly

```python
# ✅ Immutable result (frozen=True)
@dataclass(frozen=True)
class Result:
    value: float

result = Result(10.0)
result.value = 20.0  # ❌ Raises FrozenInstanceError

# Can use in set/dict:
results = {result1, result2, result3}  # ✅ Works because frozen
cache = {result1: computation1, result2: computation2}  # ✅ Hashable
```

### 5.2 Post-Init Validation

Use `__post_init__` for validation (with `frozen=True`, requires `object.__setattr__`):

```python
@dataclass(frozen=True)
class ReinforcementResult:
    area_mm2: float
    bar_count: int
    bar_diameter_mm: int

    def __post_init__(self):
        """Validate fields after initialization."""
        if self.area_mm2 < 0:
            raise ValueError(f"Area cannot be negative: {self.area_mm2}")
        if self.bar_count < 0:
            raise ValueError(f"Bar count cannot be negative: {self.bar_count}")
        if self.bar_diameter_mm not in [8, 10, 12, 16, 20, 25, 32, 40]:
            raise ValueError(f"Invalid bar diameter: {self.bar_diameter_mm}")
```

### 5.3 Computed Fields

For derived values, use `@property` or `field(init=False)`:

```python
@dataclass(frozen=True)
class BeamSection:
    width_mm: float
    depth_mm: float

    @property
    def area_mm2(self) -> float:
        """Compute cross-sectional area."""
        return self.width_mm * self.depth_mm

    @property
    def moment_of_inertia_mm4(self) -> float:
        """Compute moment of inertia."""
        return self.width_mm * self.depth_mm ** 3 / 12

# Usage:
section = BeamSection(230, 450)
print(section.area_mm2)  # 103500 (computed on demand)
print(section.moment_of_inertia_mm4)  # 1950843750
```

**Alternative with `field(init=False)`** (for expensive computations cached at init):

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class ExpensiveResult:
    input_data: list[float]
    _cached_sum: float = field(init=False, repr=False)

    def __post_init__(self):
        # Cache expensive computation at init time
        object.__setattr__(self, '_cached_sum', sum(self.input_data))

    @property
    def total(self) -> float:
        return self._cached_sum
```

---

## 6. Nested Result Objects

### 6.1 Composition Pattern

Result objects should compose smaller result objects:

```python
@dataclass(frozen=True)
class ReinforcementResult:
    """Reinforcement calculation result."""
    area_mm2: float
    bar_count: int
    bar_diameter_mm: int
    spacing_mm: float

@dataclass(frozen=True)
class FlexureResult:
    """Flexure design result."""
    moment_capacity_knm: float
    tension_steel: ReinforcementResult
    compression_steel: Optional[ReinforcementResult] = None

@dataclass(frozen=True)
class ShearResult:
    """Shear design result."""
    shear_capacity_kn: float
    stirrups: ReinforcementResult

@dataclass(frozen=True)
class CompleteDesignResult:
    """Complete beam design result."""
    flexure: FlexureResult
    shear: ShearResult
    deflection: DeflectionResult
    compliance: ComplianceResult

    def summary(self) -> str:
        """Aggregate summary from all sub-results."""
        return (
            f"Complete Design Summary:\n"
            f"\nFlexure:\n{self.flexure.summary()}"
            f"\nShear:\n{self.shear.summary()}"
            f"\nDeflection:\n{self.deflection.summary()}"
            f"\nCompliance: {'PASS' if self.compliance.is_valid() else 'FAIL'}"
        )
```

### 6.2 Accessing Nested Fields

```python
result = design_beam_complete(...)

# Access nested fields:
tension_bars = result.flexure.tension_steel.bar_count
tension_dia = result.flexure.tension_steel.bar_diameter_mm
print(f"Tension: {tension_bars}-#{tension_dia}")

stirrup_spacing = result.shear.stirrups.spacing_mm
print(f"Stirrups @ {stirrup_spacing}mm c/c")

# Check compliance:
if result.compliance.is_valid():
    print("All checks passed!")
else:
    print(f"Failed: {', '.join(result.compliance.failed_checks)}")
```

---

## 7. Error Handling in Results

### 7.1 Success/Failure Pattern

For operations that can fail without raising exceptions:

```python
from typing import Optional
from dataclasses import dataclass

@dataclass(frozen=True)
class OptimizationResult:
    """Result of optimization attempt."""
    success: bool
    solution: Optional[dict] = None
    error_message: Optional[str] = None
    iterations: int = 0

    def __post_init__(self):
        """Validate that success implies solution exists."""
        if self.success and self.solution is None:
            raise ValueError("Success=True requires solution")
        if not self.success and self.error_message is None:
            raise ValueError("Success=False requires error_message")

# Usage:
def optimize_design(...) -> OptimizationResult:
    try:
        solution = run_optimization(...)
        return OptimizationResult(
            success=True,
            solution=solution,
            iterations=solution['iterations']
        )
    except ConvergenceError as e:
        return OptimizationResult(
            success=False,
            error_message=str(e),
            iterations=100  # max iterations reached
        )

# Caller checks success:
result = optimize_design(...)
if result.success:
    print(f"Optimized in {result.iterations} iterations")
    use_solution(result.solution)
else:
    print(f"Optimization failed: {result.error_message}")
```

### 7.2 Result with Warnings

```python
@dataclass(frozen=True)
class DesignResult:
    """Design result with optional warnings."""
    reinforcement: ReinforcementResult
    moment_capacity_knm: float
    warnings: list[str] = field(default_factory=list)

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    def print_warnings(self) -> None:
        """Print all warnings to console."""
        if self.has_warnings:
            print("Warnings:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")

# Usage:
def design_beam(...) -> DesignResult:
    warnings = []

    if span_depth_ratio > 20:
        warnings.append(
            f"Span/depth ratio ({span_depth_ratio:.1f}) exceeds recommended limit (20)"
        )

    if steel_ratio < 0.001:
        warnings.append(
            f"Steel ratio ({steel_ratio:.4f}) below minimum (0.0015) - check for light reinforcement"
        )

    return DesignResult(
        reinforcement=...,
        moment_capacity_knm=...,
        warnings=warnings
    )

# Caller:
result = design_beam(...)
if result.has_warnings:
    result.print_warnings()
```

---

## 8. Serialization & Persistence

### 8.1 JSON Serialization

```python
import json
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass(frozen=True)
class DesignResult:
    span_mm: float
    load_kn: float
    reinforcement: ReinforcementResult
    warnings: list[str] = field(default_factory=list)

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'DesignResult':
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        # Reconstruct nested objects:
        data['reinforcement'] = ReinforcementResult(**data['reinforcement'])
        return cls(**data)

# Usage:
result = design_beam(...)
json_str = result.to_json()
with open('design_result.json', 'w') as f:
    f.write(json_str)

# Load back:
with open('design_result.json', 'r') as f:
    loaded_result = DesignResult.from_json(f.read())
```

### 8.2 DataFrame Export

For batch results:

```python
import pandas as pd

@dataclass(frozen=True)
class BatchResult:
    """Results from batch design operation."""
    results: list[DesignResult]

    def to_dataframe(self) -> pd.DataFrame:
        """Convert all results to DataFrame."""
        rows = []
        for result in self.results:
            rows.append({
                'span_mm': result.span_mm,
                'load_kn': result.load_kn,
                'ast_mm2': result.reinforcement.area_mm2,
                'bar_count': result.reinforcement.bar_count,
                'bar_dia_mm': result.reinforcement.bar_diameter_mm,
                'moment_capacity_knm': result.moment_capacity_knm,
                'has_warnings': result.has_warnings
            })
        return pd.DataFrame(rows)

# Usage:
batch_result = design_beam_batch([...])
df = batch_result.to_dataframe()
df.to_excel('batch_design_results.xlsx')
```

---

## 9. Display & Formatting

### 9.1 Rich Display (`__str__` vs `__repr__`)

**Rule:**
- `__repr__`: Developer representation (auto-generated by dataclass) - shows all fields
- `__str__`: User-friendly representation (custom) - shows summary

```python
@dataclass(frozen=True)
class DesignResult:
    span_mm: float
    load_kn: float
    reinforcement: ReinforcementResult
    moment_capacity_knm: float

    # __repr__ auto-generated:
    # DesignResult(span_mm=5000, load_kn=10.0, ...)

    def __str__(self) -> str:
        """User-friendly string representation."""
        return (
            f"Beam Design (span={self.span_mm}mm, load={self.load_kn}kN):\n"
            f"  Reinforcement: {self.reinforcement.bar_count}-#{self.reinforcement.bar_diameter_mm}\n"
            f"  Capacity: {self.moment_capacity_knm:.1f} kN-m"
        )

# Usage:
result = design_beam(...)
print(repr(result))  # Developer: DesignResult(span_mm=5000, load_kn=10.0, ...)
print(str(result))   # User: Beam Design (span=5000mm, load=10.0kN): ...
print(result)        # Calls __str__ by default
```

### 9.2 Table Display

For results with tabular data:

```python
@dataclass(frozen=True)
class LoadCombinationResult:
    """Results for multiple load combinations."""
    combinations: list[tuple[str, float]]  # (name, moment)
    governing_combination: str
    governing_moment_knm: float

    def to_table(self) -> str:
        """Format as ASCII table."""
        lines = ["Load Combinations:", "=" * 40]
        for name, moment in self.combinations:
            marker = " *" if name == self.governing_combination else "  "
            lines.append(f"{marker} {name:20s}: {moment:8.2f} kN-m")
        lines.append("=" * 40)
        lines.append(f"Governing: {self.governing_combination}")
        return "\n".join(lines)

# Output:
# Load Combinations:
# ========================================
#    1.5DL + 1.5LL      :   150.00 kN-m
#  * 1.2DL + 1.2LL + 1.2WL:   175.50 kN-m
#    1.5DL + 1.05WL     :   142.75 kN-m
# ========================================
# Governing: 1.2DL + 1.2LL + 1.2WL
```

---

## 10. Anti-Patterns

### 10.1 Avoid Mixing Data and Behavior

**Problem:** Result objects are data containers, not active objects.

```python
# ❌ BAD: Result object with business logic
@dataclass(frozen=True)
class DesignResult:
    span_mm: float
    load_kn: float

    def redesign_with_higher_grade(self) -> 'DesignResult':
        """WRONG: Results shouldn't create new results"""
        return design_beam(self.span_mm, self.load_kn, concrete='M30')

# ✅ GOOD: Separate data from operations
@dataclass(frozen=True)
class DesignResult:
    span_mm: float
    load_kn: float

def redesign_with_higher_grade(original: DesignResult) -> DesignResult:
    """Function operates on result to create new design."""
    return design_beam(
        original.span_mm,
        original.load_kn,
        concrete='M30'
    )
```

**Acceptable behavior in results:**
- ✅ Formatting methods (`summary()`, `to_table()`, `to_json()`)
- ✅ Validation methods (`is_valid()`, `has_warnings()`)
- ✅ Comparison methods (`compare()`, `__eq__()`)
- ✅ Accessor properties (`@property` for computed fields)
- ❌ Operations that modify state
- ❌ Operations that create new designs
- ❌ Database/file I/O operations

### 10.2 Avoid Result Soup

**Problem:** Too many small result objects creates complexity.

```python
# ❌ BAD: Over-granular
@dataclass(frozen=True)
class BarCountResult:
    count: int

@dataclass(frozen=True)
class BarDiameterResult:
    diameter: int

@dataclass(frozen=True)
class BarAreaResult:
    area: float

@dataclass(frozen=True)
class ReinforcementResult:
    count: BarCountResult
    diameter: BarDiameterResult
    area: BarAreaResult  # Too much nesting!

# ✅ GOOD: Appropriate granularity
@dataclass(frozen=True)
class ReinforcementResult:
    area_mm2: float
    bar_count: int
    bar_diameter_mm: int
    spacing_mm: float
```

**Guideline:** Create nested objects when:
- The nested object is used independently elsewhere
- The nested object has 5+ related fields
- The nested object has its own behavior/methods

### 10.3 Avoid Optional Soup

**Problem:** Every field marked `Optional` makes usage unclear.

```python
# ❌ BAD: Everything optional
@dataclass(frozen=True)
class DesignResult:
    moment_capacity: Optional[float] = None
    reinforcement: Optional[ReinforcementResult] = None
    shear_capacity: Optional[float] = None
    deflection: Optional[float] = None
    # User: "Which fields will actually be present?"

# ✅ GOOD: Clear required vs optional
@dataclass(frozen=True)
class DesignResult:
    # Always present:
    moment_capacity_knm: float
    reinforcement: ReinforcementResult

    # Optional only when semantically valid:
    compression_steel: Optional[ReinforcementResult] = None  # Only for doubly reinforced
    warnings: list[str] = field(default_factory=list)  # May be empty
```

---

## 11. Migration Strategy

### 11.1 Tuple → Dataclass Migration

**Step 1:** Identify tuple returns in public API

```bash
# Find tuple returns
grep -r "return (" Python/structural_lib/*.py | grep -v "__pycache__"
```

**Step 2:** Create result dataclass

```python
# BEFORE:
def calculate_reinforcement(moment, width, depth):
    ast = ...
    count = ...
    diameter = ...
    return (ast, count, diameter)

# AFTER (new function):
@dataclass(frozen=True)
class ReinforcementResult:
    area_mm2: float
    bar_count: int
    bar_diameter_mm: int

def calculate_reinforcement_v2(
    moment_knm: float,
    width_mm: float,
    depth_mm: float
) -> ReinforcementResult:
    ast = ...
    count = ...
    diameter = ...
    return ReinforcementResult(ast, count, diameter)
```

**Step 3:** Add deprecation wrapper

```python
import warnings

def calculate_reinforcement(moment, width, depth) -> tuple:
    """
    DEPRECATED: Use calculate_reinforcement_v2() which returns ReinforcementResult.

    This function will be removed in v1.0.
    """
    warnings.warn(
        "calculate_reinforcement() returns tuple and is deprecated. "
        "Use calculate_reinforcement_v2() which returns ReinforcementResult. "
        "See migration guide: docs/guides/tuple-to-dataclass-migration.md",
        DeprecationWarning,
        stacklevel=2
    )

    result = calculate_reinforcement_v2(moment, width, depth)
    return (result.area_mm2, result.bar_count, result.bar_diameter_mm)
```

**Step 4:** Remove tuple version in next major release

### 11.2 Dict → Dataclass Migration

```python
# BEFORE:
def design_beam(...) -> dict:
    return {
        'moment': 150,
        'reinforcement': {
            'area': 1250,
            'count': 4,
            'diameter': 16
        }
    }

# AFTER:
@dataclass(frozen=True)
class ReinforcementResult:
    area_mm2: float
    bar_count: int
    bar_diameter_mm: int

@dataclass(frozen=True)
class DesignResult:
    moment_capacity_knm: float
    reinforcement: ReinforcementResult

    def to_dict(self) -> dict:
        """For backward compatibility."""
        return {
            'moment': self.moment_capacity_knm,
            'reinforcement': {
                'area': self.reinforcement.area_mm2,
                'count': self.reinforcement.bar_count,
                'diameter': self.reinforcement.bar_diameter_mm
            }
        }

def design_beam(...) -> DesignResult:
    ...
    return DesignResult(
        moment_capacity_knm=150,
        reinforcement=ReinforcementResult(1250, 4, 16)
    )

# Old callers can still use .to_dict() during transition
```

---

## 12. Examples by Complexity

### 12.1 Simple Result (Core Calculation)

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class MomentCapacityResult:
    """
    Result of moment capacity calculation per IS 456 Cl. 38.1.

    Example:
        >>> result = calculate_moment_capacity(230, 450, 1250, 20, 415)
        >>> print(result.summary())
        Moment Capacity: 165.5 kN-m (xu/d = 0.32)
    """
    moment_capacity_knm: float
    neutral_axis_depth_mm: float
    effective_depth_mm: float

    @property
    def xu_over_d(self) -> float:
        """Neutral axis depth ratio (dimensionless)."""
        return self.neutral_axis_depth_mm / self.effective_depth_mm

    def summary(self) -> str:
        return (
            f"Moment Capacity: {self.moment_capacity_knm:.1f} kN-m "
            f"(xu/d = {self.xu_over_d:.2f})"
        )
```

### 12.2 Medium Complexity (Module Result)

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass(frozen=True)
class FlexureDesignResult:
    """
    Complete flexure design result per IS 456 Cl. 38.

    Includes tension steel, optional compression steel, capacity checks.
    """
    # Primary results
    moment_capacity_knm: float
    tension_steel: ReinforcementResult
    compression_steel: Optional[ReinforcementResult] = None

    # Intermediate values
    neutral_axis_depth_mm: float
    effective_depth_mm: float
    steel_ratio: float

    # Metadata
    design_type: str = "singly_reinforced"  # or "doubly_reinforced"
    assumptions: list[str] = field(default_factory=list)

    # Compliance
    min_steel_satisfied: bool = True
    max_steel_satisfied: bool = True

    @property
    def xu_over_d(self) -> float:
        return self.neutral_axis_depth_mm / self.effective_depth_mm

    @property
    def is_under_reinforced(self) -> bool:
        """Check if section is under-reinforced (xu/d < 0.48)."""
        return self.xu_over_d < 0.48

    def summary(self) -> str:
        comp_str = ""
        if self.compression_steel:
            comp_str = f"\n  Compression: {self.compression_steel.bar_count}-#{self.compression_steel.bar_diameter_mm}"

        return (
            f"Flexure Design ({self.design_type}):\n"
            f"  Tension: {self.tension_steel.bar_count}-#{self.tension_steel.bar_diameter_mm}"
            f"{comp_str}\n"
            f"  Capacity: {self.moment_capacity_knm:.1f} kN-m\n"
            f"  xu/d: {self.xu_over_d:.2f} ({'Under' if self.is_under_reinforced else 'Over'}-reinforced)"
        )
```

### 12.3 Complex Result (Top-Level API)

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class CompleteBeamDesignResult:
    """
    Complete beam design result from design_beam_is456().

    Contains all design calculations, compliance checks, and metadata.
    Suitable for:
    - Design report generation
    - CAD drawing export
    - Database storage
    - Comparison with alternative designs
    """
    # Input echo (for traceability)
    input_parameters: BeamInput

    # Design results (primary outputs)
    flexure: FlexureDesignResult
    shear: ShearDesignResult
    deflection: DeflectionCheckResult
    detailing: DetailingResult

    # Compliance summary
    compliance: ComplianceResult

    # Cost estimation
    material_quantities: MaterialQuantities
    estimated_cost_inr: float

    # Metadata
    design_timestamp: datetime = field(default_factory=datetime.now)
    design_code: str = "IS 456:2000"
    software_version: str = "0.15.0"
    warnings: list[str] = field(default_factory=list)

    @property
    def all_checks_passed(self) -> bool:
        """True if all compliance checks passed."""
        return self.compliance.is_valid()

    @property
    def design_is_economical(self) -> bool:
        """True if design efficiency is good (utilization 85-95%)."""
        return (
            0.85 <= self.flexure.moment_capacity_knm / self.input_parameters.moment_knm <= 0.95
        )

    def summary(self) -> str:
        """Concise one-page summary."""
        status = "✓ PASS" if self.all_checks_passed else "✗ FAIL"
        efficiency = "ECONOMICAL" if self.design_is_economical else "CHECK EFFICIENCY"

        return f"""
{'=' * 60}
BEAM DESIGN SUMMARY - {self.design_timestamp.strftime('%Y-%m-%d %H:%M')}
{'=' * 60}

Input:
  Span: {self.input_parameters.span_mm} mm
  Load: {self.input_parameters.load_kn_per_m} kN/m
  Section: {self.input_parameters.width_mm} x {self.input_parameters.depth_mm} mm

Design:
{self.flexure.summary()}

{self.shear.summary()}

{self.deflection.summary()}

Compliance: {status}
Efficiency: {efficiency}
Cost: ₹{self.estimated_cost_inr:,.2f}

Warnings: {len(self.warnings)}
{'=' * 60}
"""

    def to_report(self, format: str = 'pdf') -> bytes:
        """Generate detailed design report."""
        if format == 'pdf':
            return self._generate_pdf_report()
        elif format == 'html':
            return self._generate_html_report()
        else:
            raise ValueError(f"Unsupported format: {format}")

    def to_cad(self, format: str = 'dxf') -> bytes:
        """Export to CAD format using detailing result."""
        from structural_lib.dxf_export import export_beam_to_dxf
        return export_beam_to_dxf(self.detailing, format=format)

    def compare(self, other: 'CompleteBeamDesignResult') -> ComparisonResult:
        """Compare with alternative design."""
        return ComparisonResult(
            cost_difference_pct=(self.estimated_cost_inr - other.estimated_cost_inr) / other.estimated_cost_inr * 100,
            steel_difference_kg=self.material_quantities.steel_kg - other.material_quantities.steel_kg,
            depth_difference_mm=self.input_parameters.depth_mm - other.input_parameters.depth_mm,
            recommendation=self._determine_better_design(other)
        )
```

---

## Appendix A: Quick Reference

**Result Object Checklist:**

- [ ] Use `@dataclass(frozen=True)` (99% of cases)
- [ ] All fields have type hints
- [ ] Dimensional fields have unit suffixes
- [ ] Class docstring with description and example
- [ ] Implement `summary()` method
- [ ] Implement `to_dict()` if serialization needed
- [ ] Fields ordered: primary → secondary → intermediate → metadata → flags
- [ ] Mutable defaults use `field(default_factory=...)`
- [ ] Validation in `__post_init__` if needed
- [ ] Computed fields use `@property`

**When NOT to use frozen:**
- Never for public API results (always frozen)
- Only for internal mutable builders (rare)

---

## Appendix B: SciPy OptimizeResult Deep Dive

**Case Study:** How SciPy evolved from tuples to rich result objects.

### Before (SciPy < 0.11)

```python
# Tuple return (5+ values)
x, fval, iterations, funcalls, warnflag = fmin(func, x0)
# Problem: Must remember order, can't add fields without breaking
```

### After (SciPy >= 0.11)

```python
class OptimizeResult(dict):
    """
    Result object with dict-like interface plus attribute access.

    Clever: Subclasses dict for backward compatibility,
    adds attribute access for discoverability.
    """
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

    def __dir__(self):
        return list(self.keys())

result = minimize(func, x0)
print(result.x)        # Attribute access (discoverable)
print(result['x'])     # Dict access (backward compatible)
print(result.keys())   # Can iterate like dict
```

**Lesson:** If you need dict interface AND discoverability, consider dict subclass. But for new APIs, plain dataclass is cleaner.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-07 | Initial version based on TASK-200/201/202 research |

---

## References

1. [Function Signature Standard](function-signature-standard.md) - Complementary standard
2. [Professional API Patterns](../research/professional-api-patterns.md) - SciPy OptimizeResult case study
3. [UX Patterns](../research/ux-patterns-for-technical-apis.md) - Tuple Mystery problem
4. Python dataclasses documentation: https://docs.python.org/3/library/dataclasses.html
5. SciPy OptimizeResult source: https://github.com/scipy/scipy/blob/main/scipy/optimize/_optimize.py
6. Scikit-learn result conventions: https://scikit-learn.org/stable/glossary.html

---

**END OF DOCUMENT**
