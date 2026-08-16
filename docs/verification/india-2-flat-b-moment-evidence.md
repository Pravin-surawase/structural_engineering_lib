---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-FLAT-B
---

# INDIA-2-FLAT-B Direct-Design Moment Evidence

## Implemented boundary

FLAT-B adds only the gravity moment calculation approved by FLAT-G0. The input
must first satisfy the FLAT-A equal-span square interior-panel, direct-design,
identical-full-loading, and live/dead applicability contracts. The calculation
does not add flexural design, bar detailing, serviceability, punching, a public
workflow, or any alternate panel topology.

For each orthogonal direction, all geometry is resolved again through the
FLAT-A fail-closed function. The factored uniform action remains in kN/m2;
transverse and governing clear spans are explicitly converted from mm to m.
The design load on the panel strip is `W = wu * l2 * ln` in kN, and the total
static moment is `Mo = W * ln / 8` in kN m.

The admitted interior span assigns `0.65 Mo` to the negative region and
`0.35 Mo` to the positive region. The column strip receives 75 percent of the
negative moment and 60 percent of the positive moment. The middle strip
receives the exact remainder, so both negative and positive distributions
preserve their parent totals.

## Source and traceability

The controlled consolidated IS 456:2000 source was checked for Clauses
31.4.2.2, 31.4.3.2, 31.4.4, 31.5.5.1, 31.5.5.3, and 31.5.5.4. Amendment 6 was
also checked and contains no Clause 31 change. The implementation records those
identifiers, `IS456-2000-A6`, and the caller's geometry/load evidence. It stores
no clause prose, page image, watermark, or source PDF.

The identifier-only registry now contains 162 records and adds the required
Clause 31.4/31.5 hierarchy and search metadata. Registering the 31.5.5
distribution identifiers does not activate the equivalent-frame method; only
their panel-width distribution rules are applied through the direct-design
cross-reference in Clause 31.4.4.

## Frozen benchmark

`INDIA-2-FLAT-HAND-01` has `wu = 19.5 kN/m2`, `l2 = 6.0 m`, and
`ln = 5.5 m` in both directions. The independent hand values are:

- design load on the strip: `643.5 kN`;
- total static moment: `442.40625 kN m`;
- total negative/positive moment: `287.5640625 / 154.8421875 kN m`;
- column-strip negative/positive moment:
  `215.673046875 / 92.9053125 kN m`; and
- middle-strip negative/positive moment:
  `71.891015625 / 61.936875 kN m`.

The implementation reproduces all values in both directions. Direct tests also
prove conservation of total, negative, and positive moments; reuse of the
resolved 5500 mm clear span and 3000 mm strip widths; immutable typed results;
exact clause/source provenance; and rejection of non-panel inputs.

## Verification and retained holds

All 6 direct moment tests pass. The combined moment, geometry, clause-database,
and traceability selection passes 141 tests; adding deterministic-manifest
truth produces a 147-test focused packet selection. Black, Ruff, mypy, and
Bandit pass on the changed executable paths. Architecture validation reports
zero violations across 181 files, and import validation reports zero broken
imports across 614 Python files. All 1,200 internal links are valid, all seven
touched folder indexes are current, the token-efficiency control passes, and
the quick repository gate passes 10/10.

Flat slab remains `HELD`/`NOT_IMPLEMENTED` until FLAT-E publishes the complete
bounded workflow. Exterior/end panels, unequal spans, drops, heads, openings,
patterned loading, moment transfer, equivalent-frame analysis, FEM, flexural
design, serviceability, punching reinforcement, and all other G0 exclusions
remain held. The next packet is `INDIA-2-FLAT-C`; the broad Python suite and
30-check gate remain deferred to whole-INDIA-2 closeout.
