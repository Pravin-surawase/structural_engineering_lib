---
owner: Main Agent
status: active
last_updated: 2026-11-13
doc_type: guide
complexity: advanced
tags: [column, interaction, section, is456]
---

# Trace a signed column interaction slice

Use `column.load_interaction_slice` and `column.check_interaction_slice` to
trace signed `Mx` and `My` capacities at one supplied axial compression.
The API accepts solid rectangular and circular sections with explicit bar
centres and diameters. It returns each requested direction, the neutral-plane
angle and depth, the signed moments, and axial and transverse residuals.

## Run the worked example

Copy the [script](../../../Python/examples/column_interaction_slice.py) and
[frozen reference](../../verification/library-029-sec02-column-interaction.json)
to a working directory and use the matching 0.29 candidate.

```bash
python column_interaction_slice.py --reference library-029-sec02-column-interaction.json \
  --case rectangle --output-dir rectangle-slice
python column_interaction_slice.py --reference library-029-sec02-column-interaction.json \
  --case circle --output-dir circle-slice
python column_interaction_slice.py --reference library-029-sec02-column-interaction.json \
  --case above_compression_domain --output-dir held-slice
```

The examples use the COL02 300 × 400 mm rectangle and the COL05 Ø450 mm
circle with eight Ø20 bars at 500 kN compression. The
[independent replay](../../verification/check_library_029_sec02_reference.py)
uses rectangular strip and circular chord integration. Eight directions
include the four signed axes and the four diagonals. With 16 requested points,
the eight common directions retain the same solutions.

Measure coordinates from the left and top of the section bounding box.
The diagram angle advances from positive `Mx` toward positive `My`.
It describes the moment vector. The reported neutral-plane angle describes
the compression direction and can differ from the diagram angle.

The result includes gross area and centroidal inertias. Transformed properties
use the caller’s modular ratio and add the net equivalent area of each bar
after concrete displacement. The inertias and product of inertia refer to the
transformed centroid, with x increasing right and y increasing down.

A section PASS means the requested equilibrium points were resolved. A held
ray stays visible without a substituted capacity. The report and JSON
identify the same input. Cracked section properties, member stability,
restraint, and fabrication require their own checks.
