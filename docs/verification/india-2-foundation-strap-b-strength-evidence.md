---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-FOUNDATION-STRAP-B
---

# INDIA-2 Foundation Strap B Strength Evidence

## Scope and retained boundary

This packet composes A actions with caller-supplied M20-M40 concrete, Fe415/
Fe500 uncoated deformed bars, longitudinal/side-face reinforcement, vertical
closed stirrups, approved cover, and straight anchorage into both footings. It
checks exact rectangular stress-block flexure, Clause 26.5.1.1 beam minimum
steel, side-face steel, clear spacing, cover, development length, Table 19/20
shear, minimum stirrups, stirrup strength/spacing, and gross service bearing.

Footing slabs, column/strap transfer, soil capacity, settlement, connections,
automatic reinforcement, public Python composition, FastAPI, capability
promotion, React, release, broad Python, and the full 30-check gate remain
outside B.

## Frozen benchmark

`INDIA-2-STRAP-HAND-01` returns `PASS` with qualified review required and
complete engineering approval false. The exact physical stress-block root is
`2788.774499810215 mm2` with `xu = 224.651279151378 mm`; direct substitution
returns the `916.6875 kN m` demand, while six 25 mm top bars provide
`2945.243112740431 mm2` and `961.337320139164 kN m` resistance. Four 16 mm
bottom bars exceed the `722.5 mm2` beam minimum.

Eight 12 mm side-face bars provide `904.77868423386 mm2` total against
`475 mm2`. Table 19 interpolation gives `tau_c = 0.569479416608601 N/mm2`
against `tau_v = 0.615661764705882 N/mm2`; the stirrup-carried demand is
`19.6274979428445 kN`. Two-leg 10 mm stirrups at 250 mm provide
`157.07963267949 mm2`, exceed the `114.942528735632 mm2` minimum, and resist
`232.320776807564 kN`. Required 25 mm top-bar development is `1132.8125 mm`;
`1200 mm` is supplied into both footings.

## Dispositions and provenance

Valid inadequate bearing, longitudinal/side-face steel, stirrups, spacing,
cover, anchorage, singly reinforced capacity, or maximum shear produces
`FAIL`. Unsupported grades/layouts/approvals, coated/bundled/spliced/curtailed
bars, invalid values, or an invalid A contract fail closed without a result.
The result carries normalized clause/source IDs, controlled source hashes,
the public IISc/NPTEL model ID, hand-benchmark ID, and caller references. No
source scans or protected prose are committed.

## Verification

- Direct STRAP-B tests, cumulative A/B tests, exact-helper regression, Ruff,
  Black, mypy, architecture/import, manifest/parity, links/indexes, source
  binding, and quick gate pass.
- Capability remains held at `12 supported / 9 held`; it now truthfully states
  that G0/A/B exist while public composition/publication remain pending.
- Exact candidate commit/tree, independent audit, hosted checks, and merge
  identity are bound by the packet Git handoff receipt.
