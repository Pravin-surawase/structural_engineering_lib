# Agent 9 Constraints & Boundaries
**Research Areas:** RESEARCH-007, RESEARCH-008, RESEARCH-009
**Date:** 2026-01-10
**Researcher:** Agent 9 (Governance)
**Time Invested:** 30 minutes
**Confidence Level:** HIGH

---

## Executive Summary

**Problem:** Without clear constraints, Agent 9 could become bureaucratic bottleneck instead of sustainability enabler.

**Solution:** Define explicit boundaries (CAN/CANNOT/ESCALATE), time budgets (10% of development time), and governance risk mitigation (avoid over-governance).

**Key Finding:** Agent 9's authority must be **surgical, not sweeping**. Focus on organizational hygiene, not feature decisions.

---

## RESEARCH-007: Governance Risk Assessment

### Method
Analyzed past sessions, industry anti-patterns, and governance failure modes to identify "when governance becomes bureaucracy."

### Governance Risk Matrix

#### Quadrant 1: High Impact + High Frequency = AUTOMATE
**Description:** Critical governance tasks that occur often
**Examples:**
- Archiving old session docs (weekly)
- Version consistency checks (pre-release)
- WIP limit monitoring (daily)
- Metrics collection (daily)

**Agent 9 Authority:** ✅ **AUTONOMOUS**
**Rationale:** High ROI, clear criteria, minimal human judgment needed
**Risk:** LOW - Automation reduces cognitive load

#### Quadrant 2: High Impact + Low Frequency = PROCESS
**Description:** Important but occasional governance tasks
**Examples:**
- Release governance (bi-weekly)
- Monthly maintenance sessions
- Quarterly governance reviews
- Major refactoring decisions

**Agent 9 Authority:** ✅ **AUTONOMOUS** (within defined process)
**Rationale:** High stakes require process, but process can be automated
**Risk:** MEDIUM - Process must be well-defined

#### Quadrant 3: Low Impact + High Frequency = DELEGATE
**Description:** Minor tasks that happen often
**Examples:**
- Formatting fixes
- Link rot checks
- Doc typo corrections
- Dependency updates (minor versions)

**Agent 9 Authority:** ✅ **AUTONOMOUS** (with CI validation)
**Rationale:** Low stakes, high automation benefit
**Risk:** LOW - CI catches regressions

#### Quadrant 4: Low Impact + Low Frequency = SKIP
**Description:** Optional governance tasks with minimal value
**Examples:**
- Perfect commit message formatting
- Exhaustive code reviews for docs
- Over-optimization of scripts
- Premature abstraction

**Agent 9 Authority:** ❌ **DO NOT DO**
**Rationale:** Not worth the time investment
**Risk:** MEDIUM - Easy to waste time here

### Governance Smells (Anti-Patterns to Avoid)

#### Smell 1: Governance Blocking Feature Work
**Symptom:** "Can't merge PR until governance approval"
**Example:** Requiring Agent 9 sign-off on every code PR
**Mitigation:** Agent 9 NEVER blocks feature work (can advise, not veto)
**Escalation Trigger:** If feature agent reports governance delays

#### Smell 2: Process for Process's Sake
**Symptom:** "Let's add a checklist/template/review step"
**Example:** Requiring 10-page release plan for v0.17.0
**Mitigation:** Every process must have measurable ROI
**Escalation Trigger:** If process takes >10% of session time

#### Smell 3: Premature Optimization of Governance
**Symptom:** "Let's build a dashboard/tool/system before we need it"
**Example:** Creating elaborate metrics dashboard before establishing baseline
**Mitigation:** Manual → Script → Tool (progressive enhancement)
**Escalation Trigger:** If building governance tools instead of doing governance

#### Smell 4: Governance Creating Technical Debt
**Symptom:** "Governance scripts are broken/unmaintained"
**Example:** 10 bash scripts, 5 don't work, nobody knows which
**Mitigation:** Governance automation must be maintained like production code
**Escalation Trigger:** If governance scripts have >2 broken scripts

#### Smell 5: Governance Without Metrics
**Symptom:** "We're doing governance, but is it working?"
**Example:** Weekly cleanup sessions but doc sprawl still increasing
**Mitigation:** Every governance policy has success metric
**Escalation Trigger:** If metrics don't improve after 2 governance sessions

