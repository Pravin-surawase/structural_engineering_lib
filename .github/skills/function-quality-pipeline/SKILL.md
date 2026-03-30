# Function Quality Pipeline

**Purpose:** Mandatory quality workflow for adding any new IS 456 function to structural_engineering_lib. Ensures accuracy, traceability, and professional-grade output.

**When to use:** Every time a new function is added to `codes/is456/`, `services/api.py`, or a new structural element module.

**Philosophy:** Develop slowly but with 100% accuracy. Every function must be verifiable against IS 456 text, SP:16 design aids, or standard textbooks.

---

## The 9-Step Pipeline (MANDATORY — no step skipped)

### Step 1: PLAN — Clause Research & Formula Identification

Before writing ANY code, document:

```bash
# Check if function already exists
grep -ri "<function_name>" Python/structural_lib/ --include="*.py"
.venv/bin/python scripts/discover_api_signatures.py <function_name>
```

**Required documentation before coding:**
- [ ] IS 456 clause number(s) with exact text quoted
- [ ] Mathematical formula in symbolic form
- [ ] Input parameters with units (mm, N/mm², kN, kNm)
- [ ] Output type (frozen dataclass with `is_safe()`, `to_dict()`, `summary()`)
- [ ] Edge cases identified (zero inputs, max values, boundary conditions)
- [ ] Benchmark source identified (SP:16 chart/table number, textbook page)

**Agent:** @orchestrator plans, @structural-engineer researches clauses

---

### Step 2: MATH REVIEW — Formula Verification

Before implementation, verify the formula independently:

- [ ] Formula matches IS 456 clause text EXACTLY
- [ ] Units are dimensionally consistent (dimensional analysis)
- [ ] Boundary conditions produce expected results (Mu=0 → Ast=min, Mu=Mu_lim → balanced)
- [ ] Formula agrees with at least 2 benchmark sources
- [ ] Degenerate cases identified: What happens with zero/extreme inputs?
- [ ] Monotonicity check: increasing fck → capacity increases (never decreases)

**Agent:** @structural-engineer verifies, @library-expert cross-checks

---

### Step 3: IMPLEMENT — Write Pure Function

Follow the 12-point quality checklist:

```
✅ 1. @clause("XX.X") decorator present with correct IS 456 clause
✅ 2. Frozen dataclass return type with is_safe(), to_dict(), summary()
✅ 3. Docstring: IS 456 clause, formula, args, returns, raises, references
✅ 4. Every formula preceded by # IS 456 Cl XX.X: [symbolic form] comment
✅ 5. No float == comparisons — use abs(a-b) < TOLERANCE
✅ 6. Division uses safe_divide() from core/numerics.py
✅ 7. Output checked for NaN/Inf before return
✅ 8. Intermediate variables used (not one-line complex expressions)
✅ 9. Units explicit in parameter names (_mm, _kNm, _kN)
✅ 10. No I/O, no file reads, no env vars, no network calls
✅ 11. validate_*() called before calculation
✅ 12. Errors accumulated as tuple[DesignError, ...], not raised individually
```

**Numerical stability rules:**
- NEVER `if result == 0.0:` → use `if abs(result) < EPSILON:`
- NEVER divide without checking denominator → use `safe_divide()`
- NEVER extrapolate beyond IS 456 table bounds → clamp to bounds
- NEVER accept γc or γs as function parameters → hardcoded constants only
- ALWAYS check: `if math.isnan(result) or math.isinf(result): raise CalculationError`

**IS 456 formula annotation (mandatory):**
```python
# IS 456 Cl 38.1: xu_max/d from Table 21.1 (based on fy)
xu_max_d = materials.get_xu_max_d(fy)

# IS 456 Cl 38.1: Mu_lim = 0.36 × (xu_max/d) × [1 - 0.42 × (xu_max/d)] × b × d² × fck
k = 0.36 * xu_max_d * (1 - 0.42 * xu_max_d)
mu_lim_nmm = k * fck * b * d * d
```

**Agent:** @structural-math writes the function

---

### Step 4: TEST — Write Comprehensive Tests

**Minimum test requirements per function:**

| Test Type | Minimum Count | Tolerance | Source |
|-----------|---------------|-----------|--------|
| Unit tests (normal cases) | 3 | exact | Hand calculation |
| Boundary/edge cases | 3 | exact | IS 456 limits |
| Degenerate cases | 2 | exact | Zero/extreme inputs |
| SP:16 benchmark | 2 | ±0.1% | SP:16 chart values |
| Textbook benchmark | 1 | ±1% | Pillai & Menon / Ramamrutham |
| Property-based (Hypothesis) | 2 | — | Monotonicity, equilibrium |

**Degenerate case tests (MANDATORY):**
- What happens with `Mu_kNm=0`?
- What happens with `Vu_kN=0`?
- What happens with minimum reinforcement?
- What happens at balanced section exactly?
- What happens with maximum allowed steel ratio?

**Monotonicity tests (MANDATORY):**
- Increasing fck → capacity must increase (or stay same)
- Increasing fy → steel area must decrease (or stay same)
- Increasing Mu → required Ast must increase
- Increasing b → required Ast must decrease (wider section)

**Golden test rule:** Once a SP:16 benchmark test passes, it becomes a golden test.
Golden tests can NEVER be deleted or have their expected values changed (only tolerance can be loosened with justification).

```bash
# Run tests
.venv/bin/pytest Python/tests/unit/test_<module>.py -v
.venv/bin/pytest Python/tests/ -v -k "<function_name>"
```

**Agent:** @tester writes tests, @structural-engineer provides benchmark values

