# Agent 8 Consolidation Plan

**Date:** 2026-01-10
**Purpose:** Consolidate Agent 8 docs into `docs/agents/` (guides + sessions) while keeping scripts in `scripts/` and logs in `git_operations_log/` (indexed and linked).
**Owner:** Agent 9 (Governance)
**Status:** 📋 Planning Complete

---

## Executive Summary

Agent 8 files are currently scattered across:
- `docs/planning/` (7 files)
- `docs/research/` (5 files)
- `scripts/` (13 automation scripts)
- `git_operations_log/` (3 operational logs)

**Goal:** Consolidate Agent 8 documentation into `docs/agents/` (guides + sessions) with clear entry points, preserve git history, and avoid breaking shared automation in `scripts/`.

---

## Inventory of Agent 8 Files

### Documentation Files (12 total)

**Core Protocol & Guides (docs/planning/ → docs/agents/guides/)**
1. `agent-8-tasks-git-ops.md` (1,320 lines) - Core mission & protocol
2. `agent-8-mistakes-prevention-guide.md` (1,096 lines) - Historical mistakes DB
3. `agent-8-implementation-guide.md` - Implementation instructions
4. `agent-8-multi-agent-coordination.md` - Multi-agent workflow

**Weekly Summaries (docs/planning/ → docs/agents/sessions/2026-01/)**
5. `agent-8-week1-completion-summary.md` - Week 1 results
6. `agent-8-week2-plan.md` - Week 2 plan
7. `agent-8-git-operations-log.md` - Log format specification (move to guides)

**Research & Analysis (remain in docs/research/)**
8. `agent-8-week1-summary.md` - Week 1 research summary
9. `agent-8-week1-reality-check.md` - Week 1 reality check
10. `agent-8-week1-implementation-blocker.md` - Week 1 blockers
11. `agent-8-implementation-priority.md` - Implementation priorities
12. `agent-8-optimization-research.md` - Optimization research

### Automation Scripts (13 total)

**Core Workflow (stay in scripts/, index in docs/agents/guides/agent-8-automation.md)**
1. `ai_commit.sh` (2.6K) - Entry point for commits
2. `safe_push.sh` (13K) - Core 7-step workflow
3. `safe_push_v2.sh` (11K) - Version 2 (backup)
4. `should_use_pr.sh` (13K) - PR decision logic
5. `should_use_pr_old.sh` (7.6K) - Old version (backup)

**PR Management (stay in scripts/)**
6. `create_task_pr.sh` (1.8K) - Start PR workflow
7. `finish_task_pr.sh` (3.0K) - Submit PR

**Recovery & Validation (stay in scripts/)**
8. `recover_git_state.sh` (3.4K) - Emergency recovery
9. `validate_git_state.sh` (8.3K) - State validation

**Environment Setup (stay in scripts/)**
10. `agent_setup.sh` (8.1K) - Session setup
11. `agent_preflight.sh` (10K) - Pre-task checks
12. `worktree_manager.sh` (15K) - Worktree management

**Testing (stay in scripts/)**
13. `test_should_use_pr.sh` (7.6K) - PR decision tests

**Related Test Scripts (keep in scripts/, link from agent-8/)**
- `test_merge_conflicts.sh` - Merge conflict tests
- `test_branch_operations.sh` - Branch operation tests
- `ci_monitor_daemon.sh` - CI monitoring

### Operational Logs (3 files)

**Keep in git_operations_log/ (index from docs/agents/guides/)**
1. `2026-01.log` - January operations log
2. `2026-01-08.md` - Jan 8 operations
3. `2026-01-08-operations.log` - Jan 8 detailed log

---

## Proposed Structure

```
docs/agents/
├── README.md
├── guides/
│   ├── agent-8-git-ops.md
│   ├── agent-8-mistakes-prevention-guide.md
│   ├── agent-8-implementation-guide.md
│   ├── agent-8-multi-agent-coordination.md
│   ├── agent-8-operations-log-spec.md
│   ├── agent-8-automation.md
│   └── agent-8-quick-start.md
└── sessions/
    └── 2026-01/
        ├── agent-8-week1-completion-summary.md
        └── agent-8-week2-plan.md

docs/research/
├── agent-8-week1-summary.md
├── agent-8-week1-reality-check.md
├── agent-8-week1-implementation-blocker.md
├── agent-8-implementation-priority.md
└── agent-8-optimization-research.md

scripts/               # No move (keep automation stable)
git_operations_log/    # No move (index from docs/agents/guides/)
```

---

## Governance Alignment

- Follows `RULE 3.2` (agent-specific docs live in `docs/agents/`).
- Keeps automation in `scripts/` per `RULE 4.2`.
- Avoids symlinks for cross-platform safety.

---

## Key Improvements

### 1. Discoverability
- **Single entry point:** `docs/agents/guides/agent-8-quick-start.md`
- **Quick reference:** `docs/agents/guides/agent-8-git-ops.md` (protocol)
- **Organized by purpose:** guides, sessions, research, scripts (indexed)

