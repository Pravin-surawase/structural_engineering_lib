---
Type: Research
Audience: All Agents
Status: Active
Importance: Critical
Created: 2026-04-08
Last Updated: 2026-04-08
---

# 2026 Python Toolchain Report — Best-in-Class Tools for a Structural Engineering Library

**Research Method:** Primary web research across 20+ official repositories and documentation sites, April 2026.
**Scope:** Build/package, type checking, testing, documentation, CI/CD, architecture enforcement, numerical computing, code quality, AI agent tooling.

---

## 1. Build & Package — Best Stack for April 2026

### Winner: **uv** (Astral)

| Attribute | Value |
|-----------|-------|
| **Version** | **0.11.3** (released 2026-04-01) |
| **Stars** | 55k+ |
| **Written in** | Rust |
| **License** | MIT / Apache 2.0 |

**Why uv dominates in 2026:**

- **`uv audit`** (preview): Vulnerability scanning with `--ignore` and `--ignore-until-fixed` flags — replaces `pip-audit` and `safety`
- **PEP 803 support**: Latest packaging standards
- **Workspace metadata**: Dependency info from lockfile
- **SBOM attestations**: Docker images include Software Bill of Materials via GitHub Artifact Attestations (supply chain security)
- **Python version management**: Supports Python 3.6–3.15+, installs interpreters automatically
- **Progress bar** for `uv publish`
- **ROCm 7.2 + CUDA** support for GPU-heavy scientific computing
- **v0.11.0 breaking change**: Switched to `rustls-platform-verifier` (aws-lc crypto backend); `--native-tls` deprecated in favor of `--system-certs`

