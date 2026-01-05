# Research: Cost Optimization for RC Beams (IS 456)

**Date:** 2026-01-05
**Status:** Research Complete (Day 1)
**Agent:** RESEARCHER (Subagent)

---

## 1. Market Rates (India Benchmarks)
Based on CPWD DSR 2023 and current market trends.

| Component | Unit | Rate (INR) | Notes |
| :--- | :--- | :--- | :--- |
| **Concrete (M25)** | m³ | ₹6,700 | Materials + mixing + placing |
| **Concrete (M30)** | m³ | ₹7,200 | ~₹500 premium per grade |
| **Steel (Fe500)** | kg | ₹72 | Cutting + bending + binding |
| **Formwork** | m² | ₹500 | Shuttering + propping + removal |

## 2. Cost Objective Function
The total cost $C_{total}$ for a beam of length $L$:

$$C_{total} = (C_c \cdot V_c) + (C_s \cdot W_s) + (C_f \cdot A_f) + P_{congestion}$$

### Optimization Heuristics:
- **Steel vs. Concrete:** Steel is ~10x more expensive per unit weight. Increasing depth ($D$) to reduce $A_{st}$ is the primary lever.
- **Congestion Penalty:** Apply **1.2x multiplier** to labor if $p_t > 2.5\%$.
- **Standardization:** Prefer $b$ in 230mm/300mm increments and $D$ in 50mm increments.

## 3. Data Schema (`CostProfile`)
```json
{
  "currency": "INR",
  "concrete": { "M25": 6700, "M30": 7200 },
  "steel": { "Fe500": 72 },
  "formwork_rate_per_m2": 500,
  "labor": {
    "congestion_threshold_pt": 2.5,
    "congestion_penalty_multiplier": 1.2
  }
}
```

## 4. Implementation Plan
1. **Core Layer:** `Python/structural_lib/costing.py` (Pure math for volumes/weights).
2. **App Layer:** `Python/structural_lib/optimization.py` (Candidate evaluation).
3. **API:** Update `api.py` to accept `cost_profile`.
