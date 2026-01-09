# Agent 9: Operational Checklists

**Purpose:** Copy-paste ready checklists for governance sessions
**Usage:** Use these during sessions to track progress
**Last Updated:** 2026-01-10

---

## Table of Contents

1. [Weekly Maintenance Checklist](#checklist-1-weekly-maintenance)
2. [Pre-Release Checklist](#checklist-2-pre-release)
3. [Monthly Review Checklist](#checklist-3-monthly-review)
4. [Emergency Triage Checklist](#checklist-4-emergency-triage)
5. [Quick Health Check](#checklist-5-quick-health-check)

---

## Checklist 1: Weekly Maintenance

**Duration:** 2-4 hours | **Frequency:** Every 5th session

### Phase 1: Documentation Cleanup (45 min)
- [ ] Run archive script dry-run: `./scripts/archive_old_sessions.sh --dry-run`
- [ ] Review files to be archived (verify nothing critical)
- [ ] Execute archival: `./scripts/archive_old_sessions.sh`
- [ ] Verify archive structure: `ls -R docs/archive/`
- [ ] Check archive index: `cat docs/archive/$(date +%Y-%m)/README.md`
- [ ] Count active docs: `ls docs/planning/*.md | wc -l` (target: <10)
- [ ] If >10: Identify and archive additional files
- [ ] Commit changes: `git add docs/ && git commit -m "chore(docs): weekly archive"`

**Success Criteria:**
- ✅ All docs >7 days old archived
- ✅ Archive index up to date
- ✅ Active docs <10

---

### Phase 2: Worktree & Branch Cleanup (30 min)
- [ ] List worktrees: `git worktree list` (target: max 2)
- [ ] Identify merged worktrees (check if work is done)
- [ ] Remove completed worktrees: `git worktree remove <path>`
- [ ] List remote branches: `git branch -r | grep -v "HEAD\|main"`
- [ ] Identify merged feature branches
- [ ] Delete merged branches: `gh pr list --state merged --limit 20 --json headRefName | jq -r '.[].headRefName' | xargs -I {} git push origin --delete {}`
- [ ] Prune remote references: `git remote prune origin && git fetch --prune`
- [ ] Verify cleanup: `git worktree list` and `git branch -r`

**Success Criteria:**
- ✅ Worktrees ≤2
- ✅ Merged branches deleted
- ✅ Remote refs clean

---

### Phase 3: Version Consistency (30 min)
- [ ] Run version checker: `./scripts/check_version_consistency.sh`
- [ ] Review reported mismatches
- [ ] Auto-fix if available: `./scripts/check_version_consistency.sh --fix`
- [ ] OR manually update files with stale versions
- [ ] Verify all references: `grep -r "v0\.1[0-9]\." docs/ | grep -v "archive"`
- [ ] Check three critical locations:
  - [ ] pyproject.toml version field
  - [ ] VBA VERSION constant
  - [ ] docs/ version references
- [ ] Re-run checker: `./scripts/check_version_consistency.sh` (should pass)

**Success Criteria:**
- ✅ All version refs match current
- ✅ No stale version references
- ✅ Checker shows "consistent"

---

### Phase 4: Link Validation (15 min)
- [ ] Run link checker: `.venv/bin/python scripts/check_links.py`
- [ ] Review broken links report
- [ ] Categorize issues:
  - [ ] Internal links (files moved)
  - [ ] Redirect stubs needed
  - [ ] External links (verify manually)
- [ ] Fix internal links:
  - [ ] Update source documents
  - [ ] OR create redirect stubs
- [ ] Verify external links (spot-check critical ones)
- [ ] Re-run checker: `.venv/bin/python scripts/check_links.py` (should pass)

**Success Criteria:**
- ✅ No broken internal links
- ✅ Redirect stubs created
- ✅ Checker passes

---

### Phase 5: Metrics Collection (30 min)
- [ ] Generate weekly health report: `./scripts/generate_health_report.sh --weekly`
- [ ] Collect manual metrics:
  - [ ] Commits this week: `git log --since="1 week ago" --oneline | wc -l`
  - [ ] PRs merged: `gh pr list --state merged --search "merged:>=$(date -d '7 days ago' +%Y-%m-%d)" --json number | jq length`
  - [ ] Docs created: `find docs/planning -name "*.md" -mtime -7 | wc -l`
  - [ ] Test count: `.venv/bin/python -m pytest --collect-only | grep "test session"`
  - [ ] Code quality: `ruff check Python/ --statistics` and `mypy Python/structural_lib/`
- [ ] Update GOVERNANCE-METRICS.md with:
  - [ ] Commits/day average
  - [ ] Active docs count
  - [ ] Feature:Governance ratio
  - [ ] WIP compliance %
  - [ ] PRs merged this week
  - [ ] Test count
  - [ ] Code quality status
- [ ] Identify trends (improving/declining/stable)

**Success Criteria:**
- ✅ Metrics collected and documented
- ✅ Dashboard updated
- ✅ Trends noted

---

### Phase 6: Governance Adjustments (30 min)
- [ ] Review metrics for sustainability risks:
  - [ ] Is commits/day sustainable? (target: 50-75)
  - [ ] Are WIP limits being violated?
  - [ ] Is doc sprawl returning? (target: <10)
  - [ ] Is 80/20 ratio maintained? (4:1 sessions)
- [ ] Identify policy effectiveness:
  - [ ] WIP limits: EFFECTIVE / NEEDS ADJUSTMENT
  - [ ] Release cadence: ON TRACK / DELAYED
  - [ ] Documentation lifecycle: WORKING / NEEDS TWEAKING
- [ ] Document recommendations:
  - [ ] What's working well?
  - [ ] What needs adjustment?
  - [ ] Specific action items
- [ ] Update governance policies if needed: `vim agents/agent-9/README.md`
- [ ] Commit governance updates: `git add agents/agent-9/ docs/planning/ && git commit -m "chore(governance): weekly maintenance $(date +%Y-%m-%d)"`
- [ ] Push changes: `git push`

**Success Criteria:**
- ✅ Risks identified
- ✅ Recommendations documented
- ✅ Changes committed

**Total Time:** ~2-4 hours

---

## Checklist 2: Pre-Release

**Duration:** 1-2 hours | **Frequency:** 3 days before each release

### Phase 1: Feature Freeze (15 min)
- [ ] Calculate release date (2 weeks from last release)
- [ ] Announce feature freeze in `docs/planning/next-session-brief.md`
- [ ] Add freeze policy:
  - [ ] ✅ Bug fixes allowed
  - [ ] ✅ Docs allowed
  - [ ] ✅ Tests allowed
  - [ ] ❌ New features blocked
  - [ ] ❌ Breaking changes blocked
- [ ] Update TASKS.md with [RELEASE-BLOCKER] labels
- [ ] Commit announcement: `git add docs/ && git commit -m "chore(release): feature freeze for v0.X.0"`

**Success Criteria:**
- ✅ Freeze announced
- ✅ Policy communicated
- ✅ Blockers identified

---

### Phase 2: Quality Gates (30 min)
- [ ] Run full test suite: `cd Python && .venv/bin/pytest -q`
  - [ ] Verify: 2370+ tests passing
- [ ] Check code quality:
  - [ ] Ruff: `.venv/bin/python -m ruff check Python/` (target: 0 errors)
  - [ ] Mypy: `.venv/bin/python -m mypy Python/structural_lib/` (target: 0 errors)
- [ ] Verify documentation completeness:
  - [ ] CHANGELOG.md has all features/fixes for this release
  - [ ] RELEASES.md has release notes draft
  - [ ] README.md reflects current capabilities
- [ ] Verify version bumped in 3 places:
  - [ ] `grep "version" pyproject.toml` → version = "0.X.0"
  - [ ] `grep "VERSION" VBA/Modules/M15_Constants.bas` → VERSION = "0.X.0"
  - [ ] `grep "v0.X.0" docs/*.md | wc -l` → multiple references
- [ ] Run example scripts: `cd Python/examples && .venv/bin/python simple_beam_design.py`

**Success Criteria:**
- ✅ All tests passing
- ✅ 0 quality errors
- ✅ Docs complete
- ✅ Version bumped
- ✅ Examples working

---

### Phase 3: Documentation Cleanup (30 min)
- [ ] Archive pre-release docs: `./scripts/archive_old_sessions.sh`
- [ ] Update version references: `./scripts/check_version_consistency.sh --fix`
- [ ] Validate all links: `.venv/bin/python scripts/check_links.py`
- [ ] Fix any broken links
- [ ] Run final formatting:
  - [ ] `.venv/bin/python -m black Python/`
  - [ ] `.venv/bin/python -m ruff check --fix Python/`
- [ ] Commit cleanup: `git add -A && git commit -m "chore(release): pre-release cleanup"`

**Success Criteria:**
- ✅ Docs archived
- ✅ Versions consistent
- ✅ Links valid
- ✅ Code formatted

---

### Phase 4: Readiness Report (15 min)
- [ ] Create release readiness doc: `docs/planning/RELEASE-READINESS-v0.X.0.md`
- [ ] Include quality gate results:
  - [ ] Tests: PASS / FAIL (count)
  - [ ] Ruff: PASS / FAIL (error count)
  - [ ] Mypy: PASS / FAIL (error count)
  - [ ] Docs: COMPLETE / INCOMPLETE
  - [ ] Version: CONSISTENT / INCONSISTENT
- [ ] List any blockers (critical bugs, incomplete features)
- [ ] Make go/no-go recommendation:
  - [ ] GO: All gates green, no blockers
  - [ ] NO-GO: Gates failed or blockers present
- [ ] Provide reasoning for recommendation
- [ ] Commit report: `git add docs/planning/ && git commit -m "chore(release): v0.X.0 readiness report"`

**Success Criteria:**
- ✅ Report created
- ✅ All gates checked
- ✅ Recommendation clear

**Total Time:** ~1-2 hours

---

## Checklist 3: Monthly Review

**Duration:** 3-4 hours | **Frequency:** First session of each month

### Phase 1: Metrics Analysis (1 hour)
- [ ] Collect 30-day commit metrics:
  - [ ] Total commits: `git log --since="30 days ago" --oneline | wc -l`
  - [ ] Commits by day: `git log --since="30 days ago" --pretty=format:"%ad" --date=short | uniq -c`
  - [ ] Calculate average: total / 30
- [ ] Collect 30-day PR metrics:
  - [ ] PRs merged: `gh pr list --state merged --search "merged:>=$(date -d '30 days ago' +%Y-%m-%d)" --json number | jq length`
  - [ ] PRs open: `gh pr list --state open --json number | jq length`
  - [ ] Calculate average: total / 30
- [ ] Collect code metrics:
  - [ ] Lines changed: `git diff --shortstat HEAD@{30.days.ago}`
  - [ ] Test count: `.venv/bin/python -m pytest --collect-only | grep "test session"`
- [ ] Collect documentation metrics:
  - [ ] Docs created this month: `find docs -name "*.md" -mtime -30 | wc -l`
  - [ ] Total docs: `find docs -name "*.md" | wc -l`
- [ ] Calculate sustainability ratios:
  - [ ] Commits/day = total / 30 (target: 50-75)
  - [ ] PRs/day = total / 30 (target: 1.4-2.1)
  - [ ] Docs/week = (created / 30) * 7 (target: <5)
- [ ] Identify trends:
  - [ ] Is pace increasing or decreasing?
  - [ ] Is debt accumulating or reducing?
  - [ ] Are we staying within targets?

**Success Criteria:**
- ✅ 30-day metrics collected
- ✅ Ratios calculated
- ✅ Trends identified

---

### Phase 2: Archive Organization (1 hour)
- [ ] Create new monthly archive structure:
  ```bash
  mkdir -p docs/archive/$(date +%Y-%m)/{agent-6,agent-8,main-agent,research}
  ```
- [ ] Identify previous month's docs:
  - [ ] In docs/planning/
  - [ ] With date stamps from last month
- [ ] Categorize by agent:
  - [ ] AGENT-6-* → agent-6/
  - [ ] AGENT-8-* → agent-8/
  - [ ] RESEARCH-* → research/
  - [ ] Others → main-agent/
- [ ] Move files to archive:
  - [ ] Use mv or script: `./scripts/archive_old_sessions.sh --force`
- [ ] Create archive index: `docs/archive/$(date +%Y-%m)/README.md`
  - [ ] Table of contents
  - [ ] Brief description of each file
  - [ ] Links to files
- [ ] Verify no broken links: `.venv/bin/python scripts/check_links.py`
- [ ] Create redirect stubs if needed
- [ ] Commit archive: `git add docs/archive/ && git commit -m "chore(docs): archive $(date -d 'last month' +%B %Y)"`

**Success Criteria:**
- ✅ Monthly archive created
- ✅ Files organized by agent
- ✅ Index complete
- ✅ No broken links

---

### Phase 3: Policy Review (1 hour)
- [ ] Review WIP limits effectiveness:
  - [ ] Count limit violations this month (from SESSION_LOG)
  - [ ] Identify patterns (what causes violations?)
  - [ ] Assess if limits are appropriate (too tight/loose?)
- [ ] Review 80/20 ratio:
  - [ ] Count feature sessions from SESSION_LOG
  - [ ] Count governance sessions
  - [ ] Calculate ratio (target: 4:1)
  - [ ] Identify if drifting (too many features?)
- [ ] Review release cadence:
  - [ ] Were releases on time? (check release dates)
  - [ ] Was feature freeze effective? (check commit history during freeze)
  - [ ] Were there quality issues? (check bug reports post-release)
- [ ] Document policy effectiveness:
  - [ ] WIP Limits: EFFECTIVE / TOO TIGHT / TOO LOOSE
  - [ ] 80/20 Ratio: MAINTAINED / DRIFTED (feature-heavy) / DRIFTED (governance-heavy)
  - [ ] Release Cadence: ON TRACK / DELAYED / TOO RUSHED
- [ ] Recommend policy adjustments:
  - [ ] Example: "Increase WIP limit to 3 worktrees (we've been compliant for 3 months)"
  - [ ] Example: "Add governance session (we've done 6 feature sessions in a row)"
  - [ ] Example: "Extend feature freeze to 5 days (last release had bugs)"
- [ ] Create governance review doc: `docs/planning/GOVERNANCE-REVIEW-$(date +%Y-%m).md`
- [ ] Commit review: `git add docs/planning/ && git commit -m "chore(governance): monthly review $(date +%Y-%m)"`

**Success Criteria:**
- ✅ Policy effectiveness assessed
- ✅ Recommendations documented
- ✅ Adjustments committed

---

### Phase 4: Automation Health (1 hour)
- [ ] Test all governance scripts:
  - [ ] `./scripts/archive_old_sessions.sh --dry-run`
  - [ ] `./scripts/check_wip_limits.sh`
  - [ ] `./scripts/check_version_consistency.sh`
  - [ ] `./scripts/generate_health_report.sh --weekly`
- [ ] Check GitHub Actions health:
  - [ ] `gh run list --workflow=git-workflow-tests.yml --limit 10`
  - [ ] Identify any failures
  - [ ] Check error logs: `gh run view <run_id> --log`
- [ ] Review automation logs:
  - [ ] Check for silent failures
  - [ ] Check for unexpected errors
  - [ ] Verify automation is running as scheduled
- [ ] Identify automation gaps:
  - [ ] Are there manual steps we repeat?
  - [ ] Are there checks we forgot to automate?
  - [ ] Are there pain points in current automation?
- [ ] Document improvement opportunities:
  - [ ] New scripts needed
  - [ ] Existing scripts need fixes
  - [ ] Better error messages
  - [ ] Improved logging
- [ ] Implement high-priority improvements:
  - [ ] Create new script if needed
  - [ ] Fix bugs in existing scripts
  - [ ] Add better error handling
- [ ] Update automation docs: `vim agents/agent-9/AUTOMATION.md`
- [ ] Commit automation updates: `git add agents/agent-9/ scripts/ && git commit -m "chore(automation): monthly improvements"`

**Success Criteria:**
- ✅ All scripts tested
- ✅ GitHub Actions verified
- ✅ Gaps identified
- ✅ Improvements implemented

**Total Time:** ~3-4 hours

---

## Checklist 4: Emergency Triage

**Duration:** 1 hour | **Trigger:** Critical sustainability metrics exceeded

### Rapid Assessment (10 min)
- [ ] Check critical limits:
  - [ ] Active docs: `ls docs/planning/*.md | wc -l` (critical: >20)
  - [ ] Open PRs: `gh pr list --state open | wc -l` (critical: >10)
  - [ ] Worktrees: `git worktree list | wc -l` (critical: >3)
  - [ ] Unreleased commits: `git log origin/main..HEAD --oneline | wc -l` (critical: >200)
- [ ] Identify red flags (which limits exceeded?)
- [ ] Assess impact:
  - [ ] HIGH: Blocks new work completely
  - [ ] MEDIUM: Slows down agents significantly
  - [ ] LOW: Organizational debt accumulating

**Prioritization:**
1. Worktrees (HIGH) - blocks new parallel work
2. Open PRs (HIGH) - blocks releases
3. Active docs (MEDIUM) - slows agent onboarding
4. Unreleased commits (LOW) - creates merge conflicts

---

### Rapid Cleanup (40 min)

**Priority 1: Worktree Cleanup (if >3)**
- [ ] List worktrees: `git worktree list`
- [ ] Identify completed work (branches merged?)
- [ ] Remove completed worktrees: `git worktree remove <path>`
- [ ] Target: Get down to 2 worktrees

**Priority 2: PR Cleanup (if >10)**
- [ ] List open PRs: `gh pr list --state open`
- [ ] Categorize:
  - [ ] Ready to merge (CI passed)
  - [ ] Waiting for CI
  - [ ] Blocked (needs fixes)
  - [ ] Stale (no activity >7 days)
- [ ] Merge ready PRs: `gh pr merge <num> --squash --delete-branch`
- [ ] Close stale PRs (after verifying work is obsolete)
- [ ] Target: Get down to <5 PRs

**Priority 3: Docs Cleanup (if >20)**
- [ ] Run aggressive archival: `./scripts/archive_old_sessions.sh`
- [ ] Manually move recent but completeddocs to archive
- [ ] Target: Get down to <10 docs

---

### Verification (10 min)
- [ ] Re-check metrics:
  - [ ] Worktrees: `git worktree list | wc -l` (should be ≤2)
  - [ ] Open PRs: `gh pr list --state open | wc -l` (should be ≤5)
  - [ ] Active docs: `ls docs/planning/*.md | wc -l` (should be <10)
- [ ] All critical limits back to green?
- [ ] Document triage actions: `docs/planning/EMERGENCY-TRIAGE-$(date +%Y-%m-%d).md`
- [ ] Commit: `git add docs/ && git commit -m "chore(governance): emergency triage $(date +%Y-%m-%d)"`

**Success Criteria:**
- ✅ All critical limits resolved
- ✅ Triage documented
- ✅ Changes committed

**Total Time:** ~1 hour

---

## Checklist 5: Quick Health Check

**Duration:** 5 minutes | **Frequency:** Before starting any new work

### WIP Limits Check
- [ ] Worktrees: `git worktree list | wc -l` (max: 2)
- [ ] Open PRs: `gh pr list --state open | wc -l` (max: 5)
- [ ] Active docs: `ls docs/planning/*.md | wc -l` (max: 10)
- [ ] Research tasks: `grep "RESEARCH-" docs/TASKS.md | grep -v "DONE" | wc -l` (max: 3)

### Session Ratio Check
- [ ] Count recent sessions from SESSION_LOG.md
- [ ] Feature sessions since last governance: ___
- [ ] If ≥4: Time for governance session

### Quick Metrics
- [ ] Recent commits: `git log --since="24 hours ago" --oneline | wc -l`
- [ ] If >50/day: Check if pace is sustainable

### Action
- [ ] All limits OK? → Proceed with work
- [ ] Any limit exceeded? → Run cleanup first (Phase relevant checklist)
- [ ] Time for governance? → Schedule governance session

**Total Time:** ~5 minutes

---

## Usage Tips

### How to Use These Checklists

1. **Copy-Paste Method:** Copy the relevant checklist into session notes and check items as you go
2. **Split Screen:** Keep checklist visible while working in terminal
3. **Time Boxing:** Use duration estimates to stay on track
4. **Adaptation:** Skip optional items if time-constrained
5. **Documentation:** Always document deviations from checklist

### Checklist Selection Guide

| Situation | Use This Checklist |
|-----------|-------------------|
| Every 5th session | Weekly Maintenance |
| 3 days before release | Pre-Release |
| 1st session of month | Monthly Review |
| Critical limits exceeded | Emergency Triage |
| Before starting new work | Quick Health Check |

---

## Related Documentation

- **[WORKFLOWS.md](WORKFLOWS.md)** - Detailed workflow procedures
- **[AUTOMATION.md](AUTOMATION.md)** - Script specifications
- **[METRICS.md](METRICS.md)** - Tracking templates
- **[README.md](README.md)** - Main specification

---

**Last Updated:** 2026-01-10 | **Version:** 1.0.0
