# Repository Hygiene Audit Report - 2026-01-07

**Agent:** Project Hygiene & Maintenance Specialist (Agent 2)
**Mode:** Mode 1 (Audit & Document)
**Date:** 2026-01-07
**Branch:** audit/hygiene-2026-01-07

---

## Executive Summary

Comprehensive hygiene audit of the structural_engineering_lib repository identified **61 actionable items** across 5 priority categories:

- **P0 (Critical):** 18 issues - Fix immediately
- **P1 (High):** 30+ issues - Fix within sprint
- **P2 (Medium):** 13 issues - Nice to have

**Top Priority Issues:**
1. ✅ 17 broken internal links (5 critical, 12 placeholder/example)
2. ✅ 1 root `.coverage` file tracked by git (should be in Python/ only)
3. ✅ 4 git worktrees (2 active, 2 potentially stale)
4. ✅ 30+ UPPERCASE doc filenames (inconsistent naming)
5. ✅ 4 duplicate LICENSE/SUPPORT files across directories

**Repository Health Metrics:**
- Total markdown files checked: **267**
- Total internal links: **470**
- Repository size: **20M** (.git directory)
- Large files (>1MB): **3** (all mypy cache - safe)

---

## P0 (Critical) - Fix Immediately

### ISSUE-001: Broken Internal Links (17 total)

**Impact:** Documentation navigation broken, poor user experience
**Effort:** 2-3 hours
**Risk Level:** 🔴 HIGH

#### Category A: Real Broken Links (5) - CRITICAL

1. **docs/planning/background-agents-setup-complete.md**
   - Link: `[ai-enhancements.md](../research/ai-enhancements.md)`
   - Issue: File doesn't exist
   - Fix: Either create file or remove reference

2. **docs/planning/background-agents-setup-complete.md**
   - Link: `[detailing-research.md](../research/detailing-research.md)`
   - Issue: File doesn't exist
   - Fix: Either create file or remove reference

3. **docs/planning/v0.17-task-specs.md**
   - Link: `[LICENSE_ENGINEERING.md](LICENSE_ENGINEERING.md)`
   - Issue: File doesn't exist
   - Fix: Either create file or update link to existing LICENSE

4. **docs/planning/v0.17-task-specs.md**
   - Link: `[docs/legal/usage-guidelines.md](docs/legal/usage-guidelines.md)`
   - Issue: Directory/file doesn't exist
   - Fix: Either create legal directory or remove reference

5. **docs/guidelines/api-design-guidelines.md**
   - Link: `[Examples](examples/)`
   - Issue: Examples directory doesn't exist at that path
   - Fix: Create examples or link to existing Python/examples/

#### Category B: Placeholder/Example Links (12) - MEDIUM

These are in template/example sections but should still be fixed:

6-7. **docs/planning/agent-2-tasks.md** (3 links)
   - `[docs/_archive/original-filename.md]` - Example placeholder
   - `[Next Session Brief](planning/next-session-brief.md)` - Wrong path
   - `[SUPPORT.md](../SUPPORT.md)` - Correct path but example context

8-10. **docs/planning/agent-2-tasks.md** (3 links)
   - `[docs/_archive/old-file.md]` - Example placeholder
   - `[current-file.md](current-file.md)` - Example placeholder
   - All in code example blocks

11. **docs/planning/v0.17-task-specs.md**
   - Link: `[SECURITY.md](SECURITY.md)` - Wrong relative path
   - Fix: `[SECURITY.md](../../SECURITY.md)`

12-17. **docs/guidelines/api-evolution-standard.md** (6 links)
   - `[Migration Guide](link)` - Placeholder
   - `[FAQ](link)` - Placeholder
   - `[#123](link-to-issue)` - Placeholder
   - `[GitHub Discussions](link)` - Placeholder
   - `[GitHub Issues](link)` - Placeholder
   - All marked as TODOs in document

**Recommendations:**

```bash
# Fix critical broken links (Category A)
# Option 1: Create missing files
touch docs/research/ai-enhancements.md
touch docs/research/detailing-research.md

# Option 2: Remove broken references
# Edit files to remove non-existent links

# Fix SECURITY.md path
sed -i 's|[SECURITY.md](SECURITY.md)|[SECURITY.md](../../SECURITY.md)|g' docs/planning/v0.17-task-specs.md

# Fix examples/ path
# Edit docs/guidelines/api-design-guidelines.md
# Change: [Examples](examples/)
# To: [Examples](../../Python/examples/)

# Fix placeholder links in api-evolution-standard.md
# Either remove or replace with actual URLs
```

