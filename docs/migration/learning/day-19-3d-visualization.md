# Day 19: 3D Visualization — Rendering Concrete, Rebar & Stirrups with React Three Fiber

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** High
**Created:** 2026-04-08
**Last Updated:** 2026-04-08
**Prerequisites:** Day 17 (React architecture), Day 18 (React hooks)
**Library files:** `react_app/src/components/viewport/Viewport3D.tsx`, `react_app/src/hooks/useBeamGeometry.ts`, `Python/structural_lib/visualization/geometry_3d.py`
**Tech Stack:** React Three Fiber (R3F), Three.js, @react-three/drei

---

## What You'll Learn Today

By the end of this module you'll understand:
- What React Three Fiber is — 3D scenes as React components
- Why 3D visualization matters for a structural engineering tool
- The complete data flow: IS 456 design result → `geometry_3d.py` → 3D coordinates → R3F rendering
- How concrete beams, rebars, and stirrups are rendered
- Coordinate system conversion between Python library and Three.js
- Performance optimization with instancedMesh
- Camera, lighting, and interactive controls

---

## Part 1: What is React Three Fiber?

**React Three Fiber (R3F)** is a React renderer for Three.js. Instead of writing imperative 3D code, you write 3D scenes as React components:

```tsx
// IMPERATIVE Three.js (verbose, manual memory management)
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });
const mesh = new THREE.Mesh(geometry, material);
scene.add(mesh);
// Must manually: dispose geometry, dispose material, remove from scene

// DECLARATIVE R3F (React manages lifecycle)
<mesh>
  <boxGeometry args={[1, 1, 1]} />
  <meshStandardMaterial color="red" />
</mesh>
// React auto-disposes when component unmounts
```

**Why R3F instead of vanilla Three.js?**

| Feature | Three.js | R3F |
|---------|----------|-----|
| Style | Imperative | Declarative (React components) |
| Memory cleanup | Manual dispose() calls | Automatic on unmount |
| State updates | Manual scene graph mutation | React re-render = scene update |
| Ecosystem | Standalone | Full React hooks, context, suspense |
| Reusability | Copy-paste classes | `<BeamMesh>` components |

---

## Part 2: Why 3D for Structural Engineering?

2D drawings and tables are the standard. Here's what 3D adds:

1. **Visual verification** — See if rebar positions match reality. If a bar is outside the beam, you spot it instantly in 3D. In a table, "bar at y=460" looks fine until you realize depth is 450.
2. **Communication** — Show a contractor where bars go. "4-#25 @ 40mm cover" is abstract. A 3D view with orange bars inside a gray box is obvious.
3. **Debugging** — When the detailing code has a bug (bars overlapping, stirrups at wrong spacing), the 3D render makes it immediately visible.
4. **Education** — New engineers learn faster seeing theory → actual bar placement in real-time.

**What we render:**

| Element | 3D Shape | Material | Purpose |
|---------|----------|----------|---------|
| Concrete beam | Box (transparent) | Gray, 70% opacity | Shows overall dimensions |
| Longitudinal rebar | Cylinders | Orange, metallic | Tension/compression bars |
| Stirrups | Rectangular loops | Orange, thin | Shear reinforcement |
| Grid | Flat plane | Gray lines | Scale reference |
| Dimensions | Text labels | White | Width × Depth labels |

---

## Part 3: The Three Building Blocks

Every R3F scene uses three fundamental components:

### `<Canvas>` — The Root Container
```tsx
<Canvas camera={{ position: [6, 4, 6], fov: 50 }}>
  {/* All 3D content goes inside Canvas */}
</Canvas>
```
Like `<div>` in HTML, but creates a WebGL context and render loop (60fps).

### `<mesh>` — A Renderable Object
```tsx
<mesh position={[0, 1, 0]} rotation={[0, Math.PI / 4, 0]}>
  <boxGeometry args={[1, 2, 3]} />       {/* Shape: width=1, height=2, depth=3 */}
  <meshStandardMaterial color="blue" />    {/* Appearance: blue, realistic lighting */}
</mesh>
```
Every mesh = geometry (shape) + material (appearance).

