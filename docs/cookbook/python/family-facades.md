---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: intermediate
tags: [canonical-api, family-facades, lib-pro-012-r0]
---

# Canonical IS 456 Family Facades

These 13 copy-paste journeys are generated from the frozen facade registry and
the exact-wheel recipe owner. Every page uses strict grouped intake, the common
structured error boundary, the maintained calculation owner, and finite JSON
result consumption.

| Journey | Recipe | Valid recipe outcome |
|---|---|---|
| `is456.beam.design/v1` | [Beam Design](beam-design.md) | `PASS` |
| `is456.torsion.design/v1` | [Torsion Design](torsion-design.md) | `PASS` |
| `is456.column.supplied-steel-check/v1` | [Column Supplied Steel Check](column-supplied-steel-check.md) | `PASS` |
| `is456.slab.one-way/v1` | [Slab One Way](slab-one-way.md) | `PASS` |
| `is456.slab.continuous-one-way/v1` | [Slab Continuous One Way](slab-continuous-one-way.md) | `PASS` |
| `is456.slab.two-way/v1` | [Slab Two Way](slab-two-way.md) | `FAIL` |
| `is456.wall.braced-axial/v1` | [Wall Braced Axial](wall-braced-axial.md) | `PASS` |
| `is456.staircase.straight-flight/v1` | [Staircase Straight Flight](staircase-straight-flight.md) | `HOLD` |
| `is456.deep-beam.simply-supported/v1` | [Deep Beam Simply Supported](deep-beam-simply-supported.md) | `PASS` |
| `is456.flat-slab.regular-interior/v1` | [Flat Slab Regular Interior](flat-slab-regular-interior.md) | `PASS` |
| `is456.isolated-footing.concentric/v1` | [Isolated Footing Concentric](isolated-footing-concentric.md) | `PASS` |
| `is456.combined-footing.symmetric/v1` | [Combined Footing Symmetric](combined-footing-symmetric.md) | `PASS` |
| `is456.strap-footing.property-line/v1` | [Strap Footing Property Line](strap-footing-property-line.md) | `PASS` |

The two non-PASS recipes are intentional valid-input evidence. An engineering
`FAIL` or review `HOLD` is not invalid intake.

See [family facade contracts](../../reference/family-facade-contracts.md) for
generated signatures, schema identities, units, enums, structured issues, and
status guidance. Replay all pages against an exact wheel with:

```bash
./scripts/python_runtime.sh scripts/verify_lib_pro_012_r0_external_preview.py --wheel dist/structural_lib_is456-*.whl
```

This external-preview candidate remains subject to qualified review. It is not
professional approval, Windows application acceptance, release authorization,
or publication.
