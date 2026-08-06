---
owner: Main Agent
status: active
last_updated: 2026-08-07
doc_type: tutorial
complexity: beginner
tags: [learning, foundations]
---

# Module 7: Frontend — UI, Components, and State

## The Big Idea

The **frontend** is everything the user sees and interacts with — buttons, forms, charts, 3D views. Modern frontends are built from small, reusable **components** that manage their own **state** (data) and react to user actions.

---

## Part 1: What Is a Frontend?

```
┌───────────────────────────────────────────────────┐
│                   THE BROWSER                      │
│                                                   │
│  ┌─────────────────────────────────────────────┐  │
│  │              YOUR FRONTEND                   │  │
│  │                                             │  │
│  │  ┌─────────┐  ┌──────────┐  ┌───────────┐  │  │
│  │  │  Forms  │  │  3D View │  │  Results  │  │  │
│  │  │(input)  │  │(R3F/3js) │  │ (tables)  │  │  │
│  │  └─────────┘  └──────────┘  └───────────┘  │  │
│  │                                             │  │
│  │  Built with: HTML + CSS + JavaScript        │  │
│  └─────────────────────────────────────────────┘  │
│                                                   │
│  Talks to backend via HTTP ──→ FastAPI ──→ Python  │
└───────────────────────────────────────────────────┘
```

Three building blocks:
- **HTML** — Structure (what elements exist)
- **CSS** — Appearance (how they look)
- **JavaScript** — Behavior (what happens when you click)

Modern frameworks (React) combine all three into components.

---

## Part 2: React — Components as Building Blocks

**React** is a library for building UIs from reusable components.

### What's a component?

A component is a function that returns what should be displayed:

```tsx
// A simple component
function Greeting() {
  return <h1>Hello, Engineer!</h1>;
}

// A component with data (props)
function BeamLabel({ width, depth }: { width: number; depth: number }) {
  return <p>Beam: {width}mm × {depth}mm</p>;
}

// Using components (composition)
function App() {
  return (
    <div>
      <Greeting />
      <BeamLabel width={300} depth={500} />
    </div>
  );
}
```

### JSX — HTML inside JavaScript
```tsx
// This looks like HTML but it's actually JavaScript (JSX)
function ResultCard({ value, label }: { value: number; label: string }) {
  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <span className="text-sm text-gray-500">{label}</span>
      <span className="text-2xl font-bold">{value.toFixed(1)} mm²</span>
    </div>
  );
}
```

### Components compose (nest inside each other):
```
App
├── TopBar
│   ├── Logo
│   └── Navigation
├── DesignView
│   ├── BeamForm          ← Input form
│   │   ├── NumberInput    ← Width
│   │   ├── NumberInput    ← Depth
│   │   └── SubmitButton
│   ├── ResultsPanel      ← Design results
│   │   ├── FlexureResult
│   │   └── ShearResult
│   └── CrossSectionView  ← Visual diagram
└── Footer
```

---

## Part 3: Props — Passing Data Down

**Props** (properties) are how parent components send data to child components.

```tsx
// Parent passes data to child via props
function ParentPage() {
  return <BeamCard width={300} depth={500} status="SAFE" />;
}

// Child receives and uses props
function BeamCard({ width, depth, status }: {
  width: number;
  depth: number;
  status: string;
}) {
  return (
    <div>
      <h3>Beam: {width} × {depth} mm</h3>
      <span>{status === "SAFE" ? "✅ Safe" : "❌ Unsafe"}</span>
    </div>
  );
}
```

**Data flows ONE direction:** parent → child (never child → parent directly).

```
     Parent
    ┌──┴──┐
    │props│
    ▼     ▼
 Child A  Child B
```

---

## Part 4: State — Data That Changes

**State** is data that can change over time. When state changes, React re-renders the component.

### useState — local state
```tsx
import { useState } from "react";

function BeamForm() {
  // State: current value + function to change it
  const [width, setWidth] = useState(300);   // starts at 300
  const [depth, setDepth] = useState(500);   // starts at 500

  return (
    <div>
      <input
        type="number"
        value={width}
        onChange={(e) => setWidth(Number(e.target.value))}
      />
      <input
        type="number"
        value={depth}
        onChange={(e) => setDepth(Number(e.target.value))}
      />
      <p>Area: {width * depth} mm²</p>
    </div>
  );
}
```

