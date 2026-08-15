---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-WALL-D
---

# INDIA-2-WALL-D Publication Evidence

## Published boundary

WALL-D publishes the integrated `design_braced_wall_is456` workflow through
`POST /api/v1/design/wall/braced-axial` and promotes exactly one bounded `wall`
entry in canonical capability discovery. Both surfaces delegate to the same
typed service used by the public Python API; no engineering formula exists in
the transport layer.

The supported capability is one regular 100-200 mm thick one-grid Clause 32.2
braced wall under caller-supplied factored in-plane vertical compression, with
empirical axial-capacity and Clause 32.5 caller-provided minimum-reinforcement
checks. Qualified engineering review remains mandatory.

## Public clause and source visibility

The typed REST result exposes Clause 32.2.1-32.2.5 and 32.5-32.5.2 identifiers,
normalized standard/source IDs, benchmark `INDIA-2-WALL-HAND-01`, explicit
bracing/action/reinforcement references, load-generation status, supported
case, held cases, and approval booleans. The request and response schemas keep
mm, kN, N/mm2, N/mm, kN/m, dimensionless ratios, and mm2/m quantities explicit.

The deterministic Indian-code manifest now records `wall` as
`SUPPORTED`/`IMPLEMENTED_BOUNDED` with the sole public workflow
`design_braced_wall_is456`; the broad IS 13920 wall-detailing family remains
separately `HELD`/`NOT_IMPLEMENTED`.

## Transport evidence

The frozen endpoint example returns:

- overall and axial status `PASS`;
- effective height 2250 mm;
- capacity 684 N/mm, demand 500 N/mm, utilization 0.7309941520;
- vertical provided steel 201.061930 mm2/m;
- horizontal provided steel 314.159265 mm2/m;
- qualified review required true and complete engineering approval false.

A valid overload and valid inadequate reinforcement return HTTP 200 with a
typed `FAIL`. Extra fields, non-finite values, unconfirmed bracing, walls above
200 mm, and core-contract violations return HTTP 422 in the standard safe error
envelope. OpenAPI binds the success response to `BracedWallResponse`.

## Retained holds

Applied moment, horizontal action, wall shear, combined flexure, openings,
out-of-plane behavior, two-grid walls, transverse-enclosure design, global/load
analysis, load combinations, bar selection, anchorage, lap, crack width, direct
deflection, seismic/IS 13920 detailing, React, professional approval, release,
and alternate wall systems remain outside the supported capability.

## Focused verification

- 20 focused wall publication, manifest, FastAPI, and capability tests passed.
- The combined wall, API, manifest, clause-database, and traceability selection
  passed 128 tests.
- Black, Ruff, mypy, and Bandit passed on the changed Python/FastAPI paths.
- API compatibility reports no break across 77 endpoints and 293 schemas.
- The exact OpenAPI snapshot was regenerated to the same counts; semantic diff
  inspection found only the one wall endpoint and seven wall schemas added,
  with no path or schema removals.
- Architecture validation found 0 violations across 170 files and structural-
  library import validation found 0 broken imports across 205 files.
- The generated Indian-code manifest reports 9 supported and 12 held declared
  families, with 43 percent informational declared-capability coverage.
- The packet quick gate passed 10/10 and all 1,153 internal links are valid.

WALL-D publication does not by itself close family acceptance. The next packet
runs the focused cumulative wall acceptance selection from integrated A-D and
freezes its exact receipt before starting `INDIA-2-DEEP-G0`.
