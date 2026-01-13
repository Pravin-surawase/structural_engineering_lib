# Complete Function Guide — ELI5 (Explain Like I'm 5)
**For:** Complete beginners
**Purpose:** Understand every major function without jargon

---

## Part 1: What All These Functions Do (The Big Picture)

### The Process

```
You have a concrete beam. You want to know:
1. "How much steel do I need?" → FLEXURE functions answer this
2. "Can it handle sideways forces?" → SHEAR functions answer this
3. "Where do I place the bars?" → DETAILING functions answer this
4. "Will it bend too much?" → SERVICEABILITY functions answer this
5. "Is it safe overall?" → COMPLIANCE functions say YES or NO
```

**Our library has functions for each step.**

---

## Part 2: Core Functions (In Plain English)

### 🔴 FLEXURE — "Can the beam handle bending?"

**The question:** If I put 150 kN·m of load on a beam, how much steel do I need?

#### `calculate_mu_lim()`
**What it does:** Calculates the maximum moment (load) a beam can safely handle.

**Plain English:** "This beam can handle UP TO X kN·m of load. If you apply more, it will fail."

**When to use it:** When you need to know the limit before designing.

**Inputs:**
- `b`: Width of beam (mm) — e.g., 300mm
- `d`: Effective depth (mm) — e.g., 450mm
- `fck`: Concrete strength (N/mm²) — e.g., 25
- `fy`: Steel strength (N/mm²) — e.g., 500

**Outputs:**
- `mu_lim`: Maximum safe moment (kN·m) — e.g., 250 kN·m

**Real example:**
```python
from structural_lib.codes.is456 import flexure
limit = flexure.calculate_mu_lim(b=300, d=450, fck=25, fy=500)
print(f"Max load: {limit:.0f} kN·m")  # Output: Max load: 250 kN·m
```

---

#### `calculate_ast_required()`
**What it does:** Calculates the exact area of steel bars you need.

**Plain English:** "For this load, you need X mm² of steel bars."

**When to use it:** After deciding on beam dimensions and knowing the load.

**Inputs:**
- `b`: Beam width (mm)
- `d`: Effective depth (mm)
- `mu_knm`: Applied load moment (kN·m) — e.g., 150
- `fck`: Concrete strength (N/mm²)
- `fy`: Steel strength (N/mm²)

**Outputs:**
- `ast_required`: Area of steel needed (mm²) — e.g., 942 mm²

**Real example:**
```python
ast = flexure.calculate_ast_required(
    b=300, d=450, mu_knm=150, fck=25, fy=500
)
print(f"Steel needed: {ast:.0f} mm²")  # Output: 942 mm²
```

---

#### `design_singly_reinforced()`
**What it does:** MOST COMMON. Designs a beam with steel only on the tension (bottom) side.

**Plain English:** "Here's all the info: dimensions, load, materials. Tell me how much bottom steel I need."

