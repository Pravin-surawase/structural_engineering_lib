# Design Suggestions Guide

The design suggestions engine provides expert recommendations to improve your beam designs beyond basic code compliance. Think of it as having an experienced structural engineer review your work and suggest optimizations.

## Quick Start

```python
from structural_lib.beam_pipeline import design_single_beam
from structural_lib.insights import suggest_improvements

# Design your beam
design = design_single_beam(
    units="IS456",
    beam_id="B1",
    story="GF",
    b_mm=300,
    D_mm=600,  # Conservative depth
    d_mm=550,
    cover_mm=40,
    span_mm=5000,
    mu_knm=100,  # Moderate moment
    vu_kn=70,
    fck_nmm2=25,
    fy_nmm2=500,
    include_detailing=True,
)

# Get improvement suggestions
suggestions = suggest_improvements(
    design,
    span_mm=5000,
    mu_knm=100,
    vu_kn=70,
)

# Review top suggestions
for suggestion in suggestions.suggestions[:3]:
    print(f"\n{suggestion.title} ({suggestion.impact.value} impact)")
    print(f"  {suggestion.description}")
    print(f"  Expected benefit: {suggestion.estimated_benefit}")
    print(f"  Next steps:")
    for step in suggestion.action_steps:
        print(f"    • {step}")
```

**Output:**
```
Reduce section size (high impact)
  Section is oversized (utilization: 42%)
  Expected benefit: ~17% cost reduction
  Next steps:
    • Try reducing depth by 104mm
    • Re-run design with smaller section
    • Verify serviceability limits

Explore cost-optimized designs (high impact)
  Current design may not be cost-optimal
  Expected benefit: 8-20% cost reduction typical
  Next steps:
    • Run optimize_beam_cost() function
    • Compare with current design
    • Verify serviceability of optimal design
```

---

## What Gets Checked?

The engine analyzes your design across 6 categories with 17+ expert rules:

### 1. **Geometry** (5 rules)
- Oversized sections (low utilization)
- Non-standard widths
- Non-standard depths
- Excessive depth/width ratio
- Shallow beams for span

### 2. **Steel** (4 rules)
- High steel percentage (congestion risk)
- Very low steel percentage (deflection risk)
- Steel grade opportunities
- Tight stirrup spacing

### 3. **Cost** (2 rules)
- Cost optimization opportunities
- Concrete grade optimization

### 4. **Constructability** (2 rules)
- Excessive bar count
- Mixed bar diameters

### 5. **Serviceability** (2 rules)
- Span/depth ratio near limits
- Missing serviceability checks

### 6. **Materials** (2 rules)
- Uncommon concrete grades
- Material cost vs strength trade-offs

---

## Understanding Suggestions

Each suggestion includes:

### Impact Level
- **HIGH**: >15% improvement (priority score 8-10)
- **MEDIUM**: 5-15% improvement (priority score 5-7)
- **LOW**: <5% improvement (priority score 2-4)

### Confidence Score
- **0.90-1.00**: Strong evidence (codified rules, industry standards)
- **0.75-0.89**: Good evidence (common practice, textbook guidance)
- **0.60-0.74**: Reasonable evidence (heuristics, experience-based)

### Components
```python
suggestion = DesignSuggestion(
    category=SuggestionCategory.GEOMETRY,  # What aspect
    impact=ImpactLevel.HIGH,               # How much improvement
    confidence=0.85,                       # How certain
    title="Reduce section size",          # What to do
    description="Section is oversized...", # Why it matters
    rationale="Low moment utilization...", # Technical basis
    estimated_benefit="~17% cost reduction", # Expected gain
    action_steps=[...],                    # How to implement
    rule_id="G1",                          # Rule identifier
    priority_score=9.0,                    # Combined metric
)
```

---

## Common Scenarios

### Scenario 1: Conservative Design

**Situation:** You used conservative dimensions and the section is oversized.

**Suggestions you'll get:**
- `G1`: Reduce section size (HIGH impact)
- `C1`: Explore cost-optimized designs (HIGH impact)
- `C2`: Consider lower concrete grade (MEDIUM impact)

**Action:** Run cost optimization to find optimal section.

```python
from structural_lib.insights import optimize_beam_design

optimal = optimize_beam_design(
    span_mm=5000,
    mu_knm=100,
    vu_kn=70,
)

print(f"Optimal: {optimal.optimal_candidate.b_mm}x{optimal.optimal_candidate.D_mm}")
print(f"Savings: {optimal.savings_percent:.1f}%")
```

