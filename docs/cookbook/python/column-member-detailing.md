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
It evaluates proposed compression laps and checks one physical contact
splice layout. Passing continuous and supported spliced members can
produce a BBS with the required transverse cut data.

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
tied six- or eight-bar column. Coverage across the actual load envelope,
two-plane shear interaction, other splice assemblies, adjoining joint or
support checks, slender and circular members, and seismic detailing
need separate verification.

## Replay six-bar layouts and a tie revision

Use `--case six_bar_omit_x_face_midpoints` or
`--case six_bar_omit_y_face_midpoints` with the same example and reference.
Each cage has four corner bars, two face-midpoint bars, a closed hoop
and one cross-tie. The continuous cages schedule six straight 4,700 mm
longitudinal bars and 25 pieces of each transverse mark.

`six_bar_revised_pitch` reduces the field pitch from 140 to 120 mm under
detail revision D2. It produces 27 hoop and cross-tie levels.
`six_bar_stale_cut` uses that same edit with the D1 cut register and
withholds the schedule. `six_bar_unresolved_lap` retains the numeric
lap check and holds the physical splice and BBS.

## Replay a mixed positioned member

Use the same [example script](../../../Python/examples/column_member_detailing.py)
with the [mixed member reference](../../verification/library-029-col07-mixed-member.json).

```bash
python column_member_detailing.py --positioned --reference library-029-col07-mixed-member.json   --case mixed_continuous --output-dir mixed-member
```

In Python use `column.load_positioned_column_member_detailing` and
`column.check_column_member_detailing`. The 450 × 550 mm member has
four Ø20 corner bars, eight Ø16 bars, three actual cross-ties, and
23 hoop levels. The hoop cut comes from the current approved register.
The cross-tie cuts come from their checked straight and hook segments.
The [independent replay](../../verification/check_library_029_col07_mixed_reference.py)
gives 906.25 mm required full-tension development for Ø20 and
163.960 kg scheduled steel for the continuous case.

The supplied station actions are checked against the actual mixed cage.
Shear credits only two closed hoop legs. The section drawing and schedule
retain all actual bar identities. Run the `stale_register`, `short_anchor`
and `unresolved_splice` cases to see how the report withholds the BBS.
Mixed-cage splice assembly requires its own qualification.

## Replay a braced slender member

Use the [slender member fixture](../../verification/library-029-col07-slender-member.json)
and `column.load_slender_column_member_detailing` for a continuous
tied rectangle with supplied second-order actions.

```bash
python column_member_detailing.py --slender --reference library-029-col07-slender-member.json   --case slender --output-dir slender-member
```

The 6 m case binds the physical station actions to the independent COL04
second-order rows. MID governs at a utilization of about 0.6266. The checked
schedule includes eight Ø20 bars of 7,700 mm each and 52 hoop levels.
The [independent replay](../../verification/check_library_029_col07_slender_reference.py)
uses the frozen COL04 strength and independently computes the full-length
quantities. A stale analysis, disagreement between station rows or short
straight projection withholds the BBS.

The admitted slender profile has continuous bars, one supplied
second-order combination and zero shear. First-order member detailing,
slender member shear and physical splices require their own checks.

## Run a physical contact splice

Use the same example script with the
[contact splice fixture](../../verification/library-029-col07-contact-splice.json).
The first physical profile splices the two opposing side-midpoint bars of
the eight-bar cage. Supply a single compression lap group up to Ø25 and
its `contact_assembly`. This profile uses straight partners along the
same two side faces. The upper bar centres are one diameter towards the
bottom face. The lower and upper section checks use the appropriate
physical bar locations, and both eight-bar layouts are checked through
the overlap.

```bash
python column_member_detailing.py --reference library-029-col07-contact-splice.json \
  --case contact_splice --output-dir col07-contact
python column_member_detailing.py --reference library-029-col07-contact-splice.json \
  --case congested_longitudinal --output-dir col07-contact-fail
python column_member_detailing.py --reference library-029-col07-contact-splice.json \
  --case compression_basis --output-dir col07-contact-hold
```

1. The Ø20 partners contact at y = 200 and 220 mm. The **740 mm overlap**
   exceeds the **709.21 mm** minimum including the contact-pair allowance.
   The fixture includes a compression reference for the overlap. Each
   supplied in-lap row must also remain inside the gross-section elastic
   kern as an admission check.
