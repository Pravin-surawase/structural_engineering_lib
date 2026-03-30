# Mac Mini Migration — Issues & Solutions

**Type:** Reference
**Audience:** All Agents
**Status:** Approved
**Importance:** High
**Created:** 2026-03-27
**Last Updated:** 2026-03-27 (Session 103 — uvicorn IPv6 fix)

> Tracks every issue found after migrating from the old Mac to the new Mac Mini (M-series, Homebrew, Colima).
> **Why?** So the next time we set up a machine (or debug a "it worked before" issue), we have instant answers.

---

## Issues Found & Fixed

### 1. React app won't load in browser (localhost:5173 not reachable)
| | |
|---|---|
| **Symptom** | Browser shows "This site can't be reached" or blank page. `curl` from terminal works. Console tab empty. |
| **Root cause** | Vite dev server binds to **IPv6 only** (`::1`) by default. Browser tries **IPv4** (`127.0.0.1`) → connection refused. |
| **Why after migration** | New macOS / network stack defaults may prefer IPv6 loopback differently than the old machine. |
| **Fix** | Added `server: { host: '0.0.0.0' }` to `react_app/vite.config.ts` — binds to all interfaces (IPv4 + IPv6). |
| **File changed** | `react_app/vite.config.ts` |

### 2. "Sample Building" button does nothing
| | |
|---|---|
| **Symptom** | Clicking "Try our sample building (154 beams)" on mode select page — nothing visible happens. |
| **Root cause** | Two bugs: (1) Button only called `navigate("/import")` without triggering data load. (2) React StrictMode double-executes useEffect — first run strips `?sample=true` from URL, second run finds it gone and skips. |
| **Why after migration** | Not migration-specific — pre-existing bugs, first noticed during post-migration testing. |
| **Fix** | (1) Changed to `navigate("/import?sample=true")`. (2) Added `useRef` guard (`sampleLoadedRef`) in ImportView's `useEffect` to prevent StrictMode double-execution from aborting the API call. |
| **Files changed** | `react_app/src/components/pages/ModeSelectPage.tsx`, `react_app/src/components/import/ImportView.tsx` |
| **Debug steps tried** | Verified API works (`curl /api/v1/import/sample` → 153 beams), checked CORS headers, checked routing, traced lazy-load Suspense flow, identified StrictMode as root cause of silent abort. |

### 3. FastAPI backend not running → CSV import fails silently
| | |
|---|---|
| **Symptom** | Import page shows spinner briefly, then error "Cannot connect to backend server". Sample data button does nothing. |
| **Root cause** | FastAPI / uvicorn wasn't started. React app needs the backend on :8000 for all API calls. |
| **Why after migration** | No auto-start configured on new machine. Previous machine may have had background processes. |
| **Fix** | Start backend first: `.venv/bin/uvicorn fastapi_app.main:app --reload --port 8000`. Added better error message in ImportView. |
| **Files changed** | `react_app/src/components/import/ImportView.tsx` (error messaging), `react_app/src/hooks/useCSVImport.ts` (null guards) |

### 4. Docker "permission denied" on `docker ps`
| | |
|---|---|
| **Symptom** | `docker ps` gives "permission denied" or "Cannot connect to the Docker daemon". |
| **Root cause** | Colima (Docker runtime) was installed but not running. Docker CLI needs a running VM to connect to. |
| **Why after migration** | New Mac Mini uses Colima (not Docker Desktop). Colima VM needs explicit `colima start`. |
| **Fix** | Run `colima start --cpu 4 --memory 4` before any `docker` command. First run downloads ~300MB VM image. |
| **Files changed** | Documented in `agent-bootstrap.md`, `CLAUDE.md`, `AGENTS.md`, `copilot-instructions.md` |

### 5. `python` / `uvicorn` commands use wrong Python (system 3.9)
| | |
|---|---|
| **Symptom** | `ModuleNotFoundError` for structural_lib, numpy, etc. `python --version` shows 3.9.6. |
| **Root cause** | System Python at `/usr/bin/python3` is 3.9. Project needs 3.11 from `.venv`. |
| **Why after migration** | New machine has clean macOS with default system Python. Venv must be activated per-terminal. |
| **Fix** | Always `source .venv/bin/activate` first, or use `.venv/bin/python` / `.venv/bin/uvicorn` by full path. |
| **Files changed** | Documented in bootstrap §5 "Start Fresh" section |

