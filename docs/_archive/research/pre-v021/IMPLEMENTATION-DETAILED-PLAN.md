# Implementation Task Plan - Pareto Optimization MVP

**Status:** Ready to Start
**Target:** 4 weeks
**Priority:** Phase 2 (Brute Force MVP)

---

## Why This Order?

We're following a principle: **Build the simplest thing that works first.**

1. **Validator** = foundation (must work perfectly)
2. **Cost Calculator** = objective function (must be accurate)
3. **Brute Force** = 80% of value with 20% of effort
4. **NSGA-II** = nice-to-have for later

---

## TASK GROUP 1: Foundation (Week 1)

### TASK-001: Refactor is456_validator.py

**What:**
Currently: Throws exceptions (messy)
Needed: Returns structured data {valid: bool, failures: list, utilization: float}

**Code Change:**
```python
# Current (BAD)
def check_deflection(span, deflection):
    if deflection > span/250:
        raise DeflectionError("Exceeds limit")

# New (GOOD)
def validate_deflection(span, deflection):
    limit = span / 250
    ratio = deflection / limit
    return {
        'check': 'Deflection',
        'status': 'PASS' if ratio <= 1.0 else 'FAIL',
        'limit': limit,
        'actual': deflection,
        'utilization': ratio,
        'clause': 'IS 456 Cl. 23.2'
    }
```

**Acceptance Criteria:**
- All 8 IS 456 checks return dicts (not exceptions)
- Each dict has: check, status, limit, actual, utilization, clause
- Existing tests still pass

**Estimated Time:** 4 hours

---

### TASK-002: Create Cost Calculator

**What:**
Given a beam design, calculate total cost.

**Logic:**
```
Cost = Material Cost + Labor Cost

Material Cost = (Concrete Volume × Rate/m³) + (Steel Weight × Rate/kg)

Where:
  Concrete Volume = width × depth × length (in m³)
  Steel Weight = (Ast + Asv) × length × density (in kg)

Labor Cost = (Cost per m³ concrete) × volume
```

**Code Template:**
```python
def calculate_cost(design, rates):
    """
    design = {width, depth, bars_main, bars_shear, dia_main, dia_shear}
    rates = {concrete_rate: 300/m³, steel_rate: 80/kg, labor_rate: 50/m³}

    Returns: cost in INR
    """
    # 1. Calculate volumes
    concrete_vol = (design['width']/1000) * (design['depth']/1000) * design['span']
    steel_weight = calculate_steel_weight(design)  # From existing code

    # 2. Calculate costs
    material_cost = (concrete_vol * rates['concrete']) + (steel_weight * rates['steel'])
    labor_cost = concrete_vol * rates['labor']

    # 3. Add contingency (10%)
    total = (material_cost + labor_cost) * 1.1

    return total
```

**Acceptance Criteria:**
- Can calculate cost for any valid beam
- Results are ±5% of manual calculation
- Rates are configurable (not hardcoded)

**Estimated Time:** 3 hours

---

### TASK-003: Create Carbon Calculator

**What:**
Given a beam design, calculate CO2 impact.

**Logic:**
```
Carbon = (Concrete Volume × Emission Factor) + (Steel Weight × Steel Factor)

Typical factors:
  Concrete: 0.4 kgCO2/kg (includes cement + aggregate)
  Steel: 2.0 kgCO2/kg (includes recycling, transport)
```

**Code Template:**
```python
def calculate_carbon(design, factors):
    """
    design = {width, depth, bars_main, bars_shear}
    factors = {concrete: 0.4 kgCO2/kg, steel: 2.0 kgCO2/kg}

    Returns: kgCO2
    """
    concrete_weight = calculate_concrete_weight(design)  # density = 2400 kg/m³
    steel_weight = calculate_steel_weight(design)

    carbon = (concrete_weight * factors['concrete']) + (steel_weight * factors['steel'])
    return carbon
```

**Acceptance Criteria:**
- Can calculate carbon for any beam
- Results match LCA database (±10%)
- Factors are configurable

**Estimated Time:** 2 hours

---

### TASK-004: Integration Test

**What:**
Create a test that validates a design end-to-end.

