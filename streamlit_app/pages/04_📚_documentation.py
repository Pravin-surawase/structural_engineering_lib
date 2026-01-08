"""
Documentation Page
==================

User guides, examples, and help resources.

Sections:
- Quick start guide
- Design examples
- API reference
- IS 456 clause index
- Troubleshooting
"""

import streamlit as st

st.set_page_config(
    page_title="Documentation | IS 456 Dashboard",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Documentation & Help")

st.markdown("### 🎯 Quick Links")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **📖 User Guide**
    - [Getting Started](#getting-started)
    - [Design Workflow](#design-workflow)
    - [Understanding Results](#understanding-results)
    """)

with col2:
    st.markdown("""
    **💡 Examples**
    - [Simple Beam Design](#example-simple)
    - [Continuous Beam](#example-continuous)
    - [Cost Optimization](#example-cost)
    """)

with col3:
    st.markdown("""
    **🔧 Reference**
    - [IS 456 Clauses](#is-456-reference)
    - [Material Properties](#material-properties)
    - [API Documentation](#api-docs)
    """)

st.markdown("---")

# Getting Started Section
st.markdown("### 🚀 Getting Started")

st.markdown("""
#### Installation

**Option 1: Streamlit Cloud (Recommended)**
```bash
# No installation needed - use the web app directly
# URL: https://your-app.streamlit.app
```

**Option 2: Local Installation**
```bash
# Clone repository
git clone https://github.com/your-repo/structural-lib.git

# Install dependencies
cd structural-lib/streamlit_app
pip install -r requirements.txt

# Run app
streamlit run app.py
```

#### Basic Workflow

1. **Navigate** to Beam Design page
2. **Enter** beam parameters in sidebar
3. **Click** "Analyze Design"
4. **Review** results in tabs
5. **Export** if needed
""")

st.markdown("---")

# Example Section
st.markdown("### 💡 Example: 5m Simply Supported Beam")

with st.expander("View complete example", expanded=False):
    st.markdown("""
    **Given:**
    - Span: 5000 mm
    - Width: 300 mm
    - Total Depth: 500 mm
    - Effective Depth: 450 mm (assuming 40mm cover + 8mm stirrup)
    - Materials: M25 concrete, Fe500 steel
    - Loading: Mu = 120 kNm, Vu = 80 kN

    **Design Steps:**

    1. **Flexure Design**
       - Calculate limiting moment: Mu,lim = 0.138 × fck × b × d² = 185.6 kNm
       - Required steel: Ast = 655 mm²
       - Provide: 3-16mm bars (603 mm²) ✅

    2. **Shear Design**
       - Nominal shear stress: τv = Vu/(b×d) = 0.59 N/mm²
       - Design shear strength: τc = 0.48 N/mm² (from Table 19)
       - Required stirrups: 2L-8φ @ 175 mm c/c ✅

    3. **Deflection Check**
       - Span/depth = 5000/450 = 11.1
       - Maximum allowed = 20 (Cl. 23.2.1)
       - Status: ✅ PASS

    **Result:** Design is safe and economical!
    """)

st.markdown("---")

# IS 456 Reference
st.markdown("### 📋 IS 456 Quick Reference")

st.markdown("""
#### Key Clauses

| Clause | Topic | Description |
|--------|-------|-------------|
| **23.2** | Deflection | Span/depth ratios, deflection limits |
| **26.5.1** | Minimum Steel | 0.85 bd/fy (tension), 0.12 bD/100 (total) |
| **35.3.2** | Crack Width | Maximum 0.3mm (exposure dependent) |
| **38.1** | Flexure | Moment of resistance, steel area |
| **40.1** | Shear | Shear strength, stirrup design |

**Full Reference:** [IS 456:2000 PDF](https://example.com/is456.pdf)
""")

st.markdown("---")

# Troubleshooting
st.markdown("### 🔧 Troubleshooting")

with st.expander("App won't start"):
    st.markdown("""
    **Problem:** `streamlit run app.py` fails

    **Solutions:**
    1. Check Python version: `python --version` (need 3.10+)
    2. Install dependencies: `pip install -r requirements.txt`
    3. Verify streamlit: `streamlit --version`
    """)

with st.expander("Design fails with 'Section too small'"):
    st.markdown("""
    **Problem:** Section depth inadequate for applied moment

    **Solutions:**
    1. Increase depth (D)
    2. Increase width (b)
    3. Use higher grade concrete (M30 instead of M25)
    4. Check if compression steel is needed
    """)

with st.expander("Cost optimization shows no solutions"):
    st.markdown("""
    **Problem:** No feasible bar arrangements found

    **Solutions:**
    1. Check if required Ast is too large for width
    2. Reduce cover if possible
    3. Consider multiple layers of bars
    4. Review min spacing requirements
    """)

st.markdown("---")

# Contact Section
st.markdown("### 📞 Support")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Report Issues**
    - [GitHub Issues](https://github.com/your-repo/issues)
    - [Email Support](mailto:support@example.com)
    """)

with col2:
    st.markdown("""
    **Resources**
    - [Video Tutorials](https://youtube.com/your-channel)
    - [API Documentation](https://docs.example.com)
    """)
