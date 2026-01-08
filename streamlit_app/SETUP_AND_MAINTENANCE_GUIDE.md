# 🚀 Streamlit App Setup & Maintenance Guide

**Complete guide for setting up, running, and maintaining the IS 456 RC Beam Design Dashboard**

---

## 📋 Table of Contents

1. [Quick Start (5 minutes)](#quick-start)
2. [Detailed Setup](#detailed-setup)
3. [Running the App](#running-the-app)
4. [Common Issues & Solutions](#common-issues--solutions)
5. [Maintenance Tasks](#maintenance-tasks)
6. [FAQ](#faq)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

**Get the app running in 5 minutes:**

```bash
# 1. Navigate to the streamlit app directory
cd streamlit_app

# 2. Install dependencies (one-time setup)
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

---

## 🔧 Detailed Setup

### Prerequisites

- **Python**: 3.8 or higher
- **pip**: Latest version
- **Operating System**: Windows, macOS, or Linux
- **Browser**: Chrome, Firefox, Safari, or Edge

### Step-by-Step Setup

#### 1. Check Python Version

```bash
python --version
# or
python3 --version
```

Expected output: `Python 3.8.x` or higher

#### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

**Why use a virtual environment?**
- Isolates dependencies
- Prevents conflicts with other Python projects
- Makes it easy to replicate setup

#### 3. Install Dependencies

```bash
# Make sure you're in the streamlit_app directory
cd streamlit_app

# Install all required packages
pip install -r requirements.txt
```

**What gets installed?**
- `streamlit`: Web framework (version 1.28+)
- `plotly`: Interactive charts (version 5.17+)
- `pandas`: Data manipulation (version 2.0+)
- `numpy`: Numerical computing (version 1.24+)

#### 4. Verify Installation

```bash
# Check Streamlit version
streamlit version

# Check all packages
pip list | grep -E "streamlit|plotly|pandas|numpy"
```

#### 5. Run Tests (Optional but Recommended)

```bash
# Install pytest if not already installed
pip install pytest

# Run all tests
pytest tests/ -v

# Expected: 200+ tests passing
```

---

## ▶️ Running the App

### Basic Usage

```bash
# From the streamlit_app directory
streamlit run app.py
```

The app will:
1. Start a local web server
2. Open your default browser automatically
3. Display at `http://localhost:8501`

### Advanced Options

#### Custom Port

```bash
# Run on a different port (e.g., 8502)
streamlit run app.py --server.port 8502
```

#### Headless Mode (No Browser)

```bash
# Useful for remote servers
streamlit run app.py --server.headless true
```

#### Development Mode (Auto-reload on changes)

```bash
# This is the default - any code changes trigger auto-reload
streamlit run app.py --server.runOnSave true
```

#### Network Access (Allow Other Devices)

```bash
# Allow access from other devices on your network
streamlit run app.py --server.address 0.0.0.0
```

### Stopping the App

- **In Terminal**: Press `Ctrl+C`
- **In Browser**: Just close the tab (server keeps running until you Ctrl+C)

---

## ⚠️ Common Issues & Solutions

### Issue 1: "Command not found: streamlit"

**Problem**: Streamlit not installed or not in PATH

**Solution**:
```bash
# Verify pip installation
pip list | grep streamlit

# If not found, install it:
pip install streamlit

# If using virtual environment, make sure it's activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### Issue 2: "Port 8501 already in use"

**Problem**: Another Streamlit app or service is using the default port

**Solution 1**: Stop the other app
```bash
# Find the process
lsof -i :8501  # macOS/Linux
netstat -ano | findstr :8501  # Windows

# Kill it (use PID from above)
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

**Solution 2**: Use a different port
```bash
streamlit run app.py --server.port 8502
```

### Issue 3: "Module not found" errors

**Problem**: Missing dependencies

**Solution**:
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall

# Or install specific missing package
pip install <package-name>
```

### Issue 4: App won't load or shows errors

**Problem**: Code errors or corrupted cache

**Solution**:
```bash
# Clear Streamlit cache
streamlit cache clear

# Run with error details
streamlit run app.py --logger.level debug
```

### Issue 5: Charts not displaying

**Problem**: Plotly not properly installed

**Solution**:
```bash
# Reinstall Plotly
pip uninstall plotly
pip install plotly==5.17.0

# Clear browser cache and refresh
```

---

## 🔄 Maintenance Tasks

### Daily Maintenance

**Not required** - The app is stateless and self-contained.

### Weekly Maintenance

1. **Check for updates**:
   ```bash
   # Check outdated packages
   pip list --outdated
   ```

2. **Run tests**:
   ```bash
   pytest tests/ -v
   ```

### Monthly Maintenance

1. **Update dependencies**:
   ```bash
   # Update all packages (carefully!)
   pip install --upgrade streamlit plotly pandas numpy
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
   # Test thoroughly after updating
   pytest tests/ -v
   ```

2. **Review logs** (if any):
   ```bash
   # Streamlit logs location
   ls ~/.streamlit/logs/
   ```

3. **Clean cache**:
   ```bash
   streamlit cache clear
   ```

### Backup Strategy

**What to backup**:
- `streamlit_app/` directory (entire folder)
- `requirements.txt` (dependencies)
- Any custom configurations

**What NOT to backup**:
- `venv/` (virtual environment - recreate instead)
- `__pycache__/` (Python cache - auto-regenerated)
- `.streamlit/cache/` (Streamlit cache - auto-regenerated)

---

## ❓ FAQ

### Q1: Can I deploy this app to the cloud?

**A**: Yes! Options:
- **Streamlit Community Cloud** (free, easiest)
- **Heroku** (free tier available)
- **AWS/Google Cloud/Azure** (for production)

See [Streamlit deployment docs](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app) for details.

### Q2: How do I add new features?

<<<<<<< Updated upstream
**A**:
=======
**A**:
>>>>>>> Stashed changes
1. Create a new branch (if using git)
2. Add your feature in appropriate file (components/, pages/, utils/)
3. Add tests in `tests/test_<feature>.py`
4. Run tests: `pytest tests/ -v`
5. Test manually: `streamlit run app.py`

### Q3: Can multiple users use this at the same time?

<<<<<<< Updated upstream
**A**:
=======
**A**:
>>>>>>> Stashed changes
- **Local development**: No - one app instance per machine
- **Deployed (cloud)**: Yes - Streamlit handles multiple sessions automatically

### Q4: How do I change the color theme?

**A**: Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF6600"  # Change this
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### Q5: Where is the data stored?

<<<<<<< Updated upstream
**A**:
=======
**A**:
>>>>>>> Stashed changes
- **Session data**: In-memory (lost when browser refreshes)
- **Cache**: `.streamlit/cache/` (temporary)
- **User uploads**: Not persistent (need custom storage)

### Q6: How much RAM/CPU does it need?

<<<<<<< Updated upstream
**A**:
=======
**A**:
>>>>>>> Stashed changes
- **Minimum**: 2GB RAM, dual-core CPU
- **Recommended**: 4GB RAM, quad-core CPU
- **Typical usage**: 200-500MB RAM, 10-20% CPU

### Q7: Can I use this offline?

**A**: Yes! Once installed, no internet required (except for initial `pip install`).

### Q8: How do I update the structural engineering library?

<<<<<<< Updated upstream
**A**:
=======
**A**:
>>>>>>> Stashed changes
```bash
# If the Python library is updated
pip install --upgrade structural-lib-is456

# Or manually copy updated files to Python/structural_lib/
```

### Q9: Is there a dark mode?

**A**: Yes! In the app:
1. Click ☰ menu (top-right)
2. Settings
3. Choose theme: Light/Dark/Auto

### Q10: How do I export designs?

**A**: Currently implemented exports:
- **PDF**: Print from browser (Ctrl+P / Cmd+P)
- **CSV**: Click "Export CSV" buttons on results pages
- **Copy**: Use clipboard buttons for quick copy-paste

---

## 🔍 Troubleshooting

### Debug Mode

```bash
# Run with detailed logging
streamlit run app.py --logger.level debug
```

### Check System Requirements

```bash
# Python version
python --version

# Pip version
pip --version

# Available memory
free -h  # Linux
vm_stat  # macOS
systeminfo | findstr Memory  # Windows
```

### Test Individual Components

```bash
# Test a specific component
pytest tests/test_inputs.py -v

# Test a specific test
pytest tests/test_inputs.py::TestMaterialDatabases -v
```

### Clear All Caches

```bash
# Streamlit cache
streamlit cache clear

# Python cache
find . -type d -name __pycache__ -exec rm -rf {} +

# Browser cache (in browser settings)
```

### Reinstall Everything

```bash
# Remove virtual environment
rm -rf venv/  # macOS/Linux
rmdir /s venv  # Windows

# Recreate
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## 📞 Getting Help

### Resources

1. **Streamlit Docs**: https://docs.streamlit.io
2. **Plotly Docs**: https://plotly.com/python/
3. **Project Docs**: See `docs/` directory
4. **Error Messages**: Read carefully - they usually indicate the issue

### Reporting Issues

When reporting issues, include:
1. **Python version**: `python --version`
2. **Streamlit version**: `streamlit version`
3. **Operating system**: Windows/macOS/Linux
4. **Error message**: Full traceback
5. **Steps to reproduce**: What you did before error occurred

---

## 🎯 Quick Reference Commands

```bash
# Setup
pip install -r requirements.txt

# Run
streamlit run app.py

# Run on different port
streamlit run app.py --server.port 8502

# Run tests
pytest tests/ -v

# Clear cache
streamlit cache clear

# Check version
streamlit version

# Update dependencies
pip install --upgrade -r requirements.txt

# Reinstall dependency
pip install --force-reinstall <package-name>
```

---

## ✅ Pre-flight Checklist

Before running the app:
- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated (optional but recommended)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Tests passing (`pytest tests/ -v`)
- [ ] Port 8501 available (or use `--server.port <port>`)

---

## 📝 Notes

- **First run**: May take 10-15 seconds to load all components
- **Auto-reload**: Enabled by default in development
- **Session state**: Lost on page refresh (by design)
- **Cache**: Used for expensive operations (design calculations)
- **Logs**: Not persistent by default (configure if needed)

---

<<<<<<< Updated upstream
**Last Updated**: January 2026
**Version**: 1.0.0
=======
**Last Updated**: January 2026
**Version**: 1.0.0
>>>>>>> Stashed changes
**Maintainer**: Structural Engineering Team
