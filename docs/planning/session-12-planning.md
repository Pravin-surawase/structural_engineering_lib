# Session 12+ Planning Document

**Type:** Research
**Audience:** All Agents
**Status:** Active
**Importance:** High
**Version:** 1.0.0
**Created:** 2026-01-11
**Last Updated:** 2026-01-11
**Related Tasks:** Root file reduction, Governance compliance

---

## I. Priority 1: Root File Reduction (14 → 10)

### Current Root Files (14)

| File | Size | Purpose | Keep/Move |
|------|------|---------|-----------|
| AUTHORS.md | 127B | Author credits | 🔀 MOVE → docs/contributing/ |
| CHANGELOG.md | 40KB | Version history | ✅ KEEP (standard) |
| CITATION.cff | 362B | Citation metadata | 🔀 MOVE → .github/ |
| CODE_OF_CONDUCT.md | 343B | Community guidelines | ✅ KEEP (standard) |
| CONTRIBUTING.md | 8KB | Contribution guide | ✅ KEEP (standard) |
| LICENSE | varies | Main license | ✅ KEEP (required) |
| LICENSE_ENGINEERING.md | 2KB | Engineering license | 🔀 MOVE → docs/legal/ |
| README.md | 17KB | Project overview | ✅ KEEP (required) |
| SECURITY.md | 449B | Security policy | 🔀 MOVE → .github/ |
| SUPPORT.md | 436B | Support info | 🔀 MOVE → .github/ |
| colab_workflow.ipynb | 251KB | Colab notebook | 🔀 MOVE → docs/getting-started/ |
| index.json | 5KB | Agent index | 🤔 CONSOLIDATE with index.md |
| index.md | 3KB | Project index | 🤔 CONSOLIDATE or keep |
| llms.txt | 1KB | LLM info | 🤔 REVIEW necessity |

### Research: GitHub Standard Files

**Files that MUST be at root (per GitHub):**
- README.md ✅
- LICENSE ✅
- CHANGELOG.md ✅
- CONTRIBUTING.md ✅
- CODE_OF_CONDUCT.md ✅

**Files that can be in .github/ (GitHub recognizes both):**
- SECURITY.md → .github/SECURITY.md ✅
- SUPPORT.md → .github/SUPPORT.md ✅
- CITATION.cff → .github/CITATION.cff ⚠️ (GitHub may not recognize)

**Custom files (our decision):**
- AUTHORS.md → docs/contributing/AUTHORS.md
- LICENSE_ENGINEERING.md → docs/legal/LICENSE_ENGINEERING.md
- colab_workflow.ipynb → docs/getting-started/colab-workflow.ipynb
- index.json/index.md → Consolidate or move

### Proposed Final Root (10 files)

```
Root after cleanup:
├── README.md         ← Required
├── LICENSE           ← Required
├── CHANGELOG.md      ← Standard
├── CONTRIBUTING.md   ← Standard
├── CODE_OF_CONDUCT.md ← Standard
├── pyproject.toml    ← Python config (when added)
├── llms.txt          ← LLM context
├── index.md          ← Project index (consolidate index.json into this)
└── (2 slots reserved for future needs)

Moved to .github/:
├── SECURITY.md
├── SUPPORT.md
└── CITATION.cff

Moved to docs/:
├── docs/contributing/AUTHORS.md
├── docs/legal/LICENSE_ENGINEERING.md
└── docs/getting-started/colab-workflow.ipynb

Consolidated:
├── index.json → Merge into index.md or agents/index.json
```

### Migration Commands

```bash
# Phase 1: Move to .github/
.venv/bin/python scripts/safe_file_move.py SECURITY.md .github/SECURITY.md
.venv/bin/python scripts/safe_file_move.py SUPPORT.md .github/SUPPORT.md
.venv/bin/python scripts/safe_file_move.py CITATION.cff .github/CITATION.cff

# Phase 2: Move to docs/
.venv/bin/python scripts/safe_file_move.py AUTHORS.md docs/contributing/AUTHORS.md
.venv/bin/python scripts/safe_file_move.py LICENSE_ENGINEERING.md docs/legal/LICENSE_ENGINEERING.md
.venv/bin/python scripts/safe_file_move.py colab_workflow.ipynb docs/getting-started/colab-workflow.ipynb

# Phase 3: Consolidate index files
# Manually merge index.json content into index.md or agents/index.json
```

