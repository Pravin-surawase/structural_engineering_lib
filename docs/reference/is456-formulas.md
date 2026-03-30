---
owner: Main Agent
status: active
last_updated: 2026-03-30
doc_type: reference
complexity: intermediate
tags: []
---

# IS 456:2000 Quick Reference — RC Beam Design Formulas

**Type:** Reference
**Audience:** Developers
**Status:** Production Ready
**Importance:** High
**Created:** 2025-01-01
**Last Updated:** 2026-03-29

---

**For use with:** IS 456 RC Beam Design Library
**Code Reference:** IS 456:2000, SP:16-1980

---

## 1. Effective Depth

$$d = D - c_{clear} - \phi_{stirrup} - \frac{\phi_{main}}{2}$$

| Symbol | Description | Unit |
|--------|-------------|------|
| $D$ | Overall depth | mm |
| $c_{clear}$ | Clear cover (Table 16: 25-50mm) | mm |
| $\phi_{stirrup}$ | Stirrup bar diameter | mm |
| $\phi_{main}$ | Main bar diameter | mm |
| $d$ | Effective depth | mm |

---

## 2. Limiting Neutral Axis Depth (Annex G.1.1)

| Steel Grade | $f_y$ (N/mm²) | $x_{u,max}/d$ |
|-------------|---------------|---------------|
| Fe 250 | 250 | **0.53** |
| Fe 415 | 415 | **0.48** |
| Fe 500 | 500 | **0.46** |

---

## 3. Limiting Moment of Resistance (Clause 38.1)

$$M_{u,lim} = 0.36 \times f_{ck} \times b \times x_{u,max} \times (d - 0.42 \times x_{u,max})$$

**Simplified form:**
$$M_{u,lim} = R_u \times f_{ck} \times b \times d^2$$

| Steel | $R_u = 0.36k(1-0.42k)$ where $k = x_{u,max}/d$ |
|-------|-----------------------------------------------|
| Fe 250 | 0.149 |
| Fe 415 | 0.138 |
| Fe 500 | 0.133 |

**Note:** Result is in N·mm. Divide by 10⁶ for kN·m.

---

## 4. Area of Steel — Singly Reinforced (Clause 38.1)

$$A_{st} = \frac{0.5 \times f_{ck}}{f_y} \times \left[1 - \sqrt{1 - \frac{4.6 \times M_u}{f_{ck} \times b \times d^2}}\right] \times b \times d$$

| Variable | Unit |
|----------|------|
| $M_u$ | N·mm (convert kN·m × 10⁶) |
| $f_{ck}$, $f_y$ | N/mm² |
| $b$, $d$ | mm |
| $A_{st}$ | mm² |

**Check:** If discriminant $(1 - 4.6M_u/(f_{ck} \cdot b \cdot d^2)) < 0$, then $M_u > M_{u,lim}$ → doubly reinforced required.

---

## 5. Reinforcement Limits (Clause 26.5.1)

### Minimum Tension Steel (Clause 26.5.1.1)
$$A_{st,min} = \frac{0.85 \times b \times d}{f_y}$$

### Maximum Tension Steel (Clause 26.5.1.2)
$$A_{st,max} = 0.04 \times b \times D$$

### Side Face Reinforcement (Clause 26.5.1.3)
- Required when $D > 750$ mm
- $A_{sf} = 0.1\%$ of web area on each face
- Spacing ≤ 300 mm

---

## 6. Shear Stress (Clause 40.1)

$$\tau_v = \frac{V_u}{b \times d}$$

| Variable | Unit |
|----------|------|
| $V_u$ | N (convert kN × 10³) |
| $b$, $d$ | mm |
| $\tau_v$ | N/mm² |

---

## 7. Design Shear Strength τc — Table 19

| $p_t$ (%) | M15 | M20 | M25 | M30 | M35 | M40+ |
|-----------|-----|-----|-----|-----|-----|------|
| ≤0.15 | 0.28 | 0.28 | 0.29 | 0.29 | 0.29 | 0.30 |
| 0.25 | 0.35 | 0.36 | 0.36 | 0.37 | 0.37 | 0.38 |
| 0.50 | 0.46 | 0.48 | 0.49 | 0.50 | 0.50 | 0.51 |
| 0.75 | 0.54 | 0.56 | 0.57 | 0.59 | 0.59 | 0.60 |
| 1.00 | 0.60 | 0.62 | 0.64 | 0.66 | 0.67 | 0.68 |
| 1.25 | 0.64 | 0.67 | 0.70 | 0.71 | 0.73 | 0.74 |
| 1.50 | 0.68 | 0.72 | 0.74 | 0.76 | 0.78 | 0.79 |
| 1.75 | 0.71 | 0.75 | 0.78 | 0.80 | 0.82 | 0.84 |
| 2.00 | 0.71 | 0.79 | 0.82 | 0.84 | 0.86 | 0.88 |
| 2.25 | 0.71 | 0.81 | 0.85 | 0.88 | 0.90 | 0.92 |
| 2.50 | 0.71 | 0.82 | 0.88 | 0.91 | 0.93 | 0.95 |
| 2.75 | 0.71 | 0.82 | 0.90 | 0.94 | 0.96 | 0.98 |
| ≥3.00 | 0.71 | 0.82 | 0.92 | 0.96 | 0.99 | 1.01 |

