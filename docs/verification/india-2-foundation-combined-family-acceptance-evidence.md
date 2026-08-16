---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-FOUNDATION-COMBINED-ACCEPTANCE
---

# INDIA-2-FOUNDATION-COMBINED Focused Family Acceptance Evidence

## Acceptance decision

**ACCEPT** the implemented combined-footing family within its written boundary.
The exact integrated G0/A-D starting head is
`079ca22b00744ca9b01f859be0b64333b5830fcb`, tree
`efba5971017b03e14e3b2f30fd40750f8fc68987`. The supported public workflow is
`design_symmetric_combined_footing_is456`, exposed at
`POST /api/v1/design/combined-footing/symmetric`, for exactly two identical
square columns with equal concentric axial loads on one symmetric rigid
rectangular constant-depth footing under a caller-approved uniform-pressure
model.

This receipt adds no calculation or product scope. Unequal or eccentric loads,
property-line or trapezoidal layouts, flexible or variable soil pressure,
bearing-capacity and settlement calculation, alternate columns, pedestals,
openings, variable depth, shear or punching reinforcement, coated, bundled,
spliced, or curtailed bars, automatic sizing, durability selection, strap
footings, pile caps, raft foundations, React, release, construction approval,
and professional approval remain held. Qualified engineering review remains
mandatory and complete engineering approval remains false.

## Integrated publication chain

| Packet | Merged identity | Integrated tree |
|---|---|---|
| G0, PR #787 | `ee80091ee14366dacb650797dd4de82f3da67516` | `697d3c13ca2be41cb5563b79197ae9856037248b` |
| A, PR #788 | `6d230500b34dc9c79913d2cae87b8382ca732a27` | `fb4483f6d5590e6c26f23388323cccdf9b2a0c68` |
| B, PR #789 | `f87c8a32aca7edc015f96f6e053f30c904ae683b` | `66243e06608f9323c605f16b8ca96eaf93d04fa5` |
| C, PR #790 | `7b7b310a9310c04a65b1dcdfd4ef812c792bb8cb` | `dd9ed4adf0b20de5d307689ecdf502801fad2d6e` |
| D, PR #791 | `079ca22b00744ca9b01f859be0b64333b5830fcb` | `efba5971017b03e14e3b2f30fd40750f8fc68987` |

The controlled consolidated IS 456 source SHA-256 is
`964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264`.
The complete Amendment 6 source SHA-256 is
`4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881`.
Public approved-scope normalized formulas, limits, and references are
authorized by `IS456-PUBLIC-DISTRIBUTION-001`. No source PDF, scan, page image,
watermark, or protected clause prose is a repository artifact.

## Frozen benchmark replay

`INDIA-2-COMBINED-HAND-01` uses a `6000 x 2500 x 850 mm` footing with
`750 mm` effective depth, `500 mm` square columns at `x = 1000/5000 mm`,
M30/Fe500 materials, `900/1350 kN` service/factored load at each column,
`25/37.5 kN/m2` distributed carriers, and `150 kN/m2` allowable gross
pressure. The public workflow reproduces `145 kN/m2` gross service pressure,
`180 kN/m2` net factored structural pressure, `675 kN m` governing top moment,
`2645.551708286142 mm2` provided top steel, concrete-only punching utilization
`0.208134572`, and `1256.6370614359173 mm2` provided dowel area. The aggregate
result is `PASS`, qualified review is true, and complete engineering approval
is false.

An independent non-frozen replay uses a `7200 x 3000 x 900 mm` footing with
`800 mm` effective depth, `600 mm` square columns at `x = 1300/5900 mm`,
16 mm top/bottom bars at 160 mm, 12 mm transverse bars at 100 mm, six 20 mm
dowels, and 900 mm anchorage/development. It returns `PASS` with `125 kN/m2`
net pressure, `3239.9999999999995 / 3769.9111843077517 mm2` governing-required/
provided top steel, `0.24665178571428573 / 1.3693063937629153 N/mm2` punching
stress/capacity, and `1800 / 1884.9555921538758 mm2` required/provided dowels.
The complete load, carrier, bearing, topology, approval, material, detailing,
supporting-area, and transfer contract is committed as the
[`INDIA-2-COMBINED-ACCEPTANCE-NONFROZEN-01` replay fixture](india-2-foundation-combined-acceptance-nonfrozen-replay.json).

