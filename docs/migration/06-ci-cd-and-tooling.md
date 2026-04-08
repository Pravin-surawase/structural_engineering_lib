# CI/CD and Tooling Setup

**Version:** 2.0
**Type:** Reference
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-04-07
**Last Updated:** 2026-04-08

---

## GitHub Actions Workflows

### ci.yml (Library)

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.11", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        uses: astral-sh/setup-uv@v8
        with:
          enable-cache: true
      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}
      - name: Install dependencies
        run: uv sync --group test --group lint --group arch
      - name: Lint (ruff 0.15.9)
        run: |
          uv run ruff check src/ tests/
          uv run ruff format --check src/ tests/
      - name: Type check (basedpyright — primary)
        run: uv run basedpyright src/
      - name: Type check (mypy strict — backup)
        run: uv run mypy --strict src/
      - name: Architecture boundaries (tach)
        run: uv run tach check
      - name: Test with coverage
        run: uv run pytest --cov --cov-report=xml -v
      - name: Upload coverage
        if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.12'
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: coverage.xml
          fail_ci_if_error: true

  benchmark:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v8
      - run: uv python install 3.12
      - run: uv sync --group test
      - name: SP:16 Benchmarks
        run: uv run pytest -m benchmark -v --tb=short

  check:  # Single required status check
    if: always()
    needs: [test, benchmark]
    runs-on: ubuntu-latest
    steps:
      - uses: re-actors/alls-green@release/v1
        with:
          jobs: ${{ toJSON(needs) }}
```

> **`re-actors/alls-green`** is used as the single required status check on the `main` branch.
> This avoids needing to update branch protection every time you add/rename a job.
> Only `check` needs to be required — it gates on all upstream jobs.

### test-publish.yml (Auto TestPyPI on every push)

```yaml
name: TestPyPI Dev Publish

on:
  push:
    branches: [main]
    tags-ignore: ["*"]

jobs:
  detect-version:
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.detect.outputs.tag }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 2
      - id: detect
        uses: salsify/action-detect-and-tag-new-version@v2
        with:
          version-command: |
            python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])"
          create-tag: false  # Don't tag, just detect

  publish-dev:
    needs: detect-version
    runs-on: ubuntu-latest
    permissions:
      id-token: write
    environment: testpypi
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: astral-sh/setup-uv@v8
      - run: uv build
      - name: Publish to TestPyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          repository-url: https://test.pypi.org/legacy/
```

> Every non-tagged push to `main` builds and publishes a dev version to TestPyPI
> via `salsify/action-detect-and-tag-new-version`. This ensures the packaging
> pipeline is always exercised, not just at release time.

### publish.yml (Library — Trusted Publishers)

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

permissions:
  id-token: write  # OIDC for Trusted Publishers

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for hatch-vcs
      - uses: astral-sh/setup-uv@v8
      - run: uv build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: pypi  # Requires manual approval for production
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        # No token needed — OIDC Trusted Publisher handles auth
```

### ci-backend.yml (App)

```yaml
name: Backend CI

on:
  push:
    paths: ["backend/**", "docker-compose*.yml"]
  pull_request:
    paths: ["backend/**"]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v8
      - run: uv python install 3.12
      - working-directory: backend
        run: |
          uv sync --group test
          uv run ruff check app/ tests/
          uv run pytest -v --cov
```

### ci-frontend.yml (App)

```yaml
name: Frontend CI

on:
  push:
    paths: ["frontend/**"]
  pull_request:
    paths: ["frontend/**"]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - working-directory: frontend
        run: |
          npm ci
          npm run build
          npx vitest run
```

### deploy.yml (App — Docker)

```yaml
name: Deploy

on:
  push:
    branches: [main]
    paths: ["backend/**", "frontend/**", "docker-compose.yml"]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker images
        run: docker compose build
      - name: Run integration tests
        run: |
          docker compose up -d
          sleep 10
          curl -f http://localhost:8000/health
          docker compose down
```

---

## Pre-commit Configuration

### .pre-commit-config.yaml (Library)

