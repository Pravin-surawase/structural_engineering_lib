---
owner: Main Agent
status: active
last_updated: 2026-11-17
doc_type: evidence
tags: [beam, column, etabs, import, verification]
---

# FLOW04 ETABS source review

The Altair workshop supplies a matched native beam and column pair for the
21.0.0 intake. The source binding and limits are recorded below. Imported
project design remains on HOLD.

The [paired intake example](../cookbook/python/etabs-paired-forces.md) replays
synthetic beam and column rows in the reviewed native table layouts. Its
complete intake status describes the declared teaching inventory.

## Altair workshop database

The [Altair concrete design workshop](https://community.altair.com/discussion/62902/atcxaec-concrete-design-made-easier-workshop)
links a ZIP containing one Microsoft Access ACE database. The ZIP SHA-256
is `503d4e8abe0f60c186cb79bb5f6ad2e3273eb6ab397b569d40267117bc21f2e5`.
The database SHA-256 is
`4f5661c09f40f262cdc1972c3efa74ac1a061dfa09ebbe2383a3632293157199`.
A read-only table inspection using
[mdb-reader 3.2.0](https://github.com/andipaetzold/mdb-reader) returned 111
tables. `Program Control` identifies ETABS 21.0.0 and kip, ft, F.
`Project Information` contains a model name and a revision number.

The database contains 66,180 rows in `Element Forces - Beams` and 12,560 in
`Element Forces - Columns`. Both tables preserve `P`, `V2`, `V3`, `T`,
`M2`, `M3`, object station, analysis-element station and location.
Connectivity, local-axis assignments and the load combination definitions are
present. The export groups a combination's terms under its named first row,
with the type populated on that first row. The source review omits the
licence field and project contact fields.

The screened pair is `STORY25/B43` (object and element 684) and
`STORY25/C20` (object and element 651). Each is unmeshed and both connect
to joint 548. The endpoints and all six signed actions reproduce four
native rows per member across `SLS_Gravity` and `ULS_Gravity`. The beam
and column station lengths are 8,911.226755 and 4,572 mm. The largest
absolute native local M3 converts to −246.037048 kN·m on the beam and
−183.225995 kN·m on the column. The independent reference SHA-256 is
`d3d40b3835b59a2ef8b89db254f1a8b62bae69331af32d3af7e57b5e78bb22da`.
[CSI frame axes](https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/Local_Axes_Frames.htm) ·
[CSI analysis reference](https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf) ·
[NIST unit conversions](https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors)

The native project revision is `0`. Both force tables are in the same
hashed export. The screened tables provide no standalone analysis-run ID.
All six linear-static case definitions specify P-Delta. PROJECT02 still
requires an independent second-order design basis and stations appropriate
to its checks. The selected beam has two native end stations.

Both 21.0.0 tables include `Location`. The selected rows have a blank
location and identical object and element stations. The reference retains
the near-zero beam axial force and minor-axis values from the export.
Across the four beam rows their largest magnitudes are
`1.94e-14 kip` for `P`, `5.20e-19 kip` for `V3` and
`1.14e-15 kip-ft` for `M2`. The current exact-zero guard would hold
these rows even after recognising the layout. Before design use, specify
any numerical zero treatment, preserve all native values and test a
material nonzero component separately. Keep the existing 22.7.0 controls.

The [intake replay](../cookbook/python/etabs-paired-forces.md#replay-the-altair-etabs-2100-export)
checks missing and duplicate station rows, a changed capture identity,
an envelope definition, an ambiguous station location and changed I/J
orientation. The exact zero rule for 22.7.0 has its own regression.

The initial B43/C20 replay has endpoint-only beam rows. PROJECT01 needs
interior design stations as well as the project material and reinforcement
basis. Its companion source screen below includes a native interior pair.
PROJECT02 needs documented axis-specific slenderness and the torsion
transfer path with current support and receiving cages.

### Native interior station sides

Both gravity combinations contain interior rows for 539 Altair beam
objects. Fourteen of those objects each map to one analysis element.
All 28 interior station pairs on those unmeshed objects have separate
`Before` and `After` rows. The separate station-side intake replay uses B130 and its
connected column C1, object 23.

`STORY1/B130` (object and element 43) and `STORY1/B131` (object and
element 44) each have an assigned downward `SDL` load of 2.248089 kip
at half span. Their native shear jumps match that load at factors 1.0
and 1.2 in `SLS_Gravity` and `ULS_Gravity`, respectively. Both pairs
preserve moment and torque across the load. The independent check
reproduced 9.999998 kN and 11.999998 kN jumps from the source values.
Its receipt SHA-256 is
`288d439cfeca95253db59f6892dfd373dcfe087804f2bcdc6074a0d5cab16b10`.

The two beams meet at joint 94 at an included angle of 171.120435°.
All eight screened adjacent pairs with a column at each support are
noncollinear. Use these rows as an interior station-side reference.
PROJECT01 still needs a regular frame with adequate station coverage and
a verified design and reinforcement basis. The database lists ACI 318-08
as its concrete frame design code. The geometry screen also found zero
rectangular columns with physical length divided by their smaller side
above 12 among 496 checked objects. PROJECT02 needs independently
supported effective lengths and receiving reinforcement for equilibrium
torsion.

## Public archive

[Balcı, Seismic Performance of Reinforced Concrete Frame Systems for Airfield Structures, V03](https://zenodo.org/records/20662171)
lists the ETABS models and `04_LINEAR.rar` with MD5
`00e24209808fd6fe883a3817738a1d20`. The review read selected files using
byte ranges. The hashes below identify the extracted files. The full
archive checksum was not verified.

- `01_LINEER/UYB-AAD-RC-LayeredSlab.e2k` identifies ETABS 22.7.0,
  the `RF/(+24.00)` story, and section assignments for both B1 and C1.
  The model defines `DSG2. 1.4G+1.6Q` as Linear Add.
  SHA-256 `19c41cb1de0f98f6c0e76c010d70caddd35a33a622f0031b30b3ddaa547fdd46`.
- `06_RC_Kolon_Eksenel_Yuk_Kontrolu1.4g1.6q-etabsv34.xlsx` contains
  `Element Forces - Columns` and `Frame Assignments - Summary`. The
  former has signed P, V2, V3, T, M2 and M3, stations in m, forces in kN
  and moments in kN·m. Rows 4–6 contain C1 at that story, unique name 109,
  for the exact DSG2 case. SHA-256
  `f38b1700cfacd41ec25c26c751e8cf031e2e5a39b5d26fcb4188715407502420`.
- The companion beam selection workbook contains `Design Forces - Beams`
  for B1, unique name 145, at the same story. Its design combinations use
  suffixed IDs such as `DSG2. 1.4G+1.6Q-1`. A separate
  `Element Forces - Beams` sheet in the same workbook contains
  six-component station rows for a different roof level and different
  combination names. That sheet supplies no B1 force row at
  `RF/(+24.00)` under the exact DSG2 case. The shared strings and both
  sheets were inspected from ZIP entries recovered from the workbook.

The numerical column rows and the shape/section labels support a candidate
source mapping. Evidence is still needed for the design-combination
suffixes, the beam station and element mapping, the local axes, and the
model revision that produced both exports. The public listing supplied
no redistribution terms for repackaging its workbooks. The fixture
remains outside the tracked repository.

## Other published examples checked

- Bentley's [STAAD.Pro tutorial 1 output](https://docs.bentley.com/LiveContent/web/STAAD.Pro-v2026.0.1/Help/en/topics/Getting_Started/Tutorial%20Problem%201/c-stpst_TUT01_Viewing_the_output_file.html)
  includes one steel portal frame run. It contains the geometry, member
  offsets, local end actions for its beam and two columns, and a defined
  load combination. It can support an endpoint-only STAAD sign and unit
  test. The beam's offset and axial force require their own mapping and
  downstream scope checks.
- Bentley's [reinforced-concrete tutorial 2 output](https://docs.bentley.com/LiveContent/web/STAAD.Pro-v2025.0.0/Help/en/topics/Getting_Started/Tutorial%20Problem%202/c-stpst_TUT02_Viewing_the_output_file.html)
  includes the input, second-order analysis and beam and column design
  summaries. A matching member-force table for cases 4 and 5 is still
  needed for the reinforced-concrete replay.
- The [ETABS dual-tower dataset](https://data.mendeley.com/datasets/b4tzn35bj9/1)
  provides joint, base, drift and time-history results. Its workbook has
  no beam and column station-force tables.

For the next qualification replay, pin an ETABS export containing both
`Element Forces` tables, frame assignments and connectivity or explicit
axes, a combination definition table, units, and a model fingerprint.
Preserve the row's original combination and station identifiers. ETABS
provides the station and six concurrent action columns through its
[FrameForce API](https://docs.csiamerica.com/help-files/etabs-api-2016/html/87689f3e-4175-1627-618b-c4ebae5e89b5.htm).
The [ETABS analysis reference](https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf)
defines which combination types produce one result per station and which
produce envelopes.
