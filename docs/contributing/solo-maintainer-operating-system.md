# Solo Maintainer Operating System (Public)

**Type:** Guide
**Audience:** Maintainers
**Status:** Approved
**Importance:** High
**Version:** 1.0.0
**Created:** 2026-01-09
**Last Updated:** 2026-01-13

---

**Purpose:** Keep a solo-maintained engineering library stable, trusted, and low-drift.

**Scope:** Applies to all public releases, schemas, and APIs.

---

## Principles

- Deterministic outputs, explicit units, stable contracts.
- One active task at a time (WIP=1).
- Trust and correctness before new features.
- No silent defaults in design or reporting.

---

## Intake and Triage (No Diversion)

Use `docs/TASKS.md` Backlog as the INBOX.

Every new issue/feature must include:
- Severity: P0 / P1 / P2
- Impact area: design / schema / CLI / DXF / docs / parity
- Reproducible: yes / no
- Minimal input and expected vs actual output
- Link to failing case or file

Only P0 can interrupt the current week:
1) Incorrect or unsafe design result.
2) Fresh install or CLI broken (cannot run or invalid outputs).

Everything else waits for the next stabilization week.

---

## Weekly Operating Loop

Start of week:
- `.venv/bin/.venv/bin/python scripts/start_session.py`
- Pick exactly one task.

During week:
- Implement, test, and document together.
- No parallel tasks.

End of week:
- `.venv/bin/.venv/bin/python scripts/end_session.py`
- Summarize in `docs/SESSION_LOG.md`.

---

## Testing and Verification Rules

- Any change that affects math requires:
  - Before/after snapshot for a known input.
  - A regression test with documented source.
- Add golden vectors with clause references and tolerances.
- Use normalized comparisons for outputs; avoid raw DXF hashes across platforms.
- Maintain a compatibility test that loads last-release fixtures.

---

## Schema and Versioning

- All machine outputs include `schema_version`.
- No semantic changes without a version bump and migration note.
- Schemas live in `docs/specs/` and are treated as contracts.

---

## Release Gates (No Exceptions)

Required before tagging:
- `./scripts/ci_local.sh`
- `.venv/bin/.venv/bin/python scripts/check_doc_versions.py --ci`
- Update `CHANGELOG.md`, `docs/releases.md`, `docs/SESSION_LOG.md`

If any gate fails, do not release.

---

## Documentation Discipline

Single sources of truth:
- `docs/TASKS.md` (work queue)
- `docs/ai-context-pack.md` (agent context)
- `docs/planning/production-roadmap.md` (weekly plan)

If outputs or APIs change, update docs in the same PR.

---

## Parity Policy (Python <-> VBA)

Minimum for v1.0:
- 10 to 15 parity vectors passing within tolerance.

Full automation can expand post-v1.0; do not block v1.0 on it.

---

## External Trust Signals

- Publish verification pack outputs and sources.
- Include clause tags in results.
- Provide clear error messages with hints.

---

## Stop List (Scope Control)

Follow the "NO until v1.1" list in `docs/planning/production-roadmap.md`.
