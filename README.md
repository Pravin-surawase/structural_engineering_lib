# IS 456 RC Beam Design Library

[![Python tests](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/python-tests.yml)

A reusable, UI-agnostic structural engineering library for RC rectangular beam design (flexure + shear) per **IS 456:2000** (Indian Standard for Plain and Reinforced Concrete).

## Status

🚀 **Active (v0.9.1)** — Strength design + detailing + DXF export + serviceability + compliance + batch runner. See the CI badge above for latest status.

**Production note:** v0.8.0 introduced Level A serviceability (deflection, crack width) and the compliance checker. See [docs/PRODUCTION_ROADMAP.md](docs/PRODUCTION_ROADMAP.md).

## What makes it different

- **End-to-end pipeline** — design → compliance → detailing → drawings (DXF)
- **Governing-case traceability** — utilization ratios + summary per case
- **Same API in Excel + Python** — VBA + Python with matching inputs/outputs

## Outputs you get

- Reinforcement schedules + bar callouts
- DXF drawings with bar layouts
- Compliance summary and governing case
- Batch CSV outputs for reports or downstream tools

## Who it helps

- Consultants running 100+ beams from ETABS exports
- Detailers generating DXF + schedules quickly
- Students verifying hand calculations and code limits

## Adoption (Early Users)

This repository is public, so anyone can read the code, docs, and examples.

- **Engineering note:** This library is a calculation aid. Final responsibility for code-compliant design, detailing, and drawing checks remains with the qualified engineer.
- **Stability note:** While in active development, prefer pinning to a release tag (example: `@v0.9.1`) rather than installing from `main`.

### Install (Users) — without cloning the repo

Recommended for early adopters.

```bash
python3 -m pip install --upgrade pip

# Base install
python3 -m pip install "structural-lib-is456 @ git+https://github.com/Pravin-surawase/structural_engineering_lib.git@v0.9.1#subdirectory=Python"

# With DXF export support
python3 -m pip install "structural-lib-is456[dxf] @ git+https://github.com/Pravin-surawase/structural_engineering_lib.git@v0.9.1#subdirectory=Python"
```

### Install (Google Colab)

```python
%pip install -q "structural-lib-is456[dxf] @ git+https://github.com/Pravin-surawase/structural_engineering_lib.git@v0.9.1#subdirectory=Python"
```

Then: `Runtime > Restart runtime` and rerun your notebook cells.

## 60-second demo (CSV → schedule + DXF)

If you have the repo locally, use the sample CSV input; otherwise create a CSV with these columns:

- `Python/examples/sample_beam_design.csv`
- Columns: `BeamID, Story, b, D, Span, Cover, fck, fy, Mu, Vu, Ast_req, Asc_req, Stirrup_Dia, Stirrup_Spacing` (case-insensitive)

Run the batch integration:

```bash
python3 -m structural_lib.excel_integration Python/examples/sample_beam_design.csv \
  -o ./out_demo --schedule schedule.csv
```

Outputs:
- `./out_demo/*.dxf` (if `ezdxf` is installed)
- `schedule.csv` (detailing schedule)

ETABS exports can be normalized into this schema. See `docs/PROJECT_OVERVIEW.md` for the ETABS CSV import flow.

## 30-second quickstart (no repo clone)

Install (with DXF support):

```bash
python3 -m venv .venv && source .venv/bin/activate

python3 -m pip install --upgrade pip
python3 -m pip install "structural-lib-is456[dxf] @ git+https://github.com/Pravin-surawase/structural_engineering_lib.git@v0.9.1#subdirectory=Python"
```

Run a batch compliance job (JSON in → JSON/CSV out):

```bash
python3 -c "import json,pathlib; job={'schema_version':1,'code':'IS456','units':'IS456','job_id':'demo-001','beam':{'b_mm':230,'D_mm':500,'d_mm':450,'fck_nmm2':25,'fy_nmm2':500},'cases':[{'case_id':'ULS-1','mu_knm':120,'vu_kn':90}]}; pathlib.Path('job.json').write_text(json.dumps(job,indent=2,sort_keys=True)+"\n",encoding='utf-8')"
python3 -m structural_lib.job_cli run --job job.json --out ./out_demo
```

Generate a quick DXF (detailing JSON in → DXF out):

```bash
python3 -c "import json,pathlib; data={'beam_id':'B1','story':'S1','b':230,'D':450,'span':4000,'cover':25,'fck':25,'fy':500,'ast_start':800,'ast_mid':1200,'ast_end':800}; pathlib.Path('dxf_input.json').write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding='utf-8')"
python3 -m structural_lib.dxf_export dxf_input.json -o beam_detail.dxf
```

## Features

- ✅ **Pure functions** — No UI dependencies (no MsgBox, no worksheet access)
- ✅ **Limit state design** — As per IS 456:2000
- ✅ **Flexural design** — Singly, Doubly, and Flanged (T/L) beams
- ✅ **Shear design** — Stirrup design with Table 19/20 lookup
- ✅ **Ductile Detailing** — IS 13920:2016 checks (Geometry, Min/Max steel, Confinement)
- ✅ **Reinforcement detailing** — Bar patterns / drafting-ready schedules
- ✅ **DXF export** — Drawing output for reinforcement detailing
- ✅ **Batch runner** — Deterministic file-in/file-out runner (`job.json` → JSON/CSV outputs)
- ✅ **Serviceability** — Level A checks (deflection, crack width)
- ✅ **Compliance checker** — Multi-check summary (strength + serviceability) across load cases
- ✅ **ETABS Integration** — Import CSV from ETABS with header normalization and sign preservation
- ✅ **Dual implementation** — VBA (Excel) + Python with identical API
- ✅ **Mac Compatible** — Hardened against Mac VBA stack corruption issues

## 📚 Getting Started

**New to this library?** Start here:

- **[Beginner's Guide](docs/BEGINNERS_GUIDE.md)** — Complete tutorial covering Python AND Excel paths
- **[Python Quickstart](docs/GETTING_STARTED_PYTHON.md)** — Install, run, and verify in 5 minutes
- **[Excel Quickstart](docs/EXCEL_QUICKSTART.md)** — Load the `.xlam` and try a function in 5 minutes
- **[Excel Tutorial](docs/EXCEL_TUTORIAL.md)** — Step-by-step Excel/VBA guide with formulas
- **Sample files** in `Python/examples/` — Ready-to-run scripts and CSV data

## Community

- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
- Support: [SUPPORT.md](SUPPORT.md)
- Security: [SECURITY.md](SECURITY.md)

## Contributing (Dev Setup)

| Task | Command | Where |
| --- | --- | --- |
| Install dev deps | `cd Python && python3 -m pip install -e ".[dev]"` | repo root |
| Install hooks | `pre-commit install` | repo root |
| Run tests | `cd Python && python3 -m pytest` | repo root |
| Format check | `cd Python && python3 -m black --check .` | repo root |
| Type check | `cd Python && python3 -m mypy` | repo root |
| Pre-release gate (all checks + wheel import) | `Python/scripts/pre_release_check.sh` | repo root |

```bash
# Install dev dependencies
cd Python
python3 -m pip install -e ".[dev]"

# Install git hooks (recommended)
cd ..
pre-commit install

# Run checks locally
cd Python
python3 -m pytest
python3 -m black --check .
python3 -m mypy
```

## Install (Developers)

This repo is a monorepo; the Python package lives under `Python/`.

```bash
cd Python
python3 -m pip install -e .
```

Optional dependencies:

- DXF export (ezdxf):

```bash
cd Python
python3 -m pip install -e ".[dxf]"
```

## Scope

| Version | Features | Status |
|---------|----------|--------|
| **v0.1** | Rectangular beams, singly reinforced flexure, shear design | ✅ Completed |
| **v0.2** | Doubly reinforced flexure | ✅ Completed |
| **v0.3** | Flanged beams (T, L) | ✅ Completed |
| **v0.4** | IS 13920 ductile detailing, packaging | ✅ Completed |
| **v0.5** | Excel workbook integration | ✅ Completed |
| **v0.6** | ETABS Integration, Beam Schedule Generation | ✅ Completed |
| **v0.7** | Reinforcement Detailing, DXF Export | ✅ Completed |
| **v0.8** | Serviceability (deflection + crack width), Compliance checker | ✅ Completed |
| **v0.9** | Batch runner (job.json → JSON/CSV), docs + QA hardening | ✅ Completed |

## Directory Structure (current)

```
structural_engineering_lib/
├── VBA/
│   ├── Modules/            ← Core .bas modules (import into Excel)
│   └── Tests/
├── Python/
│   ├── structural_lib/     ← Python package (rectangular + flanged flexure, shear)
│   └── tests/
├── Excel/                  ← Excel workbooks (see Excel/README.md)
├── docs/
│   ├── PROJECT_OVERVIEW.md ← High-level scope/architecture
│   ├── README.md            ← Docs index (start here)
│   ├── _archive/RESEARCH_AND_FINDINGS.md
│   ├── DEVELOPMENT_GUIDE.md
│   ├── API_REFERENCE.md
│   └── IS456_QUICK_REFERENCE.md
├── agents/                 ← Role docs for AI prompts
├── CHANGELOG.md
└── README.md
```

## Using the VBA Library in Excel

### Method 1: Import .bas Files (Recommended)

1. Open your Excel workbook.
2. Press `Alt + F11` to open the VBA Editor.
3. Right-click on "VBAProject (YourWorkbook)" > Import File.
4. Select all `.bas` files from `VBA/Modules/`.
5. You can now use functions like `=IS456_MuLim(...)` directly in cells or call `Design_Singly_Reinforced` from your macros.

## Using the Python Library

```python
from structural_lib import flexure

result = flexure.design_singly_reinforced(
    b=230,
    d=450,
    d_total=500,
    mu_knm=100,
    fck=20,
    fy=415,
)

if result.is_safe:
    print(f"Ast Required: {result.ast_required:.1f} mm²")
else:
    print(f"Design not safe: {result.error_message}")
```

### Method 2: Excel Add-in (Recommended for Distribution)

1. Install the add-in: `Excel/StructEngLib.xlam` (or a GitHub Release asset, if published)
2. Functions available automatically in all workbooks

### Example Usage (VBA)

```vba
Sub DesignBeam()
    Dim result As FlexureResult
    
    ' Design a beam: Mu = 150 kN·m, 300x500 section, M25/Fe415
    result = IS456_FlexureDesign(150, 300, 450, 500, 25, 415)
    
    If result.DesignStatus = "OK" Then
        Debug.Print "Ast required: " & result.Ast_required & " mm²"
    End If
End Sub
```

More worked examples in `VBA/Examples/Example_Usage.bas`.

## Documentation

- **[Docs Index](docs/README.md)** — Start here (who should read what)
- **[Project Overview](docs/PROJECT_OVERVIEW.md)** — High-level scope, architecture, and workflows
- **[Research and Findings (archived)](docs/_archive/RESEARCH_AND_FINDINGS.md)** — Historical research document with formulas, tables, and early API design notes
- **[API Reference](docs/API_REFERENCE.md)** — Public function signatures, inputs/outputs, units
- **[Development Guide](docs/DEVELOPMENT_GUIDE.md)** — Coding standards, naming conventions, testing guidelines
- **[IS 456 Quick Reference](docs/IS456_QUICK_REFERENCE.md)** — Formulas cheat sheet for quick lookup
- **[Known Pitfalls](docs/KNOWN_PITFALLS.md)** — Common traps (units, tables, limits)

## Testing

- Python: `python3 -m pytest Python/tests -q`
- VBA: manual/Rubberduck tests planned for later iteration

## Packaging

- Python: `cd Python && python3 -m build` (outputs to `Python/dist/`)

## References

- IS 456:2000 — Plain and Reinforced Concrete — Code of Practice
- SP:16-1980 — Design Aids for Reinforced Concrete to IS 456
- IS 13920:2016 — Ductile Design and Detailing of RC Structures

## License

MIT License — Free to use, modify, and distribute.

## Author

Pravin Surawase (GitHub: https://github.com/Pravin-surawase)
