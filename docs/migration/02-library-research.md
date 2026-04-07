# Library Research — 20 Top Python Libraries Analyzed

**Type:** Research
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-04-07
**Last Updated:** 2026-04-08

---

## Purpose

Systematic review of 20 leading Python libraries to extract best practices for repository structure, packaging, CI/CD, tooling, and AI agent configuration. Findings directly inform our two-repo migration. Includes deep-dive analysis of pyproject.toml configs, CI/CD patterns, pre-commit hooks, and structural engineering libraries.

---

## 1. NumPy

| Attribute | Value |
|-----------|-------|
| **Stars** | 31.8k |
| **Contributors** | 1,854 |
| **Layout** | Flat (`numpy/`) |
| **Build system** | meson-python |
| **License** | BSD-3-Clause |
| **Key insight** | `spin` developer CLI wrapping build/test/docs/lint — single entry point for all dev tasks |

- Uses `spin` CLI (`spin build`, `spin test`, `spin docs`) as developer workflow UX
- C/Fortran extensions make meson-python necessary — not relevant for pure Python
- Extensive CI matrix across OS and Python versions
- `numpy/typing/` subfolder for type stubs

## 2. Pandas

| Attribute | Value |
|-----------|-------|
| **Stars** | 48.4k |
| **Contributors** | 3,711 |
| **Layout** | Flat (`pandas/`) |
| **Build system** | meson-python |
| **License** | BSD-3-Clause |
| **Key insight** | `pixi.toml` for reproducible environments — largest open-source contributor base |

- Largest contributor count (3,711) — governance model worth studying
- Uses `pixi` for environment management (conda-based)
- Heavy C extension use → meson-python
- Comprehensive `pandas-stubs` for typing

## 3. SciPy

| Attribute | Value |
|-----------|-------|
| **Stars** | 14.6k |
| **Contributors** | 1,707 |
| **Layout** | Flat (`scipy/`) |
| **Build system** | meson-python |
| **License** | BSD-3-Clause |
| **Key insight** | `tach.toml` module boundary enforcement — prevents internal import violations |

- Uses `tach` for module boundary enforcement — prevents architecture drift
- Similar to our 4-layer import rule but automated
- Extensive benchmark suite with `asv` (airspeed velocity)
- `scipy.special` pattern: submodules with clean `__init__.py` re-exports

## 4. FastAPI

| Attribute | Value |
|-----------|-------|
| **Stars** | 96.9k |
| **Contributors** | 903 |
| **Layout** | Flat (`fastapi/`) |
| **Build system** | pdm-backend → migrating to uv |
| **License** | MIT |
| **Key insight** | `dependency-groups` (PEP 735), `inline-snapshot` for snapshot testing |

- Most starred Python framework — excellent docs as competitive advantage
- Uses `dependency-groups` for dev/test/docs separation (PEP 735)
- `inline-snapshot` for API response testing — worth adopting
- Migration from pdm-backend to uv shows industry direction

## 5. Pydantic

| Attribute | Value |
|-----------|-------|
| **Stars** | 27.4k |
| **Contributors** | 741 |
| **Layout** | Flat (`pydantic/`) |
| **Build system** | hatchling with uv workspace |
| **License** | MIT |
| **Key insight** | `hatch-fancy-pypi-readme`, `mkdocs-llmstxt`, runs 3 type checkers (mypy + pyright + pytype) |

- Uses `hatch-fancy-pypi-readme` to generate rich PyPI README from docs
- `mkdocs-llmstxt` plugin for LLM-friendly documentation
- Runs three type checkers in CI — most thorough type safety
- uv workspace for managing multiple related packages

## 6. Polars

| Attribute | Value |
|-----------|-------|
| **Stars** | 38k |
| **Contributors** | 691 |
| **Layout** | Rust monorepo (`polars/`, `py-polars/`) |
| **Build system** | maturin (Rust → Python) |
| **License** | MIT |
| **Key insight** | Runtime splitting for CPU architectures, most comprehensive ruff config with `ban-relative-imports = "all"` |

