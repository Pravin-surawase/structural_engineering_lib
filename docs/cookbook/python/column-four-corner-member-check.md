# Check a physical four-corner column member

**Type:** Guide
**Audience:** All Agents
**Status:** active
**Importance:** Medium
**Created:** 2026-11-07
**Last Updated:** 2026-11-07
**Related Tasks:** LIB-027-CLOSURE-C
**Abstract:** Run the physical column API with explicit bars, closed ties and independent principal-axis references

---

Use `column.load_four_corner_member` and `column.check_four_corner_member`
for the ordinary short braced rectangle with four equal corner bars. The
request derives the steel area and two-face calculation depth from actual
diameters, cover and corner inset. Supply a single principal bending axis
with compression and a moment magnitude. The example checks x and y as
separate actions on the same physical cage.

From the repository root, install the current source in a Python 3.11 or
newer environment and run the example.

```bash
python -m pip install ./Python
python Python/examples/four_corner_column_member.py --output-dir column-output
```

The directory contains matching JSON and HTML for five cases. The passing
case is 300 × 400 mm, 3,000 mm unsupported length, fixed at both ends, with
M25 concrete and Fe415 longitudinal bars. Four Ø20 bars give 1,256.637 mm²
of steel. A closed Ø8 tie has 300 mm pitch, 16 mm internal bend radius,
135° hooks and 48 mm tails. The declared project schedule requires 40 mm
nominal cover, 16 mm internal bend radius and 20 mm aggregate.

| Case | Expected status | Main result |
|---|---|---|
| `axis_x` | PASS | 500 kN, 50 kN·m, utilization 0.5088 |
| `axis_y` | PASS | Same cage and separate y-axis action, utilization 0.6419 |
| `overload` | FAIL | Both actions multiplied by three |
| `insufficient_tie` | FAIL | Ø4 ties at 350 mm |
| `missing_tie` | HOLD | Actual tie omitted, strength remains unevaluated |

## Physical inputs and schema

Use `FourCornerColumnInputV1.model_json_schema()` to obtain the complete
versioned input schema. Load either a mapping, JSON text, UTF-8 bytes or
a typed request with `load_four_corner_member`. A request round-trips
through `model_dump_json()` and the same loader.

| Group | Required inputs |
|---|---|
| `identity` | Family and case IDs, with optional member and source identifiers |
| `geometry` | `b_mm`, `D_mm`, `unsupported_length_mm`, an end condition and `braced=true` |
| `actions` | Positive compression `pu_kn`, nonnegative `moment_knm`, `bending_axis="x"` or `"y"` |
| `materials` | `fck_nmm2` from 15 to 80 and `fy_nmm2` from 250 to 550 |
| `reinforcement` | Equal bar diameter, nominal cover to the tie, corner inset, aggregate size, project cover and bend-radius requirements, their reference, and the actual tie |
| `tie` | ID, diameter, spacing, internal bend radius, closed state, hook angle and hook tail length |

Supported restraints are `FIXED_FIXED`, `FIXED_HINGED` and
`HINGED_HINGED`. Their recommended Table 28 effective length is checked
against both physical section dimensions. A slender section receives HOLD.
The supplied project cover requirement accounts for the applicable exposure
and fire basis. The supported ordinary column minimum is also checked.

The bar centroid offset is
`nominal_cover + tie_diameter + longitudinal_diameter/2 + corner_inset`.
With 2 mm inset the example gives 60 mm, placing the bars at
(60,60), (240,60), (240,340) and (60,340) mm. An x-axis check projects
them onto depths 60 and 340 mm. A y-axis check projects onto 60 and 240 mm.
Each projected layer has two bars.

The inset matters at a rounded tie corner. Setting it to zero in this
example fails the whole-bar enclosure check. The calculation also checks
each physical face for the 300 mm peripheral bar-spacing limit, clear
spacing, 0.8–4% supported steel ratio, minimum Ø12 longitudinal bars,
tie diameter, tie pitch, closure, bend fit and the supported 135° hook
with at least six tie diameters of tail. The 16 mm internal bend minimum
in this example comes from its declared project schedule. The supported
hook continuation must also fit within the shortest straight tie leg
between the corner bend tangencies, which is 172 mm for this cage.

## Result and report