### How state triggers re-render:
```
1. User types "350" in width input
2. onChange fires → setWidth(350)
3. React re-renders BeamForm with width = 350
4. Screen updates: Area shows 350 × 500 = 175000
```

---

## Part 5: Hooks — Reusable Logic

**Hooks** are functions that let you "hook into" React features. They start with `use`.

### Built-in hooks:
```tsx
// useState — manage local data
const [value, setValue] = useState(0);

// useEffect — run code when something changes
useEffect(() => {
  console.log("Width changed to:", width);
}, [width]);  // runs when 'width' changes

// useRef — reference a DOM element
const inputRef = useRef<HTMLInputElement>(null);
```

### Custom hooks — reusable logic:
```tsx
// Custom hook that calls the design API
function useLiveDesign(input: BeamInput) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetch("/api/v1/design/beam", {
      method: "POST",
      body: JSON.stringify(input),
    })
      .then((res) => res.json())
      .then((data) => {
        setResult(data);
        setLoading(false);
      });
  }, [input]);  // Re-fetch when input changes

  return { result, loading };
}

// Use it in any component
function DesignView() {
  const { result, loading } = useLiveDesign({ b_mm: 300, d_mm: 500, ... });

  if (loading) return <p>Designing...</p>;
  return <ResultsPanel data={result} />;
}
```

### This project's key custom hooks:

| Hook | Purpose |
|------|---------|
| `useCSVFileImport` | Upload CSV, send to API, get parsed beams |
| `useBeamGeometry` | Get 3D coordinates from API |
| `useLiveDesign` | Auto-design beam as inputs change |
| `useBatchDesign` | Design multiple beams via SSE |
| `useExport` | Download BBS/DXF/Report files |

---

## Part 6: State Management — Sharing Data Between Components

### Problem: Two sibling components need the same data
```
          App
         ┌─┴─┐
    BeamForm  ResultsPanel
    (has width)  (needs width — how?)
```

### Solution 1: Lift state up
```tsx
function App() {
  const [width, setWidth] = useState(300);  // State lives in parent

  return (
    <>
      <BeamForm width={width} onChange={setWidth} />
      <ResultsPanel width={width} />
    </>
  );
}
```

### Solution 2: Global state store (Zustand)
When many components need the same data, use a global store.

```tsx
import { create } from "zustand";

// Define the store
interface DesignStore {
  width: number;
  depth: number;
  result: BeamResult | null;
  setWidth: (w: number) => void;
  setDepth: (d: number) => void;
  setResult: (r: BeamResult) => void;
}

const useDesignStore = create<DesignStore>((set) => ({
  width: 300,
  depth: 500,
  result: null,
  setWidth: (w) => set({ width: w }),
  setDepth: (d) => set({ depth: d }),
  setResult: (r) => set({ result: r }),
}));

// Any component can read and write
function BeamForm() {
  const { width, setWidth } = useDesignStore();
  return <input value={width} onChange={(e) => setWidth(+e.target.value)} />;
}

function ResultsPanel() {
  const result = useDesignStore((s) => s.result);
  return <div>{result?.Ast_mm2} mm²</div>;
}
```

### This project's stores:

| Store | What It Holds |
|-------|--------------|
| `useDesignStore` | Current beam inputs + design results |
| `useImportedBeamsStore` | Imported CSV beams + selection state |

---

## Part 7: Tailwind CSS — Styling With Utility Classes

Instead of writing CSS files, Tailwind gives you small utility classes.

### Traditional CSS:
```css
/* styles.css */
.card {
  padding: 16px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
```

### Tailwind CSS:
```tsx
// No CSS file needed — classes directly in JSX
<div className="p-4 bg-white rounded-lg shadow">
  Content
</div>
```

### Common Tailwind classes:

| Category | Class | CSS equivalent |
|----------|-------|---------------|
| Padding | `p-4` | `padding: 16px` |
| Margin | `mt-2` | `margin-top: 8px` |
| Background | `bg-blue-500` | `background-color: #3b82f6` |
| Text | `text-lg font-bold` | `font-size: 1.125rem; font-weight: 700` |
| Flex | `flex items-center gap-2` | `display: flex; align-items: center; gap: 8px` |
| Grid | `grid grid-cols-3` | `display: grid; grid-template-columns: repeat(3, 1fr)` |
| Border | `border rounded-lg` | `border: 1px solid; border-radius: 8px` |
| Responsive | `md:grid-cols-2` | `@media (min-width: 768px) { grid-template-columns: repeat(2, 1fr) }` |

