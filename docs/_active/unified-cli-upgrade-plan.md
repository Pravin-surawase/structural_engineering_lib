# Unified CLI Upgrade Plan

**Type:** Architecture
**Audience:** All Agents
**Status:** Draft
**Importance:** High
**Created:** 2026-03-24
**Last Updated:** 2026-03-24

---

## Problem

Agents face **85 active scripts** and waste time discovering, learning, and calling the right ones. Even experienced agents frequently:

- Call archived scripts (46 stale references found in Session 93)
- Duplicate functionality that already exists in hooks
- Run individual check scripts instead of the consolidated versions
- Skip validation because they don't know which scripts to run

The consolidation from 163 → 85 helped, but the **interface remained the same**: a flat directory of 85 scripts with no clear hierarchy.

---

## Vision: 5 Entry Points

An AI agent should only need to know **5 commands** for 95% of their work:

```bash
./run.sh check              # "Is everything healthy?"
./run.sh commit "message"   # "Save my work"
./run.sh pr TASK-XXX "desc" # "Ship this for review"
./run.sh session start      # "Begin work"
./run.sh session end        # "Wrap up work"
```

Each entry point orchestrates the right sub-scripts internally. Agents never need to know about `check_governance.py`, `check_api.py`, etc. — they just run `./run.sh check` and get a unified report.

---

## Architecture

### `./run.sh` — Single CLI Entry Point

```
./run.sh <command> [subcommand] [options]

Commands:
  check     Run validation checks (all, or by category)
  commit    Stage, commit, and push safely
  pr        Create/finish pull requests
  session   Start/end agent sessions
  find      Discover scripts and API signatures
  release   Version bumps and release management
```

Under the hood, `run.sh` dispatches to the existing scripts — no rewrite needed. It's a **thin orchestration layer** that calls the same proven scripts.

### Command: `./run.sh check`

```
./run.sh check                    # Run ALL checks (governance + code + docs + architecture)
./run.sh check --quick            # Fast subset (links, imports, types — <30s)
./run.sh check --category api     # API checks only
./run.sh check --category docs    # Doc checks only
./run.sh check --category arch    # Architecture checks only
./run.sh check --fix              # Auto-fix what's fixable
./run.sh check --json             # Machine-readable output
```

**Internally calls:**

| Category | Scripts Called |
|----------|--------------|
| `api` | `check_api.py --all`, `validate_api_contracts.py`, `generate_api_manifest.py --check` |
| `docs` | `check_docs.py --all`, `check_links.py`, `check_doc_versions.py` |
| `arch` | `check_architecture_boundaries.py`, `check_circular_imports.py`, `validate_imports.py` |
| `governance` | `check_governance.py --full`, `check_repo_hygiene.py`, `check_scripts_index.py` |
| `code` | `check_type_annotations.py`, `check_python_version.py` |
| `streamlit` | `check_streamlit.py --all-pages` |
| `fastapi` | `check_fastapi_issues.py`, `check_docker_config.py`, `check_openapi_snapshot.py` |
| `git` | `validate_git_state.sh`, `check_unfinished_merge.sh` |
| `stale` | `validate_script_refs.py`, `check_instruction_drift.py`, `check_bootstrap_freshness.py` |

**Unified output:**
```
━━━ Check Report ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  API:          ✅ 3/3 passed
  Docs:         ⚠️  2/3 passed (1 warning)
  Architecture: ✅ 3/3 passed
  Governance:   ✅ 3/3 passed
  Code:         ✅ 2/2 passed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total: 16/17 passed, 1 warning
  Auto-fixable: 1 (run with --fix)
```

### Command: `./run.sh commit "message"`

Same as `ai_commit.sh` — just a cleaner interface. Internally calls `ai_commit.sh`.

### Command: `./run.sh pr`

```
./run.sh pr create TASK-XXX "description"    # → create_task_pr.sh
./run.sh pr finish TASK-XXX "description"    # → finish_task_pr.sh
./run.sh pr status                           # → gh pr view
```

