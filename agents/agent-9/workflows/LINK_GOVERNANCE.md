# Link Governance Workflow

**Owner:** Agent 9 (Governance)
**Created:** 2026-01-10
**Purpose:** Prevent broken internal links through automation and clear processes

---

## Problem Statement

Internal markdown links break when:
1. Files are renamed/moved without updating references
2. Relative paths use wrong `../` levels
3. New docs reference files that don't exist yet
4. Planning docs contain example/target paths (false positives)

**Historical Impact:** 130+ broken links detected on 2026-01-10 after migration work.

---

## Prevention Strategy (3 Layers)

### Layer 1: Pre-Commit Hook (Automatic)

**Trigger:** Any commit that modifies `docs/**/*.md`

**Behavior:**
- Runs `scripts/check_links.py`
- Blocks commit if broken links detected in active docs
- Excludes planning/archive/research directories

**Configuration:** `.pre-commit-config.yaml`
```yaml
- id: check-markdown-links
  name: Check markdown internal links
  entry: python3 scripts/check_links.py
  files: ^docs/.*\.md$
```

### Layer 2: CI Validation (Safety Net)

**Trigger:** Every push to main, every PR

**Workflow:** `.github/workflows/fast-checks.yml`
```yaml
- name: Doc checks (parallel)
  run: |
    python scripts/check_links.py &
```

**Behavior:** Fails PR if broken links introduced.

### Layer 3: Manual Validation (Deep Check)

**When to run:**
- After major file migrations
- Monthly governance review
- Before releases

**Command:**
```bash
# Full check (includes archive/planning/research)
python scripts/check_links.py --all

# Active docs only (default)
python scripts/check_links.py
```

---

## Excluded Directories

These directories are **not checked** for broken links:

| Directory | Reason |
|-----------|--------|
| `agents/agent-9` | Planning docs with target paths |
| `docs/_archive` | Historical docs with outdated references |
| `docs/research` | Research docs with example content |

**Modify exclusions:** Edit `SKIP_DIRECTORIES` in `scripts/check_links.py`

---

## Excluded Link Patterns

These patterns are **skipped** (detected as placeholders):

| Pattern | Example |
|---------|---------|
| `text` | `[text](target.md)` |
| `Link 1`, `Link 2` | Example links |
| `$variable` | Variable placeholders |
| `path/to/` | Example paths |
| `file.md`, `target.md` | Generic examples |

**Modify patterns:** Edit `SKIP_LINK_PATTERNS` in `scripts/check_links.py`

---

## Workflow: When Moving/Renaming Files

### Before Moving
```bash
# 1. Check current link status
python scripts/check_links.py

# 2. Find all references to the file
grep -r "old-filename.md" docs/
```

### Moving Files
```bash
# Always use git mv
git mv docs/old-path/file.md docs/new-path/file.md

# Update references
grep -rl "old-path/file.md" docs/ | xargs sed -i '' 's|old-path/file.md|new-path/file.md|g'
```

### After Moving
```bash
# 3. Verify no broken links
python scripts/check_links.py

# 4. Commit with Agent 8 workflow
./scripts/ai_commit.sh "refactor(docs): Move file.md to new location"
```

---

## Bulk Link Fixing

When many links are broken (>10), use automation:

```bash
# 1. Generate broken link report
python scripts/check_links.py 2>&1 | tee broken_links.txt

# 2. For pattern-based issues, use sed
grep -rl "old-pattern" docs/ | xargs sed -i '' 's|old-pattern|new-pattern|g'

# 3. Verify fix
python scripts/check_links.py

# 4. Commit
./scripts/ai_commit.sh "fix(docs): Fix broken links (old-pattern → new-pattern)"
```

---

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Broken links (active docs) | 0 | ✅ 0 |
| Pre-commit blocks | 0/week | N/A |
| CI failures (links) | 0/week | N/A |

---

## Integration with Agent 9 Governance

This workflow is part of **Phase A5: Link + Script Integrity**.

**Weekly Check (during governance session):**
```bash
# Run during weekly maintenance
python scripts/check_links.py --all
```

**Monthly Deep Validation:**
- Check all directories including excluded
- Update `SKIP_DIRECTORIES` if new planning folders added
- Review false positives and update patterns

---

## Troubleshooting

### Pre-commit fails on broken links
```bash
# See what's broken
python scripts/check_links.py

# Fix and re-commit
./scripts/ai_commit.sh "fix: resolve broken links"
```

### False positive (planning doc flagged)
```bash
# Add directory to exclusions
# Edit scripts/check_links.py, add to SKIP_DIRECTORIES:
"docs/new-planning-folder",
```

### Need to check all files (including excluded)
```bash
# Temporarily comment out SKIP_DIRECTORIES
# Or modify script to add --all flag
```

---

**Last Updated:** 2026-01-10
