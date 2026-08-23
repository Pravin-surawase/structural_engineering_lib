---
task: INDIA-2-PLAN
title: INDIA-2 Remaining Practical IS 456 Elements Plan
status: archived
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

The bounded straight-flight staircase and five other bounded families are
complete. Pile-cap and raft were separately decided as `HOLD`; INDIA-2 is now
administratively closed without implementing those held systems.

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
| Clause 32 walls | Focused family acceptance complete after A-D integration | One braced empirical vertical-compression wall check supported; alternate wall systems held |
| Clause 33 stairs | One bounded longitudinal straight waist-slab flight supported | Complete; alternate stair systems remain held |
| Clause 29 deep beams | Focused family acceptance complete after G0 and A-D integration | One simply supported positive-moment reinforcement check supported; alternate deep-beam systems held |
| Flat slabs and column punching | Focused family acceptance complete after G0 and A-E integration | One regular interior direct-design and concrete-only punching workflow supported; alternate systems held |
| Combined footing | Focused family acceptance complete | One symmetric equal-load two-column rigid rectangular workflow supported; alternate systems held |
| Strap footing | Focused family acceptance complete after G0 and A-D integration | One property-line two-footing/equal-pressure/no-soil-contact strap model supported; footing slabs remain externally verified prerequisites |
| Pile cap | `HELD / NOT_IMPLEMENTED` after G0 | Missing controlled IS 2911 companion source and accepted structural benchmark; exact reactivation contract retained |
| Raft foundation | `HELD / NOT_IMPLEMENTED` after G0 | Missing controlled IS 2950 source/amendment binding and accepted structural benchmark; exact reactivation contract retained |

There is no progress percentage. A family is either supported within a written
boundary, held with a written reason, or not implemented.

## 4. Recommended execution order

Before resuming the element sequence, complete the separately bounded
GIT-001 Phase 8 reconciliation, frontmatter checker/data repair, and Clause
38.2 truth-hygiene packets defined by the current next-session plan. They repair
cross-cutting execution truth and must not be mixed into a foundation G0.

| Order | Program | Why it is placed here | State |
|---:|---|---|---|
| 1 | `INDIA-2-WALL` | First clause-bounded remaining element; established the new-family workflow | Complete within the written bounded case |
| — | `INDIA-2-STAIR` | Already implemented and cumulatively gated | Complete |
| 2 | `INDIA-2-DEEP` | Extends beam capability under its own geometry, action, and detailing boundary | Complete within the written bounded case |
| 3 | `INDIA-2-FLAT` | Requires panel analysis/distribution plus column punching; broader than the existing solid-slab route | Complete within the written bounded case |
| 4 | Foundation extensions | Each uses a different analysis model and must be activated separately | Combined and strap footing accepted; pile-cap and raft G0 completed as HOLD |
| 5 | `INDIA-2-CLOSEOUT` | Reconcile truth, run final cumulative gates, and freeze the INDIA-2 evidence set | Complete on merge of the unchanged closeout candidate |

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

`INDIA-2-WALL-G0` selected one regular, laterally supported braced wall strip
under caller-supplied factored in-plane vertical compression. The empirical
Clause 32.2 case applies the minimum transverse eccentricity but does not accept
an applied moment or horizontal action. The exact boundary and benchmark are in
[`india-2-wall-g0-scope-evidence.md`](../verification/india-2-wall-g0-scope-evidence.md).

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

1. `INDIA-2-WALL-G0` — integrated GO; bounded case, sources, and benchmark.
2. `INDIA-2-WALL-A` — integrated; types, geometry, effective height,
   slenderness, eccentricity, and empirical axial-capacity contract.
3. `INDIA-2-WALL-B` — integrated; bounded minimum/provided
   reinforcement and spacing checks.
4. `INDIA-2-WALL-C` — integrated; typed public Python workflow and
   frozen end-to-end benchmark example.
