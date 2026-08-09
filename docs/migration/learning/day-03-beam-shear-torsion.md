# Day 3: Shear & Torsion Design (IS 456 Cl 40-41)

**Type:** Guide
**Audience:** Developers, Students
**Status:** Active
**Importance:** High
**Created:** 2026-04-08
**Last Updated:** 2026-04-08

---

> **Prerequisites:** Day 1 (Materials & Sections) and Day 2 (Flexural Design).
> You should be comfortable with beam geometry (b, d, D) and steel percentages.

---

## 1. What is Shear in a Beam?

When a beam carries load, bending is only half the story. The beam also develops
**internal cutting forces** at every cross-section â these are shear forces.

### The Book Analogy

Hold a thick paperback book by its two ends and press down in the middle. Watch
the pages: they **slide past each other**. That sliding motion between adjacent
layers is exactly what shear does inside a beam. Concrete, unlike a book, can't
slide freely â so if the shear force gets too large, diagonal cracks appear
(roughly at 45 degrees) and the beam can fail suddenly, often without warning.

> **Why shear matters:** Shear failure is **brittle** â unlike flexural failure
> (where you see big cracks and deflections before collapse), a beam failing in
> shear can snap with almost no warning. That's why IS 456 is very conservative
> on shear design.

### Nominal Shear Stress

The first thing we calculate is the **nominal shear stress**:

$$\tau_v = \frac{V_u}{b \times d}$$

Where:
- $V_u$ = factored shear force (N)
- $b$ = beam width (mm)
- $d$ = effective depth (mm)

This is IS 456 **Clause 40.1**. In the library:

```python
from structural_lib.codes.is456.beam.shear import calculate_tv

# Beam: b=300 mm, d=450 mm, Vu=150 kN
tv = calculate_tv(vu_kn=150, b=300, d=450)
# tv = 150000 / (300 x 450) = 1.11 N/mm²
```

> **Critical section location (Cl 40.5.1):** For beams with standard supports,
> the critical section for shear is taken at a distance $d$ from the face of the
> support. Loads applied closer than $d$ from the support get carried partly
> by direct compression (strut action) — more on this later.

---

## 2. Concrete Shear Capacity ($\tau_c$)

Here's the good news: concrete **can resist some shear by itself**, through
three mechanisms:

1. **Aggregate interlock** — rough crack surfaces wedge against each other
2. **Dowel action** — tension bars crossing the crack resist vertical displacement
3. **Uncracked compression zone** — the concrete above the neutral axis carries shear

The combined effect is captured by $\tau_c$ (design shear strength of concrete),
which depends on two things:

| Factor | Why it matters |
|--------|---------------|
| Concrete grade ($f_{ck}$) | Stronger concrete = more aggregate interlock |
| Tension steel percentage ($p_t = 100 A_{st} / (b d)$) | More steel = better dowel action |

### IS 456 Table 19 â Design Shear Strength $\\tau_c$ (N/mmÂ²)

This is one of the most-used tables in structural design. Here's a portion:

| $p_t$ (%%) | M15 | M20 | M25 | M30 | M35 | M40 |
|-----------|-----|-----|-----|-----|-----|-----|
| 0.15      | 0.28 | 0.28 | 0.29 | 0.29 | 0.29 | 0.30 |
| 0.25      | 0.35 | 0.36 | 0.36 | 0.37 | 0.37 | 0.38 |
| 0.50      | 0.46 | 0.48 | 0.49 | 0.50 | 0.50 | 0.51 |
| 0.75      | 0.54 | 0.56 | 0.57 | 0.59 | 0.59 | 0.60 |
| 1.00      | 0.60 | 0.62 | 0.64 | 0.66 | 0.67 | 0.68 |
| 1.25      | 0.64 | 0.67 | 0.70 | 0.71 | 0.73 | 0.74 |
| 1.50      | 0.68 | 0.72 | 0.74 | 0.76 | 0.78 | 0.79 |
| 2.00      | 0.71 | 0.79 | 0.82 | 0.84 | 0.86 | 0.88 |
| 2.50      | 0.71 | 0.82 | 0.88 | 0.91 | 0.93 | 0.95 |
| 3.00      | 0.71 | 0.82 | 0.92 | 0.96 | 0.99 | 1.01 |

Notice how $\\tau_c$ **saturates** for M15 at around $p_t = 1.75\%%$ (stays 0.71).
Higher grade concretes keep gaining strength up to $p_t = 3\%%$.

