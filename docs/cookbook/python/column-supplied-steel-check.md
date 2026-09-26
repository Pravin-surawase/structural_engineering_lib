---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: intermediate
tags: [canonical-api, family-facades, lib-pro-012-r0]
---

# Column Supplied Steel Check

Journey: `is456.column.supplied-steel-check/v1`
Request: `column-supplied-steel-check-input/v1`
Result: `family-design-result/v1 + structural-result-envelope/v2`
Errors: `input-issue/v1 + structural-problem/v1`

This recipe constructs caller-supplied data and delegates to the maintained
calculation owner. It does not infer loads, geometry, topology, soil data,
evidence, review inputs, or professional acceptance.

## Copy-paste recipe

```python
import json

from structural_lib.design.is456 import column

request_json = r"""{
    "actions": {
        "m1x_signed_knm": 120.0,
        "m1y_signed_knm": 0.0,
        "m2x_signed_knm": 120.0,
        "m2y_signed_knm": 0.0,
        "mux_knm": 120.0,
        "muy_knm": 0.0,
        "pu_kn": 800.0
    },
    "geometry": {
        "D_mm": 450.0,
        "b_mm": 300.0,
        "braced": true,
        "end_condition": "FIXED_FIXED",
        "minimum_eccentricity_length_mm": 3000.0,
        "unsupported_length_mm": 3000.0
    },
    "identity": {
        "case_id": "COL-F0",
        "family_id": "column",
        "member_id": "COL-F0",
        "source_reference": "LIB-PRO-013-F0",
        "story": "F0"
    },
    "materials": {
        "fck_nmm2": 25.0,
        "fy_nmm2": 415.0
    },
    "reinforcement": {
        "reinforcement_centroid_depth_mm": 50.0,
        "supplied_steel_area_mm2": 2400.0
    }
}"""
request = column.load_json(request_json)
payload = request.model_dump(mode="json")
result = column.design(request)

print(result.intake_status)
print(result.calculation_status)
print(result.engineering_status)  # expected: PASS
print(json.dumps(result.to_dict(), allow_nan=False, sort_keys=True))
```

`PASS`, `FAIL`, and `HOLD` are engineering/review outcomes for valid intake.
They are not interchangeable with `InputContractError`.

The JSON loader accepts text or UTF-8 bytes (including a byte-order mark),
rejects duplicate fields and non-finite numbers, and preserves field issue
paths. For a saved request, use
`column.load_json(Path("request.json").read_bytes())` after importing
`Path` from `pathlib`. Existing Python mappings use `column.load`.

## Rejected-input example

```python
import copy

from structural_lib.core.errors import InputContractError

invalid_payload = copy.deepcopy(payload)
invalid_payload['geometry']['braced'] = 1

try:
    column.load(invalid_payload)
except InputContractError as error:
    print([issue.to_dict() for issue in error.issues])
```

## Python API

Typed request groups are exported from `structural_lib.design.is456.column` alongside the
operations below. Mapping inputs remain supported for JSON/HTTP callers.
This reference follows the current source; JSON loaders, newly added builders,
and group imports require its matching build rather than an older published wheel.

::: structural_lib.design.is456.column
    options:
      docstring_style: numpy
      show_root_heading: false
      show_signature_annotations: true
      members:
        - input
        - load
        - load_json
        - design
        - check

## Compatibility and evidence

- Maintained calculation owner: `structural_lib.services.column_api.design_column_is456`
- Result consumer: `to_dict() -> finite JSON + structural-result-envelope/v2`
- Evidence class: independent arithmetic + wrapper parity + generated regression
- Exact signatures, units, enums, field decisions, and status guidance:
  [family facade contracts](../../reference/family-facade-contracts.md)

This recipe is verified against the current source build (package version
`0.24.0`), not the older published wheel with that version, and remains
subject to qualified review. It is not professional approval, engineering-use
approval, construction-use approval, or Windows application acceptance.
