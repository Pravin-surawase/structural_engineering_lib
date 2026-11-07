---
owner: Main Agent
status: active
last_updated: 2026-11-07
doc_type: guide
complexity: intermediate
tags: [canonical-api, family-facades, lib-pro-012-r0]
---

# Column Supplied Steel Check

Journey: `is456.column.supplied-steel-check/v1`
Request: `column-supplied-steel-check-input/v1`
Result: `family-design-result/v1 + structural-result-envelope/v2`
Errors: `input-issue/v1 + structural-problem/v1`

This recipe constructs caller-supplied data and delegates to the maintained
calculation owner. It does not infer loads, geometry, topology, soil data,
evidence, review inputs, or professional acceptance.

## Copy-paste recipe

```python
import json

from structural_lib.design.is456 import column

request_json = r"""{
    "actions": {
        "m1x_signed_knm": 120.0,
        "m1y_signed_knm": 0.0,
        "m2x_signed_knm": 120.0,
        "m2y_signed_knm": 0.0,
        "mux_knm": 120.0,
        "muy_knm": 0.0,
        "pu_kn": 800.0
    },
    "geometry": {
        "D_mm": 450.0,
        "b_mm": 300.0,
        "braced": true,
        "end_condition": "FIXED_FIXED",
        "minimum_eccentricity_length_mm": 3000.0,
        "unsupported_length_mm": 3000.0
    },
    "identity": {
        "case_id": "COL-F0",
        "family_id": "column",
        "member_id": "COL-F0",
        "source_reference": "LIB-PRO-013-F0",
        "story": "F0"
    },
    "materials": {
        "fck_nmm2": 25.0,
        "fy_nmm2": 415.0
    },
    "reinforcement": {
        "reinforcement_centroid_depth_mm": 50.0,
        "supplied_steel_area_mm2": 2400.0
    }
}"""
request = column.load_json(request_json)
payload = request.model_dump(mode="json")
result = column.design(request)

print(result.intake_status)
print(result.calculation_status)
print(result.engineering_status)  # expected: PASS
print(json.dumps(result.to_dict(), allow_nan=False, sort_keys=True))
```

`PASS`, `FAIL`, and `HOLD` are engineering/review outcomes for valid intake.
They are not interchangeable with `InputContractError`.

The JSON loader accepts text or UTF-8 bytes (including a byte-order mark),
rejects duplicate fields and non-finite numbers, and preserves field issue
paths. For a saved request, use
`column.load_json(Path("request.json").read_bytes())` after importing
`Path` from `pathlib`. Existing Python mappings use `column.load`.

## Rejected-input example

```python
import copy

from structural_lib.core.errors import InputContractError

invalid_payload = copy.deepcopy(payload)
invalid_payload['geometry']['braced'] = 1

try:
    column.load(invalid_payload)
except InputContractError as error:
    print([issue.to_dict() for issue in error.issues])
```

## Python API

Typed request groups are exported from `structural_lib.design.is456.column` alongside the
operations below. Mapping inputs remain supported for JSON/HTTP callers.
This reference follows the current source; JSON loaders, newly added builders,
and group imports require its matching build rather than an older published wheel.

::: structural_lib.design.is456.column
    options:
      docstring_style: numpy
      show_root_heading: false
      show_signature_annotations: true
      members:
        - input
        - load
        - load_json
        - design
        - check
        - load_four_corner_member
        - check_four_corner_member
        - render_four_corner_member_html

## Compatibility and evidence

- Maintained calculation owner: `structural_lib.services.column_api.design_column_is456`
- Result consumer: `to_dict() -> finite JSON + structural-result-envelope/v2`
- Evidence class: independent arithmetic + wrapper parity + generated regression
- Exact signatures, units, enums, field decisions, and status guidance:
  [family facade contracts](../../reference/family-facade-contracts.md)

This recipe is verified against the current source build (package version
`0.26.0`), not the older published wheel with that version, and remains
subject to qualified review. It is not professional approval, engineering-use
approval, construction-use approval, or Windows application acceptance.

## Physical four-corner member workflow

Use `column.load_four_corner_member` and `column.check_four_corner_member`
for the ordinary short braced rectangle with four equal corner bars. The
request derives the steel area and two-face calculation depth from actual
diameters, cover and corner inset. Supply a single principal bending axis
with compression and a moment magnitude. The example checks x and y as
separate actions on the same physical cage.

From the repository root, install the current source in a Python 3.11 or
newer environment and run the example.

