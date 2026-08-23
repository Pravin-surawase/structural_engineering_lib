# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-23
- Focus: Replace split file-operation safety with one fail-closed transactional system.
- Git receipt: docs/verification/maint-0130-git-handoff-receipt.json | sha256:4ba9dd73d694e8b3606336222de5eb06116b73051873180da23627161dc5fa47 | HOLD
- Git identity: codex/maint-0130-safe-file-foundation@242ba386925d29766b1467810044e276ebbceb64 | upstream=origin/main@242ba386925d29766b1467810044e276ebbceb64 | base=origin/main@242ba386925d29766b1467810044e276ebbceb64 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | `MAINT-0130` replaces the unsafe file-operation split with one classified, fail-closed, transactional system |
| **Next** | Freeze and prove the exact candidate locally and in hosted checks; only after merge may the separately classified cleanup plan begin |
| **Why** | Move/delete discovery, mutation, validation, backup, and batch rollback previously disagreed, allowing false success and incomplete recovery |
| **Held** | Bulk cleanup, automatic archival, unclassified file movement, branch/worktree deletion, product behavior, release, and professional approval |

## Exact MAINT-0130 state

- Branch: `codex/maint-0130-safe-file-foundation`, created from freshly fetched
  `origin/main` commit `242ba386925d29766b1467810044e276ebbceb64`.
- `scripts/_lib/safe_file_ops.py` owns regular-file/repository path checks,
  reference classification, exact snapshots, link-validator protocol, hashes,
  and content-addressed delete backups.
- Move/delete commands default to explicit dry-run registry entries; directories,
  symlinks, outside paths, existing destinations, missing validators,
  unresolved maintained references, force overwrite, and no-backup deletion fail.
- Link checks cover maintained Markdown and local images, including `.github`
  and current research. Historical surfaces are supplemental; ambiguous repair
  requires an explicit mapping.
- Python/React previews include generated `__init__.py`/barrel paths and live
  validation failures restore exact bytes.
- Batch migration preflights every operation, rejects collisions/cycles/bypass
  flags, protects arbitrary rollback roots from child rewriting, compares exact
  preview/live paths and hashes, and restores the whole batch.
- Age-only `archive_old_files.sh` is inactive under `scripts/_archive/`;
  `evolve.py` reports candidates without moving them.
- The registry now has 114 active operations and 101/101 active top-level
  scripts. Historical references remain preserved.

## Required Reading

1. [Safe file operations guide](../guidelines/file-operations-safety-guide.md)
2. [Folder cleanup workflow](../guidelines/folder-cleanup-workflow.md)
3. [Current task board](../TASKS.md)
4. [Git workflow single source](../git-automation/git-workflow-single-source.md)
