---
name: is456-verification
description: "Verify a changed IS 456 calculation against its governing source, units, benchmark, and existing targeted regression evidence without substituting test counts for engineering correctness."
---

# IS 456 Verification

Use after changing a calculation or when diagnosing a reported structural result. Verification has two independent parts: engineering evidence and software execution.

## Required Evidence

- IS 456 edition and clause identifiers governing the result;
- formula and assumptions used by the implementation;
- explicit input/output units;
- trusted independent benchmark with expected value and justified tolerance;
- exact supported case and exclusions.

Tests passing prove software behavior only. They do not certify the formula, replace access to the governing standard, or constitute professional design approval.

Do not require a separate qualified sign-off for each verified development
change or Alpha release. Preserve the evidence for cumulative review before a
stable or engineering-use approval.

## Locate the Narrow Evidence

```bash
rg -n "<function_or_clause>" Python/structural_lib/codes/is456 Python/tests
rg --files Python/tests | rg "<element_or_topic>"
```

Choose the exact existing test module or keyword that exercises the changed main result. Do not rely on a stale file list in instructions.

## Run Targeted Verification

```bash
./scripts/python_runtime.sh -m pytest <exact-test-path> -q
./scripts/python_runtime.sh -m pytest Python/tests/ -q -k "<function_or_clause>"
```

Compare the result independently with the benchmark and show the unit conversion. Use the source's precision to set tolerance; do not apply one universal percentage to tables, charts, and textbook examples.

When the task is review-only, do not add tests. Report only a confirmed mismatch that changes the scoped design outcome.

## Structural Closeout

For an implemented structural change:

```bash
./scripts/python_runtime.sh scripts/check_architecture_boundaries.py
./scripts/python_runtime.sh scripts/validate_imports.py --scope structural_lib
./run.sh check --quick
```

Run the full `./run.sh check` once at stable closeout. Use `./run.sh test` only when the change can affect the broader Python suite or as the designated full test run; do not repeatedly run both equivalent full gates.

## Failure Decision

- Benchmark mismatch: stop and resolve formula, assumptions, or units.
- Targeted regression failure: fix the root calculation or contract; do not update an expected value without source evidence.
- Unavailable or ambiguous governing evidence: stop or narrow the supported
  case, record the unresolved interpretation, and defer it to the final
  qualified-review ledger.
- Unrelated pre-existing failure: preserve evidence and keep it outside the current implementation unless it blocks the main process.

## Report

Return the clause/source, benchmark case, actual versus expected result with
units, commands run, supported conclusion, exclusions, and evidence deferred to
the final qualified review.
