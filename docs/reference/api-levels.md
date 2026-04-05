# Which API Should I Use?

**Type:** Reference | **Audience:** Developers | **Status:** Active
**Importance:** High | **Created:** 2026-04-05 | **Last Updated:** 2026-04-05

---

structural_lib exposes three API levels. Pick the one that matches your use case.

## Level 1: High-Level Service API (recommended)

**Module:** `structural_lib` (top-level) or `structural_lib.services.api`
**Best for:** Complete design workflows with all IS 456 compliance checks.

```python
import structural_lib as sl

# Beam design (flexure + shear + serviceability)
result = sl.design_beam_is456(
    units="IS456", b_mm=300, D_mm=500, d_mm=450,
    fck_nmm2=25, fy_nmm2=500, mu_knm=150, vu_kn=100,
)

# Column axial capacity
col = sl.design_column_axial_is456(
    b_mm=400, D_mm=400, fck=25, fy=415,
    Ast_mm2=2412, unsupported_length_mm=3000,
)

# Design + detailing + BBS in one call
full = sl.design_and_detail_beam_is456(
    units="IS456", beam_id="B1", story="GF", span_mm=6000,
    b_mm=300, D_mm=500, mu_knm=150, vu_kn=100,
)
```

**Returns:** Typed dataclasses (`ComplianceCaseResult`, `DesignAndDetailResult`) with `.is_safe()`, `.to_dict()`, `.summary()`.

## Level 2: Module-Level Functions (custom workflows)

**Module:** `structural_lib.codes.is456.beam.flexure`, `.shear`, etc.
**Best for:** Individual calculations without the full pipeline.

```python
from structural_lib.codes.is456.beam.flexure import design_singly_reinforced
from structural_lib.codes.is456.beam.shear import design_shear

# Just flexure
flexure = design_singly_reinforced(b=300, d=450, d_total=500, mu_knm=150, fck=25, fy=500)

# Just shear
shear = design_shear(b_mm=300, d_mm=450, vu_kn=100, fck=25, fy=500)
```

**Returns:** Individual result dataclasses (`FlexureResult`, `ShearResult`).

> **Parameter names differ between levels.** Level 1 uses `b_mm`, `fck_nmm2`; Level 2 uses `b`, `fck`. Always run `discover_api_signatures.py <func>` to confirm.

## Level 3: FastAPI REST API (web/mobile apps)

**Base URL:** `http://localhost:8000/api/v1/`
**Best for:** Web frontends, mobile apps, microservice integration.

```bash
curl -X POST http://localhost:8000/api/v1/design/beam \
  -H "Content-Type: application/json" \
  -d '{"b_mm": 300, "D_mm": 500, "d_mm": 450,
       "fck": 25, "fy": 500, "Mu_kNm": 150, "Vu_kN": 100}'
```

**Key endpoints:** `POST /design/beam`, `POST /design/column`, `POST /detailing/beam`, `POST /export/bbs`
**API docs:** `http://localhost:8000/docs` (auto-generated OpenAPI)

## Decision Tree

| I want to... | Use |
|--------------|-----|
| Design a complete beam | Level 1: `design_beam_is456()` |
| Design a column | Level 1: `design_column_axial_is456()` |
| Get only flexure capacity | Level 2: `flexure.design_singly_reinforced()` |
| Build a web frontend | Level 3: `POST /api/v1/design/beam` |
| Run a full pipeline (design → detail → BBS → report) | Level 1: `design_and_detail_beam_is456()` + `compute_bbs()` |
| Import ETABS CSV and batch-design | Level 1: `create_jobs_from_etabs_csv()` |
| Get xu_max/d for Fe500 | Level 2: `materials.get_xu_max_d(500)` |

## See Also

- [API Reference](api.md) — full function signatures
- [End-to-end example](../../Python/examples/end_to_end_workflow.py) — complete workflow