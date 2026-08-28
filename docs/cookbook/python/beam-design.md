---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: intermediate
tags: [canonical-api, family-facades, lib-pro-012-r0]
---

# Beam Design

Journey: `is456.beam.design/v1`
Request: `beam-design-input/v1`
Result: `beam-design-result/v1 + structural-result-envelope/v2`
Errors: `input-issue/v1 + structural-problem/v1`

This recipe constructs caller-supplied data and delegates to the maintained
calculation owner. It does not infer loads, geometry, topology, soil data,
evidence, review inputs, or professional acceptance.

## Copy-paste recipe

```python
import json

from structural_lib.design.is456 import beam

payload = json.loads(
    r"""{
    "actions": {
        "mu_knm": 150.0,
        "tu_knm": 0.0,
        "vu_kn": 75.0
    },
    "calculation_basis": {
        "asv_mm2": 100.53096491487338,
        "d_dash_mm": 43.0
    },
    "identity": {
        "case_id": "B-F0",
        "member_id": "B-F0",
        "story": "F0"
    },
    "materials": {
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0
    },
    "section": {
        "D_mm": 500.0,
        "b_mm": 300.0,
        "d_mm": 457.0,
        "span_mm": 5000.0
    },
    "source_provenance": "LIB-PRO-013-F0"
}"""
)
request = beam.load(payload)
result = beam.design(request)

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
invalid_payload['actions']['mu_knm'] = -1.0

try:
    beam.load(invalid_payload)
except InputContractError as error:
    print([issue.to_dict() for issue in error.issues])
```

## Compatibility and evidence

- Maintained calculation owner: `structural_lib.services.canonical_beam.design`
- Result consumer: `to_dict() -> finite JSON + structural-result-envelope/v2`
- Evidence class: independent arithmetic + wrapper parity + generated regression
- Exact signatures, units, enums, field decisions, and status guidance:
  [family facade contracts](../../reference/family-facade-contracts.md)

This recipe ships in `structural-lib-is456===0.24.0` and remains subject to
qualified review. It is not professional approval, engineering-use approval,
construction-use approval, or Windows application acceptance.
