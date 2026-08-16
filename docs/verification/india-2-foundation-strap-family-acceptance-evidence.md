---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-FOUNDATION-STRAP-ACCEPTANCE
---

# INDIA-2-FOUNDATION-STRAP Focused Family Acceptance Evidence

## Acceptance decision

**ACCEPT** the implemented strap-footing family within its written boundary.
The exact integrated G0/A-D starting head is
`b75daa970b2976cbd5d51e9a951926a7946d5fa6`, tree
`af2695a815bb0a71898d58e98a70109b7dd5c2b4`. The supported public workflow is
`design_property_line_strap_footing_is456`, exposed at
`POST /api/v1/design/strap-footing/property-line`, for exactly two separate
rectangular constant-depth footings on soil with one eccentric property-line
exterior square column, one centred interior square column, and one straight
prismatic no-soil-contact strap under caller-approved equal uniform net
pressure and common-factor vertical actions.

This receipt adds no calculation or product scope. Automatic footing sizing or
slab/transfer/connection design, unequal or nonuniform pressure, strap soil
bearing, alternate layouts, column moments, lateral or seismic actions, uplift,
reversal, independent factoring or patterning, nonlinear soil response,
torsion, deep/haunched/skewed/crossed or multiple straps, coated, bundled,
spliced or curtailed bars, pile caps, raft foundations, React, release,
construction approval, and professional approval remain held. Both footing
slabs and every footing/strap transfer region remain externally verified
prerequisites. Qualified engineering review remains mandatory and complete
engineering approval remains false.

## Integrated publication chain

| Packet | Merged identity | Integrated tree |
|---|---|---|
| G0, PR #793 | `70cd2894485d88b72d22544ee18533733789d0f1` | `60d5636265e157e723236909b1de7f582791b297` |
| A, PR #794 | `c410b28024e44e3e2670c8b359b69ae29165f2ae` | `08899dbedd35e3d0b0e2c9ba2e78813d87be1f70` |
| B, PR #795 | `ec6a81b32b9fc2ae227d041ec19bb848a99ac3eb` | `02f3a5c0bd0de0afbda6ca3ab128b40283efde5e` |
| C, PR #796 | `e3e4b2ae5d6559472c2e6595ce05d36887b32a1c` | `40040d5433b38b6c322bb1f6a789cab1bc5e2872` |
| D, PR #797 | `b75daa970b2976cbd5d51e9a951926a7946d5fa6` | `af2695a815bb0a71898d58e98a70109b7dd5c2b4` |

