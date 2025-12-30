# Error Schema v1

*Structured error format for machine-readable and human-friendly errors*

**Status:** Implemented (v0.10.5)
**Last updated:** 2025-12-28

---

## Overview

This document defines the standard error schema for all structural_lib errors. The goal is:
- **Machine-readable:** Parseable by downstream tools (JSON, CI, dashboards)
- **Human-friendly:** Clear hints for engineers to fix issues
- **Traceable:** Links to IS 456 clauses where applicable

**Implementation:** See `structural_lib/errors.py` for the `DesignError` dataclass.

---

## Error Schema

### Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | string | ✅ | Unique error code (e.g., `E001`, `E_FLEXURE_001`) |
| `severity` | string | ✅ | One of: `error`, `warning`, `info` |
| `field` | string | ❌ | Input field that caused the error (e.g., `b`, `fck`, `Mu`) |
| `message` | string | ✅ | Human-readable error description |
| `hint` | string | ❌ | Actionable suggestion to fix the error |
| `clause` | string | ❌ | IS 456 clause reference (e.g., `Cl. 26.5.1.1`) |

### JSON Example

```json
{
  "code": "E_FLEXURE_001",
  "severity": "error",
  "field": "Mu",
  "message": "Mu exceeds Mu_lim. Doubly reinforced section required.",
  "hint": "Use design_doubly_reinforced() or increase section depth.",
  "clause": "Cl. 38.1"
}
```

---

## Error Code Catalog

### Severity Definitions

| Severity | Meaning | Action |
|----------|---------|--------|
| `error` | Design fails. Cannot proceed. | Must fix before using result. |
| `warning` | Design passes but has concerns. | Review and acknowledge. |
| `info` | Informational only. | No action required. |

### Error Code Prefixes

| Prefix | Module | Examples |
|--------|--------|----------|
| `E_INPUT_` | Input validation | `E_INPUT_001` (negative dimension) |
| `E_FLEXURE_` | Flexure design | `E_FLEXURE_001` (Mu > Mu_lim) |
| `E_SHEAR_` | Shear design | `E_SHEAR_001` (tv > tc_max) |
| `E_DUCTILE_` | Ductile detailing | `E_DUCTILE_001` (pt > pt_max) |
| `E_DETAILING_` | Detailing | `E_DETAILING_001` (spacing too small) |
| `E_SERVICE_` | Serviceability | `E_SERVICE_001` (deflection limit) |
| `W_` | Warnings | `W_MIN_STEEL` (near minimum steel) |

### Error Code Registry

#### Input Validation (`E_INPUT_`)

| Code | Field | Message | Hint |
|------|-------|---------|------|
| `E_INPUT_001` | `b` | `b must be > 0` | Check beam width input. |
| `E_INPUT_002` | `d` | `d must be > 0` | Check effective depth input. |
| `E_INPUT_003` | `d_total` | `d_total must be > d` | Ensure D > d + cover. |
| `E_INPUT_003a` | `d_total` | `d_total must be > 0` | Check overall depth input. |
| `E_INPUT_004` | `fck` | `fck must be > 0` | Use valid concrete grade (15-80 N/mm²). |
| `E_INPUT_005` | `fy` | `fy must be > 0` | Use valid steel grade (250/415/500/550). |
| `E_INPUT_006` | `Mu` | `Mu must be >= 0` | Check moment input sign. |
| `E_INPUT_007` | `Vu` | `Vu must be >= 0` | Check shear input sign. |
| `E_INPUT_008` | `asv` | `asv must be > 0` | Provide stirrup area. |
| `E_INPUT_009` | `pt` | `pt must be >= 0` | Check tension steel percentage. |
| `E_INPUT_010` | `d_dash` | `d_dash must be > 0` | Check compression steel cover input. |
| `E_INPUT_011` | `min_long_bar_dia` | `min_long_bar_dia must be > 0` | Provide smallest longitudinal bar diameter. |
| `E_INPUT_012` | `bw` | `bw must be > 0` | Check web width input. |
| `E_INPUT_013` | `bf` | `bf must be > 0` | Check flange width input. |
| `E_INPUT_014` | `Df` | `Df must be > 0` | Check flange thickness input. |
| `E_INPUT_015` | `bf` | `bf must be >= bw` | Ensure flange width is not smaller than web width. |
| `E_INPUT_016` | `Df` | `Df must be < d` | Ensure flange thickness is less than effective depth. |

#### Flexure (`E_FLEXURE_`)

| Code | Field | Message | Hint | Clause |
|------|-------|---------|------|--------|
| `E_FLEXURE_001` | `Mu` | `Mu exceeds Mu_lim` | Use doubly reinforced or increase depth. | Cl. 38.1 |
| `E_FLEXURE_002` | `Ast` | `Ast < Ast_min` | Increase steel to meet minimum. | Cl. 26.5.1.1 |
| `E_FLEXURE_003` | `Ast` | `Ast > Ast_max` | Reduce steel or increase section. | Cl. 26.5.1.1 |
| `E_FLEXURE_004` | `d_dash` | `d' too large for doubly reinforced` | Reduce compression steel cover. | — |

