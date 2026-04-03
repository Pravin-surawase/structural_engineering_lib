---
Type: Research
Audience: All Agents
Status: Draft
Importance: High
Created: 2026-04-03
Last Updated: 2026-04-03
---

# Innovation: Sustainability Scoring — Embodied Carbon per Beam Design

**Innovation Domain:** #1 — Sustainability Scoring
**Impact Level:** 🌍 Planet
**Prototype:** `Python/structural_lib/research/research_sustainability.py`

## Problem Statement

Every beam design in our library produces structural results (area of steel, utilization, safety checks) and cost estimates — but **zero information about environmental impact**. Engineers designing RC structures in India have no way to:

1. Know the **embodied carbon (kgCO₂e)** of their chosen beam cross-section
2. **Compare alternatives** by carbon, not just cost — a 300×500 M25 beam vs 230×600 M30
3. Track designs against **net-zero targets** (ECBC 2017, GRIHA, UK NZCBS)
4. Make **carbon-cost trade-off decisions** — sometimes 5% more cost = 20% less carbon

This is a massive gap. The IStructE's "How to Calculate Embodied Carbon" (3rd ed, Jan 2025) makes this a **core competency** for structural engineers. The ICE Database v4.1 (Oct 2025) by Circular Ecology is the global standard for embodied carbon factors, used by 50,000+ professionals.

**No open-source structural design library scores individual element designs for carbon.** ETABS, SAP2000, SAFE — none of them do this at the element level. This would make us the first.

## Current State

What our library already has:
- `services/costing.py` — `calculate_concrete_volume()`, `calculate_steel_weight()`, `CostProfile`, `CostBreakdown`
- `insights/cost_optimization.py` — `optimize_beam_design()` finds cheapest design
- `insights/comparison.py` — `compare_designs()` multi-criteria comparison (safety, cost, constructability, robustness)
- `insights/sensitivity.py` — parameter sensitivity analysis
- `insights/design_suggestions.py` — rule-based improvement suggestions

What's missing:
- Carbon emission factors for concrete grades (M20-M40) and steel rebar
- Carbon scoring function that takes design inputs → kgCO₂e breakdown
- Carbon intensity metrics (kgCO₂e/m, kgCO₂e/kN·m capacity)
- Carbon rating system (A-E scale with benchmarks)
- Integration with existing comparison and optimization modules

## Proposed Approach

### Carbon Calculation Method

Based on IStructE guidance + ICE Database v4.1:

$$EC_{total} = EC_{concrete} + EC_{steel}$$

Where:
- $EC_{concrete} = V_{concrete} \times EF_{concrete}(f_{ck})$ — volume × emission factor per grade
- $EC_{steel} = W_{steel} \times EF_{steel}$ — weight × emission factor for rebar

Emission factors (kgCO₂e per unit) from ICE Database v4.1:

| Material | Unit | Factor (kgCO₂e) | Source |
|----------|------|-----------------|--------|
| Concrete M20 (C20/25) | per m³ | 240 | ICE v4.1 |
| Concrete M25 (C25/30) | per m³ | 290 | ICE v4.1 |
| Concrete M30 (C30/37) | per m³ | 340 | ICE v4.1 |
| Concrete M35 (C35/45) | per m³ | 390 | ICE v4.1 |
| Concrete M40 (C40/50) | per m³ | 440 | ICE v4.1 |
| Steel rebar (global avg) | per kg | 1.40 | ICE v4.1 |
| Steel rebar (India EAF) | per kg | 1.10 | ICE v4.1, adjusted |

Note: Indian concrete emission factors are adjusted upward from European values because Indian cement production is more carbon-intensive (higher clinker ratio, older kilns in many plants). These are conservative estimates.

### Carbon Rating System

| Rating | kgCO₂e per kN·m capacity | Interpretation |
|--------|--------------------------|----------------|
| A+ | < 1.5 | Exceptional — minimal carbon |
| A | 1.5 – 2.5 | Excellent — well-optimized |
| B | 2.5 – 4.0 | Good — typical efficient design |
| C | 4.0 – 6.0 | Average — room for improvement |
| D | 6.0 – 10.0 | Below average — review design |
| E | > 10.0 | Poor — significant optimization needed |

### Key Metrics

1. **Total embodied carbon** (kgCO₂e) — absolute emission
2. **Carbon intensity** (kgCO₂e per m beam length) — normalized per length
3. **Carbon efficiency** (kgCO₂e per kN·m capacity) — carbon per unit structural utility
4. **Concrete carbon share** (%) — how much comes from concrete vs steel
5. **Carbon rating** (A+ to E) — quick visual indicator

