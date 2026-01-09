# Research → Task Conversion Process
**Purpose:** Document how research findings become actionable tasks
**Version:** 1.0
**Created:** 2026-01-10
**Maintained By:** Agent 9 (Governance)

---

## Process Overview

```
Research Finding
    ↓
Validate & Prioritize
    ↓
Extract Insight
    ↓
Define Task
    ↓
Add to TASKS.md
    ↓
Track Progress
```

---

## Step 1: Validate Findings

### Validation Checklist

Before converting research to tasks, verify:

- [ ] **Evidence-based:** Finding backed by data, citations, or examples
- [ ] **Applicable:** Relevant to our specific context (solo dev + AI agents)
- [ ] **Actionable:** Can be translated to concrete implementation steps
- [ ] **Measurable:** Success criteria can be defined
- [ ] **Non-redundant:** Not already in TASKS.md or implemented

### Confidence Thresholds

Only convert findings with:
- **HIGH confidence** (multiple sources, validated)
- **MEDIUM confidence** + user approval

Skip:
- **LOW confidence** (single source, unvalidated)

### Example Validation

❌ **Don't Convert (LOW confidence):**
```markdown
**Finding:** Some projects use monorepos
**Problem:** Too vague, not validated, unclear applicability
```

✅ **Convert (HIGH confidence):**
```markdown
**Finding:** High-velocity projects (Vitest: 300 commits/month, tRPC: 200/month)
maintain <5 files in root directory

**Evidence:** 5 projects analyzed (150k+ combined stars, 3-8 year track record)

**Application:** This project has 41 root files, 8x over best practice
```

---

## Step 2: Prioritize Findings

### Priority Matrix

| Impact | Effort | Priority | Action |
|--------|--------|----------|--------|
| HIGH | LOW | **P0 - Critical** | Implement immediately |
| HIGH | MEDIUM | **P1 - High** | Implement this release |
| HIGH | HIGH | **P2 - Medium** | Plan for next release |
| MEDIUM | LOW | **P1 - High** | Quick wins |
| MEDIUM | MEDIUM | **P2 - Medium** | Backlog |
| MEDIUM | HIGH | **P3 - Low** | Defer or decline |
| LOW | ANY | **P4 - Backlog** | Revisit quarterly |

### Impact Assessment

**HIGH Impact:**
- Blocks current work
- Affects sustainability (burnout risk)
- Causes frequent errors/rework
- Impacts external users (breaking changes)

**MEDIUM Impact:**
- Improves efficiency (saves 30+ min/week)
- Reduces technical debt
- Enhances developer experience
- Prevents future problems

**LOW Impact:**
- Nice-to-have
- Minor convenience
- Aesthetic improvements

### Effort Estimation

**LOW Effort:** <2 hours (1 session)
- Script creation
- Documentation updates
- Configuration changes

**MEDIUM Effort:** 2-8 hours (1-2 sessions)
- Feature implementation
- Test suite additions
- Process changes

**HIGH Effort:** 8+ hours (2+ sessions)
- Major refactoring
- New subsystems
- Breaking changes

### Example Prioritization

**Finding:** 41 root files (target: <10)
- **Impact:** HIGH (onboarding delays, cognitive overload)
- **Effort:** LOW (script + manual archival, 1-2 hours)
- **Priority:** **P0 - Critical**

**Finding:** Add metrics dashboard
- **Impact:** MEDIUM (improved visibility)
- **Effort:** MEDIUM (data collection + visualization, 4-6 hours)
- **Priority:** **P2 - Medium**

---

## Step 3: Extract Insights

### Insight Template

For each research finding, extract:

```markdown
## [Insight Name]

**What We Learned:** [Research finding in 1 sentence]

**Why It Matters:** [Impact on project/team/users]

**Current State:** [How we do things now - specific metrics]

**Gap:** [What's missing or broken - quantified]

**Recommendation:** [Specific action to take - who/what/when]
```

### Example Insight Extraction

