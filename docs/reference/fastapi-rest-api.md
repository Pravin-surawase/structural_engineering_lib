# FastAPI REST API Reference

**Type:** Reference
**Audience:** Developers
**Status:** Draft
**Importance:** High
**Created:** 2026-01-24
**Last Updated:** 2026-01-24
**Related Tasks:** TASK-V3-FOUNDATION

---

## Overview

The Structural Engineering Library provides a REST API via FastAPI for beam design, analysis, and detailing per IS 456:2000.

### Base URL

| Environment | URL |
|-------------|-----|
| Local Development | `http://localhost:8000` |
| Docker | `http://localhost:8000` (same, mapped port) |
| Production | TBD |

### API Documentation

| Endpoint | Description |
|----------|-------------|
| `/docs` | Interactive Swagger UI |
| `/redoc` | ReDoc documentation |
| `/openapi.json` | OpenAPI 3.0 specification |

---

## Authentication

Currently the API operates in open mode. JWT authentication is available via the `auth.py` module.

### JWT Token (Optional)

```bash
# Include in header when auth is enabled
Authorization: Bearer <jwt_token>
```

---

## Endpoints

### Health Checks

#### GET `/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-01-24T10:00:00Z"
}
```

#### GET `/health/ready`

Readiness probe for container orchestration.

**Response:**
```json
{
  "ready": true
}
```

#### GET `/health/info`

Detailed system information.

**Response:**
```json
{
  "version": "0.1.0",
  "python_version": "3.11.8",
  "structural_lib_version": "0.19.0"
}
```

---

### Beam Design

#### POST `/api/v1/design/beam`

Design a reinforced concrete beam for flexure and shear.

**Request Body:**
```json
{
  "width": 300,
  "depth": 500,
  "moment": 150,
  "shear": 75,
  "fck": 25,
  "fy": 500,
  "clear_cover": 25
}
```

**Parameters:**

| Field | Type | Required | Description | Range |
|-------|------|----------|-------------|-------|
| `width` | float | Yes | Beam width (mm) | 0 < width ≤ 2000 |
| `depth` | float | Yes | Overall depth (mm) | 0 < depth ≤ 3000 |
| `moment` | float | Yes | Factored moment (kN·m) | ≥ 0 |
| `shear` | float | No | Factored shear (kN) | ≥ 0, default 0 |
| `fck` | float | No | Concrete strength (N/mm²) | 15-80, default 25 |
| `fy` | float | No | Steel strength (N/mm²) | 250-600, default 500 |
| `clear_cover` | float | No | Clear cover (mm) | 20-75, default 25 |

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Design complete: Ast = 882 mm²",
  "flexure": {
    "ast_required": 881.88,
    "ast_min": 229.5,
    "ast_max": 6000.0,
    "xu": 89.5,
    "xu_max": 214.5,
    "is_under_reinforced": true,
    "moment_capacity": 180.5,
    "asc_required": 0.0
  },
  "shear": {
    "tau_v": 0.65,
    "tau_c": 0.48,
    "tau_c_max": 3.1,
    "asv_required": 0.12,
    "stirrup_spacing": 200,
    "sv_max": 225,
    "shear_capacity": 150.0
  },
  "ast_total": 881.88,
  "asc_total": 0.0,
  "utilization_ratio": 0.83,
  "warnings": []
}
```

**Error Response (422 Validation Error):**
```json
{
  "detail": [
    {
      "loc": ["body", "width"],
      "msg": "Input should be greater than 0",
      "type": "greater_than"
    }
  ]
}
```

**Example - cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/design/beam" \
  -H "Content-Type: application/json" \
  -d '{"width": 300, "depth": 500, "moment": 150, "fck": 25, "fy": 500}'
```

**Example - Python:**
```python
import httpx

