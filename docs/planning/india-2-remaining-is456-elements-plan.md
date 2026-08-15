---
task: INDIA-2-PLAN
title: INDIA-2 Remaining Practical IS 456 Elements Plan
status: active
owner: Main Agent and repository owner
created: 2026-08-16
last_updated: 2026-08-16
doc_type: spec
---

# INDIA-2 — Remaining Practical IS 456 Elements Plan

## 1. The simple meaning

INDIA-2 finishes a practical, explicitly limited set of IS 456 reinforced
concrete elements that are still missing from the library.

It does **not** mean “implement all of IS 456.” It means:

1. choose one useful and benchmarkable case for each accepted family;
2. implement and test pure calculation logic first;
3. publish only the workflows that actually pass their evidence gates; and
4. keep every alternate or unresolved case visibly unsupported.

The bounded straight-flight staircase is already complete. The remaining work
is walls, deep beams, flat slabs with column punching, and separately approved
combined, strap, raft, and pile-cap foundation programs.

## 2. Authority and truth sources

This document is the single execution plan for INDIA-2. The parent
[Indian-code completion plan](indian-code-completion-plan.md) controls the
INDIA-0 through INDIA-4 wave hierarchy. The generated
[Indian-code capability/coverage manifest](../verification/indian-code-capability-coverage.json)
controls current support and registration truth. [TASKS.md](../TASKS.md)
controls only the active and immediately next packet.

Historical staircase task IDs, PRs, and evidence remain unchanged. The former
`INDIA-2A` through `INDIA-2D` sequence is mapped here as the completed
`INDIA-2-STAIR` family; it is not renamed or rerun.

## 3. Current status

| Family | Current truth | INDIA-2 treatment |
|---|---|---|
| Clause 32 walls | Not implemented | Next decision candidate |
| Clause 33 stairs | One bounded longitudinal straight waist-slab flight supported | Complete; alternate stair systems remain held |
| Clause 29 deep beams | Not implemented | Planned after the wall program |
| Flat slabs and column punching | Not implemented | Planned after deep beams |
| Combined footing | Not implemented | Separate foundation program |
| Strap footing | Not implemented | Separate foundation program |
| Pile cap | Not implemented | Separate foundation program |
| Raft foundation | Not implemented | Separate foundation program |

There is no progress percentage. A family is either supported within a written
boundary, held with a written reason, or not implemented.

## 4. Recommended execution order

| Order | Program | Why it is placed here | State |
|---:|---|---|---|
| 1 | `INDIA-2-WALL` | Next clause-bounded practical element; establishes the new-family workflow | Ready for G0 discussion |
| — | `INDIA-2-STAIR` | Already implemented and cumulatively gated | Complete |
| 2 | `INDIA-2-DEEP` | Extends beam capability but requires its own geometry, action, and detailing boundary | Planned |
| 3 | `INDIA-2-FLAT` | Requires panel analysis/distribution plus column punching; broader than the existing solid-slab route | Planned |
| 4 | Foundation extensions | Each uses a different analysis model and must be activated separately | Planned, order provisional |
| 5 | `INDIA-2-CLOSEOUT` | Reconcile truth, run final cumulative gates, and freeze the INDIA-2 evidence set | Pending |

The provisional foundation order is combined footing, strap footing, pile cap,
then raft. This is a planning recommendation, not activation. The owner may
change that order after each preceding family is integrated and the next G0
evidence is available.

## 5. The packet pattern used for every new family

Every family follows the same control sequence, although the engineering
contents differ.

### G0 — Scope and evidence decision

No calculation code is written. The packet must end in `GO` or `HOLD` and must
record:

- governing standard edition and clause/table identifiers;
- lawful source provenance without copying protected clause prose;
- exactly one supported geometry, material, support, and loading model;
- explicit units and required caller-supplied inputs;
- one independent benchmark and justified tolerance;
- unsafe and out-of-domain cases that must fail closed;
- proposed pure-math, workflow, and publication packets;
- explicit exclusions and capability wording.

A missing source, ambiguous analysis model, or unsuitable benchmark produces a
`HOLD`; it is not guessed around.

### A — Types, geometry, and analysis contract

- Add typed inputs/results with explicit units.
- Define geometry eligibility and action assumptions.
- Implement only pure deterministic math in the IS 456 layer.
- Reject unsupported topology, invalid geometry, and missing required actions.
- Prove the first independently checkable intermediate results.

### B — Strength, serviceability, and detailing checks

