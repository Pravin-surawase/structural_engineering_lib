# Scripts

> **Purpose:** Automation scripts for development, CI/CD, and maintenance tasks

**Type:** Python Package
**Last Updated:** 2026-04-07
**Files:** 114

## Config Files

- [automation-map.json](automation-map.json)

## Documentation Files

| File | Title | Description | Lines |
|------|-------|-------------|-------|
| [README.md](README.md) | Scripts | > **Purpose:** Automation scripts for development, CI/CD, an | 165 |

## Python Files

| File | Description | Classes | Functions | Lines |
|------|-------------|---------|-----------|-------|
| [_tmp_add_groups.py](_tmp_add_groups.py) | Temporary script to add group fields to automation-map.json. | 0 | 0 | 168 |
| [agent_compliance_checker.py](agent_compliance_checker.py) | Agent compliance checker — verify agents followed their .age | 0 | 12 | 514 |
| [agent_context.py](agent_context.py) | Agent Context Loader — gives each agent its tailored startup | 0 | 18 | 579 |
| [agent_drift_detector.py](agent_drift_detector.py) | Agent drift detector — detect when agents deviate from presc | 0 | 9 | 591 |
| [agent_evolve_instructions.py](agent_evolve_instructions.py) | Agent instruction evolver — self-improving agent customizati | 0 | 12 | 540 |
| [agent_feedback.py](agent_feedback.py) | Agent feedback collection and analysis. | 0 | 6 | 423 |
| [agent_scorer.py](agent_scorer.py) | Agent scorer — score agents on 11 performance dimensions. | 0 | 9 | 548 |
| [agent_session_collector.py](agent_session_collector.py) | Agent session collector — gather all session artifacts for s | 0 | 9 | 320 |
| [agent_trends.py](agent_trends.py) | Agent trends — time series analysis and degradation detectio | 0 | 7 | 375 |
| [audit_error_handling.py](audit_error_handling.py) | Audit error handling compliance across structural_lib module | 2 | 3 | 286 |
| [audit_input_validation.py](audit_input_validation.py) | Audit Input Validation Coverage for structural_lib. | 2 | 5 | 393 |
| [audit_permissions.py](audit_permissions.py) | Permission audit report for all agents. | 3 | 2 | 394 |
| [audit_readiness_report.py](audit_readiness_report.py) | Audit Readiness Report Generator | 2 | 11 | 827 |
| [batch_migrate_runner.py](batch_migrate_runner.py) | Batch migration runner with per-operation rollback logs. | 1 | 2 | 442 |
| [benchmark_api.py](benchmark_api.py) | API Performance Benchmark Script. | 4 | 9 | 837 |
| [bump_version.py](bump_version.py) | Version Bump Script — Single Source of Truth | 0 | 3 | 432 |
| [check_all.py](check_all.py) | Unified check orchestrator — runs all validation scripts in  | 3 | 1 | 714 |
| [check_api.py](check_api.py) | Unified API validation — signatures, docs, and sync checks. | 1 | 4 | 442 |
| [check_api_compat.py](check_api_compat.py) | Check API backward compatibility. | 0 | 3 | 152 |
| [check_architecture_boundaries.py](check_architecture_boundaries.py) | Architecture Boundary Linter. | 3 | 9 | 521 |
| [check_bootstrap_freshness.py](check_bootstrap_freshness.py) | Check if bootstrap docs are stale compared to actual codebas | 0 | 4 | 290 |
| [check_circular_imports.py](check_circular_imports.py) | Circular Import Detector for Streamlit Application | 5 | 1 | 464 |
| [check_clause_coverage.py](check_clause_coverage.py) | IS 456 clause coverage gap detection. | 0 | 8 | 486 |
| [check_cli_reference.py](check_cli_reference.py) | Ensure CLI reference includes required commands. | 0 | 1 | 48 |
| [check_doc_versions.py](check_doc_versions.py) | Doc Version Drift Check — Validate no stale *library* versio | 0 | 2 | 72 |
| [check_docker_config.py](check_docker_config.py) | Docker Configuration Validator. | 0 | 6 | 295 |
| [check_docs.py](check_docs.py) | Unified documentation checker — consolidates 4 doc validatio | 0 | 6 | 653 |
| [check_fastapi_issues.py](check_fastapi_issues.py) | FastAPI Issues AST Scanner. | 3 | 4 | 450 |
| [check_function_quality.py](check_function_quality.py) | 12-point quality checklist for IS 456 functions. | 3 | 6 | 668 |
| [check_git_script_budget.py](check_git_script_budget.py) | Check that git automation scripts stay within line budget (T | 0 | 1 | 63 |
| [check_governance.py](check_governance.py) | Unified governance checker — folder structure + compliance v | 2 | 18 | 1026 |
| [check_instruction_drift.py](check_instruction_drift.py) | Check for content drift between .github/instructions/ and .c | 0 | 2 | 219 |
| [check_links.py](check_links.py) | Check and fix broken internal links in markdown files. | 0 | 2 | 351 |
| [check_new_element_completeness.py](check_new_element_completeness.py) | Check structural element completeness across all 7 layers. | 0 | 14 | 622 |
| [check_next_session_brief_length.py](check_next_session_brief_length.py) | Ensure next-session-brief.md stays concise. | 0 | 1 | 31 |
| [check_openapi_drift.py](check_openapi_drift.py) | Check OpenAPI spec for drift against baseline. | 0 | 5 | 193 |
| [check_openapi_snapshot.py](check_openapi_snapshot.py) | Check OpenAPI spec against baseline snapshot to detect API d | 0 | 1 | 231 |
| [check_python_version.py](check_python_version.py) | Python Version Consistency Checker | 0 | 5 | 216 |
| [check_repo_hygiene.py](check_repo_hygiene.py) | Fail if tracked hygiene artifacts exist in the repository. | 0 | 1 | 44 |
| [check_scripts_index.py](check_scripts_index.py) | Ensure scripts/index.json and automation-map.json match the  | 0 | 1 | 180 |
| [check_tasks_format.py](check_tasks_format.py) | Validate docs/TASKS.md structure and WIP rules. | 0 | 1 | 161 |
| [check_type_annotations.py](check_type_annotations.py) | Type Annotation Checker for Streamlit Application | 4 | 1 | 543 |
| [cleanup_stale_branches.py](cleanup_stale_branches.py) | Cleanup stale remote branches. | 0 | 7 | 187 |
| [collect_diagnostics.py](collect_diagnostics.py) | Collect a compact diagnostics bundle for debugging and suppo | 0 | 2 | 123 |
| [config_precedence.py](config_precedence.py) | Configuration precedence auditing for instruction files. | 2 | 10 | 562 |
| [create_doc.py](create_doc.py) | Create a new documentation file with proper metadata header. | 0 | 5 | 260 |
| [create_test_scaffold.py](create_test_scaffold.py) | Test Scaffold Generator (Solution 2) | 0 | 3 | 238 |
| [diagnose_ci.py](diagnose_ci.py) | CI failure diagnosis — check, reproduce, and fix CI failures | 0 | 13 | 339 |
| [discover_api_signatures.py](discover_api_signatures.py) | Discover and display structural_lib API function signatures. | 2 | 6 | 391 |
| [dxf_render.py](dxf_render.py) | Render DXF drawings to PNG or PDF using ezdxf + matplotlib. | 0 | 2 | 141 |
| [evolve.py](evolve.py) | Self-evolution engine — orchestrates project health, feedbac | 0 | 12 | 567 |
| [export_paper_data.py](export_paper_data.py) | Export agent performance data for academic paper. | 0 | 8 | 388 |
| [external_cli_test.py](external_cli_test.py) | External CLI smoke test (S-007). | 1 | 1 | 385 |
| [find_automation.py](find_automation.py) | Find the right automation script for a task. | 0 | 9 | 208 |
| [fix_broken_links.py](fix_broken_links.py) | Fix broken internal links in markdown files. | 0 | 6 | 268 |
| [generate_api_manifest.py](generate_api_manifest.py) | Generate or validate the public API manifest for structural_ | 0 | 1 | 159 |
| [generate_client_sdks.py](generate_client_sdks.py) | Generate client SDKs from FastAPI OpenAPI specification. | 0 | 6 | 531 |
| [generate_docs_index.py](generate_docs_index.py) | Generate machine-readable JSON index of documentation. | 0 | 7 | 246 |
| [generate_enhanced_index.py](generate_enhanced_index.py) | Generate enhanced index.json + index.md for ANY folder type. | 0 | 10 | 816 |
| [generate_error_docs.py](generate_error_docs.py) | Generate docs/reference/error-codes.md from core/errors.py. | 0 | 4 | 139 |
| [governance_health_score.py](governance_health_score.py) | Governance Health Score - TASK-289 | 3 | 1 | 515 |
| [migrate_python_module.py](migrate_python_module.py) | Migrate a Python module to a new location with import update | 0 | 8 | 517 |
| [migrate_react_component.py](migrate_react_component.py) | Migrate a React component to a new feature-grouped folder. | 0 | 9 | 478 |
| [parity_dashboard.py](parity_dashboard.py) | Parity Dashboard — coverage/parity across IS 456, API, endpo | 0 | 6 | 479 |
| [pipeline_state.py](pipeline_state.py) | Pipeline state tracking for multi-step agent workflows. | 2 | 17 | 868 |
| [preflight.py](preflight.py) | Pre-flight check — catch common mistakes BEFORE they happen. | 0 | 9 | 200 |
| [project_health.py](project_health.py) | Unified project health scanner with auto-fix capability. | 3 | 9 | 864 |
| [prompt_router.py](prompt_router.py) | Prompt router — routes natural language queries to the best  | 1 | 3 | 492 |
| [release.py](release.py) | Unified release management CLI. | 0 | 7 | 919 |
| [safe_file_delete.py](safe_file_delete.py) | Safe file delete script with reference checking. | 0 | 5 | 355 |
| [safe_file_move.py](safe_file_move.py) | Safe file move script with automatic link updates. | 0 | 6 | 505 |
| [session.py](session.py) | Unified session management CLI. | 0 | 20 | 2035 |
| [session_store.py](session_store.py) | JSON-based session state persistence for AI agent sessions. | 1 | 14 | 372 |
| [skill_tiers.py](skill_tiers.py) | Skill tier classification and management for AI agents. | 1 | 8 | 516 |
| [sync_numbers.py](sync_numbers.py) | Scan codebase and sync stale numbers across documentation fi | 2 | 11 | 479 |
| [test_api_parity.py](test_api_parity.py) | API Parity Testing Script (V3 Preparation) | 2 | 10 | 457 |
| [test_changed.py](test_changed.py) | Smart test runner — run only tests related to changed files. | 0 | 3 | 216 |
| [test_cli_smoke.py](test_cli_smoke.py) | CLI Smoke Tests — validate all key scripts work correctly. | 0 | 3 | 294 |
| [test_import_3d_pipeline.py](test_import_3d_pipeline.py) | Import → Design → 3D Pipeline Test | 0 | 1 | 211 |
| [test_import_pipeline.py](test_import_pipeline.py) | End-to-end test of all import paths. | 0 | 20 | 391 |
| [test_sample_endpoint.py](test_sample_endpoint.py) | Quick test of the sample data endpoint. | 0 | 0 | 55 |
| [tool_permissions.py](tool_permissions.py) | Tool permission enforcement for agent operations. | 1 | 4 | 346 |
| [tool_registry.py](tool_registry.py) | Unified tool registry — connects agents, skills, scripts, an | 1 | 13 | 535 |
| [update_test_stats.py](update_test_stats.py) | Update Test Stats — Dynamic test count updater. | 0 | 5 | 211 |
| [validate_api_contracts.py](validate_api_contracts.py) | API Contract Validator. | 2 | 9 | 620 |
| [validate_imports.py](validate_imports.py) | Validate Python imports across the project after migration. | 0 | 6 | 372 |
| [validate_schema_snapshots.py](validate_schema_snapshots.py) | Schema Snapshot Validator. | 0 | 6 | 257 |
| [validate_script_refs.py](validate_script_refs.py) | Validate that active scripts don't reference archived script | 0 | 4 | 169 |

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
| [hooks/](hooks/) 📦 | 5 |  |
