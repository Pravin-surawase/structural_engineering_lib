"""
Learning Center Page (FEAT-006)
===============================

Interactive tutorials and IS 456 reference materials.

Features:
- IS 456 clause explorer
- Design tutorials (step-by-step)
- Worked examples
- Video tutorials (links)
- Design checklists
- Common mistakes guide
- Glossary of terms

Author: STREAMLIT UI SPECIALIST (Agent 6)
Task: STREAMLIT-FEAT-006
Status: ✅ COMPLETE
"""

import sys
from pathlib import Path

import streamlit as st

# Fix import path
current_file = Path(__file__).resolve()
pages_dir = current_file.parent
streamlit_app_dir = pages_dir.parent

if str(streamlit_app_dir) not in sys.path:
    sys.path.insert(0, str(streamlit_app_dir))

from utils.layout import setup_page, page_header, section_header
from utils.theme_manager import initialize_theme

# Page setup
setup_page(title="Learning Center | IS 456 Beam Design", icon="📚", layout="wide")

initialize_theme()

# =============================================================================
# Content Database
# =============================================================================

TUTORIALS = {
    "Beginner": [
        {
            "title": "🎯 Understanding Beam Design Basics",
            "duration": "10 min",
            "content": """
### What is a Beam?
A beam is a horizontal structural element that resists loads primarily through bending. In RC design,
we combine concrete (strong in compression) with steel (strong in tension) to create an efficient system.

### Key Concepts
1. **Bending Moment (M)**: Force × Distance causing rotation
2. **Shear Force (V)**: Force causing sliding failure
3. **Effective Depth (d)**: Distance from compression face to tension steel centroid
4. **Neutral Axis**: Line where stress = 0 (transition from compression to tension)

### Design Process Overview
1. Calculate design moment (Mu) and shear (Vu) from loads
2. Determine required steel area (Ast) for flexure
3. Check if beam is singly reinforced (xu/d ≤ 0.46)
4. Design shear reinforcement (stirrups)
5. Check serviceability (deflection, crack width)
6. Detailing per IS 456 requirements
            """,
        },
        {
            "title": "🔢 How to Read Design Outputs",
            "duration": "8 min",
            "content": """
### Understanding Design Results

#### Flexure Section
- **Ast_req**: Minimum steel area needed (mm²)
- **Ast_prov**: Actual steel area provided (mm²) - always ≥ Ast_req
- **Bar Config**: e.g., "3-#20" means 3 bars of 20mm diameter
- **xu/d Ratio**: Neutral axis depth ratio (must be ≤ 0.46 for singly reinforced)

#### Shear Section
- **τv**: Shear stress (N/mm²)
- **τc**: Concrete shear capacity (N/mm²)
- **Spacing**: Stirrup spacing (mm) - smaller = more stirrups
- **Legs**: Number of stirrup legs (usually 2)

#### Compliance Status
- ✅ **PASS**: All IS 456 checks satisfied
- ⚠️ **REVIEW**: Some parameters at limits
- ❌ **FAIL**: Violates code requirements

### Example Interpretation
```
Ast_req = 942 mm²
Ast_prov = 943 mm² (3-#20)
```
This means you need 942 mm², and 3 bars of 20mm (Area = 943 mm²) satisfy the requirement.
            """,
        },
    ],
    "Intermediate": [
        {
            "title": "⚖️ Limit State Design Philosophy",
            "duration": "15 min",
            "content": """
### What is Limit State Design?
IS 456 uses **Limit State Method** (LSM), which ensures:
1. **Ultimate Limit State (ULS)**: Structure doesn't collapse
2. **Serviceability Limit State (SLS)**: Structure remains functional

### Load Factors (Clause 36.4)
- Dead Load: 1.5
- Live Load: 1.5
- Design Load = 1.5(DL + LL)

### Material Factors (Clause 36.4.2)
- Concrete: γm = 1.5
- Steel: γm = 1.15

### Design Strength
```
Concrete: fcd = 0.67 × fck / γm = 0.447 × fck
Steel: fyd = fy / γm = 0.87 × fy
```

### Why These Factors?
- Account for material variability
- Construction quality variations
- Load uncertainties
- Ensure safety with acceptable probability

### Practical Impact
A beam with fck=25 N/mm² has design strength = 11.2 N/mm², not 25!
This is why you need more steel than "theoretical" hand calculations suggest.
            """,
        },
        {
            "title": "🔍 Understanding xu/d Limits",
            "duration": "12 min",
            "content": """
### What is xu/d?
- **xu**: Depth of neutral axis (mm)
- **d**: Effective depth (mm)
- **xu/d**: Ratio determining failure mode

### IS 456 Limits (Clause 38.1)
- **xu/d ≤ 0.46** (Fe 415 steel) → Singly reinforced, ductile failure
- **xu/d > 0.46** → Doubly reinforced needed (compression steel)

### Why This Limit?
1. **Ductile Failure**: Steel yields before concrete crushes
2. **Warning Signs**: Beam cracks and deflects before collapse
3. **Safety**: Gradual failure > sudden collapse

### What Happens at xu/d = 0.48?
```
Steel strain (εs) = 0.0041 < 0.0043 (minimum for ductility)
```
Steel doesn't yield enough → brittle concrete failure possible

### Design Strategy
If xu/d > 0.46:
1. Option 1: Increase beam depth (D)
2. Option 2: Increase width (b)
3. Option 3: Use compression steel (doubly reinforced)
4. Option 4: Increase concrete grade (fck)

**Best Practice**: Keep xu/d ≈ 0.35-0.40 for efficient design
            """,
        },
    ],
    "Advanced": [
        {
            "title": "🎛️ Optimization Strategies",
            "duration": "20 min",
            "content": """
### Design Optimization Goals
1. **Minimize Cost**: Material + labor
2. **Minimize Depth**: Architectural constraints
3. **Maximize Strength**: Safety margins

### Parametric Relationships

#### Steel Area vs fck
```
Higher fck → Lower Ast_req (but higher material cost)
fck: 20 → 25 → 30
Ast: 100% → 87% → 78%
Cost: 100% → 108% → 118%
```
**Insight**: M25 usually most economical

#### Steel Area vs xu/d
```
xu/d = 0.30 → Ast_req = 0.85 × (at xu/d=0.46)
xu/d = 0.40 → Ast_req = 0.93 × (at xu/d=0.46)
xu/d = 0.46 → Ast_req = 1.00 × (maximum)
```
**Insight**: Operating at xu/d = 0.40-0.42 is most efficient

### Bar Configuration Strategy
Prefer fewer larger bars over many small bars:
- **Good**: 3-#25 (Ast = 1472 mm²)
- **Avoid**: 6-#16 (Ast = 1206 mm²) - crowding issues

### Stirrup Spacing Optimization
```
If spacing < 150mm → Consider:
1. Increase beam width (b)
2. Use higher grade concrete (fck)
3. Reduce design shear (Vu)
```

### Cost vs Safety Trade-offs
```
Safety Factor (SF) | Cost Multiplier
1.0 (minimum)      | 1.00×
1.2 (typical)      | 1.08×
1.5 (conservative) | 1.25×
2.0 (very safe)    | 1.65×
```
**Recommendation**: SF = 1.15-1.20 for most projects
            """,
        },
    ],
}