2. The horizontal link surrounds both bars at each end of its run in the
   lap. Two quarter bends and a straight tangent form each return. The
   final bend is followed by an 8-diameter tail. The nine overlap links
   replace the ordinary horizontal links at those levels. The nearest
   links to the two lap ends lie 58 and 26 mm from the first end and 42
   and 42 mm from the second end, inside the profile's 80 mm limit.
3. The smallest gap between unrelated longitudinal bars is **70 mm**.
   The smallest link-to-bar clearance is **2 mm**. The checker tests the
   actual quarter arcs and tails and the clearances between transverse
   levels. The reported steel ratio at the lap includes all ten bars.
4. Each lower spliced piece is **2740 mm** and each upper piece is
   **2700 mm**. The **448.53 mm** overlap link uses its checked
   centreline, including arcs and tails. The supplied cut register
   contains the closed hoop. The checked links supply their own cuts.
   The spliced BBS contains **109 pieces**, **109.963 m** and **124.346 kg**.

The report and elevation identify the individual pieces. Section cuts
show the bars and link paths below, within and above the lap. Provide the
fabrication reference for the bend schedule and the interval compression
basis as part of the request. A lap with only station limits and bar IDs
remains HOLD. Cranked and other lap assemblies require their own verification. The C1/C2 corner case follows below. [Independent replay](../../verification/check_library_029_col07_splice_reference.py)

## Resolve the original C1/C2 corner lap

The [corner splice fixture](../../verification/library-029-col07-corner-splice.json)
starts from the numeric-only C1/C2 case and supplies a physical assembly.
It uses the same 300 × 400 mm section and Ø20 bars. The lower C1 and C2
centres are (60, 60) and (240, 60) mm from the left and top faces.
Their straight upper partners run at (60, 80) and (240, 80) mm. Each
pair touches over the overlap. The assembly adds `corner_link_id` and
`corner_link_offset_mm` to the contact splice input.

```bash
python column_member_detailing.py --reference library-029-col07-corner-splice.json \
  --case corner_splice --output-dir col07-corners
python column_member_detailing.py --reference library-029-col07-corner-splice.json \
  --case link_level_clash --output-dir col07-corner-clash
python column_member_detailing.py --reference library-029-col07-corner-splice.json \
  --case original_numeric_only --output-dir col07-original-hold
```

1. The original 700 mm overlap satisfied the base numerical check.
   The contact-pair allowance raises the required length to **709.21 mm**.
   The detailed case uses **740 mm** and supplies the verified compression
   basis for the lap interval. The in-lap action row is inside the gross
   section kern.
2. The two midpoint link series stay in place. The supplemental `CX`
   series restrains the lower and upper corner bars outside the overlap.
   Nine `CL` links enclose both corner partners inside it. Above the
   lap, `CX` mirrors about the shifted corner centres so its straight leg
   passes clear of the top midpoint bar. All links use checked quarter
   bends and 8-diameter tails.
3. The supplemental links sit 36 mm above each hoop. The smallest gap
   between transverse steel surfaces is **4 mm** and the end face cover
   after adding them is **30 mm**. The nearest corner links lie **29 and
   54 mm** from the first lap end and **22 and 61 mm** from the second.
4. The section check uses the actual upper corners above the lap and
   checks both eight-bar layouts inside it. The conservative effective
   depth for the Vy plane is **320 mm** from the start of the lap, compared
   with 340 mm below. The Vx plane retains 240 mm.
5. The checked BBS contains **142 pieces**, **123.445 m** of bar and
   **129.666 kg** of theoretical steel mass. Its corner link marks are
   24 × `CX` at 408.53 mm and 9 × `CL` at 448.53 mm. The front elevation
   separates C1 and C2 across the width. Three section cuts show the
   individual partners, their offset and the mirrored upper restraint.

The numeric-only case stays HOLD with no BBS. Corner links at an existing
link level fail the clash check. The profile covers one C1/C2 compression
group of straight equal bars up to Ø25. The fabrication and compression
references must apply to the supplied assembly. The
[independent replay](../../verification/check_library_029_col07_corner_reference.py)
derives the restraint stations, section capacities and schedule quantities.
