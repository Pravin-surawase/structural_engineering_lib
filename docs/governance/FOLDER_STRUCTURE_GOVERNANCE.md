# Folder Structure Governance
**Version:** 0.16.0
**Status:** 🚨 MANDATORY - All agents MUST follow
**Last Updated:** 2026-01-10
**Authority:** Project-wide standard

> **FOR ALL AI AGENTS:** These rules are PRESCRIPTIVE and MANDATORY. No exceptions without explicit approval. Breaking these rules creates technical debt and confusion.

---

## 🎯 Executive Summary

**Current State:** CHAOS (45 files in docs/ root, 13 files in agents/ root, duplicate folder concepts, dated files everywhere)

**Target State:** ORGANIZED (max 5 files in docs/ root, clear hierarchy, predictable locations, time-based archival)

**Enforcement:** Pre-commit hooks (planned), CI checks, agent training

---

## 📊 Industry Standards Analysis

### Research Findings from Major Projects

| Project | Root Docs Files | Max Depth | Naming | Insights |
|---------|----------------|-----------|--------|----------|
| **tRPC** | 12 files | 2 levels | kebab-case | `.github/`, `packages/`, `examples/`, `www/` (website) |
| **Vitest** | 16 files | 2 levels | kebab-case | `.github/`, `packages/`, `examples/`, `docs/` (website source) |
| **Prettier** | 20 files | 2 levels | kebab-case | `src/`, `website/`, `scripts/`, `tests/` |
| **Django** | 13 files | 2-3 levels | snake_case | `django/` (source), `docs/`, `tests/`, `scripts/` |

**Key Patterns:**
1. ✅ Root contains 10-20 essential files (README, LICENSE, CONTRIBUTING, CHANGELOG, config files)
2. ✅ Documentation lives in `docs/` subfolder (NOT 45 files at root level)
3. ✅ Max 2-3 levels of nesting (deeper = harder to find)
4. ✅ Kebab-case for docs, snake_case for Python code
5. ✅ Clear separation: source code, tests, docs, examples, scripts
6. ✅ No dated files in active directories (archives exist but are hidden)

---

## 🏗️ Prescribed Folder Structure

### Level 1: Project Root (5-10 files MAX)
```
/
├── README.md              ✅ Required
├── CHANGELOG.md           ✅ Required
├── CONTRIBUTING.md        ✅ Required
├── LICENSE                ✅ Required
├── pyproject.toml         ✅ Required (Python projects)
├── .gitignore             ✅ Required
├── .pre-commit-config.yaml ✅ Recommended
└── [Max 3 other config files]
```

**RULE 1.1:** Root directory MUST contain only:
- Essential metadata files (README, LICENSE, CHANGELOG, CONTRIBUTING)
- Build/config files (pyproject.toml, .gitignore, .pre-commit-config.yaml)
- Max 10 files total

**RULE 1.2:** NO documentation content files in root (move to docs/)
**RULE 1.3:** NO dated files in root (archive immediately)

### Level 2: docs/ (5 files MAX in root)
```
docs/
├── README.md              ✅ Index/navigation hub
├── TASKS.md               ✅ Current work items
├── SESSION_LOG.md         ✅ Session history
├── CHANGELOG.md           ⚠️  (if different from root)
├── TODO.md                ⚠️  (if needed)
│
├── getting-started/       📂 User-facing documentation
│   ├── README.md          ✅ Section index
│   ├── installation.md
│   ├── quickstart.md
│   └── tutorial.md
│
├── reference/             📂 API and technical reference
│   ├── README.md
│   ├── api-reference.md
│   ├── is456-quick-reference.md
│   └── troubleshooting.md
│
├── contributing/          📂 Contributor guides
│   ├── README.md
│   ├── development-guide.md
│   ├── testing-strategy.md
│   └── code-style.md
│
├── architecture/          📂 System design docs
│   ├── README.md
│   ├── project-overview.md
│   └── layer-architecture.md
│
├── governance/            📂 Process and policy docs
│   ├── README.md
│   ├── git-workflow.md
│   ├── folder-structure-governance.md (THIS FILE)
│   └── release-process.md
│
├── agents/                📂 AI agent documentation
│   ├── README.md
│   ├── roles/             📂 Role definitions
│   │   ├── dev.md
│   │   ├── tester.md
│   │   └── docs.md
│   ├── guides/            📂 Agent-specific guides
│   │   ├── workflow-master-guide.md
│   │   └── quick-reference.md
│   └── sessions/          📂 Agent session logs (time-limited)
│       └── 2026-01/       📂 Year-month archives (auto-cleanup after 90 days)
│
├── _active/               📂 Work-in-progress (90-day retention)
│   └── 2026-01/           📂 Year-month folders
│       ├── research-findings-validation.md
│       └── hygiene-suggestions-2026-01-07.md
│
├── _archive/              📂 Historical docs (permanent, indexed)
│   ├── README.md          ✅ Archive index
│   └── 2025-12/           📂 Year-month folders
│       ├── session-log-2025-12-28.md
│       └── tasks-2025-12-27.md
│
└── images/                📂 Documentation assets
    └── architecture/
```