**Test:**
```python
def test_design_validation_and_objectives():
    design = {
        'span': 6000,  # 6m
        'load': 40,    # 40 kN
        'width': 300,
        'depth': 450,
        'bars_main': 4,
        'dia_main': 16,
        'bars_shear': 2,
        'dia_shear': 8,
        'grade_concrete': 25,
        'grade_steel': 500
    }

    # Validate
    validation = validate_beam(design)
    assert validation['Moment']['status'] == 'PASS'
    assert validation['Deflection']['status'] == 'PASS'

    # Calculate objectives
    cost = calculate_cost(design, RATES)
    carbon = calculate_carbon(design, FACTORS)
    depth = design['depth']

    # Assert reasonable
    assert cost > 0
    assert carbon > 0
    assert 200 < depth < 600
```

**Acceptance Criteria:**
- Test passes for 5 different designs
- Cost is within ±5% of manual calc
- Carbon is within ±10%

**Estimated Time:** 2 hours

---

## TASK GROUP 2: Phase 1 MVP (Week 2)

### TASK-005: Create Streamlit Page (Single Design Analysis)

**What:**
User inputs: Span, Load, Grade
System shows: Cost, Depth, Safety Factor for that design

**UI Layout:**
```
┌─────────────────────────────────────────┐
│        Beam Design Calculator           │
├─────────────────────────────────────────┤
│ Span (m):           [_________]         │
│ Load (kN):          [_________]         │
│ Concrete Grade:     [25 ▼]              │
│ Steel Grade:        [500 ▼]             │
│                     [CALCULATE]         │
├─────────────────────────────────────────┤
│ RESULTS:                                │
│ ─────────────────────────────────────── │
│ Width:   300 mm     Cost:    INR 45,000 │
│ Depth:   450 mm     Carbon:  1,200 kg   │
│ Safety:  2.1        Status:  ✓ PASS    │
├─────────────────────────────────────────┤
│ [Show Calculation Details]              │
└─────────────────────────────────────────┘
```

**Code Template:**
```python
import streamlit as st
from structural_lib import calculate_cost, calculate_carbon, validate_beam

st.title("Beam Design Calculator")

col1, col2 = st.columns(2)
with col1:
    span = st.number_input("Span (m)", 3, 15, 6)
    load = st.number_input("Load (kN/m)", 5, 100, 40)

with col2:
    grade_concrete = st.selectbox("Concrete Grade", [20, 25, 30])
    grade_steel = st.selectbox("Steel Grade", [415, 500])

if st.button("Calculate"):
    design = {
        'span': span * 1000,  # Convert to mm
        'load': load,
        'width': 300,
        'depth': 450,
        'bars_main': 4,
        'dia_main': 16,
    }

    # Validate
    validation = validate_beam(design)

    # Objectives
    cost = calculate_cost(design, RATES)
    carbon = calculate_carbon(design, FACTORS)

    # Display
    st.metric("Cost", f"INR {cost:,.0f}")
    st.metric("Carbon", f"{carbon:.0f} kg CO2")
    st.metric("Status", "✓ PASS" if validation['Moment']['status'] == 'PASS' else "✗ FAIL")
```

**Acceptance Criteria:**
- Page loads without errors
- Can input span, load, grade
- Displays cost, carbon, safety
- Clicking "Details" shows which IS 456 checks passed/failed

**Estimated Time:** 4 hours

---

### TASK-006: Create Trade-off Visualization

**What:**
Add a chart showing: "What if I change depth?"

**Logic:**
```
For each depth in [300, 350, 400, 450, 500, 550, 600]:
  Calculate cost
  Calculate carbon
  Validate against IS 456
  Plot point on scatter
```

**UI Addition:**
```
[CHART] Cost vs Depth

Cost (INR)
  │
  │       ●(450mm, 45K)  ← Current design
  │      ●
  │     ●
  │    ●                  ← Increasing depth makes it cheaper
  │   ●
  ├──────────────────────
  300   400   500   600   Depth (mm)
```