```yaml
# .pre-commit-config.yaml for <PACKAGE_NAME>
minimum_pre_commit_version: "4.0.0"

repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: check-yaml
      - id: check-toml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: debug-statements

  - repo: https://github.com/codespell-project/codespell
    rev: v2.4.2
    hooks:
      - id: codespell
        args: [--toml=pyproject.toml]

  - repo: https://github.com/zizmorcore/zizmor-pre-commit
    rev: v1.23.0
    hooks:
      - id: zizmor
        args: [--fix, --no-progress]

  - repo: https://github.com/kynan/nbstripout
    rev: "0.8.2"
    hooks:
      - id: nbstripout

  - repo: https://github.com/scientific-python/cookie
    rev: "2025.01.01"
    hooks:
      - id: sp-repo-review
```

---

## Tooling Stack (2026)

| Tool | Version | Purpose | Replaces | Config Location |
|---|---|---|---|---|
| **uv** | 0.11.3 | Package management, 10–100× faster | pip, poetry, Rye | `uv.lock` |
| **ruff** | 0.15.9 | Lint + format (19 rule sets) | black, isort, flake8, bandit, darglint | `[tool.ruff]` in pyproject.toml |
| **basedpyright** | v1.39.0 | Primary type checker (stricter than pyright) | pyright basic | `[tool.basedpyright]` in pyproject.toml |
| **mypy** | strict | Backup type checker in CI | — | `[tool.mypy]` in pyproject.toml |
| **tach** | v0.34.1 | Architecture boundary enforcement (NEW) | import-linter | `tach.toml` |
| **pytest** | 9.0.3 | Testing (strict mode) | — | `[tool.pytest]` in pyproject.toml |
| **mutmut** | 3.x | Mutation testing for safety-critical math (NEW) | — | `[tool.mutmut]` in pyproject.toml |
| **hypothesis** | ≥6.100 | Property-based testing | — | Part of test deps |
| **pytest-benchmark** | ≥5.0 | Performance regression detection | — | Part of test deps |
| **inline-snapshot** | ≥0.10 | Snapshot testing | — | Part of test deps |
| **codecov** | — | Coverage tracking, fail on regression | — | `.codecov.yml` |
| **towncrier** | — | Structured changelogs | — | `[tool.towncrier]` |
| **pre-commit** | ≥4.0 | Git hooks | — | `.pre-commit-config.yaml` |
| **zizmor** | v1.23.0 | GitHub Actions security linter | — | `.pre-commit-config.yaml` |
| **MkDocs Material** | 9.7.6 | Documentation site | — | `mkdocs.yml` |
| **mkdocstrings** | 1.0.3 | Auto-generate API docs from docstrings | — | Part of docs deps |
| **Sigstore** | — | Supply chain security for releases (NEW) | — | CI workflow |
| **pip-audit** | — | Dependency CVE scanning (NEW) | — | CI workflow |
| **cyclonedx-bom** | — | SBOM generation (NEW) | — | CI workflow |

---

## Superseded Tools (AVOID)

These tools are **fully replaced** by modern alternatives. Do NOT add them to new projects.

| ❌ Superseded Tool | ✅ Use Instead | Why |
|--------------------|---------------|-----|
| black | `ruff format` | ruff is 10–100× faster, same output |
| isort | `ruff` (I rules) | Built into ruff |
| flake8 | `ruff` (E, W, F rules) | Built into ruff, plus 700+ additional rules |
| bandit | `ruff` (S rules) | Security rules built into ruff |
| darglint | `ruff` (D rules) | Docstring linting built into ruff |
| pip | `uv` | 10–100× faster, lockfile support, Python management |
| poetry | `uv` | uv replaces all poetry functionality |
| Rye | `uv` | Rye creator (Armin) recommends uv as successor |
| pyright (standalone) | `basedpyright` | Stricter defaults, better error messages |

---

## Architecture Enforcement

### tach v0.34.1 (Primary — NEW)

