# Day 16: FastAPI Advanced — WebSocket, SSE, Batch Processing & File I/O

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** High
**Created:** 2026-04-08
**Last Updated:** 2026-04-08
**Prerequisites:** Day 15 (FastAPI basics — you know router anatomy and Pydantic models)
**Library files:** `fastapi_app/routers/websocket.py`, `fastapi_app/routers/streaming.py`, `fastapi_app/routers/imports.py`, `fastapi_app/routers/export.py`, `fastapi_app/routers/health.py`, `fastapi_app/auth.py`
**IS 456 Clauses:** N/A — this day covers transport protocols, not structural math

---

## What You'll Learn Today

By the end of this module you'll understand:
- WebSocket live design: persistent bidirectional connection for instant feedback as engineers tweak beam parameters
- Server-Sent Events (SSE): streaming progress updates when batch-designing 100+ beams
- The complete import → design → export pipeline
- How `GenericCSVAdapter` auto-detects ETABS, SAFE, STAAD, and generic CSV formats
- Health, readiness, authentication, and rate limiting
- How each protocol (REST, WebSocket, SSE) handles errors differently

---

## Part 1: Three Protocols — When to Use Which

Day 15 covered REST: send a request, get a response. But a real design tool needs two more communication patterns:

| Protocol | Direction | Connection | Our Use Case | Example |
|----------|-----------|------------|--------------|---------|
| **REST** | Request → Response | One-shot | Design a single beam | `POST /api/v1/design/beam` |
| **WebSocket** | Bidirectional | Persistent | Live design — tweak & see results instantly | `ws://localhost:8000/ws/design/{session}` |
| **SSE** | Server → Client | Persistent | Batch progress — "beam 47/200 done" | `GET /stream/batch-design?beams=[...]` |

> **Think of it like...** REST is sending a letter — write your question, mail it, wait for the reply. WebSocket is a phone call — both sides talk freely, the line stays open until you hang up. SSE is a radio broadcast — the station transmits updates and you just listen.

### Why WebSocket for live design?

When an engineer drags a slider to change beam depth from 500mm to 600mm, they want to see the new steel area **instantly** — not click "Submit" and wait. WebSocket keeps a persistent connection open so:

1. Client sends `{"type": "design_beam", "params": {"depth": 600, ...}}`
2. Server computes and sends `{"type": "design_result", "data": {"Ast_mm2": 742}}`
3. No HTTP overhead, no connection setup — just raw messages on an open pipe

The React live-design editor uses this to update results as the user types or drags.

### Why SSE for batch processing?

When you upload a CSV with 200 beams and click "Design All", you need:
- A progress bar (not 30 seconds of silence)
- Individual results as they complete
- The ability to cancel mid-way

SSE gives you a unidirectional stream of events:
```
Server → Client: {"event": "start", "total": 200}
Server → Client: {"event": "design_result", "index": 0, "result": {...}}
Server → Client: {"event": "progress", "completed": 1}
...
Server → Client: {"event": "complete"}
```

**Why not WebSocket for batch too?** SSE is simpler — it's just HTTP, works through proxies that block WebSocket, auto-reconnects on network drops, and the client doesn't need to send messages after the initial request.

---

## Part 2: WebSocket Architecture — The Connection Manager

The WebSocket system has three layers:

```
┌──────────────────────────────────────────────────┐
│  DesignConnectionManager (singleton)              │
│  ┌────────────────┐  ┌────────────────┐          │
│  │ session-001     │  │ session-002     │  ...    │
│  │ WebSocket obj   │  │ WebSocket obj   │         │
│  └────────────────┘  └────────────────┘          │
├──────────────────────────────────────────────────┤
│  Message Router (switch on type)                  │
│  design_beam → handle_design_beam()              │
│  check_beam  → handle_check_beam()               │
│  ping        → pong                               │
│  unknown     → error message                      │
├──────────────────────────────────────────────────┤
│  Handler functions (call structural_lib)          │
│  handle_design_beam() → design_beam_is456()      │
│  handle_check_beam()  → compliance checks        │
└──────────────────────────────────────────────────┘
```

