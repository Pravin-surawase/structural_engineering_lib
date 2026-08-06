# Day 25: Code Quality Tools

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** High
**Created:** 2026-04-08
**Last Updated:** 2026-04-08
**Prerequisites:** Day 7 (Python project structure), Day 24 (agent system)
**Library files:** `pyrightconfig.json`, `Python/pyproject.toml` (ruff config), `scripts/check_architecture_boundaries.py`, `scripts/validate_imports.py`, `scripts/check_links.py`
**Related docs:** `docs/architecture/project-overview.md`

---

## What You'll Learn Today

By the end of this module you'll understand:
- Why type checking matters for structural code (catching unit errors before runtime)
- How `basedpyright` and `pyrightconfig.json` enforce types
- What ruff does and why it's 10-30x faster than the old tools
- How architecture boundary enforcement prevents layer violations
- How import validation catches broken references after file moves
- How documentation quality tools keep 870+ links healthy
- How pre-commit hooks tie everything together

---

## 📖 Theory

### 1. Type Checking — basedpyright

#### Why Types Matter for Structural Code

Imagine a function that calculates shear capacity:

```python
def check_shear(b_mm: float, d_mm: float, fck: float) -> float:
    """Return shear capacity in kN."""
    tau_c = 0.25 * fck ** 0.5  # N/mm²
    return tau_c * b_mm * d_mm / 1000  # Convert N to kN
```

Without type checking, nothing stops you from passing `fck` as a string, or forgetting the return type, or accidentally returning `None` on one branch. In structural engineering, a silent `None` that propagates through a design pipeline could mean an undersized beam reaching a construction site.

**Type checking catches these at dev time — before any test runs, before any CI pipeline.**

#### Our Config — `pyrightconfig.json`

The project's type checking config is minimal but effective:

```json
{
  "extraPaths": ["Python", "scripts"],
  "venvPath": ".",
  "venv": ".venv"
}
```

That's it. The `extraPaths` ensure pyright can resolve imports from both `Python/` (structural_lib) and `scripts/`. The venv settings point to the project's virtual environment so pyright sees installed dependencies like `pydantic`.

#### Common Type Errors

```python
# ❌ Missing types → pyright: reportMissingParameterType
def calc_moment(b, d, fck):
    return 0.138 * fck * b * d**2

# ✅ Fixed
def calc_moment(b: float, d: float, fck: float) -> float:
    return 0.138 * fck * b * d**2
```

```python
# ❌ Unhandled Optional — dict.get() can return None
def get_result(data: dict) -> float:
    return data.get("Mu")  # Could be None!

# ✅ Fixed — check before returning
def get_result(data: dict) -> float:
    value = data.get("Mu")
    if value is None:
        raise KeyError("Missing 'Mu' in results")
    return value
```

---

### 2. Linting — ruff

#### Why ruff?

Before ruff, Python projects ran 3-5 separate tools: `flake8` (style), `isort` (imports), `black` (formatting), `pyupgrade` (modernization), `bandit` (security). Each had its own config format and speed profile.

**ruff replaces all of them in one tool, running 10-30x faster.** Written in Rust, it checks thousands of files in under a second.

#### Our ruff Configuration

From `Python/pyproject.toml`:

```toml
[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = [
  "F",   # Pyflakes — actual errors (undefined names, unused imports)
  "E",   # pycodestyle — style errors
  "W",   # pycodestyle — style warnings
  "I",   # isort — import sorting
  "N",   # pep8-naming — naming conventions
  "UP",  # pyupgrade — Python version improvements
  "B",   # flake8-bugbear — common bugs
  "C4",  # flake8-comprehensions — better comprehensions
  "PIE", # flake8-pie — miscellaneous lints
]

ignore = [
  "E501",  # Line too long (handled by formatter)
  "B008",  # Function call in default argument (common in our API)
]
```

#### Structural Engineering Naming Exceptions

Here's something unique about this project. Standard Python naming says variables should be `lowercase_snake_case`. But structural engineering has its own conventions:

- $A_{st}$ → `Ast` (area of tension steel)
- $M_u$ → `Mu` (factored moment)
- $V_u$ → `Vu` (factored shear force)
- $f_{ck}$ → `fck` (concrete strength)