- `ban-relative-imports = "all"` in ruff config — enforces absolute imports everywhere
- Runtime splitting: different wheels for different CPU architectures
- Most comprehensive ruff rule set — good template for our config
- Rust core with Python bindings — excellent performance architecture

## 7. HTTPX

| Attribute | Value |
|-----------|-------|
| **Stars** | 15.2k |
| **Contributors** | 238 |
| **Layout** | Flat (`httpx/`) |
| **Build system** | hatchling |
| **License** | BSD-3-Clause |
| **Key insight** | Cleanest pyproject.toml — ideal model for mid-size pure Python libraries |

- Minimal, well-organized `pyproject.toml` — best template for our library
- Uses hatchling with no plugins — simplest build setup
- Clean `__init__.py` with explicit `__all__`
- Good balance of features vs. simplicity

## 8. Rich

| Attribute | Value |
|-----------|-------|
| **Stars** | 56k |
| **Contributors** | 273 |
| **Layout** | Flat (`rich/`) |
| **Build system** | poetry-core |
| **License** | MIT |
| **Key insight** | Simplest tooling despite 56k stars — proof you don't need complexity for a successful library |

- 56k stars with relatively simple tooling — quality matters more than infrastructure
- Uses poetry-core (not full poetry) — lighter weight
- Single `rich/` package with submodules — clean structure
- Excellent docstrings and examples in code

## 9. Ruff

| Attribute | Value |
|-----------|-------|
| **Stars** | 46.9k |
| **Contributors** | 834 |
| **Layout** | Rust monorepo |
| **Build system** | maturin |
| **License** | MIT |
| **Key insight** | Self-dogfooding (uses ruff to lint itself), cargo-dist for releases |

- Self-dogfooding: uses ruff to check ruff's own Python code
- `cargo-dist` for cross-platform binary releases
- Aggressive CI: checks on every commit, benchmarks on PRs
- Replaced flake8 + black + isort + pyupgrade — single tool

## 10. sectionproperties ⭐ (Best Reference)

| Attribute | Value |
|-----------|-------|
| **Stars** | 520 |
| **Contributors** | 16 |
| **Layout** | **src/ layout** (`src/sectionproperties/`) |
| **Build system** | hatchling with uv |
| **License** | MIT |
| **Key insight** | JOSS-published, CITATION.cff, dependency-groups, pyright, Codecov — **closest peer to our project** |

- **Most relevant reference** — structural engineering library on PyPI
- Uses src/ layout (industry standard for libraries)
- hatchling + uv — modern, fast, simple
- JOSS publication + CITATION.cff — academic credibility
- `dependency-groups` (PEP 735) for dev/test/docs
- pyright for type checking in IDE
- Codecov for coverage tracking
- Clean API design with builder pattern

## 11. PyNite

| Attribute | Value |
|-----------|-------|
| **Stars** | 684 |
| **Contributors** | 22 |
| **Layout** | Flat (`PyNite/`) |
| **Build system** | Legacy setup.py |
| **License** | MIT |
| **Key insight** | `PyniteFEA` PyPI name (domain suffix pattern). **Anti-pattern: no modern tooling** |

- Structural engineering library — relevant domain
- Uses legacy `setup.py` — anti-pattern, do not follow
- PyPI name `PyniteFEA` — uses domain suffix for disambiguation
- No type hints, no CI, no pre-commit — shows what NOT to do
- Still has 684 stars — proves demand for structural engineering tools

## 12. COMPAS

| Attribute | Value |
|-----------|-------|
| **Stars** | 356 |
| **Contributors** | 53 |
| **Layout** | **src/ layout** (`src/compas/`) |
| **Build system** | setuptools with multi-package support |
| **License** | MIT |
| **Key insight** | 4 packages from one repo (compas, compas_viewer, etc.), invoke tasks, conda-first distribution |

- Multi-package architecture — 4 related packages from one repo
- Uses `invoke` for task automation (alternative to our `run.sh`)
- conda-first distribution — academic/research audience
- src/ layout with namespace packages
- Good model for future expansion (compas_fea, compas_timber)