**Recommended `pyproject.toml` build stack:**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
requires-python = ">=3.10"
```

**What to use uv for:**
- Package management (`uv add`, `uv remove`, `uv sync`)
- Virtual environments (`uv venv`)
- Publishing (`uv publish`)
- Security audits (`uv audit`)
- Python version management (`uv python install 3.14`)
- Running tools (`uvx ruff check`, `uvx ty check`)

### Alternative: pixi (prefix.dev)

Conda-based package manager for polyglot projects. Useful if you need C/Fortran scientific libraries (LAPACK, BLAS) that conda handles better than pip. Not recommended as primary — use uv unless you have hard conda dependencies.

### Build backend: Hatchling

Preferred over setuptools for new projects. Fastest, most modern, used by the Astral ecosystem.

---

## 2. Type Checking — Recommended Type Checker Combination

### The Big 4 in April 2026

| Tool | Version | Stars | Speed | Maturity | Our Recommendation |
|------|---------|-------|-------|----------|-------------------|
| **ty** (Astral) | **0.0.29** | 18.2k | 10-100x faster than mypy | **Beta** | ⭐ Watch closely, adopt when stable |
| **Pyrefly** (Meta/Facebook) | **0.60.0** | 5.6k | Very fast (Rust) | Active dev, known issues | Experimental — evaluate |
| **basedpyright** | **v1.39.0** (pyright 1.1.408) | 3.3k | Fast | Stable fork | ⭐ **Use NOW** as primary |
| **mypy** | 1.14+ | 19k+ | Slow | Mature, standard | Keep for CI backup |

### Recommended Strategy (April 2026)

```
PRIMARY:     basedpyright (stable, fast, excellent VS Code integration)
CI:          basedpyright + mypy (belt-and-suspenders)
WATCH:       ty (Astral) — when it exits beta (likely H2 2026), migrate to ty
EXPERIMENT:  Pyrefly — interesting but too early for production
```

**Why basedpyright over vanilla pyright:**
- Fork of pyright with "various type checking improvements"
- Better VS Code support with pylance features built into the language server
- Uses uv for dependency management
- Pinned to Python 3.14
- 3.3k stars, 191 contributors, actively maintained

**Why ty is the future:**
- From Astral (makers of uv and Ruff) — same team, same ecosystem
- 10-100x faster than mypy and Pyright
- Comprehensive diagnostics with rich contextual info
- Configurable rule levels, per-file overrides, suppression comments
- Full language server: completions, code actions, auto-import, inlay hints
- Fine-grained incremental analysis
- VS Code, PyCharm, Neovim integrations
- **BUT**: Currently v0.0.x with `0.0.x` versioning — "breaking changes may occur between any two versions"
- 18.2k stars already in beta — massive community interest

**Why Pyrefly is interesting but too early:**
- Facebook/Meta team, MIT license, written in Rust
- Module-level incrementality + parallelism
- Type inference (except function params), flow types
- v0.60.0 but "active development with known issues"
- mutmut already integrates with it for type-checked mutation filtering

---

## 3. Testing — Best Testing Stack and Innovations

### Core: pytest 9.0.3 (released 2026-04-07)

Major pytest 9.0 features that matter for us:

| Feature | Impact for Structural Lib |
|---------|--------------------------|
| **Built-in subtests** (#1367) | Test multiple IS 456 parameters in one test, get per-subcase reporting |
| **Native TOML config** (`[tool.pytest]`) | Consolidate all config in `pyproject.toml` |
| **`pytest.RaisesGroup`** | Test ExceptionGroup errors (Python 3.11+) |
| **Strict mode** (`strict = true`) | Enables strict_config, strict_markers, strict_parametrization_ids, strict_xfail — catches sloppy tests |
| **`capteesys` fixture** | Capture AND see output simultaneously (great for debugging) |
| **PEP 657 traceback support** | Better error messages with fine-grained location info |
| **Dropped Python 3.9** | We can use 3.10+ features freely |

### Snapshot Testing: inline-snapshot v0.32.5

| Attribute | Value |
|-----------|-------|
| **Stars** | 720 |
| **Why it matters** | Auto-generate and auto-update expected values in tests |

Key features:
- `snapshot()` function that auto-fills expected values on first run
- Normal assertion support: `assert 1+1 == snapshot()` → auto-fills `snapshot(2)`
- `@Customize` decorator for custom comparison
- `dirty-equals` integration
- `--inline-snapshot=review` for interactive review of changes
- **Perfect for structural engineering**: Run `design_beam_is456()`, capture result as snapshot, auto-detect regressions

### Property-Based Testing: Hypothesis v6.151.11

Essential for structural engineering — generates random valid inputs to find edge cases:
- Test beam design with random (but valid) dimensions, loads, materials
- Find the boundary cases where IS 456 formulas break or produce unexpected results
- `@given(st.floats(min_value=150, max_value=1500))` for beam width, etc.
- **Mature** (6.x line), extensive docs, reorganized into Tutorial/How-to/Explanations/API format

### Mutation Testing: mutmut 3.x

| Attribute | Value |
|-----------|-------|
| **Stars** | 1.3k |
| **Contributors** | 40 |

mutmut 3.x (current) highlights:
- **Parallel execution** — essential for our 500+ test suite
- **Interactive TUI** with `mutmut browse` — visual mutant exploration
- **Type checker filtering** — integrates with mypy and Pyrefly to filter invalid mutants (e.g., `x: str = None` caught by type checker)
- **Wildcard support**: `mutmut run "my_module*"` — test just IS 456 modules
- **Coverage.py integration**: Only mutate covered lines (`mutate_only_covered_lines=true`)
- **Stack depth limiting**: `max_stack_depth=8` to avoid testing incidental code paths
- **Pragma controls**: `# pragma: no mutate`, `# pragma: no mutate block`, `# pragma: no mutate start/end`
- Works on macOS (with `setproctitle` auto-disabled for fork safety)

**Recommendation:** Add mutation testing for critical IS 456 math modules. These are life-safety calculations — mutation testing proves tests catch real bugs.

### Benchmarking: pytest-codspeed v4.3.0

| Attribute | Value |
|-----------|-------|
| **Stars** | 122 |
| **Modes** | Simulation (deterministic) + Walltime |

- `@pytest.mark.benchmark` decorator or `benchmark` fixture
- Local mode with `--codspeed` flag shows rich table output
- CI integration with `CodSpeedHQ/action@v4` for PR regression detection
- **Use case**: Benchmark `design_beam_is456()` performance, catch regressions when adding new features

### Recommended Test Stack

```
pytest 9.0.3          — Core test runner (strict mode ON)
inline-snapshot 0.32  — Snapshot testing for design results
hypothesis 6.151      — Property-based testing for edge cases
mutmut 3.x            — Mutation testing for IS 456 math (safety-critical)
pytest-codspeed 4.3   — Performance benchmarking
coverage.py           — Branch coverage (85%+ target)
```

---

## 4. Documentation — Best Docs Stack

### MkDocs Material v9.7.6

| Attribute | Value |
|-----------|-------|
| **Stars** | 26.5k |
| **Status** | Dominant documentation framework for Python |

