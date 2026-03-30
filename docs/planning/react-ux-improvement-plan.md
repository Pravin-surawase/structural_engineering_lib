---
owner: Main Agent
status: active
last_updated: 2026-03-30
doc_type: guide
complexity: intermediate
tags: []
---

# React App — UX & Visual Improvement Plan

**Type:** Architecture
**Audience:** All Agents
**Status:** Active
**Importance:** High
**Created:** 2026-03-25
**Last Updated:** 2026-03-25 (Session 98 — A1–A6 implemented, bugs fixed)

---

## The Design Philosophy

> "A structural engineer shouldn't have to fill in a form to see their own building."

The primary workflow is **import-first**: bring in a real project (CSV / ETABS / SAFE), see all beams in 3D, select any beam, see its reinforcement live. Manual input is a secondary tool for quick single-beam checks — it should not appear in the batch workflow at all.

The app should feel like a **structural workstation** — dense, contextual, and precise. Not a form wizard. The 3D view is the anchor; everything else serves it.

---

## Core Principle: The Editor is the Center

```
WRONG mental model:       RIGHT mental model:
  Form → design → 3D        Import → 3D Editor → select beam → see reinforcement
  (form-first)              (data-first, visual-first)
```

Manual beam input belongs **only** in `/design` (single-beam check). Everywhere else — Editor, Dashboard, Batch — the engineer works with their actual imported project data, navigated through the 3D view and the AG Grid.

---

## Current State — Navigation Flowchart

```
┌────────────────────────────────────────────────────────────────┐
│  CURRENT UI FLOW                                               │
└────────────────────────────────────────────────────────────────┘

   Browser opens
        │
        ▼
   ┌──────────┐      "Start Engineering" CTA
   │ HomePage │ ────────────────────────────►  /start
   │  (/)     │                                   │
   │  3D hero │                                   ▼
   └──────────┘                         ┌─────────────────┐
                                        │ ModeSelectPage  │ ← speed bump
                                        │ 2 cards         │
                                        └────────┬────────┘
                                                 │
                          ┌──────────────────────┼─────────────────────┐
                          │                       │                     │
                          ▼                       ▼              (if beams loaded)
                  ┌──────────────┐      ┌──────────────┐        Editor / Batch
                  │  DesignView  │      │  ImportView  │
                  │  (/design)   │      │  (/import)   │
                  │              │      │  drag-drop   │
                  │  340px FORM  │      └──────┬───────┘
                  │  60% 3D      │             │
                  │  40% results │             ▼
                  └──────┬───────┘    ┌──────────────────┐
                         │            │ BuildingEditorPage│
                  [Full 3D] button    │  (/editor)        │
                         │            │                   │
                         ▼            │  ┌─────────────┐  │
                  ┌──────────────┐    │  │ 3D building │  │
                  │ BeamDetail   │    │  │ (top 30%)   │  │
                  │ (/design/    │    │  ├─────────────┤  │
                  │  results)    │    │  │ AG Grid     │  │
                  │ separate page│    │  │ (bottom 70%)│  │
                  └──────────────┘    │  └─────────────┘  │
                                      │                   │
                                      │  ← click beam →   │
                                      │  nothing happens  │ ← WASTED OPPORTUNITY
                                      └──────────────────┘
                                               │
                                               ▼
                                      ┌──────────────────┐
                                      │  BatchDesignPage │
                                      └──────────────────┘
                                               │
                                               ▼
                                      ┌──────────────────┐
                                      │  DashboardPage   │
                                      │  plain cards     │ ← no export
                                      └──────────────────┘

PROBLEMS:
  ✓ Manual form appears redundantly outside single-beam design  ← FIXED (form only in /design)
  ✓ BeamDetailPage is a separate route  ← FIXED (detail is inline in Editor via BeamDetailPanel)
  ✓ Clicking a beam in the Editor does NOT show its reinforcement ← FIXED (BeamDetailPanel slides in)
  ✓ 3D building view is only 30% of Editor  ← IMPROVED (wider split when panel active)
  ✓ DashboardPage has no export  ← FIXED (export buttons in BentoGrid header)
  × TopBar Settings → dead link  ← TODO
  ✓ FloatingDock.tsx, BentoGrid.tsx — ACTIVATED
  × CommandPalette.tsx — still unused
```

---

## Future State — Navigation Flowchart

