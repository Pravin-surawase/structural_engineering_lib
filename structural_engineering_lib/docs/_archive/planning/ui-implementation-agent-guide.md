# UI Layout Implementation - Agent Step-by-Step Guide
**Version:** 2.0.0
**Date:** 2026-01-08
**Priority:** 🔴 PRODUCTION-CRITICAL
**For:** All agents (background + main)

---

## ⚠️ CRITICAL: Read Before Any Code Changes

### Current State (DO NOT BREAK)
```
✅ 651 Streamlit tests passing (36 token-specific tests)
✅ Dual-token system working (CSS strings + Plotly integers)
✅ All visualizations use correct ANIMATION.duration_*_ms tokens
✅ All CSS uses ANIMATION.fast/normal/slow (strings)
✅ No runtime errors in production
```

### What We're Adding (NOT replacing)
```
➕ Duration/Color Protocol classes (future migration path)
➕ Two-column layout (UI improvement)
➕ Real-time preview component (UX enhancement)
➕ Additional tests for new code
```

---

## 🎯 Mission Summary

| Task | Priority | Hours | Risk |
|------|----------|-------|------|
| Phase 1: Token Protocols (Optional) | LOW | 2h | LOW |
| Phase 2: Two-Column Layout | HIGH | 3-4h | MEDIUM |
| Phase 3: Preview Component | HIGH | 2h | MEDIUM |
| Phase 4: Test Updates | HIGH | 1h | LOW |

**Recommended order:** Phase 2 → Phase 3 → Phase 4 → Phase 1 (deferred)

---

## 📋 Phase 2: Two-Column Layout (PRIORITY)

### Task 2.1: Backup Current Code (5 min)

**Purpose:** Ensure rollback is possible

**Steps:**
```bash
# 1. Create backup branch
git checkout -b backup/ui-layout-$(date +%Y%m%d)
git push origin backup/ui-layout-$(date +%Y%m%d)
git checkout main
```

**Verification:**
```bash
git branch -a | grep backup
# Should show: backup/ui-layout-YYYYMMDD
```

---

### Task 2.2: Modify beam_design.py Layout (45 min)

**File:** `streamlit_app/pages/01_🏗️_beam_design.py`

**Current code (lines 77-85):**
```python
# ============================================================================
# SIDEBAR: Input Parameters
# ============================================================================

with st.sidebar:
    st.header("📋 Input Parameters")
```

**Replace with:**
```python
# ============================================================================
# TWO-COLUMN LAYOUT: Input + Preview/Results
# ============================================================================

# Create two-column layout (40% input, 60% preview/results)
col_input, col_preview = st.columns([2, 3], gap="large")

# Left column: Input parameters
with col_input:
    st.header("📋 Input Parameters")

    # Theme toggle
    render_theme_toggle()

    st.markdown("---")
```

**Critical changes required:**

1. **Replace ALL `with st.sidebar:` blocks** with `with col_input:`

   Find and replace each occurrence:
   ```python
   # OLD:
   with st.sidebar:
       st.header("📋 Input Parameters")

   # NEW:
   with col_input:
       st.header("📋 Input Parameters")
   ```

2. **Move Analyze button to col_input:**
   ```python
   with col_input:
       # ... all inputs ...

       st.markdown("---")
       analyze_button = st.button(
           "🔍 Analyze Design",
           type="primary",
           use_container_width=True
       )
   ```

3. **Add Preview in col_preview:**
   ```python
   with col_preview:
       st.header("📊 Design Preview")

       # Show preview or results based on state
       if st.session_state.beam_inputs.get('design_computed', False):
           # Show full results (existing tabs)
           render_results_tabs(st.session_state.beam_inputs['design_result'])
       else:
           # Show real-time preview
           render_real_time_preview(
               span_mm=st.session_state.beam_inputs['span_mm'],
               b_mm=st.session_state.beam_inputs['b_mm'],
               D_mm=st.session_state.beam_inputs['D_mm'],
               d_mm=st.session_state.beam_inputs['d_mm'],
               concrete_grade=st.session_state.beam_inputs['concrete_grade'],
               steel_grade=st.session_state.beam_inputs['steel_grade'],
               mu_knm=st.session_state.beam_inputs['mu_knm'],
               vu_kn=st.session_state.beam_inputs['vu_kn'],
               exposure=st.session_state.beam_inputs['exposure'],
               support_condition=st.session_state.beam_inputs['support_condition']
           )
   ```

