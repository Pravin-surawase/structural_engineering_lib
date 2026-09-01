# FastAPI Backend

REST API + WebSocket bridge between the React frontend and the Python `structural_lib`.

## Quick Start

```bash
docker compose up --build                        # Production at :8000
docker compose -f docker-compose.dev.yml up      # Dev with hot reload
```

API docs: `http://localhost:8000/docs` (auto-generated OpenAPI).

## Live-route security

The ETABS bridge is offline-only by default: readiness and retained-evidence
beam-demand routes remain mounted, while every COM-attaching route is absent
from both routing and OpenAPI. To enable live read/attach routes, set
`ETABS_LIVE_BRIDGE_ENABLED=true` together with `HOST=127.0.0.1`,
`AUTH_ENABLED=true`, and a non-default JWT secret. Calls must originate from a
loopback peer and carry the `etabs:live:read` scope. The transiently mutating
beam-pilot route additionally requires `ETABS_LIVE_MUTATION_ENABLED=true` and
the `etabs:live:mutate` scope. Public/container profiles keep both flags false.

`/ws/design/{session_id}` also requires a JWT query token with the `design`
scope. Missing, invalid, or wrongly scoped tokens are rejected before the
server accepts the WebSocket.

## Structure

```
fastapi_app/
├── main.py          # App entry point, middleware, CORS
├── config.py        # Settings and environment config
├── auth.py          # Authentication (API key)
├── models/          # Pydantic request/response models
├── routers/         # API route handlers (13 routers)
├── tests/           # Endpoint, auth, WebSocket, load tests
└── examples/        # Example request payloads
```

## Routers (13)

| Router | Endpoint Prefix | Purpose |
|--------|----------------|--------|
| design | `/api/v1/design` | Beam design (IS 456) |
| column | `/api/v1/design/column` | Column design (IS 456) |
| detailing | `/api/v1/detailing` | Rebar detailing |
| analysis | `/api/v1/analysis` | Structural analysis |
| geometry | `/api/v1/geometry` | 3D rebar/stirrup geometry |
| imports | `/api/v1/import` | CSV/ETABS import |
| insights | `/api/v1/insights` | Design suggestions, checks |
| optimization | `/api/v1/optimization` | Cross-section optimization |
| rebar | `/api/v1/rebar` | Rebar editing/validation |
| export | `/api/v1/export` | BBS/DXF/report export |
| streaming | `/api/v1/streaming` | SSE streaming |
| websocket | `/ws/design` | JWT-authenticated WebSocket live updates |
| etabs-bridge | `/api/v1/etabs-bridge/v1` | Offline evidence plus opt-in loopback live ETABS access |
| health | `/api/v1/health` | Health check + diagnostics |

## Testing

```bash
.venv/bin/pytest fastapi_app/tests/ -v
```