```
┌────────────────────────────────────────────────────────────────┐
│  FUTURE UI FLOW                                                │
└────────────────────────────────────────────────────────────────┘

   Browser opens
        │
        ▼
   ┌──────────┐
   │ HomePage │ ─────────────────────────────► /start
   │  (/)     │                                   │
   └──────────┘                                   ▼
                                       ┌─────────────────────┐
                                       │  HubPage (/start)   │
                                       │                     │
                                       │  [New Design]       │  ← replaces ModeSelect
                                       │  [Import CSV]       │
                                       │  [Resume project →] │  ← from localStorage
                                       │  Capabilities bar   │
                                       └──────┬──────────────┘
                                              │
                      ┌───────────────────────┼──────────────────────┐
                      │                       │                      │
                      ▼                       ▼                      ▼
             ┌──────────────┐       ┌──────────────┐        ┌──────────────┐
             │  DesignView  │       │  ImportView  │        │  Dashboard   │
             │  (/design)   │       │  (/import)   │        │  (resume)    │
             │              │       │              │        └──────────────┘
             │  ONLY place  │       │  drag-drop   │
             │  with manual │       │  CSV / ETABS │
             │  beam form   │       └──────┬───────┘
             │              │              │
             │  Dynamic:    │    Workflow Breadcrumb:
             │  no result = │    Import ●── Editor ○── Batch ○── Dashboard
             │  3D 100%     │              │
             │  has result= │              ▼
             │  3D 55%+     │    ┌──────────────────────────────────────────┐
             │  results 45% │    │  BuildingEditorPage (/editor)  ← THE HUB│
             │              │    │                                          │
             │  [Export ▼]  │    │  ┌── 3D building (left, ~50%) ──────┐   │
             │  in header   │    │  │  Full 3D building frame          │   │
             │              │    │  │  Floors, selections, highlights  │   │
             └──────────────┘    │  └─────────────────────┬────────────┘   │
                                 │                         │                │
                                 │  AG Grid (bottom half)  │                │
                                 │  click beam ────────────┘                │
                                 │           │                               │
                                 │           ▼                               │
                                 │  ┌── Beam Detail Panel (right, ~40%) ─┐  │
                                 │  │ SLIDES IN when beam selected        │  │
                                 │  │                                     │  │
                                 │  │  ┌─ 3D Reinforcement View ───────┐  │  │
                                 │  │  │ Full rebar + stirrups of      │  │  │
                                 │  │  │ selected beam only            │  │  │
                                 │  │  │ (same Viewport3D component)   │  │  │
                                 │  │  └───────────────────────────────┘  │  │
                                 │  │                                     │  │
                                 │  │  ✓ SAFE  73%  Ast 850mm² Sv 150c/c │  │
                                 │  │  [████████░░] utilization bar       │  │
                                 │  │                                     │  │
                                 │  │  Cross-section SVG (annotated)      │  │
                                 │  │                                     │  │
                                 │  │  IS 456 clause checks ▼             │  │
                                 │  │  Rebar suggestions ▼                │  │
                                 │  │                                     │  │
                                 │  │  [📐 DXF]  [📊 BBS]  [📄 Report]   │  │
                                 │  └─────────────────────────────────────┘  │
                                 └──────────────────────────────────────────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │ BatchDesignPage  │
                                    │ SSE progress     │
                                    │ per-beam status  │
                                    └────────┬─────────┘
                                             │
                                             ▼
                                    ┌─────────────────────────────────────┐
                                    │ DashboardPage                       │
                                    │                                     │
                                    │ BentoGrid layout (already built!)   │
                                    │ Pass rate · Utilization · BOQ       │
                                    │ [Export PDF]  [Export BOQ CSV]      │
                                    │ in header — not buried at bottom    │
                                    └─────────────────────────────────────┘

GLOBAL (all pages except /):
┌──────────────────────────────────────────────────────────────────────────────────┐
│ TopBar: StructLib  Design | Import | Batch | Editor | Dashboard   [M25] [154b] ⚙ │
└──────────────────────────────────────────────────────────────────────────────────┘

FloatingDock (already built) — activate on all pages except /:
         ┌─────────────────────────────────────────┐
         │  [🏠] [🔧] [📁] [🏗] [⚡] [📊]        │  ← bottom-center, macOS magnify
         └─────────────────────────────────────────┘
```

---

## The Central Feature: Beam Selection → Split Detail Panel

This is the single highest-impact change. When an engineer clicks any beam — in the 3D building OR in the AG Grid — the Editor splits to show:

```
BEFORE (clicking a beam does nothing meaningful):
┌────────────────────────────────────┐
│  3D Building (top 30%)             │
├────────────────────────────────────┤
│                                    │
│  AG Grid — all beams               │
│  click row → row highlights        │
│  (that's it)                       │
│                                    │
└────────────────────────────────────┘


AFTER (clicking any beam):
┌──────────────────────────┬─────────────────────────────────────────┐
│                          │  B-204 · Floor 2                   [×]  │
│  3D Building (left 55%)  ├─────────────────────────────────────────┤
│                          │                                         │
│  Selected beam glows     │  ┌─ 3D Reinforcement ────────────────┐  │
│  blue in the building    │  │                                   │  │
│                          │  │  Full rebar + stirrup 3D model    │  │
│  Floor isolation still   │  │  Rotate / zoom freely             │  │
│  works — other beams     │  │  Same Viewport3D, single beam     │  │
│  fade to 20% opacity     │  │  mode                             │  │
│                          │  └───────────────────────────────────┘  │
├──────────────────────────┤                                         │
│                          │  ✓ SAFE   Ast 850mm²   Sv 8φ@150c/c    │
│  AG Grid (bottom)        │  [████████░░] 73% utilized              │
│  selected row = active   │                                         │
│                          │  Cross-section (annotated SVG)          │
│  Can keep editing cells  │  ←300mm→                                │
│  in grid while panel     │  ┌─────────┐ ─┬─                       │
│  is open → live update   │  │ ⊗  ⊗  ⊗ │  │                       │
│  in 3D reinforcement     │  │         │ 500mm                     │
│                          │  │ ○  ○  ○ │  │                       │
│                          │  └─────────┘ ─┴─                       │
│                          │  3-20φ (942mm²)  Sv: 8φ@150c/c         │
│                          │                                         │
│                          │  IS 456 clause checks (collapsible)     │
│                          │  Rebar suggestions (collapsible)        │
│                          │                                         │
│                          │  [📐 DXF]  [📊 BBS]  [📄 Report]       │
└──────────────────────────┴─────────────────────────────────────────┘

  Editing a cell in the AG Grid (e.g. depth 500→600):
  → auto-triggers re-design for that beam
  → 3D reinforcement updates live (WebSocket or REST)
  → results panel updates
  → row color in grid updates (pass/fail/utilization)
  → building 3D model updates that beam's rendered height
  All without leaving the page.
```

---

## What Each Component Does in the New Model

| Component | Role | Manual form? |
|-----------|------|-------------|
| `DesignView` | Single-beam quick check & exploration | ✓ Yes — this is its only job |
| `BuildingEditorPage` | Primary workstation for real projects | ✗ No form — data comes from import |
| `BeamDetailPage` | **Retired or repurposed** — detail is now inline in Editor | ✗ Removed from batch flow |
| `DashboardPage` | Post-batch analytics + BOQ + export | ✗ No form |
| `ImportView` | Entry point for project data | ✗ No beam form |
| `BatchDesignPage` | SSE progress view | ✗ No form |

The BeamDetailPage (`/design/results`) can be kept as a standalone deep-link (for sharing a specific beam result), but it should no longer be a required step in any workflow.

---

## Bugs Found & Fixed (Session 98)

| Bug | Root Cause | Fix | Commit |
|-----|-----------|-----|--------|
| **3D shows 3 top bars, 2D shows 2** | CrossSectionView used `Math.min(2, ceil(numBars * 0.3))` while 3D API uses `select_bar_arrangement(0.25 * Ast)` — different formulas | Added `ascRequired` prop to CrossSectionView; now computes `ceil(ascRequired / barArea)` | `a5612b0` |
| **Utilization shows wrong %** | BuildingEditorPage computed `ast_required / (0.04 * b * D)` (steel ratio) instead of `Mu / Mu_cap` (moment utilization) | Added `utilization_ratio` to backend `BatchDesignResult`; frontend uses API value | `a5612b0` |
| **Stirrup max 275 not 300** | **Not a bug** — IS 456 Cl 26.5.1.5: `max_sv = min(0.75d, 300mm)`. For d≈367mm: 0.75×367=275mm governs | Added annotation showing which limit governs: "Sv = X mm (max: 0.75d = Y mm)" | `a5612b0` |
| **asc_required not passed to CrossSectionView** | BeamDetailPanel stored value but never forwarded as prop | Added `ascRequired={beam.asc_required}` prop pass-through | `a5612b0` |

