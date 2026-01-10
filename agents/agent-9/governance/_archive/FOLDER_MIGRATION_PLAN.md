# Folder Structure Migration Plan
**Version:** 0.16.0
**Status:** 🚧 Ready to Execute
**Created:** 2026-01-10
**Estimated Duration:** 2-4 weeks

> **Context:** This plan executes the migration from current chaos (45 files in docs/ root) to organized structure defined in [FOLDER_STRUCTURE_GOVERNANCE.md](../FOLDER_STRUCTURE_GOVERNANCE.md).

---

## 📊 Current State Analysis

### Problems Identified
1. **45 files in docs/ root** (should be 5 max)
2. **13 files in agents/ root** (should be in agents/roles/)
3. **Duplicate folder concepts:** `_internal/`, `_references/`, `planning/`, `research/`
4. **Dated files everywhere:** 18+ files with dates in names scattered across folders
5. **Inconsistent naming:** Mix of kebab-case, snake_case, UPPERCASE
6. **No clear archival strategy**

### Files to Migrate

#### docs/ Root (44 files → 5 files)
**Keep in Root:**
- README.md
- TASKS.md
- SESSION_LOG.md
- (Maybe) CHANGELOG.md
- (Maybe) TODO.md

**Move to Categories:**
- Agent docs → docs/agents/guides/
- Getting-started → docs/getting-started/
- Reference → docs/reference/
- Architecture → docs/architecture/
- Governance → agents/agent-9/governance/
- Dated files → docs/_active/2026-01/

#### agents/ Root (13 files → 1 file)
**Keep in Root:**
- README.md

**Move to Subfolders:**
- Role files (DEV.md, TESTER.md, etc.) → agents/roles/
- Agent guides → agents/guides/ (or docs/agents/guides/ for cross-reference)

---

## 🗺️ Migration Phases

### Phase 1: Structure Creation (Day 1)
**Goal:** Create new folder structure
**Duration:** 1 hour
**Risk:** LOW

```bash
# Create new structure
mkdir -p docs/getting-started
mkdir -p docs/reference
mkdir -p docs/contributing
mkdir -p docs/architecture/adr
mkdir -p agents/agent-9/governance
mkdir -p docs/agents/sessions/2026-01
mkdir -p docs/_active/2026-01
mkdir -p docs/_archive/2025-12
mkdir -p agents/roles
mkdir -p agents/guides
mkdir -p agents/templates

# Create README.md files
touch docs/getting-started/README.md
touch docs/reference/README.md
touch docs/contributing/README.md
touch docs/architecture/README.md
touch agents/agent-9/governance/README.md
touch docs/agents/README.md
touch docs/_active/README.md
touch docs/_archive/README.md
touch agents/roles/README.md
touch agents/guides/README.md
```

**Validation:**
```bash
# Verify structure
tree docs -L 2
tree agents -L 1
```

### Phase 2: Agent Files Migration (Day 1-2)
**Goal:** Organize agent-related files
**Duration:** 2 hours
**Risk:** LOW

#### Step 2.1: Move Agent Role Definitions
```bash
# From agents/ root to agents/roles/
mv agents/DEV.md agents/roles/dev.md
mv agents/TESTER.md agents/roles/tester.md
mv agents/DOCS.md agents/roles/docs.md
mv agents/RESEARCHER.md agents/roles/researcher.md
mv agents/INTEGRATION.md agents/roles/integration.md
mv agents/UI.md agents/roles/ui.md
mv agents/ARCHITECT.md agents/roles/architect.md
mv agents/CLIENT.md agents/roles/client.md
mv agents/DEVOPS.md agents/roles/devops.md
mv agents/GOVERNANCE.md agents/roles/governance.md
mv agents/PM.md agents/roles/pm.md
mv agents/SUPPORT.md agents/roles/support.md
```

#### Step 2.2: Move Agent Guides
```bash
# From docs/ to agents/guides/ or docs/agents/guides/
# Decision: Keep in docs/ for consistency (all docs in docs/)

# High-level agent docs stay in docs/
# Role-specific stay in agents/

mv docs/AGENT_WORKFLOW_MASTER_GUIDE.md agents/guides/workflow-master-guide.md
mv docs/AGENT_QUICK_REFERENCE.md agents/guides/quick-reference.md
mv docs/AGENT_ONBOARDING.md agents/guides/onboarding.md
mv docs/agent-bootstrap.md agents/guides/bootstrap.md
```

#### Step 2.3: Update Links
```bash
# Find all references to old paths
grep -r "agents/DEV.md" docs/ agents/
grep -r "AGENT_WORKFLOW" docs/ agents/

# Update with sed or manual editing
```