response = httpx.post(
    "http://localhost:8000/api/v1/design/beam",
    json={"width": 300, "depth": 500, "moment": 150, "fck": 25, "fy": 500}
)
result = response.json()
print(f"Ast required: {result['flexure']['ast_required']:.1f} mm²")
```

---

#### POST `/api/v1/design/beam/check`

Check if existing reinforcement is adequate.

**Request Body:**
```json
{
  "width": 300,
  "depth": 500,
  "moment": 150,
  "shear": 75,
  "ast_provided": 942,
  "stirrup_area": 157,
  "stirrup_spacing": 150,
  "fck": 25,
  "fy": 500
}
```

**Response:**
```json
{
  "is_adequate": true,
  "success": true,
  "message": "Section is adequate",
  "moment_capacity": 195.5,
  "shear_capacity": 165.0,
  "moment_utilization": 0.77,
  "shear_utilization": 0.45,
  "flexure_adequate": true,
  "shear_adequate": true,
  "warnings": []
}
```

---

#### GET `/api/v1/design/limits`

Get IS 456 design limits.

**Response:**
```json
{
  "fck_min": 15,
  "fck_max": 80,
  "fy_min": 250,
  "fy_max": 600,
  "cover_min": 20,
  "cover_max": 75,
  "pt_min_percentage": 0.12,
  "pt_max_percentage": 4.0
}
```

---

### Detailing

#### POST `/api/v1/detailing/beam`

Get reinforcement detailing for a beam.

**Request Body:**
```json
{
  "width": 300,
  "depth": 500,
  "ast_required": 882,
  "asc_required": 0,
  "asv_required": 0.12,
  "fck": 25,
  "fy": 500,
  "span_length": 6000
}
```

**Response:**
```json
{
  "success": true,
  "message": "Detailing complete",
  "tension_bars": [
    {
      "layer": 1,
      "bar_count": 4,
      "bar_diameter": 16,
      "area_provided": 804.2,
      "spacing": 52.0
    }
  ],
  "ast_provided": 942.5,
  "compression_bars": [],
  "asc_provided": 0,
  "stirrups": {
    "diameter": 8,
    "legs": 2,
    "spacing": 150,
    "area_per_meter": 0.67
  },
  "ld_tension": 752,
  "ld_compression": 0,
  "anchorage_length": 480,
  "curtailment_points": [],
  "warnings": []
}
```

---

#### GET `/api/v1/detailing/development-length/{bar_diameter}`

Calculate development length for a bar.

**Path Parameters:**
- `bar_diameter`: Bar diameter in mm (8, 10, 12, 16, 20, 25, 32)

**Query Parameters:**
- `fck`: Concrete strength (default 25)
- `fy`: Steel strength (default 500)
- `bar_type`: "deformed" or "plain" (default "deformed")

**Example:**
```
GET /api/v1/detailing/development-length/16?fck=25&fy=500
```

**Response:**
```json
{
  "bar_diameter": 16,
  "development_length": 752,
  "bond_stress": 1.92,
  "bar_type": "deformed"
}
```

---

#### GET `/api/v1/detailing/bar-areas`

Get standard bar areas reference.

**Response:**
```json
{
  "bars": [
    {"diameter": 8, "area": 50.27},
    {"diameter": 10, "area": 78.54},
    {"diameter": 12, "area": 113.1},
    {"diameter": 16, "area": 201.1},
    {"diameter": 20, "area": 314.2},
    {"diameter": 25, "area": 490.9},
    {"diameter": 32, "area": 804.2}
  ]
}
```

---

### Analysis

#### POST `/api/v1/analysis/beam/smart`

Get smart design insights and recommendations.

**Request Body:**
```json
{
  "width": 300,
  "depth": 500,
  "moment": 150,
  "fck": 25,
  "fy": 500
}
```

**Response:**
```json
{
  "utilization": 0.83,
  "recommendations": [
    "Section is under-reinforced as required by IS 456",
    "Consider 4-16mm bars for main reinforcement"
  ],
  "optimization_potential": "low"
}
```

---

### Optimization

#### POST `/api/v1/optimization/beam/cost`

Optimize beam section for cost.

**Request Body:**
```json
{
  "moment": 150,
  "fck": 25,
  "fy": 500,
  "width_range": [200, 400],
  "depth_range": [400, 600],
  "concrete_rate": 8000,
  "steel_rate": 75
}
```

**Response:**
```json
{
  "optimal_width": 280,
  "optimal_depth": 520,
  "ast_required": 845,
  "total_cost_per_meter": 2450,
  "concrete_cost": 1165,
  "steel_cost": 1285
}
```

---

### Geometry

#### POST `/api/v1/geometry/beam/3d`

Generate 3D geometry data for visualization.

**Request Body:**
```json
{
  "width": 300,
  "depth": 500,
  "length": 6000,
  "include_rebar": true
}
```

**Response:**
```json
{
  "vertices": [...],
  "faces": [...],
  "rebar_cylinders": [...],
  "bounding_box": {
    "min": [0, 0, 0],
    "max": [300, 500, 6000]
  }
}
```

---

### Streaming Endpoints

#### GET `/stream/batch-design`

Stream batch design results via Server-Sent Events (SSE).

**Query Parameters:**
- `beams`: JSON array of beam specifications

**Example:**
```
GET /stream/batch-design?beams=[{"id":"B1","width":300,"depth":500,"moment":100}]
```

**SSE Events:**
```
event: start
data: {"job_id": "abc123", "total": 5}

