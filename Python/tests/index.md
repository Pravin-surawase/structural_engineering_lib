# Tests

This document describes the test taxonomy and structure for the structural_engineering_lib test suite.

**Type:** Python Package
**Last Updated:** 2026-08-23
**Files:** 76

## Documentation Files

| File | Title | Description | Lines |
|------|-------|-------------|-------|
| [README.md](README.md) | Test Suite Organization | This document describes the test taxonomy and structure for  | 394 |

## Python Files

| File | Description | Classes | Functions | Lines |
|------|-------------|---------|-----------|-------|
| [__init__.py](__init__.py) |  | 0 | 0 | 1 |
| [conftest.py](conftest.py) | Pytest configuration and Hypothesis profiles for the test su | 0 | 6 | 131 |
| [test_agent_governance_automation.py](test_agent_governance_automation.py) | Regression tests for agent-governance automation controls. | 0 | 20 | 640 |
| [test_api_classification.py](test_api_classification.py) | Executable truth checks for the Alpha API classification reg | 0 | 4 | 105 |
| [test_api_manifest_tools.py](test_api_manifest_tools.py) | Regression tests for the single canonical public API manifes | 0 | 5 | 134 |
| [test_api_results.py](test_api_results.py) | Tests for API result dataclasses. | 3 | 0 | 394 |
| [test_api_stability.py](test_api_stability.py) | EA-9: Wheel API stability tests. | 6 | 0 | 233 |
| [test_api_surface_snapshot.py](test_api_surface_snapshot.py) | Snapshot regression tests — assert minimum API surface count | 5 | 0 | 122 |
| [test_assertion_helpers.py](test_assertion_helpers.py) | Tests for the IS 456 test assertion helpers. | 3 | 0 | 82 |
| [test_audit.py](test_audit.py) | Tests for audit module (TASK-278). | 6 | 0 | 471 |
| [test_audit_readiness_truth.py](test_audit_readiness_truth.py) | Readiness must aggregate semantic truth instead of reporting | 0 | 16 | 289 |
| [test_boq.py](test_boq.py) | Tests for the BOQ (Bill of Quantities) aggregation module. | 1 | 0 | 252 |
| [test_branch_disposition.py](test_branch_disposition.py) | Outcome tests for the inspection-only branch disposition cla | 0 | 12 | 437 |
| [test_bump_version_semantics.py](test_bump_version_semantics.py) | Regression coverage for candidate-version documentation sema | 0 | 1 | 66 |
| [test_calculation_report.py](test_calculation_report.py) | Tests for the calculation_report module (TASK-277). | 9 | 4 | 745 |
| [test_ci_workflow_contract.py](test_ci_workflow_contract.py) | Regression tests for fail-closed PR workflow routing. | 0 | 8 | 255 |
| [test_clause_traceability.py](test_clause_traceability.py) | Tests for IS 456 Traceability Module | 10 | 2 | 489 |
| [test_column_axial.py](test_column_axial.py) | Tests for column axial module — effective_length() per IS 45 | 6 | 0 | 273 |
| [test_column_biaxial.py](test_column_biaxial.py) | Tests for IS 456 Cl 39.6 biaxial bending check — TASK-635. | 8 | 0 | 958 |
| [test_column_helical.py](test_column_helical.py) | Tests for IS 456 Cl 39.4 helical reinforcement check. | 7 | 0 | 356 |
| [test_column_long.py](test_column_long.py) | Tests for IS 456 Cl 39.7 long (slender) column design. | 15 | 0 | 662 |
| [test_column_return_types.py](test_column_return_types.py) | Tests for UX-02: Column API return type unification. | 7 | 6 | 349 |
| [test_control_plane.py](test_control_plane.py) | Contract tests for the canonical repository control plane. | 0 | 8 | 124 |
| [test_core.py](test_core.py) | Tests for structural_lib.core module. | 6 | 0 | 176 |
| [test_core_types.py](test_core_types.py) | Tests for core types and error dataclasses. | 11 | 0 | 391 |
| [test_dashboard.py](test_dashboard.py) | Tests for the dashboard analytics module. | 4 | 0 | 259 |
| [test_design_from_input.py](test_design_from_input.py) | Tests for design_from_input API function. | 1 | 0 | 142 |
| [test_docs_index_generator.py](test_docs_index_generator.py) | Regression tests for deterministic docs-index file output. | 0 | 1 | 32 |
| [test_error_messages.py](test_error_messages.py) | Tests for error message templates. | 7 | 0 | 294 |
| [test_etabs_import_integration.py](test_etabs_import_integration.py) | Integration tests for etabs_import Pydantic conversion funct | 4 | 4 | 330 |
| [test_evidence.py](test_evidence.py) | Focused tests for the supported IS 456 beam evidence envelop | 0 | 10 | 254 |
| [test_exception_hierarchy.py](test_exception_hierarchy.py) | Tests for exception hierarchy in errors module. | 4 | 0 | 278 |
| [test_footing.py](test_footing.py) | Tests for IS 456 footing design — TASK-650/651/652. | 11 | 1 | 1801 |
| [test_footing_api.py](test_footing_api.py) | Focused contract tests for Phase B1 isolated-footing orchest | 0 | 15 | 401 |
| [test_footing_detailing.py](test_footing_detailing.py) | Outcome-focused tests for the bounded footing detailing slic | 0 | 11 | 238 |
| [test_footing_load_transfer.py](test_footing_load_transfer.py) | Focused independent arithmetic checks for IS 456 Cl. 34.4 lo | 0 | 7 | 165 |
| [test_function_quality_checker.py](test_function_quality_checker.py) | Focused regressions for the IS 456 function-quality checker. | 0 | 6 | 132 |
| [test_generated_clients.py](test_generated_clients.py) | Contract checks for the checked-in basic generated clients. | 0 | 3 | 123 |
| [test_git_guidance_semantics.py](test_git_guidance_semantics.py) | Semantic live-guidance discovery and coherence regressions. | 0 | 10 | 362 |
| [test_git_handoff_receipt.py](test_git_handoff_receipt.py) | Regressions for the durable, fail-closed task-to-Git handoff | 0 | 20 | 429 |
| [test_git_state.py](test_git_state.py) | Outcome tests for the read-only, worktree-aware Git state au | 0 | 20 | 682 |
| [test_india_2_truth_hygiene_38_2.py](test_india_2_truth_hygiene_38_2.py) | INDIA-2 Clause 38.2 truth-hygiene acceptance tests. | 0 | 5 | 109 |
| [test_indian_code_manifest.py](test_indian_code_manifest.py) | INDIA-0 truth-manifest and reporting contract tests. | 0 | 10 | 228 |
| [test_inputs.py](test_inputs.py) | Tests for the inputs module (TASK-276: Input Flexibility). | 7 | 0 | 464 |
| [test_install_preflight.py](test_install_preflight.py) | Installed-package preflight is source-independent and decisi | 0 | 1 | 33 |
| [test_is456_common.py](test_is456_common.py) | Tests for IS 456:2000 common modules - stress_blocks, reinfo | 15 | 0 | 900 |
| [test_is456_constants.py](test_is456_constants.py) | Tests for IS 456:2000 named design constants. | 1 | 0 | 163 |
| [test_model_picker.py](test_model_picker.py) | Tests for the deterministic low-token model picker. | 0 | 8 | 132 |
| [test_multi_objective_optimizer.py](test_multi_objective_optimizer.py) | Tests for the multi-objective optimizer module (NSGA-II). | 5 | 0 | 339 |
| [test_new_element_completeness.py](test_new_element_completeness.py) | Regression tests for nested element completeness discovery. | 0 | 3 | 45 |
| [test_numerics.py](test_numerics.py) | Tests for structural_lib.core.numerics - safe arithmetic uti | 4 | 0 | 136 |
| [test_packaging.py](test_packaging.py) | Tests for package distribution correctness. | 9 | 0 | 462 |
| [test_pipeline_state.py](test_pipeline_state.py) | Tests for scripts/pipeline_state.py — Pipeline step tracking | 7 | 0 | 353 |
| [test_private_source_boundary.py](test_private_source_boundary.py) | Protected engineering-source material stays local and outsid | 0 | 2 | 40 |
| [test_release_environment.py](test_release_environment.py) | Regression tests for local release preflight environment sel | 0 | 13 | 281 |
| [test_release_scripts.py](test_release_scripts.py) | Tests for release scripts (bump_version.py, release.py). | 15 | 11 | 1052 |
| [test_release_uat.py](test_release_uat.py) | The exact-wheel acceptance matrix remains data-driven and ex | 0 | 1 | 55 |
| [test_report_edge_cases.py](test_report_edge_cases.py) | Edge case tests for report generation modules (TASK-520). | 4 | 0 | 303 |
| [test_report_svg.py](test_report_svg.py) | Tests for the SVG report generation module. | 4 | 0 | 141 |
| [test_reports.py](test_reports.py) | Tests for the reports module. | 8 | 0 | 447 |
| [test_research_prototypes.py](test_research_prototypes.py) | Tests for research prototypes: Sustainability, Generative De | 4 | 0 | 949 |
| [test_result_base.py](test_result_base.py) | Tests for result_base module. | 7 | 0 | 217 |
| [test_session_automation.py](test_session_automation.py) | Regression tests for maintenance session automation. | 0 | 20 | 1583 |
| [test_session_store.py](test_session_store.py) | Tests for scripts/session_store.py — JSON session persistenc | 7 | 0 | 287 |
| [test_slenderness.py](test_slenderness.py) | Unit tests for slenderness module. | 5 | 0 | 360 |
| [test_testing_strategies.py](test_testing_strategies.py) | Tests for the testing_strategies module (TASK-279). | 12 | 0 | 681 |
| [test_timing_regression.py](test_timing_regression.py) | Regression tests for Windows-compatible timing. | 0 | 1 | 86 |
| [test_token_efficiency.py](test_token_efficiency.py) | Regression tests for repository-side token-efficiency contro | 0 | 5 | 83 |
| [test_tool_manifest.py](test_tool_manifest.py) | Focused gates for the catalogue-derived beam tool manifest. | 0 | 5 | 105 |
| [test_visualization_edge_cases.py](test_visualization_edge_cases.py) | Edge case tests for 3D visualization / geometry module (TASK | 12 | 0 | 757 |
| [test_visualization_geometry_3d.py](test_visualization_geometry_3d.py) | Tests for visualization.geometry_3d module. | 10 | 0 | 781 |
| [test_visualization_integration.py](test_visualization_integration.py) | Integration tests for visualization.geometry_3d with detaili | 2 | 0 | 246 |
| [test_workflow_catalog.py](test_workflow_catalog.py) | Focused contract tests for the one-beam application workflow | 0 | 4 | 89 |
| [test_workflow_runner.py](test_workflow_runner.py) | Bounded-runner tests for the approved beam workflow only. | 0 | 8 | 203 |

## Subfolders

| Folder | Files | Description |
|--------|-------|-------------|
| [codes/](codes/) 📦 | 53 |  |
| [data/](data/) | 5 |  |
| [fixtures/](fixtures/) | 11 |  |
| [helpers/](helpers/) 📦 | 2 |  |
| [integration/](integration/) 📦 | 55 |  |
| [performance/](performance/) 📦 | 3 |  |
| [property/](property/) 📦 | 9 |  |
| [regression/](regression/) 📦 | 11 |  |
| [unit/](unit/) 📦 | 42 |  |
