---
owner: Main Agent
status: active
last_updated: 2026-11-07
doc_type: guide
complexity: intermediate
tags: [column, section-response, python]
---

# Calculate a layered rectangular column section response

Use `column.layered_section_response` to evaluate a solid rectangular
section at a prescribed neutral-axis depth, inside or outside the section.
The example uses a
230 × 450 mm M20/Fe415 section with 3Ø16 at 50 mm, 2Ø16 at 225 mm
and 3Ø16 at 400 mm, measured from the top compression face.

From the repository root, run the example in a Python 3.11 or newer virtual
environment using the current source build.

```bash
python -m pip install ./Python
python -m structural_lib install-preflight
python Python/examples/layered_column_section.py
```

For an installed wheel containing this API, copy the example into a working
directory and run `python layered_column_section.py` with that environment's
interpreter. [Download the example](https://github.com/Pravin-surawase/structural_engineering_lib/blob/main/Python/examples/layered_column_section.py)

## Build and load a request

Use `column.load_layered_section` with a Python mapping, a validated request,
or JSON text or UTF-8 bytes. Use `ColumnSectionInputV1.model_json_schema()`
for the request schema and `ColumnSectionResponseV1.model_json_schema()`
for the response schema. Both models support `model_dump_json()`. Load
a saved request through the same loader. Use
`ColumnSectionResponseV1.model_validate_json()` to restore a response.

| Request field | Admitted input |
|---|---|
| `b_mm`, `D_mm` | Positive width and depth up to 2,000 mm |
| `xu_mm` | Positive depth measured from the top, with a finite ratio `D_mm / xu_mm` |
| `fck_nmm2`, `fy_nmm2` | Concrete 15–80 N/mm² and representative steel 250–550 N/mm² |
| `layers` | A nonempty list of diameter groups. Each row has `depth_from_top_mm`, integer `count` from 1 to 2,000, and `diameter_mm` from 1 to 2,000 mm |

Use separate rows at the same depth for mixed diameters. For example, two
Ø16 bars and one Ø20 bar at 50 mm are two groups, both with
`depth_from_top_mm=50`. The loader checks that each bar diameter fits between
the depth faces, all diameters at the same depth fit within the width, and
total bar area is below gross section area. Each response row follows the
same group order as the request.
Invalid values, unknown fields and duplicate JSON keys raise
`InputContractError` with structured issues.

## Read the section results

`axial_kn` is positive in compression. `centroid_moment_knm` is about the
axis through the section centroid parallel to the width. A compression
force above the centroid contributes positive moment. Each diameter group
contributes steel force less the concrete force displaced at its depth.
With the neutral axis inside the section, steel on the far side can be in
tension and its displaced concrete stress is zero.

| Neutral-axis depth | Top strain | Far-face strain | Axial force (kN) | Centroidal moment (kN·m) |
|---|---:|---:|---:|---:|
| 900 mm | 0.002545455 | 0.001272727 | +1,394.806807 | +9.955790 |
| 450 mm, equal to section depth | 0.003500000 | 0 | +1,124.900363 | +56.942945 |
| 300 mm, partial compression | 0.003500000 | −0.001750000 | +633.823982 | +110.974614 |
| 900 mm, mixed diameters at 50 mm | 0.002545455 | 0.001272727 | +1,432.527185 | +16.556856 |

The independent references use absolute tolerances of 0.001 kN and
0.001 kN·m. At the full-depth boundary the far face has zero strain.
At 900 mm, the whole section is in compression. The output includes gross
concrete and net layer contributions, the original request, and method
`IS456_FIG21_INTEGRATED_V1__STEEL_FIG23_GS115_V1`.
[Frozen 900 mm reference](../../verification/library-027-comparator-reference.md#expected-values-and-acceptance)
· [Boundary fixture](../../verification/library-027-column-section-boundary.json)
· [Partial compression and mixed diameter fixtures](../../verification/library-027-column-section-extension.json)

The calculation evaluates the prescribed strain plane directly. It returns
`COMPLETED` with member and detailing acceptance both `NOT_EVALUATED`.
Member checks use the separate `column.check` workflow, with their own
geometry, actions, effective length and reinforcement contract.
[Column member cookbook](family-facades.md)
