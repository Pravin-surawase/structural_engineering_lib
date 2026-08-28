# Python Test Guide

Run every command from the repository root. The maintained launcher binds tests
to the current worktree's Python source; do not use bare `python`, `pytest`,
or a different checkout's virtual environment.

## Standard gates

```bash
# Complete Python package suite (configured to exclude slow tests)
./run.sh test

# One exact focused selection
./scripts/python_runtime.sh -m pytest -q Python/tests/unit/test_flexure.py

# Repository quick gate
./run.sh check --quick

# Cumulative repository gate
./run.sh check
```

Use the broad Python suite and full repository gate once at the cumulative
candidate boundary described by `AGENTS.md`. During implementation, run only
the narrow reproducer needed to guide the current change, then batch the
affected focused tests after content freezes.

## Maintained categories

The marker vocabulary is owned by `Python/pytest.ini`:

| Marker | Purpose |
|---|---|
| `unit` | Fast calculation-module tests |
| `integration` | Multi-module API, CLI, and export tests |
| `regression` | Frozen golden and compatibility outcomes |
| `property` | Invariant and generated-boundary tests |
| `contract` | Public contract and signature protection |
| `performance` | Explicit benchmark tests |
| `golden` | Retained engineering golden evidence |
| `repo_only` | Requires the complete repository checkout |
| `slow` | Takes more than one second and is excluded by default |

Examples:

```bash
./scripts/python_runtime.sh -m pytest -q -m unit Python/tests
./scripts/python_runtime.sh -m pytest -q -m integration Python/tests/integration
./scripts/python_runtime.sh -m pytest -q -m regression Python/tests/regression
./scripts/python_runtime.sh -m pytest -q -m property Python/tests/property
./scripts/python_runtime.sh -m pytest -q -m contract Python/tests
./scripts/python_runtime.sh -m pytest -q -m performance Python/tests/performance
./scripts/python_runtime.sh -m pytest -q -m "not slow" Python/tests
```

Do not infer an evidence class from a directory name alone. Independent
arithmetic, controlled-source examples, internal recomputation, wrapper parity,
generated regression, UI projection, and qualified review remain distinct.

## Focused test selection

Search before guessing a path:

```bash
rg -n "symbol_or_journey" Python/tests Python/structural_lib
rg --files Python/tests | rg "beam|column|slab|footing"
```

Then run the exact node or file:

```bash
./scripts/python_runtime.sh -m pytest -q Python/tests/integration/test_external_preview_r0.py
./scripts/python_runtime.sh -m pytest -q Python/tests/test_release_uat.py::test_release_negative_matrix_and_public_examples_pass
```

For the configured package context needed by type checking, follow the exact
command in the current task authority or run the maintained gate that owns it.
Do not change terminal directories and assume they will reset between commands.

## Property and performance profiles

```bash
./scripts/python_runtime.sh -m pytest -q Python/tests/property --hypothesis-profile=dev
./scripts/python_runtime.sh -m pytest -q Python/tests/property --hypothesis-profile=ci
./scripts/python_runtime.sh -m pytest -q Python/tests/performance -m performance --benchmark-only
```

Performance results are environment-bound observations. Record the runtime,
dataset, threshold, and exact source before using them as evidence.

## Troubleshooting

- Confirm source binding with `./scripts/python_runtime.sh --diagnose`.
- Confirm the current worktree with
  `./scripts/python_runtime.sh scripts/git_state.py --json`.
- Use `./scripts/python_runtime.sh -m pytest --collect-only Python/tests` to
  inspect discovery.
- Do not delete caches, test files, fixtures, retained evidence, or ignored data
  as a troubleshooting shortcut.
- If a maintained command fails before dispatch, record the terminal issue and
  use the fallback chain in `AGENTS.md`.

## Evidence and claim boundary

A passing generated or wrapper-parity test does not become independent
engineering validation. A green software suite does not grant professional
approval, engineering-use approval, release authorization, or publication.
