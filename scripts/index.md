# Scripts

> **Purpose:** Automation scripts for development, CI/CD, and maintenance tasks

**Type:** Python Package
**Last Updated:** 2026-03-24
**Files:** 85

## Config Files

- [automation-map.json](automation-map.json)

## Documentation Files

| File | Title | Description | Lines |
|------|-------|-------------|-------|
| [README.md](README.md) | Scripts | > **Purpose:** Automation scripts for development, CI/CD, an | 119 |

## Python Files

| File | Description | Classes | Functions | Lines |
|------|-------------|---------|-----------|-------|
| [audit_error_handling.py](audit_error_handling.py) | Audit error handling compliance across structural_lib module | 2 | 3 | 286 |
| [audit_input_validation.py](audit_input_validation.py) | Audit Input Validation Coverage for structural_lib. | 2 | 5 | 393 |
| [audit_readiness_report.py](audit_readiness_report.py) | Audit Readiness Report Generator | 2 | 11 | 815 |
| [batch_migrate_runner.py](batch_migrate_runner.py) | Batch migration runner with per-operation rollback logs. | 1 | 2 | 439 |
| [benchmark_api.py](benchmark_api.py) | API Performance Benchmark Script. | 4 | 9 | 799 |
| [bump_version.py](bump_version.py) | Version Bump Script — Single Source of Truth | 0 | 3 | 397 |
| [check_api.py](check_api.py) | Unified API validation — signatures, docs, and sync checks. | 1 | 4 | 379 |
| [check_architecture_boundaries.py](check_architecture_boundaries.py) | Architecture Boundary Linter. | 3 | 9 | 501 |
| [check_bootstrap_freshness.py](check_bootstrap_freshness.py) | Check if bootstrap docs are stale compared to actual codebas | 0 | 4 | 262 |
| [check_circular_imports.py](check_circular_imports.py) | Circular Import Detector for Streamlit Application | 5 | 1 | 462 |
| [check_cli_reference.py](check_cli_reference.py) | Ensure CLI reference includes required commands. | 0 | 1 | 48 |
| [check_cost_optimizer_issues.py](check_cost_optimizer_issues.py) | Automated detection of common cost optimizer issues. | 1 | 2 | 237 |
| [check_doc_versions.py](check_doc_versions.py) | Doc Version Drift Check — Validate no stale *library* versio | 0 | 2 | 72 |
| [check_docker_config.py](check_docker_config.py) | Docker Configuration Validator. | 0 | 6 | 260 |
| [check_docs.py](check_docs.py) | Unified documentation checker — consolidates 4 doc validatio | 0 | 5 | 534 |
| [check_fastapi_issues.py](check_fastapi_issues.py) | FastAPI Issues AST Scanner. | 3 | 4 | 422 |
| [check_governance.py](check_governance.py) | Unified governance checker — folder structure + compliance v | 2 | 18 | 847 |
| [check_links.py](check_links.py) | Check and fix broken internal links in markdown files. | 0 | 2 | 327 |
| [check_next_session_brief_length.py](check_next_session_brief_length.py) | Ensure next-session-brief.md stays concise. | 0 | 1 | 31 |
| [check_openapi_snapshot.py](check_openapi_snapshot.py) | Check OpenAPI spec against baseline snapshot to detect API d | 0 | 1 | 207 |
| [check_performance_issues.py](check_performance_issues.py) | Performance Issue Detector for Streamlit Application | 4 | 1 | 597 |
| [check_python_version.py](check_python_version.py) | Python Version Consistency Checker | 0 | 5 | 215 |
| [check_repo_hygiene.py](check_repo_hygiene.py) | Fail if tracked hygiene artifacts exist in the repository. | 0 | 1 | 44 |
| [check_scripts_index.py](check_scripts_index.py) | Ensure scripts/index.json and automation-map.json match the  | 0 | 1 | 157 |
| [check_streamlit.py](check_streamlit.py) | Unified Streamlit validation CLI. | 4 | 4 | 2367 |
| [check_tasks_format.py](check_tasks_format.py) | Validate docs/TASKS.md structure and WIP rules. | 0 | 1 | 160 |
| [check_type_annotations.py](check_type_annotations.py) | Type Annotation Checker for Streamlit Application | 4 | 1 | 542 |
| [check_ui_duplication.py](check_ui_duplication.py) | Streamlit UI Duplication Scanner. | 2 | 11 | 619 |
| [cleanup_stale_branches.py](cleanup_stale_branches.py) | Cleanup stale remote branches. | 0 | 7 | 187 |
| [collect_diagnostics.py](collect_diagnostics.py) | Collect a compact diagnostics bundle for debugging and suppo | 0 | 2 | 122 |
| [create_doc.py](create_doc.py) | Create a new documentation file with proper metadata header. | 0 | 5 | 261 |
| [create_test_scaffold.py](create_test_scaffold.py) | Test Scaffold Generator (Solution 2) | 0 | 4 | 423 |
| [discover_api_signatures.py](discover_api_signatures.py) | Discover and display structural_lib API function signatures. | 2 | 6 | 376 |
| [dxf_render.py](dxf_render.py) | Render DXF drawings to PNG or PDF using ezdxf + matplotlib. | 0 | 2 | 128 |
| [external_cli_test.py](external_cli_test.py) | External CLI smoke test (S-007). | 1 | 1 | 396 |
| [find_automation.py](find_automation.py) | Find the right automation script for a task. | 0 | 6 | 174 |
| [generate_api_manifest.py](generate_api_manifest.py) | Generate or validate the public API manifest for structural_ | 0 | 1 | 157 |
| [generate_client_sdks.py](generate_client_sdks.py) | Generate client SDKs from FastAPI OpenAPI specification. | 0 | 6 | 526 |
| [generate_docs_index.py](generate_docs_index.py) | Generate machine-readable JSON index of documentation. | 0 | 7 | 245 |
| [generate_enhanced_index.py](generate_enhanced_index.py) | Generate enhanced index.json + index.md for ANY folder type. | 0 | 10 | 800 |
| [generate_streamlit_page.py](generate_streamlit_page.py) | Streamlit Page Scaffold Generator | 0 | 4 | 477 |
| [governance_health_score.py](governance_health_score.py) | Governance Health Score - TASK-289 | 3 | 1 | 515 |
| [lint_vba.py](lint_vba.py) | VBA Syntax Linter - Pre-import validation | 1 | 1 | 212 |
| [migrate_python_module.py](migrate_python_module.py) | Migrate a Python module to a new location with import update | 0 | 8 | 512 |
| [migrate_react_component.py](migrate_react_component.py) | Migrate a React component to a new feature-grouped folder. | 0 | 9 | 470 |
| [profile_streamlit_page.py](profile_streamlit_page.py) | Streamlit Performance Profiler | 4 | 9 | 633 |
| [release.py](release.py) | Unified release management CLI. | 0 | 6 | 369 |
| [run_vba_smoke_tests.py](run_vba_smoke_tests.py) | Run VBA smoke tests via Excel automation (macOS). | 0 | 2 | 155 |
| [safe_file_delete.py](safe_file_delete.py) | Safe file delete script with reference checking. | 0 | 5 | 355 |
| [safe_file_move.py](safe_file_move.py) | Safe file move script with automatic link updates. | 0 | 6 | 484 |
| [session.py](session.py) | Unified session management CLI. | 0 | 20 | 1260 |
| [sync_numbers.py](sync_numbers.py) | Scan codebase and sync stale numbers across documentation fi | 2 | 11 | 389 |
| [test_api_parity.py](test_api_parity.py) | API Parity Testing Script (V3 Preparation) | 2 | 10 | 444 |
| [test_import_3d_pipeline.py](test_import_3d_pipeline.py) | Import → Design → 3D Pipeline Test | 0 | 1 | 205 |
| [test_vba_adapter.py](test_vba_adapter.py) | Test ETABSAdapter with actual VBA ETABS export data. | 0 | 1 | 171 |
| [update_test_stats.py](update_test_stats.py) | Update Test Stats — Dynamic test count updater. | 0 | 5 | 211 |
| [validate_api_contracts.py](validate_api_contracts.py) | API Contract Validator. | 2 | 9 | 608 |
| [validate_imports.py](validate_imports.py) | Validate Python imports across the project after migration. | 0 | 6 | 306 |
| [validate_schema_snapshots.py](validate_schema_snapshots.py) | Schema Snapshot Validator. | 0 | 6 | 256 |
| [validate_session_state.py](validate_session_state.py) | Session State Validator (TASK-413) | 3 | 4 | 408 |

