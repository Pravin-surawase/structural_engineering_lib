---
owner: Main Agent
status: active
last_updated: 2026-11-15
doc_type: guide
complexity: advanced
tags: [column, circular, detailing, bbs, is456]
---

# Check circular column member quantities and tied-member shear

Use `column.load_circular_column_detailing` and
`column.check_circular_column_detailing` for a short braced circular
member with a regular cage and continuous straight bars. Supply current signed
compression and bending rows and the checked end-development basis. Rings use
an approved closure and cut register. Spirals use the body pitch and actual
extra turns and pitches at both ends.

```bash
./scripts/python_runtime.sh Python/examples/circular_column_detailing.py \
  --reference docs/verification/library-029-col07-circular-member.json \
  --case tied --output-dir tied
./scripts/python_runtime.sh Python/examples/circular_column_detailing.py \
  --reference docs/verification/library-029-col07-circular-member.json \
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

## Tied circular shear replay

The 0.30 reference adds one declared single-plane, closed-ring shear basis to
the existing tied cage. U1 governs at −120 kN Vy with 188.09 kN resistance
and passes. The −210 kN row fails at `COLUMN.SHEAR_CAPACITY`.
The two HOLD controls use `COLUMN.COMBINED_SHEAR` for simultaneous `Vx` and `Vy` and
`COLUMN.CIRCULAR_MEMBER_BASIS_HELD` for a missing action-source reference.
Only the `PASS` case makes a checked drawing and BBS available.

```bash
./scripts/python_runtime.sh Python/examples/circular_column_detailing.py \
  --reference docs/verification/library-030-col07-circular-shear.json \
  --case single_plane_pass --output-dir circular-shear-pass
./scripts/python_runtime.sh Python/examples/circular_column_detailing.py \
  --reference docs/verification/library-030-col07-circular-shear.json \
  --case shear_capacity_fail
./scripts/python_runtime.sh Python/examples/circular_column_detailing.py \
  --reference docs/verification/library-030-col07-circular-shear.json \
  --case combined_planes_hold
./scripts/python_runtime.sh Python/examples/circular_column_detailing.py \
  --reference docs/verification/library-030-col07-circular-shear.json \
  --case missing_shear_evidence_hold
```

For a fixture with a top-level `supplied_shear_basis`, the example adds
that basis to the selected member request before loading it. A plain
`--input` request carries the optional `shear_basis` directly.

```python
fixture = json.loads(Path("docs/verification/library-030-col07-circular-shear.json").read_text())
request = column.load_circular_column_detailing({
    **fixture["cases"]["single_plane_pass"]["request"],
    "shear_basis": fixture["supplied_shear_basis"],
})
result = column.check_circular_column_detailing(request)
```

This reference is limited to a Ø450 M30 tied specimen, one `y` shear plane,
two credited legs of a closed Grade 415 ring, `d = 0.8D`, and effective
concrete area `min(Dd, 0.8Ag)`. It applies ordinary IS 456 shear equations
using the Table 19 lower row, compression multiplier and Table 20 cap.
ACI 318-14 informs the circular depth and closed-hoop analogy. The
frozen fixture records source URLs, assumptions and
tolerances, and its [independent replay](../../verification/check_library_030_col07_circular_shear_reference.py)
checks the expected numbers independently. Installed-artifact qualification is
a separate release step.

The report, drawing and BBS share the member, analysis revision, detailing
revision and input hash. The shear outputs identify the governing row and
station. The passing BBS contains 20 Ø10 rings and eight Ø20 longitudinal
bars, with a theoretical mass of 113.196 kg.
The BBS is withheld for a stale ring cut register, missing spiral pitch or
crowded turns.

## One checked circular compression contact lap

The circular-lap profile covers one straight Ø20 compression contact pair
with both centres on the same perimeter of a short braced eight-bar tied
cage. The CL1 reference supplies constant signed U1 actions with zero shear,
an interval compression basis, 75 mm ring spacing through the overlap and
the external ring closure detail. The report records both transfer layouts
and the signed strength checks at each station.

```bash
./scripts/python_runtime.sh Python/examples/circular_column_detailing.py \
  --reference docs/verification/library-030-col07-circular-lap-reference.json \
  --case circular_contact_lap --output-dir circular-contact-lap
```

The 840 mm overlap meets the 797.5 mm requirement. The upper transfer
layout governs at U1 MID and B with a utilization of 0.202402. The drawing
shows each longitudinal piece, the CL1 bounds and the 26 R1 stations.
The BBS contains 35 pieces with a theoretical mass of 119.633 kg.
The three FAIL and four HOLD controls retain the diagnostic report and
withhold the drawing and BBS.
