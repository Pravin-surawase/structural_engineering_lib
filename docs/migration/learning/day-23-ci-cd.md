# Day 23: CI/CD Pipeline

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** Critical
**Created:** 2026-04-08
**Last Updated:** 2026-08-23
**Prerequisites:** Day 22 (Git Automation), Day 12 (Testing Patterns)
**Library files:** `scripts/check_all.py`, `scripts/verification-manifest.json`, `.github/workflows/fast-checks.yml`, `.github/workflows/nightly.yml`, `.github/workflows/publish.yml`
**Related scripts:** `scripts/diagnose_ci.py`, `scripts/check_architecture_boundaries.py`, `scripts/validate_imports.py`

---

## What You'll Learn Today

By the end of this module you'll understand:
- What CI/CD means and why it matters for a structural engineering library
- The 31 automated checks that guard this codebase (and what each one validates)
- The difference between `--quick` (10 checks, <30s) and full validation (31 checks)
- How GitHub Actions workflows trigger on push, PR, and release
- The 3 quality gate levels: commit, PR, and release
- How to diagnose and fix CI failures without panic
- The release pipeline: preflight → tag → PyPI publish
- Why the feedback loop (fail → fix → green → merge) prevents regressions

---

## 📖 Theory

### 1. What is CI/CD?

**CI (Continuous Integration):** Every time someone commits code, automated tests run immediately. If anything is broken, the team knows within minutes — not days or weeks later when a user reports a bug in a shear capacity calculation.

**CD (Continuous Delivery):** An explicitly authorized version tag can invoke
the validated package/publication workflow. A merge alone never publishes this
library, and repository-owner release authority remains mandatory.

> **Think of it like...** a structural inspection process. CI is the inspector who checks every weld on every beam the moment it's fabricated. CD is the logistics system that ships approved beams to the construction site. Without CI, you're hoping the welds are good. Without CD, approved beams sit in the factory.

For a structural engineering library, CI is especially critical. A wrong sign in a moment equation, a missing safety factor, or a unit conversion error doesn't cause a UI glitch — it causes an *unsafe design*. The 31 checks exist because correctness isn't optional.

---

### 2. Our 31 Checks

The `check_all.py` orchestrator organizes all validation into **8 categories**. Each category runs its checks in parallel for speed:

#### Category 1: API (4 checks)

Verifies public API signatures, response contracts, and OpenAPI manifest consistency.

#### Category 2: Docs (7 checks)

Broken links (870+ internal links), stale version numbers, CLI reference, tasks format, brief length, scripts index, and general doc validation.

#### Category 3: Architecture (3 checks)

Enforces 4-layer boundaries (Core → IS 456 → Services → UI), detects circular imports, validates all `import` statements resolve.

#### Category 4: Governance (5 checks)

Governance rules, repo hygiene, Python version, Pydantic schema snapshots.

#### Category 5: FastAPI (3 checks)

FastAPI issues, Docker config validity, OpenAPI snapshot drift.

#### Category 6: Git (4 checks)

Clean git state, no unfinished merges, version consistency across 13+ files, script line budget.

#### Category 7: Stale References (4 checks)

Script references still exist, agent instructions match codebase, bootstrap docs are fresh.

#### Category 8: Code Quality (1 check)

Type annotations present on functions.

---

### 3. Check Levels: Quick vs Full

You don't always need all 31 checks. The `--quick` flag runs a curated **fast subset** for rapid feedback:

```python
# Quick checks — 10 checks from 5 categories, <30 seconds
QUICK_CHECKS = {
    "docs": ["Broken links", "Doc versions", "Brief length"],
    "arch": ["Import validation"],
    "governance": ["Repo hygiene", "Token efficiency"],
    "git": ["Git state", "Unfinished operation"],
    "stale": ["Script references", "CLI smoke"],
}
```

When to use which:

| Situation | Command | Checks | Time |
|-----------|---------|--------|------|
| Quick sanity check | `./run.sh check --quick` | 10 | <30s |
| Before a PR | `./run.sh check` | 31 | 2-5 min |
| Single category | `./run.sh check --category api` | 4 | ~30s |
| Only what changed | `./run.sh check --changed` | varies | varies |
| Auto-fix issues | `./run.sh check --fix` | 31 | 2-5 min |

The `--changed` flag compares the whole candidate with `origin/main`, includes
working-tree changes, and uses the canonical verification-domain manifest.
Unknown paths or Git failures select every domain rather than silently skipping.

---

### 4. GitHub Actions

GitHub Actions are cloud-based CI runners. When you push code or open a PR,
GitHub spins up a virtual machine and runs checks. The maintained automation is
consolidated into four workflow lanes.

#### On every push and PR: Fast Checks

```yaml
# .github/workflows/fast-checks.yml
name: PR Validation
on:
  pull_request:
  push:
    branches: [ main ]
```

