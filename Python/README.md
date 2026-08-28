# structural-lib-is456

IS 456 reinforced-concrete design library (Python package).

**Version:** 0.24.0 (normal software release; broader development in progress)
**Status:** [![Weekly Verification](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/nightly.yml/badge.svg)](https://github.com/Pravin-surawase/structural_engineering_lib/actions/workflows/nightly.yml)

> ⚠️ **Pre-1.0 API:** APIs may change until v1.0. For reproducible results, pin to an exact release.

> **Supported-case boundary:** this package implements selected IS 456 workflows,
> not the whole standard. Every output requires independent verification and
> qualified structural-engineering review. Use official standards as the
> authoritative source.

## New in v0.24.0

- **Fail-closed project intake:** malformed, missing, unknown, or mixed-validity
  beam rows block the whole project instead of being defaulted or skipped.
- **Safe public CLI:** `design` keeps JSON on stdout, sends diagnostics to stderr,
  exits non-zero on blocked input, and preserves the `bbs`/`detail`/`dxf` chain.
- **Traceable results:** import ledgers, input/result provenance, API classification,
  and qualified-review boundaries are explicit and machine-readable.
- **Additional bounded workflows:** braced walls, straight-flight staircases,
  simply supported deep beams, regular interior flat slabs, symmetric combined
  footings, and property-line strap footings expose case-qualified APIs.
- **Release evidence:** exact-wheel UAT covers 29 positive and negative cases,
  15 CLI entries, and the 13 canonical family construction journeys.

## Install

```bash
pip install structural-lib-is456===0.24.0         # exact normal release
pip install "structural-lib-is456[dxf]===0.24.0"  # release with DXF export
python -m structural_lib install-preflight          # interpreter/origin/extras
```

`0.24.0` is the current normal package version and is selected without `--pre`.
The Beta maturity classifier and the explicit limitations above
remain: broader library development and cumulative practicing-engineer review
are still in progress.

> **Requires Python 3.11+.** On Python 3.9–3.10, pip installs the older v0.16.x (beam-only, no column/footing).

---

## If You Want To…

### Design and Detail a Beam Through the Canonical Facade

```python
from structural_lib.design.is456 import beam

detailing = beam.BeamDetailingOptionsV1(
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
request = beam.input(
    member_id="B1",
    story="GF",
    case_id="ULS-1",
    span_mm=5000,
    b_mm=300,
    D_mm=550,
    d_mm=500,
    fck_nmm2=25,
    fy_nmm2=500,
    mu_knm=150,
    vu_kn=80,
    d_dash_mm=50,
    asv_mm2=detailing.asv_mm2,
    detailing=detailing,
    source_provenance="analysis-envelope:ULS-1",
)
result = beam.design_and_detail(
    request,
    detailing_standard=beam.DetailingStandard.IS456,
)

print(result.engineering_status)
print(result.to_dict())
```

The complete 13-journey cookbook is maintained at
`docs/cookbook/python/family-facades.md` in the source repository.

### Generate a Bar Bending Schedule (BBS)

```python
bbs = beam.bbs(result)
print(f"Total weight: {bbs.total_weight_kg:.1f} kg")
for item in bbs.items:
    print(f"  {item.bar_mark}: ø{item.diameter_mm:.0f} × {item.no_of_bars} nos")
```

### Export DXF Drawings and Reports

Use the fail-closed CLI pipeline for project files and exports:

```bash
python -m structural_lib design input.csv -o results.json
python -m structural_lib detail results.json -o detailing.json
python -m structural_lib bbs results.json -o schedule.csv
python -m structural_lib dxf results.json -o drawings.dxf
python -m structural_lib report results.json --format=html -o report.html
```

> Requires the `dxf` extra: `pip install "structural-lib-is456[dxf]"`

### Batch Design with the Canonical Project Schema

```python
from structural_lib.services.batch import design_project_beams_v1

batch = design_project_beams_v1(
    [
        {
            "schema_version": "project-beam-design/v1",
            "member_id": "B1",
            "b_mm": 300,
            "D_mm": 500,
            "d_mm": 442,
            "mu_knm": 150,
            "vu_kn": 100,
            "fck_nmm2": 25,
            "fy_nmm2": 500,
        }
    ]
)
print(batch.summary.to_dict())
print(batch.members[0].calculation["flexure"]["ast_required"])
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

The `design` command is fail-closed. CSV input must explicitly supply
`BeamID,Story,b,D,eff_d,Span,Cover,fck,fy,Mu,Vu,Stirrup_Dia,Stirrup_Spacing`.
Instead of `eff_d`, supply `tension_bar_diameter_mm` so effective depth can be
derived from the explicit cover and stirrup diameter. JSON input uses the
`cli-beam-design-input/v1` envelope. Unknown, duplicate, malformed, non-finite,
empty, ambiguous, or mixed-validity input blocks the whole project without a
partial result.

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

The primary combined beam route covers flexure and shear. Torsion is available
only through the separate explicit torsion workflow.

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
| **Unified Design** | `design_column_is456` | Bounded rectangular-column orchestration |
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
| **Load Transfer** | `check_isolated_footing_load_transfer` | Bounded concentric bearing/dowel transfer with approved effective A1 |

The low-level functions in this section cover isolated footings. Separate
canonical facades cover bounded symmetric combined-footing and property-line
strap-footing cases; use their generated recipes to see every required
assumption and evidence field. Raft and pile-cap foundations, settlement,
geotechnical design, and lateral stability remain outside the supported routes.

### Solid Slab Design (Supported Cases)

| Category | Functions | Description |
|----------|-----------|-------------|
| **One-Way Slab** | `design_one_way_slab_is456` | Simply supported solid rectangular strip: flexure and supplied-bar checks |
| **Two-Way Slab** | `design_two_way_slab_is456` | One interior four-edge-continuous flexure case using accepted caller-supplied coefficients |
| **Discovery** | `get_supported_is456_capabilities` | Machine-readable supported workflows and held cases |

The canonical two-way facade uses the library's bounded normalized coefficient
lookup and interpolation for supported common panels. Compatibility functions
that accept caller-supplied coefficients remain separate and require explicit
source approval. Drop/ribbed slabs, openings, irregular panels, concentrated
loads, and FEM remain outside the solid-slab route; use the separate regular
interior flat-slab facade only for its documented bounded case.

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

Engineering-use conditions and professional responsibilities are described in
the repository's `LICENSE_ENGINEERING.md`. The software is a design aid, not a
substitute for official code publications, independent calculation, or
professional approval.
