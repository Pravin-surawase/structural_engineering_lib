# IS 456 Beam Design Dashboard

**Professional Streamlit dashboard for RC beam design per IS 456:2000**

> **Status: Legacy UI** — The primary frontend is now **React 19 + React Three Fiber** (`react_app/`).
> Streamlit remains functional and maintained for features not yet ported to React.
> See [Migration Status](#migration-status) below for details.

![Version](https://img.shields.io/badge/version-0.19.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.53+-red)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🎯 Features

- **⚡ AI Assistant v2** - Chat-based structural design with dynamic workspace, 3D building visualization, and interactive rebar editor
- **🏗️ Interactive Beam Design** - Complete flexure, shear, and detailing design with live visualization
- **💰 Cost Optimization** - Find the most economical bar arrangements
- **✅ Compliance Checking** - Automated IS 456 clause verification with pass/fail status
- **📥 Multi-Format Import** - Import beam data from ETABS, SAFE, and custom CSV files
- **📐 DXF Export** - CAD-ready drawings for beam sections and elevations
- **📄 PDF Reports** - Professional design reports with IS 456 references
- **📚 Documentation** - Interactive tutorials and IS 456 references

---

## 🚀 Quick Start

### Option 1: Web App (Recommended)

Visit: **[https://your-app.streamlit.app](https://your-app.streamlit.app)**

No installation needed!

### Option 2: Local Installation

**Requirements:**
- Python 3.9 or higher
- pip package manager

**Installation:**

```bash
# Clone repository
git clone https://github.com/your-repo/structural-lib.git
cd structural-lib

# Install the library with all dependencies
pip install -e Python[full]

# Run app
cd streamlit_app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📖 Usage

### Basic Workflow

1. **Navigate** to the **Beam Design** page from the sidebar
2. **Enter** your beam parameters:
   - Geometry (span, width, depth)
   - Materials (concrete grade, steel grade)
   - Loading (moment, shear)
3. **Click** "Analyze Design" to get instant results
4. **Review** results in tabs:
   - Summary (key metrics, utilization)
   - Visualization (cross-section diagram with stirrups)
   - Cost Analysis (bar arrangement options)
   - Compliance (IS 456 checks with clause references)
   - Export (PDF, DXF, BBS)
5. **Export** your design in your preferred format

### Example: 5m Simply Supported Beam

```
# Inputs
Span: 5000 mm
Width: 300 mm
Depth: 500 mm
Materials: M25 / Fe500
Moment: 120 kNm
Shear: 80 kN

# Results
✅ Design OK
Steel: 3-16mm bars (603 mm²)
Stirrups: 2L-8φ @ 175 mm c/c
Utilization: 65%
```

---

## 📁 Project Structure

```
streamlit_app/
├── app.py                              # Home page
├── pages/
│   ├── 01_🏗️_beam_design.py            # Main design page
│   ├── 02_💰_cost_optimizer.py          # Cost optimization
│   ├── 03_✅_compliance.py              # IS 456 compliance checking
│   ├── 04_📚_documentation.py           # Help & examples
│   ├── 05_3d_viewer_demo.py             # 3D visualization demo
│   ├── 06_📤_etabs_import.py            # ETABS import
│   ├── 07_📥_multi_format_import.py     # Multi-format CSV/Excel import
│   ├── 10_🤖_ai_assistant.py            # AI Assistant v1 (legacy)
│   ├── 11_⚡_ai_assistant_v2.py          # AI Assistant v2 (recommended)
│   └── 90_feedback.py                   # User feedback
├── components/
│   ├── __init__.py
│   ├── ai_workspace.py                 # Dynamic workspace for AI v2
│   ├── inputs.py                       # Input widgets
│   ├── visualizations.py               # Plotly charts & beam diagrams
│   ├── visualizations_3d.py            # 3D beam visualization
│   └── results.py                      # Result displays
├── utils/
│   ├── __init__.py
│   ├── api_wrapper.py                  # Cached API calls
│   ├── design_system.py                # Design tokens (colors, typography)
│   ├── global_styles.py                # CSS styling
│   ├── error_handler.py                # Input validation
│   ├── session_manager.py              # State management
│   └── layout.py                       # Page layout utilities
├── tests/
│   ├── conftest.py                     # Test fixtures
│   ├── test_page_smoke.py              # Page import tests
│   └── test_critical_journeys.py       # E2E journey tests
├── .streamlit/
│   ├── config.toml                     # Theme configuration
│   └── secrets.toml.example            # Example secrets (OpenAI API key)
├── requirements.txt                    # Dependencies
└── README.md                           # This file
```

---

## 🎨 Design Philosophy

### Theme: IS 456 Professional

- **Colors:** Navy blue (#003366), Orange (#FF6600), Colorblind-safe palette
- **Accessibility:** WCAG 2.1 Level AA compliant
- **Typography:** Inter (body), JetBrains Mono (code/numbers)

### User Experience

- **Input-Output Split:** Sidebar for inputs, main area for results
- **Progressive Disclosure:** Advanced options hidden in expanders
- **Real-Time Validation:** Immediate feedback as you type
- **Friendly Errors:** Clear messages with fix suggestions
- **Practical Values:** Stirrup spacings rounded to construction-friendly values (75, 100, 125... 300mm)

---

## 🧪 Testing

### Run Tests

```bash
# All Streamlit tests
cd streamlit_app
pytest tests/ -v

# Specific test file
pytest tests/test_page_fixes_2026_01_13.py -v

# Core library tests
cd ../Python
pytest tests/ -v
```

### Static Analysis

```bash
# Streamlit-specific scanner (checks for runtime errors)
.venv/bin/python scripts/check_streamlit.py --all-pages

# Pylint
.venv/bin/python -m pylint --rcfile=.pylintrc-streamlit streamlit_app/
```

---

## 📊 Test Coverage

| Test Category | Tests | Description |
|---------------|-------|-------------|
| Page Smoke | 43 | Import tests, structure, design system |
| Critical Journeys | 16 | E2E user workflows |
| Regression | 20 | Bug fix verification |
| Integration | 25+ | API wrapper, components |

---

## 🤝 Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dev dependencies
pip install -e Python[dev,full]

# Run in development mode
cd streamlit_app
streamlit run app.py --server.runOnSave true
```

---

## 📚 Documentation

- **User Guide:** [docs/getting-started/](../docs/getting-started/)
- **API Reference:** [docs/reference/api.md](../docs/reference/api.md)
- **Architecture:** [docs/architecture/](../docs/architecture/)
- **Streamlit Research:** [docs/research/](../docs/research/)

---

## 📝 License

MIT License - see [LICENSE](../LICENSE) for details

---

## 🙏 Acknowledgments

- **IS 456:2000** - Bureau of Indian Standards
- **Streamlit** - Amazing framework for data apps
- **Plotly** - Interactive visualization library
- **structural-lib-is456** - Core design library

---

## Migration Status

The project is migrating from Streamlit to **React 19 + React Three Fiber + FastAPI**.
The React app (`react_app/`) is the primary frontend going forward.

### Feature Parity

| Feature | Streamlit | React | Notes |
|---------|-----------|-------|-------|
| Single beam design | ✅ | ✅ | **Parity achieved** |
| CSV import (40+ columns) | ✅ | ✅ | **Parity achieved** |
| 3D visualization | ✅ Plotly | ✅ R3F | React is superior (WebGL) |
| Export (BBS/DXF/Report) | ✅ | ✅ | **Parity achieved** |
| Dashboard insights | ✅ | ✅ | **Parity achieved** |
| Rebar suggestions | ✅ | ✅ | **Parity achieved** |
| Cost optimizer | ✅ | -- | Streamlit only |
| Compliance checker | ✅ | -- | Streamlit only |
| AI Assistant v2 | ✅ | -- | Streamlit only |
| Batch design (full UI) | ✅ | -- | API exists, React UI pending |
| Learning center / Docs | ✅ | -- | Streamlit only |

### What This Means

- **Use React** (`react_app/`) for core beam design, CSV import, 3D visualization, and exports.
- **Use Streamlit** for cost optimization, compliance checking, and AI assistant until React ports are complete.
- **New features** should be built in React, not Streamlit.
- **Bug fixes** in Streamlit are still accepted for features not yet in React.

**Version:** 0.19.0
**Status:** ✅ Production Ready
**Python:** 3.11+

Built with ❤️ using Streamlit