### Command: `./run.sh session`

```
./run.sh session start          # → agent_start.sh --quick
./run.sh session end            # → session.py end
./run.sh session summary        # → session.py summary --write
./run.sh session sync           # → session.py sync --fix
```

### Command: `./run.sh find`

```
./run.sh find "commit code"              # → find_automation.py
./run.sh find --api design_beam_is456    # → discover_api_signatures.py
./run.sh find --list                     # → find_automation.py --list
```

---

## Archived Scripts Without Replacements

These 50 archived scripts have no active replacement. Most are correctly archived (one-off utilities, research scripts, migration-era tools). **None need restoration:**

### One-Off Utilities (Correctly Archived — task is done)
- `add_future_annotations.py` — Added `from __future__` to all files (done)
- `add_license_headers.py` — Added SPDX headers (done)
- `fix_services_relative_imports.py` — Fixed services/ imports (done)
- `update_is456_init.py` — Updated IS456 __init__.py (done)
- `update_redirect_refs.py` — Updated redirect references (done)
- `create_reexport_stub.py` — Created re-export stubs (done)
- `rename_folder_safe.py` — Covered by `safe_file_move.py`
- `find_orphan_files.py` — One-time analysis
- `enhance_readme.py` — One-time enhancement
- `batch_archive.py` — One-time batch archive
- `batch_migrate_modules.py` — Migration complete
- `consolidate_docs.py` — Doc consolidation complete
- `archive_deprecated_docs.py` — Used once
- `archive_deprecated_scripts.py` — Used once
- `archive_old_sessions.sh` — Covered by `archive_old_files.sh`

### Research/Analysis (Correctly Archived — results captured)
- `analyze_doc_redundancy.py` — Research output in docs/
- `analyze_navigation_data.py` — Research output captured
- `analyze_release_cadence.py` — Research output captured
- `predict_velocity.py` — Research one-off
- `measure_agent_navigation.sh` — Research measurement

### Migration-Era Validators (Correctly Archived — migration done)
- `validate_migration.py` — IS 456 migration complete
- `validate_stub_exports.py` — Stubs verified
- `validate_trial_data.py` — Trial data validated
- `validate_streamlit_page.py` — Covered by `check_streamlit.py`
- `pre_migration_check.py` — Migration complete
- `migrate_module.py` — Superseded by `migrate_python_module.py`
- `comprehensive_validator.py` — Covered by `check_streamlit.py`

### Agent-8 Git Automation (Correctly Archived — superseded)
- `git_ops.sh` — Replaced by `ai_commit.sh` + `safe_push.sh`
- `git_automation_health.sh` — Replaced by `validate_git_state.sh`
- `ci_monitor_daemon.sh` — PR polling built into `finish_task_pr.sh`
- `pr_async_merge.sh` — PR workflow in `finish_task_pr.sh`
- `worktree_manager.sh` — Not used in current workflow
- `quick_push.sh` — Replaced by `safe_push.sh`
- `quick_check.sh` — Replaced by direct pytest
- `safe_push_v2.sh` — Replaced by current `safe_push.sh`
- `should_use_pr_old.sh` — Replaced by `should_use_pr.sh`
- `install_enforcement_hook.sh` — Replaced by `install_git_hooks.sh`
- `install_hooks.sh` — Replaced by `install_git_hooks.sh`
- `pre-push-hook.sh` — Replaced by `scripts/git-hooks/`
- `verify_git_fix.sh` — One-time verification

### Testing Scripts (Correctly Archived — tested what's needed)
- `test_agent_automation.sh` — Meta-test, not needed
- `test_branch_operations.sh` — Agent-8 specific
- `test_git_workflow.sh` — Agent-8 specific
- `test_merge_conflicts.sh` — Agent-8 specific
- `test_page.sh` — Streamlit-era
- `test_setup.py` — Simple install test
- `test_should_use_pr.sh` — Meta-test

