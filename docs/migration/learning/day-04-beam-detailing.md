# Day 4: Beam Detailing & Serviceability

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** Critical
**Created:** 2026-04-08
**Last Updated:** 2026-04-08
**Prerequisites:** Day 1 (materials), Day 2 (flexure), Day 3 (shear & torsion)
**Library files:** `Python/structural_lib/codes/is456/beam/detailing.py`, `Python/structural_lib/codes/is456/beam/serviceability.py`, `Python/structural_lib/services/bbs.py`
**IS 456 Clauses:** Cl 23.2, Cl 26.2, Cl 26.3, Cl 26.4, Cl 26.5, Cl 43, Annex C, Annex F, Table 16/16A

---

## What You'll Learn Today

By the end of this module you'll understand:
- Why concrete cover exists and how to pick the right thickness
- Bar spacing rules — why you can't just shove bars anywhere
- Development length — how bars "grip" the concrete
- Anchorage — what happens when you can't get enough straight length
- Minimum and maximum reinforcement limits
- Crack width control — why cracks are normal but wide cracks are dangerous
- Deflection checks using span/depth ratios
- Bar Bending Schedules — the construction site's "API contract"

---

## 📖 Theory

### 1. Clear Cover — The Phone Case for Rebar

In Days 2 and 3 you designed steel to resist bending and shear. But how do you protect that steel from the outside world? That's what **clear cover** does.

> **Think of it like...** a phone case. Your phone (steel rebar) is the expensive, functional part. The case (concrete cover) protects it from drops (fire), scratches (corrosion), and water (aggressive environments). A thin case works for mild conditions; a rugged case is needed for harsh ones.

**IS 456 Cl 26.4, Table 16** prescribes minimum cover based on exposure:

| Exposure Class | Min Cover (mm) | Real-World Example |
|---------------|---------------|-------------------|
| Mild          | 20            | Interior of a dry building |
| Moderate      | 30            | Sheltered exterior, bathroom walls |
| Severe        | 45            | Coastal area (within 5 km of sea) |
| Very Severe   | 50            | Direct sea spray, chemical plants |

Why does cover matter?
- **Corrosion protection** — Steel rusts when moisture and chlorides penetrate. More cover = longer path for corrosive agents.
- **Fire resistance** — Table 16A gives covers for fire ratings (1hr, 2hr, etc.). Concrete insulates steel from heat.
- **Bond** — Steel needs surrounding concrete to grip. Without cover, bars can split out.

The cover is measured from the **outer surface of the concrete** to the **nearest surface of the bar** (not the center). In our library, cover is an input parameter `cover` in mm.

---

### 2. Bar Spacing — Don't Pack Them Like Sardines

You've calculated that a beam needs, say, 1200 mm² of steel. You could use 4-20φ bars (4 × 314 = 1256 mm²). But will they fit?

**IS 456 Cl 26.3** sets spacing rules:

**Minimum horizontal spacing** (whichever is greatest):
- Bar diameter
- Maximum aggregate size + 5 mm
- 25 mm

**Maximum spacing** (to control cracking):
- 300 mm for main bars
- 3d or 300 mm for distribution bars (slabs)

> **Think of it like...** parking spaces. Cars (bars) need a minimum gap to open doors (for concrete to flow around each bar during pouring). Pack them too tight and the concrete can't get between them — you get voids, which are structural defects. Space them too far apart and cracks form in the concrete between bars.

Our library's `calculate_bar_spacing()` function handles this:

```python
from structural_lib.codes.is456.beam.detailing import calculate_bar_spacing

# For a 300mm wide beam, 40mm cover each side, 8mm stirrup, using 20mm bars:
# Available width = 300 - 2×(40 + 8) = 204 mm
# For 3 bars: spacing = (204 - 3×20) / (3-1) = 72 mm → OK (> 25mm)
```

If bars don't fit in one layer, the library arranges them in **multiple layers**, with a vertical gap ≥ max(bar_dia, 15mm) between layers. The `select_bar_arrangement()` function returns a `BarArrangement` dataclass with `count`, `diameter`, `spacing`, and `layers`.

---

### 3. Development Length (Ld) — How Bars Grip Concrete