### Scenario 2: Congested Steel

**Situation:** Small section with high moment → heavy reinforcement.

**Suggestions you'll get:**
- `S1`: Reduce steel congestion (HIGH impact)
- `G4`: Depth/width ratio too high (MEDIUM impact)

**Action:** Increase section depth or width.

### Scenario 3: Non-Standard Dimensions

**Situation:** Using odd dimensions like 375mm width or 425mm depth.

**Suggestions you'll get:**
- `G2`: Use standard beam width (LOW impact)
- `G3`: Round depth to 50mm increment (LOW impact)

**Action:** Round to nearest standard dimension (230, 300, 400, 500mm for width; 50mm increments for depth).

### Scenario 4: Fe 415 Steel

**Situation:** Still using older Fe 415 grade instead of Fe 500.

**Suggestions you'll get:**
- `S3`: Use Fe 500 steel for efficiency (MEDIUM impact)

**Action:** Switch to Fe 500 (widely available, reduces steel area by ~17%).

---

## API Reference

### `suggest_improvements()`

```python
def suggest_improvements(
    design: BeamDesignOutput,
    detailing: Optional[BeamDetailingResult] = None,
    cost_profile: Optional[CostProfile] = None,
    span_mm: Optional[float] = None,
    mu_knm: Optional[float] = None,
    vu_kn: Optional[float] = None,
) -> SuggestionReport:
    """Generate design improvement suggestions."""
```

**Required Parameters:**
- `design`: Beam design output from `design_single_beam()`

**Optional Parameters (enable more rules):**
- `detailing`: Detailing result (enables constructability rules)
- `cost_profile`: Regional cost data (for cost optimization suggestions)
- `span_mm`: Beam span (enables serviceability rules)
- `mu_knm`: Factored moment (enables optimization suggestions)
- `vu_kn`: Factored shear (enables optimization suggestions)

**Returns:**
- `SuggestionReport` with prioritized list of suggestions

### `SuggestionReport`

```python
@dataclass
class SuggestionReport:
    suggestions: List[DesignSuggestion]  # Sorted by priority
    analysis_time_ms: float
    suggestions_count: int
    high_impact_count: int
    medium_impact_count: int
    low_impact_count: int
    engine_version: str  # "1.0.0"
```

**Methods:**
- `.to_dict()`: Serialize to JSON-compatible dict

### `DesignSuggestion`

```python
@dataclass
class DesignSuggestion:
    category: SuggestionCategory
    impact: ImpactLevel
    confidence: float  # 0.0-1.0
    title: str
    description: str
    rationale: str
    estimated_benefit: str
    action_steps: List[str]
    rule_id: str
    priority_score: float
```

**Methods:**
- `.to_dict()`: Serialize to JSON-compatible dict

---

## Performance

- **Analysis time:** <10ms typical (<100ms worst case)
- **Memory:** Negligible (suggestions generated on-the-fly)
- **No external dependencies:** Pure Python, deterministic

---

## Best Practices

### 1. Run Early
Get suggestions before detailed analysis to save time:

```python
design = design_single_beam(...)
suggestions = suggest_improvements(design)

if any(s.impact == ImpactLevel.HIGH for s in suggestions.suggestions):
    print("⚠️ High-impact improvements available - review before proceeding")
```

### 2. Provide Context
More parameters = better suggestions:

```python
# Minimal (basic rules only)
suggestions = suggest_improvements(design)

# Full context (all rules active)
suggestions = suggest_improvements(
    design,
    detailing=design.detailing,
    span_mm=5000,
    mu_knm=120,
    vu_kn=80,
)
```

### 3. Filter by Category

Focus on specific improvement areas:

```python
cost_suggestions = [
    s for s in suggestions.suggestions
    if s.category == SuggestionCategory.COST
]

for s in cost_suggestions:
    print(f"{s.title}: {s.estimated_benefit}")
```

### 4. Act on High-Impact First

Prioritize by impact level:

```python
high_impact = [
    s for s in suggestions.suggestions
    if s.impact == ImpactLevel.HIGH
]

if high_impact:
    print(f"⚠️ {len(high_impact)} high-impact improvements found:")
    for s in high_impact:
        print(f"  • {s.title} - {s.estimated_benefit}")
```

