---
owner: Main Agent
status: active
last_updated: 2026-11-13
doc_type: guide
complexity: advanced
tags: [column, section, serviceability, is456]
---

# Resolve service stresses in a column section

Use `column.load_service_section` and `column.check_service_section` for one
supplied service action row on a solid rectangular or circular section. Enter actual bar
centres and diameters, concrete and steel elastic moduli, and the declared
concrete stress limit for the linear model.

## Run the worked example

Use the matching 0.29 candidate and copy the [example script](../../../Python/examples/column_service_section.py)
and [frozen reference](../../verification/library-029-sec03-column-service.json)
into a working directory.

```bash
python column_service_section.py --reference library-029-sec03-column-service.json \
  --case biaxial --output-dir column-service
python column_service_section.py --reference library-029-sec03-column-service.json \
  --case reflected --output-dir column-reflected
python column_service_section.py --reference library-029-sec03-column-service.json \
  --case outside_linear_range --output-dir column-held
```

For an application, load the complete request JSON and inspect the result.

```python
from pathlib import Path

from structural_lib.design.is456 import column

request = column.load_service_section(Path("column-request.json").read_text())
result = column.check_service_section(request)
section_state = result.calculation["section_state"]
Path("column-report.html").write_text(column.render_service_section_html(result))
```

The example uses the 450 × 550 mm COL03 section with twelve mixed Ø20/Ø16
bars. Its service row contains 300 kN compression and moments −40 and +25
kN·m. All moments use the gross centroid. Positive axial force means
compression. Positive `Mx` compresses the top and positive `My` compresses
the left when each acts alone. The drawing uses x right and y down from
the top-left corner.

The solver resolves one affine strain plane. Concrete carries only
compressive elastic stress. Steel carries both signs, with a point area at
each bar centre. The net bar force subtracts the concrete stress already
included at that position. The example gives peak concrete compression
of 4.7399 N/mm². Rotating all bars through 180° and reversing both moments
preserves that stress and rotates the compression region. The
[independent replay](../../verification/check_library_029_sec03_reference.py)
computes the same equilibrium by integrating vertical strips. The
`rectangle_cracked` and `circle_cracked` cases use the same physical
cages as the fixed-compression interaction slices, with their own signed
service moments. The circular calculation integrates the compressed
part of the circle using chords. Its drawing approximates the circular
edge with straight segments. Properties use the integrated chords.

JSON and the HTML drawing carry the same input identity. Read the
equilibrium table to compare applied actions with the resolved total.
The active transformed properties use the compressed concrete region
and the equivalent point area of each bar. Their axes pass through the
transformed centroid and remain parallel to the section axes.

PASS means equilibrium was found within the declared elastic range. HOLD
retains any calculated state as a diagnostic when concrete exceeds the
declared linear limit or steel reaches yield. The model covers one
section and omits tension stiffening, creep, crack-width limits, member
stability and reinforcement detailing. Member and detailing acceptance
remain `NOT_EVALUATED`.
