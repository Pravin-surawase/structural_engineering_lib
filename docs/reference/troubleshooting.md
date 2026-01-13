# Troubleshooting Guide

**Type:** Reference
**Audience:** Developers
**Status:** Production Ready
**Importance:** High
**Created:** 2025-01-01
**Last Updated:** 2026-01-13

---

## VBA Runtime Error 6: Overflow

### The Issue (Pinpointed)

**Root Cause:** VBA evaluates arithmetic expressions **left-to-right** and uses the **smallest possible type** for intermediate results. When you write:

```vb
result = 0.85 * b * d / fy
```

VBA evaluates it as:
1. `0.85 * b` → Double (because `0.85` is Double)
2. `(result of step 1) * d` → **HERE IS THE PROBLEM**

Even though `b` and `d` are declared as `Double` parameters, **VBA may still treat them as 16-bit Integers internally** depending on how they were passed or if they're whole numbers. This causes overflow when `b * d > 32,767`.

**Example:**
- `b = 230`, `d = 450`
- `230 * 450 = 103,500` → **OVERFLOW** (exceeds Integer max of 32,767)

### Why This Happens

1. **VBA's Type Inference is Aggressive:** Even when parameters are `ByVal ... As Double`, VBA sometimes stores small whole numbers as `Integer` internally.
2. **Multiplication Order Matters:** `0.85 * b * d` might still overflow because VBA can reorder or optimize.
3. **The `#` Suffix is Not Enough:** Adding `#` to literals in the **calling code** (test file) doesn't fix the issue inside the **library functions**.

### The Solution

**Wrap ALL dimension multiplications in `CDbl()` INSIDE the library code itself:**

```vb
' WRONG - Can overflow
Ast_min = 0.85 * b * d / fy

' CORRECT - Forces Double arithmetic
Ast_min = 0.85 * CDbl(b) * CDbl(d) / CDbl(fy)
```

### Fixed Locations in This Library

The following expressions in `M06_Flexure.bas` and `M07_Shear.bas` have been fixed:

| Module | Function | Expression |
|--------|----------|------------|
| M06_Flexure | Calculate_Mu_Lim | `k * fck * b * d * d` |
| M06_Flexure | Calculate_Ast_Required | `term1 * ... * b * d` |
| M06_Flexure | Design_Singly_Reinforced | `0.85 * b * d / fy` |
| M06_Flexure | Design_Singly_Reinforced | `0.04 * b * D_total` |

### Known Unresolved Overflows (v0.4.0)
- **Test_Doubly_Reinforced [Design_Doubly_Case1]**:
  - **Error**: `6 - Overflow`
  - **Context**: Occurs when `Design_Doubly_Reinforced` falls back to singly reinforced logic (Mu < Mu_lim) on Mac Excel.
  - **Action**: This error is currently **ignored** and documented as a known pitfall. It does not affect the core singly reinforced or shear modules.

## Compile Error: User-defined type not defined

### The Issue
When compiling or running code, you see:
`Compile error: User-defined type not defined`
highlighting a function signature like `... As FlexureResult`.

### Root Cause
**Import Order Matters.**
Modules like `M06_Flexure` depend on types defined in `M02_Types`. If you import `M06_Flexure` before `M02_Types` is known to the project, VBA cannot resolve the `FlexureResult` type.

### The Solution
Always import `M02_Types.bas` **FIRST**, before any other modules.

**Correct Import Order:**
1. `M02_Types.bas` (Definitions)
2. `M01_Constants.bas` (Constants)
3. `M03_Tables.bas` (Data)
4. ... all other modules ...

## Mac VBA Specific Issues

### UDT Member Access Overflow
On Mac Excel (VBA 7.x), accessing User-Defined Type (UDT) members immediately after a `Debug.Print` statement involving string concatenation can cause `Runtime Error 6: Overflow`.

**Workaround:**
Capture all UDT members into local variables immediately after the function returns, before doing any printing or assertions.

```vb
' BAD - Can crash on Mac
res = Design_Function(...)
Debug.Print "Result: " & res.IsSafe ' <--- Overflow here

' GOOD - Safe pattern
res = Design_Function(...)
Dim isSafe As Boolean: isSafe = res.IsSafe
Debug.Print "Result: " & isSafe
```
| M06_Flexure | Design_Singly_Reinforced | `(Ast * 100) / (b * d)` |
| M06_Flexure | Design_Doubly_Reinforced | Same patterns |
| M07_Shear | Calculate_Tv | `b * d` in condition and division |
| M07_Shear | Design_Shear | `Tc * b * d` |

### Best Practices

1.  **Inside Library Functions:** Always wrap dimension/material variables in `CDbl()` before multiplication:
    ```vb
    result = 0.85 * CDbl(b) * CDbl(d) / CDbl(fy)
    ```

2.  **In Calling Code (Optional):** Use `#` suffix for safety:
    ```vb
    res = Design_Singly_Reinforced(230#, 450#, 500#, 150#, 20#, 415#)
    ```

3.  **Avoid `Integer` for Dimensions:** Always use `Long` or `Double` for any variable that might exceed 32,767.

