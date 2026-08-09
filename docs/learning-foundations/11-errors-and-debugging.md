---
owner: Main Agent
status: active
last_updated: 2026-08-07
doc_type: tutorial
complexity: beginner
tags: [learning, foundations]
---

# Module 11: Errors, Debugging, and Logging

## The Big Idea

Errors are inevitable. What matters is how your code **handles** them, how you **find** them, and how you **fix** them. Good error handling turns a crash into a helpful message. Good debugging turns hours of confusion into minutes of targeted investigation.

---

## Part 1: Types of Errors

### Syntax Errors — Code that can't even run
```python
# Missing colon
def calculate_area(width, height)
    return width * height
# SyntaxError: expected ':'
```
**When:** Before code runs. Caught by the editor or interpreter.
**Fix:** Read the error message — it points to the exact line.

### Runtime Errors — Code that crashes while running
```python
def divide(a, b):
    return a / b

divide(10, 0)
# ZeroDivisionError: division by zero
```
**When:** During execution. Input was unexpected.
**Fix:** Add checks before the operation.

### Logic Errors — Code that runs but gives wrong answers
```python
def calculate_area(width, height):
    return width + height  # Should be * not +

calculate_area(300, 500)  # Returns 800, should be 150000
```
**When:** Never crashes — just silently wrong. **The most dangerous kind.**
**Fix:** Tests with known expected answers (benchmark tests).

### Type Errors — Wrong data type
```python
"hello" + 5
# TypeError: can only concatenate str to str

# TypeScript catches these BEFORE running:
const width: number = "hello";
// Error: Type 'string' is not assignable to type 'number'
```

---

## Part 2: Error Handling in Python

### try / except — Catching errors
```python
def safe_divide(a: float, b: float) -> float:
    try:
        return a / b
    except ZeroDivisionError:
        raise ValueError("Cannot divide by zero")
```

### Common exception types:

| Exception | When | Example |
|-----------|------|---------|
| `ValueError` | Wrong value | `int("hello")` |
| `TypeError` | Wrong type | `"hello" + 5` |
| `KeyError` | Missing dict key | `d["missing_key"]` |
| `IndexError` | List index out of range | `[1,2,3][10]` |
| `FileNotFoundError` | File doesn't exist | `open("nope.txt")` |
| `ZeroDivisionError` | Division by zero | `10 / 0` |
| `ImportError` | Can't import module | `import nonexistent` |

### Best practices:
```python
# ✅ GOOD: Catch specific exceptions
try:
    result = calculate_ast(b_mm, d_mm, fck, fy, Mu_kNm)
except ValueError as e:
    # Handle domain errors (negative width, etc.)
    print(f"Invalid input: {e}")

# ❌ BAD: Catch everything (hides real bugs)
try:
    result = calculate_ast(b_mm, d_mm, fck, fy, Mu_kNm)
except:  # Catches EVERYTHING — even keyboard interrupt
    print("Something went wrong")  # Useless message

# ❌ BAD: Silently swallow errors
try:
    result = calculate_ast(b_mm, d_mm, fck, fy, Mu_kNm)
except ValueError:
    pass  # Error ignored — nobody will ever know
```

### Raising your own errors:
```python
def calculate_ast_required(b_mm: float, d_mm: float, fck: float,
                           fy: float, Mu_kNm: float) -> float:
    if b_mm <= 0:
        raise ValueError(f"Width must be positive, got {b_mm}")
    if d_mm <= 0:
        raise ValueError(f"Depth must be positive, got {d_mm}")
    if fck < 15 or fck > 80:
        raise ValueError(f"fck must be 15-80 N/mm², got {fck}")

    # ... calculation ...
    return ast
```

---

## Part 3: Error Handling in TypeScript

### try / catch:
```typescript
async function designBeam(input: BeamInput): Promise<BeamResult> {
  try {
    const response = await fetch("/api/v1/design/beam", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      console.error("Design failed:", error.message);
    }
    throw error;  // Re-throw so the UI can handle it
  }
}
```

### Showing errors to users (React):
```tsx
function DesignView() {
  const [error, setError] = useState<string | null>(null);

  const handleDesign = async () => {
    try {
      setError(null);
      const result = await designBeam(inputs);
      setResult(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    }
  };

  return (
    <div>
      {error && (
        <div className="bg-red-100 text-red-700 p-3 rounded">
          ⚠️ {error}
        </div>
      )}
      <button onClick={handleDesign}>Design</button>
    </div>
  );
}
```

---

## Part 4: HTTP Error Codes — Errors Across the Network