event: progress
data: {"completed": 1, "total": 5, "percent": 20}

event: design_result
data: {"beam_id": "B1", "status": "PASS", "flexure": {...}}

event: complete
data: {"completed": 5, "failed": 0, "duration_seconds": 0.45}
```

---

### WebSocket Endpoints

#### WS `/ws/design/{session_id}`

Live design updates via WebSocket.

**Connection:**
```javascript
const ws = new WebSocket("ws://localhost:8000/ws/design/my-session");
```

**Send Message:**
```json
{
  "type": "design_beam",
  "params": {
    "width": 300,
    "depth": 500,
    "moment": 150,
    "fck": 25,
    "fy": 500
  }
}
```

**Receive Message:**
```json
{
  "type": "design_result",
  "latency_ms": 12.5,
  "data": {
    "flexure": {...},
    "shear": {...}
  }
}
```

---

## Error Codes

| Status | Description |
|--------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input format |
| 422 | Validation Error - Input out of range |
| 429 | Rate Limited - Too many requests |
| 500 | Internal Server Error |

---

## Rate Limiting

Default limits (configurable via environment):
- 100 requests per 60 seconds per IP
- WebSocket: 10 messages per second

---

## Client SDKs

Pre-generated clients available in `clients/`:

### Python
```python
from structural_client import StructuralDesignClient

client = StructuralDesignClient("http://localhost:8000")
result = client.design_beam(width=300, depth=500, moment=150, fck=25, fy=500)
print(f"Ast: {result.flexure.ast_required}")
```

### TypeScript
```typescript
import { StructuralDesignClient } from '@structural-lib/api-client';

const client = new StructuralDesignClient('http://localhost:8000');
const result = await client.designBeam({
  width: 300, depth: 500, moment: 150, fck: 25, fy: 500
});
console.log(`Ast: ${result.flexure.ast_required}`);
```

---

## OpenAPI Specification

The full OpenAPI 3.0 specification is available at:
- Live: `GET /openapi.json`
- File: `fastapi_app/openapi_baseline.json`

Generate client SDKs:
```bash
.venv/bin/python scripts/generate_client_sdks.py
```

---

## Related Documents

- [fastapi-deployment-guide.md](../guides/fastapi-deployment-guide.md) - Deployment guide
- [docker-fundamentals-guide.md](../learning/docker-fundamentals-guide.md) - Docker basics
- [api.md](api.md) - Python library API reference
- [v3-infrastructure-gap-analysis.md](../research/v3-infrastructure-gap-analysis.md) - Infrastructure audit