### Streamlit-Specific (Correctly Archived — V3 is React)
- `check_streamlit_imports.py` — Covered by `check_streamlit.py`
- `auto_fix_page.py` — Streamlit auto-fixer
- `autonomous_fixer.py` — Streamlit auto-fixer
- `pylint_streamlit.sh` — V3 is React
- `streamlit_preflight.sh` — V3 is React

### Other (Correctly Archived)
- `check_folder_readmes.py` — Nice-to-have, not enforced
- `check_folder_structure.py` — Absorbed into `check_governance.py`
- `check_duplicate_docs.py` — Low-frequency utility
- `check_handoff_ready.py` — Inlined into `session.py`
- `check_readme_quality.py` — Overlaps with other checks
- `check_redirect_stubs.py` — Migration utility
- `copilot_setup.sh` — Absorbed into `agent_start.sh`
- `agent_preflight.sh` — Absorbed into `agent_start.sh`
- `agent_setup.sh` — Absorbed into `agent_start.sh`
- `end_session.py` — Absorbed into `session.py`
- `start_session.py` — Absorbed into `session.py`
- `generate_api_routes.py` — One-time scaffolding
- `generate_dashboard.sh` — Agent-9 specific
- `governance_session.sh` — Agent-9 specific
- `weekly_governance_check.sh` — Agent-9 specific
- `risk_cache.sh` — Niche utility
- `lint_docs_git_examples.sh` — Niche linter
- `vba_validator.py` — Covered by `lint_vba.py`

---

## Implementation Plan

### Phase 1: Create `./run.sh` (Quick Win)
**Effort:** ~200 lines of shell
**Impact:** Agents go from remembering 85 scripts to 5 commands

1. Create `run.sh` at repo root
2. Implement `check`, `commit`, `pr`, `session`, `find` subcommands
3. Each subcommand delegates to existing scripts
4. Unified output formatting with pass/fail/warn counts
5. Update CLAUDE.md, AGENTS.md, copilot-instructions.md to show `./run.sh` as primary interface

### Phase 2: Smart Check Orchestrator
**Effort:** ~300 lines of Python
**Impact:** `./run.sh check` runs 30+ checks in parallel with unified report

1. Create `scripts/check_all.py` — Python orchestrator for all check_*.py scripts
2. Parallel execution of independent checks
3. Category grouping with summary output
4. `--fix` flag propagated to all fixable checks
5. JSON output for CI integration

### Phase 3: Archive Remaining Candidates
**Effort:** ~1 hour
**Impact:** 85 → ~70 active scripts

Scripts that can be archived now (V3 migration makes them obsolete):
- `check_performance_issues.py` (Streamlit-specific)
- `check_ui_duplication.py` (Streamlit-specific)
- `generate_streamlit_page.py` (V3 is React)
- `profile_streamlit_page.py` (Streamlit profiler)
- `validate_session_state.py` (Streamlit session state)
- `check_cost_optimizer_issues.py` (Streamlit-specific patterns)

### Phase 4: Update Documentation
1. Update `scripts/README.md` with `./run.sh` as primary interface
2. Update `automation-map.json` to map tasks → `./run.sh` subcommands
3. Update all agent instruction files
4. Regenerate `scripts/index.json` and `scripts/index.md`

---

## Migration Path

Existing scripts remain unchanged — `run.sh` is purely additive. Agents can use either interface:

```bash
# Old way (still works)
.venv/bin/python scripts/check_governance.py --structure

# New way (preferred)
./run.sh check --category governance
```

No breaking changes. Gradual migration through documentation updates.

---

## Success Metrics

| Metric | Before | After |
|--------|--------|-------|
| Commands agents need to memorize | 85 | 5 |
| Time to find the right script | 30-60s (grep/find) | 0s (run.sh subcommand) |
| Stale reference risk | High (93 archive + flat dir) | Low (stable entry points) |
| Validation coverage per session | Partial (agents pick random checks) | Full (`run.sh check` runs all) |
