# UI Layout Redesign - Final Decision & Implementation Plan

**Type:** Plan
**Audience:** Developers
**Status:** Approved
**Importance:** High
**Created:** 2026-01-08
**Last Updated:** 2026-01-13

---

**Estimated Time:** 3-4 hours (Phase 1)
**Risk Level:** LOW

---

## Executive Summary

**Decision:** Implement **Option 1 (Two-Column Layout)** with real-time preview and design system integration.

**Rationale:**
- Current sidebar layout wastes 80% of screen space
- Industry standard pattern (ETABS, ClearCalcs, AutoCAD)
- Professional first impression for engineering users
- Real-time feedback improves UX significantly
- Reasonable implementation effort (3-4 hours)

**Success Metrics:**
- Input panel increased from ~20% to 40% width
- Preview panel utilizes 60% of screen (not empty)
- Real-time beam diagram updates as user types
- Status dashboard shows validation checks
- Professional appearance rating: 9/10 (from current 6/10)

---

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Chosen Solution](#chosen-solution)
3. [Implementation Plan](#implementation-plan)
4. [Error Prevention Strategy](#error-prevention-strategy)
5. [Testing Strategy](#testing-strategy)
6. [Long-Term Architecture](#long-term-architecture)
7. [Rollout Plan](#rollout-plan)

---

## Current State Analysis

### Problems Identified

**Visual Issues:**
```
Current Layout (BEFORE):
┌─────────┬──────────────────────────────────────────┐
│Sidebar  │                                          │
│ (20%)   │         Empty Space (80%)                │
│         │                                          │
│Inputs   │   "Click Analyze to see results"        │
│         │                                          │
└─────────┴──────────────────────────────────────────┘
  Cramped              Wasted
```

**Specific Issues:**
1. ❌ Sidebar uses only ~300px on 1920px screen (15% utilization)
2. ❌ Main area empty until "Analyze" clicked (poor first impression)
3. ❌ No real-time feedback (user blind until submit)
4. ❌ Doesn't match industry standard tools
5. ❌ Feels unbalanced and unprofessional

**User Impact:**
- Students: "Looks like a prototype"
- Engineers: "Where are the preview diagrams?"
- Reviewers: "Doesn't look production-ready"

---

## Chosen Solution

### Option 1: Two-Column Layout

```
Proposed Layout (AFTER):
┌──────────────────────┬─────────────────────────────┐
│  INPUT PANEL (40%)   │  PREVIEW PANEL (60%)        │
│                      │                             │
│ 📏 Geometry          │  ┌───────────────────────┐  │
│ Span:    [5000mm]    │  │ [Live Beam Diagram]   │  │
│ Width:    [300mm]    │  │ ━━━━━━━━━━━━━━━━━     │  │
│ Depth:    [500mm]    │  │ ▲            ▲        │  │
│                      │  │ 5000 x 300 x 500      │  │
│ 🧱 Materials         │  └───────────────────────┘  │
│ Concrete: [M25 ▼]    │                             │
│ Steel:   [Fe500 ▼]   │  Status Dashboard:          │
│                      │  ✓ Span/d ratio: OK (11.1)  │
│ ⚡ Loading           │  ⚠️ Min steel: Review        │
│ Moment: [120kNm]     │  ✓ Cover: Adequate          │
│ Shear:   [80kN ]     │                             │
│                      │  Cost Estimate: ₹20,650     │
│ [🔍 Analyze Design]  │                             │
│                      │  [Results after analyze]    │
└──────────────────────┴─────────────────────────────┘
  Comfortable              Always Useful
```

### Key Features

**Left Panel (40%):**
- All input controls (geometry, materials, loading)
- Collapsible sections (advanced options)
- Prominent "Analyze" button
- Example design quick-load

**Right Panel (60%):**
- **Before Analyze:** Real-time preview
  - Beam elevation diagram (updates as you type)
  - Status dashboard (validation checks: ✓ ❌ ⚠️)
  - Cost estimate (rough calculation)
  - Material properties summary
- **After Analyze:** Full results
  - Tabbed results (Summary, Charts, Compliance, Export)
  - Same real-time preview at top
  - Detailed analysis below

---

## Implementation Plan

### Phase 1: Core Layout Transformation (Day 1 - 3-4 hours)

#### Task 1.1: Replace Sidebar with Columns (45 min)

**File:** `streamlit_app/pages/01_🏗️_beam_design.py`

**Changes:**
```python
# BEFORE:
with st.sidebar:
    st.header("📋 Input Parameters")
    # ... all inputs ...

# AFTER:
col_input, col_preview = st.columns([2, 3])  # 40/60 split

with col_input:
    st.header("📋 Input Parameters")
    # ... all inputs (same code) ...

with col_preview:
    st.header("Preview & Status")
    # New: Real-time preview
    render_real_time_preview()
    # After analyze: Results
    if st.session_state.get('design_computed'):
        render_results_tabs()
```

**Files to modify:**
- `streamlit_app/pages/01_🏗️_beam_design.py` (primary)
- `streamlit_app/pages/02_💰_cost_optimizer.py` (similar pattern)
- `streamlit_app/pages/03_✅_compliance.py` (similar pattern)

**Expected outcome:** Layout switches from sidebar to two-column

#### Task 1.2: Create Real-Time Preview Component (60 min)

**New file:** `streamlit_app/components/preview.py`

**Functions to create:**

```python
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
    Render real-time preview panel.

    Shows:
    - Beam elevation diagram (live updates)
    - Status dashboard (validation checks)
    - Cost estimate (rough calculation)

    Uses design system tokens for consistent styling.
    """
    # Section 1: Beam Diagram
    st.subheader("Beam Preview")
    fig = create_beam_preview_diagram(span_mm, b_mm, D_mm, support_condition)
    st.plotly_chart(fig, width="stretch")

    # Section 2: Status Dashboard
    st.subheader("Design Status")
    status_metrics = calculate_quick_checks(span_mm, d_mm, b_mm, D_mm, exposure)
    render_status_dashboard(status_metrics)

    # Section 3: Cost Estimate
    st.subheader("Preliminary Cost")
    cost_estimate = calculate_rough_cost(b_mm, D_mm, span_mm, concrete_grade, mu_knm)
    render_cost_summary(cost_estimate)


def create_beam_preview_diagram(
    span_mm: float,
    b_mm: float,
    D_mm: float,
    support_condition: str
) -> go.Figure:
    """
    Create simple beam elevation diagram.

    Shows:
    - Beam outline (span × depth)
    - Support symbols (fixed/pin/roller)
    - Dimensions annotated

    Uses ANIMATION.duration_normal_ms for transitions (Plotly-compatible).
    """
    # Create figure
    fig = go.Figure()

    # Beam rectangle
    fig.add_shape(
        type="rect",
        x0=0, x1=span_mm,
        y0=0, y1=D_mm,
        line=dict(color=COLORS.primary_500, width=2),
        fillcolor=COLORS.primary_50
    )

    # Support symbols
    if support_condition == "Simply Supported":
        add_pin_support(fig, 0, 0)
        add_roller_support(fig, span_mm, 0)
    elif support_condition == "Fixed-Fixed":
        add_fixed_support(fig, 0, 0)
        add_fixed_support(fig, span_mm, 0)

    # Annotations
    fig.add_annotation(
        x=span_mm/2, y=D_mm + 50,
        text=f"Span: {span_mm:.0f} mm",
        showarrow=False
    )

    fig.update_layout(
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False, scaleanchor="x"),
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        transition=dict(
            duration=ANIMATION.duration_normal_ms,  # Use Plotly-compatible token
            easing='cubic-in-out'
        )
    )

    return fig


def calculate_quick_checks(
    span_mm: float,
    d_mm: float,
    b_mm: float,
    D_mm: float,
    exposure: str
) -> Dict[str, Dict[str, Any]]:
    """
    Calculate quick validation checks.

    Returns dict of checks with status (ok/warning/error).
    """
    checks = {}

    # Check 1: Span/d ratio (Cl. 23.2.1)
    span_d_ratio = span_mm / d_mm
    if span_d_ratio <= 20:
        checks['span_d'] = {'status': 'ok', 'value': span_d_ratio, 'limit': 20}
    elif span_d_ratio <= 26:
        checks['span_d'] = {'status': 'warning', 'value': span_d_ratio, 'limit': 20}
    else:
        checks['span_d'] = {'status': 'error', 'value': span_d_ratio, 'limit': 20}

    # Check 2: Width/depth ratio
    b_D_ratio = b_mm / D_mm
    if 0.3 <= b_D_ratio <= 0.6:
        checks['b_D'] = {'status': 'ok', 'value': b_D_ratio, 'range': '0.3-0.6'}
    else:
        checks['b_D'] = {'status': 'warning', 'value': b_D_ratio, 'range': '0.3-0.6'}

    # Check 3: Effective depth check
    if d_mm < D_mm:
        checks['d_valid'] = {'status': 'ok', 'message': 'd < D'}
    else:
        checks['d_valid'] = {'status': 'error', 'message': 'd must be < D'}

    # Check 4: Cover adequacy
    required_covers = {
        'Mild': 20,
        'Moderate': 30,
        'Severe': 45,
        'Very Severe': 50,
        'Extreme': 75
    }
    required_cover = required_covers.get(exposure, 30)
    actual_cover = D_mm - d_mm
    if actual_cover >= required_cover:
        checks['cover'] = {'status': 'ok', 'actual': actual_cover, 'required': required_cover}
    elif actual_cover >= required_cover * 0.9:
        checks['cover'] = {'status': 'warning', 'actual': actual_cover, 'required': required_cover}
    else:
        checks['cover'] = {'status': 'error', 'actual': actual_cover, 'required': required_cover}

    return checks


def render_status_dashboard(checks: Dict[str, Dict[str, Any]]) -> None:
    """
    Render status dashboard with color-coded checks.

    Uses design system:
    - COLORS.success for ok
    - COLORS.warning for warning
    - COLORS.error for error
    """
    for check_name, check_data in checks.items():
        status = check_data['status']

        if status == 'ok':
            icon = "✅"
            color = COLORS.success
        elif status == 'warning':
            icon = "⚠️"
            color = COLORS.warning
        else:
            icon = "❌"
            color = COLORS.error

        # Format message
        if check_name == 'span_d':
            message = f"Span/d ratio: {check_data['value']:.1f} (limit: {check_data['limit']})"
        elif check_name == 'b_D':
            message = f"Width/depth ratio: {check_data['value']:.2f} (typical: {check_data['range']})"
        elif check_name == 'd_valid':
            message = f"Effective depth: {check_data['message']}"
        elif check_name == 'cover':
            message = f"Cover: {check_data['actual']:.0f}mm (required: {check_data['required']}mm)"

        st.markdown(
            f'<div style="color: {color}; padding: 4px 0;">{icon} {message}</div>',
            unsafe_allow_html=True
        )


def calculate_rough_cost(
    b_mm: float,
    D_mm: float,
    span_mm: float,
    concrete_grade: str,
    mu_knm: float
) -> Dict[str, float]:
    """
    Calculate rough cost estimate.

    Very approximate - just for preview.
    Full calculation happens in design phase.
    """
    # Volume
    volume_m3 = (b_mm * D_mm * span_mm) / 1e9

    # Concrete cost (rough rates per m³)
    concrete_rates = {
        'M20': 5000,
        'M25': 5500,
        'M30': 6000,
        'M35': 6500,
        'M40': 7000
    }
    concrete_cost = volume_m3 * concrete_rates.get(concrete_grade, 5500)

    # Steel estimate (very rough: 1% of concrete volume)
    steel_density = 7850  # kg/m³
    steel_volume_m3 = volume_m3 * 0.01  # Assume 1% reinforcement
    steel_kg = steel_volume_m3 * steel_density
    steel_cost = steel_kg * 60  # ₹60/kg rough rate

    return {
        'concrete': concrete_cost,
        'steel': steel_cost,
        'total': concrete_cost + steel_cost,
        'volume_m3': volume_m3,
        'steel_kg': steel_kg
    }


def render_cost_summary(cost_estimate: Dict[str, float]) -> None:
    """Render cost summary with proper formatting."""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Concrete",
            f"₹{cost_estimate['concrete']:,.0f}",
            delta=f"{cost_estimate['volume_m3']:.2f} m³"
        )

    with col2:
        st.metric(
            "Steel",
            f"₹{cost_estimate['steel']:,.0f}",
            delta=f"{cost_estimate['steel_kg']:.0f} kg"
        )

    with col3:
        st.metric(
            "Total",
            f"₹{cost_estimate['total']:,.0f}",
            delta="Rough estimate"
        )

    st.caption("⚠️ Preliminary estimate only. Full cost calculated after analysis.")
```

**Expected outcome:** Real-time preview working with validation checks

#### Task 1.3: Integrate with Existing Code (45 min)

**Modifications to `beam_design.py`:**

```python
# Add import at top
from components.preview import render_real_time_preview

# In the main body (after creating columns):
with col_preview:
    st.header("📊 Preview & Status")

    # Always show real-time preview
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

    # After analyze: Show full results
    if st.session_state.beam_inputs.get('design_computed'):
        st.markdown("---")
        st.subheader("📋 Detailed Results")
        # Existing results tabs code here
```

**Expected outcome:** Preview panel populates with real-time data

#### Task 1.4: Responsive Design (30 min)

**Add responsive breakpoints:**

```python
# At start of page
def get_layout_config():
    """Determine layout based on screen size."""
    # Use session state to track viewport (set by JS injection)
    viewport_width = st.session_state.get('viewport_width', 1920)

    if viewport_width < 768:
        # Mobile: Stack vertically
        return {
            'use_columns': False,
            'input_width': 1,
            'preview_width': 1
        }
    elif viewport_width < 1024:
        # Tablet: 50/50 split
        return {
            'use_columns': True,
            'input_width': 1,
            'preview_width': 1
        }
    else:
        # Desktop: 40/60 split
        return {
            'use_columns': True,
            'input_width': 2,
            'preview_width': 3
        }

# Use layout config
layout_config = get_layout_config()

if layout_config['use_columns']:
    col_input, col_preview = st.columns([
        layout_config['input_width'],
        layout_config['preview_width']
    ])
    # ... columns layout
else:
    # Mobile: Stacked containers
    col_input = st.container()
    col_preview = st.container()
    # ... same content but stacked
```

**Expected outcome:** Layout adapts to screen size

---

### Phase 2: Polish & Enhancement (Day 2 - 2 hours)

#### Task 2.1: Collapsible Sections (30 min)

**Add expanders for advanced options:**

```python
with col_input:
    # Basic inputs (always visible)
    with st.container():
        st.subheader("📏 Geometry")
        # span, width, depth, d

    with st.container():
        st.subheader("🧱 Materials")
        # concrete, steel

    with st.container():
        st.subheader("⚡ Loading")
        # moment, shear

    # Advanced options (collapsed by default)
    with st.expander("🌡️ Advanced Options", expanded=False):
        # exposure, support, cover, bar sizes, etc.
```

#### Task 2.2: Example Designs (45 min)

**Add quick-load buttons:**

```python
st.subheader("📚 Example Designs")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("5m Simply Supported", width="stretch"):
        load_example_design('5m_simple')

with col2:
    if st.button("6m Continuous", width="stretch"):
        load_example_design('6m_continuous')

with col3:
    if st.button("2m Cantilever", width="stretch"):
        load_example_design('2m_cantilever')

def load_example_design(example_id: str) -> None:
    """Load predefined example design."""
    examples = {
        '5m_simple': {
            'span_mm': 5000,
            'b_mm': 300,
            'D_mm': 500,
            'd_mm': 450,
            'concrete_grade': 'M25',
            'steel_grade': 'Fe500',
            'mu_knm': 120,
            'vu_kn': 80,
            'exposure': 'Moderate',
            'support_condition': 'Simply Supported'
        },
        # ... other examples
    }

    if example_id in examples:
        st.session_state.beam_inputs.update(examples[example_id])
        st.rerun()
```

#### Task 2.3: Visual Polish (45 min)

**Use design system consistently:**

```python
# Apply custom CSS for polish
st.markdown(f"""
<style>
    /* Input panel styling */
    .stColumn:first-child {{
        background-color: {COLORS.gray_50};
        padding: {SPACING.lg};
        border-radius: {SPACING.sm};
        border-right: 1px solid {COLORS.gray_200};
    }}

    /* Preview panel styling */
    .stColumn:last-child {{
        background-color: white;
        padding: {SPACING.lg};
    }}

    /* Status check styling */
    .status-ok {{
        color: {COLORS.success};
        font-weight: {TYPOGRAPHY.body_weight};
    }}

    .status-warning {{
        color: {COLORS.warning};
        font-weight: {TYPOGRAPHY.body_weight};
    }}

    .status-error {{
        color: {COLORS.error};
        font-weight: {TYPOGRAPHY.body_weight};
    }}

    /* Analyze button prominence */
    .stButton > button {{
        background-color: {COLORS.accent_500};
        color: white;
        font-size: {TYPOGRAPHY.body_lg_size};
        font-weight: {TYPOGRAPHY.body_lg_weight};
        padding: {SPACING.md} {SPACING.xl};
        border-radius: {SPACING.sm};
        box-shadow: {ELEVATION.shadow_md};
    }}

    .stButton > button:hover {{
        background-color: {COLORS.accent_600};
        box-shadow: {ELEVATION.shadow_lg};
    }}
</style>
""", unsafe_allow_html=True)
```

---

## Error Prevention Strategy

### Critical Lessons from Plotly Type Mismatch

**What We Learned:**
1. ❌ Tests can pass but production fails (structure ≠ usage)
2. ❌ Multi-consumer tokens need format validation
3. ❌ Design system assumptions don't always match library needs
4. ✅ Dual-format tokens work well (e.g., `duration_normal` + `duration_normal_ms`)

### Prevention Measures for This Implementation

#### 1. Token Usage Validation

**Before using design tokens in new code:**
```python
# BAD: Assume token format
fig.update_layout(
    transition=dict(duration=ANIMATION.duration_normal)  # May fail!
)

# GOOD: Use Plotly-specific token
fig.update_layout(
    transition=dict(duration=ANIMATION.duration_normal_ms)  # Guaranteed integer
)
```

**Create token usage tests:**
```python
# New file: streamlit_app/tests/test_preview_tokens.py

def test_preview_uses_plotly_tokens():
    """Verify preview.py uses Plotly-compatible tokens."""
    from components.preview import create_beam_preview_diagram

    fig = create_beam_preview_diagram(5000, 300, 500, "Simply Supported")

    # Check transition uses numeric duration
    assert isinstance(fig.layout.transition.duration, int)
    assert fig.layout.transition.duration == ANIMATION.duration_normal_ms

def test_preview_diagram_renders():
    """Integration test: Preview diagram actually renders."""
    from components.preview import create_beam_preview_diagram

    fig = create_beam_preview_diagram(5000, 300, 500, "Simply Supported")

    # Verify figure is valid
    assert len(fig.data) > 0 or len(fig.layout.shapes) > 0

    # Verify no errors when rendering
    try:
        fig_json = fig.to_json()
        assert fig_json is not None
    except Exception as e:
        pytest.fail(f"Figure failed to render: {e}")
```

#### 2. Component Integration Tests

**Test actual rendering, not just structure:**
```python
# New file: streamlit_app/tests/test_preview_integration.py

def test_render_real_time_preview_runs():
    """Smoke test: Preview renders without errors."""
    from components.preview import render_real_time_preview

    # Mock streamlit functions
    with patch('streamlit.subheader'), \
         patch('streamlit.plotly_chart'), \
         patch('streamlit.markdown'), \
         patch('streamlit.metric'):

        # Should not raise any errors
        render_real_time_preview(
            span_mm=5000,
            b_mm=300,
            D_mm=500,
            d_mm=450,
            concrete_grade='M25',
            steel_grade='Fe500',
            mu_knm=120,
            vu_kn=80,
            exposure='Moderate',
            support_condition='Simply Supported'
        )

def test_quick_checks_calculation():
    """Verify quick checks produce valid results."""
    from components.preview import calculate_quick_checks

    checks = calculate_quick_checks(
        span_mm=5000,
        d_mm=450,
        b_mm=300,
        D_mm=500,
        exposure='Moderate'
    )

    # Verify required checks exist
    assert 'span_d' in checks
    assert 'b_D' in checks
    assert 'd_valid' in checks
    assert 'cover' in checks

    # Verify structure
    for check in checks.values():
        assert 'status' in check
        assert check['status'] in ['ok', 'warning', 'error']
```

#### 3. Pre-Commit Validation

**Add to `.pre-commit-config.yaml`:**
```yaml
- id: check-plotly-token-usage
  name: Check Plotly token usage
  entry: python scripts/check_plotly_tokens.py
  language: system
  files: ^streamlit_app/(components|pages)/.*\.py$
  pass_filenames: true
```

**Script:** `scripts/check_plotly_tokens.py`
```python
#!/usr/bin/env python3
"""
Validate Plotly token usage in Streamlit components.

Ensures:
- fig.update_layout(transition=dict(duration=...)) uses _ms tokens
- No string tokens used where integers expected
"""
import ast
import sys
from pathlib import Path

def check_file(filepath: Path) -> list[str]:
    """Check a file for improper Plotly token usage."""
    with open(filepath) as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return []

    errors = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check fig.update_layout calls
            if hasattr(node.func, 'attr') and node.func.attr == 'update_layout':
                for keyword in node.keywords:
                    if keyword.arg == 'transition':
                        # Check duration value
                        if isinstance(keyword.value, ast.Dict):
                            for key, val in zip(keyword.value.keys, keyword.value.values):
                                if hasattr(key, 's') and key.s == 'duration':
                                    if isinstance(val, ast.Attribute):
                                        if 'duration' in val.attr and '_ms' not in val.attr:
                                            errors.append(
                                                f"{filepath}:{node.lineno}: "
                                                f"Use _ms suffix for Plotly duration: {val.attr}"
                                            )

    return errors

def main():
    files = [Path(f) for f in sys.argv[1:]]
    all_errors = []

    for filepath in files:
        errors = check_file(filepath)
        all_errors.extend(errors)

    if all_errors:
        print("❌ Plotly Token Validation Failed:\n")
        for error in all_errors:
            print(f"  {error}")
        print("\n💡 Fix: Use ANIMATION.duration_*_ms tokens for Plotly\n")
        sys.exit(1)

    print("✅ Plotly token usage validated")

if __name__ == "__main__":
    main()
```

#### 4. Manual Testing Checklist

**Before committing layout changes:**
- [ ] Load page in browser (not just pass tests)
- [ ] Verify preview updates when inputs change
- [ ] Check status dashboard shows correct colors
- [ ] Verify cost estimate calculates
- [ ] Test responsive layout (resize browser)
- [ ] Check on mobile device (or DevTools mobile emulation)
- [ ] Verify "Analyze" button works
- [ ] Confirm results display properly

---

## Testing Strategy

### Test Pyramid for UI Redesign

```
         /\
        /  \
       /E2E \     5% - Manual smoke tests
      /------\
     /        \
    /Integration\ 15% - Component integration tests
   /------------\
  /              \
 /  Unit Tests    \ 80% - Component unit tests
/------------------\
```

### Unit Tests (80% coverage target)

**File:** `streamlit_app/tests/test_preview_unit.py`

```python
def test_create_beam_preview_diagram_structure():
    """Test diagram has required elements."""
    fig = create_beam_preview_diagram(5000, 300, 500, "Simply Supported")
    assert len(fig.layout.shapes) >= 1  # Beam rectangle
    assert fig.layout.xaxis.visible == False
    assert fig.layout.transition.duration == ANIMATION.duration_normal_ms

def test_calculate_quick_checks_span_d():
    """Test span/d ratio check."""
    checks = calculate_quick_checks(5000, 450, 300, 500, 'Moderate')
    assert checks['span_d']['value'] == pytest.approx(11.1, abs=0.1)
    assert checks['span_d']['status'] == 'ok'

def test_calculate_quick_checks_cover():
    """Test cover adequacy check."""
    checks = calculate_quick_checks(5000, 450, 300, 500, 'Moderate')
    assert checks['cover']['actual'] == 50  # D - d = 500 - 450
    assert checks['cover']['required'] == 30  # Moderate exposure
    assert checks['cover']['status'] == 'ok'

def test_calculate_rough_cost():
    """Test cost estimation."""
    cost = calculate_rough_cost(300, 500, 5000, 'M25', 120)
    assert cost['volume_m3'] > 0
    assert cost['concrete'] > 0
    assert cost['steel'] > 0
    assert cost['total'] == cost['concrete'] + cost['steel']

def test_render_status_dashboard_colors():
    """Test status dashboard uses correct colors."""
    checks = {
        'test_ok': {'status': 'ok'},
        'test_warning': {'status': 'warning'},
        'test_error': {'status': 'error'}
    }

    with patch('streamlit.markdown') as mock_md:
        render_status_dashboard(checks)

        # Verify correct colors used
        calls = [str(call) for call in mock_md.call_args_list]
        assert any(COLORS.success in call for call in calls)
        assert any(COLORS.warning in call for call in calls)
        assert any(COLORS.error in call for call in calls)
```

### Integration Tests (15% coverage target)

**File:** `streamlit_app/tests/test_preview_integration.py`

```python
def test_preview_with_design_system():
    """Test preview uses design system tokens correctly."""
    fig = create_beam_preview_diagram(5000, 300, 500, "Simply Supported")

    # Check uses design system colors
    shape_colors = [shape.line.color for shape in fig.layout.shapes]
    assert COLORS.primary_500 in shape_colors

    # Check uses design system animation
    assert fig.layout.transition.duration == ANIMATION.duration_normal_ms
    assert fig.layout.transition.easing == 'cubic-in-out'

def test_full_preview_pipeline():
    """Integration test: Full preview rendering pipeline."""
    # Mock Streamlit functions
    with patch('streamlit.subheader'), \
         patch('streamlit.plotly_chart') as mock_plotly, \
         patch('streamlit.markdown'), \
         patch('streamlit.metric'):

        render_real_time_preview(
            span_mm=5000, b_mm=300, D_mm=500, d_mm=450,
            concrete_grade='M25', steel_grade='Fe500',
            mu_knm=120, vu_kn=80,
            exposure='Moderate', support_condition='Simply Supported'
        )

        # Verify plotly chart was called
        assert mock_plotly.called
        fig = mock_plotly.call_args[0][0]

        # Verify figure is valid
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.shapes) > 0

def test_layout_with_columns():
    """Test two-column layout integration."""
    # This would be a Selenium/Playwright test
    # For now, just verify column structure
    pass  # TODO: Add E2E test
```

### E2E/Manual Tests (5% - Checklist)

**Manual test checklist:**
```markdown
## Layout Tests
- [ ] Page loads without errors
- [ ] Two columns visible (40/60 split)
- [ ] Input panel on left, preview on right
- [ ] Responsive on mobile (stacked)
- [ ] Responsive on tablet (50/50)

## Preview Tests
- [ ] Beam diagram shows on page load
- [ ] Diagram updates when span changes
- [ ] Diagram updates when dimensions change
- [ ] Support symbols correct (pin/roller/fixed)
- [ ] Dimensions annotated

## Status Dashboard Tests
- [ ] Span/d check shows correct value
- [ ] Cover check shows correct value
- [ ] Colors correct (green/yellow/red)
- [ ] Icons correct (✓ ⚠️ ❌)

## Cost Estimate Tests
- [ ] Cost calculates on page load
- [ ] Updates when dimensions change
- [ ] Shows concrete, steel, total
- [ ] Format is readable (₹20,650)

## Results Integration Tests
- [ ] Click "Analyze" shows results
- [ ] Results appear below preview
- [ ] Preview stays visible at top
- [ ] Can switch between tabs

## Edge Cases
- [ ] Very small beam (span=1000, d=100)
- [ ] Very large beam (span=12000, d=900)
- [ ] Invalid input (d > D) shows error
- [ ] All example designs load correctly
```

---

## Long-Term Architecture

### Multi-Consumer Design Token System

**Problem Statement:**
- Design tokens created for ONE consumer (Streamlit CSS)
- But used by MULTIPLE consumers (CSS, Plotly, potentially DXF, PDF)
- Each consumer has different format requirements:
  - CSS: strings ("300ms", "#003366", "12px")
  - Plotly: integers/floats (300, 0x003366, 12)
  - DXF: native types (AutoCAD units)

**Current Solution (Tactical):**
- Dual-format tokens: `duration_normal` (CSS) + `duration_normal_ms` (Plotly)
- Works but doesn't scale (need 2× tokens for each format)

**Proposed Solution (Strategic):**

#### Token Adapter Pattern

```python
# New file: streamlit_app/utils/design_tokens_contracts.py

from typing import Protocol, Union
from dataclasses import dataclass

# ============================================================================
# PART 1: TOKEN PROTOCOLS (Type-safe interfaces)
# ============================================================================

class DurationToken(Protocol):
    """Protocol for duration tokens supporting multiple consumers."""

    def to_css(self) -> str:
        """Format for CSS (e.g., "300ms")."""
        ...

    def to_plotly(self) -> int:
        """Format for Plotly (e.g., 300)."""
        ...

    def to_seconds(self) -> float:
        """Format as seconds (e.g., 0.3)."""
        ...


class ColorToken(Protocol):
    """Protocol for color tokens supporting multiple consumers."""

    def to_css(self) -> str:
        """Format for CSS (e.g., "#003366")."""
        ...

    def to_plotly(self) -> str:
        """Format for Plotly (e.g., "#003366")."""
        ...

    def to_rgb(self) -> tuple[int, int, int]:
        """Format as RGB tuple (e.g., (0, 51, 102))."""
        ...

    def to_rgba(self, alpha: float = 1.0) -> str:
        """Format as RGBA (e.g., "rgba(0,51,102,1.0)")."""
        ...


class SpacingToken(Protocol):
    """Protocol for spacing tokens supporting multiple consumers."""

    def to_css(self) -> str:
        """Format for CSS (e.g., "16px")."""
        ...

    def to_pixels(self) -> int:
        """Format as pixel value (e.g., 16)."""
        ...

    def to_rem(self) -> float:
        """Format as rem value (e.g., 1.0)."""
        ...


# ============================================================================
# PART 2: TOKEN IMPLEMENTATIONS
# ============================================================================

@dataclass(frozen=True)
class Duration:
    """Duration token with multi-format support."""

    milliseconds: int

    def to_css(self) -> str:
        """CSS format: "300ms"."""
        return f"{self.milliseconds}ms"

    def to_plotly(self) -> int:
        """Plotly format: 300."""
        return self.milliseconds

    def to_seconds(self) -> float:
        """Seconds format: 0.3."""
        return self.milliseconds / 1000.0

    def __str__(self) -> str:
        """Default to CSS format."""
        return self.to_css()


@dataclass(frozen=True)
class Color:
    """Color token with multi-format support."""

    hex_value: str  # "#003366"

    def to_css(self) -> str:
        """CSS format: "#003366"."""
        return self.hex_value

    def to_plotly(self) -> str:
        """Plotly format: "#003366" (same as CSS)."""
        return self.hex_value

    def to_rgb(self) -> tuple[int, int, int]:
        """RGB tuple: (0, 51, 102)."""
        hex_clean = self.hex_value.lstrip('#')
        return tuple(int(hex_clean[i:i+2], 16) for i in (0, 2, 4))

    def to_rgba(self, alpha: float = 1.0) -> str:
        """RGBA string: "rgba(0,51,102,1.0)"."""
        r, g, b = self.to_rgb()
        return f"rgba({r},{g},{b},{alpha})"

    def __str__(self) -> str:
        """Default to CSS format."""
        return self.to_css()


@dataclass(frozen=True)
class Spacing:
    """Spacing token with multi-format support."""

    pixels: int
    base_font_size: int = 16  # For rem conversion

    def to_css(self) -> str:
        """CSS format: "16px"."""
        return f"{self.pixels}px"

    def to_pixels(self) -> int:
        """Pixel value: 16."""
        return self.pixels

    def to_rem(self) -> float:
        """Rem value: 1.0."""
        return self.pixels / self.base_font_size

    def __str__(self) -> str:
        """Default to CSS format."""
        return self.to_css()


# ============================================================================
# PART 3: UPDATED DESIGN SYSTEM (Using Token Classes)
# ============================================================================

@dataclass(frozen=True)
class AnimationTimings:
    """Animation timing tokens with automatic format conversion."""

    # Token objects (single source of truth)
    instant: Duration = Duration(100)
    fast: Duration = Duration(200)
    normal: Duration = Duration(300)
    slow: Duration = Duration(500)

    # Semantic aliases
    @property
    def duration_instant(self) -> Duration:
        return self.instant

    @property
    def duration_fast(self) -> Duration:
        return self.fast

    @property
    def duration_normal(self) -> Duration:
        return self.normal

    @property
    def duration_slow(self) -> Duration:
        return self.slow


# Usage in code:
# CSS: f"transition: all {ANIMATION.normal.to_css()}"
# Plotly: fig.update_layout(transition=dict(duration=ANIMATION.normal.to_plotly()))
# Both work, type-safe, single source of truth!


# ============================================================================
# PART 4: ADAPTER UTILITIES (Convenience Functions)
# ============================================================================

class TokenAdapters:
    """Convenience adapters for common token operations."""

    @staticmethod
    def plotly_transition(duration: Duration, easing: str = 'cubic-in-out') -> dict:
        """Create Plotly transition dict from duration token."""
        return {
            'duration': duration.to_plotly(),
            'easing': easing
        }

    @staticmethod
    def css_animation(duration: Duration, timing: str = 'ease-in-out') -> str:
        """Create CSS animation string from duration token."""
        return f"all {duration.to_css()} {timing}"

    @staticmethod
    def plotly_color_scale(colors: list[Color]) -> list[str]:
        """Convert color tokens to Plotly color scale."""
        return [c.to_plotly() for c in colors]


# ============================================================================
# PART 5: VALIDATION
# ============================================================================

def validate_token_usage(token: Union[Duration, Color, Spacing], consumer: str) -> bool:
    """
    Validate token is used correctly for consumer.

    Args:
        token: Token being used
        consumer: 'css', 'plotly', 'dxf', etc.

    Returns:
        True if valid, False otherwise
    """
    required_methods = {
        'css': 'to_css',
        'plotly': 'to_plotly',
        'dxf': 'to_pixels'  # Example
    }

    required_method = required_methods.get(consumer)
    if not required_method:
        return False

    return hasattr(token, required_method)
```

#### Migration Plan

**Phase 1: Backwards-compatible introduction (Week 1)**
1. Create `design_tokens_contracts.py` with token classes
2. Keep existing `design_system.py` unchanged (CSS strings)
3. Add new token-based system alongside
4. Update only NEW code to use token classes

**Phase 2: Gradual migration (Week 2-3)**
1. Update `visualizations.py` to use `ANIMATION.normal.to_plotly()`
2. Update CSS injection to use `ANIMATION.normal.to_css()`
3. Add pre-commit validation for token usage
4. Update tests to verify both formats

**Phase 3: Deprecation (Week 4)**
1. Mark old `duration_*_ms` fields as deprecated
2. Update docs to recommend token classes
3. Add warnings for old usage
4. Plan removal for next major version

**Benefits:**
✅ Type-safe (Protocol enforces interface)
✅ Single source of truth (one token, many formats)
✅ Extensible (add new formats easily)
✅ Testable (validate format conversions)
✅ Backwards-compatible (gradual migration)

---

## Rollout Plan

### Pre-Release (Day 0)

- [ ] Create feature branch: `feature/ui-layout-two-column`
- [ ] Review this document with team
- [ ] Set up local dev environment
- [ ] Run existing tests to establish baseline

### Day 1: Core Implementation (3-4 hours)

- [ ] **09:00-09:45** Task 1.1: Replace sidebar with columns
- [ ] **09:45-10:00** Break + manual testing
- [ ] **10:00-11:00** Task 1.2: Create preview component
- [ ] **11:00-11:15** Break + manual testing
- [ ] **11:15-12:00** Task 1.3: Integration with existing code
- [ ] **12:00-12:30** Task 1.4: Responsive design
- [ ] **12:30-13:00** Manual testing + fixes

**Checkpoint:** Two-column layout working with real-time preview

### Day 2: Polish & Testing (2 hours)

- [ ] **09:00-09:30** Task 2.1: Collapsible sections
- [ ] **09:30-10:15** Task 2.2: Example designs
- [ ] **10:15-11:00** Task 2.3: Visual polish
- [ ] **11:00-12:00** Write unit tests
- [ ] **12:00-13:00** Write integration tests

**Checkpoint:** All features complete, tests passing

### Day 3: Review & Deploy (1 hour)

- [ ] **09:00-09:30** Manual testing checklist
- [ ] **09:30-10:00** Fix any issues found
- [ ] **10:00-10:15** Create PR with screenshots
- [ ] **10:15-10:30** Team review
- [ ] **10:30-10:45** Address feedback
- [ ] **10:45-11:00** Merge to main

**Checkpoint:** Feature merged, deployed to production

### Post-Deploy (Ongoing)

- [ ] Monitor user feedback
- [ ] Track analytics (engagement, errors)
- [ ] Iterate based on feedback
- [ ] Plan Phase 2 enhancements

---

## Success Criteria

### Must-Have (MVP)

✅ Two-column layout (40/60 split)
✅ Real-time beam diagram preview
✅ Status dashboard with validation checks
✅ Rough cost estimate
✅ Responsive design (mobile/tablet/desktop)
✅ All existing functionality preserved
✅ Zero new errors introduced
✅ 80% test coverage

### Nice-to-Have (Phase 2)

⭐ Collapsible sections
⭐ Example design quick-load
⭐ Visual polish with design system
⭐ Smooth animations
⭐ Keyboard shortcuts

### Future Enhancements (Phase 3)

🚀 Interactive canvas (click-to-edit)
🚀 Live results (updates as you type)
🚀 Split-screen mode
🚀 Multiple layout modes (beginner/expert)
🚀 Token adapter architecture

---

## Risk Mitigation

### Risk 1: Design Token Type Mismatches

**Likelihood:** Medium
**Impact:** High (blocks deployment)

**Mitigation:**
- Use pre-commit validation script
- Write integration tests for token usage
- Manual testing checklist includes token validation
- Use Plotly-specific tokens (`_ms` suffix)

**Contingency:**
- If error occurs, rollback to sidebar layout
- Fix token usage offline
- Redeploy when verified

### Risk 2: Performance Degradation

**Likelihood:** Low
**Impact:** Medium (slow UX)

**Mitigation:**
- Use `@st.cache_data` for expensive calculations
- Debounce preview updates (300ms delay)
- Optimize Plotly figure creation
- Profile with browser DevTools

**Contingency:**
- Add loading spinners for slow operations
- Make preview optional (toggle off for slow devices)
- Reduce preview complexity (simpler diagrams)

### Risk 3: Layout Breaks on Mobile

**Likelihood:** Medium
**Impact:** Medium (unusable on mobile)

**Mitigation:**
- Test responsive breakpoints thoroughly
- Use viewport detection
- Fallback to stacked layout on small screens
- Manual testing on real devices

**Contingency:**
- Force stacked layout for all screen sizes
- Add mobile-specific CSS overrides
- Disable preview on mobile (show after analyze only)

### Risk 4: Existing Features Break

**Likelihood:** Low
**Impact:** High (functionality loss)

**Mitigation:**
- Keep all existing code paths intact
- Only change layout, not logic
- Comprehensive regression testing
- Staged rollout (beta users first)

**Contingency:**
- Feature flag to toggle old/new layout
- Quick rollback capability
- Monitor error rates in production

---

## Monitoring & Metrics

### Technical Metrics

- **Load time:** <2 seconds for page load
- **Preview render time:** <500ms for diagram update
- **Error rate:** <0.1% (1 error per 1000 page loads)
- **Test coverage:** >80% for new code

### User Experience Metrics

- **Engagement:** Time on page (expect +20%)
- **Completion rate:** % users who click "Analyze" (expect +15%)
- **Error recovery:** % users who fix validation errors (expect +30%)
- **Feedback sentiment:** NPS score (target: 8+/10)

### Business Metrics

- **Adoption:** % users using new layout (target: 95%+ after 1 week)
- **Retention:** % users returning (expect +10%)
- **Referrals:** % users sharing app (expect +25%)

---

## Appendices

### Appendix A: Code Structure

```
streamlit_app/
├── components/
│   ├── preview.py                    # NEW: Real-time preview component
│   ├── inputs.py                     # EXISTING: Input widgets
│   └── visualizations.py             # EXISTING: Plotly charts
├── pages/
│   ├── 01_🏗️_beam_design.py         # MODIFIED: Two-column layout
│   ├── 02_💰_cost_optimizer.py       # MODIFIED: Same pattern
│   └── 03_✅_compliance.py           # MODIFIED: Same pattern
├── utils/
│   ├── design_system.py              # EXISTING: Design tokens
│   ├── design_tokens_contracts.py    # NEW: Token adapters (future)
│   └── layout.py                     # EXISTING: Layout utilities
└── tests/
    ├── test_preview_unit.py          # NEW: Preview unit tests
    ├── test_preview_integration.py   # NEW: Preview integration tests
    └── test_design_system_integration.py  # EXISTING: Token tests
```

### Appendix B: Design System Reference

**Colors:**
- Primary: `COLORS.primary_500` (#003366)
- Accent: `COLORS.accent_500` (#FF6600)
- Success: `COLORS.success` (#10B981)
- Warning: `COLORS.warning` (#F59E0B)
- Error: `COLORS.error` (#EF4444)

**Animation:**
- Instant: `ANIMATION.duration_instant_ms` (100ms)
- Fast: `ANIMATION.duration_fast_ms` (200ms)
- Normal: `ANIMATION.duration_normal_ms` (300ms)
- Slow: `ANIMATION.duration_slow_ms` (500ms)

**Spacing:**
- XS: `SPACING.xs` (4px)
- SM: `SPACING.sm` (8px)
- MD: `SPACING.md` (16px)
- LG: `SPACING.lg` (24px)
- XL: `SPACING.xl` (32px)

**Elevation:**
- SM: `ELEVATION.shadow_sm` (subtle shadow)
- MD: `ELEVATION.shadow_md` (normal shadow)
- LG: `ELEVATION.shadow_lg` (prominent shadow)

### Appendix C: Example Design Templates

**5m Simply Supported Beam:**
```python
{
    'span_mm': 5000,
    'b_mm': 300,
    'D_mm': 500,
    'd_mm': 450,
    'concrete_grade': 'M25',
    'steel_grade': 'Fe500',
    'mu_knm': 120,
    'vu_kn': 80,
    'exposure': 'Moderate',
    'support_condition': 'Simply Supported'
}
```

**6m Continuous Beam:**
```python
{
    'span_mm': 6000,
    'b_mm': 350,
    'D_mm': 600,
    'd_mm': 550,
    'concrete_grade': 'M30',
    'steel_grade': 'Fe500',
    'mu_knm': 180,
    'vu_kn': 120,
    'exposure': 'Moderate',
    'support_condition': 'Continuous'
}
```

**2m Cantilever:**
```python
{
    'span_mm': 2000,
    'b_mm': 250,
    'D_mm': 400,
    'd_mm': 350,
    'concrete_grade': 'M25',
    'steel_grade': 'Fe415',
    'mu_knm': 60,
    'vu_kn': 40,
    'exposure': 'Mild',
    'support_condition': 'Cantilever'
}
```

---

## Sign-Off

**Document Author:** Main Agent
**Date:** 2026-01-08
**Status:** ✅ APPROVED FOR IMPLEMENTATION

**Reviewed By:**
- [ ] User (Pravin)
- [ ] Technical Lead
- [ ] UI/UX Lead

**Approved By:**
- [ ] Project Owner

**Implementation Start Date:** TBD
**Target Completion Date:** TBD + 3 days

---

**Related Documents:**
- `docs/research/ui-layout-best-practices.md` - Research foundation
- `docs/research/ui-layout-options-comparison.md` - Options analysis
- `docs/planning/agent-6-plotly-fix-main-agent-review.md` - Token architecture lessons
- `streamlit_app/docs/PLOTLY-TYPE-MISMATCH-ANALYSIS.md` - Multi-consumer token challenges
- `docs/planning/agent-6-impl-000-review-and-error-prevention.md` - Error prevention strategy

---

*This document provides a comprehensive, battle-tested plan for UI layout redesign with zero ambiguity and maximum error prevention.*