**Verification after change:**
```bash
cd streamlit_app && ../.venv/bin/streamlit run app.py --server.headless=true &
sleep 5
curl -s http://localhost:8501 | head -20
pkill -f streamlit
```

---

### Task 2.3: Add Import for Preview Component (5 min)

**File:** `streamlit_app/pages/01_🏗️_beam_design.py`

**Add to imports (around line 30):**
```python
from components.preview import render_real_time_preview
```

**Note:** This import will fail until Task 3.1 creates the file.
Order of tasks: Create preview.py first (Task 3.1), then modify beam_design.py.

---

## 📋 Phase 3: Preview Component (PRIORITY)

### Task 3.1: Create preview.py (60 min)

**File:** `streamlit_app/components/preview.py`

**Complete implementation:**

```python
"""
Real-Time Preview Component
===========================

Provides instant visual feedback as users modify beam design inputs.

Features:
- Beam elevation diagram with support symbols
- Quick design checks (span/d, cover, b/D ratios)
- Color-coded status dashboard
- Rough cost estimate

Author: Agent implementing UI-LAYOUT-FINAL-DECISION
Status: 🆕 NEW COMPONENT
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Dict, List, Optional, Tuple, Literal

# Import design system
from utils.design_system import COLORS, TYPOGRAPHY, SPACING, ANIMATION


def render_real_time_preview(
    span_mm: float,
    b_mm: float,
    D_mm: float,
    d_mm: float,
    concrete_grade: str,
    steel_grade: str,
    mu_knm: float,
    vu_kn: float,
    exposure: str,
    support_condition: str
) -> None:
    """
    Render the complete real-time preview panel.

    This is the main entry point for the preview component.
    Called from beam_design.py in col_preview context.

    Args:
        span_mm: Beam span in millimeters
        b_mm: Beam width in millimeters
        D_mm: Total beam depth in millimeters
        d_mm: Effective depth in millimeters
        concrete_grade: e.g., "M25", "M30"
        steel_grade: e.g., "Fe500", "Fe415"
        mu_knm: Design moment in kN·m
        vu_kn: Design shear in kN
        exposure: Exposure condition string
        support_condition: e.g., "Simply Supported", "Cantilever"
    """
    # Section 1: Beam Diagram
    st.subheader("🏗️ Beam Elevation")
    fig = create_beam_preview_diagram(
        span_mm=span_mm,
        b_mm=b_mm,
        D_mm=D_mm,
        support_condition=support_condition
    )
    st.plotly_chart(fig, use_container_width=True, key="preview_beam_diagram")

    # Section 2: Quick Checks
    st.subheader("✅ Design Checks")
    checks = calculate_quick_checks(
        span_mm=span_mm,
        d_mm=d_mm,
        b_mm=b_mm,
        D_mm=D_mm,
        exposure=exposure
    )
    render_status_dashboard(checks)

    # Section 3: Rough Cost
    st.subheader("💰 Preliminary Cost")
    cost = calculate_rough_cost(
        b_mm=b_mm,
        D_mm=D_mm,
        span_mm=span_mm,
        concrete_grade=concrete_grade,
        mu_knm=mu_knm
    )
    render_cost_summary(cost)


def create_beam_preview_diagram(
    span_mm: float,
    b_mm: float,
    D_mm: float,
    support_condition: str
) -> go.Figure:
    """
    Create a simple beam elevation diagram with supports.

    Args:
        span_mm: Beam span
        b_mm: Beam width (for label)
        D_mm: Beam depth (for scale)
        support_condition: Determines support symbols

    Returns:
        Plotly figure with beam diagram
    """
    fig = go.Figure()

    # Scale: fit 0-100 coordinate system
    # Beam drawn from x=10 to x=90 (80% of width)
    beam_left = 10
    beam_right = 90
    beam_top = 60
    beam_bottom = 40
    beam_thickness = beam_top - beam_bottom  # 20 units

    # Draw beam (gray rectangle)
    fig.add_shape(
        type="rect",
        x0=beam_left, y0=beam_bottom,
        x1=beam_right, y1=beam_top,
        fillcolor="rgba(200, 200, 200, 0.5)",
        line=dict(color=COLORS.primary_500, width=2)
    )

    # Beam label
    fig.add_annotation(
        x=50, y=50,
        text=f"{span_mm/1000:.1f}m × {b_mm}×{D_mm}mm",
        showarrow=False,
        font=dict(size=12, color=COLORS.gray_700)
    )

    # Support symbols based on condition
    if support_condition == "Simply Supported":
        # Left support: triangle (pinned)
        _add_triangle_support(fig, beam_left, beam_bottom)
        # Right support: triangle with roller
        _add_roller_support(fig, beam_right, beam_bottom)
    elif support_condition == "Cantilever":
        # Fixed support at left
        _add_fixed_support(fig, beam_left, beam_bottom, beam_top)
        # Free end at right (no support)
    elif support_condition == "Fixed-Fixed":
        _add_fixed_support(fig, beam_left, beam_bottom, beam_top)
        _add_fixed_support(fig, beam_right, beam_bottom, beam_top)
    else:
        # Default: simply supported
        _add_triangle_support(fig, beam_left, beam_bottom)
        _add_roller_support(fig, beam_right, beam_bottom)

    # Layout
    fig.update_layout(
        showlegend=False,
        xaxis=dict(visible=False, range=[0, 100]),
        yaxis=dict(visible=False, range=[0, 100], scaleanchor="x"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=200,
        paper_bgcolor='white',
        plot_bgcolor='white',
        # Use integer duration for Plotly (CRITICAL!)
        transition=dict(duration=ANIMATION.duration_normal_ms, easing='cubic-in-out')
    )

    return fig


def _add_triangle_support(fig: go.Figure, x: float, y: float) -> None:
    """Add triangular (pinned) support symbol."""
    size = 5
    fig.add_trace(go.Scatter(
        x=[x - size, x, x + size, x - size],
        y=[y - size, y, y - size, y - size],
        fill="toself",
        fillcolor=COLORS.gray_400,
        line=dict(color=COLORS.gray_600, width=1),
        mode="lines",
        hoverinfo="skip",
        showlegend=False
    ))


def _add_roller_support(fig: go.Figure, x: float, y: float) -> None:
    """Add roller support symbol (triangle + circle)."""
    size = 5
    # Triangle
    fig.add_trace(go.Scatter(
        x=[x - size, x, x + size, x - size],
        y=[y - size - 3, y - 3, y - size - 3, y - size - 3],
        fill="toself",
        fillcolor=COLORS.gray_400,
        line=dict(color=COLORS.gray_600, width=1),
        mode="lines",
        hoverinfo="skip",
        showlegend=False
    ))
    # Circles (rollers)
    for dx in [-3, 0, 3]:
        fig.add_shape(
            type="circle",
            x0=x + dx - 1.5, y0=y - size - 5,
            x1=x + dx + 1.5, y1=y - size - 2,
            fillcolor=COLORS.gray_300,
            line=dict(color=COLORS.gray_500, width=1)
        )


def _add_fixed_support(fig: go.Figure, x: float, y_bottom: float, y_top: float) -> None:
    """Add fixed support symbol (hatched rectangle)."""
    width = 5
    if x < 50:  # Left side
        x0 = x - width
        x1 = x
    else:  # Right side
        x0 = x
        x1 = x + width

    fig.add_shape(
        type="rect",
        x0=x0, y0=y_bottom,
        x1=x1, y1=y_top,
        fillcolor="rgba(100, 100, 100, 0.3)",
        line=dict(color=COLORS.gray_600, width=2)
    )
    # Hatching lines
    for i in range(5):
        y = y_bottom + i * (y_top - y_bottom) / 4
        fig.add_shape(
            type="line",
            x0=x0, y0=y,
            x1=x1, y1=y + 3,
            line=dict(color=COLORS.gray_600, width=1)
        )


def calculate_quick_checks(
    span_mm: float,
    d_mm: float,
    b_mm: float,
    D_mm: float,
    exposure: str
) -> List[Dict]:
    """
    Calculate quick design checks for status dashboard.

    Returns list of check results, each with:
    - name: Check name
    - status: "pass", "warning", or "fail"
    - value: Current value
    - limit: Limit or reference value
    - message: Human-readable message
    """
    checks = []

    # Check 1: Span/d ratio (IS 456 Cl. 23.2.1)
    span_d = span_mm / d_mm if d_mm > 0 else float('inf')
    span_d_limit = 20  # Simply supported basic limit
    if span_d <= span_d_limit:
        status = "pass"
        message = f"OK ({span_d:.1f} ≤ {span_d_limit})"
    elif span_d <= span_d_limit * 1.2:
        status = "warning"
        message = f"Review ({span_d:.1f} > {span_d_limit})"
    else:
        status = "fail"
        message = f"Exceeds ({span_d:.1f} >> {span_d_limit})"

    checks.append({
        "name": "Span/d Ratio",
        "status": status,
        "value": round(span_d, 1),
        "limit": span_d_limit,
        "message": message,
        "clause": "IS 456 Cl. 23.2.1"
    })

    # Check 2: Cover adequacy
    cover_required = _get_min_cover(exposure)
    cover_available = (D_mm - d_mm)  # Approximate from effective depth
    if cover_available >= cover_required:
        status = "pass"
        message = f"OK ({cover_available:.0f}mm ≥ {cover_required}mm)"
    elif cover_available >= cover_required * 0.9:
        status = "warning"
        message = f"Marginal ({cover_available:.0f}mm ~ {cover_required}mm)"
    else:
        status = "fail"
        message = f"Insufficient ({cover_available:.0f}mm < {cover_required}mm)"

    checks.append({
        "name": "Cover",
        "status": status,
        "value": round(cover_available, 0),
        "limit": cover_required,
        "message": message,
        "clause": "IS 456 Cl. 26.4"
    })

    # Check 3: b/D ratio (reasonable proportions)
    b_D = b_mm / D_mm if D_mm > 0 else 0
    if 0.3 <= b_D <= 0.67:
        status = "pass"
        message = f"Good proportions ({b_D:.2f})"
    elif 0.25 <= b_D <= 0.75:
        status = "warning"
        message = f"Unusual ({b_D:.2f})"
    else:
        status = "fail"
        message = f"Check proportions ({b_D:.2f})"

    checks.append({
        "name": "b/D Ratio",
        "status": status,
        "value": round(b_D, 2),
        "limit": "0.3-0.67",
        "message": message,
        "clause": "Practice"
    })

    # Check 4: d < D
    if d_mm < D_mm:
        status = "pass"
        message = "OK"
    else:
        status = "fail"
        message = f"d ({d_mm}) must be < D ({D_mm})"

    checks.append({
        "name": "d < D",
        "status": status,
        "value": d_mm,
        "limit": D_mm,
        "message": message,
        "clause": "Basic"
    })

    return checks


def _get_min_cover(exposure: str) -> int:
    """Get minimum cover per IS 456 Table 16."""
    cover_map = {
        "Mild": 20,
        "Moderate": 30,
        "Severe": 45,
        "Very Severe": 50,
        "Extreme": 75
    }
    return cover_map.get(exposure, 30)


def render_status_dashboard(checks: List[Dict]) -> None:
    """
    Render color-coded status dashboard.

    Args:
        checks: List of check dicts from calculate_quick_checks()
    """
    # Create columns for checks
    cols = st.columns(len(checks))

    for i, check in enumerate(checks):
        with cols[i]:
            # Status indicator
            if check["status"] == "pass":
                icon = "✅"
                color = COLORS.success
            elif check["status"] == "warning":
                icon = "⚠️"
                color = COLORS.warning
            else:
                icon = "❌"
                color = COLORS.error

            # Render metric-like display
            st.markdown(f"""
            <div style="
                padding: 8px;
                border-radius: 8px;
                background: {color}15;
                border-left: 4px solid {color};
                text-align: center;
            ">
                <div style="font-size: 20px;">{icon}</div>
                <div style="font-weight: 600; font-size: 12px; color: {COLORS.gray_700};">
                    {check['name']}
                </div>
                <div style="font-size: 11px; color: {COLORS.gray_500};">
                    {check['message']}
                </div>
            </div>
            """, unsafe_allow_html=True)


def calculate_rough_cost(
    b_mm: float,
    D_mm: float,
    span_mm: float,
    concrete_grade: str,
    mu_knm: float
) -> Dict:
    """
    Calculate rough cost estimate for beam.

    Uses simplified assumptions:
    - Concrete volume = b × D × span
    - Steel estimate from moment (empirical formula)
    - Standard rates (approximate)

    Returns dict with cost breakdown.
    """
    # Convert to meters
    b_m = b_mm / 1000
    D_m = D_mm / 1000
    span_m = span_mm / 1000

    # Concrete volume (m³)
    volume_m3 = b_m * D_m * span_m

    # Concrete rate (₹/m³) - approximate
    concrete_rates = {
        "M20": 5500,
        "M25": 6000,
        "M30": 6500,
        "M35": 7500,
        "M40": 8500
    }
    concrete_rate = concrete_rates.get(concrete_grade, 6000)
    concrete_cost = volume_m3 * concrete_rate

    # Steel estimate (kg) - rough empirical: 80-120 kg/m³ concrete
    steel_kg_per_m3 = 100  # Middle estimate
    steel_kg = volume_m3 * steel_kg_per_m3

    # Adjust for moment intensity (higher moment = more steel)
    moment_factor = min(max(mu_knm / 100, 0.5), 2.0)  # Scale 0.5-2.0
    steel_kg *= moment_factor

    # Steel rate (₹/kg) - approximate
    steel_rate = 85
    steel_cost = steel_kg * steel_rate

    # Total
    total_cost = concrete_cost + steel_cost

    return {
        "concrete_m3": round(volume_m3, 3),
        "concrete_rate": concrete_rate,
        "concrete_cost": round(concrete_cost, 0),
        "steel_kg": round(steel_kg, 1),
        "steel_rate": steel_rate,
        "steel_cost": round(steel_cost, 0),
        "total_cost": round(total_cost, 0)
    }


def render_cost_summary(cost: Dict) -> None:
    """
    Render cost summary in compact format.

    Args:
        cost: Dict from calculate_rough_cost()
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Concrete",
            value=f"₹{cost['concrete_cost']:,.0f}",
            help=f"{cost['concrete_m3']} m³ @ ₹{cost['concrete_rate']}/m³"
        )

    with col2:
        st.metric(
            label="Steel (est.)",
            value=f"₹{cost['steel_cost']:,.0f}",
            help=f"~{cost['steel_kg']:.0f} kg @ ₹{cost['steel_rate']}/kg"
        )

    with col3:
        st.metric(
            label="Total (approx.)",
            value=f"₹{cost['total_cost']:,.0f}",
            help="Preliminary estimate only"
        )

    st.caption("⚠️ Estimates are approximate. Actual costs depend on detailed design.")


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "render_real_time_preview",
    "create_beam_preview_diagram",
    "calculate_quick_checks",
    "render_status_dashboard",
    "calculate_rough_cost",
    "render_cost_summary"
]
```

