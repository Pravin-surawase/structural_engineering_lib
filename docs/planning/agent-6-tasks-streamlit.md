# Background Agent 6 Tasks (STREAMLIT SPECIALIST)

**Agent Role:** STREAMLIT UI SPECIALIST (Daily Development)
**Primary Focus:** Build production-ready Streamlit dashboards for structural engineering, following professional UI/UX practices
**Status:** Active
**Last Updated:** 2026-01-09T00:15Z
**Frequency:** Daily (30-60 min/day)

---

## 📊 Progress Tracker

### ✅ Completed Tasks

| Task | Description | Lines | Tests | Status |
|------|-------------|-------|-------|--------|
| STREAMLIT-RESEARCH-001 | Streamlit Ecosystem Research | 1,359 | - | ✅ Complete |
| STREAMLIT-RESEARCH-002 | Codebase Integration Research | 1,639 | - | ✅ Complete |
| STREAMLIT-RESEARCH-003 | UI/UX Best Practices | 1,187 | - | ✅ Complete |
| STREAMLIT-IMPL-001 | Project Setup & Architecture | 1,842 | - | ✅ Complete |
| STREAMLIT-IMPL-002 | Input Components | 690 | 29 | ✅ Complete |
| STREAMLIT-IMPL-003 | Visualizations (5 Plotly charts) | 719 | - | ✅ Complete |
| STREAMLIT-IMPL-004 | Beam Design Page | 586 | - | ✅ Complete |
| STREAMLIT-IMPL-005 | Cost Optimizer Page | 494 | - | ✅ Complete |
| STREAMLIT-IMPL-006 | Compliance Checker Page | 485 | - | ✅ Complete |
| STREAMLIT-FIX-001 | Fix All Failing Tests | 1,156 | 52 | ✅ Complete |

**Total Delivered:** 11,157 lines, 81 tests (3 complete pages, 100% pass rate)

### 🔄 ACTIVE PHASES (Start Immediately)

| Task | Description | Priority | Status | Days |
|------|-------------|----------|--------|------|
| STREAMLIT-IMPL-008 | Documentation Page + User Guide | 🔴 CRITICAL | 🟡 TODO | Day 1-2 |
| STREAMLIT-IMPL-009 | Error Handling & Validation | 🔴 CRITICAL | 🟡 TODO | Day 3-4 |
| STREAMLIT-IMPL-010 | Session State & Data Persistence | 🟠 HIGH | 🟡 TODO | Day 5-6 |
| STREAMLIT-IMPL-011 | Export Features (PDF/CSV/DXF) | 🟠 HIGH | 🟡 TODO | Day 7-8 |
| STREAMLIT-IMPL-012 | Settings & Configuration Page | 🟠 HIGH | 🟡 TODO | Day 9-10 |
| STREAMLIT-IMPL-013 | About & Help System | 🟠 HIGH | 🟡 TODO | Day 11-12 |
| STREAMLIT-IMPL-014 | Performance & Caching Optimization | 🟢 MEDIUM | 🟡 TODO | Day 13-14 |
| STREAMLIT-IMPL-015 | Accessibility Audit (WCAG 2.1 AA) | 🟢 MEDIUM | 🟡 TODO | Day 15-16 |
| STREAMLIT-IMPL-016 | E2E Integration Tests | 🟢 MEDIUM | 🟡 TODO | Day 17-18 |
| STREAMLIT-IMPL-017 | Mobile Responsiveness | 🟢 MEDIUM | 🟡 TODO | Day 19-20 |

---

## 🔴 CRITICAL: STREAMLIT-IMPL-008 - Documentation Page + User Guide (Day 1-2)
**Priority:** 🔴 CRITICAL - START NOW
**Status:** 🟡 TODO
**Estimated Effort:** 4-5 hours

### Objective
Create comprehensive, interactive documentation page with:
- IS 456 clause quick reference with search
- Step-by-step user guides for each feature
- Formula explanations with interactive examples
- FAQ section with common questions
- Glossary of structural engineering terms

### Page Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ 📚 Documentation - IS 456 Reference & User Guide                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ [🔍 Search: _______________]   [Quick Links ▼]                      │
│                                                                      │
│ ┌───────────────────────────────────────────────────────────────┐   │
│ │ [Getting Started] [IS 456 Clauses] [Formulas] [FAQ] [Glossary]│   │
│ └───────────────────────────────────────────────────────────────┘   │
│                                                                      │
│ ══════════════════════════════════════════════════════════════════  │
│                                                                      │
│ 🚀 GETTING STARTED                                                  │
│ ┌───────────────────────────────────────────────────────────────┐   │
│ │ **Step 1: Enter Geometry**                                     │   │
│ │ Width (b): 150-600mm typical    Depth (D): Span/10 to Span/15 │   │
│ │                                                                │   │
│ │ **Step 2: Select Materials**                                   │   │
│ │ M20 for residential | M25-M30 for commercial | Fe415/Fe500    │   │
│ │                                                                │   │
│ │ **Step 3: Enter Loads**                                        │   │
│ │ Moment from structural analysis | Shear from support reactions│   │
│ └───────────────────────────────────────────────────────────────┘   │
│                                                                      │
│ 📋 IS 456 CLAUSE REFERENCE                                          │
│ ┌───────────────────────────────────────────────────────────────┐   │
│ │ ▼ Flexure (Cl. 26.5)           ▼ Shear (Cl. 40)              │   │
│ │ ▼ Detailing (Cl. 26.3-26.4)    ▼ Serviceability (Cl. 23)     │   │
│ │ ▼ Ductility (Cl. 21.6)         ▼ Cover (Cl. 26.4.1)          │   │
│ └───────────────────────────────────────────────────────────────┘   │
│                                                                      │
│ 📐 FORMULA CALCULATOR                                               │
│ ┌───────────────────────────────────────────────────────────────┐   │
│ │ Select Formula: [Moment of Resistance ▼]                       │   │
│ │ Inputs: fck=[ 25 ] fy=[ 415 ] b=[ 300 ] d=[ 450 ]            │   │
│ │ Result: Mu_lim = 234.5 kN·m                                   │   │
│ └───────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
# streamlit_app/pages/04_📚_documentation.py (~600 lines)

import streamlit as st

st.set_page_config(
    page_title="Documentation | IS 456 Dashboard",
    page_icon="📚",
    layout="wide"
)

# Search functionality
search_query = st.text_input("🔍 Search documentation...", key="doc_search")

# Navigation tabs
tabs = st.tabs([
    "🚀 Getting Started",
    "📋 IS 456 Clauses",
    "📐 Formulas",
    "❓ FAQ",
    "📖 Glossary"
])

with tabs[0]:  # Getting Started
    st.header("Getting Started Guide")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1️⃣ Understanding Inputs")
        st.markdown("""
        **Geometry:**
        - **Width (b):** 150-600mm for typical beams
        - **Depth (D):** Usually span/10 to span/15
        - **Effective depth (d):** D - cover - bar_dia/2

        **Materials:**
        | Grade | Use Case | fck (N/mm²) |
        |-------|----------|-------------|
        | M20 | Residential | 20 |
        | M25 | Commercial | 25 |
        | M30 | High-rise | 30 |
        """)

    with col2:
        st.subheader("2️⃣ Reading Results")
        st.markdown("""
        **Status Indicators:**
        - ✅ **SAFE** - All checks pass
        - ⚠️ **WARNING** - Marginal, review recommended
        - ❌ **UNSAFE** - Redesign required

        **Key Outputs:**
        - **Ast required** - Tension steel area
        - **Utilization** - % of capacity used
        - **Margin** - Safety factor above minimum
        """)

with tabs[1]:  # IS 456 Clauses
    st.header("IS 456:2000 Clause Reference")

    # Searchable clause database
    clause_search = st.text_input("Search clauses...", key="clause_search")

    with st.expander("📏 Flexure Requirements (Cl. 26.5)", expanded=True):
        st.markdown("""
        ### Cl. 26.5.1.1 - Minimum Tension Reinforcement

        **Formula:**
        $$A_{s,min} = \\frac{0.85 \\cdot b_w \\cdot d}{f_y}$$

        **Purpose:** Ensures ductile failure mode and controls cracking.

        **Typical Values:**
        | Concrete | Steel | pt_min (%) |
        |----------|-------|------------|
        | M20 | Fe415 | 0.205 |
        | M25 | Fe500 | 0.170 |
        """)

    with st.expander("🛡️ Shear Requirements (Cl. 40)"):
        st.markdown("""
        ### Cl. 40.1 - Nominal Shear Stress

        **Formula:**
        $$\\tau_v = \\frac{V_u}{b \\cdot d}$$

        **Check:** τv must be ≤ τc,max (Table 20)

        ### Cl. 40.4 - Shear Reinforcement

        When τv > τc:
        $$A_{sv} = \\frac{V_{us} \\cdot s_v}{0.87 \\cdot f_y \\cdot d}$$
        """)

    # More clauses...

with tabs[2]:  # Formulas
    st.header("📐 Interactive Formula Calculator")

    formula_type = st.selectbox(
        "Select Formula",
        ["Moment of Resistance", "Shear Strength", "Development Length",
         "Deflection Check", "Crack Width"]
    )

    if formula_type == "Moment of Resistance":
        col1, col2 = st.columns([1, 2])
        with col1:
            fck = st.number_input("fck (N/mm²)", value=25.0)
            fy = st.number_input("fy (N/mm²)", value=415.0)
            b = st.number_input("b (mm)", value=300.0)
            d = st.number_input("d (mm)", value=450.0)

        with col2:
            # Calculate Mu_lim
            xu_max_d = 0.48 if fy <= 415 else 0.46
            Mu_lim = 0.36 * fck * b * d**2 * xu_max_d * (1 - 0.42 * xu_max_d) / 1e6

            st.metric("Mu,lim", f"{Mu_lim:.1f} kN·m")
            st.latex(r"M_{u,lim} = 0.36 f_{ck} b d^2 \frac{x_{u,max}}{d} \left(1 - 0.42\frac{x_{u,max}}{d}\right)")

with tabs[3]:  # FAQ
    st.header("❓ Frequently Asked Questions")

    faqs = [
        ("What concrete grade should I use?",
         "M20 for residential (up to 3 floors), M25 for commercial buildings, M30+ for high-rise or aggressive environments."),
        ("How do I size a beam initially?",
         "Start with D = span/12 for simply supported, span/15 for continuous. Width typically 200-400mm."),
        ("What is utilization ratio?",
         "Percentage of the beam's capacity being used. 85-95% is optimal. Below 70% is over-designed, above 100% is unsafe."),
        # Add 10+ FAQs
    ]

    for question, answer in faqs:
        with st.expander(question):
            st.write(answer)

with tabs[4]:  # Glossary
    st.header("📖 Glossary of Terms")

    glossary = {
        "Ast": "Area of tension steel reinforcement (mm²)",
        "Asc": "Area of compression steel reinforcement (mm²)",
        "b": "Width of beam (mm)",
        "d": "Effective depth (mm)",
        "D": "Overall depth (mm)",
        "fck": "Characteristic compressive strength of concrete (N/mm²)",
        "fy": "Characteristic yield strength of steel (N/mm²)",
        # Add 30+ terms
    }

    cols = st.columns(3)
    for i, (term, definition) in enumerate(sorted(glossary.items())):
        with cols[i % 3]:
            st.markdown(f"**{term}:** {definition}")
```

### Files to Create/Modify
1. `streamlit_app/pages/04_📚_documentation.py` (~600 lines) - Main page
2. `streamlit_app/data/is456_clauses.json` (~200 lines) - Clause database
3. `streamlit_app/data/faq.json` (~100 lines) - FAQ content
4. `streamlit_app/data/glossary.json` (~80 lines) - Glossary terms

### Acceptance Criteria
- [ ] Search filters content dynamically across all tabs
- [ ] At least 15 IS 456 clauses documented with formulas
- [ ] Interactive formula calculator for 5+ formulas
- [ ] FAQ has at least 15 questions
- [ ] Glossary has at least 40 terms
- [ ] Formulas render with LaTeX/KaTeX
- [ ] Mobile responsive layout
- [ ] All links work correctly

### Verification
```bash
# Page loads without errors
streamlit run streamlit_app/app.py

# Tests pass
pytest streamlit_app/tests/ -v -k "documentation"
```

---

## 🔴 STREAMLIT-IMPL-009: Error Handling & Validation (Day 3-4)
**Priority:** 🔴 CRITICAL
**Status:** 🟡 TODO
**Estimated Effort:** 4-5 hours

### Objective
Implement comprehensive, user-friendly error handling:
- Centralized error handler with IS 456 clause references
- Input validation with helpful suggestions
- Graceful degradation (partial results when possible)
- Error logging for debugging

### Implementation

#### 1. Create Centralized Error Handler

```python
# streamlit_app/utils/error_handler.py (~150 lines)

import streamlit as st
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import traceback
import logging

class ErrorSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class DesignError:
    """Structured design error with context."""
    message: str
    severity: ErrorSeverity
    clause: Optional[str] = None
    suggestion: Optional[str] = None
    technical_details: Optional[str] = None

    def display(self):
        """Display error in Streamlit UI."""
        icon = {
            ErrorSeverity.INFO: "ℹ️",
            ErrorSeverity.WARNING: "⚠️",
            ErrorSeverity.ERROR: "❌",
            ErrorSeverity.CRITICAL: "🚨"
        }[self.severity]

        if self.severity == ErrorSeverity.WARNING:
            st.warning(f"{icon} {self.message}")
        elif self.severity in (ErrorSeverity.ERROR, ErrorSeverity.CRITICAL):
            st.error(f"{icon} {self.message}")
        else:
            st.info(f"{icon} {self.message}")

        if self.clause:
            st.caption(f"📋 Reference: IS 456 {self.clause}")

        if self.suggestion:
            st.info(f"💡 **Suggestion:** {self.suggestion}")

        if self.technical_details:
            with st.expander("🔍 Technical Details"):
                st.code(self.technical_details)


