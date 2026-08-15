---
owner: Main Agent
status: active
last_updated: 2026-08-15
doc_type: reference
task: INDIA-2D
---

# INDIA-2D Staircase Public-Workflow Evidence

INDIA-2D publishes one typed Python service and one thin FastAPI transport for
the bounded straight-flight staircase developed in INDIA-2A-C. It does not add
another stair family or change the accepted structural calculations.

## Canonical workflow

`design_straight_flight_staircase_is456(StraightFlightStaircaseInput)` composes:

1. the frozen Clause 33 horizontal geometry;
2. explicit concrete self-weight and caller-supplied superimposed loads, landing
   shares, load basis, and ultimate factor;
3. the equilibrated three-segment simply supported action calculation; and
4. the accepted flexure, supplied-bar, ordinary-shear, and basic L/d checks.

The returned `StraightFlightStaircaseResult` retains geometry, actions, design,
supported and held cases, `PASS`/`REVIEW_REQUIRED`/`FAIL`, load and source
provenance, `qualified_review_required=True`, and
`complete_engineering_design_approved=False`.

The transport is `POST /api/v1/design/staircase/straight-flight`. Its Pydantic
request forbids unknown fields, non-finite values, and alternate scope literals;
its typed response is generated from the same service result. The router
contains no engineering calculation.

## Independent public benchmark

The complete Python and FastAPI route reproduces IIT Kharagpur NPTEL Example
9.1 from the [published lesson](https://archive.nptel.ac.in/content/storage2/courses/105105104/pdf/m9l20.pdf):

| Quantity | Public workflow |
|---|---:|
| Effective horizontal span | 5100.0 mm |
| Maximum factored moment | 68.048997 kNm/m |
| Required main steel | 921.196 mm2/m |
| Provided main steel | 942.478 mm2/m |
| Nominal shear stress | 0.21756 N/mm2 |
| Basic span/depth ratio | 22.7679 |
| Aggregate disposition | `REVIEW_REQUIRED` |

The example is not reported as `PASS` because the unmodified L/d exceeds 20.
A shorter accepted case returns `PASS`; insufficient supplied main steel returns
`FAIL`.

## Capability reconciliation

The machine-readable registry and generated Indian-code manifest now classify
`IS456:2000:stair` as `SUPPORTED` / `IMPLEMENTED_BOUNDED` with exactly one
public workflow. Decorator registration and file existence remain separate
from this capability claim. The completeness checker reports `L2 API Complete`;
React is intentionally absent and therefore no full-stack claim is made.

Retained holds include alternate stair systems, transverse/stringer action,
load generation/combinations/envelopes, continuity, modification factors,
direct deflection, crack width, landing torsion, automatic bar selection,
qualified review, professional approval, and release.

## Focused verification

- 54 focused Python, public-contract, capability/manifest, and FastAPI tests
  passed.
- The singly reinforced capacity-exceedance route serializes a nullable
  unevaluated steel limit and remains a JSON-safe `FAIL` response.
- API signature discovery resolves the typed request and result.
- The API manifest and OpenAPI baseline were regenerated and verify current.
- Indian-code capability manifest generation/check is current with no unknown
  state.
- Architecture, import, typing, quick-gate, commit-hook, and hosted PR evidence
  are recorded by the task closeout.
- Maintained mypy passed 200 source files; architecture reported 0 violations
  across 163 files; import validation reported 0 broken imports across 583
  files; and the quick gate passed 10/10.

The cumulative broad Python and full repository gates run once after this packet
is integrated, following the approved INDIA-2 cadence.
