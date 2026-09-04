---
name: quality-gate
description: "Apply the executable project verification ladder without duplicating gates: implementation first, changed-path formatting, consolidated focused evidence, one read-only candidate-integrity check, the required PR Gate, one cumulative full gate, and release preflight only for releases."
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

### 3. After content freeze: format and focused evidence together

After all intended versioned writes are complete, run the affected focused
tests, benchmarks, and architecture/import checks as one consolidated
selection. First run `./run.sh format --write`; it selects only changed Python,
FastAPI, and C# paths and fails if formatter bytes escape that scope. Validate
live repository context before this selection when routing or repository
structure is affected; this check is read-only.

### 4. Accepted candidate: integrity once

```bash
./run.sh check --candidate-integrity
```

Run this read-only hosted-equivalent file check only after the independent audit
accepts the immutable candidate. If it fails, the candidate is not immutable:
record `INTEGRITY_REJECTED`, return to the writer state, repair the root cause,
and create the one allowed repair candidate. A failure on that repaired
candidate enters `REPLAN`. Do not run `check --quick` as a ritual before every
commit.

### 5. PR acceptance: required CI

The GitHub check named `PR Gate` is the authoritative merge gate. Inspect the check for the current commit. Do not rerun an equivalent local suite merely because CI already passed it. A failing or stale check blocks acceptance; bypass flags and admin merges are forbidden. Record a failed hosted run as `HOSTED_REJECTED` before repairing its confirmed root cause. The replacement candidate must repeat exact-head audit, integrity, pre-push closeout, and one hosted verdict; retain the failed run in closeout metrics.

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
