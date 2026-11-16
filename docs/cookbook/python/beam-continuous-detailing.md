---
owner: Main Agent
status: active
last_updated: 2026-11-13
doc_type: guide
complexity: advanced
tags: [beam, detailing, anchorage, bbs, is456]
---

# Schedule continuous bars across two beam spans

Use `beam.load_continuous_detailing` and `beam.check_continuous_detailing`
with a two-span member, current supplied actions, continuous straight bars
and a link placement grid. The link input declares
its ordinary two-hook path and a fabrication source reference.

Run the [worked example](../../../Python/examples/beam_continuous_detailing.py)
with the [frozen cases](../../verification/library-029-beam05-member-detailing.json).

```bash
python beam_continuous_detailing.py --reference library-029-beam05-member-detailing.json \
  --case continuous --output-dir continuous
python beam_continuous_detailing.py --reference library-029-beam05-member-detailing.json \
  --case short_anchor --output-dir short-anchor
python beam_continuous_detailing.py --reference library-029-beam05-member-detailing.json \
  --case missing_link --output-dir missing-link
```

The continuous BEAM01 cage has six Ø20 longitudinal bars, each 8,436 mm
long, and 28 Ø8 links spaced at 300 mm. Each link has two physical hook
tails in separated planes. The resolved cut length is 1,582.175 mm per
link. The [independent replay](../../verification/check_library_029_beam05_reference.py)
derives these lengths from straight segments and tangent bend corrections.
The total theoretical steel mass is 142.307 kg at 7,850 kg/m³.

The checked action rows drive strength and anchorage. Physical bar path,
link enclosure, hook tails and placement must also pass before BBS and
SVG are available. The report, drawing and BBS use the same input hash,
and the schedule identifies its resolved path result. The short-anchor
case gives FAIL and the missing link detail gives HOLD. Both still produce
an HTML review report.

This example uses the original rectangular schema and its review elevation.
The route also accepts prismatic web cages with actual layers and optional
monolithic flanges. Serviceability is a separate calculation.

## Detail an L beam with two bottom layers

Run the same example against the [flanged and multilayer references](../../verification/library-029-beam05-flanged-detailing.json).

```bash
./scripts/python_runtime.sh Python/examples/beam_continuous_detailing.py \
  --reference docs/verification/library-029-beam05-flanged-detailing.json \
  --case l_multilayer --output-dir output/beam05-l-multilayer
```

Keep the outer detailing schema and set `member.schema_version` to
`is456-layered-continuous-beam-check/v1`. Use `member.width_mm` for the
web and measure bar centres from the web's left edge and the section top.
Number each face's layers from the outside inward. Supply the physical
overhangs, flange thickness and distance between zero-moment points
through `member.flange`. Omit `flange` for a rectangular multilayer
member. Declare both spans, both sides of the internal centreline and all
four support faces in every ULS combination. Supply one concurrent
`mu_knm`, `vu_kn`, `tu_knm` row for each station and combination.

The example uses a 300 × 600 mm web with a 300 mm right overhang and a
120 mm flange thickness. Two 4 m spans carry factored uniform loads of
24 and 32 kN/m in U1 and U2. For U2, three-moment equilibrium gives an
internal centreline moment of −64.0 kN·m, retained as diagnostic evidence.
The internal support faces see −52.36 kN·m and shears of −75.2 and
+75.2 kN. The sagging peak is +36.0 kN·m. Sagging resistance is
361.204 kN·m with a 600 mm effective flange. Hogging resistance is
156.420 kN·m with web-only compression. Both shear checks use the
300 mm web.

