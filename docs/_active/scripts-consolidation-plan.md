# Scripts Consolidation Plan

**Date:** 2026-02-10
**Current state:** 163 scripts (110 .py + 53 .sh) → **Target: ~80 scripts**
**Estimated removal:** ~83 scripts (50% reduction)

---

## Executive Summary

The `scripts/` directory has grown organically across 50+ agent sessions. Many scripts were single-purpose, created for a specific task, and never cleaned up. The major problems:

1. **42 `check_*` scripts** — many do narrow, overlapping validation that could be consolidated
2. **3 install hook scripts** — 2 are deprecated
3. **3 index generators** — `generate_folder_index.py` is superseded by `generate_enhanced_index.py`
4. **2 cleanup_stale_branches** — duplicate .py/.sh
5. **3 migrate scripts** — `migrate_module.py` is the old version of `migrate_python_module.py`
6. **2 benchmark scripts** — overlapping API benchmarks
7. **Many one-off migration/fix scripts** that are no longer needed

---

## Group 1: CHECK Scripts (42 → 18)

### 1A. API Checkers (3 → 3 KEEP ALL — distinct purposes, all in pre-commit)

| Script | Lines | Purpose | Pre-commit? | Verdict |
|--------|-------|---------|-------------|---------|
| `check_api_doc_signatures.py` | 56 | `api.__all__` symbols in docs/reference/api.md | YES | **KEEP** |
| `check_api_docs_sync.py` | 70 | api.md ↔ api-stability.md symbol sync | YES | **KEEP** |
| `check_api_signatures.py` | ~250 | Streamlit pages use correct API signatures | YES | **KEEP** |

**Rationale:** Each checks a different contract. All three are in pre-commit. Keep separate.

### 1B. Doc Checkers (7 → 3) — CONSOLIDATE into `check_docs.py`

| Script | Lines | Purpose | Pre-commit? | Verdict |
|--------|-------|---------|-------------|---------|
| `check_doc_frontmatter.py` | ~200 | YAML front-matter validation | NO | **MERGE** → `check_docs.py --frontmatter` |
| `check_doc_metadata.py` | ~200 | Metadata headers (Type, Audience) | YES | **MERGE** → `check_docs.py --metadata` |
| `check_doc_similarity.py` | ~200 | Fuzzy-match titles to prevent dupes | NO | **ARCHIVE** — rarely used utility |
| `check_doc_versions.py` | 69 | Version drift (thin wrapper on bump_version.py) | YES | **KEEP** separate (CI-specific) |
| `check_docs_index.py` | 39 | docs/README.md heading structure | YES | **MERGE** → `check_docs.py --index` |
| `check_docs_index_links.py` | 66 | docs/README.md link resolution | YES | **MERGE** → `check_docs.py --index-links` |
| `check_duplicate_docs.py` | 97 | Duplicate filenames in docs/ | NO | **ARCHIVE** — low-frequency utility |

**Action:** Create `check_docs.py` with subcommands: `--metadata`, `--frontmatter`, `--index`, `--index-links`, `--all`. Archive `check_doc_similarity.py` and `check_duplicate_docs.py` (on-demand utilities, not CI).

### 1C. Folder Checkers (2 → 1) — OVERLAP with validate_folder_structure.py

| Script | Lines | Purpose | Pre-commit? | Verdict |
|--------|-------|---------|-------------|---------|
| `check_folder_readmes.py` | ~150 | Folders have README.md | NO | **ARCHIVE** — rarely enforced |
| `check_folder_structure.py` | ~250 | Python library structure validation | NO | **MERGE** into `validate_folder_structure.py` |

**Overlap:** `check_folder_structure.py` validates Python lib structure. `validate_folder_structure.py` (434 lines) validates governance rules. They complement each other but `check_folder_structure.py` should be absorbed into the larger validator. `check_folder_readmes.py` is a nice-to-have that's never in CI.

### 1D. Release Checkers (3 → 3 KEEP ALL — distinct, all in pre-commit)

| Script | Lines | Purpose | Pre-commit? | Verdict |
|--------|-------|---------|-------------|---------|
| `check_cli_reference.py` | 45 | CLI commands in docs | YES | **KEEP** |
| `check_pre_release_checklist.py` | 70 | Pre-release doc structure | YES | **KEEP** |
| `check_release_docs.py` | 81 | CHANGELOG ↔ releases.md sync | YES | **KEEP** |

