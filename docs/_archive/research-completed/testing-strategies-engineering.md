# Testing Strategies for Engineering Software

**Document Version:** 1.0
**Last Updated:** 2026-01-07
**Status:** Research Complete
**Task:** TASK-230
**Author:** Research Team (Structural Engineer + Library Developer)

---

## Executive Summary

Engineering software requires specialized testing strategies beyond standard software testing. This document researches testing approaches for structural_lib focusing on:

1. **Visual regression testing** for DXF drawings and reports
2. **Property-based testing** for mathematical invariants
3. **Mutation testing** for test suite quality
4. **Reference verification** against hand calculations and external tools

**Key Finding:** Engineering libraries need multi-layered testing—unit tests verify individual calculations, property tests verify mathematical laws, visual regression catches drawing errors, and reference tests ensure code compliance accuracy.

**Recommendation:** Implement visual regression for DXF (4-6 hours), expand property-based tests for core calculations (8-10 hours), add mutation testing to CI (2-3 hours).

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Visual Regression Testing for DXF/Reports](#2-visual-regression-testing-for-dxfreports)
3. [Property-Based Testing for Engineering](#3-property-based-testing-for-engineering)
4. [Mutation Testing](#4-mutation-testing)
5. [Reference Verification Testing](#5-reference-verification-testing)
6. [Testing Strategy Matrix](#6-testing-strategy-matrix)
7. [Implementation Roadmap](#7-implementation-roadmap)
8. [Tools & Libraries](#8-tools--libraries)
9. [Cost-Benefit Analysis](#9-cost-benefit-analysis)
10. [Recommendations](#10-recommendations)

---

## 1. Problem Statement

### 1.1 Current Gap

**Identified Issues:**
- DXF export changes could break visually without detection
- Reports (PDF/text) may have layout/formatting regressions
- No systematic testing of mathematical invariants (e.g., equilibrium, compatibility)
- Test suite quality unknown (are we testing the right things?)
- Manual verification against hand calcs is ad-hoc

**Evidence from Current State:**
```python
# Current test: checks output exists but not visual correctness
def test_dxf_export():
    result = export_dxf(beam_data)
    assert result.success  # ✅ File created
    # ❌ Missing: Does drawing look correct?
    # ❌ Missing: Are dimensions placed properly?
    # ❌ Missing: Is rebar pattern correct?
```

### 1.2 Why Standard Testing Isn't Enough

**Challenge 1: Visual Outputs**
- Unit tests verify data structures, not visual appearance
- A DXF file can be "valid" but visually wrong (dimension arrows reversed, text overlapping)

**Challenge 2: Mathematical Invariants**
- Engineering calculations must satisfy physical laws (equilibrium, strain compatibility)
- Example: `Σ Moments = 0` must hold regardless of input values
- Standard tests check specific cases, not universal laws

**Challenge 3: Test Quality**
- How do we know our tests catch bugs?
- 100% coverage ≠ 100% confidence
- Mutation testing reveals weak tests

**Challenge 4: Code Compliance**
- IS 456 clauses are complex and interrelated
- Small code changes can break compliance in non-obvious ways
- Need systematic verification against code requirements

---

## 2. Visual Regression Testing for DXF/Reports

### 2.1 What is Visual Regression Testing?

**Definition:** Automated comparison of visual outputs (images, PDFs, drawings) against baseline "golden" references to detect unintended changes.

**Workflow:**
```
1. Generate DXF → Convert to PNG → Compare with baseline
2. Flag differences → Developer reviews → Accept or reject
3. If accepted → Update baseline → Commit
```

### 2.2 DXF Visual Regression Strategy

**Approach 1: Rasterization + Image Diff**

**Tools:** ezdxf + Pillow + pixelmatch

**Process:**
```python
def test_beam_dxf_visual():
    # 1. Generate DXF
    dxf_data = export_beam_dxf(beam_data)

    # 2. Rasterize DXF to PNG
    png_bytes = rasterize_dxf(dxf_data, resolution=300)

    # 3. Compare with baseline
    baseline_path = "tests/fixtures/dxf/beam_01_baseline.png"
    diff_pixels = compare_images(png_bytes, baseline_path)

    # 4. Assert similarity (allow 0.1% diff for anti-aliasing)
    assert diff_pixels < 0.001, f"Visual diff: {diff_pixels:.2%}"
```

**Tools Stack:**
- **ezdxf** (already used): DXF reading/writing
- **matplotlib** or **Pillow**: Rasterize DXF entities to PNG
- **pixelmatch** (Python port of JS library): Pixel-by-pixel comparison
- **pytest-mpl**: Matplotlib test images plugin

**Pros:**
- ✅ Catches visual layout bugs
- ✅ Fast (PNG comparison is quick)
- ✅ Easy to review diffs (visual)

**Cons:**
- ❌ Sensitive to anti-aliasing, font rendering
- ❌ Requires baseline image management
- ❌ DXF → PNG conversion may lose precision

**Alternative Approach 2: DXF Entity Comparison**

**Process:**
```python
def test_beam_dxf_entities():
    dxf_data = export_beam_dxf(beam_data)
    doc = ezdxf.read(dxf_data)

    # Check specific entities exist and positioned correctly
    assert count_lines(doc) == 12  # Expected beam outline lines
    assert count_texts(doc, layer="DIMENSIONS") == 8
    assert get_text_content(doc, "WIDTH") == "230 mm"
    assert dimension_position(doc, "SPAN") == (0, -100)  # Below beam
```

**Pros:**
- ✅ Precise (checks actual DXF data)
- ✅ No image conversion needed
- ✅ Faster than rasterization

**Cons:**
- ❌ More verbose tests
- ❌ Doesn't catch "looks wrong" issues (e.g., overlapping text)
- ❌ Requires DXF format knowledge

**Recommendation:** Use **hybrid approach**:
- Entity tests for structure/data correctness
- Visual regression for layout/appearance
- Start with entity tests (faster to implement), add visual later

### 2.3 Report Visual Regression Strategy

**Reports:** Text-based calculation sheets, PDF outputs

**Approach 1: Text Diff**

```python
def test_calculation_report_content():
    report = generate_report(beam_data)

    # Normalize whitespace/formatting
    normalized = normalize_report(report)
    baseline = load_baseline("beam_01_report.txt")

    # Compare text (allow minor formatting changes)
    assert normalized == baseline
```

**Pros:**
- ✅ Simple, fast
- ✅ Easy to review diffs (text)
- ✅ No image processing

**Cons:**
- ❌ Sensitive to whitespace changes
- ❌ Doesn't catch PDF layout issues

**Approach 2: PDF Visual Comparison**

**Tools:** pdf2image + pixelmatch

```python
def test_pdf_report_visual():
    pdf_bytes = generate_pdf_report(beam_data)

    # Convert PDF pages to images
    images = pdf2image.convert_from_bytes(pdf_bytes)

    # Compare each page
    for i, img in enumerate(images):
        baseline = f"tests/fixtures/reports/beam_01_page_{i}.png"
        diff = compare_images(img, baseline)
        assert diff < 0.005  # 0.5% tolerance
```

**Pros:**
- ✅ Catches layout issues
- ✅ Works for complex PDFs

**Cons:**
- ❌ Slower than text diff
- ❌ Font rendering differences across platforms

**Recommendation:**
- Text reports: Use text diff (faster, sufficient)
- PDF reports: Use visual comparison (necessary for layout)

### 2.4 Baseline Management Strategy

**Challenge:** How to manage baseline images/files?

**Solution: Git LFS + Test Fixtures**

```
tests/
  fixtures/
    dxf/
      baselines/
        beam_01.png
        beam_02.png
      current/           # Generated during tests
        beam_01.png
      diffs/             # Visual diffs if mismatch
        beam_01_diff.png
    reports/
      baselines/
        report_01.txt
```

**Baseline Update Workflow:**
```bash
# 1. Run tests with --update-baselines flag
pytest tests/visual/ --update-baselines

# 2. Review changes
git diff tests/fixtures/dxf/baselines/

# 3. If intentional, commit new baselines
git add tests/fixtures/dxf/baselines/
git commit -m "test: update DXF baselines after dimension style change"
```

**CI Strategy:**
- Store baselines in repo (Git LFS for PNGs)
- CI fails if diffs detected
- Developer reviews diff images in CI artifacts
- Updates baselines if intentional

### 2.5 Implementation Estimate

**Phase 1: DXF Entity Tests (2-3 hours)**
- Write helpers to extract DXF entities
- Add 5-10 entity structure tests
- Covers major DXF regressions

**Phase 2: DXF Visual Regression (4-6 hours)**
- Set up ezdxf → PNG rasterization
- Create baseline images (10-15 beams)
- Integrate pixelmatch comparison
- Add to CI

**Phase 3: Report Testing (2-3 hours)**
- Text diff for calculation sheets
- PDF visual comparison for PDF reports
- Create baseline reports

**Total:** 8-12 hours for comprehensive visual testing

---

## 3. Property-Based Testing for Engineering

### 3.1 What is Property-Based Testing?

**Definition:** Testing that universal properties (mathematical laws, physical constraints) hold for all inputs, not just specific examples.

**Standard Test (Example-Based):**
```python
def test_moment_capacity():
    # Test specific case
    Mu = calculate_moment_capacity(b=230, d=400, fck=25, fy=415, ast=1200)
    assert Mu == pytest.approx(180.5, rel=0.01)  # Expected from hand calc
```

**Property-Based Test:**
```python
from hypothesis import given, strategies as st

@given(
    b=st.floats(min_value=200, max_value=500),
    d=st.floats(min_value=300, max_value=800),
    fck=st.sampled_from([20, 25, 30, 35, 40]),
    ast=st.floats(min_value=500, max_value=5000)
)
def test_moment_capacity_properties(b, d, fck, ast):
    Mu = calculate_moment_capacity(b, d, fck, ast)

    # Property 1: Moment must be positive
    assert Mu > 0

    # Property 2: More steel → More capacity (monotonic)
    Mu_more_steel = calculate_moment_capacity(b, d, fck, ast * 1.1)
    assert Mu_more_steel >= Mu

    # Property 3: Deeper beam → More capacity
    Mu_deeper = calculate_moment_capacity(b, d * 1.1, fck, ast)
    assert Mu_deeper >= Mu
```

**Key Difference:** Property tests generate 100s of random inputs, checking universal truths instead of specific values.

### 3.2 Engineering Properties to Test

**Category 1: Physical Laws**

**Equilibrium:**
```python
@given(beam=beam_strategy())
def test_equilibrium(beam):
    result = design_beam(beam)

    # Σ Forces = 0 (vertical equilibrium)
    V_top = sum(result.support_reactions)
    V_loads = sum(result.applied_loads)
    assert abs(V_top - V_loads) < 1e-6  # Tolerance for floating point

    # Σ Moments = 0 (rotational equilibrium about any point)
    M_about_left = calculate_moment_about_point(result, x=0)
    assert abs(M_about_left) < 1e-6
```

**Strain Compatibility:**
```python
@given(section=section_strategy())
def test_strain_compatibility(section):
    result = analyze_section(section)

    # Strain distribution must be linear (plane sections remain plane)
    strain_top = result.strain_at(y=0)
    strain_bottom = result.strain_at(y=section.depth)
    strain_mid = result.strain_at(y=section.depth/2)

    # Linear interpolation check
    expected_mid = (strain_top + strain_bottom) / 2
    assert abs(strain_mid - expected_mid) < 1e-9
```

**Category 2: Monotonicity (More X → More Y)**

```python
@given(beam=beam_strategy())
def test_capacity_monotonic_in_depth(beam):
    """Deeper beam should have equal or greater capacity."""
    capacity_1 = calculate_capacity(beam)

    beam_deeper = beam.copy()
    beam_deeper.depth *= 1.1
    capacity_2 = calculate_capacity(beam_deeper)

    assert capacity_2 >= capacity_1
```

**Category 3: Symmetry**

```python
@given(beam=symmetric_beam_strategy())
def test_symmetric_loading_symmetric_response(beam):
    """Symmetric beam + symmetric load → symmetric reactions."""
    result = analyze_beam(beam)

    # Reactions at left and right should be equal
    assert abs(result.R_left - result.R_right) < 1e-6

    # Moment diagram should be symmetric about centerline
    x_mid = beam.span / 2
    M_left = result.moment_at(x_mid - 100)
    M_right = result.moment_at(x_mid + 100)
    assert abs(M_left - M_right) < 1e-6
```

**Category 4: Code Compliance Invariants**

```python
@given(beam=valid_beam_strategy())
def test_min_steel_always_provided(beam):
    """Designed beam must always meet minimum steel requirement."""
    result = design_beam(beam)

    if result.is_safe:
        ast_min = calculate_ast_min(beam.b, beam.d, beam.fck)
        assert result.ast_provided >= ast_min
```

**Category 5: Idempotence**

```python
@given(beam=beam_strategy())
def test_design_idempotent(beam):
    """Designing the same beam twice should give same result."""
    result_1 = design_beam(beam)
    result_2 = design_beam(beam)

    assert result_1.ast_required == result_2.ast_required
    assert result_1.is_safe == result_2.is_safe
```

### 3.3 Hypothesis Library Strategies

**Custom Strategies for Engineering Data:**

```python
from hypothesis import strategies as st

# Valid beam dimensions strategy
beam_dimensions = st.builds(
    dict,
    b=st.floats(min_value=200, max_value=600),
    d=st.floats(min_value=300, max_value=1200),
    fck=st.sampled_from([20, 25, 30, 35, 40]),
    fy=st.sampled_from([415, 500, 550]),
)

# Ensure d > cover + bar_dia (physical constraint)
@st.composite
def valid_section_strategy(draw):
    b = draw(st.floats(min_value=200, max_value=600))
    cover = draw(st.floats(min_value=25, max_value=75))
    bar_dia = draw(st.sampled_from([12, 16, 20, 25, 32]))
    d = draw(st.floats(min_value=cover + bar_dia + 100, max_value=1200))

    return {
        'b': b,
        'd': d,
        'cover': cover,
        'bar_dia': bar_dia,
    }
```

### 3.4 Property Testing Best Practices

**1. Start Simple:**
```python
# ✅ Good: Simple, fast property
@given(x=st.floats(min_value=0, max_value=1000))
def test_area_positive(x):
    assert calculate_area(x) >= 0
```

**2. Use Shrinking:**
When Hypothesis finds a failing case, it "shrinks" to the minimal failing example:
```
Original failure: beam(b=472.3, d=891.7, fck=33.2, ...)
Shrunk to: beam(b=200, d=300, fck=20, ...)  # Simpler to debug
```

**3. Use Decorators for Complex Constraints:**
```python
from hypothesis import assume

@given(beam=beam_strategy())
def test_property(beam):
    # Skip cases that don't meet preconditions
    assume(beam.span / beam.depth > 10)  # Only test slender beams
    assume(beam.load > 0)  # Only test loaded beams

    # Property check
    assert design_beam(beam).is_safe or beam.load > beam.capacity
```

**4. Profile Performance:**
Property tests run 100+ times → must be fast
```python
# ✅ Fast: Simple calculation
@given(x=st.floats(0, 1000))
def test_fast(x):
    assert calculate_simple(x) > 0

# ❌ Slow: Complex iterative calculation
@given(beam=beam_strategy())
@settings(max_examples=10)  # Reduce examples for slow tests
def test_slow(beam):
    assert optimize_beam(beam).cost < float('inf')
```

### 3.5 Implementation Estimate

**Phase 1: Infrastructure (1-2 hours)**
- Set up Hypothesis library
- Create custom strategies for beam/section/material

**Phase 2: Core Properties (4-6 hours)**
- Add 10-15 property tests for key calculations
- Cover equilibrium, monotonicity, symmetry

**Phase 3: Expand Coverage (8-10 hours)**
- Add properties for all core modules
- Document which properties apply to which functions

**Total:** 13-18 hours for comprehensive property testing

---

## 4. Mutation Testing

### 4.1 What is Mutation Testing?

**Definition:** Mutation testing evaluates test suite quality by introducing bugs (mutations) into code and checking if tests catch them.

**Concept:**
```python
# Original code
def calculate_capacity(b, d, fck):
    return 0.87 * fck * b * d

# Mutation 1: Change constant
def calculate_capacity(b, d, fck):
    return 0.85 * fck * b * d  # Changed 0.87 → 0.85

# Mutation 2: Change operator
def calculate_capacity(b, d, fck):
    return 0.87 * fck * b + d  # Changed * → +

# If tests PASS with mutation → Tests are weak!
# If tests FAIL with mutation → Tests caught the bug ✅
```

**Mutation Score:** % of mutations caught by tests
- **<50%:** Weak test suite
- **50-75%:** Decent coverage
- **75-90%:** Strong test suite
- **>90%:** Excellent (hard to achieve)

### 4.2 Mutation Testing Tools for Python

**Tool 1: mutmut** (Recommended)

```bash
pip install mutmut

# Run mutation testing on a module
mutmut run --paths-to-mutate=structural_lib/flexure.py

# View results
mutmut results

# Show specific mutations that survived
mutmut show 1
```

**Example Output:**
```
Mutations: 150 total, 120 killed, 25 survived, 5 skipped
Mutation score: 80.0%

Survived mutation 7:
  File: flexure.py, Line 45
  Original:  if ast < ast_min:
  Mutant:    if ast <= ast_min:

  → Add test for boundary case ast == ast_min
```

**Tool 2: cosmic-ray** (More configurable)

```bash
pip install cosmic_ray

# Initialize session
cosmic-ray init config.toml session.sqlite

# Run mutations
cosmic-ray exec session.sqlite

# View report
cr-report session.sqlite
```

### 4.3 Mutation Operators for Engineering Code

**Arithmetic Operators:**
```python
# Original
Mu = 0.87 * fy * ast * (d - 0.42 * xu)

# Mutations:
# - Change 0.87 → 0.85
# - Change 0.42 → 0.40
# - Change * → +
# - Change - → +
```

**Comparison Operators:**
```python
# Original
if ast < ast_min:
    ast = ast_min

# Mutations:
# - < → <=
# - < → >
# - ast_min → ast_min * 0.9
```

**Boolean Operators:**
```python
# Original
if is_safe and meets_deflection:
    return True

# Mutations:
# - and → or
# - True → False
```

**Constant Mutations:**
```python
# Original
ES = 200000  # N/mm²

# Mutations:
# - 200000 → 200001
# - 200000 → 199999
# - 200000 → 0
```

### 4.4 Mutation Testing Strategy

**Phase 1: Baseline (1 hour)**
- Run mutmut on 1-2 core modules
- Identify mutation score baseline
- Document weak areas

**Phase 2: Improve Tests (4-8 hours)**
- For each survived mutation:
  - Understand why it survived
  - Add test to kill it
  - Re-run mutation testing

**Phase 3: CI Integration (2-3 hours)**
- Add mutation testing to CI (run nightly)
- Set mutation score threshold (e.g., >75%)
- Fail PR if mutation score drops

**Example CI Config:**
```yaml
# .github/workflows/mutation-test.yml
name: Mutation Testing

on:
  schedule:
    - cron: '0 2 * * *'  # Nightly at 2 AM

jobs:
  mutation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install mutmut
      - run: mutmut run --paths-to-mutate=structural_lib/flexure.py
      - run: mutmut report --threshold=75
```

### 4.5 Mutation Testing Best Practices

**1. Start Small:**
- Don't mutate entire codebase at once
- Start with 1-2 critical modules (flexure.py, shear.py)
- Expand gradually

**2. Ignore Low-Value Mutations:**
```python
# Exclude logging, error messages from mutation
# mutmut.ini
[mutmut]
paths_to_exclude=structural_lib/logging.py
```

**3. Focus on Critical Code:**
- Prioritize calculations over formatting
- Prioritize safety checks over convenience features

**4. Use Mutation Score as Guidance:**
- Don't chase 100% (diminishing returns)
- 80% mutation score is excellent for engineering code

### 4.6 Implementation Estimate

**Total:** 7-12 hours for mutation testing setup + initial improvement cycle

---

## 5. Reference Verification Testing

### 5.1 What is Reference Verification?

**Definition:** Testing library outputs against trusted external references:
- Hand calculations (engineer-verified)
- Textbook examples (published, peer-reviewed)
- External tools (ETABS, SAFE, commercial software)
- Code examples (IS 456 handbook, SP:16)

**Purpose:** Validate not just that code is bug-free, but that it's **correct** per IS 456.

### 5.2 Reference Test Categories

**Category 1: Hand Calculations**

```python
def test_beam_01_hand_calc():
    """
    Reference: Hand calculation by PE, dated 2026-01-05
    File: tests/fixtures/hand_calcs/beam_01.pdf

    Simply supported beam:
    - Span: 5000 mm
    - Width: 230 mm
    - Depth: 450 mm
    - M25 concrete, Fe415 steel
    - Moment: 120 kN·m

    Expected:
    - Ast required: 843 mm²
    - Provide: 3-#20 (942 mm²)
    """
    result = design_beam(
        span_mm=5000,
        width_mm=230,
        depth_mm=450,
        moment_knm=120,
        fck_mpa=25,
        fy_mpa=415,
    )

    assert result.ast_required_mm2 == pytest.approx(843, rel=0.02)  # ±2%
    assert result.ast_provided_mm2 >= 843
    assert result.bar_config == "3-#20"
```

**Category 2: Textbook Examples**

```python
def test_pillai_menon_example_5_3():
    """
    Reference: "Reinforced Concrete Design" by Pillai & Menon
    3rd Edition, Example 5.3, Page 187

    Doubly reinforced beam design
    """
    result = design_beam_doubly_reinforced(
        # ... parameters from textbook
    )

    # Compare with textbook solution
    assert result.ast_mm2 == pytest.approx(2450, rel=0.05)  # Textbook: 2450 mm²
    assert result.asc_mm2 == pytest.approx(628, rel=0.05)   # Textbook: 628 mm²
```

**Category 3: IS 456 Worked Examples**

```python
def test_is456_handbook_example_1():
    """
    Reference: IS 456 Explanatory Handbook
    Example 1: Simply supported beam
    """
    # ... test code
```

**Category 4: External Tool Verification**

```python
def test_etabs_verification_beam_42():
    """
    Reference: ETABS model output
    File: tests/fixtures/etabs/model_01.EDB

    Beam 42 design from ETABS:
    - Ast required: 1256 mm²
    - V_max: 85.2 kN
    """
    result = design_beam(...)

    # Allow 5% difference (ETABS uses different code interpretation)
    assert result.ast_required_mm2 == pytest.approx(1256, rel=0.05)
```

### 5.3 Reference Test Organization

**Directory Structure:**
```
tests/
  reference/
    hand_calcs/
      test_hand_calcs.py
      fixtures/
        beam_01.pdf          # Hand calc sheet
        beam_01_data.json    # Inputs/outputs
    textbooks/
      test_pillai_menon.py
      test_raju.py
    is456_examples/
      test_is456_handbook.py
    external_tools/
      test_etabs_verification.py
      fixtures/
        etabs_model_01.EDB
```

### 5.4 Creating Hand Calculation References

**Process:**
1. Engineer performs hand calculation (manual or spreadsheet)
2. Document all steps, clauses used
3. Export to PDF + JSON
4. Write test referencing the calculation

**Example JSON:**
```json
{
  "reference": {
    "type": "hand_calculation",
    "author": "John Doe, PE",
    "date": "2026-01-05",
    "file": "beam_01_hand_calc.pdf"
  },
  "input": {
    "span_mm": 5000,
    "width_mm": 230,
    "depth_mm": 450,
    "moment_knm": 120,
    "fck_mpa": 25,
    "fy_mpa": 415
  },
  "expected_output": {
    "ast_required_mm2": 843,
    "xu_mm": 65.2,
    "mu_lim_knm": 245.3,
    "is_singly_reinforced": true
  },
  "tolerance": {
    "ast_required_mm2": 0.02,
    "xu_mm": 0.05,
    "mu_lim_knm": 0.02
  }
}
```

### 5.5 Implementation Estimate

**Phase 1: Hand Calculations (8-10 hours)**
- Create 10-15 hand calc references
- Cover common cases (simply supported, continuous, doubly reinforced)
- Write tests

**Phase 2: Textbook Examples (4-6 hours)**
- Identify 5-10 relevant textbook examples
- Write tests

**Phase 3: IS 456 Examples (2-3 hours)**
- Convert IS 456 handbook examples to tests

**Phase 4: External Tool Verification (4-6 hours)**
- Export ETABS/SAFE models
- Write verification tests

**Total:** 18-25 hours for comprehensive reference testing

---

## 6. Testing Strategy Matrix

| Test Type | Purpose | Coverage | Speed | Cost | Priority |
|-----------|---------|----------|-------|------|----------|
| **Unit Tests** | Verify individual functions | High (92%) | Fast (0.5s) | Low | 🔴 HIGH |
| **Property Tests** | Verify mathematical laws | Universal | Medium (5s) | Medium | 🔴 HIGH |
| **Visual Regression** | Verify DXF/report appearance | DXF/reports only | Slow (30s) | Medium | 🟡 MEDIUM |
| **Mutation Tests** | Verify test quality | N/A (meta) | Very Slow (30min) | High | 🟢 LOW |
| **Reference Tests** | Verify code correctness | Critical paths | Fast (1s) | High (manual) | 🔴 HIGH |
| **Integration Tests** | Verify end-to-end workflows | Workflows | Medium (10s) | Low | 🟡 MEDIUM |

**Recommended Mix:**
- **Every commit:** Unit tests (fast, high coverage)
- **Every PR:** Property tests (catches edge cases)
- **Weekly:** Visual regression (catches visual bugs)
- **Monthly:** Mutation testing (improves test quality)
- **On demand:** Reference verification (validates correctness)

---

## 7. Implementation Roadmap

### Phase 1: Foundation (Week 1) - 16 hours

**Deliverables:**
- [ ] Set up Hypothesis for property-based testing
- [ ] Write 10 property tests for core calculations
- [ ] Add 5 hand calculation reference tests
- [ ] Document testing strategy

**Success Criteria:**
- Property tests catch at least 2 new bugs
- Reference tests pass for all hand calcs

### Phase 2: Visual Testing (Week 2) - 12 hours

**Deliverables:**
- [ ] Set up DXF entity testing
- [ ] Create 15 baseline DXF fixtures
- [ ] Add report text comparison tests
- [ ] Integrate into CI

**Success Criteria:**
- Visual tests catch DXF layout bugs
- CI fails on visual regressions

### Phase 3: Quality (Week 3) - 10 hours

**Deliverables:**
- [ ] Run mutation testing on 3 core modules
- [ ] Improve tests to kill survived mutations
- [ ] Add mutation testing to nightly CI
- [ ] Document mutation score baseline

**Success Criteria:**
- Mutation score >75% for core modules
- CI tracks mutation score over time

### Phase 4: Expansion (Ongoing)

**Deliverables:**
- [ ] Add 10+ textbook example tests
- [ ] Add ETABS verification tests
- [ ] Expand property tests to all modules
- [ ] Improve visual regression coverage

---

## 8. Tools & Libraries

### 8.1 Property-Based Testing

**Hypothesis** (Python)
- **Install:** `pip install hypothesis`
- **Docs:** https://hypothesis.readthedocs.io/
- **Best for:** Universal properties, edge case generation
- **Cost:** Free, open source

**Example:**
```python
pip install hypothesis
```

### 8.2 Visual Regression Testing

**ezdxf** (DXF manipulation)
- **Install:** `pip install ezdxf`
- **Docs:** https://ezdxf.readthedocs.io/
- **Best for:** Reading/writing DXF files
- **Cost:** Free, open source

**Pillow** (Image processing)
- **Install:** `pip install Pillow`
- **Best for:** Rasterizing DXF to PNG
- **Cost:** Free, open source

**pixelmatch** (Image comparison)
- **Install:** `pip install pixelmatch`
- **Best for:** Pixel-by-pixel comparison
- **Cost:** Free, open source

**pytest-mpl** (Matplotlib testing)
- **Install:** `pip install pytest-mpl`
- **Best for:** Matplotlib figure comparison
- **Cost:** Free, open source

### 8.3 Mutation Testing

**mutmut** (Recommended)
- **Install:** `pip install mutmut`
- **Docs:** https://mutmut.readthedocs.io/
- **Best for:** Fast mutation testing
- **Cost:** Free, open source

**cosmic-ray** (Alternative)
- **Install:** `pip install cosmic_ray`
- **Best for:** Configurable mutation operators
- **Cost:** Free, open source

### 8.4 Reference Testing

**No special tools needed** - just pytest + fixtures

---

## 9. Cost-Benefit Analysis

### 9.1 Implementation Costs

| Test Type | Setup Cost | Maintenance Cost | Total (Year 1) |
|-----------|------------|------------------|----------------|
| Property Testing | 16 hours | 2 hours/month | 40 hours |
| Visual Regression | 12 hours | 1 hour/month | 24 hours |
| Mutation Testing | 10 hours | 2 hours/month | 34 hours |
| Reference Testing | 25 hours | 4 hours/month | 73 hours |
| **Total** | **63 hours** | **9 hours/month** | **171 hours** |

### 9.2 Benefits

**Quantifiable:**
- **Bug prevention:** Catch 2-3 bugs per month that would otherwise reach production (estimated 10 hours debugging per bug)
- **Refactoring confidence:** 50% faster refactoring due to comprehensive tests
- **Code quality:** 75%+ mutation score indicates strong test suite

**Qualitative:**
- **Professional confidence:** Reference tests validate code correctness
- **Regulatory compliance:** Visual regression ensures drawings meet standards
- **Maintenance:** Property tests document mathematical invariants

**ROI Estimate:**
- **Year 1:** 171 hours invested, ~300 hours saved in debugging/rework
- **Year 2+:** 108 hours/year maintenance, ~200 hours/year saved
- **Break-even:** 4-5 months

---

## 10. Recommendations

### 10.1 Immediate Actions (Next 2 Weeks)

**Priority 1: Property-Based Testing (16 hours)**
- Install Hypothesis
- Write 10-15 property tests for core calculations
- Document mathematical invariants
- **Why:** Catches edge cases that unit tests miss

**Priority 2: Reference Testing (8 hours)**
- Create 5 hand calculation references
- Write reference tests
- Add to CI
- **Why:** Validates code correctness per IS 456

**Priority 3: DXF Entity Testing (4 hours)**
- Write entity structure tests
- Add to CI
- **Why:** Prevents DXF regressions (faster than visual)

### 10.2 Medium-Term Actions (Next 1-2 Months)

**Priority 4: Visual Regression (12 hours)**
- Set up DXF → PNG rasterization
- Create baseline fixtures
- Integrate into CI
- **Why:** Catches visual layout bugs

**Priority 5: Mutation Testing (10 hours)**
- Run mutmut on core modules
- Improve tests to kill mutations
- Add to nightly CI
- **Why:** Ensures test suite quality

### 10.3 Long-Term Strategy

**Continuous Improvement:**
- Add 2-3 new property tests per month
- Add 1-2 reference tests per module
- Run mutation testing quarterly
- Update visual baselines as design evolves

**Success Metrics:**
- Property tests: 50+ tests covering all core modules
- Reference tests: 30+ tests covering common scenarios
- Visual regression: 20+ DXF baselines
- Mutation score: >75% for core modules

---

## Appendix A: Sample Property Tests

```python
from hypothesis import given, strategies as st
import pytest

# Strategy for valid beam dimensions
@st.composite
def valid_beam_strategy(draw):
    b = draw(st.floats(min_value=200, max_value=600))
    d = draw(st.floats(min_value=300, max_value=1200))
    fck = draw(st.sampled_from([20, 25, 30, 35, 40]))
    fy = draw(st.sampled_from([415, 500, 550]))
    return {'b': b, 'd': d, 'fck': fck, 'fy': fy}

# Property 1: Moment capacity increases with depth
@given(beam=valid_beam_strategy())
def test_capacity_increases_with_depth(beam):
    capacity_1 = calculate_moment_capacity(**beam)

    beam_deeper = beam.copy()
    beam_deeper['d'] *= 1.1
    capacity_2 = calculate_moment_capacity(**beam_deeper)

    assert capacity_2 >= capacity_1

# Property 2: Designed beam always meets minimum steel
@given(beam=valid_beam_strategy())
def test_minimum_steel_always_met(beam):
    result = design_beam(**beam, moment_knm=50)

    if result.is_safe:
        ast_min = 0.85 * beam['b'] * beam['d'] / beam['fy']
        assert result.ast_provided >= ast_min

# Property 3: Equilibrium always satisfied
@given(beam=valid_beam_strategy())
def test_equilibrium(beam):
    result = analyze_beam(**beam, load_kn_per_m=25, span_mm=5000)

    # Sum of reactions = Total load
    total_load = 25 * 5  # kN
    total_reactions = result.R_left + result.R_right

    assert abs(total_reactions - total_load) < 1e-6
```

---

## Appendix B: Visual Regression Example

```python
import pytest
from PIL import Image
import pixelmatch

def test_beam_dxf_visual_regression():
    """Test DXF visual output matches baseline."""
    # 1. Generate DXF
    beam_data = {
        'width_mm': 230,
        'depth_mm': 450,
        'span_mm': 5000,
    }
    dxf_bytes = export_beam_dxf(beam_data)

    # 2. Rasterize to PNG
    img = rasterize_dxf(dxf_bytes, resolution=300, width=1920, height=1080)

    # 3. Load baseline
    baseline = Image.open('tests/fixtures/dxf/baselines/beam_01.png')

    # 4. Compare
    diff_pixels = pixelmatch(
        img,
        baseline,
        threshold=0.1,  # 10% tolerance for anti-aliasing
    )

    diff_percent = diff_pixels / (1920 * 1080)

    # 5. Assert similarity (< 0.1% difference allowed)
    assert diff_percent < 0.001, f"Visual diff: {diff_percent:.4%}"

    # 6. Save diff image if failed (for debugging)
    if diff_percent >= 0.001:
        diff_img = create_diff_image(img, baseline)
        diff_img.save('tests/fixtures/dxf/diffs/beam_01_diff.png')
        pytest.fail("Visual regression detected. See diff image.")
```

---

## Appendix C: Mutation Testing Example

```bash
# Install mutmut
pip install mutmut

# Run mutation testing on flexure module
mutmut run --paths-to-mutate=structural_lib/flexure.py

# View results
mutmut results

# Output:
# Mutations: 87 total, 68 killed, 15 survived, 4 skipped
# Mutation score: 78.2%

# Show survived mutation
mutmut show 7

# Output:
# --- structural_lib/flexure.py ---
# Line 45:
# Original:  if ast < ast_min:
# Mutant:    if ast <= ast_min:
#
# Suggestion: Add test for boundary case ast == ast_min
```

---

## Document Control

**Version History:**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-07 | Initial research complete | Research Team |

**Approval:**

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Lead Researcher | TBD | TBD | |
| Technical Lead | TBD | TBD | |

**Next Steps:**

1. Review this document with development team
2. Prioritize recommendations for implementation
3. Create implementation tasks in backlog
4. Begin Phase 1 (Property-based testing) within 1 week

---

**End of Document**