**Code:**
```python
if st.checkbox("Show Trade-off Analysis"):
    depths = range(300, 601, 50)
    results = []

    for d in depths:
        design['depth'] = d
        valid = validate_beam(design)
        if valid['Moment']['status'] == 'PASS':
            cost = calculate_cost(design, RATES)
            carbon = calculate_carbon(design, FACTORS)
            results.append({'depth': d, 'cost': cost, 'carbon': carbon})

    # Plot
    import plotly.express as px
    fig = px.scatter(results, x='depth', y='cost', color='carbon',
                     title='Cost vs Depth Trade-off')
    st.plotly_chart(fig)
```

**Acceptance Criteria:**
- Chart displays correctly
- Points are only valid designs
- Color gradient shows carbon impact

**Estimated Time:** 3 hours

---

## TASK GROUP 3: Phase 2 Brute Force (Week 3)

### TASK-007: Brute Force Design Generator

**What:**
Loop through all combinations and find the cheapest valid design for each depth.

**Logic:**
```
For each depth in [300, 350, 400, 450, 500, 550, 600]:
  For each bar_count in [2, 3, 4, 5, 6]:
    For each dia in [10, 12, 16, 20]:
      Create design
      Validate
      If PASS, store cost
  Pick the cheapest PASS design for this depth
```

**Code:**
```python
def generate_pareto_frontier_bruteforce(span, load, grade_c, grade_s):
    """
    Returns list of valid designs (the frontier)
    """
    frontier = []

    for depth in range(300, 601, 50):
        cheapest = None
        cheapest_cost = float('inf')

        for bars in range(2, 7):
            for dia in [10, 12, 16, 20]:
                design = {
                    'span': span, 'load': load,
                    'width': 300, 'depth': depth,
                    'bars_main': bars, 'dia_main': dia,
                    'grade_concrete': grade_c, 'grade_steel': grade_s
                }

                validation = validate_beam(design)
                if validation['Moment']['status'] == 'PASS':
                    cost = calculate_cost(design, RATES)
                    if cost < cheapest_cost:
                        cheapest_cost = cost
                        cheapest = design

        if cheapest:
            frontier.append({
                'design': cheapest,
                'cost': calculate_cost(cheapest, RATES),
                'carbon': calculate_carbon(cheapest, FACTORS),
                'depth': depth
            })

    return frontier
```

**Acceptance Criteria:**
- Returns 7-10 valid designs (one per depth)
- Each design is the cheapest valid option for that depth
- Runs in <30 seconds

**Estimated Time:** 4 hours

---

### TASK-008: Pareto Front Filter

**What:**
From the brute force results, remove any design that is "worse in all ways."

**Logic:**
```
Design A is Pareto Optimal if:
  There does NOT exist Design B such that:
    B.cost ≤ A.cost AND
    B.depth ≤ A.depth AND
    B.carbon ≤ A.carbon AND
    at least one is strictly better
```

**Code:**
```python
def filter_pareto_front(designs):
    """
    designs = [{cost, depth, carbon, design}, ...]
    Returns only the Pareto optimal ones
    """
    pareto = []

    for candidate in designs:
        is_dominated = False
        for other in designs:
            if other is candidate:
                continue

            # Check if 'other' dominates 'candidate'
            better_cost = other['cost'] <= candidate['cost']
            better_depth = other['depth'] <= candidate['depth']
            better_carbon = other['carbon'] <= candidate['carbon']

            # Strictly better in at least one
            strictly_better = (
                (other['cost'] < candidate['cost'] or
                 other['depth'] < candidate['depth'] or
                 other['carbon'] < candidate['carbon'])
            )

            if better_cost and better_depth and better_carbon and strictly_better:
                is_dominated = True
                break

        if not is_dominated:
            pareto.append(candidate)

    return pareto
```

**Acceptance Criteria:**
- Filters out dominated designs
- Keeps 3-8 Pareto optimal designs
- All remaining designs are non-dominated

**Estimated Time:** 2 hours

---

### TASK-009: Dashboard for Pareto Front

**What:**
Interactive chart showing the frontier with hover details.

**UI:**
```
[CHART] Pareto Optimal Beam Designs
Click on any point for details

Cost (INR)
  │
  │       ●← Option A (Cheap, Deep, High CO2)
  │      ●  ← Option B (Medium, Medium, Medium)
  │     ●   ← Option C (Expensive, Shallow, Low CO2)
  │    ●
  │   ●
  ├──────────────────────────────────────
  300   350   400   450   500   550   600   Depth (mm)

[Color: Green (low CO2) to Red (high CO2)]

--- Hover Over Point for Details ---
Option B:
  Width: 300mm, Depth: 450mm
  Reinforcement: 4 bars × 16mm
  Cost: INR 45,000
  Carbon: 1,200 kgCO2
  Safety Factor: 2.1
```

