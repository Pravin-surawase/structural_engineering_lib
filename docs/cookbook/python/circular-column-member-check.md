---
owner: Main Agent
status: active
last_updated: 2026-11-12
doc_type: guide
---

# Circular tied and spiral column check

Use `column.load_circular_member` and `column.check_circular_member` for a
short braced circular column with one regular ring of equal longitudinal
bars. Supply one concurrent factored compressive action and signed moments
at the checked station. The bar centres are measured from the left and top.
The first bar angle starts at the right and increases clockwise. Positive
Mx compresses the top, and positive My compresses the left.

Choose a closed circular ring with its circumferential closure reference,
or a uniform spiral with the extra turns at each end. The spiral flag
`axial_enhancement` identifies a design that relies on the additional
confinement requirements. A missing closure or end-turn declaration produces
HOLD. An inadequate declared detail produces FAIL. The section-strength and
local-restraint outcomes remain independently visible.

## Run the worked example

Use `python -m structural_lib install-preflight --json` to verify the
candidate version and its origin. The Python workflow and input schema are
listed in `python -m structural_lib capabilities --json`. Copy the
[example script](../../../Python/examples/circular_column_member.py) and
[matching reference JSON](../../verification/library-029-col05-circular-column.json)
into a working directory and run:

```bash
python circular_column_member.py --reference library-029-col05-circular-column.json --case spiral --output-dir column-output
```

The directory contains `result.json`, `report.html` and `section.svg`,
all tied to the same input hash. The report gives the strength and restraint
outcomes, signed capacities, bar coordinates, spiral ratio and source
clauses. The SVG is a local section projection of the checked bars and
transverse centreline. Supply a custom request with `--input`; inspect the
fields with `column.CircularColumnInputV1.model_json_schema()`.

## Worked check

The section is Ø450 mm in M30 concrete with eight Ø20 Fe500 bars at 165 mm
radius. The factored compression is 650 kN with moments of +70 and +40 kN·m.
The independent circular-chord calculation gives 184.623 kN·m in each
principal direction and 183.315 kN·m along the demand ray. The combined
governing utilization is **0.58118** with either Ø10 rings at 150 mm or the
Ø10 spiral at 60 mm.

The spiral has 40 mm cover to the outside of the transverse steel, a 370 mm
outside core diameter, and a 360 mm centreline diameter. Its volume ratio is
0.013788 against 0.012470 required, with the transverse steel grade capped
at 415 N/mm² in that calculation. The enhancement pitch window is 30 to
61.667 mm. The checked schedule supplies 1.5 extra turns at each end.

The 5% increase applies to the admitted short axial check. Run
`--case axial_tied` and `--case axial_spiral` at 2800 kN to compare
2720.305 kN tied capacity with 2856.320 kN spiral capacity. Use
`--case spiral_wide` for a 120 mm spiral that fails the requested
enhancement checks. The same pitch in `--case spiral_ordinary_wide`
is checked as ordinary restraint without enhancement. The signed moment
cases use the ordinary tied interaction basis.

This profile covers one short braced station. Slender circular members,
shear, seismic confinement, splices, joints and member-wide fabrication
have separate acceptance cases. The
[independent replay](../../verification/check_library_029_col05_reference.py)
derives the frozen section values without importing the production solver.
