---
owner: Main Agent
status: active
last_updated: 2026-09-30
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

## Annex G branch and equilibrium correction — 30 September 2026

The existing ordinary web-neutral-axis solver incorrectly reused the limiting
`Df/d <= 0.2` criterion. Direct inspection of the original Annex G, printed
pages 96–97 of the controlled Amendment-5 consolidation, confirms that G-2.3
instead uses `Df/xu <= 0.43`. G-2.2 and G-2.2.1 retain the distinct limiting
criterion. The reference source is the
[original IS 456 Annex G](https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf#page=109).
The fixture records the controlled source hash and edition limitation; this
packet does not certify the latest complete amendment set.

Use mechanics to derive and independently check the calculation; the original
standard defines its code-specific requirements. Inspect comparator source and
assumptions before treating agreement as evidence. Independent benchmarks and
tests must check the resulting forces, moments and domains. NPTEL remains a
supporting reference, not the default authority. Valid citations are retained.

Lengths are in mm, stresses in N/mm², forces in N and moments in Nmm before
conversion to kN·m. For the existing rounded Annex G code-design profile:

- `Cw = 0.36*fck*bw*xu`, acting at `0.42*xu` from the compression face;
- `Cf = 0.45*fck*(bf-bw)*yf`, acting at `yf/2`;
- `Mu = Cw*(d-0.42*xu) + Cf*(d-yf/2)`;
- `Ast = (Cw+Cf)/(0.87*fy)` under the prescribed yielded-tension idealization;
- ordinary G-2.3 state: `yf=Df` when `Df/xu<=0.43`, otherwise
  `yf=min(0.15*xu+0.65*Df,Df)`;
- limiting G-2.2 state: use `xu_max` and the separate `Df/d` criterion.

In each ordinary branch `yf=a*xu+c`, so the moment is quadratic in `xu`.
The stable smaller root is evaluated only within its actual branch and below
the limiting depth. Its demand residual must be within
`max(1e-6 Nmm,1e-12*abs(Mu))`. This is floating-point precision for a stipulated
law, not a claim of physical accuracy. No mesh, iterative fallback endpoint or
invented interpolation replaces the source equations. When the whole limiting
compression zone lies in the flange, G-2.1 uses width `bf`; the unchanged
rectangular compression-steel routine is reused above its limit. The existing
conservative `4%*bw*D` flanged doubly-reinforced cap is retained separately.
Minimum/maximum steel conventions are not globally reconciled by this packet.

For `bw=230`, `bf=1000`, `d=450`, `Df=60`, `D=500`, M25/Fe415:

| Source demand (kN·m) | Source xu (mm) / Ast (mm²) | Previous xu (mm) / Ast (mm²) |
|---|---|---|
| 256.49463375 | 80 / 1682.280847528 | 60 / 1783.547985044 |
| 307.38153375 | 120 / 2055.567095970 | 106.155… / 2048.169695890 |

The rounded equations have small gaps at the flange/web interface, the `0.43`
switch and some ordinary/limiting transitions. The independent selected gaps
are `0.49896`, `0.235721663737155` and `1.404202078125 kN·m`, respectively.
Demands inside them now return `E_FLEXURE_005`, no solved `xu`/steel, and
`is_safe=False`. These are unsupported code-profile states, not claimed
convergence failures of a continuous exact concrete law. The previous solver
returned safe without satisfying the relevant source equation.

The frozen reference evaluates 100 known-depth states using 60-digit Decimal
force and lever-arm arithmetic with no production imports. It also retains
three unsupported gaps and geometry containing the limiting neutral axis.
Core and composed-service checks retain Table 19 domain failures when derived
steel percentage is outside `0.15–3.0%`; successful flexure must not erase a
separate unsupported shear lookup. The original diagnostic and corrected
outcomes are preserved locally under
`external_data/library-evidence/96170d8/flange-correctness-20260930`.

The local candidate passed 185 focused source checks and 106 checks against
its separately installed wheel. The wheel SHA256 is
`9374507e52688478c3fba03b2502c0e75958226e51e7f811706ebbadbe0933ad`.
All 223 imported package modules originated in the isolated target; no
checkout fallback occurred. The 13 existing family recipes retained their
expected 11 PASS, one FAIL and one HOLD outcomes. The existing 196-distribution
environment and its `.pth` identities were unchanged. Build/install used
offline `--no-index --no-deps` commands with existing build tools. The wheel,
342 source files, installed package, JUnit, commands and raw observations are
preserved locally with hashes; no publication followed.

Across the 100 independent known-depth states, the largest raw moment residual
is `1.1920928955078125e-7 Nmm` and force residual is
`1.1641532182693481e-10 N`. The composed T-beam consumer retains 70 PASS,
29 Table 19 domain failures and three unsupported flexure failures. One
zero-overhang case is a core rectangular-geometry control, outside this
composed T-beam test packet. Non-finite utilization values in failed results
are explicitly tagged in JSON, not discarded. The first raw observer rounded
`Df/xu` just above `0.43` at eight exact-boundary states; its initial outputs
remain preserved. The corrected observer evaluates the equivalent
`xu >= Df/0.43` condition, consistent with the independently frozen inclusive
Decimal boundary states. No production revision was made to fit that observer.

The essential check batch passed 11 of 12 checks before the new test's caller
was reflected in the generated API ledger. Canonical regeneration and the
classification recheck passed. The only semantic ledger change is that new
maintained caller; public owners, signatures and facade projections remain
unchanged. The other passed checks were not rerun. All 23 reviewed column
files and the frozen column evidence remain separate from this flange packet.

Unmodified rcdesign evidence for the two anchors gives integrated concrete
moments `276.747177415497` and `316.346535554847 kN·m`, respectively. Its
literal Fig. 21 integration is a different model from these rounded Annex G
equations. Preserve those raw differences; agreement is not authority and the
comparator is not an Annex G oracle. Closed-form algebra is exact for each
chosen law; model fidelity, numerical error and code-design conventions remain
distinct. This correction does not silently introduce a new integrated beam
analysis profile or re-open the completed physical multilayer beam workflow.

The necessary next bounded packet is material qualification followed by SLS
reconciliation: identify the actual steel laws and supported grades; verify
sign, yield/clipping, design factors and strain domains against original
definitions and pinned comparator source; then trace the maintained service
checks' stress/strain inputs and load level. ULS section strains must not be
inferred to be service strains. Native differences and unsupported outcomes
remain evidence until a specific source-backed correction is established.
No new serviceability or beam features, blanket material switch, publication
or whole-library completion claim follows from these local checks.

The estimated next effort is 2–4 hours for the steel/source profile matrix and
2–4 hours for the existing SLS load-level/input trace, with another 2–6 hours
only for reproduced outcome-changing corrections and their focused evidence.
These are uncertain development estimates, not an accepted programme. Inputs
are the controlled standard/amendments, inspected SP16 ordinate provenance,
the already installed pinned comparator, and current supported APIs. Acceptance
requires named factors/strain domains, independent full-precision anchors and
residuals, correct signs and clipping, preservation of code-design conventions,
and explicit unsupported domains. A source ambiguity narrows the supported
claim rather than becoming an invented engineering requirement.

The executable material trace starts at `codes/is456/materials.py`,
`codes/is456/common/stress_blocks.py` and their maintained column and
compression-steel callers. Existing independent sensitivities include the
Fe250 definite-yield/five-point difference at strain `0.001`, the omitted
HYSD knot near strain `0.003`, and the Fe550 ideal-plastic fallback at strain
`0.0025`. Classify their declared families and source domains before changing
any profile. The SLS trace starts at `codes/is456/beam/serviceability.py`:
the legacy Branson stiffness is attributed to Annex C despite differing from
C-2.1; duration, creep and shrinkage models also need their own source and
service-load basis. Reuse the preserved independent Annex C anchors and the
already explicit-basis physical SLS owner. Do not fold those models into a
decimal cleanup or infer service stresses from ULS section strains.
