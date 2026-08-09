---
owner: Main Agent
status: active
last_updated: 2026-08-10
doc_type: reference
complexity: intermediate
tags: [fastapi, rest, openapi, is456]
---

# FastAPI REST API Reference

**Type:** Reference
**Audience:** Developers
**Status:** Active
**Importance:** High
**Created:** 2026-01-24
**Last Updated:** 2026-08-10

---

## Overview

The FastAPI application exposes the maintained Python calculation services to
the React workbench and external clients. The current v0.23.0 application has 63
HTTP operations plus streaming and WebSocket workflows.

| Environment | Base URL |
|---|---|
| Local development | `http://127.0.0.1:8000` |
| Docker evaluation | `http://localhost:8000` |
| Production | Deployment-specific; do not expose the default open-mode service |

Interactive, generated documentation is available from a running application:

| Endpoint | Purpose |
|---|---|
| `GET /docs` | Swagger UI |
| `GET /redoc` | ReDoc |
| `GET /openapi.json` | Current OpenAPI document |

The checked-in compatibility snapshot is
`fastapi_app/openapi_baseline.json`. Use the live document for request and
response generation, and use the snapshot to detect unintended contract drift.

## Authentication boundary

Local development defaults to open mode. Production-like profiles
(`production`, `prod`, or `staging`) fail during application construction unless
`AUTH_ENABLED=true` and `JWT_SECRET_KEY` is a non-placeholder value of at least
32 characters. The production Compose profile declares both requirements;
direct local development keeps the current open default.

When authentication is enabled, send:

```http
Authorization: Bearer <jwt-token>
```

Do not place the local development configuration directly on the public
internet.

## Response envelope

Maintained JSON calculation endpoints return a common outer envelope:

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

The runtime may omit optional `error` or `clause_refs` keys when they are not
needed. Read calculation fields from `data`; an inner calculation model may also
have its own `success`, `is_safe`, or `is_adequate` field.

Validation failures use the same boundary:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "REQUEST_VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": []
  }
}
```

Health checks, file downloads, server-sent events, and WebSockets use their
endpoint-specific response contracts rather than the JSON calculation envelope.

## Health checks

### `GET /health`

```json
{
  "status": "healthy",
  "version": "0.23.0",
  "timestamp": "<ISO-8601 timestamp>",
  "uptime_seconds": 0.0
}
```

### `GET /health/ready`

```json
{
  "ready": true,
  "checks": {
    "compute_engine": true,
    "structural_lib": true
  }
}
```

### `GET /health/info`

```json
{
  "api_version": "0.23.0",
  "python_version": "<runtime version>",
  "platform": "<runtime platform>",
  "structural_lib_available": true
}
```

## Executable beam-design example

### `POST /api/v1/design/beam`

Request units are explicit in the model descriptions: section dimensions and
cover are millimetres, moment is kN·m, shear is kN, and material strengths are
N/mm².

```bash
curl -X POST http://127.0.0.1:8000/api/v1/design/beam \
  -H "Content-Type: application/json" \
  -d '{
    "width": 300,
    "depth": 500,
    "moment": 150,
    "shear": 75,
    "fck": 25,
    "fy": 500,
    "clear_cover": 25
  }'
```

A successful response has this maintained shape. Numeric values are deliberately
not frozen in the guide; calculation regression evidence owns exact values.

```json
{
  "success": true,
  "data": {
    "success": true,
    "message": "Design complete: Ast = ... mm²",
    "flexure": {
      "ast_required": 0.0,
      "ast_min": 0.0,
      "ast_max": 0.0,
      "xu": 0.0,
      "xu_max": 0.0,
      "is_under_reinforced": true,
      "moment_capacity": 0.0,
      "asc_required": 0.0
    },
    "shear": {},
    "ast_total": 0.0,
    "asc_total": 0.0,
    "utilization_ratio": 0.0,
    "effective_depth_used": 0.0,
    "warnings": []
  }
}
```

Python client using the raw HTTP contract:

```python
import httpx

response = httpx.post(
    "http://127.0.0.1:8000/api/v1/design/beam",
    json={
        "width": 300,
        "depth": 500,
        "moment": 150,
        "shear": 75,
        "fck": 25,
        "fy": 500,
        "clear_cover": 25,
    },
    timeout=30.0,
)
response.raise_for_status()
payload = response.json()
design = payload["data"]
print(f"Ast required: {design['flexure']['ast_required']:.1f} mm²")
```

These examples are exercised by
`fastapi_app/tests/test_public_documentation_contract.py`.

## Endpoint families

The live OpenAPI document is authoritative for every field. The main endpoint
families are:

| Family | Representative operations |
|---|---|
| Beam design | `POST /api/v1/design/beam`, `/beam/check`, `/beam/torsion` |
| Column design | classification, axial, uniaxial, biaxial, long-column, detailing |
| Library core | bounded slab and footing workflows |
| Detailing | beam layout, anchorage, development length, standard bar areas |
| Compliance | ductility, slenderness, anchorage, deflection, crack width |
| Import | combined CSV, dual CSV, ETABS/sample workflows |
| Geometry | beam, cross-section, building, and full reinforcement geometry |
| Insights | batch dashboard and design insight operations |
| Optimization | cost and Pareto beam optimization |
| Export | BBS, DXF, HTML/PDF reports, CSV summaries, and BOQ |
| Runtime | health, readiness, system information, SSE, and WebSocket updates |

Use Swagger/ReDoc or the OpenAPI JSON instead of copying an undocumented model
from another endpoint. Some Python-level names intentionally differ from REST
names because unit conversion occurs at the service boundary.

## Client generation status

Raw HTTP plus the live OpenAPI document is the supported integration path for
v0.23.0 Alpha. Every maintained JSON 2xx operation now declares a response
schema; binary downloads and SSE routes declare their non-JSON response class.
The development clients under `clients/` have been regenerated from this
snapshot and correctly unwrap `{success, data}`. They remain unpublished Alpha
templates rather than a stable client-package promise.

Regenerate after an intentional OpenAPI change with:

```bash
.venv/bin/python scripts/validate_api_contracts.py --diff
.venv/bin/python scripts/generate_client_sdks.py
```

## Validation commands

```bash
.venv/bin/pytest fastapi_app/tests/test_public_documentation_contract.py -q
.venv/bin/python scripts/validate_api_contracts.py
./run.sh test --fastapi
```

## Related documents

- [Which API should I use?](api-levels.md)
- [Python API reference](api.md)
- [FastAPI deployment guide](../guides/fastapi-deployment-guide.md)
- [Engineering evidence boundary](../verification/is456-library-first-evidence.md)
