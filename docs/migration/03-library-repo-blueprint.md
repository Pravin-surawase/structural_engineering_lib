# Library Repository Blueprint

**Version:** 2.0
**Type:** Reference
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-04-07
**Last Updated:** 2026-04-08

---

## Repository Name Options

| # | Name | PyPI | Import | Pros | Cons |
|---|------|------|--------|------|------|
| 1 | **rcdesign** | `rcdesign` | `rcdesign` | Short, professional, universally understood | May conflict with other RC design tools |
| 2 | **concretepy** | `concretepy` | `concretepy` | Clear domain + "py" suffix | Longer |
| 3 | **structlib** | `structlib` | `structlib` | Short, expandable beyond IS 456 | Generic |
| 4 | **is456py** | `is456py` | `is456py` | Direct IS 456 reference | Too specific for future codes |
| 5 | **rcdcodes** | `rcdcodes` | `rcdcodes` | "RCD Codes" — signals code compliance | Less memorable |

More options and detailed analysis in [08-naming-and-accounts.md](08-naming-and-accounts.md).

**Recommendation:** `rcdesign` — best balance of short, professional, memorable.

> **Note:** `rcdesign` is taken on PyPI. See [08-naming-and-accounts.md](08-naming-and-accounts.md) for final name selection. Throughout this document, `<PACKAGE_NAME>` is used as a placeholder for the chosen package/import name.

---

## Folder Structure (5-Layer Multi-Code Architecture)

