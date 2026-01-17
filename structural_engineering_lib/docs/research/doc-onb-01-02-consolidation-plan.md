# DOC-ONB-01/02 Guide Consolidation Plan

**Type:** Research
**Audience:** All Agents
**Status:** In Progress
**Importance:** High
**Created:** 2026-01-13
**Last Updated:** 2026-01-13
**Related Tasks:** DOC-ONB-01, DOC-ONB-02
**Archive Condition:** Archive after DOC-ONB-02 complete

---

## Current State Analysis

### 4 Onboarding Guides (1,404 lines total)

| Guide | Lines | Purpose | Key Content |
|-------|-------|---------|-------------|
| **agent-bootstrap.md** | 115 | Quick start | First 30s commands, required context, API checklist |
| **agent-workflow-master-guide.md** | 704 | Comprehensive reference | Decision trees, patterns, troubleshooting |
| **agent-quick-reference.md** | 272 | Cheat sheet | Essential commands, emergency procedures |
| **agent-onboarding.md** | 313 | First session walkthrough | Pre-session checklist, git rules, common mistakes |

### Overlap Analysis

**High Overlap (appears in 3-4 docs):**
- `agent_start.sh` command and usage
- Git workflow rules ("never use manual git commands")
- Required reading lists
- Common mistakes/pitfalls
- Automation-first mentality

**Unique Content Worth Preserving:**
- **Bootstrap:** API touchpoints checklist (unique)
- **Master Guide:** Comprehensive decision trees, recovery procedures (authoritative)
- **Quick Ref:** Printable cheat sheet format, emergency commands table (unique format)
- **Onboarding:** Step-by-step first task workflow (redundant, covered in others)

---

## Consolidation Options Evaluated

### Option A: Single Comprehensive Guide ❌
**Approach:** Merge all 4 into one document

**Pros:**
- Single source of truth
- No navigation between docs

**Cons:**
- Would be 1,400+ lines (too long)
- Overwhelming for quick reference
- Different audiences need different depths

**Verdict:** NOT RECOMMENDED

---

### Option B: Two-Guide System ⚠️
**Approach:**
1. Quick Start Guide (250 lines) - Merge bootstrap + onboarding
2. Complete Reference (750 lines) - Keep master-guide, absorb quick-ref

**Pros:**
- Clear separation: quick start vs deep dive
- Easier navigation than 4 docs
- ~35% line reduction

**Cons:**
- Loses quick-ref card format (printable cheat sheet)
- No middle ground between 250 and 750 lines

**Verdict:** ACCEPTABLE but not optimal

---

### Option C: Three-Guide Hierarchy ✅ RECOMMENDED
**Approach:**
1. **Quick Start** (~115 lines) - agent-bootstrap.md (minimal edits)
2. **Quick Reference** (~280 lines) - agent-quick-reference.md (add onboarding steps)
3. **Complete Guide** (~720 lines) - agent-workflow-master-guide.md (minimal edits)

**Archive:** agent-onboarding.md (313 lines, content preserved in others)

**Pros:**
- Preserves different use cases (30s start → cheat sheet → deep dive)
- Minimal disruption to existing well-structured content
- Clear progression path for agents
- Maintains printable cheat sheet format
- 22% reduction (1,404 → 1,115 lines, archive 313)

**Cons:**
- Still 3 documents (but intentionally serving different needs)

**Verdict:** RECOMMENDED - Balanced approach

---

## Recommended Implementation Plan

### Phase 1: Enhance Quick Reference (DOC-ONB-01)

**File:** `docs/agents/guides/agent-quick-reference.md`

**Changes:**
1. Add "First Session Workflow" section from agent-onboarding.md
2. Add pre-session checklist (condensed to bullet list)
3. Add "After Your First Commit" section
4. Update cross-links at top to show hierarchy

**Estimated additions:** +10-15 lines
**New size:** ~285 lines

---

### Phase 2: Add Cross-Links (DOC-ONB-02)

**Files:** agent-bootstrap.md, agent-quick-reference.md, agent-workflow-master-guide.md

**Changes to each file (top section):**
```markdown
## 📚 Guide Hierarchy

**You are here:** [Current Doc Name]

| Need | Guide | Use When |
|------|-------|----------|
| **Quick Start** | [agent-bootstrap.md](../../getting-started/agent-bootstrap.md) | First 30 seconds, immediate productivity |
| **Quick Reference** | [agent-quick-reference.md](agent-quick-reference.md) | Cheat sheet, emergency commands, first session |
| **Complete Guide** | [agent-workflow-master-guide.md](agent-workflow-master-guide.md) | Decision trees, troubleshooting, patterns |
```