### 6. Colima VM download fails (network connection reset)
| | |
|---|---|
| **Symptom** | `colima start` downloads Ubuntu VM image but fails at ~16-24% with "connection reset". |
| **Root cause** | Slow/unstable network downloading ~300MB file from GitHub releases. |
| **Why after migration** | First-time Colima setup on new machine requires this download. |
| **Fix** | `colima delete -f && colima start` to retry. Reduce resources: `--cpu 2 --memory 2 --disk 20`. Succeeded on 3rd attempt. |
| **Files changed** | Documented in bootstrap troubleshooting table |

---

## Quick Reference — Startup Sequence

```bash
# 1. Activate venv
cd /Users/pravinsurawase/VS_code_project/structural_engineering_lib
source .venv/bin/activate

# 2. Kill old processes
lsof -ti :8000 | xargs kill -9 2>/dev/null
lsof -ti :5173 | xargs kill -9 2>/dev/null

# 3. Start FastAPI (Terminal 1) — use "::" for dual-stack IPv4+IPv6
.venv/bin/uvicorn fastapi_app.main:app --host "::" --port 8000 --reload

# 4. Start React (Terminal 2)
cd react_app && npm run dev

# 5. Open browser → http://localhost:5173
```

### 7. API parameter naming — different layers use different names
| | |
|---|---|
| **Symptom** | Manual `curl` test of `/api/v1/design/beam` with `b_mm`, `d_mm`, `Mu_kNm` returns 422 validation error. |
| **Root cause** | The **FastAPI API** uses user-friendly names (`width`, `depth`, `moment`, `shear`, `clear_cover`). The **structural_lib** uses engineering names (`b_mm`, `D_mm`, `Mu_kNm`). The router maps between them. Batch-design uses a third convention: `width_mm`, `depth_mm`, `mu_knm`. |
| **Why after migration** | Not migration-specific — confusing naming across layers. Bootstrap doc Warning #2 referenced structural_lib params, not FastAPI params. |
| **Fix** | Not a bug — just different naming conventions at each layer. Reference: |
| | • Single design API: `width`, `depth`, `moment`, `shear`, `fck`, `fy`, `clear_cover` |
| | • Batch design API: `width_mm`, `depth_mm`, `span_mm`, `mu_knm`, `vu_kn`, `fck_mpa`, `fy_mpa`, `cover_mm` |
| | • structural_lib: `b_mm`, `D_mm`, `Mu_kNm`, `Vu_kN`, `fck`, `fy`, `clear_cover_mm` |
| **Files reference** | `fastapi_app/models/beam.py`, `fastapi_app/routers/design.py`, `fastapi_app/routers/imports.py` |

### 8. Single beam design shows "Design Failed — Connection error (retry 9/10)"
| | |
|---|---|
| **Symptom** | Opening `/design` page shows "Calculating..." then "Design Failed" with "Connection error (retry 9/10)" and "Using REST API (WebSocket unavailable)". Design never completes even though backend is running. |
| **Root cause** | Two bugs in `useLiveDesign.ts`: (1) **No initial design on mount** — the auto-design `useEffect` only triggers when inputs _change_, but on first render the defaults haven't changed, so no REST call fires. (2) **WS error overrides state** — `state.error` was set to `ws.error` (WebSocket retry messages) even when the REST fallback had a successful result. |
| **Why after migration** | Not migration-specific — existed since TASK-503 REST fallback was added. WebSocket connects on old machine where server was always running; on fresh setup the timing exposes the race condition. |
| **Fix** | (1) Added `initialDesignFired` ref and a mount-time `useEffect` that fires `runRestDesign()` immediately. (2) Changed error state to: `result ? null : (ws.error \|\| geometryError)` — suppress WS error when a valid REST result exists. |
| **Files changed** | `react_app/src/hooks/useLiveDesign.ts` |
| **Debug steps tried** | Verified API works via curl, checked CORS preflight, traced `useLiveDesign` → `useDesignWebSocket` → `designStore` data flow, checked WS handler accepts connections (server log shows open→close cycle), identified missing initial trigger and error propagation bug. |