## 13. OpenSeesPy

| Attribute | Value |
|-----------|-------|
| **Stars** | 250 |
| **Contributors** | 94 |
| **Layout** | C++/CMake with Python bindings |
| **Build system** | CMake + setuptools |
| **License** | Restrictive (modified BSD) |
| **Key insight** | Shows challenge of wrapping C++ FEA for Python. **Anti-pattern: no modern Python packaging** |

- Most popular FEA Python binding — shows market demand
- C++ core with Python bindings via pybind11
- Complex build system (CMake + setuptools) — unnecessary for pure Python
- Restrictive license — not ideal for open source
- No modern Python packaging (no pyproject.toml, no ruff)

## 14. Django

| Attribute | Value |
|-----------|-------|
| **Stars** | 87.2k |
| **Contributors** | 2,761 |
| **Layout** | Flat (`django/`) |
| **Build system** | setuptools |
| **License** | BSD-3-Clause |
| **Key insight** | Minimal pyproject.toml for 87k-star project. `.editorconfig` for cross-editor consistency |

- 87k stars with minimal `pyproject.toml` — proves simple packaging works at scale
- `.editorconfig` for consistent formatting across editors — worth adopting
- Uses setuptools (legacy choice, but stable)
- Towncrier for structured changelogs

## 15. pytest ⭐ (Gold Standard Quality)

| Attribute | Value |
|-----------|-------|
| **Stars** | 13.7k |
| **Contributors** | 941 |
| **Layout** | **src/ layout** (`src/pytest/`) |
| **Build system** | setuptools-scm |
| **License** | MIT |
| **Key insight** | Most thorough quality toolchain: ruff + pylint + codespell + mypy + pyright + check-wheel-contents + pyproject-fmt + towncrier |

- **Gold standard** for quality toolchain — 8 tools in CI
- src/ layout with setuptools-scm for version management
- `check-wheel-contents` — verifies built wheel has all files
- `pyproject-fmt` — auto-formats pyproject.toml
- `towncrier` for changelog fragments — each PR adds a news fragment
- `codespell` for catching typos in code and docs
- Both mypy and pyright in CI

---

## Comparison Tables

### Build System Comparison

| Build Backend | Used By | Best For | Our Choice? |
|---|---|---|---|
| **hatchling** | sectionproperties, httpx, pydantic | Pure Python, modern | ✅ **Yes** |
| setuptools | pytest, django, compas | Mature, stable | No — older |
| pdm-backend | FastAPI (migrating away) | pdm ecosystem | No — niche |
| meson-python | numpy, pandas, scipy | C/Fortran extensions | No — overkill |
| poetry-core | Rich | Poetry ecosystem | No — lock-in |
| maturin | ruff, polars | Rust+Python | No — not Rust |

### Tooling Adoption Across 15 Libraries

| Tool | Adoption | Verdict for Us |
|---|---|---|
| **ruff** | 12/15 | ✅ Universal standard — must adopt |
| **mypy** | 10/15 | ✅ Most common type checker — use strict mode |
| **pre-commit** | 9/15 | ✅ Standard hook management — must adopt |
| **MkDocs** | 6/15 | ✅ Rising (Material theme) — already using |
| **Sphinx** | 6/15 | ❌ Traditional — MkDocs is better for us |
| **pyright** | 5/15 | ✅ Best strict checking — use alongside mypy |
| **uv** | 4/15 | ✅ Fastest, growing fast — must adopt |
| **codecov** | 5/15 | ✅ Standard coverage tracking — adopt |
| **towncrier** | 3/15 | 🔶 Optional — structured changelogs |

### Layout Comparison

| Layout | Used By | Recommendation |
|---|---|---|
| **src/ layout** | sectionproperties, COMPAS, pytest | ✅ **Use for library** — prevents import confusion |
| Flat layout | numpy, pandas, httpx, rich | OK for frameworks, not ideal for libraries |
| Monorepo | polars, ruff | Only if Rust core needed |

---

## Key Takeaways