When the frontend calls the backend, errors are communicated via HTTP status codes.

```
Frontend                              Backend
   │                                     │
   │  POST /design/beam                  │
   │  {"b_mm": -300}                     │
   │ ──────────────────────────────────→ │
   │                                     │  Pydantic: b_mm must be > 0
   │  ←──────────────────────────────── │
   │  422 Unprocessable Entity           │
   │  {"detail": "b_mm must be > 0"}     │
   │                                     │
```

### Error flow through layers:

```
Layer 4 (Math):      ValueError("width must be positive")
                           │
                           ▼
Layer 3 (Service):   Catches ValueError, re-raises
                           │
                           ▼
Layer 2 (Backend):   HTTPException(status_code=422, detail="width must be positive")
                           │
                           ▼
Layer 1 (Frontend):  Response.status === 422
                     Shows: "⚠️ width must be positive"
```

### FastAPI error handling:
```python
from fastapi import HTTPException

@router.post("/design/beam")
def design_beam(input: BeamInput):
    try:
        result = design_beam_is456(**input.model_dump())
        return result
    except ValueError as e:
        # Domain error → 422 (client sent bad data)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        # Unexpected error → 500 (our bug)
        raise HTTPException(status_code=500, detail="Internal server error")
```

---

## Part 5: Logging — Recording What Happened

**Logging** writes messages about what your program is doing. When something goes wrong, logs tell you what happened.

### Python logging:
```python
import logging

logger = logging.getLogger(__name__)

def design_beam(b_mm, d_mm, fck, fy, Mu_kNm):
    logger.info(f"Designing beam: b={b_mm}, d={d_mm}, fck={fck}")

    try:
        ast = calculate_ast(b_mm, d_mm, fck, fy, Mu_kNm)
        logger.info(f"Result: Ast={ast:.1f} mm²")
        return ast
    except ValueError as e:
        logger.warning(f"Invalid input: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise
```

### Log levels (from least to most serious):

| Level | When | Example |
|-------|------|---------|
| `DEBUG` | Detailed tracing | `"Calculating xu/d ratio: 0.456"` |
| `INFO` | Normal events | `"Designing beam: b=300, d=500"` |
| `WARNING` | Unexpected but handled | `"Steel ratio near maximum: 0.038"` |
| `ERROR` | Something failed | `"Database connection failed"` |
| `CRITICAL` | System is broken | `"Out of memory, shutting down"` |

### Log level configuration:
```python
# Development: show everything
logging.basicConfig(level=logging.DEBUG)

# Production: only warnings and above
logging.basicConfig(level=logging.WARNING)
```

### Frontend logging (console):
```typescript
console.log("Input:", input);       // Normal info
console.warn("Steel ratio high");   // Warning
console.error("API call failed");   // Error
```

---

## Part 6: Debugging — Finding the Bug

### Strategy 1: Read the error message
```
Traceback (most recent call last):
  File "flexure.py", line 45, in calculate_ast
    xu = 0.87 * fy * Ast / (0.36 * fck * b_mm)
ZeroDivisionError: float division by zero
```
The traceback tells you: file, line, function, and what went wrong.

### Strategy 2: Add print/log statements
```python
def calculate_ast(b_mm, d_mm, fck, fy, Mu_kNm):
    print(f"DEBUG: b_mm={b_mm}, d_mm={d_mm}, fck={fck}, fy={fy}, Mu={Mu_kNm}")

    Mu_Nmm = Mu_kNm * 1e6
    print(f"DEBUG: Mu_Nmm = {Mu_Nmm}")

    ratio = Mu_Nmm / (fck * b_mm * d_mm**2)
    print(f"DEBUG: ratio = {ratio}")
    # ... continue ...
```

### Strategy 3: Use a debugger
VS Code has a built-in debugger:
1. Click left of a line number to set a **breakpoint** (red dot)
2. Press F5 to start debugging
3. Code stops at the breakpoint
4. Inspect variables in the sidebar
5. Step through line by line (F10)

### Strategy 4: Binary search
When you don't know where the bug is:
```
1. The code has 100 lines
2. Add a print at line 50 — is the data correct there?
   YES → Bug is in lines 51-100
   NO  → Bug is in lines 1-50
3. Add a print at line 75 (or 25)
4. Repeat until you find the exact line
```

### Strategy 5: Reproduce with a test
```python
def test_bug_fix():
    """This used to return wrong answer — now it should be correct."""
    result = calculate_ast(b_mm=300, d_mm=500, fck=25, fy=500, Mu_kNm=150)
    assert abs(result - 1206.5) < 1.0  # Known correct answer
```

