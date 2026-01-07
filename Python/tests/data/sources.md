# Test Vector Sources

This folder holds pinned regression vectors used by pytest. These files are
intentionally stable so numerical regressions are caught early.

## Files

- `golden_vectors_is456.json`
  - Used by: `Python/tests/test_golden_vectors_is456.py`
  - Purpose: Lock down key outputs for `api.design_beam_is456` and ensure
    deterministic results for representative IS 456 inputs.
  - Origin: Curated from a known-good release and reviewed against expected
    engineering behavior. Updated only when formulas or accepted outputs change.

- `parity_test_vectors.json`
  - Used by: `Python/tests/test_parity_vectors.py`
  - Purpose: Cross-check Python vs VBA outputs for core flexure, shear,
    detailing, and serviceability calculations.
  - Origin: Captured from the VBA implementation and verified in Python with
    tolerance rules stored in the same file.

## Update workflow (when outputs legitimately change)

1. Run the relevant tests to confirm the change scope.
2. Recompute outputs using the same inputs and capture the new expected values.
3. Cross-check against the VBA implementation or the verification pack.
4. Update the JSON metadata (e.g., created date) and document the change in
   `docs/releases.md` and `docs/SESSION_log.md`.
