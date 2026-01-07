# TASK-142: Design Suggestions Engine

**Status:** 🎯 READY
**Priority:** 🔴 HIGH
**Agent:** DEV
**Estimated Time:** 2-3 days
**Created:** 2026-01-06

---

## Objective

Build an AI-driven design suggestions engine that provides smart recommendations for beam design based on heuristics and IS 456 best practices.

---

## Requirements

### 1. Rule-Based Expert System
- Implement 20+ heuristics from IS 456 and practical experience
- Confidence scoring (0-100%) for each suggestion
- Context-aware recommendations (span, load, usage type)

### 2. Data Structures

```python
from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class DesignSuggestion:
    """A single design suggestion with confidence and rationale."""

    suggestion_type: str  # "dimension", "material", "optimization", "compliance"
    message: str  # Human-readable suggestion
    confidence: float  # 0.0 to 1.0
    rationale: str  # Why this suggestion is made
    impact: str  # "high", "medium", "low"
    clause_reference: Optional[str] = None  # IS 456 clause if applicable

    def __post_init__(self):
        """Validate fields."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")
        if self.impact not in ["high", "medium", "low"]:
            raise ValueError(f"Impact must be high/medium/low, got {self.impact}")
        if self.suggestion_type not in ["dimension", "material", "optimization", "compliance"]:
            raise ValueError(f"Invalid suggestion_type: {self.suggestion_type}")


@dataclass
class SuggestionResult:
    """Complete suggestion analysis result."""

    suggestions: List[DesignSuggestion]
    risk_level: str  # "low", "medium", "high"
    overall_score: float  # 0-100 (higher = better design quality)
    categories: Dict[str, List[DesignSuggestion]]  # Grouped by type

    def __post_init__(self):
        """Auto-categorize suggestions."""
        if not self.categories:
            self.categories = {
                "dimension": [],
                "material": [],
                "optimization": [],
                "compliance": []
            }
            for sug in self.suggestions:
                self.categories[sug.suggestion_type].append(sug)
```

### 3. Core Functions

```python
def suggest_beam_design(
    span_mm: float,
    mu_knm: float,
    vu_kn: float,
    usage_type: str = "residential",  # residential, commercial, industrial
    current_design: Optional[Dict] = None,
    fck_nmm2: Optional[int] = None,
    fy_nmm2: Optional[int] = None
) -> SuggestionResult:
    """Generate smart design suggestions.

    Args:
        span_mm: Beam span (mm)
        mu_knm: Factored bending moment (kNm)
        vu_kn: Factored shear force (kN)
        usage_type: Building usage type (affects recommendations)
        current_design: Optional current design dict for improvement suggestions
        fck_nmm2: Proposed concrete grade (optional)
        fy_nmm2: Proposed steel grade (optional)

    Returns:
        SuggestionResult with categorized suggestions

    Example:
        >>> result = suggest_beam_design(
        ...     span_mm=6000,
        ...     mu_knm=200,
        ...     vu_kn=120,
        ...     usage_type="commercial"
        ... )
        >>> print(f"Risk Level: {result.risk_level}")
        >>> print(f"Overall Score: {result.overall_score}/100")
        >>> for sug in result.suggestions:
        ...     print(f"{sug.message} (confidence: {sug.confidence*100:.0f}%)")
    """
    pass
```

### 4. Heuristics to Implement

**DIMENSION Heuristics:**
1. ✅ **Span/Depth Ratio** (Confidence: 95%)
   - If span/d > 20 → "Consider increasing depth for deflection control" (IS 456 Cl 23.2)
   - If span/d < 10 → "Beam is very deep, may be over-designed"

2. ✅ **Beam Width** (Confidence: 90%)
   - If b < 230mm → "Narrow beam - check bar spacing and constructability"
   - If b < span/50 → "Width too narrow for span, suggest b ≥ span/50"

3. ✅ **Depth Recommendation** (Confidence: 85%)
   - Residential: suggest D = span/15 to span/12
   - Commercial: suggest D = span/12 to span/10
   - Industrial: suggest D = span/10 to span/8

