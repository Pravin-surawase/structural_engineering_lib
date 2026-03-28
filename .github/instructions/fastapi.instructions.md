---
applyTo: "**/fastapi_app/**"
---

# FastAPI Backend Rules

## Check existing routes before adding new ones

```bash
grep -r "@router" fastapi_app/routers/ | head -30
```

Key existing routes (12 routers, 38 endpoints):
- `POST /api/v1/design/beam` — Beam design
- `POST /api/v1/import/csv` — CSV import with adapters
- `POST /api/v1/geometry/beam/full` — 3D rebar/stirrup positions
- `POST /api/v1/detailing/beam` — Rebar detailing
- `POST /api/v1/insights/dashboard` — Batch analytics
- `POST /api/v1/export/bbs|dxf|report` — File downloads
- `/ws/design/{session}` — WebSocket live updates
- `GET /health` — Health check
- API docs at `/docs` (auto-generated OpenAPI)

## FastAPI calls structural_lib directly

Routers import from `structural_lib` — they don't duplicate logic.
Never reimplement core math in FastAPI routers.

## Test with Docker

> **Prerequisite:** Start Colima first: `colima start --cpu 4 --memory 4`

```bash
docker compose up --build                        # Production at :8000/docs
docker compose -f docker-compose.dev.yml up      # Dev with hot reload
```

## Production code requires PR

Never direct-commit changes to `fastapi_app/`. Use PR workflow.
