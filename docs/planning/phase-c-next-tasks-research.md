# Phase C Next Tasks Research

**Date:** 2026-01-10
**Agent:** Main Agent (Phase C)
**Purpose:** Prepare for Phase C.2 and C.3 tasks

---

## Current Progress (Phase C.1 Complete)

### Completed This Session

| Task | Status | Commit | Key Outcome |
|------|--------|--------|-------------|
| TASK-300 | ✅ Done | 18cfaf8 | Semantic metadata in 3 README indexes |
| TASK-301 | ✅ Done | 22a8730 | 4 redirect stubs removed, check script created |
| TASK-306 | ✅ Done | f7be195 | Duplicate docs checker created |

### Metrics After Phase C.1

- **Files:** 289 markdown files
- **Links:** 729 internal links, 0 broken
- **Root files:** 9 (target: ≤10) ✅
- **docs/ root files:** 3 (target: ≤5) ✅

---

## Phase C.2 Tasks (Next Session)

### TASK-302: Clean Redirect Stubs with References

**Problem:** 13 redirect stubs remain that have active references to them.

**Approach:**
1. Use `scripts/check_redirect_stubs.py` to identify stubs and their references
2. For each stub, update references to point to canonical location
3. Remove the stub after all references updated
4. Verify links

**Estimated Effort:** 2-3 hours (many files to update)

**Priority Files (by reference count):**
1. `docs/getting-started/project-overview.md` (24 refs) - redirect to architecture/
2. `docs/reference/api-reference.md` (14 refs) - redirect to reference/api.md
3. `docs/reference/vba-guide.md` (12 refs) - redirect to contributing/
4. `docs/planning/production-roadmap.md` (11 refs) - redirect to _archive/

### TASK-303: Add Front-Matter Template

**Problem:** Docs lack metadata for automated governance (owner, status, last updated).

**Proposed Template:**
```markdown
---
owner: Agent 9 / Main Agent / User
status: active | deprecated | draft
last_updated: 2026-01-10
doc_type: guide | reference | tutorial | index
complexity: beginner | intermediate | advanced
---
```

**Implementation:**
1. Create template in `docs/contributing/doc-template.md`
2. Add front-matter to key docs (start with indexes)
3. Create validation script `scripts/check_doc_frontmatter.py`
4. Optionally add pre-commit check

**Priority Docs:**
- docs/README.md (main index)
- docs/agents/README.md (agent hub)
- docs/research/README.md (research index)
- docs/TASKS.md (task board)

---

## Phase C.3 Tasks (Future Session)

### TASK-304: Resolve Duplicate Doc Names

**Problem:** 1 true duplicate found (ui-layout-final-decision.md in two places).

**Files:**
- `docs/research/ui-layout-final-decision.md` (27,968 bytes)
- `docs/planning/ui-layout-final-decision.md` (46,418 bytes)

**Resolution:**
1. Compare content - determine which is more complete
2. Archive the less complete version
3. Update references

### TASK-305: Re-run Navigation Study

**Purpose:** Validate if semantic metadata improves AI agent navigation.

**Baseline (from previous study):**
- Time speedup: 1.0x (no improvement)
- Token reduction: -17% (increased)
- Error rate: 62.5%

**Expected After Semantic Metadata:**
- Time speedup: >1.2x
- Token reduction: >20%
- Error rate: <50%

**Method:**
1. Use existing scripts: `scripts/measure_agent_navigation.sh`
2. Run 30 trials with updated semantic indexes
3. Compare to baseline

---

## Innovation Ideas

### 1. Automated Reference Updater

Create a script that:
- Finds all references to a redirect stub
- Calculates the new path (following the redirect)
- Updates all references automatically
- Removes the stub

This would make TASK-302 much faster.

### 2. Doc Freshness Dashboard

Create a report showing:
- Docs not updated in 30+ days
- Docs with no owner
- Docs with broken cross-references
- Docs with missing front-matter

### 3. Context Budget Calculator

For AI agents, calculate:
- Total tokens to read all docs in a folder
- "Essential" subset (indexes + key docs)
- Context savings from semantic navigation

---

## Research Questions

1. **Do semantic indexes actually help AI agents?**
   - Phase C.1 added metadata to 3 indexes
   - Need to measure impact (TASK-305)

2. **What's the optimal front-matter schema?**
   - Too many fields = maintenance burden
   - Too few fields = limited automation

3. **Should we auto-generate indexes?**
   - Current: hand-written with semantic descriptions
   - Alternative: script that scans files and generates table
   - Trade-off: consistency vs. quality of descriptions

---

## Dependencies

| Task | Depends On | Blocks |
|------|------------|--------|
| TASK-302 | None | TASK-305 |
| TASK-303 | None | None |
| TASK-304 | None | None |
| TASK-305 | TASK-302 | Phase C complete |

---

## Session Planning

### Next Session Priority

1. **TASK-302** (redirect stubs) - highest impact, unblocks TASK-305
2. **TASK-303** (front-matter) - enables future automation
3. Research for automated reference updater (innovation)

### Success Criteria for Next Session

- [ ] 13 → <5 redirect stubs remaining
- [ ] Front-matter template created
- [ ] At least 5 docs have front-matter
- [ ] All links still valid

---

**Prepared by:** Main Agent
**Session:** 2026-01-10 (Phase C Planning)