Run the fixture independently from the repository root:

```bash
./scripts/python_runtime.sh - <<'PY'
import json
from pathlib import Path

from structural_lib.services.combined_footing_api import (
    build_symmetric_combined_footing_design_input,
    design_symmetric_combined_footing_is456,
)

fixture = Path(
    "docs/verification/india-2-foundation-combined-acceptance-nonfrozen-replay.json"
)
request = build_symmetric_combined_footing_design_input(
    json.loads(fixture.read_text(encoding="utf-8"))
)
result = design_symmetric_combined_footing_is456(request)
strength = result.strength
observed = (
    result.status.value,
    strength.actions.net_factored_structural_pressure_kn_per_m2,
    strength.top_longitudinal_flexure.governing_steel_required_mm2,
    strength.top_longitudinal_flexure.provided_steel_area_mm2,
    strength.punching[0].nominal_punching_stress_nmm2,
    strength.punching[0].concrete_capacity_nmm2,
    strength.load_transfer[0].required_transfer_steel_area_mm2,
    strength.load_transfer[0].provided_transfer_steel_area_mm2,
)
expected = (
    "PASS",
    125.0,
    3239.9999999999995,
    3769.9111843077517,
    0.24665178571428573,
    1.3693063937629153,
    1800.0,
    1884.9555921538758,
)
assert observed == expected, (observed, expected)
print(observed)
PY
```

Focused tests prove that inadequate bearing, reinforcement/detailing,
one-way shear, concrete-only punching, and column-to-footing transfer remain
valid typed `FAIL` results. Unsupported topology, materials, approval bases,
supporting area, non-finite input, and non-boolean approval flags fail closed
without a design disposition.

## Acceptance findings and root-cause corrections

No calculation, workflow, transport, capability, semantic, OpenAPI, or
deterministic-manifest mismatch remained after the focused acceptance review.
The first non-frozen replay returned a valid transverse-reinforcement `FAIL`
and then its diagnostic command referenced a nonexistent result field. The B
evidence preserved the independently audited outputs but not the complete
supplied reinforcement schedule, and the diagnostic field name had been
guessed before inspecting the result dataclass. The replay was corrected only
after inspecting the maintained types: transverse spacing is 100 mm and the
exact field is `required_transfer_steel_area_mm2`. The corrected input returns
the independently recorded `PASS` quantities above; no kernel change was
needed.

The first immutable acceptance audit then found that the corrected output was
still not independently reproducible from the committed packet because its
receipt summarized only geometry, reinforcement, dowels, and anchorage. The
complete typed JSON fixture and executable replay above now bind every input
field and exact expected output; the repair changes evidence only.

The maintained plans still projected D as a candidate or acceptance as the next
packet after D had merged. Their status was intentionally not reconciled inside
D before its exact integration receipt existed. This acceptance packet binds
the family to merged D, adds itself to the deterministic evidence chain, and
moves the next action to the separate decision-only
`INDIA-2-FOUNDATION-STRAP-G0` packet.

## Focused acceptance gates

- All 84 combined G0/A-D analysis, strength, public-workflow, and transport
  tests pass, including the frozen benchmark, valid failures, and every
  maintained fail-closed boundary.
- The 339-test combined/public-contract selection passes, including public
  export, JSON serialization, OpenAPI, capability, semantic, deterministic
  manifest, clause data, traceability, and API-manifest checks.
- The deterministic manifest remains current at 12 supported and 9 held
  families; all 80 endpoints have direct tests and actionable cross-layer
  parity remains 100 percent.
- Architecture reports 0 violations across 193 files. Import validation reports
  0 broken imports across 635 Python files and 2,018 internal imports. All 1,258
  internal links and touched indexes pass.
- Black, Ruff, and focused mypy pass for the two touched Python files. Source
  binding, token efficiency, and the 10/10 quick repository gate pass.
- An independent exact-head audit and all applicable hosted PR checks must pass
  before this acceptance receipt can enter `main` unchanged.

Using the accepted cadence: focused gates run for every packet, with the broad
Python suite and full 30-check repository gate only at the final INDIA-2
integration boundary unless a confirmed repository-wide failure forces them
earlier. The next packet is decision-only `INDIA-2-FOUNDATION-STRAP-G0`; no
strap-footing implementation is authorized by this receipt.
