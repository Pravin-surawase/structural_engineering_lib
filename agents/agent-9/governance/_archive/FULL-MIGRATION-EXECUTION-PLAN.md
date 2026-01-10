# Full Folder Structure Migration - Ultra-Safe Execution Plan

**Version:** 1.0.0
**Date:** 2026-01-10
**Status:** 🚀 APPROVED - Ready for Execution
**Duration:** 6-8 days (dedicated migration work)
**Expected Result:** 0 validation errors, governance-aligned folder structure

---

## 📋 Executive Summary

This document provides a **step-by-step, ultra-safe migration plan** to completely clean up the project folder structure, eliminating all 115 validation errors.

**Key Principles:**
- ✅ **Safety First:** Every phase has rollback procedures
- ✅ **Validation After Each Step:** Catch errors immediately
- ✅ **Git History Preserved:** Use `git mv` for all moves
- ✅ **Automated Where Possible:** Scripts reduce human error
- ✅ **Comprehensive Testing:** Verify at each checkpoint

**User Approval Received:**
- ✅ Option D (Full Migration) selected
- ✅ 6+ days dedicated work authorized
- ✅ Focus on migration (pause feature work)
- ✅ Review at end of each phase
- ✅ Start date: 2026-01-10

---

## 📊 Migration Scope

### Current State (2026-01-10)
```
❌ 115 VALIDATION ERRORS

Breakdown:
- Root directory: 16 files (limit: 10) - 6 over
- docs/ root: 44 files (limit: 5) - 39 over 🔴 CRITICAL
- agents/ root: 13 files (limit: 1) - 12 over 🔴 CRITICAL
- Dated files misplaced: 23 files
- Naming violations: 92 files (UPPERCASE/underscores)
```

### Target State (After Migration)
```
✅ 0 VALIDATION ERRORS

Expected:
- Root directory: ≤10 files (canonical only)
- docs/ root: ≤5 files (index + top-level guides)
- agents/ root: 1 file (agents/README.md)
- Dated files: All in docs/_archive/YYYY-MM/
- Naming: All files in kebab-case
```

---

## 🧭 Lessons Learned + One-Time Migration Policy

This is a **one-time structural migration**. We already attempted a similar cleanup last month and it was time-consuming because we did **not** follow a clean, phased process.

**Key lessons from the previous attempt:**
- Migration overlapped with feature work → paths drifted mid-move.
- No freeze window → new docs appeared while files were moving.
- Incomplete governance alignment → target structure drifted from validator rules.

**Non-repeat policy (must hold):**
- **Single migration window** only; no repeat migration for this project unless:
  1) `agents/agent-9/governance/FOLDER_STRUCTURE_GOVERNANCE.md` is updated first,
  2) validator expectations are updated and green,
  3) a new phased plan is approved.
- Any future structural change is treated as a **governance change request**, not an ad-hoc refactor.

---

## 🧩 Future Growth Guardrails (Before We Grow)

We must plan for expansion without breaking structure again. Growth should be **additive** within governed categories, not a repeat migration.

**Reserved expansion zones (require governance update before use):**
- `docs/integrations/` (external systems, DXF, IFC, ETABS, etc.)
- `docs/data/` (datasets, fixtures, validation baselines)
- `docs/ui/` (UX patterns, component specs, UI architecture)
- `docs/benchmarks/` (performance targets, baselines)
- `docs/ops/` (deployment/monitoring/runbooks)

**Rule:** If a new category is needed, update governance + validator before creating it.

---

## 🗂️ Document Structure

This migration plan is organized into multiple documents for clarity:

### Main Documents (Read in Order)

1. **[FULL-MIGRATION-EXECUTION-PLAN.md](FULL-MIGRATION-EXECUTION-PLAN.md)** (this file)
   - Executive summary
   - Overview and scope
   - Quick reference

2. **[PHASE-0-PREPARATION.md](PHASE-0-PREPARATION.md)**
   - Pre-migration checklist
   - Backup procedures
   - Tool installation
   - Risk assessment

3. **[PHASE-1-STRUCTURE-CREATION.md](PHASE-1-STRUCTURE-CREATION.md)**
   - Create new folder structure
   - Validation of structure
   - Low risk, foundation phase

4. **[PHASE-2-AGENTS-MIGRATION.md](PHASE-2-AGENTS-MIGRATION.md)**
   - Move 12 agent role files
   - Update agent references
   - High impact phase

5. **[PHASE-3-DOCS-MIGRATION.md](PHASE-3-DOCS-MIGRATION.md)**
   - Move 39 docs/ root files
   - Largest, most complex phase
   - Categorization required

