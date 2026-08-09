---
name: safe-file-ops
description: "Safely move, rename, or delete repository files while preserving internal links. Preview first, use the repository scripts, and stop if references or validation failures remain."
---

# Safe File Operations

Use the repository file-operation scripts from the workspace root. They constrain targets to this repository, inspect references, and validate links. Manual `mv`, `rm`, or `git mv` bypasses those controls.

## When to Use

- Moving or renaming a tracked repository file
- Deleting a repository file
- Reorganizing folder structure
- Migrating Python modules or React components whose imports must change

Do not use this skill for generated build output or disposable files outside the repository.

## Safe Move / Rename

Preview the exact source and destination:

```bash
.venv/bin/python scripts/safe_file_move.py old/path/file.ext new/path/file.ext --dry-run
```

Confirm that both resolved paths are inside the repository, the source is the intended file, the destination is exact, and the preview contains no unexpected edits.

Then execute the same command without `--dry-run`:

```bash
.venv/bin/python scripts/safe_file_move.py old/path/file.ext new/path/file.ext
```

Inspect `git diff --summary` and `git diff` immediately afterward. If the live result differs from the preview, stop and report it.

## Safe Delete

The command without `--dry-run` deletes the file. Always preview explicitly:

```bash
.venv/bin/python scripts/safe_file_delete.py path/to/file.ext --dry-run
```

If references are reported, update or remove those references first and repeat the preview. Do not bypass the result.

Only after a clean preview, execute the exact same target without `--dry-run`:

```bash
.venv/bin/python scripts/safe_file_delete.py path/to/file.ext
```

The script creates a backup under `tmp/deleted_backups/` by default. Never use `--force` or `--no-backup` in the normal agent workflow. If a referenced file genuinely must be removed, stop for owner direction instead of weakening the guardrail.

## Python Module Migration (with import updates)

Use the dedicated migration script when Python imports must change:

```bash
.venv/bin/python scripts/migrate_python_module.py Python/structural_lib/old.py Python/structural_lib/new.py --dry-run
.venv/bin/python scripts/migrate_python_module.py Python/structural_lib/old.py Python/structural_lib/new.py
```

## React Component Migration (with import updates)

Use the dedicated migration script when React imports must change:

```bash
.venv/bin/python scripts/migrate_react_component.py react_app/src/old.tsx react_app/src/new.tsx --dry-run
.venv/bin/python scripts/migrate_react_component.py react_app/src/old.tsx react_app/src/new.tsx
```

## Verification

After a successful move or delete:

```bash
git diff --summary
.venv/bin/python scripts/check_links.py
```

Regenerate an index only when the affected folder has a generated index:

```bash
.venv/bin/python scripts/generate_enhanced_index.py affected/folder
```

For source migrations, also run the narrow import/build check for that language. Do not regenerate all indexes unless the task actually changes all indexed folders.

## Stop Conditions

Stop without executing when the target is ambiguous, outside the repository, a directory rather than the expected file, already missing, or referenced in ways the script cannot repair. Never substitute a broader shell deletion command.
