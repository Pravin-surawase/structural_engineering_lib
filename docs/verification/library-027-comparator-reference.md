---
owner: Main Agent
status: active
last_updated: 2026-11-06
doc_type: reference
---

# StructLib 0.27 section comparison references

[LIB-9](https://pravinsurawase.atlassian.net/browse/LIB-9) freezes the four
section cases below. Use the [machine-readable fixture](library-027-comparator-reference.json)
for unrounded expected values and acceptance checks. The
[observed baseline](library-027-comparator-baseline.json) retains the original
engine outputs and their limitations. The two records serve different purposes.

## Frozen inputs

Depth `y` and neutral-axis depth `xu` are measured from the top compression
face in mm. Strengths are in N/mm², forces in kN and moments in kN·m.
All longitudinal steel uses the representative Fe415 deformed-bar curve.
The three beams have zero axial force and sagging bending. For shear use the
web width and the area-weighted depth of the tension reinforcement.

| Case | Section (mm), concrete | Longitudinal reinforcement from the top | Transverse steel |
|---|---|---|---|
| 1. Singly reinforced | 230 × 450, M20 | At 415: Ø20, Ø16, Ø20 | 2 active legs Ø8 at 150 mm, Fe415, vertical |
| 2. Doubly reinforced | 230 × 450, M20 | At 35: 2Ø16; at 415: 3Ø16 | Same |
| 3. Flanged, two tension layers | Web 300 × 475; flange width 800, thickness 150; M25 | At 405: 2Ø18; at 440: 3Ø20 | Same |
| 4. Three-layer rectangular column | 230 × 450, M20; prescribed `xu = 900` | At 50: 3Ø16; at 225: 2Ø16; at 400: 3Ø16 | Ø8 at 150 mm, Fe415; context only |

Use the executable bar list in case 1. The [rcdesign quickstart](https://rcdesign.readthedocs.io/en/latest/quickstart.html)
prose instead describes two Ø16 and one Ø20. Case 4's runnable depth gives
`xu/D = 2`; its source comment gives a different ratio. Neither discrepancy
changes the runnable input. The quickstart lists 25 mm cover for beams and
35 mm for the column. Use the explicit bar depths. The fixtures do not verify
cover, fit, ties, support or anchorage. Where an API needs transverse
coordinates, the JSON defines the symmetric placeholders used for replay.

## Calculation basis

The [controlled source record](is456-library-first-evidence.md#controlled-sources)
identifies IS 456:2000 through Amendment 5 and the issued
[June 2024 Amendment 6](https://egazette.gov.in/WriteReadData/2024/254982.pdf).
Both local PDF hashes were checked. The issued amendment was reviewed for
these cases; it does not change the selected flexural, column strain or shear
provisions for these uncoated-bar sections. This is a case-specific source
review. No standard pages or clause prose are distributed here.

- **Beam flexure:** Cl. 38.1 and Figs. 21–23 give the strain plane and
  material profiles. Solve axial equilibrium with `ε(y) = 0.0035(1 − y/xu)`.
  Bar area is `πφ²/4`. A bar contributes its steel force less the concrete
  force displaced at that depth. Use the Fig. 23A representative curve with
  `Es = 200,000 N/mm²` and steel partial factor 1.15.
  The rcdesign reference integrates the Fig. 21 parabola and plateau at
  `0.67 fck/1.5`. The StructLib reference uses the Annex G rounded block
  `C = 0.36 fck b xu` at `0.42 xu` while retaining the per-bar stress law.
  Case 3 has `xu < 150 mm` under both methods, so `b = 800 mm` for its flexure.
- **Beam shear:** `d = Σ(Aᵢ yᵢ)/ΣAᵢ` for tension steel and
  `pₜ = 100 Aₛ/(b d)`. StructLib uses Table 19 linear interpolation and
  `Vₛ = 0.87 fy Aₛᵥ d/s` per Cl. 40.4. The frozen Table 19 brackets
  `(pₜ %, τc N/mm²)` are M20: (0.75, 0.56)–(1.00, 0.62) for case 1,
  M20: (0.50, 0.48)–(0.75, 0.56) for case 2, and M25:
  (1.00, 0.64)–(1.25, 0.70) for case 3. Table 20 caps of 2.8 N/mm² (M20)
  and 3.1 N/mm² (M25) do not govern these examples. rcdesign 0.4.18 instead
  uses its continuous concrete shear formula and `fy/1.15` for vertical links.
  Its concrete shear result is a comparator value, not a Table 19 target.
- **Column:** Cl. 39.1(b) fixes the fully compressed strain plane:
  `εtop + 0.75 εfar = 0.0035` and `εfar/εtop = 1 − D/xu`.
  At `xu = 900 mm`, the strains are about 0.00254545 and 0.00127273 at the
  top and far faces. Integrate concrete stress and take net bar forces as
  above. With compression positive and the moment about the horizontal axis
  at the section centroid, the lever arm is `D/2 − y`. The intermediate
  comparator moment `951.450385 kN·m` is about the neutral axis. Subtract
  `P × (xu − D/2)/1000` to get the centroidal moment. Cl. 39.3 and the
  interaction slice's axial cap remain separate from this raw response.

## Expected values and acceptance

Each beam row is an independent result for the stated method. Values below
are rounded for reading; comparisons use the JSON values.

| Case and method | `xu` mm | `d` mm | `pₜ` % | `M` kN·m | Concrete shear kN | Link shear kN | Total shear kN |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 · rcdesign | 179.942212 | 415.000000 | 0.868916 | 101.806298 | 56.461878 | 100.370698 | 156.832577 |
| 1 · StructLib | 180.735608 | 415.000000 | 0.868916 | 101.489328 | 56.176131 | 100.420884 | 156.597015 |
| 2 · rcdesign | 61.568274 | 415.000000 | 0.631939 | 83.676694 | 50.067404 | 100.370698 | 150.438102 |
| 2 · StructLib | 61.725604 | 415.000000 | 0.631939 | 83.642779 | 49.845945 | 100.420884 | 150.266829 |
| 3 · rcdesign | 72.426740 | 427.727273 | 1.131107 | 208.251760 | 86.135928 | 103.448879 | 189.584808 |
| 3 · StructLib | 72.746082 | 427.727273 | 1.131107 | 208.028494 | 86.161252 | 103.500604 | 189.661856 |

Case 4 has one shared reference: **+1394.806807 kN** and **+9.955790 kN·m**
about the centroid at exactly 900 mm. The experimental slice's nominal
axial cap is about 1262.374193 kN. The raw fixed-depth response is above that
cap, so this fixture cannot establish member acceptance. The stable column
member input still rejects explicit layers.

Use absolute tolerances: 0.001 mm for the solved beam `xu`, 0.00001 mm for
`d`, 0.000001 percentage points for `pₜ`, 0.001 kN per force or shear result,
and 0.001 kN·m per moment. The beam axial residual must be within 0.01 N.
Match the prescribed column depth, discrete inputs, and method and branch
selection exactly. The tolerances address numerical replay; systematic
differences between methods are reported separately. Both baseline engines
meet their respective targets. The column diagnostic is within tolerance
at both recorded mesh resolutions.

## Reproduce the freeze

From the repository root:

```bash
./scripts/python_runtime.sh docs/verification/check_library_027_references.py
```

The replay uses standard-library arithmetic, piecewise Simpson integration
of the concrete stress and moment, and bisection of beam equilibrium. It
imports neither engine. The four computed reference records are compared
against the frozen fixture and the observed baseline.

The external replay used [rcdesign 0.4.18](https://pypi.org/project/rcdesign/0.4.18/)
and the [pinned quickstart source](https://github.com/satish-annigeri/rcdesign/blob/ec8fe94b71dc02b07f7d83d12d3a4ddb511dd360/docs/quickstart.rst).
The fixture records the checked source and artifact SHA-256 values. The wheel
import reads `pyproject.toml` from the current directory.
To reproduce it, extract only that file from the verified source archive
into an otherwise empty working directory and run each unchanged quickstart
script with the isolated wheel interpreter. Confirm `rcdesign.__file__` is
under its `site-packages`. All four formatted reports and 24 unrounded
outputs were reproduced. Both retained StructLib installs also reproduced
their captured result JSON. These are baseline replays; the 0.27.0 wheel and
source archive will be checked in Goal 5.

## Handoff to Goal 2

Use the existing public `flexural_capacity` and `shear_capacity` operations.
Give a new caller one runnable example that emits all three named cases and
the quantities in the table, plus a guide explaining the method differences
and how to compare results. Keep the exact layers, shear width, link data,
and method identity visible. Verify every output against the StructLib rows
and explain the separate rcdesign rows. The independently reproduced results
do not call for beam calculation changes.

Keep the doubly reinforced case at section level: the member diagnostic
remains HOLD for conflicting depth and missing support width. Goal 3 adds
the bounded layered column section API; Goal 4 owns physical beam member
examples; Goal 5 owns exact installed candidate and release evidence.