### `<group>` — Container for Grouping
```tsx
<group position={[10, 0, 0]}>  {/* Offset everything inside by 10m right */}
  <mesh>...</mesh>   {/* Inherits the group's position */}
  <mesh>...</mesh>
</group>
```
Like `<div>` — lets you transform (move, rotate, scale) multiple objects together.

---

## Part 4: Coordinate System Conversion

**Python library uses** (structural engineering convention):
- X → beam length (along span)
- Y → beam width (cross-section horizontal)
- Z → beam depth (cross-section vertical)

**Three.js uses** (game engine convention):
- X → horizontal (left/right)
- Y → vertical (up/down) ← THIS IS THE KEY DIFFERENCE
- Z → depth (forward/backward)

**The conversion:**
```tsx
// Library returns: { x: 2000, y: 150, z: 450 } (mm)
// Convert to Three.js:
const SCALE = 0.001;  // mm → meters (better camera framing)
const threejsPosition = [
  point.x * SCALE,    // X stays X (along beam)
  point.z * SCALE,    // Z (library depth) → Y (Three.js up)
  point.y * SCALE,    // Y (library width) → Z (Three.js depth)
];
```

If you get this wrong, beams appear sideways or bars float above the concrete. This is the most common 3D bug.

---

## Part 5: The Complete Data Flow

```
1. User designs beam (width=300, depth=450, fck=25, fy=500)
       ↓
2. useLiveDesign → POST /api/v1/design/beam → IS 456 math
       ↓
3. Result: Ast_provided=942mm², stirrup_dia=8, stirrup_spacing=150
       ↓
4. useBeamGeometry → POST /api/v1/geometry/beam/full
       ↓
5. Python geometry_3d.beam_to_3d_geometry() calculates:
   - Bottom rebar at y = cover + dia/2 = 40 + 12.5 = 52.5mm from bottom
   - Top rebar at y = depth - cover - dia/2 = 450 - 40 - 12.5 = 397.5mm
   - Stirrup loops every 150mm along span
       ↓
6. Returns JSON: { rebars: [{segments: [start, end, dia]}], stirrups: [...] }
       ↓
7. R3F renders each segment as a <mesh> with <cylinderGeometry>
       ↓
8. User sees 3D beam with orange bars inside gray transparent concrete
```

---

## Part 6: Viewport3D — The Canvas Setup

```tsx
// components/viewport/Viewport3D.tsx
export function Viewport3D() {
  const { inputs, result } = useDesignStore();

  return (
    <div className="h-full w-full bg-zinc-950">
      <Canvas
        camera={{ position: [6, 4, 6], fov: 50 }}
        gl={{ antialias: true, alpha: false }}
      >
        {/* Lighting */}
        <ambientLight intensity={0.6} />
        <directionalLight position={[10, 10, 5]} intensity={0.8} />
        <Environment preset="city" />

        {/* Grid reference */}
        <Grid args={[20, 20]} cellSize={1} cellColor="#444" sectionColor="#666" />

        {/* Camera controls — drag to rotate, scroll to zoom */}
        <OrbitControls makeDefault maxPolarAngle={Math.PI / 2} />

        {/* 3D beam content */}
        <Suspense fallback={null}>
          <BeamVisualization inputs={inputs} result={result} />
        </Suspense>
      </Canvas>
    </div>
  );
}
```

**Lighting strategy:**
- `ambientLight` — Soft overall illumination (prevents pure black shadows)
- `directionalLight` — Main light from upper-right (like the sun — creates depth perception)
- `Environment preset="city"` — HDRI reflections (metallic rebar looks shiny and realistic)

**Camera:**
- `position={[6, 4, 6]}` — Start at 6m right, 4m up, 6m forward — good initial view of a 4m beam
- `fov={50}` — 50° field of view (natural perspective, not fisheye)
- `OrbitControls` — Mouse drag rotates, scroll zooms, right-click pans

---

## Part 7: Rendering the Concrete Beam

