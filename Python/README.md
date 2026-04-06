# structural-lib-is456

IS 456 RC Beam Design Library (Python package).

**Version:** 0.21.6 (development preview)
**Status:** [![Python tests](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/python-tests.yml)

> ⚠️ **Development Preview:** APIs may change until v1.0. For reproducible results, pin to a release tag.

## Install

```bash
pip install structural-lib-is456           # from PyPI
pip install "structural-lib-is456[dxf]"    # with DXF export support

# Or pin to a release tag
pip install "structural-lib-is456 @ git+https://github.com/Pravin-surawase/structural_engineering_lib.git@v0.21.5#subdirectory=Python"
```

> **Requires Python 3.11+.** On Python 3.9–3.10, pip installs the older v0.16.x (beam-only, no column/footing).

---

## If You Want To…

### Design a Beam (IS 456 flexure + shear)

```python
from structural_lib import design_beam_is456

result = design_beam_is456(
    units="IS456", b_mm=300, D_mm=500, d_mm=450,
    fck_nmm2=25, fy_nmm2=500,
    mu_knm=150, vu_kn=100,
)
print(f"Ast = {result.flexure.Ast_required:.0f} mm²")
print(f"Safe? {result.flexure.is_safe}")
```

### Get Detailing (bar sizes, stirrups, cut lengths)

```python
from structural_lib import build_detailing_input, compute_detailing

detailing_input = build_detailing_input(
    result, beam_id="B1", b_mm=300, D_mm=500, d_mm=450,
    span_mm=6000, cover_mm=30, fck_nmm2=25, fy_nmm2=500,
)
detailed = compute_detailing(detailing_input)

for beam in detailed:
    print(f"{beam.beam_id}: {len(beam.top_bars)} top, {len(beam.bottom_bars)} bottom zones")
```

### Generate a Bar Bending Schedule (BBS)

```python
from structural_lib import compute_bbs

bbs = compute_bbs(detailed, project_name="My Project")
print(f"Total weight: {bbs.summary.total_weight_kg:.1f} kg")
for item in bbs.items:
    print(f"  {item.bar_mark}: ø{item.diameter_mm:.0f} × {item.no_of_bars} nos")
```

### Export DXF Drawings

```python
from structural_lib import compute_dxf

output_path = compute_dxf(detailed, "beam.dxf")  # returns Path
print(f"DXF saved to {output_path}")
```

> Requires the `dxf` extra: `pip install "structural-lib-is456[dxf]"`

### Generate an HTML Report

```python
from structural_lib import compute_report

html = compute_report(detailing_input, format="html")
with open("report.html", "w") as f:
    f.write(html)
```

### Batch Design from CSV

```python
from structural_lib.services.adapters import GenericCSVAdapter
from structural_lib import design_beam_is456

adapter = GenericCSVAdapter()
geometry_list, forces_list = adapter.load_combined("beams.csv")
# Pair geometry with forces and design each beam
for geom, forces in zip(geometry_list, forces_list):
    result = design_beam_is456(
        units="IS456", b_mm=geom.b_mm, D_mm=geom.D_mm, d_mm=geom.d_mm,
        fck_nmm2=geom.fck_nmm2, fy_nmm2=geom.fy_nmm2,
        mu_knm=forces.mu_knm, vu_kn=forces.vu_kn,
    )
    print(f"Ast = {result.flexure.Ast_required:.0f} mm²")
```

### Run the Full Pipeline (design → detail → BBS → report)

See [examples/end_to_end_workflow.py](https://github.com/Pravin-surawase/structural_engineering_lib/blob/main/Python/examples/end_to_end_workflow.py) for a complete working script (available in the source repository).

### Cost-Optimize a Beam

```python
from structural_lib import optimize_beam_cost

optimized = optimize_beam_cost(
    units="IS456", span_mm=6000, mu_knm=150, vu_kn=100,
)
print(f"Optimal: {optimized.optimal_design.b_mm}×{optimized.optimal_design.D_mm} mm")
```

### Check Multi-Case Compliance

```python
from structural_lib import check_beam_is456

report = check_beam_is456(
    units="IS456", b_mm=230, D_mm=500, d_mm=450,
    fck_nmm2=25, fy_nmm2=500,
    cases=[{"case_id": "ULS-1", "mu_knm": 100, "vu_kn": 80}],
)
print(f"Governing case: {report.governing_case_id}")
```

---

## CLI Usage

```bash
python -m structural_lib design input.csv -o results.json        # Beam design
python -m structural_lib bbs results.json -o bbs.csv             # Bar bending schedule
python -m structural_lib dxf results.json -o drawings.dxf        # DXF drawings
python -m structural_lib report results.json --format=html -o report.html  # HTML report
python -m structural_lib job job.json -o output/                 # Full job from spec
python -m structural_lib --help                                  # All options
```

---

## What's Available

### Beam Design & Detailing

| Category | Functions | Description |
|----------|-----------|-------------|
| **Beam Design** | `design_beam_is456`, `design_and_detail_beam_is456`, `design_from_input` | IS 456 flexure + shear |
| **Detailing** | `build_detailing_input`, `compute_detailing`, `detail_beam_is456` | Bar sizes, stirrups, cut lengths |
| **Optimization** | `optimize_beam_cost`, `smart_analyze_design`, `suggest_beam_design_improvements` | Cost optimization, smart analysis |
| **Compliance** | `check_beam_is456`, `check_compliance_report`, `check_beam_slenderness`, `check_beam_ductility` | Multi-case IS 456 checks |
| **Torsion** | `design_torsion`, `calculate_equivalent_shear`, `calculate_equivalent_moment`, `calculate_torsion_shear_stress`, `calculate_torsion_stirrup_area`, `calculate_longitudinal_torsion_steel` | IS 456 Cl 41 torsion design |
| **Serviceability** | `check_deflection_span_depth`, `check_crack_width` | Deflection + crack width |
| **Shear** | `enhanced_shear_strength_is456` | Enhanced shear near supports (IS 456 Cl 40.5) |
| **Load Analysis** | `compute_bmd_sfd` | Bending moment & shear force diagrams |

### Column Design (IS 456 Cl 25, 39.3–39.7)

| Category | Functions | Description |
|----------|-----------|-------------|
| **Unified Design** | `design_column_is456` | Full column design orchestration |
| **Axial Capacity** | `design_column_axial_is456` | Short column axial capacity (Cl 39.3) |
| **Uniaxial Bending** | `design_short_column_uniaxial_is456` | Short column with uniaxial moment (Cl 39.5) |
| **Biaxial Bending** | `biaxial_bending_check_is456` | Biaxial bending check (Cl 39.6) |
| **Long/Slender Columns** | `design_long_column_is456`, `calculate_additional_moment_is456` | Slender column design with additional moment (Cl 39.7) |
| **Classification** | `classify_column_is456`, `calculate_effective_length_is456`, `min_eccentricity_is456` | Short/slender classification, effective length (Table 28) |
| **Interaction Curve** | `pm_interaction_curve_is456` | P-M interaction diagram generation |
| **Helical Reinforcement** | `check_helical_reinforcement_is456` | Helical reinforcement check (Cl 39.4) |
| **Column Detailing** | `detail_column_is456` | Reinforcement detailing (Cl 26.5.3) |

### Footing Design (IS 456 Cl 34)

| Category | Functions | Description |
|----------|-----------|-------------|
| **Sizing** | `size_footing` | Footing plan dimensions from load & SBC |
| **Flexure** | `footing_flexure` | Critical section bending design |
| **One-Way Shear** | `footing_one_way_shear` | One-way shear check at d from face |
| **Punching Shear** | `footing_punching_shear` | Two-way punching shear at d/2 perimeter |
| **Bearing** | `check_bearing_pressure`, `bearing_stress_enhancement` | Bearing pressure & stress enhancement |

### IS 13920 Ductile Detailing

| Category | Functions | Description |
|----------|-----------|-------------|
| **Ductile Detailing** | `check_column_ductility_is13920` | IS 13920 seismic ductile detailing checks |

### Export, Import & Visualization

| Category | Functions | Description |
|----------|-----------|-------------|
| **BBS / Export** | `compute_bbs`, `export_bbs`, `compute_dxf`, `compute_report` | BBS, DXF, HTML reports |
| **CSV Import** | `GenericCSVAdapter` (via `structural_lib.services.adapters`) | 40+ column mappings |
| **ETABS Integration** | `load_etabs_csv`, `create_job_from_etabs`, `create_jobs_from_etabs_csv`, `validate_etabs_csv`, `normalize_etabs_forces` | ETABS CSV import |
| **3D Geometry** | `beam_to_3d_geometry`, `compute_rebar_positions`, `compute_stirrup_positions`, `compute_beam_outline` | 3D rebar visualization |
| **Validation** | `validate_job_spec`, `validate_design_results`, `verify_calculation` | Input/output validation |
| **Audit** | `compute_hash`, `create_calculation_certificate`, `generate_calculation_report` | Calculation audit trail |

> Full API reference: see [docs/reference/api.md](../docs/reference/api.md)

## License

MIT — see [LICENSE](LICENSE).