### Key IS 456 Reference
- **Stirrup spacing limit (Cl 26.5.1.5):** `max_sv = min(0.75d, 300mm)` — for beams with d < 400mm, 0.75d governs (not 300)
- **Compression steel default:** When `asc = 0`, detailing uses `0.25 × Ast` as minimum compression reinforcement
- **Standard stirrup spacings:** `[75, 100, 125, 150, 175, 200, 225, 250, 275, 300]` — `round_to_practical_spacing()` rounds down

---

## Improvement Plan (3 Phases)

### Phase A: Polish & Core Flow Fixes

---

#### A1. BuildingEditorPage — Beam Selection Detail Panel ✅ DONE

**IMPLEMENTED in commit `a5612b0`.** When a beam is clicked (row in AG Grid or mesh in 3D), a BeamDetailPanel slides in from the right.

**Layout change:**
- Existing: 3D top 30% + Grid bottom 70%
- New when beam selected: 3D left 55% + Grid bottom-left 55% + Detail panel right 45%
- Panel slides in with `transition-all duration-300`
- Close button (×) returns to normal layout
- Panel has its own scroll

**Detail panel sections (top to bottom):**
1. Beam ID + floor label header
2. `Viewport3D` in single-beam mode (rebar + stirrups, rotateable, ~220px tall)
3. Compact result bar: `✓ SAFE  73%  850mm²  150c/c`
4. Animated utilization bar (count-up)
5. `CrossSectionView` with annotations (see A4)
6. IS 456 code checks (collapsible, `useCodeChecks`)
7. Rebar suggestions (collapsible, `useRebarSuggestions`)
8. Export row: `[DXF]` `[BBS]` `[Report]`

**Live edit loop:**
- User changes a cell in AG Grid (e.g. depth 500 → 600)
- `useAutoDesign` triggers for that beam
- Result and 3D reinforcement in the panel update live
- Row color in grid updates
- 3D building model updates that beam's height

**Implementation:**
- New `components/design/BeamDetailPanel.tsx` (~200 lines)
- Embed `Viewport3D` in single-beam mode (already supports this)
- `useBeamGeometry(selectedBeam)` + `useCodeChecks(selectedBeam)` + `useRebarSuggestions`
- Pass `onClose`, `beam`, `result` as props

---

#### A2. DesignView — Dynamic Layout (viewport expands when empty) ✅ DONE

**IMPLEMENTED in commit `a242878`.** Results panel now collapses/expands dynamically.

**3 states:**
```
EMPTY (just opened):        HAS RESULT:              MINIMIZED:
┌──────┬─────────────┐     ┌──────┬────┬────────┐   ┌──────┬────────────────┐
│      │             │     │      │ 3D │        │   │      │                │
│ Form │  3D (100%)  │     │ Form │55% │Results │   │ Form │  3D (100%)     │
│      │             │     │      │    │  45%   │   │      │                │
│      │  [Try M25   │     │      │    │        │   ├──────┴────────────────┤
│      │   300×500 →]│     │      │    │        │   │ ✓ SAFE 73% 850mm² [▲]│
└──────┴─────────────┘     └──────┴────┴────────┘   └────────────────────── ┘
```

- Animate `flex-[3] ↔ flex-[5.5]` with `transition-all duration-300`
- Empty state: show preset button "Try: 300×500 M25 Mu=120 kN·m →" that auto-fills and designs
- Minimized: `CompactResultsBar` single-line (`✓ SAFE  73%  Ast 850mm²  Sv 150c/c`)

---

#### A3. Replace ModeSelectPage → Smart Hub

**Current:** 2 mode cards. Returning users click through it every session — pure friction.

```
┌───────────────────────────────────────────────────────────────────┐
│  StructLib                                                 [⚙]   │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─── Quick Actions ──────────────┐  ┌─── Last Session ────────┐ │
│  │  [🔧  New Beam Design    →]    │  │  MedPlaza · 154 beams   │ │
│  │  [📁  Import CSV / ETABS →]    │  │  96% pass · 2 min ago   │ │
│  │  [📊  Open Dashboard     →]    │  │  [Resume Project →]     │ │
│  └────────────────────────────────┘  └─────────────────────────┘ │
│                                                                   │
│  ✓ IS 456:2000   ✓ Live 3D   ✓ BBS / DXF   ✓ ETABS / SAFE      │
└───────────────────────────────────────────────────────────────────┘
```

