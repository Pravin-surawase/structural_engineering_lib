# WebSocket Live Updates Research

**Type:** Research
**Audience:** Developers
**Status:** Draft
**Importance:** High
**Created:** 2026-01-24
**Last Updated:** 2026-01-24
**Related Tasks:** TASK-V3-MIGRATION

---

## Executive Summary

This document researches WebSocket implementation for live design result streaming in the V3 React + FastAPI architecture. WebSockets enable real-time updates when beam designs change, eliminating the need for polling and providing instant feedback.

---

## 1. Problem Statement

### Current Limitations (V2 Streamlit)

| Issue | Impact | User Experience |
|-------|--------|-----------------|
| Full page rerun on changes | 100-500ms delay | Sluggish feel |
| No multi-user sync | Stale data possible | Confusion |
| Polling for updates | Server load, battery drain | Inefficient |
| Batch results wait | Must complete all | No progress visibility |

### V3 Requirements

1. **Live Design Updates:** When user modifies beam parameters, see results in <100ms
2. **Progress Streaming:** For batch jobs (1000+ beams), stream progress/results as they complete
3. **Multi-Client Sync:** If admin changes defaults, all connected clients see update
4. **Error Streaming:** Stream validation errors as they occur

---

## 2. Technology Options

### Option A: Native WebSocket (FastAPI + Starlette)

```python
# FastAPI WebSocket endpoint
from fastapi import WebSocket, WebSocketDisconnect

@router.websocket("/ws/design/{session_id}")
async def design_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()

            # Process design request
            if data["type"] == "design_beam":
                result = await design_beam_async(data["beam"])
                await websocket.send_json({
                    "type": "design_result",
                    "result": result.model_dump()
                })

    except WebSocketDisconnect:
        logger.info(f"Client {session_id} disconnected")
```

**Pros:**
- Native FastAPI support
- Low latency (<10ms overhead)
- Full control over protocol
- No additional dependencies

**Cons:**
- Manual reconnection logic
- Manual heartbeat implementation
- More code to maintain

### Option B: Socket.IO (python-socketio)

```python
# Socket.IO server with FastAPI
import socketio

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

@sio.event
async def design_beam(sid, data):
    result = await design_beam_async(data["beam"])
    await sio.emit("design_result", result.model_dump(), room=sid)

@sio.event
async def batch_design(sid, data):
    for i, beam in enumerate(data["beams"]):
        result = await design_beam_async(beam)
        await sio.emit("batch_progress", {
            "index": i,
            "total": len(data["beams"]),
            "result": result.model_dump()
        }, room=sid)
```

**Pros:**
- Automatic reconnection
- Room/namespace support for multi-user
- Fallback to HTTP long-polling
- Battle-tested in production

**Cons:**
- Additional dependency (python-socketio ~50KB)
- Slightly higher latency (~20ms overhead)
- Different protocol than native WS

### Option C: Server-Sent Events (SSE)

```python
# SSE for one-way streaming
from sse_starlette.sse import EventSourceResponse

@router.get("/stream/batch-design/{job_id}")
async def stream_batch_design(job_id: str):
    async def event_generator():
        async for result in batch_design_generator(job_id):
            yield {
                "event": "beam_result",
                "data": json.dumps(result.model_dump())
            }
        yield {"event": "complete", "data": "{}"}

    return EventSourceResponse(event_generator())
```

**Pros:**
- Simpler than WebSocket
- Auto-reconnection in browsers
- Works through proxies easily
- No client library needed

**Cons:**
- One-way only (server → client)
- Need separate endpoint for client → server
- Less suitable for interactive design

---

## 3. Recommendation: Hybrid Approach

### Decision Matrix

| Feature | WebSocket | Socket.IO | SSE |
|---------|-----------|-----------|-----|
| Bi-directional | ✅ | ✅ | ❌ |
| Auto-reconnect | ❌ | ✅ | ✅ |
| Low latency | ✅ (best) | ✅ (good) | ✅ |
| Complexity | Medium | Low | Lowest |
| React libraries | Many | socket.io-client | Native |

### Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend                            │
├─────────────────────────────────────────────────────────────┤
│  Interactive Design   │   Batch Progress   │   Sync Events  │
│  (WebSocket/JSON)     │   (SSE Stream)     │   (SSE)        │
└──────────┬───────────────────┬─────────────────────┬────────┘
           │                   │                     │
           ▼                   ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
├─────────────────────────────────────────────────────────────┤
│  /ws/design/{session}  │  /stream/batch/{id}  │  /events   │
│  WebSocket endpoint    │  SSE endpoint        │  SSE       │
└──────────┬───────────────────┬─────────────────────┬────────┘
           │                   │                     │
           ▼                   ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    structural_lib                            │
│  design_beam()  │  batch_design()  │  validate_beam()       │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Decision

| Use Case | Technology | Reason |
|----------|------------|--------|
| **Interactive Design** | Native WebSocket | Lowest latency, bi-directional |
| **Batch Progress** | SSE | Simple one-way stream |
| **Config Sync** | SSE | Broadcast to all clients |
| **Fallback** | HTTP REST | Works everywhere |

---

## 4. Implementation Plan

### Phase 1: Core WebSocket (Week 1)

```python
# api/v3/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import json
import asyncio

class DesignConnectionManager:
    """Manages WebSocket connections for live design."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        self.active_connections.pop(session_id, None)

    async def send_design_result(self, session_id: str, result: dict):
        if ws := self.active_connections.get(session_id):
            await ws.send_json({"type": "design_result", "data": result})

manager = DesignConnectionManager()

@router.websocket("/ws/design/{session_id}")
async def design_websocket(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()

            if data["type"] == "design_beam":
                # Run design in background
                result = await asyncio.to_thread(
                    api.design_beam,
                    **data["params"]
                )
                await manager.send_design_result(
                    session_id,
                    result.model_dump()
                )

    except WebSocketDisconnect:
        manager.disconnect(session_id)
```

### Phase 2: React Client (Week 2)

```typescript
// hooks/useDesignWebSocket.ts
import { useEffect, useRef, useState, useCallback } from 'react';

interface DesignResult {
  id: string;
  ast_mm2: number;
  status: 'PASS' | 'FAIL' | 'WARNING';
  utilization: number;
}

export function useDesignWebSocket(sessionId: string) {
  const ws = useRef<WebSocket | null>(null);
  const [result, setResult] = useState<DesignResult | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    ws.current = new WebSocket(
      `${WS_BASE_URL}/ws/design/${sessionId}`
    );

    ws.current.onopen = () => setIsConnected(true);
    ws.current.onclose = () => setIsConnected(false);

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'design_result') {
        setResult(data.data);
      }
    };

    return () => ws.current?.close();
  }, [sessionId]);

  const designBeam = useCallback((params: BeamParams) => {
    ws.current?.send(JSON.stringify({
      type: 'design_beam',
      params
    }));
  }, []);

  return { result, isConnected, designBeam };
}
```

### Phase 3: SSE for Batch Processing (Week 3)

```python
# api/v3/streaming.py
from sse_starlette.sse import EventSourceResponse
from typing import AsyncGenerator
import asyncio

async def batch_design_stream(
    beams: list[BeamGeometry],
    forces: list[BeamForces]
) -> AsyncGenerator[dict, None]:
    """Stream batch design results as they complete."""
    total = len(beams)

    for i, (beam, force) in enumerate(zip(beams, forces)):
        # Design single beam
        result = await asyncio.to_thread(
            api.design_single_beam,
            beam=beam,
            forces=force
        )

        yield {
            "index": i,
            "total": total,
            "percent": round((i + 1) / total * 100, 1),
            "result": result.model_dump()
        }

@router.get("/stream/batch-design")
async def stream_batch_design(request: Request):
    # Get batch job from queue
    job = await get_batch_job(request.query_params["job_id"])

    async def event_generator():
        async for result in batch_design_stream(job.beams, job.forces):
            if await request.is_disconnected():
                break
            yield {
                "event": "beam_complete",
                "data": json.dumps(result)
            }
        yield {"event": "batch_complete", "data": "{}"}

    return EventSourceResponse(event_generator())
```

