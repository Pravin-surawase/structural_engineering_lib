# Agent 8 Consolidation Plan

**Date:** 2026-01-10
**Purpose:** Consolidate all Agent 8 files into agents/agent-8/ folder
**Owner:** Agent 9 (Governance)
**Status:** 📋 Planning Complete

---

## Executive Summary

Agent 8 files are currently scattered across:
- `docs/planning/` (7 files)
- `docs/research/` (5 files)
- `scripts/` (13 automation scripts)
- `git_operations_log/` (3 operational logs)

**Goal:** Consolidate into `agents/agent-8/` with proper structure, preserve git history, make easily accessible.

---

## Inventory of Agent 8 Files

### Documentation Files (12 total)

**Core Protocol & Guides (docs/planning/ → agents/agent-8/protocol/)**
1. `agent-8-tasks-git-ops.md` (1,320 lines) - Core mission & protocol
2. `agent-8-mistakes-prevention-guide.md` (1,096 lines) - Historical mistakes DB
3. `agent-8-implementation-guide.md` - Implementation instructions
4. `agent-8-multi-agent-coordination.md` - Multi-agent workflow

**Weekly Summaries (docs/planning/ → agents/agent-8/weekly/)**
5. `agent-8-week1-completion-summary.md` - Week 1 results
6. `agent-8-week2-plan.md` - Week 2 plan
7. `agent-8-git-operations-log.md` - Log format specification

**Research & Analysis (docs/research/ → agents/agent-8/research/)**
8. `agent-8-week1-summary.md` - Week 1 research summary
9. `agent-8-week1-reality-check.md` - Week 1 reality check
10. `agent-8-week1-implementation-blocker.md` - Week 1 blockers
11. `agent-8-implementation-priority.md` - Implementation priorities
12. `agent-8-optimization-research.md` - Optimization research

### Automation Scripts (13 total)

**Core Workflow (scripts/ → agents/agent-8/scripts/)**
1. `ai_commit.sh` (2.6K) - Entry point for commits
2. `safe_push.sh` (13K) - Core 7-step workflow
3. `safe_push_v2.sh` (11K) - Version 2 (backup)
4. `should_use_pr.sh` (13K) - PR decision logic
5. `should_use_pr_old.sh` (7.6K) - Old version (backup)

**PR Management (scripts/ → agents/agent-8/scripts/)**
6. `create_task_pr.sh` (1.8K) - Start PR workflow
7. `finish_task_pr.sh` (3.0K) - Submit PR

**Recovery & Validation (scripts/ → agents/agent-8/scripts/)**
8. `recover_git_state.sh` (3.4K) - Emergency recovery
9. `validate_git_state.sh` (8.3K) - State validation

**Environment Setup (scripts/ → agents/agent-8/scripts/)**
10. `agent_setup.sh` (8.1K) - Session setup
11. `agent_preflight.sh` (10K) - Pre-task checks
12. `worktree_manager.sh` (15K) - Worktree management

**Testing (scripts/ → agents/agent-8/tests/)**
13. `test_should_use_pr.sh` (7.6K) - PR decision tests

**Related Test Scripts (keep in scripts/, link from agent-8/)**
- `test_merge_conflicts.sh` - Merge conflict tests
- `test_branch_operations.sh` - Branch operation tests
- `ci_monitor_daemon.sh` - CI monitoring

### Operational Logs (3 files)

