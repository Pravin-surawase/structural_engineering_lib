# Concepts Map (Concept -> Code -> Tests -> Docs)

This map links engineering concepts to the exact files in the repo.
Use it when you want to understand where something is implemented.

## Entry points (start here)
- CLI: Python/structural_lib/__main__.py
- Public API: Python/structural_lib/api.py
- Application flow: Python/structural_lib/beam_pipeline.py

## Core concepts

| Concept | Code | Tests | Docs |
|--------|------|-------|------|
| Units + schema | Python/structural_lib/beam_pipeline.py | Python/tests/test_beam_pipeline.py | docs/reference/api.md |
| Flexure (Mu_lim, xu, Ast) | Python/structural_lib/flexure.py | Python/tests/test_flexure.py, Python/tests/test_critical_is456.py | docs/reference/api.md, docs/reference/is456-formulas.md |
| Shear (tau_v, tau_c, spacing) | Python/structural_lib/shear.py | Python/tests/test_shear.py | docs/reference/api.md |
| Serviceability (Level A) | Python/structural_lib/serviceability.py | Python/tests/test_serviceability.py | docs/reference/api.md |
| Serviceability (Level B) | Python/structural_lib/serviceability.py | Python/tests/test_serviceability.py | docs/reference/api.md |
| Detailing (Ld, lap, spacing) | Python/structural_lib/detailing.py | Python/tests/test_detailing.py | docs/reference/api.md |
| Compliance report | Python/structural_lib/compliance.py | Python/tests/test_compliance.py | docs/reference/api.md |
| BBS output | Python/structural_lib/bbs.py | Python/tests/test_bbs.py | docs/cookbook/cli-reference.md |
| DXF drawings | Python/structural_lib/dxf_export.py | Python/tests/test_dxf_export_edges.py | docs/cookbook/cli-reference.md |
| Job runner | Python/structural_lib/job_runner.py | Python/tests/test_job_runner_is456.py | docs/cookbook/cli-reference.md |

## Data files and vectors
- Parity vectors: Python/tests/data/parity_test_vectors.json
- Validation examples: docs/verification/examples.md

## VBA parity
- VBA tests: VBA/Tests/Test_Parity.bas
- VBA core modules: VBA/Modules/*.bas
- VBA tests runner: VBA/Tests/Test_RunAll.bas

## Automation and release
- Local CI parity: scripts/ci_local.sh
- Doc drift check: scripts/check_doc_versions.py
- Release helper: scripts/release.py
