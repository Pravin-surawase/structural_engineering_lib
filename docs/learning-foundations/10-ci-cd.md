# Module 10: CI/CD — Automated Quality and Deployment

## The Big Idea

**CI/CD** (Continuous Integration / Continuous Deployment) means every code change is automatically tested, checked, and optionally deployed. Instead of hoping your code works, machines verify it for you — every single time.

---

## Part 1: What Is CI/CD?

### CI — Continuous Integration
Every time you push code, automated checks run immediately.

```
Developer pushes code
       │
       ▼
┌─────────────────────┐
│  CI Pipeline Runs   │
│  • Run all tests    │
│  • Check types      │
│  • Check linting    │
│  • Check imports    │
│  • Check security   │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     │ ALL PASS  │ ANY FAIL
     ▼           ▼
  ✅ Merge     ❌ Block
  allowed      Fix required
```

### CD — Continuous Deployment
When code is merged to `main`, it's automatically deployed.

```
Merge to main
       │
       ▼
┌─────────────────────┐
│  CD Pipeline Runs    │
│  • Build package     │
│  • Run final tests   │
│  • Deploy to PyPI    │
│  • Deploy Docker     │
│  • Update docs site  │
└─────────────────────┘
```

---

## Part 2: GitHub Actions — The CI/CD Platform

**GitHub Actions** runs automated workflows triggered by events (push, PR, schedule).

### Workflow file structure:
```yaml
# .github/workflows/tests.yml

name: Run Tests                    # Workflow name

on:                                 # When to run
  push:
    branches: [main]               # On push to main
  pull_request:
    branches: [main]               # On PR to main

jobs:                               # What to do
  test:
    runs-on: ubuntu-latest         # Which OS

    steps:                          # Step by step
      - uses: actions/checkout@v4  # Get the code

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest Python/tests/ -v
```

### Key concepts:

| Concept | Meaning | Example |
|---------|---------|---------|
| **Workflow** | A YAML file that defines automation | `tests.yml` |
| **Trigger** (`on`) | What event starts the workflow | `push`, `pull_request`, `schedule` |
| **Job** | A set of steps that run on one machine | `test`, `build`, `deploy` |
| **Step** | An individual command or action | `pip install`, `pytest` |
| **Action** | Reusable step from the marketplace | `actions/checkout@v4` |
| **Runner** | The machine that executes the job | `ubuntu-latest` |

---

## Part 3: Common Workflow Patterns

