# Code Style Consistency Audit

**Task:** TASK-169
**Date:** 2026-01-06
**Status:** Complete
**Scope:** Python and VBA code style consistency including formatting, docstrings, comments, TODOs, and duplication risks.

---

## Executive Summary
The codebase is largely consistent in structure and style, with strong module-level docstrings and a standardized lint/format toolchain (black + ruff). The main gaps are (1) limited ruff rule coverage (pyflakes only), (2) a small set of TODO markers in production code, and (3) no documented docstring style guide. There is no evidence of widespread formatting drift, but a deeper automated audit (ruff rule expansion, vulture for dead code) would better quantify remaining risk.

## Methodology
- Reviewed lint/format configuration in `Python/pyproject.toml`.
- Scanned Python modules for module-level docstrings.
- Indexed TODO/FIXME/HACK markers in Python/VBA.
- Spot-checked core modules for comment clarity and unit annotations.

## Findings

### 1) Black/Ruff Report
- **Black:** configured via pre-commit; no explicit file list, but standard formatting appears consistent.
- **Ruff:** configured with `select = ["F"]` (pyflakes only). This means style, complexity, and docstring rules are not enforced.
- **Ruff run (pyflakes only):** `ruff check --statistics Python/structural_lib` returned 0 findings.

Recommendation: Expand ruff rules gradually (E/W/I or select targeted rule sets) to increase automated style consistency without overwhelming churn.

### 2) Docstring Audit
- **Module docstrings:** all scanned Python modules in `Python/structural_lib` include top-level docstrings (0 missing).
- **Function docstrings:** no consistent format documented (Google vs NumPy vs reST). Mixed levels of detail.

Recommendation: adopt a lightweight docstring standard (e.g., Google style for new functions) and update high-traffic APIs first.

### 3) Comment Audit
- No large blocks of commented-out code detected in spot checks.
- Comments are mostly descriptive and unit-oriented, which is good for engineering formulas.

### 4) TODO/FIXME/HACK Inventory
Markers found:
- `Python/structural_lib/__main__.py`: TODO for constructability scoring integration.
- `Python/structural_lib/insights/comparison.py`: TODOs for constructability and sensitivity integration.

Total markers: 3 across 2 files.

Recommendation: convert TODOs to explicit tasks (with IDs) or resolve during next feature iteration to avoid drift.

### 5) Dead Code / Magic Numbers / Duplication
- No automated dead-code scan performed.
- Domain constants appear to be embedded in code and comments; some may warrant extraction into named constants.
- Duplication risk exists between Python/VBA implementations; parity checks mitigate this, but naming and constants should be consolidated where practical.

### 6) Quantitative Size Metrics
- **Modules scanned:** 37 Python modules in `Python/structural_lib`.
- **Total LOC:** 15,744 lines (all modules combined).
- **Largest modules by LOC:** `report.py` (1545), `dxf_export.py` (1376), `api.py` (1255), `bbs.py` (1004), `serviceability.py` (873).

### 7) Complexity Metrics (radon cc)
- **Blocks analyzed:** 99 (functions, methods, classes).
- **Average complexity:** C (12.81).
- **Grade counts:** A: 262, B: 52, C: 36, D: 7, E: 4.
- **Highest complexity items (D/E):**
  - E 40: `Python/structural_lib/insights/smart_designer.py:246` `SmartDesigner`
  - E 39: `Python/structural_lib/insights/smart_designer.py:268` `analyze`
  - E 37: `Python/structural_lib/insights/constructability.py:25` `calculate_constructability_score`
  - E 36: `Python/structural_lib/flexure.py:462` `design_flanged_beam`
  - D 28: `Python/structural_lib/__main__.py:121` `cmd_design`
  - D 27: `Python/structural_lib/dxf_export.py:1041` `generate_multi_beam_dxf`
  - D 27: `Python/structural_lib/insights/precheck.py:35` `quick_precheck`
  - D 24: `Python/structural_lib/api.py:310` `compute_detailing`
  - D 23: `Python/structural_lib/report.py:250` `get_input_sanity`
  - D 22: `Python/structural_lib/compliance.py:285` `check_compliance_report`

### 8) Maintainability Index (radon mi)
- **Average MI:** 62.18.
- **Lowest 5 MI files:**
  - 11.81 (B) `Python/structural_lib/report.py`
  - 13.96 (B) `Python/structural_lib/__main__.py`
  - 20.44 (A) `Python/structural_lib/dxf_export.py`
  - 33.63 (A) `Python/structural_lib/flexure.py`
  - 34.10 (A) `Python/structural_lib/api.py`

### 9) Dead Code Scan (vulture --min-confidence 80)
Findings (2):
- `Python/structural_lib/bbs.py:459` unused variable `include_hooks`.
- `Python/structural_lib/insights/comparison.py:340` unused variable `structural_sens`.

### 10) Numeric Literals (magic-number proxy)
Token-based numeric literal count (NUMBER tokens only):
- **Total numeric literals:** 1,783.
- **Top files by numeric literals:**
  - `Python/structural_lib/dxf_export.py` (292)
  - `Python/structural_lib/flexure.py` (150)
  - `Python/structural_lib/tables.py` (136)
  - `Python/structural_lib/detailing.py` (124)
  - `Python/structural_lib/bbs.py` (101)
  - `Python/structural_lib/serviceability.py` (98)

## Recommendations
1. **Expand ruff rules** incrementally (e.g., `E`, `W`, `I`, `B`) to capture common style issues.
2. **Adopt a docstring style guide** and add to `docs/contributing/development-guide.md`.
3. **Convert TODO markers into tasks** or remove them if obsolete.
4. **Add lightweight dead-code detection** (e.g., vulture) for periodic audits.

