---
owner: Main Agent
status: active
last_updated: 2026-10-29
doc_type: guide
complexity: intermediate
tags: []
---

# Beginner's Guide

**Type:** Guide
**Audience:** Users
**Status:** Approved
**Importance:** High
**Version:** 0.25.0
**Created:** 2025-12-15
**Last Updated:** 2026-10-29

---

This guide is written for engineers and students who are new to Python. The
Python path is copy/paste friendly; the Excel path does not require Python.

The Python route below is the reproducible starter workflow for the library
and CLI. Excel/VBA is a separate host-integration track with its own artifacts
and installed-host evidence; the Python wheel does not install an Excel add-in.

---

## Path 1: Python (step by step, copy/paste)

### Step 1: Install Python
- Windows: download from https://www.python.org/downloads/ and check "Add Python to PATH"
- macOS: download from https://www.python.org/downloads/
- Check it worked: `python3 --version` (Windows: `py --version`)

### Step 2: Create a clean folder
Open Terminal (macOS) or Command Prompt (Windows), then run:
```bash
mkdir structural_lib_demo
cd structural_lib_demo
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### Step 3: Install the library
Pins track the version prepared on this source branch. The registry commands
require verified publication in the [release record](releases.md); a source
version bump alone does not make a candidate available to install.

```bash
python3 -m pip install --upgrade pip
python3 -m pip install "structural-lib-is456==0.25.0"
python3 -m structural_lib install-preflight
```

Optional (only if you want DXF drawings):
```bash
python3 -m pip install "structural-lib-is456[dxf]==0.25.0"
```

### Step 4: Run a first check (no files yet)
Create a new file named `check.py` and paste this:
```python
from structural_lib.design.is456 import beam

request = beam.load(
    {
        "identity": {"member_id": "B1", "story": "GF", "case_id": "ULS-1"},
        "section": {"span_mm": 5000.0, "b_mm": 300.0, "D_mm": 500.0, "d_mm": 442.0},
        "materials": {"fck_nmm2": 25.0, "fy_nmm2": 500.0},
        "actions": {"mu_knm": 150.0, "vu_kn": 80.0, "tu_knm": 0.0},
        "calculation_basis": {"d_dash_mm": 58.0, "asv_mm2": 100.0},
    }
)
result = beam.design(request)
print("Engineering status:", result.engineering_status)
print("Ast required (mm^2):", round(result.calculation.flexure.Ast_required))
```

Run it:
```bash
python3 check.py
```

Expected output:
```
Engineering status: PASS
Ast required (mm^2): 906
```

### Step 5: Run the CLI with a tiny CSV
Create a file named `beams.csv` with this content:
```csv
BeamID,Story,b,D,tension_bar_diameter_mm,Span,Cover,fck,fy,Mu,Vu,Stirrup_Dia,Stirrup_Spacing
B1,Ground,300,500,16,4000,40,25,500,150,100,8,150
```

The 16 mm tension bars, 40 mm clear cover and 8 mm links give
`d = 500 - 40 - 8 - 16/2 = 444 mm`. This case fits one tension layer. Keep the
depth/layout validation when adapting the example to a different member.

Run design and schedule generation with the base package:
```bash
python3 -m structural_lib design beams.csv -o results.json
python3 -m structural_lib bbs results.json -o schedule.csv
python3 -m structural_lib report results.json --format=html -o report.html
```

After installing the optional DXF extra in Step 3, you can also run:

```bash
python3 -m structural_lib dxf results.json -o drawings.dxf
```

You will get:
- `results.json` (design + compliance results)
- `schedule.csv` (bar bending schedule)
- `report.html` (inspectable design report)
- `drawings.dxf` (only if DXF support is installed)

### Optional: Generate a 500-beam batch (no ETABS needed)
From a source checkout root, this optional larger source-bound batch writes
under an explicit output directory:
```bash
./scripts/python_runtime.sh Python/examples/full_pipeline_synthetic.py --count 500 --output-dir ./output/demo_500
```
Skip DXF if you want a faster run:
```bash
./scripts/python_runtime.sh Python/examples/full_pipeline_synthetic.py --count 500 --skip-dxf --output-dir ./output/demo_500
```

---

## Path 2: Excel/VBA (separate host workflow)

The repository contains Excel/VBA source and a separate
[Excel-DNA/XLL plan](../planning/xll-product/README.md). A Python-package install
is not proof of a built, signed or qualified Excel workbook/add-in. Use the
selected host packet's actual artifact, installation instructions and evidence;
do not assume the historical `StructEngLib.xlam` or `BeamDesignApp.xlsm` names
refer to files supplied by this package. Native Excel/ETABS/XLL qualification
remains a separate gate and is not established by this Python starter replay.

---

## Common fixes
- "Module not found": make sure the virtual environment is active.
- "python3 not found" on Windows: use `py` instead of `python3`.
- DXF not working: install `structural-lib-is456[dxf]==0.25.0`.

---

## Next steps
- Python quickstart: `docs/getting-started/python-quickstart.md`
- Colab workflow: `docs/getting-started/colab-workflow.md`
- Excel tutorial: `docs/getting-started/excel-tutorial.md`
- CLI reference: `docs/cookbook/cli-reference.md`
- API reference: `docs/reference/api.md`
- Learning path: `docs/learning/README.md`

Document Version: 0.25.0 | Last Updated: 2026-10-29
