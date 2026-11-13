---
owner: Main Agent
status: active
last_updated: 2026-11-13
doc_type: evidence
tags: [beam, column, etabs, import, verification]
---

# FLOW04 ETABS source review

Import qualification remains HOLD. The repository's building fixture contains
both member geometries and a synthetic beam envelope. The public archive below
contains genuine ETABS results for both element types. The reviewed force
tables cannot yet be tied to the same model revision with the required
concurrent case and station definitions.

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

For the next qualification replay, pin an ETABS export containing both
`Element Forces` tables, frame assignments and connectivity or explicit
axes, a combination definition table, units, and a model fingerprint.
Preserve the row's original combination and station identifiers. ETABS
provides the station and six concurrent action columns through its
[FrameForce API](https://docs.csiamerica.com/help-files/etabs-api-2016/html/87689f3e-4175-1627-618b-c4ebae5e89b5.htm).
The [ETABS analysis reference](https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf)
defines which combination types produce one result per station and which
produce envelopes.
