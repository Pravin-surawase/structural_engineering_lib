# Governance Automation Catalog

**Date:** 2026-01-10
**Owner:** Agent 9 (Governance)
**Purpose:** Single source of truth for all automated governance checks

---

## Quick Reference

| Check | Trigger | Command | Blocks Commit? |
|-------|---------|---------|----------------|
| Link Validation | Pre-commit, CI | `python scripts/check_links.py` | Yes |
| Folder Structure | Pre-commit | `python scripts/validate_folder_structure.py` | No (warnings only) |
| Doc Version Drift | Pre-commit, CI | `python scripts/check_doc_versions.py` | Yes |
| TASKS.md Format | Pre-commit | `python scripts/check_tasks_format.py` | Yes |
| Docs Index | Pre-commit, CI | `python scripts/check_docs_index.py` | Yes |
| Session Docs | Pre-commit | `python scripts/check_session_docs.py` | Yes |
| API Docs Sync | Pre-commit | `python scripts/check_api_docs_sync.py` | Yes |
| Large Files | Pre-commit | `check-added-large-files` | Yes |
| Trailing Whitespace | Pre-commit | `trailing-whitespace` | Auto-fix |
| Black Formatting | Pre-commit | `black` | Auto-fix |
| **Weekly Governance** | **Manual/Weekly** | `./scripts/weekly_governance_check.sh` | **No (reporting)** |

---

## Weekly Governance Check (NEW)

**File:** `scripts/weekly_governance_check.sh`
**Purpose:** Consolidated health check for governance compliance

**What it checks:**
1. Folder structure validation (all rules)
2. Internal link validation (all docs)
3. Root file count (≤10)
4. docs/ root file count (≤5)
5. Agent entry points (3/3)

**Usage:**
```bash
./scripts/weekly_governance_check.sh           # Full check
./scripts/weekly_governance_check.sh --quick   # Skip slow checks
./scripts/weekly_governance_check.sh --fix     # Auto-fix where possible
```

**When to run:**
- Weekly maintenance check
- Before major releases
- After large documentation changes

---

## Pre-Commit Hooks (Automatic)

### 1. Markdown Link Validation

**File:** `scripts/check_links.py`
**Hook ID:** `check-markdown-links`
**Triggers:** Any `.md` file in `docs/`

**What it checks:**
- All internal markdown links `[text](path.md)`
- Relative paths resolve correctly
- Target files exist

**Skip Patterns:**
- `SKIP_DIRECTORIES`: agents/agent-9, docs/_archive, docs/research
- `SKIP_LINK_PATTERNS`: Placeholder patterns like "TBD", "TODO", example paths

**Fix procedure:**
```bash
# Check all links
python scripts/check_links.py

# If broken links found:
# 1. Use sed for bulk fixes
sed -i '' 's|old-path.md|new-path.md|g' affected-files.md

# 2. Or manually edit files
```

**Workflow:** [LINK_GOVERNANCE.md](workflows/LINK_GOVERNANCE.md)

---

### 2. Folder Structure Validation

**File:** `scripts/validate_folder_structure.py`
**Triggers:** Manual or CI

**What it checks:**
- Root file count (target: ≤10)
- docs/ root file count (target: ≤5)
- Kebab-case naming convention
- Required folders exist

**Smart Allowlists:**
- Underscore-prefixed folders (_internal, _references) - intentional
- Data/research folders - may have specialized naming
- Internal/archive files - may use legacy naming

**Fix procedure:**
```bash
# Check structure
python scripts/validate_folder_structure.py

# If errors found:
# 1. Move files to appropriate folders
git mv docs/file.md docs/appropriate-folder/file.md

# 2. Rename to kebab-case
git mv "FILE.md" "file.md"
```

---

### 3. Doc Version Drift

**File:** `scripts/check_doc_versions.py`
**Hook ID:** `check-doc-versions`
**Triggers:** Any commit

**What it checks:**
- Version numbers in docs match pyproject.toml
- Prevents stale version references

