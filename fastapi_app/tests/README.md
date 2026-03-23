# FastAPI Tests

Tests for the FastAPI backend endpoints, authentication, WebSocket, and streaming.

## Test Files

| File | Scope |
|------|-------|
| `test_security.py` | Security headers, CORS, input sanitization |
| `test_integration.py` | Multi-endpoint integration tests |
| `test_endpoints.py` | Individual endpoint contract tests |
| `test_load.py` | Load/stress testing |
| `test_auth.py` | Authentication and authorization |
| `test_streaming.py` | SSE streaming endpoints |
| `test_websocket.py` | WebSocket live design |

## Running Tests

```bash
cd /path/to/repo && .venv/bin/pytest fastapi_app/tests/ -v
```

## Development

Start the FastAPI server with Docker:

```bash
docker compose up --build          # Production
docker compose -f docker-compose.dev.yml up  # Dev with hot reload
```

API docs available at `http://localhost:8000/docs`.
