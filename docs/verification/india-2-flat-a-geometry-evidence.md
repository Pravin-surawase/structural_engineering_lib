---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-FLAT-A
---

# INDIA-2-FLAT-A Geometry and Eligibility Evidence

## Implemented boundary

FLAT-A implements the typed pure-math foundation for the G0-approved case: one
solid square interior panel in an equal-span orthogonal column grid, using the
direct design method under identical uniform gravity loading. It adds no panel
moment, reinforcement, serviceability disposition, punching calculation, or
public capability claim; those belong to FLAT-B-E.

`FlatSlabGridGeometry` requires explicit mm dimensions, at least three
continuous equal spans in each direction, a square panel and square column,
the 125 mm minimum overall depth, a smaller caller-confirmed conservative
effective depth, the direct design method, the interior-panel location, every
supported topology assertion, and a non-blank geometry reference.

`FlatSlabMaterial` admits standard M20-M60 concrete, Fe415 or Fe500 uncoated
deformed bars, and explicit provenance. `FlatSlabGravityLoad` accepts service
dead/live and factored uniform loads in kN/m2 only when self-weight and an
approved `1.5(D + L)` combination are already included, live/dead is at most
`0.5`, all represented panels carry identical full gravity loading, and neither
patterned loading nor moment transfer is required.

## Normalized Clause 31 behavior

`resolve_regular_interior_flat_slab_geometry` exposes, in each orthogonal
direction:

- centre-to-centre and transverse spans;
- support width and face-to-face clear span;
- the `0.65` centre-span lower component and governing clear span;
- column-strip width on each side of the support centreline, total column-strip
  width, and remaining middle-strip width; and
- exact direction, units, source identities, and caller evidence.

The result also retains the 125 mm minimum thickness, service live/dead ratio,
expected factored uniform load, and affirmative direct-design eligibility. The
strip widths partition the full transverse span exactly.

Unsupported unequal or rectangular panels, fewer than three spans, unequal
spans, offset columns, non-solid slabs, drops, column heads, marginal beams or
walls, openings, exterior panels, equivalent-frame analysis, coated bars,
unsupported grades, incomplete load basis, patterned loading, moment transfer,
and non-finite values raise `FlatSlabContractError`; no partial geometry result
is produced.

## Public clause registration

The identifier-only traceability database registers Clause 31, 31.1, 31.1.1,
31.2, 31.2.1, 31.3, 31.3.1, 31.4, and 31.4.1 with titles, sections, the existing
`slabs` category, and search keywords. No clause prose, figure, or table value
is stored. The resolver is decorated with Clauses 31.1.1, 31.2.1, 31.3.1, and
31.4.1 and retains `IS456-2000-A6` plus the three caller evidence references.

## Benchmark and unsafe evidence

The frozen `INDIA-2-FLAT-HAND-01` inputs resolve identically in both
directions: centre span 6000 mm, face-to-face clear span 5500 mm, lower clear-
span component 3900 mm, governing clear span 5500 mm, 1500 mm half-column
strip, 3000 mm total column strip, and 3000 mm middle strip. Service live/dead
is `4/9`, the expected factored load is 19.5 kN/m2, and the geometry is direct-
design eligible.

A large-column case proves the `0.65` span component can govern. Tests also
cover the exact three-span and live/dead `0.5` boundaries, every frozen
topology/load assertion, material/action mismatch, clause/source provenance,
nested type contracts, non-finite values, and all out-of-domain cases listed
above.

The direct flat-slab geometry package passes 33 tests; the combined geometry,
clause-database, traceability, and deterministic-manifest selection passes 131
tests. The clause database contains 152 identifier-only records. Black, Ruff,
mypy, and Bandit pass on the changed executable paths. Architecture validation
reports zero violations across 180 files, and import validation reports zero
broken imports across 612 Python files. All 1,196 internal links are valid, all
seven touched folder indexes are current, the token-efficiency control passes,
and the quick repository gate passes 10/10.

The generated manifest remains current at 10 supported and 11 held families;
flat slab remains `HELD`/`NOT_IMPLEMENTED` until FLAT-E publication. The broad
Python suite and 30-check repository gate remain deferred to whole-INDIA-2
closeout unless an outcome-changing repository-wide issue appears earlier.
The next packet is `INDIA-2-FLAT-B`.
