---
name: user-acceptance-test
description: "Test the library from an end-user perspective — pip install, import, run all workflows. Catches packaging, import, and API issues that internal tests miss."
---

# User Acceptance Test Skill

Simulates what a real structural engineer experiences when they install and use the library. This is the test we never ran before v0.21.0, which led to 4 emergency releases.

## When to Use

- **Before every release** — mandatory gate
- **After packaging changes** — pyproject.toml, __init__.py, __all__ changes
- **After API surface changes** — new/renamed/removed public functions
- **After fixing audit findings** — verify fixes from user's view

## Why This Exists

### Issues caught only by users (not our CI):
1. `clauses.json` missing from wheel → clause traceability silently returns `{}`
2. `import structural_lib` emits deprecation warnings → breaks `-W error` users
3. README says `optimize_pareto_front()` exists → ImportError for users
4. `compute_report()` returns str or Path or list[Path] depending on args → type confusion
5. No `build_detailing_input()` documented → users can't build detailing dicts
6. Tests shipped inside wheel → bloated install

## Test Scenarios

### Scenario 1: Fresh Install (2 min)

```bash
# Create isolated environment
python -m venv /tmp/uat_test
source /tmp/uat_test/bin/activate

# Install from local wheel (pre-release) or PyPI (post-release)
pip install dist/structural_lib_is456-*.whl  # or: pip install structural-lib-is456

# Verify clean import
python -W error::DeprecationWarning -c "import structural_lib; print(f'v{structural_lib.__version__}')"
```

### Scenario 2: Basic Beam Design (2 min)

```python
from structural_lib import design_beam_is456

result = design_beam_is456(
    units="IS456", b_mm=300, D_mm=500, d_mm=450,
    fck_nmm2=25, fy_nmm2=500,
    mu_knm=150, vu_kn=100,
)
assert result.flexure.is_safe
assert result.flexure.Ast_required > 0
assert result.shear.is_safe
print(f"✅ Beam design: Ast={result.flexure.Ast_required:.0f} mm²")
```

### Scenario 3: Full Pipeline (5 min)

```python
from structural_lib import (
    design_beam_is456, build_detailing_input, compute_detailing,
    compute_bbs, compute_report
)

# Step 1: Design
result = design_beam_is456(
    units="IS456", b_mm=300, D_mm=500, d_mm=450,
    fck_nmm2=25, fy_nmm2=500, mu_knm=150, vu_kn=100,
)

# Step 2: Detailing
detailing_input = build_detailing_input(
    result, beam_id="B1", b_mm=300, D_mm=500, d_mm=450,
    span_mm=6000, cover_mm=30, fck_nmm2=25, fy_nmm2=500,
)
detailed = compute_detailing(detailing_input)

# Step 3: BBS
bbs = compute_bbs(detailed, project_name="UAT Test")
assert bbs.summary.total_weight_kg > 0

# Step 4: Report
report_html = compute_report(detailing_input, format="html")
assert len(report_html) > 100

print(f"✅ Full pipeline: {bbs.summary.total_weight_kg:.1f} kg steel")
```

### Scenario 4: CSV Import (3 min)

```python
from structural_lib.services.adapters import GenericCSVAdapter

adapter = GenericCSVAdapter()
# Test with sample CSV
sample = "beam_id,b_mm,D_mm,d_mm,fck,fy,Mu_kNm,Vu_kN\nB1,300,500,450,25,500,150,100"
import tempfile, os
with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
    f.write(sample)
    path = f.name
beams = adapter.parse_file(path)
os.unlink(path)
assert len(beams) == 1
print(f"✅ CSV import: {len(beams)} beam(s) parsed")
```

### Scenario 5: Column Design (2 min)

```python
from structural_lib import design_column_axial_is456, classify_column_is456

classification = classify_column_is456(
    unsupported_length_mm=3000, least_lateral_dimension_mm=300
)
assert classification is not None

result = design_column_axial_is456(
    b_mm=300, D_mm=300, fck=25, fy=415,
    Pu_kN=1500, unsupported_length_mm=3000
)
assert result is not None
print(f"✅ Column design complete")
```

### Scenario 6: API Surface Completeness (1 min)

```python
import structural_lib

# Verify all __all__ exports are real objects
for name in structural_lib.__all__:
    obj = getattr(structural_lib, name, None)
    assert obj is not None, f"FAIL: {name} in __all__ but None"

# Verify no import-time side effects
import warnings
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    import importlib
    importlib.reload(structural_lib)
    user_warnings = [x for x in w if not issubclass(x.category, DeprecationWarning)]
    assert len(user_warnings) == 0, f"FAIL: {len(user_warnings)} warnings on import"

print(f"✅ API surface: {len(structural_lib.__all__)} exports verified")
```

## Cleanup

```bash
deactivate
rm -rf /tmp/uat_test
```

## Report Format

```
## User Acceptance Test Report

| Scenario | Status | Notes |
|----------|--------|-------|
| Fresh Install | ✅/❌ | [version, any warnings] |
| Basic Beam Design | ✅/❌ | [Ast value, is_safe] |
| Full Pipeline | ✅/❌ | [steel weight, report length] |
| CSV Import | ✅/❌ | [beam count] |
| Column Design | ✅/❌ | [classification] |
| API Surface | ✅/❌ | [export count, warning count] |

**Verdict:** ALL PASS / FAILURES FOUND
**Issues:** [list any failures with details]
```

## Who Runs This

- **@tester** runs during pre-release validation
- **@ops** includes in release preflight pipeline
- **@reviewer** verifies UAT report before release approval