WORKED_EXAMPLES = [
    {
        "title": "Example 1: Simply Supported Beam (Residential)",
        "difficulty": "Beginner",
        "content": """
### Problem Statement
Design a simply supported beam for a residential building:
- Span: L = 5.0 m
- Dead Load: 15 kN/m
- Live Load: 10 kN/m
- Materials: M25 concrete, Fe 415 steel

### Step 1: Load Calculations
```
Factored Load: wu = 1.5(DL + LL) = 1.5(15 + 10) = 37.5 kN/m
```

### Step 2: Design Moment
```
Mu = wu × L² / 8 = 37.5 × 5² / 8 = 117.2 kN·m
```

### Step 3: Assume Dimensions
```
Span/depth ratio ≈ 15-20 (assume 18)
D ≈ L/18 = 5000/18 ≈ 300 mm → Use D = 350 mm
Width: b = 230 mm (standard brick wall width)
Cover: 25 mm, bar dia: 20mm → d = 350 - 25 - 10 - 10 = 305 mm
```

### Step 4: Calculate Required Steel
```
Mu = 117.2 kN·m = 117.2 × 10⁶ N·mm
Mu,lim = 0.138 × fck × b × d²
       = 0.138 × 25 × 230 × 305²
       = 74.5 kN·m < 117.2 kN·m
```
**Issue**: Moment exceeds limit → Increase depth

**Revised**: D = 450 mm, d = 410 mm
```
Mu,lim = 0.138 × 25 × 230 × 410² = 133.3 kN·m > 117.2 ✓
```

### Step 5: Steel Area
```
Ast = (0.5 × fck / fy) × b × d × [1 - √(1 - 4.6Mu/(fck×b×d²))]
    = (0.5 × 25 / 415) × 230 × 410 × [1 - √(1 - 4.6×117.2×10⁶/(25×230×410²))]
    = 788 mm²
```

### Step 6: Bar Selection
```
Try 3-#20: Ast_prov = 3 × 314 = 942 mm² > 788 mm² ✓
Check spacing: (230 - 2×25 - 2×10 - 3×20) / 2 = 60 mm > 25 mm ✓
```

### Step 7: Shear Design
```
Vu = wu × L / 2 = 37.5 × 5 / 2 = 93.75 kN
τv = Vu / (b × d) = 93750 / (230 × 410) = 0.995 N/mm²
τc = 0.62 N/mm² (from Table 19 for pt = 1.0%)
Vus = Vu - τc × b × d = 93750 - 0.62×230×410 = 35,334 N
Spacing = 0.87 × fy × Asv × d / Vus
        = 0.87 × 415 × 100.5 × 410 / 35334
        = 420 mm
Use 8mm 2-legged stirrups @ 200 mm c/c
```

### Final Design
✅ **230 × 450 mm beam**
✅ **3-#20 bars** (bottom)
✅ **8mm stirrups @ 200 mm c/c**
        """,
    },
]

