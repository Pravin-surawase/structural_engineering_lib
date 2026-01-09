# Agent 9: Operational Workflows

**Purpose:** Detailed step-by-step procedures for governance sessions
**Audience:** AI agents executing governance tasks
**Last Updated:** 2026-01-10

---

## Table of Contents

1. [Weekly Maintenance Session](#workflow-1-weekly-maintenance-session)
2. [Pre-Release Governance](#workflow-2-pre-release-governance)
3. [Monthly Governance Review](#workflow-3-monthly-governance-review)
4. [Emergency Cleanup Triage](#workflow-4-emergency-cleanup-triage)

---

## Workflow 1: Weekly Maintenance Session

**Trigger:** Every 5th session (20% of development time)
**Duration:** 2-4 hours
**Frequency:** Weekly (Feature → Feature → Feature → Feature → Governance)

### Phase 1: Documentation Cleanup (45 min)

```bash
# Step 1: Run archival script
./scripts/archive_old_sessions.sh --dry-run
# Review what will be moved
./scripts/archive_old_sessions.sh
# Execute archival

# Step 2: Verify archive structure
ls -R docs/archive/
# Should see: YYYY-MM/agent-6/, agent-8/, main-agent/, research/

# Step 3: Check archive index
cat docs/archive/$(date +%Y-%m)/README.md
# Should have table of contents with all archived files

# Step 4: Count active docs
ls docs/planning/*.md | wc -l
# Target: <10 files
# If >10: Review and archive more aggressively
```

**Success Criteria:**
- ✅ All docs older than 7 days archived
- ✅ Archive has proper folder structure
- ✅ Archive index up to date
- ✅ Active docs count <10

**Time Check:** 45 minutes elapsed → Continue

---

### Phase 2: Worktree & Branch Cleanup (30 min)

```bash
# Step 5: List active worktrees
git worktree list
# Target: Max 2 (main + 1 agent worktree)
# If >2: Identify and clean up completed worktrees

# Step 6: Clean up merged worktrees
for wt in $(git worktree list --porcelain | grep "worktree" | awk '{print $2}'); do
  # Check if worktree branch is merged
  # If merged and pushed: git worktree remove $wt
done

# Step 7: List remote branches
git branch -r | grep -v "HEAD\|main"
# Identify merged feature branches

# Step 8: Delete merged feature branches
gh pr list --state merged --limit 20 --json headRefName | \
  jq -r '.[].headRefName' | \
  xargs -I {} git push origin --delete {}

# Step 9: Clean up local references
git remote prune origin
git fetch --prune
```

**Success Criteria:**
- ✅ Active worktrees ≤2
- ✅ Merged feature branches deleted
- ✅ Remote references clean

**Time Check:** 1h 15min elapsed → Continue

---

### Phase 3: Version Consistency Check (30 min)

```bash
# Step 10: Run version consistency checker
./scripts/check_version_consistency.sh
# Lists any version mismatches

# Step 11: Review mismatches
# Common issues:
# - Old docs still referencing v0.15.0
# - CHANGELOG not updated to v0.16.0
# - VBA VERSION constant outdated

# Step 12: Auto-fix if available
./scripts/check_version_consistency.sh --fix
# OR manually update files

# Step 13: Verify fix
./scripts/check_version_consistency.sh
# Should show: "All version references consistent"
```

**Success Criteria:**
- ✅ All version references match current version
- ✅ pyproject.toml = VBA = docs/
- ✅ No stale version references

**Time Check:** 1h 45min elapsed → Continue

---

### Phase 4: Link Validation (15 min)

```bash
# Step 14: Run link checker
.venv/bin/python scripts/check_links.py
# Scans all markdown files for broken links

# Step 15: Review broken links
# Common causes:
# - Files moved during archival
# - Renamed files
# - External URLs changed

# Step 16: Fix broken links
# Option A: Update redirect stubs
# Option B: Update source links
# Option C: Remove dead links

# Step 17: Re-run checker
.venv/bin/python scripts/check_links.py
# Should show: "All links valid"
```

**Success Criteria:**
- ✅ No broken internal links
- ✅ Redirect stubs created if needed
- ✅ External links verified

**Time Check:** 2h elapsed → Continue

---

### Phase 5: Metrics Collection (30 min)

```bash
# Step 18: Generate health report
./scripts/generate_health_report.sh --weekly

# Manual metrics collection:

# Commits this week
git log --since="1 week ago" --oneline | wc -l

# PRs merged this week
gh pr list --state merged --search "merged:>=$(date -d '7 days ago' +%Y-%m-%d)" --json number | jq length

# Docs created this week
find docs/planning -name "*.md" -mtime -7 | wc -l

# Current test count
.venv/bin/python -m pytest --collect-only | grep "test session starts"

# Code quality
.venv/bin/python -m ruff check Python/ --statistics
.venv/bin/python -m mypy Python/structural_lib/ --no-error-summary
```

**Step 19: Update metrics dashboard**
```bash
# Update docs/planning/GOVERNANCE-METRICS.md
# Or create if first time
cat > docs/planning/GOVERNANCE-METRICS.md <<EOF
# Governance Metrics Dashboard
**Week:** $(date +%Y-W%U)
**Updated:** $(date +%Y-%m-%d)

## Sustainability Indicators
- Commits/Day: XX (target: 50-75)
- Active Docs: XX (target: <10)
- Feature:Governance Ratio: X:X (target: 80:20)
- WIP Compliance: XX% (target: 100%)

## Velocity Indicators
- PRs Merged/Week: XX (target: 10-15)
- Test Count: XXXX tests
- Code Quality: X ruff errors, X mypy errors

## Health Indicators
- Worktrees: X/2
- Open PRs: X/5
- Research Tasks: X/3
EOF
```

**Success Criteria:**
- ✅ Weekly metrics collected
- ✅ GOVERNANCE-METRICS.md updated
- ✅ Trends identified (improving/declining)

**Time Check:** 2h 30min elapsed → Continue

---

### Phase 6: Governance Adjustments (30 min)

```bash
# Step 20: Review metrics for risks
# Questions to ask:
# - Is commits/day trending up unsustainably?
# - Are WIP limits being violated?
# - Is documentation sprawling again?
# - Are we maintaining 80/20 ratio?

# Step 21: Recommend policy adjustments
# Examples:
# - "Commits/day at 85 → recommend stricter PR batching"
# - "3 worktrees active → enforce cleanup before new work"
# - "15 active docs → run archive script more aggressively"

# Step 22: Update governance documentation
# If policies need adjustment:
vim agents/agent-9/README.md
# Update WIP limits, targets, or procedures

# Step 23: Commit governance updates
git add agents/agent-9/ docs/planning/GOVERNANCE-METRICS.md
git commit -m "chore(governance): weekly maintenance $(date +%Y-%m-%d)"
git push
```

**Success Criteria:**
- ✅ Sustainability risks identified
- ✅ Recommendations documented
- ✅ Policies updated if needed
- ✅ Changes committed

**Total Time:** ~2-4 hours

---

## Workflow 2: Pre-Release Governance

**Trigger:** 3 days before scheduled release
**Duration:** 1-2 hours
**Frequency:** Bi-weekly (with each release)

### Phase 1: Feature Freeze Announcement (15 min)

```bash
# Step 1: Update next-session-brief.md
cat >> docs/planning/next-session-brief.md <<EOF

## 🔒 FEATURE FREEZE: v0.X.0
**Release Date:** YYYY-MM-DD
**Freeze Start:** $(date +%Y-%m-%d)
**Duration:** 3 days

**Policy:**
- ✅ Bug fixes allowed
- ✅ Documentation updates allowed
- ✅ Test improvements allowed
- ❌ New features blocked
- ❌ Breaking changes blocked
- ❌ Large refactors blocked

**Why:** Quality assurance window before release
EOF

# Step 2: Update TASKS.md with release blockers
# Add label to any critical bugs: [RELEASE-BLOCKER]

# Step 3: Communicate freeze
# Post in session notes, commit message, etc.
```

---

### Phase 2: Release Quality Checks (30 min)

```bash
# Step 4: Run full test suite
cd Python
.venv/bin/pytest -q
# Should show: 2370+ tests passing

# Step 5: Check code quality
.venv/bin/python -m ruff check Python/
.venv/bin/python -m mypy Python/structural_lib/
# Should show: 0 errors

# Step 6: Verify documentation
# Check CHANGELOG.md
cat CHANGELOG.md | head -n 50
# Should list all features/fixes for this release

# Check RELEASES.md
cat docs/releases.md | head -n 50
# Should have release notes draft

# Step 7: Verify version bumped in 3 places
grep "version" pyproject.toml
# Should show: version = "0.X.0"

grep "VERSION" VBA/Modules/M15_Constants.bas
# Should show: Public Const VERSION As String = "0.X.0"

grep "v0.X.0" docs/*.md | wc -l
# Should show multiple references
```

---

### Phase 3: Documentation Cleanup (30 min)

```bash
# Step 8: Archive pre-release session docs
./scripts/archive_old_sessions.sh

# Step 9: Update all version references
./scripts/check_version_consistency.sh --fix

# Step 10: Run link checker
.venv/bin/python scripts/check_links.py
# Fix any broken links

# Step 11: Final formatting pass
.venv/bin/python -m black Python/
.venv/bin/python -m ruff check --fix Python/
```

---

### Phase 4: Release Readiness Report (15 min)

```bash
# Step 12: Generate readiness checklist
cat > docs/planning/RELEASE-READINESS-v0.X.0.md <<EOF
# Release Readiness: v0.X.0
**Date:** $(date +%Y-%m-%d)
**Target Release:** YYYY-MM-DD

## Quality Gates
- [ ] All tests passing (2370+)
- [ ] 0 ruff errors
- [ ] 0 mypy errors
- [ ] CHANGELOG.md updated
- [ ] RELEASES.md updated
- [ ] Version bumped (3 places)
- [ ] Documentation archived
- [ ] Links validated
- [ ] Code formatted

## Blockers
- List any release-blocking issues

## Go/No-Go Decision
**Recommendation:** GO / NO-GO
**Reason:** ...
EOF

# Step 13: Review and commit
git add docs/planning/RELEASE-READINESS-v0.X.0.md
git commit -m "chore(release): v0.X.0 readiness report"
git push
```

**Total Time:** ~1-2 hours

---

## Workflow 3: Monthly Governance Review

**Trigger:** First session of each month
**Duration:** 3-4 hours
**Frequency:** Monthly

### Phase 1: Metrics Analysis (1 hour)

```bash
# Step 1: Collect 30-day metrics
# Commits
git log --since="30 days ago" --oneline | wc -l
git log --since="30 days ago" --pretty=format:"%ad" --date=short | uniq -c

# PRs
gh pr list --state merged --search "merged:>=$(date -d '30 days ago' +%Y-%m-%d)" --json number,title,mergedAt
gh pr list --state open --json number,title,createdAt

# Lines of code
git diff --shortstat HEAD@{30.days.ago}

# Test count growth
# (Compare current vs 30 days ago)

# Documentation growth
find docs -name "*.md" -mtime -30 | wc -l
find docs -name "*.md" | wc -l

# Step 2: Calculate ratios
# Commits/day = total commits / 30
# PRs/day = total PRs / 30
# Docs/week = (docs created in 30 days) / 4

# Step 3: Identify trends
# Plot data points mentally or in spreadsheet
# - Is pace sustainable?
# - Is debt accumulating or reducing?
# - Are policies working?
```

---

### Phase 2: Archive Organization (1 hour)

```bash
# Step 4: Create new monthly archive
mkdir -p docs/archive/$(date +%Y-%m)/
mkdir -p docs/archive/$(date +%Y-%m)/agent-6/
mkdir -p docs/archive/$(date +%Y-%m)/agent-8/
mkdir -p docs/archive/$(date +%Y-%m)/main-agent/
mkdir -p docs/archive/$(date +%Y-%m)/research/

# Step 5: Move previous month's docs
# Find all docs from previous month in docs/planning/
find docs/planning -name "*$(date -d 'last month' +%Y-%m)*" -type f

# Move to appropriate archive subdirectories
# Based on filename patterns:
# - AGENT-6-* → agent-6/
# - AGENT-8-* → agent-8/
# - RESEARCH-* → research/
# - Others → main-agent/

# Step 6: Update archive index
cat > docs/archive/$(date +%Y-%m)/README.md <<EOF
# Archive: $(date +%B %Y)

## Agent 6 (Streamlit/UI)
- [List archived files here]

## Agent 8 (Workflow Optimization)
- [List archived files here]

## Main Agent
- [List archived files here]

## Research
- [List archived files here]
EOF

# Step 7: Verify no broken links
.venv/bin/python scripts/check_links.py
# Fix any broken links with redirect stubs
```

---

### Phase 3: Policy Review (1 hour)

```bash
# Step 8: Review WIP limits effectiveness
# Questions:
# - Have we stayed within limits?
# - Are limits too tight or too loose?
# - Have violations correlated with issues?

# Step 9: Review 80/20 ratio
# Count sessions from SESSION_LOG.md:
# - Feature sessions: X
# - Governance sessions: Y
# - Ratio: X:Y (target 80:20 = 4:1)

# Step 10: Review release cadence
# - Were releases on time?
# - Was feature freeze effective?
# - Were there quality issues?

# Step 11: Recommend policy adjustments
# Example recommendations:
# - "Increase WIP limit to 3 worktrees (we've been compliant)"
# - "Tighten active docs limit to 8 (we've had sprawl)"
# - "Extend feature freeze to 5 days (more quality time)"

# Step 12: Document recommendations
cat > docs/planning/GOVERNANCE-REVIEW-$(date +%Y-%m).md <<EOF
# Governance Review: $(date +%B %Y)

## Metrics Summary
- Commits/day: XX (target: 50-75)
- Feature:Governance ratio: X:X (target: 4:1)
- WIP compliance: XX%

## Policy Effectiveness
- WIP Limits: EFFECTIVE / NEEDS ADJUSTMENT
- 80/20 Ratio: MAINTAINED / DRIFTED
- Release Cadence: ON TRACK / DELAYED

## Recommendations
1. [Recommendation 1]
2. [Recommendation 2]
...
EOF
```

---

### Phase 4: Automation Health (1 hour)

```bash
# Step 13: Test all governance scripts
./scripts/archive_old_sessions.sh --dry-run
./scripts/check_wip_limits.sh
./scripts/check_version_consistency.sh
./scripts/generate_health_report.sh --weekly

# Step 14: Review GitHub Actions
cat .github/workflows/git-workflow-tests.yml
# Check for failures in recent runs:
gh run list --workflow=git-workflow-tests.yml --limit 10

# Step 15: Identify automation gaps
# Questions:
# - Are there manual steps we repeat?
# - Are there checks we forgot to automate?
# - Are scripts failing silently?

# Step 16: Improve automation
# Examples:
# - Add new script for recurring task
# - Fix bugs in existing scripts
# - Add better error messages
# - Improve logging

# Step 17: Update automation docs
vim agents/agent-9/AUTOMATION.md
# Document new scripts or changes
```

**Total Time:** ~3-4 hours

---

## Workflow 4: Emergency Cleanup Triage

**Trigger:** Critical sustainability metrics exceeded
**Duration:** 1 hour
**Purpose:** Rapid assessment and prioritized cleanup

### Triage Process

```bash
# Step 1: Assess severity (5 min)
# Check critical limits:
ACTIVE_DOCS=$(ls docs/planning/*.md | wc -l)
OPEN_PRS=$(gh pr list --state open | wc -l)
WORKTREES=$(git worktree list | wc -l)

# Red flags:
# - Active docs >20 (critical)
# - Open PRs >10 (critical)
# - Worktrees >3 (critical)

# Step 2: Prioritize by impact (10 min)
# High impact: Blocks new work
# Medium impact: Slows down agents
# Low impact: Organizational debt

# Step 3: Execute rapid cleanup (40 min)
# Focus on highest impact items first

# Example: Docs cleanup
./scripts/archive_old_sessions.sh
# Should immediately reduce to <10

# Example: PR cleanup
gh pr list --state open --json number,title
# Close/merge stale PRs

# Example: Worktree cleanup
git worktree list
git worktree remove <path>

# Step 4: Verify resolution (5 min)
# Re-check metrics
# All critical limits back to green?
```

**Output:** Cleaned state + triage report documenting actions taken

---

## Best Practices

### ✅ DO
- Follow workflows in order (phases build on each other)
- Document deviations from standard workflow
- Update metrics dashboards after each session
- Commit governance changes immediately
- Use checklists to track progress

### ❌ DON'T
- Skip phases (they're all important)
- Rush through metrics collection (data quality matters)
- Ignore trends (early warning system)
- Forget to commit changes
- Batch multiple governance types (one session = one workflow)

---

## Time Management

| Workflow | Typical Duration | Can Be Shortened | Emergency Mode |
|----------|------------------|------------------|----------------|
| Weekly Maintenance | 2-4 hours | 1.5 hours (skip optional) | 1 hour (critical only) |
| Pre-Release | 1-2 hours | 1 hour (automated checks) | 30 min (go/no-go only) |
| Monthly Review | 3-4 hours | 2 hours (skip deep analysis) | N/A (not for emergency) |
| Emergency Triage | 1 hour | N/A (already minimal) | 30 min (top priority only) |

---

## Related Documentation

- **[README.md](README.md)** - Main specification
- **[CHECKLISTS.md](CHECKLISTS.md)** - Copy-paste ready checklists
- **[AUTOMATION.md](AUTOMATION.md)** - Script specifications
- **[METRICS.md](METRICS.md)** - Tracking templates
- **[KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md)** - Git/CI governance

---

**Last Updated:** 2026-01-10 | **Version:** 1.0.0