def validate_geometry(b: float, D: float, d: float) -> list[DesignError]:
    """Validate beam geometry and return errors/warnings."""
    errors = []

    if d >= D:
        errors.append(DesignError(
            message="Effective depth (d) must be less than overall depth (D)",
            severity=ErrorSeverity.ERROR,
            clause="Cl. 26.4.1",
            suggestion=f"Reduce d to at least {D - 50}mm (allowing for cover + bar diameter)"
        ))

    if b > D:
        errors.append(DesignError(
            message=f"Width ({b}mm) greater than depth ({D}mm) is unusual for beams",
            severity=ErrorSeverity.WARNING,
            suggestion="Consider if this should be a slab instead, or increase depth"
        ))

    aspect_ratio = D / b if b > 0 else 0
    if aspect_ratio > 4:
        errors.append(DesignError(
            message=f"High aspect ratio ({aspect_ratio:.1f}) may cause lateral buckling",
            severity=ErrorSeverity.WARNING,
            clause="Cl. 23.3",
            suggestion="Add lateral restraints or increase width"
        ))

    if b < 150:
        errors.append(DesignError(
            message=f"Width ({b}mm) below practical minimum of 150mm",
            severity=ErrorSeverity.WARNING,
            suggestion="Increase width to at least 150mm for constructability"
        ))

    return errors


def validate_materials(fck: float, fy: float) -> list[DesignError]:
    """Validate material properties."""
    errors = []

    valid_fck = [20, 25, 30, 35, 40, 45, 50, 55, 60]
    if fck not in valid_fck:
        errors.append(DesignError(
            message=f"Non-standard concrete grade M{int(fck)}",
            severity=ErrorSeverity.WARNING,
            clause="Table 2",
            suggestion=f"Use standard grade: {', '.join(f'M{g}' for g in valid_fck)}"
        ))

    valid_fy = [250, 415, 500, 550]
    if fy not in valid_fy:
        errors.append(DesignError(
            message=f"Non-standard steel grade Fe{int(fy)}",
            severity=ErrorSeverity.WARNING,
            clause="Cl. 5.6",
            suggestion=f"Use standard grade: {', '.join(f'Fe{g}' for g in valid_fy)}"
        ))

    return errors


def safe_design_call(design_func, **kwargs) -> tuple[Optional[Dict], list[DesignError]]:
    """Wrap design function with error handling."""
    errors = []

    try:
        result = design_func(**kwargs)
        return result, errors
    except ValueError as e:
        errors.append(DesignError(
            message=str(e),
            severity=ErrorSeverity.ERROR,
            suggestion="Check input values are within valid ranges"
        ))
    except Exception as e:
        errors.append(DesignError(
            message="Unexpected calculation error",
            severity=ErrorSeverity.CRITICAL,
            technical_details=traceback.format_exc()
        ))

    return None, errors
```

#### 2. Apply to All Pages

```python
# In each page, use the error handler:

from utils.error_handler import validate_geometry, validate_materials, safe_design_call

# Validate inputs before design
geo_errors = validate_geometry(b, D, d)
mat_errors = validate_materials(fck, fy)

all_errors = geo_errors + mat_errors

# Display any warnings/errors
for error in all_errors:
    error.display()

# Only proceed if no critical errors
critical_errors = [e for e in all_errors if e.severity in (ErrorSeverity.ERROR, ErrorSeverity.CRITICAL)]

if not critical_errors:
    result, calc_errors = safe_design_call(cached_design, b_mm=b, D_mm=D, ...)

    for error in calc_errors:
        error.display()

    if result:
        # Display results
        pass
else:
    st.warning("⚠️ Please fix the errors above before analyzing")
```

### Files to Create/Modify
1. `streamlit_app/utils/error_handler.py` (~150 lines) - NEW
2. `streamlit_app/pages/01_🏗️_beam_design.py` - Add validation
3. `streamlit_app/pages/02_💰_cost_optimizer.py` - Add validation
4. `streamlit_app/pages/03_✅_compliance.py` - Add validation
5. `streamlit_app/tests/test_error_handler.py` (~100 lines) - NEW

### Acceptance Criteria
- [ ] All pages have try/except blocks
- [ ] Errors include IS 456 clause references where applicable
- [ ] Suggestions provided for common issues
- [ ] No raw Python tracebacks shown to users
- [ ] Graceful degradation when partial results possible
- [ ] Error logging to file for debugging
- [ ] At least 20 tests for error handler

---

## 🟠 STREAMLIT-IMPL-010: Session State & Data Persistence (Day 5-6)
**Priority:** 🟠 HIGH
**Status:** 🟡 TODO
**Estimated Effort:** 3-4 hours

### Objective
Implement robust session state management:
- Persist user inputs across page navigation
- Save/load design sessions (local storage or file)
- Recent designs history
- Undo/redo functionality

### Implementation

```python
# streamlit_app/utils/session_manager.py (~200 lines)

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List

@dataclass
class DesignSession:
    """Represents a saved design session."""
    id: str
    timestamp: str
    inputs: dict
    results: Optional[dict]
    notes: str = ""

class SessionManager:
    """Manage design sessions with persistence."""

    HISTORY_KEY = "design_history"
    CURRENT_KEY = "current_design"
    MAX_HISTORY = 20

    @classmethod
    def save_current(cls, inputs: dict, results: dict, notes: str = ""):
        """Save current design to session state."""
        session = DesignSession(
            id=datetime.now().strftime("%Y%m%d_%H%M%S"),
            timestamp=datetime.now().isoformat(),
            inputs=inputs,
            results=results,
            notes=notes
        )

        st.session_state[cls.CURRENT_KEY] = asdict(session)

        # Add to history
        if cls.HISTORY_KEY not in st.session_state:
            st.session_state[cls.HISTORY_KEY] = []

        st.session_state[cls.HISTORY_KEY].insert(0, asdict(session))

        # Trim history
        st.session_state[cls.HISTORY_KEY] = st.session_state[cls.HISTORY_KEY][:cls.MAX_HISTORY]

    @classmethod
    def get_current(cls) -> Optional[DesignSession]:
        """Get current design session."""
        data = st.session_state.get(cls.CURRENT_KEY)
        return DesignSession(**data) if data else None

    @classmethod
    def get_history(cls) -> List[DesignSession]:
        """Get design history."""
        history = st.session_state.get(cls.HISTORY_KEY, [])
        return [DesignSession(**h) for h in history]

    @classmethod
    def export_session(cls, session: DesignSession) -> str:
        """Export session to JSON string."""
        return json.dumps(asdict(session), indent=2)

    @classmethod
    def import_session(cls, json_str: str) -> DesignSession:
        """Import session from JSON string."""
        data = json.loads(json_str)
        return DesignSession(**data)

    @classmethod
    def clear_history(cls):
        """Clear design history."""
        st.session_state[cls.HISTORY_KEY] = []
```

### Acceptance Criteria
- [ ] Inputs persist across page navigation
- [ ] Design history shows last 20 designs
- [ ] Export/import sessions as JSON
- [ ] Clear history option
- [ ] Tests for session manager

---

## 🟠 STREAMLIT-IMPL-011: Export Features (PDF/CSV/DXF) (Day 7-8)
**Priority:** 🟠 HIGH
**Status:** 🟡 TODO
**Estimated Effort:** 4-5 hours

### Objective
Add comprehensive export capabilities:
- PDF report with all design details
- CSV for data analysis
- DXF for CAD integration
- PNG/SVG for charts

### Implementation

```python
# streamlit_app/utils/exporters.py (~300 lines)

import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Image

class PDFExporter:
    """Generate PDF design reports."""

    def generate_report(self, design_data: dict) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)

        # Build report content
        story = []
        story.append(Paragraph("IS 456 Beam Design Report", title_style))
        story.append(Paragraph(f"Generated: {datetime.now()}", subtitle_style))

        # Input summary table
        story.append(Paragraph("Input Parameters", heading_style))
        input_table = Table([
            ["Width (b)", f"{design_data['b']} mm"],
            ["Depth (D)", f"{design_data['D']} mm"],
            # ...
        ])
        story.append(input_table)

        # Results section
        story.append(Paragraph("Design Results", heading_style))
        # ...

        doc.build(story)
        return buffer.getvalue()


class CSVExporter:
    """Export design data to CSV."""

    def export_design(self, design_data: dict) -> str:
        # Generate CSV content
        pass


class DXFExporter:
    """Export beam cross-section to DXF."""

    def export_section(self, b, D, rebars) -> bytes:
        # Generate DXF using ezdxf
        pass
```

### Acceptance Criteria
- [ ] PDF report with inputs, results, diagrams
- [ ] CSV export for comparison table
- [ ] DXF export for beam cross-section
- [ ] PNG/SVG export for individual charts
- [ ] Download buttons work correctly

---

## 🟠 STREAMLIT-IMPL-012: Settings & Configuration Page (Day 9-10)
**Priority:** 🟠 HIGH
**Status:** 🟡 TODO
**Estimated Effort:** 3-4 hours

### Objective
Create settings page for user preferences:
- Unit system (SI/Imperial)
- Default material grades
- Display preferences (theme, decimal places)
- Safety factors

### Implementation

```python
# streamlit_app/pages/05_⚙️_settings.py (~250 lines)

import streamlit as st

st.set_page_config(page_title="Settings", page_icon="⚙️")

st.title("⚙️ Settings")

# Initialize defaults
if "settings" not in st.session_state:
    st.session_state.settings = {
        "units": "SI",
        "decimal_places": 2,
        "default_fck": 25,
        "default_fy": 415,
        "partial_safety_concrete": 1.5,
        "partial_safety_steel": 1.15,
    }

settings = st.session_state.settings

# Units
st.subheader("🔢 Units")
settings["units"] = st.radio("Unit System", ["SI (mm, N, kN·m)", "Imperial (in, lb, kip·ft)"])

# Display
st.subheader("🖥️ Display")
settings["decimal_places"] = st.slider("Decimal Places", 0, 4, settings["decimal_places"])

# Defaults
st.subheader("🏗️ Default Materials")
col1, col2 = st.columns(2)
with col1:
    settings["default_fck"] = st.selectbox("Default Concrete", [20, 25, 30, 35, 40])
with col2:
    settings["default_fy"] = st.selectbox("Default Steel", [250, 415, 500, 550])

# Safety Factors
st.subheader("🛡️ Safety Factors")
st.caption("Per IS 456 Table 18")
col1, col2 = st.columns(2)
with col1:
    settings["partial_safety_concrete"] = st.number_input("γc (concrete)", value=1.5, disabled=True)
with col2:
    settings["partial_safety_steel"] = st.number_input("γs (steel)", value=1.15, disabled=True)

# Save
if st.button("💾 Save Settings"):
    st.session_state.settings = settings
    st.success("✅ Settings saved!")
```

### Acceptance Criteria
- [ ] Settings persist across sessions
- [ ] Default values applied to input forms
- [ ] Reset to defaults option
- [ ] Export/import settings

---

## 🟠 STREAMLIT-IMPL-013: About & Help System (Day 11-12)
**Priority:** 🟠 HIGH
**Status:** 🟡 TODO
**Estimated Effort:** 3-4 hours

### Objective
Create about page and contextual help:
- App version and credits
- Contact/feedback form
- Contextual help tooltips
- Keyboard shortcuts

---

## 📅 Extended Timeline Summary

| Day | Phase | Task | Deliverables |
|-----|-------|------|--------------|
| 1-2 | IMPL-008 | Documentation Page | 600+ lines, searchable guide |
| 3-4 | IMPL-009 | Error Handling | Centralized handler, 150+ lines |
| 5-6 | IMPL-010 | Session Management | Persistence, history, 200+ lines |
| 7-8 | IMPL-011 | Export Features | PDF/CSV/DXF, 300+ lines |
| 9-10 | IMPL-012 | Settings Page | Configuration UI, 250+ lines |
| 11-12 | IMPL-013 | About & Help | Credits, tooltips, 150+ lines |
| 13-14 | IMPL-014 | Performance | Caching optimization |
| 15-16 | IMPL-015 | Accessibility | WCAG 2.1 AA audit |
| 17-18 | IMPL-016 | E2E Tests | Playwright integration |
| 19-20 | IMPL-017 | Mobile | Responsive layout |

**Total Expected Output:**
- ~2,500+ lines of new code
- 100+ tests
- Full production-ready quality
- Complete feature set for professional use

---

## 🔴 PHASE 5: STREAMLIT-IMPL-005 - Cost Optimizer Page (Day 1-2)
**Priority:** 🔴 CRITICAL
- Searchable clause lookup
- Step-by-step user guide
- FAQ section
- Formula explanations

### Page Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ 📚 Documentation - IS 456 Reference & User Guide                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ [🔍 Search: _______________]                                        │
│                                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 📖 QUICK NAVIGATION                                             │ │
│ │ [Getting Started] [IS 456 Clauses] [Formulas] [FAQ] [Glossary] │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🚀 GETTING STARTED                                               │ │
│ │                                                                  │ │
│ │ **Step 1: Enter Geometry**                                       │ │
│ │ - Width (b): 150-600mm for typical beams                        │ │
│ │ - Depth (D): Usually L/10 to L/15 for initial sizing            │ │
│ │                                                                  │ │
│ │ **Step 2: Select Materials**                                     │ │
│ │ - Concrete: M20 for residential, M25-M30 for commercial         │ │
│ │ - Steel: Fe415 (most common), Fe500 for high-strength           │ │
│ │                                                                  │ │
│ │ **Step 3: Enter Loads**                                          │ │
│ │ - Moment (Mu): From structural analysis                          │ │
│ │ - Shear (Vu): Typically Mu/L for simply supported               │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 📋 IS 456 CLAUSE REFERENCE                                       │ │
│ │                                                                  │ │
│ │ ▼ Flexure Requirements                                           │ │
│ │ ├─ Cl. 26.5.1.1 - Minimum Steel Ratio                           │ │
│ │ │   Formula: pt_min = 0.85 * sqrt(fck) / fy                     │ │
│ │ │   Example: For M20, Fe415: pt_min = 0.85%                      │ │
│ │ │                                                               │ │
│ │ ├─ Cl. 26.5.1.2 - Maximum Steel Ratio                           │ │
│ │ │   Limit: pt_max = 4.0% (to ensure ductile failure)            │ │
│ │ │                                                               │ │
│ │ ▼ Shear Requirements                                             │ │
│ │ ├─ Cl. 40.1 - Shear Stress Check                                │ │
│ │ │   Formula: τv = Vu / (b × d)                                  │ │
│ │ │   Must satisfy: τv ≤ τc + τs                                  │ │
│ │ │                                                               │ │
│ │ ▼ Detailing Requirements                                         │ │
│ │ ├─ Cl. 26.3.3 - Bar Spacing                                     │ │
│ │ ├─ Cl. 26.4.1 - Cover Requirements                              │ │
│ │ │                                                               │ │
│ │ ▼ Serviceability                                                 │ │
│ │ ├─ Cl. 23.2.1 - Deflection Limits                               │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ ❓ FREQUENTLY ASKED QUESTIONS                                    │ │
│ │                                                                  │ │
│ │ Q: What concrete grade should I use?                             │ │
│ │ A: M20 for residential (up to 3 floors), M25 for commercial...  │ │
│ │                                                                  │ │
│ │ Q: How do I determine the initial beam depth?                    │ │
│ │ A: Start with D = L/12 for simply supported, L/15 for continuous│ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Implementation

```python
# streamlit_app/pages/04_📚_documentation.py

