# Day 20: End-to-End Data Flow — Tracing a Beam from CSV Upload to 3D Render

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** Critical
**Created:** 2026-04-08
**Last Updated:** 2026-04-08
**Prerequisites:** Days 1-19 (materials, flexure, shear, detailing, FastAPI, React, hooks, 3D)
**Library files:** All layers — hooks, routers, services, IS 456 code, visualization
**IS 456 Clauses:** All — this module traces data through every clause implementation

---

## What You'll Learn Today

By the end of this module you'll understand:
- How data flows through ALL four architectural layers (React → FastAPI → Services → IS 456 Code)
- The complete journey of a CSV file: upload → parse → design → visualize → export
- Where units convert, where validation happens, and where math lives
- How to trace ANY bug through the full stack
- Why the layered architecture makes debugging possible

---

## Part 1: The Four-Layer Architecture

Every piece of data passes through exactly four layers. No shortcuts.

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: UI / IO                                           │
│  React 19 + R3F + Tailwind  |  FastAPI Routers              │
│  Components, hooks, stores  |  Pydantic models, endpoints   │
│  Units: display (mm, kN)    |  Units: API (mm, kN)          │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: Services                                          │
│  services/api.py — orchestration (calls IS 456 functions)   │
│  services/adapters.py — CSV/Excel parsing (40+ mappings)    │
│  services/beam_pipeline.py — multi-step workflows           │
│  Units: explicit (mm, N/mm², kN, kNm)                      │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3: IS 456 Code                                       │
│  codes/is456/flexure.py, shear.py, detailing.py             │
│  Pure math — NO I/O, NO imports from layers above           │
│  Units: internal (mm, N, N·mm)                              │
├─────────────────────────────────────────────────────────────┤
│  LAYER 4: Core Types                                        │
│  core/data_types.py — FlexureResult, ShearResult            │
│  core/sections.py — RectangularSection                      │
│  core/materials.py — base material properties               │
│  Units: stored as explicit fields (b_mm, d_mm, fck)         │
└─────────────────────────────────────────────────────────────┘
```

**The import rule:** Data flows DOWN. Each layer imports from layers below, NEVER above.
- Core: imports nothing from the library
- IS 456 Code: imports from Core only
- Services: imports from IS 456 Code and Core
- UI/IO: imports from Services (through API endpoints)

**Why this matters for debugging:** A CSS change in React can NEVER affect IS 456 math. A formula fix in flexure.py can NEVER break the CSV parser. Bugs are isolated to their layer.

---

## Part 2: Journey 1 — CSV Upload

The complete flow when a user drops a CSV file:

```
User drops beams.csv
    ↓
FileDropZone → useCSVFileImport → POST /api/v1/import/csv (FormData)
    ↓
FastAPI router → GenericCSVAdapter.parse(text)
    ↓
Adapter: matches 40+ column name variations → normalizes to standard names
    ↓
Returns: { beams: [{width_mm: 300, depth_mm: 500, mu_knm: 150, ...}], count: 42 }
    ↓
React: onSuccess → setBeams(data.beams) → Zustand store updated
    ↓
All components using beams re-render
```

**React side (useCSVFileImport):**
```tsx
export function useCSVFileImport() {
  const { setBeams } = useImportedBeamsStore();
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`${API_BASE_URL}/api/v1/import/csv`, {
        method: "POST", body: formData
      });
      return unwrapResponse(response);
    },
    onSuccess: (data) => {
      setBeams(data.beams);
      toast.success(`Imported ${data.beams.length} beams`);
    },
  });
}
```

**FastAPI router (imports.py):**
```python
@router.post("/csv", response_model=CSVImportResponse)
async def import_csv(file: UploadFile = File(...), adapter: str = Query("generic")):
    content = await file.read()
    text = content.decode("utf-8")
    adapters = {"generic": GenericCSVAdapter(), "etabs": ETABSAdapter()}
    chosen = adapters.get(adapter, adapters["generic"])
    beams = chosen.parse(text)
    return success_response({"beams": beams, "count": len(beams)})
