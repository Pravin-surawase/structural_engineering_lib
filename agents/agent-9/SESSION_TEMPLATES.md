# Agent 9: Session Planning Templates

**Purpose:** Pre-filled templates for planning governance sessions
**Usage:** Copy template → Fill in details → Use as session guide
**Last Updated:** 2026-01-10

---

## Table of Contents

1. [Weekly Maintenance Session Template](#template-1-weekly-maintenance-session)
2. [Pre-Release Session Template](#template-2-pre-release-session)
3. [Monthly Review Session Template](#template-3-monthly-review-session)
4. [Emergency Triage Session Template](#template-4-emergency-triage-session)

---

## Template 1: Weekly Maintenance Session

**Copy this to:** `docs/planning/GOVERNANCE-SESSION-YYYY-MM-DD.md`

```markdown
# Governance Session: Weekly Maintenance
**Date:** YYYY-MM-DD
**Agent:** Agent 9 (Governance & Sustainability)
**Type:** Weekly Maintenance
**Duration:** 2-4 hours
**Session Number:** X of 5 this cycle

---

## Pre-Session Checklist

- [ ] Read [CHECKLISTS.md](../../agents/agent-9/CHECKLISTS.md) (Weekly Maintenance)
- [ ] Review last week's metrics from GOVERNANCE-METRICS.md
- [ ] Check SESSION_LOG.md for session count (should be 5th session)
- [ ] Verify all required scripts exist in scripts/

---

## Phase 1: Documentation Cleanup (45 min)

### Actions
- [ ] Run archive script dry-run: `./scripts/archive_old_sessions.sh --dry-run`
- [ ] Review files to be archived (verify nothing critical)
- [ ] Execute archival: `./scripts/archive_old_sessions.sh`
- [ ] Verify archive structure: `ls -R docs/archive/`
- [ ] Check archive index: `cat docs/archive/$(date +%Y-%m)/README.md`
- [ ] Count active docs: `ls docs/planning/*.md | wc -l`

### Results
- Files archived: XX
- Active docs remaining: XX (target: <10)
- Archive index: ✅ Updated / ❌ Needs update

### Issues Encountered
[None / Describe any issues]

---

## Phase 2: Worktree & Branch Cleanup (30 min)

### Actions
- [ ] List worktrees: `git worktree list`
- [ ] Identify completed worktrees
- [ ] Remove completed: `git worktree remove <path>`
- [ ] List remote branches: `git branch -r | grep -v "HEAD\|main"`
- [ ] Delete merged branches: [command]
- [ ] Prune remote refs: `git remote prune origin && git fetch --prune`

### Results
- Worktrees removed: X
- Branches deleted: X
- Current worktrees: X/2

### Issues Encountered
[None / Describe any issues]

---

## Phase 3: Version Consistency (30 min)

### Actions
- [ ] Run version checker: `./scripts/check_version_consistency.sh`
- [ ] Review mismatches (if any)
- [ ] Auto-fix: `./scripts/check_version_consistency.sh --fix`
- [ ] Verify fix: Re-run checker

### Results
- Mismatches found: X
- Mismatches fixed: X
- Current version: vX.X.X
- All references consistent: ✅ / ❌

### Issues Encountered
[None / Describe any issues]

---

## Phase 4: Link Validation (15 min)

### Actions
- [ ] Run link checker: `.venv/bin/python scripts/check_links.py`
- [ ] Review broken links
- [ ] Fix broken links (update sources or create redirect stubs)
- [ ] Re-run checker

### Results
- Broken links found: X
- Links fixed: X
- All links valid: ✅ / ❌

### Issues Encountered
[None / Describe any issues]

---

## Phase 5: Metrics Collection (30 min)

### Actions
- [ ] Generate health report: `./scripts/generate_health_report.sh --weekly`
- [ ] Collect manual metrics (see commands in CHECKLISTS.md)
- [ ] Update GOVERNANCE-METRICS.md

### Results

**Sustainability:**
- Commits/day (7d avg): XX (target: 50-75) ✅/⚠️/❌
- Active docs: XX (target: <10) ✅/⚠️/❌
- F:G ratio: X:X (target: 4:1) ✅/⚠️/❌
- WIP compliance: XX% (target: 100%) ✅/⚠️/❌

**Velocity:**
- PRs merged: XX (target: 10-15) ✅/⚠️/❌
- Test count: XXXX
- Ruff errors: X (target: 0) ✅/⚠️/❌
- Mypy errors: X (target: 0) ✅/⚠️/❌

**Health:**
- Worktrees: X/2 ✅/⚠️/❌
- Open PRs: X/5 ✅/⚠️/❌
- Research tasks: X/3 ✅/⚠️/❌

### Trends
- Commits/day: [↗️ up / → stable / ↘️ down] (was XX, now XX)
- Active docs: [↗️ up / → stable / ↘️ down] (was XX, now XX)
- WIP compliance: [↗️ improving / → stable / ↘️ declining]

---

## Phase 6: Governance Adjustments (30 min)

### Risk Assessment
- [ ] Is commits/day sustainable? (50-75 target)
- [ ] Are WIP limits being violated?
- [ ] Is documentation sprawling?
- [ ] Is 80/20 ratio maintained?

### Identified Risks
[List any risks identified]

### Recommendations
1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]

### Policy Updates
- [ ] No changes needed
- [ ] Updated: [Describe changes]

---

## Session Summary

**Duration:** X hours XX minutes
**Overall Status:** 🟢 Healthy / 🟡 Warning / 🔴 Critical

**Completed:**
- ✅ Documentation archived (XX files)
- ✅ Worktrees cleaned (X removed)
- ✅ Version consistency verified
- ✅ Links validated
- ✅ Metrics collected and updated
- ✅ Risks assessed

**Next Actions:**
- Next governance session: YYYY-MM-DD (estimated)
- Policy adjustments: [None / See recommendations]
- Follow-up items: [List if any]

---

## Commit Message

```bash
git add agents/agent-9/ docs/planning/ docs/archive/
git commit -m "chore(governance): weekly maintenance $(date +%Y-%m-%d)

- Archived XX session docs
- Cleaned X worktrees, deleted X branches
- Updated version references
- Validated XX links
- Collected weekly metrics
- All sustainability metrics: ✅/⚠️/❌
"
```

---

**Session Completed:** YYYY-MM-DD HH:MM
**Next Governance Session:** YYYY-MM-DD (Week 5 of next cycle)
```

---

## Template 2: Pre-Release Session

**Copy this to:** `docs/planning/RELEASE-PREP-v0.X.0.md`

```markdown
# Release Preparation: v0.X.0
**Release Date:** YYYY-MM-DD
**Feature Freeze:** YYYY-MM-DD (3 days before)
**Session Date:** YYYY-MM-DD
**Agent:** Agent 9 (Governance & Sustainability)

---

## Pre-Session Checklist

- [ ] Read [CHECKLISTS.md](../../agents/agent-9/CHECKLISTS.md) (Pre-Release)
- [ ] Verify release schedule (bi-weekly cadence)
- [ ] Check feature freeze announcement in next-session-brief.md

---

## Phase 1: Feature Freeze Announcement (15 min)

### Actions
- [ ] Calculate release date (2 weeks from last release)
- [ ] Update next-session-brief.md with freeze announcement
- [ ] Add freeze policy (bugs ✅, features ❌, breaking ❌)
- [ ] Update TASKS.md with [RELEASE-BLOCKER] labels
- [ ] Commit announcement

### Results
- Release date: YYYY-MM-DD
- Freeze start: YYYY-MM-DD
- Freeze announced: ✅ / ❌
- Blockers identified: X

---

## Phase 2: Quality Gates (30 min)

### Test Suite
- [ ] Run full tests: `cd Python && .venv/bin/pytest -q`
- **Result:** XXXX tests passed, X failed
- **Status:** ✅ Pass / ❌ Fail

### Code Quality
- [ ] Ruff: `.venv/bin/python -m ruff check Python/`
- **Result:** X errors
- **Status:** ✅ Pass (0 errors) / ❌ Fail

- [ ] Mypy: `.venv/bin/python -m mypy Python/structural_lib/`
- **Result:** X errors
- **Status:** ✅ Pass (0 errors) / ❌ Fail

### Documentation
- [ ] CHANGELOG.md has all features/fixes
- **Status:** ✅ Complete / ❌ Incomplete

- [ ] RELEASES.md has release notes draft
- **Status:** ✅ Complete / ❌ Incomplete

- [ ] README.md reflects current capabilities
- **Status:** ✅ Up to date / ❌ Outdated

### Version Verification
- [ ] pyproject.toml: version = "0.X.0"
- [ ] VBA VERSION: "0.X.0"
- [ ] docs/ references: "v0.X.0"
- **Status:** ✅ Consistent / ❌ Inconsistent

### Examples
- [ ] Run example: `cd Python/examples && .venv/bin/python simple_beam_design.py`
- **Status:** ✅ Works / ❌ Fails

---

## Phase 3: Documentation Cleanup (30 min)

### Actions
- [ ] Archive pre-release docs: `./scripts/archive_old_sessions.sh`
- [ ] Update version references: `./scripts/check_version_consistency.sh --fix`
- [ ] Validate links: `.venv/bin/python scripts/check_links.py`
- [ ] Fix broken links
- [ ] Run formatting: `black Python/ && ruff check --fix Python/`
- [ ] Commit cleanup

### Results
- Docs archived: XX
- Version refs updated: XX
- Links fixed: X
- Code formatted: ✅ / ❌

---

## Phase 4: Release Readiness Report (15 min)

### Quality Gate Summary

| Gate | Status | Details |
|------|--------|---------|
| Tests | ✅/❌ | XXXX passing, X failing |
| Ruff | ✅/❌ | X errors |
| Mypy | ✅/❌ | X errors |
| Docs | ✅/❌ | CHANGELOG/RELEASES complete |
| Version | ✅/❌ | Consistent across 3 locations |
| Examples | ✅/❌ | Working / Not tested |

### Blockers

[List any release-blocking issues]

1. [Blocker 1]
2. [Blocker 2]

**Blocker Count:** X

---

### Go/No-Go Decision

**Recommendation:** 🟢 GO / 🔴 NO-GO

**Reasoning:**
[Explain decision based on quality gates and blockers]

**Conditions for GO:**
- All tests passing
- 0 ruff/mypy errors
- Docs complete
- Version consistent
- No critical blockers

**If NO-GO:**
- [ ] List required fixes
- [ ] Estimate fix time
- [ ] Recommend new release date

---

## Session Summary

**Duration:** X hours XX minutes

**Release Status:** 🟢 Ready / 🟡 Needs Work / 🔴 Not Ready

**Completed:**
- ✅ Feature freeze announced
- ✅ Quality gates checked
- ✅ Documentation cleaned up
- ✅ Readiness report generated
- ✅ Go/no-go decision made

**Next Actions:**
- [ ] [If GO] Tag release on YYYY-MM-DD
- [ ] [If NO-GO] Fix blockers, re-assess
- [ ] Announce decision to stakeholders

---

## Commit Message

```bash
git add docs/planning/
git commit -m "chore(release): v0.X.0 readiness report

Quality Gates:
- Tests: [✅/❌]
- Code Quality: [✅/❌]
- Documentation: [✅/❌]

Decision: [GO/NO-GO]
Blockers: X
"
```

---

**Session Completed:** YYYY-MM-DD HH:MM
**Release Date:** YYYY-MM-DD (if GO)
```

---

## Template 3: Monthly Review Session

**Copy this to:** `docs/planning/GOVERNANCE-REVIEW-YYYY-MM.md`

```markdown
# Monthly Governance Review: MMMM YYYY
**Date:** YYYY-MM-DD
**Agent:** Agent 9 (Governance & Sustainability)
**Period:** YYYY-MM-01 to YYYY-MM-DD
**Duration:** 3-4 hours

---

## Pre-Session Checklist

- [ ] Read [CHECKLISTS.md](../../agents/agent-9/CHECKLISTS.md) (Monthly Review)
- [ ] Review last month's governance review (if exists)
- [ ] Collect baseline data from 30 days ago

---

## Phase 1: Metrics Analysis (1 hour)

### 30-Day Commit Metrics

**Total Commits:**
```bash
git log --since="30 days ago" --oneline | wc -l
# Result: XXX commits
```

**Commits/Day Average:** XXX / 30 = XX.X
**Target:** 50-75
**Status:** ✅/⚠️/❌

**Peak Day:** XXX commits on YYYY-MM-DD
**Target:** <100
**Status:** ✅/⚠️/❌

---

### 30-Day PR Metrics

**PRs Merged:**
```bash
gh pr list --state merged --search "merged:>=$(date -d '30 days ago' +%Y-%m-%d)" --json number | jq length
# Result: XX PRs
```

**PRs/Day Average:** XX / 30 = X.X
**Target:** 1.4-2.1 (42-63 per month)
**Status:** ✅/⚠️/❌

**Average Merge Time:** XX hours
**Target:** <24 hours
**Status:** ✅/⚠️/❌

---

### 30-Day Code Metrics

**Lines Changed:**
```bash
git diff --shortstat HEAD@{30.days.ago}
# Result: XXX insertions(+), XXX deletions(-)
```

**Net Change:** ±XX,XXX lines

**Test Count Growth:**
- Start of month: XXXX tests
- End of month: XXXX tests
- Growth: +XXX tests
- **Target:** +200-400
- **Status:** ✅/⚠️/❌

---

### 30-Day Documentation Metrics

**Docs Created:** XX
**Target:** <20
**Status:** ✅/⚠️/❌

**Docs Archived:** XX

**Active Docs (current):** XX
**Target:** <10
**Status:** ✅/⚠️/❌

---

### Session Metrics

**Total Sessions:** XX

**Feature Sessions:** XX
**Governance Sessions:** XX
**Ratio:** X:X
**Target:** 4:1 (80:20)
**Status:** ✅/⚠️/❌

---

### WIP Compliance

**Violations This Month:**
- Worktree limit (≤2): X violations
- PR limit (≤5): X violations
- Docs limit (≤10): X violations
- Research limit (≤3): X violations

**Compliance Rate:** XX%
**Target:** 100%
**Status:** ✅/⚠️/❌

---

### Trend Analysis

**Compared to Last Month:**

| Metric | This Month | Last Month | Change | Trend |
|--------|------------|------------|--------|-------|
| Commits/Day | XX | XX | ±XX% | ↗️/→/↘️ |
| PRs Merged | XX | XX | ±XX% | ↗️/→/↘️ |
| Active Docs | XX | XX | ±XX | ↗️/→/↘️ |
| Test Count | XXXX | XXXX | +XXX | ↗️/→/↘️ |
| WIP Compliance | XX% | XX% | ±XX% | ↗️/→/↘️ |

**Key Observations:**
[What patterns emerged? What changed significantly?]

---

## Phase 2: Archive Organization (1 hour)

### Actions
- [ ] Create monthly archive: `mkdir -p docs/archive/$(date +%Y-%m)/{agent-6,agent-8,main-agent,research}`
- [ ] Move previous month's docs from docs/planning/
- [ ] Update archive index: `docs/archive/$(date +%Y-%m)/README.md`
- [ ] Verify no broken links: `.venv/bin/python scripts/check_links.py`

### Results
- Archive created: docs/archive/YYYY-MM/
- Files moved: XX
- Index created: ✅ / ❌
- Broken links: X found, X fixed

---

## Phase 3: Policy Review (1 hour)

### WIP Limits Effectiveness

**Evidence:**
- Violations: X times this month
- Average compliance: XX%
- Common violation: [worktrees / PRs / docs / research]

**Assessment:** 🟢 Effective / 🟡 Partially Effective / 🔴 Ineffective

**Recommendation:**
- [ ] Keep current limits (working well)
- [ ] Tighten limits: [which and why]
- [ ] Loosen limits: [which and why]

---

### 80/20 Ratio Effectiveness

**Evidence:**
- Feature sessions: XX
- Governance sessions: XX
- Ratio: X:X (target: 4:1)

**Assessment:** 🟢 Maintained / 🟡 Drifted / 🔴 Ignored

**Recommendation:**
- [ ] Maintain current pattern
- [ ] Add governance session (too feature-heavy)
- [ ] Extend governance sessions (need more time)

---

### Release Cadence Effectiveness

**Evidence:**
- Releases this month: X
- On-time releases: X/X
- Feature freeze effectiveness: [good / needs improvement]
- Post-release bugs: X

**Assessment:** 🟢 On Track / 🟡 Delayed / 🔴 Off Track

**Recommendation:**
- [ ] Maintain bi-weekly cadence
- [ ] Extend to 3 weeks
- [ ] Extend feature freeze to 5 days

---

### Documentation Lifecycle Effectiveness

**Evidence:**
- Docs archived: XX
- Archive organization: [clean / messy]
- Link breakage: [rare / common]
- Agent onboarding time: [<15 min / >15 min]

**Assessment:** 🟢 Working / 🟡 Needs Adjustment / 🔴 Broken

**Recommendation:**
- [ ] Current process working
- [ ] Archive more aggressively (7 days → 5 days)
- [ ] Improve indexing
- [ ] Better redirect stubs

---

## Phase 4: Automation Health (1 hour)

### Script Testing

- [ ] Test archive script: `./scripts/archive_old_sessions.sh --dry-run`
- [ ] Test WIP limits: `./scripts/check_wip_limits.sh`
- [ ] Test version check: `./scripts/check_version_consistency.sh`
- [ ] Test health report: `./scripts/generate_health_report.sh --weekly`

### Results

| Script | Status | Issues |
|--------|--------|--------|
| archive_old_sessions.sh | ✅/❌ | [None / Describe] |
| check_wip_limits.sh | ✅/❌ | [None / Describe] |
| check_version_consistency.sh | ✅/❌ | [None / Describe] |
| generate_health_report.sh | ✅/❌ | [None / Describe] |

---

### GitHub Actions Review

```bash
gh run list --workflow=git-workflow-tests.yml --limit 10
```

**Success Rate:** XX%
**Recent Failures:** X
**Status:** ✅/⚠️/❌

---

### Automation Gaps

**Identified Gaps:**
1. [Gap 1]
2. [Gap 2]

**Proposed Solutions:**
1. [Solution 1]
2. [Solution 2]

---

### Improvements Implemented

- [ ] [Improvement 1]
- [ ] [Improvement 2]

---

## Session Summary

**Duration:** X hours XX minutes

**Overall Health:** 🟢 Healthy / 🟡 Warning / 🔴 Critical

**Key Findings:**
1. [Finding 1]
2. [Finding 2]
3. [Finding 3]

**Recommendations:**

**High Priority:**
1. [Recommendation 1]
2. [Recommendation 2]

**Medium Priority:**
1. [Recommendation 1]

**Low Priority:**
1. [Recommendation 1]

---

## Action Items

**For Next Week:**
- [ ] [Action 1]
- [ ] [Action 2]

**For Next Month:**
- [ ] [Action 1]
- [ ] [Action 2]

---

## Commit Message

```bash
git add agents/agent-9/ docs/planning/ docs/archive/
git commit -m "chore(governance): monthly review $(date +%Y-%m)

Metrics Summary:
- Commits/day: XX (target: 50-75)
- F:G ratio: X:X (target: 4:1)
- WIP compliance: XX%

Policy Assessment:
- WIP Limits: [Effective/Needs Adjustment]
- 80/20 Ratio: [Maintained/Drifted]
- Release Cadence: [On Track/Delayed]

Recommendations: See GOVERNANCE-REVIEW-$(date +%Y-%m).md
"
```

---

**Session Completed:** YYYY-MM-DD HH:MM
**Next Monthly Review:** YYYY-MM-DD (First session of next month)
```

---

## Template 4: Emergency Triage Session

**Copy this to:** `docs/planning/EMERGENCY-TRIAGE-YYYY-MM-DD.md`

```markdown
# Emergency Governance Triage
**Date:** YYYY-MM-DD
**Agent:** Agent 9 (Governance & Sustainability)
**Trigger:** [Critical limits exceeded / Sustainability crisis]
**Duration:** 1 hour

---

## Rapid Assessment (10 min)

### Critical Limits Check

**Active Docs:**
```bash
ls docs/planning/*.md | wc -l
# Result: XX
```
**Status:** XX/10 - 🟢 OK / 🟡 Warning (>10) / 🔴 Critical (>20)

**Open PRs:**
```bash
gh pr list --state open | wc -l
# Result: XX
```
**Status:** XX/5 - 🟢 OK / 🟡 Warning (>5) / 🔴 Critical (>10)

**Worktrees:**
```bash
git worktree list | wc -l
# Result: X
```
**Status:** X/2 - 🟢 OK / 🟡 Warning (>2) / 🔴 Critical (>3)

**Unreleased Commits:**
```bash
git log origin/main..HEAD --oneline | wc -l
# Result: XXX
```
**Status:** XXX - 🟢 OK (<100) / 🟡 Warning (100-200) / 🔴 Critical (>200)

---

### Prioritization

**Red Flags (Immediate Action):**
- [ ] [Flag 1]
- [ ] [Flag 2]

**Priority Order:**
1. [Highest impact item]
2. [Second highest]
3. [Third highest]

---

## Rapid Cleanup (40 min)

### Priority 1: [Item Name] (15 min)

**Actions:**
- [ ] [Action 1]
- [ ] [Action 2]

**Commands:**
```bash
[Commands executed]
```

**Results:**
- [Result 1]
- [Result 2]

**Status:** ✅ Resolved / ⚠️ Partially Resolved / ❌ Not Resolved

---

### Priority 2: [Item Name] (15 min)

**Actions:**
- [ ] [Action 1]
- [ ] [Action 2]

**Commands:**
```bash
[Commands executed]
```

**Results:**
- [Result 1]
- [Result 2]

**Status:** ✅ Resolved / ⚠️ Partially Resolved / ❌ Not Resolved

---

### Priority 3: [Item Name] (10 min)

**Actions:**
- [ ] [Action 1]
- [ ] [Action 2]

**Commands:**
```bash
[Commands executed]
```

**Results:**
- [Result 1]
- [Result 2]

**Status:** ✅ Resolved / ⚠️ Partially Resolved / ❌ Not Resolved

---

## Verification (10 min)

### Re-Check Metrics

- [ ] Active docs: `ls docs/planning/*.md | wc -l` → Result: XX (target: <10)
- [ ] Open PRs: `gh pr list --state open | wc -l` → Result: XX (target: <5)
- [ ] Worktrees: `git worktree list | wc -l` → Result: X (target: ≤2)

**All Limits Green?** ✅ / ❌

---

### Root Cause Analysis

**Why Did This Happen?**
[Identify root cause]

**Prevention:**
[How to prevent recurrence]

---

## Session Summary

**Duration:** XX minutes

**Initial State:**
- Active docs: XX (🔴 Critical)
- Open PRs: XX (🔴 Critical)
- Worktrees: X (🟡 Warning)

**Final State:**
- Active docs: XX (✅ OK)
- Open PRs: XX (✅ OK)
- Worktrees: X (✅ OK)

**Actions Taken:**
1. [Action 1]
2. [Action 2]
3. [Action 3]

**Outcome:** 🟢 Crisis Resolved / 🟡 Partially Resolved / 🔴 Still Critical

---

## Follow-Up Actions

**Immediate (Today):**
- [ ] [Action 1]

**Short-Term (This Week):**
- [ ] [Action 1]
- [ ] [Action 2]

**Long-Term (Policy Changes):**
- [ ] [Action 1]

---

## Commit Message

```bash
git add docs/planning/ docs/archive/
git commit -m "chore(governance): emergency triage $(date +%Y-%m-%d)

Crisis: [Brief description]

Actions Taken:
- [Action 1]
- [Action 2]

Outcome: [Resolved / Partially Resolved]
Follow-up: See EMERGENCY-TRIAGE-$(date +%Y-%m-%d).md
"
```

---

**Session Completed:** YYYY-MM-DD HH:MM
**Status:** 🟢 Resolved / 🟡 Monitoring / 🔴 Requires Additional Action
```

---

## Usage Guidelines

### When to Use Templates

| Template | Use When |
|----------|----------|
| Weekly Maintenance | Every 5th session (80/20 cycle) |
| Pre-Release | 3 days before scheduled release |
| Monthly Review | First session of each month |
| Emergency Triage | Critical limits exceeded |

### Template Customization

**DO Customize:**
- Specific actions for your situation
- Commands based on your environment
- Metrics relevant to your project
- Timings based on actual duration

**DON'T Remove:**
- Phase structure (ensures completeness)
- Verification steps (quality gates)
- Commit message templates (maintain history)
- Cross-references to other docs

---

## Related Documentation

- **[README.md](README.md)** - Main specification
- **[WORKFLOWS.md](WORKFLOWS.md)** - Detailed procedures
- **[CHECKLISTS.md](CHECKLISTS.md)** - Copy-paste checklists
- **[METRICS.md](METRICS.md)** - Tracking templates

---

**Last Updated:** 2026-01-10 | **Version:** 1.0.0
