---
owner: Main Agent
status: active
last_updated: 2026-11-06
doc_type: guide
complexity: beginner
tags: [beam, section-capacity, python]
---

# Compare three supplied beam sections in Python

Run one example to calculate flexural and shear capacities for a singly
reinforced beam with mixed bar diameters, a doubly reinforced beam, and a
flanged beam with two tension layers. Download
[`beam_comparator_reference.py`](https://github.com/Pravin-surawase/structural_engineering_lib/blob/main/Python/examples/beam_comparator_reference.py)
from the source repository.

With Python 3.11 or newer, run these commands in a virtual environment from
the directory where you saved the script.

```bash
python -m pip install "structural-lib-is456==0.26.0"
python -m structural_lib install-preflight
python beam_comparator_reference.py
```

The script prints one JSON object keyed by case. It uses the base install
and takes all inputs from the script. All 21 values were checked against the
frozen targets in a fresh environment installed from the published 0.26.0 wheel.

## Follow the inputs through the two operations

Bar depths are measured from the top compression face in millimetres.
All cases have Fe415 longitudinal steel and two active vertical Ø8 Fe415
link legs at 150 mm spacing. The script uses the bar list in the first
rcdesign code block, which differs from the surrounding prose.
[Pinned rcdesign examples](https://github.com/satish-annigeri/rcdesign/blob/ec8fe94b71dc02b07f7d83d12d3a4ddb511dd360/docs/quickstart.rst)

| Case ID | Section and concrete | Bar layers from the top |
|---|---|---|
| `singly_reinforced_rectangular` | 230 × 450 mm, M20 | 415 mm: Ø20, Ø16, Ø20 |
| `doubly_reinforced_rectangular` | 230 × 450 mm, M20 | 2Ø16 at 35 mm and 3Ø16 at 415 mm |
| `flanged_two_tension_layers` | 300 × 475 mm web, 800 × 150 mm flange, M25 | 2Ø18 at 405 mm and 3Ø20 at 440 mm |

1. Call `structural_lib.beam.flexural_capacity` with the section, individual
   `BarPosition` values, and bottom tension face. The API solves the
   neutral-axis depth and returns the effective depth of the tension steel.
   The flanged section's neutral axis lies within the flange.
2. Call `structural_lib.beam.shear_capacity` with that effective depth and
   the calculated tension steel area. Use the web width and the links active
   on the vertical `V2` axis. The provided shear capacity is the sum of the
   concrete and link contributions subject to the Table 20 limit.
3. Read both `method_revision_ids` in the JSON before comparing values.
   The example uses `is456-flexural-capacity-wp01-v3` and
   `is456-shear-capacity-wp02-v1`.

The transverse bar positions are illustrative. The doubly reinforced
section uses 35 mm bar-center offsets. A separate member check with 25 mm
clear cover, Ø8 links, and Ø16 bars expects a 41 mm offset. That check
returns `HOLD` for the effective-depth mismatch and missing support width.
[Frozen references and scope](../../verification/library-027-comparator-reference.md)

## Compare the output

These are the StructLib targets rounded for display. The JSON keys include
the units and `pt_percent` is a percentage.

| Case | `xu_mm` | `d_mm` | `pt_percent` | `mu_knm` | `vuc_kn` | `vus_kn` | `shear_total_kn` |
|---|---:|---:|---:|---:|---:|---:|---:|
| Singly reinforced | 180.735608 | 415.000000 | 0.868916 | 101.489328 | 56.176131 | 100.420884 | 156.597015 |
| Doubly reinforced | 61.725604 | 415.000000 | 0.631939 | 83.642779 | 49.845945 | 100.420884 | 150.266829 |
| Flanged | 72.746082 | 427.727273 | 1.131107 | 208.028494 | 86.161252 | 103.500604 | 189.661856 |

For automated comparisons, read each `expected.structlib` row and
`acceptance.absolute_tolerances` from the fixture. Compare unrounded
values using absolute differences. The tolerances are 0.001 mm for `xu`,
0.00001 mm for `d`, 0.000001 percentage points for `pt`, 0.001 kN·m for
moment, and 0.001 kN for each shear value.
[Frozen JSON fixture](../../verification/library-027-comparator-reference.json)

## Why rcdesign gives different numbers

The two tools use the same bar depths and tension steel areas, so `d`
and `pt` agree. Three method choices account for the other differences.

| Quantity | StructLib | rcdesign 0.4.18 |
|---|---|---|
| Neutral axis and moment | Rounded concrete resultant of `0.36 fck b xu` acting at `0.42 xu` for these sections | Integrates the parabolic and rectangular regions of the concrete stress curve |
| Concrete shear | Interpolates between IS 456 Table 19 entries | Evaluates a continuous concrete shear formula |
| Link shear | Uses `0.87 fy` for these vertical Fe415 links | Uses `fy / 1.15` |

For example, the singly reinforced beam has 101.489328 kN·m moment and
156.597015 kN total shear in StructLib. rcdesign gives 101.806298 kN·m and
156.832577 kN. To reproduce both tools, compare each output with its own
method row. The three cases differ by at most 0.32% in moment and total shear.
[Independent references for both methods](../../verification/library-027-comparator-reference.md#calculation-basis)
· [rcdesign stress block](https://github.com/satish-annigeri/rcdesign/blob/ec8fe94b71dc02b07f7d83d12d3a4ddb511dd360/src/rcdesign/is456/stressblock.py)
· [rcdesign concrete shear](https://github.com/satish-annigeri/rcdesign/blob/ec8fe94b71dc02b07f7d83d12d3a4ddb511dd360/src/rcdesign/is456/concrete.py)
· [rcdesign reinforcement](https://github.com/satish-annigeri/rcdesign/blob/ec8fe94b71dc02b07f7d83d12d3a4ddb511dd360/src/rcdesign/is456/rebar.py)