```tsx
function BeamMesh({ width, depth, length, isDesigned }: BeamMeshProps) {
  const SCALE = 0.001;  // mm → meters
  const w = width * SCALE;
  const d = depth * SCALE;
  const l = length * SCALE;

  return (
    <mesh position={[0, d / 2, 0]}>
      <boxGeometry args={[l, d, w]} />
      <meshStandardMaterial
        color={isDesigned ? '#b0b0b0' : '#909090'}
        metalness={0.1}     // Concrete is not metallic
        roughness={0.85}    // Concrete is rough/matte
        transparent
        opacity={isDesigned ? 0.7 : 0.9}  // See-through when designed (rebar visible)
      />
    </mesh>
  );
}
```

**Why transparent?** When `isDesigned=true`, the beam is 70% opaque so the rebar inside is visible. Before design, it's 90% opaque (just a gray box).

---

## Part 8: Rendering Rebars

Each rebar is a series of straight segments. Each segment becomes a `<cylinderGeometry>`:

```tsx
function RebarVisualization({ rebars }: { rebars: RebarPath[] }) {
  return (
    <group>
      {rebars.map((rebar, rIdx) =>
        rebar.segments.map((segment, sIdx) => {
          const SCALE = 0.001;

          // Convert library coordinates to Three.js
          const start = [
            segment.start.x * SCALE,
            segment.start.z * SCALE,  // Z → Y (depth → up)
            segment.start.y * SCALE,  // Y → Z (width → depth)
          ];
          const end = [
            segment.end.x * SCALE,
            segment.end.z * SCALE,
            segment.end.y * SCALE,
          ];

          const midpoint = [
            (start[0] + end[0]) / 2,
            (start[1] + end[1]) / 2,
            (start[2] + end[2]) / 2,
          ];

          const length = segment.length * SCALE;
          const radius = (segment.diameter / 2) * SCALE;

          // Align cylinder with bar direction using quaternion rotation
          const dir = new THREE.Vector3(...end).sub(new THREE.Vector3(...start)).normalize();
          const yAxis = new THREE.Vector3(0, 1, 0);
          const quat = new THREE.Quaternion().setFromUnitVectors(yAxis, dir);

          return (
            <mesh key={`${rIdx}-${sIdx}`} position={midpoint} quaternion={quat}>
              <cylinderGeometry args={[radius, radius, length, 8]} />
              <meshStandardMaterial color="#d97706" metalness={0.6} roughness={0.3} />
            </mesh>
          );
        })
      )}
    </group>
  );
}
```

**Key details:**
- `cylinderGeometry args={[radius, radius, length, 8]}` — Top radius, bottom radius (same = uniform bar), height, 8-sided cross-section (octagon — fast enough, looks round)
- `quaternion` — Rotates the cylinder to align with the bar direction. Quaternions avoid "gimbal lock" (a problem with Euler angles where certain rotations get stuck)
- `color="#d97706"` — Orange/amber, representing steel rebar
- `metalness={0.6}` — Rebar is metallic (steel)

---

## Part 9: Performance — InstancedMesh for Stirrups

A 4m beam with 150mm stirrup spacing = 26+ stirrups. Each stirrup has 4 sides = 100+ cylinders. Rendering each as a separate `<mesh>` means 100+ draw calls.

**InstancedMesh renders ALL instances in ONE draw call:**

```tsx
function StirrupVisualization({ stirrups }: { stirrups: StirrupLoop[] }) {
  const meshRef = useRef<THREE.InstancedMesh>(null);

  useEffect(() => {
    if (!meshRef.current) return;
    const matrix = new THREE.Matrix4();

    stirrups.forEach((stirrup, i) => {
      matrix.setPosition(stirrup.x * SCALE, stirrup.z * SCALE, stirrup.y * SCALE);
      meshRef.current!.setMatrixAt(i, matrix);
    });
    meshRef.current.instanceMatrix.needsUpdate = true;
  }, [stirrups]);

  return (
    <instancedMesh ref={meshRef} args={[undefined, undefined, stirrups.length]}>
      <boxGeometry args={[0.002, 0.4, 0.28]} />  {/* Thin rectangle */}
      <meshStandardMaterial color="#d97706" metalness={0.5} />
    </instancedMesh>
  );
}
```

**Performance impact:**
- 100 individual meshes = 100 draw calls → 30 FPS on mobile
- 1 instancedMesh with 100 instances = 1 draw call → 60 FPS on mobile

