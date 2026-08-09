# Day 5: Column Design

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** Critical
**Created:** 2026-04-08
**Last Updated:** 2026-04-08
**Prerequisites:** Day 1 (materials), Day 2 (flexure concepts — stress block, neutral axis)
**Library files:** `Python/structural_lib/codes/is456/column/axial.py`, `Python/structural_lib/codes/is456/column/uniaxial.py`, `Python/structural_lib/codes/is456/column/biaxial.py`
**IS 456 Clauses:** Cl 25.1.2, Cl 25.2, Cl 25.4, Cl 26.5.3, Cl 39.3, Cl 39.5, Cl 39.6, Cl 39.7, Table 28

---

## What You'll Learn Today

By the end of this module you'll understand:
- What a column actually does and how it differs from a beam
- Short vs slender columns — classification and effective length
- Minimum eccentricity — why no load is ever truly "axial"
- The axial capacity formula (Cl 39.3)
- P-M interaction curves — *the* central concept in column design
- Biaxial bending — real columns bend in two directions
- Slender columns and the additional moment method
- Column detailing rules

---

## 📖 Theory

### 1. What Is a Column?

A beam lies horizontally and carries loads by bending. A column stands **vertically** and carries loads primarily by **compression** — the weight of all the floors above pressing straight down.

> **Think of it like...** the legs of a table. The tabletop (slab) transfers load to the legs (columns), which push it down to the floor (foundation). If a leg buckles or crushes, the table collapses.

But here's the key difference from a simple compression member: real columns almost always carry **bending moments too**. Beams frame into columns at joints, and the unbalanced moments from those beams get transferred into the column. So a column must resist:
- **Axial compression** ($P_u$) — the weight above
- **Bending moment** ($M_u$) — from connected beams, wind loads, seismic forces

This combined loading is what makes column design fundamentally different from beam design. In a beam, you design for M and V separately. In a column, P and M interact — you can't design for one without considering the other.

```
        Pu (axial compression)
         ↓↓↓↓↓↓↓↓↓↓↓↓↓↓
    ┌──────────────────────┐
    │     ┌──────────┐     │  ← beam framing in
    │     │  Column  │     │
    │     │  b × D   │→ Mu (moment from beam)
    │     │          │     │
    │     │  ● ● ● ● │     │  ← reinforcement bars
    │     └──────────┘     │
    │                      │
    └──────────────────────┘
```

---

### 2. Column Classification: Short vs Slender

Not all columns behave the same way under load. A stocky column fails by **crushing** — the concrete and steel simply exceed their material strength. A slender column fails by **buckling** — it bows out sideways before the material is fully stressed.

**IS 456 Cl 25.1.2** defines the boundary:

$$\frac{l_e}{D} < 12 \implies \text{Short column}$$
$$\frac{l_e}{D} \geq 12 \implies \text{Slender column}$$

Where:
- $l_e$ = **effective length** (not the actual physical length between floors)
- $D$ = column depth in the direction considered

#### Effective Length (Cl 25.2, Table 28)

The effective length depends on how the column ends are restrained. This is exactly like Euler's buckling theory — a column fixed at both ends is much stronger (in buckling) than one that's free at the top.

**IS 456 Table 28** gives the ratio $l_e / l$ for seven standard cases:

| End Condition | Theoretical | Recommended (Design) | Real-World Case |
|--------------|------------|---------------------|------------------|
| Fixed–Fixed | 0.50 | 0.65 | Column between rigid beams on both floors |
| Fixed–Hinged | 0.70 | 0.80 | Column with stiff beam at bottom, flexible at top |
| Fixed–Fixed (sway) | 1.00 | 1.20 | Braced frame with some sway |
| Fixed–Free | 2.00 | 2.00 | Cantilever column (flagpole) |
| Hinged–Hinged | 1.00 | 1.00 | Simply supported at both ends |
| Fixed–Partial | — | 1.50 | Partially restrained at one end |
| Hinged–Partial | — | 2.00 | One end hinged, other partially restrained |

