---
owner: Main Agent
status: active
last_updated: 2026-08-12
doc_type: reference
task: COLUMN-PMM-001
---

# Column PMM independent analytical benchmark

## Purpose and claim boundary

This record independently checks the experimental rectangular-column fiber
kernel at an oblique neutral-axis orientation. It is a calculation benchmark,
not a comparison with another repository solver. It does not promote the PMM
module into the supported API, replace the IS 456 Cl. 39.6 Bresler workflow, or
constitute qualified engineering review or professional approval.

The governing standard identity is IS 456:2000, fourth revision, confirmed by
the [Bureau of Indian Standards record](https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/standard_review/Standard_review/Isdetails?ID=MzE2NjI%3D)
and [official preview](https://www.services.bis.gov.in/tmp/SR456.pdf). The
calculation uses the repository's normalized Cl. 38.1 parabolic-rectangular
concrete curve and Fig. 23/SP:16 Table F steel interpolation. No protected
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

Using peak design concrete stress `0.446*fck = 11.15 N/mm2`:

- `Pc = 4*a^2*(0.446*fck)*(33/98) = 150.183673469 kN`;
- `Mx,c = 4*a^3*(0.446*fck)*(1499/10290) = 6.497123421 kNm`;
- `My,c = -6.497123421 kNm`.

## Exact steel calculation

Only the two diagonal corner bars have nonzero strain. Their strains are
`+0.002625` and `-0.002625`. Interpolation on the normalized five-point Fe415
curve gives steel stress magnitude `345.724503466 N/mm2`.

The compression-bar force subtracts its displaced concrete stress:

- compression bar: `(345.724503466 - 11.15)*400 = 133.829801386 kN`;
- tension bar: `-345.724503466*400 = -138.289801386 kN`.

Therefore the steel contribution is `Ps = -4.46 kN`,
`Mx,s = 20.408970208 kNm`, and `My,s = -20.408970208 kNm`.

## Independent expected response

| Result | Expected |
|---|---:|
| `Pu_kN` | `145.723673469` |
| `Mx_kNm` | `+26.906093629` |
| `My_kNm` | `-26.906093629` |

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
