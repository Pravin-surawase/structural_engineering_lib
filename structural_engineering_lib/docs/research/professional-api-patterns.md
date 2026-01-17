# Professional Python Library API Patterns Research

**Status:** Draft
**Task:** TASK-200
**Date:** 2026-01-07
**Author:** AI Researcher

## 1. Executive Summary

This document analyzes API design patterns from top-tier Python libraries (NumPy, SciPy, Pandas, Requests, Pydantic, Scikit-learn) to establish professional standards for `structural_engineering_lib`. The goal is to move from "functional script" patterns to "professional library" patterns.

**Key Findings:**
1. **Explicit > Implicit:** Top libraries favor explicit types, shapes, and units.
2. **Predictable Signatures:** Consistent argument ordering (Subject -> Parameters -> Options) is universal.
3. **Rich Result Objects:** Complex calculations return specialized objects, not raw tuples.
4. **"Pit of Success":** APIs are designed so the default usage is the correct usage.

---

## 2. Scientific Computing Libraries Analysis

### 2.1 NumPy
**Focus:** High-performance array computing, mathematical consistency.

#### A. Function Signatures
NumPy signatures are heavily standardized with a clear philosophy: **"Subject first, options last"**.

**The Universal Pattern:**
```python
func(x, /, ..., out=None, *, where=True, casting='same_kind', order='K', dtype=None, subok=True)
```

**Key Insights:**
- **Positional-Only (/):** The `/` separator enforces positional-only args for the primary subject (the array). This prevents `np.sum(a=array)` (confusing) and forces `np.sum(array)` (clear).
- **Keyword-Only (*):** Configuration options after `*` MUST be named: `np.sum(arr, axis=0, keepdims=True)` is readable at call site.
- **Consistency:** Every mathematical function follows this pattern. Users learn once, apply everywhere.

**Real Examples:**
```python
import numpy as np

# Example 1: Reduction operations
arr = np.array([[1, 2], [3, 4]])
np.sum(arr, axis=0, keepdims=True)  # Shape (1, 2), preserves dimensions
np.sum(arr, axis=0, keepdims=False) # Shape (2,), collapses dimension

# Example 2: Type control
np.sum(arr, dtype=np.float64)  # Force output type
np.sum(arr, out=result_buffer) # Pre-allocated output for performance

# Example 3: Conditional operations
np.sum(arr, where=arr > 2)  # Sum only elements > 2
```

