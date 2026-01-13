"""
Documentation and Reference Page
=================================

Interactive documentation for IS 456:2000 beam design.

Features:
- IS 456 clause reference with search
- Formula calculator
- Design examples
- FAQ and glossary
- Quick reference tables

Author: STREAMLIT UI SPECIALIST (Agent 6)
Phase: STREAMLIT-IMPL-008 | UI-002: Page Layout Redesign
"""

import streamlit as st
import pandas as pd
import math
from typing import Dict, List, Optional

# Import clause data and other helpers
from utils.documentation_data import (
    IS456_CLAUSES,
    FAQ_DATA,
    GLOSSARY_DATA,
    REFERENCE_TABLES,
)
from utils.layout import setup_page, page_header, section_header, info_panel
from utils.theme_manager import (
    apply_dark_mode_theme,
    render_theme_toggle,
    initialize_theme,
)

# Initialize theme
initialize_theme()

# Modern page setup
setup_page(title="Documentation - IS 456 Beam Design", icon="📚", layout="wide")

# Apply dark mode styling
apply_dark_mode_theme()

# Page header
page_header(
    title="Documentation & Reference",
    subtitle="IS 456:2000 Plain and Reinforced Concrete - Code of Practice",
    icon="📚",
)

# Sidebar navigation
st.sidebar.header("📑 Contents")
section = st.sidebar.radio(
    "Jump to section:",
    [
        "📖 IS 456 Clauses",
        "🧮 Formula Calculator",
        "📋 Examples",
        "❓ FAQ",
        "📊 Reference Tables",
        "📚 Glossary",
    ],
)