### 9. "Cannot connect to backend" when clicking Sample Building button (Session 103)
| | |
|---|---|
| **Symptom** | Clicking "Sample Building" in Import page → immediate red error: "Cannot connect to backend server. Is FastAPI running on port 8000?" — even though FastAPI is running and `curl http://localhost:8000/health` works fine. |
| **Root cause** | macOS on Mac Mini resolves `localhost` to **IPv6 `::1` first**. Uvicorn started with `--host 0.0.0.0` only binds IPv4 — browser's fetch to `http://localhost:8000` hits `[::1]:8000` → connection refused → `fetch` throws `TypeError: Failed to fetch` → caught as "Cannot connect" error. `curl` works because it falls back to `127.0.0.1`; browsers don't fall back. |
| **Why this was missed** | Issue #1 (Vite IPv6) was fixed by binding Vite to `0.0.0.0`. The inverse problem — uvicorn not listening on IPv6 — was overlooked. Both sides need fixing; only one was fixed. |
| **Why diagnosis took time** | `curl http://localhost:8000/health` returned 200 OK (IPv4 fallback). Health check looked fine. The failure only occurred via browser fetch (IPv6 `::1`). Not obvious without checking IPv6 explicitly: `curl -6 http://localhost:8000/health`. |
| **Fix** | Start uvicorn with `--host "::"` — dual-stack IPv6 binds **both** `::1` (IPv6) and `0.0.0.0` (IPv4) simultaneously: `.venv/bin/uvicorn fastapi_app.main:app --host "::" --port 8000 --reload` |
| **Verify** | `curl "http://[::1]:8000/health"` should return `{"status":"healthy"}`. If connection refused, uvicorn is still IPv4-only. |
| **Files changed** | `docs/getting-started/agent-bootstrap.md`, `docs/getting-started/mac-mini-setup.md`, `docs/_archive/planning-completed-2026-03/github-fix-plan.md` |

---

## Validation Results (Session 101)

| Check | Status | Notes |
|-------|--------|-------|
| Python tests (3194) | ✅ All pass | 5 skipped, 339 warnings (deprecation only) |
| FastAPI tests (122) | ✅ All pass | 32 warnings (deprecation only) |
| React build | ✅ Builds | Large chunk warnings for three.js/ag-grid (expected) |
| TypeScript | ✅ No errors | `npx tsc --noEmit` clean |
| Design endpoint | ✅ Works | `POST /api/v1/design/beam` → correct response |
| Batch design endpoint | ✅ Works | `POST /api/v1/import/batch-design` → correct response |
| Geometry endpoint | ✅ Works | `POST /api/v1/geometry/beam/full` → 3D geometry returned |
| Detailing endpoint | ✅ Works | `POST /api/v1/detailing/beam` → bar layout returned |
| Sample data endpoint | ✅ Works | `GET /api/v1/import/sample` → 153 beams loaded |
| Health endpoints | ✅ All healthy | `/health`, `/health/ready`, `/health/info` |

---

## Lessons Learned

1. **Always start backend before frontend** — React depends on FastAPI for all data
2. **Vite IPv6 binding is a silent killer** — server runs fine, `curl` works, but browser can't connect
3. **Colima needs explicit start** — unlike Docker Desktop, no background daemon
4. **Venv activation is per-terminal** — opening a new tab means activating again
5. **Test the full click path, not just the API** — the sample button bug was a UI wiring issue, not a backend problem
6. **`curl` lies about localhost connectivity** — `curl` tries IPv4 fallback automatically; browsers do not. Always test with `curl -6` or `curl "http://[::1]:8000"` to simulate browser behavior
7. **Fix one side of IPv6 mismatch, not just one** — Vite was fixed (issue #1) to bind both IPv4+IPv6. Uvicorn was missed — the same IPv6 mismatch reappeared months later in reverse
8. **Debug from the browser, not the terminal** — network errors in the React console show the actual failing URL; `curl` from terminal is not equivalent to a browser fetch
