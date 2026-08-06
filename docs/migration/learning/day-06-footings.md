# Day 6: Footing Design (IS 456 Cl 34, Cl 31.6)

**Type:** Guide
**Audience:** Developers, Students
**Status:** Active
**Importance:** High
**Created:** 2026-04-08
**Last Updated:** 2026-04-08

**Prerequisites:** [Day 1](day-01-concrete-basics.md) (materials), [Day 3](day-03-beam-shear-torsion.md) (shear concepts)
**Library files:** `Python/structural_lib/codes/is456/footing/` — bearing.py, flexure.py, one_way_shear.py, punching_shear.py
**IS 456 clauses:** Cl 34.1 (Sizing), Cl 34.2.3.1 (Flexure), Cl 34.2.4.1 (One-way shear), Cl 31.6.1 (Punching shear), Cl 34.4 (Bearing stress)

---

## What You’ll Learn Today

By the end of this module you’ll understand:
- What a footing is and why buildings need them
- How to size a footing from soil bearing capacity
- Two completely different shear failure modes (beam shear vs punching)
- How to design flexural reinforcement in a footing
- How eccentricity changes the pressure distribution under a footing
- How the library’s `footing/` subpackage maps to each IS 456 clause

---

## 📖 Theory

### 1. What is a Footing?

A column might carry 500 kN of load, concentrated on a 300×300 mm cross-section. That’s a pressure of about 5.6 N/mm² (5,600 kPa). Most soils can handle maybe 150–300 kPa before they start sinking. So we need something to **spread the load** over a much wider area.

That’s what a footing does. It’s a thick slab of concrete at the base of a column that distributes the concentrated column load over enough soil area to keep the pressure safe.

> **Think of it like...** shoes. You can walk barefoot on soft sand, but your feet sink in. Strap on wide snowshoes, and suddenly you float on the surface. A footing is a snowshoe for a column — it spreads the weight so the soil doesn’t sink.

```
         Column (300×300)
             |   |
    ╔════════╪═══╪════════╗
    ║                     ║  ← Footing (1500×1500)
    ╚═════════════════════╝
    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ← Soil
```

### 2. Types of Footings

| Type | When to Use | Our Library? |
|------|-------------|-------------|
| **Isolated (spread)** | Single column, enough space | ✅ Yes |
| **Combined** | Two columns close together | ❌ Not yet |
| **Strip (continuous)** | Wall or line of columns | ❌ Not yet |
| **Raft (mat)** | Entire building, poor soil | ❌ Not yet |
| **Pile cap** | Very weak or deep soil | ❌ Not yet |

Our library covers **isolated spread footings** — both square and rectangular. This is the most common type for individual column foundations in typical buildings.

---

### 3. Safe Bearing Capacity (SBC)

Before you can design the concrete, you need to know what the **soil** can handle. This is expressed as the **Safe Bearing Capacity (SBC)**, typically in kPa (= kN/m²).

| Soil Type | Typical SBC (kPa) |
|-----------|-------------------|
| Soft clay | 50–100 |
| Medium clay | 100–200 |
| Stiff clay | 150–300 |
| Loose sand | 100–150 |
| Dense sand | 200–400 |
| Gravel | 300–500 |
| Soft rock | 400–1000 |
| Hard rock | > 1000 |

> **Key fact:** The SBC is determined by a geotechnical engineer through soil testing (plate load test, SPT, etc.). Our library takes it as an **input** — we don’t calculate it.
### 4. Sizing the Footing — Cl 34.1

This is the first step and uses **service (unfactored) loads**. IS 456 Cl 34.1 is explicit about this:

> *“In calculating the bearing pressure ... the loads and reactions shall be taken as the service values.”*

The logic is simple:

$$A_{required} = \frac{P_{service}}{q_{safe}}$$

For a square footing: $L = B = \sqrt{A_{required}}$

Then round up to the nearest 50 mm for constructability.

**Important distinction:** Sizing uses **service loads**, but all subsequent structural design (flexure, shear) uses **factored loads**. This trips up many students.

### 5. Pressure Distribution

How the soil pushes back depends on whether the load is centered:

**Concentric load (e = 0):**
$$q = \frac{P}{A} \quad \text{(uniform pressure)}$$

**Eccentric load (e ≤ L/6):**
$$q_{max, min} = \frac{P}{A}\left(1 \pm \frac{6e}{L}\right) \quad \text{(trapezoidal)}$$

**Large eccentricity (e > L/6):**
Part of the footing lifts off — the soil can’t pull downward! The pressure distribution becomes triangular, and we need a wider footing.

