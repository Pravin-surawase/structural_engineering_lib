# AI Workspace Expansion - Research & Architecture (V3)

**Type:** Research
**Audience:** Developers
**Status:** Draft (POST-LAUNCH - Do not start before March 2026)
**Importance:** Critical
**Created:** 2026-01-21
**Last Updated:** 2026-01-21 (V3.1 - LLM Integration + Migration Roadmap)
**Scope:** Beams only (IS 456 / IS 13920 focus)
**Stack Decision:** React + React Three Fiber + FastAPI
**Prerequisites:** Complete 8-week plan Phase 4, launch Streamlit v1.0
**Related:** [8-week-development-plan.md](../planning/8-week-development-plan.md), [ai-workspace-expansion-v2.md](ai-workspace-expansion-v2.md)

---

## Executive Summary

We will keep the library as the primary strength and move the product UI to a premium, workspace-first shell built on React + React Three Fiber (R3F). The research confirms that premium feel will come from:

- An IDE-like workspace (dockable panels, saved layouts).
- A performance-first rendering pipeline (instancing, LOD, delta updates).
- A command/event model with revision history and diffs.
- Automation for non-coders (playbooks and recipes).

Scope is intentionally narrow: beams only. This lets us build a complete and professional beam pipeline before expanding to columns and slabs.

---

## 1. Scope and Non-Goals

**In scope (v3):**
- Beam design, detailing, checks, and optimization.
- ETABS import and mapping report.
- Beam-line standardization and constructability.
- Premium workspace UI for beam workflows.

**Out of scope (for now):**
- Columns, slabs, walls, footings.
- IFC/BIM full viewer integration.
- Multi-discipline coordination.

---

## 2. Stack Decision: Three.js + React Three Fiber

We choose R3F as the main 3D stack because it gives:
- Declarative scene composition aligned with React state (R3F docs).
- Access to full Three.js features without impedance.
- A strong ecosystem for performance and visuals.

### 2.1 Why R3F fits this product

- UI and 3D should share state and update together.
- R3F integrates with React toolchains (Next.js, hooks, suspense).
- It is not slower than raw Three.js and keeps feature parity (R3F docs).

### 2.2 Risks and mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| SSR incompatibility for WebGL | Medium | Client-only rendering, dynamic imports in Next.js |
| React/Three version mismatch | Medium | Lock versions and test in CI |
| Performance drops on large scenes | High | Instancing, LOD, delta updates, selective redraw |

### 2.3 Renderer performance research

Key Three.js capabilities we will use:
- Instanced meshes for rebar (Three.js InstancedMesh).
- WebGPU renderer where available, fallback to WebGL (Three.js WebGPURenderer).
- GPU-friendly materials and simple post FX.

---

## 3. Premium Workspace UX (Non-Negotiable)

A premium product in this domain feels like an IDE, not a chat UI.

### 3.1 Dockable panels and layouts

Use a docking layout system to create an IDE-style workspace:
- Dockview is a modern docking layout for React.
- GoldenLayout is a fallback but older in feel.

### 3.2 Pro data grid

AG Grid is the standard for large, editable engineering tables:
- Virtualized rows and columns.
- Filters, grouping, and inline edits.
- Works well for failure dashboards and optimization tables.

### 3.3 Required panels (beams-only scope)

- 3D building view (select, isolate story or beam line).
- Failure dashboard (table with filters and badges).
- Beam editor (bars, stirrups, constraints).
- Optimization table (before/after, apply/revert).
- History/diff panel (revision tracking).
- Export panel (BBS, DXF, report pack).

---

## 4. Architecture: Command/Event Model + Delta Updates

Premium UX is only possible if the backend and frontend share a reliable state model.

### 4.1 Command/event pattern

All changes are commands:
- EditRebar(beam_id, new_bars)
- OptimizeBeam(beam_id, target, constraints)
- StandardizeBeamLine(line_id, rules)

Commands produce:
- New state snapshot
- Deltas (geometry, checks, cost)
- Audit log entry

### 4.2 Delta updates

Only update what changed:
- Patch only affected rows in the grid.
- Update only the beam instance in 3D.
- Stream progress updates for long operations.

This enables instant feedback and avoids slow full re-renders.

---

## 5. Library as the Core Advantage

The library is already a strong foundation:
- Beam design/check/detailing functions in `structural_lib.api`.
- ETABS CSV import and envelope normalization.
- BBS, DXF, and report generation.
- 3D geometry helpers for rebar and stirrups.

### 5.1 Strong points (today)

