# Agent 9: Automation Scripts Specifications

**Purpose:** Complete specifications for all governance automation scripts
**Audience:** Developers implementing or maintaining governance scripts
**Last Updated:** 2026-01-10

---

## Table of Contents

1. [Archive Old Sessions Script](#script-1-archive_old_sessionssh)
2. [Check WIP Limits Script](#script-2-check_wip_limitssh)
3. [Check Version Consistency Script](#script-3-check_version_consistencysh)
4. [Generate Health Report Script](#script-4-generate_health_reportsh)
5. [Monthly Maintenance Script](#script-5-monthly_maintenancesh)
6. [Script Maintenance Guidelines](#script-maintenance-guidelines)

---

## Script 1: archive_old_sessions.sh

### Purpose
Move session documentation older than 7 days from `docs/planning/` to `docs/archive/YYYY-MM/` with proper organization and indexing.

### Location
`scripts/archive_old_sessions.sh`

### Usage
```bash
# Dry run (show what would be archived)
./scripts/archive_old_sessions.sh --dry-run

# Execute archival
./scripts/archive_old_sessions.sh

# Force archive specific files (ignore age check)
./scripts/archive_old_sessions.sh --force FILE1.md FILE2.md

# Verbose mode (detailed logging)
./scripts/archive_old_sessions.sh --verbose
```

### Features

#### 1. Age Detection
- Identify files in `docs/planning/` older than 7 days
- Use file modification time (`mtime`)
- Exclude files matching patterns in `.archiveignore` (if exists)

#### 2. Categorization
Automatically categorize files by agent:
- `AGENT-6-*` → `agent-6/`
- `AGENT-8-*` → `agent-8/`
- `RESEARCH-*` → `research/`
- `*-HANDOFF-*`, `*-SESSION-*` → Agent-specific based on filename
- Default: `main-agent/`

#### 3. Archive Structure
Create if missing:
```
docs/archive/
  YYYY-MM/
    agent-6/
    agent-8/
    main-agent/
    research/
    README.md
```

#### 4. Link Updates
- Scan all `.md` files for links to archived files
- Update relative paths: `../planning/FILE.md` → `../archive/YYYY-MM/agent-X/FILE.md`
- Create redirect stubs for high-value files (optional)

#### 5. Index Generation
Update or create `docs/archive/YYYY-MM/README.md`:
```markdown
# Archive: January 2026

## Agent 6 (Streamlit/UI)
- [AGENT-6-SESSION-01.md](agent-6/AGENT-6-SESSION-01.md) - UI-001 implementation
- ...

## Agent 8 (Workflow Optimization)
- ...

## Main Agent
- ...

## Research
- ...
```

### Implementation Pseudocode
```bash
#!/bin/bash
set -euo pipefail

# Configuration
CUTOFF_DAYS=7
PLANNING_DIR="docs/planning"
ARCHIVE_BASE="docs/archive"
CURRENT_MONTH=$(date +%Y-%m)
DRY_RUN=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=true ;;
    --verbose) VERBOSE=true ;;
    --force) FORCE_FILES=("${@:2}"); break ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
  shift
done

# Create archive structure
create_archive_structure() {
  mkdir -p "$ARCHIVE_BASE/$CURRENT_MONTH"/{agent-6,agent-8,main-agent,research}
}

# Find old files
find_old_files() {
  if [ ${#FORCE_FILES[@]} -gt 0 ]; then
    echo "${FORCE_FILES[@]}"
  else
    find "$PLANNING_DIR" -name "*.md" -mtime +$CUTOFF_DAYS
  fi
}

# Categorize file
categorize_file() {
  local file=$1
  case $(basename "$file") in
    AGENT-6-*) echo "agent-6" ;;
    AGENT-8-*) echo "agent-8" ;;
    RESEARCH-*) echo "research" ;;
    *) echo "main-agent" ;;
  esac
}

# Move file
archive_file() {
  local src=$1
  local category=$(categorize_file "$src")
  local dest="$ARCHIVE_BASE/$CURRENT_MONTH/$category/$(basename "$src")"

  if [ "$DRY_RUN" = true ]; then
    echo "[DRY-RUN] Would move: $src → $dest"
  else
    [ "$VERBOSE" = true ] && echo "Moving: $src → $dest"
    mv "$src" "$dest"
  fi
}

# Update links
update_links() {
  local old_file=$1
  local new_path=$2

  # Find all markdown files
  find docs -name "*.md" -type f | while read file; do
    # Replace links
    sed -i "s|$old_file|$new_path|g" "$file"
  done
}

# Generate index
generate_index() {
  local index="$ARCHIVE_BASE/$CURRENT_MONTH/README.md"

  cat > "$index" <<EOF
# Archive: $(date +%B %Y)
**Created:** $(date +%Y-%m-%d)

## Agent 6 (Streamlit/UI)
EOF

  # List agent-6 files
  ls "$ARCHIVE_BASE/$CURRENT_MONTH/agent-6/" | while read file; do
    echo "- [$file](agent-6/$file)" >> "$index"
  done

  # Repeat for other categories...
}

# Main execution
main() {
  create_archive_structure

  find_old_files | while read file; do
    archive_file "$file"
  done

  if [ "$DRY_RUN" = false ]; then
    generate_index
    echo "✅ Archival complete"
  else
    echo "🔍 Dry-run complete (no files moved)"
  fi
}

main "$@"
```

### Exit Codes
- `0`: Success (files archived or dry-run complete)
- `1`: Error (permission denied, file not found, etc.)

### Testing
```bash
# Test dry-run
./scripts/archive_old_sessions.sh --dry-run

# Test with verbose
./scripts/archive_old_sessions.sh --verbose --dry-run

# Test force mode
./scripts/archive_old_sessions.sh --force OLD-FILE.md

# Verify archive structure
ls -R docs/archive/

# Verify index
cat docs/archive/$(date +%Y-%m)/README.md
```

---

## Script 2: check_wip_limits.sh

### Purpose
Enforce WIP (Work In Progress) limits to prevent organizational debt accumulation.

### Location
`scripts/check_wip_limits.sh`

### Usage
```bash
# Check all WIP limits
./scripts/check_wip_limits.sh

# Check specific limit only
./scripts/check_wip_limits.sh --worktrees
./scripts/check_wip_limits.sh --prs
./scripts/check_wip_limits.sh --docs
./scripts/check_wip_limits.sh --research

# Verbose output
./scripts/check_wip_limits.sh --verbose

# JSON output (for automation)
./scripts/check_wip_limits.sh --json
```

### WIP Limits

| Category | Limit | Rationale |
|----------|-------|-----------|
| Active Worktrees | 2 | Prevents context fragmentation |
| Open PRs | 5 | Forces completion before starting new |
| Active Docs | 10 | Maintains clean context |
| Research Tasks | 3 | Prevents analysis paralysis |

### Checks

#### 1. Worktrees Check
```bash
WORKTREE_COUNT=$(git worktree list | wc -l)
WORKTREE_LIMIT=2

if [ $WORKTREE_COUNT -gt $WORKTREE_LIMIT ]; then
  echo "❌ WORKTREE LIMIT EXCEEDED: $WORKTREE_COUNT/$WORKTREE_LIMIT"
  git worktree list
  exit 1
fi
```

#### 2. PRs Check
```bash
PR_COUNT=$(gh pr list --state open | wc -l)
PR_LIMIT=5

if [ $PR_COUNT -gt $PR_LIMIT ]; then
  echo "❌ PR LIMIT EXCEEDED: $PR_COUNT/$PR_LIMIT"
  gh pr list --state open
  exit 1
fi
```

#### 3. Docs Check
```bash
DOCS_COUNT=$(ls docs/planning/*.md 2>/dev/null | wc -l)
DOCS_LIMIT=10

if [ $DOCS_COUNT -gt $DOCS_LIMIT ]; then
  echo "❌ DOCS LIMIT EXCEEDED: $DOCS_COUNT/$DOCS_LIMIT"
  ls -lh docs/planning/*.md
  exit 1
fi
```

#### 4. Research Tasks Check
```bash
RESEARCH_COUNT=$(grep -c "RESEARCH-" docs/TASKS.md | grep -v "DONE" || true)
RESEARCH_LIMIT=3

if [ $RESEARCH_COUNT -gt $RESEARCH_LIMIT ]; then
  echo "❌ RESEARCH LIMIT EXCEEDED: $RESEARCH_COUNT/$RESEARCH_LIMIT"
  grep "RESEARCH-" docs/TASKS.md | grep -v "DONE"
  exit 1
fi
```

### Output Formats

**Standard Output:**
```
Checking WIP Limits...
✅ Worktrees: 2/2
✅ Open PRs: 3/5
✅ Active Docs: 8/10
✅ Research Tasks: 2/3

All WIP limits OK
```

**Verbose Output:**
```
Checking WIP Limits...

Worktrees (2/2):
  /path/to/main (main)
  /path/to/worktree-agent-6 (feat/ui-feature)

Open PRs (3/5):
  #315 - feat: UI enhancement
  #314 - fix: bug in calculator
  #313 - docs: update guide

Active Docs (8/10):
  next-session-brief.md
  GOVERNANCE-METRICS.md
  ...

Research Tasks (2/3):
  RESEARCH-001: Investigate optimization
  RESEARCH-002: Explore new API

All WIP limits OK
```

**JSON Output:**
```json
{
  "worktrees": {"current": 2, "limit": 2, "ok": true},
  "prs": {"current": 3, "limit": 5, "ok": true},
  "docs": {"current": 8, "limit": 10, "ok": true},
  "research": {"current": 2, "limit": 3, "ok": true},
  "overall": "pass"
}
```

### Exit Codes
- `0`: All limits OK
- `1`: One or more limits exceeded
- `2`: Configuration error

### Integration

#### Pre-Commit Hook
```bash
# .git/hooks/pre-commit
./scripts/check_wip_limits.sh --docs --research
if [ $? -ne 0 ]; then
  echo "⚠️  WIP limits exceeded. Consider cleanup before new work."
  # Allow commit but warn
fi
```

#### GitHub Action
```yaml
# .github/workflows/wip-limits.yml
name: WIP Limits Check
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check WIP Limits
        run: ./scripts/check_wip_limits.sh --json
```

---

## Script 3: check_version_consistency.sh

### Purpose
Ensure all version references across the codebase match the current version.

### Location
`scripts/check_version_consistency.sh`

### Usage
```bash
# Check consistency
./scripts/check_version_consistency.sh

# Auto-fix inconsistencies
./scripts/check_version_consistency.sh --fix

# Check specific location only
./scripts/check_version_consistency.sh --check-python
./scripts/check_version_consistency.sh --check-vba
./scripts/check_version_consistency.sh --check-docs

# Verbose output
./scripts/check_version_consistency.sh --verbose
```

### Version Sources (3 Critical Locations)

1. **pyproject.toml** (Python package version)
   ```toml
   [project]
   version = "0.16.0"
   ```

2. **VBA VERSION Constant**
   ```vba
   ' VBA/Modules/M15_Constants.bas
   Public Const VERSION As String = "0.16.0"
   ```

3. **Documentation** (all markdown files)
   ```markdown
   Current version: v0.16.0
   ```

### Check Algorithm

```bash
#!/bin/bash

# Extract current version
PYTHON_VERSION=$(grep -oP '(?<=version = ")[^"]+' pyproject.toml)
VBA_VERSION=$(grep -oP '(?<=VERSION As String = ")[^"]+' VBA/Modules/M15_Constants.bas)

# Check if they match
if [ "$PYTHON_VERSION" != "$VBA_VERSION" ]; then
  echo "❌ Version mismatch:"
  echo "  Python: $PYTHON_VERSION"
  echo "  VBA: $VBA_VERSION"
  exit 1
fi

CURRENT_VERSION="$PYTHON_VERSION"

# Check documentation
DOC_MISMATCHES=$(grep -rn "v0\.[0-9]\+\.[0-9]\+" docs/ | grep -v "v$CURRENT_VERSION" | grep -v "archive" || true)

if [ -n "$DOC_MISMATCHES" ]; then
  echo "❌ Stale version references found:"
  echo "$DOC_MISMATCHES"
  exit 1
fi

echo "✅ All version references consistent: $CURRENT_VERSION"
```

### Auto-Fix Mode

```bash
# --fix mode
if [ "$FIX_MODE" = true ]; then
  # Update docs
  find docs -name "*.md" -not -path "*/archive/*" -exec \
    sed -i "s/v0\.[0-9]\+\.[0-9]\+/v$CURRENT_VERSION/g" {} \;

  echo "✅ Updated all version references to v$CURRENT_VERSION"
  echo "⚠️  Please review changes: git diff"
fi
```

### Exit Codes
- `0`: All versions consistent
- `1`: Inconsistencies found
- `2`: Configuration error (files not found)

### Testing
```bash
# Test detection
./scripts/check_version_consistency.sh

# Test fix mode
./scripts/check_version_consistency.sh --fix

# Verify fix
git diff docs/

# Check again
./scripts/check_version_consistency.sh
```

---

## Script 4: generate_health_report.sh

### Purpose
Generate sustainability metrics report for governance review.

### Location
`scripts/generate_health_report.sh`

### Usage
```bash
# Generate weekly report
./scripts/generate_health_report.sh --weekly

# Generate monthly report
./scripts/generate_health_report.sh --monthly

# Output to file
./scripts/generate_health_report.sh --weekly --output docs/planning/health-report-$(date +%Y-%m-%d).md

# JSON format
./scripts/generate_health_report.sh --weekly --json
```

### Metrics Collected

#### Sustainability Indicators
```bash
# Commits/day (7-day average)
COMMITS_7D=$(git log --since="7 days ago" --oneline | wc -l)
COMMITS_PER_DAY=$((COMMITS_7D / 7))

# Active docs count
ACTIVE_DOCS=$(ls docs/planning/*.md | wc -l)

# Feature:Governance ratio (from SESSION_LOG)
FEATURE_SESSIONS=$(grep -c "Feature" docs/SESSION_LOG.md || true)
GOVERNANCE_SESSIONS=$(grep -c "Governance" docs/SESSION_LOG.md || true)

# WIP compliance
WIP_CHECK=$(./scripts/check_wip_limits.sh --json)
```

#### Velocity Indicators
```bash
# PRs merged (7 days)
PRS_MERGED=$(gh pr list --state merged --search "merged:>=$(date -d '7 days ago' +%Y-%m-%d)" --json number | jq length)

# Test count
TEST_COUNT=$(.venv/bin/python -m pytest --collect-only | grep -oP '\d+ items$' | awk '{print $1}')

# Code quality
RUFF_ERRORS=$(.venv/bin/python -m ruff check Python/ --statistics | tail -n 1 | awk '{print $1}')
MYPY_ERRORS=$(.venv/bin/python -m mypy Python/structural_lib/ 2>&1 | grep -c "error:" || echo "0")
```

#### Health Indicators
```bash
# Worktrees
WORKTREES=$(git worktree list | wc -l)

# Open PRs
OPEN_PRS=$(gh pr list --state open | wc -l)

# Research tasks
RESEARCH=$(grep -c "RESEARCH-" docs/TASKS.md | grep -v "DONE" || echo "0")
```

### Report Format

**Markdown Output:**
```markdown
# Health Report: $(date +%Y-%m-%d)
**Period:** Last 7 days
**Generated:** $(date +%Y-%m-%d %H:%M:%S)

## Sustainability Indicators
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Commits/Day | 55 | 50-75 | ✅ |
| Active Docs | 8 | <10 | ✅ |
| F:G Ratio | 4:1 | 4:1 | ✅ |
| WIP Compliance | 100% | 100% | ✅ |

## Velocity Indicators
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| PRs/Week | 12 | 10-15 | ✅ |
| Test Count | 2,380 | +50/week | ✅ |
| Code Quality | 0 errors | 0 | ✅ |

## Health Indicators
| Metric | Current | Limit | Status |
|--------|---------|-------|--------|
| Worktrees | 2 | 2 | ✅ |
| Open PRs | 4 | 5 | ✅ |
| Research | 2 | 3 | ✅ |

## Trends
- Commits/day: Stable (was 58, now 55)
- Active docs: Improving (was 15, now 8)
- WIP compliance: Excellent (no violations)

## Recommendations
- Continue current pace
- No policy adjustments needed
- Next governance session: $(date -d '+7 days' +%Y-%m-%d)
```

**JSON Output:**
```json
{
  "date": "2026-01-10",
  "period": "7d",
  "sustainability": {
    "commits_per_day": {"current": 55, "target": [50, 75], "status": "pass"},
    "active_docs": {"current": 8, "target": 10, "status": "pass"},
    "fg_ratio": {"current": [4, 1], "target": [4, 1], "status": "pass"},
    "wip_compliance": {"current": 100, "target": 100, "status": "pass"}
  },
  "velocity": {
    "prs_per_week": {"current": 12, "target": [10, 15], "status": "pass"},
    "test_count": {"current": 2380, "growth": 50, "status": "pass"},
    "code_quality": {"ruff": 0, "mypy": 0, "status": "pass"}
  },
  "health": {
    "worktrees": {"current": 2, "limit": 2, "status": "pass"},
    "open_prs": {"current": 4, "limit": 5, "status": "pass"},
    "research": {"current": 2, "limit": 3, "status": "pass"}
  },
  "overall": "healthy"
}
```

---

## Script 5: monthly_maintenance.sh

### Purpose
Comprehensive monthly cleanup and health check.

### Location
`scripts/monthly_maintenance.sh`

### Usage
```bash
# Full monthly maintenance
./scripts/monthly_maintenance.sh

# Checks only (no cleanup)
./scripts/monthly_maintenance.sh --checks-only

# Dry run (show what would be done)
./scripts/monthly_maintenance.sh --dry-run

# Specific tasks only
./scripts/monthly_maintenance.sh --archive-only
./scripts/monthly_maintenance.sh --cleanup-only
```

### Tasks Performed

1. **Archive Previous Month's Docs** (15 min)
   ```bash
   # Create monthly archive structure
   mkdir -p docs/archive/$(date -d 'last month' +%Y-%m)/{agent-6,agent-8,main-agent,research}

   # Move old docs
   ./scripts/archive_old_sessions.sh
   ```

2. **Clean Up Merged Worktrees** (10 min)
   ```bash
   # List worktrees
   git worktree list | while read wt; do
     # Check if branch is merged
     # If merged: git worktree remove $wt
   done
   ```

3. **Delete Merged Remote Branches** (10 min)
   ```bash
   # Get merged PRs from last month
   gh pr list --state merged --search "merged:>=$(date -d '30 days ago' +%Y-%m-%d)" --json headRefName | \
     jq -r '.[].headRefName' | \
     xargs -I {} git push origin --delete {}
   ```

4. **Version Consistency Check** (5 min)
   ```bash
   ./scripts/check_version_consistency.sh
   ```

5. **Link Validation** (10 min)
   ```bash
   .venv/bin/python scripts/check_links.py
   ```

6. **Generate Monthly Health Report** (10 min)
   ```bash
   ./scripts/generate_health_report.sh --monthly --output docs/planning/health-report-$(date +%Y-%m).md
   ```

7. **Create Archive Index** (10 min)
   ```bash
   # Generate README for last month's archive
   cat > docs/archive/$(date -d 'last month' +%Y-%m)/README.md <<EOF
   # Archive: $(date -d 'last month' +%B %Y)
   ...
   EOF
   ```

### Output
```
Running Monthly Maintenance...

[1/7] Archiving previous month's docs...
  ✅ 23 files archived

[2/7] Cleaning up merged worktrees...
  ✅ 1 worktree removed

[3/7] Deleting merged remote branches...
  ✅ 8 branches deleted

[4/7] Checking version consistency...
  ✅ All versions consistent

[5/7] Validating links...
  ✅ All links valid

[6/7] Generating monthly health report...
  ✅ Report saved to docs/planning/health-report-2026-01.md

[7/7] Creating archive index...
  ✅ Index created

Monthly maintenance complete! ✅
```

---

## Script Maintenance Guidelines

### Adding New Scripts

1. **Create script in `scripts/`**
2. **Add to this document** (complete specification)
3. **Add usage to CHECKLISTS.md**
4. **Add to appropriate workflow in WORKFLOWS.md**
5. **Test thoroughly** (dry-run mode, error cases)
6. **Document in SESSION_LOG.md** (when implemented)

### Script Quality Standards

- **Error handling:** Use `set -euo pipefail`
- **Logging:** Verbose and quiet modes
- **Dry-run:** Always provide `--dry-run` option
- **Help text:** Include `--help` with usage examples
- **Exit codes:** 0 = success, 1 = error, 2 = usage error
- **Testing:** Test both success and failure cases

### Common Patterns

```bash
#!/bin/bash
set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DRY_RUN=false
VERBOSE=false

# Logging functions
log() { echo "[$(date +%H:%M:%S)] $*"; }
verbose() { [ "$VERBOSE" = true ] && echo "[VERBOSE] $*"; }
error() { echo "[ERROR] $*" >&2; exit 1; }

# Help text
usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Description of script

Options:
  --dry-run    Show what would be done
  --verbose    Verbose output
  --help       Show this help

Examples:
  $(basename "$0") --dry-run
  $(basename "$0") --verbose
EOF
  exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run) DRY_RUN=true ;;
    --verbose) VERBOSE=true ;;
    --help) usage ;;
    *) error "Unknown option: $1" ;;
  esac
  shift
done

# Main logic
main() {
  log "Starting..."

  # Do work

  log "Complete"
}

main "$@"
```

---

## Related Documentation

- **[README.md](README.md)** - Main specification
- **[WORKFLOWS.md](WORKFLOWS.md)** - Workflow procedures
- **[CHECKLISTS.md](CHECKLISTS.md)** - Operational checklists

---

**Last Updated:** 2026-01-10 | **Version:** 1.0.0
