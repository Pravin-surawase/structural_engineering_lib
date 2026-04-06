# Tests

This document describes the test taxonomy and structure for the structural_engineering_lib test suite.

**Type:** Python Package
**Last Updated:** 2026-04-07
**Files:** 44

## Documentation Files

| File | Title | Description | Lines |
|------|-------|-------------|-------|
| [README.md](README.md) | Test Suite Organization | This document describes the test taxonomy and structure for  | 394 |

## Python Files

| File | Description | Classes | Functions | Lines |
|------|-------------|---------|-----------|-------|
| [__init__.py](__init__.py) |  | 0 | 0 | 1 |
| [conftest.py](conftest.py) | Pytest configuration and Hypothesis profiles for the test su | 0 | 6 | 131 |
| [test_api_results.py](test_api_results.py) | Tests for API result dataclasses. | 3 | 0 | 394 |
| [test_api_stability.py](test_api_stability.py) | EA-9: Wheel API stability tests. | 6 | 0 | 227 |
| [test_api_surface_snapshot.py](test_api_surface_snapshot.py) | Snapshot regression tests — assert minimum API surface count | 5 | 0 | 122 |
| [test_assertion_helpers.py](test_assertion_helpers.py) | Tests for the IS 456 test assertion helpers. | 3 | 0 | 82 |
| [test_audit.py](test_audit.py) | Tests for audit module (TASK-278). | 6 | 0 | 468 |
| [test_boq.py](test_boq.py) | Tests for the BOQ (Bill of Quantities) aggregation module. | 1 | 0 | 190 |
| [test_calculation_report.py](test_calculation_report.py) | Tests for the calculation_report module (TASK-277). | 9 | 4 | 715 |
| [test_clause_traceability.py](test_clause_traceability.py) | Tests for IS 456 Traceability Module | 10 | 2 | 489 |
| [test_column_axial.py](test_column_axial.py) | Tests for column axial module — effective_length() per IS 45 | 6 | 0 | 273 |
| [test_column_biaxial.py](test_column_biaxial.py) | Tests for IS 456 Cl 39.6 biaxial bending check — TASK-635. | 8 | 0 | 947 |
| [test_column_helical.py](test_column_helical.py) | Tests for IS 456 Cl 39.4 helical reinforcement check. | 7 | 0 | 356 |
| [test_column_long.py](test_column_long.py) | Tests for IS 456 Cl 39.7 long (slender) column design. | 15 | 0 | 640 |
| [test_column_return_types.py](test_column_return_types.py) | Tests for UX-02: Column API return type unification. | 7 | 2 | 281 |
| [test_core.py](test_core.py) | Tests for structural_lib.core module. | 6 | 0 | 176 |
| [test_core_types.py](test_core_types.py) | Tests for core types and error dataclasses. | 11 | 0 | 391 |
| [test_dashboard.py](test_dashboard.py) | Tests for the dashboard analytics module. | 4 | 0 | 259 |
| [test_design_from_input.py](test_design_from_input.py) | Tests for design_from_input API function. | 1 | 0 | 142 |
| [test_error_messages.py](test_error_messages.py) | Tests for error message templates. | 7 | 0 | 294 |
| [test_etabs_import_integration.py](test_etabs_import_integration.py) | Integration tests for etabs_import Pydantic conversion funct | 4 | 4 | 330 |
| [test_exception_hierarchy.py](test_exception_hierarchy.py) | Tests for exception hierarchy in errors module. | 4 | 0 | 278 |
| [test_footing.py](test_footing.py) | Tests for IS 456 footing design — TASK-650/651/652. | 11 | 0 | 1564 |
| [test_inputs.py](test_inputs.py) | Tests for the inputs module (TASK-276: Input Flexibility). | 7 | 0 | 464 |
| [test_is456_common.py](test_is456_common.py) | Tests for IS 456:2000 common modules - stress_blocks, reinfo | 15 | 0 | 747 |
| [test_is456_constants.py](test_is456_constants.py) | Tests for IS 456:2000 named design constants. | 1 | 0 | 163 |
| [test_multi_objective_optimizer.py](test_multi_objective_optimizer.py) | Tests for the multi-objective optimizer module (NSGA-II). | 5 | 0 | 319 |
| [test_numerics.py](test_numerics.py) | Tests for structural_lib.core.numerics - safe arithmetic uti | 4 | 0 | 136 |
| [test_packaging.py](test_packaging.py) | Tests for package distribution correctness. | 6 | 0 | 258 |
| [test_pipeline_state.py](test_pipeline_state.py) | Tests for scripts/pipeline_state.py — Pipeline step tracking | 7 | 0 | 353 |
| [test_release_scripts.py](test_release_scripts.py) | Tests for release scripts (bump_version.py, release.py). | 13 | 1 | 342 |
| [test_report_edge_cases.py](test_report_edge_cases.py) | Edge case tests for report generation modules (TASK-520). | 4 | 0 | 290 |
| [test_report_svg.py](test_report_svg.py) | Tests for the SVG report generation module. | 4 | 0 | 141 |
| [test_reports.py](test_reports.py) | Tests for the reports module. | 8 | 0 | 418 |
| [test_research_prototypes.py](test_research_prototypes.py) | Tests for research prototypes: Sustainability, Generative De | 4 | 0 | 908 |
| [test_result_base.py](test_result_base.py) | Tests for result_base module. | 7 | 0 | 217 |
| [test_session_store.py](test_session_store.py) | Tests for scripts/session_store.py — JSON session persistenc | 7 | 0 | 287 |
| [test_slenderness.py](test_slenderness.py) | Unit tests for slenderness module. | 5 | 0 | 360 |
| [test_testing_strategies.py](test_testing_strategies.py) | Tests for the testing_strategies module (TASK-279). | 12 | 0 | 681 |
| [test_visualization_edge_cases.py](test_visualization_edge_cases.py) | Edge case tests for 3D visualization / geometry module (TASK | 12 | 0 | 757 |
| [test_visualization_geometry_3d.py](test_visualization_geometry_3d.py) | Tests for visualization.geometry_3d module. | 10 | 0 | 765 |
| [test_visualization_integration.py](test_visualization_integration.py) | Integration tests for visualization.geometry_3d with detaili | 2 | 0 | 246 |

## Subfolders

| Folder | Files | Description |
|--------|-------|-------------|
| [codes/](codes/) 📦 | 11 |  |
| [data/](data/) | 5 |  |
| [fixtures/](fixtures/) | 11 |  |
| [helpers/](helpers/) 📦 | 2 |  |
| [integration/](integration/) 📦 | 43 |  |
| [performance/](performance/) 📦 | 3 |  |
| [property/](property/) 📦 | 9 |  |
| [regression/](regression/) 📦 | 11 |  |
| [unit/](unit/) 📦 | 32 |  |