**git_operations_log/ → agents/agent-8/logs/**
1. `2026-01.log` - January operations log
2. `2026-01-08.md` - Jan 8 operations
3. `2026-01-08-operations.log` - Jan 8 detailed log

---

## Proposed Structure

```
agents/agent-8/
├── README.md                    # Main entry point (NEW)
├── QUICK-START.md              # Quick reference (NEW)
├── protocol/                   # Core documentation
│   ├── README.md               # Protocol overview
│   ├── tasks-git-ops.md        # Core mission (from agent-8-tasks-git-ops.md)
│   ├── mistakes-prevention.md  # Historical mistakes (from agent-8-mistakes-prevention-guide.md)
│   ├── implementation-guide.md
│   └── multi-agent-coordination.md
├── weekly/                     # Weekly summaries
│   ├── README.md
│   ├── week1-completion.md
│   ├── week2-plan.md
│   └── operations-log-spec.md  # Log format (from agent-8-git-operations-log.md)
├── research/                   # Research & analysis
│   ├── README.md
│   ├── week1-summary.md
│   ├── week1-reality-check.md
│   ├── week1-blockers.md       # (from agent-8-week1-implementation-blocker.md)
│   ├── implementation-priority.md
│   └── optimization-research.md
├── scripts/                    # Automation scripts
│   ├── README.md               # Script documentation (NEW)
│   ├── core/                   # Core workflow
│   │   ├── ai_commit.sh
│   │   ├── safe_push.sh
│   │   └── should_use_pr.sh
│   ├── pr/                     # PR management
│   │   ├── create_task_pr.sh
│   │   └── finish_task_pr.sh
│   ├── recovery/               # Recovery & validation
│   │   ├── recover_git_state.sh
│   │   └── validate_git_state.sh
│   ├── setup/                  # Environment setup
│   │   ├── agent_setup.sh
│   │   ├── agent_preflight.sh
│   │   └── worktree_manager.sh
│   ├── legacy/                 # Old versions (backup)
│   │   ├── safe_push_v2.sh
│   │   └── should_use_pr_old.sh
│   └── tests/                  # Script tests
│       └── test_should_use_pr.sh
└── logs/                       # Operations logs
    ├── README.md               # Log format & retention
    ├── 2026-01.log
    ├── 2026-01-08.md
    └── 2026-01-08-operations.log
```

---

## Key Improvements

### 1. Discoverability
- **Single entry point:** `agents/agent-8/README.md`
- **Quick reference:** `QUICK-START.md` with essential commands
- **Organized by purpose:** protocol, weekly, research, scripts, logs

### 2. Script Organization
- **Grouped by function:** core, pr, recovery, setup
- **Clear naming:** Remove "agent-8-" prefix (folder provides context)
- **Legacy preserved:** Old versions in legacy/ subfolder

### 3. Documentation Clarity
- **Shorter names:** Remove "agent-8-" prefix
- **README in each folder:** Explains contents
- **Consistent structure:** Matches agent-9 folder pattern

### 4. Git History Preservation
- **Use `git mv`:** Preserves history
- **Move in logical batches:** Easier to review
- **Update references incrementally:** Test after each batch

---

## Migration Strategy

### Phase 1: Create Structure (Safe, No Git History Risk)
1. Create all folders: `agents/agent-8/{protocol,weekly,research,scripts,logs}/`
2. Create all README.md files with content
3. Create `QUICK-START.md` with essential commands
4. **Checkpoint:** Commit structure creation

### Phase 2: Move Documentation (Preserve Git History)
1. **Batch 1 - Protocol docs:** Move from `docs/planning/` to `agents/agent-8/protocol/`
   - Use `git mv` for each file
   - Rename (remove "agent-8-" prefix)
   - Commit batch
2. **Batch 2 - Weekly docs:** Move from `docs/planning/` to `agents/agent-8/weekly/`
   - Same process
3. **Batch 3 - Research docs:** Move from `docs/research/` to `agents/agent-8/research/`
   - Same process
4. **Checkpoint:** All docs moved, git history preserved

### Phase 3: Move Scripts (Critical - Test Each)
1. **Batch 1 - Core scripts:** Move to `agents/agent-8/scripts/core/`
   - Test each script after move
   - Update shebangs if needed
2. **Batch 2 - PR scripts:** Move to `agents/agent-8/scripts/pr/`
3. **Batch 3 - Recovery scripts:** Move to `agents/agent-8/scripts/recovery/`
4. **Batch 4 - Setup scripts:** Move to `agents/agent-8/scripts/setup/`
5. **Batch 5 - Legacy & tests:** Move to `agents/agent-8/scripts/{legacy,tests}/`
6. **Checkpoint:** All scripts moved and tested

### Phase 4: Move Logs (Safe)
1. Move `git_operations_log/` contents to `agents/agent-8/logs/`
2. Keep `git_operations_log/` as symlink (for backward compatibility)
3. **Checkpoint:** Logs moved

### Phase 5: Update References (Critical)
1. **Search & update all references:**
   - `docs/planning/agent-8-*.md` → `agents/agent-8/protocol/*.md`
   - `docs/research/agent-8-*.md` → `agents/agent-8/research/*.md`
   - Script paths in documentation
2. **Update scripts that reference other scripts:**
   - `ai_commit.sh` → update path to `safe_push.sh`
   - `safe_push.sh` → update path to `should_use_pr.sh`
3. **Create redirects at old locations (optional):**
   - Small stub files pointing to new location
4. **Checkpoint:** All references updated

### Phase 6: Validation & Testing
1. Run all Agent 8 scripts to verify they work
2. Check all documentation links
3. Run validation bundle
4. Test a full commit workflow (end-to-end)
5. **Checkpoint:** Everything validated

### Phase 7: Documentation & Rollout
1. Update main project README.md
2. Update `.github/copilot-instructions.md`
3. Update `docs/AGENT_WORKFLOW_MASTER_GUIDE.md`
4. Update `docs/git-workflow-ai-agents.md`
5. Announce in SESSION_LOG.md
6. **Final commit:** Agent 8 consolidation complete

---

## Risk Mitigation

### Risk 1: Script Paths Break
**Mitigation:**
- Test each script after move
- Update paths incrementally
- Keep old locations temporarily (deprecate later)
- Use absolute paths in critical scripts

### Risk 2: Git History Lost
**Mitigation:**
- Always use `git mv` (not mv + git add)
- Commit each batch separately
- Test `git log --follow` after each move
- Keep backups of original locations

### Risk 3: Other Agents Can't Find Files
**Mitigation:**
- Create comprehensive README.md at `agents/agent-8/`
- Update all documentation with new paths
- Create redirects at old locations
- Announce change in SESSION_LOG.md

### Risk 4: CI/Automation Breaks
**Mitigation:**
- Search for all script references in .github/workflows/
- Update workflow files before moving scripts
- Test CI after script moves
- Use relative paths where possible

---

## Success Criteria

- [ ] All 12 Agent 8 docs moved to `agents/agent-8/`
- [ ] All 13 scripts moved and tested
- [ ] All 3 logs moved
- [ ] Git history preserved (`git log --follow` works)
- [ ] All references updated (0 broken links)
- [ ] All scripts functional (end-to-end test passes)
- [ ] Main README.md updated
- [ ] Documentation updated
- [ ] Easy to find: `agents/agent-8/README.md` is clear entry point

---

## Timeline Estimate

- **Phase 1 (Structure):** 30 minutes
- **Phase 2 (Docs):** 1 hour
- **Phase 3 (Scripts):** 2 hours (testing critical)
- **Phase 4 (Logs):** 15 minutes
- **Phase 5 (References):** 1.5 hours
- **Phase 6 (Validation):** 1 hour
- **Phase 7 (Documentation):** 1 hour

**Total:** ~7 hours (spread across multiple commits for safety)

---

## Next Steps

1. **Review this plan** with user
2. **Get approval** to proceed
3. **Execute Phase 1** (structure creation - safe)
4. **Commit and validate** before proceeding
5. **Execute remaining phases** incrementally with checkpoints

---

## References

- [AGENT-8-INCIDENT-ANALYSIS.md](./AGENT-8-INCIDENT-ANALYSIS.md) - Root cause of recent issues
- [MIGRATION-STATUS.md](./MIGRATION-STATUS.md) - Overall migration status
- Agent 9 folder structure (as reference model)