- Create `HubPage.tsx` (~150 lines)
- Read `useImportedBeamsStore` for last project context
- `localStorage` for project name + last pass rate
- No new API calls

---

#### A4. Cross-Section Annotations ✅ DONE

**IMPLEMENTED in commits `a242878` + `a5612b0`.** CrossSectionView now accepts `ascRequired`, `barDia`, `barCount`, `utilization` props.

**Proposed (extend `CrossSectionView.tsx`):**
```
          ←── 300mm ──→
         ┌──────────────┐ ─┬─
         │  ⊗    ⊗    ⊗ │  │
cover ──►│╌╌╌╌╌╌╌╌╌╌╌╌╌│  │
  40mm   │              │ 500mm
         │              │  │
         │  ○    ○    ○ │  │
         └──────────────┘ ─┴─
          3-20φ  (942 mm²)
          Sv: 8φ @ 150 c/c
          Utilization: 73% [████████░░]

Bar color: emerald-400 < 75%  |  amber-400 75–90%  |  rose-400 > 90%
```

Adds: width/depth dimension lines (SVG arrows), cover dashed line, bar label, stirrup label, utilization color. Pure SVG, ~60 lines. Used in both BeamDetailPanel and BeamDetailPage.

---

#### A5. Activate FloatingDock (already built, unused) ✅ DONE

**IMPLEMENTED in commit `a242878`.** FloatingDock is now mounted in App.tsx on all routes except `/`.

Wire it to App.tsx (~10 lines):
- Show on all routes except `/`
- Replace or supplement TopBar on mobile
- Badge: imported beam count, last pass rate
- Active state on current route

```
         ┌──────────────────────────────────────────────┐
         │  [🏠] [🔧 Design] [📁 Import] [🏗 Editor] [📊]│
         └──────────────────────────────────────────────┘
                    bottom-center, spring magnify on hover
```

---

#### A6. Activate BentoGrid for Dashboard (already built, unused) ✅ DONE

**IMPLEMENTED in commit `a242878`.** DashboardPage rewritten with BentoGrid + BentoCard layout. Export buttons (BBS, Report) moved to page header.

```
╔══════════════════╦═══════════════════╦══════════════════════╗
║ PASS RATE 96%    ║ AVG UTIL 73%      ║  PASS / FAIL         ║
║ 148 / 154 beams  ║ [████████░░]      ║  148 ██████████████  ║
╠══════════════════╩═══════════════════╣   6  ██             ║
║ CRITICAL BEAMS                       ╠══════════════════════╣
║ B-204  Floor 2  94%  ████████████    ║  STEEL    CONCRETE   ║
║ B-112  Floor 1  91%  █████████████   ║  4,250kg   12.3m³   ║
╠═══════════════╦══════════════════════╣  ₹2,55,000  ₹73,800 ║
║ BY STORY      ║  [📊 Export BBS]     ╚══════════════════════╝
║ GF  52 beams  ║  [📐 Export DXF]
║ 1F  48 beams  ║  [📄 Export PDF]
║ 2F  54 beams  ║
╚═══════════════╩══════════════════════╝
```

Export buttons move from buried at the bottom to a visible BentoCard at the top-right.

---

#### A7. Workflow Breadcrumb (batch flow only)

Shown below TopBar on the 4-step batch flow. Clickable.

```
Import ──●── Editor ──●── Batch Design ──○── Dashboard
                           ↑ you are here
```

New `WorkflowBreadcrumb.tsx` (~60 lines). Added to ImportView, BuildingEditorPage, BatchDesignPage, DashboardPage.

---

#### A8. TopBar — Context Badges + Fix Settings

**Context badges (right side, when data exists):**
```
StructLib  Design | Import | Batch | Editor | Dashboard   [M25 Fe500] [154b] [96%✓] [⚙]
```

**Fix settings:** TopBar settings button currently navigates to `/settings` (dead). Replace with a slide-over `SettingsPanel` (~60 lines):
- API endpoint field
- Theme + version info
- No new routes needed

---

### Phase B: New Feature Panels (TASK-514–521)

---

#### B1. Load Calculator — `[Loads]` tab in DesignView (TASK-515)

Second tab in DesignView left panel. Compute Mu/Vu from span + loads, then "Use These Values" fills the Beam tab.

