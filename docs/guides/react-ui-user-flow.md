# React App User Flow Guide

**Type:** Guide
**Audience:** All Agents, Developers, Users
**Status:** Production Ready
**Importance:** High
**Created:** 2026-01-27
**Last Updated:** 2026-01-27
**Related Tasks:** TASK-V3-REACT-UI, TASK-V3-PHASE4

---

## Executive Summary

This document is the **single source of truth** for React app UX flows, consolidating research from:
- [STREAMLIT-RESEARCH-009-USER-JOURNEY.md](../../streamlit_app/docs/research/STREAMLIT-RESEARCH-009-USER-JOURNEY.md) (1,081 lines)
- [v3-streamlit-parity-library-evolution-plan.md](../planning/v3-streamlit-parity-library-evolution-plan.md)
- [8-week-development-plan.md](../planning/8-week-development-plan.md)

The React app (`react_app/`) provides a modern workspace UI with 3D visualization, data grid editing, and intelligent design assistance for structural engineers.

---

## App Structure Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    ModernAppLayout                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ LandingView │  │ ImportView  │  │ DesignView  │         │
│  │   (home)    │→ │  (import)   │→ │  (design)   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                           ↓                 │
│         ┌─────────────────────────────────────┐             │
│         │          ResultsView                │             │
│         │   ┌──────────┐ ┌──────────────┐     │             │
│         │   │Viewport3D│ │  BeamTable   │     │             │
│         │   │  (3D)    │ │  (grid)      │     │             │
│         │   └──────────┘ └──────────────┘     │             │
│         └─────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

**Key Components:**
| Component | Path | Purpose |
|-----------|------|---------|
| `ModernAppLayout` | `layout/ModernAppLayout.tsx` | Root layout, view routing |
| `LandingView` | `LandingView.tsx` | Welcome screen, quick actions |
| `ImportView` | `ImportView.tsx` | CSV/Excel import, sample data |
| `DesignView` | `DesignView.tsx` | Single beam design + settings |
| `Viewport3D` | `Viewport3D.tsx` | 3D beam/building visualization |
| `BeamTable` | `BeamTable.tsx` | Data grid for batch editing |
| `ResultsView` | (inline) | 3D + table combined view |

---

## User Flows by Persona

### 🎓 Flow A: First-Time User (Learning)

**Persona:** Junior engineer, learning IS 456 beam design

**Goal:** Design a simple beam, understand the tool

#### Flow Steps

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Landing Page                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   🏠 StructEng Workspace                                   │
│                                                             │
│   [ 📐 Design Beam ]  [ 📥 Import Data ]  [ ⚙️ Settings ] │
│                                                             │
│   Recent Projects: (empty for first-time user)              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Click "Design Beam"
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Design View                                         │
├─────────────────────────────────────────────────────────────┤
│ ←Back     Live Design Status: ● Connected                   │
│                                                             │
│ ┌─────────────────┐ ┌───────────────────────────────────┐  │
│ │  Input Form     │ │  3D Preview                       │  │
│ │                 │ │                                   │  │
│ │ Width: [300]mm  │ │  ┌─────────────────┐             │  │
│ │ Depth: [450]mm  │ │  │   Beam mesh     │             │  │
│ │ Span:  [5000]mm │ │  │   with rebar    │             │  │
│ │                 │ │  │   (real-time)   │             │  │
│ │ Moment:[100]kNm │ │  └─────────────────┘             │  │
│ │ Shear: [50]kN   │ │                                   │  │
│ │                 │ │  Rotation: drag to orbit          │  │
│ │ fck:   [25]MPa  │ │  Scroll: zoom in/out              │  │
│ │ fy:    [500]MPa │ │                                   │  │
│ └─────────────────┘ └───────────────────────────────────┘  │
│                                                             │
│ ┌───────────────────────────────────────────────────────┐  │
│ │ Results Panel                                         │  │
│ │                                                       │  │
│ │ ✅ Design OK | Ast: 804mm² | 4-16φ bars | Util: 72%  │  │
│ │                                                       │  │
│ │ [ Code Checks ]  [ Rebar Options ]  [ Export ]        │  │
│ └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

#### Key Interactions

| Action | Result | Latency |
|--------|--------|---------|
| Type in any input field | 3D preview + results update | <100ms debounce, <200ms API |
| Change width/depth | Beam mesh resizes, rebar repositions | <150ms |
| Click "Code Checks" tab | Shows IS 456 clause status (✅/❌) | Cached, instant |
| Click any ❌ check | Expands with explanation + fix suggestion | Instant |
| Click "Rebar Options" | Shows 3-5 optimal configurations | 200ms API call |
| Click "Apply" on suggestion | Updates design + 3D preview | <100ms |