6. **[PHASE-4-DATED-FILES.md](PHASE-4-DATED-FILES.md)**
   - Archive 23 dated files
   - Automated archival
   - Medium complexity

7. **[PHASE-5-NAMING-CLEANUP.md](PHASE-5-NAMING-CLEANUP.md)**
   - Rename 92 files to kebab-case
   - Can be automated
   - Low risk, high volume

8. **[PHASE-6-LINK-FIXING.md](PHASE-6-LINK-FIXING.md)**
   - Update all internal links
   - Critical for usability
   - Automated + manual verification

9. **[PHASE-7-SCRIPT-UPDATES.md](PHASE-7-SCRIPT-UPDATES.md)**
   - Update hardcoded paths in scripts
   - Test all automation
   - Medium risk

10. **[PHASE-8-FINAL-VALIDATION.md](PHASE-8-FINAL-VALIDATION.md)**
    - Comprehensive validation
    - Performance testing
    - Sign-off procedures

### Supporting Documents

11. **[ROLLBACK-PROCEDURES.md](ROLLBACK-PROCEDURES.md)**
    - Emergency rollback for each phase
    - Recovery procedures
    - Troubleshooting guide

12. **[MIGRATION-SCRIPTS.md](MIGRATION-SCRIPTS.md)**
    - All automation scripts
    - Script documentation
    - Usage examples

13. **[LINK-MAP.md](LINK-MAP.md)** (auto-generated)
    - Old path → New path mapping
    - Used for automated link fixing
    - Reference for manual updates

---

## 📅 Timeline & Schedule

### Recommended 8-Day Schedule

**Day 0: Preparation (2-3 hours)**
- Create backup tag
- Install tools
- Review plan
- Verify prerequisites

**Day 1: Foundation (3-4 hours)**
- Phase 1: Create folder structure
- Phase 2: Migrate agents/ files
- First validation checkpoint

**Day 2: Documentation Migration Part 1 (6-8 hours)**
- Phase 3: Move docs/ files (first 20 files)
- Categorization and planning
- Mid-phase validation

**Day 3: Documentation Migration Part 2 (6-8 hours)**
- Phase 3: Move docs/ files (remaining 19 files)
- Complete docs/ migration
- End-of-phase validation

**Day 4: Archival & Naming Part 1 (4-6 hours)**
- Phase 4: Archive dated files
- Phase 5: Naming cleanup (first 45 files)
- Mid-phase validation

**Day 5: Naming Part 2 (4-6 hours)**
- Phase 5: Naming cleanup (remaining 47 files)
- Complete naming migration
- End-of-phase validation

**Day 6: Link Fixing (6-8 hours)**
- Phase 6: Update all links
- Automated fixing + manual verification
- Critical validation

**Day 7: Script Updates (3-4 hours)**
- Phase 7: Update automation scripts
- Test all scripts
- Verify CI/CD

**Day 8: Final Validation (2-3 hours)**
- Phase 8: Comprehensive testing
- Performance validation
- Migration completion report

**Total Effort:** 30-40 hours over 8 days

---

## 🎯 Success Criteria

### Phase-Level Success Criteria

Each phase must meet these criteria before proceeding:

1. ✅ **All phase tasks completed** (checklist 100%)
2. ✅ **Validation errors reduced** (measurable progress)
3. ✅ **Git history preserved** (`git log --follow` works)
4. ✅ **Changes committed and pushed** (backed up remotely)
5. ✅ **No regressions** (existing functionality intact)

### Overall Success Criteria

Migration is complete when:

1. ✅ **0 validation errors** (`validate_folder_structure.py --report`)
2. ✅ **0 broken links** (`check_links.py`)
3. ✅ **All tests passing** (2,370+ tests)
4. ✅ **All scripts working** (automation functional)
5. ✅ **Documentation complete** (README updated)
6. ✅ **Performance maintained** (no degradation)

---

## 🔒 Safety Mechanisms

### Backup Strategy (Triple Protection)

1. **Git Tags:** Backup tag before each phase
   ```bash
   git tag backup-phase-N-$(date +%Y-%m-%d-%H%M)
   git push origin --tags
   ```

2. **Branch Checkpoints:** Feature branch for migration
   ```bash
   git checkout -b migration-full-cleanup-2026-01
   # Work on this branch, merge to main at end
   ```

3. **Local Backup:** External copy (optional but recommended)
   ```bash
   tar -czf ../backup-pre-migration-$(date +%Y-%m-%d).tar.gz .
   ```

### Change Freeze Window (Mandatory)

During migration phases:
- **No feature work** (docs/code) in parallel.
- **No new documents** outside `docs/_active/YYYY-MM/`.
- **No renames** outside the phase steps.
- **Close editors** before file moves.

