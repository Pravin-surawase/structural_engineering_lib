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
Version: 0.1.0 (Phase 2 - Implementation)
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="IS 456 Beam Design Dashboard",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/issues',
        'Report a bug': 'https://github.com/your-repo/issues',
        'About': '# IS 456 Beam Design Dashboard\n\nProfessional RC design per IS 456:2000'
    }
)

# Custom CSS for typography and styling
st.markdown("""
<style>
    /* Import Inter font for better readability */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    /* Apply Inter to all text */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Apply JetBrains Mono to code and numbers */
    code, pre, [class*="css"] code {
        font-family: 'JetBrains Mono', monospace;
    }

    /* Improve metric styling */
    [data-testid="stMetric"] {
        background-color: #F0F2F6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF6600;
    }

    /* Style success/error messages */
    .stAlert {
        border-radius: 0.5rem;
        padding: 1rem;
    }

    /* Improve button styling */
    .stButton>button {
        border-radius: 0.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 102, 0, 0.3);
    }

    /* Hero section styling */
    .hero {
        background: linear-gradient(135deg, #003366 0%, #004d99 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        text-align: center;
    }

    .hero h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }

    .hero p {
        font-size: 1.25rem;
        opacity: 0.9;
    }

    /* Feature card styling */
    .feature-card {
        background: #F0F2F6;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 4px solid #FF6600;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }

    .feature-card:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .feature-card h3 {
        color: #003366;
        margin-bottom: 0.5rem;
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .hero h1 {
            font-size: 2rem;
        }
        .hero p {
            font-size: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Hero section
st.markdown("""
<div class="hero">
    <h1>🏗️ IS 456 Beam Design Dashboard</h1>
    <p>Professional reinforced concrete design per IS 456:2000</p>
</div>
""", unsafe_allow_html=True)

# Welcome message
st.markdown("## Welcome to the Professional Beam Design Tool")

st.markdown("""
This dashboard provides comprehensive RC beam design capabilities following **IS 456:2000** standards.
Design with confidence using our intelligent analysis tools and instant cost optimization.
""")

# Feature overview
st.markdown("### 🎯 Key Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>🏗️ Beam Design</h3>
        <p>Complete flexure, shear, and detailing design with real-time validation and visual feedback.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <h3>✅ Compliance Checking</h3>
        <p>Automated IS 456 clause verification with detailed compliance reports and suggestions.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>💰 Cost Optimization</h3>
        <p>Find the most economical bar arrangements while maintaining safety and constructability.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card">
        <h3>📚 Documentation</h3>
        <p>Export to DXF drawings, bar bending schedules, and comprehensive design reports.</p>
    </div>
    """, unsafe_allow_html=True)

# Quick start guide
st.markdown("---")
st.markdown("### 🚀 Quick Start")

st.markdown("""
1. **Navigate** to the **Beam Design** page from the sidebar
2. **Enter** your beam parameters (span, dimensions, materials, loading)
3. **Click** "Analyze Design" to get instant results
4. **Review** flexure, shear, and serviceability checks
5. **Export** drawings, BBS, or reports as needed

💡 **Tip:** Use the example designs in each section to get started quickly!
""")

# Status indicators
st.markdown("---")
st.markdown("### 📊 System Status")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Version", "0.1.0", help="Dashboard version")

with col2:
    st.metric("Library", "0.15.0", help="structural-lib-is456 version")

with col3:
    st.metric("Code", "IS 456:2000", help="Design code standard")

with col4:
    st.metric("Status", "✅ Ready", help="System operational")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; opacity: 0.6; padding: 2rem 0;">
    <p>Built with Streamlit • Following WCAG 2.1 Level AA accessibility standards</p>
    <p>© 2026 IS 456 Structural Engineering Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📋 Navigation")
    st.info("""
    Use the pages above to navigate between different features:

    - **🏗️ Beam Design:** Main design workflow
    - **💰 Cost Optimizer:** Find economical solutions
    - **✅ Compliance:** IS 456 checking
    - **📚 Documentation:** Help & examples
    """)

    st.markdown("---")
    st.markdown("### 🎨 Theme")
    st.markdown("""
    This dashboard uses the **IS 456 Professional Theme**:
    - **Navy Blue** (#003366) - Primary text
    - **Orange** (#FF6600) - Highlights
    - **Colorblind-safe** palette
    """)

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    **Version:** 0.1.0
    **Phase:** Implementation
    **Status:** Active Development

    [📖 Documentation](https://github.com/your-repo/docs)
    [🐛 Report Issue](https://github.com/your-repo/issues)
    """)
