# Tests

This document describes the test taxonomy and structure for the structural_engineering_lib test suite.

**Type:** Python Package
**Last Updated:** 2026-04-02
**Files:** 34

## Documentation Files

| File | Title | Description | Lines |
|------|-------|-------------|-------|
| [README.md](README.md) | Test Suite Organization | This document describes the test taxonomy and structure for  | 394 |

## Python Files

| File | Description | Classes | Functions | Lines |
|------|-------------|---------|-----------|-------|
| [conftest.py](conftest.py) | Pytest configuration and Hypothesis profiles for the test su | 0 | 5 | 116 |
| [test_api_results.py](test_api_results.py) | Tests for API result dataclasses. | 3 | 0 | 394 |
| [test_api_surface_snapshot.py](test_api_surface_snapshot.py) | Snapshot regression tests — assert minimum API surface count | 5 | 0 | 120 |
| [test_assertion_helpers.py](test_assertion_helpers.py) | Tests for the IS 456 test assertion helpers. | 3 | 0 | 80 |
| [test_audit.py](test_audit.py) | Tests for audit module (TASK-278). | 6 | 0 | 468 |
| [test_boq.py](test_boq.py) | Tests for the BOQ (Bill of Quantities) aggregation module. | 1 | 0 | 190 |
| [test_calculation_report.py](test_calculation_report.py) | Tests for the calculation_report module (TASK-277). | 8 | 4 | 612 |
| [test_clause_traceability.py](test_clause_traceability.py) | Tests for IS 456 Traceability Module | 10 | 2 | 489 |
| [test_column_axial.py](test_column_axial.py) | Tests for column axial module — effective_length() per IS 45 | 6 | 0 | 273 |
| [test_column_biaxial.py](test_column_biaxial.py) | Tests for IS 456 Cl 39.6 biaxial bending check — TASK-635. | 8 | 0 | 947 |
| [test_core.py](test_core.py) | Tests for structural_lib.core module. | 6 | 0 | 176 |
| [test_core_types.py](test_core_types.py) | Tests for core types and error dataclasses. | 8 | 0 | 261 |
| [test_dashboard.py](test_dashboard.py) | Tests for the dashboard analytics module. | 4 | 0 | 259 |
| [test_design_from_input.py](test_design_from_input.py) | Tests for design_from_input API function. | 1 | 0 | 142 |
| [test_error_messages.py](test_error_messages.py) | Tests for error message templates. | 7 | 0 | 294 |
| [test_etabs_import_integration.py](test_etabs_import_integration.py) | Integration tests for etabs_import Pydantic conversion funct | 4 | 4 | 330 |
| [test_exception_hierarchy.py](test_exception_hierarchy.py) | Tests for exception hierarchy in errors module. | 4 | 0 | 278 |
| [test_inputs.py](test_inputs.py) | Tests for the inputs module (TASK-276: Input Flexibility). | 7 | 0 | 442 |
| [test_is456_common.py](test_is456_common.py) | Tests for IS 456:2000 common modules - stress_blocks, reinfo | 10 | 0 | 537 |
| [test_is456_constants.py](test_is456_constants.py) | Tests for IS 456:2000 named design constants. | 1 | 0 | 163 |
| [test_multi_objective_optimizer.py](test_multi_objective_optimizer.py) | Tests for the multi-objective optimizer module (NSGA-II). | 5 | 0 | 319 |
| [test_numerics.py](test_numerics.py) | Tests for structural_lib.core.numerics - safe arithmetic uti | 4 | 0 | 136 |
| [test_pipeline_state.py](test_pipeline_state.py) | Tests for scripts/pipeline_state.py — Pipeline step tracking | 7 | 0 | 351 |
| [test_release_scripts.py](test_release_scripts.py) | Tests for release scripts (bump_version.py, release.py). | 13 | 1 | 340 |
| [test_report_svg.py](test_report_svg.py) | Tests for the SVG report generation module. | 4 | 0 | 141 |
| [test_reports.py](test_reports.py) | Tests for the reports module. | 8 | 0 | 418 |
| [test_result_base.py](test_result_base.py) | Tests for result_base module. | 7 | 0 | 217 |
| [test_session_store.py](test_session_store.py) | Tests for scripts/session_store.py — JSON session persistenc | 7 | 0 | 285 |
| [test_slenderness.py](test_slenderness.py) | Unit tests for slenderness module. | 5 | 0 | 360 |
| [test_testing_strategies.py](test_testing_strategies.py) | Tests for the testing_strategies module (TASK-279). | 12 | 0 | 647 |
| [test_visualization_geometry_3d.py](test_visualization_geometry_3d.py) | Tests for visualization.geometry_3d module. | 10 | 0 | 765 |
| [test_visualization_integration.py](test_visualization_integration.py) | Integration tests for visualization.geometry_3d with detaili | 2 | 0 | 246 |

## Subfolders

| Folder | Files | Description |
|--------|-------|-------------|
| [codes/](codes/) 📦 | 7 |  |
| [data/](data/) | 5 |  |
| [fixtures/](fixtures/) | 11 |  |
| [helpers/](helpers/) 📦 | 2 |  |
| [integration/](integration/) | 41 |  |
| [performance/](performance/) | 1 |  |
| [property/](property/) 📦 | 8 |  |
| [regression/](regression/) | 8 |  |
| [unit/](unit/) | 27 |  |
