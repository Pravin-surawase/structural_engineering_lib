# Task Board

> **How to use:** Start each session here. Pick from "Up Next", move to "Active", then "Done".

---

## 🔴 Active

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **S-007** | External engineer CLI test | CLIENT | ⏳ Waiting (requires human) |

**Context:** This is the last blocker before v0.20.0 release.

---

## 📋 Up Next

### v0.20.0 Release (after S-007 passes)

| ID | Task | Agent | Est. |
|----|------|-------|------|
| REL-001 | Update CHANGELOG | PM | 15 min |
| REL-002 | Bump version to 0.20.0 | DEVOPS | 10 min |
| REL-003 | Tag and release | DEVOPS | 15 min |

### v1.0 Gates

| Gate | Status | Notes |
|------|--------|-------|
| External CLI test | ⏳ | = S-007 |
| All tests pass | ✅ | 1810 pass, 91 skip |
| VBA parity verified | ✅ | Spot-checked |
| 5 beam validations | ✅ | Documented |

---

## 📦 Backlog (Post-v1.0)

| ID | Task | Agent | Description |
|----|------|-------|-------------|
| TASK-081 | Level C Serviceability | DEV | Shrinkage + creep (Annex C) |
| TASK-082 | VBA Parity Automation | DEVOPS | Python vs VBA harness |
| TASK-085 | Torsion Design | DEV | Cl. 41 + closed stirrups |
| TASK-086 | Side-Face Reinforcement | DEV | D > 750mm check (Cl. 26.5.1.3) |
| TASK-087 | Anchorage Check | DEV | Ld at supports (Cl. 26.2) |
| TASK-088 | Slenderness Check | DEV | L > 60b warning (Cl. 23.1.2) |
| TASK-089 | Flanged Width Helper | INTEGRATION | bf from slab geometry |

---

## ✅ Recently Completed

### v0.20.0 Stabilization (PRs #89-98)

- **S-015:** Fixed 4 broken doc links + created `scripts/check_links.py`
- **S-014:** Fixed expected output in beginners-guide (942→882)
- **S-009:** Fixed D1 expected Ld value (752→777)
- **S-006:** Improved job_runner error messages
- **S-020–S-032:** Verified all High Priority items (edge cases, performance)

### Earlier Sprints

| Sprint | Key Deliverables |
|--------|-----------------|
| Level B Serviceability (PR #62) | 7 functions, `DeflectionLevelBResult`, 16 tests |
| Release Automation (PR #59) | `release.py`, `check_doc_versions.py`, pre-commit hooks |
| Multi-Agent Review | CODEOWNERS, API docs, `__all__` exports |
| DXF Polish | Title blocks, PDF/PNG workflow |

> Full history: `docs/_archive/`

---

## 🛠️ Agent Roles

| Role | Use For |
|------|---------|
| **DEV** | Implementation, refactoring |
| **TESTER** | Test design, edge cases |
| **DEVOPS** | Automation, releases |
| **PM** | Scope, changelog |
| **DOCS** | API docs, guides |
| **CLIENT** | Requirements, validation |
| **SUPPORT** | Troubleshooting |

> Full list: `agents/README.md`

---

## 📊 Status

| Metric | Value |
|--------|-------|
| **Version** | v0.10.3 |
| **Tests** | 1810 passed, 91 skipped |
| **Coverage** | 92% branch |
| **Next Release** | v0.20.0 (awaiting S-007) |
| **Updated** | 2025-12-28 |

---

*Checklist: `docs/planning/v0.20-stabilization-checklist.md`*