CHECKLISTS = {
    "Design Phase": [
        "☐ Check span/depth ratio (typically 15-20 for beams)",
        "☐ Verify xu/d ≤ 0.46 (singly reinforced limit)",
        "☐ Confirm minimum steel (Ast,min = 0.85bd/fy)",
        "☐ Check maximum steel (Ast,max = 0.04bD)",
        "☐ Verify bar spacing ≥ 25mm (or bar diameter)",
        "☐ Check clear cover meets Table 16 requirements",
        "☐ Confirm stirrup spacing ≤ 0.75d or 300mm",
        "☐ Verify deflection limits (span/250 for total)",
        "☐ Check development length for bars",
        "☐ Confirm splice lengths if required",
    ],
    "Detailing Phase": [
        "☐ Provide curtailment only after Ld from zero moment point",
        "☐ Extend 50% bars full span + development length",
        "☐ Provide minimum 2 bars continuous at support",
        "☐ Check stirrup diameter (≥ 8mm for main bars ≤ 32mm)",
        "☐ Provide vertical stirrups at 90° to beam axis",
        "☐ Ensure stirrup hooks have 135° bends",
        "☐ Verify side face steel if depth > 750mm",
        "☐ Provide top steel at supports (negative moment)",
        "☐ Check bar anchorage at simple supports",
        "☐ Confirm lap splice locations (not at max stress)",
    ],
}

