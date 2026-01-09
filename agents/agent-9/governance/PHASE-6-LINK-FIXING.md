# Phase 6: Link Fixing and Verification

**Duration:** 6-8 hours
**Complexity:** Medium-High
**Risk:** Low (doesn't move files, only updates links)
**Validation Impact:** No error reduction (links don't affect governance validation, but critical for usability)

---

## Overview

Update all internal markdown links to reflect new file paths after Phases 2-5 migrations.

**What needs fixing:**
- Links to files moved in Phase 2 (agents/ → agents/roles/)
- Links to files moved in Phase 3 (docs/ root → subdirectories)
- Links to files archived in Phase 4 (various → docs/_archive/YYYY-MM/)
- Links to files renamed in Phase 5 (92 naming changes)

**Link Types:**
1. **Relative links:** `[text](../path/file.md)`, `[text](./file.md)`
2. **Absolute links:** `[text](/docs/path/file.md)`
3. **Anchor links:** `[text](file.md#section)`
4. **Reference links:** `[text][ref]` with `[ref]: path/file.md`

---

## Prerequisites

- ✅ Phase 0 complete (backup created, link checker installed)
- ✅ Phase 2 complete (agents/ files moved)
- ✅ Phase 4 complete (dated files archived)
- ✅ Phase 5 complete (files renamed) - **critical prerequisite**
- ✅ LINK-MAP.md populated with all migrations
- ✅ Working tree is clean
- ✅ Migration branch active

**Required Tool:**
- `scripts/check_links.py` - link validation script (created in Phase 0 or Phase 1)

---

## Step-by-Step Execution

### Step 1: Baseline Link Check

```bash
# Run link checker to identify all broken links
python scripts/check_links.py docs/ agents/ --report

# Or if script doesn't exist, use simple grep
echo "Finding all markdown links..."
grep -r "\[.*\](.*\.md" docs/ agents/ --include="*.md" | \
  grep -v "http" > /tmp/all-links.txt

# Count total links
wc -l /tmp/all-links.txt
```

**Expected output:**
```
🔍 Checking links in docs/ and agents/...

Broken links found:
  ❌ docs/README.md:15 → agents/AGENT-9-GOVERNANCE.md (file not found)
  ❌ docs/architecture/design.md:42 → ../planning/Analysis_Report.md (file not found)
  ❌ docs/getting-started/guide.md:8 → ../../session-2025-12-15.md (file not found)
  ... (estimated 50-100 broken links)

Total broken links: 87
Total links checked: 324
```

**Checkpoint 1:** ✅ Baseline established (broken links identified)

---

### Step 2: Generate Link Fix Map

**Use LINK-MAP.md to create fix patterns:**

```bash
# Extract all Phase 2-5 entries from LINK-MAP.md
grep -E "Phase (2|3|4|5)" agents/agent-9/governance/LINK-MAP.md -A 500 > /tmp/link-map-extract.txt

# Generate sed commands for bulk replacement
cat > /tmp/generate_fix_commands.py << 'EOF'
#!/usr/bin/env python3
import re

with open('/tmp/link-map-extract.txt') as f:
    for line in f:
        line = line.strip()
        # Skip comments, headers, empty lines
        if line.startswith('#') or not line or '→' not in line:
            continue

        # Parse: old/path.md → new/path.md
        old, new = line.split('→')
        old = old.strip()
        new = new.strip()

        old_file = old.split('/')[-1]
        new_file = new.split('/')[-1]

        # Generate sed command for filename replacement
        print(f"# {old} → {new}")
        print(f"find docs/ agents/ -name '*.md' -type f -exec sed -i '' 's|{old_file}|{new_file}|g' {{}} +")
        print()
EOF

python /tmp/generate_fix_commands.py > /tmp/link-fix-commands.sh
chmod +x /tmp/link-fix-commands.sh
```

**Review generated commands:**

```bash
# Preview first 20 commands
head -40 /tmp/link-fix-commands.sh

# Expected:
# # agents/AGENT-1-RESEARCH.md → agents/roles/agent-1-research.md
# find docs/ agents/ -name '*.md' -type f -exec sed -i '' 's|AGENT-1-RESEARCH.md|agent-1-research.md|g' {} +
#
# # agents/AGENT-2-PLANNING.md → agents/roles/agent-2-planning.md
# find docs/ agents/ -name '*.md' -type f -exec sed -i '' 's|AGENT-2-PLANNING.md|agent-2-planning.md|g' {} +
# ...
```

**Checkpoint 2:** ✅ Fix commands generated

---

### Step 3: Execute Automated Link Fixes (Filename Only)

**Run generated fix commands:**

```bash
# Execute bulk replacements
bash /tmp/link-fix-commands.sh

# This updates filenames in links, but NOT paths
# Example: [Agent 9](agents/AGENT-9-GOVERNANCE.md)
#       → [Agent 9](agents/agent-9-governance.md)
# But path is still wrong (should be agents/roles/agent-9-governance.md)
```

**Checkpoint 3:** ✅ Filenames updated in links

---

### Step 4: Fix Path Changes (Manual or Script)

**Now update paths for moved files:**

```bash
# Phase 2: agents/*.md → agents/roles/*.md
find docs/ agents/ -name "*.md" -type f -exec sed -i '' \
  's|](agents/agent-\([0-9]\{1,2\}\)-|](agents/roles/agent-\1-|g' {} +

# Phase 3: docs/*.md → docs/subdirectory/*.md
# (This requires knowing which files moved where - use LINK-MAP.md)

# Example: Task-Specs.md moved to docs/getting-started/
find docs/ agents/ -name "*.md" -type f -exec sed -i '' \
  's|](docs/task-specs\.md)|](docs/getting-started/task-specs.md)|g' {} +

find docs/ agents/ -name "*.md" -type f -exec sed -i '' \
  's|]\(\.\./task-specs\.md\)|](../getting-started/task-specs.md)|g' {} +

# Phase 4: docs/path/file-YYYY-MM-DD.md → docs/_archive/YYYY-MM/file-YYYY-MM-DD.md
# (Automated path update based on date in filename)

cat > /tmp/fix_archived_links.sh << 'EOF'
#!/bin/bash
# Fix links to archived dated files

# Get archived files from LINK-MAP Phase 4
grep "Phase 4" agents/agent-9/governance/LINK-MAP.md -A 50 | \
while IFS='→' read -r old new; do
  [[ "$old" =~ ^# ]] && continue
  [[ -z "$old" ]] && continue

  old=$(echo "$old" | xargs)
  new=$(echo "$new" | xargs)

  echo "Fixing links: $old → $new"

  # Update full path
  find docs/ agents/ -name "*.md" -type f -exec sed -i '' \
    "s|]($old)|]($new)|g" {} +

  # Update relative path (various forms)
  old_file=$(basename "$old")
  new_rel="../../_archive/$(basename $(dirname "$new"))/$(basename "$new")"

  find docs/ agents/ -name "*.md" -type f -exec sed -i '' \
    "s|](.*/$old_file)|]($new_rel)|g" {} +
done
EOF

chmod +x /tmp/fix_archived_links.sh
bash /tmp/fix_archived_links.sh
```

**Checkpoint 4:** ✅ Paths updated

---

### Step 5: Fix Relative Links

**Relative links broken by file moves need path adjustments:**

```bash
# Example: If docs/getting-started/guide.md references ../design.md
# and design.md moved to docs/architecture/design.md,
# the link should become ../architecture/design.md

# Manual approach: Find broken relative links
grep -r "](\.\./" docs/ agents/ --include="*.md" > /tmp/relative-links.txt

# Review and fix manually (tedious but accurate)
# For each broken link:
#   1. Determine source file location
#   2. Determine target file new location
#   3. Calculate new relative path
#   4. Update link

# Or use link checker with auto-fix (if available)
python scripts/check_links.py docs/ agents/ --fix-relative
```

**Checkpoint 5:** ✅ Relative links fixed (manual or automated)

---

### Step 6: Verify Link Fixes

```bash
# Run link checker again
python scripts/check_links.py docs/ agents/ --report

# Expected improvement:
# Broken links: 87 → ~10 (manual fixes needed)

# Manual verification:
# Open 10-15 random files in editor/browser
# Click through links, verify they work
```

**Expected output:**
```
🔍 Checking links in docs/ and agents/...

Broken links remaining:
  ⚠️ docs/architecture/design.md:42 → ../old-file.md (intentional - archived)
  ⚠️ docs/reference/api.md:15 → external-doc.md (external link, not in repo)
  ... (5-10 remaining broken links)

Total broken links: 8
Total links checked: 324
```

**Checkpoint 6:** ✅ Link fixes verified (most fixed, few intentional broken links remain)

---

### Step 7: Fix Anchor Links

**Links with anchors need special handling:**

```bash
# Find anchor links
grep -r "](.*\.md#" docs/ agents/ --include="*.md" > /tmp/anchor-links.txt

# Update anchor links (filename + path)
# Example: [text](Old_File.md#section) → [text](old-file.md#section)

# Run same sed commands as Step 3, but include the anchor
# Example:
find docs/ agents/ -name "*.md" -type f -exec sed -i '' \
  's|AGENT-9-GOVERNANCE\.md#|agent-9-governance.md#|g' {} +

# Verify anchors still exist in target files
# (Manual check - open files, verify section headers match)
```

**Checkpoint 7:** ✅ Anchor links updated

---

### Step 8: Fix Reference-Style Links

**Find and fix reference-style links:**

```bash
# Find reference-style links
grep -r "^\[.*\]:.*\.md" docs/ agents/ --include="*.md" > /tmp/reference-links.txt

# Example reference link:
# [agent9]: agents/AGENT-9-GOVERNANCE.md
# ... later in file ...
# See [agent9] for details.

# Update references (same sed patterns as inline links)
find docs/ agents/ -name "*.md" -type f -exec sed -i '' \
  's|^\(\[.*\]:\s*\)agents/AGENT-9-GOVERNANCE\.md|\1agents/roles/agent-9-governance.md|g' {} +
```

**Checkpoint 8:** ✅ Reference links updated

---

### Step 9: Update Link Checker Ignore List (Optional)

**Some broken links are intentional (archived docs, external refs):**

```bash
# Create ignore list for link checker
cat > /tmp/link-checker-ignore.txt << 'EOF'
# Intentionally broken links (archived, deprecated, or external)

# Archived docs (no longer actively maintained, keep links for history)
docs/_archive/2025-10/*.md

# External references (not in repo)
external-doc.md
vendor-guide.md

# Deprecated links (planned for removal)
old-api.md
EOF

# Run link checker with ignore list
python scripts/check_links.py docs/ agents/ --ignore /tmp/link-checker-ignore.txt
```

**Checkpoint 9:** ✅ Ignore list created (optional)

---

### Step 10: Commit Link Fixes

```bash
# Stage all link updates
git add -A

# Verify changes
git diff --cached --stat

# Create commit
git commit -m "$(cat <<'EOF'
fix(migration): Phase 6 - Fix all internal links after file migrations

Updated links to reflect:
- Phase 2: Agent files moved to agents/roles/ (12 files)
- Phase 3: Docs categorized to subdirectories (~44 files)
- Phase 4: Dated files archived to docs/_archive/ (23 files)
- Phase 5: Files renamed to kebab-case (92 files)

Link fixes:
- Updated filenames in all links (171 files touched)
- Updated paths for moved files (agents/, docs/ subdirs, _archive/)
- Fixed relative links broken by moves
- Updated anchor links with new filenames
- Fixed reference-style links

Broken links reduced: 87 → 8 (91% improvement)
Remaining broken links are intentional (archived/external refs).

Phase 6 of 8 complete.
Ref: agents/agent-9/governance/FULL-MIGRATION-EXECUTION-PLAN.md

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"

# Push
git push origin migration/folder-structure-cleanup
```

**Checkpoint 10:** ✅ Changes committed and pushed

---

## Validation Checklist

After completing all steps, verify:

- [ ] Link checker shows <10 broken links (down from ~87)
- [ ] All remaining broken links are intentional (documented in ignore list)
- [ ] Manual spot-check of 15 files confirms links work
- [ ] Anchor links point to correct sections
- [ ] Reference-style links work correctly
- [ ] Relative links calculate correct paths
- [ ] No 404s when navigating documentation in browser/editor
- [ ] Git history shows link updates (many files modified)
- [ ] Changes committed with descriptive message
- [ ] Migration branch pushed

---

## Link Checker Script

**If `scripts/check_links.py` doesn't exist, create it:**

```python
#!/usr/bin/env python3
"""Check markdown links in documentation."""

import re
import sys
from pathlib import Path
from typing import List, Tuple

def find_links(file_path: Path) -> List[Tuple[int, str, str]]:
    """Find all markdown links in file.

    Returns: List of (line_number, link_text, link_target)
    """
    links = []
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            for match in link_pattern.finditer(line):
                text = match.group(1)
                target = match.group(2)

                # Skip external links
                if target.startswith('http'):
                    continue

                # Skip anchors within same file
                if target.startswith('#'):
                    continue

                links.append((i, text, target))

    return links

def check_link(source_file: Path, target: str) -> bool:
    """Check if link target exists.

    Handles:
    - Relative paths (../path/file.md)
    - Absolute paths (/docs/path/file.md)
    - Anchors (file.md#section)
    """
    # Split anchor
    if '#' in target:
        target, anchor = target.split('#', 1)
    else:
        anchor = None

    # Resolve relative path
    if target.startswith('/'):
        target_path = Path(target[1:])  # Remove leading /
    else:
        target_path = (source_file.parent / target).resolve()

    # Check file exists
    return target_path.exists()

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: check_links.py <directory> [--report]")
        sys.exit(1)

    search_dir = Path(sys.argv[1])
    report_mode = '--report' in sys.argv

    broken = []
    total = 0

    # Find all markdown files
    for md_file in search_dir.rglob('*.md'):
        links = find_links(md_file)

        for line_num, text, target in links:
            total += 1

            if not check_link(md_file, target):
                broken.append((md_file, line_num, target))

                if not report_mode:
                    print(f"❌ {md_file}:{line_num} → {target} (broken)")

    print()
    print(f"Total links checked: {total}")
    print(f"Broken links: {len(broken)} ({len(broken)/total*100:.1f}%)")

    sys.exit(0 if len(broken) == 0 else 1)

if __name__ == '__main__':
    main()
```

**Install:**

```bash
# Save to scripts/check_links.py
chmod +x scripts/check_links.py

# Test
python scripts/check_links.py docs/
```

---

## Common Issues

### Issue 1: Link checker reports false positives

**Cause:** Doesn't handle all link formats

**Solution:**
```bash
# Manually verify reported broken links
# Some may be external, some may use uncommon syntax
```

### Issue 2: Relative links still broken after fix

**Cause:** Incorrect path calculation

**Solution:**
```bash
# Debug path calculation
# Example: Source: docs/getting-started/guide.md
#          Target (old): ../design.md (docs/design.md)
#          Target (new): docs/architecture/design.md
#          Relative from source: ../architecture/design.md

# Manual fix
sed -i '' 's|](../design\.md)|](../architecture/design.md)|g' docs/getting-started/guide.md
```

### Issue 3: Anchor links don't work

**Cause:** Section headers changed or don't match anchor format

**Solution:**
```bash
# GitHub-style anchors: lowercase, hyphens, no special chars
# Example: "## API Design" → #api-design

# Verify anchors manually
# Open target file, search for section header
```

### Issue 4: Too many files to fix manually

**Cause:** Automated tools can't handle all edge cases

**Solution:**
```bash
# Prioritize high-traffic docs (README, getting-started/)
# Fix critical broken links first
# Defer low-priority docs to later cleanup
```

---

## Rollback Procedure

**If Phase 6 creates broken links:**

```bash
# Undo last commit
git reset --hard HEAD~1

# Or restore specific files
git checkout HEAD~1 -- docs/path/to/file.md

# Re-run link fixes with corrections
```

**See:** [ROLLBACK-PROCEDURES.md](ROLLBACK-PROCEDURES.md)

---

## Time Estimates

- **Step 1 (Baseline check):** 15 minutes
- **Step 2 (Generate fix map):** 30 minutes
- **Step 3 (Automated filename fixes):** 20 minutes
- **Step 4 (Path fixes):** 90-120 minutes
- **Step 5 (Relative links):** 60-90 minutes (manual intensive)
- **Step 6 (Verify):** 30 minutes
- **Step 7 (Anchor links):** 30 minutes
- **Step 8 (Reference links):** 15 minutes
- **Step 9 (Ignore list):** 15 minutes (optional)
- **Step 10 (Commit):** 10 minutes

**Total:** 6-8 hours

---

## Next Steps

After Phase 6 completion:

1. **Update MIGRATION-STATUS.md** to mark Phase 6 complete
2. **Proceed to Phase 7** (script updates) - update hardcoded paths in automation
3. **Or proceed to Phase 3** if skipped earlier (docs/ categorization)

---

## Success Criteria

Phase 6 is complete when:

1. ✅ Broken links reduced from ~87 to <10
2. ✅ All remaining broken links are intentional/documented
3. ✅ Link checker passes with <5% broken links
4. ✅ Manual spot-check confirms navigation works
5. ✅ Anchor links point to correct sections
6. ✅ Relative links calculate correct paths
7. ✅ Changes committed and pushed

---

**Phase 6 Status:** 📋 Ready for execution
**Last Updated:** 2026-01-10
**Next Phase:** [PHASE-7-SCRIPT-UPDATES.md](PHASE-7-SCRIPT-UPDATES.md)
