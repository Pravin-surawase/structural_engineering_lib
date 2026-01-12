# API CAPABILITY ANALYSIS — What We Can Do

**Type:** Research
**Status:** Current State Analysis
**Created:** 2026-01-13
**Archive After:** 2026-01-27 (if needed)

---

## 📦 WHAT YOUR LIBRARY ALREADY HAS (THE GOLD MINE)

Based on review of `/Python/structural_lib/api.py`, `/costing.py`, `/optimization.py`:

### TIER 1: Core Design Functions (100% Ready)

**✅ design_beam_is456()**
- Flexure analysis (calculate required steel)
- Shear analysis (calculate stirrups)
- Ductility checks
- Deflection checks
- **Returns:** Full design object with all results

**✅ check_beam_is456()**
- Validation against IS 456 rules
- Compliance report
- Warnings/errors if design fails

**✅ detail_beam_is456()**
- Rebar detailing per IS 13920 (ductile design)
- Development length calculations
- Lap length calculations
- Spacing checks

**✅ design_and_detail_beam_is456()**
- One-shot function: design + check + detail
- **Perfect for batch processing 1000 designs**

---

### TIER 2: Cost Analysis (80% Ready)

**✅ CostProfile class**
- Regional cost data (CPWD DSR 2023)
- Concrete costs by grade (M20-M40)
- Steel costs (per kg)
- Formwork costs
- Location factors
- **Customizable for regional variation**

**✅ Cost calculation functions**
- `calculate_concrete_volume()` — m³
- `calculate_steel_weight()` — kg
- `calculate_formwork_area()` — m²
- `calculate_beam_cost()` — full cost breakdown (concrete + steel + formwork + labor)

**✅ CostBreakdown dataclass**
- Detailed cost breakdown (steel | concrete | formwork | labor)
- Currency support
- Easy serialization to dict

**📊 What you get per design:**
```
{
  "concrete_cost": 4500,      # ₹
  "steel_cost": 3200,         # ₹
  "formwork_cost": 800,       # ₹
  "labor_adjustment": 400,    # ₹
  "total_cost": 8900,         # ₹
}
```

---

### TIER 3: Optimization (Partially Ready)

**✅ optimize_beam_cost()**
- Brute-force search for cheapest design
- Intelligent pruning
- Returns top 3 alternatives
- **Limited search space:** ~30-50 combinations
- **Current grades:** M25, M30 only
- **Current widths:** 230, 300, 400 mm
- **Current steel:** Fe500 only

**⚠️ Limitation noted in code:**
```python
# NOTE: Limited search space for v1.0 (most common grades/steel)
# Future enhancement: Add M20, M35, Fe415 for comprehensive optimization
# Current: ~30-50 combinations, Full spec: ~300-500 combinations
```

**📌 Implication for Pareto:** This tells us we can easily EXTEND this to cover more combinations!

---

### TIER 4: Reporting & Export (Ready)

**✅ compute_bbs()** — Bar Bending Schedule
- Rebar scheduling
- Diameter, count, length, weight

**✅ compute_dxf()** — DXF export
- Drawing generation
- Ready for CAD

**✅ compute_report()** — PDF calculation report
- Full technical report
- Stamps, signatures, audit trail

**✅ CalculationReport class**
- ProjectInfo section
- InputSection (loads, geometry, materials)
- ResultSection (design results)
- Audit trail for compliance

---

## 🎯 WHAT WE NEED FOR PARETO (5-MINUTE ASSESSMENT)

### What We Have ✅

| Component | Status | Notes |
|-----------|--------|-------|
| Fast beam design (`design_and_detail_beam_is456`) | ✅ Ready | Can process 1000s in minutes |
| Cost calculation | ✅ Ready | Every design gets cost breakdown |
| IS 456 validation | ✅ Ready | Every design checked for compliance |
| Costing module extensible | ✅ Ready | Can add carbon footprint tracking |
| Result serialization | ✅ Ready | Easy to export to CSV/JSON |

### What We Need to Build 🔨

