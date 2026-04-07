# CI/CD and Tooling Setup

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
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true
      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}
      - name: Install dependencies
        run: uv sync --group test --group lint
      - name: Lint (ruff)
        run: |
          uv run ruff check src/ tests/
          uv run ruff format --check src/ tests/
      - name: Type check (mypy)
        run: uv run mypy src/
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
      - uses: astral-sh/setup-uv@v4
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
      - uses: astral-sh/setup-uv@v4
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
      - uses: astral-sh/setup-uv@v4
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
      - uses: astral-sh/setup-uv@v4
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
# .pre-commit-config.yaml for rcdesign
minimum_pre_commit_version: "4.0.0"

repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.0
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

## Tooling Stack

| Tool | Purpose | Why | Config Location |
|---|---|---|---|
| **uv** | Package management | 82.8k⭐, replaces pip/poetry/pipx, 10-100x faster | `uv.lock` |
| **ruff** | Lint + format | 46.9k⭐, replaces flake8+black+isort+pyupgrade | `[tool.ruff]` in pyproject.toml |
| **mypy** | Type checking | Industry standard, strict mode catches bugs | `[tool.mypy]` in pyproject.toml |
| **pyright** | Type checking (IDE) | Powers Pylance in VS Code | `pyrightconfig.json` |
| **pytest** | Testing | Gold standard for Python testing | `[tool.pytest]` in pyproject.toml |
| **hypothesis** | Property testing | Discovers edge cases automatically | Part of test deps |
| **pytest-benchmark** | Performance | Regression detection for critical paths | Part of test deps |
| **codecov** | Coverage tracking | Track coverage over time, fail on regression | `.codecov.yml` |
| **towncrier** | Changelogs | Structured, contributor-friendly changelog | `[tool.towncrier]` |
| **pre-commit** | Git hooks | Consistent quality on every commit | `.pre-commit-config.yaml` |
| **zizmor** | GH Actions security | Catches injection, unpinned actions, missing permissions | `.pre-commit-config.yaml` |
| **MkDocs Material** | Documentation | Beautiful docs with API auto-generation | `mkdocs.yml` |
| **mkdocstrings** | API docs | Auto-generate from docstrings | Part of docs deps |

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
