# Project Hygiene & File Organization Audit

**Task:** TASK-165
**Date:** 2026-01-06
**Status:** Complete
**Scope:** Repository-wide hygiene audit focused on duplicate files, obsolete content, naming consistency, broken links, and directory structure.

---

## Executive Summary
The repo is functionally healthy, but its documentation and file organization have drifted into a multi-root structure (top-level docs plus topical subfolders) that increases maintenance cost and link breakage. Duplicate filenames and parallel doc trees (e.g., `docs/project-overview.md` vs `docs/architecture/project-overview.md`) create ambiguity about canonical sources. Broken links exist in critical docs and research notes, and several top-level docs reflect older versioning, which reduces trust in the current release narrative. Build artifacts and OS metadata (`.coverage`, `.DS_Store`) are present and should be cleaned or ignored consistently.

Top 5 issues:
1. **Duplicate docs across multiple roots** (top-level `docs/*.md` vs `docs/**/`), creating canonical ambiguity.
2. **Broken internal links** in core onboarding docs and troubleshooting references.
3. **Outdated/legacy planning docs** still in primary doc trees (v0.10-v0.12 era) without clear archive labeling.
4. **Naming inconsistency** (UPPERCASE vs kebab-case, underscores vs hyphens) across docs and directories.
5. **Tracked artifacts** like `.coverage` and `.DS_Store` in repo root and subfolders.

## Methodology
- Enumerated repository structure with `ls docs`.
- Identified duplicate filenames using a Python scan (excluding `.venv`/cache/build directories).
- Scanned for backup artifacts using `rg --files -g` with common backup globs.
- Ran `scripts/check_links.py` to identify broken internal links.
- Spot-checked representative docs and structure for canonicality and organization.

## Findings

### 1) Duplicate Files Report
Duplicates (non-venv, non-cache) identified by basename:
- **`LICENSE`**:
  - `LICENSE`
  - `Python/LICENSE`
  - Recommendation: keep root `LICENSE` as canonical; remove or replace `Python/LICENSE` with a short pointer file if packaging requires it.
- **`README.md`** (25 locations):
  - `README.md`, `docs/README.md`, `docs/reference/README.md`, `docs/architecture/README.md`, etc.
  - Recommendation: maintain a single top-level `docs/README.md` as the documentation index; keep subfolder READMEs as local indexes, but link clearly to the canonical root doc index.
- **`SUPPORT.md`**:
  - `SUPPORT.md`
  - `agents/SUPPORT.md`
  - Recommendation: keep root `SUPPORT.md` as canonical; in `agents/`, link to it rather than duplicating.
- **`types.py` / `data_types.py`**:
  - `Python/structural_lib/types.py` and `Python/structural_lib/insights/types.py`
  - `Python/structural_lib/data_types.py` and `Python/structural_lib/insights/data_types.py`
  - Recommendation: this is an intentional domain split but creates naming collisions and import confusion; document the separation explicitly and prefer `*_types.py` naming if refactoring.

### 2) Obsolete Content Report
Likely archive candidates (still referenced in active doc trees):
- `docs/v0.7-requirements.md`
- `docs/v0.8-execution-checklist.md`
- `docs/planning/v0.12-plan.md`
- `docs/planning/production-roadmap.md` (current state references v0.10.x)
- `docs/planning/project-status.md` (current release listed as v0.11.0)

Recommendation: move clearly historical planning docs to `docs/_archive/` and leave a short redirect stub in `docs/planning/` for preserved linking.

Removal candidates (if not required for auditing):
- `.coverage` in repo root and `Python/.coverage`
- `.DS_Store` in root/Excel/VBA

### 3) Naming Inconsistencies
- **Docs:** uppercase + underscore (`ai-context-pack.md`) vs kebab-case (`project-overview.md`) vs title-style (`project-overview.md`).
- **Directories:** `docs/_internal`, `docs/_archive`, `docs/_references` mixed with `docs/reference` and `docs/architecture`.
- **Files:** `docs/project-overview.md` vs `docs/architecture/project-overview.md` (duplicate topic, different naming convention).

Recommendation: Standardize on **kebab-case** for file names and **lowercase** directory names; reserve `docs/_internal` and `docs/_archive` for non-user-facing content.

