---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-FLAT-C
---

# INDIA-2-FLAT-C Reinforcement and Serviceability Evidence

## Implemented boundary

FLAT-C consumes the FLAT-A/B panel and moment contracts and adds only bounded
singly reinforced flexure, caller-provided straight-bar checks, the frozen
no-drop support-top extension, and a reviewed span/depth comparison. It does not
select bars, design bends or splices, calculate direct deflection or crack
width, check punching, or activate a public workflow.

Every calculation re-runs the FLAT-A eligibility and FLAT-B moment functions.
The common effective depth is the caller-confirmed conservative 260 mm carrier.
Each column or middle strip uses its derived 3000 mm width and the maintained
rectangular stress-block solver. Required steel is returned both for the entire
strip in mm2 and per metre in mm2/m.

The existing generic slab provided-bar checker supplies the 0.12 percent
minimum for Fe415/Fe500, diameter limit, and ordinary slab spacing limit. FLAT-C
also records the flat-slab-specific maximum spacing of twice the overall slab
depth. Failed provided area, spacing, or extension comparisons return an
inadequate disposition; unsupported topology/detailing input fails closed.

## Source and traceability

The controlled consolidated IS 456:2000 source was checked for Clauses 23.2.1,
26.3.3, 26.5.2.1, 31.2.1, 31.7.1, 31.7.2, 31.7.3, Figure 16, and Clause 38.1.
Amendment 6 contains no Clause 31 change. The identifier-only registry adds the
Clause 31.7 hierarchy and Figure 16 identity; it stores no clause prose, figure
geometry, page image, watermark, or source PDF.

For the G0 no-drop interior panel, caller-provided support-top straight bars
must extend at least `0.30 ln` from each support face, all bottom bars must be
continuous, and splices are excluded. This is a deliberately narrower
normalization than generalized Figure 16 detailing.

## Frozen benchmark

The both-direction strip results reproduce the independent hand values:

| Region | Required total strip | Required per m | Governing per m | Supplied per m |
|---|---:|---:|---:|---:|
| Column strip, negative | 1993.075996 mm2 | 664.358665 mm2/m | 664.358665 mm2/m | 706.858347 mm2/m |
| Column strip, positive | 836.624293 mm2 | 278.874764 mm2/m | 360.000000 mm2/m | 392.699082 mm2/m |
| Middle strip, negative | 644.654258 mm2 | 214.884753 mm2/m | 360.000000 mm2/m | 392.699082 mm2/m |
| Middle strip, positive | 554.292752 mm2 | 184.764251 mm2/m | 360.000000 mm2/m | 392.699082 mm2/m |

Column-strip negative reinforcement is 12 mm at 160 mm; the other three
regions use 10 mm at 200 mm. Both general slab and 600 mm flat-slab spacing
limits pass. The support-top extension is `0.30 x 5500 = 1650 mm` in each
direction.

The reviewed no-drop comparison uses centre span/effective depth
`6000 / 260 = 23.076923077` against `26 x 0.9 = 23.4`, utilization
`0.986193294`. It passes only the reviewed span/depth boundary. The reused
serviceability result truthfully keeps `verified_by_library = false`; direct
deflection and crack width remain held.

## Verification and retained holds

All 12 direct FLAT-C tests pass. The combined reinforcement, moment, geometry,
clause-database, and traceability selection passes 157 tests; adding
deterministic-manifest truth produces a 163-test focused packet selection.
Black, Ruff, mypy, and Bandit pass on the changed executable paths.
Architecture validation reports zero violations across 182 files, and import
validation reports zero broken imports across 616 Python files. All 1,204
internal links are valid, all seven touched folder indexes are current, token
efficiency passes, and the quick repository gate passes 10/10.

Flat slab remains `HELD`/`NOT_IMPLEMENTED` until FLAT-E. Inadequate provided
reinforcement and extension behavior, span/depth exceedance, explicit
straight/continuous/no-splice contracts, exact provenance, and non-input
rejection are tested. Automatic depth/bar selection, bends, splices, general
anchorage, congestion, direct deflection, crack width, punching, moment
transfer, and all alternate G0 topologies remain held. The next packet is
`INDIA-2-FLAT-D`; broad Python and the 30-check gate remain deferred to final
INDIA-2 closeout.
