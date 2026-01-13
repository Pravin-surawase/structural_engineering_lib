# Nomenclature Standardization Audit

**Task:** TASK-166
**Date:** 2026-01-06
**Status:** Complete
**Scope:** Naming standards across Python, VBA, and documentation, including abbreviations and unit suffix conventions.

---

## Executive Summary
The codebase uses consistent domain abbreviations (Mu, Vu, Ast, fck, fy) but applies naming conventions unevenly between API boundary functions, core calculation functions, and VBA modules. Python naming mixes `calculate_*`, `compute_*`, `get_*`, `design_*`, and unprefixed names; VBA uses PascalCase with underscores; docs alternate between `IS456`, `IS 456`, and `IS-456`. This is manageable now but will become a scaling cost as new modules and contributors are added. Standardizing naming patterns and documenting abbreviations will improve readability, reduce unit mistakes, and make Python/VBA parity audits faster.

## Methodology
- Scanned Python function name prefixes in `Python/structural_lib` via regex.
- Reviewed representative Python modules (`api.py`, `flexure.py`, `shear.py`, `detailing.py`).
- Reviewed representative VBA modules (`VBA/Modules/M06_Flexure.bas`).
- Reviewed documentation naming and terminology in `docs/` and `docs/reference/`.

## Findings

### 1) Python Naming Audit
Observed prefix distribution (from function definitions):
- `calculate_*` (most common explicit prefix)
- `get_*`, `validate_*`, `check_*`, `export_*`, `design_*`, `generate_*`, `compute_*`
- A large set of functions without a prefix (single-word function names or domain names).

Issues:
- **Inconsistent verb usage:** similar operations use `calculate_*` vs `compute_*` vs `get_*`.
- **Unit suffixes not uniform:** API boundary functions use `*_mm`, `*_knm`, `*_nmm2`, but core functions often use `b`, `d`, `fck`, `fy` without explicit unit suffixes.
- **Domain abbreviations:** abbreviations are used consistently but are not defined centrally.

### 2) VBA Naming Audit
Patterns:
- PascalCase with underscores, e.g., `Calculate_Mu_Lim`, `Design_Singly_Reinforced`.
- Module naming uses `M##_Name` conventions (e.g., `M06_Flexure`).

Issues:
- **Mixed casing vs Python:** VBA uses PascalCase; Python uses snake_case.
- **Underscore usage inconsistent:** Some VBA functions include multiple underscores; others use fewer.
- **Units not explicit in function names:** most functions rely on doc comments.

### 3) Documentation Terms Audit
Observed inconsistencies:
- `IS456` vs `IS 456` vs `IS-456`.
- `kN-m` vs `kNm` vs `kN m`.
- `Mu` vs `M_u` vs `mu` (case and formatting differences).
- `BBS` vs `Bar Bending Schedule` in headings vs body text.

### 4) Abbreviations Inventory (Core)
Common abbreviations and recommended meanings:
- **Mu**: factored bending moment (kN-m)
- **Vu**: factored shear (kN)
- **Ast**: area of tension reinforcement (mm^2)
- **Asc**: area of compression reinforcement (mm^2)
- **Asv**: area of shear reinforcement (mm^2)
- **fck**: characteristic compressive strength of concrete (N/mm^2)
- **fy**: yield strength of steel (N/mm^2)
- **b, D, d**: beam width, total depth, effective depth (mm)
- **xu/xu_max**: neutral axis depth and maximum depth (mm)
- **pt**: percentage of tension steel (%)
- **tv/tc**: nominal shear stress / concrete shear capacity (N/mm^2)
- **Ld**: development length (mm)
- **BBS**: Bar Bending Schedule
- **DXF**: Drawing Exchange Format

## Proposed Standards

### Function Naming Rules (Python)
- **`calculate_*`**: deterministic formula output (single quantity).
- **`check_*`**: validation or compliance checks returning `is_ok` or `is_safe`.
- **`design_*`**: full design routines that produce a result object.
- **`compute_*`**: orchestration-level wrapper that assembles or aggregates outputs.
- **`get_*`**: simple lookups or constant retrieval.
- **`export_*` / `load_*`**: I/O boundaries only.

