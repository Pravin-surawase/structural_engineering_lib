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
NumPy signatures are heavily standardized.
- **Pattern:** `func(x, /, ..., out=None, *, where=True, casting='same_kind', order='K', dtype=None, subok=True[, signature, extobj])`
- **Positional-Only Arguments:** NumPy extensively uses `/` to enforced positional-only arguments for the primary subject (the array).
- **Keyword-Only Arguments:** Options like `dtype`, `keepdims` are almost always keyword-only or optional.

**Example:**
```python
# numpy.sum(a, axis=None, dtype=None, out=None, keepdims=<no value>, initial=<no value>, where=<no value>)
import numpy as np
arr = np.array([1, 2, 3])
# Usage enforced by convention/signature
result = np.sum(arr, axis=0, dtype=float)
```

#### B. Return Types
- **Scalars vs Arrays:** Returns 0-d arrays for scalar reductions, preserving type information.
- **Views vs Copies:** Explicit documentation on whether a return is a view (memory efficiency) or copy.
- **Output Parameters:** `out` parameter allows in-place operation optimization, critical for performance engineering.

#### C. Error Handling
- **Type Promotion:** Automatic type promotion (int -> float) rather than errors for compatible types.
- **Floating Point Errors:** Configurable via `np.seterr` (ignore, warn, raise, call) rather than hard-coded behavior.

### 2.2 SciPy
**Focus:** Scientific algorithms, integration, optimization.

#### A. Result Object Pattern
SciPy rarely returns tuples for complex results. It uses `OptimizeResult` (a `dict` subclass with attribute access).

**Pattern:**
```python
from scipy.optimize import minimize
res = minimize(fun, x0)
# res is an object, not a tuple
print(res.x)       # Solution
print(res.success) # Boolean status
print(res.message) # Human-readable status
```

**Why we should adopt this:**
- Extensible: Can add new return fields without breaking unpacking.
- Self-documenting: `res.success` is clearer than `res[2]`.
- Backward compatible.

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