**Estimated additions:** +15 lines per file

---

### Phase 3: Archive agent-onboarding.md

**Action:** Move to `docs/_archive/2026-01/agent-onboarding.md`

**Reason:** Content now preserved in:
- First session workflow → agent-quick-reference.md
- Git rules → All 3 guides (canonical in master-guide)
- Common mistakes → master-guide troubleshooting section

**Safe to archive:** Yes, 0 unique content remaining after Phase 1+2

---

### Phase 4: Update References (DOC-ONB-02)

**Files to update:**
- `.github/copilot-instructions.md` - Update "Quick Start" section
- `docs/README.md` - Update agent onboarding links
- `docs/agents/README.md` - Update guide references
- Any other files linking to agent-onboarding.md

**Tool:** Use `grep_search` to find all references, then `multi_replace_string_in_file`

---

## Before/After Comparison

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **Total guides** | 4 | 3 | -25% |
| **Total lines** | 1,404 | 1,115 | -21% |
| **Archived lines** | 0 | 313 | +313 |
| **Active lines** | 1,404 | 1,115 | -289 (-21%) |
| **Quick start lines** | 115 | 115 | 0% |
| **Cheat sheet lines** | 272 | ~285 | +5% |
| **Complete guide lines** | 704 | ~720 | +2% |

**Impact:**
- 21% reduction in active onboarding content
- Clearer hierarchy (bootstrap → quick-ref → master-guide)
- Preserved all unique content
- Improved first session experience (quick-ref now has walkthrough)

---

## Risk Analysis

### Low Risk Changes:
- ✅ Adding cross-links (non-breaking)
- ✅ Archiving agent-onboarding.md (all content preserved)
- ✅ Enhancing quick-ref with onboarding steps (additive)

### Medium Risk Changes:
- ⚠️ Updating references (many files may link to agent-onboarding.md)
- **Mitigation:** Use `safe_file_move.py` to auto-update links

### High Risk Changes:
- None identified

---

## Time Estimates

| Phase | Task | Estimate |
|-------|------|----------|
| **Phase 1** | Enhance quick-ref with onboarding content | 45-60 min |
| **Phase 2** | Add cross-links to 3 guides | 20-30 min |
| **Phase 3** | Archive agent-onboarding.md | 5 min |
| **Phase 4** | Update references | 30-45 min |
| **Testing** | Link validation, readability check | 15-20 min |
| **Total** | | **2.0-2.5 hrs** |

**Original estimate:** 3-4 hrs (conservative)
**Revised estimate:** 2.0-2.5 hrs (based on detailed analysis)

---

## Success Criteria

**Quantitative:**
- [ ] 3 guides remain (bootstrap, quick-ref, master-guide)
- [ ] 1 guide archived (agent-onboarding.md)
- [ ] 20%+ line reduction achieved
- [ ] 0 broken links after consolidation
- [ ] All 3 guides have cross-link navigation

**Qualitative:**
- [ ] Clear hierarchy: quick start → cheat sheet → deep dive
- [ ] First session workflow preserved in quick-ref
- [ ] All unique content from agent-onboarding.md preserved
- [ ] No duplicate content across the 3 guides

---

## Implementation Sequence

1. ✅ Research and analysis (this document)
2. Create backup commits before changes
3. Phase 1: Enhance quick-ref
4. Commit: "feat(docs): add first session workflow to quick-reference"
5. Phase 2: Add cross-links
6. Commit: "docs: add guide hierarchy navigation to onboarding docs"
7. Phase 3: Archive agent-onboarding.md
8. Commit: "refactor: archive agent-onboarding.md after consolidation"
9. Phase 4: Update all references
10. Commit: "docs: update references after onboarding guide consolidation"
11. Validation: Link check, readability review
12. Final commit: "docs: complete DOC-ONB-01/02 guide consolidation"

**Total commits:** 5-6 meaningful commits

---

## Next Steps

1. Review this plan with user
2. Execute Phase 1 (enhance quick-ref)
3. Execute Phase 2 (cross-links)
4. Execute Phase 3 (archive)
5. Execute Phase 4 (update references)
6. Validate and document results

---

**Status:** Ready for execution
**Approval:** Awaiting user confirmation
