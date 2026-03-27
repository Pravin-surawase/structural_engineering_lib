---
name: safe-file-ops
description: "Safely move, rename, or delete files while preserving 870+ internal documentation links. Use INSTEAD of manual mv, rm, or git mv. Wraps safe_file_move.py and safe_file_delete.py scripts."
---

# Safe File Operations Skill

This project has 870+ internal documentation links. Moving or deleting files manually breaks them. Always use these safe scripts instead.

## When to Use

- Moving or renaming ANY file (Python, React, docs, scripts)
- Deleting ANY file
- Reorganizing folder structure
- NEVER use `mv`, `rm`, `git mv`, or manual rename on tracked files

## Safe Move / Rename

### Preview first (dry run):
```bash
.venv/bin/python scripts/safe_file_move.py old/path/file.ext new/path/file.ext --dry-run
```

This shows:
- All internal links that reference this file
- Which links will be updated
- Any potential conflicts

### Execute the move:
```bash
.venv/bin/python scripts/safe_file_move.py old/path/file.ext new/path/file.ext
```

This automatically:
- Moves the file
- Updates all internal links across the project
- Preserves git history

### Examples:
```bash
# Move a Python module
.venv/bin/python scripts/safe_file_move.py Python/structural_lib/old_module.py Python/structural_lib/services/new_module.py --dry-run

# Move a React component
.venv/bin/python scripts/safe_file_move.py react_app/src/components/OldComponent.tsx react_app/src/components/design/NewComponent.tsx --dry-run

# Move a doc
.venv/bin/python scripts/safe_file_move.py docs/old-guide.md docs/guides/new-guide.md --dry-run
```

## Safe Delete

### Preview first:
```bash
.venv/bin/python scripts/safe_file_delete.py path/to/file.ext
```

This checks:
- Which files reference the target file
- Whether deletion is safe (no dangling links)
- Shows warnings for files with active references

### Force delete (when you've handled references):
```bash
.venv/bin/python scripts/safe_file_delete.py path/to/file.ext --force
```

## Python Module Migration (with import updates)

For Python modules, use the dedicated migration script that also updates `import` statements:

```bash
.venv/bin/python scripts/migrate_python_module.py Python/structural_lib/old.py Python/structural_lib/new.py --dry-run
.venv/bin/python scripts/migrate_python_module.py Python/structural_lib/old.py Python/structural_lib/new.py
```

## React Component Migration (with import updates)

For React components, use the dedicated migration script:

```bash
.venv/bin/python scripts/migrate_react_component.py react_app/src/old.tsx react_app/src/new.tsx --dry-run
.venv/bin/python scripts/migrate_react_component.py react_app/src/old.tsx react_app/src/new.tsx
```

## After Any File Move

Regenerate folder indexes:
```bash
.venv/bin/python scripts/generate_enhanced_index.py <affected-folder>
# Or regenerate all:
./scripts/generate_all_indexes.sh
```

## Common Mistakes

| Mistake | Why It's Bad | Do This Instead |
|---------|-------------|-----------------|
| `mv file.md new/` | Breaks doc links silently | `safe_file_move.py` |
| `rm old_file.py` | Leaves dangling imports | `safe_file_delete.py` |
| `git mv a b` | Doesn't update internal links | `safe_file_move.py` |
| Skipping `--dry-run` | Can't preview impact | Always dry-run first |
| Forgetting index regen | Stale folder indexes | Run `generate_enhanced_index.py` after |
