# Archived scripts

Files here are inactive historical reference. They are excluded from the active
control-plane inventory and must not be called by CI, `run.sh`, agents, hooks, or
current documentation.

Scripts are archived when their outcome is owned by a maintained replacement,
their workflow has ended, or no supported caller remains. Archival preserves the
old implementation for audit and recovery without leaving another executable
path in the live scripts surface.

## MAINT-012D control-plane retirement

The following compatibility paths were archived after their callers and
outcome-changing contracts were mapped to canonical owners:

- Git state wrappers: `validate_git_state.sh`, `check_unfinished_merge.sh`, and
  `check_not_main.sh` → `scripts/git_state.py`.
- Generated-index bridges: `generate_all_indexes.sh`, `generate_docs_index.py`,
  and `generate_enhanced_index.py` → `./run.sh context`.
- Duplicate scanners: `check_openapi_drift.py` → `check_openapi_snapshot.py`;
  `governance_health_score.py` and `repo_health_check.sh` → `project_health.py`;
  `check_wip_limits.sh` → `check_tasks_format.py` plus task-intake Git/PR
  inspection; `fix_deleted_file_links_legacy.py` → `check_links.py --fix`.
- Unsupported writers: `collect_metrics.sh` and `export_paper_data.py` have no
  maintained caller; current usage, health, and evolution evidence have explicit
  canonical owners.
- Dormant non-Git hook prototype: `hooks/` → `prompt_router.py` and
  `tool_permissions.py`.

The readiness, error-handling, input-validation, function-quality, and
public-route safety scanners were deliberately retained because they validate
different safety contracts.

## MAINT-0130 safe-file retirement

`archive_old_files.sh` was archived after its root check and age-only
classification were shown to be unsuitable for repository cleanup. Current
cleanup requires explicit ownership/retention classification followed by a
complete dry-run batch plan; `evolve.py` reports age candidates but never moves
them automatically.

## Reactivation rule

Do not run a file from this directory. If a future approved task needs an old
capability, reassess it against the current architecture, then preview the move:

```bash
./scripts/python_runtime.sh scripts/safe_file_move.py <archive-path> <active-path> --dry-run
```

After the reviewed live move, register one canonical operation and prove the
focused contract before use.
