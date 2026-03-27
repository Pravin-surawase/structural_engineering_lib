---
description: "File move or rename workflow — safe migration preserving 870+ internal links"
---

# File Move / Rename Workflow

Use this workflow whenever moving, renaming, or deleting files.
NEVER use `mv`, `rm`, `git mv`, or manual rename.

## Step 1: Preview Impact (Dry Run)

### Moving a file:
```bash
.venv/bin/python scripts/safe_file_move.py {{old_path}} {{new_path}} --dry-run
```

### Deleting a file:
```bash
.venv/bin/python scripts/safe_file_delete.py {{file_path}}
```

## Step 2: Execute

```bash
.venv/bin/python scripts/safe_file_move.py {{old_path}} {{new_path}}
```

## Step 3: For Python/React modules, also update imports

### Python module:
```bash
.venv/bin/python scripts/migrate_python_module.py {{old_path}} {{new_path}} --dry-run
.venv/bin/python scripts/migrate_python_module.py {{old_path}} {{new_path}}
```

### React component:
```bash
.venv/bin/python scripts/migrate_react_component.py {{old_path}} {{new_path}} --dry-run
.venv/bin/python scripts/migrate_react_component.py {{old_path}} {{new_path}}
```

## Step 4: Regenerate Indexes

```bash
.venv/bin/python scripts/generate_enhanced_index.py {{affected_folder}}
```

## Step 5: Validate

```bash
.venv/bin/python scripts/validate_imports.py --scope structural_lib   # Python imports
.venv/bin/python scripts/check_links.py                               # Doc links
```

## Step 6: Commit

```bash
./scripts/ai_commit.sh "refactor: move {{old_path}} to {{new_path}}"
```
