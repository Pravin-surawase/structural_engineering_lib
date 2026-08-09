# 12 — Ten Development Infrastructure Innovations

**Type:** Research
**Version:** 2.1
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-04-08
**Last Updated:** 2026-04-09
**Author:** innovator agent (deep web research session)

---

> **These are innovations in HOW WE BUILD the library, not what the library does.**
> Focus: development tools, testing innovations, AI agent workflows, maintenance automation.
> Version 1.0 was about library features — this version replaces it entirely.

## Research Sources

| Area | Source | Key Insight |
|------|--------|-------------|
| A. Aerospace safety | DO-178C + DO-333 formal methods supplement | Requirements-to-code traceability matrix; formal verification at highest criticality levels |
| B. Metamorphic testing | T.Y. Chen (2018), 750+ papers | Test without knowing exact expected output — define relations between inputs/outputs instead |
| C. Symbolic verification | SymPy assumptions system | Prove `0 < ρ < ρ_max` symbolically across all input ranges, not just test cases |
| D. Supply chain security | SLSA v1.0 framework (Build L0-L3) | Provenance attestation: unforgeable proof of build origin and process |
| E. Reproducible builds | reproducible-builds.org | Bit-for-bit identical output from same source — verify builds independently |
| F. Mutation testing | mutmut 3.x | Inject faults into code; if tests still pass, tests are weak |
| G. Agent coordination | GitHub agentic-development (65 repos) | Multi-agent conflict detection, semantic merge, concurrent editing protocols |
| H. Formula documentation | Jupyter Book / MyST / literate programming | Executable documentation where formulas and code are the same artifact |
| I. API compatibility | semantic versioning + AST diffing | Detect breaking changes by comparing abstract syntax trees, not string diffs |
| J. IS 456 amendment tracking | BIS notification system, SP:16 errata | Code amendments propagate to dozens of functions — need automated tracking |

## Comparison Matrix

> **Revised timeline:** ~30-35 weeks total (originally estimated ~20 weeks; difficulty upgrades after 3-agent review)

| # | Innovation | Development Problem | Difficulty | Impact | Phase |
|---|-----------|-------------------|:----------:|:------:|:-----:|
| 1 | Symbolic-Numerical Crosscheck Engine | Formula errors survive 5000+ tests | M-H | Critical | 2 |
| 2 | Metamorphic Test Amplifier | Writing test oracles for 564 functions is infeasible | M | High | 1 |
| 3 | Formula Provenance Chain | No traceability from IS 456 clause to code to test | L-M | Critical | 1 |
| 4 | Agent Conflict Resolution Protocol | 16 agents editing same files create merge conflicts | XL | High | 4 |
| 5 | Living Formula Documentation | Docs drift from code within 2 sessions | L | High | 1 |
| 6 | Semantic API Breakage Detector | String-based changelog misses breaking changes | L | Critical | 1 |
| 7 | Self-Healing CI Pipeline | CI failures block all agents for hours | M | High | 2 |
| 8 | Golden Vector Factory | Hand-crafting golden test vectors takes days per clause | M | High | 3 |
| 9 | Code Amendment Propagation Engine | IS 456 amendments affect dozens of functions silently | XL | Critical | 4 |
| 10 | Reproducible Calculation Attestation | No proof that a design result came from verified code | M-H | Critical | 3 |

---

## 3-Agent Review Summary

### Reviewers

- **@reviewer:** Quality 8/10, Feasibility 6/10, Novelty 5/10. Verdict: NEEDS CHANGES
- **@structural-engineer:** Formula verification, 3/6 metamorphic relations incorrect, Amendment 4 factual error
- **@library-expert:** Architecture placement review, 4 wrong placements, build vs buy analysis

### Consensus Ranking (by effort-to-value ratio)

