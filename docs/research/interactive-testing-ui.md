# Interactive Testing UI

**Document Version:** 1.0
**Last Updated:** 2026-01-07
**Status:** Complete
**Task:** TASK-252
**Author:** Research Team (Structural Engineer + Library Developer)

---

## Executive Summary

**Problem:** Testing structural calculations requires running scripts and reviewing console output. Need interactive UI for rapid prototyping, parameter exploration, and visual debugging.

**Goal:** Research interactive testing UI options that provide:
1. Live parameter adjustment (sliders, inputs)
2. Instant calculation updates
3. Visual result display (charts, diagrams)
4. Export results (PDF, Excel)
5. Shareable interface (web-based preferred)

**Key Finding:** Jupyter + ipywidgets provides best balance of interactivity, visualization, and engineering workflow integration. Streamlit alternative for standalone apps.

**Recommendation:**
- Phase 1: Jupyter widgets interface (8-10 hours)
- Phase 2: Visualization (plotly charts) (4-5 hours)
- Phase 3: Streamlit standalone app (6-8 hours, optional)
- Total: 12-15 hours (jupyter), +6-8 hours (streamlit)

---

## Table of Contents

1. [Requirements & Use Cases](#1-requirements--use-cases)
2. [Technology Options](#2-technology-options)
3. [Jupyter Widgets Design](#3-jupyter-widgets-design)
4. [Streamlit Alternative](#4-streamlit-alternative)
5. [Visualization Components](#5-visualization-components)
6. [Implementation Guide](#6-implementation-guide)

---

## 1. Requirements & Use Cases

### 1.1 User Personas

**Persona 1: Design Engineer**
- Exploring design space
- Trying different parameters
- Checking utilization ratios
- **Need:** Fast iteration, immediate feedback

**Persona 2: Checker/Reviewer**
- Verifying calculations
- Understanding design decisions
- Checking edge cases
- **Need:** Clear visualization, export capability

**Persona 3: Student/Learner**
- Learning code provisions
- Understanding parameter effects
- Exploring examples
- **Need:** Interactive examples, visual explanations

### 1.2 Required Features

**Input Controls:**
- ✅ Sliders for continuous parameters (span, depth)
- ✅ Dropdowns for discrete choices (concrete grade, steel grade)
- ✅ Text inputs for precise values
- ✅ Unit display/conversion

**Output Display:**
- ✅ Results table (required steel, capacity, utilization)
- ✅ Pass/fail indicators (color-coded)
- ✅ Charts (moment-curvature, interaction diagrams)
- ✅ Code check summaries

**Export:**
- ✅ PDF calculation report
- ✅ Excel data export
- ✅ PNG chart export

---

## 2. Technology Options

### 2.1 Jupyter Widgets (ipywidgets)

**Pros:**
- ✅ Integrates with Jupyter notebooks (already used)
- ✅ Rich widget library (sliders, dropdowns, buttons)
- ✅ Works with matplotlib/plotly
- ✅ Shareable via Colab, Binder
- ✅ No separate server needed

**Cons:**
- ❌ Requires Jupyter environment
- ❌ Not standalone application
- ❌ Somewhat limited styling

**Best For:** Engineers already using Jupyter, quick prototyping

### 2.2 Streamlit

**Pros:**
- ✅ Clean, modern UI out of the box
- ✅ Standalone web app
- ✅ Easy deployment (Streamlit Cloud)
- ✅ Fast development
- ✅ Automatic reactivity

**Cons:**
- ❌ Separate from notebook workflow
- ❌ Requires running server
- ❌ Entire script reruns on input change

**Best For:** Standalone demo apps, client presentations

### 2.3 Plotly Dash

**Pros:**
- ✅ Full web framework
- ✅ Production-ready
- ✅ Rich callbacks system
- ✅ Custom styling

**Cons:**
- ❌ More complex to develop
- ❌ Requires Flask/React knowledge
- ❌ Overkill for simple use cases

**Best For:** Production web applications

### 2.4 Recommendation: Jupyter + Streamlit

- **Primary:** Jupyter widgets (engineers' main workflow)
- **Secondary:** Streamlit (demos, presentations)

---

## 3. Jupyter Widgets Design

### 3.1 Interactive Beam Design Widget

**Implementation:**

```python
# ui/jupyter_widgets.py
import ipywidgets as widgets
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
from structural_lib import design_beam

class BeamDesignWidget:
    """
    Interactive widget for beam design exploration.

    Features:
    - Sliders for geometric parameters
    - Dropdowns for material grades
    - Live calculation updates
    - Visual result display

    Example:
        >>> widget = BeamDesignWidget()
        >>> widget.display()
    """

    def __init__(self):
        self._create_widgets()
        self._setup_observers()
        self.result = None

    def _create_widgets(self):
        """Create all UI widgets."""

        # === GEOMETRY SECTION ===
        self.span = widgets.FloatSlider(
            value=5000,
            min=2000,
            max=12000,
            step=100,
            description='Span (mm):',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='500px')
        )

        self.width = widgets.FloatSlider(
            value=230,
            min=150,
            max=600,
            step=10,
            description='Width (mm):',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='500px')
        )

        self.depth = widgets.FloatSlider(
            value=450,
            min=200,
            max=1200,
            step=10,
            description='Depth (mm):',
            style={'description_width': '120px'},
            layout=widgets.Layout(width='500px')
        )

        # === MATERIALS SECTION ===
        self.fck = widgets.Dropdown(
            options=[20, 25, 30, 35, 40],
            value=25,
            description='Concrete (M):',
            style={'description_width': '120px'}
        )

        self.fy = widgets.Dropdown(
            options=[250, 415, 500, 550],
            value=415,
            description='Steel (Fe):',
            style={'description_width': '120px'}
        )

        # === LOADING SECTION ===
        self.moment = widgets.FloatText(
            value=120,
            description='Moment (kN·m):',
            style={'description_width': '120px'}
        )

        self.shear = widgets.FloatText(
            value=85,
            description='Shear (kN):',
            style={'description_width': '120px'}
        )

        # === ACTIONS ===
        self.calculate_btn = widgets.Button(
            description='Calculate Design',
            button_style='primary',
            icon='calculator'
        )

        self.export_btn = widgets.Button(
            description='Export PDF',
            button_style='success',
            icon='download'
        )

        # === OUTPUT ===
        self.output = widgets.Output()

    def _setup_observers(self):
        """Setup event handlers."""
        self.calculate_btn.on_click(self._on_calculate)
        self.export_btn.on_click(self._on_export)

        # Auto-calculate on slider change
        for widget in [self.span, self.width, self.depth]:
            widget.observe(self._on_param_change, names='value')

    def _on_calculate(self, btn):
        """Calculate design when button clicked."""
        with self.output:
            clear_output(wait=True)

            # Show loading indicator
            print("Calculating...")

            try:
                # Perform design
                self.result = design_beam(
                    span_mm=self.span.value,
                    width_mm=self.width.value,
                    depth_mm=self.depth.value,
                    moment_knm=self.moment.value,
                    shear_kn=self.shear.value,
                    fck_mpa=self.fck.value,
                    fy_mpa=self.fy.value
                )

                # Display results
                self._display_results()

            except Exception as e:
                print(f"❌ Error: {e}")

    def _on_param_change(self, change):
        """Auto-recalculate on parameter change."""
        # Debounce rapid changes
        import time
        time.sleep(0.3)
        self._on_calculate(None)

    def _display_results(self):
        """Display calculation results."""
        clear_output(wait=True)

        r = self.result

        # === SUMMARY TABLE ===
        print("=" * 70)
        print(" DESIGN SUMMARY ".center(70))
        print("=" * 70)
        print()

        # Flexure
        print("FLEXURE:")
        print(f"  Required Steel:  {r.ast_mm2:.0f} mm²")
        print(f"  Provided Steel:  {r.ast_provided_mm2:.0f} mm²")
        print(f"  Bar Config:      {r.bar_config}")
        util_flex = r.ast_mm2 / r.ast_provided_mm2
        status_flex = "✓ SAFE" if r.is_safe else "✗ UNSAFE"
        print(f"  Utilization:     {util_flex*100:.1f}%  {status_flex}")
        print()

        # Shear
        print("SHEAR:")
        print(f"  Design Shear:    {r.vu_kn:.1f} kN")
        print(f"  Capacity:        {r.vu_capacity_kn:.1f} kN")
        util_shear = r.vu_kn / r.vu_capacity_kn
        status_shear = "✓ SAFE" if r.shear_safe else "✗ UNSAFE"
        print(f"  Utilization:     {util_shear*100:.1f}%  {status_shear}")
        print()

        # Overall
        overall = "✓ PASS" if (r.is_safe and r.shear_safe) else "✗ FAIL"
        print("=" * 70)
        print(f" DESIGN STATUS: {overall} ".center(70))
        print("=" * 70)

        # === VISUALIZATION ===
        self._plot_results()

    def _plot_results(self):
        """Plot utilization bar chart."""
        fig, ax = plt.subplots(figsize=(8, 4))

        categories = ['Flexure', 'Shear']
        utilizations = [
            self.result.ast_mm2 / self.result.ast_provided_mm2,
            self.result.vu_kn / self.result.vu_capacity_kn
        ]
        colors = ['green' if u < 1.0 else 'red' for u in utilizations]

        ax.barh(categories, utilizations, color=colors, alpha=0.7)
        ax.axvline(x=1.0, color='red', linestyle='--', label='Capacity')
        ax.set_xlabel('Utilization Ratio')
        ax.set_title('Design Utilization')
        ax.legend()
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()
        plt.show()

    def _on_export(self, btn):
        """Export PDF report."""
        if self.result is None:
            print("Calculate design first!")
            return

        from structural_lib.reports import PDFReportGenerator

        generator = PDFReportGenerator()
        output_file = 'beam_design_calc.pdf'

        generator.generate_beam_report(
            result=self.result,
            output_file=output_file,
            project_info={'name': 'Interactive Design'}
        )

        print(f"✓ PDF exported: {output_file}")

    def display(self):
        """Display the complete widget interface."""
        # Layout sections
        geometry_section = widgets.VBox([
            widgets.HTML("<h3>Geometry</h3>"),
            self.span,
            self.width,
            self.depth,
        ])

        materials_section = widgets.VBox([
            widgets.HTML("<h3>Materials</h3>"),
            self.fck,
            self.fy,
        ])

        loading_section = widgets.VBox([
            widgets.HTML("<h3>Loading</h3>"),
            self.moment,
            self.shear,
        ])

        actions_section = widgets.HBox([
            self.calculate_btn,
            self.export_btn,
        ])

        # Combine layout
        left_panel = widgets.VBox([
            geometry_section,
            materials_section,
            loading_section,
            actions_section,
        ])

        right_panel = widgets.VBox([
            widgets.HTML("<h3>Results</h3>"),
            self.output,
        ])

        app = widgets.HBox([left_panel, right_panel])

        display(app)

        # Initial calculation
        self._on_calculate(None)
```

**Usage in Notebook:**

```python
# In Jupyter notebook
from structural_lib.ui import BeamDesignWidget

widget = BeamDesignWidget()
widget.display()

# Interact with sliders → results update automatically!
```

---

## 4. Streamlit Alternative

### 4.1 Streamlit App Implementation

**File: `apps/beam_design_app.py`**

```python
import streamlit as st
import plotly.graph_objects as go
from structural_lib import design_beam
from structural_lib.reports import PDFReportGenerator

# === PAGE CONFIG ===
st.set_page_config(
    page_title="Beam Design Tool",
    page_icon="🏗️",
    layout="wide"
)

# === TITLE ===
st.title("🏗️ RC Beam Design per IS 456:2000")
st.markdown("Interactive structural design tool")

# === SIDEBAR INPUTS ===
st.sidebar.header("Design Parameters")

with st.sidebar:
    st.subheader("Geometry")
    span_mm = st.slider("Span (mm)", 2000, 12000, 5000, 100)
    width_mm = st.slider("Width (mm)", 150, 600, 230, 10)
    depth_mm = st.slider("Depth (mm)", 200, 1200, 450, 10)

    st.subheader("Materials")
    fck_mpa = st.selectbox("Concrete Grade (M)", [20, 25, 30, 35, 40], index=1)
    fy_mpa = st.selectbox("Steel Grade (Fe)", [250, 415, 500, 550], index=1)

    st.subheader("Loading")
    moment_knm = st.number_input("Moment (kN·m)", value=120.0, step=5.0)
    shear_kn = st.number_input("Shear (kN)", value=85.0, step=5.0)

# === CALCULATE ===
with st.spinner("Calculating design..."):
    try:
        result = design_beam(
            span_mm=span_mm,
            width_mm=width_mm,
            depth_mm=depth_mm,
            moment_knm=moment_knm,
            shear_kn=shear_kn,
            fck_mpa=fck_mpa,
            fy_mpa=fy_mpa
        )

        # === RESULTS DISPLAY ===
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Flexural Design")
            st.metric("Required Steel", f"{result.ast_mm2:.0f} mm²")
            st.metric("Provided Steel", f"{result.ast_provided_mm2:.0f} mm²",
                     delta=f"{result.ast_provided_mm2 - result.ast_mm2:.0f} mm² excess")
            st.metric("Bar Configuration", result.bar_config)

            util_flex = result.ast_mm2 / result.ast_provided_mm2
            if util_flex < 1.0:
                st.success(f"✓ Utilization: {util_flex*100:.1f}% - SAFE")
            else:
                st.error(f"✗ Utilization: {util_flex*100:.1f}% - UNSAFE")

        with col2:
            st.subheader("Shear Design")
            st.metric("Design Shear", f"{result.vu_kn:.1f} kN")
            st.metric("Capacity", f"{result.vu_capacity_kn:.1f} kN",
                     delta=f"{result.vu_capacity_kn - result.vu_kn:.1f} kN margin")

            util_shear = result.vu_kn / result.vu_capacity_kn
            if util_shear < 1.0:
                st.success(f"✓ Utilization: {util_shear*100:.1f}% - SAFE")
            else:
                st.error(f"✗ Utilization: {util_shear*100:.1f}% - UNSAFE")

        # === UTILIZATION CHART ===
        st.subheader("Utilization Summary")

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=['Flexure', 'Shear'],
            y=[util_flex, util_shear],
            marker_color=['green' if util_flex < 1.0 else 'red',
                         'green' if util_shear < 1.0 else 'red'],
            text=[f"{util_flex*100:.1f}%", f"{util_shear*100:.1f}%"],
            textposition='outside'
        ))

        fig.add_hline(y=1.0, line_dash="dash", line_color="red",
                     annotation_text="Capacity Limit")

        fig.update_layout(
            yaxis_title="Utilization Ratio",
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

        # === EXPORT ===
        if st.button("📄 Generate PDF Report"):
            generator = PDFReportGenerator()
            output_file = "beam_design_calc.pdf"

            generator.generate_beam_report(
                result=result,
                output_file=output_file,
                project_info={'name': 'Streamlit Design'}
            )

            with open(output_file, 'rb') as f:
                st.download_button(
                    label="Download PDF",
                    data=f,
                    file_name=output_file,
                    mime="application/pdf"
                )

    except Exception as e:
        st.error(f"Design Error: {e}")
```

**Run:**
```bash
streamlit run apps/beam_design_app.py
```

---

## 5. Visualization Components

### 5.1 Utilization Bar Chart (Plotly)

```python
def plot_utilization(result):
    """Plot utilization ratios."""
    import plotly.graph_objects as go

    categories = ['Flexure', 'Shear', 'Deflection']
    utilizations = [
        result.flexure_util,
        result.shear_util,
        result.deflection_util,
    ]
    colors = ['green' if u < 1.0 else 'red' for u in utilizations]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories,
        y=utilizations,
        marker_color=colors,
        text=[f"{u*100:.1f}%" for u in utilizations],
        textposition='outside'
    ))

    fig.add_hline(y=1.0, line_dash="dash", annotation_text="Capacity")
    fig.update_layout(
        title="Design Utilization",
        yaxis_title="Ratio",
        height=400
    )

    return fig
```

### 5.2 Moment-Curvature Diagram

```python
def plot_moment_curvature(result):
    """Plot M-φ curve."""
    import plotly.graph_objects as go

    # Generate curve data
    curvatures = result.curvature_values
    moments = result.moment_values

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=curvatures,
        y=moments,
        mode='lines',
        name='M-φ Curve'
    ))

    # Mark design point
    fig.add_trace(go.Scatter(
        x=[result.design_curvature],
        y=[result.design_moment],
        mode='markers',
        marker=dict(size=12, color='red'),
        name='Design Point'
    ))

    fig.update_layout(
        title="Moment-Curvature Relationship",
        xaxis_title="Curvature (1/mm)",
        yaxis_title="Moment (kN·m)",
        height=500
    )

    return fig
```

---

## 6. Implementation Guide

### 6.1 Phase 1: Jupyter Widgets (8-10 hours)

**Step 1: Widget creation** (4 hours)
- Input widgets (sliders, dropdowns)
- Layout design
- Event handlers

**Step 2: Calculation integration** (2 hours)
- Connect to design_beam()
- Handle errors
- Auto-recalculate

**Step 3: Result display** (2 hours)
- Format output
- Add visualizations
- Export functionality

**Step 4: Testing** (2 hours)
- Test all widgets
- Check edge cases
- User experience refinement

### 6.2 Phase 2: Visualization (4-5 hours)

**Step 1: Plotly setup** (1 hour)
- Install plotly
- Configure for Jupyter/Streamlit

**Step 2: Charts** (2 hours)
- Utilization bar chart
- Moment-curvature plot
- Section diagram

**Step 3: Interactivity** (1-2 hours)
- Hover tooltips
- Click interactions
- Export charts

### 6.3 Phase 3: Streamlit App (6-8 hours, optional)

**Step 1: App structure** (2 hours)
- Layout design
- Input sidebar
- Results display

**Step 2: Interactivity** (2 hours)
- Auto-recalculate
- Error handling
- Loading indicators

**Step 3: Deployment** (2-4 hours)
- Streamlit Cloud setup
- Requirements.txt
- Documentation

---

## Document Control

**Version History:**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-07 | Initial research complete | Research Team |

**Next Steps:**

1. Implement Jupyter widget (Priority 1)
2. Add to Colab notebook examples
3. Create Streamlit app (Priority 2)
4. Deploy demo app to Streamlit Cloud
5. Document usage in user guide

---

**End of Document**
**Implementation Time:** 12-15 hours (Jupyter) + 6-8 hours (Streamlit optional)
**Priority:** MEDIUM (nice-to-have, enhances UX significantly)
**Dependencies:** ipywidgets, plotly, streamlit