### 2. Script Organization
- **Stable paths:** scripts stay in `scripts/` (no breakage)
- **Single index:** `docs/agents/guides/agent-8-automation.md`
- **Legacy preserved:** keep legacy scripts where they are (documented)

### 3. Documentation Clarity
- **Clear naming:** keep `agent-8-` prefix for search and context
- **README hubs:** use `docs/agents/README.md` + guides for entry
- **Consistent structure:** aligns with `FOLDER_STRUCTURE_GOVERNANCE.md`

### 4. Git History Preservation
- **Use `git mv`:** Preserves history
- **Move in logical batches:** Easier to review
- **Update references incrementally:** Test after each batch

---

## Migration Strategy

### Phase 1: Create Doc Entry Points (Safe)
1. Ensure `docs/agents/guides/` and `docs/agents/sessions/2026-01/` exist.
2. Add `docs/agents/guides/agent-8-quick-start.md` (entry point).
3. Add `docs/agents/guides/agent-8-automation.md` (script index).
4. **Checkpoint:** Commit entry points.

### Phase 2: Move Protocol & Guides (Preserve Git History)
1. Move from `docs/planning/` → `docs/agents/guides/` using `git mv`:
   - `agent-8-tasks-git-ops.md` → `agent-8-git-ops.md`
   - `agent-8-mistakes-prevention-guide.md` → `agent-8-mistakes-prevention-guide.md`
   - `agent-8-implementation-guide.md` → `agent-8-implementation-guide.md`
   - `agent-8-multi-agent-coordination.md` → `agent-8-multi-agent-coordination.md`
   - `agent-8-git-operations-log.md` → `agent-8-operations-log-spec.md`
2. **Checkpoint:** Guides moved + links updated.

### Phase 3: Move Weekly Summaries (Preserve Git History)
1. Move from `docs/planning/` → `docs/agents/sessions/2026-01/`:
   - `agent-8-week1-completion-summary.md`
   - `agent-8-week2-plan.md`
2. **Checkpoint:** Weekly docs moved + links updated.

### Phase 4: Research Docs (No Move)
1. Keep research in `docs/research/` for discoverability.
2. Add cross-links from `docs/agents/guides/agent-8-quick-start.md`.
3. **Checkpoint:** Research index links added.

### Phase 5: References + Validation
1. Update references across repo to the new guide/session paths.
2. Keep scripts in `scripts/` and reference them from `agent-8-automation.md`.
3. Run validation bundle + link checks.
4. **Final commit:** Agent 8 consolidation complete.

---

## Risk Mitigation

### Risk 1: Script References Drift
**Mitigation:**
- Keep scripts in `scripts/` (no path changes)
- Centralize references in `docs/agents/guides/agent-8-automation.md`
- Update any docs that hardcode old script paths

### Risk 2: Git History Lost
**Mitigation:**
- Always use `git mv` (not mv + git add)
- Commit each batch separately
- Test `git log --follow` after each move
- Keep backups of original locations

### Risk 3: Other Agents Can't Find Files
**Mitigation:**
- Create a clear entry point at `docs/agents/guides/agent-8-quick-start.md`
- Update all documentation with new paths
- Create redirects at old locations
- Announce change in SESSION_LOG.md

### Risk 4: CI/Automation Breaks
**Mitigation:**
- No script moves (CI paths remain stable)
- Only update documentation references

---

## Success Criteria

- [ ] Core Agent 8 guides moved to `docs/agents/guides/`
- [ ] Weekly summaries moved to `docs/agents/sessions/2026-01/`
- [ ] Research docs remain in `docs/research/` with cross-links
- [ ] Scripts remain in `scripts/` and are indexed in `agent-8-automation.md`
- [ ] Logs remain in `git_operations_log/` and are linked
- [ ] Git history preserved (`git log --follow` works)
- [ ] All references updated (0 broken links)
- [ ] All scripts functional (end-to-end test passes)
- [ ] Main README.md updated
- [ ] Documentation updated
- [ ] Easy to find: `docs/agents/guides/agent-8-quick-start.md` is clear entry point

---

## Timeline Estimate

- **Phase 1 (Entry points):** 30 minutes
- **Phase 2 (Guides):** 1 hour
- **Phase 3 (Weekly):** 30 minutes
- **Phase 4 (Research links):** 30 minutes
- **Phase 5 (References + validation):** 1.5 hours

**Total:** ~4 hours (spread across multiple commits for safety)

---

## Next Steps

1. **Review this plan** with user
2. **Get approval** to proceed
3. **Execute Phase 1** (entry points - safe)
4. **Commit and validate** before proceeding
5. **Execute remaining phases** incrementally with checkpoints

---

## References

- [AGENT-8-INCIDENT-ANALYSIS.md](./AGENT-8-INCIDENT-ANALYSIS.md) - Root cause of recent issues
- [MIGRATION-STATUS.md](./MIGRATION-STATUS.md) - Overall migration status
- Agent 9 folder structure (as reference model)
