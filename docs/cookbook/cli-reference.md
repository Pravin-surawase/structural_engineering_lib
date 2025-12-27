# CLI Reference

Complete command-line reference for `structural_lib`.

## Installation

```bash
pip install structural-lib-is456
# For DXF support:
pip install structural-lib-is456[dxf]
```

## Quick Start

```bash
# Design beams from CSV
python -m structural_lib design input.csv -o results.json

# Generate bar bending schedule
python -m structural_lib bbs results.json -o schedule.csv

# Generate DXF drawings
python -m structural_lib dxf results.json -o drawings.dxf

# Run complete job
python -m structural_lib job job.json -o ./output/
```

---

## Commands

### `design` — Beam Design

Run IS 456 beam design calculations from CSV or JSON input.

```bash
python -m structural_lib design <input> [-o <output>]
```

| Argument | Required | Description |
|----------|----------|-------------|
| `input` | Yes | Input CSV or JSON file with beam parameters |
| `-o, --output` | No | Output JSON file (prints to stdout if omitted) |

**Input CSV format:**

```csv
BeamID,Story,b,D,Span,Cover,fck,fy,Mu,Vu,Ast_req,Asc_req,Stirrup_Dia,Stirrup_Spacing,Status
B1,Story1,300,500,4000,40,25,500,150,100,942.5,0,8,150,OK
B2,Story1,300,450,3000,40,25,500,100,80,628.3,0,8,175,OK
```

| Column | Unit | Description |
|--------|------|-------------|
| `BeamID` | — | Unique beam identifier |
| `Story` | — | Story/level name |
| `b` | mm | Beam width |
| `D` | mm | Overall depth |
| `Span` | mm | Clear span |
| `Cover` | mm | Clear cover |
| `fck` | N/mm² | Concrete grade |
| `fy` | N/mm² | Steel grade |
| `Mu` | kN·m | Factored moment |
| `Vu` | kN | Factored shear |
| `d` | mm | Effective depth (optional; defaults to `D - Cover` if omitted) |
| `Ast_req` | mm² | Required tension steel (used for detailing outputs) |
| `Asc_req` | mm² | Required compression steel (optional; defaults to 0) |
| `Stirrup_Dia` | mm | Stirrup diameter |
| `Stirrup_Spacing` | mm | Stirrup spacing |
| `Status` | — | Optional status field |

Notes:
- `Ast_req` / `Asc_req` are used to generate detailing and BBS outputs. If you want
  detailing to reflect computed design results, provide those values explicitly.
- If `d` is not provided, it is computed as `D - Cover`.

**Examples:**

```bash
# Design from CSV, output to file
python -m structural_lib design examples/sample_beam_design.csv -o results.json

# Design from CSV, print to stdout
python -m structural_lib design beams.csv

# Design from JSON input
python -m structural_lib design beams.json -o results.json
```

**Output JSON structure:**

```json
{
  "schema_version": 1,
  "code": "IS456",
  "units": "IS456",
  "beams": [
    {
      "beam_id": "B1",
      "story": "Story1",
      "geometry": {
        "b_mm": 300,
        "D_mm": 500,
        "d_mm": 450,
        "span_mm": 4000,
        "cover_mm": 40,
        "d_dash_mm": 50
      },
      "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
      "loads": {"case_id": "Story1_B1", "mu_knm": 150, "vu_kn": 100},
      "flexure": {
        "ast_required_mm2": 942.5,
        "asc_required_mm2": 0,
        "xu_mm": 115.2,
        "xu_max_mm": 207.0,
        "mu_lim_knm": 185.5,
        "xu_d_ratio": 0.26,
        "section_type": "UNDER_REINFORCED",
        "is_safe": true,
        "utilization": 0.72,
        "remarks": ""
      },
      "shear": {
        "tau_v_nmm2": 0.74,
        "tau_c_nmm2": 0.62,
        "tau_c_max_nmm2": 2.8,
        "vus_kn": 45.0,
        "sv_required_mm": 150,
        "is_safe": true,
        "utilization": 0.65,
        "remarks": ""
      },
      "serviceability": {
        "deflection_ok": true,
        "deflection_remarks": "",
        "deflection_utilization": 0.6,
        "crack_width_ok": true,
        "crack_width_remarks": "",
        "crack_width_utilization": 0.7
      },
      "detailing": {
        "bottom_bars": [{"count": 3, "diameter": 16, "callout": "3-16φ"}],
        "top_bars": [{"count": 2, "diameter": 12, "callout": "2-12φ"}],
        "stirrups": [{"diameter": 8, "spacing": 150, "callout": "2L-8φ@150"}],
        "ld_tension_mm": 752,
        "lap_length_mm": 564
      },
      "is_ok": true,
      "governing_utilization": 0.72,
      "governing_check": "flexure",
      "remarks": ""
    }
  ],
  "summary": {"total_beams": 1, "passed": 1, "failed": 0}
}
```

`section_type` values: UNDER_REINFORCED, BALANCED, OVER_REINFORCED.

---

### `bbs` — Bar Bending Schedule

Generate bar bending schedule from design results.

```bash
python -m structural_lib bbs <input> [-o <output>]
```

| Argument | Required | Description |
|----------|----------|-------------|
| `input` | Yes | Design results JSON (output from `design` command) |
| `-o, --output` | No | Output CSV or JSON file (prints CSV to stdout if omitted) |

**Examples:**

```bash
# Generate CSV schedule
python -m structural_lib bbs results.json -o bbs.csv

# Generate JSON schedule
python -m structural_lib bbs results.json -o bbs.json

# Print to stdout
python -m structural_lib bbs results.json
```

