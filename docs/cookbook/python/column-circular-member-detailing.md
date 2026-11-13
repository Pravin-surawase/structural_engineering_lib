---
owner: Main Agent
status: active
last_updated: 2026-11-13
doc_type: guide
complexity: advanced
tags: [column, circular, detailing, bbs, is456]
---

# Check circular column member quantities

Use `column.load_circular_column_detailing` and
`column.check_circular_column_detailing` for a short braced circular
member with a regular cage and continuous straight bars. Supply current
signed compression and bending rows, zero shear, and the checked end
development basis. Rings use an approved closure and cut register.
Spirals use the body pitch and actual extra turns and pitches at both ends.

```bash
python circular_column_detailing.py --reference library-029-col07-circular-member.json \
  --case tied --output-dir tied
python circular_column_detailing.py --reference library-029-col07-circular-member.json \
  --case spiral --output-dir spiral
```

Use the [example script](../../../Python/examples/circular_column_detailing.py)
and [frozen cases](../../verification/library-029-col07-circular-member.json)
with the matching 0.29 candidate. The Ø450 member contains eight Ø20
bars. Each is 5,000 mm long including the two straight projections.
The tied case places 20 Ø10 rings. The spiral case uses one continuous
Ø10 bar. The cut sums the centreline lengths of 47 body turns and
1.5 anchorage turns at each end. The
[independent replay](../../verification/check_library_029_col07_circular_reference.py)
verifies the quantities and theoretical steel mass of 113.196 kg for
the tied case and 133.557 kg for the spiral case.

Each accepted output carries the same member and detail identity. The
report preserves the individual signed action rows. The SVG shows the
section and a review projection of the checked transverse arrangement.
The BBS is withheld for a stale ring cut register, missing spiral pitch
or crowded turns. Circular shear, physical splices, seismic confinement,
slenderness and professional approval require separate checks.