- Compose accepted actions into the bounded design/check workflow.
- Preserve formula, limit, table/case, and source provenance in results.
- Test governing safe, unsafe, boundary, and out-of-domain cases.
- Compare final and important intermediate results with the accepted benchmark.
- Return a truthful disposition such as pass, fail, review required, or held.

### C — Public Python workflow

- Publish one typed service workflow only after pure-math acceptance.
- Keep calculation logic out of services and UI/IO layers.
- Provide one executable example with units, assumptions, provenance, and
  limitations.
- Retain backward compatibility without adding duplicate calculation routes.

### D — API, capability truth, and evidence

- Add a thin FastAPI route only when a real consumer needs it.
- Add React only through a separately accepted product scope; it is not an
  automatic requirement for INDIA-2.
- Update the runtime capability registry and generated Indian-code manifest.
- Record benchmark evidence, fail-closed exclusions, tests, and exact Git/PR
  identity.
- Do not advertise adjacent cases that were not accepted in G0.

The G0 decision may change the number or names of A-D packets when the family
cannot be safely split this way. It must preserve the same evidence gates.

## 6. Family-specific plan

### 6.1 INDIA-2-WALL — Clause 32 wall program

`INDIA-2-WALL-G0` must select exactly one practical reinforced-concrete wall
case before code begins. The initial case to investigate is a regular braced
wall strip under caller-supplied axial load and moments, subject to source and
benchmark confirmation.

The G0 decision must settle:

- braced/unbraced and short/slender classification boundaries;
- effective height/length assumptions and who supplies them;
- minimum eccentricity and axial/moment interaction treatment;
- reinforcement faces, minimum steel, spacing, and detailing scope;
- strength and serviceability outputs;
- benchmark source and tolerance.

Initial exclusions are retaining walls, liquid-retaining walls, openings,
irregular or flanged wall sections, global building stability, lateral-load
analysis, seismic/shear-wall provisions, FEM, and IS 13920 detailing.

Provisional packets:

1. `INDIA-2-WALL-G0` — bounded case, sources, benchmark, GO/HOLD.
2. `INDIA-2-WALL-A` — types, classification, geometry, and effective-dimension
   contract.
3. `INDIA-2-WALL-B` — bounded axial/flexural strength and detailing checks.
4. `INDIA-2-WALL-C` — typed public Python workflow and benchmark example.
5. `INDIA-2-WALL-D` — optional thin API, capability truth, and evidence freeze.
6. `INDIA-2-WALL-CUMULATIVE` — family-level full gate after A-D integration.

### 6.2 INDIA-2-STAIR — Clause 33 staircase program

This family is complete. Its accepted case is one cast-in-situ longitudinal
straight waist-slab flight with two collinear landing segments spanning between
outer beam or wall supports. Historical `INDIA-2A` through `INDIA-2D` and
`INDIA-2-CUMULATIVE` are its immutable evidence.

Dog-legged, open-well, turning, bifurcated, spiral, cantilever, transverse,
precast, and stringer-supported stairs remain held. INDIA-2 does not reopen
them unless the owner activates a separate extension after the remaining
families are considered.

### 6.3 INDIA-2-DEEP — Clause 29 deep-beam program

`INDIA-2-DEEP-G0` must choose one deep-beam geometry and loading model. The
initial case to investigate is a simply supported solid rectangular deep beam
with caller-supplied factored actions and no openings, subject to source and
benchmark confirmation.

The decision must settle:

- deep-beam classification and effective-span/depth limits;
- whether actions are caller-supplied or generated by a bounded analysis;
- flexure, shear, bearing, anchorage, and web reinforcement scope;
- load/support region assumptions and discontinuity treatment;
- benchmark intermediate values and tolerance.

Initial exclusions are openings, dapped ends, corbels, coupling beams, hollow
sections, prestressing, cyclic/seismic design, generalized strut-and-tie
modelling, nonlinear analysis, and FEM.

Provisional packets are G0 decision; A geometry/classification/action contract;
B strength and reinforcement checks; C public workflow; D capability/evidence;
then one family cumulative gate.

### 6.4 INDIA-2-FLAT — Flat slab and column-punching program

This is broader than the existing beam/wall-supported solid-slab workflow and
must not reuse its capability claim. `INDIA-2-FLAT-G0` must choose one regular
gravity-load panel system and one punching-check boundary before code begins.

The initial case to investigate is a regular interior rectangular panel without
openings or lateral moment transfer, subject to source, applicability, and
benchmark confirmation.

The decision must settle:

