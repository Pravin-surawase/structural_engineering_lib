# Verification Pack

This repo’s unit tests validate correctness and edge cases, but they don’t always answer the question: **“did the numerical design outputs change?”**

The **Verification Pack** is a small set of **pinned regression targets** (deterministic inputs → expected numeric outputs) intended to:

- catch accidental numerical drift,
- validate core public APIs end-to-end,
- increase confidence before using the library on real projects.

## What’s included

Pinned cases live in:

- [Python/tests/regression/test_verification_pack.py](../../Python/tests/regression/test_verification_pack.py)

Coverage (current):

- Flexure: singly reinforced rectangular
- Flexure: doubly reinforced rectangular
- Flexure: flanged beam
- Shear design
- Serviceability: deflection (span/depth simplified method)
- Serviceability: crack width
- Compliance: orchestration across multiple load cases

## How to run

From repo root:

- `cd Python && pytest -q tests/regression/test_verification_pack.py`

This is also exercised as part of the full test suite (`pytest`) and therefore by the pre-release gate script.

## Updating expectations

If you intentionally change calculation logic (bug fix / standards interpretation):

1. Update the expected values in [Python/tests/regression/test_verification_pack.py](../../Python/tests/regression/test_verification_pack.py).
2. Add a note to `CHANGELOG.md` describing the behavior change.
3. Consider updating/adding a worked example in docs (or Excel parity check) to justify the new baseline.

## Notes

- These cases are **not** a replacement for engineering review/approval.
- All inputs/outputs are in explicit units (mm, N/mm², kN, kN·m) to reduce ambiguity.
