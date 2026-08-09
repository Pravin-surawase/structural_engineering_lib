# Day 26: PyPI Packaging

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** High
**Created:** 2026-04-08
**Last Updated:** 2026-04-08
**Prerequisites:** Day 7 (Python project structure), Day 25 (code quality tools)
**Library files:** `Python/pyproject.toml`, `Python/MANIFEST.in`, `Python/structural_lib/__init__.py`
**Related docs:** `CHANGELOG.md`, `.github/workflows/` (CI publishing)

---

## What You'll Learn Today

By the end of this module you'll understand:
- What PyPI is and why packaging matters
- How `pyproject.toml` defines everything about the package
- What `MANIFEST.in` controls and why you need it
- How version management works across multiple files
- The difference between wheels and source distributions
- How Trusted Publishers eliminates API tokens
- What release preflight checks catch before publishing
- The most common packaging mistakes (and how to avoid them)

---

## 📖 Theory

### 1. What Is PyPI?

PyPI — the **Python Package Index** — is the official repository where Python packages live. When someone types:

```bash
pip install structural-lib-is456
```

pip connects to `https://pypi.org`, downloads the package, and installs it. That's how the library reaches users who don't clone the Git repo.

> **Think of it like...** the App Store for Python libraries. `pyproject.toml` is the app listing. `pip install` is the download button. PyPI is the store.

Without PyPI packaging, users would need to clone the repo, navigate to the right directory, install dependencies manually, and set up their `sys.path`. With it, they get a one-line install that just works.

---

### 2. `pyproject.toml` — The Modern Packaging Config

Before 2022, Python packaging was a mess — `setup.py`, `setup.cfg`, `requirements.txt`, `MANIFEST.in`, all scattered everywhere. PEP 621 unified everything into **one file**: `pyproject.toml`.

Here's our config, section by section:

#### Build System

```toml
[build-system]
requires = ["setuptools>=77.0"]
build-backend = "setuptools.build_meta"
```

This tells Python: "To build this package, install `setuptools` version 77+, and use its `build_meta` backend." Other backends exist (flit, hatch, poetry), but setuptools is the most widely supported.

#### Project Metadata

```toml
[project]
name = "structural-lib-is456"
version = "0.21.6"
description = "IS 456 RC Design Library — beams, columns & footings"
readme = "README.md"
requires-python = ">=3.11"
license = "MIT"
authors = [{ name = "Pravin Surawase" }]
```

- **`name`** — what appears on PyPI and in `pip install structural-lib-is456`
- **`version`** — semantic versioning (major.minor.patch)
- **`requires-python`** — minimum Python version. Users on 3.10 get: `ERROR: Requires Python >=3.11`
- **`license`** — MIT means anyone can use, modify, distribute

#### Dependencies

```toml
dependencies = [
  "pydantic>=2.0",
]
```

**Just one runtime dependency.** This is intentional. A structural engineering library should install fast and not drag in hundreds of transitive dependencies. `pydantic` is needed for data validation models — that's it.

Everything else is optional:

```toml
[project.optional-dependencies]
dev = ["pytest", "pytest-cov", "ruff", "bandit", "hypothesis>=6.0"]
dxf = ["ezdxf>=1.0"]           # DXF drawing export
render = ["ezdxf>=1.0", "matplotlib>=3.5"]  # DXF render to PNG/PDF
report = ["jinja2>=3.1"]       # HTML report templates
pdf = ["reportlab>=4.0"]       # PDF generation
docs = ["mkdocs-material>=9.5"]
```

Users install extras with square brackets:
```bash
pip install structural-lib-is456          # Just the core (+ pydantic)
pip install structural-lib-is456[dxf]     # Core + DXF export
pip install structural-lib-is456[dev]     # Core + dev tools (for contributors)
pip install "structural-lib-is456[dxf,report]"  # Multiple extras
```

#### Package Discovery

```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["structural_lib*"]
exclude = ["tests*", "examples*", "scripts*"]
```

This tells setuptools: "Look in the current directory for packages starting with `structural_lib`. Don't include tests, examples, or scripts — those aren't part of the distributed library."

#### Package Data

```toml
[tool.setuptools.package-data]
structural_lib = [
  "py.typed",
  "codes/is456/clauses.json",
  "reports/templates/*.j2",
]
```

Python packages normally only include `.py` files. If your package ships JSON data files or Jinja2 templates, you must explicitly list them here. Without this line, `clauses.json` would be missing from the installed package and `from structural_lib.codes.is456 import clauses` would fail with a FileNotFoundError.

- **`py.typed`** — marker file that tells type checkers "this package has type annotations"
- **`clauses.json`** — IS 456 clause definitions used at runtime
- **`templates/*.j2`** — Jinja2 templates for report generation

---

