---
owner: Main Agent
status: active
last_updated: 2026-11-13
doc_type: guide
complexity: advanced
tags: [beam, reinforcement, catalogue, is456]
---

# Select bottom bars from a finite beam section catalogue

Use `beam.load_section_catalogue` and `beam.select_section_catalogue` for a
solid rectangular section with two bottom bar layers at fixed depths.
The request carries the same signed actions and fixed top bars for every
candidate. Each layer option supplies an ID, diameter and explicit
bar centres.

Copy the [example script](../../../Python/examples/beam_section_catalogue.py)
and [frozen case](../../verification/library-029-flow02-beam-catalogue.json)
into a working folder with the matching 0.29 candidate.

```bash
python beam_section_catalogue.py --reference library-029-flow02-beam-catalogue.json \
  --output-dir checked-catalogue
```

The example replays all 81 combinations of 2, 3 or 4 bars and diameters
16, 20 or 25 mm per bottom layer. The first 53 feasible candidates are
ordered by increasing bottom steel area, then bar count and option ID.
The selected layout has 2Ø20 in the outer bottom layer and 2Ø16 in the
inner bottom layer. The [independent replay](../../verification/check_library_029_flow02_reference.py)
checks both signed flexural branches and shear. The original BEAM04
hogging overload has its own fixture. This example uses −95 kN·m
hogging to exercise the fixed top cage across the catalogue.

The result retains every candidate’s status, governing supplied row,
capacity, steel provision and issues. The selected section retains its
actual bars and a new content-derived reinforcement revision. Read
`calculation.selected_id` and `calculation.selected` from a PASS result.
The HTML report uses the same input hash as the JSON.

An exhausted budget or stale analysis produces HOLD. A complete catalogue
with no feasible candidate gives FAIL. Set the analysis basis to
`reinforcement_dependent_stiffness` when changing the bars requires a
fresh analysis. Selection then remains HOLD pending that evidence.
The selection covers one section and the declared action rows.
Member-wide detailing and fabrication outputs require their own checks.