import streamlit as st

st.set_page_config(
    page_title="Documentation - IS 456 Reference",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Documentation")
st.markdown("IS 456:2000 Reference Guide and User Manual")

# Search functionality
search_query = st.text_input("🔍 Search documentation...", "")

# Navigation tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚀 Getting Started",
    "📋 IS 456 Clauses",
    "📐 Formulas",
    "❓ FAQ",
    "📖 Glossary"
])

with tab1:
    st.header("Getting Started Guide")

    st.subheader("Step 1: Understanding Inputs")
    st.markdown("""
    **Geometry Inputs:**
    - **Width (b):** 150-600mm typical for RC beams
    - **Total Depth (D):** Usually span/10 to span/15
    - **Effective Depth (d):** D minus cover minus half bar diameter

    **Material Selection:**
    | Grade | Use Case | fck (N/mm²) |
    |-------|----------|-------------|
    | M20 | Residential | 20 |
    | M25 | Commercial | 25 |
    | M30 | High-rise | 30 |
    """)

    st.subheader("Step 2: Interpreting Results")
    # ... more content

with tab2:
    st.header("IS 456:2000 Clause Reference")

    # Expandable sections for each clause category
    with st.expander("📏 Flexure Requirements", expanded=True):
        st.markdown("""
        ### Cl. 26.5.1.1 - Minimum Steel Ratio

        **Formula:**
        $$p_{t,min} = \\frac{0.85 \\sqrt{f_{ck}}}{f_y}$$

        **Purpose:** Ensures ductile behavior and prevents sudden failure.

        **Typical Values:**
        | Concrete | Steel | pt_min |
        |----------|-------|--------|
        | M20 | Fe415 | 0.85% |
        | M25 | Fe500 | 0.76% |
        """)

    with st.expander("🛡️ Shear Requirements"):
        st.markdown("""
        ### Cl. 40.1 - Shear Strength

        **Check:** τv ≤ τc + τs

        Where:
        - τv = Vu / (b × d) — Applied shear stress
        - τc = From Table 19 — Concrete shear capacity
        - τs = From stirrups — Steel shear capacity
        """)

# ... more tabs
```

### Files to Create/Modify
1. `streamlit_app/pages/04_📚_documentation.py` (~600 lines)
2. `streamlit_app/data/is456_clauses.json` - Clause database (~200 lines)
3. `streamlit_app/data/faq.json` - FAQ content (~100 lines)

### Acceptance Criteria
- [ ] Search filters content dynamically
- [ ] All major IS 456 clauses documented (at least 15)
- [ ] Formulas rendered with MathJax/KaTeX
- [ ] FAQ has at least 10 common questions
- [ ] Glossary has at least 30 terms
- [ ] Mobile-responsive

---

## 🟠 STREAMLIT-IMPL-009: Error Handling & Validation (Day 5-6)
**Priority:** 🟠 HIGH
**Status:** 🟡 TODO
**Estimated Effort:** 3-4 hours

### Objective
Implement comprehensive error handling and input validation across all pages:
- User-friendly error messages
- Input validation with suggestions
- Graceful degradation
- Error logging

### Implementation Areas

#### 1. Create Centralized Error Handler
```python
# streamlit_app/utils/error_handler.py

import streamlit as st
from typing import Optional
import traceback

class DesignError(Exception):
    """Custom error for design calculations."""
    def __init__(self, message: str, clause: Optional[str] = None, suggestion: Optional[str] = None):
        self.message = message
        self.clause = clause
        self.suggestion = suggestion
        super().__init__(message)

def display_error(error: Exception, context: str = ""):
    """Display user-friendly error message."""
    if isinstance(error, DesignError):
        st.error(f"❌ **Design Error:** {error.message}")
        if error.clause:
            st.caption(f"Reference: IS 456 {error.clause}")
        if error.suggestion:
            st.info(f"💡 **Suggestion:** {error.suggestion}")
    else:
        st.error(f"❌ **Unexpected Error:** {str(error)}")
        with st.expander("🔍 Technical Details"):
            st.code(traceback.format_exc())

def validate_beam_geometry(b_mm: float, D_mm: float, d_mm: float) -> list[str]:
    """Validate beam geometry and return list of warnings/errors."""
    issues = []

    if d_mm >= D_mm:
        issues.append("❌ Effective depth (d) must be less than total depth (D)")

    if b_mm > D_mm:
        issues.append("⚠️ Width greater than depth is unusual for beams")

    aspect_ratio = D_mm / b_mm
    if aspect_ratio > 4:
        issues.append(f"⚠️ Aspect ratio {aspect_ratio:.1f} is high. Consider increasing width.")

    return issues
```

#### 2. Apply to All Pages
```python
# In each page, wrap calculations:
try:
    result = cached_design(...)
except DesignError as e:
    display_error(e, context="Beam Design")
except Exception as e:
    display_error(e, context="Unexpected")
```

### Acceptance Criteria
- [ ] All pages have try/except blocks
- [ ] Custom DesignError class with clause references
- [ ] User-friendly error messages (no raw tracebacks)
- [ ] Input validation with warnings before errors
- [ ] Error logging to file (optional)

---

## 🟠 STREAMLIT-IMPL-010: Performance Optimization (Day 7-8)
**Priority:** 🟠 HIGH
**Status:** 🟡 TODO
**Estimated Effort:** 3-4 hours

### Objective
Optimize app performance for production:
- Efficient caching strategy
- Lazy loading for heavy components
- Memory management
- Load time < 3 seconds

### Implementation Areas

#### 1. Caching Strategy Review
```python
# Review all @st.cache_data decorators
# Ensure TTL is appropriate
# Add cache_resource for expensive objects

@st.cache_resource
def load_plotly_template():
    """Load custom Plotly template once."""
    return {...}

@st.cache_data(ttl=3600)  # 1 hour cache
def cached_design(...):
    ...
```

#### 2. Lazy Loading
```python
# Only import heavy modules when needed
def get_plotly():
    import plotly.graph_objects as go
    return go

# Use st.experimental_fragment for partial updates (if available)
```

#### 3. Memory Profiling
```python
# Add to utils/performance.py
import tracemalloc

def profile_memory():
    tracemalloc.start()
    # ... run code ...
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')[:10]
    return top_stats
```

### Acceptance Criteria
- [ ] Initial page load < 3 seconds
- [ ] Cached calls < 50ms
- [ ] No memory leaks on repeated use
- [ ] Bundle size documented

---

## 🟠 STREAMLIT-IMPL-011: Accessibility Audit & Fixes (Day 9-10)
**Priority:** 🟠 HIGH
**Status:** 🟡 TODO
**Estimated Effort:** 3-4 hours

### Objective
Ensure WCAG 2.1 Level AA compliance:
- Keyboard navigation
- Screen reader support
- Color contrast verification
- Focus indicators

### Checklist

#### Color Contrast (WCAG 1.4.3)
- [ ] All text has 4.5:1 contrast ratio
- [ ] Large text has 3:1 contrast ratio
- [ ] Focus indicators visible

#### Keyboard Navigation (WCAG 2.1.1)
- [ ] All interactive elements reachable via Tab
- [ ] No keyboard traps
- [ ] Skip links for navigation

#### Screen Reader (WCAG 1.1.1)
- [ ] All images have alt text
- [ ] Charts have text descriptions
- [ ] Form inputs have labels

### Implementation
```python
# Add accessibility attributes where possible
st.markdown("""
<div role="region" aria-label="Design Results">
    <!-- Results content -->
</div>
""", unsafe_allow_html=True)

# Add text descriptions for charts
st.caption("Chart shows cost comparison between 5 bar arrangements. 3-16mm is optimal at ₹87.45/m.")
```

---

## 🟠 STREAMLIT-IMPL-012: End-to-End Integration Tests (Day 11-12)
**Priority:** 🟠 HIGH
**Status:** 🟡 TODO
**Estimated Effort:** 4-5 hours

### Objective
Create comprehensive E2E tests using Selenium or Playwright:
- User flow testing
- Cross-browser compatibility
- Regression testing

### Test Scenarios

```python
# tests/e2e/test_user_flows.py

import pytest
from playwright.sync_api import Page

class TestBeamDesignFlow:
    def test_complete_design_workflow(self, page: Page):
        """Test complete beam design from input to results."""
        page.goto("http://localhost:8501")

        # Navigate to Beam Design
        page.click("text=🏗️ Beam Design")

        # Enter inputs
        page.fill('[data-testid="width_input"]', "300")
        page.fill('[data-testid="depth_input"]', "500")
        page.fill('[data-testid="moment_input"]', "120")

        # Click Analyze
        page.click("text=🚀 Analyze")

        # Verify results appear
        assert page.locator("text=Design Summary").is_visible()
        assert page.locator("text=✅").count() >= 1

    def test_cost_optimizer_flow(self, page: Page):
        """Test cost optimization workflow."""
        # ... test steps
```

### Files to Create
1. `tests/e2e/conftest.py` - Playwright fixtures
2. `tests/e2e/test_user_flows.py` - User flow tests (~300 lines)
3. `tests/e2e/test_cross_browser.py` - Browser compatibility (~100 lines)

---

## 📅 Extended Timeline Summary

| Day | Phase | Task | Deliverables |
|-----|-------|------|--------------|
| 1-2 | FIX-001 | Fix Failing Tests | 44 tests fixed, 81/81 passing |
| 3-4 | IMPL-008 | Documentation Page | 600+ lines, searchable guide |
| 5-6 | IMPL-009 | Error Handling | Centralized error handler |
| 7-8 | IMPL-010 | Performance | < 3s load, caching optimized |
| 9-10 | IMPL-011 | Accessibility | WCAG 2.1 AA compliance |
| 11-12 | IMPL-012 | E2E Tests | Playwright tests, CI integration |

**Total Expected Output:**
- ~2,000+ lines of new/fixed code
- 81+ passing tests (up from 37)
- 100% test pass rate
- Production-ready quality

## 🔴 PHASE 5: STREAMLIT-IMPL-005 - Cost Optimizer Page (Day 1-2)
**Priority:** 🔴 CRITICAL
**Status:** 🟡 TODO - START IMMEDIATELY
**Estimated Effort:** 3-4 hours

### Objective
Create a dedicated Cost Optimizer page that allows engineers to:
- Compare multiple rebar arrangements side-by-side
- Visualize cost vs utilization trade-offs
- Export comparison data for reports
- Load designs from Beam Design page

### Page Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ 💰 Cost Optimizer - Find the Most Economical Design                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 📊 LOAD FROM BEAM DESIGN                                        │ │
│ │ [Load Current Design] or [Enter New Parameters]                 │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 💡 OPTIMIZATION SUMMARY                                         │ │
│ │ ┌───────────┬───────────┬───────────┬───────────┐              │ │
│ │ │ Optimal   │ Savings   │ Utilization│ Options  │              │ │
│ │ │ 3-16mm    │ ₹4.85/m   │ 92%        │ 5 shown  │              │ │
│ │ └───────────┴───────────┴───────────┴───────────┘              │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 📈 COST vs UTILIZATION SCATTER PLOT                             │ │
│ │                                                                  │ │
│ │        ●                 (hover for details)                    │ │
│ │     💚 ○ 3-16mm (OPTIMAL)                                       │ │
│ │        ○ ○                                                      │ │
│ │     ○                                                           │ │
│ │  ─────┼─────┼─────┼─────┼─────→ Utilization (%)                │ │
│ │      70%   80%   90%  100%                                      │ │
│ │  Cost ↑                                                         │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 📋 COMPARISON TABLE                                              │ │
│ │ ┌────────────┬────────┬───────┬────────┬────────┬───────────┐  │ │
│ │ │ Arrange    │ Area   │ Util% │ Cost   │ Saving │ Status    │  │ │
│ │ ├────────────┼────────┼───────┼────────┼────────┼───────────┤  │ │
│ │ │ 3-16mm ⭐  │ 603mm² │ 92%   │ ₹87.45 │ BASE   │ ✅ OPTIMAL │  │ │
│ │ │ 2-20mm     │ 628mm² │ 96%   │ ₹92.30 │ -₹4.85 │ ✅ OK      │  │ │
│ │ │ 4-14mm     │ 616mm² │ 94%   │ ₹89.50 │ -₹2.05 │ ✅ OK      │  │ │
│ │ │ 2-16+1-12  │ 515mm² │ 78%   │ ₹75.20 │ +₹12.25│ ⚠️ UNDER   │  │ │
│ │ └────────────┴────────┴───────┴────────┴────────┴───────────┘  │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ [📥 Export CSV] [📄 Export PDF] [🖨️ Print]                          │
└─────────────────────────────────────────────────────────────────────┘
```

