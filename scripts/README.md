# Scripts

> Development, validation, discovery, release-preparation, and maintenance tools.
> Git/GitHub lifecycle wrappers were retired on 2026-08-09; Codex owns that
> workflow directly.

## Preferred entry points

```bash
./run.sh session start
./run.sh task brief "describe the task"
./run.sh check --quick
./run.sh check
./run.sh test
./run.sh test --fastapi
./run.sh test --react
./run.sh frontend check
./run.sh find "topic"
./run.sh find --api function_name
./run.sh control validate
./run.sh context validate
./run.sh context summary automation
./run.sh audit
./run.sh health
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
| Branch disposition | `classify_branch_disposition.py` | Inspection-only worktree/ref/patch facts plus supplied remote and PR evidence |
| Task intake | `run.sh task brief` | Read-only lane, base, worktree, route, and safe-start summary |
| Python runtime | `python_runtime.sh --diagnose` | Prove linked-worktree import identity with `source_bound=true` |
| Discovery | `find_automation.py` | Find an existing project automation |
| Control registry | `run.sh control` | Validate/query canonical operations, permissions, targets, and compatibility projection |
| API discovery | `discover_api_signatures.py` | Exact Python API signatures |
| Files | `safe_file_move.py` | Move files after a dry run and link scan |
| Files | `safe_file_delete.py` | Delete files after a dry run and reference scan |
| Live context | `run.sh context` | Validate canonical routing and summarize current files without generated folder indexes |
| IS 456 quality | `check_function_quality.py --module <name>` | Source-relative static function-contract scan; not a numerical benchmark |
| Sessions | `session.py` | Bounded session lifecycle and usage checkpoints |
| CI | `diagnose_ci.py` | Diagnose CI failures without managing Git |
| Release | `release.py` | Authorized release preparation and validation |
| Frontend runtime | `node_runtime.py` | Select `.nvmrc` Node/npm for root-stable commands |

## Operating rules

- Run from the repository root and use `./scripts/python_runtime.sh`, never bare `python`.
- Inspect `--help` before invoking an unfamiliar tool.
- Use `--dry-run` before supported destructive file operations.
- Use `./run.sh context show <area>` for routing and
  `./run.sh context summary <area-or-folder>` for a bounded live inventory.
  Both are read-only.
- Prefer targeted checks while editing and one full gate at closeout.
- Preserve unrelated changes in a dirty worktree.
- Stop on unclear Git state; do not automate recovery or rewrite history.
- Release, merge, issue closure, and branch deletion require explicit user
  confirmation.

Operation metadata is canonical in [control-plane.json](control-plane.json).
[automation-map.json](automation-map.json) is generated compatibility data;
refresh it only with `./run.sh control export-legacy --write`.
[context-manifest.json](context-manifest.json) owns repository-area routing;
validate it with `./run.sh context validate`. Top-level script coverage is
derived directly from the live scripts directory and the control registry.
