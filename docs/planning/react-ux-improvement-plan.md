# React App — UX & Visual Improvement Plan

**Type:** Architecture
**Audience:** All Agents
**Status:** Draft
**Importance:** High
**Created:** 2026-03-25
**Last Updated:** 2026-03-25

---

## The Engineer's Perspective

A structural engineer opens this app. What do they need?

1. **First 10 seconds:** "Can this tool do what I need?" → Clear capabilities, trust signals
2. **First 5 minutes:** "Let me try it" → Quick input, instant result, professional output
3. **Daily use:** "Fast, predictable, no wasted clicks" → Shortcuts, remembered state, batch power
4. **Deliverables:** "Give me something I can hand to my boss" → PDF report, BBS table, DXF drawing

The current app is **technically powerful** but doesn't always communicate that power at a glance. Here's the audit:

---

## Current State Audit

### What's Already Great
| Aspect | Rating | Why |
|--------|--------|-----|
| 3D visualization | ★★★★★ | R3F + Three.js — rebar, stirrups, building frame. Best in class for a web tool |
| Auto-design (WebSocket) | ★★★★★ | <100ms live updates. Engineers LOVE instant feedback |
| AG Grid editor | ★★★★☆ | Professional table — sort, edit, filter, 40+ cols |
| Dark theme | ★★★★☆ | Modern, clean. Correct choice for a CAD-style tool |
| Code splitting | ★★★★☆ | <70KB initial bundle, lazy routes |
| Batch design (SSE) | ★★★★☆ | Live progress, per-beam status |

### What Needs Work
| Issue | Impact | Page(s) |
|-------|--------|---------|
| **Dead-end pages** — no clear "what next?" | Engineers get stuck | DashboardPage, BeamDetailPage |
| **No breadcrumb trail in batch flow** | Lose context after 3 clicks | BatchDesign → Dashboard |
| **ModeSelectPage is a speed bump** | 2-card page with no value for returning users | /start |
| **No persistent quick-actions** | No way to jump Import → Design → Export without TopBar | All pages |
| **Results area is 40% of viewport** | Wastes prime screen space when no result yet | DesignView |
| **No onboarding hints** | New users see empty forms, don't know what to try | DesignView |
| **Export buttons small, hidden** | Engineers want PDF/BBS front-and-center | DesignView |
| **Dashboard has no export** | Engineers can't hand this to anyone | DashboardPage |
| **TopBar settings icon → nothing** | Broken promise | TopBar |
| **No keyboard shortcuts** | Ctrl+D (design), Ctrl+E (export), Ctrl+I (import) | Global |
| **Cross-section view lacks annotations** | Bare SVG — no dimension lines, no bar labels | BeamDetailPage |
| **3D viewport doesn't show loads** | Engineer can't verify what they entered visually | DesignView |

---

## Improvement Plan (3 Phases)

### Phase A: Polish & Flow (No new features — visual only)
*Goal: Make existing features feel professional. Zero new API calls.*

#### A1. Replace ModeSelectPage → Smart Hub
**Current:** 2 cards, minimal info, speed bump for returning users.
**Proposed:** Activity hub that gives context:

```
┌────────────────────────────────────────────────────────────────┐
│ 🏗 StructLib                                            [⚙]  │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──── Quick Actions ──────────┐  ┌──── Recent ──────────────┐│
│  │ [🔧 New Beam Design]       │  │ Project: MedPlaza (154b) ││
│  │ [📁 Import CSV]            │  │ Last: 2 min ago          ││
│  │ [📊 Open Dashboard]        │  │ Pass: 148/154 (96%)      ││
│  │                            │  │ [Resume →]               ││
│  └────────────────────────────┘  └───────────────────────────┘│
│                                                                │
│  ┌──── Capabilities ────────────────────────────────────────┐ │
│  │ ✓ IS 456:2000   ✓ Live 3D    ✓ BBS Export              │ │
│  │ ✓ 40+ CSV cols  ✓ <100ms WS  ✓ DXF + PDF              │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  "Import from ETABS, SAFE, or STAAD → design all in seconds"  │
└────────────────────────────────────────────────────────────────┘
```

**Why:** Returning users skip the mode-select. New users see capabilities. Both get value.

**Implementation:**
- Rename `ModeSelectPage.tsx` → keep as fallback
- Create `HubPage.tsx` (~200 lines)
- Read `useImportedBeamsStore` for recent data
- Store last project name in `localStorage`
- No new API calls