**RULE 2.1:** `docs/` root MUST contain only:
- `README.md` (navigation hub)
- `TASKS.md` (current work)
- `SESSION_LOG.md` (session history)
- Max 2 other "living" documents
- NO dated files (move to `_active/` or `_archive/`)

**RULE 2.2:** Maximum 2 levels of nesting in `docs/` (docs/category/file.md)
- Exception: Year-month archives can be 3 levels (docs/_archive/2025-12/file.md)

**RULE 2.3:** Every category folder MUST have a `README.md` index

**RULE 2.4:** Use underscore prefix (`_`) ONLY for:
- `_active/` - Work-in-progress (90-day retention)
- `_archive/` - Historical records (permanent)
- Never for regular documentation categories

### Level 2: agents/ (organized by role)
```
agents/
├── README.md              ✅ Agent system overview
├── roles/                 📂 Agent role definitions
│   ├── dev.md
│   ├── tester.md
│   ├── docs.md
│   ├── researcher.md
│   ├── integration.md
│   └── ui.md
├── guides/                📂 Workflow and process guides
│   ├── workflow-master-guide.md
│   ├── quick-reference.md
│   ├── agent-bootstrap.md
│   └── git-workflow.md
└── templates/             📂 Reusable templates
    ├── session-handoff.md
    └── task-template.md
```

**RULE 3.1:** NO role files in `agents/` root (move to `agents/roles/`)
**RULE 3.2:** Agent-specific documentation lives in `docs/agents/`
**RULE 3.3:** `agents/` contains ONLY role definitions, guides, templates

### Level 2: Other Top-Level Folders
```
Python/                    📂 Python source code
├── structural_lib/        📂 Main package
├── tests/                 📂 Tests (mirrors package structure)
└── examples/              📂 Usage examples

VBA/                       📂 VBA source code
Excel/                     📂 Excel workbooks
streamlit_app/             📂 Streamlit application
scripts/                   📂 Automation scripts
tests/                     📂 Cross-cutting tests (if needed)
.github/                   📂 GitHub-specific files (workflows, templates)
```

**RULE 4.1:** One folder per major component (Python/, VBA/, Excel/, streamlit_app/)
**RULE 4.2:** `scripts/` for automation (not executable code)
**RULE 4.3:** `.github/` for CI/CD and GitHub templates only

---

## 📏 Naming Conventions

### File Naming Rules

| File Type | Convention | Examples | Forbidden |
|-----------|------------|----------|-----------|
| **Documentation** | kebab-case | `getting-started.md`, `api-reference.md` | `getting_started.md`, `APIReference.md` |
| **Python modules** | snake_case | `flexure.py`, `job_runner.py` | `flexure-module.py`, `JobRunner.py` |
| **Python classes** | PascalCase | `BeamDesigner`, `RebarOptimizer` | `beamDesigner`, `rebar_optimizer` |
| **Scripts** | snake_case | `agent_setup.sh`, `safe_push.sh` | `agent-setup.sh`, `SafePush.sh` |
| **Config files** | Project convention | `.pre-commit-config.yaml`, `pyproject.toml` | N/A |
| **Folders** | kebab-case | `getting-started/`, `api-docs/` | `getting_started/`, `ApiDocs/` |
| **Special folders** | Prefix with _ | `_active/`, `_archive/` | `active/`, `archive/` |

**RULE 5.1:** Kebab-case for ALL documentation files and folders
**RULE 5.2:** Snake_case for ALL Python code files
**RULE 5.3:** NO MixedCase in file or folder names (except Python class names in code)
**RULE 5.4:** NO spaces in file or folder names (use hyphens)
**RULE 5.5:** NO dates in file names UNLESS in archive folders

