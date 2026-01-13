# ETABS Integration Guide

**Task:** TASK-044
**Status:** Complete
**Date:** 2025-12-26

---

## 1. Overview

This document provides a complete mapping from ETABS beam force exports to the `structural_engineering_lib` design workflow. The integration is **CSV-first** (no COM/API dependencies), making it portable across Windows, Mac, and Linux.

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│                         ETABS → structural_engineering_lib WORKFLOW                │
├────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌─────────────────┐  │
│  │    ETABS     │───▶│  CSV Export  │───▶│  Normalize   │───▶│  Compliance     │  │
│  │   Analysis   │    │ (Beam Forces)│    │  + job.json  │    │  Check / BBS    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘    └─────────────────┘  │
│                                                                                    │
│  Model + Loads       "Show Tables / Export" Python/Excel      Deterministic         │
│  → Run Analysis      → Select tables      integration        JSON + CSV outputs    │
│                                                                                    │
└────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Supported ETABS Export Tables

### 2.1 Primary Table: Beam Forces (Required)

**ETABS Menu Path (typical):** `Display -> Show Tables` (also available via `Model Explorer -> Tables`)

Or via **Export (typical):**
1. Go to `File -> Export -> ETABS Tables to Excel` (save as CSV)
2. Select: `Analysis Results -> Frame Results -> Element Forces - Beams` (label varies by version)
3. Export as CSV

**Typical table labels (version-dependent):**
- `Frame Results - Element Forces - Beams`
- `Frame Results - Beam Forces`
- `Beam Forces` (short list names)

**Expected Columns:**

| ETABS Column | Description | Unit (Typical) | Library Mapping |
|--------------|-------------|----------------|-----------------|
| `Story` | Floor/level name | — | `story` |
| `Label` | Beam label (B1, B2, etc.) | — | `beam_id` |
| `Unique Name` | Internal ETABS ID | — | (optional) |
| `Output Case` / `Load Case/Combo` | Load combination name | — | `case_id` |
| `Station` | Location along beam (output station) | mm or m | `station` (optional) |
| `P` | Axial force | kN | (usually 0 for beams) |
| `V2` | Shear in the 1-2 plane (local 2) | kN | `vu_kn` |
| `M3` | Bending in the 1-2 plane (about local 3) | kN·m | `mu_knm` |

**Sign Convention:**
- ETABS reports `M3` and `V2` using the member local axes and the i/j end. Sign depends on local 2/3 orientation.
- For strength envelopes in this workflow we use `abs(M3)` and `abs(V2)`. For top/bottom steel, map signs using local axes and beam "up" direction.
- Before assuming "vertical bending = M3", confirm the beam local 2 axis is vertical in your model (local axes can be reassigned).

**Extra Columns:**
- ETABS force tables often include additional fields (e.g., Case Type, Step, or Envelope). Ignore unknown columns in the normalizer.

### 2.2 Geometry Table: Frame Sections (Optional but Recommended)

**ETABS Menu Path:** `Define -> Section Properties -> Frame Sections`

Export for beam dimensions:

| ETABS Column | Description | Library Mapping |
|--------------|-------------|-----------------|
| `Name` | Section property name | join key for assignments |
| `Material` | Concrete grade | → `fck` lookup |
| `Depth` | Overall depth (D) | `D_mm` |
| `Width` | Beam width (b) | `b_mm` |

### 2.3 Frame Section Assignments (Recommended)

**ETABS Menu Path (typical):** `Display -> Show Tables`

Export to map each frame object to its assigned section property:

| ETABS Column | Description | Library Mapping |
|--------------|-------------|-----------------|
| `Story` | Floor/level name | `story` |
| `Label` | Frame label (B1, B2, etc.) | `beam_id` |
| `Unique Name` | Internal ETABS ID | (optional) |
| `Section` | Section property name | join to Frame Sections |

**Typical table labels (version-dependent):**
- `Frame Assignments - Section Properties`
- `Frame Section Assignments`
ETABS exports commonly include `Frame Assignments - Section Properties` in this family.

### 2.4 Material Table: Concrete Properties

**ETABS Menu Path:** `Define -> Materials`
**Typical table labels (version-dependent):**
- `Material Properties - Concrete Data`

| ETABS Column | Description | Library Mapping |
|--------------|-------------|-----------------|
| `Name` | Material name | "M25", "M30", etc. |
| `Fc` | Characteristic strength | `fck_nmm2` |