---

### Step 5: REVIEW — Architecture & Math Verification

**Two-pass review:**

**Pass 1 — Math Correctness (@structural-engineer):**
- [ ] Formula matches IS 456 clause text
- [ ] Benchmark values match within tolerance
- [ ] Edge cases produce correct results
- [ ] Safety factors are hardcoded (γc=1.5, γs=1.15)
- [ ] Units are consistent throughout
- [ ] Degenerate cases handled correctly

**Pass 2 — Code Quality (@reviewer):**
- [ ] 12-point function quality checklist passes
- [ ] Architecture boundaries respected (no upward imports)
- [ ] No code duplication (check existing functions first)
- [ ] Tests exist and pass
- [ ] No security issues (no stack trace leaks, input validation)
- [ ] Result type is frozen dataclass with required methods

```bash
# Architecture check
.venv/bin/python scripts/check_architecture_boundaries.py
.venv/bin/python scripts/validate_imports.py --scope structural_lib

# Full test suite
.venv/bin/pytest Python/tests/ -v
```

**Agent:** @structural-engineer (math), @reviewer (code)

---

### Step 6: API WIRE — Connect to Service Layer

- [ ] Add function to `services/api.py` (follow existing pattern)
- [ ] Re-export from `__init__.py`
- [ ] Unit plausibility guards at API boundary
- [ ] Update `api_manifest.json`

```bash
# Verify API surface
.venv/bin/python scripts/discover_api_signatures.py <function_name>
.venv/bin/python scripts/check_api_compat.py
```

**Agent:** @backend wires service layer

---

### Step 7: ENDPOINT — FastAPI Router (if applicable)

- [ ] Create/extend router in `fastapi_app/routers/`
- [ ] Pydantic request/response models in `fastapi_app/models/`
- [ ] API test in `fastapi_app/tests/`
- [ ] Verify at `/docs` (OpenAPI)

```bash
# Check existing routes first
grep -r "@router" fastapi_app/routers/ | head -30

# Test endpoint
.venv/bin/pytest fastapi_app/tests/ -v -k "<endpoint>"
```

**Agent:** @api-developer creates endpoint

---

### Step 8: DOCUMENT — Update Documentation

- [ ] Function docstring complete (clause, formula, args, returns, raises)
- [ ] API reference updated (`docs/reference/api.md`)
- [ ] Clause coverage updated in `clauses.json`
- [ ] WORKLOG.md entry added
- [ ] Example script in `Python/examples/`
- [ ] CHANGELOG.md entry (for release notes)

**Agent:** @doc-master updates docs

---

### Step 9: COMMIT — Safe Commit via PR

```bash
# Preview changes
./scripts/ai_commit.sh "feat(is456): add <function_name> per Cl XX.X" --preview

# Check if PR required
./run.sh pr status

# Commit
./scripts/ai_commit.sh "feat(is456): add <function_name> per Cl XX.X"
```

**Agent:** @ops commits safely

---

## Pipeline Status Tracking Template

Use this checklist for every new function:

```markdown
### Function: `<function_name>` — IS 456 Cl XX.X

| Step | Status | Agent | Notes |
|------|--------|-------|-------|
| 1. PLAN | ⬜ | orchestrator | |
| 2. MATH REVIEW | ⬜ | structural-engineer | |
| 3. IMPLEMENT | ⬜ | structural-math | |
| 4. TEST | ⬜ | tester | |
| 5. REVIEW (math) | ⬜ | structural-engineer | |
| 5. REVIEW (code) | ⬜ | reviewer | |
| 6. API WIRE | ⬜ | backend | |
| 7. ENDPOINT | ⬜ | api-developer | |
| 8. DOCUMENT | ⬜ | doc-master | |
| 9. COMMIT | ⬜ | ops | |
```

---

## Incremental Complexity Rule

When implementing a new structural element (e.g., column), follow this order:

1. **Simplest case first** — e.g., short column, pure axial load
2. **Verify against SP:16** — must pass benchmark before proceeding
3. **Add next level** — e.g., short column with uniaxial bending
4. **Verify again** — new benchmarks, regression tests still pass
5. **Add next level** — biaxial bending
6. **Verify again** — all previous tests still pass
7. **Continue** — slender column, effective length, helical reinforcement

**NEVER jump to the complex case.** Each level builds on the verified foundation below it.

---

## Red Flags — Stop and Investigate

If ANY of these occur during implementation, STOP and review:

| Red Flag | Action |
|----------|--------|
| Utilization > 0.95 on benchmark case | Verify formula — may be off by factor |
| Negative reinforcement area | Calculation error — never valid |
| Result doesn't match SP:16 within tolerance | DO NOT proceed — fix first |
| Division by zero in edge case | Add guard, document which input causes it |
| Test passes but value is "close enough" | Tighten tolerance or investigate source difference |
| Monotonicity violated | Fundamental error — escalate to @library-expert |
| Safety factor appears as parameter | FORBIDDEN — hardcoded only |

---

## Quick Reference Commands

```bash
# Before starting
grep -ri "<function>" Python/structural_lib/ --include="*.py"
.venv/bin/python scripts/discover_api_signatures.py <func>

# During implementation
.venv/bin/pytest Python/tests/ -v -k "<test_name>"
.venv/bin/python scripts/check_architecture_boundaries.py
.venv/bin/python scripts/validate_imports.py --scope structural_lib

# After implementation
.venv/bin/pytest Python/tests/ -v
./run.sh check --quick
./scripts/ai_commit.sh "feat(is456): add <func> per Cl XX.X" --preview
```
