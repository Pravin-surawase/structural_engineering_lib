---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: intermediate
tags: [canonical-api, family-facades, lib-pro-012-r0]
---

# Combined Footing Symmetric

Journey: `is456.combined-footing.symmetric/v1`
Request: `symmetric-combined-footing-input/v1`
Result: `family-design-result/v1 + structural-result-envelope/v2`
Errors: `input-issue/v1 + structural-problem/v1`

This recipe constructs caller-supplied data and delegates to the maintained
calculation owner. It does not infer loads, geometry, topology, soil data,
evidence, review inputs, or professional acceptance.

## Copy-paste recipe

```python
import json

from structural_lib.design.is456 import combined_footing

payload = json.loads(
    r"""{
    "actions": {
        "allowable_gross_bearing_pressure_kn_per_m2": 150.0,
        "bearing_and_settlement_approved": true,
        "column_moments_present": false,
        "distributed_carrier_cancellation_approved": true,
        "factored_axial_load_each_kn": 1350.0,
        "factored_uniform_carrier_kn_per_m2": 37.5,
        "horizontal_actions_present": false,
        "load_combination_approved": true,
        "pressure_uniformity_approved": true,
        "service_axial_load_each_kn": 900.0,
        "service_uniform_carrier_kn_per_m2": 25.0,
        "uplift_or_load_reversal_present": false
    },
    "evidence_review": {
        "detailing_basis_reference": "COMBINED-F0-DETAILING",
        "qualified_review_required": true,
        "transfer_basis_reference": "COMBINED-F0-TRANSFER"
    },
    "geometry_topology": {
        "analysis_method": "conventional_rigid",
        "column_count": 2,
        "column_side_mm": 500.0,
        "columns_centered_across_width": true,
        "columns_identical": true,
        "columns_square": true,
        "constant_depth": true,
        "effective_depth_mm": 750.0,
        "footing_length_mm": 6000.0,
        "footing_width_mm": 2500.0,
        "foundation_on_soil": true,
        "left_column_center_x_mm": 1000.0,
        "openings_present": false,
        "overall_depth_mm": 850.0,
        "pedestals_present": false,
        "pressure_model": "uniform",
        "right_column_center_x_mm": 5000.0,
        "rigid_footing_verified": true
    },
    "identity_source": {
        "bearing_settlement_basis_reference": "COMBINED-F0-BEARING",
        "cancellation_basis_reference": "COMBINED-F0-CANCELLATION",
        "geometry_basis_reference": "COMBINED-F0-GEOMETRY",
        "identity": {
            "case_id": "COMBINED-F0",
            "family_id": "combined_footing",
            "member_id": "COMBINED-F0",
            "source_reference": "LIB-PRO-013-F0",
            "story": "F0"
        },
        "load_basis_reference": "COMBINED-F0-LOAD",
        "material_basis_reference": "COMBINED-F0-MATERIAL",
        "rigidity_basis_reference": "COMBINED-F0-RIGIDITY"
    },
    "materials_reinforcement": {
        "aggregate_size_mm": 20.0,
        "available_bottom_longitudinal_anchorage_each_end_mm": 800.0,
        "available_dowel_development_into_column_mm": 800.0,
        "available_dowel_development_into_footing_mm": 800.0,
        "available_top_longitudinal_anchorage_each_end_mm": 800.0,
        "available_transverse_anchorage_each_edge_mm": 800.0,
        "bottom_longitudinal_diameter_mm": 16,
        "bottom_longitudinal_spacing_mm": 190.0,
        "column_concrete_grade_nmm2": 30,
        "column_longitudinal_bar_diameter_mm": 20,
        "dowel_count_each": 4,
        "dowel_diameter_mm": 20,
        "effective_depth_basis_approved": true,
        "effective_supporting_area_approved": true,
        "effective_supporting_area_basis": "largest_frustum_1v_2h",
        "effective_supporting_area_each_mm2": 250000.0,
        "footing_concrete_grade_nmm2": 30,
        "nominal_cover_mm": 50.0,
        "reinforcement_schedule_approved": true,
        "steel_grade_nmm2": 500,
        "straight_uncoated_deformed_bars": true,
        "top_longitudinal_diameter_mm": 16,
        "top_longitudinal_spacing_mm": 190.0,
        "transverse_diameter_mm": 12,
        "transverse_spacing_mm": 110.0,
        "uncoated_deformed_bars": true,
        "uncoated_deformed_dowels": true
    }
}"""
)
request = combined_footing.load(payload)
result = combined_footing.design(request)

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
invalid_payload['actions']['column_moments_present'] = True

try:
    combined_footing.load(invalid_payload)
except InputContractError as error:
    print([issue.to_dict() for issue in error.issues])
```

## Compatibility and evidence

- Maintained calculation owner: `structural_lib.services.combined_footing_api.design_symmetric_combined_footing_is456`
- Result consumer: `to_dict() -> finite JSON + structural-result-envelope/v2`
- Evidence class: independent arithmetic + wrapper parity
- Exact signatures, units, enums, field decisions, and status guidance:
  [family facade contracts](../../reference/family-facade-contracts.md)

This recipe is verified against `structural-lib-is456==0.24.0` and remains
subject to qualified review. It is not professional approval, engineering-use
approval, construction-use approval, or Windows application acceptance.