### 1E. Architecture Checkers (3 → 2)

| Script | Lines | Purpose | Pre-commit? | Verdict |
|--------|-------|---------|-------------|---------|
| `check_architecture_boundaries.py` | 494 | 3-layer architecture linter | NO | **KEEP** — critical |
| `check_circular_imports.py` | 458 | Streamlit circular import detection | NO | **KEEP** — useful |
| `check_fragment_violations.py` | ~200 | Streamlit fragment API violations | YES | **ARCHIVE** — very specific to old Streamlit pattern, V3 is React |

### 1F. Issue Checkers (5 → 3)

| Script | Lines | Purpose | Pre-commit? | Verdict |
|--------|-------|---------|-------------|---------|
| `check_cost_optimizer_issues.py` | ~200 | Cost optimizer anti-patterns | YES | **KEEP** |
| `check_fastapi_issues.py` | 419 | FastAPI anti-patterns | NO | **KEEP** — V3 critical |
| `check_performance_issues.py` | 594 | Streamlit perf anti-patterns | YES | **ARCHIVE** — Streamlit-specific, V3 is React |
| `check_streamlit_issues.py` | 2204 | Comprehensive Streamlit scanner | YES | **KEEP** (until V3 migration complete) |
| `check_streamlit_imports.py` | ~150 | Streamlit import validation | NO | **ARCHIVE** — covered by `check_streamlit_issues.py` |

**Rationale:** `check_streamlit_imports.py` is a subset of what `check_streamlit_issues.py` does (which also checks imports). `check_performance_issues.py` is Streamlit-specific and will be irrelevant post-V3.

### 1G. Governance/Session Checkers (4 → 2)

| Script | Lines | Purpose | Pre-commit? | Verdict |
|--------|-------|---------|-------------|---------|
| `check_governance_compliance.py` | 430 | Folder governance spec compliance | NO | **KEEP** |
| `check_handoff_ready.py` | ~150 | Pre-handoff doc freshness | NO | **ARCHIVE** — agent workflow-specific |
| `check_repo_hygiene.py` | 41 | .DS_Store/.coverage artifacts | YES | **KEEP** (tiny, CI guard) |
| `check_session_docs.py` | ~100 | session brief/log consistency | YES | **KEEP** |

### 1H. Format Checkers (3 → 2)

| Script | Lines | Purpose | Pre-commit? | Verdict |
|--------|-------|---------|-------------|---------|
| `check_readme_quality.py` | ~200 | README quality indicators | NO | **ARCHIVE** — overlaps `check_folder_readmes.py` which is also archived |
| `check_tasks_format.py` | 157 | TASKS.md structure | YES | **KEEP** |
| `check_next_session_brief_length.py` | 28 | Brief length cap | YES | **KEEP** (trivial) |

### 1I. Code Quality (2 → 2 KEEP)

| Script | Lines | Purpose | Pre-commit? | Verdict |
|--------|-------|---------|-------------|---------|
| `check_type_annotations.py` | 538 | Missing type hints | YES | **KEEP** |
| `check_python_version.py` | ~200 | Python version consistency | YES | **KEEP** |

### 1J. Misc Check Scripts (4 → 3)

| Script | Lines | Purpose | Pre-commit? | Verdict |
|--------|-------|---------|-------------|---------|
| `check_redirect_stubs.py` | ~150 | Find/fix redirect stubs | NO | **ARCHIVE** — migration utility, one-time |
| `check_scripts_index.py` | 69 | scripts/index.json sync | YES | **KEEP** |
| `check_ui_duplication.py` | 616 | Streamlit code duplication | NO | **ARCHIVE** after V3 migration |
| `check_docker_config.py` | ~200 | Docker config validation | NO | **KEEP** |
| `check_links.py` | ~250 | Broken markdown links | YES | **KEEP** |

### 1K. Shell Check Scripts (5 → 5 KEEP ALL)

All are small, targeted, and serve distinct CI/hook purposes:
- `check_not_main.sh` (14 lines) — prevents commits to main
- `check_root_file_count.sh` (50 lines) — root file limit
- `check_unfinished_merge.sh` (29 lines) — pre-commit hook
- `check_version_consistency.sh` (65 lines) — version sync
- `check_wip_limits.sh` (76 lines) — WIP limits

