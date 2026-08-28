---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: intermediate
tags: []
---

# Python Quickstart (Beginner-Friendly)

**Type:** Guide
**Audience:** Users
**Status:** Beta Maturity / Normal Software Release
**Importance:** High
**Version:** 0.24.0
**Created:** 2025-12-15
**Last Updated:** 2026-08-28

---

This guide shows how to install, run, and verify the Python library with simple, copy/paste steps. No prior packaging experience required.

> **📚 New to this?** See [beginners-guide.md](beginners-guide.md) for comprehensive step-by-step instructions with explanations.

## Fast install (no repo clone)

This is the easiest path for beginners.

```bash
python3 -m pip install --upgrade pip

# Install the exact normal release
python3 -m pip install "structural-lib-is456===0.24.0"

# Optional DXF support
python3 -m pip install "structural-lib-is456[dxf]===0.24.0"

# Verify the interpreter, package origin/version, and installed extras
python3 -m structural_lib install-preflight
```

`0.24.0` is the current normal release. Use the exact pin for reproducibility.
It covers the audited supported cases; it does not claim complete IS 456
coverage, professional approval, or construction readiness. Every result still
requires independent review by a qualified structural engineer.

## Google Colab quick install

```python
%pip install -q "structural-lib-is456[dxf]===0.24.0"
```

Then: `Runtime > Restart runtime` and rerun.

---

## 1) Create a clean workspace (recommended)
If you are on Windows, replace `python3` with `py`.
1. Check Python is installed: `python3 --version` (Windows: `py --version`)
2. Create a folder and virtual environment:
   ```bash
   mkdir structural_lib_demo
   cd structural_lib_demo
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```
3. Install the library:
   ```bash
   python3 -m pip install --upgrade pip
   python3 -m pip install "structural-lib-is456===0.24.0"
   python3 -m structural_lib install-preflight
   ```
4. Optional DXF support:
   ```bash
   python3 -m pip install "structural-lib-is456[dxf]===0.24.0"
   ```

## 2) Canonical beam design (no files)

Workflow ID: `is456.beam.design/v1`. Supported case: rectangular IS 456 beam
with caller-supplied factored action magnitudes. The result may be engineering
`PASS` or `FAIL`; invalid intake raises `InputContractError` before a result is
created.

```bash
python3 - <<'PY'
from structural_lib.design.is456 import beam

request = beam.input(
    member_id="B1",
    story="GF",
    case_id="ULS-1",
    span_mm=5000,
    b_mm=300,
    D_mm=550,
    d_mm=500,
    fck_nmm2=25,
    fy_nmm2=500,
    mu_knm=150,
    vu_kn=80,
    d_dash_mm=50,
    asv_mm2=100,
)
result = beam.design(request)
print("Engineering status:", result.engineering_status)
print("Ast required (mm²):", round(result.calculation.flexure.Ast_required))
PY
```

For explicit detailing and BBS composition, see the
[canonical beam recipe](../cookbook/python/beam.md).
For all advertised families, use the generated
[13-journey facade cookbook](../cookbook/python/family-facades.md).

## 3) Use the library in a script (optional)

Create a file `example.py` with this content:

```python
from structural_lib.design.is456 import beam

request = beam.input(
    member_id="B1",
    story="GF",
    case_id="ULS-1",
    span_mm=5000,
    b_mm=300,
    D_mm=550,
    d_mm=500,
    fck_nmm2=25,
    fy_nmm2=500,
    mu_knm=150,
    vu_kn=80,
    d_dash_mm=50,
    asv_mm2=100,
    source_provenance="analysis-envelope:ULS-1",
)
result = beam.design(request)

print("Engineering status:", result.engineering_status)
print("Ast required (mm²):", round(result.calculation.flexure.Ast_required))
```

Run it:

```bash
python3 example.py
```

## 4) No CSV? Generate synthetic inputs (batch + full pipeline)
If you do not have ETABS or CSV inputs, clone the source repository and use its
synthetic generator. Repository examples are intentionally not bundled in the
installed wheel.

```bash
git clone https://github.com/Pravin-surawase/structural_engineering_lib.git
cd structural_engineering_lib
python3 -m pip install "structural-lib-is456===0.24.0"
cd Python
python3 examples/full_pipeline_synthetic.py --count 500 --output-dir ./output/demo_500
```
This will create:
- `beams_synthetic_500.csv`
- `results.json`
- `schedule.csv`
- `drawings.dxf` (requires `ezdxf`)

To skip DXF (faster):
```bash
python3 examples/full_pipeline_synthetic.py --count 500 --skip-dxf
```

## 5) Use the CLI (CSV -> JSON -> BBS/DXF)

