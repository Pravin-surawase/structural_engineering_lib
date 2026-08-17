---
owner: Main Agent
status: active
last_updated: 2026-08-17
doc_type: reference
complexity: advanced
tags: [a2, lossless-import, load-analysis, etabs, smart-analysis, evidence]
---

# A2 Lossless Intake and Calculation Evidence

**Evidence boundary:** Packet A2 implementation and focused local verification.
This record does not authorize gravity orchestration, live ETABS, Excel
write-back, optimization, a release, or professional approval. Cumulative broad
and hosted results are bound during immutable M2/G1 closeout.

## Authorization and source

- The owner approved G0, directed A1, then directed A2 without ordinary approval
  pauses.
- Branch: `codex/a2-lossless-intake-calculation`.
- Base before the candidate commit: A1 merge
  `a0458e1935e9f14bcba47a838d5fe61b46174b05`.
- The isolated runtime reported `source_bound=true`.

## Root-cause closure

### F3 — lossless intake and source accounting

- `POST /geometry/building` now accepts a non-empty typed member list. Every
  identity, point, section, filter, and coordinate scale is validated before the
  route runs; duplicate identity and an all-excluding filter block. The React
  hook consumes the same request/response shape.
- The response receipts `visualization_only`, source-coordinate basis,
  millimetre scale, input/output counts, and filtered count. It is not a gravity
  or analysis-model intake.
- Strict imports ledger every physical row and calculation field. Header-only,
  malformed/non-finite, missing case/station/section, duplicate, unmatched, and
  unknown-section inputs expose no calculable batch.
- ETABS raw station envelopes retain signed moment/shear extrema, their stations,
  and concurrent companion values. A source-precomputed envelope carries the
  explicit `source_precomputed_extrema_provenance_unavailable` basis.
- Section dimensions come from a source name or explicit map; no unknown ETABS
  section silently becomes `300 x 500 mm`.

### F4 — load mathematics, basis, and applicability

- Combined-load inputs are finite; magnitudes are positive; locations and UDL
  bounds lie inside the span; and display density is an integer of at least two.
- Point/moment discontinuities and zero-shear roots are inserted into the plot
  grid, so off-grid engineering extrema are exact and independent of requested
  display density.
- Zero is preserved as an applied-moment location. Partial UDL bounds are
  calculated in Python and REST rather than retained and ignored.
- Exact vectors cover UDL, point, mirrored location, magnitude scaling, support
  moment, and partial UDL behavior. Unsupported triangular/moment cantilever
  combinations block explicitly.
- Global dead/live generation, combinations, transfers, self-weight ownership,
  and footing external service/soil bases remain held for the gated gravity
  workflow; A2 does not invent them.

### F5 — smart calculation/advice semantics

- REST requires explicit overall/effective depth and span; it no longer derives
  `d = D - 50` or `span = 12D`.
- Utilization remains demand/capacity. Remaining-capacity margin is
  `max(0, 1 - utilization)`, so lower utilization is safer.
- Flexure/shear checks and clause identities come from the canonical beam
  pipeline. Failed canonical designs remain engineering `FAIL` under HTTP 200
  transport success, even when the caller hides the check list.
- The route returns core score names and core cost analysis. It no longer labels
  capacity margin as steel efficiency, cost efficiency as concrete efficiency,
  or invents a zero steel estimate. Text rendering alone converts normalized
  `0..1` scores to `/100`.

## Focused verification

The frozen selection covered adverse import ledgers, ETABS adapter/integration
fixtures, exact and metamorphic load vectors, core/result/model serialization,
smart PASS/FAIL semantics, typed FastAPI responses, the building React contract,
OpenAPI, and architecture/import checks.

- The initial Python/FastAPI selection collected all related failures in one
  run. Five contract assertions rejected the candidate; all other collected
  checks passed.
- Impact-mapped repair proved the two plot-grid assertions, additive
  `BeamForces` schema, and all eight semantic-contract checks.
- The React live contract passed `1/1`; production TypeScript/Vite build and
  full React lint passed.
- Changed-file Ruff passed. Architecture passed with 209 files and zero
  violations. Import validation passed with 668 files, 4,585 imports, and zero
  broken imports.
- The six building-route impact tests passed after the service-facade repair.
- OpenAPI matches the refreshed baseline: 82 endpoints and 368 schemas.
- The first cumulative Python run exposed eight stale public depth-error
  assertions and three non-reproducing audit-readiness failures. The central
  effective-depth validator now preserves the field-specific finite and
  overall-depth messages; all eight failed cases, 46 canonical transport/batch
  cases, and changed-file Ruff pass. The audit-readiness cases passed unchanged
  in their isolated failed-only selection.
- The first full repository gate passed 28/31 checks. Its three closeout
  rejections were generated ETABS manifest/schema truth and the active-document
  hard limit, not calculation failures. The maintained generators now carry the
  additive fields. Four already archived/deprecated documents were safely moved
  to `_archive`, leaving 400 active markdown files and zero broken links.
- The first normal commit-hook attempt retained its deterministic Black/EOF
  edits and exposed two static-contract gaps. Explicit `default=None` provenance
  fields now pass the configured 236-file mypy check; three legacy adapter
  silent skips now emit identity/reason warnings; the engineering `PASS` enum is
  narrowly marked as a Bandit credential false positive. Changed-file Bandit
  and 55 affected model/adapter tests pass.

The cumulative broad Python suite, full repository gate, quick gate, normal
commit hooks, immutable exact-head audit, push, and hosted validation occur in
the M2/G1 candidate closeout. A material change to calculation or transport
behavior invalidates the affected evidence above.

## Holds at G1 candidate boundary

- `/geometry/building` remains visualization-only.
- ETABS support remains read-only CSV/file intake; live process state, local
  axes/units, model completeness, analysis validity, and combination approval
  are not established.
- Footing design remains conditional on an approved external service action and
  allowable soil basis.
- Gravity Workflow V1, Excel, live ETABS, write-back/nightly optimization,
  release, qualified review, and professional approval remain separate gates.

## Efficiency receipt through content freeze

| Receipt | Actual |
|---|---:|
| Unchanged-suite reruns | 0 |
| Frozen focused verification batches | 1 |
| Impact-mapped repair/replan batches | 5 |
| React dependency installs in this lane | 1 pinned lockfile install |
| Quick gates | 0 |
| Broad Python suites | 1 (rejected candidate; 11 collected failures) |
| Full repository gates | 1 (28/31; one bounded repair batch) |
| Hosted validation runs | 0 |