These are international conventions from IS 456, ACI 318, and Eurocode. Renaming them would confuse every structural engineer who reads the code.

So we tell ruff to allow them:

```toml
[tool.ruff.lint.pep8-naming]
ignore-names = [
  "D", "D_mm",       # Total depth
  "Mu", "Mu_lim",    # Moment parameters
  "Vu", "Vu_kn",     # Shear force
  "Ast", "Ast_prov",  # Steel area
  "Asv",              # Stirrup area
  "Ld",               # Development length
  ...
]
```

And for entire IS 456 code directories:
```toml
[tool.ruff.lint.per-file-ignores]
"structural_lib/codes/is456/**/*.py" = ["N803", "N806"]  # Allow CamelCase args/vars
"tests/codes/is456/**/*.py" = ["N802", "N803", "N806"]   # Also in test methods
```

#### Running ruff

```bash
# Check for issues
cd Python && ruff check structural_lib/

# Auto-fix what can be fixed
cd Python && ruff check --fix structural_lib/

# Format code (replaces black)
cd Python && ruff format structural_lib/
```

---

### 3. Architecture Boundary Enforcement

This is the most important quality tool in the project. The 4-layer architecture only works if imports flow in one direction:

```
Core (codes/) ← Services (api.py) ← UI (fastapi_app/, react_app/)
     ↑ NEVER imports from →             ↑ NEVER imports from →
```

`scripts/check_architecture_boundaries.py` enforces this by scanning every Python file's imports:

```python
LAYERS = {
    "core": {
        "paths": ["Python/structural_lib/codes"],
        "allowed_imports": [
            "structural_lib.codes",
            "structural_lib.constants",
            "math", "dataclasses", "typing",
        ],
        "forbidden_imports": [
            "pandas",
            "structural_lib.api",
            "structural_lib.job_runner",
        ],
    },
    "application": {
        "paths": [
            "Python/structural_lib/api.py",
            "Python/structural_lib/adapters.py",
        ],
        "allowed_imports": [
            "structural_lib", "pydantic", "pandas",
        ],
        "forbidden_imports": [],
    },
    "ui": {
        "paths": ["react_app", "fastapi_app"],
        # UI can import anything
    },
}
```

#### Why This Matters

If `codes/is456/flexure.py` imports from `fastapi_app`, then anyone who installs the library with `pip install structural-lib-is456` and runs `from structural_lib import design_beam_is456` would get an `ImportError` because they don't have FastAPI installed. The core math layer must have **zero external dependencies** beyond pydantic.

Running the check:

```bash
.venv/bin/python scripts/check_architecture_boundaries.py
# ✅ No violations found (3 layers, 47 files checked)

# Or with fix hints:
.venv/bin/python scripts/check_architecture_boundaries.py --fix
```

---

### 4. Import Validation

After moving files (with `safe_file_move.py`), some imports may break. `scripts/validate_imports.py` checks:

```bash
.venv/bin/python scripts/validate_imports.py --scope structural_lib
```

This scans every `.py` file in `structural_lib/`, tries to resolve each import, and reports:
- **Broken imports** — file was moved but import path wasn't updated
- **Circular dependencies** — module A imports B which imports A
- **Missing `__init__.py`** — new directory without package marker

---

### 5. Documentation Quality

With 870+ internal links across hundreds of markdown files, link rot is a real problem. Three tools handle this:

**Link checking:**
```bash
.venv/bin/python scripts/check_links.py
# Scans all .md files for [text](path) links and verifies targets exist
```

**Doc budget:**
```bash
.venv/bin/python scripts/check_docs.py --budget
# Non-archived docs must stay under 400 files
# Prevents "doc sprawl" — creating docs faster than maintaining them
```

**Number sync:**
```bash
.venv/bin/python scripts/sync_numbers.py --fix
# Keeps stats consistent (e.g., "16 agents" in docs matches actual count)
```

---

### 6. Pre-Commit Hooks

All of the above runs automatically before every commit, thanks to `./scripts/ai_commit.sh`. When you run:

```bash
./scripts/ai_commit.sh "fix(shear): correct T-beam capacity formula"
```

