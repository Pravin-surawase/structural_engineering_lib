# Verify a physical rectangular torsion beam

**Type:** Guide
**Audience:** All Agents
**Status:** active
**Importance:** Medium
**Created:** 2026-11-07
**Last Updated:** 2026-11-07
**Related Tasks:** LIB-027-CLOSURE-D2
**Abstract:** D2 physical and strength workflow with signed support transfer and explicit D3 HOLD.

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
and run it with the installed interpreter. The example needs the build
containing D2; the published 0.26.0 package predates these operations.
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
The planar solver supplies V/M only. Independent static torque equilibrium
supplies T, with all three components bound to each normalized source row.

| Station (mm) | V2 (kN) | M3 (kNm) | Internal T (kNm) |
|---:|---:|---:|---:|
| 0 | 30 | 0 | 1.5 |
| 500, left face | 24 | 13.5 | 1.2 |
| 850, d inside face | 19.8 | 21.165 | 0.99 |
| 2500 | 0 | 37.5 | 0 |
| 4150, d inside face | -19.8 | 21.165 | -0.99 |
| 4500, right face | -24 | 13.5 | -1.2 |
| 5000 | -30 | 0 | -1.5 |

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
Ø20 bars on each face at transverse section coordinates 50/350/650/950
mm and depths 50/350 mm. Its declared four active Ø8 legs at 100 mm
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

The profile freezes 29 expected leaves before execution. Twenty-six D2
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
evidence, changed/stale receiver bindings, and zero torsion. D3 HOLD is
retained throughout. Its torsional serviceability method and applicable
criteria must be independently verified before full member acceptance.
