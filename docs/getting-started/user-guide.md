# User Guide — Complete Workflow

**Version:** 0.14.0
**Time to complete:** 10–15 minutes

This guide walks you through a complete beam design workflow from start to finish. For detailed installation help, see [Beginner's Guide](beginners-guide.md).

---

## Prerequisites

```bash
pip install structural-lib-is456
```

---

## 1. Design a Single Beam (Command Line)

The fastest way to design a beam is via the CLI:

```bash
# Create input file
echo '{"beams": [{"id": "B1", "b": 300, "D": 500, "d": 450, "Mu_mid": 150, "Vu_max": 100, "fck": 25, "fy": 500}], "units": "IS456"}' > beam.json

# Run design
python -m structural_lib design beam.json -o results.json
```

**Output (`results.json`):**
```json
{
  "schema_version": 1,
  "units": {"length": "mm", "force": "kN", "moment": "kN.m", "stress": "N/mm2"},
  "beams": [{
    "id": "B1",
    "flexure": {"ast_required": 942.3, "mu_lim": 196.54, "is_safe": true},
    "shear": {"spacing": 175, "is_safe": true}
  }]
}
```

---

## 2. Batch Process Multiple Beams

Create a CSV file with your beam data:

```csv
id,b,D,d,Mu_mid,Vu_max,fck,fy
B1,300,500,450,150,100,25,500
B2,230,450,400,80,75,20,415
B3,350,600,550,250,150,30,500
```

Run:
```bash
python -m structural_lib design beams.csv -o results.json
```

---

## 3. Generate Bar Bending Schedule (BBS)

After design, generate the BBS:

```bash
python -m structural_lib bbs results.json -o schedule.csv
```

**Output columns:** Mark, Type, Diameter, Length, Quantity, Weight

---

## 4. Generate DXF Drawings

Create CAD-ready drawings (requires `pip install ezdxf`):

```bash
python -m structural_lib dxf results.json -o drawings.dxf
```

Opens in AutoCAD, LibreCAD, or any DXF viewer.

---

## 5. Complete Job Workflow

For complex projects, use a job file that combines everything:

**job.json:**
```json
{
  "project": "My Building",
  "units": "IS456",
  "beams": [
    {"id": "B1", "b": 300, "D": 500, "d": 450, "Mu_mid": 150, "Vu_max": 100, "fck": 25, "fy": 500},
    {"id": "B2", "b": 230, "D": 450, "d": 400, "Mu_mid": 80, "Vu_max": 75, "fck": 20, "fy": 415}
  ],
  "output": {
    "design": true,
    "bbs": true,
    "dxf": true
  }
}
```

Run:
```bash
python -m structural_lib job job.json -o ./output/
```

Creates:
- `output/design_results.json`
- `output/bbs_schedule.csv`
- `output/drawings.dxf`

---

## 6. Python API (for scripting)

For integration into your own scripts:

```python
from structural_lib import api

# Single beam design
result = api.design_beam_is456(
    b=300, d=450, D=500,
    Mu_knm=150, Vu_kn=100,
    fck=25, fy=500,
    units="IS456"
)

print(f"Ast required: {result.flexure.ast_required:.0f} mm²")
print(f"Stirrup spacing: {result.shear.spacing:.0f} mm")
print(f"Safe: {result.is_compliant}")
```

---

## 7. Interpreting Results

### Flexure Results

| Field | Meaning | Action if Issue |
|-------|---------|-----------------|
| `is_safe=True` | Section is adequate | Proceed |
| `is_safe=False` | Section inadequate | Increase b or D |
| `section_type="under_reinforced"` | Good (ductile) | Ideal |
| `section_type="over_reinforced"` | Bad (brittle) | Add compression steel |

### Shear Results

| Field | Meaning | Action if Issue |
|-------|---------|-----------------|
| `is_safe=True` | τv ≤ τc,max | Proceed |
| `is_safe=False` | τv > τc,max | Increase section |
| `spacing` | Required stirrup spacing | Use standard pitch ≤ spacing |

### Common Warnings

| Warning | Cause | Fix |
|---------|-------|-----|
| `"Minimum steel governs"` | Mu is very low | Normal, use minimum |
| `"Over-reinforced section"` | Mu > Mu,lim | Add Asc or increase section |
| `"τv exceeds τc,max"` | Shear too high | Increase b or d |

---

## 8. Units Reference

The library uses IS 456 standard units:

| Quantity | Unit |
|----------|------|
| Dimensions (b, D, d) | mm |
| Moment (Mu) | kN·m |
| Shear (Vu) | kN |
| Stress (fck, fy) | N/mm² |
| Area (Ast, Asc) | mm² |

---

## 9. Getting Help

```bash
# CLI help
python -m structural_lib --help
python -m structural_lib design --help

# Run tests to verify installation
cd Python && python -m pytest -q
```

**Resources:**
- [API Reference](../reference/api.md)
- [Verification Examples](../verification/examples.md)
- [Troubleshooting](../reference/troubleshooting.md)

---

## Next Steps

1. **Validate your workflow** — Run the [verification examples](../verification/examples.md) to confirm library accuracy
2. **Try Excel integration** — See [Excel Quickstart](excel-quickstart.md) for spreadsheet workflows
3. **Explore advanced features** — See [Python Recipes](../cookbook/python-recipes.md) for complex scenarios