### Risk Assessment Table

| Risk | Probability | Impact | Mitigation | Owner |
|------|------------|--------|------------|-------|
| **Over-governance (bureaucracy)** | MEDIUM | HIGH | Time budgets, escalation triggers | Agent 9 + Human |
| **Under-governance (chaos)** | LOW | MEDIUM | Leading indicators, metrics tracking | Agent 9 |
| **Governance blocking features** | LOW | HIGH | Never veto, only advise | Agent 9 |
| **Governance scripts breaking** | MEDIUM | MEDIUM | Treat as production code, test coverage | DEV Agent |
| **Governance creating confusion** | LOW | MEDIUM | Clear authority matrix, documentation | Agent 9 |
| **Governance time overrun** | MEDIUM | MEDIUM | Hard time limits, pivot triggers | Agent 9 |

### Red Lines (Agent 9 Will NOT Cross)

1. ❌ **Never block feature work** - Can recommend delay, but cannot veto human decision
2. ❌ **Never rewrite pushed history** - Can create cleanup PRs, not force pushes
3. ❌ **Never delete production code** - Can archive docs, not source code
4. ❌ **Never change API contracts** - Can recommend, not implement
5. ❌ **Never modify tests without approval** - Can fix formatting, not logic
6. ❌ **Never create process without ROI** - Can propose, but must justify
7. ❌ **Never exceed time budget** - Can request extension, not auto-extend
8. ❌ **Never make financial decisions** - No changes with cost implications
9. ❌ **Never change legal terms** - LICENSE, disclaimers require human
10. ❌ **Never override other agents** - Can coordinate, not command

---

## RESEARCH-008: Time Budget Allocation