---

## Part 10: Exercises

### Exercise 1: Run the 3D viewport
```bash
cd react_app && npm run dev
```
1. Navigate to `/design`, fill in beam dimensions, click "Design"
2. Drag to rotate the 3D view, scroll to zoom
3. Inspect the orange rebars inside the transparent concrete
4. Change beam width from 300 to 500 — watch the 3D update

### Exercise 2: Change the beam color
In the BeamMesh code, change:
```tsx
color={isDesigned ? '#b0b0b0' : '#909090'}
```
to:
```tsx
color={isDesigned ? '#3b82f6' : '#909090'}
```
Save — the designed beam turns blue instead of gray.

### Exercise 3: Add a floating text label
```tsx
import { Text } from '@react-three/drei';

<Text position={[0, 3, 0]} fontSize={0.3} color="white">
  Beam: {inputs.width}×{inputs.depth}mm
</Text>
```

---

## Part 11: Self-Check Q&A

1. **What is React Three Fiber?** A React renderer for Three.js — write 3D as components.
2. **Why 3D for structural engineering?** Visual verification, debugging, communication, education.
3. **What are the 3 building blocks?** `<Canvas>`, `<mesh>`, `<group>`.
4. **Why is the beam transparent?** So rebar inside is visible.
5. **What coordinate conversion happens?** Library Z (depth) → Three.js Y (up), Library Y (width) → Three.js Z.
6. **What is instancedMesh?** Renders many identical shapes in 1 draw call. Used for stirrups.
7. **Why quaternion instead of Euler rotation?** Avoids gimbal lock.
8. **What does `geometry_3d.py` return?** RebarPath[] (segments with start/end/diameter) and StirrupLoop[] (3D loop coordinates).
9. **What is `enabled` in `useBeamGeometry`?** Prevents fetching when inputs are invalid (width=0).
10. **Why `metalness={0.6}` for rebar but `metalness={0.1}` for concrete?** Steel is metallic, concrete is not.

---

## Part 12: Things to Know — Deep Insights

### 12.1: R3F has its own render loop separate from React
React Three Fiber renders at 60fps using Three.js's native `requestAnimationFrame` loop. React's reconciler only runs when props/state change — it doesn't run every frame. This means the 3D scene stays smooth even when React is busy updating the form inputs. The `useFrame` hook taps into the 60fps loop for animations.

### 12.2: WebGL context loss is a real production issue
On mobile devices and some laptops, the browser can "lose" the WebGL context (GPU gets reclaimed by the OS). When this happens, the 3D canvas goes blank. R3F doesn't auto-recover from this. You need an event listener on `webglcontextlost` to show a fallback message and `webglcontextrestored` to re-render.

### 12.3: Memory leaks from unmounted 3D objects
In vanilla Three.js, you must call `geometry.dispose()` and `material.dispose()` manually. R3F handles this automatically on component unmount — but only for objects created via JSX. If you imperatively create `new THREE.BufferGeometry()` inside a `useEffect`, you must dispose it in the cleanup return.

### 12.4: `<Suspense fallback={null}>` prevents blank canvas
Without Suspense, if `useBeamGeometry` is loading, the entire Canvas crashes because a child tries to access undefined geometry. `Suspense` catches the loading state and shows nothing (or a loading indicator) until data arrives. Always wrap data-dependent 3D content in Suspense.

### 12.5: The SCALE factor isn't arbitrary
`0.001` converts mm to meters. Three.js cameras work best with scene dimensions of 1-100 units. A beam of 4000mm = 4 units = good. A beam of 4000 units (without scaling) would break float precision at the camera's near/far clipping planes.

### 12.6: 8 segments for cylinder geometry is a deliberate optimization
`cylinderGeometry args={[r, r, length, 8]}` — the `8` makes each rebar bar an octagon cross-section, not a smooth circle. At the zoom levels users view beams, you can't tell the difference between 8 and 32 segments. But 8 segments = 4× fewer triangles = much faster rendering for 50+ bars.

---

## Part 13: What Can Be Done Better