### Pattern 1: Test on every push
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: pytest Python/tests/ -v
```

### Pattern 2: Test on multiple Python versions
```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: ["3.11", "3.12", "3.13"]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pytest
```

### Pattern 3: Build and deploy only on main
```yaml
jobs:
  deploy:
    if: github.ref == 'refs/heads/main'    # Only on main branch
    needs: [test]                            # Only after tests pass
    runs-on: ubuntu-latest
    steps:
      - run: python -m build
      - run: twine upload dist/*             # Publish to PyPI
```

### Pattern 4: Scheduled checks (cron)
```yaml
on:
  schedule:
    - cron: "0 6 * * 1"    # Every Monday at 6 AM UTC

jobs:
  weekly-audit:
    runs-on: ubuntu-latest
    steps:
      - run: pip audit       # Check for vulnerable dependencies
```

---

## Part 4: Quality Gates — What Gets Checked

A **quality gate** blocks merging if any check fails.

### This project's 3-level quality gates:

```
LEVEL 1: COMMIT GATE (every commit)
  ┌─────────────────────────────────────────┐
  │  ✅ Conventional commit format           │
  │  ✅ No import violations                │
  │  ✅ No stub files accidentally edited   │
  │  ✅ Code formatted (ruff)               │
  └─────────────────────────────────────────┘

LEVEL 2: PR GATE (every pull request)
  ┌─────────────────────────────────────────┐
  │  ✅ All Python tests pass               │
  │  ✅ React builds without errors         │
  │  ✅ Type checks pass                    │
  │  ✅ Architecture boundaries respected   │
  │  ✅ No broken documentation links       │
  │  ✅ Coverage meets threshold (85%)      │
  └─────────────────────────────────────────┘

LEVEL 3: RELEASE GATE (before version bump)
  ┌─────────────────────────────────────────┐
  │  ✅ All Level 1 + Level 2 checks        │
  │  ✅ Package builds successfully          │
  │  ✅ Package installs in clean env        │
  │  ✅ API docs are up to date             │
  │  ✅ Security scan passes                │
  │  ✅ User acceptance tests pass          │
  └─────────────────────────────────────────┘
```

---

## Part 5: The check_all.py Script

This project has 28 automated checks grouped into 8 categories:

```bash
# Run all 28 checks
.venv/bin/python scripts/check_all.py

# Run quick subset (8 checks, <30 seconds)
.venv/bin/python scripts/check_all.py --quick
```

### The 8 categories:
```
Category        Checks                                What It Catches
─────────      ──────                                 ────────────────
API            OpenAPI drift, schema consistency       API changed without docs update
Docs           Broken links, metadata, budget          Dead links, missing metadata
Architecture   4-layer violations, circular imports    Math importing from UI
Governance     File limits, naming conventions         Too many files, bad names
FastAPI        Route conflicts, model consistency      Duplicate endpoints
Git            Uncommitted changes, branch hygiene     Dirty working tree
Stale          Old drafts, unused files                Files nobody maintains
Code           Type errors, import validation          Type mismatches
```

---

## Part 6: Workflow Files in This Project

```
.github/workflows/
├── fast-checks.yml          ← Quick checks on every push (<2 min)
├── python-tests.yml         ← Full pytest suite
├── react-build.yml          ← React build + type-check
├── publish.yml              ← Publish to PyPI on release
├── docker-build.yml         ← Build and test Docker image
├── security-scan.yml        ← Dependency vulnerability scan
├── docs-deploy.yml          ← Deploy documentation site
└── weekly-audit.yml         ← Scheduled maintenance checks
```

### How they connect:

```
Developer pushes to feature branch:
  fast-checks.yml runs immediately (quick validation)

Developer opens PR:
  python-tests.yml + react-build.yml + security-scan.yml all run
  All must pass before merge is allowed

PR merged to main:
  publish.yml runs (if version was bumped)
  docs-deploy.yml runs (update docs site)
  docker-build.yml runs (update Docker image)
```

---

## Part 7: Reading CI Results

### On GitHub:

```
PR #42: feat(column): add axial capacity

  Checks:
  ✅ fast-checks       (32s)    ← All quick checks passed
  ✅ python-tests      (1m 45s) ← 147 tests passed
  ❌ react-build       (52s)    ← Type error in BeamForm.tsx
  ✅ security-scan     (28s)    ← No vulnerabilities

  ❌ Some checks failed — merge blocked
```

### When a check fails:
1. Click the failed check to see logs
2. Find the error message
3. Fix the issue locally
4. Push again — CI re-runs automatically

### Common CI failures:

| Failure | Cause | Fix |
|---------|-------|-----|
| Test failed | Code change broke something | Fix the test or fix the code |
| Type error | TypeScript/Python type mismatch | Add proper type annotations |
| Build error | Missing import or syntax error | Fix the import/syntax |
| Lint error | Code style violation | Run formatter (`ruff format`) |
| Security alert | Vulnerable dependency | Update the dependency |

---

## Part 8: Release Pipeline

When ready to publish a new version:

```
1. Bump version in pyproject.toml
         │
         ▼
2. Create GitHub release
         │
         ▼
3. CI automatically:
   ┌─────────────────────────────────┐
   │  a. Build Python package (.whl)  │
   │  b. Run full test suite          │
   │  c. Build Docker image           │
   │  d. Publish to PyPI              │
   │  e. Push Docker image            │
   │  f. Deploy docs                  │
   └─────────────────────────────────┘
         │
         ▼
4. Users can: pip install structural-lib-is456==0.21.6
```

### Pre-release validation:
```bash
# Run all pre-release checks locally first
./run.sh release preflight 0.21.7

# What it checks:
# ✅ Package builds
# ✅ Package installs in clean environment
# ✅ All tests pass
# ✅ API docs match code
# ✅ No security vulnerabilities
# ✅ Docker image builds and starts
```

---

## Part 9: CI/CD Best Practices

### Do:
```
✅ Run CI on every push and PR
✅ Block merging if CI fails
✅ Keep CI fast (under 5 minutes)
✅ Fix failing tests immediately
✅ Run security scans weekly
✅ Cache dependencies to speed up CI
```

### Don't:
```
❌ Skip CI to merge faster (-- force)
❌ Ignore flaky tests ("it sometimes passes")
❌ Put secrets in workflow files
❌ Run the entire test suite on every push (use --quick)
❌ Deploy without running all checks first
```

---

## Part 10: Setting Up CI/CD for a New Project

Here's the minimum CI setup for a new Python project:

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Lint
        run: ruff check .

      - name: Type check
        run: pyright

      - name: Test
        run: pytest tests/ -v --cov --cov-report=term-missing
```

This gives you: linting + type checking + tests + coverage on every push. You can add more checks as the project grows.

---

## Part 11: Exercises

1. **Read a workflow:** Open any file in `.github/workflows/`. Identify the trigger, jobs, and steps.
2. **Trigger CI:** Make a small change, push it, and watch the CI run on GitHub.
3. **Read CI output:** Find a recent PR. Look at the "Checks" tab. What ran?
4. **Run checks locally:** Execute `.venv/bin/python scripts/check_all.py --quick`. What passes? What fails?

---

## Part 12: Self-Check

1. **What is CI?** Automatically running tests and checks on every code change.
2. **What is CD?** Automatically deploying code after checks pass.
3. **What triggers a workflow?** Events like push, pull_request, schedule, or release.
4. **What's a quality gate?** A set of checks that must pass before code can proceed.
5. **Why block merging on CI failure?** To ensure main branch always has working code.
6. **What's the minimum CI for a new project?** Lint + type check + tests on every push.

---

## Key Takeaway

> CI/CD is your **automated quality assurance**. It catches problems before they reach users. Every project should have at least basic CI from day one — the cost of setting it up is tiny compared to the cost of shipping broken code.

**Next:** [Module 11 — Errors and Debugging](11-errors-and-debugging.md) explains what goes wrong and how to fix it.
