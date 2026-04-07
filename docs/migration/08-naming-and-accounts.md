# Naming, Accounts & Setup

**Type:** Guide
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-04-07
**Last Updated:** 2026-04-08

---

## Library Name Options

| # | Name | PyPI | Import | Pros | Cons |
|---|------|------|--------|------|------|
| 1 | **rcdesign** | `rcdesign` | `rcdesign` | Short, professional, universally understood | May conflict with other RC design tools |
| 2 | **concretepy** | `concretepy` | `concretepy` | Clear domain + "py" suffix | Longer |
| 3 | **rcdcodes** | `rcdcodes` | `rcdcodes` | "RCD Codes" — signals code compliance | Less memorable |
| 4 | **structlib** | `structlib` | `structlib` | Short, expandable beyond IS 456 | Generic |
| 5 | **is456py** | `is456py` | `is456py` | Direct IS 456 reference | Too specific if expanding to other codes |
| 6 | **designcodes** | `designcodes` | `designcodes` | Expandable to multi-code (ACI, Eurocode) | Generic |
| 7 | **rcdetail** | `rcdetail` | `rcdetail` | Design + detailing emphasis | Limits scope perception |
| 8 | **indiarc** | `indiarc` | `indiarc` | Geographic focus, catchy | Too narrow for international use |

**Recommendation:** `rcdesign` — best balance of short, professional, and memorable. "RC Design" is universally understood in structural engineering.

---

## Decision: `rcdesign` is the Chosen Name

> **`rcdesign`** is the decided package name — both PyPI name and Python import name.

### Why `rcdesign`

- **Short** (8 chars) — comparable to `numpy` (5), `scipy` (5), `flask` (5)
- **Professional** — "RC Design" is universally understood in structural/civil engineering
- **Expandable** — works for IS 456 today, ACI 318 or Eurocode 2 tomorrow
- **PyPI = import** — no discrepancy: `pip install rcdesign` → `import rcdesign`
- **Valid Python identifier** — unlike `is456` which starts with digits

### Fallback Names (if `rcdesign` is taken on PyPI)

| Priority | Name | PyPI | Import |
|----------|------|------|--------|
| 1st | `rcdesign` | `rcdesign` | `rcdesign` |
| 2nd | `rcdesign-py` | `rcdesign-py` | `rcdesign_py` |
| 3rd | `rc-design` | `rc-design` | `rc_design` |

### PyPI Availability Check

```bash
# Check if the name is available
pip index versions rcdesign
# Or visit: https://pypi.org/project/rcdesign/
# "No versions found" = available
```

### Keyword Strategy: `is456` as Discoverability Keyword

Use `is456` in pyproject.toml **keywords** and **classifiers**, not in the package name:

```toml
[project]
name = "rcdesign"
keywords = [
    "structural-engineering",
    "reinforced-concrete",
    "is456",             # ← discoverability: engineers searching for IS 456
    "beam-design",
    "column-design",
    "civil-engineering",
    "concrete-design",
    "indian-standard",
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Education",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Physics",
    "Typing :: Typed",
]
```

This way, `pip search` and PyPI search for "is456" will find `rcdesign`.

### Install & Import Example

```bash
pip install rcdesign
```

```python
from rcdesign import design_beam

result = design_beam(b_mm=230, d_mm=450, Mu_kNm=85, fck=25, fy=415)
print(f"Steel: {result.Ast_mm2:.0f} mm²")
print(f"Safe: {result.is_safe()}")
```

Or with alias:

```python
import rcdesign as rc

result = rc.design_beam(b_mm=230, d_mm=450, Mu_kNm=85, fck=25, fy=415)
stress = rc.tau_c(fck=25, pt=0.8)  # IS 456 Table 19
```

---

## PyPI Naming Best Practices

- **PyPI name = import name = package directory name** (avoid discrepancies)
- All lowercase, underscores OK for import (PEP 8), hyphens OK for PyPI
- 1–2 words ideal, 3 words maximum
- Check availability: `pip index versions <name>` or search pypi.org
- Use keywords in metadata for discoverability, not in the package name
- Avoid "lib" or "py" in names unless it aids clarity (everything on PyPI is a Python library)
- Short names win: numpy (5), scipy (5), flask (5), rich (4), ruff (4)

---

## Account Setup (Step by Step)

### 1. GitHub Repository