> **Think of it like...** a ruler standing on end. Hold both ends firmly (fixed-fixed) and it's hard to buckle — effective length is just 0.65× the actual length. Hold one end and leave the other free (cantilever) and it buckles easily — effective length is 2× the actual length.

**Why "recommended" > "theoretical"?** Because real connections are never perfectly fixed or perfectly hinged. The recommended values add a safety margin for imperfect restraints.

Our library implements this with `EndCondition` enums:

```python
from structural_lib.codes.is456.column.axial import effective_length, classify_column
from structural_lib.core.data_types import EndCondition

# A 3000mm column, fixed at both ends
le = effective_length(l_mm=3000, end_condition=EndCondition.FIXED_FIXED)
print(f"Effective length: {le} mm")  # 3000 x 0.65 = 1950 mm

# Classify: short or slender?
# For a 400mm x 400mm column:
classification = classify_column(le_mm=1950, D_mm=400)
print(f"Classification: {classification}")  # SHORT (1950/400 = 4.875 < 12)
```

---

### 3. Minimum Eccentricity — No Load Is Ever Truly Axial

Even when an architect draws a load arrow pointing straight down through the column center, the real-world load is never perfectly centered. Construction tolerances, unequal beam spans, lateral loads, and creep all introduce some eccentricity.

**IS 456 Cl 25.4** mandates a minimum eccentricity:

$$e_{min} = \max\left(\frac{l_{unsupported}}{500} + \frac{D}{30},\ 20\right) \text{ mm}$$

Where:
- $l_{unsupported}$ = actual clear height between floors (mm)
- $D$ = lateral dimension of column (mm)
- 20 mm = absolute minimum

**Example:** Column height 3000 mm, dimension 300 mm:

$$e_{min} = \max\left(\frac{3000}{500} + \frac{300}{30},\ 20\right) = \max(6 + 10,\ 20) = 20 \text{ mm}$$

This means every column is really a **column with bending** — purely axial design is just a simplified special case for small eccentricities.

```python
from structural_lib.codes.is456.column.axial import min_eccentricity

e_min = min_eccentricity(l_unsupported_mm=3000, D_mm=300)
print(f"Minimum eccentricity: {e_min} mm")  # 20.0 mm

# Larger column:
e_min_large = min_eccentricity(l_unsupported_mm=5000, D_mm=600)
print(f"Minimum eccentricity: {e_min_large} mm")  # max(10 + 20, 20) = 30.0 mm
```

---

### 4. Short Column Under Axial Load — Cl 39.3

For a short column where the eccentricity is small ($e_{min} \leq 0.05D$), IS 456 gives a simple formula:

$$P_u = 0.4 \times f_{ck} \times A_c + 0.67 \times f_y \times A_{sc}$$

Where:
- $A_c = A_g - A_{sc}$ = concrete area (gross area minus steel area)
- $A_{sc}$ = area of longitudinal steel
- $A_g$ = gross cross-sectional area ($b \times D$)

**Let's break down the coefficients:**

The 0.4 for concrete comes from: $\frac{0.446 \times f_{ck}}{1.0} \approx 0.4$ (the stress block factor divided by partial safety factor considerations, already built-in).

The 0.67 for steel comes from: $\frac{f_y}{\gamma_s} \times \text{strain factor} \approx \frac{f_y}{1.15} \times 0.77 \approx 0.67 \times f_y$

These are IS 456 prescribed constants — they already include the material safety factors ($\gamma_c = 1.5$, $\gamma_s = 1.15$).

> **Think of it like...** a box of mixed produce. The box's total capacity is the weight the cardboard (concrete) can hold plus the weight the reinforcing tape (steel) can support. Equation 39.3 adds: "concrete contribution + steel contribution = total capacity."

**Example:** 400 × 400 mm column, M25, Fe415, 4-20φ bars

