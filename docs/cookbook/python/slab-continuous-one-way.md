---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: intermediate
tags: [canonical-api, family-facades, lib-pro-012-r0]
---

# Slab Continuous One Way

Journey: `is456.slab.continuous-one-way/v1`
Request: `continuous-one-way-slab-input/v1`
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
        "factored_dead_and_fixed_imposed_load_kn_per_m2": 7.5,
        "factored_nonfixed_imposed_load_kn_per_m2": 2.5,
        "negative_location": "next_to_end_support_negative",
        "positive_location": "end_span_positive",
        "redistribution_applied": false,
        "shear_location": "end_support",
        "substantially_uniform_load_acknowledged": true
    },
    "geometry": {
        "effective_depth_mm": 130.0,
        "long_effective_span_mm": 7500.0,
        "maximum_span_variation_percent": 0.0,
        "number_of_spans": 3,
        "short_effective_span_mm": 3000.0,
        "strip_width_mm": 1000.0,
        "thickness_mm": 160.0,
        "uniform_cross_section_acknowledged": true
    },
    "identity": {
        "case_id": "SLAB-C-F0",
        "family_id": "solid_slab",
        "member_id": "SLAB-C-F0",
        "source_reference": "LIB-PRO-013-F0",
        "story": "F0"
    },
    "materials": {
        "fck_nmm2": 20.0,
        "fy_nmm2": 415.0
    },
    "reinforcement": {
        "distribution_bar_diameter_mm": 8.0,
        "distribution_bar_spacing_mm": 200.0,
        "negative_bar_diameter_mm": 10.0,
        "negative_bar_spacing_mm": 150.0,
        "positive_bar_diameter_mm": 10.0,
        "positive_bar_spacing_mm": 150.0
    },
    "serviceability_evidence": {
        "qualified_serviceability_acceptance_acknowledged": true,
        "qualified_serviceability_acceptance_reference": "review:F0",
        "reviewed_aggregate_modification_factor": 1.2,
        "reviewed_base_span_depth_limit": 20.0,
        "serviceability_limit_source_is_approved": true,
        "serviceability_limit_source_reference": "reviewed-limit:F0"
    }
}"""
)
request = slab.load_continuous_one_way(payload)
result = slab.design_continuous_one_way(request)

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
invalid_payload['actions']['redistribution_applied'] = True

try:
    slab.load_continuous_one_way(invalid_payload)
except InputContractError as error:
    print([issue.to_dict() for issue in error.issues])
```

## Compatibility and evidence

- Maintained calculation owner: `structural_lib.services.slab_api.design_continuous_one_way_slab_builtin_is456`
- Result consumer: `to_dict() -> finite JSON + structural-result-envelope/v2`
- Evidence class: normalized data + wrapper parity + generated regression
- Exact signatures, units, enums, field decisions, and status guidance:
  [family facade contracts](../../reference/family-facade-contracts.md)

This recipe is verified against `structural-lib-is456==0.24.0` and remains
subject to qualified review. It is not professional approval, engineering-use
approval, construction-use approval, or Windows application acceptance.