### 2.5 Material Table: Rebar Properties

**ETABS Menu Path:** `Define -> Materials`
**Typical table labels (version-dependent):**
- `Material Properties - Rebar Data`

| ETABS Column | Description | Library Mapping |
|--------------|-------------|-----------------|
| `Name` | Rebar material name | "Fe415", "Fe500", etc. |
| `Fy` | Rebar yield strength | `fy_nmm2` |

---

## 3. ETABS Column → Job Schema Mapping

### 3.1 Force Mapping (Critical)

Transform ETABS output to library input:

| ETABS | Transform | Job Schema (v1) | Notes |
|-------|-----------|-----------------|-------|
| `M3` (kN·m) | `abs(M3)` | `mu_knm` | Use envelope max |
| `V2` (kN) | `abs(V2)` | `vu_kn` | Use envelope max |
| `Label` | direct | `beam_id` | Use `Unique Name` if you need a stable ID |
| `Output Case` / `Load Case/Combo` | direct | `cases[].case_id` | e.g., "1.5(DL+LL)" |
| `Station` | optional | `station` (if preserved) | Use when keeping left/mid/right points |

### 3.2 Geometry Mapping

| Source | Job Schema Field | Unit | Default |
|--------|------------------|------|---------|
| Frame Section depth | `beam.D_mm` | mm | Join via section assignments |
| Frame Section width | `beam.b_mm` | mm | Join via section assignments |
| `D_mm - cover - stirrup_dia - bar_dia/2` | `beam.d_mm` | mm | Calculate |
| User input / assumption | `beam.d_dash_mm` | mm | 50 |

### 3.3 Material Mapping

Concrete grades (from **Material Properties - Concrete Data**):

| ETABS Material | `fck_nmm2` | Notes |
|----------------|------------|-------|
| M20 | 20 | Default fy = Fe500 if rebar table not provided |
| M25 | 25 | Most common |
| M30 | 30 | |
| M35 | 35 | |
| M40 | 40 | |

Rebar grades (from **Material Properties - Rebar Data**):

| ETABS Material | `fy_nmm2` | Notes |
|----------------|-----------|-------|
| Fe415 | 415 | |
| Fe500 | 500 | Most common |

If the rebar table is not exported, `fy_nmm2` may come from ETABS default/design preferences.

---

## 4. Step-by-Step Workflow

### 4.1 Export from ETABS

1. **Run Analysis** in ETABS (ensure combinations are defined)
2. Open tables via `Display -> Show Tables` (or `Model Explorer -> Tables`)
3. Export via `File -> Export -> ETABS Tables to Excel` (save as CSV)
4. Select the following tables (labels vary by version):
   - ✅ `Element Forces - Beams` (required)
   - ✅ `Frame Section Definitions` (recommended)
   - ✅ `Frame Assignments - Section Properties` (recommended)
   - ✅ `Material Properties - Concrete Data` (recommended)
   - ✅ `Material Properties - Rebar Data` (recommended if you need fy)
5. Save to your working folder

### 4.2 Prepare Input CSV

Create `beams_input.csv` with the following columns:

```csv
BeamID,Story,b,D,d,Span,Cover,fck,fy,Mu,Vu,Ast_req,Asc_req,Stirrup_Dia,Stirrup_Spacing,Status
B1,Story1,300,500,450,4000,40,25,500,150,100,942,0,8,150,OK
B2,Story1,300,450,400,3000,40,25,500,100,80,628,0,8,175,OK
```

**Mapping from ETABS:**
- `Mu` = max |M3| along the beam for the governing combination
- `Vu` = max |V2| along the beam for the governing combination
- `Ast_req` / `Asc_req` = from design calculations (or run through library first)

### 4.3 Create Job JSON (for Batch Runner)

```json
{
  "schema_version": 1,
  "job_id": "ETABS_project_001_B1",
  "code": "IS456",
  "units": "IS456",
  "beam": {
    "b_mm": 300.0,
    "D_mm": 500.0,
    "d_mm": 450.0,
    "d_dash_mm": 50.0,
    "fck_nmm2": 25.0,
    "fy_nmm2": 500.0,
    "asv_mm2": 100.0,
    "pt_percent": null
  },
  "cases": [
    {"case_id": "1.5(DL+LL)_left", "mu_knm": 50.0, "vu_kn": 100.0},
    {"case_id": "1.5(DL+LL)_mid", "mu_knm": 150.0, "vu_kn": 0.0},
    {"case_id": "1.5(DL+LL)_right", "mu_knm": 50.0, "vu_kn": 100.0}
  ]
}
```

