# UI Layout Best Practices Research
**Date:** 2026-01-08
**Focus:** Dashboard layout for engineering design tools
**Status:** 🔍 Research Phase

---

## Current State Analysis

### Problems Identified
1. **Narrow sidebar** with all input controls (300-400px)
2. **Large empty main area** underutilized until "Analyze" is clicked
3. **Poor first impression** - sparse, unbalanced layout
4. **Wasted screen real estate** on wide monitors
5. **Input-output separation** feels disconnected

### Current Layout Pattern
```
┌──────────────────────────────────────────────────────┐
│  [Sidebar]         [Main Area]                       │
│  ┌─────────┐      ┌────────────────────────────────┐ │
│  │ Inputs  │      │                                 │ │
│  │  - Span │      │   Empty until                   │ │
│  │  - Width│      │   "Analyze" clicked            │ │
│  │  - Depth│      │                                 │ │
│  │  - Steel│      │   Then: Charts appear           │ │
│  │  - Load │      │                                 │ │
│  │         │      │                                 │ │
│  │ [Button]│      │                                 │ │
│  └─────────┘      └────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
     20%                    80% wasted
```

---

## Industry Research

### 1. Engineering Software Layouts

#### ETABS, SAP2000 (CSI Software)
**Pattern:** Toolbar + Split Panel
```
┌────────────────────────────────────────────────────┐
│  [Toolbar]                                         │
├─────────────┬──────────────────────────────────────┤
│  Properties │  3D View / Results                   │
│  Panel      │                                      │
│  - Quick    │  [Large interactive area]           │
│  - Compact  │                                      │
│  - Left     │                                      │
├─────────────┴──────────────────────────────────────┤
│  Status Bar                                        │
└────────────────────────────────────────────────────┘
```
**Insight:** Left panel is COMPACT, right area is DOMINANT

#### STAAD.Pro
**Pattern:** Multi-dock interface
- Left: Model tree
- Center: 3D workspace (LARGEST)
- Right: Properties (collapsible)
- Bottom: Output tables (toggle)

**Insight:** Main work area is CENTRAL and LARGE

#### Autodesk Robot Structural Analysis
**Pattern:** Ribbon + Canvas
- Top: Ribbon toolbar (collapsible)
- Center: Full-width canvas
- Side panels: On-demand, floating

**Insight:** Work area gets MAXIMUM space

### 2. Modern Dashboard Patterns

#### Tableau, Power BI
**Pattern:** Full-width canvas with floating controls
```
┌────────────────────────────────────────────────────┐
│  [Filters: Inline, Top] [Actions: Right]          │
├────────────────────────────────────────────────────┤
│                                                    │
│  [Chart 1]         [Chart 2]                      │
│                                                    │
│  [Chart 3]         [Chart 4]                      │
│                                                    │
└────────────────────────────────────────────────────┘
```
**Insight:** Filters are INLINE or TOP, not sidebar

#### Grafana, Kibana
**Pattern:** Full-width panels with top controls
- Top: Time range, refresh, settings (compact)
- Main: Dashboard panels (full width)
- Sidebar: Only for navigation between dashboards

**Insight:** Data visualization gets FULL WIDTH

### 3. CAD/Engineering Tool Patterns

#### AutoCAD
**Pattern:** Ribbon + Canvas + Palettes
- Top: Ribbon (collapsible)
- Center: Drawing canvas (FULL SCREEN capable)
- Right: Palettes (collapsible, stackable)

**Insight:** Work area can go FULL SCREEN

#### Revit
**Pattern:** Properties panel + Main view
- Left: Properties (300-400px, collapsible)
- Center: 3D/2D view (expandable)
- Right: Optional palettes

**Insight:** Panels are COLLAPSIBLE, view is expandable

---

## User Psychology Research

### Visual Hierarchy Principles
1. **F-Pattern Reading:** Users scan top-left → top-right → down
2. **Z-Pattern:** Important CTAs in top-right or bottom-right
3. **Left-to-right flow:** Inputs left → process middle → outputs right

### Dashboard Design Psychology
From "Information Dashboard Design" (Stephen Few):
- **Data-to-pixel ratio:** Maximize information, minimize chrome
- **White space:** Use intentionally, not accidentally
- **Visual grouping:** Related items closer together
- **Progressive disclosure:** Show essentials, reveal details on demand