```
<PACKAGE_NAME>/                        # See 08-naming-and-accounts.md for final name
├── .github/
│   ├── copilot-instructions.md        # Global AI agent instructions
│   ├── dependabot.yml                 # Dependency updates
│   ├── CODEOWNERS                     # Auto-assign reviewers
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   ├── feature_request.yml
│   │   └── config.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── workflows/
│   │   ├── ci.yml                     # Test matrix (Python 3.11-3.13 × 3 OS)
│   │   ├── publish.yml                # PyPI Trusted Publishers
│   │   ├── docs.yml                   # ReadTheDocs build
│   │   └── label.yml                  # Auto-label PRs
│   ├── agents/
│   │   ├── coder.agent.md             # Main implementation agent
│   │   ├── reviewer.agent.md          # Code review (read-only)
│   │   ├── tester.agent.md            # Test writing agent
│   │   └── math-verifier.agent.md     # IS 456 formula verification
│   ├── instructions/
│   │   ├── python.instructions.md     # applyTo: '**/*.py'
│   │   ├── tests.instructions.md      # applyTo: 'tests/**'
│   │   └── docs.instructions.md       # applyTo: 'docs/**'
│   ├── prompts/
│   │   ├── new-feature.prompt.md      # New IS 456 function workflow
│   │   ├── fix-bug.prompt.md          # Bug fix workflow
│   │   ├── add-clause.prompt.md       # New IS 456 clause implementation
│   │   └── release.prompt.md          # Release workflow
│   └── skills/
│       ├── test-pipeline/
│       │   └── SKILL.md               # Testing pipeline skill
│       └── is456-verify/
│           └── SKILL.md               # IS 456 verification skill
├── src/
│   └── <PACKAGE_NAME>/               # See 08-naming-and-accounts.md
│       ├── __init__.py                # Public API exports
│       ├── py.typed                   # PEP 561
│       ├── _version.py               # hatch-vcs auto-generated
│       ├── core/                      # Layer 1 — Types, protocols, registry
│       │   ├── protocols.py           # FlexureDesigner, ShearDesigner, DesignCode
│       │   ├── results.py             # BaseResult, FlexureResult, ShearResult
│       │   ├── types.py               # BeamSection, ColumnSection, Material
│       │   ├── materials.py           # Concrete, Steel, MaterialFactory
│       │   ├── constants.py           # Physical constants (Es=200000)
│       │   ├── registry.py            # CodeRegistry
│       │   ├── errors.py              # StructuralLibError hierarchy
│       │   ├── numerics.py            # safe_divide(), approx_equal()
│       │   └── validation.py          # validate_dimensions(), validate_materials()
│       ├── common/                    # Layer 2 — Shared math
│       │   ├── stress_block.py        # Rectangular stress block
│       │   ├── reinforcement.py       # Bar areas, BBS math
│       │   ├── grades.py              # GradeMapping, concrete/steel grade maps
│       │   ├── interpolation.py       # Linear/bilinear with bounds
│       │   └── units.py              # mm_to_in(), kN_to_kip(), MPa_to_psi()
│       ├── codes/                     # Layer 3 — Code implementations
│       │   ├── is456/                 # IS 456:2000
│       │   │   ├── _code.py           # IS456Code implementing DesignCode
│       │   │   ├── constants.py       # GAMMA_C=1.5, GAMMA_S=1.15
│       │   │   ├── tables.py          # Table 19, 23, 26
│       │   │   ├── beam/              # flexure, shear, torsion, detailing, serviceability
│       │   │   ├── column/            # axial, uniaxial, biaxial, slender
│       │   │   ├── slab/              # one_way, two_way
│       │   │   ├── footing/           # isolated, punching
│       │   │   └── seismic/           # IS 13920 ductile detailing
│       │   ├── aci318/                # ACI 318-19
│       │   │   ├── _code.py
│       │   │   ├── constants.py       # PHI_FLEXURE=0.9, Whitney block
│       │   │   ├── beam/
│       │   │   └── column/
│       │   └── ec2/                   # Eurocode 2
│       │       ├── _code.py
│       │       ├── constants.py       # ALPHA_CC=0.85, parabolic block
│       │       └── beam/
│       ├── services/                  # Layer 4 — Orchestration
│       │   ├── api.py                 # High-level design_beam(), compare_codes()
│       │   ├── comparison.py          # Multi-code comparison engine
│       │   ├── adapters.py            # CSV/Excel import
│       │   └── pipeline.py            # Multi-step design pipeline
│       └── _cli/                      # Optional future CLI
│           └── main.py
├── tests/
│   ├── conftest.py                    # Shared fixtures
│   ├── test_beam_flexure.py
│   ├── test_beam_shear.py
│   ├── test_beam_torsion.py
│   ├── test_column_axial.py
│   ├── test_column_uniaxial.py
│   ├── test_footing.py
│   ├── test_common.py
│   ├── test_sp16_benchmarks.py        # SP:16 golden vector tests
│   └── test_property_based.py         # Hypothesis tests
├── benchmarks/
│   └── bench_flexure.py               # pytest-benchmark
├── docs/
│   ├── mkdocs.yml                     # MkDocs Material config
│   ├── index.md                       # Home page
│   ├── getting-started.md
│   ├── api-reference/
│   │   ├── beam.md
│   │   ├── column.md
│   │   └── footing.md
│   └── examples/
│       ├── simple-beam.md
│       └── column-design.md
├── examples/
│   ├── basic_beam_design.py
│   ├── column_with_biaxial.py
│   └── batch_design.py
├── .pre-commit-config.yaml            # ruff, mypy, codespell, check-yaml
├── .python-version                    # 3.12
├── .readthedocs.yaml
├── .editorconfig                      # Cross-editor consistency
├── AGENTS.md                          # Cross-agent instructions
├── CHANGELOG.md                       # towncrier or manual
├── CITATION.cff                       # Academic citation
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md                    # Developer setup guide
├── LICENSE                            # MIT
├── README.md                          # PyPI README
├── pyproject.toml                     # Single source of truth
├── derivations/                       # Theory and formula derivations
│   ├── beam-flexure-theory.md         # Stress block derivation
│   ├── column-interaction.md          # P-M curve derivation
│   └── shear-design-rationale.md      # IS 456 shear provisions
└── uv.lock                           # Locked dependencies
```

---

## Layer Decision Matrix

| Question | Location | Layer |
|----------|----------|-------|
| Type, protocol, or base class? | `core/` | 1 |
| Shared math used by 2+ codes? | `common/` | 2 |
| Specific to IS 456/ACI 318/EC2? | `codes/<code>/` | 3 |
| Orchestrates multiple code calls? | `services/` | 4 |
| Reads files, calls APIs, does I/O? | `services/` or external layer | 4–5 |
| React component or FastAPI route? | `react_app/` or `fastapi_app/` | 5 (UI/IO) |