```
[Beam] [Loads]
────────────────
Span: [5000] mm
Support: [Simply Supported ▼]

#1 UDL   [15] kN/m       ×
#2 Point [30]kN @[2500]mm ×
[+ Add Load]

[Compute]

 BMD: /\   SVG polyline (inline, no chart lib)
     /  \
SFD: ─────\

Mu_max = 46.9 kN·m
Vu_max = 37.5 kN

[↗ Use These Values]
```

---

#### B2. Torsion Toggle in DesignView (TASK-518)

Inside "Design Forces" accordion, below Vu:
```
▼ Design Forces
  Mu [120] kN·m
  Vu  [75] kN
  ☐ Include Torsion
    └─ Tu [8.5] kN·m
```

When checked → POST to `/api/v1/design/beam/torsion`. Results show equivalent forces. 3D renders closed stirrups (already supported).

---

#### B3. Alternatives Panel in DesignView (TASK-519)

Collapsible section below results:
```
▶ Alternatives (3 Pareto-optimal options)

● 300×500  3-20φ  78%  ₹1,250/m  ← current
○ 250×600  3-18φ  82%  ₹1,180/m  [Apply]
○ 350×450  4-18φ  71%  ₹1,320/m  [Apply]

Sort: [Cost ▼]  [Util]  [Steel]
```

"Apply" → `updateInputs()` → auto-design → live 3D update.

---

#### B4. Dashboard BOQ Card (TASK-517)

Full-width BentoCard at bottom:
```
┌─ Bill of Quantities ────────────────────────────────────────┐
│  Fe500: 4,250 kg  ₹2,55,000    M25: 12.3 m³  ₹73,800       │
│  By story: GF ████  1F ████  2F ████████████                │
│  Grand Total: ₹3,28,800                                     │
│  [📥 Export BOQ CSV]   [📕 Download PDF Summary]           │
└─────────────────────────────────────────────────────────────┘
```

---

### Phase C: Micro-Polish

---

#### C1. Micro-Animations (Framer Motion — already installed)

| Element | Animation |
|---------|-----------|
| BeamDetailPanel slide-in | `x: 400 → 0`, spring, 300ms |
| Result cards appear | Staggered fade-in (0, 50, 100ms) |
| Utilization bar | Count-up 0 → actual % |
| SAFE/FAIL badge | Scale spring + colored glow |
| Accordion expand | `height: 0 → auto` |
| Export download | Button → spinner → checkmark |

---

#### C2. Design Input Presets

Dropdown at top of BeamForm (single-beam only):
```
Preset: [Custom ▼]
├── Plinth beam (230×300, M20, Mu=15)
├── Floor beam  (300×500, M25, Mu=120)
├── Transfer    (400×800, M30, Mu=450)
└── Custom
```

One click → fills all fields → auto-design triggers. Helps first-time users and repetitive check scenarios.

---

#### C3. Print Styles for BeamDetailPage

`Ctrl+P` on BeamDetailPage hides nav/buttons, formats clean report:
- Header: `StructLib — IS 456:2000 Beam Design Report`
- Full-width annotated cross-section SVG
- Results table + IS 456 clause refs
- Footer: version + date

Tailwind `print:` modifier. No new CSS files.

---

#### C4. Settings Panel (fixes broken TopBar button)

Slide-over panel (~60 lines). Shows:
- API endpoint (editable, saves to localStorage)
- App version
- About / credits

No new routes. No new API calls.

---

## Visual System

### Colors (refined)
| Role | Tailwind | Notes |
|------|---------|-------|
| Util low (< 75%) | `emerald-400` | Warmer green than green-500 |
| Util mid (75–90%) | `amber-400` | More readable than yellow-500 |
| Util high (> 90%) | `rose-400` | Less alarming than red-500 |
| Util over (> 100%) | `red-500 font-bold` | FAIL — intentionally alarming |
| Card border | `white/6` | Subtler than current white/8 |
| Text secondary | `white/60` | Slightly lower than current white/70 |

### Spacing Standard
| Element | Padding | Gap |
|---------|---------|-----|
| Compact card | `p-3` | `gap-2` |
| Standard card | `p-4` | `gap-3` |
| Page wrapper | `px-6 py-6` | `space-y-6` |

---

## Implementation Priority

