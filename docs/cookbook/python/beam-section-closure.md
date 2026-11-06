---
owner: Main Agent
status: active
last_updated: 2026-11-07
doc_type: guide
complexity: beginner
tags: [beam, shear, flexure, python]
---

# Check supplied reinforcement at a beam section

Run the example from a clone using a virtual environment with Python 3.11 or
newer. The supplied shear operation is available in the current source build.

```bash
python -m pip install ./Python
python Python/examples/beam_section_closure.py
```

The script prints JSON under `shear` and `flexure`. Each result includes its
effective inputs, engineering state, diagnostics and calculation provenance.
[Example source](../../../Python/examples/beam_section_closure.py)

## Supply the shear section and reinforcement

Call `beam.supplied_section_shear_capacity` with a
`beam.SuppliedSectionShearRequest`. Set the web width and effective depth in mm,
concrete strength in N/mm² and continuing longitudinal tension steel area
eligible for Table 19 in mm². The concrete strength domain is M15 through M40.
Use the effective depth of the declared tension steel.

Use `beam.SectionShearReinforcement` for one stirrup group and optionally one
distinct bent-up group effective at the same section. Supply the total area of
active legs or bars perpendicular to the steel, the steel grade in N/mm² and
the inclination to the beam axis. The calculation caps each steel grade at
415 N/mm². Stirrup inclinations are 90° or 45° with positive spacing measured
along the beam. Bent-up bars may be inclined from 45° through 90°. Supply a
positive spacing for repeated bent-up bars or `spacing_mm=None` for a single
group. Use distinct group IDs and count each effective bar once. A missing
group declares zero provision.

```python
from math import pi
from structural_lib import beam

stirrups = beam.SectionShearReinforcement("S1", 2 * pi * 8**2 / 4, 415, 90, 150)
bent_up = beam.SectionShearReinforcement("B1", 2 * pi * 16**2 / 4, 415, 45, None)
result = beam.supplied_section_shear_capacity(
    beam.SuppliedSectionShearRequest(
        profile_id="web-section",
        web_width_mm=300,
        effective_depth_mm=450,
        fck_nmm2=25,
        longitudinal_tension_area_mm2=1350,
        stirrups=stirrups,
        bent_up_bars=bent_up,
    )
)
print(result.engineering, result.outputs["provided_capacity_kn"])
```

The stirrups contribute 108.890 kN. The single bent-up group contributes
102.663 kN raw and receives full credit. Table 19 contributes 86.400 kN,
bringing the section resistance to 297.953 kN. With these same section
dimensions, Table 20 limits resistance to 418.500 kN.

- The check credits at most the stirrup contribution to bent-up bars. If
  the raw bent-up contribution exceeds half the raw total reinforcement
  contribution, the result carries the limited capacity and
  `SHEAR.BENT_UP_LIMIT` with engineering `fail`.
- Stirrup spacing is limited to `min(0.75d, 300 mm)` for vertical stirrups
  and `min(d, 300 mm)` for 45° stirrups. Only the stirrup group counts
  toward the minimum stirrup area. The profile assumes an ordinary beam
  subject to that minimum.
- `pass` covers the supplied reinforcement checks at the section. Shear
  demand, physical bar placement, anchorage, member detailing, support
  enhancement, seismic checks and torsion require separate evidence.
  The existing `beam.shear_capacity` remains the vertical-link operation
  used by physical-member callers.

## Read the sagging flexure branch

The example also calls `beam.flexural_capacity` with a 300 × 475 mm web,
800 mm wide flange, M25 concrete and Fe415 bars at 405 and 440 mm from the
top compression face. Changing only the flange thickness gives these cases.

| Flange thickness (mm) | Neutral axis (mm) | Moment resistance (kN·m) | Compression block |
|---:|---:|---:|---|
| 150 | 72.746082 | 208.028494 | Entirely within the flange |
| 50 | 96.214262 | 207.338948 | Web plus reduced flange block |
| 30 | 131.489552 | 201.893934 | Web plus full flange block |

Beyond the flange depth the operation uses the Annex G-2.3 cutoff at
`Df / xu = 0.43`. The full flange block applies at and below that ratio.
Results in the web use method `is456-flexural-capacity-flanged-web-v1`.
When the rounded block change leaves a gap in possible equilibrium
forces, the result returns `FLEXURE.FLANGE_FORCE_GAP`, applicability
`not_applicable` and engineering `not_evaluated` with empty outputs.

## Replay the independent references

```bash
python docs/verification/check_library_027_beam_section_reference.py
```

The fixture records per-component shear targets, combined resistance and
limits, the two web branches, and the flange force gap. In an isolated
rcdesign 0.4.18 replay, its vertical, inclined, single bent-up and repeated
bent-up components were 108.836, 153.917, 102.611 and 615.668 kN. The
corresponding StructLib targets are 108.890, 153.994, 102.663 and 615.976 kN
because this operation uses `0.87 fy` and rcdesign uses `fy / 1.15`.
These four numbers compare raw components before application of group
and concrete limits. [Frozen targets](../../verification/library-027-beam-section-closure.json)
· [Pinned rcdesign reinforcement source](https://github.com/satish-annigeri/rcdesign/blob/ec8fe94b71dc02b07f7d83d12d3a4ddb511dd360/src/rcdesign/is456/rebar.py)
