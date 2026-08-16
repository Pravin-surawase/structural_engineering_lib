---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-FOUNDATION-COMBINED-A
---

# INDIA-2-FOUNDATION-COMBINED-A Analysis Evidence

## Accepted outcome

COMBINED-A implements only the G0-frozen pure IS 456 analysis layer for two
identical square columns carrying equal concentric axial compression on one
symmetric rigid rectangular constant-depth footing. It resolves the approved
uniform-pressure geometry, service bearing carrier, factored net structural
pressure, resultant alignment, whole-width longitudinal shear/moment, and
transverse spread-footing actions.

This packet does not design reinforcement, check strength, publish a service or
FastAPI workflow, or promote combined footing to supported capability truth.

## Implementation identity

- Typed inputs and fail-closed eligibility:
  `Python/structural_lib/codes/is456/combined_footing/models.py`.
- Geometry and action kernel:
  `Python/structural_lib/codes/is456/combined_footing/analysis.py`.
- Package exports:
  `Python/structural_lib/codes/is456/combined_footing/__init__.py`.
- Direct benchmark, boundary, equilibrium, determinism, and clause tests:
  `Python/tests/codes/is456/combined_footing/test_analysis.py`.

Both calculation functions are exact-registered to Clauses 34.1, 34.2.3.1,
and 34.2.4.1. Clause 34.1.2 remains visible as an external settlement/bearing
source boundary, not misregistered as a calculation implemented by this
packet. The runtime provenance also carries `IS456-2000-A5`,
`IS456-AMD6-2024`, and `NPTEL-AFE-C3 Sections 3.7, 3.8, 3.14`.

## Typed eligibility contract

The kernel requires all of the following before analysis:

- one rectangular footing on soil with constant depth, no opening, no
  pedestal, and explicit overall/effective depths;
- exactly two identical square columns centred across the width, symmetric in
  length, with end projections and clear gap large enough for the frozen
  critical-section contract;
- complete non-overlapping `d/2` punching perimeters inside the footing;
- conventional rigid analysis and uniform pressure only, with a caller-
  verified rigidity reference;
- one equal service load and equal factored load for each column;
- explicit uniform service and factored self-weight/overburden carriers whose
  factored/service ratio matches the column-load ratio;
- approved load combination, gross bearing and settlement, pressure
  uniformity, and local distributed-carrier cancellation bases; and
- no moment, horizontal action, uplift, or load reversal.

Non-finite or non-positive numeric inputs, absent references, false approvals,
alternate topology carriers, asymmetric positions, incomplete critical
sections, or inconsistent load factors raise `CombinedFootingContractError`
before any result is returned.

## Frozen benchmark replay

`INDIA-2-COMBINED-HAND-01` reproduces:

| Quantity | Implemented result |
|---|---:|
| Plan area / centroid | `15.0 m2` / `3000 mm` |
| Column spacing / clear gap / end projection | `4000 / 3500 / 750 mm` |
| Punching side / area / perimeter for each column | `1250 mm` / `1.5625 m2` / `5000 mm` |
| Service total / gross pressure / utilization | `2175 kN` / `145 kN/m2` / `0.966666667` |
| Factored carrier / gross / net pressure | `37.5` / `217.5` / `180 kN/m2` |
| Upward whole-width line load | `450 kN/m` |
| Exterior/inner column-face bottom moments | `126.5625 / 14.0625 kN m` |
| Inter-column midpoint top moment | `675.0 kN m` |
| Inner longitudinal one-way shear, each side | `450.0 kN` |
| Outer longitudinal one-way shear, each side | `0.0 kN` |
| Transverse moment / one-way shear per metre | `90.0 kN m/m` / `45.0 kN/m` |
| Right-edge vertical / moment equilibrium residual | `0.0 kN` / `0.0 kN m` |

Three additional symmetric geometries close vertical and moment equilibrium
and reproduce left/right critical-action symmetry. A valid in-domain gross
bearing exceedance returns `gross_service_bearing_within_allowable=False`
rather than being confused with an unsupported input.

## Retained holds

Combined-footing strength, flexure/minimum/provided reinforcement, concrete
shear capacity, punching capacity, bearing/dowels/anchorage, composed
disposition, typed public workflow, REST transport, semantic truth, and
capability promotion remain for COMBINED-B through D. Unequal or eccentric
loads, property-line cases, trapezoidal/irregular plans, variable or tensile
pressure, flexible-soil analysis, settlement or bearing-capacity calculation,
elastic-line, Winkler, plate, FEM, alternate columns, openings, pedestals,
automatic sizing, React, release, and professional approval remain held.

## Focused verification

- 43 direct COMBINED-A tests and a 169-test combined clause, traceability,
  manifest, and function-quality selection pass.
- The strict maintained function-quality gate reports both new calculation
  functions 6/6; Black, Ruff, and mypy pass.
- Generated truth remains deterministic at 11 supported and 10 held families;
  combined footing remains `HELD`/`NOT_IMPLEMENTED` without a public workflow.
- Architecture reports 0/189 violations, imports 0/628 broken, all 1,223
  internal links valid, touched indexes current, token efficiency PASS, and
  the quick repository gate 10/10. Required hosted checks must pass on the
  unchanged reviewed head before integration.

The broad Python suite and full 30-check repository gate remain deferred to
`INDIA-2-CLOSEOUT` under the accepted packet cadence.
