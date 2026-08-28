---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: intermediate
tags: [canonical-api, family-facades, lib-pro-012-r0]
---

# Wall Braced Axial

Journey: `is456.wall.braced-axial/v1`
Request: `braced-wall-input/v1`
Result: `family-design-result/v1 + structural-result-envelope/v2`
Errors: `input-issue/v1 + structural-problem/v1`

This recipe constructs caller-supplied data and delegates to the maintained
calculation owner. It does not infer loads, geometry, topology, soil data,
evidence, review inputs, or professional acceptance.

## Copy-paste recipe

```python
import json

from structural_lib.design.is456 import wall

payload = json.loads(
    r"""{
    "actions": {
        "action_basis_reference": "WALL-F0-ACTIONS",
        "factored_axial_load_kn": 2000.0,
        "supplied_eccentricity_mm": 0.0
    },
    "evidence_review": {
        "qualified_review_required": true,
        "reinforcement_basis_reference": "WALL-F0-REINFORCEMENT"
    },
    "geometry_topology": {
        "bracing_elements_in_two_directions": true,
        "diaphragm_transfer_confirmed": true,
        "lateral_connection_capacity_confirmed": true,
        "lateral_forces_resisted_by_bracing_system": true,
        "lateral_restraint_spacing_mm": 4000.0,
        "rotation_restraint": "restrained_both_ends",
        "unsupported_height_mm": 3000.0,
        "wall_length_mm": 4000.0,
        "wall_thickness_mm": 150.0
    },
    "identity_source": {
        "bracing_basis_reference": "WALL-F0-BRACING",
        "identity": {
            "case_id": "WALL-F0",
            "family_id": "wall",
            "member_id": "WALL-F0",
            "source_reference": "LIB-PRO-013-F0",
            "story": "F0"
        }
    },
    "materials_reinforcement": {
        "concrete_grade_nmm2": 20,
        "horizontal_bar_diameter_mm": 10.0,
        "horizontal_bar_spacing_mm": 250.0,
        "reinforcement_kind": "deformed_415_or_greater",
        "vertical_bar_diameter_mm": 8.0,
        "vertical_bar_spacing_mm": 250.0
    }
}"""
)
request = wall.load(payload)
result = wall.design(request)

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
invalid_payload['geometry_topology']['wall_thickness_mm'] = '150'

try:
    wall.load(invalid_payload)
except InputContractError as error:
    print([issue.to_dict() for issue in error.issues])
```

## Compatibility and evidence

- Maintained calculation owner: `structural_lib.services.wall_api.design_braced_wall_is456`
- Result consumer: `to_dict() -> finite JSON + structural-result-envelope/v2`
- Evidence class: independent arithmetic + wrapper parity
- Exact signatures, units, enums, field decisions, and status guidance:
  [family facade contracts](../../reference/family-facade-contracts.md)

This recipe is verified against `structural-lib-is456==0.24.0` and remains
subject to qualified review. It is not professional approval, engineering-use
approval, construction-use approval, or Windows application acceptance.