1. **sectionproperties is our closest peer** — same domain, same scale, modern tooling. Model our library after it.
2. **src/ layout is standard for libraries** — used by pytest, sectionproperties, COMPAS. Prevents the "import from source instead of installed package" bug.
3. **hatchling is ideal for pure Python** — simple, modern, fast. No compilation step needed.
4. **ruff replaces 4 tools** — flake8 + black + isort + pyupgrade → just ruff. Universal adoption (12/15).
5. **uv is the clear winner** for package management — 82.8k stars, 10-100x faster than pip.
6. **Trusted Publishers for PyPI** — zero secrets, OIDC-based auth. Used by all modern libraries.
7. **Ban relative imports** (Polars pattern) — enforces clean module boundaries.
8. **pytest is the gold standard** for quality toolchain — 8 tools in CI. Aspire to this.
9. **Rich proves simplicity works** — 56k stars with minimal tooling. Don't over-engineer.
10. **PyNite shows what NOT to do** — no types, no CI, legacy setup.py. We must be the opposite.

---

## Deep Dive: pyproject.toml Configuration Comparison

Detailed analysis of how top libraries configure their build, lint, type-checking, and testing tools.

### pytest

- **Build:** setuptools + setuptools-scm (version from git tags)
- **Ruff:** 17 rule categories — `E, W, F, I, UP, B, C4, PIE, SIM, PYI, Q, RET, SLF, T10, T20, TID, ARG`
- **mypy:** Strict-ish with 12 explicit flags (not `strict = true`, but most strict flags individually enabled)
- **Docstrings:** pep257 convention
- **Unique:** `towncrier` with 11 changelog fragment types (breaking, deprecation, improvement, bugfix, vendor, doc, trivial, feature, improvement, bugfix, doc)
- **Note:** setuptools-scm is legacy for their project — for new pure-Python libraries, hatch-vcs is the modern equivalent

### pydantic

- **Build:** hatchling + hatch-fancy-pypi-readme (generates rich PyPI README from docs)
- **Ruff:** 14 rule categories — `E, F, I, D (google), UP, B, C4, PIE, SIM, T20, RUF, Q, W, ANN`
- **Line length:** 120
- **Docstrings:** Google convention
- **Type checking:** 3 type checkers in CI (mypy + pyright + pyrefly)
- **Package management:** uv workspace (manages pydantic + pydantic-core + pydantic-settings)
- **Unique:** PGO (Profile-Guided Optimization) builds for pydantic-core Rust extension

### polars

- **Build:** maturin (Rust → Python bindings)
- **Ruff:** 25 rule categories (MOST comprehensive of any library surveyed):
  `A, ARG, B, C4, COM, D, DTZ, E, EM, ERA, EXE, F, FA, FBT, I, ICN, ISC, N, PD, PGH, PIE, PLC, PLE, PLW, Q, RET, RSE, RUF, S, SIM, SLF, TCH, TD, TID, TRY, UP, W, YTT`
- **Key config:** `ban-relative-imports = "all"` (enforces absolute imports everywhere)
- **Coverage:** `fail_under = 85` in coverage config
- **pytest:** `strict_markers = true`
- **Docstrings:** numpy convention
- **Unique:** flake8-type-checking with `strict = true` — moves imports to `TYPE_CHECKING` blocks aggressively

### sectionproperties ⭐ (Closest Peer)

- **Build:** hatchling (pure Python, no plugins beyond hatch-vcs)
- **Dependency groups:** PEP 735 `[dependency-groups]` — `dev`, `test`, `docs` properly separated
- **Type checking:** pyright with `strict = ["src"]`
- **Testing:** pytest-check (soft assertions), pytest-benchmark with `[histogram]` extra
- **Package management:** uv + ReadTheDocs integration
- **Academic:** JOSS paper, CITATION.cff
- **CI:** 4 workflows (test, docs, publish, label) — cleanest setup of all surveyed
- **Unique:** nbstripout for stripping Jupyter notebook output from version control

### httpx

