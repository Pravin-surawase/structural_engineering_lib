# IS Code Detailing Research — RESEARCHER Agent

**Type:** Research
**Audience:** Developers
**Status:** Complete
**Importance:** Medium
**Created:** 2025-12-11
**Last Updated:** 2026-01-13

---

**Scope:** IS 456:2000, IS 13920:2016, SP 34:1987 for RC Beam Detailing

---

## 1. Cover Requirements (IS 456 Cl 26.4)

### 1.1 Nominal Cover
| Exposure Condition | Minimum Cover (mm) |
|-------------------|-------------------|
| Mild | 20 |
| Moderate | 30 |
| Severe | 45 |
| Very Severe | 50 |
| Extreme | 75 |

**Note:** Cover should not be less than the bar diameter.

### 1.2 Effective Cover
```
Effective Cover = Nominal Cover + Stirrup Diameter + (Bar Diameter / 2)
```

---

## 2. Minimum Bar Spacing (IS 456 Cl 26.3)

### 2.1 Horizontal Spacing
- Minimum = MAX(Bar Diameter, Aggregate Size + 5mm, 25mm)
- For bundled bars: Use equivalent diameter

### 2.2 Vertical Spacing (Layers)
- Minimum = 15mm or 2/3 of aggregate size, whichever is greater
- Bars in upper layer should be directly above lower layer bars

---

## 3. Development Length (IS 456 Cl 26.2.1)

### 3.1 Formula
```
Ld = (φ × σs) / (4 × τbd)
```
Where:
- φ = Bar diameter (mm)
- σs = Stress in bar (usually 0.87 × fy)
- τbd = Design bond stress (Table 5.3)

### 3.2 Design Bond Stress (τbd) — IS 456 Table 5.3
| Concrete Grade | Plain Bars (N/mm²) | Deformed Bars (N/mm²) |
|---------------|-------------------|----------------------|
| M20 | 1.2 | 1.92 |
| M25 | 1.4 | 2.24 |
| M30 | 1.5 | 2.40 |
| M35 | 1.7 | 2.72 |
| M40+ | 1.9 | 3.04 |

### 3.3 Simplified Ld Values (Deformed Bars, Fe500)
| fck | Ld (in terms of φ) |
|-----|-------------------|
| M20 | 47φ |
| M25 | 40φ |
| M30 | 38φ |
| M35 | 33φ |
| M40 | 30φ |

---

## 4. Lap/Splice Length (IS 456 Cl 26.2.5)

### 4.1 Tension Lap
```
Lap Length = α × Ld
```
Where α depends on percentage of bars spliced at section:
| % Bars Spliced | α Factor |
|---------------|----------|
| ≤ 50% | 1.0 |
| > 50% | 1.3 |

**For Seismic (IS 13920):** Minimum lap = 1.5 × Ld

### 4.2 Compression Lap
- Lap Length = Ld (no enhancement needed)
- Must have stirrups at both ends of lap

### 4.3 Splice Location (IS 13920 Cl 6.2.6)
- **NOT ALLOWED** within:
  - 2d from column face (plastic hinge zone)
  - Joints
- **Preferred:** Middle third of span (low moment region)

---

## 5. Stirrup/Shear Reinforcement (IS 456 Cl 26.5.1.6)

### 5.1 Minimum Diameter
- 6mm for beams up to 300mm depth
- 8mm for beams > 300mm depth

### 5.2 Maximum Spacing
```
Sv,max = MIN(0.75d, 300mm)
```

### 5.3 Minimum Shear Reinforcement
```
Asv,min = (0.4 × b × Sv) / (0.87 × fy)
```

### 5.4 Stirrup Anchorage (IS 456 Cl 26.2.2.4)
- 135° hook at each end (mandatory for seismic)
- Hook extension = 6φ or 75mm, whichever is greater

---

## 6. Ductile Detailing — IS 13920:2016

### 6.1 Geometry Limits (Cl 6.1)
- b ≥ 200mm
- b/D ≥ 0.3
- Span/D ≤ 4 (deep beam provisions otherwise)

### 6.2 Longitudinal Reinforcement (Cl 6.2)
| Parameter | Requirement |
|-----------|-------------|
| Min Tension Steel | $\frac{0.24\sqrt{f_{ck}}}{f_y}$ but ≥ 0.35% |
| Max Steel (Tension) | 2.5% |
| Min at Any Face | 2 bars, min 12mm |
| Max at Any Face | 4% (practical limit) |

### 6.3 Confinement Zones (Cl 6.3.5)
**Plastic Hinge Zone Length:**
```
Lo = 2 × D (from column face)
```

