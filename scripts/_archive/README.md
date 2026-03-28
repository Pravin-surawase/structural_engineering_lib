# scripts/_archive/

Archived scripts — **no longer actively maintained**, kept for historical reference.

**Total: ~99 scripts** across 8 categories. These were moved here as the project evolved from V2 → V3.

## Why scripts are archived

- Superseded by a newer/better script (e.g., replaced by `run.sh` orchestration)
- Specific to a completed migration or feature (V2→V3 helpers, Streamlit→React migration)
- Experimental scripts never promoted to production
- Functionality absorbed into another tool

## Contents by category

### Documentation (24)
`add_license_headers.py` · `analyze_doc_redundancy.py` · `archive_deprecated_docs.py` · `check_api_doc_signatures.py` · `check_api_docs_sync.py` · `check_doc_frontmatter.py` · `check_doc_metadata.py` · `check_doc_similarity.py` · `check_docs_index.py` · `check_docs_index_links.py` · `check_duplicate_docs.py` · `check_folder_readmes.py` · `check_readme_quality.py` · `check_redirect_stubs.py` · `check_release_docs.py` · `check_session_docs.py` · `consolidate_docs.py` · `enhance_readme.py` · `find_orphan_files.py` · `fix_broken_links.py` · `generate_folder_index.py` · `generate_dashboard.sh` · `lint_docs_git_examples.sh` · `update_redirect_refs.py`

### Git / CI (16)
`cleanup_stale_branches.sh` · `ci_monitor_daemon.sh` · `git_automation_health.sh` · `git_ops.sh` · `install_enforcement_hook.sh` · `install_hooks.sh` · `pr_async_merge.sh` · `pre-push-hook.sh` · `quick_push.sh` · `risk_cache.sh` · `safe_push_v2.sh` · `should_use_pr_old.sh` · `test_branch_operations.sh` · `test_git_workflow.sh` · `verify_git_fix.sh` · `worktree_manager.sh`

### Code quality (19)
`auto_fix_page.py` · `autonomous_fixer.py` · `check_api_signatures.py` · `check_cost_optimizer_issues.py` · `check_folder_structure.py` · `check_fragment_violations.py` · `check_governance_compliance.py` · `check_links.py` · `check_performance_issues.py` · `check_ui_duplication.py` · `comprehensive_validator.py` · `create_reexport_stub.py` · `fix_services_relative_imports.py` · `pylint_streamlit.sh` · `validate_fastapi_schema.py` · `validate_folder_structure.py` · `validate_stub_exports.py` · `validate_trial_data.py` · `vba_validator.py`

### Session management (8)
`check_handoff_ready.py` · `check_pre_release_checklist.py` · `end_session.py` · `governance_session.sh` · `start_session.py` · `update_handoff.py` · `validate_session_state.py` · `weekly_governance_check.sh`

### Streamlit (8)
`check_streamlit_imports.py` · `check_streamlit_issues.py` · `generate_streamlit_page.py` · `launch_streamlit.sh` · `profile_streamlit_page.py` · `streamlit_preflight.sh` · `test_page.sh` · `validate_streamlit_page.py`

### API / Migration (7)
`batch_migrate_modules.py` · `benchmark_api_latency.py` · `generate_api_routes.py` · `migrate_module.py` · `pre_migration_check.py` · `update_is456_init.py` · `validate_migration.py`

### Testing (4)
`test_agent_automation.sh` · `test_merge_conflicts.sh` · `test_setup.py` · `test_should_use_pr.sh`

### Other (13)
`add_future_annotations.py` · `agent_preflight.sh` · `agent_setup.sh` · `analyze_navigation_data.py` · `analyze_release_cadence.py` · `archive_deprecated_scripts.py` · `archive_old_sessions.sh` · `batch_archive.py` · `copilot_setup.sh` · `measure_agent_navigation.sh` · `predict_velocity.py` · `quick_check.sh` · `rename_folder_safe.py` · `verify_release.py`

## Reactivating a script

1. Move it back: `.venv/bin/python scripts/safe_file_move.py scripts/_archive/<name>.py scripts/<name>.py`
2. Test it: `.venv/bin/python scripts/<name>.py --help`
3. Add to `scripts/index.json`
4. Update `docs/reference/automation-catalog.md`

## Do NOT run archived scripts in CI or agent workflows

Archived scripts are reference only. They may have outdated imports or stale assumptions about project structure.
