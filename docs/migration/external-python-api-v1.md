---
owner: Main Agent
status: active
last_updated: 2026-08-27
doc_type: guide
complexity: intermediate
tags: [canonical-api, beam, lib-pro-013-b0]
---

# External Python API Migration: Beam v1

The canonical beginner import is:

```python
from structural_lib.design.is456 import beam
```

Existing `structural_lib.design_beam_is456`,
`structural_lib.services.api.design_beam_is456`, and
`structural_lib.api.design_beam_is456` signatures remain callable during the
Alpha migration. They now delegate to the same canonical service/calculation
owner and have no removal schedule.

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

Safety corrections are immediate: negative magnitude actions, booleans or
numeric strings in numeric fields, non-finite values, blank identities,
unknown fields, incomplete effective-depth bases, and invalid downstream
result types reject. Valid golden calculations remain numerically unchanged.

Do not convert `InputContractError` into an engineering `FAIL`, and do not
treat a valid engineering `FAIL` as invalid intake. BBS generation is
all-or-nothing and accepts only named canonical detailing result types.