### Implementation Details

```python
# streamlit_app/pages/02_💰_cost_optimizer.py

import streamlit as st
import pandas as pd
import plotly.express as px
from components.visualizations import create_cost_comparison
from utils.api_wrapper import get_rebar_options

st.set_page_config(
    page_title="Cost Optimizer | IS 456 Dashboard",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Cost Optimizer")
st.markdown("Find the most economical rebar arrangement for your design")

# ── Load from Beam Design ──
col1, col2 = st.columns([3, 1])
with col1:
    if st.button("📊 Load from Beam Design", use_container_width=True):
        if 'beam_inputs' in st.session_state:
            st.session_state.optimizer_inputs = st.session_state.beam_inputs
            st.success("✅ Loaded design from Beam Design page")
        else:
            st.warning("⚠️ No design found. Complete Beam Design first.")

with col2:
    st.button("🔄 Clear", use_container_width=True)

# ── Get Options ──
if 'optimizer_inputs' in st.session_state:
    inputs = st.session_state.optimizer_inputs

    with st.spinner("🔄 Finding optimal arrangements..."):
        options = get_rebar_options(
            ast_required=inputs.get('ast_required', 600),
            b_mm=inputs.get('b_mm', 230),
            d_mm=inputs.get('d_mm', 400)
        )

    # ── Summary Metrics ──
    st.subheader("💡 Optimization Summary")
    optimal = [o for o in options if o.get('is_optimal')][0]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Optimal Choice", optimal['name'])
    m2.metric("Cost per Meter", f"₹{optimal['cost']:.2f}")
    m3.metric("Utilization", f"{optimal['utilization']*100:.0f}%")
    m4.metric("Options Analyzed", len(options))

    # ── Scatter Plot ──
    st.subheader("📈 Cost vs Utilization")

    df = pd.DataFrame(options)
    fig = px.scatter(
        df,
        x='utilization',
        y='cost',
        text='name',
        color='is_optimal',
        color_discrete_map={True: '#28A745', False: '#6C9BD1'},
        size='area',
        hover_data=['area', 'status']
    )
    fig.update_layout(
        xaxis_title="Utilization (%)",
        yaxis_title="Cost (₹/m)",
        showlegend=False
    )
    fig.update_traces(textposition='top center')
    st.plotly_chart(fig, use_container_width=True)

    # ── Comparison Table ──
    st.subheader("📋 Comparison Table")

    # Format DataFrame for display
    display_df = df[['name', 'area', 'utilization', 'cost', 'savings', 'status']].copy()
    display_df.columns = ['Arrangement', 'Area (mm²)', 'Utilization', 'Cost (₹/m)', 'Savings', 'Status']
    display_df['Utilization'] = display_df['Utilization'].apply(lambda x: f"{x*100:.0f}%")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Arrangement': st.column_config.TextColumn(width='medium'),
            'Status': st.column_config.TextColumn(width='small'),
        }
    )

    # ── Export Options ──
    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        csv = display_df.to_csv(index=False)
        st.download_button(
            "📥 Export CSV",
            csv,
            "cost_comparison.csv",
            "text/csv",
            use_container_width=True
        )

    with col2:
        st.button("📄 Export PDF", use_container_width=True, disabled=True)
        st.caption("Coming soon")

    with col3:
        if st.button("🖨️ Print", use_container_width=True):
            st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

else:
    st.info("👈 Load a design from the Beam Design page or enter parameters below")

    # Manual input fallback
    with st.expander("📝 Enter Parameters Manually"):
        ast = st.number_input("Steel Area Required (mm²)", 200, 2000, 600)
        b = st.number_input("Width (mm)", 150, 600, 230)
        d = st.number_input("Effective Depth (mm)", 200, 800, 400)

        if st.button("Find Options"):
            st.session_state.optimizer_inputs = {'ast_required': ast, 'b_mm': b, 'd_mm': d}
            st.rerun()
```

### API Wrapper Addition

```python
# Add to streamlit_app/utils/api_wrapper.py

@st.cache_data
def get_rebar_options(
    ast_required: float,
    b_mm: float,
    d_mm: float
) -> list[dict]:
    """
    Get list of rebar arrangement options sorted by cost.

    Returns list of dicts with: name, area, cost, utilization, savings, status, is_optimal
    """
    # TODO: Integrate with rebar_optimizer module
    # from structural_lib.rebar_optimizer import get_all_options

    # Placeholder data
    base_cost = 87.45
    return [
        {"name": "3-16mm", "area": 603, "cost": base_cost, "utilization": 0.92,
         "savings": 0, "status": "✅ OPTIMAL", "is_optimal": True},
        {"name": "2-20mm", "area": 628, "cost": 92.30, "utilization": 0.96,
         "savings": -4.85, "status": "✅ OK", "is_optimal": False},
        {"name": "4-14mm", "area": 616, "cost": 89.50, "utilization": 0.94,
         "savings": -2.05, "status": "✅ OK", "is_optimal": False},
        {"name": "2-16mm+1-12mm", "area": 515, "cost": 75.20, "utilization": 0.78,
         "savings": 12.25, "status": "⚠️ UNDER", "is_optimal": False},
        {"name": "5-12mm", "area": 565, "cost": 82.00, "utilization": 0.86,
         "savings": 5.45, "status": "✅ OK", "is_optimal": False},
    ]
```

### Acceptance Criteria

- [ ] Page loads without errors
- [ ] "Load from Beam Design" works with session state
- [ ] Manual input fallback works
- [ ] Scatter plot is interactive (hover, zoom)
- [ ] Table is sortable
- [ ] CSV export downloads correctly
- [ ] Optimal option highlighted in green
- [ ] Under-designed options show warning
- [ ] Responsive design (mobile-friendly)
- [ ] Print button triggers print dialog

### Files to Create/Modify

1. `streamlit_app/pages/02_💰_cost_optimizer.py` (~400 lines)
2. `streamlit_app/utils/api_wrapper.py` - Add `get_rebar_options()` (~50 lines)

---

## 🔴 PHASE 6: STREAMLIT-IMPL-006 - Compliance Checker Page (Day 3-4)
**Priority:** 🔴 CRITICAL
**Status:** 🟡 TODO - AFTER IMPL-005
**Estimated Effort:** 3-4 hours

### Objective
Create a dedicated Compliance Checker page for comprehensive IS 456 verification:
- Check all relevant IS 456 clauses
- Show pass/fail with expandable details
- Display margin of safety for each check
- Generate compliance certificate

### Page Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ ✅ Compliance Checker - IS 456:2000 Verification                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🎯 OVERALL STATUS                                               │ │
│ │ ┌───────────────────────────────────────────────────────────┐  │ │
│ │ │  ✅ COMPLIANT  │  12/12 checks passed  │  Min margin: 8%  │  │ │
│ │ └───────────────────────────────────────────────────────────┘  │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 📋 DETAILED CHECKS                                              │ │
│ │                                                                  │ │
│ │ ▼ FLEXURE REQUIREMENTS                                          │ │
│ │ ├─ ✅ Cl. 26.5.1.1 - Minimum Steel Ratio      Margin: +8.2%    │ │
│ │ │   └─ Required: pt ≥ 0.85√fck/fy = 0.85%                      │ │
│ │ │   └─ Provided: pt = 0.92%                                     │ │
│ │ │   └─ Status: PASS (margin = 8.2%)                            │ │
│ │ │                                                               │ │
│ │ ├─ ✅ Cl. 26.5.1.2 - Maximum Steel Ratio      Margin: +77%     │ │
│ │ │   └─ Required: pt ≤ 4.0%                                      │ │
│ │ │   └─ Provided: pt = 0.92%                                     │ │
│ │ │                                                               │ │
│ │ ▼ SHEAR REQUIREMENTS                                            │ │
│ │ ├─ ✅ Cl. 40.1 - Shear Capacity               Margin: +51%     │ │
│ │ │   └─ τv = 0.45 N/mm² ≤ τc + τs = 0.68 N/mm²                  │ │
│ │ │                                                               │ │
│ │ ├─ ✅ Cl. 40.2.3 - Min Shear Reinforcement    Margin: +120%    │ │
│ │ │   └─ Asv/sv ≥ 0.4/(0.87*fy)                                  │ │
│ │ │                                                               │ │
│ │ ▼ DETAILING REQUIREMENTS                                        │ │
│ │ ├─ ✅ Cl. 26.3.3 - Bar Spacing                Margin: +25%     │ │
│ │ ├─ ✅ Cl. 26.4.1 - Cover Requirements         Margin: +33%     │ │
│ │ ├─ ✅ Cl. 40.4 - Max Stirrup Spacing          Margin: +30%     │ │
│ │ │                                                               │ │
│ │ ▼ SERVICEABILITY                                                │ │
│ │ ├─ ✅ Cl. 23.2.1 - Deflection Limits          Margin: +22%     │ │
│ │ ├─ ✅ Cl. 35.1.1 - Cracking Control           Margin: +10%     │ │
│ │ │                                                               │ │
│ │ ▼ DURABILITY                                                    │ │
│ │ ├─ ✅ Cl. 26.4.2 - Fire Resistance Cover      Margin: +50%     │ │
│ │ └─────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ [📜 Generate Certificate] [📥 Export PDF] [🖨️ Print]                │
└─────────────────────────────────────────────────────────────────────┘
```

### Implementation Details

```python
# streamlit_app/pages/03_✅_compliance.py

import streamlit as st
from typing import Dict, List

st.set_page_config(
    page_title="Compliance Checker | IS 456 Dashboard",
    page_icon="✅",
    layout="wide"
)

st.title("✅ Compliance Checker")
st.markdown("Verify your design against **IS 456:2000** requirements")

# Compliance check categories
COMPLIANCE_CATEGORIES = {
    "FLEXURE": [
        {
            "clause": "26.5.1.1",
            "name": "Minimum Steel Ratio",
            "formula": "pt ≥ 0.85√fck/fy",
            "check_fn": lambda d: d['pt_provided'] >= d['pt_min'],
            "margin_fn": lambda d: (d['pt_provided'] - d['pt_min']) / d['pt_min'] * 100
        },
        {
            "clause": "26.5.1.2",
            "name": "Maximum Steel Ratio",
            "formula": "pt ≤ 4.0%",
            "check_fn": lambda d: d['pt_provided'] <= 4.0,
            "margin_fn": lambda d: (4.0 - d['pt_provided']) / 4.0 * 100
        },
    ],
    "SHEAR": [
        {
            "clause": "40.1",
            "name": "Shear Capacity",
            "formula": "τv ≤ τc + τs",
            "check_fn": lambda d: d['tau_v'] <= d['tau_c'] + d['tau_s'],
            "margin_fn": lambda d: ((d['tau_c'] + d['tau_s']) - d['tau_v']) / d['tau_v'] * 100
        },
        {
            "clause": "40.2.3",
            "name": "Minimum Shear Reinforcement",
            "formula": "Asv/sv ≥ 0.4/(0.87*fy)",
            "check_fn": lambda d: d['asv_sv'] >= d['asv_sv_min'],
            "margin_fn": lambda d: (d['asv_sv'] - d['asv_sv_min']) / d['asv_sv_min'] * 100
        },
    ],
    "DETAILING": [
        {
            "clause": "26.3.3",
            "name": "Bar Spacing",
            "formula": "spacing ≥ max(bar_dia, 25mm)",
            "check_fn": lambda d: d['spacing'] >= d['min_spacing'],
            "margin_fn": lambda d: (d['spacing'] - d['min_spacing']) / d['min_spacing'] * 100
        },
        {
            "clause": "26.4.1",
            "name": "Cover Requirements",
            "formula": "cover ≥ nominal_cover",
            "check_fn": lambda d: d['cover'] >= d['min_cover'],
            "margin_fn": lambda d: (d['cover'] - d['min_cover']) / d['min_cover'] * 100
        },
    ],
    "SERVICEABILITY": [
        {
            "clause": "23.2.1",
            "name": "Deflection Limits",
            "formula": "L/d ≤ basic_ratio × factors",
            "check_fn": lambda d: d['ld_ratio'] <= d['ld_limit'],
            "margin_fn": lambda d: (d['ld_limit'] - d['ld_ratio']) / d['ld_limit'] * 100
        },
    ],
}