```

**Services layer (adapters.py) — the column mapping magic:**
```python
class GenericCSVAdapter:
    COLUMN_MAPPINGS = {
        "width_mm": ["width", "b", "B", "Width", "beam_width", "BeamBreadth"],
        "depth_mm": ["depth", "D", "h", "H", "Depth", "beam_depth"],
        "mu_knm":   ["Mu", "moment", "M_u", "BendingMoment"],
        "vu_kn":    ["Vu", "shear", "V_u", "ShearForce"],
        # 40+ total mappings
    }
```

This is where the chaos of real-world CSV files (ETABS says "Width", STAAD says "b", SAP2000 says "BeamBreadth") gets normalized into clean, standard parameter names.

---

## Part 3: Journey 2 — Batch Design (SSE Streaming)

When the user clicks "Design All" on 100+ imported beams:

```
User clicks "Design All"
    ↓
useBatchDesign → EventSource connects to SSE endpoint
    ↓
FastAPI: for each beam → design_beam_is456(b_mm, D_mm, fck, fy, mu_knm, vu_kn)
    ↓
services/api.py orchestrates: flexure → shear → torsion → deflection
    ↓
Each beam result streams back via SSE as it completes
    ↓
React: updates progress bar (42/100), adds result to Zustand
    ↓
User sees live progress, can cancel mid-batch
```

**Why SSE instead of a single POST?**
Designing 200 beams takes 30+ seconds. With a single POST the user sees nothing until ALL beams finish. With SSE:
- Progress bar updates per beam
- User can cancel mid-batch
- If the connection drops at beam 199, you keep the 198 results

**The IS 456 math pipeline for each beam:**
```python
# services/api.py — orchestration order
def design_beam_is456(b_mm, D_mm, fck, fy, mu_knm, vu_kn, ...):
    # Step 1: Flexure (Cl 38.1)
    flexure = calculate_ast_required(b_mm, d_mm, fck, fy, mu_knm)

    # Step 2: Shear (Cl 40)
    shear = calculate_shear_reinforcement(b_mm, d_mm, fck, fy, vu_kn, flexure.Ast)

    # Step 3: Torsion (Cl 41) — if torsion provided
    # Step 4: Deflection (Cl 23.2)
    # Step 5: Detailing (Cl 26)

    return DesignResult(flexure=flexure, shear=shear, ...)
```

---

## Part 4: Journey 3 — 3D Visualization

When the user clicks a beam to see it in 3D:

```
User clicks beam in table
    ↓
useBeamGeometry → POST /api/v1/geometry/beam/full
    ↓
FastAPI → beam_to_3d_geometry(width, depth, span, Ast, stirrup_dia, stirrup_spacing)
    ↓
geometry_3d.py calculates:
  - Bottom rebar at y = cover + dia/2 = 40 + 12.5 = 52.5mm from bottom
  - Top rebar at y = depth - cover - dia/2 = 450 - 40 - 12.5 = 397.5mm
  - 26 stirrup loops, one every 150mm
    ↓
Returns: { rebars: [{segments: [{start, end, diameter}]}], stirrups: [...] }
    ↓
R3F renders: <CylinderGeometry> for each rebar segment, instancedMesh for stirrups
    ↓
User sees orange bars inside transparent gray concrete
```

---

## Part 5: Journey 4 — Export BBS

```
User clicks "Export BBS"
    ↓
useExportBBS → POST /api/v1/export/bbs with beam_ids
    ↓
Python generates CSV: bar mark, type, diameter, cut length, number, weight
    ↓
Returns: binary blob (CSV file)
    ↓
React: URL.createObjectURL(blob) → invisible <a>.click() → browser download
    ↓
User gets "beam_bbs.csv" in Downloads
```

---

## Part 6: Tracing a Single Value Through All Layers

Let's trace `width = 300mm` from CSV to 3D:

```
CSV file:       "Width,Depth,Mu\n300,500,150"
                   ↓