This is one of the most important detailing concepts. When a bar is embedded in concrete, it transfers force through **bond stress** along its surface. The bar needs to be embedded *long enough* for the bond to develop the full strength of the bar.

> **Think of it like...** gluing two pieces of wood. A 2-cm overlap might hold for light loads, but you need a 20-cm overlap for heavy loads. The "overlap" for rebar is the **development length**.

**IS 456 Cl 26.2.1:**

$$L_d = \frac{\phi \times \sigma_s}{4 \times \tau_{bd}}$$

Where:
- $\phi$ = bar diameter (mm)
- $\sigma_s$ = stress in bar at design load = $0.87 \times f_y$ (N/mm²)
- $\tau_{bd}$ = design bond stress from IS 456 Table (depends on $f_{ck}$ and bar type)

**Bond stress values** (IS 456, for deformed bars — 60% higher than plain):

| Concrete Grade | $\tau_{bd}$ (N/mm²) |
|---------------|---------------------|
| M20 | 1.92 |
| M25 | 2.24 |
| M30 | 2.40 |
| M35 | 2.72 |
| M40 | 3.04 |

**Example:** 16φ bar, M25 concrete, Fe415 steel:

$$L_d = \frac{16 \times 0.87 \times 415}{4 \times 2.24} = \frac{5779.2}{8.96} = 645 \text{ mm}$$

That's about **40 times the bar diameter**. This is a critical number — if a bar doesn't have $L_d$ of embedment past the point where it's needed, the bar can pull out.

---

### 4. Anchorage — When Straight Length Isn't Enough

Sometimes there isn't enough room for a straight development length — the beam ends at a column face, or you need to terminate bars mid-span. That's where **hooks and bends** come in.

**IS 456 Cl 26.2.2:** Anchorage value of a standard hook or bend:
- **90° bend** — contributes $8\phi$ of anchorage length
- **Standard U-hook (180°)** — contributes $16\phi$ of anchorage length

So if you need $L_d = 645$ mm and only have 500 mm of straight length available, you add a standard hook:
- Required remaining: $645 - 500 = 145$ mm
- Hook gives: $16 \times 16 = 256$ mm → More than enough

Our library's `calculate_standard_hook()` returns a `HookDimensions` dataclass, and `check_anchorage_at_simple_support()` verifies the IS 456 formula:

$$\frac{M_1}{V} + L_0 \geq L_d$$

Where $M_1$ = moment capacity at the support, $V$ = shear at support, $L_0$ = anchorage beyond support center.

---

### 5. Minimum and Maximum Reinforcement

IS 456 sets limits on how much (and how little) steel you can put in a beam.

**Minimum steel (Cl 26.5.1.1):**

$$A_{s,min} = \frac{0.85 \times b \times d}{f_y}$$

For Fe415: $A_{s,min} \approx 0.205\%$ of $b \times d$

*Why a minimum?* If you put too little steel, the beam behaves like a plain concrete beam — it cracks suddenly without warning (brittle failure). The minimum ensures the steel can carry the cracking load, so the beam fails gradually (ductile failure).

**Maximum steel (Cl 26.5.1.2):**

$$A_{s,max} = 0.04 \times b \times D$$

That's 4% of the gross section. More than that and:
- Bars can't fit with proper spacing
- Concrete can't flow around the steel
- The section becomes congested and unworkable

> **Think of it like...** thread count in a CPU. Too few threads (min steel) = the program crashes on any spike. Too many threads (max steel) = context-switching overhead makes everything slower. There's a practical window.

---

### 6. Crack Width Control — Cracks Are Normal

Here's a counterintuitive fact: **all reinforced concrete beams crack**. That's by design. Concrete's tensile strength is so low that under service loads, the tension zone cracks. The steel then takes over.

The question isn't *whether* cracks appear, but *how wide* they get.

**IS 456 Cl 43, Annex F** limits:

| Exposure | Max Crack Width |
|----------|----------------|
| Mild/Moderate | 0.3 mm |
| Severe/Very Severe | 0.2 mm |

The Annex F formula:

$$w_{cr} = \frac{3 \times a_{cr} \times \epsilon_m}{1 + 2 \times \frac{a_{cr} - c_{min}}{h - x}}$$

Where:
- $a_{cr}$ = distance from the point on the surface to the nearest bar
- $\epsilon_m$ = average strain at the level considered
- $c_{min}$ = minimum cover to the bar
- $h$ = overall depth, $x$ = neutral axis depth

> **Think of it like...** stress testing your API. You don't expect zero errors — you expect errors to stay below a threshold. Similarly, you don't expect zero cracks — you expect crack widths to stay below 0.3 mm.

Our library's `check_crack_width()` implements this:

```python
from structural_lib.codes.is456.beam.serviceability import check_crack_width

result = check_crack_width(
    exposure_class="moderate",
    acr_mm=75.0,           # distance to nearest bar
    cmin_mm=25.0,          # minimum cover
    h_mm=500.0,            # overall depth
    x_mm=180.0,            # neutral axis depth
    fs_service_nmm2=230.0, # service stress in steel
)
print(result.is_ok)      # True or False
print(result.remarks)    # "OK: wcr=0.21 mm <= limit=0.30 mm"
```

---

### 7. Deflection Check — Will the Beam Sag?

A beam might be strong enough (passes flexure and shear) but still deflect too much — the ceiling sags, doors jam, plaster cracks. IS 456 provides a quick **deemed-to-satisfy** check using span/depth ratios.

**IS 456 Cl 23.2.1** — Basic L/d ratios:

| Support Condition | Max L/d |
|-------------------|---------|
| Cantilever        | 7       |
| Simply Supported  | 20      |
| Continuous        | 26      |

These are modified by factors:
- **Tension steel factor** ($MF_1$, Fig. 4) — more steel → stiffer → higher L/d allowed
- **Compression steel factor** ($MF_2$, Fig. 5) — compression steel reduces deflection
- **Flanged beam factor** ($MF_3$, Fig. 6) — flanged beams may reduce allowed L/d

$$\text{Allowable } L/d = \text{Base} \times MF_1 \times MF_2 \times MF_3$$

**Example:** Simply supported beam, span = 6000 mm, d = 450 mm:
- $L/d$ = 6000/450 = 13.3
- Allowable = 20 × 1.0 × 1.0 × 1.0 = 20
- 13.3 < 20 → **OK** ✅

Our library implements this:

```python
from structural_lib.codes.is456.beam.serviceability import check_deflection_span_depth

result = check_deflection_span_depth(
    span_mm=6000,
    d_mm=450,
    support_condition="simply_supported",
    mf_tension_steel=1.2,  # from IS 456 Fig. 4
)
print(result.is_ok)     # True
print(result.remarks)   # "OK: L/d=13.333 <= allowable=24.000"
print(result.assumptions)  # Lists any defaults used
```

The function also accepts `SupportCondition` enums and records any assumed defaults in the `assumptions` field — so you always know what was assumed vs. provided. This is important for engineering transparency.

For more precise deflection calculations, the library provides **Level B** (effective moment of inertia method) and **Level C** (creep + shrinkage, Annex C):

```python
# Level B — uses cracking moment and effective I
from structural_lib.codes.is456.beam.serviceability import check_deflection_level_b

# Level C — long-term creep and shrinkage
from structural_lib.codes.is456.beam.serviceability import check_deflection_level_c
```

---

### 8. Bar Bending Schedule (BBS) — The Construction Site's API Contract

Everything so far has been design math. But at some point, the results must leave the computer and arrive at a construction site where workers cut and bend real steel bars.

The **Bar Bending Schedule** (IS 2502) is a table that tells the fabricator:
- Bar mark (ID)
- Type of bar (shape code)
- Diameter
- Number of bars
- Length of each bar
- Total weight

> **Think of it like...** an API response schema. The BBS is the **contract** between the design engineer and the construction team. If the contract is wrong (wrong lengths, missing bars), the building is wrong. Our library's `BeamDetailingResult` dataclass is the structured output that feeds into BBS generation.

The `BeamDetailingResult` from `create_beam_detailing()` contains:

```python
from structural_lib.codes.is456.beam.detailing import BeamDetailingResult

# The result object has:
result.beam_id         # "B1" — beam identifier
result.b               # 300 mm — beam width
result.D               # 500 mm — overall depth
result.cover           # 25 mm — clear cover
result.top_bars        # [BarArrangement, BarArrangement, BarArrangement]
result.bottom_bars     # [BarArrangement, BarArrangement, BarArrangement]
result.stirrups        # [StirrupArrangement, StirrupArrangement, StirrupArrangement]
result.ld_tension      # 645 mm — development length for tension bars
result.ld_compression  # 483 mm — development length for compression bars
result.lap_length      # 749 mm — lap splice length
result.is_valid        # True/False
```

Each `BarArrangement` has a `.callout()` method that returns the standard notation:
```python
result.bottom_bars[1].callout()  # "3-16φ" — 3 bars of 16mm diameter
result.stirrups[0].callout()     # "2L-8φ@150" — 2-legged 8mm stirrups at 150mm spacing
```

This is what goes on the drawing and into the BBS table.

---

## 🏗️ Library Examples

### Example 1: Calculate Development Length

```python
from structural_lib.codes.is456.beam.detailing import (
    calculate_development_length,
    get_bond_stress,
)

# Step 1: Get bond stress for M25 concrete, deformed bars
tau_bd = get_bond_stress(fck=25, bar_type="deformed")
print(f"Bond stress (M25, deformed): {tau_bd} N/mm²")  # 2.24

# Step 2: Calculate Ld for 16mm bar, Fe415 steel
ld = calculate_development_length(bar_dia=16, fck=25, fy=415)
print(f"Development length: {ld} mm")  # 645 mm

# Step 3: Compare with different grades
ld_m20 = calculate_development_length(bar_dia=16, fck=20, fy=415)
ld_m30 = calculate_development_length(bar_dia=16, fck=30, fy=415)
print(f"Ld (M20): {ld_m20} mm")  # higher — weaker concrete, weaker bond
print(f"Ld (M30): {ld_m30} mm")  # lower — stronger concrete, better bond
```

### Example 2: Check Deflection (Level A)

```python
from structural_lib.codes.is456.beam.serviceability import check_deflection_span_depth

# A 6m simply-supported beam, effective depth 450mm
result = check_deflection_span_depth(
    span_mm=6000,
    d_mm=450,
    support_condition="simply_supported",
)
print(f"L/d = {result.computed['ld_ratio']:.1f}")
print(f"Allowable L/d = {result.computed['allowable_ld']:.1f}")
print(f"Deflection OK? {result.is_ok}")
print(f"Assumptions: {result.assumptions}")
```

### Example 3: Check Crack Width

```python
from structural_lib.codes.is456.beam.serviceability import check_crack_width

result = check_crack_width(
    exposure_class="severe",   # coastal area — tighter limit (0.2mm)
    acr_mm=65.0,
    cmin_mm=45.0,              # severe exposure needs 45mm cover
    h_mm=500.0,
    x_mm=165.0,
    fs_service_nmm2=200.0,
)
print(f"Crack width OK? {result.is_ok}")
print(f"Details: {result.remarks}")
```

### Example 4: Calculate Lap Length

```python
from structural_lib.codes.is456.beam.detailing import calculate_lap_length

# Normal splice (50% bars spliced)
lap = calculate_lap_length(bar_dia=16, fck=25, fy=415)
print(f"Lap length (normal): {lap} mm")

# Seismic splice (IS 13920 requires 1.5×Ld)
lap_seis = calculate_lap_length(bar_dia=16, fck=25, fy=415, is_seismic=True)
print(f"Lap length (seismic): {lap_seis} mm")
```

---

## 🎯 Simple Examples (Hand Calculations)

### Hand Calc 1: Development Length

**Given:** 20φ bar, M25 concrete, Fe500 steel

$$\tau_{bd} = 2.24 \text{ N/mm² (from table, M25, deformed)}$$

$$L_d = \frac{20 \times 0.87 \times 500}{4 \times 2.24} = \frac{8700}{8.96} = 971 \text{ mm}$$

That's about **48.5 bar diameters**. Notice how Fe500 steel needs *longer* development than Fe415 — higher stress means more bond length needed.

