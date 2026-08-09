# Scripts

> Development, validation, discovery, release-preparation, and maintenance tools.
> Git/GitHub lifecycle wrappers were retired on 2026-08-09; Codex owns that
> workflow directly.

## Preferred entry points

```bash
./run.sh session start
./run.sh check --quick
./run.sh check
./run.sh test
./run.sh find "topic"
./run.sh find --api function_name
./run.sh audit
./run.sh health
./run.sh generate indexes
./run.sh session usage --summary
./run.sh session end
```

`run.sh` is a thin dispatcher for project validation and discovery. It does not
stage, commit, push, create PRs, merge, or recover Git state.

## Codex-native Git/GitHub boundary

Codex must inspect the branch, worktree, and diff; stage only intended paths;
create a conventional commit; push without rewriting history; and create or
update the PR through the connected GitHub integration. The canonical contract
is [git-workflow-single-source.md](../docs/git-automation/git-workflow-single-source.md).

Standard pre-commit validation may run during a Codex commit. Repository-owned
hook enforcement and scripts that automate the Git lifecycle are prohibited.

## Important tools

| Area | Tool | Purpose |
|------|------|---------|
| Validation | `check_all.py` | Quick and full validation orchestrator |
| API contract | `check_api.py` | Validate React call sites against FastAPI OpenAPI |
| Docs | `check_docs.py` | Metadata and documentation checks |
| Governance | `check_governance.py` | Folder and policy validation |
| Git diagnosis | `validate_git_state.sh` | Read-only Git state report |
| Discovery | `find_automation.py` | Find an existing project automation |
| API discovery | `discover_api_signatures.py` | Exact Python API signatures |
| Files | `safe_file_move.py` | Move files after a dry run and link scan |
| Files | `safe_file_delete.py` | Delete files after a dry run and reference scan |
| Indexes | `generate_enhanced_index.py` | Regenerate folder indexes |
| Sessions | `session.py` | Bounded session lifecycle and usage checkpoints |
| CI | `diagnose_ci.py` | Diagnose CI failures without managing Git |
| Release | `release.py` | Authorized release preparation and validation |

## Operating rules

- Run from the repository root and use `./scripts/python_runtime.sh`, never bare `python`.
- Inspect `--help` before invoking an unfamiliar tool.
- Use `--dry-run` before supported destructive file operations.
- Prefer targeted checks while editing and one full gate at closeout.
- Preserve unrelated changes in a dirty worktree.
- Stop on unclear Git state; do not automate recovery or rewrite history.
- Release, merge, issue closure, and branch deletion require explicit user
  confirmation.

The generated inventories [index.json](index.json) and [index.md](index.md) are
the exhaustive script catalog. Regenerate them after adding, removing, or
renaming scripts.