### Dated File Naming Rules

**RULE 5.6:** Active dated files MUST follow format: `description-YYYY-MM-DD.md`
- ✅ `hygiene-audit-2026-01-07.md`
- ✅ `needs-assessment-2026-01-09.md`
- ❌ `2026-01-07-hygiene.md` (date-first is hard to search)
- ❌ `hygiene_2026_01_07.md` (underscores in docs)

**RULE 5.7:** Dated files MUST live in:
- `docs/_active/YYYY-MM/` (work-in-progress, auto-archive after 90 days)
- `docs/_archive/YYYY-MM/` (historical reference, permanent)
- NEVER in category folders (docs/planning/, docs/architecture/, etc.)

**RULE 5.8:** Session logs use format: `session-YYYY-MM-DD.md` or `SESSION_LOG.md` (rolling)

---

## 🗂️ Folder-Specific Governance Rules

### docs/getting-started/
**Purpose:** User-facing onboarding and tutorials
**File Limit:** 10 files max
**Retention:** Permanent (keep up-to-date)
**Allowed:**
- installation.md
- quickstart.md
- tutorial-*.md
- faq.md

**Forbidden:**
- Implementation details (use docs/architecture/)
- Agent-specific docs (use docs/agents/)
- Dated files (use docs/_active/)

### docs/reference/
**Purpose:** API documentation, technical specifications
**File Limit:** 15 files max
**Retention:** Permanent
**Allowed:**
- api-reference.md
- is456-quick-reference.md
- troubleshooting.md
- known-pitfalls.md

**Forbidden:**
- Tutorials (use docs/getting-started/)
- Work-in-progress research (use docs/_active/)

### docs/architecture/
**Purpose:** System design, architectural decisions
**File Limit:** 10 files max
**Retention:** Permanent (ADRs never deleted)
**Allowed:**
- project-overview.md
- layer-architecture.md
- adr/ subfolder (Architecture Decision Records)

**Forbidden:**
- Implementation tasks (use TASKS.md)
- Session notes (use docs/agents/sessions/)

### docs/governance/
**Purpose:** Process, policy, workflow rules
**File Limit:** 10 files max
**Retention:** Permanent
**Allowed:**
- git-workflow.md
- release-process.md
- folder-structure-governance.md (this file)
- code-review-guidelines.md

**Forbidden:**
- User-facing docs (use docs/getting-started/)
- Technical reference (use docs/reference/)

### docs/agents/
**Purpose:** AI agent documentation and session logs
**File Limit:**
- `agents/roles/`: 15 files max (one per role)
- `agents/guides/`: 10 files max
- `agents/sessions/YYYY-MM/`: No limit, auto-cleanup after 90 days

**Retention:**
- Role definitions: Permanent
- Guides: Permanent
- Session logs: 90 days (then archive or delete)

