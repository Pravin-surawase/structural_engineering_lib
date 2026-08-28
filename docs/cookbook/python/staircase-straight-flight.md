---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: intermediate
tags: [canonical-api, family-facades, lib-pro-012-r0]
---

# Staircase Straight Flight

Journey: `is456.staircase.straight-flight/v1`
Request: `straight-flight-staircase-input/v1`
Result: `family-design-result/v1 + structural-result-envelope/v2`
Errors: `input-issue/v1 + structural-problem/v1`

This recipe constructs caller-supplied data and delegates to the maintained
calculation owner. It does not infer loads, geometry, topology, soil data,
evidence, review inputs, or professional acceptance.

## Copy-paste recipe

```python
import json

from structural_lib.design.is456 import staircase

payload = json.loads(
    r"""{
    "actions": {
        "concrete_unit_weight_kn_per_m3": 25.0,
        "flight_superimposed_service_load_kn_per_m2": 6.0,
        "lower_landing_load_share": 0.5,
        "lower_landing_superimposed_service_load_kn_per_m2": 6.0,
        "ultimate_load_factor": 1.5,
        "upper_landing_load_share": 1.0,
        "upper_landing_superimposed_service_load_kn_per_m2": 6.0
    },
    "evidence_review": {
        "qualified_review_required": true
    },
    "geometry_topology": {
        "flight_width_mm": 1500.0,
        "going_mm": 2700.0,
        "has_stringer_beams": false,
        "is_cast_in_situ_solid": true,
        "landing_thickness_mm": 200.0,
        "landings_collinear": true,
        "lower_landing_effective_length_mm": 750.0,
        "riser_mm": 160.0,
        "span_direction": "longitudinal",
        "support_case": "landings_span_with_flight",
        "tread_mm": 270.0,
        "upper_landing_effective_length_mm": 1650.0,
        "waist_thickness_mm": 250.0
    },
    "identity_source": {
        "identity": {
            "case_id": "STAIR-F0",
            "family_id": "stair",
            "member_id": "STAIR-F0",
            "source_reference": "LIB-PRO-013-F0",
            "story": "F0"
        },
        "load_basis_reference": "NPTEL-M9L20-EX9.1"
    },
    "materials_reinforcement": {
        "distribution_bar_diameter_mm": 8.0,
        "distribution_bar_spacing_mm": 160.0,
        "effective_depth_mm": 224.0,
        "fck_nmm2": 20.0,
        "fy_nmm2": 415.0,
        "main_bar_diameter_mm": 12.0,
        "main_bar_spacing_mm": 120.0
    }
}"""
)
request = staircase.load(payload)
result = staircase.design(request)

print(result.intake_status)
print(result.calculation_status)
print(result.engineering_status)  # expected: HOLD
print(json.dumps(result.to_dict(), allow_nan=False, sort_keys=True))
```

`PASS`, `FAIL`, and `HOLD` are engineering/review outcomes for valid intake.
They are not interchangeable with `InputContractError`.

## Rejected-input example

```python
import copy

from structural_lib.core.errors import InputContractError

invalid_payload = copy.deepcopy(payload)
invalid_payload['geometry_topology']['has_stringer_beams'] = True

try:
    staircase.load(invalid_payload)
except InputContractError as error:
    print([issue.to_dict() for issue in error.issues])
```

## Compatibility and evidence

- Maintained calculation owner: `structural_lib.services.staircase_api.design_straight_flight_staircase_is456`
- Result consumer: `to_dict() -> finite JSON + structural-result-envelope/v2`
- Evidence class: independent arithmetic + wrapper parity
- Exact signatures, units, enums, field decisions, and status guidance:
  [family facade contracts](../../reference/family-facade-contracts.md)

This recipe ships in `structural-lib-is456===0.24.0` and remains subject to
qualified review. It is not professional approval, engineering-use approval,
construction-use approval, or Windows application acceptance.