---

## Group 2: VALIDATE Scripts (11 → 7)

| Script | Lines | Purpose | Verdict |
|--------|-------|---------|---------|
| `validate_api_contracts.py` | ~200 | FastAPI ↔ OpenAPI contract | **KEEP** — V3 critical |
| `validate_fastapi_schema.py` | ~350 | FastAPI ↔ structural_lib API | **MERGE** with `validate_api_contracts.py` (both validate FastAPI contracts) |
| `validate_folder_structure.py` | 434 | Governance folder rules | **KEEP** — absorb `check_folder_structure.py` |
| `validate_imports.py` | ~200 | Broken import detection | **KEEP** — critical for migrations |
| `validate_migration.py` | ~200 | IS 456 migration status | **ARCHIVE** — migration complete |
| `validate_schema_snapshots.py` | ~200 | Pydantic schema snapshots | **KEEP** — V3 critical |
| `validate_stub_exports.py` | ~200 | Backward-compat stub exports | **ARCHIVE** — migration complete |
| `validate_session_state.py` | 405 | Streamlit session_state audit | **ARCHIVE** after V3 |
| `validate_streamlit_page.py` | ~100 | Streamlit page pre-validation | **ARCHIVE** — covered by `comprehensive_validator.py` |
| `validate_trial_data.py` | 100 | Trial data JSON schema | **ARCHIVE** — research-specific one-off |
| `validate_git_state.sh` | ~100 | Git state validation | **KEEP** |

**Action:** Merge `validate_fastapi_schema.py` into `validate_api_contracts.py`. Archive 4 scripts that are migration-complete or Streamlit-specific.

---

## Group 3: GENERATE Scripts (9 → 5)

| Script | Lines | Purpose | Verdict |
|--------|-------|---------|---------|
| `generate_all_indexes.sh` | 50 | Shell wrapper calling generate_enhanced_index.py | **KEEP** — orchestrator |
| `generate_folder_index.py` | ~200 | Basic folder indexing | **ARCHIVE** — superseded by `generate_enhanced_index.py` |
| `generate_enhanced_index.py` | 745 | Enhanced folder indexing (Python/React/etc.) | **KEEP** — the canonical indexer |
| `generate_api_manifest.py` | 153 | API manifest for contract testing | **KEEP** — in pre-commit |
| `generate_api_routes.py` | 408 | FastAPI route stub generator | **ARCHIVE** — one-time scaffolding, already used |
| `generate_client_sdks.py` | 523 | TypeScript/Python SDK generator | **KEEP** — V3 critical |
| `generate_dashboard.sh` | ~100 | Governance metrics dashboard | **ARCHIVE** — agent-9 specific, rarely used |
| `generate_docs_index.py` | ~150 | docs-index.json generator | **KEEP** — distinct from folder index |
| `generate_streamlit_page.py` | 474 | Streamlit page scaffolder | **ARCHIVE** after V3 |

---

## Group 4: TEST Scripts (10 → 5)

| Script | Lines | Purpose | Verdict |
|--------|-------|---------|---------|
| `test_api_parity.py` | 441 | FastAPI ↔ library parity | **KEEP** — V3 critical |
| `test_import_3d_pipeline.py` | ~200 | Import→Design→3D integration | **KEEP** |
| `test_vba_adapter.py` | ~150 | VBA adapter tests | **KEEP** |
| `test_agent_automation.sh` | 136 | Agent automation integration test | **ARCHIVE** — meta-test tooling |
| `test_branch_operations.sh` | 454 | Git branch/worktree tests | **ARCHIVE** — agent-8 specific |
| `test_git_workflow.sh` | 1032 | Git workflow test suite | **ARCHIVE** — agent-8 specific |
| `test_merge_conflicts.sh` | 942 | Merge conflict test suite | **ARCHIVE** — agent-8 specific |
| `test_page.sh` | 102 | Streamlit page test runner | **ARCHIVE** after V3 |
| `test_setup.py` | 11 | Quick library install test | **KEEP** |
| `test_should_use_pr.sh` | ~100 | PR decision logic test | **ARCHIVE** — meta-test |

---

