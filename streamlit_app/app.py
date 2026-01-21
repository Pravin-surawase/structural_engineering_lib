"""
IS 456 Structural Engineering Dashboard
=========================================

A professional Streamlit dashboard for RC beam design per IS 456:2000.

Features:
- Interactive beam design
- Cost optimization
- Compliance checking
- Export to DXF, BBS

Author: STREAMLIT UI SPECIALIST (Agent 6)
Version: 0.19.0 (Streamlit app release)
"""

import streamlit as st
from utils.layout import setup_page, page_header, info_panel, section_header
from utils.design_system import COLORS
from utils.theme_manager import (
    apply_dark_mode_theme,
    render_theme_toggle,
    initialize_theme,
)

# Initialize theme
initialize_theme()

# Modern page setup
setup_page(title="IS 456 Beam Design Dashboard", icon="🏗️", layout="wide")

# Apply dark mode styling
apply_dark_mode_theme()

# Hero section with professional styling
page_header(
    title="IS 456 Beam Design Dashboard",
    subtitle="Professional reinforced concrete design per IS 456:2000",
    icon="🏗️",
)

# Welcome message
st.markdown("## Welcome to the Professional Beam Design Tool")

st.markdown(
    """
This dashboard provides comprehensive RC beam design capabilities following **IS 456:2000** standards.
Design with confidence using our intelligent analysis tools and instant cost optimization.
"""
)

# Feature overview
section_header("Key Features", icon="🎯")

col1, col2 = st.columns(2)

with col1:
    info_panel(
        message="Complete flexure, shear, and detailing design with real-time validation and visual feedback.",
        title="Beam Design",
        icon="🏗️",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    info_panel(
        message="Automated IS 456 clause verification with detailed compliance reports and suggestions.",
        title="Compliance Checking",
        icon="✅",
    )

with col2:
    info_panel(
        message="Find the most economical bar arrangements while maintaining safety and constructability.",
        title="Cost Optimization",
        icon="💰",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    info_panel(
        message="Export to DXF drawings, bar bending schedules, and comprehensive design reports.",
        title="Documentation",
        icon="📚",
    )

# Quick start guide
st.markdown("---")
section_header("Quick Start", icon="🚀")

st.markdown(
    """
1. **Navigate** to the **Beam Design** page from the sidebar
2. **Enter** your beam parameters (span, dimensions, materials, loading)
3. **Click** "Analyze Design" to get instant results
4. **Review** flexure, shear, and serviceability checks
5. **Export** drawings, BBS, or reports as needed

💡 **Tip:** Use the example designs in each section to get started quickly!
"""
)

# Status indicators
st.markdown("---")
section_header("System Status", icon="📊")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Version", "0.19.0", help="Dashboard version")

with col2:
    st.metric("Library", "0.19.0", help="structural-lib-is456 version")

with col3:
    st.metric("Code", "IS 456:2000", help="Design code standard")

with col4:
    st.metric("Status", "✅ Ready", help="System operational")

# Footer
st.markdown("---")
st.markdown(
    """
<div style="text-align: center; opacity: 0.6; padding: 2rem 0;">
    <p>Built with Streamlit • Following WCAG 2.1 Level AA accessibility standards</p>
    <p>© 2026 IS 456 Structural Engineering Dashboard</p>
</div>
""",
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.markdown("### 📋 Navigation")
    st.info(
        """
    **Core Features:**

    - **🏗️ Beam Design:** Main design workflow
    - **💰 Cost Optimizer:** Find economical solutions
    - **✅ Compliance:** IS 456 checking
    - **📚 Documentation:** Help & examples

    *More features coming soon!*
    """
    )

    # Theme toggle
    render_theme_toggle()

    st.markdown("---")
    st.markdown("### 🎨 Theme")
    st.markdown(
        """
    This dashboard uses the **IS 456 Professional Theme**:
    - **Navy Blue** (#003366) - Primary text
    - **Orange** (#FF6600) - Highlights
    - **Colorblind-safe** palette
    """
    )

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown(
        """
    **Version:** 0.19.0
    **Library:** structural-lib-is456
    **Code:** IS 456:2000

    [📖 Documentation](https://github.com/Pravin-surawase/structural_engineering_lib/tree/main/docs)
    [🐛 Report Bug](https://github.com/Pravin-surawase/structural_engineering_lib/issues/new?template=bug_report.yml)
    [✨ Request Feature](https://github.com/Pravin-surawase/structural_engineering_lib/issues/new?template=feature_request.yml)
    [❓ Ask Question](https://github.com/Pravin-surawase/structural_engineering_lib/issues/new?template=support.yml)
    """
    )

    st.markdown("---")
    st.markdown("### 💬 Feedback")
    st.markdown(
        """
    Help us improve! Your feedback shapes future versions.

    [![PyPI Stats](https://img.shields.io/pypi/dm/structural-lib-is456)](https://pypistats.org/packages/structural-lib-is456)
    """
    )
