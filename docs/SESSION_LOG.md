# Session Log

> **Purpose:** Append-only record of session summaries. For task tracking, see [TASKS.md](TASKS.md).
>
> **Archive:** Older entries are moved to `docs/_archive/SESSION_LOG_*.md`

---

## 2025-12-28 (Night) — v0.10.5 Error Schema Implementation

### Summary

Implemented structured error schema (W03-W04) with machine-readable error codes, hints, and IS 456 clause references.

### PRs Merged

| PR | Summary |
|----|---------|
| #106 | feat: add AGENT_BOOTSTRAP.md and enhance start_session.py |
| #107 | chore: add git workflow learnings to copilot-instructions |
| #108 | docs: clarify version messaging, reduce duplication, add VBA parity harness |
| #109 | docs: overhaul production-roadmap.md with phases, baseline, and governance |
| #110 | docs: align TASKS.md with roadmap (INBOX, severity, week sync) |
| #111 | docs: add error schema v1 draft |
| #112 | feat: implement error schema in core functions |

### Key Deliverables

- **errors.py module:** `DesignError` dataclass with code/severity/message/field/hint/clause
- **Core integration:** Structured errors in `design_singly_reinforced()`, `design_shear()`, `check_beam_ductility()`
- **Tests:** 29 new tests in `test_error_schema.py`
- **Documentation:** Error schema doc updated to "Implemented" status

### Status

| Metric | Value |
|--------|-------|
| Version | v0.10.5 |
| Tests | 1877 passed |
| Coverage | 92% branch |

**Next:** W05 (input validation pass) or S-007 when tester available

---

## 2025-12-28 (Evening) — v0.10.4 Release + Automation Suite

### Summary

Released v0.10.4 with developer automation tooling. Added session scripts, nightly QA workflow, and handoff checker.

### PRs Merged

| PR | Summary |
|----|---------|
| #99 | docs: polish core docs (TASKS, SESSION_LOG, AI_CONTEXT_PACK) |
| #100 | docs: fix P0-P2 issues from review |
| #101 | feat: add pre-handoff doc freshness checker |
| #102 | feat: session start/end automation scripts |
| #103 | chore: add nightly QA workflow |
| #104 | chore: release v0.10.4 |

### Key Deliverables

- **Session automation:** `start_session.py`, `end_session.py`, `check_handoff_ready.py`
- **Nightly QA:** Full test suite + CLI smoke test (design → bbs → dxf → job)
- **Release v0.10.4:** Published to PyPI

### Status

| Metric | Value |
|--------|-------|
| Version | v0.10.4 |
| Tests | 1810 passed, 91 skipped |
| Coverage | 92% branch |

**Next:** S-007 (owner CLI test) → v0.20.0 release

---

## 2025-12-28 — v0.20.0 Stabilization Sprint

### Summary

Completed 14 of 15 Critical stabilization items. Only S-007 (external CLI test) remains.

### PRs Merged

| PR | Summary |
|----|---------|
| #89 | S-015: Fixed 4 broken doc links, added `scripts/check_links.py` |
| #90 | S-014: Fixed expected output in beginners-guide (942→882mm²) |
| #91 | S-009: Fixed D1 expected Ld value (752→777mm) |
| #92 | S-006: Improved job_runner error messages |
| #93 | S-020–S-032: Verified all High Priority items |
| #95-98 | Documentation updates and cleanup |

### Key Deliverables

- **Link checker:** `scripts/check_links.py` — validates 173 links across 85 files
- **Error messages:** `job_runner.py` gives specific errors for missing fields
- **Performance verified:** 0.009ms/beam, 94,000 beams/second

### Status

| Category | Complete |
|----------|----------|
| 🔴 Critical | 14/15 |
| 🟡 High Priority | 12/12 ✅ |
| 🟢 Nice to Have | 0/4 |

**Blocker:** S-007 (external CLI test) requires human tester.

---

## 2025-12-28 — v0.10.2 Release

### Summary

Added CLI serviceability flags and summary output.

### PRs Merged

| PR | Summary |
|----|---------|
| #68 | docs: update Python/README.md to v0.10.0 |
| #69 | chore: bump version to 0.10.1 |
| #70 | feat(cli): add serviceability flags and summary output |

### Key Features

- `--deflection` — Run Level A deflection check
- `--support-condition` — Set support condition
- `--crack-width-params` — JSON file for crack width parameters
- `--summary` — Write compact `design_summary.csv`

---

## 2025-12-27 — v0.10.0 Release

### Summary

Level B Serviceability, code quality improvements, and PyPI release.

### PRs Merged

| PR | Summary |
|----|---------|
| #62 | Level B Serviceability + CLI/AI Discoverability |
| #63 | PM Planning Update |
| #64-66 | Release v0.10.0 + code quality |

### Key Deliverables

- 7 new Level B functions in `serviceability.py`
- 22 shear unit tests in `tests/test_shear.py`
- `llms.txt` for AI discovery
- **v0.10.0** published to PyPI

---

## 2025-12-27 — v0.9.5/v0.9.6 Releases

### Summary

PyPI Trusted Publishing setup, docs restructure, and validation examples.

### Key Deliverables

- Trusted Publishing (OIDC) workflow — no API tokens needed
- 7-folder docs structure with migration complete
- Verification examples pack (5 textbook validations)
- **v0.9.5** and **v0.9.6** published to PyPI

---

## Earlier Sessions

Full history archived in `docs/_archive/`

Previous sessions covered:
- v0.9.4: Unified CLI, cutting-stock optimizer, VBA parity
- v0.9.0-0.9.3: DXF export, BBS, compliance module
- v0.8.x: Detailing, serviceability foundations
- v0.7.x: Initial Python/VBA implementation

---

## Session Template

```markdown
## YYYY-MM-DD — Title

### Summary
One-line summary of what was accomplished.

### PRs Merged
| PR | Summary |
|----|---------|
| #XX | Description |

### Key Deliverables
- Bullet points of main outputs

### Lessons Learned (optional)
- What to do differently next time
```
