# Learning Plan (Beginner Friendly)

Audience: Structural engineer with 2 years experience, basic to medium Python/VBA.
Goal: Understand the engineering concepts, the code, and how to maintain the repo.

This plan is split into phases. Each phase has a goal, what to read, and a
checkpoint. Move at your own pace.

## Phase 0: Setup and First Success (0.5 to 1 day)

Goal: Run the library end to end once.

Read:
- docs/getting-started/beginners-guide.md
- docs/getting-started/python-quickstart.md

Do:
- Run the one-liner flexure example
- Run the CLI pipeline on a tiny CSV

Checkpoint:
- You can generate results.json, schedule.csv, and drawings.dxf

## Phase 1: Concepts Used in This Repo (1 week)

Goal: Understand the IS 456 ideas used in code.

Read:
- docs/reference/is456-formulas.md
- docs/reference/known-pitfalls.md

Focus topics:
- Mu_lim, xu/xu_max
- tau_v, tau_c, shear checks
- Ld, lap length, bar spacing
- Serviceability Level A and Level B

Checkpoint:
- You can explain each output field in results.json

## Phase 2: How to Use the Library (1 week)

Goal: Become a power user (CLI + job runner).

Read:
- docs/cookbook/cli-reference.md
- docs/getting-started/colab-workflow.md

Do:
- Run a 50 or 500 beam synthetic batch
- Try --deflection and --crack-width-params

Checkpoint:
- You can run a job.json and explain the output folder layout

## Phase 3: Code Walkthrough (1 to 2 weeks)

Goal: Learn the code structure and flow.

Read:
- docs/architecture/project-overview.md
- docs/architecture/deep-project-map.md
- docs/reference/api.md

Trace these entrypoints:
- Python/structural_lib/__main__.py (CLI)
- Python/structural_lib/api.py (public API)
- Python/structural_lib/beam_pipeline.py (application flow)

Checkpoint:
- You can trace CSV input to design output without guessing

## Phase 4: Tests and Validation (1 week)

Goal: Learn how quality is enforced.

Read:
- docs/contributing/testing-strategy.md
- Python/tests/test_critical_is456.py
- Python/tests/test_property_invariants.py

Do:
- Run one focused test file
- Read at least one parity vector in Python/tests/data/parity_test_vectors.json

Checkpoint:
- You can add a small unit test for a missing edge case

## Phase 5: VBA Parity (optional, 1 week)

Goal: Keep Excel and Python consistent.

Read:
- docs/contributing/vba-testing-guide.md

Do:
- Open VBA/Tests/Test_Parity.bas and compare a vector to Python

Checkpoint:
- You can update a VBA test and explain why the value changed

## Phase 6: Release and Maintenance (ongoing)

Goal: Ship stable updates without drift.

Read:
- docs/planning/pre-release-checklist.md
- docs/planning/v0.20-stabilization-checklist.md

Do:
- Run ./scripts/ci_local.sh
- Run scripts/check_doc_versions.py

Checkpoint:
- You can release without manual version edits

---

## Suggested weekly schedule (6 weeks)

Week 1: Phase 0 + Phase 1
Week 2: Phase 2
Week 3: Phase 3
Week 4: Phase 4
Week 5: Phase 5 (optional)
Week 6: Phase 6

If you only have 30 minutes per day, stretch the schedule to 10 to 12 weeks.
