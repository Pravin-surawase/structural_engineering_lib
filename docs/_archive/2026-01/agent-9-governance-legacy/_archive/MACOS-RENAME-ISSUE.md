# macOS Case-Insensitive Filesystem - Rename Issue

**Date:** 2026-01-10
**Context:** Phase A4 - Naming Cleanup (kebab-case conversions)

## Problem

When renaming files on macOS from UPPERCASE to lowercase (e.g., `FILE.md` → `file.md`), the case-insensitive filesystem causes issues:

1. **Git sees the rename** but filesystem may not change case
2. **Stash operations revert** case-only changes
3. **`git mv` fails** with "destination exists" error on direct rename

## Root Cause

macOS uses **case-insensitive but case-preserving** APFS/HFS+ filesystem:
- `AGENT-6-FILE.md` and `agent-6-file.md` are treated as the same file
- Git tracks case changes, but filesystem operations can be inconsistent
- Stash/unstash operations may revert to original case

## Failed Approaches

### ❌ Direct rename
```bash
git mv "docs/FILE.md" "docs/file.md"
# Error: fatal: destination exists
```

### ❌ Using ai_commit.sh/safe_push.sh
- These scripts use stash operations
- Stash/unstash reverts case-only renames
- Files revert to UPPERCASE after unstash

## ✅ Working Solution: Two-Step Rename

```bash
# Step 1: Rename to temp name (different filename)
git mv "docs/_archive/2026-01/AGENT-6-FILE.md" \
      "docs/_archive/2026-01/AGENT-6-FILE.md.tmp"

# Step 2: Rename temp to final lowercase
git mv "docs/_archive/2026-01/AGENT-6-FILE.md.tmp" \
      "docs/_archive/2026-01/agent-6-file.md"

# Step 3: Commit immediately (avoid stash)
git commit -m "docs: rename to kebab-case"
git push
```

### Why This Works

1. **Temp suffix** creates genuinely different filename (case doesn't matter)
2. **Two separate operations** ensure filesystem catches up
3. **Immediate commit** avoids stash operations that could revert changes

## Implementation Pattern (Agent 9)

### Batch Processing (5-8 files per batch)

```bash
# Batch of 5 files
for file in FILE1.md FILE2.md FILE3.md FILE4.md FILE5.md; do
  new=$(echo "$file" | tr 'A-Z_' 'a-z-')
  git mv "docs/_archive/2026-01/$file" "docs/_archive/2026-01/${file}.tmp"
  git mv "docs/_archive/2026-01/${file}.tmp" "docs/_archive/2026-01/$new"
done

# Commit immediately
git commit -m "docs(governance): Phase A4 Batch X - Rename 5 files to kebab-case

Details...
Progress: X/Y files"

git push
```

### Critical Rules

1. ✅ **Process in small batches** (5-8 files)
2. ✅ **Commit immediately** after each batch
3. ✅ **Use two-step rename** with .tmp suffix
4. ✅ **Push immediately** to preserve progress
5. ❌ **Never use stash** with case-only renames
6. ❌ **Don't batch too many files** (increases failure risk)

## Results (Phase A4)

**Batch 1** (3cd500e): 10 _internal files ✅ (UPPERCASE_SNAKE to kebab-case)
**Batch 2a** (be7a164): 5 _archive files ✅ (AGENT-6 files)

- Both batches succeeded with two-step approach
- Zero git conflicts
- 100% history preserved
- Validation errors reduced: 117 → 107 → (ongoing)

## Alternative: Linux/CI Approach

For future automation, consider:
- Running rename operations in Linux container (case-sensitive filesystem)
- CI pipeline handles renames during merge
- Agent 9 generates rename script, CI executes

## Reference

- Issue discovered: 2026-01-10 during Phase A4 Batch 2
- Pattern established: be7a164
- Validation: Works for both _internal and _archive folders