5. `INDIA-2-WALL-D` — integrated; thin API, capability truth, and evidence
   freeze.
6. `INDIA-2-WALL-ACCEPTANCE` — complete; focused family acceptance from the
   integrated A-D head is frozen in the verification receipt.

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

`INDIA-2-DEEP-G0` returned GO for one simply supported solid rectangular deep
beam with no openings or hanging action. The caller supplies one governing
positive factored moment and externally verifies bearing/compression-nodal
regions. The bounded software route checks effective span and classification,
Clause 29.2 lever arm, required/provided positive tie steel, placement zone,
continuity, anchorage, and Amendment-3-corrected Clause 32.5 side-face steel.
The exact source interpretation and pre-implementation benchmark are frozen in
[`india-2-deep-g0-scope-evidence.md`](../verification/india-2-deep-g0-scope-evidence.md).

The decision must settle:

- deep-beam classification and effective-span/depth limits;
- whether actions are caller-supplied or generated by a bounded analysis;
- flexure, shear, bearing, anchorage, and web reinforcement scope;
- load/support region assumptions and discontinuity treatment;
- benchmark intermediate values and tolerance.

Initial exclusions are openings, dapped ends, corbels, coupling beams, hollow
sections, prestressing, cyclic/seismic design, generalized strut-and-tie
modelling, nonlinear analysis, and FEM.

Packets G0 and A-D are integrated, and the focused family acceptance from the
integrated D head is frozen in
[`india-2-deep-family-acceptance-evidence.md`](../verification/india-2-deep-family-acceptance-evidence.md).

### 6.4 INDIA-2-FLAT — Flat slab and column-punching program

This is broader than the existing beam/wall-supported solid-slab workflow and
must not reuse its capability claim. `INDIA-2-FLAT-G0` chose one regular
gravity-load panel system and one punching-check boundary before code begins.

`INDIA-2-FLAT-G0` returned GO for one solid square interior panel in a minimum
three-by-three equal-span orthogonal column grid. It uses the direct design
method under identical uniform gravity loading and checks one centred square
interior column for punching without drops, heads, openings, unbalanced moment
transfer, or shear reinforcement.

The decision settled:

- analysis method eligibility and required panel regularity;
- column strip, middle strip, support, drop, and column-head assumptions;
- gravity-load moment distribution and design-strip outputs;
- interior/edge/corner column scope;
- critical punching perimeter, openings, moment transfer, and shear
  reinforcement boundaries;
- flexure, serviceability, detailing, and benchmark tolerances.

The frozen benchmark uses 6000 mm equal spans, a 500 mm square column, 300 mm
slab thickness, 260 mm conservative common effective depth, M30/Fe500,
9 kN/m2 service dead load, 4 kN/m2 service live load, and 19.5 kN/m2 factored
uniform load. It independently fixes total/directional/strip moments, flexural
steel, straight-bar detailing, reviewed span/depth, and punching targets.

Initial exclusions are unequal-sided rectangular panels, irregular grids,
exterior panels and edge/corner columns, drops or heads, transfer slabs,
openings, point/line or patterned loading, moment transfer, punching
reinforcement, equivalent-frame/FEM automation, post-tensioning, progressive
collapse, seismic diaphragm design, and cases outside the selected topology.

Activated packets:

1. G0 scope/source/benchmark decision — complete GO.
2. A panel geometry, eligibility, and strip definitions — integrated.
3. B bounded gravity analysis and moment distribution — integrated.
4. C flexure, serviceability, and detailing checks — integrated.
5. D column-punching checks and fail-closed boundaries — integrated.
6. E typed public workflow, capability truth, and evidence — integrated.
7. Focused family acceptance — complete from the integrated E head; receipt in
   [`india-2-flat-family-acceptance-evidence.md`](../verification/india-2-flat-family-acceptance-evidence.md).

