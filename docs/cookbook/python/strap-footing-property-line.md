---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: intermediate
tags: [canonical-api, family-facades, lib-pro-012-r0]
---

# Strap Footing Property Line

Journey: `is456.strap-footing.property-line/v1`
Request: `property-line-strap-footing-input/v1`
Result: `family-design-result/v1 + structural-result-envelope/v2`
Errors: `input-issue/v1 + structural-problem/v1`

This recipe constructs caller-supplied data and delegates to the maintained
calculation owner. It does not infer loads, geometry, topology, soil data,
evidence, review inputs, or professional acceptance.

## Copy-paste recipe

```python
import json

from structural_lib.design.is456 import strap_footing

payload = json.loads(
    r"""{
    "actions": {
        "allowable_gross_bearing_pressure_kn_per_m2": 250.0,
        "bearing_and_settlement_approved": true,
        "column_moments_present": false,
        "equal_uniform_pressure_approved": true,
        "factored_clear_strap_line_load_kn_per_m": 18.0,
        "factored_exterior_column_load_kn": 1538.34375,
        "factored_exterior_footing_carrier_kn_per_m2": 30.0,
        "factored_interior_column_load_kn": 2612.15625,
        "factored_interior_footing_carrier_kn_per_m2": 30.0,
        "footing_carrier_basis_approved": true,
        "horizontal_actions_present": false,
        "independently_factored_or_patterned_actions_present": false,
        "load_combination_approved": true,
        "load_pattern_compatible": true,
        "service_clear_strap_line_load_kn_per_m": 12.0,
        "service_exterior_column_load_kn": 1025.5625,
        "service_exterior_footing_carrier_kn_per_m2": 20.0,
        "service_interior_column_load_kn": 1741.4375,
        "service_interior_footing_carrier_kn_per_m2": 20.0,
        "strap_line_load_basis_approved": true,
        "uplift_or_load_reversal_present": false
    },
    "evidence_review": {
        "column_and_strap_transfer_verified": true,
        "construction_clearances_verified": true,
        "construction_verification_reference": "CONSTRUCTION-01",
        "detailing_basis_reference": "STRAP-F0-DETAILING",
        "durability_basis_reference": "STRAP-F0-DURABILITY",
        "exterior_footing_design_verified": true,
        "exterior_footing_verification_reference": "EXT-FOOTING-01",
        "footing_reinforcement_and_anchorage_verified": true,
        "interior_footing_design_verified": true,
        "interior_footing_verification_reference": "INT-FOOTING-01",
        "qualified_review_required": true,
        "supporting_areas_verified": true,
        "transfer_verification_reference": "TRANSFER-01"
    },
    "geometry_topology": {
        "analysis_method": "rigid_equal_pressure",
        "column_count": 2,
        "columns_and_strap_share_centerline": true,
        "columns_square": true,
        "exterior_column_center_x_mm": 400.0,
        "exterior_column_side_mm": 500.0,
        "exterior_footing_depth_mm": 700.0,
        "exterior_footing_length_mm": 2400.0,
        "exterior_footing_width_mm": 2500.0,
        "footing_count": 2,
        "footings_constant_depth": true,
        "footings_parallel": true,
        "footings_rectangular": true,
        "foundation_on_soil": true,
        "interior_column_center_x_mm": 6400.0,
        "interior_column_centered_on_footing": true,
        "interior_column_side_mm": 500.0,
        "interior_footing_depth_mm": 700.0,
        "interior_footing_length_mm": 2500.0,
        "interior_footing_width_mm": 3200.0,
        "openings_present": false,
        "pedestals_present": false,
        "pressure_model": "equal_uniform_net",
        "strap_centered_across_footings": true,
        "strap_effective_depth_mm": 850.0,
        "strap_overall_depth_mm": 950.0,
        "strap_soil_contact": false,
        "strap_straight_and_prismatic": true,
        "strap_width_mm": 500.0
    },
    "identity_source": {
        "bearing_settlement_basis_reference": "STRAP-F0-GEOTECH",
        "footing_carrier_basis_reference": "STRAP-F0-CARRIER",
        "geometry_basis_reference": "STRAP-F0-GEOMETRY",
        "identity": {
            "case_id": "STRAP-F0",
            "family_id": "strap_footing",
            "member_id": "STRAP-F0",
            "source_reference": "LIB-PRO-013-F0",
            "story": "F0"
        },
        "load_basis_reference": "STRAP-F0-LOAD",
        "load_pattern_basis_reference": "STRAP-F0-PATTERN",
        "material_basis_reference": "STRAP-F0-MATERIAL",
        "rigidity_basis_reference": "STRAP-F0-RIGIDITY",
        "strap_isolation_basis_reference": "STRAP-F0-ISOLATION",
        "strap_line_load_basis_reference": "STRAP-F0-LINE-LOAD"
    },
    "materials_reinforcement": {
        "available_bottom_anchorage_exterior_mm": 1200.0,
        "available_bottom_anchorage_interior_mm": 1200.0,
        "available_top_anchorage_exterior_mm": 1200.0,
        "available_top_anchorage_interior_mm": 1200.0,
        "bars_bundled": false,
        "bars_curtailed": false,
        "bars_spliced": false,
        "bottom_bar_count": 4,
        "bottom_bar_diameter_mm": 16,
        "durability_cover_basis_approved": true,
        "effective_depth_basis_approved": true,
        "maximum_aggregate_size_mm": 20.0,
        "nominal_cover_mm": 50.0,
        "reinforcement_schedule_approved": true,
        "required_nominal_cover_mm": 50.0,
        "side_face_bar_count_each_face": 4,
        "side_face_bar_diameter_mm": 12,
        "side_face_vertical_spacing_mm": 250.0,
        "steel_grade_nmm2": 500,
        "stirrup_diameter_mm": 10,
        "stirrup_leg_count": 2,
        "stirrup_spacing_mm": 250.0,
        "straight_anchorage": true,
        "strap_concrete_grade_nmm2": 30,
        "top_bar_count": 6,
        "top_bar_diameter_mm": 25,
        "uncoated_deformed_bars": true,
        "vertical_closed_stirrups": true
    }
}"""
)
request = strap_footing.load(payload)
result = strap_footing.design(request)

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
invalid_payload['geometry_topology']['strap_soil_contact'] = True

try:
    strap_footing.load(invalid_payload)
except InputContractError as error:
    print([issue.to_dict() for issue in error.issues])
```

## Compatibility and evidence

- Maintained calculation owner: `structural_lib.services.strap_footing_api.design_property_line_strap_footing_is456`
- Result consumer: `to_dict() -> finite JSON + structural-result-envelope/v2`
- Evidence class: independent arithmetic + wrapper parity
- Exact signatures, units, enums, field decisions, and status guidance:
  [family facade contracts](../../reference/family-facade-contracts.md)

This recipe ships in `structural-lib-is456===0.24.0` and remains subject to
qualified review. It is not professional approval, engineering-use approval,
construction-use approval, or Windows application acceptance.