### Engineering Tool User Expectations
- **Quick entry:** Engineers want fast data entry
- **Immediate feedback:** Real-time validation
- **Visual dominance:** Charts/diagrams more important than numbers
- **Professional appearance:** Sparse ≠ professional, rich ≠ cluttered

---

## Best Practices from Research

### Layout Patterns (Ranked by Suitability)

#### Pattern A: Two-Column Layout (Recommended)
```
┌────────────────────────────────────────────────────┐
│  Header: Title + Navigation                        │
├────────────────────┬───────────────────────────────┤
│  Left (40%)        │  Right (60%)                  │
│  ┌──────────────┐  │  ┌─────────────────────────┐ │
│  │ Geometry     │  │  │ Real-time Preview       │ │
│  │ - Span       │  │  │                         │ │
│  │ - Width      │  │  │ [Beam diagram]          │ │
│  │ - Depth      │  │  │                         │ │
│  ├──────────────┤  │  └─────────────────────────┘ │
│  │ Materials    │  │                              │
│  │ - Concrete   │  │  ┌─────────────────────────┐ │
│  │ - Steel      │  │  │ Design Status           │ │
│  ├──────────────┤  │  │ - Min Steel: ✓          │ │
│  │ Loading      │  │  │ - Span/d: ⚠️            │ │
│  │ - Moment     │  │  │ - Cover: ✓              │ │
│  │ - Shear      │  │  └─────────────────────────┘ │
│  └──────────────┘  │                              │
│                    │  [Analyze Button - Prominent] │
└────────────────────┴───────────────────────────────┘
```

**Pros:**
- Balanced layout (40/60 split, not 20/80)
- Real-time preview shows beam as you type
- Immediate feedback on validity
- Professional, modern appearance
- Good for desktop AND tablet

**Cons:**
- More complex to implement
- Needs responsive breakpoints

#### Pattern B: Collapsible Sidebar + Full Canvas
```
┌────────────────────────────────────────────────────┐
│  [☰] Title                             [Actions]   │
├─┬──────────────────────────────────────────────────┤
│ │  [Full-width work area]                         │
│S│  - Shows example beam OR                        │
│I│  - Shows input form in cards (when sidebar off) │
│D│  - Shows results after analyze                  │
│E│                                                  │
│B│  [Floating "Analyze" button]                    │
│A│                                                  │
│R│                                                  │
└─┴──────────────────────────────────────────────────┘
```

**Pros:**
- Maximum screen space for results
- Modern, clean, minimalist
- Familiar pattern (Gmail, Slack)

**Cons:**
- Complex state management
- Can be confusing for new users

#### Pattern C: Top Form + Bottom Results (Linear Flow)
```
┌────────────────────────────────────────────────────┐
│  Header                                            │
├────────────────────────────────────────────────────┤
│  [Input Form - Horizontal Cards]                  │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐            │
│  │Geom  │ │Mater │ │Load  │ │Supp  │ [Analyze]  │
│  └──────┘ └──────┘ └──────┘ └──────┘            │
├────────────────────────────────────────────────────┤
│  [Results Area - Full Width]                      │
│  ┌──────────────┐ ┌──────────────┐               │
│  │ Beam Diagram │ │ BMD/SFD      │               │
│  └──────────────┘ └──────────────┘               │
└────────────────────────────────────────────────────┘
```

**Pros:**
- Natural top-to-bottom flow
- Full width for both inputs and outputs
- Easy to understand

**Cons:**
- Long pages, lots of scrolling
- Inputs not visible when viewing results
- Less efficient use of vertical space

---

## Competitive Analysis

### Structural Design Apps

#### SpBeam (Web-based)
- **Layout:** Top inputs (tabbed), bottom results
- **Strength:** Clean, organized tabs
- **Weakness:** Inputs hidden when viewing results

#### ClearCalcs
- **Layout:** Left panel (inputs), right panel (live results)
- **Strength:** Real-time feedback, professional
- **Weakness:** Can feel cramped on small screens

#### SkyCiv Beam
- **Layout:** Top toolbar, center canvas, right panel
- **Strength:** CAD-like feel, interactive
- **Weakness:** Complex for simple use cases

### Key Takeaways
1. **Real-time feedback is expected** in modern tools
2. **Two-column layouts dominate** professional tools
3. **Input panels are 30-40% width**, not sidebar-thin
4. **Progressive disclosure** - start simple, reveal complexity

---

## Specific Recommendations for This Project

### Immediate Improvements (IMPL-UI-001)

