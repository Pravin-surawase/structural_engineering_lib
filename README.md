# IS 456 RC Beam Design Library

A reusable, UI-agnostic structural engineering library for RC rectangular beam design (flexure + shear) per **IS 456:2000** (Indian Standard for Plain and Reinforced Concrete).

## Status

✅ **v1.0.0** — Implementation Complete.

## Features

- ✅ **Pure functions** — No UI dependencies (no MsgBox, no worksheet access)
- ✅ **Limit state design** — As per IS 456:2000
- ✅ **Flexural design** — Singly reinforced rectangular beams
- ✅ **Shear design** — Stirrup design with Table 19/20 lookup
- ✅ **Dual implementation** — VBA (Excel) + Python with identical API
- ✅ **Portable** — Import into any Excel workbook or Python project

## Scope

| Version | Features |
|---------|----------|
| **v1.0** (Current) | Rectangular beams, singly reinforced flexure, shear design |
| v1.1 | Doubly reinforced flexure |
| v1.2 | Flanged beams (T, L) |
| v2.0 | IS 13920 ductile detailing |

## Directory Structure

```
structural_engineering_lib/
├── VBA/
│   ├── Modules/            ← Core .bas modules (Import these into Excel)
│   │   ├── M01_Constants.bas
│   │   ├── M02_Types.bas
│   │   ├── M03_Tables.bas
│   │   ├── M04_Utilities.bas
│   │   ├── M05_Materials.bas
│   │   ├── M06_Flexure.bas
│   │   ├── M07_Shear.bas
│   │   ├── M08_API.bas
│   │   └── M09_UDFs.bas    ← Excel UDF wrappers
│   └── Tests/              ← VBA test modules
├── Python/
│   ├── structural_lib/     ← Python package
│   └── tests/              ← Unit tests
├── docs/
│   ├── RESEARCH_AND_FINDINGS.md    ← Comprehensive research document
│   ├── DEVELOPMENT_GUIDE.md        ← Coding standards and guidelines
│   └── IS456_QUICK_REFERENCE.md    ← Formulas cheat sheet
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
from structural_lib import flexure, shear

# Design a beam
result = flexure.design_singly_reinforced(
    b=230, d=450, d_total=500, 
    mu_knm=100, fck=20, fy=415
)

if result.is_safe:
    print(f"Ast Required: {result.asc_required} mm2")
```

2. Press `Alt + F11` to open VBA Editor
3. Right-click on VBA Project → **Import File...**
4. Select all `.bas` files from `VBA/Modules/`
5. Save workbook as `.xlsm`

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

## Documentation

- **[Research and Findings](docs/RESEARCH_AND_FINDINGS.md)** — Complete research document with formulas, tables, and API design
- **[Development Guide](docs/DEVELOPMENT_GUIDE.md)** — Coding standards, naming conventions, testing guidelines
- **[IS 456 Quick Reference](docs/IS456_QUICK_REFERENCE.md)** — Formulas cheat sheet for quick lookup

## References

- IS 456:2000 — Plain and Reinforced Concrete — Code of Practice
- SP:16-1980 — Design Aids for Reinforced Concrete to IS 456
- IS 13920:2016 — Ductile Design and Detailing of RC Structures

## License

MIT License — Free to use, modify, and distribute.

## Author

Structural Engineering Library Project
