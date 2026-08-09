# Day 17: React Architecture & Stack — Building the Frontend for a Math Library

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** High
**Created:** 2026-04-08
**Last Updated:** 2026-04-08
**Prerequisites:** Days 1-16 (Python library + FastAPI)
**Library files:** `react_app/src/App.tsx`, `react_app/src/store/`, `react_app/src/components/`, `react_app/src/hooks/`
**Tech Stack:** React 19, TypeScript, Tailwind CSS, Zustand, React Three Fiber, Vite

---

## What You'll Learn Today

By the end of this module you'll understand:
- Why React 19 + TypeScript + Vite is the right stack for a structural engineering tool
- Feature-first folder structure that keeps related code together
- Tailwind CSS only — why zero custom CSS files (except one exception)
- Zustand stores vs Redux vs Context — why we chose minimal state management
- TypeScript strict mode and how it catches unit mistakes at compile time
- The complete data flow: User → Hook → API → Backend → Result → Store → Re-render

---

## Part 1: Why This Stack?

A structural engineering design tool has specific needs:

| Need | Solution | Why |
|------|----------|-----|
| Interactive 3D visualization | React Three Fiber (R3F) | Mature, React-native 3D — no separate rendering engine |
| Type safety for engineering values | TypeScript strict mode | `width: "300"` (string) caught at compile time |
| Fast dev server with hot reload | Vite | Sub-second rebuilds vs 10+ seconds with webpack |
| Minimal state management | Zustand | 2 stores, not 50 — Redux would be massive overkill |
| Consistent styling | Tailwind CSS | Utility classes inline — no CSS file hunting |
| Data fetching with caching | TanStack Query (React Query) | Caches API results, handles loading/error states |

**Why React 19 specifically?**
- **Concurrent rendering** — React works on multiple UI updates simultaneously. When the user drags a slider, the 3D preview updates smoothly even if the results panel is mid-render.
- **Automatic batching** — Multiple `setInputs()` calls in one event handler trigger ONE re-render, not many.
- **Ecosystem** — React Three Fiber is the most mature React 3D library. No Vue/Svelte equivalent with the same quality.

**What we DON'T use:**
- No SSR (Server-Side Rendering) — we're a SPA, no SEO needs
- No Next.js — overkill, we don't need routing frameworks or static generation
- No class components — everything is functional components with hooks

---

## Part 2: Feature-First Folder Structure

```
react_app/src/
├── components/          # UI components (grouped by FEATURE)
│   ├── design/          # Beam design: BeamForm, ResultsPanel, CrossSectionView
│   ├── import/          # CSV import: ImportView, CSVImportPanel, BeamTable
│   ├── viewport/        # 3D visualization: Viewport3D, WorkspaceLayout
│   ├── layout/          # App shell: TopBar, ModernAppLayout
│   ├── pages/           # Route-level: Home, BatchDesign, BeamDetail
│   └── ui/              # Shared primitives: Toast, FileDropZone, Skeleton
├── hooks/               # Custom hooks (data fetching, state logic)
├── store/               # Zustand stores (global state)
├── types/               # TypeScript type definitions
├── utils/               # Utility functions
├── App.tsx              # Root component (routing + providers)
└── main.tsx             # Entry point (mounts to DOM)
```

**The principle:** Group by **feature**, not by type.

```
❌ BAD: Group by type         ✅ GOOD: Group by feature
components/buttons/           components/design/      ← All design UI
components/forms/             components/import/      ← All import UI
components/modals/            components/viewport/    ← All 3D UI
```

**Why?** When working on beam design, everything you need is in `components/design/`. You don't hunt across 5 folders for "the design button" vs "the design form" vs "the design modal."

### Component hierarchy