### Hand Calc 2: Deflection Check

**Given:** Continuous beam, span = 8000 mm, d = 400 mm, with tension steel modification factor 1.3

$$L/d = \frac{8000}{400} = 20.0$$

$$\text{Allowable } L/d = 26 \times 1.3 = 33.8$$

$$20.0 < 33.8 \implies \textbf{OK} ✅$$

### Hand Calc 3: Minimum Steel

**Given:** Beam b = 300 mm, d = 500 mm, Fe415

$$A_{s,min} = \frac{0.85 \times 300 \times 500}{415} = 307 \text{ mm}^2$$

That's approximately 2-16φ bars (2 × 201 = 402 mm²) — you can never go below this, even if the moment demand requires less.

---

## 🔧 Exercise

### Task: Complete Detailing Check

You have a beam: b = 250 mm, D = 500 mm, span = 5000 mm (simply supported), M25 concrete, Fe415 steel, moderate exposure, bottom steel = 3-16φ bars.

1. Calculate the clear cover (Table 16)
2. Check if 3 bars fit in one layer (spacing rules)
3. Calculate development length for 16φ bars
4. Check deflection using L/d ratio (d = D - cover - stirrup - bar/2 ≈ 442 mm)
5. Is the steel above minimum? (calculate $A_{s,min}$)

**Verify with library:**
```python
from structural_lib.codes.is456.beam.detailing import (
    calculate_development_length,
    calculate_bar_spacing,
)
from structural_lib.codes.is456.beam.serviceability import check_deflection_span_depth

# Your calculations here — compare hand calc vs library output
ld = calculate_development_length(bar_dia=16, fck=25, fy=415)
defl = check_deflection_span_depth(span_mm=5000, d_mm=442, support_condition="ss")
print(f"Ld = {ld} mm")
print(f"Deflection OK? {defl.is_ok}, L/d = {defl.computed['ld_ratio']:.1f}")
```

**Expected answers:**
- Cover = 30 mm (moderate exposure)
- Available width = 250 - 2×(30 + 8) = 174 mm; 3 bars × 16 = 48 mm; spacing = (174 - 48)/2 = 63 mm > 25 mm → fits ✅
- $L_d$ = 645 mm
- L/d = 5000/442 = 11.3, allowable = 20 → OK ✅
- $A_{s,min}$ = 0.85 × 250 × 442 / 415 = 228 mm²; provided = 3 × 201 = 603 mm² > 228 → OK ✅

---

## 💬 Can You Explain?

1. **Why does higher concrete grade *reduce* development length?** (Hint: stronger concrete bonds better.)
2. **A beam passes the flexure check but fails the deflection check. What do you do?** (Increase d? Add compression steel? Shorten span?)
3. **Why does IS 456 specify a *maximum* steel ratio of 4%?** What practical problem occurs if you exceed it?
4. **A colleague says "RC beams should never crack." Are they right?** Explain using the crack width concept.
5. **Why is the BBS so important on site?** What happens if a bar is cut 100 mm too short?

---

## 📎 References

- **IS 456:2000** — Cl 23.2 (Deflection), Cl 26.2 (Development length), Cl 26.3 (Spacing), Cl 26.4 (Cover), Cl 26.5 (Min/max reinforcement), Cl 43 (Crack width), Annex C (Deflection calc), Annex F (Crack width formula), Table 16/16A (Cover)
- **IS 2502:1963** — Bar Bending Schedule
- **IS 13920:2016** — Cl 6.2.6 (Seismic splice requirements)
- **SP:34:1987** — Handbook on Concrete Reinforcement and Detailing
- **Library source:** `Python/structural_lib/codes/is456/beam/detailing.py`, `Python/structural_lib/codes/is456/beam/serviceability.py`

---

## What's Next?

**Day 5: Column Design** — We move from horizontal members (beams) to vertical ones (columns). You'll learn how columns carry axial load *plus* bending moment simultaneously, why the P-M interaction curve is the most important concept in column design, and how biaxial bending makes things even more interesting. That's where `short_axial_capacity()`, `pm_interaction_curve()`, and `biaxial_bending_check()` live.
