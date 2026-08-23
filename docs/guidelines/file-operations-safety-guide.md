---
owner: Main Agent
status: active
last_updated: 2026-08-23
doc_type: guide
complexity: intermediate
tags: [file-operations, safety, migration]
---

# File Operations Safety Guide

Use these controls for tracked or maintained repository files. Manual `mv`,
`git mv`, `rm`, destination overwrite, and reference bypass are not accepted
file-maintenance paths.

## Safety contract

The live tools accept only regular files inside the current repository. They
reject directories, symlinks, outside paths, existing destinations, missing
validators, and maintained references that cannot be updated deterministically.

Reference results have three meanings:

- **updateable** — the preview identifies an exact target rewrite and the live
  transaction must update that same file;
- **preserved** — historical evidence retains the path text that was true when
  recorded;
- **unresolved** — the operation is blocked until an explicit repair is made.

Every live operation starts from a structured link baseline. If the live
changed paths differ from the preview, a validator fails, or new broken links
appear, the original bytes and file modes are restored and the command exits
nonzero.

## Move or rename one file

```bash
./scripts/python_runtime.sh scripts/safe_file_move.py old/path/file.md new/path/file.md --dry-run --json
./scripts/python_runtime.sh scripts/safe_file_move.py old/path/file.md new/path/file.md --json
```

Use `--stub` only when a maintained Markdown redirect is intentionally part of
the reviewed preview. There is no force-overwrite option.

## Delete one file

```bash
./scripts/python_runtime.sh scripts/safe_file_delete.py path/to/file.md --dry-run --json
./scripts/python_runtime.sh scripts/safe_file_delete.py path/to/file.md --json
```

Any maintained reference blocks deletion. A successful live deletion always
creates a content-addressed backup and JSON manifest under
`tmp/deleted_backups/<sha256>/`. There is no force or no-backup mode.

## Check and repair Markdown references

```bash
./scripts/python_runtime.sh scripts/check_links.py
./scripts/python_runtime.sh scripts/check_links.py --json
./scripts/python_runtime.sh scripts/check_links.py --fix --map explicit-links.json
```

The default scan covers maintained Markdown throughout the repository,
including `.github`, current research, and local image targets. Historical
archives and declared historical evidence are excluded from the maintained
baseline; add `--include-historical` for a supplemental audit.

Automatic repair is allowed only when the indexed repository has exactly one
candidate. Ambiguous cases require an explicit mapping. Mapping keys may be a
target or `source/file.md::target`; every mapped destination must exist.

## Python and React source migration

```bash
./scripts/python_runtime.sh scripts/migrate_python_module.py Python/structural_lib/old.py Python/structural_lib/new.py --dry-run --json
./scripts/python_runtime.sh scripts/migrate_python_module.py Python/structural_lib/old.py Python/structural_lib/new.py --json

./scripts/python_runtime.sh scripts/migrate_react_component.py react_app/src/old.tsx react_app/src/new.tsx --dry-run --json
./scripts/python_runtime.sh scripts/migrate_react_component.py react_app/src/old.tsx react_app/src/new.tsx --json
```

The Python preview includes a newly required `__init__.py`; the React preview
includes a created or updated barrel `index.ts`. Live source migrations reject
existing destinations and restore all predicted files if validation fails.
Run the language-level focused suite once after the intended migration content
is frozen.

## Transactional batch migration

Create a reviewed JSON plan:

```json
{
  "operations": [
    {
      "tool": "safe_move",
      "source": "docs/old.md",
      "destination": "docs/new.md"
    },
    {
      "tool": "python_module",
      "source": "Python/structural_lib/old.py",
      "destination": "Python/structural_lib/new.py",
      "args": ["--no-stub"]
    }
  ]
}
```

Then preflight the complete plan before any live operation:

```bash
./scripts/python_runtime.sh scripts/batch_migrate_runner.py plan.json --dry-run --json
./scripts/python_runtime.sh scripts/batch_migrate_runner.py plan.json --json
```

The runner rejects bypass flags, collisions, cycles, chained sources, and any
failed operation preview. It writes one batch manifest, compares actual changed
paths and per-file hashes with the complete preview, and restores the entire
batch after any failure. The generated rollback can also be executed and
verified later:

```bash
logs/migration-rollbacks/<run-id>/rollback.sh
```

## Archival and cleanup

Age is metadata, not an archival decision. Automatic age-based archival is
retired. First classify exact files by current ownership,
replacement, reference, retention, and historical-evidence requirements. Put
the accepted moves in a transactional batch plan; do not scan and move a whole
folder merely because modification timestamps are old.

## Review and verification

After content freezes, inspect the exact diff and run the affected checks
together:

```bash
git diff --summary
git diff
./scripts/python_runtime.sh scripts/check_links.py
./scripts/python_runtime.sh -m pytest tests/integration/test_migration_scripts.py -q
./run.sh context validate
./run.sh check --quick
```

Stop if preview/live path sets differ, a rollback cannot be verified, the
repository lane is unclear, or references remain unresolved.