```
 Concentric        Eccentric (e ≤ L/6)     Eccentric (e > L/6)
 |██████████|      |██████████|         |██████|
 |██████████|      |████████  |         |████  |
 |██████████|      |██████    |         |██    |
   uniform           trapezoidal          partial contact
```

---

### 6. One-Way (Beam) Shear — Cl 34.2.4.1

This is exactly the same concept as beam shear from Day 3 — the footing acts like a wide, short cantilever beam.

**Critical section:** at distance **d** from the column face.

$$\tau_v = \frac{V_u}{b \times d}$$

Where $V_u$ is the upward soil reaction on the footing area **beyond** the critical section:

$$V_u = q_u \times B \times \left(\frac{L - a}{2} - d\right)$$

The check: $\tau_v \leq \tau_c$ (from IS 456 Table 19, same as beams).

> **Both directions matter.** Unlike a beam (which has one shear direction), a footing must be checked in **both** the L-direction and B-direction. The library does this automatically.

```
     ┌───┬─┬─┬───┐
     │   │ │ │   │
     │   │ │ │   │
     └───┴─┴─┴───┘
     |←d→|col|←d→|
     critical sections
```

---

### 7. Two-Way (Punching) Shear — Cl 31.6.1

This is the failure mode **unique to footings and slabs**. The column doesn’t slide the footing apart in one direction — it tries to **punch straight through** it, like a hole punch through paper.

**Critical perimeter:** at distance **d/2** from the column face, forming a rectangle around the column.

$$b_0 = 2 \times \left[(a + d) + (b + d)\right]$$

**Shear force:** Total load minus the soil reaction inside the punching perimeter:

$$V_u = P_u - q_u \times (a + d)(b + d)$$

**Nominal shear stress:**

$$\tau_v = \frac{V_u}{b_0 \times d}$$

**Permissible stress:**

$$\tau_c = k_s \times 0.25 \times \sqrt{f_{ck}}$$

Where $k_s = \min(1.0, \; 0.5 + \beta_c)$ and $\beta_c$ is the ratio of the short side to the long side of the column.

> **Why ks?** A rectangular column concentrates shear stress at the short-side face. The $k_s$ factor reduces the permissible stress for elongated columns (βc ≪ 1) to account for this non-uniform distribution.

> **Critical difference from beam shear:** If punching shear fails, you **can’t add stirrups** (unlike beams). The only fixes are: increase footing depth, increase footing size, or use a pedestal. That’s why punching shear is often the governing check.

```
     ┌─────────────────┐
     │    ┌───────┐    │ ← Punching perimeter (d/2 from column)
     │    │ ┌───┐ │    │
     │    │ │col│ │    │
     │    │ └───┘ │    │
     │    └───────┘    │
     └─────────────────┘ ← Footing edge
```

---

### 8. Flexure in Footings — Cl 34.2.3.1

A footing bends because the soil pushes up uniformly, but the column pushes down in the center. The footing acts as a **cantilever** from the column face.

**Critical section for moment:** at the **face** of the column.

For the L-direction:
$$M_u = q_u \times B \times \frac{\text{cant}_L^2}{2}$$

Where $\text{cant}_L = (L - a)/2$ is the cantilever projection.

Then use the standard flexure formula (Day 2) to find the required steel area $A_{st}$.

> **Both directions again.** The footing needs steel **in both directions** — bottom bars running both ways, forming a grid. For rectangular footings, IS 456 Cl 34.3.1 requires a fraction $2/(\beta+1)$ of the short-direction steel to be concentrated in a central band (where $\beta = L/B$).

**Minimum steel:** 0.12% for HYSD bars (Fe 415/500), 0.15% for mild steel (Fe 250) — same as slabs (Cl 26.5.2.1).

---

## 🏗️ Library Examples

### Sizing a Footing

```python
from structural_lib.codes.is456.footing.bearing import size_footing
from structural_lib.core.data_types import FootingType

# Column: 300x400mm, service load 600 kN, soil SBC 200 kPa
result = size_footing(
    P_service_kN=600,
    q_safe_kPa=200,
    a_mm=300,
    b_mm=400,
    footing_type=FootingType.ISOLATED_SQUARE,
)

print(f"Footing size: {result.L_mm} x {result.B_mm} mm")
print(f"Max bearing pressure: {result.q_max_kPa:.1f} kPa (safe: {result.q_safe_kPa})")
print(f"Safe? {result.is_safe}")
# Footing size: 1750 x 1750 mm  (rounded up to nearest 50mm)
```