**Validation:**
```bash
# Check agents/ structure
ls -la agents/roles/
ls -la agents/guides/

# Verify only README.md in agents/ root
ls -1 agents/*.md | wc -l  # Should be 1
```

### Phase 3: Dated Files Migration (Day 2-3)
**Goal:** Move all dated files to _active/ or _archive/
**Duration:** 3 hours
**Risk:** MEDIUM (many files, link updates needed)

#### Step 3.1: Identify Dated Files
```bash
# Find all dated files
find docs -type f -name "*-202[456]-*.md" | sort > /tmp/dated_files.txt

# Review list
cat /tmp/dated_files.txt

# Expected ~18 files:
# docs/PROJECT-NEEDS-ASSESSMENT-2026-01-09.md
# docs/planning/WORK-DIVISION-MAIN-AGENT6-2026-01-09.md
# docs/planning/hygiene-suggestions-2026-01-07.md
# ... etc
```

#### Step 3.2: Categorize by Age and Relevance
```bash
# Active work (less than 90 days old, still relevant)
# → docs/_active/2026-01/

# Historical reference (older than 90 days or completed)
# → docs/_archive/2025-12/ or docs/_archive/2026-01/

# Manual review required:
# - Is this still being worked on? → _active/
# - Is this historical reference? → _archive/
# - Is this obsolete? → Delete or archive
```

#### Step 3.3: Execute Migration
```bash
# Active work files (recent, relevant)
mv docs/PROJECT-NEEDS-ASSESSMENT-2026-01-09.md docs/_active/2026-01/
mv docs/planning/WORK-DIVISION-MAIN-AGENT6-2026-01-09.md docs/_active/2026-01/
mv docs/planning/hygiene-suggestions-2026-01-07.md docs/_active/2026-01/
mv docs/planning/handoff-agent-2-hygiene-2026-01-07.md docs/_active/2026-01/
# ... repeat for all active files

# Historical files (completed, archived)
mv docs/_internal/session-issues-2026-01-06.md docs/_archive/2026-01/
mv docs/_internal/main-agent-summary-2026-01-06.md docs/_archive/2026-01/
mv docs/_archive/session-log-2025-12-28.md docs/_archive/2025-12/
# ... repeat for all archive files
```

#### Step 3.4: Update _active/ README
```bash
cat > docs/_active/README.md << 'EOF'
# Active Work (90-Day Retention)

This folder contains work-in-progress documents, temporary research, and drafts.

**Retention Policy:** Files are automatically archived after 90 days (see [archival script](../../scripts/archive_old_files.sh)).

## Current Active Work (2026-01)

- [Project Needs Assessment](../../../../docs/_archive/2026-01/project-needs-assessment-2026-01-09.md)
- [Work Division Main Agent 6](../../../../docs/planning/work-division-main-agent6-2026-01-09.md)
- [Hygiene Suggestions](../../../../docs/planning/hygiene-suggestions-2026-01-07.md)

## How to Use

1. Create dated files: `description-YYYY-MM-DD.md`
2. Place in month folder: `docs/_active/YYYY-MM/`
3. After 90 days: File auto-moves to `docs/_archive/YYYY-MM/`
4. If still relevant: Integrate content into permanent docs (remove date from filename)
EOF
```

**Validation:**
```bash
# No dated files outside _active/ or _archive/
find docs -type f -name "*-202[456]-*.md" | grep -v "_active" | grep -v "_archive"
# Should return nothing

# Verify _active/ structure
tree docs/_active -L 2
```

### Phase 4: Category Organization (Day 3-5)
**Goal:** Move remaining docs/ root files to appropriate categories
**Duration:** 6 hours
**Risk:** MEDIUM (requires careful categorization and link updates)

#### Step 4.1: Map Files to Categories

**Getting-Started:**
```bash
mv docs/getting-started-python.md docs/getting-started/python.md
mv docs/excel-quickstart.md docs/getting-started/excel-quickstart.md
mv docs/excel-tutorial.md docs/getting-started/excel-tutorial.md
mv docs/beginners-guide.md docs/getting-started/beginners-guide.md
```

**Reference:**
```bash
mv docs/api-reference.md docs/reference/api-reference.md
mv docs/is456-quick-reference.md docs/reference/is456-quick-reference.md
mv docs/known-pitfalls.md docs/reference/known-pitfalls.md
mv docs/troubleshooting.md docs/reference/troubleshooting.md
mv docs/verification-examples.md docs/reference/verification-examples.md
mv docs/verification-pack.md docs/reference/verification-pack.md
```

