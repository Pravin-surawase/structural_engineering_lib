# Professional Certification Template

**Document Type:** PE/Licensed Engineer Certification Guidance
**Status:** Template
**Version:** 0.16.5
**Last Updated:** 2026-01-11

---

## Purpose

This document provides guidance for licensed professional engineers who wish to
use outputs from `structural-lib-is456` in their professional practice. It is
NOT a legal document and does not replace professional judgment or regulatory
requirements.

---

## Certification Checklist

Before signing or sealing any design that uses calculations from this library,
the licensed engineer should verify:

### 1. Input Verification

- [ ] All input dimensions have been verified against project drawings
- [ ] Material properties match specified materials
- [ ] Load values are from appropriate load analysis
- [ ] Exposure conditions are correctly specified
- [ ] Support conditions accurately reflect structural system

### 2. Calculation Verification

- [ ] IS 456:2000 clause references are appropriate for the design
- [ ] Local code amendments or variations have been checked
- [ ] Assumptions are documented and appropriate for the project
- [ ] Limiting conditions (min/max values) are satisfied
- [ ] At least one independent check has been performed

### 3. Output Review

- [ ] Reinforcement quantities are reasonable for the member size
- [ ] Detailing meets minimum/maximum spacing requirements
- [ ] Utilization ratios are within acceptable limits
- [ ] Serviceability checks (deflection, cracking) pass
- [ ] Any warnings or design notes have been addressed

### 4. Documentation

- [ ] Input data is documented and archived
- [ ] Calculation outputs are saved with version information
- [ ] Any manual overrides are documented with justification
- [ ] Review comments from quality check are addressed

---

## Sample Certification Statement

> *"I, [Name], a licensed Professional Engineer in [Jurisdiction], have reviewed
> the structural calculations for [Project Name] produced using structural-lib-is456
> version [X.Y.Z]. I have independently verified the input assumptions, checked
> critical calculations, and confirm that the design meets the requirements of
> IS 456:2000 [with amendments as applicable]. This certification is based on my
> professional judgment and the information available at the time of review."*
>
> Signature: ____________________
>
> PE License No: ____________________
>
> Date: ____________________

---

## Jurisdiction-Specific Notes

### India
- Registration with Council of Architecture or State Professional Bodies
- Follow NBC (National Building Code) requirements
- Check for state-specific amendments to IS 456

### International Use
- Verify IS 456 is acceptable for the jurisdiction
- Consider Eurocode, ACI, or other standards if required
- Document any code conversion or adaptation

---

## Version Tracking

When using this library in professional practice, document:

| Item | Value |
|------|-------|
| Library Version | e.g., 0.16.5 |
| Python Version | e.g., 3.11.0 |
| Date of Calculation | YYYY-MM-DD |
| Reviewer | Name, License # |

---

## Related Documents

- [LICENSE_ENGINEERING.md](../../LICENSE_ENGINEERING.md) - Engineering disclaimer
- [usage-guidelines.md](usage-guidelines.md) - Professional use guidance
- [verification-checklist.md](verification-checklist.md) - Detailed verification steps

---

**DISCLAIMER:** This template is provided as guidance only. It is the
responsibility of the licensed engineer to ensure compliance with all applicable
professional and regulatory requirements in their jurisdiction.