**Allowed:**
- Role definitions (agents/roles/*.md)
- Workflow guides (agents/guides/*.md)
- Session handoffs (agents/sessions/YYYY-MM/*.md)

**Forbidden:**
- General project docs (use other categories)

### docs/_active/
**Purpose:** Work-in-progress, temporary research, drafts
**File Limit:** No hard limit, but trigger review at 50 files
**Retention:** 90 days (then archive or delete)
**Structure:** `docs/_active/YYYY-MM/filename.md`

**Allowed:**
- Research findings (research-*.md)
- Audit reports (audit-*.md)
- Planning documents (planning-*.md)
- Any file with date in name

**Forbidden:**
- Permanent documentation (move to appropriate category)
- Completed work (move to docs/_archive/ or integrate into main docs)

**Automation:**
```bash
# Auto-archive script (runs monthly in CI)
# Move files older than 90 days from _active/ to _archive/
find docs/_active/ -type f -mtime +90 -exec mv {} docs/_archive/$(date +%Y-%m)/ \;
```

### docs/_archive/
**Purpose:** Historical snapshots, completed work, reference
**File Limit:** No limit (but compress/index annually)
**Retention:** Permanent (never auto-delete)
**Structure:** `docs/_archive/YYYY-MM/filename.md`

**Required:**
- `README.md` index (updated monthly)
- Year-month folders (YYYY-MM/)
- Clear naming (includes original context)

**Forbidden:**
- Active work (use docs/_active/)
- Living documents (use appropriate category)

---

## 🚨 Critical Anti-Patterns (NEVER DO THIS)

### ❌ Anti-Pattern 1: Root Directory Clutter
**Problem:** 45 files in docs/ root
**Why Bad:** Impossible to find anything, no clear organization
**Solution:** Move to category folders, max 5 files in root

### ❌ Anti-Pattern 2: Duplicate Folder Concepts
**Problem:** `_internal/`, `_references/`, `planning/`, `research/` all mixed
**Why Bad:** Where do I put X? Multiple answers = confusion
**Solution:**
- Work-in-progress → `docs/_active/YYYY-MM/`
- Historical → `docs/_archive/YYYY-MM/`
- Research → Integrate into main docs or active/
- Planning → Use `TASKS.md` or `docs/_active/`

### ❌ Anti-Pattern 3: Dated Files Everywhere
**Problem:** `hygiene-2026-01-07.md` in docs/planning/
**Why Bad:** Dated files clutter categories, hard to know what's current
**Solution:**
- All dated files → `docs/_active/YYYY-MM/` or `docs/_archive/YYYY-MM/`
- If content is valuable, integrate into permanent docs without date

### ❌ Anti-Pattern 4: Inconsistent Naming
**Problem:** Mix of `api-reference.md`, `vba_guide.md`, `ExcelTutorial.md`
**Why Bad:** Unpredictable, breaks search/autocomplete
**Solution:** Enforce kebab-case for all docs

### ❌ Anti-Pattern 5: Deep Nesting
**Problem:** `docs/architecture/design/patterns/mvc/explanation.md` (5 levels)
**Why Bad:** Too many clicks, hard to remember path
**Solution:** Max 2-3 levels, flatten where possible

### ❌ Anti-Pattern 6: Scattered Research Folders
**Problem:** `docs/research/`, `docs/planning/research-*`, `streamlit_app/docs/research/`
**Why Bad:** Duplicate concepts, unclear which is canonical
**Solution:**
- Active research → `docs/_active/YYYY-MM/research-*.md`
- Completed research → Integrate into main docs or archive
- One canonical location per concept

---

## 📋 Migration Plan

### Phase 1: Immediate Cleanup (Week 1)
**Priority:** HIGH
**Goal:** Reduce docs/ root from 45 → 5 files

```bash
# Step 1: Create new structure
mkdir -p docs/{getting-started,reference,contributing,architecture,governance,agents/{roles,guides,sessions/2026-01},_active/2026-01,_archive}

# Step 2: Move files to appropriate categories
# (Use migration script - see below)

# Step 3: Update all internal links
# (Use find-replace script)

# Step 4: Commit with descriptive message
./scripts/ai_commit.sh "chore: migrate docs to new folder structure (Phase 1)"
```

**Tasks:**
- [ ] Create folder structure
- [ ] Move essential docs to root (README, TASKS, SESSION_LOG, CHANGELOG)
- [ ] Move dated files to `docs/_active/2026-01/`
- [ ] Move agent roles to `agents/roles/`
- [ ] Update `docs/README.md` with new navigation
- [ ] Run link checker and fix broken links

### Phase 2: Category Organization (Week 2)
**Priority:** MEDIUM
**Goal:** Organize remaining docs into categories

**Tasks:**
- [ ] Move getting-started docs (installation, quickstart, tutorials)
- [ ] Move reference docs (API, troubleshooting, known-pitfalls)
- [ ] Move architecture docs (project-overview, layer-architecture)
- [ ] Move governance docs (git-workflow, release-process)
- [ ] Create README.md index for each category
- [ ] Archive obsolete docs to `docs/_archive/2025-12/`

### Phase 3: Archival System (Week 3)
**Priority:** MEDIUM
**Goal:** Set up automated archival for dated files

**Tasks:**
- [ ] Create `scripts/archive_old_files.sh`
- [ ] Add CI job to run monthly
- [ ] Document archival policy in this file
- [ ] Add pre-commit hook to warn about dated files in wrong location
- [ ] Create `docs/_archive/README.md` index

### Phase 4: Enforcement (Week 4)
**Priority:** HIGH
**Goal:** Prevent regression via automation

**Tasks:**
- [ ] Add pre-commit hook: Check folder structure rules
- [ ] Add pre-commit hook: Check naming conventions
- [ ] Add pre-commit hook: Check file counts per folder
- [ ] Add CI check: Validate folder governance
- [ ] Update agent instructions with new structure
- [ ] Create migration guide for future files

---

## 🤖 Automation Scripts

### Script 1: Folder Structure Validator
**Location:** `scripts/validate_folder_structure.py`
**Runs:** Pre-commit hook, CI

```python
"""Validate folder structure against governance rules."""
import os
from pathlib import Path

RULES = {
    "docs": {
        "max_root_files": 5,
        "allowed_root": ["README.md", "TASKS.md", "SESSION_LOG.md", "CHANGELOG.md"],
        "required_subfolders": ["getting-started", "reference", "contributing", "architecture", "governance", "agents"],
    },
    "agents/roles": {
        "max_files": 15,
    },
    # ... more rules
}

def validate_folder_structure():
    """Check if folder structure follows governance rules."""
    errors = []

    # Check docs/ root file count
    docs_root_files = [f for f in Path("docs").iterdir() if f.is_file()]
    if len(docs_root_files) > RULES["docs"]["max_root_files"]:
        errors.append(f"docs/ root has {len(docs_root_files)} files, max is {RULES['docs']['max_root_files']}")

    # Check for dated files in wrong location
    for root, dirs, files in os.walk("docs"):
        for file in files:
            if "-202" in file and "_active" not in root and "_archive" not in root:
                errors.append(f"Dated file in wrong location: {os.path.join(root, file)}")

    return errors

if __name__ == "__main__":
    errors = validate_folder_structure()
    if errors:
        print("❌ Folder structure violations:")
        for error in errors:
            print(f"  - {error}")
        exit(1)
    else:
        print("✅ Folder structure is valid")
        exit(0)
```

### Script 2: Auto-Archival System
**Location:** `scripts/archive_old_files.sh`
**Runs:** Monthly (CI cron job)

```bash
#!/bin/bash
# Auto-archive files older than 90 days from docs/_active/

set -euo pipefail

ACTIVE_DIR="docs/_active"
ARCHIVE_DIR="docs/_archive"
RETENTION_DAYS=90

echo "🗂️  Checking for files to archive..."

# Find files older than 90 days in _active/
find "$ACTIVE_DIR" -type f -name "*.md" -mtime +$RETENTION_DAYS | while read -r file; do
    # Extract year-month from file modification date
    year_month=$(date -r "$file" +%Y-%m)

    # Create archive folder if needed
    mkdir -p "$ARCHIVE_DIR/$year_month"

    # Move file to archive
    filename=$(basename "$file")
    echo "  📦 Archiving: $file → $ARCHIVE_DIR/$year_month/$filename"
    mv "$file" "$ARCHIVE_DIR/$year_month/$filename"
done

# Update archive README.md index
echo "📝 Updating archive index..."
python scripts/update_archive_index.py

echo "✅ Archival complete"
```

### Script 3: Migration Helper
**Location:** `scripts/migrate_docs_structure.sh`
**Runs:** One-time migration

```bash
#!/bin/bash
# Migrate docs/ from current chaos to new structure

set -euo pipefail

echo "🚀 Starting docs/ migration..."

# Create new structure
echo "📁 Creating folder structure..."
mkdir -p docs/{getting-started,reference,contributing,architecture,governance}
mkdir -p docs/agents/{roles,guides,sessions/2026-01}
mkdir -p docs/_active/2026-01
mkdir -p docs/_archive

# Move dated files to _active/
echo "📅 Moving dated files to _active/..."
find docs -maxdepth 1 -type f -name "*-202[456]-*.md" -exec mv {} docs/_active/2026-01/ \;

# Move agent roles
echo "🤖 Organizing agent docs..."
mv docs/agents/*.md docs/agents/roles/ 2>/dev/null || true

# Move specific doc categories (requires manual mapping)
echo "📚 Categorizing documentation..."
# This requires a mapping file: migration_map.json
python scripts/apply_migration_map.py

echo "✅ Migration complete. Please review and test!"
```

---

## 🔍 Monitoring and Maintenance

### Monthly Review Checklist
**Owner:** Main Agent or Docs role
**Frequency:** Monthly

- [ ] Run `scripts/validate_folder_structure.py` and fix violations
- [ ] Review docs/ root file count (should be ≤5)
- [ ] Check for dated files in wrong locations
- [ ] Archive files older than 90 days from `docs/_active/`
- [ ] Update `docs/_archive/README.md` index
- [ ] Check for duplicate folder concepts
- [ ] Verify all category folders have README.md
- [ ] Test documentation links (run link checker)

### Quarterly Audit
**Owner:** Governance role
**Frequency:** Quarterly

- [ ] Review folder structure against governance rules
- [ ] Check naming consistency across all folders
- [ ] Assess if categories need splitting or merging
- [ ] Review retention policies (90-day rule still appropriate?)
- [ ] Update this document with lessons learned
- [ ] Train new agents on folder structure

---

## 📖 Quick Reference Card

### Where Do I Put This File?

| File Type | Location | Example |
|-----------|----------|---------|
| **User getting-started guide** | `docs/getting-started/` | `installation.md` |
| **API documentation** | `docs/reference/` | `api-reference.md` |
| **Architectural decision** | `docs/architecture/` | `adr-001-use-pydantic.md` |
| **Git workflow rules** | `docs/governance/` | `git-workflow.md` |
| **Agent role definition** | `agents/roles/` | `dev.md` |
| **Agent guide** | `agents/guides/` | `workflow-master-guide.md` |
| **Session handoff** | `docs/agents/sessions/YYYY-MM/` | `session-2026-01-10.md` |
| **Work-in-progress research** | `docs/_active/YYYY-MM/` | `research-benchmarking-2026-01.md` |
| **Dated audit report** | `docs/_active/YYYY-MM/` | `hygiene-audit-2026-01-07.md` |
| **Historical reference** | `docs/_archive/YYYY-MM/` | `session-log-2025-12-28.md` |
| **Python source code** | `Python/structural_lib/` | `flexure.py` |
| **Python tests** | `Python/tests/` | `test_flexure.py` |
| **Automation script** | `scripts/` | `agent_setup.sh` |
| **CI workflow** | `.github/workflows/` | `ci.yml` |

### Naming Quick Rules

- Docs: `kebab-case.md`
- Python: `snake_case.py`
- Folders: `kebab-case/`
- Special folders: `_prefix/`
- Dated files: `description-YYYY-MM-DD.md` (in `_active/` or `_archive/` only)

### File Count Limits

| Folder | Max Files | Enforcement |
|--------|-----------|-------------|
| Project root | 10 | Pre-commit hook |
| docs/ root | 5 | Pre-commit hook |
| docs/getting-started/ | 10 | Manual review |
| docs/reference/ | 15 | Manual review |
| agents/roles/ | 15 | Pre-commit hook |
| docs/_active/YYYY-MM/ | 50 (triggers review) | Monthly check |

---

## 🎓 Training for AI Agents

### Before Creating Any File
1. **Ask:** Does this file have a date in the name?
   - YES → Put in `docs/_active/YYYY-MM/` or `docs/_archive/YYYY-MM/`
   - NO → Continue to step 2

2. **Ask:** Is this a permanent documentation file?
   - YES → Determine category (getting-started, reference, architecture, governance)
   - NO → Put in `docs/_active/YYYY-MM/`

3. **Ask:** Is this an agent-related file?
   - YES → Determine: role definition (`agents/roles/`), guide (`agents/guides/`), or session log (`docs/agents/sessions/YYYY-MM/`)
   - NO → Continue to step 4

4. **Check:** File naming convention
   - Docs → kebab-case
   - Python → snake_case
   - Consistent with existing files in same folder

5. **Verify:** File count in target folder
   - Run: `ls -1 target_folder/*.md | wc -l`
   - If approaching limit → Flag for review

### When Migrating Existing Files
1. **Identify:** File type and purpose
2. **Check date:** If dated → `_active/` or `_archive/`
3. **Map to category:** Use decision tree above
4. **Update links:** Search for all references to old path
5. **Create redirect:** Add note in old location pointing to new location
6. **Commit:** Use descriptive message explaining migration

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-10 | Initial governance document based on industry research and project needs |

---

## 🔗 Related Documents

- [Git Workflow for AI Agents](git-workflow-ai-agents.md)
- [Agent Workflow Master Guide](../AGENT_WORKFLOW_MASTER_GUIDE.md)
- [Project Overview](../architecture/project-overview.md)
- [TASKS.md](../TASKS.md)

---

**Questions or Need Clarification?**
Consult the main agent or create an issue in TASKS.md labeled `governance`.
