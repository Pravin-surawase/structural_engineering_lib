# Day 18: React Hooks Deep Dive — The Data Pipeline Between UI and Math

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** High
**Created:** 2026-04-08
**Last Updated:** 2026-04-08
**Prerequisites:** Day 17 (React architecture)
**Library files:** `react_app/src/hooks/useCSVImport.ts`, `react_app/src/hooks/useLiveDesign.ts`, `react_app/src/hooks/useBeamGeometry.ts`, `react_app/src/hooks/useExport.ts`
**Key Pattern:** Custom hooks encapsulate data fetching + loading/error state + API calls

---

## What You'll Learn Today

By the end of this module you'll understand:
- What custom hooks are and why they're the most important pattern in our frontend
- The 21-hook library organized into 5 categories
- React Query — why it replaces manual useState + useEffect + fetch
- How `useCSVFileImport` handles file upload → API → store updates
- How `useLiveDesign` switches between WebSocket and REST
- How `useBeamGeometry` fetches 3D coordinates for React Three Fiber
- How `useExport` triggers browser file downloads from API blobs
- When to create a new hook vs. reusing existing (the #1 agent duplication mistake)

---

## Part 1: What Are Custom Hooks?

A **custom hook** is a JavaScript function that:
1. Starts with `use` (React naming convention — not optional, React enforces this)
2. Uses other hooks inside it (`useState`, `useQuery`, `useMutation`, etc.)
3. Returns both **data** AND **actions** — not just a value

**The before/after difference:**

```tsx
// ❌ WITHOUT hooks — component does everything (30 lines of boilerplate)
function BeamForm() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchDesign = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/design/beam', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(inputs),
      });
      const json = await res.json();
      setData(json);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return <button onClick={fetchDesign}>Design</button>;
}

// ✅ WITH hooks — component is 3 lines
function BeamForm() {
  const { mutate, data, isLoading, error } = useLiveDesign();
  return <button onClick={() => mutate(inputs)}>Design</button>;
}
```

The hook version is **reusable** (5 components can call `useLiveDesign()`) and **consistent** (every hook handles loading, error, caching the same way).

---

## Part 2: Our 21-Hook Library

We have 21 custom hooks across 11 files in `react_app/src/hooks/`:

| Category | Hooks | What It Does |
|----------|-------|-------------|
| **CSV Import** | `useCSVFileImport`, `useCSVTextImport`, `useDualCSVImport`, `useBatchDesign` | File upload → API parses CSV → returns beam array |
| **Design** | `useLiveDesign`, `useAutoDesign`, `useTorsionDesign`, `useLoadAnalysis` | Design inputs → API computes IS 456 math → returns results |
| **Geometry** | `useBeamGeometry`, `useBuildingGeometry`, `useCrossSectionGeometry` | Design result → API generates 3D coordinates → R3F renders |
| **Export** | `useExportBBS`, `useExportDXF`, `useExportReport`, `useExportBuildingSummary` | Selected beams → API generates file → browser download |
| **Insights** | `useDashboardInsights`, `useCodeChecks`, `useRebarSuggestions`, `useRebarValidation`, `useRebarApply` | Batch beams → API analyzes → metrics/suggestions |

**The iron rule:** Hooks call the backend API. They NEVER duplicate math or CSV parsing in JavaScript.

```
WRONG:  Parse CSV in React → calculate flexure in JS → render result
RIGHT:  useCSVFileImport → API → GenericCSVAdapter (Python) → return beams
RIGHT:  useLiveDesign → API → design_beam_is456 (Python) → return result
```

---

## Part 3: React Query — The Foundation Under Every Hook

Every hook is built on **TanStack React Query** (`@tanstack/react-query`). It provides two core primitives:

| Primitive | HTTP Method | When It Runs | Use Case |
|-----------|-------------|-------------|----------|
| `useQuery` | GET-like | Automatically on mount + when dependencies change | Fetching data (geometry, insights) |
| `useMutation` | POST-like | Manually when you call `mutate()` | Creating/updating data (design, import, export) |

**What React Query gives you for free:**
- `isLoading` / `isError` / `isSuccess` states — no manual `useState` for loading
- Automatic retries on network failure
- Caching — same request twice = instant second response from cache
- Deduplication — if 3 components request the same data simultaneously, only 1 API call
- DevTools — Chrome extension to inspect all queries/mutations

```tsx
// This 8-line hook replaces 30+ lines of manual state management
function useBeamList() {
  return useQuery({
    queryKey: ['beams'],              // Cache key — unique per request
    queryFn: async () => {            // The actual fetch
      const res = await fetch('/api/v1/beams');
      if (!res.ok) throw new Error('Failed to fetch');
      return res.json();
    },
    staleTime: 1000 * 60 * 5,        // Cache valid for 5 minutes
  });
}

// In a component — React Query provides loading/error/data automatically
function BeamList() {
  const { data, isLoading, error } = useBeamList();
  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  return <div>{data.length} beams loaded</div>;
}
```

---

## Part 4: The Data Flow Pattern

Every user interaction follows the same 10-step pattern:

```
1. User action (click button, upload file, change input)
       ↓
2. Component calls hook function (mutate() or auto-trigger)
       ↓
3. Hook sends HTTP request to FastAPI backend
       ↓
4. FastAPI router validates request (Pydantic)
       ↓
5. Router calls Python library (design_beam_is456, GenericCSVAdapter, etc.)
       ↓
6. Library computes result (pure math, no I/O)
       ↓
7. FastAPI returns JSON response
       ↓
8. Hook receives response → calls onSuccess callback
       ↓
9. onSuccess updates Zustand store (setResult, setBeams, etc.)
       ↓
10. All components subscribed to that store slice re-render
```

**This pattern never varies.** Import? Same pattern. Export? Same pattern. 3D geometry? Same pattern. The only difference is which hook, which API endpoint, and which store.

---

## Part 5: Hook Deep Dive — `useCSVFileImport`

This hook handles file upload → API parsing → store update:

```tsx
// hooks/useCSVImport.ts
export function useCSVFileImport() {
  const setBeams = useImportedBeamsStore((s) => s.setBeams);

  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch(`${API_BASE_URL}/api/v1/import/csv`, {
        method: 'POST',
        body: formData,   // Note: no Content-Type header — browser sets it for FormData
      });

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Import failed');
      }

      return res.json() as Promise<CSVImportResponse>;
    },
    onSuccess: (data) => {
      setBeams(data.beams);
      toast(`Imported ${data.beam_count} beams`, 'success');
      if (data.warnings.length > 0) {
        data.warnings.forEach(w => toast(w, 'warning'));
      }
    },
    onError: (error: Error) => {
      toast(`Import failed: ${error.message}`, 'error');
    },
  });
}
```

**Line-by-line what matters:**

| Line | What It Does | Why |
|------|-------------|-----|
| `useImportedBeamsStore((s) => s.setBeams)` | Gets ONLY the setBeams action from store | Selector prevents re-renders when beams change |
| `new FormData()` + `formData.append('file', file)` | Wraps file in multipart form | Server expects `multipart/form-data`, not JSON |
| No `Content-Type` header | Browser auto-sets boundary for multipart | Setting it manually breaks the upload |
| `throw new Error(error.detail)` | Converts API error to JS error | React Query catches thrown errors → calls onError |
| `setBeams(data.beams)` | Updates Zustand store | All components using beams re-render |
| `data.warnings.forEach(w => toast(w, 'warning'))` | Shows per-warning toasts | Backend reports partial parse issues |

**Usage in component:**
```tsx
function ImportView() {
  const { mutate, isPending } = useCSVFileImport();

  return (
    <FileDropZone
      onDrop={(file: File) => mutate(file)}
      disabled={isPending}
    >
      {isPending ? 'Importing...' : 'Drop CSV here'}
    </FileDropZone>
  );
}
```

---

## Part 6: Hook Deep Dive — `useLiveDesign`

This hook has a unique pattern: it **switches between WebSocket and REST** based on user preference:

```tsx
// hooks/useLiveDesign.ts
export function useLiveDesign() {
  const { setResult, setLoading, setWsLatency, useWebSocket } = useDesignStore();
  const ws = useDesignWebSocket();

  // REST fallback
  const restMutation = useMutation({
    mutationFn: async (inputs: BeamDesignRequest) => {
      const res = await fetch(`${API_BASE_URL}/api/v1/design/beam`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(inputs),
      });
      if (!res.ok) throw new Error('Design failed');
      return res.json();
    },
    onSuccess: (data) => setResult(data),
  });

  // Main function — chooses WebSocket or REST
  const mutate = (inputs: BeamDesignRequest) => {
    if (useWebSocket && ws.connected) {
      const start = performance.now();
      ws.send({ action: 'design', inputs });
      ws.onMessage((data) => {
        setResult(data);
        setWsLatency(performance.now() - start);  // Track round-trip latency
      });
    } else {
      restMutation.mutate(inputs);
    }
  };

  return { mutate, isLoading: restMutation.isPending, error: restMutation.error };
}
```

**Why the dual approach?**

| Scenario | Protocol | Latency | Why |
|----------|----------|---------|-----|
| User drags a slider (continuous updates) | WebSocket | ~50ms | Connection already open, no HTTP overhead |
| User clicks "Design" once | REST | ~200ms | Simpler, cached by React Query |
| WebSocket disconnected | REST (automatic fallback) | ~200ms | Graceful degradation |

The `performance.now()` timing is displayed in the UI so the user can see WebSocket vs REST speed difference.

---

## Part 7: Hook Deep Dive — `useBeamGeometry`

This hook fetches 3D coordinates for React Three Fiber rendering:

```tsx
// hooks/useBeamGeometry.ts
export function useBeamGeometry(request: BeamGeometryRequest) {
  return useQuery({
    queryKey: ['beam-geometry', request],  // Re-fetches when request changes
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/api/v1/geometry/beam/full`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });
      if (!res.ok) throw new Error('Failed to fetch geometry');
      return res.json() as Promise<Beam3DGeometry>;
    },
    enabled: request.width > 0 && request.depth > 0,  // Don't fetch for invalid inputs
    staleTime: 1000 * 60,  // Cache for 1 minute
  });
}
```

**Critical detail: `enabled` option.** Without it, the hook would fire a request even when width=0 and depth=0 (initial state). The `enabled` flag prevents wasted API calls.

**Usage with React Three Fiber:**
```tsx
function Viewport3D() {
  const { inputs, result } = useDesignStore();

  const { data: geometry, isLoading } = useBeamGeometry({
    width: inputs.width,
    depth: inputs.depth,
    span: 4000,
    ast_start: result?.flexure.Ast_provided,
    stirrup_dia: result?.shear.stirrup_dia,
    stirrup_spacing: result?.shear.stirrup_spacing,
  });

  if (isLoading) return <LoadingSpinner />;

  return (
    <Canvas>
      <ambientLight />
      {geometry?.rebars.map((rebar, i) => (
        <RebarMesh key={i} path={rebar.segments} />
      ))}
      {geometry?.stirrups.map((stirrup, i) => (
        <StirrupMesh key={i} path={stirrup.path} />
      ))}
    </Canvas>
  );
}
```

**The geometry data shape:**
```tsx
interface Beam3DGeometry {
  concreteOutline: Point3D[];      // 8 vertices of the concrete box
  rebars: RebarPath[];              // Each bar: segments of 3D coordinates
  stirrups: StirrupLoop[];          // Each stirrup: closed loop of 3D coordinates
  metadata: {
    cover: number;                  // Clear cover in mm
    isValid: boolean;               // Whether geometry is buildable
    remarks: string[];              // Warnings (e.g., "bars too close")
  };
}
```

---

## Part 8: Hook Deep Dive — `useExport`

Export hooks download binary files from the API:

```tsx
// hooks/useExport.ts
export function useExportBBS() {
  return useMutation({
    mutationFn: async (beamIds: string[]) => {
      const res = await fetch(`${API_BASE_URL}/api/v1/export/bbs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ beam_ids: beamIds }),
      });
      if (!res.ok) throw new Error('Export failed');
      return res.blob();  // Binary data, NOT json
    },
    onSuccess: (blob) => {
      // Create temporary download link
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `bbs-${Date.now()}.csv`;
      a.click();
      URL.revokeObjectURL(url);  // Free memory
      toast('BBS exported successfully', 'success');
    },
  });
}
```

**The download trick explained:**
1. `res.blob()` — Get binary data (not JSON) from the response
2. `URL.createObjectURL(blob)` — Create a temporary URL pointing to the blob in memory
3. Create an invisible `<a>` element with `download` attribute
4. Programmatically `.click()` it — browser triggers download
5. `URL.revokeObjectURL(url)` — Free the memory (the blob stays in the downloaded file)

This same pattern is used for BBS (CSV), DXF (CAD), and PDF (report) exports — only the endpoint and filename change.

---

## Part 9: Error Handling Patterns

All hooks follow the same 3-tier strategy:

```tsx
const mutation = useMutation({
  mutationFn: async (inputs) => { /* API call */ },
  onSuccess: (data) => {
    setResult(data);
    toast("Design complete!", "success");
  },
  onError: (err) => {
    toast(`Design failed: ${err.message}`, "error");
  },
  retry: (failureCount, error) => {
    if (error.status === 400) return false;   // Validation → don't retry
    if (error.status === 422) return false;   // Bad input → don't retry
    return failureCount < 2;                   // Network/500 → retry twice
  },
  retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 30000),
});
```

| Error Type | HTTP Status | Retry? | User Sees |
|------------|-------------|--------|-----------|
| Validation | 400 / 422 | No | Red toast: "Width must be > 0" |
| Network timeout | — | Yes (2x, exponential backoff) | Yellow toast: "Retrying..." → then red if both fail |
| Server error | 500 | Yes (2x) | Red toast: "Server error, please try again" |

---

## Part 10: When to Create vs. Reuse Hooks

**This is the #1 mistake agents make** — creating a new hook when an existing one covers the use case.

```bash
# ALWAYS check first
ls react_app/src/hooks/
```

**Decision tree:**

```
Need to fetch/send data?
    ├── Is there an existing hook that does the same API call? → REUSE IT
    ├── Does an existing hook accept params for your use case? → PASS DIFFERENT PARAMS
    └── Genuinely new API endpoint + new data shape? → CREATE NEW HOOK
```

**Example:**
```tsx
// ❌ WRONG — duplicates useBeamGeometry logic
function useMyCustomGeometry(beamId: string) {
  return useQuery({
    queryKey: ['custom-geo', beamId],
    queryFn: async () => fetch(`/api/v1/geometry/beam/full`, ...),
  });
}

// ✅ RIGHT — reuse with different params
const { data } = useBeamGeometry({ beam_id: beamId, width, depth, span: 4000 });
```

---

## Part 11: Exercises

### Exercise 1: Inspect hooks in DevTools
1. `cd react_app && npm run dev`
2. Open `http://localhost:5173/design`
3. Open DevTools → install React Query DevTools extension
4. Click "Design Beam" — watch the mutation appear with payload, response, timing

### Exercise 2: Trace a CSV import
1. Navigate to `/import`, drop a CSV file
2. Open DevTools → Network tab → find `POST /api/v1/import/csv`
3. Check the response: how many beams? Any warnings?
4. Check the Zustand store: does `useImportedBeamsStore.beams` match?

### Exercise 3: Test error handling
1. Upload an invalid CSV (rename a `.txt` file to `.csv`)
2. Watch the Network tab for the 400 response
3. See how `onError` in `useCSVFileImport` triggers a toast notification

---

## Part 12: Self-Check Q&A

1. **What is a custom hook?** A function starting with `use` that encapsulates reusable logic.
2. **Why React Query instead of `useEffect` + `fetch`?** Auto loading/error/cache/retry/dedup.
3. **Difference between `useQuery` and `useMutation`?** useQuery = auto-fetch on mount; useMutation = manual trigger.
4. **Why does `useBeamGeometry` use `useQuery` not `useMutation`?** It fetches data that updates when inputs change — query behavior, not mutation.
5. **Why does `useCSVFileImport` NOT set `Content-Type`?** Browser auto-sets multipart boundary for FormData.
6. **How does `useExportBBS` trigger a file download?** Blob URL → invisible `<a>` → programmatic click.
7. **What does `enabled: false` do in `useQuery`?** Prevents the query from running until the condition is true.
8. **Why does `useLiveDesign` have both WebSocket and REST?** WS for fast continuous updates, REST as fallback.
9. **When should you create a new hook?** Only for genuinely new API endpoints + data shapes. Check existing hooks first.
10. **What does `staleTime: 5 * 60 * 1000` mean?** Cached data is considered fresh for 5 minutes — no refetch until then.

---

## Part 13: Things to Know — Deep Insights

### 13.1: `queryKey` is the cache identity
React Query uses `queryKey` to decide if two requests are the same. `['beam-geometry', { width: 300 }]` and `['beam-geometry', { width: 350 }]` are DIFFERENT cache entries. Change any property in the key, and React Query treats it as a new request. This is why `useBeamGeometry` includes the full request object in `queryKey` — every different beam dimension gets its own cache entry.

### 13.2: `mutate` vs `mutateAsync`
`mutate()` fires and forgets — the hook handles success/error via callbacks. `mutateAsync()` returns a Promise you can `await`. Use `mutate()` in onClick handlers (fire-and-forget). Use `mutateAsync()` when you need to chain multiple mutations sequentially (e.g., import CSV → then batch design → then export).

### 13.3: FormData drops the Content-Type header on purpose
When you upload a file via `FormData`, the browser generates a `Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...` header automatically. If you manually set `Content-Type: 'multipart/form-data'`, you're missing the boundary string, and the server can't parse the body. This is why `useCSVFileImport` has no Content-Type header.

### 13.4: `enabled` prevents cascade fetches
Without `enabled`, `useBeamGeometry` would fire a request when `width=0, depth=0` (initial store state). The server would return an error, the user would see a flash of red. The `enabled: request.width > 0` flag prevents this — the query just sits idle until valid inputs arrive.

### 13.5: Selective Zustand subscriptions matter in hooks
`useImportedBeamsStore((s) => s.setBeams)` subscribes to ONLY the `setBeams` action. This means the component won't re-render when `beams` array changes — it only needs the action, not the data. If you wrote `useImportedBeamsStore()` (entire store), the component would re-render on every beam change.

### 13.6: React Query DevTools are essential for debugging
Install the `@tanstack/react-query-devtools` package. It shows: every active query/mutation, their status (loading/success/error), the cached data, the request timing, and how many times it retried. Without it, debugging hook behavior is blind guessing.

---

## Part 14: What Can Be Done Better

### 14.1: No request cancellation
When the user types fast in a design input (300 → 350 → 400), three API requests fire. The first two are wasted because only the 400 result matters. React Query supports `AbortSignal` for cancellation, but none of our hooks use it. Adding `signal` to fetch calls would cancel in-flight requests when inputs change.

### 14.2: No optimistic updates
When the user clicks "Design", the UI shows a loading spinner until the API responds. With optimistic updates, the UI could immediately show an estimate (based on previous results for similar inputs) and then replace it with the real result. This makes the app feel instant.

### 14.3: No request deduplication across hooks
If `BeamForm` and `ResultsPanel` both use `useLiveDesign` and both call `mutate()` in the same event, two requests fire. Mutations aren't deduplicated like queries. A shared "design in progress" flag in the Zustand store would prevent this.

### 14.4: Hardcoded API_BASE_URL
Most hooks reference `${API_BASE_URL}` which comes from an environment variable. But some hooks hardcode the URL or have inconsistent patterns. A central `apiClient` object with typed methods (`apiClient.designBeam(inputs)`) would centralize URL construction and headers.

### 14.5: No hook-level error logging
When a hook's `onError` fires, it shows a toast but doesn't log to any service. In production, API failures should be logged (with request details but without sensitive data) for monitoring. A shared `logError()` utility in every onError callback would enable this.

---

## Part 15: Innovation Directions

### 15.1: Auto-generated hooks from OpenAPI
Tools like `orval` or `openapi-react-query-codegen` can auto-generate React Query hooks from the FastAPI OpenAPI spec. Zero manual hook maintenance — when the API changes, regenerate hooks. Type-safe API calls guaranteed.

### 15.2: Suspense-native hooks
React 19 supports `use()` for data fetching with Suspense boundaries. Instead of checking `if (isLoading)` in every component, the component just renders and React pauses it until data arrives. Cleaner code, unified loading states.

### 15.3: Service Worker caching for offline
A service worker could cache API responses for previously designed beams. If the user revisits a design they did yesterday, the result loads instantly from the cache — no server needed. Useful for site engineers with spotty internet.

### 15.4: Shared workers for heavy computation
If any client-side computation is needed (e.g., mesh generation for 3D), it could run in a `SharedWorker` — shared across all open tabs, doesn't block the main thread. Multiple browser tabs wouldn't duplicate the work.

### 15.5: Real-time collaboration hooks
Hooks that sync state across multiple users via WebSocket rooms. Two engineers could work on the same building — one changes a beam in Mumbai, the other sees it update in Delhi. Built on top of the existing WebSocket infrastructure.

---

## Part 16: Next Repo Must-Add

### Concrete items

1. **AbortSignal for request cancellation** — Cancel stale requests when user types fast
2. **Central `apiClient` module** — Typed methods for all endpoints, single URL construction
3. **Auto-generated hooks from OpenAPI** — `orval` or `openapi-react-query-codegen` in CI
4. **Error logging in onError callbacks** — Structured logging for production monitoring
5. **Optimistic updates for design** — Show estimated result instantly, replace with real result
6. **Hook testing with MSW** — Mock Service Worker for testing hook behavior without a running server
7. **Custom hook documentation** — JSDoc comments on every public hook with usage examples

### Day-1 checklist for a new hook

```
□ 1. Check react_app/src/hooks/ — does a hook already exist for this?
□ 2. Use useMutation for POST (user-triggered) or useQuery for GET (auto-fetch)
□ 3. Include queryKey with all dependencies that affect the response
□ 4. Use enabled flag to prevent unnecessary initial fetches
□ 5. Add onSuccess callback that updates the Zustand store
□ 6. Add onError callback with toast notification
□ 7. Set appropriate retry logic (no retry for 400/422)
□ 8. Use Zustand selectors (not entire store) to minimize re-renders
□ 9. Export from the hooks barrel file for clean imports
□ 10. Verify the hook works: cd react_app && npm run build
```

---

## 📎 References

- [React Hooks Docs](https://react.dev/reference/react)
- [TanStack React Query Docs](https://tanstack.com/query/latest)
- [Custom Hooks Guide](https://react.dev/learn/reusing-logic-with-custom-hooks)
- `react_app/src/hooks/useCSVImport.ts` — CSV import hooks
- `react_app/src/hooks/useLiveDesign.ts` — Design hooks (WS + REST)
- `react_app/src/hooks/useBeamGeometry.ts` — 3D geometry hook
- `react_app/src/hooks/useExport.ts` — Export/download hooks
- **Previous:** Day 17 covers React architecture, Zustand stores, Tailwind
- **Next:** Day 19 covers 3D visualization with React Three Fiber