**Verification:**
```bash
cd streamlit_app
../.venv/bin/python -c "from components.preview import render_real_time_preview; print('OK')"
# Should print: OK
```

---

### Task 3.2: Add __init__.py Export (5 min)

**File:** `streamlit_app/components/__init__.py`

**Add to file:**
```python
from .preview import (
    render_real_time_preview,
    create_beam_preview_diagram,
    calculate_quick_checks,
    render_status_dashboard,
    calculate_rough_cost,
    render_cost_summary
)
```

---

## 📋 Phase 4: Test Updates

### Task 4.1: Create Preview Component Tests (30 min)

**File:** `streamlit_app/tests/test_preview.py`

```python
"""
Preview Component Tests
=======================

Tests for real-time preview functionality.

Priority: HIGH (new code must have tests)
Coverage Target: 80%
"""

import pytest
from unittest.mock import Mock, patch

# Import preview functions
from components.preview import (
    create_beam_preview_diagram,
    calculate_quick_checks,
    calculate_rough_cost,
    _get_min_cover
)
from utils.design_system import ANIMATION


class TestCreateBeamPreviewDiagram:
    """Tests for beam preview diagram generation."""

    def test_returns_figure(self):
        """Should return a Plotly Figure object."""
        import plotly.graph_objects as go

        fig = create_beam_preview_diagram(
            span_mm=5000.0,
            b_mm=300.0,
            D_mm=500.0,
            support_condition="Simply Supported"
        )

        assert isinstance(fig, go.Figure)

    def test_uses_numeric_duration(self):
        """CRITICAL: Must use integer duration for Plotly."""
        fig = create_beam_preview_diagram(
            span_mm=5000.0,
            b_mm=300.0,
            D_mm=500.0,
            support_condition="Simply Supported"
        )

        # Check transition duration is integer
        duration = fig.layout.transition.duration
        assert isinstance(duration, int), f"Expected int, got {type(duration)}"
        assert duration == ANIMATION.duration_normal_ms

    def test_different_support_conditions(self):
        """Should handle all support conditions."""
        conditions = ["Simply Supported", "Cantilever", "Fixed-Fixed", "Unknown"]

        for condition in conditions:
            fig = create_beam_preview_diagram(
                span_mm=5000.0,
                b_mm=300.0,
                D_mm=500.0,
                support_condition=condition
            )
            assert fig is not None

    def test_has_beam_shape(self):
        """Figure should contain beam rectangle shape."""
        fig = create_beam_preview_diagram(
            span_mm=5000.0,
            b_mm=300.0,
            D_mm=500.0,
            support_condition="Simply Supported"
        )

        # Check for at least one shape (beam rectangle)
        assert len(fig.layout.shapes) >= 1


class TestCalculateQuickChecks:
    """Tests for design check calculations."""

    def test_returns_list(self):
        """Should return a list of checks."""
        checks = calculate_quick_checks(
            span_mm=5000.0,
            d_mm=450.0,
            b_mm=300.0,
            D_mm=500.0,
            exposure="Moderate"
        )

        assert isinstance(checks, list)
        assert len(checks) >= 4  # At least 4 checks

    def test_check_structure(self):
        """Each check should have required fields."""
        checks = calculate_quick_checks(
            span_mm=5000.0,
            d_mm=450.0,
            b_mm=300.0,
            D_mm=500.0,
            exposure="Moderate"
        )

        required_fields = ["name", "status", "value", "limit", "message"]
        for check in checks:
            for field in required_fields:
                assert field in check, f"Missing {field} in check {check.get('name')}"

    def test_status_values(self):
        """Status should be one of: pass, warning, fail."""
        checks = calculate_quick_checks(
            span_mm=5000.0,
            d_mm=450.0,
            b_mm=300.0,
            D_mm=500.0,
            exposure="Moderate"
        )

        valid_statuses = {"pass", "warning", "fail"}
        for check in checks:
            assert check["status"] in valid_statuses

    def test_span_d_pass(self):
        """Good span/d should pass."""
        checks = calculate_quick_checks(
            span_mm=5000.0,
            d_mm=450.0,  # span/d = 11.1, well under 20
            b_mm=300.0,
            D_mm=500.0,
            exposure="Moderate"
        )

        span_d_check = next(c for c in checks if c["name"] == "Span/d Ratio")
        assert span_d_check["status"] == "pass"

    def test_span_d_fail(self):
        """Bad span/d should fail."""
        checks = calculate_quick_checks(
            span_mm=10000.0,
            d_mm=300.0,  # span/d = 33.3, over 20
            b_mm=300.0,
            D_mm=350.0,
            exposure="Moderate"
        )

        span_d_check = next(c for c in checks if c["name"] == "Span/d Ratio")
        assert span_d_check["status"] == "fail"

    def test_d_less_than_D(self):
        """d < D check should work."""
        # Valid case
        checks_valid = calculate_quick_checks(
            span_mm=5000.0,
            d_mm=450.0,
            b_mm=300.0,
            D_mm=500.0,
            exposure="Moderate"
        )
        d_D_check = next(c for c in checks_valid if c["name"] == "d < D")
        assert d_D_check["status"] == "pass"

        # Invalid case (d >= D)
        checks_invalid = calculate_quick_checks(
            span_mm=5000.0,
            d_mm=500.0,  # d == D, invalid
            b_mm=300.0,
            D_mm=500.0,
            exposure="Moderate"
        )
        d_D_check = next(c for c in checks_invalid if c["name"] == "d < D")
        assert d_D_check["status"] == "fail"


class TestGetMinCover:
    """Tests for minimum cover lookup."""

    def test_known_exposures(self):
        """Should return correct cover for known exposures."""
        assert _get_min_cover("Mild") == 20
        assert _get_min_cover("Moderate") == 30
        assert _get_min_cover("Severe") == 45
        assert _get_min_cover("Very Severe") == 50
        assert _get_min_cover("Extreme") == 75

    def test_unknown_exposure(self):
        """Should return default for unknown exposure."""
        assert _get_min_cover("Unknown") == 30
        assert _get_min_cover("") == 30


class TestCalculateRoughCost:
    """Tests for cost estimation."""

    def test_returns_dict(self):
        """Should return a cost dict."""
        cost = calculate_rough_cost(
            b_mm=300.0,
            D_mm=500.0,
            span_mm=5000.0,
            concrete_grade="M25",
            mu_knm=120.0
        )

        assert isinstance(cost, dict)

    def test_cost_structure(self):
        """Cost dict should have required fields."""
        cost = calculate_rough_cost(
            b_mm=300.0,
            D_mm=500.0,
            span_mm=5000.0,
            concrete_grade="M25",
            mu_knm=120.0
        )

        required = ["concrete_m3", "concrete_cost", "steel_kg", "steel_cost", "total_cost"]
        for field in required:
            assert field in cost, f"Missing {field}"

    def test_positive_values(self):
        """All costs should be positive."""
        cost = calculate_rough_cost(
            b_mm=300.0,
            D_mm=500.0,
            span_mm=5000.0,
            concrete_grade="M25",
            mu_knm=120.0
        )

        assert cost["concrete_cost"] > 0
        assert cost["steel_cost"] > 0
        assert cost["total_cost"] > 0

    def test_total_is_sum(self):
        """Total should be concrete + steel."""
        cost = calculate_rough_cost(
            b_mm=300.0,
            D_mm=500.0,
            span_mm=5000.0,
            concrete_grade="M25",
            mu_knm=120.0
        )

        expected_total = cost["concrete_cost"] + cost["steel_cost"]
        assert cost["total_cost"] == expected_total

    def test_higher_moment_more_steel(self):
        """Higher moment should estimate more steel."""
        cost_low = calculate_rough_cost(
            b_mm=300.0,
            D_mm=500.0,
            span_mm=5000.0,
            concrete_grade="M25",
            mu_knm=50.0  # Low moment
        )

        cost_high = calculate_rough_cost(
            b_mm=300.0,
            D_mm=500.0,
            span_mm=5000.0,
            concrete_grade="M25",
            mu_knm=200.0  # High moment
        )

        assert cost_high["steel_kg"] > cost_low["steel_kg"]


class TestIntegration:
    """Integration tests for preview pipeline."""

    def test_full_preview_flow(self):
        """Test complete preview generation without errors."""
        # This simulates what render_real_time_preview does
        fig = create_beam_preview_diagram(
            span_mm=5000.0,
            b_mm=300.0,
            D_mm=500.0,
            support_condition="Simply Supported"
        )
        assert fig is not None

        checks = calculate_quick_checks(
            span_mm=5000.0,
            d_mm=450.0,
            b_mm=300.0,
            D_mm=500.0,
            exposure="Moderate"
        )
        assert len(checks) >= 4

        cost = calculate_rough_cost(
            b_mm=300.0,
            D_mm=500.0,
            span_mm=5000.0,
            concrete_grade="M25",
            mu_knm=120.0
        )
        assert cost["total_cost"] > 0

    def test_preview_with_design_system_tokens(self):
        """Verify design system tokens are used correctly."""
        fig = create_beam_preview_diagram(
            span_mm=5000.0,
            b_mm=300.0,
            D_mm=500.0,
            support_condition="Simply Supported"
        )

        # CRITICAL: Verify Plotly gets integer duration
        assert isinstance(fig.layout.transition.duration, int)
        assert fig.layout.transition.duration == ANIMATION.duration_normal_ms
```

