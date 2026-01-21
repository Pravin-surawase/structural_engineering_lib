# Streamlit Cloud Professional Deployment Plan

**Type:** Research + Action Plan
**Audience:** Solo Developer + AI Agents
**Status:** Active
**Importance:** Critical
**Created:** 2026-01-15
**Last Updated:** 2026-01-15
**Related Tasks:** TASK-POC-STREAMLIT

---

## Executive Summary

This document is the **single source of truth** for making the Streamlit app professional and deploying it to Streamlit Cloud. It consolidates all research, plans tasks in numbered phases, and provides beginner-friendly step-by-step instructions.

**Goal:** Deploy a professional, simple, subtle, advanced-looking Beam Design app to Streamlit Cloud with 3D visualizations and optimizations.

**Current State:**
- Beam design page: 949 lines, complex, works but cluttered
- Library: v0.17.5, 70%+ complete, has all needed functions
- Streamlit app: Multi-page, has all features but needs polish

**Target State:**
- Simple, professional UI with "wow factor"
- 3D beam visualization
- BMD/SFD diagrams
- Cost optimization visible
- Deployed to Streamlit Cloud

---

## Table of Contents

1. [Current State Audit](#1-current-state-audit)
2. [What We Already Have (No New Code Needed)](#2-what-we-already-have-no-new-code-needed)
3. [What We Need to Add (New Functions)](#3-what-we-need-to-add-new-functions)
4. [UI Simplification Strategy](#4-ui-simplification-strategy)
5. [3D Visualization Plan](#5-3d-visualization-plan)
6. [Streamlit Cloud Deployment (Step-by-Step)](#6-streamlit-cloud-deployment-step-by-step)
7. [Task Breakdown (Numbered Phases)](#7-task-breakdown-numbered-phases)
8. [Technical Specifications](#8-technical-specifications)
9. [My Recommendations](#9-my-recommendations)
10. [Quick Reference Commands](#10-quick-reference-commands)

---

## 1. Current State Audit

### 1.1 Beam Design Page Analysis

**File:** [streamlit_app/pages/01_🏗️_beam_design.py](../../streamlit_app/pages/01_🏗️_beam_design.py)

| Metric | Value | Issue |
|--------|-------|-------|
| Lines of code | 949 | Too long, hard to maintain |
| Input sections | 4 (Geometry, Materials, Loading, Exposure) | Good structure |
| Result tabs | 5 (Summary, Visualization, Cost, Compliance, Export) | Too many tabs |
| Fragments used | Yes (`@st.fragment`) | Good for performance |
| Caching | Yes (SmartCache) | Good for performance |

**Current Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ Beam Design - IS 456:2000                               │
├─────────────────────────────┬───────────────────────────┤
│  LEFT COLUMN (40%)          │  RIGHT COLUMN (60%)       │
│                             │                           │
│  📋 Inputs                  │  📊 Design Preview        │
│  ├─ 📏 Geometry             │  ├─ 📐 Geometry Preview   │
│  │   ├─ Span               │  └─ (Results after click) │
│  │   ├─ Width              │                           │
│  │   ├─ Total Depth        │  TABS (after analyze):    │
│  │   └─ Effective Depth    │  ├─ 📊 Summary            │
│  ├─ 🧱 Materials            │  ├─ 🎨 Visualization      │
│  │   ├─ Concrete grade     │  ├─ 💰 Cost Analysis      │
│  │   └─ Steel grade        │  ├─ ✅ Compliance         │
│  ├─ ⚖️ Loading              │  └─ 📄 Export            │
│  │   ├─ Moment Mu          │                           │
│  │   └─ Shear Vu           │                           │
│  ├─ Exposure + Support     │                           │
│  └─ [🚀 Analyze Design]    │                           │
│                             │                           │
│  ⚙️ Advanced (Expander)     │                           │
│  └─ Cache stats & controls │                           │
└─────────────────────────────┴───────────────────────────┘
```

**Problems:**
1. Too many input fields visible at once
2. 5 result tabs is overwhelming
3. No "wow factor" - looks like a form
4. 3D visualization not present
5. BMD/SFD buried in tab 2
6. Cost optimization buried in tab 3

### 1.2 Library Functions Available

**Already implemented (no new code needed):**

| Function | Location | Purpose | UI Integration |
|----------|----------|---------|----------------|
| `design_beam_is456()` | `api.py` | Core design | ✅ Used |
| `design_and_detail_beam_is456()` | `api.py` | Design + detailing | ⚠️ Not used in UI |
| `optimize_beam_cost()` | `api.py` | Cost optimization | ⚠️ Partially used |
| `suggest_beam_design_improvements()` | `api.py` | AI suggestions | ❌ Not used |
| `smart_analyze_design()` | `api.py` | Full dashboard | ❌ Not used |
| `compute_bmd_sfd()` | `api.py` | BMD/SFD data | ✅ Used |
| `compute_detailing()` | `api.py` | Bar schedules | ⚠️ Partially used |
| `check_compliance_report()` | `api.py` | IS 456 checks | ✅ Used |

**Visualization functions available:**

| Function | File | Purpose |
|----------|------|---------|
| `create_beam_diagram()` | `visualizations.py` | 2D cross-section |
| `create_bmd_sfd_diagram()` | `visualizations.py` | BMD/SFD plots |
| `create_cost_comparison()` | `visualizations.py` | Cost bar chart |
| `create_utilization_gauge()` | `visualizations.py` | Utilization gauge |
| `create_sensitivity_tornado()` | `visualizations.py` | Sensitivity chart |
| `create_compliance_visual()` | `visualizations.py` | Compliance checklist |

### 1.3 Missing Pieces

| Feature | Status | Action Needed |
|---------|--------|---------------|
| 3D beam visualization | ❌ Missing | Add (Plotly 3D or PyVista) |
| Longitudinal section view | ❌ Missing | Add (2D Plotly) |
| Optimization results display | ⚠️ Buried | Move to main view |
| Quick presets | ❌ Missing | Add (Residential/Office/Industrial) |
| Design alternatives | ❌ Missing | Use `suggest_beam_design_improvements()` |

---

## 2. What We Already Have (No New Code Needed)

### 2.1 Library Functions Ready to Use

These functions exist and work, just need better UI integration:

```python
# 1. COST OPTIMIZATION (already exists!)
from structural_lib import optimize_beam_cost

result = optimize_beam_cost(
    units="IS456",
    span_mm=5000,
    mu_knm=150,
    vu_kn=80,
)
# Returns: optimal_design, baseline_cost, savings_amount, savings_percent, alternatives

# 2. DESIGN SUGGESTIONS (already exists!)
from structural_lib import suggest_beam_design_improvements

suggestions = suggest_beam_design_improvements(
    units="IS456",
    design=design_result,  # From design_beam_is456()
    span_mm=5000,
    mu_knm=150,
    vu_kn=80,
)
# Returns: suggestions with impact, confidence, action_steps

# 3. SMART ANALYZE (already exists!)
from structural_lib import smart_analyze_design

dashboard = smart_analyze_design(
    units="IS456",
    span_mm=5000,
    mu_knm=150,
    vu_kn=80,
    b_mm=300,
    D_mm=500,
    d_mm=450,
    fck_nmm2=25,
    fy_nmm2=500,
    include_cost=True,
    include_suggestions=True,
    include_sensitivity=True,
    include_constructability=True,
)
# Returns: Complete dashboard data (cost, suggestions, sensitivity, constructability)

# 4. BMD/SFD (already exists!)
from structural_lib import compute_bmd_sfd

bmd_sfd = compute_bmd_sfd(
    span_mm=5000,
    support_condition="simply_supported",
    udl_kn_m=20.0,
)
# Returns: positions_mm, bmd_knm, sfd_kn, max_moment, max_shear

# 5. DETAILING (already exists!)
from structural_lib import compute_detailing

detailing_list = compute_detailing(
    design_results={"beams": [beam_result]},
    config={"is_seismic": False},
)
# Returns: bar_schedule, stirrup_layout, construction_notes
```

### 2.2 Visualization Functions Ready

These visualization functions exist in [streamlit_app/components/visualizations.py](../../streamlit_app/components/visualizations.py):

```python
# All these already exist!
from components.visualizations import (
    create_beam_diagram,      # 2D cross-section
    create_bmd_sfd_diagram,   # BMD/SFD plots
    create_cost_comparison,   # Cost bar chart
    create_utilization_gauge, # Utilization gauge
    create_sensitivity_tornado, # Sensitivity analysis
    create_compliance_visual, # Compliance checklist
)
```

---

## 3. What We Need to Add (New Functions)

### 3.1 For 3D Visualization

**Option A: Plotly 3D (Simplest, Recommended)**

No external dependency. Plotly already installed.

```python
# Add to streamlit_app/components/visualizations_3d.py

import plotly.graph_objects as go
from typing import List, Tuple, Optional

def create_beam_3d_visualization(
    span_mm: float,
    b_mm: float,
    D_mm: float,
    rebar_positions: List[Tuple[float, float]],
    bar_dia: float = 16.0,
    stirrup_spacing: float = 150.0,
    stirrup_dia: float = 8.0,
    cover: float = 40.0,
) -> go.Figure:
    """
    Create interactive 3D beam visualization using Plotly.

    Features:
    - Transparent concrete block
    - Tension rebar (bottom)
    - Compression rebar (top, if any)
    - Stirrups at intervals
    - Rotatable view

    Args:
        span_mm: Beam span in mm
        b_mm: Beam width in mm
        D_mm: Beam depth in mm
        rebar_positions: List of (x, y) positions in cross-section
        bar_dia: Main bar diameter in mm
        stirrup_spacing: Stirrup spacing in mm
        stirrup_dia: Stirrup diameter in mm
        cover: Clear cover in mm

    Returns:
        Plotly 3D figure
    """
    fig = go.Figure()

    # Convert mm to m for display
    span_m = span_mm / 1000
    b_m = b_mm / 1000
    D_m = D_mm / 1000

    # 1. Concrete beam (transparent box)
    # Create vertices of the beam
    x = [0, span_m, span_m, 0, 0, span_m, span_m, 0]
    y = [0, 0, b_m, b_m, 0, 0, b_m, b_m]
    z = [0, 0, 0, 0, D_m, D_m, D_m, D_m]

    # Define faces
    i = [0, 0, 0, 1, 4, 0]
    j = [1, 2, 4, 5, 5, 1]
    k = [2, 3, 5, 2, 6, 5]
    l = [3, 0, 7, 6, 7, 4]  # noqa: E741

    # Simplified: use Mesh3d for concrete
    fig.add_trace(go.Mesh3d(
        x=x, y=y, z=z,
        color='lightgray',
        opacity=0.3,
        name='Concrete',
        hoverinfo='name',
    ))

    # 2. Tension rebars (cylinders along span)
    for (bar_x, bar_y) in rebar_positions:
        bar_x_m = bar_x / 1000
        bar_y_m = bar_y / 1000

        # Rebar as a line (simplified)
        fig.add_trace(go.Scatter3d(
            x=[0, span_m],
            y=[bar_x_m, bar_x_m],
            z=[bar_y_m, bar_y_m],
            mode='lines',
            line=dict(color='#FF6600', width=bar_dia / 2),
            name=f'{bar_dia}mm Bar',
            hovertemplate=f'Tension Bar: {bar_dia}mm<extra></extra>',
        ))

    # 3. Stirrups at intervals
    num_stirrups = int(span_mm / stirrup_spacing)
    for i in range(num_stirrups + 1):
        x_pos = i * stirrup_spacing / 1000

        # Stirrup outline (rectangle in yz plane)
        stirrup_y = [cover/1000, b_m - cover/1000, b_m - cover/1000, cover/1000, cover/1000]
        stirrup_z = [cover/1000, cover/1000, D_m - cover/1000, D_m - cover/1000, cover/1000]
        stirrup_x = [x_pos] * 5

        fig.add_trace(go.Scatter3d(
            x=stirrup_x,
            y=stirrup_y,
            z=stirrup_z,
            mode='lines',
            line=dict(color='#003366', width=2),
            name='Stirrups' if i == 0 else None,
            showlegend=(i == 0),
            hovertemplate=f'Stirrup: {stirrup_dia}mm @ {stirrup_spacing}mm c/c<extra></extra>',
        ))

    # Layout
    fig.update_layout(
        title=dict(
            text=f'3D Beam Visualization ({span_m:.2f}m × {b_mm:.0f}mm × {D_mm:.0f}mm)',
            font=dict(size=16, color='#003366'),
        ),
        scene=dict(
            xaxis_title='Span (m)',
            yaxis_title='Width (m)',
            zaxis_title='Depth (m)',
            camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=1.5, y=1.5, z=0.5),
            ),
            aspectmode='data',
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        height=500,
    )

    return fig
```

**Option B: PyVista (More realistic, requires dependency)**

Would need to add `pyvista` and `stpyvista` to requirements.

### 3.2 For Longitudinal Section View

```python
# Add to streamlit_app/components/visualizations.py

def create_beam_longitudinal_section(
    span_mm: float,
    D_mm: float,
    cover: float,
    num_bars: int,
    bar_dia: float,
    stirrup_spacing: float,
    stirrup_dia: float,
    support_condition: str = "simply_supported",
) -> go.Figure:
    """
    Create longitudinal section view of beam.

    Shows:
    - Beam outline
    - Bottom bars continuous
    - Top bars (if doubly reinforced)
    - Stirrups at spacing
    - Support symbols
    """
    fig = go.Figure()

    span_m = span_mm / 1000
    D_m = D_mm / 1000

    # 1. Beam outline
    fig.add_trace(go.Scatter(
        x=[0, span_m, span_m, 0, 0],
        y=[0, 0, D_m, D_m, 0],
        fill='toself',
        fillcolor='rgba(200, 200, 200, 0.3)',
        line=dict(color='#003366', width=2),
        mode='lines',
        name='Concrete',
    ))

    # 2. Bottom bars
    bar_y = cover / 1000 + (bar_dia / 2) / 1000
    fig.add_trace(go.Scatter(
        x=[0, span_m],
        y=[bar_y, bar_y],
        mode='lines',
        line=dict(color='#FF6600', width=4),
        name=f'Bottom Steel ({num_bars}-{bar_dia}mm)',
    ))

    # 3. Stirrups
    num_stirrups = int(span_mm / stirrup_spacing)
    for i in range(num_stirrups + 1):
        x_pos = i * stirrup_spacing / 1000
        stirrup_y_top = D_m - cover / 1000
        stirrup_y_bottom = cover / 1000

        fig.add_trace(go.Scatter(
            x=[x_pos, x_pos],
            y=[stirrup_y_bottom, stirrup_y_top],
            mode='lines',
            line=dict(color='#003366', width=1, dash='dash'),
            showlegend=(i == 0),
            name=f'Stirrups ({stirrup_dia}mm @ {stirrup_spacing:.0f}mm)' if i == 0 else None,
        ))

    # 4. Support symbols
    if support_condition == "simply_supported":
        # Left support (triangle)
        fig.add_trace(go.Scatter(
            x=[0, -0.1, 0.1, 0],
            y=[0, -0.1, -0.1, 0],
            fill='toself',
            fillcolor='#003366',
            line=dict(color='#003366'),
            showlegend=False,
        ))
        # Right support (triangle with roller)
        fig.add_trace(go.Scatter(
            x=[span_m, span_m - 0.1, span_m + 0.1, span_m],
            y=[0, -0.1, -0.1, 0],
            fill='toself',
            fillcolor='#003366',
            line=dict(color='#003366'),
            showlegend=False,
        ))

    fig.update_layout(
        title='Longitudinal Section',
        xaxis_title='Length (m)',
        yaxis_title='Depth (m)',
        yaxis=dict(scaleanchor="x", scaleratio=1),
        height=300,
        showlegend=True,
        legend=dict(x=1.02, y=1),
    )

    return fig
```

### 3.3 For Quick Presets

```python
# Add to streamlit_app/utils/presets.py

BEAM_PRESETS = {
    "residential": {
        "name": "Residential Building",
        "description": "Typical residential floor beam",
        "span_mm": 4000,
        "b_mm": 230,
        "D_mm": 450,
        "concrete_grade": "M25",
        "steel_grade": "Fe500",
        "mu_knm": 80,
        "vu_kn": 50,
        "exposure": "Moderate",
    },
    "office": {
        "name": "Office Building",
        "description": "Standard office floor beam",
        "span_mm": 6000,
        "b_mm": 300,
        "D_mm": 600,
        "concrete_grade": "M30",
        "steel_grade": "Fe500",
        "mu_knm": 150,
        "vu_kn": 80,
        "exposure": "Moderate",
    },
    "industrial": {
        "name": "Industrial Structure",
        "description": "Heavy-duty industrial beam",
        "span_mm": 8000,
        "b_mm": 400,
        "D_mm": 750,
        "concrete_grade": "M35",
        "steel_grade": "Fe550",
        "mu_knm": 300,
        "vu_kn": 150,
        "exposure": "Severe",
    },
    "custom": {
        "name": "Custom Design",
        "description": "Enter your own values",
        "span_mm": 5000,
        "b_mm": 300,
        "D_mm": 500,
        "concrete_grade": "M25",
        "steel_grade": "Fe500",
        "mu_knm": 100,
        "vu_kn": 60,
        "exposure": "Moderate",
    },
}
```

---

## 4. UI Simplification Strategy

### 4.1 Current Problems

1. **Too many visible inputs** - Users see 9+ fields before doing anything
2. **5 tabs for results** - Overwhelming, hard to find key info
3. **No visual "wow"** - Looks like a form, not a design tool
4. **Optimization hidden** - Cost savings buried in tab 3
5. **No presets** - Beginners don't know what values to use

### 4.2 Proposed New Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🏗️ Beam Design — IS 456:2000                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  QUICK START: Select a preset or enter custom values            │   │
│  │  [Residential ▾] [Office ▾] [Industrial ▾] [Custom ▾]           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
├─────────────────────────────┬───────────────────────────────────────────┤
│  📐 Design Inputs           │  📊 Live Preview & Results               │
│                             │                                           │
│  Geometry                   │  ┌───────────────────────────────────┐   │
│  ├─ Span: [5000] mm        │  │                                   │   │
│  ├─ Width: [300] mm        │  │     3D BEAM VISUALIZATION         │   │
│  └─ Depth: [500] mm        │  │                                   │   │
│                             │  │  [Rotate with mouse]              │   │
│  Materials                  │  │                                   │   │
│  ├─ Concrete: [M25 ▾]      │  └───────────────────────────────────┘   │
│  └─ Steel: [Fe500 ▾]       │                                           │
│                             │  STATUS: ✅ SAFE                         │
│  Loading                    │  ┌─────┬─────┬─────┬─────┐              │
│  ├─ Moment: [100] kN·m     │  │ Ast │Util.│Defl.│Cost │              │
│  └─ Shear: [60] kN         │  │452mm²│68% │OK  │₹87/m│              │
│                             │  └─────┴─────┴─────┴─────┘              │
│  [⚙️ Advanced Settings ▾]   │                                           │
│                             │  [📈 BMD/SFD] [💰 Optimize] [📄 Export]  │
│  [🚀 DESIGN BEAM]           │                                           │
│                             │  ─────────────────────────────────────   │
│                             │  💡 Suggestions:                         │
│                             │  • Consider increasing depth for 12% cost│
│                             │    reduction                              │
│                             │  • 3-16mm bars optimal (vs 4-14mm)       │
└─────────────────────────────┴───────────────────────────────────────────┘
```

### 4.3 Design Principles

1. **Progressive disclosure** - Show essential inputs first, hide advanced
2. **Visual first** - 3D preview is the hero element
3. **Key metrics prominent** - Status, Ast, Utilization, Cost visible immediately
4. **Actions clear** - One primary button: "Design Beam"
5. **Suggestions visible** - AI recommendations always shown

### 4.4 Simplification Actions (Ordered)

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| 1 | Add Quick Preset selector | 30 min | ★★★★★ |
| 2 | Merge result tabs into 2 (Results + Details) | 1 hour | ★★★★☆ |
| 3 | Add 3D visualization (Plotly) | 1-2 hours | ★★★★★ |
| 4 | Move key metrics to result cards | 30 min | ★★★★☆ |
| 5 | Add BMD/SFD toggle button | 30 min | ★★★☆☆ |
| 6 | Add "Optimize Cost" button | 30 min | ★★★★☆ |
| 7 | Show AI suggestions by default | 30 min | ★★★★☆ |
| 8 | Hide Advanced Settings by default | 15 min | ★★★☆☆ |

---

## 5. 3D Visualization Plan

### 5.1 Approach: Plotly 3D

**Why Plotly 3D?**
- Already installed (no new dependencies)
- Works in Streamlit without extra packages
- Interactive (rotate, zoom, pan)
- Good for structural visualization

**Limitations:**
- Not photorealistic (that requires Three.js/R3F)
- Limited to wireframe/mesh visualization

### 5.2 3D Features to Implement

| Feature | Priority | Description |
|---------|----------|-------------|
| Concrete box (transparent) | High | Main beam shape |
| Tension bars (lines) | High | Bottom reinforcement |
| Compression bars (lines) | Medium | Top reinforcement |
| Stirrups (rectangles) | High | Shear reinforcement |
| Support symbols | Low | Hinged/roller markers |
| Stress gradient colors | Low | Color by stress level |

### 5.3 Implementation Location

Add new file: [streamlit_app/components/visualizations_3d.py](../../streamlit_app/components/visualizations_3d.py)

---

## 6. Streamlit Cloud Deployment (Step-by-Step)

### 6.1 Pre-Deployment Checklist

Before deploying, verify:

- [ ] App runs locally without errors
- [ ] All imports work
- [ ] No hardcoded file paths
- [ ] No secrets in code
- [ ] requirements.txt is complete
- [ ] Entry point is correct (app.py or main.py)

### 6.2 Step-by-Step Deployment

#### Step 1: Verify Local Run

```bash
# Navigate to streamlit app directory
cd streamlit_app

# Activate virtual environment
source ../.venv/bin/activate

# Run locally
streamlit run app.py
```

Expected: App opens at http://localhost:8501 without errors.

#### Step 2: Verify requirements.txt

Check [streamlit_app/requirements.txt](streamlit_app/requirements.txt):

```
# Required
streamlit>=1.30.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
jinja2>=3.1.0

# For structural_lib (need to add this!)
# Option A: Install from local
# pip install -e ../Python

# Option B: Install from PyPI (if published)
# structural-lib-is456>=0.17.0
```

**Important:** Streamlit Cloud needs to install structural_lib.

#### Step 3: Create Streamlit Cloud Configuration

Create [streamlit_app/.streamlit/config.toml](streamlit_app/.streamlit/config.toml):

```toml
[server]
headless = true
port = 8501

[theme]
primaryColor = "#FF6600"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F5F5F5"
textColor = "#003366"
font = "sans serif"
```

#### Step 4: Create Streamlit Cloud Secrets (if needed)

If app uses any API keys, create [streamlit_app/.streamlit/secrets.toml](streamlit_app/.streamlit/secrets.toml):

```toml
# Example (do NOT commit this file!)
[api_keys]
openai_key = "sk-..."
```

Add to .gitignore:
```
.streamlit/secrets.toml
```

#### Step 5: Connect to Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Sign in with GitHub
3. Click **"New app"**
4. Select repository: `Pravin-surawase/structural_engineering_lib`
5. Branch: `main`
6. Main file path: `streamlit_app/app.py`
7. Python version: 3.11 or 3.12
8. Click **"Deploy!"**

#### Step 6: Handle Dependencies

Streamlit Cloud needs to install structural_lib. Options:

**Option A: Add packages.txt (Recommended)**

Create [streamlit_app/packages.txt](streamlit_app/packages.txt):
```
# System packages (if needed)
```

Create [streamlit_app/.streamlit/requirements.txt](streamlit_app/requirements.txt) with:
```
streamlit>=1.30.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
jinja2>=3.1.0
# Point to local library
-e ../Python
```

**Option B: Publish to PyPI first**

If library is on PyPI:
```
structural-lib-is456>=0.17.5
```

#### Step 7: Configure App Settings

In Streamlit Cloud dashboard:

1. Go to **Settings** → **Secrets**
2. Add any API keys
3. Go to **Settings** → **General**
4. Set Python version to 3.11
5. Click **Reboot app**

#### Step 8: Verify Deployment

1. Click the deployed URL
2. Test all features:
   - [ ] Homepage loads
   - [ ] Beam Design page works
   - [ ] Inputs accept values
   - [ ] "Analyze Design" computes result
   - [ ] Visualizations render
   - [ ] No error messages

---

## 7. Task Breakdown (Numbered Phases)

### Phase 0: Pre-Work (30 min)

| # | Task | Time | Owner |
|---|------|------|-------|
| 0.1 | Read this document completely | 10 min | You |
| 0.2 | Verify local app runs | 10 min | You |
| 0.3 | Create development branch | 5 min | Agent |
| 0.4 | Run existing tests | 5 min | Agent |

### Phase 1: Quick Wins (2 hours)

| # | Task | Time | Deliverable |
|---|------|------|-------------|
| 1.1 | Add Quick Preset selector | 30 min | Preset dropdown in UI |
| 1.2 | Create presets.py with 4 presets | 15 min | Preset data file |
| 1.3 | Hide Advanced Settings by default | 15 min | Cleaner input panel |
| 1.4 | Merge 5 result tabs into 2 | 30 min | Simplified results |
| 1.5 | Move key metrics to result cards | 30 min | Clean status display |

### Phase 2: 3D Visualization (2-3 hours)

| # | Task | Time | Deliverable |
|---|------|------|-------------|
| 2.1 | Create visualizations_3d.py | 1 hour | 3D visualization module |
| 2.2 | Implement create_beam_3d_visualization() | 1 hour | 3D beam function |
| 2.3 | Add 3D preview to beam design page | 30 min | Integrated 3D view |
| 2.4 | Add view toggle (2D/3D) | 30 min | User can switch views |

### Phase 3: Enhanced Features (2 hours)

| # | Task | Time | Deliverable |
|---|------|------|-------------|
| 3.1 | Add "Optimize Cost" button | 30 min | Cost optimization UI |
| 3.2 | Display optimization results | 30 min | Savings and alternatives |
| 3.3 | Add AI suggestions panel | 30 min | Improvement suggestions |
| 3.4 | Add longitudinal section view | 30 min | Side view of beam |

### Phase 4: Polish (1 hour)

| # | Task | Time | Deliverable |
|---|------|------|-------------|
| 4.1 | Review and fix styling | 30 min | Consistent design |
| 4.2 | Add loading states | 15 min | User feedback |
| 4.3 | Test all features | 15 min | Bug-free app |

### Phase 5: Deployment (1 hour)

| # | Task | Time | Deliverable |
|---|------|------|-------------|
| 5.1 | Update requirements.txt | 15 min | Complete dependencies |
| 5.2 | Create .streamlit/config.toml | 10 min | Theme configuration |
| 5.3 | Deploy to Streamlit Cloud | 20 min | Live app |
| 5.4 | Verify live deployment | 15 min | Working public URL |

### Total Estimated Time: 8-9 hours

---

## 8. Technical Specifications

### 8.1 File Changes Summary

| File | Action | Description |
|------|--------|-------------|
| `streamlit_app/utils/presets.py` | Create | Beam preset configurations |
| `streamlit_app/components/visualizations_3d.py` | Create | 3D Plotly visualizations |
| `streamlit_app/pages/01_🏗️_beam_design.py` | Modify | Simplified layout |
| `streamlit_app/requirements.txt` | Update | Add any new dependencies |
| `streamlit_app/.streamlit/config.toml` | Create | Theme configuration |

### 8.2 Dependencies

Current requirements.txt is sufficient. No new packages needed for Plotly 3D.

### 8.3 Browser Compatibility

- Chrome, Firefox, Safari: Full support
- Edge: Full support
- Mobile: Limited (Streamlit responsive)

---

## 9. My Recommendations

### 9.1 What to Do First

1. **Phase 1 first** - Quick wins make biggest impact
2. **3D visualization second** - This is the "wow factor"
3. **Deployment last** - Don't deploy until it's polished

### 9.2 What to Skip for Now

- PyVista/Three.js integration (too complex)
- Chat UI (that's Phase 2 product)
- Multi-code support (future)
- Complex animations

### 9.3 Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Streamlit Cloud dependency issues | Test locally with clean venv first |
| 3D visualization slow | Use Plotly caching |
| Library import fails | Ensure path configuration correct |
| Users confused by UI | Add help tooltips |

---

## 10. Quick Reference Commands

### Local Development

```bash
# Navigate to streamlit app
cd streamlit_app

# Activate venv
source ../.venv/bin/activate

# Run locally
streamlit run app.py

# Run with specific port
streamlit run app.py --server.port 8502

# Clear cache and run
streamlit run app.py --clear-cache
```

### Testing

```bash
# Run streamlit tests
cd streamlit_app
pytest tests/ -v

# Run library tests
cd Python
.venv/bin/python -m pytest tests/ -v

# Check for Streamlit issues
.venv/bin/python scripts/check_streamlit_issues.py --all-pages
```

### Git Operations

```bash
# Use automated commit (per project rules)
./scripts/ai_commit.sh "feat: add 3D beam visualization"

# Check PR need
./scripts/should_use_pr.sh --explain
```

### Deployment

```bash
# Verify before deploy
cd streamlit_app
streamlit run app.py --server.headless true

# Check requirements
pip freeze > requirements.txt.check
diff requirements.txt requirements.txt.check
```

---

## Appendix: Research Sources

- Streamlit Cloud Docs: https://docs.streamlit.io/streamlit-community-cloud
- Plotly 3D Surface: https://plotly.com/python/3d-surface-plots/
- Plotly 3D Scatter: https://plotly.com/python/3d-scatter-plots/
- Library API: [Python/structural_lib/api.py](../../Python/build/lib/structural_lib/api.py)
- Current Visualizations: [streamlit_app/components/visualizations.py](../../streamlit_app/components/visualizations.py)
- Previous Research: [docs/research/chat-ui-product-strategy-research.md](chat-ui-product-strategy-research.md)

---

*Document created by AI agent. Single source of truth for Streamlit Cloud deployment.*
