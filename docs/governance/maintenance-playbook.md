# Governance & Maintenance Playbook

**Type:** Guide
**Audience:** All Agents
**Status:** Active
**Importance:** High
**Created:** 2026-04-02
**Last Updated:** 2026-09-27

This is the canonical maintenance guide. [AGENTS.md](../../AGENTS.md), the
[Git workflow](../git-automation/git-workflow-single-source.md#routine-integration)
and [token-efficiency policy](../guidelines/ai-token-efficiency.md) own execution
rules. Maintenance fixes confirmed drift and preserves unfinished work.

## 1. Per-Session Checklist

### Session Start

Run one task-bound start from the verified repository root:

```bash
./run.sh session begin --task-id <task> --agent <role>
git fetch origin
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
```

The start already supplies a compact brief and environment check. Confirm the
remote, current PR and writer device before edits. Read additional context only
for the task. Create a `codex/<task-slug>` branch from synchronized main.

### Session End

Complete related work in cohesive commits. After the batch, format changed
files, run affected behavior checks once, review the essential diff, and publish
one PR. Required hosted checks must pass on the reviewed head before merge.
Close the timer after delivery:

```bash
./run.sh session usage --checkpoint closeout --task-id <task> \
  --verification "focused tests and required PR checks passed"
```

Update the maintained handoff when the next task, completed milestone or device
boundary changes. Routine commits do not require multiple session records,
delivery-ledger transitions, evolution runs or a second validation suite.

## 2. Weekly Maintenance

Inspect GitHub and the current checkout, then select diagnostics for the
maintenance question:

```bash
./run.sh health
./run.sh feedback summary
./run.sh efficiency check
./run.sh context validate
```

Health is a repository diagnostic, not engineering acceptance. Repair confirmed
issues at their owning source. Inspect a fix before applying it; a generic
`--fix` suggestion does not authorize broad edits. Existing feedback is closed
only after its resolution is proved. No change means no maintenance commit.

## 3. Monthly Review

Review recurring failures, dependency/release needs and unfinished work.
Run `./run.sh check --full` or a broad test suite only for a named release or
repository-wide risk. Routine `./run.sh check` selects essential changed-area
checks; do not stack quick, default and full runs on an unchanged candidate.

Branch/worktree classification is read-only. Missing remote evidence remains
unknown; age, a green score or a merged branch does not authorize deletion.

## 4. Quality Gate Enforcement (Per PR)

For new engineering calculations, use the maintained
[function-quality workflow](../../.github/skills/function-quality-pipeline/SKILL.md)
and approved feature scope. Preserve explicit units, source provenance and
independent arithmetic evidence. Named quality roles do not require separate
agents. Routine maintenance does not rerun unchanged engineering suites.

## 5. Quarterly Benchmarks (Structural Engineering)

Use a representative workload and before/after evidence when making a speed
claim. Select existing independent benchmarks for affected calculations.
Inspect code amendments only when that source review is in scope. Formula,
installed-host and whole-building acceptance remain distinct.

## 6. Error Handling Standards

Use the [error-handling standard](../guidelines/error-handling-standard.md).
Preserve structured input failures, engineering FAIL/HOLD, incomplete or stale
evidence, and human approval as separate outcomes throughout caller workflows.

## 7. Governance Limits

Use current executable checks and maintained owners rather than copying counts
or inventories into guides. HTTP operation counts come from
`scripts/sync_numbers.py:scan_endpoints`, which reads the independently checked
default OpenAPI snapshot; decorator matches and WebSockets are not that count.

No automatic archive, move or deletion follows from document age or count.
Preserve unrelated dirty work, old candidates and device-only evidence.

## 8. Documentation and Context Validation

Prefer updating a canonical document to creating another. For a status report,
state its time window, evidence source, confirmed defects, effect and next work.
Check metadata as well as rendering: a successful MkDocs build does not validate
the document's status/type vocabulary.

```bash
./scripts/python_runtime.sh scripts/check_docs.py --all
./scripts/python_runtime.sh scripts/check_links.py
./run.sh context validate
```

These are available diagnostics; use the selected changed-area check when it
already covers them. Correct reported metadata explicitly; `check_docs.py`
has no `--fix` option. Use safe-file tools for authorized moves/deletions and
preview their exact targets first. Generic folder indexes remain retired.

## 9. Release Checklist

Each release needs the owner's per-release authorization and the maintained
release preflight. A source build or successful example is not a publication.
Use the [release checklist](../planning/pre-release-checklist.md) when a release
is actually selected.

## 10. Incident Response

Reproduce the main-process failure, trace the responsible boundary, fix its
owner, and rerun the affected evidence. Record symptom, confirmed root cause,
resolution and proof once. During maintenance, reuse recurrence IDs for the
same cause; do not count mentions or repeated reports as new incidents.

## 11. Agent System Maintenance

Use `./run.sh tools`, `./run.sh route "task"`, and the maintained registries
for discovery. Keep one parent by default. Use
`./run.sh evolve --review weekly` only for an explicit governance review;
evolution is not a routine session-end mutation. Preserve provider settings and
report actual elapsed time rather than invented token or cost estimates.
