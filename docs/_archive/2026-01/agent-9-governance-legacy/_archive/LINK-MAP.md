# Link Map - File Migration Tracking

**Purpose:** Track all file moves and renames during folder structure migration
**Format:** `old-path → new-path` (one per line)
**Usage:** Used by automated scripts to update references

---

## How to Use This File

### For Scripts (Automated):

```bash
# Extract all migrations
cat agents/agent-9/governance/LINK-MAP.md | grep "→"

# Extract specific phase
grep "Phase 2" agents/agent-9/governance/LINK-MAP.md -A 50

# Update references using link map
while IFS='→' read -r old new; do
  [[ "$old" =~ ^# ]] && continue
  old=$(echo "$old" | xargs)
  new=$(echo "$new" | xargs)
  find docs/ -name "*.md" -exec sed -i '' "s|$old|$new|g" {} +
done < agents/agent-9/governance/LINK-MAP.md
```

### For Humans (Manual):

- **Find where a file moved:** Search for old path
- **Update a reference:** Look up new path for old reference
- **Verify migration:** Check that all phases have entries

### During Migration:

- **Auto-populated** by migration scripts (archive_old_docs.py, rename_batch.sh, etc.)
- **Manually append** if moving files manually
- **Verify after each phase** that entries are correct

---

## Migration Timeline

**Migration Start:** 2026-01-10
**Migration End:** TBD
**Phases:** 8 phases total

---

## Phase 0: Preparation (2026-01-10)

No file moves in Phase 0 (preparation only).

---

## Phase 1: Structure Creation (2026-01-10)

No file moves in Phase 1 (only new directories/READMEs created).

New directories created:
- `agents/roles/`
- `agents/guides/`
- `agents/templates/`
- `docs/getting-started/`
- `docs/reference/`
- `docs/contributing/`
- `docs/architecture/`
- `agents/agent-9/governance/`
- `docs/agents/roles/`
- `docs/agents/guides/`
- `docs/agents/sessions/2026-01/`
- `docs/images/`
- `docs/_active/2026-01/`
- `docs/_archive/`

---

## Phase 2: Agents Migration (2026-01-10)

**12 agent files moved to agents/roles/ and renamed to kebab-case:**

agents/AGENT-1-RESEARCH.md → agents/roles/agent-1-research.md
agents/AGENT-2-PLANNING.md → agents/roles/agent-2-planning.md
agents/AGENT-3-IMPLEMENTATION.md → agents/roles/agent-3-implementation.md
agents/AGENT-4-TESTING.md → agents/roles/agent-4-testing.md
agents/AGENT-5-DOCUMENTATION.md → agents/roles/agent-5-documentation.md
agents/AGENT-6-REFACTORING.md → agents/roles/agent-6-refactoring.md
agents/AGENT-7-PERFORMANCE.md → agents/roles/agent-7-performance.md
agents/AGENT-8-SECURITY.md → agents/roles/agent-8-security.md
agents/AGENT-9-GOVERNANCE.md → agents/roles/agent-9-governance.md
agents/AGENT-10-INTEGRATION.md → agents/roles/agent-10-integration.md
agents/AGENT-11-DEPLOYMENT.md → agents/roles/agent-11-deployment.md
agents/AGENT-12-MONITORING.md → agents/roles/agent-12-monitoring.md

---

## Phase 3: Docs Migration (TBD)

**Phase 3 status:** Not yet executed (or DEFERRED)

When executed, entries will appear here in format:
```
# docs/Old_File.md → docs/getting-started/old-file.md
# docs/Design_Doc.md → docs/architecture/design-doc.md
# ... (up to 44 files)
```

Placeholder for future entries:
<!-- Phase 3 entries will be appended here by migration script or manually -->

---

## Phase 4: Dated Files Archival (TBD)

**Phase 4 status:** Not yet executed

When executed, entries will appear here in format:
```
# docs/planning/session-2025-12-15.md → docs/_archive/2025-12/session-2025-12-15.md
# docs/design-2025-11-20.md → docs/_archive/2025-11/design-2025-11-20.md
# ... (up to 23 files)
```

Placeholder for future entries:
<!-- Phase 4 entries will be appended here by archive_old_docs.py script -->

---

## Phase 5: Naming Cleanup (TBD)

**Phase 5 status:** Not yet executed

When executed, entries will appear here in format:

### Phase 5 Batch 1 (TBD)
```
# docs/planning/Old_Analysis.md → docs/planning/old-analysis.md
# docs/planning/Draft_Ideas.md → docs/planning/draft-ideas.md
# ... (up to 20 files)
```

### Phase 5 Batch 2 (TBD)
```
# docs/architecture/Design_Patterns.md → docs/architecture/design-patterns.md
# docs/reference/API_Guide.md → docs/reference/api-guide.md
# ... (up to 30 files)
```

