# Installation & Setup Guide

## ✅ Current Status (Jan 22, 2026)

All required packages have been installed successfully:

### Installed Packages
- **Core**: plotly 6.5.2, pandas 2.3.3, numpy 2.4.1, scipy 1.17.0
- **Structural Design**: structural-lib-is456 0.19.0
- **DXF/CAD**: ezdxf 1.4.3
- **PDF/Reports**: reportlab 4.4.9, jinja2 3.1.6
- **Validation**: jsonschema 4.26.0, pydantic 2.12.5
- **App**: streamlit 1.53.0
- **3D Viewer**: pyvista, stpyvista (installing in background)

## 🚀 Quick Start

### Activate Virtual Environment
```bash
cd structural_engineering_lib
source .venv/bin/activate
```

### Start Streamlit App
```bash
streamlit run streamlit_app/app.py
```

The app will open at: `http://localhost:8501`

## 📦 Installing Additional Packages

If you need to install more packages later:

```bash
# Using the virtual environment pip directly
.venv/bin/pip install <package_name>

# Or after activating the venv
source .venv/bin/activate
pip install <package_name>
```

## 🔧 Important Files

- **Python package**: `Python/pyproject.toml` - All Python dependencies
- **Virtual environment**: `.venv/` - Isolated Python environment
- **Streamlit app**: `streamlit_app/app.py` - Main entry point
- **Components**: `streamlit_app/components/` - Reusable UI components

## ⚠️ Troubleshooting

### "ModuleNotFoundError: No module named 'X'"
Use the full path to pip:
```bash
/Users/Pravin/Library/Mobile\ Documents/com~apple~CloudDocs/pravin/projects/project_21_dec_25/structural_engineering_lib/.venv/bin/pip install <package>
```

### Streamlit Not Found
Make sure you're in the repo directory and use the full path:
```bash
cd structural_engineering_lib
.venv/bin/python -m streamlit run streamlit_app/app.py
```

## 📋 Environment Details

- **Python Version**: 3.11
- **Virtual Environment Tool**: venv (built-in)
- **Location**: `.venv/` in repo root
- **Package Manager**: pip (via .venv/bin/pip)

## 🎯 Next Steps

1. ✅ All packages installed
2. ⏳ PyVista/StPyVista installing (3D viewer support)
3. 🚀 Ready to run: `streamlit run streamlit_app/app.py`

The app should now start without the "ModuleNotFoundError" for plotly!