| Rank | # | Innovation | Effort | Value | Verdict |
|------|---|-----------|--------|-------|--------|
| 1 | 6 | API Breakage Detector | 2 days (wire existing griffe) | Critical | BUY — griffe already installed |
| 2 | 5 | Living Formula Docs | 3 days | High | BUILD (small) |
| 3 | 3 | Provenance (as extension) | 1 week (extend traceability.py) | Critical | EXTEND existing @clause system |
| 4 | 2 | Metamorphic Tests | 1 week (as Hypothesis tests) | High | EXTEND — no framework needed |
| 5 | 1 | Symbolic Crosscheck | 3 weeks | Critical | BUILD — genuinely novel |
| 6 | 7 | CI Diagnostician | 2 weeks | High | BUILD incrementally |
| 7 | 8 | Golden Vector Factory | 2 weeks | High | BUILD |
| 8 | 10 | Attestation MVP | 1 week | Medium | BUILD MVP only |
| 9 | 9 | Amendment Propagation | 4 weeks | Critical (long-term) | BUILD later (depends on #3) |
| 10 | 4 | Agent Conflict | Not recommended as described | Low | DEPRIORITIZE — existing hooks solve most of it |

### Unanimous Conclusions

- Ideas 1, 5, 9 are genuinely valuable and novel
- Ideas 3, 4, 8, 10 have significant overlap with existing infrastructure that was NOT acknowledged
- The proposed `verification/` folder violates architecture — distribute code to proper locations
- SymPy MUST be dev-only dependency, never in structural_lib proper
- Total timeline should be ~35 weeks, not ~20 weeks
- 5 of 10 difficulty ratings are underestimated
- 6 code bugs found in implementation sketches

### Critical Architecture Warning

Do NOT create `Python/structural_lib/verification/` as proposed. Correct placement:
- Test infrastructure (symbolic, metamorphic) → `Python/tests/`
- Development tooling (provenance, amendments) → `scripts/`
- Runtime feature (attestation) → `Python/structural_lib/services/attestation.py`

---

## Idea 1: Symbolic-Numerical Crosscheck Engine

### Development Problem

We have 564 functions and 5,143 tests. Yet formula errors can hide for months. Why? Because numerical tests only check specific input values. A test that checks `Mu_lim` for `fck=25, fy=415, b=300, d=450` tells you nothing about whether the formula is correct for `fck=30, fy=500, b=250, d=500`. A wrong exponent, a swapped variable, a missing factor — if the specific test value happens to be close enough, the test passes.

In aerospace (DO-178C Level A), this is solved with formal verification: prove the formula is correct for ALL inputs, not just test cases. We can bring this to structural engineering Python.

### Innovation

Build a crosscheck engine that maintains TWO independent representations of every critical formula:
1. **Numerical** (current Python code) — fast, used in production
2. **Symbolic** (SymPy expression) — slow, used for verification

At test time, the engine:
- Evaluates both representations for random inputs (Hypothesis-powered)
- Checks that they agree within floating-point tolerance
- Proves algebraic properties symbolically (e.g., `Mu_lim > 0` for all valid inputs)
- Detects when a code change breaks the symbolic equivalence

### Why This Does Not Exist

No structural engineering library has symbolic verification. SymPy exists, Hypothesis exists, but nobody combines them with domain-specific structural formulas. The closest analog is NASA's PVS theorem prover for flight software — but that is not Python and not for civil engineering.

### How It Works

```
IS 456 Clause 38.1 (Mu_lim formula)
         |
    +---------+---------+
    |                   |
  symbolic.py        numerical.py
  (SymPy expr)       (Python code)
    |                   |
    +----> crosscheck <----+
              |
    random inputs (Hypothesis)
              |
    agree within 1e-10?
    +-- YES -> formula verified for N random inputs
    +-- NO  -> ALERT: formula mismatch at input X
              |
    symbolic properties (SymPy.ask)
              |
    Mu_lim > 0 for fck>0, fy>0, b>0, d>0?
    +-- PROVEN -> property holds for ALL inputs
    +-- UNPROVEN -> needs investigation
```

### Implementation Sketch

```python
# scripts/symbolic_crosscheck.py
import sympy as sp
from hypothesis import given, strategies as st

# Symbolic representation of Mu_lim (IS 456 Cl 38.1)
def mu_lim_symbolic(fck, fy, b, d):
    xu_max_ratio = sp.Rational(700, 1100 + sp.Rational(87, 100) * fy)
    return (sp.Rational(36, 100) * fck * b * xu_max_ratio
            * (1 - sp.Rational(42, 100) * xu_max_ratio) * d**2)

# Numerical representation (from production code)
def mu_lim_numerical(fck, fy, b, d):
    xu_max_ratio = 700 / (1100 + 0.87 * fy)
    return 0.36 * fck * b * xu_max_ratio * (1 - 0.42 * xu_max_ratio) * d**2

@given(
    fck=st.sampled_from([20, 25, 30, 35, 40]),
    fy=st.sampled_from([250, 415, 500]),
    b=st.integers(min_value=150, max_value=600),
    d=st.integers(min_value=200, max_value=900),
)
def test_symbolic_numerical_agree(fck, fy, b, d):
    sym_val = float(mu_lim_symbolic(fck, fy, b, d))
    num_val = mu_lim_numerical(fck, fy, b, d)
    assert abs(sym_val - num_val) / max(abs(sym_val), 1) < 1e-10

# Symbolic property: Mu_lim > 0 for all positive inputs
fck_s, fy_s, b_s, d_s = sp.symbols("fck fy b d", positive=True)
mu_expr = mu_lim_symbolic(fck_s, fy_s, b_s, d_s)
assert sp.ask(sp.Q.positive(mu_expr))  # PROVEN for all positive inputs
```

> **⚠️ Review Finding:** The example uses the pure formula `700/(1100+0.87*fy)`, but the actual codebase (materials.py) uses a **hybrid approach**: table lookup for standard grades (Fe250→0.53, Fe415→0.48, Fe500→0.46) and the formula as fallback. For Fe415: formula gives 0.4791, table gives 0.48 (0.19% diff). The symbolic crosscheck must account for this hybrid. Additionally, `sp.ask(sp.Q.positive(mu_expr))` returns `None` (unprovable) for most multivariate IS 456 expressions — fall back to numerical bounds checking. Coverage metric: proven / tested / unproven. Symbolic verification works for ~40% of formulas (closed-form); the remaining ~60% (table-based, iterative, piecewise) degrade to numerical-only comparison.

### Architecture

```
scripts/symbolic_crosscheck.py              <- runner script
Python/tests/verification_helpers/          <- NEW folder (NOT in structural_lib)
    symbolic_registry.py                    <- maps clause -> (symbolic, numerical) pair
    crosscheck_engine.py                    <- evaluator + property prover
    properties.py                           <- domain properties (Mu>0, rho in range)
scripts/run_symbolic_crosscheck.py          <- CI integration script
Python/tests/test_symbolic_crosscheck/      <- Hypothesis-powered tests
```

### AI Agent Integration

- **@tester** registers symbolic representations when adding new formula tests
- **@structural-math** provides symbolic version alongside numerical implementation
- **@reviewer** runs crosscheck as part of code review for any formula change
- CI runs `pytest tests/test_symbolic_crosscheck/ -v` on every PR touching `codes/is456/`

### Difficulty and Impact

- **Difficulty:** M-H (SymPy `ask()` returns `None` for most multivariate expressions; table-formula hybrid complicates)
- **Impact:** Critical — catches formula errors that 5,000+ numerical tests miss
- **Dependencies:** sympy (dev-only, NEVER in structural_lib proper), hypothesis (already used)
- **Time estimate:** 3 weeks for 10 critical formulas, ongoing for coverage

### Example Scenario

A developer changes the `xu_max` calculation from `700 / (1100 + 0.87 * fy)` to `700 / (1100 + 0.87) * fy` (parenthesis error). All 69 golden vector tests pass because they test with `fy=415` where the numerical difference is small. The symbolic crosscheck catches it instantly because the SymPy expression does not simplify to the same form.

---

## Idea 2: Metamorphic Test Amplifier

### Development Problem

We have 564 functions. Writing a correct expected-output test for each requires hand-calculating the answer (or trusting SP:16 tables, which themselves have known errata). This is the **test oracle problem**: for many functions, computing the expected output is as hard as writing the function itself. Result: tests cover happy paths but miss edge cases.

### Innovation

Metamorphic testing does not need expected outputs. Instead, it defines **relations** between inputs and outputs:

- **Scaling:** Double the load -> moment should double (linear regime)
- **Monotonicity:** Increase concrete grade -> capacity should increase
- **Symmetry:** Swap top/bottom reinforcement -> shear capacity unchanged
- **Invariance:** Change units (mm to m) -> same result after unit conversion
- **Bounding:** Result must be between analytical lower and upper bounds

For 564 functions, we can define ~20 universal metamorphic relations that apply to HUNDREDS of functions automatically.

### Why This Does Not Exist

Metamorphic testing has 750+ academic papers but almost zero adoption in Python testing frameworks. No structural engineering tool uses it. The closest is Hypothesis, which generates random inputs — but Hypothesis still needs an oracle (assertion). Metamorphic testing needs NO oracle, just relations.

### How It Works

```
Function: calculate_shear_capacity(b, d, fck, Ast, Vu)
                    |
    Metamorphic Relations:
    +-- MR1: increase b by 50% -> capacity increases
    +-- MR2: increase fck from 25 to 30 -> capacity increases
    +-- MR3: set Ast=0 -> capacity = concrete contribution only
    +-- MR4: double b AND halve d -> capacity changes predictably
    +-- MR5: capacity >= tau_c_min * b * d (lower bound)
                    |
    For each MR, generate 1000 random input pairs (Hypothesis)
                    |
    Any violation? -> BUG FOUND (no expected output needed)
```

### Implementation Sketch

```python
# Python/tests/metamorphic/metamorphic.py
from dataclasses import dataclass
from typing import Callable
from hypothesis import given, strategies as st

@dataclass
class MetamorphicRelation:
    name: str
    transform_input: Callable  # how to modify input
    check_output: Callable     # relation between original and transformed output

# Universal relations for structural functions
MONOTONE_CAPACITY_VS_FCK = MetamorphicRelation(
    name="capacity increases with fck",
    transform_input=lambda kwargs: {**kwargs, "fck": kwargs["fck"] + 5},
    check_output=lambda orig, transformed: transformed >= orig * 0.99,
)

MONOTONE_CAPACITY_VS_WIDTH = MetamorphicRelation(
    name="capacity increases with width",
    transform_input=lambda kwargs: {**kwargs, "b_mm": kwargs["b_mm"] + 50},
    check_output=lambda orig, transformed: transformed >= orig * 0.99,
)

POSITIVE_CAPACITY = MetamorphicRelation(
    name="capacity is always positive for valid inputs",
    transform_input=lambda kwargs: kwargs,  # identity
    check_output=lambda orig, _: orig > 0,
)

def run_metamorphic_suite(func, relations, input_strategy, n=1000):
    """Run all metamorphic relations against a function."""
    violations = []
    for rel in relations:
        for _ in range(n):
            inputs = input_strategy.example()
            orig_output = func(**inputs)
            transformed_inputs = rel.transform_input(inputs)
            transformed_output = func(**transformed_inputs)
            if not rel.check_output(orig_output, transformed_output):
                violations.append((rel.name, inputs, orig_output,
                                   transformed_output))
    return violations
```

> **⚠️ Review Finding:** `input_strategy.example()` is NOT valid Hypothesis API for production tests (it's debug-only). Use `@given` decorator or `@composite` with `draw()`. Three of the proposed relations have issues: (1) "Swap reinforcement → shear unchanged" is **wrong** — IS 456 Table 19 τ_c depends on tension steel percentage p_t; swapping tension/compression steel changes p_t. (2) "Double load → double moment" is structural analysis, not IS 456 design — design functions take Mu as INPUT. Correct relation: ↑Mu → ↑Ast required. (3) ↑fck → ↑capacity is NOT guaranteed for biaxial columns (Cl 39.6 exponent α_n). Each metamorphic relation must be domain-validated per function.

### Architecture

```
Python/tests/metamorphic/                  <- NOT in structural_lib
    metamorphic.py                         <- relation definitions + runner
    relations_is456.py                     <- IS 456-specific relations (20+)
Python/tests/test_metamorphic/
    test_beam_metamorphic.py               <- beam functions
    test_shear_metamorphic.py              <- shear functions
    test_column_metamorphic.py             <- column functions
scripts/run_metamorphic.py                 <- CLI: amplify tests for a module
```

### AI Agent Integration

- **@tester** defines metamorphic relations for new functions (required in quality pipeline)
- **@structural-engineer** validates that relations are physically correct
- **@reviewer** checks that new functions have at least 3 metamorphic relations
- CI runs metamorphic suite nightly (too slow for every PR)

### Difficulty and Impact

- **Difficulty:** M (novel concept but straightforward implementation)
- **Impact:** High — finds bugs that conventional tests miss, especially in edge cases
- **Dependencies:** hypothesis (already used)
- **Time estimate:** 2 weeks for framework + 20 universal relations

### Example Scenario

A developer adds a new column interaction curve function. Writing expected outputs requires solving complex nonlinear equations. Instead, the metamorphic amplifier applies: (1) increasing axial load reduces moment capacity, (2) increasing section size increases capacity, (3) swapping X/Y dimensions mirrors the curve. These catch a sign error in the biaxial term that would have required months of manual verification to find.

---

## Idea 3: Formula Provenance Chain (DO-178C for Python)

### Development Problem

When a bug is found in a design result, the debugging question is: "Which IS 456 clause does this formula implement? Who wrote it? What test verifies it? When was it last changed?" Currently this requires reading git blame, grepping for comments, and hoping someone left a docstring. There is no formal traceability from IS 456 clause -> Python function -> test case -> golden vector.

In aerospace (DO-178C), every line of flight-critical code has a traceable link back to a requirement. Our library is also safety-critical — buildings collapse when formulas are wrong. We need the same discipline.

### Innovation

Build a provenance chain that links every formula to its source:

```
IS 456 Clause 38.1 -> flexure.py:calculate_mu_lim() -> test_flexure.py::test_mu_lim_fe415 -> golden_vector_038
```

This is stored as structured metadata (JSON), not comments. It can be queried: "Show me all functions implementing Clause 40.4" or "Which tests cover the shear provisions?"

> **Note:** Most functions implement a COMBINATION of clauses (e.g., beam design = Cl 38.1 + Annex G-1.1 + Table J). The provenance schema must support `clauses: list[str]`.

### Why This Does Not Exist

DO-178C tools (LDRA, VectorCAST) cost $50k+ and target C/Ada. No open-source Python tool provides requirements-to-code traceability. The `parity_dashboard.py` script tracks clause coverage but has no function-level or test-level linkage.

### Existing Foundation

This idea builds on significant existing infrastructure:
- **`@clause` decorator** — already used on 93+ functions to tag IS 456 clause references
- **`_CLAUSE_REGISTRY`** — runtime registry mapping functions to clauses
- **`clause-map.json`** — 119 clauses mapped, 63 with function linkage
- **`parity_dashboard.py`** — tracks clause coverage at function level
- **`check_clause_coverage.py`** — checks gaps in clause coverage
- **`generate_traceability_report()`** — produces existing traceability reports

**What's genuinely new:** test-level linkage (which test covers which clause), golden vector tracing, and stale verification detection. This should EXTEND the existing `@clause` + `_CLAUSE_REGISTRY` system, not replace it.

### How It Works

```
IS 456:2000 Clause Registry (YAML)
    |
    v
provenance_registry.json
    clause_38_1:
        functions: [flexure.calculate_mu_lim, flexure.xu_max_ratio]
        tests: [test_flexure::test_mu_lim_*, test_golden::gv_038_*]
        golden_vectors: [gv_038_m20_fe415, gv_038_m25_fe500]
        last_verified: 2026-04-08
        sp16_reference: "Table E, p.98"
    |
    v
scripts/check_provenance.py
    - Every function tagged with a clause? (no orphans)
    - Every clause has at least one test? (no untested clauses)
    - Every golden vector traced to a clause? (no disconnected vectors)
    - Any function changed since last verification? (stale verification)
```

### Implementation Sketch

```python
# scripts/provenance/provenance.py
from dataclasses import dataclass, field
import json
from pathlib import Path

@dataclass
class ClauseProvenance:
    clause_id: str              # "38.1"
    clause_title: str           # "Limiting moment of resistance"
    functions: list[str]        # ["codes.is456.flexure.calculate_mu_lim"]
    tests: list[str]            # ["test_flexure::test_mu_lim_fe415"]
    golden_vectors: list[str]   # ["gv_038_m20_fe415"]
    sp16_reference: str = ""    # "Table E, p.98"
    last_verified: str = ""     # ISO date
    notes: str = ""

class ProvenanceRegistry:
    def __init__(self, path: Path):
        self.path = path
        self.clauses: dict[str, ClauseProvenance] = {}
        if path.exists():
            data = json.loads(path.read_text())
            for k, v in data.items():
                self.clauses[k] = ClauseProvenance(**v)

    def orphan_functions(self, all_functions: list[str]) -> list[str]:
        """Functions not traced to any clause."""
        traced = set()
        for cp in self.clauses.values():
            traced.update(cp.functions)
        return [f for f in all_functions if f not in traced]

    def untested_clauses(self) -> list[str]:
        """Clauses with no test coverage."""
        return [cid for cid, cp in self.clauses.items()
                if not cp.tests]

    def stale_verifications(self, changed_files: list[str]) -> list[str]:
        """Clauses whose functions were modified since last verification."""
        stale = []
        for cid, cp in self.clauses.items():
            for func in cp.functions:
                module = func.rsplit(".", 1)[0].replace(".", "/") + ".py"
                if module in changed_files:
                    stale.append(cid)
        return stale
```

### Architecture

```
scripts/provenance/                         <- development tooling (NOT in structural_lib)
    provenance.py                           <- registry loader + checker
scripts/check_provenance.py                 <- CI checker: no orphans, no gaps
scripts/update_provenance.py                <- auto-discover new functions/tests
provenance_registry.json                    <- clause-to-function-to-test mappings (project root)
```

### AI Agent Integration

- **@structural-math** updates provenance when adding new IS 456 functions
- **@tester** links tests to clauses when creating test cases
- **@reviewer** runs `check_provenance.py` during code review
- **@governance** monitors provenance coverage as a project health metric
- CI blocks merge if provenance coverage drops below threshold

### Difficulty and Impact

- **Difficulty:** L-M (metadata management is simple, but backfilling ~100 existing functions is real work)
- **Impact:** Critical — enables DO-178C-grade traceability for safety-critical code
- **Dependencies:** none (pure Python + JSON)
- **Time estimate:** 1 week for framework, 2 weeks to backfill existing functions

### Example Scenario

A user reports that shear capacity seems too high for a specific case. The provenance chain instantly shows: Clause 40.4 is implemented by `shear.py:tau_c()`, tested by `test_shear::test_tau_c_table19`, verified against golden vector `gv_040_m25`. The developer checks the golden vector, finds it matches SP:16 Table 19, and the issue turns out to be the user's input, not the formula. Total debug time: 5 minutes instead of 2 hours.

---

## Idea 4: Agent Conflict Resolution Protocol

### Development Problem

We have 16 AI agents that can edit files concurrently. When @backend modifies `api.py` while @api-developer modifies a router that imports from `api.py`, merge conflicts arise. Worse: when @structural-math changes a formula and @tester simultaneously updates tests for the old formula, the tests break silently.

Current mitigation: human orchestration. This does not scale. We had 10+ hours of rework from merge conflicts in v0.21.x.

### Innovation

Build a conflict detection and resolution protocol that operates BEFORE agents start editing:

1. **Intent Declaration:** Before editing, each agent declares: "I intend to modify X, Y, Z"
2. **Conflict Detection:** A coordinator checks if any declared intents overlap
3. **Resolution:** If conflict, one of: (a) serialize (agent B waits), (b) partition (agent A edits lines 1-50, agent B edits lines 51-100), (c) merge protocol (both edit, automated 3-way merge)
4. **Post-Edit Verification:** After both agents finish, verify no semantic conflicts

### Existing Foundation

Significant conflict prevention already exists:
- **`ai_commit.sh`** — prevents manual git operations that cause conflicts
- **PR enforcement** — all production changes require PRs
- **`scripts/hooks/pre_commit.py`, `pre_route.py`** — pre-commit validation hooks
- **`agent_registry.json`** — tracks agent capabilities and file scopes
- **Orchestrator pipeline** — serializes agent work through mandatory steps

The "10+ hours of rework" problem was largely solved by these existing tools. The REMAINING gap is semantic dependency detection (two agents editing different files that import from each other).

### Why This Does Not Exist

Git handles text-level merges. But semantic merges (two agents changed different functions that call each other) are unsolved in general. For our specific domain — 16 agents with known roles editing a known codebase — we can build targeted conflict resolution.

The GitHub "agentic-development" topic (65 repos) shows increasing interest in multi-agent coordination, but no production-ready conflict resolution protocol exists.

### How It Works

```
@backend declares: "editing services/api.py, adding new function"
@api-developer declares: "editing routers/design.py, adding new endpoint"
                    |
         Conflict Detector
                    |
    Overlap in api.py? NO (different files)
    Semantic dependency? YES (router imports from api.py)
                    |
         Resolution: SERIALIZE
    @backend edits first -> @api-developer edits second
    (api-developer sees the new function and can import it)
```

### Implementation Sketch

```python
# scripts/agent_conflict_detector.py
from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class EditIntent:
    agent: str
    files: list[str]            # files to modify
    functions: list[str]        # functions to add/modify
    imports_from: list[str]     # modules this change depends on
    timestamp: str

class ConflictDetector:
    def __init__(self, intents_dir: Path):
        self.intents_dir = intents_dir
        self.intents_dir.mkdir(exist_ok=True)

    def declare_intent(self, intent: EditIntent):
        path = self.intents_dir / f"{intent.agent}.json"
        path.write_text(json.dumps(intent.__dict__, indent=2))

    def check_conflicts(self) -> list[dict]:
        intents = []
        for p in self.intents_dir.glob("*.json"):
            intents.append(EditIntent(**json.loads(p.read_text())))

        conflicts = []
        for i, a in enumerate(intents):
            for b in intents[i+1:]:
                # File-level conflict
                shared_files = set(a.files) & set(b.files)
                if shared_files:
                    conflicts.append({
                        "type": "file_overlap",
                        "agents": [a.agent, b.agent],
                        "files": list(shared_files),
                        "resolution": "serialize",
                    })
                # Semantic dependency conflict
                a_modules = {f.rsplit("/", 1)[0] for f in a.files}
                if set(b.imports_from) & a_modules:
                    conflicts.append({
                        "type": "semantic_dependency",
                        "agents": [a.agent, b.agent],
                        "detail": f"{b.agent} imports from modules {a.agent} is editing",
                        "resolution": "serialize_a_first",
                    })
        return conflicts

    def clear_intent(self, agent: str):
        path = self.intents_dir / f"{agent}.json"
        if path.exists():
            path.unlink()
```

### Architecture

```
scripts/agent_conflict_detector.py      <- conflict detection engine
logs/agent_intents/                     <- intent declarations (JSON)
    backend.json
    api-developer.json
    ...
scripts/hooks/pre_edit_hook.py          <- called before agent edits
    -> declares intent, checks conflicts, blocks or proceeds
```

### AI Agent Integration

- **All agents** declare edit intents before starting work
- **@orchestrator** uses conflict detection to sequence agent work
- **@ops** monitors conflict logs and adjusts scheduling
- Pre-edit hook blocks conflicting edits with clear message: "Wait for @backend to finish editing api.py"

### Difficulty and Impact

- **Difficulty:** XL (distributed coordination via JSON files is fundamentally fragile; needs file locking when agents run in parallel VS Code windows or CI)
- **Impact:** High — eliminates the 10+ hours of merge-conflict rework
- **Dependencies:** none (JSON files + Python)
- **Time estimate:** 3 weeks for protocol + hooks, 2 weeks for testing

> **⚠️ Review Warning:** The JSON-file-based protocol breaks when agents run in parallel VS Code windows or CI, where file locking is needed. This is fundamentally a distributed coordination problem.

### Example Scenario

@structural-math is adding a new column formula to `codes/is456/column.py`. @tester declares intent to add tests for column functions. The conflict detector sees the semantic dependency and tells @tester: "Wait — @structural-math is modifying column.py. Start after their commit." @tester works on beam tests instead. When @structural-math commits, @tester gets notified and writes tests against the new API. Zero merge conflicts.

---

## Idea 5: Living Formula Documentation

### Development Problem

Documentation drifts from code within 2 sessions. A developer changes `xu_max_ratio = 700 / (1100 + 0.87 * fy)` to handle a new steel grade, but the docs still show the old formula. The API reference says `fck` is in MPa but the code was changed to accept both MPa and N/mm^2. We have 870+ internal links — manual doc updates are unsustainable.

### Innovation

Make formulas executable documentation. Instead of writing the formula in docs AND in code, write it ONCE as a literate programming artifact that is both:
1. **Rendered as documentation** (LaTeX math in MkDocs)
2. **Executed as code** (importable Python)

When the code changes, the documentation changes automatically because they are THE SAME ARTIFACT.

### Why This Does Not Exist

Jupyter notebooks exist but are terrible for library development (merge conflicts, no static analysis, not importable). MyST-NB can execute notebooks in docs. But nobody has built a system where the same function definition serves as both production code and rendered documentation with LaTeX formulas.

### How It Works

```
Python/structural_lib/codes/is456/flexure.py
    |
    Contains: docstring with MyST math syntax
    |
    def calculate_mu_lim(fck, fy, b_mm, d_mm):
        '''Calculate limiting moment of resistance.

        $$M_{u,lim} = 0.36 f_{ck} b x_{u,max}(1 - 0.42 x_{u,max}/d) d$$

        where $x_{u,max}/d$ = 700 / (1100 + 0.87 f_y)

        IS 456 Clause 38.1, SP:16 Table E
        '''
        xu_max_ratio = 700 / (1100 + 0.87 * fy)
        return 0.36 * fck * b_mm * xu_max_ratio * (1 - 0.42 * xu_max_ratio) * d_mm**2
    |
    v
scripts/extract_formula_docs.py
    -> Parses docstrings with MyST math
    -> Generates docs/reference/formulas/flexure.md
    -> Includes: LaTeX formula, parameter table, clause reference
    -> Auto-generated — never hand-edited
    |
    v
docs/reference/formulas/flexure.md (auto-generated)
    Shows: rendered LaTeX, parameter types, units, source clause
    Links back to: source code line, test file, golden vectors
```

### Implementation Sketch

```python
# scripts/extract_formula_docs.py
import ast
import inspect
import re
from pathlib import Path

def extract_formulas(module_path: Path) -> list[dict]:
    """Extract formula documentation from Python source."""
    source = module_path.read_text()
    tree = ast.parse(source)
    formulas = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            docstring = ast.get_docstring(node)
            if docstring and "$$" in docstring:
                # Extract LaTeX blocks
                math_blocks = re.findall(r'\$\$(.*?)\$\$', docstring, re.DOTALL)
                # Extract clause references
                clauses = re.findall(r'IS 456 Clause ([\d.]+)', docstring)
                # Extract parameters from type hints
                params = []
                for arg in node.args.args:
                    if arg.arg != 'self':
                        params.append(arg.arg)

                formulas.append({
                    "function": node.name,
                    "file": str(module_path),
                    "line": node.lineno,
                    "math": math_blocks,
                    "clauses": clauses,
                    "params": params,
                    "docstring": docstring,
                })
    return formulas

def generate_formula_page(formulas: list[dict], output: Path):
    """Generate a MkDocs-compatible formula reference page."""
    lines = ["# Formula Reference (Auto-Generated)\n",
             "> Do not edit — regenerate with `scripts/extract_formula_docs.py`\n"]
    for f in formulas:
        lines.append(f"## `{f['function']}()`\n")
        lines.append(f"**Source:** `{f['file']}` line {f['line']}\n")
        if f['clauses']:
            lines.append(f"**IS 456 Clauses:** {', '.join(f['clauses'])}\n")
        for math in f['math']:
            lines.append(f"\n$$\n{math.strip()}\n$$\n")
        lines.append(f"**Parameters:** `{'`, `'.join(f['params'])}`\n")
        lines.append("---\n")
    output.write_text("\n".join(lines))
```

### Architecture

```
scripts/extract_formula_docs.py         <- parser + generator
docs/reference/formulas/                <- auto-generated formula pages
    flexure.md
    shear.md
    column.md
    ...
mkdocs.yml                             <- includes formula pages
CI: regenerate + diff on every PR       <- catches drift
```

### AI Agent Integration

- **@structural-math** writes formulas with MyST math in docstrings (single source of truth)
- **@doc-master** runs formula extraction as part of doc generation
- **@reviewer** checks that new formulas include LaTeX in docstrings
- CI regenerates formula docs and fails if output differs from committed docs (drift detection)

### Difficulty and Impact

- **Difficulty:** L (AST docstring extraction is well-understood; weekend project)
- **Impact:** High — eliminates formula drift, the #1 documentation problem
- **Dependencies:** none (standard library ast + re)
- **Time estimate:** 1 week for extractor, 2 weeks to add LaTeX to all docstrings

### Example Scenario

@structural-math updates the shear capacity formula in `shear.py` to handle high-strength concrete (IS 456 Amendment 4). The docstring includes the new LaTeX formula. On the next CI run, `extract_formula_docs.py` regenerates `docs/reference/formulas/shear.md`. The PR diff shows both the code change AND the doc change. The reviewer can verify both are correct in one review. Zero drift.

---

## Idea 6: Semantic API Breakage Detector

### Development Problem

We have 37 public API functions with 104 exports in `__all__`. When a developer renames a parameter from `Ast_mm2` to `ast_mm2`, or changes a return type from `float` to `dict`, the changelog says "refactored shear module" but does not mention the breaking change. Downstream users discover it at runtime. `discover_api_signatures.py` shows current signatures but cannot detect CHANGES.

### Innovation

Build an AST-based API comparator that:
1. Snapshots the entire public API surface (function signatures, parameter names, types, return types, defaults)
2. On every PR, diffs the snapshot against the baseline
3. Classifies changes as: SAFE (new function), MINOR (new optional parameter), BREAKING (removed parameter, changed type, renamed)
4. Blocks merge for unacknowledged BREAKING changes

This is semantic versioning, automatically enforced.

### Why This Does Not Exist

Tools like `griffe` (Python API diff) exist and `griffe` is already installed in this project (griffelib==2.0.2 in requirements-lock.txt). It does AST-based Python API diffing. The gap is not the tool but the **CI integration**: wiring griffe into the PR workflow for `structural_lib`'s Python API (not just the REST/OpenAPI layer). No structural engineering library has this wired into CI.

### Existing Foundation

Partial solutions already exist:
- **`openapi_baseline.json`** — detects FastAPI endpoint changes
- **`discover_api_signatures.py`** — introspects current Python API signatures
- **`test_api_surface_snapshot.py`** — snapshot regression on export counts
- **`griffe` (griffelib==2.0.2)** — already in requirements-lock.txt, does AST-based Python API diffing

**What's genuinely new:** wiring griffe into CI for the Python `structural_lib` API (not just REST). This is a **configuration task** (~50 lines of glue script), not a new tool.

### How It Works

```
Git baseline (main branch)          PR branch
    |                                   |
    v                                   v
api_snapshot_main.json              api_snapshot_pr.json
    |                                   |
    +---------> AST Differ <-----------+
                    |
    Changes detected:
    +-- SAFE: new function design_column_biaxial()
    +-- MINOR: new optional param 'verbose' in design_beam_is456()
    +-- BREAKING: param 'Ast_mm2' renamed to 'ast_mm2' in tau_c()
    +-- BREAKING: return type changed float -> dict in calculate_mu()
                    |
    BREAKING changes found -> require explicit acknowledgment:
    # api-breakage: tau_c param rename Ast_mm2->ast_mm2 (deprecation added)
    # api-breakage: calculate_mu returns dict (migration guide in CHANGELOG)
```

### Implementation Sketch

```python
# scripts/api_breakage_detector.py
import ast
import json
from pathlib import Path
from dataclasses import dataclass

@dataclass
class FunctionSignature:
    name: str
    module: str
    params: list[dict]          # [{name, type, default, required}]
    return_type: str
    is_public: bool

def snapshot_api(source_dir: Path) -> dict[str, FunctionSignature]:
    """Snapshot all public function signatures via AST."""
    signatures = {}
    for py_file in source_dir.rglob("*.py"):
        tree = ast.parse(py_file.read_text())
        module = str(py_file.relative_to(source_dir)).replace("/", ".").removesuffix(".py")
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                params = []
                for arg in node.args.args:
                    if arg.arg == "self":
                        continue
                    params.append({
                        "name": arg.arg,
                        "type": ast.unparse(arg.annotation) if arg.annotation else "Any",
                    })
                sig = FunctionSignature(
                    name=node.name, module=module,
                    params=params,
                    return_type=ast.unparse(node.returns) if node.returns else "Any",
                    is_public=not node.name.startswith("_"),
                )
                signatures[f"{module}.{node.name}"] = sig
    return signatures

def diff_api(baseline: dict, current: dict) -> list[dict]:
    """Detect breaking changes between two API snapshots."""
    changes = []
    for key in baseline:
        if key not in current:
            changes.append({"type": "BREAKING", "detail": f"removed: {key}"})
        else:
            old, new = baseline[key], current[key]
            old_params = {p["name"] for p in old.params}
            new_params = {p["name"] for p in new.params}
            removed = old_params - new_params
            if removed:
                changes.append({"type": "BREAKING",
                    "detail": f"{key}: removed params {removed}"})
            if old.return_type != new.return_type:
                changes.append({"type": "BREAKING",
                    "detail": f"{key}: return type {old.return_type} -> {new.return_type}"})
    for key in current:
        if key not in baseline:
            changes.append({"type": "SAFE", "detail": f"added: {key}"})
    return changes
```

### Architecture

```
scripts/api_breakage_detector.py        <- AST differ
fastapi_app/openapi_baseline.json       <- existing OpenAPI baseline (extend to Python API)
Python/structural_lib/api_baseline.json <- NEW: Python API signature snapshot
CI: run on every PR, block if unacknowledged BREAKING changes
```

### AI Agent Integration

- **@api-developer** runs breakage detector before modifying public APIs
- **@reviewer** checks that BREAKING changes have migration guides
- **@ops** updates baseline snapshot after each release
- CI auto-comments on PRs with API change summary

### Difficulty and Impact

- **Difficulty:** L (griffe already installed and does most of this; just wire into CI)
- **Impact:** Critical — prevents silent breaking changes that cause downstream failures
- **Dependencies:** griffe (already in requirements-lock.txt)
- **Time estimate:** 2 days for CI integration + domain-specific rules

### Example Scenario

@backend renames `Ast_mm2` to `ast_provided_mm2` in the shear calculation (for clarity). The API breakage detector catches this as BREAKING, blocks the PR, and shows: "Parameter renamed in `tau_c()`: `Ast_mm2` -> `ast_provided_mm2`. Add deprecation alias or acknowledge breakage." The developer adds `Ast_mm2` as a deprecated alias, and the PR passes.

---

## Idea 7: Self-Healing CI Pipeline

### Development Problem

CI failures block all 16 agents for hours. Common failures:
- Flaky tests (timing-dependent, order-dependent)
- Dependency resolution failures (pip version conflicts)
- Linting false positives after ruff/basedpyright updates
- Docker build failures (base image changes)

An agent cannot tell whether a CI failure is caused by their change or by a pre-existing issue. They waste hours debugging failures they did not cause.

### Innovation

Build a CI diagnostician that:
1. **Classifies failures** as: (a) caused by PR, (b) pre-existing (flaky), (c) infrastructure
2. **Auto-remediates** known failure patterns (retry flaky, pin dependency, skip broken lint rule)
3. **Learns from history:** tracks which tests are flaky, which dependencies conflict
4. **Reports actionable fixes** to agents: "This failure is caused by X. Fix: change Y on line Z."

### Why This Does Not Exist

CI/CD tools (GitHub Actions, CircleCI) retry on failure but cannot diagnose root causes. Flaky test detectors exist (pytest-repeat, flaky) but do not integrate with multi-agent workflows. No tool maps CI failures to specific agent actions.

### How It Works

```
CI Run Failed
    |
    v
Self-Healing Diagnostician
    |
    +-- Step 1: Classify failure
    |   +-- Test failure? -> Check if test was flaky in last 10 runs
    |   +-- Import error? -> Check if dependency changed
    |   +-- Lint failure? -> Check if rule was added in ruff update
    |   +-- Build failure? -> Check Docker base image changes
    |
    +-- Step 2: Check causality
    |   +-- Did this PR touch the failing file? -> PR-caused
    |   +-- Did this test fail on main too? -> Pre-existing
    |   +-- Is this a known flaky test? -> Infrastructure
    |
    +-- Step 3: Auto-remediate or report
        +-- Flaky: retry (max 2x), mark as flaky in registry
        +-- Dependency: pin to last working version, alert @ops
        +-- Lint: suppress new rule for this PR, create follow-up issue
        +-- PR-caused: report exact failure + suggested fix to agent
```

### Implementation Sketch

```python
# scripts/ci_diagnostician.py
import json
import subprocess
from pathlib import Path
from dataclasses import dataclass

@dataclass
class CIFailure:
    test_name: str
    error_type: str             # "assertion", "import", "timeout", "lint"
    error_message: str
    file_path: str
    line_number: int

class CIDiagnostician:
    def __init__(self, history_path: Path):
        self.history = json.loads(history_path.read_text()) if history_path.exists() else {}

    def classify(self, failure: CIFailure, pr_files: list[str]) -> dict:
        """Classify CI failure and suggest remediation."""
        # Check if test is known flaky
        flaky_count = self.history.get(failure.test_name, {}).get("flaky_count", 0)
        if flaky_count >= 3:
            return {"classification": "flaky", "action": "retry",
                    "confidence": 0.9}

        # Check if PR touched the failing file
        if failure.file_path in pr_files:
            return {"classification": "pr_caused", "action": "fix_required",
                    "detail": f"Your PR modified {failure.file_path}",
                    "confidence": 0.95}

        # Check if test fails on main branch too
        main_result = self._check_main_branch(failure.test_name)
        if main_result == "fail":
            return {"classification": "pre_existing",
                    "action": "not_your_fault",
                    "confidence": 0.85}

        return {"classification": "unknown", "action": "investigate",
                "confidence": 0.5}

    def _check_main_branch(self, test_name: str) -> str:
        """Check if test passes on main branch."""
        result = subprocess.run(
            [".venv/bin/pytest", "-x", "-k", test_name, "--tb=no"],
            capture_output=True, timeout=60
        )
        return "pass" if result.returncode == 0 else "fail"

    def update_history(self, failure: CIFailure, was_flaky: bool):
        if failure.test_name not in self.history:
            self.history[failure.test_name] = {"flaky_count": 0, "total": 0}
        self.history[failure.test_name]["total"] += 1
        if was_flaky:
            self.history[failure.test_name]["flaky_count"] += 1
```

### Architecture

```
scripts/ci_diagnostician.py             <- failure classifier + remediator
logs/ci_history.json                    <- historical failure patterns
scripts/hooks/post_ci_hook.py           <- runs after CI, updates history
.github/workflows/ci.yml               <- integrates diagnostician
```

### AI Agent Integration

- **@ops** maintains the CI diagnostician and flaky test registry
- **All agents** receive classified failure reports instead of raw CI output
- **@tester** is notified when a test becomes flaky (3+ intermittent failures)
- PR comments include: "CI Diagnosis: test_shear_M25 is FLAKY (failed 4/10 recent runs). Retrying..."

### Difficulty and Impact

- **Difficulty:** M (parsing diverse test output formats; `_check_main_branch` subprocess is infeasible in CI)
- **Impact:** High — eliminates hours of agent time debugging failures they did not cause
- **Dependencies:** none (Python standard library + subprocess)
- **Time estimate:** 2 weeks for classifier, ongoing for pattern expansion

> **⚠️ Review Finding:** `_check_main_branch` running full pytest in CI is an anti-pattern (doubles CI time, requires checkout). Replace with historical test result database.

### Example Scenario

@frontend submits a PR that only touches React files. CI fails because `test_column_biaxial` has a timing-dependent assertion (it rounds differently on GitHub's Ubuntu vs local macOS). The diagnostician classifies this as "flaky — not PR-caused" with 90% confidence, retries the test (passes), and marks it in the flaky registry. @frontend's PR proceeds without delay. @tester gets a notification to fix the timing sensitivity.

---

## Idea 8: Golden Vector Factory

### Development Problem

We have 69 golden test vectors — hand-calculated design results verified against SP:16 tables. Adding a new golden vector takes DAYS: open SP:16, find the right table, extract values, verify units, create the test fixture, cross-check. For new IS 456 clauses being implemented, this bottleneck delays testing by weeks.

### Innovation

Build a factory that semi-automatically generates golden vectors by:
1. **SP:16 Table Parser:** OCR/parse SP:16 tables into structured data
2. **Cross-Calculator:** Run the same inputs through 2+ independent methods
3. **Uncertainty Quantification:** Flag vectors where methods disagree beyond tolerance
4. **Registry:** Store vectors with provenance (source, method, uncertainty)

The factory does NOT eliminate human review — it ACCELERATES it. Every generated vector requires engineer sign-off.

### Why This Does Not Exist

SP:16 is a physical book (published 1980). No machine-readable version exists. Golden vectors in structural engineering are always hand-crafted. The concept of automated golden vector generation with cross-validation does not exist in any structural tool.

### Existing Foundation

Golden vector infrastructure already exists:
- **69 golden vectors** as hand-crafted fixtures
- **TASK-722** completed: `conftest.py` golden_vectors fixture with SP:16 values
- **`test_golden_vectors_column.py`** and **`test_vba_parity.py`** — existing golden vector tests

**What's genuinely new:** the automated FACTORY (cross-validation, parameter sampling, provenance metadata). This amplifies existing infrastructure, not replaces it.

### How It Works

```
Input: IS 456 Clause 38.1, parameter ranges
    |
    v
Golden Vector Factory
    |
    +-- Step 1: Generate parameter combinations
    |   Latin Hypercube Sampling over:
    |   fck: [20, 25, 30, 35, 40]
    |   fy: [250, 415, 500]
    |   b: [200, 250, 300, 350, 400, 450, 500]
    |   d: [250, 300, 350, 400, 450, 500, 550, 600]
    |
    +-- Step 2: Calculate using multiple methods
    |   Method A: Our library (numerical)
    |   Method B: SymPy (symbolic) [from Idea 1]
    |   Method C: SP:16 table lookup (where available)
    |
    +-- Step 3: Cross-validate
    |   All methods agree within 0.1%? -> GOLDEN (high confidence)
    |   Methods disagree? -> FLAG for human review
    |
    +-- Step 4: Generate test fixture
        pytest fixture with full provenance metadata
```

### Implementation Sketch

```python
# scripts/golden_vector_factory.py
from dataclasses import dataclass
import itertools
from pathlib import Path
import json

@dataclass
class GoldenVector:
    clause: str                 # "38.1"
    inputs: dict                # {"fck": 25, "fy": 415, "b_mm": 300, "d_mm": 450}
    expected: dict              # {"Mu_lim_kNm": 234.5}
    methods: dict               # {"numerical": 234.5, "symbolic": 234.5, "sp16": 234.3}
    tolerance: float            # 0.001 (0.1%)
    confidence: str             # "high" | "medium" | "needs_review"
    source: str                 # "SP:16 Table E" | "cross-validated"
    reviewed_by: str = ""       # engineer sign-off

class GoldenVectorFactory:
    def __init__(self):
        self.vectors: list[GoldenVector] = []

    def generate_combinations(self, param_ranges: dict) -> list[dict]:
        """Generate parameter combinations via Latin Hypercube."""
        keys = list(param_ranges.keys())
        values = list(param_ranges.values())
        combos = list(itertools.product(*values))
        # Sample subset for efficiency
        import random
        sample = random.sample(combos, min(50, len(combos)))
        return [dict(zip(keys, c)) for c in sample]

    def cross_validate(self, clause: str, inputs: dict,
                       calculators: dict) -> GoldenVector:
        """Run inputs through multiple calculators, compare results."""
        results = {}
        for name, calc_fn in calculators.items():
            results[name] = calc_fn(**inputs)

        values = list(results.values())
        max_diff = max(values) - min(values)
        mean_val = sum(values) / len(values)
        relative_diff = max_diff / mean_val if mean_val else float("inf")

        return GoldenVector(
            clause=clause,
            inputs=inputs,
            expected={"result": mean_val},
            methods=results,
            tolerance=0.001,
            confidence="high" if relative_diff < 0.001 else "needs_review",
            source="cross-validated",
        )

    def export_pytest_fixtures(self, output: Path):
        """Generate pytest fixture file from golden vectors."""
        lines = ['"""Auto-generated golden vectors. DO NOT EDIT."""',
                 "import pytest\n",
                 "GOLDEN_VECTORS = ["]
        for gv in self.vectors:
            lines.append(f"    {json.dumps(gv.__dict__)},")
        lines.append("]\n")
        lines.append('@pytest.fixture(params=GOLDEN_VECTORS, ids=lambda g: '
                     'f"{g[\\"clause\\"]}-{g[\\"confidence\\"]}")')
        lines.append("def golden_vector(request):")
        lines.append("    return request.param")
        output.write_text("\n".join(lines))
```

### Architecture

```
scripts/golden_vector_factory.py        <- factory engine
Python/tests/golden_vectors/            <- generated fixtures
    flexure_vectors.json                <- clause 38.x vectors
    shear_vectors.json                  <- clause 40.x vectors
    column_vectors.json                 <- clause 39.x vectors
    REVIEW_LOG.md                       <- engineer sign-off log
scripts/sp16_table_parser.py            <- SP:16 data extraction (future)
```

### AI Agent Integration

- **@tester** uses factory to generate vectors for new clauses
- **@structural-engineer** reviews and signs off on generated vectors
- **@structural-math** provides symbolic calculator for cross-validation
- Factory runs automatically when new IS 456 functions are added

### Difficulty and Impact

- **Difficulty:** M (cross-validation logic + fixture generation)
- **Impact:** High — reduces golden vector creation from days to hours
- **Dependencies:** none for cross-validation; OCR library for SP:16 parsing (future)
- **Time estimate:** 2 weeks for factory, ongoing for SP:16 parsing

### Example Scenario

@structural-math implements IS 456 Clause 39.3 (short column under axial load). The golden vector factory generates 50 parameter combinations, runs them through both the numerical implementation and a SymPy symbolic version, and produces 47 high-confidence vectors and 3 needing review (edge cases near slenderness limit). @structural-engineer reviews the 3 flagged vectors, confirms 2 are correct (edge case behavior is expected), and identifies 1 where the formula breaks down. That edge case gets a special test and a code fix. Time: 4 hours instead of 3 days.

---

## Idea 9: Code Amendment Propagation Engine

### Development Problem

IS 456:2000 has had 5 amendments since publication. Each amendment changes clauses that propagate to dozens of functions. Example: Amendment 4 (2013) primarily addressed durability provisions (minimum cement content, exposure conditions) — NOT stress block parameters. The stress block in Cl 38.1 has remained unchanged since IS 456:2000 publication. The primary value of amendment tracking is in durability/detailing changes (Cl 26 cover, Cl 8 exposure).

The parity dashboard tracks which clauses are implemented but not which amendment version each function reflects.

### Innovation

Build an amendment propagation engine that:
1. **Maps amendments to clauses:** "Amendment 4 modifies Clauses 38.1, 39.1, 40.2"
2. **Maps clauses to functions:** (from Idea 3 provenance chain)
3. **When an amendment is applied to one function, auto-identifies ALL other functions that need updating**
4. **Tracks amendment status per function:** "v1.0 original", "v1.0+A1", "v1.0+A4"
5. **Blocks release if functions are at inconsistent amendment levels**

### Why This Does Not Exist

No structural engineering library tracks code amendments systematically. BIS publishes amendments as one-page errata sheets. The mapping from amendment text to affected code is a manual, error-prone process. No tool automates this propagation.

### How It Works

```
IS 456 Amendment 4 (2020)
    |
    v
Amendment Registry (YAML)
    amendment_4:
        date: 2020-06-15
        clauses_modified: [38.1, 39.1, 40.2.1]
        description: "Revised stress block parameters for HSC"
        changes:
            - clause: 38.1
              detail: "xu_max/d values updated for fy > 500"
              affected_params: [xu_max_ratio]
    |
    v
Propagation Engine
    clause 38.1 -> functions: [
        flexure.calculate_mu_lim,
        flexure.xu_max_ratio,
        design.check_doubly_reinforced,
        column.interaction_curve,      <- often missed
        shear.enhanced_shear,          <- often missed
    ]
    |
    v
Amendment Status Report:
    flexure.calculate_mu_lim  -> A4 APPLIED (2026-03-15)
    flexure.xu_max_ratio      -> A4 APPLIED (2026-03-15)
    design.check_doubly       -> A4 MISSING <- UPDATE REQUIRED
    column.interaction_curve  -> A4 MISSING <- UPDATE REQUIRED
    shear.enhanced_shear      -> A4 MISSING <- UPDATE REQUIRED
```

### Implementation Sketch

```python
# scripts/amendment_propagation.py
import json
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Amendment:
    id: str                     # "A4"
    date: str                   # "2020-06-15"
    clauses: list[str]          # ["38.1", "39.1"]
    description: str

@dataclass
class FunctionAmendmentStatus:
    function: str
    current_amendment: str      # "A4" or "original"
    required_amendment: str     # "A4"
    is_current: bool

class AmendmentPropagationEngine:
    def __init__(self, amendments_path: Path, provenance_path: Path):
        self.amendments = self._load_amendments(amendments_path)
        self.provenance = json.loads(provenance_path.read_text())

    def _load_amendments(self, path: Path) -> list[Amendment]:
        data = json.loads(path.read_text())
        return [Amendment(**a) for a in data]

    def check_propagation(self) -> list[FunctionAmendmentStatus]:
        """Check which functions need amendment updates."""
        results = []
        latest_amendment = self.amendments[-1]  # most recent

        for clause_id, clause_data in self.provenance.items():
            # Is this clause affected by the latest amendment?
            if clause_id in latest_amendment.clauses:
                for func in clause_data.get("functions", []):
                    func_amendment = clause_data.get("amendment_level", "original")
                    results.append(FunctionAmendmentStatus(
                        function=func,
                        current_amendment=func_amendment,
                        required_amendment=latest_amendment.id,
                        is_current=(func_amendment == latest_amendment.id),
                    ))
        return results

    def blocking_issues(self) -> list[str]:
        """Issues that must be resolved before release."""
        statuses = self.check_propagation()
        return [
            f"{s.function}: at {s.current_amendment}, needs {s.required_amendment}"
            for s in statuses if not s.is_current
        ]
```

### Architecture

```
scripts/amendment_propagation/              <- development tooling (NOT in structural_lib)
    amendment_propagation.py                <- propagation engine
    amendments_registry.json                <- amendment -> clause mappings
scripts/check_amendments.py                 <- CLI: check amendment consistency
    -> integrates with provenance chain (Idea 3)
    -> integrates with parity dashboard
```

### AI Agent Integration

- **@structural-engineer** maintains the amendments registry when BIS publishes updates
- **@structural-math** applies amendments to functions and updates their amendment level
- **@governance** monitors amendment consistency as a project health metric
- CI blocks release if any function is behind on amendments (inconsistent state)

### Difficulty and Impact

- **Difficulty:** XL (requires comprehensive clause-to-function mapping first — depends on Idea 3)
- **Impact:** Critical — prevents shipping code with inconsistent IS 456 amendment levels
- **Dependencies:** Idea 3 (provenance chain) must be built first
- **Time estimate:** 3 weeks (after Idea 3 is complete)

### Example Scenario

BIS publishes IS 456 Amendment 5 modifying Clause 26.5.1 (cover requirements). The engine identifies 12 functions that reference cover: `min_cover()`, `effective_depth()`, `crack_width()`, `detailing_check()`, and 8 others. @structural-math updates `min_cover()` and `effective_depth()`. The engine reports: "Amendment A5: 2/12 functions updated, 10 remaining." The release is blocked until all 12 are updated. No function is accidentally left at the old cover requirements.

---

## Idea 10: Reproducible Calculation Attestation

### Development Problem

When a structural engineer uses our library to design a beam, there is no proof that:
1. The calculation was performed by a specific version of the library
2. The library code had not been tampered with
3. The input parameters were exactly what the engineer provided
4. The output has not been modified after generation

In regulated environments (nuclear, bridge design, government projects), calculations must be auditable. Currently our library produces results but no verifiable audit trail.

### Innovation

Build a calculation attestation system inspired by SLSA (Supply Chain Levels for Software Artifacts):

1. **Calculation Receipt:** Every design call produces a signed receipt containing: library version, git commit hash, input hash, output hash, timestamp
2. **Verification:** Anyone can verify a receipt against the published library to confirm the result is genuine
3. **Tamper Detection:** If someone modifies the output, the hash mismatch is detected
4. **Reproducibility:** Given the receipt, the exact calculation can be reproduced

### Existing Foundation

Partial audit infrastructure already exists:
- **`services/audit.py`** — `CalculationHash` (SHA-256) and `AuditTrail` (immutable logs)
- **TASK-735** — `CalculationProvenance` planned for v0.22.0
- **TASK-797** — SLSA build provenance planned

**What's genuinely new:** the verification CLI (anyone can independently verify a receipt), cross-platform reproducibility, and the user-facing attestation workflow. The incremental value is the verification layer, not the core hashing concept.

### Why This Does Not Exist

SLSA exists for software builds but not for calculation results. No structural engineering tool provides cryptographic attestation of calculations. This would be a world-first: provable, verifiable structural calculations.

### How It Works

```
Engineer calls: design_beam_is456(fck=25, fy=415, b_mm=300, d_mm=450, Mu=150)
    |
    v
Attestation Layer (middleware)
    |
    +-- Capture inputs: hash(fck=25, fy=415, b_mm=300, ...)
    +-- Record environment: library v0.21.3, commit abc123, Python 3.11.9
    +-- Execute calculation: result = design_beam_is456(...)
    +-- Capture outputs: hash(result)
    +-- Generate receipt:
        {
            "library_version": "0.21.3",
            "git_commit": "abc123def",
            "input_hash": "sha256:aabb...",
            "output_hash": "sha256:ccdd...",
            "timestamp": "2026-04-08T10:30:00Z",
            "clause_references": ["38.1", "40.4", "26.5.1"],
            "signature": "ed25519:eeff..."
        }
    |
    v
Engineer gets: (design_result, receipt)
    |
    v
Verifier (anyone):
    pip install structural-lib==0.21.3
    verify_receipt(receipt, design_result) -> VALID / TAMPERED
```

### Implementation Sketch

```python
# Python/structural_lib/services/attestation.py
import hashlib
import json
import time
from dataclasses import dataclass, asdict
from typing import Any
from importlib.metadata import version

@dataclass
class CalculationReceipt:
    library_version: str
    input_hash: str
    output_hash: str
    timestamp: float
    function_name: str
    clause_references: list[str]

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)

def hash_dict(d: dict) -> str:
    """Deterministic hash of a dictionary."""
    canonical = json.dumps(d, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()

def attest_calculation(func, kwargs: dict,
                       clause_refs: list[str]) -> tuple[Any, CalculationReceipt]:
    """Execute a calculation with attestation."""
    input_hash = hash_dict(kwargs)
    result = func(**kwargs)

    # Hash the result (handle dataclasses, dicts, floats)
    if hasattr(result, "__dict__"):
        output_hash = hash_dict(result.__dict__)
    elif isinstance(result, dict):
        output_hash = hash_dict(result)
    else:
        output_hash = hashlib.sha256(str(result).encode()).hexdigest()

    receipt = CalculationReceipt(
        library_version=version("structural-lib-is456"),
        input_hash=f"sha256:{input_hash}",
        output_hash=f"sha256:{output_hash}",
        timestamp=time.time(),
        function_name=func.__qualname__,
        clause_references=clause_refs,
    )
    return result, receipt

def verify_receipt(receipt: CalculationReceipt, func, kwargs: dict,
                   result: Any) -> bool:
    """Verify a calculation receipt is valid."""
    # Check input hash matches
    if f"sha256:{hash_dict(kwargs)}" != receipt.input_hash:
        return False
    # Re-run calculation
    reproduced = func(**kwargs)
    # Check output matches
    if hasattr(reproduced, "__dict__"):
        repro_hash = f"sha256:{hash_dict(reproduced.__dict__)}"
    elif isinstance(reproduced, dict):
        repro_hash = f"sha256:{hash_dict(reproduced)}"
    else:
        repro_hash = f"sha256:{hashlib.sha256(str(reproduced).encode()).hexdigest()}"
    return repro_hash == receipt.output_hash
```

### Architecture

```
Python/structural_lib/services/
    attestation.py                          <- receipt generation + verification (runtime feature)
Python/structural_lib/services/
    api.py                                  <- optional attestation wrapper for all public functions
scripts/verify_calculation.py               <- CLI tool for receipt verification
```

### AI Agent Integration

- **@backend** wraps public API functions with optional attestation
- **@security** reviews cryptographic implementation
- **@ops** integrates with release pipeline (published libs must be attestation-ready)
- **@library-expert** validates that attestation meets professional engineering standards

### Difficulty and Impact

- **Difficulty:** M-H (float determinism across platforms is a known hard problem)
- **Impact:** Critical — enables auditable, verifiable structural calculations (world-first)
- **Dependencies:** none for MVP (hashlib is stdlib); ed25519 signing for v2
- **Time estimate:** 1 week for core MVP, 2 weeks for CLI + integration

> **⚠️ Review Finding (3 bugs):** (1) `time.time()` makes receipts non-reproducible — use `time.perf_counter()` or deterministic timestamp input. (2) `str(result)` for float hashing is platform-dependent (repr differs across Python versions/OS). Use `struct.pack` or round to fixed precision. (3) `version("structural-lib-is456")` will raise `PackageNotFoundError` unless the package was pip-installed — add fallback to git commit hash or `__version__`.

### Example Scenario

A municipal building inspector reviews a beam design. The engineer provides the design report with an attestation receipt. The inspector runs `verify_calculation receipt.json` which confirms: (1) the calculation used structural-lib v0.21.3, (2) the inputs match the report, (3) the outputs have not been modified, (4) re-running the calculation produces identical results. The inspector accepts the design without needing to re-check every formula. Trust through verification.

---

## Implementation Priority

> **Revised after 3-agent review.** Phase 1 starts with quick wins (wire existing tools), not greenfield builds.

### Phase 1 — Quick Wins + Foundation (Weeks 1-4)

| # | Innovation | Effort | Why First |
|---|-----------|--------|-----------|
| 6 | API Breakage Detector | 2 days | Wire existing griffe into CI — highest ROI, lowest effort |
| 5 | Living Formula Docs | 3 days | Single script eliminates doc drift |
| 3 | Provenance Chain (extend existing) | 1 week | Extend @clause + traceability.py — foundation for Ideas 5, 8, 9 |
| 2 | Metamorphic Tests | 1 week | Write as plain Hypothesis tests, no framework needed |

### Phase 2 — Core Build (Weeks 5-10)

| # | Innovation | Effort | Why Now |
|---|-----------|--------|---------|
| 1 | Symbolic Crosscheck Engine | 3 weeks | Genuinely novel; catches formula errors that 5,000+ tests miss |
| 7 | Self-Healing CI | 2 weeks | Start with classifier only (no auto-remediation) |

### Phase 3 — Acceleration (Weeks 11-16)

| # | Innovation | Effort | Why Now |
|---|-----------|--------|---------|
| 8 | Golden Vector Factory | 2 weeks | Amplifies existing 69 golden vectors |
| 10 | Attestation MVP | 1 week | Hashing + receipts only, no signing/PKI |

### Phase 4 — Long-term (Weeks 17-24+)

| # | Innovation | Effort | Why Last |
|---|-----------|--------|----------|
| 9 | Amendment Propagation | 4 weeks | Depends on Idea 3 provenance; IS 456 amendments are infrequent |
| 4 | Agent Conflict Resolution | TBD | Deprioritized — existing hooks solve most of the problem; revisit if distributed agent coordination becomes a real issue |

## Dependencies Between Ideas

```
Idea 3 (Provenance)  ─────> Idea 9 (Amendment Propagation)
        |
        +──────────────────> Idea 5 (Living Docs)
        |
        +──────────────────> Idea 8 (Golden Vectors)

Idea 1 (Symbolic)    ─────> Idea 8 (Golden Vectors, cross-validation)

Idea 4 (Conflict)    ─────> improves all agent-touching ideas

Idea 6 (API Breakage) ───> Idea 10 (Attestation, version tracking)
```

## Risks and Challenges

| Risk | Mitigation |
|------|-----------|
| SymPy cannot prove all properties symbolically | Fall back to numerical verification with Hypothesis; track which properties are proven vs tested |
| Metamorphic relations may be wrong (false sense of safety) | Every relation must be validated by @structural-engineer; wrong relations are worse than no relations |
| Provenance maintenance overhead becomes too high | Auto-generate provenance from decorators + AST scanning; minimize manual metadata |
| Agent conflict resolution adds latency | Keep protocol lightweight (JSON files, not databases); fall back to manual orchestration if protocol fails |
| Living docs generate incorrect LaTeX | CI checks that generated docs match committed docs; rendered preview in PR |
| API breakage detector has false positives | Start strict, allow per-function exemptions with reason; tune over time |
| CI diagnostician misclassifies failures | Always show raw error alongside classification; human override available |
| Golden vectors from factory may have systematic errors | Cross-validation catches this; never deploy without engineer review |
| Amendment mapping is incomplete | Start with critical clauses (flexure, shear, column); expand iteratively |
| Attestation gives false sense of security | Clear disclaimer: attestation proves code identity, not structural safety |

---

## Conclusion

These 10 innovations transform how we BUILD the library, not what the library does. They address the specific infrastructure gaps that cause the most rework:

1. **Formula correctness** (Ideas 1, 2) — prove formulas right, not just test specific cases
2. **Traceability** (Ideas 3, 9) — link every line of code to its IS 456 source
3. **Documentation** (Idea 5) — make docs and code the same artifact
4. **API stability** (Idea 6) — catch breaking changes before users do
5. **Agent productivity** (Ideas 4, 7) — reduce conflicts and CI debugging
6. **Testing velocity** (Idea 8) — generate golden vectors in hours, not days
7. **Professional trust** (Idea 10) — verifiable, auditable calculations

Total implementation: ~30-35 weeks across 4 phases (revised from original ~20 week estimate after 3-agent review). Each idea is independent enough to deliver value on its own, but they compound when combined. The provenance chain (Idea 3) is the keystone — build it first, and half the other ideas become easier. Start with Idea 6 (2-day quick win wiring griffe) for immediate value.

No other structural engineering library in the world has any of these development infrastructure innovations. Building them makes this library not just technically superior, but TRUSTWORTHY.

---