The `DesignConnectionManager` tracks active sessions:

```python
# fastapi_app/routers/websocket.py
class DesignConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        self.active_connections.pop(session_id, None)

    async def send_json(self, session_id: str, data: dict):
        if websocket := self.active_connections.get(session_id):
            await websocket.send_json(data)

manager = DesignConnectionManager()  # Global singleton
```

**Key design decisions:**
- **Session-keyed dict** — each browser tab gets its own session ID, so two engineers can use live design simultaneously
- **Walrus operator** (`if websocket :=`) — only sends if the connection still exists (graceful handling of disconnects)
- **Global singleton** — one manager for all WebSocket connections (fine for single-process; would need Redis for multi-process)

---

## Part 3: WebSocket Message Loop — The Event Dispatcher

The WebSocket endpoint is an infinite loop that dispatches messages by type:

```python
@router.websocket("/ws/design/{session_id}")
async def design_websocket(websocket: WebSocket, session_id: str,
                           token: str | None = Query(None)):
    # Auth check (opt-in) — verify before accepting
    user = await verify_ws_token(websocket, token)
    if token and not user:
        return  # Connection rejected

    await manager.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type", "unknown")

            if message_type == "design_beam":
                await handle_design_beam(session_id, data.get("params", {}))
            elif message_type == "check_beam":
                await handle_check_beam(session_id, data.get("params", {}))
            elif message_type == "ping":
                await manager.send_json(session_id, {
                    "type": "pong",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            else:
                await manager.send_json(session_id, {
                    "type": "error",
                    "message": f"Unknown type: {message_type}"
                })
    except WebSocketDisconnect:
        manager.disconnect(session_id)
```

**The message types:**

| Client sends | Server responds | What happens |
|-------------|----------------|-------------|
| `{"type": "design_beam", "params": {...}}` | `{"type": "design_result", "data": {...}}` | Full beam design via `design_beam_is456()` |
| `{"type": "check_beam", "params": {...}}` | `{"type": "check_result", "data": {...}}` | Compliance checks only |
| `{"type": "ping"}` | `{"type": "pong", "timestamp": "..."}` | Keep-alive heartbeat |
| `{"type": "xyz"}` | `{"type": "error", "message": "Unknown type: xyz"}` | Graceful unknown handling |

**Error handling is different from REST:** There's no HTTP status code on a WebSocket message. Errors are sent as JSON messages with `"type": "error"`. The `sanitize_error()` function from Day 15 is used here too — stack traces never leak to clients.

---

## Part 4: SSE Batch Design — Streaming Progress

When 200 beams need designing, the SSE endpoint streams results one-by-one:

```python
# fastapi_app/routers/streaming.py
@router.get("/batch-design")
async def stream_batch_design(
    request: Request,
    beams: str = Query(..., description="JSON array of beam parameters"),
) -> EventSourceResponse:

    beam_list = json.loads(beams)
    job_id = job_manager.create_job(total_items=len(beam_list))

    async def event_generator():
        yield {"event": "start", "data": json.dumps(
            {"job_id": job_id, "total": len(beam_list)})}

        for i, params in enumerate(beam_list):
            if await request.is_disconnected():
                break
            try:
                result = batch.design_single_beam(params)
                yield {"event": "design_result", "data": json.dumps(
                    {"index": i, "result": result})}
            except Exception as e:
                yield {"event": "error", "data": json.dumps(
                    {"index": i, "error": sanitize_error(e, "batch")})}

            yield {"event": "progress", "data": json.dumps(
                {"completed": i + 1, "total": len(beam_list)})}
            await asyncio.sleep(0)  # Yield control to event loop

        yield {"event": "complete", "data": json.dumps(
            job_manager.get_job(job_id))}

    return EventSourceResponse(event_generator())
```

**Critical details:**

