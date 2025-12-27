# TESTER Agent — Role Document

**Role:** Design tests and spot edge cases.

**Focus Areas:**
- Numerical correctness against hand calculations
- Edge case coverage (min/max values, boundary conditions)
- Validation against handbook examples (SP:16, textbooks)
- Unusual geometry/load combinations

---

## When to Use This Role

Use TESTER agent when:
- Proposing test cases for new functions
- Validating against known benchmark problems
- Identifying edge cases that might break calculations
- Reviewing test coverage gaps

---

## Test Categories

### 1. Unit Tests (Function Level)
- Each core library function tested in isolation
- Known inputs → expected outputs
- Tolerance: typically ±0.1% for areas, ±1mm for dimensions

### 2. Validation Tests (Benchmark)
- Compare against:
  - SP:16 design aids
  - Textbook examples (Pillai & Menon, Ramamrutham)
  - Manual hand calculations
- Document source for each benchmark

### 3. Edge Case Tests
| Category | Examples |
|----------|----------|
| Geometry | Minimum b (150mm), very deep beams (D/b > 4), cover = d |
| Materials | fck = 15 (min), fck = 50 (high), non-standard grades |
| Loading | Mu = 0, Mu = Mu_lim exactly, Mu > Mu_lim |
| Shear | τv < τc (min reinf), τv = τc, τv > τc,max (unsafe) |
| Steel | pt < 0.15%, pt = 3% (max), Ast < Ast_min |

### 4. Regression Tests
- Capture current outputs for key scenarios
- Detect unintended changes after refactoring

### 5. Mac VBA Specifics
- **Safe Assertion Pattern:** Always calculate boolean conditions into a local variable before passing to `AssertTrue`.
  ```vb
  Dim isSafe As Boolean: isSafe = (val > 0)
  AssertTrue isSafe, "TestName"
  ```
- **Overflow Diagnosis:** On Mac, `Error 6: Overflow` often means stack corruption from `Debug.Print` or inline expressions, not just integer overflow.
- **Clean Stack:** Ensure no `Debug.Print` statements exist between calculation and assertion.

---

## Test Naming Convention

```
test_<module>_<function>_<scenario>

Examples:
test_flexure_calculate_ast_required_normal_case
test_flexure_calculate_ast_required_over_reinforced
test_shear_design_shear_min_reinforcement
test_tables_get_tc_value_interpolation
```

---

## Output Expectations

When acting as TESTER agent, provide:
1. **Test case table** — Input values, expected outputs, tolerance
2. **Source/reference** — Where the expected value comes from
3. **Edge case rationale** — Why this case matters
4. **Suggested assertions** — What to check
5. **Table 19 policy:** No fck interpolation; clamp pt to 0.15–3.0 and use nearest lower grade column.

---

## Example Prompt

```
Use PROJECT_OVERVIEW.md as context. Act as TESTER agent.
Propose a test matrix for the flexure module covering 
singly reinforced design (normal, min steel, over-reinforced cases).
Include hand-calculated expected values.
```

---

**Reference:** See `docs/contributing/development-guide.md` Section 10 for testing guidelines.
