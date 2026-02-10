---
applyTo: "**/docs/**,**/*.md"
---

# Documentation Rules

- NEVER move/delete files manually: use `safe_file_move.py` / `safe_file_delete.py`
- New docs require metadata (Type, Audience, Status): use `.venv/bin/python scripts/create_doc.py`
- Check `docs/docs-canonical.json` before creating to avoid duplicates
- After structural changes: run `./scripts/generate_all_indexes.sh`