---

## Integration with Workflow

### Batch Design with Suggestions

```python
from structural_lib.beam_pipeline import design_multiple_beams
from structural_lib.insights import suggest_improvements

beams = [...]  # List of beam parameters
results = design_multiple_beams(units="IS456", beams=beams)

# Get suggestions for each beam
for beam_result in results.beams:
    suggestions = suggest_improvements(beam_result)

    if suggestions.high_impact_count > 0:
        print(f"\n{beam_result.beam_id}: {suggestions.high_impact_count} high-impact suggestions")

        for s in suggestions.suggestions[:2]:  # Top 2
            print(f"  • {s.title}: {s.estimated_benefit}")
```

### JSON Export

```python
suggestions = suggest_improvements(design)
data = suggestions.to_dict()

import json
with open("suggestions.json", "w") as f:
    json.dump(data, f, indent=2)
```

**Output structure:**
```json
{
  "suggestions": [
    {
      "category": "cost",
      "impact": "high",
      "confidence": 0.85,
      "title": "Explore cost-optimized designs",
      "description": "Current design may not be cost-optimal",
      "rationale": "Cost optimization algorithm can find cheaper section with same safety.",
      "estimated_benefit": "8-20% cost reduction typical",
      "action_steps": [
        "Run optimize_beam_cost() function",
        "Compare with current design",
        "Verify serviceability of optimal design"
      ],
      "rule_id": "C1",
      "priority_score": 9.0
    }
  ],
  "suggestions_count": 5,
  "high_impact_count": 2,
  "medium_impact_count": 2,
  "low_impact_count": 1,
  "engine_version": "1.0.0"
}
```

---

## Limitations

1. **No structural analysis:** Suggestions are heuristic-based, not FEM-validated
2. **Advisory only:** Always verify suggestions with proper design checks
3. **Context-dependent:** Some suggestions may not apply to your project constraints
4. **Regional variation:** Cost/constructability rules based on Indian practice
5. **No conflict resolution:** Suggestions presented independently (may conflict)

---

## Rule Reference

| Rule ID | Category | Title | Trigger | Impact |
|---------|----------|-------|---------|--------|
| **G1** | Geometry | Reduce section size | Utilization < 50% | HIGH |
| **G2** | Geometry | Use standard width | Width not in [230,300,400,500] | LOW |
| **G3** | Geometry | Round depth to 50mm | Depth not in 50mm steps | LOW |
| **G4** | Geometry | Increase width for stability | D/b > 4.0 | MEDIUM |
| **G5** | Geometry | Increase depth for span | d/span < 0.05 | HIGH |
| **S1** | Steel | Reduce steel congestion | Steel % > 2.5% | HIGH |
| **S2** | Steel | Check minimum steel | Steel % < 0.3% | MEDIUM |
| **S3** | Steel | Use Fe 500 steel | Currently Fe 415 | MEDIUM |
| **S4** | Steel | Optimize stirrup spacing | Spacing < 100mm | LOW |
| **C1** | Cost | Explore cost optimization | Utilization < 70% | HIGH |
| **C2** | Cost | Consider lower grade | fck > M30 | MEDIUM |
| **CT1** | Constructability | Reduce bar count | Bars > 6 in layer | MEDIUM |
| **CT2** | Constructability | Standardize bar sizes | >2 different diameters | LOW |
| **SV1** | Serviceability | Increase depth margin | 18 < L/d ≤ 20 | MEDIUM |
| **SV2** | Serviceability | Run serviceability checks | Checks not performed | LOW |
| **M1** | Materials | Use standard grade | Grade not in [20,25,30,35] | LOW |
| **M2** | Materials | Consider M25 vs M20 | M20 with moderate loads | MEDIUM |

---

## Version History

### v1.0.0 (2026-01-05)
- Initial release with 17 expert rules
- 6 categories: Geometry, Steel, Cost, Constructability, Serviceability, Materials
- JSON serialization support
- Comprehensive test coverage (22 tests)

---

## See Also

- [Cost Optimization Guide](./cost-optimization-guide.md) - Automated cost minimization
- [Constructability Scoring](./insights-guide.md#constructability-scoring) - Buildability assessment
- [Sensitivity Analysis](./insights-guide.md#sensitivity-analysis) - Parameter robustness
- [API Reference](../reference/insights-api.md) - Complete API documentation
