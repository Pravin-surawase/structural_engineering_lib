---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: intermediate
tags: [canonical-api, family-facades, lib-pro-012-r0]
---

# Isolated Footing Concentric

Journey: `is456.isolated-footing.concentric/v1`
Request: `concentric-isolated-footing-input/v1`
Result: `family-design-result/v1 + structural-result-envelope/v2`
Errors: `input-issue/v1 + structural-problem/v1`

This recipe constructs caller-supplied data and delegates to the maintained
calculation owner. It does not infer loads, geometry, topology, soil data,
evidence, review inputs, or professional acceptance.

## Copy-paste recipe

```python
import json

from structural_lib.design.is456 import isolated_footing

payload = json.loads(
    r"""{
    "actions": {
        "allowable_soil_pressure_kpa": 200.0,
        "factored_axial_load_kn": 1200.0,
        "service_axial_load_kn": 800.0
    },
    "evidence_review": {
        "allowable_soil_pressure_is_externally_approved": true,
        "cover_exposure_basis": "approved severe footing schedule",
        "cover_exposure_basis_is_approved": true,
        "effective_supporting_area_basis": "largest_frustum_1v_2h",
        "effective_supporting_area_is_approved": true,
        "effective_supporting_area_mm2": 640000.0,
        "effective_supporting_area_origin": "provided",
        "qualified_review_required": true
    },
    "geometry_topology": {
        "column_length_mm": 400.0,
        "column_width_mm": 400.0,
        "effective_depth_offset_length_mm": 100.0,
        "effective_depth_offset_width_mm": 100.0,
        "footing_type": "ISOLATED_SQUARE",
        "maximum_overall_thickness_mm": 500.0,
        "minimum_overall_thickness_mm": 500.0,
        "thickness_increment_mm": 50.0
    },
    "identity_source": {
        "allowable_soil_pressure_origin": "verified",
        "allowable_soil_pressure_source_reference": "GEO-REPORT-001",
        "factored_load_combination_id": "ULS-GRAVITY-01",
        "identity": {
            "case_id": "ISO-F0",
            "family_id": "isolated_footing",
            "member_id": "ISO-F0",
            "source_reference": "LIB-PRO-013-F0",
            "story": "F0"
        },
        "service_load_basis": "includes_footing_self_weight_and_overburden",
        "service_load_combination_id": "SLS-GRAVITY-01",
        "service_load_origin": "provided"
    },
    "materials_reinforcement": {
        "available_dowel_development_length_into_column_mm": 1000.0,
        "available_dowel_development_length_into_footing_mm": 1000.0,
        "bottom_bar_end_arrangement": "straight",
        "column_concrete_fck_nmm2": 25.0,
        "column_longitudinal_bar_diameter_mm": 20.0,
        "dowel_bar_type": "deformed",
        "dowel_count": 4,
        "dowel_diameter_mm": 20.0,
        "footing_bottom_bar_type": "deformed",
        "footing_concrete_fck_nmm2": 25.0,
        "lower_bottom_bar_direction": "L",
        "nominal_cover_mm": 50.0,
        "nominal_max_aggregate_size_mm": 20.0,
        "permitted_bottom_bar_diameters_mm": [
            12,
            16,
            20,
            25,
            32
        ],
        "steel_fy_nmm2": 415.0,
        "upper_bottom_bar_direction": "B"
    }
}"""
)
request = isolated_footing.load(payload)
result = isolated_footing.design(request)

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
invalid_payload['evidence_review']['allowable_soil_pressure_is_externally_approved'] = False

try:
    isolated_footing.load(invalid_payload)
except InputContractError as error:
    print([issue.to_dict() for issue in error.issues])
```

## Compatibility and evidence

- Maintained calculation owner: `structural_lib.services.footing_api.design_concentric_isolated_footing_is456`
- Result consumer: `to_dict() -> finite JSON + structural-result-envelope/v2`
- Evidence class: independent arithmetic + wrapper parity + generated regression
- Exact signatures, units, enums, field decisions, and status guidance:
  [family facade contracts](../../reference/family-facade-contracts.md)

This recipe ships in `structural-lib-is456===0.24.0` and remains subject to
qualified review. It is not professional approval, engineering-use approval,
construction-use approval, or Windows application acceptance.