If any of these are violated, **stop and reset** to the last backup tag.

### Validation Checkpoints

**After Each Phase:**
```bash
# 1. Structural validation
cd Python && ../.venv/bin/python ../scripts/validate_folder_structure.py --report

# 2. Git status check
git status
# Should show only expected changes

# 3. History verification
git log --stat -1
# Should show moves, not deletions

# 4. Test suite
.venv/bin/python -m pytest -q
# Should show 2,370+ passed
```

### Rollback Triggers

**STOP and rollback if ANY of these occur:**

1. ❌ Validation errors **increase** (should only decrease)
2. ❌ Git shows **deletions** instead of renames
3. ❌ Tests **fail** (regression introduced)
4. ❌ **Unable to find** moved files
5. ❌ **Uncertain** about next step

**See [ROLLBACK-PROCEDURES.md](ROLLBACK-PROCEDURES.md) for recovery steps.**

---

## 🚀 Quick Start (For Agent 9)

### First-Time Execution

**Step 1: Read this document** (15 minutes)
- Understand scope and timeline
- Review success criteria
- Note safety mechanisms

**Step 2: Execute Phase 0** (2-3 hours)
```bash
# Follow PHASE-0-PREPARATION.md step by step
# Create backups, install tools, verify prerequisites
```

**Step 3: Execute Phases 1-8 in sequence** (30-40 hours)
```bash
# Each phase has its own detailed document
# Follow each document step by step
# Validate after each phase
# Commit and push after each phase
```

**Step 4: Final validation** (2-3 hours)
```bash
# Follow PHASE-8-FINAL-VALIDATION.md
# Comprehensive testing
# Sign-off and completion
```

---

## 📖 Reading Guide

### For Agent 9 (Governance Agent)

**Before Starting:**
1. Read this document (FULL-MIGRATION-EXECUTION-PLAN.md) - 15 min
2. Read PHASE-0-PREPARATION.md - 15 min
3. Read ROLLBACK-PROCEDURES.md - 10 min

**During Migration:**
- Read each phase document **before** executing that phase
- Keep ROLLBACK-PROCEDURES.md accessible
- Refer to LINK-MAP.md (auto-generated) for path mappings

**After Completion:**
- Update agents/agent-9/README.md with migration completion
- Archive migration documents to docs/archive/2026-01/governance/
- Update next-session-brief.md with post-migration status

### For Human Reviewer

**Quick Review (10 minutes):**
- This document (executive summary)
- Success criteria section
- Timeline section

**Full Review (45 minutes):**
- This document
- PHASE-0-PREPARATION.md (pre-flight checklist)
- PHASE-3-DOCS-MIGRATION.md (most complex phase)
- ROLLBACK-PROCEDURES.md (safety net)

**Deep Dive (2 hours):**
- All 13 documents in sequence
- Understand every step
- Review scripts in MIGRATION-SCRIPTS.md

---

## 🎓 Integration with Agent 9

### Agent 9 Role in Migration

This migration is a **special governance session** for Agent 9. Normal governance sessions are 2-4 hours; this is an extended 30-40 hour session spread over 8 days.

**Agent 9's Responsibilities:**
1. Execute migration phases step by step
2. Validate after each phase
3. Maintain migration log (SESSION_LOG.md)
4. Report progress daily
5. Handle rollbacks if needed
6. Generate completion report

### Agent 9 Prompts (For User)

**To Start Migration:**
```
Act as Agent 9 (GOVERNANCE). Execute the full folder structure migration.

Start with Phase 0 (Preparation). Follow the step-by-step instructions in:
agents/agent-9/governance/PHASE-0-PREPARATION.md

Report progress after completing Phase 0.

Ref: agents/agent-9/governance/FULL-MIGRATION-EXECUTION-PLAN.md
```

**To Resume After Phase N:**
```
Act as Agent 9 (GOVERNANCE). Continue full folder structure migration.

Execute Phase N+1. Follow the step-by-step instructions in:
agents/agent-9/governance/PHASE-[N+1]-*.md

Validate and report progress after completing Phase N+1.

Ref: agents/agent-9/governance/FULL-MIGRATION-EXECUTION-PLAN.md
```

**To Complete Migration:**
```
Act as Agent 9 (GOVERNANCE). Complete the full folder structure migration.

Execute Phase 8 (Final Validation). Follow:
agents/agent-9/governance/PHASE-8-FINAL-VALIDATION.md

Generate migration completion report and update governance metrics.

Ref: agents/agent-9/governance/FULL-MIGRATION-EXECUTION-PLAN.md
```

---

## 📊 Progress Tracking

### Migration Dashboard (Update Daily)