This workflow calls `scripts/verification.py plan`; the same strict manifest
drives local scheduling and hosted applicability. Unknown impact selects all
seven domains, while known docs-only changes skip unrelated product jobs.

#### Scheduled/manual: Full Test Matrix

```yaml
# .github/workflows/nightly.yml
name: Weekly Full Verification
on:
  schedule:
  workflow_dispatch:
```

The weekly/manual lane runs the broad suites, clean-wheel/CLI checks, dependency
audits, Docker health, and optional cross-platform smoke.

#### On release tag: Publish to PyPI

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI
on:
  push:
    tags:
      - 'v[0-9]+.[0-9]+.[0-9]+'   # Triggers on v0.22.0, v1.0.0, etc.
```

When a version tag is pushed, it validates tests, checks tag matches `pyproject.toml`, builds wheel + sdist, and publishes to PyPI using **Trusted Publishers** (no API tokens — GitHub's OIDC identity proves legitimacy).

#### Other workflows

The four maintained lanes are `fast-checks.yml`, `nightly.yml`, `publish.yml`,
and `deploy-docs.yml`. Former standalone Docker, security, CodeQL, link,
scorecard, and performance workflows were consolidated or explicitly parked by
MAINT-008; see `.github/workflows/README.md` for the retained signal map.

---

### 5. Quality Gates

The checks are organized into three progressive levels. Each level is a gate — code must pass to proceed:

#### Level 1: Commit Gate (local, via git hooks)

Lint (Black, Ruff) + type check + import validation + commit message format + no force flags + no stub edits. **Blocks the commit** if any check fails.

#### Level 2: PR Gate (GitHub Actions)

Applicable manifest-planned Python, FastAPI, React, Excel, control,
documentation, and repository jobs. The always-run required `PR Gate` rejects
failed, cancelled, missing, or improperly skipped work and **blocks the merge**.

#### Level 3: Release Gate (pre-release)

All Level 2 + release preflight + User Acceptance Testing + security scan + API doc freshness. **Blocks the tag** from being pushed.

---

### 6. Fixing CI Failures

CI failures are normal — they're the system working as designed. Here's the workflow:

#### Step 1: Diagnose

```bash
./scripts/python_runtime.sh scripts/diagnose_ci.py --pr 42   # Check a PR
./scripts/python_runtime.sh scripts/diagnose_ci.py --local    # Check locally
```

#### Step 2: Auto-fix if possible

```bash
./scripts/python_runtime.sh scripts/diagnose_ci.py --local --fix
```

#### Step 3: Manual fix, verify, recommit

```bash
./scripts/python_runtime.sh -m pytest Python/tests/test_column.py -v -x
# Fix the code...
./run.sh check --quick                              # Verify once
# Codex stages only intended paths and creates the normal verified commit.
```

#### Common failures

| CI Failure | Auto-fixable? | Fix |
|------------|:---:|-----|
| Black formatting | ✅ | `diagnose_ci.py --local --fix` |
| Ruff lint | ✅ | `diagnose_ci.py --local --fix` |
| Python test | ❌ | Read traceback, fix code |
| Import error | ❌ | Run `validate_imports.py`, fix paths |
| React build | ❌ | `cd react_app && npm run build`, fix TS errors |
| Architecture violation | ❌ | Move the import to the correct layer |

---

### 7. Release CI

```bash
# Preflight — validates EVERYTHING before release
./run.sh release preflight <version>
# Checks: git state, tests, React build, docs, versions, CHANGELOG, security

# Only after the repository owner explicitly authorizes that release:
./run.sh release run <version>
# Codex performs the normal commit/tag/push flow without bypassing gates.
```

---

### 8. The Feedback Loop

```
Commit → Hooks check → Push → GitHub Actions → Pass? → Merge
                                              → Fail? → Fix → Recommit → ...

Authorized release → Preflight → Tag checks → Package publication
```

Each stage catches problems cheaper than the next: a hook catches formatting in 2 seconds. The same issue in a PR review costs 10 minutes. After release? Hours of emergency patching.

---

## 🏗️ Library Examples

### Example 1: Running quick checks

```bash
$ ./run.sh check --quick

🔍 Running 10 quick checks (5 categories)...

  ✅ Broken links        (1.2s)
  ✅ Doc versions         (0.8s)
  ✅ Brief length         (0.3s)
  ✅ Import validation    (2.1s)
  ✅ Repo hygiene         (0.5s)
  ✅ Token efficiency     (0.4s)
  ✅ Git state            (0.2s)
  ✅ Unfinished operation (0.1s)
  ✅ Script references    (1.8s)
  ✅ CLI smoke            (0.8s)

━━━━━━━━━━━━━━━━━━━━━━
✅ 10/10 checks passed (8.2s)
```

### Example 2: Full validation with a failure

```bash
$ ./run.sh check

