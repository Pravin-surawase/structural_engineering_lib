---
owner: Main Agent
status: active
last_updated: 2026-08-23
doc_type: reference
complexity: intermediate
tags: [automation, scripts, codex]
---

# Automation Catalog

Operation discovery, commands, aliases, permissions, and exhaustive top-level
script coverage live in the canonical
[control-plane.json](../../scripts/control-plane.json) and are queried with:

```bash
./run.sh find "task description"
./run.sh find --list
./run.sh control validate
./run.sh context show automation
./run.sh context summary scripts
```

[automation-map.json](../../scripts/automation-map.json) is a deterministic
temporary compatibility projection. Do not edit it directly; refresh it with
`./run.sh control export-legacy --write` after changing the canonical registry.

The detailed one-by-one maintenance assessment is
[Automation Scripts Audit — 2026-08-09](../audit/automation-scripts-audit-2026-08-09.md).

## Primary entry points

| Need | Command |
|------|---------|
| Session start | `./run.sh session start` |
| Quick validation | `./run.sh check --quick` |
| Full validation | `./run.sh check` |
| Tests | `./run.sh test` |
| API contract | `.venv/bin/python scripts/check_api.py --all` |
| Project audit | `./run.sh audit` |
| Health scan | `./run.sh health` |
| API discovery | `./run.sh find --api function_name` |
| Control registry | `./run.sh control validate` |
| Safe file move | `.venv/bin/python scripts/safe_file_move.py old new --dry-run` |
| Safe file delete | `.venv/bin/python scripts/safe_file_delete.py file --dry-run` |
| Live repository context | `./run.sh context show automation` |
| Bounded live file summary | `./run.sh context summary scripts` |

## Git/GitHub is not repository automation

Commit, push, PR creation/update, merge, and Git recovery wrappers were retired
on 2026-08-09. Codex owns ordinary scoped Git operations and connected GitHub PR
work. See the
[canonical workflow](../git-automation/git-workflow-single-source.md).

Standard pre-commit validation may run, but the repository must not install a
custom `core.hooksPath` or reintroduce lifecycle wrappers. The read-only guard is:

```bash
./scripts/python_runtime.sh scripts/check_codex_git_workflow.py
```

## Maintenance rule

Before updating or archiving a script, inspect its canonical operation entry,
consult its ledger row in the audit, verify active callers with `rg`, run its
focused tests, refresh the compatibility projection when operation metadata
changes, and run control/context validation. Historical references may remain
in archives, but active instructions and runtime callers must not invoke
retired scripts.