Key features:
- Built-in search
- Code annotations (essential for showing IS 456 formulas alongside code)
- Social cards (auto-generated)
- 10,000+ icons
- Blog support
- Privacy plugin
- Projects plugin (multi-project docs)
- **Math support** — critical for structural engineering formulas
- Typeset plugin for beautiful typography

### mkdocstrings v1.0.3

| Attribute | Value |
|-----------|-------|
| **Stars** | 2k+ |
| **Status** | v1.0 stable release — language-agnostic |

Key features:
- **Cross-references** across pages and sites (like Sphinx intersphinx) — link IS 456 functions across docs
- Inline injection in Markdown — embed docstrings directly
- Python handler with full autodoc support
- Used by FastAPI, Pydantic, Textual, NVIDIA, Microsoft, Google

### mkdocs-llmstxt

Plugin to generate `llms.txt` for AI agent consumption. We already have `llms.txt` — ensure it stays current.

### Recommended Docs Stack

```
mkdocs-material 9.7   — Theme and framework
mkdocstrings 1.0      — Auto-generated API docs from docstrings
mkdocs-llmstxt         — AI-friendly docs
KaTeX/MathJax          — Formula rendering (prefer KaTeX for speed)
```

---

## 5. CI/CD — Latest Patterns and Tools

### GitHub Actions: setup-uv v8.0.0

| Feature | Benefit |
|---------|---------|
| Automatic version detection | Reads uv version from `uv.toml` or `pyproject.toml` |
| Cache support | Auto-enabled on GitHub-hosted runners |
| Python version matrix | `uv python install 3.10 3.11 3.12 3.13 3.14` |
| venv activation | Automatic |
| Checksum verification | Supply chain security |
| Problem matchers | Rich error annotations in PR |

### Recommended CI Pipeline

```yaml
name: CI
on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13", "3.14"]
    steps:
      - uses: actions/checkout@v5
      - uses: astral-sh/setup-uv@v8
      - run: uv python install ${{ matrix.python-version }}
      - run: uv sync --dev
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uv run basedpyright
      - run: uv run pytest --strict -v
      - run: uv run deptry .
      - run: uv audit
```

### Supply Chain Security

- **uv audit**: Built-in vulnerability scanning (replaces `pip-audit`, `safety`)
- **SBOM attestations**: GitHub Artifact Attestations on Docker images
- **Sigstore**: Sign releases — becoming standard for open-source Python packages
- **Trusted publishers**: PyPI trusted publishing with GitHub Actions (no API tokens)

### Coverage

- **codecov** remains the standard (vs coveralls). Better GitHub integration, PR annotations, coverage diff tracking.

---

## 6. Architecture Enforcement — Best Boundary Checking Tools

### tach v0.34.1 (gauge-sh → tach-org)

| Attribute | Value |
|-----------|-------|
| **Stars** | 2.7k |
| **Contributors** | 28 |
| **Written in** | Rust + Python |
| **Status** | Actively developing, moved to `tach-org/tach` |

Key features:
- **Module boundary enforcement** via `tach.toml` — prevents upward imports in our 4-layer architecture
- **Dependency graph visualization**: `tach show --web` — interactive web-based graph
- **Public interfaces**: Declare what's public from each module
- **Deprecating dependencies**: Mark cross-module imports as deprecated (migrate gradually)
- **Layered architecture support**: Exactly what we need for Core → IS 456 → Services → UI
- **Incremental adoption**: Add boundaries module by module
- **JSON dependency maps**: Machine-readable for AI agents
- **VS Code extension** available
- **basedpyright integration**
- **Pre-commit hooks**
- **Inline ignore comments**: `# tach-ignore` for exceptions

**This is exactly what our library needs** — enforcing that `core/` never imports from `services/`, etc.

### Alternative: import-linter

More established but slower (pure Python). tach is faster (Rust) and has better visualization.

### Recommendation

Adopt tach immediately:

```toml
# tach.toml
[[modules]]
path = "Python.structural_lib.core"
depends_on = []  # Core depends on nothing

[[modules]]
path = "Python.structural_lib.codes"
depends_on = ["Python.structural_lib.core"]

[[modules]]
path = "Python.structural_lib.services"
depends_on = ["Python.structural_lib.core", "Python.structural_lib.codes"]

[[modules]]
path = "fastapi_app"
depends_on = ["Python.structural_lib"]

[[modules]]
path = "react_app"
depends_on = []  # Frontend can't import Python
```

---

## 7. Numerical Computing — Algorithms and Precision

### For Structural Engineering Specifically

