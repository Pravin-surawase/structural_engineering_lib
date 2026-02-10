---
description: Rules for editing FastAPI backend files
globs: fastapi_app/**
---

# FastAPI Backend Rules

## Check existing routes before adding new ones

```bash
grep -r "@router" fastapi_app/routers/ | head -30
```

Key existing routes:
- `POST /api/v1/import/csv` — CSV import with adapters
- `POST /api/v1/geometry/beam/full` — 3D rebar/stirrup positions
- `POST /api/v1/design/beam` — Beam design
- `/ws/design/{session}` — WebSocket live updates
- API docs at `/docs` (auto-generated OpenAPI)

## FastAPI calls structural_lib directly

Routers import from `structural_lib` — they don't duplicate logic.

## Test with Docker

```bash
docker compose up --build                        # Production
docker compose -f docker-compose.dev.yml up      # Dev with hot reload
```

## Production code requires PR

Never direct-commit changes to `fastapi_app/`. Use PR workflow.