🔍 Running 31 checks (8 categories, 4 workers)...

  API ━━━━━━ 4/4 ✅  |  Docs ━━━━━ 6/7 ⚠️  |  Arch ━━━━━ 3/3 ✅
  Governance ━ 5/5 ✅  |  FastAPI ━━ 3/3 ✅  |  Git ━━━━━ 4/4 ✅
  Stale ━━━━━ 4/4 ✅  |  Code ━━━━━ 1/1 ✅

  ❌ Broken links: 2 broken links found
     → docs/reference/api.md:42 → docs/old-file.md (not found)

❌ 30/31 checks passed, 1 failed (127.3s)
```

### Example 3: Diagnosing a CI failure

```bash
$ ./scripts/python_runtime.sh scripts/diagnose_ci.py --local

🔍 Local CI Diagnosis
━━━━━━━━━━━━━━━━━━━━
  ✅ Black formatting    — all files formatted
  ❌ Ruff lint           — 2 issues found
     Python/structural_lib/codes/is456/column.py:42: F841 unused variable 'x_u'
     Python/structural_lib/codes/is456/column.py:87: E501 line too long (142 > 120)
  ✅ Import validation   — all imports resolve
  ✅ Pytest              — 247 passed, 0 failed

Fix: run with --fix to auto-resolve lint issues

$ ./scripts/python_runtime.sh scripts/diagnose_ci.py --local --fix

  ✅ Ruff: fixed 2 issues in column.py
  ✅ All checks now passing
```

### Example 4: GitHub Actions output (PR view)

```
PR Validation
├── Detect Changes       ✅ (5s)   │ python: true, docs: false
├── Python Validation    ✅ (45s)  │ lint, types, contracts, architecture
├── FastAPI Validation   ✅ (75s)  │ tests and API/deployment contracts
├── Documentation        — skipped │ canonical plan: docs=false
└── PR Gate              ✅ (4s)   │ every applicable job succeeded
All checks passed ✅ — ready to merge
```

---

## 🎯 Simple Examples

### Run the quick check (your daily sanity check)

```bash
./run.sh check --quick
```

Get into the habit of running this before every commit. It takes less than 30 seconds and catches the most common issues.

### Run checks for what you changed

```bash
./run.sh check --changed    # Only categories relevant to your git diff
./run.sh check --category api   # Single category
```

### List all checks

```bash
./scripts/python_runtime.sh scripts/check_all.py --list
```

---

## 🔧 Exercise

### Exercise 1: Run the quick checks

```bash
./run.sh check --quick
```

**What to look for:**
- How many checks ran? (Should be 10)
- How long did it take? (Should be <30s)
- Did any fail? What was the error message?

### Exercise 2: Run the full validation

```bash
./run.sh check
```

**What to look for:**
- How many categories are there? (8)
- How many total checks? (31)
- Which category took the longest?
- Did anything fail? Read the error messages carefully

### Exercise 3: Try the CI diagnostic tool

```bash
./scripts/python_runtime.sh scripts/diagnose_ci.py --local
```

**What to look for:** Which local checks pass (Black, Ruff, imports, pytest)? Can failures be auto-fixed with `--fix`?

### Exercise 4: Read a GitHub Actions workflow

Open `.github/workflows/fast-checks.yml` and identify:
- What triggers the workflow? (`on:` section)
- How does it decide which jobs to skip? (`scripts/verification.py plan`)
- What Python version does it use?

---

## 💬 Can You Explain?

Test your understanding — try to answer these without looking back:

1. **What does CI stand for, and why is it critical for a structural engineering library?** (Hint: wrong answers have real-world consequences)
2. **How many checks does `--quick` run vs the full suite?** Why is the quick subset faster?
3. **Name the 8 check categories.** What does each one validate?
4. **A PR's CI shows a "Black formatting" failure. What command fixes it?** Is it auto-fixable?
5. **What are the 3 quality gate levels?** What does each one block?
6. **When does the `publish.yml` workflow trigger?** What tag pattern activates it?
7. **What is "Trusted Publishers" in PyPI?** Why is it better than storing API tokens?
8. **Why can one changed path select several domains?** How does the shared
   manifest keep local and hosted scheduling consistent?

---

## 📎 References

- [check_all.py](../../../scripts/check_all.py) — The 31-check orchestrator
- [diagnose_ci.py](../../../scripts/diagnose_ci.py) — CI failure diagnosis + auto-fix
- [fast-checks.yml](../../../.github/workflows/fast-checks.yml) — PR/push CI workflow
- [nightly.yml](../../../.github/workflows/nightly.yml) — scheduled/manual broad verification
- [publish.yml](../../../.github/workflows/publish.yml) — PyPI release workflow
- [check_architecture_boundaries.py](../../../scripts/check_architecture_boundaries.py) — 4-layer enforcement
- [validate_imports.py](../../../scripts/validate_imports.py) — Import resolution checker
- **Day 22** — Git Automation (how commits enter the pipeline)
- **Day 24** — AI Agents (who runs these checks and when)
- [GitHub Actions documentation](https://docs.github.com/en/actions) — Official reference