- **Build:** hatchling + hatch-fancy-pypi-readme
- **Ruff:** Minimal — only 5 rule sets: `E, F, I, B, PIE`
- **mypy:** `strict = true`
- **Scripts directory:** Standalone test/validation scripts (not integrated into CI)
- **CI:** 2 workflows only (test + publish) — most minimal setup
- **Unique:** Proves you don't need complex tooling for a successful library

---

## Deep Dive: CI/CD Pattern Comparison

| Library | Workflows | Test Matrix | Trusted Publishing | Changelog |
|---------|-----------|-------------|-------------------|-----------|
| **pytest** | 6 | 3 OS × 6 Python | Yes (OIDC) | towncrier (11 fragment types) |
| **pydantic** | 9 | 3 OS × 8 Python + pypy + ARM | Yes (OIDC) | Manual |
| **polars** | 18 | 2 OS × 5 Python | N/A (maturin) | release-drafter |
| **sectionproperties** | 4 | 3 OS × 4 Python | Yes (OIDC) | release-drafter |
| **httpx** | 2 | 1 OS × 5 Python | No (token) | Manual |
| **FastAPI** | 5 | 1 OS × 6 Python | Yes (OIDC) | Manual |
| **Django** | 4 | 3 OS × 6 Python | Yes (OIDC) | — (release notes) |
| **Rich** | 2 | 1 OS × 5 Python | No (token) | Manual |

**Our recommendation:** 4 workflows (test, publish, docs, label) — follows sectionproperties pattern. Add `re-actors/alls-green` as a check job.

### Key CI Patterns to Adopt

1. **`re-actors/alls-green`** — Single required status check that passes only when ALL matrix jobs pass. Used by pydantic, FastAPI.
2. **`cancel-in-progress: true`** — Cancel outdated CI runs when new pushes arrive. Universal best practice.
3. **`salsify/action-detect-and-tag-new-version`** — Auto-tag from `pyproject.toml` version changes (sectionproperties pattern).
4. **Auto TestPyPI on pushes** — sectionproperties publishes to TestPyPI on every non-tagged main push for continuous validation.

---

## Deep Dive: Pre-commit Hook Comparison

| Library | Total Hooks | Unique Hooks |
|---------|-------------|-------------|
| **pytest** | 12+ | zizmor (GitHub Actions security), pyproject-fmt (format toml), blacken-docs, custom changelog validation |
| **pydantic** | 9 | markdownlint-cli2, yamlfmt, no-commit-to-branch |
| **polars** | N/A | CI-only linting (no pre-commit) |
| **sectionproperties** | 6 | nbstripout (strip Jupyter output) |
| **httpx** | 0 | No pre-commit at all |
| **Django** | 4 | blacken-docs, pyproject-fmt |
| **Rich** | 3 | Standard (ruff, check-yaml) |

**Our recommendation:** 7 hooks — ruff (lint + format), mypy, codespell, check-yaml, check-toml, end-of-file-fixer, trailing-whitespace. Add zizmor if using GitHub Actions extensively.

### What is zizmor?

`zizmor` is a security linter for GitHub Actions workflows. It catches:
- Untrusted input injection (`${{ github.event.pull_request.title }}`)
- Missing `permissions` settings
- Unpinned action versions
- Known-vulnerable action patterns

Used by pytest — worth adding to our pre-commit config since we rely heavily on GitHub Actions.

---

## Structural Engineering Libraries — Deep Dive

### sectionproperties ⭐ (Best Reference for Our Project)

| Aspect | Detail |
|--------|--------|
| **Pattern** | Class pipeline: `Section() → .mesh() → .solve() → .results()` |
| **API design** | Builder pattern with `SectionProperties` dataclass as result |
| **Validation** | BibTeX-cited validation against known analytical solutions |
| **Testing** | pytest-check for soft assertions, pytest-benchmark for performance |
| **Academic** | JOSS paper provides citable DOI |
| **Key insight** | Cleanest build/CI of any structural engineering library |

### structuralcodes (Multi-Code Architecture)

