---
owner: Main Agent
status: active
last_updated: 2026-08-09
doc_type: reference
complexity: intermediate
tags: [automation, scripts, codex]
---

# Automation Catalog

The exhaustive machine-generated script inventory is
[scripts/index.json](../../scripts/index.json), with a readable companion at
[scripts/index.md](../../scripts/index.md). Task-to-script discovery lives in
[automation-map.json](../../scripts/automation-map.json) and is queried with:

```bash
./run.sh find "task description"
./run.sh find --list
```

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
| Safe file move | `.venv/bin/python scripts/safe_file_move.py old new --dry-run` |
| Safe file delete | `.venv/bin/python scripts/safe_file_delete.py file --dry-run` |
| Regenerate indexes | `./run.sh generate indexes` |

## Git/GitHub is not repository automation

Commit, push, PR creation/update, merge, and Git recovery wrappers were retired
on 2026-08-09. Codex owns ordinary scoped Git operations and connected GitHub PR
work. See the
[canonical workflow](../git-automation/git-workflow-single-source.md).

Standard pre-commit validation may run, but the repository must not install a
custom `core.hooksPath` or reintroduce lifecycle wrappers. The read-only guard is:

```bash
.venv/bin/python scripts/check_codex_git_workflow.py
```

## Maintenance rule

Before updating or archiving a script, consult its ledger row in the audit,
verify active callers with `rg`, run its focused tests, and regenerate the
scripts indexes. Historical references may remain in archives, but active
instructions and runtime callers must not invoke retired scripts.
