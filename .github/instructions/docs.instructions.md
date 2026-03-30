---
applyTo: "**/docs/**,**/*.md"
---

# Documentation Rules

## NEVER move/delete files manually

Use safe scripts that preserve 870+ internal links:
```bash
.venv/bin/python scripts/safe_file_move.py old.md new.md --dry-run  # Preview first
.venv/bin/python scripts/safe_file_move.py old.md new.md            # Then execute
.venv/bin/python scripts/safe_file_delete.py file.md
```

## New docs require metadata

Use `create_doc.py` or add manually:
```markdown
**Type:** [Guide|Research|Reference|Architecture|Decision]
**Audience:** [All Agents|Developers|Users]
**Status:** [Draft|Approved|Deprecated]
**Importance:** [Critical|High|Medium|Low]
**Created:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD
```

## Check for duplicates before creating

```bash
.venv/bin/python scripts/find_automation.py "topic"
```
Check `docs/docs-canonical.json` for existing canonical docs on the topic.

## Append-first policy (MANDATORY)

ALWAYS try updating an existing doc before creating a new one:
1. Search `docs-canonical.json` — if topic has a canonical doc, update that one
2. Search docs/ for existing docs on the same topic
3. Only create a new doc if NO existing doc covers the topic
4. Use `create_doc.py` for ALL new doc creation (enforces similarity check)

## Doc lifecycle

Every doc should have a clear status:
- **Draft** — Work in progress (max 7 days, then promote or delete)
- **Active** — Current and maintained
- **Deprecated** — Superseded, will be archived
- **Archived** — Historical record in `_archive/`

Multi-session WIP docs go to `docs/_active/` first, then move to permanent location when complete.

## Doc budget

Non-archived docs must stay under 400 files. Check with:
```bash
.venv/bin/python scripts/check_docs.py --budget
```

## After structural changes

Update indexes: `./scripts/generate_all_indexes.sh`
