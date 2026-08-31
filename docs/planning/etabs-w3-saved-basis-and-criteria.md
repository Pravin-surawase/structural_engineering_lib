---
owner: Main Agent
status: active
last_updated: 2026-08-31
doc_type: reference
complexity: advanced
tags: [etabs, w3, evidence, serviceability, planning]
---

# W3 saved physical basis and audit criteria

## Decision

The saved text source now has a bounded, reproducible crosswalk to all 225
accepted frame objects. It is useful input evidence, but none of the three
preselected beam lines is ready for independent calibration. Stop broad table
diagnosis here. Complete the audit's typed basis/serviceability route next;
acquire further building data only against the residual matrix below.

This follows the [whole-W3 reset](etabs-data-analysis-optimization-foundation-plan.md#whole-w3-execution-reset-2026-08-31)
from accepted PR #934, merge `f5e425ced924546d1f67d07f17841d0b83bfb68c`.
The [safe receipt](../verification/etabs-w3-saved-basis-evidence.json) binds the
external operator, checks and proprietary results. No application or solver
ran. This research operator is not a public importer or accepted W3F snapshot.

## Reconciliation actually completed

| Source question | Result | Limit |
|---|---|---|
| Saved evidence integrity | Seven selected files match two accepted manifests; all five typed canonical snapshots verify | Historical saved evidence, not fresh application state |
| Frame identity and section | All 225 label/story assignments join; dimensions and material labels match exactly; 170 template/story point identities join | Object connectivity is not generated analysis-mesh connectivity |
| Coordinates and stories | Explicit base elevation and six story heights expanded; maximum printed-coordinate difference is below 0.001 mm | Exact differences retained; no fitted tolerance or complete revision equality asserted |
| Load patterns and selected combination | Nine pattern self-weight values match; all five selected linear-static case load lists and ordered combination factors match | Text `PRESET` initial-condition semantics remain unproved; accepted API zero-state evidence remains the authority |
| Direct and shell loading | 151 explicit frame records in DEAD; 112 shell records split equally between DEAD and LIVE; 56 assigned areas | Zero records in a pattern do not prove zero generated/transferred load or justify dropping any of the five cases |
| Release evidence | 109 beam records say PINNED, 22 explicitly release the two J-end bending moments, 22 omit RELEASE | Omission is not a verified fixed end; two saved readback scopes remain bounded |
| Slab context | Six assigned areas use membrane behavior and 50 use thin shells | Same-story context is not a tributary-area or stiffness-influence map |
| Previously typed frame overlap | Explicit J-end release token, insertion cardinal point and direct-load intensity match the saved one-frame readback | Its automatic offsets/modifiers cannot be inferred from their omission in the text |
| Combination design purpose | Text explicitly marks the selected combination Concrete/Strength | Source metadata is not project criteria, engineer approval or a complete design envelope |

The operator retains exact record locations and source tokens. It rejects
duplicate identities, malformed attribute pairs and unsupported load forms.
An independent literal-record cross-check verifies the 225 assignment joins,
load counts and selected factors. Ten synthetic checks cover the actual token,
story and omission hazards; full saved-output replay verifies determinism.

## Three candidates, chosen before force comparison

Population: the 77 previously saved geometric simple chains within the existing
one-to-five-span bound. Selection was frozen before new assessment: the previously
inspected shortest line, shortest other line, and longest other line, with stable
line identity breaking ties. No results were fitted and no solver was run.
Exact identities, lengths, assignments and matrices remain external.

| Candidate | Evidence gained | Physical decision |
|---|---|---|
| A: previously inspected single span | Explicit pinned token and direct load; saved releases/offsets/restraints/displacements; two endpoints coincide with other beam interiors | Known moving supports plus incomplete transferred loading: NOT_COMPARABLE_AS_IS |
| B: shortest other single span | Explicit pinned token/direct load, two endpoint-to-interior geometric contacts, mixed membrane/thin-shell story context | Required support/mesh/transfer basis unproved: NOT_COMPARABLE_AS_IS |
| C: longest three-span chain | Explicit pinned tokens/direct loads, four externally connected object joints, mixed slab context | Required support/mesh/transfer basis unproved: NOT_COMPARABLE_AS_IS |

These are eligibility decisions for the current evidence and solver, not
structural failures or proof that every building member is unsuitable. A/B
geometric contacts do not establish generated connectivity; C's object joints
do not establish effective support stiffness. A pinned member end does not
mean that its supporting building joint has zero displacement.

CSI distinguishes membrane load transfer from shell bending participation;
therefore a generic tributary-width load cannot replace this missing basis.
[CSI membrane versus shell guidance](https://web.wiki.csiamerica.com/wiki/spaces/etabs/pages/1476978/Membrane%2Bvs.%2Bshell%2Bslab),
[CSI floor mesh options](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Shell/Floor_Auto_Mesh_Options.htm).
Release locations also depend on end offsets.
[CSI release guidance](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/Frame_Releases_and_Partial_Fixity.htm).

## Two newly exposed audit-basis hazards

The source distinguishes longitudinal and confinement steel grades. The current
`IS456MaterialsV1` contract has one `fy_nmm2`; it cannot preserve that distinction.
This is a representation gap, not evidence that an accepted calculation is wrong.
Trace the separate consumers and any code limits before changing the calculation.
Do not replace the already supplied pilot defaults or relabel them as installed steel.

The beam source's top/bottom cover belongs to ETABS's longitudinal-rebar-centroid
basis. Our detailing contract requests clear cover. Equal numeric values do not
make these fields interchangeable. Preserve both bases and require the actual
bar/layer arrangement for conversion; do not silently subtract assumed diameters.
The zero beam reinforcement overwrites are not proof of zero installed steel.
[CSI reinforcement data definitions](https://docs.csiamerica.com/help-files/etabs/Menus/Define/Section_Properties/Frame_Sections/Frame_Section_Property_Reinforcement_Data_Form.htm).

## Executable serviceability and screening gap matrix

| Requirement | Existing owner / reusable work | Missing contract or decision |
|---|---|---|
| Canonical serviceability input | `services/contracts/beam.py`: dictionary placeholder is deliberately rejected; `services/canonical_beam.py` passes no service parameters | Strict discriminated check requests with units, provenance, required/optional status and fail-closed applicability; preserve existing v1 compatibility |
| Audit routing and verdict | `services/beam_audit.py`: string evidence basis; required checks block | Bind a typed service request/result to the member, scenario, section, reinforcement revision and source digest; required missing/unsupported checks cannot become PASS |
| Deemed span/depth check | `codes/is456/beam/serviceability.py::check_deflection_span_depth` | Effective-span basis, actual support classification, effective depth and explicit modification factors with source; defaults of 1 are not accepted project evidence |
| Calculated deflection | Same module, levels B/C | Service scenarios, sustained/live split, reinforcement areas, loading/support applicability, duration or age/humidity/shrinkage inputs, total versus post-finish limits and construction basis |
| Deflection-method validity | Existing B/C functions use simplified support/load coefficients; their comments limit irregular/multispan applicability | Independently review maintained equations and intended method against authorized sources before exposing them; no generic PASS on an arbitrary building line |
| Flexural crack check | `check_crack_width` | Exposure/limit, cover to nearest bar, section depth, neutral axis, crack-distance geometry and mean strain or justified service stress/steel modulus; no automatic exposure or installed-bar assumptions |
| Signed service actions | Accepted W3 same-row demand/scenario machinery | Service selection/factors, member/station/face mapping and sustained load basis; never divide one factored governing row to invent all service scenarios |
| Strength applicability | `BeamAuditApplicabilityBasisV1` | Independent P/V3/M2 limits, positive/negative M3 tension faces and factored-action basis; observed maxima cannot set acceptance limits |
| Reinforcement and constructability | Existing detailing/BBS/check owners; pilot preferences already supplied | Separate proposed/required/installed steel, longitudinal/transverse grades, clear/centroid cover, layer fit, spacing, anchorage/laps and support widths as applicable |
| Screening scope | W3R feasibility repair exists; W3I service functions absent | Finite section/bar families, every mandatory scenario/check, approved bounds, cost/objective units and provenance, deterministic ranking/ties, no held candidate retained |
| Candidate-range validity | W3H comparator exists; building L5 held | Baseline agreement alone cannot qualify section/stiffness changes; define calibration domain and whole-model safeguards before enabling I/K |

This is a software/source inventory, not certification of every existing
serviceability formula. Strongly typed plumbing alone does not validate an
engineering method. Missing project choices remain explicit; do not ask for
model facts that are recoverable from saved evidence or repeat the pilot inputs.

## Next packet and residual acquisition decision

**Next offline packet: W3E basis and serviceability.** Freeze the compatibility
and source-provenance contracts, first resolving cover/steel-basis mapping and
tracing existing calculation consumers. Implement only source-verified,
explicitly applicable service methods with independent reference cases and
same-row/face binding. If a requested method or project basis is unavailable,
return a precise hold and preserve the existing strength route. The exit is an
executable typed route for its declared scope, not a real-building PASS.

For H, do not acquire more merely to complete an inventory:

| Residual field | Cheapest admissible route | Stop condition |
|---|---|---|
| Specific member release/offset/modifier or support assignment | Existing accepted typed getters, only for the finally selected scope | Cannot infer effective surrounding stiffness from a restraint flag |
| Generated nodes/elements, object-to-element and station-side identity | Documented output/table schema; then bounded saved export or integrated client if needed | No row access until exact schema, units, scope and revision can answer the mapping |
| Slab influence and effective loads for all five cases, self-weight and coupling | Explicit input/mesh/stiffness model or independently justified reduced-load derivation | Direct assignments, same-story areas or ETABS force-fitting cannot supply independent transfer proof |
| Zero/nonzero support motion and shear/slab physics | Existing evidence first; a justified physical reduction or separate solver extension | More getters alone cannot add unsupported solver degrees of freedom |
| Comparison tolerances and applicability | Project engineering decision, frozen independently of the candidate results | No defaults or thresholds chosen from the observed mismatch |

The preferred near-term delivery is complete ETABS-sourced beam audit/review.
An ETABS-first candidate programme would avoid rebuilding global physics but
requires an explicitly revised candidate/reanalysis contract and separately
authorized copy mutations, analysis, safeguards and recovery. A surrogate
extension preserves independent prediction but adds support-motion, load-transfer,
coupling and new benchmark/calibration work; a settlement-only patch is insufficient.
Neither route is activated here, and neither clears W3H/I/K/L.

Do not issue a new numerical delivery estimate until that route and its required
physical scope are chosen. Final combined gates and Mac review remain due after
integration; professional attestation and release authority remain separate.
