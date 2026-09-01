---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: intermediate
tags: [testing, verification, evidence]
---

# Testing Strategy

This guide owns the current test entry points and evidence taxonomy. Exact test
counts are deliberately not copied here because the maintained suites change.
Use collection or the task-owned evidence receipt when an exact count matters.

## Required command boundary

Run commands from the repository root through the worktree-bound launchers:

```bash
# Focused Python node
./scripts/python_runtime.sh -m pytest -q Python/tests/test_release_uat.py

# Complete product suites
./run.sh test
./run.sh test --fastapi
./run.sh test --react
./run.sh test --all

# Repository gates
./run.sh check --quick
./run.sh check
```

Do not use bare `python` or `pytest`. Do not assume that a linked worktree
shares ignored virtual environments or JavaScript dependencies. Confirm source
binding with `./scripts/python_runtime.sh --diagnose`.

The implementation sequence is:

1. use only a narrow reproducer while a change is still being debugged;
2. finish the bounded code, tests, generated owners, and documentation;
3. run the affected focused selection once after content freezes;
4. run any affected architecture/import/generated checks;
5. run the broad Python suite and full repository gate once at the cumulative
   milestone required by `AGENTS.md`;
6. push coherent commits together, verify one immutable artifact, and wait for
   all required hosted checks in the single PR cycle.

An outcome-changing repair after freeze repeats its affected evidence; unchanged
broad suites are not rerun for appearance.

## Python test taxonomy

The marker vocabulary is defined by `Python/pytest.ini`:

| Marker | Evidence purpose |
|---|---|
| `unit` | Fast calculation-module behavior |
| `integration` | Multi-module API, CLI, and export behavior |
| `regression` | Frozen golden and compatibility outcomes |
| `property` | Generated invariants and boundary exploration |
| `contract` | Public contract and signature protection |
| `performance` | Explicit environment-bound benchmarks |
| `golden` | Retained engineering golden vectors |
| `repo_only` | Requires the full repository checkout |
| `slow` | Excluded by the default package configuration |

Examples:

```bash
./scripts/python_runtime.sh -m pytest -q -m unit Python/tests
./scripts/python_runtime.sh -m pytest -q -m integration Python/tests/integration
./scripts/python_runtime.sh -m pytest -q -m regression Python/tests/regression
./scripts/python_runtime.sh -m pytest -q -m property Python/tests/property
./scripts/python_runtime.sh -m pytest -q -m contract Python/tests
```

Use `rg --files Python/tests` and targeted symbol searches before selecting a
path. A directory name does not by itself establish an evidence class.

## Property testing

Hypothesis profiles live in `Python/tests/conftest.py`. Use the maintained
runtime and the intended profile explicitly:

```bash
./scripts/python_runtime.sh -m pytest -q Python/tests/property --hypothesis-profile=dev
./scripts/python_runtime.sh -m pytest -q Python/tests/property --hypothesis-profile=ci
./scripts/python_runtime.sh -m pytest -q Python/tests/property --hypothesis-profile=exhaustive
```

Generated examples can falsify a contract or invariant. They do not become
independent engineering arithmetic or qualified review.

## Coverage

Coverage is one software signal, not a readiness score. When a task requires a
coverage run, bind the exact command, source, exclusions, and threshold in its
evidence receipt. Do not copy an old percentage into current documentation.

```bash
./scripts/python_runtime.sh -m pytest Python/tests \
  --cov=structural_lib --cov-branch --cov-report=term-missing
```

## Cross-surface verification

For a promoted journey, distinguish and bind the applicable surfaces:

| Surface | Required question |
|---|---|
| Direct Python | Does strict input reject before calculation and preserve the valid result? |
| Request model | Are type, finite, range, unit, enum, identity, relation, and collection decisions explicit? |
| Compatibility wrapper | Does it delegate to the same calculation owner without changing valid outcomes? |
| FastAPI | Where the journey is advertised, do error path/code and result status match Python? |
| Consumer | Can downstream output be produced without silent omission or non-finite values? |
| Exact wheel | Does the same recipe run with imports bound only to the installed artifact? |
| UI projection | Is the displayed status/identity current and accessible in the tested application? |

A surface that is unavailable or outside the packet is `NOT_TESTED` or
`NOT_APPLICABLE`; it is not silently promoted to PASS.

## Evidence classes

Keep these claims separate:

- independent arithmetic;
- controlled-source example;
- internal recomputation;
- wrapper or transport parity;
- generated regression/property evidence;
- UI projection;
- external-software comparison;
- qualified practicing-engineer review;
- explicit `NOT_TESTED`.

The cumulative receipt must say which class supports each claim. Green CI and
source-free artifact replay are software evidence, not professional approval.

## CI and hosted acceptance

The path/domain owner is `scripts/verification-manifest.json`. Unknown impact
fails closed to every domain. Pull requests must pass every applicable job and
the required `PR Gate` on the unchanged reviewed head. Never bypass, force,
or represent a skipped changed-path job as executed evidence.

Weekly/manual workflows can provide broader platform and artifact evidence, but
only when their exact head, runtime, inputs, and artifacts are bound in the
receipt.

## Safe troubleshooting

```bash
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json
./scripts/python_runtime.sh -m pytest --collect-only Python/tests
./run.sh verification plan
```

Do not delete caches, fixtures, retained evidence, ignored data, branches, or
worktrees to make a test pass. Record terminal dispatch issues and use the
fallback chain in `AGENTS.md`.

## Claim boundary

No software test, coverage percentage, generated vector, wrapper parity run,
browser projection, or hosted check grants professional approval,
engineering-use approval, release authorization, or publication.
