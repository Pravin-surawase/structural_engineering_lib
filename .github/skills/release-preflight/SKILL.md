---
name: release-preflight
description: "Pre-release validation — packaging verification, user acceptance testing, security scan, API drift detection. Prevents the recurring pattern of shipping broken wheels and missing files."
---

# Release Preflight Skill

Comprehensive pre-release validation that catches the issues we've repeatedly shipped: missing package data, broken imports, security gaps, API/doc drift, and silent failures.

## When to Use

- **Before ANY version release** — run the full checklist
- **Before creating a release PR** — catch issues before they reach PyPI
- **After fixing audit findings** — verify fixes actually work from user perspective

## Why This Exists

v0.21.0 through v0.21.3 required 4 releases in 2 days because we shipped:
- Missing `clauses.json` in wheel (silent failure)
- Tests packaged in wheel (scope leak)
- 32 instances of `str(e)` leaking internals
- Rate limiting on only 2/60 endpoints
- README advertising non-existent functions
- Import-time warnings breaking user scripts

## Full Preflight Checklist (ALL steps mandatory)

### Phase 1: Packaging Verification (5 min)

```bash
# 1. Build wheel and sdist
cd Python && ../.venv/bin/python -m build

# 2. Verify wheel contents (no tests/, no scripts/)
unzip -l dist/*.whl | grep -E "tests/|scripts/|examples/" && echo "FAIL: leaked files" || echo "PASS"

# 3. Verify required data files
unzip -l dist/*.whl | grep "clauses.json" && echo "PASS" || echo "FAIL: clauses.json missing"

# 4. Install in clean temp venv and test imports
python -m venv /tmp/test_release && \
  /tmp/test_release/bin/pip install dist/*.whl && \
  /tmp/test_release/bin/python -c "import structural_lib; print(structural_lib.__version__)" && \
  rm -rf /tmp/test_release
```

### Phase 2: User Acceptance Test (10 min)

```bash
# 5. Import silence test — ZERO warnings allowed
/tmp/test_release/bin/python -W error -c "import structural_lib"

# 6. Core workflow: design → detailing → BBS → report
/tmp/test_release/bin/python -c "
from structural_lib import design_beam_is456, build_detailing_input, compute_detailing, compute_bbs
result = design_beam_is456(units='IS456', b_mm=300, D_mm=500, d_mm=450, fck_nmm2=25, fy_nmm2=500, mu_knm=150, vu_kn=100)
assert result.flexure.is_safe, 'Design should be safe'
print('PASS: Core workflow')
"

# 7. Verify all __all__ exports are importable
/tmp/test_release/bin/python -c "
import structural_lib
for name in structural_lib.__all__:
    obj = getattr(structural_lib, name)
    assert obj is not None, f'{name} is None'
print(f'PASS: All {len(structural_lib.__all__)} exports importable')
"

# 8. Verify README code examples actually work
# Run examples/end_to_end_workflow.py against installed package
```

### Phase 3: Security Quick Scan (5 min)

```bash
# 9. Check for str(e) in router error responses
grep -rn "str(e)" fastapi_app/routers/ && echo "FAIL: raw exception strings" || echo "PASS"

# 10. Check for bare except clauses
grep -rn "except Exception:" Python/structural_lib/ | grep -v "# nosec" && echo "WARNING: bare except" || echo "PASS"

# 11. Dependency vulnerability scan
.venv/bin/pip-audit 2>/dev/null || echo "SKIP: pip-audit not installed"
```

### Phase 4: API/Doc Consistency (5 min)

```bash
# 12. Verify README claims match actual API
.venv/bin/python -c "
import structural_lib
readme_functions = ['design_beam_is456', 'build_detailing_input', 'compute_detailing',
                    'compute_bbs', 'compute_dxf', 'compute_report', 'optimize_beam_cost',
                    'check_beam_is456', 'design_column_axial_is456']
for func in readme_functions:
    assert hasattr(structural_lib, func), f'README claims {func} but not in package'
print('PASS: All README functions exist')
"

# 13. Version consistency
.venv/bin/python scripts/check_doc_versions.py

# 14. OpenAPI baseline check (if FastAPI changed)
diff <(.venv/bin/python -c "from fastapi_app.main import app; import json; print(json.dumps(app.openapi(), indent=2))") fastapi_app/openapi_baseline.json || echo "WARNING: OpenAPI schema changed"
```

### Phase 5: CI Green Check (2 min)

```bash
# 15. Full test suite
.venv/bin/pytest Python/tests/ -v --tb=short

# 16. FastAPI tests
.venv/bin/pytest fastapi_app/tests/ -v --tb=short

# 17. React build
cd react_app && npm run build
```

## Report Format

```
## Release Preflight: v{VERSION}

| Phase | Status | Issues |
|-------|--------|--------|
| Packaging | ✅/❌ | [details] |
| User Acceptance | ✅/❌ | [details] |
| Security | ✅/❌ | [details] |
| API/Doc Consistency | ✅/❌ | [details] |
| CI Green | ✅/❌ | [details] |

**Verdict:** READY / NOT READY
**Blockers:** [list any]
```

## Integration

- **Ops agent** runs this before `./run.sh release run X.Y.Z`
- **Reviewer agent** verifies preflight report before approving release PR
- **Tester agent** can run Phase 2 independently for regression testing