## Group 5: MIGRATE Scripts (3 → 2)

| Script | Lines | Purpose | Verdict |
|--------|-------|---------|---------|
| `migrate_module.py` | 420 | IS 456 module migration (original) | **ARCHIVE** — superseded |
| `migrate_python_module.py` | 410 | General Python module migration | **KEEP** — referenced in instructions |
| `migrate_react_component.py` | 387 | React component migration | **KEEP** — referenced in instructions |

**Confirmed:** `migrate_module.py` is the old IS-456-specific version. `migrate_python_module.py` is the generalized replacement.

---

## Group 6: GIT/CI Scripts (17 → 9)

### 6A. Core Git (5 → 2)

| Script | Lines | Purpose | Verdict |
|--------|-------|---------|---------|
| `ai_commit.sh` | 158 | THE one commit script | **KEEP** — the golden path |
| `safe_push.sh` | 408 | Full safe push workflow | **KEEP** — called by ai_commit.sh |
| `quick_push.sh` | 8 | Deprecated → just prints error | **ARCHIVE** (already deprecated) |
| `git_ops.sh` | ~200 | Git operations router | **ARCHIVE** — not used, agent convention is ai_commit.sh |
| `git_automation_health.sh` | ~200 | Validate git automation scripts | **ARCHIVE** — meta-script for agent-8 |

### 6B. CI (4 → 2)

| Script | Lines | Purpose | Verdict |
|--------|-------|---------|---------|
| `ci_local.sh` | 40 | Local CI runner | **KEEP** |
| `ci_monitor_daemon.sh` | ~300 | Background PR CI monitor | **ARCHIVE** — agent-8 specific |
| `pre_commit_check.sh` | 35 | Pre-flight whitespace/conflict check | **KEEP** |
| `pre-push-hook.sh` | 52 | Pre-push validation hook | **ARCHIVE** — superseded by `scripts/git-hooks/` |

### 6C. Install Hooks (3 → 1)

| Script | Lines | Purpose | Verdict |
|--------|-------|---------|---------|
| `install_enforcement_hook.sh` | 81 | DEPRECATED — says so in file | **ARCHIVE** |
| `install_git_hooks.sh` | 149 | Install versioned hooks via core.hooksPath | **KEEP** — the canonical installer |
| `install_hooks.sh` | 68 | Install hooks from scripts/hooks/ | **ARCHIVE** — `install_git_hooks.sh` is canonical |

### 6D. Git State (5 → 2)

| Script | Lines | Purpose | Verdict |
|--------|-------|---------|---------|
| `cleanup_stale_branches.py` | ~150 | Python branch cleanup | **KEEP** — more capable |
| `cleanup_stale_branches.sh` | 132 | Shell branch cleanup | **ARCHIVE** — duplicate of .py version |
| `recover_git_state.sh` | ~200 | Git recovery automation | **KEEP** |
| `verify_git_fix.sh` | 118 | Test safe_push whitespace fix | **ARCHIVE** — one-time verification |
| `validate_git_state.sh` | ~100 | Git state validation | **KEEP** (already counted in validate group) |

---

## Group 7: ARCHIVE Scripts (4 → 1)

| Script | Lines | Purpose | Verdict |
|--------|-------|---------|---------|
| `archive_deprecated_docs.py` | ~200 | Archive deprecated docs | **ARCHIVE** — migration-era one-off |
| `archive_old_files.sh` | ~150 | Auto-archive old docs/_active files | **KEEP** — monthly CI cron |
| `archive_old_sessions.sh` | ~150 | Archive session docs | **ARCHIVE** — overlaps with archive_old_files.sh |
| `batch_archive.py` | ~200 | Batch archive by pattern | **ARCHIVE** — utility, `safe_file_move.py` + shell is enough |

---

## Group 8: BENCHMARK Scripts (2 → 1)

| Script | Lines | Purpose | Verdict |
|--------|-------|---------|---------|
| `benchmark_api.py` | 455 | FastAPI endpoint benchmarks (JSON output) | **KEEP** — CI-focused |
| `benchmark_api_latency.py` | 431 | Library API latency (V3 prep) | **MERGE** into `benchmark_api.py` |

**Overlap:** Both benchmark API functions. `benchmark_api.py` tests FastAPI endpoints, `benchmark_api_latency.py` tests direct library calls. Merge into one script with `--mode fastapi|direct|all`.

