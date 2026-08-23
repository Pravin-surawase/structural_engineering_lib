---
owner: Main Agent
status: active
last_updated: 2026-08-23
doc_type: guide
complexity: intermediate
tags: [cleanup, migration, governance]
---

# Folder Cleanup Workflow

Repository cleanup is a classified migration, not an age-based sweep. Keep
inspection read-only until every candidate has an owner, disposition, exact
source/destination, and retention reason.

## 1. Verify the lane

```bash
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
./scripts/python_runtime.sh --diagnose
```

Work only from a clean, source-bound task branch/worktree. Preserve dirty,
detached, foreign, or uncertain lanes; cleanup permission does not authorize
branch or worktree deletion.

## 2. Classify exact files

For each candidate record:

| Field | Required decision |
|---|---|
| Source | Exact regular repository file |
| Disposition | KEEP, MOVE, or DELETE |
| Owner | Current responsible surface |
| Reason | Duplicate, replaced, misplaced, or obsolete |
| Destination | Exact new path for MOVE |
| References | Updateable, preserved historical, or unresolved |
| Retention | Evidence/history requirement |

Modification time is supporting metadata only. Do not classify a file as
obsolete solely because it is old.

## 3. Preview single operations

```bash
./scripts/python_runtime.sh scripts/safe_file_move.py old/path.md new/path.md --dry-run --json
./scripts/python_runtime.sh scripts/safe_file_delete.py obsolete/path.md --dry-run --json
```

Resolve every `unresolved` maintained reference before proceeding. Existing
destinations, directories, symlinks, outside paths, and missing validators are
hard failures.

## 4. Preflight the complete batch

Put independent accepted moves into one JSON plan and run:

```bash
./scripts/python_runtime.sh scripts/batch_migrate_runner.py cleanup-plan.json --dry-run --json
```

The preflight must cover every operation before the first write. Split chained
moves into separately reviewed batches. Do not add force, no-backup,
continue-on-error, or partial-rollback behavior.

Deletion remains a separately reviewed single-file action because every
maintained reference must already be removed and each deletion creates its own
content-hashed recovery manifest.

## 5. Execute frozen content once

```bash
./scripts/python_runtime.sh scripts/batch_migrate_runner.py cleanup-plan.json --json
./scripts/python_runtime.sh scripts/safe_file_delete.py accepted-obsolete.md --json
```

The batch runner compares actual paths/hashes with the preview and restores the
whole batch on any failure. A delete restores the exact source bytes if
post-delete validation fails.

## 6. Verify the result

```bash
git diff --summary
git diff
./scripts/python_runtime.sh scripts/check_links.py
./run.sh context validate
./run.sh control validate
./run.sh check --quick
```

Run language-specific focused checks for Python or React migrations. After all
intended cleanup packets integrate, run the repository full gate once.

## Held actions

- Automatic archival by file age is retired.
- Manual `mv`, `git mv`, `rm`, and `git rm` bypass the safety contract.
- Branch/worktree cleanup, history rewriting, release publication, and
  professional approval require separate authority.
- Historical evidence retains original path text unless its own correction is
  explicitly in scope.