Behind the scenes:
1. **ruff check** — lint + style validation
2. **Type check** — pyright catches type errors
3. **Import validation** — no broken imports
4. **Architecture check** — no layer violations
5. **Test run** — relevant tests pass
6. Only then → `git add` → `git commit` → `git push`

If any step fails, the commit is blocked. You fix the issue, then try again. This catches 90% of problems before they ever reach CI.

---

## 🏗️ Library Examples

### Quick Check Output

```bash
$ ./run.sh check --quick

✅ ruff lint .............. OK (0.3s)
✅ import validation ....... OK (1.2s)
✅ architecture boundaries . OK (0.8s)
✅ broken links ............ OK (2.1s)
✅ doc budget .............. OK (0.1s)
✅ version consistency ..... OK (0.2s)
✅ test suite .............. OK (8.4s)
✅ type check .............. OK (3.1s)

8/8 checks passed in 16.2s
```

---

## 🎯 Simple Examples

### Example 1: Catching an Architecture Violation

You're working on `codes/is456/flexure.py` and need beam dimensions from a CSV:

```python
# ❌ WRONG — importing from application layer in core
from structural_lib.services.adapters import GenericCSVAdapter

def calc_flexure(csv_path: str) -> float:
    adapter = GenericCSVAdapter()
    data = adapter.parse(csv_path)
    ...
```

The architecture check catches this:
```
VIOLATION: core layer file 'codes/is456/flexure.py'
  imports 'structural_lib.services.adapters' (application layer)
  Core layer CANNOT import from Application layer
```

The fix: the *service layer* reads the CSV and passes *values* to the core function:
```python
# ✅ RIGHT — core function takes values, not file paths
def calc_flexure(b_mm: float, d_mm: float, fck: float) -> float:
    ...
```

### Example 2: ruff Auto-Fix

```python
# Before ruff --fix
import os, sys
from typing import List, Dict, Optional
from structural_lib.codes.is456 import flexure
from structural_lib.core import data_types
import json

# After ruff --fix (sorted imports, modernized types)
import json
import os
import sys

from structural_lib.codes.is456 import flexure
from structural_lib.core import data_types
```

ruff also upgrades `List[str]` → `list[str]` and `Dict[str, int]` → `dict[str, int]` for Python 3.11+.

---

## 🔧 Exercise

1. Run the quick quality check:
   ```bash
   ./run.sh check --quick
   ```

2. Run the architecture boundary check directly:
   ```bash
   .venv/bin/python scripts/check_architecture_boundaries.py
   ```

3. Check for broken documentation links:
   ```bash
   .venv/bin/python scripts/check_links.py 2>/dev/null | tail -10
   ```

4. Look at the ruff configuration in `Python/pyproject.toml` — find the `per-file-ignores` section. Why does `codes/is456/**/*.py` ignore rules N803 and N806?

5. **Challenge:** Intentionally create a file `Python/structural_lib/codes/is456/test_violation.py` with `import pandas`. Run the architecture checker. Observe the violation. Delete the file.

<details>
<summary>Answer to #4</summary>

N803 = "Argument name should be lowercase" and N806 = "Variable in function should be lowercase." IS 456 structural engineering uses uppercase notation by convention: `Mu` for moment, `Vu` for shear, `Ast` for steel area. These are international standards, not Python style violations.

</details>

---

## 💬 Can You Explain?

Test yourself — can you answer these in one sentence each?

1. Why can't `codes/is456/flexure.py` import from `services/adapters.py`?
2. What does ruff's `UP` rule set do?
3. Why does the project's `pyright` config need `extraPaths: ["Python", "scripts"]`?
4. What's the difference between `check_architecture_boundaries.py` and `validate_imports.py`?
5. Why does `tool_permissions.py` default unknown operations to the "danger" category?

---

## 📎 References

- [pyrightconfig.json](../../../pyrightconfig.json) — type checking config
- [pyproject.toml](../../../Python/pyproject.toml) — ruff, mypy, bandit, isort config
- [check_architecture_boundaries.py](../../../scripts/check_architecture_boundaries.py) — layer enforcement
- [validate_imports.py](../../../scripts/validate_imports.py) — import validation
- [check_links.py](../../../scripts/check_links.py) — documentation link checking
- [Architecture overview](../../architecture/project-overview.md) — 4-layer architecture docs