# Colab Workflow (End-to-End, No ETABS Needed)

> **Version:** v0.10.7 | **Updated:** 2025-12-29

This guide runs the full pipeline in Google Colab:
install → generate inputs → design → BBS → DXF → reports → critical set.

**All CLI commands covered:**
- `design` — Run beam design from CSV
- `bbs` — Generate bar bending schedule
- `dxf` — Generate CAD drawings
- `job` — Run full job from JSON spec
- `report` — Generate HTML/JSON reports *(NEW in v0.10.7)*
- `critical` — Export critical set sorted by utilization *(NEW in v0.10.7)*

---

## 🆕 What's New in v0.10.7 (Visual v0.11)

**V01–V07 features delivered:**

| Feature | CLI Command | Description |
|---------|-------------|-------------|
| **V01** | — | `report.py` skeleton + `load_job_spec()` helper |
| **V02** | `report` | Report CLI subcommand (JSON/HTML output) |
| **V03** | `critical` | Critical set export (sorted utilization table) |
| **V04** | `report --format=html` | Cross-section SVG rendering |
| **V05** | `report --format=html` | Input sanity heatmap |
| **V06** | `report --format=html` | Stability scorecard |
| **V07** | `report --format=html` | Units sentinel |

**Quick demo of new features:**
```python
# After running job (Step 6), generate reports:
!python -m structural_lib critical ./job_out --top=5 --format=csv
!python -m structural_lib report ./job_out --format=html -o report.html
```

---

## Step 0: Start Fresh

In Colab: **Runtime → Restart runtime**, then run the cells below in order.

---

## Step 1: Install the Package

```python
!pip -q install "structural-lib-is456[dxf]"
```

Verify installation:
```python
from structural_lib import api
print("Version:", api.get_library_version())
```

---

## Step 2: Quick Sanity Check (No Files)

```python
from structural_lib import flexure

res = flexure.design_singly_reinforced(
    b=300, d=450, d_total=500, mu_knm=150, fck=25, fy=500
)
print("Ast required (mm²):", round(res.ast_required))
print("Status:", "OK" if res.is_safe else res.error_message)
```

Expected output:
```
Ast required (mm²): 942
Status: OK
```

---

## Step 3: Full Pipeline (Small Sample)

### 3a: Generate sample CSV (5 beams)

```python
import csv
import random
from structural_lib import flexure, tables

random.seed(7)

def make_row(i):
    b = random.choice([230, 250, 300])
    D = random.choice([450, 500, 550])
    span = random.choice([3000, 3500, 4000, 4500])
    cover = random.choice([30, 40])
    fck = random.choice([20, 25, 30])
    fy = random.choice([415, 500])
    stirrup_dia = 8
    stirrup_spacing = 150

    d = D - cover - stirrup_dia - 8
    probe = flexure.design_singly_reinforced(b=b, d=d, d_total=D, mu_knm=1, fck=fck, fy=fy)
    mu = 0.55 * probe.mu_lim

    tc_max = tables.get_tc_max_value(fck)
    vu_cap = 0.6 * tc_max * b * d / 1000.0
    vu = min(4.0 * mu / (span / 1000.0), vu_cap)

    return {
        "BeamID": f"B{i+1}",
        "Story": "G",
        "b": b,
        "D": D,
        "Span": span,
        "Cover": cover,
        "fck": fck,
        "fy": fy,
        "Mu": round(mu, 2),
        "Vu": round(vu, 2),
        "Ast_req": 0,
        "Asc_req": 0,
        "Stirrup_Dia": stirrup_dia,
        "Stirrup_Spacing": stirrup_spacing,
    }

rows = [make_row(i) for i in range(5)]
with open("beams_small.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

print("✓ Wrote beams_small.csv")
```

### 3b: Run design → BBS → DXF

```python
# Design beams
!python -m structural_lib design beams_small.csv -o results_small.json

# Generate bar bending schedule
!python -m structural_lib bbs results_small.json -o schedule_small.csv

# Generate DXF drawings
!python -m structural_lib dxf results_small.json -o drawings_small.dxf
```

### 3c: Optional flags

```python
# With deflection checks + title block
!python -m structural_lib design beams_small.csv -o results_small.json --deflection
!python -m structural_lib dxf results_small.json -o drawings_small.dxf --title-block --title "Beam Sheet"
```

```python
# With crack width parameters (requires explicit JSON)
import json

crack_params = {
    "acr_mm": 120.0,
    "cmin_mm": 25.0,
    "h_mm": 500.0,
    "x_mm": 200.0,
    "epsilon_m": 0.001
}
with open("crack_width_params.json", "w") as f:
    json.dump(crack_params, f, indent=2)

!python -m structural_lib design beams_small.csv -o results_small.json \
  --deflection --crack-width-params crack_width_params.json
```

---

## Step 4: Batch Test (500 Beams)

### 4a: Generate batch CSV

