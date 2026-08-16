# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-17
- Focus: LIB-PRO-002-G0 contract-first remediation plan for confirmed input/defaulting, import-accounting, route-convergence, result/review, and release-truth defects
- Base: freshly fetched `origin/main = 904a2f8cf0ea5d4595f57c46dac06e2e837bba45`
- Lane: `codex/pre-release-input-safety-plan`; current source binding reports `source_bound=true`
- Pilot truth: the exact synthetic values matched independent arithmetic, and the footing dowel failure is correct; neither fact certifies the library or a whole-building workflow
- Decision: every next public package remains held until the Alpha gate in the active plan is accepted and the owner separately authorizes the exact release
- Current packet: G0 planning candidate; no calculation, API, UI, adapter, or release behavior changed
- Exact next packet after G0 merge: LIB-PRO-002-A strict service intake
<!-- HANDOFF:END -->

**Date:** 2026-08-17

| State | Boundary |
|---|---|
| **Current** | `v0.23.1a1` Alpha remains the current public release; `LIB-PRO-001` remains a completed historical evidence ledger |
| **Active** | `LIB-PRO-002-G0` freezes the new input-safety and publication contract |
| **Next** | `LIB-PRO-002-A`: strict beam project/service intake and negative contract matrix |
| **Held** | Publication, stable/engineering-use claims, professional approval, whole-building workflow, INDIA-3, dependency work, retained Git lanes, and unrelated cleanup |

## Required Reading

1. [Active pre-release input-safety plan](pre-release-input-safety-and-professional-readiness-plan.md)
2. [Current task board](../TASKS.md)
3. [Completed LIB-PRO-001 evidence ledger](professional-library-remediation-plan.md)
4. [Git workflow single source](../git-automation/git-workflow-single-source.md)

## Exact next start

Complete G0 repository validation and immutable review in the current lane. If
G0 merges, fetch and verify the new `origin/main`, then create one fresh
`codex/lib-pro-002-a-strict-input` worktree for Packet A.

```bash
./run.sh session brief --agent backend
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
```

Require `source_bound=true`, `READY_LOCAL`, no operation marker, exact equality
with freshly fetched `origin/main`, and a clean tree before Packet A edits.

## Packet A boundary

Own only the new versioned project input/result types,
`Python/structural_lib/services/batch.py`, and focused service tests. Start with
the plan's negative acceptance matrix and a spy proving that blocked input never
calls structural calculations. Then implement:

- required finite canonical values and stable field/path issue codes;
- mutually exclusive explicit `d_mm` or complete effective-depth basis;
- rejection of unknown/conflicting fields and duplicate member identities;
- no production structural defaults;
- empty/all-blocked summaries that cannot be PASS;
- unchanged numerical outcome for the accepted synthetic beam input.

Do not edit adapters, FastAPI/React routes, column/slab/footing behavior,
release automation, API classification, or whole-building calculations in
Packet A.

## Validation cadence

Run focused service tests and the architecture/import boundary check during
Packet A. Run quick once after content freeze. Reserve broad Python,
FastAPI/React, full canonical, packaging, and exact-wheel gates for cumulative
Packet G unless an outcome-changing failure proves repository-wide risk.

## Stop rule

G0 ends after its exact candidate is independently accepted and merged. Packet
A requires its own fresh lane. Do not infer tag/package publication,
professional approval, whole-building implementation, issue closure, branch
deletion, or retained-lane cleanup authority.