$$A_g = 400 \times 400 = 160{,}000 \text{ mm}^2$$
$$A_{sc} = 4 \times 314 = 1{,}256 \text{ mm}^2 \quad (0.79\%)$$
$$A_c = 160{,}000 - 1{,}256 = 158{,}744 \text{ mm}^2$$
$$P_u = 0.4 \times 25 \times 158{,}744 + 0.67 \times 415 \times 1{,}256$$
$$P_u = 1{,}587{,}440 + 349{,}273 = 1{,}936{,}713 \text{ N} = 1{,}937 \text{ kN}$$

```python
import math
from structural_lib.codes.is456.column.axial import short_axial_capacity

result = short_axial_capacity(
    fck=25,
    fy=415,
    Ag_mm2=400 * 400,           # 160,000 mm²
    Asc_mm2=4 * math.pi * 20**2 / 4,  # 4-20φ = 1257 mm²
)

print(f"Axial capacity: {result.Pu_kN:.0f} kN")
print(f"Steel ratio: {result.steel_ratio:.2%}")
print(f"Warnings: {result.warnings}")
```

Note the library also checks steel ratio limits: min 0.8%, max 4% (Cl 26.5.3.1). If your steel ratio is below 0.8%, you'll get a warning — the column doesn't have enough reinforcement for ductility.

---

### 5. Uniaxial Bending — The P-M Interaction Curve

This is the **most important concept in column design**. When a column carries both axial load P and moment M, the capacity isn't a single number — it's a **curve** showing all valid (P, M) combinations.

> **Think of it like...** a performance envelope for a car. At zero speed, you can carry maximum cargo (pure axial). At maximum speed, you can carry zero cargo (pure bending). Between those extremes, there's a curve showing valid speed-cargo combinations. For any (speed, cargo) point inside the curve, the car is safe. Outside = failure.

**IS 456 Cl 39.5** — The P-M interaction envelope has these key points:

```
        Pu (kN)
        ↑
   Pu,0 ●━━━━━━━━━━━         ← Pure axial (M=0): Cl 39.3 formula
        ┃           ╲
        ┃            ╲
        ┃             ╲       ← Compression-controlled zone
   Pb   ┃ · · · · · · ·●     ← Balanced point (both materials yield)
        ┃             ╱
        ┃            ╱        ← Tension-controlled zone
        ┃           ╱
     0  ●━━━━━━━━━●━━━━━→ Mu (kNm)
                  Mu,0        ← Pure bending (P=0): like beam flexure
```

**Key points on the curve:**

1. **Pure axial** ($P_{u,0}$, $M = 0$) — Maximum axial load, no bending. This is Cl 39.3.
2. **Balanced point** ($P_b$, $M_b$) — Both concrete and steel reach their limits simultaneously. Maximum moment capacity occurs near here.
3. **Pure bending** ($P = 0$, $M_{u,0}$) — No axial load, just bending. This is basically beam flexure.

For any applied load combination ($P_u$, $M_u$):
- **Inside the curve** → **SAFE** ✅
- **On the curve** → At capacity (utilization = 1.0)
- **Outside the curve** → **UNSAFE** ❌

Our library generates the full interaction curve by sweeping the neutral axis position from 0 to infinity:

```python
from structural_lib.codes.is456.column.uniaxial import pm_interaction_curve

pm = pm_interaction_curve(
    b_mm=400,
    D_mm=400,
    fck=25,
    fy=415,
    Asc_mm2=4 * 314,    # 4-20φ = 1256 mm²
    d_prime_mm=50,       # cover to steel centroid
)

print(f"Pure axial capacity: {pm.Pu_0_kN:.0f} kN")
print(f"Pure moment capacity: {pm.Mu_0_kNm:.1f} kNm")
print(f"Balanced point: P={pm.Pb_kN:.0f} kN, M={pm.Mb_kNm:.1f} kNm")
print(f"Envelope has {len(pm.points)} points")

# Check a specific load combination:
from structural_lib.codes.is456.column.uniaxial import design_short_column_uniaxial

result = design_short_column_uniaxial(
    Pu_kN=800,
    Mu_kNm=120,
    b_mm=400,
    D_mm=400,
    le_mm=1950,          # effective length
    fck=25,
    fy=415,
    Asc_mm2=1256,
    d_prime_mm=50,
)
print(f"Safe? {result.is_safe}")
print(f"Utilization: {result.utilization:.2f}")  # < 1.0 means safe
```