| Aspect | Detail |
|--------|--------|
| **Pattern** | Multi-code: `codes/` → `materials/` → `sections/` directory structure |
| **API design** | `set_design_code("is456")` then call generic functions |
| **Clause referencing** | Each function has `@clause("IS 456:2000", "38.1")` decorator |
| **Materials** | `CONCRETES` registry with pre-defined grades |
| **Key insight** | Best model for multi-code support if we ever add ACI 318 / Eurocode 2 |

### PyNite (What NOT to Do)

| Aspect | Detail |
|--------|--------|
| **Pattern** | Model builder: `model.add_member()`, `model.analyze()` |
| **Unique** | `Derivations/` folder with PDF derivations of FEA theory |
| **Load combos** | Built-in load combination support |
| **Warning** | No modern tooling — legacy setup.py, no types, no CI, no pre-commit |

### OpenSeesPy (Anti-Pattern for Python API)

| Aspect | Detail |
|--------|--------|
| **Pattern** | Command-driven: `ops.node(1, 0.0, 0.0)`, `ops.element('truss', 1, 1, 2)` |
| **Materials** | 40+ material models |
| **Warning** | Anti-pattern for Python — imperative state machine, not Pythonic at all |

### COMPAS (Plugin Architecture)

| Aspect | Detail |
|--------|--------|
| **Pattern** | Plugin architecture: core + extensions (`compas_fea`, `compas_timber`) |
| **Unique** | Tolerance module for numerical precision management |
| **Model** | Core package + separate packages for CAD integration |
| **Key insight** | Best model for extensibility — if we add `rcdesign-fea` or `rcdesign-timber` later |

### anaStruct (Simplest API)

| Aspect | Detail |
|--------|--------|
| **Stars** | 441 |
| **Pattern** | Simplest API of any structural library: `ss.add_element()`, `ss.solve()`, `ss.show_structure()` |
| **Unique** | `show_*` methods for integrated visualization |
| **Key insight** | Proves demand for simple, accessible structural engineering tools |

---

## What's Missing From ALL Libraries (Our Blue Ocean)

No existing Python library offers ANY of these capabilities — this is our unique value proposition:

| # | Gap | Status | Impact |
|---|-----|--------|--------|
| 1 | **No IS 456 support anywhere** | We're the only one | Blue ocean — zero competition |
| 2 | **No integrated design workflow** (loads → code check → rebar → drawings) | Our design_beam() does this | Unique selling point |
| 3 | **No ETABS/STAAD import** | Our GenericCSVAdapter (app repo) | Bridges analysis → design gap |
| 4 | **No BBS generation** (bar bending schedule math) | Our common/bbs.py | Critical for Indian practice |
| 5 | **No 3D rebar visualization** | Our beam_to_3d_geometry (app repo) | Visual verification |
| 6 | **No real-time design feedback** | Our WebSocket live design (app repo) | Interactive design |
| 7 | **No detailing output** (spacing, cover, curtailment) | Our detail_beam() | Complete design package |
| 8 | **No design report generation** | Our reports module (app repo) | Professional deliverables |
| 9 | **No multi-format export** (DXF) | Our dxf_export (app repo) | CAD integration |
| 10 | **No accessibility for non-FEA users** | Our simplified API | Practicing engineers, not just researchers |

**Strategic implication:** The library doesn't need to compete with FEA tools. It occupies a completely uncontested niche: **IS 456 design code compliance for practicing Indian engineers.**

---

## Deep-Dive: pyproject.toml Analysis (Top 5)

### pytest (Gold Standard Quality)
- **Build:** setuptools + setuptools-scm (git tag versioning)
- **Ruff:** 17 rule categories (B, D, E, F, FA100, I, PGH004, PIE, PLC/PLE/PLR/PLW, PYI, RUF, T100, UP, W)
- **Mypy:** strict-ish (12 individual flags, not `strict = true`)
- **Pyright:** basic mode
- **Docstrings:** pep257 convention
- **Unique:** towncrier changelog (11 fragment types), zizmor (GitHub Actions linter), pyproject-fmt, check-wheel-contents, custom pygrep hooks
- **Pre-commit hooks:** 12+ including zizmor, blacken-docs, codespell, mypy, pyright (manual), pylint (manual)

