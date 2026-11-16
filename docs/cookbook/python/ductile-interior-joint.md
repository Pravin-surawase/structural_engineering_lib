---
owner: Main Agent
status: active
last_updated: 2026-11-16
doc_type: guide
tags: [column, beam, joint, is13920, detailing]
---

# Check a ductile interior joint

Use `structural_lib.design.is13920.joint` for a regular non-roof joint with
centred rectangular beams on four faces, a square column and straight through
beam bars. Supply the factored rows for X+, X−, Y+ and Y−, the column
inflection positions for the joint equilibrium, and the physical cage
dimensions. Coordinates and bar diameters are in mm. Actions are in kN or
kN·m, with column compression and downward beam reactions positive.

The check uses IS 13920:2016 with Amendments 1 and 2. The supplied actions
and stated applicability form the basis for this local check.
[BIS standard and amendments](https://standards.bis.gov.in/website/standard-details?encryptedId=eyJpdiI6Ik9yaTN1NC9ERTFvYVN5b1UwTG1ZUVE9PSIsInZhbHVlIjoiRHdrTlIzRloyOXg1WXFqMUN6ZTVBdz09IiwibWFjIjoiNmM5NTg5NzU4ZTIwOTNlMDkwMjcyZDg1MzM1MjEzMmNlNGYwMjc2MGVjMWFjYjM2ODdjYWRhOGQyNzE2MDU1NiIsInRhZyI6IiJ9)

```python
import json
from pathlib import Path

from structural_lib.design.is13920 import joint

fixture_path = Path("docs/verification/library-030-duct01-interior-joint.json")
specimen = json.loads(fixture_path.read_text(encoding="utf-8"))["request"]
request = joint.load_joint({
    **specimen,
    "applicability_reference": "Declared IS 13920 regular interior specimen.",
})
result = joint.check_joint(request)
report_html = joint.render_joint_html(result, current=request)
drawing_svg = joint.render_joint_svg(result, current=request)
bbs_csv = joint.render_joint_bbs_csv(result, current=request)
```

Set `applicability_reference` to the project decision for a supplied cage.
The calculation reports beam and column capacity shear, strong-column
weak-beam, joint shear, confinement, anchorage and cage fit. The HTML
report remains available for FAIL and HOLD. The SVG and BBS require PASS
and an explicit current request matching the result. The BBS covers
the joint hoop and the two cross-tie marks. The drawing also shows
the local beam continuations used in the anchorage check.

[JSON request and output example](../../../Python/examples/ductile_interior_joint.py) ·
[Independent reference](../../verification/library-030-duct01-interior-joint.json)

## Check the regular exterior joint

The exterior request describes a square column, a terminating X-minus beam
and two opposed through beams in Y. Use `ductile-exterior-joint/v1` as
`schema_version` and supply the declared applicability with the fixture
request. Provide the separate top and bottom X bends and straight tails,
the through-bar development in Y, and the overlapping hoops and exterior
cross-tie. The cross-tie has an inside 90° hook and an exterior 135° hook.

The four-direction result includes the governing vertical reaction and
capacity shear checks, joint shear, strong-column weak-beam,
termination development, full confinement and the fitted cage.
The SVG shows the actual return directions, bar positions and link
stations. The local BBS schedules the two closed hoops and cross-tie.
The X termination rows show the measured portion beyond the joint face
and carry blank order lengths and weights. The final cage fit and
compaction opening use the supplied tolerances. Site insertion
sequencing and temporary supports require separate project evidence.

The same Python example and export guard apply to the versioned exterior
request. [Independent exterior reference](../../verification/library-030-duct02-exterior-joint.json)