The utilization ratio is the **radial distance** from the origin to the applied point, divided by the distance from the origin to the curve. Under 1.0 = inside the curve = safe.

The library uses **SP:16 Table I** coefficients for the stress block when the neutral axis falls outside the section ($x_u > D$), which happens at high axial loads. This is a lookup + interpolation approach from the Design Aids handbook — the same approach practicing engineers use.

---

### 6. Biaxial Bending — Real Columns Bend Both Ways

In a real building, a corner column gets moments from beams on **two perpendicular** axes — $M_{ux}$ about the x-axis and $M_{uy}$ about the y-axis. This is **biaxial bending**.

**IS 456 Cl 39.6** uses the **Bresler load contour formula:**

$$\left(\frac{M_{ux}}{M_{ux1}}\right)^{\alpha_n} + \left(\frac{M_{uy}}{M_{uy1}}\right)^{\alpha_n} \leq 1.0$$

Where:
- $M_{ux}$, $M_{uy}$ = applied moments about each axis
- $M_{ux1}$ = uniaxial moment capacity about x-axis at the applied $P_u$ (from the P-M curve)
- $M_{uy1}$ = uniaxial moment capacity about y-axis at the applied $P_u$ (from the P-M curve)
- $\alpha_n$ = exponent that depends on $P_u / P_{uz}$

**The $\alpha_n$ exponent** (IS 456 Cl 39.6):

$$\alpha_n = \begin{cases} 1.0 & \text{if } P_u/P_{uz} \leq 0.2 \\ 2.0 & \text{if } P_u/P_{uz} \geq 0.8 \\ 1.0 + \frac{P_u/P_{uz} - 0.2}{0.6} & \text{between} \end{cases}$$

Where $P_{uz}$ = **pure crush capacity** = $0.45 f_{ck} A_c + 0.75 f_y A_{sc}$ (Cl 39.6a)

> **Think of it like...** a health score with two dimensions. Imagine your CPU is at 60% ($M_{ux}/M_{ux1}$) and your memory is at 70% ($M_{uy}/M_{uy1}$). Independently, both are fine. But *combined*, the server might crash. Bresler's formula is the check: $(0.6)^{\alpha_n} + (0.7)^{\alpha_n} \leq 1.0$?

**Why the exponent varies:** When $P_u$ is small relative to $P_{uz}$, the failure surface is more like a straight line ($\alpha_n = 1$, conservative diamond shape). When $P_u$ is large, the surface is more like a circle ($\alpha_n = 2$, less conservative).

```python
from structural_lib.codes.is456.column.biaxial import biaxial_bending_check

result = biaxial_bending_check(
    Pu_kN=1000,
    Mux_kNm=80,          # moment about x-axis
    Muy_kNm=60,          # moment about y-axis
    b_mm=400,             # width (perpendicular to x-axis bending)
    D_mm=400,             # depth (in x-axis bending direction)
    le_mm=1950,
    fck=25,
    fy=415,
    Asc_mm2=4 * 314,     # symmetric: half on each face
    d_prime_mm=50,
    l_unsupported_mm=3000,
)

print(f"Safe? {result.is_safe}")
print(f"Interaction ratio: {result.interaction_ratio:.3f}")  # must be <= 1.0
print(f"Alpha_n: {result.alpha_n:.2f}")
print(f"Mux1: {result.Mux1_kNm:.1f} kNm")  # uniaxial capacity about x
print(f"Muy1: {result.Muy1_kNm:.1f} kNm")  # uniaxial capacity about y
```

The library internally:
1. Generates P-M curves for **both** axes (using `pm_interaction_curve`)
2. Interpolates each curve at the applied $P_u$ to get $M_{ux1}$ and $M_{uy1}$
3. Calculates $P_{uz}$ and $\alpha_n$
4. Evaluates the Bresler formula

