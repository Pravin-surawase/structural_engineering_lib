---
description: "Add a new structural element (column, slab, footing) — research IS 456 clauses, define types, implement math, wire API, add tests, create frontend"
---

# Add New Structural Element

## Context

You are adding a **{{element_name}}** design module to structural_engineering_lib. The library currently supports beams only. Follow the 4-layer architecture strictly.

## Step 1: Research IS 456 Clauses

Before coding, identify the exact IS 456:2000 clauses:

```bash
# Check what's already implemented
ls Python/structural_lib/codes/is456/
grep -ri "{{element_name}}" Python/structural_lib/ --include="*.py" -l

# Check clauses.json for references
grep -i "{{element_name}}" Python/structural_lib/codes/is456/clauses.json
```

Key questions to answer:
- Which IS 456 clauses govern this element?
- What are the design formulas?
- What are the min/max limits (reinforcement, dimensions)?
- What SP:16 charts/tables are available for verification?

## Step 2: Define Types (Layer 1 — Core)

Add to existing files — do NOT create new type files:

**`core/inputs.py`** — Input dataclasses:
```python
@dataclass
class {{Element}}GeometryInput:
    b_mm: float        # Width
    D_mm: float        # Depth/diameter
    # ... element-specific dimensions

@dataclass
class {{Element}}LoadsInput:
    # ... element-specific loads with units in name
```

**`core/data_types.py`** — Result dataclass:
```python
@dataclass
class {{Element}}Result:
    # ... design results with explicit units
    is_ok: bool
    governing_check: str
    clause_ref: str
```

**`core/errors.py`** — Error codes:
```python
E_{{ELEMENT}}_001 = DesignError("E_{{ELEMENT}}_001", "Description")
```

## Step 3: Implement Math (Layer 2 — codes/is456/)

Create `Python/structural_lib/codes/is456/{{element}}.py`:

**Pattern to follow (from flexure.py):**
```python
# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       {{element}}
Description:  {{Element}} design per IS 456:2000
Traceability: Functions decorated with @clause.
"""
from __future__ import annotations
import math
from structural_lib.codes.is456.traceability import clause
from structural_lib.core.data_types import {{Element}}Result
from structural_lib.core.errors import E_{{ELEMENT}}_001, DimensionError
from structural_lib.core.validation import validate_dimensions, validate_materials

__all__ = ["design_{{element}}", ...]

@clause("XX.X")
def design_{{element}}(...) -> {{Element}}Result:
    """Design per IS 456 Cl. XX.X."""
    validate_dimensions(...)
    validate_materials(...)
    # Pure math — no I/O
    return {{Element}}Result(...)
```

**Rules:**
- NO import from services/ or UI
- NO I/O (print, file, HTTP)
- ALL units explicit
- ALL formulas cite clause reference
- ALL public functions use `@clause` decorator

## Step 4: Write Tests

Create `Python/tests/unit/test_{{element}}.py`:

```bash
# Reference existing test pattern
head -30 Python/tests/unit/test_compliance.py
```

Requirements:
- 3+ cases per function (normal, boundary, edge)
- Benchmark vs SP:16 within ±0.1%
- Test error cases
- Test min/max limits

## Step 5: Wire into API (Layer 3 — Services)

Add to `Python/structural_lib/services/api.py`:

```bash
.venv/bin/python scripts/discover_api_signatures.py design_beam_is456
# Follow the same pattern for the new element
```

## Step 6: Add FastAPI Endpoint (Layer 4)

```bash
# Check existing router pattern
head -50 fastapi_app/routers/design.py
grep "include_router" fastapi_app/main.py
```

Add router + Pydantic models + register in main.py.

## Step 7: Verify

```bash
.venv/bin/pytest Python/tests/ -v -k "{{element}}"
.venv/bin/python scripts/check_architecture_boundaries.py
.venv/bin/python scripts/validate_imports.py --scope structural_lib
./run.sh check --quick
```

## Step 8: Commit

```bash
./scripts/ai_commit.sh "feat(is456): add {{element}} design module — Cl {{clauses}}"
```

## Agent Pipeline

```
@structural-math  → types + math (Steps 2-3)
@tester           → tests (Step 4)
@structural-engineer → IS 456 verification
@backend          → services/api.py (Step 5)
@api-developer    → FastAPI endpoint (Step 6)
@frontend         → React hook + component
@reviewer         → mandatory gate
@doc-master       → documentation
@ops              → commit + PR
```