Adapter:        COLUMN_MAPPINGS["width_mm"] matches "Width" → 300.0
                   ↓
FastAPI:        BeamRow(width_mm=300, ...) [Pydantic validates: must be number]
                   ↓
React store:    beam.width_mm = 300 [Zustand]
                   ↓
Design API:     design_beam_is456(b_mm=300, ...)
                   ↓
Flexure:        calculate_ast_required(b_mm=300, d_mm=450, ...) [d = D - cover - φ/2]
                   ↓
3D Geometry:    beam_to_3d_geometry(width=300, ...)
                → concrete_box: [0, 0, 0] to [300, 500, 5000]
                   ↓
R3F render:     <boxGeometry args={[0.3, 0.5, 5.0]} /> [mm * 0.001 = meters]
```

The value `300` stays as millimeters through every layer. Only the 3D renderer applies SCALE (0.001) to convert to meters for Three.js camera framing.

---

## Part 7: Where Unit Conversion Actually Happens

Most values pass unchanged. But bending moment converts at the Layer 2/3 boundary:

```
CSV:       "Mu" = 150 (meaning kNm)
Adapter:   mu_knm = 150.0
Service:   Mu_knm = 150.0
  ──────── BOUNDARY ────────
IS 456:    Mu = Mu_knm * 1e6 = 150,000,000 N·mm ← CONVERTS ON ENTRY
Math:      All calculations in N·mm
Result:    Mu_capacity = 165,300,000 N·mm
  ──────── BOUNDARY ────────
Service:   Mu_capacity_knm = 165,300,000 / 1e6 = 165.3 ← CONVERTS ON EXIT
FastAPI:   {"moment_capacity_knm": 165.3}
React:     displays "165.3 kNm"
```

Unit conversions happen at exactly TWO places:
1. **Entering Layer 3:** kNm → N·mm, kN → N
2. **Leaving Layer 3:** N·mm → kNm, N → kN

---

## Part 8: Error Propagation

What happens when a CSV has invalid data?

```
CSV: "Width,Depth,Mu\nabc,500,150"
  ↓
Adapter: float("abc") → ValueError  [caught, row skipped]
  ↓
FastAPI: {"beams": [...valid...], "warnings": ["Row 1: invalid width"]}
  ↓
React: toast.warn("1 row skipped — see warnings")
  ↓
