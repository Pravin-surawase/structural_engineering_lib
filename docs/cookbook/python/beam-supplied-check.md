---
owner: Main Agent
status: active
last_updated: 2026-09-01
doc_type: guide
complexity: advanced
tags: [beam, supplied-reinforcement, canonical-api, lib-pro-015-d1]
---

# Supplied Beam Reinforcement Check V2

Request: `beam-supplied-check/v2`<br>
Result: `beam-supplied-check-result/v2`<br>
Errors: `input-issue/v1`, `structural-problem/v1`, and
`beam-supplied-check-error/v2`

The check consumes exact longitudinal layers, stirrup diameter/legs/spacing,
effective depth, materials, factored actions, selection constraints, support
basis, source references, identity, tension face, and correlation identity.

## Valid `PASS`

```python
import json

from structural_lib.design.is456 import beam

payload = json.loads(
    r"""{
    "actions": {
        "mu_knm": 100.0,
        "primary_tension_face": "BOTTOM",
        "vu_kn": 60.0
    },
    "correlation_id": "DOC-B1-ULS-1",
    "identity": {
        "case_id": "ULS-1",
        "member_id": "B1",
        "story": "L1"
    },
    "materials": {
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
        "fy_transverse_nmm2": 415.0
    },
    "reinforcement": {
        "bar_type": "deformed",
        "clear_cover_mm": 40.0,
        "compression_or_hanger": {
            "bars_per_layer": [
                2
            ],
            "diameter_mm": 12.0
        },
        "has_standard_bend_at_end": true,
        "has_standard_bend_at_start": true,
        "source_reference": "reviewed schedule B1-R1",
        "stirrup_diameter_mm": 8.0,
        "stirrup_legs": 2,
        "stirrup_spacing_mm": 150.0,
        "tension": {
            "bars_per_layer": [
                4
            ],
            "diameter_mm": 20.0
        }
    },
    "schema_version": "beam-supplied-check/v2",
    "section": {
        "D_mm": 500.0,
        "b_mm": 300.0,
        "effective_depth_basis": {
            "clear_cover_mm": 40.0,
            "stirrup_diameter_mm": 8.0,
            "tension_bar_diameter_mm": 20.0
        }
    },
    "selection": {
        "effective_depth_tolerance_mm": 1.0,
        "maximum_bars_per_layer": 8,
        "maximum_layers": 2,
        "nominal_max_aggregate_size_mm": 20.0,
        "objective": "min_area",
        "permitted_diameters_mm": [
            12.0,
            16.0,
            20.0,
            25.0
        ],
        "source_reference": "reviewed project bar catalogue P1"
    },
    "source_provenance": "reviewed supplied reinforcement schedule",
    "support": {
        "end_width_mm": 5000.0,
        "source_reference": "reviewed supports C1 and C2",
        "start_width_mm": 5000.0
    }
}"""
)
request = beam.load_supplied_check(payload)
result = beam.check_supplied(request)
assert result.status == "PASS"
assert result.effective_depth_resolution["d_mm"] == 442.0
```

## Rejected input

```python
import copy

from structural_lib.core.errors import InputContractError

invalid_payload = copy.deepcopy(payload)
del invalid_payload["section"]["effective_depth_basis"]

try:
    beam.load_supplied_check(invalid_payload)
except InputContractError as error:
    issue = error.issues[0]
    assert issue.code == "CROSS_FIELD_CONTRACT_INVALID"
    assert issue.path == "section"
```

## Engineering `FAIL`

```python
failed_payload = copy.deepcopy(payload)
failed_payload["actions"]["vu_kn"] = 200.0
failed_payload["reinforcement"]["stirrup_spacing_mm"] = 300.0
failed = beam.check_supplied(beam.load_supplied_check(failed_payload))
assert failed.status == "FAIL"
assert failed.shear.spacing_is_adequate is False
```

## Engineering `HOLD`

```python
held_payload = copy.deepcopy(payload)
held_payload["support"] = None
held = beam.check_supplied(beam.load_supplied_check(held_payload))
assert held.status == "HOLD"
assert held.result_envelope.overall_status.value == "HOLD"
```

`HOLD` is never an adequate Boolean. REST and WebSocket project the same result
dictionary and preserve `correlation_id`. See the
[V1 migration](../../migration/beam-supplied-check-v2.md) and
[beam facade reference](../../reference/beam-facade.md).

These examples execute from `structural-lib-is456==0.24.0`. Software
status is not professional, engineering-use, or construction-use approval.