def render_compliance_category(category: str, checks: List[Dict], design_data: Dict):
    """Render an expandable category of compliance checks."""
    with st.expander(f"{'▼' if True else '▶'} {category} REQUIREMENTS", expanded=True):
        for check in checks:
            passed = check['check_fn'](design_data)
            margin = check['margin_fn'](design_data)

            icon = "✅" if passed else "❌"
            color = "green" if passed else "red"

            col1, col2, col3 = st.columns([4, 2, 1])

            with col1:
                st.markdown(f"**{icon} Cl. {check['clause']}** - {check['name']}")

            with col2:
                st.markdown(f"Margin: **{margin:+.1f}%**")

            with col3:
                if not passed:
                    st.error("FAIL")

            # Expandable details
            with st.container():
                st.caption(f"Formula: `{check['formula']}`")


# ── Load Design Data ──
if 'beam_result' in st.session_state:
    result = st.session_state.beam_result

    # Extract data for checks
    design_data = {
        'pt_provided': result.get('pt', 0.92),
        'pt_min': 0.85,
        'tau_v': result.get('tau_v', 0.45),
        'tau_c': result.get('tau_c', 0.48),
        'tau_s': result.get('tau_s', 0.20),
        'asv_sv': result.get('asv_sv', 0.35),
        'asv_sv_min': result.get('asv_sv_min', 0.16),
        'spacing': result.get('bar_spacing', 50),
        'min_spacing': result.get('min_spacing', 40),
        'cover': result.get('cover', 40),
        'min_cover': result.get('min_cover', 30),
        'ld_ratio': result.get('ld_ratio', 18),
        'ld_limit': result.get('ld_limit', 23),
    }

    # Calculate overall status
    all_checks = []
    for category, checks in COMPLIANCE_CATEGORIES.items():
        for check in checks:
            all_checks.append({
                'passed': check['check_fn'](design_data),
                'margin': check['margin_fn'](design_data)
            })

    passed_count = sum(1 for c in all_checks if c['passed'])
    total_count = len(all_checks)
    min_margin = min(c['margin'] for c in all_checks)

    # ── Overall Status ──
    st.subheader("🎯 Overall Status")

    if passed_count == total_count:
        st.success(f"✅ **COMPLIANT** | {passed_count}/{total_count} checks passed | Min margin: {min_margin:.1f}%")
    else:
        st.error(f"❌ **NON-COMPLIANT** | {passed_count}/{total_count} checks passed")

    # ── Detailed Checks ──
    st.subheader("📋 Detailed Checks")

    for category, checks in COMPLIANCE_CATEGORIES.items():
        render_compliance_category(category, checks, design_data)

    # ── Export Options ──
    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📜 Generate Certificate", use_container_width=True):
            st.balloons()
            st.success("Certificate generated!")

    with col2:
        st.button("📥 Export PDF", use_container_width=True, disabled=True)

    with col3:
        st.button("🖨️ Print", use_container_width=True)

else:
    st.info("👈 Complete a design in the Beam Design page first")
```

### Acceptance Criteria

- [ ] Page loads without errors
- [ ] All 12 IS 456 clauses checked
- [ ] Pass/fail status clearly visible
- [ ] Margins calculated correctly
- [ ] Expandable sections work
- [ ] Certificate generation button works
- [ ] Session state integration works
- [ ] Color coding: green=pass, red=fail, yellow=marginal

### Files to Create/Modify

1. `streamlit_app/pages/03_✅_compliance.py` (~400 lines)
2. `streamlit_app/utils/compliance_checker.py` - Reusable check logic (~100 lines)

---

## 🔴 PHASE 7: STREAMLIT-IMPL-007 - Visualization Tests + Integration (Day 5-6)
**Priority:** 🔴 CRITICAL
**Status:** 🟡 TODO - AFTER IMPL-006
**Estimated Effort:** 2-3 hours

### Objective
Create comprehensive test suite for:
- All 5 visualization components
- API wrapper functions
- Page integration tests
- Accessibility checks

### Test Structure

```python
# streamlit_app/tests/test_visualizations.py

import pytest
import plotly.graph_objects as go
from components.visualizations import (
    create_beam_diagram,
    create_cost_comparison,
    create_utilization_gauge,
    create_sensitivity_tornado,
    create_compliance_visual
)


class TestBeamDiagram:
    """Tests for beam cross-section visualization."""

    @pytest.fixture
    def sample_inputs(self):
        return {
            'b_mm': 230,
            'D_mm': 450,
            'd_mm': 400,
            'rebar_positions': [(50, 50), (115, 50), (180, 50)],
            'xu': 120,
            'bar_dia': 16,
            'cover': 30
        }

    def test_returns_plotly_figure(self, sample_inputs):
        """Test function returns Plotly Figure object."""
        fig = create_beam_diagram(**sample_inputs)
        assert isinstance(fig, go.Figure)

    def test_has_concrete_shape(self, sample_inputs):
        """Test figure contains concrete rectangle."""
        fig = create_beam_diagram(**sample_inputs)
        shapes = fig.layout.shapes
        assert len(shapes) >= 1
        assert any(s.type == 'rect' for s in shapes)

    def test_has_rebar_circles(self, sample_inputs):
        """Test figure contains rebar circles."""
        fig = create_beam_diagram(**sample_inputs)
        shapes = fig.layout.shapes
        circles = [s for s in shapes if s.type == 'circle']
        assert len(circles) == 3  # 3 rebars

    def test_neutral_axis_shown(self, sample_inputs):
        """Test neutral axis line is visible."""
        fig = create_beam_diagram(**sample_inputs)
        shapes = fig.layout.shapes
        lines = [s for s in shapes if s.type == 'line']
        assert len(lines) >= 1

    def test_dimensions_annotated(self, sample_inputs):
        """Test dimension annotations are present."""
        fig = create_beam_diagram(**sample_inputs)
        annotations = fig.layout.annotations
        assert len(annotations) >= 2  # At least b and D

    def test_aspect_ratio_correct(self, sample_inputs):
        """Test figure maintains 1:1 aspect ratio."""
        fig = create_beam_diagram(**sample_inputs)
        # Check scaleanchor is set
        assert fig.layout.yaxis.scaleanchor == 'x'


class TestCostComparison:
    """Tests for cost comparison bar chart."""

    @pytest.fixture
    def sample_options(self):
        return [
            {"name": "3-16mm", "cost": 87.45, "is_optimal": True, "utilization": 0.92},
            {"name": "2-20mm", "cost": 92.30, "is_optimal": False, "utilization": 0.96},
        ]

    def test_returns_plotly_figure(self, sample_options):
        """Test function returns Plotly Figure."""
        fig = create_cost_comparison(sample_options)
        assert isinstance(fig, go.Figure)

    def test_bar_count_matches_options(self, sample_options):
        """Test number of bars matches input options."""
        fig = create_cost_comparison(sample_options)
        assert len(fig.data) >= 1
        assert len(fig.data[0].x) == 2

    def test_optimal_is_green(self, sample_options):
        """Test optimal option has green color."""
        fig = create_cost_comparison(sample_options)
        colors = fig.data[0].marker.color
        assert '#28A745' in colors or 'green' in str(colors).lower()

    def test_cost_labels_shown(self, sample_options):
        """Test cost labels appear on bars."""
        fig = create_cost_comparison(sample_options)
        assert fig.data[0].text is not None


class TestUtilizationGauge:
    """Tests for utilization gauge."""

    def test_returns_plotly_figure(self):
        """Test function returns Plotly Figure."""
        fig = create_utilization_gauge(0.85, "Test")
        assert isinstance(fig, go.Figure)

    def test_value_displayed(self):
        """Test value is displayed in gauge."""
        fig = create_utilization_gauge(0.85, "Test")
        indicator = fig.data[0]
        assert indicator.value == 85

    def test_color_zones_exist(self):
        """Test gauge has colored zones."""
        fig = create_utilization_gauge(0.85, "Test")
        gauge = fig.data[0].gauge
        assert len(gauge.steps) >= 2

    def test_over_100_handled(self):
        """Test values over 100% are handled."""
        fig = create_utilization_gauge(1.2, "Test")
        # Should not raise error
        assert fig is not None


class TestSensitivityTornado:
    """Tests for tornado diagram."""

    @pytest.fixture
    def sample_data(self):
        return [
            {"param": "Moment", "low": -15, "high": 18},
            {"param": "Depth", "low": -10, "high": 12},
        ]

    def test_returns_plotly_figure(self, sample_data):
        """Test function returns Plotly Figure."""
        fig = create_sensitivity_tornado(sample_data)
        assert isinstance(fig, go.Figure)

    def test_sorted_by_impact(self, sample_data):
        """Test parameters sorted by total impact."""
        fig = create_sensitivity_tornado(sample_data)
        # First parameter should have highest impact
        y_values = fig.data[0].y
        assert y_values[0] == "Moment"  # |−15|+|18| = 33 > |−10|+|12| = 22


class TestComplianceVisual:
    """Tests for compliance checklist visualization."""

    @pytest.fixture
    def sample_checks(self):
        return [
            {"clause": "26.5.1.1", "description": "Min steel", "passed": True, "value": "0.92%", "limit": "0.85%"},
            {"clause": "40.1", "description": "Shear", "passed": False, "value": "0.95", "limit": "0.80"},
        ]

    def test_returns_plotly_figure(self, sample_checks):
        """Test function returns Plotly Figure."""
        fig = create_compliance_visual(sample_checks)
        assert isinstance(fig, go.Figure)

    def test_all_checks_displayed(self, sample_checks):
        """Test all checks are shown."""
        fig = create_compliance_visual(sample_checks)
        annotations = fig.layout.annotations
        assert len(annotations) >= 2

    def test_pass_fail_colors(self, sample_checks):
        """Test passed checks are green, failed are red."""
        fig = create_compliance_visual(sample_checks)
        shapes = fig.layout.shapes
        colors = [s.fillcolor for s in shapes if hasattr(s, 'fillcolor')]
        assert any('#28A745' in str(c) for c in colors)  # Green for pass
        assert any('#DC3545' in str(c) for c in colors)  # Red for fail
```

### API Wrapper Tests

```python
# streamlit_app/tests/test_api_wrapper.py

import pytest
from utils.api_wrapper import cached_design, get_rebar_options


class TestCachedDesign:
    """Tests for cached design wrapper."""

    def test_returns_dict(self):
        """Test function returns dictionary."""
        result = cached_design(
            mu_knm=120, vu_kn=80, b_mm=300, D_mm=500,
            d_mm=450, fck_nmm2=25, fy_nmm2=500
        )
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        """Test result has expected keys."""
        result = cached_design(
            mu_knm=120, vu_kn=80, b_mm=300, D_mm=500,
            d_mm=450, fck_nmm2=25, fy_nmm2=500
        )
        assert 'flexure' in result
        assert 'shear' in result
        assert 'is_safe' in result


class TestGetRebarOptions:
    """Tests for rebar options function."""

    def test_returns_list(self):
        """Test function returns list."""
        options = get_rebar_options(600, 230, 400)
        assert isinstance(options, list)

    def test_has_optimal_option(self):
        """Test at least one option is marked optimal."""
        options = get_rebar_options(600, 230, 400)
        optimal = [o for o in options if o.get('is_optimal')]
        assert len(optimal) == 1

    def test_options_sorted_by_cost(self):
        """Test options are sorted by cost."""
        options = get_rebar_options(600, 230, 400)
        costs = [o['cost'] for o in options]
        # Optimal should be first or near first
```

### Acceptance Criteria

- [ ] 30+ unit tests written
- [ ] All tests pass (pytest)
- [ ] Coverage > 80% for visualization module
- [ ] Edge cases tested (empty data, extremes)
- [ ] Accessibility checks included
- [ ] Performance benchmarks added

### Files to Create

1. `streamlit_app/tests/test_visualizations.py` (~300 lines)
2. `streamlit_app/tests/test_api_wrapper.py` (~100 lines)
3. `streamlit_app/tests/test_pages.py` (~100 lines) - Optional page integration tests

---

## 📅 3-Phase Timeline Summary

| Day | Phase | Task | Deliverables |
|-----|-------|------|--------------|
| 1 | PHASE 5 | IMPL-005 Part 1 | Cost Optimizer layout, scatter plot |
| 2 | PHASE 5 | IMPL-005 Part 2 | Table, export, integration |
| 3 | PHASE 6 | IMPL-006 Part 1 | Compliance page layout, categories |
| 4 | PHASE 6 | IMPL-006 Part 2 | All checks, certificate |
| 5 | PHASE 7 | IMPL-007 Part 1 | Visualization tests (20+ tests) |
| 6 | PHASE 7 | IMPL-007 Part 2 | API + page tests (10+ tests) |

**Total Output Expected:**
- ~1,400 lines of new code
- 30+ new tests
- 2 complete pages
- Comprehensive test coverage

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
# (MAIN agent ensures main is up-to-date before handoff)
git checkout main

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

### Quality Gates (Non-Negotiable)

Every UI change must meet these before handoff:

1. **Runs cleanly**
   - `streamlit run streamlit_app/app.py` starts without errors.
   - No red exceptions in the browser or terminal.
2. **UI stays usable**
   - All inputs validate (no silent failures).
   - Errors are shown with actionable guidance.
3. **Docs updated**
   - Component usage documented in `streamlit_app/docs/` or `docs/ui/`.
4. **Tests (if present)**
   - Run targeted tests when added: `python -m pytest streamlit_app/tests -q`.

### Definition of Done (Per Component)
- Working UI with real library data (no placeholders).
- Validation + error state behavior verified.
- Component doc snippet added.
- Handoff note includes what changed + how to test.

### Phase Closeout Rule
At the end of each phase, produce a concise handoff summary:
- What shipped (components/pages)
- Files added/changed
- How to test
- Known gaps or follow-ups

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

## Ownership & Collaboration Rules

**Agent 6 owns:** `streamlit_app/` and `docs/ui/` only.
**MAIN owns:** merges, pushes, and changes to core library code.

**If a change needs core API updates:**
- Write a request to MAIN (see template above).
- Do not implement API changes yourself.

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
   # Start from clean main (MAIN agent ensures it's up-to-date)
   git checkout main

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

## ✅ STREAMLIT-IMPL-002: COMPLETED (2026-01-08)

**Deliverables:**
- 5 input components with real-time validation
- 4 IS 456 material databases
- 29 unit tests (100% passing)
- 690 lines of production code + tests

**Components Delivered:**
1. `dimension_input()` - Real-time validation with visual feedback
2. `material_selector()` - Concrete (M20-M40) & Steel (Fe415-Fe550)
3. `load_input()` - Moment & shear with ratio validation
4. `exposure_selector()` - 5 exposure conditions per IS 456 Table 16
5. `support_condition_selector()` - 4 support types with moment factors

---

## 🔴 STREAMLIT-IMPL-003: Visualizations (Day 6-10)
**Priority:** 🔴 CRITICAL
**Status:** 🟡 TODO - START IMMEDIATELY
**Estimated Effort:** 6-8 hours (1-2 hours/day over 5 days)

### Objective
Create 5 interactive Plotly visualization components for structural engineering data display. All charts must be:
- Interactive (hover tooltips, zoom, pan)
- Responsive (mobile-friendly)
- Accessible (WCAG 2.1 Level AA - colorblind-safe)
- Tested (unit tests + visual regression)

### Component Specifications

#### 1. Beam Cross-Section Diagram (`create_beam_diagram`)
**Purpose:** Visualize rectangular beam section with rebar placement

**Input Data:**
```python
@dataclass
class BeamVisualizationData:
    b_mm: float           # Width of beam
    D_mm: float           # Total depth
    d_mm: float           # Effective depth
    cover_mm: float       # Clear cover
    bar_diameter: int     # Main bar diameter (mm)
    num_bars: int         # Number of main bars
    stirrup_diameter: int # Stirrup diameter (mm)
    xu_mm: float          # Neutral axis depth