4. ✅ **Width-to-Depth Ratio** (Confidence: 80%)
   - If b/D < 0.4 → "Deep beam behavior - consider IS 456 Cl 29.1"
   - If b/D > 2.0 → "Wide shallow beam - check shear capacity"

**MATERIAL Heuristics:**
5. ✅ **Concrete Grade Selection** (Confidence: 90%)
   - If residential + span > 6m → "Consider M25 minimum for durability"
   - If commercial → "Suggest M30 for better durability and reduced maintenance"
   - If industrial + heavy loads → "Suggest M30 or higher for long-term performance"

6. ✅ **Steel Grade** (Confidence: 85%)
   - If new construction → "Use Fe500 (modern standard, better economy)"
   - If rehabilitation → "Check existing grade compatibility"

7. ✅ **Grade vs Moment** (Confidence: 80%)
   - If high Mu + M20 → "Consider upgrading to M25/M30 for easier reinforcement"

**OPTIMIZATION Heuristics:**
8. ✅ **Steel Percentage** (Confidence: 95%)
   - If pt < 0.2% → "Below minimum steel - add reinforcement" (IS 456 Cl 26.5.1.1)
   - If pt > 2.5% → "High congestion - suggest increasing depth" (Constructability)
   - If pt > 4.0% → "Exceeds maximum - must increase section" (IS 456 Cl 26.5.1.1)

9. ✅ **Cost Optimization** (Confidence: 85%)
   - If pt > 1.5% → "Run cost optimizer - increasing depth may save money"
   - If narrow beam + high steel → "Wider section may be more economical"

10. ✅ **Deflection Risk** (Confidence: 90%)
    - If span > 6m + shallow → "High deflection risk - check serviceability"
    - If live load > dead load → "Check long-term deflection carefully"

**COMPLIANCE Heuristics:**
11. ✅ **Minimum Cover** (Confidence: 95%)
    - If mild exposure → "Suggest cover = 25mm" (IS 456 Cl 26.4)
    - If moderate exposure → "Suggest cover = 30mm"
    - If severe exposure → "Suggest cover = 45mm minimum"

12. ✅ **Bar Spacing** (Confidence: 90%)
    - If b < 300mm + large bars → "Check min clear spacing (bar_dia or 25mm)"
    - Warn if spacing violations likely

13. ✅ **Development Length** (Confidence: 85%)
    - If large bars + short span → "Check adequate development length at supports"

14. ✅ **Stirrup Spacing** (Confidence: 95%)
    - If high shear → "Max spacing = min(0.75d, 300mm)" (IS 456 Cl 26.5.1.5)
    - If low shear → "Max spacing = d or 300mm"

15. ✅ **Ductility (IS 13920)** (Confidence: 90%)
    - If seismic zone → "Apply ductile detailing - closer stirrups, min 2 bars top/bottom"

**ADVANCED Heuristics:**
16. ✅ **Doubly Reinforced Check** (Confidence: 85%)
    - If Mu > 0.9 × Mu_lim → "Near singly reinforced limit - consider compression steel"

17. ✅ **Flanged Beam Opportunity** (Confidence: 75%)
    - If part of floor system → "Consider T/L beam for economy"

18. ✅ **Torsion Warning** (Confidence: 80%)
    - If edge beam or significant eccentricity → "Check torsion requirements"

19. ✅ **Temperature & Shrinkage** (Confidence: 70%)
    - If long beam (> 10m) → "Consider temperature/shrinkage reinforcement"

20. ✅ **Construction Sequence** (Confidence: 75%)
    - If heavy beam → "Plan lifting points and temporary supports"

21. ✅ **Multi-Span Continuity** (Confidence: 80%)
    - If continuous beam → "Add top reinforcement at supports"

22. ✅ **Fire Resistance** (Confidence: 70%)
    - If commercial/public → "Verify cover for required fire rating"

### 5. Confidence Scoring Logic

