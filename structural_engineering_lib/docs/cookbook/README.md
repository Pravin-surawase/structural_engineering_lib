# Cookbook

Task-focused recipes and code snippets for common structural engineering workflows.

**Files:** 2 | **Updated:** 2026-01-11

---

## 📋 Recipe Index

| Recipe | Description | Status |
|--------|-------------|--------|
| [cli-reference.md](cli-reference.md) | Complete CLI command reference with examples | ✅ |
| [python-recipes.md](python-recipes.md) | Copy-paste Python snippets for common tasks | ✅ |

---

## 🚀 Quick CLI Examples

### Design Workflow

```bash
# Design beams from CSV input
python -m structural_lib design input.csv -o results.json

# Generate bar bending schedule from results
python -m structural_lib bbs results.json -o schedule.csv

# Generate DXF drawings from results
python -m structural_lib dxf results.json -o drawings.dxf

# Run complete job (design + BBS + DXF)
python -m structural_lib job job.json -o ./output
```

### Quick Validation

```bash
# Check a single beam design
python -m structural_lib check --width 300 --depth 500 --fck 25 --fy 500

# Validate input CSV format
python -m structural_lib validate input.csv
```

---

## 🐍 Quick Python Examples

### Basic Beam Design

```python
from structural_lib import design_beam

result = design_beam(
    b=300,           # mm
    d=500,           # mm effective depth
    fck=25,          # N/mm²
    fy=500,          # N/mm²
    Mu=150,          # kN·m
    Vu=80,           # kN
)
print(f"Main steel: {result.Ast_provided} mm²")
print(f"Stirrups: {result.stirrup_spacing} mm c/c")
```

### Batch Processing

```python
from structural_lib import JobRunner

runner = JobRunner("job_config.json")
results = runner.run()
runner.export_bbs("schedule.csv")
runner.export_dxf("drawings.dxf")
```

See [python-recipes.md](python-recipes.md) for more examples.

---

## 📚 Related Documentation

| Document | Purpose |
|----------|---------|
| [CLI Reference](cli-reference.md) | All command-line options |
| [Python Recipes](python-recipes.md) | Python code snippets |
| [API Reference](../reference/api.md) | Full API documentation |
| [User Guide](../getting-started/user-guide.md) | Complete workflow guide |

---

**Parent:** [docs/README.md](../README.md)