```

**Visual Elements:**
1. **Concrete section** - Light blue rectangle with navy border
2. **Effective depth line** - Green dashed horizontal line at d
3. **Neutral axis** - Red dotted horizontal line at xu
4. **Compression zone** - Light red fill above neutral axis
5. **Tension zone** - Light green fill below neutral axis
6. **Main bars** - Orange circles at calculated positions
7. **Stirrups** - Gray rectangular outline (simplified)
8. **Dimension annotations** - b, D, d, cover with leaders

**Interactions:**
- Hover on bars → Show "16mm bar, Area = 201 mm²"
- Hover on zones → Show "Compression zone: 0.42*xu = 45mm"
- Click to highlight individual elements

**Code Template:**
```python
def create_beam_diagram(data: BeamVisualizationData) -> go.Figure:
    """
    Create interactive beam cross-section diagram.

    Features:
    - Accurate proportions (1:1 aspect ratio)
    - Color-coded stress zones
    - Interactive hover tooltips
    - Dimension annotations

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    # 1. Draw concrete section
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=data.b_mm, y1=data.D_mm,
        line=dict(color="#003366", width=3),
        fillcolor="rgba(173, 216, 230, 0.3)"  # Light blue
    )

    # 2. Draw compression zone (above neutral axis)
    fig.add_shape(
        type="rect",
        x0=0, y0=data.D_mm - data.xu_mm, x1=data.b_mm, y1=data.D_mm,
        fillcolor="rgba(255, 200, 200, 0.5)",  # Light red
        line=dict(width=0)
    )

    # 3. Draw tension zone (below neutral axis)
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=data.b_mm, y1=data.D_mm - data.xu_mm,
        fillcolor="rgba(200, 255, 200, 0.5)",  # Light green
        line=dict(width=0)
    )

    # 4. Draw neutral axis line
    fig.add_shape(
        type="line",
        x0=0, y0=data.D_mm - data.xu_mm,
        x1=data.b_mm, y1=data.D_mm - data.xu_mm,
        line=dict(color="red", width=2, dash="dot")
    )

    # 5. Calculate and draw rebar positions
    spacing = (data.b_mm - 2*data.cover_mm - data.bar_diameter) / (data.num_bars - 1)
    bar_y = data.cover_mm + data.stirrup_diameter + data.bar_diameter/2

    for i in range(data.num_bars):
        bar_x = data.cover_mm + data.stirrup_diameter + data.bar_diameter/2 + i * spacing

        fig.add_shape(
            type="circle",
            x0=bar_x - data.bar_diameter/2,
            y0=bar_y - data.bar_diameter/2,
            x1=bar_x + data.bar_diameter/2,
            y1=bar_y + data.bar_diameter/2,
            fillcolor="#FF6600",
            line=dict(color="#CC5200", width=2)
        )

    # 6. Add dimension annotations
    fig.add_annotation(x=data.b_mm/2, y=data.D_mm + 30,
                       text=f"b = {data.b_mm:.0f} mm", showarrow=False)
    fig.add_annotation(x=data.b_mm + 40, y=data.D_mm/2,
                       text=f"D = {data.D_mm:.0f} mm", showarrow=False, textangle=90)

    # 7. Layout
    fig.update_layout(
        title=dict(text="Beam Cross-Section", x=0.5),
        xaxis=dict(visible=False, range=[-50, data.b_mm + 80]),
        yaxis=dict(visible=False, range=[-50, data.D_mm + 80], scaleanchor="x"),
        width=500, height=500,
        showlegend=False,
        hovermode='closest'
    )

    return fig
```

**Acceptance Criteria:**
- [ ] Accurate proportions (1:1 aspect ratio)
- [ ] All 7 visual elements rendered
- [ ] Hover tooltips on bars and zones
- [ ] Dimension annotations visible
- [ ] Colorblind-safe palette
- [ ] Unit tests for rebar position calculation

---

#### 2. Cost Comparison Chart (`create_cost_comparison`)
**Purpose:** Bar chart comparing different bar arrangements by cost

**Input Data:**
```python
options = [
    {"name": "3-16mm", "area": 603, "cost": 87.45, "is_optimal": True, "utilization": 0.92},
    {"name": "2-20mm", "area": 628, "cost": 92.30, "is_optimal": False, "utilization": 0.96},
    {"name": "4-14mm", "area": 616, "cost": 89.50, "is_optimal": False, "utilization": 0.94},
    {"name": "2-16mm+1-12mm", "area": 515, "cost": 75.20, "is_optimal": False, "utilization": 0.78},
]
```

**Visual Elements:**
1. **Bars** - Vertical bars with costs
2. **Optimal highlight** - Green bar for recommended option
3. **Non-optimal** - Blue bars for alternatives
4. **Cost labels** - ₹ values above each bar
5. **Utilization overlay** - Small indicator showing steel utilization %
6. **Savings annotation** - "Saves ₹X.XX vs next option"

**Code Template:**
```python
def create_cost_comparison(options: list[dict]) -> go.Figure:
    """
    Bar chart comparing design options by cost.

    Highlights optimal choice, shows utilization overlay.
    """
    names = [opt["name"] for opt in options]
    costs = [opt["cost"] for opt in options]
    colors = ["#28A745" if opt.get("is_optimal") else "#6C9BD1" for opt in options]
    utilizations = [opt.get("utilization", 0.9) for opt in options]

    fig = go.Figure()

    # Cost bars
    fig.add_trace(go.Bar(
        x=names, y=costs,
        marker_color=colors,
        text=[f"₹{c:.2f}" for c in costs],
        textposition='outside',
        hovertemplate="<b>%{x}</b><br>Cost: ₹%{y:.2f}<br>Utilization: %{customdata:.0%}<extra></extra>",
        customdata=utilizations
    ))

    fig.update_layout(
        title="Cost Comparison: Bar Arrangements",
        xaxis_title="Arrangement",
        yaxis_title="Cost per Meter (₹/m)",
        yaxis=dict(range=[0, max(costs) * 1.2]),
        showlegend=False,
        height=400
    )

    return fig
```

**Acceptance Criteria:**
- [ ] All options displayed as bars
- [ ] Optimal option highlighted in green
- [ ] Cost labels visible above bars
- [ ] Hover shows utilization %
- [ ] Responsive width

---

#### 3. Utilization Gauge (`create_utilization_gauge`)
**Purpose:** Circular gauge showing design capacity utilization

**Input Data:**
```python
utilization_data = {
    "flexure": {"value": 0.92, "limit": 1.0, "status": "OK"},
    "shear": {"value": 0.45, "limit": 1.0, "status": "OK"},
    "deflection": {"value": 0.78, "limit": 1.0, "status": "OK"},
}
```

**Visual Elements:**
1. **Gauge arc** - 180° arc showing 0-100%
2. **Colored zones** - Green (0-80%), Yellow (80-95%), Red (95-100%)
3. **Needle** - Pointing to current value
4. **Value label** - "92%" in center
5. **Status text** - "OK" or "EXCEEDS LIMIT"

**Code Template:**
```python
def create_utilization_gauge(value: float, title: str = "Utilization") -> go.Figure:
    """
    Semicircular gauge for capacity utilization.

    Colors: Green (0-80%), Yellow (80-95%), Red (95-100%)
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value * 100,
        number={"suffix": "%", "font": {"size": 40}},
        title={"text": title, "font": {"size": 16}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 2},
            "bar": {"color": "#003366"},
            "steps": [
                {"range": [0, 80], "color": "#28A745"},
                {"range": [80, 95], "color": "#FFC107"},
                {"range": [95, 100], "color": "#DC3545"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 100
            }
        }
    ))

    fig.update_layout(height=300, margin=dict(t=50, b=20, l=20, r=20))
    return fig
```

**Acceptance Criteria:**
- [ ] Gauge shows 0-100% range
- [ ] Color zones correct (green/yellow/red)
- [ ] Value displayed prominently
- [ ] Threshold line at 100%

---

#### 4. Sensitivity Tornado Chart (`create_sensitivity_tornado`)
**Purpose:** Show which input parameters most affect the design

**Input Data:**
```python
sensitivity_data = [
    {"param": "Moment (Mu)", "low": -15, "high": 18, "base": 80},
    {"param": "Concrete Grade", "low": -8, "high": 12, "base": 25},
    {"param": "Steel Grade", "low": -5, "high": 8, "base": 415},
    {"param": "Width (b)", "low": -3, "high": 4, "base": 230},
    {"param": "Depth (D)", "low": -10, "high": 15, "base": 450},
]
```

**Visual Elements:**
1. **Horizontal bars** - Extending left (decrease) and right (increase)
2. **Parameter labels** - On Y-axis
3. **Base value line** - Vertical line at 0%
4. **Color coding** - Blue for decrease, Orange for increase
5. **Sorted by impact** - Largest impact at top

**Code Template:**
```python
def create_sensitivity_tornado(data: list[dict]) -> go.Figure:
    """
    Tornado chart showing parameter sensitivity.
    """
    # Sort by total impact (|low| + |high|)
    sorted_data = sorted(data, key=lambda x: abs(x["low"]) + abs(x["high"]), reverse=True)

    params = [d["param"] for d in sorted_data]
    lows = [d["low"] for d in sorted_data]
    highs = [d["high"] for d in sorted_data]

    fig = go.Figure()

    # Low bars (negative)
    fig.add_trace(go.Bar(
        y=params, x=lows, orientation='h',
        marker_color='#6C9BD1', name='Decrease (-10%)',
        text=[f"{v}%" for v in lows], textposition='outside'
    ))

    # High bars (positive)
    fig.add_trace(go.Bar(
        y=params, x=highs, orientation='h',
        marker_color='#FF6600', name='Increase (+10%)',
        text=[f"+{v}%" for v in highs], textposition='outside'
    ))

    fig.update_layout(
        title="Sensitivity Analysis: Cost Impact",
        xaxis_title="% Change in Cost",
        barmode='overlay',
        height=400
    )

    return fig
```

**Acceptance Criteria:**
- [ ] Bars extend both directions from center
- [ ] Sorted by total impact
- [ ] Clear color distinction
- [ ] Percentage labels visible

---

#### 5. Compliance Checklist Visual (`create_compliance_visual`)
**Purpose:** Visual checklist of IS 456 compliance status

**Input Data:**
```python
compliance_checks = [
    {"clause": "26.5.1.1", "description": "Min steel ratio", "passed": True, "value": "0.85%", "limit": "0.85%"},
    {"clause": "26.5.1.2", "description": "Max steel ratio", "passed": True, "value": "2.1%", "limit": "4.0%"},
    {"clause": "40.1", "description": "Shear capacity", "passed": True, "value": "0.45", "limit": "1.0"},
    {"clause": "26.3.3", "description": "Bar spacing", "passed": False, "value": "35mm", "limit": "≥40mm"},
]
```

**Visual Elements:**
1. **Checklist rows** - One per compliance check
2. **Status icons** - ✅ or ❌
3. **Clause reference** - IS 456 clause number
4. **Description** - Human-readable check name
5. **Value/Limit** - Actual vs allowed
6. **Progress bar** - Visual utilization

**Code Template:**
```python
def create_compliance_visual(checks: list[dict]) -> go.Figure:
    """
    Visual compliance checklist with status indicators.
    """
    fig = go.Figure()

    n = len(checks)
    for i, check in enumerate(checks):
        y = n - i - 1  # Reverse order (top to bottom)
        color = "#28A745" if check["passed"] else "#DC3545"
        icon = "✅" if check["passed"] else "❌"

        # Status icon
        fig.add_annotation(x=0, y=y, text=icon, showarrow=False, font=dict(size=20))

        # Clause + Description
        fig.add_annotation(x=0.5, y=y,
                           text=f"<b>Cl. {check['clause']}</b>: {check['description']}",
                           showarrow=False, xanchor='left')

        # Value bar
        limit_val = float(check["limit"].replace('%', '').replace('≥', '').replace('mm', ''))
        actual_val = float(check["value"].replace('%', '').replace('mm', ''))
        ratio = min(actual_val / limit_val, 1.0) if limit_val > 0 else 0

        fig.add_shape(type="rect", x0=3, y0=y-0.3, x1=3 + ratio*2, y1=y+0.3,
                      fillcolor=color, opacity=0.7)

    fig.update_layout(
        xaxis=dict(visible=False, range=[-0.5, 6]),
        yaxis=dict(visible=False, range=[-1, n]),
        height=50 * n + 100,
        showlegend=False
    )

    return fig
