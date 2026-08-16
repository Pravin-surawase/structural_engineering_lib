# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-17
- Focus: LIB-PRO-002-A strict beam project/service intake, blocking issue contract, effective-depth basis, and accounted batch result
- Base: freshly fetched `origin/main = 55104e11257937b0a42fb06f931a70b8484cef39`
- Lane: `codex/lib-pro-002-a-strict-input`; current source binding reports `source_bound=true`
- G0 closeout: PR #812 merged at the exact base above; the reviewed G0 tree changed no calculation, API, UI, adapter, or release behavior
- Pilot truth: the exact synthetic values matched independent arithmetic, and the footing dowel failure is correct; neither fact certifies the library or a whole-building workflow
- Decision: every next public package remains held until the Alpha gate in the active plan is accepted and the owner separately authorizes the exact release
- Current packet: Packet A local candidate; 43 focused service cases, focused Mypy/Ruff, architecture, and import checks pass before the final post-repair quick gate
- Exact next action: freeze Packet A evidence/indexes, run quick once, create the immutable local candidate, and obtain exact-head independent review before push
<!-- HANDOFF:END -->

**Date:** 2026-08-17

| State | Boundary |
|---|---|
| **Current** | `v0.23.1a1` Alpha remains the current public release; `LIB-PRO-001` remains a completed historical evidence ledger |
| **Active** | `LIB-PRO-002-A`: strict beam project/service intake local candidate; immutable review and hosted closeout remain |
| **Next** | `LIB-PRO-002-B`: lossless import boundary, only after Packet A merges |
| **Held** | Publication, stable/engineering-use claims, professional approval, whole-building workflow, INDIA-3, dependency work, retained Git lanes, and unrelated cleanup |

## Required Reading

1. [Active pre-release input-safety plan](pre-release-input-safety-and-professional-readiness-plan.md)
2. [Current task board](../TASKS.md)
3. [Completed LIB-PRO-001 evidence ledger](professional-library-remediation-plan.md)
4. [Git workflow single source](../git-automation/git-workflow-single-source.md)

## Exact next start

Resume only the existing Packet A worktree while it remains cleanly bound to
the exact candidate. Do not recreate the branch or migrate its changes into a
retained lane.

```bash
./run.sh session brief --agent backend
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
```

Before any repair candidate, require `source_bound=true`, no operation marker,
and the expected branch/head/diff. A changed base, overlapping dirty path, or
second rejected candidate returns Packet A to contract/design planning.

## Packet A boundary

Packet A owns only the new versioned project input/result types,
`Python/structural_lib/services/batch.py`, focused service tests, and compact
task/session handoff evidence. The local candidate implements:

- required finite canonical values and stable field/path issue codes;
- mutually exclusive explicit `d_mm` or complete effective-depth basis;
- rejection of unknown/conflicting fields and duplicate member identities;
- no project structural defaults and no alias precedence;
- empty/all-blocked summaries that cannot be PASS;
- unchanged numerical outcome for the accepted synthetic beam input.

The legacy batch functions now delegate to the strict contract. Aliases may map
only when their values agree; missing structural values still block. Blocked or
duplicate members never call `design_beam_is456`.

Do not edit adapters, FastAPI/React routes, column/slab/footing behavior,
release automation, API classification, or whole-building calculations in
Packet A.

## Validation cadence

Focused service tests, Ruff, Mypy, architecture, and import validation pass.
Run quick once after the final receipt/index write. Reserve broad Python,
FastAPI/React, full canonical, packaging, and exact-wheel gates for cumulative
Packet G unless an outcome-changing failure proves repository-wide risk.

## Stop rule

Packet B does not start until Packet A's unchanged exact head is independently
accepted, required hosted checks pass, and Packet A merges. Do not infer
tag/package publication, professional approval, whole-building implementation,
issue closure, branch deletion, or retained-lane cleanup authority.
