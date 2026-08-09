---
name: function-quality-pipeline
description: "Implement or materially change an IS 456 calculation function with traceable engineering inputs, the correct layer, narrow evidence, and one non-duplicative closeout gate."
argument-hint: "Function name and IS 456 clause or calculation scope"
---

# IS 456 Function Quality Pipeline

Use this for a new or materially changed calculation in `Python/structural_lib/codes/is456/`. Do not invoke it for a thin service re-export, documentation-only work, or review-only work.

The active parent normally performs the stages below. Named project roles describe quality concerns, not a mandatory multi-agent chain.

## Required Intake

Before editing, write down:

- exact calculation/function outcome in scope;
- relevant IS 456 edition and clause identifiers, paraphrased rather than copied at length;
- input/output quantities and explicit units;
- trusted benchmark source, inputs, expected result, and justified tolerance;
- public API or UI wiring required by the request;
- non-goals, especially adjacent element cases and speculative edge cases.

If the clause source or benchmark needed to establish correctness is unavailable, stop before implementing the formula. Passing repository tests cannot replace that evidence.

## 1. Locate Existing Behavior

```bash
rg -n "<function_or_concept>" Python/structural_lib Python/tests fastapi_app
./run.sh find --api <function_name>
```

Inspect the folder index and the nearest implemented calculation. Reuse current validators, result types, constants, traceability utilities, and error conventions. Do not create a parallel formula or public name.

## 2. Define the Calculation Contract

Record the symbolic formula, dimensional reduction, permitted input domain, result meaning, and failure behavior. Resolve these before coding:

- which layer owns each input and conversion;
- whether an existing result type is correct;
- what a zero or invalid denominator means physically;
- whether the benchmark uses the same design assumptions;
- which existing public behavior must remain compatible.

Do not silently clamp, return zero, or change safety factors unless the governing formula explicitly requires it.

## 3. Implement the Root Calculation

- Put pure calculation logic in the existing element subpackage under `codes/is456/`.
- Keep I/O, environment access, serialization, and network behavior out of the calculation layer.
- Use explicit unit suffixes and readable intermediate values.
- Cite the clause identifier near the formula and explain any non-obvious conversion.
- Validate inputs consistently with adjacent functions.
- Use `safe_divide()` only with a deliberate domain-appropriate default; otherwise reject the invalid domain.
- Match the established result/error pattern instead of imposing a new universal dataclass shape.

Run the narrowest existing test or direct calculation check after the calculation is stable.

## 4. Establish Engineering Evidence

For implementation work, add or update only the narrow tests needed for the requested calculation. Cover the accepted benchmark and the governing limit that changes the main result. Do not invent universal test counts or tolerances.

```bash
.venv/bin/pytest <exact-test-path> -q
.venv/bin/pytest Python/tests/ -q -k "<function_or_clause>"
```

Independently compare the computed result with the recorded source and show units. A benchmark mismatch is a stop condition; do not loosen the tolerance merely to pass.

For review-only work, inspect existing evidence and report outcome-changing defects only. Do not add tests.

## 5. Wire Only Requested Consumers

If a public service is required, add it through the existing element API module and public facade, then rediscover its signature:

```bash
./run.sh find --api <function_name>
```

Add FastAPI and React consumers only when they are part of the requested main process. Preserve layer direction and keep unit conversions at explicit boundaries. Do not build every layer for a library-only change.

## 6. Verify Without Duplication

During implementation, run only affected checks. Before commit:

```bash
.venv/bin/python scripts/check_architecture_boundaries.py
.venv/bin/python scripts/validate_imports.py --scope structural_lib
./run.sh check --quick
```

At stable closeout, run `./run.sh check` once. If a gate fails, repair the root cause with its narrow command; repeat the full gate only to establish the final green result or when the fix affects other categories.

## 7. Handoff and Commit

The handoff must state:

- formula/clause and benchmark source used;
- exact files and public consumers changed;
- targeted and closeout commands with results;
- remaining owner or qualified-engineer decisions;
- explicit statement that software verification is not professional design approval.

Commit only through:

```bash
./run.sh pr status
./scripts/ai_commit.sh "feat(is456): <outcome>"
```

## Stop Conditions

Stop when the governing source is ambiguous, units cannot be reconciled, the benchmark disagrees, the requested change would require an unapproved broader element scope, or a qualified engineering decision is missing.