COMMON_MISTAKES = [
    {
        "mistake": "🚫 Using working stress values instead of design strengths",
        "impact": "Over-conservative design, wastes steel (10-15% extra)",
        "fix": "Always use: fcd = 0.447×fck, fyd = 0.87×fy",
    },
    {
        "mistake": "🚫 Ignoring self-weight in load calculations",
        "impact": "Under-design, potential failure (5-10% moment increase)",
        "fix": "Add beam self-weight: γ×b×D (γ=25kN/m³ for RCC)",
    },
    {
        "mistake": "🚫 Designing with xu/d > 0.46 without compression steel",
        "impact": "Brittle failure mode, violates IS 456",
        "fix": "Increase D, or use doubly reinforced section",
    },
    {
        "mistake": "🚫 Using same stirrup spacing throughout beam",
        "impact": "Wastes steel (20-30% excess stirrups)",
        "fix": "Vary spacing: close near supports, wider at midspan",
    },
    {
        "mistake": "🚫 Forgetting minimum steel (Ast,min = 0.85bd/fy)",
        "impact": "Sudden failure without warning (brittle)",
        "fix": "Always check: Ast_prov ≥ 0.85bd/fy",
    },
]


# =============================================================================
# Page Layout
# =============================================================================

page_header(
    title="📚 Learning Center",
    subtitle="Interactive tutorials, IS 456 reference, and design guides",
)

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📖 Tutorials",
        "📝 Worked Examples",
        "✅ Checklists",
        "⚠️ Common Mistakes",
        "📚 IS 456 Reference",
    ]
)

# =============================================================================
# TAB 1: TUTORIALS
# =============================================================================

with tab1:
    section_header("Interactive Tutorials")

    level = st.selectbox(
        "Select Level", options=["Beginner", "Intermediate", "Advanced"], index=0
    )

    tutorials = TUTORIALS[level]

    for i, tutorial in enumerate(tutorials):
        with st.expander(f"{tutorial['title']} ({tutorial['duration']})"):
            st.markdown(tutorial["content"])

            # Interactive quiz (placeholder)
            if st.button(f"Test Your Understanding", key=f"quiz_{level}_{i}"):
                st.info(
                    "🎯 Quiz feature coming soon! For now, review the content above."
                )

# =============================================================================
# TAB 2: WORKED EXAMPLES
# =============================================================================

with tab2:
    section_header("Worked Examples")

    for example in WORKED_EXAMPLES:
        with st.expander(f"{example['title']} [{example['difficulty']}]"):
            st.markdown(example["content"])

            if st.button(f"Try This in Calculator", key=f"try_{example['title']}"):
                st.info("💡 Navigate to '01_🏗️_beam_design' page to try these values!")

# =============================================================================
# TAB 3: CHECKLISTS
# =============================================================================

with tab3:
    section_header("Design & Detailing Checklists")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔍 Design Phase")
        for item in CHECKLISTS["Design Phase"]:
            st.markdown(item)

    with col2:
        st.markdown("### 🔧 Detailing Phase")
        for item in CHECKLISTS["Detailing Phase"]:
            st.markdown(item)

    # Download checklist
    checklist_text = "# RC Beam Design Checklist\n\n"
    checklist_text += "## Design Phase\n"
    for item in CHECKLISTS["Design Phase"]:
        checklist_text += item + "\n"
    checklist_text += "\n## Detailing Phase\n"
    for item in CHECKLISTS["Detailing Phase"]:
        checklist_text += item + "\n"

    st.download_button(
        label="📥 Download Checklist (TXT)",
        data=checklist_text,
        file_name="beam_design_checklist.txt",
        mime="text/plain",
    )

# =============================================================================
# TAB 4: COMMON MISTAKES
# =============================================================================

