# Research Methodology for Smart Library

**Purpose:** Systematic approach to research, document, and implement smart features that differentiate our platform.

**Philosophy:** Research-driven development → Build features backed by solid research, not speculation.

---

## Research Workflow

```
1. Problem Definition (Claude)
   ↓
2. Literature Review (Claude + Background Agent)
   ↓
3. Data Collection (Claude + Web Research)
   ↓
4. Algorithm/Approach Selection (Claude)
   ↓
5. Validation Strategy (Claude)
   ↓
6. Implementation Spec (Claude → Copilot)
   ↓
7. Implementation (Copilot + Test Agent)
   ↓
8. Validation (Claude + Test Data)
   ↓
9. Documentation (Copilot)
```

**Time per feature:** 2-3 days (with AI agents), not 3-4 weeks

---

## Research Template

For each smart feature, create a research folder with these documents:

### **01-problem-definition.md**

```markdown
# Problem Definition: [Feature Name]

## What problem are we solving?
[Clear statement of the problem]

## Who has this problem?
[Target users: Junior engineers? Senior engineers? Firms?]

## Why does this matter?
[Business value: Time saved? Cost reduced? Errors prevented?]

## Current solutions (if any)
[What do engineers do today? Manual calculations? Commercial software?]

## Our unique approach
[What makes our solution different/better?]

## Success criteria
[How do we know if we solved it?]
- Metric 1: ...
- Metric 2: ...
```

### **02-literature-review.md**

```markdown
# Literature Review: [Feature Name]

## Academic Papers
1. [Paper title](link)
   - Key findings: ...
   - Relevant algorithms: ...
   - Limitations: ...

## Industry Standards
1. IS 456:2000 clauses: ...
2. Best practices from: ...

## Existing Implementations
1. Software X does: ...
   - Strengths: ...
   - Weaknesses: ...
   - Can we do better?

## Key Insights
[Synthesize what you learned]

## Approach Decision
[Based on research, what approach will we use?]
```

### **03-data-collection.md**

```markdown
# Data Collection: [Feature Name]

## Data Needed
- [ ] Material costs (India, 2025)
- [ ] Labor rates by region
- [ ] Historical beam designs
- [ ] Failure case studies

## Data Sources
1. Source 1: [Link/Contact]
   - What we get: ...
   - Quality: ...
   - Cost: Free/Paid

## Data Validation
[How do we ensure data quality?]

## Data Storage
[Where/how to store? CSV? Database?]
```

### **04-algorithm-exploration.md**

```markdown
# Algorithm Exploration: [Feature Name]

## Candidate Approaches

### Approach 1: [Name]
- **Description:** ...
- **Pros:** ...
- **Cons:** ...
- **Complexity:** O(...)
- **Accuracy:** ...
- **Example:** ...

### Approach 2: [Name]
- **Description:** ...
- **Pros:** ...
- **Cons:** ...

## Recommended Approach
[Which one and why?]

## Prototype Code
```python
# Quick prototype to test concept
def feature_prototype(inputs):
    # ...
    pass
```

## Test Results
[Results from prototype testing]
```

### **05-validation-plan.md**

```markdown
# Validation Plan: [Feature Name]

## How do we know it works?

### Test Cases
1. **Simple beam (residential)**
   - Input: ...
   - Expected output: ...
   - Tolerance: ±5%

2. **Complex beam (commercial)**
   - Input: ...
   - Expected output: ...

### Benchmark Comparison
[Compare our results to commercial software/manual calculations]

### Edge Cases
[What edge cases must we handle?]

### Performance
[Speed requirements? Must run in <1 second?]

## Validation Data
[Real-world beams to test on]
```

### **implementation-spec.md** (Hand to Copilot)

```markdown
# Implementation Specification: [Feature Name]

**For:** GitHub Copilot
**From:** Claude (based on research)

## API Design

```python
def smart_feature_name(
    param1: float,
    param2: float,
    config: Optional[FeatureConfig] = None
) -> FeatureResult:
    """
    [Clear docstring]

    Args:
        param1: Description
        param2: Description
        config: Optional configuration

    Returns:
        FeatureResult with:
            - result: Main output
            - confidence: 0-1 confidence score
            - warnings: List of warnings
            - suggestions: List of suggestions

    Examples:
        >>> result = smart_feature_name(300, 450)
        >>> result.result
        120.5
    """
    pass
```

## Implementation Steps

1. Create `Python/structural_lib/insights/[feature_name].py`
2. Implement core algorithm (from 04-algorithm-exploration.md)
3. Add validation logic
4. Add error handling
5. Write unit tests (from 05-validation-plan.md)
6. Add to `insights/__init__.py`

## Test Requirements

```python
# tests/test_insights_[feature_name].py