#### 1. Two-Column Layout (Recommended)
**Implementation:**
- Left: 40% width (`st.columns([2, 3])`)
- Right: 60% width
- Replace sidebar with left column
- Add real-time preview in right column

**Benefits:**
- Better balance
- Real-time feedback
- Professional appearance
- Easier to compare inputs/outputs

#### 2. Real-Time Preview Panel
**Show before "Analyze":**
- Beam diagram (span, supports)
- Current dimensions (width × depth)
- Material properties (fck, fy)
- Basic validity checks (❌ or ✓)

**Benefits:**
- Reduces perceived emptiness
- Immediate feedback
- Catches errors early
- Looks professional

#### 3. Smart Input Organization
**Group inputs into collapsible sections:**
- 📏 Geometry (always expanded)
- 🧱 Materials (expanded)
- ⚡ Loading (expanded)
- 🌡️ Exposure & Support (collapsed by default)

**Benefits:**
- Less overwhelming
- Vertical space saved
- Power users can collapse
- New users see essentials

#### 4. Prominent CTA
**"Analyze Design" button:**
- Large, primary color
- Center of screen OR top-right
- Icon + text
- Keyboard shortcut (Ctrl+Enter)

**Benefits:**
- Clear next action
- Professional appearance
- Accessible

### Medium-Term Improvements (IMPL-UI-002)

#### 1. Tabbed Input Interface
```
[Geometry] [Materials] [Loading] [Advanced]
┌─────────────────────────────────────────┐
│ ... inputs for active tab ...           │
└─────────────────────────────────────────┘
[Analyze Design ➜]
```

#### 2. Live Validation Dashboard
```
✓ Span/depth ratio: OK (L/d = 11.1)
⚠️ Min reinforcement: Review (ρ = 0.18%)
✓ Cover: Adequate (40mm for moderate)
```

#### 3. Example Designs Carousel
```
[← Previous] [Simply Supported 5m Beam] [Next →]
[Load Example]
```

### Long-Term Vision (IMPL-UI-003)

#### 1. Interactive Canvas
- Click beam to edit dimensions
- Drag supports to change span
- Click loads to adjust values

#### 2. Split-Screen Mode
- Left: Inputs
- Right: Live results (updates as you type)
- Toggle: Edit mode ↔ Review mode

#### 3. Workspace Layouts
- **Beginner:** Step-by-step wizard
- **Professional:** Split-screen, all controls
- **Presentation:** Results-only, full screen

---

## Implementation Priority

### Phase 1: Quick Wins (2-3 hours) ⚡
1. **Two-column layout** - Replace sidebar with st.columns([2, 3])
2. **Real-time preview** - Show beam diagram + basic checks
3. **Better spacing** - Use design system properly
4. **Prominent button** - Make "Analyze" more obvious

**Impact:** 80% of visual improvement
**Effort:** Low
**Risk:** Low

### Phase 2: Enhanced UX (4-6 hours) 📈
1. **Collapsible sections** - Group inputs logically
2. **Live validation** - Show OK/Warning/Error inline
3. **Example designs** - Quick-load templates
4. **Better mobile support** - Responsive breakpoints

**Impact:** 15% additional improvement
**Effort:** Medium
**Risk:** Medium (state management)

### Phase 3: Advanced Features (8-10 hours) 🚀
1. **Tabbed inputs** - Reduce vertical scrolling
2. **Interactive canvas** - Click-to-edit
3. **Split-screen mode** - Live updates
4. **Keyboard shortcuts** - Power user efficiency

**Impact:** 5% additional (power users)
**Effort:** High
**Risk:** High (complex interactions)

---

## Success Metrics

### Before (Current State)
- Input area: ~20% of screen
- Empty space: ~80% before analyze
- Time to first insight: After "Analyze" click
- Professional appearance: 6/10

### After Phase 1
- Input area: ~40% of screen
- Utilized space: ~90% (with preview)
- Time to first insight: Immediate (live preview)
- Professional appearance: 9/10

### After Phase 2
- Utilized space: ~95%
- Error detection: Before clicking "Analyze"
- Learning curve: Reduced by examples
- Professional appearance: 9.5/10

---

## Design Mockups (Text-based)