**Output CSV columns:**

| Column | Description |
|--------|-------------|
| `bar_mark` | Unique bar identifier (e.g., A1, B2) |
| `member_id` | Beam identifier |
| `location` | Position in member (top, bottom, stirrup) |
| `zone` | Span zone (start, mid, end) |
| `shape_code` | IS 2502 / SP 34 shape code |
| `diameter_mm` | Bar diameter |
| `no_of_bars` | Number of bars |
| `cut_length_mm` | Cutting length per bar |
| `total_length_mm` | Total length (count × cut length) |
| `unit_weight_kg` | Weight per bar |
| `total_weight_kg` | Total weight |
| `remarks` | Additional notes |

---

### `dxf` — DXF Drawings

Generate DXF reinforcement drawings from design results.

> **Note:** Requires `ezdxf` library. Install with: `pip install ezdxf`

```bash
python -m structural_lib dxf <input> -o <output>
```

| Argument | Required | Description |
|----------|----------|-------------|
| `input` | Yes | Design results JSON |
| `-o, --output` | **Yes** | Output DXF file path |

**Examples:**

```bash
# Single beam drawing
python -m structural_lib dxf results.json -o beam_detail.dxf

# Multiple beams (auto-layout in grid)
python -m structural_lib dxf all_beams.json -o drawings.dxf
```

**Output features:**

- Cross-section view with bars
- Longitudinal elevation with stirrups
- Bar callouts and dimensions
- Multi-beam grid layout (when multiple beams)
- DXF R2010 format (AC1024, compatible with most CAD software)

---

### `job` — Complete Job

Run a complete job from JSON specification including design, BBS, and optional DXF.

```bash
python -m structural_lib job <input> -o <output_dir>
```

| Argument | Required | Description |
|----------|----------|-------------|
| `input` | Yes | Job specification JSON file |
| `-o, --output` | **Yes** | Output directory for all results |

**Job JSON format:**

```json
{
  "schema_version": 1,
  "job_id": "project_001",
  "code": "IS456",
  "units": "IS456",
  "beam": {
    "b_mm": 300.0,
    "D_mm": 500.0,
    "d_mm": 450.0,
    "d_dash_mm": 50.0,
    "fck_nmm2": 25.0,
    "fy_nmm2": 500.0,
    "asv_mm2": 100.0
  },
  "cases": [
    {"case_id": "DL+LL", "mu_knm": 80.0, "vu_kn": 60.0},
    {"case_id": "1.5(DL+LL)", "mu_knm": 120.0, "vu_kn": 90.0},
    {"case_id": "EQ-X", "mu_knm": 160.0, "vu_kn": 120.0}
  ]
}
```

| Field | Unit | Description |
|-------|------|-------------|
| `job_id` | — | Unique job identifier |
| `code` | — | Design code (`IS456`) |
| `beam.b_mm` | mm | Beam width |
| `beam.D_mm` | mm | Overall depth |
| `beam.d_mm` | mm | Effective depth |
| `beam.d_dash_mm` | mm | Compression cover |
| `beam.fck_nmm2` | N/mm² | Concrete grade |
| `beam.fy_nmm2` | N/mm² | Steel grade |
| `beam.asv_mm2` | mm² | Stirrup leg area (2-legged) |
| `cases[].case_id` | — | Load case name |
| `cases[].mu_knm` | kN·m | Factored moment |
| `cases[].vu_kn` | kN | Factored shear |

**Examples:**

```bash
# Run job with all outputs
python -m structural_lib job examples/sample_job_is456.json -o output/

# Results in output/:
#   - inputs/job.json
#   - parsed/beam.json
#   - parsed/cases.json
#   - design/design_results.json
#   - design/compliance_summary.csv
```

**Output directory contents:**

| File | Description |
|------|-------------|
| `design/design_results.json` | Complete design results with all cases |
| `design/compliance_summary.csv` | Tabular summary for spreadsheet import |

---

## Workflow Examples

### Example 1: Full Design Pipeline

```bash
# Step 1: Design beams from CSV
python -m structural_lib design project_beams.csv -o design_results.json

# Step 2: Generate bar bending schedule
python -m structural_lib bbs design_results.json -o bbs.csv

# Step 3: Generate DXF drawings
python -m structural_lib dxf design_results.json -o drawings.dxf
```

### Example 2: Quick Single-Beam Check

```bash
# Create minimal CSV
echo "BeamID,Story,b,D,Span,Cover,fck,fy,Mu,Vu,Ast_req,Asc_req,Stirrup_Dia,Stirrup_Spacing,Status
B1,GF,300,500,5000,40,25,500,180,100,0,0,8,150,OK" > beam.csv

# Run design and view output
python -m structural_lib design beam.csv
```

### Example 3: Batch Processing

```bash
# Process multiple projects
for project in project_a project_b project_c; do
  python -m structural_lib design ${project}/beams.csv -o ${project}/results.json
  python -m structural_lib bbs ${project}/results.json -o ${project}/bbs.csv
done
```

---

## Help

Get help for any command:

```bash
# Main help
python -m structural_lib --help

# Command-specific help
python -m structural_lib design --help
python -m structural_lib bbs --help
python -m structural_lib dxf --help
python -m structural_lib job --help
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (file not found, invalid input, calculation failure) |

---

## Related

- [Python Quickstart](../getting-started/python-quickstart.md) — Getting started with Python API
- [API Reference](../reference/api.md) — Programmatic API documentation
- [Job Schema](../specs/v0.9_JOB_SCHEMA.md) — Full job specification schema
