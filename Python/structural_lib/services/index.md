# Services

**Type:** Python Package
**Last Updated:** 2026-08-22
**Files:** 54

## Public API

- `SymmetricCombinedFootingDesignInput`
- `SymmetricCombinedFootingDesignProvenance`
- `SymmetricCombinedFootingDesignResult`
- `SymmetricCombinedFootingDesignStatus`
- `design_symmetric_combined_footing_is456`
- `GravityBalanceBoundaryV1`
- `GravityBalanceV1`
- `GravityCombinationActionV1`
- `GravityCombinationContributionV1`
- `GravityLedgerEntryV1`
- `GravityLedgerStageV1`
- `GravityLoadLedgerError`
- `GravityLoadLedgerV1`
- `build_gravity_load_ledger_v1`
- `PropertyLineStrapFootingDesignInput`
- `PropertyLineStrapFootingDesignProvenance`
- `PropertyLineStrapFootingDesignResult`
- `PropertyLineStrapFootingDesignStatus`
- `design_property_line_strap_footing_is456`

## Python Files

| File | Description | Classes | Functions | Lines |
|------|-------------|---------|-----------|-------|
| [__init__.py](__init__.py) | Application-layer public workflow exports. | 0 | 0 | 50 |
| [adapters.py](adapters.py) | Adapters for converting various input formats to canonical m | 6 | 0 | 2100 |
| [api.py](api.py) | Module:       api | 0 | 0 | 454 |
| [api_hub.py](api_hub.py) | Module:       api | 0 | 0 | 238 |
| [api_results.py](api_results.py) | Module:       api_results | 8 | 0 | 507 |
| [audit.py](audit.py) | Module:       audit | 3 | 3 | 587 |
| [batch.py](batch.py) | Strict project beam design plus a delegating legacy batch su | 0 | 5 | 626 |
| [bbs.py](bbs.py) | Bar Bending Schedule (BBS) Module — IS 2502:1999 / SP 34:198 | 3 | 19 | 1134 |
| [beam_api.py](beam_api.py) | Module:       beam_api | 0 | 20 | 2367 |
| [beam_pipeline.py](beam_pipeline.py) | beam_pipeline — Unified application-layer pipeline for beam  | 10 | 3 | 660 |
| [boq.py](boq.py) | Project Bill of Quantities (BOQ) — Aggregation Module | 4 | 1 | 209 |
| [calculation_report.py](calculation_report.py) | Module:       calculation_report | 4 | 1 | 722 |
| [capabilities.py](capabilities.py) | Discoverable supported-case registry for the IS 456 public l | 7 | 3 | 2057 |
| [cli_design.py](cli_design.py) | Strict, lossless intake and compatibility output for the adv | 4 | 2 | 628 |
| [column_api.py](column_api.py) | Module:       column_api | 0 | 13 | 1546 |
| [combined_footing_api.py](combined_footing_api.py) | Stable orchestration for the bounded symmetric combined-foot | 4 | 2 | 252 |
| [common_api.py](common_api.py) | Module:       common_api | 0 | 5 | 709 |
| [costing.py](costing.py) | Cost calculation utilities for structural elements. | 2 | 8 | 376 |
| [dashboard.py](dashboard.py) | Insights module for dashboard aggregation and live code chec | 4 | 3 | 512 |
| [deep_beam_api.py](deep_beam_api.py) | Stable orchestration for the bounded IS 456 simply supported | 3 | 1 | 247 |
| [dxf_export.py](dxf_export.py) | DXF Export Module — Beam Detail Drawing Generation | 0 | 18 | 1833 |
| [etabs_import.py](etabs_import.py) | ETABS CSV Import Module. | 3 | 12 | 1089 |
| [evidence.py](evidence.py) | Canonical evidence identity for the supported IS 456 beam de | 0 | 4 | 386 |
| [excel_bridge.py](excel_bridge.py) | Excel UDF Bridge - Exposes structural_lib functions to Excel | 0 | 7 | 305 |
| [excel_integration.py](excel_integration.py) | Excel Integration Module — Bridge between Excel data and Det | 2 | 9 | 489 |
| [excel_workbench.py](excel_workbench.py) | Strict selected-table orchestration for Excel Routine Workbe | 1 | 8 | 951 |
| [flat_slab_api.py](flat_slab_api.py) | Stable orchestration for the bounded regular interior flat-s | 4 | 2 | 339 |
| [footing_api.py](footing_api.py) | Bounded orchestration for concentric isolated footings (IS 4 | 5 | 1 | 915 |
| [gravity_calculation_book.py](gravity_calculation_book.py) | Deterministic review dossier for Building Gravity Workflow V | 3 | 4 | 254 |
| [gravity_loads.py](gravity_loads.py) | Deterministic dead/live source, transfer, combination, and b | 8 | 1 | 631 |
| [gravity_workflow.py](gravity_workflow.py) | Fail-closed component orchestration for Building Gravity Wor | 0 | 3 | 914 |
| [import_ledger.py](import_ledger.py) | Versioned, lossless import evidence models. | 11 | 0 | 187 |
| [imports.py](imports.py) | Fail-closed multi-format CSV import boundary. | 2 | 6 | 1104 |
| [intelligence.py](intelligence.py) | Compatibility shim for legacy imports. | 0 | 0 | 36 |
| [job_cli.py](job_cli.py) | job_cli | 0 | 1 | 203 |
| [job_runner.py](job_runner.py) | job_runner | 0 | 4 | 317 |
| [multi_objective_optimizer.py](multi_objective_optimizer.py) | Multi-Objective Optimization Module | 2 | 2 | 642 |
| [optimization.py](optimization.py) | Optimization algorithms for structural design. | 2 | 1 | 311 |
| [project_beam.py](project_beam.py) | Versioned, fail-closed project beam input and result contrac | 8 | 2 | 716 |
| [rebar.py](rebar.py) | Rebar configuration validation and application helpers. | 0 | 2 | 251 |
| [rebar_optimizer.py](rebar_optimizer.py) | Rebar arrangement optimizer (deterministic). | 1 | 1 | 322 |
| [release_uat.py](release_uat.py) | Source-free exact-wheel UAT for the pre-release input-safety | 0 | 2 | 591 |
| [report.py](report.py) | Report generation module for beam design results. | 5 | 14 | 1772 |
| [report_svg.py](report_svg.py) | SVG helpers for report visuals (stdlib only). | 0 | 2 | 279 |
| [serialization.py](serialization.py) | JSON serialization utilities for canonical data models. | 0 | 13 | 476 |
| [slab_api.py](slab_api.py) | Stable orchestration entry points for the bounded IS 456 sla | 4 | 7 | 851 |
| [source_identity.py](source_identity.py) | Controlled IS 456 source and route-specific amendment identi | 2 | 0 | 67 |
| [staircase_api.py](staircase_api.py) | Stable orchestration for the bounded IS 456 straight-flight  | 3 | 1 | 209 |
| [strap_footing_api.py](strap_footing_api.py) | Stable orchestration for the bounded property-line strap-foo | 4 | 2 | 280 |
| [testing_strategies.py](testing_strategies.py) | Module:       testing_strategies | 9 | 2 | 655 |
| [tool_manifest.py](tool_manifest.py) | Deterministic AI-tool descriptors projected from the workflo | 1 | 3 | 163 |
| [wall_api.py](wall_api.py) | Stable orchestration for the bounded IS 456 braced-wall work | 3 | 1 | 227 |
| [workflow_catalog.py](workflow_catalog.py) | Versioned, transport-neutral catalogue for approved applicat | 6 | 7 | 445 |
| [workflow_runner.py](workflow_runner.py) | Bounded in-memory runner for one approved beam review workfl | 5 | 3 | 568 |