```python
import csv
import random
from structural_lib import flexure, tables

random.seed(42)

def make_row(i):
    b = random.choice([230, 250, 300, 350])
    D = random.choice([450, 500, 550, 600])
    span = random.choice([3000, 3500, 4000, 4500, 5000])
    cover = random.choice([30, 40, 50])
    fck = random.choice([20, 25, 30, 35])
    fy = random.choice([415, 500])
    stirrup_dia = random.choice([8, 10])
    stirrup_spacing = random.choice([125, 150, 175])

    d = D - cover - stirrup_dia - 8
    probe = flexure.design_singly_reinforced(b=b, d=d, d_total=D, mu_knm=1, fck=fck, fy=fy)
    mu = 0.6 * probe.mu_lim

    tc_max = tables.get_tc_max_value(fck)
    vu_cap = 0.6 * tc_max * b * d / 1000.0
    vu = min(4.0 * mu / (span / 1000.0), vu_cap)

    return {
        "BeamID": f"B{i+1:04d}",
        "Story": "G",
        "b": b,
        "D": D,
        "Span": span,
        "Cover": cover,
        "fck": fck,
        "fy": fy,
        "Mu": round(mu, 2),
        "Vu": round(vu, 2),
        "Ast_req": 0,
        "Asc_req": 0,
        "Stirrup_Dia": stirrup_dia,
        "Stirrup_Spacing": stirrup_spacing,
    }

rows = [make_row(i) for i in range(500)]
with open("beams_500.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

print("✓ Wrote beams_500.csv (500 beams)")
```

### 4b: Run batch design

```python
# Basic design + BBS
!python -m structural_lib design beams_500.csv -o results_500.json
!python -m structural_lib bbs results_500.json -o schedule_500.csv
```

```python
# With deflection + summary CSV
!python -m structural_lib design beams_500.csv -o results_500.json --deflection --summary
```

```python
# DXF for batch (can be slow for 500 beams)
!python -m structural_lib dxf results_500.json -o drawings_500.dxf --title-block --title "Batch Sheet"
```

---

## Step 5: Inspect Results

```python
import json

with open("results_500.json") as f:
    data = json.load(f)

beams = data.get("beams", [])
summary = data.get("summary", {})

print("Beams processed:", len(beams))
print("Summary:", summary)
print("First beam serviceability:", beams[0].get("serviceability"))
```

---

## Step 6: Job Runner (JSON Spec)

For multi-case compliance checks, use the job runner:

```python
import json

job = {
    "schema_version": 1,
    "code": "IS456",
    "units": "IS456",
    "job_id": "colab_job_001",
    "beam": {
        "b_mm": 230,
        "D_mm": 500,
        "d_mm": 450,
        "d_dash_mm": 50,
        "fck_nmm2": 25,
        "fy_nmm2": 500,
        "asv_mm2": 100
    },
    "cases": [
        {"case_id": "LC1", "mu_knm": 100, "vu_kn": 70},
        {"case_id": "LC2", "mu_knm": 150, "vu_kn": 90},
        {"case_id": "LC3", "mu_knm": 180, "vu_kn": 110}
    ]
}

with open("job.json", "w") as f:
    json.dump(job, f, indent=2)

!python -m structural_lib job job.json -o ./job_out

print("✓ Job completed. Outputs in ./job_out/")
```

---

## Step 7: 🆕 Critical Set Export (V03)

Sort load cases by utilization to find critical beams:

```python
# Export as CSV (to stdout)
!python -m structural_lib critical ./job_out --format=csv

# Export top 5 to file
!python -m structural_lib critical ./job_out --top=5 --format=csv -o critical.csv

# Export as HTML table with utilization bars
!python -m structural_lib critical ./job_out --format=html -o critical.html
```

View the CSV:
```python
import pandas as pd
pd.read_csv("critical.csv")
```

---

## Step 8: 🆕 Report Generation (V04–V06)

Generate full reports with SVG, sanity heatmap, and scorecard:

```python
# JSON report (machine-readable)
!python -m structural_lib report ./job_out --format=json -o report.json

# HTML report (human-readable with visuals)
!python -m structural_lib report ./job_out --format=html -o report.html
```

View the HTML report inline:
```python
from IPython.display import HTML, display

with open("report.html", "r", encoding="utf-8") as f:
    display(HTML(f.read()))
```

**What's in the HTML report:**
- Job summary (ID, code, status)
- Cross-section SVG (beam geometry visualization)
- Input sanity heatmap (geometry/material validation)
- Stability scorecard (ductility, shear margin, utilization)
- Units sentinel (magnitude-based unit checks)

---

## Step 9: Download All Outputs

```python
import shutil
import os

# List generated files
for f in os.listdir("."):
    if f.endswith((".csv", ".json", ".dxf", ".html")):
        print(f"  {f}")

# Create zip archive
shutil.make_archive("colab_outputs", "zip", ".")
print("\n✓ Created colab_outputs.zip — download from file browser (left sidebar)")
```

---

## CLI Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `design` | Run beam design from CSV | `design input.csv -o results.json` |
| `bbs` | Generate bar bending schedule | `bbs results.json -o schedule.csv` |
| `dxf` | Generate DXF drawings | `dxf results.json -o drawings.dxf` |
| `job` | Run job from JSON spec | `job job.json -o ./output/` |
| `report` | Generate report (JSON/HTML) | `report ./output/ --format=html` |
| `critical` | Export critical set | `critical ./output/ --top=10 --format=csv` |

For help on any command:
```python
!python -m structural_lib --help
!python -m structural_lib design --help
!python -m structural_lib critical --help
!python -m structural_lib report --help
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Restart runtime after install |
| `No DXF output` | Install with `[dxf]` extra |
| `FileNotFoundError` | Check file paths, run cells in order |
| `KeyError in results` | Ensure design ran successfully first |

---

*Last updated: 2025-12-29 | v0.10.7*
