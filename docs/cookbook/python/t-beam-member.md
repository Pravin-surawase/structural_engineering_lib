# Verify an ordinary physical T-beam member

**Type:** Guide
**Audience:** Users
**Status:** active
**Importance:** Medium
**Created:** 2026-11-07
**Last Updated:** 2026-11-07
**Related Tasks:** LIB-027-PACKET-E
**Abstract:** Source-bound T geometry, flange provision, zero-torque admission, service screening and matching installed consumer artifacts.

---

## Run the two complete cases

This example composes the public beam, construction and reporting operations
for one ordinary, symmetric, monolithic, simply supported sagging T profile.
Its 30 obligations comprise 18 member rules, including ordinary seismic
non-applicability, and full tension development at 12 actual bar ends.
Engineering approval remains **unreviewed**, even when every leaf qualifies.

Use the current development build. Published 0.26.0 predates these APIs;
development-wheel metadata may still say 0.26.0 until Goal 5 prepares the
versioned release candidate. Packet E does not publish 0.27.

```bash
python -m pip install ./Python
python -I Python/examples/t_beam_member.py --case main --output-dir t-main
python -I Python/examples/t_beam_member.py --case width-limited --output-dir t-wide
```

For an external consumer, install the retained qualified development wheel
in a fresh environment, copy only
[t_beam_member.py](https://github.com/Pravin-surawase/structural_engineering_lib/blob/main/Python/examples/t_beam_member.py)
outside the checkout, and run it with that installed interpreter. The base
package is sufficient; no report, plotting, NumPy or CAD extra is required.

Both cases should report `PASS`, 30/30 qualified and `issue_ready`. Outputs are
`calculation.json`, `bbs.csv`, `report.html`, plus standalone JSON request
files and their JSON schemas in `requests/` and `schemas/`.

## Physical inputs and the three widths

All lengths are mm, forces N/kN, moments Nmm/kNm and stresses N/mm².
The section datum is x from the **physical flange-left**, y from the flange
top; station zero is the left bearing centre. The web projection subtracts
the explicit web-left offset and retains every actual bar/path identity.

| Input | Main | Width-limited |
|---|---:|---:|
| Physical flange width | 1000 | 2500 |
| Effective compression width | 1000 | 2200 |
| Web width / overall depth / flange thickness | 300 / 550 / 150 | 300 / 550 / 150 |
| Web-left offset in global section coordinates | 350 | 1100 |
| Clear distances to both adjacent beams | 700 / 700 | 2200 / 2200 |
| Analysis bearing-centre span / actual zero-moment distance | 6000 / 6000 | 6000 / 6000 |
| Clear span / code effective span | 5000 / 5500 | 5000 / 5500 |

This is the adjacent-beam T classification. The supplied clear distances
bound the owned flange strip, and Cl. 23.1.2 gives
`bf_effective = min(bf_physical, bw + l0/6 + 6*Df)`.
An isolated T requires its different source basis; missing adjacency is HOLD.
Do not substitute code effective span 5500 for the actual `l0=6000`.

M25 concrete, uncoated Fe415 steel and `Es=200000 N/mm²` are explicit.
The mild-exposure OPC mix is 320 kg/m³ cement, water/cement 0.50 and 20 mm
maximum aggregate. Beam nominal cover is 25 mm; the separately owned slab
strip declares its own 20 mm nominal cover.

Four bottom Ø20 bars have web-local x values 50, 116.666666667,
183.333333333 and 250, at y=500. Two top Ø16 bars are at web x=50/250,
y=50. Add the web-left offset to obtain every global x. The actual T
material/cover owner independently checks those bars and the resolved curves;
a rectangular bounding box cannot qualify a bar beside the web below `Df`.

Both supports are 1000 mm wide, centred at 0/6000, with faces
-500/500 and 5500/6500. All six beam bars run from -450 to 6450.
Full design-tension development is checked at both near support faces:
available 950 mm, required **805.915178571 mm** for Ø20 and
**644.732142857 mm** for Ø16. No M/V reduction or borrowed compression label
is used. The receiving support system remains a separate design owner.

Forty Ø8 ordinary web links occur at stations 75 through 5925 at 150 mm
pitch. Their web-local centre dimensions are 242 × 492 mm, internal bend
radius 16 mm and centreline radius 20 mm. Two actual 90° hooks have 80 mm
tangent tails against a 64 mm minimum, with closure planes 10 mm apart.
The shared hook owner binds **all six** actual longitudinal IDs and their
coordinates, marks, ends and revision; the four-bar torsion case remains valid.

## Actions, strength and serviceability

The independent reference includes these values:

| Quantity | Main | Width-limited |
|---|---:|---:|
| Actual concrete area (mm²) | 270000 | 495000 |
| Self-weight at 25 kN/m³ (N/mm) | 6.75 | 12.375 |
| Permanent G including 2 N/mm superimposed (N/mm) | 8.75 | 14.375 |
| Imposed Q / total SLS (N/mm) | 3 / 11.75 | 3 / 17.375 |
| ULS, `1.5G + 1.5Q` (N/mm) | 17.625 | 26.0625 |
| ULS maximum M / absolute V (kNm / kN) | 79.3125 / 52.875 | 117.28125 / 78.1875 |
| No-slab-credit supplied-bar resistance (kNm) | 217.134250281 | 226.198874914 |
| Web shear resistance (kN) | 210.174853995 | 210.174853995 |
| No-slab-credit service NA (mm) | 89.602362333 | 62.938638865 |
| No-slab-credit cracked I (mm⁴) | 1937413084.320837 | 2103672726.442183 |
| Selected soffit crack upper bound (mm) | 0.083983421 | 0.121546385 |

The normalized ULS, total-service and permanent snapshots retain distinct
case/result identities and concurrent end, support-face and exact midspan
rows. Their values must reconstruct physical-width self-weight and the
declared components/factors. Missing, stale or conflicting rows remain HOLD.
The longer 6000 mm bearing-centre action model is retained conservatively;
the code effective span is independently derived from actual supports and d.

`check_t_zero_torsion` verifies zero torque in **all three snapshots**.
It is a new Python T-profile demand-admission operation, with semantic ID
`is456.beam.t_zero_torsion.check/v1`, not a torsion-resistance calculation.
Its output explicitly says `zero_demand=true` and
`torsion_resistance_computed=false`. It has no C#/.NET/Excel projection or
new shared WP02 T-capacity-parity claim. Existing `check_torsion` and its
native counterpart retain their rectangular resistance scope. Nonzero beam
torsion, axial/weak-axis actions and beam-axis hogging are unadmitted/HOLD.

Deflection uses the **complete flanged span/depth screen** in 23.2.1,
including Figs. 4, 5 and 6. Percentages use `bf_effective*d`, not `bw*d`.
The frozen no-enhancement source envelope is tension factor 1 for
`pt<=0.4%` and actual service `fs<=145 N/mm²`, compression factor 1,
and flange factor 0.8 on the plotted `0<=bw/bf<=0.3` branch.
Both cases give `L/d=11 <= 20*1*1*0.8=16`.
Outside that envelope the provider retains HOLD instead of extrapolating.

This is deemed-to-satisfy screening for the declared ordinary gravity
history, **not calculated deflection**: `calculated_deflection_mm` is null.
G begins at 28 days, finishes at 56 and assessment is at 3650 days; applicable
thermal actions are excluded from this selected profile. No rectangular
Annex-C stiffness, creep/shrinkage shortcut or torsional model is borrowed.

Crack evidence independently solves the actual T compression geometry and
positioned-steel transformed section, removing displaced compression
concrete and ignoring tension concrete. It retains full elastic surface
strain without tension-stiffening credit. Web soffit edges and all adjacent
bar midgaps form the complete envelope for the admitted equal-diameter,
single-depth bottom row. Mild, nonharmful cracking uses the explicit 0.3 mm
code criterion. Other bottom-row layouts require their own surface envelope.

## Required local flange provision and ownership

Monolithic casting and actual slab-main direction are required evidence.
Here slab main bars run **perpendicular** to the beam; the conditional
parallel-main Fig. 3 requirement is explicitly non-applicable. A parallel-main
or non-monolithic input retains HOLD for its separately qualified profile.

The flange still has an actual separately owned local strip. Three adjacent
webs define two transverse spans of 1000 or 2500 mm. Its main Ø10/150 bars
are at y=35/115; Ø8/200 parallel distribution bars are at y=49/101.
Both faces/directions satisfy their supplied geometry, slab minima, spacing,
diameter, cover and nonintersection checks. A 600 mm repeating strip is
checked for both transverse bending signs against a conservative
`factored_area_load * 600/1000 * span²/8` envelope, corroborated by the
two-span continuous analysis. The resulting envelopes are 0.984375 and
4.04296875 kNm; supplied strip resistance is 12.652188666 kNm per sign.
Conservative concrete shear and every transverse full-stress anchorage
are also checked. This local provision does not qualify the whole floor.

Full external slab-domain paths remain in JSON: 94 transverse main runs,
plus 22/54 distribution runs for main/wide. The declared transforms tie them
to the beam for actual 3D crossing checks. Their steel is **excluded from
beam BBS and steel quantities** and is not credited in beam design resistance.
Five/thirteen parallel slab bars per y layer lie in the owned physical flange;
five/eleven per layer lie within the respective effective compression strip.
The latter receive an actual-y ductility/capacity and cracked-service audit.
Wide outer bars remain physical slab records outside that design strip.
The report retains both service models and selects the larger crack result.

The six beam bars are all in the web cage. Reclassifying outer flange bars
as beam longitudinal reinforcement requires the flange-enclosing arrangement
in 26.5.1.4; this example does not grant that different profile.

Native changes are limited to append-only `BarPathRole.FlangeTransverse` and
`BarPathRole.FlangeDistribution` metadata compatibility and the shared
WP06/WP07 schemas. Two role-preservation tests and required hosted .NET
checks gate integration; this adds no native T-member or torsion-capacity API.

Concrete uses the non-overlapping **physical** flange-plus-web-below union
over 7000 mm: 1.89/3.465 m³. The T owns that union; a supporting-system
assembly must exclude it to avoid overlap. Only clear-span web/flange
soffits and web sides are exposed formwork: 9/16.5 m². Bearing, internal
web/flange and continuing slab interfaces are excluded. Effective compression
width never becomes concrete/formwork/self-weight width. The unchanged web
cage gives 46 beam paths and 115.499264221 kg scheduled steel in both cases.

## Inspect schemas and rerun a public request

The exported schemas are ordinary Pydantic dataclass JSON schemas. Parsing
validates shape/types; the operation then evaluates physical/code admissibility.
For example, after copying the example and generating `t-main`:

```python
from pathlib import Path
from pydantic import TypeAdapter
from structural_lib import beam

request = TypeAdapter(beam.TServiceabilityRequest).validate_json(
    Path("t-main/requests/t-serviceability.json").read_bytes(), strict=True
)
result = beam.check_t_serviceability(request)
print(result.engineering, result.result_id)
```

The exports also include `TGeometryCheckRequest`, `TBeamActionBasisRequest`,
`TFlangeParticipationRequest`, `TLateralStabilityRequest` and the complete
`MemberDesignRequest`. Zero-torque admission reuses the typed action request.
Section, load and external-strip records appear as nested schema definitions.
Direct paths, projected paths, scoped member leaves and package dependencies
retain their original semantic identities through strict JSON round trips.

## Verify genuine failure and missing-evidence behavior

```bash
python -I t_beam_member.py --probe short-hook --output-dir t-short-hook
python -I t_beam_member.py --probe service-fail --output-dir t-service-fail
python -I t_beam_member.py --probe missing-service --output-dir t-held
```

`overload`, `insufficient-bars`, `short-anchor`, `short-hook`, `shoulder-bar`, `end-cover`
and `depth-conflict` retain a failed required check and draft artifacts.
`end-cover` extends the bars to the declared concrete end face: all full-Ld
checks pass, but the physical end-cover check correctly fails.
`service-fail` supplies a deliberately stricter **0.05 mm test criterion**;
strength still passes and the real crack check fails. It is not a project
criterion inferred for the user. Missing support, flange or service evidence
retains HOLD/draft. Offending bars, tails, depths, criteria and paths remain
visible in JSON, CSV and HTML.

The workflow summary reports FAIL when a trusted required leaf fails. If
other evidence is incomplete, the generic member's original engineering
dimension remains `not_evaluated` and completeness `partial`; both are
printed and serialized unchanged. A FAIL summary does not erase a HOLD,
and all such outputs remain draft. `issue_ready` requires every obligation.

The [independent reference](../../verification/library-027-t-beam-member.json)
and [stdlib-only checker](../../verification/check_library_027_t_beam_reference.py)
disclose shared IS equations/data, source hashes and numerical tolerances.
The [consumer verifier](../../verification/replay_library_027_t_member.py)
replays both positive cases, all named probes, strict public requests, schemas,
source/width controls and each export format. It also checks a component
web-shear trap; that trap is not another qualified physical cage/member.
Use `--require-site-packages` for the neutral installed-wheel qualification.

Packet B's other T compression branches remain section regression evidence.
This complete member profile does not add nonzero T torsion, beam-axis
hogging, L sections, axial/biaxial/seismic design, arbitrary layouts/openings,
splices/cutoffs, whole-floor design or support-system approval.
Goal 5 still qualifies both exact versioned 0.27 archives before publication.
