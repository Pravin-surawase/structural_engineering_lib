---
description: Rules for editing documentation files
globs: docs/**,*.md
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

## After structural changes

Update indexes: `./scripts/generate_all_indexes.sh`
