# IS 456 RC Beam Design Library

[![Python tests](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/python-tests.yml)

A reusable, UI-agnostic structural engineering library for RC rectangular beam design (flexure + shear) per **IS 456:2000** (Indian Standard for Plain and Reinforced Concrete).

## Status

🚀 **Active (v0.8.0)** — Strength design + detailing + DXF export + serviceability + compliance. 158 Python tests passing.

**Production note:** v0.8.0 includes Level A serviceability (deflection, crack width) and the compliance checker. See [docs/PRODUCTION_ROADMAP.md](docs/PRODUCTION_ROADMAP.md).

## Features

- ✅ **Pure functions** — No UI dependencies (no MsgBox, no worksheet access)
- ✅ **Limit state design** — As per IS 456:2000
- ✅ **Flexural design** — Singly, Doubly, and Flanged (T/L) beams
- ✅ **Shear design** — Stirrup design with Table 19/20 lookup
- ✅ **Ductile Detailing** — IS 13920:2016 checks (Geometry, Min/Max steel, Confinement)
- ✅ **Reinforcement detailing** — Bar patterns / drafting-ready schedules
- ✅ **DXF export** — Drawing output for reinforcement detailing
- ✅ **Serviceability** — Level A checks (deflection, crack width)
- ✅ **Compliance checker** — Multi-check summary (strength + serviceability) across load cases
- ✅ **ETABS Integration** — Import CSV from ETABS with header normalization and sign preservation
- ✅ **Dual implementation** — VBA (Excel) + Python with identical API
- ✅ **Mac Compatible** — Hardened against Mac VBA stack corruption issues

## 📚 Getting Started

**New to this library?** Start here:

- **[Beginner's Guide](docs/BEGINNERS_GUIDE.md)** — Complete tutorial covering Python AND Excel paths
- **[Python Quickstart](docs/GETTING_STARTED_PYTHON.md)** — Install, run, and verify in 5 minutes
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
| Run tests | `cd Python && python -m pytest` | repo root |
| Format check | `cd Python && python -m black --check .` | repo root |
| Type check | `cd Python && python -m mypy` | repo root |

```bash
# Install dev dependencies
cd Python
python3 -m pip install -e ".[dev]"

# Install git hooks (recommended)
cd ..
pre-commit install

# Run checks locally
cd Python
python -m pytest
python -m black --check .
python -m mypy
```

## Install (Python)

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

## Directory Structure (current)

```
structural_engineering_lib/
├── VBA/
│   ├── Modules/            ← Core .bas modules (import into Excel)
│   └── Tests/
├── Python/
│   ├── structural_lib/     ← Python package (rectangular + flanged flexure, shear)
│   └── tests/
├── Excel/                  ← Flagship workbook (placeholder)
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

1. Install the `.xlam` add-in file
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
