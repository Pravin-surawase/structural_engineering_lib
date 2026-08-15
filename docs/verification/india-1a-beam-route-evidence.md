---
owner: Main Agent
status: active
last_updated: 2026-08-15
doc_type: reference
complexity: advanced
tags: [is456, beam, flanged, verification, india-1]
---

# INDIA-1A Sagging T-Beam Route Evidence

## Supported outcome

`design_flanged_beam_is456()` composes one monolithic sagging T-beam case from
already-factored supplied actions. It calculates the effective flange width,
runs the maintained flanged-flexure design, evaluates shear using the web
width, and optionally runs the maintained span/depth and crack-width checks
when their complete geometry and service inputs are supplied.

This is software verification evidence. It is not professional design approval;
the cumulative qualified structural-engineering review remains required before
stable or engineering-use approval.

## Governing source and units

| Result | IS 456:2000 reference | Input units | Output units |
|---|---|---|---|
| Effective flange width | Cl 23.1.2 | `bw`, span, flange thickness and overhangs in mm | mm |
| Flanged flexure | Cl 38.1 and Annex G | geometry in mm, `Mu` in kN·m, strengths in N/mm² | steel in mm², capacity in kN·m |
| Web shear | Cl 40 and Tables 19/20 | `Vu` in kN, `bw` and `d` in mm | stress in N/mm², spacing in mm |
| Level-A deflection | Cl 23.2 | span and effective depth in mm | span/depth result |
| Crack width | Annex F | explicit geometry in mm and strain or service stress | crack width in mm |

The repository implements normalized formulas and identifiers without copying
protected standard prose or page images.

## Independent benchmark

The accepted B3 benchmark in
[`validation-pack.md`](validation-pack.md) supplies `bw=300 mm`, physical
`bf=1000 mm`, `Df=150 mm`, `D=550 mm`, `d=500 mm`, `Mu=200 kN·m`, M25 and
Fe500. With an effective span of `6000 mm` and `350 mm` overhang on each side:

- physical flange width = `300 + 350 + 350 = 1000 mm`;
- T-beam code limit = `300 + 6000/6 + 6(150) = 2200 mm`;
- effective flange width = `min(1000, 2200) = 1000 mm`;
- accepted flexure targets are `Mu,lim=835.04 kN·m`,
  `Ast=956.6 mm²`, and `xu=46.24 mm`;
- for the added `Vu=150 kN` combined-route check, nominal shear stress is
  `150000/(300×500) = 1.000 N/mm²`, proving that shear uses the web width
  rather than the effective flange width.

The focused test allows the benchmark source precision: `±1 kN·m` for
`Mu,lim`, `±10 mm²` for `Ast`, and `±1 mm` for `xu`; the web-shear identity
uses floating-point approximation only.

## Fail-closed boundary

| Input or interpretation | Outcome |
|---|---|
| Monolithic T-beam, sagging, two positive flange overhangs | Supported |
| Single supplied factored case | Supported |
| Caller-supplied governing factored envelope result | Supported as supplied; envelope completeness is not validated |
| Route asked to generate an envelope | `LOAD_ENVELOPE_SCOPE_HOLD` |
| L-beam | `FLANGED_SECTION_SCOPE_HOLD` pending its own benchmark |
| Hogging or flange in tension | `FLANGED_MOMENT_SCOPE_HOLD` |
| Non-zero flanged torsion | `FLANGED_TORSION_SCOPE_HOLD` |
| Compatibility/equilibrium redistribution selection | `TORSION_REDISTRIBUTION_SCOPE_HOLD` |
| Serviceability geometry inconsistent with strength geometry | `SERVICEABILITY_GEOMETRY_HOLD` |
| Hollow/box, deep, prestressed, axially loaded, or composed flanged detailing | Explicitly retained hold |

## Verification commands

```bash
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh -m pytest Python/tests/integration/test_flanged_beam_service.py -q
./scripts/python_runtime.sh -m pytest Python/tests/integration/test_flanged_beam.py Python/tests/regression/test_verification_pack.py -q
./scripts/python_runtime.sh -m pytest Python/tests/integration/test_capability_semantics.py Python/tests/test_indian_code_manifest.py -q
./scripts/python_runtime.sh scripts/generate_indian_code_manifest.py --check
```

Safe benchmark, unsafe shear, effective-width boundary, explicit
serviceability, geometry mismatch, L-beam, hogging, envelope-generation,
flanged-torsion, and redistribution-hold cases are all covered.
