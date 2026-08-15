# Next Session Briefing

## Latest Handoff

<!-- HANDOFF:START -->
- Date: 2026-08-15
- Focus: Integrate INDIA-1B rectangular-column decision closure, then start INDIA-1C with milestone-level gate efficiency
- Draft PR: [#755](https://github.com/Pravin-surawase/structural_engineering_lib/pull/755)
- Branch: `codex/india-1b-column-decision-closure`
- Base: verified integrated `origin/main` at `3a7e162e049f28a9c9f63438f44ff116aa408e26`
- Implementation commit: `64a75d5f7543928154ae8072f27dd2a948a04bbb`
- Next action: inspect PR #755 at its live exact head; if required checks pass with no conflicts or blockers, mark ready, merge, verify integrated main, and start INDIA-1C from a fresh lane
- Holds: no release, engineering-use approval, branch/worktree deletion, or historical-lane cleanup
<!-- HANDOFF:END -->

**Date:** 2026-08-15

| Release state | Target |
|---|---|
| **Current** | `v0.23.1a1` Alpha; qualified engineering review still required |
| **Next** | Publish INDIA-1B, then execute INDIA-1C and 1D as bounded packets |

## Required Reading

1. [INDIA-0 truth baseline](../verification/indian-code-truth-baseline.md)
2. [Generated Indian-code manifest](../verification/indian-code-capability-coverage.json)
3. [Current task board](../TASKS.md)
4. [IS 456 library-first plan](is456-library-first-master-plan.md)
5. [Canonical Git workflow](../git-automation/git-workflow-single-source.md)

## Start Boundary

INDIA-1A is integrated. Finish INDIA-1B only from its isolated branch. After its
exact-head PR checks pass with no conflicts or blockers, merge normally, fetch
`origin/main`, verify tree identity, and create a fresh isolated
`codex/india-1c-<packet>` lane. Preserve the dirty primary checkout and all
unrelated worktrees; do not bypass checks.

```bash
./run.sh session brief --agent structural-math
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
./scripts/python_runtime.sh scripts/generate_indian_code_manifest.py --check
```

Require `source_bound=true` before producing test or benchmark evidence.

## INDIA-1 Objective

Close or explicitly retain every material limitation inside the already
supported IS 456 beam, rectangular-column, isolated-footing, and solid-slab
families. “Close” means an independently benchmarked, provenance-bearing,
fail-closed supported route. “Retain” means the manifest and public capability
wording clearly exclude the case and identify the analysis or evidence needed.

This wave does not add walls, stairs, deep beams, flat slabs, combined/strap/
raft/pile-cap foundations, IS 875 load generation, or IS 1893 analysis. Those
remain INDIA-2 or INDIA-3 work.

## Recommended Packet Sequence

### INDIA-1A — Beam route closure

- Inventory existing flanged-flexure, torsion, shear, detailing, deflection,
  and crack-width math before adding code.
- Decide and implement the smallest coherent combined flanged-beam route.
- Propagate only explicit serviceability inputs supported by maintained math.
- State load-envelope and torsion-redistribution exclusions fail-closed.
- Do not claim hollow/box, deep, prestressed, or axially loaded beam support.

### INDIA-1B — Rectangular-column decision closure

- Reconfirm the supported symmetric/two-face rectangular reinforcement model.
- Decide whether circular, asymmetric, and arbitrary multilayer layouts remain
  held or need separate approved packets; do not silently broaden geometry.
- Keep experimental PMM work outside the stable capability unless its separate
  numerical and API acceptance gates are completed.

### INDIA-1C — Isolated-footing composed workflow

- Compose sizing, flexure, one-way shear, punching, bearing pressure, detailing,
  and concentric load transfer into one reviewable supported workflow.
- Add eccentric pressure only after documenting load reference, contact model,
  units, kern/tension assumptions, and unsafe/out-of-domain behavior.
- Keep combined, strap, raft, pile-cap, settlement, lateral stability, and soil-
  structure interaction outside this packet.

### INDIA-1D — Solid-slab serviceability and shear boundary

- Evaluate direct deflection and crack-width routes with explicit required
  geometry, material, load-duration, reinforcement, and service-stress inputs.
- Add automatic shear reinforcement only for a justified supported slab model;
  otherwise retain the exclusion explicitly.
- Define the load-envelope boundary. Concentrated loads, openings, irregular
  panels, flat slabs, and FEM remain held unless separately approved.

## Acceptance Per Packet

- Governing edition, clause/table identifier, and source provenance are explicit.
- Units, geometry, loading, topology, and support assumptions are explicit.
- Pure math is accepted before service, FastAPI, or React expansion.
- At least one independent benchmark has a justified tolerance.
- Governing safe, unsafe, boundary, and out-of-domain cases are tested.
- Unsupported inputs fail closed; capability wording matches executable behavior.
- Focused tests and the narrow benchmark pass while iterating; quick gate and
  normal commit hooks remain the per-commit controls.
- Required hosted PR checks remain mandatory for every packet and are not bypassed.
- Run the broad Python suite, full repository gate, manifest reconciliation,
  and cumulative review once after INDIA-1A through INDIA-1D are integrated.
- Repeat a broad/full local gate earlier only when an outcome-changing failure
  or repository-wide surface makes it necessary.
- Record material issues, confirmed root causes, resolutions, and evidence in
  the newest task-owned `docs/SESSION_LOG.md` entry.

## Git and Review Strategy

Use one PR per coherent packet when packets are independently reviewable; do
not keep all INDIA-1 work on a long-lived mega-branch. A named integration owner
alone updates shared/generated surfaces such as the manifest, capability
registry, `TASKS.md`, indexes, and session log. Read-only engineering review can
run in parallel, but qualified structural-engineering review remains a distinct
acceptance gate.

## INDIA-1 Exit

INDIA-1 is complete only when every original limitation is either supported by
executable evidence or retained as an explicit hold, the generated manifest is
current with no unknown status, focused and repository gates pass, and the
cumulative engineering-review boundary is unchanged. Release remains separately
owner-authorized.
