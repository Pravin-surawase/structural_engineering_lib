# Session Log

Append-only record of decisions, PRs, and next actions. For detailed task tracking, see [TASKS.md](TASKS.md).

---

## 2025-12-27 — v0.9.5 Release + Docs Restructure

### Decisions

1. **PyPI Publishing:** Implemented Trusted Publishing (OIDC) workflow. No API tokens needed.
2. **Docs restructure:** Approved 7-folder structure with redirect stubs. Files staying at root: `README.md`, `TASKS.md`, `AI_CONTEXT_PACK.md`, `RELEASES.md`, `v0.7_REQUIREMENTS.md`, `v0.8_EXECUTION_CHECKLIST.md`.
3. **VBA parity scope:** Limited to critical workflows (design, compliance, detailing), not every function.

### PRs Merged

| PR | Title | Summary |
|----|-------|---------|
| #36 | feat: add PyPI publish workflow | Trusted Publishing + GitHub Release automation |
| #37 | chore: bump version to 0.9.5 | Version bump for first PyPI release |
| #38 | docs: update README and CHANGELOG for v0.9.5 | PyPI badge, simplified install |
| #39 | fix: README accuracy corrections | VBA parity wording, optimizer import, test command |
| #40 | docs: add migration scaffold folders (Phase 1) | 7 new folders with README indexes |
| #41 | docs: migrate verification docs (Phase 2) | Moved VERIFICATION_*.md with redirect stubs |
| #42 | docs: migrate reference docs (Phase 3) | Moved API_REFERENCE, KNOWN_PITFALLS, IS456_QUICK_REFERENCE, TROUBLESHOOTING |

### Releases

- **v0.9.5** published to PyPI: `pip install structural-lib-is456`
- **v0.9.4** tag created (was missing)

### Docs Migration Progress

| Phase | Folder | Status |
|-------|--------|--------|
| 1 | Scaffold folders | ✅ PR #40 |
| 2 | verification/ | ✅ PR #41 |
| 3 | reference/ | ✅ PR #42 |
| 4 | getting-started/ | Pending |
| 5 | contributing/ | Pending |
| 6 | architecture/ + planning/ | Pending |

### Next Actions

- [x] Phase 3: Migrate reference docs (API_REFERENCE, KNOWN_PITFALLS, IS456_QUICK_REFERENCE, TROUBLESHOOTING)
- [ ] Phase 4: Migrate getting-started docs
- [ ] Phase 5-6: Complete remaining migrations
- [ ] Create `cookbook/cli-reference.md` (new content)
- [ ] Update `docs/README.md` index with new folder links

---
