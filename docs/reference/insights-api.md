# Insights API Reference

> **Status:** Preview (v0.13.0+)
> **Stability:** Experimental - API may change before v1.0

Complete API reference for the advisory insights module.

---

## Module: `structural_lib.insights`

### Imports

```python
from structural_lib.insights import (
    # Functions
    quick_precheck,
    sensitivity_analysis,
    calculate_robustness,
    calculate_constructability_score,

    # Types
    HeuristicWarning,
    PredictiveCheckResult,
    SensitivityResult,
    RobustnessScore,
    ConstructabilityFactor,
    ConstructabilityScore,
)
```

---

## Functions

### `quick_precheck()`

Fast heuristic validation before detailed design.

**Signature:**

```python
def quick_precheck(
    *,
    span_mm: float,
    b_mm: float,
    d_mm: float,
    D_mm: float,
    mu_knm: float,
    fck_nmm2: float,
    fy_nmm2: float = 500.0,
    support_condition: SupportCondition = SupportCondition.SIMPLY_SUPPORTED,
) -> PredictiveCheckResult:
```

**Parameters:**

- `span_mm` (float) - Clear span in mm
- `b_mm` (float) - Beam width in mm
- `d_mm` (float) - Effective depth in mm
- `D_mm` (float) - Total depth in mm
- `mu_knm` (float) - Factored moment in kNm
- `fck_nmm2` (float) - Concrete strength in N/mm²
- `fy_nmm2` (float, optional) - Steel yield strength in N/mm² (default: 500)
- `support_condition` (SupportCondition, optional) - Support type (default: SIMPLY_SUPPORTED)

**Returns:**

`PredictiveCheckResult` with:
- `risk_level`: "LOW" | "MEDIUM" | "HIGH"
- `warnings`: List[HeuristicWarning]
- `recommended_action`: "proceed" | "review" | "revise"
- `check_time_ms`: Execution time in milliseconds

**Example:**

```python
result = quick_precheck(
    span_mm=5000,
    b_mm=300,
    d_mm=450,
    D_mm=500,
    mu_knm=140,
    fck_nmm2=25,
    fy_nmm2=500,
)

if result.risk_level == "HIGH":
    for warning in result.warnings:
        print(f"{warning.severity}: {warning.message}")
```

**Checks Performed:**

1. **Depth adequacy** (IS 456 Cl. 23.2)
   - Compares d with minimum required depth
   - Warning if span/depth ratio is too high

2. **Flexural capacity estimate**
   - Quick estimate of Ast,req using simplified formula
   - Warning if required area seems excessive

3. **Geometry ratios**
   - Checks b/D ratio (typical: 0.5-0.7)
   - Checks d/D ratio (typical: 0.85-0.92)

**Complexity:** O(1) - constant time (~0.1-0.5ms)

---

### `sensitivity_analysis()`

Analyze parameter sensitivity using finite difference method.

**Signature:**

```python
def sensitivity_analysis(
    design_function: Callable[..., Any],
    base_params: Dict[str, Any],
    parameters_to_vary: Iterable[str] | None = None,
    perturbation: float = 0.10,
) -> Tuple[List[SensitivityResult], RobustnessScore]:
```

**Parameters:**

- `design_function` (Callable) - Design function that returns result with `governing_utilization` and `is_ok`
- `base_params` (Dict[str, Any]) - Baseline parameter values
- `parameters_to_vary` (Iterable[str] | None) - Parameters to analyze (default: all numeric parameters)
- `perturbation` (float) - Fractional perturbation (default: 0.10 = 10%)

**Returns:**

Tuple of:
- `List[SensitivityResult]` - Per-parameter sensitivities (sorted by |sensitivity|)
- `RobustnessScore` - Overall design robustness

**Example:**

