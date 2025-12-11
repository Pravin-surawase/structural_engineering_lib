# Beginner's Complete Guide to IS 456 Structural Engineering Library

Welcome! This guide will walk you through using the **Structural Engineering Library** step by step — even if you've never written code before. We'll cover both **Python** and **Excel/VBA** paths.

---

## What This Library Does

This library automates structural engineering calculations for **reinforced concrete beams** per **IS 456:2000** (Indian Standard for Plain and Reinforced Concrete). It can:

1. **Design beams** — Calculate required reinforcement for bending (flexure) and shear
2. **Generate detailing** — Compute development lengths, lap lengths, bar spacing
3. **Create CAD drawings** — Export DXF files for fabrication drawings
4. **Batch process** — Handle multiple beams from CSV/Excel files

---

## Choose Your Path

| If you prefer... | Use this |
|------------------|----------|
| Writing scripts, automation, batch processing | **Python** (see Part A) |
| Spreadsheets, Excel formulas, visual interface | **Excel/VBA** (see Part B) |
| Both for different tasks | Read both sections! |

---

# Part A: Python Path

## Step 1: Install Python

### Windows
1. Download Python from [python.org](https://www.python.org/downloads/)
2. **Important:** Check "Add Python to PATH" during installation
3. Open Command Prompt and verify: `python --version`

### macOS
1. Open Terminal
2. Install via Homebrew: `brew install python`
3. Or download from [python.org](https://www.python.org/downloads/)
4. Verify: `python3 --version`

### Linux
```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv
```

---

## Step 2: Set Up the Project

```bash
# 1. Navigate to your projects folder
cd ~/projects  # or wherever you want

# 2. Clone or download the repository
git clone https://github.com/your-repo/structural_engineering_lib.git
cd structural_engineering_lib

# 3. Create a virtual environment (keeps dependencies isolated)
python3 -m venv .venv

# 4. Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# 5. Install the library
pip install --upgrade pip
pip install -e Python/.[dev]

# 6. (Optional) Install DXF export support
pip install ezdxf
```

Your terminal prompt should now show `(.venv)` indicating the virtual environment is active.

---

## Step 3: Your First Calculation

Create a file called `my_first_beam.py`:

```python
"""
My First Beam Design
A simply supported beam carrying a moment of 150 kN·m
"""

from structural_lib import flexure

# Beam dimensions (all in mm)
b = 300      # Width
d = 450      # Effective depth (to centroid of tension steel)
D = 500      # Overall depth
cover = 40   # Clear cover

# Material properties
fck = 25     # Concrete grade M25 (N/mm²)
fy = 500     # Steel grade Fe500 (N/mm²)

# Applied moment (from analysis)
Mu = 150     # Factored moment in kN·m

# Design the beam
result = flexure.design_singly_reinforced(
    b=b, d=d, d_total=D, mu_knm=Mu, fck=fck, fy=fy
)

# Print results
print("=" * 50)
print("BEAM DESIGN RESULTS (IS 456:2000)")
print("=" * 50)
print(f"Section: {b} × {D} mm")
print(f"Materials: M{fck} / Fe{fy}")
print(f"Applied Moment: {Mu} kN·m")
print("-" * 50)
print(f"Limiting Moment (Mu_lim): {result.mu_lim:.2f} kN·m")
print(f"Section Type: {'Singly Reinforced' if result.ast_required > 0 else 'Doubly Reinforced'}")
print(f"Tension Steel Required (Ast): {result.ast_required:.0f} mm²")
print(f"Steel Percentage: {result.pt_provided:.2f}%")
print(f"Status: {'✓ SAFE' if result.is_safe else '✗ ' + result.error_message}")
print("=" * 50)
```

Run it:
```bash
python my_first_beam.py
```

Expected output:
```
==================================================
BEAM DESIGN RESULTS (IS 456:2000)
==================================================
Section: 300 × 500 mm
Materials: M25 / Fe500
Applied Moment: 150 kN·m
--------------------------------------------------
Limiting Moment (Mu_lim): 196.54 kN·m
Section Type: Singly Reinforced
Tension Steel Required (Ast): 942 mm²
Steel Percentage: 0.70%
Status: ✓ SAFE
==================================================
```

---

## Step 4: Complete Design with Detailing

```python
"""
Complete Beam Design with Detailing
Includes shear design and rebar detailing
"""

from structural_lib import flexure, shear, detailing
import math

# === INPUTS ===
beam_id = "B1"
story = "Ground Floor"

# Geometry (mm)
b = 300       # Width
D = 500       # Total depth
d = 450       # Effective depth
span = 4000   # Clear span
cover = 40    # Clear cover

# Materials (N/mm²)
fck = 25      # M25 concrete
fy = 500      # Fe500 steel

# Loads (from structural analysis)
Mu = 150      # Factored moment (kN·m)
Vu = 100      # Factored shear (kN)

# === FLEXURE DESIGN ===
print("\n" + "=" * 60)
print("1. FLEXURE DESIGN")
print("=" * 60)

flex_result = flexure.design_singly_reinforced(
    b=b, d=d, d_total=D, mu_knm=Mu, fck=fck, fy=fy
)

print(f"Mu_lim = {flex_result.mu_lim:.2f} kN·m")
print(f"Ast required = {flex_result.ast_required:.0f} mm²")

# Select bars
bar_dia = 16  # Using 16mm bars
bar_area = math.pi * (bar_dia/2)**2
n_bars = math.ceil(flex_result.ast_required / bar_area)
ast_provided = n_bars * bar_area

print(f"Provide: {n_bars} nos. of {bar_dia}mm bars")
print(f"Ast provided = {ast_provided:.0f} mm²")
print(f"Status: {'✓ OK' if ast_provided >= flex_result.ast_required else '✗ Insufficient'}")

# === SHEAR DESIGN ===
print("\n" + "=" * 60)
print("2. SHEAR DESIGN")
print("=" * 60)

# Stirrup details
stirrup_dia = 8
legs = 2
Asv = legs * math.pi * (stirrup_dia/2)**2  # Area of stirrup legs

# Percentage of tension steel
pt = (ast_provided * 100) / (b * d)

shear_result = shear.design_shear(
    Vu_kN=Vu, b=b, d=d, fck=fck, fy=fy, Asv=Asv, pt=pt
)

print(f"Nominal shear stress τv = {shear_result.tv:.3f} N/mm²")
print(f"Concrete shear capacity τc = {shear_result.tc:.3f} N/mm²")
print(f"Maximum shear τc,max = {shear_result.tc_max:.3f} N/mm²")
print(f"Required stirrup spacing = {shear_result.spacing:.0f} mm")
print(f"Provide: 2L-{stirrup_dia}φ @ {int(shear_result.spacing // 25) * 25} mm c/c")
print(f"Status: {'✓ OK' if shear_result.is_safe else '✗ Redesign'}")

# === DETAILING ===
print("\n" + "=" * 60)
print("3. DETAILING (IS 456 Cl 26)")
print("=" * 60)

ld = detailing.calculate_development_length(bar_dia, fck, fy)
lap = detailing.calculate_lap_length(bar_dia, fck, fy, is_seismic=False)
min_spacing = detailing.get_min_spacing(bar_dia)
actual_spacing = detailing.calculate_bar_spacing(b, cover, stirrup_dia, bar_dia, n_bars)

print(f"Development length Ld = {ld:.0f} mm ({ld/bar_dia:.0f}φ)")
print(f"Lap length = {lap:.0f} mm ({lap/bar_dia:.0f}φ)")
print(f"Min bar spacing = {min_spacing:.0f} mm")
print(f"Actual bar spacing = {actual_spacing:.0f} mm")
print(f"Spacing check: {'✓ OK' if actual_spacing >= min_spacing else '✗ Revise bars'}")

# === SUMMARY ===
print("\n" + "=" * 60)
print("DESIGN SUMMARY")
print("=" * 60)
print(f"Beam: {beam_id} at {story}")
print(f"Size: {b} × {D} mm, Span: {span} mm")
print(f"Bottom steel: {n_bars}-{bar_dia}φ")
print(f"Top steel: 2-12φ (hanger bars)")
print(f"Stirrups: 2L-{stirrup_dia}φ @ {int(shear_result.spacing // 25) * 25} mm c/c")
print(f"Clear cover: {cover} mm")
print("=" * 60)
```

---

## Step 5: Batch Processing Multiple Beams

Create a CSV file `my_beams.csv`:

```csv
BeamID,Story,b,D,Span,Cover,fck,fy,Mu,Vu
B1,Ground,300,500,4000,40,25,500,150,100
B2,Ground,300,450,3500,40,25,500,120,80
B3,First,350,600,5000,40,30,500,220,140
B4,First,300,500,4000,40,25,500,160,110
B5,Roof,250,400,3000,40,25,500,80,60
```

Process all beams:

```python
"""
Batch Process Multiple Beams
Reads from CSV, designs each beam, outputs results
"""

import csv
from structural_lib import flexure, shear, detailing
import math

def design_beam(row):
    """Design a single beam from CSV row."""
    # Parse inputs
    b = float(row['b'])
    D = float(row['D'])
    d = D - float(row['Cover']) - 8 - 8  # cover + stirrup + half bar
    fck = float(row['fck'])
    fy = float(row['fy'])
    Mu = float(row['Mu'])
    Vu = float(row['Vu'])
    cover = float(row['Cover'])
    
    # Flexure
    flex = flexure.design_singly_reinforced(b=b, d=d, d_total=D, mu_knm=Mu, fck=fck, fy=fy)
    
    # Select bars
    bar_dia = 16 if flex.ast_required > 600 else 12
    bar_area = math.pi * (bar_dia/2)**2
    n_bars = max(2, math.ceil(flex.ast_required / bar_area))
    ast_provided = n_bars * bar_area
    
    # Shear
    stirrup_dia = 8
    Asv = 2 * math.pi * (stirrup_dia/2)**2
    pt = (ast_provided * 100) / (b * d)
    shear_res = shear.design_shear(Vu_kN=Vu, b=b, d=d, fck=fck, fy=fy, Asv=Asv, pt=pt)
    
    # Detailing
    ld = detailing.calculate_development_length(bar_dia, fck, fy)
    
    return {
        'BeamID': row['BeamID'],
        'Story': row['Story'],
        'Size': f"{int(b)}x{int(D)}",
        'Ast_req': round(flex.ast_required),
        'Bars': f"{n_bars}-{bar_dia}φ",
        'Ast_prov': round(ast_provided),
        'Stirrups': f"2L-{stirrup_dia}φ@{int(shear_res.spacing // 25) * 25}",
        'Ld': round(ld),
        'Status': '✓' if flex.is_safe and shear_res.is_safe else '✗'
    }

# Read input CSV
with open('my_beams.csv', 'r') as f:
    reader = csv.DictReader(f)
    beams = list(reader)

# Design all beams
results = [design_beam(row) for row in beams]

# Print results table
print("\n" + "=" * 90)
print("BATCH DESIGN RESULTS")
print("=" * 90)
print(f"{'Beam':<8} {'Story':<10} {'Size':<10} {'Ast_req':<10} {'Bars':<12} {'Ast_prov':<10} {'Stirrups':<18} {'Ld':<8} {'OK'}")
print("-" * 90)
for r in results:
    print(f"{r['BeamID']:<8} {r['Story']:<10} {r['Size']:<10} {r['Ast_req']:<10} {r['Bars']:<12} {r['Ast_prov']:<10} {r['Stirrups']:<18} {r['Ld']:<8} {r['Status']}")
print("=" * 90)

# Save to output CSV
with open('beam_results.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)
    print(f"\n✓ Results saved to beam_results.csv")
```

---

## Step 6: Generate DXF Drawings

```python
"""
Generate DXF CAD Drawings
Creates drawings for fabrication/detailing
"""

from structural_lib import detailing
from structural_lib.dxf_export import draw_beam_section, draw_beam_detailing

# Check if ezdxf is available
try:
    import ezdxf
    print("✓ ezdxf found - DXF export enabled")
except ImportError:
    print("✗ Install ezdxf for DXF export: pip install ezdxf")
    exit()

# Create a beam detailing result
result = detailing.create_beam_detailing(
    beam_id="B1",
    story="Ground",
    b=300, D=500, span=4000, cover=40,
    fck=25, fy=500,
    ast_start=800, ast_mid=1000, ast_end=800,
    asc_start=200, asc_mid=200, asc_end=200,
    stirrup_dia=8,
    sv_start=100, sv_mid=150, sv_end=100,
    is_seismic=False
)

# Generate section drawing
draw_beam_section(
    filepath="beam_section_B1.dxf",
    b=300, D=500, cover=40,
    top_bars=[12, 12],
    bottom_bars=[16, 16, 16],
    stirrup_dia=8
)
print("✓ Created: beam_section_B1.dxf")

# Generate complete detailing drawing
draw_beam_detailing(
    filepath="beam_detailing_B1.dxf",
    result=result
)
print("✓ Created: beam_detailing_B1.dxf")

print("\nOpen these .dxf files in AutoCAD, DraftSight, or any CAD viewer.")
```

---

# Part B: Excel/VBA Path

## Step 1: Set Up Excel

1. **Download** the latest `StructEngLib.xlam` add-in OR the `BeamDesignApp.xlsm` workbook
2. **Enable macros:**
   - File → Options → Trust Center → Trust Center Settings
   - Macro Settings → Enable all macros
   - Check "Trust access to the VBA project object model"
3. **Install add-in** (if using .xlam):
   - File → Options → Add-ins → Go → Browse → Select the .xlam file

---

## Step 2: Available Functions

After setup, these functions are available in your worksheets:

### Flexure Functions
| Function | Description | Example |
|----------|-------------|---------|
| `=IS456_MuLim(b, d, fck, fy)` | Limiting moment capacity | `=IS456_MuLim(300, 450, 25, 500)` → 196.5 |
| `=IS456_AstRequired(b, d, Mu, fck, fy)` | Required tension steel | `=IS456_AstRequired(300, 450, 150, 25, 500)` → 942 |

### Shear Functions
| Function | Description | Example |
|----------|-------------|---------|
| `=IS456_Tc(fck, pt)` | Concrete shear strength | `=IS456_Tc(25, 0.75)` → 0.56 |
| `=IS456_TcMax(fck)` | Maximum shear stress | `=IS456_TcMax(25)` → 3.1 |
| `=IS456_ShearSpacing(Vu, b, d, fck, fy, Asv, pt)` | Required stirrup spacing | `=IS456_ShearSpacing(100, 300, 450, 25, 500, 100, 0.75)` |

### Detailing Functions
| Function | Description | Example |
|----------|-------------|---------|
| `=IS456_Ld(bar_dia, fck, fy)` | Development length | `=IS456_Ld(16, 25, 500)` → 752 |
| `=IS456_LapLength(bar_dia, fck, fy)` | Lap splice length | `=IS456_LapLength(16, 25, 500)` → 752 |
| `=IS456_BarSpacing(b, cover, stirrup_dia, bar_dia, count)` | Bar spacing | `=IS456_BarSpacing(300, 40, 8, 16, 4)` |
| `=IS456_BarCallout(count, diameter)` | Format "3-16φ" | `=IS456_BarCallout(3, 16)` → "3-16φ" |
| `=IS456_StirrupCallout(legs, dia, spacing)` | Format "2L-8φ@150" | `=IS456_StirrupCallout(2, 8, 150)` → "2L-8φ@150" |

---

## Step 3: Sample Spreadsheet Layout

Create a new worksheet with this structure:

**Column Headers (Row 1):**
```
A: BeamID | B: b | C: D | D: d | E: Span | F: Cover | G: fck | H: fy | I: Mu | J: Vu | K: Ast_req | L: Bars | M: Stirrups | N: Ld | O: Status
```

**Sample Data (Row 2):**
```
B1 | 300 | 500 | 450 | 4000 | 40 | 25 | 500 | 150 | 100 | (formula) | (formula) | (formula) | (formula) | (formula)
```

**Formulas:**

| Cell | Formula |
|------|---------|
| K2 | `=IS456_AstRequired(B2, D2, I2, G2, H2)` |
| L2 | `=IS456_BarCallout(CEILING(K2/201, 1), 16)` |
| M2 | `=IS456_StirrupCallout(2, 8, FLOOR(IS456_ShearSpacing(J2, B2, D2, G2, H2, 100, K2*100/(B2*D2)), 25))` |
| N2 | `=IS456_Ld(16, G2, H2)` |
| O2 | `=IF(K2>0, "OK", "Check")` |

---

## Step 4: Using VBA Macros

Press `Alt+F11` to open the VBA editor, then:

```vba
Sub DesignSingleBeam()
    ' Simple beam design example
    
    Dim b As Double, d As Double, D_total As Double
    Dim fck As Double, fy As Double, Mu As Double
    Dim result As FlexureResult
    
    ' Inputs
    b = 300: d = 450: D_total = 500
    fck = 25: fy = 500: Mu = 150
    
    ' Design
    result = M06_Flexure.Design_Singly_Reinforced(b, d, D_total, Mu, fck, fy)
    
    ' Output
    MsgBox "Beam Design Results:" & vbCrLf & _
           "Mu_lim = " & Round(result.Mu_Lim, 2) & " kN-m" & vbCrLf & _
           "Ast required = " & Round(result.Ast_Required, 0) & " mm²" & vbCrLf & _
           "Status: " & IIf(result.IsSafe, "OK", result.ErrorMessage)
End Sub
```

---

## Step 5: Generate DXF from Excel

```vba
Sub ExportBeamDXF()
    ' Export current beam to DXF
    
    Dim result As BeamDetailingResult
    Dim filePath As String
    
    ' Create detailing result
    Call M15_Detailing.Create_Beam_Detailing( _
        beam_id:="B1", _
        story:="Ground", _
        b:=300, D:=500, span:=4000, cover:=40, _
        fck:=25, fy:=500, _
        ast_start:=800, ast_mid:=1000, ast_end:=800, _
        sv_start:=100, sv_mid:=150, sv_end:=100, _
        result:=result)
    
    ' Export to DXF
    filePath = ThisWorkbook.Path & "\Beam_B1.dxf"
    
    If M16_DXF.Draw_BeamDetailing(filePath, result) Then
        MsgBox "DXF exported to: " & filePath
    Else
        MsgBox "Export failed!"
    End If
End Sub
```

---

# Quick Reference Tables

## Concrete Grades (IS 456)

| Grade | fck (N/mm²) | τc,max (N/mm²) | Typical Use |
|-------|-------------|----------------|-------------|
| M15 | 15 | 2.5 | Mass concrete |
| M20 | 20 | 2.8 | Slabs, foundations |
| M25 | 25 | 3.1 | Beams, columns |
| M30 | 30 | 3.5 | High-rise structures |
| M35 | 35 | 3.7 | Prestressed concrete |
| M40 | 40 | 4.0 | Special structures |

## Steel Grades (IS 1786)

| Grade | fy (N/mm²) | xu,max/d | Typical Use |
|-------|------------|----------|-------------|
| Fe250 | 250 | 0.53 | Mild steel (old) |
| Fe415 | 415 | 0.48 | Standard HYSD |
| Fe500 | 500 | 0.46 | Common current |
| Fe550 | 550 | 0.44 | High strength |

## Standard Bar Sizes

| Diameter (mm) | Area (mm²) | Weight (kg/m) |
|--------------|------------|---------------|
| 8 | 50.3 | 0.395 |
| 10 | 78.5 | 0.617 |
| 12 | 113.1 | 0.888 |
| 16 | 201.1 | 1.58 |
| 20 | 314.2 | 2.47 |
| 25 | 490.9 | 3.85 |
| 32 | 804.2 | 6.31 |

---

# Troubleshooting

| Problem | Solution |
|---------|----------|
| "Module not found" (Python) | Activate venv: `source .venv/bin/activate` |
| "ezdxf not found" | `pip install ezdxf` |
| Excel functions not working | Enable macros, install add-in |
| VBA compile error | Import modules in correct order (see VBA_GUIDE.md) |
| DXF won't open | Check file path has no special characters |
| Results seem wrong | Verify units (mm, N/mm², kN·m) |

---

# Next Steps

1. **Learn IS 456** — See `docs/IS456_QUICK_REFERENCE.md`
2. **API Reference** — See `docs/API_REFERENCE.md`
3. **Contribute** — See `docs/DEVELOPMENT_GUIDE.md`
4. **Report Issues** — Open a GitHub issue with input values and expected vs actual results

---

*Document Version: 0.7.0 | Last Updated: December 2025*