---

## Group 9: Remaining One-Off / Migration Scripts → ARCHIVE

These scripts were created for specific tasks and are no longer actively needed:

| Script | Lines | Purpose | Verdict |
|--------|-------|---------|---------|
| `batch_migrate_modules.py` | 517 | Batch migration runner | **ARCHIVE** — migration complete |
| `create_reexport_stub.py` | ~100 | Create re-export stubs | **ARCHIVE** — migration utility |
| `fix_services_relative_imports.py` | 104 | Fix services/ imports | **ARCHIVE** — one-time fix |
| `pre_migration_check.py` | ~200 | Pre-migration validation | **ARCHIVE** — migration complete |
| `update_is456_init.py` | ~200 | Update IS456 __init__.py | **ARCHIVE** — migration utility |
| `update_redirect_refs.py` | ~200 | Update redirect references | **ARCHIVE** — migration utility |
| `autonomous_fixer.py` | 462 | Auto-fix Streamlit issues | **ARCHIVE** — Streamlit-era |
| `auto_fix_page.py` | 146 | Auto-fix single page | **ARCHIVE** — Streamlit-era |
| `analyze_doc_redundancy.py` | ~200 | Doc redundancy analysis | **ARCHIVE** — one-time analysis |
| `analyze_navigation_data.py` | ~200 | Navigation study data | **ARCHIVE** — research one-off |
| `analyze_release_cadence.py` | 430 | Release cadence analysis | **ARCHIVE** — research one-off |
| `consolidate_docs.py` | 592 | Doc consolidation engine | **ARCHIVE** — one-time consolidation |
| `predict_velocity.py` | ~200 | Velocity prediction | **ARCHIVE** — research one-off |
| `find_orphan_files.py` | ~200 | Find orphan files | **ARCHIVE** — one-time utility |
| `enhance_readme.py` | ~200 | Auto-enhance README files | **ARCHIVE** — one-time utility |
| `add_license_headers.py` | ~200 | Add SPDX license headers | **ARCHIVE** — one-time utility |
| `add_future_annotations.py` | 93 | Add `from __future__` | **ARCHIVE** — one-time utility |
| `rename_folder_safe.py` | ~200 | Safe folder rename | **ARCHIVE** — covered by `safe_file_move.py` |
| `lint_docs_git_examples.sh` | 131 | Lint git examples in docs | **ARCHIVE** — niche |
| `pylint_streamlit.sh` | ~50 | Pylint for Streamlit | **ARCHIVE** — V3 is React |
| `streamlit_preflight.sh` | ~50 | Streamlit preflight checks | **ARCHIVE** — V3 is React |
| `measure_agent_navigation.sh` | ~100 | Navigation measurement | **ARCHIVE** — research one-off |
| `risk_cache.sh` | ~50 | Risk caching | **ARCHIVE** |
| `quick_check.sh` | 24 | Quick validation runner | **ARCHIVE** — unclear what it does |
| `worktree_manager.sh` | 454 | Git worktree management | **ARCHIVE** — agent-8 specific |
| `pr_async_merge.sh` | ~100 | Async PR merge | **ARCHIVE** — agent-8 specific |
| `create_task_pr.sh` | 94 | Create task PR branch | **KEEP** |
| `finish_task_pr.sh` | ~100 | Finish task PR | **KEEP** |
| `governance_session.sh` | ~100 | Governance session runner | **ARCHIVE** — agent-9 specific |
| `weekly_governance_check.sh` | 141 | Weekly governance | **ARCHIVE** — agent-9 specific |

---

## Group 10: Comprehensive/Meta Validators

| Script | Lines | Purpose | Verdict |
|--------|-------|---------|---------|
| `comprehensive_validator.py` | 526 | Streamlit validator (4-level) | **ARCHIVE** after V3 — overlaps `check_streamlit_issues.py` |
| `profile_streamlit_page.py` | 630 | Streamlit page profiler | **ARCHIVE** after V3 |

---

## Broken Import Risk Assessment

Scripts importing `structural_lib.*` that may have broken paths after Phase 1/2 migration:

