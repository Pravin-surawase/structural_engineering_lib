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

The `0.24.0` normal release includes the accepted B0/F0/R0 programme and the
post-R0 cumulative audit. Use the exact pin for reproducibility. This is a
normal software-release claim for the audited supported scope, not complete IS
456 coverage or professional approval.

Engineer review is a single final-stage activity after B0, F0, and R0 complete
the integrated library. It is not an intermediate approval gate for this B0
contract cycle, and no current software result claims that review has occurred.

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
   python3 -m pip install "structural-lib-is456[dxf]"
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
from structural_lib.codes.is456.beam import detailing, flexure

# Design a singly reinforced beam (230x500, Mu = 150 kN·m, M25/Fe415)
res = flexure.design_singly_reinforced(
    b=230, d=450, d_total=500, mu_knm=150, fck=25, fy=415
)
print("Status:", "OK" if res.is_safe else res.error_message)
print("Ast required (mm²):", round(res.ast_required, 1))

# Detailing helpers
ld = detailing.calculate_development_length(bar_dia=16, fck=25, fy=415)
lap = detailing.calculate_lap_length(bar_dia=16, fck=25, fy=415, is_seismic=False)
print("Ld (mm):", ld, " Lap length (mm):", lap)
```
Run it:
```bash
python3 example.py
```

## 4) No CSV? Generate synthetic inputs (batch + full pipeline)
If you do not have ETABS or CSV inputs, generate a realistic dataset and run the full workflow.
This step uses the repo examples folder.
```bash
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
```bash
# Design beams from CSV
python3 -m structural_lib design path/to/beams.csv -o results.json

# Include Level A deflection check
python3 -m structural_lib design path/to/beams.csv -o results.json --deflection

# Include crack width check (explicit params JSON)
python3 -m structural_lib design path/to/beams.csv -o results.json \
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

## 6) Minimal “one-liner” example (no files)
```bash
python3 - <<'PY'
from structural_lib.codes.is456.beam import shear
res = shear.design_shear(vu_kn=100, b=300, d=500, fck=25, fy=415, asv=100, pt=0.75)
print("Shear OK?", res.is_safe, "Spacing (mm):", res.spacing)
PY
```

## 7) Column Design (IS 456)

```python
import structural_lib as sl

# Short column — axial capacity (IS 456 Cl 39.3)
result = sl.design_column_axial_is456(
    fck=25,        # Concrete grade (N/mm²)
    fy=415,        # Steel grade (N/mm²)
    Ag_mm2=90000,  # Gross area 300×300 mm
    Asc_mm2=2412,  # 6 nos. 20mm dia
)
print(f"Axial capacity: {result['Pu_kN']:.1f} kN")
```

For the full column API (uniaxial, biaxial, slender columns), see [api.md](../reference/api.md).

## 8) Packaging notes (contributors only)
- Build a wheel: `cd Python && python3 -m build`.
- Version source of truth: `Python/pyproject.toml`.

## 9) Troubleshooting
- "Module not found": ensure the venv is activated and you installed `structural-lib-is456`.
- DXF generation missing: install `structural-lib-is456[dxf]`.
- Tests failing on path issues: run commands from the repo root.
## 10) Sample Files & Examples
- `Python/examples/simple_examples.py` - 7 beginner examples with explanations
- `Python/examples/complete_beam_design.py` - Full design workflow
- `Python/examples/full_pipeline_synthetic.py` - Generates 50-500 beams and runs full CLI pipeline
- `Python/examples/sample_beam_design.csv` - Simple 5-beam sample
- `Python/examples/sample_building_beams.csv` - Complete 12-beam building

## 11) Further Reading
- [beginners-guide.md](beginners-guide.md) - Comprehensive tutorial (Python + Excel)
- [colab-workflow.md](colab-workflow.md) - Step-by-step Colab workflow (full pipeline + batch)
- [../reference/api.md](../reference/api.md) - Full API documentation
- [../reference/is456-formulas.md](../reference/is456-formulas.md) - IS 456 code reference