**Run tests:**
```bash
cd streamlit_app
../.venv/bin/python -m pytest tests/test_preview.py -v
```

**Expected:** All tests pass

---

### Task 4.2: Update Existing Tests If Needed (15 min)

**Check for test failures:**
```bash
cd streamlit_app
../.venv/bin/python -m pytest tests/ -v --tb=short 2>&1 | grep -E "(FAILED|ERROR)"
```

**If any failures related to layout changes:**
1. Update test expectations for new layout structure
2. Don't change logic tests, only UI structure tests

---

## 📋 Phase 1: Token Protocols (OPTIONAL - Future)

### Task 1.1: Create Token Contracts File

**Note:** This task is DEFERRED. The current dual-token system works correctly.

Only implement if:
- Adding new consumers beyond CSS/Plotly
- Starting DXF/PDF export features
- Refactoring design_system.py

**File to create (future):** `streamlit_app/utils/design_tokens_protocols.py`

See [UI-LAYOUT-CRITICAL-FINDINGS.md](UI-LAYOUT-CRITICAL-FINDINGS.md) for complete implementation.

---

## 🔧 Verification Checklist

### After All Changes

```bash
# 1. Run all tests
cd streamlit_app
../.venv/bin/python -m pytest tests/ -v --tb=short

# 2. Check specific token tests
../.venv/bin/python -m pytest tests/test_design_token_contracts.py tests/test_plotly_token_usage.py -v

# 3. Check preview tests
../.venv/bin/python -m pytest tests/test_preview.py -v

# 4. Test app runs
../.venv/bin/streamlit run app.py --server.headless=true &
sleep 5
curl -s http://localhost:8501 | head -20
pkill -f streamlit

# 5. Check imports
../.venv/bin/python -c "
from components.preview import render_real_time_preview
from utils.design_system import ANIMATION
print(f'ANIMATION.fast = {ANIMATION.fast}')  # Should be '200ms'
print(f'ANIMATION.duration_fast_ms = {ANIMATION.duration_fast_ms}')  # Should be 200
print('All imports OK')
"
```

