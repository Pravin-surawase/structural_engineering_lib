---
owner: Main Agent
status: active
last_updated: 2026-10-29
doc_type: guide
complexity: beginner
tags: [onboarding, development]
---

# Onboarding Guide for New Developers

**Type:** Guide
**Audience:** Developers
**Status:** Active
**Importance:** High
**Last Updated:** 2026-10-29

## First 30 minutes

1. Read [AGENTS.md](../../AGENTS.md) and the selected task's scope. Verify the
   actual checkout and current Git state before writing.
2. Follow the [Python quickstart](python-quickstart.md) for the complete first
   calculation and CSV → design → BBS → report journey. It supplies all required
   inputs and separates optional rendering dependencies.
3. Use [API levels](../reference/api-levels.md) and the
   [family cookbook](../cookbook/python/family-facades.md) to choose a promoted
   typed task API and its declared support class.
4. Read [Agent Coding Standards](../contributing/agent-coding-standards.md) before
   changing a maintained owner. Use the [native Git workflow](../git-automation/git-workflow-single-source.md)
   for the scoped branch/PR and required checks.

## Find the implementation

| Layer | Location | Meaning |
| --- | --- | --- |
| Core types | `Python/structural_lib/core/` | Shared types and explicit evidence/result state |
| IS 456 code | `Python/structural_lib/codes/is456/` | Pure calculations with units and source provenance |
| Services | `Python/structural_lib/services/` | Admission, adapters, workflows and serialization |
| UI/IO | `fastapi_app/`, `react_app/` | Application interaction using the maintained services |

Imports point inward. Root modules such as `structural_lib.api` are retained
compatibility projections, not the implementation location. Do not start new
math in `core/`, put implementation into `api.py`, or use retired Streamlit
paths. Inspect the exact public signature and caller before editing.

## A source-bound first command

From the repository root, after the project's environment is available:

```bash
./scripts/python_runtime.sh -m structural_lib capabilities --json
./scripts/python_runtime.sh -m structural_lib design Python/examples/sample_beam_design.csv -o output/onboarding-results.json
./scripts/python_runtime.sh -m structural_lib bbs output/onboarding-results.json -o output/onboarding-schedule.csv
```

The shipped sample supplies a physical bar-diameter basis for its effective
depths. Its generated one-layer bar centroids must agree with strength inputs.
An invalid row or unverified layout blocks the command; do not bypass that
check. Output paths name files, not a directory whose contents are invented.

## Understand the result

Invalid intake is rejected before a design. Admitted results can be `PASS`,
`FAIL` or `HOLD`. Inspect source/case identity, completeness, freshness, issues,
unavailable quantities and approval state; software success is not professional
approval. Use the [library contract](../reference/library-contract.md) and
[API reference](../reference/api.md) for the maintained semantics.

## Make and verify a change

Trace a reproduced main-process problem to its owner. Complete the scoped code,
tests and documentation as one batch, then format/lint and run affected tests
with `./scripts/python_runtime.sh` and the changed-area checks. Reuse existing
adapters and serializers. Preserve compatibility unless the selected task
explicitly owns its migration. Do not copy stale function examples or global
inventories into another guide.

Use the canonical coding guide for numerical-change evidence, output review,
working directories and delivery. Excel/VBA and the separate XLL planning track
have their own artifact/native-host gates; a Python package installation does
not supply or qualify those applications.