```
App.tsx (routing + providers)
├── TopBar (always visible)
├── HomePage /
├── DesignView /design
│   ├── BeamForm (inputs → Zustand store)
│   ├── ResultsPanel (results from Zustand store)
│   └── CrossSectionView (3D visualization)
├── ImportView /import
│   ├── CSVImportPanel (file upload → API)
│   └── BeamTable (imported data display)
├── BuildingEditorPage /editor
│   └── Viewport3D (React Three Fiber canvas)
└── FloatingDock (always visible)
```

---

## Part 3: Tailwind CSS Only — Zero Custom CSS

**Rule:** Every component uses Tailwind utility classes inline. No `.css` files.

```tsx
// ✅ CORRECT — all styling in className
<div className="flex items-center gap-4 p-6 bg-zinc-900 rounded-lg shadow-lg">
  <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded">
    Design Beam
  </button>
</div>

// ❌ WRONG — requires BeamCard.css
<div className="beam-card">
  <button className="primary-button">Design Beam</button>
</div>
```

**Why Tailwind only?**

| Benefit | Explanation |
|---------|-------------|
| Consistency | Same spacing scale(`p-4`, `gap-6`), colors (`bg-zinc-900`), breakpoints (`md:flex-row`) |
| No naming conflicts | No BEM names like `.beam-card__button--primary` to invent |
| Easy refactoring | Change `bg-blue-600` to `bg-green-600` inline — no CSS file hunt |
| Tiny bundle | Vite purges unused classes. Final CSS ≈ 10KB |
| Dark theme built-in | `dark:` variant applies automatically based on system preference |

**The ONE exception:** `index.css` has CSS variables for Dockview (a third-party panel layout library). This is the only non-Tailwind CSS in the entire app.

**Responsive design with Tailwind:**
```tsx
<header className="
  flex items-center justify-between
  px-6 py-4 bg-zinc-900 border-b border-zinc-800
  md:px-8        /* 768px+ → larger padding */
  lg:px-12       /* 1024px+ → even larger padding */
">
```

---

## Part 4: Zustand Stores — Global State Management

### Why Zustand?

| Criteria | Redux | Context API | Zustand |
|----------|-------|-------------|---------|
| Boilerplate | Heavy (actions, reducers, thunks) | Light | **Minimal** |
| TypeScript | Good but verbose | Requires manual typing | **Inferred** |
| Re-renders | selective with selectors | ALL consumers re-render | **Selective** |
| DevTools | Yes | No | **Yes** |
| Our use case | Overkill (2 stores) | Too slow (3D updates) | **Perfect** |

### Store 1: `useDesignStore` — Single Beam Design

```tsx
// store/designStore.ts
import { create } from 'zustand';

export interface DesignState {
  inputs: BeamDesignRequest;
  length: number;
  result: BeamDesignResponse | null;
  isLoading: boolean;
  error: string | null;
  autoDesign: boolean;
  useWebSocket: boolean;

  setInputs: (inputs: Partial<BeamDesignRequest>) => void;
  setResult: (result: BeamDesignResponse | null) => void;
  setLoading: (loading: boolean) => void;
}

export const useDesignStore = create<DesignState>((set) => ({
  inputs: { width: 300, depth: 450, moment: 150, shear: 80, fck: 25, fy: 500 },
  length: 4000,
  result: null,
  isLoading: false,
  error: null,
  autoDesign: true,
  useWebSocket: false,

  setInputs: (inputs) => set((state) => ({
    inputs: { ...state.inputs, ...inputs }
  })),
  setResult: (result) => set({ result, error: null }),
  setLoading: (isLoading) => set({ isLoading }),
}));
```

**How selective re-rendering works:**
```tsx
// Only re-renders when inputs change (not when result changes)
const { inputs, setInputs } = useDesignStore();

// Only re-renders when result changes (not when inputs change)
const result = useDesignStore((state) => state.result);
```

### Store 2: `useImportedBeamsStore` — Batch CSV Beams