| Library | Use Case | Recommendation |
|---------|----------|---------------|
| **NumPy 2.x** | Array operations, stress block computation | ✅ Continue using — mature, fast, universal |
| **SciPy** | Optimization (`minimize`), root finding, interpolation | ✅ Use for optimization (cost/carbon) |
| **Python `decimal`** | Exact arithmetic (when you need 0.1 + 0.2 = 0.3 exactly) | ⚠️ Only for money/reporting, NOT for structural math |
| **Pure Python `float`** | IS 456 formula computation | ✅ Correct for engineering (IEEE 754 double: 15-16 sig figs) |
| **mpmath** | Arbitrary precision when needed | ⚠️ Rarely needed — research only |

### Key Insight: Ruff Rule RUF069

Ruff 0.15.9 includes **RUF069: float equality comparison** — detects `if x == 0.0` which is a common engineering bug. **Enable this rule immediately** for our IS 456 math modules.

### Optimization for Structural Design

| Library | Version | Use Case |
|---------|---------|----------|
| `scipy.optimize` | SciPy 1.14+ | Single-objective: minimize cost, minimize carbon |
| `pymoo` | 0.6+ | Multi-objective Pareto optimization (cost vs carbon vs utilization) |
| `optuna` | 4.x | Hyperparameter-style search for design parameters |

### Precision Guidelines for Structural Engineering

```python
# ✅ CORRECT: Use relative tolerance for float comparison
import math
assert math.isclose(Ast_provided, Ast_required, rel_tol=1e-6)

# ✅ CORRECT: Use >= for capacity checks (conservative)
assert capacity >= demand  # Never exact equality

# ❌ WRONG: Exact float comparison
assert Ast == 1256.637  # Fails due to floating point

# ❌ WRONG: Using Decimal for structural math (slow, unnecessary)
from decimal import Decimal
Mu = Decimal("150.5")  # Overkill — IEEE 754 is more than sufficient
```

---

## 8. Code Quality — Full Tool List with Versions

### Tier 1: Must-Have (Run on Every Commit)

| Tool | Version | Purpose | Notes |
|------|---------|---------|-------|
| **Ruff** | **0.15.9** | Linting + formatting (replaces flake8, isort, black, bandit, pyupgrade) | 900+ rules, preview mode for expanded defaults |
| **basedpyright** | **v1.39.0** | Type checking | Primary type checker |
| **pytest** | **9.0.3** | Testing | Strict mode ON |
| **deptry** | **0.25.1** | Unused/missing dependency detection | Rust-powered, fast. Codes: DEP001-DEP004 |
| **uv audit** | **0.11.3** | Vulnerability scanning | Replaces pip-audit, safety |

### Tier 2: Should-Have (Run in CI)

| Tool | Version | Purpose | Notes |
|------|---------|---------|-------|
| **vulture** | **v2.16** | Dead code detection | 4.4k stars, MIT. Use `--min-confidence 80` |
| **tach** | **v0.34.1** | Architecture boundary enforcement | Rust, module dependencies |
| **pydoclint** | **v0.8.3** | Docstring linting | 1000x faster than darglint. Supports numpy/google/sphinx styles |
| **codespell** | **2.4+** | Spell checking in code | Fast, low false positives |
| **pyproject-fmt** | **2.x** | Normalize pyproject.toml formatting | Consistent config formatting |
| **check-wheel-contents** | latest | Verify wheel packaging | Catches missing files before PyPI publish |

### Tier 3: Nice-to-Have (Run Periodically)

| Tool | Version | Purpose | Notes |
|------|---------|---------|-------|
| **mutmut** | **3.x** | Mutation testing | Run on critical IS 456 modules monthly |
| **pytest-codspeed** | **v4.3.0** | Performance benchmarking | Track regressions in CI |
| **cyclonedx-python** | 7.x+ | SBOM generation (CycloneDX format) | Supply chain compliance |

### Ruff Configuration Highlights for Structural Engineering

```toml
[tool.ruff]
target-version = "py310"
line-length = 120

[tool.ruff.lint]
select = [
    "E", "W",      # pycodestyle
    "F",            # pyflakes
    "I",            # isort
    "UP",           # pyupgrade (UP050 rules)
    "B",            # flake8-bugbear (B911, B912)
    "S",            # flake8-bandit (security)
    "C4",           # flake8-comprehensions
    "SIM",          # flake8-simplify
    "TC",           # flake8-type-checking
    "RUF",          # Ruff-specific (RUF069 float equality!)
    "FURB",         # refurb (FURB192)
    "DOC",          # pydoclint rules
    "ASYNC",        # async rules
    "FAST",         # FastAPI rules
]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]  # Allow assert in tests
"Python/structural_lib/codes/**" = ["RUF069"]  # Float comparison OK in math (with isclose)
```

