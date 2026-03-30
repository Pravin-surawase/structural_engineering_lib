# Scripts

> **Purpose:** Automation scripts for development, CI/CD, and maintenance tasks

**Type:** Python Package
**Last Updated:** 2026-03-30
**Files:** 90

## Config Files

- [automation-map.json](automation-map.json)

## Documentation Files

| File | Title | Description | Lines |
|------|-------|-------------|-------|
| [README.md](README.md) | Scripts | > **Purpose:** Automation scripts for development, CI/CD, an | 165 |

## Python Files

| File | Description | Classes | Functions | Lines |
|------|-------------|---------|-----------|-------|
| [agent_context.py](agent_context.py) | Agent Context Loader — gives each agent its tailored startup | 0 | 18 | 590 |
| [agent_feedback.py](agent_feedback.py) | Agent feedback collection and analysis. | 0 | 6 | 380 |
| [audit_error_handling.py](audit_error_handling.py) | Audit error handling compliance across structural_lib module | 2 | 3 | 286 |
| [audit_input_validation.py](audit_input_validation.py) | Audit Input Validation Coverage for structural_lib. | 2 | 5 | 393 |
| [audit_readiness_report.py](audit_readiness_report.py) | Audit Readiness Report Generator | 2 | 11 | 773 |
| [batch_migrate_runner.py](batch_migrate_runner.py) | Batch migration runner with per-operation rollback logs. | 1 | 2 | 439 |
| [benchmark_api.py](benchmark_api.py) | API Performance Benchmark Script. | 4 | 9 | 799 |
| [bump_version.py](bump_version.py) | Version Bump Script — Single Source of Truth | 0 | 3 | 392 |
| [check_all.py](check_all.py) | Unified check orchestrator — runs all validation scripts in  | 3 | 1 | 664 |
| [check_api.py](check_api.py) | Unified API validation — signatures, docs, and sync checks. | 1 | 4 | 379 |
| [check_api_compat.py](check_api_compat.py) | Check API backward compatibility. | 0 | 3 | 152 |
| [check_architecture_boundaries.py](check_architecture_boundaries.py) | Architecture Boundary Linter. | 3 | 9 | 518 |
| [check_bootstrap_freshness.py](check_bootstrap_freshness.py) | Check if bootstrap docs are stale compared to actual codebas | 0 | 4 | 262 |
| [check_circular_imports.py](check_circular_imports.py) | Circular Import Detector for Streamlit Application | 5 | 1 | 464 |
| [check_cli_reference.py](check_cli_reference.py) | Ensure CLI reference includes required commands. | 0 | 1 | 48 |
| [check_doc_versions.py](check_doc_versions.py) | Doc Version Drift Check — Validate no stale *library* versio | 0 | 2 | 72 |
| [check_docker_config.py](check_docker_config.py) | Docker Configuration Validator. | 0 | 6 | 282 |
| [check_docs.py](check_docs.py) | Unified documentation checker — consolidates 4 doc validatio | 0 | 6 | 653 |
| [check_fastapi_issues.py](check_fastapi_issues.py) | FastAPI Issues AST Scanner. | 3 | 4 | 422 |
| [check_governance.py](check_governance.py) | Unified governance checker — folder structure + compliance v | 2 | 18 | 847 |
| [check_instruction_drift.py](check_instruction_drift.py) | Check for content drift between .github/instructions/ and .c | 0 | 2 | 210 |
| [check_links.py](check_links.py) | Check and fix broken internal links in markdown files. | 0 | 2 | 327 |
| [check_next_session_brief_length.py](check_next_session_brief_length.py) | Ensure next-session-brief.md stays concise. | 0 | 1 | 31 |
| [check_openapi_snapshot.py](check_openapi_snapshot.py) | Check OpenAPI spec against baseline snapshot to detect API d | 0 | 1 | 207 |
| [check_python_version.py](check_python_version.py) | Python Version Consistency Checker | 0 | 5 | 215 |
| [check_repo_hygiene.py](check_repo_hygiene.py) | Fail if tracked hygiene artifacts exist in the repository. | 0 | 1 | 44 |
| [check_scripts_index.py](check_scripts_index.py) | Ensure scripts/index.json and automation-map.json match the  | 0 | 1 | 164 |
| [check_tasks_format.py](check_tasks_format.py) | Validate docs/TASKS.md structure and WIP rules. | 0 | 1 | 160 |
| [check_type_annotations.py](check_type_annotations.py) | Type Annotation Checker for Streamlit Application | 4 | 1 | 542 |
| [cleanup_stale_branches.py](cleanup_stale_branches.py) | Cleanup stale remote branches. | 0 | 7 | 187 |
| [collect_diagnostics.py](collect_diagnostics.py) | Collect a compact diagnostics bundle for debugging and suppo | 0 | 2 | 122 |
| [create_doc.py](create_doc.py) | Create a new documentation file with proper metadata header. | 0 | 5 | 261 |
| [create_test_scaffold.py](create_test_scaffold.py) | Test Scaffold Generator (Solution 2) | 0 | 3 | 236 |
| [discover_api_signatures.py](discover_api_signatures.py) | Discover and display structural_lib API function signatures. | 2 | 6 | 376 |
| [dxf_render.py](dxf_render.py) | Render DXF drawings to PNG or PDF using ezdxf + matplotlib. | 0 | 2 | 128 |
| [evolve.py](evolve.py) | Self-evolution engine — orchestrates project health, feedbac | 0 | 12 | 543 |
| [external_cli_test.py](external_cli_test.py) | External CLI smoke test (S-007). | 1 | 1 | 396 |
| [find_automation.py](find_automation.py) | Find the right automation script for a task. | 0 | 6 | 174 |
| [fix_broken_links.py](fix_broken_links.py) | Fix broken internal links in markdown files. | 0 | 6 | 251 |
| [generate_api_manifest.py](generate_api_manifest.py) | Generate or validate the public API manifest for structural_ | 0 | 1 | 157 |
| [generate_client_sdks.py](generate_client_sdks.py) | Generate client SDKs from FastAPI OpenAPI specification. | 0 | 6 | 526 |
| [generate_docs_index.py](generate_docs_index.py) | Generate machine-readable JSON index of documentation. | 0 | 7 | 245 |
| [generate_enhanced_index.py](generate_enhanced_index.py) | Generate enhanced index.json + index.md for ANY folder type. | 0 | 10 | 800 |
| [generate_error_docs.py](generate_error_docs.py) | Generate docs/reference/error-codes.md from core/errors.py. | 0 | 4 | 139 |
| [governance_health_score.py](governance_health_score.py) | Governance Health Score - TASK-289 | 3 | 1 | 515 |
| [migrate_python_module.py](migrate_python_module.py) | Migrate a Python module to a new location with import update | 0 | 8 | 511 |
| [migrate_react_component.py](migrate_react_component.py) | Migrate a React component to a new feature-grouped folder. | 0 | 9 | 470 |
| [preflight.py](preflight.py) | Pre-flight check — catch common mistakes BEFORE they happen. | 0 | 9 | 204 |
| [project_health.py](project_health.py) | Unified project health scanner with auto-fix capability. | 3 | 9 | 741 |
| [release.py](release.py) | Unified release management CLI. | 0 | 6 | 369 |
| [safe_file_delete.py](safe_file_delete.py) | Safe file delete script with reference checking. | 0 | 5 | 355 |
| [safe_file_move.py](safe_file_move.py) | Safe file move script with automatic link updates. | 0 | 6 | 484 |
| [session.py](session.py) | Unified session management CLI. | 0 | 20 | 1401 |
| [sync_numbers.py](sync_numbers.py) | Scan codebase and sync stale numbers across documentation fi | 2 | 11 | 389 |
| [test_api_parity.py](test_api_parity.py) | API Parity Testing Script (V3 Preparation) | 2 | 10 | 444 |
| [test_changed.py](test_changed.py) | Smart test runner — run only tests related to changed files. | 0 | 3 | 207 |
| [test_import_3d_pipeline.py](test_import_3d_pipeline.py) | Import → Design → 3D Pipeline Test | 0 | 1 | 203 |
| [test_import_pipeline.py](test_import_pipeline.py) | End-to-end test of all import paths. | 0 | 20 | 249 |
| [test_sample_endpoint.py](test_sample_endpoint.py) | Quick test of the sample data endpoint. | 0 | 0 | 50 |
| [update_test_stats.py](update_test_stats.py) | Update Test Stats — Dynamic test count updater. | 0 | 5 | 211 |
| [validate_api_contracts.py](validate_api_contracts.py) | API Contract Validator. | 2 | 9 | 608 |
| [validate_imports.py](validate_imports.py) | Validate Python imports across the project after migration. | 0 | 6 | 305 |
| [validate_schema_snapshots.py](validate_schema_snapshots.py) | Schema Snapshot Validator. | 0 | 6 | 256 |
| [validate_script_refs.py](validate_script_refs.py) | Validate that active scripts don't reference archived script | 0 | 4 | 167 |

## Shell Script Files

- [agent_brief.sh](agent_brief.sh) — ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
- [launch_stack.sh](launch_stack.sh) — launch_stack.sh — Full-stack development launcher for structural_engineering_lib
- [pre_commit_check.sh](pre_commit_check.sh) — Pre-flight checks before committing
- [recover_git_state.sh](recover_git_state.sh) — Recover from common git workflow failure states
- [repo_health_check.sh](repo_health_check.sh)
- [safe_push.sh](safe_push.sh) — Safe push workflow for AI agents - PREVENTS ALL MERGE CONFLICTS
- [should_use_pr.sh](should_use_pr.sh) — Deprecation notice — use ai_commit.sh --pr-check instead
- [validate_git_state.sh](validate_git_state.sh) — Git workflow validator - run before any git operation
- [watch_tests.sh](watch_tests.sh) — Watch Mode (Solution 5 - Dev Automation)

## Subfolders

| Folder | Files | Description |
|--------|-------|-------------|
| [git-hooks/](git-hooks/) | 3 |  |
