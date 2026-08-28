---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: intermediate
tags: [canonical-api, family-facades, lib-pro-012-r0]
---

# Deep Beam Simply Supported

Journey: `is456.deep-beam.simply-supported/v1`
Request: `simply-supported-deep-beam-input/v1`
Result: `family-design-result/v1 + structural-result-envelope/v2`
Errors: `input-issue/v1 + structural-problem/v1`

This recipe constructs caller-supplied data and delegates to the maintained
calculation owner. It does not infer loads, geometry, topology, soil data,
evidence, review inputs, or professional acceptance.

## Copy-paste recipe

```python
import json

from structural_lib.design.is456 import deep_beam

payload = json.loads(
    r"""{
    "actions": {
        "action_basis_reference": "DEEP-F0-ACTIONS",
        "factored_positive_moment_knm": 900.0
    },
    "evidence_review": {
        "bearing_nodal_zone_reference": "DEEP-F0-BEARING",
        "bearing_nodal_zone_verified": true,
        "qualified_review_required": true,
        "reinforcement_basis_reference": "DEEP-F0-REINFORCEMENT"
    },
    "geometry_topology": {
        "beam_width_mm": 300.0,
        "centre_to_centre_span_mm": 3000.0,
        "clear_span_mm": 2800.0,
        "dapped_ends_present": false,
        "hanging_action_required": false,
        "openings_present": false,
        "overall_depth_mm": 2000.0,
        "solid_rectangular_section": true,
        "support_type": "simply_supported",
        "top_loaded": true
    },
    "identity_source": {
        "geometry_basis_reference": "DEEP-F0-GEOMETRY",
        "identity": {
            "case_id": "DEEP-F0",
            "family_id": "deep_beam",
            "member_id": "DEEP-F0",
            "source_reference": "LIB-PRO-013-F0",
            "story": "F0"
        }
    },
    "materials_reinforcement": {
        "concrete_grade_nmm2": 30,
        "face_grid_count": 2,
        "furthest_main_bar_from_tension_face_mm": 250.0,
        "horizontal_side_bar_diameter_mm": 10.0,
        "horizontal_side_bar_spacing_mm": 250.0,
        "left_support_embedment_mm": 850.0,
        "main_bar_count": 4,
        "main_bar_diameter_mm": 22.0,
        "main_bar_splices_present": false,
        "main_bars_bundled": false,
        "main_bars_continuous_between_supports": true,
        "right_support_embedment_mm": 850.0,
        "steel_grade_nmm2": 500,
        "vertical_side_bar_diameter_mm": 10.0,
        "vertical_side_bar_spacing_mm": 300.0
    }
}"""
)
request = deep_beam.load(payload)
result = deep_beam.design(request)

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
invalid_payload['geometry_topology']['openings_present'] = True

try:
    deep_beam.load(invalid_payload)
except InputContractError as error:
    print([issue.to_dict() for issue in error.issues])
```

## Compatibility and evidence

- Maintained calculation owner: `structural_lib.services.deep_beam_api.design_simply_supported_deep_beam_is456`
- Result consumer: `to_dict() -> finite JSON + structural-result-envelope/v2`
- Evidence class: independent arithmetic + wrapper parity
- Exact signatures, units, enums, field decisions, and status guidance:
  [family facade contracts](../../reference/family-facade-contracts.md)

This recipe ships in `structural-lib-is456===0.24.0` and remains subject to
qualified review. It is not professional approval, engineering-use approval,
construction-use approval, or Windows application acceptance.
