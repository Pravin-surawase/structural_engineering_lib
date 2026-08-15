# Next Session Briefing

## Latest Handoff

<!-- HANDOFF:START -->
- Date: 2026-08-15
- Focus: Complete INDIA-2B geometry/actions and launch INDIA-2C design from its integrated merge
- Current branch: `codex/india-2b-staircase-actions`
- Base: verified integrated `origin/main` at `1cd08b9cab20a34b9dad1806f500eef01a2f4739`
- Next action: merge the unchanged INDIA-2B packet after required checks pass, then create a fresh `codex/india-2c-staircase-design` worktree from integrated `main`
- Holds: structural design and capability promotion wait for later packets; alternate stairs, other held families, IS 875/IS 1893 generation, React, stable/engineering-use approval, release, and cleanup remain out of scope
<!-- HANDOFF:END -->

**Date:** 2026-08-15

| Release state | Target |
|---|---|
| **Current** | `v0.23.1a1` Alpha; INDIA-1 software and cumulative gates complete |
| **Next** | INDIA-2C structural design after INDIA-2B integration; qualified review remains separate |

## Required Reading

1. [Generated Indian-code manifest](../verification/indian-code-capability-coverage.json)
2. [INDIA-1 cumulative evidence](../verification/india-1-cumulative-gate-evidence.md)
3. [Current task board](../TASKS.md)
4. [IS 456 library-first plan](is456-library-first-master-plan.md)
5. [Canonical Git workflow](../git-automation/git-workflow-single-source.md)

## Start Boundary

INDIA-1A through INDIA-1D and their cumulative software gates are integrated.
They do not provide qualified engineering approval. INDIA-2 starts a separate
new-family program and must not reopen INDIA-1 or combine multiple held systems
into one implementation wave.

```bash
./run.sh session brief --agent structural-math
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
./scripts/python_runtime.sh scripts/generate_indian_code_manifest.py --check
```

Require a clean fresh branch from verified current `origin/main` and
`source_bound=true`. Preserve the dirty primary checkout and every unrelated
worktree.

## Why INDIA-2 Begins With a Decision Packet

The generated manifest holds eight unimplemented IS 456 families: wall, stair,
deep beam, flat slab, combined footing, strap footing, raft foundation, and
pile cap. None has a frozen supported case or accepted benchmark program.
IS 875 and IS 1893 also remain held with editions and analysis boundaries not
selected, so they are not INDIA-2 implementation candidates.

Do not treat those holds as one backlog to code in parallel. INDIA-2 selects
one coherent family, proves that it has a bounded useful route, and leaves all
other families explicitly held.

## INDIA-2A — Scope and Evidence Foundation

**Objective:** produce a GO/NO-GO decision for exactly one new IS 456 family
before adding calculation code.

The initial recommendation is a bounded straight-flight staircase because its
RC design can potentially reuse maintained slab/beam patterns. INDIA-2A must
verify that assumption against sources and benchmarks; recommendation is not
implementation evidence.

### Required decisions

- Confirm the selected family is owner-activated despite its historical
  post-v1.0 roadmap position; INDIA-2A planning alone does not activate B-D.
- Select one governing edition and source set with clause/table provenance.
- Freeze one useful geometry, support, span, load-action, material, and
  reinforcement model with explicit units.
- Separate caller-supplied actions from any self-weight calculation; do not
  imply IS 875 load generation.
- Define result dispositions and fail-closed exclusions before public naming.
- Map reusable accepted functions versus genuinely new pure math.
- Define independent safe, unsafe, boundary, and out-of-domain benchmarks with
  justified tolerances.
- Record GO, REVISE, or NO-GO and update the task board. Do not change the
  capability manifest from `HELD` until executable evidence exists.

### Candidate boundaries to compare

| Candidate | Minimum decision needed before implementation |
|---|---|
| Straight-flight stair | support/span model, flight/landing scope, load projection, serviceability, detailing |
| RC wall | axial-flexure model, slenderness, reinforcement layout, openings, frame-analysis boundary |
| Combined footing | column actions, contact-pressure model, rigidity assumption, soil/geotechnical boundary |
| Flat slab | column/drop strips, punching perimeters, openings, moment transfer, analysis method |
| Deep beam | load path, nodal zones, reinforcement model, ordinary-beam transition |

Strap, raft, pile-cap, IS 875, and IS 1893 work remains held unless a later
owner-approved program replaces this order.

## Provisional Staircase Packets After INDIA-2A GO

### INDIA-2B — Types, geometry, and action contract

- Add explicit types for the accepted straight-flight case only.
- Implement and benchmark geometry and action transformation as pure math.
- Reject unsupported support, landing, transverse, cantilever, helical,
  folded, precast, and stringer/rib cases.

### INDIA-2C — Structural design and checks

- Compose accepted flexure, shear, detailing, and serviceability logic without
  bypassing the four-layer architecture.
- Add provenance-bearing independent benchmarks and fail-closed outcomes.

### INDIA-2D — Public workflow and capability truth

- Publish one typed Python service/facade route after pure-math acceptance.
- Add a thin FastAPI consumer only if it preserves the exact supported case.
- Update capability truth, API manifests, docs, and evidence as a single-writer
  closeout. React/UI expansion is outside INDIA-2 unless separately approved.

If INDIA-2A selects another family, replace B-D with equivalently bounded
packets before implementation; do not reuse staircase-specific acceptance rows.

## Gate Cadence

For every packet, run focused tests, independent benchmarks, architecture and
import checks, `./run.sh check --quick`, normal commit hooks, and every required
hosted PR check. After INDIA-2A through the activated final packet are
integrated, run the broad Python suite, `./run.sh check` (currently 30 checks),
manifest reconciliation, provenance review, and cumulative essential review
once. Run a broad gate earlier only for an outcome-changing failure or a
repository-wide surface. Never bypass required hosted checks.

## INDIA-2 Exit

INDIA-2 is complete only when one newly approved family is either supported by
executable, independently benchmarked, provenance-bearing evidence or returned
to an explicit hold; all other families remain truthful holds; manifests have
no unknown status; cumulative software gates pass; and qualified engineering
review and release authorization remain separate.