```python
def calculate_confidence(heuristic_type: str, conditions: Dict) -> float:
    """Calculate confidence based on input quality and applicability.

    Base confidence levels:
    - Code-based rules (IS 456): 90-95%
    - Practical experience: 75-85%
    - Optimization hints: 70-80%
    - Advanced considerations: 65-75%

    Adjust down if:
    - Missing optional inputs (-10%)
    - Edge case conditions (-5-15%)
    - Conflicting indicators (-10-20%)
    """
    pass
```

### 6. Risk Level Calculation

```python
def calculate_risk_level(suggestions: List[DesignSuggestion]) -> str:
    """Determine overall risk level.

    HIGH risk if:
    - Any compliance violations (pt < min, pt > max, cover insufficient)
    - Structural safety concerns (span/d extreme, shear capacity)

    MEDIUM risk if:
    - Optimization opportunities missed
    - Constructability issues likely
    - Deflection/serviceability concerns

    LOW risk if:
    - Only minor optimization suggestions
    - All code requirements clearly met
    """
    pass
```

### 7. Overall Score Calculation

```python
def calculate_overall_score(design_params: Dict, suggestions: List[DesignSuggestion]) -> float:
    """Calculate design quality score 0-100.

    Scoring:
    - Start at 100
    - Deduct for each issue:
      - High impact compliance issue: -15 points
      - Medium impact optimization miss: -5 points
      - Low impact suggestion: -2 points
    - Floor at 0, cap at 100

    Score interpretation:
    - 90-100: Excellent design
    - 75-89: Good design with minor improvements possible
    - 60-74: Acceptable but needs optimization
    - 40-59: Poor design, significant issues
    - 0-39: Unacceptable, major violations
    """
    pass
```

---

## Files to Create

1. **`Python/structural_lib/insights/design_suggestions.py`**
   - All data structures and core functions
   - 22+ heuristic implementations
   - Confidence/risk/score calculators

2. **`Python/tests/test_design_suggestions.py`**
   - Test each heuristic independently (22+ tests)
   - Test edge cases (narrow beams, long spans, etc.)
   - Test confidence scoring
   - Test risk level assignment
   - Test overall scoring
   - Test categorization
   - **Minimum 30 tests total**

3. **Update `Python/structural_lib/insights/__init__.py`**
   ```python
   from .design_suggestions import suggest_beam_design, DesignSuggestion, SuggestionResult

   __all__ = [
       # ... existing ...
       "suggest_beam_design",
       "DesignSuggestion",
       "SuggestionResult",
   ]
   ```

4. **Update `Python/structural_lib/api.py`**
   ```python
   def suggest_beam_design_smart(
       *,
       units: str,
       span_mm: float,
       mu_knm: float,
       vu_kn: float,
       usage_type: str = "residential",
       fck_nmm2: Optional[int] = None,
       fy_nmm2: Optional[int] = None
   ) -> Dict[str, Any]:
       """Get AI-driven design suggestions (IS456 units)."""
       _require_is456_units(units)

       from structural_lib.insights import suggest_beam_design

       result = suggest_beam_design(
           span_mm=span_mm,
           mu_knm=mu_knm,
           vu_kn=vu_kn,
           usage_type=usage_type,
           fck_nmm2=fck_nmm2,
           fy_nmm2=fy_nmm2
       )

       return {
           "suggestions": [
               {
                   "type": s.suggestion_type,
                   "message": s.message,
                   "confidence_percent": round(s.confidence * 100, 1),
                   "rationale": s.rationale,
                   "impact": s.impact,
                   "clause": s.clause_reference
               }
               for s in result.suggestions
           ],
           "risk_level": result.risk_level,
           "overall_score": result.overall_score,
           "categories": {
               cat: len(sugs) for cat, sugs in result.categories.items()
           }
       }
   ```

5. **Documentation: `docs/reference/insights.md`**
   - Add design_suggestions section
   - Example usage
   - Heuristic reference table
   - Confidence scoring explanation

