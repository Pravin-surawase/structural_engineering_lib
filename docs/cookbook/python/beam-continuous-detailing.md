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
with a two-span rectangular member, current supplied actions, continuous
straight bars and a uniform link placement grid. The link input declares
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

This route covers straight bars, one ordinary link mark and a
rectangular section. Other link shapes and construction approval require
their own checks. The
SVG is a review elevation. Serviceability is a separate calculation.

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