## Shell Script Files

- [agent_mistakes_report.sh](agent_mistakes_report.sh) — Agent Mistakes Report
- [agent_start.sh](agent_start.sh) — Unified Agent Start Script
- [ai_commit.sh](ai_commit.sh) — AI-friendly wrapper for safe commits and pushes
- [archive_old_files.sh](archive_old_files.sh) — Auto-archive files older than 90 days from docs/_active/
- [check_not_main.sh](check_not_main.sh)
- [check_root_file_count.sh](check_root_file_count.sh) — Check Root File Count
- [check_unfinished_merge.sh](check_unfinished_merge.sh) — Check for unfinished merge before allowing new commits
- [check_version_consistency.sh](check_version_consistency.sh) — check_version_consistency.sh - Verify version strings are consistent
- [check_wip_limits.sh](check_wip_limits.sh) — check_wip_limits.sh - Enforce WIP (Work In Progress) limits
- [ci_local.sh](ci_local.sh) — shellcheck source=/dev/null
- [collect_metrics.sh](collect_metrics.sh) — Metrics Collection Script
- [create_task_pr.sh](create_task_pr.sh) — Create a PR for completed task work
- [finish_task_pr.sh](finish_task_pr.sh) — Finish task work and create PR
- [generate_all_indexes.sh](generate_all_indexes.sh) — Generate index.json + index.md for all research-relevant folders
- [install_git_hooks.sh](install_git_hooks.sh) — Install versioned git hooks via core.hooksPath
- [launch_streamlit.sh](launch_streamlit.sh) — =============================================================================
- [pre_commit_check.sh](pre_commit_check.sh) — Pre-flight checks before committing
- [recover_git_state.sh](recover_git_state.sh) — Recover from common git workflow failure states
- [repo_health_check.sh](repo_health_check.sh)
- [safe_push.sh](safe_push.sh) — Safe push workflow for AI agents - PREVENTS ALL MERGE CONFLICTS
- [should_use_pr.sh](should_use_pr.sh) — Helper script: Should this change use a Pull Request?
- [validate_git_state.sh](validate_git_state.sh) — Git workflow validator - run before any git operation
- [watch_tests.sh](watch_tests.sh) — Watch Mode (Solution 5 - Dev Automation)

## Subfolders

| Folder | Files | Description |
|--------|-------|-------------|
| [git-hooks/](git-hooks/) | 2 |  |
| [hooks/](hooks/) | 1 |  |