### 4) Broken Links Report
From `scripts/check_links.py` (2026-01-06):
- `docs/ai-context-pack.md` -> `.github/copilot-instructions.md` (should be `../.github/copilot-instructions.md`).
- `docs/research/documentation-handoff-analysis.md` -> `reference/automation-catalog.md` (should be `../reference/automation-catalog.md`).
- `docs/research/session-2026-01-06-documentation-enhancement.md` -> `reference/automation-catalog.md` (same issue, appears twice).
- `docs/research/research-methodology.md` -> `Paper title (link placeholder)` placeholder.
- `docs/troubleshooting/merge-conflict-prevention.md` -> `/.github/copilot-instructions.md` (should be `../.github/copilot-instructions.md`).
- `docs/troubleshooting/merge-conflict-prevention.md` -> `/scripts/check_unfinished_merge.sh` (script not present).
- `docs/getting-started/design-suggestions-guide.md` -> `./cost-optimization-guide.md` (missing file).

### 5) Directory Structure Assessment
Observations:
- `docs/` contains both top-level canonical docs and subfoldered versions of similar content.
- The repo has multiple "indices" (`docs/README.md`, `docs/reference/README.md`, etc.) without a clear canonical navigation path.
- `_internal` and `_archive` are used, but many historical planning docs remain in `docs/planning` without archive flags.

Proposal:
- Make `docs/README.md` the only canonical entrypoint.
- Move high-level guides into `docs/getting-started/` or `docs/reference/` and retain short stub files at the old locations for back-compat.
- Clearly mark "archived" planning docs in `docs/_archive/` and add a small index redirect in `docs/planning/`.

## Recommendations
1. **Canonicalize doc paths:** Choose one canonical location per topic and add redirect stubs where necessary.
2. **Fix broken links immediately:** The 8 identified broken links are low-effort, high-impact fixes.
3. **Archive historical planning docs:** Move pre-v0.13 planning artifacts to `docs/_archive/`.
4. **Adopt naming standard:** Kebab-case filenames; avoid uppercase/underscore for docs.
5. **Clean build artifacts:** Remove `.DS_Store` and `.coverage`; add rules to `.gitignore` if needed.

## Action Plan
Priority | Action | Effort
---|---|---
P0 | Fix 8 broken links identified by `check_links.py` | 1-2 hrs
P1 | Canonicalize top-level docs vs subfolder duplicates (project overview, API ref, workflow docs) | 0.5-1 day
P1 | Archive old planning docs (v0.10-v0.12 scope) with redirect stubs | 0.5 day
P2 | Standardize doc naming conventions (rename + link updates) | 1-2 days
P2 | Add repo hygiene checks for `.DS_Store`/`.coverage` | 1 hr

## File Organization Standards
- **Docs:** use kebab-case filenames, lowercase directories.
- **Canonical doc roots:**
  - `docs/README.md` (index)
  - `docs/getting-started/` (tutorials)
  - `docs/reference/` (API & technical reference)
  - `docs/architecture/` (design/architecture)
  - `docs/planning/` (current planning only)
  - `docs/_archive/` (historical/obsolete)
  - `docs/_internal/` (internal-only, not user-facing)
- **Redirect stubs:** When moving docs, leave a 3-5 line stub with a link to the canonical location.
- **No artifacts:** `.DS_Store`, `.coverage`, and build caches should not be committed.

## Additional Research Opportunities

### High Value Additions (Optional)

1. **File Size Analysis** (30 min)
   ```bash
   # Identify large docs that could be split
   find docs -name "*.md" -exec wc -l {} + | sort -n | tail -20
   ```
   **Benefit:** Identify documentation that's too long for single read

2. **Dead Link Analysis in Archives** (30 min)
   ```bash
   # Check archived docs for broken links
   scripts/check_links.py --include docs/_archive/
   ```
   **Benefit:** Ensure archived docs remain valid references

3. **Doc-to-Code Ratio by Module** (1 hour)
   ```bash
   # Calculate documentation coverage per module
   find Python/structural_lib -name "*.py" -exec wc -l {} + > code_lines.txt
   find docs -name "*.md" -exec wc -l {} + > doc_lines.txt
   ```
   **Benefit:** Identify under-documented vs over-documented modules

4. **Dependency Analysis** (1 hour)
   - Map P0/P1/P2 task dependencies
   - Create critical path diagram
   - Identify tasks that can run in parallel

## Enhancement Recommendations

### For Implementation Phase
1. **Create redirect stub template** - Standardize format for moved docs
2. **Add verification script** - Automate checking P0 completion
3. **Document canonicalization decisions** - Record which doc is canonical for each topic

### Tracking Metrics
```bash
# Weekly hygiene check
scripts/check_links.py  # Target: 0 broken links
find . -name "*.DS_Store" | wc -l  # Target: 0
rg "v0\.(10|11|12)" docs/ | wc -l  # Target: 0 (only v0.14+)
```

## References
- `scripts/check_links.py`
- Duplicate scan script (Python, filename-based)
- `rg --files` with backup globs