| Line | Why it matters |
|------|---------------|
| `await request.is_disconnected()` | If the user closes the tab, stop wasting CPU on 200 beam designs nobody will see |
| `await asyncio.sleep(0)` | Yield control so the event loop can handle other requests — without this, 200 sequential designs would block the entire server |
| `job_manager.create_job()` | Creates a trackable job ID so the client can query status later |
| `sanitize_error(e, "batch")` | An individual beam failure doesn't crash the entire batch — it emits an error event and continues |

**The event flow diagram:**

```
Client                                      Server
  │                                            │
  │──── GET /stream/batch-design?beams=[...]──▶│
  │                                            │
  │◀── event: start, total: 200 ──────────────│
  │◀── event: design_result, index: 0 ────────│
  │◀── event: progress, completed: 1 ─────────│
  │◀── event: design_result, index: 1 ────────│
  │◀── event: progress, completed: 2 ─────────│
  │       ... (198 more) ...                   │
  │◀── event: complete ───────────────────────│
  │                                            │
```

---

## Part 5: The Complete Import → Design → Export Pipeline

The full batch workflow connects four API endpoints:

```
┌──────────────┐      ┌───────────────┐      ┌──────────────────┐      ┌────────────────┐
│  1. Upload   │─────▶│  2. Import    │─────▶│ 3. Batch Design  │─────▶│  4. Export      │
│  CSV file    │      │  POST /import │      │ GET /stream/     │      │ POST /export/  │
│  (ETABS,     │      │  /csv         │      │ batch-design     │      │ bbs|dxf|report │
│  SAFE, etc.) │      │               │      │                  │      │                │
└──────────────┘      └───────────────┘      └──────────────────┘      └────────────────┘
   File upload         GenericCSVAdapter       SSE stream of            BBS CSV, DXF CAD,
                       auto-detects format     individual results       PDF report download
                       40+ column mappings     + progress events
```

### Step 1: CSV Import with auto-detection

```python
# fastapi_app/routers/imports.py
@router.post("/csv")
async def import_csv(file: UploadFile = File(...)):
    """Auto-detects ETABS, SAFE, STAAD, or Generic CSV format."""
    content = await file.read()
    text = content.decode("utf-8")

    from structural_lib.services.adapters import GenericCSVAdapter
    adapter = GenericCSVAdapter()
    result = adapter.parse(text)  # 40+ column mappings

    beams = [BeamRow(**row) for row in result.beams]
    return CSVImportResponse(
        success=True, message=f"Imported {len(beams)} beams",
        beam_count=len(beams), beams=beams,
        format_detected=result.format_name, warnings=result.warnings,
    )
```

**The import router doesn't parse CSV itself** — it delegates to `GenericCSVAdapter` in `structural_lib`. This adapter handles 40+ column name variations (`"Width"`, `"b"`, `"B_mm"`, `"BEAM_WIDTH"` etc.) and detects whether the file came from ETABS, SAFE, STAAD, or a manual spreadsheet.

### Step 4: File Export with StreamingResponse

```python
# fastapi_app/routers/export.py
@router.post("/bbs")
async def export_bbs(request: ExportBeamRequest):
    bbs_data = generate_bbs(request)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Bar Mark", "Dia (mm)", "Length (mm)", "Qty", "Shape"])
    for row in bbs_data:
        writer.writerow(row)

    safe_name = sanitize_filename(f"BBS_{request.beam_id}")
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}.csv"'},
    )
```

**`sanitize_filename()`** strips path traversal (`..`), null bytes, and special characters. Without this, a malicious `beam_id` like `../../etc/passwd` could cause the server to write files outside the intended directory (CWE-22).

---

## Part 6: Error Handling Across All Three Protocols

Each protocol handles errors differently, but the security invariant is the same: **never expose internal paths or stack traces.**

| Protocol | Error Mechanism | Example |
|----------|----------------|---------|
| **REST** | HTTP status code + JSON body | `422: {"detail": [{"loc": ["body", "width"], "msg": "Input should be > 0"}]}` |
| **WebSocket** | JSON message on the same channel | `{"type": "error", "message": "Invalid beam parameters"}` |
| **SSE** | Error event in the stream | `event: error\ndata: {"index": 5, "error": "Invalid fck value"}` |

