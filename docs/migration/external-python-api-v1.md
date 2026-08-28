---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: intermediate
tags: [canonical-api, family-facades, lib-pro-012-r0]
---

# External Python API Migration: Family Facades v1

The canonical beginner namespace is:

```python
from structural_lib.design.is456 import beam
```

Existing `structural_lib.design_beam_is456`,
`structural_lib.services.api.design_beam_is456`, and
`structural_lib.api.design_beam_is456` signatures remain callable during the
Alpha migration. They now delegate to the same canonical service/calculation
owner and have no removal schedule.

R0 extends this construction/delegation pattern to every advertised family.
The compatibility owners remain callable with no removal schedule; new code
should use grouped `input(...)` or nested-mapping `load(...)` constructors so
units, identities, evidence, and topology decisions remain explicit.

The old flat signature lacks distinct member, storey, and span identities. New
code should build `BeamDesignInputV1` through `beam.input()` or load the nested
JSON contract through `beam.load()`. The canonical result preserves intake,
calculation, engineering, freshness, and final-review state separately.

| Old surface | Canonical target |
|---|---|
| `design_beam_is456(...)` | `beam.design(beam.input(...))` |
| `design_and_detail_beam_is456(...)` | `beam.design_and_detail(request, detailing_standard=...)` |
| direct `services.bbs.generate_bbs_from_detailing(...)` | `beam.bbs(canonical_result)` |
| `POST /api/v1/design/beam` | `POST /api/v2/design/beam` for new clients |
| generated client `design_beam` / `designBeam` | `design_beam_v2` / `designBeamV2` |

| Maintained compatibility owner | Canonical facade target |
|---|---|
| `services.canonical_beam.design` | `design.is456.beam.load` → `beam.design` |
| `codes.is456.beam.torsion.design_torsion` | `design.is456.torsion.load` → `torsion.design` |
| `services.column_api.design_column_is456` | `design.is456.column.load` → `column.design` / `column.check` |
| `services.slab_api.design_complete_one_way_slab_is456` | `design.is456.slab.load_one_way` → `slab.design_one_way` |
| `services.slab_api.design_continuous_one_way_slab_builtin_is456` | `slab.load_continuous_one_way` → `slab.design_continuous_one_way` |
| `services.slab_api.design_two_way_slab_panel_builtin_is456` | `slab.load_two_way` → `slab.design_two_way` |
| `services.wall_api.design_braced_wall_is456` | `design.is456.wall.load` → `wall.design` |
| `services.staircase_api.design_straight_flight_staircase_is456` | `design.is456.staircase.load` → `staircase.design` |
| `services.deep_beam_api.design_simply_supported_deep_beam_is456` | `design.is456.deep_beam.load` → `deep_beam.design` |
| `services.flat_slab_api.design_regular_interior_flat_slab_is456` | `design.is456.flat_slab.load` → `flat_slab.design` |
| `services.footing_api.design_concentric_isolated_footing_is456` | `design.is456.isolated_footing.load` → `isolated_footing.design` |
| `services.combined_footing_api.design_symmetric_combined_footing_is456` | `design.is456.combined_footing.load` → `combined_footing.design` |
| `services.strap_footing_api.design_property_line_strap_footing_is456` | `design.is456.strap_footing.load` → `strap_footing.design` |

The [family cookbook](../cookbook/python/family-facades.md) supplies the exact
payload for every row. The generated
[contract reference](../reference/family-facade-contracts.md) owns signatures,
units, enums, structured issue codes, and result/review status guidance.

Safety corrections are immediate: negative magnitude actions, booleans or
numeric strings in numeric fields, non-finite values, blank identities,
unknown fields, incomplete effective-depth bases, and invalid downstream
result types reject. Valid golden calculations remain numerically unchanged.

Do not convert `InputContractError` into an engineering `FAIL`, and do not
treat a valid engineering `FAIL` as invalid intake. BBS generation is
all-or-nothing and accepts only named canonical detailing result types.

This migration has no stable-API, engineering-use, professional-approval,
Windows-application-acceptance, or release-publication implication.