### 13.1: No error boundary around `<Canvas>`
If R3F crashes (bad geometry, WebGL context loss), the entire app goes blank. An error boundary wrapping `<Canvas>` would catch the crash and show "3D unavailable — here are your results as a table" instead.

### 13.2: No level-of-detail (LOD)
When zoomed out, stirrups are tiny and still rendered with full geometry. A LOD system would simplify distant objects (fewer triangles) or hide them entirely, improving performance for large building models.

### 13.3: No screenshot/export
Users can't save the 3D view as an image. Adding `canvas.toDataURL()` would let users download a PNG of the current view for reports or presentations.

### 13.4: No cross-section view
The 3D view shows the full beam. A 2D cross-section view (looking along the beam axis) would clearly show bar arrangement — useful for comparing with traditional detailing drawings.

### 13.5: No measurement tool
Users can't click two points and see the distance. A measurement tool would let engineers verify cover, spacing, or bar positions directly in the 3D view.

---

## Part 14: Innovation Directions

### 14.1: OffscreenCanvas in Web Worker
Move the entire Three.js render to a Web Worker via OffscreenCanvas. The 3D rendering won't block the main thread — form inputs stay responsive even during complex building visualization. R3F support is experimental but improving.

### 14.2: AR/VR visualization
Three.js supports WebXR for augmented/virtual reality. An engineer could view the beam in AR on their phone — hold it up at the construction site and overlay the designed rebar arrangement on the actual beam. R3F has `<XR>` support.

### 14.3: Animated construction sequence
Show rebars being placed step-by-step: first bottom bars, then stirrups, then top bars. This animated sequence helps contractors understand installation order and is excellent for training.

### 14.4: Clash detection
Highlight when two rebars occupy the same space, or when a bar is too close to another (minimum spacing violation). This is a common issue in dense reinforcement zones and requires checking every bar pair for intersection.

### 14.5: Multi-element building visualization
Instead of single beams, render an entire floor plan — beams, columns, slabs — in one 3D scene. The user clicks an element to inspect its design. Uses instancedMesh heavily for performance.

---

## Part 15: Next Repo Must-Add

### Concrete items

1. **Error boundary for Canvas** — Graceful fallback on WebGL crash
2. **Screenshot/export button** — `canvas.toDataURL('image/png')` → download
3. **Cross-section 2D view** — Looking along beam axis, showing bar arrangement
4. **Level-of-detail** — Simplify distant objects, hide tiny details when zoomed out
5. **WebGL context recovery** — Listen for `webglcontextlost`, show message, auto-recover
6. **Measurement tool** — Click two points, display distance
7. **Loading skeleton** — Show beam outline immediately, load rebar detail progressively

### Day-1 checklist for a new 3D component

```
□ 1. Place in components/viewport/ folder
□ 2. Apply SCALE (0.001) conversion — mm → meters
□ 3. Convert coordinates: Library Z → Three.js Y, Library Y → Three.js Z
□ 4. Use instancedMesh if rendering >10 identical shapes
□ 5. Set appropriate metalness/roughness (steel: 0.5-0.7/0.2-0.4, concrete: 0.1/0.8)
□ 6. Wrap data-dependent content in <Suspense> inside Canvas
□ 7. Dispose any imperatively created geometry in useEffect cleanup
□ 8. Test with OrbitControls — does the object appear at a reasonable position?
□ 9. Check performance: aim for 60fps with 100 stirrups
□ 10. Verify the React build passes: cd react_app && npm run build
```

---

## 📎 References

- [React Three Fiber Docs](https://docs.pmnd.rs/react-three-fiber)
- [Three.js Docs](https://threejs.org/docs/)
- [@react-three/drei Helpers](https://github.com/pmndrs/drei)
- `react_app/src/components/viewport/Viewport3D.tsx` — Main 3D canvas
- `react_app/src/hooks/useBeamGeometry.ts` — Geometry data hook
- `Python/structural_lib/visualization/geometry_3d.py` — 3D coordinate calculator
- **Previous:** Day 18 covers React hooks (data flow, React Query, custom hooks)
- **Next:** Day 20 covers end-to-end data flow (full pipeline: CSV → design → 3D → export)