- Mature IS 456 design pipeline.
- Detailing logic and serviceability checks.
- ETABS import support with normalized envelopes.
- 3D geometry and rebar placement utilities.
- Audit and calculation report structures.

### 5.2 Weak points (today)

- No incremental edit + revalidation API.
- No beam-line detection or standardization.
- No explicit constructability scoring.
- Limited professional examples and guide-level docs.

### 5.3 What to add (beams-only completeness)

Minimum new API layer for premium workflow:
- modify_beam_reinforcement
- validate_beam_design
- compare_beam_designs
- compute_beam_cost
- detect_beam_lines
- analyze_beam_line
- optimize_beam_line
- score_constructability
- suggest_standardization
- check_bar_congestion
- compute_bar_cut_lengths
- generate_cross_section_data
- export_visualization (png/svg)

---

## 6. Automation for Normal Engineers (Feasibility)

Yes, this is possible and proven by adoption of:
- Dynamo (Revit) visual programming for architects/engineers.
- Grasshopper (Rhino) parametric workflows for design teams.

### 6.1 What makes it usable for non-coders

- Playbooks: pre-configured firm workflows.
- Recipes: sequences of actions with parameters.
- Exception budgets: limits on deviations.
- Pattern library: approved beam patterns.

### 6.2 Design rule

Automation must call the same command API the UI and AI use. This guarantees:
- Consistent outputs.
- Auditable changes.
- A single source of truth.

---

## 7. Execution Reality: VS Code + AI Agents

We assume code will be written by AI agents in VS Code. That is an advantage if we enforce:

- Strict API contracts and tests.
- Deterministic outputs for given inputs.
- Linting and formatting gates.
- Review gates for API and workflow changes.

---

## 8. Reuse Map (What We Can Leverage Now)

### 8.1 From the library

- Existing beam design and detailing functions.
- ETABS CSV import and normalization.
- BBS, DXF, and report exports.

### 8.2 From Streamlit

- Plotly cross-section and BMD/SFD logic.
- Three.js HTML renderer and geometry format.

These can be migrated into a React UI without redoing math or geometry.

---

## 9. Research Agenda (Beams-Only)

### 9.1 Engineering workflow research

- How consultants define typical floors.
- How revisions are approved and re-issued.
- What deliverable formats are accepted by clients.

### 9.2 Visual quality research

- Best patterns for picking and isolating beams.
- Labeling without clutter (LOD for labels).
- Ghosted concrete with highlighted rebar.

### 9.3 Automation research

- What firm rules are standard (bar sets, patterns, max layers).
- How firms share templates internally.

---

## 10. Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Premium UI takes longer than expected | High | Build a shell spike first with mock data |
| Performance issues in 3D | High | Use instancing, LOD, delta updates |
| Trust issues with ETABS mapping | High | Produce Mapping Report + audit trail |
| AI edits create invalid designs | Medium | Auto-validate after every command |

---

## 11. Implementation Plan (Beams-Only, Research-Driven)

### Phase 1: API Layer + Premium Shell (Week 1-2)

**FastAPI Backend:**
- Create FastAPI wrapper for all `structural_lib` functions
- Export 3D geometry, design, detailing, optimization endpoints
- Set up OpenAPI documentation for React integration
- Write integration tests for API parity

**React Shell:**
- Set up Next.js + React Three Fiber + Dockview
- Build command palette with `cmdk` library
- Implement AG Grid with mock data
- Create basic 3D viewport with beam rendering

### Phase 2: Library P0 APIs + Core UI (Week 2-3)

**Library Functions:**
- Add P0 APIs: modify_beam_reinforcement, validate_beam_design, compare_beam_designs, compute_beam_cost
- Add real-time validation endpoint (< 100ms response)

**UI Components:**
- Beam editor panel with live preview
- Compliance status indicators (green/yellow/red)
- Keyboard shortcuts and command palette integration

### Phase 3: AI Integration + Collaboration (Week 3-4)

**AI Features:**
- Port AI tool definitions to React frontend
- Implement tool handlers calling FastAPI backend
- Add confidence-based execution (auto-execute vs approval)
- Build proactive AI observer with state hooks

**Collaborative UX:**
- Real-time co-editing with visual indicators
- AI suggestion overlays in 3D viewport
- Inspector panel for suggestion details

### Phase 4: Multi-Beam Intelligence (Week 4-5)

**Library Functions:**
- Add P1 APIs: detect_beam_lines, analyze_beam_line, optimize_beam_line
- Add constructability scoring functions