```python
from structural_lib.api import design_beam_is456

params = {
    "units": "IS456",
    "mu_knm": 140,
    "vu_kn": 85,
    "b_mm": 300,
    "D_mm": 500,
    "d_mm": 450,
    "fck_nmm2": 25,
    "fy_nmm2": 500,
}

sensitivities, robustness = sensitivity_analysis(
    design_beam_is456,
    params,
    parameters_to_vary=["d_mm", "b_mm", "fck_nmm2"],
    perturbation=0.10,  # 10% perturbation
)

# Most critical parameter
critical = sensitivities[0]
print(f"{critical.parameter}: S={critical.sensitivity:.2f}")
```

**Algorithm:**

1. Compute base utilization: `U_base = design(**base_params).governing_utilization`
2. For each parameter `p`:
   - Perturb: `p' = p × (1 + perturbation)`
   - Compute: `U_perturbed = design(**perturbed_params).governing_utilization`
   - Calculate normalized sensitivity: `S = (ΔU/U) / (Δp/p)`
   - Classify impact based on |S|

3. Compute robustness score from sensitivities

**Sensitivity Coefficient:**

```
S = (ΔU/U_base) / (Δp/p_base)
```

Where:
- `ΔU = U_perturbed - U_base` (change in utilization)
- `Δp = p_perturbed - p_base` (change in parameter)

**Dimensionless and comparable across parameter types:**
- `S = -2.0`: 10% increase in parameter → 20% decrease in utilization
- `S = +0.5`: 10% increase in parameter → 5% increase in utilization

**Impact Classification:**

- `|S| > 2.0` → **Critical** (extreme sensitivity)
- `|S| > 1.0` → **High** (very sensitive)
- `|S| > 0.5` → **Medium** (moderately sensitive)
- `|S| ≤ 0.5` → **Low** (weakly sensitive)

**Complexity:** O(N×M) where N = number of parameters, M = design function complexity

**Typical runtime:** ~1-5 seconds for 4-6 parameters

---

### `calculate_robustness()`

Calculate design robustness score from sensitivity results.

**Signature:**

```python
def calculate_robustness(
    sensitivities: List[SensitivityResult],
    base_utilization: float,
    failure_threshold: float = 1.0,
) -> RobustnessScore:
```

**Parameters:**

- `sensitivities` (List[SensitivityResult]) - Sensitivity results (from `sensitivity_analysis`)
- `base_utilization` (float) - Current utilization ratio (e.g., 0.78)
- `failure_threshold` (float) - Failure threshold (default: 1.0)

**Returns:**

`RobustnessScore` with:
- `score`: 0.0-1.0 (1.0 = very robust)
- `rating`: "excellent" | "good" | "acceptable" | "poor"
- `vulnerable_parameters`: List of critical/high-impact parameters
- `base_utilization`: Current utilization ratio
- `sensitivity_count`: Number of parameters analyzed

**Method:**

1. Compute margin to failure: `margin = 1.0 - base_utilization`
2. For each parameter with negative sensitivity (helps when increased):
   - Calculate allowable decrease: `δ = margin / (U_base × |S|)`
3. Robustness = `min(δ) / 0.20` (normalized to 0-1)

**Rating Thresholds:**

- `≥0.80` → **Excellent** (can tolerate 20%+ variations)
- `≥0.65` → **Good** (robust for normal tolerances)
- `≥0.50` → **Acceptable** (requires QC)
- `<0.50` → **Poor** (fragile, little margin)

**Example:**

```python
# Manual calculation
robustness = calculate_robustness(
    sensitivities=sensitivities,
    base_utilization=0.78,
    failure_threshold=1.0,
)

if robustness.rating == "poor":
    print(f"Warning: Design is fragile (score={robustness.score:.2f})")
    print(f"Vulnerable to: {', '.join(robustness.vulnerable_parameters)}")
```

**Note:** Usually called automatically by `sensitivity_analysis()`.

---

### `calculate_constructability_score()`

Assess construction ease on 0-100 scale.

**Signature:**

```python
def calculate_constructability_score(
    design_result: ComplianceCaseResult,
    detailing: BeamDetailingResult,
) -> ConstructabilityScore:
```

**Parameters:**

- `design_result` (ComplianceCaseResult) - Design result with utilization data
- `detailing` (BeamDetailingResult) - Detailing with bar layouts and stirrup configuration