### Risk Assessment

| Move | Risk | Mitigation |
|------|------|------------|
| SECURITY.md → .github/ | LOW | GitHub recognizes .github/SECURITY.md |
| SUPPORT.md → .github/ | LOW | GitHub recognizes .github/SUPPORT.md |
| CITATION.cff → .github/ | MEDIUM | May affect citation detection |
| AUTHORS.md → docs/ | LOW | Update any references |
| colab_workflow.ipynb → docs/ | MEDIUM | Update Colab links |
| index.json consolidation | MEDIUM | Verify agents/ uses work |

---

## II. Priority 2: Document Metadata Adoption

### Documents Needing Metadata

**Recently created (Session 11-12):**
- ✅ session-11-review-and-analysis.md (has metadata)
- ⏳ session-11-structure-issues-analysis.md
- ⏳ session-11-migration-lessons.md
- ⏳ FOLDER_STRUCTURE_GOVERNANCE.md

**Critical documents (should have metadata):**
- docs/TASKS.md
- docs/ai-context-pack.md
- docs/agents/guides/agent-workflow-master-guide.md
- All docs/research/*.md files

### Automation Opportunity

Create script: `scripts/add_doc_metadata.py`
```python
# Scans docs for missing metadata
# Suggests/adds metadata template to files
# Validates existing metadata format
```

---

## III. Priority 3: Quarterly Governance Audit System

### Proposal

1. Add `scripts/quarterly_governance_audit.py`
   - Runs full compliance check
   - Compares against previous quarter
   - Generates audit report

2. Schedule reminder in TASKS.md
   - Q2 2026: 2026-04-11
   - Q3 2026: 2026-07-11
   - Q4 2026: 2026-10-11

3. Add to pre-release checklist
   - Must pass governance check before major releases

---

## IV. Research: Preventing Future Issues

### Lessons from Session 11 Review

| Issue | Prevention |
|-------|------------|
| Claims without verification | Add `verify-claims` step to session end |
| Spec not updated after migration | Add "update spec" to migration checklist |
| Leftover duplicate files | Run `git status` before closing session |
| Validator-spec mismatch | Write spec first, then implement validator |

### New Workflow Additions

1. **Verify-Claims Step** (added to end_session.py)
   - Governance compliance check ✅
   - Uncommitted files check ✅
   - Link validation ✅

2. **Migration Checklist** (add to FOLDER_STRUCTURE_GOVERNANCE.md)
   - [ ] Run pre-migration compliance check
   - [ ] Use safe_file_move.py for moves
   - [ ] Validate links after migration
   - [ ] Update governance spec Section VIII
   - [ ] Run post-migration compliance check
   - [ ] Commit with clear message

3. **Session Summary Template**
   - Include actual line counts (wc -l)
   - Run compliance check before summary
   - Distinguish "documented" vs "fixed"

---

## V. Next Session Priorities

### Session 12 Immediate Tasks

1. **Root file reduction** (CRITICAL)
   - Move 4 files to .github/
   - Move 2 files to docs/
   - Consolidate index.json

2. **Metadata adoption** (HIGH)
   - Add metadata to Session 11 docs
   - Create metadata template validator

3. **TASKS.md update** (MEDIUM)
   - Add root cleanup task
   - Add metadata adoption task
   - Mark Session 11 issues as resolved

### Session 13+ Roadmap

1. **Quarterly audit system**
2. **Streamlit improvements** (v0.17.0)
3. **VBA parity testing**

---

## VI. Estimated Effort

| Task | Time | Complexity |
|------|------|------------|
| Root file reduction | 30-45 min | Low |
| Metadata adoption (5 docs) | 20-30 min | Low |
| Create metadata validator | 45-60 min | Medium |
| Quarterly audit script | 30-45 min | Medium |
| TASKS.md update | 15 min | Low |

**Total Session 12 estimate:** 2-3 hours for all priorities

---

## VII. Success Criteria

**Session 12 is successful if:**
1. ✅ Root files reduced from 14 to ≤10
2. ✅ Governance compliance check passes (except known items)
3. ✅ All Session 11 docs have metadata
4. ✅ No leftover/duplicate files
5. ✅ TASKS.md reflects current state
6. ✅ SESSION_LOG updated with Session 12 summary

---

**Document Owner:** Session 12 Agent
**Review:** After Session 12 completion