`result.to_dict()` contains the original request, input SHA-256,
`family-design-result/v1`, `structural-result-envelope/v2`, named checks,
physical bar records and the reused P–M owner result. Read
`engineering_status` and `issues` before consuming the strength.
Inadequate provision produces FAIL. A declared missing tie produces HOLD.
Malformed fields and unsupported topology raise `InputContractError`.

`column.render_four_corner_member_html(result)` renders the same request,
bars, tie, checks, status and hash. Every report carries the selected
principal-axis and cage scope, source references and qualified-review state.
Joint anchorage, splices, serviceability, seismic confinement and the project
fire assessment require their respective evidence.

The independent reference solves the integrated strain-plane section and
intersects the demand ray continuously. The reused member owner samples 201
points and rounds its output. Both directions agree within the frozen
comparison tolerances. [Independent fixture](../../verification/library-027-four-corner-column.json)
· [Reference replay](../../verification/check_library_027_four_corner_reference.py)
· [Runnable example](../../../Python/examples/four_corner_column_member.py)

```bash
python docs/verification/check_library_027_four_corner_reference.py
```


## Six- and eight-bar tied rectangles

The 0.29 source supports eight equal longitudinal bars, six bars with the
left/right face midpoints omitted, and six bars with the top/bottom face
midpoints omitted. Use the separate `column.load_tied_rectangular_member` and
`column.check_tied_rectangular_member` entry points. Inspect the complete
request schema through `column.TiedRectangularColumnInputV1.model_json_schema()`.

Run the [example](../../../Python/examples/tied_rectangular_column_member.py)
against the 0.29 checkout or a local 0.29 installation.

```bash
python Python/examples/tied_rectangular_column_member.py --layout eight_bar --mx 50 --my 35 --output-dir column-output
python Python/examples/tied_rectangular_column_member.py --layout six_bar_omit_x_face_midpoints --mx -50 --my 35
python Python/examples/tied_rectangular_column_member.py --layout six_bar_omit_y_face_midpoints --mx 0 --my 50
```

Supply one factored compressive action and its simultaneous signed moments at
the checked station. Positive Mx compresses the top and positive My compresses
the left, using the same top-left coordinates as the cage. The strength result
reports each actual bar's contribution and the fixed-axial-load residual. It
checks the supplied pair using IS 456 Cl. 39.6 and compares the Cl. 25.4
minimum eccentricity independently on each principal axis.

The closed perimeter tie's schedule specifies diameter, pitch, bend radius,
and both end hooks for the open midpoint links. Identify each link by its
two opposite midpoint bars and axial offset within the pitch. The perimeter
tie and links occupy separate levels. The supported corner inset past the
inside tie face and bar radius is 0–2 mm. The checks cover bar fit, restraint
span, hook fit and clear spacing. Missing tie evidence produces HOLD and an
inadequate supplied detail produces FAIL. The scoped strength check is also
held if either axis is outside partial compression.

The JSON and HTML share the request hash, bar IDs and restraint paths. The
section schematic shows the checked cross section. Member-wide scheduling,
fabrication lengths, laps and joints require separate evidence.

| Cage | Mx capacity at 500 kN | My capacity at 500 kN |
|---|---:|---:|
| Eight bars | 152.541 kN·m | 102.738 kN·m |
| Six bars, left/right midpoints omitted | 152.469 kN·m | 84.176 kN·m |
| Six bars, top/bottom midpoints omitted | 122.595 kN·m | 102.711 kN·m |

The [independent case record](../../verification/library-029-col02-rectangular-column.json)
defines the exact dimensions, material laws, tie schedule, expected values
and negative controls. The earlier four-corner request and report remain
available through their existing entry points.

## Positioned mixed-bar rectangles

Use `column.load_positioned_rectangular_member` and
`column.check_positioned_rectangular_member` for a short braced rectangular
column with 9–32 explicitly positioned bars. Supply each bar's ID, diameter,
centre measured from the top and left, and outer or inner row. The bars use
one common longitudinal steel grade. The complete request schema is available
from `column.PositionedRectangularColumnInputV1.model_json_schema()`.