**Skip patterns:**
- Research docs (external tool versions)
- Archive docs (historical content)

---

### 4. TASKS.md Format

**File:** `scripts/check_tasks_format.py`
**Hook ID:** `check-tasks-format`

**What it checks:**
- Task ID format
- Status consistency
- Required sections present

---

### 5. Docs Index Structure

**File:** `scripts/check_docs_index.py`
**Hook ID:** `check-docs-index`

**What it checks:**
- docs/README.md structure
- Required sections present
- Link format consistency

---

### 6. Large Files

**Hook:** `check-added-large-files`
**Threshold:** 500 KB

**What it checks:**
- Files being added exceed size limit

**Fix procedure:**
```bash
# If large file detected:
# 1. Add to .gitignore
echo "path/to/large-file" >> .gitignore

# 2. Unstage the file
git reset HEAD path/to/large-file

# 3. Retry commit
```

---

## CI Checks (Safety Net)

### fast-checks.yml

**Location:** `.github/workflows/fast-checks.yml`

**Doc Checks (Parallel):**
```yaml
python scripts/check_docs_index_links.py &
python scripts/check_links.py &
python scripts/check_doc_versions.py &
wait
```

**Purpose:** Catch issues that slip past pre-commit

---

## Agent 8 Git Workflow

### safe_push.sh

**Location:** `scripts/safe_push.sh`
**Purpose:** Conflict-free commits

**Features:**
- Stashes changes before sync
- Handles pre-commit modifications
- Pulls before committing (prevents conflicts)
- Auto-resolves merge conflicts
- Never rewrites pushed history

**Usage:**
```bash
./scripts/safe_push.sh "commit message"
```

### ai_commit.sh

**Location:** `scripts/ai_commit.sh`
**Purpose:** Decision logic + safe_push

**Features:**
- Analyzes changes to suggest PR vs direct commit
- Delegates to safe_push.sh for execution

**Usage:**
```bash
./scripts/ai_commit.sh "commit message"
```

---

## Adding New Automation

### Step 1: Create the Check Script

```python
#!/usr/bin/env python3
"""Check description.

Usage: python scripts/check_something.py [options]
"""

def main():
    # Check logic
    errors = []

    # ... validation ...

    if errors:
        print(f"❌ {len(errors)} error(s) found")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("✅ All checks passed!")
    return 0

if __name__ == "__main__":
    exit(main())
```

### Step 2: Add Pre-Commit Hook

```yaml
# In .pre-commit-config.yaml
- id: check-something
  name: Check something description
  entry: python3 scripts/check_something.py
  language: system
  files: ^pattern/.*\.ext$  # Optional file filter
  pass_filenames: false
```

### Step 3: Add CI Check (Optional)

```yaml
# In .github/workflows/fast-checks.yml
- name: Check something
  run: python scripts/check_something.py
```

### Step 4: Document in This Catalog

Add entry to the Quick Reference table and create detailed section.

---

## Troubleshooting

### Pre-commit Hook Fails

```bash
# See which hook failed
# Look for "Failed" in output

# Run hook manually
python scripts/check_<name>.py

# Fix issues, then retry
git add -A && git commit -m "message"
```

### CI Check Fails but Pre-commit Passed

```bash
# CI may check more files than pre-commit
# Run full check locally
python scripts/check_<name>.py --all

# Or check specific files
python scripts/check_<name>.py path/to/file.md
```

### Adding Skip Patterns

```python
# In the check script, add to SKIP list:
SKIP_DIRECTORIES = [
    "existing/dir",
    "new/dir/to/skip",  # Add here
]

SKIP_PATTERNS = [
    r"existing.*pattern",
    r"new.*pattern",  # Add here
]
```

---

## Maintenance Schedule

### Weekly
- Review any new false positives
- Update skip patterns as needed

### Monthly
- Run deep validation: `python scripts/check_links.py --all`
- Review automation effectiveness
- Update this catalog with new checks

### Per Release
- Run full validation suite
- Ensure all docs are up-to-date
- Archive outdated governance docs