### Eccentric Footing

```python
# Same column, but with 40 kN·m moment
result = size_footing(
    P_service_kN=600,
    q_safe_kPa=200,
    a_mm=300,
    b_mm=400,
    M_service_kNm=40.0,
    footing_type=FootingType.ISOLATED_RECTANGULAR,
)

print(f"Pressure type: {result.pressure_type}")
print(f"q_max: {result.q_max_kPa:.1f}, q_min: {result.q_min_kPa:.1f} kPa")
# Pressure type: trapezoidal
```

### Punching Shear Check

```python
from structural_lib.codes.is456.footing.punching_shear import footing_punching_shear

# Factored load: 900 kN (= 1.5 x 600), footing 1750x1750, d=400mm
result = footing_punching_shear(
    Pu_kN=900,
    L_mm=1750,
    B_mm=1750,
    d_mm=400,
    a_mm=300,
    b_mm=400,
    fck=25,
)

print(f"τv = {result.tau_v_nmm2:.3f} N/mm²")
print(f"τc = {result.tau_c_nmm2:.3f} N/mm²")
print(f"Punching safe? {result.is_safe}")
print(f"ks = {result.ks:.3f} (βc = {result.beta_c:.3f})")
```

### One-Way Shear Check

```python
from structural_lib.codes.is456.footing.one_way_shear import footing_one_way_shear

result = footing_one_way_shear(
    Pu_kN=900,
    L_mm=1750,
    B_mm=1750,
    d_mm=400,
    a_mm=300,
    b_mm=400,
    fck=25,
    pt=0.15,  # Assumed steel percentage for Table 19 lookup
)

print(f"Governing direction: {result.governing_direction}")
print(f"τv = {result.tau_v_nmm2:.3f}, τc = {result.tau_c_nmm2:.3f}")
print(f"One-way shear safe? {result.is_safe}")
```

### Flexure Design

```python
from structural_lib.codes.is456.footing.flexure import footing_flexure

result = footing_flexure(
    Pu_kN=900,
    L_mm=1750,
    B_mm=1750,
    d_mm=400,
    a_mm=300,
    b_mm=400,
    fck=25,
    fy=415,
)

print(f"L-direction: Mu={result.Mu_L_kNm:.1f} kNm, Ast={result.Ast_L_mm2:.0f} mm²")
print(f"B-direction: Mu={result.Mu_B_kNm:.1f} kNm, Ast={result.Ast_B_mm2:.0f} mm²")
```

---

## 🎯 Simple Example: Complete Footing Design

Let’s walk through the full design sequence for a typical footing:

**Given:**
- Column: 350×350 mm
- Service load: 800 kN (no moment)
- Soil SBC: 200 kPa
- Concrete: M25, Steel: Fe415

**Step 1: Sizing (service loads)**
$$A_{req} = \frac{800}{200} = 4.0 \text{ m}^2 \implies L = B = \sqrt{4.0} = 2.0 \text{ m} = 2000 \text{ mm}$$

**Step 2: Factored load**
$$P_u = 1.5 \times 800 = 1200 \text{ kN}$$
$$q_u = \frac{1200 \times 1000}{2000 \times 2000} = 0.3 \text{ N/mm}^2$$

**Step 3: Assume effective depth d = 450 mm**

**Step 4: Punching shear check**

Critical perimeter at d/2:
$$b_0 = 2[(350 + 450) + (350 + 450)] = 3200 \text{ mm}$$

Punching area:
$$(350 + 450)(350 + 450) = 640{,}000 \text{ mm}^2$$

$$V_u = 1200 \times 10^3 - 0.3 \times 640{,}000 = 1{,}008{,}000 \text{ N}$$

$$\tau_v = \frac{1{,}008{,}000}{3200 \times 450} = 0.700 \text{ N/mm}^2$$

$$\tau_c = 1.0 \times 0.25 \times \sqrt{25} = 1.25 \text{ N/mm}^2$$

✅ $\tau_v < \tau_c$ — Punching shear OK.

**Step 5: One-way shear check**

Cantilever: $(2000 - 350)/2 = 825$ mm. Critical section at d from face: $825 - 450 = 375$ mm.

$$V_u = 0.3 \times 2000 \times 375 = 225{,}000 \text{ N} = 225 \text{ kN}$$

$$\tau_v = \frac{225{,}000}{2000 \times 450} = 0.250 \text{ N/mm}^2$$

