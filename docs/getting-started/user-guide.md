---
owner: Main Agent
status: active
last_updated: 2026-03-30
doc_type: guide
complexity: intermediate
tags: []
---

# User Guide — Complete Workflow

**Type:** Guide
**Audience:** Users
**Status:** Approved
**Importance:** High
**Version:** 0.24.0a1
**Created:** 2025-12-15
**Last Updated:** 2026-03-29

---

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
echo '{"schema_version":"cli-beam-design-input/v1","beams":[{"beam_id":"B1","story":"Ground","b":300,"D":500,"d":450,"span":4000,"cover":40,"fck":25,"fy":500,"Mu":150,"Vu":100,"stirrup_dia":8,"stirrup_spacing":150}]}' > beam.json

# Run design
python -m structural_lib design beam.json -o results.json
```

**Output (`results.json`):**
```json
{
  "schema_version": 1,
  "code": "IS456",
  "units": "IS456",
  "beams": [{
    "beam_id": "B1",
    "story": "Ground",
    "flexure": {"ast_required_mm2": 942.3, "is_safe": true},
    "shear": {"sv_required_mm": 175, "is_safe": true}
  }],
  "summary": {"total_beams": 1, "passed": 1, "failed": 0}
}
```

---

## 2. Batch Process Multiple Beams

Create a CSV file with your beam data:

```csv
BeamID,Story,b,D,eff_d,Span,Cover,fck,fy,Mu,Vu,Stirrup_Dia,Stirrup_Spacing
B1,Ground,300,500,450,4000,40,25,500,150,100,8,150
B2,Ground,230,450,400,3500,40,20,415,80,75,8,175
B3,First,350,600,550,5000,40,30,500,250,150,10,125
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
import structural_lib as sl

# Single beam design
result = sl.design_beam_is456(
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
3. **Explore advanced features** — See [Python Recipes](../cookbook/python-recipes.md) for complex scenarios
