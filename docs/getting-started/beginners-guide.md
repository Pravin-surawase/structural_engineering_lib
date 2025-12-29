# Beginner's Guide (No Coding Required)

This guide is written for engineers and students who are new to coding. Follow the steps exactly and you will get a working result.

You have two ways to use this library:
- Python (recommended for batch work and the CLI)
- Excel/VBA (recommended if you live in spreadsheets)

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
```bash
python3 -m pip install --upgrade pip
python3 -m pip install structural-lib-is456
```

Optional (only if you want DXF drawings):
```bash
python3 -m pip install "structural-lib-is456[dxf]"
```

### Step 4: Run a first check (no files yet)
Create a new file named `check.py` and paste this:
```python
from structural_lib import flexure

res = flexure.design_singly_reinforced(
    b=300, d=450, d_total=500, mu_knm=150, fck=25, fy=500
)
print("Ast required (mm^2):", round(res.ast_required))
print("Status:", "OK" if res.is_safe else res.error_message)
```

Run it:
```bash
python3 check.py
```

Expected output:
```
Ast required (mm^2): 882
Status: OK
```

### Step 5: Run the CLI with a tiny CSV
Create a file named `beams.csv` with this content:
```csv
BeamID,Story,b,D,Span,Cover,fck,fy,Mu,Vu
B1,Ground,300,500,4000,40,25,500,150,100
```

Now run the full pipeline:
```bash
python3 -m structural_lib design beams.csv -o results.json
python3 -m structural_lib bbs results.json -o schedule.csv
python3 -m structural_lib dxf results.json -o drawings.dxf
```

You will get:
- `results.json` (design + compliance results)
- `schedule.csv` (bar bending schedule)
- `drawings.dxf` (only if DXF support is installed)

### Optional: Generate a 500-beam batch (no ETABS needed)
If you are using the repo and want a big batch test, run:
```bash
cd Python
python3 examples/full_pipeline_synthetic.py --count 500 --output-dir ./output/demo_500
```
Skip DXF if you want a faster run:
```bash
python3 examples/full_pipeline_synthetic.py --count 500 --skip-dxf
```

---

## Path 2: Excel/VBA (no coding)

### Step 1: Get the Excel file
Use one of these:
- `Excel/StructEngLib.xlam` (add-in)
- `Excel/BeamDesignApp.xlsm` (workbook)

If you received a zip or release bundle, extract it first.

### Step 2: Enable macros (required)
In Excel:
- File -> Options -> Trust Center -> Trust Center Settings
- Macro Settings -> Enable all macros
- Check "Trust access to the VBA project object model"

### Step 3: Load the add-in (if using .xlam)
- Excel -> File -> Options -> Add-ins
- Manage: Excel Add-ins -> Go...
- Browse -> select `StructEngLib.xlam` -> OK

### Step 4: Try one formula
In any cell, enter:
```
=IS456_MuLim(300, 450, 25, 500)
```

You should get a number around 196.5 (kN-m).

---

## Common fixes
- "Module not found": make sure the virtual environment is active.
- "python3 not found" on Windows: use `py` instead of `python3`.
- DXF not working: install `structural-lib-is456[dxf]`.
- Excel formulas not showing: re-open Excel after enabling macros.

---

## Next steps
- Python quickstart: `docs/getting-started/python-quickstart.md`
- Colab workflow: `docs/getting-started/colab-workflow.md`
- Excel tutorial: `docs/getting-started/excel-tutorial.md`
- CLI reference: `docs/cookbook/cli-reference.md`
- API reference: `docs/reference/api.md`
- Learning path: `docs/learning/README.md`

Document Version: 0.10.7 | Last Updated: 2025-12-29
