---
owner: Main Agent
status: active
last_updated: 2026-08-17
doc_type: reference
complexity: advanced
tags: [gravity, workflow, actions, component-api, calculation-book, evidence]
---

# B2 Building Gravity Workflow V1 Evidence

## Evidence boundary

This record covers the bounded B2 orchestration candidate built on the frozen
B1 model and dead/live load ledger. It proves contract binding, exact action
derivation, prerequisite visibility, canonical component routing, calculation
book completeness, and transport parity. It does not prove release readiness,
professional approval, Excel/ETABS integration, or a general whole-building
analysis capability.

## Controlled implementation

| Concern | Controlled implementation |
|---|---|
| Request and result types | `Python/structural_lib/core/gravity_workflow.py` |
| Action derivation and component orchestration | `Python/structural_lib/services/gravity_workflow.py` |
| Review dossier | `Python/structural_lib/services/gravity_calculation_book.py` |
| CLI | `Python/structural_lib/__main__.py` command `gravity-v1` |
| REST | `fastapi_app/routers/building_gravity.py` |
| Review UI | `react_app/src/features/building-gravity/` |

The service module deliberately remains an exact import rather than an eager
`services.__init__` export. This preserves the repository's dependency
direction and avoids importing the beam pipeline while service modules are
still initializing.

## Hand-calculation vector

The B1 6 m x 4 m model and its two combinations produce 22 exact downstream
actions. The directly frozen B2 values are:

| Evidence | Expected value |
|---|---:|
| Service line load on each beam | 20.25 kN/m |
| Service maximum beam moment | 91.125 kNm |
| Service support shear | 60.75 kN |
| ULS line load on each beam | 30.375 kN/m |
| ULS maximum beam moment | 136.6875 kNm |
| ULS support shear | 91.125 kN |
| ULS slab area action | 12.375 kN/m2 |
| ULS axial handoff to each footing | 101.25 kN |

Footing F1's ULS action traces exactly to `footing:DL:F1` and
`footing:LL:F1`. The calculation book reports all 26 ledger reconciliation
boundaries balanced and a maximum absolute residual of 0.0 kN.

## Fail-closed component vectors

- The 6 m x 4 m request with no supplied component bases returns 11 component
  `HOLD` results and an aggregate `HOLD`; no component result is fabricated.
- The slab also records
  `SLAB_COMPONENT_REQUIRES_EFFECTIVE_ASPECT_RATIO_GT_2`, because the declared
  one-way X/Y aspect ratio is 1.5 even though load transfer is valid.
- A 10 m x 4 m request with complete slab, beam, and column bases calls the
  canonical adapters. The four footings remain `HOLD` without an external
  service/soil basis.
- A deliberately shallow 200 mm beam effective depth preserves the beam
  component `FAIL`; the unresolved footing holds keep the overall dossier on
  `HOLD` rather than obscuring either fact.
- Passing the 67.5 kN service and 101.25 kN factored superstructure handoffs as
  supposedly complete footing actions is rejected with
  `FOOTING_EXTERNAL_ACTION_NOT_ADDED`.
- A larger, complete external footing basis reaches
  `design_concentric_isolated_footing_is456`; its bounded test vector returns
  the component's truthful `FAIL` rather than a workflow-created result.

## Transport and review evidence

Python, CLI, REST, and React consume the same `GravityWorkflowRequestV1` and
versioned bundle. The REST definition names every product surface and all four
canonical component adapters. Unknown REST fields are rejected before
calculation. The React review surface labels input blocking, calculation
errors, `PASS`, `FAIL`, and `HOLD` separately, shows the model/load/ledger/result
hashes, and downloads the bound JSON calculation book.

The calculation book includes the accepted input snapshots, ledger,
reconciliation, applicability, actions, component results, issues, exclusions,
limitations, and `QUALIFIED_REVIEW_REQUIRED` disposition. A deterministic
Markdown view is also available from the CLI.

## Verification selection

The frozen candidate uses one impact-mapped verification batch:

- the B1 ledger tests plus B2 Python workflow/CLI tests;
- the focused building-gravity FastAPI route tests;
- the focused React review-page tests and one production frontend build;
- changed-source formatting, lint, type, architecture, import, OpenAPI, and
  documentation checks;
- one quick gate and normal commit hooks; and
- the cumulative broad Python and full repository gates once at B2 closeout.

Unchanged suites are not repeated after ordinary edits. If a check fails, only
the failed or directly affected evidence is repaired and repeated before the
single consolidated gate resumes.

## Remaining gates

This evidence does not authorize Excel or ETABS work, write-back, optimization,
tagging, package publication, or a GitHub release. It also does not replace
qualified structural-engineering review of a specific project and its complete
load, material, detailing, geotechnical, and regulatory basis.
