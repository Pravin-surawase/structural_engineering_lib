# Phase 7: Script and Automation Updates

**Duration:** 3-4 hours
**Complexity:** Medium
**Risk:** Low (changes isolated to scripts/)
**Validation Impact:** No error reduction (scripts don't affect folder validation)

---

## Overview

Update hardcoded file paths in scripts, CI/CD workflows, and automation tools to reflect new folder structure.

**What needs updating:**
- Python scripts in `scripts/`
- Shell scripts (if any)
- GitHub Actions workflows (`.github/workflows/`)
- Pre-commit hooks (`.pre-commit-config.yaml`)
- Documentation generation scripts
- Any automation referencing old paths

**Types of updates:**
1. **Path constants:** `DOCS_PATH = "docs/planning/"` → `"docs/architecture/"`
2. **File references:** `"agents/AGENT-9-GOVERNANCE.md"` → `"agents/roles/agent-9-governance.md"`
3. **Glob patterns:** `"docs/*.md"` → `"docs/**/*.md"` (if now in subdirectories)
4. **Import paths:** (if code organization changed)

---

## Prerequisites

- ✅ Phase 0 complete (backup created)
- ✅ Phases 2-5 complete (files moved and renamed)
- ✅ Phase 6 complete (links fixed) - recommended
- ✅ Working tree is clean
- ✅ Migration branch active

---

## Step-by-Step Execution

### Step 1: Inventory Scripts

```bash
# List all scripts
find scripts/ -type f -name "*.py" -o -name "*.sh"

# List CI/CD workflows
ls -la .github/workflows/

# List pre-commit hooks
cat .pre-commit-config.yaml | grep -E "(repo:|id:)"

# Count total scripts
echo "Python scripts: $(find scripts/ -name '*.py' | wc -l)"
echo "Shell scripts: $(find scripts/ -name '*.sh' | wc -l)"
echo "GitHub workflows: $(ls -1 .github/workflows/*.yml 2>/dev/null | wc -l)"
```

**Expected output:**
```
scripts/validate_folder_structure.py
scripts/archive_old_docs.py
scripts/check_links.py
scripts/generate_health_report.py
scripts/check_wip_limits.py
scripts/check_version_consistency.py

Python scripts: 6
Shell scripts: 2
GitHub workflows: 3
```

**Checkpoint 1:** ✅ Scripts inventoried

---

### Step 2: Search for Hardcoded Paths

```bash
# Find hardcoded paths to moved files
grep -r "agents/AGENT-" scripts/ .github/ --include="*.py" --include="*.sh" --include="*.yml"

# Find old docs/ paths
grep -r "docs/planning\|docs/design\|docs/architecture" scripts/ .github/ --include="*.py" --include="*.sh"

# Find dated file references
grep -r "session-202[0-9]" scripts/ .github/ --include="*.py"

# Find naming violations in scripts
grep -r "Old_File\|Task_Specs\|UPPERCASE" scripts/ --include="*.py"

# Save findings
grep -rn "agents/AGENT\|docs/planning\|docs/design" scripts/ .github/ --include="*.py" --include="*.yml" > /tmp/hardcoded-paths.txt
```

**Expected findings:**
```
scripts/validate_folder_structure.py:156: if str(rel_path).startswith("docs/planning/"):
scripts/archive_old_docs.py:42: ACTIVE_DIR = "docs/planning/"
scripts/generate_health_report.py:78: agent_files = Path("agents").glob("AGENT-*.md")
.github/workflows/validate.yml:23: - name: Check docs/planning/
```

**Checkpoint 2:** ✅ Hardcoded paths identified

---

### Step 3: Update `validate_folder_structure.py`

**Review current script:**

```bash
# Check current governance rules in validator
grep -A 10 "RULES = " scripts/validate_folder_structure.py
```

**Update paths (if needed):**

The validator uses dynamic patterns, but check for:
- **Fixed paths:** Any hardcoded directory checks
- **Allowed files lists:** May reference old filenames
- **Special folder checks:** Update if folder structure changed

**Example updates:**

```python
# OLD (if exists)
if str(rel_path).startswith("docs/planning/"):
    # Special handling for planning docs

# NEW
if str(rel_path).startswith("docs/getting-started/") or \
   str(rel_path).startswith("docs/architecture/"):
    # Special handling
```

**No major changes expected** - validator already uses governance rules which are up-to-date.

**Checkpoint 3:** ✅ Validator updated (likely no changes needed)

---

### Step 4: Update `archive_old_docs.py`

**Current script paths:**

```bash
# Check current paths in archive script
grep -n "ACTIVE_DIR\|ARCHIVE_DIR\|docs/" scripts/archive_old_docs.py
```

**Expected paths:**

```python
# Should already be correct from Phase 0/1 setup
ACTIVE_DIR = "docs/_active/"
ARCHIVE_DIR = "docs/_archive/"

# If script has hardcoded planning/ references, update
# OLD:
# scan_dirs = ["docs/planning/", "docs/design/"]

# NEW:
scan_dirs = [
    "docs/getting-started/",
    "docs/reference/",
    "docs/architecture/",
    "docs/contributing/",
]
```

**Test after update:**

```bash
# Dry-run to verify no errors
python scripts/archive_old_docs.py --dry-run
```

**Checkpoint 4:** ✅ Archive script updated

---

### Step 5: Update `generate_health_report.py`

**Update agent file references:**

```python
# OLD (if script exists):
agent_files = Path("agents").glob("AGENT-*.md")

# NEW:
agent_files = Path("agents/roles").glob("agent-*.md")

# Or more robust:
agent_files = list(Path("agents/roles").glob("agent-*.md"))
if not agent_files:
    # Fallback for old structure
    agent_files = list(Path("agents").glob("AGENT-*.md"))
```

**Update docs/ scanning:**

```python
# OLD (if script scans specific paths):
docs_files = list(Path("docs/planning").glob("*.md"))

# NEW (scan all category folders):
docs_files = []
for category in ["getting-started", "reference", "architecture", "contributing", "governance", "agents"]:
    category_path = Path(f"docs/{category}")
    if category_path.exists():
        docs_files.extend(category_path.rglob("*.md"))
```

**Test after update:**

```bash
# Run script to verify no errors
python scripts/generate_health_report.py --output /tmp/health-report.md

# Check output
cat /tmp/health-report.md
```

**Checkpoint 5:** ✅ Health report script updated

---

### Step 6: Update `check_links.py`

**Minimal changes expected** (already handles dynamic paths).

**Verify:**

```bash
# Test link checker still works
python scripts/check_links.py docs/ agents/

# Should find few broken links after Phase 6
```

**Update ignore patterns (if needed):**

```python
# Add new paths to ignore
IGNORE_PATTERNS = [
    "docs/_archive/**/*.md",  # Archived docs may have broken links
    "docs/_active/**/*.md",   # Active docs in progress
]
```

**Checkpoint 6:** ✅ Link checker updated

---

### Step 7: Update GitHub Actions Workflows

**Check workflows:**

```bash
ls -la .github/workflows/
```

**Common workflow files:**
- `validate.yml` - run folder structure validation
- `tests.yml` - run test suite
- `docs.yml` - build documentation

**Update paths in workflows:**

```yaml
# .github/workflows/validate.yml

# OLD:
- name: Check folder structure
  run: |
    python scripts/validate_folder_structure.py
    grep -r "agents/AGENT-" docs/ && exit 1 || true

# NEW:
- name: Check folder structure
  run: |
    python scripts/validate_folder_structure.py
    # Agents files should now be in agents/roles/
    test $(ls -1 agents/*.md 2>/dev/null | wc -l) -eq 1  # Only README.md
```

**Update documentation build paths:**

```yaml
# .github/workflows/docs.yml

# OLD:
- name: Build docs
  run: |
    mkdocs build --strict
    # Or other doc builder

# NEW: (likely no changes, but verify paths)
- name: Build docs
  run: |
    mkdocs build --strict
```

**Test workflows locally (if possible):**

```bash
# Install act (GitHub Actions local runner)
# brew install act

# Run workflow locally
act -j validate
```

**Checkpoint 7:** ✅ GitHub workflows updated

---

### Step 8: Update Pre-Commit Hooks

**Check `.pre-commit-config.yaml`:**

```bash
cat .pre-commit-config.yaml
```

**Update paths in hooks (if needed):**

```yaml
# OLD (example):
- id: check-docs
  name: Check docs folder
  entry: bash -c 'test $(ls -1 docs/*.md | wc -l) -le 5'

# NEW:
- id: check-docs
  name: Check docs root folder
  entry: bash -c 'test $(ls -1 docs/*.md 2>/dev/null | wc -l) -le 5'

# Or reference validator instead
- id: validate-structure
  name: Validate folder structure
  entry: python scripts/validate_folder_structure.py
  language: system
  pass_filenames: false
```

**Test pre-commit hooks:**

```bash
# Run all hooks
pre-commit run --all-files

# Should pass with no errors
```

**Checkpoint 8:** ✅ Pre-commit hooks updated

---

### Step 9: Update Documentation Scripts (If Any)

**Check for doc generation scripts:**

```bash
# Find scripts that generate or process docs
grep -l "docs/" scripts/*.py scripts/*.sh

# Common patterns:
# - generate_index.py
# - build_toc.py
# - sync_readmes.py
```

**Update doc generation paths:**

```python
# Example: TOC generator

# OLD:
toc_files = [
    "docs/README.md",
    "docs/TASKS.md",
    "docs/planning/overview.md",
]

# NEW:
toc_files = [
    "docs/README.md",
    "docs/TASKS.md",
    "docs/getting-started/overview.md",
    "docs/architecture/overview.md",
]

# Or dynamic discovery:
toc_files = list(Path("docs").rglob("README.md"))
```

**Checkpoint 9:** ✅ Doc generation scripts updated

---

### Step 10: Test All Scripts

```bash
# Test each script individually
echo "Testing validate_folder_structure.py..."
python scripts/validate_folder_structure.py
echo "✅ Passed"

echo "Testing archive_old_docs.py..."
python scripts/archive_old_docs.py --dry-run
echo "✅ Passed"

echo "Testing check_links.py..."
python scripts/check_links.py docs/ agents/
echo "✅ Passed"

echo "Testing generate_health_report.py..."
python scripts/generate_health_report.py --output /tmp/report.md
echo "✅ Passed"

# Test pre-commit
echo "Testing pre-commit hooks..."
pre-commit run --all-files
echo "✅ Passed"

# Summarize
echo ""
echo "All scripts tested successfully!"
```

**Checkpoint 10:** ✅ All scripts tested

---

### Step 11: Commit Script Updates

```bash
# Stage all script changes
git add scripts/ .github/ .pre-commit-config.yaml

# Verify changes
git diff --cached

# Create commit
git commit -m "$(cat <<'EOF'
fix(migration): Phase 7 - Update script paths after folder migration

Updated hardcoded paths in:
- scripts/archive_old_docs.py: scan dirs updated
- scripts/generate_health_report.py: agent files path updated
- scripts/check_links.py: ignore patterns updated
- .github/workflows/validate.yml: path checks updated
- .pre-commit-config.yaml: folder validation updated

All scripts tested and passing:
✅ validate_folder_structure.py
✅ archive_old_docs.py
✅ check_links.py
✅ generate_health_report.py
✅ pre-commit hooks

Phase 7 of 8 complete.
Ref: agents/agent-9/governance/FULL-MIGRATION-EXECUTION-PLAN.md

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"

# Push
git push origin migration/folder-structure-cleanup
```

**Checkpoint 11:** ✅ Changes committed and pushed

---

## Validation Checklist

After completing all steps, verify:

- [ ] All scripts run without errors
- [ ] `python scripts/validate_folder_structure.py` passes
- [ ] `python scripts/archive_old_docs.py --dry-run` works
- [ ] `python scripts/check_links.py docs/ agents/` works
- [ ] `python scripts/generate_health_report.py` produces report
- [ ] `pre-commit run --all-files` passes
- [ ] GitHub Actions workflows pass (if testable locally)
- [ ] No hardcoded old paths remain in `grep -r "agents/AGENT" scripts/`
- [ ] No hardcoded old paths remain in `grep -r "docs/planning" scripts/` (unless intentional)
- [ ] Changes committed and pushed

---

## Common Issues

### Issue 1: Script imports fail after update

**Cause:** Import paths not updated

**Solution:**
```python
# Update relative imports
# OLD:
from validate import check_structure

# NEW:
from scripts.validate_folder_structure import FolderValidator
```

### Issue 2: GitHub Actions fail after push

**Cause:** Workflow paths not updated

**Solution:**
```bash
# Check workflow logs on GitHub
# Update paths in .github/workflows/*.yml
# Push fix
```

### Issue 3: Pre-commit hook blocks commit

**Cause:** Hook still checks old structure

**Solution:**
```bash
# Update hook in .pre-commit-config.yaml
# Or skip hook temporarily
SKIP=check-docs git commit -m "..."
```

### Issue 4: Script can't find files after migration

**Cause:** Hardcoded path not updated

**Solution:**
```python
# Use dynamic path discovery instead
files = list(Path("docs").rglob("*.md"))
# Instead of:
# files = Path("docs/planning").glob("*.md")
```

---

## Rollback Procedure

**If Phase 7 breaks scripts:**

```bash
# Undo last commit
git reset --hard HEAD~1

# Or restore specific script
git checkout HEAD~1 -- scripts/generate_health_report.py

# Re-run update with fixes
```

**See:** [ROLLBACK-PROCEDURES.md](ROLLBACK-PROCEDURES.md)

---

## Time Estimates

- **Step 1 (Inventory):** 15 minutes
- **Step 2 (Search paths):** 20 minutes
- **Step 3 (Update validator):** 15 minutes
- **Step 4 (Update archive script):** 20 minutes
- **Step 5 (Update health report):** 30 minutes
- **Step 6 (Update link checker):** 15 minutes
- **Step 7 (Update workflows):** 30 minutes
- **Step 8 (Update pre-commit):** 20 minutes
- **Step 9 (Update doc scripts):** 30 minutes
- **Step 10 (Test all):** 30 minutes
- **Step 11 (Commit):** 10 minutes

**Total:** 3-4 hours

---

## Next Steps

After Phase 7 completion:

1. **Update MIGRATION-STATUS.md** to mark Phase 7 complete
2. **Proceed to Phase 8** (final validation) - last phase!
3. **Or proceed to Phase 3** if skipped earlier (docs/ categorization)

---

## Success Criteria

Phase 7 is complete when:

1. ✅ All scripts run without errors
2. ✅ No hardcoded old paths in scripts/
3. ✅ GitHub Actions workflows pass
4. ✅ Pre-commit hooks work correctly
5. ✅ Validator, archive, link checker, health report all tested
6. ✅ Changes committed and pushed

---

**Phase 7 Status:** 📋 Ready for execution
**Last Updated:** 2026-01-10
**Next Phase:** [PHASE-8-FINAL-VALIDATION.md](PHASE-8-FINAL-VALIDATION.md)