This is a significant computation — the library does about 400 stress-block calculations (200 per axis) to generate the two envelopes.

---

### 7. Slender Columns — The P-Delta Effect

When $l_e/D \geq 12$, the column is **slender**. This matters because:

As a slender column deflects under load, the axial load $P$ acts at an eccentricity equal to the lateral deflection $\delta$. This creates an **additional moment** $P \times \delta$, which causes more deflection, which causes more moment... This is the **P-delta effect**.

**IS 456 Cl 39.7.1** — Additional moment method:

$$M_{add} = P_u \times e_{add}$$

Where the additional eccentricity:

$$e_{add} = \frac{D}{2000} \times \left(\frac{l_e}{D}\right)^2$$

**Example:** Slender column, $P_u$ = 1500 kN, $l_e$ = 6000 mm, $D$ = 400 mm:

$$\frac{l_e}{D} = \frac{6000}{400} = 15 \geq 12 \implies \text{Slender}$$

$$e_{add} = \frac{400}{2000} \times 15^2 = 0.2 \times 225 = 45 \text{ mm}$$

$$M_{add} = 1500 \times 0.045 = 67.5 \text{ kNm}$$

This additional moment gets **added** to the primary moment from frame analysis. So if the frame analysis gives $M_u = 100$ kNm, the total design moment becomes $100 + 67.5 = 167.5$ kNm — a 67% increase! This is why slender columns are expensive and engineers try to avoid them.

> **Think of it like...** compound interest on technical debt. A small deflection (initial "debt") generates additional moment ("interest"), which causes more deflection ("more debt"), in a feedback loop. The additional moment formula is IS 456's way of accounting for this without solving the nonlinear equation iteratively.

---

### 8. Column Detailing — Cl 26.5.3

Like beams, columns have detailing rules that ensure the design is actually buildable and performs as intended.

**Key rules (IS 456 Cl 26.5.3):**

| Rule | Requirement | Why |
|------|------------|-----|
| Min bars | 4 (rectangular), 6 (circular) | Restrain ties at corners |
| Min bar dia | 12 mm | Practical minimum for handling |
| Min steel | 0.8% of $A_g$ | Prevent brittle failure |
| Max steel | 4% of $A_g$ (6% at lap) | Constructability — bars must fit |
| Tie spacing | min(16φ, 300mm, least dimension) | Prevent bar buckling |
| Tie diameter | ≥ φ/4 or 6mm | Strong enough to restrain main bars |

**Why 0.8% minimum?** Without enough steel, a column can fail suddenly — the concrete crushes before the steel yields, giving no warning. The 0.8% minimum ensures some ductility.

**Why 4% maximum?** With more than 4% steel, the bars physically can't fit with proper spacing. At laps (where two bars overlap), the effective steel area doubles temporarily — hence the 6% allowance. But designing for > 4% is a sign the column is too small.

---

## 🏗️ Library Examples

### Example 1: Full Axial Design Workflow

```python
import math
from structural_lib.codes.is456.column.axial import (
    effective_length,
    classify_column,
    min_eccentricity,
    short_axial_capacity,
)
from structural_lib.core.data_types import EndCondition

# Step 1: Column geometry
b, D = 400, 400          # mm (square column)
l_unsup = 3200           # mm (clear height between floors)

# Step 2: Effective length
le = effective_length(l_mm=l_unsup, end_condition=EndCondition.FIXED_FIXED)
print(f"Effective length: {le} mm")  # 3200 x 0.65 = 2080 mm

# Step 3: Classify
cls = classify_column(le_mm=le, D_mm=D)
print(f"Column type: {cls}")  # SHORT (2080/400 = 5.2 < 12)

# Step 4: Minimum eccentricity
e_min = min_eccentricity(l_unsupported_mm=l_unsup, D_mm=D)
print(f"Min eccentricity: {e_min} mm")

# Step 5: Axial capacity
Ag = b * D
Asc = 8 * math.pi * 16**2 / 4  # 8-16φ = 1608 mm²
result = short_axial_capacity(fck=25, fy=415, Ag_mm2=Ag, Asc_mm2=Asc)
print(f"Capacity: {result.Pu_kN:.0f} kN")
print(f"Steel ratio: {result.steel_ratio:.2%}")
```

