# Python Recipes

Copy-paste snippets for common structural engineering tasks.

## Setup

```bash
pip install structural-lib-is456
# For DXF support:
pip install structural-lib-is456[dxf]
```

```python
from structural_lib import api, flexure, shear, detailing, bbs
```

---

## 1. Quick Beam Design (Single Case)

```python
from structural_lib import api

b_mm = 300
D_mm = 500
d_mm = 450

result = api.design_beam_is456(
    units="IS456",
    case_id="DL+LL",
    b_mm=b_mm,
    D_mm=D_mm,
    d_mm=d_mm,
    fck_nmm2=25,
    fy_nmm2=500,
    mu_knm=150,
    vu_kn=100,
)

print(f"Flexure: {'OK' if result.flexure.is_safe else 'FAIL'}")
print(f"  Ast required: {result.flexure.ast_required:.1f} mm²")
print(f"  xu/d: {result.flexure.xu / d_mm:.3f}")

print(f"Shear: {'OK' if result.shear.is_safe else 'FAIL'}")
print(f"  τv: {result.shear.tv:.3f} N/mm²")
print(f"  τc: {result.shear.tc:.3f} N/mm²")
print(f"  Stirrup spacing: {result.shear.spacing:.0f} mm")
```

---

## 2. Multi-Case Compliance Check

```python
from structural_lib import api

cases = [
    {"case_id": "DL+LL", "mu_knm": 80, "vu_kn": 60},
    {"case_id": "1.5(DL+LL)", "mu_knm": 120, "vu_kn": 90},
    {"case_id": "EQ-X", "mu_knm": 160, "vu_kn": 120},
]

report = api.check_beam_is456(
    units="IS456",
    cases=cases,
    b_mm=300,
    D_mm=500,
    d_mm=450,
    fck_nmm2=25,
    fy_nmm2=500,
)

print(f"Overall: {'PASS' if report.is_ok else 'FAIL'}")
print(f"Governing case: {report.governing_case_id}")
print(f"Max utilization: {report.governing_utilization:.2%}")

for result in report.cases:
    status = "OK" if result.is_ok else "FAIL"
    print(f"  {result.case_id}: {status}")
```

---

## 3. Flexure Design (Low-Level)

### Singly Reinforced
```python
from structural_lib import flexure

result = flexure.design_singly_reinforced(
    b=230,
    d=450,
    d_total=500,
    mu_knm=100,
    fck=20,
    fy=415,
)

print(f"Mu,lim: {result.mu_lim:.2f} kN·m")
print(f"Ast required: {result.ast_required:.1f} mm²")
print(f"xu: {result.xu:.1f} mm")
print(f"Section type: {result.section_type}")
```

### Doubly Reinforced
```python
from structural_lib import flexure

result = flexure.design_doubly_reinforced(
    b=300,
    d=450,
    d_dash=50,
    d_total=500,
    mu_knm=250,
    fck=25,
    fy=500,
)

print(f"Ast: {result.ast_required:.1f} mm²")
print(f"Asc: {result.asc_required:.1f} mm²")
```

### Flanged Beam (T-Beam)
```python
from structural_lib import flexure

Df = 150
result = flexure.design_flanged_beam(
    bw=300,
    bf=1000,
    d=500,
    Df=Df,
    d_total=550,
    mu_knm=200,
    fck=25,
    fy=500,
)

print(f"Ast: {result.ast_required:.1f} mm²")
print(f"NA location: {'in flange' if result.xu <= Df else 'in web'}")
```

---

## 4. Shear Design

```python
from structural_lib import shear

result = shear.design_shear(
    vu_kn=150,
    b=230,
    d=450,
    fck=20,
    fy=415,
    asv=100,  # total leg area (mm²)
    pt=1.0,   # % tension steel
)

print(f"τv: {result.tv:.3f} N/mm²")
print(f"τc: {result.tc:.3f} N/mm²")
print(f"τc,max: {result.tc_max:.2f} N/mm²")
print(f"Stirrup spacing: {result.spacing:.0f} mm")
print(f"Safe: {result.is_safe}")
```

---

## 5. Detailing (Ld, Lap, Bar Selection)

### Development Length
```python
from structural_lib import detailing

ld = detailing.calculate_development_length(
    bar_dia=16,
    fck=25,
    fy=500,
    bar_type="deformed",
)
print(f"Ld: {ld:.0f} mm")
```

### Lap Length
```python
lap = detailing.calculate_lap_length(
    bar_dia=16,
    fck=25,
    fy=500,
    bar_type="deformed",
)
print(f"Lap: {lap:.0f} mm")
```

### Full Beam Detailing
```python
from structural_lib import api

detail = api.detail_beam_is456(
    units="IS456",
    beam_id="B1",
    story="GF",
    b_mm=300,
    D_mm=500,
    span_mm=4000,
    cover_mm=40,
    fck_nmm2=25,
    fy_nmm2=500,
    ast_start_mm2=942,
    ast_mid_mm2=628,
    ast_end_mm2=942,
)

print(f"Bottom bars: {[b.callout() for b in detail.bottom_bars]}")
print(f"Top bars: {[b.callout() for b in detail.top_bars]}")
print(f"Stirrups: {[s.callout() for s in detail.stirrups]}")
print(f"Ld: {detail.ld_tension:.0f} mm")
```

