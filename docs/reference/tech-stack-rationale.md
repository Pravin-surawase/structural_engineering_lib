# Tech Stack Rationale

**Type:** Reference | **Audience:** All Agents | **Status:** Approved | **Importance:** Medium
**Created:** 2026-01-11 | **Last Updated:** 2026-01-11

> Moved from agent-bootstrap.md to keep bootstrap lean. This is reference material — agents don't need this to start working.

---

## Why each technology?

| Technology | Why chosen | What it gives us | Trade-offs |
|------------|-----------|-------------------|------------|
| **Python** (core lib) | Standard in structural engineering; NumPy/SciPy ecosystem; readable math | Engineers can read and verify IS 456 formulas directly | Slower than C/Rust for heavy computation (acceptable — single-beam calcs are <10ms) |
| **FastAPI** | Auto-generates OpenAPI docs; Pydantic validation built-in; async + WebSocket native; fastest Python web framework | Type-safe request/response, interactive `/docs` page, SSE streaming, WebSocket for live design | Smaller ecosystem than Django; no built-in ORM (we don't need one — no database) |
| **React 19** | Most widely-adopted UI framework; R3F (React Three Fiber) for 3D; massive ecosystem | Component reuse, lazy loading, Suspense for code-splitting, strong TypeScript support | Larger bundle than Svelte/Preact; requires build step |
| **React Three Fiber (R3F)** | Declarative 3D in React — no imperative WebGL boilerplate | 3D beam visualization, rebar positioning, building models — all as React components | Three.js is ~720KB (unavoidable for 3D); requires GPU |
| **Tailwind CSS** | Utility-first — no CSS files, no naming debates; co-located with markup | Consistent design tokens, fast prototyping, tree-shakes unused classes | Verbose class strings; learning curve for traditional CSS devs |
| **AG Grid** | Enterprise-grade data grid; handles 1000+ beams with virtual scrolling | Batch beam editing, sorting, filtering — ETABS-like spreadsheet feel | 858KB chunk (large); free tier sufficient for our needs |
| **Zustand** | Minimal state management (2KB); no boilerplate vs Redux | Two stores: `useDesignStore` + `useImportedBeamsStore` — simple, fast | No dev tools middleware out-of-box (can add if needed) |
| **Docker** | Reproducible deployment; eliminates "works on my machine" | One command (`docker compose up`) runs the entire backend with correct Python, deps, env | Adds ~200MB image size; requires Docker installed |
| **Vite** | Near-instant HMR, fast builds, native ES modules | React dev server in <200ms; production build with code-splitting in ~4s | Less battle-tested than Webpack for edge cases (hasn't been an issue) |
| **Streamlit** (legacy) | Rapid prototyping for data apps; zero frontend knowledge needed | Quick interactive UI for single-beam design during early development | Not suitable for production multi-page apps; limited layout control; being replaced by React |

## Is it efficient?

- **Python core**: Single beam design = **<10ms**. Batch of 153 beams = **<2s**. Pure math, no I/O overhead.
- **FastAPI**: Handles **1000+ req/s** on a single core. Pydantic v2 validation is C-compiled.
- **React bundle**: Code-split into 19 chunks. Initial load = **~67KB** (index). Three.js/AG Grid load on-demand only when needed.
- **Docker**: Production image is a slim Python 3.11 container. Healthcheck ensures reliability.

## Is it safe?

- **Input validation**: Every API endpoint uses Pydantic models with `Field(ge=0, le=2000)` constraints — invalid data is rejected before reaching the math layer.
- **CORS**: Configured for development origins; must be locked down for production.
- **JWT auth**: Available (opt-in) for API authentication. Default dev key triggers a warning.
- **Rate limiting**: Configurable via `RATE_LIMIT_REQUESTS` / `RATE_LIMIT_WINDOW` env vars.
- **No database**: No SQL injection surface. Stateless computation only.
- **Docker isolation**: Backend runs in container — host filesystem not exposed (except VBA volume).

## Future improvements to consider

| Area | Current | Potential improvement |
|------|---------|----------------------|
| **3D bundle size** | Three.js = 720KB | Consider lighter alternatives if 3D scope narrows |
| **AG Grid size** | 858KB | Could switch to TanStack Table if simpler grid is sufficient |
| **WebAssembly** | Not used | Could compile hot-path IS 456 math to WASM for browser-side calc |
| **CDN/edge** | Not deployed | Static React bundle could go to CDN; API to edge workers |
| **Caching** | None | Redis/in-memory cache for repeated design calls with same params |
| **Database** | None (stateless) | PostgreSQL if we add project save/load, user accounts |
| **Monitoring** | Health endpoints only | OpenTelemetry + Prometheus for production observability |
