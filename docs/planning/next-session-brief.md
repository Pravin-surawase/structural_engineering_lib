# Next Session Briefing

## Latest Handoff

<!-- HANDOFF:START -->
- Date: 2026-08-11
- Focus: Concentric isolated-footing calculation, detailing, API, and React workbench complete through D1
<!-- HANDOFF:END -->

**Current release:** `v0.23.0` Alpha

**Branch:** `codex/footing-isolated-v1` (local; not pushed)

**Base:** `a0e115e1` (`origin/main` at branch creation)
**Task board:** [TASKS.md](../TASKS.md)

| State | Target | Decision |
|---|---|---|
| **Current** | Concentric isolated footing D1 | Calculation, detailing, typed API, and workbench are verified locally |
| **Next** | Owner review / integration decision | Reconcile with current main and open a PR only when explicitly requested |
| **Held** | Report/export, catalogue, production use | Outside D1; qualified structural-engineering review remains mandatory |

## Required Reading

- [Latest session record](../SESSION_LOG.md)
- [Current task board](../TASKS.md)
- [Release policy](../getting-started/releases.md)

## Accepted footing outcome

- The maintained scope is one concentric square/rectangular isolated-footing
  workflow with explicit service and factored actions, external allowable-soil-
  pressure approval, and approved A1 load-transfer evidence.
- Overall thickness and effective depth are distinct; flexure, directional
  one-way shear, punching shear, bearing and uniform-depth selection are
  fail-closed.
- Optional two-layer bottom-reinforcement detailing returns physical directional
  depths, bar schedules, rectangular central/outer-band zones, anchorage evidence
  and linked dowels. Missing or unsupported inputs remain visible HOLDs.
- One typed FastAPI route and one lazy React workbench page preserve separate
  calculation, detailing and aggregate statuses, provenance, exclusions and
  revision-safe result authority.

## Verification

- 206 focused footing/core/service/load-transfer/golden-vector/FastAPI tests pass.
- The React gate passes ESLint, 246 tests and the production build; the footing
  page remains a separate 34.84 kB lazy chunk.
- `./run.sh check --quick` passes 10/10.
- `PYTHONPATH="$PWD/Python" ./run.sh check` passes 30/30 and binds the gate to
  this worktree rather than another editable checkout.

## Holds and exclusions

- Eccentric, combined, strap, raft, pile-cap, sloped/stepped and uplift footing
  cases are outside this bounded workflow.
- Report/export and catalogue integration are intentionally absent from D1.
- External soil-bearing approval, approved A1 load-transfer evidence, source/
  licensing verification before launch, and qualified structural-engineering
  review are not replaced by green software checks.
- No push, pull request, merge, release or publication has been performed.

## Repeat-prevention record

Run worktree validation with `PYTHONPATH="$PWD/Python"` when reusing the primary
virtual environment. After any public signature change, regenerate
`docs/reference/api-manifest.json`. Preserve explicit screening versus final
provided-steel shear evidence and never convert absent approvals into request
literals.