| Script | Import | Risk |
|--------|--------|------|
| `batch_migrate_modules.py` | References `structural_lib.services.api` | **HIGH** — services/ path may not exist; ARCHIVE anyway |
| `benchmark_api_latency.py` | `structural_lib.services.api` | **HIGH** — needs path update |
| `check_folder_structure.py` | `structural_lib.core.CodeRegistry`, `structural_lib.codes.is456` | **OK** — these paths exist |
| `discover_api_signatures.py` | `structural_lib.services.api` | **HIGH** — needs path update to `structural_lib.api` |
| `generate_api_routes.py` | `structural_lib.services.api` | **HIGH** — ARCHIVE anyway |
| `migrate_module.py` | `structural_lib.codes.is456.*` | **OK** — but ARCHIVE |
| `pre_migration_check.py` | `structural_lib.flexure`, `structural_lib.core` | **MEDIUM** — ARCHIVE |
| `test_api_parity.py` | Dynamic imports via inspect | **LOW** |
| `test_import_3d_pipeline.py` | Dynamic | **LOW** |
| `validate_fastapi_schema.py` | `structural_lib.services.api` | **HIGH** — needs path update |
| `validate_migration.py` | Various old paths | **ARCHIVE** |
| `validate_stub_exports.py` | Stub paths | **ARCHIVE** |

**Immediate fix needed:** Update `structural_lib.services.api` → `structural_lib.api` in:
- `benchmark_api_latency.py`
- `discover_api_signatures.py` (critical — used in daily workflow)

---

## Final Kept Script Set (~80 scripts)

### Core Workflow (8)
- `ai_commit.sh`, `safe_push.sh`, `agent_start.sh`, `agent_setup.sh`, `agent_preflight.sh`, `copilot_setup.sh`, `should_use_pr.sh`, `ci_local.sh`

### Git Operations (6)
- `install_git_hooks.sh`, `recover_git_state.sh`, `validate_git_state.sh`, `cleanup_stale_branches.py`, `create_task_pr.sh`, `finish_task_pr.sh`

### Pre-commit Checks (20 - all in .pre-commit-config.yaml)
- `check_unfinished_merge.sh`, `check_repo_hygiene.py`, `check_doc_versions.py`, `check_python_version.py`, `check_tasks_format.py`, `check_docs_index.py` (→ merge into `check_docs.py`), `check_release_docs.py`, `check_session_docs.py`, `check_api_docs_sync.py`, `check_pre_release_checklist.py`, `check_api_doc_signatures.py`, `generate_api_manifest.py`, `check_next_session_brief_length.py`, `check_cli_reference.py`, `check_scripts_index.py`, `check_docs_index_links.py` (→ merge into `check_docs.py`), `check_links.py`, `check_cost_optimizer_issues.py`, `check_streamlit_issues.py`, `check_fragment_violations.py` (→ archive after V3), `check_api_signatures.py`, `check_type_annotations.py`, `check_performance_issues.py` (→ archive after V3), `check_doc_metadata.py` (→ merge into `check_docs.py`), `pre_commit_check.sh`

### Shell Guards (5)
- `check_not_main.sh`, `check_root_file_count.sh`, `check_version_consistency.sh`, `check_wip_limits.sh`

### Architecture/Quality (6)
- `check_architecture_boundaries.py`, `check_circular_imports.py`, `check_governance_compliance.py`, `check_docker_config.py`, `check_fastapi_issues.py`, `validate_folder_structure.py`

### Migration Tools (2)
- `migrate_python_module.py`, `migrate_react_component.py`

### Code Generation (5)
- `generate_all_indexes.sh`, `generate_enhanced_index.py`, `generate_api_manifest.py`, `generate_client_sdks.py`, `generate_docs_index.py`

### V3/FastAPI (5)
- `validate_api_contracts.py`, `validate_schema_snapshots.py`, `validate_imports.py`, `benchmark_api.py`, `test_api_parity.py`

### Testing (4)
- `test_import_3d_pipeline.py`, `test_vba_adapter.py`, `test_setup.py`, `external_cli_test.py`

### Utilities (12)
- `safe_file_move.py`, `safe_file_delete.py`, `safe_push.sh`, `discover_api_signatures.py`, `bump_version.py`, `release.py`, `verify_release.py`, `create_doc.py`, `create_test_scaffold.py`, `collect_diagnostics.py`, `dxf_render.py`, `find_automation.py`