**From Research:**
```markdown
### Finding 1: Root Directory Discipline

**Source:** Prettier (5 files), Zod (3 files), Vitest (2 files)

**Evidence:** High-velocity projects maintain <5 root files
```

**Extracted Insight:**
```markdown
## Root Directory Discipline

**What We Learned:** High-velocity projects maintain <5 files in root
(Prettier/Zod/Vitest: 2-5 files, 100-300 commits/month)

**Why It Matters:** Reduces cognitive load during agent onboarding (5 files
vs. 41 = 8x faster scan)

**Current State:** 41 root files (34 archivable completion/crisis docs)

**Gap:** No archival process, docs accumulate indefinitely (2.8 files/session
creation rate)

**Recommendation:** Archive 34 files to docs/_archive/2026-01/ by v0.17.0
(Due: 2026-01-23)
```

---

## Step 4: Define Tasks

### Task Specification Template

```markdown
## TASK-XXX: [Task Title] (v0.X.0)

**Type:** [Governance | Feature | Bugfix | Refactor | Documentation]
**Priority:** [P0-Critical | P1-High | P2-Medium | P3-Low]
**Effort:** [S (≤2h) | M (2-8h) | L (8-24h) | XL (24+h)]
**Owner:** [Agent Name | Human]
**Due:** YYYY-MM-DD
**Status:** [Queued | Active | Blocked | Complete]

### Context

[1-2 sentences: Why are we doing this? What problem does it solve?]

**Research Source:** [Link to research findings document]
- Finding: [Specific finding that led to this task]
- Evidence: [Key metric or citation]

### Success Criteria

- [ ] Criterion 1 (measurable)
- [ ] Criterion 2 (testable)
- [ ] Criterion 3 (observable)

### Implementation Steps

1. Step 1 (specific action)
2. Step 2 (specific action)
3. Step 3 (specific action)

### Acceptance Tests

```bash
# Test 1: [What to verify]
command_to_test

# Expected output:
expected_result
```

### Dependencies

- **Blocks:** [Tasks that depend on this]
- **Blocked By:** [Tasks this depends on]
- **Related:** [Related tasks]

### Rollback Plan

[What to do if this goes wrong]
```

### Example Task Definition

```markdown
## TASK-280: Archive 34 Root Files to Timestamped Directory (v0.17.0)

**Type:** Governance
**Priority:** P0-Critical
**Effort:** S (≤2h)
**Owner:** Agent 9 (Governance)
**Due:** 2026-01-15
**Status:** Queued

### Context

Root directory has 41 .md files vs. best practice of <5 (8x over threshold).
Research shows high-velocity projects (Prettier, Vitest, tRPC) maintain
minimal root to reduce cognitive load during onboarding.

**Research Source:** [RESEARCH_FINDINGS_EXTERNAL.md](agents/agent-9/research/RESEARCH_FINDINGS_EXTERNAL.md#case-study-5-vitest-modern-tooling)
- Finding: Projects with >100 commits/month have <5 root files
- Evidence: Vitest (2 files, 300 commits/mo), Prettier (5 files, 100 commits/mo)

### Success Criteria

- [ ] 34 files moved from root to `docs/_archive/2026-01/`
- [ ] Root directory has ≤10 .md files remaining
- [ ] All links to archived files updated (or redirect stubs added)
- [ ] CI check added to fail if >10 root files

### Implementation Steps

1. Create archive directory: `mkdir -p docs/_archive/2026-01/`
2. Run archival script: `./scripts/archive_old_sessions.sh --older-than=7days`
3. Verify files moved: `find . -maxdepth 1 -name "*.md" | wc -l` (should be ≤10)
4. Add CI check: `.github/workflows/root-file-limit.yml`
5. Update root README.md with archive note

### Acceptance Tests

```bash
# Test 1: Root file count
find . -maxdepth 1 -name "*.md" | wc -l
# Expected: ≤10

# Test 2: Archive exists
ls docs/_archive/2026-01/ | wc -l
# Expected: 34