## Data Requirements

- Concrete volume: already computed by `costing.calculate_concrete_volume()`
- Steel weight: already computed by `costing.calculate_steel_weight()`
- Emission factors: hardcoded from ICE Database v4.1 (publicly available data)
- No external data sources needed for v1 prototype

## Implementation Sketch

### New Module
`Python/structural_lib/research/research_sustainability.py`

### Functions
1. `score_beam_carbon(b_mm, D_mm, span_mm, fck, ast_mm2, asc_mm2=0)` → `CarbonScore`
2. `compare_carbon(designs: list)` → comparison table
3. `carbon_vs_cost_tradeoff(span_mm, mu_knm, vu_kn)` → Pareto-ish analysis

### Data Types
```python
@dataclass
class CarbonScore:
    total_kgco2e: float           # Total embodied carbon
    concrete_kgco2e: float        # Concrete contribution
    steel_kgco2e: float           # Steel contribution
    carbon_per_meter: float       # kgCO2e/m beam length
    carbon_per_knm: float         # kgCO2e per kN·m capacity
    concrete_share_pct: float     # % from concrete
    steel_share_pct: float        # % from steel
    rating: str                   # "A+" to "E"
    rating_description: str       # Human-readable
```

### Architecture Fit
- **Layer:** Research (prototype) — will move to `insights/` when production-ready
- **Dependencies:** Only `services/costing.py` (for volume/weight utilities)
- **Import direction:** research → services → core ✓ (never upward)

### Production Path (after validation)
1. Move to `insights/sustainability.py`
2. Add `CarbonProfile` to `services/costing.py` (parallel to `CostProfile`)
3. Wire into `compare_designs()` as a 5th comparison dimension
4. Add to `optimize_beam_cost()` as carbon-aware optimization mode
5. FastAPI endpoint: `POST /api/v1/insights/carbon`
6. React: carbon badge in `ResultsPanel`, carbon column in `BeamTable`

## Validation Plan

1. **Unit test:** Known concrete volume × emission factor = expected kgCO₂e
2. **Cross-check:** Compare with IStructE Structural Carbon Tool (Excel) results
3. **Sensitivity:** Verify that M30 beam has higher carbon than M25 for same dimensions
4. **Integration:** Run on all existing test beam designs, verify no crashes
5. **Engineering review:** @structural-engineer validates factors and methodology

## IS 456 Clause Map

| Clause | Relationship | Notes |
|--------|-------------|-------|
| All clauses | Unaffected | Carbon scoring is a post-design analysis — it does NOT modify any IS 456 calculations |
| Cl 26.5.1 | Read-only | Minimum steel ratio affects carbon floor |
| Table 2 | Read-only | Concrete grade affects emission factor selection |

**Important:** This innovation adds information to designs — it never changes structural calculations, safety factors, or code minimums.

## Impact Assessment

| Criterion | Score (1-10) | Notes |
|-----------|-------------|-------|
| Engineering Value | 9 | Every engineer needs this for net-zero compliance |
| Uniqueness | 9 | No open-source structural library does element-level carbon scoring |
| Feasibility | 10 | We already have volume/weight calculations — just add emission factors |
| Data Availability | 8 | ICE Database is public, well-established, annually updated |
| User Demand | 9 | GRIHA, ECBC 2017, UK NZCBS all require embodied carbon reporting |
| Code Integration | 9 | Fits perfectly into insights layer, reuses costing infrastructure |
| Safety | 10 | Pure analysis — cannot produce unsafe designs (no modification of structural calculations) |
| **Total** | **64/70** | Well above 40/70 threshold |

## Next Steps — Delegation Plan

1. **@structural-engineer:** Verify emission factors and methodology against IStructE guidance
2. **@structural-math:** Move validated prototype to `insights/sustainability.py` with full type annotations
3. **@tester:** Write unit tests (target: 95% branch coverage for sustainability module)
4. **@api-developer:** Add `POST /api/v1/insights/carbon` endpoint
5. **@frontend:** Add carbon badge to `ResultsPanel`, carbon column to comparison views
6. **@security:** Review — low risk (pure computation, no external data at runtime)

## References

- ICE Database v4.1 (Oct 2025) — Circular Ecology / University of Bath
- IStructE "How to Calculate Embodied Carbon" 3rd ed (Jan 2025)
- UK Net Zero Carbon Buildings Standard v1 (Mar 2026)
- ECBC 2017 — India Energy Conservation Building Code
- GRIHA — Green Rating for Integrated Habitat Assessment
