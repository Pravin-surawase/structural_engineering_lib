# Agent Essentials — Critical Rules (50 Lines)

**Type:** Guide
**Audience:** All Agents
**Status:** Approved
**Importance:** Critical
**Created:** 2026-01-23
**Last Updated:** 2026-01-23

---

> **Load this FIRST.** Everything else is optional context.

## 🚨 THE ONE RULE

```bash
./scripts/ai_commit.sh "type: message"   # ALL commits
```

**NEVER use:** `git add`, `git commit`, `git push`, `git pull` manually.

## ⚡ Session Start

```bash
./scripts/agent_start.sh --quick         # 6 seconds, validates everything
```

## 📋 Before Manual Work — Use Scripts Instead

| Action | USE THIS SCRIPT |
|--------|-----------------|
| Commit code | `./scripts/ai_commit.sh "msg"` |
| Move file | `.venv/bin/python scripts/safe_file_move.py old.md new.md` |
| Delete file | `.venv/bin/python scripts/safe_file_delete.py file.md` |
| Create doc | `.venv/bin/python scripts/create_doc.py path/file.md "Title"` |
| Fix links | `.venv/bin/python scripts/fix_broken_links.py --fix` |
| Check Streamlit | `.venv/bin/python scripts/check_streamlit_issues.py --all-pages` |

## 🎯 Golden Rules

1. **Never create duplicate docs** — Check [docs-canonical.json](../docs-canonical.json) first
2. **Verify outdated info online** — AI models, library versions, frameworks
3. **Use existing infrastructure** — Check `scripts/index.json` before writing new code
4. **Test before commit** — `.venv/bin/python -m pytest Python/tests -q`

## 📖 Load More Context When Needed

| Task | Load This |
|------|-----------|
| Git decisions | [git-automation/workflow-guide.md](../git-automation/workflow-guide.md) |
| Streamlit UI | [guidelines/streamlit-fragment-best-practices.md](../guidelines/streamlit-fragment-best-practices.md) |
| API changes | [reference/api.md](../reference/api.md) |
| Architecture | [architecture/project-overview.md](../architecture/project-overview.md) |

## ⚠️ Knowledge Cutoff Warning

**Your training data is outdated!** Before using:
- AI model names → Verify via `fetch_webpage` to official docs
- Library versions → Check actual `pyproject.toml`
- Framework APIs → Verify current documentation

**Verified (2026-01-23):** `gpt-4o`, `gpt-4o-mini`, `claude-sonnet-4-20250514`

---

**Next:** [agent-bootstrap.md](agent-bootstrap.md) for full onboarding
