---
owner: Main Agent
status: active
last_updated: 2026-09-30
doc_type: reference
task: COLUMN-PMM-001
---

# Column PMM independent analytical benchmark

## Engineering reference method — owner decision, 30 September 2026

Derive mechanics independently from equilibrium, strain compatibility, section
geometry and constitutive assumptions. Original standards define code-specific
requirements and parameters. Inspect the actual source of comparator libraries,
including their laws, factors, strain domains, signs and displaced-concrete
conventions; agreement alone does not establish correctness. Verify the result
with independent analytical or numerical benchmarks and meaningful regressions.
NPTEL lectures remain useful supporting references, not the default authority
or a substitute for these derivations. Valid historical citations are retained.

For the approved column correction, the owner selected consistent integration
of the original IS 456 Fig. 21 design relationship with its stated factors,
rather than SP:16's rounded coefficients as the numerical engine. This decision
does not replace separately prescribed code-design formulas, steel material
laws, nominal axial caps, or member-design checks by inference.

## Purpose and claim boundary

This record independently checks the experimental rectangular-column fiber
kernel at an oblique neutral-axis orientation. It is a calculation benchmark,
not a comparison with another repository solver. It does not promote the PMM
module into the supported API, replace the IS 456 Cl. 39.6 Bresler workflow, or
constitute qualified engineering review or professional approval.

