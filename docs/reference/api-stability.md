# API Stability

> This document defines which parts of the library are safe to depend on and which may change.

---

## Versioning Policy

This library follows [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0 → 2.0): Breaking changes to Stable API
- **MINOR** (1.0 → 1.1): New features, no breaking changes
- **PATCH** (1.0.0 → 1.0.1): Bug fixes only

**Current status:** Pre-1.0 (API may change between minor versions)

---

## Stable API (Safe to Depend On)

These functions have stable signatures and behavior. We will not break them without a major version bump.

### Core Design Functions

```python
from structural_lib import flexure, shear

# Flexure
flexure.design_singly_reinforced(b, d, d_total, mu_knm, fck, fy, ...)
flexure.design_doubly_reinforced(b, d, d_dash, d_total, mu_knm, fck, fy, ...)
flexure.design_flanged_beam(bf, bw, Df, d, d_total, mu_knm, fck, fy, ...)

# Shear
shear.design_shear(vu_kn, b, d, fck, fy, asv, pt)
```

### High-Level API

```python
from structural_lib import api

api.get_library_version()
api.validate_job_spec(path)
api.validate_design_results(path)
api.check_beam_ductility(b, D, d, fck, fy, min_long_bar_dia)
api.check_deflection_span_depth(span_mm, d_mm, support_condition, ...)
api.check_crack_width(exposure_class, limit_mm, ...)
api.check_compliance_report(cases, b_mm, D_mm, d_mm, fck_nmm2, fy_nmm2, ...)
api.design_beam_is456(units, case_id, mu_knm, vu_kn, b_mm, D_mm, d_mm, ...)
api.check_beam_is456(
    units, cases, b_mm, D_mm, d_mm, fck_nmm2, fy_nmm2, ...
)
api.detail_beam_is456(
    units, beam_id, story, b_mm, D_mm, span_mm, cover_mm, fck_nmm2, fy_nmm2, ...
)
api.design_and_detail_beam_is456(
    units, beam_id, story, span_mm, mu_knm, vu_kn, b_mm, D_mm, ...
)  # Combined design + detailing convenience function
api.design_from_input(beam, include_detailing=True)  # Design using BeamInput
```

### Input Dataclasses (v0.17+)

```python
from structural_lib import api

# Input containers for type-safe design workflow
api.BeamGeometryInput(b_mm, D_mm, span_mm, d_mm=None, cover_mm=40.0)
api.MaterialsInput(fck_nmm2, fy_nmm2, es_nmm2=200000.0)
api.MaterialsInput.m25_fe500()  # Factory method
api.MaterialsInput.m30_fe500()  # Factory method
api.LoadsInput(mu_knm, vu_kn, case_id="CASE-1")
api.LoadCaseInput(case_id, mu_knm, vu_kn, description="")
api.DetailingConfigInput(is_seismic=False, seismic_zone=None, ...)
api.DetailingConfigInput.seismic(zone=3)  # Factory method
api.BeamInput(beam_id, story, geometry, materials, loads=None, load_cases=[], ...)
api.BeamInput.from_dict(data)  # Create from dictionary
api.BeamInput.from_json(json_string)  # Create from JSON string
api.BeamInput.from_json_file(path)  # Create from JSON file
```

Note: `api.check_compliance_report()` assumes IS456 units (mm, N/mm², kN, kN·m)
and does not perform explicit unit validation. Use `api.check_beam_is456()` when
you want unit validation at the API boundary.

### Pipeline Functions

```python
from structural_lib import beam_pipeline

beam_pipeline.validate_units(units)
beam_pipeline.design_single_beam(units, beam_id, story, b_mm, D_mm, ...)
beam_pipeline.design_multiple_beams(units, beams, ...)
```

### Serviceability

```python
from structural_lib import serviceability

serviceability.check_deflection_span_depth(span_mm, d_mm, support_condition, ...)
serviceability.check_deflection_level_b(...)
serviceability.check_crack_width(...)
```

### Detailing

```python
from structural_lib import detailing

detailing.get_development_length(dia_mm, fck, fy, bar_type)
detailing.get_lap_length(dia_mm, fck, fy, bar_type, lap_class)
detailing.create_beam_detailing(...)
```

### BBS & Export

```python
from structural_lib import bbs, dxf_export

# BBS
doc = bbs.generate_bbs_document(detailing_list, project_name="Beam BBS")
bbs.export_bbs_to_csv(doc.items, "schedule.csv")
bbs.export_bbs_to_json(doc, "schedule.json")

# DXF
dxf_export.generate_beam_dxf(detailing, "beam_detail.dxf")
dxf_export.generate_multi_beam_dxf(detailing_list, "all_beams.dxf")
```