---

## Acceptance Criteria

- [ ] All 22 heuristics implemented with IS 456 references
- [ ] Confidence scoring works correctly (0-100%)
- [ ] Risk level calculation (low/medium/high)
- [ ] Overall score calculation (0-100)
- [ ] Categorization by type (dimension/material/optimization/compliance)
- [ ] 30+ unit tests covering all heuristic types
- [ ] API integration complete (`api.suggest_beam_design_smart`)
- [ ] All existing tests still passing (2040+ tests)
- [ ] Documentation with examples
- [ ] Type hints on all functions
- [ ] Docstrings following NumPy/Google style

---

## Example Usage

```python
from structural_lib.insights import suggest_beam_design

# Example 1: Pre-design suggestions
result = suggest_beam_design(
    span_mm=6000,
    mu_knm=200,
    vu_kn=120,
    usage_type="commercial"
)

print(f"Overall Design Score: {result.overall_score}/100")
print(f"Risk Level: {result.risk_level}")
print(f"\nSuggestions by Category:")

for category, suggestions in result.categories.items():
    if suggestions:
        print(f"\n{category.upper()}:")
        for sug in suggestions:
            print(f"  [{sug.impact.upper()}] {sug.message}")
            print(f"    Confidence: {sug.confidence*100:.0f}%")
            if sug.clause_reference:
                print(f"    Reference: {sug.clause_reference}")

# Example 2: With proposed design
result = suggest_beam_design(
    span_mm=5000,
    mu_knm=150,
    vu_kn=90,
    usage_type="residential",
    current_design={
        "b_mm": 230,
        "D_mm": 400,
        "d_mm": 360,
        "ast_mm2": 1200
    },
    fck_nmm2=25,
    fy_nmm2=500
)

print(f"\nDesign Review Score: {result.overall_score}/100")
if result.risk_level != "low":
    print(f"⚠️ Risk Level: {result.risk_level.upper()}")
    high_impact = [s for s in result.suggestions if s.impact == "high"]
    for sug in high_impact:
        print(f"  • {sug.message}")
```

---

## Testing Strategy

### Unit Tests (22+ tests, one per heuristic)
```python
def test_span_depth_ratio_warning():
    """Test span/d ratio heuristic triggers correctly."""
    result = suggest_beam_design(span_mm=8000, mu_knm=100, vu_kn=50)
    # Should suggest deflection check if d < 400 (span/d > 20)
    # ...

def test_narrow_beam_warning():
    """Test narrow beam width detection."""
    # ...

def test_steel_percentage_limits():
    """Test pt min/max violation detection."""
    # ...
```

### Integration Tests (8+ tests)
```python
def test_residential_beam_suggestions():
    """Test complete suggestion flow for residential beam."""
    # ...

def test_commercial_heavy_beam():
    """Test suggestions for heavy commercial beam."""
    # ...

def test_risk_level_high_for_violations():
    """Ensure HIGH risk for code violations."""
    # ...
```

---

## Research Resources

- IS 456:2000 Clauses (especially 23, 26, 29)
- `docs/research/in-progress/cost-optimization/` (for pattern reference)
- Existing `insights/precheck.py` (for heuristic patterns)
- `insights/constructability.py` (for scoring approach)
- `insights/sensitivity.py` (for analysis patterns)

---

## Notes for Implementation

1. **Start with core data structures** - get DesignSuggestion and SuggestionResult working first
2. **Implement 5 heuristics at a time** - test each batch before moving on
3. **Use descriptive messages** - suggestions should be actionable, not vague
4. **Reference IS 456 clauses** - builds user trust and enables learning
5. **Keep confidence realistic** - don't over-promise (75-95% typical range)
6. **Test edge cases** - very short spans, very long spans, extreme loads
7. **Follow existing patterns** - look at precheck.py for structure

---

**Ready for Agent Pickup:** ✅ YES
**Dependencies:** None (uses existing modules)
**Estimated Completion:** 2-3 days with focused development