**Contributing:**
```bash
mv docs/development-guide.md docs/contributing/development-guide.md
mv docs/testing-strategy.md docs/contributing/testing-strategy.md
mv docs/vba-testing-guide.md docs/contributing/vba-testing-guide.md
mv docs/vba-guide.md docs/contributing/vba-guide.md
```

**Architecture:**
```bash
mv docs/project-overview.md docs/architecture/project-overview.md
mv docs/deep-project-map.md docs/architecture/deep-project-map.md
mv docs/current-state-and-goals.md docs/architecture/current-state-and-goals.md
```

**Governance:**
```bash
mv docs/git-workflow-ai-agents.md agents/agent-9/governance/git-workflow-ai-agents.md
mv docs/ai-context-pack.md agents/agent-9/governance/ai-context-pack.md
# FOLDER_STRUCTURE_GOVERNANCE.md already in governance/
```

**Special Cases:**
```bash
# Mission and principles → Root or governance?
# Decision: Keep in root as it's foundational
# OR move to governance if it's process-related

# Production roadmap → Architecture or Planning?
# Decision: Keep in _active/ if dated, or architecture/ if timeless

# Streamlit-specific docs → Keep in docs/ or move to streamlit_app/docs/?
# Decision: Keep in docs/ for now (cross-cutting concerns)
```

#### Step 4.2: Create Category README Files
```bash
# docs/getting-started/README.md
cat > docs/getting-started/README.md << 'EOF'
# Getting Started with structural_lib

User-facing documentation for getting started with the library.

## Quick Links

- [Installation](installation.md)
- [Python Quickstart](python.md)
- [Excel Quickstart](../../../../docs/getting-started/excel-quickstart.md)
- [Beginner's Guide](../../../../docs/getting-started/beginners-guide.md)

## For Contributors

See [../contributing/](../../../../CONTRIBUTING.md) for development guides.
EOF

# Repeat for other categories...
```

#### Step 4.3: Update Main docs/README.md
```bash
cat > docs/README.md << 'EOF'
# Documentation Index

This is the main documentation hub for the structural_engineering_lib project.

## 📚 Documentation Categories

### Getting Started
- [Installation](getting-started/installation.md)
- [Python Quickstart](getting-started/python.md)
- [Excel Quickstart](../../../../docs/getting-started/excel-quickstart.md)

### Reference
- [API Reference](../../../docs/reference/api-reference.md)
- [IS 456 Quick Reference](../../../docs/reference/is456-quick-reference.md)
- [Troubleshooting](../../../../docs/reference/troubleshooting.md)

### Contributing
- [Development Guide](../../../../docs/contributing/development-guide.md)
- [Testing Strategy](../../../../docs/contributing/testing-strategy.md)

### Architecture
- [Project Overview](../../../../docs/architecture/project-overview.md)
- [Deep Project Map](../../../../docs/architecture/deep-project-map.md)

### Governance
- [Git Workflow](../../../../docs/contributing/git-workflow-ai-agents.md)
- [Folder Structure](../FOLDER_STRUCTURE_GOVERNANCE.md)

### AI Agents
- [Agent Guides](agents/)
- [Workflow Master Guide](../agents/guides/workflow-master-guide.md)

## 📝 Living Documents

- [TASKS.md](../../../../docs/TASKS.md) - Current work items
- [SESSION_LOG.md](../../../../docs/SESSION_LOG.md) - Session history

## 🗂️ Special Folders

- [_active/](_active/) - Work-in-progress (90-day retention)
- [_archive/](_archive/) - Historical reference (permanent)

---

**Can't find something?** Check the [search guide](reference/search-guide.md) or ask in the project Discord.
EOF
```

**Validation:**
```bash
# Check docs/ root file count
ls -1 docs/*.md | wc -l  # Should be ≤5

# Verify category structure
tree docs -L 2 -I "_*"

# Test links
# (Manual verification or use link checker tool)
```

### Phase 5: Cleanup Duplicate Folders (Day 5-6)
**Goal:** Consolidate duplicate concepts (_internal/, _references/, planning/)
**Duration:** 4 hours
**Risk:** HIGH (requires careful review to not lose important content)

#### Step 5.1: Review and Consolidate _internal/
```bash
# _internal/ contains:
# - COST_OPTIMIZER_* files (dated)
# - agent-workflow.md (governance)
# - automation-improvements.md (governance)
# - quality-gaps-assessment.md (dated audit)
# - session-issues-2026-01-06.md (already handled in Phase 3)

# Decision tree:
# - Dated files → _active/ or _archive/
# - Process docs → governance/
# - Obsolete → Delete

# Example:
mv docs/_internal/agent-workflow.md agents/agent-9/governance/agent-workflow-legacy.md
mv docs/_internal/COST_OPTIMIZER_FIX_PLAN.md docs/_archive/2026-01/
# ... review each file
```

