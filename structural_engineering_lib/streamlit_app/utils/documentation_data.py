"""
Documentation Data Module
=========================

Contains all static data for the documentation page:
- IS 456 clause database
- FAQ content
- Glossary terms
- Reference tables

Author: STREAMLIT UI SPECIALIST (Agent 6)
Phase: STREAMLIT-IMPL-008
"""

# IS 456 Clause Database
IS456_CLAUSES = {
    "26.5.1": {
        "title": "Assumptions for Limit State of Collapse in Flexure",
        "category": "Flexure",
        "content": """
**Key Assumptions:**
1. Plane sections remain plane after bending
2. Maximum strain in concrete at outermost compression fiber: 0.0035
3. Tensile strength of concrete is ignored
4. Stresses in reinforcement below yield stress are taken as Es × ε
5. Maximum strain in tension reinforcement: 0.002 + (0.87fy/Es)

**Application:**
These assumptions form the basis for all flexural strength calculations.
        """,
        "equations": [
            "εc,max = 0.0035 (concrete compression strain)",
            "εs,max = 0.002 + 0.87fy/Es (steel tension strain)",
            "xu/d ≤ 0.48 for Fe415 (under-reinforced section)",
        ],
        "related": ["26.5.2", "G-1.1"],
    },
    "26.5.2.1": {
        "title": "Moment of Resistance - Singly Reinforced Beams",
        "category": "Flexure",
        "content": """
**Design Equation:**
Mu = 0.87 fy Ast d [1 - (Ast fy)/(b d fck)]

**Design Process:**
1. Calculate xu (neutral axis depth) from equilibrium
2. Check xu/d ≤ xu,max/d for ductile failure
3. Calculate moment capacity
4. If Mu < Mu,required → increase Ast or add compression steel
        """,
        "equations": [
            "xu = (0.87 fy Ast)/(0.36 fck b)",
            "Mu = 0.87 fy Ast (d - 0.42 xu)",
        ],
        "related": ["26.5.1", "G-1.1", "38.1"],
    },
    "40.1": {
        "title": "Shear Strength of Members without Shear Reinforcement",
        "category": "Shear",
        "content": """
**Design Shear Strength:**
τc = k τc,table

where:
- τc = Design shear strength of concrete
- k = Factor for depth effect = 1.0 for d ≤ 300mm
- τc,table = From IS 456 Table 19

**Critical Section:**
For beams with concentrated loads:
- Check at d from face of support
- For UDL: check at face of support
        """,
        "equations": ["τv = Vu/(b × d)", "τc = 0.85√(0.8 fck) × (Ast/bd)^(1/3) / (γm)"],
        "related": ["40.2", "40.3", "40.4"],
    },
    "40.4": {
        "title": "Minimum Shear Reinforcement",
        "category": "Shear",
        "content": """
**Requirement:**
Minimum shear reinforcement shall be provided such that:
Asv/(b × sv) ≥ 0.4/0.87fy

**Practical Limits:**
- Minimum stirrup diameter: 6mm
- Maximum spacing: 0.75d or 300mm, whichever is less
- For τv > τc,max, increase section size
        """,
        "equations": ["sv,max = min(0.75d, 300mm)", "Asv,min = 0.4 b sv / (0.87 fy)"],
        "related": ["40.1", "40.2", "40.3"],
    },
    "26.2.1": {
        "title": "Minimum Tension Reinforcement",
        "category": "Detailing",
        "content": """
**Code Requirement:**
Ast,min = 0.85 bd / fy (for rectangular sections)

**Purpose:**
1. Control cracking due to shrinkage and temperature
2. Ensure ductile failure (steel yields before concrete crushes)
3. Provide reserve strength
4. Avoid sudden brittle failure

**Practical Values:**
- For Fe415: Ast,min ≈ 0.2% of bd
- For Fe500: Ast,min ≈ 0.17% of bd
        """,
        "equations": ["Ast,min = 0.85 bd / fy", "ρmin = Ast,min/(bd) = 0.85/fy"],
        "related": ["26.5.1.1", "26.5.2"],
    },
    "23.2.1": {
        "title": "Nominal Cover to Reinforcement",
        "category": "Durability",
        "content": """
**Purpose:**
1. Protect steel from corrosion
2. Provide fire resistance
3. Ensure adequate bond
4. Protect reinforcement from external environment

**Minimum Cover (IS 456 Table 16):**
- Mild: 25mm (beams)
- Moderate: 30mm (beams)
- Severe: 45mm (beams)
- Very Severe: 50mm (beams)
- Extreme: 75mm (beams)
        """,
        "equations": [],
        "related": ["8.2", "16.1"],
    },
}

