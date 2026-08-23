---
description: "File move or rename workflow — safe migration preserving 870+ internal links"
---

# File Move / Rename Workflow

Use this workflow whenever moving, renaming, or deleting files.
NEVER use `mv`, `rm`, `git mv`, or manual rename.

## Step 1: Preview Impact (Dry Run)

### Moving a file:
```bash
./scripts/python_runtime.sh scripts/safe_file_move.py {{old_path}} {{new_path}} --dry-run
```

### Deleting a file:
```bash
./scripts/python_runtime.sh scripts/safe_file_delete.py {{file_path}} --dry-run --json
```

## Step 2: Execute

```bash
./scripts/python_runtime.sh scripts/safe_file_move.py {{old_path}} {{new_path}}
```

For multiple independent moves, create one reviewed JSON plan, run
`batch_migrate_runner.py <plan> --dry-run --json`, then execute that exact plan.
The runner restores the full batch if any operation or changed-path check fails.

## Step 3: For Python/React modules, also update imports

### Python module:
```bash
./scripts/python_runtime.sh scripts/migrate_python_module.py {{old_path}} {{new_path}} --dry-run
./scripts/python_runtime.sh scripts/migrate_python_module.py {{old_path}} {{new_path}}
```

### React component:
```bash
./scripts/python_runtime.sh scripts/migrate_react_component.py {{old_path}} {{new_path}} --dry-run
./scripts/python_runtime.sh scripts/migrate_react_component.py {{old_path}} {{new_path}}
```

## Step 4: Validate Live Context

```bash
./run.sh context validate
./run.sh context summary {{affected_folder}}
```

## Step 5: Validate

```bash
./scripts/python_runtime.sh scripts/validate_imports.py --scope structural_lib   # Python imports
./scripts/python_runtime.sh scripts/check_links.py                    # Doc links
```

## Step 6: Commit

```bash
# Suggest to Codex: refactor: move {{old_path}} to {{new_path}}
```
