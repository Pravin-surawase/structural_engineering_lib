# Cookbook

Task-focused recipes for common workflows.

## Contents

| Recipe | Status | Use case |
|--------|--------|----------|
| [CLI Reference](cli-reference.md) | ✅ | All command-line options with examples |
| [Python Recipes](python-recipes.md) | 🔜 | Copy-paste snippets for common tasks |

## Quick CLI examples

```bash
# Design beams from CSV
python -m structural_lib design input.csv -o results.json

# Generate bar bending schedule
python -m structural_lib bbs results.json -o schedule.csv

# Generate DXF drawings
python -m structural_lib dxf results.json -o drawings.dxf

# Run complete job
python -m structural_lib job job.json -o ./output
```

See [cli-reference.md](cli-reference.md) for full documentation.
