---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-FOUNDATION-COMBINED-D
---

# INDIA-2-FOUNDATION-COMBINED-D Publication Evidence

## Published boundary

`POST /api/v1/design/combined-footing/symmetric` is a thin typed transport over
the canonical `design_symmetric_combined_footing_is456` service accepted in
COMBINED-C. The nested request forbids unknown fields and non-finite values,
requires actual JSON booleans for every topology and approval boundary, and
admits only the frozen symmetric two-column contract. The router converts the
transport models into the existing domain types, delegates once to the public
service, and performs no engineering arithmetic.

The typed response exposes the complete action and strength disposition:
geometry, service/factored resultants and pressures, longitudinal and
transverse actions, flexure/detailing, one-way shear, concrete-only punching,
bearing/dowels, anchorage, exact provenance, supported and held cases,
qualified-review requirement, and false complete-engineering-approval flag.
A valid in-domain inadequacy remains HTTP 200 with aggregate `FAIL`;
unsupported scope returns the maintained safe HTTP 422 envelope.

## Capability and semantic truth

The canonical capability registry publishes exactly one `combined_footing`
workflow: `design_symmetric_combined_footing_is456`. Its supported case is
exactly two identical square columns with equal concentric axial loads on one
symmetric rigid rectangular constant-depth footing on soil under a caller-
approved uniform-pressure model.

The semantic contract names the nested geometry, actions, materials,
reinforcement, supporting-area/transfer inputs and all evaluated action,
strength, result, review, and approval meanings. `PASS` means that the bounded
bearing, reinforcement/detailing, one-way shear, concrete-only punching,
load-transfer, and equilibrium checks all pass. It does not represent soil
capacity or settlement calculation, complete structural design, construction
approval, or professional approval.

The deterministic Indian-code manifest promotes combined footing from held to
supported only after the A-D implementation, public workflow, route,
capability, semantic contract, exact clauses/sources, benchmark, and tests are
present. Live deterministic truth is 12 supported / 9 held and 80/80 directly
tested endpoints.

## Retained holds

Unequal or eccentric loads, property-line or trapezoidal layouts, flexible or
variable soil pressure, bearing-capacity and settlement calculation, alternate
columns, pedestals, openings, variable depth, shear or punching reinforcement,
coated, bundled, spliced, or curtailed bars, automatic sizing, durability
selection, strap footings, pile caps, raft foundations, React, release,
construction approval, and professional approval remain held.

The bounded software result always requires qualified engineering review and
never grants complete engineering approval. Public distribution permission is
already recorded; no source PDF, scan, page image, watermark, or protected
clause prose is added by this packet.

## Verification boundary

Direct transport tests cover the frozen `PASS` benchmark, strict unknown,
non-finite, non-boolean, and held-scope rejection, safe domain-error mapping,
JSON-safe valid `FAIL`, typed OpenAPI success schema, and main-app mounting.
The focused packet gate also covers all combined A-D tests, public workflow,
capability and semantic contracts, deterministic manifests, exact OpenAPI
drift, architecture/import/link/index checks, source binding, token efficiency,
and the quick gate. Required hosted checks must pass on the unchanged reviewed
head before integration.

All 6 direct D tests, all 84 cumulative combined A-D tests, and the 339-test
focused combined/public-contract selection pass. Black, Ruff, focused mypy,
and Bandit pass. Architecture reports 0 violations across 193 files; import
validation reports 0 broken internal imports across 222 Python files; all 1,250
internal documentation links are valid. The three API contract checks pass,
and independently reviewed OpenAPI drift is limited to one new path, 19 new
combined-footing schemas, one tag, and the matching feature description; no
existing path or schema changed. The deterministic snapshot contains 80
endpoints and 340 schemas. Touched indexes, source binding, token efficiency,
and the quick gate pass before the immutable candidate is audited.

Using the accepted cadence: focused gates run for every packet, with the broad
Python suite and full 30-check repository gate only at the final INDIA-2
integration boundary unless a confirmed repository-wide failure forces them
earlier. The next packet after D integration is a fresh acceptance-only lane;
no strap, pile-cap, or raft work begins in D.