## Action Plan
Priority | Action | Effort
---|---|---
P1 | Adopt docstring format standard and apply to core API modules | 1 day
P1 | Expand ruff rules (start with import sorting or complexity checks) | 0.5 day
P2 | Resolve or formalize TODOs in `__main__.py` and `insights/comparison.py` | 0.5 day
P3 | Add periodic dead-code scan using vulture or a custom script | 0.5 day

## Additional Research Opportunities

### High Value Additions (RECOMMENDED)

1. **Quantified Style Metrics** (1 hour) - **HIGH PRIORITY**
   ```bash
   # Install tools
   pip install radon vulture

   # Lines of code by module
   find Python/structural_lib -name "*.py" -exec wc -l {} + | sort -n

   # Complexity analysis
   radon cc -a -nb Python/structural_lib > complexity_report.txt
   radon mi -s Python/structural_lib > maintainability_report.txt

   # Ruff statistics
   ruff check --statistics Python/structural_lib > ruff_stats.txt
   ```
   **Benefit:** Baseline metrics for tracking improvement

2. **Magic Number Inventory** (1-2 hours) - **HIGH PRIORITY**
   ```bash
   # Find magic numbers (candidates)
   rg "\b(\d+\.\d+|\d{2,})\b" Python/structural_lib --type py

   # Categorize:
   # - IS 456 constants (0.87, 0.36, etc.)
   # - Unit conversions (1000, 1000000)
   # - Table lookups (15, 20, 25, 30, 35, 40)
   ```
   **Benefit:** Identify constants that should be named

3. **Code Duplication Analysis** (1 hour)
   ```bash
   # Find duplicate code blocks
   pylint --disable=all --enable=duplicate-code Python/structural_lib

   # Or use PMD copy-paste detector
   # https://pmd.github.io/latest/pmd_userdocs_cpd.html
   ```
   **Benefit:** Identify refactoring opportunities

4. **Import Structure Analysis** (30 min)
   ```bash
   # Check for circular imports
   pydeps Python/structural_lib --show-deps

   # Import depth analysis
   rg "^(import|from)" Python/structural_lib --count-matches
   ```
   **Benefit:** Detect architectural issues

5. **Comment-to-Code Ratio** (30 min)
   ```bash
   # Count comments vs code
   find Python/structural_lib -name "*.py" -exec sh -c '
     comments=$(grep -c "^\s*#" "$1" || echo 0)
     code=$(grep -c "^\s*[^#]" "$1" || echo 0)
     echo "$1: $comments comments, $code code lines"
   ' _ {} \;
   ```
   **Benefit:** Identify under-commented modules

6. **Dead Code Detection** (1 hour)
   ```bash
   # Find unused functions/variables
   vulture Python/structural_lib --min-confidence 80
   ```
   **Benefit:** Clean up unused code

## Enhancement Recommendations

### For Implementation Phase

1. **Expanded Ruff Configuration**
   ```toml
   [tool.ruff]
   select = [
     "F",   # Pyflakes (current)
     "E",   # pycodestyle errors
     "W",   # pycodestyle warnings
     "I",   # isort (import sorting)
     "N",   # pep8-naming
     "UP",  # pyupgrade
     "B",   # flake8-bugbear
     "C4",  # flake8-comprehensions
     "PIE", # flake8-pie (includes magic number detection)
   ]
   ```

2. **Docstring Style Guide** (Google Style)
   ```python
   def calculate_mu_lim(b: float, d: float, fck: float, fy: float) -> float:
       """Calculate limiting moment of resistance.

       Args:
           b: Width of beam in mm
           d: Effective depth in mm
           fck: Characteristic compressive strength in N/mm²
           fy: Yield strength of steel in N/mm²

       Returns:
           Limiting moment in kN·m

       Raises:
           ValueError: If any dimension is non-positive

       References:
           IS 456:2000, Cl. 38.1
       """
   ```

3. **Magic Number Constants File**
   ```python
   # Python/structural_lib/constants.py
   """IS 456:2000 design constants."""

   # Stress block factors (Cl. 38.1)
   STRESS_BLOCK_FACTOR_K1 = 0.36
   STRESS_BLOCK_FACTOR_K2 = 0.42
   STRESS_BLOCK_FACTOR_K3 = 0.48
   STRESS_BLOCK_FACTOR_K4 = 0.87

   # Unit conversions
   KN_TO_N = 1000
   KNM_TO_NMM = 1_000_000
   ```

### Tracking Metrics
```bash
# Code quality dashboard
ruff check --statistics Python/structural_lib | grep "Found"
radon cc -a Python/structural_lib | grep "Average complexity"
vulture Python/structural_lib --min-confidence 80 | wc -l  # Dead code count
rg "TODO|FIXME|HACK" Python/structural_lib | wc -l  # Marker count (target: 0)
```

## Quantitative Baseline (To Be Added)

**Run these commands and add results:**
```bash
# 1. Total lines of code
find Python/structural_lib -name "*.py" -exec wc -l {} + | tail -1

# 2. Average complexity
radon cc -a Python/structural_lib | grep "Average"

# 3. Maintainability index
radon mi -s Python/structural_lib

# 4. Current ruff violations
ruff check Python/structural_lib --statistics

# 5. Magic number count
rg "\b\d{2,}\b" Python/structural_lib --type py | wc -l
```

## References
- `Python/pyproject.toml`
- `Python/structural_lib/__main__.py`
- `Python/structural_lib/insights/comparison.py`
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Radon Documentation](https://radon.readthedocs.io/)
