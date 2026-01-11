# Independent Verification Checklist

**Document Type:** Quality Assurance Checklist
**Status:** Template
**Version:** 0.16.5
**Last Updated:** 2026-01-11

---

## Purpose

This checklist provides a structured approach for independent verification of
calculations produced by `structural-lib-is456`. Use this for quality control
and peer review processes.

---

## Part A: Pre-Calculation Checks

### A1. Project Information
| Item | Verified | Notes |
|------|:--------:|-------|
| Project name and reference correct | ☐ | |
| Design code specified (IS 456:2000) | ☐ | |
| Any code amendments identified | ☐ | |
| Design load combinations documented | ☐ | |

### A2. Input Data
| Item | Verified | Notes |
|------|:--------:|-------|
| Beam dimensions match drawings | ☐ | |
| Material grades specified correctly | ☐ | |
| Clear cover appropriate for exposure | ☐ | |
| Span lengths and support conditions | ☐ | |
| Effective depth calculation | ☐ | |

### A3. Loading
| Item | Verified | Notes |
|------|:--------:|-------|
| Dead load calculation | ☐ | |
| Live load per IS 875 or project spec | ☐ | |
| Load factor applied (1.5 DL+LL typical) | ☐ | |
| Moment and shear from analysis | ☐ | |

---

## Part B: Calculation Verification

### B1. Flexure Design (IS 456 Annex G)
| Check | Hand Calc | Software | Match? |
|-------|-----------|----------|:------:|
| Mu,lim calculation | | | ☐ |
| Section type (under/over-reinforced) | | | ☐ |
| Required Ast | | | ☐ |
| Provided reinforcement | | | ☐ |

### B2. Shear Design (IS 456 Clause 40)
| Check | Hand Calc | Software | Match? |
|-------|-----------|----------|:------:|
| Design shear Vu | | | ☐ |
| τv (nominal shear stress) | | | ☐ |
| τc (design shear strength) | | | ☐ |
| Stirrup spacing | | | ☐ |

### B3. Detailing (IS 456 Clause 26)
| Check | Verified | Notes |
|------|:--------:|-------|
| Minimum reinforcement (0.85bd/fy) | ☐ | |
| Maximum reinforcement (4% Ag) | ☐ | |
| Clear spacing ≥ max(bar dia, 25mm) | ☐ | |
| Development length | ☐ | |
| Anchorage at supports | ☐ | |

---

## Part C: Serviceability Checks

### C1. Deflection (IS 456 Clause 23.2)
| Item | Value | Limit | Pass? |
|------|-------|-------|:-----:|
| Basic L/d ratio | | | ☐ |
| Modification factor (tension steel) | | | ☐ |
| Modification factor (compression steel) | | | ☐ |
| Actual L/d ratio | | | ☐ |

### C2. Crack Width (IS 456 Clause 35.3.2)
| Item | Value | Limit | Pass? |
|------|-------|-------|:-----:|
| Exposure class | | | ☐ |
| Maximum crack width | | | ☐ |
| Calculated crack width | | | ☐ |

---

## Part D: Summary

### Verification Outcome
| Category | Status |
|----------|--------|
| Input data correct | ☐ Pass ☐ Fail |
| Flexure design adequate | ☐ Pass ☐ Fail |
| Shear design adequate | ☐ Pass ☐ Fail |
| Detailing compliant | ☐ Pass ☐ Fail |
| Serviceability satisfied | ☐ Pass ☐ Fail |

### Comments
```
[Add any comments, discrepancies, or recommendations here]




```

### Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Design Engineer | | | |
| Checker | | | |
| Approver | | | |

---

## Related Documents

- [certification-template.md](certification-template.md) - PE certification guidance
- [usage-guidelines.md](usage-guidelines.md) - Professional use guidance
- [LICENSE_ENGINEERING.md](../../LICENSE_ENGINEERING.md) - Engineering disclaimer
