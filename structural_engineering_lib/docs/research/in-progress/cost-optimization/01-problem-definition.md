# Problem Definition: Cost Optimization for Beam Design

**Date:** 2026-01-05
**Status:** Complete
**Researcher:** User + Claude

---

## What problem are we solving?

**Problem Statement:** Structural engineers want to design beams that meet IS 456:2000 safety requirements while **minimizing total construction cost**.

Currently, engineers either:
1. Use conservative "thumb rules" → Over-design → Waste money
2. Manually try multiple configurations → Time-consuming
3. Use commercial software that doesn't optimize cost → Miss savings opportunities

**Our solution:** Automatic cost optimization that finds the cheapest design meeting all code requirements.

---

## Who has this problem?

**Primary users:**
- **Junior engineers** - Don't know cost-effective thumb rules yet
- **Design firms** - Want to win competitive bids with lower costs
- **Small contractors** - Operate on thin margins, need to save every rupee

**Market size:**
- India: 100,000+ structural engineers
- Global (IS 456 users): 150,000+ engineers
- Potential users: Every engineer designing RC beams

---

## Why does this matter?

**Business value:**
- **Time saved:** 2-3 hours per project (no manual trials)
- **Cost saved:** 10-20% on materials for typical beam
- **Win rates:** Firms can bid 5-10% lower and still profit

**Example impact:**
- Small residential project (20 beams)
  - Traditional design: ₹5,00,000 material cost
  - Optimized design: ₹4,25,000 (15% savings)
  - **Savings: ₹75,000 per project**

**Annual impact for a firm doing 10 projects:**
- Savings: ₹7,50,000/year
- **ROI on our software: Massive**

---

## Current solutions (if any)

### Manual Approach
**What engineers do today:**
1. Start with span/d ratio (thumb rule)
2. Design beam
3. Check cost
4. If too expensive, increase depth and retry
5. Repeat 3-5 times until "good enough"

**Problems:**
- Time-consuming (2-3 hours)
- May miss optimal solution
- No guarantee of cost-effectiveness

### Commercial Software (STAAD, ETABS)
**What they provide:**
- Beam design per IS 456
- Multiple trial runs

**What they DON'T provide:**
- ❌ Automatic cost optimization
- ❌ Cost comparison of alternatives
- ❌ Material quantity estimation
- ❌ Regional cost data

**Gap:** No software automatically finds cheapest design!

---

## Our unique approach

**What makes our solution different:**

1. **Automated optimization** - Not manual trials
2. **Regional cost data** - India-specific rates (CPWD DSR 2023)
3. **Constructability-aware** - Penalizes impractical designs
4. **Instant comparison** - Show savings vs standard design
5. **Integrated in workflow** - Not a separate tool

**Competitive advantage:** First structural design tool with built-in cost optimization.

---

## Success criteria

**How do we know if we solved it?**

### Functional Requirements
- [ ] Find cheapest design meeting IS 456:2000
- [ ] Handle realistic constraints (max depth, standard sizes)
- [ ] Include constructability penalties
- [ ] Return savings percentage vs standard design
- [ ] Run in < 5 seconds for typical beam

### Quality Metrics
1. **Correctness:** All designs must pass IS 456 compliance
2. **Cost savings:** 10-20% vs conservative design
3. **Speed:** < 5 seconds for single beam
4. **Accuracy:** Within 5% of true optimal (if verified manually)

### User Acceptance
- [ ] Engineer trusts the recommendation
- [ ] Can explain why this design is optimal
- [ ] Clear documentation of cost breakdown
- [ ] Warnings if unusual design (e.g., very deep beam)

---

## Cost Model (From User's Research)

Based on CPWD DSR 2023 and market trends:

| Component | Unit | Rate (INR) | Notes |
|-----------|------|-----------|-------|
| Concrete (M25) | m³ | ₹6,700 | Materials + mixing + placing |
| Concrete (M30) | m³ | ₹7,200 | ~₹500 premium per grade |
| Steel (Fe500) | kg | ₹72 | Cutting + bending + binding |
| Formwork | m² | ₹500 | Shuttering + propping + removal |

**Cost Objective Function:**

$$C_{total} = (C_c \cdot V_c) + (C_s \cdot W_s) + (C_f \cdot A_f) + P_{congestion}$$

Where:
- $C_c$ = Concrete cost per m³
- $V_c$ = Concrete volume (b × D × L)
- $C_s$ = Steel cost per kg
- $W_s$ = Steel weight (Ast × L × 7850 kg/m³)
- $C_f$ = Formwork cost per m²
- $A_f$ = Formwork area (2(b+D) × L)
- $P_{congestion}$ = Penalty for high steel ratio

---

## Optimization Heuristics (From User's Research)

**Key insights:**

1. **Steel is 10x more expensive than concrete (per volume)**
   - Strategy: Increase depth to reduce steel area

2. **Congestion penalty**
   - If pt > 2.5% → Apply 1.2x labor multiplier
   - Reason: Dense reinforcement is harder to place

3. **Standardization bonus**
   - Prefer standard sizes: b ∈ {230, 300, 400}, D ∈ {50mm increments}
   - Reason: Easier to procure formwork

4. **Formwork cost matters**
   - Deeper beams = more formwork area
   - Balance: steel savings vs formwork cost increase

---

## Constraints

**Hard constraints (Must satisfy):**
- IS 456:2000 compliance (all clauses)
- Minimum steel ratio (pt,min)
- Maximum steel ratio (pt,max)
- Minimum cover
- Spacing limits

**Soft constraints (Prefer but not required):**
- Standard widths (230, 300, 400mm)
- Standard depths (multiples of 50mm)
- Depth-to-width ratio (typically 1.5-3.0)
- Constructability (pt < 2.5% ideal)

---

## Design Space

**Variables to optimize:**
- Width (b): 230-600mm
- Depth (D): 300-900mm
- Concrete grade (fck): 20, 25, 30, 35 N/mm²
- Steel grade (fy): 415, 500 N/mm²

**Fixed inputs:**
- Span (L)
- Loads (dead, live)
- Factored moment (Mu)
- Support conditions

**Search space size:**
- Width: ~15 options (230-600 in 30mm steps)
- Depth: ~20 options (300-900 in 50mm steps)
- Grades: 4 × 2 = 8 combinations
- **Total: 2,400 combinations** (brute force feasible!)

---

## Next Steps (Research Timeline)

**Day 1 (Today):** ✅ Problem definition complete

**Day 2 (Tomorrow):**
- Literature review: Optimization algorithms
- Algorithm selection: Brute force vs heuristic vs genetic

**Day 3:**
- Prototype implementation
- Test on 10 sample beams
- Validate cost savings

**Day 4:**
- Refine algorithm based on testing
- Create implementation spec for Copilot

**Day 5+:**
- Copilot implements production version
- Integration tests
- Documentation

---

## Open Questions

1. Should we optimize for just one beam, or system of beams?
   - Decision: Start with single beam, extend to system later

2. Should we include labor cost variations by region?
   - Decision: Start with national average, add regional later

3. How to handle uncertainty in material prices?
   - Decision: Use CPWD DSR as baseline, allow user override

4. Should we consider lifecycle costs (maintenance)?
   - Decision: No - focus on initial construction cost only

---

## References

- CPWD DSR 2023 (Central Public Works Department Schedule of Rates)
- IS 456:2000 (Indian Standard for Plain and Reinforced Concrete)
- User's domain expertise (market rates, constructability insights)

---

**Status:** Problem well-defined. Ready to proceed to algorithm selection (Day 2).
