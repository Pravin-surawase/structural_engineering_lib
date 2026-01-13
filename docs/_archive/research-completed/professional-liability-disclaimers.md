# Professional Liability & Disclaimers

**Document Version:** 1.0
**Last Updated:** 2026-01-07
**Status:** Complete
**Task:** TASK-261
**Author:** Research Team (Structural Engineer + Library Developer)

---

## Executive Summary

**Problem:** Engineering software that produces structural designs carries significant professional liability risk. Without proper disclaimers and guidance, both library authors and users face legal exposure.

**Scope:** Research professional liability considerations for structural engineering software:
1. Legal disclaimers & warranties
2. Professional responsibility guidelines
3. License considerations (MIT implications)
4. Documentation requirements
5. Risk mitigation strategies

**Key Finding:** Engineering software requires explicit disclaimers about professional responsibility. The library is a **tool**, not a replacement for engineering judgment. Users (licensed engineers) remain legally responsible for designs.

**Critical Recommendation:** Add comprehensive disclaimers in:
- LICENSE file
- README.md
- Module docstrings
- Function docstrings (critical functions)
- Generated reports

---

## Table of Contents

1. [Legal Framework & Liability](#1-legal-framework--liability)
2. [Disclaimer Requirements](#2-disclaimer-requirements)
3. [Professional Responsibility](#3-professional-responsibility)
4. [License Implications](#4-license-implications)
5. [Documentation Standards](#5-documentation-standards)
6. [Risk Mitigation](#6-risk-mitigation)
7. [Implementation Guide](#7-implementation-guide)

---

## 1. Legal Framework & Liability

### 1.1 Engineering Software Liability Categories

**Category 1: Design Responsibility**
- **Who:** Licensed professional engineer using the software
- **Liability:** Engineer is responsible for design adequacy and safety
- **Not library author:** Software is a tool, like a calculator

**Category 2: Software Defects**
- **Who:** Library authors/maintainers
- **Liability:** If software has bugs causing incorrect calculations
- **Mitigated by:** MIT License disclaimer, testing, documentation

**Category 3: Misuse**
- **Who:** User who misapplies software
- **Liability:** User responsible for appropriate use
- **Example:** Using residential beam design for bridge design

### 1.2 Professional Engineering Standards

**Key Principle:** Software does not practice engineering—engineers do.

**From NSPE Code of Ethics:**
> "Engineers shall not affix their signatures to any plans or documents dealing with subject matter in which they lack competence, nor to any plan or document not prepared under their direction and control."

**Implication:** Engineer using structural_lib must:
- Verify calculations independently
- Review code assumptions
- Check results for reasonableness
- Seal/sign designs personally
- Not delegate professional judgment to software

---

## 2. Disclaimer Requirements

### 2.1 Essential Disclaimers

**Disclaimer 1: No Warranty of Fitness**

Required language:
```
THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE, OR DESIGN ADEQUACY. THE SOFTWARE IS A
COMPUTATIONAL TOOL ONLY AND DOES NOT REPLACE PROFESSIONAL ENGINEERING JUDGMENT.
```

**Disclaimer 2: Professional Responsibility**

Required language:
```
PROFESSIONAL RESPONSIBILITY: This library is a calculation tool for use by
licensed professional engineers. The engineer using this software remains
solely responsible for:
- Verifying all calculations
- Ensuring design adequacy and safety
- Compliance with applicable codes and standards
- Professional judgment and decision-making
- Sealing and signing final designs

The software authors assume no liability for designs produced using this library.
```

**Disclaimer 3: Code Compliance**

Required language:
```
CODE COMPLIANCE: This library implements IS 456:2000 (Plain and Reinforced
Concrete - Code of Practice) as interpreted by the authors. Users must:
- Verify code interpretation is appropriate for their jurisdiction
- Check for code amendments or local modifications
- Consult original code documents for authoritative guidance
- Apply engineering judgment for cases not explicitly covered
```

### 2.2 Disclaimer Placement

**Location 1: LICENSE File**

Add engineering-specific disclaimer to MIT License:

```
MIT License

Copyright (c) 2024-2026 [Author Name]

[Standard MIT License text...]

ENGINEERING SOFTWARE DISCLAIMER:
This software is a computational tool for structural engineering calculations.
It does not replace professional engineering judgment, and the authors assume
no liability for designs produced using this library. Users (licensed
professional engineers) are solely responsible for verifying calculations,
ensuring design adequacy, and compliance with applicable codes and standards.
```

**Location 2: README.md**

Prominent disclaimer section:

```markdown
## ⚠️ Professional Use Disclaimer

**THIS SOFTWARE IS FOR USE BY LICENSED PROFESSIONAL ENGINEERS ONLY**

- This library is a **calculation tool**, not a substitute for engineering judgment
- **You** (the engineer) are responsible for all designs produced
- Verify all calculations independently
- Check assumptions and applicability to your project
- Comply with local codes, amendments, and jurisdiction requirements
- Seal and sign designs per professional licensing requirements

**By using this software, you acknowledge:**
1. You are a licensed professional engineer (or under supervision of one)
2. You will independently verify all calculations
3. You accept full professional responsibility for designs
4. Authors/maintainers have no liability for your designs
```

**Location 3: Module Docstring**

Top of main modules:

```python
"""
Structural design calculations per IS 456:2000.

DISCLAIMER: This is a calculation tool for licensed professional engineers.
Users are solely responsible for verifying results, ensuring design adequacy,
and professional judgment. See LICENSE for full disclaimer.
"""
```

**Location 4: Critical Function Docstrings**

Functions that directly produce design outputs:

```python
def design_beam(...) -> BeamDesignResult:
    """
    Design reinforced concrete beam per IS 456:2000.

    PROFESSIONAL RESPONSIBILITY: Engineer using this function is responsible
    for verifying results, checking assumptions, and ensuring design adequacy.
    This function is a computational tool only.

    ...
    """
```

**Location 5: Generated Reports**

If library generates calculation reports:

```
STRUCTURAL DESIGN CALCULATIONS
Generated by structural_lib v0.15.0

DISCLAIMER: These calculations are for preliminary design and analysis only.
A licensed professional engineer must review, verify, and seal these calculations
before use in construction. The software authors assume no liability for designs
based on these calculations.

Engineer's Review:
Name: ________________     License: ________________
Signature: ___________     Date: _________________
```

---

## 3. Professional Responsibility

### 3.1 User Responsibilities

**Engineers using this library MUST:**

1. **Verify Calculations**
   - Spot-check key results manually
   - Compare with alternative methods
   - Check limiting cases (span→0, load→0, etc.)

2. **Review Assumptions**
   - Understand code assumptions
   - Verify applicability to project
   - Check for edge cases not covered

3. **Independent Judgment**
   - Don't blindly accept results
   - Apply engineering experience
   - Question unreasonable outputs

4. **Code Compliance**
   - Verify local code applicability
   - Check for amendments
   - Consult authoritative sources

5. **Documentation**
   - Document library version used
   - Record verification steps
   - Maintain calculation records

### 3.2 Library Author Responsibilities

**Authors/maintainers MUST:**

1. **Accurate Implementation**
   - Implement codes correctly
   - Document assumptions clearly
   - Test thoroughly

2. **Clear Documentation**
   - Explain methods and limitations
   - Provide examples
   - Document known issues

3. **Transparent Development**
   - Open source (verifiable)
   - Version control
   - Changelog

4. **Responsive Maintenance**
   - Fix bugs promptly
   - Address security issues
   - Update for code changes

5. **Appropriate Disclaimers**
   - Clear professional responsibility
   - No implied fitness claims
   - Explicit limitations

---

## 4. License Implications

### 4.1 MIT License for Engineering Software

**MIT License Characteristics:**
- ✅ Permissive (allows commercial use)
- ✅ Includes warranty disclaimer
- ✅ Limits liability
- ❌ Generic (not engineering-specific)

**Recommendation:** Keep MIT, add engineering-specific addendum

**Enhanced MIT License:**

```
MIT License

Copyright (c) 2024-2026 [Authors]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

ENGINEERING SOFTWARE ADDENDUM:

This software is a computational tool for structural engineering design per
IS 456:2000. It is intended for use by licensed professional engineers only.

PROFESSIONAL RESPONSIBILITY: The engineer using this software is solely
responsible for:
- Verifying all calculations produced by this software
- Ensuring design adequacy and structural safety
- Compliance with applicable building codes and standards
- Professional judgment and engineering decisions
- Reviewing, sealing, and signing all designs

NO IMPLIED FITNESS FOR PURPOSE: This software does not warrant fitness for
any particular design or project. Results must be independently verified.

NO LIABILITY: Authors and contributors have no liability for designs,
structural failures, or damages resulting from use of this software. Use
at your own professional risk and responsibility.

CODE INTERPRETATION: This software implements IS 456:2000 as interpreted
by the authors. Users must verify code interpretation is appropriate for
their jurisdiction and consult authoritative code documents.

By using this software, you acknowledge and accept these terms.
```

### 4.2 Alternative Licenses Considered

**GPL (GNU General Public License):**
- ❌ Too restrictive (forces derivatives to be GPL)
- ❌ Not commonly used for libraries
- ✅ Strong copyleft protection

**Apache 2.0:**
- ✅ Similar to MIT but with patent clause
- ✅ More explicit contributor terms
- ❌ More complex than needed

**Custom License:**
- ❌ Reduces adoption (legal review required)
- ❌ May not be OSI approved
- ✅ Could have specific engineering terms

**Decision:** Keep MIT + Engineering Addendum (balance of openness & protection)

---

## 5. Documentation Standards

### 5.1 Calculation Documentation

**For every calculation function, document:**

1. **Code Reference**
   ```python
   """
   Calculate beam capacity per IS 456:2000 Cl. 38.1.

   Code Reference:
   - IS 456:2000 Clause 38.1 (Flexural Strength)
   - IS 456:2000 Clause 38.1.1 (Singly Reinforced)
   - SP:16 Example 4.2 (Verification)
   """
   ```

2. **Assumptions**
   ```python
   """
   Assumptions:
   - Plane sections remain plane (Cl. 38.1)
   - Concrete stress-strain per Fig. 21
   - Steel stress-strain per Fig. 22.1
   - Fe415 steel (fy = 415 N/mm²)
   - Rectangular stress block (Cl. 38.1)
   """
   ```

3. **Limitations**
   ```python
   """
   Limitations:
   - Singly reinforced sections only (no compression steel)
   - Rectangular cross-sections only (no flanged beams)
   - Normal weight concrete (unit weight = 25 kN/m³)
   - Does not include torsion effects
   """
   ```

4. **Verification**
   ```python
   """
   Verification:
   - Compared with SP:16 Example 4.2 (±0.1% agreement)
   - Validated against hand calculations
   - Cross-checked with commercial software
   """
   ```

### 5.2 User Documentation

**User guide must include:**

1. **Scope & Applicability**
   - What designs are covered
   - What is NOT covered
   - When to use vs not use

2. **Verification Examples**
   - Worked examples with hand calcs
   - Comparison with code examples
   - Edge case demonstrations

3. **Professional Use Guidance**
   - How to verify results
   - What to check manually
   - When to consult specialists

4. **Troubleshooting**
   - Common errors
   - Unusual results interpretation
   - When results seem wrong

---

## 6. Risk Mitigation

### 6.1 Risk Mitigation Strategies

**Strategy 1: Comprehensive Testing**
- Unit tests (92% coverage)
- Reference tests (hand calcs, textbooks)
- Property tests (mathematical invariants)
- → Reduces software defect liability

**Strategy 2: Clear Documentation**
- Code references in every function
- Assumptions explicitly stated
- Limitations clearly documented
- → Reduces misuse liability

**Strategy 3: Conservative Defaults**
- Default to safer values (higher safety factors)
- Warn for unusual inputs
- Require explicit overrides for edge cases
- → Reduces design inadequacy risk

**Strategy 4: Verification Encouragement**
- Provide comparison examples
- Document verification process
- Include self-check features
- → Encourages professional due diligence

**Strategy 5: Version Tracking**
- Clear version in all outputs
- Changelog with breaking changes
- Deprecation warnings
- → Ensures reproducibility

### 6.2 Risk Matrix

| Risk | Likelihood | Impact | Mitigation | Residual Risk |
|------|-----------|--------|------------|---------------|
| Software bug causes incorrect calc | Medium | High | Testing, peer review | Low |
| User misapplies software | Medium | High | Documentation, disclaimers | Medium |
| Code interpretation differs from jurisdiction | Low | Medium | Explicit code reference | Low |
| User doesn't verify results | Medium | High | Disclaimers, encouragement | Medium |
| Structural failure blamed on software | Low | Critical | Disclaimers, MIT license | Low |

---

## 7. Implementation Guide

### 7.1 Immediate Actions (Before v1.0)

**Action 1: Update LICENSE** (15 minutes)
- Add Engineering Software Addendum
- Review with legal counsel if available
- Commit to repository

**Action 2: Update README** (30 minutes)
- Add prominent disclaimer section
- Add "Who Should Use" section
- Add "Professional Responsibility" section

**Action 3: Add Module Disclaimers** (1 hour)
- Add to all core modules
- Consistent wording
- Test imports still work

**Action 4: Critical Function Disclaimers** (2 hours)
- Identify critical design functions
- Add professional responsibility notes
- Update docstring tests

**Total:** ~4 hours before v1.0 release

### 7.2 Documentation Templates

**Template 1: Module Header**

```python
# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 [Authors]
"""
[Module name and description]

PROFESSIONAL USE DISCLAIMER:
This module is a computational tool for licensed professional engineers.
Engineers using these functions are solely responsible for verifying
results, ensuring design adequacy, and professional judgment. See
LICENSE for full terms.

Code Basis: IS 456:2000 [specific clauses]
"""
```

**Template 2: Design Function**

```python
def design_beam(...) -> BeamDesignResult:
    """
    [Function description]

    RESPONSIBILITY: Engineer using this function must verify results and
    ensure design adequacy per professional licensing requirements.

    Code Reference: IS 456:2000 Cl. X.Y.Z

    Assumptions:
    - [List key assumptions]

    Limitations:
    - [List what's NOT covered]

    Args:
        [Parameters]

    Returns:
        [Return value]

    Raises:
        [Exceptions]

    Example:
        [Usage example with verification note]

    See Also:
        [Related functions]
    """
```

### 7.3 Report Template

If generating calculation sheets:

```
================================================================================
REINFORCED CONCRETE BEAM DESIGN CALCULATIONS
Generated by structural_lib v0.15.0
Date: 2026-01-07
================================================================================

DISCLAIMER: PRELIMINARY DESIGN ONLY

These calculations are produced by computational software and are for
preliminary design purposes only. A licensed professional engineer MUST:
- Review and verify all calculations
- Check assumptions and applicability
- Apply professional judgment
- Ensure compliance with local codes
- Seal and sign before use in construction

The software authors assume NO LIABILITY for designs based on these
calculations.

================================================================================

DESIGN INPUTS
[... calculation details ...]

DESIGN OUTPUTS
[... results ...]

================================================================================

PROFESSIONAL ENGINEER'S CERTIFICATION

I, the undersigned licensed professional engineer, have reviewed these
calculations, verified their accuracy, and take full professional
responsibility for this design.

Engineer: _____________________  License No.: ______________
Signature: ___________________  Date: _____________________

================================================================================
```

---

## Document Control

**Version History:**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-07 | Initial research complete | Research Team |

**Legal Review:** Recommended before v1.0 release (if resources available)

**Next Steps:**

1. Review with legal counsel (if available)
2. Implement immediate actions before v1.0
3. Update all documentation
4. Add disclaimers to generated outputs
5. Review annually or when codes update

---

**End of Document**
**Implementation Time:** ~4 hours (critical for v1.0)
**Legal Risk Reduction:** HIGH
**Priority:** CRITICAL (must complete before public v1.0)