#### A2. Add Contextual Navigation Breadcrumbs
**Current:** TopBar nav links + mobile breadcrumbs.
**Proposed:** Add a **workflow progress bar** on batch flow pages:

```
Import ──●── Editor ──●── Batch Design ──○── Dashboard
                              ↑ you are here
```

Show on: ImportView, BuildingEditorPage, BatchDesignPage, DashboardPage.
Clickable — clicking "Editor" from Dashboard takes you back.

**Implementation:**
- New `WorkflowBreadcrumb.tsx` component (~50 lines)
- Takes `currentStep: 1|2|3|4` prop
- Render below TopBar (h-8, transparent)
- Uses `useNavigate` for click navigation

#### A3. Smart Empty States
**Current:** Empty forms with "Enter parameters to see results" placeholder.
**Proposed:** Each empty state suggests an action:

| Page | Current Empty State | Proposed |
|------|-------------------|----------|
| DesignView (no result) | Calculator icon + gray text | "Try M25, 300×500, Mu=120kN·m" button → auto-fills |
| DashboardPage (no beams) | "Import CSV first" | "Load sample building (154 beams — 2 seconds)" |
| BuildingEditor (no beams) | Redirects to /import | Show sample preview + "Load Sample" CTA |
| BeamDetailPage (no result) | Crashes or shows nothing | Redirect to /design with toast |

**Implementation:**
- `SampleDataCTA` component (~30 lines) — reused across 3 pages
- Calls existing `loadSampleData()` API function
- "Try Example" button on DesignView — `setInputs` with preset values

#### A4. Design View — Dynamic Layout
**Current:** Results panel is always 40% of right side even with no result.
**Proposed:**
- **No result:** Viewport fills 100% of right side
- **Has result:** Viewport 55% + results 45% (animated slide-up)
- **Collapsed:** Result summary bar (1 line: "SAFE 73% | Ast 850mm² | Sv 150mm") — click to expand

```
BEFORE (no result):          AFTER (has result):
┌───┬──────────────┐        ┌───┬──────────────┐
│   │              │        │   │   3D View     │
│ F │   3D View    │        │ F │   (55%)       │
│ o │   (100%)     │   →    │ o ├──────────────┤
│ r │              │        │ r │   Results     │
│ m │              │        │ m │   (45%)       │
└───┴──────────────┘        └───┴──────────────┘
```

**Implementation:**
- Animate `flex-[3]` ↔ `flex-[5.5]` with `transition-all duration-300`
- Collapsed summary bar: `CompactResultsBar` component (~40 lines)
- Click bar → expand; click "minimize" → collapse

#### A5. Export Menu (Unified)
**Current:** ExportPanel shows 3 small buttons at the bottom — easy to miss.
**Proposed:** Add an export dropdown to the DesignView header:

```
[💾 Export ▼]
├─ 📊 Bar Bending Schedule (CSV)
├─ 📐 DXF Drawing
├─ 📄 HTML Report
└─ 📕 PDF Report  ← NEW (TASK-514)
```

- Also add Ctrl+Shift+E shortcut
- Loading state per item (spinner next to text)
- Disable options when no result available

#### A6. Cross-Section Annotations
**Current:** Bare SVG — concrete box + colored circles.
**Proposed:** Add dimension lines and labels:

```
          ←── 300mm ──→
         ┌──────────────┐ ─┬─
         │ ⊗    ⊗   ⊗  │  │
  cover→ │╌╌╌╌╌╌╌╌╌╌╌╌│  │
  40mm   │              │  500mm
         │              │  │
         │ ○    ○    ○  │  │
         └──────────────┘ ─┴─
          3-20φ (942 mm²)
          Sv: 8φ @ 150 c/c
```

Add:
- Width + depth dimension lines (arrow-ended)
- Cover indicator (dashed line)
- Bar count + size label below
- Stirrup spacing text
- Utilization color on bars (green < 80%, yellow < 100%, red > 100%)

**Implementation:**
- Extend `CrossSectionView.tsx` (~60 lines of SVG additions)
- Data already available from design result
- Pure SVG — no new library

---

### Phase B: New Feature Panels (Aligned with TASK-514–519)
*Goal: Integrate v0.21 library features into the React UI.*

#### B1. Load Calculator Panel (TASK-515 React part)

Position: **Left sidebar tab** in DesignView — toggle between "Beam" and "Loads" tabs:

```
[Beam] [Loads]          ← tabs at top of left panel
─────────────
Span: [5000] mm
Support: [Simply Supported ▼]

Loads:
#1 UDL  [15] kN/m  ×
#2 Point [30] kN @ [2500] mm  ×
[+ Add Load]

[Compute]

┌── BMD ──────────────┐
│ /\                  │  ← SVG polyline
│/  \                 │
└─────────────────────┘
┌── SFD ──────────────┐
│─────\               │
│      \──────────────│
└─────────────────────┘

Mu_max = 46.875 kN·m
Vu_max = 37.500 kN

[↗ Use These Values]  ← switches to Beam tab + fills Mu/Vu
```

**Key UX decisions:**
- BMD/SFD as inline SVG — no chart library (keeps bundle small)
- "Use These Values" is the power feature — one click feeds design
- Span value syncs with the Beam tab span
- Tab state persists in component state (not URL)

#### B2. Torsion Toggle (TASK-518 React part)

Position: **Inside "Design Forces" accordion** in DesignView:

```
▼ Design Forces
  Moment (Mu) [120] kN·m
  Shear (Vu)  [75]  kN
  ☐ Include Torsion
    └─ Torsion (Tu) [8.5] kN·m  ← shown when checked
```

When torsion is checked:
- POST to `/api/v1/design/beam/torsion` instead of `/api/v1/design/beam`
- Results panel shows extra row: "Torsion: Ve=XX kN, Me=XX kN·m, Closed stirrups ✓"
- 3D view renders closed stirrup loops (already supported)

#### B3. Alternatives Panel (TASK-519 React part)

Position: **Expandable section** below results in DesignView:

```
▶ See Alternatives (3 Pareto-optimal options)  ← collapsed by default

┌ Design Alternatives ──────────────────────────┐
│ Sort: [Cost ▼] [Utilization] [Steel]          │
│                                                │
│ ● 300×500  3-20φ  78%  ₹1,250/m  ← current  │
│ ○ 250×600  3-18φ  82%  ₹1,180/m  [Apply]     │
│ ○ 350×450  4-18φ  71%  ₹1,320/m  [Apply]     │
│                                                │
│ [Generate More Options]                        │
└────────────────────────────────────────────────┘
```

"Apply" → `updateInputs({ width, depth })` → auto-design triggers → viewport updates live.

#### B4. Dashboard BOQ Section (TASK-517 React part)

Position: **New card** at bottom of DashboardPage:

```
┌── Bill of Quantities ──────────────────────────────┐
│  Steel                              Concrete       │
│  ┌────────────────────┐            ┌─────────────┐│
│  │ Fe500: 4,250 kg    │            │ M25: 12.3m³ ││
│  │ ₹2,55,000          │            │ ₹73,800     ││
│  │                    │            │              ││
│  │ By diameter:       │            │ Gross volume ││
│  │ 8φ: 320 kg        │            │ +5-10% waste ││
│  │ 16φ: 1,890 kg     │            └─────────────┘│
│  │ 20φ: 2,040 kg     │                           │
│  └────────────────────┘                           │
│                                                    │
│  By Story:                                         │
│  GF:  Steel 1,200kg  Concrete 3.8m³  ₹1,08,000   │
│  1F:  Steel 1,050kg  Concrete 3.1m³  ₹94,500     │
│  2F:  Steel 2,000kg  Concrete 5.4m³  ₹1,52,400   │
│                                                    │
│  Grand Total: 4,250 kg + 12.3 m³ = ₹3,28,800     │
│                                                    │
│  [📥 Export BOQ as CSV]  [📕 Download PDF]         │
└────────────────────────────────────────────────────┘
```

---

### Phase C: Professional Polish (Advanced)
*Goal: Make it look and feel like a ₹50 lakh/year commercial engineering tool.*

#### C1. Keyboard Shortcuts
| Shortcut | Action | Where |
|----------|--------|-------|
| `Ctrl+D` | Trigger design | DesignView |
| `Ctrl+Shift+E` | Open export menu | DesignView, BeamDetailPage |
| `Ctrl+I` | Navigate to import | Global |
| `Ctrl+K` | Open command palette | Global |
| `Ctrl+/` | Toggle sidebar | BuildingEditorPage |
| `Escape` | Close expanded panels | Global |

**Implementation:** Global `useKeyboardShortcuts()` hook (~40 lines).

