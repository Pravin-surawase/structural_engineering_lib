---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-FLAT-ACCEPTANCE
---

# INDIA-2-FLAT Focused Family Acceptance Evidence

## Acceptance decision

**ACCEPT** the implemented flat-slab family within its written boundary. The
exact integrated G0/A-E starting head was
`b04d80653484a8dc43e8ff73936d8171e4b65d40`. The supported public route remains
one equal-span square interior solid panel in a minimum three-by-three
orthogonal column grid under identical uniform gravity loading, using the
direct design method and one centred square interior-column concrete-only
punching check.

This receipt adds no calculation or product scope. Unequal or rectangular
panels, fewer than three continuous spans, exterior panels, edge/corner or
offset columns, drops, heads, marginal beams or walls, openings, patterned or
nonuniform loading, concentrated actions, unbalanced moment transfer,
punching-reinforcement design, equivalent-frame or FEM analysis, direct
deflection, crack width, automatic sizing, prestress, seismic/progressive-
collapse design, fire, React, and release remain held. Qualified engineering
review remains mandatory and complete engineering approval remains false.

## Public clause and source evidence

The Python and REST results expose IS 456:2000 Clauses 23.2, 26.3, and
31.1-31.7; normalized Figure 16 length rules; standard and amendment source
IDs; explicit mm, kN, kN m, kN/m2, and N/mm2 units; the accepted case;
retained cases; and benchmark `INDIA-2-FLAT-HAND-01`. Approved-scope formulas,
limits, case identifiers, and provenance are public repository content.
Controlled source PDFs, page images, and copied clause prose are not repository
artifacts.

## Independent benchmark replay

The frozen benchmark was recomputed independently of the flat-slab kernel and
compared with the public workflow. Governing clear span `5500 mm`, total static
moment `442.40625 kN m`, column-strip negative steel
`1993.0759957303314 mm2`, reviewed span/depth utilization
`0.9861932938856016`, tributary reaction `702 kN`, punching shear
`690.7368 kN`, and concrete-only punching utilization
`0.6382120901359107` match within the frozen replay tolerance. The aggregate
result is `PASS`, qualified review is true, and complete engineering approval
is false.

Focused tests also prove valid inadequate reinforcement, detailing,
span/depth, or punching returns typed `FAIL`, while unsupported topology,
material/load/action, geometry, review-evidence, reaction-integrity, non-finite,
and missing-evidence cases fail closed without a design disposition.

## Acceptance finding and truth correction

No calculation, workflow, transport, capability declaration, or manifest
mismatch remained after focused audit. The audit found that the maintained
semantic validator traversed only one typed dataclass level and therefore could
not verify FLAT-E's truthful two-level canonical request paths. It also found
stale planning: the dedicated and parent plans, task board, and next-session
brief still described FLAT-E as a candidate or FLAT-G0 as next after FLAT-E
had entered `main` through PR #785.

The semantic root cause was a one-level-only test helper, not a false public
field declaration. The helper now follows typed dataclass fields recursively,
with cycle protection, so it verifies `request.panel.geometry`, the nested
gravity-load action, and all other declared paths against the actual public
types. The planning root cause was incomplete reconciliation after FLAT-E
integration. This receipt binds acceptance to the exact integrated main base,
promotes no new capability, adds itself to the flat-slab evidence chain, and
moves the next action to decision-only `INDIA-2-FOUNDATION-COMBINED-G0`.

## Focused acceptance gates

- 214 flat-slab kernel, public workflow, FastAPI, capability, manifest,
  semantic, clause-data, traceability, and API-manifest tests passed.
- Independent hand arithmetic matched every frozen benchmark quantity and the
  public `PASS`/qualified-review/false-approval disposition.
- Architecture validation found 0 violations across 186 files and import
  validation found 0 broken imports across 623 Python files.
- API documentation, compatibility, exact OpenAPI snapshot, and schema
  snapshot checks passed for the unchanged 79-endpoint public surface.
- The deterministic manifest is current at 11 supported and 10 held families;
  all 79 endpoints have direct tests and actionable cross-layer parity is
  100 percent.
- All 1,216 internal links, touched folder indexes, the token-efficiency check,
  and the quick repository gate pass.
- Required hosted PR checks must pass on the unchanged reviewed head before
  this acceptance receipt can enter `main`.

The broad Python suite and 30-check repository gate remain deferred until all
intended INDIA-2 families are integrated, unless an outcome-changing
repository-wide issue appears earlier. The next packet is
`INDIA-2-FOUNDATION-COMBINED-G0`; it is decision-only until its own source,
analysis model, supported geometry/action boundary, benchmark, units, and
exclusions return GO.
