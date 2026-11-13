---
owner: Main Agent
status: active
last_updated: 2026-03-30
doc_type: guide
complexity: intermediate
tags: []
---

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

A **Python library for structural engineering calculations** following IS 456:2000 (Indian Standard Code). It provides:

- ✅ **29 public functions** for beam design, analysis, and detailing
- ✅ **Type-safe API** with comprehensive validation
- ✅ **Production-ready** (2700+ tests, 84%+ coverage)
- ✅ **Multiple interfaces** (Python API, React UI, FastAPI REST, CLI)
- ✅ **Extensible architecture** for custom modules

### What Can You Build?

**Use this library as a foundation to create:**

| Application Type | Examples |
|-----------------|----------|
| **Custom Analysis Tools** | ACI 318 designer, Eurocode validator |
| **Report Generators** | PDF/HTML reports with company branding |
| **Web Applications** | Online calculators (React/Flask/Django) |
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
| **Multi-Interface** | Python API, React UI, FastAPI, CLI |

---

##  Quick Start

**Goal:** Design a beam in < 15 minutes

### Step 1: Install the current release

Use the exact version listed on the
[current release page](../getting-started/release-status.md).

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install "structural-lib-is456==0.29.0"
python -m structural_lib install-preflight
```

To qualify an unreleased candidate, use a fresh environment and pass the exact
wheel path from its artifact record to `python -m pip install`.

For source development, clone the repository and run
`python -m pip install -e ./Python` from its root. Python 3.11+ and the base
dependencies declared in the package metadata are required. DXF, Jinja2 and
PDF rendering use their separately declared extras.

To test an unpublished candidate, install its retained wheel by absolute path
in a fresh environment and confirm its version and origin with
`python -m structural_lib install-preflight`.

### Step 2: Design, detail, schedule and report one beam

Save this complete block as `quick_start_example.py` and run it from any
writable directory. Every geometric/material/detailing choice is explicit.
These values illustrate one supported case; they are not a project approval.

```python
# quick_start_example.py
import json
from pathlib import Path

from structural_lib import api
from structural_lib.design.is456 import beam
from structural_lib.reports import generate_html_report

options = beam.BeamDetailingOptionsV1(
    standard=beam.DetailingStandard.IS456,
    clear_cover_mm=40,
    tension_bar_diameter_mm=20,
    compression_bar_diameter_mm=16,
    nominal_top_steel_ratio=0.25,
    stirrup_diameter_mm=8,
    stirrup_legs=2,
    stirrup_spacing_support_mm=150,
    stirrup_spacing_mid_mm=200,
)
request = beam.load({
    "identity": {"member_id": "B1", "story": "L1", "case_id": "ULS-1"},
    "section": {"span_mm": 5000, "b_mm": 300, "D_mm": 550, "d_mm": 492},
    "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
    "actions": {"mu_knm": 150, "vu_kn": 80},
    "calculation_basis": {"d_dash_mm": 56, "asv_mm2": options.asv_mm2},
    "detailing": options.model_dump(mode="json"),
    "source_provenance": "Illustrative developer quickstart inputs",
})
result = beam.design_and_detail(request)
print("Engineering status:", result.engineering_status.value)
print("Qualified review required:", result.qualified_review_required)

# BBS admission uses the checked canonical result, including detailing.
schedule = beam.bbs(result)
print("BBS rows:", len(schedule.items))

output = Path("beam_B1_outputs")
output.mkdir(exist_ok=True)
api.export_bbs(schedule, output / "beam_B1.bbs.json", fmt="json")
api.export_bbs(schedule, output / "beam_B1.bbs.csv", fmt="csv")
(output / "beam_B1.result.json").write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
report = api.generate_calculation_report(result)
report.export_json(output / "beam_B1.calculation.json")
report.export_html(output / "beam_B1.html")
report.export_markdown(output / "beam_B1.md")
(output / "beam_B1.template.html").write_text(generate_html_report(result), encoding="utf-8")
```

Expected status: `PASS`; qualified review required: `True`; BBS rows: `9`.
The calculation report contains required steel separately from the actual
provided top/bottom bars. Missing detailing is unavailable, never inferred
from required steel. `generate_html_report` uses a complete basic fallback
without Jinja2; install `[report]` for the named Jinja2 templates. The raw
canonical JSON export keeps its own result schema and envelope.

### Step 3: Optional drawing and PDF exports

Install the matching candidate with its `[dxf]` extra before running the DXF
block. For example, use the quoted local wheel path with `[dxf]` appended in
`python -m pip install`. Continue in the same Python session as Step 2:

```python
# optional_dxf_export
api.compute_dxf(result, output / "beam_B1.dxf")
```

The `[pdf]` extra supplies WeasyPrint; its platform renderer dependencies must
also be available. PDF is a rendering of the same calculation HTML:

```python
# optional_pdf_export
from weasyprint import HTML