### Example 2: P-M Interaction Curve

```python
from structural_lib.codes.is456.column.uniaxial import pm_interaction_curve

pm = pm_interaction_curve(
    b_mm=300, D_mm=500, fck=30, fy=500,
    Asc_mm2=6 * 314,      # 6-20φ
    d_prime_mm=50,
)

# The curve has ~200 points for smooth plotting
print(f"Points on curve: {len(pm.points)}")
print(f"Pure axial: Pu,0 = {pm.Pu_0_kN:.0f} kN")
print(f"Pure bending: Mu,0 = {pm.Mu_0_kNm:.1f} kNm")
print(f"Balanced: Pb = {pm.Pb_kN:.0f} kN, Mb = {pm.Mb_kNm:.1f} kNm")

# You can extract points for plotting:
P_values = [p[0] for p in pm.points]  # kN
M_values = [p[1] for p in pm.points]  # kNm
# Plot with matplotlib, plotly, or pass to React frontend
```

### Example 3: Biaxial Bending Check

```python
from structural_lib.codes.is456.column.biaxial import biaxial_bending_check

# Corner column with moments from two perpendicular beams
result = biaxial_bending_check(
    Pu_kN=1200,
    Mux_kNm=95,
    Muy_kNm=70,
    b_mm=400, D_mm=500,
    le_mm=2400,
    fck=30, fy=415,
    Asc_mm2=8 * 314,     # 8-20φ, symmetric
    d_prime_mm=55,
    l_unsupported_mm=3500,
)

print(f"Interaction ratio: {result.interaction_ratio:.3f}")
print(f"Safe? {result.is_safe}")   # True if ratio <= 1.0
print(f"Alpha_n = {result.alpha_n:.2f}")
print(f"Mux1 = {result.Mux1_kNm:.1f} kNm (capacity about x at Pu)")
print(f"Muy1 = {result.Muy1_kNm:.1f} kNm (capacity about y at Pu)")
```

---

## 🎯 Simple Hand Calculation Practice

### Hand Calc 1: Effective Length

**Given:** Column 3.6 m clear height, both ends fixed in position but one end free to rotate.

From IS 456 Table 28 (case: fixed-hinged):

$$l_e = 0.80 \times l = 0.80 \times 3600 = 2880 \text{ mm}$$

### Hand Calc 2: Minimum Eccentricity

**Given:** Column 350 mm wide, 4200 mm unsupported length.

$$e_{\min} = \frac{l_{\text{unsup}}}{500} + \frac{D}{30}$$

$$e_{\min} = \frac{4200}{500} + \frac{350}{30} = 8.4 + 11.67 = 20.07 \text{ mm}$$

Check floor: $e_{\min} \geq 20$ mm. Here 20.07 > 20 mm ✔️, so $e_{\min} = 20.07$ mm.

### Hand Calc 3: Axial Capacity of Short Column

**Given:** 350 × 350 mm column, M30 concrete, Fe415 steel, 4−16φ + 4−12φ bars.

Steel area:

$$A_{sc} = 4 \times \frac{\pi \times 16^2}{4} + 4 \times \frac{\pi \times 12^2}{4} = 804.2 + 452.4 = 1256.6 \text{ mm}^2$$

Gross area: $A_g = 350 \times 350 = 122500$ mm²

Steel ratio check: $p = 1256.6 / 122500 = 1.03\%$ (OK: 0.8% < 1.03% < 6%)

IS 456 Cl 39.3 capacity:

$$P_u = 0.4 \cdot f_{ck} \cdot (A_g - A_{sc}) + 0.67 \cdot f_y \cdot A_{sc}$$

$$P_u = 0.4 \times 30 \times (122500 - 1256.6) + 0.67 \times 415 \times 1256.6$$

$$P_u = 12 \times 121243.4 + 278.05 \times 1256.6$$