```tsx
// store/importedBeamsStore.ts
export const useImportedBeamsStore = create<ImportedBeamsState>((set) => ({
  beams: [],
  selectedIds: new Set(),
  designResults: new Map(),

  setBeams: (beams) => set({
    beams, selectedIds: new Set(), designResults: new Map()
  }),
  toggleSelection: (id) => set((state) => {
    const newSet = new Set(state.selectedIds);
    newSet.has(id) ? newSet.delete(id) : newSet.add(id);
    return { selectedIds: newSet };
  }),
  setDesignResult: (id, result) => set((state) => {
    const newMap = new Map(state.designResults);
    newMap.set(id, result);
    return { designResults: newMap };
  }),
}));
```

---

## Part 5: TypeScript Strict Mode

`tsconfig.json` has `"strict": true`. This means:
- No implicit `any` types
- No implicit `undefined` or `null`
- All function parameters must have types

**Why it matters for engineering:**
```tsx
// ❌ TypeScript ERROR: Argument of type 'string' is not assignable to 'number'
setInputs({ width: "300" });  // Would silently pass in JavaScript!

// ✅ OK
setInputs({ width: 300 });

// ❌ TypeScript ERROR: Property 'span' is missing
designBeam({ width: 300, depth: 450 });  // Forgot required field

// ✅ OK
designBeam({ width: 300, depth: 450, span: 4000 });
```

**Types mirror the backend Pydantic models:**
```tsx
// types/api.ts — matches Python BeamDesignRequest
export interface BeamDesignRequest {
  width: number;    // mm — matches b_mm in Python
  depth: number;    // mm — matches D_mm in Python
  moment: number;   // kNm — matches mu_knm in Python
  shear: number;    // kN — matches vu_kn in Python
  fck: number;      // N/mm² — matches fck_nmm2 in Python
  fy: number;       // N/mm² — matches fy_nmm2 in Python
}
```

If the Python API changes a field name, the TypeScript build fails — you catch the mismatch before the user does.

---

## Part 6: App.tsx — Routing and Providers

```tsx
// react_app/src/App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { lazy, Suspense } from 'react';

// Lazy-load routes for code splitting
const HomePage = lazy(() => import('./components/pages/HomePage'));
const DesignView = lazy(() => import('./components/design/DesignView'));
const ImportView = lazy(() => import('./components/import/ImportView'));
const BuildingEditorPage = lazy(() => import('./components/pages/BuildingEditorPage'));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,  // Cache API results for 5 minutes
      retry: 1,                    // Retry failed requests once
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="h-screen bg-zinc-950 text-zinc-100">
          <TopBar />
          <Suspense fallback={<LoadingSpinner />}>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/design" element={<DesignView />} />
              <Route path="/import" element={<ImportView />} />
              <Route path="/editor" element={<BuildingEditorPage />} />
              <Route path="/batch" element={<BatchDesignPage />} />
            </Routes>
          </Suspense>
          <FloatingDock />
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
```

**Key patterns:**
- `lazy()` + `Suspense` — Code splitting. `ImportView.tsx` isn't downloaded until the user navigates to `/import`
- `QueryClientProvider` — Wraps the app so all components can use `useQuery`/`useMutation` hooks
- `staleTime: 5 min` — If you design a beam then navigate away and back, the last result is cached. No unnecessary API call.

---

## Part 7: The Complete Data Flow

When the user types a new beam width and clicks "Design":

```
User types 350 in width field
    ↓
onChange → setInputs({ width: 350 })     [Zustand store update]
    ↓
autoDesign hook detects input change      [useLiveDesign / useAutoDesign]
    ↓
Hook calls POST /api/v1/design/beam       [TanStack Query mutation]
    ↓
FastAPI router → design_beam_is456()      [FastAPI + structural_lib]
    ↓
API returns JSON response                 [HTTP 200 + JSON body]
    ↓
onSuccess → setResult(data)               [Zustand store update]
    ↓
Components using 'result' re-render       [Selective Zustand subscription]
    ↓
ResultsPanel shows new Ast, xu values     [UI updated]
CrossSectionView re-renders 3D beam       [R3F re-renders mesh]
```

