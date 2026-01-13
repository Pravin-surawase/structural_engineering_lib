# Naming Conventions

**Type:** Guide
**Audience:** Developers
**Status:** Approved
**Importance:** Medium
**Version:** 1.0.0
**Created:** 2025-12-01
**Last Updated:** 2026-01-13

This document defines naming standards for files, modules, and symbols in this
repository.

---

## 1. File Naming

### Documentation Files

- **Standard:** kebab-case (e.g., `api-design-guidelines.md`)
- **Exceptions:**
  - `README.md` (directory index)
  - `TASKS.md` (task ledger)
  - `SESSION_LOG.md` (session log)
  - `LICENSE`, `CHANGELOG.md` (industry-standard names)

### Python Files

- **Modules:** snake_case (e.g., `beam_design.py`)
- **Classes:** PascalCase (e.g., `BeamDesignResult`)
- **Functions:** snake_case (e.g., `calculate_moment_capacity`)

### Directories

- **Preferred:** kebab-case (e.g., `getting-started/`)
- **Avoid:** Uppercase or mixed naming unless required by tooling

---

## 2. Branch Naming

- **Feature branches:** `feature/TASK-123-short-description`
- **Fix branches:** `fix/TASK-456-brief-title`
- **Hygiene branches:** `hygiene/cleanup-topic`
- **Audit branches:** `audit/hygiene-YYYY-MM-DD`
- **Release branches:** `release/v0.X.Y`

---

## 3. Document Headers

Use consistent headers for documents:

```
# Title

**Status:** Draft | In Review | Active
**Last Updated:** YYYY-MM-DD
**Owner:** <role or person>
```

---

## 4. Notes

- Renaming a file requires updating all references.
- If in doubt, prefer clarity and consistency over brevity.