#### Error Handling

| Error | Display | Recovery |
|-------|---------|----------|
| Invalid input (e.g., depth < 100mm) | Red border + inline message | Fix value |
| API unavailable | "⚠️ Offline mode" banner | Local validation only |
| Design fails (moment too high) | Red "❌ Design Failed" | Increase depth suggestion |

---

### 🔧 Flow B: Production Engineer (Batch Import)

**Persona:** Mid-level engineer, designing 50+ beams for a project

**Goal:** Import ETABS/SAFE export, batch design, export results

#### Flow Steps

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Landing → Import                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Click [ 📥 Import Data ]                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Import View                                         │
├─────────────────────────────────────────────────────────────┤
│ ←Back     Import Beams                                      │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │  📁 Drag & Drop CSV or Excel                           ││
│ │                                                         ││
│ │  Supported: ETABS, SAFE, STAAD, Generic CSV            ││
│ │  Format auto-detected                                   ││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ OR                                                          │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │  📊 Load Sample Building (154 beams from ETABS)        ││
│ │  [ Load Sample ]                                        ││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ Material Overrides (applied to all beams)               ││
│ │ fck: [25] MPa   fy: [500] MPa   Cover: [40] mm         ││
│ └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Drop files or click "Load Sample"
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Import Progress + Warnings                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ✅ Imported 154 beams from ETABS format                  │
│                                                             │
│   ⚠️ Warnings (3)                                          │
│   ┌───────────────────────────────────────────────────────┐│
│   │ • B12: Missing Mu_mid, using max(Mu_start, Mu_end)   ││
│   │ • B45: Shear value unusually high (350kN), verify    ││
│   │ • B89: Span converted from m to mm (auto)             ││
│   └───────────────────────────────────────────────────────┘│
│                                                             │
│   [ Continue to Results → ]                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Click "Continue to Results"
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Results View (3D + Table)                           │
├─────────────────────────────────────────────────────────────┤
│ ←Back     154 Beams Imported     [ Run Batch Design ]       │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ 3D Building View                                        ││
│ │                                                         ││
│ │    ┌────┐ ┌────┐ ┌────┐   (Beams as wireframe          ││
│ │    │    │ │    │ │    │    Color = story or status)     ││
│ │    └────┴─┴────┴─┴────┘                                 ││
│ │                                                         ││
│ │ Click beam → highlights in table                        ││
│ │ Drag → orbit, Scroll → zoom                             ││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ BeamTable (editable data grid)                          ││
│ │─────────────────────────────────────────────────────────││
│ │ ID   │ Story │ Width │ Depth │ Mu    │ Status │ Ast    ││
│ │──────┼───────┼───────┼───────┼───────┼────────┼────────││
│ │ B1   │ GF    │ 300   │ 450   │ 125   │ ● OK   │ 804    ││
│ │ B2   │ GF    │ 300   │ 500   │ 180   │ ● OK   │ 1206   ││
│ │ B3   │ 1F    │ 250   │ 400   │ 95    │ ● OK   │ 603    ││
│ │ B4   │ 1F    │ 300   │ 450   │ 200   │ ● FAIL │ —      ││
│ │ ...  │       │       │       │       │        │        ││
│ └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

#### Batch Design Flow

```
Click [ Run Batch Design ]
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Batch Design Progress (SSE streaming)               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Designing 154 beams...                                    │
│                                                             │
│   ████████████████░░░░░░░░░░░░░░ 67/154 (43%)              │
│                                                             │
│   ✅ 65 OK  ❌ 2 Failed  ⏳ 87 Pending                       │
│                                                             │
│   Last: B67 → 4-16φ, 804mm², 0.8s                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
          │
          │ ~30-60 seconds for 154 beams
          ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 6: Results Complete                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ✅ Batch Design Complete                                  │
│                                                             │
│   Summary: 150 OK, 4 Failed (97% success)                   │
│                                                             │
│   3D view now shows:                                        │
│   • Green = OK                                              │
│   • Red = Failed (click to see issue)                       │
│   • Blue = Selected                                         │
│                                                             │
│   Actions:                                                  │
│   [ Export All (CSV) ]  [ Export DXF ]  [ View Failed ]     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Key Interactions

| Action | Result | Latency |
|--------|--------|---------|
| Drop CSV file | Auto-detect format, parse, show beam count | <500ms |
| Load sample data | 154 beams from `/api/sample-beams` | <1s |
| Click "Run Batch Design" | SSE stream starts, progress bar updates | 200-500ms/beam |
| Click beam in 3D | Table scrolls to row, highlights | Instant |
| Click row in table | 3D camera zooms to beam | <200ms |
| Edit cell in table | Live re-design, 3D updates | <300ms debounce |
| Click "Export All" | Downloads CSV with all results | <1s |

---

### 👔 Flow C: Senior Engineer (Validation)

**Persona:** Team lead, reviewing and approving designs

**Goal:** Verify IS 456 compliance, identify issues, generate reports

#### Flow Steps

```
After batch import and design (Flow B), click on a failed beam:

┌─────────────────────────────────────────────────────────────┐
│ Step 1: Click Failed Beam B4                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ 3D View: B4 highlighted, camera zooms in               ││
│ │                                                         ││
│ │    ┌────────────────────┐                              ││
│ │    │ B4 (red outline)   │                              ││
│ │    │ with cross-section │                              ││
│ │    └────────────────────┘                              ││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ Inspector Panel (right side)                            ││
│ │─────────────────────────────────────────────────────────││
│ │ B4 — 1F — FAILED                                       ││
│ │                                                         ││
│ │ Geometry: 300 × 450 × 5000 mm                          ││
│ │ Forces: Mu=200 kNm, Vu=80 kN                           ││
│ │                                                         ││
│ │ ❌ Issue: Moment capacity exceeded                      ││
│ │    Mu_lim = 175 kNm < Mu_applied = 200 kNm             ││
│ │                                                         ││
│ │ 💡 Suggestions:                                         ││
│ │    • Increase depth to 500mm → Mu_lim = 210 kNm        ││
│ │    • Change to doubly reinforced                        ││
│ │    • Increase width to 350mm                            ││
│ │                                                         ││
│ │ [ Apply Suggestion 1 ]                                  ││
│ └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

#### Code Checks Panel

```
┌─────────────────────────────────────────────────────────────┐
│ Code Checks (Beam B1)                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Overall: 6/6 Passed ✅                                      │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐│
│ │ Clause    │ Check              │ Value   │ Limit │ ✓/✗ ││
│ │───────────┼────────────────────┼─────────┼───────┼─────││
│ │ 26.5.1.1  │ Min bar count      │ 4       │ ≥2    │ ✅  ││
│ │ 26.3.2    │ Clear spacing      │ 48mm    │ ≥25mm │ ✅  ││
│ │ 26.5.1.1a │ Min steel ratio    │ 0.34%   │ ≥0.17%│ ✅  ││
│ │ 26.5.1.1b │ Max steel ratio    │ 0.34%   │ ≤4%   │ ✅  ││
│ │ 23.2.1    │ Depth/span ratio   │ 9%      │ ≥5%   │ ✅  ││
│ │ 26.4.1    │ Minimum cover      │ 40mm    │ ≥25mm │ ✅  ││
│ └─────────────────────────────────────────────────────────┘│
│                                                             │
│ Click any row for detailed calculation                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Practical Scenarios

### Scenario 1: Small Residential Project (5 beams)

**User:** Junior engineer at a small consulting firm
**Time available:** 30 minutes
**Equipment:** Laptop, no dual monitors

**Optimal Flow:**
1. Open app → Click "Design Beam"
2. Design beam 1 manually (2 min)
3. Note: fck=25, fy=500, cover=40 (same for all)
4. Design beams 2-5, changing only span/moment/shear (4×2 min = 8 min)
5. Export each to DXF (5×30s = 2.5 min)
6. Total: ~15 minutes

**Pain Points to Address:**
- Session state should persist (don't re-enter materials each time)
- "Copy from previous" button would save 6 min
- Batch export would save 2 min

### Scenario 2: Large Commercial Project (200 beams)

**User:** Mid-level engineer at a structural design firm
**Time available:** 2 hours
**Equipment:** Desktop, ETABS model available

**Optimal Flow:**
1. Export from ETABS to CSV (5 min, outside app)
2. Open app → Import View → Drop CSV (30s)
3. Set material overrides: fck=30, fy=500, cover=40 (30s)
4. Click "Continue" → See 200 beams in table (instant)
5. Click "Run Batch Design" → Wait for SSE stream (2-3 min)
6. Review failures (10 beams) → Fix via suggestions (10 min)
7. Click "Export All" → CSV + DXF zip (1 min)
8. Total: ~20 minutes for 200 beams

**Pain Points to Address:**
- Very large CSV (1000+ beams) might need chunked upload
- Failed beam editing should be inline, not need separate form
- Bulk apply suggestions ("Apply to all similar failures")

### Scenario 3: Design Review Meeting (30 min, 50 beams)

**User:** Senior engineer, team lead
**Time available:** 30 minutes during meeting
**Equipment:** Conference room display, projector

**Optimal Flow:**
1. Load previously saved session (2s)
2. Show 3D building view → Explain structure to team (5 min)
3. Filter to "Failed" beams → 4 beams shown (30s)
4. Click each failed beam → Show issue + suggestion (4×2 min = 8 min)
5. Apply approved changes live (2 min)
6. Show compliance summary → All green (2 min)
7. Export report → PDF with compliance certificate (1 min)
8. Total: ~20 minutes

**Pain Points to Address:**
- "Presentation mode" with larger fonts
- Quick filter buttons: "Show All", "Show Failed", "Show Selected"
- PDF export with professional header/footer

---

## Size & Responsiveness Considerations

### Viewport Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Desktop XL | ≥1920px | 3-column: Sidebar + 3D + Inspector |
| Desktop | 1280-1919px | 2-column: 3D (60%) + Table/Inspector (40%) |
| Laptop | 1024-1279px | Stacked: 3D above, Table below |
| Tablet | 768-1023px | Single column, tabs for 3D/Table |
| Mobile | <768px | Not recommended, show "Desktop required" |

### 3D View Sizing

| Context | Recommended Size | Notes |
|---------|------------------|-------|
| Single beam design | 400×400px min | Needs room for rotation |
| Building view (50 beams) | 600×400px min | More zoom headroom |
| Building view (200+ beams) | 800×600px min | Performance considerations |

### Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Initial load | <2s | ~3s (chunking needed) |
| 3D frame rate | ≥30 FPS | 45-60 FPS for <100 beams |
| Input response | <100ms | ~50ms with debounce |
| Batch design | <500ms/beam | ~300ms/beam |
| Memory (200 beams) | <500MB | ~350MB |

---

## Common Issues & Solutions

### Issue 1: 3D View Not Loading

**Symptoms:** Black screen, "Loading 3D viewport..." spinner forever
**Causes:**
- WebGL not supported
- GPU driver issue
- Browser extension blocking

**Solution:**
1. Check browser console for WebGL errors
2. Try Chrome/Firefox (Safari has WebGL issues)
3. Disable hardware acceleration extensions
4. Fallback: Show 2D cross-section instead

### Issue 2: CSV Import Fails

**Symptoms:** "No beams imported" or 0 beam count
**Causes:**
- Wrong column names
- Missing required columns (beam_id, width, depth)
- Encoding issues (UTF-16 vs UTF-8)

**Solution:**
1. Check warnings panel for specific column issues
2. Download sample CSV template
3. Ensure columns are: beam_id, story, b, D, span, Mu, Vu
4. Save as UTF-8 CSV

### Issue 3: Batch Design Slow

**Symptoms:** Progress bar stuck, >1s per beam
**Causes:**
- Server overloaded
- Network latency
- Complex beams (high reinforcement)

**Solution:**
1. Check network tab for request times
2. Reduce batch size (import in chunks of 50)
3. Check server health: `/api/v1/health`

### Issue 4: Results Don't Match Hand Calculation

**Symptoms:** Ast differs from Excel calculation
**Causes:**
- Different design method (singly vs doubly reinforced)
- Rounding differences
- Different IS 456 interpretation

**Solution:**
1. Click "Show Calculations" to see step-by-step
2. Verify input units (mm vs m, kNm vs Nm)
3. Check if compression steel is included
4. Report discrepancy with sample data

---

## Related Documentation

- [Streamlit User Journey Research](../../streamlit_app/docs/research/STREAMLIT-RESEARCH-009-USER-JOURNEY.md) - Original research
- [V3 Parity Plan](../planning/v3-streamlit-parity-library-evolution-plan.md) - Implementation status
- [8-Week Development Plan](../planning/8-week-development-plan.md) - Timeline
- [React Hooks Index](../index.md) - All available hooks
- [API Reference](../reference/api.md) - Backend endpoints

---

## Changelog

| Date | Change |
|------|--------|
| 2026-01-27 | Initial creation, consolidated from research docs |