### 4.4 Run Compliance Check

**Python CLI:**
```bash
python -m structural_lib.job_cli run --job job.json --out ./output/B1
```

**Python Script:**
```python
from structural_lib.job_runner import load_job_json, run_job_is456

job = load_job_json("job.json")
result = run_job_is456(job=job, out_dir="./output/B1")
print(result)
```

---

## 5. ETABS CSV Normalization (Python Helper)

Use this helper to convert raw ETABS exports to the library's expected format:

```python
import csv
from pathlib import Path

def normalize_etabs_forces(
    etabs_csv_path: str,
    output_path: str = None
) -> list[dict]:
    """
    Normalize ETABS beam forces export to library format.

    Extracts envelope (max abs) for each beam and combination.
    """
    rows = []
    with open(etabs_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                'story': row.get('Story', ''),
                'beam_id': row.get('Label', ''),
                'case_id': row.get('Output Case')
                    or row.get('Load Case/Combo')
                    or row.get('Load Case', ''),
                'station': float(row.get('Station', 0)),
                'm3': float(row.get('M3', 0)),
                'v2': float(row.get('V2', 0)),
            })

    # Group by (story, beam_id, case_id) and find envelope
    from collections import defaultdict
    grouped = defaultdict(list)
    for r in rows:
        key = (r['story'], r['beam_id'], r['case_id'])
        grouped[key].append(r)

    envelope = []
    for (story, beam_id, case_id), stations in grouped.items():
        max_mu = max(abs(s['m3']) for s in stations)
        max_vu = max(abs(s['v2']) for s in stations)
        envelope.append({
            'story': story,
            'beam_id': beam_id,
            'case_id': case_id,
            'mu_knm': max_mu,
            'vu_kn': max_vu,
        })

    if output_path:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['story', 'beam_id', 'case_id', 'mu_knm', 'vu_kn'])
            writer.writeheader()
            writer.writerows(envelope)

    return envelope

# Usage:
# envelope = normalize_etabs_forces("ETABS_Sample_Export.csv", "normalized_forces.csv")
```

---

## 6. Sample Files Reference

The repository includes sample ETABS exports for testing:

| File | Description |
|------|-------------|
| `Python/examples/ETABS_Sample_Export.csv` | Raw ETABS beam forces export |
| `Python/examples/ETABS_BeamForces_Example.csv` | Alternative format with reordered columns |
| `Python/examples/sample_job_is456.json` | Job schema example |

---

## 7. Common Issues & Solutions

### 7.1 Unit Mismatches

| Issue | Solution |
|-------|----------|
| ETABS exports in meters | Convert Station × 1000 to mm |
| Moments in kN·mm | Divide by 1000 to get kN·m |
| ETABS uses kip/ft (US) | Switch ETABS to kN/m system before export |

### 7.2 Sign Convention Confusion

| Symptom | Cause | Fix |
|---------|-------|-----|
| Negative moments treated as positive | Local axes / i-j orientation not accounted for | Use local axes to interpret sign; use `abs(M3)` for envelope |
| Design seems under-designed | Using wrong governing case | Check all combinations |

### 7.3 Multiple Load Combinations

The library expects **factored** design forces. If ETABS exports multiple combos:

1. **Option A (Recommended):** Use envelope max across all combos
2. **Option B:** Run separate jobs per combo and compare results

---

## 8. Future Enhancements

- [ ] Add Python script to auto-generate `job.json` from ETABS CSV
- [ ] Support for ETABS API direct connection (Windows only)
- [ ] Multi-beam batch processing with single input CSV
- [ ] SAFE integration (slab and beam strips)

---

## 9. References

- ETABS User Manual: Table Export Formats
- [docs/specs/v0.9-job-schema.md](../../specs/v0.9-job-schema.md) — Job schema specification
- [docs/specs/v0.7-data-mapping.md](../../specs/v0.7-data-mapping.md) — Detailing data mapping
- [docs/getting-started/python-quickstart.md](../../getting-started/python-quickstart.md) — Python quickstart
