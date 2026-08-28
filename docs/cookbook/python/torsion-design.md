---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: intermediate
tags: [canonical-api, family-facades, lib-pro-012-r0]
---

# Torsion Design

Journey: `is456.torsion.design/v1`
Request: `torsion-design-input/v1`
Result: `family-design-result/v1 + structural-result-envelope/v2`
Errors: `input-issue/v1 + structural-problem/v1`

This recipe constructs caller-supplied data and delegates to the maintained
calculation owner. It does not infer loads, geometry, topology, soil data,
evidence, review inputs, or professional acceptance.

## Copy-paste recipe

```python
import json

from structural_lib.design.is456 import torsion

payload = json.loads(
    r"""{
    "actions": {
        "mu_knm": 150.0,
        "tu_knm": 10.0,
        "vu_kn": 75.0
    },
    "geometry": {
        "D_mm": 500.0,
        "b_mm": 300.0,
        "clear_cover_mm": 25.0,
        "d_mm": 457.0
    },
    "identity": {
        "case_id": "TOR-F0",
        "family_id": "torsion",
        "member_id": "TOR-F0",
        "source_reference": "LIB-PRO-013-F0",
        "story": "F0"
    },
    "materials": {
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0
    },
    "reinforcement": {
        "stirrup_diameter_mm": 8.0,
        "tension_steel_percent": 1.0
    }
}"""
)
request = torsion.load(payload)
result = torsion.design(request)

print(result.intake_status)
print(result.calculation_status)
print(result.engineering_status)  # expected: PASS
print(json.dumps(result.to_dict(), allow_nan=False, sort_keys=True))
```

`PASS`, `FAIL`, and `HOLD` are engineering/review outcomes for valid intake.
They are not interchangeable with `InputContractError`.

## Rejected-input example

```python
import copy

from structural_lib.core.errors import InputContractError

invalid_payload = copy.deepcopy(payload)
invalid_payload['actions']['tu_knm'] = '10'

try:
    torsion.load(invalid_payload)
except InputContractError as error:
    print([issue.to_dict() for issue in error.issues])
```

## Compatibility and evidence

- Maintained calculation owner: `structural_lib.codes.is456.beam.torsion.design_torsion`
- Result consumer: `to_dict() -> finite JSON + structural-result-envelope/v2`
- Evidence class: independent arithmetic + wrapper parity
- Exact signatures, units, enums, field decisions, and status guidance:
  [family facade contracts](../../reference/family-facade-contracts.md)

This recipe ships in `structural-lib-is456===0.24.0` and remains subject to
qualified review. It is not professional approval, engineering-use approval,
construction-use approval, or Windows application acceptance.
