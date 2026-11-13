---
owner: Main Agent
status: active
last_updated: 2026-11-13
doc_type: guide
complexity: advanced
tags: [beam, flexure, shear, multilayer, is456]
---

# Check a signed beam section

Use `beam.load_section` and `beam.check_section` with concurrent action rows
at one physical section. Supply the actual longitudinal bar coordinates,
face and layer, the web dimensions and the vertical links. For a monolithic
flange, supply both overhangs, the flange thickness and the zero-moment
distance used for the effective-width check.

## Run the worked example

Copy the [script](../../../Python/examples/signed_beam_section_check.py)
and [reference](../../verification/library-029-beam03-beam04-sections.json)
and run them with the matching 0.29 candidate. Each evaluated case writes
`result.json` and `report.html` with the same input hash and revisions.

```bash
python signed_beam_section_check.py --reference library-029-beam03-beam04-sections.json \
  --case l --output-dir l-section
python signed_beam_section_check.py --reference library-029-beam03-beam04-sections.json \
  --case multilayer --output-dir layered-section
python signed_beam_section_check.py --reference library-029-beam03-beam04-sections.json \
  --case stale --output-dir section-hold
```

Use `--input` to supply your own complete request.

## Read the checked faces and layers

The T and L specimens have a 300 mm web and a 550 mm depth. For sagging the
effective flange widths are 1000 mm and 600 mm, respectively. The independent
sagging resistances are 217.134 and 211.863 kN·m. At −150 kN·m, each
specimen has top tension and bottom web compression. The hogging resistance
is 69.228 kN·m, and the hogging row fails. Web shear uses 300 mm in both
directions. The reflected L fixture keeps its distinct flange side and
reproduces the same strengths. T identity with one overhang fails intake.

The 300 × 600 mm M30 multilayer specimen has two bottom 3Ø25 layers at 520 mm
and 450 mm from the top, giving a tension centroid at 485 mm in sagging. The
equilibrium neutral axis is 283.488 mm, beyond the 237.167 mm limiting depth.
The sagging row fails despite resistance exceeding the supplied 200 kN·m.
Reducing the bottom bars to Ø20 brings the neutral axis to 178.303 mm and
passes the sagging row. The reversed −200 kN·m row still fails. The
[independent section replay](../../verification/check_library_029_beam_sections_reference.py)
calculates each bar’s strain and net force as well as the concrete resultant.

## Use the Python API

```python
import json
from pathlib import Path

from structural_lib.design.is456 import beam

fixture = json.loads(Path("library-029-beam03-beam04-sections.json").read_text())
request = beam.load_section(fixture["cases"]["l"]["request"])
result = beam.check_section(request)
assert result.effective_flange_width_mm == 600
assert {row.action.row_id: row.section_status for row in result.rows} == {
    "HOG:SECTION": "FAIL",
    "SAG:SECTION": "PASS",
}
Path("l-section.html").write_text(beam.render_section_html(result), encoding="utf-8")
```

Measure x from the left web edge and y from the section top. Use mm, kN and
kN·m. Number layers outward to inward on each face. The profile covers
web-local bars and monolithic T or L flanges. The report carries section
resistance and checked bar IDs. Member-wide continuity, fabrication schedules,
torsion and serviceability require separate checks.