$$P_u = 1{,}454{,}921 + 349{,}397 = 1{,}804{,}318 \text{ N} = 1804.3 \text{ kN}$$

### Hand Calc 4: Biaxial Interaction Check (Bresler Concept)

**Given:** From P-M analysis, at $P_u = 1000$ kN:
- Uniaxial capacity about x: $M_{ux1} = 180$ kNm
- Uniaxial capacity about y: $M_{uy1} = 140$ kNm
- Applied: $M_{ux} = 80$ kNm, $M_{uy} = 60$ kNm
- $P_u / P_{uz} = 0.45$, so $\alpha_n = 1.50$ (interpolated)

Check:

$$\left(\frac{M_{ux}}{M_{ux1}}\right)^{\alpha_n} + \left(\frac{M_{uy}}{M_{uy1}}\right)^{\alpha_n} \leq 1.0$$

$$\left(\frac{80}{180}\right)^{1.50} + \left(\frac{60}{140}\right)^{1.50}$$

$$= 0.444^{1.50} + 0.429^{1.50} = 0.296 + 0.281 = 0.577$$

Since $0.577 \leq 1.0$ — the column is **SAFE** under biaxial bending.

---

## 🔧 Exercise: Design-Check a Real Column

**Problem:** A 450 × 450 mm interior column in a 5-storey building.

| Parameter | Value |
|-----------|-------|
| Width × Depth | 450 × 450 mm |
| Unsupported length | 3600 mm |
| Concrete | M25 (fck = 25 N/mm²) |
| Steel | Fe415 (fy = 415 N/mm²) |
| Reinforcement | 8−20φ bars (one at each corner + 1 midway each face) |
| End condition | Fixed–Fixed |
| Factored axial load | Pu = 2000 kN |
| Moment about x | Mux = 100 kNm |
| Moment about y | Muy = 75 kNm |
| Cover | 40 mm + 8 mm ties + ½ bar = 58 mm |

**Tasks:**

1. **Calculate effective length.** What is the slenderness ratio? Is the column short or slender?

2. **Compute minimum eccentricity.** Does the applied eccentricity exceed the minimum?

3. **Find axial capacity.** What is $P_u$ from Cl 39.3? Is axial load alone sufficient?

4. **Check biaxial bending.** Using Bresler, does the column pass the interaction check?

5. **Verify with the library:**

```python
import math
from structural_lib.codes.is456.column.axial import (
    effective_length, classify_column, min_eccentricity, short_axial_capacity
)
from structural_lib.codes.is456.column.biaxial import biaxial_bending_check
from structural_lib.core.data_types import EndCondition

# Geometry
b, D = 450, 450
l_unsup = 3600
d_prime = 58  # cover + tie + half bar

# Step 1: Effective length & classification
le = effective_length(l_mm=l_unsup, end_condition=EndCondition.FIXED_FIXED)
cls = classify_column(le_mm=le, D_mm=D)
print(f"le = {le} mm, le/D = {le/D:.1f}, Type = {cls}")

# Step 2: Min eccentricity
e_min = min_eccentricity(l_unsupported_mm=l_unsup, D_mm=D)
print(f"e_min = {e_min:.1f} mm")

# Step 3: Axial capacity
Ag = b * D
Asc = 8 * math.pi * 20**2 / 4  # 8-20phi = 2513 mm2
cap = short_axial_capacity(fck=25, fy=415, Ag_mm2=Ag, Asc_mm2=Asc)
print(f"Axial capacity = {cap.Pu_kN:.0f} kN (demand = 2000 kN)")

# Step 4: Biaxial check
bi = biaxial_bending_check(
    Pu_kN=2000, Mux_kNm=100, Muy_kNm=75,
    b_mm=b, D_mm=D, le_mm=le,
    fck=25, fy=415,
    Asc_mm2=Asc, d_prime_mm=d_prime,
    l_unsupported_mm=l_unsup,
)
print(f"Interaction ratio = {bi.interaction_ratio:.3f}")
print(f"Safe? {bi.is_safe}")
```