### 3. `MANIFEST.in` — Source Distribution Control

`MANIFEST.in` controls what goes into the *source distribution* (`.tar.gz`). Here's ours:

```
include structural_lib/py.typed
include structural_lib/codes/is456/clauses.json
recursive-include structural_lib/reports/templates *.j2
include LICENSE
include README.md

# Exclude non-distribution files from sdist
global-exclude tests
global-exclude *.pyc
prune tests
prune examples
prune scripts
```

**Why two configs?** `pyproject.toml`'s `package-data` controls what goes in the *wheel* (`.whl`). `MANIFEST.in` controls what goes in the *sdist* (`.tar.gz`). They overlap but serve different build paths.

| Directive | What It Does |
|-----------|-------------|
| `include` | Add a specific file |
| `recursive-include` | Add all matching files under a directory |
| `global-exclude` | Remove matching files everywhere |
| `prune` | Remove an entire directory tree |

---

### 4. Version Management

The version lives in multiple places and must stay in sync:

| Location | Example |
|----------|---------|
| `Python/pyproject.toml` | `version = "0.21.6"` |
| `Python/structural_lib/__init__.py` | `__version__ = "0.21.6"` |
| `CITATION.cff` | `version: 0.21.6` |

Updating manually is error-prone. The release script handles it:

```bash
./run.sh release run 0.22.0
```

This bumps the version in all files, creates a git tag, and starts the release workflow. Never edit version strings manually — use the script.

---

### 5. Building the Distribution

Two distribution formats exist:

**Wheel (`.whl`)** — Pre-built, fast to install. No build step needed on the user's machine.
```bash
cd Python && python -m build --wheel
# Creates: dist/structural_lib_is456-0.21.6-py3-none-any.whl
```

**Source distribution (`.tar.gz`)** — Contains source code. User's pip runs the build step.
```bash
cd Python && python -m build --sdist
# Creates: dist/structural_lib_is456-0.21.6.tar.gz
```

**Build both at once:**
```bash
cd Python && python -m build
# Creates both in dist/
```

The wheel filename tells you everything:
```
structural_lib_is456-0.21.6-py3-none-any.whl
│                    │       │   │    │
│                    │       │   │    └── Any CPU architecture
│                    │       │   └────── No platform restriction
│                    │       └────────── Python 3 (any minor version)
│                    └────────────────── Version 0.21.6
└─────────────────────────────────────── Package name
```

`py3-none-any` means this is a **pure Python package** — no compiled C extensions, works on any OS and CPU. This is ideal because structural engineering math is pure Python + pydantic.

---

### 6. Publishing to PyPI

#### Trusted Publishers (Modern Way)

The old way: generate an API token on pypi.org, paste it into GitHub Secrets, use it in CI. Tokens can leak, expire, and need rotation.

The modern way: **Trusted Publishers**. You tell PyPI "trust builds from this GitHub repository" and GitHub Actions can publish directly — no tokens stored anywhere.

How it works:
1. Register the package on pypi.org
2. Add a Trusted Publisher: `github.com/Pravin-surawase/structural_engineering_lib`
3. In CI, the publish step uses OIDC authentication (identity federation)
4. GitHub proves "I am this repo" → PyPI says "OK, you're trusted" → package published

#### The CI Pipeline

When you push a git tag like `v0.22.0`:

```
git tag v0.22.0 → GitHub Actions triggers →
  1. Run full test suite
  2. python -m build (wheel + sdist)
  3. twine check dist/* (validate metadata)
  4. Upload to PyPI via Trusted Publisher
```

---

### 7. Release Preflight

Before any release, run the preflight check:

```bash
./run.sh release preflight 0.22.0
```

This runs **5 phases** — packaging test (build → install → verify imports), UAT (run key functions against benchmarks), security scan (bandit + CVE check), API/doc consistency, and CI readiness (tests, coverage, links).

You can also run preflight in Docker to simulate a truly fresh environment:
```bash
./run.sh release preflight --docker
```

---

### 8. Common Packaging Mistakes

| Mistake | Fix |
|---------|-----|
| Missing data file in `MANIFEST.in` | Add `include` directive — preflight catches this |
| Version mismatch (`__init__` vs `pyproject.toml`) | Use `./run.sh release run` — never edit manually |
| Too many dependencies | Keep `dependencies` minimal — extras for optional features |
| Tests included in wheel | `exclude = ["tests*"]` in `packages.find` |
| Missing `py.typed` | Add to `package-data` — enables type checker support |
| No `requires-python` | Set `>=3.11` — prevents broken installs on old Python |

---

## 🏗️ Library Examples

### Full pyproject.toml Tour

```bash
# See the complete packaging config
cat Python/pyproject.toml | head -50
```

Key sections and what they control:

```
[build-system]         → How to build the package
[project]              → Metadata (name, version, deps)
[project.urls]         → Links shown on PyPI page
[project.optional-dependencies] → pip install lib[extra]
[tool.setuptools]      → Package discovery rules
[tool.ruff]            → Linting config (Day 25)
[tool.mypy]            → Type checking config
[tool.bandit]          → Security scanning
[tool.isort]           → Import sorting
```

### Building and Installing Locally

```bash
# Install build tool and build from the Python/ directory
cd Python && pip install build && python -m build

# Inspect the wheel — verify data files are included
unzip -l dist/structural_lib_is456-0.21.6-py3-none-any.whl | grep -E "clauses|py.typed|j2"

# Test in a clean venv
python -m venv /tmp/test-install && source /tmp/test-install/bin/activate
pip install dist/structural_lib_is456-0.21.6-py3-none-any.whl
python -c "import structural_lib; print(f'Version: {structural_lib.__version__}')"
deactivate && rm -rf /tmp/test-install
```

---

## 🎯 Simple Examples

### Example 1: Why Only One Runtime Dependency?

Compare our `dependencies` with a typical web framework:

```toml
# ours: 1 dependency
dependencies = ["pydantic>=2.0"]

# a typical web project: 20+ dependencies
dependencies = [
    "fastapi>=0.100",
    "uvicorn[standard]>=0.23",
    "sqlalchemy>=2.0",
    "alembic>=1.12",
    "redis>=5.0",
    ...
]
```

Why? Because structural engineers installing this library may not have (or want) a web server. They want `pip install structural-lib-is456` and then:

```python
from structural_lib import design_beam_is456
result = design_beam_is456(b_mm=300, D_mm=500, fck=25, fy=415, Mu_knm=150)
```

FastAPI is a *deployment* dependency for our API server, not a *library* dependency. It lives in `requirements.txt` (for the dev stack) but not in `pyproject.toml` (for the published library).

### Example 2: Optional Extras in Action

```python
# Basic usage — no extras needed
from structural_lib import design_beam_is456

# DXF export — needs: pip install structural-lib-is456[dxf]
from structural_lib import export_beam_dxf
export_beam_dxf(result, "beam_detail.dxf")
# Without [dxf]: ImportError with helpful message
```

---

## 🔧 Exercise

1. Look at our `pyproject.toml` and answer:
   - What Python versions are supported?
   - What's the only runtime dependency?
   - How many optional extra groups are defined?

2. Look at `MANIFEST.in` and answer:
   - What non-Python files are included in the source distribution?
   - What directories are pruned (excluded)?

3. Build the wheel locally:
   ```bash
   cd Python && pip install build && python -m build --wheel
   ```

4. Inspect the wheel contents:
   ```bash
   unzip -l dist/structural_lib_is456-*.whl | grep -E "clauses|py.typed|j2"
   ```
   Verify that `clauses.json`, `py.typed`, and `.j2` templates are included.

5. **Challenge:** Install the wheel in a temporary venv and verify the import works:
   ```bash
   python -m venv /tmp/test-pkg
   source /tmp/test-pkg/bin/activate
   pip install dist/structural_lib_is456-*.whl
   python -c "import structural_lib; print(structural_lib.__version__)"
   deactivate && rm -rf /tmp/test-pkg
   ```

<details>
<summary>Answers to #1</summary>

- **Python versions:** >=3.11 (also classified for 3.11, 3.12, 3.13)
- **Runtime dependency:** pydantic>=2.0 (only one!)
- **Optional extras:** 7 groups — dev, dxf, render, report, pdf, validation, docs

</details>

<details>
<summary>Answers to #2</summary>

- **Included non-Python files:** `py.typed`, `clauses.json`, `*.j2` templates, LICENSE, README.md
- **Pruned directories:** tests, examples, scripts

</details>

---

## 💬 Can You Explain?

Test yourself — can you answer these in one sentence each?

1. What's the difference between a wheel and a source distribution?
2. Why does `MANIFEST.in` exist when `pyproject.toml` already has `package-data`?
3. Why is pydantic the only runtime dependency instead of including FastAPI?
4. What does `py3-none-any` in a wheel filename mean?
5. What problem do Trusted Publishers solve compared to API tokens?

---

## 📎 References

- [pyproject.toml](../../../Python/pyproject.toml) — our complete packaging config
- [MANIFEST.in](../../../Python/MANIFEST.in) — source distribution control
- [Python Packaging User Guide](https://packaging.python.org/) — official docs
- [PEP 621](https://peps.python.org/pep-0621/) — pyproject.toml metadata standard
- [Trusted Publishers](https://docs.pypi.org/trusted-publishers/) — OIDC publishing
- [setuptools docs](https://setuptools.pypa.io/) — build backend documentation
- [CHANGELOG](../../../CHANGELOG.md) — release history