| Component | Effort | Notes |
|-----------|--------|-------|
| **Batch design generator** | Low | Loop 1000 designs, collect results |
| **Pareto frontier filter** | Low | Algorithm to find non-dominated designs |
| **Carbon footprint module** | Low | Add emission factors to `CostProfile` |
| **Weight calculation** | Very Low | Already in `costing.py` |
| **Interactive visualization** | Medium | Plotly/Streamlit UI |
| **Design space sampler** | Low | Latin Hypercube or factorial sampling |

---

## 🔧 SPECIFIC FUNCTIONS YOU'LL USE (In Order)

### Step 1: Generate Design Space (Sampling)

```python
# What you'll call:
from structural_lib.api import design_and_detail_beam_is456

# For each of 1000 designs:
result = design_and_detail_beam_is456(
    span_mm=5000,
    mu_knm=120,
    vu_kn=80,
    b_mm=300,
    D_mm=500,
    d_mm=450,
    fck_nmm2=25,
    fy_nmm2=500,
    cover_mm=40,
)

# You get: FlexureResult + ShearResult + DetailingResult + All checks
```

### Step 2: Calculate Cost

```python
from structural_lib.api import CostProfile, CostBreakdown
from structural_lib.costing import calculate_beam_cost

profile = CostProfile()  # India default

cost = calculate_beam_cost(
    b_mm=300,
    D_mm=500,
    span_mm=5000,
    ast_mm2=result.ast_required,  # From step 1
    fck_nmm2=25,
    steel_percentage=result.steel_percentage,
    cost_profile=profile,
)

# You get: CostBreakdown(concrete=X, steel=Y, formwork=Z, total=TOTAL)
```

### Step 3: Calculate Weight

```python
from structural_lib.costing import calculate_steel_weight, calculate_concrete_volume

steel_weight = calculate_steel_weight(ast_mm2, span_mm)  # kg
concrete_volume = calculate_concrete_volume(b_mm, D_mm, span_mm)  # m³
total_weight = concrete_volume * 2400 + steel_weight  # kg (approx)
```

### Step 4: Filter Pareto Frontier

```python
# Simple Python:
def pareto_frontier(designs):
    """Keep only non-dominated designs."""
    frontier = []
    for d1 in designs:
        dominated = False
        for d2 in designs:
            if d1 != d2:
                # d2 is better if lower cost AND lower weight
                if d2.cost < d1.cost and d2.weight < d1.weight:
                    dominated = True
                    break
        if not dominated:
            frontier.append(d1)
    return frontier
```

### Step 5: Visualize

```python
import plotly.express as px
import pandas as pd

df = pd.DataFrame(designs)

fig = px.scatter(
    df,
    x='cost',
    y='weight',
    color='depth_mm',
    size='carbon_kg',
    hover_data=['ast_required', 'fck_nmm2'],
    title='Pareto Frontier: Cost vs Weight',
)

# Highlight Pareto frontier
frontier_df = pd.DataFrame(frontier)
fig.add_scatter(
    x=frontier_df['cost'],
    y=frontier_df['weight'],
    mode='lines+markers',
    name='Pareto Frontier',
    line=dict(color='red', width=2),
)

fig.show()
```

---

## 📊 DATA YOU'LL COLLECT PER DESIGN

**Output schema (for CSV/database):**

```
design_id,span_mm,load_knm,b_mm,D_mm,d_mm,fck_nmm2,fy_nmm2,
ast_required,ast_min,ast_max,
asv_required,stirrup_spacing,
deflection_mm,deflection_ok,
ductility_mu_lim,ductility_ok,
concrete_vol_m3,steel_weight_kg,total_weight_kg,
concrete_cost,steel_cost,formwork_cost,labor_cost,total_cost_inr,
carbon_kg,
is_valid,failure_reason
```

**Example row:**
```
D001,5000,120,300,500,450,25,500,
1200,900,1500,
150,150,
20,PASS,
80.5,PASS,
0.75,5.9,1800,
4050,400,400,150,5000,
1.2,
TRUE,""
```

---

## 🎯 WHAT'S MISSING (THE GAPS)

### Gap 1: Carbon Footprint

