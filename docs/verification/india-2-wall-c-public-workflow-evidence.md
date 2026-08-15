---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-WALL-C
---

# INDIA-2-WALL-C Public Python Workflow Evidence

## Published boundary

WALL-C publishes one canonical typed Python function,
`design_braced_wall_is456`, through `structural_lib.services.api`, the
compatibility `structural_lib.api` facade, and package-root imports. The service
builds one shared geometry contract and composes the integrated Clause 32.2
axial kernel with the Clause 32.5 provided-reinforcement check. It does not
duplicate calculation logic or generate actions.

The public types are `BracedWallDesignInput`, `BracedWallDesignProvenance`, and
`BracedWallDesignResult`. The API manifest and reference/stability documentation
include all four names. The capability registry and FastAPI route remain held
until WALL-D, so this packet does not yet advertise wall support.

## Public IS 456 provenance

The result exposes the public Clause 32.2.1-32.2.5 and 32.5-32.5.2 identifiers,
the normalized source IDs `IS 456:2000 Cl. 32.2.1-32.2.5`,
`IS 456:2000 Cl. 32.5-32.5.2`, and `IS456-2000-A6`, and the caller's bracing,
factored-action, and reinforcement-basis references. Provenance also identifies
schema version `1.0`, workflow `design_braced_wall_is456`, benchmark
`INDIA-2-WALL-HAND-01`, and the fact that loads were not generated.

All dimensions are explicit mm, concrete strength is N/mm2, factored total
compression is kN, per-unit-length capacity/demand is N/mm and kN/m, and
provided/required reinforcement is mm2/m.

## Frozen end-to-end result

The public workflow reproduces the integrated benchmark:

- effective height: 2250 mm;
- design and additional eccentricity: 7.5 mm and 13.5 mm;
- empirical capacity and demand: 684 N/mm and 500 N/mm;
- axial utilization: 0.7309941520, `PASS`;
- vertical steel: 201.061930 mm2/m against 180 mm2/m, `PASS`;
- horizontal steel: 314.159265 mm2/m against 300 mm2/m, `PASS`;
- composed disposition: `PASS` with qualified review required and complete
  engineering approval false.

The frozen dataclass result serializes through `dataclasses.asdict` and JSON.
An axial overload and valid inadequate provided reinforcement each produce a
composed `FAIL`.

## Retained holds

Applied moment, horizontal action, wall shear, combined flexure, openings,
out-of-plane behavior, walls thicker than 200 mm, two grids, transverse-
enclosure design, global/load analysis, load combinations, bar selection,
anchorage, lap, crack width, direct deflection, seismic/IS 13920 detailing,
React, professional approval, release, and every alternate wall system remain
outside WALL-C.

## Focused verification

- 39 wall/publication tests passed.
- The combined wall, public API, manifest-tool, clause-database, and
  traceability selection passed 119 tests.
- API manifest generation/check and the 76-endpoint/286-schema compatibility
  validator passed with no breaking changes.
- Black, Ruff, and mypy passed on the new service and public-contract tests.
- API reference coverage and API/stability-document synchronization passed.
- Architecture validation found 0 violations across 168 files and import
  validation found 0 broken imports across 205 files.
- The packet-level quick gate passed 10/10 and all 1,152 internal links are
  valid.

These results establish bounded software behavior and public-code provenance;
they do not constitute professional design approval or release authorization.