The immutable decision record is
[`india-2-flat-g0-scope-evidence.md`](../verification/india-2-flat-g0-scope-evidence.md).

### 6.5 Separate foundation programs

The following are four separate programs, not one generic “foundation” route:

| Program | G0 analysis decision that must be frozen | Initial exclusions |
|---|---|---|
| `INDIA-2-FOUNDATION-COMBINED` | **G0 GO.** Equal symmetric square columns on one rigid rectangular constant-depth footing under caller-approved uniform pressure | Unequal/eccentric loads, trapezoidal plans, variable/tensile pressure, settlement, elastic-line, Winkler, plate, and FEM |
| `INDIA-2-FOUNDATION-STRAP` | **G0 GO.** Property-line exterior/interior rectangular footings with equal uniform net pressure, a straight prismatic no-soil-contact strap, explicit service/factored actions, and externally verified footing slabs | Automatic footing sizing/strength, strap-soil contact, unequal pressure, flexible-soil interaction, alternate topology/actions |
| `INDIA-2-FOUNDATION-PILE-CAP` | One pile layout, pile-reaction input/model, cap action model, anchorage, and deep-region treatment | General pile groups, lateral piles, soil-pile interaction, dynamic or seismic analysis |
| `INDIA-2-FOUNDATION-RAFT` | One bounded raft idealization, soil-pressure input/model, strip/panel action extraction, and settlement boundary | General plate/FEM soil-structure interaction, irregular rafts, basements, staged construction |

Each program receives its own G0, pure-math packets, benchmark, public workflow,
capability record, and focused family acceptance. Shared material or detailing
helpers do not justify sharing or guessing the analysis model.

`INDIA-2-FOUNDATION-COMBINED-G0` returned GO for exactly two identical square
columns with equal concentric axial loads, symmetric end projections, and one
centred-width rectangular footing. The caller must approve allowable gross
bearing pressure, settlement, rigidity, load combinations, and the uniform
self-weight/overburden carrier. Structural actions use the explicitly approved
net-pressure cancellation model; the library does not calculate soil capacity
or settlement.

The frozen `6000 x 2500 x 850 mm` M30/Fe500 benchmark proves gross service
pressure, resultant equilibrium, full-width longitudinal shear and moment,
transverse cantilever action, flexure/minimum/provided steel, wide-beam shear,
concrete-only punching, bearing, dowels, and anchorage. The immutable decision
record is
[`india-2-foundation-combined-g0-scope-evidence.md`](../verification/india-2-foundation-combined-g0-scope-evidence.md).
It activates COMBINED-A through D followed by focused family acceptance; the
public capability remains held until publication passes.

`INDIA-2-FOUNDATION-COMBINED-A` implements the typed symmetric geometry and
approved-action contract, service gross pressure, factored gross/net pressure,
resultant alignment, full-width longitudinal equilibrium sections, and
transverse flexure/shear actions. The frozen benchmark and additional symmetric
geometries close vertical and moment equilibrium. Evidence is in
[`india-2-foundation-combined-a-analysis-evidence.md`](../verification/india-2-foundation-combined-a-analysis-evidence.md).
`INDIA-2-FOUNDATION-COMBINED-B` implements the exact rectangular stress-block
flexure checks, solid-slab minimum/provided reinforcement, spacing, cover,
tension anchorage, longitudinal/transverse Table 19 one-way shear,
concrete-only punching, and bearing/compression-dowel transfer over A. Valid
inadequacy returns `FAIL`; unsupported input fails closed; review remains
required. Evidence is in
[`india-2-foundation-combined-b-strength-evidence.md`](../verification/india-2-foundation-combined-b-strength-evidence.md).
`INDIA-2-FOUNDATION-COMBINED-C` publishes the sole accepted composition as the
typed `design_symmetric_combined_footing_is456` Python workflow with immutable
input/provenance/result/status types, an executable benchmark, exact caller-
basis and source traceability, and canonical exports. Evidence is in
[`india-2-foundation-combined-c-public-workflow-evidence.md`](../verification/india-2-foundation-combined-c-public-workflow-evidence.md).
`INDIA-2-FOUNDATION-COMBINED-D` adds strict nested transport at
`POST /api/v1/design/combined-footing/symmetric`, exact OpenAPI drift, and the
matching capability/semantic/manifest promotion without changing structural
math. Evidence is in
[`india-2-foundation-combined-d-publication-evidence.md`](../verification/india-2-foundation-combined-d-publication-evidence.md).
Focused family acceptance adds no feature behavior and binds the integrated
G0/A-D source, benchmark, public truth, valid failures, fail-closed boundaries,
and deferred broad-gate decision. Evidence is in
[`india-2-foundation-combined-family-acceptance-evidence.md`](../verification/india-2-foundation-combined-family-acceptance-evidence.md).

