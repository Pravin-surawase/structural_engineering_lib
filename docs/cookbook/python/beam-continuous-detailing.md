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
and a uniform link placement grid. The link input declares
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
slab steel, joint reinforcement, cutoffs and laps in this cage, varying
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
directions need separate evidence.

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
