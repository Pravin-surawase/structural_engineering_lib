# GitHub Workflows Reference

**Type:** Reference
**Audience:** All Agents
**Status:** Production Ready
**Importance:** High
**Version:** 1.0.0
**Created:** 2026-01-13
**Last Updated:** 2026-01-13

---

## Overview

This folder contains 12 GitHub Actions workflows that automate CI/CD for the project.

**For AI Agents:** Understand these workflows to:
- Know what checks run on your commits/PRs
- Diagnose CI failures
- Understand the release process

---

## Quick Reference

| Workflow | Trigger | Time | Purpose |
|----------|---------|------|---------|
| **fast-checks.yml** | PR + Push | ~3min | Quick validation (Python 3.11) |
| **python-tests.yml** | Push to main | ~5min | Full test matrix (3.11, 3.12) |
| **streamlit-validation.yml** | Streamlit changes | ~2min | AST scanner + pylint |
| **auto-format.yml** | Push | ~2min | Auto-format code |
| **git-workflow-tests.yml** | Git script changes | ~2min | Test git automation |
| **publish.yml** | Release tag | ~5min | Publish to PyPI |
| **security.yml** | Push + Schedule | ~3min | Security scanning |
| **codeql.yml** | Push + Schedule | ~10min | Code analysis |
| **nightly.yml** | Schedule (daily) | ~10min | Nightly full checks |
| **cost-optimizer-analysis.yml** | On demand | ~3min | Cost optimization analysis |
| **root-file-limit.yml** | Push | ~1min | Root file count check |
| **leading-indicator-alerts.yml** | Push | ~2min | Quality metric alerts |

---

## Workflow Details

### 1. fast-checks.yml (Primary PR Check)

**Purpose:** Quick validation for PRs - provides fast feedback

**Runs on:** Pull requests + Push to main

**What it checks:**
- Python 3.11 only (single version for speed)
- Lint with ruff
- Type check with mypy
- Unit tests with pytest
- Format check with black

**Timeout:** 5 minutes

**Agent Action:** If this fails on your PR, fix the issues before merge.

---

### 2. python-tests.yml (Full Test Matrix)

**Purpose:** Comprehensive testing after merge to main

**Runs on:** Push to main only

**What it checks:**
- Full matrix: Python 3.11 and 3.12
- Lint and typecheck
- Full test suite
- Coverage reporting

**Agent Action:** If this fails after merge, create a fix PR immediately.

---

### 3. streamlit-validation.yml

**Purpose:** Catch Streamlit runtime errors before they reach production

**Runs on:** Changes to `streamlit_app/**/*.py`

**What it checks:**
- AST Scanner (`check_streamlit_issues.py`): NameError, ZeroDivisionError, KeyError, etc.
- Import validation (`check_streamlit_imports.py`)
- Pylint with Streamlit-specific config

**Agent Action:** Run `python scripts/check_streamlit_issues.py --all-pages` locally before pushing Streamlit changes.

---

### 4. auto-format.yml

**Purpose:** Auto-format code that wasn't formatted locally

**Runs on:** Push to main

**What it does:**
- Runs black on Python code
- Commits formatting fixes automatically

**Agent Action:** Run `python -m black .` locally to avoid auto-format commits.

---

### 5. git-workflow-tests.yml

**Purpose:** Test git automation scripts

**Runs on:** Changes to git scripts (`scripts/*git*.sh`, `scripts/*push*.sh`, etc.)

**What it tests:**
- safe_push.sh workflow
- should_use_pr.sh decision logic
- Recovery scripts

**Agent Action:** Run `./scripts/test_git_workflow.sh` locally if editing git scripts.

---

### 6. publish.yml

**Purpose:** Publish package to PyPI

**Runs on:** Release tag creation (v*.*.*)

**What it does:**
- Build wheel and sdist
- Publish to PyPI
- Create GitHub release

**Agent Action:** Use `python scripts/release.py` for releases.

---

### 7. security.yml

**Purpose:** Security vulnerability scanning

**Runs on:** Push + Weekly schedule

**What it checks:**
- Dependency vulnerabilities (pip-audit)
- Secret scanning
- SAST scanning

**Agent Action:** Review security alerts in GitHub Security tab.

---

### 8. codeql.yml

**Purpose:** Advanced code analysis

**Runs on:** Push + Weekly schedule

**What it checks:**
- CodeQL analysis for Python
- Security vulnerabilities
- Code quality issues

**Agent Action:** Check CodeQL alerts if workflow fails.

---

### 9. nightly.yml

**Purpose:** Full validation suite (catches issues that slip through)

**Runs on:** Daily at midnight UTC

**What it checks:**
- Full test matrix
- Doc link validation
- Coverage thresholds
- Performance benchmarks

**Agent Action:** Check nightly results each morning.

---

### 10. cost-optimizer-analysis.yml

**Purpose:** Analyze cost optimization opportunities

**Runs on:** Manual trigger (workflow_dispatch)

**What it does:**
- Analyzes CI run times
- Suggests optimizations

**Agent Action:** Trigger manually when investigating CI costs.

---

### 11. root-file-limit.yml

**Purpose:** Enforce root directory cleanliness

**Runs on:** Push

**What it checks:**
- Max 10 files in repo root
- Prevents root clutter

**Agent Action:** If blocked, move file to appropriate subfolder.

---

### 12. leading-indicator-alerts.yml

**Purpose:** Alert on quality metric degradation

**Runs on:** Push

**What it checks:**
- Test count changes
- Coverage changes
- Doc count changes

**Agent Action:** Review alerts for quality regressions.

---

## CI Failure Troubleshooting

### Common Issues

| Error | Cause | Fix |
|-------|-------|-----|
| `black check failed` | Code not formatted | Run `python -m black .` locally |
| `ruff check failed` | Lint errors | Run `ruff check --fix .` |
| `mypy failed` | Type errors | Fix type annotations |
| `pytest failed` | Test failure | Run tests locally, fix failures |
| `AST scanner CRITICAL` | Runtime error risk | Fix the flagged issue |

### Quick Local Validation

```bash
# Run same checks as fast-checks.yml
cd Python
python -m black --check .
python -m ruff check .
python -m mypy structural_lib/
python -m pytest tests/ -v
```

---

## Related Documentation

- [automation-scripts.md](../../docs/git-automation/automation-scripts.md) - All automation scripts
- [workflow-guide.md](../../docs/git-automation/workflow-guide.md) - Git workflow
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Contribution guidelines

---

## Workflow Dependencies

```
PR Created
    └── fast-checks.yml (3 min)
            ├── PASS → Ready for review
            └── FAIL → Fix required

PR Merged
    └── python-tests.yml (5 min)
            ├── auto-format.yml (if needed)
            └── streamlit-validation.yml (if applicable)

Release Tag (v*.*.*)
    └── publish.yml
            └── PyPI publish

Daily (midnight)
    └── nightly.yml
            ├── security.yml
            └── Full validation
```