`INDIA-2-FOUNDATION-STRAP-G0` returned GO for the property-line model described
in
[`india-2-foundation-strap-g0-scope-evidence.md`](../verification/india-2-foundation-strap-g0-scope-evidence.md).
The strap is an infinitely stiff pure flexural connector with no soil reaction;
the two fixed footing geometries must produce equal uniform net pressure, all
service/factored action pairs must share one multiplier, and clear-strap self-
weight is explicit. The activated A/B/C/D/acceptance sequence covers system
analysis, strap-member strength, typed Python, FastAPI/truth, and focused
acceptance. Both footing slabs and transfer regions remain caller-verified
prerequisites. Evidence is in
[`india-2-foundation-strap-family-acceptance-evidence.md`](../verification/india-2-foundation-strap-family-acceptance-evidence.md).

## 7. Validation and Git cadence

For each implementation packet:

- run focused formula, property, benchmark, unsafe, and out-of-domain tests;
- run relevant architecture and duplication checks;
- run `./run.sh check --quick` before commit;
- require the normal hosted PR checks on the exact head;
- merge only an unchanged reviewed head with required checks green.

Run the expensive broad Python suite and 30-check repository gate once at
`INDIA-2-CLOSEOUT`, after every accepted family is integrated. Family
acceptance uses focused engineering, benchmark, unsafe/out-of-domain,
architecture/import, quick-gate, and hosted-check evidence. Run a broad gate
earlier only when a confirmed repository-wide issue could change the result.

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
- every family has focused acceptance evidence and the final cumulative broad
  gates pass on the exact integrated INDIA-2 tree;
- an INDIA-2 evidence index identifies source, benchmark, PR, test, and
  integrated-tree receipts for every accepted family.

An owner-approved `HOLD` may remove a blocked family from the current delivery
scope, but it cannot be reported as implemented. The plan must then record the
blocker, retained boundary, and reactivation condition before INDIA-2 is
administratively closed.

These criteria are satisfied by the
[final closeout evidence](../verification/india-2-final-closeout-evidence.md):
six bounded families are accepted, both unresolved foundation systems remain
machine-visible holds with reactivation contracts, and the cumulative broad
Python and full repository gates pass without adding behavior.

Qualified structural-engineering review, professional approval, stable release,
package publication, IS 13920, IS 875, IS 1893, response-spectrum analysis, and
FEM remain outside INDIA-2. They belong to INDIA-3, INDIA-4, or separately
authorized programs.

## 9. Closed boundary

Pile-cap and raft G0 completed as `HOLD`. The exact blockers and reactivation
contracts are in the [pile-cap decision evidence](../verification/india-2-foundation-pile-cap-g0-hold-evidence.md)
and [raft decision evidence](../verification/india-2-foundation-raft-g0-hold-evidence.md).
The final closeout packet began from the exact merged raft-HOLD tree and closes
INDIA-2 without calculation changes. Do not use leftover time to begin INDIA-3,
dependency, React, cleanup, release, or professional-approval work; each
requires separate authorization.