# FAQ Data
FAQ_DATA = {
    "General": [
        {
            "q": "What is the difference between characteristic strength and design strength?",
            "a": """
**Characteristic Strength (fck, fy):**
- The strength below which not more than 5% of test results are expected to fall
- Used in design equations directly
- Example: M25 concrete has fck = 25 N/mm²

**Design Strength:**
- Characteristic strength divided by partial safety factor (γm)
- For concrete: γm = 1.5
- For steel: γm = 1.15
- Design strength is used in stress checks
            """,
        },
        {
            "q": "When should I use doubly reinforced sections?",
            "a": """
Use doubly reinforced sections when:
1. **Moment demand exceeds balanced capacity:** Mu > Mu,lim
2. **Depth is restricted:** Architectural or functional constraints
3. **Improve ductility:** Better behavior under seismic loads
4. **Control long-term deflection:** Compression steel reduces creep
5. **Moment reversal:** Continuous beams, wind/earthquake loads
            """,
        },
        {
            "q": "What is the significance of xu/d ratio?",
            "a": """
**xu/d Ratio = Depth of neutral axis / Effective depth**

**Limits (IS 456):**
- For Fe415: xu,max/d = 0.48
- For Fe500: xu,max/d = 0.46
- For Fe550: xu,max/d = 0.44

**Purpose:**
1. Ensure under-reinforced (ductile) failure
2. Steel yields before concrete crushes
3. Large deflections warn of impending failure
4. Prevent sudden brittle collapse
            """,
        },
    ],
    "Flexure": [
        {
            "q": "How do I calculate effective depth (d)?",
            "a": """
**Formula:**
d = D - cover - φstirrup - φbar/2

**Example:**
For D = 500mm, cover = 25mm, 8mm stirrups, 20mm main bars:
d = 500 - 25 - 8 - 10 = 457 mm
            """,
        },
        {
            "q": "What is the minimum and maximum steel percentage?",
            "a": """
**Minimum Steel (Clause 26.5.1.1):**
- Ast,min = 0.85 bd / fy
- For Fe415: ρmin ≈ 0.205%
- For Fe500: ρmin ≈ 0.17%

**Maximum Steel (Clause 26.5.1.2):**
- Ast,max = 0.04 bD (4% of gross area)
- Purpose: prevent congestion, ensure proper compaction
            """,
        },
    ],
    "Shear": [
        {
            "q": "Why do we check shear at 'd' from support face?",
            "a": """
**Reason:**
1. **Arching Action:** Near supports, load transfers directly via compression strut
2. **Less Critical:** Shear stress is lower at 'd' from support than at face
3. **Conservative for UDL:** For concentrated loads, critical section depends on load location

**When to check at face:**
- Uniformly distributed loads (UDL)
- When required by code
- For corbels and brackets
            """,
        },
        {
            "q": "What if τv > τc,max?",
            "a": """
**If τv > τc,max:**
1. **Increase section dimensions** (preferred solution)
   - Increase width (b)
   - Increase effective depth (d)

2. **Use higher grade concrete**
   - Increases τc,max
   - Also improves flexural capacity

**Note:** Simply increasing stirrups won't help if τv > τc,max!
            """,
        },
    ],
}

