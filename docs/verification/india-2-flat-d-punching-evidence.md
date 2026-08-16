---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-FLAT-D
---

# INDIA-2-FLAT-D Centred Punching Evidence

## Implemented boundary

FLAT-D adds the centred concentric punching check for the G0-frozen square
interior column. It consumes the fail-closed FLAT-A panel contract and requires
an explicit caller-provided factored support reaction with a non-blank analysis
basis. The reaction must match the uniform tributary action for this equal-span,
identically loaded interior topology; the calculation does not silently create
or alter a global-analysis reaction.

The critical section is a geometrically similar square at one-half effective
depth from the column faces. Openings, free edges, edge or corner columns,
offset or rectangular columns, drops, heads, nonuniform loading, unbalanced
moment transfer, and incomplete perimeters remain rejected by the inherited or
FLAT-D contracts.

This route checks concrete-only punching adequacy. It does not select or design
punching reinforcement. A demand above the no-reinforcement capacity therefore
fails the route. The result separately identifies the mandatory redesign
boundary above 1.5 times the basic concrete shear strength so it never implies
that reinforcement can rescue an inadmissible section.

## Source and traceability

The controlled consolidated IS 456:2000 source was checked for Clauses 31.6.1,
31.6.2.1, 31.6.3.1, and 31.6.3.2. Amendment 6 contains no Clause 31 change. The
identifier-only registry adds the three exact subclause identities that were
not already present and now contains 169 identifiers. No clause prose, figure,
page image, watermark, or source PDF is stored in the repository.

The calculation retains the standard and amendment identifiers together with
the caller's geometry, material, load, support-reaction, and punching-basis
references. Qualified engineering review and project approval remain explicit
limitations.

## Frozen benchmark

For `INDIA-2-FLAT-HAND-01`, the exact calculation is:

- factored tributary support reaction: `19.5 x 6 x 6 = 702.0 kN`;
- critical-section sides: `500 + 260 = 760 mm` in both directions;
- critical perimeter and enclosed area: `3040 mm` and `577600 mm2`;
- factored load inside the perimeter: `11.2632 kN`;
- punching shear force: `690.7368 kN`;
- nominal punching stress: `0.873907895 N/mm2`;
- `beta_c = 1`, `ks = 1`, and concrete-only capacity
  `0.25 sqrt(30) = 1.369306394 N/mm2`;
- mandatory redesign boundary: `2.053959591 N/mm2`; and
- concrete-only utilization: `0.638212090`, producing
  `SAFE_WITHOUT_PUNCHING_REINFORCEMENT`.

Direct tests also distinguish an intermediate demand that requires punching
reinforcement or redesign from a demand above the mandatory redesign boundary.
Reaction mismatch, every explicit applicability/review flag, missing
provenance, moment transfer, and non-input objects fail closed.

## Verification and retained holds

All 14 direct FLAT-D tests pass. The complete flat-slab geometry, moments,
reinforcement, punching, clause-database, traceability, and deterministic
manifest selection passes all 184 tests. Black, Ruff, mypy, and Bandit pass on
the changed executable paths. Architecture validation reports zero violations
across 183 files, and import validation reports zero broken imports across 618
Python files. All 1,207 internal links are valid and token efficiency passes.
All eight touched folder indexes are current, and the quick repository gate
passes 10/10.

Flat slab remains `HELD`/`NOT_IMPLEMENTED` until FLAT-E publishes the composed
Python workflow and thin FastAPI route. All alternate G0 topologies, punching
reinforcement design, direct deflection, crack width, professional approval,
and release remain held. Broad Python and the 30-check repository gate remain
deferred to final INDIA-2 closeout.