# IS 456 CLAUSE REFERENCE
if section == "📖 IS 456 Clauses":
    section_header("IS 456:2000 Clause Reference", icon="📖")

    # Search functionality
    search_query = st.text_input(
        "🔍 Search clauses",
        placeholder="e.g., 'limit state', 'flexure', 'minimum reinforcement'",
        help="Search by clause number, keyword, or topic",
    )

    # Filter clauses based on search
    if search_query:
        filtered_clauses = {
            k: v
            for k, v in IS456_CLAUSES.items()
            if search_query.lower() in k.lower()
            or search_query.lower() in v["title"].lower()
            or search_query.lower() in v["content"].lower()
            or search_query.lower() in v["category"].lower()
        }
    else:
        filtered_clauses = IS456_CLAUSES

    # Display clause count
    st.info(f"📚 Showing {len(filtered_clauses)} of {len(IS456_CLAUSES)} clauses")

    # Group by category
    categories = {}
    for clause_num, clause_data in filtered_clauses.items():
        cat = clause_data["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((clause_num, clause_data))

    # Display clauses by category
    for category, clause_list in sorted(categories.items()):
        with st.expander(
            f"📂 {category} ({len(clause_list)} clauses)",
            expanded=(len(categories) == 1),
        ):
            for clause_num, clause_data in sorted(clause_list):
                st.subheader(f"Clause {clause_num}: {clause_data['title']}")

                # Content
                st.markdown(clause_data["content"])

                # Equations (if any)
                if clause_data.get("equations"):
                    st.markdown("**Key Equations:**")
                    for eq in clause_data["equations"]:
                        st.code(eq, language="text")

                # Related clauses
                if clause_data.get("related"):
                    related_str = ", ".join(clause_data["related"])
                    st.markdown(f"**Related Clauses:** {related_str}")

                st.divider()

# FORMULA CALCULATOR
elif section == "🧮 Formula Calculator":
    st.header("🧮 Formula Calculator")
    st.markdown("*Quick calculations for common design formulas*")

    calc_type = st.selectbox(
        "Select calculation type:",
        [
            "Moment of Resistance (Singly Reinforced)",
            "Neutral Axis Depth",
            "Steel Area Required",
            "Shear Stress",
            "Stirrup Spacing",
            "Development Length",
        ],
    )

    col1, col2 = st.columns(2)

    if calc_type == "Moment of Resistance (Singly Reinforced)":
        with col1:
            st.subheader("Inputs")
            Ast = st.number_input(
                "Ast (mm²)", value=804.0, step=50.0, help="Area of tension steel"
            )
            d = st.number_input(
                "d (mm)", value=450.0, step=10.0, help="Effective depth"
            )
            b = st.number_input("b (mm)", value=300.0, step=10.0, help="Width")
            fck = st.number_input(
                "fck (N/mm²)", value=25.0, step=5.0, help="Concrete grade"
            )
            fy = st.number_input(
                "fy (N/mm²)", value=500.0, step=50.0, help="Steel grade"
            )

        with col2:
            st.subheader("Results")

            # Calculate xu
            denominator = 0.36 * fck * b
            xu = (0.87 * fy * Ast) / denominator if denominator > 0 else 0

            # Check under-reinforced
            xu_max = 0.48 * d  # For Fe500
            is_under_reinforced = xu <= xu_max

            # Calculate Mu
            Mu = 0.87 * fy * Ast * (d - 0.42 * xu) / 1_000_000  # Convert to kN·m

            st.metric("Neutral Axis Depth (xu)", f"{xu:.2f} mm")
            xu_d_ratio = xu / d if d > 0 else 0
            st.metric("xu/d Ratio", f"{xu_d_ratio:.3f}")

            if is_under_reinforced:
                st.success(f"✅ Under-reinforced (xu/d = {xu_d_ratio:.3f} ≤ 0.48)")
            else:
                st.error(f"❌ Over-reinforced! (xu/d = {xu_d_ratio:.3f} > 0.48)")
                st.warning("⚠️ Add compression steel or increase depth")

            st.metric("Moment Capacity (Mu)", f"{Mu:.2f} kN·m")

            st.divider()
            st.markdown("**Formula:**")
            st.latex(r"M_u = 0.87 f_y A_{st} \left(d - 0.42 x_u\right)")
            st.latex(r"x_u = \frac{0.87 f_y A_{st}}{0.36 f_{ck} b}")

    elif calc_type == "Steel Area Required":
        with col1:
            st.subheader("Inputs")
            Mu = st.number_input(
                "Mu (kN·m)", value=120.0, step=10.0, help="Factored moment"
            )
            d = st.number_input(
                "d (mm)", value=450.0, step=10.0, help="Effective depth"
            )
            b = st.number_input("b (mm)", value=300.0, step=10.0, help="Width")
            fck = st.number_input(
                "fck (N/mm²)", value=25.0, step=5.0, help="Concrete grade"
            )
            fy = st.number_input(
                "fy (N/mm²)", value=500.0, step=50.0, help="Steel grade"
            )

        with col2:
            st.subheader("Results")

            # Convert Mu to N·mm
            Mu_nmm = Mu * 1_000_000

            # Calculate Ru
            denominator = b * d**2
            Ru = Mu_nmm / denominator if denominator > 0 else 0

            # Calculate ρ
            if fy > 0 and fck > 0:
                rho = (0.5 * fck / fy) * (1 - (1 - (4.6 * Ru) / (fck)) ** 0.5)
            else:
                rho = 0

            # Calculate Ast
            Ast_req = rho * b * d

            # Check minimum
            Ast_min = 0.85 * b * d / fy if fy > 0 else 0
            Ast_final = max(Ast_req, Ast_min)

            st.metric("Ru (N/mm²)", f"{Ru:.3f}")
            st.metric("Steel Ratio (ρ)", f"{rho*100:.3f}%")
            st.metric("Ast Required", f"{Ast_req:.0f} mm²")
            st.metric("Ast Minimum", f"{Ast_min:.0f} mm²")
            st.metric(
                "Ast Final",
                f"{Ast_final:.0f} mm²",
                delta=f"{Ast_final - Ast_req:.0f} mm²" if Ast_final > Ast_req else None,
            )

            # Suggest bar configuration
            st.divider()
            st.markdown("**Suggested Bar Configurations:**")
            bar_sizes = [12, 16, 20, 25]
            for bar_dia in bar_sizes:
                bar_area = 3.14159 * (bar_dia / 2) ** 2
                if bar_area > 0:
                    try:
                        num_bars = int(Ast_final / bar_area) + 1
                    except (TypeError, ValueError):
                        num_bars = 0
                else:
                    num_bars = 0
                provided_area = num_bars * bar_area
                if 2 <= num_bars <= 6 and provided_area >= Ast_final:
                    st.code(f"{num_bars}-{bar_dia}mm (Ast = {provided_area:.0f} mm²)")

    elif calc_type == "Stirrup Spacing":
        with col1:
            st.subheader("Inputs")
            Vu = st.number_input(
                "Vu (kN)", value=85.0, step=5.0, help="Factored shear force"
            )
            b = st.number_input("b (mm)", value=300.0, step=10.0, help="Width")
            d = st.number_input(
                "d (mm)", value=450.0, step=10.0, help="Effective depth"
            )
            fck = st.number_input("fck (N/mm²)", value=25.0, step=5.0)
            Ast = st.number_input(
                "Ast (mm²)", value=804.0, step=50.0, help="Tension steel area"
            )
            stirrup_dia = st.number_input("Stirrup φ (mm)", value=8.0, step=2.0)
            stirrup_legs = st.number_input(
                "Number of legs", value=2, step=1, min_value=2
            )
            fy_stirrup = st.number_input("fy stirrup (N/mm²)", value=415.0, step=50.0)

        with col2:
            st.subheader("Results")

            # Calculate τv
            denominator = b * d
            tau_v = (Vu * 1000) / denominator if denominator > 0 else 0

            # Calculate τc (simplified)
            pt = 100 * Ast / denominator if denominator > 0 else 0
            tau_c = 0.85 * (0.8 * fck) ** 0.5 * (pt / 100) ** (1 / 3) / 1.5 if pt > 0 else 0

            # Calculate required Asv/sv
            if tau_v > tau_c:
                Vus = (tau_v - tau_c) * b * d / 1000
                Asv = stirrup_legs * 3.14159 * (stirrup_dia / 2) ** 2
                sv_req = (0.87 * fy_stirrup * Asv * d) / (Vus * 1000) if Vus > 0 else math.inf
            else:
                sv_req = math.inf

            # Maximum spacing
            sv_max = min(0.75 * d, 300)

            # Final spacing
            sv_final = min(sv_req, sv_max, 300) if tau_v > tau_c else sv_max

            st.metric("τv", f"{tau_v:.3f} N/mm²")
            st.metric("τc", f"{tau_c:.3f} N/mm²")

            if tau_v > tau_c:
                st.warning(f"⚠️ Shear reinforcement required (τv > τc)")
                st.metric("Required Spacing", f"{sv_req:.0f} mm")
            else:
                st.success("✅ Shear reinforcement not required (provide minimum)")

            st.metric("Maximum Spacing", f"{sv_max:.0f} mm")
            st.metric("Final Spacing", f"{sv_final:.0f} mm")

            # Provide recommendation
            standard_spacings = [75, 100, 125, 150, 175, 200, 250, 300]
            recommended = min(
                [s for s in standard_spacings if s <= sv_final], default=75
            )

            st.info(
                f"💡 Recommended: {stirrup_legs}-legged {stirrup_dia}mm @ {recommended}mm c/c"
            )

# EXAMPLES
elif section == "📋 Examples":
    st.header("📋 Design Examples")

    example_selection = st.selectbox(
        "Select an example:",
        [
            "Example 1: Simply Supported Beam (4m span)",
            "Example 2: Doubly Reinforced Section",
            "Example 3: Shear Design with Stirrups",
        ],
    )

    if "Example 1" in example_selection:
        st.subheader("Example 1: Simply Supported Beam")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown(
                """
**Given Data:**
- Span: 4.0 m (c/c of supports)
- Dead load: 10 kN/m (including self-weight)
- Live load: 15 kN/m
- Width: 230 mm
- Overall depth: 450 mm
- Clear cover: 25 mm
- Concrete: M20 (fck = 20 N/mm²)
- Steel: Fe415 (fy = 415 N/mm²)
- Exposure: Mild

**Required:**
1. Design for flexure
2. Design for shear
3. Check deflection
4. Detailing
            """
            )

        with col2:
            st.markdown(
                """
**Solution:**

**Step 1: Load Calculation**
- Factored load = 1.5 × (10 + 15) = 37.5 kN/m
- Max moment = wL²/8 = 37.5 × 4²/8 = 75 kN·m
- Max shear = wL/2 = 37.5 × 4/2 = 75 kN

**Step 2: Effective Depth**
- d = D - cover - φstirrup - φbar/2
- d = 450 - 25 - 8 - 8 = 409 mm
- Use d = 410 mm

**Step 3: Flexural Design**
- Mu,lim = 0.138 fck bd²
- Mu,lim = 0.138 × 20 × 230 × 410² / 10⁶ = 106.5 kN·m
- Mu < Mu,lim → Singly reinforced section OK
- Ast = 575 mm²
- Provide 3-16mm bars (Ast = 603 mm²) ✅

**Step 4: Shear Design**
- τv = 0.795 N/mm²
- τc = 0.49 N/mm² (from Table 19)
- τv > τc → Provide shear reinforcement
- Use 2L-8mm @ 150mm c/c ✅
            """
            )

        st.success("✅ Design Complete: 3-16mm + 2L-8mm @ 150mm c/c")

# FAQ
elif section == "❓ FAQ":
    st.header("❓ Frequently Asked Questions")

    # Display FAQs by category
    for category, qa_list in FAQ_DATA.items():
        st.subheader(f"📂 {category}")
        for qa in qa_list:
            with st.expander(f"**Q:** {qa['q']}", expanded=False):
                st.markdown(qa["a"])

# REFERENCE TABLES
elif section == "📊 Reference Tables":
    st.header("📊 Quick Reference Tables")

    table_selection = st.selectbox(
        "Select table:",
        [
            "Table 19: Design Shear Strength (τc)",
            "Table 20: Maximum Shear Stress (τc,max)",
            "Table 16: Nominal Cover Requirements",
            "Standard Bar Sizes and Areas",
        ],
    )

    # Display selected table from REFERENCE_TABLES
    if table_selection in REFERENCE_TABLES:
        table_data = REFERENCE_TABLES[table_selection]

        st.subheader(table_data["title"])

        df = pd.DataFrame(table_data["data"])
        st.dataframe(
            df, width="stretch", hide_index=table_data.get("hide_index", False)
        )

        if "notes" in table_data:
            st.info(table_data["notes"])

# GLOSSARY
elif section == "📚 Glossary":
    st.header("📚 Technical Glossary")

    # Display glossary by letter
    for letter, terms in sorted(GLOSSARY_DATA.items()):
        with st.expander(f"📖 {letter}", expanded=False):
            for term, definition in terms:
                st.markdown(f"**{term}:** {definition}")
                st.divider()

# Footer
st.divider()
st.markdown(
    """
<div style='text-align: center; color: gray; font-size: 0.9em;'>
📚 IS 456:2000 Plain and Reinforced Concrete - Code of Practice<br>
Bureau of Indian Standards, New Delhi<br>
<br>
<em>This documentation is for educational purposes. Always refer to the official IS 456:2000 code for design.</em>
</div>
""",
    unsafe_allow_html=True,
)