**UI Components:**
- Beam line visualization and selection
- Multi-beam optimization table
- Standardization recommendations

### Phase 5: Automation + Polish (Week 5-6)

**Automation:**
- Playbooks and recipes system
- Template library for firm standards
- Batch operation progress UI

**Polish:**
- Revision diff and export pack
- Performance optimization (1000+ beams)
- Ghosting, isolation, and heatmap layers
- Documentation and examples

### Milestone Summary

| Phase | Duration | Key Deliverables |
| --- | --- | --- |
| 1 | Week 1-2 | FastAPI backend, React shell, basic 3D |
| 2 | Week 2-3 | P0 library APIs, beam editor, shortcuts |
| 3 | Week 3-4 | AI tools, collaborative UX, overlays |
| 4 | Week 4-5 | Multi-beam intelligence, beam lines |
| 5 | Week 5-6 | Automation, polish, documentation |

---

## 12. LLM Agent Integration Architecture

The AI agent must integrate seamlessly with the command/event model. This section defines how AI actions flow through the same pipeline as user actions.

### 12.1 Command Pipeline Design

All actions (user, AI, or automation) go through a unified command pipeline:

```python
class Command:
    action: str              # "EditRebar", "OptimizeBeam", etc.
    arguments: dict          # Parameters for the action
    reasoning: str           # Why this command (AI explains its thinking)
    confidence: float        # 0-1 confidence score
    side_effects: list       # What else might change
    rollback_fn: Callable    # How to undo this command
    estimated_impact: dict   # Cost/steel/utilization deltas
```

Benefits of unified pipeline:
- Undo/redo works for AI actions
- Audit trail captures AI reasoning
- Batch execution for multiple beams
- Collaborative approval before execution

### 12.2 Confidence-Based Execution

Structural engineering calculations are deterministic. Use IS 456 compliance as the confidence source:

| Confidence Level | Threshold | Behavior |
| --- | --- | --- |
| High | > 0.95 | Auto-execute (routine changes) |
| Medium | 0.7 - 0.95 | Show as "Review Suggested Change" |
| Low | < 0.7 | Interactive clarification dialog |

Confidence calculation:
- IS 456 clause compliance: +0.3 if all clauses pass
- Design margin: +0.2 if utilization < 0.85
- Similar to previous designs: +0.2 if pattern matches project history
- Cost reduction: +0.1 if savings > 5%
- Constructability: +0.2 if bar congestion score is low

### 12.3 AI Showing Its Work

Every AI command includes supporting calculations and citations:

```json
{
    "command_id": "opt_B1_Ground",
    "action": "optimize_beam",
    "result": {
        "status": "success",
        "previous_ast": 2000,
        "new_ast": 1850,
        "reasoning": [
            "Original utilization: 0.78 (IS 456 Cl 26.5.2.1)",
            "Optimization maintains > 0.75 margin",
            "Bar size reduced 25mm to 20mm (same count)",
            "Cost savings: Rs 1,200 (8%)"
        ],
        "citations": ["IS:456-2000 Cl 26.5.2.1", "Cl 26.2", "Table 19"]
    }
}
```

Visual annotations in 3D:
- Callouts showing key values (Ast, utilization, cost)
- Highlight regions referenced in reasoning
- Link to detailed calculation report

---

## 13. Collaborative Human + AI Workspace

The workspace must support real-time collaboration between engineer and AI.

### 13.1 Real-Time Co-Editing Pattern

When engineer edits reinforcement:
1. AI computes IS 456 compliance in real-time (< 100ms)
2. Visual indicators update immediately:
   - Green checkmark: design is safe
   - Yellow triangle: warning (marginal compliance)
   - Red X: failure (code violation)
3. AI proactively suggests: "Stirrup spacing violates Cl 26.5.3.2"

Implementation:
```typescript
// React hook for real-time compliance
function useComplianceCheck(beamId: string, rebarConfig: RebarConfig) {
    const [status, setStatus] = useState<ComplianceStatus>('checking');

    useEffect(() => {
        const check = debounce(async () => {
            const result = await api.validateBeam(beamId, rebarConfig);
            setStatus(result.isCompliant ? 'safe' : 'violation');
        }, 100);
        check();
    }, [rebarConfig]);

    return status;
}
```

### 13.2 Proactive AI Observer

AI monitors workspace state and surfaces opportunities:

