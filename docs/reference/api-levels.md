---
owner: Main Agent
status: active
last_updated: 2026-08-10
doc_type: reference
complexity: intermediate
tags: [api, reference]
---

# Which API Should I Use?

**Type:** Reference | **Audience:** Developers | **Status:** Active
**Importance:** High | **Created:** 2026-04-05 | **Last Updated:** 2026-08-10

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

# Complete short-column workflow, including biaxial interaction
col = sl.design_column_is456(
    Pu_kN=1000, Mux_kNm=80, Muy_kNm=40,
    b_mm=400, D_mm=400, l_mm=3000,
    fck_nmm2=25, fy_nmm2=415, Asc_mm2=2412,
)
assert col["is_safe"]

# Design + detailing + BBS in one call
full = sl.design_and_detail_beam_is456(
    units="IS456", beam_id="B1", story="GF", span_mm=6000,
    b_mm=300, D_mm=500, mu_knm=150, vu_kn=100,
)
```

**Returns:** Beam workflows return typed result dataclasses. Use `.is_ok` for the
aggregate beam status and `.to_dict()`, `.to_json()`, or `.summary()` for the
supported representations. Column service functions currently return their
documented result type: `design_column_is456()` returns a dictionary with
`is_safe` and `governing_check`, while `design_column_axial_is456()` returns a
`ColumnAxialResult` with an `is_safe` field and `.to_dict()`.

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
  -d '{"width": 300, "depth": 500, "moment": 150,
       "shear": 100, "fck": 25, "fy": 500}'
```

JSON calculation endpoints use the maintained response envelope:

```json
{"success": true, "data": {"success": true, "flexure": {}}}
```

Read the calculation payload from `response.json()["data"]`. Health checks,
file downloads, streaming responses, and WebSockets use their endpoint-specific
contracts.

**Key endpoints:** `POST /design/beam`, `POST /design/column`, `POST /detailing/beam`, `POST /export/bbs`
**API docs:** `http://localhost:8000/docs` (auto-generated OpenAPI)

## Decision Tree

| I want to... | Use |
|--------------|-----|
| Design a complete beam | Level 1: `design_beam_is456()` |
| Run a complete supported column workflow | Level 1: `design_column_is456()` |
| Calculate short-column axial capacity | Level 1: `design_column_axial_is456()` |
| Get only flexure capacity | Level 2: `flexure.design_singly_reinforced()` |
| Build a web frontend | Level 3: `POST /api/v1/design/beam` |
| Run a full pipeline (design → detail → BBS → report) | Level 1: `design_and_detail_beam_is456()` + `compute_bbs()` |
| Import ETABS CSV and batch-design | Level 1: `create_jobs_from_etabs_csv()` |
| Get xu_max/d for Fe500 | Level 2: `materials.get_xu_max_d(500)` |

## See Also

- [API Reference](api.md) — full function signatures
- [End-to-end example](../../Python/examples/end_to_end_workflow.py) — complete workflow
