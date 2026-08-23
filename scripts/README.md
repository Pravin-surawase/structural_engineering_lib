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
./run.sh verification validate
./run.sh verification plan
./run.sh audit
./run.sh health
./run.sh session usage --summary
./run.sh session end
```

A `session usage --checkpoint closeout` record is fail-closed unless it includes
all canonical phase timings, exact candidate heads, and the required retry/run
counters documented in `docs/guidelines/ai-token-efficiency.md`.

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
| Git diagnosis | `git_state.py` | Sole typed, read-only local Git state authority |
| Branch disposition | `classify_branch_disposition.py` | Inspection-only worktree/ref/patch facts plus supplied remote and PR evidence |
| Task intake | `run.sh task brief` | Read-only lane, base, worktree, route, and safe-start summary |
| Python runtime | `python_runtime.sh --diagnose` | Prove linked-worktree import identity with `source_bound=true` |
| Discovery | `find_automation.py` | Find an existing project automation |
| Control registry | `run.sh control` | Validate/query canonical operations, permissions, targets, and compatibility projection |
| API discovery | `discover_api_signatures.py` | Exact Python API signatures |
| Files | `safe_file_move.py` | Transactionally move one regular file after classified-reference preview |
| Files | `safe_file_delete.py` | Delete one unreferenced regular file with a content-hashed backup |
| Files | `batch_migrate_runner.py` | Preflight a complete plan, compare exact live paths, and roll back the whole batch |
| Live context | `run.sh context` | Validate canonical routing and summarize current files without generated folder indexes |
| Verification impact | `run.sh verification` | Plan explicit change domains and inspect command/runtime/input-bound PASS evidence |
| Link integrity | `check_links.py` | Check maintained links and images; repair only explicit or unique targets |
| Project health | `project_health.py` | Unified read-only scan; persist only with explicit `--write` or `--fix` |
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
- Quick/full checks reuse only an exact PASS receipt from the shared Git common
  directory. `./run.sh check --no-reuse` forces fresh execution; failed,
  malformed, runtime-different, command-different, or input-different evidence
  never skips a check.
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

The readiness, error-handling, input-validation, function-quality, and public-route
safety scanners intentionally remain separate because they answer different
outcome-changing questions. Archived scripts are inactive reference material and
must not be called from CI, `run.sh`, agent routing, or the control registry.
[verification-manifest.json](verification-manifest.json) is the single local and
hosted path-to-domain contract. The same rules select work and define the input
bytes in its PASS fingerprint; new or unclassified paths select every domain.
