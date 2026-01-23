# Document Naming Conventions

**Type:** Guide
**Audience:** All Agents
**Status:** Draft
**Importance:** High
**Created:** 2026-01-23
**Last Updated:** 2026-01-23
**Related Tasks:** TASK-AGENT-EFFICIENCY

---

## Purpose

Reduce duplication, improve findability, and ensure every topic has a clear canonical home.

---

## Core Rules

1. **One topic = one canonical file.** Check `docs/docs-canonical.json` first.
2. **Name by topic, not by agent or session.** Avoid `agent-8-` or `session-64-` prefixes for long-lived docs.
3. **Prefer folder context over long prefixes.** Example: `docs/reference/api.md` not `reference-api.md` if already in `/reference`.
4. **Use lowercase with hyphens.** No spaces, no ALL_CAPS.

---

## Standard Patterns

| Doc Type | Pattern | Example |
|----------|---------|---------|
| Guide | `guide-{topic}.md` or `{topic}-guide.md` | `guide-git-workflow.md` |
| Reference | `reference-{topic}.md` or `{topic}.md` in `/reference` | `api.md` |
| Research | `research-{topic}.md` or `{topic}-research.md` | `ai-agent-effectiveness-research.md` |
| Decision | `decision-{topic}.md` or `adr-NNN-{topic}.md` | `adr-012-indexing-strategy.md` |
| Plan | `{topic}-plan.md` in `/planning` | `v0-20-rollout-plan.md` |

---

## Forbidden Patterns

- **ALL_CAPS_NAMES.md** (except `README.md`, `CHANGELOG.md`, `TASKS.md`, `SESSION_LOG.md`)
- **Numbered prefixes** (`01-`, `02_`) unless order matters (e.g., ADR series)
- **Agent/session prefixes for canonical docs** (`agent-8-`, `session-64-`)

---

## Session Docs

Session artifacts must live under:
- `docs/agents/sessions/YYYY-MM/`
- or `docs/_archive/YYYY-MM/` once complete

If a session doc contains long-lived guidance, **promote it** to a canonical guide and archive the session file.

---

## Before Creating a New Doc

1. Check canonical registry: `docs/docs-canonical.json`
2. Run similarity check: `.venv/bin/python scripts/check_doc_similarity.py "your topic"`
3. Create via script: `.venv/bin/python scripts/create_doc.py path "Title"`

---

## Examples (Good)

- `docs/getting-started/agent-bootstrap.md`
- `docs/reference/api.md`
- `docs/guidelines/doc-naming-conventions.md`
- `docs/research/ai-agent-effectiveness-research.md`

## Examples (Bad)

- `docs/AGENT_BOOTSTRAP_COMPLETE_REVIEW.md`
- `docs/research/01-ai-research.md`
- `docs/agents/session-64-final.md`

---

*This standard aligns with `docs/docs-canonical.json` and is enforced in `scripts/check_doc_metadata.py`.*