**Why This Matters for Structural Lib:**
- Our `calculate_ast(...)` should follow: `calculate_ast(Mu, b, d, /, *, fck=20, fy=415, **options)`
- Primary inputs (Mu, b, d) are positional (they're always needed, order is logical).
- Material properties (fck, fy) are keyword-only (less likely to be memorized, need explicit names).

#### B. Return Types & The `out` Parameter
NumPy's `out` parameter is performance-critical for iterative calculations.

**Pattern:**
```python
# Without out: allocates new array every iteration (slow)
for i in range(1000):
    result = np.sin(arr)  # 1000 allocations!

# With out: reuses same buffer (fast)
result = np.empty_like(arr)
for i in range(1000):
    np.sin(arr, out=result)  # 1 allocation total
```

**Application to Structural Lib:**
Our batch processing (job runner) could benefit:
```python
# Bad: allocates 100 result objects
results = [design_beam(span, load, ...) for beam in beams]

# Better: preallocate results array
results = [BeamResult() for _ in beams]
for i, beam in enumerate(beams):
    design_beam(beam.span, beam.load, out=results[i])
```

#### C. Error Handling Philosophy
NumPy doesn't raise exceptions for "soft errors" like division by zero or overflow. Instead:

**Configurable Error Modes:**
```python
import numpy as np

# Default: warnings
np.array([1, 2]) / np.array([0, 1])  # Warns about division by zero, returns [inf, 2]

# Strict mode: raise exceptions
with np.errstate(divide='raise'):
    np.array([1, 2]) / np.array([0, 1])  # Raises FloatingPointError

# Silent mode: ignore
with np.errstate(divide='ignore'):
    np.array([1, 2]) / np.array([0, 1])  # Returns [inf, 2], no warning
```

**Lesson for Structural Lib:**
- **Validation Errors** (negative depth) → Raise immediately.
- **Convergence Warnings** (iteration didn't converge) → Configurable via context manager or parameter.
- **Code Violations** (span/depth ratio) → Collect all, return in result object.

### 2.2 SciPy
**Focus:** Scientific algorithms, integration, optimization.

#### A. Result Object Pattern (Deep Dive)
SciPy pioneered the "Result Object" pattern that we must adopt. Instead of returning tuples, SciPy returns rich objects.

**The `OptimizeResult` Class:**
```python
from scipy.optimize import minimize, OptimizeResult

# Standard usage
def rosenbrock(x):
    return sum(100.0*(x[1:]-x[:-1]**2.0)**2.0 + (1-x[:-1])**2.0)

x0 = [1.3, 0.7, 0.8]
res = minimize(rosenbrock, x0, method='nelder-mead')

# Result is NOT a tuple - it's a rich object
print(type(res))  # <class 'scipy.optimize.optimize.OptimizeResult'>

# Access by attribute (self-documenting)
print(res.x)          # Solution: [1.0, 1.0, 1.0]
print(res.fun)        # Final function value: 0.0
print(res.success)    # Boolean: True
print(res.message)    # Human-readable: 'Optimization terminated successfully.'
print(res.nit)        # Number of iterations: 48
print(res.nfev)       # Number of function evaluations: 90

# Can still unpack if needed (backward compatibility)
x_opt, fun_val = res.x, res.fun
```

**Under the Hood:**
```python
# OptimizeResult is actually a dict subclass with attribute access
class OptimizeResult(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value
```

**Why This Is Brilliant:**
1. **Extensibility:** Add new fields (`res.jac` for Jacobian) without breaking old code.
2. **Self-Documentation:** `res.success` beats `res[4]`.
3. **Backward Compatibility:** Can still do `x, fun = res.x, res.fun`.
4. **JSON Serializable:** It's a dict, so `json.dumps(dict(res))` works.

#### B. Multiple Return Strategies Compared

**SciPy's Evolution:**
```python
# OLD (pre-1.0): Tuple hell
eigvals, eigvecs = scipy.linalg.eig(matrix)  # OK for 2 returns
x, fun, jac, hess, nfev, njev = minimize(...)  # Nightmare for 6 returns

# NEW (post-1.0): Result objects
result = scipy.optimize.minimize(...)
result.x, result.fun, result.jac, result.hess, result.nfev, result.njev  # Clear!
```

**Structural Lib Application:**
```python
# Current (BAD):
ast, asc, bar_count, bar_dia, status = design_flexure(Mu, b, d, fck, fy)
# What was index 2? Count or diameter? Must check docs every time.

# Proposed (GOOD):
result = design_flexure(Mu, b, d, /, fck=20, fy=415)
result.ast_provided    # Self-documenting
result.asc_provided    # Clear meaning
result.bars_tension    # Obviously bars, not area
result.bar_diameter    # Explicit unit (mm implied by convention)
result.status          # OK/FAIL/WARNING
result.utilization     # 0.0-1.0, how close to limit
result.warnings        # List[str] of non-fatal issues
```

#### C. Metadata & Debugging Information
SciPy result objects include debugging metadata:

```python
from scipy.optimize import minimize

res = minimize(lambda x: x**2, x0=[10], method='BFGS')

# Metadata for debugging
print(res.message)  # "Optimization terminated successfully."
print(res.nit)      # 3 iterations
print(res.nfev)     # 8 function evaluations
print(res.njev)     # 4 Jacobian evaluations

# This is CRITICAL for engineering:
# If design takes 5 seconds, we need to know:
# - How many iterations?
# - Did it converge?
# - How close are we to the limit?
```

**Structural Lib Debugging Pattern:**
```python
@dataclass(frozen=True)
class FlexureDesignResult:
    # Primary results
    ast_provided: float
    asc_provided: float
    status: Literal["OK", "FAIL", "WARNING"]

    # Debugging metadata
    iterations: int = 0
    convergence_tolerance: float = 1e-6
    calculation_time_ms: float = 0.0
    warnings: list[str] = field(default_factory=list)

    # Calculation trail (for verification)
    Mu_lim: float = 0.0
    xu_max: float = 0.0
    neutral_axis_depth: float = 0.0
```

### 2.3 Pandas
**Focus:** Data manipulation, fluent interfaces.

#### A. Method Chaining & Fluent API
Pandas methods often return a new Series/DataFrame, enabling chaining.
```python
# Fluent pattern
df.dropna().groupby('A').sum().reset_index()
```
*Note:* While powerful, this can make debugging hard. Pandas mitigates this with clear "inplace=False" defaults.

#### B. "Inplace" Parameter
The `inplace=Boolean` pattern is ubiquitous but often discouraged in modern pandas (deprecation discussions active).
**Lesson:** Prefer returning new objects. `inplace` mutation complicates memory management and method chaining.

---

## 3. General-Purpose Libraries Analysis

### 3.1 Requests
**Focus:** "HTTP for Humans" - Usability first.

#### A. Sensible Defaults
Requests is famous for inferring intent.
```python
# Complex under the hood, simple interface
requests.get('https://api.github.com/user', auth=('user', 'pass'))
```
- Content-Type headers inferred.
- Encoding inferred.
- Connection pooling handled automatically.

#### B. Progressive Disclosure
Basic usage is one line. Advanced usage (Sessions, Adapters) is available but hidden.
**Lesson:** Simple features should be simple imports. Complex features should be in submodules.

### 3.2 Pydantic
**Focus:** Data validation, type coercion.

#### A. Validation / Parsing Separation
Pydantic parses *into* the type, it doesn't just validate.
```python
class Beam(BaseModel):
    length: float = Field(gt=0, description="Length in mm")

# Input: string "3000" -> Output: float 3000.0
b = Beam(length="3000")
```
**Lesson:** API inputs should be forgiving but internal storage strict. "Parse, don't validate."

#### B. Error Aggregation
Pydantic collects *all* validation errors, not just the first one.
```json
// ValidationError:
[
  {"loc": ["width"], "msg": "field required", "type": "value_error.missing"},
  {"loc": ["depth"], "msg": "value must be > 0", "type": "value_error"}
]
```
**Lesson:** We must return all design check failures at once, not stop at the first failure.

---

## 4. Machine Learning Libraries Analysis

### 4.1 Scikit-learn
**Focus:** Consistent API across interchangeable algorithms.

#### A. The Estimator Interface
Every algorithm implements `fit(X, y)` and `predict(X)`.
**Lesson:** Consistent "verbs" (verbs as methods) reduce cognitive load. In our case: `calculate_`, `check_`, `design_`.

#### B. Validation Checks
`check_is_fitted(estimator)` pattern ensures state validity before operation.

---

## 5. Comparison Matrix

| Feature | NumPy | Pandas | Requests | Pydantic | Scikit-learn | **Structural Lib Goal** |
|---------|-------|--------|----------|----------|--------------|-------------------------|
| **Signature Style** | Positional + KW | Method heavy | KW heavy | Class fields | Class init + Methods | **Functional + Dataclasses** |
| **Input Validation** | Casting/Coercion | Loose | Inference | Strict Parsing | Check arrays | **Strict Types + Units** |
| **Return Types** | `ndarray` | `DataFrame`/`Series` | `Response` obj | `BaseModel` | Arrays/Self | **Result Objects** |
| **Error Handling** | Warnings/settings | Exceptions | Exceptions | Aggregated List | Exceptions | **Hierarchical + Aggregated** |
| **Defaults** | `None` (sentinel) | `None` | Sensible Defaults | Required/Default | Sensible Defaults | **Explicit Defaults (SP:16)** |
| **Mutability** | Mutable | Mixed (Copy default) | Mutable internal | Immutable (config) | Mutable state | **Immutable Results** |

---

## 6. Recommendations for Structural Lib

### 6.1 Function Signatures
**Adopt the "Subject-Config-Options" Pattern:**
```python
def design_beam(
    # 1. Subject (Positional strict or logical first)
    span: float,
    load: float,
    # 2. Key configuration (Keyword or Positional)
    width: float,
    depth: float,
    # 3. Options / Toggles (Keyword Only)
    *,
    concrete_grade: str = "M20",
    steel_grade: str = "Fe415",
    cover: float = 25.0
) -> BeamDesignResult:
    ...
```

### 6.2 Return Values: The "Result Object"
Stop returning tuples `(ast, asc, cr)`. Start returning Typed Objects.

```python
@dataclass(frozen=True)
class ReinforcementResult:
    ast_provided: float
    num_bars: int
    bar_dia: int
    status: Literal["OK", "FAIL"]
    # Metadata for debugging
    calc_log: List[str] = field(default_factory=list)
```

### 6.3 Error Handling
Adopt **Error Aggregation** for compliance checks. Don't raise on the first IS:456 violation. Collect them.

```python
result = check_compliance(beam)
if not result.passed:
    # Returns list of ALL failures
    print(result.failures)
    # ["Span/Depth ratio exceeded: 22 > 20", "Min reinforcement not met"]
```

### 6.4 Documentation
- **Docstrings:** Google Style is standard and readable.
- **Type Hints:** 100% coverage required.
- **Examples:** Every public function must have a `Examples:` block in the docstring.

### 6.5 Top 10 Patterns to Adopt
1. **Keyword-Only Arguments (`*`)**: Force clarity for boolean flags and optional config.
2. **Rich Return Objects**: Use Pydantic models or Frozen Dataclasses for returns.
3. **Parse Don't Validate**: Coerce units where safe (e.g. `int` -> `float`), fail where ambiguous.
4. **Sentinel `None`**: Use `None` for "calculate this for me" vs explicit value.
5. **Error Hierarchy**: Define `StructuralError`, `CalculationError`, `ComplianceError`.
6. **Fluent Builders**: For complex object construction (Job setup).
7. **Input Models**: Pass `BeamParams` objects instead of 20 arguments for complex functions.
8. **Explicit Exports**: Use `__all__` to define public API surface.
9. **Deprecation Decorators**: Explicitly mark old functions when refactoring.
10. **Vectorization Ready**: Design core funcs to possibly accept arrays in future (NumPy compatibility).

### 6.6 Top 5 Anti-Patterns to Avoid
1. **The "God Function"**: Signatures with 20+ positional arguments (use `BeamParams` object).
2. **Mystery Tuples**: Returning `(2450, 3, 12)` without context (use `Result` objects).
3. **Silent Defaults**: Defaulting critical loads/grades without user awareness (force explicit inputs or standardized defaults).
4. **"Print" Debugging**: Libraries should log, not print.
5. **Mixed Return Types**: Returning `None` on failure mixed with `float` on success (raise exceptions or return Result with status).

---

## 7. Advanced Patterns & Deep Dives

### 7.1 The "Builder Pattern" (Complex Object Construction)
When inputs grow complex, top libraries use the Builder pattern.

**Example from scikit-learn:**
```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# Instead of: model = SVC(C=1.0, kernel='rbf', gamma='scale', ...) with 20 params
# Use a builder:
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', SVC(C=1.0, kernel='rbf'))
])
```

**Application to Structural Lib:**
```python
# Instead of: design_beam(span, load, width, depth, fck, fy, cover, exposure, ...)
# Use a builder:
from structural_lib import BeamDesigner

designer = (BeamDesigner()
    .set_geometry(span=5000, width=230, depth=450)
    .set_loading(dead_load=10, live_load=5)
    .set_materials(concrete='M20', steel='Fe415')
    .set_environment(exposure='moderate', fire_rating=90)
    .design())

result = designer.result
```

### 7.2 The "Validator" Pattern (Pydantic Deep Dive)
Pydantic's validation is more sophisticated than simple type checking.

**Real Example:**
```python
from pydantic import BaseModel, Field, validator, root_validator

class BeamInput(BaseModel):
    span_mm: float = Field(gt=0, le=12000, description="Span in mm")
    width_mm: float = Field(ge=150, le=600)
    depth_mm: float = Field(ge=200, le=1200)
    concrete_grade: str = Field(regex=r"M\d+")

    @validator('depth_mm')
    def depth_must_exceed_width(cls, v, values):
        if 'width_mm' in values and v < values['width_mm']:
            raise ValueError('Depth must be >= width for typical beams')
        return v

    @root_validator
    def check_span_depth_ratio(cls, values):
        span = values.get('span_mm')
        depth = values.get('depth_mm')
        if span and depth and (span / depth) > 25:
            raise ValueError(f'Span/depth ratio {span/depth:.1f} > 25 (preliminary limit)')
        return values

# Usage:
try:
    beam = BeamInput(span_mm=6000, width_mm=230, depth_mm=200, concrete_grade='M20')
except ValidationError as e:
    print(e.json())  # Returns ALL errors, not just first
```

**Output:**
```json
[
  {
    "loc": ["depth_mm"],
    "msg": "Depth must be >= width for typical beams",
    "type": "value_error"
  },
  {
    "loc": ["__root__"],
    "msg": "Span/depth ratio 30.0 > 25 (preliminary limit)",
    "type": "value_error"
  }
]
```

### 7.3 The "Context Manager" Pattern (Resource & State Management)
NumPy and Pandas use context managers for temporary state changes.

**NumPy's `errstate`:**
```python
import numpy as np

# Temporarily change error handling
with np.errstate(divide='ignore', invalid='ignore'):
    result = np.log(arr)  # Doesn't warn about log(0)
# Error handling reverts after block
```

**Application to Structural Lib:**
```python
from structural_lib import DesignContext

# Temporary override for a batch of beams
with DesignContext(code='IS456:2000', partial_safety_factors={'concrete': 1.5, 'steel': 1.15}):
    for beam in beams:
        result = design_beam(beam.span, beam.load)
        # Uses overridden PSF values
# Reverts to defaults after block
```

### 7.4 The "Deprecation" Pattern (API Evolution)
Professional libraries deprecate gracefully, not abruptly.

**Pandas Example:**
```python
import warnings

def old_function(x):
    warnings.warn(
        "old_function is deprecated and will be removed in v2.0. "
        "Use new_function instead.",
        FutureWarning,
        stacklevel=2
    )
    return new_function(x)
```

**Structural Lib Deprecation Strategy:**
```python
from warnings import warn
from functools import wraps

def deprecated(replacement=None, version="1.0.0"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            msg = f"{func.__name__} is deprecated and will be removed in v{version}."
            if replacement:
                msg += f" Use {replacement} instead."
            warn(msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage:
@deprecated(replacement="design_beam_is456", version="1.0.0")
def calculate_beam(span, load):
    return design_beam_is456(span, load)
```

---

## 8. Code Quality Patterns

### 8.1 Type Hints (Beyond the Basics)
Professional libraries use advanced type hints.

**Example:**
```python
from typing import Union, Optional, Literal, TypedDict, Protocol
from dataclasses import dataclass

# Union types for flexible inputs
def calculate_load(
    value: Union[float, int, 'LoadCase']  # Accept number or custom type
) -> float:
    ...

# Literal for restricted strings (better than Enum for simple cases)
def set_exposure(
    level: Literal['mild', 'moderate', 'severe', 'very_severe', 'extreme']
) -> None:
    ...

# Protocol for structural typing (duck typing with type safety)
class Designable(Protocol):
    def calculate_capacity(self) -> float: ...
    def check_compliance(self) -> bool: ...

def optimize_section(element: Designable) -> float:
    # Works with ANY object that has these methods
    ...
```

### 8.2 The `__all__` Export Pattern
Control your public API surface explicitly.

**Example:**
```python
# structural_lib/flexure.py
__all__ = [
    'design_singly_reinforced',
    'design_doubly_reinforced',
    'FlexureResult',
    'FlexureInput'
]

# Private helpers (not exported)
def _calculate_neutral_axis_depth(...):
    ...

# Users can only import explicitly exported names
from structural_lib.flexure import *  # Only gets __all__ items
```

### 8.3 The "Immutable Result" Pattern
Results should be immutable to prevent bugs.

**Pattern:**
```python
from dataclasses import dataclass

# BAD: Mutable result
@dataclass
class Result:
    ast: float

result = design_beam(...)
result.ast = -1000  # Oops! Silently corrupts result

# GOOD: Immutable result
@dataclass(frozen=True)
class Result:
    ast: float

result = design_beam(...)
result.ast = -1000  # Raises FrozenInstanceError
```

---