```bash
python -m pip install ./Python
python Python/examples/four_corner_column_member.py --output-dir column-output
```

The directory contains matching JSON and HTML for five cases. The passing
case is 300 × 400 mm, 3,000 mm unsupported length, fixed at both ends, with
M25 concrete and Fe415 longitudinal bars. Four Ø20 bars give 1,256.637 mm²
of steel. A closed Ø8 tie has 300 mm pitch, 16 mm internal bend radius,
135° hooks and 48 mm tails. The declared project schedule requires 40 mm
nominal cover, 16 mm internal bend radius and 20 mm aggregate.

| Case | Expected status | Main result |
|---|---|---|
| `axis_x` | PASS | 500 kN, 50 kN·m, utilization 0.5088 |
| `axis_y` | PASS | Same cage and separate y-axis action, utilization 0.6419 |
| `overload` | FAIL | Both actions multiplied by three |
| `insufficient_tie` | FAIL | Ø4 ties at 350 mm |
| `missing_tie` | HOLD | Actual tie omitted, strength remains unevaluated |

### Physical inputs and schema

Use `FourCornerColumnInputV1.model_json_schema()` to obtain the complete
versioned input schema. Load either a mapping, JSON text, UTF-8 bytes or
a typed request with `load_four_corner_member`. A request round-trips
through `model_dump_json()` and the same loader.

| Group | Required inputs |
|---|---|
| `identity` | Family and case IDs, with optional member and source identifiers |
| `geometry` | `b_mm`, `D_mm`, `unsupported_length_mm`, an end condition and `braced=true` |
| `actions` | Positive compression `pu_kn`, nonnegative `moment_knm`, `bending_axis="x"` or `"y"` |
| `materials` | `fck_nmm2` from 15 to 80 and `fy_nmm2` from 250 to 550 |
| `reinforcement` | Equal bar diameter, nominal cover to the tie, corner inset, aggregate size, project cover and bend-radius requirements, their reference, and the actual tie |
| `tie` | ID, diameter, spacing, internal bend radius, closed state, hook angle and hook tail length |

Supported restraints are `FIXED_FIXED`, `FIXED_HINGED` and
`HINGED_HINGED`. Their recommended Table 28 effective length is checked
against both physical section dimensions. A slender section receives HOLD.
The supplied project cover requirement accounts for the applicable exposure
and fire basis. The supported ordinary column minimum is also checked.

The bar centroid offset is
`nominal_cover + tie_diameter + longitudinal_diameter/2 + corner_inset`.
With 2 mm inset the example gives 60 mm, placing the bars at
(60,60), (240,60), (240,340) and (60,340) mm. An x-axis check projects
them onto depths 60 and 340 mm. A y-axis check projects onto 60 and 240 mm.
Each projected layer has two bars.

The inset matters at a rounded tie corner. Setting it to zero in this
example fails the whole-bar enclosure check. The calculation also checks
each physical face for the 300 mm peripheral bar-spacing limit, clear
spacing, 0.8–4% supported steel ratio, minimum Ø12 longitudinal bars,
tie diameter, tie pitch, closure, bend fit and the supported 135° hook
with at least six tie diameters of tail. The 16 mm internal bend minimum
in this example comes from its declared project schedule. The supported
hook continuation must also fit within the shortest straight tie leg
between the corner bend tangencies, which is 172 mm for this cage.

### Result and report

`result.to_dict()` contains the original request, input SHA-256,
`family-design-result/v1`, `structural-result-envelope/v2`, named checks,
physical bar records and the reused P–M owner result. Read
`engineering_status` and `issues` before consuming the strength.
Inadequate provision produces FAIL. A declared missing tie produces HOLD.
Malformed fields and unsupported topology raise `InputContractError`.

`column.render_four_corner_member_html(result)` renders the same request,
bars, tie, checks, status and hash. Every report carries the selected
principal-axis and cage scope, source references and qualified-review state.
Joint anchorage, splices, serviceability, seismic confinement and the project
fire assessment require their respective evidence.

The independent reference solves the integrated strain-plane section and
intersects the demand ray continuously. The reused member owner samples 201
points and rounds its output. Both directions agree within the frozen
comparison tolerances. [Independent fixture](../../verification/library-027-four-corner-column.json)
· [Reference replay](../../verification/check_library_027_four_corner_reference.py)
· [Runnable example](../../../Python/examples/four_corner_column_member.py)

```bash
python docs/verification/check_library_027_four_corner_reference.py
```
