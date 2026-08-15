---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-DEEP-A
---

# INDIA-2-DEEP-A Geometry and Lever-Arm Evidence

## Implemented boundary

DEEP-A implements the typed pure-math foundation for the G0-approved case: one
simply supported, top-loaded, solid rectangular deep beam without openings,
dapped ends, or hanging action. It adds no reinforcement-area or final design
disposition; those belong to DEEP-B.

`DeepBeamGeometry` requires explicit mm geometry, the supported support type,
all topology assertions, geometry provenance, and affirmative external
bearing/compression-nodal verification with a non-blank reference.
`DeepBeamActionInput` accepts standard M20-M60 concrete, Fe415 or Fe500 steel,
one caller-supplied positive factored moment in kN m, and its action reference.

## Normalized Clause 29 behavior

`resolve_simply_supported_deep_beam_geometry` exposes:

- both effective-span components and their governing minimum;
- effective-span/overall-depth ratio, failing closed at or above `2.0`;
- the visually verified `0.6l` lever arm below ratio one;
- the `0.2(l + 2D)` lever arm from ratio one to below two;
- the Clause 29.3.1 positive-reinforcement zone depth; and
- exact clause, standard, geometry-basis, and external bearing/nodal references.

The two lever-arm branches produce the same value at ratio one. Unsupported
continuous support, openings, non-solid sections, dapped ends, non-top loading,
hanging action, missing bearing/nodal confirmation, invalid material/action,
and non-finite values raise `DeepBeamContractError`; they do not produce a
partial geometry result.

## Public clause registration

The identifier-only traceability database now registers Clause 29, 29.1, 29.2,
29.3, and 29.3.1-29.3.4 with titles, sections, categories, and search keywords.
No clause prose or table content is stored. The resolver is decorated with
Clauses 29.1, 29.2, and 29.3.1, and its runtime result retains
`IS456-2000-A6` plus caller evidence.

## Benchmark and unsafe evidence

The frozen `INDIA-2-DEEP-HAND-01` geometry resolves exactly to effective span
3000 mm, ratio 1.5, lever arm 1400 mm, and positive-reinforcement zone depth
350 mm. A clear-span-controlled case, the below-one branch, the ratio-one
continuity point, the just-below-two boundary, and exact ratio-two rejection are
all directly tested.

The direct deep-beam package passes 20 tests; the combined geometry,
clause-database, traceability, and deterministic-manifest selection passes 109
tests. The clause database now contains 143 identifier-only records. Black,
Ruff, mypy, and Bandit pass on the changed executable paths. Architecture
validation reports 0 violations across 173 files and import validation reports
0 broken imports across 208 files.

The generated manifest remains current at 9 supported and 12 held families;
deep beam remains `HELD`/`NOT_IMPLEMENTED` until the later publication packet.
Actionable parity remains 100%, all 77 endpoints retain direct tests, touched
folder indexes are current, and quick gate passes 10/10. Required hosted checks
must pass on the unchanged reviewed head before integration.

The broad Python suite and 30-check repository gate remain deferred to the one
whole-INDIA-2 closeout, unless an outcome-changing repository-wide issue
appears earlier. The next packet is `INDIA-2-DEEP-B`.