### pydantic (Modern Python Leader)
- **Build:** hatchling + hatch-fancy-pypi-readme
- **Ruff:** 14 categories (F, E, I, D, UP, YTT, B, T10, T20, C4, PERF, PIE, PYI specific rules), line-length=120, Google docstrings, single quotes
- **Type checking:** 3 checkers — mypy + pyright + pyrefly (pyrefly = Meta OSS)
- **Testing:** pytest-benchmark + CodSpeed + pytest-memray (memory profiling) + pytest-run-parallel + pytest-examples
- **Docs:** MkDocs Material with mkdocs-llmstxt (AI-friendly llms.txt generation)
- **CI:** 9 workflows, Python 3.9–3.14 + 3.14t (free-threaded) + pypy3.11
- **Unique:** uv workspace (pydantic-core as member), PGO-optimized builds, WASM/Emscripten build, automated tweet on release

### polars (Most Comprehensive Ruff)
- **Ruff:** 25 rule categories — the most comprehensive of any library
  - Includes ANN (type annotations), ARG (unused args), EM (error messages), FBT001 (boolean trap), PT (pytest style), PTH (pathlib), SIM (simplify), TCH (type checking), TD (todos), TID (tidy imports), TRY (exception handling)
  - **`ban-relative-imports = "all"`** — forces absolute imports everywhere
  - **`flake8-type-checking.strict = true`** — enforces TYPE_CHECKING imports
  - **`fail_under = 85`** — hard coverage minimum in config
- **Mypy:** `strict = true` (full strict mode)
- **Pytest:** 13 custom markers, `xfail_strict = true`, `strict_config = true`, `strict_markers = true`
- **CI:** 18 workflow files — most granular of any library
- **Unique:** morsel size matrix testing, import test without dependencies (graceful degradation), ARM64 Windows builds

### sectionproperties (Our Closest Peer)
- **Build:** hatchling (static version, not dynamic)
- **Deps:** PEP 735 dependency-groups (dev, docs, lint, test)
- **Pyright:** `strict = ["src"]` — full strict on source
- **Testing:** pytest-check (non-short-circuiting assertions), pytest-benchmark[histogram]
- **CI:** 4 workflows — the CLEANEST, simplest setup
- **Pre-commit:** nbstripout (strip notebook outputs), ruff, standard hooks
- **Release:** Auto TestPyPI on every non-tagged push, auto-detect version changes
- **Docs:** Sphinx + Furo + ReadTheDocs (with uv)
- **Unique:** JOSS paper in CITATION.cff, macos-15-intel testing

### httpx (Cleanest Minimal Template)
- **Build:** hatchling + hatch-fancy-pypi-readme
- **Ruff:** Just 5 rules: E, F, I, B, PIE — deliberately minimal
- **Mypy:** `strict = true` with test override
- **CI:** 2 workflow files — absolute minimum
- **Pre-commit:** None (CI-only checks)
- **Unique:** scripts/ directory pattern (all CI actions are shell scripts), `copied_from` test marker

## Deep-Dive: CI Pattern Comparison

| Feature | pytest | pydantic | polars | sectionproperties | httpx | **Our Plan** |
|---------|--------|----------|--------|-------------------|-------|-------------|
| Workflows | 6 | 9 | 18 | **4** ✅ | 2 | **4** |
| OS matrix | 3 | 3+ARM | 2 | **3+intel** | 1 | **3** |
| Python versions | 3.10–3.14+pypy | 3.9–3.14+3.14t+pypy | 3.10–3.14+3.14t | 3.11–3.14 | 3.9–3.13 | **3.11–3.13** |
| Trusted Publishing | ✅ | ✅ | N/A | ✅ | ❌ (token) | **✅** |
| Changelog | towncrier | manual | release-drafter | release-drafter | manual | **towncrier** |
| Auto TestPyPI | ❌ | ❌ | ❌ | **✅** | ❌ | **✅** |
| Coverage gate | CI | CI | **85% config** | CI+Codecov | script | **95% config** |
| alls-green gate | ✅ | ✅ | ❌ | ❌ | ❌ | **✅** |

