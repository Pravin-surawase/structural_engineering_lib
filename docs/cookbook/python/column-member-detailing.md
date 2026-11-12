---
owner: Main Agent
status: active
last_updated: 2026-11-12
doc_type: guide
---

# Check shear and detailing for a tied column

Use `column.load_column_member_detailing` and
`column.check_column_member_detailing` for an ordinary short braced
rectangular member with eight equal bars. The workflow checks section
strength and principal-plane shear at the supplied factored stations,
resolves the tie and cross-tie levels, and checks straight end development.
It also evaluates proposed compression laps. The BBS is available for
passing continuous-bar members with an approved transverse cut register.

## Run the worked example

Install the matching 0.29 candidate. Run `python -m structural_lib
install-preflight --json` to confirm its version and source. Copy the
[example script](../../../Python/examples/column_member_detailing.py) and
[frozen fixture](../../verification/library-029-col07-column-member.json)
to a working directory.

```bash
python column_member_detailing.py --reference library-029-col07-column-member.json \
  --case continuous --output-dir col07-continuous
python column_member_detailing.py --reference library-029-col07-column-member.json \
  --case shear_shortfall --output-dir col07-shear-fail
python column_member_detailing.py --reference library-029-col07-column-member.json \
  --case lap_numeric_pass --output-dir col07-lap-hold
```

Each run writes `result.json`, `report.html` and `member.svg`. The continuous
case also writes `bbs.csv`. The report, drawing and CSV carry the checked
input hash, member identifier and revisions. The SVG is a section and
elevation schematic, with proposed laps marked as such. The CSV uses the
approved transverse cut lengths from the request and calculates quantity,
total length and theoretical steel mass. Use a fresh directory for each
run. Use `--input` to supply a complete request JSON.

## Read the calculations

The example is a 300 × 400 mm, 3 m braced column with M25 concrete, eight
Ø20 Fe415 bars at 60 mm centres from the adjacent faces and an Ø8 hoop
plus two Ø8 links. Supply signed moments and shears together at each station.
Positive Mx compresses the top face and positive My compresses the left.
Vy uses the 400 mm overall depth and Vx the 300 mm overall depth.

1. U1 at 150 mm supplies 500 kN compression and 160 kN Vy. The 340 mm
   effective depth and two Ø8 hoop legs at 100 mm give **123.41 kN**
   steel resistance. The lowest Table 19 row, with an axial factor of
   1.5, gives **44.37 kN** concrete resistance. The 167.78 kN sum is below
   the 316.20 kN Table 20 limit. Governing utilization is **95.36%**.
   The calculation uses the lowest concrete row to avoid crediting
   unverified continuing tension steel. The open links restrain bars
   but receive no shear credit. The admitted vertical shear model
   also limits pitch to 0.75 times effective depth.
2. The hoop grid runs from 60 to 2940 mm. The end zones use 100 mm pitch
   and the field uses 140 mm. At shared boundaries the schedule counts
   one hoop, and the shear check uses the larger pitch. The grid gives
   **25 hoops and 25 links of each mark**. The open links sit 12 and 24 mm
   above each hoop. Use `zone_boundary` to see the larger field pitch
   govern, and `congested_links` for colliding link levels.
3. The unrounded straight tension development is **805.92 mm** from each
   face. The 850 mm projections meet that length on the supplied adjoining
   concrete basis. For a straight compression lap, the minimum is
   **644.73 mm**, the greater of compression development and 24 bar
   diameters. The 700 mm lap in the worked control meets length, location
   and pitch. Its physical splice partner paths, restraint and congestion
   remain **HOLD**. No BBS is issued for the spliced member. Use
   `lap_short`, `lap_bad_zone` or `lap_pitch` for numerical failures.
4. The continuous case has eight 4700 mm longitudinal cuts. Combined with
   the supplied transverse cut register, the BBS contains **83 pieces**,
   **88.850 m** of bar and **112.950 kg** theoretical mass.

## Use the Python API

```python
import json
from pathlib import Path

from structural_lib.design.is456 import column

fixture = json.loads(Path("library-029-col07-column-member.json").read_text())
request = column.load_column_member_detailing(fixture["cases"]["continuous"]["request"])
result = column.check_column_member_detailing(request)
print(result.engineering_status.value)
print(result.to_dict()["calculation"]["governing_shear"])
csv_text = column.render_column_member_bbs_csv(result)
```

Inspect `column.ColumnMemberDetailingInputV1.model_json_schema()` for
field names and limits. The caller supplies the applicable nonseismic basis,
current analysis revision, end details and tie placement criteria. For
compression laps, supply the approved low-stress window and pitch limit.
The check preserves a stale revision or missing mandatory evidence as HOLD.
The [independent replay](../../verification/check_library_029_col07_reference.py)
checks the cases without the library.

This profile covers the supplied stations and combinations of one short
tied eight-bar column. Coverage across the actual load envelope,
two-plane shear interaction, local splice assembly, adjoining joint or
support checks, slender and circular members, and seismic detailing
need separate verification.
