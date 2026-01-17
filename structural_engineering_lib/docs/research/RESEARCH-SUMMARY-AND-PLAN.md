# Research Summary & Mathematical Formulation
> **Making the research simple + Converting to a solvable problem**

---

## PART 1: What Did We Discover? (In Simple Language)

### The Main Insight
**Problem:** Right now, structural engineers design beams one at a time. They pick a depth, check if it works, and if not, they try again. This is slow and wasteful.

**Solution:** We can use math (Pareto Optimization) to automatically show engineers *all the best options* at once. For example:
- Option A: Cheapest beam (but a bit deeper)
- Option B: Thinnest beam (but costs more)
- Option C: Safest beam (but heaviest)

None of these is "the best"—they're all equally good at different things. The engineer picks which matters most to them.

### What Makes This Hard?
1. **The Code (IS 456):** It's strict. A design must follow hundreds of rules or it fails completely.
2. **Trade-offs:** Making it cheaper usually makes it deeper. Making it safer costs more.
3. **Trust:** Engineers don't trust "black box" tools. They need to *see* and *understand* the decision.

### What Did Each Phase Teach Us?

| Phase | What We Learned | Simple Version |
|-------|-----------------|-----------------|
| **1.1** | NSGA-II is the standard algorithm | The "best tested" tool for this type of problem |
| **1.2** | Modern research (2025-2026) has smarter visualizations | Show the trade-offs visually, don't overwhelm with numbers |
| **1.3** | Top researchers (Parhi et al.) now combine NSGA-II + IS 456 code | The idea works—it's been done. We can replicate it. |
| **1.4** | Engineers trust systems that *explain* decisions | Don't say "this is optimal." Say "this is optimal *because* it minimizes deflection." |
| **1.5** | Roadmap: Start simple (brute force), graduate to smart (NSGA-II) | Build in steps. Don't try to do everything at once. |

---

## PART 2: What Are We Building? (Phase Breakdown)

### Phase 1: The "What If" Tool (v0.17.x)
**Goal:** Let engineers see trade-offs in their current manual designs.

**What You Do:**
1. Engineer enters: Span, Load, Concrete Grade, Steel Grade.
2. System calculates: Cost, Depth, Safety Factor for that one design.
3. System plots: "If you changed depth to 500mm, cost would be INR X, safety would be Y."

**Why First?** Easiest to build. No fancy algorithms. Just loops.

**Finding:** Engineers learn that "safer" ≠ "more cost." There's a sweet spot.

---

### Phase 2: The "Brute Force" Frontier (v0.18.0)
**Goal:** Show all possible valid beam designs in a visual chart.

**What You Do:**
1. Engineer says: "Show me all valid designs for depths from 300mm to 600mm."
2. System loops through depths: 300, 320, 340, ... 600 mm.
3. For each depth: Calculate cost, safety. If it passes IS 456, plot it.
4. Display as scatter plot: X-axis = Depth, Y-axis = Cost, Color = Safety Factor.

**Why This?** Still simple (no algorithms). But now engineer *sees* the frontier.

**Finding:** Most engineers see patterns they didn't expect. "Wow, increasing depth by 50mm saves INR 5000!"

---