User: sees which rows failed and why
```

Errors propagate UPWARD, getting more user-friendly at each level:
- Layer 3: `ValueError("b_mm must be positive")`
- Layer 2: catches + adds context → `"Row 3: width must be positive"`
- Layer 1 (FastAPI): wraps → `422 Unprocessable Entity`
- Layer 1 (React): toast notification with specific message

---

## Part 9: Exercises

### Exercise 1: Trace a beam through the stack
Open `Etabs_CSV/beam_forces.csv`, pick a beam. Write down every variable name its width takes through: CSV header → Adapter mapping → FastAPI model → Service parameter → IS 456 function → 3D geometry.

### Exercise 2: Full stack smoke test
```bash
./run.sh dev
# Open http://localhost:5173
# 1. Upload Etabs_CSV/beam_forces.csv
# 2. Click "Design All" — watch SSE progress
# 3. Click a beam — see 3D view
# 4. Export BBS — check the downloaded file
```
At each step, check DevTools Network tab: what URL? what data? how long?

### Exercise 3: Debugging exercise
If a beam's shear capacity shows as 0 in the UI, what files do you check? (Answer: React display → FastAPI router → services/api.py → codes/is456/shear.py → core/data_types.py)

---

## Part 10: Self-Check Q&A

1. **Name the four layers in order.** UI/IO → Services → IS 456 Code → Core Types.
2. **Can IS 456 code import from Services?** No — imports only go downward.
3. **Where does CSV column mapping happen?** `services/adapters.py` (GenericCSVAdapter).
4. **Why SSE for batch design?** Live progress, cancellable, resilient to drops.
5. **Where do kNm → N·mm unit conversions happen?** At the Layer 2/3 boundary.
6. **If the 3D shows rebar in the wrong position, which file likely has the bug?** `visualization/geometry_3d.py`.
7. **Why doesn't React parse CSV directly?** Architecture rule: UI doesn't process data. Also, adapter handles 40+ column name variations.
8. **What does the SCALE constant (0.001) do?** Converts mm to meters for Three.js camera framing.
9. **How many places does unit conversion happen for moment?** Exactly 2: entering and leaving Layer 3.
10. **How do errors propagate?** Upward — Layer 3 ValueError → Layer 2 adds context → Layer 1 HTTP error → React toast.

---

## Part 11: Things to Know — Deep Insights

### 11.1: The "b_mm not width" naming convention is intentional
Every parameter name includes its unit: `b_mm`, `fck_nmm2`, `mu_knm`. This prevents the Mars Climate Orbiter class of bugs — where one function expects meters and another passes feet. When you see `b_mm`, you KNOW it's millimeters. If someone passes `b_m = 0.3` to a function expecting `b_mm`, the value (0.3mm) would flag as obviously wrong.

### 11.2: GenericCSVAdapter handles chaos by design
Real ETABS exports have column names like "Mu3+" and "VMax-". Different versions use different names. The 40+ mapping dictionary is the result of testing with actual exports from 5+ structural analysis software packages. Adding a new mapping is a one-line change, not a code rewrite.

### 11.3: SSE has a 6-connection browser limit
Browsers allow only 6 simultaneous connections per host (HTTP/1.1). If the user opens 7 tabs all connected to SSE endpoints, the 7th blocks. This is a browser limitation, not a code bug. HTTP/2 multiplexing solves this, but the backend must support it.

### 11.4: The service layer is NOT just a pass-through
`services/api.py` doesn't just call `calculate_flexure(params)` and return. It orchestrates: call flexure → use flexure result in shear calculation → use both in detailing → assemble the final result. The ORDER matters: shear needs to know Ast from flexure, detailing needs both.

### 11.5: React Three Fiber and React don't share render timing
R3F renders at 60fps independently. React reconciles on state change. When you call `setResult()` in Zustand, React re-renders the results panel. But R3F only updates the 3D view when its props change (via the hook). They're two independent render loops sharing one DOM.

### 11.6: The Pydantic → TypeScript type gap is manual
`BeamDesignRequest` in Python and `BeamDesignRequest` in TypeScript are manually kept in sync. If Python adds a field, TypeScript won't know until someone updates `types/api.ts`. This is a known pain point (see Day 17: Innovation).

---

## Part 12: What Can Be Done Better

### 12.1: No end-to-end type safety
The TypeScript `BeamDesignRequest` and Python `BeamDesignRequest` are separate definitions. If they drift apart, the frontend silently sends wrong data. An auto-generated TypeScript SDK from `openapi.json` would eliminate this.

### 12.2: No request/response logging middleware
When a design fails, there's no audit trail of what inputs were sent. A FastAPI middleware that logs request body + response status (without sensitive data) would make debugging faster.

### 12.3: CSV adapter doesn't detect unit conflicts
If a CSV has "Width" in meters (0.3) and "Depth" in mm (500), the adapter doesn't detect the inconsistency. It would import `width_mm=0.3`, which is clearly wrong but passes validation. A sanity check (is width < 50mm? probably wrong units) would catch this.

### 12.4: No data lineage tracking
When a final design result says `Ast = 942 mm²`, there's no trace of which CSV row → which adapter mapping → which API call → which IS 456 clause produced it. A data lineage ID propagated through all layers would enable "click to explain" on any result.

### 12.5: SSE doesn't support resume-on-reconnect
If the SSE connection drops at beam 50/200, the client must restart from beam 1. An offset parameter (`start_from=50`) would let the client resume where it left off.

---

## Part 13: Innovation Directions

### 13.1: GraphQL for flexible queries
Instead of separate REST endpoints for design, geometry, and export, a GraphQL API would let the client request exactly the data it needs in one query: `beam(id: "B1") { flexure { Ast xu } geometry { rebars } }`.

### 13.2: Event sourcing for design history
Store every design input change as an event. Replay events to reconstruct any point in time. Engineers could see "at 2pm, I changed fck from 25 to 30, and Ast dropped from 1200 to 942."

### 13.3: WebAssembly for client-side IS 456 math
Compile the IS 456 Python code to WASM (via Pyodide or Rust port). No API call needed — design results appear instantly. Works offline. The server becomes optional.

### 13.4: Digital twin integration
Connect the design data to BIM (Building Information Modeling) tools. Upload an IFC file, the library designs all beams, and exports the results back to the BIM model with rebar positions.

### 13.5: AI-powered CSV column detection
Instead of hardcoded mappings, use a small ML model to detect which CSV columns represent width, depth, moment, etc. based on column names AND sample values. Would handle any unknown software export.

---

## Part 14: Next Repo Must-Add

### Concrete items

1. **Auto-generated TypeScript SDK** — `openapi-typescript` in CI, zero manual type sync
2. **Request/response logging middleware** — Structured logs for all API calls
3. **CSV unit sanity checker** — Flag "width_mm=0.3" as likely wrong unit
4. **SSE resume-on-reconnect** — `start_from=N` parameter for batch design
5. **Data lineage IDs** — Trace any result back through all 4 layers
6. **E2E integration tests** — Selenium/Playwright test: upload CSV → design → export → verify file
7. **Adapter test suite** — Test with real exports from ETABS, STAAD, SAP2000, SAFE

### Day-1 checklist for a new layer-crossing feature

```
□ 1. Define the data shape at each layer (TypeScript interface, Pydantic model, Python type)
□ 2. Verify import direction — never import upward
□ 3. Add unit conversion at Layer 2/3 boundary if needed
□ 4. Add Pydantic validation for all inputs
□ 5. Handle errors at each layer boundary (catch, add context, re-raise)
□ 6. Write tests at each layer: unit test (L3), integration test (L2), API test (L1)
□ 7. Update GenericCSVAdapter if new columns needed
□ 8. Update TypeScript types to match new Pydantic models
□ 9. Test the full round-trip: React → API → Python → API → React
□ 10. Verify in browser: DevTools Network tab shows correct request/response
```

---

## Summary

| Data Journey | React | FastAPI | Services | IS 456 Code |
|-------------|-------|---------|----------|-------------|
| CSV Upload | FileDropZone → useCSVFileImport | POST /import/csv | GenericCSVAdapter | — |
| Batch Design | useBatchDesign (SSE) | /stream/batch-design | design_beam_is456 | flexure + shear + detailing |
| 3D View | useBeamGeometry → R3F Canvas | POST /geometry/beam/full | geometry_3d.py | — |
| Export BBS | useExportBBS → download | POST /export/bbs | generate_bbs() | — |

---

## 📎 References

- `react_app/src/hooks/` — useCSVImport.ts, useBatchDesign.ts, useBeamGeometry.ts, useExport.ts
- `fastapi_app/routers/` — imports.py, design.py, geometry.py, export.py, streaming.py
- `Python/structural_lib/services/api.py` — Orchestration hub
- `Python/structural_lib/services/adapters.py` — CSV parser (40+ mappings)
- `Python/structural_lib/codes/is456/` — Pure IS 456 math
- `Python/structural_lib/visualization/geometry_3d.py` — 3D coordinate calculation
- **Previous:** Day 19 covers 3D visualization with React Three Fiber
- **Next:** Day 21 covers Docker containerization

**Day 21: Docker & Deployment** — Now that you understand how data flows through the stack, we'll containerize the whole thing. You'll learn how Docker packages all four layers into a single deployable image, how `docker-compose` connects the services, and how `./run.sh dev` launches everything with one command.