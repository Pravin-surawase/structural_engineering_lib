---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-DEEP-ACCEPTANCE
---

# INDIA-2-DEEP Focused Family Acceptance Evidence

## Acceptance decision

**ACCEPT** the implemented deep-beam family within its written boundary. The
exact integrated G0/A-D starting head was
`ce45e22032ea234f588ce88c601db5f6a42af166`. The supported public route remains
one simply supported, single-span, solid rectangular, top-loaded Clause 29 deep
beam without openings, dapped ends, or hanging action, under one caller-supplied
positive factored moment.

This receipt adds no calculation or product scope. Bearing/compression-nodal
verification remains an external caller prerequisite. Continuous or cantilever
members, negative moment, openings, dapped ends, corbels, coupling beams,
irregular or prestressed members, hanging action, load/reaction generation,
automatic sizing, bundles, splices, transverse-enclosure design, serviceability,
fire, seismic/IS 13920, generalized strut-and-tie, nonlinear analysis, and FEM
remain held. Qualified engineering review remains mandatory and complete
engineering approval remains false.

## Public clause and source evidence

The Python and REST results expose IS 456:2000 Clauses 29, 29.1, 29.2, 29.3,
29.3.1, 29.3.4, 26.2.1, 26.2.1.1, and 32.5-32.5.2; the Amendment No. 3
side-face correction; normalized source IDs; explicit mm, kN m, and N/mm2 units;
the accepted case; held cases; and benchmark `INDIA-2-DEEP-HAND-01`.
Approved-scope identifiers, formulas, limits, and provenance are public
repository content. Controlled source PDFs, page images, and copied clause
prose are not repository artifacts.

## Independent benchmark replay

The frozen benchmark was recomputed independently of the deep-beam kernel and
compared with the public workflow. Effective span `3000 mm`, lever arm
`1400 mm`, required/provided tie steel
`1477.832512315271 / 1520.530844337460 mm2`, permitted tie-zone depth `350 mm`,
required embedment `797.5 mm`, vertical side-face steel
`360 / 523.598775598299 mm2/m`, and horizontal side-face steel
`600 / 628.318530717959 mm2/m` match within the frozen `1e-9` replay tolerance.
The aggregate result is `PASS`, qualified review is true, and complete
engineering approval is false.

Focused tests also prove valid inadequate tie or anchorage returns typed
`FAIL`, while unsupported topology, material/action, geometry, grid,
non-finite input, and missing external verification fail closed without a
design disposition.

## Acceptance finding and truth correction

No calculation, workflow, transport, capability-semantic, or manifest mismatch
was found in the bounded main process. The material finding was stale planning:
the dedicated plan still described DEEP-B-D as pending, the parent wave table
still placed WALL-G0 next, the task summary described accepted families as held,
and the auto-handoff retained the pre-merge DEEP-D branch candidate.

The root cause was incomplete reconciliation of higher-level status projections
after the later packet integrations. This receipt binds acceptance to the exact
integrated main head, promotes no new capability, adds itself to the existing
deep-beam evidence chain, and moves the next action to decision-only
`INDIA-2-FLAT-G0`.

## Focused acceptance gates

- 157 deep-beam kernel, public workflow, FastAPI, capability, manifest,
  semantic, clause-data, traceability, and API-manifest tests passed.
- Independent hand arithmetic matched every frozen benchmark quantity and the
  public `PASS`/qualified-review/false-approval disposition.
- Architecture validation found 0 violations across 177 files and import
  validation found 0 broken imports across 210 structural-library files.
- API documentation, compatibility, exact OpenAPI snapshot, and schema
  snapshot checks passed for the unchanged 78-endpoint public surface.
- Scoped Black, Ruff, mypy, and Bandit checks passed.
- The deterministic manifest is current at 10 supported and 11 held families;
  all 78 endpoints have direct tests and actionable cross-layer parity is 100%.
- All 1,185 internal links, touched folder indexes, the token-efficiency check,
  and the quick repository gate pass.
- Required hosted PR checks must pass on the unchanged reviewed head before
  this acceptance receipt can enter `main`.

The broad Python suite and 30-check repository gate remain deferred until all
intended INDIA-2 families are integrated, unless an outcome-changing
repository-wide issue appears earlier. The next packet is `INDIA-2-FLAT-G0`;
it is decision-only until its own source, analysis model, supported panel and
punching boundary, benchmark, units, and exclusions return GO.