**REST errors** (Day 15): Pydantic rejects bad input → 422. Library throws `ValueError` → 422 via handler. Unknown exception → 500 via `sanitize_error()`.

**WebSocket errors**: No HTTP status codes. Errors are JSON messages with `"type": "error"`:
```python
except (ValueError, TypeError) as e:
    await manager.send_json(session_id, {
        "type": "error",
        "message": sanitize_error(e, "live design")
    })
```

**SSE errors**: Individual beam failures emit error events without crashing the batch:
```python
except Exception as e:
    yield {"event": "error", "data": json.dumps(
        {"index": i, "error": sanitize_error(e, "batch")})}
# Continue with next beam — don't abort the batch
```

---

## Part 7: Health, Auth, and Rate Limiting

### Health probes — liveness vs readiness

```python
@router.get("/")
async def health_check() -> HealthStatus:
    return HealthStatus(
        status="healthy", version=__version__,
        timestamp=datetime.now(timezone.utc).isoformat(),
        uptime_seconds=time.time() - _start_time
    )

@router.get("/ready")
async def readiness_check() -> ReadinessStatus:
    lib_ok = False
    try:
        import structural_lib
        lib_ok = True
    except ImportError:
        pass
    return ReadinessStatus(ready=lib_ok, checks={"structural_lib": lib_ok})
```

| Endpoint | Question it answers | Kubernetes usage |
|----------|--------------------|-----------------|
| `/health` | "Is the process alive?" | Liveness probe — restart if it fails |
| `/health/ready` | "Can it do useful work?" | Readiness probe — don't route traffic if it fails |

### Authentication (opt-in)

Auth disabled in dev (`AUTH_ENABLED=false`). When enabled:
- REST: `Authorization: Bearer <token>` header
- WebSocket: `?token=<jwt>` query param (browsers can't set headers on WS)
- `/health`, `/docs` skip auth

### Rate limiting

Global: 120 req/min per IP. Excluded: `/health`, `/docs`, `/ws/`. Batch endpoints have additional protection via FastAPI dependencies.

---

## Part 8: Testing API Protocols

Tests use `pytest` + `httpx` with `ASGITransport` — no real server:

```python
from httpx import AsyncClient, ASGITransport
from fastapi_app.main import app

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_beam_design(client):
    response = await client.post("/api/v1/design/beam", json={
        "width": 300, "depth": 500, "moment": 150, "fck": 25, "fy": 415,
    })
    assert response.status_code == 200
    assert response.json()["success"] is True
```

For WebSocket testing:
```python
from fastapi.testclient import TestClient

def test_websocket_ping():
    client = TestClient(app)
    with client.websocket_connect("/ws/design/test-session") as ws:
        ws.send_json({"type": "ping"})
        response = ws.receive_json()
        assert response["type"] == "pong"
```

---

## Part 9: Hands-On Examples

### WebSocket: Python client

```python
import asyncio, json, websockets

async def live_design():
    async with websockets.connect("ws://localhost:8000/ws/design/session-001") as ws:
        await ws.send(json.dumps({
            "type": "design_beam",
            "params": {"width": 300, "depth": 500, "moment": 150, "fck": 25, "fy": 500}
        }))
        r1 = json.loads(await ws.recv())
        print(f"Ast at d=500: {r1['data']['Ast_mm2']} mm²")

        await ws.send(json.dumps({
            "type": "design_beam",
            "params": {"width": 300, "depth": 600, "moment": 150, "fck": 25, "fy": 500}
        }))
        r2 = json.loads(await ws.recv())
        print(f"Ast at d=600: {r2['data']['Ast_mm2']} mm²")

asyncio.run(live_design())
```

### SSE: JavaScript client

```javascript
const beams = JSON.stringify([
    { id: "B1", width: 300, depth: 500, moment: 100, fck: 25, fy: 500 },
    { id: "B2", width: 300, depth: 500, moment: 150, fck: 25, fy: 500 },
]);
const es = new EventSource(
    `http://localhost:8000/stream/batch-design?beams=${encodeURIComponent(beams)}`
);
es.addEventListener("progress", (e) => {
    const { completed, total } = JSON.parse(e.data);
    console.log(`Progress: ${completed}/${total}`);
});
es.addEventListener("complete", () => { console.log("Done!"); es.close(); });
```

### Import CSV and Export BBS

```bash
# Import
curl -X POST http://localhost:8000/api/v1/import/csv \
  -F "file=@Etabs_CSV/beam_forces.csv" | python -m json.tool

