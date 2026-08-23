---
owner: Main Agent
status: active
last_updated: 2026-08-24
doc_type: guide
complexity: intermediate
tags: [parity, etabs, react, excel, gravity]
---

# Cross-Surface Parity V1

## Boundary

LIB-PRO-007-P6 proves that maintained transports carry the same canonical
calculation request and result; it does not give any transport calculation
authority. Python remains the calculation authority. FastAPI delegates, React
retains revision-bound evidence, and Excel transports reviewed selected-table
rows through the local REST service.

P6 performs no live ETABS operation. It does not open or parse EDB files,
unlock a model, run or change analysis, modify model data, save, or write back.
The trial-compatible exported-file boundary from P5 remains unchanged.

## Frozen datasets

| Dataset | Identity | P6 use | Disclosure boundary |
|---|---|---|---|
| P5 synthetic ETABS exported-file fixture | Snapshot `a82d927d347108f56aa3fcdd559c1aa45ba8d87673cb3feec61a03d5eadbf4f8`; members `101` and `102` | Deterministic Python, REST, React, and Excel beam parity | Public synthetic data; no real model or protected source content |
| Maintained open-hall gravity example | `get_gravity_workflow_example_request_v1()` | Python/REST/React workflow-result hash, governing `HOLD`, and issue parity | Maintained demonstration; not a real project design basis |
| Optional real trial export | One P5-accepted private snapshot | Additional read-only acquisition evidence only | Review project/confidential identifiers before any Git inclusion; retain hashes privately when disclosure is not approved |

The synthetic fixture is the repeatable software acceptance dataset. A real
trial export can supplement it, but P6 does not wait for trial API access and
does not publish project data by default. Manual E2K and selected-table export
from a locked model remains valid.

## Parity matrix

| Surface | Frozen entry | Required equality | Freshness owner |
|---|---|---|---|
| Python | `build_etabs_canonical_snapshot_v1` then `design_project_beams_v1` | Canonical member ID, normalized input hash, result identity, status, and issues | Caller supplies the current accepted snapshot |
| REST | `POST /api/v1/import/project-beams` | Exact canonical request payload and the Python result identity/status/issues | Stateless; clients must retain source identity |
| React | `buildProjectBeamBatchRequest`, canonical batch stream, and `WorkspaceSnapshotV1` | No transport-side depth arithmetic; result envelope must match evidence identity before becoming current | Project/member/input revision plus complete imported source metadata |
| Excel | Routine Workbench V1 selected table | Calculation-bearing cells produce the same input hash and result identity; an evidence-only `Source Snapshot SHA-256` column is excluded from calculation but retained in source-table freshness | Source-table, mapping, and engine hashes |
| Gravity review | Maintained example through Python, REST, and React | Workflow-result hash, governing status, and canonical issues | Request/result hash; Excel is not a full gravity-workflow surface |

Excel participates in the canonical rectangular-beam slice. It does not become
a Building Gravity V1 calculator, and no structural formula is added to
Office.js. The full gravity review dossier remains a Python/REST/React surface.

## Root parity repair

P5 requests use either an explicit effective depth or a complete
cover/stirrup/tension-bar basis. Before P6, the strict project batch resolved a
derived depth to a number and then called the canonical beam service as though
that number had been supplied explicitly. For the P5 fixture this changed the
compression-steel depth basis from `D - d = 58 mm` to the historical explicit
depth default of `50 mm`. Excel preserved the original basis, so its normalized
input and result identity differed.

P6 passes the original basis to `design_beam_is456` and uses the same resolved
compression-depth value in the project evidence identity. This repairs the
calculation path, rather than normalizing two different outcomes after the
fact.

## Freshness and export rules

- React hashes the complete imported source metadata, including the P5
  snapshot hash. A source-only identity change advances the revision, marks
  retained results stale, and makes current export ineligible.
- React accepts a current result only when the canonical result envelope and
  evidence agree on contract version, normalized input hash, calculation
  identity, library version, and governing status.
- Excel may carry `Source Snapshot SHA-256` as an evidence-only selected-table
  column. It is not a calculation input, but it is covered by the source-table
  hash. Changing only that value returns `STALE` and blocks the current review
  bundle until recalculation.
- REST is stateless. It preserves source metadata in the evidence response but
  cannot declare a retained client result current.
- `PASS`, `FAIL`, `HOLD`, and source freshness remain separate from qualified
  review, release approval, and professional approval.

## P6 non-goals

- live ETABS API or UI automation;
- EDB parsing, analysis control, unlock, save, or write-back;
- structural formulas in React, Office.js, or FastAPI;
- a new Excel gravity-workflow implementation;
- P7 compatibility migration or deletion;
- INDIA-3 formulas or source promotion;
- release, package publication, or professional approval.