#### Step 5.2: Review and Consolidate _references/
```bash
# _references/ contains:
# - downloads_snapshot/ (external references)

# Decision: Keep _references/ for external downloaded docs
# OR: Delete if not needed

# Recommendation: Delete if downloads are reproducible
# Otherwise: Keep with clear README explaining purpose
```

#### Step 5.3: Review and Consolidate planning/
```bash
# planning/ contains:
# - Dated files (already handled in Phase 3)
# - research-* subfolders (scattered research)

# Decision:
# - Active research → docs/_active/YYYY-MM/
# - Completed research → Integrate into main docs or archive
# - Delete obsolete research

# Example:
mv docs/planning/research-findings-validation/ docs/_active/2026-01/
# ... review each subfolder
```

#### Step 5.4: Final Cleanup
```bash
# Remove empty folders
find docs -type d -empty -delete

# Remove duplicate folders if empty
rmdir docs/_internal/ 2>/dev/null || echo "_internal/ not empty, review needed"
rmdir docs/planning/ 2>/dev/null || echo "planning/ not empty, review needed"
```

**Validation:**
```bash
# Verify duplicate folders are gone or have clear purpose
ls -la docs/ | grep "^d"

# Check for any remaining clutter
find docs -type d -empty
```

### Phase 6: Link Updates and Validation (Day 6-7)
**Goal:** Update all internal links and validate structure
**Duration:** 4 hours
**Risk:** MEDIUM (missed links can break navigation)

#### Step 6.1: Find All Internal Links
```bash
# Find all markdown links
grep -r "\[.*\](.*\.md)" docs/ agents/ > /tmp/all_links.txt

# Find all broken links (404s)
# Use tool like markdown-link-check or manual verification
```

#### Step 6.2: Update Links in Bulk
```bash
# Example: Update agent role links
find docs agents -type f -name "*.md" -exec sed -i '' 's|agents/DEV.md|agents/roles/dev.md|g' {} +
find docs agents -type f -name "*.md" -exec sed -i '' 's|AGENT_WORKFLOW_MASTER_GUIDE.md|agents/guides/workflow-master-guide.md|g' {} +

# Repeat for all moved files
```

#### Step 6.3: Validate Structure
```bash
# Run validation script (create in Phase 7)
python scripts/validate_folder_structure.py

# Expected output:
# ✅ docs/ root has 5 files (within limit)
# ✅ No dated files in wrong location
# ✅ All category folders have README.md
# ✅ Folder structure is valid
```

#### Step 6.4: Manual Review
```bash
# Review key documents manually:
# - docs/README.md (navigation works?)
# - TASKS.md (links updated?)
# - SESSION_LOG.md (links work?)
# - agents/README.md (structure makes sense?)
```

**Validation:**
```bash
# No broken links
markdown-link-check docs/**/*.md

# File counts within limits
./scripts/validate_folder_structure.py

# Naming conventions followed
find docs agents -type f -name "*.md" | grep -E "[A-Z_]" | grep -v "README\|TASKS\|SESSION_LOG\|CHANGELOG"
# Should return minimal results (only allowed UPPERCASE files)
```

### Phase 7: Automation Setup (Day 7-8)
**Goal:** Create automation scripts to prevent regression
**Duration:** 4 hours
**Risk:** LOW

#### Step 7.1: Create Validation Script
```bash
# Already outlined in FOLDER_STRUCTURE_GOVERNANCE.md
# Create: scripts/validate_folder_structure.py
# (See governance doc for implementation)
```

#### Step 7.2: Create Archival Script
```bash
# Already outlined in FOLDER_STRUCTURE_GOVERNANCE.md
# Create: scripts/archive_old_files.sh
# (See governance doc for implementation)
```

#### Step 7.3: Add Pre-Commit Hook
```bash
# Add to .pre-commit-config.yaml
cat >> .pre-commit-config.yaml << 'EOF'
  - repo: local
    hooks:
      - id: validate-folder-structure
        name: Validate Folder Structure
        entry: python scripts/validate_folder_structure.py
        language: system
        pass_filenames: false
        always_run: true
EOF
```

#### Step 7.4: Add CI Check
```bash
# Add to .github/workflows/ci.yml
# (Add job to run validation on every PR)
```