**Returns:**

`ConstructabilityScore` with:
- `score`: 0-100 (higher = easier to construct)
- `rating`: "excellent" | "good" | "acceptable" | "poor"
- `factors`: List[ConstructabilityFactor] - Factor-by-factor breakdown
- `overall_message`: Summary message
- `version`: Scoring algorithm version

**Scoring Factors:**

| Factor | Weight | Criteria |
|--------|--------|----------|
| Bar clear spacing | 20 pts | <40mm (congested), <60mm (tight) |
| Stirrup spacing | 20 pts | <100mm (very tight), <125mm (tight) |
| Bar variety | 10 pts | >2 sizes (procurement complexity) |
| Standard sizes | 10 pts | Non-standard sizes (8,10,12,16,20,25,32mm) |
| Layer count | 15 pts | >2 layers (congestion) |
| Depth increments | 5 pts | Not 50mm multiple (formwork cost) |
| Bar configuration | 10 pts | >5 bars/layer (complexity) |

**Score Interpretation:**

- **85-100**: Excellent - Easy construction, low labor cost
- **70-84**: Good - Typical construction complexity
- **55-69**: Acceptable - Requires experienced crew
- **<55**: Poor - Congested, high rework risk

**Example:**

```python
from structural_lib.api import design_beam_is456
from structural_lib.detailing import create_beam_detailing
from structural_lib.insights import calculate_constructability_score

# Get design and detailing
design = design_beam_is456(...)
detailing = create_beam_detailing(...)

# Score constructability
score = calculate_constructability_score(design, detailing)

print(f"Score: {score.score:.0f}/100 ({score.rating})")

# Review factors
for factor in score.factors:
    if factor.penalty < 0:
        print(f"❌ {factor.factor}: {factor.message}")
        if factor.recommendation:
            print(f"   → {factor.recommendation}")
```

**Basis:** Singapore BDAS framework (Poh & Chen, 1998, *Construction Management and Economics*)

---

## Data Types

### `HeuristicWarning`

Warning from heuristic pre-check.

**Fields:**

```python
@dataclass(frozen=True)
class HeuristicWarning:
    type: str                  # "depth" | "flexure" | "geometry"
    severity: Severity         # ERROR | WARNING | INFO
    message: str              # Human-readable description
    suggestion: str           # Recommended action
    rule_basis: str           # Code clause reference
```

**Methods:**

- `to_dict() -> Dict[str, Any]` - Convert to JSON-serializable dict

**Example:**

```python
{
    "type": "depth",
    "severity": "warning",
    "message": "Effective depth (400mm) is below recommended minimum (420mm) for this span",
    "suggestion": "Increase depth to at least 420mm",
    "rule_basis": "IS 456 Cl. 23.2 (span/depth limits)"
}
```

---

### `PredictiveCheckResult`

Results from quick heuristic validation.

**Fields:**

```python
@dataclass(frozen=True)
class PredictiveCheckResult:
    check_time_ms: float              # Execution time
    risk_level: str                   # "LOW" | "MEDIUM" | "HIGH"
    warnings: List[HeuristicWarning]  # List of warnings
    recommended_action: str           # "proceed" | "review" | "revise"
    heuristics_version: str           # Algorithm version
```

**Methods:**

- `to_dict() -> Dict[str, Any]` - Convert to JSON-serializable dict

---

### `SensitivityResult`

Sensitivity of one parameter.

**Fields:**

```python
@dataclass(frozen=True)
class SensitivityResult:
    parameter: str              # Parameter name (e.g., "d_mm")
    base_value: float          # Baseline value
    perturbed_value: float     # Perturbed value
    base_utilization: float    # Baseline utilization ratio
    perturbed_utilization: float  # Perturbed utilization ratio
    delta_utilization: float   # Change in utilization
    sensitivity: float         # Normalized coefficient S
    impact: str                # "critical" | "high" | "medium" | "low"
```

**Methods:**

- `to_dict() -> Dict[str, Any]` - Convert to JSON-serializable dict

**Example:**