# Export
curl -X POST http://localhost:8000/api/v1/export/bbs \
  -H "Content-Type: application/json" \
  -d '{"beam_id":"B1","width":300,"depth":500,"fck":25,"fy":500,
       "ast_required":942,"moment":150,"shear":75,"span_length":5000}' \
  --output bbs_B1.csv
```

---

## Part 10: Exercises

### Exercise 1: WebSocket live design
1. Install: `.venv/bin/pip install websockets`
2. Start: `./run.sh dev --no-react`
3. Connect to `ws://localhost:8000/ws/design/exercise`
4. Send ping → verify pong
5. Design with depth 500 and 700 — verify deeper beam needs less steel
6. Explain why: $A_{st} \propto \frac{M_u}{d}$

### Exercise 2: Trace the import pipeline
1. Inspect `Etabs_CSV/beam_forces.csv`
2. Import it via curl → what format was detected?
3. How many beams? Any warnings?

### Exercise 3: Error resilience
1. Send unknown WebSocket type — what response?
2. In a 5-beam batch, make beam #3 have `fck: -5` — does the batch abort?
3. Import a non-CSV file — what error?

---

## Part 11: Self-Check Q&A

1. **When do you use WebSocket vs SSE?** Give a concrete scenario for each.
2. **Why check `request.is_disconnected()` in SSE?** What happens without it?
3. **Why does the import router delegate to `GenericCSVAdapter`?**
4. **What does `sanitize_filename()` prevent?** What CWE?
5. **Difference between `/health` and `/health/ready`?** Kubernetes scenario.
6. **Why does WebSocket auth use a query parameter** instead of a header?
7. **What does `await asyncio.sleep(0)` do?** Why is it critical?
8. **How does `ASGITransport` speed up tests?** What does it bypass?
9. **What stops one beam failure from crashing a batch?**
10. **Why is the connection manager a singleton?** What breaks if it's per-request?

---

## Part 12: Things to Know — Deep Insights

### 12.1: WebSocket is not HTTP after the upgrade
The initial WebSocket connection starts as an HTTP GET with `Upgrade: websocket`. After the server accepts, the protocol switches to binary framing. HTTP middleware (CORS, rate limiting) only runs on the initial handshake, not on subsequent messages. A client can send unlimited messages after connecting — rate limiting must be done inside the message loop.

### 12.2: SSE has a 6-connection browser limit
Browsers limit simultaneous SSE connections to the same domain to 6 (HTTP/1.1). If a user opens 7 batch jobs in 7 tabs, the 7th hangs until one finishes. HTTP/2 multiplexes streams, lifting this limit.

### 12.3: `EventSourceResponse` is not built into FastAPI
FastAPI doesn't ship with SSE support. This project uses `sse-starlette`, a third-party library. If you see import errors related to SSE, check that `sse-starlette` is in `requirements.txt`.

### 12.4: WebSocket auth can't use headers
Browsers' WebSocket API (`new WebSocket(url)`) doesn't support custom headers. The workaround is `?token=<jwt>` in the query string — which means the token appears in server logs and URL bars. In production, always use `wss://` (TLS) to encrypt.

### 12.5: `asyncio.sleep(0)` is not a delay
It yields control to the event loop so other coroutines can run. Without it, a 200-beam batch monopolizes the event loop, making the server unresponsive to all other requests.

### 12.6: The `while True` disconnection pattern
The WebSocket loop uses `while True` + `except WebSocketDisconnect`. There's no "on_close" callback — `receive_json()` raises the exception when the client disconnects, breaking the loop.

---

## Part 13: What Can Be Done Better