**No data lives in component state.** All shared data flows through Zustand stores. Components are pure views of store data.

---

## Part 8: Exercises

### Exercise 1: Run the dev server
```bash
cd react_app && npm run dev
```
Open `http://localhost:5173`. Explore:
1. `/design` — change width/depth, observe results updating
2. `/import` — drag a CSV file
3. Open DevTools → React Developer Tools → Components → find `useDesignStore`

### Exercise 2: Trace a state change
1. Open DevTools → Console
2. In the design view, change beam width
3. Watch the network tab — does a new API request fire?
4. Check the Zustand DevTools — what state changed?

### Exercise 3: Responsive breakpoints
1. In `/design`, resize the browser window from 1200px → 600px
2. Observe how the layout changes at `md:` (768px) and `lg:` (1024px) breakpoints
3. Inspect an element and look at the applied Tailwind classes

---

## Part 9: Self-Check Q&A

1. **Why React 19 instead of React 17?** Name two concrete features we use.
2. **Why group components by feature rather than by type?**
3. **Why Tailwind CSS only?** What's the one exception?
4. **What's the difference between `useDesignStore` and `useImportedBeamsStore`?**
5. **Why TypeScript strict mode?** Give a concrete bug it prevents.
6. **What happens when you call `setInputs({ width: 350 })`?** Trace the full path.
7. **Why Zustand over Redux?** Why over Context API?
8. **What does `lazy()` + `Suspense` do?** Why is it important for page load?
9. **What is `staleTime` in React Query?** Why 5 minutes?
10. **Why do TypeScript types mirror Python Pydantic models?**

---

## Part 10: Things to Know — Deep Insights

### 10.1: Zustand selectors prevent wasted re-renders
If you write `const store = useDesignStore()`, the component re-renders on ANY store change. If you write `const result = useDesignStore(s => s.result)`, it only re-renders when `result` changes. The 3D viewport should use selectors — it doesn't need to re-render when the user is just typing in a text field.

### 10.2: Vite HMR preserves state
When you edit a component file and save, Vite hot-module-replaces just that component. Zustand store state survives the reload — you don't lose your design inputs. This makes development fast because you're not re-entering beam dimensions after every code change.

### 10.3: React Three Fiber runs its own render loop
R3F renders at 60fps in a `<Canvas>` element. It doesn't use React's reconciliation for every frame — it uses Three.js's native render loop. React only reconciles when props/state change (e.g., when `result` updates). This is why the 3D preview is smooth even while React updates other parts of the UI.

### 10.4: TypeScript interfaces vs types for API contracts
The codebase uses `interface` for API contracts (`BeamDesignRequest`, `BeamDesignResponse`) and `type` for unions/intersections. Interfaces are extendable (`extends`), types are more flexible (`|`, `&`). For API contracts, interfaces are preferred because they produce clearer error messages.

### 10.5: Dark theme is the default
The entire UI uses `bg-zinc-950` (nearly black) as the base. This isn't just aesthetic — engineers often work in dimly lit offices, and light-on-dark reduces eye strain for long CAD-like sessions. The Tailwind `dark:` variant isn't needed because everything is already dark-themed.

### 10.6: No `useEffect` for API calls
The codebase uses TanStack Query instead of raw `useEffect` + `fetch`. Why? `useEffect` doesn't handle loading states, error states, caching, deduplication, or retry. React Query handles all of these with zero boilerplate.

---

## Part 11: What Can Be Done Better

### 11.1: No error boundary around 3D canvas
If React Three Fiber crashes (bad geometry data, WebGL context loss), the entire app crashes. An error boundary around `<Canvas>` would catch the crash and show a fallback UI instead of a blank screen.

### 11.2: No suspense for data loading
Routes use `Suspense` for code splitting, but data fetching doesn't use suspense. Components show their own loading spinners. React 19 supports Suspense for data, which would unify loading states.

