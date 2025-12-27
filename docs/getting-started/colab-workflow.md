# Colab Workflow (End-to-End, No ETABS Needed)

This guide runs the full pipeline in Google Colab:
install -> generate inputs -> design -> BBS -> DXF -> batch testing.

---

## Step 0: Start fresh
In Colab: Runtime -> Restart runtime, then run the cells below in order.

---

## Step 1: Install the package
```python
!pip -q install "structural-lib-is456[dxf]"
```

---

## Step 2: Quick sanity check (no files)
```python
from structural_lib import flexure

res = flexure.design_singly_reinforced(
    b=300, d=450, d_total=500, mu_knm=150, fck=25, fy=500
)
print("Ast required (mm^2):", round(res.ast_required))
print("Status:", "OK" if res.is_safe else res.error_message)
```

---

## Step 3: Full workflow on a small sample (includes DXF)
Create a small CSV (5 beams), then run the full CLI:

```python
import csv
import math
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

print("Wrote beams_small.csv")
```

Run the full pipeline:
```python
!python -m structural_lib design beams_small.csv -o results_small.json --deflection
!python -m structural_lib bbs results_small.json -o schedule_small.csv
!python -m structural_lib dxf results_small.json -o drawings_small.dxf
```

Optional crack width (requires explicit inputs):
```python
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

## Step 4: Batch test (500 beams)
Generate a big dataset and run design + BBS:

```python
import csv
import math
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

print("Wrote beams_500.csv")
```

Run the batch:
```python
!python -m structural_lib design beams_500.csv -o results_500.json --deflection --summary
!python -m structural_lib bbs results_500.json -o schedule_500.csv
```

Optional (DXF for 500 beams can be heavy):
```python
!python -m structural_lib dxf results_500.json -o drawings_500.dxf
```

---

## Step 5: Sanity checks (optional)
```python
import json

with open("results_500.json") as f:
    data = json.load(f)

beams = data.get("beams", [])
summary = data.get("summary", {})

print("Beams:", len(beams))
print("Summary:", summary)
print("First beam serviceability:", beams[0].get("serviceability"))
```

---

## Step 6: Job runner (JSON spec, optional)
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
        "fck_nmm2": 25,
        "fy_nmm2": 500
    },
    "cases": [
        {"case_id": "C1", "mu_knm": 120, "vu_kn": 90}
    ]
}

with open("job.json", "w") as f:
    json.dump(job, f, indent=2)

!python -m structural_lib job job.json -o ./job_out
```

---

## Step 7: Download outputs (optional)
```python
import shutil

shutil.make_archive("colab_outputs", "zip", ".")
print("Created colab_outputs.zip")
```

Then in the file browser (left sidebar), download `colab_outputs.zip`.
