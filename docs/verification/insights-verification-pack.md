# Insights Module Verification Pack

**Version: 0.14.0
**Purpose:** Automated regression tests for insights module accuracy

This pack provides benchmark test cases for the insights module to ensure accuracy and prevent regressions. Tests are automatically run in CI on every PR.

---

## Quick Validation

Run all insights benchmark tests:

```bash
cd Python
pytest tests/test_insights_verification_pack.py -v
```

**Expected output:** 10 passed (3 precheck + 4 sensitivity + 3 constructability)

---

## Benchmark Case Summary

| Case ID | Category | IS 456 Ref | Description |
|---------|----------|------------|-------------|
| precheck_normal_beam | Precheck | Table 23 | Normal dimensions, LOW risk |
| precheck_shallow_beam | Precheck | Table 23 | Deflection risk, HIGH risk |
| precheck_narrow_beam | Precheck | IS 456 Cl 23.1 | Width warning, MEDIUM risk |
| sensitivity_light_loading | Sensitivity | IS 456 design equations | Low utilization (~0.4), excellent robustness |
| sensitivity_moderate_loading | Sensitivity | SP:16 Example 1 | Moderate utilization (~0.6), excellent robustness |
| sensitivity_heavy_loading | Sensitivity | IS 456 design equations | High utilization (~0.9), poor robustness |
| sensitivity_doubly_reinforced | Sensitivity | SP:16 Example 2 | Doubly reinforced beam case |
| constructability_excellent | Constructability | BDAS framework | Light reinforcement, standard sizes |
| constructability_acceptable | Constructability | BDAS framework | Moderate reinforcement (now scores excellent) |
| constructability_poor | Constructability | BDAS framework | Congested, non-standard sizes |

---

## Test Data Location

Full benchmark case definitions with expected values and tolerances:
- **JSON data:** `Python/tests/data/insights_benchmark_cases.json`
- **Test module:** `Python/tests/test_insights_verification_pack.py`

Each case includes:
- Input parameters
- Expected output ranges (not exact values, to handle variations)
- IS 456/SP:16 references for traceability
- Rationale explaining physical expectations

---

## CI Integration

These tests run automatically on every pull request as part of the pytest suite. This prevents regressions in:
- **Precheck heuristics** - Deflection risk detection, width adequacy warnings
- **Sensitivity analysis** - Parameter impact classification, robustness scoring
- **Constructability scoring** - Construction ease factors (spacing, layers, bar sizes)

See `.github/workflows/python-tests.yml` for CI configuration.

---

## Verification Philosophy

This pack uses **range-based validation** rather than exact value matching:
- Allows for minor implementation changes without breaking tests
- Focuses on physical correctness (e.g., depth more critical than width)
- Tests behavior boundaries (LOW vs MEDIUM vs HIGH risk)
- Validates IS 456 compliance for key checks

**Example:** Instead of expecting `robustness_score == 0.723`, we test `0.7 <= score <= 0.8` and `rating == "good"`.

---

## For Contributors

When modifying insights algorithms:
1. Run `pytest tests/test_insights_verification_pack.py -v` locally
2. If tests fail, verify changes are intentional
3. Update JSON expected values if behavior intentionally changed
4. Document rationale for changes in commit message
5. CI will automatically run tests on PR

---

**Last updated:** 2025-12-31
**Test count:** 10 benchmark cases
**Coverage:** All 3 insights functions (precheck, sensitivity, constructability)