### Session Management (4)
- `start_session.py`, `end_session.py`, `update_handoff.py`, `update_test_stats.py`

### Archive/Maintenance (1)
- `archive_old_files.sh`

### Audit (3)
- `audit_error_handling.py`, `audit_input_validation.py`, `audit_readiness_report.py`

### VBA (2)
- `run_vba_smoke_tests.py`, `vba_validator.py`, `lint_vba.py`

---

## Implementation Priority

### Phase 1: Quick Wins (archive clearly dead/deprecated) — ~40 scripts
1. Archive `quick_push.sh` (already deprecated)
2. Archive `install_enforcement_hook.sh` (already deprecated)
3. Archive `install_hooks.sh` (superseded)
4. Archive `migrate_module.py` (superseded by `migrate_python_module.py`)
5. Archive `generate_folder_index.py` (superseded by `generate_enhanced_index.py`)
6. Archive `cleanup_stale_branches.sh` (duplicate of .py version)
7. Archive all migration one-offs: `batch_migrate_modules.py`, `create_reexport_stub.py`, `fix_services_relative_imports.py`, `pre_migration_check.py`, `update_is456_init.py`, `update_redirect_refs.py`, `validate_migration.py`, `validate_stub_exports.py`
8. Archive research one-offs: `analyze_doc_redundancy.py`, `analyze_navigation_data.py`, `analyze_release_cadence.py`, `predict_velocity.py`, `measure_agent_navigation.sh`
9. Archive agent-specific: `git_ops.sh`, `git_automation_health.sh`, `ci_monitor_daemon.sh`, `worktree_manager.sh`, `pr_async_merge.sh`, `governance_session.sh`, `weekly_governance_check.sh`, `generate_dashboard.sh`, `test_agent_automation.sh`, `test_branch_operations.sh`, `test_git_workflow.sh`, `test_merge_conflicts.sh`, `test_should_use_pr.sh`
10. Archive Streamlit one-offs: `auto_fix_page.py`, `autonomous_fixer.py`, `pylint_streamlit.sh`, `streamlit_preflight.sh`, `test_page.sh`
11. Archive doc utilities: `consolidate_docs.py`, `enhance_readme.py`, `find_orphan_files.py`, `archive_deprecated_docs.py`, `archive_old_sessions.sh`, `batch_archive.py`
12. Archive misc one-offs: `add_license_headers.py`, `add_future_annotations.py`, `rename_folder_safe.py`, `risk_cache.sh`, `quick_check.sh`, `lint_docs_git_examples.sh`, `check_redirect_stubs.py`, `verify_git_fix.sh`

### Phase 2: Consolidations — ~5 merges
1. Create `check_docs.py` from: `check_doc_frontmatter.py`, `check_doc_metadata.py`, `check_docs_index.py`, `check_docs_index_links.py`
2. Merge `validate_fastapi_schema.py` into `validate_api_contracts.py`
3. Merge `benchmark_api_latency.py` into `benchmark_api.py`
4. Absorb `check_folder_structure.py` into `validate_folder_structure.py`

### Phase 3: Fix Broken Imports
1. Fix `discover_api_signatures.py`: `structural_lib.services.api` → `structural_lib.api`
2. Fix `benchmark_api_latency.py`: same fix (if not archived)

### Phase 4: Post-V3 Archival — when React migration complete
- `check_streamlit_issues.py`, `check_fragment_violations.py`, `check_performance_issues.py`, `check_ui_duplication.py`, `comprehensive_validator.py`, `profile_streamlit_page.py`, `validate_session_state.py`, `validate_streamlit_page.py`, `generate_streamlit_page.py`, `check_streamlit_imports.py`

---

## Summary

| Category | Current | After Phase 1 | After Phase 2 | After Phase 4 |
|----------|---------|---------------|---------------|---------------|
| Total scripts | 163 | ~110 | ~105 | ~85 |
| check_* | 42 | 35 | 31 | 25 |
| validate_* | 11 | 7 | 6 | 4 |
| generate_* | 9 | 5 | 5 | 4 |
| test_* | 10 | 4 | 4 | 4 |
| Git/CI | 17 | 9 | 9 | 9 |
| One-offs | ~30 | 0 | 0 | 0 |
