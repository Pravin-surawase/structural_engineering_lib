# structural_lib - Core Python Library

> **Purpose:** IS 456:2000 RC beam design calculations
> **Package:** `structural_lib_is456`
> **Last Updated:** 2026-01-10

## Directory Structure

```
structural_lib/
├── core/              # Code-agnostic base classes (NEW - v0.16+)
│   ├── base.py        # Abstract DesignCode, DesignResult
│   ├── materials.py   # Universal Concrete, Steel, MaterialFactory
│   ├── geometry.py    # Section geometry classes
│   └── registry.py    # CodeRegistry for runtime code selection
├── codes/             # Code-specific implementations (NEW - v0.16+)
│   ├── is456/         # IS 456:2000 (active)
│   ├── aci318/        # ACI 318 (placeholder)
│   └── ec2/           # Eurocode 2 (placeholder)
├── flexure.py         # Flexural design (Mu, Ast)
├── shear.py           # Shear design (Vu, stirrups)
├── detailing.py       # Reinforcement detailing
├── serviceability.py  # Deflection, cracking
├── compliance.py      # Code compliance checking
├── tables.py          # IS 456 table lookups
├── materials.py       # Material properties (legacy)
├── constants.py       # Physical constants
├── types.py           # Type definitions
├── utilities.py       # Helper functions
├── api.py             # Public API (start here)
└── __init__.py        # Package exports
```

## Key Design Principles

### 1. Layer Architecture

| Layer | Modules | Rules |
|-------|---------|-------|
| **Core** | flexure, shear, detailing, materials, constants | Pure functions, no I/O |
| **Application** | api, job_runner, bbs | Orchestrates core |
| **UI/I-O** | excel_integration, dxf_export | External interfaces |

### 2. Multi-Code Architecture (v0.16+)

```python
from structural_lib.core import CodeRegistry

# Register codes at import time
CodeRegistry.register("IS456", IS456Code)
CodeRegistry.register("ACI318", ACI318Code)

# Select code at runtime
code = CodeRegistry.get("IS456")
result = code.design_beam(...)
```

### 3. Units Convention

- **Inputs:** mm, N/mm², kN, kN·m
- **Internal:** mm, N, N·mm (convert at boundaries)
- **Outputs:** mm, N/mm², kN, kN·m

## For AI Agents

### When modifying code:

1. **Check layer** - Don't add I/O to core modules
2. **Update VBA** - Keep Python/VBA parity
3. **Add tests** - Every function needs test coverage
4. **Clause refs** - Add IS 456 clause numbers in comments
5. **Type hints** - Use `from __future__ import annotations`

### Running tests:

```bash
# Run all tests
.venv/bin/python -m pytest Python/tests/ -v

# Run specific module
.venv/bin/python -m pytest Python/tests/test_flexure.py -v

# Check types
.venv/bin/python -m mypy Python/structural_lib/
```

### Adding new calculations:

1. Add to appropriate core module
2. Export in `__init__.py`
3. Add to `api.py` if public
4. Write tests with IS 456 reference values
5. Update VBA equivalent

## Archive Policy

- This folder is **never archived**
- Deprecated functions get `@deprecated` decorator before removal
- Major changes require version bump