### Variable Naming Rules (Python)
- **Boundary/API functions:** use explicit unit suffixes (`b_mm`, `mu_knm`, `fck_nmm2`).
- **Core functions:** allow short names (`b`, `d`, `fck`) but require unit comment in docstring.
- **Avoid ambiguous abbreviations** unless documented in glossary.

### Module/File Naming Rules
- Avoid `types.py` due to stdlib conflicts; prefer `data_types.py` or `*_types.py`.
- Use kebab-case for docs, snake_case for Python modules, PascalCase for VBA functions.

### Documentation Style Guide (Terms)
- **Standard term:** `IS 456` (with a space) in prose; `IS456` only in identifiers.
- **Units:** `kN-m` in prose, `*_knm` in identifiers.
- **Symbols:** `Mu`, `Vu`, `Ast`, `Asc`, `Asv` (case-sensitive, no underscores in prose).

## Recommendations
1. Publish a short glossary of abbreviations in a canonical reference doc.
2. Document naming rules (verbs + units) in the development guide.
3. Apply standards to new code first; refactor older modules incrementally.

## Action Plan
Priority | Action | Effort
---|---|---
P1 | Add glossary and naming rules to `docs/contributing/development-guide.md` | 0.5 day
P1 | Align API boundary parameter naming (units suffixes) in docs/examples | 0.5 day
P2 | Normalize naming in new modules and refactor high-traffic files over time | 1-2 days

## Migration Plan
1. **Define glossary:** add abbreviations list to `docs/reference/known-pitfalls.md` or a new `docs/reference/glossary.md`.
2. **Establish naming rules:** document in `docs/contributing/development-guide.md`.
3. **Align new code first:** enforce naming rules for all new modules.
4. **Incremental refactor:** target high-traffic modules first (API, core calculations) with minimal diffs.
5. **VBA alignment:** update VBA comments to match Python naming and units.

## Examples

Before:
- `calculate_mu_lim(b, d, fck, fy)`
- `compute_detailing(design_results, config=None)`

After (standardized usage):
- `calculate_mu_lim(b, d, fck, fy)` (core calc - keep, add unit docstring)
- `compute_detailing(...)` (orchestration wrapper - keep)
- `design_beam_is456(...)` (full design - keep)

## Additional Research Opportunities

### High Value Additions (Optional)

1. **Quantified Prefix Distribution** (1 hour)
   ```bash
   # Count functions by prefix
   rg "^def (calculate|compute|check|design|get|validate)_" Python/structural_lib/ --count
   ```
   **Benefit:** Exact metrics for naming consistency

2. **Third-Party Library Analysis** (2 hours)
   - Survey naming conventions in: numpy, scipy, pandas, sympy
   - Identify patterns we should follow for consistency
   - Document rationale for deviations
   **Benefit:** Align with ecosystem standards

3. **Related Structural Libraries Survey** (2-3 hours)
   - Analyze naming in: OpenSees, PyNite, anastruct
   - Document domain-specific conventions
   - Identify best practices for engineering libraries
   **Benefit:** Domain-appropriate naming standards

4. **Before/After Impact Analysis** (1 hour)
   - Create examples for each proposed naming change
   - Estimate API stability impact (breaking vs non-breaking)
   - Calculate refactoring effort per module
   **Benefit:** Clear cost/benefit for each change

## Enhancement Recommendations

### For Implementation Phase
1. **Automated Enforcement** - Add ruff/custom rules for naming conventions
2. **Migration Tool** - Script to rename functions following new standards
3. **API Stability Labels** - Mark functions by stability (stable/experimental/deprecated)

### Tracking Metrics
```bash
# Naming consistency check
rg "^def [A-Z]" Python/structural_lib/  # PascalCase (should be 0)
rg "IS456|IS 456|IS-456" docs/ | sort -u  # Variant count (target: 1)
rg "kN-m|kNm|kN m" docs/ | sort -u  # Unit variants (target: 1)
```

## References
- `Python/structural_lib/api.py`
- `Python/structural_lib/flexure.py`
- `VBA/Modules/M06_Flexure.bas`
- `docs/reference/known-pitfalls.md`
