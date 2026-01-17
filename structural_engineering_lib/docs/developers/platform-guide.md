# Platform Guide: Build Structural Automations

**Type:** Guide
**Audience:** Developers
**Status:** Production Ready
**Importance:** Critical
**Created:** 2026-01-15
**Last Updated:** 2026-01-15

---

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start (15 Minutes)](#quick-start)
3. [Core Concepts](#core-concepts)
4. [Integration Patterns](#integration-patterns)
5. [Advanced Topics](#advanced-topics)
6. [Best Practices](#best-practices)
7. [Next Steps](#next-steps)

---

## Introduction

### What is structural_engineering_lib?

A **Python/VBA library for structural engineering calculations** following IS 456:2000 (Indian Standard Code). It provides:

- ✅ **29 public functions** for beam design, analysis, and detailing
- ✅ **Type-safe API** with comprehensive validation
- ✅ **Production-ready** (2700+ tests, 84%+ coverage)
- ✅ **Multiple interfaces** (Python API, Excel VBA, Streamlit UI, CLI)
- ✅ **Extensible architecture** for custom modules

### What Can You Build?

**Use this library as a foundation to create:**

| Application Type | Examples |
|-----------------|----------|
| **Custom Analysis Tools** | ACI 318 designer, Eurocode validator |
| **Report Generators** | PDF/HTML reports with company branding |
| **Web Applications** | Online calculators (Streamlit/Flask/Django) |
| **Excel Add-ins** | Custom ribbon tools for structural teams |
| **Batch Processors** | Analyze 100s of beams from ETABS/SAP2000 |
| **QA Tools** | Multi-code compliance checkers |
| **Cost Optimizers** | Find cheapest compliant designs |

### Why Use This Platform?

| Benefit | Description |
|---------|-------------|
| **Save Time** | Don't reinvent beam design calculations |
| **Production-Ready** | 2700+ tests, proven in real projects |
| **Well-Documented** | Every function has examples + docs |
| **Extensible** | Add features without modifying core |
| **Multi-Interface** | Python API, VBA, Streamlit, CLI |

---

##  Quick Start

**Goal:** Design a beam in < 15 minutes

### Step 1: Install (2 minutes)

```bash
# Python installation
pip install git+https://github.com/Pravin-surawase/structural_engineering_lib.git

# Or clone and install locally
git clone https://github.com/Pravin-surawase/structural_engineering_lib.git
cd structural_engineering_lib/Python
pip install -e .
```

**Dependencies:**
- Python 3.11+
- No required dependencies (ezdxf optional for DXF export)

### Step 2: Design Your First Beam (3 minutes)

```python
# quick_start_example.py
from structural_lib.api import design_beam_is456

# Design a residential beam
result = design_beam_is456(
    beam_id="B1",
    story="Ground Floor",
    span_mm=5000,          # 5m span
    b_mm=300,              # 300mm width
    D_mm=500,              # 500mm total depth
    cover_mm=25,           # 25mm clear cover
    fck_nmm2=25.0,         # M25 concrete
    fy_nmm2=500.0,         # Fe500 steel
    mu_knm=120.0,          # 120 kN·m moment
    vu_kn=80.0,            # 80 kN shear
)

# Check if design is OK
if result.ok:
    print(f"✓ Design successful!")
    print(f"  Steel required: {result.ast_required_start:.0f} mm²")
    print(f"  Provided: {result.bars_bottom_start.count}-T{result.bars_bottom_start.diameter}")
    print(f"  Stirrups: {result.stirrups_start.callout()}")
else:
    print(f"✗ Design failed:")
    for error in result.errors:
        print(f"  - {error.error_message}")
```

**Run it:**
```bash
python quick_start_example.py
```

**Expected output:**
```
✓ Design successful!
  Steel required: 1256 mm²
  Provided: 4-T20
  Stirrups: 2-legged T8 @ 150 mm c/c
```

### Step 3: Export Results (5 minutes)

#### Generate Bar Bending Schedule (BBS)

```python
from structural_lib.api import generate_bbs_from_detailing

# Continue from previous example
bbs_items = generate_bbs_from_detailing(result)

for item in bbs_items:
    print(f"{item.bar_mark}: {item.count}x T{item.diameter} @ {item.length_mm}mm")
```

#### Export to DXF Drawing

```python
from structural_lib.dxf_export import quick_dxf

# Generate CAD drawing (requires ezdxf: pip install ezdxf)
dxf_path = quick_dxf(
    detailing=result,
    output_path="beam_B1.dxf",
    include_title_block=True,
    project_name="My Project"
)

print(f"DXF saved to: {dxf_path}")
```

#### Generate PDF Report

```python
from structural_lib.reports import generate_html_report

# Generate detailed HTML report
html = generate_html_report(
    design_result=result,
    title="Beam B1 - Ground Floor",
    show_detailed=True
)

# Save to file
with open("beam_B1.html", "w") as f:
    f.write(html)
```

### Step 4: Validate & Check (5 minutes)

```python
from structural_lib.api import check_beam_is456

# Comprehensive compliance check
compliance = check_beam_is456(
    b_mm=result.b,
    D_mm=result.D,
    ast_top_start_mm2=result.ast_top_start,
    ast_bottom_start_mm2=result.ast_required_start,
    fck_nmm2=25.0,
    fy_nmm2=500.0,
    # ... other parameters
)

if compliance.compliant:
    print("✓ Design is IS 456 compliant")
else:
    print("✗ Compliance issues:")
    for issue in compliance.violations:
        print(f"  - {issue.clause}: {issue.message}")
```

**Congratulations!** You've designed, exported, and validated a beam in 15 minutes.

---

## Core Concepts

### API Surface

**29 public functions organized by purpose:**

| Category | Functions | Purpose |
|----------|-----------|---------|
| **Design** | `design_beam_is456`, `check_beam_is456`, `detail_beam_is456` | Main entry points |
| **Flexure** | `design_beam_flexure_is456`, `calculate_mu_lim` | Moment design |
| **Shear** | `design_shear`, `calculate_shear_capacity` | Shear design |
| **Detailing** | `calculate_development_length`, `calculate_lap_length` | Rebar details |
| **Serviceability** | `check_deflection_is456`, `check_crack_width` | Service checks |
| **Optimization** | `optimize_beam_cost`, `suggest_design_improvements` | Smart features |
| **Analysis** | `compute_bmd_sfd`, `analyze_torsion` | Load analysis |
| **BBS** | `generate_bbs_from_detailing`, `format_bbs_csv` | Bar schedules |

**Full API reference:** [docs/reference/api.md](../reference/api.md)

### Data Flow

```
Input Parameters → Validation → Design → Detailing → Output
      ↓                ↓          ↓         ↓         ↓
   (b, D, Mu)    (errors?)   (Ast req)  (bars)   (result)
```

**Example:**
```python
# 1. Input
params = {"b_mm": 300, "D_mm": 500, "mu_knm": 120, ...}

# 2. Validation (automatic)
# Library checks: b > 0, D > b, Mu > 0, etc.

# 3. Design (flexure + shear)
# Calculates: Ast required, xu, Mu_capacity, etc.

# 4. Detailing (bar selection)
# Selects: 4-T20 bottom, 2-T12 top, T8@150 stirrups

# 5. Output (structured result)
result = design_beam_is456(**params)
# result.ok = True
# result.ast_required_start = 1256 mm²
# result.bars_bottom_start = BarArrangement(count=4, diameter=20, ...)
```

### Data Structures

**All functions use typed data structures:**

```python
from structural_lib.data_types import (
    BeamDesignResult,     # Main result from design_beam_is456()
    BarArrangement,       # Rebar configuration (count, dia, spacing)
    StirrupArrangement,   # Stirrup details (dia, legs, spacing)
    DesignError,          # Error/warning messages
    ComplianceResult,     # IS 456 compliance check
    BBSItem,              # Bar bending schedule item
)
```

**Why typed structures?**
- **Autocomplete:** Your IDE knows all available fields
- **Type safety:** Catch errors before runtime
- **Clear contracts:** Know exactly what functions return
- **Easy serialization:** Convert to JSON/dict easily

**Example:**
```python
result = design_beam_is456(...)

# IDE autocomplete works:
print(result.bars_bottom_start.count)      # Number of bars
print(result.bars_bottom_start.diameter)   # Bar diameter
print(result.bars_bottom_start.callout())  # "4-T20"

# Convert to dict for JSON/database
result_dict = result.as_dict()
```

### Extension Points

**Where you can add custom functionality:**

| Extension Point | How | Examples |
|----------------|-----|----------|
| **Custom Output Formats** | Import result, format as needed | PDF, Excel, JSON, XML |
| **Additional Validations** | Use `check_beam_is456()` + custom rules | Seismic, wind, deflection |
| **New Design Codes** | Build similar API for other codes | ACI 318, Eurocode 2, AS 3600 |
| **Cost Models** | Extend `optimize_beam_cost()` | Regional pricing, labor costs |
| **UI Layers** | Wrap API in your interface | Web app, desktop GUI, Excel |

**Key principle:** Library provides **calculations**, you add **presentation** and **workflow**.

---

## Integration Patterns

### Pattern 1: Simple Script

**Use case:** Quick calculations

```python
# analyze_beam.py
from structural_lib.api import design_beam_is456

# Read inputs (CSV, JSON, user input)
beams = [
    {"id": "B1", "span": 5000, "mu": 120, "vu": 80},
    {"id": "B2", "span": 6000, "mu": 180, "vu": 100},
]

# Design each beam
for beam in beams:
    result = design_beam_is456(
        beam_id=beam["id"],
        story="Ground Floor",
        span_mm=beam["span"],
        b_mm=300,
        D_mm=500,
        cover_mm=25,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
        mu_knm=beam["mu"],
        vu_kn=beam["vu"],
    )

    if result.ok:
        print(f"{beam['id']}: OK - {result.bars_bottom_start.callout()}")
    else:
        print(f"{beam['id']}: FAILED")
```

### Pattern 2: Batch Processor

**Use case:** Process 100s of beams from ETABS/SAP2000

```python
# batch_processor.py
import csv
from structural_lib.api import design_beam_is456

def process_etabs_export(csv_path, output_path):
    """Process ETABS beam forces CSV and generate design summary."""

    results = []

    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            result = design_beam_is456(
                beam_id=row["Beam"],
                story=row["Story"],
                span_mm=float(row["Length"]) * 1000,  # m to mm
                b_mm=float(row["Width"]),
                D_mm=float(row["Depth"]),
                cover_mm=25,
                fck_nmm2=25.0,
                fy_nmm2=500.0,
                mu_knm=float(row["Mu_max"]),
                vu_kn=float(row["Vu_max"]),
            )

            results.append({
                "Beam": result.beam_id,
                "Story": result.story,
                "Status": "OK" if result.ok else "FAIL",
                "Steel_Bottom": result.bars_bottom_start.callout() if result.ok else "-",
                "Stirrups": result.stirrups_start.callout() if result.ok else "-",
            })

    # Write summary CSV
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    return results

# Usage
results = process_etabs_export("etabs_forces.csv", "design_summary.csv")
print(f"Processed {len(results)} beams")
```

### Pattern 3: Web Application (Streamlit)

**Use case:** Online calculator

```python
# streamlit_app.py
import streamlit as st
from structural_lib.api import design_beam_is456

st.title("Beam Design Calculator")

# Inputs
col1, col2 = st.columns(2)
with col1:
    span = st.number_input("Span (mm)", value=5000)
    b = st.number_input("Width (mm)", value=300)
    D = st.number_input("Depth (mm)", value=500)

with col2:
    mu = st.number_input("Moment (kN·m)", value=120.0)
    vu = st.number_input("Shear (kN)", value=80.0)
    fck = st.selectbox("Concrete Grade", [20, 25, 30, 35, 40])

if st.button("Design Beam"):
    result = design_beam_is456(
        beam_id="B1",
        story="Ground Floor",
        span_mm=span,
        b_mm=b,
        D_mm=D,
        cover_mm=25,
        fck_nmm2=float(fck),
        fy_nmm2=500.0,
        mu_knm=mu,
        vu_kn=vu,
    )

    if result.ok:
        st.success("✓ Design successful!")
        st.write(f"**Bottom Steel:** {result.bars_bottom_start.callout()}")
        st.write(f"**Top Steel:** {result.bars_top_start.callout()}")
        st.write(f"**Stirrups:** {result.stirrups_start.callout()}")
    else:
        st.error("✗ Design failed")
        for error in result.errors:
            st.warning(error.error_message)
```

**Run:** `streamlit run streamlit_app.py`

### Pattern 4: Excel VBA Integration

**Use case:** Custom Excel add-in

```vba
' Excel VBA Module
Private Declare PtrSafe Function DesignBeamIS456 Lib "structural_lib.dll" _
    (ByVal span As Double, ByVal b As Double, ByVal D As Double, _
     ByVal mu As Double, ByVal vu As Double) As String

Function BEAM_DESIGN(span As Double, b As Double, D As Double, _
                      mu As Double, vu As Double) As String
    ' Wrapper function for Excel formula
    ' Usage: =BEAM_DESIGN(5000, 300, 500, 120, 80)

    Dim result As String
    result = DesignBeamIS456(span, b, D, mu, vu)

    BEAM_DESIGN = result  ' Returns "4-T20 + T8@150"
End Function
```

**Or use Python-Excel bridge (xlwings):**

```python
# excel_functions.py
import xlwings as xw
from structural_lib.api import design_beam_is456

@xw.func
def beam_design_xl(span, b, D, mu, vu):
    """Excel function: =beam_design_xl(5000, 300, 500, 120, 80)"""
    result = design_beam_is456(
        beam_id="B1",
        story="GF",
        span_mm=span,
        b_mm=b,
        D_mm=D,
        cover_mm=25,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
        mu_knm=mu,
        vu_kn=vu,
    )

    if result.ok:
        return f"{result.bars_bottom_start.callout()} + {result.stirrups_start.callout()}"
    else:
        return "ERROR"
```

### Pattern 5: REST API (Flask)

**Use case:** Microservice for design calculations

```python
# api_server.py
from flask import Flask, request, jsonify
from structural_lib.api import design_beam_is456

app = Flask(__name__)

@app.route("/api/v1/design/beam", methods=["POST"])
def design_beam():
    """
    POST /api/v1/design/beam
    Body: {"span_mm": 5000, "b_mm": 300, ...}
    """
    try:
        params = request.json

        result = design_beam_is456(
            beam_id=params.get("beam_id", "B1"),
            story=params.get("story", "GF"),
            span_mm=params["span_mm"],
            b_mm=params["b_mm"],
            D_mm=params["D_mm"],
            cover_mm=params.get("cover_mm", 25),
            fck_nmm2=params.get("fck_nmm2", 25.0),
            fy_nmm2=params.get("fy_nmm2", 500.0),
            mu_knm=params["mu_knm"],
            vu_kn=params["vu_kn"],
        )

        return jsonify({
            "ok": result.ok,
            "beam_id": result.beam_id,
            "bottom_steel": result.bars_bottom_start.callout() if result.ok else None,
            "top_steel": result.bars_top_start.callout() if result.ok else None,
            "stirrups": result.stirrups_start.callout() if result.ok else None,
            "errors": [e.error_message for e in result.errors],
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
```

**Usage:**
```bash
curl -X POST http://localhost:5000/api/v1/design/beam \
  -H "Content-Type: application/json" \
  -d '{"span_mm": 5000, "b_mm": 300, "D_mm": 500, "mu_knm": 120, "vu_kn": 80}'
```

---

## Advanced Topics

### Custom Output Formats

**Generate PDF reports:**

```python
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from structural_lib.api import design_beam_is456

def generate_pdf_report(result, output_path):
    """Generate PDF report from design result."""
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []

    # Title
    story.append(Paragraph(f"<b>Beam Design Report: {result.beam_id}</b>"))

    # Design summary table
    data = [
        ["Parameter", "Value"],
        ["Beam ID", result.beam_id],
        ["Story", result.story],
        ["Span (mm)", result.span],
        ["Width (mm)", result.b],
        ["Depth (mm)", result.D],
        ["Bottom Steel", result.bars_bottom_start.callout()],
        ["Top Steel", result.bars_top_start.callout()],
        ["Stirrups", result.stirrups_start.callout()],
    ]

    story.append(Table(data))
    doc.build(story)

# Usage
result = design_beam_is456(...)
generate_pdf_report(result, "beam_report.pdf")
```

### Custom Validation Rules

**Add seismic checks:**

```python
from structural_lib.api import design_beam_is456, check_beam_is456

def design_with_seismic(span_mm, mu_knm, vu_kn, **kwargs):
    """Design beam with additional seismic requirements."""

    # 1. Standard design
    result = design_beam_is456(
        span_mm=span_mm,
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        **kwargs
    )

    if not result.ok:
        return result

    # 2. Additional seismic checks (custom rules)
    errors = []

    # Rule 1: Minimum steel for ductility (1.2% min)
    steel_ratio = result.ast_required_start / (result.b * result.d)
    if steel_ratio < 0.012:
        errors.append(f"Seismic: Steel ratio {steel_ratio:.3f} < 1.2% min for ductile detailing")

    # Rule 2: Stirrup spacing for confinement
    if result.stirrups_start.spacing > 100:
        errors.append(f"Seismic: Stirrup spacing {result.stirrups_start.spacing}mm > 100mm (not ductile)")

    # Rule 3: Minimum shear reinforcement
    if result.stirrups_start.diameter < 10:
        errors.append(f"Seismic: Stirrup diameter {result.stirrups_start.diameter}mm < 10mm min")

    # 3. Return modified result
    if errors:
        result.ok = False
        result.errors.extend([DesignError(error_message=e) for e in errors])

    return result
```

### New Design Code Implementation

**Build ACI 318 support:**

```python
# aci318.py - Custom module
from structural_lib.data_types import BeamDesignResult, BarArrangement

def design_beam_aci318(width_in, depth_in, mu_kipft, fc_psi=4000, fy_ksi=60):
    """
    Design beam per ACI 318 (US code).

    Args:
        width_in: Beam width (inches)
        depth_in: Beam depth (inches)
        mu_kipft: Factored moment (kip-ft)
        fc_psi: Concrete strength (psi)
        fy_ksi: Steel yield strength (ksi)

    Returns:
        BeamDesignResult (reuses library data structure)
    """

    # 1. Convert units (ACI uses imperial)
    mu_inkip = mu_kipft * 12  # Convert kip-ft to in-kip
    d_in = depth_in - 2.5  # Assume 2.5" cover

    # 2. Calculate steel (ACI 318 equations)
    Rn = mu_inkip / (width_in * d_in**2)  # psi
    rho = 0.85 * fc_psi / fy_ksi / 1000 * (1 - (1 - 2*Rn/(0.85*fc_psi))**0.5)
    As_required = rho * width_in * d_in  # in²

    # 3. Select bars (US bar sizes: #4=#13mm, #5=#16mm, #6=#19mm, #7=#22mm, #8=#25mm)
    bar_areas = {4: 0.20, 5: 0.31, 6: 0.44, 7: 0.60, 8: 0.79}  # in²

    for size, area in sorted(bar_areas.items(), key=lambda x: x[1]):
        count = int(As_required / area) + 1
        if count <= 6:  # Max 6 bars in single layer
            break

    # 4. Return result (reuse library structure)
    return BeamDesignResult(
        ok=True,
        beam_id="B1",
        story="ACI Design",
        span=width_in * 25.4,  # Convert back to mm for consistency
        b=width_in * 25.4,
        D=depth_in * 25.4,
        d=d_in * 25.4,
        ast_required_start=As_required * 645.16,  # in² to mm²
        bars_bottom_start=BarArrangement(
            count=count,
            diameter=size * 3.175,  # US bar # to mm
            area_provided=count * area * 645.16,
            spacing=100,
            layers=1
        ),
        # ... other fields
    )

# Usage - same interface as IS 456
result = design_beam_aci318(
    width_in=12,
    depth_in=20,
    mu_kipft=150,
    fc_psi=4000,
    fy_ksi=60
)

print(f"ACI Design: {result.bars_bottom_start.count} bars")
```

### Cost Optimization Integration

**Add regional pricing:**

```python
from structural_lib.api import optimize_beam_cost

def optimize_with_regional_pricing(span_mm, mu_knm, vu_kn, region="Mumbai"):
    """Optimize beam cost with regional material prices."""

    # Regional pricing (INR per unit)
    prices = {
        "Mumbai": {
            "concrete_m3": 6500,
            "steel_kg": 75,
            "formwork_m2": 450,
        },
        "Delhi": {
            "concrete_m3": 6000,
            "steel_kg": 70,
            "formwork_m2": 400,
        },
        "Bangalore": {
            "concrete_m3": 6200,
            "steel_kg": 72,
            "formwork_m2": 420,
        },
    }

    # Get optimization result
    result = optimize_beam_cost(
        span_mm=span_mm,
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        # Use regional pricing
        price_concrete_per_m3=prices[region]["concrete_m3"],
        price_steel_per_kg=prices[region]["steel_kg"],
        price_formwork_per_m2=prices[region]["formwork_m2"],
    )

    return result

# Usage
result = optimize_with_regional_pricing(5000, 120, 80, region="Bangalore")
print(f"Optimal design (Bangalore): ₹{result.optimal_cost:.0f}")
```

---

## Best Practices

### 1. Error Handling

**Always check `result.ok` before accessing fields:**

```python
result = design_beam_is456(...)

if result.ok:
    # Safe to access design fields
    steel = result.bars_bottom_start.callout()
    print(f"Steel: {steel}")
else:
    # Handle errors
    print("Design failed:")
    for error in result.errors:
        print(f"  - {error.error_message}")
        if error.clause_ref:
            print(f"    Ref: IS 456 {error.clause_ref}")
```

### 2. Input Validation

**Library validates automatically, but pre-check for better UX:**

```python
def validate_inputs_before_design(span, b, D, mu, vu):
    """Pre-validate inputs before calling library."""

    errors = []

    if span <= 0:
        errors.append("Span must be positive")
    if b <= 0 or D <= 0:
        errors.append("Dimensions must be positive")
    if D < b:
        errors.append("Depth must be >= width")
    if mu < 0 or vu < 0:
        errors.append("Forces must be non-negative")
    if span / D > 35:
        errors.append("Span/depth ratio > 35 (deflection issues likely)")

    return errors

# Usage
errors = validate_inputs_before_design(5000, 300, 500, 120, 80)
if errors:
    for e in errors:
        print(f"Input error: {e}")
else:
    result = design_beam_is456(...)  # Safe to proceed
```

### 3. Unit Consistency

**Library uses mm, kN, kN·m, N/mm² internally:**

```python
# ✅ CORRECT: Consistent units
result = design_beam_is456(
    span_mm=5000,        # mm
    b_mm=300,            # mm
    D_mm=500,            # mm
    mu_knm=120.0,        # kN·m
    vu_kn=80.0,          # kN
    fck_nmm2=25.0,       # N/mm² (MPa)
    fy_nmm2=500.0,       # N/mm² (MPa)
)

# ❌ WRONG: Mixed units
result = design_beam_is456(
    span_mm=5,           # ERROR: Meant 5m, but gave 5mm!
    mu_knm=120000,       # ERROR: Gave N·m instead of kN·m
)
```

**Convert at boundaries:**

```python
def design_beam_metric(span_m, b_mm, D_mm, mu_knm, vu_kn):
    """Wrapper that accepts span in meters."""
    return design_beam_is456(
        span_mm=span_m * 1000,  # Convert m to mm
        b_mm=b_mm,
        D_mm=D_mm,
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        # ...
    )
```

### 4. Testing Custom Code

**Test your integrations:**

```python
import pytest
from my_module import design_with_seismic

def test_seismic_design_success():
    """Test seismic design for valid input."""
    result = design_with_seismic(
        span_mm=5000,
        mu_knm=120,
        vu_kn=80,
        b_mm=300,
        D_mm=500,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
    )

    assert result.ok, "Design should succeed"
    assert result.stirrups_start.spacing <= 100, "Stirrup spacing for ductility"

def test_seismic_design_failure():
    """Test seismic design rejection for inadequate steel."""
    result = design_with_seismic(
        span_mm=8000,  # Long span
        mu_knm=50,     # Low moment → low steel
        vu_kn=40,
        b_mm=300,
        D_mm=400,
        fck_nmm2=20.0,
        fy_nmm2=500.0,
    )

    assert not result.ok, "Should fail seismic checks"
    assert any("Seismic" in e.error_message for e in result.errors)
```

### 5. Performance Optimization

**Cache results for repeated calculations:**

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_beam_design(span, b, D, mu, vu, fck, fy):
    """Cache design results for identical inputs."""
    return design_beam_is456(
        beam_id="B1",
        story="GF",
        span_mm=span,
        b_mm=b,
        D_mm=D,
        cover_mm=25,
        fck_nmm2=fck,
        fy_nmm2=fy,
        mu_knm=mu,
        vu_kn=vu,
    )

# First call: computes design
result1 = cached_beam_design(5000, 300, 500, 120, 80, 25.0, 500.0)

# Second call with same inputs: instant (from cache)
result2 = cached_beam_design(5000, 300, 500, 120, 80, 25.0, 500.0)

assert result1 is result2  # Same object from cache
```

### 6. Logging & Debugging

**Add logging for production systems:**

```python
import logging
from structural_lib.api import design_beam_is456

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def design_with_logging(beam_id, **kwargs):
    """Design beam with comprehensive logging."""

    logger.info(f"Designing beam {beam_id}")
    logger.debug(f"Inputs: {kwargs}")

    try:
        result = design_beam_is456(beam_id=beam_id, **kwargs)

        if result.ok:
            logger.info(f"✓ {beam_id} design successful")
            logger.debug(f"Steel: {result.bars_bottom_start.callout()}")
        else:
            logger.warning(f"✗ {beam_id} design failed")
            for error in result.errors:
                logger.warning(f"  - {error.error_message}")

        return result

    except Exception as e:
        logger.error(f"Exception designing {beam_id}: {e}", exc_info=True)
        raise
```

---

## Next Steps

### Continue Learning

1. **Explore Examples** → [Integration Examples](integration-examples.md) - 10+ real-world patterns
2. **Understand Extension** → [Extension Guide](extension-guide.md) - How to add features
3. **Check API** → [API Reference](../reference/api.md) - All 29 functions documented
4. **Read Architecture** → [Project Overview](../architecture/project-overview.md) - System design

### Build Your First Project

**Choose a starter project:**

1. **Simple:** Command-line batch processor for 50 beams
2. **Medium:** Streamlit web app with custom branding
3. **Advanced:** REST API with database integration
4. **Expert:** Custom design code (ACI/Eurocode) implementation

### Get Help

- **Questions?** → Open [GitHub Issue](https://github.com/Pravin-surawase/structural_engineering_lib/issues)
- **Bug report?** → Include code snippet + error message
- **Feature request?** → Explain use case + expected behavior

### Contribute Back

**Built something cool?**

1. Share your project (we'll feature it!)
2. Contribute examples back to the library
3. Write a blog post about your experience
4. Help answer questions in Issues

---

**Happy Building!** 🚀

*Questions or feedback? [Open an issue](https://github.com/Pravin-surawase/structural_engineering_lib/issues)*
