# Python Examples

Runnable examples for `structural-lib-is456` 0.24.0. These files live in the
source repository and are intentionally excluded from the wheel. Install the
published package, then run the examples from a clone:

```bash
git clone https://github.com/Pravin-surawase/structural_engineering_lib.git
cd structural_engineering_lib
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python3 -m pip install "structural-lib-is456==0.24.0"
python3 -m structural_lib install-preflight
```

## Typed workflows from the current source

`complete_member_workflow.py` includes the frozen LIB-MEMBER-WORKFLOW-001 acceptance
case: a 300 × 500 mm ordinary beam with separate ULS/SLS loads, actual bars,
19 required leaf checks, physical BBS, quantities and an HTML calculation report.
Its [source and independent evidence](../../docs/planning/library-usability-improvement.md#lib-member-workflow-001-frozen-acceptance-case)
defines the complete supported profile and manual case-admission conditions.
It requires the current source build; it is not present in the older public wheel.

```bash
python3 -m pip install -e ./Python
python3 Python/examples/complete_member_workflow.py --output-dir /tmp/complete-beam
```

Use `--case multilayer` for LIB-MEMBER-WORKFLOW-002: two layers on each face,
27 required checks, 43 physical bars and per-bar ULS strains/stresses in the
report. The [multilayer acceptance record](../../docs/planning/multilayer-member-workflow.md)
defines the inputs, independent reference and limits. Both cases retain SLS
cracked-section evidence and span/depth screening, without a calculated
long-term deflection claim.

```bash
python3 Python/examples/complete_member_workflow.py --case multilayer --output-dir /tmp/multilayer-beam
```

Open `report.html`; `calculation.json` retains every input/result/source identity
and `bbs.csv` carries the same issue state for each physical bar. The fixed case
passes, each missing required check remains visible/draft, and actual overload
or insufficient anchorage cannot export an accepted package. Preparation and
engineering review are manual; the run copies no intermediate values by hand.
This is one qualified worked case with span/depth screening and supplied,
independently verified SLS section evidence. It is not a general beam-design
profile, calculated long-term deflection, fabrication drawing or human approval.

`canonical_workflows.py` uses public request groups, a beam-to-BBS workflow,
column and slab checks, structured errors and a JSON round-trip. The newly
exposed group imports, slab builders, and JSON loaders require the current source build;
they are not assumed to exist in the older published wheel.

```bash
python3 -m pip install -e ./Python
python3 Python/examples/canonical_workflows.py
```

`physical_member_workflow.py` connects the physical-beam operations: actual bars,
an explicit project/profile, check results, member aggregation, resolved paths,
BBS, quantities, declared costs, and calculation-package data. It demonstrates
missing and stale evidence too. Its teaching profile covers geometry, positive
flexure, and ordinary-frame seismic applicability; it is not a complete
building-design profile. It uses current-source typed output and leaf helpers:

```bash
python3 Python/examples/physical_member_workflow.py
```

`candidate_ranking_workflow.py` reuses that physical fixture to calculate three
actual arrangements, including their 40 links, BBS and quantities. It excludes
a failed smaller-bar arrangement, ranks the passing ones, and shows budget and
stale-evidence outcomes. Keep both example files together:

```bash
python3 Python/examples/candidate_ranking_workflow.py
```

`beam_checks_workflow.py` gives explicit calls for topology, beam-line analysis,
action normalization, physical capacity, deflection, crack width, anchorage,
laps, and reinforcement fit. It also shows missing-evidence and seismic
applicability outcomes. Service components and strain are declared teaching
inputs; the elastic analysis does not establish them:

```bash
python3 Python/examples/beam_checks_workflow.py
```

`analysis_snapshot_replay.py` validates and round-trips an existing portable
snapshot without ETABS. With no argument it reads the clone's synthetic WP10
fixture; supply your snapshot path to validate your own captured evidence:

```bash
python3 Python/examples/analysis_snapshot_replay.py
python3 Python/examples/analysis_snapshot_replay.py /path/to/snapshot.json
```

## Recommended order

| Example | What it demonstrates | Writes files? |
|---|---|---|
| `complete_member_workflow.py` | One independently checked ordinary beam → all required checks → physical BBS and report; current source build | Yes, with `--output-dir` |
| `canonical_workflows.py` | Typed canonical beam, column and slab journeys; current source build | No |
| `beam_checks_workflow.py` | Explicit analysis, capacity, serviceability and detailing calls; evidence remains distinct | No |
| `physical_member_workflow.py` | Physical bars → profile checks → BBS/quantities/cost/package; missing/stale evidence; current source build | No |
| `candidate_ranking_workflow.py` | Genuine candidate calculations → finite-domain ranking; failed, budget and stale outcomes; current source build | No |
| `analysis_snapshot_replay.py` | Offline snapshot validation, canonical replay and rejection diagnostics | No |
| `end_to_end_workflow.py` | Installed-package beam design → detailing → BBS → HTML report | No |
| `simple_examples.py` | Seven focused flexure, shear, detailing, and bar-selection demonstrations | No |
| `bmd_sfd_example.py` | Bending-moment and shear-force diagrams | No |
| `full_pipeline_synthetic.py` | Strict synthetic CSV → CLI design → BBS → optional DXF | Yes, under `--output-dir` |
| `complete_beam_design.py` | Educational CSV-driven beam workflow using `sample_building_beams.csv` | Yes, beside the copied script |
| `canonical_data_workflow.py` | Canonical models, adapters, caching, and serialization | Yes, temporary/example output |
| `colab_workflow.py` | Single-file Colab job, flexure, shear, detailing, and optional DXF | Yes, under `output/` |
| `demo_intelligence.py` | Precheck and sensitivity utilities | No |
| `validate_intelligence.py` | Representative intelligence validation cases | No |
| `professional_workflow.py` | Compatibility API, calculation fingerprints, reports, and invariant checks | Temporary files only |

Start with the installed-package example:

```bash
python3 Python/examples/end_to_end_workflow.py
```

Run the maintained strict CLI pipeline without DXF dependencies:

```bash
cd Python
python3 examples/full_pipeline_synthetic.py \
  --count 50 \
  --skip-dxf \
  --output-dir ./output/demo_50
```

Install `structural-lib-is456[dxf]==0.24.0` and omit `--skip-dxf` to generate
drawings. `sample_beam_design.csv` is strict CLI input;
`sample_building_beams.csv` is an educational fixture for
`complete_beam_design.py` and includes output-like columns that the strict CLI
correctly rejects.

## Other structural families

The maintained [family facade cookbook](../../docs/cookbook/python/family-facades.md)
contains copy-paste inputs for beam, torsion, column, slab, wall, staircase,
deep-beam, flat-slab, isolated-footing, combined-footing, and strap-footing
journeys. Those recipes are the canonical starting point for new integrations.

An example completing successfully demonstrates software behavior only. Review
the reported `PASS`, `FAIL`, or `HOLD` status and limitations; no example is
professional approval or authorization for construction use.