**Validation:**
```bash
# Test pre-commit hook
pre-commit run validate-folder-structure --all-files

# Test archival script (dry run)
bash scripts/archive_old_files.sh --dry-run
```

### Phase 8: Documentation and Training (Day 8-10)
**Goal:** Update all agent instructions and documentation
**Duration:** 4 hours
**Risk:** LOW

#### Step 8.1: Update Agent Instructions
```bash
# Update .github/copilot-instructions.md
# Add section referencing FOLDER_STRUCTURE_GOVERNANCE.md

# Update agent role files
# Add folder structure rules to each role
```

#### Step 8.2: Create Migration Guide
```bash
# Create: agents/agent-9/governance/FOLDER_MIGRATION_GUIDE.md
# (For future agents who need to add files)
```

#### Step 8.3: Update Session Handoff Templates
```bash
# Update docs/planning/next-session-brief.md template
# Include folder structure reminder
```

**Validation:**
```bash
# All agent instructions updated
grep -r "FOLDER_STRUCTURE_GOVERNANCE" .github/ agents/

# Migration guide complete
ls -la agents/agent-9/governance/FOLDER_MIGRATION_GUIDE.md
```

---

## 📋 Rollback Plan

If migration fails or causes major issues:

### Rollback Option 1: Git Revert
```bash
# If migration was single commit
git log --oneline | head -5
git revert <migration_commit_hash>
```

### Rollback Option 2: Restore from Backup
```bash
# Before migration, create backup
tar -czf ~/docs_backup_$(date +%Y%m%d).tar.gz docs/ agents/

# Restore if needed
tar -xzf ~/docs_backup_YYYYMMDD.tar.gz
```

### Rollback Option 3: Selective Undo
```bash
# Only undo specific files
git checkout HEAD~1 -- docs/specific-file.md
```

---

## ✅ Success Criteria

### Must-Have (Required for completion)
- [ ] docs/ root has ≤5 files
- [ ] agents/ root has only README.md
- [ ] All dated files in _active/ or _archive/
- [ ] All category folders have README.md
- [ ] No broken links in documentation
- [ ] Pre-commit hook validates structure
- [ ] CI validates structure on every PR

### Nice-to-Have (Post-migration improvements)
- [ ] Automated link checker in CI
- [ ] Automated archival runs monthly
- [ ] Documentation search improved
- [ ] Category READMEs include examples
- [ ] Visual documentation map (diagram)

---

## 🚨 Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Broken links** | HIGH | MEDIUM | Run link checker after each phase |
| **Lost content** | MEDIUM | HIGH | Review each file before moving, create backups |
| **Confusion during transition** | HIGH | LOW | Clear communication, rollback plan ready |
| **Automation script bugs** | MEDIUM | MEDIUM | Test scripts thoroughly before production use |
| **Agent resistance** | LOW | MEDIUM | Clear documentation, training, benefits explained |

---

## 📊 Progress Tracking

### Phase Completion Checklist

- [ ] Phase 1: Structure Creation (1 hour)
- [ ] Phase 2: Agent Files Migration (2 hours)
- [ ] Phase 3: Dated Files Migration (3 hours)
- [ ] Phase 4: Category Organization (6 hours)
- [ ] Phase 5: Cleanup Duplicate Folders (4 hours)
- [ ] Phase 6: Link Updates and Validation (4 hours)
- [ ] Phase 7: Automation Setup (4 hours)
- [ ] Phase 8: Documentation and Training (4 hours)

**Total Estimated Time:** 28 hours (~1 week of focused work)

### Daily Progress Log

**Day 1:**
- [ ] Phases 1-2 complete
- [ ] Commit: "chore: create new folder structure and migrate agent files"

**Day 2:**
- [ ] Phase 3 complete
- [ ] Commit: "chore: migrate dated files to _active/ and _archive/"

**Day 3-4:**
- [ ] Phase 4 complete
- [ ] Commit: "chore: organize docs into categories"

**Day 5:**
- [ ] Phase 5 complete
- [ ] Commit: "chore: consolidate duplicate folders"

**Day 6:**
- [ ] Phase 6 complete
- [ ] Commit: "chore: update links and validate structure"

**Day 7:**
- [ ] Phase 7 complete
- [ ] Commit: "chore: add automation for folder structure governance"

**Day 8:**
- [ ] Phase 8 complete
- [ ] Commit: "docs: update agent instructions for new folder structure"

---

## 🎓 Lessons Learned (Post-Migration)

_To be filled after migration completes_

### What Went Well
-

### What Could Be Improved
-

### Unexpected Issues
-

### Recommendations for Future Migrations
-

---

**Next Steps:** Execute Phase 1 and commit the new structure!
