# Documentation Structure Review (2026-01-07)

**Goal:** Reduce root-level clutter while keeping canonical docs discoverable

---

## Findings

- Canonical documentation lives in structured subfolders (`architecture/`,
  `contributing/`, `getting-started/`, `reference/`, `planning/`, `research/`).
- Root-level files are mostly **redirect stubs** pointing to canonical paths.
- The canonical mapping is documented in `docs/README.md`.

---

## Current Root Policy

**Keep at root (canonical):**

- `README.md`
- `TASKS.md`
- `SESSION_LOG.md`
- `ai-context-pack.md`
- `agent-bootstrap.md`
- `git-workflow-ai-agents.md`
- `handoff.md`
- `releases.md`
- `v0.7-requirements.md` (archived stub)
- `v0.8-execution-checklist.md` (archived stub)

**Redirect stubs (legacy paths):**

- Root stubs remain to prevent link breakage in older docs and external notes.
- Canonical targets are listed in `docs/README.md`.

---

## Decision

- **Short term (pre-v1.0):** Keep legacy redirect stubs for backward
  compatibility.
- **Post v1.0:** Remove legacy stubs after confirming no external references.

---

## Next Actions

- Revisit stub removal after v1.0.
- If removing stubs, update internal references and
  document a final migration note in `docs/README.md`.
