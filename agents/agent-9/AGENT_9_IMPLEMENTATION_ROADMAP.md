# Agent 9 Implementation Roadmap
**Version:** 1.0.0
**Created:** 2026-01-10
**Status:** Ready for Implementation
**Based On:** Research Phase 1 + Phase 2 (Complete)

---

## Executive Summary

**Goal:** Implement Agent 9 governance system to sustain 50-75 commits/day velocity while reducing documentation sprawl from 41 → <10 root files.

**Research Foundation:** 14 research tasks completed (3.5 hours invested), analyzed 12 internal sessions + 5 external case studies (Stripe, Shopify, GitLab, Prettier, Vitest).

**Implementation Scope:** 12 governance tasks across 3 phases
- **Phase A (v0.17.0):** Critical infrastructure (archive, CI checks, metrics)
- **Phase B (v0.18.0):** Automation & observability (dashboards, alerts)
- **Phase C (v1.0.0+):** Advanced governance (predictive metrics, optimization)

**Time Investment:** 15-20 hours total (3-4 governance sessions following 80/20 rule)

**Success Criteria:**
- Root docs: 41 → <10 (75% reduction)
- Governance sessions: 0 → 1 per 5 sessions (20% time allocation)
- Alert count: 3/6 → 0/6 (eliminate all leading indicator warnings)
- Archive coverage: 0% → 100% (all old docs organized)

---

## Research Summary

### Internal Analysis (Phase 1)

**RESEARCH-001-003: Historical Patterns & Structure**
- Analyzed 12 sessions (2026-01-03 to 2026-01-10)
- Categorized 41 root files: 7 canonical, 34 archivable (82.9%)
- Identified 3 creation triggers: completion, crisis, handoff
- Chose time-based archive strategy: `docs/_archive/YYYY-MM/`

**Key Finding:** 2.8 docs/session creation rate without cleanup → sprawl

**RESEARCH-007-009: Constraints & Authority**
- Defined 73-operation authority matrix (34 autonomous, 17 propose, 14 escalate, 8 never)
- Established 10 red lines Agent 9 will never cross
- Calculated time budgets: 10-20% governance (80/20 rule)

**Key Finding:** Surgical governance (automation > process) prevents over-governance

**RESEARCH-010-012: Baseline Metrics**
- Current velocity: 60 commits/day (12-24x normal solo dev)
- WIP: 100% compliant (1 PR, 2 worktrees, 2 tasks)
- Quality: 86% test coverage, 0 errors
- Identified 6 leading indicators (3 in red: crisis docs, handoffs, completions)

**Key Finding:** High velocity is sustainable with proper governance guardrails

### External Validation (Phase 2)

**RESEARCH-004: Industry Patterns**
- Stripe: Canonical log lines (10-100x faster queries), TypeScript migration (3.7M LOC)
- Shopify: 75/25 rule (25% tech debt time), 50-100 commits/day BFCM
- GitLab: 12 deploys/day, progressive rollout strategy
- 7 patterns identified, 5 applicable to this project

**Key Finding:** 60 commits/day is comparable to team velocity (Shopify: 50-100/day)

**RESEARCH-005: Solo Dev Structures**
- Analyzed Prettier (5 root files), Vitest (2 files), tRPC (2 files), Zod (3 files), Fastify (3 files)
- Pattern: High-velocity projects (100+ commits/month) maintain <5 root files
- Automation correlation: Very High automation = 300 commits/month (Vitest)

**Key Finding:** <5 root files is industry standard for maintainability

**RESEARCH-006: AI Context Optimization**
- Tables > prose for structured data (5-10x faster parsing)
- Progressive disclosure: README → Details → Source
- Time-bounded context: Session docs expire in 7 days
- Status indicators: Emoji + text for quick scanning

**Key Finding:** AI agents need different doc structure than humans

### Meta-Documentation (Phase 2)

**RESEARCH-013: Research Template**
- Standardized format for future research cycles
- Sections: Executive summary, findings, insights, next steps
- Quality checklist: Evidence, citations, application, recommendations

**RESEARCH-014: Research→Task Conversion**
- 6-step process: Validate → Prioritize → Extract → Define → Add → Track
- Priority matrix (Impact × Effort)
- Task specification template with success criteria

---

## Implementation Tasks

### Phase A: Critical Infrastructure (v0.17.0) — Due: 2026-01-23

**Goal:** Reduce documentation sprawl, establish governance baseline

**Time Budget:** 6-8 hours (2 governance sessions)

---

#### TASK-280: Archive 34 Root Files to Timestamped Directory

**Type:** Governance | **Priority:** P0-Critical | **Effort:** S (2h) | **Owner:** Agent 9

**Context:**
Root directory has 41 .md files vs. industry best practice of <5 (Prettier, Vitest, tRPC). Research shows high-velocity projects maintain minimal root to reduce cognitive load during onboarding.