---

## Stable API (v0.12)

These library-first helpers are stable once released.

```python
from structural_lib import api

api.compute_detailing(design_results, config=None)
api.compute_bbs(detailing_list, project_name="Beam BBS")
api.export_bbs(bbs_doc, path, fmt="csv")
api.compute_dxf(detailing_list, output, multi=False)
api.compute_report(source, format="html")
api.compute_critical(job_out, top=10, format="csv")
```

## Planned API (v0.12 Target)

These helpers are planned next (see `docs/planning/v0.12-plan.md`).
They are **not available yet**, but will be stable once shipped.

No additional helpers are planned in this bucket yet.

---

## Experimental API (Preview Features)

These features are available for testing but API may change before v1.0.

### Advisory Insights (v0.13.0+)

```python
from structural_lib.insights import (
    quick_precheck,
    sensitivity_analysis,
    calculate_constructability_score,
)

# Heuristic precheck
precheck = quick_precheck(span_mm=5000, b_mm=300, d_mm=450, ...)

# Sensitivity analysis
sensitivities, robustness = sensitivity_analysis(design_function, params, ...)

# Constructability scoring
score = calculate_constructability_score(design_result, detailing)
```

**Status:** Preview - API signatures and scoring algorithms may change.

See: [Insights Guide](../getting-started/insights-guide.md), [Insights API Reference](insights-api.md)

---

## Internal API (May Change Without Notice)

These modules are implementation details. Do not depend on them directly.

| Module | Purpose | Why Internal |
|--------|---------|--------------|
| `tables.py` | IS 456 table lookups | May be reorganized for performance |
| `utilities.py` | Helper functions | Signatures may change |
| `constants.py` | Magic numbers | May be consolidated |
| `materials.py` | Material properties | May merge with constants |
| `types.py` | Type definitions | Dataclass fields may change |
| `ductile.py` | Ductile detailing checks | Under development |
| `report.py` | Report generation helpers | Experimental; subject to change |
| `report_svg.py` | SVG rendering helpers | Experimental; subject to change |
| `excel_integration.py` | Excel batch helpers | Under review |
| `insights/` | Advisory insights module | Preview; API may change before v1.0 |

### How to Use Internal Modules Safely

If you must use an internal module:

```python
# Pin to exact version
# requirements.txt
structural-lib-is456==0.16.6

# Or wrap with try/except
try:
    from structural_lib.tables import get_tau_c
except ImportError:
    # Fallback or error handling
    pass
```

---

## Deprecated API (Will Be Removed)

| Function | Deprecated In | Remove In | Replacement |
|----------|---------------|-----------|-------------|
| _(none currently)_ | — | — | — |

When we deprecate something:
1. We add a deprecation warning
2. It stays for at least one minor version
3. We document the replacement

---

## CLI Stability

The CLI interface (`python -m structural_lib`) is considered **stable**:

```bash
# These commands are stable
python -m structural_lib design input.csv -o results.json
python -m structural_lib bbs results.json -o bbs.csv
python -m structural_lib detail results.json -o detailing.json
python -m structural_lib dxf results.json -o drawings.dxf
python -m structural_lib job job.json -o output/
python -m structural_lib validate job.json
python -m structural_lib critical output/ --top 10 --format=csv -o critical.csv
python -m structural_lib report output/ --format=html -o report.html
python -m structural_lib mark-diff --bbs schedule.csv --dxf drawings.dxf
```

Output JSON schema is versioned via `schema_version` field.

---

## Output Schema Stability

### Schema Version 1 (Current)

The `BeamDesignOutput` schema is stable:

```json
{
  "schema_version": 1,
  "code": "IS456",
  "units": "IS456",
  "beam_id": "B1",
  "story": "Story1",
  "geometry": { "b_mm": 300, "D_mm": 500, ... },
  "materials": { "fck_nmm2": 25, "fy_nmm2": 500 },
  "flexure": { "ast_required_mm2": 1200, ... },
  "shear": { ... },
  "serviceability": { ... },
  "detailing": { ... },
  "is_ok": true,
  "governing_check": "flexure"
}
```

**Guarantees:**
- Existing fields will not be removed
- Field meanings will not change
- New fields may be added (forward-compatible)

---

## How to Report Breaking Changes

If you find a breaking change:

1. Check if you're using a Stable or Internal API
2. If Stable: [Open an issue](https://github.com/Pravin-surawase/structural_engineering_lib/issues) — this is a bug
3. If Internal: Consider switching to Stable API

---

## Changelog

- **2025-12-27**: Initial API stability document (v0.9.6)
- **2025-12-29**: Added planned API targets (library-first expansion)
