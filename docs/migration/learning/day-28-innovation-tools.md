# Day 28: Innovation & Development Infrastructure

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** High
**Created:** 2026-04-09
**Last Updated:** 2026-04-09
**Prerequisites:** Day 12 (Testing), Day 24 (AI Agents), Day 25 (Code Quality)
**Library files:** `docs/migration/12-innovation-ideas.md`

---

## What You'll Learn Today

Six innovation tools that turn a "good enough" library into a professional-grade one:
- Symbolic math (SymPy) to catch formula bugs that 5,000 tests miss
- Metamorphic testing — test WITHOUT knowing the expected answer
- Formula provenance — trace every result to an IS 456 clause
- Auto-generated API docs (griffe), property-based testing (Hypothesis), API breakage detection
- Which tools to install (buy) vs. build yourself

---

## 📖 Theory

### Why "Good Enough" Isn't Good Enough

Our library has 564 functions and 5,000+ tests. But consider: a formula bug hides if your test only checks ONE input combination. Writing expected outputs for every function requires hand-calculating the answer. When someone renames a parameter, you might not notice until production breaks. Professional engineering software needs tools that catch the bugs tests miss.

### The Six Ideas at a Glance

| # | Innovation | Problem It Solves | Effort |
|---|-----------|-------------------|--------|
| 1 | Symbolic-Numerical Crosscheck | Formula errors hide in specific test values | BUILD (3 weeks) |
| 2 | Metamorphic Testing | Can't write expected output for every function | EXTEND (2 weeks) |
| 3 | Formula Provenance | No audit trail from clause → code → test | EXTEND (1 week) |
| 4 | API Docs from Code (griffe) | Docs drift from code within days | BUY (2 days) |
| 5 | Hypothesis Property Testing | Tests only check hand-picked inputs | BUY + configure |
| 6 | Semantic API Breakage Detection | String changelogs miss breaking changes | BUY (2 days) |

---

## 🏗️ Library Examples — What Already Exists

Before building new things, know what the library already has:

```
scripts/parity_dashboard.py      — tracks which IS 456 clauses have code + tests
Python/tests/                    — 5,000+ tests using pytest + Hypothesis
clause-map.json                  — 119 clauses mapped, 63 with function links
@clause decorator                — tags functions with their IS 456 clause reference
```

The innovations below build ON TOP of this, not beside it.

---

## 🎯 Idea 1: Symbolic-Numerical Crosscheck (SymPy)

### The Problem

```python
def xu_max_ratio(fy):
    return 700 / (1100 + 0.87 * fy)
```

What if you accidentally wrote `700 / (1100 + 0.87) * fy` (misplaced parenthesis)? For `fy=415`, both formulas give numbers — a rushed developer might not spot the difference.

### The Solution: Two Representations

**SymPy** is a Python library for symbolic mathematics. Instead of computing numbers, it keeps formulas as algebra:

```python
import sympy as sp

fy = sp.Symbol('fy', positive=True)
expr = 700 / (1100 + sp.Rational(87, 100) * fy)
print(expr)  # 70000/(110000 + 87*fy) — exact, no floating point
```

Maintain BOTH a symbolic version (SymPy) and the numerical version (production code). Run both with random inputs. If they disagree → bug found.

```
IS 456 Clause 38.1: xu_max/d = 700 / (1100 + 0.87 * fy)
     +----------+----------+
     |                     |
  SYMBOLIC               NUMERICAL
  (SymPy algebra)        (Python float math)
     +---> CROSSCHECK <----+
     Feed 1000 random fy values → agree within 0.0001%? → verified
```

### Runnable Example

```python
import sympy as sp

fy_sym = sp.Symbol('fy', positive=True)
xu_max_symbolic = 700 / (1100 + sp.Rational(87, 100) * fy_sym)

def xu_max_numerical(fy_val):
    return 700 / (1100 + 0.87 * fy_val)

for fy_val in [250, 415, 500, 550]:
    sym_result = float(xu_max_symbolic.subs(fy_sym, fy_val))
    num_result = xu_max_numerical(fy_val)
    diff = abs(sym_result - num_result)
    status = "✅" if diff < 1e-10 else "❌"
    print(f"fy={fy_val}: sym={sym_result:.6f}, num={num_result:.6f} {status}")

# Prove: xu_max > 0 for ALL positive fy — not just test cases
print(sp.ask(sp.Q.positive(xu_max_symbolic)))  # True
```

**Caveat:** `sp.ask()` returns `None` for complex multi-variable expressions. Fall back to numerical comparison when symbolic proof fails. Our `materials.py` also uses table lookups for standard grades alongside the formula.

**BUILD** — SymPy is `pip install sympy`, but the crosscheck engine is custom code.

---

## 🎯 Idea 2: Metamorphic Testing

### The Problem (Test Oracle Problem)

To test `calculate_ast_required(Mu, fck, fy, b, d)`, you need: "For Mu=150, fck=25, b=300, d=450, the answer should be 982.3 mm²." Computing that expected value is as hard as writing the function. For 564 functions, this is impractical.