### 11.3: TypeScript types are manually synced with Python
When `BeamDesignRequest` changes in Python, someone must manually update `types/api.ts` in TypeScript. There's no auto-generation from the OpenAPI spec. If they drift apart, the frontend silently sends wrong field names.

### 11.4: No i18n/l10n
All text is hardcoded in English. Structural engineering is global — IS 456 is used in India, neighboring countries adopt it too. Adding `react-intl` or `i18next` would be a significant but valuable effort.

### 11.5: Bundle analysis not checked regularly
Vite produces optimized builds, but nobody checks bundle sizes. A large npm dependency could sneak in and double the load time. Regular `npx vite-bundle-visualizer` runs would catch this.

---

## Part 12: Innovation Directions

### 12.1: Auto-generate TypeScript types from OpenAPI
The FastAPI server generates an OpenAPI spec at `/openapi.json`. Tools like `openapi-typescript` can auto-generate TypeScript interfaces from this spec. Zero manual type synchronization — if Python changes, regenerate the types.

### 12.2: React Server Components for reports
Report generation (PDF, design summary) could use React Server Components — render the report on the server, send HTML to the client. No client-side JS needed for static content.

### 12.3: Offscreen Canvas for 3D
React Three Fiber can render to an OffscreenCanvas in a Web Worker. This moves all 3D computation off the main thread, making the UI inputs and 3D visualization completely independent. Complex building models wouldn't slow down form interactions.

### 12.4: Zustand middleware for undo/redo
Zustand has a `temporal` middleware that records state history. Engineers could undo/redo design changes — change beam depth, see the result, undo, try a different depth. Built-in to the state manager, no custom code needed.

### 12.5: Progressive Web App (PWA)
With a service worker, the app could work offline — cached API responses for previously designed beams, offline form entry with sync-when-online. Useful for site engineers with intermittent internet.

---

## Part 13: Next Repo Must-Add

### Concrete items

1. **Error boundary for R3F Canvas** — Catch 3D crashes without killing the entire app
2. **Auto-generated TypeScript types** — `openapi-typescript` piped from `/openapi.json` in CI
3. **Bundle size budget** — CI check that fails if the build exceeds 500KB gzipped
4. **Zustand undo/redo** — `temporal` middleware for design input history
5. **Storybook for UI primitives** — Visual catalog of `components/ui/` for design consistency
6. **Accessibility audit** — `axe-core` integration — screen reader support for form inputs and results
7. **Performance monitoring** — React Profiler + Web Vitals reporting in production

### Day-1 checklist for a new React component

```
□ 1. Place in the correct feature folder (components/design/, components/import/, etc.)
□ 2. Use Tailwind CSS only — no .css files
□ 3. Define proper TypeScript interfaces for all props
□ 4. Use Zustand store for shared state, not local useState for data needed elsewhere
□ 5. Use TanStack Query for API calls, not raw useEffect + fetch
□ 6. Add responsive breakpoints (md: and lg:) for layout changes
□ 7. Check for existing hooks before creating new ones (ls react_app/src/hooks/)
□ 8. Check for existing UI primitives (components/ui/) before creating new ones
□ 9. Verify the build passes: cd react_app && npm run build
□ 10. Test in both desktop (1200px) and tablet (768px) widths
```

---

## 📎 References

- [React 19 Docs](https://react.dev)
- [Zustand Docs](https://github.com/pmndrs/zustand)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [TanStack Query Docs](https://tanstack.com/query)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [React Router Docs](https://reactrouter.com)
- [Vite Docs](https://vitejs.dev/guide/)
- `react_app/src/App.tsx` — Root component, routing, providers
- `react_app/src/store/designStore.ts` — Single beam design state
- `react_app/src/store/importedBeamsStore.ts` — Batch import state
- **Previous:** Day 16 covers FastAPI WebSocket, SSE, batch processing
- **Next:** Day 18 covers React hooks and custom data flow patterns