**Hoop Spacing in Plastic Hinge Zone:**
```
Sv,conf = MIN(d/4, 8×db_min, 100mm)
```

**Outside Plastic Hinge Zone:**
```
Sv = MIN(d/2, 150mm)
```

### 6.4 Special Confining Reinforcement
- Closed hoops (135° hooks at both ends)
- First hoop within 50mm from column face
- No splices in plastic hinge zone

---

## 7. Drawing Conventions (SP 34:1987)

### 7.1 Standard Representations
| Element | Symbol | Representation |
|---------|--------|----------------|
| Main Bar | Solid line | With diameter callout |
| Stirrup | Rectangular loop | With spacing annotation |
| Section Cut | Dashed line | With section letter |
| Dimension | Arrow-ended line | With value in mm |

### 7.2 Bar Callout Format
```
n - φ d
```
Where:
- n = Number of bars
- φ = Phi symbol (diameter indicator)
- d = Bar diameter in mm

**Examples:**
- `3 - φ 16` = 3 nos. of 16mm diameter bars
- `2 - φ 20 + 1 - φ 16` = 2 nos. 20mm + 1 no. 16mm

### 7.3 Stirrup Notation
```
φ d @ s c/c
```
Where:
- d = Stirrup diameter
- s = Spacing
- c/c = Center to center

**Example:** `φ 8 @ 150 c/c`

### 7.4 Beam Elevation Layout
```
                    CLEAR SPAN (L)
    ├─────────────────────────────────────────────┤

    ┌─────────────────────────────────────────────┐
    │  TOP STEEL: 2-16                            │
    │  ════════════════════════════════════════   │ D
    │  BOT STEEL: 3-20                            │
    └─────────────────────────────────────────────┘
        ↑           ↑           ↑           ↑
    φ8@150      φ8@200      φ8@200      φ8@150
    (Lo=2D)     (Mid Span)  (Mid Span)  (Lo=2D)
```

---

## 8. Key Formulas Summary

### 8.1 Development Length (Simplified)
```python
def calc_Ld(dia: float, fck: float, fy: float) -> float:
    """Development length in mm for deformed bars."""
    tau_bd = {20: 1.92, 25: 2.24, 30: 2.40, 35: 2.72, 40: 3.04}
    grade = min(40, max(20, 5 * (fck // 5)))  # Round to nearest grade
    sigma_s = 0.87 * fy
    return (dia * sigma_s) / (4 * tau_bd.get(grade, 1.92))
```

### 8.2 Confinement Spacing
```python
def calc_confinement_spacing(d: float, db_min: float) -> float:
    """Maximum hoop spacing in plastic hinge zone (mm)."""
    return min(d / 4, 8 * db_min, 100)
```

### 8.3 Plastic Hinge Zone Length
```python
def calc_plastic_hinge_length(D: float) -> float:
    """Length of plastic hinge zone from column face (mm)."""
    return 2 * D
```

---

## 9. Implementation Recommendations

### 9.1 DXF Layer Mapping
| IS Concept | DXF Layer |
|------------|-----------|
| Beam Outline | `BEAM_OUTLINE` |
| Main Bars | `REBAR_MAIN` |
| Stirrups | `REBAR_STIRRUP` |
| Dimensions | `DIMENSIONS` |
| Text/Callouts | `TEXT` |
| Confinement Zone | `ZONE_CONF` |

### 9.2 Drawing Dimensions to Calculate
| Dimension | Source | Formula |
|-----------|--------|---------|
| Overall Length | Input | User-defined or from Station data |
| Section Height | Input | D (overall depth) |
| Section Width | Input | b (beam width) |
| Cover | Input | Nominal cover |
| Bar Positions | Calculated | Cover + stirrup + bar/2 |
| Stirrup Zones | Design Output | From M14 schedule |

### 9.3 Dependencies
- **Python:** `ezdxf` library for DXF generation
- **VBA:** Optionally call Python script or write raw DXF (ASCII format)

---

## 10. References

| Code | Title |
|------|-------|
| IS 456:2000 | Plain and Reinforced Concrete — Code of Practice |
| IS 13920:2016 | Ductile Design and Detailing of RC Structures |
| SP 34:1987 | Handbook on Concrete Reinforcement and Detailing |
| SP 16:1980 | Design Aids for Reinforced Concrete to IS 456 |

---

## 11. Sign-off

| Role | Status | Date |
|------|--------|------|
| RESEARCHER | ✅ Complete | 2025-12-11 |