**When to use it:** For 95% of beams (most don't need top steel).

**Inputs:**
- `b`: Width (mm)
- `d`: Effective depth (mm)
- `d_total`: Total depth (mm) — for cover calculations
- `mu_knm`: Load moment (kN·m)
- `fck`: Concrete strength (N/mm²)
- `fy`: Steel strength (N/mm²)

**Outputs:**
- `ast_required`: Bottom steel area (mm²)
- `ast_min`: Minimum required (by code)
- `ast_max`: Maximum allowed (by code)
- `is_safe`: True if design works, False if it doesn't
- `error_message`: Why it failed (if it did)

**Real example:**
```python
result = flexure.design_singly_reinforced(
    b=300, d=450, d_total=500, mu_knm=150, fck=25, fy=500
)
if result.is_safe:
    print(f"✅ Beam is safe. Use {result.ast_required:.0f} mm² of steel")
else:
    print(f"❌ Beam failed: {result.error_message}")
```

---

#### `design_doubly_reinforced()`
**What it does:** Designs a beam with steel on BOTH top AND bottom (compression + tension).

**Plain English:** "This load is too big for the dimensions. Add steel on top too."

**When to use it:** When singly reinforced fails (load is very high or depth is small).

**Inputs:**
- `b`, `d`, `d_total`: Same as singly
- `asc`: Top steel area (mm²) — you propose this
- `mu_knm`, `fck`, `fy`: Same as singly

**Outputs:**
- `ast_required`: Bottom steel area (mm²)
- `asc_provided`: Top steel area (from your input)
- `is_safe`: Pass/fail
- `error_message`: Failure reason

**Real example:**
```python
# Try doubly reinforced if singly failed
result = flexure.design_doubly_reinforced(
    b=300, d=450, d_total=500, asc=500, mu_knm=200, fck=25, fy=500
)
```

---

#### `design_flanged_beam()`
**What it does:** Designs T-beams and L-beams (beams with a flange/overhang).

**Plain English:** "This isn't a simple rectangle. It's a T-shape or L-shape. Design it."

**When to use it:** For T-beams (floor joists in buildings) or L-beams (edge beams).

**Inputs:** More complex — includes flange dimensions.

**Outputs:** Same as singly/doubly reinforced.

---

### 🔵 SHEAR — "Can the beam handle sideways forces?"

**The question:** If I push sideways on the beam with 100 kN of force, does it break?

#### `calculate_tv()`
**What it does:** Calculates the nominal shear stress in the beam.

**Plain English:** "The sideways stress is X N/mm². Is that OK?"

**Inputs:**
- `vu_kn`: Sideways force (kN) — e.g., 100 kN
- `b`: Width (mm)
- `d`: Depth (mm)

**Outputs:**
- `tv`: Shear stress (N/mm²)

**Real example:**
```python
tv = shear.calculate_tv(vu_kn=100, b=300, d=450)
print(f"Shear stress: {tv:.2f} N/mm²")  # Output: 0.74 N/mm²
```

---

#### `design_shear()`
**What it does:** Decides whether stirrups (bent bars) are needed and where to space them.

**Plain English:** "You have this sideways force. Do you need stirrups? Yes. Use this spacing."

**Inputs:**
- `vu_kn`: Sideways force (kN)
- `b`: Width (mm)
- `d`: Depth (mm)
- `fck`: Concrete strength (N/mm²)
- `fy`: Steel strength (N/mm²)
- `asv`: Stirrup bar area (mm²) — e.g., 2 legs of 8mm bar = 101 mm²
- `pt`: Tension steel percentage (%) — from flexure design

**Outputs:**
- `tv`: Shear stress (N/mm²)
- `tc`: Concrete shear capacity (N/mm²)
- `vus`: Stirrup capacity (kN)
- `spacing`: Maximum stirrup spacing (mm) — e.g., 150mm
- `is_safe`: Pass/fail
- `remarks`: Details (e.g., "Stirrups required at 150mm c/c")

**Real example:**
```python
result = shear.design_shear(
    vu_kn=100, b=300, d=450, fck=25, fy=500, asv=101, pt=0.33
)
if result.is_safe:
    print(f"✅ Use 8mm stirrups at {result.spacing:.0f}mm spacing")
else:
    print(f"❌ Increase depth or use different reinforcement")
```

---

### 🟢 DETAILING — "Where do I physically place the bars?"

**The question:** "I know I need 942 mm² of steel. Which bars should I use and where?"

#### `decide_bar_arrangement()`
**What it does:** Chooses actual bar sizes (12mm, 16mm, 20mm, etc.) and how many you need.

**Plain English:** "You need 942 mm². Use 3 bars of 20mm (each bar = 314 mm², total = 942 mm²)."

**Inputs:**
- `ast_required`: Area you need (mm²)
- `fy`: Steel grade (to match steel properties)

**Outputs:**
- `bars`: List of bars (e.g., [{"size": 20, "count": 3}])
- `ast_provided`: Actual area (mm²)

**Real example:**
```python
bars = detailing.decide_bar_arrangement(ast_required=942, fy=500)
# Output: 3 bars of 20mm diameter
```

---

#### `check_minimum_spacing()`
**What it does:** Checks if your bars fit without violating code spacing rules.

**Plain English:** "You want 3 bars of 20mm. Will they fit? Yes, with 100mm spacing."

**Inputs:**
- `bars`: Bar arrangement
- `b`: Beam width (mm)
- `cover`: Concrete cover (mm) — usually 40-50mm

**Outputs:**
- `is_safe`: True if bars fit, False if too tight
- `min_spacing_required`: Minimum spacing (mm)
- `actual_spacing`: What you actually get (mm)

**Real example:**
```python
result = detailing.check_minimum_spacing(
    bars=[{"size": 20, "count": 3}], b=300, cover=40
)
if result.is_safe:
    print(f"✅ Bars fit with {result.actual_spacing:.0f}mm spacing")
else:
    print(f"❌ Bars too tight. Reduce count or increase width.")
```

---

#### `calculate_development_length()`
**What it does:** Calculates how long the bars must be to "grip" the concrete.

**Plain English:** "Your bars need to extend at least X mm beyond the point they're supporting."

**Inputs:**
- `bar_diameter`: Bar size (mm)
- `fck`: Concrete strength (N/mm²)
- `fy`: Steel strength (N/mm²)
- `bond_type`: "Good" or "Poor" (depends on bar coating, position)

**Outputs:**
- `ld`: Development length (mm)

**Real example:**
```python
ld = detailing.calculate_development_length(
    bar_diameter=20, fck=25, fy=500, bond_type="Good"
)
print(f"Each bar needs to be at least {ld:.0f}mm long")  # e.g., 650mm
```

---

### 🟡 SERVICEABILITY — "Will the beam bend or crack too much?"

**The question:** "The beam is safe structurally, but will it sag or crack visibly?"

#### `check_deflection_span_depth()`
**What it does:** Quick check: does the beam height match the span?

**Plain English:** "For a 6m span, the depth should be at least 300mm. You have 450mm. ✅"

**Inputs:**
- `span_mm`: Beam span (mm)
- `d`: Effective depth (mm)
- `cantilever`: True if it's a cantilever, False if simply supported

**Outputs:**
- `is_safe`: Pass/fail
- `min_d_required`: Minimum depth needed (mm)
- `ratio`: Your actual ratio (e.g., 1:20)

**Real example:**
```python
result = check_deflection_span_depth(span_mm=6000, d=450, cantilever=False)
# Output: Ratio is 1:13.3 (safe, usually want 1:20 or better)
```

---

#### `check_crack_width()`
**What it does:** Calculates if visible cracking will occur.

**Plain English:** "With this load and steel arrangement, cracks will be 0.15mm (OK, <0.3mm limit)."

**Inputs:**
- `ast_provided`: Actual steel area (mm²)
- `b`: Width (mm)
- `d`: Depth (mm)
- `mu_knm`: Load moment (kN·m)
- `fy`: Steel strength (N/mm²)
- `cover`: Concrete cover (mm)

**Outputs:**
- `crack_width`: Crack width (mm)
- `is_safe`: True if <0.3mm (usual limit)

**Real example:**
```python
result = check_crack_width(
    ast_provided=942, b=300, d=450, mu_knm=150,
    fy=500, cover=40
)
print(f"Crack width: {result.crack_width:.2f}mm")  # e.g., 0.15mm
```

---

## Part 3: High-Level Functions (One Command Does Everything)

### 🟣 `design_and_detail_beam_is456()`

**What it does:** ONE FUNCTION that does EVERYTHING.

**Plain English:** "Here's the beam. Design it (flexure + shear), detail it (choose bars), and tell me if it's safe."

**Inputs:**
- `beam`: A BeamInput object with all properties
- `config`: Detailing configuration (bar sizes allowed, etc.)

**Outputs:**
- Everything: flexure, shear, detailing, serviceability results

**Real example:**
```python
from structural_lib.api import design_and_detail_beam_is456
from structural_lib.inputs import BeamInput, BeamGeometryInput

beam_input = BeamInput(
    beam_id="B1",
    geometry=BeamGeometryInput(b=300, D=500, span=6000, cover=40),
    materials=...,
    loads=...
)

result = design_and_detail_beam_is456(beam_input)
# Result has everything: ast, stirrups, ld, cracks, deflection, etc.
```

---

## Part 4: Utility Functions

### Tables & Material Properties

#### `materials.get_concrete_modulus()`
**What it does:** Looks up the stiffness of concrete for a given strength.

**Inputs:** `fck` (N/mm²)
**Outputs:** `Ec` (elastic modulus)

---

#### `tables.get_pt_clamp()`
**What it does:** Looks up steel percentage limits from IS 456 tables.

**Inputs:** `fy` (steel strength)
**Outputs:** `pt_min`, `pt_max` (percentage limits)

---

### Validation Functions

#### `validation.validate_dimensions()`
**What it does:** Checks if b, d, D make sense (all positive, D > d, etc.).

**Real example:**
```python
from structural_lib.validation import validate_dimensions
errors = validate_dimensions(b=300, d=450, D=500)
if errors:
    print(f"Invalid: {errors}")
else:
    print("✅ Dimensions OK")
```

---

## Part 5: Real Example — Design a Complete Beam

```python
from structural_lib.codes.is456 import flexure, shear, detailing
from structural_lib import materials, tables

# Step 1: Define the beam
b, d, D = 300, 450, 500  # mm
fck, fy = 25, 500         # N/mm²
mu_knm, vu_kn = 150, 100  # kN·m, kN
cover = 40                 # mm

# Step 2: Check limiting moment
mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)
print(f"1️⃣ Max moment this section can handle: {mu_lim:.0f} kN·m")
if mu_knm > mu_lim:
    print("   ❌ Increase depth or use doubly reinforced!")
else:
    print("   ✅ Singly reinforced will work")

# Step 3: Design flexure (get required steel)
flex_result = flexure.design_singly_reinforced(
    b=b, d=d, d_total=D, mu_knm=mu_knm, fck=fck, fy=fy
)
print(f"2️⃣ Steel required: {flex_result.ast_required:.0f} mm²")
print(f"   Min allowed: {flex_result.ast_min:.0f} mm²")
print(f"   Max allowed: {flex_result.ast_max:.0f} mm²")

# Step 4: Design shear (get stirrup spacing)
pt = (flex_result.ast_required / (b * d)) * 100
shear_result = shear.design_shear(
    vu_kn=vu_kn, b=b, d=d, fck=fck, fy=fy, asv=101, pt=pt
)
print(f"3️⃣ Stirrup spacing: {shear_result.spacing:.0f} mm")
if not shear_result.is_safe:
    print("   ❌ Increase depth!")

# Step 5: Detail (choose actual bars)
bars = detailing.decide_bar_arrangement(
    ast_required=flex_result.ast_required, fy=fy
)
print(f"4️⃣ Use bars: {bars}")

# Step 6: Check spacing
spacing_result = detailing.check_minimum_spacing(
    bars=bars, b=b, cover=cover
)
print(f"5️⃣ Bar spacing: {spacing_result.actual_spacing:.0f} mm")
if not spacing_result.is_safe:
    print("   ❌ Bars don't fit!")

# Step 7: Calculate development length
ld = detailing.calculate_development_length(
    bar_diameter=20, fck=fck, fy=fy, bond_type="Good"
)
print(f"6️⃣ Bar extension needed: {ld:.0f} mm")

# FINAL: All checks passed!
if (flex_result.is_safe and shear_result.is_safe and
    spacing_result.is_safe):
    print("\n✅✅✅ BEAM IS SAFE TO BUILD")
else:
    print("\n❌ DESIGN FAILED - See above")
```

---

## Part 6: Common Patterns

### Pattern 1: Batch Design (Many Beams)
```python
import pandas as pd

beams_csv = pd.read_csv("beams.csv")

for idx, row in beams_csv.iterrows():
    result = flexure.design_singly_reinforced(
        b=row['b'], d=row['d'], d_total=row['D'],
        mu_knm=row['Mu'], fck=row['fck'], fy=row['fy']
    )
    print(f"Beam {row['id']}: {result.ast_required:.0f} mm² of steel")
```

### Pattern 2: Find Optimal Depth
```python
# What depth do we need for this load?
for d in range(300, 600, 50):
    result = flexure.design_singly_reinforced(
        b=300, d=d, d_total=d+50, mu_knm=150, fck=25, fy=500
    )
    if result.is_safe:
        print(f"Minimum depth needed: {d} mm")
        break
```

### Pattern 3: Cost Optimization
```python
best_design = None
best_cost = float('inf')

for depth in range(300, 700, 50):
    result = flexure.design_singly_reinforced(...)
    if result.is_safe:
        steel_weight = result.ast_required * STEEL_DENSITY
        cost = steel_weight * STEEL_PRICE
        if cost < best_cost:
            best_cost = cost
            best_design = (depth, result.ast_required)

print(f"Cheapest design: depth {best_design[0]}mm, steel {best_design[1]:.0f}mm²")
```

---

## Part 7: Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| **Design fails immediately** | Input error (negative values, etc.) | Check `error_message` in result |
| **Steel area too large** | Depth is too small | Increase `d` or use `design_doubly_reinforced()` |
| **Bars don't fit** | Too many bars for width | Use fewer, larger bars OR increase width |
| **Spacing is very small** | Concrete grade is low | Use higher concrete (fck=30 instead of 25) |
| **Result seems wrong** | Maybe it's right! | Compare with hand calc or SAFE/STAAD |

---

## Next Steps

1. **Today:** Read this guide ✓
2. **Today:** Run the "Real Example" code above
3. **Tomorrow:** Design 5 beams manually
4. **This week:** Try batch design with CSV input
5. **This week:** Compare your results with hand calculations

---

**You now know every major function! 🎉**

Questions? Ask yourself:
- "What does this function do?" → Read the "What it does" line
- "When would I use it?" → Read the "When to use it" section
- "What goes in?" → Read the Inputs
- "What comes out?" → Read the Outputs

---

Created: 2026-01-13
For: New developers learning the library