For pt=0.15%, $\tau_c = 0.29$ N/mm² (Table 19, M25). ✅ Safe.

**Step 6: Flexure at column face**

$$M_u = 0.3 \times 2000 \times \frac{825^2}{2} = 204{,}187{,}500 \text{ N\cdot mm} = 204.2 \text{ kN\cdot m}$$

Use Day 2 flexure formula to find $A_{st}$ — the library’s `footing_flexure` does this internally.

---

## 🔧 Exercise

**Problem:** Design an isolated square footing for:
- Column: 400×400 mm
- Service load: 1000 kN
- Soil SBC: 150 kPa
- M25 concrete, Fe415 steel

Questions:
1. What is the required footing size?
2. What factored pressure $q_u$ acts on the footing?
3. Is punching shear safe with d = 500 mm?
4. What is the bending moment at the column face?

<details>
<summary>💡 Hints</summary>

1. $A = 1000/150 = 6.67$ m² → $L = \sqrt{6.67} = 2.58$ m → round up to 2600 mm
2. $P_u = 1.5 \times 1000 = 1500$ kN; $q_u = 1500 \times 10^3 / (2600 \times 2600)$
3. Check $\tau_v$ against $k_s \times 0.25 \sqrt{f_{ck}}$. Since column is square, $\beta_c = 1$, $k_s = 1.0$
4. Cantilever = $(2600 - 400)/2 = 1100$ mm; $M_u = q_u \times 2600 \times 1100^2/2$
</details>

---

## 💬 Can You Explain?

Test your understanding:

1. **Why does footing sizing use service loads, but structural design uses factored loads?**
   (Because SBC already includes a factor of safety from the geotechnical engineer. Applying load factors on top would be double-counting safety.)

2. **Why is punching shear more dangerous than one-way shear?**
   (Because you can’t add shear reinforcement for punching in footings. If it fails, your only options are increasing depth or size.)

3. **Why does a rectangular column need the $k_s$ factor for punching?**
   (The shear stress isn’t uniform around the critical perimeter — it concentrates near the short side. $k_s$ reduces the permissible stress to account for this.)

4. **What happens if eccentricity exceeds L/6?**
   (Part of the footing base loses contact with the soil. The pressure distribution becomes triangular with one edge at zero. If eccentricity is too large, the footing overturns.)

---

## Summary — What You Now Know

| Concept | Formula | Library Function |
|---------|---------|------------------|
| Footing sizing | $A = P_{service} / q_{safe}$ | `size_footing()` |
| Bearing pressure (concentric) | $q = P/A$ | `size_footing()` |
| Bearing pressure (eccentric) | $q = P/A (1 \pm 6e/L)$ | `size_footing(M_service_kNm=...)` |
| Punching perimeter | $b_0 = 2[(a+d)+(b+d)]$ | `footing_punching_shear()` |
| Punching stress | $\tau_v = V_u / (b_0 \times d)$ | `footing_punching_shear()` |
| Punching capacity | $\tau_c = k_s \times 0.25\sqrt{f_{ck}}$ | `footing_punching_shear()` |
| One-way shear | $\tau_v = V_u / (b \times d)$ at d from face | `footing_one_way_shear()` |
| Footing moment | $M_u = q_u \times B \times cant^2/2$ | `footing_flexure()` |
| Steel distribution (rect.) | $2/(\beta+1)$ in central band | `footing_flexure()` |
| Bearing enhancement | $\sqrt{A_1/A_2} \leq 2.0$ | `bearing_stress_enhancement()` |

---

## 📎 References

- **IS 456:2000** — Cl 34.1 (General), Cl 34.2.3.1 (Flexure at column face), Cl 34.2.4.1 (One-way shear), Cl 31.6.1 (Punching shear), Cl 34.3.1 (Steel distribution), Cl 34.4 (Bearing stress)
- **SP:16** — Tables for τc (Table 19), permissible stresses
- **Library source:** `Python/structural_lib/codes/is456/footing/` (bearing.py, flexure.py, one_way_shear.py, punching_shear.py)
- **Data types:** `Python/structural_lib/core/data_types.py` (FootingBearingResult, FootingPunchingResult, FootingOneWayShearResult, FootingFlexureResult)

---

## What’s Next?

**Day 7: IS 456 Big Picture & Clause Navigation** — We’ll step back from individual calculations and look at IS 456 as a whole. You’ll learn how the standard is organized, how our library’s clause traceability system maps 93+ functions to 119 clauses, and where IS 456 sits among international codes. Think of Day 7 as your navigation guide to the entire standard.
