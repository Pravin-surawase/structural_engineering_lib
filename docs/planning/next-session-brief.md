# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-23
- Focus: Turn the reproduced MAINT-0130 efficiency defects into narrow,
- Git receipt: docs/verification/maint-0131-git-handoff-receipt.json | sha256:034994ac2f36c9af805e711e421da103c38159524c4a12baa5192141dd537333 | HOLD
- Git identity: codex/maint-0131-efficiency-controls@58ecc149bd4525ae92c4affb369851919fe1c402 | upstream=origin/main@58ecc149bd4525ae92c4affb369851919fe1c402 | base=origin/main@58ecc149bd4525ae92c4affb369851919fe1c402 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | `MAINT-0131` repairs deterministic efficiency-control defects observed during the merged MAINT-0130 workflow |
| **Next** | Prove closeout status, helper-level impact routing, executable compatibility, and complete timing evidence on one frozen candidate |
| **Why** | Broad helper routing selected unrelated product jobs, dirty preparation contradicted its documented exit, and timing requirements were not executable |
| **Held** | Bulk cleanup, automatic archival, unclassified file movement, branch/worktree deletion, product behavior, release, and professional approval |

## Exact MAINT-0131 state

- Branch: `codex/maint-0131-efficiency-controls`, created from merged MAINT-0130
  baseline `58ecc149bd4525ae92c4affb369851919fe1c402`.
- Dirty preparation is status `2` only when every non-cleanliness check passes;
  unknown Git state, operations/conflicts, missing receipts, and final dirty
  validation remain status `1`.
- `scripts/_lib/safe_file_ops.py` selects control-plane, docs, and repository
  validation rather than unrelated Python/FastAPI/React/Excel product jobs.
  Unknown paths still select all domains.
- Closeout usage evidence requires all seven phase timings, exact candidate
  heads, and rejection/repair/retry/full/hosted counters before it writes the
  ignored local ledger.
- Focused control, instruction, and migration evidence is green; candidate
  closeout still requires the quick/full gates, hooks, and hosted checks.

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