# Glossary Data
GLOSSARY_DATA = {
    "A": [
        (
            "Anchorage Length",
            "Length required to develop full strength of reinforcing bar through bond.",
        ),
        ("Ast", "Area of tension steel reinforcement (mm²)."),
        ("Asc", "Area of compression steel reinforcement (mm²)."),
    ],
    "B": [
        (
            "Balanced Section",
            "Section where concrete and steel reach ultimate strain simultaneously.",
        ),
        ("Bond Stress (τbd)", "Shear stress at interface between concrete and steel."),
    ],
    "C": [
        (
            "Clear Cover",
            "Distance from surface of concrete to nearest surface of reinforcement.",
        ),
        (
            "Characteristic Strength",
            "Strength below which 5% of test results may fall.",
        ),
    ],
    "D": [
        (
            "d",
            "Effective depth - distance from compression face to centroid of tension steel (mm).",
        ),
        ("D", "Overall depth of beam section (mm)."),
        (
            "Development Length (Ld)",
            "Embedment length required to develop design stress in reinforcement.",
        ),
    ],
    "F": [
        ("fck", "Characteristic compressive strength of concrete (N/mm²)."),
        ("fy", "Characteristic yield strength of reinforcing steel (N/mm²)."),
    ],
    "M": [
        ("Mu", "Ultimate (factored) moment capacity (kN·m or N·mm)."),
    ],
    "N": [
        ("Neutral Axis", "Line in cross-section where stress/strain is zero."),
    ],
    "S": [
        (
            "Shear Reinforcement",
            "Stirrups or bent-up bars provided to resist shear forces.",
        ),
        ("sv", "Spacing of stirrups along beam length (mm)."),
    ],
    "T": [
        ("τv", "Nominal shear stress = Vu/(bd) (N/mm²)."),
        ("τc", "Design shear strength of concrete (from IS 456 Table 19) (N/mm²)."),
    ],
    "X": [
        ("xu", "Depth of neutral axis from compression face (mm)."),
    ],
}

# Reference Tables
REFERENCE_TABLES = {
    "Table 19: Design Shear Strength (τc)": {
        "title": "IS 456 Table 19: Design Shear Strength of Concrete (τc)",
        "data": {
            "pt (%)": [0.15, 0.25, 0.50, 0.75, 1.00, 1.25, 1.50],
            "M20": [0.28, 0.36, 0.48, 0.56, 0.62, 0.67, 0.72],
            "M25": [0.29, 0.36, 0.49, 0.57, 0.64, 0.70, 0.74],
            "M30": [0.29, 0.37, 0.50, 0.59, 0.66, 0.71, 0.76],
        },
        "notes": """
**Notes:**
- pt = 100 Ast / (b × d) = Percentage of tension reinforcement
- Interpolate for intermediate values
- For pt > 3%: use τc for 3%
        """,
        "hide_index": False,
    },
    "Table 20: Maximum Shear Stress (τc,max)": {
        "title": "IS 456 Table 20: Maximum Shear Stress (τc,max)",
        "data": {
            "Concrete Grade": ["M20", "M25", "M30", "M35", "M40"],
            "τc,max (N/mm²)": [2.8, 3.1, 3.5, 3.7, 4.0],
        },
        "notes": """
**Important:**
- If τv > τc,max, section dimensions must be increased
- Simply providing more stirrups will not help
        """,
        "hide_index": True,
    },
    "Table 16: Nominal Cover Requirements": {
        "title": "IS 456 Table 16: Nominal Cover to Meet Durability Requirements",
        "data": {
            "Exposure": ["Mild", "Moderate", "Severe", "Very Severe", "Extreme"],
            "Min Concrete": ["M20", "M25", "M30", "M35", "M40"],
            "Cover - Beams (mm)": [20, 30, 45, 50, 75],
        },
        "notes": """
**Exposure Conditions:**
- **Mild:** Interior of buildings (normal humidity)
- **Moderate:** Exterior surfaces, non-coastal
- **Severe:** Coastal areas (within 1km of sea)
- **Very Severe:** Structures in tidal zone
- **Extreme:** Surfaces in seawater, industrial chemical exposure
        """,
        "hide_index": True,
    },
    "Standard Bar Sizes and Areas": {
        "title": "Standard Bar Sizes and Cross-Sectional Areas",
        "data": {
            "Diameter (mm)": [8, 10, 12, 16, 20, 25, 32],
            "Area (mm²)": [50, 79, 113, 201, 314, 491, 804],
            "Weight (kg/m)": [0.395, 0.617, 0.888, 1.578, 2.466, 3.854, 6.313],
        },
        "notes": """
**Common Usage:**
- 8mm, 10mm: Stirrups, distribution steel
- 12mm, 16mm: Main bars in beams (small to medium spans)
- 20mm, 25mm: Main bars in beams (large spans), column bars
- 32mm: Column bars (large columns)
        """,
        "hide_index": True,
    },
}
