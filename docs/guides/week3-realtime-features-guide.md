# Week 3 FastAPI Real-Time Features: Learning Guide

**Type:** Learning
**Audience:** Developers
**Status:** Production Ready
**Importance:** High
**Created:** 2026-01-24
**Last Updated:** 2026-01-24
**Related Tasks:** TASK-WS-001, TASK-AUTH-001

---

## Overview

This document explains the real-time communication features implemented in Week 3 of the FastAPI migration: **WebSocket** for live design sessions, **Server-Sent Events (SSE)** for batch processing, **JWT authentication** for security, and **rate limiting** for abuse prevention.

---

## Table of Contents

1. [WebSocket vs SSE: When to Use Which](#websocket-vs-sse-when-to-use-which)
2. [WebSocket Implementation](#websocket-implementation)
3. [Server-Sent Events (SSE) Implementation](#server-sent-events-sse-implementation)
4. [JWT Authentication](#jwt-authentication)
5. [Rate Limiting](#rate-limiting)
6. [Testing Real-Time Endpoints](#testing-real-time-endpoints)
7. [Client Examples](#client-examples)
8. [Best Practices](#best-practices)

---

## WebSocket vs SSE: When to Use Which

| Feature | WebSocket | SSE |
|---------|-----------|-----|
| Direction | Bidirectional | Server → Client only |
| Protocol | WS/WSS | HTTP/HTTPS |
| Reconnection | Manual | Built-in auto-reconnect |
| Complexity | Higher | Lower |
| Use Case | Interactive sessions | Progress updates, notifications |

### Our Design Decisions

- **WebSocket** (`/ws/design/{session_id}`): For interactive beam design where the user modifies parameters and gets instant results.
- **SSE** (`/stream/batch-design`): For batch processing where user submits multiple beams and receives progress updates.

---

## WebSocket Implementation

### Endpoint: `/ws/design/{session_id}`

Location: [fastapi_app/routers/websocket.py](../../fastapi_app/routers/websocket.py)

```python
@router.websocket("/ws/design/{session_id}")
async def websocket_design_endpoint(
    websocket: WebSocket,
    session_id: str,
    token: str | None = Query(None),  # JWT auth
):
    await websocket.accept()

    # Process messages
    while True:
        data = await websocket.receive_json()
        result = await process_design_request(data)
        await websocket.send_json(result)
```

### Message Protocol

**Client → Server:**
```json
{
  "action": "design",
  "beam": {
    "width": 300,
    "depth": 450,
    "length": 5000,
    "Mu": 150.0,
    "fck": 25,
    "fy": 500
  }
}
```

**Server → Client:**
```json
{
  "type": "design_result",
  "session_id": "abc123",
  "beam": {...},
  "result": {
    "Ast_required": 785.0,
    "bars_provided": "3-16φ",
    "status": "SUCCESS"
  },
  "timestamp": "2026-01-24T10:30:00Z"
}
```

### Connection Manager

The `ConnectionManager` class handles multiple connections:

```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    async def broadcast(self, session_id: str, message: dict):
        for ws in self.active_connections.get(session_id, []):
            await ws.send_json(message)
```

---

## Server-Sent Events (SSE) Implementation

### Endpoint: `/stream/batch-design`

Location: [fastapi_app/routers/streaming.py](../../fastapi_app/routers/streaming.py)

SSE uses standard HTTP with a special `text/event-stream` content type.

```python
from sse_starlette.sse import EventSourceResponse

@router.post("/stream/batch-design")
async def batch_design_sse(request: Request) -> EventSourceResponse:
    async def event_generator():
        yield {"event": "start", "data": json.dumps({"job_id": job_id})}

        for i, beam in enumerate(beams):
            result = await process_beam(beam)
            yield {
                "event": "progress",
                "data": json.dumps({"current": i + 1, "total": len(beams)})
            }
            yield {
                "event": "design_result",
                "data": json.dumps(result)
            }

        yield {"event": "complete", "data": json.dumps({"status": "done"})}

    return EventSourceResponse(event_generator())
```

### Event Types

| Event | When | Payload |
|-------|------|---------|
| `start` | Job begins | `{job_id, total_beams}` |
| `progress` | Each beam | `{current, total, percent}` |
| `design_result` | Design complete | `{beam, result}` |
| `error` | Failure | `{beam_index, error}` |
| `complete` | All done | `{status, summary}` |

### Job Tracking

The `BatchJobManager` tracks in-progress jobs:

```python
class BatchJobManager:
    def __init__(self):
        self.jobs: dict[str, BatchJob] = {}

    def create_job(self, beams: list[dict]) -> str:
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = BatchJob(
            job_id=job_id,
            total_beams=len(beams),
            status="pending"
        )
        return job_id

    def update_progress(self, job_id: str, completed: int):
        self.jobs[job_id].completed_beams = completed
```

---

## JWT Authentication

### Overview

Location: [fastapi_app/auth.py](../../fastapi_app/auth.py)

We use JSON Web Tokens (JWT) for stateless authentication:

1. Client obtains token (via login endpoint or external auth)
2. Client includes token in requests
3. Server validates token on each request

### Token Structure

```
Header.Payload.Signature
```

Payload contains:
```json
{
  "sub": "user123",        // User ID
  "email": "user@example.com",
  "scopes": ["design", "analyze"],
  "exp": 1706097600       // Expiration timestamp
}
```

### Creating Tokens

```python
from fastapi_app.auth import create_access_token
from datetime import timedelta

token = create_access_token(
    data={
        "sub": "user123",
        "email": "user@example.com",
        "scopes": ["design"]
    },
    expires_delta=timedelta(hours=1)
)
```

### Protecting REST Endpoints

```python
from fastapi_app.auth import require_auth, User

@router.get("/protected")
async def protected_endpoint(user: User = Depends(require_auth)):
    return {"message": f"Hello, {user.email}"}
```

### Protecting WebSocket Endpoints

```python
from fastapi_app.auth import verify_ws_token

@router.websocket("/ws/design/{session}")
async def ws_endpoint(
    websocket: WebSocket,
    session: str,
    token: str | None = Query(None),
):
    user = await verify_ws_token(websocket, token)
    if not user:
        return  # Connection closed by verify_ws_token

    await websocket.accept()
    # ... continue with authenticated session
```

### Client Usage

**REST API:**
```bash
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/v1/protected
```

**WebSocket:**
```
ws://localhost:8000/ws/design/session123?token=<token>
```

---

## Rate Limiting

### Overview

Rate limiting prevents API abuse by limiting requests per client per time window.

### Configuration

```python
RATE_LIMIT_REQUESTS = 100  # requests per window
RATE_LIMIT_WINDOW_SECONDS = 60  # 1 minute window
```

### Usage

```python
from fastapi_app.auth import check_rate_limit

@router.get("/endpoint")
async def endpoint(
    _: None = Depends(check_rate_limit)
):
    return {"data": "..."}
```

### Response Headers

Rate limit info is returned in headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Window: 60
X-RateLimit-Reset: 1706097660  (when limit resets)
```

### 429 Response

When rate limit exceeded:

```json
{
  "detail": "Rate limit exceeded. Please slow down."
}
```

---

## Testing Real-Time Endpoints

### WebSocket Tests

```python
from fastapi.testclient import TestClient

def test_websocket_design():
    client = TestClient(app)

    with client.websocket_connect("/ws/design/test123") as ws:
        ws.send_json({"action": "design", "beam": {...}})
        response = ws.receive_json()
        assert response["type"] == "design_result"
```

### SSE Tests

```python
import httpx

async def test_sse_batch():
    async with httpx.AsyncClient(app=app) as client:
        async with client.stream(
            "POST",
            "/stream/batch-design",
            json={"beams": [...]},
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    data = json.loads(line[5:])
                    assert "job_id" in data
```

---

## Client Examples

### Python Client

Location: [fastapi_app/examples/test_client.py](../../fastapi_app/examples/test_client.py)

```python
import asyncio
import httpx
import websockets

async def test_websocket():
    uri = "ws://localhost:8000/ws/design/session123"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({
            "action": "design",
            "beam": {"width": 300, "depth": 450, ...}
        }))
        response = await ws.recv()
        print(json.loads(response))

async def test_sse():
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            "http://localhost:8000/stream/batch-design",
            json={"beams": [...]},
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    print(json.loads(line[5:]))
```

### JavaScript Client

```javascript
// WebSocket
const ws = new WebSocket("ws://localhost:8000/ws/design/session123?token=xxx");
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("Design result:", data);
};
ws.send(JSON.stringify({action: "design", beam: {...}}));

// SSE
const eventSource = new EventSource("/stream/batch-design");
eventSource.addEventListener("design_result", (event) => {
    const result = JSON.parse(event.data);
    console.log("Beam result:", result);
});
```

---

## Best Practices

### 1. Use Appropriate Protocol

- **WebSocket**: Interactive, low-latency, bidirectional
- **SSE**: Simple progress updates, auto-reconnect
- **REST**: One-off requests, simple CRUD

### 2. Handle Disconnections

```python
try:
    while True:
        data = await websocket.receive_json()
        result = await process(data)
        await websocket.send_json(result)
except WebSocketDisconnect:
    manager.disconnect(session_id, websocket)
```

### 3. Validate Input

Always validate incoming WebSocket/SSE data:

```python
from pydantic import ValidationError

try:
    request = BeamDesignRequest(**data)
except ValidationError as e:
    await websocket.send_json({"type": "error", "errors": e.errors()})
```

### 4. Add Timeouts

```python
async def with_timeout(coro, timeout: float = 30.0):
    return await asyncio.wait_for(coro, timeout=timeout)
```

### 5. Secure Endpoints

- Always use JWT in production
- Never expose secrets in code
- Use HTTPS/WSS in production
- Rate limit public endpoints

---

## Files Reference

| File | Purpose |
|------|---------|
| [fastapi_app/routers/websocket.py](../../fastapi_app/routers/websocket.py) | WebSocket endpoint |
| [fastapi_app/routers/streaming.py](../../fastapi_app/routers/streaming.py) | SSE batch endpoint |
| [fastapi_app/auth.py](../../fastapi_app/auth.py) | JWT + rate limiting |
| [fastapi_app/examples/test_client.py](../../fastapi_app/examples/test_client.py) | Python demo client |
| [fastapi_app/tests/test_websocket.py](../../fastapi_app/tests/test_websocket.py) | WebSocket tests |
| [fastapi_app/tests/test_streaming.py](../../fastapi_app/tests/test_streaming.py) | SSE tests |
| [fastapi_app/tests/test_auth.py](../../fastapi_app/tests/test_auth.py) | Auth tests |

---

## Summary

Week 3 added real-time capabilities to our FastAPI backend:

1. **WebSocket** for interactive beam design sessions
2. **SSE** for batch processing with progress updates
3. **JWT authentication** for secure access
4. **Rate limiting** to prevent abuse

All features have comprehensive tests and work together to provide a robust, production-ready API.