### Current (BEFORE)
```
┌─────────┬──────────────────────────────────────────┐
│Sidebar  │                                          │
│         │                                          │
│Span: __ │         [Empty space]                    │
│Width:__ │                                          │
│Depth:__ │   "Click Analyze to see results"        │
│Steel:__ │                                          │
│Load: __ │                                          │
│         │                                          │
│[Analyze]│                                          │
│         │                                          │
└─────────┴──────────────────────────────────────────┘
  Cramped              Wasted
```

### Proposed (AFTER Phase 1)
```
┌──────────────────────┬─────────────────────────────┐
│  Input Panel (40%)   │  Preview Panel (60%)        │
│                      │                             │
│ 📏 Geometry          │  ┌───────────────────────┐  │
│ Span:    5000 mm     │  │ [Beam Diagram]        │  │
│ Width:    300 mm     │  │ 5000mm x 300x500mm    │  │
│ Depth:    500 mm     │  │ ━━━━━━━━━━━━━━━━━     │  │
│                      │  │ ▲            ▲        │  │
│ 🧱 Materials         │  └───────────────────────┘  │
│ Concrete: M25        │                             │
│ Steel:    Fe500      │  Status:                    │
│                      │  ✓ Dimensions OK            │
│ ⚡ Loading           │  ✓ Materials OK             │
│ Moment:   120 kNm    │  ⚠️ Ready to analyze        │
│ Shear:     80 kN     │                             │
│                      │  ┌─────────────────────┐   │
│ [🔍 Analyze Design]  │  │                     │   │
│                      │  │ Results will appear │   │
└──────────────────────┴──│ here after analyze  │───┘
                          └─────────────────────┘
  Comfortable              Always useful
```

### Future Vision (Phase 3)
```
┌──────────────────────────────────────────────────────┐
│ [Mode: ● Edit  ○ Review]  [Workspace: Professional] │
├────────────────────┬─────────────────────────────────┤
│  Inputs (35%)      │  Live Results (65%)             │
│  [Tabbed]          │  [Updates as you type]          │
│  • Geometry ✓      │                                 │
│  • Materials       │  ┌──────────────────────────┐   │
│  • Loading         │  │ Interactive Beam Diagram│   │
│  • Advanced        │  │ (click to edit)         │   │
│                    │  └──────────────────────────┘   │
│  Live Checks:      │                                 │
│  ✓ Min steel       │  ┌──────────────────────────┐   │
│  ⚠️ L/d ratio      │  │ BMD (live)              │   │
│  ✓ Cover           │  └──────────────────────────┘   │
│                    │                                 │
│  [Ctrl+Enter]      │  Utilization: ░░░░░░░░░░ 75%   │
└────────────────────┴─────────────────────────────────┘
```

---

## Technical Implementation Notes

### Streamlit Considerations

#### Current Limitation
- Streamlit reruns entire script on interaction
- Sidebar vs main area is separate

#### Solutions
1. **Use `st.columns()` instead of sidebar**
   ```python
   col_input, col_preview = st.columns([2, 3])
   with col_input:
       # Input controls
   with col_preview:
       # Real-time preview
   ```

2. **Session state for real-time updates**
   ```python
   st.session_state.beam_params = {...}
   # Preview updates automatically on rerun
   ```

3. **Caching for performance**
   ```python
   @st.cache_data
   def generate_preview(span, width, depth):
       # Generate diagram
   ```

### Responsive Design
```python
# Desktop: Two columns
if st.session_state.get('viewport_width', 1920) > 768:
    col1, col2 = st.columns([2, 3])
else:
    # Mobile: Stacked
    col1 = st.container()
    col2 = st.container()
```

---

## Conclusion

### Recommendation
**Implement Pattern A (Two-Column Layout) in Phase 1**

**Why:**
- Biggest visual impact
- Relatively simple to implement
- Industry standard for engineering tools
- Matches user expectations
- Good ROI (80% improvement, 3 hours effort)

### Next Steps
1. Create IMPL-UI-001 task in TASKS.md
2. Design mockups for two-column layout
3. Refactor beam_design.py to use columns
4. Add real-time preview component
5. Update other pages (cost, compliance) similarly
6. Test on different screen sizes
7. Gather user feedback

### Success Criteria
- [ ] Input area increased to 40% width
- [ ] Preview panel shows beam diagram + status
- [ ] "Analyze" button is prominent and clear
- [ ] Layout works on 1024px+ screens
- [ ] Professional appearance rating 9/10
- [ ] Zero usability regressions

---

**Research completed:** 2026-01-08
**Next action:** Create implementation task
**Estimated total effort:** 2-3 hours (Phase 1)
