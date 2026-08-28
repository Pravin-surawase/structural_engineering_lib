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

## Recommended order

| Example | What it demonstrates | Writes files? |
|---|---|---|
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