def test_simple_case():
    # From validation plan test case 1
    result = smart_feature_name(...)
    assert result.result == pytest.approx(expected, rel=0.05)

def test_complex_case():
    # From validation plan test case 2
    ...

def test_edge_cases():
    # From validation plan edge cases
    ...
```

## Dependencies
[Any new libraries needed?]

## Performance Target
[Must run in <1 second for typical inputs]

## Estimated Implementation Time
[With Copilot: X hours]
```

---

## Agent Roles in Research

### **Claude (Main Agent - You)**
- Problem definition
- Literature review coordination
- Algorithm selection
- Research synthesis
- Create implementation specs
- Validation review

### **Background Research Agent**
- Web research (papers, standards, docs)
- Data collection (scraping, API calls)
- Benchmark testing (run comparisons)
- Runs in parallel, doesn't block main work

### **GitHub Copilot**
- Implement from spec
- Write unit tests
- Refactor code
- Generate documentation

### **Test Agent**
- Run validation tests
- Generate test data
- Coverage reports
- Regression testing

---

## Example: Cost Optimization Research (Your Top Priority)

### **Week 1: Research Phase (Claude + Background Agent)**

**Day 1: Problem Definition**
- Claude writes `01-problem-definition.md`
- Identifies: Engineers want to minimize material + labor costs
- Success: Find cheapest design that meets IS 456

**Day 2: Literature Review**
- Background Agent searches academic papers on structural optimization
- Claude reviews findings, selects approach
- Decision: Multi-objective optimization (cost vs constructability)

**Day 3: Data Collection**
- Background Agent scrapes material prices (cement, steel, formwork)
- Claude validates data quality
- Store in `data/material_costs_india_2025.csv`

**Day 4: Algorithm Exploration**
- Claude prototypes 3 approaches:
  1. Brute force (try all combinations)
  2. Genetic algorithm
  3. Gradient descent
- Prototype code in Jupyter notebook
- Test on 10 sample beams
- Decision: Genetic algorithm (best results)

**Day 5: Validation Plan**
- Claude defines 20 test beams
- Get manual calculations from engineer
- Define acceptance criteria: Within 5% of manual

### **Week 2: Implementation Phase (Copilot + Test Agent)**

**Day 1-2: Implementation**
- Claude writes `implementation-spec.md`
- Copilot implements `cost_optimization.py`
- Test Agent generates unit tests

**Day 3: Validation**
- Run on 20 test beams
- Compare to manual calculations
- All within 5%? ✅ Ship it!

**Day 4: Documentation**
- Copilot generates API docs
- Claude writes user guide with examples

**Day 5: Integration**
- Add to `insights/__init__.py`
- Update main library API
- Release as part of v1.0

**Total time: 10 days (not 3-4 weeks!)**

---

## Research Repository Structure

```
docs/research/
├── README.md (this file)
├── RESEARCH_METHODOLOGY.md
├── completed/
│   ├── precheck/
│   │   ├── 01-problem-definition.md
│   │   ├── 02-literature-review.md
│   │   ├── implementation-spec.md
│   │   └── validation-results.md
│   ├── sensitivity/
│   └── constructability/
├── in-progress/
│   ├── cost-optimization/        ← CURRENT
│   │   ├── 01-problem-definition.md
│   │   ├── 02-literature-review.md (Claude working)
│   │   └── ...
│   └── design-suggestions/
└── backlog/
    ├── ml-predictions/
    ├── failure-prediction/
    └── code-compliance-ai/
```

---

## Research Metrics (Track Progress)

| Feature | Status | Research Days | Impl Days | Total | Confidence |
|---------|--------|--------------|-----------|-------|------------|
| Precheck | ✅ Done | 3 | 2 | 5 | High |
| Sensitivity | ✅ Done | 2 | 2 | 4 | Medium |
| Constructability | ✅ Done | 2 | 2 | 4 | Medium |
| **Cost Optimization** | 🔄 Research | 3/5 | 0/2 | 3/7 | TBD |
| Design Suggestions | ⏸️ Backlog | 0/4 | 0/3 | 0/7 | TBD |
| ML Predictions | ⏸️ Backlog | 0/6 | 0/4 | 0/10 | TBD |

---

## Key Principles

1. **Research BEFORE coding** - Don't guess, research
2. **Document everything** - Future you will thank you
3. **Validate rigorously** - Smart features must be correct
4. **Iterate quickly** - AI agents enable fast cycles
5. **Build on research** - Each feature builds on previous research

---

## Next Steps

1. **Set up research folders** for top 3 smart features
2. **Start with cost optimization** (highest ROI)
3. **Use agent orchestration** to parallelize research
4. **Review research weekly** with Claude
5. **Ship when validated**, not when "done"

---

**Remember:** Your competitive advantage is smart features. Invest time in research to build features that competitors can't easily replicate.