**Rule in this project:** All styling uses Tailwind. No custom CSS files (except Dockview theme in `index.css`).

---

## Part 8: Vite — The Build Tool

**Vite** (French for "fast") is the build tool for React projects.

### Development mode:
```bash
cd react_app && npm run dev
# → Starts at http://localhost:5173
# → Changes show instantly (Hot Module Replacement)
```

### Production build:
```bash
cd react_app && npm run build
# → Creates optimized files in dist/
# → Minified, tree-shaken, ready for deployment
```

### What Vite does:
```
Development:
  You save a file → Vite detects change → Browser updates instantly (no page reload)

Production:
  All .tsx files → bundled into a few .js files
  All CSS → combined and minified
  Unused code → removed (tree-shaking)
  Images → optimized
```

---

## Part 9: 3D Visualization with React Three Fiber (R3F)

This project uses **React Three Fiber** to show 3D beam cross-sections and rebar layouts.

```tsx
import { Canvas } from "@react-three/fiber";

function BeamVisualization({ geometry }) {
  return (
    <Canvas camera={{ position: [5, 5, 5] }}>
      {/* Lighting */}
      <ambientLight />
      <directionalLight position={[10, 10, 5]} />

      {/* Beam concrete body */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[geometry.width, geometry.depth, geometry.length]} />
        <meshStandardMaterial color="gray" opacity={0.5} transparent />
      </mesh>

      {/* Rebars */}
      {geometry.rebars.map((rebar, i) => (
        <mesh key={i} position={rebar.position}>
          <cylinderGeometry args={[rebar.radius, rebar.radius, geometry.length]} />
          <meshStandardMaterial color="red" />
        </mesh>
      ))}

      {/* Controls (orbit, zoom) */}
      <OrbitControls />
    </Canvas>
  );
}
```

The actual coordinates come from the backend (`/api/v1/geometry/beam/full`), not calculated in React.

---

## Part 10: This Project's Frontend Structure

```
react_app/src/
├── components/
│   ├── design/          ← Beam design UI
│   │   ├── DesignView.tsx       ← Main design page
│   │   ├── BeamForm.tsx         ← Input form
│   │   ├── ResultsPanel.tsx     ← Results display
│   │   └── CrossSectionView.tsx ← 2D cross-section
│   ├── import/          ← CSV import UI
│   │   ├── ImportView.tsx
│   │   └── BeamTable.tsx
│   ├── viewport/        ← 3D visualization
│   │   └── Viewport3D.tsx
│   ├── layout/          ← App shell
│   │   └── TopBar.tsx
│   ├── pages/           ← Route-level pages
│   │   ├── Home.tsx
│   │   └── BeamDetail.tsx
│   └── ui/              ← Shared components
│       ├── FileDropZone.tsx
│       └── Toast.tsx
├── hooks/               ← Custom hooks
├── store/               ← Zustand stores
├── types/               ← TypeScript type definitions
└── App.tsx              ← Root component
```

---

## Part 11: Exercises

1. **Read a component:** Open `react_app/src/components/design/BeamForm.tsx`. Identify: props, state, event handlers.
2. **Find the hooks:** List all hooks in `react_app/src/hooks/`. What does each one do?
3. **Trace data flow:** When a user changes "width" in the form, what components re-render?
4. **Tailwind challenge:** Build a card component with: padding, rounded corners, shadow, title text, subtitle text — using only Tailwind classes.

---

## Part 12: Self-Check

1. **What is a React component?** A function that returns JSX (describes what to display).
2. **What are props?** Data passed from parent to child component.
3. **What is state?** Data that can change, triggering a re-render.
4. **What is a custom hook?** A reusable function that encapsulates logic with React hooks.
5. **Why is data flow one-directional in React?** To make data changes predictable and debuggable.
6. **Why Tailwind instead of CSS files?** Faster development, co-located with components, no naming conflicts.

---

## Key Takeaway

> A frontend is built from **small, composable pieces**. Components handle display. Hooks handle logic. Stores handle shared data. Build tools handle optimization. You don't need to understand all of React on day one — start with components and props, add hooks and state as needed.

**Next:** [Module 8 — Backend](08-backend.md) explains the server that processes requests and runs the actual calculations.