### Phase 5 Batch 3 (TBD)
```
# docs/Task_Specifications.md → docs/task-specifications.md
# docs/Agent_Coordination.md → docs/agent-coordination.md
# ... (up to 20 files)
```

### Phase 5 Batch 4 (TBD)
```
# docs/v0.16-Task_Specs.md → docs/v0.16-task-specs.md
# docs/v0.15-Design_Doc.md → docs/v0.15-design-doc.md
# ... (up to 22 files)
```

Placeholder for future entries:
<!-- Phase 5 entries will be appended here by rename_batch.sh script -->

---

## Phase 6: Link Fixing (TBD)

**Phase 6 note:** This phase doesn't move files, only updates references.

No entries needed for Phase 6 (uses mappings from Phases 2-5).

---

## Phase 7: Script Updates (TBD)

**Phase 7 note:** This phase updates scripts, not documentation files.

No entries needed for Phase 7.

---

## Phase 8: Final Validation (TBD)

**Phase 8 note:** This phase validates completion, no file moves.

No entries needed for Phase 8.

---

## Summary Statistics

**Total File Moves/Renames:**
- Phase 2: 12 files (agents)
- Phase 3: TBD (up to 44 files)
- Phase 4: TBD (up to 23 files)
- Phase 5: TBD (up to 92 files)
- **Total: 12+ files** (more after remaining phases)

**Link Map Completion:**
- ✅ Phase 2 entries complete (12 entries)
- ⏸️ Phase 3 entries pending
- ⏸️ Phase 4 entries pending
- ⏸️ Phase 5 entries pending

---

## Manual Entry Format

**When adding entries manually:**

```
# Add phase header
## Phase X: Description (YYYY-MM-DD)

# Add entries (one per line)
old/path/file.md → new/path/new-file.md
another/old.md → another/location/new.md

# Use consistent format:
# - Full path from project root
# - Space → space (with arrows)
# - One entry per line
# - Group by phase/batch
```

**Example:**

```
## Phase 3: Docs Migration (2026-01-15)

docs/Task_Specs.md → docs/getting-started/task-specs.md
docs/Design_Overview.md → docs/architecture/design-overview.md
docs/API_Guide.md → docs/reference/api-guide.md
```

---

## Validation

**Verify link map completeness:**

```bash
# Count entries per phase
grep "Phase 2" agents/agent-9/governance/LINK-MAP.md | grep "→" | wc -l
# Should show 12

grep "Phase 3" agents/agent-9/governance/LINK-MAP.md | grep "→" | wc -l
# Should show ~44 (after Phase 3 complete)

grep "Phase 4" agents/agent-9/governance/LINK-MAP.md | grep "→" | wc -l
# Should show ~23 (after Phase 4 complete)

grep "Phase 5" agents/agent-9/governance/LINK-MAP.md | grep "→" | wc -l
# Should show ~92 (after Phase 5 complete)
```

**Verify all old paths no longer exist:**

```bash
# Extract old paths
grep "→" agents/agent-9/governance/LINK-MAP.md | awk '{print $1}' > /tmp/old-paths.txt

# Check if any old paths still exist
while read old_path; do
  if [ -f "$old_path" ]; then
    echo "❌ Old file still exists: $old_path"
  fi
done < /tmp/old-paths.txt
```

**Verify all new paths exist:**

```bash
# Extract new paths
grep "→" agents/agent-9/governance/LINK-MAP.md | awk '{print $3}' > /tmp/new-paths.txt

# Check if all new paths exist
while read new_path; do
  if [ ! -f "$new_path" ]; then
    echo "❌ New file missing: $new_path"
  fi
done < /tmp/new-paths.txt
```

---

## Notes

- **This file is auto-updated** by migration scripts in Phases 4 and 5
- **Manual updates OK** for Phases 2, 3, 6 if needed
- **Do not delete entries** - keeps historical record of migrations
- **Use for rollback** - can reverse migrations using this map
- **Reference for link fixing** - Phase 6 uses this to update all references

---

## After Migration

**Keep this file** for historical reference:

- Shows complete audit trail of file moves
- Useful for understanding history of file locations
- Helps debug broken links found later
- Documents migration decisions

**Archive after migration complete:**

```bash
# After migration merged to main and stable
cp agents/agent-9/governance/LINK-MAP.md docs/_archive/migrations/2026-01/LINK-MAP.md
# Keep original in agents/agent-9/governance/ for easy reference
```

---

**Last Updated:** 2026-01-10 (Phase 2 entries added)
**Next Update:** After Phase 3 execution (or Phase 4 if Phase 3 deferred)
**Maintained By:** Migration scripts + manual updates
**Related:** [FULL-MIGRATION-EXECUTION-PLAN.md](FULL-MIGRATION-EXECUTION-PLAN.md), [MIGRATION-SCRIPTS.md](MIGRATION-SCRIPTS.md)
