# Project BHEEM: Open-Source Structural Design Software Masterplan

**Type:** Architecture
**Audience:** All Agents, Developers, Users
**Status:** Draft
**Importance:** Critical
**Created:** 2026-04-11
**Last Updated:** 2026-04-11

> **Current planning boundary (2026-08-29):** This document is a directional
> product vision and contains historical capability claims, estimates, and
> implementation proposals. It is not current execution authority or
> acceptance evidence. Use
> [ETABS Data, Beam Analysis, and Optimization Foundation](etabs-data-analysis-optimization-foundation-plan.md)
> for the dependency-ordered W2/W3 data, bounded beam-line surrogate, and
> ETABS-verified optimization plan. Use the companion
> [ETABS, Excel, Professional Attestation, and Surface Retirement Audit](etabs-excel-professional-surface-audit.md)
> for Excel review, professional evidence, API retirement, React freeze, and
> compaction decisions. Use
> [Excel + ETABS Beam Workflow — Next-Phase Plan](excel-etabs-beam-next-phase-plan.md)
> for the integrated W2 evidence and W3 execution boundary.

> **BHEEM** — **B**uilding **H**olistic **E**ngineering **E**nvironment with **M**achine-intelligence
> An open-source, AI-native structural design platform that aims to surpass ETABS in usability, transparency, and accessibility.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Why This Is Possible Now](#2-why-this-is-possible-now)
3. [Competitive Analysis: ETABS vs What We're Building](#3-competitive-analysis)
4. [Our Unfair Advantages](#4-our-unfair-advantages)
5. [Architecture Vision](#5-architecture-vision)
6. [Phase Roadmap](#6-phase-roadmap)
7. [AI-Native Development Methodology](#7-ai-native-development-methodology)
8. [Technical Deep Dives](#8-technical-deep-dives)
9. [Hard Technical Problems & Solutions](#9-hard-technical-problems--solutions)
10. [What the Library Still Needs — Algorithms, ML & Optimization](#10-what-the-library-still-needs)
11. [Risk Analysis & Mitigation](#11-risk-analysis--mitigation)
12. [Success Metrics](#12-success-metrics)
13. [Resource & Funding Strategy](#13-resource--funding-strategy)
14. [The Knightly Run — Full ETABS Import & Overnight Optimization](#14-the-knightly-run)
15. [Appendix: Current State Assessment](#appendix-current-state-assessment)

---

## 1. Executive Summary

We're building an open-source structural design platform that does what ETABS does — but better, cheaper, and smarter. ETABS costs $5,000–$15,000/year per seat. It's a 45-year-old desktop application. We're building a web-native, AI-assisted, code-transparent alternative that:

- **Costs $0** for basic use (open-source core)
- **Runs in a browser** — no installation, no hardware requirements
- **Has AI copilot** — engineers describe what they want in natural language
- **Shows its work** — every calculation traces back to the code clause (IS 456, ACI 318, EC2)
- **Is built by AI** — planned, coded, tested, and maintained by AI agents with human oversight

### What We Already Have (Foundation — ~18 months of work)

| Capability | Status | Quality |
|------------|--------|---------|
| IS 456 Beam Design (full) | ✅ Production | 99% branch coverage, 5,003 tests |
| IS 456 Column Design (full) | ✅ Production | 14 endpoints, P-M curves |
| IS 456 Footing Design | ✅ Production | Bearing, shear, flexure |
| 3D Visualization (WebGL/R3F) | ✅ Production | Real-time rebar rendering |
| FastAPI Backend (60 endpoints) | ✅ Production | REST + WebSocket |
| React 19 Frontend | ✅ Production | 7 pages, Zustand state |
| CSV Import from ETABS | ✅ Production | 40+ column mappings |
| BBS/DXF/Report Export | ✅ Production | Industry-standard outputs |
| AI Agent Infrastructure | ✅ Production | 16 agents, 14 skills |

### What We're Building Toward

A platform where a structural engineer can:
1. **Model** a building in a browser (or import from Revit/ETABS)
2. **Analyze** it with FEM (linear + nonlinear)
3. **Design** all elements (beams, columns, slabs, walls, footings, stairs) per multiple codes
4. **Detail** with auto-generated rebar schedules and drawings
5. **Optimize** with AI that suggests better sections, layouts, and reinforcement
6. **Collaborate** with team members in real-time
7. **Export** to BIM tools, procurement systems, and construction teams

---

## 2. Why This Is Possible Now

### 2.1 Technology Convergence (2024–2026)

| Technology | Impact |
|-----------|--------|
| **LLM Code Generation** | AI can write 80% of boilerplate structural code from IS 456 text |
| **WebGPU/WebGL2** | Browser 3D rendering now rivals desktop OpenGL |
| **React Three Fiber** | Three.js + React = declarative 3D scenes |
| **Python Scientific Stack** | NumPy/SciPy = C-speed matrix solvers in Python |
| **WebAssembly** | Run FEM solvers at near-native speed in browsers |
| **Cloud GPUs** | Offload heavy analysis to scalable cloud infrastructure |
| **AI Agents** | Self-maintaining codebases with 16+ specialized agents |

### 2.2 Market Gap

- **ETABS**: $5K–$15K/year, Windows-only, closed-source, 45-year-old architecture
- **STAAD.Pro**: $4K–$8K/year, similar constraints
- **Robot Structural**: Part of Autodesk suite ($3K+/year)
- **OpenSees**: Powerful but research-focused, no GUI, no design code integration
- **PyNite**: FEM library only, no design codes, no UI
- **No one** offers: open-source + web-native + AI-assisted + multi-code design

### 2.3 The ETABS Pain Points We Solve

| ETABS Pain | Our Solution |
|-----------|-------------|
| $15K/year license | Free open-source core |
| Windows-only desktop app | Browser-based, any device |
| Black-box calculations | Every result traces to code clause |
| No AI assistance | AI copilot for design suggestions |
| Manual model building | AI generates models from floor plans |
| Static reporting | Interactive, real-time dashboards |
| No version control | Git-native project management |
| Slow iteration cycle | Live design updates in <500ms |
| Hard to learn (6-12 months) | AI-guided onboarding, natural language |
| Vendor lock-in | Open formats, open API, extensible |

---

## 3. Competitive Analysis

### 3.1 Feature Matrix: ETABS vs BHEEM (Target State)

| Feature Category | ETABS v23 | BHEEM v1.0 (Target) | BHEEM v2.0 (Vision) |
|-----------------|-----------|---------------------|---------------------|
| **Modeling** | | | |
| Grid/story-based modeling | ✅ Full | 🟡 v0.8 | ✅ Full |
| Physical ↔ Analytical model | ✅ Full | 🟡 Analytical only | ✅ Both |
| DXF/DWG import as template | ✅ Full | 🟡 DXF export only | ✅ Import + Export |
| Section Designer | ✅ Full | ✅ Cross-section view | ✅ Full designer |
| Mesh generation | ✅ Advanced | ❌ Not yet | ✅ Auto-mesh |
| **Loading** | | | |
| Auto seismic (IS 1893) | ✅ Multi-code | ❌ Not yet | ✅ IS 1893 + ASCE 7 |
| Auto wind (IS 875) | ✅ Multi-code | ❌ Not yet | ✅ IS 875 + ASCE 7 |
| Load combinations (auto) | ✅ Full | 🟡 Manual UDL/point | ✅ Auto per code |
| Temperature loads | ✅ Full | ❌ | 🟡 Basic |
| **Analysis** | | | |
| Linear static | ✅ Full | ❌ FEM needed | ✅ Full |
| P-Delta | ✅ Full | ❌ | ✅ Full |
| Modal analysis | ✅ Eigen + Ritz | ❌ | ✅ Eigen |
| Response spectrum | ✅ Full | ❌ | 🟡 Basic |
| Time history (linear) | ✅ Full | ❌ | 🟡 Basic |
| Nonlinear static (pushover) | ✅ Advanced | ❌ | 🟡 Basic |
| Nonlinear time history | ✅ Advanced | ❌ | ❌ v3.0+ |
| Staged construction | ✅ Full | ❌ | ❌ v3.0+ |
| Buckling | ✅ Full | ❌ | 🟡 Linear |
| **Design** | | | |
| Concrete beam design | ✅ Multi-code | ✅ IS 456 (full) | ✅ IS 456 + ACI + EC2 |
| Concrete column design | ✅ Multi-code | ✅ IS 456 (full) | ✅ IS 456 + ACI + EC2 |
| Concrete slab design | ✅ Multi-code | 🟡 40% done | ✅ Multi-code |
| Shear wall design | ✅ Multi-code | ❌ Planned | ✅ IS 456 + ACI |
| Steel frame design | ✅ Multi-code | ❌ | 🟡 IS 800 |
| Composite design | ✅ Full | ❌ | ❌ v3.0+ |
| Footing design | 🟡 (via SAFE) | ✅ IS 456 | ✅ Multi-code |
| **AI / Intelligence** | | | |
| AI design assistant | ❌ None | ✅ SmartDesigner | ✅ Full copilot |
| Design optimization | ❌ Manual | ✅ Cost optimizer | ✅ Multi-objective |
| Natural language interface | ❌ None | 🟡 Planned | ✅ Full chat UI |
| Auto-suggestions | ❌ None | ✅ Rebar suggestions | ✅ Full assistance |
| Error explanation | ❌ Cryptic errors | ✅ Plain English | ✅ With fix suggestions |
| **Output** | | | |
| 3D visualization | ✅ DirectX | ✅ WebGL/R3F | ✅ WebGPU |
| Report generation | ✅ Word/Excel | ✅ PDF/BBS/DXF | ✅ Full suite |
| BIM export (IFC) | ✅ Full | ❌ | ✅ IFC 4 |
| Revit integration | ✅ Bi-directional | ❌ | 🟡 One-way |
| **Platform** | | | |
| Web-based | ❌ Desktop only | ✅ Browser-native | ✅ PWA + desktop |
| Real-time collaboration | ❌ | ❌ | ✅ Multiplayer |
| Open-source | ❌ Proprietary | ✅ MIT License | ✅ |
| API for automation | ✅ COM/VBA/.NET | ✅ REST + WebSocket | ✅ Full SDK |
| Cost | $5K–$15K/year | $0 (core) | $0 core + paid cloud |

### 3.2 Where ETABS Will Always Win (For Now)

- **45 years of validation** — ETABS was used for the Burj Khalifa
- **Regulatory acceptance** — many firms require "approved" software
- **Advanced nonlinear** — FNA, fiber models, staged construction
- **BIM ecosystem** — deep Revit/Tekla integration
- **Enterprise support** — 24/7 phone support, training programs

### 3.3 Where We Win From Day One

- **Price**: Free vs $15K/year
- **Transparency**: Every calculation visible and verifiable
- **AI Integration**: No structural software has AI copilot
- **Accessibility**: Browser = works on any device, any OS
- **Developer Experience**: REST API, open formats, extensible
- **Learning Curve**: AI-guided vs 6-month ETABS learning curve
- **Indian Market**: IS 456 first-class support (ETABS treats it as secondary)

---

## 4. Our Unfair Advantages

### 4.1 AI-Native Development

We don't just use AI — we ARE an AI-built product:

- **16 specialized AI agents** already work on this codebase
- **14 skills** automate common engineering tasks
- **Session continuity** — AI remembers context across sessions
- **Self-evolving** — agents score themselves and improve instructions
- **Cost**: ~$2–5/session vs $200+/hour for human developers

This means we can:
- Ship features 10x faster than traditional development
- Maintain perfect code coverage (99% branch coverage, 5003 tests)
- Respond to user issues in hours, not weeks
- Add new design codes in weeks, not years

### 4.2 Code-Transparent Engineering

Every result includes:
```
Clause: IS 456:2000, Cl. 40.4(a)
Formula: Vc = τc × b × d
τc = 0.48 N/mm² (Table 19, for pt = 0.50%, M25)
Input: b=300mm, d=450mm, fck=25 N/mm², fy=500 N/mm²
Result: Vc = 0.48 × 300 × 450 = 64,800 N = 64.8 kN
```

No engineer has ever gotten this from ETABS.

### 4.3 Open Ecosystem

- **Python library**: `pip install structural-lib-is456`
- **REST API**: Any language, any platform
- **WebSocket**: Real-time streaming results
- **Plugin architecture**: Community can add codes, elements, materials
- **Educational**: Students learn real engineering, not button-clicking

---

## 5. Architecture Vision

### 5.1 System Architecture (Target State)

```
┌──────────────────────────────────────────────────────────────────┐
│                        BHEEM Platform                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   Web App     │  │  Desktop App │  │  Mobile App (PWA)    │   │
│  │  React 19     │  │  Tauri/Wails │  │  Responsive React    │   │
│  │  R3F + WebGPU │  │  + WebView   │  │  + Touch gestures    │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘   │
│         │                  │                      │               │
│  ┌──────▼──────────────────▼──────────────────────▼───────────┐  │
│  │                    API Gateway Layer                        │  │
│  │  FastAPI  ·  REST  ·  WebSocket  ·  GraphQL  ·  gRPC       │  │
│  │  Auth  ·  Rate Limiting  ·  Caching  ·  Load Balancing     │  │
│  └──────────────────────┬────────────────────────────────────┘  │
│                          │                                       │
│  ┌───────────────────────▼───────────────────────────────────┐  │
│  │                   Service Layer                            │  │
│  │                                                            │  │
│  │  ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌───────────────┐  │  │
│  │  │ Design  │ │ Analysis │ │ Loading │ │ AI / ML       │  │  │
│  │  │ Service │ │ Service  │ │ Service │ │ Service       │  │  │
│  │  │         │ │          │ │         │ │               │  │  │
│  │  │ Beam    │ │ FEM Core │ │ Seismic │ │ Copilot       │  │  │
│  │  │ Column  │ │ Solver   │ │ Wind    │ │ Optimizer     │  │  │
│  │  │ Slab    │ │ Mesher   │ │ Gravity │ │ Suggestions   │  │  │
│  │  │ Wall    │ │ P-Delta  │ │ Combos  │ │ Auto-design   │  │  │
│  │  │ Footing │ │ Modal    │ │ IS 1893 │ │ NL Interface  │  │  │
│  │  │ Stair   │ │ Dynamic  │ │ IS 875  │ │ Anomaly Det.  │  │  │
│  │  └─────────┘ └──────────┘ └─────────┘ └───────────────┘  │  │
│  │                                                            │  │
│  │  ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌───────────────┐  │  │
│  │  │ Export  │ │ Import   │ │  BIM    │ │ Collaboration │  │  │
│  │  │ Service │ │ Service  │ │ Service │ │ Service       │  │  │
│  │  │         │ │          │ │         │ │               │  │  │
│  │  │ BBS     │ │ CSV/ETAB │ │ IFC 4   │ │ WebSocket RT  │  │  │
│  │  │ DXF/DWG │ │ Revit    │ │ Revit   │ │ CRDT sync     │  │  │
│  │  │ PDF     │ │ SAP2000  │ │ Tekla   │ │ Comments      │  │  │
│  │  │ IFC     │ │ STAAD    │ │ speckle │ │ Versioning    │  │  │
│  │  └─────────┘ └──────────┘ └─────────┘ └───────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   Code Layer (Pure Math)                   │  │
│  │                                                            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │  │
│  │  │ IS 456   │  │ ACI 318  │  │   EC2    │  │ IS 800   │  │  │
│  │  │ :2000    │  │ -19      │  │ EN 1992  │  │ :2007    │  │  │
│  │  │          │  │          │  │          │  │          │  │  │
│  │  │ Beam     │  │ Beam     │  │ Beam     │  │ Beam     │  │  │
│  │  │ Column   │  │ Column   │  │ Column   │  │ Column   │  │  │
│  │  │ Slab     │  │ Slab     │  │ Slab     │  │ Tension  │  │  │
│  │  │ Wall     │  │ Wall     │  │ Wall     │  │ Compress │  │  │
│  │  │ Footing  │  │ Footing  │  │ Footing  │  │ Connect. │  │  │
│  │  │ Stair    │  │ Stair    │  │          │  │          │  │  │
│  │  │ Ductile  │  │          │  │          │  │          │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │  │
│  │                                                            │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │  Core Types: Materials · Sections · Loads · Results  │  │  │
│  │  │  FEM Core: Elements · Assembly · Solver · Mesh       │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   Infrastructure Layer                     │  │
│  │  PostgreSQL · Redis · S3 · Docker · K8s · CI/CD · CDN     │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### 5.2 FEM Engine Architecture (The Missing Piece)

The single biggest gap between our current state and an ETABS competitor is a **Finite Element Analysis engine**. Here's the plan:

```
FEM Engine (Python + WASM)
├── Elements/
│   ├── Beam2D          # Euler-Bernoulli, 2-node, 6-DOF
│   ├── Beam3D          # Timoshenko, 2-node, 12-DOF
│   ├── Shell4          # MITC4 shell, 4-node, 24-DOF
│   ├── Shell3          # DKT triangle, 3-node, 18-DOF
│   ├── Solid8          # 8-node hexahedron, 24-DOF
│   └── Link            # Spring/damper, 2-node
├── Assembly/
│   ├── GlobalStiffness # Sparse matrix assembly (scipy.sparse)
│   ├── Constraints     # Rigid diaphragm, body constraints
│   └── BoundaryConditions # Fixed, pinned, spring supports
├── Solver/
│   ├── LinearStatic    # K·u = F (direct: SuperLU, iterative: CG)
│   ├── PDelta          # Geometric stiffness iteration
│   ├── Modal           # Eigenvalue: scipy.sparse.linalg.eigsh
│   ├── ResponseSpectrum # CQC/SRSS modal combination
│   └── Nonlinear       # Newton-Raphson with arc-length control
├── Mesh/
│   ├── AutoMesh        # Delaunay triangulation for slabs/walls
│   ├── BeamMesh        # Auto-subdivide beams at intersections
│   └── Refinement      # h-refinement, p-refinement
├── PostProcess/
│   ├── Forces          # Member forces, reactions
│   ├── Stresses        # Element stresses, principal stresses
│   ├── Displacements   # Nodal displacements, drift ratios
│   └── Contours        # Stress/displacement contour generation
└── Export/
    ├── ToDesign        # Feed analysis results → design modules
    └── ToVisualization # Feed results → 3D rendering
```

**Key Decision: Build vs Integrate**

| Option | Pros | Cons |
|--------|------|------|
| **Build from scratch** | Full control, optimized for our use case | 12-18 months for basic FEM |
| **Wrap PyNite** | Already works, 3D FEM, well-tested | Limited elements, no shell/solid |
| **Wrap OpenSeesPy** | Industry standard, nonlinear | Complex API, research-focused |
| **Use SciPy/NumPy core** | Lightweight, we control everything | Must build element library |
| **Hybrid: SciPy core + Rust WASM** | Python for dev, WASM for browser speed | Higher complexity |

**Recommended**: **SciPy/NumPy core with progressive enhancement**
- Phase 1: Frame analysis (beam/column elements) using direct stiffness method
- Phase 2: Shell elements for slabs/walls using MITC4 formulation
- Phase 3: Rust/WASM compilation for browser-side analysis
- Phase 4: OpenSeesPy integration for advanced nonlinear

### 5.3 Frontend Architecture (Building Modeler)

```
React App (Current: 7 pages → Target: Full Modeler)
├── Modeling Mode/
│   ├── GridEditor        # Define grids, stories (Cartesian/polar)
│   ├── FloorPlanEditor   # Draw beams, columns, walls on plan view
│   ├── SectionAssigner   # Assign properties via drag-and-drop
│   ├── LoadAssigner      # Visual load application
│   ├── ConstraintEditor  # Supports, diaphragms, releases
│   └── 3DModelViewer     # Real-time 3D assembly visualization
├── Analysis Mode/
│   ├── RunPanel          # Select analysis types, run
│   ├── ResultsViewer     # BMD, SFD, deformed shape, contours
│   ├── AnimationPlayer   # Mode shapes, time history animation
│   └── DriftCheck        # Story drift verification (IS 1893)
├── Design Mode/
│   ├── DesignRunner      # Run design per selected code
│   ├── ElementResults    # Beam/column/slab design results
│   ├── InteractionDiag   # P-M curves, D/C ratios
│   ├── RebarSchedule     # Auto-generated BBS
│   └── DetailingView     # 3D rebar visualization (existing)
├── AI Copilot/
│   ├── ChatPanel         # Natural language design interface
│   ├── SuggestionPanel   # AI recommendations overlay
│   ├── OptimizationView  # Multi-objective optimization dashboard
│   └── WhyPanel          # "Why did you choose this?" explanations
└── Output Mode/
    ├── ReportBuilder     # Customizable calculation reports
    ├── DrawingExporter   # DXF/DWG with auto-dimensioning
    ├── BIMExporter       # IFC 4 export
    └── BOQGenerator      # Quantities + cost estimation
```

---

## 6. Phase Roadmap (Library-First Strategy)

> **Key Strategic Decision (April 2026):** Build and validate the library FIRST in a
> dedicated repo. Get engineers using it. Stabilize the API. THEN build the app on top.
>
> ```
> Phase A: Library repo (pip installable, validated, engineer-tested)
>     ↓ stable, trusted API
> Phase B: App repo (FastAPI + React, consumes library via pip)
> ```
>
> This is how every successful engineering tool is built: NumPy → SciPy → Jupyter,
> OpenSees (lib) → GUIs built by others, PyNite (lib) → UIs on top.

### Two Repositories

| Repo | Purpose | Package Name |
|------|---------|-------------|
| **`structural-lib`** | Pure library — analysis + design + export | `structural-lib` on PyPI |
| **`bheem-app`** (later) | Full app — FastAPI + React + AI copilot | `bheem` on Docker Hub |

---

### Phase 0: Library Extraction & Cleanup (v1.0-alpha)
**Timeline: Now → 6 weeks**
**Status: STARTING**

| Milestone | Description | Status |
|-----------|-------------|--------|
| 0.1 | Create new `structural-lib` repo with `src/` layout | ❌ |
| 0.2 | Migrate `core/`, `codes/is456/`, `codes/is13920/` (pure math) | ❌ |
| 0.3 | Clean up 30+ backward-compat stubs — remove dead code | ❌ |
| 0.4 | Migrate 5,003 tests, verify all pass in new repo | ❌ |
| 0.5 | Complete IS 456 slab design (one-way + two-way) | 🟡 40% done |
| 0.6 | Migrate services/ (design orchestration only, no app logic) | ❌ |
| 0.7 | Clean pyproject.toml — minimal deps, optional extras | ❌ |
| 0.8 | Publish to TestPyPI, verify `pip install structural-lib` works | ❌ |

**Exit criteria**: `pip install structural-lib` → `from structural_lib import design_beam_is456` works.
All 5,000+ tests pass. Zero backward-compat stubs.

**Library structure (new repo):**
```
structural-lib/
├── src/structural_lib/
│   ├── core/                    # Types, materials, sections, validation
│   ├── codes/
│   │   ├── is456/               # IS 456 — beam, column, slab, footing
│   │   ├── is13920/             # IS 13920 — ductile detailing
│   │   ├── is1893/              # IS 1893 — seismic (Phase 1)
│   │   ├── is875/               # IS 875 — gravity/wind (Phase 1)
│   │   ├── aci318/              # ACI 318 (Phase 3)
│   │   └── ec2/                 # EC2 (Phase 3)
│   ├── analysis/                # FEM engine (Phase 1)
│   ├── loading/                 # Load computation (Phase 1)
│   ├── design/                  # Design orchestration (thin API)
│   ├── export/                  # BBS, DXF, reports
│   └── intelligence/            # Smart designer, optimizer
├── tests/                       # ALL tests (unit + integration + benchmarks)
├── benchmarks/                  # ETABS/hand-calc validation vectors
├── examples/                    # Jupyter notebooks, CLI scripts
├── docs/                        # Library docs only (mkdocs)
├── pyproject.toml
└── README.md
```

---

### Phase 1: FEM Engine + Loading Codes (v1.0)
**Timeline: Weeks 6–20 (~3.5 months)**
**The Core Differentiator**

| Milestone | Description | Priority |
|-----------|-------------|----------|
| 1.1 | **Direct Stiffness FEM** — 2D/3D frame element, sparse solver | P0 |
| 1.2 | **IS 875 Loading** — dead loads (Part 1), live loads (Part 2) | P0 |
| 1.3 | **IS 1893 Seismic** — equivalent static method, response spectrum | P0 |
| 1.4 | **Load Combinations** — auto-generate per IS 456 Table 18 | P0 |
| 1.5 | **Analysis → Design pipeline** — FEM results feed design modules | P0 |
| 1.6 | **P-Delta analysis** — geometric nonlinearity | P1 |
| 1.7 | **Modal analysis** — eigenvalue solver for natural periods | P1 |
| 1.8 | **IS 875 Part 3 Wind** — basic wind loading | P2 |
| 1.9 | **Drift checks** — auto IS 1893 story drift verification | P2 |

**Key Technical Decisions**:

1. **Sparse matrix solver**: SciPy's `scipy.sparse.linalg.spsolve` (SuperLU) for direct, `cg` for iterative
2. **Element formulation**: Euler-Bernoulli beam → Timoshenko for short beams
3. **Assembly**: CSR sparse format, DOF numbering with bandwidth optimization
4. **Rigid diaphragm**: Master-slave DOF condensation at floor levels
5. **Loading**: IS 875 Part 1-5 + IS 1893:2016 Part 1
6. **Optional deps**: `structural-lib[analysis]` installs scipy/numpy for FEM

**Deliverable**: An engineer can script a 5-story RC frame, analyze it, and design all members in 20 lines of Python.

```python
# Example: What an engineer writes after Phase 1
from structural_lib import Building, design_building
from structural_lib.loading import IS1893Seismic, IS875Gravity
from structural_lib.analysis import LinearStatic, ModalAnalysis

building = Building(
    grids_x=[0, 6000, 12000, 18000],    # mm
    grids_y=[0, 5000, 10000],
    stories=[3200] * 5,                   # 5 stories @ 3200mm
    columns="300x450",                    # default section
    beams="230x500",
)

# Auto-apply loads
building.add_loading(IS875Gravity(dead_floor=5.0, live=3.0))       # kN/m²
building.add_loading(IS1893Seismic(zone="III", soil="medium", R=5))

# Analyze + Design in one call
results = design_building(building, code="IS456", analysis=[LinearStatic, ModalAnalysis])

# Results for every member
for beam in results.beams:
    print(f"{beam.id}: Ast={beam.flexure.Ast_req:.0f} mm², Asv/sv={beam.shear.Asv_sv:.2f}")

results.export_report("output/building_report.pdf")
results.export_bbs("output/bbs.xlsx")
```

**Validation Plan (Critical for Engineer Trust)**:
- 10 hand-calculated portal frame benchmarks
- 5 ETABS-validated multi-story models
- 3 textbook examples (Varghese, Jain, Pillai & Menon)
- Published in benchmarks/ with step-by-step verification

---

### Phase 1.5: Engineer Validation & Feedback (v1.0 → v1.1)
**Timeline: Weeks 20–28 (~2 months)**
**This is where the library earns trust**

| Milestone | Description |
|-----------|-------------|
| 1.5.1 | **Publish to PyPI** — `pip install structural-lib` |
| 1.5.2 | **Create Jupyter example notebooks** — 10 real-world examples |
| 1.5.3 | **Share with 5-10 engineers** — structural consultants, professors |
| 1.5.4 | **Collect feedback** — API ergonomics, missing features, accuracy |
| 1.5.5 | **Run benchmarks against ETABS** — publish comparison report |
| 1.5.6 | **Fix API pain points** — based on real engineer feedback |
| 1.5.7 | **Write documentation** — API reference, tutorials, IS 456 clause map |
| 1.5.8 | **Submit to university** — offer for academic use/endorsement |

**Goal**: 10+ engineers have used it. Documented feedback. API is stable. Trust established.

---

### Phase 2: Shell Elements + Complete IS 456 (v1.5)
**Timeline: Months 7–12**

| Milestone | Description |
|-----------|-------------|
| 2.1 | **Shell element (MITC4)** — for slab and wall modeling |
| 2.2 | **Slab design from FEM** — FEM forces → IS 456 slab checks |
| 2.3 | **Shear wall design** — pier/spandrel extraction from shells |
| 2.4 | **Auto-meshing** — Delaunay triangulation with refinement |
| 2.5 | **Floor diaphragm** — rigid/semi-rigid/flexible |
| 2.6 | **Staircase design** — IS 456 Cl. 33 |
| 2.7 | **WASM compilation** — solver runs in browser via Pyodide/Rust |

**Deliverable**: Full building models with slabs and walls analyzed and designed.

---

### Phase 3: Multi-Code + Steel (v2.0)
**Timeline: Months 12–20**

| Milestone | Description |
|-----------|-------------|
| 3.1 | **CodeRegistry** — plug-and-play design code system |
| 3.2 | **ACI 318-19** — beam + column + slab |
| 3.3 | **Eurocode 2** — beam + column |
| 3.4 | **IS 800:2007** — steel frame design |
| 3.5 | **ASCE 7-22 / EN 1998** — seismic + wind |
| 3.6 | **Design envelope** — compare results across codes |

**Deliverable**: Same building designed per IS 456, ACI 318, EC2 side-by-side.

---

### Phase 4: App Layer — BHEEM (v1.0-app)
**Timeline: Months 15–24 (overlaps with Phase 3)**
**Built in SEPARATE repo, consumes the library**

| Milestone | Description |
|-----------|-------------|
| 4.1 | **FastAPI backend** — wraps library, adds auth/sessions/storage |
| 4.2 | **Building modeler UI** — grid/story editor, element placement |
| 4.3 | **Analysis visualization** — BMD/SFD, deformed shape, contours |
| 4.4 | **AI Copilot** — natural language → building model → design |
| 4.5 | **Real-time collaboration** — CRDT multiplayer editing |
| 4.6 | **IFC 4 import/export** — BIM interoperability |
| 4.7 | **Cloud analysis** — offload heavy FEM to cloud |

**Note**: Much of this already exists in the current monorepo (react_app, fastapi_app).
The app repo will reuse those components but consume the library via `pip install`.

---

### Phase 5: Advanced & Market Leadership (v2.0-app)
**Timeline: Month 24+**

| Milestone | Description |
|-----------|-------------|
| 5.1 | **Nonlinear analysis** — pushover, time history |
| 5.2 | **Performance-Based Design** — FEMA 356 |
| 5.3 | **AI generative design** — topology optimization |
| 5.4 | **Foundation suite** — pile caps, rafts, retaining walls |
| 5.5 | **Bridge design** — T-beam, box girder, prestressed |
| 5.6 | **Desktop app** — Tauri-based for offline |
| 5.7 | **Marketplace** — community plugins, templates |
| 5.8 | **Mobile inspector** — field verification with AR |

---

## 7. AI-Native Development Methodology

### 7.1 How We Build This (The Meta-Innovation)

This project is itself a demonstration of AI-driven software development:

```
┌─────────────────────────────────────────────────────┐
│              AI-Native Development Loop              │
│                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐       │
│  │  Human    │───▶│  AI Plan │───▶│  AI Code │       │
│  │  Intent   │    │  (Orch.) │    │ (Backend)│       │
│  └──────────┘    └──────────┘    └────┬─────┘       │
│                                       │              │
│  ┌──────────┐    ┌──────────┐    ┌────▼─────┐       │
│  │  Human    │◀───│ AI Review│◀───│ AI Test  │       │
│  │  Approve  │    │(Reviewer)│    │ (Tester) │       │
│  └──────────┘    └──────────┘    └──────────┘       │
│                                                      │
│  Cycle time: 2-4 hours per feature                   │
│  Human involvement: ~20 minutes per feature          │
└─────────────────────────────────────────────────────┘
```

### 7.2 Agent Roles in Development

| Phase | Human Role | AI Agent Roles |
|-------|-----------|---------------|
| **Planning** | Define feature intent, approve scope | `orchestrator` breaks into tasks |
| **Research** | Verify IS 456 clauses | `structural-engineer` + `library-expert` research codes |
| **Architecture** | Approve design decisions | `orchestrator` + `reviewer` propose architecture |
| **Implementation** | Spot-check critical code | `structural-math` (pure math), `backend` (services), `api-developer` (endpoints), `frontend` (UI) |
| **Testing** | Review test coverage | `tester` writes tests, `structural-engineer` validates results |
| **Review** | Final approval | `reviewer` + `security` automated review |
| **Documentation** | Review user-facing docs | `doc-master` auto-generates docs from code |
| **Deployment** | Approve release | `ops` handles CI/CD, Docker, PyPI |

### 7.3 Development Velocity Projection

| Phase | Features/Month (Manual) | Features/Month (AI-Native) | Speedup |
|-------|------------------------|---------------------------|---------|
| Phase 0 | 2-3 | 8-12 | 4x |
| Phase 1 (FEM) | 1-2 | 4-6 | 4x |
| Phase 2 (Shell) | 1 | 3-4 | 3-4x |
| Phase 3 (Multi-code) | 1-2 | 5-8 | 4-5x |

### 7.4 Quality Assurance Strategy

```
Every Feature Goes Through:

1. AI writes implementation          (structural-math / backend)
2. AI writes tests                   (tester — 85%+ branch coverage)
3. AI runs IS 456 verification       (structural-engineer — golden vectors)
4. AI runs architecture check        (reviewer — 4-layer boundary validation)
5. AI runs security scan             (security — OWASP Top 10)
6. Human reviews critical math       (engineer — spot-check formulas)
7. AI generates documentation        (doc-master — API refs, tutorials)
8. AI runs regression suite          (tester — 5000+ existing tests MUST pass)
9. AI validates packaging            (ops — wheel, imports, version)
```

### 7.5 Cost Model

| Resource | Monthly Cost | Notes |
|----------|-------------|-------|
| AI API (Claude/GPT) | $200–500 | ~100 agent sessions/month |
| Cloud hosting (dev) | $50–100 | Small VPS for CI/CD |
| Cloud hosting (prod) | $0 (initially) | Static site + API on demand |
| Human time | 20–40 hrs/month | Architecture decisions, reviews, marketing |
| **Total** | **$250–600/month** | vs $50K+/month for a traditional 5-person team |

---

## 8. Technical Deep Dives

### 8.1 FEM Solver: Direct Stiffness Method

The core of any structural analysis software. Here's our approach:

```python
# Pseudocode for the FEM pipeline

class FEMModel:
    nodes: List[Node]         # (x, y, z) coordinates
    elements: List[Element]   # beam, shell, solid
    loads: List[Load]         # forces, moments, pressures
    supports: List[Support]   # fixed, pinned, roller, spring

    def assemble(self) -> sparse.csr_matrix:
        """Assemble global stiffness matrix K (sparse)"""
        K = sparse.lil_matrix((n_dof, n_dof))
        for element in self.elements:
            ke = element.stiffness_matrix()    # Local 12x12
            Te = element.transformation()       # Local → global
            Ke = Te.T @ ke @ Te                # Global element
            K[element.dofs, element.dofs] += Ke
        return K.tocsr()

    def solve_linear(self) -> np.ndarray:
        """Solve K·u = F for displacements"""
        K = self.assemble()
        F = self.load_vector()
        K_red, F_red = self.apply_boundary(K, F)
        u = sparse.linalg.spsolve(K_red, F_red)
        return self.expand_solution(u)

    def solve_modal(self, n_modes=12) -> Tuple[np.ndarray, np.ndarray]:
        """Solve eigenvalue problem for natural frequencies"""
        K = self.assemble()
        M = self.mass_matrix()
        K_red, M_red = self.apply_boundary_eigen(K, M)
        eigenvalues, eigenvectors = sparse.linalg.eigsh(
            K_red, k=n_modes, M=M_red, sigma=0, which='LM'
        )
        omega = np.sqrt(eigenvalues)
        periods = 2 * np.pi / omega
        return periods, eigenvectors
```

**Performance targets**:
- 100-node model: <0.1s
- 1,000-node model: <1s
- 10,000-node model: <10s
- 50,000-node model: <60s (cloud-offloaded)

### 8.2 Building Modeler UI

The UI that makes this usable for engineers (not just programmers):

**Grid System**:
```
User defines:
  X-grids: A(0), B(6000), C(12000), D(18000) mm
  Y-grids: 1(0), 2(5000), 3(10000) mm
  Stories: GF(0), 1F(3200), 2F(6400), 3F(9600), Terrace(12800) mm

→ Auto-generates 3D grid wireframe
→ User clicks grid intersections to place columns
→ User draws between grids to place beams
→ User selects a floor plate area for slabs
→ User draws wall paths
```

**Technology**:
- React Three Fiber for 3D
- Zustand for state
- Dockview for panel layout (already using)
- Custom 2D canvas for plan views (HTML Canvas or SVG)

### 8.3 IS 1893:2016 Seismic Loading

```python
# IS 1893:2016 Part 1 — Seismic load calculation

def equivalent_static_force(
    Z: float,           # Zone factor (0.10, 0.16, 0.24, 0.36)
    I: float,           # Importance factor (1.0, 1.2, 1.5)
    R: float,           # Response reduction factor (3.0–5.0 for RC)
    Sa_g: float,        # Spectral acceleration coefficient
    W: float,           # Seismic weight of building (kN)
) -> float:
    """IS 1893:2016 Cl. 7.6.1 — Design base shear"""
    Ah = (Z * I * Sa_g) / (2 * R)  # Design horizontal acceleration
    VB = Ah * W                     # Base shear
    return VB

def vertical_distribution(
    VB: float,           # Base shear (kN)
    Wi: List[float],     # Floor weights (kN)
    hi: List[float],     # Floor heights from base (m)
) -> List[float]:
    """IS 1893:2016 Cl. 7.6.2 — Distribute base shear to floors"""
    Qi = []
    sum_Wh2 = sum(w * h**2 for w, h in zip(Wi, hi))
    for w, h in zip(Wi, hi):
        Qi.append(VB * (w * h**2) / sum_Wh2)
    return Qi
```

### 8.4 AI Copilot Architecture

```
User: "Design a 5-story residential building, 4 bays × 3 bays,
       span 6m × 5m, story height 3.2m, Zone III, medium soil"

AI Copilot Pipeline:
1. NLP Parser → Extract: stories=5, bays=(4,3), spans=(6000,5000),
                          height=3200, zone=III, soil=medium
2. Model Generator → Create grid, place columns, beams, slabs
3. Load Calculator → Auto-apply IS 875 dead+live, IS 1893 seismic
4. Analysis Runner → FEM solve → forces in all members
5. Design Runner → IS 456 design for each beam, column, slab
6. Optimization → Suggest section sizes, rebar optimization
7. Report Generator → Full calculation report with clause references
8. Visualization → 3D model with rebar, force diagrams

Time: ~30 seconds for full design
Traditional: 2-3 days in ETABS
```

---

## 9. Hard Technical Problems & Solutions

> "Everyone has a plan until they get punched in the mouth." — Mike Tyson
>
> This section is where we get punched. These are the problems that kill structural software projects. We name them, face them, and write down exactly how we'll solve them.

### 9.1 Problem: Python Is Slow for FEM — Should We Use C++/Rust?

**The fear:** Python is 50-100x slower than C++ for raw loops. FEM needs to assemble and solve matrices with millions of DOFs. ETABS uses compiled C++. Are we dead on arrival?

**The reality:** It depends on *where* the time is spent.

**Profiling a typical FEM solve:**
```
Step                    | % of wall time | Language that matters
------------------------|----------------|---------------------
Element stiffness calc  | 10-15%         | NumPy (C under hood) ✅
Global matrix assembly  | 15-20%         | SciPy sparse (C) ✅
Linear solve (Kx = F)   | 40-60%         | SciPy spsolve → UMFPACK/SuperLU (Fortran/C) ✅
Eigenvalue (modal)      | 30-50%*        | SciPy eigsh → ARPACK (Fortran) ✅
Post-processing         | 5-10%          | NumPy vectorized ✅
Python overhead         | 2-5%           | Pure Python (loops, book-keeping)
```
*\* Modal analysis only*

**Key insight:** 95%+ of FEM compute time is in C/Fortran libraries called through NumPy/SciPy. Python is just the orchestrator. PyNite (687 stars, MIT license) already proves this — it does full 3D frame analysis, P-Δ, modal analysis, and DKMQ shell elements in pure Python+NumPy and handles real structures.

**Our strategy — 3 tiers:**

| Tier | Model Size | Solver | Where | Target Time |
|------|-----------|--------|-------|-------------|
| **Tier 1: Library** | 1-5,000 DOF | SciPy sparse (spsolve) | Python process | < 2 sec |
| **Tier 2: Desktop** | 5,000-100,000 DOF | SciPy + sparse LU preconditioning | Python + multiprocessing | < 30 sec |
| **Tier 3: Cloud** | 100,000-1M+ DOF | Rust solver (nalgebra-sparse) or C++ (Eigen) via PyO3/pybind11 | Cloud worker | < 2 min |

**Tier 1 is where we start.** A typical 10-story building with 200 beams + 100 columns = ~3,000 DOF. SciPy handles this in milliseconds.

**When to go Rust/C++ (and NOT before):**
- When we have 10+ validated benchmark models passing in Python
- When profiling shows the *solver* (not assembly, not post-processing) is the bottleneck
- When users are actually hitting the wall (>30 sec solve times)
- Target: Phase 3 of roadmap (not Phase 0 or 1)

**What PyNite taught us:**
- v2.4.2 got ~30% faster assembly just by vectorizing NumPy operations (no C++ needed)
- Their main bottleneck is plate/shell stiffness matrix calculation, not the solver
- Lesson: Optimize the Python first. Rewrite to C++ is the *last* resort, not the *first* instinct

**Numerical accuracy:**
- SciPy spsolve uses SuperLU (direct solver) — same class of algorithm as commercial FEM
- We will check condition numbers (`numpy.linalg.cond`) and warn if matrix is ill-conditioned
- Every solve will include residual check: `‖Kx - F‖ / ‖F‖ < 1e-10`
- Benchmark: Every IS 456 function already validated against hand calculations (5,003 tests, 99% coverage). FEM solver gets the same treatment.

**Decision: Start with Python + SciPy. It's not a compromise — it's the right tool.**

### 9.2 Problem: Can You Really Do 3D Structural Modeling in a Browser?

**The fear:** ETABS has a native desktop modeler built over 30 years. We're trying to do this in a web browser? That sounds impossible.

**The reality:** The browser caught up. Three things happened:

1. **WebGL 2.0** (2017) — GPU-accelerated 3D rendering, universally supported
2. **WebGPU** (2024) — Native GPU compute in browser, 10-100x faster than WebGL for compute shaders
3. **React Three Fiber** (R3F) — Declarative 3D in React, 25k+ stars, production-proven

**We already have this working.** Our current React app uses R3F for 3D beam visualization with rebar placement. Extending to full structural modeling is incremental, not revolutionary.

**What we need vs what exists:**

| Feature | Status | Technology |
|---------|--------|------------|
| 3D model viewing (rotate, zoom, pan) | ✅ Already working | React Three Fiber |
| Beam/column 3D geometry with rebar | ✅ Already working | Three.js + custom geometry |
| Grid-based modeling (draw beams/columns on grid) | 🔨 Phase 1 | R3F + raycasting + snapping |
| Node/member editing (select, modify, delete) | 🔨 Phase 1 | R3F event system + Zustand state |
| Load visualization (arrows, distributed loads) | 🔨 Phase 1 | Three.js arrows + line geometry |
| Deformed shape animation | 🔨 Phase 2 | Vertex shader displacement |
| Force diagram overlay (BMD, SFD) | 🔨 Phase 2 | Line geometry + color mapping |
| 10,000+ element rendering | 🔨 Phase 2 | Instanced meshes + LOD |
| Section property preview | 🔨 Phase 1 | 2D canvas overlay or R3F cross-section |

**Performance for large models:**
- **Instanced rendering:** Three.js `InstancedMesh` draws 100,000 similar objects in one draw call. A building with 5,000 beams = trivial.
- **Level of Detail (LOD):** Far-away members become simple lines. Close-up members show full cross-section with rebar.
- **Web Workers:** FEM assembly + solve runs in a separate thread. UI never freezes.
- **Progressive loading:** Show wireframe instantly, load detailed geometry progressively.

**What Speckle proved:**
Speckle (open-source AEC data platform, used by Arup, WSP, SOM) renders full BIM models in the browser. Their viewer handles IFC models with 100,000+ elements. If they can do it, we absolutely can — and our models are simpler (structural only, no MEP/arch).

**Modeling UX — How it will work:**

```
1. Define grid system (axes + levels)
   └── Input: axis spacing X/Y + story heights (or import from DXF/CSV)

2. Place members on grid intersections
   └── Click node → click node → beam/column created
   └── Snap to grid intersections, offset allowed
   └── Property panel: section size, material, supports

3. Apply loads
   └── Click member → add dead/live/seismic/wind
   └── Auto-generate load combinations per IS 875/1893

4. Analyze → Design → Report
   └── One-click pipeline (already exists in Python core)
```

**Decision: Browser 3D modeling is absolutely feasible. We have the foundation and the proof.**

### 9.3 Problem: How Do We Import ETABS Models?

**The fear:** Engineers have years of ETABS models. If they can't bring existing work into our tool, they won't switch. But ETABS model files (.EDB) are proprietary binary format.

**The reality:** There are 4 import paths, ordered by feasibility:

#### Path 1: ETABS CSV/Text Export (Available NOW)

ETABS exports data as CSV and text files. We already support beam force CSV import (`etabs_import.py`).

**What we can import today:**
- Beam forces (Vu, Mu, Tu per load combination) ✅
- Frame geometry (coordinates, section assignments) — via CSV ✅
- Story data, section properties — via CSV ✅

**What we need to add:**
- Column forces import
- Load case/combination definitions
- Node restraints (supports)
- Shell element data

**Effort: 2-3 weeks.** This is the pragmatic first step. Tell engineers: "Export your ETABS model as CSV tables → import into BHEEM → redesign with IS 456."

#### Path 2: E2K Text File Format (Phase 1)

ETABS can export to `.e2k` format — a structured text file with the full model definition (geometry, sections, materials, loads, restraints, everything). It's human-readable.

**E2K file structure (example):**
```
$ PROGRAM INFORMATION
  PROGRAM "ETABS" VERSION "20.0.0"

$ MATERIAL PROPERTIES
  MATERIAL "M25" TYPE "Concrete" FY 0 FC 25 E 25000

$ FRAME SECTIONS
  FRAMESECTION "B230x450" MATERIAL "M25" SHAPE "Rectangular" D 450 B 230

$ CONNECTIVITY - MEMBER INCIDENCES
  LINEASSIGN "B1" POINT "1" POINT "2" SECTION "B230x450"

$ JOINT COORDINATES
  POINT "1"  0  0  0
  POINT "2"  5000  0  0

$ LOAD PATTERNS
  LOADPATTERN "Dead" TYPE "Dead"
  LOADPATTERN "Live" TYPE "Live"
```

**Strategy:**
- Write a line-by-line `.e2k` parser (it's keyword-based, not complex)
- Map CSI section/material names to our core types
- Build a model translation layer: E2K → our `StructuralModel` object
- Initial support: frames + joints + loads. Shells later.

**Challenge:** CSI doesn't publish formal e2k documentation anymore (their wiki is down). But the format is stable, well-known in the community, and hundreds of `.e2k` files exist in academic papers. We'll reverse-engineer from sample files.

**Effort: 4-6 weeks.** This gives engineers one-click import of full ETABS models.

#### Path 3: IFC Universal Exchange (Phase 2)

IFC (Industry Foundation Classes) is the open standard for BIM data exchange. ETABS exports IFC. So does Revit, Tekla, SAP2000, and every modern structural tool.

**Advantages:**
- Universal — not locked to one vendor
- Open standard (buildingSMART)
- Libraries exist: `ifcopenshell` (Python, well-maintained, 1.5k+ stars)
- Contains geometry, materials, loads, structural model, analysis results

**Strategy:**
- Use `ifcopenshell` to parse IFC files
- Map IFC structural entities (IfcBeam, IfcColumn, IfcSlab) to our types
- Extract material properties, cross-sections, and loads
- This also enables Revit → BHEEM import (huge win)

**Effort: 6-8 weeks.** But the payoff is enormous — import from ANY BIM tool, not just ETABS.

#### Path 4: ETABS API / COM Automation (Phase 3, Windows Only)

ETABS has a COM/API interface. We can automate ETABS to extract model data programmatically.

**Why this is LAST:**
- Windows-only (COM is Windows technology)
- Requires ETABS license installed
- Fragile (version-dependent API)
- Slow (COM marshaling)

**When it makes sense:** For firms that want to keep using ETABS for analysis but use BHEEM for IS 456 design checks and reporting. This is a "co-existence" strategy, not a "replacement" strategy.

**Our migration story for engineers:**

```
TODAY:      Export CSV from ETABS → Import to BHEEM → Design checks + reports
PHASE 1:    Export .e2k from ETABS → Full model import → Complete redesign
PHASE 2:    Export IFC from ANY tool → BHEEM handles everything
PHASE 3:    Don't need ETABS anymore → Model directly in BHEEM
```

**Decision: Four-path strategy. Start with CSV (ready now), build e2k parser next, IFC for universality, COM last.**

### 9.4 Problem: Will Engineers Trust This?

**The fear:** Structural engineers sign off on designs. If the software is wrong, buildings collapse. No engineer will trust an open-source tool written by AI unless it's proven beyond doubt.

**This is the HARDEST problem.** Not technical — social. And we take it deadly seriously.

**Trust-building strategy (5 layers):**

#### Layer 1: Transparent Calculations
Every output includes the IS 456 clause reference and the actual formula used:
```
Shear capacity Vc = 142.3 kN
  ├── Clause: IS 456:2000, Table 19
  ├── Formula: τc × b × d
  ├── τc = 0.62 N/mm² (for pt = 1.05%, M25 concrete)
  ├── b = 230 mm, d = 412 mm
  └── Vc = 0.62 × 230 × 412 × 1e-3 = 58.7 kN (per meter)
```
An engineer can verify every step by hand. No black box.

#### Layer 2: Validation Against Known Results
- Every IS 456 function: tested against **hand calculations** from SP 16, SP 34, and textbooks
- FEM solver: validated against **benchmark problems** (MacNeal-Harder patch tests, Scordelis-Lo roof, etc.)
- Full building models: validated against **ETABS and STAAD results** (published comparison reports)
- **5,003 tests passing today** — this number only grows

#### Layer 3: Third-Party Verification
- Publish validation report as a peer-reviewed paper
- Partner with IIT structural engineering departments for independent testing
- Submit to BIS (Bureau of Indian Standards) for review
- Get practicing engineers (50+ years experience) to audit clause mappings

#### Layer 4: Open Source = Auditable
- Every formula is readable Python code — not compiled binary
- Any engineer can read `codes/is456/beam/shear.py` and verify the logic
- Bug reports and fixes are public — no hidden errata
- Version history shows exactly what changed and why

#### Layer 5: Conservative Defaults
- When IS 456 is ambiguous, we choose the **conservative** interpretation
- Partial safety factors are never reduced without explicit user override
- Warnings on edge cases (high reinforcement ratio, slender columns, etc.)
- The library will REFUSE to design if inputs violate IS 456 limits (not just warn)

**Decision: Trust is built incrementally. Transparent calculations → validation reports → third-party audits → conservative defaults. No shortcuts.**

### 9.5 Problem: How Do We Handle Large Models?

**The fear:** A 40-story building might have 10,000+ members and 50,000+ DOF. Can we handle this without becoming uselessly slow?

**Scaling strategy:**

| Model Size | Members | DOF | Strategy | Target Time |
|-----------|---------|-----|----------|-------------|
| Small (1-5 stories) | < 500 | < 3,000 | Direct solve (SciPy spsolve) | < 1 sec |
| Medium (5-20 stories) | 500-3,000 | 3,000-20,000 | Sparse LU (SciPy splu) | < 10 sec |
| Large (20-40 stories) | 3,000-10,000 | 20,000-60,000 | Iterative (CG/GMRES + preconditioner) | < 60 sec |
| Very large (40+ / complex) | 10,000+ | 60,000+ | Cloud solver (Rust) or substructuring | < 5 min |

**Key techniques:**
- **Sparse matrix storage:** Only non-zero entries stored. A 50,000×50,000 matrix with 0.1% fill = 2.5M entries (20MB), not 20GB.
- **Bandwidth optimization:** Cuthill-McKee reordering reduces solver bandwidth → faster LU decomposition.
- **Substructuring:** Solve each floor independently, then combine. Embarrassingly parallel.
- **Iterative solvers:** For very large systems, CG with incomplete Cholesky preconditioner converges fast for structural problems (matrices are SPD).

**Progressive UX for large models:**
1. User clicks "Analyze" → wireframe deformation shows in 2 seconds (coarse solve)
2. Background worker refines the solution → full results update live
3. Design runs in parallel for each member → results stream via WebSocket

**Decision: SciPy handles 90% of real-world buildings. Cloud solver for the 10% of extreme cases. Substructuring for embarrassingly parallel speedup.**

### 9.6 Problem: Multiple Design Codes (Not Just IS 456)

**The fear:** If we only support IS 456, we limit ourselves to India. But implementing every code is impossible.

**Strategy: IS 456 first, code-agnostic architecture always.**

Our 4-layer architecture already separates the math:
```
core/           → Code-agnostic types (BeamSection, Forces, Materials)
codes/is456/    → IS 456 math (pure functions, explicit units)
codes/aci318/   → ACI 318 math (same interfaces, different formulas)  [STUB]
codes/ec2/      → Eurocode 2 math  [STUB]
services/       → Orchestration (calls whichever code module is selected)
```

**The interface contract:**
Every design code module implements the same function signatures:
```python
# codes/is456/beam/shear.py
def check_shear(Vu_kN, b_mm, d_mm, fck, Ast_mm2, ...) -> ShearResult

# codes/aci318/beam/shear.py  (future)
def check_shear(Vu_kN, b_mm, d_mm, fc_prime, Ast_mm2, ...) -> ShearResult
```

The `services/api.py` layer dispatches based on selected code:
```python
def design_beam(inputs, code="IS456"):
    if code == "IS456":
        return is456.beam.design(inputs)
    elif code == "ACI318":
        return aci318.beam.design(inputs)
```

**Prioritized code support:**
1. **IS 456:2000** — Complete (beam, column, footing, ductile detailing). Our foundation.
2. **IS 1893:2016** — Seismic loads. Required for any Indian building.
3. **IS 875** — Dead/live/wind loads. Required for load generation.
4. **ACI 318** — Opens US market. Many formulas similar to IS 456.
5. **Eurocode 2** — Opens EU market. Different philosophy (partial factors vs load factors).

**Decision: IS 456 is our moat. The architecture supports plugging in any code. We don't implement others until IS 456 is bulletproof and the library has paying users.**

### 9.7 Problem: FEM Element Types — What Do We Actually Need?

**The fear:** ETABS supports 20+ element types. Do we need to implement all of them?

**The reality:** 95% of building structures use just 3 element types:

| Element | Use Case | Priority | Complexity |
|---------|----------|----------|------------|
| **Frame (beam-column)** | Beams, columns, braces | Phase 1 | Medium — 12 DOF/element, well-understood |
| **Shell (plate/membrane)** | Slabs, shear walls, cores | Phase 2 | Hard — MITC4 or DKMQ, locking issues |
| **Spring/Link** | Isolators, connections | Phase 3 | Easy — diagonal stiffness |

**What we DON'T need (and won't build):**
- Solid elements (3D stress) — not used in building design
- Cable elements — rare, specialist use
- Contact elements — not relevant for RC design
- Nonlinear material models — advanced analysis, Phase 4+ if ever

**Frame element roadmap:**
```
Phase 1: Euler-Bernoulli beam (6 DOF/node, 2 nodes)
         → Handles: axial, bending (2-axis), torsion, shear
         → Good for: 90% of building frames

Phase 2: Timoshenko beam (adds shear deformation)
         → Needed for: deep beams, stocky columns
         → Adds: shear correction factors per code

Phase 2: P-Delta (geometric stiffness)
         → Needed for: tall buildings, slender columns
         → Adds: Kg matrix, iterative solve
```

**Shell element roadmap:**
```
Phase 2: MITC4 (Mixed Interpolation of Tensorial Components)
         → Locking-free, works for thin and thick plates
         → 4-node, 5 DOF/node (3 translations + 2 rotations)
         → Well-documented, ABAQUS uses a variant

Phase 3: Meshing automation
         → Auto-mesh slabs and walls from edge definitions
         → Adaptive refinement near openings and supports
```

**Decision: Frame elements first (covers 90% of needs). Shells in Phase 2. Never build what engineers don't need for RC building design.**

### 9.8 Excel Validation & Engineer Adoption Strategy

> Engineers live in Excel. If they can verify our answers in a spreadsheet they already trust, they'll trust the library. This isn't just validation — it's our #1 adoption funnel.

**The insight:** We don't need to convince engineers to *stop* using Excel. We need to meet them *inside* Excel, prove our library matches their hand calculations, and then offer them something better.

#### Option 1: Validation Spreadsheets (Ready-Made Excel Templates)

**What:** Pre-built `.xlsx` files with IS 456 hand calculations alongside library output — cell by cell, formula by formula.

**How it works:**
```
Sheet: "Beam Shear Check — IS 456 Table 19"
┌─────────────────────────────────────────────────────────────────────┐
│ Column A-D: INPUTS          │ Column F-I: EXCEL HAND CALC         │
│ b = 230 mm                  │ pt = (Ast / b*d) × 100 = 1.05%     │
│ d = 412 mm                  │ τc = VLOOKUP(pt, Table19, ...) =0.62│
│ fck = 25 N/mm²              │ Vc = τc × b × d / 1000 = 58.7 kN   │
│ Ast = 994 mm²               │                                     │
│ Vu = 85 kN                  │ Column K-N: LIBRARY OUTPUT           │
│                              │ Vc = 58.7 kN    ← from Python      │
│                              │ Status: SAFE     ✅ MATCH           │
│                              │ Clause: Table 19                    │
│                              │                                     │
│                              │ Column P: DELTA                     │
│                              │ |Excel - Library| = 0.00 kN ✅     │
└─────────────────────────────────────────────────────────────────────┘
```

**Template library (one sheet per function):**

| Template | IS 456 Clause | Status |
|----------|--------------|--------|
| Beam flexure (singly reinforced) | Cl 38.1, Annex G | Can build now |
| Beam flexure (doubly reinforced) | Cl 38.1 | Can build now |
| Beam shear check | Table 19, Cl 40.2 | Can build now |
| Beam shear reinforcement | Cl 40.4 | Can build now |
| Beam torsion design | Cl 41.4 | Can build now |
| Beam deflection check | Cl 23.2, Table 4 | Can build now |
| Column axial capacity | Cl 39.3 | Can build now |
| Column uniaxial bending | Cl 39.5 | Can build now |
| Column biaxial check | Cl 39.6 | Can build now |
| Column slenderness | Cl 25.1.2 | Can build now |
| Footing bearing pressure | Cl 34.1 | Can build now |
| Footing one-way shear | Cl 34.2 | Can build now |
| Footing punching shear | Cl 31.6 | Can build now |
| Development length | Cl 26.2 | Can build now |
| Lap splice length | Cl 26.2.5 | Can build now |
| Crack width check | Annex F | Can build now |

**Effort: 1-2 weeks per batch of 5 templates.** These become downloadable assets on our docs site and GitHub releases.

**Why this is powerful:**
- Engineer opens Excel, sees familiar formulas
- Plugs in *their* project's numbers
- Sees library gives identical answers
- Trust established in 10 minutes

#### Option 2: Python-to-Excel Bridge (xlwings / openpyxl)

**What:** A Python script that takes an Excel input sheet, runs the library, and writes results back into the same Excel file.

**How it works:**
```python
# engineer_validate.py — ships with the library
import openpyxl
from structural_lib import design_beam_is456

wb = openpyxl.load_workbook("my_beams.xlsx")
ws = wb["BeamDesign"]

for row in ws.iter_rows(min_row=2):  # skip header
    inputs = {
        "b_mm": row[0].value,      # Column A
        "d_mm": row[1].value,      # Column B
        "fck": row[2].value,       # Column C
        "fy": row[3].value,        # Column D
        "Mu_kNm": row[4].value,    # Column E
        "Vu_kN": row[5].value,     # Column F
    }
    result = design_beam_is456(**inputs)
    row[7].value = result.Ast_required   # Column H: Library Ast
    row[8].value = result.status         # Column I: SAFE/UNSAFE
    row[9].value = result.clause_ref     # Column J: IS 456 clause

wb.save("my_beams_validated.xlsx")
```

**Engineer workflow:**
```
1. Fill beam data in Excel (columns A-F) ← they already have this
2. Run: pip install structural-lib-is456 && python engineer_validate.py
3. Open Excel → see library results next to their hand calcs
4. Compare. Done.
```

**Effort: 1 week for the bridge script + example templates.** openpyxl is pure Python, no Excel installation needed.

#### Option 3: Excel Add-in with xlwings (Live Functions)

**What:** Custom Excel functions that call the Python library in real-time. Engineer types `=BHEEM_SHEAR(b, d, fck, Ast, Vu)` in a cell and gets the answer.

**How it works:**
```python
# excel_addin.py — xlwings UDF (User Defined Function)
import xlwings as xw

@xw.func
@xw.arg('b_mm', doc='Beam width in mm')
@xw.arg('d_mm', doc='Effective depth in mm')
@xw.arg('fck', doc='Concrete grade in N/mm²')
@xw.arg('Ast_mm2', doc='Tension steel area in mm²')
@xw.arg('Vu_kN', doc='Factored shear force in kN')
@xw.ret(expand='table')
def BHEEM_SHEAR(b_mm, d_mm, fck, Ast_mm2, Vu_kN):
    """Check shear capacity per IS 456 Table 19"""
    from structural_lib import check_beam_shear_is456
    result = check_beam_shear_is456(
        b_mm=b_mm, d_mm=d_mm, fck=fck,
        Ast_mm2=Ast_mm2, Vu_kN=Vu_kN
    )
    return [[result.Vc_kN, result.Vs_required_kN, result.status]]
```

**Custom Excel functions we'd provide:**

| Excel Function | Python Function | Returns |
|---------------|----------------|---------|
| `=BHEEM_FLEXURE(b, d, fck, fy, Mu)` | `design_beam_is456()` | Ast_req, xu/d, status |
| `=BHEEM_SHEAR(b, d, fck, Ast, Vu)` | `check_beam_shear_is456()` | Vc, Vs_req, status |
| `=BHEEM_DEFLECTION(b, d, L, Ast, Ast_comp)` | `check_deflection_is456()` | L/d_actual, L/d_limit, status |
| `=BHEEM_COLUMN(b, D, fck, fy, Pu, Mu)` | `design_column_is456()` | Ast_req, Asc, status |
| `=BHEEM_FOOTING(L, B, d, fck, P, M)` | `design_footing_is456()` | Ast_req, punching, status |
| `=BHEEM_DEV_LENGTH(dia, fck, fy)` | `development_length_is456()` | Ld in mm |
| `=BHEEM_CRACK(b, d, Ast, M, cover)` | `crack_width_is456()` | width_mm, limit, status |

**Pros:** Engineers use it like any other Excel function. Zero learning curve. Live recalculation.
**Cons:** Requires xlwings + Python installed. Windows/Mac only (not browser Excel).
**Effort: 2-3 weeks.** xlwings has excellent UDF support.

#### Option 4: Google Sheets + Cloud API

**What:** Google Sheets custom functions that call our FastAPI backend. Works in any browser, no installation.

**How it works:**
```javascript
// Google Apps Script — Custom function
function BHEEM_SHEAR(b_mm, d_mm, fck, Ast_mm2, Vu_kN) {
  const url = "https://api.bheem.dev/v1/design/shear-check";
  const payload = { b_mm, d_mm, fck, Ast_mm2, Vu_kN };
  const response = UrlFetchApp.fetch(url, {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload)
  });
  const result = JSON.parse(response.getContentText());
  return [[result.Vc_kN, result.Vs_required_kN, result.status]];
}
```

**Pros:** Zero install. Works on any device. Sharable Google Sheets become our viral loop.
**Cons:** Needs internet + our API running. Rate limiting needed. Latency per cell.
**Effort: 1 week** (we already have the FastAPI endpoints).

**Viral potential:** Engineer shares a Google Sheet with BHEEM functions → colleague opens it → functions just work → new user acquired. **Zero friction.**

#### Option 5: Comparison Report Generator

**What:** Engineer provides inputs (Excel/CSV), library runs all calculations, outputs a formatted comparison report (PDF/Excel) showing hand-calc vs library side by side.

```
INPUT:  my_beams.xlsx (engineer's beam schedule)
OUTPUT: validation_report.xlsx

Report Columns:
| Beam ID | b | d | Mu | Vu | Excel Ast | Library Ast | Delta | Match? |
|---------|---|---|----|----|-----------|-------------|-------|--------|
| B1      |230|412|125 | 85 | 628       | 628.3       | 0.05% | ✅     |
| B2      |300|550|210 |120 | 1005      | 1005.1      | 0.01% | ✅     |
```

Plus a summary page:
```
VALIDATION SUMMARY
─────────────────
Total beams checked: 47
Exact matches (< 0.1% delta): 45 (95.7%)
Close matches (< 1% delta): 2 (4.3%)
Mismatches (> 1% delta): 0 (0%)
Maximum delta: 0.3% (beam B23, shear reinforcement)

CONCLUSION: Library results match hand calculations within 0.3% for all 47 beams.
Signed: [Engineer Name]  Date: [Date]
```

**This is gold for trust.** An engineer can run this on their REAL project, get a signed validation report, and show it to their boss / client / regulatory body.

**Effort: 2 weeks.** We already have the batch design pipeline + adapters.

#### Recommended Rollout Sequence

```
Phase 0 (NOW — with library launch):
├── Option 1: Validation spreadsheets (16 templates)     ← TRUST builder
├── Option 2: Python-to-Excel bridge script               ← POWER users
└── Option 5: Comparison report generator                  ← PROOF for bosses

Phase 1 (Month 3):
├── Option 3: xlwings Excel add-in (live functions)        ← DAILY USE tool
└── Marketing: "Validate our library with YOUR spreadsheet"

Phase 2 (Month 6, after cloud API exists):
├── Option 4: Google Sheets integration                    ← VIRAL growth
└── Marketing: "Share a beam design sheet, functions included"
```

#### Why This Is Our Secret Weapon

| Strategy | Effect |
|----------|--------|
| Validation spreadsheets | "I checked it against my Excel — it matches" → instant trust |
| Python-to-Excel bridge | "I ran 200 beams in 10 seconds instead of 2 days" → time savings |
| Excel add-in | "I use BHEEM functions daily in my existing workflow" → habit formation |
| Google Sheets | "I shared the sheet with my team — they all use it now" → viral adoption |
| Comparison reports | "Here's a validation report signed by our senior engineer" → institutional trust |

**The funnel:**
```
Excel templates (free, zero install) → validates library → trusts it
    ↓
Python bridge (pip install) → automates their Excel work → saves time
    ↓
Excel add-in (daily use) → BHEEM functions in every spreadsheet → dependency
    ↓
Google Sheets (viral) → shared across teams → org-wide adoption
    ↓
Full BHEEM app (modeling + analysis + design) → replaces ETABS entirely
```

**Engineers don't switch tools because you tell them to. They switch because the new tool made their Excel work faster, and then they realized they didn't need Excel anymore.**

### 9.9 Summary: Technical Risk Matrix

| Problem | Severity | Solution | When |
|---------|---------|----------|------|
| Python performance | Medium | SciPy (C/Fortran under hood) handles 90% of buildings. Rust for extreme cases. | Phase 1-3 |
| Browser 3D modeling | Medium | R3F already working. Instanced meshes + LOD for scale. WebGPU later. | Phase 1-2 |
| ETABS model import | High | CSV now → e2k parser Phase 1 → IFC Phase 2 → COM last. | Phase 0-3 |
| Engineer trust | Critical | Transparent calcs + 5,003 tests + third-party validation + open source. | Always |
| Large model handling | Medium | Sparse solvers + substructuring + cloud offloading. | Phase 2-3 |
| Multi-code support | Low (now) | IS 456 first, code-agnostic architecture from day 1. | Phase 4+ |
| Element types | Medium | Frame first, shell Phase 2. Only what RC buildings need. | Phase 1-2 |
| Excel validation & adoption | High | 5 options: templates → Python bridge → xlwings add-in → Google Sheets → reports. | Phase 0-2 |

**Bottom line: Every hard problem has a concrete path. None of them require magic — they require disciplined engineering, clear priorities, and the willingness to say "not yet" to features we don't need today.**

---

## 10. What the Library Still Needs — Algorithms, ML & Optimization

> This is an honest gap analysis. The current library (v0.21.6) is production-ready for IS 456 beam/column/footing design with 104 exported functions, 5,003 tests, and a custom NSGA-II optimizer. But to compete with ETABS and become the go-to structural engineering platform, we need upgrades in three areas: modern libraries, machine learning, and optimization.

### 10.1 Gap Analysis: What We Have vs. What's State-of-the-Art

| Capability | Our Library (v0.21.6) | Best-in-Class Open Source | Gap |
|-----------|----------------------|--------------------------|-----|
| **IS 456 Design** | ✅ 104 functions, beam/column/footing/ductile | No equivalent exists | We ARE best-in-class |
| **Section Properties** | ❌ Rectangular only | `section-properties` (FEM-based, arbitrary shapes) | Critical — can't do T-beams, L-beams, composite |
| **RC Section Analysis** | ❌ Uses simplified formulas | `concrete-properties` (fiber model, moment-curvature) | High — needed for accurate P-M interaction and IS 13920 |
| **Scientific Computing** | ❌ Pure Python, no NumPy | NumPy/SciPy ecosystem | High — 10-100x slower for batch operations |
| **Optimization** | ⚠️ Custom NSGA-II only | DEAP (NSGA-II/III, CMA-ES, GP), scipy.optimize | Medium — limited to evolutionary, no gradient methods |
| **FEM** | ❌ Not implemented | PyNite (frames, P-Δ, modal, shells) | Critical — can't analyze structures |
| **Probabilistic Design** | ❌ Deterministic only | pystra (FORM/SORM, Monte Carlo) | Medium — no reliability analysis |
| **BIM Interoperability** | ❌ CSV only | IfcOpenShell (IFC2x3, IFC4, IFC4x3) | High — can't exchange with Revit, Tekla |
| **Unit Management** | ❌ Naming convention (b_mm, fck) | Pint, forallpeople | Medium — unit errors are #1 engineering bug |
| **Loading Codes** | ❌ Not implemented | No python equivalent | High — IS 875 and IS 1893 are prerequisites |
| **ML/AI** | ❌ None | JaxSSO (differentiable FEM), various research | Future — but specific applications are valuable |
| **Topology Optimization** | ❌ None | SIMP method, JaxSSO, TopOpt-88-lines | Phase 3+ |
| **Fatigue Analysis** | ❌ None | fatpack (rainflow, S-N curves) | Low — not critical for buildings |

### 10.2 Libraries We MUST Integrate (Priority Order)

#### Tier 1: Add NOW (Library Launch) — These Are Table Stakes

**1. NumPy + SciPy (Foundation for everything)**
```python
# BEFORE (current - pure Python):
def interpolate_shear_strength(pt_percent, fck):
    # 50 lines of manual table lookup with if/elif chains
    ...

# AFTER (with NumPy/SciPy):
from scipy.interpolate import interp2d
tau_c = interp2d(pt_values, fck_values, table19_data)(pt, fck)
# 3 lines. Faster. Exact IS 456 Table 19 interpolation.
```

**Why NOW:** Every other library below depends on NumPy. It's the lingua franca of scientific Python. Our library is the ONLY structural engineering library that doesn't use NumPy. That's not a feature — it's a liability when we add FEM.

**Migration strategy:** Add as required dependency (not optional). Keep IS 456 formulas readable — use NumPy for array operations and interpolation, not to obfuscate the math.

**2. section-properties (Arbitrary cross-section analysis)**

```python
import sectionproperties.pre.geometry as geometry
from sectionproperties.analysis import Section

# Define a T-beam cross-section
flange = geometry.rectangular_section(b=1000, d=150)  # slab flange
web = geometry.rectangular_section(b=230, d=300).align_to(flange, "bottom")
t_beam = flange + web

section = Section(geometry=t_beam)
section.calculate_geometric_properties()
section.calculate_warping_properties()

# Get: A, Ixx, Iyy, Zxx, Zyy, J (torsion), Cw (warping), plastic moduli
# Works for ANY shape — L-beams, box sections, composite, with holes
```

**Why NOW:** Engineers don't design rectangular beams in isolation. In real buildings:
- Beams act as T-beams (with slab flange)
- Columns can be L-shaped, T-shaped, or circular
- Sections have cutouts for ducts
- Composite steel-concrete sections exist

Our library can only handle `b × d` rectangles. That's a deal-breaker for real projects.

**3. Pint (Unit safety)**

```python
import pint
ureg = pint.UnitRegistry()

# Type-safe units — impossible to mix mm and m by accident
b = 230 * ureg.mm
d = 450 * ureg.mm
fck = 25 * ureg.MPa

# Automatic conversion
area = b * d  # → 103500 mm²
area.to(ureg.m**2)  # → 0.1035 m²
```

**Why NOW:** Unit errors have caused real structural failures (Mars Climate Orbiter, Hyatt Regency walkway). Our current approach (naming convention: `b_mm`, `fck`) works but relies on discipline. Pint makes wrong units a runtime error, not a silent bug.

**4. IfcOpenShell (BIM interoperability)**

```python
import ifcopenshell

# Read a Revit/Tekla-exported IFC file
ifc = ifcopenshell.open("building_model.ifc")

# Extract all beams
beams = ifc.by_type("IfcBeam")
for beam in beams:
    props = ifcopenshell.util.element.get_psets(beam)
    # Get: section dimensions, material, span, supports
    # → Feed directly into our design_beam_is456()
```

**Why NOW:** IFC is the universal BIM format. Every structural tool (Revit, Tekla, STAAD, ETABS) exports IFC. Without IFC support, we're an island — engineers can't integrate us into their workflow.

#### Tier 2: Add in Phase 1 (Months 3-6)

**5. concrete-properties (Advanced RC section analysis)**

```python
from concreteproperties.concrete_section import ConcreteSection
from concreteproperties.stress_strain_profile import (
    ConcreteLinear, SteelElasticPlastic
)

# Define materials per IS 456
concrete = ConcreteLinear(elastic_modulus=25e3, ultimate_strain=0.0035)
steel = SteelElasticPlastic(yield_strength=415, elastic_modulus=2e5)

# Create section, add bars, analyze
section = ConcreteSection(...)
moment_curvature = section.moment_curvature_analysis()
interaction = section.moment_interaction_diagram()  # True P-M curve
biaxial = section.biaxial_bending_diagram()  # True biaxial surface
```

**Why Phase 1:** Our current P-M interaction curve uses IS 456 simplified method (Cl 39.5-39.6). `concrete-properties` uses fiber analysis — more accurate, works for any section shape, and produces the actual failure surface instead of an approximation.

**6. Shapely (2D geometry engine)**

```python
from shapely.geometry import Polygon, Point

# Define footing shape (can be irregular, with cutouts)
footing = Polygon([(0,0), (2000,0), (2000,1500), (0,1500)])
column = Point(1000, 750).buffer(200)  # circular column
critical_section = column.buffer(d/2)  # punching shear perimeter

perimeter = critical_section.length  # exact, works for any shape
area_outside = footing.difference(critical_section).area
```

**Why Phase 1:** Real footings aren't always rectangular. Combined footings, strap footings, and irregular shapes need proper 2D geometry operations.

**7. IS 875 / IS 1893 Loading Code Libraries**

No Python library exists for Indian loading codes. We build them ourselves:

```python
# IS 875 Part 2 — Live Loads
from structural_lib.codes.is875 import live_loads
load = live_loads.get_floor_load(occupancy="residential")  # 2.0 kN/m²

# IS 1893:2016 — Seismic Loads
from structural_lib.codes.is1893 import seismic
Ah = seismic.design_horizontal_coefficient(
    zone=3, importance=1.0, R=5.0, soil="medium",
    T=0.5  # fundamental period
)
base_shear = seismic.calculate_base_shear(W=12000, Ah=Ah)
story_forces = seismic.distribute_vertical(base_shear, story_weights, story_heights)
```

**Why Phase 1:** You can't design a building without knowing the loads. Every ETABS user starts with load generation. Without IS 875/1893, our library can only check designs — it can't generate them from scratch.

#### Tier 3: Add in Phase 2+ (Months 6-12)

| Library | Purpose | When |
|---------|---------|------|
| `PyNite` (or custom FEM) | Frame analysis, P-Δ, modal | Phase 2 |
| `pystra` | Structural reliability (FORM/SORM, Monte Carlo) | Phase 3 |
| `forallpeople` | Alternative unit system (lighter than Pint) | Evaluate |
| `networkx` | Graph-based structural topology analysis | Phase 2 |
| `meshio` | Mesh I/O for FEM (multiple format support) | Phase 2 |

### 10.3 Machine Learning — What Actually Works (and What's Hype)

> **Rule: ML enhances IS 456, never replaces it.** Every ML prediction must be verifiable against code calculations. We never ship a "black box says your beam is safe."

#### ML Applications That Are PROVEN and Valuable

**1. Surrogate Models — Instant Design Prediction (HIGH VALUE)**

**What:** Train a model on 100,000+ design results → predict Ast, status, and cost in microseconds.

**How it works:**
```python
# TRAINING (offline, one-time):
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

# Generate 100,000 beam designs across full IS 456 parameter space
X = []  # [b, d, fck, fy, Mu, Vu, Tu, cover, span]
y = []  # [Ast_required, Asv_required, cost, status]
for _ in range(100_000):
    inputs = random_valid_beam_inputs()
    result = design_beam_is456(**inputs)  # Our library's exact calculation
    X.append(inputs_as_array)
    y.append(results_as_array)

model = GradientBoostingRegressor()
model.fit(X, y)
joblib.dump(model, "beam_surrogate_v1.pkl")

# INFERENCE (real-time, in UI):
model = joblib.load("beam_surrogate_v1.pkl")
prediction = model.predict([[230, 450, 25, 415, 125, 85, 0, 25, 5000]])
# → Ast ≈ 628 mm² (in 0.001 seconds vs 0.05 seconds for full calc)
```

**Use cases:**
- **Real-time design feedback** as engineer types dimensions → UI instantly shows approximate result
- **Parametric studies** — explore 10,000 design combinations in 1 second
- **Design space heatmaps** — visualize how cost changes with width and depth
- **Feasibility screening** — instantly tell if a design is remotely viable before running full calculation

**Important:** The surrogate model is ALWAYS followed by exact IS 456 calculation for the final design. ML is the fast preview, code is the truth.

**Tech stack:** scikit-learn (GBM, Random Forest) or XGBoost. Not deep learning — tabular data works best with tree-based models.

**Accuracy target:** < 2% error vs full IS 456 calculation for 95% of cases.

**2. Smart Design Recommendations (MEDIUM VALUE)**

**What:** Given a design problem, recommend the best starting point based on historical designs.

```python
# Engineer inputs: span=6m, Mu=180 kNm, Vu=120 kN, M25 concrete
# ML model recommends:
{
    "recommended_section": "230 x 500",
    "confidence": 0.92,
    "reasoning": "87% of similar beams (span 5-7m, Mu 150-200) use 230×450 to 250×550",
    "alternatives": [
        {"section": "250 x 450", "cost_savings": "8%", "note": "wider, shallower"},
        {"section": "200 x 550", "cost_savings": "-3%", "note": "narrower, deeper"}
    ]
}
```

**How:** k-NN or Random Forest trained on a curated database of 10,000+ validated designs from textbooks, SP 16/34, and real projects.

**Value:** New engineers often struggle to pick a starting size. This gives them a smart default that's usually close to optimal.

**3. Anomaly Detection in Inputs (MEDIUM VALUE)**

**What:** Catch likely input errors before they become wrong designs.

```python
# Engineer enters: b=2300 mm (probably meant 230)
# ML flags: "⚠️ Beam width 2300 mm is unusual. Did you mean 230 mm?
#            Only 0.3% of beams in our database are wider than 1000 mm."

# Engineer enters: fck=250 (probably meant 25)
# ML flags: "⚠️ Concrete grade 250 N/mm² doesn't exist in IS 456.
#            Did you mean M25 (fck=25)?"
```

**How:** Isolation Forest or simple statistical bounds (mean ± 3σ from training data), plus rule-based constraints.

**Value:** Prevents the #1 real-world engineering error: typos in input data. A beam designed with wrong inputs passes all code checks but is still wrong.

**4. Construction Cost Prediction (MEDIUM VALUE)**

**What:** Predict total construction cost from design parameters, trained on CPWD rate analysis and project databases.

```python
# Input: beam_design_result + region="Maharashtra" + year=2026
# Output:
{
    "concrete_cost": 4500,   # ₹/m³
    "steel_cost": 75,        # ₹/kg
    "formwork_cost": 850,    # ₹/m²
    "labor_cost": 2100,      # ₹/m³ (form + pour + cure)
    "total_per_beam": 18500, # ₹
    "cost_index": 1.12,      # vs national average
    "confidence": "±8%"
}
```

**How:** Gradient boosting trained on CPWD Schedule of Rates + regional multipliers.

**Value:** Currently our CostProfile uses static 2023 CPWD rates. ML makes this dynamic, regional, and predictive.

**5. Design Pattern Library with Similarity Search (HIGH VALUE)**

**What:** A vector database of validated designs that engineers can search by similarity.

```python
# Engineer has: 8m span continuous beam, heavy loads, M30, seismic zone III
# System finds: 47 similar validated designs from textbooks + real projects
# Shows: most common section sizes, rebar patterns, stirrup spacing
# Includes: clause references, verification status, source

results = design_library.search(
    span_m=8, continuity="continuous", load_level="heavy",
    fck=30, seismic_zone=3
)
# Returns ranked list of similar validated designs with source citations
```

**How:** Embeddings from design parameters → FAISS or Annoy for similarity search. Database starts with SP 16, SP 34, textbooks, and grows with user contributions.

**Value:** This is the "Stack Overflow for structural design" — every design has precedent, and engineers can find it instantly.

#### ML Applications That Are HYPE (Don't Build These)

| Idea | Why It's Hype | What To Do Instead |
|------|--------------|-------------------|
| "AI designs buildings" | Can't sign/stamp drawings. Liability issue. | AI *assists* human designer |
| Neural network replaces IS 456 formulas | Unverifiable black box. No clause references. | Keep IS 456 math, use ML for speed/recommendations |
| Generative AI structural drawings | DXF output needs engineering precision, not artistic creativity | Template-based DXF export with exact coordinates |
| LLM reads IS 456 and auto-implements | Hallucination risk in safety-critical code | Human writes code, AI tests it |
| Deep learning for structural analysis | NumPy/SciPy FEM is exact. Why approximate? | Use FEM for analysis, ML for previews |
| Reinforcement learning for design | Design space is well-understood. RL overkill. | Gradient-based or evolutionary optimization |

#### ML Architecture in the Library

```
structural_lib/
├── ml/                          # NEW — machine learning module
│   ├── __init__.py
│   ├── surrogate/
│   │   ├── beam_model.py        # Beam design surrogate (GBM)
│   │   ├── column_model.py      # Column design surrogate
│   │   └── training.py          # Model training utilities
│   ├── recommendations/
│   │   ├── section_recommender.py  # Smart starting dimensions
│   │   └── design_library.py    # Validated design search
│   ├── validation/
│   │   ├── anomaly_detector.py  # Input anomaly detection
│   │   └── sanity_checker.py    # Output sanity validation
│   └── costing/
│       ├── cost_predictor.py    # Regional cost prediction
│       └── data/                # CPWD rates, regional multipliers
│
├── codes/is456/                 # UNCHANGED — pure IS 456 math (the truth)
└── services/api.py              # Orchestrates: ML preview → IS 456 full calc
```

**Dependencies:** `scikit-learn` (required for ML), `xgboost` (optional, better accuracy), `joblib` (model serialization). All are well-maintained, production-grade libraries.

**ML is opt-in:** `pip install structural-lib-is456[ml]`. The core library works without ML models installed.

### 10.4 Optimization — From Single-Element to Whole-Building

#### What We Have (v0.21.6)

| Feature | Implementation | Limitation |
|---------|---------------|------------|
| Cost optimization | `optimize_beam_cost()` | Single beam only |
| Pareto front | Custom NSGA-II | Slow for >3 objectives, beam only |
| Sensitivity analysis | `sensitivity_analysis()` | No gradient info, Monte Carlo only |
| Design comparison | `compare_designs()` | Manual — engineer picks alternatives |
| Constructability scoring | `calculate_constructability_score()` | Heuristic scoring, not optimized |

#### What We Need

**1. Gradient-Based Optimization (for continuous variables)**

Current NSGA-II is population-based (evolutionary) — great for finding Pareto fronts but slow for single-objective optimization. For "find the cheapest beam that passes IS 456", gradient-based methods converge 100x faster.

```python
from scipy.optimize import minimize

def cost_objective(x):
    b, d = x  # continuous section dimensions
    result = design_beam_is456(b_mm=b, d_mm=d, fck=25, fy=415, Mu_kNm=125)
    if result.status != "SAFE":
        return 1e6  # penalty for unsafe design
    return result.cost

# L-BFGS-B with bounds
result = minimize(cost_objective, x0=[250, 450], method='L-BFGS-B',
                  bounds=[(150, 500), (300, 900)])
# Converges in ~20 iterations vs ~500 generations for NSGA-II
```

**When:** Phase 0. SciPy is free.

**2. Discrete Optimization (rebar selection from standard sizes)**

Real engineering: you can't use 17.3mm diameter bars. Standard sizes are 8, 10, 12, 16, 20, 25, 32 mm. This is a **mixed-integer** problem.

```python
# Available bar sizes (IS standard)
standard_bars = [8, 10, 12, 16, 20, 25, 32]  # mm diameter

# Find: minimum steel area using N bars of standard sizes
# Such that: total_Ast >= Ast_required AND spacing >= 25mm AND bars fit in width

from scipy.optimize import milp, LinearConstraint, Bounds

# Mixed-integer linear program:
# minimize: Σ n_i × area_i (total steel)
# subject to: Σ n_i × area_i >= Ast_required
#             Σ n_i × (dia_i + 25) <= b - 2*cover
#             n_i ∈ {0, 1, 2, 3, 4, 5, ...}  (integer)
```

**Why this matters:** Our library currently outputs `Ast_required = 628.3 mm²` and the engineer manually picks bars. That manual step is where optimization waste happens — most engineers pick 4-#16 (804 mm²) when 3-#16+1-#12 (716 mm²) would save 11% steel.

**When:** Phase 0. This is pure algorithm work.

**3. Building-Level Optimization (all members simultaneously)**

Current optimization: each beam is optimized independently. Real optimization: all beams on a floor should be considered together.

```python
# Floor with 20 beams:
# Objective: minimize total cost
# Constraints:
#   - Each beam passes IS 456
#   - Prefer uniform depths (fewer formwork changes)
#   - Rebar sizes limited to 2-3 diameters (reduce inventory)
#   - Total steel weight within budget

def building_cost(section_sizes):
    """section_sizes: [b1, d1, b2, d2, ..., b20, d20]"""
    total_cost = 0
    for i, (b, d) in enumerate(pairs(section_sizes)):
        result = design_beam_is456(b_mm=b, d_mm=d, ...)
        total_cost += result.cost
    # Add uniformity penalty (prefer same depth)
    unique_depths = len(set(d for _, d in pairs(section_sizes)))
    total_cost += 5000 * unique_depths  # penalty per unique depth
    return total_cost
```

**Why this matters:** ETABS has no built-in optimization. If we optimize entire floors automatically, we have a feature ETABS doesn't have.

**When:** Phase 1. Requires batch design to be fast (NumPy vectorization).

**4. Carbon Footprint Optimization (the next frontier)**

```python
# Embodied carbon per material
CO2_FACTORS = {
    "M25_concrete": 0.159,  # tCO₂/m³ (IS 456 concrete, typical India)
    "M30_concrete": 0.178,  # tCO₂/m³
    "Fe415_steel": 1.46,    # tCO₂/tonne (Indian production)
    "Fe500_steel": 1.52,    # tCO₂/tonne
}

# Multi-objective: cost vs carbon
optimize_pareto(
    objectives=["cost_inr", "carbon_tco2"],
    constraints=[is456_compliance, deflection_limit, crack_width_limit],
    variables=[b_range(200, 400), d_range(300, 700), fck_options([25, 30, 35])]
)

# Output: Pareto front showing cost-carbon trade-off
# "For ₹2,500 more per beam, you save 0.8 tonnes CO₂"
```

**Why this matters:** Green building certifications (IGBC, GRIHA, LEED) are becoming mandatory in India. Carbon optimization will be a legal requirement soon.

**When:** Phase 1. The formulas are simple — it's just adding CO₂ factors alongside cost factors.

**5. Reliability-Based Design Optimization (RBDO)**

Instead of deterministic safety factors (γ = 1.5 for concrete, 1.15 for steel), use probabilistic methods:

```python
from structural_lib.reliability import ReliabilityAnalysis

# Define random variables with distributions
ra = ReliabilityAnalysis()
ra.add_variable("fck", dist="lognormal", mean=25, cov=0.15)  # concrete strength
ra.add_variable("fy", dist="normal", mean=415, cov=0.05)      # steel yield
ra.add_variable("Mu", dist="gumbel", mean=125, cov=0.20)      # applied moment
ra.add_variable("b", dist="normal", mean=230, cov=0.02)       # dimensional tolerance
ra.add_variable("d", dist="normal", mean=450, cov=0.02)

# Limit state function: g(x) > 0 means safe
ra.set_limit_state(lambda x: capacity(x) - demand(x))

# Compute reliability index
beta = ra.form()       # First-Order Reliability Method → β ≈ 3.5
pf = ra.failure_prob() # P(failure) ≈ 2.3 × 10⁻⁴

# Compare with IS 456 deterministic:
# IS 456 implicit β ≈ 3.0-3.5 (Table 18 live load factors assume β ≈ 3.0)
```

**Why this matters:** Probabilistic methods are where structural engineering is heading globally. Eurocode already supports semi-probabilistic methods. IS 456's next revision will likely include reliability concepts.

**When:** Phase 3. This is advanced — requires pystra integration and careful calibration against IS 456 safety levels.

#### Optimization Techniques Summary

| Technique | Library | What It Optimizes | When |
|-----------|---------|------------------|------|
| **Gradient-based** (L-BFGS-B, SLSQP) | SciPy | Section dimensions (continuous) | Phase 0 |
| **Mixed-integer** (MILP, branch-and-bound) | SciPy / PuLP | Rebar selection (discrete) | Phase 0 |
| **Evolutionary** (NSGA-II, NSGA-III) | Existing / DEAP | Multi-objective Pareto | Already done |
| **CMA-ES** (Covariance Matrix Adaptation) | DEAP or pycma | High-dimensional continuous | Phase 1 |
| **Bayesian** (Gaussian Process) | scikit-optimize | Expensive-to-evaluate functions | Phase 2 |
| **Topology** (SIMP, BESO) | Custom / JaxSSO | Material distribution | Phase 3 |
| **Reliability** (FORM/SORM, Monte Carlo) | pystra | Safety vs. economy | Phase 3 |

### 10.5 Summary: Technology Upgrade Roadmap

```
PHASE 0 — Library Launch (NOW)
├── Add NumPy/SciPy as core dependency
├── Integrate section-properties (T-beams, L-beams, arbitrary)
├── Add Pint for unit safety
├── Gradient-based optimization (scipy.optimize)
├── Discrete rebar selection (mixed-integer)
└── IfcOpenShell integration (IFC import)

PHASE 1 — Smart Library (Months 3-6)
├── concrete-properties integration (fiber analysis)
├── IS 875 loading code implementation
├── IS 1893 seismic code implementation
├── ML surrogate models (instant beam/column prediction)
├── Smart section recommender
├── Building-level optimization
├── Carbon footprint optimization
├── Shapely for 2D geometry
└── Input anomaly detection

PHASE 2 — Analysis-Ready (Months 6-12)
├── FEM solver (or PyNite integration)
├── Design pattern library with similarity search
├── Bayesian optimization for expensive analyses
├── Regional cost prediction ML model
├── meshio for FEM mesh I/O
└── networkx for topology analysis

PHASE 3 — Research-Grade (Months 12+)
├── Topology optimization (SIMP method)
├── Reliability-based design (pystra)
├── Differentiable FEM (JAX-based, inspired by JaxSSO)
├── Pushover analysis (nonlinear)
└── Performance-based seismic design
```

### 10.6 Key Open-Source Libraries We're Learning From

| Library | Stars | What We Learn | How We Use It |
|---------|-------|---------------|---------------|
| **PyNite** | 687 | Python FEM is viable. Vectorized NumPy assembly. | Reference for our FEM implementation. |
| **section-properties** | 500+ | FEM-based cross-section analysis for any shape. | Direct integration — use as dependency. |
| **concrete-properties** | 250+ | Fiber model for RC sections, by same author as above. | Direct integration — better P-M interaction. |
| **DEAP** | 6.4k | NSGA-II/III, CMA-ES, genetic programming, parallel eval. | Replace our custom NSGA-II with DEAP (better maintained). |
| **IfcOpenShell** | 2.4k | Complete IFC parsing, BIM ecosystem, 243 contributors. | Direct integration — IFC import/export. |
| **COMPAS** | 357 | AEC computation framework (ETH Zurich). CAD interop. | Architecture inspiration, potential mesh/geometry tools. |
| **pystra** | 100+ | Structural reliability (FORM, SORM, Monte Carlo). | Phase 3 integration for probabilistic design. |
| **JaxSSO** | 41 | Differentiable FEM with JAX. Auto-differentiation for optimization. | Research inspiration. Possible Phase 3 integration. |
| **efficalc** | 100+ | Auto-documented engineering calculations. | Inspiration for our calculation report format. |
| **fatpack** | 100+ | Fatigue analysis (rainflow, S-N curves). | Phase 4+ if we expand to steel/bridge design. |

### 10.7 What NOT To Build (Scope Discipline)

| Temptation | Why Not | When (If Ever) |
|-----------|---------|----------------|
| Our own FEM from scratch | PyNite exists, SciPy handles the math. Don't reinvent. | Only if PyNite's license or API is a blocker |
| Our own ML framework | scikit-learn + XGBoost are battle-tested | Never |
| Our own geometry kernel | Shapely + section-properties cover our needs | Never |
| Our own mesher | meshio + Triangle + CGAL wrappers exist | Never |
| Our own CAD format | IFC is the standard, IfcOpenShell handles it | Never |
| Deep learning for design | Tabular data → tree models. Deep learning is overkill. | Only for image-based input (scan drawings) |
| AGI for structural engineering | Focus on tool, not AI hype | Never (seriously) |

**The rule: Build the domain logic (IS 456, IS 875, IS 1893). Use the best existing libraries for everything else.**

---

## 11. Risk Analysis & Mitigation

### 11.1 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| FEM solver accuracy | Medium | Critical | Validate against ETABS/SAP2000 benchmark models |
| Browser performance (large models) | High | High | WASM solver + cloud offloading + LOD rendering |
| Numerical stability (sparse matrices) | Medium | High | Use proven SciPy solvers, condition number checking |
| Shell element convergence | Medium | Medium | Start with MITC4 (locking-free), validate with patches |
| Real-time UI responsiveness | Medium | Medium | Web Workers for FEM, React virtualization for large tables |

### 11.2 Market Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Engineers don't trust open-source | High | High | Publish validation reports, get university endorsements |
| Regulatory bodies require "approved" software | High | High | Partner with BIS, publish validation suite |
| ETABS drops prices | Low | Medium | We're free — can't compete with $0 |
| Better-funded competitor enters | Medium | Medium | Community moat, open-source lock-in advantage |
| AI coding quality degrades | Low | Medium | Human review gates, 5000+ regression tests |

### 11.3 Resource Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Sole developer burnout | High | Critical | AI handles 80% of coding, focus human on decisions |
| AI API costs spike | Medium | Medium | Local model fallback (Ollama), efficient prompt engineering |
| Community doesn't form | Medium | High | Focus on students/academia first, then practitioners |

---

## 12. Success Metrics

### 12.1 Phase 0 Success (Foundation — 3 months)

- [ ] All IS 456 elements designed in tests: beam ✅, column ✅, slab 🟡, footing ✅
- [ ] AI chat interface working for beam design
- [ ] 6,000+ passing tests
- [ ] Load calculator in UI
- [ ] 100+ GitHub stars

### 12.2 Phase 1 Success (Frame Analysis — 9 months)

- [ ] Linear static FEM verified against ETABS on 5 benchmark models
- [ ] Building modeler UI — model a 5-story frame in <15 minutes
- [ ] IS 1893 seismic loading automated
- [ ] Full design pipeline: model → analyze → design → report
- [ ] 500+ GitHub stars
- [ ] 10+ engineers using it for real projects (non-critical)

### 12.3 Phase 2 Success (Shells — 15 months)

- [ ] Shell elements verified on standard patch tests
- [ ] Slab + wall design from FEM results
- [ ] WASM solver running in browser
- [ ] 1,000+ GitHub stars
- [ ] First university adoption for teaching

### 12.4 Phase 3 Success (Multi-Code — 24 months)

- [ ] ACI 318 + EC2 beam/column design
- [ ] Design comparison dashboard
- [ ] 2,000+ GitHub stars
- [ ] Listed in engineering software directories
- [ ] First paid cloud tier generating revenue

### 12.5 Ultimate Success Metric

**An Indian structural engineering student can design a building for their final-year project using BHEEM instead of pirated ETABS.**

---

## 13. Resource & Funding Strategy

### 13.1 Development Team Model

```
Phase 0–1 (Months 0–9):
├── 1 Human (you) — Architecture, decisions, marketing, reviews
├── 16 AI Agents — Coding, testing, documentation, DevOps
└── Cost: $300–600/month

Phase 2 (Months 9–15):
├── 1 Human (you) — Full-time
├── 1-2 Contributors (from community)
├── 16 AI Agents
└── Cost: $500–1000/month

Phase 3+ (Months 15+):
├── 1 Human (you) — Project lead
├── 3-5 Contributors
├── AI Agents
├── Optional: 1-2 paid developers (from funding)
└── Cost: $1000–3000/month (or funded)
```

### 13.2 Revenue Model (Sustainability)

| Tier | Price | Features |
|------|-------|----------|
| **Free (Open Source)** | $0 | Full library, CLI, self-hosted API |
| **BHEEM Cloud (Individual)** | $29/month | Cloud analysis, AI copilot, collaboration |
| **BHEEM Cloud (Team)** | $99/month per seat | Multi-user, project management, Revit sync |
| **BHEEM Enterprise** | Custom | On-premise, SLA, custom codes, training |
| **BHEEM Academic** | Free | Full cloud access for universities |

### 13.3 Funding Opportunities

| Source | Amount | Timeline |
|--------|--------|----------|
| GitHub Sponsors | $100–500/month | Immediate |
| Open-source grants (NLnet, NumFOCUS) | $10K–50K | 3-6 months |
| BIRAC (Indian govt, tech innovation) | ₹25-50 lakhs | 6-12 months |
| AICTE Sponsorship (academic tool) | ₹10-25 lakhs | 6-12 months |
| Y Combinator / RebelFund | $125K–500K | When Phase 1 complete |
| Construction-tech VCs | $500K–2M | When Phase 2 complete |

---

## 14. The Knightly Run — Full ETABS Import & Overnight Optimization

> **The Vision:** An engineer exports their ETABS model at 6 PM. Clicks "Start Knightly Run." Goes home. By 7 AM, the machine has run 50-200 design iterations and found the optimal member sizes for the entire building — safe, cost-efficient, and practical for on-site construction, with every decision traceable to IS 456 clauses.

This is not science fiction. This is an automation loop. And it's the single feature that would make structural engineers switch overnight (literally).

### 14.1 What's Inside a Full ETABS Model (Everything We Need to Import)

An ETABS `.e2k` or `.EDB` model contains the complete definition of a building. Here's the full inventory of what we need to capture — nothing less:

#### Model Geometry

| Data Category | Contents | Import Priority |
|--------------|----------|-----------------|
| **Grid System** | Grid line coordinates (X, Y), story heights, base elevation | P0 — Critical |
| **Stories** | Story names, heights, master/similar stories, splice heights | P0 — Critical |
| **Joint Coordinates** | (X, Y, Z) for every node in the model | P0 — Critical |
| **Frame Elements** | Beams, columns, braces — connectivity (node i → node j), section assignment, insertion point, offsets, end releases, P-Δ flag | P0 — Critical |
| **Shell Elements** | Slabs, walls, ramps — 3/4-node elements, section assignment, thickness, local axes | P1 — Phase 1 |
| **Link Elements** | Springs, isolators, dampers — stiffness matrices | P2 — Phase 2 |
| **Diaphragms** | Rigid/semi-rigid floor assignments per story | P0 — Critical |
| **Constraints** | Body constraints, weld constraints, equal DOF | P1 — Phase 1 |

#### Materials & Sections

| Data Category | Contents | Import Priority |
|--------------|----------|-----------------|
| **Concrete Materials** | fck, Ec, Poisson, weight density, stress-strain model (Mander, IS 456, Eurocode) | P0 — Critical |
| **Steel Materials** | fy, fu, Es, stress-strain model | P0 — Critical |
| **Rebar Materials** | fy, fu, Es for reinforcing bars | P0 — Critical |
| **Frame Sections** | Rectangular, T-beam, circular, I-beam, channel, angle — with dimensions, cover, rebar layout | P0 — Critical |
| **Shell Sections** | Slab thickness, wall thickness, membrane/plate/shell type | P1 — Phase 1 |
| **Section Modifiers** | Cracked section factors (0.35Ig for beams, 0.70Ig for columns per IS 1893) | P0 — Critical |

#### Loading (This Is Where Most Import Tools Stop — We Won't)

| Data Category | Contents | Import Priority |
|--------------|----------|-----------------|
| **Load Patterns** | Dead, Live, SIDL, Wall, EQ-X, EQ-Y, Wind-X, Wind-Y (names + types + self-weight multiplier) | P0 — Critical |
| **Static Loads** | Point loads, UDL, trapezoidal, temperature — on frames and shells | P0 — Critical |
| **Auto Lateral Loads** | IS 1893 seismic parameters (zone, I, R, soil type, damping), response spectrum definition | P0 — Critical |
| **Response Spectrum Cases** | Spectrum function, scale factor, direction (U1, U2, U3), combination method (CQC, SRSS, GMC), modal damping | P1 — High |
| **Time History Cases** | Acceleration records, function definitions, time steps, damping model | P2 — Future |
| **Load Cases** | Linear static, modal, response spectrum, moving load, buckling, P-Δ nonlinear static, pushover, time history — with analysis parameters | P0 — Critical |
| **Load Combinations** | Envelope, linear combination, absolute — IS 456 Table 18 combinations (1.5DL+1.5LL, 1.2DL+1.2LL±1.2EQ, 0.9DL±1.5EQ, etc.) | P0 — Critical |
| **Mass Source** | Which load patterns contribute to mass, mass multipliers | P0 — Critical |

#### Restraints & Supports

| Data Category | Contents | Import Priority |
|--------------|----------|-----------------|
| **Joint Restraints** | Fixed, pinned, roller, spring stiffness per DOF | P0 — Critical |
| **Joint Springs** | Translational and rotational spring constants (for soil springs) | P1 — Phase 1 |
| **End Releases** | Moment releases at beam ends (for pinned connections) | P0 — Critical |

#### Analysis Results (If Available)

| Data Category | Contents | Import Priority |
|--------------|----------|-----------------|
| **Joint Displacements** | Ux, Uy, Uz, Rx, Ry, Rz per load combination | P0 — Critical |
| **Frame Forces** | Axial (P), Shear (V2, V3), Moment (M2, M3), Torsion (T) per station per combination | P0 — Critical |
| **Shell Forces** | F11, F22, F12, M11, M22, M12, V13, V23 per element per combination | P1 — Phase 1 |
| **Reactions** | Support reactions per combination | P0 — Critical |
| **Modal Results** | Periods, frequencies, mode shapes, mass participation ratios, total mass participation | P0 — Critical |
| **Story Results** | Story drifts, story shears, story forces, torsional irregularity ratio | P0 — Critical |

#### Design Data (The Gold Mine)

| Data Category | Contents | Import Priority |
|--------------|----------|-----------------|
| **Design Code** | IS 456:2000, ACI 318-19, BS 8110, EC2 — and version/year | P0 — Critical |
| **Design Preferences** | Min/max rebar ratio, max bar size, cover, crack width limit, deflection limit | P0 — Critical |
| **Design Overwrites** | Per-member overrides (effective length, unbraced length, Cb, Cm) | P1 — Phase 1 |
| **Design Results** | Required Ast, provided Ast, utilization ratio, governing combo, status per member | P0 — Critical |

**Total: ~30 data categories, ~150+ individual data fields.**

### 14.2 The E2K Parser — Our Gateway to Full Import

The `.e2k` format is ETABS's text-based model export. It's keyword-driven and human-readable. Here's what a more complete e2k file looks like in practice:

```
$ PROGRAM INFORMATION
  PROGRAM "ETABS" VERSION "21.2.0"

$ CONTROLS
  UNITS "KN" "M" "C"

$ STORIES - IN SEQUENCE FROM TOP
  STORY "ROOF"  HEIGHT 3.2
  STORY "4F"    HEIGHT 3.2
  STORY "3F"    HEIGHT 3.2
  STORY "2F"    HEIGHT 3.2
  STORY "1F"    HEIGHT 4.2
  STORY "BASE"  HEIGHT 0

$ DIAPHRAGM NAMES
  DIAPHRAGM "D1" TYPE RIGID

$ MATERIAL PROPERTIES
  MATERIAL "M25"  TYPE "CONCRETE"  FE 25000  FU 25  FY 0  WT 24.0
  MATERIAL "M30"  TYPE "CONCRETE"  FE 27386  FU 30  FY 0  WT 24.0
  MATERIAL "Fe415" TYPE "REBAR"    FE 200000 FU 485 FY 415 WT 76.98
  MATERIAL "Fe500" TYPE "REBAR"    FE 200000 FU 545 FY 500 WT 76.98

$ FRAME SECTIONS
  FRAMESECTION "B230x450"  MATERIAL "M25"  SHAPE "Rectangular"  D 0.45  B 0.23
  FRAMESECTION "B230x600"  MATERIAL "M30"  SHAPE "Rectangular"  D 0.60  B 0.23
  FRAMESECTION "C300x300"  MATERIAL "M30"  SHAPE "Rectangular"  D 0.30  B 0.30
  FRAMESECTION "C400x400"  MATERIAL "M30"  SHAPE "Rectangular"  D 0.40  B 0.40
  FRAMESECTION "C450x450"  MATERIAL "M30"  SHAPE "Rectangular"  D 0.45  B 0.45

$ SECTION MODIFIERS  (cracked section per IS 1893)
  FRAMESECTION "B230x450"  I3MOD 0.35  I2MOD 0.35
  FRAMESECTION "C300x300"  I3MOD 0.70  I2MOD 0.70

$ JOINT COORDINATES
  JOINT "1"   0.0    0.0    0.0
  JOINT "2"   5.0    0.0    0.0
  JOINT "3"   10.0   0.0    0.0
  JOINT "4"   0.0    5.0    0.0
  ...

$ CONNECTIVITY - FRAME
  LINE "B1"  "1" "2"  SECTION "B230x450"  ANG 0
  LINE "B2"  "2" "3"  SECTION "B230x600"  ANG 0
  LINE "C1"  "1" "101" SECTION "C400x400"  ANG 0

$ JOINT RESTRAINT
  JOINT "1"  UX UY UZ RX RY RZ    ;Fixed
  JOINT "2"  UX UY UZ             ;Pinned

$ LOAD PATTERNS
  LOADPATTERN "Dead"  TYPE "Dead"  SELFWEIGHT 1.0
  LOADPATTERN "Live"  TYPE "Live"  SELFWEIGHT 0
  LOADPATTERN "SIDL"  TYPE "Super Dead"
  LOADPATTERN "Wall"  TYPE "Super Dead"
  LOADPATTERN "EQX"   TYPE "Seismic"
  LOADPATTERN "EQY"   TYPE "Seismic"

$ AUTO SEISMIC LOAD — IS 1893:2016
  AUTOLOAD "EQX"  TYPE "IS 1893:2016"  DIR "X"  ZONE 3  SOIL "II"
    IMPORTANCE 1.0  RFACTOR 5.0  DAMPING 0.05

$ LOAD ASSIGNMENTS — FRAME
  LINE "B1"  LOADPAT "Dead"  TYPE "UNIF"  DIR "GZ"  FVAL -15.0
  LINE "B1"  LOADPAT "Live"  TYPE "UNIF"  DIR "GZ"  FVAL -12.0
  LINE "B1"  LOADPAT "Wall"  TYPE "UNIF"  DIR "GZ"  FVAL -8.5

$ LOAD COMBINATIONS
  COMBO "1.5DL+1.5LL"       TYPE "Linear Add"
    LOADCASE "Dead"  SF 1.5
    LOADCASE "Live"  SF 1.5
  COMBO "1.2DL+1.2LL+1.2EQX" TYPE "Linear Add"
    LOADCASE "Dead"  SF 1.2
    LOADCASE "Live"  SF 1.2
    LOADCASE "EQX"   SF 1.2
  COMBO "0.9DL+1.5EQX"      TYPE "Linear Add"
    LOADCASE "Dead"  SF 0.9
    LOADCASE "EQX"   SF 1.5
  COMBO "Envelope"           TYPE "Envelope"
    COMBO "1.5DL+1.5LL"      SF 1.0
    COMBO "1.2DL+1.2LL+1.2EQX" SF 1.0
    COMBO "0.9DL+1.5EQX"     SF 1.0

$ RESPONSE SPECTRUM FUNCTION — IS 1893
  FUNCTION "IS1893-2016"  DAMPING 0.05
    PERIOD  0.0   SA/G 1.0
    PERIOD  0.1   SA/G 2.5
    PERIOD  0.55  SA/G 2.5
    PERIOD  4.0   SA/G 0.344
```

**Our E2K parser architecture:**

```python
# structural_lib/importers/e2k/
├── __init__.py
├── parser.py          # Line-by-line keyword parser → raw dict
├── model_builder.py   # Raw dict → StructuralModel object
├── section_mapper.py  # CSI section names → our Section types
├── material_mapper.py # CSI material defs → our Material types
├── load_mapper.py     # CSI load patterns/cases/combos → our Load types
├── seismic_mapper.py  # Auto seismic params → IS 1893 parameters
├── result_reader.py   # Analysis results tables → our Result types
└── validator.py       # Cross-check imported model for completeness
```

**Parsing strategy:**
- Each `$` header starts a new section
- Keywords are positional (keyword-value pairs on each line)
- Support all CSI unit systems (kN-m, kip-ft, N-mm, etc.) → normalize to our units
- Handle section modifiers, end releases, offsets — these are critical for correct analysis
- Preserve ETABS naming (story names, section names) → map to our types but keep originals for traceability

**Effort estimate:** 6-8 weeks for full parser covering 80% of e2k keywords. Remaining 20% (rare features like staged construction, cable elements) can be added incrementally.

### 14.3 The Knightly Run — How Overnight Optimization Works

This is the concept you originally envisioned: **Start a run in the evening, machine iterates all night, morning gives you optimal sizes.** Here's the technical design:

#### The Problem It Solves

Today, a structural engineer's workflow for a G+4 building:

```
Day 1: Assume member sizes → Model in ETABS → Run analysis
Day 2: Check results → Sizes too big (over-designed) or too small (fails)
Day 3: Manually adjust sizes → Re-run analysis → Check again
Day 4: Repeat... some beams now fail because stiffer column attracted more force
Day 5: Final iteration → "Good enough" → Move to design
Day 6-8: Manual IS 456 design checks in Excel
```

**The Knightly Run does Days 1-8 in one overnight run.**

#### The Optimization Loop

```
                    ┌─────────────────────────────────────┐
                    │         THE KNIGHTLY RUN             │
                    │   "Sleep well. Wake up to optimal."  │
                    └─────────────┬───────────────────────┘
                                  │
                    ┌─────────────▼───────────────────┐
                    │  STEP 1: Import ETABS Model      │
                    │  (e2k/CSV/IFC → StructuralModel) │
                    └─────────────┬───────────────────┘
                                  │
                    ┌─────────────▼───────────────────┐
                    │  STEP 2: Analyze                 │
                    │  (FEM or ETABS COM re-run)       │
                    └─────────────┬───────────────────┘
                                  │
                    ┌─────────────▼───────────────────┐
                    │  STEP 3: Design ALL Members      │
                    │  (IS 456 beam + column + footing)│
                    │  Track: Ast, status, utilization │
                    └─────────────┬───────────────────┘
                                  │
                    ┌─────────────▼───────────────────┐
                    │  STEP 4: Grade Each Member       │
                    │  Under-designed? → increase size │
                    │  Over-designed (>40% margin)?    │
                    │  → try smaller size              │
                    │  Just right? → lock it           │
                    └─────────────┬───────────────────┘
                                  │
                    ┌─────────────▼───────────────────┐
                    │  STEP 5: Apply Practical Rules   │
                    │  - Max 3 beam depths per floor   │
                    │  - Standard sizes (multiples of  │
                    │    25mm or 50mm)                  │
                    │  - Rebar from standard diameters  │
                    │  - Column sizes ≥ beam widths     │
                    │  - Construction joint alignment  │
                    └─────────────┬───────────────────┘
                                  │
                    ┌─────────────▼───────────────────┐
                    │  STEP 6: Update Model            │
                    │  Change member sizes in model    │
                    │  (stiffness changes!)            │
                    └─────────────┬───────────────────┘
                                  │
              ┌─────│  CONVERGED?  │─── Yes ──────────┐
              │     │  (sizes stopped changing OR      │ │
              No    │   max iterations reached)        │ │
              │     └──────────────────────────────────┘ │
              │                                          │
              └──── Go to STEP 2 (re-analyze) ◄──────────┘
                                                         │
                    ┌─────────────▼───────────────────┐
                    │  STEP 7: Generate Report         │
                    │  - All iterations logged         │
                    │  - Final vs initial comparison   │
                    │  - Cost savings calculated       │
                    │  - IS 456 compliance status      │
                    │  - Construction practicality     │
                    └─────────────────────────────────┘
```

#### Two Modes of Operation

**Mode A: ETABS-in-the-Loop (Phase 1 — needs ETABS license)**

```python
from structural_lib.knightly import KnightlyRun
from structural_lib.importers.etabs_com import ETABSConnection

# Connect to running ETABS instance
etabs = ETABSConnection.attach()  # COM API, Windows only

run = KnightlyRun(
    model_source=etabs,
    analysis_engine="etabs",       # ETABS does the FEM
    design_engine="bheem",         # We do IS 456 design
    max_iterations=50,
    convergence_tolerance=0.02,    # 2% size change = converged
    practical_rules={
        "max_beam_depths_per_floor": 3,
        "size_increment_mm": 25,
        "prefer_uniform_columns_per_stack": True,
        "max_rebar_diameters": 3,   # e.g., only 12, 16, 20mm
        "min_constructability_score": 70,
    },
    cost_weights={
        "concrete": 7500,    # ₹/m³
        "steel": 75,         # ₹/kg
        "formwork": 850,     # ₹/m²
    }
)

# Start the overnight run
result = run.execute()  # Takes 2-8 hours for a 20-story building

# Morning: review results
print(result.summary)
# Iterations: 23 (converged at iteration 21)
# Total beams: 340, Total columns: 120, Total footings: 40
# Cost savings vs initial: ₹12.3 lakhs (18.7%)
# All members: SAFE per IS 456:2000
# Constructability score: 82/100
```

**How it works under the hood with ETABS:**
1. Read model via COM API (`etabs_api` library: 71 stars, battle-tested)
2. Run analysis → `etabs.analyze.RunAnalysis()`
3. Extract results → `etabs.database.read("Frame Forces - All")`
4. Design in BHEEM (our IS 456 engine)
5. Update sizes → `etabs.prop_frame.SetRectangle("C1", "M30", 0.40, 0.40)`
6. Go to step 2

**Speed:** Each iteration takes 3-10 minutes for a typical building (analysis is the bottleneck). 50 iterations = 2.5-8 hours. Perfect for overnight.

**Mode B: Full BHEEM (Phase 2+ — no ETABS needed)**

```python
run = KnightlyRun(
    model_source="exported_model.e2k",  # or .ifc
    analysis_engine="bheem_fem",        # Our own FEM solver
    design_engine="bheem",
    max_iterations=200,                 # Faster iterations, so more
    convergence_tolerance=0.01,
    # ... same practical rules
)

result = run.execute()  # Takes 30-90 minutes (no ETABS overhead)
```

**Speed:** With our own FEM + NumPy sparse solver, each iteration takes 5-30 seconds. 200 iterations = 15-100 minutes. Runs during a lunch break.

### 14.4 Practical Construction Rules — The Secret Sauce

ETABS optimizes for structural efficiency. Engineers optimize for **buildability.** That's the difference.

A structurally "optimal" building might have:
- 15 different beam depths on one floor (nightmare for formwork)
- Column sizes changing every floor (extra lap splices everywhere)
- 7 different rebar diameters (procurement hell)
- Some beams with 32mm bars at 40mm spacing (can't vibrate concrete)

**The Knightly Run applies real-world construction constraints:**

```python
PRACTICAL_RULES = {
    # FORMWORK EFFICIENCY
    "max_beam_depths_per_floor": 3,        # Max 3 depths: e.g., 450, 500, 600
    "max_beam_widths_per_floor": 2,        # Usually 230 and 300 only
    "prefer_depth_over_width": True,       # Deeper beam = less rebar
    "size_increment_mm": 25,               # Only multiples of 25mm
    "min_beam_depth_mm": 300,              # Below this is impractical

    # COLUMN RATIONALIZATION
    "prefer_uniform_columns_per_stack": True,  # Same size base to top
    "max_column_size_changes": 2,          # At most 2 reductions going up
    "column_reduction_max_percent": 25,    # Don't shrink by >25% at once
    "column_width_gte_beam_width": True,   # Column ≥ beam at every joint

    # REBAR PRACTICALITY
    "max_rebar_diameters": 3,              # e.g., 12, 16, 20 — not 8,10,12,16,20,25,32
    "min_bar_spacing_mm": 30,              # IS 456 Cl 26.3.2 + vibrator access
    "prefer_fewer_larger_bars": True,      # 4-#20 better than 8-#12 (less tying labor)
    "curtailment_step_mm": 500,            # Rebar curtailment at 500mm increments

    # CONSTRUCTION JOINTS
    "align_beam_bottoms_per_floor": True,  # Same soffit level → one formwork height
    "construction_joint_at_mid_span": True,  # Standard practice

    # MATERIAL RATIONALIZATION
    "max_concrete_grades": 2,              # e.g., M25 for beams, M30 for columns
    "max_steel_grades": 1,                 # Fe500 everywhere (India standard now)

    # COST AWARENESS
    "penalize_congested_reinforcement": True,  # >3% steel = hard to pour
    "penalize_heavy_sections": True,       # >700mm deep = difficult to handle
}
```

**Why this matters more than structural optimization:**

| Pure Optimization Says | Construction Reality |
|-----------------------|---------------------|
| Beam B12 should be 230×437mm | No one makes 437mm formwork. Use 450mm. |
| Column C3 should be 287×287mm | Use 300×300. Same formwork as all other columns. |
| Use 6-#14mm + 2-#18mm bars | We don't stock 14mm or 18mm. Use 6-#16mm + 2-#20mm. |
| Reduce column at floor 3 from 450 to 375 | Keep 450 for 3 more floors — splice savings > concrete savings |
| Different concrete grades per element | M30 everywhere. One mix design, one testing regime. |

**The Knightly Run produces a design that a contractor can ACTUALLY BUILD — not just a design that passes IS 456.**

### 14.5 The Output — What Engineers See in the Morning

```
╔══════════════════════════════════════════════════════════╗
║                  KNIGHTLY RUN REPORT                     ║
║                  Building: G+4 Residential               ║
║                  Date: 2026-04-12, Run ID: KR-00047      ║
╠══════════════════════════════════════════════════════════╣

CONVERGENCE
├── Iterations completed:     23 of 50
├── Converged at iteration:   21
├── Final max size change:    0.8% (threshold: 2%)
├── Total analysis runs:      23
├── Total wall-clock time:    4h 12m
├── CPU time (analysis):      3h 48m
├── CPU time (IS 456 design): 24m

MODEL SUMMARY
├── Stories:     5 (G + 4)
├── Beams:       340 (68 per floor)
├── Columns:     120 (24 per floor)
├── Footings:    24
├── Load combos: 13 (IS 456 Table 18 + IS 1893)

OPTIMIZATION RESULTS
├─── BEAMS
│    ├── Initial sizes:    8 different depths (300-700mm)
│    ├── Final sizes:      3 depths only (450, 500, 600mm)
│    ├── Avg utilization:  78% (was 52% — less waste)
│    ├── All passing:      ✅ 340/340
│    └── Steel saved:      2,340 kg (-14%)
│
├─── COLUMNS
│    ├── Initial sizes:    6 different sizes
│    ├── Final sizes:      3 sizes (300×300, 400×400, 450×450)
│    ├── Column stacks:    All uniform base-to-top ✅
│    ├── All passing:      ✅ 120/120
│    └── Concrete saved:   4.2 m³ (-8%)
│
├─── FOOTINGS
│    ├── Resized:          18 of 24
│    ├── All passing:      ✅ (bearing + flexure + shear + punching)
│    └── Concrete saved:   2.1 m³ (-12%)

COST COMPARISON
├── Initial estimate:      ₹65.8 lakhs (structural only)
├── Optimized estimate:    ₹53.5 lakhs
├── SAVINGS:               ₹12.3 lakhs (18.7%)
├── Breakdown:
│   ├── Concrete savings:  ₹4.7 lakhs
│   ├── Steel savings:     ₹6.1 lakhs
│   └── Formwork savings:  ₹1.5 lakhs

CONSTRUCTABILITY SCORE: 82/100
├── Formwork simplicity:   85 (3 beam depths ✅)
├── Rebar practicality:    78 (2 bar diameters ✅, some congestion ⚠️)
├── Column continuity:     90 (uniform stacks ✅)
├── Material rationality:  88 (2 concrete grades, 1 steel grade ✅)
├── Construction joints:   70 (aligned soffits ✅)

WARNINGS
├── ⚠️ Beam B23-2F: Steel ratio 2.8% — close to 3% congestion limit
├── ⚠️ Column C5: Utilization 94% — minimal margin
├── ⚠️ Footing F12: Bearing pressure 95% of allowable — verify SBC

ITERATION HISTORY (sample)
│ Iter │ Beams Δ │ Cols Δ │ Max Util │ Cost (₹L) │ Status │
│    1 │  42 chg │ 18 chg │   1.12   │   65.8    │ 3 FAIL │
│    5 │  28 chg │   8 chg │  0.97   │   58.2    │ 0 FAIL │
│   10 │  12 chg │   3 chg │  0.91   │   55.1    │ 0 FAIL │
│   15 │   5 chg │   1 chg │  0.89   │   54.0    │ 0 FAIL │
│   20 │   2 chg │   0 chg │  0.88   │   53.6    │ 0 FAIL │
│   21 │   0 chg │   0 chg │  0.88   │   53.5    │ CONVG  │

╚══════════════════════════════════════════════════════════╝

Full report: building_G4_knightly_report.html (with 3D visualization)
Design sheets: Per-member IS 456 calculation sheets (PDF, 340 pages)
BBS: Bar bending schedule for all members (Excel + DXF)
```

### 14.6 Why This Changes Everything

#### For Engineers

| Today | With Knightly Run |
|-------|------------------|
| 5-10 days of manual iteration | 1 overnight run |
| "Good enough" sizes (over-designed by 20-40%) | Optimized to 75-85% utilization |
| 3-5 section sizes tried per beam | 50-200 iterations per beam |
| Manual IS 456 checks in Excel | Automated IS 456 with full clause tracing |
| Cost estimated after design | Cost optimized during design |
| Constructability checked by site engineer (too late) | Constructability built into optimization |

#### Cost Impact (Typical Buildings)

| Building Type | Floors | Initial Cost | After Knightly Run | Savings |
|--------------|--------|-------------|-------------------|---------|
| Residential G+4 | 5 | ₹65L | ₹53L | ₹12L (18%) |
| Commercial G+7 | 8 | ₹2.1Cr | ₹1.75Cr | ₹35L (17%) |
| Residential G+14 | 15 | ₹5.8Cr | ₹4.9Cr | ₹90L (15%) |
| High-rise G+25 | 26 | ₹14Cr | ₹12.2Cr | ₹1.8Cr (13%) |

**Note:** Savings decrease for taller buildings because seismic/wind governs more members (less room to optimize). But even 13% on ₹14Cr is ₹1.8 crore in real money.

**For India's construction industry:** India builds ~500,000 buildings/year. If even 1% use Knightly Run and save an average ₹15 lakhs each, that's **₹7,500 crore/year** in national construction savings.

### 14.7 Is This Too Much? Feasibility Assessment

Let's be honest about what's hard and what's not:

| Component | Difficulty | Already Exists? | Timeline |
|-----------|-----------|----------------|----------|
| E2K parser (full model) | Medium | Partial (we have CSV) | 6-8 weeks |
| IS 456 design (all members) | Done ✅ | 104 functions, 5,003 tests | NOW |
| Size optimization logic | Easy | Custom NSGA-II exists, extend it | 2-3 weeks |
| Practical construction rules | Easy | Constructability scorer exists | 2-3 weeks |
| ETABS COM integration | Medium | `etabs_api` package (71 stars) | 4-6 weeks |
| Re-analysis via ETABS COM | Easy | Standard COM API calls | Already in `etabs_api` |
| Our own FEM (for Mode B) | Hard | Not started yet | Phase 2 (6-12 months) |
| Report generation | Easy | HTML/JSON reports exist | 2 weeks |
| BBS + DXF export | Done ✅ | Already in library | NOW |
| Convergence algorithm | Medium | Standard structural engineering | 2-3 weeks |
| Building-level cost estimator | Medium | Per-element exists, need aggregation | 2-3 weeks |

**Total for Mode A (ETABS-in-the-loop):** ~16-20 weeks of AI agent development (= 4-5 months).

**Verdict: This is NOT too much. Not even close.**

The hardest part — IS 456 design engine — is already done. The second hardest part — analysis — is delegated to ETABS. Everything else is data plumbing and iteration logic.

**Mode A is fully achievable by Phase 1 (Month 6).** Mode B (our own FEM) comes in Phase 2.

### 14.8 Implementation Roadmap

```
PHASE 0 — Foundation (NOW, Months 1-3)
├── Build full e2k parser (geometry, materials, sections, loads)
├── Build StructuralModel data class (the universal model object)
├── Extend CSV import to cover columns, load combos, story data
├── Build member-sizing optimizer (single member → try smaller/bigger)
├── Implement ETABS COM connection (via etabs_api package)
└── Design the KnightlyRun orchestrator class

PHASE 1 — Mode A: ETABS-in-the-Loop (Months 3-6)
├── Full optimization loop: import → analyze (ETABS) → design → resize → repeat
├── Practical construction rules engine
├── Convergence detection (sizes stabilized)
├── Building-level cost estimator
├── Multi-floor optimization (uniform columns, limited beam depths)
├── Report generator (HTML + PDF + BBS + DXF)
├── BETA: Test on 5 real buildings from practicing engineers
└── LAUNCH: "Knightly Run v1" — ETABS-assisted overnight optimization

PHASE 2 — Mode B: Full BHEEM (Months 6-12)
├── Replace ETABS analysis with our own FEM solver
├── No ETABS license needed
├── 10-100x faster iterations (seconds vs minutes)
├── Add response spectrum analysis (IS 1893)
├── Add P-Delta effects
├── Cloud version: run on server, results in browser
└── LAUNCH: "Knightly Run v2" — fully independent

PHASE 3 — Intelligence (Months 12+)
├── ML surrogate model for instant pre-screening
├── Multi-objective: cost vs carbon vs constructability
├── Topology suggestions (add/remove members)
├── Learn from previous runs (database of optimized buildings)
├── Auto-report to BIS standards
└── LAUNCH: "Knightly Run v3" — AI-assisted optimization
```

### 14.9 The Bigger Picture — Why "Knightly Run" Is Our Moat

ETABS is an analysis tool. It tells you forces.
SAFE is a design tool. It tells you reinforcement.
Neither of them **optimizes the whole building for construction reality.**

The Knightly Run is not just an optimization. It's a new category:

```
ETABS:        Model → Analyze → ❌ (engineer does the rest manually)
SAFE:         Forces → Design → ❌ (no iteration, no optimization)
Knightly Run: Model → Analyze → Design → Optimize → Iterate → Report
              (fully automatic, overnight, IS 456 compliant)
```

**This is the feature that turns our library from "nice open-source tool" to "essential engineering infrastructure."**

An engineer who has tasted overnight optimization will never go back to manually adjusting sizes in ETABS for 5 days. Just like an engineer who has tasted AutoCAD never went back to a drawing board.

> **"Run it knightly. Wake up rightly."**

---

## 15. Appendix: Current State Assessment

### What We Have (April 2026)

```
Repository: structural_engineering_lib
Version: v0.21.7 (in progress)
Language: Python 3.11+ / TypeScript 5 / React 19
Tests: 5,003 passing, 99% branch coverage
Lines of code: ~50,000+ (Python) + ~15,000+ (TypeScript)
Documentation: 400+ pages
AI Infrastructure: 16 agents, 14 skills, 16 prompts
Quality: Production-grade for element design
```

### Capability Readiness Matrix

| Capability | Readiness | Blockers |
|-----------|-----------|----------|
| IS 456 Beam Design | 100% ✅ | None |
| IS 456 Column Design | 100% ✅ | None |
| IS 456 Footing Design | 90% ✅ | API completion, dowels |
| IS 456 Slab Design | 40% 🟡 | Math for two-way slab |
| 3D Visualization | 95% ✅ | WebGPU upgrade planned |
| CSV/ETABS Import | 100% ✅ | None |
| BBS/DXF/Report Export | 100% ✅ | None |
| AI Design Assistant | 70% 🟡 | Chat UI, tool definitions |
| Frame Analysis (FEM) | 0% ❌ | **Primary gap** |
| Seismic Loading (IS 1893) | 0% ❌ | Depends on FEM |
| Wind Loading (IS 875) | 0% ❌ | Depends on FEM |
| Building Modeler UI | 15% 🟡 | BuildingEditorPage exists |
| Shell Elements | 0% ❌ | Phase 2 |
| Multi-Code (ACI/EC2) | 5% 🟡 | Blueprint ready |
| BIM (IFC) | 0% ❌ | Phase 4 |
| Collaboration | 0% ❌ | Phase 4 |

### The Critical Path

```
Current → IS 456 Slab → AI Chat → FEM Engine → Building Modeler →
Seismic/Wind → Design Pipeline → Multi-Code → Shell → BIM → v2.0
```

The **FEM engine** is gate item #1. Everything after Phase 0 depends on it. This is where the majority of Phase 1 engineering effort goes.

---

## How to Start Tomorrow

### Week 1: New Repo Setup
1. Create `structural-lib` repo on GitHub (MIT license)
2. Set up `src/structural_lib/` layout with pyproject.toml
3. Migrate `core/` — types, materials, sections, validation
4. Migrate `codes/is456/` — all pure math modules (beam, column, footing)
5. Migrate `codes/is13920/` — ductile detailing
6. Run all existing tests in new repo — target: 5,000+ passing

### Week 2: Clean API & Complete Slab
7. Remove 30+ backward-compat stubs — clean imports only
8. Define clean public API in `__init__.py` — no re-export spaghetti
9. Complete IS 456 one-way slab design
10. Start IS 456 two-way slab design (Cl. 24.4, Table 26)

### Week 3-4: FEM Prototype
11. Implement `Node`, `BeamElement2D`, `GlobalAssembly` classes
12. Solve a simple 2-bay portal frame — validate against hand calc
13. Add 3D beam element (12-DOF Timoshenko)
14. Build `Building` convenience class (grids, stories, auto-elements)

### Month 2: Loading & Analysis
15. Implement IS 875 Part 1-2 (dead + live loads)
16. Implement IS 1893:2016 equivalent static method
17. Build auto load combination generator (IS 456 Table 18)
18. Solve a 3-story frame under gravity + seismic
19. Validate against ETABS for 3 benchmark models

### Month 3: Design Pipeline & Publishing
20. Connect FEM results → beam/column/slab design modules
21. Build `design_building()` — one-call full building design
22. Create 10 Jupyter example notebooks
23. Write library documentation (mkdocs)
24. **Publish v1.0-alpha to PyPI**
25. **Share with 5 engineers for feedback**

### Month 4-5: Validation & Trust-Building
26. Run full ETABS comparison benchmarks (5 buildings)
27. Fix issues from engineer feedback
28. Add textbook validation examples (Varghese, Jain)
29. **Publish v1.0 to PyPI**
30. **Start building app repo (Phase 4) on top of stable library**

---

### What Stays in the Old Repo (for now)

The current `structural_engineering_lib` monorepo continues as the app development ground:
- `fastapi_app/` — becomes the BHEEM backend (consumes library via pip)
- `react_app/` — becomes the BHEEM frontend
- `scripts/` — agent/CI tooling (repo-specific)
- `agents/` — AI infrastructure (repo-specific)

Once the library is published, the monorepo's `Python/structural_lib/` is replaced with:
```
pip install structural-lib
```

---

*This document is a living plan. It will be updated as we progress through each phase.*

*Built with AI. For humans. By an engineer who believes structural design software should be free, transparent, and intelligent.*