---

## Dependency Rules (STRICT)

Imports flow **downward only** — never upward.

```
Layer 5 (UI/IO)    → can import from: services, codes, common, core
Layer 4 (Services) → can import from: codes, common, core
Layer 3 (Codes)    → can import from: common, core
Layer 2 (Common)   → can import from: core
Layer 1 (Core)     → imports NOTHING from this package
```

### Forbidden Import Directions

| From → To | Example | Why Forbidden |
|-----------|---------|---------------|
| core → codes | `from <PACKAGE_NAME>.codes.is456 import ...` | Core has zero code-specific knowledge (AR-04) |
| core → common | `from <PACKAGE_NAME>.common import ...` | Core is the foundation — no upward deps |
| common → codes | `from <PACKAGE_NAME>.codes.is456 import ...` | Common is shared, not code-specific |
| codes → services | `from <PACKAGE_NAME>.services import ...` | Pure math, no orchestration |
| codes → UI | `from fastapi_app import ...` | Pure math, no I/O (AR-02) |
| Any → relative | `from .sibling import ...` | Ban all relative imports (AR-03) |

---

## Architecture Enforcement

### tach v0.34.1 (Primary)

[tach](https://github.com/gauge-sh/tach) enforces import boundaries at CI time:

```toml
# tach.toml
[modules]
core = { depends_on = [] }
common = { depends_on = ["core"] }
"codes.*" = { depends_on = ["common", "core"] }
services = { depends_on = ["codes", "common", "core"] }
```

```bash
# CI step
uv run tach check   # Fails if any forbidden import exists
```

### import-linter (Backup)

```toml
# pyproject.toml
[tool.importlinter]
root_packages = ["<PACKAGE_NAME>"]

[[tool.importlinter.contracts]]
name = "5-layer architecture"
type = "layers"
layers = [
    "services",
    "codes",
    "common",
    "core",
]
```

---

## pyproject.toml (Complete Template)

```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[project]
name = "<PACKAGE_NAME>"
dynamic = ["version"]
description = "Multi-code reinforced concrete design library for Python (IS 456, ACI 318, EC2)"
readme = "README.md"
license = "MIT"
requires-python = ">=3.11"
authors = [
    { name = "Pravin Surawase", email = "pravin@example.com" },
]
keywords = [
    "structural-engineering",
    "reinforced-concrete",
    "is456",
    "beam-design",
    "column-design",
    "civil-engineering",
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Education",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Physics",
    "Typing :: Typed",
]
dependencies = [
    "pydantic>=2.0",
]

[project.urls]
Homepage = "https://github.com/owner/<PACKAGE_NAME>"
Documentation = "https://<PACKAGE_NAME>.readthedocs.io"
Repository = "https://github.com/owner/<PACKAGE_NAME>"
Changelog = "https://github.com/owner/<PACKAGE_NAME>/blob/main/CHANGELOG.md"
Issues = "https://github.com/owner/<PACKAGE_NAME>/issues"

[tool.hatch.version]
source = "vcs"

[tool.hatch.build.targets.sdist]
include = ["src/<PACKAGE_NAME>"]

[tool.hatch.build.targets.wheel]
packages = ["src/<PACKAGE_NAME>"]

# --- Dependency Groups (PEP 735) ---

[dependency-groups]
dev = ["pre-commit>=4.0"]
test = [
    "pytest>=9.0",
    "pytest-cov>=6.0",
    "pytest-benchmark>=5.0",
    "hypothesis>=6.100",
    "inline-snapshot>=0.10",
    "mutmut>=3.0",
]
docs = [
    "mkdocs-material>=9.7",
    "mkdocstrings[python]>=1.0",
    "mkdocs-llmstxt>=0.1",
]
lint = [
    "basedpyright>=1.39",
    "mypy>=1.10",
]
arch = [
    "tach>=0.34",
]

# --- Ruff Configuration (19 rule sets — synthesis of pytest, pydantic, polars) ---

[tool.ruff]
target-version = "py311"
line-length = 99
src = ["src"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "N",      # pep8-naming
    "UP",     # pyupgrade
    "B",      # flake8-bugbear
    "A",      # flake8-builtins
    "C4",     # flake8-comprehensions
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
    "RUF",    # ruff-specific rules
    "PT",     # flake8-pytest-style
    "D",      # pydocstyle
    "ANN",    # flake8-annotations
    "S",      # flake8-bandit (security)
    "PIE",    # flake8-pie
    "T20",    # flake8-print
    "PERF",   # perflint
]
ignore = [
    "D100",   # Missing docstring in public module (too noisy initially)
    "ANN101", # Missing type annotation for self
    "ANN102", # Missing type annotation for cls
]

[tool.ruff.lint.pydocstyle]
convention = "numpy"

[tool.ruff.lint.flake8-type-checking]
strict = true

[tool.ruff.lint.flake8-import-conventions]
ban-relative-imports = "all"

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "ANN", "D"]
"benchmarks/**" = ["S101", "ANN", "D", "T20"]

# --- mypy Configuration (strict — following pydantic/httpx pattern) ---

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

# --- basedpyright Configuration (primary type checker — stricter than pyright) ---

[tool.basedpyright]
pythonVersion = "3.11"
typeCheckingMode = "standard"
reportMissingTypeStubs = false
reportUnusedImport = true
reportUnusedVariable = true

# --- pyright Configuration (IDE support via Pylance) ---

[tool.pyright]
pythonVersion = "3.11"
typeCheckingMode = "basic"
strict = ["src"]

# --- pytest Configuration (strict — following polars/sectionproperties) ---

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "-ra",
]
xfail_strict = true
strict_markers = true
strict_config = true
filterwarnings = [
    "error",
    "ignore::DeprecationWarning:hypothesis",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "benchmark: SP:16 benchmark tests",
    "hypothesis: property-based tests",
]

# --- Coverage ---

[tool.coverage.run]
source = ["<PACKAGE_NAME>"]
branch = true

[tool.coverage.report]
show_missing = true
fail_under = 95
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
]
```

---

## .editorconfig Template

Cross-editor consistency — used by Django, most professional libraries:

```ini
root = true

[*]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.{yml,yaml,json,toml}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
```

---

## API Design Philosophy

### Naming Convention
- **Drop** `_is456` suffix from function names — the whole library IS for IS 456
- **Pattern:** `verb_element_specific()` → `design_beam()`, `check_deflection()`
- **Table lookups** use engineering symbols: `tau_c(fck, pt)`, `Mu_lim(b, d, fck)`
- **Dimensions** use unit suffixes: `b_mm`, `d_mm`, `Mu_kNm`
- **Material properties** use IS 456 standard symbols: `fck`, `fy` — units documented in docstrings, not in parameter names

### Return Types
- Return typed dataclasses or Pydantic models, **never raw dicts**
- Every result type has `.is_safe()`, `.to_dict()`, `.summary()` methods
- Frozen dataclasses for immutability

### Import Patterns

```python
# Primary — concise
import <PACKAGE_NAME> as rc
result = rc.design_beam(b_mm=230, d_mm=450, Mu_kNm=85, fck=25, fy=415)

# Direct import — for scripts
from <PACKAGE_NAME> import design_beam, check_shear, tau_c

# Submodule access — for power users
from <PACKAGE_NAME>.codes.is456.beam import flexure
Mu_lim = flexure.calculate_mu_lim(b_mm=230, d_mm=450, fck=25)

# Multi-code comparison
from <PACKAGE_NAME>.services import comparison
result = comparison.compare_codes(["is456", "aci318"], b_mm=300, d_mm=500, fck=30)
```

---

## Success Criteria

| Criteria | Target | Measurement |
|----------|--------|-------------|
| Install time | < 5 sec | `time pip install <PACKAGE_NAME>` |
| Package size | < 500KB | `pip show <PACKAGE_NAME>` |
| SP:16 accuracy | ±0.1% | `pytest -m benchmark` |
| Type safety | Zero errors | `mypy --strict src/` |
| Lint | Zero issues | `ruff check src/` |
| CI time | < 60 sec | GitHub Actions run time |
| Test coverage | 95%+ | `pytest --cov` |
| Python versions | 3.11, 3.12, 3.13 | CI matrix |
| OS support | Linux, macOS, Windows | CI matrix |
