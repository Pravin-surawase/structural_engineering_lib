---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-FOUNDATION-COMBINED-C
---

# INDIA-2-FOUNDATION-COMBINED-C Public Workflow Evidence

## Accepted outcome

COMBINED-C publishes one typed Python workflow,
`design_symmetric_combined_footing_is456`, over the already accepted
COMBINED-A action and COMBINED-B strength/detailing composition. It adds no
structural formula, alternate topology, automatic sizing, soil calculation,
FastAPI transport, React surface, or capability promotion.

The workflow returns `PASS` or valid in-domain `FAIL` with immutable result and
provenance types. Unsupported input raises `CombinedFootingContractError`.
Every result requires qualified engineering review and explicitly denies
complete engineering approval.

## Implementation identity

- Workflow and immutable public types:
  `Python/structural_lib/services/combined_footing_api.py`.
- Canonical exports: `Python/structural_lib/services/api.py`,
  `Python/structural_lib/services/__init__.py`, and
  `Python/structural_lib/__init__.py`.
- Backward compatibility: `Python/structural_lib/api.py` remains an unchanged
  re-export stub and inherits the canonical identities.
- Frozen benchmark, export identity, serialization, valid failure, fail-closed,
  immutability, provenance, and retained-truth tests:
  `Python/tests/integration/test_combined_footing_publication.py`.
- Public evaluation documentation: `docs/reference/api.md` and
  `docs/reference/api-stability.md`.

The public types are:

- `SymmetricCombinedFootingDesignInput`;
- `SymmetricCombinedFootingDesignProvenance`;
- `SymmetricCombinedFootingDesignResult`; and
- `SymmetricCombinedFootingDesignStatus`.

## Composition and provenance contract

`SymmetricCombinedFootingDesignInput` carries a case identity, the complete
typed `CombinedFootingDesignInput`, and explicit acknowledgement that qualified
review remains required. The service passes that typed input unchanged into
`check_symmetric_combined_footing_strength`; it does not repeat analysis,
flexure, shear, punching, bearing, dowel, anchorage, or detailing math.

The result retains the complete B strength result, including its recomputed A
actions. Stable provenance records schema `1.0`, the IS 456 base/amendment
edition, workflow and benchmark identities, exact inherited clause/source
references, and all caller-supplied bases for geometry, rigidity, loads,
bearing/settlement, distributed-carrier cancellation, materials, detailing,
effective supporting area, and dowel transfer.

The controlled source identities remain:

- consolidated IS 456 base through Amendment 5 SHA-256
  `964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264`;
- Amendment 6 SHA-256
  `4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881`;
  and
- public normalized-data permission `IS456-PUBLIC-DISTRIBUTION-001`.

No source PDF, scan, page image, watermark, or copied clause prose is a
repository artifact.

## Frozen benchmark replay

`INDIA-2-COMBINED-HAND-01` uses the inherited `6000 x 2500 x 850 mm` footing,
`750 mm` effective depth, two `500 mm` square columns at `x = 1000/5000 mm`,
M30/Fe500, `900/1350 kN` service/factored column loads,
`25/37.5 kN/m2` distributed carrier, and `150 kN/m2` allowable gross pressure.
It retains 16 mm longitudinal bars at 190 mm, 12 mm transverse bars at 110 mm,
50 mm cover, 20 mm aggregate, 800 mm anchorage, approved `250000 mm2`
supporting area, and four 20 mm dowels with 800 mm development into both
members.

The public result reproduces `145 kN/m2` gross service pressure,
`180 kN/m2` net factored structural pressure, `675 kNm` governing top
longitudinal moment, `2645.551708 mm2` supplied top steel,
`0.208134572` punching utilization, and `1256.637061 mm2` supplied dowel area.
Aggregate status is `PASS`; qualified review is true and complete engineering
approval is false.

## Retained truth and held cases

Generated capability truth remains exactly `11 supported / 10 held` and
combined footing remains `HELD` while its implementation status truthfully
records the bounded public Python preview. COMBINED-D still owns the thin
FastAPI route, runtime capability registration, semantic-contract projection,
and family acceptance. All existing 79 endpoints remain the only transport
routes and remain directly tested.

Unequal/eccentric loads, property-line or trapezoidal layouts, flexible or
variable soil pressure, bearing-capacity and settlement calculation, alternate
columns, pedestals, openings, variable depth, shear/punching reinforcement,
coated/bundled/spliced/curtailed bars, automatic sizing, durability selection,
strap footings, pile caps, raft foundations, React, release, construction or
professional approval remain held.

## Inherited B receipt correction

Live Git/GitHub verification before C confirmed that PR #789 squash-merged
final audited B head `948787bb56d28b8fbcca83aa94f1c68a26ec2eab` as
`f87c8a32aca7edc015f96f6e053f30c904ae683b`. Both the final head and merged
commit have tree `66243e06608f9323c605f16b8ca96eaf93d04fa5`; six applicable
hosted checks passed and two correctly skipped.

Three maintained prose documents still named the first audit candidate
`b9cb06f7` / `f5e405ad`, even though that audit had held the packet before the
semantic repair and the corrected head was re-audited. The final identity had
been propagated to the PR body but not back to the evidence/plan/handoff. The
closeout also had no later post-merge reconciliation step; attempting to embed
a commit's own final identity in its tree would be self-referential.
COMBINED-C corrects those maintained B identities, records the historical pre-
publication JSON Git receipt as `HOLD` rather than post-merge proof, and leaves
its own candidate identity fail-closed for live Git/GitHub verification. The
prior append-only B session entry is not rewritten.

## Focused verification

- All 7 direct C publication tests and all 78 combined A/B/C tests pass.
- The 213-test API export, packaging, manifest, clause-traceability, and public-
  contract selection passes; the combined focused total is 291 tests.
- Public API documentation/symbol parity, the 160-symbol generated API
  manifest, and deterministic Indian-code manifest pass. Capability remains
  11 supported / 10 held and there is no combined-footing semantic workflow or
  endpoint in C.
- Focused Ruff and mypy pass. Architecture reports 0/191 violations, imports
  0/632 broken, all 1,242 internal links are valid, and touched indexes are
  current.
- Source binding and token efficiency pass, and the quick gate is 10/10.
  Immutable exact-head audit, hosted checks, and merge identity are completed
  at closeout.

Using the accepted cadence: run focused gates for every packet, with broad
Python and the full 30-check repository gate only at the final INDIA-2
integration boundary unless a confirmed repository-wide failure forces them
earlier.