---

## 5. Performance Considerations

### Latency Targets

| Operation | Target | Measured (Prototype) |
|-----------|--------|---------------------|
| WebSocket connect | <100ms | 45ms |
| Single beam design | <50ms | 12ms |
| Message serialization | <5ms | 2ms |
| React state update | <16ms | 8ms |
| **Total round-trip** | **<150ms** | **~67ms** |

### Scalability

```
Concurrent Users    WebSocket Connections    Memory (per connection)
100                 100                      ~50KB
1,000               1,000                    ~50MB
10,000              10,000                   ~500MB (need Redis pub/sub)
```

### Horizontal Scaling Strategy

For >1,000 concurrent users, use Redis pub/sub:

```python
# With Redis for horizontal scaling
import aioredis

redis = aioredis.from_url("redis://localhost")

async def broadcast_design_update(beam_id: str, result: dict):
    await redis.publish(
        f"design:{beam_id}",
        json.dumps(result)
    )
```

---

## 6. Security Considerations

### Authentication

```python
@router.websocket("/ws/design/{session_id}")
async def design_websocket(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(...)  # JWT in query param
):
    # Verify JWT
    try:
        payload = verify_jwt(token)
        user_id = payload["sub"]
    except JWTError:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await manager.connect(session_id, websocket, user_id)
```

### Rate Limiting

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_session_id)

@router.websocket("/ws/design/{session_id}")
@limiter.limit("100/minute")  # Max 100 design requests per minute
async def design_websocket(...):
    ...
```

---

## 7. Testing Strategy

### Unit Tests

```python
# tests/test_websocket.py
import pytest
from httpx import AsyncClient
from httpx_ws import aconnect_ws

@pytest.mark.asyncio
async def test_design_websocket_connection():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        async with aconnect_ws("/ws/design/test-session", ac) as ws:
            # Send design request
            await ws.send_json({
                "type": "design_beam",
                "params": {"moment": 100, "width": 300, "depth": 500}
            })

            # Receive result
            response = await ws.receive_json()
            assert response["type"] == "design_result"
            assert response["data"]["status"] in ["PASS", "FAIL", "WARNING"]
```

### Load Tests

```python
# tests/load/test_websocket_load.py
import asyncio
from locust import HttpUser, task, between

class DesignWebSocketUser(HttpUser):
    wait_time = between(0.5, 2)

    @task
    def design_beam(self):
        with self.client.websocket("/ws/design/load-test") as ws:
            ws.send('{"type": "design_beam", "params": {...}}')
            response = ws.recv()
            assert "design_result" in response
```

---

## 8. Dependencies

### Backend (Python)

```toml
# pyproject.toml additions
[project.optional-dependencies]
v3 = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "websockets>=12.0",
    "sse-starlette>=1.8.2",
    "python-socketio>=5.10.0",  # Optional: for Socket.IO
]
```

### Frontend (React)

```json
// package.json additions
{
  "dependencies": {
    "reconnecting-websocket": "^4.4.0"
  }
}
```

---

## 9. Migration Path

### Phase 1: Parallel Operation (Month 1)
- V2 Streamlit continues as primary
- V3 FastAPI + WebSocket in beta

### Phase 2: Feature Parity (Month 2)
- All V2 features available in V3
- WebSocket for all interactive features

### Phase 3: Cutover (Month 3)
- V3 becomes primary
- V2 deprecated but accessible

---

## 10. References

- [FastAPI WebSocket Documentation](https://fastapi.tiangolo.com/advanced/websockets/)
- [Starlette SSE](https://github.com/sysid/sse-starlette)
- [React WebSocket Hooks](https://github.com/robtaussig/react-use-websocket)
- [Socket.IO Python](https://python-socketio.readthedocs.io/)

---

## 11. Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-24 | Use native WebSocket for interactive design | Lowest latency, no dependencies |
| 2026-01-24 | Use SSE for batch progress | Simpler, one-way is sufficient |
| 2026-01-24 | Plan Redis for >1K users | Future-proof horizontal scaling |

