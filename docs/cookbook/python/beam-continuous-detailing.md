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
rectangular section. Physical laps, other link shapes and construction
approval require their own checks. The
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
directions and physical laps need separate evidence.
