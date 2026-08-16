---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-FLAT-E
---

# INDIA-2-FLAT-E Publication Evidence

## Published boundary

FLAT-E composes the integrated FLAT-A-D calculations into the sole public
`design_regular_interior_flat_slab_is456` service and exposes the same workflow
through `POST /api/v1/design/flat-slab/regular-interior`. The transport only
converts strict typed models, delegates to the service, and serializes the
result; it contains no engineering arithmetic.

The supported case is one equal-span square interior solid panel in at least
three continuous spans each way, designed by the direct design method under
identical full uniform gravity loading. It uses one centred square column with
no drop, head, opening, offset, moment transfer, or punching reinforcement.
The caller supplies reviewed geometry, material, load, detailing, span/depth,
and support-reaction evidence.

## Public result and provenance

The Python and REST results expose both-direction geometry and direct-design
moments, four reinforcement regions per direction, caller-provided straight-
bar adequacy, no-drop support-top extension, reviewed span/depth status, and
one full-perimeter concrete-only punching disposition. `PASS` requires all
reinforcement/detailing checks, both span/depth comparisons, and the punching
check to pass. A valid inadequate design returns `FAIL`; it is not rejected as
invalid input.

Provenance retains the case and benchmark identity, action-generation and
support-reaction status, geometry/material/load/detailing/serviceability/
punching basis references, applicable Clause 31 and shared slab identifiers,
standard/amendment source IDs, and the public-distribution decision ID.
Qualified review remains required and complete engineering approval remains
false.

## Frozen benchmark and fail-closed proof

The public benchmark reproduces the integrated hand targets, including:

- 5500 mm governing clear span and 442.40625 kN m total static moment in each
  direction;
- 1993.0759957 mm2 required column-strip negative steel;
- 23.076923 actual versus 23.4 reviewed span/depth limit, utilization
  0.986193294;
- 702.0 kN tributary reaction, 690.7368 kN punching shear, and
  0.638212090 concrete-only punching utilization; and
- aggregate `PASS`, qualified-review required true, and approval false.

Unknown fields, non-finite values, non-boolean review flags, unequal or
ineligible topology, openings, moment transfer, reaction mismatch, and missing
evidence fail with HTTP 422. A valid provided-bar inadequacy remains JSON-safe
HTTP 200 with aggregate `FAIL`. OpenAPI binds the success result to a fully
typed nested response schema.

## Capability truth and retained holds

Canonical capability discovery promotes exactly one `flat_slab` workflow:
`design_regular_interior_flat_slab_is456`. The generated Indian-code manifest
therefore records 11 supported and 10 held families. All 79 FastAPI endpoints
have a direct test and actionable cross-layer parity remains 100 percent.

Unequal or rectangular panels, fewer than three continuous spans, exterior
panels, edge/corner or offset columns, drops, heads, marginal beams/walls,
openings, patterned or nonuniform loading, concentrated actions, unbalanced
moment transfer, punching reinforcement, equivalent-frame/FEM analysis,
prestress, seismic/progressive-collapse design, automatic sizing/detailing,
direct deflection, crack width, fire, professional approval, React, release,
and alternate flat-slab systems remain held.

## Verification boundary

The cumulative FLAT-A-E, public workflow, clause/traceability, manifest,
FastAPI, capability, and API-manifest selection passes 207 tests. Black, Ruff,
mypy, and Bandit pass on the changed executable paths. Architecture reports 0
violations across 186 files and imports report 0 broken across 623 Python
files. All 1,211 internal links are valid; all 11 owned/touched folder indexes
are current; all three API documentation/contract checks, schema snapshots,
the 79-endpoint OpenAPI baseline, parity, token efficiency, and the quick gate
pass. Hosted Repository, Python, FastAPI, Documentation, and PR gates must then
pass before integration. The separate flat-slab family-acceptance packet will
run from the integrated FLAT-E head.

The broad Python suite and 30-check repository gate remain deferred to final
INDIA-2 closeout. This packet does not authorize release, professional
approval, or cleanup.
