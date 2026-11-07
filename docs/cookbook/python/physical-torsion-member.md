# Verify a physical rectangular torsion beam

**Type:** Guide
**Audience:** All Agents
**Status:** active
**Importance:** Medium
**Created:** 2026-11-07
**Last Updated:** 2026-11-07
**Related Tasks:** LIB-027-CLOSURE-D2, LIB-027-CLOSURE-D3
**Abstract:** Physical torsion member with a separate, verified transient service basis and explicit unsupported-case HOLD.

---

## Run the worked profile

This standalone example uses the public beam, construction and reporting
operations. It verifies the D2 physical/ULS scope and keeps three D3
serviceability obligations missing. The expected result is **D2 PASS,
D3 HOLD, full member not evaluated, draft artifacts**.

```bash
python -m pip install ./Python
python -I Python/examples/physical_torsion_member.py --output-dir torsion-d2
```

From an installed wheel outside the checkout, copy only
[physical_torsion_member.py](https://github.com/Pravin-surawase/structural_engineering_lib/blob/main/Python/examples/physical_torsion_member.py)
and run it with the installed interpreter. The example needs the current
development build; the published 0.26.0 package predates these operations.
No optional report dependency is needed.

## Physical inputs and independent targets

The supplied rectangular beam is 300 × 400 mm, M25/Fe415. Four continuous
Ø20 bars have centres (50,50), (250,50), (50,350), (250,350) mm.
Nominal cover is 25 mm, maximum aggregate size 20 mm, and the declared
mild-exposure mix explicitly uses ordinary Portland cement at 300 kg/m³
and water/cement ratio 0.55. For Portland calcined clay limestone cement,
Amendment 6 reduces the maximum ratio to 0.50; the API checks this branch
and rejects unsupported cement identities rather than assuming ordinary cement.
These values are checked against Tables 5/16 and the bar-diameter cover rule.
The ordinary profile also checks the Amendment 6 cement ceiling of
450 kg/m³; special-consideration exceptions are outside this profile.

Support centres are 0 and 5000 mm. Their physical faces are -500/500
and 4500/5500 mm, giving a 4000 mm clear span. All main-bar paths run
from -450 to 5450 mm, giving 950 mm past each near face. Full design
tension stress is 361.05 N/mm²; Cl. 26.2.1.1 deformed-bar bond is 2.24 N/mm²,
so the unrounded required Ld is **805.915178571 mm** at all eight bar ends.
`AnchorageLocation.DIRECT_SUPPORT` uses this full development criterion,
requires actual support faces/centres, and credits no M/V reduction.

The supplied analysis applies 12 N/mm downward over the 5000 mm support
centre span at transverse eccentricity 50 mm. This deliberately retains
the supplied centre-span action basis. The separate Cl. 22.2 topology
effective-span value is 4350 mm; it is not substituted into those actions.
Closed-form static equilibrium supplies each concurrent source row,
including the two exact combined-moment peaks. The independent planar
solve cross-checks regular V/M stations; it supplies no torsional stiffness.

| Station (mm) | V2 (kN) | M3 (kNm) | Internal T (kNm) |
|---:|---:|---:|---:|
| 0 | 30 | 0 | 1.5 |
| 500, left face | 24 | 13.5 | 1.2 |
| 850, d inside face | 19.8 | 21.165 | 0.99 |
| 2431.372549, combined peak | 0.823529 | 37.471742 | 0.041176 |
| 2500 | 0 | 37.5 | 0 |
| 2568.627451, combined peak | -0.823529 | 37.471742 | -0.041176 |
| 4150, d inside face | -19.8 | 21.165 | -0.99 |
| 4500, right face | -24 | 13.5 | -1.2 |
| 5000 | -30 | 0 | -1.5 |

The governing primary equivalent moment is 37.528258362 kNm, slightly
above the plain-bending midspan value. Both peak rows are checked.

## Torque transfer into the receiving system

The declared global frame is right-handed: e1 along the main member,
e2 vertically upward, e3 transverse. External support torque equals
minus the sum of each upward reaction times its signed transverse arm.
**Both external support couples are -1.5 kNm.** The opposite signs of
the internal end-cut actions do not reverse the right-hand support couple.
The two support couples balance the applied +3 kNm total torque.

At each support, actual upward reaction lines at transverse offsets
-100/+100 mm carry 7.5/22.5 kN. Their sum is 30 kN. The opposite downward
loads enter a transverse 3000 mm receiver crosshead at its stations
1400/1600 mm. The crosshead is 1000 × 400 mm, M25/Fe415, with four
Ø20 bars on each face at section coordinates 100/400/700/900
mm and depths 95/305 mm. Both sections share the same physical top datum.
The staggered depths and horizontal positions
avoid the actual primary main bars and link planes in the support joints.
The transfer check binds the primary path request and verifies conservative
projected crossing clearance, including circular bends. The governing
clearance is 25 mm under the maintained ordinary bar-spacing criterion.
This is a geometric clearance check, not a receiver-joint capacity check.
The receiver's declared four active Ø8 legs at 100 mm
provide section shear reinforcement. Receiver geometry, load identity,
topology and source case are checked before section strength.

The transferred pair alone develops 14.5/15.5 kN receiver end reactions
and 21.7 kNm maximum moment. Receiver strength also includes its explicit
gross self-weight: 25 kN/m³, factor 1.5 and section 1000 × 400 mm give
15 N/mm factored UDL. Total receiver end reactions are 37/38 kN, maximum
moment 38.5 kNm and maximum shear 38 kN. No embedded-primary overlap is
deducted from gross self-weight. The public flexure and shear owners
check the actual section against these total loads. Reversing only the right
support couple fails both source-action and global torque equilibrium.

The interface stops at the receiver's end reactions and section-strength
checks. It supplies transfer demands to the supporting-system designer;
it does not qualify bearing/contact stresses, receiver end connections,
the remaining support members or foundations. No invented catalogue
capacity or approval flag is used.

## Cage, fabricated links and common paths

The actual two-leg Ø8 links have centre dimensions 242 × 342 mm and
internal bend radius 16 mm. Their five-bend fabrication path forms a
closed cage using two 90° hooks with 80 mm clear tangent tails, in planes
10 mm apart. This is an overlapping fabricated hoop, not a welded loop.
Cl. 26.2.2.4(b) needs 64 mm tails for this Ø8 ordinary detail. The pure
source helper also exposes 135°/180° tail limits of 48/32 mm and a
minimum internal radius of 4 mm under the stated mandrel convention.
The actual 90° fabrication geometry is the admitted path profile.

Fifty links are placed at 50..4950 mm, exactly 100 mm apart. The hook
check binds the actual resolved longitudinal IDs, centres, diameters and
end stations to the same arrangement and cage. Both faces' continuous
runs and all eight direct-support tension anchors use that arrangement.
There are 54 physical paths: four at 5900 mm and fifty links at
1325.286156126 mm each. Bar-path geometry and BBS use the same resolved
lengths and detail revision.

## APIs, held obligations and verification

The new reusable Python operations are `beam.check_closed_link_detail`,
`beam.check_mild_durability` and `beam.check_torsion_support_transfer`,
with public frozen request dataclasses. Their semantic results retain
effective inputs, source/method revisions, diagnostics and result identity.
Inspect `dataclasses.fields` or `inspect.signature` for their exact request
fields; `pydantic.TypeAdapter(RequestType).json_schema()` exposes the JSON
schema. The workflow example shows complete request construction.
No new HTTP or native-host route is claimed by this Python packet.

The profile freezes 31 expected leaves before execution. Twenty-eight D2
leaves qualify; flexural deflection, flexural cracking and torsional
serviceability remain missing for D3. An ordinary non-seismic
non-applicability result is qualified explicitly. The ordinary 19-leaf and
multilayer 27-leaf profiles remain unchanged.

The example writes `calculation.json`, `bbs.csv` and `report.html`, all
carrying the draft state. JSON retains the complete expected check set,
source actions, receiver results and physical paths. The HTML shows D2
separately from member acceptance. Quantities are the primary prism only,
before union with the supports; receiver reinforcement and overlap
measurement are excluded.

The independent [frozen inputs and targets](../../verification/library-027-torsion-physical.json)
and [standard-library replay](../../verification/check_library_027_torsion_physical_reference.py)
were prepared before production calculations. Tests replay adequate and
insufficient anchorage, short hooks, mismatched actual pitch, reversed
support couples, insufficient receiver/main steel, missing transfer
evidence, changed/stale receiver bindings, colliding support bars, both
torsion signs and zero torsion. D3 HOLD is
retained throughout. Its torsional serviceability method and applicable
criteria must be independently verified before full member acceptance.

## Complete the selected D3 service case

```bash
python -I Python/examples/physical_torsion_member.py --with-serviceability --output-dir torsion-d3
```

The expected result is **D2 PASS, D3 PASS, all 31 obligations qualified,
54 physical paths, issue_ready outputs, engineering approval unreviewed**.
The original command without the flag remains the D2 HOLD control.
`issue_ready` records completeness of this declared model and criteria;
engineering approval remains a separate result dimension.

The independently frozen [D3 reference](../../verification/library-027-torsion-serviceability.json)
and [standard-library replay](../../verification/check_library_027_torsion_serviceability_reference.py)
define the following demonstration assumptions. They are not project facts.

| Component | Unfactored UDL | Transverse eccentricity | Time basis |
|---|---:|---:|---|
| Permanent G | 5 N/mm: 3 self-weight plus 2 superimposed | 0 mm | Applied at concrete age 28 days |
| Imposed Q | 3 N/mm | 400/3 mm, inside the 150 mm half-width | Immediate response at application, age 3650 days |
| Finishes | — | — | Installed at age 56 days |

Total service load is 8 N/mm at resultant eccentricity 50 mm. Equal 1.5
factors give the original D2 12 N/mm at 50 mm, including every concurrent
V/M/T row. Sustained torque is zero; the full service end torque of 1 kNm
is retained as transient torque. The API requires application and assessment
ages explicitly. A transient flag alone cannot discharge the time basis.
Any finite imposed-load duration or permanent torque remains HOLD until
its torsional time-dependent response is qualified.

The receiving beams use the explicit identical, pinned-ended,
zero-settlement boundary from the demonstration analysis. Their actual
section, orientation, nodal restraints and loads are bound and compared.
Equal modeled receiver rotations cancel when deflection is measured
relative to the chord joining the **same physical edge** at the supports.
The calculation does not assume absolute primary-support rotations are
zero and does not qualify real column/foundation movements. Missing or
asymmetric boundary evidence retains HOLD.

## Service methods and criteria

Flexural response uses actual transformed compression and tension bars,
removing displaced concrete and neglecting tensile concrete. The fully
cracked inertia is a conservative lower bound within Annex C's inertia
bounds; no tension-stiffening benefit is used. The permanent section is
re-solved at `Ec/(1+1.6)` under Cl. 6.2.5.1/C-4, with the permanent
concrete stress checked against `fck/3`. The ultimate creep coefficient
is used as an upper bound at the selected assessment age.

Shrinkage uses the Cl. 6.2.4.1 strain 0.0003 and a conservative Annex C-3
single-face equivalent, ignoring beneficial compression steel **for this
shrinkage estimate only**. It does not extrapolate the source's
`pt-pc >= 0.25%` equation to zero difference. All creep and shrinkage are
counted after finishes, giving an upper bound rather than assuming a
measured finish-stage deformation.

The separately adopted torsional stiffness is the cracked secant model in
[Bruun, Kuan and Bentz (2020), Eq. 3](https://www.bar-lab.org/_files/ugd/a76105_c2e5f0130fd34dd48658126af2184844.pdf),
DOI [10.14359/51728290](https://doi.org/10.14359/51728290), PDF pages 4–6
and 12. This is supplementary research mechanics, not an IS 456 formula.
`GKcr = 4 Es A2³ / [p2² (1/rho_l + 1/rho_t)]`, where `A2` is the
area enclosed by corner longitudinal-bar centres. The cubic area power
is dimensionally required and reproduces the paper's rounded
104.1 × 10³ kNm² worked example. The selected beam gives
576.216741104 kNm². Integrating the actual service torque gives twist;
its vertical edge displacement is added conservatively to flexural
deformation at the same edge.

IS 456 Cl. 23.2 supplies the displacement criteria. Deformations retain
the actual 5000 mm analysis span; the shorter 4350 mm code effective
span supplies the conservative limits. No universal twist-angle limit
is invented.

Torsional crack control is a separate **indirect Annex-B B-5/B-6
service stress/detail compliance check**. It retains both-face equivalent
moments and closed-link demands, applies the M25/Fe415 Tables 21/22/24
limits, and rechecks the actual physical hooks/cage. Compression-steel
and concrete-shear benefits are conservatively ignored in this WSM
screen. This does not calculate or guarantee a torsional crack width.
The Annex-F result is explicitly flexural, using the elastic **surface**
strain with no tension-stiffening reduction; steel-bar strain is not
substituted for surface strain.

| Frozen service result | Value | Criterion |
|---|---:|---:|
| Final total edge deflection bound | 8.532890067 mm | 17.4 mm |
| After-finishes edge deflection bound | 4.653362991 mm | 12.428571429 mm |
| Flexural crack-width upper bound | 0.162898079 mm | 0.3 mm, mild/non-harmful |
| Relative midspan twist | 0.002169322602 rad | Assessed through edge displacement |
| Torsional edge displacement magnitude | 0.325398390 mm | Included in both displacement checks |

## API, controls and outputs

`beam.TorsionalServiceabilityRequest` binds the current D2 support/path
and actual hook requests, distinct normalized total/permanent snapshots,
the explicit `TorsionServiceHistory`, and a physical edge offset.
`beam.check_torsional_serviceability` returns its source/method revisions,
service-state values, indirect WSM rows, and bound `deflection` and
`flexural_crack` OperationResults for the existing member leaves.
Use `TypeAdapter(TorsionalServiceabilityRequest).json_schema()` for the
complete machine-readable contract and strict JSON round trips.

`run_workflow(include_serviceability=True, load_n_per_mm=21)` is an
important negative control: D2 strength still passes, but Annex-B service
compression exceeds 8.5 MPa, so D3 and the member fail and outputs remain
draft. `omit_service_history=True`, missing service evidence, nonzero
permanent eccentricity, stale/conflicting rows, missing peak stations,
unqualified duration and unknown/asymmetric receiver boundaries retain HOLD.
Zero and reversed torsion preserve their real signs and complete the
same supported service workflow.

The JSON, HTML and BBS retain the same 31 obligations, actual paths,
steel lengths/mass, primary-prism quantity policy and input/result
identities. Unsupported service conditions cannot produce issue-ready
outputs. Receiver connections, bearing/contact, foundations and
professional approval retain their existing boundaries.
