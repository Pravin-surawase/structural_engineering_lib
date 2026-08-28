# Cookbook

Task-focused recipes and code snippets for common structural engineering workflows.

**Canonical family recipes:** 13 | **Updated:** 2026-08-28

---

## 📋 Recipe Index

| Recipe | Description | Status |
|--------|-------------|--------|
| [cli-reference.md](cli-reference.md) | Complete CLI command reference with examples | ✅ |
| [python/family-facades.md](python/family-facades.md) | All 13 canonical family construction journeys | Published in 0.24.0 |
| [family facade contracts](../reference/family-facade-contracts.md) | Generated signatures, units, enums, errors, and statuses | Published in 0.24.0 |
| [python-recipes.md](python-recipes.md) | Compatibility and low-level API snippets | Advanced / compatibility |

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

### Installation Check

```bash
# Confirm interpreter, version, package origin, and optional extras
python -m structural_lib install-preflight
```

---

## 🐍 Quick Python Examples

### Canonical Beam Design

```python
from structural_lib.design.is456 import beam

request = beam.load(
    {
        "identity": {"member_id": "B1", "story": "GF", "case_id": "ULS-1"},
        "section": {"span_mm": 5000.0, "b_mm": 300.0, "D_mm": 500.0, "d_mm": 442.0},
        "materials": {"fck_nmm2": 25.0, "fy_nmm2": 500.0},
        "actions": {"mu_knm": 150.0, "vu_kn": 80.0, "tu_knm": 0.0},
        "calculation_basis": {"d_dash_mm": 58.0, "asv_mm2": 100.0},
    }
)
result = beam.design(request)
print(result.engineering_status)
```

See the [family facade index](python/family-facades.md) for complete copy-paste
payloads and valid error/result handling.

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