**Expected answers (approximate):**
- le = 2340 mm, le/D = 5.2 → **SHORT**
- e_min ~ 22.2 mm
- Axial capacity ~ 2800+ kN > 2000 kN → OK for pure axial
- Biaxial ratio < 1.0 → **SAFE**

---

## 💬 Can You Explain?

Test your understanding. Try to answer in 2–3 sentences:

1. **Why is the effective length factor for "fixed-fixed" only 0.65, not 1.0?**
   A perfectly fixed end provides both translation *and* rotation restraint, so the buckled shape has inflection points within the member. The distance between inflection points is shorter than the physical length, reducing the effective length.

2. **A column has le/D = 11.9. Your colleague says it's "short." Are they right?**
   Borderline! IS 456 Cl 25.1.2 defines short as le/D < 12 for a braced column. 11.9 < 12, so technically short, but this close to the limit you should check additional moment effects as a precaution. Good engineers don't rely on razor-thin margins.

3. **Why does the P-M interaction curve bulge outward below the balance point?**
   Below the balance point, axial compression helps the moment capacity — the concrete compressive zone is larger and can resist more bending. Above the balance point, the compression zone is already large and adding more axial load causes crushing before the steel yields, so moment capacity decreases.

4. **When is biaxial bending most critical — corner, edge, or interior columns?**
   Corner columns are worst because they receive beams from two perpendicular directions with no compensating span on the other side. Edge columns may have significant moment about one axis. Interior columns often have roughly balanced moments if spans are equal.

5. **Why does IS 456 impose e_min >= 20 mm even for short axially loaded columns?**
   Perfect axial loading doesn't exist in reality. Construction tolerances, non-uniform concrete placement, and load eccentricities from beam reactions always introduce some moment. The 20 mm floor ensures the design accounts for unavoidable real-world imperfections.

---

## Summary

| # | Concept | Key Formula / Value | Library Function |
|---|---------|--------------------|-----------------|
| 1 | Effective length | $l_e = k \times l$ (Table 28) | `effective_length()` |
| 2 | Short vs Slender | $l_e/D < 12$ (braced) | `classify_column()` |
| 3 | Min eccentricity | $l/500 + D/30 \geq 20$ mm | `min_eccentricity()` |
| 4 | Axial capacity | $0.4 f_{ck}(A_g - A_{sc}) + 0.67 f_y A_{sc}$ | `short_axial_capacity()` |
| 5 | P-M interaction | SP:16 envelope curve | `pm_interaction_curve()` |
| 6 | Uniaxial design | Strain-compatibility method | `design_short_column_uniaxial()` |
| 7 | Biaxial check | $(M_{ux}/M_{ux1})^{\alpha_n} + (M_{uy}/M_{uy1})^{\alpha_n} \leq 1$ | `biaxial_bending_check()` |
| 8 | Slender columns | Additional moment $M_a = P_u \cdot e_a$ | Cl 39.7.1 |
| 9 | Ties spacing | $\leq 16\phi, 48\phi_t, 300$ mm | Cl 26.5.3.2 |
| 10 | Steel ratio | $0.8\% \leq p \leq 6\%$ | Cl 26.5.3.1 |

---

## 📎 References

- **IS 456:2000** — Cl 25 (General Requirements), Cl 39 (Design), Cl 26.5.3 (Detailing)
- **SP:16 Design Aids** — Interaction diagrams (Charts 27–62)
- **IS 13920:2016** — Seismic ductile detailing of RC columns
- **Pillai & Menon** (8th Ed.) — Ch. 13–14: Column design with solved examples
- **N. Krishna Raju** (4th Ed.) — Ch. 11: Short and slender column design
- **Paulay & Priestley** — Seismic design of RC structures, column ductility

---

## What's Next?

**Day 6: Footings** moves from vertical members to the foundation system, covering sizing, bearing, flexure, one-way shear, and punching shear.

[<< Day 4: Beam Detailing & Serviceability](day-04-beam-detailing.md) | [Day 6: Footings >>](day-06-footings.md)
