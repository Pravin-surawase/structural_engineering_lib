---
name: quality-gate
description: "Apply the project verification ladder without duplicating gates: implementation first, necessary narrow diagnostics, one consolidated focused selection, one quick pre-commit gate, the required PR Gate, one cumulative full gate, and release preflight only for releases."
---

# Quality Gate

Use the repository's canonical gates from the workspace root. Do not recreate them with ad hoc greps, repeated test suites, or persistent `cd` commands.

## When to Use

- Before committing a production change
- Before a PR is accepted or merged
- At implementation closeout
- Before a release

## Verification Ladder

### 1. Implement the bounded scope first

Complete the scoped code, tests, documentation, evidence, and other intended
writes before the routine verification sequence. Do not treat every saved edit
as a gate boundary.

### 2. While editing: diagnose only when needed

When a current question or failure requires evidence, run only the smallest
existing check that exercises the changed main process. Do not rerun a check
merely because another edit was made. Examples:

```bash
./scripts/python_runtime.sh -m pytest Python/tests/path/to/test_file.py -q
./scripts/python_runtime.sh -m pytest fastapi_app/tests/path/to/test_file.py -q
npm --prefix react_app run lint
./scripts/python_runtime.sh scripts/check_architecture_boundaries.py
```

Choose commands from the affected component's skill or existing project automation. Do not add tests during a review-only task.

### 3. After content freeze: focused evidence together

After all intended versioned writes are complete, run the affected focused
tests, benchmarks, and architecture/import checks as one consolidated
selection. Refresh maintained indexes once before this selection when they are
affected.

### 4. Before commit: quick gate once

```bash
./run.sh check --quick
```

If it fails, diagnose the first relevant failure, fix its root cause, rerun that narrow check, then rerun the quick gate once.

### 5. PR acceptance: required CI

The GitHub check named `PR Gate` is the authoritative merge gate. Inspect the check for the current commit. Do not rerun an equivalent local suite merely because CI already passed it. A failing or stale check blocks acceptance; bypass flags and admin merges are forbidden.

### 6. Cumulative implementation closeout: full gate once

```bash
./run.sh check
```

Run the full gate once after all intended packets in the milestone are integrated.
Run it earlier only when repository-wide risk makes that necessary. After a
failure, rerun only the failed check while repairing it; repeat the full gate
only when the fix can affect other categories or to establish the final green
result.

### 7. Release only

For an actual release candidate, use the release skill and its canonical preflight:

```bash
./run.sh release preflight <version>
```

Do not run packaging, Docker, UAT, or release checks for an ordinary review or commit.

## Essential-Only Review Rule

For each possible finding ask: **Would fixing it change the outcome of the main process in scope?** Report and block only when the answer is yes and the defect is confirmed by evidence. Ignore comments, adjacent improvements, coverage gaps, generic hardening, and security or concurrency observations that do not change that outcome. Do not add tests during review.

## Report Format

```
## Quality Gate Report

| Check | Status | Details |
|-------|--------|---------|
| [check name] | ✅/❌/⚠️ | [details] |

**Gate:** PASS / FAIL
**Current commit:** [hash]
**Blockers:** [only confirmed main-process failures]
**Not rerun:** [checks already covered by green CI, if any]
```

## Who Uses This

- **@reviewer** — evaluates main-process findings and PR Gate evidence
- **@ops** — runs the safe Git/CI workflow and release preflight
- **@tester** — runs narrow behavior checks and the canonical closeout gate
- **@governance** — keeps the gate definitions truthful and non-duplicative
