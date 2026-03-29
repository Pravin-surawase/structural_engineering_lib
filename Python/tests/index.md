# Tests

This document describes the test taxonomy and structure for the structural_engineering_lib test suite.

**Type:** Python Package
**Last Updated:** 2026-03-29
**Files:** 20

## Documentation Files

| File | Title | Description | Lines |
|------|-------|-------------|-------|
| [README.md](README.md) | Test Suite Organization | This document describes the test taxonomy and structure for  | 394 |

## Python Files

| File | Description | Classes | Functions | Lines |
|------|-------------|---------|-----------|-------|
| [conftest.py](conftest.py) | Pytest configuration and Hypothesis profiles for the test su | 0 | 5 | 116 |
| [test_api_results.py](test_api_results.py) | Tests for API result dataclasses. | 3 | 0 | 394 |
| [test_audit.py](test_audit.py) | Tests for audit module (TASK-278). | 6 | 0 | 468 |
| [test_calculation_report.py](test_calculation_report.py) | Tests for the calculation_report module (TASK-277). | 8 | 4 | 612 |
| [test_clause_traceability.py](test_clause_traceability.py) | Tests for IS 456 Traceability Module | 10 | 2 | 489 |
| [test_core.py](test_core.py) | Tests for structural_lib.core module. | 6 | 0 | 176 |
| [test_design_from_input.py](test_design_from_input.py) | Tests for design_from_input API function. | 1 | 0 | 142 |
| [test_error_messages.py](test_error_messages.py) | Tests for error message templates. | 7 | 0 | 294 |
| [test_etabs_import_integration.py](test_etabs_import_integration.py) | Integration tests for etabs_import Pydantic conversion funct | 4 | 4 | 330 |
| [test_exception_hierarchy.py](test_exception_hierarchy.py) | Tests for exception hierarchy in errors module. | 4 | 0 | 278 |
| [test_inputs.py](test_inputs.py) | Tests for the inputs module (TASK-276: Input Flexibility). | 7 | 0 | 442 |
| [test_multi_objective_optimizer.py](test_multi_objective_optimizer.py) | Tests for the multi-objective optimizer module (NSGA-II). | 5 | 0 | 319 |
| [test_reports.py](test_reports.py) | Tests for the reports module. | 8 | 0 | 418 |
| [test_result_base.py](test_result_base.py) | Tests for result_base module. | 7 | 0 | 217 |
| [test_slenderness.py](test_slenderness.py) | Unit tests for slenderness module. | 5 | 0 | 360 |
| [test_testing_strategies.py](test_testing_strategies.py) | Tests for the testing_strategies module (TASK-279). | 12 | 0 | 647 |
| [test_visualization_geometry_3d.py](test_visualization_geometry_3d.py) | Tests for visualization.geometry_3d module. | 10 | 0 | 765 |
| [test_visualization_integration.py](test_visualization_integration.py) | Integration tests for visualization.geometry_3d with detaili | 2 | 0 | 246 |

## Subfolders

| Folder | Files | Description |
|--------|-------|-------------|
| [data/](data/) | 5 |  |
| [fixtures/](fixtures/) | 11 |  |
| [helpers/](helpers/) 📦 | 2 |  |
| [integration/](integration/) | 41 |  |
| [performance/](performance/) | 1 |  |
| [property/](property/) 📦 | 8 |  |
| [regression/](regression/) | 8 |  |
| [unit/](unit/) | 26 |  |