- analysis method eligibility and required panel regularity;
- column strip, middle strip, support, drop, and column-head assumptions;
- gravity-load moment distribution and design-strip outputs;
- interior/edge/corner column scope;
- critical punching perimeter, openings, moment transfer, and shear
  reinforcement boundaries;
- flexure, serviceability, detailing, and benchmark tolerances.

Initial exclusions are irregular grids, transfer slabs, significant openings,
unbounded lateral-load participation, equivalent-frame/FEM automation,
post-tensioning, progressive collapse, seismic diaphragm design, and cases
outside the selected column/panel topology.

Provisional packets:

1. G0 scope/source/benchmark decision.
2. A panel geometry, eligibility, and strip definitions.
3. B bounded gravity analysis and moment distribution.
4. C flexure, serviceability, and detailing checks.
5. D column-punching checks and fail-closed boundaries.
6. E typed public workflow, capability truth, and evidence.
7. One family cumulative gate after integration.

### 6.5 Separate foundation programs

The following are four separate programs, not one generic “foundation” route:

| Program | G0 analysis decision that must be frozen | Initial exclusions |
|---|---|---|
| `INDIA-2-FOUNDATION-COMBINED` | Column/load arrangement, footing shape, soil-pressure model, rigidity, and action generation | More than the accepted column arrangement, biaxial/general soil interaction, settlement/FEM |
| `INDIA-2-FOUNDATION-STRAP` | Two-footing/strap idealization, strap-soil interaction assumption, load path, and member actions | General combined mats, flexible-soil interaction, more than the accepted topology |
| `INDIA-2-FOUNDATION-PILE-CAP` | One pile layout, pile-reaction input/model, cap action model, anchorage, and deep-region treatment | General pile groups, lateral piles, soil-pile interaction, dynamic or seismic analysis |
| `INDIA-2-FOUNDATION-RAFT` | One bounded raft idealization, soil-pressure input/model, strip/panel action extraction, and settlement boundary | General plate/FEM soil-structure interaction, irregular rafts, basements, staged construction |

Each program receives its own G0, pure-math packets, benchmark, public workflow,
capability record, and cumulative gate. Shared material or detailing helpers do
not justify sharing or guessing the analysis model.

## 7. Validation and Git cadence

For each implementation packet:

- run focused formula, property, benchmark, unsafe, and out-of-domain tests;
- run relevant architecture and duplication checks;
- run `./run.sh check --quick` before commit;
- require the normal hosted PR checks on the exact head;
- merge only an unchanged reviewed head with required checks green.

Run the expensive broad Python suite and 30-check repository gate once after a
family's implementation packets are integrated. The final family's broad gate
may also serve as `INDIA-2-CLOSEOUT` when no subsequent code or evidence change
invalidates it. Run a broad gate earlier only when a confirmed repository-wide
issue could change the result.

Use one fresh `codex/<packet>` worktree per activated packet from verified
current `main`. Preserve unrelated lanes. Branch, remote-ref, and worktree
cleanup remain separate owner-authorized actions.

## 8. INDIA-2 completion criteria

The successful target is:

- the accepted bounded wall, deep-beam, flat-slab/punching, and separately
  activated foundation programs are implemented and independently benchmarked;
- the existing staircase family remains supported without scope inflation;
- every advertised workflow has explicit units, assumptions, provenance,
  unsafe cases, and machine-visible exclusions;
- every unimplemented or out-of-domain case is `HELD` or `NOT_IMPLEMENTED`,
  with no contradictory or unknown status;
- public Python/API behavior and generated capability truth agree;
- family and final cumulative gates pass on exact integrated trees;
- an INDIA-2 evidence index identifies source, benchmark, PR, test, and
  integrated-tree receipts for every accepted family.

An owner-approved `HOLD` may remove a blocked family from the current delivery
scope, but it cannot be reported as implemented. The plan must then record the
blocker, retained boundary, and reactivation condition before INDIA-2 is
administratively closed.

Qualified structural-engineering review, professional approval, stable release,
package publication, IS 13920, IS 875, IS 1893, response-spectrum analysis, and
FEM remain outside INDIA-2. They belong to INDIA-3, INDIA-4, or separately
authorized programs.

## 9. Exact next action

Start with `INDIA-2-WALL-G0` as a decision-only packet. Its deliverable is one
short GO/HOLD record that freezes the wall case, controlled source set,
independent benchmark, units, assumptions, outputs, exclusions, downstream
packet split, and acceptance commands.

Do not write wall calculation code until that decision is reviewed and the
owner activates the downstream packets.