## Deep-Dive: Pre-commit Comparison

| Library | Hooks | Notable Unique Hooks |
|---------|-------|---------------------|
| pytest | 12+ | zizmor, pyproject-fmt, blacken-docs, custom changelog validators |
| pydantic | 9 | markdownlint-cli2, yamlfmt, no-commit-to-branch |
| polars | 0 | CI-only (no pre-commit at all) |
| sectionproperties | 6 | nbstripout |
| httpx | 0 | No pre-commit |
| **Our Plan** | **7** | zizmor, nbstripout, sp-repo-review, codespell |

## Deep-Dive: Structural Engineering Libraries

### sectionproperties — Pipeline Pattern
- Class pipeline: `Geometry` → `create_mesh()` → `Section(geometry)` → `calculate_*()` → `get_*()`/`plot_*()`
- Each stage validates prerequisites (RuntimeError if prior stage not run)
- Results in `SectionProperties` **dataclass** with `.asdict()` method
- **Validation suite**: dedicated `tests/validation/` with textbook problems (Peery, Pilkey) — BibTeX-cited
- **Non-short-circuiting assertions** via `pytest_check` — all checks run even if one fails
- **Benchmarks**: parametrized by element count (50, 500, 5000), `--benchmark-histogram`

### structuralcodes (fib International) — Multi-Code Architecture
- Three-layer hierarchy: code equations → material classes → sections
- **`set_design_code('ec2_2004')`** — global switch, all factories return correct implementation
- **Factory pattern**: `create_concrete(fck=45)` returns code-specific class
- **CONCRETES registry**: `{'fib Model Code 2010': ConcreteMC2010, 'EUROCODE 2': ConcreteEC2_2004, ...}`
- **Every function docstring** cites exact code clause: `"EN 1992-1-1:2023, Eq. (5.3)"`
- **Constitutive laws**: materials embed laws via string or object
- **Code metadata**: `__title__`, `__year__`, `__materials__` per code module

### Pynite — Model Builder + Derivations
- Model builder pattern: `FEModel3D()` → `add_node()` → `add_member()` → `analyze()` → results
- **Unique: `Derivations/` folder** with mathematical proofs alongside code (with images!)
- Load case / load combination system
- PDF report generation built-in

### OpenSeesPy — Anti-Pattern
- Command-driven API (Tcl heritage): `ops.model('basic', '-ndm', 2, '-ndf', 3)`
- Tag-based object referencing (integer IDs) — error-prone
- 40+ uniaxial materials (aspirational coverage)
- **What to avoid**: unfriendly API, silent failures, no modern Python packaging

### COMPAS — Plugin Architecture
- Core + extensions model: `compas` (core) + `compas_fea2`, `compas_timber` (separate repos)
- Plugin system via `compas.plugins` module
- `compas.tolerance` module for floating-point handling
- Scene-based visualization pattern

### anaStruct — Simplicity Wins
- 441 stars with the SIMPLEST API: `SystemElements()` → `add_element()` → `solve()` → `show_*()`
- `show_*` methods for instant visualization
- Steel section databases (EU, US, UK) — **we should add IS 808 (Indian)**

## What's Missing From ALL Libraries (Our Blue Ocean)

| Gap | Libraries Affected | Our Advantage |
|-----|-------------------|---------------|
| IS 456 implementation | ALL (zero on PyPI) | Only IS 456 library on PyPI |
| Integrated design workflow | ALL | Loads → code check → rebar → drawings |
| ETABS/STAAD import | ALL | CSV adapter for real-world workflow |
| Bar Bending Schedule | ALL | BBS generation + export |
| 3D rebar visualization | ALL | R3F 3D bar placement |
| Real-time design feedback | ALL | WebSocket live updates |
| Detailing output | ALL | Development length, spacing, cover checks |
| Design calculation reports | ALL | Stampable reports for engineers |
| Multi-format export (DXF) | ALL | CAD integration |
| Non-FEA accessibility | sectionproperties, OpenSeesPy, COMPAS | Usable by any civil engineer |

---
