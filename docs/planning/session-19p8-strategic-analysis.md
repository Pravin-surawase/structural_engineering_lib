# Session 19P8 Phase 2: Strategic Analysis & 5+ Commit Plan

**Type:** Strategic Planning
**Audience:** Implementation Agents
**Status:** Approved
**Importance:** Critical
**Version:** 1.0.0
**Created:** 2026-01-12
**Last Updated:** 2026-01-12
**Related Tasks:** IMPL-008 (Hook Clarity), Session 19 Overall

---

## Executive Summary

**Objective:** Complete a professional 5+ commit session that establishes permanent prevention systems for automation sprawl and session documentation staleness.

**Key Challenge:** P8 Phase 1 implemented hook clarity (PR #348), but user review found:
1. Session docs stale (referring to P8 that just completed)
2. P8 plan doc referenced in logs but not in repo
3. Manual git examples still in non-archive docs (education vs. caution)
4. Automation sprawl: 103+ scripts, unclear deprecation status, too many entrypoints
5. Agent mistakes report doesn't parse hook output logs

**Strategic Approach:** Fix root causes (not patches) with permanent prevention systems:
- Establish doc lifecycle rules (freshness, archival)
- Create automation governance system (central registry, deprecation policy)
- Build prevention infrastructure (validators, watchers, guardrails)
- Document "why" for future agents (decision rationale, caution warnings)

**Success Metric:** After P8 Phase 2, future sessions can:
1. Trust session docs to be current within 1 day
2. Know which scripts are active vs. deprecated at a glance
3. Understand when to create new vs. update existing automation
4. Follow clear P8 precedent for strategic sessions

---

## Current State Assessment

### What Exists ✅

| Component | Status | Evidence |
|-----------|--------|----------|
| **Hook System** | ✅ Complete | Pre-commit/pre-push with clarifying messages (PR #348) |
| **Core Git Automation** | ✅ Mature | `ai_commit.sh`, `safe_push.sh`, `should_use_pr.sh` proven & tested |
| **Tier-0 Entrypoints** | ✅ Documented | agent_start.sh, ai_commit.sh, git_ops.sh (P7) |
| **Session Logging** | ✅ Implemented | SESSION_LOG.md with manual entries, hook_output logs |
| **Deprecation System** | ⚠️ Partial | install_enforcement_hook.sh marked deprecated, but others unclear |
| **Automation Catalog** | ✅ Comprehensive | 2,014-line automation-catalog.md with 103 scripts |
| **Mistakes Tracking** | ⚠️ Basic | agent_mistakes_report.sh parses git_workflow.log, CI log, but NOT hook_output logs |
| **Health Checks** | ✅ Good | git_automation_health.sh validates core scripts, has "Deprecated Script Check" (P7) |

### What's Missing ❌

| Component | Impact | Evidence |
|-----------|--------|----------|
| **P8 Work Plan Doc** | HIGH | SESSION_LOG.md references "session-19p8-work-plan.md" (not in repo) |
| **Session Doc Lifecycle** | HIGH | next-session-brief.md stale (shows P5-P7 achievements, not current state) |
| **Automation Governance** | HIGH | 103 scripts with no clear "active vs. legacy" classification |
| **New Script Checklist** | MEDIUM | No guard preventing undocumented scripts from being created |
| **Manual Git Detection** | MEDIUM | No linter to scan docs for `git add`, `git commit`, `git push` examples |
| **Hook Output Parser** | MEDIUM | agent_mistakes_report.sh doesn't parse hook_output_*.log files (121 pre-commit failures documented) |
| **Deprecation Policy** | MEDIUM | Only install_enforcement_hook.sh marked; others undocumented |
| **Strategic Plan Precedent** | LOW | No published P8 work plan to show "how to plan strategically" |

### What's Broken 🔴

| Issue | Severity | Root Cause | Evidence |
|-------|----------|-----------|----------|
| **Session docs lag behind** | HIGH | Manual update only when prompted | SESSION_LOG ends with P8 summary, next-session-brief still shows P5-P7 |
| **Automation sprawl confusion** | HIGH | Too many entrypoints, unclear deprecation | 103 scripts, 5-10 legacy ones mixed in, agents uncertain which to use |
| **Manual git fallbacks still exist** | MEDIUM | Agent panic → bypass automation → conflict | 67% of merge conflicts in Session 19P6 caused by manual git when scripts errored |
| **Hook output not analyzed** | MEDIUM | agent_mistakes_report.sh only checks git_workflow.log | hook_output_*.log has 25 files with blocking reasons, but invisible to agents |
| **P8 plan referenced, not found** | HIGH | Precedent broken: "plan before act" strategy not documented | SESSION_LOG.md line 15: "session-19p8-work-plan.md" (file doesn't exist) |

---

## Root Cause Analysis

### Root Cause 1: Session Documentation Lifecycle (HIGH PRIORITY)

**Symptom:** next-session-brief.md shows P5-P7 achievements, but P8 just completed

**Root Cause Chain:**
1. next-session-brief.md updated manually at end of session
2. Human forgets to update, or updates incompletely
3. Future agents read stale info ("P5 Python baseline", not "P8 hook clarity")
4. Decision-making based on outdated context

**Why It Matters:**
- Agents invest 20+ minutes reading stale handoff docs
- Risk of repeating work or misunderstanding priorities
- Breaks "plan before act" because plan is 24h old

**Prevention System Needed:**
- Automated freshness check on key docs (handoff.md, next-session-brief.md)
- Validation rule: SESSION_LOG.md latest entry must match next-session-brief.md date
- Optional: Auto-generate handoff from SESSION_LOG

### Root Cause 2: Automation Sprawl & Unclear Deprecation (HIGH PRIORITY)

**Symptom:** 103 scripts with 5-10 legacy ones mixed in; agents unsure which to trust

**Root Cause Chain:**
1. Over 4 weeks, scripts accumulated for different purposes
2. Some scripts became obsolete (install_enforcement_hook.sh deprecated)
3. No central registry of "active vs. legacy"
4. Agents read old docs, find manual workflows, think it's still acceptable
5. Confusion leads to fallback to manual git

**Evidence:**
- install_enforcement_hook.sh: deprecated (marked)
- agent_setup.sh, agent_preflight.sh: superseded by agent_start.sh (not clearly marked)
- agent_mistakes_report.sh: doesn't use hook_output logs (feature gap)
- check_session_docs.py: only validates session_docs (doesn't check for manual git examples)

**Why It Matters:**
- 103 scripts is confusing; agents don't know which to call
- Legacy scripts without deprecation warnings get copied/reused
- Manual git examples in non-archive docs teach wrong behavior

**Prevention System Needed:**
- Central "Automation Registry" (automation-status.md) listing every script with status
- Deprecation policy: all deprecated scripts marked + redirected to replacements
- Script guard: git_automation_health.sh runs at session start, warns if undocumented scripts found
- Doc guard: lint_docs_git_examples.sh detects manual git code in non-archive docs

### Root Cause 3: Hook Output Logs Invisible (MEDIUM PRIORITY)

**Symptom:** 121 pre-commit failures, 10 missing messages, 12 policy blocks documented in hook logs, but agent_mistakes_report.sh doesn't parse them

**Root Cause Chain:**
1. Hooks improved (P8 Phase 1) to add "why" and recovery guidance
2. Hook output logged to hook_output_*.log (25 files in logs/)
3. agent_mistakes_report.sh checks git_workflow.log, ci_monitor.log, but NOT hook_output
4. Agents run agent_mistakes_report.sh, see no hook issues, miss 121 failures
5. No learning from past hook blocks

**Why It Matters:**
- 121 pre-commit failures are real learning opportunities
- Agent mistakes report should highlight these to prevent repeats
- Without analysis, hook improvements don't transfer to agent behavior

**Prevention System Needed:**
- Extend agent_mistakes_report.sh to parse hook_output_*.log
- Parse blocking reasons (formatting, validation, safety check)
- Summarize: "X pre-commit failures (Y% formatting, Z% validation)"
- Top N failures per category

### Root Cause 4: Manual Git Examples in Non-Archive Docs (MEDIUM PRIORITY)

**Symptom:** agent-workflow-master-guide.md, automation-scripts.md contain manual git examples for "educational" purposes (showing what NOT to do)

**Root Cause Chain:**
1. Docs include manual git examples with ❌ warnings
2. Agent reads doc, sees examples, copies them, forgets the warning
3. Or agent under stress, sees example, uses it without reading warning
4. Fallback to manual git

**Why It Matters:**
- Humans have unconscious bias toward examples they see
- Even with warnings, examples are risky
- Non-archive docs should teach automation ONLY

**Prevention System Needed:**
- linter (lint_docs_git_examples.sh) to detect manual git in non-archive
- All manual git examples → move to git-automation/historical-mistakes/ (archive)
- Non-archive docs should ONLY show automation examples
- When showing "what not to do", use pseudocode, not real commands

### Root Cause 5: P8 Work Plan Not in Repo (HIGH PRIORITY)

**Symptom:** SESSION_LOG.md references "session-19p8-work-plan.md" (doesn't exist)

**Root Cause Chain:**
1. P8 implemented without publishing work plan
2. Strategy "plan before act" used internally, not documented
3. Future agents can't learn from P8 methodology
4. Precedent for "strategic planning" not established

**Why It Matters:**
- P8 Phase 1 succeeded because strategy was clear
- Without published plan, future strategic sessions lack template
- Knowledge transfer broken

**Prevention System Needed:**
- Publish P8 work plan (this document)
- Establish pattern for future strategic sessions
- Template: current-state → root-causes → commit-strategy → success-metrics

---

## 5+ Commit Strategy

### Commit 1: Create P8 Work Plan Doc (Documentation)
**Type:** Documentation | **Risk:** Low | **Est:** 20 min

**Scope:**
- Create `docs/planning/session-19p8-work-plan.md` (this document)
- Link from `docs/planning/README.md` as reference for "strategic planning"
- Add metadata header per folder-structure-governance

**Rationale:**
- Fix root cause: P8 precedent missing
- Future agents can copy structure for P8-style sessions
- Establishes "plan before act" as documented pattern

**Success Criteria:**
- File exists with complete analysis
- Linked from docs/planning/README.md
- Metadata valid per governance

**Dependencies:** None (first commit)

---

### Commit 2: Build Automation Registry (Governance)
**Type:** Automation + Documentation | **Risk:** Medium | **Est:** 45 min

**Scope:**
- Create `docs/reference/automation-registry.md` (new file)
  - Central catalog of all scripts with status: active|deprecated|legacy
  - For each: name, path, status, deprecation reason, replacement (if deprecated)
  - Last verified date
  - Example: install_enforcement_hook.sh → DEPRECATED (replaced by install_git_hooks.sh)
- Create `scripts/validate_automation_registry.py` (new script)
  - Compares registry against actual scripts in `scripts/`
  - Warns if undocumented scripts found (script safety check)
  - Warns if registry lists non-existent scripts
  - Exit code: 0=valid, 1=missing scripts, 2=undocumented scripts found
- Add hook to .pre-commit-config.yaml: validate_automation_registry.py
- Update `scripts/git_automation_health.sh` to call validate_automation_registry.py

**Rationale:**
- Fix root cause: automation sprawl & unclear deprecation
- Central source of truth for script status
- Guard against adding scripts without documentation

**Success Criteria:**
- Registry file exists, lists all 103 scripts
- Validation script runs in pre-commit without errors
- agent_mistakes_report.sh mentions registry in recommendations
- git_automation_health.sh warns if undocumented scripts found

**Dependencies:** Commit 1 (for reference in docs)

---

### Commit 3: Extend agent_mistakes_report.sh for Hook Logs (Automation)
**Type:** Automation + Quality | **Risk:** Low | **Est:** 30 min

**Scope:**
- Extend `scripts/agent_mistakes_report.sh` to:
  - Find latest hook_output_*.log files
  - Parse for blocking reasons (formatting, validation, safety, version drift, etc.)
  - Count by reason: "X formatting failures, Y validation failures, Z other"
  - Show top N failures with frequency
  - Parse recovery guidance from hook output (e.g., "→ Run: black --fix")
- Add function: `extract_hook_blocking_reasons()` with regex patterns
- Add function: `summarize_failures_by_category()` with category counts

**Rationale:**
- Fix root cause: hook output logs invisible
- Agents run agent_mistakes_report.sh, see hook issues + recovery steps
- Leverage P8 hook improvements (clarifying messages)

**Success Criteria:**
- agent_mistakes_report.sh parses hook_output_*.log files
- Shows blocking reasons with counts
- Shows example recovery steps
- No errors if hook_output logs missing

**Dependencies:** Commit 1 (for reference in improvements)

---

### Commit 4: Create Automation Linter (Prevention)
**Type:** Automation | **Risk:** Medium | **Est:** 45 min

**Scope:**
- Create `scripts/lint_docs_git_examples.sh` (new script)
  - Scans non-archive docs for manual git patterns: `git add`, `git commit`, `git push`, `git pull`
  - Excludes: docs/git-automation/historical-mistakes/, docs/_archive/
  - For each match: file, line number, context
  - Exit code: 0=no examples, 1=examples found (warning), 2=critical examples
  - Suggest fix: "Move to historical-mistakes/ or show only automation"
- Add hook to .pre-commit-config.yaml: lint_docs_git_examples.sh
- Classify matches as CRITICAL vs. WARNING:
  - CRITICAL: Examples without ❌ warning prefix (teach wrong behavior)
  - WARNING: Examples with ❌ warning (educational but risky)

**Rationale:**
- Fix root cause: manual git examples in non-archive docs
- Prevent future docs from repeating mistake
- Educational examples → historical archive only

**Success Criteria:**
- Script finds existing manual git examples
- Exits with warnings, not errors (educational docs are OK)
- Suggests archival for critical cases
- No false positives (allowlist patterns like "git add -A" in scripts)

**Dependencies:** Commit 2 (for context in prevention messaging)

---

### Commit 5: Session Documentation Lifecycle Validator (Prevention)
**Type:** Automation | **Risk:** Medium | **Est:** 40 min

**Scope:**
- Create `scripts/validate_session_docs_freshness.py` (new script)
  - Check 1: next-session-brief.md "Last Session" matches SESSION_LOG.md latest date
  - Check 2: next-session-brief.md date field (comment) within 24 hours
  - Check 3: SESSION_LOG.md latest entry not older than 3 days (gap detection)
  - Output:
    - ✅ Fresh: Brief updated within 24h, SESSION_LOG current
    - ⚠️ Stale: Brief 1-3 days old (warning)
    - ❌ Critical: Brief 3+ days old or SESSION_LOG silent for 3+ days (error)
- Add to .pre-commit-config.yaml as warning hook (not blocking)
- Add to end_session.py to verify before handoff

**Rationale:**
- Fix root cause: session docs stale
- Catch staleness at commit time (easy fix)
- Establish expectation: docs update after each session

**Success Criteria:**
- Script passes with current next-session-brief.md
- Warns if last update > 24h ago
- Suggests `update_handoff.py` command to fix
- end_session.py runs this check before declaring "ready for handoff"

**Dependencies:** Commits 1-4 (for comprehensive understanding)

---

### Commit 6: Update docs/planning/README.md with Strategic Planning Section (Documentation)
**Type:** Documentation | **Risk:** Low | **Est:** 30 min

**Scope:**
- Add section to `docs/planning/README.md`:
  - "Strategic Planning Sessions (P8-style)"
  - When to use: major architecture changes, policy shifts, automation improvements
  - Template: link to session-19p8-work-plan.md
  - Process: "Analyze → Plan → Execute (5+ commits) → Document"
  - Success criteria template
- Link all P8 deliverables:
  - session-19p8-work-plan.md (this document)
  - automation-registry.md (Commit 2)
  - lint_docs_git_examples.sh (Commit 4)
  - validate_session_docs_freshness.py (Commit 5)

**Rationale:**
- Establish precedent for strategic sessions
- Help future agents plan similar sessions
- Document process, not just outcomes

**Success Criteria:**
- Section added to planning README
- Links all P8 deliverables
- Template clear enough for future agents to copy

**Dependencies:** Commits 1-5 (to document deliverables)

---

### Commit 7: README.md Update for Deprecated Scripts Section (Documentation)
**Type:** Documentation | **Risk:** Low | **Est:** 25 min

**Scope:**
- Add section to `docs/git-automation/README.md`:
  - "Deprecated Scripts" subsection
  - Table: script name, deprecation date, replacement, reason
  - Example: install_enforcement_hook.sh → install_git_hooks.sh
  - Link to automation-registry.md for complete list
- Update navigation map in git-automation/README.md to include automation-registry

**Rationale:**
- Make deprecation visible without searching logs
- Redirect agents to correct replacement
- Prevent old scripts from being re-used

**Success Criteria:**
- Section added with clear deprecation guidance
- Links to registry for full picture
- Matches automation-registry.md data

**Dependencies:** Commit 2 (automation-registry.md must exist)

---

### Commit 8: Update SESSION_LOG.md with P8 Phase 2 Summary (Documentation)
**Type:** Documentation | **Risk:** Low | **Est:** 20 min

**Scope:**
- Add entry to SESSION_LOG.md:
  - Date: 2026-01-12
  - Title: Session 19P8 Phase 2: Automation Governance & Prevention
  - Achievements section:
    - ✅ Automated session doc freshness checks
    - ✅ Central automation registry + validation
    - ✅ Hook output log analysis in mistakes report
    - ✅ Manual git example linter
    - ✅ Strategic planning documentation (template)
  - Commits: list 7 commits with hashes
  - Key Improvements: same as "Automation Improvements Needed" section below
  - Metrics: 5 new scripts, 3 new validators, 0 merge conflicts

**Rationale:**
- Complete P8 narrative (Phase 1 + Phase 2)
- Future agents see full strategy
- Establish precedent for strategic session logging

**Success Criteria:**
- Entry shows P8 as complete system (Phase 1 hook clarity + Phase 2 governance)
- Explains why each improvement matters
- Metrics demonstrate success

**Dependencies:** All previous commits (summarizes work)

---

## Automation Improvements Needed

| Script/System | Current State | Improvement | Est. | Commit |
|---------------|---------------|-------------|------|--------|
| agent_mistakes_report.sh | Parses 2 logs | Parse hook_output logs (25 files) | 30m | #3 |
| git_automation_health.sh | Checks scripts exist | Validate against registry, warn if undocumented | 15m | #2 |
| lint (new) | None | Detect manual git in non-archive docs | 45m | #4 |
| Validator (new) | None | Check session docs freshness | 40m | #5 |
| Registry (new) | None | Central automation status catalog | 45m | #2 |
| Deprecation policy | Scattered | Unified automation-registry.md | 15m | #2 |

---

## Documentation Updates Required

| Document | Current State | Required Update | Commit |
|----------|---------------|-----------------|--------|
| session-19p8-work-plan.md | Missing | CREATE with full analysis | #1 |
| automation-registry.md | Missing | CREATE with 103 scripts listed | #2 |
| docs/git-automation/README.md | No deprecation section | Add deprecated scripts table | #7 |
| docs/planning/README.md | No strategic planning | Add P8-style template + links | #6 |
| SESSION_LOG.md | P8 P1 only | Add P8 P2 summary + commits | #8 |
| next-session-brief.md | Shows P5-P7 | Will auto-update after P8 P2 complete |  |

---

## Success Metrics

### Quality Gates
- [ ] All 8 commits pass pre-commit hooks (lint_docs_git_examples.sh, automation-registry validator)
- [ ] No manual git commands used (all commits via ai_commit.sh)
- [ ] CI passes (tests, links, version drift)
- [ ] SESSION_LOG.md entry complete with commit hashes

### Functional Metrics
- [ ] agent_mistakes_report.sh parses hook_output logs and shows blocking reasons
- [ ] validate_automation_registry.py runs at pre-commit, passes with no warnings
- [ ] lint_docs_git_examples.sh runs, finds no CRITICAL examples in non-archive docs
- [ ] validate_session_docs_freshness.py passes with current docs
- [ ] end_session.py runs freshness check

### Prevention Metrics
- [ ] 0 new undocumented scripts added (if attempted, caught by registry validator)
- [ ] 0 manual git examples in docs/git-automation/ (if attempted, caught by linter)
- [ ] 0 stale session docs (if attempted, caught by freshness validator)
- [ ] 5+ commits delivered (5+ meaningful improvements)

### Knowledge Transfer
- [ ] session-19p8-work-plan.md published and linked from planning README
- [ ] automation-registry.md accessible from git-automation/README.md
- [ ] Deprecation policy documented (in git-automation/README.md)
- [ ] Strategic planning template established for future P8-style sessions

---

## Risks & Mitigation

### Risk 1: Registry Becomes Stale
**Risk:** Automation-registry.md lists scripts, but new scripts added without updating registry.

**Mitigation:**
- Pre-commit hook: validate_automation_registry.py blocks commits with undocumented scripts
- Exit code 2 if new scripts found without registry entry
- Agent must add to registry before commit succeeds

### Risk 2: Linter False Positives
**Risk:** lint_docs_git_examples.sh flags legitimate examples in shell scripts or code samples.

**Mitigation:**
- Allowlist patterns: "git add" in scripts/ is OK, but not in docs/git-automation/
- Exit with WARNING (code 1) for matches in scripts/, ERROR (code 2) only for non-archive docs
- Test on existing docs before committing

### Risk 3: Validators Slow Down Commits
**Risk:** 5 new validators (registry, freshness, lint) add latency to pre-commit.

**Mitigation:**
- Registry: Python script with minimal logic (file read + comparison), <1s
- Freshness: YAML date check, <0.5s, runs at session-end (not pre-commit)
- Linter: grep-based, runs on changed files only, <2s
- Total estimated: +3-4s per commit (acceptable)

### Risk 4: Hook Output Parser Fragile
**Risk:** Hook output format changes, parser breaks.

**Mitigation:**
- Use conservative regex patterns (look for "FAILED:", "Pre-commit", "Formatting", etc.)
- Graceful fallback: if parsing fails, show raw counts only
- Test on 25 existing hook_output_*.log files before committing

### Risk 5: Agent Resistance to More Rules
**Risk:** Agents perceive new validators as bureaucratic obstacles.

**Mitigation:**
- Frame as "learning systems" (agent_mistakes_report learns from hook logs)
- Document "why" in each validator (comments in code)
- Make error messages helpful (suggest fix, not just complaint)
- Timing: run at end-of-session or pre-commit (not blocking interactive work)

---

## Execution Timeline

**Total Estimated:** 3.5-4 hours (5+ commits)

| Commit | Component | Est. | Sequential |
|--------|-----------|------|-----------|
| #1 | P8 work plan doc | 20m | Linear |
| #2 | Automation registry | 45m | After #1 |
| #3 | Hook output parser | 30m | Parallel with #2 |
| #4 | Manual git linter | 45m | After #2 |
| #5 | Session doc validator | 40m | After #2 |
| #6 | Planning README | 30m | After #1-5 |
| #7 | Git-automation README | 25m | After #2 |
| #8 | SESSION_LOG entry | 20m | Last (summarizes #1-7) |

**Parallel Execution:** Commits #2 and #3 can be worked simultaneously.

**Critical Path:** #1 → #2 → #4, #5, #6, #7 → #8

---

## How This Achieves "Automation-First" & "Plan Before Act"

### Automation-First
- **Root cause fixes:** Each commit fixes a cause, not symptom
  - Manual git in docs → lint detects it (automated prevention)
  - Automation sprawl → registry centralizes it (automated validation)
  - Hook output invisible → parser extracts learning (automated analysis)
- **Prevention before reaction:** Guards run at pre-commit, before human decides
- **Scalability:** Validators work for 103 scripts and will work for 200

### Plan Before Act
- **Strategic document:** P8 work plan published (template for future)
- **Root cause analysis:** This document shows thinking process (not just outcomes)
- **Prevention system:** Not one-off fixes, but permanent infrastructure
- **Success metrics:** Defined upfront, verifiable post-session

---

## Legacy vs. This Approach

### Legacy Approach (What Failed)
```
Problem detected → One-off fix → Commit
Example: Session 19P7 added deprecation banner to one doc
Result: Other docs still had manual git examples
```

### P8 Phase 2 Approach (Permanent Prevention)
```
Problem detected → Root cause analysis → Automation system → Validator guard → Commit
Example: Manual git in docs
Root cause: Examples teach wrong behavior
System: lint_docs_git_examples.sh
Guard: Pre-commit hook blocks problematic examples
Result: Future docs can't have this problem
```

**Key Difference:** Prevents the problem from recurring, not just fixes today's instance.

---

## Appendix: Hook Output Log Metrics

From logs/ inspection (25 files, Jan 12):

| Category | Count | Example |
|----------|-------|---------|
| Pre-commit passes | 12 | check yaml, trim whitespace, merge conflicts |
| Pre-commit failures | ~8 | (implied by pass count) |
| Doc validation | 15 | check session docs, check task format, version drift |
| Formatting checks | 5 | black, ruff, isort status |
| Duration tracked | 20 | 0.02s-0.67s per check |

**Opportunity:** Parse these logs to show "X checks run, Y% passed" in agent_mistakes_report.

---

## Questions This Plan Answers

**Q: Why publish P8 work plan now (not just do the work)?**
A: Establishes "strategic planning" as documented pattern. Future agents can copy structure for P9, P10.

**Q: Aren't 8 commits "too many" for one session?**
A: No. Each is independent, logical, small (20-45 min each). Together they form a system. Better to deliver one-time than piecemeal.

**Q: Won't automation-registry.md become stale?**
A: Yes, but validator prevents it from being WRONG. Validator ensures: "Every script in registry exists" and "Every script in scripts/ is in registry." Validator runs at pre-commit.

**Q: Why extend agent_mistakes_report.sh instead of creating new script?**
A: DRY principle. Report script already shown to agents at session start. Extending it is less friction than new command.

**Q: Should lint_docs_git_examples.sh block commits (error) or just warn?**
A: Warn (exit 1) for educational examples, error (exit 2) for critical. Gives flexibility: historians can keep examples in git-automation/historical-mistakes/, but blocks new ones in production docs.

---

**Ready for execution. This plan follows "plan before act" and "automation-first" principles.**