The controlled consolidated IS 456 source SHA-256 is
`964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264`.
The complete Amendment 6 source SHA-256 is
`4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881`.
The independent public analysis model is
[IISc Bangalore NPTEL Advanced Foundation Engineering Chapter 3](https://archive.nptel.ac.in/content/storage2/courses/105108069/mod03/lec03.pdf),
Section 3.6.1 and Fig. 3.2. Public approved-scope normalized formulas, limits,
and references are authorized by
`IS456-PUBLIC-DISTRIBUTION-001`. No source PDF, scan, page image, watermark, or
protected clause prose is a repository artifact.

## Frozen and non-frozen benchmark replay

`INDIA-2-STRAP-HAND-01` uses `2400 x 2500 mm` exterior and
`2500 x 3200 mm` interior footings, a `500 x 950 mm` strap with `850 mm`
effective depth, M30/Fe500 materials, and a common `1.5` factored multiplier.
The public workflow reproduces `1200/1600 kN` service reactions,
`200 kN/m2` equal service net pressure, `916.6875 kN m` governing factored top
moment, `261.65625 kN` governing factored shear,
`2788.774499810215/2945.243112740431 mm2` required/provided top steel,
`0.615661764705882/0.569479416608601 N/mm2` nominal/concrete shear stress,
and `19.6274979428445/232.320776807564 kN` required/provided stirrup-carried
shear. The aggregate result is `PASS`, qualified review is true, and complete
engineering approval is false.

The independent non-frozen replay scales the plan and member geometry by
`1.10` and the column actions by `1.21`. It uses `2640 x 2750 x 770 mm` and
`2750 x 3520 x 770 mm` footings, `550 mm` square columns at
`x = 440/7040 mm`, a `550 x 1045 mm` strap with `935 mm` effective depth,
seven 25 mm top bars, five 16 mm bottom bars, four 12 mm side-face bars on each
face at 260 mm, two-leg 10 mm stirrups at 225 mm, 55 mm cover, and 1320 mm
bilateral anchorage. It returns `PASS` with approximately `200/200 kN/m2`
service net pressure, `1220.1110625000001 kN m` governing factored moment,
`316.60406250000005 kN` governing factored shear,
`3374.4171447703598/3436.116964863836 mm2` required/provided top steel,
`0.6156617647058825/0.5605448920468606 N/mm2` nominal/concrete shear stress,
and `28.343851764902013/283.9476160069575 kN` required/provided stirrup-
carried shear. The complete geometry, load, carrier, topology, approval,
material, reinforcement, cover, detailing, durability, and anchorage contract
is committed as the
[`INDIA-2-STRAP-ACCEPTANCE-NONFROZEN-01` replay fixture](india-2-foundation-strap-acceptance-nonfrozen-replay.json).

Run the fixture independently from the repository root:

```bash
./scripts/python_runtime.sh - <<'PY'
import json
from pathlib import Path

from structural_lib.services.strap_footing_api import (
    build_property_line_strap_footing_design_input,
    design_property_line_strap_footing_is456,
)

fixture = Path(
    "docs/verification/india-2-foundation-strap-acceptance-nonfrozen-replay.json"
)
request = build_property_line_strap_footing_design_input(
    json.loads(fixture.read_text(encoding="utf-8"))
)
result = design_property_line_strap_footing_is456(request)
strength = result.strength
observed = (
    result.status.value,
    strength.actions.factored_clear_strap.governing_moment_demand_kn_m,
    strength.actions.factored_clear_strap.governing_shear_demand_kn,
    strength.flexure.exact_flexural_steel_required_mm2,
    strength.flexure.top_steel_provided_mm2,
    strength.shear.nominal_shear_stress_nmm2,
    strength.shear.concrete_design_shear_strength_nmm2,
    strength.shear.stirrup_carried_shear_required_kn,
    strength.shear.stirrup_shear_capacity_provided_kn,
)
expected = (
    "PASS",
    1220.1110625000001,
    316.60406250000005,
    3374.4171447703598,
    3436.116964863836,
    0.6156617647058825,
    0.5605448920468606,
    28.343851764902013,
    283.9476160069575,
)
assert observed == expected, (observed, expected)
assert result.qualified_review_required is True
assert result.complete_engineering_design_approved is False
print(observed)
PY
```

Focused tests prove that inadequate bearing, longitudinal/side-face steel,
stirrups, spacing, cover, anchorage, singly reinforced capacity, or maximum
shear remains a valid typed `FAIL`. Unsupported pressure/equilibrium,
topology, materials, action pattern, approval bases, connection verification,
non-finite input, and non-boolean approval flags fail closed without a design
disposition.

## Acceptance findings and root-cause corrections

No calculation, workflow, transport, capability, semantic, OpenAPI, or
deterministic-manifest mismatch remained after the focused acceptance review.
The first fixture replay command passed `case_id` as a separate workflow
argument and stopped before calculation. The command had inferred the public
signature instead of using the repository's discovery control. The maintained
signature accepts only one typed `PropertyLineStrapFootingDesignInput`; the
fixture builder already binds `case_id`. The corrected discovered invocation
reproduces every value above, so no kernel or fixture change was needed.

STRAP-D itself encountered and corrected two hosted-only integration defects
before merge: a FastAPI test imported a fixture across pytest roots, and a
dual-use validated request model produced Pydantic-version-dependent OpenAPI
component suffixes. D made the transport test self-contained, fixed the schema
mode explicitly, added semantic regression coverage, and passed 443 hosted-
equivalent FastAPI tests plus all required hosted checks on the exact audited
tree. Acceptance verified those corrections in the merged starting tree.

The maintained plans still projected D or focused acceptance as the next
packet because final family truth intentionally waited for this receipt. This
packet binds the family to merged D, adds itself to the deterministic evidence
chain, and moves the next action to the separate decision-only
`INDIA-2-FOUNDATION-PILE-CAP-G0` packet without starting it.

## Focused acceptance gates

- All 85 strap G0/A-D analysis, strength, public-workflow, and transport tests
  pass, including the frozen benchmark, valid failures, and every maintained
  fail-closed boundary.
- The 143-test strap/public-contract selection passes, including public export,
  JSON serialization, OpenAPI, capability, semantic, deterministic manifest,
  clause data, traceability, and API-manifest checks.
- The deterministic manifest remains current at 13 supported and 8 held
  families; all 81 endpoints have direct tests and actionable cross-layer
  parity remains 100 percent.
- Architecture reports 0 violations across 200 files. Import validation reports
  0 broken imports across 647 Python files, 4,387 imports, and 2,053 internal
  imports. All 1,279 internal links and every touched maintained index pass.
- Black, Ruff, and focused mypy pass for the two touched Python files. Source
  binding, token efficiency, and the 10/10 quick repository gate pass.
- An independent exact-head audit and all applicable hosted PR checks must pass
  before this acceptance receipt can enter `main` unchanged.

Using the cadence you quoted: focused gates per packet, with the broad Python
and 30-check gates only at the final INDIA-2 integration boundary unless a
repository-wide failure forces them earlier. The next packet is decision-only
`INDIA-2-FOUNDATION-PILE-CAP-G0`; this receipt does not begin or authorize its
implementation.
