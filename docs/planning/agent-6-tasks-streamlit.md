# Background Agent 6 Tasks (STREAMLIT SPECIALIST)

**Agent Role:** STREAMLIT UI SPECIALIST (Daily Development)
**Primary Focus:** Build production-ready Streamlit dashboards for structural engineering, following professional UI/UX practices
**Status:** Active
**Last Updated:** 2026-01-08
**Frequency:** Daily (30-60 min/day)

---

## Mission Statement

Build a **world-class Streamlit UI** for the structural engineering library that:
- **Professional** - Production-ready, not prototype quality
- **User-Centric** - Intuitive for structural engineers (not just developers)
- **Fast** - Optimized performance, instant feedback
- **Accessible** - WCAG 2.1 compliant, keyboard navigation
- **Tested** - Automated tests, visual regression, load testing
- **Documented** - Every component documented with examples
- **Maintainable** - Clean code, design system, reusable components

**Philosophy:** Research → Prototype → Test → Iterate → Deploy

---

## Git Workflow (Critical - Follow Strictly!)

### Daily Development Workflow

**Morning Routine (5-10 min):**
```bash
# 1. Always start from clean main
git checkout main
git pull origin main  # Get latest changes from MAIN agent

# 2. Create dated feature branch
# Format: streamlit/YYYY-MM-DD-feature-name
git checkout -b streamlit/2026-01-08-add-beam-visualizer

# 3. Verify clean state
git status  # Should show "nothing to commit, working tree clean"
```

**During Development:**
```bash
# 4. Make small, incremental changes (1 component at a time)
# ... edit files ...

# 5. Test locally (hot reload enabled)
streamlit run app.py

# 6. Commit when component works
git add .
git commit -m "feat(ui): add beam cross-section visualizer

- Interactive SVG diagram of beam section
- Show rebar placement with dimensions
- Color-coded stress zones
- Responsive design (mobile-friendly)

Component tested locally, ready for review."

# 7. Continue with next component
# ... repeat steps 4-6 ...
```

**End of Day Handoff:**
```bash
# 8. Final commit with summary
git add .
git commit -m "chore(ui): daily streamlit updates 2026-01-08

Summary of today's work:
- Added beam visualizer component
- Improved input validation UX
- Fixed layout on mobile devices
- Updated component documentation

Total: 3 components, 450 lines, all tested locally.

Ready for MAIN review and push."

# 9. STOP - Do NOT push to remote
# Notify MAIN agent with handoff template (see below)
```

### Branch Naming Convention

**Pattern:** `streamlit/YYYY-MM-DD-feature-name`

**Examples:**
- `streamlit/2026-01-08-add-beam-visualizer`
- `streamlit/2026-01-09-cost-comparison-chart`
- `streamlit/2026-01-10-improve-mobile-layout`

**Why dated branches:**
- ✅ Easy to identify when work was done
- ✅ Chronological order in git log
- ✅ Can track daily progress
- ✅ Prevents branch name conflicts

### File Boundaries (STRICT)

**✅ Safe to Create/Edit:**
- `streamlit_app/` (all UI code)
  - `app.py` (main entry point)
  - `components/` (reusable UI components)
  - `pages/` (multi-page app)
  - `utils/` (UI helper functions)
  - `styles/` (custom CSS/themes)
  - `assets/` (images, icons, fonts)
- `streamlit_app/tests/` (UI tests)
- `streamlit_app/docs/` (UI documentation)
- `docs/ui/` (UI design docs, guidelines)

**✅ Safe to Read (for integration):**
- `Python/structural_lib/` (import for calculations)
- `Python/structural_lib/insights/` (SmartDesigner API)
- Any docs for understanding requirements

**❌ NEVER Edit:**
- `Python/structural_lib/` (implementation code - DEV agent territory)
- `Python/tests/` (unit tests - TESTER agent territory)
- `docs/TASKS.md`, `docs/SESSION_log.md` (MAIN agent owns)
- `.github/workflows/` (DEVOPS agent owns)

### Merge Conflicts Prevention

