# IS 456 Solid Slab Source and Benchmark Ledger

**Type:** Verification
**Audience:** Developers and engineering reviewers
**Status:** Internal implementation evidence; qualified review required
**Importance:** Critical
**Created:** 2026-08-10
**Last Updated:** 2026-08-15

## Source lock

| ID | Identity | Permitted implementation use | State |
|---|---|---|---|
| `SLAB-SRC-IS456-A5` | Controlled IS 456:2000 copy through Amendment 5, SHA-256 `964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264` | Owner-authorized implementation and public distribution of required formulas, normalized tables, limits, figure-derived values, lookup and interpolation; protected prose/images excluded | Implementation and approved-scope normalized-data distribution authorized |
| `SLAB-SRC-IS456-A6` | Amendment 6, June 2024, SHA-256 `4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881` | Amendment-impact review | Controlled copy; no slab change identified by the existing evidence record |
| `SLAB-SRC-NPTEL-18` | IIT Kharagpur/NPTEL, Module 8 Lesson 18, One-way Slabs | Public secondary explanation and benchmark B02 | Accepted as independent educational evidence, not primary-code approval |
| `SLAB-SRC-NPTEL-19` | IIT Kharagpur/NPTEL, Module 8 Lesson 19, Two-way Slabs | Public secondary explanation and benchmark B04 | Accepted as independent educational evidence, not primary-code approval |

The private corpus manifest declares `private_only=true`,
`public_distribution_allowed=false`, and `review_state=UNREVIEWED_SOURCE_CORPUS`.
Those flags apply to the protected source corpus itself, which remains private;
they do not describe the separately authorized normalized code data. The owner
authorized implementation on 2026-08-10 and confirmed source/licensing
permission for public distribution of approved-scope normalized data on
2026-08-11. The canonical decision is
[`is456-public-distribution-permission.json`](is456-public-distribution-permission.json),
and the release path validates it fail closed. Agents must not report this gate
as pending or request it again unless the owner explicitly changes the decision.
Runtime results retain table, case, aspect-ratio, interpolation, and amendment
provenance; external coefficient carriers remain available.

## Clause and behavior map

| Calculation behavior | Primary reference area | Public corroboration | Runtime policy |
|---|---|---|---|
| One-way/two-way classification | Cl. 24.1 and 24.3 | Lesson 18 pp. 5-6 | Ratio is computed from explicit effective spans; no support is inferred |
| Continuous one-way coefficient domain | Cl. 22.5 | Lesson 18 p. 7 | At least three spans, uniform section/load acknowledgement, span variation no more than 15 percent, and no redistribution |
| Slab reinforcement minimum, diameter and spacing | Cl. 26.5.2.1, 26.5.2.2, 26.3.3 | Lesson 18 pp. 8-11 | Deterministic provided-bar checks |
| Two-way middle/edge strips | Annex D | Lesson 19 pp. 4-5 | Middle strip 3/4; two edge strips 1/8 each |
| Restrained-corner torsion | Annex D, D-1.8 to D-1.10 | Lesson 19 pp. 7-8 | Full, half, none, or free-to-lift disposition from physical adjacent edges |
| One-way slab shear | Cl. 40.1, 40.2.1.1; Tables 19 and 20 | Lesson 18 pp. 6 and 15 | Existing packaged Table 19/20 lookup plus slab-depth factor; no automatic stirrup design |
| Span/depth serviceability | Cl. 23.2.1 and Cl. 24.1 | Lessons 18-19 | Explicit support or reviewed limit carrier; direct deflection remains held |

## Accepted benchmark ledger

| ID | Inputs | Expected values | Tolerance |
|---|---|---|---|
| `SLAB-B01` | Simply supported one-way: `Lx=3 m`, `wu=10 kN/m2`, one-metre strip, `d=125 mm`, M20/Fe415 | `Mu=11.25 kN m/m`, `Ast=260.7266304 mm2/m` | moment `1e-12`; steel `1e-7 mm2` |
| `SLAB-B02` | Continuous one-way Lesson 18 Problem 8.1: `L=3 m`, `D=140 mm`, `d=115 mm`, M20/Fe415, `wu=14.25 kN/m` with reviewed external coefficients `1/12`, `1/10`, `0.4` | positive `10.6875`, negative `12.825 kN m/m`; shear `17.1 kN/m`; lesson steel `270.615` and `328.34 mm2/m`; canonical 0.36/0.42 stress-block steel `270.835` and `328.665 mm2/m`; `tau_v about 0.148 N/mm2` | actions `1e-12`; canonical steel `0.001 mm2`; lesson comparison `0.35 mm2`; shear stress `0.001 N/mm2` |
| `SLAB-B03` | Interior two-way compatibility route: `Lx=4 m`, `Ly=6 m`, `wu=10 kN/m2`, external `alpha_x=.08`, `alpha_y=.06` | `Mx=12.8`, `My=9.6 kN m/m` | `1e-12` |
| `SLAB-B04` | Restrained two-way Lesson 19 Problem 8.2: `Lx=4 m`, `Ly=6 m`, `wu=15.5 kN/m2`, two adjacent discontinuous edges, reviewed coefficients `0.075/.056/.047/.035` | negative `Mx/My=18.6/11.656`, positive `13.888/8.68 kN m/m`; shear `31 kN/m`; corner zone `800 mm` | actions `0.01 kN m/m`; shear `1e-12`; zone `1e-12 mm` |