Supply the simultaneous factored compression and signed moments at one
station. Positive Mx compresses the top and positive My compresses the left.
At the supplied axial force, the solver finds each signed principal capacity
at zero orthogonal moment. The strength verdict uses the Cl. 39.6 interaction,
the capacity along the demand direction, and adverse signed minimum-eccentricity
checks. A failed local restraint check still leaves the section strength
available for diagnosis.

Supply a closed hoop and explicit open links between aligned bars on opposite
faces. Each outer intermediate bar needs a checked link. The hoop and links
lie at separate transverse levels within the pitch. Inner-row restraint uses
the checked outer row and the concrete-face clearance required by
IS 456 Cl. 26.5.3.2(b)(3). The result includes local counts by diameter, open-link
centreline lengths, and an HTML section schematic via
`column.render_positioned_rectangular_member_html`. Joint anchorage, laps and
member-wide fabrication quantities require separate checks.

Run the [example](../../../Python/examples/positioned_rectangular_column_member.py)
from the 0.29 checkout, or use it with a local 0.29 installation.

```bash
python Python/examples/positioned_rectangular_column_member.py --case admitted_12_bar --output-dir column-output
python Python/examples/positioned_rectangular_column_member.py --case original_50_mm
```

The admitted 450 × 550 mm cage has four Ø20 and eight Ø16 bars. At
`Pu = 800 kN`, the signed axis capacity magnitudes are 377.728 and
405.477 kN·m for positive and negative Mx, and 284.091 and 283.752 kN·m
for positive and negative My. The original 50 mm layout fails local
restraint. The [independent case record](../../verification/library-029-col03-mixed-column.json)
includes the geometry, centre-reflected cage and fivefold action case.

## Slender rectangular columns with actual bars

Use this workflow for one factored compression combination on a prismatic,
braced rectangular column. It accepts the existing six- or eight-bar tied
cage and the positioned cage with aligned links. Use
`column.load_slender_rectangular_member` to load the request,
`column.check_slender_rectangular_member` to check it, and the HTML and SVG
renderers to view the same result. The field schema is available through
`column.SlenderRectangularColumnInputV1.model_json_schema()`.

Verify the version and origin of the package with
`python -m structural_lib install-preflight --json`. The candidate
workflow appears in `python -m structural_lib capabilities --json` under
the column Python profiles. With the matching candidate installed, copy the
[example](../../../Python/examples/slender_rectangular_column_member.py)
and [frozen JSON](../../verification/library-029-col04-slender-column.json)
into a working directory and run:

```bash
python slender_rectangular_column_member.py --reference library-029-col04-slender-column.json --case minor_slender --output-dir column-output
```

Open `column-output/report.html` and `section.svg`. The report, drawing
and `result.json` share the input hash. The section identifies bars and ties.
The HTML also lists the action basis, analysis revision, checked moment pairs,
axis restraints and governing result.

### Worked first-order case

The 300 × 400 mm section has eight Ø20 bars and 500 kN axial compression.
The effective lengths are 3900 mm on x and 6000 mm on y, giving
slenderness ratios 9.75 and 20.0. Only y receives an additional moment.
The unsupported length used for minimum eccentricity is 6000 mm on both
axes, giving eccentricities 25.333 mm and 22.000 mm.

The signed end pairs at A and B are (−60, +25) and (−30, −25) kN·m.
The y moments reverse sign. The braced initial moment magnitude is
10 kN·m and the unreduced y addition is 30 kN·m, giving a 40 kN·m
equivalent component. The report keeps the two physical end pairs and
checks the equivalent (−60, −40) and (−60, +40) pairs without station
locations. The governing utilization is **0.73794**, with separate
minimum-eccentricity and local restraint results. The [independent replay](../../verification/check_library_029_col04_reference.py)
checks the signed capacities and action calculations against the frozen record.

Repeat with `--case overload` for strength FAIL, `--case stale_revision`
for HOLD, and `--case conflicting_summary` for a structured input error.
Use `--case supplied_second_order` to see the interior station govern using
the supplied deflection-aware actions with zero further addition. For a
custom check, save one complete request and pass it with `--input`.

First-order inputs need an explicit declaration of no transverse member
load. Supplied second-order inputs need a local-deflection basis, the current
analysis revision and the required critical stations. This profile uses
unreduced additional moments. Global sway, member shear, joint anchorage,
splices and member-wide fabrication have separate scope.