HTML(filename=str(output / "beam_B1.html")).write_pdf(output / "beam_B1.pdf")
```

### Step 4: Verify the exported basis and outcome

```python
# verify_quickstart_outputs
import json

saved = json.loads((output / "beam_B1.calculation.json").read_text(encoding="utf-8"))
assert saved["source"]["identity"] == request.identity.model_dump(mode="json")
assert saved["result_envelope"] == result.envelope.to_dict()
assert saved["inputs"]["loads"][0]["mu_knm"] == 150
assert saved["inputs"]["loads"][0]["vu_kn"] == 80
assert saved["results"]["detailing"]["status"] == "available"
assert saved["results"]["summary"]["engineering_status"] == "PASS"
assert len(schedule.items) == 9
```

Read the source checks and issues when a calculation returns `FAIL` or `HOLD`.
A failed/held case cannot become issue-ready because a file was exported.
Automatic canonical detailing after explicit serviceability retains its
existing scope HOLD; this quickstart does not expand that engineering profile.
Qualified review and professional approval remain separate from these checks.

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
from structural_lib.core.data_types import (
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
from structural_lib import design_beam_is456

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
from structural_lib import design_beam_is456

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

### Pattern 3: Web Application (React + FastAPI)

**Use case:** Online beam design calculator with 3D visualization

The V3 stack uses React 19 + React Three Fiber for the frontend and FastAPI for the backend:

```python
# fastapi_app/routers/design.py (already implemented)
from fastapi import APIRouter
from structural_lib.services.api import design_beam_is456

router = APIRouter(prefix="/api/v1/design")

@router.post("/beam")
async def design_beam(request: BeamDesignRequest):
    result = design_beam_is456(
        beam_id=request.beam_id,
        story=request.story,
        span_mm=request.span_mm,
        b_mm=request.b_mm,
        D_mm=request.D_mm,
        cover_mm=request.cover_mm,
        fck_nmm2=request.fck_nmm2,
        fy_nmm2=request.fy_nmm2,
        mu_knm=request.mu_knm,
        vu_kn=request.vu_kn,
    )
    return result.to_dict()
```

```typescript
// react_app/src/hooks/useLiveDesign.ts (already implemented)
// React frontend calls FastAPI backend
const { result, isLoading } = useLiveDesign(beamParams);
```

**Run:** `./run.sh dev` (launches both FastAPI at :8000 and React at :5173)

### Pattern 4: REST API (Flask)

**Use case:** Microservice for design calculations

```python
# api_server.py
from flask import Flask, request, jsonify
from structural_lib import design_beam_is456

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
from structural_lib import design_beam_is456

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
from structural_lib import design_beam_is456, check_beam_is456

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
from structural_lib.core.data_types import BeamDesignResult, BarArrangement

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
from structural_lib import CostProfile, OptimizationConstraints, optimize_beam_cost

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

    grade = 25
    result = optimize_beam_cost(
        units="IS456",
        span_mm=span_mm,
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        # 25 mm clear cover + 8 mm stirrup + half of a 16 mm main bar
        effective_depth_deduction_mm=25.0 + 8.0 + 16.0 / 2.0,
        fck_nmm2=grade,
        fy_nmm2=500,
        asv_mm2=100.53,
        constraints=OptimizationConstraints(
            min_width_mm=200,
            max_width_mm=500,
            min_depth_mm=300,
            max_depth_mm=800,
            width_step_mm=50,
            depth_step_mm=50,
            min_flexural_utilization=0.7,
        ),
        cost_profile=CostProfile(
            currency="INR",
            concrete_costs={grade: prices[region]["concrete_m3"]},
            steel_cost_per_kg=prices[region]["steel_kg"],
            formwork_cost_per_m2=prices[region]["formwork_m2"],
            congestion_threshold_pt=2.5,
            congestion_multiplier=1.2,
            location_factor=1.0,
        ),
    )

    return result

# Usage
result = optimize_with_regional_pricing(5000, 120, 80, region="Bangalore")
print(
    "Optimal design (Bangalore): "
    f"₹{result.optimal_design.cost_breakdown.total_cost:.0f}"
)
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
from structural_lib import design_beam_is456

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
2. **Medium:** React + FastAPI web app with 3D visualization
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
