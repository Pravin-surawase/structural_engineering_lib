# Folder Structure Governance

**Version:** 2.0
**Last Updated:** 2026-01-11
**Status:** Comprehensive specification
**Enforcement:** Automated validators + pre-commit hooks

---

## I. Root Principles

1. **Progressive Disclosure** - Short entry docs, detailed content one level down
2. **Clear Ownership** - Every folder has a clear purpose and maintainer
3. **Automation First** - Rules are enforced by code, not conversation
4. **Long-term Stability** - Structure supports multi-year growth without major reorganization
5. **Discoverability** - Every document is reachable from a README index

---

## II. Repository Root (/)

**Purpose:** Metadata, configuration, entry points
**Max files:** 10 (strictly enforced)
**Allowed files:**

| File | Purpose | Required? |
|------|---------|-----------|
| README.md | Project overview | YES |
| LICENSE | License text | YES |
| LICENSE_ENGINEERING.md | Engineering-specific license | OPTIONAL |
| CONTRIBUTING.md | Contribution guidelines | YES |
| CODE_OF_CONDUCT.md | Community guidelines | YES |
| CHANGELOG.md | Version history | YES |
| pyproject.toml | Python configuration | YES |
| .github/copilot-instructions.md | AI agent guidelines | YES |
| llms.txt | LLM-friendly documentation | OPTIONAL |
| CITATION.cff | Citation metadata | OPTIONAL |

**Current count:** 10 files ✅
**Status:** COMPLIANT

---

## III. Documentation Root (docs/)

**Purpose:** All user-facing and developer documentation
**Max root files:** 3-5 (hub documents only)
**Structure:** Three levels
1. **Root (3-5 files):** Quick links, landing page, index
2. **Categories (15-20 folders):** Organized by audience/purpose
3. **Detail (files in folders):** Actual content

### III.A. Required Root Files (docs/)

| File | Purpose |
|------|---------|
| README.md | Hub index with quick-start paths |
| TASKS.md | Active task tracking |
| SESSION_LOG.md | Session history and decisions |

### III.B. Approved Doc Categories (Level 2)

| Folder | Purpose | Max Files | Sub-levels | Notes |
|--------|---------|-----------|------------|-------|
| **Core Learning** |
| getting-started/ | Onboarding for all users | 10 | 0 | Platform-specific quickstarts |
| learning/ | Structured learning paths | 10 | 0 | Beginner-friendly, self-paced |
| cookbook/ | Task-focused recipes | 15 | 0 | "How to" with examples |
| reference/ | API, CLI, formula reference | 20 | 1 | Searchable reference material |
| **Architecture & Design** |
| architecture/ | System design, decisions | 10 | 1 | Layer diagrams, trade-offs |
| adr/ | Architecture Decision Records | 50 | 0 | Searchable by decision type |
| **Contributing** |
| contributing/ | Developer guides | 20 | 1 | Testing, PR workflow, standards |
| guidelines/ | Development standards | 15 | 1 | API design, naming, patterns |
| **Verification** |
| verification/ | Test vectors, benchmarks | 15 | 1 | Hand calculations, edge cases |
| **Planning & Research** |
| planning/ | Roadmaps, sprints, briefs | 30 | 1 | Product roadmap, session planning |
| research/ | Research notes, findings | 100 | 2 | Exploratory work, deep dives |
| **Content** |
| blog-drafts/ | Blog posts in progress | 20 | 0 | Editorial pipeline |
| publications/ | Published content | 20 | 0 | Links to external publications |
| **Infrastructure** |
| _archive/ | Completed/deprecated docs | ∞ | 3 | Old versions, obsolete guides |
| _internal/ | Internal notes, checklists | 50 | 1 | Not for users, internal only |
| _references/ | Local research materials | 50 | 0 | PDFs, spreadsheets you own |
| **Agent-Specific** |
| agents/ | AI agent documentation | 5 (root) | 2 | Quick-start → guides → sessions |
| **Utility** |
| images/ | Images referenced by docs | - | 0 | Screenshots, diagrams |
| legal/ | Legal documents | 10 | 0 | Terms, privacy, licensing |

### III.C. Current Compliance Check

**Compliant categories (✅):**
- getting-started/ (8 files)
- learning/ (9 files)
- cookbook/ (3 files)
- reference/ (9 files)
- architecture/ (12 files)
- adr/ (1 file)
- contributing/ (16 files)
- guidelines/ (11 files)
- verification/ (5 files)
- planning/ (12 files)
- research/ (20+ files)

**Needs attention (⚠️):**
- blog-drafts/ - 4 files (OK)
- publications/ - (old archive exists)
- agents/ - 6 root files (SHOULD BE 3-5)
- _archive/ - properly structured ✅
- _internal/ - exists, used ✅
- _references/ - exists, used ✅

---

## IV. Agents Folder (agents/)

**Purpose:** Agent definitions, role descriptions, index
**Structure (ENFORCED):**