---

## ⚠️ Error Prevention

### Common Mistakes to Avoid

| Mistake | Consequence | Prevention |
|---------|-------------|------------|
| Using `ANIMATION.fast` in Plotly | TypeError at runtime | Always use `ANIMATION.duration_*_ms` for Plotly |
| Using `ANIMATION.duration_fast_ms` in CSS | Shows "200" not "200ms" | Always use `ANIMATION.fast` for CSS |
| Forgetting to import preview | ImportError | Check imports before running |
| Not running tests | Regressions slip through | Run all tests after changes |
| Breaking existing tests | CI failures | Don't modify logic tests |

### Rollback Procedure

If something goes wrong:
```bash
# 1. Reset to backup branch
git checkout backup/ui-layout-YYYYMMDD

# 2. Force push to main (ONLY if safe)
# git push origin backup/ui-layout-YYYYMMDD:main --force
# ⚠️ Only do this if no one else has pushed

# 3. Or just reset and re-implement carefully
git checkout main
git reset --hard origin/main
```

---

## 📊 Success Criteria

| Metric | Target | Verification |
|--------|--------|--------------|
| All tests pass | 100% | `pytest tests/ -v` |
| Token tests pass | 100% | `pytest tests/test_*token*.py -v` |
| Preview tests pass | 100% | `pytest tests/test_preview.py -v` |
| No runtime errors | 0 errors | Run app, click through pages |
| Layout renders | Visible two columns | Visual check on desktop |
| Preview updates | Real-time | Change input, see preview update |

---

## 📚 Reference Documents

| Document | Purpose |
|----------|---------|
| [UI-LAYOUT-CRITICAL-FINDINGS.md](UI-LAYOUT-CRITICAL-FINDINGS.md) | Token architecture details |
| [ui-layout-implementation-plan.md](../../planning/ui-layout-implementation-plan.md) | Original plan (reference) |
| [ui-layout-best-practices.md](../../research/ui-layout-best-practices.md) | Research findings |
| [data-model-compatibility-checklist.md](../../planning/data-model-compatibility-checklist.md) | Data model alignment |

---

## 🔄 Git Workflow Reminder

```bash
# ALWAYS use:
./scripts/ai_commit.sh "feat(ui): implement two-column layout"

# NEVER use:
git add . && git commit -m "..."
```

---

## 📝 Sign-Off

**Document reviewed:** ✅
**Tests defined:** ✅
**Rollback plan:** ✅
**Error prevention:** ✅

**Ready for implementation.** Follow tasks in order. Run verification after each task.
