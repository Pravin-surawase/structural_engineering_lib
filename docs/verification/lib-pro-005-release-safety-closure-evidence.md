---
owner: Main Agent
status: active
last_updated: 2026-08-22
doc_type: reference
complexity: advanced
tags: [safety, validation, websocket, boq, packaging, react, evidence]
---

# LIB-PRO-005 Release-Safety Closure Evidence

**Source base:** `f1a9937cfdba4c72c22e6219ffaf02f94809f1a5`

**Local product verdict:** `PARTIAL`. The reproduced defect families in this
packet are repaired, but static ownership evidence still reports 361 unproven
parameters across the maintained 101-owner inventory. No package publication
or professional-release claim is authorized.

## Corrected runtime outcomes

| Boundary | Corrected outcome |
|---|---|
| WebSocket `design_beam` with `{}` | Returns a sanitized input error; no `design_result` or calculation data. |
| BOQ used grade absent from custom/default rate table | Returns/raises a decisive validation error listing the missing grade; no fallback rate. |
| Mixed-grade story BOQ | Sums each beam's concrete volume at its exact grade rate instead of using an average rate. |
| Equivalent shear with boolean/NaN/infinity | Raises before arithmetic. |
| Development length/bond stress with boolean/non-finite/unknown bar type | Raises at the pure IS 456 detailing boundary before arithmetic. |
| Beam outline with boolean/non-finite/non-positive dimensions | Raises before coordinates are created. |
| Root workflow catalogue imports | The four service-facade symbols are identical through `structural_lib`, `structural_lib.api`, and `structural_lib.services.api`. |
| Streaming `BLOCKED` result | React retains `BLOCKED`; the compatibility workspace remains non-exportable and held. |
| Experimental column PMM | NumPy is declared by the `pmm` extra; a missing extra produces an actionable installation message. |

## Diagnostic result

The maintained input-ownership diagnostic now reports:

| State | Parameters |
|---|---:|
| `PROVEN` | 132 |
| `DELEGATED` | 96 |
| `UNPROVEN` | 361 |
| `NOT_APPLICABLE` | 130 |
| **Total** | **719 across 101 owners** |

Equivalent shear, development length, and beam outline now have explicit
validator/delegation evidence. The development-length service adapter is bound
to its validated pure calculation rather than left as a known false-negative
row. The diagnostic still exits 1 because unresolved ownership remains.

## Conditional audit items

- Performance: no implementation change. The repository documents the
  standalone baseline/comment workflow as parked; FastAPI load tests contain
  executable thresholds and performance benchmarks remain in the full Python
  suite.
- Excel: no CI-wiring change. The path classifier is intentionally selective,
  while the PR gate remains required. The complete 21-test add-in suite is part
  of cumulative local verification.
- Documentation: `sync_numbers.py` identified and updated exactly two active
  counts—89 endpoints across 26 routers in `llms.txt`, and 18 private service
  helpers in the bootstrap guide. Historical release-ledger counts are
  immutable and unchanged.

## Verification through repaired content freeze

- focused Python/FastAPI/manual-comparison selection: 306/306 pass after one
  sanitizer-message expectation correction;
- focused React hook: 17/17 pass; Excel add-in: 21/21 pass;
- complete product gate: Python phase passes, FastAPI 482/482, and React
  277/277;
- exact built wheel: minimal root import passes, missing PMM extra fails with
  the actionable install message, and installation with `[pmm]` imports PMM
  with NumPy 2.4.6;
- public-route safety gate: 20 Python and 4 FastAPI targets pass;
- readiness audit: 22/23 pass with the input-ownership diagnostic as the sole
  expected warning; verdict remains `PARTIAL` with exit 2;
- quick repository gate: 10/10 pass;
- API-classification and task-board contract repairs pass their direct checks;
- diagnostic inventory: 132 proven, 96 delegated, 361 unproven, 130 not
  applicable; expected exit 1.

The first full repository gate correctly found two stale generated/governance
records: the four new root exports were absent from the API-classification
registry, and two completed predecessor rows remained in the WIP-limited Active
table. The registry was regenerated and both completed rows were moved to
Recently Done. The full repository rerun, normal hooks, immutable-candidate
review, and hosted checks remain read-only closeout evidence after this repaired
documentation/index freeze.

## Authority and limits

This evidence proves software behavior for the bounded packet. It does not
prove every public parameter safe, approve a structural design, replace
independent calculations, grant qualified engineering acceptance, or authorize
a package release.