```
agents/
├── README.md                    ← Hub (list all agents)
├── index.md                     ← Registry (metadata JSON/YAML format)
├── roles/                       ← REQUIRED
│   ├── README.md                (hub for roles)
│   ├── ARCHITECT.md
│   ├── CLIENT.md
│   ├── DEV.md
│   ├── DEVOPS.md
│   ├── DOCS.md
│   ├── INTEGRATION.md
│   ├── PM.md
│   ├── RESEARCHER.md
│   ├── SUPPORT.md
│   ├── TESTER.md
│   └── UI.md
├── guides/                      ← Agent guides (docs/agents/guides/)
│   └── *.md                     (Not in agents/ root!)
├── templates/                   ← PLANNED (not yet populated)
│   ├── prompt-template.md
│   └── session-log-template.md
└── agent-9/                     ← Agent-specific folders
    ├── README.md
    └── ...
```

**Current status (verified 2026-01-11):**

1. ✅ **agents/roles/ exists** - All 12 role files properly organized
2. ✅ **agents/roles/GOVERNANCE.md** - In correct location
3. ✅ **docs/agents/guides/** - All agent guides properly nested
4. ✅ **agents/ root** - Only 4 files (README.md, index.json, index.md, roles/, agent-9/)

**Note:** Historical governance docs archived at `docs/_archive/2026-01/agent-9-governance-legacy/`

**Enforcement rules:**

| Rule | Check | Consequence |
|------|-------|-------------|
| Only 3-5 files in agents/ root | Automated | CI failure if violated |
| All role .md in agents/roles/ | Automated | Warning in validator |
| agents/GOVERNANCE.md moved | Link check | Broken link detected |
| guides/ properly nested | Structure check | Non-compliant flag |

---

## V. Document Metadata Standard

**NEW (Session 11):** Every document should have a metadata section.

```markdown
# Document Title

**Type:** [Guide | Reference | Research | Archive]
**Audience:** [All | Users | Developers | Maintainers]
**Last Updated:** YYYY-MM-DD
**Status:** [Active | Obsolete | Superseded | In Progress]
**Importance:** [Critical | High | Medium | Low]
**Version:** [Original | v2 | Supersedes: doc-name.md]

---

[Rest of document...]

---

**Archive:** [If obsolete, link to new location or explain why]
**Related:** [Link to related docs or tasks]
**Next Review:** YYYY-MM-DD (or "Quarterly")
```

---

## VI. Validation Checklist

### Automated Checks (Pre-commit)

- [ ] Root has ≤10 files
- [ ] docs/ root has ≤5 files
- [ ] All categories use proper structure
- [ ] agents/ roles in agents/roles/ folder
- [ ] No redirect stubs (single source rule)
- [ ] All internal links valid
- [ ] governance spec and validator synchronized

### Manual Review (Quarterly)

- [ ] New doc categories reviewed and approved
- [ ] Orphan docs migrated or archived
- [ ] Link structure audit
- [ ] Navigation usability check

---

## VII. Rule Updates & Governance

### Changing the Spec

1. **Propose change** in GitHub issue with rationale
2. **Update FOLDER_STRUCTURE_GOVERNANCE.md first**
3. **Update validators to match**
4. **Run full validation**
5. **Execute moves if needed**
6. **Document in CHANGELOG**

### When to Create a New Category

**Required answers:**

1. Does this fit in an existing category? (Prefer reuse)
2. Is it audience-specific or purpose-specific?
3. Will it have 5+ documents? (Or just temporary?)
4. Does it need governance rules?
5. Can validators check compliance?

---

## VIII. Current Status

**Last Updated:** 2026-01-11 (Session 13 Part 2)

| Aspect | Status | Notes |
|--------|--------|-------|
| Root files (≤10) | ✅ PASS | 9 files |
| docs/ root (≤5) | ✅ PASS | 3 files |
| Link validity | ✅ PASS | 801 links, 0 broken |
| agents/ roles | ✅ PASS | 12 files in agents/roles/ |
| Governance consolidated | ✅ PASS | Single location: docs/guidelines/ |
| docs/agents structure | ✅ PASS | All agent guides in docs/agents/guides/ |
| Spec/validator sync | ✅ PASS | max_files=10 aligned |
| Naming convention | ✅ PASS | All files kebab-case |
| Doc metadata | ⚠️ IN PROGRESS | New standard being applied |

---

## IX. Migration Path (Session 11-12)

| Phase | Task | Status |
|-------|------|--------|
| 1 | Publish this governance spec | ✅ Complete (Session 11) |
| 2 | Update validators | ✅ Complete (Session 12) |
| 3 | Create migration tools | ✅ Complete (safe_file_move.py) |
| 4 | Migrate agents/ roles (12 files) | ✅ Complete (Session 11) |
| 5 | Reorganize docs/agents (6 files) | ✅ Complete (Session 11) |
| 6 | Move agents/GOVERNANCE.md | ✅ Complete (to agents/roles/) |
| 7 | Apply document metadata standard | ⏳ In Progress |
| 8 | Reduce root files (14 → 10) | ⏳ Session 12 Priority |

---

**Owner:** Project Governance Team
**Review Schedule:** Quarterly (2026-04-11)
**Validator:** scripts/validate_folder_structure.py + pre-commit hooks