```

**Acceptance Criteria:**
- [ ] All checks displayed
- [ ] Clear pass/fail indicators
- [ ] Clause references visible
- [ ] Value vs limit comparison

---

### Testing Requirements

**Unit Tests (20+ tests):**
```python
# streamlit_app/tests/test_visualizations.py

class TestBeamDiagram:
    def test_rebar_positions_calculated(self):
        """Test rebar positions are correctly spaced."""
        pass

    def test_neutral_axis_within_section(self):
        """Test neutral axis is between 0 and D."""
        pass

    def test_figure_has_correct_shapes(self):
        """Test figure contains expected shape types."""
        pass

class TestCostComparison:
    def test_optimal_highlighted(self):
        """Test optimal option is green."""
        pass

    def test_sorted_by_cost(self):
        """Test bars sorted by cost."""
        pass

class TestUtilizationGauge:
    def test_color_zones(self):
        """Test gauge color at different values."""
        pass

    def test_over_100_capped(self):
        """Test values over 100% are capped."""
        pass
```

---

### Daily Work Plan

| Day | Focus | Deliverable |
|-----|-------|-------------|
| 6 | Beam diagram | `create_beam_diagram()` + tests |
| 7 | Cost comparison | `create_cost_comparison()` + tests |
| 8 | Utilization gauge | `create_utilization_gauge()` + tests |
| 9 | Sensitivity tornado | `create_sensitivity_tornado()` + tests |
| 10 | Compliance visual | `create_compliance_visual()` + integration tests |

---

### Handoff Checklist

When IMPL-003 is complete, include in handoff:
- [ ] All 5 visualization functions implemented
- [ ] 20+ unit tests passing
- [ ] Screenshots of each visualization
- [ ] Responsive design verified (mobile/tablet/desktop)
- [ ] Accessibility verified (colorblind-safe)
- [ ] Performance: Each chart renders < 100ms

## 🔴 STREAMLIT-IMPL-004: Beam Design Page (Day 11-15)
**Priority:** 🔴 CRITICAL
**Status:** 🟡 TODO - AFTER IMPL-003
**Estimated Effort:** 8-10 hours (1.5-2 hours/day over 5 days)

### Objective
Create the complete Beam Design page that integrates:
- All 5 input components from IMPL-002
- All 5 visualization components from IMPL-003
- structural_lib API via smart_analyze_design()
- Session state for persistence
- Error handling and validation

### Page Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🏗️ Beam Design - IS 456 RC Beam Design                              │
├─────────────────┬───────────────────────────────────────────────────┤
│ SIDEBAR         │ MAIN AREA                                         │
│ ─────────────── │ ─────────────────────────────────────────────────│
│ 📏 Geometry     │ [📊 Summary] [🎨 Viz] [💰 Cost] [✅ Compliance]   │
│ • Span          │ ─────────────────────────────────────────────────│
│ • Width (b)     │                                                   │
│ • Depth (D)     │  SUMMARY TAB:                                     │
│ • Cover         │  ┌─────────┬─────────┬─────────┐                 │
│                 │  │Ast_req  │Bars     │Cost     │                 │
│ 🧱 Materials    │  │450 mm²  │3-16mm   │₹87.45/m │                 │
│ • Concrete      │  └─────────┴─────────┴─────────┘                 │
│ • Steel         │                                                   │
│                 │  VIZ TAB:                                         │
│ ⚖️ Loading      │  [Beam Cross-Section Diagram]                     │
│ • Moment        │                                                   │
│ • Shear         │  COST TAB:                                        │
│                 │  [Cost Comparison Bar Chart]                      │
│ 🌧️ Exposure     │  [Sensitivity Tornado Chart]                      │
│ • Condition     │                                                   │
│                 │  COMPLIANCE TAB:                                  │
│ 📐 Support      │  [Compliance Checklist Visual]                    │
│ • Type          │  [Utilization Gauges (3x)]                        │
│                 │                                                   │
│ ─────────────── │                                                   │
│ [🚀 ANALYZE]    │                                                   │
└─────────────────┴───────────────────────────────────────────────────┘
```

### Full Implementation

```python
# streamlit_app/pages/01_🏗️_beam_design.py

import streamlit as st
from structural_lib.api import smart_analyze_design
from structural_lib.types import DesignError

from components.inputs import (
    dimension_input,
    material_selector,
    load_input,
    exposure_selector,
    support_condition_selector,
    CONCRETE_GRADES,
    STEEL_GRADES,
)
from components.visualizations import (
    create_beam_diagram,
    create_cost_comparison,
    create_utilization_gauge,
    create_sensitivity_tornado,
    create_compliance_visual,
    BeamVisualizationData,
)
from utils.api_wrapper import cached_design_analysis
from utils.validation import validate_beam_inputs

# Page config
st.set_page_config(
    page_title="Beam Design | IS 456 Calculator",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for print-friendly results
st.markdown("""
<style>
    @media print {
        .stSidebar { display: none; }
        .stButton { display: none; }
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF6600;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🏗️ Beam Design")
st.markdown("Design reinforced concrete beams per **IS 456:2000**")

# Initialize session state
if 'beam_inputs' not in st.session_state:
    st.session_state.beam_inputs = {
        'span_mm': 4000,
        'b_mm': 230,
        'D_mm': 450,
    }

if 'beam_result' not in st.session_state:
    st.session_state.beam_result = None

# ─────────────────────────────────────────────────────────────
# SIDEBAR: Input Parameters
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📝 Input Parameters")

    # ── Geometry Section ──
    st.subheader("📏 Geometry")

    span_mm, span_valid = dimension_input(
        label="Span",
        min_val=1000,
        max_val=12000,
        default_val=st.session_state.beam_inputs.get('span_mm', 4000),
        unit="mm",
        help_text="Clear span between supports (Cl. 23.2.1)",
        key="input_span"
    )

    b_mm, b_valid = dimension_input(
        label="Width (b)",
        min_val=150,
        max_val=600,
        default_val=st.session_state.beam_inputs.get('b_mm', 230),
        unit="mm",
        help_text="Width of beam section",
        key="input_width"
    )

    D_mm, D_valid = dimension_input(
        label="Total Depth (D)",
        min_val=200,
        max_val=900,
        default_val=st.session_state.beam_inputs.get('D_mm', 450),
        unit="mm",
        help_text="Overall depth of beam",
        key="input_depth"
    )

    # ── Materials Section ──
    st.subheader("🧱 Materials")

    concrete_grade, concrete_props = material_selector(
        material_type="concrete",
        key="input_concrete"
    )

    steel_grade, steel_props = material_selector(
        material_type="steel",
        key="input_steel"
    )

    # ── Loading Section ──
    st.subheader("⚖️ Loading")

    mu_knm, vu_kn, load_valid = load_input(
        default_moment=80.0,
        default_shear=60.0,
        key="input_loads"
    )

    # ── Exposure Section ──
    st.subheader("🌧️ Exposure")

    exposure, exposure_props = exposure_selector(key="input_exposure")
    min_cover = exposure_props["cover"]

    # ── Support Section ──
    st.subheader("📐 Support Condition")

    support, support_props = support_condition_selector(key="input_support")

    # ── Calculate effective depth ──
    stirrup_dia = 8  # Assume 8mm stirrups
    bar_dia = 16     # Initial assumption, will be updated
    d_mm = D_mm - min_cover - stirrup_dia - bar_dia / 2

    st.info(f"📐 Effective depth (d) ≈ **{d_mm:.0f} mm**")
    st.caption(f"Based on: D={D_mm}, cover={min_cover}, stirrup=8mm")

    # ── Validation Check ──
    st.divider()

    all_valid = all([span_valid, b_valid, D_valid, load_valid])

    if not all_valid:
        st.error("❌ Fix validation errors above before analyzing")

    # ── Analyze Button ──
    analyze_clicked = st.button(
        "🚀 Analyze Design",
        type="primary",
        disabled=not all_valid,
        use_container_width=True
    )

# ─────────────────────────────────────────────────────────────
# MAIN AREA: Results
# ─────────────────────────────────────────────────────────────

if analyze_clicked:
    # Update session state with current inputs
    st.session_state.beam_inputs = {
        'span_mm': span_mm,
        'b_mm': b_mm,
        'D_mm': D_mm,
    }

    with st.spinner("🔄 Analyzing design..."):
        try:
            # Call cached API wrapper
            result = cached_design_analysis(
                span_mm=span_mm,
                b_mm=b_mm,
                d_mm=d_mm,
                D_mm=D_mm,
                mu_knm=mu_knm,
                vu_kn=vu_kn,
                fck=concrete_props["fck"],
                fy=steel_props["fy"],
                exposure=exposure,
                support=support,
            )

            # Store result
            st.session_state.beam_result = result

        except DesignError as e:
            st.error(f"❌ Design Error: {e}")
            st.session_state.beam_result = None
            st.stop()
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            st.session_state.beam_result = None
            st.stop()

# Display results if available
if st.session_state.beam_result:
    result = st.session_state.beam_result

    st.success("✅ Design analysis complete!")

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Summary",
        "🎨 Visualization",
        "💰 Cost Analysis",
        "✅ Compliance"
    ])

    # ── Tab 1: Summary ──
    with tab1:
        st.subheader("Design Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="Steel Area Required",
                value=f"{result.Ast_required:.0f} mm²",
            )

        with col2:
            st.metric(
                label="Steel Area Provided",
                value=f"{result.Ast_provided:.0f} mm²",
                delta=f"+{result.Ast_provided - result.Ast_required:.0f}",
                delta_color="normal"
            )

        with col3:
            st.metric(
                label="Bar Arrangement",
                value=f"{result.num_bars}–{result.bar_dia}mm"
            )

        with col4:
            st.metric(
                label="Cost per Meter",
                value=f"₹{result.cost_per_m:.2f}"
            )

        # Detailed results table
        st.divider()

        details_col1, details_col2 = st.columns(2)

        with details_col1:
            st.markdown("**Flexure Design**")
            st.markdown(f"- Neutral axis: xu = {result.xu:.1f} mm")
            st.markdown(f"- xu/d ratio: {result.xu/d_mm:.3f}")
            st.markdown(f"- Tension steel: {result.Ast_provided:.0f} mm²")
            st.markdown(f"- Steel ratio: {result.Ast_provided/(b_mm*d_mm)*100:.2f}%")

        with details_col2:
            st.markdown("**Shear Design**")
            st.markdown(f"- Shear capacity: τc = {result.tau_c:.2f} N/mm²")
            st.markdown(f"- Shear stress: τv = {result.tau_v:.2f} N/mm²")
            st.markdown(f"- Stirrup spacing: {result.stirrup_spacing:.0f} mm")
            st.markdown(f"- Shear utilization: {result.shear_utilization*100:.0f}%")

    # ── Tab 2: Visualization ──
    with tab2:
        st.subheader("Beam Cross-Section")

        # Create visualization data
        viz_data = BeamVisualizationData(
            b_mm=b_mm,
            D_mm=D_mm,
            d_mm=d_mm,
            cover_mm=min_cover,
            bar_diameter=result.bar_dia,
            num_bars=result.num_bars,
            stirrup_diameter=8,
            xu_mm=result.xu,
        )

        fig = create_beam_diagram(viz_data)
        st.plotly_chart(fig, use_container_width=True)

        # Utilization gauges in a row
        st.subheader("Capacity Utilization")

        gauge_col1, gauge_col2, gauge_col3 = st.columns(3)

        with gauge_col1:
            fig = create_utilization_gauge(result.flexure_utilization, "Flexure")
            st.plotly_chart(fig, use_container_width=True)

        with gauge_col2:
            fig = create_utilization_gauge(result.shear_utilization, "Shear")
            st.plotly_chart(fig, use_container_width=True)

        with gauge_col3:
            fig = create_utilization_gauge(result.deflection_utilization, "Deflection")
            st.plotly_chart(fig, use_container_width=True)

    # ── Tab 3: Cost Analysis ──
    with tab3:
        st.subheader("Cost Optimization")

        if hasattr(result, 'alternatives') and result.alternatives:
            fig = create_cost_comparison(result.alternatives)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ Cost comparison requires rebar_optimizer module")

        st.divider()
        st.subheader("Sensitivity Analysis")

        if hasattr(result, 'sensitivity_data') and result.sensitivity_data:
            fig = create_sensitivity_tornado(result.sensitivity_data)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ Sensitivity analysis not available for this design")

    # ── Tab 4: Compliance ──
    with tab4:
        st.subheader("IS 456 Compliance")

        if hasattr(result, 'compliance_checks') and result.compliance_checks:
            fig = create_compliance_visual(result.compliance_checks)
            st.plotly_chart(fig, use_container_width=True)

            # Summary
            passed = sum(1 for c in result.compliance_checks if c["passed"])
            total = len(result.compliance_checks)

            if passed == total:
                st.success(f"✅ All {total} compliance checks passed!")
            else:
                st.warning(f"⚠️ {passed}/{total} checks passed. See failures above.")
        else:
            st.info("ℹ️ Compliance data not available")

        # Print button
        st.divider()
        if st.button("🖨️ Print Report"):
            st.markdown("""
            <script>window.print();</script>
            """, unsafe_allow_html=True)

else:
    # Show placeholder when no results
    st.info("👈 Enter design parameters in the sidebar and click **Analyze Design**")

    # Quick example
    with st.expander("📖 Example: 4m Span Beam"):
        st.markdown("""
        **Given (typical residential beam):**
        - Span: 4000 mm
        - Width (b): 230 mm
        - Total Depth (D): 450 mm
        - Moment: 80 kNm
        - Shear: 60 kN
        - Concrete: M20
        - Steel: Fe415
        - Exposure: Moderate

        **Expected Result:**
        - Steel required: ~450 mm²
        - Arrangement: 3–16mm bars
        - Cost: ~₹87/meter
        """)
```