The governing standard identity is IS 456:2000, fourth revision, confirmed by
the [Bureau of Indian Standards record](https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/standard_review/Standard_review/Isdetails?ID=MzE2NjI%3D)
and [official preview](https://www.services.bis.gov.in/tmp/SR456.pdf). The
calculation now uses the literal Cl. 38.1(c)/Fig. 21 parabolic-rectangular
concrete design curve with peak `0.67*fck/1.5`. The current representative steel profile uses Fig. 23 with `gamma_s=1.15`
and six cold-worked salient points; the existing Fe250 convention selects
the definite-yield branch. The frozen predecessor used a separately named
five-point/`0.87*fy` compatibility approximation. No protected
clause prose or source image is reproduced here.

## Exact case

| Quantity | Value |
|---|---:|
| Section | 200 mm x 200 mm |
| Concrete | M25, `fck = 25 N/mm2` |
| Steel | Fe415, `Es = 200000 N/mm2` |
| Bars | Four bars, each 400 mm2 |
| Bar coordinates | `(+-75, +-75) mm` |
| Neutral-axis angle | `theta = 45 degrees` |
| Neutral-axis depth | `100 sqrt(2) = 141.421356237 mm` |

The gross-section centroid is the origin. Compression is positive, and the
module convention is `Mx = sum(F*y)` and `My = -sum(F*x)`.

## Closed-form concrete calculation

Let `a = 100 mm` and use the projected coordinate
`q = (x + y) / sqrt(2)`. The neutral axis passes through the centroid, so the
compressed triangle occupies `0 <= q <= a*sqrt(2)`. Its strip width is

`L(q) = 2 * (a*sqrt(2) - q)`.

The extreme strain is 0.0035 and the constant-stress plateau starts where the
strain reaches 0.002. With `t = q/(a*sqrt(2))`, that transition is `t = 4/7`.
Integrating the normalized stress over the triangular strips gives

- axial integral factor: `33/98`;
- moment integral factor: `1499/10290`.

Using peak design concrete stress `(0.67/1.5)*fck = 11.1666666667 N/mm2`:

- `Pc = 4*a^2*(0.67*fck/1.5)*(33/98) = 150.408163265 kN`;
- `Mx,c = 4*a^3*(0.67*fck/1.5)*(1499/10290) = 6.506835115 kNm`;
- `My,c = -6.506835115 kNm`.

## Exact steel calculation

Only the two diagonal corner bars have nonzero strain. Their strains are
`+0.002625` and `-0.002625`. Interpolation between the source-defined `.95` and `.975` Fig. 23A vertices
with `fy/1.15` gives steel stress magnitude `348.338582677 N/mm2`.

The compression-bar force subtracts its displaced concrete stress:

- compression bar: `(348.338582677 - 11.166666667)*400 = 134.868766404 kN`;
- tension bar: `-348.338582677*400 = -139.335433071 kN`.

Therefore the steel contribution is `Ps = -4.466666667 kN`,
`Mx,s = 20.565314961 kNm`, and `My,s = -20.565314961 kNm`.

## Independent expected response

| Result | Expected |
|---|---:|
| `Pu_kN` | `145.941496599` |
| `Mx_kNm` | `+27.072150076` |
| `My_kNm` | `-27.072150076` |

The kernel regression uses a square 128 x 128 mesh and absolute tolerances of
`0.02 kN` for axial force and `0.001 kNm` for each moment. The public
experimental slice regression separately interpolates the 45-degree slice at
the benchmark axial force with `0.01 kNm` moment tolerance. These tolerances
cover numerical fiber/slice discretization only; the analytical expected values
are not adjusted to match implementation output.

## Supported conclusion and exclusions

This case proves that the experimental kernel and slice assembly reproduce one
independently derived oblique strain plane, including the signed two-axis moment
convention. Principal-axis comparisons, axial-cap verification, invalid-domain
checks, and serialization are separate regressions.

The module remains limited to rectangular short-column section analysis. It
does not include slenderness, second-order response, confinement, circular
sections, detailing, automatic design, or a supported safety decision.

Experimental callers import directly from
`structural_lib.codes.is456.column.pmm` and construct reinforcement with
`ColumnReinforcementBar` / `ColumnReinforcementLayout` from
`structural_lib.core.data_types`. Absence from `structural_lib.api` is
intentional until a separate public-support contract is approved.

## Source-defined integrated column correction, 30 September 2026

The selected concrete profile is `IS456_FIG21_INTEGRATED_V1`, using the literal
strength reduction `0.67` and concrete partial factor `1.5` from Cl. 38.1(c).
The current section method is
`IS456_FIG21_INTEGRATED_V1__STEEL_FIG23_GS115_V1`; the immutable column
packet retains `IS456_FIG21_INTEGRATED_V1__STEEL5_087_COMPAT_V1`. Supported uniaxial and P-M
results expose that method in their Python serialization and HTTP responses.
The experimental surface appends `__FIBER_V2`. This does not claim that the
five-point steel curve is an exact representation of every accepted grade.

The [primary BIS historical scan](https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf#page=82)
at printed pages 69–70 establishes the selected design curve and full-compression
strain constraint. A controlled local copy with SHA256
`964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264` was inspected
directly at those pages. The historical public scan includes amendments 1–2;
The controlled consolidation includes Amendment 5; Amendment 6 (June 2024)
was checked for these provisions and does not alter them. The latest complete
amendment set and manufacturer-specific material applicability remain uncertified.
This source-use decision does not mark the entire private corpus reviewed.

Take depth `y` from the nominated compression face, section depth `D`, neutral
axis depth `xu`, and compression-positive strain. Plane sections require
`epsilon_far/epsilon_top = 1-D/xu`. Combining this with 39.1(b)'s extreme-face
constraint gives, for `xu >= D`,

`epsilon(y) = 0.002*(1-y/xu)/(1-3*D/(7*xu))`.

The zero-strain axis remains `xu`; the strain at `3D/7` is 0.002. The plane
connects continuously to 0.0035/zero at `xu=D` and approaches uniform 0.002
as `xu` increases without limit. The compression face cannot reverse at
`xu/D=7/3`. These are mechanics and source constraints, not table fitting.

Set `f0=0.67*fck/1.5`. With no tensile concrete, integrating the Fig. 21
parabola up to strain 0.002 and its plateau gives, for `xu<=D`,

- `C=f0*b*xu*(17/21)`;
- first moment about the compressed top, `Qtop=f0*b*xu^2*(33/98)`;
- centroid `Qtop/C=(99/238)*xu`.

For `xu>=D`, let `q=[4*D/(7*xu-3*D)]^2`:

- `C=f0*b*D*(1-4*q/21)`;
- `Qtop=f0*b*D^2*(1/2-8*q/49)`;
- moment about the gross centroid `Mcenter=f0*b*D^2*(10*q/147)`.

Force is N and first moment/moment are Nmm. Production computes the last
moment directly to avoid cancellation near uniform compression. The gross
concrete contribution subtracts the actual local concrete stress displaced
by each compression bar; tension bars displace no force-carrying concrete.
The Cl. 39.3 nominal `0.4/0.67` capacity and Cl. 39.6 `0.45/0.75` Puz remain
separate code checks. Unrelated beam/slab/footing `0.36/0.42` design blocks
are not changed by this correction.

The exact integrated force coefficient is `0.3615873015873016`, centroid
`0.41596638655462186*xu`. “Exact” means exact for this chosen design curve,
not experimentally exact concrete behavior. The alternatives `4/9` and
`0.446` give force coefficients `0.35978835978835976` and
`0.361047619047619`; they are retained as sensitivity evidence rather than
silently substituted. SP:16's age alone does not invalidate it, and its
rounded design-aid convention must be distinguished from literal integration.

[Rcdesign source](https://github.com/satish-annigeri/rcdesign/blob/ec8fe94b71dc02b07f7d83d12d3a4ddb511dd360/src/rcdesign/is456/concrete.py)
uses `0.67*fck/gamma_m`; its
[stressblock source](https://github.com/satish-annigeri/rcdesign/blob/ec8fe94b71dc02b07f7d83d12d3a4ddb511dd360/src/rcdesign/is456/stressblock.py)
uses the full-compression geometry and symbolic integrals. The pinned 0.4.18
official wheel is the test-only comparator. Its native six-point/fy/1.15 steel
results remain distinct from the library's retained five-point/.87fy profile.
[Concreteproperties 0.8.0 source](https://github.com/robbievanleeuwen/concrete-properties/blob/v0.8.0/src/concreteproperties/stress_strain_profile.py)
separates rectangular, bilinear, and discretized parabolic profiles with named
parameters. Its Eurocode/AS/NZS assumptions are not an IS 456 oracle, and its
piecewise-linear discretization introduces a separate approximation. These
comparisons inform implementation choices; they do not override the standard.

The independent generator
`Python/tests/data/benchmark_vectors/generate_column_strain_reference.py`
does not import production code. It solves the face constraints separately,
integrates general piecewise polynomials, and checks them with SciPy adaptive
quadrature. The frozen `column_strain_compatibility.json` includes 56 states,
nine peak sensitivities, the revised oblique anchor, and independently derived
P-M, radial uniaxial, biaxial and long-column consumer cases. It records the
existing 50-interval public curve and 200-interval uniaxial sampling explicitly;
continuous root and interpolation error are separate evidence. No tolerance
is enlarged to match a material-model discrepancy.

For b230/D450/M20/Fe415, six 20mm bars split equally at y50/y400, xu900mm:
the corrected retained-steel profile gives `P=1474.64267433845 kN` and
`M=13.47370152288 kNm`, before a nominal axial cap. Native rcdesign gives
`1474.51100775044 kN` and `13.45065986998 kNm`; the small remaining difference
is the explicit steel-profile difference, not concrete integration error.
The original audit's actual legacy state was `1072.66112419811 kN` and
`51.31251127491 kNm`. Raw states are not automatically allowable design points.

The GC-PM1/GC-UNI1/GC-BI1 golden updates are generated from those independent
references, preserving their nominal axial values and existing tolerances.
The safety-boundary regression still requires an UNSAFE result when a rounded
display reads utilization 1.0. Previous audit, native-model and installed-wheel
artifacts remain immutable in local evidence storage.

### Local candidate qualification

The affected core, service, inherited biaxial/long-column and HTTP checks passed
573 tests. The independent fixture covers 56 section states, including the
compression boundary and uniform-strain limit. The maximum difference between
the closed concrete integral and independent adaptive quadrature is
`1.17e-10 N` in force and `2.99e-8 Nmm` in centroidal moment. These are numerical
errors for the stipulated design law, not physical-model accuracy estimates.

Seven unmodified rcdesign cases retain both steel profiles and all raw results.
At `xu/D=20`, computing the native centroidal concrete moment by subtracting
neutral-axis moments loses about `3.12e-5 Nmm`; this is approximately
`3.12e-11 kNm`, distinct from the steel-model difference. The native diagnostic
records a normalized `1e-12*C*D` moment-precision bound. The independent
regression tolerances remain unchanged. Midpoint meshes with 16, 32, 64 and 128
depth cells have separate convergence evidence; at the compression boundary
the 128-cell moment error is `0.002911 kNm`, within its existing `0.003 kNm`
bound. More mesh cells do not change the constitutive assumptions.

The offline-built local 0.24.0 candidate wheel has SHA256
`07a01cbf1df0cb4a0bf61c6d43d375e65d25dc42edf87a9f0b7cb4c403b9670d`.
Its separate target installation passed 83 independent column regressions and
13 expected family recipes: 11 PASS, one FAIL and one HOLD. All 224 imported
library modules came from that wheel; no source fallback occurred. The
existing Python environment was unchanged. Formatting and all 12 essential
repository checks passed. The OpenAPI baseline changes consist only of the
two optional method fields; the endpoint inventory remains at 92.

These results record the original local column candidate and its tested consumers.
The earlier 55 physical-member checks remain preserved for their unchanged
beam implementation. This packet does not establish full-stack qualification,
latest-amendment/material-domain qualification, or package-release approval.

### Inherited slender-column correction — 30 September 2026

Independent review of the frozen wheel found two consequential defects in the
inherited Cl. 39.7 consumers. Its original long-column reference had repeated
the implementation's wrong definition of `Pb`; a passing regression therefore
did not establish compliance with Cl. 39.7.1.1. The original wheel, generator,
fixture, HTTP files and diff remain immutable in local evidence. The concrete
and strain-plane benchmarks are separate from this failed consumer assumption.

The [original IS 456 Cl. 39.7.1 note 2 and Cl. 39.7.1.1](https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf#page=85)
were checked directly against printed page 72 of the controlled Amendment-5
consolidation. Note 2 treats `M2` as the larger end-moment magnitude and gives
`M1` a negative sign for double curvature. Normalize the bending-plane direction
before forming the initial moment and adding the nonnegative additional
moment. Reversing both end-moment signs changes neither relative curvature nor
the resistance of the supported symmetric section. This braced expression
applies to members without transverse loads along the height; the API does not
model those loads or substitute for a complete second-order frame analysis.

For `Pb`, plane sections independently give
`epsilon_t = -0.0035*(D-d'-xu)/xu`. The clause prescribes
`epsilon_t = -0.002`, hence
`xu = (D-d')*0.0035/(0.0035+0.002)`, with compression positive and lengths in mm.
Axial equilibrium at that depth uses the selected integrated Fig. 21 concrete
profile, the separately retained steel profile and local displaced-concrete
subtraction. It must not use the public interaction curve's distinct
yield-balanced point. Both `design_long_column` and
`calculate_additional_moment` now use the clause-specific calculation; the
public curve's balanced-point convention remains separately defined.

For `b=300 mm`, `D=450 mm`, `d'=50 mm`, M25/Fe415, `Asc=2700 mm2`,
`Pu=1000 kN`, `lex=6300 mm`, `ley=3000 mm` and unsupported length `6300 mm`,
the independently prescribed `xu` is `254.545454545455 mm` and
`Pb=702.825268537539 kN`, compared with the previously substituted
`483.366250043148 kN`. The correction changes `k` from about `0.7200` to
`0.817227251845070`. With zero y-axis end moments, the independently computed
combined corrections give:

| x-axis end moments (kNm) | Frozen original Mux (kNm) / ratio / status | Corrected Mux (kNm) / ratio / status |
|---|---|---|
| +170, +170 | 201.75 / 1.0315 / unsafe | 206.04 / 1.0591 / unsafe |
| -170, -170 | 170.00 / 0.8339 / safe | 206.04 / 1.0591 / unsafe |
| +165, +165 | 196.75 / 0.9995 / safe | 201.04 / 1.0269 / unsafe |

These ratios use the existing 50-interval section-capacity interpolation,
Cl. 39.6 exponent and independent minimum eccentricity. Full-precision
reference values and integration residuals are retained separately; displayed
rounding does not govern the safety decision. The reference generator now
asserts the prescribed tension strain, evaluates `Pb` independently of grade,
and covers three safety-reversal anchors plus sixteen sign/curvature cases.
Tests exercise both code and service owners and the two HTTP routes.

This packet corrects the two confirmed definitions/load paths. It does not
change the steel law, nominal axial caps, public envelope sampling or API
schemas. Latest-amendment/material qualification and a broader assessment of
the existing single-`k` representation for two bending planes remain separate
engineering scope questions; these checks do not certify every long-column
configuration. The later outcome-changing plane-factor finding and separately
revised implementation are recorded in
[Slender-column axis qualification](slender-column-axis-qualification.md).

The local correction check ran 225 affected tests: 223 passed initially and the
two stale golden cases failed. After the independent source-based reference
repair, both failed cases passed; their original failure log and JUnit remain
preserved. A freshly built, separately installed wheel then passed all 106
independent column regressions, including the new prescribed-strain and
sign/curvature cases. Its SHA256 is
`c6fdda9aabde18a0b7417ca83b7dbbea52b15d0379a6849ab01b610af81ca0af`.
All 224 imported library modules came from that wheel; the 196 existing
distribution identities were unchanged. The 13 expected recipes still report
11 PASS, one FAIL and one HOLD. All 12 essential repository checks and the
changed-path formatter/linter passed. These results belong to the consumer
correction packet, not to the unchanged original review snapshot.

### Per-plane slender-column correction — 30 September 2026

Independent review reproduced a third inherited defect: applying the x-plane
`Pb` and `k` to the y-plane additional moment made an accepted rectangular
orientation return safe while its axis-relabelled equivalent returned unsafe.
The correction independently evaluates the Cl. 39.7.1.1 prescribed strain state
in each plane. Both consumers now apply `k_x` and `k_y` respectively. Existing
scalar `k` and `Pb_kN` remain explicitly documented x-plane aliases; new optional
code/service/HTTP fields expose both states and the versioned reduction method.

The source anchor now returns `197.04 kNm` augmented demand and interaction
`1.0013`, unsafe, in either orientation. All 312 affected source/consumer checks
and 151 isolated-wheel independent checks passed. The preceding repaired
consumer packet remains immutable; the new candidate wheel has SHA256
`3458400840fee618b48488875904ee97950d7f909ce0c3f359fa7de46bdb1721`.
Exact compatibility, source assumptions, unchanged caps, retained recipe
FAIL/HOLD statuses and separate qualification limits are recorded in
[Slender-column axis qualification](slender-column-axis-qualification.md).


## Representative steel and compression-bar revision — 1 October 2026

The current section method names the selected six-point representative law.
Original [IS 456 Fig. 23 and Cl. 38.1(e)](https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf#page=83)
define the steel family and partial factor. The independently inspected original
[SP:16 Table A, printed page 6](https://law.resource.org/pub/in/bis/S03/is.sp.16.1980.pdf#page=29)
corroborates six salient points for Fe415/500. Its rounded numerical values and
Table F compression-bar shortcut are distinct from the unrounded figure-defined
law. These references support the model parameters, not arbitrary grade-to-type
substitution: fy alone does not identify cold-worked, definite-yield or a tested
manufacturer curve. Fe550 uses the selected parameterized representative law,
not a nearest-grade extrapolation or an early ideal-plastic plateau.

The source-defined vertices use stress fractions `.8/.85/.9/.95/.975/1`
and plastic offsets `0/.0001/.0003/.0007/.001/.002`, with `Es=200000 N/mm²`
and `fyd=fy/1.15`. Stress is signed and clipped at the appropriate plateau.
Native [rcdesign 0.4.18 source](https://github.com/satish-annigeri/rcdesign/blob/ec8fe94b71dc02b07f7d83d12d3a4ddb511dd360/src/rcdesign/is456/rebar.py)
provides differential evidence: 107/110 signed states agree. Three native
negative-strain plateau results lose their sign in its final branch; those
raw discrepancies are retained and are not used to redefine the source law.

Doubly reinforced beam design now subtracts the Fig. 21 concrete stress at
the actual compression-bar strain, as required by Annex G-1.2 equilibrium.
The `.36/.42` base block, `.87fy` yielded tension force, xu limits, reinforcement
caps and nominal column axial formulas remain separately prescribed design
conventions. This correction does not replace the beam code-design route with
a fiber solver. Independent 60-digit Decimal fixtures check 110 steel states
and 16 compression-bar/beam-consumer force and moment states; the column fixtures are separately
regenerated from mechanics and quadrature with the named material profile.

Compatibility changes are intentional and require review against this packet,
not acceptance by the older frozen wheel. For the prior axis anchor at
`Pu=1000 kN`, `b=300 mm`, `D=450 mm`, M25/Fe415, `Asc=2700 mm²`, `d'=50 mm`,
`lex=6300 mm`, `ley=3000 mm`, braced ends `161/161 kNm`, independent new-profile
results are `Pbx=708.606029358691 kN`, `kx=.820143162631427`, demand
`197.168313472046 kNm` and ratio `.993158454119813`. The frozen five-point
packet gave `197.04 kNm`, ratio `1.0013`. Both orientations remain identical;
the changed verdict is a material-model sensitivity, not a relaxed safety
limit or reversal of the accepted per-axis correction.

The current local packet and raw full-precision observations are in
`external_data/library-evidence/96170d8/material-sls-correctness-20260930`.
The original column and flange review packets remain immutable. No numerical
or mesh tolerance is enlarged to conceal a model difference. This qualification
covers the representative constitutive profile, not cyclic behavior, buckling,
fracture, manufacturer tests, confinement or the whole library's release.
