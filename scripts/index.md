# Scripts

> Development, validation, discovery, release-preparation, and maintenance tools.

**Type:** Python Package
**Last Updated:** 2026-08-17
**Files:** 112

## Config Files

- [automation-map.json](automation-map.json)

## Documentation Files

| File | Title | Description | Lines |
|------|-------|-------------|-------|
| [README.md](README.md) | Scripts | > Development, validation, discovery, release-preparation, a | 80 |

## Python Files

| File | Description | Classes | Functions | Lines |
|------|-------------|---------|-----------|-------|
| [agent_compliance_checker.py](agent_compliance_checker.py) | Agent compliance checker — verify agents followed their .age | 0 | 12 | 541 |
| [agent_context.py](agent_context.py) | Agent Context Loader — gives each agent its tailored startup | 0 | 20 | 642 |
| [agent_drift_detector.py](agent_drift_detector.py) | Agent drift detector — detect when agents deviate from presc | 0 | 9 | 649 |
| [agent_evolve_instructions.py](agent_evolve_instructions.py) | Agent instruction evolver — self-improving agent customizati | 0 | 12 | 550 |
| [agent_feedback.py](agent_feedback.py) | Agent feedback collection and analysis. | 0 | 6 | 423 |
| [agent_scorer.py](agent_scorer.py) | Agent scorer — score agents on 11 performance dimensions. | 0 | 9 | 548 |
| [agent_session_collector.py](agent_session_collector.py) | Agent session collector — gather all session artifacts for s | 0 | 9 | 320 |
| [agent_trends.py](agent_trends.py) | Agent trends — time series analysis and degradation detectio | 0 | 7 | 383 |
| [audit_error_handling.py](audit_error_handling.py) | Audit error handling compliance across structural_lib module | 2 | 3 | 286 |
| [audit_input_validation.py](audit_input_validation.py) | Audit Input Validation Coverage for structural_lib. | 2 | 5 | 393 |
| [audit_permissions.py](audit_permissions.py) | Permission audit report for all agents. | 3 | 3 | 468 |
| [audit_readiness_report.py](audit_readiness_report.py) | Audit Readiness Report Generator | 2 | 11 | 783 |
| [batch_migrate_runner.py](batch_migrate_runner.py) | Batch migration runner with per-operation rollback logs. | 1 | 2 | 467 |
| [benchmark_api.py](benchmark_api.py) | API Performance Benchmark Script. | 4 | 9 | 837 |
| [bump_version.py](bump_version.py) | Version Bump Script — Single Source of Truth | 0 | 4 | 484 |
| [check_all.py](check_all.py) | Unified check orchestrator — runs all validation scripts in  | 3 | 1 | 717 |
| [check_api.py](check_api.py) | Validate the live React/FastAPI contract and Python API docu | 1 | 4 | 400 |
| [check_api_compat.py](check_api_compat.py) | Compatibility wrapper for the canonical public API manifest  | 0 | 1 | 49 |
| [check_architecture_boundaries.py](check_architecture_boundaries.py) | Architecture Boundary Linter. | 3 | 9 | 495 |
| [check_bootstrap_freshness.py](check_bootstrap_freshness.py) | Check if bootstrap docs are stale compared to actual codebas | 0 | 4 | 290 |
| [check_circular_imports.py](check_circular_imports.py) | Circular Import Detector for the Python Structural Library | 5 | 1 | 464 |
| [check_clause_coverage.py](check_clause_coverage.py) | Report standard-namespaced clause/reference decorator regist | 0 | 5 | 254 |
| [check_cli_reference.py](check_cli_reference.py) | Ensure CLI reference includes required commands. | 0 | 1 | 48 |
| [check_codex_git_workflow.py](check_codex_git_workflow.py) | Guard the Codex-native Git/GitHub workflow contract. | 0 | 3 | 638 |
| [check_doc_versions.py](check_doc_versions.py) | Doc Version Drift Check — Validate no stale *library* versio | 0 | 2 | 72 |
| [check_docker_config.py](check_docker_config.py) | Docker Configuration Validator. | 0 | 6 | 295 |
| [check_docs.py](check_docs.py) | Unified documentation checker — consolidates 4 doc validatio | 0 | 6 | 675 |
| [check_fastapi_issues.py](check_fastapi_issues.py) | FastAPI Issues AST Scanner. | 3 | 4 | 468 |
| [check_function_quality.py](check_function_quality.py) | 12-point quality checklist for IS 456 functions. | 3 | 6 | 678 |
| [check_governance.py](check_governance.py) | Unified governance checker — folder structure + compliance v | 2 | 19 | 1042 |
| [check_instruction_drift.py](check_instruction_drift.py) | Check for content drift between .github/instructions/ and .c | 0 | 2 | 219 |
| [check_links.py](check_links.py) | Check and fix broken internal links in markdown files. | 0 | 2 | 351 |
| [check_new_element_completeness.py](check_new_element_completeness.py) | Check structural element completeness across all 7 layers. | 0 | 14 | 669 |
| [check_next_session_brief_length.py](check_next_session_brief_length.py) | Ensure next-session-brief.md stays concise. | 0 | 1 | 31 |
| [check_openapi_drift.py](check_openapi_drift.py) | Check OpenAPI spec for drift against baseline. | 0 | 5 | 193 |
| [check_openapi_snapshot.py](check_openapi_snapshot.py) | Check OpenAPI spec against baseline snapshot to detect API d | 0 | 1 | 231 |
| [check_python_version.py](check_python_version.py) | Python Version Consistency Checker | 0 | 5 | 208 |
| [check_repo_hygiene.py](check_repo_hygiene.py) | Fail if tracked hygiene artifacts exist in the repository. | 0 | 1 | 44 |
| [check_scripts_index.py](check_scripts_index.py) | Ensure scripts/index.json and automation-map.json match the  | 0 | 1 | 223 |
| [check_tasks_format.py](check_tasks_format.py) | Validate docs/TASKS.md structure and WIP rules. | 0 | 1 | 161 |
| [check_token_efficiency.py](check_token_efficiency.py) | Validate repository-side Codex token-efficiency controls. | 0 | 2 | 206 |
| [check_type_annotations.py](check_type_annotations.py) | Type Annotation Checker for the Python Structural Library | 4 | 1 | 542 |
| [classify_branch_disposition.py](classify_branch_disposition.py) | Classify branch/worktree disposition from inspection-only ev | 2 | 3 | 823 |
| [collect_diagnostics.py](collect_diagnostics.py) | Collect a compact diagnostics bundle for debugging and suppo | 0 | 2 | 123 |
| [config_precedence.py](config_precedence.py) | Configuration precedence auditing for instruction files. | 2 | 10 | 564 |
| [create_doc.py](create_doc.py) | Create a new documentation file with proper metadata header. | 0 | 5 | 259 |
| [create_test_scaffold.py](create_test_scaffold.py) | Test Scaffold Generator (Solution 2) | 0 | 3 | 238 |
| [diagnose_ci.py](diagnose_ci.py) | CI failure diagnosis — check, reproduce, and fix CI failures | 0 | 13 | 339 |
| [discover_api_signatures.py](discover_api_signatures.py) | Discover and display structural_lib API function signatures. | 2 | 6 | 398 |
| [dxf_render.py](dxf_render.py) | Render DXF drawings to PNG or PDF using ezdxf + matplotlib. | 0 | 2 | 141 |
| [evolve.py](evolve.py) | Self-evolution engine — orchestrates project health, feedbac | 0 | 12 | 552 |
| [export_paper_data.py](export_paper_data.py) | Export agent performance data for academic paper. | 0 | 8 | 388 |
| [external_cli_test.py](external_cli_test.py) | External CLI smoke test (S-007). | 1 | 1 | 401 |
| [find_automation.py](find_automation.py) | Find the right automation script for a task. | 0 | 8 | 192 |
| [fix_broken_links.py](fix_broken_links.py) | Fix broken internal links in markdown files. | 0 | 6 | 268 |
| [generate_api_classification.py](generate_api_classification.py) | Generate or validate the Alpha public API classification reg | 0 | 2 | 152 |
| [generate_api_manifest.py](generate_api_manifest.py) | Generate or validate the public API manifest for structural_ | 0 | 1 | 159 |
| [generate_beam_tool_manifest.py](generate_beam_tool_manifest.py) | Generate and byte-check the catalogue-derived beam tool mani | 0 | 4 | 64 |
| [generate_client_sdks.py](generate_client_sdks.py) | Generate client SDKs from FastAPI OpenAPI specification. | 0 | 6 | 560 |
| [generate_docs_index.py](generate_docs_index.py) | Generate machine-readable JSON index of documentation. | 0 | 7 | 246 |
| [generate_enhanced_index.py](generate_enhanced_index.py) | Generate enhanced index.json + index.md for ANY folder type. | 0 | 11 | 947 |
| [generate_error_docs.py](generate_error_docs.py) | Generate docs/reference/error-codes.md from core/errors.py. | 0 | 4 | 139 |
| [generate_indian_code_manifest.py](generate_indian_code_manifest.py) | Generate or verify the INDIA-0 Indian-code truth manifest. | 0 | 1 | 43 |
| [git_handoff_receipt.py](git_handoff_receipt.py) | Build and validate fail-closed task-to-Git handoff receipts. | 0 | 4 | 573 |
| [git_state.py](git_state.py) | Read-only, worktree-aware Git state authority. | 5 | 5 | 1004 |
| [governance_health_score.py](governance_health_score.py) | Governance Health Score - TASK-289 | 3 | 1 | 515 |
| [migrate_python_module.py](migrate_python_module.py) | Migrate a Python module to a new location with import update | 0 | 8 | 516 |
| [migrate_react_component.py](migrate_react_component.py) | Migrate a React component to a new feature-grouped folder. | 0 | 9 | 475 |
| [model_picker.py](model_picker.py) | Recommend a supported model and reasoning effort for a repos | 1 | 2 | 305 |
| [node_runtime.py](node_runtime.py) | Select and run the healthy Node.js major pinned by ``.nvmrc` | 0 | 4 | 205 |
| [parity_dashboard.py](parity_dashboard.py) | Parity dashboard across declared Indian-code scope and appli | 0 | 6 | 466 |
| [pipeline_state.py](pipeline_state.py) | Pipeline state tracking for multi-step agent workflows. | 2 | 17 | 868 |
| [preflight.py](preflight.py) | Pre-flight check — catch common mistakes BEFORE they happen. | 0 | 9 | 203 |
| [project_health.py](project_health.py) | Unified project health scanner with auto-fix capability. | 3 | 9 | 908 |
| [prompt_router.py](prompt_router.py) | Prompt router — routes natural language queries to the best  | 1 | 5 | 700 |
| [release.py](release.py) | Unified release management CLI. | 0 | 11 | 2252 |
| [safe_file_delete.py](safe_file_delete.py) | Safe file delete script with reference checking. | 0 | 5 | 355 |
| [safe_file_move.py](safe_file_move.py) | Safe file move script with automatic link updates. | 0 | 6 | 500 |
| [session.py](session.py) | Unified session management CLI. | 0 | 20 | 2512 |
| [session_store.py](session_store.py) | JSON-based session state persistence for AI agent sessions. | 1 | 14 | 374 |
| [skill_tiers.py](skill_tiers.py) | Skill tier classification and management for AI agents. | 1 | 11 | 485 |
| [sync_numbers.py](sync_numbers.py) | Scan codebase and sync stale numbers across documentation fi | 2 | 11 | 502 |
| [test_api_parity.py](test_api_parity.py) | API Parity Testing Script | 2 | 10 | 457 |
| [test_changed.py](test_changed.py) | Smart test runner — run only tests related to changed files. | 0 | 3 | 219 |
| [test_cli_smoke.py](test_cli_smoke.py) | CLI Smoke Tests — validate all key scripts work correctly. | 0 | 3 | 298 |
| [test_import_pipeline.py](test_import_pipeline.py) | End-to-end test of all import paths. | 0 | 20 | 412 |
| [tool_permissions.py](tool_permissions.py) | Tool permission enforcement for agent operations. | 1 | 5 | 437 |
| [tool_registry.py](tool_registry.py) | Unified tool registry — connects agents, skills, scripts, an | 1 | 12 | 556 |
| [update_test_stats.py](update_test_stats.py) | Update Test Stats — Dynamic test count updater. | 0 | 5 | 211 |
| [validate_api_contracts.py](validate_api_contracts.py) | API Contract Validator. | 2 | 9 | 647 |
| [validate_imports.py](validate_imports.py) | Validate Python imports across the project after migration. | 0 | 6 | 365 |
| [validate_schema_snapshots.py](validate_schema_snapshots.py) | Schema Snapshot Validator. | 0 | 6 | 257 |
| [validate_script_refs.py](validate_script_refs.py) | Validate that active control paths reference existing script | 0 | 6 | 235 |

## Shell Script Files

- [agent_brief.sh](agent_brief.sh) — ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- [agent_mistakes_report.sh](agent_mistakes_report.sh) — Agent Mistakes Report
- [agent_start.sh](agent_start.sh) — Unified Agent Start Script
- [archive_old_files.sh](archive_old_files.sh) — Auto-archive files older than 90 days from docs/_active/
- [check_not_main.sh](check_not_main.sh) — Compatibility entrypoint. Fails closed on main, detached, or unknown state.
- [check_root_file_count.sh](check_root_file_count.sh) — Check Root File Count
- [check_unfinished_merge.sh](check_unfinished_merge.sh) — Compatibility entrypoint. The shared kernel detects every operation from the
- [check_version_consistency.sh](check_version_consistency.sh) — check_version_consistency.sh - Verify version strings are consistent
- [check_wip_limits.sh](check_wip_limits.sh) — check_wip_limits.sh - Enforce WIP (Work In Progress) limits
- [ci_local.sh](ci_local.sh) — Local equivalent of the maintained PR validation lanes.
- [collect_metrics.sh](collect_metrics.sh) — Metrics Collection Script
- [generate_all_indexes.sh](generate_all_indexes.sh) — Generate index.json + index.md for all research-relevant folders
- [launch_stack.sh](launch_stack.sh) — launch_stack.sh — Full-stack development launcher for structural_engineering_lib
- [python_runtime.sh](python_runtime.sh) — Resolve the repository Python interpreter across primary and linked worktrees.
- [repo_health_check.sh](repo_health_check.sh)
- [validate_git_state.sh](validate_git_state.sh) — Compatibility entrypoint. scripts/git_state.py owns all Git-state semantics.
- [watch_tests.sh](watch_tests.sh) — Watch Mode (Solution 5 - Dev Automation)

## Subfolders

| Folder | Files | Description |
|--------|-------|-------------|
| [hooks/](hooks/) 📦 | 3 |  |
