---
owner: Main Agent
status: active
last_updated: 2026-09-30
doc_type: reference
task: COLUMN-AXIS-QUALIFICATION
---

# Slender-column axis qualification

The first local column consumer candidate corrected the signed end-moment load
path and Cl. 39.7.1.1 `Pb` definition but retained an outcome-changing single-`k`
defect. The separately identified axis correction now evaluates and applies
each plane's prescribed state. Its general engineering qualification remains
**HOLD** pending independent review and material/edition qualification. The
previous frozen consumer packet is preserved; this record does not change its
files or retrospectively alter its evidence.

## Mechanics and source

The [original IS 456 Cl. 39.7.1 and 39.7.1.1](https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf#page=84)
define additional moments in the respective bending planes and prescribe
concrete strain `0.0035` with outer tension-steel strain `-0.002` for `Pb`.
The controlled Amendment-5 consolidation was checked visually at printed
pages 71–72. Plane sections therefore locate the zero-strain axis separately
for the depth and outer steel layer in the corresponding plane. Under the
API's existing equivalent symmetric two-face idealization:

- x plane: `xu_x = (D-d')*0.0035/(0.0035+0.002)`;
- y plane: `xu_y = (b-d')*0.0035/(0.0035+0.002)`.

The section force is independently integrated for each orientation. The
selected integrated Fig. 21 concrete law and retained five-point steel law
are explicit assumptions. This is not validation of an arbitrary physical
reinforcement layout, nor replacement of a second-order frame analysis.

## Confirmed outcome-changing case

Inputs are `b=450 mm`, `D=300 mm`, M25/Fe415, `Asc=2700 mm2`, `d'=50 mm`,
`Pu=1000 kN`, `lex=4200 mm`, `ley=6300 mm`, unsupported length `6300 mm`,
braced, equal x end moments `40 kNm`, equal y end moments `112.3 kNm`.
The input contract does not enforce `D>=b`; this orientation is accepted.

The independent reference gives `Pbx=651.968030635258 kN` and
`Pby=702.825268537539 kN`, hence `kx=0.792440534474142` and
`ky=0.817227251845070`. The frozen preceding consumer applies `kx` to both additional
moments, producing `Muy=147.25 kNm`, interaction `0.9970` and `is_safe=True`.
Using the prescribed y-plane state gives `Muy=148.339721806368 kNm` and
continuous-capacity interaction `1.002920902985825`, unsafe. The independent
axial root residuals are below `2.3e-13 kN`; the discrepancy is not explained
by displayed rounding or the existing 50-interval capacity interpolation.

For the reciprocal orientation `b=300 mm`, `D=450 mm`, the common x-plane
factor is larger and can instead be conservative for the y-plane. Age of a
source or agreement between implementations does not resolve this axis
dependence. A square section with the same cover and equivalent reinforcement
has equal prescribed states; a one-slender-plane case needs the factor for
that actual plane. No blanket `D>=b` exclusion has been invented as a repair.

## Implemented correction and compatibility

Both `design_long_column` and `calculate_additional_moment` now evaluate the
two plane-specific states and apply `k_x` to `Max`, `k_y` to `May`. The public
yield-balanced PM point and nominal `Puz` remain separate. Existing `k` and
`Pb_kN` are explicitly x-plane aliases; they must not be used to recompute the
y-plane moment. New optional result fields `k_x`, `k_y`, `Pb_x_kN` and `Pb_y_kN`
expose both states in code, service and HTTP responses. The reduction method
is versioned `IS456_39_7_1_1_PER_AXIS_V1`. Unsupported equivalent two-face
geometry where cover is not below half of **both** dimensions raises a
dimension error; accepted rectangular orientations are not arbitrarily banned.

The independent fixture enforces the prescribed tension strains for both
planes. It includes 42 axis/curvature cases: swapped axes, global sign reversal,
single/double curvature, braced/unbraced paths, square equality and one-axis
slenderness. The previously retained long-column and golden cases use updated
plane-specific references without changing numerical tolerances or caps.
Core, service and HTTP evidence belongs to a new immutable revision; it does
not claim an older wheel has the repaired behavior.

The independent-review anchor uses x end moments `161 kNm` in the original
orientation and y end moments `161 kNm` after exchanging the axes and lengths.
Both corrected orientations give the corresponding augmented moment
`197.04 kNm`, transverse minimum-eccentricity moment `22.60 kNm` and
interaction `1.0013`, unsafe. Each applied state has
`Pb=702.825268537539 kN`, `k=0.817227251845070` in its own active plane.
The legacy scalar fields remain x-plane aliases even when only y is slender.

Local full-precision diagnostic evidence is preserved under
`external_data/library-evidence/96170d8/column-two-plane-assessment-20260930`.
The observation uses the frozen consumer wheel with SHA256
`c6fdda9aabde18a0b7417ca83b7dbbea52b15d0379a6849ab01b610af81ca0af`.

## Local qualification of the axis correction

The 312 affected core, service, return-contract, golden and HTTP checks passed.
A freshly built project-only wheel, installed into a separate temporary target
without downloading dependencies, passed all 151 independent column checks.
Its SHA256 is
`3458400840fee618b48488875904ee97950d7f909ce0c3f359fa7de46bdb1721`.
All 224 imported library modules originated in that target; the 196 existing
distribution identities were unchanged. The 13 existing family recipes retain
their expected outcomes: 11 PASS, one FAIL and one HOLD.

The formatter identified two test-only dictionary constructors after the wheel
snapshot. Their equivalent literal form was checked with the three affected
tests; the original tested source and final test revision are both retained.
The first essential-check run passed 11 of 12 checks: its sole failure required
staging this intended new document before API classification. The narrow repair
passed. Formatter/linter, architecture, imports, API contracts and schema
snapshots passed; no broad unchanged suite was repeated. The OpenAPI change
adds only the plane-factor fields to the two existing response models. There
are still 92 HTTP operations.

The immutable review packet is
`external_data/library-evidence/96170d8/column-axis-correction-20260930`.
It preserves the previous packets, original unsafe/safe axis-relabelled outputs,
independent fixture, raw corrected outputs, source and installed wheel, JUnit,
OpenAPI and combined/incremental diffs with hashes. No beam/flange behavior,
nominal column cap or steel law changed in this revision. Independent review
and the retained material/latest-amendment qualification gaps remain separate
from these completed local checks. Nothing has been pushed or published.

During preservation, 331 files were unavailable in the temporary build-source
directory; its 11 surviving selected files included the original tested
regression and independent fixture. The wheel and all 322 installed package
files were intact. The missing source files were recovered from the current
repository only after each hash matched the pre-build manifest. The durable
source therefore has all 342 recorded file identities. The cause of the
temporary loss has not been established; `source-recovery.json` retains the
exact recovered paths and provenance. Passed numerical tests were not repeated
for this byte-identical recovery.
