---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: intermediate
tags: [canonical-api, family-facades, lib-pro-012-r0]
---

# Slab Two Way

Journey: `is456.slab.two-way/v1`
Request: `two-way-slab-input/v1`
Result: `family-design-result/v1 + structural-result-envelope/v2`
Errors: `input-issue/v1 + structural-problem/v1`

This recipe constructs caller-supplied data and delegates to the maintained
calculation owner. It does not infer loads, geometry, topology, soil data,
evidence, review inputs, or professional acceptance.

## Copy-paste recipe

```python
import json

from structural_lib.design.is456 import slab

payload = json.loads(
    r"""{
    "actions": {
        "factored_area_load_kn_per_m2": 15.5
    },
    "geometry": {
        "corner_lift_condition": "restrained",
        "d_x_mm": 135.0,
        "d_y_mm": 125.0,
        "thickness_mm": 160.0,
        "x_effective_span_mm": 4000.0,
        "x_max_edge": "continuous",
        "x_min_edge": "discontinuous",
        "y_effective_span_mm": 6000.0,
        "y_max_edge": "continuous",
        "y_min_edge": "discontinuous"
    },
    "identity": {
        "case_id": "SLAB-TW-F0",
        "family_id": "solid_slab",
        "member_id": "SLAB-TW-F0",
        "source_reference": "LIB-PRO-013-F0",
        "story": "F0"
    },
    "materials": {
        "fck_nmm2": 20.0,
        "fy_nmm2": 415.0
    },
    "reinforcement": {
        "edge_strip_bar_diameter_mm": 8.0,
        "edge_strip_bar_spacing_mm": 250.0,
        "torsion_bar_diameter_mm": 8.0,
        "torsion_bar_spacing_mm": 200.0,
        "x_negative_bar_diameter_mm": 10.0,
        "x_negative_bar_spacing_mm": 200.0,
        "x_positive_bar_diameter_mm": 10.0,
        "x_positive_bar_spacing_mm": 200.0,
        "y_negative_bar_diameter_mm": 8.0,
        "y_negative_bar_spacing_mm": 200.0,
        "y_positive_bar_diameter_mm": 8.0,
        "y_positive_bar_spacing_mm": 200.0
    },
    "serviceability_evidence": {
        "qualified_serviceability_acceptance_acknowledged": true,
        "qualified_serviceability_acceptance_reference": "review:F0",
        "reviewed_aggregate_modification_factor": 1.0,
        "reviewed_base_span_depth_limit": 30.0,
        "serviceability_limit_source_is_approved": true,
        "serviceability_limit_source_reference": "reviewed-limit:F0"
    }
}"""
)
request = slab.load_two_way(payload)
result = slab.design_two_way(request)

print(result.intake_status)
print(result.calculation_status)
print(result.engineering_status)  # expected: FAIL
print(json.dumps(result.to_dict(), allow_nan=False, sort_keys=True))
```

`PASS`, `FAIL`, and `HOLD` are engineering/review outcomes for valid intake.
They are not interchangeable with `InputContractError`.

## Rejected-input example

```python
import copy

from structural_lib.core.errors import InputContractError

invalid_payload = copy.deepcopy(payload)
invalid_payload['geometry']['corner_lift_condition'] = 'invented'

try:
    slab.load_two_way(invalid_payload)
except InputContractError as error:
    print([issue.to_dict() for issue in error.issues])
```

## Compatibility and evidence

- Maintained calculation owner: `structural_lib.services.slab_api.design_two_way_slab_panel_builtin_is456`
- Result consumer: `to_dict() -> finite JSON + structural-result-envelope/v2`
- Evidence class: normalized data + wrapper parity + generated regression
- Exact signatures, units, enums, field decisions, and status guidance:
  [family facade contracts](../../reference/family-facade-contracts.md)

This recipe ships in `structural-lib-is456===0.24.0` and remains subject to
qualified review. It is not professional approval, engineering-use approval,
construction-use approval, or Windows application acceptance.
