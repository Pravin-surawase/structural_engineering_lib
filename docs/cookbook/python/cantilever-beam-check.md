---
owner: Main Agent
status: active
last_updated: 2026-11-13
doc_type: guide
complexity: advanced
tags: [beam, cantilever, concurrent-actions, is456]
---

# Check a rectangular cantilever

Use `beam.load_cantilever` and `beam.check_cantilever` with actual face bars,
a fixed-support width and concurrent actions from the current analysis.
The Python check evaluates signed flexure, shear and straight development at
the fixed face.

## Run the worked example

Use a matching 0.29 candidate. Copy the [script](../../../Python/examples/cantilever_beam_check.py)
and [frozen reference](../../verification/library-029-beam02-cantilever.json)
into your working directory. Each run writes `result.json` and `report.html`
with the same input hash and revisions.

```bash
python cantilever_beam_check.py --reference library-029-beam02-cantilever.json \
  --case point_and_udl --output-dir cantilever-pass
python cantilever_beam_check.py --reference library-029-beam02-cantilever.json \
  --case short_anchorage --output-dir cantilever-fail
python cantilever_beam_check.py --reference library-029-beam02-cantilever.json \
  --case missing_side --output-dir cantilever-hold
```

Use `--input` for your own complete request JSON.

## Read the example

The specimen has a 2 m clear span and a 300 × 500 mm M25 section. It has
3Ø20 Fe415 top bars and 2Ø16 Fe415 bottom bars at 50 mm face offsets, with
two-leg Ø8 links at 250 mm. The example preserves the UDL and point-load
combinations as distinct rows.

| Physical station | UDL M / V | UDL plus point load M / V |
|---|---:|---:|
| Fixed face | −40 kN·m / −40 kN | −50 kN·m / −50 kN |
| 1000 mm, left side | −10 kN·m / −20 kN | −10 kN·m / −30 kN |
| 1000 mm, right side | −10 kN·m / −20 kN | −10 kN·m / −20 kN |
| Free end | 0 kN·m / 0 kN | 0 kN·m / 0 kN |

The point-load row at the fixed face governs hogging and shear. The
[independent replay](../../verification/check_library_029_beam02_reference.py)
gives **139.341 kN·m** flexural and **140.043 kN** shear resistance for the
top-tension section. The top bars have **850 mm** available for **805.915 mm**
required straight development. The short control leaves 750 mm and fails
anchorage while the local section checks still pass.

## Use the Python API

```python
import json
from pathlib import Path

from structural_lib.design.is456 import beam

fixture = json.loads(Path("library-029-beam02-cantilever.json").read_text())
request = beam.load_cantilever(fixture["cases"]["point_and_udl"]["request"])
result = beam.check_cantilever(request)
assert result.ultimate_status == "PASS"
assert result.governing_rows["hogging"] == "POINT:FIXED"
assert result.serviceability_status == "HOLD"
Path("cantilever.html").write_text(beam.render_cantilever_html(result), encoding="utf-8")
```

Use mm, kN and kN·m. Coordinates increase from the fixed face at zero
toward the free end. The support lies at negative coordinates. Negative
moment selects the top face in tension. Each ULS combination needs both ends
and an interior station. Supply distinct LEFT and RIGHT rows for each
declared discontinuity. Missing rows or straight paths hold the applicable
check. Duplicate station identities are rejected with a structured input error.

The profile covers ordinary prismatic rectangular beams with one layer per
face, two vertical link legs and uninterrupted straight bars. Serviceability
rows stay visible and hold for separate checks. Source-analysis completeness,
frame stability, torsion, seismic detailing, laps, curtailment and
fabrication schedules require their own evidence. The result requires
qualified review.