**Code:**
```python
import plotly.express as px

pareto = generate_pareto_frontier_bruteforce(...)
pareto = filter_pareto_front(pareto)

fig = px.scatter(
    pareto,
    x='depth',
    y='cost',
    color='carbon',
    size=[5]*len(pareto),
    hover_data=['design'],
    title='Pareto Optimal Beam Designs',
    color_continuous_scale='RdYlGn_r'  # Red (high CO2) to Green (low)
)

st.plotly_chart(fig, width="stretch")

# Detail view
selected_idx = st.selectbox("Select Design", range(len(pareto)))
design = pareto[selected_idx]['design']
st.write(f"Width: {design['width']}mm, Depth: {design['depth']}mm")
st.write(f"Reinforcement: {design['bars_main']} bars × {design['dia_main']}mm")
```

**Acceptance Criteria:**
- Chart displays all frontier designs
- Hover shows reinforcement details
- Color accurately represents carbon

**Estimated Time:** 3 hours

---

## TASK GROUP 4: Phase 3 NSGA-II (Week 4)

### TASK-010: Integrate pymoo

**What:**
Replace brute force with NSGA-II for speed and better exploration.

**Installation:**
```bash
pip install pymoo
```

**Code Template:**
```python
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.problems import Problem
from pymoo.optimize import minimize

class BeamProblem(Problem):
    def __init__(self):
        super().__init__(
            n_var=4,  # width, depth, bars, dia
            n_obj=3,  # cost, depth, carbon
            n_constr=8,  # IS 456 checks
            bounds=([230, 150, 2, 10], [400, 600, 6, 20])  # min, max
        )

    def _evaluate(self, x, out, *args, **kwargs):
        designs = x  # Array of designs

        # Objectives
        costs = []
        carbons = []
        depths = []

        # Constraints
        constraint_violations = []

        for design in designs:
            validation = validate_beam(design)
            cost = calculate_cost(design, RATES)
            carbon = calculate_carbon(design, FACTORS)
            depth = design[1]  # depth variable

            costs.append(cost)
            carbons.append(carbon)
            depths.append(depth)

            # Constraints (must be g(x) ≤ 0)
            violations = [
                0 if validation['Moment']['status'] == 'PASS' else 1,
                0 if validation['Deflection']['status'] == 'PASS' else 1,
                # ... 8 total
            ]
            constraint_violations.append(violations)

        out["F"] = np.column_stack([costs, depths, carbons])
        out["G"] = np.array(constraint_violations)

# Optimize
problem = BeamProblem()
algorithm = NSGA2(pop_size=100)
res = minimize(problem, algorithm, ('n_gen', 50), verbose=True)

# Extract frontier
frontier = res.X  # Decision variables
objectives = res.F  # Objectives (cost, depth, carbon)
```

**Acceptance Criteria:**
- Runs without errors
- Finds 30-50 designs in <30 seconds
- Results are similar to brute force (but faster)

**Estimated Time:** 5 hours

---

## Summary Timeline

| Week | Task | Hours | Status |
|------|------|-------|--------|
| **1** | TASK-001 to 004 | 11h | Foundation |
| **2** | TASK-005 to 006 | 7h | Phase 1 MVP |
| **3** | TASK-007 to 009 | 9h | Phase 2 MVP |
| **4** | TASK-010 | 5h | Phase 3 Smart |
| **Total** | | **32h** | **≈ 1 week (full-time)** |

---

## Success Criteria (How to Know It Works)

1. **Engineer opens app** → Sees beam calculator
2. **Enters Span=6m, Load=40kN** → Gets cost + carbon in 2 seconds
3. **Clicks "Find Optimal Designs"** → Scatter plot appears with 5-10 options
4. **Hovers over a point** → Sees reinforcement details
5. **Clicks a design** → Full calculation trace shows (with IS 456 clause references)
6. **Engineer thinks** → "This is way better than what I would have designed manually!"

That's the real success.