The two outer support faces provide 960 mm of straight development for
the Ø20 bars. Full-tension development requires 906.250 mm in M30 with
Fe500 bars. The checker also applies the positive-bar simple-support
criterion using web-only resistance and the concurrent support shear.
Internal support development follows the continuous bar into the
adjoining span. [IS 456 clauses 23.1.2 and 26.2](https://wriddodoti.gov.np/uploads/blog/20230331071217_IS-456-with-all-ammendments.pdf)

The cross-section shows two Ø20 top bars and two layers of three Ø20
bottom bars. The schedule assigns a separate mark to each layer. All
eight straight cuts are 8,920 mm. The 41 Ø8 links at 200 mm have a
1,698.171 mm cut length each. The schedule totals 203.457 kg. The
report, elevation, section and BBS share the input and path identities.
[Independent replay](../../verification/check_library_029_beam05_flanged_reference.py)

Use `--case t_beam`, `l_reflected` or `rect_multilayer` for the other
passing layouts. `short_anchor` and `congested` give FAIL.
`missing_combination_face`, `missing_link`, `torsion`, `stale`
and `cutoff` give HOLD. Each failing or held result still writes
`result.json` and `report.html`. The example writes `member.svg` and
`bbs.csv` only when the checked schedule is eligible.

This profile assumes uninterrupted bars, uniform ordinary web links and
a prismatic section up to 750 mm deep. Supply zero torsion only where
the source analysis establishes that the scope is appropriate. Flange
slab steel, joint reinforcement, flanged laps, varying
sections, serviceability and fabrication approval need their own checks.

## Check one bottom bar cutoff

Use the same loader and checker with a `cutoff` record. Name the bar, a
conservative station where the remaining bottom bars can carry the supplied
demands, and the physical termination station. Supply both stations for
every declared ULS combination. This slice admits one straight bottom bar
ending within the first clear span, with at least two bottom bars continuing
through both spans.

```bash
./scripts/python_runtime.sh Python/examples/beam_continuous_detailing.py \
  --reference docs/verification/library-029-beam05-cutoff.json \
  --case cutoff --output-dir output/beam05-cutoff
```

The worked bar `bottom-3` terminates at 3500 mm. The remaining two Ø20
bottom bars provide 628.319 mm². The 900 mm extension exceeds both the
500 mm geometric requirement and 805.915 mm full-stress straight
development. The 70 kN maximum supplied termination shear is below the
85.111 kN limit from two-thirds of the reduced shear resistance. The
actual shortened cut is 3718 mm, so it receives a distinct BBS mark.
The report, SVG and CSV use the same checked path. [Independent replay](../../verification/check_library_029_beam05_cutoff_reference.py)

The reduced cage is checked at supplied ULS stations from the declared
theoretical cutoff onward, including affected support anchors. The example
includes a 100 mm development deficit, a termination shear failure and
missing ULS rows. Each withholds the drawing and schedule. Full action
coverage between supplied stations, points of inflection, other cutoff
and other cutoff directions need separate evidence.

## Check a cutoff in a layered rectangular, T or L beam

```bash
./scripts/python_runtime.sh Python/examples/beam_continuous_detailing.py \
  --reference docs/verification/library-030-beam05-layered-cutoff.json \
  --case rect_multilayer --output-dir output/beam05-layered-cutoff
```

Use the same cutoff fields with the layered member schema. Curtail one
straight outer-layer bottom bar in the first clear span. Keep at least two
outer-layer bottom bars and the remaining layers continuous. Declare zero
torsion and supply the concurrent rows at both cutoff stations in every ULS
combination.

In the rectangular case, `B1-3` ends at 3500 mm, giving 1000 mm of straight
extension against 906.250 mm of required development. The continuing
bottom bars provide 1570.796 mm² across both layers. The maximum supplied
termination shear is 64 kN and the reduced section permits 113.881 kN
under the two-thirds check. The shortened bar has a 3960 mm BBS cut. The
seven other longitudinal bars have 8920 mm cuts, and the 41 uniform Ø8
links retain their 1698.171 mm cut length.

The report carries the action and reinforcement revisions and signed
checks for the continuing cage. The drawing shows the elevation and
sections before and immediately after the end of the bar. The SVG and
BBS carry the same input and path identities. The `short_development`
control fails with a 100 mm deficit. `missing_action` and `stale_action`
hold. All three withhold the drawing and BBS.

The independent references also cover `t_multilayer`, `l_multilayer`
and `l_multilayer_reflected`. The T and reflected L cases use the
published flange geometries with multilayer web cages. For these cases,
the flange contributes to sagging resistance and shear uses the web.
[Independent cutoff replay](../../verification/check_library_030_beam05_cutoff_reference.py)

## Edit a checked bar and recheck the schedule

Use `beam.recheck_continuous_bar_edit(current, previous, edit, analysis_basis=...)`
with a `beam.BeamBarEditV1`. For an analysis whose supplied actions are fixed
independently of the reinforcement, replay the cutoff example with:

```bash
./scripts/python_runtime.sh Python/examples/beam_continuous_detailing.py \
  --reference docs/verification/library-029-beam05-cutoff.json --case cutoff \
  --edit-bar bottom-3 --edit-diameter-mm 16 --output-dir output/beam03-edit
```

The new revision carries a Ø16 bar cut to 3718 mm. The total theoretical
mass changes to 127.371 kg. The congestion control places that bar at
175 mm from the left face, leaving a 7 mm clear gap against a 25 mm
minimum. It fails and withholds drawing and BBS. A changed stiffness basis
or a previous result from different current inputs returns HOLD. [Independent replay](../../verification/check_library_029_flow03_beam_reference.py)

In an editable session, pass the active request as `current=` to the
HTML, SVG and CSV renderers. They compare the input identity before
issuing the checked artifacts. To export the edited result, pass
`current=edited_result.request` after adopting the edited request as
the active input.

## Check one separated bottom bar lap

Set `lap` with the original and partner IDs, the partner's transverse
centre and the start, interior and end stations of the overlap. Retain
the placement reference and every declared ULS combination at those
stations. The same checker verifies the downstream partner layout, both
pieces inside the checked closed links, spacing to all nearby bars and
the signed splice-zone moment limit. It credits one bar at a time in
strength checks. The BBS carries both physical pieces and the splice
result identity.

```bash
./scripts/python_runtime.sh Python/examples/beam_continuous_detailing.py \
  --reference docs/verification/library-029-beam05-lap.json \
  --case lap --output-dir output/beam05-lap
```

The 900 mm overlap between 2600 and 3500 mm exceeds the 805.915 mm
flexural-tension requirement. The two Ø20 pieces are 3718 and 5618 mm
long, and the minimum clear spacing to the partner is 28 mm. A short
overlap and a congested partner fail. Omitting the interior U2 row holds
the result. [Independent replay](../../verification/check_library_029_beam05_lap_reference.py)

This profile covers a single straight separated lap at the bottom of a
rectangular beam with ordinary links. Contact or bundled laps, other
directions, multiple groups, and simultaneous laps and cutoffs need
separate acceptance cases. [IS 456 clauses 26.2.5 and 26.3](https://wriddodoti.gov.np/uploads/blog/20230331071217_IS-456-with-all-ammendments.pdf)


## Check a separated lap in the multilayer rectangle

```bash
./scripts/python_runtime.sh Python/examples/beam_continuous_detailing.py \
  --reference docs/verification/library-030-beam05-rectangular-lap-placement-reference.json \
  --case rectangular_lap --output-dir output/beam05-layered-lap
```

Use the same lap fields with the layered rectangular schema. Keep the lap
within the first clear span, with sagging moment in each supplied overlap
row. Both pieces are Ø20 in the outer bottom layer, with at least two bar
diameters of clear concrete cover. The inner bottom bars stay in line
over uninterrupted outer bars, as required by IS 456 clause 26.3.2(c).

The specimen keeps the original 300 × 600 mm rectangular section, spans
and actions. Four continuous corner bars are seated inside the exterior
closed links. One fully nested link restrains the two additional top bars
and the separated pieces of the intermediate bottom bar `B1-2`. Both
inner bottom bars align with the continuous exterior bars. The two Ø8
link grids use 200 mm nominal pitch and a 60 mm offset.

The nominal 1,300 mm lap runs from 1,550 to 2,850 mm. The declared limits
leave at least 1,280 mm of overlap and 950 mm of straight support
development against 906.25 mm required. The lowest adverse capacities
are 300.106 kN·m in sagging, 260.327 kN·m in hogging and 186.351 kN in
shear. The report records the signed rows and placement checks.
The drawing shows the three lap sections and both link grids in elevation.
The 92-piece BBS totals 249.352 kg.

Short overlap, congestion and bend interference fail. Missing actions,
stale analysis, lost bend restraint and missing placement evidence hold.
Each control withholds the checked drawing and BBS. The original
`layered_lap` remains a separate numerical control for unverified
compression restraint.
[Independent replay](../../verification/check_library_030_beam05_rectangular_lap_placement_reference.py)
[IS 456 clauses 26.2.5 and 26.3.2](https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf)

## Check a separated Ø20 lap in the right-flanged L and symmetric T beams

```bash
./scripts/python_runtime.sh Python/examples/beam_continuous_detailing.py \
  --reference docs/verification/library-030-beam05-flanged-lap-restraint-reference.json \
  --case l_lap --output-dir output/beam05-l-lap
```

Both cases use a 300 × 600 mm web and have zero torsion in the supplied U1
and U2 actions. The effective sagging flange width is 600 mm for the L
beam and 1,000 mm for the T beam. Hogging, shear and positive support
anchorage use the web. The lap provides 1,300 mm where 906.25 mm is
required. The L-beam lap check is governed by `U2:LAP-START` at 35.960 kN·m
against 163.513 kN·m.

Use four continuous Ø20 bars at the exterior link bends. A narrower
closed link seats the intermediate lap bars and two continuous top bars.
Both Ø8 grids use 200 mm pitch. The narrower grid is offset 50 mm and has
32 mm clear to the nearest exterior link. The two tie marks and each
physical lap piece appear in the drawing and BBS. The schedule has 92
pieces totaling 251.261 kg.

Replay `t_control` for the symmetric T case. Short overlap and congestion
fail. Missing actions and stale analysis hold. The original T and L
fixtures retain their numerical checks and hold for unverified
compression restraint. Each control supplies a diagnostic report and
withholds the checked drawing and BBS.
[Independent replay](../../verification/check_library_030_beam05_flanged_lap_restraint_reference.py)

The example checks nominal bar and link geometry, clearances, hooks and
placement grids. A project detail also needs its placement tolerances,
cover blocks, layer spacers, cage installation sequence and concrete
access checked. Apply ductile hook and confinement details under the
separate seismic basis when applicable.
[CPWD Specifications 2009, §5.3.3](https://cpwd.gov.in/Publication/speci_vol1.pdf)

### Check the declared placement envelope

```bash
./scripts/python_runtime.sh Python/examples/beam_continuous_detailing.py \
  --reference docs/verification/library-030-beam05-lap-placement-reference.json \
  --case l_lap --output-dir output/beam05-l-lap-placement
```

The revised L and T cages use four continuous corner bars and one
fully nested closed link. Both Ø8 link grids are nominally at 200 mm
pitch and the nested links are offset by 60 mm. The request carries
the project placement limits as `placement_envelope`. The L review
checks all eight combinations of adverse bar row depths and uses only
the exterior links for strength. Its lowest signed flexural capacities
are 311.491 kN·m in sagging and 260.327 kN·m in hogging. Minimum link
cover is 34.5 mm and the minimum lap is 1,280 mm.

The report records the clearances, placement basis and adverse
capacities. The drawing and BBS retain the nominal geometry, including
the two link schedules of 41 pieces each. The full BBS totals 92 pieces
and 249.352 kg. Check flange and support obstructions with the actual
project details. A declared cage tolerance supports this review route.
An explicit null holds the requested placement check for missing
evidence. The bend interference case fails and the lost restraint case
holds. All three controls withhold the checked drawing and BBS.
[Independent placement replay](../../verification/check_library_030_beam05_lap_placement_reference.py)

### Check an ordinary top lap near the interior support

```bash
./scripts/python_runtime.sh Python/examples/beam_continuous_detailing.py \
  --reference docs/verification/library-030-beam05-support-top-lap-reference.json \
  --case support_top_lap --output-dir output/beam05-support-top-lap
```

The Ø16 top pieces overlap from 3,020 to 3,780 mm on the first-span
side of support B. After bar-end tolerances the minimum lap is
740 mm against 725 mm required. The left and right support faces have
4,600 and 1,120 mm of straight development on the partner in their
respective support directions. Supply signed rows at both expanded
lap endpoints and at the inflections in each span. Two continuous top
corner bars provide the required extension past both inflections.

The exterior and fully nested links remain in place through the sagging
regions, where the top pieces can be credited in compression. The
review report records the placement check and governing rows. The
drawing uses the checked top bar paths and the BBS totals 92 pieces
and 239.426 kg. This case uses ordinary detailing. Ductile beam
lap locations and actual support obstructions need separate checks.
[Independent top lap replay](../../verification/check_library_030_beam05_support_top_lap_reference.py)

## Check varied link pitches in a rectangular cage

```bash
./scripts/python_runtime.sh Python/examples/beam_continuous_detailing.py \
  --reference docs/verification/library-030-beam05-varied-links.json \
  --case dense_required --output-dir output/beam05-varied-links
```

Supply `link_zones` with ordered bounds, spacing, and explicit start
and end inclusion for each zone. The ordinary rectangular example uses
four uninterrupted Ø20 corner bars and one fabricated Ø8 closed link
shape. It places the link at 2,000 mm in the left zone and the link at
6,000 mm in the middle zone. The signed actions at each transition are
checked at both adjacent pitches.

In the concentrated-load case, U2 reaches 219.368 kN shear at the
interior support face. The 100 mm links provide 266.150 kN resistance
there. The uniform 250 mm control provides 145.936 kN and fails under
the same load. The drawing shows the pitch changes and one resolved
section. The BBS has one link mark with 57 pieces at 1,598.230 mm each.
The individual zone counts are 9, 40 and 8. Including four continuous
bars, the total theoretical mass is 123.939 kg.

The checked schedule requires the complete placement grid and signed
rows at every declared member station for each ULS combination.
Overpitch, conflicting ownership and excessive shear
fail. Missing zone evidence, missing transition actions and stale
actions hold. The supplied cage and support fit use nominal dimensions.
[Independent varied-link replay](../../verification/check_library_030_beam05_varied_links_reference.py)

## Check a beam with a variable-depth haunch

```bash
./scripts/python_runtime.sh Python/examples/beam_continuous_detailing.py \
  --reference docs/verification/library-030-beam05-haunch.json \
  --case haunch --output-dir output/beam05-variable-depth
```

Supply the flat-top concrete outline, the nominal bottom-bar bend
vertices and centreline bend radii, the individual link heights and
marks, and the links assigned to each bend in `haunch`. The 250 mm
wide example deepens from 500 to 600 mm around the interior support.
Top corner bars remain straight. The two bottom bars follow 1:6
ramps with four rounded bends. The checked section uses the resolved
bar ordinate and a signed shear correction at each slope.

At 3,300 mm the U2 shear is −60.026 kN. The slope correction reduces
the absolute design shear by 8.012 kN. Two dedicated links per bend
provide 36.297 kN per side against a 22.543 kN demand for each bottom
bar. The 200 mm regular link grid carries the shear check. The
additional links are reserved for the bend forces.

The drawing shows actual bar bends, link stations and the cage
sections. The schedule includes 49 links, two straight bars with
8,920 mm cuts and two bent bars with 8,936.101 mm cuts. It totals
53 pieces and 115.119 kg. The bounded nominal cage retains 32 mm
link cover and a 32 mm axial opening. Check the project tolerances
and actual support obstructions before using the detail on site.

Clashing link geometry, insufficient dedicated bend restraint and
excessive corrected shear fail. Omitted transition actions, missing
bend evidence and stale actions hold. Each control withholds the
checked drawing and BBS.
[Independent haunch replay](../../verification/check_library_030_beam05_haunch_reference.py)

## Check an ordinary T beam with physical flange reinforcement

```bash
./scripts/python_runtime.sh Python/examples/beam_continuous_detailing.py \
  --reference docs/verification/library-030-beam05-physical-flange.json \
  --case physical_flange --output-dir output/beam05-physical-flange
```

The two 4 m beam spans receive concurrent signed actions from uniform
loads. A perpendicular two-span strip supplies its slab reaction to
each declared beam combination. Two Ø16 bars extend outside the web
within a 400 mm hogging distribution width. Their shallow closed links
have overlapping hooks in separate planes. The web keeps its four seated corner bars and
separate shear links. Stagger the web links, flange links and slab main
bars on the grids shown in the support plan.

U2:B1 governs with −128.00 kN·m and −160.00 kN. The adverse hogging
and web shear capacities are 166.83 kN·m and 185.05 kN. The two
outboard bars are checked for straight support development and
extension past both zero-moment stations. The slab strip has its own
signed moment, shear, spacing and development checks.

The drawing reports the 47.0 × 41.3 mm clear local opening after the
declared placement allowance. The schedule carries 118 beam pieces and
142 slab pieces under nine marks and totals 458.957 kg. The report,
sections, elevation and schedule share the checked geometry. Confirm
actual joint steel and field obstructions for a construction detail.

The clash, open flange link and short flange development cases fail. Missing slab
actions and stale strip geometry hold. Each withholds the checked
drawing and schedule.
[Independent T-flange replay](../../verification/check_library_030_beam05_physical_flange_reference.py)

## Check a cutoff in the second span of a layered rectangle

```bash
./scripts/python_runtime.sh Python/examples/beam_continuous_detailing.py \
  --reference docs/verification/library-030-beam05-span2-cutoff-reference.json \
  --case span2_cutoff --output-dir output/beam05-span2-cutoff
```

Choose two continuous stations within the second clear span, with the
physical termination closer to the interior support than the theoretical
station. The reference checks development from 5,500 mm toward decreasing
x. The Ø20 cutoff bar runs from 4,500 to 8,460 mm and its 1,000 mm extension
meets the 906.25 mm requirement. The reduced cage is checked from the
theoretical station toward the left. At the termination, `U2:CUT-END`
gives +64 kN shear against the 113.881 kN reduced-section limit.

The elevation marks 4,500 mm. The two sections show the bar at the
theoretical station and the continuing cage just left of the termination.
The BBS uses the checked 3,960 mm cut. The short-development FAIL and
the missing-action and stale-analysis HOLD controls withhold the drawing
and BBS. [Independent replay](../../verification/check_library_030_beam05_span2_cutoff_reference.py)

## Check a separated lap in the second span of a layered rectangle

```bash
./scripts/python_runtime.sh Python/examples/beam_continuous_detailing.py \
  --reference docs/verification/library-030-beam05-span2-lap-reference.json \
  --case span2_lap --output-dir output/beam05-span2-lap
```

Supply the three overlap stations by increasing x within the second clear
span. Lap-I extends from the lower overlap coordinate to the right end.
Lap-J reaches from the left end to the upper overlap coordinate. The
reference checks the partner layout toward the left support and checks
each layout separately within the overlap.

The 5,150–6,450 mm overlap exceeds the 906.25 mm development requirement.
`U2:LAP-END` governs the lap at 35.960 kN·m against the 148.426 kN·m
limit. The elevation marks both piece ends, and the sections show the
partner alone to the left, both pieces in the overlap and the original
piece alone to the right. The BBS includes the distinct 3,310 and
6,910 mm cuts.

Short overlap and congestion fail. Missing actions and stale analysis
hold. These four controls keep diagnostics and withhold the checked
drawing and BBS. [Independent replay](../../verification/check_library_030_beam05_span2_lap_reference.py)

### Check the compression-bar restraint

Use the revised specimen to obtain checked artifacts for this lap.

```bash
./scripts/python_runtime.sh Python/examples/beam_continuous_detailing.py \
  --reference docs/verification/library-030-beam05-span2-lap-restraint-reference.json \
  --case restrained_span2_lap --output-dir output/beam05-span2-lap-restrained
```

The 230 × 600 mm web keeps four continuous Ø20 bars seated at the
ordinary closed link bends. Each compression layout has a single
intermediate Ø16 bar within 75 mm of the neighbouring corner bars.
Both lap pieces are present together in the sagging interval. The
overlap clearances are checked on the physical section, and the
restraint check uses the signed compression layouts and verified
link geometry. The BBS has 49 pieces and weighs 172.035 kg.

The original right-span cage remains a numerical control. Its report
shows the lap calculation and holds the checked drawing and BBS because
the credited compression bars lack verified restraint. The same check
applies to the original layered rectangular, T-beam and L-beam lap
replays. [IS 456 clauses 26.5.1.2 and 26.5.3.2](https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf) ·
[Independent restraint replay](../../verification/check_library_030_beam05_span2_lap_restraint_reference.py)

## Edit a two-layer cage with declared placement limits

The B05 companion keeps the admitted bottom-bar inventory and seats four
continuous outer bars in the rounded hoop. One open cross-tie restrains
the vertically aligned outer middle bars. The checked example changes
one inner bottom bar from Ø16 to Ø20. The check uses the new bar area
and positions through the signed actions, placement limits and
instantaneous service response.

Supply the `layered_cage` group when loading the continuous detailing
request. It carries the placement dimensions and tolerances, the physical
cross-tie and the current unfactored service load. Call
`recheck_continuous_bar_edit` using the checked base and the applicable
analysis basis. Render using the returned edited request.

```bash
./scripts/python_runtime.sh Python/examples/beam_layered_cage_edit.py \
  --reference docs/verification/library-030-flow03-two-layer-edit.json \
  --case edited --output-dir output/flow03-layered-edit
```

The checked edit retains a 63 mm consolidation opening against the
declared 40 mm requirement. Its 90-piece schedule contains eight
longitudinal bars, 41 closed hoops and 41 open cross-ties. The member
drawing projects the cross-tie shape onto the section and marks the
separate tie stations on the elevation.

Use `empty_corner`, `congested`, `short_form_opening` or
`missing_cross_tie` to replay the placement failures. The
`stale_analysis`, `stiffness_dependent` and `missing_placement`
cases return HOLD. All seven cases emit a diagnostic report and
withhold the checked drawing and BBS.
[Frozen FLOW03 reference](../../verification/library-030-flow03-two-layer-edit.json)