```python
class AIObserver:
    """Watches workspace state for actionable insights."""

    def on_beam_modified(self, beam_id, changes):
        # Check if modification created issues
        issues = check_is456_compliance(beam_id)
        if issues:
            suggest(f"Beam {beam_id} now has {len(issues)} issues")

    def on_floor_load_updated(self, floor_id):
        # Check if optimization is now possible
        opportunity = check_optimization_potential(floor_id)
        if opportunity.savings_pct > 5:
            suggest(f"Floor {floor_id}: {opportunity.savings_pct}% cost reduction available")

    def on_beam_line_detected(self, beam_ids):
        # Offer multi-beam optimization
        suggest(f"Beam line detected: consider standardization for {beam_ids}")
```

Trigger points:
- Beam forces updated (ETABS re-import)
- Reinforcement manually edited
- Optimization completed (check neighbors)
- Beam line selected (offer standardization)

### 13.3 Unified Canvas + Overlays (Not Split-Screen)

Split-screen is cognitively expensive. Use unified canvas with AI overlays:

```
+---------------------------------------------------------------+
| 3D VIEWPORT (main canvas)                                      |
| [Beam rendering with AI-added callouts]                       |
| - Green highlight: "Optimal design per optimization run 3"    |
| - Red circle: "Stirrup spacing violation at Cl 26.5.3.2"      |
| - Blue info icon: "Consider merging with beam line B1-B3"     |
+---------------------------------------------------------------+
| INSPECTOR PANEL (right, dockable)                             |
| [Details on selected suggestion - calculations, apply button] |
+---------------------------------------------------------------+
```

Key patterns:
- AI suggestions appear as non-blocking overlays
- Click overlay to expand details in inspector
- Apply/Reject buttons in inspector (not cluttering 3D)
- Overlays fade after 10 seconds if not interacted with

---

## 14. AI Visualization Control

AI should control 3D view to direct engineer attention effectively.

### 14.1 Camera Control (Auto-Framing)

AI-triggered camera movements:
- "Focus on critical beams" → auto-frame highest utilization beams
- "Show beam line" → align camera perpendicular to beam line
- "Compare designs" → split viewport with synchronized cameras

```typescript
// AI command handler for camera control
function handleAICommand(cmd: AICommand) {
    if (cmd.type === 'focus_beams') {
        const bounds = computeBounds(cmd.beamIds);
        camera.fitToBounds(bounds, { padding: 1.2 });
        camera.animate({ duration: 500 });
    }
    if (cmd.type === 'show_beam_line') {
        const line = getBeamLine(cmd.lineId);
        camera.alignTo(line.direction, { up: 'Y' });
    }
}
```

### 14.2 Highlighting and Filtering

Visual feedback for AI insights:

| Insight Type | Visual Effect |
| --- | --- |
| Problem beam | Red glow outline + pulsing |
| Optimized beam | Green highlight |
| Selected beam line | Same-color family, connected |
| Related beams | 50% opacity |
| Unrelated beams | 20% ghosted |

Filtering commands:
- "Show only beams with shear failure risk"
- "Highlight beams over 90% utilization"
- "Isolate floor 3 beam lines"

### 14.3 AI-Generated Overlays

Switchable visualization layers:

**Utilization Heatmap:**
```
0-50%   → Green (#10B981)  - Underutilized
50-85%  → Yellow (#F59E0B) - Optimal range
85-100% → Orange (#EF6632) - Highly utilized
>100%   → Red (#EF4444)    - Overstressed
```

**Other overlay types:**
- Cost distribution per beam (heat map)
- Constructability score zones
- Development/lap length visualization
- Before/after comparison (split with diff highlights)

**Comparison layer for optimization:**
```typescript
// Before/after overlay
function OptimizationComparison({ beamId, before, after }) {
    return (
        <SplitView>
            <BeamMesh config={before} opacity={0.5} color="yellow" />
            <BeamMesh config={after} opacity={1.0} color="green" />
            <DiffAnnotations changes={computeDiff(before, after)} />
        </SplitView>
    );
}
```

---

## 15. Premium UI Implementation Details

Specific implementation patterns for IDE-like experience.

### 15.1 Command Palette (Cmd+Shift+P)

Use `cmdk` or `kbar` library for React command palette:

```typescript
const commands = [
    // Design
    { id: 'open-editor', name: 'Open Beam Editor', category: 'Design',
      shortcut: 'E', action: () => openBeamEditor() },
    { id: 'validate', name: 'Validate Design Against Code', category: 'Design',
      action: () => validateSelectedBeam() },

    // Optimization
    { id: 'optimize-beam', name: 'Optimize Selected Beam', category: 'Optimization',
      shortcut: 'O', action: () => optimizeBeam() },
    { id: 'optimize-line', name: 'Optimize Beam Line', category: 'Optimization',
      action: () => optimizeBeamLine() },

    // Visualization
    { id: 'toggle-3d', name: 'Toggle 3D View', category: 'Visualization',
      shortcut: '3', action: () => togglePanel('3d') },
    { id: 'show-heatmap', name: 'Show Utilization Heatmap', category: 'Visualization',
      action: () => enableLayer('utilization') },

    // Export
    { id: 'export-bbs', name: 'Export BBS', category: 'Export',
      action: () => exportBBS() },
    { id: 'export-dxf', name: 'Export DXF', category: 'Export',
      action: () => exportDXF() },
];
```

Context-aware filtering:
- If beam selected: show beam-specific commands first
- If beam line selected: show line optimization commands
- If nothing selected: show global commands

### 15.2 Keyboard Shortcuts

Essential shortcuts:

| Shortcut | Action |
| --- | --- |
| Cmd+O | Open design file |
| Cmd+S | Save design state |
| Cmd+Z | Undo last change |
| Cmd+Shift+Z | Redo |
| Cmd+Shift+P | Command palette |
| E | Open beam editor |
| O | Optimize selected |
| Space | Toggle orbit mode |
| H | Hide selected |
| V | Show all (reset visibility) |
| 1/2/3 | Switch to floor 1/2/3 |
| Esc | Deselect / close panel |

Implementation:
- Show keyboard hints on hover (VS Code style)
- Support customizable shortcut profiles
- Display shortcut in command palette results

### 15.3 Status Badges and Utilization Coloring

AG Grid cell renderers for engineering data:

```typescript
const columnDefs = [
    { field: 'beamId', headerName: 'Beam ID', pinned: 'left' },
    {
        field: 'utilizationRatio',
        headerName: 'Utilization',
        cellStyle: (params) => ({
            backgroundColor: getUtilizationColor(params.value),
            color: params.value > 0.85 ? 'white' : 'black'
        }),
        valueFormatter: (params) => `${(params.value * 100).toFixed(1)}%`
    },
    {
        field: 'status',
        headerName: 'Status',
        cellRenderer: StatusBadgeRenderer
        // Renders: ✓ Compliant | ⚠ Warning | ✗ Error | ⚡ Optimizable
    },
    {
        field: 'costSavings',
        headerName: 'Savings',
        cellStyle: { backgroundColor: '#D1FAE5' },
        valueFormatter: (params) => params.value ? `↓ ${params.value}%` : '—'
    }
];
```

### 15.4 Ghosting and Isolation

Three.js material settings for visual hierarchy:

```typescript
// Ghosting effect
function setBeamVisibility(beam: BeamMesh, mode: 'selected' | 'related' | 'ghost') {
    const opacity = { selected: 1.0, related: 0.5, ghost: 0.2 }[mode];
    beam.material.opacity = opacity;
    beam.material.transparent = true;
    beam.renderOrder = mode === 'selected' ? 10 : 0;
}

// Concrete vs rebar visibility
function createBeamMaterials() {
    return {
        concrete: new MeshStandardMaterial({
            color: 0xD1D5DB,  // Light gray
            opacity: 0.6,
            transparent: true
        }),
        mainBars: new MeshStandardMaterial({ color: 0x1E40AF }),   // Dark blue
        stirrups: new MeshStandardMaterial({ color: 0xDC2626 }),   // Red
        links: new MeshStandardMaterial({ color: 0x7C3AED })       // Purple
    };
}
```

---

## 16. Migration Roadmap - Detailed Reuse Map

Based on code analysis, here is what can be reused from the current Streamlit implementation.

### 16.1 Reusability by Component

| Component | Reusability | Source File | Action |
| --- | --- | --- | --- |
| 3D Geometry Generation | 95% | `structural_lib/visualization/geometry_3d.py` | Export as FastAPI endpoint |
| Design Algorithms | 100% | `structural_lib/api.py` | Use directly via FastAPI |
| Detailing Logic | 100% | `structural_lib/detailing.py` | Use directly via FastAPI |
| AI Tool Definitions | 100% | `streamlit_app/ai/tools.py` | Copy JSON schema to React |
| AI Handlers | 90% | `streamlit_app/ai/handlers.py` | Refactor to FastAPI endpoints |
| Insights Engine | 100% | `structural_lib/insights/` | Use directly via FastAPI |
| ETABS Adapters | 100% | `structural_lib/adapters.py` | Use directly via FastAPI |
| Three.js Code | 60% | `static/beam_viewer_3d.html` | Port geometry logic to R3F |
| Plotly Charts | 0% | `components/visualizations.py` | Rewrite with Recharts/Visx |
| Streamlit UI | 0% | `streamlit_app/components/` | Rewrite in React |