### Key New Ruff Rules to Enable

| Rule | Description | Why It Matters |
|------|-------------|----------------|
| **RUF069** | Float equality comparison | Catches `if x == 0.0` in engineering code |
| **RUF066** | Property without return | Catches property methods that forget to return |
| **RUF055** | Unnecessary regex | Performance: use `str.replace()` instead |
| **B911/B912** | Bugbear improvements | Catches subtle bugs |
| **DOC*** | Pydoclint rules | Docstring/signature sync |
| **FAST*** | FastAPI rules | Catches FastAPI anti-patterns |
| **UP050** | Pyupgrade rules | Modern Python syntax |
| **FURB192** | Refurb rules | Code modernization |

---

## 9. Key Recommendations — Top 10 Tools/Practices We MUST Adopt

### 🏆 The List (Priority Order)

| # | Action | Tool/Practice | Impact | Effort |
|---|--------|--------------|--------|--------|
| **1** | **Adopt ty when stable** | `ty` (Astral) v0.0.29 → watch for v1.0 | 10-100x faster type checking | S (drop-in) |
| **2** | **Add mutation testing for IS 456 math** | `mutmut 3.x` | Proves test suite catches real bugs in safety-critical code | M |
| **3** | **Enforce architecture with tach** | `tach v0.34.1` | Prevents the #1 codebase issue: layer violations | S |
| **4** | **Enable RUF069 (float equality)** | Ruff 0.15.9 | Catches the most common engineering code bug | S |
| **5** | **Upgrade to pytest 9 strict mode** | pytest 9.0.3 | Catches sloppy tests, enables subtests | S |
| **6** | **Add inline-snapshot testing** | `inline-snapshot 0.32` | Auto-maintain expected design results, catch regressions instantly | M |
| **7** | **Run `uv audit` in CI** | uv 0.11.3 | Built-in vulnerability scanning, replaces 2 tools | S |
| **8** | **Add dead code detection** | `vulture v2.16` + `deptry 0.25.1` | Clean up 104-export API surface, find unused dependencies | S |
| **9** | **Benchmark critical paths** | `pytest-codspeed 4.3` | Catch performance regressions when adding features | M |
| **10** | **Supply chain security** | Sigstore signing + SBOM + trusted publishers | Professional-grade release pipeline | L |

### Quick Wins (< 1 hour each)

1. Enable RUF069 in Ruff config
2. Add `uv audit` to CI pipeline
3. Run `vulture . --min-confidence 80` to find dead code
4. Run `deptry .` to find unused dependencies
5. Switch pytest to strict mode (`strict = true` in pyproject.toml)

---

## 10. What to AVOID — Tools That Are Dying or Overhyped

### ❌ Actively Avoid

| Tool | Status | Replace With |
|------|--------|-------------|
| **black** | Superseded | **Ruff format** — same style, 100x faster, from the same AST |
| **isort** | Superseded | **Ruff** (I rules) — built-in import sorting |
| **flake8** | Superseded | **Ruff** — 900+ rules including all flake8 plugins |
| **bandit** | Superseded | **Ruff** (S rules) — flake8-bandit rules built into Ruff |
| **pyupgrade** | Superseded | **Ruff** (UP rules) — pyupgrade rules built into Ruff |
| **autopep8** | Dead | **Ruff format** |
| **yapf** | Unmaintained | **Ruff format** |
| **darglint/darglint2** | Dead/archived | **pydoclint** (1000x faster) or Ruff DOC rules |
| **pip + pip-tools** | Legacy | **uv** — 10-100x faster, replaces entire pip ecosystem |
| **poetry** | Losing mindshare | **uv** — faster, simpler, better lockfile, growing faster |
| **setuptools** (for new projects) | Legacy | **Hatchling** — modern, fast, PEP 621 native |
| **pip-audit** | Redundant | **uv audit** — built into uv 0.11+ |
| **safety** | Redundant / commercial | **uv audit** — free, built-in |
| **Docker Desktop** (Mac) | Heavy, commercial | **Colima** — lighter, open source (already using) |

### ⚠️ Overhyped / Too Early

