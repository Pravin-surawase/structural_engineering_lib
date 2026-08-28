---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: intermediate
tags: [canonical-api, family-facades, lib-pro-012-r0]
---

# Flat Slab Regular Interior

Journey: `is456.flat-slab.regular-interior/v1`
Request: `regular-interior-flat-slab-input/v1`
Result: `family-design-result/v1 + structural-result-envelope/v2`
Errors: `input-issue/v1 + structural-problem/v1`

This recipe constructs caller-supplied data and delegates to the maintained
calculation owner. It does not infer loads, geometry, topology, soil data,
evidence, review inputs, or professional acceptance.

## Copy-paste recipe

```python
import json

from structural_lib.design.is456 import flat_slab

payload = json.loads(
    r"""{
    "actions": {
        "factored_support_reaction_kn": 702.0,
        "factored_uniform_load_kn_per_m2": 19.5,
        "identical_full_loading_on_represented_panels": true,
        "load_combination_approved": true,
        "patterned_loading_required": false,
        "self_weight_included": true,
        "service_dead_load_kn_per_m2": 9.0,
        "service_live_load_kn_per_m2": 4.0,
        "unbalanced_or_lateral_moment_transfer_present": false
    },
    "evidence_review": {
        "all_bottom_bars_continuous": true,
        "centred_concentric_reaction": true,
        "detailing_basis_reference": "FLAT-F0-DETAILING",
        "full_critical_perimeter_available": true,
        "no_punching_reinforcement_provided": true,
        "punching_basis_reference": "FLAT-F0-PUNCHING",
        "qualified_review_required": true,
        "serviceability_acceptance_acknowledged": true,
        "serviceability_acceptance_reference": "FLAT-F0-SERVICEABILITY",
        "splices_present": false,
        "straight_bars_only": true,
        "support_reaction_basis_reference": "FLAT-F0-REACTION"
    },
    "geometry_topology": {
        "all_spans_equal_x": true,
        "all_spans_equal_y": true,
        "analysis_method": "direct_design",
        "centre_to_centre_span_x_mm": 6000.0,
        "centre_to_centre_span_y_mm": 6000.0,
        "column_head_present": false,
        "column_width_x_mm": 500.0,
        "column_width_y_mm": 500.0,
        "columns_offset_from_grid": false,
        "conservative_effective_depth_mm": 260.0,
        "continuous_span_count_x": 3,
        "continuous_span_count_y": 3,
        "drop_present": false,
        "marginal_beam_or_wall_present": false,
        "openings_present": false,
        "overall_depth_mm": 300.0,
        "panel_location": "interior",
        "solid_slab": true
    },
    "identity_source": {
        "geometry_basis_reference": "FLAT-F0-GEOMETRY",
        "identity": {
            "case_id": "FLAT-F0",
            "family_id": "flat_slab",
            "member_id": "FLAT-F0",
            "source_reference": "LIB-PRO-013-F0",
            "story": "F0"
        },
        "load_basis_reference": "FLAT-F0-LOAD",
        "material_basis_reference": "FLAT-F0-MATERIAL"
    },
    "materials_reinforcement": {
        "concrete_grade_nmm2": 30,
        "steel_grade_nmm2": 500,
        "uncoated_deformed_bars": true,
        "x": {
            "column_strip_negative_bars": {
                "diameter_mm": 12.0,
                "spacing_mm": 160.0
            },
            "column_strip_positive_bars": {
                "diameter_mm": 10.0,
                "spacing_mm": 200.0
            },
            "middle_strip_negative_bars": {
                "diameter_mm": 10.0,
                "spacing_mm": 200.0
            },
            "middle_strip_positive_bars": {
                "diameter_mm": 10.0,
                "spacing_mm": 200.0
            },
            "support_top_extension_from_face_mm": 1650.0
        },
        "y": {
            "column_strip_negative_bars": {
                "diameter_mm": 12.0,
                "spacing_mm": 160.0
            },
            "column_strip_positive_bars": {
                "diameter_mm": 10.0,
                "spacing_mm": 200.0
            },
            "middle_strip_negative_bars": {
                "diameter_mm": 10.0,
                "spacing_mm": 200.0
            },
            "middle_strip_positive_bars": {
                "diameter_mm": 10.0,
                "spacing_mm": 200.0
            },
            "support_top_extension_from_face_mm": 1650.0
        }
    }
}"""
)
request = flat_slab.load(payload)
result = flat_slab.design(request)

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
    flat_slab.load(invalid_payload)
except InputContractError as error:
    print([issue.to_dict() for issue in error.issues])
```

## Compatibility and evidence

- Maintained calculation owner: `structural_lib.services.flat_slab_api.design_regular_interior_flat_slab_is456`
- Result consumer: `to_dict() -> finite JSON + structural-result-envelope/v2`
- Evidence class: normalized data + independent arithmetic + wrapper parity
- Exact signatures, units, enums, field decisions, and status guidance:
  [family facade contracts](../../reference/family-facade-contracts.md)

This Alpha recipe is not professional approval, engineering-use approval,
Windows application acceptance, a release authorization, or publication.