## Common Issues in Tests

### `AssertTrue (Abs(res.Ast_Required) < 0.001)`
If `res.Ast_Required` is not calculated correctly due to an overflow in the library function, it might be uninitialized or NaN.

### `AssertTrue (res.Vus > 0)`
If `res.Vus` calculation involves `b * d` without `CDbl()`, the intermediate result overflows before assignment.

### `Test_Flexure_CalcOnly` overflow on function call assignment (Mac VBA)
**Issue:** On Mac Excel VBA, overflow can occur when a function returns a Double and assigns it directly, even though the function itself succeeds. The error happens on the **assignment expression**, not inside the function.

**Example of problem:**
```vb
muLim = M06_Flexure.Calculate_Mu_Lim(230#, 450#, 20#, 415#)  ' <-- Overflow here on Mac
```

**Root Cause:** Mac VBA's type coercion during function return can mistakenly treat intermediate literals (like `230#`) as Integers in the call expression, causing overflow before the Double assignment completes.

**Solution:** Store all parameters in Double variables first, then call the function:
```vb
Dim b As Double: b = 230#
Dim d As Double: d = 450#
Dim fck As Double: fck = 20#
Dim fy As Double: fy = 415#
muLim = M06_Flexure.Calculate_Mu_Lim(b, d, fck, fy)  ' Now safe
```

**Additional fixes needed:**
- **CRITICAL:** Do NOT use `Debug.Print` immediately after function call. Copy to intermediate variable first:
  ```vb
  muLim = Calculate_Mu_Lim(b, d, fck, fy)
  Dim muLimD As Double: muLimD = muLim  ' Safe copy
  Debug.Print muLimD  ' Now safe to print
  ```
- Split inline assignments: `okLower = (muLimD > 120#)` on its own line
- Store intermediate calculations: `Mu_over = 1.2 * muLim` before passing to function
- Split comparisons from variable declarations: `Dim okLower As Boolean` then `okLower = (value > threshold)`

**Why this matters:** On Mac VBA, string concatenation in `Debug.Print` with a function return value can trigger overflow during the implicit type conversion for the print operation, even though the value itself is valid.

---
*Issue documented: December 2025. Library modules hardened with CDbl() wrappers. Test files use explicit variable storage to avoid Mac VBA function call overflow.*

**Symptom:** `RunAllTests` fails at `Test_Flexure_CalcOnly [Bounds_Lower]` even though `Calculate_Mu_Lim(230,450,20,415)` returns `128.513...` (Double). The overflow triggers when evaluating `muLim > 120#`.

**What’s been done:**
- All `Integer` variables replaced with `Long` in modules.
- All dimension products wrapped with `CDbl(...)` in M03–M07.
- Duplicate `GetVersion` removed; fresh import macro removes old modules before re-adding.
- Tests instrumented with step tags and `TypeName(muLim)` logging.

**Repro steps:**
1. Use the bulk importer to remove/import M02–M10 and `Test_Structural.bas`.
2. `Debug > Compile`.
3. Run `RunAllTests` and observe overflow at `Flexure_CalcOnly [Bounds_Lower]`.

**Next diagnostic to try in Excel (not committed):**
Add a temporary probe inside `M06_Flexure.Calculate_Mu_Lim` before the return:
```vb
Debug.Print "[MuLimProbe] xu_max_d=" & xu_max_d & " k=" & k & _
            " term=" & k * CDbl(fck) * CDbl(b) * CDbl(d) * CDbl(d)
```
Then re-run `RunAllTests`. If this overflows, refactor the multiplication to scale down earlier (e.g., compute `k * fck` first, then multiply by `b`, then by `d`, then by `d`, each wrapped in `CDbl`), or break into smaller steps with `CDbl` at each multiplication.

### Alternative Test Patterns (Experimental)

To combat the persistent Mac VBA stack/overflow issues, we found that **removing intermediate `Debug.Print` statements** and using **Variant return types** solved the issue.

**The Winning Pattern:**
1.  Assign function return to a `Variant` first.
2.  Cast to `Double` explicitly using `CDbl()`.
3.  Perform all logic/comparisons.
4.  **Only then** use `Debug.Print` to show results.

**Why this works:**
On Mac VBA, `Debug.Print` statements interleaved with floating-point logic seem to corrupt the stack or the floating-point state, causing subsequent valid comparisons to trigger Overflow (Error 6). By deferring printing until after logic is complete, we avoid this interaction.

**Suspected cause:** Stale compiled code or a hidden implicit conversion on Mac VBA despite Double declarations. Ensure no duplicate/old modules remain loaded, and that the workbook code matches the repo (Long-safe, CDbl-wrapped math).

## Mac VBA Debugging Log (Dec 2025)

### Problem
Persistent `Runtime Error 6: Overflow` in `Test_Structural.bas` on Mac Excel, even after fixing logical integer overflows in the library.

### Attempts & Findings

1.  **Attempt:** Wrap library calculations in `CDbl()`.
    *   **Result:** Fixed the core library logic, but tests still failed.