### 16.2 Migration Phases

**Phase 1: API Layer (Week 1-2)**
- Create FastAPI wrapper for all `structural_lib` functions
- Export 3D geometry generation as JSON endpoint
- Set up OpenAPI documentation for React integration
- Write integration tests for API parity

**Phase 2: React Shell (Week 2-3)**
- Set up Next.js + React Three Fiber + Dockview
- Build command palette with `cmdk`
- Implement AG Grid with mock data
- Create 3D viewport with basic beam rendering

**Phase 3: AI Integration (Week 3-4)**
- Port AI tool definitions to React
- Implement tool handlers calling FastAPI
- Add real-time compliance checking
- Build proactive AI observer

**Phase 4: Polish and Testing (Week 4)**
- Parity testing (same inputs → same outputs)
- Performance benchmarking (1000+ beams)
- UI polish and keyboard shortcuts
- Documentation and examples

### 16.3 API Design for React Frontend

```python
# FastAPI routes for React frontend
from fastapi import FastAPI
from structural_lib import api

app = FastAPI()

@app.post("/api/design-beam")
def design_beam(params: BeamDesignRequest):
    result = api.design_beam_is456(**params.dict())
    return result.to_dict()

@app.post("/api/detail-beam")
def detail_beam(params: BeamDetailingRequest):
    result = api.detail_beam_is456(**params.dict())
    return result.to_dict()

@app.post("/api/optimize-beam")
def optimize_beam(params: BeamOptimizationRequest):
    result = api.optimize_beam_cost(**params.dict())
    return result.to_dict()

@app.post("/api/beam-3d-geometry")
def beam_3d_geometry(params: Beam3DRequest):
    result = api.beam_to_3d_geometry(**params.dict())
    return result  # Already JSON-serializable

@app.post("/api/validate-beam")
def validate_beam(params: BeamValidationRequest):
    result = api.check_beam_is456(**params.dict())
    return {"isCompliant": result.is_safe, "issues": result.issues}
```

---

## References

### Core Technology
- React Three Fiber documentation: https://docs.pmnd.rs/react-three-fiber/getting-started/introduction
- Three.js InstancedMesh: https://threejs.org/docs/#api/en/objects/InstancedMesh
- Three.js WebGPURenderer: https://threejs.org/docs/#api/en/renderers/WebGPURenderer
- Dockview docking layout: https://dockview.dev/
- AG Grid JavaScript data grid: https://www.ag-grid.com/javascript-data-grid/
- cmdk command palette: https://cmdk.paco.me/
- kbar command palette: https://kbar.vercel.app/

### Engineering Software Patterns
- ETABS vs STAAD.Pro comparison: https://caddcentre.com/blog/etabs-vs-staadpro-a-beginners-guide-to-structural-design-software/
- Revit user interface tour: https://www.autodesk.com/learn/ondemand/tutorial/revit-user-interface-tour
- CAD Software UX Design Patterns: https://medium.com/@creativenavy/cad-software-ui-design-patterns-benchmarking-97cc7834ad02
- Onshape isolation and transparency: https://www.onshape.com/en/resource-center/tech-tips/cad-assembly-visibility-isolate-transparency

### AI Collaboration Patterns
- Cursor IDE (AI code editor): https://cursor.com/
- GitHub Copilot Workspace: https://github.blog/news-insights/product-news/github-copilot-workspace/
- Command Palette UX Patterns: https://medium.com/design-bootcamp/command-palette-ux-patterns-1-d6b6e68f30c1
- How to build a remarkable command palette: https://blog.superhuman.com/how-to-build-a-remarkable-command-palette/

### Automation and Workflows
- Dynamo (visual programming for BIM): https://dynamobim.org/
- Grasshopper (parametric workflows): https://www.rhino3d.com/6/new/grasshopper/
- FastAPI documentation: https://fastapi.tiangolo.com/

### Visualization
- Color in data visualizations: https://www.sigmacomputing.com/blog/7-best-practices-for-using-color-in-data-visualizations/
- Status indicators design patterns: https://carbondesignsystem.com/patterns/status-indicator-pattern/
- Utilization ratios in structural engineering: https://oneracksolutions.com/utilization-ratios/
