# Research: Cost Optimization for RC Beams (IS 456)

**Date:** 2026-01-05
**Status:** Research Complete (Day 1)
**Agent:** RESEARCHER (Subagent)

---

## 1. Market Rates (India Benchmarks)
Based on CPWD DSR 2023 and current market trends.

| Component | Unit | Rate (INR) | Notes |
| :--- | :--- | :--- | :--- |
| **Concrete (M20)** | m^3 | 6200 | Materials + mixing + placing |
| **Concrete (M25)** | m^3 | 6700 | Baseline residential grade |
| **Concrete (M30)** | m^3 | 7200 | ~INR 500 premium per grade |
| **Concrete (M35)** | m^3 | 7700 | Higher strength |
| **Concrete (M40)** | m^3 | 8200 | Higher strength |
| **Steel (Fe500)** | kg | 72 | Cutting + bending + binding |
| **Formwork** | m^2 | 500 | Shuttering + propping + removal |
| **Base Labor** | day | 800 | Skilled labor day rate |
| **Labor Productivity** | m^3/day | 5.0 | Concrete placement rate |
| **Wastage Factor** | - | 1.05 | 5% wastage default |

---

## 2. Cost Objective Function
The total cost C_total for a beam of length L:

C_total = (C_c * V_c) + (C_s * W_s) + (C_f * A_f) + C_labor + P_congestion

Optimization heuristics:
- Steel is ~10x more expensive per unit weight. Increasing depth to reduce Ast is the primary lever.
- Congestion penalty: apply a 1.2x labor multiplier if pt > 2.5%.
- Standardization: prefer b in 230mm/300mm increments and D in 50mm increments.

---

## 3. CostProfile (Python)
The current implementation lives in `Python/structural_lib/costing.py`.

```python
@dataclass
class CostProfile:
    currency: str = "INR"
    concrete_costs: Dict[int, float] = {20: 6200, 25: 6700, 30: 7200, 35: 7700, 40: 8200}
    steel_cost_per_kg: float = 72.0
    formwork_cost_per_m2: float = 500.0
    congestion_threshold_pt: float = 2.5
    congestion_multiplier: float = 1.2
    location_factor: float = 1.0
    wastage_factor: float = 1.05
    base_labor_rate_per_day: float = 800.0
    labor_productivity_m3_per_day: float = 5.0
```

Notes:
- Concrete grades are keyed by numeric fck values (e.g., 25, 30).
- Steel is modeled with a single Fe500 baseline rate for now.
- Location factor scales totals for regional adjustments.

---

## 4. Cost Calculation Functions

### Core utilities (legacy, used by optimization)
- `calculate_concrete_volume(b_mm, D_mm, span_mm)`
- `calculate_steel_weight(ast_mm2, span_mm)`
- `calculate_formwork_area(b_mm, D_mm, span_mm)`
- `calculate_beam_cost(...)` (returns a `CostBreakdown`)

### Detailed breakdown utilities
- `calculate_concrete_cost(volume_m3, grade, cost_profile)`
- `calculate_steel_cost(weight_kg, grade, cost_profile)`
- `calculate_formwork_cost(area_m2, cost_profile)`
- `calculate_total_beam_cost(beam_data, cost_profile)`

Unit conversions (mm and mm^2 to SI):
```text
volume_m3 = (b_mm * h_mm * length_mm) / 1e9
weight_kg = (area_mm2 * length_mm * 7850) / 1e9
area_m2 = (perimeter_mm * length_mm) / 1e6
```

Formwork area for beams (3 sides: bottom + 2 sides):
```text
perimeter_mm = b_mm + 2 * h_mm
```

Congestion penalty:
```text
pt = (ast_mm2 / (b_mm * d_mm)) * 100
if pt > congestion_threshold_pt:
    labor_cost *= congestion_multiplier
```

---

## 5. Implementation Notes
- Defaults are tuned to CPWD DSR 2023 national averages.
- Missing grades fall back to the M25 rate in the cost profile.
- Totals in `calculate_total_beam_cost` apply the location factor after summing components.

---

## 6. Next Steps (Day 2+)
1. Multi-objective optimization (cost vs. constructability)
2. Regional cost variations
3. Time-dependent cost models (inflation, market fluctuations)
4. Carbon footprint integration
5. Cost comparison visualizations

---

**References:**
- IS 456:2000 - Code of Practice for Plain and Reinforced Concrete
- CPWD Schedule of Rates 2024
- Industry surveys (2025 Q1)