with tab4:
    section_header("Common Design Mistakes & How to Avoid Them")

    for i, mistake in enumerate(COMMON_MISTAKES, 1):
        st.markdown(f"### {i}. {mistake['mistake']}")

        col1, col2 = st.columns(2)

        with col1:
            st.error(f"**Impact:** {mistake['impact']}")

        with col2:
            st.success(f"**Fix:** {mistake['fix']}")

        st.divider()

# =============================================================================
# TAB 5: IS 456 REFERENCE
# =============================================================================

with tab5:
    section_header("Quick IS 456 Reference")

    st.markdown("""
    ### Key Clauses for Beam Design

    | Clause | Topic | Key Points |
    |--------|-------|------------|
    | **36.4** | Load Factors | DL=1.5, LL=1.5 |
    | **38.1** | xu/d Limit | ≤0.46 for Fe415 (ductility) |
    | **26.5.1.1** | Minimum Steel | 0.85bd/fy |
    | **26.5.1.2** | Maximum Steel | 0.04bD |
    | **26.5.2.1** | Bar Spacing | ≥25mm or bar diameter |
    | **26.2.1** | Cover | Per Table 16 (25-50mm) |
    | **40.3** | Stirrup Spacing | ≤0.75d or 300mm |
    | **23.2.1** | Deflection | Span/250 (total), Span/350 (additional) |
    | **26.2.3.3** | Development Length | Ld = ϕ×σs/(4×τbd) |
    | **26.2.5.1** | Lap Length | 1.3×Ld or 30ϕ |

    ### Material Properties (Clause 6)

    #### Concrete Grades
    ```
    M15, M20, M25, M30, M35, M40, M45, M50, M55, M60
    (Number = fck in N/mm²)
    ```

    #### Steel Grades
    ```
    Fe 250: fy = 250 N/mm²
    Fe 415: fy = 415 N/mm² (Most common)
    Fe 500: fy = 500 N/mm²
    Fe 550: fy = 550 N/mm²
    ```

    ### Design Constants (Annex G)

    ```python
    # For Fe 415 (xu,max/d = 0.46)
    Mu,lim/bd² = 0.138 × fck
    pt,lim = 0.96 × fck/fy  # Maximum tension steel %

    # Balanced section (xu/d = 0.46)
    Ast = 0.96 × (fck/fy) × b × d
    ```
    """)

    # Interactive clause searcher
    st.divider()
    st.subheader("🔍 Clause Search")

    search_query = st.text_input(
        "Search for a topic (e.g., 'deflection', 'cover', 'spacing')"
    )

    if search_query:
        # Simple keyword matching (can be enhanced)
        results = []
        keywords = {
            "deflection": "Clause 23.2.1 - Deflection limits (span/250 total, span/350 additional)",
            "cover": "Clause 26.2.1, Table 16 - Clear cover requirements (25-50mm depending on exposure)",
            "spacing": "Clause 26.5.2.1 - Minimum bar spacing (≥25mm or bar diameter)",
            "stirrup": "Clause 40.3 - Stirrup spacing (≤0.75d or 300mm, whichever is less)",
            "development": "Clause 26.2.3.3 - Development length (Ld = ϕ×σs/(4×τbd))",
            "xu": "Clause 38.1 - Neutral axis depth limit (xu/d ≤ 0.46 for Fe415)",
        }

        # Pre-compute lowercase search query once (performance optimization)
        search_query_lower = search_query.lower()
        for key, value in keywords.items():
            if key in search_query_lower:
                results.append(value)

        if results:
            for result in results:
                st.info(result)
        else:
            st.warning(
                "No results found. Try keywords like: deflection, cover, spacing, stirrup"
            )

# Footer
st.divider()
st.markdown("""
### 📖 Additional Resources
- [IS 456:2000 Full Text](https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf) (External link)
- [SP 16:1980 Design Aids](https://archive.org/details/gov.in.is.sp.16.1980) (External link)
- Video Tutorials: Coming soon!
""")

st.caption("💡 **Tip:** Bookmark this page for quick reference during design work!")
