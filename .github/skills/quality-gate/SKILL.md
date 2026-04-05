---
name: quality-gate
description: "Mandatory pre-merge quality checks for production code — security scan, packaging test, API consistency, no silent failures. Prevents the issues that caused 4 emergency releases in v0.21.x."
---

# Quality Gate Skill

Mandatory quality checks that run before any production code change is merged. These checks address the specific failure patterns discovered across v0.21.0-v0.21.3.

## When to Use

- **Before every PR merge** — reviewer runs this as part of code review
- **Before every release** — full quality gate with extended checks
- **After fixing audit findings** — verify the fix doesn't introduce new issues

## Quality Gate Levels

### Level 1: Quick Gate (every commit, < 2 min)

```bash
# 1. No bare except clauses added
git diff --cached -- '*.py' | grep "+.*except Exception:" && echo "FAIL: bare except" || echo "PASS"

# 2. No str(e) in error responses
git diff --cached -- 'fastapi_app/routers/*.py' | grep "+.*str(e)" && echo "FAIL: raw exception" || echo "PASS"

# 3. No MagicMock on structural types
git diff --cached -- 'Python/tests/*.py' | grep -E "MagicMock.*Result|Mock.*Result" && echo "WARNING: MagicMock on Result types" || echo "PASS"

# 4. Import direction check
.venv/bin/python scripts/validate_imports.py --scope structural_lib 2>&1 | tail -5
```

### Level 2: Standard Gate (every PR, < 10 min)

All Level 1 checks, plus:

```bash
# 5. Full test suite passes
.venv/bin/pytest Python/tests/ -v --tb=short -q

# 6. API tests pass
.venv/bin/pytest fastapi_app/tests/ -v --tb=short -q

# 7. React build succeeds
cd react_app && npm run build

# 8. Architecture boundaries intact
.venv/bin/python scripts/check_architecture_boundaries.py 2>&1 | tail -10

# 9. No __all__ drift (if __init__.py changed)
.venv/bin/python -c "
import structural_lib
for name in structural_lib.__all__:
    assert getattr(structural_lib, name, None) is not None, f'{name} not importable'
print('PASS: __all__ exports verified')
"

# 10. Version consistency
.venv/bin/python scripts/check_doc_versions.py
```

### Level 3: Release Gate (before release, < 25 min)

All Level 1 + Level 2, plus:

```bash
# 11. Wheel content validation
cd Python && ../.venv/bin/python -m build
unzip -l dist/*.whl | grep -E "tests/|scripts/" && echo "FAIL" || echo "PASS"

# 12. User acceptance test (see /user-acceptance-test skill)

# 13. Security scan
grep -rn "str(e)" fastapi_app/routers/ && echo "FAIL" || echo "PASS"
grep -rn "except Exception:" Python/structural_lib/ | grep -v "# nosec" | wc -l

# 14. README accuracy
.venv/bin/python -c "
import structural_lib
for func in ['design_beam_is456', 'build_detailing_input', 'compute_detailing', 'compute_bbs']:
    assert hasattr(structural_lib, func), f'{func} missing'
print('PASS')
"

# 15. Documentation links
.venv/bin/python scripts/check_links.py 2>&1 | tail -5
```

## Development Rules (Enforced at Quality Gate)

### Python Core (`Python/structural_lib/`)

| Rule | Rationale | How Checked |
|------|-----------|-------------|
| No `except Exception:` without comment | v0.21.2: silent clause DB failure | grep in Level 1 |
| No `str(e)` in HTTP responses | v0.21.3: 32 info leak instances | grep in Level 1 |
| Explicit units in all params (`_mm`, `_kn`, `_knm`) | Prevents unit confusion | code review |
| All `__all__` entries must be importable | v0.21.2: phantom API claims | Level 2 test |
| Data files must be in pyproject.toml package-data | v0.21.2: missing clauses.json | Level 3 wheel test |

### FastAPI (`fastapi_app/`)

| Rule | Rationale | How Checked |
|------|-----------|-------------|
| All routers must sanitize errors | v0.21.3 EA-18: CWE-209 | grep for str(e) |
| All endpoints must have rate limiting | v0.21.3 EA-17: DoS risk | middleware check |
| WebSocket inputs validated via Pydantic | v0.21.3 EA-19 | code review |
| CORS from config, not hardcoded | v0.21.3 EA-20 | code review |

### React (`react_app/`)

| Rule | Rationale | How Checked |
|------|-----------|-------------|
| Forms must have cross-field validation | v0.21.3 EA-15 | code review |
| All computations go through FastAPI | Architecture rule | code review |
| No duplicate hooks/components | Historical duplication | `ls hooks/ && grep` |

### Tests (`Python/tests/`)

| Rule | Rationale | How Checked |
|------|-----------|-------------|
| Never MagicMock structural Result types | v0.21.0: ShearResult bug masked | grep in Level 1 |
| repo_only marker for repo-dependent tests | v0.21.3 EA-8: broken sdist | code review |
| E2E pipeline test must exist for each element | v0.21.3 EA-7: no chain testing | test catalog |

## Report Format

```
## Quality Gate Report: Level [1/2/3]

| Check | Status | Details |
|-------|--------|---------|
| [check name] | ✅/❌/⚠️ | [details] |

**Gate:** PASS / FAIL
**Blockers:** [list any Level 1-2 failures]
**Warnings:** [list any non-blocking issues]
```

## Who Uses This

- **@reviewer** — runs Level 2 for every PR review
- **@ops** — runs Level 1 pre-commit checks
- **@tester** — can run any level for validation
- **@ops** — runs Level 3 before releases