The unified CLI supports design, schedules, and drawings:

Download the maintained
[`sample_beam_design.csv`](https://raw.githubusercontent.com/Pravin-surawase/structural_engineering_lib/v0.24.0/Python/examples/sample_beam_design.csv)
and save it as `beams.csv`, then run:

```bash
# Design beams from CSV
python3 -m structural_lib design beams.csv -o results.json

# Include Level A deflection check
python3 -m structural_lib design beams.csv -o results.json --deflection

# Include crack width check (explicit params JSON)
python3 -m structural_lib design beams.csv -o results.json \
  --crack-width-params crack_width_params.json

# Generate bar bending schedule
python3 -m structural_lib bbs results.json -o schedule.csv

# Generate DXF drawings (requires ezdxf)
python3 -m structural_lib dxf results.json -o drawings.dxf --title-block --title "Beam Sheet"

# Run complete job from spec file
python3 -m structural_lib job job.json -o ./output
```
- Required CSV input columns: `BeamID, Story, b, D, eff_d, Span, Cover, fck, fy, Mu, Vu, Stirrup_Dia, Stirrup_Spacing`. Replace `eff_d` with `tension_bar_diameter_mm` only when deriving effective depth from the explicit cover and stirrup diameter.
- The command blocks the whole file on malformed, missing, non-finite, unknown, duplicate, ambiguous, or mixed-validity records. It never uses `Ast_req`, `Asc_req`, or `Status` as design inputs.
- Outputs:
  - `results.json` — Design results with compliance status.
  - `schedule.csv` — Bar bending schedule per IS 2502.
  - DXF files (if `ezdxf` available).

## 6) Inspect the supported capability contract

```bash
python3 -m structural_lib capabilities
```

Use this machine-readable output to distinguish supported, bounded, and held
workflows before choosing an API.

## 7) Column Design (IS 456)

```python
from structural_lib.design.is456 import column

request = column.load(
    {
        "identity": {
            "case_id": "COL-1",
            "family_id": "column",
            "member_id": "C1",
            "source_reference": "analysis-envelope:ULS-1",
            "story": "GF",
        },
        "geometry": {
            "D_mm": 450.0,
            "b_mm": 300.0,
            "braced": True,
            "end_condition": "FIXED_FIXED",
            "minimum_eccentricity_length_mm": 3000.0,
            "unsupported_length_mm": 3000.0,
        },
        "actions": {
            "m1x_signed_knm": 120.0,
            "m1y_signed_knm": 0.0,
            "m2x_signed_knm": 120.0,
            "m2y_signed_knm": 0.0,
            "mux_knm": 120.0,
            "muy_knm": 0.0,
            "pu_kn": 800.0,
        },
        "materials": {"fck_nmm2": 25.0, "fy_nmm2": 415.0},
        "reinforcement": {
            "reinforcement_centroid_depth_mm": 50.0,
            "supplied_steel_area_mm2": 2400.0,
        },
    }
)
result = column.design(request)
print("Engineering status:", result.engineering_status)
```

For the supported-case boundary and rejected-input example, see the
[column supplied-steel recipe](../cookbook/python/column-supplied-steel-check.md).

## 8) Packaging notes (contributors only)
- Build a wheel: `cd Python && python3 -m build`.
- Version source of truth: `Python/pyproject.toml`.

## 9) Troubleshooting
- "Module not found": ensure the venv is activated and you installed `structural-lib-is456`.
- DXF generation missing: install `structural-lib-is456[dxf]`.
- Tests failing on path issues: run commands from the repo root.
## 10) Sample Files & Examples

These files live in the source repository, not the wheel. See the
[`Python/examples` guide on
GitHub](https://github.com/Pravin-surawase/structural_engineering_lib/blob/main/Python/examples/README.md)
for prerequisites, outputs, and the recommended order.

- `Python/examples/end_to_end_workflow.py` - installed-package design → detailing → BBS → report
- `Python/examples/simple_examples.py` - seven beam calculation demonstrations
- `Python/examples/full_pipeline_synthetic.py` - generates a strict CSV and runs design → BBS → optional DXF
- `Python/examples/sample_beam_design.csv` - strict five-beam CLI input
- `Python/examples/sample_building_beams.csv` - fixture for `complete_beam_design.py`, not strict CLI input

## 11) Further Reading
- [beginners-guide.md](beginners-guide.md) - Comprehensive tutorial (Python + Excel)
- [colab-workflow.md](colab-workflow.md) - Step-by-step Colab workflow (full pipeline + batch)
- [../reference/api.md](../reference/api.md) - Full API documentation
- [../reference/is456-formulas.md](../reference/is456-formulas.md) - IS 456 code reference