---

## 6. Serviceability Checks

### Deflection (Span/Depth)
```python
from structural_lib import api

result = api.check_deflection_span_depth(
    span_mm=4000,
    d_mm=450,
    support_condition="simply_supported",
)

print(f"L/d: {result.computed['ld_ratio']:.2f}")
print(f"Allowable: {result.computed['allowable_ld']}")
print(f"Status: {'OK' if result.is_ok else 'FAIL'}")
```

### Crack Width
```python
from structural_lib import api

result = api.check_crack_width(
    exposure_class="moderate",
    acr_mm=50,
    cmin_mm=25,
    h_mm=500,
    x_mm=200,
    epsilon_m=0.001,
)

print(f"Crack width: {result.computed['wcr_mm']:.3f} mm")
print(f"Limit: {result.computed['limit_mm']:.2f} mm")
print(f"Status: {'OK' if result.is_ok else 'FAIL'}")
```

Note: `acr_mm` is the distance from the point considered to the nearest bar surface (mm).

---

## 7. Bar Bending Schedule (BBS)

```python
from structural_lib import bbs, detailing

# Create detailing for multiple beams
details = [
    detailing.create_beam_detailing(
        beam_id="B1", story="GF", b=300, D=500, span=4000, cover=40,
        fck=25, fy=500, ast_start=942, ast_mid=628, ast_end=942,
        stirrup_dia=8, stirrup_spacing_start=150, stirrup_spacing_mid=200,
        stirrup_spacing_end=150,
    ),
    detailing.create_beam_detailing(
        beam_id="B2", story="GF", b=300, D=450, span=3000, cover=40,
        fck=25, fy=500, ast_start=628, ast_mid=400, ast_end=628,
        stirrup_dia=8, stirrup_spacing_start=175, stirrup_spacing_mid=225,
        stirrup_spacing_end=175,
    ),
]

# Generate BBS
doc = bbs.generate_bbs_document(details, project_name="Building A")

# Print summary
print(f"Total bars: {doc.summary.total_bars}")
print(f"Total weight: {doc.summary.total_weight_kg:.2f} kg")

# Export to CSV
bbs.export_bbs_to_csv(doc.items, "bbs_schedule.csv")

# Or JSON
bbs.export_bbs_to_json(doc, "bbs_schedule.json")
```

---

## 8. DXF Export

```python
from structural_lib import detailing

# Check if ezdxf is available
try:
    from structural_lib import dxf_export
    EZDXF_AVAILABLE = dxf_export.EZDXF_AVAILABLE
except ImportError:
    EZDXF_AVAILABLE = False

if EZDXF_AVAILABLE:
    detail = detailing.create_beam_detailing(
        beam_id="B1", story="GF", b=300, D=500, span=4000, cover=40,
        fck=25, fy=500, ast_start=942, ast_mid=628, ast_end=942,
        stirrup_dia=8, stirrup_spacing_start=150, stirrup_spacing_mid=200,
        stirrup_spacing_end=150,
    )

    # Single beam
    dxf_export.generate_beam_dxf(detail, "beam_detail.dxf")

    # Multiple beams in grid layout
    details = [detail, detail]  # Your list of details
    dxf_export.generate_multi_beam_dxf(details, "all_beams.dxf", columns=2)
else:
    print("Install ezdxf: pip install ezdxf")
```

---

## 9. Load from CSV/JSON

```python
from structural_lib import excel_integration

# Load beams from CSV
beams = excel_integration.load_beam_data_from_csv("beams.csv")

for beam in beams:
    print(f"{beam.story}/{beam.beam_id}: {beam.b}x{beam.D}, Mu={beam.Mu}")

# Load from JSON
beams = excel_integration.load_beam_data_from_json("beams.json")
```

---

## 10. Job Runner (Batch Processing)

```python
from structural_lib import job_runner

# Run job from JSON specification
job_runner.run_job(
    job_path="job_spec.json",
    out_dir="./output",
)

# Output directory will contain:
# - summary.json (design results)
# - summary.csv (tabular format)
```

---

## Tips

### Unit Conventions
- **Inputs:** mm, N/mm², kN, kN·m
- **Internal:** mm, N, N·mm
- **Outputs:** mm, N/mm², kN, kN·m

### Error Handling
```python
try:
    result = api.design_beam_is456(...)
except ValueError as e:
    print(f"Invalid input: {e}")
```

### Check Library Version
```python
from structural_lib import api
print(api.get_library_version())
```

---

## Related

- [CLI Reference](cli-reference.md) — Command-line interface
- [API Reference](../reference/api.md) — Full API documentation
- [Verification Examples](../verification/examples.md) — Benchmark calculations