### 13.1: No WebSocket message validation
REST endpoints validate with Pydantic, but WebSocket messages are raw JSON. Bad values pass through to `design_beam_is456()` and crash instead of returning clean errors. Pydantic models should validate WebSocket messages too.

### 13.2: No reconnection handling
A dropped WebSocket connection loses the session. There's no "resume from last state" — reconnecting creates a new session. The server should persist last design parameters per session ID.

### 13.3: SSE uses GET with query string for beam data
Beam data is JSON in a query string: `GET /batch-design?beams=[{...}]`. For 200 beams, the URL exceeds browser limits (~2000–8000 chars). POST-based SSE would be safer.

### 13.4: No backpressure on SSE
If the server emits events faster than the client consumes them, events queue in memory. For 1000+ beams, this could cause memory issues.

### 13.5: Single-process WebSocket manager
The connection manager stores WebSockets in a Python dict. Multiple uvicorn workers can't share sessions. Production needs Redis pub/sub as the backplane.

---

## Part 14: Innovation Directions

### 14.1: WebSocket multiplexing
One connection handling beam, column, slab, and footing design via the `"type"` field — reduces connection overhead and simplifies the client.

### 14.2: gRPC for internal services
Protocol Buffers would be faster and more compact for server-to-server communication in a microservice architecture.

### 14.3: Binary WebSocket frames for 3D geometry
The geometry endpoint returns vertex/face arrays as JSON. Binary formats (MessagePack, Float32Array) would be 3-5× smaller and faster to parse in Three.js.

### 14.4: Server-push design warnings
Instead of waiting for explicit requests, the WebSocket could proactively warn when $x_u/d$ approaches the limit — "Consider increasing beam depth."

### 14.5: Collaborative design via WebSocket rooms
Multiple engineers on the same building, with changes broadcast via rooms (like Figma or Google Docs).

---

## Part 15: Next Repo Must-Add

### Concrete items

1. **WebSocket message validation** — Pydantic models for all message types
2. **Session recovery** — Persist last design state per session ID
3. **POST-based SSE** — Replace GET query string with POST body for batch
4. **Redis connection manager** — Multi-worker WebSocket support
5. **In-loop rate limiting** — Per-session message throttling for WebSocket
6. **Binary frames** — MessagePack or Float32Array for 3D geometry data
7. **Batch cancellation API** — Cancel running jobs by ID, not just by disconnecting

### Day-1 checklist for a new real-time endpoint

```
□ 1. Choose protocol: WebSocket (bidirectional) vs SSE (server-push) vs REST (one-shot)
□ 2. Define message schema as Pydantic models — validate incoming AND outgoing
□ 3. Add connection/session tracking to the connection manager
□ 4. Use sanitize_error() for ALL error paths — no stack traces
□ 5. Check request.is_disconnected() in streaming loops
□ 6. Add asyncio.sleep(0) in tight loops — yield to event loop
□ 7. Write tests: happy path, error path, and disconnection
□ 8. Document message protocol (types, fields, error shapes) in docstring
□ 9. Add rate limiting appropriate to the protocol
□ 10. Load test: 10 connections, 100-beam batch — does it stay responsive?
```

---

## 📎 References

- [FastAPI WebSocket docs](https://fastapi.tiangolo.com/advanced/websockets/)
- [SSE specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [sse-starlette](https://github.com/sysid/sse-starlette) — SSE library for FastAPI
- [websockets (Python)](https://websockets.readthedocs.io/) — Client library
- [CWE-22: Path Traversal](https://cwe.mitre.org/data/definitions/22.html) — Why `sanitize_filename` exists
- `fastapi_app/routers/websocket.py` — WebSocket endpoint + connection manager
- `fastapi_app/routers/streaming.py` — SSE batch design + job tracking
- `fastapi_app/routers/imports.py` — CSV/ETABS/STAAD import
- `fastapi_app/routers/export.py` — BBS, DXF, PDF download
- `fastapi_app/routers/health.py` — Health and readiness probes
- **Previous:** Day 15 covers FastAPI basics (routers, Pydantic, CORS, error handling)
- **Next:** Day 17 covers the React frontend architecture