```python
{
    "parameter": "d_mm",
    "base_value": 450.0,
    "perturbed_value": 495.0,
    "base_utilization": 0.78,
    "perturbed_utilization": 0.61,
    "delta_utilization": -0.17,
    "sensitivity": -2.37,
    "impact": "critical"
}
```

---

### `RobustnessScore`

Overall design robustness assessment.

**Fields:**

```python
@dataclass(frozen=True)
class RobustnessScore:
    score: float                        # 0.0-1.0 (1.0 = very robust)
    rating: str                         # "excellent" | "good" | "acceptable" | "poor"
    vulnerable_parameters: List[str]    # Critical/high-impact parameters
    base_utilization: float             # Current utilization ratio
    sensitivity_count: int              # Number of parameters analyzed
```

**Methods:**

- `to_dict() -> Dict[str, Any]` - Convert to JSON-serializable dict

---

### `ConstructabilityFactor`

One factor in constructability assessment.

**Fields:**

```python
@dataclass(frozen=True)
class ConstructabilityFactor:
    factor: str          # Factor name (e.g., "bar_spacing")
    score: float         # Bonus points (if positive)
    penalty: float       # Penalty points (if negative)
    message: str         # Description
    recommendation: str  # Suggested action (empty if no issue)
```

**Methods:**

- `to_dict() -> Dict[str, Any]` - Convert to JSON-serializable dict

---

### `ConstructabilityScore`

Overall constructability assessment.

**Fields:**

```python
@dataclass(frozen=True)
class ConstructabilityScore:
    score: float                            # 0-100 (higher = easier to construct)
    rating: str                             # "excellent" | "good" | "acceptable" | "poor"
    factors: List[ConstructabilityFactor]   # Factor-by-factor breakdown
    overall_message: str                    # Summary message
    version: str                            # Scoring algorithm version
```

**Methods:**

- `to_dict() -> Dict[str, Any]` - Convert to JSON-serializable dict

---

## Error Handling

### Common Errors

**`ValueError: perturbation must be > 0`**

Raised by `sensitivity_analysis()` if perturbation ≤ 0.

```python
# Fix: Use positive perturbation
sensitivity_analysis(..., perturbation=0.10)  # ✅
```

**`AttributeError: 'NoneType' object has no attribute 'governing_utilization'`**

Raised if design function doesn't return proper result.

```python
# Ensure design function returns ComplianceCaseResult
def my_design_func(**params):
    result = design_beam_is456(**params)
    return result  # Must have governing_utilization attribute
```

### Handling Failed Designs

If base design fails (utilization > 1.0), sensitivity analysis will return poor robustness:

```python
design = design_beam_is456(**params)

if not design.is_ok:
    print("Warning: Base design failed - fix design before running sensitivity")
else:
    sensitivities, robustness = sensitivity_analysis(...)
```

---

## Performance

| Function | Typical Time | Complexity |
|----------|--------------|------------|
| `quick_precheck()` | 0.1-0.5 ms | O(1) |
| `sensitivity_analysis()` (N=4) | 1-5 seconds | O(N×M) |
| `calculate_constructability_score()` | <1 ms | O(K) |

Where:
- N = number of parameters
- M = design function complexity (~200-500ms)
- K = number of bars + stirrups (~10-30)

**Optimization tips:**

- Limit `parameters_to_vary` to 4-6 most critical parameters
- Use smaller `perturbation` if design is near failure (more stable)
- Cache design results if running multiple sensitivity analyses

---

## Version History

- **v0.13.0 (2025-12-31)**: Initial preview release
  - Added `quick_precheck()`, `sensitivity_analysis()`, `calculate_constructability_score()`
  - JSON serialization via `.to_dict()` methods
  - CLI integration with `--insights` flag

---

## See Also

- [Insights User Guide](../getting-started/insights-guide.md)
- [Sensitivity Analysis Blog Post](../publications/blog-posts/03-sensitivity-analysis/)
- [Main API Reference](api.md)

---

**Last updated:** 2025-12-31
**Version:** v0.12.0 (preview)