---

## Part 7: Error Propagation Across Layers

How does an error travel from the math layer to the user's screen?

```
LAYER                 WHAT HAPPENS                      ERROR FORM
──────               ──────────────                    ──────────

Math (IS 456)        raise ValueError("b_mm must       Python exception
                     be positive, got -300")

Service (api.py)     ValueError propagates up           Python exception
                     (not caught here)

Backend (FastAPI)    except ValueError as e:             HTTP response
                     raise HTTPException(422, str(e))   {"detail": "b_mm must
                                                         be positive, got -300"}

Frontend (React)     if (!response.ok) {                UI state
                       setError(error.detail)
                     }

User's screen        ┌─────────────────────────┐       Visual feedback
                     │ ⚠️ b_mm must be positive, │
                     │    got -300               │
                     └─────────────────────────┘
```

**Key principle:** Each layer translates the error into the appropriate format for the next layer.

---

## Part 8: Common Debugging Scenarios

### "It worked yesterday"
```bash
# What changed since yesterday?
git log --oneline --since="yesterday"
git diff HEAD~5  # Compare last 5 commits
```

### "Works on my machine but fails in CI"
- Different Python version?
- Missing environment variable?
- Different OS (Mac vs Linux)?
- Missing dependency in requirements.txt?

### "The API returns empty/wrong data"
```bash
# Test the API directly
curl -X POST http://localhost:8000/api/v1/design/beam \
  -H "Content-Type: application/json" \
  -d '{"b_mm": 300, "d_mm": 500, "fck": 25, "fy": 500, "Mu_kNm": 150}'

# Check server logs
# Look at the terminal where uvicorn is running
```

### "React component doesn't update"
```typescript
// Check: Are you mutating state instead of creating new state?
// ❌ BAD: Mutating
const handleClick = () => {
  result.value = 42;  // React won't see this change
};

// ✅ GOOD: New state
const handleClick = () => {
  setResult({ ...result, value: 42 });  // React re-renders
};
```

---

## Part 9: Error Handling Patterns

### Pattern 1: Fail fast
```python
def calculate(b_mm, d_mm):
    if b_mm <= 0:
        raise ValueError(f"b_mm must be positive, got {b_mm}")
    if d_mm <= 0:
        raise ValueError(f"d_mm must be positive, got {d_mm}")
    # Only reach here if inputs are valid
    return b_mm * d_mm
```

### Pattern 2: Return errors instead of throwing
```python
from dataclasses import dataclass

@dataclass
class Result:
    value: float | None
    error: str | None

def safe_calculate(b_mm, d_mm) -> Result:
    if b_mm <= 0:
        return Result(value=None, error="b_mm must be positive")
    return Result(value=b_mm * d_mm, error=None)
```

### Pattern 3: Default values for non-critical errors
```python
def get_exposure_factor(condition: str) -> float:
    factors = {"mild": 1.0, "moderate": 1.2, "severe": 1.5}
    return factors.get(condition, 1.0)  # Default to 1.0 if unknown
```

---

## Part 10: Exercises

1. **Read a traceback:** Run a Python file with a deliberate error. Read the full traceback. What file, line, and function caused the error?
2. **Add error handling:** Take a function without try/except. Add proper error handling with specific exception types.
3. **Use the debugger:** Set a breakpoint in any IS 456 calculation. Step through line by line. Watch how variables change.
4. **Trace an API error:** Send invalid data to the API. Follow the error from HTTP response → server logs → Python exception.

---

## Part 11: Self-Check

1. **What are the 3 types of errors?** Syntax (can't run), runtime (crashes), logic (wrong answer).
2. **Why is catching broad exceptions bad?** It hides real bugs — you don't know what actually failed.
3. **What's the difference between ERROR and WARNING log levels?** ERROR = something failed. WARNING = something unexpected but handled.
4. **How does an error reach the user from the math layer?** ValueError → HTTPException(422) → JSON response → React state → UI message.
5. **What's the fastest debugging strategy?** Read the error message first. It usually tells you exactly what's wrong.
6. **Why are logic errors the most dangerous?** They never crash — they silently produce wrong answers.

---

## Key Takeaway

> Errors are **information**, not failures. A good error message tells you exactly what went wrong and where. Good error handling turns crashes into helpful messages. Good logging leaves a trail for future debugging. The goal isn't to prevent all errors — it's to detect them fast and fix them easily.

**Next:** [Module 12 — Starting From Scratch](12-starting-from-scratch.md) brings everything together into a practical guide for starting your own project.