| # | Change | Effort | Impact | Risk | Status |
|---|--------|--------|--------|------|--------|
| 1 | **A1: BeamDetailPanel in Editor** | 3–4h | ★★★★★ highest impact | Low | ✅ DONE |
| 2 | **A5: Activate FloatingDock** — 10 lines | 30min | ★★★★ wow, free | None | ✅ DONE |
| 3 | **A6: Activate BentoGrid on Dashboard** | 2h | ★★★★ visual upgrade | Low | ✅ DONE |
| 4 | **A2: DesignView dynamic layout** | 2h | ★★★★ fixes viewport waste | Low | ✅ DONE |
| 5 | **A4: Cross-section annotations** | 3h | ★★★★ looks like real drawings | Low | ✅ DONE |
| 6 | **A7: Export dropdown in DesignView** | 1h | ★★★ engineers need this | None | ✅ DONE |
| 7 | **A8: TopBar badges + fix settings** | 2h | ★★★ professional context | Low | 📋 TODO |
| 8 | **A3: Smart Hub page** | 3h | ★★★ returning user UX | Low | 📋 TODO |
| 9 | **A9: Workflow breadcrumb** | 1h | ★★ batch flow clarity | None | 📋 TODO |
| 10 | **B1: Load calculator** | 1–2d | ★★★★ TASK-515 feature | Med | 📋 TODO |
| 11 | **B2: Torsion toggle** | 3h | ★★★ TASK-518 | Med | 📋 TODO |
| 12 | **B3: Alternatives panel** | 1d | ★★★ TASK-519 | Med | 📋 TODO |
| 13 | **B4: Dashboard BOQ** | 1d | ★★★ TASK-517 | Med | 📋 TODO |
| 14 | **C1: Micro-animations** | 3h | ★★ polish | Low | 📋 TODO |
| 15 | **C2: Design presets** | 1h | ★★ first-time UX | None | 📋 TODO |
| 16 | **C3: Print styles** | 2h | ★★★ professional output | None | 📋 TODO |
| 17 | **C4: Settings panel** | 1h | ★ fixes broken button | None | 📋 TODO |

**Quick wins (already built, just wire up):** FloatingDock + BentoGrid = ~2.5h total, major visual upgrade.

---

## Files Created / Modified

### Phase A — New Files
| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `components/design/BeamDetailPanel.tsx` | Slide-in panel: 3D rebar + results + redesign + edit rebar + export | ~495 | ✅ DONE |
| `components/pages/HubPage.tsx` | Smart hub replacing ModeSelectPage | ~150 | 📋 TODO |
| `components/ui/WorkflowBreadcrumb.tsx` | Batch flow step indicator | ~60 | 📋 TODO |
| `components/ui/CompactResultsBar.tsx` | Single-line result summary bar | ~50 | ✅ DONE (inline in DesignView) |
| `components/ui/ExportDropdown.tsx` | Unified export dropdown | ~60 | ✅ DONE (inline in DesignView) |
| `components/ui/SettingsPanel.tsx` | Slide-over settings panel | ~60 | 📋 TODO |

### Phase A — Modified Files
| File | Change | Status |
|------|--------|--------|
| `BuildingEditorPage.tsx` | Add BeamDetailPanel, split layout on beam select, removed old ChecksSidebar | ✅ DONE |
| `App.tsx` | Mount FloatingDock (AppDock component) | ✅ DONE |
| `DashboardPage.tsx` | BentoGrid layout, export in header | ✅ DONE |
| `DesignView.tsx` | Dynamic layout, export dropdown, preset, empty state, CompactResultsBar | ✅ DONE |
| `CrossSectionView.tsx` | `ascRequired`, `barDia`, `barCount`, `utilization` props, color coding | ✅ DONE |
| `Viewport3D.tsx` | Added `overrideDimensions` prop for non-store beams | ✅ DONE |
| `fastapi_app/routers/imports.py` | Added `utilization_ratio` to `BatchDesignResult` | ✅ DONE |
| `TopBar.tsx` | Context badges, fix settings to SettingsPanel | 📋 TODO |

### Phase B — New Files (from TASK plan)
| File | Task |
|------|------|
| `components/design/LoadCalculatorPanel.tsx` | TASK-515 |
| `components/design/AlternativesPanel.tsx` | TASK-519 |
| `components/design/ProjectBOQPanel.tsx` | TASK-517 |
| `hooks/useLoadAnalysis.ts` | TASK-515 |
| `hooks/useTorsionDesign.ts` | TASK-518 |
| `hooks/useParetoDesign.ts` | TASK-519 |
| `hooks/useProjectBOQ.ts` | TASK-517 |