### The Solution: Test Relationships, Not Values

Define **relationships** that must ALWAYS hold — no expected values needed:

| Relation | Plain English | Why It's True |
|----------|---------------|---------------|
| ↑ Mu → ↑ Ast | More moment → more steel needed | Steel resists moment |
| ↑ fck → ↓ Ast | Stronger concrete → less steel | Concrete carries more |
| ↑ b → ↓ Ast | Wider beam → less steel | More concrete area |
| ↑ d → ↓ Ast | Deeper beam → less steel | Larger lever arm |
| ↑ fy → ↓ Ast | Stronger steel → less area | Each bar carries more |
| Ast > 0 | Always positive | You always need SOME steel |

### Runnable Example

```python
def test_more_moment_needs_more_steel():
    from structural_lib import design_beam_is456
    base = dict(b_mm=300, d_mm=450, fck=25, fy=415)

    r_low  = design_beam_is456(Mu_knm=100, **base)
    r_high = design_beam_is456(Mu_knm=200, **base)

    assert r_high.Ast_mm2 >= r_low.Ast_mm2  # Relationship, not exact value
```

Combine with Hypothesis for thousands of random input pairs:

```python
from hypothesis import given, strategies as st

@given(
    Mu=st.floats(min_value=10, max_value=500),
    b=st.integers(min_value=200, max_value=600),
    d=st.integers(min_value=250, max_value=900),
)
def test_monotone_fck_vs_ast(Mu, b, d):
    from structural_lib import design_beam_is456
    r25 = design_beam_is456(Mu_knm=Mu, b_mm=b, d_mm=d, fck=25, fy=415)
    r40 = design_beam_is456(Mu_knm=Mu, b_mm=b, d_mm=d, fck=40, fy=415)
    assert r40.Ast_mm2 <= r25.Ast_mm2 * 1.01  # 1% tolerance for float math
```

**EXTEND** — Hypothesis already installed. Just write pytest functions with `@given` + metamorphic assertions.

---

## 🎯 Idea 3: Formula Provenance

### The Problem

A client asks: "Your software says I need 982 mm² of steel. Which code clause is that based on?" Without formal traceability, you grep through source code hoping someone left a comment.

### The Solution: Structured Traceability

Every result traces to its IS 456 clause:

```python
# result.provenance = {
#     "clauses": ["38.1", "G-1.1"],
#     "function": "flexure.calculate_mu_lim",
#     "test": "test_flexure::test_mu_lim_fe415",
#     "verified_date": "2026-04-08"
# }
```

The library already has a `@clause` decorator on 93+ functions:

```python
@clause("38.1")
def calculate_mu_lim(fck, fy, b_mm, d_mm):
    """Limiting moment of resistance (IS 456 Cl 38.1)."""
    ...
```

The full provenance chain:

```
IS 456 Clause 38.1        → clause-map.json
flexure.py:calculate_mu_lim()  → @clause("38.1") decorator
test_flexure.py::test_mu_lim_fe415  → tests this function
golden_vector_038            → {fck=25, b=300, d=450, Mu_lim=206.8 kNm}
```

**EXTEND** — Build on existing `@clause` + `_CLAUSE_REGISTRY`. Add test-level linkage. ~1 week.

---

## 🎯 Idea 4: API Documentation from Code (griffe)

**Doc drift** = someone adds a parameter but doesn't update docs. The API reference lies.

**griffe** reads Python source → extracts signatures, docstrings, types → feeds into MkDocs. Code changes, docs auto-update.

```python
import griffe

package = griffe.load("structural_lib")
api_module = package["services"]["api"]
for name, obj in api_module.members.items():
    if isinstance(obj, griffe.Function) and not name.startswith("_"):
        params = ", ".join(p.name for p in obj.parameters)
        print(f"  {name}({params})")
```

Already installed in this project. Wire into `mkdocs.yml`:

```yaml
plugins:
  - mkdocstrings:
      handlers:
        python:
          options:
            docstring_style: google
```

**BUY** — `pip install griffe mkdocstrings-python`. 2 days to wire up.

---

## 🎯 Idea 5: Hypothesis Property Testing

Hand-written tests check specific values (`fck=25, pt=0.5 → 0.49`). You're sampling a few points from a huge input space. **Hypothesis** generates random valid inputs automatically:

```python
from hypothesis import given, strategies as st

@given(
    fck=st.sampled_from([20, 25, 30, 35, 40, 45, 50]),
    pt=st.floats(min_value=0.15, max_value=3.0),
)
def test_tau_c_always_positive(fck, pt):
    result = calculate_tau_c(fck=fck, pt=pt)
    assert result > 0
```

Runs ~100 random combos. If it finds a failure, it **shrinks** to the simplest failing case. Common finds: boundary division-by-zero, extreme ratios, floating point edge cases.

Key strategies for structural engineering:

```python
fck_strategy   = st.sampled_from([20, 25, 30, 35, 40, 45, 50])
fy_strategy    = st.sampled_from([250, 415, 500, 550])
width_strategy = st.integers(min_value=200, max_value=600)
depth_strategy = st.integers(min_value=250, max_value=900)
```

**BUY** — `pip install hypothesis` (already installed). You write strategies + invariants.

---

## 🎯 Idea 6: Semantic API Breakage Detection

A developer renames `b_mm` to `width_mm`. The changelog says "refactored parameters." Downstream code breaks. **griffe** compares AST before/after:

```
Before: def design_beam(b_mm: float, d_mm: float) -> BeamResult
After:  def design_beam(width_mm: float, d_mm: float) -> BeamResult
                        ^^^^^^^^^ BREAKING: parameter renamed
```

It catches: removed/renamed parameters, changed return types, removed functions, changed defaults.

```bash
# Run in CI on every PR
griffe check structural_lib --search-paths Python/ --against git:main
```

**BUY** — griffe already installed. Wire into CI in 2 days.

---

## 🔧 Exercise

### Exercise 1: Write a Metamorphic Relation

Write 3 metamorphic tests for `calculate_mu_lim(fck, fy, b_mm, d_mm)`:

```python
def test_wider_beam_higher_capacity():
    from structural_lib.codes.is456.flexure import calculate_mu_lim
    base = calculate_mu_lim(fck=25, fy=415, b_mm=300, d_mm=450)
    wider = calculate_mu_lim(fck=25, fy=415, b_mm=350, d_mm=450)
    assert wider > base, "Wider beam should have higher Mu_lim"
```

### Exercise 2: Trace a Provenance Chain

Pick any function in `codes/is456/`. Write its full chain:
```
Clause: ___ | Function: ___ | Test file: ___ | Test name: ___
```

### Exercise 3: Run griffe

```bash
.venv/bin/python -c "
import griffe
pkg = griffe.load('structural_lib', search_paths=['Python/'])
api = pkg['services']['api']
count = sum(1 for m in api.members.values() if isinstance(m, griffe.Function))
print(f'Found {count} functions in services/api.py')
"
```

---

## 💬 Can You Explain?

1. **Why does symbolic crosschecking catch bugs that numerical tests miss?**
   Numerical tests check specific values. Symbolic crosschecking compares FORMULA STRUCTURE — a misplaced parenthesis won't simplify to the same form, even if specific numbers happen to be close.

2. **What is the "test oracle problem"?**
   "I need the correct answer to write a test, but computing the correct answer is as hard as writing the function." Metamorphic testing sidesteps this by testing RELATIONSHIPS instead of exact values.

3. **Why might `sp.ask(sp.Q.positive(expr))` return `None`?**
   SymPy can't prove it for complex multi-variable expressions. It's not false — just unproven. Fall back to numerical comparison with random inputs.

4. **What's the difference between Hypothesis and metamorphic testing?**
   Hypothesis generates random inputs but still needs an assertion. Metamorphic testing provides the assertion strategy (test relationships, not values). They combine: Hypothesis picks inputs, metamorphic relations provide assertions.

5. **What does "BUY vs BUILD" mean?**
   "Buy" = install a package (`pip install griffe`). "Build" = write custom code. Prefer buying when mature tools exist.

---

## 📎 References

### Library Files
- [docs/migration/12-innovation-ideas.md](../12-innovation-ideas.md) — Full research with 10 ideas, 3-agent review
- `scripts/parity_dashboard.py` — Clause coverage tracking

### External Tools
- [SymPy](https://docs.sympy.org/) — Symbolic math | [Hypothesis](https://hypothesis.readthedocs.io/) — Property testing
- [griffe](https://mkdocstrings.github.io/griffe/) — API extraction + breakage detection | [mutmut](https://mutmut.readthedocs.io/) — Mutation testing

### Build vs Buy Summary

| Tool | Verdict | Install | What You Write |
|------|---------|---------|----------------|
| SymPy | BUY library, BUILD engine | `pip install sympy` | Symbolic formula representations |
| Hypothesis | BUY | `pip install hypothesis` | Strategies + invariants |
| griffe | BUY | `pip install griffe` | CI config |
| mutmut | BUY | `pip install mutmut` | Nothing — auto-mutates code |
| Metamorphic relations | BUILD | — | Domain input/output relationships |
| Provenance | EXTEND | — | Extend existing `@clause` decorator |

### Implementation Phases

| Phase | Duration | What to Build |
|-------|----------|---------------|
| Phase 1 | Weeks 1-4 | griffe CI, provenance extension, metamorphic framework |
| Phase 2 | Weeks 5-10 | Symbolic crosscheck (10 critical formulas) |
| Phase 3 | Weeks 11-16 | Golden vector factory, attestation MVP |
| Phase 4 | Weeks 17-35 | Amendment propagation, agent conflict resolution |

**Start with Phase 1** — highest value for lowest effort.

---

*Next module: [Day 29](day-29-release-workflow.md) — Release Workflow & CI/CD*