**Acceptance Criteria:**
- [ ] All 5 critical broken links resolved
- [ ] Placeholders either filled or marked clearly as TODO
- [ ] `./scripts/check_links.py` returns 0 broken links

---

### ISSUE-002: Build Artifacts Tracked in Git

**Impact:** Repository bloat, unnecessary commits
**Effort:** 15 minutes
**Risk Level:** 🔴 HIGH

**Files Found:**
1. `./.coverage` (root) - ❌ Should NOT be in root
2. `Python/.coveragerc` - ✅ OK (configuration file, should be tracked)

**Analysis:**
- Root `.coverage` file should not be tracked (it's generated data)
- Python/.coverage is not tracked (good)
- `.coveragerc` is a configuration file (correct to track)

**Recommendations:**

```bash
# Remove from git tracking
git rm --cached .coverage

# Verify .gitignore has coverage exclusion
grep -q "^/.coverage$" .gitignore || echo "/.coverage" >> .gitignore

# Verify Python/.coverage is ignored
grep -q "^Python/.coverage$" .gitignore || echo "Python/.coverage" >> .gitignore

# Commit
git add .gitignore
git commit -m "chore: remove root .coverage from tracking, update .gitignore"
```

**Verification:**
```bash
git ls-files | grep "\.coverage$"
# Should only return: Python/.coveragerc
```

**Acceptance Criteria:**
- [ ] Root `.coverage` removed from git tracking
- [ ] `.gitignore` updated
- [ ] Verified: `git ls-files | grep "\.coverage$"` shows only `.coveragerc`

---

### ISSUE-003: MyPy Cache Files Not Ignored

**Impact:** Large cache files (3MB+) not in .gitignore
**Effort:** 10 minutes
**Risk Level:** 🟠 MEDIUM-HIGH

**Files Found:**
1. `Python/.mypy_cache/` - 3.0MB total
2. `.mypy_cache/` - 1.6MB total

**Currently Untracked:** ✅ Good (not in git ls-files)

**Issue:** Not explicitly in .gitignore (risk of accidental commit)

**Recommendations:**

```bash
# Add to .gitignore if not present
grep -q "\.mypy_cache" .gitignore || cat >> .gitignore << 'EOF'

# MyPy cache
.mypy_cache/
*.mypy_cache/
EOF

# Verify not tracked
git ls-files | grep ".mypy_cache"
# Should return nothing
```

**Acceptance Criteria:**
- [ ] `.mypy_cache/` in .gitignore
- [ ] Verified not tracked by git

---

## P1 (High) - Fix Within Sprint

### ISSUE-004: Inconsistent File Naming (30+ files)

**Impact:** Poor repository organization, hard to find files
**Effort:** 4-6 hours (many link updates required)
**Risk Level:** 🟠 MEDIUM-HIGH

**Current Issues:**
- Mixed UPPERCASE and kebab-case in docs/
- Inconsistent: `AI_CONTEXT_PACK.md` vs `project-overview.md`

**Files with UPPERCASE naming (30 found):**

```
docs/research/API_DESIGN_PATTERN_ANALYSIS.md
docs/research/RESEARCH_METHODOLOGY.md
docs/MISSION_AND_PRINCIPLES.md
docs/TESTING_STRATEGY.md
docs/DEEP_PROJECT_MAP.md
docs/VERIFICATION_EXAMPLES.md
docs/RELEASES.md

docs/_internal/VERSION_STRATEGY.md
docs/_internal/QUALITY_GAPS_ASSESSMENT.md
docs/_internal/AGENT_WORKFLOW.md
docs/_internal/FOUNDATION_STATUS.md
docs/_internal/STRATEGIC_ROADMAP.md
docs/_internal/GIT_GOVERNANCE.md
docs/_internal/MULTI_AGENT_REVIEW_2025-12-28.md
docs/_internal/PROJECT_MILESTONES.md
docs/_internal/MAIN_AGENT_SUMMARY_2026-01-06.md
docs/_internal/AUTOMATION_IMPROVEMENTS.md

docs/_internal/tasks/TASK-142-design-suggestions.md

docs/_internal/copilot-tasks/ (14 files):
  HANDOFF_TO_COPILOT.md
  XLWINGS_QUICK_START.md
  TASK_1.1_BeamDesignSchedule_Spec.md
  PYTHON_EXCEL_RESEARCH_2025.md
  VSCODE_VBA_QUICKSTART.md
  XLWINGS_SOLUTION_SUMMARY.md
  COPILOT_WORKFLOW.md
  PROGRESS_TRACKER.md
  VBA_VSCODE_WORKFLOW.md
  XLWINGS_MIGRATION_PLAN.md
  XLWINGS_TEST_RESULTS.md
  TASK_0.1_xlwings_installation_COPILOT.md
  (and more...)
```

**Proposed Standard:**
- **Keep UPPERCASE:** `README.md`, `LICENSE`, `CHANGELOG.md`, `TASKS.md`, `SESSION_LOG.md` (important, high-visibility files)
- **Convert to kebab-case:** All other docs

**Recommendations (Phase approach):**

**Phase 1: High-visibility root docs/** (2-3 hours)
```bash
# Rename key files
git mv docs/MISSION_AND_PRINCIPLES.md docs/mission-and-principles.md
git mv docs/TESTING_STRATEGY.md docs/testing-strategy.md
git mv docs/DEEP_PROJECT_MAP.md docs/deep-project-map.md
git mv docs/VERIFICATION_EXAMPLES.md docs/verification-examples.md
git mv docs/RELEASES.md docs/releases.md

# Update links
rg -l "MISSION_AND_PRINCIPLES.md" | xargs sed -i 's|MISSION_AND_PRINCIPLES.md|mission-and-principles.md|g'
rg -l "TESTING_STRATEGY.md" | xargs sed -i 's|TESTING_STRATEGY.md|testing-strategy.md|g'
# ... repeat for each file

# Verify
./scripts/check_links.py
```

**Phase 2: docs/_internal/** (1-2 hours)
- Lower priority (internal docs)
- Can batch rename

**Phase 3: docs/_internal/copilot-tasks/** (1 hour)
- Lowest priority
- Historical/archived content

**Estimated Total Effort:** 4-6 hours

**Acceptance Criteria:**
- [ ] Phase 1 complete: Root docs/ files renamed
- [ ] All links updated and verified
- [ ] `./scripts/check_links.py` passes
- [ ] Document naming standard in contributing guide

---

### ISSUE-005: Duplicate LICENSE and SUPPORT Files

**Impact:** Maintenance burden, potential inconsistency
**Effort:** 30 minutes
**Risk Level:** 🟠 MEDIUM

**Files Found:**
```
./LICENSE (canonical - 1.1KB)
./Python/LICENSE (duplicate - 1.1KB)
./SUPPORT.md (canonical - 500 bytes)
./agents/SUPPORT.md (duplicate - 500 bytes)
```

**Analysis:**
- `Python/LICENSE` likely for PyPI package distribution (may be intentional)
- `agents/SUPPORT.md` is unnecessary duplication

**Recommendations:**

```bash
# Option 1: Replace duplicates with stubs (preferred)

# Python/LICENSE - Check if needed for PyPI
# If not needed:
git mv Python/LICENSE Python/LICENSE.bak
cat > Python/LICENSE << 'EOF'
# License

This package is licensed under the same terms as the main project.

See: [LICENSE](../LICENSE)
EOF
git add Python/LICENSE

# agents/SUPPORT.md - Replace with stub
git mv agents/SUPPORT.md agents/SUPPORT.md.bak
cat > agents/SUPPORT.md << 'EOF'
# Support

See the main project support documentation: [SUPPORT.md](../SUPPORT.md)
EOF
git add agents/SUPPORT.md

# Option 2: Remove completely (if not referenced)
git rm Python/LICENSE
git rm agents/SUPPORT.md

# Commit
git commit -m "chore: consolidate LICENSE and SUPPORT files"
```

**Decision Required from MAIN:**
- Keep Python/LICENSE for PyPI distribution?
- Replace with stub or remove completely?

**Acceptance Criteria:**
- [ ] Duplicate files handled (stub or removed)
- [ ] Links to canonical files working
- [ ] No broken references

---

### ISSUE-006: Git Worktrees Status (4 total, 2 potentially stale)

**Impact:** Disk space usage, confusion about active work
**Effort:** 1 hour (investigation + cleanup)
**Risk Level:** 🟡 MEDIUM

**Worktrees Found:**

#### Active Worktrees (Keep)

1. **worktree-2026-01-07T14-18-11**
   - Branch: `feature/RESEARCH-001-blog-strategy`
   - Status: 1 modified file (`smart-design-analysis-deep-dive.md`)
   - Last commit: "docs: complete RESEARCH-005 type safety blog post"
   - **Recommendation:** ✅ KEEP (active work by Agent 1)

2. **worktree-2026-01-07T14-39-08**
   - Branch: `worktree-2026-01-07T14-39-08`
   - Status: Clean (no uncommitted changes)
   - Last commit: "docs: transform agent 2 to project hygiene & maintenance specialist"
   - Commit: 07dacbc (same as main)
   - **Recommendation:** ✅ KEEP (current/recent - same as main HEAD)

#### Potentially Stale Worktrees (Investigate)

3. **worktree-2026-01-07T07-28-08**
   - Branch: `worktree-2026-01-07T07-28-08`
   - Status: Clean (no uncommitted changes)
   - Last commit: "docs: add comprehensive quality review report" (9eb6b47)
   - Pushed to origin: Yes
   - Branch merged to main: No (not in `git branch --merged main`)
   - **Recommendation:** 🤔 INVESTIGATE - Work may be complete, branch not merged yet

4. **worktree-2026-01-07T08-14-04**
   - Branch: `worktree-2026-01-07T08-14-04`
   - Status: 1 staged file (`docs/research/verification-audit-trail 2.md`)
   - Last commit: "docs: TASK-252 complete - Interactive Testing UI" (bcb6d3f)
   - Pushed to origin: Yes
   - Branch merged to main: No
   - **Recommendation:** 🤔 INVESTIGATE - Has uncommitted staged file, needs review

**Detailed Investigation Commands:**

```bash
# Check if branches are merged
git branch --merged main | grep worktree-2026-01-07

# Check commit differences
git log main..worktree-2026-01-07T07-28-08 --oneline
git log main..worktree-2026-01-07T08-14-04 --oneline

# Check for uncommitted work
cd .worktrees/worktree-2026-01-07T07-28-08 && git status
cd .worktrees/worktree-2026-01-07T08-14-04 && git status

# If safe to remove:
git worktree remove .worktrees/worktree-2026-01-07T07-28-08
git worktree remove .worktrees/worktree-2026-01-07T08-14-04

# Prune deleted worktrees
git worktree prune
```

**Recommendations Summary:**

| Worktree | Branch | Status | Action |
|----------|--------|--------|--------|
| worktree-2026-01-07T07-28-08 | worktree-2026-01-07T07-28-08 | Clean, not merged | Investigate - may need merge or is obsolete |
| worktree-2026-01-07T08-14-04 | worktree-2026-01-07T08-14-04 | Staged file | Investigate - commit or discard staged file |
| worktree-2026-01-07T14-18-11 | feature/RESEARCH-001-blog-strategy | Modified file | ✅ Keep - active work |
| worktree-2026-01-07T14-39-08 | worktree-2026-01-07T14-39-08 | Clean, same as main | ✅ Keep - recent |

**Acceptance Criteria:**
- [ ] All 4 worktrees investigated
- [ ] Stale worktrees removed (if obsolete) or merged (if ready)
- [ ] Decision documented for each worktree
- [ ] `git worktree list` shows only active worktrees

---

### ISSUE-007: README File Proliferation (28 files)

**Impact:** Maintenance burden, some may be redundant
**Effort:** 2-3 hours (audit each README)
**Risk Level:** 🟡 MEDIUM

**README Files Found (28 total):**

**✅ Legitimate Index READMEs (Keep):**
```
./README.md (root - main project README)
./Python/README.md (Python package README)
./Excel/README.md (Excel integration README)
./docs/README.md (documentation index)
./docs/research/README.md (research index)
./docs/adr/README.md (ADR index)
./docs/contributing/README.md (contributing guide index)
./docs/cookbook/README.md (cookbook index)
./docs/architecture/README.md (architecture docs index)
./docs/getting-started/README.md (getting started index)
./docs/reference/README.md (reference docs index)
./docs/planning/README.md (planning docs index)
./agents/README.md (agent guide index)
./logs/README.md (logs directory purpose)
```

**🤔 Investigate (May be redundant):**
```
./.pytest_cache/README.md (pytest auto-generated - ignore)
./Python/.pytest_cache/README.md (pytest auto-generated - ignore)
./Python/tests/README.md (test documentation)
./Excel/snapshots/README.md (snapshots purpose)
./Excel/Templates/README.md (templates guide)
./docs/research/in-progress/cost-optimization/README.md (work-in-progress)
./docs/_internal/copilot-tasks/README.md (historical tasks)
./docs/images/README.md (image attribution)
./docs/learning/README.md (learning resources)
./docs/publications/README.md (publications list)
./docs/_references/README.md (references index)
./docs/planning/research-visual-design/README.md (research sub-project)
./docs/planning/research-findings-validation/README.md (research sub-project)
./docs/planning/research-platform/README.md (research sub-project)
./docs/verification/README.md (verification docs)
```

**Audit Process:**

For each README in "Investigate" category:
1. Check file size: `wc -l <file>`
2. Check content: Is it an index/TOC or duplicated info?
3. Check references: `rg -l "path/to/README.md"`
4. Decision:
   - **Keep:** If unique content or serves as directory index
   - **Consolidate:** If duplicates parent README
   - **Remove:** If empty or just says "TODO"

**Recommendations:**

```bash
# Audit each README
for readme in $(find docs/ -name "README.md" -type f); do
  echo "=== $readme ==="
  wc -l "$readme"
  head -5 "$readme"
  echo ""
done

# Remove pytest auto-generated READMEs (safe - regenerated)
# Don't track these - they're cache files
git rm --cached .pytest_cache/README.md Python/.pytest_cache/README.md 2>/dev/null

# Add to .gitignore
grep -q "\.pytest_cache" .gitignore || echo ".pytest_cache/" >> .gitignore
```

**Acceptance Criteria:**
- [ ] All 28 READMEs audited
- [ ] Redundant READMEs consolidated or removed
- [ ] pytest cache READMEs ignored
- [ ] Decision documented for each README

---

## P2 (Medium) - Nice to Have

### ISSUE-008: Repository Size Monitoring

**Impact:** Track repository growth over time
**Effort:** 30 minutes
**Risk Level:** 🟢 LOW

**Current Metrics:**
- .git/ size: **20M**
- Total repo size: ~30M (estimated with working tree)
- Large files (>1MB): 3 (all mypy cache - safe, not tracked)

**Recommendations:**

```bash
# Create repository health tracking script
cat > scripts/repo_health_check.sh << 'EOF'
#!/bin/bash
# Repository Health Check Script

echo "=== Repository Health Report ==="
echo "Date: $(date)"
echo ""

echo "Repository Size:"
du -sh .git/ | awk '{print "  .git/: " $1}'
du -sh . | awk '{print "  Total: " $1}'
echo ""

echo "Large Files (>1MB, excluding .venv and .git):"
find . -type f -size +1M -not -path "./.venv/*" -not -path "./.git/*" | xargs du -h | sort -rh
echo ""

echo "File Counts:"
echo "  Markdown: $(find . -name "*.md" -not -path "./.venv/*" | wc -l)"
echo "  Python: $(find . -name "*.py" -not -path "./.venv/*" | wc -l)"
echo "  Total files: $(git ls-files | wc -l)"
echo ""

echo "Git Objects:"
git count-objects -vH
EOF

chmod +x scripts/repo_health_check.sh

# Run monthly and track trends
./scripts/repo_health_check.sh > logs/repo-health-2026-01-07.txt
```

**Acceptance Criteria:**
- [ ] Health check script created
- [ ] Baseline report generated
- [ ] Added to monthly maintenance checklist

---

### ISSUE-009: Documentation Structure Review

**Impact:** Reduce docs/ root clutter
**Effort:** 3-4 hours
**Risk Level:** 🟢 LOW

**Current docs/ structure:**
```
docs/
├── [30+ root-level .md files] ← CLUTTERED
├── _internal/
├── _references/
├── adr/
├── architecture/
├── contributing/
├── cookbook/
├── getting-started/
├── guidelines/
├── images/
├── learning/
├── planning/
├── publications/
├── reference/
├── research/
└── verification/
```

**Recommendations:**

Proposed reorganization:
```
docs/
├── README.md (main index)
├── guides/
│   ├── MISSION_AND_PRINCIPLES.md
│   ├── TESTING_STRATEGY.md
│   └── ... (move root guides here)
├── overview/
│   ├── DEEP_PROJECT_MAP.md
│   ├── project-overview.md
│   └── ... (move overview docs here)
├── releases/
│   ├── RELEASES.md
│   ├── CHANGELOG.md
│   └── v*.md files
└── [existing subdirectories...]
```

**Process:**
1. Audit all root-level docs/ files
2. Categorize by purpose
3. Create target directories
4. Move files with `git mv`
5. Update all links
6. Test with `scripts/check_links.py`

**Acceptance Criteria:**
- [ ] docs/ root has <15 files
- [ ] Clear subdirectory structure
- [ ] All links updated
- [ ] README.md updated with new structure

---

### ISSUE-010: Obsolete Planning Docs Archive

**Impact:** Reduce active docs/ clutter
**Effort:** 2-3 hours
**Risk Level:** 🟢 LOW

**Candidates for Archive (from docs/planning/):**

```
docs/planning/v0.12-plan.md → docs/_archive/planning/v0.12-plan.md
docs/planning/production-roadmap.md → docs/_archive/planning/production-roadmap-v0.10.md
docs/planning/project-status.md → docs/_archive/planning/project-status-v0.11.md
docs/planning/task-210-211-*.md (4 files) → docs/_archive/planning/
```

**Additional Archive Candidates:**
```
docs/v0.7_REQUIREMENTS.md
docs/v0.8_EXECUTION_CHECKLIST.md
docs/v0.9_TASKS.md (if exists)
docs/planning/v0.16-task-specs.md (if complete)
docs/planning/v0.17-task-specs.md (if complete)
```

**Archive Process (with redirects):**

```bash
# Create archive directory structure
mkdir -p docs/_archive/planning

# Move file
git mv docs/planning/v0.12-plan.md docs/_archive/planning/v0.12-plan.md

# Create redirect stub
cat > docs/planning/v0.12-plan.md << 'EOF'
# v0.12 Plan

> **Note:** This document has been archived as it pertains to v0.12 development (completed).

**Archived location:** [docs/_archive/planning/v0.12-plan.md](../_archive/planning/v0.12-plan.md)

---

For current planning, see:
- [TASKS.md](../TASKS.md)
- [Next Session Brief](next-session-brief.md)
- [Current Project Status](memory.md)
EOF

# Update links (if any)
rg -l "planning/v0.12-plan.md" | xargs sed -i 's|planning/v0.12-plan.md|planning/../_archive/planning/v0.12-plan.md|g'

# Verify
./scripts/check_links.py
```

**Acceptance Criteria:**
- [ ] Obsolete docs moved to _archive/
- [ ] Redirect stubs created
- [ ] Links updated
- [ ] Archive README.md explains purpose

---

### ISSUE-011: Dependency Audit

**Impact:** Remove unused dependencies
**Effort:** 1-2 hours
**Risk Level:** 🟢 LOW

**Process:**

```bash
# Check installed packages
cd Python && ../.venv/bin/pip list

# Check pyproject.toml dependencies
cat pyproject.toml | grep -A 50 "dependencies"

# Check actual imports in code
rg "^import |^from " Python/structural_lib/ | awk '{print $2}' | sort -u

# Find unused dependencies
# (requires manual comparison)
```

**Common Unused Dependency Patterns:**
- Development dependencies listed in `dependencies` instead of `dev-dependencies`
- Transitive dependencies explicitly listed (unnecessary)
- Legacy dependencies from refactored code

**Acceptance Criteria:**
- [ ] All dependencies audited
- [ ] Unused dependencies identified
- [ ] Removal recommendations documented
- [ ] Decision from MAIN on each

---

### ISSUE-012: .gitignore Completeness Review

**Impact:** Prevent accidental commits of generated files
**Effort:** 30 minutes
**Risk Level:** 🟢 LOW

**Current .gitignore Status:**
- ✅ `.venv/` - Good
- ⚠️ `.coverage` - Should be `/.coverage` (root only)
- ⚠️ `.mypy_cache/` - Should add if not present
- ⚠️ `.pytest_cache/` - Should add if not present
- ⚠️ `.DS_Store` - Should add (macOS)

**Recommended Additions:**

```bash
# Append to .gitignore
cat >> .gitignore << 'EOF'

# OS metadata
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes

# Python cache and build
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing and coverage
/.coverage
.coverage.*
.pytest_cache/
.mypy_cache/
.tox/
htmlcov/
.hypothesis/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Documentation builds
docs/_build/
site/

# Temporary files
*.tmp
*.bak
*.old
EOF

# Verify
cat .gitignore
```

**Acceptance Criteria:**
- [ ] .gitignore covers all common generated files
- [ ] No tracked files match new .gitignore patterns
- [ ] Tested: Create test file, verify ignored

---

### ISSUE-013: Naming Convention Documentation

**Impact:** Establish clear standards for future contributions
**Effort:** 1 hour
**Risk Level:** 🟢 LOW

**Create:** `docs/contributing/naming-conventions.md`

**Content Outline:**
```markdown
# Naming Conventions

## File Naming

### Documentation Files
- **Standard:** kebab-case (e.g., `api-design-guide.md`)
- **Exceptions:**
  - `README.md` (high visibility)
  - `TASKS.md`, `SESSION_LOG.md` (important planning docs)
  - `LICENSE`, `CHANGELOG.md` (standard practice)

### Python Files
- **Modules:** snake_case (e.g., `compliance.py`)
- **Classes:** PascalCase (e.g., `BeamDesign`)
- **Functions:** snake_case (e.g., `calculate_moment_capacity`)

### Directory Names
- **All lowercase:** kebab-case preferred
- **Examples:** `getting-started/`, `api-reference/`

## Branch Naming

### Feature Branches
- `feature/TASK-XXX-description`
- `hygiene/cleanup-topic`
- `audit/hygiene-YYYY-MM-DD`

### Release Branches
- `release/v0.X.Y`
```

**Acceptance Criteria:**
- [ ] Naming conventions documented
- [ ] Linked from CONTRIBUTING.md
- [ ] Examples provided for each category

---

## Summary of Recommendations

### Immediate Actions (P0) - 3-4 hours total

1. **Fix broken links** (2-3h)
   - Fix 5 critical broken links
   - Update or remove 12 placeholder links

2. **Remove build artifacts** (15min)
   - Remove `.coverage` from git root
   - Update .gitignore

3. **Add mypy cache to .gitignore** (10min)

### Sprint Actions (P1) - 8-12 hours total

4. **Standardize file naming** (4-6h)
   - Phase 1: Root docs/ files
   - Phase 2: _internal/ files
   - Phase 3: copilot-tasks/ files

5. **Consolidate LICENSE/SUPPORT** (30min)

6. **Investigate worktrees** (1h)
   - Review 2 potentially stale worktrees
   - Remove if obsolete

7. **Audit README files** (2-3h)
   - Review 28 READMEs
   - Consolidate or remove redundant

### Nice-to-Have (P2) - 8-10 hours total

8. **Repository health monitoring** (30min)
9. **Documentation structure review** (3-4h)
10. **Archive obsolete plans** (2-3h)
11. **Dependency audit** (1-2h)
12. **.gitignore review** (30min)
13. **Naming conventions doc** (1h)

---

## Verification Commands

After implementing any recommendations:

```bash
# Check broken links
./scripts/check_links.py

# Check git artifacts
git ls-files | grep -E '\.DS_Store|\.coverage|\.pyc|__pycache__'

# Check repository size
du -sh .git/

# Check worktrees
git worktree list

# Check untracked files
git status --short

# Verify .gitignore
git check-ignore -v <file>
```

---

## Action Required from MAIN Agent

1. **Review this audit report**
   - Branch: `audit/hygiene-2026-01-07`
   - File: `docs/planning/hygiene-suggestions-2026-01-07.md`

2. **Prioritize recommendations**
   - Which P0 issues to fix first?
   - Which P1 issues for this sprint?
   - Which P2 issues to defer?

3. **Decision points:**
   - Keep or remove `Python/LICENSE`? (PyPI distribution)
   - Archive worktrees or keep for reference?
   - README consolidation strategy?

4. **Next steps:**
   - **Option A:** Assign back to Agent 2 (Mode 2) for implementation
   - **Option B:** Implement yourself
   - **Option C:** Defer to backlog

---

**Report Complete**
**Agent 2 Status:** Awaiting MAIN approval for implementation
**Branch:** audit/hygiene-2026-01-07 (local only, not pushed)