1. Create repo on github.com
   - License: MIT
   - Add README: Yes
   - .gitignore: Python
2. **Settings → Branches → Branch protection rules:**
   - Branch: `main`
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass (CI)
   - ✅ Require branches to be up to date
3. **Settings → Security:**
   - ✅ Enable Dependabot alerts
   - ✅ Enable Dependabot security updates
   - ✅ Enable secret scanning
   - ✅ Enable push protection
4. **Settings → General:**
   - Add topics: `structural-engineering`, `is456`, `reinforced-concrete`, `python-library`, `civil-engineering`
   - Description: "IS 456:2000 reinforced concrete design library for Python"
5. **Settings → Environments:**
   - Create `pypi` environment
   - Add required reviewers for production releases

### 2. PyPI — Trusted Publishers (ZERO SECRETS)

Trusted Publishers use OIDC — no API tokens needed. The GitHub Actions workflow authenticates directly with PyPI.

1. Go to https://pypi.org → Register/Login
2. Navigate to **"Your projects"** → **"Publishing"** → **"Add a new pending publisher"**
3. Fill in:
   - **PyPI Project Name:** `rcdesign` (or chosen name)
   - **Owner:** Your GitHub username or org
   - **Repository name:** `rcdesign`
   - **Workflow name:** `publish.yml`
   - **Environment name:** `pypi`
4. Click **"Add"**
5. No API token needed — OIDC handles authentication automatically

### 3. TestPyPI — Dry Run Publishing

1. Go to https://test.pypi.org → Register (separate account from PyPI)
2. Same Trusted Publisher setup as above, but:
   - Environment name: `testpypi`
   - Add a separate job in `publish.yml` for TestPyPI (runs on pre-release tags)
3. Test with: `pip install --index-url https://test.pypi.org/simple/ rcdesign`

### 4. Codecov — Coverage Tracking

1. Go to https://codecov.io → Sign in with GitHub
2. Click **"Add a repository"** → Select your repo
3. Copy the `CODECOV_TOKEN`
4. In GitHub repo: **Settings → Secrets → Actions** → Add `CODECOV_TOKEN`
5. Add `.codecov.yml` to repo root (see [06-ci-cd-and-tooling.md](06-ci-cd-and-tooling.md))

### 5. ReadTheDocs — Documentation

1. Go to https://readthedocs.org → Sign in with GitHub
2. Click **"Import a Project"** → Select your repo
3. Add `.readthedocs.yaml` to repo root:

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

4. Push `.readthedocs.yaml` — ReadTheDocs auto-builds on every push

### 6. Pre-commit.ci (Optional — Free for Open Source)

1. Go to https://pre-commit.ci
2. Click **"Install"** → Install the GitHub App
3. Enable for your repository
4. Benefits:
   - Auto-runs pre-commit hooks on every PR
   - Auto-updates hook versions weekly
   - No CI minutes consumed
   - Results appear as PR status checks

### 7. GitHub Environments

1. GitHub repo **Settings → Environments**
2. Create environment: `pypi`
3. Add protection rule: **Required reviewers** → Add maintainers
4. This ensures releases require manual approval
5. The `publish.yml` workflow references this environment

---

## Domain / Organization (Optional)

### GitHub Organization

Consider creating a GitHub organization for long-term branding:

| Option | Benefits |
|--------|----------|
| `rcdesign` | Clean namespace, team management, org-level secrets |
| `structural-py` | Broader scope for future libraries |
| Personal account | Simpler, fine for solo/small projects |

### Custom Domain (Optional)

| Domain | Purpose |
|--------|---------|
| `rcdesign.dev` | Project website |
| `rcdesign.readthedocs.io` | Documentation (free) |
| `structlib.io` | If using structlib name |

For most open-source libraries, ReadTheDocs subdomain is sufficient. Custom domains add maintenance.

---

## Name Availability Checklist

Before finalizing the name, verify across all platforms:

- [ ] **PyPI:** `pip index versions <name>` → should return "No versions found"
- [ ] **TestPyPI:** Check https://test.pypi.org/project/<name>/
- [ ] **GitHub:** Check https://github.com/<name> → should be available
- [ ] **npm:** Check `npm view <name>` → for frontend package name
- [ ] **ReadTheDocs:** Check https://<name>.readthedocs.io
- [ ] **Google:** Search "<name> python" — check for conflicts