# Test 3: CI check works
./scripts/check_root_file_count.sh
# Expected: PASS (exit 0)
```

### Dependencies

- **Blocks:** TASK-281 (CI enforcement of root file limit)
- **Blocked By:** None
- **Related:** TASK-282 (Automated weekly archival)

### Rollback Plan

If links break after archival:
1. Restore files: `git mv docs/_archive/2026-01/* .`
2. Investigate broken links
3. Add redirect stubs: `echo "Moved to docs/_archive/..." > OLD_FILE.md`
4. Re-run archival with stubs in place
```

---

## Step 5: Add to TASKS.md

### TASKS.md Format

```markdown
## TASK-XXX: [Title] (vX.Y.Z)
**Type:** [Type] | **Priority:** [Priority] | **Effort:** [Effort] | **Owner:** [Owner]
**Status:** [Status] | **Due:** YYYY-MM-DD

[1-2 sentence description]

**Success Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

**Research Source:** [Link to research doc]

**Dependencies:** [List if any]
```

### Placement Rules

1. **Active Tasks** (top of TASKS.md)
   - Currently being worked on
   - Max 5 tasks (WIP limit)
   - Sorted by priority (P0 → P1 → P2)

2. **Queued for Current Release** (e.g., v0.17.0 section)
   - Assigned to upcoming release
   - Sorted by priority, then dependencies
   - All dependencies resolved or scheduled

3. **Backlog** (Future Releases section)
   - Not yet assigned to release
   - Sorted by priority
   - Reviewed monthly

### Example TASKS.md Entry

```markdown
## TASK-280: Archive 34 Root Files (v0.17.0)
**Type:** Governance | **Priority:** P0-Critical | **Effort:** S (≤2h) | **Owner:** Agent 9
**Status:** Queued | **Due:** 2026-01-15

Archive old session docs to reduce root directory clutter. Research shows
high-velocity projects maintain <5 root files (we have 41).

**Success Criteria:**
- [ ] 34 files archived to `docs/_archive/2026-01/`
- [ ] Root ≤10 .md files
- [ ] CI check enforces limit

**Research Source:** [RESEARCH_FINDINGS_EXTERNAL.md](agents/agent-9/research/RESEARCH_FINDINGS_EXTERNAL.md#case-study-5-vitest-modern-tooling)

**Dependencies:** None
```

---

## Step 6: Track Progress

### Progress Tracking Methods

#### Method 1: TASKS.md Status Field
```markdown
**Status:** Queued → Active → Complete
```

#### Method 2: Session Log Entries
```markdown
## 2026-01-15 — Session: Agent 9 Governance [GOVERNANCE]
- ✅ TASK-280: Archived 34 root files to docs/_archive/2026-01/
- ⏳ TASK-281: CI check implementation (50% complete)
```

#### Method 3: Commit Messages
```bash
git commit -m "governance: archive 34 root files (TASK-280)"
```

#### Method 4: Metrics Tracking
Track in `agents/agent-9/research/METRICS_BASELINE.md`:
```markdown
| Metric | Baseline (2026-01-10) | Current | Target | Status |
|--------|----------------------|---------|--------|--------|
| Root files | 41 | 10 | <10 | ✅ |
```

---

## Decision Flow Diagram

```
┌─────────────────────┐
│ Research Finding    │
└──────────┬──────────┘
           │
           ▼
    ┌─────────────┐
    │ Validated?  │
    └──────┬──────┘
           │
      Yes  │  No → ❌ Discard
           ▼
    ┌─────────────┐
    │ Prioritize  │
    └──────┬──────┘
           │
           ├─ P0 → Immediate
           ├─ P1 → This Release
           ├─ P2 → Next Release
           └─ P3+ → Backlog
           │
           ▼
    ┌─────────────┐
    │ Define Task │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │ Add TASKS.md│
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │ Implement   │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │ Track & Log │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │ Update      │
    │ Metrics     │
    └─────────────┘
```

---

## Examples: Full Conversion Flow

### Example 1: Archive Root Files

#### Research Finding
```markdown
**Finding:** High-velocity projects (Vitest, Prettier, tRPC) maintain
<5 files in root

**Evidence:**
- Vitest: 2 root files, 300 commits/month
- Prettier: 5 root files, 100 commits/month
- tRPC: 2 root files, 200 commits/month

**Application:** This project has 41 root files (8x over threshold)
```

#### Validation
- ✅ Evidence-based (5 projects, combined 150k+ stars)
- ✅ Applicable (affects agent onboarding)
- ✅ Actionable (files can be moved)
- ✅ Measurable (file count)
- ✅ Non-redundant (not in TASKS.md yet)
- ✅ Confidence: HIGH (multiple sources, industry standard)

#### Prioritization
- **Impact:** HIGH (onboarding delays, cognitive overload, sustainability risk)
- **Effort:** LOW (script + manual work, 1-2 hours)
- **Priority:** **P0 - Critical**

#### Extracted Insight
```markdown
## Root Directory Discipline

**What We Learned:** Industry standard is <5 root files for maintainability

**Why It Matters:** 41 files = 8x cognitive load during agent onboarding

**Current State:** 41 root .md files (34 archivable completion docs)

**Gap:** No archival process, 2.8 files/session creation rate

**Recommendation:** Archive to docs/_archive/2026-01/ by v0.17.0
```

#### Defined Task
```markdown
## TASK-280: Archive 34 Root Files to Timestamped Directory (v0.17.0)

**Type:** Governance | **Priority:** P0-Critical | **Effort:** S (≤2h) | **Owner:** Agent 9
**Status:** Queued | **Due:** 2026-01-15

Archive old session docs to reduce root directory clutter from 41 → ≤10 files.

**Success Criteria:**
- [ ] 34 files archived to `docs/_archive/2026-01/`
- [ ] Root ≤10 .md files remaining
- [ ] CI check enforces <10 limit

**Implementation:**
1. `mkdir -p docs/_archive/2026-01/`
2. `./scripts/archive_old_sessions.sh --older-than=7days`
3. Add CI check

**Research Source:** RESEARCH_FINDINGS_EXTERNAL.md (Case Study 5: Vitest)
```

#### Added to TASKS.md
Placed in **v0.17.0 Queued** section, sorted by P0 priority

#### Tracked
- Commit: `governance: archive 34 root files (TASK-280)`
- Session log: `✅ TASK-280: Archived 34 root files`
- Metrics: Root files 41 → 10 (✅ target met)

---

### Example 2: Add Metrics Dashboard

#### Research Finding
```markdown
**Finding:** Stripe uses canonical log lines for observability (10-100x
faster queries)

**Application:** Manual metrics collection (git log, grep) is slow and
error-prone
```

#### Validation
- ✅ Evidence-based (Stripe blog, 15M LOC codebase)
- ✅ Applicable (we collect metrics manually)
- ✅ Actionable (can create dashboard)
- ✅ Measurable (time saved)
- ❓ Non-redundant (check TASKS.md... not found)
- ✅ Confidence: HIGH (industry leader, proven pattern)

#### Prioritization
- **Impact:** MEDIUM (saves 30 min/week, improves visibility)
- **Effort:** MEDIUM (dashboard + data collection, 4-6 hours)
- **Priority:** **P2 - Medium** (nice-to-have, not blocking)

#### Extracted Insight
```markdown
## Automated Metrics Collection

**What We Learned:** Observability as code reduces manual work (Stripe pattern)

**Why It Matters:** Manual metrics collection takes 30 min/week, error-prone

**Current State:** Bash commands in METRICS_BASELINE.md (manual copy-paste)

**Gap:** No automation, no visualization, no trending

**Recommendation:** Create `scripts/collect_metrics.sh` + dashboard by v0.18.0
```

#### Defined Task
```markdown
## TASK-282: Automated Metrics Collection Script (v0.18.0)

**Type:** Governance | **Priority:** P2-Medium | **Effort:** M (2-8h) | **Owner:** Agent 9
**Status:** Backlog | **Due:** 2026-02-06

Create script to automatically collect governance metrics (velocity, WIP, docs).

**Success Criteria:**
- [ ] `scripts/collect_metrics.sh` created
- [ ] Outputs JSON to `docs/metrics/current.json`
- [ ] Dashboard displays trends (last 7/30 days)
- [ ] CI runs script on push (track over time)

**Implementation:**
1. Extract bash commands from METRICS_BASELINE.md
2. Create script with JSON output
3. Add markdown dashboard generator
4. Add CI workflow to collect + commit metrics

**Research Source:** RESEARCH_FINDINGS_EXTERNAL.md (Pattern 7: Observability)
```

#### Added to TASKS.md
Placed in **v0.18.0 Backlog** section (lower priority, future release)

---

## Quality Checklist

Before adding task to TASKS.md:

- [ ] Finding is validated (HIGH or MEDIUM confidence)
- [ ] Priority assigned using matrix (P0/P1/P2/P3)
- [ ] Impact and effort assessed
- [ ] Success criteria are measurable
- [ ] Implementation steps are specific
- [ ] Dependencies identified (blocks/blocked-by)
- [ ] Research source linked
- [ ] Due date set (realistic, aligned with release)
- [ ] Owner assigned (Agent or Human)
- [ ] Rollback plan considered (for risky changes)

---

## Anti-Patterns

### ❌ Anti-Pattern 1: Vague Tasks
```markdown
## TASK-XXX: Improve Documentation

Fix docs.
```

**Problems:**
- No specific action
- No success criteria
- No measurable outcome
- No owner or due date

### ✅ Correct:
```markdown
## TASK-XXX: Archive 34 Root Files (v0.17.0)

**Type:** Governance | **Priority:** P0 | **Effort:** S | **Owner:** Agent 9
**Due:** 2026-01-15

Archive old session docs to docs/_archive/2026-01/.

**Success Criteria:**
- [ ] Root directory has ≤10 .md files
- [ ] 34 files in docs/_archive/2026-01/
- [ ] CI check enforces limit
```

---

### ❌ Anti-Pattern 2: Jumping to Implementation
```markdown
We should use TypeScript!

[Creates TASK-XXX: Migrate to TypeScript]
```

**Problems:**
- No research validation
- No context (why?)
- No alternative considered
- No effort estimation

### ✅ Correct:
```markdown
**Research:** Stripe migrated 3.7M LOC to TypeScript for type safety

**Validation:** Our Python codebase already uses mypy (0 errors), achieving
similar benefits

**Decision:** No migration needed, existing approach sufficient

[No task created]
```

---

### ❌ Anti-Pattern 3: Everything is P0
```markdown
TASK-280: P0 - Archive files
TASK-281: P0 - Add dashboard
TASK-282: P0 - Update README
TASK-283: P0 - Fix typo
```

**Problems:**
- Priority inflation
- No real prioritization
- Everything "urgent" = nothing urgent

### ✅ Correct:
```markdown
TASK-280: P0 - Archive files (blocks onboarding)
TASK-281: P2 - Add dashboard (nice-to-have)
TASK-282: P3 - Update README (minor improvement)
TASK-283: P4 - Fix typo (cosmetic)
```

---

## Workflow Summary

**For Each Research Finding:**

1. **Validate:** Is this HIGH confidence and applicable?
2. **Prioritize:** Use matrix (Impact × Effort → Priority)
3. **Extract:** What we learned, why it matters, what to do
4. **Define:** Specific task with success criteria
5. **Add:** Place in TASKS.md (appropriate section)
6. **Track:** Monitor progress in session logs + metrics

**Time Budget:** 5-10 minutes per task (research → TASKS.md)

**Quality Bar:** Every task must have:
- Measurable success criteria
- Research source link
- Clear owner + due date
- Specific implementation steps

---

**Process Version:** 1.0
**Created:** 2026-01-10
**Last Updated:** 2026-01-10
**Next Review:** After first 10 tasks implemented (validate process effectiveness)