#### C2. Micro-Animations That Add Professionalism
| Element | Animation | Effect |
|---------|-----------|--------|
| Result cards appearing | `framer-motion` staggered fade-in | Results feel "calculated" |
| Utilization bar | Count-up from 0% to actual | Draws attention to key metric |
| Status badge (SAFE/FAIL) | Scale spring with colored glow | Immediate read |
| 3D viewport load | Fade in + slight camera dolly | Smooth transition |
| Export download | Button shrinks → checkmark | Confirms action |
| Tab switches | Slide left/right with spring | Smooth, tactile |

#### C3. Design Input Presets
Quick presets for common beam types. Dropdown at top of BeamForm:

```
Preset: [Custom ▼]
├── Plinth beam (230×300, M20, 2m span)
├── Floor beam (300×500, M25, 5m span)
├── Lintel beam (230×230, M20, 1.5m span)
├── Transfer beam (400×800, M30, 8m span)
└── Custom
```

One click fills all fields. Engineers iterate much faster.

#### C4. Onboarding Tooltip Tour
First-time user sees 5 tooltips (one at a time):
1. "Enter beam dimensions here" → points to form
2. "Auto-design updates the 3D view live" → points to toggle
3. "Click for full detail view" → points to viewport
4. "Export your results" → points to export menu
5. "Try the Load Calculator" → points to Loads tab

Store `onboarding_completed` in localStorage. Show "Show Tips" in settings to replay.

#### C5. TopBar Context Indicators
Show active project context in TopBar:

```
[Logo] Design | Import | Batch | Editor | Dashboard    [M25 Fe500] [154 beams] [96% pass] [⚙]
```

The `[M25 Fe500]` chip shows active material.
`[154 beams]` shows import count.
`[96% pass]` shows latest batch result.

All are clickable — material opens material modal, beam count opens import, pass rate opens dashboard.

#### C6. Professional Print/PDF Styles
When Ctrl+P or "Print" on BeamDetailPage:
- Hide TopBar, sidebar, buttons
- Show clean report layout with:
  - Header: "StructLib — IS 456:2000 Beam Design Report"
  - Cross-section SVG (full page width)
  - Results table (properly formatted)
  - Clause references
  - Footer: "Generated by StructLib v3.0 on [date]"

Use Tailwind's `print:` modifier — zero new CSS files.

---

## Visual Design System Improvements

### Color Palette Refinement
Current palette is good but needs more hierarchy signals:

| Token | Current | Proposed | Purpose |
|-------|---------|----------|---------|
| Surface 0 | `zinc-950` (#09090b) | Same | App background |
| Surface 1 | `zinc-900` | `zinc-900/60` | Card background (more transparent) |
| Surface 2 | `white/[0.03]` | `white/[0.04]` | Elevated elements (slightly more visible) |
| Border | `white/8` (`#ffffff14`) | `white/6` (`#ffffff0f`) | Subtler borders |
| Text primary | `white` | Same | Headings, values |
| Text secondary | `white/70` | `white/60` | Labels, descriptions |
| Text tertiary | `white/40` | `white/35` | Helper text, hints |
| Text muted | `white/20` | `white/15` | Disabled, version strings |
| Accent | `blue-500 / blue-600` | Same | Primary actions |
| Success | `green-500` | `emerald-400` | Warmer green, easier to read |
| Warning | `yellow-500` | `amber-400` | Warmer amber |
| Danger | `red-500` | `rose-400` | Softer red, less alarming |

### Typography Scale
Currently using ad-hoc sizes (`text-xs`, `text-[10px]`, `text-sm`). Propose a strict scale:

| Role | Size | Weight | Class |
|------|------|--------|-------|
| Page title | 18px | Bold | `text-lg font-bold` |
| Section title | 12px | Semibold + uppercase | `text-xs font-semibold uppercase tracking-wider` |
| Input label | 11px | Regular | `text-[11px] text-white/50` |
| Value | 13px | Medium | `text-[13px] font-medium` |
| Large metric | 24px | Bold | `text-2xl font-bold` |
| Caption | 10px | Regular | `text-[10px] text-white/30` |

### Spacing Consistency
Standardize card padding and gap:

| Element | Inner padding | Gap between |
|---------|--------------|-------------|
| Card (small) | `p-3` (12px) | `gap-2` (8px) |
| Card (medium) | `p-4` (16px) | `gap-3` (12px) |
| Section | `py-4 px-3` | `space-y-3` (12px) |
| Page wrapper | `px-6 py-6` | `space-y-6` (24px) |

---

## Implementation Priority

| Priority | Change | Phase | Effort | Impact |
|----------|--------|-------|--------|--------|
| 1 | A4: Dynamic results layout | A | 2h | High — fixes wasted viewport space |
| 2 | A6: Cross-section annotations | A | 3h | High — makes output professional |
| 3 | A5: Unified export menu | A | 2h | High — engineers need this front-and-center |
| 4 | A3: Smart empty states | A | 2h | Medium — onboards new users |
| 5 | B1: Load calculator panel | B | 1-2d | High — new feature (TASK-515) |
| 6 | A1: Smart Hub page | A | 4h | Medium — returning user experience |
| 7 | B2: Torsion toggle | B | 3h | Medium — new feature (TASK-518) |
| 8 | B3: Alternatives panel | B | 1d | Medium — new feature (TASK-519) |
| 9 | A2: Workflow breadcrumbs | A | 1h | Medium — batch flow clarity |
| 10 | B4: Dashboard BOQ | B | 1d | High — new feature (TASK-517) |
| 11 | C1: Keyboard shortcuts | C | 3h | Medium — power user experience |
| 12 | C2: Micro-animations | C | 4h | Low-Medium — polish |
| 13 | C3: Design presets | C | 2h | Medium — speed for beginners |
| 14 | C5: TopBar context | C | 2h | Low — nice to have |
| 15 | C4: Onboarding tour | C | 4h | Low — first-time only |

**Total Phase A:** ~2-3 days (visual polish, no new API)
**Total Phase B:** Included in TASK-514–519 effort
**Total Phase C:** ~2-3 days (advanced polish)

---

## Engineer Workflow Scenarios

### Scenario 1: Quick Check (2 minutes)
```
Hub → "New Beam" → fill W/D/span/Mu/Vu → auto-design → read SAFE 73% → export PDF → done
```
**Pain points removed:** No mode-select speed bump, export is in header not bottom, PDF available.

### Scenario 2: Client Revision (5 minutes)
```
Hub → "Resume MedPlaza" → Editor → change beam B23 depth 500→600 → auto-redesign →
see utilization drop 92%→71% → "See Alternatives" → apply cheaper option → export BBS
```
**New:** Alternatives panel saves trial-and-error. Resume from Hub saves re-import.

### Scenario 3: Full Project (30 minutes)
```
Hub → Import CSV → Editor → review 154 beams → Rationalize (23→4 sections) →
Batch Design → Dashboard → BOQ (total ₹3.28L) → Export PDF summary → done
```
**New:** Rationalization, BOQ with costs, PDF summary — complete deliverable.

### Scenario 4: Load Uncertainty (10 minutes)
```
Hub → "New Beam" → Loads tab → add UDL 15kN/m + Point 30kN → Compute BMD/SFD →
"Use These Values" → auto-design → add torsion Tu=8.5kN·m → re-design →
"See Alternatives" → pick cheapest safe option → export report
```
**New:** Load calculator, torsion, alternatives — all in one flow without page navigation.

---

## Files Created / Modified

### Phase A (new files)
| File | Lines | Purpose |
|------|-------|---------|
| `components/pages/HubPage.tsx` | ~200 | Smart hub replacing ModeSelectPage |
| `components/ui/WorkflowBreadcrumb.tsx` | ~50 | Batch flow progress indicator |
| `components/ui/SampleDataCTA.tsx` | ~30 | Reusable "try sample" button |
| `hooks/useKeyboardShortcuts.ts` | ~40 | Global keyboard shortcuts |

### Phase A (modified files)
| File | Change |
|------|--------|
| `App.tsx` | Add `/hub` route (or replace `/start`) |
| `DesignView.tsx` | Dynamic layout, export dropdown, empty state |
| `BeamDetailPage.tsx` | Better empty handling, print styles |
| `CrossSectionView.tsx` | Add dimension lines + bar labels |
| `DashboardPage.tsx` | Add export button, better empty CTA |
| `TopBar.tsx` | Context indicators (material, beam count) |

### Phase B (new files — from TASK plan)
| File | Lines | Task |
|------|-------|------|
| `components/design/LoadCalculatorPanel.tsx` | ~150 | TASK-515 |
| `components/design/AlternativesPanel.tsx` | ~120 | TASK-519 |
| `components/design/ProjectBOQPanel.tsx` | ~100 | TASK-517 |
| `hooks/useLoadAnalysis.ts` | ~50 | TASK-515 |
| `hooks/useTorsionDesign.ts` | ~50 | TASK-518 |
| `hooks/useParetoDesign.ts` | ~50 | TASK-519 |
| `hooks/useProjectBOQ.ts` | ~50 | TASK-517 |