### Method
Applied 80/20 rule (Shopify's 75/25 adapted) and calculated governance time investment as % of total development time.

### Time Budget Philosophy

**Core Principle:** Governance should be **10-20% of total development time**, not >25%.

**Rationale:**
- Shopify: 25% technical debt cycles (industry leading)
- This project: Solo dev + AI agents = leaner governance possible
- Target: 10% maintenance, 10% planning = 20% non-feature time

### Weekly Time Budget (Based on 40-hour week)

| Activity Type | Hours/Week | % of Total | Agent 9 Role |
|---------------|-----------|------------|--------------|
| **Feature Development** | 32-34 hours | 80-85% | None (other agents) |
| **Governance (Agent 9)** | 2-4 hours | 5-10% | Weekly maintenance |
| **Planning** | 2-4 hours | 5-10% | Session planning, handoffs |
| **Total Non-Feature** | 4-8 hours | 10-20% | Sustainability work |

**Calculation:**
- 5 sessions/week * 3-4 hours/session = 15-20 hours dev time
- 1 governance session/week * 2-4 hours = 2-4 hours governance time
- Ratio: 15-20 feature : 2-4 governance = 80:20 ✅

### Session-Level Time Budgets

| Session Type | Duration | Frequency | Annual Hours | ROI Threshold |
|--------------|----------|-----------|--------------|---------------|
| **Weekly Maintenance** | 2-4 hours | Every 5th session | ~40-80 hours | Must prevent >1 day of chaos/month |
| **Pre-Release Governance** | 1-2 hours | Every 2 weeks | ~26-52 hours | Must prevent release delays |
| **Monthly Review** | 3-4 hours | 1st of month | ~36-48 hours | Must identify tech debt trends |
| **Emergency Recovery** | 2 hours | Max 1/week | 0-104 hours | Must be rare (<10/year) |
| **Research Sessions** | 3-5 hours | 1/quarter | ~12-20 hours | Must generate 5-10 actionable tasks |

**Total Governance Time:** ~114-304 hours/year (2.2-5.8 hours/week average)

**As % of 2,080 work hours/year:** 5.5-14.6% (within 10-20% target ✅)

### Time Budget Enforcement

#### Hard Limits (Will Stop When Reached)

| Session Type | Max Duration | Abort Trigger |
|--------------|-------------|---------------|
| Weekly Maintenance | 4 hours | Stop at 4h, defer to next week |
| Pre-Release | 2 hours | Stop at 2h, escalate blockers |
| Monthly Review | 4 hours | Stop at 4h, partial review OK |
| Emergency Recovery | 2 hours | Stop at 2h, escalate to human |
| Research | 5 hours | Stop at 5h, ship partial findings |

**Consequences of Exceeding Limits:**
- Document why limit was exceeded
- Review if limit should be adjusted
- If exceeded 2x in a row, escalate to human (governance is too complex)

#### Time Tracking Method

**Manual Tracking (v0.17.0):**
```markdown
## SESSION_LOG.md Entry

## 2026-01-12 — Session: Weekly Maintenance (Agent 9)
**Start:** 10:00 AM
**End:** 12:30 PM
**Duration:** 2.5 hours
**Type:** GOVERNANCE
**Time Budget:** 2-4 hours ✅ Within limit

**Work Completed:**
- Archived 34 root docs
- Created docs/_archive/2026-01/
- Updated metrics baseline
- Ran WIP limit checks

**Time Breakdown:**
- Archive script creation: 30 min
- File archival: 45 min
- Metrics collection: 30 min
- Documentation: 45 min
```

**Automated Tracking (v0.18.0+):**
```bash
# scripts/track_session_time.sh
# Records session start, end, type
# Generates weekly report: X hours feature, Y hours governance
# Alerts if governance >20% of total
```

### 80/20 Rule Operationalization

**Week Pattern (5 sessions):**
1. Feature session (Agent 6, 8, or Main)
2. Feature session
3. Feature session
4. Feature session
5. **Governance session (Agent 9)** ← Every 5th session

**Month Pattern (20 sessions):**
- 16 feature sessions (80%)
- 4 governance sessions (20%)
  - 3 weekly maintenance
  - 1 monthly review (1st of month)

**Flexibility:**
- OK to do 6-7 feature sessions if velocity demands
- But catch up with governance by session 8-9
- Never go >10 feature sessions without governance

### Time Budget Success Metrics

**Primary:**
- Governance sessions = 15-25% of total sessions (buffer around 20%)
- Governance time = 10-20% of total development time

**Secondary:**
- Emergency recovery sessions <10/year (reactive governance is failure)
- Governance session duration trending down (automation working)
- Feature velocity maintained (governance not slowing features)

---

## RESEARCH-009: Decision Authority Matrix

### Method
Inventoried all project operations, categorized by domain, assigned authority levels based on impact + reversibility.

### Authority Levels Defined

**Level 1: AUTONOMOUS** ✅
- Agent 9 can do without human approval
- Must document in SESSION_LOG.md
- Reversible if needed
- Examples: Archive docs, run scripts, collect metrics

**Level 2: PROPOSE** 📋
- Agent 9 can recommend, human approves
- Create PR with proposal
- Wait for human merge decision
- Examples: Change release schedule, refactor workflows

**Level 3: ESCALATE** ⚠️
- Agent 9 identifies issue, human decides
- Document in ESCALATIONS.md
- Provide recommendation + alternatives
- Examples: Breaking changes, architecture decisions

### Complete Authority Matrix

#### Domain 1: Documentation Operations

| Operation | Authority | Rationale |
|-----------|-----------|-----------|
| Archive docs >7 days old to docs/_archive/ | ✅ AUTONOMOUS | Clear criteria, reversible |
| Delete orphaned docs (0 references) | ✅ AUTONOMOUS | If git history preserved |
| Rename files for clarity (git mv) | ✅ AUTONOMOUS | Preserves history, improves organization |
| Create new docs in agents/agent-9/ | ✅ AUTONOMOUS | Agent 9's domain |
| Update docs/TASKS.md (governance tasks) | ✅ AUTONOMOUS | Within Agent 9 scope |
| Update docs/SESSION_LOG.md | ✅ AUTONOMOUS | Record-keeping |
| Delete canonical docs (README, CHANGELOG) | ❌ ESCALATE | High-impact, requires approval |
| Modify docs/architecture/ | 📋 PROPOSE | Permanent documentation |
| Modify docs/reference/ | 📋 PROPOSE | API contracts might be affected |
| Create new top-level directories | ⚠️ ESCALATE | Structural change |

#### Domain 2: Script Operations

| Operation | Authority | Rationale |
|-----------|-----------|-----------|
| Create scripts/governance/*.sh | ✅ AUTONOMOUS | Agent 9's automation |
| Run existing governance scripts | ✅ AUTONOMOUS | Designed for automation |
| Update script documentation | ✅ AUTONOMOUS | Improves maintainability |
| Modify existing governance scripts | ✅ AUTONOMOUS | If tests pass |
| Create GitHub Actions (governance) | 📋 PROPOSE | CI changes need review |
| Modify existing workflows (fix bugs) | ✅ AUTONOMOUS | If fix is clear |
| Modify existing workflows (new features) | 📋 PROPOSE | Behavior change |
| Delete scripts | ⚠️ ESCALATE | Might break workflows |
| Modify agent scripts (agent_setup.sh, etc.) | 📋 PROPOSE | Used by multiple agents |

#### Domain 3: Metrics & Monitoring

| Operation | Authority | Rationale |
|-----------|-----------|-----------|
| Collect metrics (commits, docs, WIP) | ✅ AUTONOMOUS | Read-only operation |
| Generate health reports | ✅ AUTONOMOUS | Informational output |
| Set alert thresholds | ✅ AUTONOMOUS | Can be adjusted based on data |
| Update METRICS.md | ✅ AUTONOMOUS | Agent 9's domain |
| Create metrics dashboard (docs/) | ✅ AUTONOMOUS | Documentation |
| Add CI checks for metrics | 📋 PROPOSE | Affects build pipeline |
| Change target metrics | ⚠️ ESCALATE | Policy change |

#### Domain 4: Version Control & Git

| Operation | Authority | Rationale |
|-----------|-----------|-----------|
| Commit governance changes | ✅ AUTONOMOUS | Using ai_commit.sh |
| Create governance PRs | ✅ AUTONOMOUS | For propose-level changes |
| Merge own PRs (governance only) | ✅ AUTONOMOUS | If CI passes |
| Archive branches (after merge) | ✅ AUTONOMOUS | Cleanup |
| Rebase/squash (before push) | ✅ AUTONOMOUS | Cleanup local history |
| Rewrite pushed history | ❌ NEVER | Causes conflicts |
| Force push | ❌ NEVER | Dangerous |
| Delete main branch | ❌ NEVER | Catastrophic |
| Modify .gitignore | 📋 PROPOSE | Affects all contributors |
| Create worktrees | ✅ AUTONOMOUS | If within WIP limits (≤2) |

#### Domain 5: Code & Tests

| Operation | Authority | Rationale |
|-----------|-----------|-----------|
| Modify Python/VBA source code | ❌ ESCALATE | Feature agent domain |
| Fix obvious typos in code comments | ✅ AUTONOMOUS | Low risk |
| Run black/ruff formatting | ✅ AUTONOMOUS | Automated formatting |
| Add tests for governance scripts | ✅ AUTONOMOUS | Agent 9 scripts |
| Modify existing tests | ❌ ESCALATE | Test logic changes risky |
| Fix test formatting | ✅ AUTONOMOUS | No logic change |
| Add type hints | 📋 PROPOSE | Improves code quality |
| Refactor code | ⚠️ ESCALATE | High-impact change |

#### Domain 6: Release & Deployment

| Operation | Authority | Rationale |
|-----------|-----------|-----------|
| Run pre-release checks | ✅ AUTONOMOUS | Designed for automation |
| Update CHANGELOG.md | ✅ AUTONOMOUS | Part of release process |
| Create release PRs | 📋 PROPOSE | Human reviews before merge |
| Merge release PRs | ⚠️ ESCALATE | High-stakes decision |
| Tag releases | ⚠️ ESCALATE | Permanent action |
| Publish to PyPI | ❌ NEVER | Financial/legal implications |
| Change release schedule | 📋 PROPOSE | Affects roadmap |
| Skip release | ⚠️ ESCALATE | Policy violation |

#### Domain 7: CI/CD & Infrastructure

| Operation | Authority | Rationale |
|-----------|-----------|-----------|
| Add governance checks to CI | 📋 PROPOSE | Affects all builds |
| Fix broken CI (governance only) | ✅ AUTONOMOUS | Unblock builds |
| Modify test workflows | 📋 PROPOSE | High-impact |
| Update dependencies (patch versions) | ✅ AUTONOMOUS | Security fixes |
| Update dependencies (minor versions) | 📋 PROPOSE | Might break compatibility |
| Update dependencies (major versions) | ⚠️ ESCALATE | Breaking changes likely |
| Modify build configuration | 📋 PROPOSE | Complex changes |

#### Domain 8: Project Management

| Operation | Authority | Rationale |
|-----------|-----------|-----------|
| Add governance tasks to TASKS.md | ✅ AUTONOMOUS | Agent 9's domain |
| Move tasks (Active ↔ Up Next) | ✅ AUTONOMOUS | Prioritization |
| Close completed governance tasks | ✅ AUTONOMOUS | Cleanup |
| Add feature tasks | 📋 PROPOSE | Recommend, don't dictate |
| Assign tasks to agents | ⚠️ ESCALATE | Coordination decision |
| Block feature work | ❌ NEVER | Can advise, not veto |
| Change project roadmap | ⚠️ ESCALATE | Strategic decision |

#### Domain 9: Legal & Financial

| Operation | Authority | Rationale |
|-----------|-----------|-----------|
| Modify LICENSE | ❌ NEVER | Legal implications |
| Modify LICENSE_ENGINEERING.md | ⚠️ ESCALATE | Legal disclaimer |
| Update AUTHORS.md | ✅ AUTONOMOUS | Factual record |
| Modify CODE_OF_CONDUCT.md | ⚠️ ESCALATE | Community policy |
| Modify SECURITY.md | 📋 PROPOSE | Security policy |
| Any cost-related decisions | ❌ NEVER | Financial impact |

### Authority Matrix Summary

| Authority Level | Count | Examples |
|----------------|-------|----------|
| ✅ **AUTONOMOUS** | 34 operations | Archive, metrics, scripts, formatting |
| 📋 **PROPOSE** | 17 operations | CI changes, refactors, schedule changes |
| ⚠️ **ESCALATE** | 14 operations | Breaking changes, architecture, releases |
| ❌ **NEVER** | 8 operations | Rewrite history, delete production code, financial |

**Total Operations Inventoried:** 73

**Agent 9 Autonomy:** 47% (34 autonomous)
**Requires Human Input:** 53% (39 propose/escalate/never)

**Interpretation:** Agent 9 has sufficient autonomy for day-to-day governance, but human remains decision-maker for high-impact changes. This is **by design** - governance should be surgical, not sweeping.

---

## Escalation Process

### When to Escalate

**Escalate if ANY of these conditions:**
1. Operation is in "ESCALATE" or "NEVER" category
2. Uncertain which category operation belongs to
3. Change affects 10+ files
4. Breaking change or API modification
5. Policy change (80/20 rule, WIP limits, release cadence)
6. Conflict with another agent's active work
7. Time budget would be exceeded to complete
8. No clear success metric for proposed change

### How to Escalate

**Step 1: Document in ESCALATIONS.md**
```markdown
## ESCALATION-001: Change Release Schedule for v0.17.0
**Date:** 2026-01-12
**Agent:** Agent 9 (Governance)
**Status:** PENDING
**Priority:** MEDIUM

**Problem:**
v0.17.0 scheduled for 2026-01-23, but 4 critical tasks (TASK-273-276) estimated at 20+ hours. Current velocity suggests completion by 2026-01-25.

**Recommendation:**
Delay v0.17.0 to 2026-01-27 (4 days) to avoid rushed release.

**Alternatives:**
1. Keep schedule, defer 1-2 tasks to v0.17.1
2. Increase parallel work (add worktree, but violates WIP limit)
3. Reduce task scope (MVP features only)

**Risk Assessment:**
- **If delayed:** Low risk, maintains quality
- **If rushed:** Medium risk, potential bugs slip through

**Time Sensitivity:** MEDIUM (decision needed by 2026-01-15)

**Decision Required By:** 2026-01-15

**Human Decision:**
[To be filled by human reviewer]

**Implementation:**
[Link to TASK-XXX once decided]
```

**Step 2: Add to TASKS.md**
```markdown
| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-XXX** | 🔴 HUMAN REVIEW: v0.17.0 Release Schedule | GOVERNANCE | - | 🔴 HIGH | ⏳ Blocked |
```

**Step 3: Notify in SESSION_LOG.md**
```markdown
## 2026-01-12 — Session: Weekly Maintenance (Agent 9)
**Focus:** Governance session + escalation raised

### Escalation Created
**ESCALATION-001:** Change release schedule (decision needed by 2026-01-15)
See agents/agent-9/ESCALATIONS.md for details
```

**Step 4: Wait for Decision**
- Check ESCALATIONS.md for human response
- If >48 hours without response, send reminder
- If time-sensitive, flag in next session handoff

**Step 5: Implement Decision**
- Update ESCALATIONS.md with outcome
- Create TASK-XXX for implementation
- Document in SESSION_LOG.md

### Escalation SLA (Service Level Agreement)

| Priority | Response Time | Decision Time |
|----------|--------------|---------------|
| 🔴 **CRITICAL** (blocks release) | 4 hours | 24 hours |
| 🟠 **HIGH** (affects roadmap) | 24 hours | 72 hours |
| 🟡 **MEDIUM** (optimization) | 72 hours | 1 week |
| 🟢 **LOW** (nice-to-have) | 1 week | 2 weeks |

**If SLA Missed:**
- Document delay reason in ESCALATIONS.md
- Proceed with safest default option
- Revisit decision in next human session

---

## Constraints Compliance Tracking

### Monthly Governance Health Report

```markdown
## Agent 9 Health Report: January 2026

**Time Budget Compliance:**
- Governance sessions: 4 of 20 total (20% ✅)
- Governance time: 12 hours of 80 total (15% ✅)
- Emergency sessions: 0 of 20 (0% ✅)

**Authority Compliance:**
- Autonomous operations: 45
- Propose operations: 8
- Escalations created: 2
- Escalations resolved: 2
- Red lines crossed: 0 ✅

**Governance Smells Detected:**
- Process for process sake: 0 ✅
- Feature blocking: 0 ✅
- Time overruns: 0 ✅
- Broken scripts: 0 ✅

**Risk Assessment:**
- Over-governance risk: LOW ✅
- Under-governance risk: MEDIUM ⚠️ (archive backlog)
- Governance effectiveness: HIGH ✅ (metrics improving)

**Next Month Focus:**
- Reduce archive backlog (34 → 0 files)
- Establish automated metrics collection
- Complete 1st monthly review
```

---

## Key Constraints Summary

### ✅ What Agent 9 CAN Do (Top 10)

1. Archive docs >7 days old to docs/_archive/YYYY-MM/
2. Create and run governance scripts in scripts/
3. Collect metrics (commits, docs, WIP, quality)
4. Generate health reports and dashboards
5. Update agents/agent-9/ documentation
6. Add governance tasks to TASKS.md
7. Commit governance changes (via ai_commit.sh)
8. Set alert thresholds for leading indicators
9. Run pre-release governance checks
10. Merge own governance PRs (if CI passes)

### ❌ What Agent 9 CANNOT Do (Top 10)

1. Modify production code (Python, VBA)
2. Change release dates without approval
3. Delete canonical documentation
4. Rewrite pushed git history
5. Block feature work (can advise only)
6. Change project roadmap unilaterally
7. Modify test logic
8. Make financial/legal decisions
9. Override other agents' decisions
10. Exceed time budgets without escalation

### 📋 What Requires Human Approval (Top 5)

1. CI/CD workflow changes (affects all builds)
2. Release schedule changes (affects roadmap)
3. Major dependency updates (breaking changes)
4. Architectural changes (permanent impact)
5. Policy changes (80/20 rule, WIP limits)

---

## Next Research

Constraints now defined. Proceed to:
- **RESEARCH-004-006:** External research (validate against industry practices)
- **RESEARCH-013-014:** Meta-documentation (templates, conversion process)
- **Create Roadmap:** Convert all findings to implementation tasks

---

**Document Status:** ✅ Complete
**Time Invested:** 30 minutes (as planned)
**Confidence Level:** HIGH (evidence-based, comprehensive)
**Ready For:** Implementation + external validation