[tach](https://github.com/gauge-sh/tach) enforces the 5-layer import boundary at CI time. If any module imports from a forbidden layer, CI fails.

```toml
# tach.toml
[modules]
core = { depends_on = [] }
common = { depends_on = ["core"] }
"codes.*" = { depends_on = ["common", "core"] }
services = { depends_on = ["codes", "common", "core"] }
```

```yaml
# CI step (add to ci.yml)
- name: Architecture boundaries (tach)
  run: uv run tach check
```

### import-linter (Backup)

```toml
# pyproject.toml
[tool.importlinter]
root_packages = ["<PACKAGE_NAME>"]

[[tool.importlinter.contracts]]
name = "5-layer architecture"
type = "layers"
layers = ["services", "codes", "common", "core"]
```

---

## Mutation Testing (Safety-Critical)

### mutmut 3.x (NEW)

For safety-critical IS 456 math functions, line coverage alone is insufficient. **Mutation testing** verifies that tests actually catch bugs by introducing small code mutations and checking that tests fail.

```bash
# Run mutation tests on safety-critical modules
uv run mutmut run --paths-to-mutate=src/<PACKAGE_NAME>/codes/is456/beam/flexure.py
uv run mutmut results
```

**Priority targets for mutation testing:**
- `flexure.py` — moment capacity, steel area (life-safety)
- `shear.py` — shear strength (life-safety)
- `tables.py` — IS 456 table interpolation (accuracy-critical)
- `stress_block.py` — stress block calculations (shared by all codes)

**CI Integration:**
```yaml
- name: Mutation testing (safety-critical)
  run: |
    uv run mutmut run --paths-to-mutate=src/<PACKAGE_NAME>/codes/is456/beam/flexure.py --no-progress
    uv run mutmut results --survived-only && exit 1 || true
```

---

## Supply Chain Security (NEW)

### Sigstore

Sign releases using Sigstore (keyless signing via OIDC). Used by pip, CPython, and all major Python projects.

```yaml
# In publish.yml
- name: Sign with Sigstore
  uses: sigstore/gh-action-sigstore-python@v3
  with:
    inputs: dist/*
```

### pip-audit

Scan dependencies for known CVEs:
```yaml
- name: Audit dependencies
  run: uv run pip-audit --require-hashes --desc
```

### cyclonedx-bom

Generate SBOM (Software Bill of Materials) for each release:
```bash
uv run cyclonedx-py environment -o sbom.json
```

---

## Zizmor — GitHub Actions Security Linter

> **zizmor** is a GitHub Actions security linter (used by pytest and pydantic). It checks for:
> - Insecure `actions/checkout` without pinned SHA
> - Dangerous `${{ github.event.* }}` template injection
> - Missing permissions blocks
> - Unpinned third-party actions

zizmor runs as a pre-commit hook (see `.pre-commit-config.yaml` above) with `--fix --no-progress`
to auto-remediate simple issues. For CI, add it as a standalone step:

```yaml
- name: Audit GitHub Actions (zizmor)
  run: uvx zizmor --fix --no-progress .github/workflows/
```

See [zizmor docs](https://woodruffw.github.io/zizmor/) for full rule reference.

---

## Dependabot Configuration

### dependabot.yml

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      actions:
        patterns: ["*"]
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      dev-deps:
        patterns: ["*"]
        dependency-type: "development"
```

---

## .editorconfig

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

## Codecov Configuration

### .codecov.yml

```yaml
# .codecov.yml
coverage:
  status:
    project:
      default:
        target: 95%
        threshold: 2%
    patch:
      default:
        target: 90%
        threshold: 5%
  range: "80...100"
comment:
  layout: "reach,diff,flags,files"
  behavior: default
  require_changes: false
```

---

## ReadTheDocs Configuration

### .readthedocs.yaml

```yaml
version: 2

build:
  os: ubuntu-22.04
  tools:
    python: "3.12"
  commands:
    - pip install uv
    - uv sync --group docs
    - uv run mkdocs build -d $READTHEDOCS_OUTPUT/html

mkdocs:
  configuration: docs/mkdocs.yml
```

---

## Watch List (Not Yet Adopted)

Tools that are promising but not yet stable enough for production use:

| Tool | Version | Status | What It Does | When to Adopt |
|------|---------|--------|--------------|---------------|
| **ty** | v0.0.29 | Beta (18.2K ⭐) | Astral's new type checker (by ruff team) | When it reaches v1.0 or gains full basedpyright parity |

> **ty** is Astral's (ruff company) new type checker. It's extremely fast and will likely become the default Python type checker. However, at v0.0.29 it's too early for production safety-critical code. Monitor progress at [github.com/astral-sh/ty](https://github.com/astral-sh/ty).
