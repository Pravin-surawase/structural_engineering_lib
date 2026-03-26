# API Integration Mistakes Analysis - Root Cause and Prevention

**Type:** Research
**Audience:** All Agents
**Status:** Approved
**Importance:** Critical
**Created:** 2026-01-24
**Last Updated:** 2026-01-24
**Related Tasks:** SESSION-73
**Abstract:** Analysis of API signature guessing failures during FastAPI implementation, with systemic fixes to prevent future agents from making the same mistakes.

---

## Problem Statement

During Session 73, implementing FastAPI backend wrappers for `structural_lib.api` resulted in **7 failing tests** (29% failure rate) due to incorrect API parameter names and return type assumptions. Despite having 3000+ lines of comprehensive API documentation at [docs/reference/api.md](../reference/api.md), the agent guessed signatures incorrectly.

### What Happened

| Error | Wrong Assumption | Correct Value | Debug Time |
|-------|------------------|---------------|------------|
| Parameter names | `width`, `depth`, `moment` | `b_mm`, `D_mm`, `mu_knm` | ~15 min |
| Units parameter | `"mm_kN_MPa"` | `"IS456"` | ~5 min |
| Result structure | `result.results[0]` | `result.cases[0]` | ~10 min |
| CostProfile params | `concrete_per_m3` | `concrete_costs={25: 6000}` | ~5 min |

**Total debug time:** ~35 minutes fixing avoidable errors.

---

## Root Cause Analysis

### A. Missing Task-to-Context Mapping

The `automation-map.json` has entries for:
- ✅ "check api docs" → links to api.md
- ✅ "validate fastapi schema" → links to api.md
- ❌ "implement api wrapper" → **DOES NOT EXIST**
- ❌ "create fastapi endpoint" → **DOES NOT EXIST**

### B. Bootstrap Doesn't Enforce API Doc Reading

[agent-bootstrap.md](../getting-started/agent-bootstrap.md) mentions api.md in "Essential Links" but doesn't **require** reading it for API wrapper tasks.

### C. No Pre-Implementation Validation

For git workflows, we have extensive pre-commit hooks.
For API wrappers, we have **nothing** that:
1. Forces agent to discover signatures first
2. Validates parameter names match documentation
3. Checks return types before writing code

### D. Trial-and-Error Was Faster (But Wrong)

Agent reasoned:
> "I'll write the code, run tests, and fix what fails"

This created 7 iterations of fixes and wasted 35 minutes.

---

## Solutions

### Solution 1: API Signature Discovery Script ⭐ CRITICAL

**Create:** `scripts/discover_api_signatures.py`

```bash
# Usage BEFORE implementing any API wrapper:
.venv/bin/python scripts/discover_api_signatures.py design_beam_is456
.venv/bin/python scripts/discover_api_signatures.py --all
```

**Output:**
```
design_beam_is456:
  Parameters:
    units: str (REQUIRED) - Must be "IS456"
    b_mm: float (REQUIRED)
    D_mm: float (REQUIRED)
    mu_knm: float (REQUIRED)
    fck_nmm2: float (REQUIRED)
  Returns: ComplianceCaseResult
    .flexure.ast_required, .flexure.mu_lim
    .shear.tv, .shear.tc, .shear.spacing
```

### Solution 2: Update automation-map.json ⭐ CRITICAL

Add new task mappings:

```json
"implement api wrapper": {
  "prereq": ".venv/bin/python scripts/discover_api_signatures.py <function>",
  "description": "ALWAYS discover signatures before wrapping",
  "context_docs": ["docs/reference/api.md"],
  "never_use": ["guess parameter names", "assume return types"]
}
```

### Solution 3: Update agent-essentials.md ⭐ HIGH

Add API Wrapper Rule:
```markdown
## API Wrapper Rule
Before wrapping ANY structural_lib.api function:
1. Run: .venv/bin/python scripts/discover_api_signatures.py <function>
2. Read: docs/reference/api.md (search for function name)
3. Test: Call function in Python REPL first
```

### Solution 4: Update copilot-instructions.md ⭐ HIGH

Add to Common Mistakes table:
```markdown
| Guessing API signatures | Failed tests, debug loops | Discover signatures first | discover_api_signatures.py |
```

---

## Correct API Signatures Reference

### design_beam_is456

```python
design_beam_is456(
    units="IS456",  # REQUIRED, must be "IS456"
    b_mm=300,       # Not "width"
    D_mm=500,       # Not "depth"
    d_mm=450,       # Not "effective_depth"
    mu_knm=150,     # Not "moment"
    vu_kn=75,       # Not "shear"
    fck_nmm2=25,    # Not "fck"
    fy_nmm2=500,    # Not "fy"
)
# Returns: ComplianceCaseResult
# Access: result.flexure.ast_required, result.shear.tv
```

### check_beam_is456

```python
check_beam_is456(
    units="IS456",
    cases=[{"label": "DL+LL", "mu_knm": 150, "vu_kn": 75}],  # Not case_id
    b_mm=300, D_mm=500, d_mm=450, fck_nmm2=25, fy_nmm2=500,
)
# Returns: ComplianceReport
# Access: result.cases[0].flexure  # NOT result.results[0]
```

### CostProfile Constructor

```python
CostProfile(
    concrete_costs={25: 6000, 30: 6800},  # dict, NOT concrete_per_m3
    steel_cost_per_kg=72.0,               # NOT steel_per_kg
    formwork_cost_per_m2=500.0,           # NOT formwork_per_m2
)
```

### SmartAnalysisResult Structure

```python
result = smart_analyze_design(...)
# Access:
result.summary_data["safety_score"]        # NOT result.design
result.suggestions["suggestions"]          # dict, NOT list
result.cost["current_cost"]                # dict
# NOT: result.efficiency, result.compliance_checks
```

---

## Implementation Checklist

### Immediate (This Session)

- [ ] Create `scripts/discover_api_signatures.py`
- [ ] Update `scripts/automation-map.json`
- [ ] Update `.github/copilot-instructions.md`
- [ ] Update `docs/getting-started/agent-essentials.md`

### Future

- [ ] Add CI check for API wrapper parameter validation
- [ ] Create `scripts/validate_api_wrapper.py`

---

## Lessons Learned

1. **Read documentation FIRST** - 3000 lines of docs existed; 5 min reading saves 35 min debugging
2. **Discover signatures programmatically** - `inspect.signature()` is authoritative
3. **Test in REPL first** - Verify API call works before writing wrapper
4. **Don't guess, verify** - Return types change between versions

---

## Related Documents

- [docs/reference/api.md](../reference/api.md) - API Reference (3000+ lines)
- [scripts/automation-map.json](../../scripts/automation-map.json) - Task mappings
- [.github/copilot-instructions.md](../../.github/copilot-instructions.md) - Agent rules