**Research Source:**
- [RESEARCH_FINDINGS_EXTERNAL.md](agents/agent-9/research/RESEARCH_FINDINGS_EXTERNAL.md#case-study-5-vitest-modern-tooling)
- Finding: Projects with >100 commits/month have <5 root files
- Evidence: Vitest (2 files, 300 commits/mo), Prettier (5 files, 100 commits/mo)

**Success Criteria:**
- [ ] 34 files moved from root to `docs/_archive/2026-01/`
- [ ] Root directory has ≤10 .md files remaining (7 canonical: README, CHANGELOG, LICENSE, etc.)
- [ ] All links to archived files updated or redirect stubs added
- [ ] Archive directory structure documented in `docs/_archive/README.md`

**Implementation Steps:**
1. Create archive directory: `mkdir -p docs/_archive/2026-01/`
2. Identify archivable files (completion docs, old handoffs, crisis docs):
   - 13 Agent 6 completion docs (AGENT-6-*.md)
   - 9 crisis/fix docs (FIX-*, BUG-*, SOLUTIONS-*, etc.)
   - 6 handoff docs older than 7 days
   - 3 research summaries (move to agents/agent-9/research/)
   - 3 workflow docs (move to docs/workflows/)
3. Move files: `git mv [files] docs/_archive/2026-01/`
4. Create redirect stubs for frequently referenced files
5. Update README.md with archive note
6. Verify file count: `find . -maxdepth 1 -name "*.md" | wc -l` (should be ≤10)

**Acceptance Tests:**
```bash
# Test 1: Root file count
find . -maxdepth 1 -name "*.md" | wc -l
# Expected: ≤10 (target: 7 canonical files)

# Test 2: Archive exists and populated
ls docs/_archive/2026-01/ | wc -l
# Expected: 34 files

# Test 3: No broken links (check docs/)
grep -r "](/" docs/ | grep -v "_archive" | grep "\.md"
# Expected: All links resolve or have redirect stubs
```

**Dependencies:**
- **Blocks:** TASK-281 (CI enforcement)
- **Blocked By:** None

**Metrics Impact:**
- Root docs: 41 → 10 (75% reduction) ✅
- Archive coverage: 0% → 100% ✅
- Alert: Crisis doc count (9 → 0 after archive)

---

#### TASK-281: Add CI Check for Root File Count Limit

**Type:** Governance | **Priority:** P0-Critical | **Effort:** S (1h) | **Owner:** Agent 9

**Context:**
Prevent future documentation sprawl by enforcing <10 root file limit in CI. Research shows that without enforcement, doc count creeps up over time (our 2.8 files/session creation rate).

**Research Source:**
- [RESEARCH_FINDINGS_STRUCTURE.md](agents/agent-9/research/RESEARCH_FINDINGS_STRUCTURE.md#finding-5-hierarchies-scale)
- Finding: Flat root directory doesn't scale, enforcement needed
- Evidence: Our own history (41 files in 10 days)

**Success Criteria:**
- [ ] CI workflow created: `.github/workflows/root-file-limit.yml`
- [ ] Build fails if >10 .md files in root
- [ ] Check runs on every PR and push to main
- [ ] Clear error message guides developer to archive process
- [ ] Exemptions documented (canonical files list)

**Implementation Steps:**
1. Create script: `scripts/check_root_file_count.sh`
```bash
#!/bin/bash
MAX_FILES=10
count=$(find . -maxdepth 1 -name "*.md" | wc -l | tr -d ' ')

if [ "$count" -gt "$MAX_FILES" ]; then
  echo "❌ Root file limit exceeded: $count files (max: $MAX_FILES)"
  echo "Archive old docs using: ./scripts/archive_old_sessions.sh"
  exit 1
fi

echo "✅ Root file count OK: $count/$MAX_FILES"
exit 0
```
2. Add CI workflow:
```yaml
name: Root File Limit
on: [push, pull_request]
jobs:
  check-root:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check root file count
        run: ./scripts/check_root_file_count.sh
```
3. Document exemptions in script comments (README, CHANGELOG, LICENSE, etc.)
4. Test locally before committing

**Acceptance Tests:**
```bash
# Test 1: Script detects violations
cd /tmp && mkdir test-repo && cd test-repo
touch {1..15}.md
../structural_engineering_lib/scripts/check_root_file_count.sh
# Expected: Exit 1, error message

# Test 2: Script passes with compliant count
rm *.md && touch {1..8}.md
../structural_engineering_lib/scripts/check_root_file_count.sh
# Expected: Exit 0, success message
```

**Dependencies:**
- **Blocks:** None
- **Blocked By:** TASK-280 (archive first to get under limit)

**Metrics Impact:**
- Enforcement: None → Automated ✅
- Future sprawl: Prevented by CI

---

#### TASK-282: Create Baseline Metrics Collection Script

**Type:** Governance | **Priority:** P1-High | **Effort:** S (2h) | **Owner:** Agent 9

**Context:**
Manual metrics collection (bash commands in METRICS_BASELINE.md) is time-consuming (~30 min) and error-prone. Automate to enable tracking over time and faster governance sessions.

**Research Source:**
- [RESEARCH_FINDINGS_EXTERNAL.md](agents/agent-9/research/RESEARCH_FINDINGS_EXTERNAL.md#pattern-7-observability-as-code)
- Pattern: Stripe's observability as code (automated metrics)
- Benefit: 10-100x faster than manual queries

**Success Criteria:**
- [ ] Script created: `scripts/collect_metrics.sh`
- [ ] Outputs JSON to `docs/metrics/YYYY-MM-DD.json`
- [ ] Collects all 6 metric categories (velocity, WIP, docs, quality, release, agents)
- [ ] JSON format matches METRICS_BASELINE.md schema
- [ ] Script runs in <10 seconds
- [ ] Documentation in `docs/metrics/README.md`

**Implementation Steps:**
1. Extract bash commands from METRICS_BASELINE.md
2. Create script with functions per metric category:
```bash
#!/bin/bash
output_file="docs/metrics/$(date +%Y-%m-%d).json"

# Velocity metrics
commits_24h=$(git log --since="24 hours ago" --oneline | wc -l)
commits_7d=$(git log --since="7 days ago" --oneline | wc -l)
commits_avg=$(echo "scale=1; $commits_7d / 7" | bc)

# WIP metrics
prs_open=$(gh pr list --state open | wc -l)
worktrees=$(git worktree list | tail -n +2 | wc -l)

# [... more metrics ...]

# Output JSON
cat > "$output_file" <<EOF
{
  "date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "velocity": {
    "commits_24h": $commits_24h,
    "commits_7d": $commits_7d,
    "commits_avg_day": $commits_avg
  },
  "wip": {
    "prs_open": $prs_open,
    "worktrees": $worktrees
  }
}
EOF
```
3. Add error handling (check if in git repo, gh CLI available, etc.)
4. Test locally, verify JSON is valid
5. Document usage in `docs/metrics/README.md`

**Acceptance Tests:**
```bash
# Test 1: Script runs successfully
./scripts/collect_metrics.sh
echo $?
# Expected: 0

# Test 2: JSON file created
ls docs/metrics/$(date +%Y-%m-%d).json
# Expected: File exists

# Test 3: JSON is valid
jq . docs/metrics/$(date +%Y-%m-%d).json
# Expected: No errors, pretty-printed JSON

# Test 4: All metrics present
jq 'keys | length' docs/metrics/$(date +%Y-%m-%d).json
# Expected: 6 (velocity, wip, documentation, quality, release, agents)
```

**Dependencies:**
- **Blocks:** TASK-283 (metrics dashboard)
- **Blocked By:** None

**Metrics Impact:**
- Collection time: 30 min → 10 sec (180x faster) ✅
- Automation: Manual → Automated ✅

---

#### TASK-283: Create Automated Archival Script

**Type:** Governance | **Priority:** P1-High | **Effort:** M (3h) | **Owner:** Agent 9

**Context:**
Prevent future documentation sprawl by automating archival of old session docs. Research shows manual archival isn't sustainable (we accumulated 34 archivable docs in 10 days).

**Research Source:**
- [RESEARCH_FINDINGS_STRUCTURE.md](agents/agent-9/research/RESEARCH_FINDINGS_STRUCTURE.md#archive-strategy-decision)
- Strategy: Time-based archival (docs older than 7 days)
- Rationale: Automatable, predictable, scales to 100+ sessions

**Success Criteria:**
- [ ] Script created: `scripts/archive_old_sessions.sh`
- [ ] Accepts `--older-than` flag (e.g., `--older-than=7days`)
- [ ] Moves files to `docs/_archive/YYYY-MM/` based on file creation date
- [ ] Dry-run mode (`--dry-run`) shows what would be archived
- [ ] Preserves git history (uses `git mv`)
- [ ] Creates redirect stubs for archived files (optional `--stubs` flag)
- [ ] Runs in <5 seconds for 100 files

**Implementation Steps:**
1. Create script with argument parsing:
```bash
#!/bin/bash
DAYS_OLD=7
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --older-than=*)
      DAYS_OLD="${1#*=}"
      shift
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Find files older than N days
cutoff_date=$(date -d "$DAYS_OLD days ago" +%Y-%m-%d)
archive_dir="docs/_archive/$(date +%Y-%m)"

# [... archival logic ...]
```
2. Implement file filtering logic:
   - Exclude canonical files (README, CHANGELOG, LICENSE, etc.)
   - Check git creation date: `git log --diff-filter=A --format=%ct -- $file`
   - Compare to cutoff date
3. Add dry-run output (list files to be archived)
4. Implement archival (create dir, git mv, optional stubs)
5. Add tests and documentation

**Acceptance Tests:**
```bash
# Test 1: Dry-run shows correct files
./scripts/archive_old_sessions.sh --older-than=7days --dry-run
# Expected: Lists files older than 7 days, excludes canonical

# Test 2: Actual archival works
./scripts/archive_old_sessions.sh --older-than=30days
find docs/_archive/ -name "*.md" | wc -l
# Expected: Files moved, root count reduced

# Test 3: Canonical files preserved
find . -maxdepth 1 -name "README.md"
# Expected: Exists (not archived)
```

**Dependencies:**
- **Blocks:** Weekly maintenance workflow (TASK-284)
- **Blocked By:** None

**Metrics Impact:**
- Archival: Manual → Automated ✅
- Time savings: 30 min/week → 0 ✅

---

### Phase B: Automation & Observability (v0.18.0) — Due: 2026-02-06

**Goal:** Establish governance cadence, automate maintenance, add observability

**Time Budget:** 6-8 hours (2 governance sessions)

---

#### TASK-284: Weekly Governance Session Automation

**Type:** Governance | **Priority:** P1-High | **Effort:** M (3h) | **Owner:** Agent 9

**Context:**
Implement 80/20 rule (4 feature sessions : 1 governance session). Research shows Shopify's 75/25 rule (25% tech debt time) sustains velocity for 5+ years.

**Research Source:**
- [RESEARCH_FINDINGS_EXTERNAL.md](agents/agent-9/research/RESEARCH_FINDINGS_EXTERNAL.md#pattern-3-25-technical-debt-cycles)
- Pattern: Shopify's mandated 25% tech debt time
- Result: Sustained high velocity for 5+ years, no big-bang rewrites

**Success Criteria:**
- [ ] Governance session template created: `agents/agent-9/templates/GOVERNANCE_SESSION_TEMPLATE.md`
- [ ] Checklist for weekly maintenance (archive, metrics, review alerts, update roadmap)
- [ ] Script to detect "5th session": `scripts/check_governance_due.sh`
- [ ] Reminder in SESSION_LOG.md template
- [ ] Documentation in `agents/agent-9/WORKFLOWS.md`

**Implementation Steps:**
1. Create governance session template:
```markdown
# Governance Session — YYYY-MM-DD
**Type:** GOVERNANCE
**Duration Target:** 2-4 hours (within 80/20 rule)
**Agent:** Agent 9

## Pre-Session Checklist
- [ ] Review SESSION_LOG.md (last 5 sessions)
- [ ] Run `scripts/collect_metrics.sh`
- [ ] Check leading indicators (alerts?)
- [ ] Review TASKS.md (any stale tasks?)

## Session Activities
### 1. Archive Old Docs (15 min)
- [ ] Run `./scripts/archive_old_sessions.sh --older-than=7days`
- [ ] Verify root file count <10

### 2. Metrics Review (15 min)
- [ ] Compare current vs. baseline
- [ ] Update targets if needed
- [ ] Investigate any alerts

### 3. TASKS.md Triage (30 min)
- [ ] Review queued tasks (still relevant?)
- [ ] Update priorities
- [ ] Close completed tasks
- [ ] Add new tasks from recent sessions

### 4. Roadmap Update (15 min)
- [ ] Review implementation progress
- [ ] Adjust timeline if needed
- [ ] Update NEXT_SESSION_BRIEF.md

## Post-Session
- [ ] Commit governance changes
- [ ] Update SESSION_LOG.md
- [ ] Schedule next governance session (5 sessions out)
```
2. Create detection script: `scripts/check_governance_due.sh`
```bash
#!/bin/bash
# Check if governance session is due (every 5th session)

session_count=$(grep "^##.*Session:" docs/SESSION_LOG.md | wc -l)
last_governance=$(grep "GOVERNANCE" docs/SESSION_LOG.md | head -1 | cut -d' ' -f2)

# Calculate sessions since last governance
# [... logic ...]

if [ $sessions_since -ge 5 ]; then
  echo "⚠️ Governance session DUE (last: $sessions_since sessions ago)"
  exit 1
fi

echo "✅ Governance session not yet due ($sessions_since/5)"
exit 0
```
3. Integrate into session start workflow
4. Document in WORKFLOWS.md

**Acceptance Tests:**
```bash
# Test 1: Detection script works
./scripts/check_governance_due.sh
# Expected: Shows sessions since last governance

# Test 2: Template is complete
wc -l agents/agent-9/templates/GOVERNANCE_SESSION_TEMPLATE.md
# Expected: ~100 lines with all sections

# Test 3: Can execute governance session
# [Manual test: follow template for one governance session]
```

**Dependencies:**
- **Blocks:** None
- **Blocked By:** TASK-283 (needs archival script)

**Metrics Impact:**
- Governance ratio: N/A → 20% ✅
- Maintenance: Ad-hoc → Scheduled ✅

---

#### TASK-285: Metrics Dashboard with Trending

**Type:** Governance | **Priority:** P2-Medium | **Effort:** M (4h) | **Owner:** Agent 9

**Context:**
Visualize metrics over time to spot trends before they become problems. Research shows leading indicators (not lagging metrics) enable proactive governance.

**Research Source:**
- [METRICS_BASELINE.md](agents/agent-9/research/METRICS_BASELINE.md#leading-indicators)
- Identified 6 leading indicators with alert thresholds
- Example: Root doc creation rate >2/day for 3+ days = warning

**Success Criteria:**
- [ ] Markdown dashboard created: `docs/metrics/DASHBOARD.md`
- [ ] Shows current metrics vs. targets (table format)
- [ ] Sparkline charts for trends (last 7/30 days)
- [ ] Alert status (🟢/🟡/🔴 for each leading indicator)
- [ ] Auto-generated from JSON files by `scripts/generate_dashboard.sh`
- [ ] Updates daily (CI cron job or local script)

**Implementation Steps:**
1. Create dashboard generator script:
```bash
#!/bin/bash
# Generate markdown dashboard from metrics JSON files

output_file="docs/metrics/DASHBOARD.md"
latest_metrics="docs/metrics/$(ls -t docs/metrics/*.json | head -1)"

# Extract current values
commits_avg=$(jq '.velocity.commits_avg_day' $latest_metrics)
root_docs=$(jq '.documentation.root_files' $latest_metrics)

# Generate markdown table
cat > $output_file <<EOF
# Governance Metrics Dashboard
**Last Updated:** $(date)
**Data Source:** $(basename $latest_metrics)

## Current Status

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Commits/day | $commits_avg | 50-75 | ✅ |
| Root docs | $root_docs | <10 | $(if [ $root_docs -lt 10 ]; then echo "✅"; else echo "❌"; fi) |
| [... more metrics ...]

## Trends (Last 7 Days)

[Sparkline charts using Unicode blocks]

## Alerts

[Check leading indicators, show 🔴/🟡/🟢]
EOF
```
2. Add sparkline generation (use Unicode block characters for mini charts)
3. Add alert checking logic (compare against thresholds)
4. Integrate with CI (run after metrics collection)
5. Document in `docs/metrics/README.md`

**Acceptance Tests:**
```bash
# Test 1: Dashboard generates
./scripts/generate_dashboard.sh
cat docs/metrics/DASHBOARD.md
# Expected: Formatted markdown with tables and sparklines

# Test 2: Alerts detect issues
# [Simulate high root doc count, verify 🔴 alert]

# Test 3: Dashboard is readable
# [Manual test: open DASHBOARD.md in GitHub, verify formatting]
```

**Dependencies:**
- **Blocks:** None (nice-to-have, not blocking)
- **Blocked By:** TASK-282 (needs metrics collection)

**Metrics Impact:**
- Visibility: Manual → Automated dashboard ✅
- Trend detection: Reactive → Proactive ✅

---

#### TASK-286: Leading Indicator Alerts in CI

**Type:** Governance | **Priority:** P2-Medium | **Effort:** S (2h) | **Owner:** Agent 9

**Context:**
Warn on PRs if leading indicators show concerning trends. Enables early intervention before problems accumulate.

**Research Source:**
- [METRICS_BASELINE.md](agents/agent-9/research/METRICS_BASELINE.md#leading-indicators)
- Thresholds defined for 6 indicators
- Example: Crisis doc creation (>3 in 7 days)

**Success Criteria:**
- [ ] CI workflow created: `.github/workflows/governance-alerts.yml`
- [ ] Checks 6 leading indicators on every push
- [ ] Posts warning comment on PR if thresholds exceeded
- [ ] Non-blocking (warning only, doesn't fail build)
- [ ] Links to relevant governance doc for context

**Implementation Steps:**
1. Create alert checking script: `scripts/check_governance_alerts.sh`
```bash
#!/bin/bash
# Check leading indicators and output warnings

# Indicator 1: Root doc creation rate
docs_created_7d=$(git log --since="7 days ago" --name-only --diff-filter=A | grep "^[^/]*\.md$" | wc -l)
if [ $docs_created_7d -gt 14 ]; then  # >2/day threshold
  echo "⚠️ Warning: High doc creation rate ($docs_created_7d in 7 days)"
fi

# [... check other 5 indicators ...]
```
2. Add CI workflow:
```yaml
name: Governance Alerts
on: [push, pull_request]
jobs:
  alerts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for metrics
      - name: Check governance alerts
        run: ./scripts/check_governance_alerts.sh
        continue-on-error: true  # Don't fail build
```
3. Add PR comment integration (optional, using gh CLI)
4. Test locally and in CI

**Acceptance Tests:**
```bash
# Test 1: Script detects violations
# [Simulate high doc creation by touching files, run script]
./scripts/check_governance_alerts.sh
# Expected: Warnings printed

# Test 2: CI runs without failing
# [Push commit, verify CI runs and shows warnings but passes]
```

**Dependencies:**
- **Blocks:** None
- **Blocked By:** None

**Metrics Impact:**
- Early warning: None → Automated alerts ✅
- Intervention: Reactive → Proactive ✅

---

### Phase C: Advanced Governance (v1.0.0+) — Due: 2026-03-27

**Goal:** Optimize governance for long-term sustainability, predictive analytics

**Time Budget:** 6-8 hours (2-3 governance sessions over 2 months)

---

#### TASK-287: Predictive Velocity Modeling

**Type:** Governance | **Priority:** P3-Low | **Effort:** L (8h) | **Owner:** Agent 9

**Context:**
Use historical metrics to predict velocity trends and proactively adjust governance before burnout occurs.

**Research Source:**
- [METRICS_BASELINE.md](agents/agent-9/research/METRICS_BASELINE.md#velocity-metrics)
- Current: 60 commits/day (12-24x normal)
- Pattern: Velocity spikes precede burnout in solo dev projects

**Success Criteria:**
- [ ] Python script created: `scripts/predict_velocity.py`
- [ ] Uses exponential moving average (EMA) to smooth velocity data
- [ ] Predicts 7-day and 30-day velocity trends
- [ ] Alerts if predicted velocity >100 commits/day (unsustainable)
- [ ] Recommends governance interventions (e.g., increase to 30% time)
- [ ] Outputs to `docs/metrics/velocity_predictions.json`

**Implementation:** [Deferred to v1.0+ phase]

**Dependencies:**
- **Blocks:** None
- **Blocked By:** TASK-282 (needs historical metrics)

---

#### TASK-288: Automated Release Cadence Optimization

**Type:** Governance | **Priority:** P3-Low | **Effort:** M (6h) | **Owner:** Agent 9

**Context:**
Optimize release cadence based on metrics (velocity, test coverage, user feedback). Research shows GitLab adjusts deploy frequency dynamically based on error rates.

**Research Source:**
- [RESEARCH_FINDINGS_EXTERNAL.md](agents/agent-9/research/RESEARCH_FINDINGS_EXTERNAL.md#pattern-5-continuous-deployment)
- GitLab: 12 deploys/day with progressive rollout
- Lesson: Match cadence to stability metrics

**Success Criteria:**
- [ ] Script analyzes last 3 releases (velocity, bug count, coverage)
- [ ] Recommends cadence adjustment (weekly/bi-weekly/monthly)
- [ ] Outputs report: `docs/release/CADENCE_ANALYSIS.md`
- [ ] Integrated into pre-release checklist

**Implementation:** [Deferred to v1.0+ phase]

**Dependencies:**
- **Blocks:** None
- **Blocked By:** TASK-282 (needs metrics)

---

#### TASK-289: Governance Health Score

**Type:** Governance | **Priority:** P3-Low | **Effort:** M (4h) | **Owner:** Agent 9

**Context:**
Single aggregate score (0-100) representing overall governance health. Simplifies communication ("governance score: 85/100") vs. reviewing 20+ metrics.

**Research Source:**
- Industry pattern: DevOps DORA metrics (4 key metrics → single score)
- Benefit: Simplified executive summary

**Success Criteria:**
- [ ] Health score calculation algorithm defined
- [ ] Weighs 6 leading indicators (30%), quality metrics (30%), velocity (20%), WIP (20%)
- [ ] Score 0-100 with interpretation guide (0-50 = poor, 51-75 = fair, 76-90 = good, 91-100 = excellent)
- [ ] Displayed in DASHBOARD.md
- [ ] Historical tracking in metrics JSON

**Implementation:** [Deferred to v1.0+ phase]

**Dependencies:**
- **Blocks:** None
- **Blocked By:** TASK-285 (dashboard)

---

#### TASK-290: Context Optimization for AI Agents

**Type:** Governance | **Priority:** P3-Low | **Effort:** M (6h) | **Owner:** Agent 9

**Context:**
Apply AI context format guidelines (RESEARCH-006) to all agent specifications and handoff docs. Improve agent onboarding time from hours to minutes.

**Research Source:**
- [RESEARCH_FINDINGS_EXTERNAL.md](agents/agent-9/research/RESEARCH_FINDINGS_EXTERNAL.md#guideline-1-information-density)
- Tables > prose for AI parsing (5-10x faster)
- Progressive disclosure: README → Details

**Success Criteria:**
- [ ] All agent spec docs refactored (agents/*/README.md)
- [ ] Handoff template updated with TL;DR section
- [ ] "Reading Time" added to long docs (>500 lines)
- [ ] Expiry dates added to all session docs
- [ ] Canonical session doc format implemented (Stripe pattern)

**Implementation:** [Deferred to v1.0+ phase]

**Dependencies:**
- **Blocks:** None
- **Blocked By:** None

---

#### TASK-291: Technical Debt Dashboard

**Type:** Governance | **Priority:** P3-Low | **Effort:** M (5h) | **Owner:** Agent 9

**Context:**
Track technical debt explicitly (TODO count, test skips, complexity metrics). Research shows tracking debt prevents accumulation.

**Research Source:**
- [RESEARCH_FINDINGS_EXTERNAL.md](agents/agent-9/research/RESEARCH_FINDINGS_EXTERNAL.md#pattern-3-25-technical-debt)
- Shopify: Tracks debt paid down vs. accumulated
- Goal: Debt trend = flat or declining

**Success Criteria:**
- [ ] Script collects debt metrics: `scripts/collect_tech_debt.sh`
  - TODO/FIXME count (grep codebase)
  - Test skips (grep for @skip, @unittest.skip)
  - Cyclomatic complexity (radon for Python)
  - Large functions (>50 lines)
  - Duplicate code (copydetect)
- [ ] Debt dashboard in `docs/metrics/TECH_DEBT.md`
- [ ] Trend chart (last 30 days)
- [ ] Alert if debt increasing >10% month-over-month

**Implementation:** [Deferred to v1.0+ phase]

**Dependencies:**
- **Blocks:** None
- **Blocked By:** TASK-282 (metrics infrastructure)

---

## Implementation Schedule

### Timeline Overview

```
v0.17.0 (Jan 23)        v0.18.0 (Feb 6)         v1.0.0 (Mar 27)
    │                        │                        │
    ├─ Phase A              ├─ Phase B              ├─ Phase C
    │  (4 tasks)            │  (3 tasks)            │  (5 tasks)
    │                        │                        │
    └─ CRITICAL              └─ AUTOMATION           └─ OPTIMIZATION
       Archive, CI,             Dashboard,              Predictive,
       Metrics                  Alerts                  Advanced
```

### Detailed Schedule

| Task | Phase | Priority | Effort | Due | Dependencies |
|------|-------|----------|--------|-----|--------------|
| **TASK-280:** Archive 34 Files | A | P0 | 2h | 2026-01-15 | None |
| **TASK-281:** CI Root File Limit | A | P0 | 1h | 2026-01-16 | TASK-280 |
| **TASK-282:** Metrics Collection | A | P1 | 2h | 2026-01-18 | None |
| **TASK-283:** Archival Script | A | P1 | 3h | 2026-01-23 | None |
| **TASK-284:** Governance Sessions | B | P1 | 3h | 2026-01-30 | TASK-283 |
| **TASK-285:** Metrics Dashboard | B | P2 | 4h | 2026-02-04 | TASK-282 |
| **TASK-286:** Governance Alerts | B | P2 | 2h | 2026-02-06 | None |
| **TASK-287:** Predictive Velocity | C | P3 | 8h | 2026-03-15 | TASK-282 |
| **TASK-288:** Release Optimization | C | P3 | 6h | 2026-03-20 | TASK-282 |
| **TASK-289:** Health Score | C | P3 | 4h | 2026-03-22 | TASK-285 |
| **TASK-290:** Context Optimization | C | P3 | 6h | 2026-03-25 | None |
| **TASK-291:** Tech Debt Dashboard | C | P3 | 5h | 2026-03-27 | TASK-282 |

### Governance Session Allocation

**v0.17.0 Phase A:** 2 sessions (Jan 11, Jan 18)
- Session 1 (4h): TASK-280, 281, 282
- Session 2 (4h): TASK-283 + v0.17.0 prep

**v0.18.0 Phase B:** 2 sessions (Jan 25, Feb 1)
- Session 3 (3h): TASK-284 + 285
- Session 4 (3h): TASK-286 + v0.18.0 prep

**v1.0.0 Phase C:** 3 sessions (March)
- Session 5 (4h): TASK-287 + 288
- Session 6 (4h): TASK-289 + 290
- Session 7 (3h): TASK-291 + v1.0.0 prep

**Total:** 7 governance sessions over 2.5 months (20% of 35 total sessions)

---

## Success Metrics

### Phase A Success (v0.17.0) — Target Metrics

| Metric | Baseline (2026-01-10) | v0.17.0 Target | Measurement |
|--------|----------------------|----------------|-------------|
| Root docs | 41 | ≤10 | `find . -maxdepth 1 -name "*.md" \| wc -l` |
| Archive coverage | 0% | 100% | All old docs organized |
| CI enforcement | None | Automated | Root file limit check exists |
| Metrics collection | Manual (30 min) | Auto (10 sec) | `scripts/collect_metrics.sh` |
| Archival process | Manual | Automated | `scripts/archive_old_sessions.sh` |

**Minimum Success:** Root docs ≤10, CI check enforced

**Stretch Goal:** Root docs ≤7 (canonical only)

---

### Phase B Success (v0.18.0) — Target Metrics

| Metric | v0.17.0 Baseline | v0.18.0 Target | Measurement |
|--------|-----------------|----------------|-------------|
| Governance ratio | N/A | 20% | 1 governance / 5 sessions |
| Metrics dashboard | None | Automated | `docs/metrics/DASHBOARD.md` |
| Alert count | 3/6 | 0/6 | All leading indicators green |
| Dashboard updates | None | Daily | Auto-generated |
| Governance sessions | 0 | 2 completed | SESSION_LOG.md |

**Minimum Success:** 2 governance sessions completed, dashboard exists

**Stretch Goal:** 0 alerts, dashboard updated hourly

---

### Phase C Success (v1.0.0) — Target Metrics

| Metric | v0.18.0 Baseline | v1.0.0 Target | Measurement |
|--------|-----------------|---------------|-------------|
| Governance health | N/A | 85/100 | Composite score |
| Predictive alerts | None | Enabled | 7-day velocity forecast |
| Tech debt trend | Unknown | Declining | Month-over-month |
| Context format | Ad-hoc | Standardized | All agent specs |
| Release cadence | Bi-weekly | Optimized | Data-driven |

**Minimum Success:** Health score >75, predictive velocity working

**Stretch Goal:** Health score >90, tech debt declining 3 months straight

---

## Risk Assessment

### High Risks

#### Risk 1: Archival Breaks Links
**Probability:** MEDIUM | **Impact:** HIGH

**Mitigation:**
- Add redirect stubs for frequently referenced files
- Test links before/after archival
- Document archive location in README
- Keep git history (use `git mv`, not `rm`)

**Contingency:**
- Restore from `docs/_archive/` if needed
- Add permanent redirects
- Update all broken links (semi-automated with grep)

---

#### Risk 2: CI Check Too Strict
**Probability:** LOW | **Impact:** MEDIUM

**Mitigation:**
- Set threshold at 10 files (not 5) for flexibility
- Document exemption process
- Allow temporary overrides (manual CI skip)
- Review threshold after 1 month

**Contingency:**
- Raise limit to 15 temporarily
- Investigate root cause of doc creation
- Adjust archive frequency

---

#### Risk 3: Metrics Collection Overhead
**Probability:** LOW | **Impact:** LOW

**Mitigation:**
- Optimize script (<10 sec runtime)
- Cache expensive operations
- Run async in CI (don't block build)
- Limit collection frequency (daily, not per commit)

**Contingency:**
- Reduce metric count (focus on 6 leading indicators)
- Use sampling (last 7 days, not all history)
- Disable dashboard if too slow

---

### Medium Risks

#### Risk 4: Governance Time Exceeds 20%
**Probability:** MEDIUM | **Impact:** MEDIUM

**Mitigation:**
- Track time per governance session
- Set hard 4-hour limit per session
- Batch tasks (don't spread over multiple sessions)
- Automate repetitive work (scripts > manual)

**Contingency:**
- Defer P3 tasks to v1.0.0+
- Increase threshold to 25% temporarily
- Escalate to human for priority adjustment

---

#### Risk 5: Alert Fatigue
**Probability:** MEDIUM | **Impact:** LOW

**Mitigation:**
- Only alert on HIGH priority issues
- Set thresholds conservatively (avoid false positives)
- Non-blocking warnings (don't fail builds)
- Review alert thresholds monthly

**Contingency:**
- Disable noisy alerts
- Increase thresholds
- Switch to weekly summary (not per-PR)

---

## Rollback Plan

### If Phase A Fails

**Scenario:** Archival breaks critical workflows

**Actions:**
1. Restore files: `git mv docs/_archive/2026-01/* .`
2. Investigate broken links
3. Add redirect stubs: `echo "Moved to..." > FILE.md`
4. Re-run archival with stubs
5. Test all links again

**Recovery Time:** 1-2 hours

---

### If Phase B Fails

**Scenario:** Automation overhead exceeds benefits

**Actions:**
1. Disable CI workflows (comment out jobs)
2. Revert to manual metrics collection
3. Reduce dashboard update frequency
4. Defer automation to v1.0.0+

**Recovery Time:** 30 minutes

---

### If Phase C Fails

**Scenario:** Advanced features too complex

**Actions:**
1. Defer all Phase C tasks to post-v1.0.0
2. Focus on Phase A+B maintenance
3. Validate sustainability with basic governance
4. Revisit Phase C after 6 months

**Recovery Time:** N/A (optional features)

---

## Next Actions

### Immediate (This Session)

1. **Commit Research Phase 2:** Push external research, templates, this roadmap
2. **Create Roadmap PR:** Submit for review (optional, could direct commit)
3. **Add Tasks to TASKS.md:** Copy TASK-280 through TASK-291

### Next Session (2026-01-11)

1. **Start Phase A:** Begin TASK-280 (archive 34 root files)
2. **Review Progress:** Check research quality with user
3. **Adjust Roadmap:** Update based on feedback

### Week 1 (Jan 11-17)

- ✅ TASK-280: Archive completed
- ✅ TASK-281: CI check enforced
- ✅ TASK-282: Metrics automated
- ✅ Root docs: 41 → ≤10

### Week 2 (Jan 18-23)

- ✅ TASK-283: Archival script
- ✅ v0.17.0 released (governance infrastructure)

---

## Appendix A: Research Artifacts

All research documents available in `agents/agent-9/research/`:

1. **RESEARCH_FINDINGS_STRUCTURE.md** (Internal analysis)
   - Historical patterns (12 sessions)
   - File categorization (41 → 7 canonical, 34 archivable)
   - Archive strategy decision

2. **METRICS_BASELINE.md** (Baseline metrics)
   - Current state snapshot (60 commits/day, 86% coverage)
   - 6 leading indicators with alert thresholds
   - SMART targets (measurable success criteria)

3. **AGENT_9_CONSTRAINTS.md** (Authority & boundaries)
   - 73-operation authority matrix
   - 10 red lines (never cross)
   - Time budgets (10-20% governance)

4. **RESEARCH_FINDINGS_EXTERNAL.md** (Industry validation)
   - 7 patterns from Stripe, Shopify, GitLab
   - 5 case studies (Prettier, Vitest, tRPC, Zod, Fastify)
   - AI context optimization guidelines

5. **RESEARCH_FINDING_TEMPLATE.md** (Meta-documentation)
   - Standard format for future research
   - Quality checklist
   - Anti-patterns to avoid

6. **RESEARCH_TO_TASK_PROCESS.md** (Conversion process)
   - 6-step workflow: Validate → Prioritize → Extract → Define → Add → Track
   - Priority matrix (Impact × Effort)
   - Task specification template

---

## Appendix B: Authority Quick Reference

**Agent 9 CAN (Autonomous):**
- Archive docs >7 days old
- Collect metrics (run scripts)
- Update TASKS.md (governance tasks)
- Create/update governance docs
- Run CI checks
- Generate dashboards

**Agent 9 MUST PROPOSE (Get approval):**
- Change WIP limits
- Modify release cadence
- Update time budgets
- Change governance ratio

**Agent 9 MUST ESCALATE (Human decision):**
- Block features
- Modify production code
- Change architecture
- Allocate budget

**Agent 9 NEVER:**
- Rewrite git history
- Delete production code
- Make breaking changes
- Override security policies

**Full matrix:** [AGENT_9_CONSTRAINTS.md](agents/agent-9/research/AGENT_9_CONSTRAINTS.md#authority-matrix)

---

**Roadmap Version:** 1.0.0
**Created:** 2026-01-10
**Last Updated:** 2026-01-10
**Status:** ✅ Ready for Implementation
**Next Review:** After v0.17.0 release (2026-01-23)