2.  **Attempt:** Use explicit `Double` variables for inputs in tests.
    *   **Result:** Helped, but `Calculate_Mu_Lim` still overflowed on assignment.
3.  **Attempt:** "Immediate Capture" of UDT members.
    *   **Result:** Fixed UDT access crashes, but scalar function returns still crashed.
4.  **Attempt:** Experimental Test Variations (Phase 1):
    *   `Test_Flexure_Alt_NoPrint`: **PASSED** (Deferred printing).
    *   `Test_Flexure_Alt_DirectInIf`: **PASSED** (No variable assignment).
    *   `Test_Flexure_Alt_Explicit`: **PASSED** (Explicit casting).
    *   Standard Test: **FAILED** (Interleaved printing).
5.  **Attempt:** Experimental Test Variations (Phase 2 - Brute Force):
    *   `Test_Exp_InlineAssert`: **PASSED** (Inline check & print).
    *   `Test_Exp_PureDouble`: **PASSED** (No Variant needed if printing deferred).
    *   `Test_Exp_ByRefHelper`: **PASSED**.
    *   `Test_Exp_SplitComp`: **PASSED**.
    *   Standard Test (Refactored to defer printing): **FAILED** at `AssertTrue`.

### The Real Culprit: Passing Expressions to Subs
We discovered that passing a **floating-point comparison expression** directly to a `ByVal Boolean` argument of a subroutine causes stack corruption on Mac VBA.

**Fails:**
```vb
AssertTrue (astOverD = -1#), "TestName"
```

**Passes:**
```vb
Dim isMatch As Boolean
isMatch = (astOverD = -1#)
AssertTrue isMatch, "TestName"
```

### Final Solution Applied
Refactored `Test_Structural.bas` to:
1.  Capture function returns into `Variant` variables first (safest).
2.  Cast to `Double` explicitly.
3.  **Assign all assertion conditions to local Boolean variables.**
4.  Pass these variables to `AssertTrue`.
5.  Print debug logs only at the very end.

## Retrospective & Best Practices (Mac VBA)

### What We Missed
1.  **Implicit Type Conversion Risks:** We assumed `AssertTrue(x > y)` was safe. On Mac VBA, passing an expression `x > y` (which evaluates to a temporary boolean) to a `ByVal` argument seems to trigger stack issues when `x` or `y` are Doubles involved in recent calculations.
2.  **`Debug.Print` Side Effects:** We treated `Debug.Print` as a harmless side-effect. On Mac VBA, it interacts with the floating-point stack/state and can cause corruption if interleaved with logic.
3.  **Platform Differences:** We assumed Windows VBA behavior == Mac VBA behavior. This was false.

### Debug Process Improvements
1.  **Isolation:** We initially tried to fix the *library* code (CDbl wrappers) when the crash was in the *test harness*. We should have isolated the crash location earlier (e.g., by stepping through or using more granular prints).
2.  **Assumption Checking:** We assumed "Overflow" meant "Integer Overflow". In this case, it was a "Stack/Memory Overflow" or corruption masquerading as Error 6.

### Recommended Coding Practices for Mac VBA
1.  **The "Safe Assertion" Pattern:** Always calculate boolean conditions into a local variable before passing to an assertion helper.
    ```vb
    Dim isSafe As Boolean: isSafe = (val > 0)
    AssertTrue isSafe, "TestName"
    ```
2.  **Deferred Printing:** Do not interleave `Debug.Print` with calculation logic. Collect results and print them at the end of the subroutine.
3.  **Explicit Casting:** Use `CDbl()` liberally when dealing with `Variant` returns or mixed-type arithmetic.
4.  **Avoid Inline Expressions:** Break complex expressions into intermediate variables. It makes debugging easier and avoids compiler/runtime bugs.

### Nested UDT Return Stack Corruption
On Mac Excel, returning a UDT from a function that is called by another function which also returns a UDT can cause stack corruption or `Runtime Error 6: Overflow`.

**Scenario:**
`Function A` returns `MyUDT`.
`Function B` calls `Function A` and returns `MyUDT`.
`Test Sub` calls `Function B`.

**Workaround:**
Avoid nested UDT returns where possible. Inline the logic of the inner function into the outer function, or use `ByRef` parameters instead of function return values for UDTs in deep call stacks.

### Summary of Mac VBA Pitfalls

| Pitfall | Symptom | Workaround |
| :--- | :--- | :--- |
| **Integer Overflow** | `Error 6` on `b * d` | Wrap all dimensions in `CDbl()` inside library functions. |
| **Inline Expressions** | `Error 6` or Crash on `AssertTrue(x > y)` | Calculate boolean to local var: `b = (x > y): AssertTrue b`. |
| **Interleaved Printing** | `Error 6` after `Debug.Print` | Defer all printing to the end of the subroutine. |
| **Nested UDT Returns** | `Error 6` on function return | Inline inner function logic or use `ByRef` parameters. |
| **UDT Member Access** | `Error 6` on `Print res.Val` | Capture to local var first: `v = res.Val: Print v`. |
