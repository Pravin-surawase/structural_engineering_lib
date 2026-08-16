---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-WALL-ACCEPTANCE
---

# INDIA-2-WALL Focused Family Acceptance Evidence

## Acceptance decision

**ACCEPT** the implemented wall family within its written boundary. The exact
integrated A-D starting head was `46094a8c35c75fcfb0644f23a851087cc3297c60`.
The supported public route remains one regular 100-200 mm thick, one-grid,
braced wall under caller-supplied factored in-plane vertical compression.

This receipt adds no wall calculation scope. Applied moment, horizontal action,
shear, openings, out-of-plane behavior, two-grid walls, global/load analysis,
automatic sizing or bar selection, seismic provisions, and IS 13920 detailing
remain held. Qualified engineering review remains mandatory and complete
engineering approval remains false.

## Public clause and source evidence

The Python and REST results expose IS 456:2000 Clause 32.2.1-32.2.5 and
32.5-32.5.2 identifiers, normalized source IDs, explicit units, the accepted
case, held cases, and benchmark `INDIA-2-WALL-HAND-01`. Approved-scope clause
identifiers, normalized formulas, limits, and provenance are public repository
content. Controlled source PDFs, page images, and copied clause prose are not
repository artifacts.

## Independent benchmark replay

The frozen hand benchmark was recomputed independently of the wall kernel and
compared with the public workflow. Effective height 2250 mm, capacity 684
N/mm, demand 500 N/mm, vertical steel 201.061929829747 mm2/m, and horizontal
steel 314.159265358979 mm2/m matched with zero displayed absolute error. The
aggregate result was `PASS`.

Focused tests also prove valid overload and inadequate reinforcement return a
typed `FAIL`, while unsupported geometry, bracing, material, action, and
non-finite input fail closed without a design disposition.

## Acceptance finding and root-cause correction

The cumulative semantic-contract test initially failed because the wall
contract advertised three typed-request quantities as if they were top-level
workflow fields. The verifier also inspected dataclass fields but not public
computed result properties such as `reinforcement.status`.

The root cause was inconsistent representation of a typed request/result
surface in capability discovery. The contract now uses
`request.wall_thickness_mm`, `request.factored_axial_load_kn`, and
`request.supplied_eccentricity_mm`; the verifier enumerates one level of typed
dataclass input and public computed result properties. The focused semantic
test and the complete 135-test family selection pass after the correction.

## Focused acceptance gates

- 135 wall kernel, public workflow, FastAPI, capability, manifest, semantic,
  clause-data, and traceability tests passed.
- The independent hand arithmetic matched the public runtime at every frozen
  benchmark quantity.
- Architecture validation found 0 violations across 170 files and import
  validation found 0 broken imports across 205 files.
- API compatibility and the exact OpenAPI snapshot pass across 77 endpoints and
  293 schemas; no API break was introduced.
- Black, Ruff, mypy, and Bandit pass on the changed executable paths.
- The deterministic manifest is current at 9 supported and 12 held families;
  all 77 endpoints have direct tests and actionable cross-layer parity is 100%.
- All 1,157 internal links and touched folder-index hashes are valid; the token-
  efficiency check and quick repository gate pass, with the latter at 10/10.
- Required hosted PR checks must pass on the unchanged reviewed head before
  this acceptance receipt can enter `main`.
- The generated manifest records this receipt for the supported wall family;
  alternate and seismic wall families remain explicitly held.

The broad Python suite and 30-check repository gate remain deferred until all
intended INDIA-2 families are integrated, unless an outcome-changing
repository-wide issue appears earlier. The next action is `INDIA-2-DEEP-G0`.
