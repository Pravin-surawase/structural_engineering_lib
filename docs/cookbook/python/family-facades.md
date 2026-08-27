---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: intermediate
tags: [canonical-api, family-facades, lib-pro-013-f0]
---

# Canonical IS 456 Family Facades

F0 adds construction-only facades for the maintained torsion, column, slab,
wall, staircase, deep-beam, flat-slab, and footing owners. The existing beam
facade remains the reference vocabulary. No facade contains an engineering
formula or creates a topology, load, material, soil, evidence, or review input.

This is an Alpha contract for the exact accepted F0 artifact. It is not a
professional approval, engineering-use approval, Windows acceptance, or public
release claim.

## Common pattern

Every family accepts either grouped Python objects through `input(...)` or the
same nested JSON-compatible mapping through `load(...)`. Invalid intake raises
`InputContractError`; valid engineering inadequacy returns `FAIL`, and retained
review or scope escalation returns `HOLD`.

```python
from structural_lib.design.is456 import torsion

request = torsion.load(
    {
        "identity": {
            "family_id": "torsion",
            "case_id": "TOR-1",
            "member_id": "B1",
            "story": "GF",
            "source_reference": "analysis-envelope:ULS-1",
        },
        "geometry": {
            "b_mm": 300.0,
            "D_mm": 500.0,
            "d_mm": 457.0,
            "clear_cover_mm": 25.0,
        },
        "actions": {"tu_knm": 10.0, "vu_kn": 75.0, "mu_knm": 150.0},
        "materials": {"fck_nmm2": 25.0, "fy_nmm2": 500.0},
        "reinforcement": {
            "stirrup_diameter_mm": 8.0,
            "tension_steel_percent": 1.0,
        },
    }
)
result = torsion.design(request)

print(result.intake_status)       # VALID
print(result.calculation_status)  # COMPLETED
print(result.engineering_status)  # PASS or FAIL
```

The evidence-heavy families use exactly five required groups:
`identity_source`, `geometry_topology`, `actions`,
`materials_reinforcement`, and `evidence_review`. Required truth fields are
retained inside those groups.

## Frozen F0 journeys

| Journey | Facade operation | Valid recipe outcome |
|---|---|---|
| `is456.beam.design/v1` | `beam.load` → `beam.design` | `PASS` |
| `is456.torsion.design/v1` | `torsion.load` → `torsion.design` | `PASS` |
| `is456.column.supplied-steel-check/v1` | `column.load` → `column.design` | `PASS` |
| `is456.slab.one-way/v1` | `slab.load_one_way` → `slab.design_one_way` | `PASS` |
| `is456.slab.continuous-one-way/v1` | `slab.load_continuous_one_way` → `slab.design_continuous_one_way` | `PASS` |
| `is456.slab.two-way/v1` | `slab.load_two_way` → `slab.design_two_way` | `FAIL` |
| `is456.wall.braced-axial/v1` | `wall.load` → `wall.design` | `PASS` |
| `is456.staircase.straight-flight/v1` | `staircase.load` → `staircase.design` | `HOLD` |
| `is456.deep-beam.simply-supported/v1` | `deep_beam.load` → `deep_beam.design` | `PASS` |
| `is456.flat-slab.regular-interior/v1` | `flat_slab.load` → `flat_slab.design` | `PASS` |
| `is456.isolated-footing.concentric/v1` | `isolated_footing.load` → `isolated_footing.design` | `PASS` |
| `is456.combined-footing.symmetric/v1` | `combined_footing.load` → `combined_footing.design` | `PASS` |
| `is456.strap-footing.property-line/v1` | `strap_footing.load` → `strap_footing.design` | `PASS` |

The two non-PASS examples are intentional valid-input evidence: the selected
two-way supplied bars are inadequate, and the staircase retains its qualified
serviceability review state. Neither outcome is an intake failure.

## Executable recipes and schemas

The maintained verifier contains one complete valid recipe and one invalid
vector for every row above:

```bash
./scripts/python_runtime.sh scripts/verify_lib_pro_013_f0_family_artifact.py --current
./scripts/python_runtime.sh scripts/verify_lib_pro_013_f0_family_artifact.py --wheel dist/structural_lib_is456-*.whl
```

The second command installs the wheel into an isolated target and proves that
all imports originate from that installed artifact. Live validation schemas,
constructor names, compatibility owners, and evidence classes are generated
under `family_facade_workflows` in
`docs/reference/api-classification.json`.

The cross-standard capability authority still reports 13 supported families:
10 bounded IS 456 families plus three retained IS 13920 capabilities. F0 does
not add a new `design.is13920` namespace or change those calculation owners.
R0 owns the later split into one public cookbook page per family and the final
cumulative documentation dossier.