#### Shear (`E_SHEAR_`)

| Code | Field | Message | Hint | Clause |
|------|-------|---------|------|--------|
| `E_SHEAR_001` | `tv` | `tv exceeds tc_max` | Increase section size. | Cl. 40.2.3 |
| `E_SHEAR_002` | `spacing` | `Spacing exceeds maximum` | Reduce stirrup spacing. | Cl. 26.5.1.6 |
| `E_SHEAR_003` | `tv` | `Nominal shear < Tc. Provide minimum shear reinforcement.` | Minimum stirrups per Cl. 26.5.1.6. | Cl. 26.5.1.6 |
| `E_SHEAR_004` | `fck` | `fck outside Table 19 range (15-40). Using nearest bound values.` | Use fck within 15-40 or confirm conservative design. | Table 19 |

#### Ductile Detailing (`E_DUCTILE_`)

| Code | Field | Message | Hint | Clause |
|------|-------|---------|------|--------|
| `E_DUCTILE_001` | `b` | `Width < 200 mm` | Increase beam width to ≥ 200 mm. | IS 13920 Cl. 6.1.1 |
| `E_DUCTILE_002` | `b/D` | `Width/Depth ratio < 0.3` | Increase width or reduce depth. | IS 13920 Cl. 6.1.2 |
| `E_DUCTILE_003` | `D` | `Invalid depth` | Depth must be > 0. | IS 13920 Cl. 6.1 |

#### Serviceability (`E_SERVICE_`)

| Code | Field | Message | Hint | Clause |
|------|-------|---------|------|--------|
| `E_SERVICE_001` | `deflection` | `Deflection exceeds L/250` | Increase depth or add compression steel. | Cl. 23.2 |
| `E_SERVICE_002` | `crack_width` | `Crack width exceeds limit` | Reduce bar spacing or diameter. | Cl. 35.3.2 |

#### Warnings (`W_`)

| Code | Field | Message | Hint |
|------|-------|---------|------|
| `W_MIN_STEEL` | `Ast` | `Ast near minimum (< 1.1 × Ast_min)` | Consider increasing for safety margin. |
| `W_HIGH_UTIL` | `utilization` | `Utilization > 95%` | Consider design margin for construction tolerance. |
| `W_NOMINAL_SHEAR` | `tv` | `tv < tc, minimum shear reinforcement required` | Provide minimum stirrups. |

---

## Integration with Result Dataclasses

### Current State (Inconsistent)

| Module | Field | Format |
|--------|-------|--------|
| `flexure.py` | `error_message` | Plain string |
| `shear.py` | `remarks` | Plain string |
| CLI | stderr | Plain string |

### Target State (Consistent)

All result dataclasses should include:

```python
@dataclass
class DesignError:
    """Structured error for design results."""
    code: str
    severity: str  # "error" | "warning" | "info"
    message: str
    field: Optional[str] = None
    hint: Optional[str] = None
    clause: Optional[str] = None

@dataclass
class FlexureResult:
    # ... existing fields ...
    errors: List[DesignError] = field(default_factory=list)

    @property
    def is_safe(self) -> bool:
        return not any(e.severity == "error" for e in self.errors)
```

---

## CLI Error Output

### Current

```
Error: Mu exceeds Mu_lim. Doubly reinforced section required.
```

### Target

```
[E_FLEXURE_001] error: Mu exceeds Mu_lim
  Field: Mu
  Hint: Use design_doubly_reinforced() or increase section depth.
  Clause: Cl. 38.1
```

### JSON Mode (--format json)

```json
{
  "success": false,
  "errors": [
    {
      "code": "E_FLEXURE_001",
      "severity": "error",
      "field": "Mu",
      "message": "Mu exceeds Mu_lim",
      "hint": "Use design_doubly_reinforced() or increase section depth.",
      "clause": "Cl. 38.1"
    }
  ]
}
```

---

## Implementation Plan

### W04: Implement in Core (3 functions)

1. Create `structural_lib/errors.py` with `DesignError` dataclass
2. Update `flexure.design_singly_reinforced()` to use structured errors
3. Update `shear.design_shear()` to use structured errors
4. Update `ductile.check_ductility()` to use structured errors
5. Add tests for error schema compliance

### W05: Input Validation Pass

1. Add `E_INPUT_*` errors to all geometry/material validation
2. Ensure all `is_safe=False` results have at least one error with code

### Future

- CLI structured output (W40)
- JSON schema for errors (TASK-090)

---

## Migration Notes

### Backward Compatibility

- `error_message` and `remarks` fields remain for backward compat
- New `errors` list is the canonical source
- `error_message = errors[0].message` for simple access

### Breaking Changes (v1.0)

- `is_safe` becomes computed from `errors` list
- `remarks` deprecated in favor of `errors`

---

*See also: [api.md](api.md), [known-pitfalls.md](known-pitfalls.md)*