**Rule 1:** Only work in `streamlit_app/` directory
**Rule 2:** Never edit implementation code
**Rule 3:** If you need a new API endpoint, REQUEST it (don't implement)
**Rule 4:** Coordinate with DEV agent if API changes needed

**Example Request to MAIN:**
```markdown
## Request: API Enhancement for UI

**Current:** `design_beam()` returns BeamResults dataclass
**Need:** Additional field `visualization_data` with coordinates for plotting

**Reason:** To render beam diagram in Streamlit without duplicating calculations

**Proposed API:**
```python
@dataclass
class BeamResults:
    # ... existing fields ...
    visualization_data: Optional[VisualizationData] = None

@dataclass
class VisualizationData:
    beam_coordinates: list[tuple[float, float]]
    rebar_positions: list[tuple[float, float]]
    neutral_axis_depth: float
```

**Who implements:** DEV agent (Agent 4)
**Priority:** Medium (blocks beam visualizer feature)
```

---

## Phase 1: Comprehensive Research (Week 1-2)

### STREAMLIT-RESEARCH-001: Streamlit Ecosystem Research (Priority: 🔴 CRITICAL)
**Status:** 🟡 TODO
**Estimated Effort:** 8-12 hours
**Deadline:** Before any coding starts!

**Objective:** Understand Streamlit's capabilities, limitations, best practices from official sources and community

**Research Sources (Minimum 15):**

1. **Official Documentation (streamlit.io)**
   - Complete API reference
   - Performance optimization guide
   - Deployment best practices
   - Caching strategies (@st.cache_data, @st.cache_resource)
   - Session state management
   - Multi-page apps
   - Custom components

2. **Streamlit GitHub Repository**
   - Read top 20 issues (common pain points)
   - Read top 10 discussions (best practices)
   - Study example apps in gallery
   - Check release notes (recent features)

3. **Streamlit Community**
   - Streamlit forums (discuss.streamlit.io)
   - Reddit r/streamlit (top posts, year)
   - Medium articles on Streamlit best practices
   - YouTube: Official Streamlit channel tutorials

4. **Production Streamlit Apps (Case Studies)**
   - Find 5-10 production Streamlit dashboards
   - Screenshot their UIs
   - Document what works well, what doesn't
   - Note performance issues mentioned in reviews

5. **Academic/Industry Research**
   - Search: "Streamlit dashboard best practices"
   - Search: "Streamlit performance optimization"
   - Search: "Streamlit vs Dash vs Gradio" (understand trade-offs)

**Deliverable:**
`streamlit_app/docs/research/streamlit-ecosystem-research.md` (1500-2000 lines)

**Structure:**
```markdown
# Streamlit Ecosystem Research

## Executive Summary
[3-5 key findings, recommended approach]

## Part 1: Official Capabilities
### 1.1 Core Components (50+ widgets)
- Inputs: st.text_input, st.number_input, st.selectbox, st.slider, etc.
- Outputs: st.write, st.dataframe, st.table, st.json, etc.
- Charts: st.line_chart, st.bar_chart, st.pyplot, st.plotly_chart, etc.
- Layouts: st.columns, st.tabs, st.expander, st.sidebar, etc.
- Media: st.image, st.audio, st.video, etc.

### 1.2 Advanced Features
- Caching (@st.cache_data vs @st.cache_resource - when to use each)
- Session state (st.session_state - persisting data between reruns)
- Custom components (React integration for advanced UI)
- Theming (custom CSS, dark mode)

### 1.3 Performance Optimization
- Rerun triggers (what causes full page reload)
- Partial reruns (st.fragment for isolated updates)
- Lazy loading (defer expensive computations)
- Connection pooling (database connections)

## Part 2: Common Pain Points (From GitHub Issues)
[List top 20 issues, how to avoid them]

Example:
### Issue #1234: Slow performance with large dataframes
**Problem:** st.dataframe(df) with 100k rows freezes UI
**Solution:** Use pagination or st.data_editor with row limits
**Our approach:** Limit beam design results to 100 rows, add "Export All" button

## Part 3: Production App Case Studies
[5-10 real apps analyzed]

Example:
### Case Study 1: Snowflake's COVID-19 Dashboard
**URL:** [link]
**What works:** Clean layout, fast load time, clear CTAs
**What doesn't:** Too many charts on one page (overwhelming)
**Lessons for us:** Focus on 1-2 key metrics per page

## Part 4: Best Practices (Synthesized)
### Layout Design
- Use st.columns for side-by-side components
- Sidebar for inputs, main area for results
- st.expander for advanced options
- st.tabs for multiple views

### State Management
- Use st.session_state for user inputs
- Reset state on "Clear" button
- Persist form data on validation errors

### Error Handling
- Never show Python stack traces to users
- Use st.error() with friendly messages
- Validate inputs before computation
- Show st.spinner() for long operations

### Accessibility
- Use semantic HTML (st.markdown with proper headings)
- Alt text for images
- ARIA labels for interactive elements
- Keyboard navigation (test with Tab key)

## Part 5: Our Architecture Decisions
[Based on research, what we'll do]

### Decision 1: Multi-page app structure
**Why:** Separate concerns (beam design, cost analysis, documentation)
**Implementation:** pages/01_beam_design.py, pages/02_cost_optimizer.py, etc.

### Decision 2: Plotly for charts (not matplotlib)
**Why:** Interactive, responsive, better performance
**Trade-off:** Larger bundle size, but worth it for UX

### Decision 3: Custom theme matching IS 456 colors
**Why:** Professional appearance, recognizable to engineers
**Colors:** Blue (#003366), Orange (#FF6600), White (#FFFFFF)

## Appendices
### A: API Reference Quick Links
### B: Performance Benchmarks
### C: Accessibility Checklist
### D: Deployment Options Comparison
```

**Acceptance Criteria:**
- [ ] 15+ sources cited with URLs
- [ ] 1500+ lines comprehensive analysis
- [ ] 5+ production app case studies
- [ ] Clear architectural recommendations
- [ ] Performance optimization strategies documented

---

### STREAMLIT-RESEARCH-002: Our Codebase Integration Research (Priority: 🔴 CRITICAL)
**Status:** 🟡 TODO (blocked by STREAMLIT-RESEARCH-001)
**Estimated Effort:** 6-8 hours

**Objective:** Understand our existing codebase, API surface, data models, and integration points

**Research Tasks:**

1. **Read All Implementation Code**
   ```bash
   # Study our library thoroughly
   find Python/structural_lib -name "*.py" | head -20

   # Priority files to understand:
   # - Python/structural_lib/beam_design.py (core calculations)
   # - Python/structural_lib/insights/smart_designer.py (unified dashboard)
   # - Python/structural_lib/insights/quick_precheck.py (fast validation)
   # - Python/structural_lib/rebar_optimizer.py (cost optimization)
   # - Python/structural_lib/compliance.py (IS 456 checks)
   # - Python/structural_lib/types.py (dataclasses, type definitions)
   ```

2. **Map API Surface**
   ```python
   # Document every public function/class we'll use in UI

   # Example:
   from structural_lib.insights import smart_analyze_design

   # Function signature:
   def smart_analyze_design(
       span_mm: float,
       b_mm: float,
       d_mm: float,
       D_mm: float,
       mu_knm: float,
       fck_nmm2: float,
       fy_nmm2: float = 415.0
   ) -> SmartAnalysisResult:
       """
       Returns:
       - SmartAnalysisResult with:
           - beam_result: BeamDesignResult
           - cost_analysis: CostAnalysis
           - design_suggestions: list[str]
           - sensitivity_data: dict
       """
   ```

3. **Understand Data Models**
   ```python
   # For each dataclass, document:
   # - All fields
   # - Field types
   # - What they represent (with units!)
   # - How to display in UI

   @dataclass
   class BeamDesignResult:
       Ast_provided: float  # mm² - display as "Steel Area: 603 mm²"
       num_bars: int        # count - display as "Number of Bars: 3"
       bar_diameter: int    # mm - display as "Bar Diameter: 16 mm"
       cost_per_meter: float  # ₹ - display as "Cost: ₹87.45/m"
       # ... etc
   ```

4. **Identify Visualization Opportunities**
   ```markdown
   # What can we visualize?

   ## Beam Cross-Section Diagram
   - Show rectangular section (b × D)
   - Draw rebar placement (circles at correct positions)
   - Indicate neutral axis depth
   - Color-code compression/tension zones

   ## Cost Comparison Chart
   - Bar chart: different bar arrangements vs cost
   - Highlight recommended option
   - Show cost savings %

   ## Design Sensitivity Plot
   - Line chart: parameter variation vs capacity
   - Example: span 3-6m vs moment capacity
   - Help engineers understand design trade-offs

   ## Compliance Checklist
   - Visual checkmarks for passed checks
   - Red warnings for failures
   - Links to IS 456 clauses
   ```

5. **Study Existing Examples**
   ```bash
   # If we have any existing Streamlit code or examples
   find . -name "*streamlit*" -o -name "*app.py"

   # Check if there are example scripts
   ls Python/examples/

   # Read any CLI implementations (can adapt for UI)
   find . -name "*cli*"
   ```

**Deliverable:**
`streamlit_app/docs/research/codebase-integration-research.md` (1000-1500 lines)

**Structure:**
```markdown
# Codebase Integration Research

## Executive Summary
[API surface map, integration strategy]

## Part 1: API Surface Documentation
### 1.1 Design Functions
- design_beam() - Core beam design
- quick_precheck() - Fast validation
- smart_analyze_design() - Complete analysis

[For each function: signature, inputs, outputs, example usage]

### 1.2 Data Models
[Complete documentation of all dataclasses]

### 1.3 Utility Functions
[Helper functions we'll need]

## Part 2: Visualization Opportunities
[Detailed specs for each visualization]

### Viz 1: Beam Cross-Section
**Input data:** b_mm, D_mm, d_mm, rebar positions
**Chart type:** Custom SVG (Plotly shapes)
**Interactions:** Hover to see dimensions, click to highlight zones
**Implementation:** Use Plotly Figure with annotations

### Viz 2: Cost Comparison
[etc.]

## Part 3: Integration Architecture
[How Streamlit app will call our library]

```python
# Proposed structure:

# streamlit_app/app.py (main entry point)
import streamlit as st
from structural_lib.insights import smart_analyze_design

st.title("Structural Engineering Design Dashboard")

# Input section
span_mm = st.number_input("Span (mm)", value=4000)
# ... more inputs ...

# Compute button
if st.button("Analyze Design"):
    with st.spinner("Analyzing..."):
        result = smart_analyze_design(span_mm, b_mm, d_mm, ...)

    # Display results
    st.success(f"Design complete! Cost: ₹{result.cost_analysis.cost_per_meter:.2f}/m")

    # Visualizations
    fig = create_beam_diagram(result)
    st.plotly_chart(fig)
```

## Part 4: Error Handling Strategy
[How to handle errors gracefully in UI]

### Validation Errors
- Input out of range → st.warning() before computation
- Invalid combinations → st.error() with suggestions

### Computation Errors
- Convergence failures → st.error() with retry suggestion
- Code violations → st.warning() with clause reference

### System Errors
- Never show stack trace → st.error("An error occurred. Please contact support.")
- Log to file for debugging

## Part 5: Testing Strategy
[How to test Streamlit UI]

### Unit Tests (pytest)
- Test utility functions
- Test data transformations
- Mock Streamlit components

### Integration Tests
- Test API calls
- Test result processing
- End-to-end workflows

### Visual Regression Tests
- Screenshot comparison (Playwright)
- Layout tests (responsive design)

## Part 6: Performance Optimization
[Caching strategy for our use case]

### Cache Design Results
```python
@st.cache_data
def compute_design(span, b, d, D, mu, fck, fy):
    return smart_analyze_design(span, b, d, D, mu, fck, fy)
```

### Cache Visualizations
```python
@st.cache_data
def create_beam_diagram(result):
    # Generate Plotly figure
    return fig
```

### Session State for Form Data
```python
if 'span_mm' not in st.session_state:
    st.session_state.span_mm = 4000
```

## Appendices
### A: Complete API Reference
### B: Data Model Diagrams
### C: Example Code Snippets
### D: Performance Benchmarks
```

**Acceptance Criteria:**
- [ ] Complete API surface documented (all functions)
- [ ] All dataclasses mapped with field descriptions
- [ ] 5+ visualization specs detailed
- [ ] Integration architecture designed
- [ ] Error handling strategy defined
- [ ] Testing strategy documented

---

### STREAMLIT-RESEARCH-003: UI/UX Best Practices for Engineering Software (Priority: 🟠 HIGH)
**Status:** 🟡 TODO (blocked by STREAMLIT-RESEARCH-001)
**Estimated Effort:** 6-8 hours

**Objective:** Research UI/UX principles specific to engineering dashboards, accessibility standards, and professional design

**Research Sources:**

1. **Engineering Software UI Examples**
   - ETABS UI (structural analysis software)
   - STAAD.Pro interface
   - AutoCAD Civil 3D
   - Tekla Structures
   - Screenshot and analyze layouts

2. **Dashboard Design Principles**
   - Google Material Design guidelines
   - Apple Human Interface Guidelines
   - Nielsen Norman Group (dashboard usability)
   - Edward Tufte (data visualization principles)

3. **Accessibility Standards**
   - WCAG 2.1 Level AA (Web Content Accessibility Guidelines)
   - ARIA (Accessible Rich Internet Applications)
   - Keyboard navigation patterns
   - Screen reader compatibility

4. **Color Theory for Engineering**
   - Colorblind-safe palettes
   - High contrast for readability
   - Semantic colors (red=danger, green=success, etc.)

5. **Typography for Technical Content**
   - Monospace fonts for code/numbers
   - Sans-serif for UI text
   - Font sizes for readability (14-16px body)

**Deliverable:**
`streamlit_app/docs/research/ui-ux-best-practices.md` (800-1200 lines)

**Structure:**
```markdown
# UI/UX Best Practices for Engineering Dashboards

## Executive Summary
[Key principles we'll follow]

## Part 1: Engineering Software UI Analysis
[Screenshots and analysis of 5+ professional tools]

### ETABS Analysis
**Strengths:**
- Clean ribbon interface (organized by task)
- 3D visualization with clear controls
- Status bar shows units, errors prominently

**Weaknesses:**
- Overwhelming number of options (steep learning curve)
- Inconsistent icon design
- Poor mobile/tablet experience

**Lessons for us:**
- Group related functions together
- Show units next to every input
- Progressive disclosure (hide advanced options)

## Part 2: Dashboard Layout Patterns
### Pattern 1: Input-Output Split
```
┌─────────────────────────────────────────┐
│  [Sidebar: Inputs]  │  [Main: Results]  │
│                     │                    │
│  Span: [4000] mm    │  ✅ Design OK      │
│  Width: [230] mm    │                    │
│  ...                │  Cost: ₹87.45/m    │
│                     │                    │
│  [Analyze Button]   │  [Beam Diagram]    │
└─────────────────────────────────────────┘
```

### Pattern 2: Wizard/Stepped Flow
```
Step 1: Geometry → Step 2: Loads → Step 3: Design → Step 4: Results
```

### Pattern 3: Tabbed Views
```
Tabs: Design | Optimization | Compliance | Export
```

**Our choice:** Pattern 1 (sidebar inputs) for main app, Pattern 3 (tabs) for results

## Part 3: Accessibility Guidelines
### WCAG 2.1 Level AA Requirements
- Color contrast ratio ≥ 4.5:1 (text)
- Color contrast ratio ≥ 3:1 (UI components)
- Keyboard navigation (Tab, Enter, Esc)
- Screen reader labels (ARIA)
- Focus indicators visible
- No flashing content (seizure risk)

### Implementation Checklist
- [ ] All inputs have labels
- [ ] All buttons have clear text (not just icons)
- [ ] Error messages descriptive, not just "Error!"
- [ ] Success messages confirm action
- [ ] Loading spinners for long operations
- [ ] Tooltips for complex concepts

## Part 4: Color Palette (Colorblind-Safe)
### Primary Colors
- Blue: #003366 (headings, primary actions)
- Orange: #FF6600 (warnings, highlights)
- Green: #28A745 (success, passed checks)
- Red: #DC3545 (errors, failed checks)
- Gray: #6C757D (secondary text)

### Testing
- Deuteranopia (red-green colorblind): ✅ Pass
- Protanopia (red-green colorblind): ✅ Pass
- Tritanopia (blue-yellow colorblind): ✅ Pass

### Chart Colors
- Use distinct shapes + colors (don't rely on color alone)
- Use patterns for print/grayscale compatibility

## Part 5: Typography Scale
### Font Families
- Headings: Inter (sans-serif, professional)
- Body: Inter (consistency)
- Code/Numbers: JetBrains Mono (monospace, clear digits)

### Font Sizes
- H1: 32px (page title)
- H2: 24px (section heading)
- H3: 18px (subsection)
- Body: 16px (readable on all devices)
- Small: 14px (captions, metadata)
- Code: 14px (monospace)

## Part 6: Responsive Design
### Breakpoints
- Mobile: < 768px (single column layout)
- Tablet: 768px - 1024px (sidebar collapses)
- Desktop: > 1024px (full layout)

### Mobile Optimizations
- Larger touch targets (44px min)
- Collapsible sections (accordions)
- Scrollable tables (horizontal scroll)
- Hide non-essential elements

## Part 7: Error Handling UX
### Input Validation
**Bad:**
```python
st.error("Invalid input")
```

**Good:**
```python
if span_mm < 1000:
    st.warning("⚠️ Span is very small (< 1m). Are you sure this is correct?")
elif span_mm > 12000:
    st.error("❌ Span exceeds maximum limit (12m). Please reduce span or use multiple supports.")
else:
    st.success("✅ Span is valid")
```

### Computation Errors
**Bad:**
```python
except Exception as e:
    st.error(str(e))  # Shows Python error
```

**Good:**
```python
except ConvergenceError:
    st.error("❌ Design did not converge. Try increasing section depth or concrete grade.")
except ComplianceError as e:
    st.warning(f"⚠️ Design violates IS 456 Cl. {e.clause}. {e.message}")
except Exception:
    st.error("❌ An unexpected error occurred. Please contact support.")
    logging.exception("Streamlit UI error")  # Log for debugging
```

## Part 8: Loading States
### Quick Operations (< 1s)
- No spinner needed

### Medium Operations (1-3s)
```python
with st.spinner("Analyzing design..."):
    result = smart_analyze_design(...)
```

### Long Operations (> 3s)
```python
progress_bar = st.progress(0)
status_text = st.empty()

for i, step in enumerate(design_steps):
    status_text.text(f"Step {i+1}/{len(design_steps)}: {step}")
    progress_bar.progress((i+1) / len(design_steps))
    # ... do work ...

status_text.text("Complete!")
```

## Part 9: Data Visualization Principles
### Edward Tufte's Rules
1. Show the data (not just decorations)
2. Maximize data-ink ratio (remove chartjunk)
3. Erase non-data ink
4. Avoid 3D charts (distort perception)
5. Use small multiples (compare charts side-by-side)

### Our Chart Guidelines
- Always label axes with units
- Use consistent colors across charts
- Show gridlines sparingly
- Highlight important values
- Interactive: hover for exact values

## Part 10: Professional Design System
### Component Library
- Buttons: Primary, Secondary, Danger
- Inputs: Text, Number, Select, Slider
- Alerts: Info, Success, Warning, Error
- Cards: Container for related content
- Tables: Sortable, filterable

### Consistency Rules
- All buttons same height (40px)
- Consistent spacing (8px, 16px, 24px multiples)
- Same border radius (4px)
- Same shadow depth

## Appendices
### A: WCAG 2.1 Checklist
### B: Color Palette Swatches
### C: Component Mockups
### D: Responsive Breakpoints
```

**Acceptance Criteria:**
- [ ] 5+ engineering software UIs analyzed
- [ ] WCAG 2.1 compliance checklist created
- [ ] Colorblind-safe palette selected
- [ ] Typography scale defined
- [ ] Responsive design strategy documented
- [ ] Error handling patterns defined

---

## Phase 2: Implementation (Week 3+, Daily Work)

### Daily Workflow Structure

**Every Day (30-60 min):**

1. **Morning Health Check (5 min)**
   ```bash
   # Start from clean main
   git checkout main
   git pull origin main

   # Run app locally to verify it works
   streamlit run streamlit_app/app.py

   # Check for any errors in browser console (F12)
   # Verify recent changes didn't break anything
   ```

2. **Today's Task (from research findings) (40-50 min)**
   - Pick ONE small component to build/improve
   - Examples:
     - "Add input validation for span field"
     - "Create beam cross-section diagram"
     - "Improve error message for invalid concrete grade"
     - "Add dark mode toggle"

3. **Commit & Handoff (5 min)**
   ```bash
   # Test one more time
   streamlit run streamlit_app/app.py

   # Commit if it works
   git add .
   git commit -m "feat(ui): [description]"

   # Handoff to MAIN at end of day
   ```

### Implementation Tasks (Based on Research)

**STREAMLIT-IMPL-001: Project Setup & Architecture** (Day 1-2)
**Priority:** 🔴 CRITICAL
**Status:** 🟡 TODO (blocked by all research tasks)

**Deliverables:**
```
streamlit_app/
├── app.py                      # Main entry point
├── pages/
│   ├── 01_🏗️_beam_design.py    # Beam design page
│   ├── 02_💰_cost_optimizer.py  # Cost optimization page
│   ├── 03_✅_compliance.py      # Compliance checker page
│   └── 04_📚_documentation.py   # Help & docs page
├── components/
│   ├── __init__.py
│   ├── inputs.py               # Reusable input widgets
│   ├── visualizations.py       # Chart components
│   ├── results.py              # Result display components
│   └── layout.py               # Layout helpers
├── utils/
│   ├── __init__.py
│   ├── validation.py           # Input validation
│   ├── formatters.py           # Data formatting
│   └── state.py                # Session state helpers
├── styles/
│   ├── theme.toml              # Streamlit theme config
│   └── custom.css              # Custom CSS
├── assets/
│   ├── logo.png
│   ├── favicon.ico
│   └── examples/
├── tests/
│   ├── test_components.py
│   ├── test_utils.py
│   └── test_integration.py
├── docs/
│   ├── research/               # Research docs (created above)
│   ├── design/                 # Design mockups
│   └── api.md                  # Internal API docs
├── requirements.txt            # Streamlit + dependencies
└── README.md                   # UI-specific README
```

**Setup Steps:**
```bash
# 1. Create directory structure
mkdir -p streamlit_app/{pages,components,utils,styles,assets,tests,docs}

# 2. Create requirements.txt
cat > streamlit_app/requirements.txt << 'EOF'
streamlit>=1.30.0
plotly>=5.18.0
pandas>=2.1.0
pillow>=10.1.0
# Our library (editable install)
-e ../Python
EOF

# 3. Create basic app.py
cat > streamlit_app/app.py << 'EOF'
import streamlit as st

st.set_page_config(
    page_title="Structural Engineering Dashboard",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏗️ Structural Engineering Design Dashboard")
st.markdown("Professional beam design, optimization, and compliance checking")

st.info("👈 Select a page from the sidebar to get started")
EOF

# 4. Create theme
mkdir -p streamlit_app/.streamlit
cat > streamlit_app/.streamlit/config.toml << 'EOF'
[theme]
primaryColor = "#FF6600"  # Orange
backgroundColor = "#FFFFFF"  # White
secondaryBackgroundColor = "#F0F2F6"  # Light gray
textColor = "#003366"  # Navy blue
font = "sans serif"
EOF
```

**Commit:**
```bash
git add streamlit_app/
git commit -m "feat(ui): initialize Streamlit app structure

- Multi-page app layout
- Custom theme (IS 456 colors)
- Component-based architecture
- Test setup
- Documentation structure

Ready for component development."
```

---

**STREAMLIT-IMPL-002: Input Components** (Day 3-5)
**Priority:** 🔴 CRITICAL

**Objective:** Create reusable, validated input components

**Components to Build:**

1. **Dimension Input (with validation)**
```python
# streamlit_app/components/inputs.py

import streamlit as st
from typing import Optional, Tuple

def dimension_input(
    label: str,
    min_value: float,
    max_value: float,
    default_value: float,
    unit: str = "mm",
    help_text: Optional[str] = None,
    key: Optional[str] = None
) -> Tuple[float, bool]:
    """
    Dimension input with validation and visual feedback.

    Returns:
        (value, is_valid): Input value and validation status
    """
    # Create input
    value = st.number_input(
        f"{label} ({unit})",
        min_value=min_value,
        max_value=max_value,
        value=default_value,
        help=help_text,
        key=key
    )

    # Validate
    is_valid = True
    if value < min_value or value > max_value:
        st.error(f"❌ {label} must be between {min_value} and {max_value} {unit}")
        is_valid = False
    elif value < min_value * 1.2:
        st.warning(f"⚠️ {label} is very small. Consider increasing for better structural performance.")
    elif value > max_value * 0.8:
        st.warning(f"⚠️ {label} is very large. Consider reducing or adding supports.")
    else:
        st.success(f"✅ {label} is valid")

    return value, is_valid
```

2. **Material Selector**
```python
def material_selector(
    material_type: str,  # "concrete" or "steel"
    key: Optional[str] = None
) -> dict:
    """
    Material grade selector with properties.

    Returns:
        dict with grade, strength, and other properties
    """
    if material_type == "concrete":
        grades = {
            "M15": {"fck": 15, "cost_factor": 0.9},
            "M20": {"fck": 20, "cost_factor": 1.0},
            "M25": {"fck": 25, "cost_factor": 1.15},
            "M30": {"fck": 30, "cost_factor": 1.3},
        }

        selected_grade = st.selectbox(
            "Concrete Grade",
            options=list(grades.keys()),
            index=1,  # Default M20
            help="IS 456 Table 2: Characteristic compressive strength",
            key=key
        )

        properties = grades[selected_grade]

        st.info(f"📊 fck = {properties['fck']} N/mm²")

        return {
            "grade": selected_grade,
            **properties
        }
```

**Tests:**
```python
# streamlit_app/tests/test_inputs.py

import pytest
from components.inputs import dimension_input

def test_dimension_input_valid():
    # Mock Streamlit context
    # ... test valid input ...
    pass

def test_dimension_input_out_of_range():
    # ... test validation ...
    pass
```

**Daily Commits:**
```bash
# Day 3
git commit -m "feat(ui): add dimension input component with validation"

# Day 4
git commit -m "feat(ui): add material selector component"

# Day 5
git commit -m "test(ui): add unit tests for input components"
```

---

**STREAMLIT-IMPL-003: Visualizations** (Day 6-10)
**Priority:** 🔴 CRITICAL

**Components:**

1. **Beam Cross-Section Diagram**
```python
# streamlit_app/components/visualizations.py

import plotly.graph_objects as go
from dataclasses import dataclass

@dataclass
class BeamVisualizationData:
    b_mm: float
    D_mm: float
    d_mm: float
    rebar_positions: list[tuple[float, float]]  # (x, y) in mm
    neutral_axis_depth: float
    bar_diameter: int

def create_beam_diagram(data: BeamVisualizationData) -> go.Figure:
    """
    Create interactive beam cross-section diagram.
    """
    fig = go.Figure()

    # Draw concrete section (rectangle)
    fig.add_shape(
        type="rect",
        x0=0, y0=0,
        x1=data.b_mm, y1=data.D_mm,
        line=dict(color="navy", width=2),
        fillcolor="lightblue",
        opacity=0.3
    )

    # Draw effective depth line
    fig.add_shape(
        type="line",
        x0=0, y0=data.d_mm,
        x1=data.b_mm, y1=data.d_mm,
        line=dict(color="green", width=1, dash="dash")
    )

    # Draw neutral axis
    fig.add_shape(
        type="line",
        x0=0, y0=data.neutral_axis_depth,
        x1=data.b_mm, y1=data.neutral_axis_depth,
        line=dict(color="red", width=2, dash="dot")
    )

    # Draw rebar
    for x, y in data.rebar_positions:
        fig.add_shape(
            type="circle",
            x0=x - data.bar_diameter/2,
            y0=y - data.bar_diameter/2,
            x1=x + data.bar_diameter/2,
            y1=y + data.bar_diameter/2,
            fillcolor="orange",
            line=dict(color="darkorange", width=2)
        )

    # Add annotations
    fig.add_annotation(
        x=data.b_mm/2, y=data.D_mm + 20,
        text=f"b = {data.b_mm:.0f} mm",
        showarrow=False
    )

    fig.add_annotation(
        x=data.b_mm + 30, y=data.D_mm/2,
        text=f"D = {data.D_mm:.0f} mm",
        showarrow=False
    )

    # Layout
    fig.update_layout(
        title="Beam Cross-Section",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False, scaleanchor="x", scaleratio=1),
        width=600,
        height=400,
        showlegend=False,
        hovermode='closest'
    )

    return fig
```

2. **Cost Comparison Chart**
```python
def create_cost_comparison(options: list[dict]) -> go.Figure:
    """
    Bar chart comparing different design options by cost.

    options: [
        {"name": "3-16mm", "cost": 87.45, "is_recommended": True},
        {"name": "2-20mm", "cost": 92.30, "is_recommended": False},
        ...
    ]
    """
    fig = go.Figure()

    names = [opt["name"] for opt in options]
    costs = [opt["cost"] for opt in options]
    colors = ["green" if opt.get("is_recommended") else "lightblue" for opt in options]

    fig.add_trace(go.Bar(
        x=names,
        y=costs,
        marker_color=colors,
        text=[f"₹{c:.2f}" for c in costs],
        textposition='outside'
    ))

    fig.update_layout(
        title="Cost Comparison: Bar Arrangements",
        xaxis_title="Arrangement",
        yaxis_title="Cost (₹/m)",
        showlegend=False,
        height=400
    )

    return fig
```

**Daily Commits:**
```bash
# Day 6
git commit -m "feat(ui): add beam cross-section visualization"

# Day 7
git commit -m "feat(ui): add cost comparison chart"

# Day 8
git commit -m "feat(ui): add interactive hover tooltips to diagrams"

# Day 9
git commit -m "feat(ui): add responsive design for mobile"

# Day 10
git commit -m "test(ui): add visual regression tests"
```

---

**STREAMLIT-IMPL-004: Page 1 - Beam Design** (Day 11-15)
**Priority:** 🔴 CRITICAL

**Full page implementation:**

```python
# streamlit_app/pages/01_🏗️_beam_design.py

import streamlit as st
from structural_lib.insights import smart_analyze_design
from components.inputs import dimension_input, material_selector
from components.visualizations import create_beam_diagram, BeamVisualizationData
from components.results import display_results
from utils.validation import validate_inputs
from utils.formatters import format_result

st.set_page_config(page_title="Beam Design", page_icon="🏗️", layout="wide")

st.title("🏗️ Beam Design")
st.markdown("Design reinforced concrete beams per IS 456:2000")

# Sidebar: Inputs
with st.sidebar:
    st.header("Input Parameters")

    # Geometry
    st.subheader("📏 Geometry")
    span_mm, span_valid = dimension_input(
        "Span", 1000, 12000, 4000, "mm",
        help_text="Clear span between supports (Cl. 23.2.1)",
        key="span"
    )

    b_mm, b_valid = dimension_input(
        "Width", 150, 600, 230, "mm",
        help_text="Width of beam section",
        key="width"
    )

    D_mm, D_valid = dimension_input(
        "Total Depth", 200, 900, 450, "mm",
        help_text="Overall depth of beam",
        key="depth"
    )

    d_mm = D_mm - 50  # Assume 50mm cover + stirrup + bar radius
    st.info(f"Effective depth (d) ≈ {d_mm:.0f} mm")

    # Materials
    st.subheader("🧱 Materials")
    concrete = material_selector("concrete", key="concrete")
    steel = material_selector("steel", key="steel")

    # Loading
    st.subheader("⚖️ Loading")
    mu_knm, mu_valid = dimension_input(
        "Factored Moment", 10, 500, 80, "kNm",
        help_text="Ultimate moment (Mu) from load combinations",
        key="moment"
    )

    # Analyze button
    st.divider()
    all_valid = all([span_valid, b_valid, D_valid, mu_valid])

    if not all_valid:
        st.error("❌ Fix validation errors before analyzing")

    analyze = st.button(
        "🚀 Analyze Design",
        type="primary",
        disabled=not all_valid,
        use_container_width=True
    )

# Main area: Results
if analyze:
    with st.spinner("🔄 Analyzing design..."):
        try:
            # Call API
            result = smart_analyze_design(
                span_mm=span_mm,
                b_mm=b_mm,
                d_mm=d_mm,
                D_mm=D_mm,
                mu_knm=mu_knm,
                fck_nmm2=concrete["fck"],
                fy_nmm2=steel["fy"]
            )

            # Store in session state
            st.session_state.last_result = result

        except Exception as e:
            st.error(f"❌ Design analysis failed: {e}")
            st.stop()

    # Display success
    st.success("✅ Design analysis complete!")

    # Results tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Summary",
        "🎨 Visualization",
        "💰 Cost Analysis",
        "✅ Compliance"
    ])

    with tab1:
        st.subheader("Design Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Steel Area Provided",
                f"{result.beam_result.Ast_provided:.0f} mm²",
                delta=f"{result.beam_result.Ast_provided - result.beam_result.Ast_required:.0f} mm² (extra)"
            )

        with col2:
            st.metric(
                "Bar Arrangement",
                f"{result.beam_result.num_bars}-{result.beam_result.bar_diameter}mm"
            )

        with col3:
            st.metric(
                "Cost per Meter",
                f"₹{result.cost_analysis.cost_per_meter:.2f}"
            )

        # Detailed table
        st.dataframe(format_result(result), use_container_width=True)

    with tab2:
        st.subheader("Beam Cross-Section")

        # Create visualization data
        viz_data = BeamVisualizationData(
            b_mm=b_mm,
            D_mm=D_mm,
            d_mm=d_mm,
            rebar_positions=result.get_rebar_positions(),  # From API
            neutral_axis_depth=result.beam_result.xu,
            bar_diameter=result.beam_result.bar_diameter
        )

        fig = create_beam_diagram(viz_data)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Cost Optimization")

        # Show cost comparison
        if hasattr(result, 'alternative_options'):
            fig = create_cost_comparison(result.alternative_options)
            st.plotly_chart(fig, use_container_width=True)

        st.info("💡 Tip: The recommended option minimizes cost while meeting all code requirements.")

    with tab4:
        st.subheader("IS 456 Compliance Checklist")

        # Show compliance results
        for check in result.compliance_results:
            if check.passed:
                st.success(f"✅ {check.description} (Cl. {check.clause})")
            else:
                st.error(f"❌ {check.description} (Cl. {check.clause})")
                st.markdown(f"**Fix:** {check.suggestion}")

else:
    # Show placeholder
    st.info("👈 Enter design parameters in the sidebar and click 'Analyze Design'")

    # Show example
    with st.expander("📖 Example: 4m Span Beam"):
        st.markdown("""
        **Given:**
        - Span: 4000 mm
        - Width: 230 mm
        - Total Depth: 450 mm
        - Moment: 80 kNm
        - Concrete: M20
        - Steel: Fe415

        **Result:**
        - 3-16mm bars
        - Cost: ₹87.45/m
        """)
```

**Daily Commits:**
```bash
# Day 11
git commit -m "feat(ui): implement beam design page layout"

# Day 12
git commit -m "feat(ui): integrate API calls with error handling"

# Day 13
git commit -m "feat(ui): add results tabs (summary, viz, cost, compliance)"

# Day 14
git commit -m "feat(ui): add session state persistence"

# Day 15
git commit -m "feat(ui): add example and help text"
```

---

## Handoff Template

**At End of Each Day:**

```markdown
## Handoff: STREAMLIT SPECIALIST (Agent 6) → MAIN

**Date:** 2026-01-XX
**Branch:** streamlit/2026-01-XX-[feature-name]
**Status:** ✅ Committed locally, tested, ready for review

### Summary
[2-3 sentences: what was built/improved today]

Example:
Built beam cross-section visualization component using Plotly. Creates interactive
SVG diagram showing concrete section, rebar placement, and neutral axis. Tested
with 5 different beam configurations, all render correctly.

### Files Changed
- `streamlit_app/components/visualizations.py` - Added create_beam_diagram()
- `streamlit_app/tests/test_visualizations.py` - Added 10 unit tests
- `streamlit_app/docs/components.md` - Documented component API

### Features Added
- ✅ Interactive beam diagram with hover tooltips
- ✅ Responsive design (works on mobile)
- ✅ Accessibility: ARIA labels, keyboard navigation
- ✅ Unit tests (100% coverage)

### Local Testing
- ✅ Ran `streamlit run app.py` - No errors
- ✅ Tested on Chrome, Firefox, Safari
- ✅ Tested on mobile (iPhone 12, Pixel 5)
- ✅ All unit tests passing: `pytest streamlit_app/tests/`
- ✅ Visual regression tests passed

### Screenshots
[Attach screenshot of component in action]

### Performance
- Initial load: 1.2s
- Rerender: 0.3s
- Bundle size: +45KB (acceptable)

### Next Steps
Tomorrow: Implement cost comparison chart component

### Action Required by MAIN
1. Review changes: `git checkout streamlit/2026-01-XX-feature-name`
2. Test locally: `streamlit run streamlit_app/app.py`
3. If approved:
   ```bash
   git push origin streamlit/2026-01-XX-feature-name
   gh pr create --title "feat(ui): beam cross-section visualizer" --body "..."
   gh pr checks --watch
   gh pr merge --squash
   ```
```

---

## Success Metrics

### Daily Targets
- ✅ 1 component built/improved per day
- ✅ Zero errors in local testing
- ✅ Commit message follows convention
- ✅ Code documented (docstrings)
- ✅ Unit tests written (if applicable)

### Weekly Targets
- ✅ 5 components shipped
- ✅ All PRs reviewed and merged by MAIN
- ✅ No regression bugs
- ✅ Performance maintained (< 2s load time)

### Quality Standards
- ✅ WCAG 2.1 Level AA compliance
- ✅ Works on Chrome, Firefox, Safari
- ✅ Responsive (mobile, tablet, desktop)
- ✅ Unit test coverage > 80%
- ✅ No console errors or warnings

---

## Research Sources Tracking

**Keep research up-to-date:**
- ✅ Check Streamlit release notes monthly (new features)
- ✅ Monitor Streamlit discussions weekly (common issues)
- ✅ Review accessibility guidelines quarterly (standards update)
- ✅ Study competitor UIs semi-annually (stay current)

**Research Log:**
```markdown
# Research Log

## 2026-01-08
- Read Streamlit 1.30 release notes
- Finding: New st.fragment for partial reruns
- Action: Update STREAMLIT-RESEARCH-001 with fragment usage

## 2026-01-15
- Analyzed ETABS 2024 UI
- Finding: Ribbon interface overwhelming for new users
- Action: Keep our sidebar simple, hide advanced options

## 2026-01-22
- WCAG 2.2 draft released
- Finding: New focus visible requirements
- Action: Update accessibility checklist
```

---

## Troubleshooting Common Issues

### Issue 1: Slow Reloads
**Symptom:** Every input change triggers full page reload (slow)
**Cause:** Not using caching or session state
**Fix:**
```python
# Bad
result = smart_analyze_design(...)  # Recomputes every time

# Good
@st.cache_data
def cached_design(span, b, d, D, mu, fck, fy):
    return smart_analyze_design(span, b, d, D, mu, fck, fy)

result = cached_design(span_mm, b_mm, ...)  # Cached!
```

### Issue 2: State Lost on Reload
**Symptom:** User inputs reset when navigating between pages
**Cause:** Not using session state
**Fix:**
```python
# Store inputs in session state
if 'span_mm' not in st.session_state:
    st.session_state.span_mm = 4000

span_mm = st.number_input("Span", value=st.session_state.span_mm)
st.session_state.span_mm = span_mm  # Update
```

### Issue 3: Charts Not Responsive
**Symptom:** Charts overflow on mobile
**Cause:** Fixed width/height
**Fix:**
```python
# Bad
st.plotly_chart(fig, width=800, height=600)

# Good
st.plotly_chart(fig, use_container_width=True)
```

---

**Version:** 1.0 (Research-Driven Professional Streamlit Development)
**Created:** 2026-01-08
**Agent:** STREAMLIT UI SPECIALIST (Agent 6)
**Status:** Ready for research phase! 🚀