$$p_t = \frac{100 \times A_{st}}{b \times d}$$

**Notes:**
- For $p_t < 0.15\%$: use 0.15% value
- For $p_t > 3.0\%$: use 3.0% value
- Interpolate for intermediate $p_t$

---

## 8. Maximum Shear Stress τc,max — Table 20

| Grade | M15 | M20 | M25 | M30 | M35 | M40+ |
|-------|-----|-----|-----|-----|-----|------|
| $\tau_{c,max}$ | 2.5 | 2.8 | 3.1 | 3.5 | 3.7 | 4.0 |

**If $\tau_v > \tau_{c,max}$:** Section inadequate — increase b or d.

---

## 9. Shear Reinforcement (Clause 40.4)

### Shear to be Carried by Stirrups
$$V_{us} = V_u - \tau_c \times b \times d$$

### Stirrup Spacing (Vertical Stirrups)
$$s_v = \frac{0.87 \times f_y \times A_{sv} \times d}{V_{us}}$$

where $A_{sv} = n \times \frac{\pi \phi^2}{4}$ (n = number of legs)

### Maximum Spacing (Clause 26.5.1.5)
$$s_{v,max} = \min(0.75d, 300 \text{ mm})$$

### Minimum Shear Reinforcement (Clause 26.5.1.6)
$$\frac{A_{sv}}{b \times s_v} \geq \frac{0.4}{0.87 \times f_y}$$

**Unit note:** Use $V_u$ and $V_{us}$ in **Newtons** when combining with $\tau_c$ and $b \times d$ (convert kN → N by ×1000). Convert back to kN only for reporting.

---

## 10. Shear Design Flowchart

```
Calculate τv = Vu / (b × d)
         ↓
Is τv > τc,max?  ──YES──→  SECTION INADEQUATE
         │                  Increase b or d
         NO
         ↓
Calculate pt = 100 × Ast / (b × d)
         ↓
Look up τc from Table 19
         ↓
Is τv ≤ 0.5 × τc?  ──YES──→  PROVIDE MINIMUM SHEAR REINFORCEMENT
         │                  (Cl. 26.5.1.6)
         NO
         ↓
Is τv ≤ τc?  ──YES──→  MINIMUM SHEAR REINFORCEMENT
         │              sv = 0.87 × fy × Asv / (0.4 × b)
         NO
         ↓
DESIGN SHEAR REINFORCEMENT
Vus = Vu - τc × b × d
sv = 0.87 × fy × Asv × d / Vus
sv ≤ sv,max = min(0.75d, 300mm)
```

---

## 11. Common Bar Areas

| Diameter (mm) | Area (mm²) |
|---------------|------------|
| 8 | 50.3 |
| 10 | 78.5 |
| 12 | 113.1 |
| 16 | 201.1 |
| 20 | 314.2 |
| 25 | 490.9 |
| 32 | 804.2 |

**Stirrup areas (2 legs):**
| Diameter | Area (mm²) |
|----------|------------|
| 8 mm | 100.5 |
| 10 mm | 157.1 |
| 12 mm | 226.2 |

---

## 12. Unit Conversions

| From | To | Multiply by |
|------|-----|-------------|
| kN·m | N·mm | 10⁶ |
| kN | N | 10³ |
| m | mm | 10³ |
| MPa | N/mm² | 1 (same) |

---

## 13. Stress Block Summary (Clause 38.1)

| Parameter | Value |
|-----------|-------|
| Stress at compression face | $0.446 f_{ck}$ |
| Compression force | $C = 0.36 f_{ck} \times b \times x_u$ |
| Lever arm from NA | $z = d - 0.42 x_u$ |
| Tension force | $T = 0.87 f_y \times A_{st}$ |

**Equilibrium:** $C = T$

$$x_u = \frac{0.87 f_y \times A_{st}}{0.36 f_{ck} \times b}$$

---

**End of Quick Reference**