### API Wrapper Implementation

```python
# streamlit_app/utils/api_wrapper.py

import streamlit as st
from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class BeamDesignResult:
    """Unified result object for UI display."""
    # Flexure
    Ast_required: float
    Ast_provided: float
    num_bars: int
    bar_dia: int
    xu: float
    flexure_utilization: float

    # Shear
    tau_c: float
    tau_v: float
    stirrup_spacing: float
    shear_utilization: float

    # Deflection
    deflection_utilization: float

    # Cost
    cost_per_m: float

    # Optional extras
    alternatives: Optional[list[dict]] = None
    sensitivity_data: Optional[list[dict]] = None
    compliance_checks: Optional[list[dict]] = None


@st.cache_data(ttl=3600, show_spinner=False)
def cached_design_analysis(
    span_mm: float,
    b_mm: float,
    d_mm: float,
    D_mm: float,
    mu_knm: float,
    vu_kn: float,
    fck: float,
    fy: float,
    exposure: str,
    support: str,
) -> BeamDesignResult:
    """
    Cached wrapper around structural_lib API.

    Caches results for 1 hour to improve performance.
    """
    from structural_lib.api import smart_analyze_design

    # Call the main API
    raw_result = smart_analyze_design(
        span_mm=span_mm,
        b_mm=b_mm,
        d_mm=d_mm,
        D_mm=D_mm,
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        fck_nmm2=fck,
        fy_nmm2=fy,
        exposure=exposure,
        support_type=support,
    )

    # Transform to UI-friendly format
    return BeamDesignResult(
        Ast_required=raw_result.flexure.Ast_required,
        Ast_provided=raw_result.flexure.Ast_provided,
        num_bars=raw_result.flexure.num_bars,
        bar_dia=raw_result.flexure.bar_diameter,
        xu=raw_result.flexure.xu,
        flexure_utilization=raw_result.flexure.utilization,
        tau_c=raw_result.shear.tau_c,
        tau_v=raw_result.shear.tau_v,
        stirrup_spacing=raw_result.shear.stirrup_spacing,
        shear_utilization=raw_result.shear.utilization,
        deflection_utilization=raw_result.serviceability.deflection_ratio,
        cost_per_m=raw_result.cost.cost_per_meter if raw_result.cost else 0,
        alternatives=raw_result.alternatives if hasattr(raw_result, 'alternatives') else None,
        sensitivity_data=raw_result.sensitivity if hasattr(raw_result, 'sensitivity') else None,
        compliance_checks=raw_result.compliance if hasattr(raw_result, 'compliance') else None,
    )
```

### Testing Requirements

**Unit Tests (15+ tests):**
```python
# streamlit_app/tests/test_beam_design_page.py

import pytest
from unittest.mock import MagicMock, patch

class TestBeamDesignPage:
    def test_sidebar_renders_all_inputs(self, page_session):
        """Test all 5 input components appear in sidebar."""
        pass

    def test_validation_blocks_analysis(self, page_session):
        """Test invalid inputs disable analyze button."""
        pass

    def test_api_called_with_correct_params(self, mock_api):
        """Test smart_analyze_design receives correct values."""
        pass

    def test_error_handling_design_error(self, mock_api):
        """Test DesignError shows user-friendly message."""
        pass

    def test_session_state_persists(self, page_session):
        """Test inputs persist across reruns."""
        pass

    def test_all_tabs_render(self, page_session, mock_result):
        """Test 4 result tabs render without error."""
        pass

class TestAPIWrapper:
    def test_caching_works(self, mock_api):
        """Test same inputs return cached result."""
        pass

    def test_result_transformation(self, mock_api):
        """Test raw API result transforms to BeamDesignResult."""
        pass
```

### Daily Work Plan

| Day | Focus | Deliverable |
|-----|-------|-------------|
| 11 | Page layout + sidebar | All inputs in sidebar, layout structure |
| 12 | API integration | `cached_design_analysis()` + error handling |
| 13 | Summary + Viz tabs | Metrics, beam diagram, gauges |
| 14 | Cost + Compliance tabs | Charts, checklist |
| 15 | Testing + polish | 15+ tests, session state, print button |

### Handoff Checklist

When IMPL-004 is complete, include:
- [ ] Full page renders without errors
- [ ] All 5 input components work
- [ ] All 5 visualizations display
- [ ] API integration tested
- [ ] Error handling tested (DesignError)
- [ ] Session state persists inputs
- [ ] 15+ unit tests passing
- [ ] Responsive design verified

---

## 🟠 STREAMLIT-IMPL-005: Cost Optimizer Page (Day 16-20)
**Priority:** 🟠 HIGH
**Status:** 🟡 TODO - AFTER IMPL-004
**Estimated Effort:** 8-10 hours

### Objective
Create a dedicated page for exploring rebar optimization options:
- Compare multiple bar arrangements
- Interactive cost vs utilization trade-off visualization
- Batch design exploration (vary parameters)
- Export comparison table

### Page Features

```
┌─────────────────────────────────────────────────────────────────────┐
│ 💰 Cost Optimizer - Find the Most Economical Design                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ [Load from Beam Design] button                                       │
│                                                                      │
│ ┌────────────────────────────────────────────────────────────────┐  │
│ │ COST vs UTILIZATION SCATTER                                     │  │
│ │                                                                  │  │
│ │     💚 3-16mm (optimal)                                         │  │
│ │   ●                                                              │  │
│ │        ○ 2-20mm                                                  │  │
│ │     ○ 4-14mm                                                     │  │
│ │  ○ 2-16mm+1-12mm (under)                                        │  │
│ │                                                                  │  │
│ │  Cost (₹/m) →                                                   │  │
│ └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│ ┌────────────────────────────────────────────────────────────────┐  │
│ │ OPTIONS TABLE                                                   │  │
│ │                                                                  │  │
│ │ | Arrangement | Area | Util% | Cost | Savings | Status |       │  │
│ │ |-------------|------|-------|------|---------|--------|       │  │
│ │ | 3-16mm ⭐    | 603  | 92%   | ₹87  | -       | ✅      |       │  │
│ │ | 2-20mm      | 628  | 96%   | ₹92  | -₹5.85  | ✅      |       │  │
│ │ | 4-14mm      | 616  | 94%   | ₹89  | -₹2.05  | ✅      |       │  │
│ │ | 2-16+1-12   | 515  | 78%   | ₹75  | +₹12.45 | ⚠️ UNDER|       │  │
│ └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│ [📥 Export CSV] [🖨️ Print]                                          │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Functions

```python
# streamlit_app/pages/02_💰_cost_optimizer.py

def create_cost_utilization_scatter(options: list[dict]) -> go.Figure:
    """
    Scatter plot: X=cost, Y=utilization
    Color: green=optimal, blue=valid, red=under-designed
    Size: proportional to steel area
    """
    pass

def create_options_table(options: list[dict]) -> pd.DataFrame:
    """
    Sortable table with:
    - Arrangement name
    - Steel area
    - Utilization %
    - Cost/meter
    - Savings vs optimal
    - Status (✅/⚠️/❌)
    """
    pass

def export_comparison_csv(options: list[dict], filename: str) -> bytes:
    """
    Export options to CSV for download.
    """
    pass
```

### Daily Work Plan

| Day | Focus | Deliverable |
|-----|-------|-------------|
| 16 | Page layout + load from beam design | Integration with session state |
| 17 | Cost/utilization scatter | Interactive Plotly scatter |
| 18 | Options table | Sortable pandas DataFrame |
| 19 | Export functionality | CSV download, print |
| 20 | Testing | 10+ unit tests |

---

## 🟠 STREAMLIT-IMPL-006: Compliance Checker Page (Day 21-25)
**Priority:** 🟠 HIGH
**Status:** 🟡 TODO - AFTER IMPL-005
**Estimated Effort:** 8-10 hours

### Objective
Create a dedicated compliance verification page:
- Comprehensive IS 456 clause checking
- Expandable clause details with code excerpts
- Generate compliance certificate
- Track revisions

### Page Features

```
┌─────────────────────────────────────────────────────────────────────┐
│ ✅ Compliance Checker - IS 456:2000 Verification                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ OVERALL STATUS: ✅ COMPLIANT (12/12 checks passed)                  │
│                                                                      │
│ ▼ 26.5.1.1 - Minimum Steel Ratio                      ✅ PASS       │
│   ├─ Requirement: pt ≥ 0.85√fck/fy = 0.85%                         │
│   ├─ Actual: pt = 0.92%                                             │
│   └─ Margin: +8.2%                                                  │
│                                                                      │
│ ▼ 26.5.1.2 - Maximum Steel Ratio                      ✅ PASS       │
│   ├─ Requirement: pt ≤ 4.0%                                         │
│   ├─ Actual: pt = 0.92%                                             │
│   └─ Margin: +77%                                                   │
│                                                                      │
│ ▼ 40.1 - Shear Capacity                               ✅ PASS       │
│   ├─ Requirement: τv ≤ τc + τs                                      │
│   ├─ Actual: τv = 0.45 N/mm² ≤ 0.68 N/mm²                          │
│   └─ Margin: +51%                                                   │
│                                                                      │
│ ▶ 26.3.3 - Bar Spacing [Click to expand]              ✅ PASS       │
│ ▶ 26.4.1 - Cover Requirements                         ✅ PASS       │
│ ▶ 23.2.1 - Deflection Limits                          ✅ PASS       │
│ ...                                                                  │
│                                                                      │
│ [📜 Generate Certificate] [📥 Export Report] [🖨️ Print]             │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Functions

```python
# streamlit_app/pages/03_✅_compliance.py

def create_clause_expander(check: dict) -> None:
    """
    Expandable section for each compliance check.
    Shows: requirement, actual, margin, clause text excerpt.
    """
    pass

def generate_compliance_certificate(
    checks: list[dict],
    project_name: str,
    engineer_name: str,
) -> bytes:
    """
    Generate PDF certificate summarizing compliance.
    """
    pass

def create_compliance_summary_card(checks: list[dict]) -> None:
    """
    Summary card showing: X/Y passed, overall status.
    """
    pass
```

### IS 456 Clauses to Check

| Clause | Description | Type |
|--------|-------------|------|
| 26.5.1.1 | Min steel ratio | Flexure |
| 26.5.1.2 | Max steel ratio | Flexure |
| 26.3.3 | Bar spacing | Detailing |
| 26.4.1 | Cover requirements | Durability |
| 26.4.2 | Fire resistance cover | Durability |
| 40.1 | Shear capacity | Shear |
| 40.2.3 | Min shear reinforcement | Shear |
| 40.4 | Max stirrup spacing | Detailing |
| 23.2.1 | Deflection limits | Serviceability |
| 35.1.1 | Cracking control | Serviceability |
| Ductile | Special seismic requirements | Seismic |
| Anchorage | Development length | Detailing |

### Daily Work Plan

| Day | Focus | Deliverable |
|-----|-------|-------------|
| 21 | Page layout + summary card | Overall status display |
| 22 | Clause expanders | Expandable sections with details |
| 23 | All 12 clauses | Complete compliance checking |
| 24 | Certificate generation | PDF export |
| 25 | Testing | 12+ unit tests (1 per clause) |

---

## 📋 IMPL-007 and Beyond (Future)

**STREAMLIT-IMPL-007: Documentation Page** (Day 26-28)
- Interactive IS 456 quick reference
- Searchable clause lookup
- Formula explanations with MathJax
- Example problems

**STREAMLIT-IMPL-008: Settings & Preferences** (Day 29-30)
- Unit preferences (mm vs m)
- Theme toggle (light/dark)
- Export preferences
- Keyboard shortcuts

**STREAMLIT-IMPL-009: Performance Optimization** (Day 31-33)
- Lazy loading for heavy components
- Caching strategy review
- Bundle size analysis
- Lighthouse audit

---

---

## Handoff Template

**At End of Each Day:**

```markdown
## Handoff: STREAMLIT SPECIALIST (Agent 6) → MAIN

**Date:** 2026-01-XX
**Task:** STREAMLIT-IMPL-XXX
**Status:** ✅ Committed locally, tested, ready for review

### Summary
[2-3 sentences: what was built/improved today]

### Files Changed
- `streamlit_app/components/xxx.py` - Added/modified function
- `streamlit_app/tests/test_xxx.py` - Added X unit tests

### Features Added
- ✅ [Feature 1]
- ✅ [Feature 2]

### Local Testing
- ✅ `streamlit run app.py` - No errors
- ✅ `pytest streamlit_app/tests/` - All tests pass
- ✅ Tested on Chrome/Firefox

### Next Steps
Tomorrow: [Next task]

### Action Required by MAIN
1. Review changes
2. Test locally
3. If approved: push and merge
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