| Tool | Status | When to Reconsider |
|------|--------|-------------------|
| **Pyrefly** (Meta) | v0.60.0, "active development with known issues" | When v1.0 ships and has stable API |
| **ty** (Astral) | v0.0.29, beta, "breaking changes may occur" | When it stabilizes (likely H2 2026). **DO watch it.** |
| **pixi** | Good for conda, overkill for pure-Python | Only if we need C/Fortran scientific deps via conda |
| **Maturin** | For Rust+Python packages | Only if we rewrite IS 456 math in Rust (premature) |
| **Rye** | Superseded by uv | Never — uv absorbed Rye's features |

### ⚠️ Use With Caution

| Tool | Caveat |
|------|--------|
| **Hypothesis** | Powerful but can generate nonsensical inputs (negative beam widths). ALWAYS constrain strategies with domain-valid ranges |
| **mutmut** | Can be slow on large codebases. Start with targeted modules (`mutmut run "codes/is456*"`) |
| **AI-generated tests** | Never trust AI-generated expected values for structural engineering. Always verify against hand calculations |

---

## Appendix A: Version Summary Table

| Tool | Current Best Version | Category |
|------|---------------------|----------|
| uv | 0.11.3 | Build & Package |
| Ruff | 0.15.9 | Linting + Formatting |
| ty | 0.0.29 (beta) | Type Checking (future) |
| basedpyright | 1.39.0 | Type Checking (current) |
| Pyrefly | 0.60.0 (experimental) | Type Checking (experimental) |
| mypy | 1.14+ | Type Checking (legacy backup) |
| pytest | 9.0.3 | Testing |
| inline-snapshot | 0.32.5 | Snapshot Testing |
| Hypothesis | 6.151.11 | Property-Based Testing |
| mutmut | 3.x | Mutation Testing |
| pytest-codspeed | 4.3.0 | Benchmarking |
| MkDocs Material | 9.7.6 | Documentation |
| mkdocstrings | 1.0.3 | API Docs |
| setup-uv | 8.0.0 | CI/CD |
| tach | 0.34.1 | Architecture Enforcement |
| vulture | 2.16 | Dead Code Detection |
| deptry | 0.25.1 | Dependency Issues |
| pydoclint | 0.8.3 | Docstring Linting |
| codespell | 2.4+ | Spell Checking |

## Appendix B: AI Agent Tooling (April 2026)

### VS Code Copilot

- Custom agents (`.github/agents/`) — we have 16
- Custom skills (`.github/skills/`) — we have 14
- Custom prompts (`.github/prompts/`) — we have 16
- Model context protocol (MCP) for tool integration
- Agent modes for specialized workflows

### Claude Code / CLAUDE.md

- `CLAUDE.md` file for project-specific instructions (we have this)
- Extended thinking for complex reasoning
- Tool use for code analysis

### Key AI-Agent Patterns

1. **`llms.txt`** — machine-readable project description (we have this)
2. **`AGENTS.md`** — cross-platform agent instructions (we have this)
3. **Folder indexes** (`index.json` + `index.md`) — AI-readable context (we have these)
4. **Session persistence** — state across conversations (we have `session_store.py`)
5. **Prompt routing** — NLP-based task → agent delegation (we have `prompt_router.py`)

**Assessment:** Our AI agent infrastructure is already state-of-the-art. The 16-agent architecture with skills, prompts, and session persistence is among the most sophisticated in any open-source project. Focus on improving agent quality/accuracy rather than adding more infrastructure.

---

## Appendix C: Action Items for structural_engineering_lib

### Immediate (This Week)

- [ ] Enable RUF069 in Ruff config
- [ ] Add `uv audit` to CI
- [ ] Run `vulture . --min-confidence 80` and clean dead code
- [ ] Run `deptry .` and fix dependency issues
- [ ] Upgrade pytest config to strict mode

### Short-Term (This Month)

- [ ] Install and configure tach for 4-layer architecture enforcement
- [ ] Add inline-snapshot tests for key design functions
- [ ] Set up pytest-codspeed benchmarks for `design_beam_is456()`
- [ ] Evaluate basedpyright as primary type checker

### Medium-Term (This Quarter)

- [ ] Add mutation testing for IS 456 math modules
- [ ] Set up Sigstore release signing
- [ ] Implement trusted publisher for PyPI
- [ ] Monitor ty for v1.0 beta exit

### Long-Term (H2 2026)

- [ ] Migrate from basedpyright to ty when stable
- [ ] Evaluate multi-objective optimization with pymoo for generative design
- [ ] Consider Rust extensions for performance-critical math (only if profiling shows need)
