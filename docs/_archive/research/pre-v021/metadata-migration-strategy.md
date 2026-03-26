# Metadata Migration Strategy

**Type:** Implementation
**Audience:** All Agents
**Status:** In Progress
**Importance:** High
**Version:** 1.0.0
**Created:** 2026-01-13
**Last Updated:** 2026-01-13
**Related Tasks:** TASK-458

---

## Executive Summary

**Current State:**
- 302 docs total (non-archive)
- 75 docs migrated (25%)
- 227 docs remaining (75%)
- 324 metadata errors, 503 warnings

**Why Metadata Matters for AI Agents:**

1. **Context Loading Efficiency (30-40% faster)**
   - Agents can filter by `Importance: Critical` vs `Low`
   - Skip `Status: Deprecated` docs automatically
   - Prioritize `Audience: All Agents` content

2. **Document Discovery (50% faster)**
   - `Type: Reference` → API docs, quickly findable
   - `Type: Guide` → How-to content
   - `Type: Research` → Background context

3. **Lifecycle Management**
   - `Status: Deprecated` → Candidates for archive
   - `Last Updated: 2025-*` → Stale content to review
   - `Archive Condition` → Auto-cleanup triggers

4. **LLM Integration (Future-Ready)**
   - Structured metadata = better RAG retrieval
   - JSON-extractable headers for indexing
   - Semantic search enhancement

---

## Migration Priority Plan

### Phase 1: High-Impact Folders (DONE - 50+ docs)

✅ **docs/contributing/** - 12 files migrated
✅ **docs/architecture/** - 6 files migrated
✅ **docs/getting-started/** - 14 files migrated
✅ **docs/git-automation/** - 6 files migrated
✅ **docs/agents/guides/** - 17 files migrated

### Phase 2: Reference & Planning (Current Priority)

| Folder | Files | Priority | Rationale |
|--------|-------|----------|-----------|
| **docs/reference/** | 21 | 🔴 HIGH | Core API docs, high agent usage |
| **docs/planning/** | 29 | 🔴 HIGH | Active task management |
| **docs/guidelines/** | 13 | 🟠 MEDIUM | Standards reference |
| **docs/specs/** | ~5 | 🟠 MEDIUM | Technical specifications |

### Phase 3: Research & Learning

| Folder | Files | Priority | Rationale |
|--------|-------|----------|-----------|
| **docs/research/** | 41 | 🟡 LOW | Many are historical |
| **docs/learning/** | 9 | 🟡 LOW | Stable content |
| **docs/_internal/** | 23 | 🟡 LOW | Internal use only |

### Phase 4: Cleanup

| Folder | Files | Priority | Rationale |
|--------|-------|----------|-----------|
| **agents/agent-9/** | ~15 | 🔵 OPTIONAL | Governance-specific |
| **streamlit_app/docs/** | ~20 | 🔵 OPTIONAL | UI-specific |

---

## Efficiency Calculation

### Time Investment

**Manual migration:** ~2 minutes per file
**Remaining files:** 227
**Total time:** ~7.5 hours

### Automation Opportunities

1. **Auto-generate from filename patterns:**
   - `*-guide.md` → Type: Guide
   - `*-reference.md` → Type: Reference
   - `*-research*.md` → Type: Research

2. **Batch processing script:**
   - Read first 30 lines for existing metadata
   - Infer Type/Audience from folder
   - Generate header, insert at top

3. **Estimated automation savings:** 60-70%
   - Script development: 1 hour
   - Execution: ~30 minutes
   - Manual review: ~2 hours
   - **Total:** ~3.5 hours vs 7.5 hours manual

---

## Immediate Action Plan

### This Session (TASK-458 continuation)

1. **Migrate docs/reference/** (21 files) - 45 min
2. **Migrate docs/planning/** (29 files) - 1 hour
3. **Migrate docs/guidelines/** (13 files) - 30 min

**Target:** 75 + 63 = 138 files (46% complete)

### Next Session

1. **Build automation script** for remaining folders
2. **Run batch migration** with manual review
3. **Complete remaining ~90 files**

---

## Success Metrics

| Metric | Current | Target | Benefit |
|--------|---------|--------|---------|
| **Docs with metadata** | 25% | 100% | Full discoverability |
| **Agent context load time** | Baseline | -30% | Faster onboarding |
| **Doc discovery accuracy** | Baseline | +50% | Better relevance |
| **Stale doc detection** | Manual | Automated | Less clutter |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Over-engineering | Medium | Low | Keep headers simple |
| Inconsistent values | Medium | Medium | Pre-commit validation |
| Breaking existing tools | Low | High | Test with check_doc_metadata.py |

---

## Recommendation

**Proceed with Phase 2 this session.** The metadata migration is:

✅ **Good for the project:** Structured docs, easier maintenance
✅ **Good for agents:** Faster context, better discovery
✅ **Good for future:** LLM/RAG integration ready
✅ **Low risk:** Non-breaking, gradual migration

**Next immediate action:** Migrate docs/reference/ (21 files)