Create `agents/agent-9/governance/MIGRATION-PROGRESS.md`:

```markdown
# Migration Progress Dashboard

**Started:** 2026-01-10
**Target Completion:** 2026-01-18
**Status:** Phase N of 8

## Phase Completion

- [x] Phase 0: Preparation ✅ (2026-01-10)
- [ ] Phase 1: Structure Creation (In Progress)
- [ ] Phase 2: Agents Migration
- [ ] Phase 3: Docs Migration
- [ ] Phase 4: Dated Files
- [ ] Phase 5: Naming Cleanup
- [ ] Phase 6: Link Fixing
- [ ] Phase 7: Script Updates
- [ ] Phase 8: Final Validation

## Error Reduction Progress

| Phase | Errors Before | Errors After | Reduction |
|-------|---------------|--------------|-----------|
| Start | 115 | 115 | 0% |
| Phase 1 | 115 | 115 | 0% (structure only) |
| Phase 2 | 115 | ~103 | 10% |
| Phase 3 | ~103 | ~64 | 44% |
| Phase 4 | ~64 | ~41 | 64% |
| Phase 5 | ~41 | ~6 | 95% |
| Phase 6 | ~6 | ~6 | 95% (links only) |
| Phase 7 | ~6 | ~6 | 95% (scripts only) |
| Phase 8 | ~6 | 0 | 100% ✅ |

## Time Tracking

- Phase 0: X hours
- Phase 1: X hours
- ...
- **Total:** X hours (Target: 30-40 hours)

## Issues Log

- Issue 1: [Description] - Resolved: [How]
- Issue 2: [Description] - Resolved: [How]

## Next Session

Date: YYYY-MM-DD
Phase: N
Estimated Duration: X hours
```

---

## 🔗 Quick Reference Links

### Phase Documents
- [Phase 0: Preparation](PHASE-0-PREPARATION.md)
- [Phase 1: Structure Creation](PHASE-1-STRUCTURE-CREATION.md)
- [Phase 2: Agents Migration](PHASE-2-AGENTS-MIGRATION.md)
- [Phase 3: Docs Migration](PHASE-3-DOCS-MIGRATION.md)
- [Phase 4: Dated Files](PHASE-4-DATED-FILES.md)
- [Phase 5: Naming Cleanup](PHASE-5-NAMING-CLEANUP.md)
- [Phase 6: Link Fixing](PHASE-6-LINK-FIXING.md)
- [Phase 7: Script Updates](PHASE-7-SCRIPT-UPDATES.md)
- [Phase 8: Final Validation](PHASE-8-FINAL-VALIDATION.md)

### Supporting Documents
- [Rollback Procedures](ROLLBACK-PROCEDURES.md)
- [Migration Scripts](MIGRATION-SCRIPTS.md)
- [Link Map](LINK-MAP.md) (auto-generated during migration)

### Related Documents
- [Agent 9 README](README.md)
- [Folder Structure Governance](FOLDER_STRUCTURE_GOVERNANCE.md)
- [Migration Review & Risks](MIGRATION_REVIEW_AND_RISKS.md)

---

## ✅ Pre-Migration Checklist (Quick)

Before starting Phase 0, verify:

- [ ] **User approval received** (Option D selected)
- [ ] **6-8 day window available** (uninterrupted)
- [ ] **Git working tree clean** (`git status`)
- [ ] **All work committed and pushed** (`git log origin/main..HEAD` is empty)
- [ ] **CI is green** (all tests passing)
- [ ] **Open PRs reviewed** (merge or pause)
- [ ] **This document read** (15 minutes)
- [ ] **Phase 0 document ready** (next step)
- [ ] **Target structure matches governance + validator** (no drift)
- [ ] **Freeze window announced** (no parallel edits during migration)

**If ALL checkboxes are ✅:** Proceed to [PHASE-0-PREPARATION.md](PHASE-0-PREPARATION.md)

**If ANY checkbox is ❌:** Fix the issue before proceeding

---

## 🆘 Emergency Contacts

**If migration encounters critical issues:**

1. **STOP immediately** - Don't proceed to next step
2. **Document the issue** - Screenshot, error messages, git status
3. **Consult [ROLLBACK-PROCEDURES.md](ROLLBACK-PROCEDURES.md)**
4. **Execute rollback** if recovery is unclear
5. **Report to user** with details and recommendation

**Remember:** It's always safer to rollback and retry than to push forward when uncertain.

---

**Status:** 📋 PLAN COMPLETE - Ready for Phase 0
**Next:** [PHASE-0-PREPARATION.md](PHASE-0-PREPARATION.md)
**Estimated Next Session:** 2-3 hours

---

**Document End**