## Holds and claim ceiling

- Built-in coefficient data and interpolation are authorized implementation and
  public-distribution scope within approved features. Protected source prose,
  page images, and unrelated standard content remain excluded.
- Unequal-span or unequal-load continuous analysis beyond the accepted
  coefficient-method domain is unsupported; no elastic envelope is inferred.
- Direct deflection remains held until a slab-specific route validates explicit
  service actions and combinations, load duration, reinforcement positions,
  cracking/effective inertia, creep and shrinkage against independent slab
  benchmarks. Crack width likewise requires validated explicit bar geometry,
  cover, neutral-axis depth, exposure limit, and service steel stress or strain.
- Each public route consumes one caller-selected factored UDL or one declared
  coefficient-method action basis. Built-in coefficient resolution does not
  generate project load combinations, patterns, concentrated/opening effects,
  or an envelope.
- Ordinary one-way concrete shear is checked for the beam/wall-supported UDL
  domain. A capacity failure requires increased depth or separate engineering;
  automatic slab shear reinforcement design remains held.
- Punching shear is not applicable to the supported beam/wall-supported UDL
  solid-panel routes. Column-supported and flat-slab punching is a separate held
  extension.
- Passing software tests demonstrates arithmetic and contract behavior only.
  Construction use requires project-specific checks and qualified structural-
  engineering approval.

## Implementation verification — 2026-08-10

- Focused slab, semantic-contract and FastAPI checks passed as a 121-test set.
- The complete repository suites passed: 5,532 Python tests with 3 skipped and
  6 deselected, 388 FastAPI tests, and 241 React tests.
- `./run.sh frontend check` passed lint, all React tests, TypeScript and the
  production build; `./run.sh check --quick` passed 10/10 and the integrated
  repository gate passed 30/30.
- Live Chromium verification loaded `/workbench/slabs` without an error overlay
  or captured console errors. The built-in continuous sample returned
  `10.688/12.825 kN m/m` with Table 12/13 provenance; editing its span made the
  result stale and disabled passport export. The oriented B04 two-way sample
  returned `18.600/13.888/11.656/8.680 kN m/m` with exact Table 26 provenance.
- This evidence supports the bounded software behavior only. The normalized-data
  public-distribution permission gate passed on 2026-08-11; each release still
  requires separate owner authorization, and project use still requires
  qualified structural-engineering review.

## IS456-SLAB-001A closeout evidence — 2026-08-10

- Complete simply supported one-way service and FastAPI results retain the B01
  arithmetic while reporting `complete_workflow_checks_composed`; their nested
  limitations no longer claim that detailing, serviceability, or shear are
  pending. The original compatibility flexure function retains
  `flexure_only_pending_p8`.
- External and built-in two-way workflows retain B04/Table 26 provenance and
  ordinary checks without the contradictory built-in-coefficient hold. The
  Table 27 free-corner workflow returns zero negative coefficients and no
  restrained-corner torsion; an all-edge-continuous restrained panel resolves
  Table 26 case 1.
- The React workbench covers B02 action-location selection, the B04 coefficient/
  strip/torsion review surface, Table 27 free-corner topology, another restrained
  topology, ordinary shear and explicit punching boundaries, and an inadequate/
  review-required result. Stale input still disables passport export.
- Focused slab/capability semantics passed; focused slab FastAPI transport passed
  5 tests with 12 deselected; focused React passed 5 tests. Frontend lint, all
  244 React tests, TypeScript, and the production build passed. The quick gate
  passed 10/10.
- The initial full repository gate passed 29/30; its sole failure was traced to
  the two beam return-annotation changes introduced by slab-lineage commit
  `7bb1512f`. After the explicitly authorized surgical restoration to the
  origin/main module-qualified annotations, the narrow manifest check and final
  full repository gate passed 30/30 without editing the generated manifest.
- These are software and interface results only. Approved-scope normalized-data
  distribution permission passed on 2026-08-11. Per-release owner authorization
  and qualified structural-engineering review remain separate gates.