**Current:** No carbon tracking in library
**Need:** Add to `CostProfile`
```python
@dataclass
class CostProfile:
    # ... existing fields ...

    # Carbon emissions (kg CO2 per unit)
    concrete_carbon_per_m3: dict[int, float] = field(
        default_factory=lambda: {
            20: 300,  # kg CO2/m³ (M20 concrete)
            25: 320,  # kg CO2/m³ (M25 concrete)
            # Higher grades need more cement
        }
    )
    steel_carbon_per_kg: float = 2.1  # kg CO2/kg (Fe500)
    formwork_carbon_per_m2: float = 15  # kg CO2/m² (amortized)
```

**Effort:** 1-2 hours
**Impact:** Opens up sustainability angle for paper

### Gap 2: Density/Weight Calculation

**Current:** In `costing.py` but not exposed in API
**Need:** Either expose function or add to API
**Effort:** <30 minutes
**Impact:** Critical for weight trade-off visualization

### Gap 3: Batch Processing Helper

**Current:** API functions are single-design focused
**Need:** Batch wrapper that handles 1000 designs
```python
def design_batch(designs: list[dict]) -> list[dict]:
    """Design multiple beams in parallel."""
    # Use multiprocessing to speed up
    # Return list of design results
```

**Effort:** 2-3 hours
**Impact:** 5-10x speedup for generating 1000 designs

### Gap 4: Extended Search Space

**Current:** Limited to M25, M30, Fe500, 230/300/400mm widths
**Need:** Expand to M20, M35, M40, Fe415, wider range of widths
**Effort:** 2-3 hours (just add options)
**Impact:** More comprehensive Pareto frontier

---

## 🚀 THE IMPLEMENTATION PATH (Detailed)

### Phase 1: Prepare API Extensions (2-3 hours)

```python
# File: Python/structural_lib/carbon.py (NEW)

@dataclass
class CarbonProfile:
    """Carbon emission factors."""
    concrete_per_m3: dict[int, float] = field(
        default_factory=lambda: {
            20: 300,
            25: 320,
            30: 340,
            40: 380,
        }
    )
    steel_per_kg: float = 2.1
    formwork_per_m2: float = 15

def calculate_beam_carbon(
    b_mm, D_mm, span_mm, ast_mm2, fck_nmm2,
    carbon_profile: CarbonProfile
) -> float:
    """Total carbon footprint in kg CO2."""
    vol = calculate_concrete_volume(b_mm, D_mm, span_mm)
    carbon_concrete = vol * carbon_profile.concrete_per_m3[fck_nmm2]

    weight_steel = calculate_steel_weight(ast_mm2, span_mm)
    carbon_steel = weight_steel * carbon_profile.steel_per_kg

    area_formwork = calculate_formwork_area(b_mm, D_mm, span_mm)
    carbon_formwork = area_formwork * carbon_profile.formwork_per_m2

    return carbon_concrete + carbon_steel + carbon_formwork
```

### Phase 2: Batch Generator (2-4 hours)

```python
# File: Python/structural_lib/batch_optimizer.py (NEW)

def generate_design_space(
    spans_mm: list[float],
    loads_knm: list[float],
    grades_fck: list[int],
    widths_mm: list[int],
    depths_mm: list[int],
    steels_fy: list[int],
) -> pd.DataFrame:
    """Generate all feasible combinations and design them."""

    designs = []
    count = 0

    for span in spans_mm:
        for load in loads_knm:
            for grade in grades_fck:
                for width in widths_mm:
                    for depth_range in depths_mm:
                        depth_min = max(300, span // 20)
                        depth_max = min(900, span // 8)
                        for depth in range(depth_min, depth_max+1, 50):
                            for steel in steels_fy:
                                result = design_and_detail_beam_is456(...)
                                design_record = {
                                    'span': span,
                                    'load': load,
                                    'grade': grade,
                                    'b_mm': width,
                                    'D_mm': depth,
                                    'ast_required': result.ast_required,
                                    'cost': calculate_beam_cost(...),
                                    'weight': calculate_weight(...),
                                    'carbon': calculate_beam_carbon(...),
                                    'is_valid': result.design_adequate,
                                }
                                designs.append(design_record)
                                count += 1

    return pd.DataFrame(designs)
```