### Phase 3: The "Smart" Optimizer (v0.19.0)
**Goal:** Automatically find the *best* frontier (don't check every depth manually).

**What You Do:**
1. Engineer says: "Find me the cheapest AND safest designs."
2. System runs NSGA-II algorithm: It's smart enough to skip useless designs.
3. In 5 seconds: Plot shows the true Pareto frontier.

**Why This?** When you add rebar patterns (which bars, how many?), manual loops are too slow.

**Finding:** The algorithm finds designs humans would never think of.

---

### Phase 4: The "Eco" Design Tool (v0.20.0)
**Goal:** Optimize for Cost + Carbon Footprint + Safety all at once.

**What You Do:**
1. Engineer says: "Find me designs that balance cost, carbon, and safety."
2. System calculates: For each design, not just cost (INR), but also CO2 impact (kg).
3. Displays: A 3D plot showing all three trade-offs.

**Why This?** Climate matters. Engineers want sustainable designs but don't know which trade-offs are worth it.

**Finding:** Carbon-efficient designs often cost *less* than traditional ones (less concrete = less money).

---

## PART 3: The Math Problem (Simple Version)

### What Are We Solving?
**English:** Find all beam designs that are simultaneously:
- As cheap as possible
- As shallow as possible
- As safe as possible
- AND obey ALL IS 456 rules

**Math Translation:**

```
MINIMIZE:  f₁(Design) = Cost (INR)
           f₂(Design) = Depth (mm)
           f₃(Design) = Carbon Footprint (kgCO2)

SUBJECT TO (Hard Constraints - Must not break):
           Deflection ≤ Span/250  [IS 456 Cl. 23.2]
           Crack Width ≤ 0.2 mm   [IS 456 Cl. 39.4]
           Ast ≥ Ast,min          [IS 456 Cl. 26.5.1.1]
           Pt% ≤ Pt,max           [IS 456 Cl. 26.5.2.2]
           Pu ≥ Design Load       [Equilibrium]

DECISION VARIABLES:
           Width (b) = 230, 300, 350, 400 mm
           Depth (d) = 150, 200, 250, ... 600 mm
           Bar Diameter = 8, 10, 12, 16, 20 mm
           Number of Bars = 2, 3, 4, 5, 6 bars
```

### What Does "Pareto Optimal" Mean?
**Simple:** A design is "Pareto Optimal" if you *cannot* make it cheaper without making it deeper OR less safe.

**Example:**
- Design A: Cost = INR 50K, Depth = 450mm, Safety Factor = 2.1
- Design B: Cost = INR 48K, Depth = 400mm, Safety Factor = 2.3

Design B is **better in all ways** (cheaper, shallower, safer). So Design A is *not* Pareto Optimal—it's wasteful.

The **Pareto Front** = the collection of all designs where no design can be improved without hurting another.

---

## PART 4: Our Implementation Logic (What We'll Do)

### Step 1: Build the "Validator" Function
```python
def validate_beam(width, depth, bars, grade_concrete, grade_steel, span, load):
    """
    Input: A design (dimensions + reinforcement)
    Check: Does it obey IS 456?
    Output: PASS/FAIL + Utilization Ratio (0.0 to 1.0)

    If FAIL, return WHY (e.g., "Deflection exceeds limit by 8%")
    """
```

**Why This First?** Everything else depends on it. Can't optimize if we can't validate.

### Step 2: Define Objective Functions
```python
def cost_function(design):
    """Calculate: Material cost + Labor cost"""
    return material_cost + labor_cost

def depth_function(design):
    """Just return the depth"""
    return design['depth_mm']

def carbon_function(design):
    """Calculate: CO2 per kg of concrete + steel"""
    return concrete_volume * emission_factor + steel_weight * steel_emission_factor
```

**Why?** NSGA-II needs these to rank designs.

### Step 3: Generate Initial Population
```python
def generate_random_design():
    """Randomly pick width, depth, bars"""
    return {
        'width': random.choice([230, 300, 350, 400]),
        'depth': random.choice([150, 200, 250, 300, 400, 500, 600]),
        'bars': random.choice([2, 3, 4, 5, 6]),
        'dia': random.choice([8, 10, 12, 16, 20])
    }
```

### Step 4: Run NSGA-II
```python
population = [generate_random_design() for _ in range(100)]
for generation in range(50):
    # NSGA-II magic: Crossover + Mutation
    new_population = nsga2_step(population, validate_beam, [cost_fn, depth_fn, carbon_fn])
    population = new_population
```

### Step 5: Plot the Pareto Front
```python
# Extract only valid designs from population
pareto_front = [d for d in population if d['valid'] == True]

# Plot: X=Depth, Y=Cost, Color=Safety
plot.scatter(
    x=[d['depth'] for d in pareto_front],
    y=[d['cost'] for d in pareto_front],
    color=[d['safety_factor'] for d in pareto_front]
)
```

---

## PART 5: Why This Approach Works

### Reason 1: Modularity
Each step is independent:
- Validator can be tested without NSGA-II
- NSGA-II can use any validator
- Plotting works for any population

### Reason 2: Transparency
Because we store *how* each design was validated, we can explain:
- "Why is this design *not* cheaper?" → Because it violates Crack Width by 0.3mm
- "Why did you pick this one?" → Because it's cheaper AND safer than all others

### Reason 3: Extensibility
Easy to add new objectives (Carbon, Durability, Constructability) without rewriting the core.

### Reason 4: Realistic
We're not building a theoretical toy. We're embedding *actual* IS 456 code logic, so results are immediately useful.

---

## PART 6: The Problem as Math (Formal)

### Multi-Objective Optimization Problem
```
Minimize: F(x) = [f₁(x), f₂(x), f₃(x)]
Where:
  x ∈ X (Decision Space)
  x = (b, d, n_bars, d_bar)
      ∈ {230..400} × {150..600} × {2..6} × {8,10,12,16,20}

  f₁(x) = Annual Cost (INR)
  f₂(x) = Beam Depth (mm)
  f₃(x) = Carbon Footprint (kgCO2)

Subject to: g_i(x) ≤ 0 for all i ∈ {1..8}
  g₁: Deflection - Limit ≤ 0
  g₂: Crack Width - Limit ≤ 0
  g₃: Steel Ratio - Max ≤ 0
  g₄: Steel Ratio - Min ≥ 0
  g₅: Moment Capacity - Demand ≥ 0
  g₆: Shear Capacity - Demand ≥ 0
  g₇: Anchorage Length - Available ≤ 0
  g₈: Cover - Requirement ≤ 0
```

### Solution Strategy
**Algorithm:** NSGA-II (Non-Dominated Sorting Genetic Algorithm)

**Why NSGA-II?**
1. Handles multiple conflicting objectives (cost, depth, carbon)
2. Finds *many* good solutions (not just one)
3. Proven in 100+ engineering papers
4. Works with discrete variables (bar sizes, counts)

**Expected Output:**
- Pareto Front: 20-100 non-dominated designs
- Time: 5-30 seconds for standard beam
- Accuracy: ±2% on structural calculations (within design safety margins)

---

## PART 7: Implementation Order (What to Code First)

### Week 1: Foundation
- [ ] Refactor `is456_validator.py` to return structured data (not just exceptions)
- [ ] Write `cost_function()` and `carbon_function()`
- [ ] Test on 10 manual designs

### Week 2: Phase 1 MVP
- [ ] Create Streamlit page: "Beam Trade-off Explorer"
- [ ] Plot: Depth vs Cost (single design analysis)
- [ ] Input: Span, Load, Grade

### Week 3: Phase 2 Brute Force
- [ ] Create `generate_designs_brute_force()` function
- [ ] Loop depths from 300 to 600mm (step 50mm)
- [ ] For each depth: Try 2-6 bars, pick the cheapest valid design
- [ ] Plot Pareto frontier

### Week 4: Phase 3 NSGA-II
- [ ] Integrate `pymoo` library
- [ ] Implement NSGA-II wrapper around validator
- [ ] Compare output with brute force (should be similar but faster)

---

## Summary: What We're Building

| What | Why | When |
|------|-----|------|
| **Validator** | Can't optimize if we can't check | Week 1 |
| **Cost Calculator** | Needs to be accurate to be useful | Week 1 |
| **Brute Force Frontier** | Simplest working version | Week 2 |
| **NSGA-II Optimizer** | Smart version (faster, more features) | Week 4 |
| **Visual Dashboard** | Engineers need to *see* the trade-offs | Weeks 2-4 |
| **Explanation Layer** | "Why did you pick this?" (Trust) | Week 5 |

**End Result:** An engineer opens our app, enters Span=10m and Load=50kN, clicks "Find Optimal Designs", and in 5 seconds sees a beautiful scatter plot with 50 designs to choose from. They click one, and it shows them the exact reinforcement, checks, and calculations.

That's the goal.
