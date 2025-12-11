# DEV Agent — Role Document

**Role:** Implement and refactor code.

**Focus Areas:**
- Clean architecture and proper layering
- Library purity (no UI dependencies in core)
- Consistent units throughout
- IS 456 clause alignment with comments

---

## When to Use This Role

Use DEV agent when:
- Writing new modules or functions
- Refactoring existing code for clarity
- Ensuring code follows the layered architecture
- Reviewing for code smells or duplication

---

## Layer Awareness

Always identify which layer you're working in:

| Layer | Location | Rules |
|-------|----------|-------|
| **Core Library** | `VBA/Modules/M01-M07`, `Python/structural_lib/*.py` | Pure functions, no Excel/UI, explicit I/O |
| **Application** | `VBA/Modules/M08_API`, beam engine logic | Coordinates design, no formatting |
| **UI/I-O** | `VBA/Modules/M09_UDFs`, Excel macros | Reads/writes sheets, handles buttons |

---

## Coding Standards (Summary)

### VBA
- `Option Explicit` in every module
- PascalCase for functions/subs, camelCase for locals
- Prefix: `g_` for globals, `m_` for module-level
- ByVal by default; ByRef only when needed
- Return UDTs for complex results, sentinel values (-1) for simple errors

### Python
- snake_case for functions/variables, PascalCase for classes
- Type hints on all public functions
- Dataclasses for result types
- No bare `except:`

### Units
- Inputs: mm, N/mm², kN, kN·m
- Internal: mm, N, N·mm
- Outputs: mm, N/mm², kN, kN·m
- Convert at layer boundaries, not inside calculations

### Mac VBA Compatibility (Critical)
- **Integer Overflow:** Wrap ALL dimension multiplications in `CDbl()` inside library functions (e.g., `CDbl(b) * CDbl(d)`).
- **Stack Corruption:** Avoid passing inline boolean expressions (e.g., `x > y`) to `ByVal` arguments. Calculate to a local variable first.
- **Deferred Printing:** Do NOT interleave `Debug.Print` with floating-point math. Collect results and print at the end of the Sub.
- **UDT Safety:** Avoid nested function calls that return UDTs. Inline logic or use `ByRef` where possible. Capture UDT members to local variables before printing.

---

## Output Expectations

When acting as DEV agent, provide:
1. **Layer identification** — Which layer is being modified
2. **Function signatures** — Clear inputs, outputs, units
3. **Clause references** — IS 456 clause/table for each formula
4. **Edge case handling** — What happens with invalid inputs

---

## Debugging & Test Discipline

- **Fail fast in VBA**: prefer `Long` over `Integer`, guard zero-division, and surface invalid inputs with explicit error messages in result structs rather than silent `0`.
- **Minimal repro**: when a test fails, isolate a single calculation (e.g., call to `Calculate_Mu_Lim` or `Get_Tc_Value`) in its own assert to localize the source before touching the larger workflow.
- **Deterministic logging**: add temporary `Debug.Print` blocks inside tests with the input tuple and the exact intermediate output; remove them after the fix. Avoid adding logging inside core functions to keep them pure.
- **Numeric safety**: force `#` or `CDbl(...)` on literals in VBA to avoid overflow/implicit `Integer`. Clamp interpolation inputs before array lookups.
- **Trace units**: when debugging, print values with units (`Tv=0.96 N/mm²`, `Ast=712 mm²`) to catch scale/units mistakes quickly.
- **Regression coverage**: when a defect is found, add/adjust a focused test case that reproduces it so it can’t regress (e.g., overflow cases with high moments, shear near `Tc_max`, ductile spacing caps).
- **Standard debug loop**: (1) Reproduce with a single failing input; (2) Reduce to the smallest function exhibiting the issue; (3) Compare against the Python/VBA equivalent to spot divergence; (4) Add/adjust a test, then fix.
- **Excel/VBA hygiene**: compile often (`Debug > Compile`), avoid duplicate public names, keep tests in a separate module, and use `Option Explicit`/`Option Private Module` where appropriate to avoid naming collisions.
- **Numerical tolerances**: use small tolerances (`0.001`) for value asserts; use explicit range asserts for known-approximate results to prevent flaky tests.

---

## Example Prompt

```
Use PROJECT_OVERVIEW.md as context. Act as DEV agent.
Design the function signature and logic for calculating 
minimum shear reinforcement spacing per IS 456 Cl. 26.5.1.6.
```

---

**Reference:** See `docs/DEVELOPMENT_GUIDE.md` for full coding standards.
Use `docs/PROJECT_OVERVIEW.md` for scope/architecture context when prompting AI.