### Phase 3: Pareto Filtering (1 hour)

```python
# File: Python/structural_lib/pareto.py (NEW)

def extract_pareto_frontier(
    designs_df: pd.DataFrame,
    objectives: list[str],  # ['cost', 'weight']
    minimize: bool = True,  # minimize cost, minimize weight
) -> pd.DataFrame:
    """Extract non-dominated designs (Pareto frontier)."""

    frontier = []

    for idx, d1 in designs_df.iterrows():
        dominated = False

        for jdx, d2 in designs_df.iterrows():
            if idx != jdx:
                # Check if d2 dominates d1
                all_better = True
                for obj in objectives:
                    if minimize:
                        if d2[obj] >= d1[obj]:
                            all_better = False
                            break
                    else:
                        if d2[obj] <= d1[obj]:
                            all_better = False
                            break

                if all_better:
                    dominated = True
                    break

        if not dominated:
            frontier.append(idx)

    return designs_df.loc[frontier]
```

### Phase 4: Visualization (3-5 hours)

```python
# File: Python/streamlit_app/pages/pareto_explorer.py (NEW)

import streamlit as st
import plotly.express as px

st.title("Pareto Optimizer: RC Beam Design")

# Inputs
span = st.slider("Span (mm)", 3000, 15000, 5000)
load = st.slider("Load (kN/m)", 10, 100, 40)
grade = st.selectbox("Concrete Grade", ["M20", "M25", "M30", "M40"])

if st.button("Generate Pareto Frontier"):
    # Generate designs
    designs = generate_design_space(
        spans_mm=[span],
        loads_knm=[load],
        grades_fck=[int(grade[1:])],
        ...
    )

    # Extract frontier
    frontier = extract_pareto_frontier(
        designs,
        objectives=['cost', 'weight'],
    )

    # Visualize
    fig = px.scatter(
        designs,
        x='cost',
        y='weight',
        color='depth',
        title=f'Pareto Frontier: {span}mm span, {load}kN/m',
    )

    # Highlight frontier
    fig.add_scatter(
        x=frontier['cost'],
        y=frontier['weight'],
        mode='lines+markers',
        name='Pareto Frontier',
    )

    st.plotly_chart(fig, use_container_width=True)

    # Details
    if st.checkbox("Show design details"):
        st.dataframe(frontier)
```

---

## 📈 EXPECTED PERFORMANCE

**With your library:**

| Task | Time | Notes |
|------|------|-------|
| Design 1 beam | ~50-100ms | `design_and_detail_beam_is456()` |
| Design 100 beams | ~5-10s | Sequential |
| Design 1000 beams | ~1-2 min | Sequential |
| Design 1000 beams (parallel) | ~15-30s | Using multiprocessing (8 cores) |
| Pareto filtering | <1s | All objective functions are fast |
| Visualization (plot) | <1s | Plotly is very fast |

**Total time for full Pareto run:** ~30-60 seconds (acceptable)

---

## 🎯 SUMMARY: WHAT YOU HAVE VS WHAT YOU NEED

### ✅ You Already Have (Don't Need to Build)
- Core design engine (flexure, shear, detailing)
- Cost calculation module
- IS 456 validation
- Result serialization
- PDF report generation

### 🔨 You Need to Build (Moderate Effort)
- Carbon emission tracking (~1-2h)
- Batch processing helper (~2-3h)
- Pareto filtering algorithm (~1h)
- Interactive visualization (~3-5h)
- Extended design space options (~2h)

**Total new code:** ~10-15 hours

### 🎊 The Wow Visualizations (Then Build These)
- Scatter plot with Pareto frontier
- Click-to-see-details modal
- Cost breakdown pie chart
- Interactive filters by span/load/grade
- Comparison tables

---

## 🚀 YOU'RE READY TO START BUILDING

Your library is 80% complete for this project. The remaining 20% is glue code (batch processing, visualization, carbon tracking).

**Next:** Build the implementation plan with specific code structure.

